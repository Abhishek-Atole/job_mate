# Technical Requirements Document (TRD)

## Job Portal with AI-Based Resume Screening System

---

## 1. System Architecture

```
┌─────────────────────────────────────────────────────┐
│                   Client Layer                       │
│  ┌──────────────────────────────────────────────┐   │
│  │         React SPA (Vite + Tailwind)          │   │
│  │    Axios · React Router · Auth Context       │   │
│  └─────────────────────┬────────────────────────┘   │
│                        │                            │
│              REST API (JSON + JWT)                   │
└────────────────────────┬────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────┐
│                Backend Layer                         │
│  ┌──────────────────────────────────────────────┐   │
│  │        Django REST Framework (Python)        │   │
│  │   Apps: users, jobs, applications, notifs    │   │
│  │   Auth: djangorestframework-simplejwt        │   │
│  │   Storage: django-file-storage / S3          │   │
│  └──────┬──────────────────────────────┬────────┘   │
│         │                              │             │
│         ▼                              ▼             │
│  ┌────────────┐              ┌──────────────────┐   │
│  │ PostgreSQL │              │  NLP Microservice │   │
│  │ (Primary)  │              │  FastAPI (Python) │   │
│  │            │              │  scikit-learn     │   │
│  │            │              │  pdfplumber       │   │
│  └────────────┘              └──────────────────┘   │
└─────────────────────────────────────────────────────┘
```

### Architecture Decisions

| Decision | Choice | Rationale |
|---|---|---|
| Frontend framework | React + Vite | Fast dev server, component-based, huge ecosystem |
| UI styling | Tailwind CSS | Utility-first, matches Stitch design tokens easily |
| Backend framework | Django REST Framework | Python-based, built-in ORM, admin panel, mature ecosystem |
| Database | PostgreSQL | Robust, supports JSON, great with Django ORM |
| AI service | FastAPI (standalone) | Async, auto-docs, decoupled from main backend |
| Auth | JWT (simplejwt) | Stateless, works with SPA architecture |
| File storage | Local media/ → S3 | Dev simplicity → production scalability |

---

## 2. Database Schema

### Entity Relationship

```
User (1) ──── (1) Employer
User (1) ──── (1) Candidate
Employer (1) ──── (M) Job
Job (1) ──── (M) Application
Candidate (1) ──── (M) Application
User (1) ──── (M) Notification
```

### Full DDL

```sql
-- ============================================
-- TABLE: users
-- ============================================
CREATE TABLE users (
    id BIGSERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    full_name VARCHAR(150) NOT NULL,
    role VARCHAR(20) NOT NULL CHECK (role IN ('admin', 'employer', 'candidate')),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_users_email ON users(email);

-- ============================================
-- TABLE: employers
-- ============================================
CREATE TABLE employers (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    company_name VARCHAR(200) NOT NULL,
    company_description TEXT,
    website VARCHAR(255),
    location VARCHAR(150),
    logo VARCHAR(255)
);

-- ============================================
-- TABLE: candidates
-- ============================================
CREATE TABLE candidates (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    resume_file VARCHAR(255),
    skills TEXT,
    experience_years INT DEFAULT 0,
    education TEXT,
    phone VARCHAR(20)
);

-- ============================================
-- TABLE: jobs
-- ============================================
CREATE TABLE jobs (
    id BIGSERIAL PRIMARY KEY,
    employer_id BIGINT NOT NULL REFERENCES employers(id) ON DELETE CASCADE,
    title VARCHAR(200) NOT NULL,
    description TEXT NOT NULL,
    required_skills TEXT,
    location VARCHAR(150),
    salary_min DECIMAL(12,2),
    salary_max DECIMAL(12,2),
    status VARCHAR(10) DEFAULT 'open' CHECK (status IN ('open', 'closed')),
    posted_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ
);

CREATE INDEX idx_jobs_employer ON jobs(employer_id);
CREATE INDEX idx_jobs_status ON jobs(status);
CREATE INDEX idx_jobs_posted ON jobs(posted_at DESC);

-- ============================================
-- TABLE: applications
-- ============================================
CREATE TABLE applications (
    id BIGSERIAL PRIMARY KEY,
    job_id BIGINT NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
    candidate_id BIGINT NOT NULL REFERENCES candidates(id) ON DELETE CASCADE,
    match_score DECIMAL(5,2),
    status VARCHAR(20) DEFAULT 'applied' CHECK (status IN ('applied', 'shortlisted', 'rejected', 'hired')),
    applied_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(job_id, candidate_id)
);

CREATE INDEX idx_applications_job ON applications(job_id);
CREATE INDEX idx_applications_candidate ON applications(candidate_id);
CREATE INDEX idx_applications_score ON applications(match_score DESC);

-- ============================================
-- TABLE: notifications
-- ============================================
CREATE TABLE notifications (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    message TEXT NOT NULL,
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_notifications_user ON notifications(user_id);
CREATE INDEX idx_notifications_read ON notifications(user_id, is_read);
```

