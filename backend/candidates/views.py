import re
from rest_framework import generics, permissions, status
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Candidate
from .serializers import CandidateSerializer
from users.permissions import IsCandidate


SKILL_KEYWORDS = [
    'python', 'django', 'flask', 'fastapi', 'react', 'angular', 'vue', 'javascript',
    'typescript', 'node.js', 'express', 'html', 'css', 'sass', 'tailwind', 'bootstrap',
    'java', 'spring', 'spring boot', 'kotlin', 'scala', 'go', 'golang', 'rust',
    'c++', 'c#', '.net', 'php', 'laravel', 'ruby', 'rails', 'swift', 'objective-c',
    'sql', 'postgresql', 'mysql', 'mongodb', 'redis', 'elasticsearch', 'cassandra',
    'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'terraform', 'ansible', 'jenkins',
    'ci/cd', 'linux', 'git', 'github actions', 'nginx', 'apache',
    'machine learning', 'deep learning', 'tensorflow', 'pytorch', 'scikit-learn',
    'nlp', 'computer vision', 'llm', 'rag', 'data science', 'pandas', 'numpy',
    'matplotlib', 'tableau', 'power bi', 'spark', 'hadoop', 'airflow',
    'graphql', 'rest api', 'grpc', 'websocket', 'microservices', 'soap',
    'agile', 'scrum', 'jira', 'confluence', 'figma', 'photoshop', 'ui/ux',
    'docker compose', 'helm', 'prometheus', 'grafana', 'datadog', 'new relic',
    'rabbitmq', 'kafka', 'celery', 'nginx', 'redis', 'memcached',
    'postman', 'swagger', 'openapi', 'junit', 'pytest', 'jest', 'selenium',
    'unittest', 'mocha', 'cypress', 'playwright',
]

def extract_skills_from_text(text):
    text_lower = text.lower()
    found = []
    for skill in SKILL_KEYWORDS:
        if skill in text_lower:
            found.append(skill.title())
    seen = set()
    unique = []
    for s in found:
        if s.lower() not in seen:
            seen.add(s.lower())
            unique.append(s)
    return unique


class CandidateProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = CandidateSerializer
    permission_classes = (permissions.IsAuthenticated, IsCandidate)
    parser_classes = (MultiPartParser, FormParser, JSONParser)

    def get_object(self):
        candidate, _ = Candidate.objects.get_or_create(user=self.request.user)
        return candidate

    def perform_update(self, serializer):
        serializer.save(user=self.request.user)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)


class ExtractSkillsView(APIView):
    permission_classes = (permissions.IsAuthenticated, IsCandidate)

    def post(self, request):
        file = request.FILES.get('resume_file')
        if not file:
            return Response({'error': 'No resume file provided'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            import pdfplumber
            with pdfplumber.open(file) as pdf:
                text = ' '.join(page.extract_text() or '' for page in pdf.pages)
        except Exception:
            return Response({'error': 'Could not parse PDF'}, status=status.HTTP_400_BAD_REQUEST)

        if not text.strip():
            return Response({'error': 'Could not extract text from PDF'}, status=status.HTTP_400_BAD_REQUEST)

        skills = extract_skills_from_text(text)
        words = text.split()
        return Response({'skills': skills, 'word_count': len(words)})
