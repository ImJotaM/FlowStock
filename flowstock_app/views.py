from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login as auth_login, update_session_auth_hash, logout
from .forms import SignUpForm, LoginForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Stock, Item
from django.contrib.auth.models import User

def root_redirect(request):
	if request.user.is_authenticated:
		return redirect('home')
	else:
		return redirect('login')

def register(request):
	if request.method == 'POST':
		form = SignUpForm(request.POST)
		if form.is_valid():
			user = form.save()
			username = form.cleaned_data.get('username')
			messages.success(request, f'Conta criada para {username}!')
			auth_login(request, user)
			return redirect('home')
	else:
		form = SignUpForm()
	return render(request, 'flowstock/register.html', {'form': form})

def login(request):
	if request.method == 'POST':
		form = LoginForm(request, data=request.POST)
		if form.is_valid():
			username = form.cleaned_data.get('username')
			password = form.cleaned_data.get('password')
			user = authenticate(request, username=username, password=password)
			if user is not None:
				auth_login(request, user)
				messages.success(request, f'Bem-vindo, {username}!')
				return redirect('home')
	else:
		form = LoginForm()
	return render(request, 'flowstock/login.html', {'form': form})

@login_required
def home(request):
	if request.method == 'POST':
		if 'create' in request.POST:
			count = Stock.objects.filter(user=request.user).count()
			Stock.objects.create(user=request.user, name=f"Estoque #{count + 1}")
		elif 'update_id' in request.POST:
			stock_id = request.POST.get('update_id')
			new_name = request.POST.get('new_name')
			stock = Stock.objects.filter(id=stock_id, user=request.user).first()
			if stock:
				stock.name = new_name
				stock.save()
		elif 'delete_id' in request.POST:
			stock_id = request.POST.get('delete_id')
			Stock.objects.filter(id=stock_id, user=request.user).delete()
            
		return redirect('home')
    
	stocks = Stock.objects.filter(user=request.user).order_by('name')
	return render(request, 'flowstock/home.html', {'stocks': stocks})

@login_required
def account_detail(request):
    
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
				return redirect('account_detail')

		field = request.POST.get('field')
		new_value = request.POST.get('new_value')
        
		if field == 'name':
			if new_value and len(new_value) > 0:
				request.user.username = new_value
				request.user.save()
				messages.success(request, 'Nome atualizado com sucesso!')
			else:
				messages.error(request, 'O nome não pode estar vazio')
				
		elif field == 'email':
			if new_value and len(new_value) > 0:
				request.user.email = new_value
				request.user.save()
				messages.success(request, 'E-mail atualizado com sucesso!')
			else:
				messages.error(request, 'O e-mail não pode estar vazio')
			
		elif field == 'password':
			if new_value and len(new_value) >= 8:
				request.user.set_password(new_value)
				request.user.save()
				update_session_auth_hash(request, request.user)
				messages.success(request, 'Senha alterada com sucesso!')
			else:
				messages.error(request, 'A senha deve ter pelo menos 8 caracteres')
			
		return redirect('account_detail')
  
	return render(request, 'flowstock/conta.html')

@login_required
def faqs(request):
	return render(request, 'flowstock/faqs.html')

@login_required
def profiles(request):
	return render(request, 'flowstock/perfis.html')

@login_required
def stock_detail(request, stock_id):
	stock = get_object_or_404(Stock, id=stock_id, user=request.user)
    
	if request.method == 'POST':
		if 'create' in request.POST:
			count = Item.objects.filter(stock=stock).count()
			Item.objects.create(stock=stock, name=f"Item #{count + 1}")
			return redirect('stock_detail', stock_id=stock.id)
		elif 'update_name' in request.POST:
			item_id = request.POST.get('update_name')
			Item.objects.filter(id=item_id, stock=stock).update()
			return redirect('stock_detail', stock_id=stock.id)
		elif 'delete_id' in request.POST:
			item_id = request.POST.get('delete_id')
			Item.objects.filter(id=item_id, stock=stock).delete()
			return redirect('stock_detail', stock_id=stock.id)
    
	return render(request, 'flowstock/estoque.html', {
        'stock': stock,
        'items': stock.items.all()
    })