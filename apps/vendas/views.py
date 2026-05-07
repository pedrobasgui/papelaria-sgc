"""
Views do app vendas.

Endpoints:
    GET    /api/vendas/                  - lista
    GET    /api/vendas/{id}/             - detalhe
    POST   /api/vendas/                  - cria nova venda
    POST   /api/vendas/{id}/cancelar/    - cancela e devolve estoque
    POST   /api/vendas/por-periodo/      - filtro por período
    GET    /api/vendas/por-cliente/{id}/ - vendas de um cliente
"""
from datetime import datetime, time

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.permissions import IsAdminOrFuncionario, IsAdmin

from .models import Venda
from .serializers import (
    VendaSerializer, VendaCreateSerializer, RelatorioPeriodoSerializer,
)
from .services import VendaService

class VendaViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Apenas leitura via ModelViewSet padrão. Criação/cancelamento
    usam endpoints específicos para clareza.
    """
    serializer_class = VendaSerializer
    permission_classes = [IsAdminOrFuncionario]
    service = VendaService()

    def get_queryset(self):
        filtros = {
            "cliente_id": self.request.query_params.get("cliente_id"),
            "usuario_id": self.request.query_params.get("usuario_id"),
            "status": self.request.query_params.get("status"),
            "data_inicio": self.request.query_params.get("data_inicio"),
            "data_fim": self.request.query_params.get("data_fim"),
        }
        filtros = {k: v for k, v in filtros.items() if v}
        return self.service.listar(filtros)

    def create(self, request):
        """POST /api/vendas/ - cria venda."""
        serializer = VendaCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        dados = serializer.validated_data
        venda = self.service.criar_venda(
            cliente_id=dados["cliente_id"],
            usuario=request.user,
            itens=dados["itens"],
            observacao=dados.get("observacao"),
        )
        return Response(
            VendaSerializer(venda).data,
            status=status.HTTP_201_CREATED,
        )

    @action(detail=True, methods=["post"], url_path="cancelar")
    def cancelar(self, request, pk=None):
        """POST /api/vendas/{id}/cancelar/"""
        venda = self.service.cancelar_venda(pk)
        if not venda:
            return Response(
                {"erro": "Venda não encontrada.",
                 "codigo": "VENDA_NAO_ENCONTRADA"},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(VendaSerializer(venda).data)

    @action(detail=False, methods=["post"], url_path="por-periodo")
    def por_periodo(self, request):
        """POST /api/vendas/por-periodo/"""
        serializer = RelatorioPeriodoSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        ini = datetime.combine(
            serializer.validated_data["data_inicio"], time.min
        )
        fim = datetime.combine(
            serializer.validated_data["data_fim"], time.max
        )
        vendas = self.service.listar({"data_inicio": ini, "data_fim": fim})
        total = sum((v.valor_total for v in vendas), 0)
        return Response({
            "periodo": {
                "inicio": serializer.validated_data["data_inicio"],
                "fim":    serializer.validated_data["data_fim"],
            },
            "quantidade": len(vendas),
            "total": float(total),
            "vendas": VendaSerializer(vendas, many=True).data,
        })

    @action(detail=False, methods=["get"], url_path=r"por-cliente/(?P<cliente_id>\d+)")
    def por_cliente(self, request, cliente_id=None):
        """GET /api/vendas/por-cliente/{id}/"""
        vendas = self.service.listar({"cliente_id": cliente_id})
        return Response(VendaSerializer(vendas, many=True).data)
