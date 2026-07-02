# Implementation Plan

## Job Portal with AI-Based Resume Screening System

---

## 1. Development Approach

**Methodology**: Agile (iterative sprints)
**Total Duration**: 6 weeks (estimated)
**Team Size**: 1 developer

---

## 2. Sprint Breakdown

### Sprint 1: Project Setup + Authentication (Week 1)

**Goal**: Working auth system with register/login and role-based access.

| Task | Details | Deliverable |
|---|---|---|
| Initialize Django project + DRF | `django-admin startproject`, configure settings, database | Working Django app |
| Set up PostgreSQL database | Create database, configure connection | Database ready |
| Implement User model | Custom User model with roles (admin/employer/candidate) | Migration applied |
| Build Register API | Endpoint with role selection, validation | POST /api/auth/register/ |
| Build Login API | JWT generation with simplejwt | POST /api/auth/login/ |
| Build Profile API | GET/PUT /api/auth/me/ | Profile endpoints |
| Initialize React project | Vite + React + Tailwind + React Router | Scaffolded frontend |
| Build Auth pages | Login + Register screens | Functional UI |
| Implement AuthContext | JWT storage, auto-refresh, protected routes | Auth state management |

**Verification**: Register as candidate → login → see candidate home. Register as employer → login → see employer home.

---

### Sprint 2: Job Management + Profiles (Week 2)

**Goal**: Employers can post/manage jobs. Candidates can create profiles + upload resumes.

| Task | Details | Deliverable |
|---|---|---|
| Employer model + API | Company profile, linked to User | Employer CRUD |
| Candidate model + API | Skills, experience, education, resume file | Candidate CRUD |
| Job model + API | Title, description, skills, salary, location | Job CRUD |
| Resume upload endpoint | PDF validation, file storage | POST /api/candidates/me/resume/ |
| Job Listings page | Browse all open jobs, search/filter | Frontend job list |
| Job Detail page | Full description, skills tags, apply CTA | Frontend job detail |
| Post Job form | Form validation, submit to API | Employer post job |
| Manage Jobs page | Employer sees own jobs, edit/close | Employer job management |
| Candidate Profile page | Edit profile, upload resume | Candidate profile UI |

**Verification**: Employer posts a job → appears in public listings. Candidate uploads resume → file stored.

---

### Sprint 3: AI/NLP Microservice (Week 3)

**Goal**: Standalone FastAPI microservice that parses resumes and computes match scores.

| Task | Details | Deliverable |
|---|---|---|
| Initialize FastAPI project | FastAPI app with health check | Working service |
| PDF extraction module | pdfplumber integration | Text extracted from PDF |
| Text preprocessing | Lowercase, stopwords, cleaning | Clean text pipeline |
| TF-IDF + cosine similarity | scikit-learn TfidfVectorizer | Match score computation |
| POST /api/score/ endpoint | Accept resume_text + job_description | Scoring API |
| Unit tests | Sample resumes + JDs to verify score ranges | Test suite |
| Dockerfile | Containerize the microservice | Docker image |
| Integration test | Call from Django backend | Full pipeline tested |

**Verification**: Upload resume PDF → extract text → score against JD → get 0-100% score.

---

### Sprint 4: Application Flow + Dashboard (Week 4)

**Goal**: Full apply → score → ranked dashboard flow.

| Task | Details | Deliverable |
|---|---|---|
| Application model + API | Apply, list applications, status update | Application CRUD |
| Trigger AI scoring on apply | Call NLP microservice after apply | Auto-scoring |
| Store match_score on application | Write score back to DB | Score persisted |
| Employer Applicants page | Ranked list sorted by match_score DESC | Frontend dashboard |
| Update application status | Shortlist/reject/hire actions | Status management |
| Candidate My Applications page | View applied jobs, statuses, scores | Candidate history |
| Candidate Job Detail — match score | Show match score before applying | Pre-apply insight |

**Verification**: Candidate applies → score computed → Employer sees ranked list → update status.

---

### Sprint 5: Frontend Completion + Notifications (Week 5)

**Goal**: All screens connected, notifications working, polished UI.

