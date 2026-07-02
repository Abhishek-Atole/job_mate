# UI/UX Design Flow

## Job Portal with AI-Based Resume Screening System

---

## 1. Design System (Stitch-Generated)

The visual design is generated using **Stitch** and follows a consistent design system:

| Token | Value |
|---|---|
| **Primary Color** | `#2563EB` (Blue 600) |
| **Headline Font** | Inter |
| **Body Font** | Inter |
| **Roundness** | 8px (ROUND_EIGHT) |
| **Color Variant** | Tonal Spot |
| **Mode** | Light |

### Design Principles
- **Professional**: Clean layouts, readable typography, corporate feel
- **Approachable**: Warm blue tones, friendly but formal
- **Data-forward**: Match scores and rankings as prominent visual elements
- **Role-aware**: Clear visual distinction between Candidate and Employer views

---

## 2. User Journey Maps

### Candidate Journey

```
Landing Page
    │
    ▼
Register (select "Candidate" role)
    │
    ▼
Complete Profile (skills, experience, education)
    │
    ▼
Upload Resume (PDF)
    │
    ▼
Browse Jobs → Search/Filter
    │
    ▼
View Job Detail → See suggested match score
    │
    ▼
Apply → Application submitted
    │
    ▼
My Applications → Track status
    │
    ▼
Receive Notification → Status updated by employer
```

### Employer Journey

```
Landing Page
    │
    ▼
Register (select "Employer" role)
    │
    ▼
Create Company Profile
    │
    ▼
Post Job → Fill form → Publish
    │
    ▼
Manage Jobs → View all postings
    │
    ▼
View Applicants → See ranked list by match score
    │
    ▼
Inspect Candidate Profile + Download Resume
    │
    ▼
Shortlist / Reject / Hire
    │
    ▼
Notification sent to candidate automatically
```

---

## 3. Screen List & Route Map

| # | Route | Screen | Role | Description |
|---|---|---|---|---|
| 1 | `/` | Landing Page | All | Hero, stats, featured jobs, how it works |
| 2 | `/register` | Register | Public | Role selection + registration form |
| 3 | `/login` | Login | Public | Email + password login |
| 4 | `/jobs` | Job Listings | All | Searchable, filterable job cards |
| 5 | `/jobs/:id` | Job Detail | All | Full description + Apply button |
| 6 | `/employer/post-job` | Post Job | Employer | Job creation form |
| 7 | `/employer/jobs` | Manage Jobs | Employer | List own jobs with status toggle |
| 8 | `/employer/jobs/:id/applicants` | Applicants | Employer | Ranked list with actions |
| 9 | `/candidate/profile` | Profile | Candidate | Edit profile + resume upload |
| 10 | `/candidate/applications` | My Applications | Candidate | Applied jobs with statuses |
| 11 | `/admin` | Admin Panel | Admin | User management + stats |
| 12 | `/notifications` | Notifications | All | In-app notification list |

---

## 4. Navigation Flow

```
                         ┌─────────────┐
                         │   Landing   │
                         │    Page     │
                         └──────┬──────┘
                                │
                    ┌───────────┴───────────┐
                    │                       │
                    ▼                       ▼
             ┌───────────┐           ┌───────────┐
             │  Login    │◄─────────►│ Register  │
             └─────┬─────┘           └───────────┘
                   │
          ┌────────┴────────────────────┐
          │                             │
          ▼                             ▼
   ┌──────────────┐            ┌──────────────────┐
   │  Candidate   │            │    Employer      │
   │  Dashboard   │            │    Dashboard     │
   └──────┬───────┘            └────────┬─────────┘
          │                             │
          ├── Browse Jobs               ├── Post Job
          ├── Job Detail                ├── Manage Jobs
          ├── Apply                     ├── View Applicants
          ├── My Applications           ├── Shortlist/Reject
          ├── Profile                   └── Company Profile
          └── Notifications
```

---

## 5. Wireframe Outlines

