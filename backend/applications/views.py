import requests
from django.conf import settings
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from .models import Application
from .serializers import ApplicationSerializer
from jobs.models import Job
from candidates.models import Candidate
from users.permissions import IsCandidate, IsEmployer, IsOwnerOrReadOnly
from notifications.models import Notification


def call_nlp_scoring(resume_text, job_description):
    try:
        nlp_url = settings.NLP_SERVICE_URL
        resp = requests.post(
            f"{nlp_url}/api/score/",
            json={"resume_text": resume_text, "job_description": job_description},
            timeout=10,
        )
        if resp.status_code == 200:
            return resp.json().get("match_score")
    except requests.exceptions.RequestException:
        pass
    return None

def local_skill_score(resume_text, job_description):
    resume_words = set(resume_text.lower().split())
    job_words = set(job_description.lower().split())
    if not resume_words or not job_words:
        return 0
    overlap = resume_words & job_words
    jaccard = len(overlap) / len(resume_words | job_words)
    coverage = len(overlap) / len(job_words)
    return round(((jaccard * 0.5) + (coverage * 0.5)) * 100, 2)


class ApplyJobView(generics.CreateAPIView):
    serializer_class = ApplicationSerializer
    permission_classes = (permissions.IsAuthenticated, IsCandidate)

    def create(self, request, *args, **kwargs):
        job_id = self.kwargs.get('job_id')
        try:
            job = Job.objects.get(id=job_id, status='open')
        except Job.DoesNotExist:
            return Response({'error': 'Job not found or closed'}, status=status.HTTP_404_NOT_FOUND)

        candidate, _ = Candidate.objects.get_or_create(user=request.user)

        if Application.objects.filter(job=job, candidate=candidate).exists():
            return Response({'error': 'Already applied'}, status=status.HTTP_400_BAD_REQUEST)

        application = Application.objects.create(job=job, candidate=candidate)

        resume_text = ''
        if candidate.resume_file:
            try:
                import pdfplumber
                with pdfplumber.open(candidate.resume_file.path) as pdf:
                    resume_text = ' '.join(page.extract_text() or '' for page in pdf.pages)
            except Exception:
                pass

        if not resume_text.strip() and candidate.skills:
            skills_clean = candidate.skills.replace(',', ' ')
            resume_text = f"{skills_clean} {candidate.education} {candidate.experience_years} years experience"

        if resume_text.strip():
            try:
                score = call_nlp_scoring(resume_text, job.description)
                if score is None:
                    score = local_skill_score(resume_text, job.description)
                application.match_score = score
                application.save(update_fields=['match_score'])
            except Exception:
                pass

        serializer = self.get_serializer(application)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class JobApplicationsView(generics.ListAPIView):
    serializer_class = ApplicationSerializer
    permission_classes = (permissions.IsAuthenticated, IsEmployer)

    def get_queryset(self):
        job_id = self.kwargs.get('job_id')
        return Application.objects.filter(job_id=job_id).select_related(
            'candidate', 'candidate__user', 'job'
        ).order_by('-match_score')


class UpdateApplicationStatusView(generics.UpdateAPIView):
    queryset = Application.objects.all()
    permission_classes = (permissions.IsAuthenticated, IsEmployer)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        status_value = request.data.get('status')
        if status_value not in dict(Application.Status.choices):
            return Response({'error': 'Invalid status'}, status=status.HTTP_400_BAD_REQUEST)
        instance.status = status_value
        instance.save()
        Notification.objects.create(
            user=instance.candidate.user,
            message=f"Your application for '{instance.job.title}' has been {instance.status}."
        )
        return Response(ApplicationSerializer(instance).data)


class MyApplicationsView(generics.ListAPIView):
    serializer_class = ApplicationSerializer
    permission_classes = (permissions.IsAuthenticated, IsCandidate)

    def get_queryset(self):
        candidate, _ = Candidate.objects.get_or_create(user=self.request.user)
        return Application.objects.filter(candidate=candidate).select_related('job', 'candidate__user')
