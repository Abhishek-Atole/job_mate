from rest_framework import serializers
from .models import Application


class ApplicationSerializer(serializers.ModelSerializer):
    candidate_name = serializers.CharField(source='candidate.user.get_full_name', read_only=True)
    candidate_email = serializers.CharField(source='candidate.user.email', read_only=True)
    candidate_skills = serializers.CharField(source='candidate.skills', read_only=True)
    candidate_experience = serializers.IntegerField(source='candidate.experience_years', read_only=True)
    resume_url = serializers.FileField(source='candidate.resume_file', read_only=True)
    job_title = serializers.CharField(source='job.title', read_only=True)

    class Meta:
        model = Application
        fields = (
            'id', 'job', 'job_title', 'candidate', 'candidate_name', 'candidate_email',
            'candidate_skills', 'candidate_experience', 'resume_url',
            'match_score', 'status', 'applied_at',
        )
        read_only_fields = ('id', 'match_score', 'applied_at')
