from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "LankaCart PayHere E-Commerce"
    PROJECT_DESCRIPTION: str = "FastAPI E-commerce platform with PayHere Sandbox payment gateway integration"
    VERSION: str = "1.0.0"
    API_V1_PREFIX: str = "/api/v1"
    
    # Database Settings (Default: SQLite for instant zero-dependency running; switch to PostgreSQL or MySQL anytime)
    DATABASE_URL: str = "sqlite:///./ecommerce.db"
    
    # PayHere Sandbox Credentials (defaults to public sandbox test credentials if not configured)
    PAYHERE_MERCHANT_ID: str = "1211149"
    PAYHERE_MERCHANT_SECRET: str = "4TkZ76v6Ea48qW6wQ3X5F1G2"
    PAYHERE_MODE: str = "sandbox"  # 'sandbox' or 'live'
    PAYHERE_CURRENCY: str = "LKR"
    
    # PayHere Endpoints
    PAYHERE_SANDBOX_URL: str = "https://sandbox.payhere.lk/pay/checkout"
    PAYHERE_LIVE_URL: str = "https://www.payhere.lk/pay/checkout"
    
    # Application Host & Public URL (Update with your ngrok URL for live PayHere sandbox webhooks)
    BASE_URL: str = "http://localhost:8000"
    
    @property
    def checkout_url(self) -> str:
        return self.PAYHERE_SANDBOX_URL if self.PAYHERE_MODE == "sandbox" else self.PAYHERE_LIVE_URL
    
    @property
    def notify_url(self) -> str:
        return f"{self.BASE_URL.rstrip('/')}/api/v1/payments/payhere/notify"
    
    @property
    def return_url(self) -> str:
        return f"{self.BASE_URL.rstrip('/')}/checkout/success"
    
    @property
    def cancel_url(self) -> str:
        return f"{self.BASE_URL.rstrip('/')}/checkout/cancel"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
