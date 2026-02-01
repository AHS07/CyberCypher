"""Centralized LLM provider management using HuggingFace only.

HuggingFace-Only Mode:
- Qwen/Qwen2.5-7B-Instruct: Primary analyzer
- microsoft/Phi-3-medium-4k-instruct: Skeptic critic  
- mistralai/Mistral-7B-Instruct-v0.3: Consensus judge

All models run via HuggingFace Inference API using OpenAI-compatible client.
"""
import asyncio
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List

from supabase import create_client, Client

from app.core.config import settings

logger = logging.getLogger(__name__)

# Supabase client for logging
supabase: Client = create_client(settings.supabase_url, settings.supabase_service_key)


class LLMManager:
    """Manages HuggingFace LLM providers with health tracking and automatic failover."""
    
    def __init__(self):
        # Import HuggingFace manager
        from app.core.hf_manager import get_hf_manager
        self.hf_manager = get_hf_manager()
        
        # Provider health tracking (HuggingFace models)
        self.provider_health = {
            "qwen": {"is_healthy": True, "consecutive_failures": 0, "last_check": None},
            "phi3": {"is_healthy": True, "consecutive_failures": 0, "last_check": None},
            "mistral": {"is_healthy": True, "consecutive_failures": 0, "last_check": None},
        }
        
    def get_llm(self, provider: str, model: Optional[str] = None, temperature: float = 0.0):
        """Get model name for specified HuggingFace provider."""
        model_mapping = {
            "qwen": "Qwen/Qwen2.5-7B-Instruct",
            "phi3": "microsoft/Phi-3-medium-4k-instruct", 
            "mistral": "mistralai/Mistral-7B-Instruct-v0.3"
        }
        
        if provider not in model_mapping:
            raise ValueError(f"Unknown provider: {provider}. Available: {list(model_mapping.keys())}")
        
        return model or model_mapping[provider]
    
    async def call_llm(self, provider: str, messages: list, temperature: float = 0.0) -> str:
        """Call HuggingFace LLM via OpenAI-compatible client.
        
        Args:
            provider: Provider name (qwen, phi3, mistral)
            messages: List of message dicts with 'role' and 'content'
            temperature: Sampling temperature
            
        Returns:
            Generated response text
        """
        model_name = self.get_llm(provider)
        
        try:
            result = await self.hf_manager.call_model(
                model_name=model_name,
                messages=messages,
                temperature=temperature,
                max_tokens=512
            )
            
            if result and result.get("content"):
                # Mark as healthy
                self.provider_health[provider]["is_healthy"] = True
                self.provider_health[provider]["consecutive_failures"] = 0
                return result["content"]
            else:
                raise Exception("Empty response from HuggingFace")
                
        except Exception as e:
            logger.error(f"HuggingFace call failed for {provider}: {e}")
            
            # Mark as unhealthy
            self.provider_health[provider]["consecutive_failures"] += 1
            if self.provider_health[provider]["consecutive_failures"] >= 3:
                self.provider_health[provider]["is_healthy"] = False
            
            raise


# Global LLM manager instance
llm_manager = LLMManager()