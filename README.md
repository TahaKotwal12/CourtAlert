<div align="center">

```
 ██████╗ ██████╗ ██╗   ██╗██████╗ ████████╗ █████╗ ██╗     ███████╗██████╗ ████████╗
██╔════╝██╔═══██╗██║   ██║██╔══██╗╚══██╔══╝██╔══██╗██║     ██╔════╝██╔══██╗╚══██╔══╝
██║     ██║   ██║██║   ██║██████╔╝   ██║   ███████║██║     █████╗  ██████╔╝   ██║   
██║     ██║   ██║██║   ██║██╔══██╗   ██║   ██╔══██║██║     ██╔══╝  ██╔══██╗   ██║   
╚██████╗╚██████╔╝╚██████╔╝██║  ██║   ██║   ██║  ██║███████╗███████╗██║  ██║   ██║   
 ╚═════╝ ╚═════╝  ╚═════╝ ╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝╚══════╝╚══════╝╚═╝  ╚═╝   ╚═╝   
```

### ⚖️ Court Date Reminders for Unrepresented Litigants in India

*No lawyer. No app. No missed hearing.*

---

[![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18-61DAFB?style=for-the-badge&logo=react&logoColor=black)](https://react.dev)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-336791?style=for-the-badge&logo=postgresql&logoColor=white)](https://postgresql.org)
[![Celery](https://img.shields.io/badge/Celery-5.3-37814A?style=for-the-badge&logo=celery&logoColor=white)](https://docs.celeryq.dev)
[![Twilio](https://img.shields.io/badge/Twilio-WhatsApp%2FSMS-F22F46?style=for-the-badge&logo=twilio&logoColor=white)](https://twilio.com)
[![Featherless.ai](https://img.shields.io/badge/Featherless.ai-LLM-8B5CF6?style=for-the-badge)](https://featherless.ai)
[![License: MIT](https://img.shields.io/badge/License-MIT-D4A843?style=for-the-badge)](LICENSE)

---

**[🚀 Live Demo](https://courtalert.vercel.app)** · **[📖 API Docs](https://courtalert.up.railway.app/docs)** · **[📋 FSD Document](docs/FSD.pdf)** · **[🗄 DB Schema](docs/DB_Schema.pdf)**

</div>

---

## 📌 The Problem

> *"A farmer from Marathwada takes 2 days off work, travels 80 km to the district court — only to find the case was adjourned 3 weeks ago. He was marked absent. His land dispute case is now ex-parte against him."*

India has **40+ million pending court cases**. A significant majority of litigants appear **without legal representation** — meaning no one tracks their hearing dates for them.

- 📵 Case status is online, but rural citizens lack digital literacy
- 📬 Court notices via post are unreliable
- ⚖️ A single missed date = case dismissed, ex-parte order, or arrest warrant
- 🏛️ Legal aid NGOs are understaffed to track individual cases at scale

**CourtAlert fixes this with a single WhatsApp message.**

---

## 💡 The Solution

CourtAlert sends **automated WhatsApp/SMS reminders** 7, 3, and 1 day before every scheduled court hearing — by polling the **eCourts India public API** daily and using **Featherless.ai's LLM** to generate plain-language, multilingual explanations.

```
User sends:  "REG MHPN010123456 HI"
                        │
                        ▼
             CourtAlert validates CNR
             via eCourts India API
                        │
                        ▼
             Featherless.ai generates
             message in Hindi
                        │
                        ▼
User gets:   "नमस्ते! आपके मामले Patil vs State में
              अगली सुनवाई 10 मई 2026 को है।
              यह Final Arguments की सुनवाई है —
              आपको कोर्ट में उपस्थित रहना है।
              📍 District Court Pune, Court No. 3
              🗺️ [Maps Link]"
```

**No app download. No smartphone literacy. Works on any phone.**

---

## ✨ Features

| Feature | Description |
|---|---|
| 📱 **WhatsApp & SMS** | Works on any mobile — even basic feature phones via SMS fallback |
| 🔔 **Smart Reminders** | Automatic alerts at 7 days, 3 days, and 1 day before hearing |
| 🌐 **6 Regional Languages** | Hindi, Marathi, Telugu, Tamil, Kannada, English |
| 🤖 **AI Legal Explainer** | Featherless.ai explains "Interlocutory Application" in plain words |
| 📍 **Court Locator** | Google Maps deep link to the court's exact location |
| 📋 **NGO Dashboard** | Web UI for bulk case registration and delivery monitoring |
| 🔒 **Privacy First** | Phone numbers hashed; no personal data shared with third parties |
| ♻️ **Auto-retry** | WhatsApp → SMS fallback on delivery failure |

---

## 🛠️ Tech Stack

```
┌─────────────────────────────────────────────────────────────┐
│                        FRONTEND                              │
│   React 18 + Vite  │  Tailwind CSS  │  Zustand  │  Recharts │
├─────────────────────────────────────────────────────────────┤
│                        BACKEND                               │
│     FastAPI (Python 3.11)  │  SQLAlchemy 2.0  │  Alembic    │
├─────────────────────────────────────────────────────────────┤
│                     BACKGROUND JOBS                          │
│           Celery + Redis  │  Celery Beat (CRON)              │
├──────────────┬──────────────────┬───────────────────────────┤
│   DATABASE   │    MESSAGING     │          AI / LLM          │
│  PostgreSQL  │  Twilio (WA+SMS) │      Featherless.ai        │
├──────────────┴──────────────────┴───────────────────────────┤
│                    EXTERNAL APIs                             │
│    eCourts India REST API (NIC)  │  Google Maps API          │
├─────────────────────────────────────────────────────────────┤
│                     DEPLOYMENT                               │
│       Railway (API + DB + Redis + Celery)  │  Vercel (SPA)   │
└─────────────────────────────────────────────────────────────┘
```

---

## 🗂️ Project Structure

```
courtalert/
├── 📁 backend/                     # FastAPI application
│   ├── app/
│   │   ├── main.py                 # App factory + CORS + router registration
│   │   ├── routers/
│   │   │   ├── auth.py             # POST /auth/register, /login, GET /me
│   │   │   ├── cases.py            # CRUD registrations + bulk upload + sync
│   │   │   ├── notifications.py    # Alert logs + delivery stats
│   │   │   ├── webhooks.py         # POST /webhook/twilio (inbound messages)
│   │   │   └── stats.py            # Dashboard overview metrics
│   │   ├── services/
│   │   │   ├── ecourts.py          # eCourts India API client (httpx async)
│   │   │   ├── featherless.py      # Featherless.ai LLM message generation
│   │   │   ├── twilio_service.py   # WhatsApp/SMS send + parse commands
│   │   │   └── maps_service.py     # Court location + Google Maps links
│   │   ├── models/                 # SQLAlchemy ORM models
│   │   │   ├── user.py
│   │   │   ├── registration.py
│   │   │   ├── hearing.py
│   │   │   └── notification.py
│   │   ├── schemas/                # Pydantic request/response schemas
│   │   ├── tasks/
│   │   │   ├── celery_app.py       # Celery + Beat config + CRON schedule
│   │   │   ├── polling.py          # poll_all_cases + sync_single_case
│   │   │   └── alerts.py           # send_due_alerts + retry_failed
│   │   └── core/
│   │       ├── config.py           # pydantic-settings env var loading
│   │       ├── database.py         # Async SQLAlchemy engine + session
│   │       └── security.py         # JWT + bcrypt utilities
│   ├── alembic/                    # DB migration files
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
│
├── 📁 frontend/                    # React SPA
│   ├── src/
│   │   ├── pages/                  # LoginPage, Dashboard, Cases, Notifications...
│   │   ├── components/             # CaseCard, HearingTimeline, AlertLog...
│   │   ├── store/                  # Zustand: authStore, casesStore
│   │   ├── api/                    # Axios client + casesApi, authApi, statsApi
│   │   └── hooks/                  # React Query: useCases, useCaseDetail, useStats
│   ├── vite.config.js
│   ├── tailwind.config.js
│   └── .env.example
│
├── 📁 docs/                        # Project documentation
│   ├── FSD.pdf                     # Full Stack Design Document
│   ├── DB_Schema.pdf               # Database schema + ERD
│   └── API_Spec.pdf                # Full API reference
│
├── docker-compose.yml              # Local dev: PostgreSQL + Redis
└── README.md
```

---

## ⚡ Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- Docker & Docker Compose
- Twilio account (free sandbox works)
- Featherless.ai API key (free with ImpactHacks 2026)

### 1. Clone the repo

```bash
git clone https://github.com/your-username/courtalert.git
cd courtalert
```

### 2. Start PostgreSQL + Redis

```bash
docker-compose up -d
```

### 3. Backend setup

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Copy env file and fill in your keys
cp .env.example .env

# Run database migrations
alembic upgrade head

# Start FastAPI dev server
uvicorn app.main:app --reload --port 8000

# In a new terminal — start Celery worker
celery -A app.tasks.celery_app worker --loglevel=info

# In a new terminal — start Celery Beat (CRON scheduler)
celery -A app.tasks.celery_app beat --loglevel=info
```

### 4. Frontend setup

```bash
cd frontend

# Install dependencies
npm install

# Copy env file
cp .env.example .env

# Start React dev server
npm run dev
```

### 5. Open in browser

| Service | URL |
|---|---|
| React Dashboard | http://localhost:5173 |
| FastAPI Server | http://localhost:8000 |
| **Swagger UI (Auto-docs)** | **http://localhost:8000/docs** |
| ReDoc | http://localhost:8000/redoc |

---

## 🔐 Environment Variables

### Backend (`backend/.env`)

```env
# Database
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/courtalert
REDIS_URL=redis://localhost:6379/0

# JWT Auth
SECRET_KEY=your-super-secret-key-generate-with-openssl-rand-hex-32
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080

# Twilio
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886
TWILIO_SMS_NUMBER=+1XXXXXXXXXX

# Featherless.ai
FEATHERLESS_API_KEY=your_featherless_api_key
FEATHERLESS_MODEL=meta-llama/Llama-3-8B-Instruct

# eCourts India API
ECOURTS_BASE_URL=https://services.ecourts.gov.in/ecourtindia_v6/

# Google Maps (optional)
GOOGLE_MAPS_API_KEY=your_google_maps_key

# CORS
CORS_ORIGINS=http://localhost:5173,https://courtalert.vercel.app

# Celery
CELERY_TIMEZONE=Asia/Kolkata
```

### Frontend (`frontend/.env`)

```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
VITE_APP_NAME=CourtAlert
```

---

## 📡 API Overview

Base URL: `/api/v1` · Full docs auto-generated at `/docs`

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| `POST` | `/auth/register` | ❌ | Register NGO user |
| `POST` | `/auth/login` | ❌ | Login → JWT token |
| `GET` | `/auth/me` | ✅ | Get current user |
| `POST` | `/cases/register` | ✅ | Register case for alerts |
| `GET` | `/cases` | ✅ | List all cases (paginated) |
| `GET` | `/cases/{id}` | ✅ | Case detail + hearings |
| `POST` | `/cases/{id}/sync` | ✅ | Force sync with eCourts |
| `POST` | `/cases/bulk-upload` | ✅ | Upload CSV (max 500 rows) |
| `GET` | `/notifications` | ✅ | Alert delivery log |
| `POST` | `/notifications/test` | ✅ | Send test WhatsApp |
| `POST` | `/webhook/twilio` | ❌ | Inbound WhatsApp handler |
| `GET` | `/stats/overview` | ✅ | Dashboard metrics |

### WhatsApp Commands

| Message | Action |
|---|---|
| `REG CNRXXXXXXXX HI` | Register case (CNR + language code) |
| `STATUS` | Get next hearing date |
| `STOP` | Unsubscribe from alerts |

**Language codes:** `HI` Hindi · `MR` Marathi · `TE` Telugu · `TA` Tamil · `KN` Kannada · `EN` English

---

## 🗄️ Database Schema

```
users ──────────────────────────────────────────────────────────┐
  id (UUID PK) · email · hashed_password · org_name · role      │
                                                                 │
registrations ────────────────────────────────────────────── FK(users.id)
  id (UUID PK) · cnr_number · phone_number · language            │
  case_title · court_name · state_code · is_active               │
  registered_by · last_synced_at · created_at                    │
         │                    │                                   
         │                    └─────────────────────────────────┐
hearings ─────────────────────────────────────────── FK(registrations.id)
  id · registration_id · hearing_date · hearing_type             │
  court_room · judge_name · is_completed · fetched_at            │
         │                                                       │
notifications ──────────────────────────────── FK(registrations.id, hearings.id)
  id · registration_id · hearing_id · channel (whatsapp/sms)
  status (sent/delivered/failed) · message_text · days_before
  twilio_sid · sent_at · delivered_at

whatsapp_commands ──────────────────────────── FK(registrations.id)
  id · from_number · body · command_type · cnr_extracted
  language_extracted · response_sent · received_at

courts (static reference)
  id · state_code · court_name · address · latitude · longitude
```

---

## ⚙️ Background Tasks (Celery)

| Task | Schedule | Description |
|---|---|---|
| `poll_all_cases` | Daily 6:00 AM IST | Polls eCourts API for all active registrations |
| `send_due_alerts` | Daily 7:00 AM IST | Sends alerts for hearings within 1/3/7 days |
| `retry_failed_notifications` | Every 2 hours | WhatsApp → SMS fallback retry |
| `sync_single_case` | On-demand | Triggered on new registration or manual sync |
| `cleanup_old_hearings` | Weekly Sunday | Archives hearings older than 6 months |

---

## 🚀 Deployment

### Backend → Railway

```bash
# 1. Push to GitHub
# 2. railway.app → New Project → Deploy from GitHub → select backend/
# 3. Add plugins: PostgreSQL + Redis
# 4. Add env vars in Variables tab
# 5. Add second service for Celery Worker:
#    Start command: celery -A app.tasks.celery_app worker --loglevel=info
# 6. Add third service for Celery Beat:
#    Start command: celery -A app.tasks.celery_app beat
# 7. Set Twilio webhook: https://your-app.up.railway.app/api/v1/webhook/twilio
```

### Frontend → Vercel

```bash
# 1. vercel.com → New Project → Import GitHub
# 2. Set Root Directory: frontend/
# 3. Add env var: VITE_API_BASE_URL=https://your-railway-app.up.railway.app/api/v1
# 4. Deploy → copy URL → add to CORS_ORIGINS in Railway
```

---

## 🌐 How Featherless.ai Powers CourtAlert

```python
from openai import OpenAI

client = OpenAI(
    base_url="https://api.featherless.ai/v1",
    api_key=settings.FEATHERLESS_API_KEY
)

async def generate_alert_message(hearing: dict, language: str) -> str:
    response = client.chat.completions.create(
        model="meta-llama/Llama-3-8B-Instruct",
        messages=[
            {
                "role": "system",
                "content": f"You are a legal assistant. Explain court hearings simply in {language}. "
                           "Always include: date, court location, what to bring, and what the hearing type means."
            },
            {
                "role": "user", 
                "content": f"Generate a WhatsApp reminder for this hearing: {hearing}"
            }
        ]
    )
    return response.choices[0].message.content
```

**Use cases:**
- 🗣️ Plain-language hearing type explanation ("Final Arguments" → what it actually means)
- 🌐 Translation into 6 regional languages
- 📋 "What to bring" checklist per hearing type
- 📝 Post-hearing outcome summary

---

## 🤝 How to Contribute

1. **Fork** the repo
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit changes: `git commit -m "feat: add your feature"`
4. Push: `git push origin feature/your-feature`
5. Open a **Pull Request**

### Development Guidelines

- Follow [Conventional Commits](https://conventionalcommits.org/) for commit messages
- Run `alembic revision --autogenerate -m "description"` for DB schema changes
- All new API endpoints must have Pydantic schemas and be reflected in `/docs`
- Test with real CNR numbers before submitting PR

---

## 🗺️ Roadmap

- [x] WhatsApp registration flow
- [x] eCourts India API integration
- [x] Featherless.ai multilingual alert generation
- [x] Daily Celery CRON polling pipeline
- [x] NGO admin dashboard (React)
- [x] Bulk CSV upload for batch registration
- [x] Twilio delivery status tracking
- [ ] SMS fallback auto-retry
- [ ] Google Maps court locator integration
- [ ] High Court jurisdiction support
- [ ] NALSA partnership integration
- [ ] Mobile app (React Native)
- [ ] Open API for third-party legal NGOs

---

## 📊 Impact

| Metric | Value |
|---|---|
| Pending cases in India | 40+ million |
| Litigants without representation | ~75% |
| Legal need unmet (low income) | 80%+ |
| UN SDG addressed | **SDG 16** — Peace, Justice & Strong Institutions |
| Languages supported | 6 |
| Minimum device required | Any mobile phone (SMS) |

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

## 🙏 Acknowledgements

- **[eCourts India (NIC)](https://services.ecourts.gov.in)** — public case data API
- **[Featherless.ai](https://featherless.ai)** — LLM inference platform
- **[Twilio](https://twilio.com)** — WhatsApp & SMS infrastructure
- **[ImpactHacks 2026](https://devpost.com/hackathons)** — built for this hackathon

---

<div align="center">

**Built with ⚖️ for the 40 million.**

*Every litigant deserves to know when their day in court is.*

[![GitHub stars](https://img.shields.io/github/stars/your-username/courtalert?style=social)](https://github.com/your-username/courtalert)
[![GitHub forks](https://img.shields.io/github/forks/your-username/courtalert?style=social)](https://github.com/your-username/courtalert)

</div>
