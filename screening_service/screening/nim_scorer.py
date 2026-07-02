import os
import json
import re
import logging

logger = logging.getLogger(__name__)

NIM_API_KEY = os.getenv('NVIDIA_NIM_API_KEY', '')
NIM_MODEL = os.getenv('NVIDIA_NIM_MODEL', 'meta/llama3-70b-instruct')
NIM_BASE_URL = os.getenv('NVIDIA_NIM_BASE_URL', 'https://integrate.api.nvidia.com/v1')
NIM_FUNCTION_ID = os.getenv('NVIDIA_NIM_FUNCTION_ID', '')
NIM_ALT_URLS = os.getenv('NVIDIA_NIM_ALT_URLS', '')


def compute_nim_score(resume_text: str, job_description: str) -> tuple:
    if not NIM_API_KEY:
        return None, "NVIDIA_NIM_API_KEY not set"

    try:
        import httpx
    except ImportError:
        return None, "httpx package not installed"

    try:
        prompt = f"""You are an expert HR AI evaluator. Analyze how well this candidate matches the job.

Return ONLY valid JSON with two keys:
- "match_score": integer 0-100
- "reasoning": brief 1 sentence explanation

Resume: {resume_text[:2000]}

Job Description: {job_description[:2000]}"""

        alt_urls = [u.strip() for u in NIM_ALT_URLS.split(',') if u.strip()]
        chat_urls = alt_urls if alt_urls else [f"{NIM_BASE_URL}/chat/completions"]

        payloads = []
        for url in chat_urls:
            payloads.append((url, {
                "model": NIM_MODEL,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.1,
                "max_tokens": 256,
            }))

        if NIM_FUNCTION_ID:
            url = f"https://api.nvcf.nvidia.com/v2/nvcf/pexec/functions/{NIM_FUNCTION_ID}"
            payloads.append((url, {"messages": [{"role": "user", "content": prompt}]}))

        content = ''
        last_error = ''
        with httpx.Client(timeout=30) as client:
            for url, body in payloads:
                try:
                    resp = client.post(
                        url,
                        headers={
                            "Authorization": f"Bearer {NIM_API_KEY}",
                            "Content-Type": "application/json",
                        },
                        json=body,
                    )
                    resp.raise_for_status()
                    data = resp.json()
                    content = data.get('choices', [{}])[0].get('message', {}).get('content', '')
                    if not content:
                        content = data.get('response', '')
                    if content:
                        break
                except Exception as e:
                    last_error = str(e)
                    continue

        if not content:
            return None, f"No endpoint succeeded. Last error: {last_error}"

        try:
            result = json.loads(content)
        except json.JSONDecodeError:
            m = re.search(r'\{.*\}', content, re.DOTALL)
            if m:
                result = json.loads(m.group())
            else:
                return None, f"Parse error: {content[:200]}"

        score = float(result.get('match_score', 0))
        score = max(0, min(100, score))
        reasoning = result.get('reasoning', '')
        return score, reasoning

    except Exception as e:
        logger.warning(f"Nim scoring failed: {e}")
        return None, str(e)
