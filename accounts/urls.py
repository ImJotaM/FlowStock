from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login, name='login'),
    path('register/', views.register, name='register'),
    path('', views.account, name='account'),
    path('profiles/', views.profiles, name='profiles'),
]