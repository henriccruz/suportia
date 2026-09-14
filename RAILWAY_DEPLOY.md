# 🚀 Deploy no Railway — Passo a Passo

Seu repositório GitHub: https://github.com/henriccruz/suportia

## ⚡ Passo 1: Criar Conta Railway (5 min)

1. Vá em: https://railway.app
2. Clique em **"Start Project"**
3. Escolha **"GitHub"** e autorize
4. Selecione o repositório: **suportia**

## ⚡ Passo 2: Configurar Backend

Railway vai detectar `railway.json` automaticamente.

Clique em **"Create**" → Espera 1 minuto

Você verá:
- ✅ Build iniciando
- ✅ Deploy iniciando
- ✅ URL pública (tipo `https://suportia-prod.up.railway.app`)

## ⚡ Passo 3: Adicionar Variáveis de Ambiente

Na aba **Variables**, clique **"Add"** e configure:

```
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxxxxxxxxx
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=seu_auth_token_aqui
TWILIO_PHONE_NUMBER=whatsapp:+14155238886
FRONTEND_URL=https://suportia.vercel.app
DATABASE_URL=postgresql://...  (Railway vai gerar)
```

⚠️ **Pega os valores reais do Twilio Console** (não deixe no código!)

> **Nota**: TWILIO_AUTH_TOKEN deve ser copiado do console do Twilio (Settings > API keys)

## ⚡ Passo 4: PostgreSQL (Opcional)

Se quiser banco de dados em produção:

1. Na aba **Plugins**, clique **"Add"**
2. Procure por **PostgreSQL**
3. Clique **"Create"**
4. Railway vai popular automaticamente `DATABASE_URL`

## ⚨ Resultado

- ✅ Backend rodando em: `https://seu-app.railway.app`
- ✅ Deploy automático a cada push no GitHub
- ✅ Logs em tempo real
- ✅ Pronto pra receber webhooks do Twilio

## 🔗 Próximo: Deploy Frontend no Vercel

Depois faça o mesmo pra frontend (veja VERCEL_DEPLOY.md)
