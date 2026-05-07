"""ViewSet de Produto."""
from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.decorators import action

from apps.core.permissions import IsAdminOrReadOnly

from .models import Produto
from .serializers import ProdutoSerializer
from .services import ProdutoService
from .repositories import ProdutoRepository

class ProdutoViewSet(viewsets.ModelViewSet):
    serializer_class = ProdutoSerializer
    permission_classes = [IsAdminOrReadOnly]
    service = ProdutoService()
    repo = ProdutoRepository()

    def get_queryset(self):
        busca = self.request.query_params.get("busca")
        apenas_ativos = self.request.query_params.get("ativos") == "true"
        return self.repo.listar(busca=busca, apenas_ativos=apenas_ativos)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        produto = self.service.criar(serializer.validated_data)
        return Response(
            self.get_serializer(produto).data,
            status=status.HTTP_201_CREATED,
        )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(
            instance, data=request.data, partial=partial
        )
        serializer.is_valid(raise_exception=True)
        produto = self.service.atualizar(
            instance.id, serializer.validated_data
        )
        return Response(self.get_serializer(produto).data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.service.remover(instance.id)
        return Response(
            {"mensagem": "Produto removido (ou inativado se possuir vendas)."},
            status=status.HTTP_200_OK,
        )

    @action(detail=False, methods=["get"], url_path="estoque-baixo")
    def estoque_baixo(self, request):
        """GET /api/produtos/estoque-baixo/"""
        produtos = self.service.estoque_baixo()
        return Response(self.get_serializer(produtos, many=True).data)
