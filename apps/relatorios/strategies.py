"""
Strategies (Strategy Pattern) para diferentes tipos de relatório.

Cada estratégia implementa a interface RelatorioStrategy e produz
um dicionário pronto para serialização em JSON.
"""
from abc import ABC, abstractmethod
from datetime import datetime, time
from decimal import Decimal

from django.db.models import Sum, Count

from apps.vendas.models import Venda, ItemVenda
from apps.vendas.repositories import VendaRepository

class RelatorioStrategy(ABC):
    @abstractmethod
    def gerar(self, **filtros) -> dict:
        ...

class VendasPorPeriodo(RelatorioStrategy):
    """RF-15: vendas em um intervalo de datas."""

    def __init__(self, repo: VendaRepository | None = None):
        self.repo = repo or VendaRepository()

    def gerar(self, **filtros) -> dict:
        ini = datetime.combine(filtros["data_inicio"], time.min)
        fim = datetime.combine(filtros["data_fim"],    time.max)
        vendas = list(self.repo.por_periodo(ini, fim))
        total = sum((v.valor_total for v in vendas), Decimal("0.00"))
        return {
            "tipo": "vendas_por_periodo",
            "periodo": {
                "inicio": filtros["data_inicio"],
                "fim":    filtros["data_fim"],
            },
            "quantidade_vendas": len(vendas),
            "valor_total": float(total),
            "ticket_medio": float(total / len(vendas)) if vendas else 0,
            "vendas": [
                {
                    "id": v.id,
                    "data": v.data,
                    "cliente": v.cliente.nome,
                    "vendedor": v.usuario.username,
                    "valor_total": float(v.valor_total),
                }
                for v in vendas
            ],
        }

class VendasPorCliente(RelatorioStrategy):
    """RF-16: histórico de compras de um cliente."""

    def __init__(self, repo: VendaRepository | None = None):
        self.repo = repo or VendaRepository()

    def gerar(self, **filtros) -> dict:
        cliente_id = filtros["cliente_id"]
        vendas = list(self.repo.por_cliente(cliente_id))
        total = sum((v.valor_total for v in vendas), Decimal("0.00"))
        return {
            "tipo": "vendas_por_cliente",
            "cliente_id": cliente_id,
            "quantidade_vendas": len(vendas),
            "valor_total": float(total),
            "vendas": [
                {
                    "id": v.id,
                    "data": v.data,
                    "valor_total": float(v.valor_total),
                    "qtd_itens": v.itens.count() if hasattr(v, "itens") else 0,
                }
                for v in vendas
            ],
        }

class VendasAnuaisGrafico(RelatorioStrategy):
    """
    RF-17: agregação mensal das vendas em um ano.
    Retorna 12 entradas (uma por mês) - meses sem vendas viram zero.
    """
    MESES = [
        "Jan", "Fev", "Mar", "Abr", "Mai", "Jun",
        "Jul", "Ago", "Set", "Out", "Nov", "Dez",
    ]

    def __init__(self, repo: VendaRepository | None = None):
        self.repo = repo or VendaRepository()

    def gerar(self, **filtros) -> dict:
        ano = int(filtros["ano"])
        agregado = self.repo.total_por_mes_no_ano(ano)

        # Map mês -> total
        por_mes = {row["mes"].month: row for row in agregado}

        labels = []
        valores = []
        quantidades = []
        for m in range(1, 13):
            labels.append(f"{self.MESES[m-1]}/{ano}")
            row = por_mes.get(m)
            if row:
                valores.append(float(row["total"] or 0))
                quantidades.append(int(row["qtd"]))
            else:
                valores.append(0.0)
                quantidades.append(0)

        return {
            "tipo": "vendas_anuais_grafico",
            "ano": ano,
            "labels": labels,
            "valores": valores,
            "quantidades": quantidades,
            "total_ano": sum(valores),
            "total_qtd_vendas": sum(quantidades),
        }

class ProdutosMaisVendidos(RelatorioStrategy):
    """Top N produtos por quantidade vendida."""

    def gerar(self, **filtros) -> dict:
        limite = int(filtros.get("limite", 10))
        qs = (
            ItemVenda.objects
            .filter(venda__status=Venda.Status.CONCLUIDA)
            .values("produto__id", "produto__nome")
            .annotate(qtd=Sum("quantidade"),
                      vendas=Count("venda", distinct=True))
            .order_by("-qtd")[:limite]
        )
        return {
            "tipo": "produtos_mais_vendidos",
            "limite": limite,
            "produtos": [
                {
                    "id": r["produto__id"],
                    "nome": r["produto__nome"],
                    "qtd_vendida": int(r["qtd"]),
                    "qtd_vendas": int(r["vendas"]),
                }
                for r in qs
            ],
        }

ESTRATEGIAS = {
    "periodo":  VendasPorPeriodo,
    "cliente":  VendasPorCliente,
    "anual":    VendasAnuaisGrafico,
    "top_produtos": ProdutosMaisVendidos,
}

def obter_estrategia(nome: str) -> RelatorioStrategy:
    classe = ESTRATEGIAS.get(nome)
    if not classe:
        raise ValueError(f"Estratégia '{nome}' não encontrada.")
    return classe()
