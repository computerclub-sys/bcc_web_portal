from django.urls import path
from . import views

app_name = 'cse_fest'

urlpatterns = [
    path('', views.index, name='index'),
    path('event/<slug:slug>/', views.event_detail, name='event_detail'),
    path('register/', views.register, name='register'),
    path('application-status/', views.application_status, name='application_status'),
    path('invitation/', views.invitation, name='invitation'),
    path('export-approved/', views.export_approved_excel, name='export_approved'),
]
