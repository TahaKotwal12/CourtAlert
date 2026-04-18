# CourtAlert — Application Flow & Architecture

> **ImpactHacks 2026** | Legal notification system for unrepresented litigants in India

---

## What It Does

CourtAlert sends automated WhatsApp/SMS reminders to poor and unrepresented litigants in India so they never miss a court hearing. NGO workers register cases on behalf of litigants; the system polls eCourts India for hearing dates and sends multilingual alerts 7, 3, and 1 day before each hearing.

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          COURTALERT SYSTEM                              │
│                                                                         │
│   ┌──────────────┐     ┌──────────────────┐     ┌───────────────────┐  │
│   │  NGO WORKER  │     │  FASTAPI BACKEND  │     │   NEONDB (PG 15)  │  │
│   │  (Dashboard) │────▶│  Python 3.12      │────▶│   6 Tables        │  │
│   └──────────────┘     │  Port 8000        │     │   NeonDB Cloud    │  │
│                        └────────┬─────────┘     └───────────────────┘  │
│   ┌──────────────┐              │                                       │
│   │   LITIGANT   │              │                                       │
│   │  (WhatsApp/  │◀─────────────┤                                       │
│   │   SMS only)  │              │                                       │
│   └──────────────┘     ┌────────▼─────────┐     ┌───────────────────┐  │
│                        │  CELERY WORKERS   │     │   REDIS           │  │
│                        │  + BEAT SCHEDULER │────▶│   Task Queue      │  │
│                        └──────────────────┘     └───────────────────┘  │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## User Roles

| Role | Who | Access |
|------|-----|--------|
| `admin` | CourtAlert team | All data, all users, trigger jobs |
| `ngo_user` | NGO / Legal Aid worker | Own registrations only |
| Litigant | Person with a court case | WhatsApp/SMS only — never logs in |

---

## Complete Application Flow

### Phase 1 — NGO Onboarding

```
NGO Worker
    │
    ├── POST /api/v1/auth/register
    │       { email, password, full_name, org_name }
    │       → Creates account in users table (role = ngo_user)
    │
    └── POST /api/v1/auth/login
            { email, password }
            → Returns JWT token (valid 7 days)
```

---

### Phase 2 — Case Registration

```
NGO Worker (authenticated)
    │
    ├── Single case
    │   POST /api/v1/cases/register
    │       { cnr_number, phone_number, language }
    │              │
    │              ├── Validates CNR via eCourts India API (mocked)
    │              ├── Saves case → registrations table
    │              └── Fetches & saves upcoming hearings → hearings table
    │
    └── Bulk upload
        POST /api/v1/cases/bulk-upload
            CSV file (up to 500 rows)
            Columns: cnr_number, phone_number, language
```

**CNR Format:** `DLHC010012342022` (4 letters + 12 digits)
**Languages:** `hi` Hindi · `mr` Marathi · `ta` Tamil · `te` Telugu · `kn` Kannada · `en` English

---

### Phase 3 — Self-Registration via WhatsApp

```
Litigant (WhatsApp)
    │
    ├── Sends: "REG MHBM010012342024 HI"
    │              │
    │              ├── Twilio receives → POST /api/v1/webhook/twilio
    │              ├── Parses CNR + language from message
    │              ├── Validates CNR via eCourts
    │              ├── Creates registration (registered_by = NULL)
    │              └── Replies: "✅ Registered! Next hearing: 12 Apr 2026"
    │
    ├── Sends: "STATUS"
    │              └── Replies with list of active cases
    │
    └── Sends: "STOP"
                   └── Deactivates all registrations, stops all alerts
```

---

### Phase 4 — Automated Daily Sync (7:00 AM IST)

```
Celery Beat Scheduler
    │
    └── Triggers: daily_sync_task
                    │
                    ├── Loads all active registrations from DB
                    ├── Calls eCourts API for each CNR
                    ├── Updates case metadata (title, court name)
                    └── Inserts new hearing dates if changed
```

---

### Phase 5 — Automated Alert Sending (8:00 AM IST)

```
Celery Beat Scheduler
    │
    └── Triggers: daily_alert_task
                    │
                    ├── Loads all active registrations + their hearings
                    │
                    ├── For each upcoming hearing:
                    │       │
                    │       ├── days_until = hearing_date - today
                    │       │
                    │       ├── If days_until IN [7, 3, 1]:
                    │       │       │
                    │       │       ├── Already sent? → SKIP (unique constraint)
                    │       │       │
                    │       │       ├── Generate message
                    │       │       │       │
                    │       │       │       ├── Featherless.ai (DeepSeek-V3.2)
                    │       │       │       │   → Natural language in litigant's language
                    │       │       │       └── Fallback: hardcoded template
                    │       │       │
                    │       │       ├── Send alert
                    │       │       │       ├── Twilio SMS (if configured)
                    │       │       │       └── Telegram Bot (demo fallback)
                    │       │       │
                    │       │       └── Log to notifications table
                    │       │               status: sent / delivered / failed
                    │       │
                    │       └── days_until NOT in [7, 3, 1] → SKIP
                    │
                    └── Done: { sent, skipped, failed }
```

