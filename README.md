# 🚀 WhatsApp Atendimento SaaS
Sistema de atendimento multicanal WhatsApp com BOT automático e atendimento humano.

**Stack:** FastAPI · Flet · Supabase · Redis · MinIO · Evolution API

---

## 📁 Estrutura

```
WHATSAPP-ATENDIMENTO/
├── .env                          # Variáveis de ambiente
├── docker-compose.yml            # Orquestração dos serviços
├── requirements.txt              # Dependências Python
├── database/
│   ├── schema.sql                # Schema completo do banco
│   └── seed.sql                  # Dados iniciais
├── backend/                      # API FastAPI
│   ├── main.py                   # App principal
│   ├── config.py                 # Configurações (.env)
│   ├── database.py               # Cliente Supabase
│   ├── redis_client.py           # Cliente Redis
│   ├── minio_client.py           # Cliente MinIO
│   ├── models/schemas.py         # Pydantic models
│   ├── routers/
│   │   ├── webhook.py            # ⭐ Core: BOT vs HUMANO
│   │   ├── auth.py               # Login/JWT
│   │   ├── contacts.py           # CRM + Takeover
│   │   ├── messages.py           # Histórico + Envio
│   │   ├── broadcasts.py         # Agendamentos
│   │   └── admin.py              # SuperAdmin
│   └── services/
│       ├── bot_service.py        # Processamento de flows
│       ├── evolution_service.py  # Evolution API
│       ├── broadcast_service.py  # Scheduler de broadcasts
│       └── media_service.py      # Upload MinIO
└── frontend/                     # Interface Flet
    ├── main.py                   # Entrypoint + Rotas
    ├── theme.py                  # Design Transforma Futuro
    ├── state.py                  # Estado global
    ├── api_client.py             # HTTP client
    ├── realtime.py               # Polling de mensagens
    ├── pages/
    │   ├── login.py              # Tela de login
    │   ├── dashboard.py          # Layout 3 colunas
    │   ├── broadcasts.py         # Broadcasts
    │   ├── settings.py           # Configurações
    │   └── admin.py              # SuperAdmin
    └── components/
        ├── sidebar.py            # Menu retrátil
        ├── chat_list.py          # Lista de conversas
        ├── chat_window.py        # Área de chat
        ├── crm_panel.py          # Painel CRM direito
        └── message_bubble.py    # Bolhas de mensagem
```

---

## ⚡ Instalação Rápida

### 1. Instalar dependências
```bash
pip install -r requirements.txt
```

### 2. Configurar `.env`
Edite o arquivo `.env` com suas credenciais:
- **Supabase:** URL e chaves já configuradas para ambiente local
- **Redis:** `redis://redis:6379/0` (VPS) ou `redis://localhost:6379/0` (local)
- **MinIO:** Endpoint e credenciais já configuradas
- **Evolution API:** Insira a URL da sua instância Evolution

### 3. Criar o banco de dados
Execute no **Supabase SQL Editor**:
```sql
-- Cole o conteúdo de database/schema.sql
-- Cole o conteúdo de database/seed.sql
```

### 4. Iniciar o Backend
```bash
# Da raiz do projeto:
uvicorn backend.main:app --reload --port 8000
```
Acesse a documentação: http://localhost:8000/docs

### 5. Iniciar o Frontend
```bash
python frontend/main.py
```
Acesse: http://localhost:8080

---

## 🐳 Docker (VPS)

```bash
# Cria a rede externa se ainda não existir
docker network create network

# Inicia os serviços
docker-compose up -d

# Ver logs
docker-compose logs -f api
```

---

## 🔑 Credenciais Padrão

| Usuário | E-mail | Senha |
|---------|--------|-------|
| SuperAdmin | superadmin@transformafuturo.com | `Admin@2024` |
| Admin Demo | admin@demo.com | `Demo@2024` |
| Agente Demo | agente@demo.com | `Demo@2024` |

> ⚠️ **Troque as senhas imediatamente em produção!**

---

## 🔗 Configurar Webhook na Evolution API

No painel da Evolution API, configure o webhook para:
```
POST http://seu-servidor:8000/webhook/evolution
```

**Eventos para habilitar:**
- `messages.upsert` ✅
- `messages.update` ✅

---

## 🧠 Lógica BOT vs HUMANO

```
Mensagem recebida
      │
      ▼
Redis: chat_status:{company_id}:{phone}
      │
      ├── "bot"    → Processa chat_flows → Responde automaticamente
      ├── "human"  → Apenas salva + notifica agente via Realtime
      └── "paused" → Ignora completamente
```

**Mudar para HUMANO:** Clique "Assumir Atendimento" no chat  
**Voltar para BOT:** Clique "Devolver ao Bot"

---

## 📡 Endpoints Principais

| Método | Rota | Descrição |
|--------|------|-----------|
| `POST` | `/auth/login` | Login com JWT |
| `POST` | `/webhook/evolution` | Recebe mensagens WhatsApp |
| `GET`  | `/contacts` | Lista conversas |
| `POST` | `/contacts/{id}/takeover` | Assume atendimento |
| `POST` | `/contacts/{id}/release` | Devolve ao bot |
| `GET`  | `/messages/{contact_id}` | Histórico de mensagens |
| `POST` | `/messages/send` | Envia mensagem |
| `POST` | `/broadcasts` | Cria broadcast |
| `GET`  | `/admin/stats` | Stats (SuperAdmin) |
| `GET`  | `/health` | Health check |

---

## 🎨 Identidade Visual

- **Fundo:** `#050810` (preto profundo)
- **Primário:** `#00E5CC` (ciano neon)
- **Secundário:** `#00FF88` (verde neon)
- **Tipografia:** Roboto + Roboto Mono
