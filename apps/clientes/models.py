"""
Modelo Cliente.

Regras de negócio (definidas no enunciado):
- CPF não pode ser duplicado
- E-mail deve ser válido
- Cliente não pode ser removido se possuir vendas registradas
"""
import re
from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator
from django.db import models

def validar_cpf(cpf: str) -> bool:
    """Validação de CPF com dígitos verificadores."""
    cpf = re.sub(r"\D", "", cpf or "")
    if len(cpf) != 11 or cpf == cpf[0] * 11:
        return False
    for i in (9, 10):
        soma = sum(int(cpf[j]) * (i + 1 - j) for j in range(i))
        digito = (soma * 10 % 11) % 10
        if digito != int(cpf[i]):
            return False
    return True

class Cliente(models.Model):
    nome     = models.CharField("Nome", max_length=120)
    cpf      = models.CharField("CPF", max_length=14, unique=True)
    email    = models.EmailField("E-mail", validators=[EmailValidator()],
                                 blank=True, null=True)
    telefone = models.CharField("Telefone", max_length=20,
                                blank=True, null=True)
    endereco = models.CharField("Endereço", max_length=200,
                                blank=True, null=True)

    criado_em     = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "clientes"
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"
        ordering = ["nome"]
        indexes = [
            models.Index(fields=["cpf"]),
            models.Index(fields=["nome"]),
        ]

    def clean(self):
        # Normaliza o CPF (mantém formatado)
        if self.cpf:
            digits = re.sub(r"\D", "", self.cpf)
            if len(digits) == 11:
                self.cpf = (f"{digits[:3]}.{digits[3:6]}."
                            f"{digits[6:9]}-{digits[9:]}")
            if not validar_cpf(self.cpf):
                raise ValidationError({"cpf": "CPF inválido."})

    def possui_vendas(self) -> bool:
        return self.vendas.exists()

    def __str__(self):
        return f"{self.nome} ({self.cpf})"
