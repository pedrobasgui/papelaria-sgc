"""
Permissões customizadas baseadas no perfil do usuário.

Conforme o enunciado:
    ADMIN       - acesso total
    FUNCIONARIO - acesso restrito a vendas/clientes/consulta
"""
from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsAdmin(BasePermission):
    """Permite apenas usuários com perfil ADMIN."""
    message = "Apenas administradores podem realizar esta ação."

    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.perfil == "ADMIN"
        )

class IsAdminOrReadOnly(BasePermission):
    """ADMIN escreve, qualquer autenticado lê."""
    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        if request.method in SAFE_METHODS:
            return True
        return request.user.perfil == "ADMIN"

class IsAdminOrFuncionario(BasePermission):
    """Permite ADMIN ou FUNCIONARIO autenticado."""
    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.perfil in ("ADMIN", "FUNCIONARIO")
        )