---

### Phase 6 — Delivery Confirmation

```
Twilio
    │
    └── POST /api/v1/webhook/twilio/status
            { MessageSid, MessageStatus }
                    │
                    └── Updates notifications.status
                            → "delivered" + sets delivered_at timestamp
                            → "failed"    + sets error_message
```

---

### Phase 7 — NGO Dashboard

```
NGO Worker (authenticated)
    │
    ├── GET  /api/v1/cases                    List all cases (paginated, searchable)
    ├── GET  /api/v1/cases/:id                Case detail + hearing history
    ├── POST /api/v1/cases/:id/sync           Manually re-sync from eCourts
    ├── DELETE /api/v1/cases/:id              Soft-delete (stop alerts)
    │
    ├── GET  /api/v1/notifications            Delivery log (filter by status/date)
    ├── POST /api/v1/notifications/test       Send test message via Telegram
    ├── POST /api/v1/notifications/run-alerts Manually trigger alert job (admin)
    │
    └── GET  /api/v1/stats/overview           Total cases, delivery rate, upcoming hearings
        GET  /api/v1/stats/upcoming-hearings  Hearings in next 7 days
        GET  /api/v1/stats/delivery-rate      WhatsApp vs SMS breakdown
```

---

## Database Schema

```
users
  id · email · hashed_password · full_name · org_name · role · is_active

registrations
  id · cnr_number · phone_number · language · case_title · court_name
  state_code · district_code · is_active · last_synced_at · registered_by → users

hearings
  id · registration_id → registrations · hearing_date · hearing_type
  court_room · judge_name · purpose · is_completed

notifications
  id · registration_id → registrations · hearing_id → hearings
  channel · status · message_text · message_language · days_before
  twilio_sid · error_message · sent_at · delivered_at
  UNIQUE(registration_id, hearing_id, days_before)   ← prevents duplicate alerts

whatsapp_commands
  id · from_number · body · command_type · cnr_extracted
  language_extracted · registration_id · response_sent · received_at

courts
  id · state_code · district_code · court_name · address · latitude · longitude
```

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend API | FastAPI (Python 3.12) + Uvicorn |
| Database | PostgreSQL 15 on NeonDB (serverless) |
| ORM | SQLAlchemy 2.0 async + asyncpg |
| Auth | JWT (python-jose) + bcrypt (passlib) |
| Task Queue | Celery 5.4 + Redis |
| Messaging (prod) | Twilio SMS/WhatsApp |
| Messaging (demo) | Telegram Bot API |
| AI Message Gen | Featherless.ai → DeepSeek-V3.2 |
| eCourts API | Mocked (real API requires govt approval) |
| Frontend | React 19 + TypeScript + Tailwind CSS |

---

## Alert Message Flow (AI-Powered)

```
Input:
  case_title  = "Sharma vs State of Maharashtra"
  hearing_date = 2026-04-12
  court_name  = "Bombay High Court"
  language    = "hi"
  days_before = 7

          │
          ▼
  Featherless.ai API
  Model: deepseek-ai/DeepSeek-V3.2
  Prompt: "Write a WhatsApp reminder in Hindi..."
          │
          ▼
Output (Hindi):
  ⚖️ CourtAlert रिमाइंडर

  आपके केस Sharma vs State of Maharashtra की
  सुनवाई 7 दिन बाद है।
  📅 तारीख: 12 April 2026
  🏛️ Bombay High Court, Court Room 3

  कृपया समय पर उपस्थित हों।
```

---

## API Summary (21 Endpoints)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/register` | Create NGO account |
| POST | `/auth/login` | Login, get JWT |
| GET | `/auth/me` | Current user profile |
| POST | `/cases/register` | Register a court case |
| GET | `/cases` | List cases (paginated) |
| GET | `/cases/:id` | Case detail |
| DELETE | `/cases/:id` | Deactivate case |
| POST | `/cases/:id/sync` | Re-sync from eCourts |
| POST | `/cases/bulk-upload` | CSV upload (500 rows) |
| GET | `/cases/:id/hearings` | Hearing list for case |
| GET | `/notifications` | Notification log |
| GET | `/notifications/:case_id` | Notifications for case |
| POST | `/notifications/test` | Send test via Telegram |
| POST | `/notifications/generate-message` | Preview AI message |
| POST | `/notifications/run-alerts` | Trigger CRON manually |
| POST | `/webhook/twilio` | Inbound WhatsApp/SMS |
| POST | `/webhook/twilio/status` | Delivery status callback |
| GET | `/stats/overview` | Dashboard stats |
| GET | `/stats/upcoming-hearings` | Hearings in next 7 days |
| GET | `/stats/delivery-rate` | Per-channel delivery rate |

---

*Built for ImpactHacks 2026 — making the Indian justice system accessible to those who need it most.*
