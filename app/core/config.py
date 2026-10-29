from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "USSD Sales Automation System"
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/ussd_sales_db"
    
    # Africa's Talking
    AT_USERNAME: str = "sandbox"
    AT_API_KEY: str = "atsk_dummy_key"
    AT_SHORTCODE: str = "12345"
    AT_WEBHOOK_URL: str = "http://localhost:8000/api/ussd"
    
    # M-Pesa Daraja
    MPESA_ENV: str = "sandbox"
    MPESA_CONSUMER_KEY: str = "dummy_consumer_key"
    MPESA_CONSUMER_SECRET: str = "dummy_consumer_secret"
    MPESA_SHORTCODE: str = "174379"
    MPESA_PASSKEY: str = "dummy_passkey"
    MPESA_CALLBACK_URL: str = "http://localhost:8000/api/mpesa/callback"
    
    DEBUG: bool = True
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
