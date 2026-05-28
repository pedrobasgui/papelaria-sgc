"""
Exceções customizadas do domínio.

Cada exceção herda de DomainException, que define o status HTTP e código
para padronização das respostas. Capturadas no handler global em handlers.py.
"""
from rest_framework import status

class DomainException(Exception):
    """Exceção base para erros de regra de negócio."""
    status_code = status.HTTP_400_BAD_REQUEST
    default_message = "Erro de domínio"
    error_code = "DOMAIN_ERROR"

    def __init__(self, message=None, **details):
        self.message = message or self.default_message
        self.details = details
        super().__init__(self.message)

class CPFInvalidoError(DomainException):
    default_message = "O CPF informado é inválido."
    error_code = "CPF_INVALIDO"


class CPFDuplicadoError(DomainException):
    status_code = status.HTTP_409_CONFLICT
    default_message = "Já existe um cliente com este CPF."
    error_code = "CPF_DUPLICADO"

class EmailInvalidoError(DomainException):
    default_message = "O e-mail informado não é válido."
    error_code = "EMAIL_INVALIDO"

class EmailDuplicadoError(DomainException):
    status_code = status.HTTP_409_CONFLICT
    default_message = "Já existe um cliente com este e-mail."
    error_code = "EMAIL_DUPLICADO"

class ClientePossuiVendasError(DomainException):
    status_code = status.HTTP_409_CONFLICT
    default_message = ("Cliente possui vendas registradas e "
                       "não pode ser removido.")
    error_code = "CLIENTE_COM_VENDAS"

class PrecoInvalidoError(DomainException):
    default_message = "Preço não pode ser negativo."
    error_code = "PRECO_INVALIDO"

class EstoqueInsuficienteError(DomainException):
    status_code = status.HTTP_409_CONFLICT
    default_message = "Estoque insuficiente para o produto."
    error_code = "ESTOQUE_INSUFICIENTE"

class VendaSemItensError(DomainException):
    default_message = "Não é possível registrar venda sem itens."
    error_code = "VENDA_SEM_ITENS"

class VendaJaCanceladaError(DomainException):
    status_code = status.HTTP_409_CONFLICT
    default_message = "Esta venda já está cancelada."
    error_code = "VENDA_JA_CANCELADA"

class PermissaoNegadaError(DomainException):
    status_code = status.HTTP_403_FORBIDDEN
    default_message = "Você não tem permissão para esta ação."
    error_code = "PERMISSAO_NEGADA"
