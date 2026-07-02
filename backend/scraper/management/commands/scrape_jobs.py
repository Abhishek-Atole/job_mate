import logging
from django.core.management.base import BaseCommand
from django.db import transaction
from jobs.models import Job
from employers.models import Employer
from users.models import User

logger = logging.getLogger(__name__)


def _get_or_create_employer(company_name):
    email = f"scraped-{company_name.lower().replace(' ', '')}@hirematch.ai"
    try:
        employer = Employer.objects.get(user__email=email)
        return employer
    except Employer.DoesNotExist:
        pass
    user = User.objects.create_user(
        email=email, password='scraped123',
        role='employer', first_name=company_name[:30],
    )
    return Employer.objects.create(
        user=user,
        company_name=company_name[:200],
        company_description=f"Jobs sourced from external platforms",
    )


class Command(BaseCommand):
    help = "Scrape jobs from external sources (Indeed, LinkedIn, career pages)"

    def add_arguments(self, parser):
        parser.add_argument(
            '--sources', type=str, default='careers',
            help='Comma-separated list: indeed,linkedin,careers'
        )
        parser.add_argument('--query', type=str, default='software engineer')
        parser.add_argument('--location', type=str, default='')

    @transaction.atomic
    def handle(self, *args, **options):
        from scraper.scrapers import scrape_indeed, scrape_linkedin, scrape_career_pages

        sources = [s.strip() for s in options['sources'].split(',')]
        query = options['query']
        location = options['location']

        fallback_employer = _get_or_create_employer("External Companies")

        all_jobs = []

        if 'indeed' in sources:
            self.stdout.write("Scraping Indeed...")
            self.stdout.flush()
            try:
                jobs = scrape_indeed(query, location, max_pages=2)
                all_jobs.extend(jobs)
                self.stdout.write(f"  Indeed: {len(jobs)} jobs found")
            except Exception as e:
                self.stdout.write(self.style.WARNING(f"  Indeed failed: {e}"))

        if 'linkedin' in sources:
            self.stdout.write("Scraping LinkedIn...")
            self.stdout.flush()
            try:
                jobs = scrape_linkedin(query, location, max_pages=2)
                all_jobs.extend(jobs)
                self.stdout.write(f"  LinkedIn: {len(jobs)} jobs found")
            except Exception as e:
                self.stdout.write(self.style.WARNING(f"  LinkedIn failed: {e}"))

        if 'careers' in sources:
            self.stdout.write("Scraping company career pages...")
            self.stdout.flush()
            try:
                jobs = scrape_career_pages()
                all_jobs.extend(jobs)
                self.stdout.write(f"  Career pages: {len(jobs)} jobs found")
            except Exception as e:
                self.stdout.write(self.style.WARNING(f"  Career pages failed: {e}"))

        if not all_jobs:
            self.stdout.write(self.style.WARNING("No jobs scraped."))
            return

        created = 0
        for item in all_jobs:
            company = (item.get('company') or '').strip() or 'Unknown'
            employer = _get_or_create_employer(company) if company != 'Unknown' else fallback_employer

            dup = Job.objects.filter(
                title=item['title'][:200], employer=employer,
                source=item.get('source', 'scraped'),
            ).exists()
            if dup:
                continue

            Job.objects.create(
                employer=employer,
                title=item['title'][:200],
                description=(item.get('description') or '')[:2000] or f"Position at {company}.",
                required_skills='',
                location=(item.get('location') or '')[:150],
                source=item.get('source', 'scraped'),
                source_url=(item.get('url') or '')[:500],
            )
            created += 1

        self.stdout.write(self.style.SUCCESS(
            f"\nCreated {created} new jobs from {len(all_jobs)} scraped listings"
        ))
