# CourtAlert — Frontend Development Plan

## Tech Stack

| Layer | Library |
|-------|---------|
| Framework | React 19 + TypeScript + Vite |
| UI Components | shadcn/ui |
| Styling | Tailwind CSS |
| Routing | React Router v6 |
| Server State | TanStack Query (React Query) |
| Tables | TanStack Table |
| Forms | React Hook Form + Zod |
| HTTP Client | Axios |
| Icons | Lucide React |
| Date Formatting | date-fns |

> **Note:** The current project uses Create React App (CRA) which is deprecated. Migrate to Vite before starting — shadcn requires Vite.

---

## Pages Overview

| Route | Page | Auth Required |
|-------|------|---------------|
| `/login` | Login | No |
| `/register` | NGO Account Signup | No |
| `/dashboard` | Stats Overview | Yes |
| `/cases` | Cases List | Yes |
| `/cases/register` | Register New Case | Yes |
| `/cases/bulk-upload` | CSV Bulk Upload | Yes |
| `/cases/:id` | Case Detail | Yes |
| `/notifications` | Notification Log | Yes |

---

## Page Specifications

### Login — `/login`

**API:** `POST /api/v1/auth/login`

- Email + password form
- On success: store JWT in localStorage, redirect to `/dashboard`
- On failure: show inline error message
- Link to `/register`

---

### Register — `/register`

**API:** `POST /api/v1/auth/register`

Fields:
- Full Name
- Organisation Name (optional)
- Email
- Password

On success: redirect to `/login`

---

### Dashboard — `/dashboard`

**APIs:**
- `GET /api/v1/stats/overview`
- `GET /api/v1/stats/upcoming-hearings`

Layout:
```
┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│ Total Cases │ │Active Cases │ │ Alerts Sent │ │Delivery Rate│
│    110      │ │    100      │ │  (30 days)  │ │    94%      │
└─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘

Upcoming Hearings Table (next 7 days)
Columns: Case Title | CNR | Court | Hearing Date | Days Left
```

Table built with TanStack Table. Days Left column shows a badge:
- Red → 1 day
- Orange → 3 days
- Blue → 7 days

---

### Cases List — `/cases`

**API:** `GET /api/v1/cases?page=1&limit=20&search=&is_active=`

Features:
- Search bar (by CNR or case title)
- Filter by status (Active / Inactive / All)
- Pagination
- Action buttons: View, Deactivate

Table columns:
```
CNR Number | Case Title | Court | Language | Next Hearing | Status | Actions
```

Buttons in header:
- `+ Register Case` → `/cases/register`
- `Bulk Upload` → `/cases/bulk-upload`

---

### Register Case — `/cases/register`

**API:** `POST /api/v1/cases/register`

Form fields:
| Field | Type | Validation |
|-------|------|------------|
| CNR Number | Text input | Required, 16 chars (4 letters + 12 digits) |
| Phone Number | Text input | Required, with +91 prefix |
| Language | Select dropdown | Required |

Language options:
- Hindi (hi)
- Marathi (mr)
- Tamil (ta)
- Telugu (te)
- Kannada (kn)
- English (en)

On success: show success toast + redirect to `/cases`
On error (duplicate / invalid CNR): show inline error

---

### Bulk Upload — `/cases/bulk-upload`

**API:** `POST /api/v1/cases/bulk-upload`

- CSV template download button
- Drag and drop file zone (or click to browse)
- Max 500 rows
- Required CSV columns: `cnr_number`, `phone_number`, `language`

On success: show summary card
```
✅ 47 registered successfully
❌ 3 failed

Errors table:
Row | CNR | Reason
```

---

### Case Detail — `/cases/:id`

**APIs:**
- `GET /api/v1/cases/:id`
- `POST /api/v1/cases/:id/sync`
- `DELETE /api/v1/cases/:id`
- `GET /api/v1/notifications/:id`

Header section:
```
Case Title                          [Sync Now]  [Deactivate]
CNR: MHMUM010001232023
Court: Bombay High Court
Language: Hindi
Last Synced: 2 hours ago
```

Two tabs:

**Tab 1 — Hearings**
```
Date | Type | Court Room | Judge | Status
```
Status badge: Upcoming (green) / Completed (grey)

**Tab 2 — Alerts Sent**
```
Days Before | Channel | Language | Status | Sent At | Delivered At
```
Status badge: delivered (green) / sent (blue) / failed (red) / retrying (orange)

---

### Notifications Log — `/notifications`

**API:** `GET /api/v1/notifications?status=&from_date=&to_date=`

Filters:
- Status: All / Sent / Delivered / Failed / Retrying
- Date range picker

Table columns:
```
Case Title | CNR | Channel | Language | Days Before | Status | Sent At | Delivered At
```

