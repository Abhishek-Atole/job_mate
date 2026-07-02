from django.urls import path
from . import views

urlpatterns = [
    path('', views.JobListCreateView.as_view(), name='job_list_create'),
    path('mine/', views.EmployerJobListView.as_view(), name='employer_jobs'),
    path('recommendations/', views.JobRecommendationsView.as_view(), name='job_recommendations'),
    path('<int:pk>/', views.JobDetailView.as_view(), name='job_detail'),
]