| Task | Details | Deliverable |
|---|---|---|
| Notification model + API | Create, list, mark-read endpoints | Notification system |
| In-app notification bell | Unread count badge, dropdown | Frontend notification UI |
| Admin Panel | User list, toggle active, platform stats | Admin dashboard |
| Loading states | Spinners, skeleton loaders everywhere | UX polish |
| Error handling | Toast messages, error boundaries | Robust error UI |
| Empty states | "No jobs found", "No applications yet" | Complete UX |
| Responsive design | Mobile <768px, tablet <1024px, desktop | Responsive all pages |
| Stitch design integration | Apply design tokens to all screens | Visual consistency |

**Verification**: All 12 screens functional, responsive, with proper loading/error/empty states.

---

### Sprint 6: Testing + Polish + Security (Week 6)

**Goal**: Comprehensive testing, security hardening, deployment readiness.

| Task | Details | Deliverable |
|---|---|---|
| Django unit tests | Models, views, serializers, auth | Test suite > 80% coverage |
| NLP microservice tests | Edge cases: empty PDF, non-PDF, large PDFs | Robust service |
| API integration tests | Full flow: register → apply → score → dashboard | E2E tested |
| Security audit | JWT, RBAC, file upload, CORS, rate limiting | Security checklist |
| Input validation | All forms, file types, sizes | Validated everywhere |
| Error logging | Structured logging for backend + frontend | Logs in place |
| README + setup docs | Installation, config, run instructions | Project documentation |
| Final demo prep | Seed data, sample resumes, test accounts | Demo ready |

**Verification**: All tests pass, security checklist complete, demo runs end-to-end.

---

## 3. Milestone Summary

| Milestone | Sprint | Criteria |
|---|---|---|
| Auth works | Sprint 1 | Register + Login + Role-based redirect |
| Jobs + Profiles | Sprint 2 | Employers post jobs, candidates have profiles |
| AI scoring works | Sprint 3 | NLP microservice returns 0-100 score |
| Apply → Score → Rank | Sprint 4 | Full application loop complete |
| All screens connected | Sprint 5 | Every page functional + responsive |
| Production ready | Sprint 6 | Tests pass, security reviewed, documented |

---

## 4. Dependencies

```
Sprint 1 ─────────────────────────────────────────────┐
                                                       │
Sprint 2 ──────────────┐                               │
                       │                               │
Sprint 3 ──────────────┼──────────────┐                │
                       │              │                │
Sprint 4 ◄─────────────┴──────────────┘────────────────┤
                                                       │
Sprint 5 ◄─────────────────────────────────────────────┘
                                                       │
Sprint 6 ◄─────────────────────────────────────────────┘
```

- Sprint 4 depends on Sprint 2 (jobs + profiles) + Sprint 3 (AI service)
- Sprint 5 depends on Sprint 4 (application flow working)
- Sprint 6 is the final hardening sprint

---

## 5. Testing Strategy

| Level | Tool | Focus |
|---|---|---|
| Unit (Backend) | Django TestCase | Models, serializers, view logic, auth |
| Unit (AI Service) | pytest | Text extraction, preprocessing, scoring |
| Integration | Django TestCase + requests | API endpoints, full application flow |
| Frontend | Manual + React Testing Library | Component rendering, user interactions |
| E2E | Manual walkthrough | Each user journey from start to end |
| Load | k6/locust (optional) | 100 concurrent users, scoring performance |

---

## 6. Deliverables Checklist

- [ ] Django REST Framework backend with 5 apps
- [ ] PostgreSQL database with 5 tables + indexes
- [ ] FastAPI NLP microservice with scoring pipeline
- [ ] React frontend with 12+ screens
- [ ] JWT authentication with role-based access control
- [ ] Resume upload (PDF) + text extraction
- [ ] TF-IDF + cosine similarity match scoring
- [ ] Employer dashboard with ranked applicants
- [ ] In-app notification system
- [ ] Admin panel for user management
- [ ] Responsive mobile-friendly UI
- [ ] Unit + integration tests
- [ ] Setup documentation
