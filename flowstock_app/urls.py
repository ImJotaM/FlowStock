from django.urls import path
from . import views

urlpatterns = [
    path('', views.root_redirect),
    path('login/', views.login, name='login'),
    path('register/', views.register, name='register'),
    path('home/', views.stock_list, name='home'),
    path('stock/create/', views.create_stock, name='stock-create'),
    path('stock/update/<int:stock_id>/', views.update_stock, name='stock-update'),
    path('stock/delete/<int:stock_id>/', views.delete_stock, name='stock-delete'),
    path('account/', views.account_detail, name='account_detail'),
    path('faqs/', views.faqs, name='faqs'),
    path('profiles/', views.profiles, name='profiles'),
    path('estoque/<int:stock_id>/', views.stock_detail, name='stock_detail'),
    path('stock/<int:stock_id>/generate-pdf-stock/', views.generate_pdf_stock, name='generate-pdf-stock'),
]