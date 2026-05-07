"""
Modelo Produto.

Regras de negócio (enunciado):
- Preço não pode ser negativo
- Estoque mínimo deve ser controlado
- Não permitir venda se estoque insuficiente (validado no service de vendas)
"""
from decimal import Decimal
from django.core.validators import MinValueValidator
from django.db import models

class Produto(models.Model):
    nome = models.CharField("Nome", max_length=120)
    descricao = models.TextField("Descrição", blank=True, null=True)
    preco = models.DecimalField(
        "Preço", max_digits=10, decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))]
    )
    estoque = models.PositiveIntegerField("Estoque", default=0)
    estoque_minimo = models.PositiveIntegerField(
        "Estoque mínimo", default=5,
        help_text="Abaixo deste valor, o produto é sinalizado como crítico."
    )
    ativo = models.BooleanField("Ativo", default=True)

    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "produtos"
        verbose_name = "Produto"
        verbose_name_plural = "Produtos"
        ordering = ["nome"]
        indexes = [
            models.Index(fields=["nome"]),
            models.Index(fields=["ativo"]),
        ]

    def tem_estoque(self, quantidade: int) -> bool:
        return self.estoque >= quantidade

    def alerta_estoque_baixo(self) -> bool:
        return self.estoque <= self.estoque_minimo

    def debitar_estoque(self, quantidade: int):
        """Reduz o estoque, lançando erro se insuficiente."""
        from apps.core.exceptions import EstoqueInsuficienteError
        if quantidade <= 0:
            raise ValueError("Quantidade deve ser positiva.")
        if not self.tem_estoque(quantidade):
            raise EstoqueInsuficienteError(
                detalhes={
                    "produto_id": self.id,
                    "produto": self.nome,
                    "estoque_atual": self.estoque,
                    "solicitado": quantidade,
                }
            )
        self.estoque -= quantidade
        self.save(update_fields=["estoque", "atualizado_em"])

    def creditar_estoque(self, quantidade: int):
        """Repõe o estoque (usado em cancelamento de vendas)."""
        if quantidade <= 0:
            raise ValueError("Quantidade deve ser positiva.")
        self.estoque += quantidade
        self.save(update_fields=["estoque", "atualizado_em"])

    def __str__(self):
        return f"{self.nome} (R$ {self.preco})"
