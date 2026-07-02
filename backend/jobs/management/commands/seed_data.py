import random
from django.core.management.base import BaseCommand
from django.utils import timezone
from users.models import User
from employers.models import Employer
from candidates.models import Candidate
from jobs.models import Job
from applications.models import Application

COMPANIES = [
    {"name": "Google", "desc": "Global technology leader in search, cloud, and AI solutions", "location": "Mountain View, CA", "domain": "google.com", "is_inr": False},
    {"name": "Stripe", "desc": "Online payment processing platform for internet businesses", "location": "San Francisco, CA", "domain": "stripe.com", "is_inr": False},
    {"name": "Airbnb", "desc": "Global marketplace for vacation rentals and travel experiences", "location": "San Francisco, CA", "domain": "airbnb.com", "is_inr": False},
    {"name": "Spotify", "desc": "Digital music streaming service with personalized audio experiences", "location": "Stockholm, Sweden", "domain": "spotify.com", "is_inr": False},
    {"name": "Netflix", "desc": "Global streaming entertainment service with original content", "location": "Los Gatos, CA", "domain": "netflix.com", "is_inr": False},
    {"name": "Infosys", "desc": "Leading Indian IT services and consulting company", "location": "Bangalore, India", "domain": "infosys.com", "is_inr": True},
    {"name": "TCS", "desc": "India's largest IT services company delivering digital transformation", "location": "Mumbai, India", "domain": "tcs.com", "is_inr": True},
    {"name": "Zoho", "desc": "Indian software company building cloud-based business tools", "location": "Chennai, India", "domain": "zoho.com", "is_inr": True},
    {"name": "Flipkart", "desc": "India's leading e-commerce marketplace", "location": "Bangalore, India", "domain": "flipkart.com", "is_inr": True},
    {"name": "Razorpay", "desc": "Indian payment gateway and banking platform for businesses", "location": "Bangalore, India", "domain": "razorpay.com", "is_inr": True},
]

CANDIDATE_NAMES = [
    ("Aarav", "Sharma"), ("Vivaan", "Verma"), ("Aditya", "Patel"), ("Vihaan", "Reddy"),
    ("Arjun", "Singh"), ("Sai", "Kumar"), ("Ishaan", "Nair"), ("Reyansh", "Joshi"),
    ("Krishna", "Menon"), ("Dhruv", "Rao"), ("Alice", "Johnson"), ("Bob", "Smith"),
    ("Charlie", "Brown"), ("Diana", "Prince"), ("Eve", "Davis"), ("Frank", "Miller"),
    ("Grace", "Wilson"), ("Henry", "Taylor"), ("Ivy", "Chen"), ("Jack", "Williams"),
    ("Kavya", "Iyer"), ("Rohan", "Deshmukh"), ("Ananya", "Gupta"), ("Neha", "Kapoor"),
    ("Rahul", "Mehta"), ("Priya", "Sundaram"), ("Vikram", "Choudhury"), ("Sneha", "Pillai"),
    ("Arun", "Krishnan"), ("Deepa", "Subramanian"), ("Nikhil", "Agarwal"), ("Pooja", "Bhat"),
    ("Manoj", "Prasad"), ("Shreya", "Ghosh"), ("Karthik", "Rajan"), ("Meera", "Narang"),
    ("Ankit", "Saxena"), ("Ritu", "Arora"), ("Harsh", "Vohra"), ("Tanya", "Sethi"),
    ("Gaurav", "Thakur"), ("Ishita", "Bajaj"), ("Pranav", "Kohli"), ("Divya", "Mishra"),
    ("Siddharth", "Wagh"), ("Nandini", "Chopra"), ("Abhay", "Tiwari"), ("Lakshmi", "Nambiar"),
    ("Raj", "Bajwa"), ("Sara", "Khan"), ("Michael", "O'Brien"), ("Emma", "Thompson"),
    ("James", "Anderson"), ("Sophia", "Martinez"), ("William", "Garcia"), ("Olivia", "Robinson"),
    ("Ethan", "Clark"), ("Isabella", "Lewis"), ("Liam", "Walker"), ("Mia", "Hall"),
    ("Noah", "Allen"), ("Charlotte", "Young"), ("Logan", "King"), ("Amelia", "Wright"),
    ("Lucas", "Scott"), ("Harper", "Adams"), ("Mason", "Baker"), ("Evelyn", "Hill"),
    ("David", "Nelson"), ("Abigail", "Campbell"), ("Oliver", "Mitchell"), ("Emily", "Roberts"),
    ("Thomas", "Turner"), ("Elizabeth", "Phillips"), ("Daniel", "Evans"), ("Sofia", "Morris"),
    ("Jose", "Gonzalez"), ("Ella", "Perez"), ("Christopher", "Sanchez"), ("Avery", "Reed"),
    ("Andrew", "Cook"), ("Scarlett", "Morgan"), ("Matthew", "Bell"), ("Victoria", "Cooper"),
    ("Luke", "Bailey"), ("Lily", "Kelly"), ("Samuel", "Howard"), ("Chloe", "Ward"),
    ("Sebastian", "Cox"), ("Penelope", "Diaz"), ("Jackson", "Richardson"), ("Layla", "Watson"),
    ("Owen", "Brooks"), ("Zoey", "Gray"), ("Dylan", "Stone"), ("Riley", "Fisher"),
    ("Nathan", "Webb"), ("Hannah", "Pearce"),
]

