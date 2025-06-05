from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login as auth_login
from .forms import SignUpForm, LoginForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Stock, Item

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
        
        elif 'delete_id' in request.POST:
            stock_id = request.POST.get('delete_id')
            Stock.objects.filter(id=stock_id, user=request.user).delete()
            
        return redirect('home')
    
    stocks = Stock.objects.filter(user=request.user).order_by('name')
    return render(request, 'flowstock/home.html', {'stocks': stocks})

@login_required
def account_detail(request):
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