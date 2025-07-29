from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from .forms import RegisterForm, LoginForm, ApplicationForm
from .models import Naprav

def naprav_detail(request, pk):
    naprav = get_object_or_404(Naprav, pk=pk)

    if request.method == 'POST':
        form = ApplicationForm(request.POST)
        if form.is_valid() and request.user.is_authenticated:
            application = form.save(commit=False)
            application.user = request.user
            application.direction = naprav
            application.save()
            return redirect('profile')
    else:
        form = ApplicationForm()

    return render(request, 'naprav_detail.html', {
        'naprav': naprav,
        'form': form,
    })

def documents(request):
    return render(request, 'documents.html')

def index(request):
    return render(request, 'index.html')

def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('profile')
    else:
        form = RegisterForm()

    return render(request, 'register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('profile')
    else:
        form = LoginForm()

    return render(request, 'login.html', {'form': form})

@login_required
def profile_view(request):
    return render(request, 'profile.html', {'user': request.user})

def logout_view(request):
    logout(request)
    return redirect('login')

def catalog(request):
    naprav_list = Naprav.objects.all()
    return render(request, 'catalog.html', {'naprav_list': naprav_list})