from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario
from .reset_token import PasswordResetToken

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

@admin.register(PasswordResetToken)
class PasswordResetTokenAdmin(admin.ModelAdmin):
    list_display = ("usuario", "criado_em", "expira_em", "usado")
    list_filter = ("usado",)
    readonly_fields = ("token_hash", "criado_em", "expira_em")
