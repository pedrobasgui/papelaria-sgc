from django.contrib import admin
from .models import Venda, ItemVenda

class ItemVendaInline(admin.TabularInline):
    model = ItemVenda
    extra = 0
    readonly_fields = ("produto", "quantidade", "preco_unitario")

@admin.register(Venda)
class VendaAdmin(admin.ModelAdmin):
    list_display = ("id", "data", "cliente", "usuario",
                    "valor_total", "status")
    list_filter = ("status", "data")
    search_fields = ("cliente__nome", "cliente__cpf", "usuario__username")
    inlines = [ItemVendaInline]
    readonly_fields = ("data", "valor_total")
