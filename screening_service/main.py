from dotenv import load_dotenv
load_dotenv(override=True)

from fastapi import FastAPI
from pydantic import BaseModel
from screening.matcher import compute_match_score
from screening.nim_scorer import compute_nim_score

app = FastAPI(title="HireMatch AI Screening Service")


class ScoreRequest(BaseModel):
    resume_text: str
    job_description: str


class ScoreResponse(BaseModel):
    match_score: float
    reasoning: str = ""
    scorer: str = "tfidf"
    status: str = "success"


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.post("/api/score/", response_model=ScoreResponse)
def score(request: ScoreRequest):
    nim_score, reasoning = compute_nim_score(
        request.resume_text, request.job_description
    )
    if nim_score is not None:
        return ScoreResponse(
            match_score=nim_score, reasoning=reasoning, scorer="nim"
        )

    tfidf_score = compute_match_score(request.resume_text, request.job_description)
    return ScoreResponse(match_score=tfidf_score, scorer="tfidf")
