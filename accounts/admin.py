from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ("Додаткова інформація", {"fields": ("role", "bio")}),
    )
    list_display = ["username", "email", "role", "is_staff"]