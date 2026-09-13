# SuportIA — Roadmap Fase 2

Melhorias e features que serão implementadas na próxima fase.

## 1. Analytics com Gráficos

### Endpoint de série temporal

Novo endpoint no backend:

```python
@router.get("/api/analytics/timeline")
def analytics_timeline(
    days: int = 7,
    db: Session = Depends(get_db),
    username: str = Depends(verify_token)
):
    # Retorna tickets por dia
    # Formato: [{"date": "2025-09-13", "count": 5}, ...]
```

### Frontend com Recharts

```typescript
// frontend/src/components/AnalyticsChart.tsx
import { BarChart } from "recharts";

// Gráfico de volume por dia
// Gráfico de taxa de resolução ao longo do tempo
// Gráfico de tempo médio de resposta
```

---

## 2. Fila de Priorização

### Features

- **Marcar como urgente**: agente pode dar prioridade a um ticket
- **Reordenar manualmente**: drag-and-drop na lista
- **Filtro por prioridade**: show only urgent

### Backend

```python
class Ticket(Base):
    priority = Column(Enum(Priority), default=Priority.NORMAL)
    # Priority = URGENT, HIGH, NORMAL, LOW
```

---

## 3. Exportar Relatórios

### Endpoint

```python
@router.get("/api/tickets/export")
def export_tickets(format: str = "csv"):  # ou "pdf"
    # Retorna arquivo com todos os tickets
```

### Formatos

- CSV (Excel)
- PDF (com formatação)
- JSON (pra integração)

---

## 4. Notificações em Tempo Real

### WebSocket

Quando um novo ticket chega, notificar agentes em tempo real (sem precisar de F5):

```python
from fastapi import WebSocket

@router.websocket("/ws/tickets")
async def websocket_tickets(websocket: WebSocket):
    # Broadcast quando novo ticket chega
```

### Frontend

```typescript
const ws = new WebSocket("wss://api/ws/tickets");
ws.onmessage = (event) => {
  const ticket = JSON.parse(event.data);
  // Mostrar notificação visual
};
```

---

## 5. Suporte a Múltiplos Clientes (WhatsApp, SMS, Email)

Atualmente: apenas WhatsApp via Twilio

Adicionar:

- SMS (Twilio SMS)
- Email (SendGrid)
- Facebook Messenger

```python
class MessageChannel(str, Enum):
    WHATSAPP = "whatsapp"
    SMS = "sms"
    EMAIL = "email"
    MESSENGER = "messenger"

class Ticket(Base):
    channel = Column(Enum(MessageChannel))
```

---

## 6. Fila de Respostas Automáticas (Background Jobs)

Usar **Celery** + **Redis** para processar respostas IA fora da requisição:

```python
# Atualmente: resposta é gerada sincronamente
# Fase 2: salva em fila, processa em background

@task
def generate_ai_response(ticket_id):
    # Rodar em worker separado
    # Notificar agente quando pronto via WebSocket
```

---

## 7. Métricas Avançadas

Adicionar dashboards com:

- Tempo médio de resolução por agente
- Taxa de aprovação vs rejeição
- Satisfação do cliente (rating após resolução)
- Cost per ticket (Twilio + Claude API)
- ROI (economia gerada)

---

## 8. Feedback do Cliente

Após resolver ticket, enviar mensagem:

> "Como foi nosso atendimento? 👍👎"

Cliente reage com emoji, dados são salvos:

```python
class Feedback(Base):
    ticket_id = Column(ForeignKey("tickets.ticket_id"))
    rating = Column(Integer)  # 1-5
    comment = Column(Text, nullable=True)
```

---

## 9. Integração com Stripe

Cobrança por:
- Volume de mensagens processadas
- Ou subscription mensal
- Ou modelo híbrido

```python
@router.post("/api/billing/checkout")
def create_checkout_session(company_id: str):
    # Criar sessão Stripe
```

---

## 10. Autenticação Melhorada

Adicionar:

- **Multi-user**: cada agente tem login próprio
- **Roles**: admin, supervisor, agente
- **SSO**: login via Google/Microsoft
- **2FA**: two-factor authentication

```python
class User(Base):
    role = Column(Enum(UserRole))  # ADMIN, SUPERVISOR, AGENT
```

---

## Timeline estimada

- **Semana 1-2**: Analytics com gráficos + fila de priorização
- **Semana 3**: Exportar relatórios + suporte a múltiplos canais
- **Semana 4**: WebSocket notifications + background jobs
- **Semana 5+**: Feedback, Stripe, autenticação avançada

---

## Como contribuir

Para implementar uma feature:

1. Crie uma branch: `git checkout -b feature/xyz`
2. Implemente a feature com testes
3. Abra um PR descrevendo as mudanças
4. Code review antes de merge

---

Sugestões? Abra uma issue! 🚀
