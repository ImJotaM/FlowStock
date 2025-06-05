from django.urls import path
from . import views

urlpatterns = [
    path('', views.root_redirect),
    path('login/', views.login, name='login'),
    path('register/', views.register, name='register'),
    path('home/', views.home, name='home'),
    path('account/', views.account_detail, name='account_detail'),
    path('faqs/', views.faqs, name='faqs'),
    path('profiles/', views.profiles, name='profiles'),
    path('estoque/<int:stock_id>/', views.stock_detail, name='stock_detail')
]