SKILL_POOL = [
    "Python", "Java", "JavaScript", "TypeScript", "Go", "Rust", "C++", "Ruby",
    "React", "Angular", "Vue.js", "Node.js", "Django", "Flask", "Spring Boot",
    "FastAPI", "PostgreSQL", "MySQL", "MongoDB", "Redis", "Elasticsearch",
    "AWS", "Azure", "GCP", "Docker", "Kubernetes", "Terraform", "CI/CD",
    "Git", "Linux", "REST API", "GraphQL", "gRPC", "Kafka", "RabbitMQ",
    "TensorFlow", "PyTorch", "Scikit-learn", "Pandas", "NumPy", "NLP",
    "Machine Learning", "Deep Learning", "Data Analysis", "Tableau", "Power BI",
    "Agile", "Scrum", "JIRA", "Product Management", "UI/UX Design", "Figma",
    "HTML", "CSS", "SASS", "Tailwind CSS", "Bootstrap", "Material UI",
    "iOS", "Android", "Swift", "Kotlin", "Flutter", "React Native",
    "C#", ".NET", "PHP", "Laravel", "WordPress", "Shopify",
    "Salesforce", "SAP", "Oracle", "Blockchain", "Solidity",
    "Cybersecurity", "Network Security", "Penetration Testing",
    "Project Management", "Digital Marketing", "SEO", "Content Writing",
]

JOB_TITLES = [
    "Software Engineer", "Senior Software Engineer", "Staff Software Engineer",
    "Backend Developer", "Frontend Developer", "Full Stack Developer",
    "Data Scientist", "Senior Data Scientist", "Machine Learning Engineer",
    "DevOps Engineer", "Site Reliability Engineer", "Cloud Architect",
    "Product Manager", "Senior Product Manager", "Technical Product Manager",
    "UI/UX Designer", "Senior UI/UX Designer", "Product Designer",
    "Data Engineer", "Senior Data Engineer", "Big Data Engineer",
    "Mobile Developer", "iOS Developer", "Android Developer",
    "QA Engineer", "SDET", "Test Automation Engineer",
    "Security Engineer", "Cybersecurity Analyst", "Security Architect",
    "Technical Writer", "Solutions Architect", "Engineering Manager",
    "Data Analyst", "Business Analyst", "Marketing Analyst",
    "Systems Administrator", "Network Engineer", "Database Administrator",
    "Research Scientist", "AI Engineer", "NLP Engineer",
    "Scrum Master", "Delivery Manager", "Technical Lead",
    "Intern - Software Engineering", "Intern - Data Science", "Associate Engineer",
]

INDIAN_CITIES = ["Mumbai", "Bangalore", "Hyderabad", "Chennai", "Pune", "Delhi", "Gurgaon", "Noida", "Kolkata", "Ahmedabad"]
US_CITIES = ["San Francisco, CA", "New York, NY", "Seattle, WA", "Austin, TX", "Chicago, IL", "Boston, MA", "Denver, CO", "Los Angeles, CA"]
GLOBAL_CITIES = ["London, UK", "Berlin, Germany", "Toronto, Canada", "Sydney, Australia", "Singapore", "Dubai, UAE"]
REMOTE = ["Remote - India", "Remote - US", "Remote - Global"]

EDUCATION = ["B.Tech", "M.Tech", "BCA", "MCA", "BSc", "MSc", "MBA", "BCom", "MCom", "BA", "MA", "PhD", "B.E.", "M.E."]

