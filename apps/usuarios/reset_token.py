import secrets
import hashlib
from datetime import timedelta
from django.db import models
from django.utils import timezone
from django.conf import settings


class PasswordResetToken(models.Model):
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reset_tokens",
    )
    token_hash = models.CharField(max_length=64, unique=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    expira_em = models.DateTimeField()
    usado = models.BooleanField(default=False)

    class Meta:
        db_table = "password_reset_tokens"
        verbose_name = "Token de recuperação de senha"

    @classmethod
    def criar_para(cls, usuario):
        """Gera token seguro, invalida anteriores e salva."""
        cls.objects.filter(usuario=usuario, usado=False).delete()
        token_raw = secrets.token_urlsafe(32)
        token_hash = hashlib.sha256(token_raw.encode()).hexdigest()
        obj = cls.objects.create(
            usuario=usuario,
            token_hash=token_hash,
            expira_em=timezone.now() + timedelta(hours=1),
        )
        return token_raw, obj

    def is_valido(self):
        return not self.usado and timezone.now() < self.expira_em

    def marcar_usado(self):
        self.usado = True
        self.save(update_fields=["usado"])

    def __str__(self):
        return f"Token de {self.usuario.username} ({self.expira_em})"

from .reset_token import PasswordResetToken
