from django.urls import path
from . import views

urlpatterns = [
    path('me/', views.MyApplicationsView.as_view(), name='my_applications'),
    path('jobs/<int:job_id>/apply/', views.ApplyJobView.as_view(), name='apply_job'),
    path('jobs/<int:job_id>/applications/', views.JobApplicationsView.as_view(), name='job_applications'),
    path('<int:pk>/status/', views.UpdateApplicationStatusView.as_view(), name='update_status'),
]