SKILL_BY_TITLE = {
    "Software": "Python,Java,JavaScript,React,Django,PostgreSQL,Docker,AWS,Git,Linux",
    "Backend": "Python,Java,Go,Node.js,Django,Spring Boot,PostgreSQL,Redis,Docker,Kubernetes",
    "Frontend": "JavaScript,TypeScript,React,Vue.js,Angular,HTML,CSS,Tailwind,SASS,Git",
    "Full Stack": "Python,JavaScript,React,Django,Node.js,PostgreSQL,Docker,AWS,Git",
    "Data Scientist": "Python,TensorFlow,PyTorch,Scikit-learn,Pandas,NumPy,Machine Learning,SQL,NLP",
    "Data Engineer": "Python,SQL,Spark,Kafka,Airflow,AWS,PostgreSQL,MongoDB,Docker",
    "Machine Learning": "Python,TensorFlow,PyTorch,Scikit-learn,NLP,Deep Learning,Docker,AWS",
    "DevOps": "Docker,Kubernetes,Terraform,AWS,Azure,CI/CD,Linux,Python,Bash,Git",
    "Product Manager": "Product Management,Agile,Scrum,JIRA,Data Analysis,UI/UX,SQL",
    "Designer": "Figma,UI/UX Design,HTML,CSS,JavaScript,Prototyping,User Research",
    "Mobile": "Swift,Kotlin,Flutter,React Native,iOS,Android,Git,REST API",
    "QA": "Python,Java,Selenium,Test Automation,CI/CD,Git,Agile,JIRA",
    "Security": "Cybersecurity,Python,Linux,Network Security,Penetration Testing,AWS",
    "Intern": "Python,JavaScript,HTML,CSS,Git,SQL,Linux",
    "Engineer": "Python,Java,JavaScript,Git,Docker,AWS,PostgreSQL,Linux",
    "Analyst": "SQL,Python,Excel,Tableau,Data Analysis,Power BI,Pandas",
    "Manager": "Project Management,Agile,Scrum,JIRA,Leadership,Product Management",
    "Architect": "AWS,Azure,GCP,Docker,Kubernetes,Terraform,Python,Java,Linux",
    "Research": "Python,TensorFlow,PyTorch,Research,NLP,Machine Learning,Statistics",
    "Lead": "Python,Java,System Design,Microservices,Agile,Leadership,Docker,Kubernetes",
}

DESCRIPTION_TEMPLATES = [
    "We are looking for a skilled {title} to join our {team} team. You will work on {work} using {skills}. Ideal candidates have {exp} years of experience and strong problem-solving skills.",
    "Join our {team} team as a {title}! You'll be responsible for {work}. We're looking for someone with expertise in {skills} and at least {exp} years of experience.",
    "{title} needed at {company}. You will {work}. Must have strong knowledge of {skills} and {exp}+ years of experience. Great team and benefits!",
    "Exciting opportunity for a {title} to join {company}. You'll {work}. Required skills: {skills}. Experience: {exp}+ years. Apply now!",
]

TEAMS = ["Platform", "Infrastructure", "Core Product", "Growth", "Data", "Mobile", "Security", "Design", "Marketplace", "Payments", "Search", "Cloud", "Enterprise", "Consumer", "Developer Experience"]
WORK_TASKS = [
    "building and maintaining scalable microservices",
    "developing customer-facing features",
    "designing and implementing APIs",
    "optimizing system performance and reliability",
    "building data pipelines and analytics tools",
    "creating intuitive user interfaces",
    "developing ML models for personalization",
    "building real-time processing systems",
    "designing cloud infrastructure",
    "implementing security best practices",
    "building mobile applications",
    "creating developer tools and frameworks",
    "designing recommendation systems",
    "building payment processing systems",
    "developing search and discovery features",
]


def pick_skills(title: str) -> str:
    for key, skills in SKILL_BY_TITLE.items():
        if key.lower() in title.lower():
            return skills
    default = random.choice(list(SKILL_BY_TITLE.values()))
    return default


def pick_salary(company_is_inr: bool, seniority: str) -> tuple:
    if company_is_inr:
        ranges = {"junior": (400000, 1200000), "mid": (1200000, 2500000), "senior": (2500000, 6000000)}
    else:
        ranges = {"junior": (60000, 120000), "mid": (120000, 200000), "senior": (200000, 450000)}
    r = ranges[seniority]
    return (random.randint(r[0], r[1]), random.randint(r[1], int(r[1] * 1.5)))


