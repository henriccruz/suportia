# 🚀 SuportIA — Checklist de Deploy em Produção

Data: 2026-09-19  
Status: **🔴 Em Progresso**

---

## 📋 Checklist de Deploy

### **PARTE 1: Backend (Railway)** 🚂

- [ ] **1.1** Atualize a página do Railway (F5)
- [ ] **1.2** Espere pelo novo deployment aparecer (status: "Building" ⏳)
- [ ] **1.3** Confirme quando ficar **"Successful"** ✅
  - Tempo estimado: 3-5 minutos
  - URL será algo como: `https://suportia-...railway.app`
- [ ] **1.4** Copie a **URL pública** do backend
  ```
  Exemplo: https://suportia-prod-abc123.railway.app
  ```
- [ ] **1.5** Guarde essa URL em um lugar seguro (vamos precisar)

---

### **PARTE 2: Frontend (Vercel)** 🎨

- [ ] **2.1** Abra: https://vercel.com/new
- [ ] **2.2** Selecione o repositório **henriccruz/suportia** do GitHub
- [ ] **2.3** Aguarde Vercel escanear o projeto
- [ ] **2.4** Configure Environment Variables:
  ```
  Nome: VITE_API_URL
  Valor: https://suportia-...railway.app
  ```
  (Cole a URL que copiou no passo 1.4)
- [ ] **2.5** Clique em **"Deploy"**
- [ ] **2.6** Espere pelo status "Ready" ✅ (2-3 minutos)
- [ ] **2.7** Copie a **URL do Vercel** (tipo: `https://suportia.vercel.app`)
- [ ] **2.8** Guarde essa URL também!

---

### **PARTE 3: Configurar Webhook Twilio** 🔗

- [ ] **3.1** Abra: https://console.twilio.com/us/console/phone-numbers/incoming
- [ ] **3.2** Clique no seu número de WhatsApp
- [ ] **3.3** Localize a seção **"Messaging"**
- [ ] **3.4** Procure por **"A message comes in"**
- [ ] **3.5** Configure:
  ```
  - Method: HTTP POST (dropdown)
  - URL: https://suportia-...railway.app/api/messages/webhook
  ```
  (Use a URL do Railway do passo 1.4)
- [ ] **3.6** Clique em **"Save"**
- [ ] **3.7** Confirme que foi salvo com sucesso ✅

---

### **PARTE 4: Teste End-to-End** 🧪

- [ ] **4.1** Abra seu **WhatsApp** (real, não sandbox)
- [ ] **4.2** Envie uma mensagem para o número do Twilio
  ```
  Mensagem: "Oi, isso é um teste?"
  ```
- [ ] **4.3** Aguarde 3-5 segundos pela resposta da IA ⏳
- [ ] **4.4** Abra o **Dashboard do SuportIA**:
  ```
  https://suportia.vercel.app
  ```
- [ ] **4.5** Faça Login:
  ```
  Usuário: admin
  Senha: admin
  ```
- [ ] **4.6** Confirme que o ticket apareceu:
  - ✅ Sua mensagem aparece na lista
  - ✅ Status: "Pending Approval"
  - ✅ Resposta da IA está lá
- [ ] **4.7** Clique em **"Approve"** para enviar a resposta
- [ ] **4.8** Confirme que a resposta chegou no WhatsApp ✅

---

## 📊 Resumo de URLs

Quando tudo estiver pronto, você terá:

| Serviço | URL | Status |
|---------|-----|--------|
| **Backend (Railway)** | `https://suportia-...railway.app` | ❌ |
| **Frontend (Vercel)** | `https://suportia.vercel.app` | ❌ |
| **Admin Dashboard** | `https://suportia.vercel.app` | ❌ |
| **WhatsApp Webhook** | `.../api/messages/webhook` | ❌ |

---

## 🔧 Troubleshooting

### Backend não conecta?
```bash
# Teste a conexão:
curl -X GET "https://suportia-...railway.app/api/health"
# Resposta esperada: {"status": "ok"}
```

### Frontend mostra erro de API?
- Verifique se a variável `VITE_API_URL` está correta no Vercel
- Confirme que o Railway URL está **sem slash** no final

### Twilio não recebe webhook?
- Verifique se o URL foi salvo corretamente no Twilio Console
- Confirme que o Railway está rodando (status "Success")

---

## ✅ Quando Está Completo

Você saberá que tudo está funcionando quando:

1. ✅ Dashboard carrega sem erros
2. ✅ Consegue fazer login (admin/admin)
3. ✅ Envia mensagem WhatsApp e recebe resposta da IA
4. ✅ Ticket aparece automaticamente no dashboard
5. ✅ Aprova a resposta e ela volta pro WhatsApp

---

## 💡 Dicas

- **Salve as URLs em um lugar seguro** (você vai precisar depois)
- **Guarde seus tokens do Anthropic/Twilio** (não compartilhe!)
- **Teste com mensagens curtas** antes de coisas complexas
- **Se der erro, ative os logs do Railway** pra debugging

---

**Tempo estimado total: 15-20 minutos** ⏱️

Boa sorte! 🚀

