# Security Concerns & Non-Functional Requirements

## Job Portal with AI-Based Resume Screening System

---

## Part 1: Security Concerns

### 1.1 Authentication Security

| Concern | Risk | Mitigation |
|---|---|---|
| **JWT Token Theft** | High | Access tokens expire in 15 minutes; refresh tokens in 7 days; store in httpOnly cookies (not localStorage); use refresh token rotation |
| **Brute Force Login** | High | Rate limiting on `/api/auth/login/` — max 5 attempts per minute per IP; account lockout after 10 failed attempts |
| **Weak Passwords** | Medium | Enforce minimum 8 chars, mixed case, numbers; use Django's built-in password validators; hash with bcrypt/PBKDF2 |
| **Token Replay** | Medium | Include `jti` (JWT ID) claim; maintain a deny-list for logged-out tokens (optional for higher security) |

### 1.2 Authorization Security

| Concern | Risk | Mitigation |
|---|---|---|
| **Privilege Escalation** | High | Role-based access control (RBAC) on every protected view via decorators (`@permission_classes`); never trust client-side role alone |
| **IDOR (Insecure Direct Object Reference)** | High | Always verify object ownership: employer can only modify own jobs; candidate can only see own applications |
| **Admin Abuse** | Medium | Admin actions logged to audit table; admin cannot post jobs or apply (role separation) |

**RBAC Enforcement Matrix**:

| Endpoint | Admin | Employer | Candidate | Public |
|---|---|---|---|---|
| `/api/auth/register/` | — | — | — | ✓ |
| `/api/auth/login/` | — | — | — | ✓ |
| `/api/jobs/` (GET) | ✓ | ✓ | ✓ | ✓ |
| `/api/jobs/` (POST) | — | ✓ | — | — |
| `/api/jobs/{id}/` (PUT/DELETE) | — | Owner only | — | — |
| `/api/jobs/{id}/apply/` | — | — | ✓ | — |
| `/api/jobs/{id}/applications/` | — | Owner only | — | — |
| `/api/applications/{id}/status/` | — | Job owner | — | — |
| `/api/admin/users/` | ✓ | — | — | — |
| `/api/notifications/` | ✓ | Own only | Own only | — |

### 1.3 File Upload Security

| Concern | Risk | Mitigation |
|---|---|---|
| **Malicious File Upload** | Critical | Validate MIME type + file extension (`.pdf` only); scan with ClamAV (optional); max file size 5MB |
| **Path Traversal** | High | Randomize stored filename using UUID; never use original filename for storage path; store outside webroot (`/media/resumes/`) |
| **PDF Bombs / Compression** | Medium | Limit decompression ratio; set PDF page limit (max 50 pages); timeout extraction after 10 seconds |

**Upload Validation Logic**:
```
1. Check file extension === '.pdf'
2. Check MIME type === 'application/pdf'
3. Check file size <= 5MB (5,242,880 bytes)
4. Generate UUID filename: {uuid}.pdf
5. Store in /media/resumes/{uuid}.pdf
6. Extract text; if text length < 50 chars → reject (blank/binary PDF)
```

### 1.4 Data Protection

| Concern | Risk | Mitigation |
|---|---|---|
| **Password Exposure** | Critical | Hash with Django's `PBKDF2PasswordHasher`; never log or return passwords in API responses |
| **SQL Injection** | High | Django ORM throughout — no raw SQL queries |
| **XSS (Cross-Site Scripting)** | Medium | React auto-escapes JSX output; sanitize any `dangerouslySetInnerHTML` usage; validate job description input |
| **CSRF (Cross-Site Request Forgery)** | Medium | Django CSRF middleware for session auth; JWT API auth is inherently immune to CSRF |
| **Sensitive Data in Logs** | Medium | Never log passwords, tokens, or file contents; use structured logging with sensitive field filtering |

### 1.5 API Security

| Concern | Risk | Mitigation |
|---|---|---|
| **CORS Misconfiguration** | Medium | Restrict to frontend origin only (`CORS_ALLOWED_ORIGINS = ["http://localhost:5173"]`); no wildcard in production |
| **Rate Limiting** | Medium | Apply to all non-GET endpoints: 20 req/min for auth, 60 req/min for others using `django-ratelimit` |
| **Request Size Limit** | Low | Limit request body to 10MB; reject oversized payloads early via middleware |
| **Information Disclosure** | Medium | Return generic error messages ("Invalid credentials" not "User not found"); disable DEBUG in production |

### 1.6 Environment & Secrets

| Concern | Risk | Mitigation |
|---|---|---|
| **Secret Leakage** | Critical | Use `.env` file with `python-decouple` or `django-environ`; add `.env` to `.gitignore`; never commit secrets |
| **Hardcoded Credentials** | Critical | Zero hardcoded credentials in code; all config via environment variables |
| **Dependency Vulnerabilities** | Medium | Pin all dependency versions in `requirements.txt`; run `pip-audit` or `safety check` before release |

