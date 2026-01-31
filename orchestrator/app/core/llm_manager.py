"""Centralized LLM provider management with intelligent failover."""
import asyncio
import time
from typing import Optional, Callable, Any
from functools import wraps
from datetime import datetime
import logging

from supabase import create_client, Client
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI

from app.core.config import settings

logger = logging.getLogger(__name__)


class ProviderUnavailableError(Exception):
    """Raised when a provider is unavailable."""
    pass


class LLMManager:
    """Manages LLM providers with health tracking and automatic failover."""
    
    def __init__(self):
        self.supabase: Client = create_client(
            settings.supabase_url,
            settings.supabase_service_key
        )
        
        # Provider health tracking
        self.provider_health = {
            "claude": {"is_healthy": True, "consecutive_failures": 0, "last_check": None},
            "gemini": {"is_healthy": True, "consecutive_failures": 0, "last_check": None},
            "ollama": {"is_healthy": True, "consecutive_failures": 0, "last_check": None},
        }
        
        # Provider priority order
        self.provider_priority = ["claude", "gemini", "ollama"]
        
    def get_llm(self, provider: str, model: Optional[str] = None, temperature: float = 0.0):
        """Get LLM instance for specified provider."""
        if provider == "claude":
            return ChatAnthropic(
                model=model or settings.claude_model,
                anthropic_api_key=settings.anthropic_api_key,
                temperature=temperature,
                max_tokens=4096,
            )
        elif provider == "gemini":
            return ChatGoogleGenerativeAI(
                model=model or settings.gemini_model,
                google_api_key=settings.google_api_key,
                temperature=temperature,
            )
        elif provider == "ollama":
            return ChatOpenAI(
                base_url=settings.ollama_base_url,
                model=model or settings.ollama_model,
                temperature=temperature,
                api_key="ollama",  # Ollama doesn't require a real API key
            )
        else:
            raise ValueError(f"Unknown provider: {provider}")
    
    def mark_failure(self, provider: str, error: Exception):
        """Mark a provider as failed and update health status."""
        self.provider_health[provider]["consecutive_failures"] += 1
        self.provider_health[provider]["last_check"] = datetime.utcnow()
        
        # Mark as unhealthy after 3 consecutive failures
        if self.provider_health[provider]["consecutive_failures"] >= 3:
            self.provider_health[provider]["is_healthy"] = False
            logger.warning(f"Provider {provider} marked as unhealthy after 3 failures")
    
    def mark_success(self, provider: str):
        """Mark a provider as successful and reset failure count."""
        self.provider_health[provider]["consecutive_failures"] = 0
        self.provider_health[provider]["is_healthy"] = True
        self.provider_health[provider]["last_check"] = datetime.utcnow()
    
    def get_next_healthy_provider(self, exclude: Optional[list[str]] = None) -> Optional[str]:
        """Get the next healthy provider based on priority order."""
        exclude = exclude or []
        for provider in self.provider_priority:
            if provider not in exclude and self.provider_health[provider]["is_healthy"]:
                return provider
        return None
    
    async def log_reliability_event(
        self,
        test_id: str,
        provider: str,
        event_type: str,
        error_code: Optional[str] = None,
        error_message: Optional[str] = None,
        failover_to: Optional[str] = None,
        response_time_ms: Optional[float] = None,
    ):
        """Log reliability event to Supabase."""
        try:
            await asyncio.to_thread(
                self.supabase.table("reliability_logs").insert({
                    "test_id": test_id,
                    "provider": provider,
                    "event_type": event_type,
                    "error_code": error_code,
                    "error_message": error_message,
                    "failover_to": failover_to,
                    "response_time_ms": response_time_ms,
                    "timestamp": datetime.utcnow().isoformat(),
                }).execute
            )
        except Exception as e:
            logger.error(f"Failed to log reliability event: {e}")


# Global LLM manager instance
llm_manager = LLMManager()


def with_failover(test_id: str):
    """Decorator that provides automatic failover between LLM providers.
    
    Usage:
        @with_failover(test_id="test-123")
        async def my_llm_call(provider: str) -> str:
            llm = llm_manager.get_llm(provider)
            return await llm.ainvoke("prompt")
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> tuple[Any, str]:
            """Wrapper that tries multiple providers with exponential backoff."""
            providers_tried = []
            last_error = None
            
            for attempt in range(settings.max_retries):
                # Get next healthy provider
                provider = llm_manager.get_next_healthy_provider(exclude=providers_tried)
                
                if provider is None:
                    logger.error("All providers exhausted")
                    await llm_manager.log_reliability_event(
                        test_id=test_id,
                        provider="all",
                        event_type="failure",
                        error_message="All providers exhausted"
                    )
                    raise ProviderUnavailableError("All LLM providers are unavailable")
                
                providers_tried.append(provider)
                logger.info(f"Attempting {func.__name__} with provider: {provider}")
                
                start_time = time.time()
                try:
                    # Call the function with the provider
                    result = await func(*args, provider=provider, **kwargs)
                    
                    # Success!
                    response_time_ms = (time.time() - start_time) * 1000
                    llm_manager.mark_success(provider)
                    
                    await llm_manager.log_reliability_event(
                        test_id=test_id,
                        provider=provider,
                        event_type="success",
                        response_time_ms=response_time_ms
                    )
                    
                    return result, provider
                    
                except Exception as e:
                    response_time_ms = (time.time() - start_time) * 1000
                    last_error = e
                    
                    # Determine error type
                    error_message = str(e)
                    error_code = None
                    
                    if "429" in error_message:
                        error_code = "RATE_LIMIT"
                    elif "500" in error_message or "502" in error_message or "503" in error_message:
                        error_code = "SERVER_ERROR"
                    elif "timeout" in error_message.lower():
                        error_code = "TIMEOUT"
                    else:
                        error_code = "UNKNOWN"
                    
                    llm_manager.mark_failure(provider, e)
                    
                    # Determine next provider for failover logging
                    next_provider = llm_manager.get_next_healthy_provider(exclude=providers_tried)
                    
                    await llm_manager.log_reliability_event(
                        test_id=test_id,
                        provider=provider,
                        event_type="failure" if next_provider is None else "failover",
                        error_code=error_code,
                        error_message=error_message[:500],  # Truncate long errors
                        failover_to=next_provider,
                        response_time_ms=response_time_ms
                    )
                    
                    logger.warning(
                        f"Provider {provider} failed with {error_code}: {error_message[:100]}. "
                        f"Failing over to {next_provider}"
                    )
                    
                    # Exponential backoff before retry
                    if attempt < settings.max_retries - 1:
                        await asyncio.sleep(settings.retry_delay_seconds * (2 ** attempt))
            
            # If we get here, all retries exhausted
            raise last_error or ProviderUnavailableError("All providers failed")
        
        return wrapper
    return decorator
