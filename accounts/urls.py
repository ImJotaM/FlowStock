from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from .forms import CustomPasswordResetForm, CustomSetPasswordForm

urlpatterns = [
    path('login/', views.login, name='login'),
    path('register/', views.register, name='register'),
    path('', views.account, name='account'),
    path('logout/', views.view_logout, name='logout'),
	path('password-reset/', auth_views.PasswordResetView.as_view(
            template_name='accounts/password_reset/main.html',
            email_template_name='accounts/password_reset/email_template/email.html',
            subject_template_name='accounts/password_reset/email_template/subject.txt',
			form_class=CustomPasswordResetForm,
			success_url='done/'), name='password_reset'),

	path('password-reset/done/', 
        auth_views.PasswordResetDoneView.as_view(template_name='accounts/password_reset/done.html'), 
        name='password_reset_done'),

    path('reset/<uidb64>/<token>/', 
        auth_views.PasswordResetConfirmView.as_view(template_name='accounts/password_reset/confirm.html', form_class=CustomSetPasswordForm), 
        name='password_reset_confirm'),

    path('reset/done/', 
        auth_views.PasswordResetCompleteView.as_view(template_name='accounts/password_reset/complete.html'), 
        name='password_reset_complete'),
]