"""Integração com a API da Claude (Anthropic) para gerar respostas de suporte."""
from __future__ import annotations

from anthropic import Anthropic

from app.config import settings

SYSTEM_PROMPT = (
    "Você é um atendente de suporte ao cliente profissional. "
    "Responda em português (BR). Seja conciso, educado e resolutivo. "
    "Se não conseguir resolver, sugira escalar para agente humano."
)

_client: Anthropic | None = None


def get_client() -> Anthropic:
    global _client
    if _client is None:
        _client = Anthropic(api_key=settings.anthropic_api_key)
    return _client


def generate_response(message_text: str, customer_name: str | None = None) -> str:
    """Gera uma resposta automática para a mensagem do cliente usando a Claude API."""
    user_content = message_text
    if customer_name:
        user_content = f"Cliente: {customer_name}\nMensagem: {message_text}"

    response = get_client().messages.create(
        model=settings.anthropic_model,
        max_tokens=500,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_content}],
    )

    text_blocks = [block.text for block in response.content if block.type == "text"]
    return "\n".join(text_blocks).strip()
