from rest_framework import generics, permissions, filters
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Job
from .serializers import JobSerializer
from .recommendations import get_recommendations
from users.permissions import IsEmployer, IsOwnerOrReadOnly, IsCandidate
from candidates.models import Candidate


class JobListCreateView(generics.ListCreateAPIView):
    queryset = Job.objects.filter(status='open')
    serializer_class = JobSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, ]
    search_fields = ['title', 'description', 'required_skills', 'location']
    ordering_fields = ['posted_at', 'salary_min', 'salary_max']
    ordering = ['-posted_at']

    def get_permissions(self):
        if self.request.method == 'POST':
            return [permissions.IsAuthenticated(), IsEmployer()]
        return [permissions.AllowAny()]

    def perform_create(self, serializer):
        serializer.save(employer=self.request.user.employer_profile)


class JobDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Job.objects.all()
    serializer_class = JobSerializer
    permission_classes = [IsOwnerOrReadOnly]

    def perform_destroy(self, instance):
        instance.status = 'closed'
        instance.save()


class EmployerJobListView(generics.ListAPIView):
    serializer_class = JobSerializer
    permission_classes = [permissions.IsAuthenticated, IsEmployer]

    def get_queryset(self):
        return Job.objects.filter(employer=self.request.user.employer_profile)


class JobRecommendationsView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsCandidate]

    def get(self, request):
        candidate, _ = Candidate.objects.get_or_create(user=request.user)
        skills = candidate.skills or ""
        text = f"{skills} {candidate.education or ''}"
        scored = get_recommendations(skills, text, limit=20)
        results = []
        for score, job in scored:
            data = JobSerializer(job, context={'request': request}).data
            data['match_score'] = score
            results.append(data)
        return Response(results)