---

## 3. API Endpoints

### Authentication

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| POST | `/api/auth/register/` | No | Register user (candidate/employer) |
| POST | `/api/auth/login/` | No | Login, returns access + refresh JWT |
| POST | `/api/auth/token/refresh/` | No | Refresh access token |
| GET | `/api/auth/me/` | Yes | Get current user profile |
| PUT | `/api/auth/me/` | Yes | Update profile |

### Jobs

| Method | Endpoint | Auth | Role | Description |
|---|---|---|---|---|
| GET | `/api/jobs/` | No | — | List open jobs (filterable) |
| POST | `/api/jobs/` | Yes | Employer | Create job posting |
| GET | `/api/jobs/{id}/` | No | — | Job detail |
| PUT | `/api/jobs/{id}/` | Yes | Employer | Update job (owner only) |
| DELETE | `/api/jobs/{id}/` | Yes | Employer | Close job (owner only) |

### Candidates

| Method | Endpoint | Auth | Role | Description |
|---|---|---|---|---|
| GET | `/api/candidates/me/` | Yes | Candidate | Get own profile |
| PUT | `/api/candidates/me/` | Yes | Candidate | Update profile |
| POST | `/api/candidates/me/resume/` | Yes | Candidate | Upload resume (PDF) |

### Applications

| Method | Endpoint | Auth | Role | Description |
|---|---|---|---|---|
| POST | `/api/jobs/{id}/apply/` | Yes | Candidate | Apply to job |
| GET | `/api/jobs/{id}/applications/` | Yes | Employer | List ranked applicants |
| PUT | `/api/applications/{id}/status/` | Yes | Employer | Update status |
| GET | `/api/applications/me/` | Yes | Candidate | My applications |

### Admin

| Method | Endpoint | Auth | Role | Description |
|---|---|---|---|---|
| GET | `/api/admin/users/` | Yes | Admin | List all users |
| PUT | `/api/admin/users/{id}/toggle/` | Yes | Admin | Enable/disable user |
| GET | `/api/admin/stats/` | Yes | Admin | Platform statistics |

### Notifications

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| GET | `/api/notifications/` | Yes | List notifications |
| PUT | `/api/notifications/{id}/read/` | Yes | Mark as read |
| PUT | `/api/notifications/read-all/` | Yes | Mark all as read |

---

## 4. NLP Microservice Specification

### Service: FastAPI (standalone)

**Endpoint**: `POST /api/score/`

**Request**:
```json
{
  "resume_text": "Experienced Python developer with Django, REST APIs...",
  "job_description": "Looking for a Python backend developer with Django experience..."
}
```

**Response**:
```json
{
  "match_score": 78.45,
  "status": "success"
}
```

**Endpoint**: `GET /health`

**Response**: `{ "status": "healthy" }`

### Processing Pipeline

```
Raw PDF Text
    │
    ▼
Preprocessing:
  - Lowercase conversion
  - Remove special characters
  - Strip whitespace
  - Remove stopwords (English)
    │
    ▼
TF-IDF Vectorization:
  - TfidfVectorizer(stop_words='english', max_features=5000)
  - Fit and transform both documents together
    │
    ▼
Cosine Similarity:
  - cosine_similarity(resume_vector, job_vector)
  - Result: float between 0 and 1
    │
    ▼
Score Conversion:
  - Round to 2 decimal places
  - Multiply by 100 for percentage
  - Return match_score
```

