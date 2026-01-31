"""Centralized LLM provider management with intelligent failover.

Ollama-Only Mode:
- deepseek-r1: Primary analyzer (replaces Claude)
- mistral: Skeptic critic (replaces Gemini)  
- llama3.2: Failover model

All models run locally via Ollama with direct client.
"""
import asyncio
import time
from typing import Optional, Callable, Any
from functools import wraps
from datetime import datetime
import logging
import json

from supabase import create_client, Client
import ollama

from app.core.config import settings

logger = logging.getLogger(__name__)


class ProviderUnavailableError(Exception):
    """Raised when a provider is unavailable."""
    pass


class LLMManager:
    """Manages Ollama LLM providers with health tracking and automatic failover."""
    
    # Model mapping for Ollama-only mode
    OLLAMA_MODELS = {
        "deepseek": "deepseek-r1:latest",      # Primary analyzer (replaces Claude)
        "mistral": "mistral:latest",            # Skeptic critic (replaces Gemini)
        "llama": "llama3.2:3b",                 # Failover
    }
    
    def __init__(self):
        self.supabase: Client = create_client(
            settings.supabase_url,
            settings.supabase_service_key
        )
        
        # Provider health tracking (all Ollama-based)
        self.provider_health = {
            "deepseek": {"is_healthy": True, "consecutive_failures": 0, "last_check": None},
            "mistral": {"is_healthy": True, "consecutive_failures": 0, "last_check": None},
            "llama": {"is_healthy": True, "consecutive_failures": 0, "last_check": None},
        }
        
        # Provider priority order for failover
        self.provider_priority = ["deepseek", "mistral", "llama"]
        
    def get_llm(self, provider: str, model: Optional[str] = None, temperature: float = 0.0):
        """Get model name for specified Ollama provider.
        
        Returns the model name to use with direct Ollama client.
        """
        if provider not in self.OLLAMA_MODELS:
            raise ValueError(f"Unknown provider: {provider}. Available: {list(self.OLLAMA_MODELS.keys())}")
        
        return model or self.OLLAMA_MODELS[provider]
    
    async def call_llm(self, provider: str, messages: list, temperature: float = 0.0) -> str:
        """Call Ollama LLM directly with messages.
        
        Args:
            provider: Provider name (deepseek, mistral, llama)
            messages: List of message dicts with 'role' and 'content'
            temperature: Temperature for generation
            
        Returns:
            Generated text response
        """
        model_name = self.get_llm(provider)
        
        # Convert messages to Ollama format
        prompt = ""
        for msg in messages:
            if msg.get("role") == "system":
                prompt += f"System: {msg['content']}\n\n"
            elif msg.get("role") == "user" or msg.get("role") == "human":
                prompt += f"User: {msg['content']}\n\n"
        
        prompt += "Assistant: "
        
        try:
            response = await asyncio.to_thread(
                ollama.generate,
                model=model_name,
                prompt=prompt,
                options={"temperature": temperature}
            )
            return response.get("response", "")
        except Exception as e:
            logger.error(f"Ollama call failed for {provider}: {e}")
            raise
    
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
            # Temporarily disable logging to debug
            logger.info(f"Reliability event: {provider} {event_type} for {test_id}")
            # await asyncio.to_thread(
            #     self.supabase.table("reliability_logs").insert({
            #         "test_id": test_id,
            #         "provider": provider,
            #         "event_type": event_type,
            #         "error_code": error_code,
            #         "error_message": error_message,
            #         "failover_to": failover_to,
            #         "response_time_ms": response_time_ms,
            #         "timestamp": datetime.utcnow().isoformat(),
            #     }).execute()
            # )
        except Exception as e:
            logger.error(f"Failed to log reliability event: {e}")


# Global LLM manager instance
llm_manager = LLMManager()


def with_failover(test_id: str):
    """Simplified decorator that provides basic failover between LLM providers."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> tuple[Any, str]:
            """Simplified wrapper with basic failover."""
            providers_to_try = ["deepseek", "mistral", "llama"]
            last_error = None
            
            for provider in providers_to_try:
                try:
                    logger.info(f"Attempting {func.__name__} with provider: {provider}")
                    
                    # Call the function with the provider
                    result = await func(*args, provider=provider, **kwargs)
                    
                    # Success!
                    llm_manager.mark_success(provider)
                    logger.info(f"Successfully completed {func.__name__} with {provider}")
                    
                    return result, provider
                    
                except Exception as e:
                    last_error = e
                    logger.warning(f"Provider {provider} failed: {str(e)[:100]}")
                    llm_manager.mark_failure(provider, e)
                    
                    # Try next provider
                    continue
            
            # If we get here, all providers failed
            raise last_error or ProviderUnavailableError("All LLM providers failed")
        
        return wrapper
    return decorator


async def simple_llm_call(provider: str, system_prompt: str, user_prompt: str) -> str:
    """Simple LLM call without complex decorators for testing."""
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]
    
    return await llm_manager.call_llm(provider, messages)
