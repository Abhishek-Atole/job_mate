# Product Requirements Document (PRD)

## Job Portal with AI-Based Resume Screening System

---

## 1. Product Vision

A web-based job portal that connects employers with candidates, where resume screening is automated via NLP-powered match scoring — reducing recruiter effort by 80% and giving candidates instant visibility into their job fit.

---

## 2. Target Audience

| Persona | Description | Goals | Pain Points |
|---|---|---|---|
| **Candidate** | Job seekers with varied experience levels | Find relevant jobs, apply quickly, know their match strength | No feedback on fit, manual applications, ghosting after applying |
| **Employer / Recruiter** | HR professionals and hiring managers | Post jobs, find best-fit candidates fast, track applications | Hundreds of manual resume reviews, inconsistent screening criteria |
| **Admin** | Platform owner/operator | Oversee platform health, manage users, view analytics | No centralized visibility into platform activity |

---

## 3. Functional Requirements

### Epic 1: Authentication & User Management

| ID | Requirement | Priority | Acceptance Criteria |
|---|---|---|---|
| FR-1 | User registration with role selection (Candidate / Employer) | P0 | User selects role at signup; role determines dashboard view |
| FR-2 | Login with JWT-based authentication | P0 | Valid credentials return JWT token; invalid returns 401 |
| FR-3 | Profile management (edit name, email, password) | P1 | User can update own profile fields |
| FR-4 | Admin user management (view, disable users) | P2 | Admin can list all users and toggle active status |

### Epic 2: Job Management (Employer)

| ID | Requirement | Priority | Acceptance Criteria |
|---|---|---|---|
| FR-5 | Create job posting (title, description, required skills, location, salary) | P0 | Form validates required fields; job appears in listings when open |
| FR-6 | Edit / Close job posting | P0 | Owner can update or close a job; closed jobs hidden from candidates |
| FR-7 | View all own job postings with status | P1 | Employer dashboard shows all jobs with open/closed status |

### Epic 3: Candidate Profile & Resume

| ID | Requirement | Priority | Acceptance Criteria |
|---|---|---|---|
| FR-8 | Create/edit candidate profile (skills, experience, education) | P0 | Profile saves and displays on applications |
| FR-9 | Upload resume (PDF only, max 5MB) | P0 | Validates file type and size; stores file; extracts text for AI scoring |
| FR-10 | View applied jobs history with statuses | P1 | Candidate can see all applications with match scores and status |

### Epic 4: Job Listings & Search (Candidate)

| ID | Requirement | Priority | Acceptance Criteria |
|---|---|---|---|
| FR-11 | Browse all open job postings | P0 | Paginated list of open jobs with key details |
| FR-12 | Search/filter by title, skills, location | P1 | Filters reduce results in real-time; search matches title/description |

### Epic 5: Application & AI Scoring

| ID | Requirement | Priority | Acceptance Criteria |
|---|---|---|---|
| FR-13 | Apply to a job (triggers resume parsing + scoring) | P0 | Application records created; NLP microservice called async |
| FR-14 | AI module extracts PDF text, computes TF-IDF + cosine similarity | P0 | Score computed within 5 seconds; stored on application record |
| FR-15 | Match score stored and displayed (0-100%) | P0 | Score visible to candidate and employer on relevant views |

### Epic 6: Employer Dashboard & Ranking

| ID | Requirement | Priority | Acceptance Criteria |
|---|---|---|---|
| FR-16 | View all applicants for a job, sorted by match_score DESC | P0 | Ranked list with scores, candidate details, resume download |
| FR-17 | Update application status (shortlisted / rejected / hired) | P0 | Status changes reflected immediately; notification triggered |
| FR-18 | View candidate profile details + download resume | P1 | Employer can inspect full candidate profile |

### Epic 7: Notifications

| ID | Requirement | Priority | Acceptance Criteria |
|---|---|---|---|
| FR-19 | In-app notification on application status change | P1 | Notification created when employer updates status |
| FR-20 | Email notification on status change | P2 | (Stretch) Email sent via SMTP |

---

## 4. User Stories

```
As a Candidate, I want to register with my role so that I can access candidate features.
As a Candidate, I want to upload my resume so that the AI can match me to jobs.
As a Candidate, I want to browse jobs with match scores so that I know which jobs fit me best.
As a Candidate, I want to apply to jobs so that employers can see my profile.
As a Candidate, I want to see my application status so that I know where I stand.

As an Employer, I want to post jobs so that candidates can find them.
As an Employer, I want to see ranked applicants so that I focus on top matches first.
As an Employer, I want to shortlist/reject candidates so that I manage my pipeline.
As an Employer, I want to download candidate resumes so that I can review them offline.

As an Admin, I want to manage users so that I can keep the platform healthy.
As an Admin, I want to view platform stats so that I understand usage patterns.
```

---

## 5. Non-Functional Requirements

| Category | Requirement | Acceptance Criteria |
|---|---|---|
| Performance | Page load time < 3 seconds | Lighthouse score > 80 |
| Performance | AI scoring completes < 5 seconds per resume | Timer test with 10-page PDF |
| Scalability | Support 100+ concurrent users | Load test passes without degradation |
| Availability | 99% uptime target | Graceful error handling on all pages |
| Security | OWASP Top 10 mitigated | Auth, upload, and API security review passed |
| Usability | Mobile-responsive design | All screens functional at 375px width |
| Maintainability | Modular architecture | Each service independently deployable |
| Accessibility | Basic web accessibility | Semantic HTML, alt tags, keyboard navigation |
