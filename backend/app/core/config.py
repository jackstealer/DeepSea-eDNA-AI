"""
Application configuration using Pydantic Settings
"""
from typing import List
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    APP_NAME: str = "DeepSea eDNA AI Backend"
    APP_VERSION: str = "2.1.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "production"
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 3000
    WORKERS: int = 4
    
    # Database
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/edna_db"
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # File Storage
    UPLOAD_DIR: str = "./data/uploads"
    RESULTS_DIR: str = "./data/results"
    MODEL_DIR: str = "../ml_models"  # Points to ml_models folder with trained model
    MAX_UPLOAD_SIZE: int = 524288000  # 500MB
    
    # Deep Learning
    DEFAULT_MODEL: str = "marine_model"  # Use the trained marine model
    MODEL_DEVICE: str = "cuda"  # Use GPU if available, fallback to CPU
    BATCH_SIZE: int = 32
    MAX_SEQUENCE_LENGTH: int = 1000
    
    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"
    
    # API Keys
    NCBI_API_KEY: str = ""
    BOLD_API_KEY: str = ""
    
    # Security
    SECRET_KEY: str = "change-this-secret-key-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000"
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Convert CORS_ORIGINS string to list"""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "./logs/app.log"
    
    # Model Training
    TRAINING_DATA_DIR: str = "./data/training"
    VALIDATION_SPLIT: float = 0.2
    EPOCHS: int = 50
    LEARNING_RATE: float = 0.001
    
    # Reference Databases
    NCBI_TAXONOMY_DB: str = "./data/ncbi_taxonomy"
    BOLD_DATABASE: str = "./data/bold_db"
    CUSTOM_REFERENCE_DB: str = "./data/custom_refs"
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # Ignore extra fields from frontend .env


settings = Settings()
