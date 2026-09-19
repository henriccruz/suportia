"""Configurações centrais da aplicação, lidas de variáveis de ambiente."""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    twilio_account_sid: str = ""
    twilio_auth_token: str = ""
    twilio_phone_number: str = ""

    anthropic_api_key: str = ""
    anthropic_model: str = "claude-opus-5"

    database_url: str = "sqlite:///./suportia.db"

    frontend_url: str = "http://localhost:5173"

    stripe_api_key: str = ""

    # Segredo de assinatura dos tokens JWT - deve vir de variável de ambiente
    # em qualquer ambiente real. O fallback abaixo só existe para dev local.
    secret_key: str = "dev-only-insecure-secret-do-not-use-in-production"

    admin_username: str = "admin"
    admin_password: str = "admin"


settings = Settings()
