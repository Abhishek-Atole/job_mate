from rest_framework import serializers
from .models import Job


class JobSerializer(serializers.ModelSerializer):
    employer_name = serializers.CharField(source='employer.company_name', read_only=True)
    employer_id = serializers.IntegerField(source='employer.id', read_only=True)
    applications_count = serializers.SerializerMethodField()

    class Meta:
        model = Job
        fields = (
            'id', 'employer', 'employer_name', 'employer_id',
            'title', 'description', 'required_skills', 'location',
            'salary_min', 'salary_max', 'status', 'posted_at', 'expires_at',
            'applications_count',
        )
        read_only_fields = ('id', 'employer', 'posted_at')

    def get_applications_count(self, obj):
        return obj.applications.count()

    def create(self, validated_data):
        validated_data['employer'] = self.context['request'].user.employer_profile
        return super().create(validated_data)