### Code Structure (screening_service/)

```
screening_service/
├── main.py              # FastAPI app, routes
├── requirements.txt     # Dependencies
├── Dockerfile           # Container definition
├── screening/
│   ├── __init__.py
│   ├── extractor.py     # PDF text extraction
│   ├── preprocessor.py  # Text cleaning
│   ├── matcher.py       # TF-IDF + cosine similarity
│   └── models.py        # Pydantic models
└── tests/
    ├── test_extractor.py
    ├── test_matcher.py
    └── sample_resume.pdf
```

---

## 5. React Component Architecture

```
src/
├── App.jsx
├── main.jsx
├── index.css              # Tailwind imports
│
├── api/
│   ├── client.js          # Axios instance + interceptors
│   └── endpoints.js       # API call functions
│
├── context/
│   ├── AuthContext.jsx     # JWT state, login/logout, role
│   └── NotificationContext.jsx
│
├── hooks/
│   ├── useAuth.js
│   ├── useJobs.js
│   └── useApplications.js
│
├── layouts/
│   ├── MainLayout.jsx     # Navbar + Footer wrapper
│   ├── AuthLayout.jsx     # Login/Register layout
│   └── DashboardLayout.jsx # Sidebar + content
│
├── pages/
│   ├── Home.jsx           # Landing page (public)
│   ├── Register.jsx       # Role-based registration
│   ├── Login.jsx
│   ├── JobList.jsx        # Browse jobs (public)
│   ├── JobDetail.jsx      # Job detail + Apply
│   ├── PostJob.jsx        # Create job (employer)
│   ├── ManageJobs.jsx     # My jobs (employer)
│   ├── Applicants.jsx     # Ranked applicants (employer)
│   ├── CandidateProfile.jsx
│   ├── MyApplications.jsx
│   ├── AdminPanel.jsx
│   ├── Notifications.jsx
│   └── NotFound.jsx
│
├── components/
│   ├── Navbar.jsx         # Role-aware navigation
│   ├── JobCard.jsx        # Job listing card
│   ├── JobForm.jsx        # Create/edit job form
│   ├── JobFilters.jsx     # Search + filter bar
│   ├── ApplicationCard.jsx
│   ├── StatusBadge.jsx    # Status indicator
│   ├── MatchScoreBar.jsx  # Visual score bar
│   ├── ResumeUploader.jsx # Drag-and-drop upload
│   ├── NotificationBell.jsx
│   └── ProtectedRoute.jsx # Role-gated routes
│
├── utils/
│   ├── validators.js
│   └── formatters.js
│
└── assets/
    └── images/
```

---

## 6. Key Technical Decisions

| Decision | Choice | Why |
|---|---|---|
| PDF parsing | pdfplumber | Better text extraction than PyPDF2, handles tables |
| Vectorization | scikit-learn TfidfVectorizer | Lightweight, well-tested, sufficient for TF-IDF |
| Async scoring | Celery / Django-Q | (Optional) For non-blocking AI scoring on large PDFs |
| File storage dev | Local `media/` | Simple setup, no cloud dependency |
| File storage prod | AWS S3 / DigitalOcean Spaces | Scalable, durable |
| CORS | django-cors-headers | Restrict to frontend origin |
| API docs | drf-spectacular (Swagger) | Auto-generated OpenAPI docs |

---

## 7. Environment Configuration

### Backend (.env)
```
DJANGO_SECRET_KEY=<secret>
DEBUG=True
DATABASE_URL=postgres://user:pass@localhost:5432/jobportal
CORS_ALLOWED_ORIGINS=http://localhost:5173
NLP_SERVICE_URL=http://localhost:8001
JWT_ACCESS_TOKEN_LIFETIME=15
JWT_REFRESH_TOKEN_LIFETIME=7
```

### NLP Service (.env)
```
FASTAPI_HOST=0.0.0.0
FASTAPI_PORT=8001
LOG_LEVEL=INFO
```

### Frontend (.env)
```
VITE_API_URL=http://localhost:8000/api
VITE_NLP_URL=http://localhost:8001
```
