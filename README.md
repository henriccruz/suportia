# SuportIA — Customer Support AI Platform (MVP)

Plataforma que recebe mensagens via WhatsApp/SMS (Twilio), processa com a Claude API
e retorna respostas automáticas, com um dashboard React para revisar, aprovar ou
customizar as respostas antes de resolver os tickets.

**Status**: MVP pronto para produção | **Próxima fase**: Analytics avançado, WebSocket, multi-canal

**Links rápidos**: [Deployment Guide](DEPLOYMENT.md) | [Roadmap Fase 2](PHASE2.md) | [Como Contribuir](CONTRIBUTING.md)

## Estrutura do projeto

```
SuportIA/
  backend/          # FastAPI + SQLAlchemy + Anthropic SDK + Twilio SDK
    app/
      main.py            # app FastAPI, CORS, startup
      routes.py          # todos os endpoints da API
      models.py          # schemas Pydantic (request/response)
      database.py        # engine SQLAlchemy, modelos ORM, init_db
      claude_service.py  # integração com a Claude API
      twilio_service.py  # integração com Twilio (envio de mensagens)
      config.py          # leitura de variáveis de ambiente
    requirements.txt
    .env.example
  frontend/         # React + TypeScript (Vite)
    src/
      components/  # Dashboard, TicketList, TicketDetail, Analytics, Settings
      pages/       # rotas: index, tickets, analytics, settings
      lib/         # api.ts (cliente HTTP), types.ts
    package.json
    .env.example
```

> Nota: o briefing original citava Create React App (`REACT_APP_API_URL`). Este MVP usa
> **Vite** por ser mais leve e rápido para desenvolvimento; a variável de ambiente
> equivalente é `VITE_API_URL`.

## Como rodar localmente

### 1. Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# edite .env e preencha ANTHROPIC_API_KEY (obrigatório para respostas de IA reais)
uvicorn app.main:app --reload --port 8000
```

O SQLite (`suportia.db`) é criado automaticamente no primeiro start. A API sobe em
`http://localhost:8000` (docs interativas em `/docs`).

### 2. Frontend

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

O dashboard sobe em `http://localhost:5173`.

### 3. Testar o webhook localmente (sem Twilio de verdade)

```bash
curl -X POST http://localhost:8000/api/messages/webhook \
  -d "From=whatsapp:+5511999999999" \
  -d "Body=Meu pedido não chegou, o que faço?" \
  -d "ProfileName=Maria"
```

Isso cria um ticket, gera a resposta com a Claude API e retorna um TwiML de resposta.
Sem `TWILIO_ACCOUNT_SID`/`TWILIO_AUTH_TOKEN` configurados, o envio real via Twilio é
simulado (apenas logado no console) — assim dá pra testar sem uma conta Twilio.

### 4. Conectar ao Twilio de verdade (WhatsApp Sandbox)

1. Crie uma conta em https://www.twilio.com e ative o WhatsApp Sandbox.
2. Preencha `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN` e `TWILIO_PHONE_NUMBER`
   (formato `whatsapp:+14155238886`) no `.env` do backend.
3. Exponha seu backend local (ex: `ngrok http 8000`) e configure a URL
   `https://<seu-ngrok>.ngrok.io/api/messages/webhook` como webhook de mensagens
   recebidas no console do Twilio.

## Fluxo de um ticket

1. Cliente manda mensagem pelo WhatsApp → Twilio chama `POST /api/messages/webhook`.
2. O backend salva a mensagem, chama a Claude API e responde automaticamente ao
   cliente via TwiML, criando um ticket com status `pending_approval` para revisão.
3. No dashboard, o agente pode:
   - **Aprovar**: marca o ticket como `resolved` (`resolution_type=ai_approved`) e
     reenvia a resposta da IA como confirmação final.
   - **Rejeitar**: marca como `rejected` para tratamento manual.
   - **Enviar resposta customizada**: grava `manual_response`, marca como `resolved`
     (`resolution_type=manual`) e envia a mensagem ao cliente via Twilio.

## Endpoints da API

| Método | Rota | Descrição |
|---|---|---|
| POST | `/api/messages/webhook` | Recebe webhook do Twilio, gera resposta com IA e responde via TwiML |
| GET | `/api/tickets` | Lista últimos 100 tickets (filtros: `status`, `date_from`, `date_to`) |
| GET | `/api/tickets/{id}` | Detalhe de um ticket + histórico de conversa |
| POST | `/api/tickets/{id}/approve` | Aprova resposta da IA e resolve o ticket |
| POST | `/api/tickets/{id}/reject` | Rejeita a resposta da IA (revisão manual) |
| POST | `/api/tickets/{id}/custom-response` | Envia resposta customizada e resolve o ticket |
| GET | `/api/analytics` | Métricas agregadas (total, % resolvido por IA, tempo médio, taxa de sucesso) |

## Variáveis de ambiente

Backend (`backend/.env`):

```
TWILIO_ACCOUNT_SID=
TWILIO_AUTH_TOKEN=
TWILIO_PHONE_NUMBER=
ANTHROPIC_API_KEY=
ANTHROPIC_MODEL=claude-3-5-sonnet-20241022
DATABASE_URL=sqlite:///./suportia.db
FRONTEND_URL=http://localhost:5173
STRIPE_API_KEY=
```

Frontend (`frontend/.env`):

```
VITE_API_URL=http://localhost:8000
```

## Testes

### Backend

```bash
cd backend && source .venv/bin/activate && pytest
```

Testes incluem:
- Autenticação (hash/verify, token creation)
- Endpoints protegidos (require auth)
- Login/logout flow
- Analytics calculation

### Frontend

Frontend atualmente sem testes automatizados. Roadmap Fase 2: Vitest + React Testing Library.

---

## Docker

Suba toda a stack com Docker:

```bash
docker-compose up
```

Isso inicia:
- Backend FastAPI em `http://localhost:8000`
- (Frontend precisa de setup adicional, ver `DEPLOYMENT.md`)

---

## Deploy

### Backend → Railway

1. Crie um projeto no [Railway](https://railway.app) e conecte este repositório
   (pasta `backend/`).
2. Configure o *start command*: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`.
3. Adicione as variáveis de ambiente listadas acima como *Variables* do projeto.
   Para produção, troque `DATABASE_URL` para um Postgres (Railway oferece um
   plugin de Postgres pronto) — veja a nota abaixo sobre `analytics`.
4. Deploy automático a cada push na branch conectada.

### Frontend → Vercel

1. Crie um projeto na [Vercel](https://vercel.com) apontando para a pasta `frontend/`.
2. Framework preset: Vite.
3. Adicione a env var `VITE_API_URL` com a URL pública do backend no Railway.
4. Deploy automático a cada push.

### Nota sobre PostgreSQL

A query de `avg_response_time_seconds` em `backend/app/routes.py` usa `julianday()`,
uma função específica do SQLite. Ao migrar `DATABASE_URL` para Postgres, troque essa
expressão por `EXTRACT(EPOCH FROM (resolved_at - created_at))`.

## Roadmap (conforme prioridades do briefing)

- **Semana 1 (MVP)**: backend FastAPI, integração Claude, SQLite, dashboard básico,
  aprovar/rejeitar. ✅ Implementado neste repositório.
- **Semana 2**: integração Twilio completa em produção, autenticação de agentes,
  analytics mais completo (gráfico de volume por dia), polish de UI/UX.
- **Semana 3**: deploy Railway + Vercel, cobrança via Stripe, suporte multi-tenant
  (múltiplas empresas/clientes).
