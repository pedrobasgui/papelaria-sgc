from django.contrib import admin
from .models import Produto

@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = ("nome", "preco", "estoque", "estoque_minimo",
                    "ativo", "criado_em")
    list_filter = ("ativo", "criado_em")
    search_fields = ("nome", "descricao")
    list_editable = ("preco", "estoque", "ativo")
