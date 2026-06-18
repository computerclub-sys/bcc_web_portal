from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.profile_update_view, name='profile_edit'),
    path('member/<uuid:member_uuid>/', views.member_public_view, name='member_public'),
    path('member/<uuid:member_uuid>/claim/', views.member_claim_view, name='member_claim'),
    path('member/<uuid:member_uuid>/qr/', views.qr_image_view, name='qr_image'),
    path('logout/', views.logout_view, name='logout'),
    path('team/', views.team, name='team'),
    path('join/', views.join_guide, name='join_guide'),
]
