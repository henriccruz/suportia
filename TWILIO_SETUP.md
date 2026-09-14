# 🚀 Setup Twilio + SuportIA em 5 minutos

Seu número: `+55 11 94586-8377`

## ⚡ Passo 1: Pegue o Auth Token

1. Abra: https://console.twilio.com/us/account/keys-credentials/api-keys-and-tokens
2. Procure por **"Live API Key"** ou **"Auth Token"**
3. Você vai ver algo como: `123abc456def789ghi...`
4. **Copie esse código inteiro**

(Se a página estiver lenta, vá em Settings > API keys)

---

## ⚡ Passo 2: Cole no Script

```bash
cd /Users/henrique/SuportIA

# Abra o arquivo
nano test_twilio_integration.py

# Procure essa linha (perto do topo):
AUTH_TOKEN = "seu_auth_token_aqui"

# Troque por (Cole o token que copiou):
AUTH_TOKEN = "123abc456def789ghi..."

# Salve: Ctrl+X → Y → Enter
```

---

## ⚡ Passo 3: Rode o Script

```bash
python3 test_twilio_integration.py
```

**Você deve ver:**
```
✅ Conectado!
📱 Enviando mensagem...
✅ Mensagem enviada!
```

---

## ⚡ Passo 4: Receba a Mensagem

Seu WhatsApp vai receber:

> 🤖 SuportIA: Teste de integração funcionando! Responda algo pra gente testar a IA.

**Responda qualquer coisa**, tipo: "Oi!"

---

## ⚡ Passo 5: Veja no Dashboard

Abra: http://localhost:5173

Login: `admin` / `admin`

Você vai ver seu ticket com:
- ✅ Sua mensagem: "Oi!"
- ✅ Resposta da IA gerada automaticamente
- ✅ Status: "Aguardando aprovação"

Clique em "Aprovar" e a resposta será enviada de volta!

---

## ✅ Pronto!

Seu SuportIA está 100% funcional com WhatsApp! 🎉

**Próximas etapas (opcional):**
1. Deploy no Railway (backend fica online)
2. Configurar webhook permanente (WhatsApp conecta automaticamente)
3. Fazer mais testes com múltiplas mensagens

---

## ❓ Deu erro?

Se aparecer erro tipo "Invalid credentials":
- Verifique se o Auth Token está certo
- Tente copiar novamente do Twilio console

Se aparecer "Invalid phone number":
- O número precisa estar no formato: `whatsapp:+55119...`
- Verifique se está tudo certo

---

Pronto? Comece agora! 🚀
