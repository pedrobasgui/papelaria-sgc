"""Modelo de Usuario customizado com perfil de acesso."""
from django.contrib.auth.models import AbstractUser
from django.db import models
from .reset_token import PasswordResetToken

class Usuario(AbstractUser):

    class Perfil(models.TextChoices):
        ADMIN = "ADMIN",       "Administrador"
        FUNCIONARIO = "FUNCIONARIO", "Funcionário"

    perfil = models.CharField(
        max_length=20,
        choices=Perfil.choices,
        default=Perfil.FUNCIONARIO,
    )
    email = models.EmailField(unique=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    REQUIRED_FIELDS = ["email"]

    class Meta:
        db_table = "usuarios"
        verbose_name = "Usuário"
        verbose_name_plural = "Usuários"
        ordering = ["username"]

    @property
    def is_admin(self) -> bool:
        return self.perfil == self.Perfil.ADMIN

    @property
    def is_funcionario(self) -> bool:
        return self.perfil == self.Perfil.FUNCIONARIO

    def tem_permissao(self, acao: str) -> bool:
        if self.perfil == self.Perfil.ADMIN:
            return True
        permitidas_funcionario = {
            "vender", "consultar_venda",
            "consultar_cliente", "criar_cliente", "atualizar_cliente",
            "consultar_produto",
        }
        return acao in permitidas_funcionario

    def __str__(self):
        return f"{self.username} ({self.get_perfil_display()})"
