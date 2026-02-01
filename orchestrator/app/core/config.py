"""Centralized configuration management using Pydantic BaseSettings."""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Supabase Configuration
    supabase_url: str
    supabase_anon_key: str
    supabase_service_key: str
    
    # HuggingFace Configuration (ONLY LLM PROVIDER)
    hf_token: str
    
    # Orchestrator Configuration
    orchestrator_host: str = "localhost"
    orchestrator_port: int = 8003
    
    # Failover Configuration
    max_retries: int = 3
    retry_delay_seconds: int = 2
    provider_health_check_interval: int = 60
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
