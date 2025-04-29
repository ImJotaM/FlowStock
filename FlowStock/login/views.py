from django.shortcuts import render
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.contrib import messages

# Create your views here.
def loginView(request):
	return render(request, 'modes/login.html')