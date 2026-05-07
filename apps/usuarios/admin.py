from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario

@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    list_display = ("username", "email", "perfil", "is_active", "criado_em")
    list_filter = ("perfil", "is_active")
    search_fields = ("username", "email", "first_name", "last_name")

    fieldsets = UserAdmin.fieldsets + (
        ("Perfil do Sistema", {"fields": ("perfil",)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Perfil do Sistema", {"fields": ("perfil", "email")}),
    )
