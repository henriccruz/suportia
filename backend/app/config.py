"""Configurações centrais da aplicação, lidas de variáveis de ambiente."""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    twilio_account_sid: str = ""
    twilio_auth_token: str = ""
    twilio_phone_number: str = ""

    anthropic_api_key: str = ""
    anthropic_model: str = "claude-3-5-sonnet-20241022"

    database_url: str = "sqlite:///./suportia.db"

    frontend_url: str = "http://localhost:5173"

    stripe_api_key: str = ""


settings = Settings()
