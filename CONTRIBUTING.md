# Contributing to SuportIA

Obrigado por estar interessado em contribuir! Este documento explica como configurar o ambiente de desenvolvimento e submeter suas mudanças.

## Setup de Desenvolvimento

### Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Rode os testes
pytest

# Inicie o servidor
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev

# Type-checking
npx tsc -b

# Build pra produção
npm run build
```

### Com Docker

```bash
# Suba backend + frontend
docker-compose up

# Backend em http://localhost:8000
# Frontend em http://localhost:5173 (precisa de `npm run dev` adicional)
```

---

## Git Workflow

1. **Crie uma branch** com nome descritivo:
   ```bash
   git checkout -b feature/nova-feature
   # ou
   git checkout -b bugfix/corrigir-xyz
   ```

2. **Commit com mensagens claras**:
   ```bash
   git commit -m "Add feature XYZ

   - Detailed explanation
   - Of what changed
   - And why
   "
   ```

3. **Push e abra um PR**:
   ```bash
   git push origin feature/nova-feature
   ```

4. **Descreva seu PR** com:
   - O que foi implementado
   - Por quê
   - Como testar
   - Screenshots (se UI)

---

## Padrões de Código

### Backend (Python)

- Use **type hints** em todas as funções
- Máx 88 caracteres por linha (Black)
- Docstrings em português
- Testes para toda lógica nova

Exemplo:

```python
def create_ticket(
    customer_phone: str,
    message_text: str,
    db: Session = Depends(get_db),
) -> Ticket:
    """Cria um novo ticket a partir da mensagem do cliente."""
    ticket = Ticket(
        customer_phone=customer_phone,
        message_text=message_text,
    )
    db.add(ticket)
    db.commit()
    return ticket
```

### Frontend (TypeScript/React)

- Use **TypeScript**, sem `any`
- Componentes funcionais com hooks
- Pasta `src/lib` para lógica
- Pasta `src/components` para componentes reutilizáveis
- Pasta `src/pages` para páginas de rotas

Exemplo:

```typescript
interface TicketProps {
  ticketId: string;
  onApprove: (id: string) => void;
}

export default function TicketDetail({ ticketId, onApprove }: TicketProps) {
  const [ticket, setTicket] = useState<Ticket | null>(null);
  // ...
}
```

---

## Testes

### Backend

```bash
cd backend
pytest                          # Roda todos os testes
pytest tests/test_auth.py       # Testa módulo específico
pytest -v                       # Verbose
pytest --cov=app               # Com cobertura
```

Adicione testes para toda funcionalidade nova:

```python
def test_novo_endpoint(client, auth_token):
    headers = {"Authorization": f"Bearer {auth_token}"}
    response = client.post("/api/xyz", headers=headers)
    assert response.status_code == 200
```

### Frontend

Testes com Vitest (a adicionar em Fase 2).

---

## Issues e Bugs

Ao reportar um bug:

1. Descreva o comportamento esperado vs atual
2. Passos para reproduzir
3. Screenshots se possível
4. Seu ambiente (OS, navegador, etc)

---

## Documentação

Mude algo? Atualize a documentação:

- README.md pra features principais
- PHASE2.md pra planejamento
- Code comments pra lógica complexa
- Docstrings pra funções públicas

---

## Code Review

Seu PR será revisado por pelo menos 1 contribuidor antes de merge. Esperamos:

- Código limpo e testado
- Sem quebra de features existentes
- Documentação atualizada
- Commits com histórico claro

---

## Perguntas?

- Abra uma **issue** no GitHub
- Comente no **PR**
- Mande uma mensagem 📧

Agradecemos sua contribuição! 🚀
