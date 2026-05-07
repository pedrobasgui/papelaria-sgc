"""Repository de Venda."""
from datetime import datetime
from typing import Optional
from django.db.models import QuerySet, Sum, Count
from django.db.models.functions import TruncMonth, TruncDay
from .models import Venda, ItemVenda

class VendaRepository:

    @staticmethod
    def listar(filtros: dict | None = None) -> QuerySet[Venda]:
        qs = Venda.objects.select_related(
            "cliente", "usuario"
        ).prefetch_related("itens__produto").all()
        filtros = filtros or {}
        if c := filtros.get("cliente_id"):
            qs = qs.filter(cliente_id=c)
        if u := filtros.get("usuario_id"):
            qs = qs.filter(usuario_id=u)
        if s := filtros.get("status"):
            qs = qs.filter(status=s)
        if di := filtros.get("data_inicio"):
            qs = qs.filter(data__gte=di)
        if df := filtros.get("data_fim"):
            qs = qs.filter(data__lte=df)
        return qs.order_by("-data")

    @staticmethod
    def por_id(venda_id: int) -> Optional[Venda]:
        return Venda.objects.select_related(
            "cliente", "usuario"
        ).prefetch_related("itens__produto").filter(pk=venda_id).first()

    @staticmethod
    def por_periodo(inicio: datetime, fim: datetime) -> QuerySet[Venda]:
        return Venda.objects.filter(
            data__range=(inicio, fim),
            status=Venda.Status.CONCLUIDA,
        ).select_related("cliente", "usuario").order_by("-data")

    @staticmethod
    def por_cliente(cliente_id: int) -> QuerySet[Venda]:
        return Venda.objects.filter(
            cliente_id=cliente_id,
            status=Venda.Status.CONCLUIDA,
        ).select_related("usuario").order_by("-data")

    @staticmethod
    def total_por_mes_no_ano(ano: int) -> list[dict]:
        """Agrega valor_total por mês no ano informado."""
        qs = (
            Venda.objects
            .filter(data__year=ano, status=Venda.Status.CONCLUIDA)
            .annotate(mes=TruncMonth("data"))
            .values("mes")
            .annotate(total=Sum("valor_total"), qtd=Count("id"))
            .order_by("mes")
        )
        return list(qs)

    @staticmethod
    def total_por_dia_no_periodo(inicio: datetime,
                                 fim: datetime) -> list[dict]:
        qs = (
            Venda.objects
            .filter(data__range=(inicio, fim),
                    status=Venda.Status.CONCLUIDA)
            .annotate(dia=TruncDay("data"))
            .values("dia")
            .annotate(total=Sum("valor_total"), qtd=Count("id"))
            .order_by("dia")
        )
        return list(qs)
