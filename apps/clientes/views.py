"""
ViewSet de Cliente.

Endpoints (auto-gerados pelo router):
    GET    /api/clientes/        - lista
    POST   /api/clientes/        - cria
    GET    /api/clientes/{id}/   - detalhe
    PUT    /api/clientes/{id}/   - atualiza
    PATCH  /api/clientes/{id}/   - atualização parcial
    DELETE /api/clientes/{id}/   - remove (bloqueado se houver vendas)
"""
from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.decorators import action

from apps.core.permissions import IsAdminOrFuncionario

from .models import Cliente
from .serializers import ClienteSerializer
from .services import ClienteService
from .repositories import ClienteRepository

class ClienteViewSet(viewsets.ModelViewSet):
    serializer_class = ClienteSerializer
    permission_classes = [IsAdminOrFuncionario]
    service = ClienteService()
    repo = ClienteRepository()

    def get_queryset(self):
        busca = self.request.query_params.get("busca")
        return self.repo.listar(busca=busca)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        cliente = self.service.criar(serializer.validated_data)
        return Response(
            self.get_serializer(cliente).data,
            status=status.HTTP_201_CREATED,
        )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(
            instance, data=request.data, partial=partial
        )
        serializer.is_valid(raise_exception=True)
        cliente = self.service.atualizar(
            instance.id, serializer.validated_data
        )
        return Response(self.get_serializer(cliente).data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.service.remover(instance.id)
        return Response(
            {"mensagem": "Cliente removido com sucesso."},
            status=status.HTTP_200_OK,
        )
