# Deployment Guide — SuportIA

Guia completo para fazer deploy da plataforma no Railway (backend) e Vercel (frontend).

## Prerequisites

- Conta GitHub com repositório conectado
- Conta Railway (railway.app)
- Conta Vercel (vercel.com)
- Chaves de API: Anthropic, Twilio (opcional para MVP)

---

## Backend → Railway

### 1. Criar um novo projeto no Railway

```bash
# Via CLI
railway login
railway init

# Ou via web em https://railway.app
```

### 2. Conectar repositório

1. Vá para [railway.app/dashboard](https://railway.app/dashboard)
2. Clique em "New Project"
3. Selecione "GitHub Repo" e autorize
4. Escolha este repositório

### 3. Configurar variáveis de ambiente

Na aba **Variables** do projeto Railway, adicione:

```
DATABASE_URL=postgresql://...  # Railway oferece PostgreSQL plugin
ANTHROPIC_API_KEY=sk-ant-...
FRONTEND_URL=https://seu-app.vercel.app
TWILIO_ACCOUNT_SID=ACxxxxxxxx
TWILIO_AUTH_TOKEN=seu_token
TWILIO_PHONE_NUMBER=whatsapp:+14155238886
```

> **Nota**: Na aba **Plugins**, Railway oferece um plugin de PostgreSQL. Clique em "Add" e Railway vai criar um banco automático e popular `DATABASE_URL`.

### 4. Deploy automático

Railway detecta `railway.json` e faz deploy automaticamente a cada push em `main`.

---

## Frontend → Vercel

### 1. Importar repositório

1. Vá para [vercel.com/new](https://vercel.com/new)
2. Clique em "Import Git Repository"
3. Autorize GitHub e selecione este repo
4. Escolha a pasta raiz: `/`

### 2. Configurar Build Settings

- **Root Directory**: `frontend`
- **Build Command**: `npm run build`
- **Output Directory**: `dist`

### 3. Adicionar Environment Variables

Na aba **Environment Variables**, adicione:

```
VITE_API_URL=https://seu-app.railway.app
```

(Substitua pela URL real do seu backend no Railway)

### 4. Deploy

Clique em "Deploy". Vercel faz deploy automático a cada push em `main`.

---

## Integração Twilio (Produção)

Após ter o backend rodando no Railway:

1. Vá para [console.twilio.com](https://console.twilio.com)
2. Selecione seu número WhatsApp Business
3. Em **Webhook Settings**, configure:
   - **URL**: `https://seu-app.railway.app/api/messages/webhook`
   - **Method**: `HTTP POST`
4. Salve

Agora mensagens reais do WhatsApp vão chamar seu backend! 📱

---

## Banco de dados: SQLite → PostgreSQL

O MVP usa SQLite (um arquivo `suportia.db`). Para produção, Railway oferece PostgreSQL.

### Migração simples

1. No Railway Dashboard, clique em "Add" e procure por "PostgreSQL"
2. Railway vai criar um banco e fornecer `DATABASE_URL`
3. Copie essa URL para a variável `DATABASE_URL` do seu projeto
4. Deploy automático recria as tabelas no Postgres

**Nota importante**: A query `analytics` usa `julianday()` (SQLite). Ao mudar para Postgres, edite [backend/app/routes.py:164](backend/app/routes.py) e troque:

```python
# De (SQLite):
func.julianday(Ticket.resolved_at) - func.julianday(Ticket.created_at)

# Para (PostgreSQL):
func.julianday(Ticket.resolved_at - Ticket.created_at) / 86400
```

Ou melhor ainda:

```python
EXTRACT(EPOCH FROM (Ticket.resolved_at - Ticket.created_at))
```

---

## Troubleshooting

### "Invalid API Key" (Claude API)

Confirme que `ANTHROPIC_API_KEY` está salvo em Railway **Variables**, não em .env do repositório.

### "Connection refused" (Frontend → Backend)

Verifique:
1. URL do backend em `VITE_API_URL` está correta
2. Backend está rodando (`railway logs` deve mostrar logs)
3. CORS está configurado (veja `FRONTEND_URL` no backend)

### "Webhook recebido mas nada acontece"

Verifique logs no Railway:

```bash
railway logs --follow
```

Se vê erro de auth da Anthropic, a chave está errada.

---

## Próximos passos

- [ ] Teste manual via WhatsApp (envie uma mensagem real)
- [ ] Configure CI/CD com GitHub Actions (testes automáticos)
- [ ] Ative backup automático do PostgreSQL
- [ ] Configure domínio personalizado (opcional)
- [ ] Integre Stripe para pagamentos (Fase 3)

---

## Links úteis

- [Railway Docs](https://railway.app/docs)
- [Vercel Docs](https://vercel.com/docs)
- [Anthropic API Docs](https://docs.anthropic.com)
- [Twilio API Docs](https://www.twilio.com/docs)
