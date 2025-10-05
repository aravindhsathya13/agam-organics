"""
Configuration settings using pydantic-settings
"""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "Agam Organics"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # Supabase
    SUPABASE_URL: str
    SUPABASE_KEY: str
    SUPABASE_SERVICE_KEY: str
    
    # JWT
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Payment Gateway (Razorpay)
    RAZORPAY_KEY: str = "rzp_test_demo"  # Replace with actual key
    RAZORPAY_SECRET: str = "demo_secret"  # Replace with actual secret
    
    # CORS - will be parsed from comma-separated string
    ALLOWED_ORIGINS: str = "http://localhost:5000,http://127.0.0.1:5000"
    
    def get_allowed_origins(self) -> List[str]:
        """Parse ALLOWED_ORIGINS into a list"""
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(',')]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
