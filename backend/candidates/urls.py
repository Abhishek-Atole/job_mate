from django.urls import path
from . import views

urlpatterns = [
    path('me/', views.CandidateProfileView.as_view(), name='candidate_profile'),
    path('extract-skills/', views.ExtractSkillsView.as_view(), name='extract_skills'),
]
