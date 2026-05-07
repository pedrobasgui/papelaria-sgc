from decimal import Decimal
from rest_framework import serializers

from apps.clientes.serializers import ClienteResumoSerializer
from apps.produtos.serializers import ProdutoResumoSerializer
from apps.usuarios.serializers import UsuarioSerializer

from .models import Venda, ItemVenda

class ItemVendaSerializer(serializers.ModelSerializer):
    produto = ProdutoResumoSerializer(read_only=True)
    subtotal = serializers.SerializerMethodField()

    class Meta:
        model = ItemVenda
        fields = ["id", "produto", "quantidade",
                  "preco_unitario", "subtotal"]

    def get_subtotal(self, obj):
        return f"{obj.subtotal():.2f}"

class VendaSerializer(serializers.ModelSerializer):
    cliente = ClienteResumoSerializer(read_only=True)
    usuario = UsuarioSerializer(read_only=True)
    itens = ItemVendaSerializer(many=True, read_only=True)

    class Meta:
        model = Venda
        fields = [
            "id", "data", "cliente", "usuario", "valor_total",
            "status", "observacao", "itens",
        ]
        read_only_fields = fields

class ItemVendaInputSerializer(serializers.Serializer):
    produto_id = serializers.IntegerField(min_value=1)
    quantidade = serializers.IntegerField(min_value=1)
    preco_unitario = serializers.DecimalField(
        max_digits=10, decimal_places=2,
        required=False, min_value=Decimal("0.00")
    )

class VendaCreateSerializer(serializers.Serializer):
    cliente_id = serializers.IntegerField(min_value=1)
    observacao = serializers.CharField(required=False, allow_blank=True,
                                       allow_null=True)
    itens = ItemVendaInputSerializer(many=True)

    def validate_itens(self, value):
        if not value:
            raise serializers.ValidationError(
                "É necessário pelo menos um item na venda."
            )
        return value

class RelatorioPeriodoSerializer(serializers.Serializer):
    """Input para POST /api/vendas/por-periodo/"""
    data_inicio = serializers.DateField()
    data_fim = serializers.DateField()
