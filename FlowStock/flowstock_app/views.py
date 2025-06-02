from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login
from .forms import SignUpForm, LoginForm
from django.contrib import messages

def register(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Conta criada para {username}!')
            return redirect('login')
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

def home(request):
    return render(request, 'flowstock/home.html')