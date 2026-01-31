"""Centralized configuration management using Pydantic BaseSettings."""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Supabase Configuration
    supabase_url: str
    supabase_anon_key: str
    supabase_service_key: str
    
    # LLM Provider API Keys (Optional for Ollama-only mode)
    anthropic_api_key: Optional[str] = None
    google_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None
    
    # Ollama Configuration (Local Fallback)
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2"
    ollama_primary_model: Optional[str] = None
    ollama_skeptic_model: Optional[str] = None
    ollama_failover_model: Optional[str] = None
    
    # LiteLLM Configuration
    litellm_log: str = "INFO"
    
    # Orchestrator Configuration
    orchestrator_host: str = "0.0.0.0"
    orchestrator_port: int = 8000
    
    # Failover Configuration
    max_retries: int = 3
    retry_delay_seconds: int = 2
    provider_health_check_interval: int = 60
    
    # Model Configurations
    claude_model: str = "claude-3-5-sonnet-20241022"
    gemini_model: str = "gemini-1.5-pro"
    llama_model: str = "llama3.2"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
