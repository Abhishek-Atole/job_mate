from django.urls import path
from . import views

urlpatterns = [
    path('users/', views.UserListView.as_view(), name='admin_users'),
    path('users/<int:pk>/toggle/', views.ToggleUserView.as_view(), name='toggle_user'),
    path('stats/', views.StatsView.as_view(), name='admin_stats'),
]