### 5.1 Landing Page
```
┌──────────────────────────────────────────────────┐
│ [Logo]  Find Jobs  For Employers  About  [Login] │
│                                        [GetStart]│
├──────────────────────────────────────────────────┤
│                                                    │
│   ┌──────────────────────────────────────┐        │
│   │  Find Your Perfect Match             │        │
│   │  AI-powered job matching that...     │        │
│   │                                      │        │
│   │  [Browse Jobs]    [Post a Job]       │        │
│   └──────────────────────────────────────┘        │
│                                                    │
│   ┌──────┐  ┌──────┐  ┌──────┐                   │
│   │10K+  │  │5K+   │  │95%   │                   │
│   │ Jobs  │  │Employ│  │Match │                   │
│   └──────┘  └──────┘  └──────┘                   │
│                                                    │
│   ┌──────────────┐ ┌──────────────┐ ┌──────────┐ │
│   │ Python Dev   │ │ UX Designer  │ │ Data Ana │ │
│   │ Company XYZ  │ │ Company ABC  │ │ Company..│ │
│   │ Location     │ │ Location     │ │ Location │ │
│   │ Skills: ...  │ │ Skills: ...  │ │ Skills:  │ │
│   │ [Score: 82%] │ │ [Score: 74%]│ │ [91%]    │ │
│   └──────────────┘ └──────────────┘ └──────────┘ │
│                                                    │
│   ┌──────┐  ┌──────┐  ┌──────┐                   │
│   │Step1 │  │Step2 │  │Step3 │                   │
│   │Upload│  │AI    │  │Apply │                   │
│   │Resume│  │Match │  │&Hire │                   │
│   └──────┘  └──────┘  └──────┘                   │
└──────────────────────────────────────────────────┘
```

### 5.2 Employer Dashboard (Ranked Applicants)
```
┌──────────────────────────────────────────────────┐
│ [Logo]  Dashboard  My Jobs  Post Job  [Profile]  │
├──────────────────────────────────────────────────┤
│                                                    │
│   Python Backend Developer                      │
│   12 Applicants · Ranked by Match Score          │
│                                                    │
│   ┌──────────────────────────────────────────┐   │
│   │ Rank │ Name    │ Score │ Status  │ Action │   │
│   ├──────┼─────────┼───────┼─────────┼───────┤   │
│   │ #1   │ Alice M │ 92%  │ Applied │ [View] │   │
│   │      │         │ ████████████     │[Short] │   │
│   ├──────┼─────────┼───────┼─────────┼───────┤   │
│   │ #2   │ Bob K   │ 71%  │ Applied │ [View] │   │
│   │      │         │ ████████        │[Short] │   │
│   ├──────┼─────────┼───────┼─────────┼───────┤   │
│   │ #3   │ Carol S │ 45%  │ Applied │ [View] │   │
│   │      │         │ █████           │[Short] │   │
│   └──────────────────────────────────────────┘   │
│                                                    │
│   [Shortlist Selected]  [Reject Selected]         │
└──────────────────────────────────────────────────┘
```

### 5.3 Job Detail + Apply
```
┌──────────────────────────────────────────────────┐
│ [Logo]  Find Jobs  [Login]                        │
├──────────────────────────────────────────────────┤
│                                                    │
│   Python Backend Developer                       │
│   Company XYZ · San Francisco, CA                │
│                                                    │
│   Salary: $80K - $120K                           │
│   Type: Full-time                                │
│                                                    │
│   ┌──────────────────────────────────────┐       │
│   │  Your Match Score: 82%              │       │
│   │  ████████████░░░░░░░░               │       │
│   │  [Apply Now]                        │       │
│   └──────────────────────────────────────┘       │
│                                                    │
│   Job Description                                 │
│   We are looking for a skilled Python developer... │
│                                                    │
│   Required Skills                                 │
│   [Python] [Django] [PostgreSQL] [REST API]      │
│                                                    │
│   About Company                                    │
│   Company XYZ is a leading tech company...        │
└──────────────────────────────────────────────────┘
```

---

## 6. Responsive Behavior

| Breakpoint | Layout | Columns |
|---|---|---|
| >1024px (Desktop) | Full layout | 3-column job cards, full sidebar |
| 768-1024px (Tablet) | Collapsed sidebar | 2-column job cards |
| <768px (Mobile) | Hamburger menu | Single column, stacked |

---

## 7. Stitch Screen Generation Plan

The following screens will be generated using Stitch:

1. **Landing Page** — Hero, stats, featured jobs, how-it-works
2. **Register Screen** — Role toggle, form fields
3. **Login Screen** — Email/password, forgot password link
4. **Job Listings** — Search bar, filters, job cards with score badges
5. **Job Detail** — Full description, match score, apply button
6. **Post Job** — Employer job creation form
7. **Manage Jobs** — Employer's job list table
8. **Applicants Dashboard** — Ranked list with action buttons
9. **Candidate Profile** — Skills, experience, resume upload
10. **My Applications** — Application history with status badges
11. **Notifications** — Notification list with read/unread state
12. **Admin Panel** — User management table + stats

All screens use the shared Stitch design system (`assets/11513412178603584541`) to ensure visual consistency.