---

## Project Structure

```
src/
├── main.tsx
├── App.tsx                         ← Router setup
│
├── api/
│   ├── client.ts                   ← Axios instance (base URL + JWT header injection)
│   ├── auth.ts                     ← login(), register(), getMe()
│   ├── cases.ts                    ← getCases(), registerCase(), getCase(), etc.
│   ├── notifications.ts            ← getNotifications(), getCaseNotifications()
│   └── stats.ts                    ← getOverview(), getUpcomingHearings()
│
├── hooks/
│   ├── useAuth.ts                  ← Auth context: user, login(), logout()
│   └── queries/
│       ├── useCases.ts             ← TanStack Query hooks for cases
│       ├── useStats.ts             ← TanStack Query hooks for stats
│       └── useNotifications.ts    ← TanStack Query hooks for notifications
│
├── components/
│   ├── layout/
│   │   ├── AppLayout.tsx           ← Sidebar + Header wrapper (all protected pages)
│   │   ├── Sidebar.tsx             ← Navigation links
│   │   └── Header.tsx              ← User info + logout button
│   ├── shared/
│   │   ├── StatCard.tsx            ← Reusable stat card (number + label + icon)
│   │   ├── DataTable.tsx           ← Reusable TanStack Table wrapper
│   │   ├── PageHeader.tsx          ← Page title + optional action button
│   │   ├── StatusBadge.tsx         ← Color-coded status badge
│   │   └── ProtectedRoute.tsx      ← Redirects to /login if no JWT
│   └── ui/                         ← shadcn components (auto-generated, do not edit)
│
└── pages/
    ├── Login.tsx
    ├── Register.tsx
    ├── Dashboard.tsx
    ├── Cases.tsx
    ├── CaseRegister.tsx
    ├── CaseDetail.tsx
    ├── BulkUpload.tsx
    └── Notifications.tsx
```

---

## API Client Setup

```ts
// src/api/client.ts
import axios from 'axios'

const client = axios.create({
  baseURL: 'http://localhost:8000/api/v1',
})

client.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

export default client
```

---

## Auth Flow

```
User visits any protected page
        │
        ▼
ProtectedRoute checks localStorage for JWT
        │
   No token → redirect to /login
   Token exists → render page
        │
        ▼
API call fails with 401
        │
        ▼
Axios interceptor catches it → clear token → redirect to /login
```

---

## shadcn Components to Install

```bash
npx shadcn@latest add button
npx shadcn@latest add input
npx shadcn@latest add label
npx shadcn@latest add card
npx shadcn@latest add table
npx shadcn@latest add badge
npx shadcn@latest add tabs
npx shadcn@latest add select
npx shadcn@latest add dialog
npx shadcn@latest add toast
npx shadcn@latest add dropdown-menu
npx shadcn@latest add separator
npx shadcn@latest add skeleton
npx shadcn@latest add avatar
```

---

## Build Order

| # | Task | Estimated Time |
|---|------|----------------|
| 1 | Delete CRA, setup Vite + Tailwind + shadcn + all packages | 30 min |
| 2 | API client + Auth context + Protected routes + Router | 30 min |
| 3 | Login + Register pages | 30 min |
| 4 | AppLayout — Sidebar + Header | 30 min |
| 5 | Dashboard page (stat cards + upcoming hearings table) | 45 min |
| 6 | Cases list page (TanStack Table + search + pagination) | 45 min |
| 7 | Register case form + Bulk upload page | 30 min |
| 8 | Case detail page (tabs + hearings + alerts) | 45 min |
| 9 | Notifications log page | 30 min |

**Total estimate: ~5 hours**

---

## Backend API Reference

Base URL: `http://localhost:8000/api/v1`

All endpoints except `/auth/login` and `/auth/register` require:
```
Authorization: Bearer <jwt_token>
```

| Method | Endpoint | Used By |
|--------|----------|---------|
| POST | `/auth/login` | Login page |
| POST | `/auth/register` | Register page |
| GET | `/auth/me` | Header (user info) |
| GET | `/cases` | Cases list |
| POST | `/cases/register` | Register case form |
| GET | `/cases/:id` | Case detail |
| DELETE | `/cases/:id` | Case detail (deactivate) |
| POST | `/cases/:id/sync` | Case detail (sync button) |
| POST | `/cases/bulk-upload` | Bulk upload page |
| GET | `/notifications` | Notifications log |
| GET | `/notifications/:case_id` | Case detail (alerts tab) |
| GET | `/stats/overview` | Dashboard |
| GET | `/stats/upcoming-hearings` | Dashboard |
| GET | `/stats/delivery-rate` | Dashboard (optional) |
