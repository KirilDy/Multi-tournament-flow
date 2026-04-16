from django.urls import reverse_lazy
from django.views.generic import CreateView
from .forms import CustomUserCreationForm
import django.contrib.auth.decorators
import django.contrib.auth.mixins
import django.shortcuts
from django.views.generic import ListView
from django.contrib.auth.mixins import UserPassesTestMixin



class RegisterView(CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('login')  # Куди перенаправити після успішної реєстрації
    template_name = 'accounts/register.html'




