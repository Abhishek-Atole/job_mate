from rest_framework import serializers
from .models import Candidate


class CandidateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Candidate
        fields = ('id', 'resume_file', 'skills', 'experience_years', 'education', 'phone')
        read_only_fields = ('id',)
        extra_kwargs = {'resume_file': {'required': False}}
