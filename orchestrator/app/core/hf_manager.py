"""Hugging Face API manager using OpenAI-compatible interface."""
import asyncio
import logging
import os
from typing import Dict, Any, Optional, List
from datetime import datetime
from openai import AsyncOpenAI

logger = logging.getLogger(__name__)

class HuggingFaceManager:
    """Manages Hugging Face API calls using OpenAI-compatible interface."""
    
    def __init__(self, token: str):
        self.token = token
        
        # Initialize OpenAI client with HF router
        self.client = AsyncOpenAI(
            base_url="https://router.huggingface.co/v1",
            api_key=token,
        )
        
        # Model assignments for different agents (using supported models)
        self.models = {
            "primary_analyzer": "Qwen/Qwen2.5-7B-Instruct:together",
            "skeptic_critic": "Qwen/Qwen2.5-7B-Instruct:together",  # Use same model with different prompts
            "consensus_judge": "Qwen/Qwen2.5-7B-Instruct:together",
            "fallback": "Qwen/Qwen2.5-7B-Instruct:together"
        }
        
        # Health tracking
        self.model_health = {model: {"is_healthy": True, "consecutive_failures": 0} 
                           for model in self.models.values()}
    
    async def call_model(self, model_name: str, messages: List[Dict[str, str]], 
                        max_tokens: int = 512, temperature: float = 0.7) -> Optional[Dict[str, Any]]:
        """Call a Hugging Face model using OpenAI-compatible chat completion."""
        try:
            logger.info(f"Calling model {model_name} with {len(messages)} messages")
            
            response = await self.client.chat.completions.create(
                model=model_name,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
            )
            
            if response.choices and len(response.choices) > 0:
                content = response.choices[0].message.content
                
                # Mark model as healthy
                self.model_health[model_name]["is_healthy"] = True
                self.model_health[model_name]["consecutive_failures"] = 0
                
                logger.info(f"Successfully got response from {model_name}")
                
                return {
                    "content": content.strip() if content else "",
                    "model": model_name,
                    "timestamp": datetime.utcnow().isoformat()
                }
            else:
                logger.error(f"No choices in response from {model_name}")
                self._mark_unhealthy(model_name)
                return None
                
        except Exception as e:
            logger.error(f"Error calling {model_name}: {e}")
            self._mark_unhealthy(model_name)
            return None
    
    def _mark_unhealthy(self, model_name: str):
        """Mark a model as unhealthy."""
        if model_name in self.model_health:
            self.model_health[model_name]["consecutive_failures"] += 1
            if self.model_health[model_name]["consecutive_failures"] >= 3:
                self.model_health[model_name]["is_healthy"] = False
                logger.warning(f"Marked {model_name} as unhealthy after 3 failures")
    
    async def get_healthy_model(self, agent_type: str) -> Optional[str]:
        """Get a healthy model for the given agent type."""
        primary_model = self.models.get(agent_type)
        
        # Try primary model first
        if primary_model and self.model_health[primary_model]["is_healthy"]:
            return primary_model
        
        # Try fallback models
        for model in self.models.values():
            if self.model_health[model]["is_healthy"]:
                logger.info(f"Using fallback model {model} for {agent_type}")
                return model
        
        # If all models are unhealthy, try the primary anyway
        logger.warning(f"All models unhealthy, trying primary {primary_model} anyway")
        return primary_model
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get health status of all models."""
        return {
            "models": self.model_health,
            "timestamp": datetime.utcnow().isoformat()
        }


# Global instance
hf_manager = None

def get_hf_manager() -> HuggingFaceManager:
    """Get the global HF manager instance."""
    global hf_manager
    if hf_manager is None:
        # Use the token provided - set as environment variable for OpenAI client
        import os
        os.environ["HF_TOKEN"] = "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"
        hf_manager = HuggingFaceManager("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")
    return hf_manager