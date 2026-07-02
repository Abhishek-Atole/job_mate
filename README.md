# Job Mate

AI-powered job portal with intelligent resume screening, skill-based job matching, and automated job scraping.

## Features

- **Smart Resume Screening** — NVIDIA NIM LLM scores resumes against job descriptions with detailed reasoning; falls back to TF-IDF
- **Job Recommendations** — Skill-based matching (Jaccard + coverage scoring) ranks open jobs for each candidate
- **Auto-Apply** — One-click batch apply to top matching jobs
- **Job Scraping** — Scrapes jobs from LinkedIn and company career pages (Indeed blocked)
- **Resume Skill Extraction** — Upload a PDF; system extracts skills from text and suggests them
- **Candidate Dashboard** — Ranked job recommendations with match score badges
- **Employer Dashboard** — Manage jobs, view applicants ranked by score, shortlist/reject/hire
- **Notifications** — Real-time status updates when applications are reviewed
- **Role-based Access** — Separate employer and candidate portals with secure JWT auth
- **Admin Panel** — User management, stats dashboard

## Architecture

```
┌─────────────┐     ┌──────────────────┐     ┌──────────────┐
│  React+Vite  │────▶│  Django REST API  │────▶│   SQLite     │
│  (Frontend)  │     │  (Port 8000)      │     │  (Database)  │
└─────────────┘     └───────┬──────────┘     └──────────────┘
                            │
                            ▼
                   ┌──────────────────┐
                   │  FastAPI (NLP)    │
                   │  (Port 8001)      │
                   │  NIM + TF-IDF     │
                   └──────────────────┘
```

## Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+

### Backend (Django)

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 manage.py migrate
python3 manage.py runserver 0.0.0.0:8000
```

### NLP Service (FastAPI)

```bash
cd screening_service
pip install -r requirements.txt
# Optional: set NVIDIA NIM API key in .env for LLM scoring
python3 -m uvicorn main:app --host 0.0.0.0 --port 8001
```

### Frontend (React + Vite)

```bash
cd frontend
npm install
npm run dev
```

### Seed Data (optional)

```bash
python3 manage.py seed_data --jobs 1000 --candidates 100
```

## API Test Suite

```bash
bash test_all.sh
```

## Credentials (seed data)

| Role      | Email                              | Password      |
|-----------|------------------------------------|---------------|
| Employer  | hr@company.com                     | employer123   |
| Candidate | first.last@email.com               | candidate123  |

## Tech Stack

- **Backend**: Django REST Framework, Python
- **Frontend**: React, Vite, Tailwind CSS
- **NLP**: FastAPI, scikit-learn (TF-IDF), NVIDIA NIM API
- **Database**: SQLite (dev)
- **Auth**: JWT (SimpleJWT)
