# HR Decision Lab | مختبر قرار الموارد البشرية

A full-stack web application that assesses HR decision-making patterns through realistic, AI-generated workplace scenarios — built for an internal client to evaluate HR professionals and job candidates.

**Live demo:** [app.theagilehr.com](https://app.theagilehr.com)

## Overview

Users (team members or job candidates) are invited by email to complete a series of realistic HR scenarios tailored to their seniority level. Each decision is scored against a set of behavioral archetypes, producing a final report that identifies the user's dominant decision-making pattern versus the target pattern for their level — complete with an AI-generated narrative summary and a shareable result card.

Admins manage the whole flow from a dashboard: sending invite batches (separated by team members vs. candidates), tracking completion status, and reviewing individual and aggregate reports.

## Features

- 🧠 **AI-generated scenarios** — dynamic, schema-validated scenarios generated per session via an LLM (OpenRouter), scoped by seniority level and category
- 📊 **Pattern analysis engine** — rule-based classification of decision archetypes with AI-polished narrative summaries
- ✉️ **Invite-based assessment flow** — admins send batched email invites with optional deadlines; recipients complete the assessment via a unique link, no account required
- 🔐 **Admin dashboard** — gated signup, session-based auth, batch invite creation, status tracking, and per-candidate report access
- 📤 **Result sharing** — users can email their own result to a peer, or download a shareable pattern card
- 🌐 **Fully Arabic (RTL) interface**

## Tech Stack

**Backend**
- FastAPI (Python) — REST API
- SQLAlchemy + PostgreSQL — persistence
- OpenRouter API — LLM scenario generation & report narrative polishing
- Resend — transactional email delivery

**Frontend**
- Next.js (App Router) + React
- Tailwind CSS

**Infrastructure**
- Railway — backend + PostgreSQL hosting
- Vercel — frontend hosting

## Project Structure

 ```app/
api/ FastAPI routers (main app, admin, invites)
services/ Business logic (scenario generation, evaluation, pattern
analysis, invites, email, admin auth)
schemas/ Pydantic models — the data contract for scenarios,
decisions, and reports
prompts/ LLM system prompts and few-shot examples
data/ Static archetype/behavior reference data
db.py / db_models.py SQLAlchemy engine and ORM models

hr_decision_lab_frontend/
app/ Next.js App Router pages (assessment flow, admin
dashboard, invite links, reports)
lib/ API clients and shared utilities

tests/ Offline and live integration tests
```

## Running Locally

### Backend

```bash
pip install -r requirements.txt
uvicorn app.api.main:app --reload
```

API docs available at `http://127.0.0.1:8000/docs` (Swagger UI).

**Required environment variables:**

| Variable | Description |
|---|---|
| `DATABASE_URL` | PostgreSQL connection string (falls back to local SQLite if unset) |
| `OPENROUTER_API_KEY` | For scenario generation and report narratives |
| `RESEND_API_KEY` | For sending invite and result-sharing emails |
| `RESEND_FROM_EMAIL` | Verified sender address |
| `ALLOWED_ORIGINS` | Comma-separated list of allowed frontend origins (CORS) |
| `FRONTEND_BASE_URL` | Used to build links in outgoing emails |
| `ALLOW_ADMIN_SIGNUP` | Set to `true` temporarily to enable `/admin/signup`; keep unset/`false` in production |

### Frontend

```bash
cd hr_decision_lab_frontend
npm install
npm run dev
```

Set `NEXT_PUBLIC_API_URL` in `.env.local` to point to the backend.

## Testing

```bash
pytest tests/
```

`tests/test_live_generation.py` requires a live `OPENROUTER_API_KEY` (or `GEMINI_API_KEY`, depending on configuration) and makes real API calls; the rest run fully offline.

---

Built by [Aya Mousa](https://github.com/Aya-mosa).
