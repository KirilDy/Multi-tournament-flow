from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.contrib.auth.decorators import login_required
from accounts.models import User
from .forms import CustomUserCreationForm, UserProfileForm
import django.contrib.auth.decorators
import django.contrib.auth.mixins
import django.shortcuts
from django.views.generic import ListView
from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import redirect, render, get_object_or_404



class RegisterView(CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('login')  # Куди перенаправити після успішної реєстрації
    template_name = 'front/register.html'


@django.contrib.auth.decorators.login_required
def profile_view(request):
    return render(request, 'front/profile.html', {
        'profile_user': request.user
    })



@login_required
def edit_profile(request):
    if request.method == 'POST':
        # request.FILES потрібен для завантаження аватара
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Профіль успішно оновлено!")
            return redirect('/accounts/profile/') # Назва URL вашої сторінки профілю
    else:
        form = UserProfileForm(instance=request.user)
    
    return render(request, 'accounts/edit_profile.html', {'form': form})


@login_required
def main_page(request):
    # Використовуємо front/home.html (карточки турнірів). Якщо потрібно — можна додати контекст.
    return render(request, 'front/home.html')


