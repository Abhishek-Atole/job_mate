from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from users.models import User
from users.serializers import UserSerializer
from users.permissions import IsAdmin
from jobs.models import Job
from applications.models import Application
from django.db.models import Count


class UserListView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (permissions.IsAuthenticated, IsAdmin)


class ToggleUserView(APIView):
    permission_classes = (permissions.IsAuthenticated, IsAdmin)

    def put(self, request, pk):
        try:
            user = User.objects.get(id=pk)
            user.is_active = not user.is_active
            user.save()
            return Response({'status': 'toggled', 'is_active': user.is_active})
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)


class StatsView(APIView):
    permission_classes = (permissions.IsAuthenticated, IsAdmin)

    def get(self, request):
        return Response({
            'total_users': User.objects.count(),
            'total_employers': User.objects.filter(role='employer').count(),
            'total_candidates': User.objects.filter(role='candidate').count(),
            'total_jobs': Job.objects.count(),
            'open_jobs': Job.objects.filter(status='open').count(),
            'total_applications': Application.objects.count(),
            'applications_by_status': {
                'applied': Application.objects.filter(status='applied').count(),
                'shortlisted': Application.objects.filter(status='shortlisted').count(),
                'rejected': Application.objects.filter(status='rejected').count(),
                'hired': Application.objects.filter(status='hired').count(),
            },
        })
