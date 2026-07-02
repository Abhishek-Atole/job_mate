from django.urls import path
from . import views

urlpatterns = [
    path('me/', views.EmployerProfileView.as_view(), name='employer_profile'),
]
