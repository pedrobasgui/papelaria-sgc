from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from .models import Cliente

class ClienteSerializer(serializers.ModelSerializer):
    # Sobrescreve o campo CPF removendo o UniqueValidator automático.
    # A unicidade é garantida pelo ClienteService, que lança
    # CPFDuplicadoError -> 409 (mais semântico que o 400 do DRF).
    cpf = serializers.CharField(max_length=14, validators=[])
    email = serializers.EmailField(required=False, allow_null=True,
				   allow_blank=True)
    possui_vendas = serializers.SerializerMethodField()

    class Meta:
        model = Cliente
        fields = [
            "id", "nome", "cpf", "email", "telefone",
            "endereco", "criado_em", "atualizado_em",
            "possui_vendas",
        ]
        read_only_fields = ["id", "criado_em", "atualizado_em",
                            "possui_vendas"]

    def get_possui_vendas(self, obj):
        return obj.possui_vendas()

class ClienteResumoSerializer(serializers.ModelSerializer):
    """Versão reduzida usada em referências (vendas, relatórios)."""
    class Meta:
        model = Cliente
        fields = ["id", "nome", "cpf"]
