import os
from pathlib import Path
from typing import List, Optional
from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).resolve().parent.parent.parent

class Settings(BaseSettings):
    PROJECT_NAME: str = "AASHIMA ERP"
    VERSION: str = "2.4.0"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")

    # Business Identity
    BUSINESS_NAME: str = "AASHIMA"
    BUSINESS_LEGAL_NAME: str = "AASHIMA Women's World & AASHIMA Stitchers 'N' Drapers"
    SHOP_ADDRESS: str = "581, Turab Nagar, Ghaziabad, Uttar Pradesh, 201001, India"
    SHOP_PHONE: str = "+91 98102 44321"
    SHOP_EMAIL: str = "contact@aashima-atelier.in"
    SHOP_GSTIN: str = "09AABCA1234F1Z8"
    CURRENCY: str = "INR"
    CURRENCY_SYMBOL: str = "₹"

    # Security & Auth
    SECRET_KEY: str = os.getenv("SECRET_KEY", "regal_atelier_super_secure_secret_key_turab_nagar_ghaziabad_2026")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    OTP_EXPIRE_MINUTES: int = 10
    DEFAULT_OTP_BYPASS: Optional[str] = os.getenv("DEFAULT_OTP_BYPASS", "123456")  # For testing/sandbox

    # Database
    POSTGRES_SERVER: str = os.getenv("POSTGRES_SERVER", "localhost")
    POSTGRES_PORT: str = os.getenv("POSTGRES_PORT", "5432")
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "postgres")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "aashima_erp")
    
    # Use SQLite by default in development if PostgreSQL is not active
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        f"sqlite:///{BASE_DIR}/aashima_erp.db"
    )

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost",
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:3002",
        "http://localhost:5173",
        "http://localhost:8000",
        "http://localhost:8080",
        "*"
    ]

    # Storage paths
    MEDIA_DIR: Path = BASE_DIR / "media"
    QR_DIR: Path = MEDIA_DIR / "qr_codes"
    INVOICE_DIR: Path = MEDIA_DIR / "invoices"
    PHOTO_DIR: Path = MEDIA_DIR / "garment_photos"

    # Notifications Gateway
    NOTIFICATION_PROVIDER: str = os.getenv("NOTIFICATION_PROVIDER", "fast2sms") # fast2sms, twilio, gupshup, mock
    SMS_API_KEY: Optional[str] = os.getenv("SMS_API_KEY", "")
    FAST2SMS_API_KEY: Optional[str] = os.getenv("FAST2SMS_API_KEY", "")
    TWILIO_ACCOUNT_SID: Optional[str] = os.getenv("TWILIO_ACCOUNT_SID", "")
    TWILIO_AUTH_TOKEN: Optional[str] = os.getenv("TWILIO_AUTH_TOKEN", "")
    TWILIO_FROM_NUMBER: Optional[str] = os.getenv("TWILIO_FROM_NUMBER", "")
    WHATSAPP_API_KEY: Optional[str] = os.getenv("WHATSAPP_API_KEY", "")

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()

# Ensure storage directories exist
os.makedirs(settings.MEDIA_DIR, exist_ok=True)
os.makedirs(settings.QR_DIR, exist_ok=True)
os.makedirs(settings.INVOICE_DIR, exist_ok=True)
os.makedirs(settings.PHOTO_DIR, exist_ok=True)
