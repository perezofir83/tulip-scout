"""Configuration management using Pydantic settings."""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )
    
    # Environment
    env: str = "development"
    
    # Database
    database_url: str = "sqlite:///./tulip_scout.db"
    
    # Google Gemini API
    gemini_api_key: str
    
    # Gmail API
    gmail_credentials_path: str = "./credentials.json"
    gmail_token_path: str = "./token.pickle"
    
    # Rate Limiting (LinkedIn Premium)
    linkedin_daily_limit: int = 40
    linkedin_hourly_limit: int = 10
    linkedin_min_delay_seconds: int = 10
    linkedin_max_delay_seconds: int = 15
    
    # Regional Settings
    target_regions: str = "Poland,Czech Republic,Romania,Japan,South Korea,Singapore,Hong Kong"
    
    @property
    def target_regions_list(self) -> List[str]:
        """Parse target regions into a list."""
        return [r.strip() for r in self.target_regions.split(",")]
    
    # Logging
    log_level: str = "INFO"
    log_format: str = "json"
    
    # API Settings
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    
    # Dashboard Settings
    dashboard_port: int = 8501


# Global settings instance
settings = Settings()
