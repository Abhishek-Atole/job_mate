from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from .preprocessor import preprocess


def compute_match_score(resume_text: str, job_description: str) -> float:
    resume_clean = preprocess(resume_text)
    job_clean = preprocess(job_description)

    documents = [resume_clean, job_clean]
    vectorizer = TfidfVectorizer(stop_words='english', max_features=5000)
    tfidf_matrix = vectorizer.fit_transform(documents)
    similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
    return round(float(similarity[0][0]) * 100, 2)
