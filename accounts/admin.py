# accounts/admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser
from .forms import  UserCreationForm


@admin.register(CustomUser)

class CustomUserAdmin(UserAdmin):
    # Make sure these are lists, not single strings
    list_display = ['email', 'full_name', 'user_type', 'is_active', 'date_joined']
    list_filter = ['user_type', 'is_active', 'date_joined']
    search_fields = ['email', 'full_name']  # This must be a list/tuple
    ordering = ['email']
    
    # Override the fieldsets from UserAdmin
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('full_name', 'user_type')}),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    # For adding new users through admin
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'full_name', 'user_type', 'password1', 'password2'),
        }),
    )
    
    # Since we're using email as username
    readonly_fields = ('date_joined', 'last_login')

# Alternative: If you want to keep it simple, use this minimal version
class SimpleCustomUserAdmin(UserAdmin):
    list_display = ('email', 'full_name', 'user_type', 'is_active')
    search_fields = ('email', 'full_name')
    list_filter = ('user_type', 'is_active')
    ordering = ('email',)

