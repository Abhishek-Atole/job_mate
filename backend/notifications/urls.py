from django.urls import path
from . import views

urlpatterns = [
    path('', views.NotificationListView.as_view(), name='notifications'),
    path('<int:pk>/read/', views.MarkAsReadView.as_view(), name='mark_read'),
    path('read-all/', views.MarkAllAsReadView.as_view(), name='mark_all_read'),
]
