import re
import logging
from datetime import datetime
from urllib.parse import urljoin

logger = logging.getLogger(__name__)


def safe_text(el, selector, default=""):
    try:
        return el.select_one(selector).get_text(strip=True)
    except AttributeError:
        return default


def scrape_indeed(query: str, location: str = "", max_pages: int = 3):
    try:
        import httpx
        from bs4 import BeautifulSoup
    except ImportError:
        logger.error("httpx and beautifulsoup4 required for scraping")
        return []

    jobs = []
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "text/html,application/xhtml+xml",
    }

    for page in range(max_pages):
        start = page * 10
        url = (
            f"https://www.indeed.com/jobs?q={query.replace(' ', '+')}"
            f"&l={location}&start={start}"
        )
        try:
            resp = httpx.get(url, headers=headers, timeout=15, follow_redirects=True)
            resp.raise_for_status()
        except Exception as e:
            logger.warning(f"Indeed page {page} failed: {e}")
            break

        soup = BeautifulSoup(resp.text, "lxml")
        cards = soup.select("[class*='job_seen_beacon'], [class*='job-listing'], .jobsearch-SerpJobCard")
        if not cards:
            cards = soup.select("a[data-jk]")

        for card in cards:
            title = safe_text(card, "h2, [class*='title'], [class*='jobTitle']")
            company = safe_text(card, "[class*='company'], [class*='employer']")
            loc = safe_text(card, "[class*='location']")
            snippet = safe_text(card, "[class*='summary'], [class*='snippet']")
            link_el = card.select_one("a[href]")
            link = urljoin("https://www.indeed.com", link_el["href"]) if link_el else ""

            if not title:
                continue

            jobs.append({
                "title": title.strip(),
                "company": company.strip(),
                "location": loc.strip(),
                "description": snippet.strip(),
                "url": link,
                "source": "indeed",
            })

    return jobs


def scrape_linkedin(query: str, location: str = "", max_pages: int = 2):
    try:
        import httpx
        from bs4 import BeautifulSoup
    except ImportError:
        logger.error("httpx and beautifulsoup4 required for scraping")
        return []

    jobs = []
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "text/html,application/xhtml+xml",
    }

    for page in range(max_pages):
        url = (
            f"https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?"
            f"keywords={query.replace(' ', '%20')}&location={location}&start={page * 25}"
        )
        try:
            resp = httpx.get(url, headers=headers, timeout=15, follow_redirects=True)
            resp.raise_for_status()
        except Exception as e:
            logger.warning(f"LinkedIn page {page} failed: {e}")
            break

        soup = BeautifulSoup(resp.text, "lxml")
        cards = soup.select("li[data-entity-urn], .job-card-container, .base-card")

        for card in cards:
            title = safe_text(card, "h3, [class*='title'], [class*='job-title']")
            company = safe_text(card, "[class*='company'], [class*='employer'], [class*='org-name']")
            loc = safe_text(card, "[class*='location'], [class*='bullet']")
            link_el = card.select_one("a[href]")
            link = link_el["href"] if link_el else ""

            if not title:
                continue

            jobs.append({
                "title": title.strip(),
                "company": company.strip(),
                "location": loc.strip(),
                "description": "",
                "url": link,
                "source": "linkedin",
            })

    return jobs


CAREER_PAGE_URLS = [
    ("Google", "https://careers.google.com/jobs/results/"),
    ("Microsoft", "https://careers.microsoft.com/us/en/search-results"),
    ("Apple", "https://jobs.apple.com/en-us/search"),
    ("Amazon", "https://www.amazon.jobs/en-gb/search"),
    ("Meta", "https://www.metacareers.com/jobs/"),
    ("Netflix", "https://jobs.netflix.com/search"),
    ("Spotify", "https://www.lifeatspotify.com/jobs"),
    ("Stripe", "https://stripe.com/jobs/search"),
    ("Airbnb", "https://careers.airbnb.com/positions/"),
    ("Uber", "https://www.uber.com/us/en/careers/list/"),
    ("Shopify", "https://www.shopify.com/careers/search"),
    ("Adobe", "https://www.adobe.com/careers.html"),
    ("Atlassian", "https://www.atlassian.com/company/careers"),
    ("Cloudflare", "https://www.cloudflare.com/careers/"),
    ("GitLab", "https://about.gitlab.com/jobs/"),
]


def scrape_career_pages(timeout_per_url: int = 8):
    try:
        import httpx
        from bs4 import BeautifulSoup
    except ImportError:
        logger.error("httpx and beautifulsoup4 required for scraping")
        return []

    all_jobs = []
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "text/html,application/xhtml+xml",
    }

    for company_name, url in CAREER_PAGE_URLS:
        try:
            resp = httpx.get(url, headers=headers, timeout=timeout_per_url, follow_redirects=True)
            resp.raise_for_status()
        except Exception as e:
            logger.info(f"Skipped {company_name}: {e}")
            continue

        soup = BeautifulSoup(resp.text, "lxml")
        text = soup.get_text()
        title_keywords = re.findall(
            r'[A-Z][a-z]+ (?:Engineer|Developer|Scientist|Manager|Designer|Analyst|Intern|Architect)',
            text
        )
        title_keywords = list(set(t.strip() for t in title_keywords if len(t.strip()) > 5))

        for title in title_keywords[:5]:
            all_jobs.append({
                "title": title,
                "company": company_name,
                "location": "See career page",
                "description": f"Position at {company_name}. Apply at their career page.",
                "url": url,
                "source": "career_page",
            })

        logger.info(f"Scraped {len(title_keywords[:5])} titles from {company_name}")

    return all_jobs