**Environment Variable Template**:
```bash
# Backend (.env) — NEVER commit this file
DJANGO_SECRET_KEY=<generate-with: python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())">
DEBUG=False
DATABASE_URL=postgres://user:password@localhost:5432/jobportal
CORS_ALLOWED_ORIGINS=https://your-frontend-domain.com
NLP_SERVICE_URL=http://nlp-service:8001
JWT_ACCESS_TOKEN_LIFETIME=15
JWT_REFRESH_TOKEN_LIFETIME=7
```

---

## Part 2: Non-Functional Requirements

### 2.1 Performance

| Requirement | Target | Measurement |
|---|---|---|
| Page load time | < 3 seconds (first paint) | Lighthouse performance score > 80 |
| API response time | < 500ms for 95th percentile | Django Debug Toolbar / drf-api-log |
| AI scoring time | < 5 seconds per resume (10-page PDF) | Timer in FastAPI middleware |
| Search query time | < 1 second for 10k jobs | DB query EXPLAIN ANALYZE |
| Static assets | < 100KB initial bundle | Vite bundle analysis |

**Optimization Strategies**:
- Frontend: Code splitting with React.lazy, image optimization, lazy loading
- Backend: Database indexing (all FK columns, status, match_score DESC), select_related/prefetch_related
- AI Service: Cache TF-IDF vectorizer after first fit; preload stopwords list

### 2.2 Scalability

| Requirement | Target | Strategy |
|---|---|---|
| Concurrent users | 100+ simultaneous | Stateless JWT auth → horizontal scaling of Django behind nginx |
| Applications per job | 500+ | Indexed match_score DESC query; pagination (20 per page) |
| Resume storage | 10,000+ files | Move from local storage to S3/DO Spaces in production |
| NLP service load | 50+ concurrent scoring requests | FastAPI async workers; queue with Celery if needed |

**Horizontal Scaling Architecture**:
```
[Load Balancer]
    │
    ├── [Django App Server 1]
    ├── [Django App Server 2]
    └── [Django App Server N]
    │
    ├── [PostgreSQL] ← Read replicas for heavy queries
    └── [FastAPI NLP Service] ← Multiple workers
```

### 2.3 Availability

| Requirement | Target | Strategy |
|---|---|---|
| Uptime | 99% (development) → 99.9% (production) | Graceful degradation, proper error handling |
| Error handling | 100% of API errors return structured JSON | Custom DRF exception handler |
| NLP service failure | Application still submits; score computed async | Fallback: queue scoring for retry; show "Scoring in progress" |

**Error Response Format**:
```json
{
  "error": true,
  "message": "Human-readable message",
  "code": "VALIDATION_ERROR",
  "details": {}
}
```

### 2.4 Maintainability

| Requirement | Strategy |
|---|---|
| Code modularity | Separate Django apps (users, jobs, applications, notifications); standalone NLP service |
| Code style | Black + isort for Python; ESLint + Prettier for JavaScript |
| Documentation | README with setup; docstrings on all views; DRF-spectacular for API docs |
| Logging | Structured logging (JSON format); separate log levels for dev/prod |
| CI/CD | GitHub Actions: lint → test → build (future scope) |

**Django App Structure**:
```
backend/
├── config/                 # Django project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── apps/
│   ├── users/              # User model, auth views
│   ├── jobs/               # Job model + CRUD
│   ├── applications/       # Application model + scoring trigger
│   └── notifications/      # Notification model + push
├── media/                  # Uploaded resumes (dev)
└── requirements.txt
```

### 2.5 Usability

| Requirement | Target |
|---|---|
| Browser support | Latest Chrome, Firefox, Safari, Edge |
| Mobile responsive | All pages functional at 375px width |
| Keyboard navigation | All interactive elements reachable via Tab |
| Screen reader | Semantic HTML, aria-labels on icons, alt text on images |
| Loading feedback | Skeleton loaders or spinners on all async operations |
| Error feedback | Toast notifications for API errors; inline validation for forms |
| Empty states | Meaningful message + CTA when no data ("No jobs yet — check back later") |

### 2.6 Accessibility Checklist

- [ ] All images have descriptive `alt` text
- [ ] Color contrast ratio ≥ 4.5:1 for normal text
- [ ] All form inputs have associated `<label>` elements
- [ ] Interactive elements are keyboard-focusable
- [ ] Error messages are associated with inputs via `aria-describedby`
- [ ] Status updates announced via `aria-live` regions
- [ ] Navigation landmark roles (`<nav>`, `<main>`, `<footer>`)

---

## 3. Security Checklist (Pre-Launch)

- [ ] DEBUG=False in production
- [ ] `SECRET_KEY` is a strong random value, stored in env
- [ ] CORS restricted to frontend domain
- [ ] All passwords hashed (bcrypt/PBKDF2)
- [ ] JWT tokens expire (15m access, 7d refresh)
- [ ] File upload validates MIME + extension + size
- [ ] No hardcoded secrets in codebase
- [ ] `.env` in `.gitignore`
- [ ] Rate limiting on auth endpoints
- [ ] ORM used everywhere (no raw SQL)
- [ ] CSRF middleware enabled (for session-based views)
- [ ] Input validation on all API endpoints
- [ ] Object ownership verified (IDOR prevention)
- [ ] Admin actions logged to audit trail
- [ ] Dependencies scanned for vulnerabilities
