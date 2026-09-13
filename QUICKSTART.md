# ⚡ SuportIA — Quick Start (5 minutos)

Comece agora sem ler toda a documentação.

## 1️⃣ Clone e entre no diretório

```bash
cd /Users/henrique/SuportIA
```

## 2️⃣ Backend (Terminal 1)

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

✅ Backend rodando em `http://localhost:8000`

## 3️⃣ Frontend (Terminal 2)

```bash
cd frontend
npm install
npm run dev
```

✅ Frontend rodando em `http://localhost:5173`

## 4️⃣ Login

Abra http://localhost:5173 e use:
- **Usuário**: `admin`
- **Senha**: `admin`

## 5️⃣ Test API (Terminal 3)

```bash
# Criar um ticket manualmente
curl -X POST http://localhost:8000/api/messages/webhook \
  -d "From=whatsapp:+5511988887777" \
  -d "Body=Oi, como vai?" \
  -d "ProfileName=Maria"

# Listar tickets (com token)
curl -H "Authorization: Bearer SEU_TOKEN_AQUI" \
  http://localhost:8000/api/tickets
```

## 📊 Ver em Ação

1. Dashboard: http://localhost:5173/dashboard
2. Analytics: http://localhost:5173/analytics
3. Settings: http://localhost:5173/settings

---

## 🧪 Rodar Testes

```bash
cd backend && source .venv/bin/activate && pytest -v
```

Resultado: ✅ 10/10 testes passando

---

## 🚀 Deploy (Later)

- **Backend**: [Railway](DEPLOYMENT.md#backend--railway)
- **Frontend**: [Vercel](DEPLOYMENT.md#frontend--vercel)

---

## ❓ Próximos Passos

- Leia [README.md](README.md) para arquitetura completa
- Veja [PHASE2.md](PHASE2.md) para o roadmap
- Contribua! [CONTRIBUTING.md](CONTRIBUTING.md)

---

**Pronto?** Comece a usar! 🎉
