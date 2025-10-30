"""Configuration management for Description Service"""
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Application configuration"""
    
    # API Configuration
    API_TOKEN = os.getenv('API_TOKEN', 'M44483403m')
    PORT = int(os.getenv('PORT', 8080))
    HOST = os.getenv('HOST', '0.0.0.0')
    # Parse CORS origins and strip whitespace from each
    CORS_ORIGINS = [origin.strip() for origin in os.getenv('CORS_ORIGINS', '').split(',') if origin.strip()]
    
    # PostgreSQL Database
    POSTGRES_HOST = os.getenv('POSTGRES_HOST')
    POSTGRES_PORT = int(os.getenv('POSTGRES_PORT', 5432))
    POSTGRES_DB = os.getenv('POSTGRES_DB')
    POSTGRES_USER = os.getenv('POSTGRES_USER')
    POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD')
    
    @property
    def DATABASE_URL(self):
        """Build database connection URL"""
        return (
            f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )
    
    # S3/R2 Storage
    S3_ENDPOINT = os.getenv('S3_ENDPOINT')
    S3_ACCESS_KEY_ID = os.getenv('S3_ACCESS_KEY_ID')
    S3_SECRET_ACCESS_KEY = os.getenv('S3_SECRET_ACCESS_KEY')
    S3_BUCKET_NAME = os.getenv('S3_BUCKET_NAME', 'audio-novels-7x1e4')
    S3_REGION = os.getenv('S3_REGION', 'auto')
    
    # Azure OpenAI Configuration
    AZURE_OPENAI_ENDPOINT = os.getenv('AZURE_OPENAI_ENDPOINT')
    AZURE_OPENAI_DEPLOYMENT = os.getenv('AZURE_OPENAI_DEPLOYMENT', 'gpt-5-nano')
    USE_AZURE_OPENAI = os.getenv('USE_AZURE_OPENAI', 'true').lower() == 'true'
    
    # Standard OpenAI Configuration
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')


config = Config()