class Command(BaseCommand):
    help = "Seed database with employers, candidates, jobs, and applications"

    def add_arguments(self, parser):
        parser.add_argument('--jobs', type=int, default=1000, help='Number of jobs to create')
        parser.add_argument('--candidates', type=int, default=100, help='Number of candidates to create')

    def handle(self, *args, **options):
        job_count = options['jobs']
        candidate_count = options['candidates']

        self.stdout.write("Creating employers...")
        employer_users = []
        employers = []
        for i, co in enumerate(COMPANIES):
            email = f"hr@{co['domain']}"
            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    'role': 'employer',
                    'first_name': co['name'],
                }
            )
            if created:
                user.set_password('employer123')
                user.save()
            emp, _ = Employer.objects.get_or_create(
                user=user,
                defaults={
                    'company_name': co['name'],
                    'company_description': co['desc'],
                    'website': f"https://{co['domain']}",
                    'location': co['location'],
                }
            )
            employer_users.append(user)
            employers.append((emp, co))

        self.stdout.write(f"  Created {len(employers)} employers (password: employer123)")

        self.stdout.write("Creating candidates...")
        candidate_users = []
        candidates_list = []
        for i in range(min(candidate_count, len(CANDIDATE_NAMES))):
            first, last = CANDIDATE_NAMES[i]
            email = f"{first.lower()}.{last.lower()}@email.com"
            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    'role': 'candidate',
                    'first_name': first,
                    'last_name': last,
                }
            )
            if created:
                user.set_password('candidate123')
                user.save()

            skill_count = random.randint(3, 8)
            skills = ", ".join(random.sample(SKILL_POOL, skill_count))
            exp_years = random.randint(0, 15)
            location_pool = INDIAN_CITIES + US_CITIES + GLOBAL_CITIES + REMOTE
            location = random.choice(location_pool)
            education = random.choice(EDUCATION)

            cand, _ = Candidate.objects.get_or_create(
                user=user,
                defaults={
                    'skills': skills,
                    'experience_years': exp_years,
                    'education': education,
                    'phone': f"+1{random.randint(2000000000, 9999999999)}",
                }
            )
            candidate_users.append(user)
            candidates_list.append(cand)

        self.stdout.write(f"  Created {len(candidates_list)} candidates (password: candidate123)")

        self.stdout.write("Creating jobs...")
        self.stdout.flush()
        jobs_created = 0
        for emp, co in employers:
            n_jobs = max(1, job_count // len(employers))
            batch = []
            for _ in range(n_jobs):
                title = random.choice(JOB_TITLES)
                team = random.choice(TEAMS)
                work = random.choice(WORK_TASKS)
                skills = pick_skills(title)

                if "Intern" in title or "Junior" in title or "Associate" in title:
                    seniority = "junior"
                    exp = random.randint(0, 2)
                elif "Senior" in title or "Staff" in title or "Lead" in title or "Architect" in title or "Manager" in title:
                    seniority = "senior"
                    exp = random.randint(5, 12)
                else:
                    seniority = "mid"
                    exp = random.randint(2, 6)

                salary_min, salary_max = pick_salary(co['is_inr'], seniority)

                desc_template = random.choice(DESCRIPTION_TEMPLATES)
                description = desc_template.format(
                    title=title, company=co['name'], team=team,
                    work=work, skills=skills, exp=exp
                )

                location_pool = [co['location']]
                if co['is_inr']:
                    location_pool += INDIAN_CITIES[:3] + ["Remote - India"]
                else:
                    location_pool += US_CITIES[:3] + ["Remote - US"]

                location = random.choice(location_pool)

                now = timezone.now()
                days_ago = random.randint(1, 60)

                batch.append(Job(
                    employer=emp,
                    title=title,
                    description=description,
                    required_skills=skills,
                    location=location,
                    salary_min=salary_min,
                    salary_max=salary_max,
                    posted_at=now - timezone.timedelta(days=days_ago),
                ))

            Job.objects.bulk_create(batch, ignore_conflicts=True)
            jobs_created += len(batch)
            self.stdout.write(f"  {co['name']}: {len(batch)} jobs created")
            self.stdout.flush()

        self.stdout.write(f"  Total: {jobs_created} jobs")

        self.stdout.write("Creating sample applications...")
        self.stdout.flush()
        open_jobs = list(Job.objects.filter(status='open').only('id', 'required_skills'))
        apps_created = 0
        batch = []
        for idx, cand in enumerate(candidates_list):
            n_apps = random.randint(0, 5)
            candidate_skills = set(s.strip().lower() for s in (cand.skills or '').split(',') if s.strip())
            if not candidate_skills:
                continue
            for job in random.sample(open_jobs, min(50, len(open_jobs))):
                job_skills = set(s.strip().lower() for s in (job.required_skills or '').split(',') if s.strip())
                overlap = len(candidate_skills & job_skills)
                if overlap > 0:
                    score = random.uniform(20, 95)
                    batch.append(Application(
                        job=job,
                        candidate=cand,
                        match_score=round(score, 2),
                        status=random.choice(['applied', 'shortlisted', 'rejected']),
                    ))
                    if len(batch) >= n_apps:
                        break
            if (idx + 1) % 20 == 0:
                self.stdout.write(f"  {idx + 1}/{len(candidates_list)} candidates processed ({len(batch)} apps so far)")
                self.stdout.flush()

        Application.objects.bulk_create(batch, ignore_conflicts=True)
        apps_created = len(batch)
        self.stdout.write(f"  Created {apps_created} applications")
        self.stdout.write(self.style.SUCCESS(
            f"\nDone! Created:\n"
            f"  {len(employers)} employers (login: hr@company.com / employer123)\n"
            f"  {len(candidates_list)} candidates (login: first.last@email.com / candidate123)\n"
            f"  {jobs_created} jobs\n"
            f"  {apps_created} applications"
        ))
