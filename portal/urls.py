from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('profile/', views.profile_view, name='profile'),
    path('apply-membership/', views.apply_membership, name='apply_membership'),
    path('member/<uuid:member_uuid>/', views.member_public_view, name='member_public'),
    path('logout/', views.logout_view, name='logout'),
]
