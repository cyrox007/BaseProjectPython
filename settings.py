import os
from urllib.parse import quote_plus

from dotenv import load_dotenv

load_dotenv()

class Config:
    DEBUG: str = os.getenv("DEBUG", 'False').lower() == 'true'
    APPNAME: str = os.getenv("APPNAME", 'Application')
    APPDESCRIPTION: str = os.getenv(
        'APPDESCRIPTION', 
        """ Lorem ipsum dolor sit amet, consectetuer 
        adipiscing elit. Aenean commodo ligula eget dolor. 
        Aenean massa. Cum sociis natoque penatibus et """
    )
    APPVERSION: str = os.getenv("APPVERSION", '1.0.0')

    ABSPATH = os.path.dirname(os.path.abspath(__file__))

    SERVER_HTTP_PROTOCOL = os.getenv("SERVER_HTTP_PROTOCOL", "http://")
    SERVER_ADDR = os.getenv("SERVER_ADDR", "localhost")
    SERVER_PORT = int(os.getenv("SERVER_PORT", "9000"))

    # Database
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "5432")
    DB_NAME = os.getenv("DB_NAME", "wb")
    DB_USER = os.getenv("DB_USER", "postgres")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")

    @property
    def get_allowed_origins(self) -> list[str]:
        origins = os.getenv("ALLOWED_ORIGINS", "")
        return [origin.strip() for origin in origins.split(",") if origin.strip()]

    def database_url(self, async_mode=False):
        driver = "postgresql+asyncpg" if async_mode else "postgresql"
        password = quote_plus(self.DB_PASSWORD)
        url = f"{driver}://{self.DB_USER}:{password}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        return url.replace("%", "%%")
    
    # Безопасность
    ENCRYPTION_KEY = os.getenv("API_TOKEN_ENCRYPTION_KEY")
    
    # Redis
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    # Celery
    CELERY_BROKER_URL: str = REDIS_URL
    CELERY_RESULT_BACKEND: str = REDIS_URL

    # Настройки JWT
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY") or 'your-secret-key-change-in-production'
    JWT_ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 30
    REFRESH_TOKEN_EXPIRE_DAYS = 7


config = Config()