from django.contrib import messages
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required

from .forms import RegisterForm, LoginForm
from django.contrib.auth import authenticate, login, logout
import os


env = os.environ.get('PROJECT_ENV', 'dev')

def sign_up(request):
    form = RegisterForm()
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Success !')
            return redirect('/account/login')
    context = {
        'form': form
    }
    return render(request, 'accounts/register.html', context)


@login_required(login_url = '/account/login')
def log_out(request):
    logout(request)
    messages.success(request, 'You are logged out.')
    
    if env == "prod":
        return redirect(os.environ['AUTH_PATH'] + "login")
    elif env == "dev":
        return redirect('http://140.116.214.156:1984/account/login')
    else:
        raise EnvironmentError("Unknown environment! Please set the 'ENV' variable to 'production' or 'development'.")


@csrf_exempt
def sign_in(request):
    form = LoginForm()
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            # django login
            login(request, user)
            messages.success(request, 'You are now logged in.')
            
            if env == "prod":
                return redirect(os.environ['WEB_PATH'])
            elif env == "dev":
                return redirect('http://140.116.214.156:1985/correlation')
            else:
                raise EnvironmentError("Unknown environment! Please set the 'ENV' variable to 'production' or 'development'.")
            
        else:
            messages.warning(request, 'Invalid login credentials')
            return redirect('/account/login' )
    
    context = {
        'form': form
    }
    return render(request, 'accounts/login.html', context)


