from rest_framework import serializers
from .models import Produto

class ProdutoSerializer(serializers.ModelSerializer):
    estoque_baixo = serializers.SerializerMethodField()

    class Meta:
        model = Produto
        fields = [
            "id", "nome", "descricao", "preco", "estoque",
            "estoque_minimo", "ativo", "estoque_baixo",
            "criado_em", "atualizado_em",
        ]
        read_only_fields = ["id", "criado_em", "atualizado_em",
                            "estoque_baixo"]

    def get_estoque_baixo(self, obj):
        return obj.alerta_estoque_baixo()

class ProdutoResumoSerializer(serializers.ModelSerializer):
    """Versão reduzida usada em itens de venda."""
    class Meta:
        model = Produto
        fields = ["id", "nome", "preco", "estoque"]
