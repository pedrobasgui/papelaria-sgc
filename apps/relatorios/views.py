"""
Views do app relatorios.

Endpoints:
    POST /api/relatorios/por-periodo/
    GET  /api/relatorios/por-cliente/{id}/
    GET  /api/relatorios/anual/?ano=YYYY
    GET  /api/relatorios/top-produtos/?limite=N
"""
from datetime import date, datetime
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.permissions import IsAdmin

from .strategies import (
    VendasPorPeriodo, VendasPorCliente,
    VendasAnuaisGrafico, ProdutosMaisVendidos,
)

# Pequeno serializer para input de período
class PeriodoSerializer(serializers.Serializer):
    data_inicio = serializers.DateField()
    data_fim = serializers.DateField()

class RelatorioPorPeriodoView(APIView):
    permission_classes = [IsAdmin]

    def post(self, request):
        s = PeriodoSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        if s.validated_data["data_fim"] < s.validated_data["data_inicio"]:
            return Response(
                {"erro": "Data final deve ser maior ou igual à data inicial.",
                 "codigo": "PERIODO_INVALIDO"},
                status=400
            )
        relatorio = VendasPorPeriodo().gerar(
            data_inicio=s.validated_data["data_inicio"],
            data_fim=s.validated_data["data_fim"],
        )
        return Response(relatorio)

class RelatorioPorClienteView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request, cliente_id):
        relatorio = VendasPorCliente().gerar(cliente_id=cliente_id)
        return Response(relatorio)

class RelatorioAnualView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        ano = request.query_params.get("ano", date.today().year)
        try:
            ano = int(ano)
        except (TypeError, ValueError):
            return Response(
                {"erro": "Ano inválido.", "codigo": "ANO_INVALIDO"},
                status=400
            )
        return Response(VendasAnuaisGrafico().gerar(ano=ano))

class TopProdutosView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        limite = request.query_params.get("limite", 10)
        try:
            limite = int(limite)
        except (TypeError, ValueError):
            limite = 10
        return Response(ProdutosMaisVendidos().gerar(limite=limite))
