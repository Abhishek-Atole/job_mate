from rest_framework import serializers
from .models import Employer


class EmployerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employer
        fields = ('id', 'company_name', 'company_description', 'website', 'location', 'logo')
        read_only_fields = ('id',)
