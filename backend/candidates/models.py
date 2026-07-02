from django.db import models
from users.models import User


def resume_upload_path(instance, filename):
    import uuid
    ext = filename.split('.')[-1]
    return f'resumes/{uuid.uuid4()}.{ext}'


class Candidate(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='candidate_profile')
    resume_file = models.FileField(upload_to=resume_upload_path, blank=True, null=True)
    skills = models.TextField(blank=True)
    experience_years = models.IntegerField(default=0)
    education = models.TextField(blank=True)
    phone = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return f"{self.user.email}'s profile"
