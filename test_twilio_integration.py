#!/usr/bin/env python3
"""
Script para testar integração Twilio + SuportIA

Rode assim (substitua os valores):
  export TWILIO_ACCOUNT_SID="seu_account_sid_aqui"
  export TWILIO_AUTH_TOKEN="seu_auth_token"
  export YOUR_WHATSAPP_NUMBER="whatsapp:+5511945868377"
  python3 test_twilio_integration.py
"""

import os
from twilio.rest import Client

# Lê credenciais de variáveis de ambiente (seguro!)
# Rode assim: export TWILIO_ACCOUNT_SID="AC..." && export TWILIO_AUTH_TOKEN="..." && python3 test_twilio_integration.py
ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
YOUR_WHATSAPP_NUMBER = os.getenv("YOUR_WHATSAPP_NUMBER")
TWILIO_WHATSAPP_NUMBER = "whatsapp:+14155238886"  # Número sandbox do Twilio


def test_twilio_connection():
    """Testa se consegue conectar no Twilio"""
    print("🔍 Testando conexão com Twilio...")
    try:
        client = Client(ACCOUNT_SID, AUTH_TOKEN)
        account = client.api.accounts.get()
        print(f"✅ Conectado! Account: {account.friendly_name}")
        return client
    except Exception as e:
        print(f"❌ Erro ao conectar: {e}")
        return None


def test_send_message(client):
    """Testa envio de mensagem WhatsApp"""
    print(f"\n📱 Enviando mensagem de teste para {YOUR_WHATSAPP_NUMBER}...")
    try:
        message = client.messages.create(
            from_=TWILIO_WHATSAPP_NUMBER,
            to=YOUR_WHATSAPP_NUMBER,
            body="🤖 SuportIA: Teste de integração funcionando! Responda algo pra gente testar a IA."
        )
        print(f"✅ Mensagem enviada! SID: {message.sid}")
        return message.sid
    except Exception as e:
        print(f"❌ Erro ao enviar: {e}")
        return None


def setup_webhook():
    """Instruções para configurar o webhook"""
    print("\n🔗 Configurando webhook...")
    print("""
    Para receber mensagens de verdade:

    1. Vá em: https://console.twilio.com/us/console/phone-numbers/incoming
    2. Clique no seu número de WhatsApp
    3. Em "Messaging", configure:
       - Webhook URL: https://seu-backend.railway.app/api/messages/webhook
       - Method: HTTP POST
    4. Salve!

    ⚠️ Seu backend precisa estar em produção (Railway) pra isso funcionar!
    """)


if __name__ == "__main__":
    print("=" * 60)
    print("🤖 SuportIA — Teste de Integração Twilio")
    print("=" * 60)

    # Valida credenciais
    if not ACCOUNT_SID or not AUTH_TOKEN or not YOUR_WHATSAPP_NUMBER:
        print("\n❌ ERRO: Variáveis de ambiente não configuradas!")
        print("\nRode assim:")
        print('  export TWILIO_ACCOUNT_SID="seu_account_sid_aqui"')
        print('  export TWILIO_AUTH_TOKEN="seu_token_aqui"')
        print('  export YOUR_WHATSAPP_NUMBER="whatsapp:+5511945868377"')
        print("  python3 test_twilio_integration.py")
        exit(1)

    # Testa conexão
    client = test_twilio_connection()
    if not client:
        exit(1)

    # Testa envio
    msg_id = test_send_message(client)

    # Próximas instruções
    setup_webhook()

    print("\n✅ Teste completo!")
    print("\n📝 Próximos passos:")
    print("   1. Você recebeu uma mensagem no WhatsApp")
    print("   2. Responda algo (tipo 'Oi')")
    print("   3. Sua resposta vai pro backend SuportIA")
    print("   4. A IA vai responder automaticamente")
    print("   5. Vá no dashboard: http://localhost:5173")
    print("   6. Veja o ticket com a conversa completa!")
