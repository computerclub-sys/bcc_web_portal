from django.urls import path
from . import views

app_name = 'cse_fest'

urlpatterns = [
    path('', views.index, name='index'),
    path('event/<slug:slug>/', views.event_detail, name='event_detail'),
    path('register/', views.register, name='register'),
]
