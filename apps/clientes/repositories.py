"""
Repository de Cliente - encapsula consultas e persistência.

Padrão Repository: isola o ORM da camada de serviço, facilitando
testes (mock) e troca de tecnologia.
"""
from typing import Iterable, Optional
from django.db.models import QuerySet
from .models import Cliente

class ClienteRepository:

    @staticmethod
    def listar(busca: Optional[str] = None) -> QuerySet[Cliente]:
        qs = Cliente.objects.all()
        if busca:
            qs = qs.filter(nome__icontains=busca) | qs.filter(cpf__icontains=busca)
        return qs.order_by("nome")

    @staticmethod
    def por_id(cliente_id: int) -> Optional[Cliente]:
        return Cliente.objects.filter(pk=cliente_id).first()

    @staticmethod
    def por_cpf(cpf: str) -> Optional[Cliente]:
        return Cliente.objects.filter(cpf=cpf).first()

    @staticmethod
    def cpf_existe(cpf: str, excluir_id: Optional[int] = None) -> bool:
        qs = Cliente.objects.filter(cpf=cpf)
        if excluir_id:
            qs = qs.exclude(pk=excluir_id)
        return qs.exists()

    @staticmethod
    def email_existe(email: str, excluir_id: Optional[int] = None) -> bool:
        qs = Cliente.objects.filter(email=email)
        if excluir_id:
            qs = qs.exclude(pk=excluir_id)
        return qs.exists()

    @staticmethod
    def criar(**dados) -> Cliente:
        c = Cliente(**dados)
        c.full_clean()       # roda validações + validação de CPF
        c.save()
        return c

    @staticmethod
    def atualizar(cliente: Cliente, **dados) -> Cliente:
        for k, v in dados.items():
            setattr(cliente, k, v)
        cliente.full_clean()
        cliente.save()
        return cliente

    @staticmethod
    def remover(cliente: Cliente) -> None:
        cliente.delete()
