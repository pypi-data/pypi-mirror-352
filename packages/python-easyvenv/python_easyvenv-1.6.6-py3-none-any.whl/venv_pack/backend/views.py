from django.contrib import messages
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt

from .forms import LoginForm, CreateUserForm, CreateProfileForm, UserUpdateForm, UserProfileUpdateForm, ReservationForm
from .models import CatalogItem, UserProfile, Reservation


def index(request):
    return render(request, 'index.html')


@login_required
def create_reservation(request):
    if request.method == 'POST':
        form = ReservationForm(request.POST)
        if form.is_valid():
            res = form.save(commit=False)
            res.user = request.user
            res.status = 'new'
            res.save()
            messages.success(request, 'Бронь успешно создана!')
            return redirect('reservations')
    else:
        form = ReservationForm()

    return render(request, 'create_reservation.html', {'form': form})


@login_required
def reservations(request):
    reservation_list = Reservation.objects.filter(user=request.user).order_by('-id')
    return render(request, 'reservations.html', {'reservations': reservation_list})


def catalog(request):
    catalog_list = CatalogItem.objects.all()

    paginator = Paginator(catalog_list, 3)
    page_number = request.GET.get('page')

    catalog_pag = paginator.get_page(page_number)

    sort_by = request.GET.get('sort', 'name')
    if sort_by == 'name':
        catalog_list = catalog_list.order_by('name')
    elif sort_by == 'price':
        catalog_list = catalog_list.order_by('price')
    else:
        catalog_list = catalog_list.order_by('-name')

    return render(request, 'catalog.html', {'catalog': catalog_pag})


def catalog_detail(request, id):
    product = get_object_or_404(CatalogItem, id=id)
    return render(request, 'catalog_detail.html', {'product': product})


@csrf_exempt
def user_login(request):
    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('index')
            else:
                messages.error(request, 'Неверное имя пользователя или пароль')
    else:
        form = LoginForm()

    context = {
        'form': form,
    }

    return render(request, 'login.html', context)


@csrf_exempt
def registration(request):
    if request.method == 'POST':
        user_form = CreateUserForm(request.POST)
        profile_form = CreateProfileForm(request.POST)

        if user_form.is_valid() and profile_form.is_valid():
            try:
                user = user_form.save()
                profile = profile_form.save(commit=False)
                profile.user = user
                profile.save()
                return redirect('login')
            except Exception as e:
                print(f"Error during registration: {str(e)}")
        else:
            print("User form errors:", user_form.errors)
            print("Profile form errors:", profile_form.errors)

    user_form = CreateUserForm()
    profile_form = CreateProfileForm()

    context = {
        'user_form': user_form,
        'profile_form': profile_form,
    }
    return render(request, 'registration.html', context)


def profile_page(request):
    user = User.objects.get(pk=request.user.id)
    user_profile = UserProfile.objects.get(user=user)

    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=user)
        profile_form = UserProfileUpdateForm(request.POST, request.FILES, instance=user_profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            return redirect('profile')
    else:
        user_form = UserUpdateForm(instance=user)
        profile_form = UserProfileUpdateForm(instance=user_profile)

    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'user': user,
        'user_profile': user_profile,
    }
    return render(request, 'profile.html', context)
