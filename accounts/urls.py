from django import views
from django.urls import path
from django.contrib.auth import views as auth_views
from .views import RegisterView
from .views import profile_view, edit_profile

urlpatterns = [
    # Використовуємо вбудовані класи для входу/виходу
    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    
    # Власний шлях для реєстрації
    path('register/', RegisterView.as_view(), name='register'),
    path('profile/', profile_view, name='profile'),
    path('profile/edit/', edit_profile,  name='edit_profile'),
]