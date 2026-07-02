from rest_framework import generics, permissions
from .models import Employer
from .serializers import EmployerSerializer
from users.permissions import IsEmployer


class EmployerProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = EmployerSerializer
    permission_classes = (permissions.IsAuthenticated, IsEmployer)

    def get_object(self):
        employer, _ = Employer.objects.get_or_create(user=self.request.user)
        return employer
