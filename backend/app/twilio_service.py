"""Integração com Twilio para enviar mensagens de WhatsApp/SMS ao cliente."""
from __future__ import annotations

from twilio.rest import Client

from app.config import settings

_client: Client | None = None


def get_client() -> Client:
    global _client
    if _client is None:
        _client = Client(settings.twilio_account_sid, settings.twilio_auth_token)
    return _client


def send_message(to_phone: str, body: str) -> None:
    """Envia uma mensagem para o cliente via Twilio.

    `to_phone` já deve estar no formato esperado pelo Twilio
    (ex: "whatsapp:+5511999999999" para WhatsApp).
    """
    if not settings.twilio_account_sid or not settings.twilio_auth_token:
        # Sem credenciais configuradas (ex: ambiente de desenvolvimento local):
        # apenas loga a mensagem em vez de falhar.
        print(f"[twilio_service] (modo simulado) Para {to_phone}: {body}")
        return

    get_client().messages.create(
        from_=settings.twilio_phone_number,
        to=to_phone,
        body=body,
    )
