from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import SignUpForm, LoginForm
from django.contrib.auth import authenticate, login as auth_login, update_session_auth_hash, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

def register(request):
	if request.method == 'POST':
		form = SignUpForm(request.POST)
		if form.is_valid():
			user = form.save()
			auth_login(request, user)
			return redirect('home')
	else:
		form = SignUpForm()
	return render(request, 'accounts/register.html', {'form': form})

def login(request):
	if request.method == 'POST':
		form = LoginForm(request, data=request.POST)
		if form.is_valid():
			username = form.cleaned_data.get('username')
			password = form.cleaned_data.get('password')
			user = authenticate(request, username=username, password=password)
			if user is not None:
				auth_login(request, user)
				return redirect('home')
	else:
		form = LoginForm()
	return render(request, 'accounts/login.html', {'form': form})


@login_required
def account(request):
    
	if request.method == 'POST':
		if 'delete_id' in request.POST:
			user_id = request.POST.get('delete_id')
			if request.user.id == int(user_id):
				logout(request)
				User.objects.filter(id=user_id).delete()
				messages.success(request, 'Sua conta foi excluída com sucesso.')
				return redirect('home')
			else:
				messages.error(request, 'Não foi possível excluir a conta.')
				return redirect('account')

		field = request.POST.get('field')
		new_value = request.POST.get('new_value')
        
		if field == 'name':
			if not new_value or not new_value.strip():
				messages.error(request, 'O nome não pode estar vazio', extra_tags='redefining_name')
			elif new_value.strip() == request.user.username:
				messages.error(request, 'Digite um nome diferente do atual', extra_tags='redefining_name')
			elif User.objects.exclude(pk=request.user.pk).filter(username=new_value.strip()).exists():
				messages.error(request, 'Este nome já está em uso por outro usuário', extra_tags='redefining_name')
			else:
				request.user.username = new_value.strip()
				request.user.save()
				messages.success(request, 'Nome atualizado com sucesso!', extra_tags='redefining_name')
		
		elif field == 'email':
			if not new_value or not new_value.strip():
				messages.error(request, 'O e-mail não pode estar vazio', extra_tags='redefining_email')
			elif new_value.strip() == request.user.email:
				messages.error(request, 'Digite um email diferente do atual', extra_tags='redefining_email')
			else:
				try:
					validate_email(new_value.strip())
				except ValidationError:
					messages.error(request, 'Formato de e-mail inválido', extra_tags='redefining_email')
				else:
					if User.objects.exclude(pk=request.user.pk).filter(email=new_value.strip()).exists():
						messages.error(request, 'Este e-mail já está em uso por outra conta', extra_tags='redefining_email')
					else:
						request.user.email = new_value.strip()
						request.user.save()
						messages.success(request, 'E-mail atualizado com sucesso!', extra_tags='redefining_email')

		elif field == 'password':
			if new_value and len(new_value) >= 8:
				request.user.set_password(new_value)
				request.user.save()
				update_session_auth_hash(request, request.user)
				messages.success(request, 'Senha alterada com sucesso!')
			else:
				messages.error(request, 'A senha deve ter pelo menos 8 caracteres')
			
		return redirect('account')

	return render(request, 'accounts/conta.html')

@login_required
def profiles(request):
	return render(request, 'accounts/perfis.html')

@login_required
def view_logout(request):
    logout(request)
    messages.success(request, 'Você saiu da sua conta.')
    return redirect('home')