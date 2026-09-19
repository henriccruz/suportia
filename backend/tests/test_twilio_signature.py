"""Testa a validação de assinatura do webhook do Twilio."""
from twilio.request_validator import RequestValidator

from app.config import settings

TEST_TOKEN = "test-auth-token-para-assinatura"
WEBHOOK_URL = "http://testserver/api/messages/webhook"


def _signed_form(monkeypatch, params):
    monkeypatch.setattr(settings, "twilio_auth_token", TEST_TOKEN)
    validator = RequestValidator(TEST_TOKEN)
    signature = validator.compute_signature(WEBHOOK_URL, params)
    return signature


def test_webhook_rejects_missing_signature(client, monkeypatch):
    monkeypatch.setattr(settings, "twilio_auth_token", TEST_TOKEN)
    resp = client.post(
        "/api/messages/webhook",
        data={"From": "whatsapp:+5511999999999", "Body": "oi", "ProfileName": "Teste"},
    )
    assert resp.status_code == 403


def test_webhook_rejects_wrong_signature(client, monkeypatch):
    monkeypatch.setattr(settings, "twilio_auth_token", TEST_TOKEN)
    resp = client.post(
        "/api/messages/webhook",
        data={"From": "whatsapp:+5511999999999", "Body": "oi", "ProfileName": "Teste"},
        headers={"X-Twilio-Signature": "assinatura-invalida"},
    )
    assert resp.status_code == 403


def test_webhook_accepts_valid_signature(client, monkeypatch):
    params = {"From": "whatsapp:+5511999999999", "Body": "oi", "ProfileName": "Teste"}
    signature = _signed_form(monkeypatch, params)
    resp = client.post(
        "/api/messages/webhook",
        data=params,
        headers={"X-Twilio-Signature": signature},
    )
    # Com assinatura valida, passa pela protecao (nunca deve dar 403).
    assert resp.status_code != 403
