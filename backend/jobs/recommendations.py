from .models import Job


def skill_match_score(candidate_skills: str, job: Job) -> float:
    if not candidate_skills or not job.required_skills:
        return 0.0

    cand = set(s.strip().lower() for s in candidate_skills.split(',') if s.strip())
    req = set(s.strip().lower() for s in job.required_skills.split(',') if s.strip())

    if not req:
        return 0.0
    if not cand:
        return 0.0

    intersection = cand & req
    union = cand | req

    jaccard = len(intersection) / len(union) if union else 0.0

    coverage = len(intersection) / len(req) if req else 0.0

    score = (jaccard * 0.5 + coverage * 0.5) * 100
    return round(score, 2)


def get_recommendations(candidate_skills: str, candidate_text: str = "", limit: int = 20):
    jobs = Job.objects.filter(status='open').select_related('employer')
    scored = []
    for job in jobs:
        s = skill_match_score(candidate_skills, job)
        if s > 0:
            scored.append((s, job))
    scored.sort(key=lambda x: x[0], reverse=True)
    return scored[:limit]
