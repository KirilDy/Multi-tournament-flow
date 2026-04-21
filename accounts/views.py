from django.urls import reverse_lazy
from django.views.generic import CreateView

from accounts.models import User
from .forms import CustomUserCreationForm
import django.contrib.auth.decorators
import django.contrib.auth.mixins
import django.shortcuts
from django.views.generic import ListView
from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import render, get_object_or_404



class RegisterView(CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('login')  # Куди перенаправити після успішної реєстрації
    template_name = 'accounts/register.html'

@django.contrib.auth.decorators.login_required
def profile_view(request):
    return render(request, 'accounts/profile.html', {
        'profile_user': request.user
    })


