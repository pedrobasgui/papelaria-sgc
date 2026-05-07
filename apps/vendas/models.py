"""
Modelos Venda e ItemVenda.

Regras de negócio (enunciado):
- Valor total calculado automaticamente
- Atualizar estoque após venda
- Não permitir venda sem itens
"""
from decimal import Decimal
from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models

from apps.clientes.models import Cliente
from apps.produtos.models import Produto

class Venda(models.Model):

    class Status(models.TextChoices):
        CONCLUIDA = "CONCLUIDA", "Concluída"
        CANCELADA = "CANCELADA", "Cancelada"

    data = models.DateTimeField("Data", auto_now_add=True)
    cliente = models.ForeignKey(
        Cliente, on_delete=models.PROTECT,
        related_name="vendas", verbose_name="Cliente"
    )
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
        related_name="vendas_realizadas",
        verbose_name="Usuário responsável"
    )
    valor_total = models.DecimalField(
        "Valor total", max_digits=10, decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))]
    )
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.CONCLUIDA
    )
    observacao = models.TextField("Observação", blank=True, null=True)

    class Meta:
        db_table = "vendas"
        verbose_name = "Venda"
        verbose_name_plural = "Vendas"
        ordering = ["-data"]
        indexes = [
            models.Index(fields=["-data"]),
            models.Index(fields=["cliente"]),
            models.Index(fields=["status"]),
        ]

    def calcular_total(self) -> Decimal:
        """Soma os subtotais dos itens. Não persiste."""
        total = sum(
            (item.subtotal() for item in self.itens.all()),
            Decimal("0.00")
        )
        return total

    def recalcular_e_salvar(self):
        self.valor_total = self.calcular_total()
        self.save(update_fields=["valor_total"])

    @property
    def esta_cancelada(self) -> bool:
        return self.status == self.Status.CANCELADA

    def __str__(self):
        return f"Venda #{self.id} - {self.cliente.nome} - R$ {self.valor_total}"

class ItemVenda(models.Model):
    venda = models.ForeignKey(
        Venda, on_delete=models.CASCADE, related_name="itens"
    )
    produto = models.ForeignKey(
        Produto, on_delete=models.PROTECT, related_name="itens_venda"
    )
    quantidade = models.PositiveIntegerField("Quantidade")
    preco_unitario = models.DecimalField(
        "Preço unitário", max_digits=10, decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))]
    )

    class Meta:
        db_table = "itens_venda"
        verbose_name = "Item de venda"
        verbose_name_plural = "Itens de venda"
        indexes = [
            models.Index(fields=["venda"]),
            models.Index(fields=["produto"]),
        ]

    def subtotal(self) -> Decimal:
        return self.preco_unitario * Decimal(self.quantidade)

    def __str__(self):
        return f"{self.quantidade}x {self.produto.nome}"
