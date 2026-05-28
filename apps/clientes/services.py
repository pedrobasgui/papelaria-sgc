"""ClienteService - regras de negócio de cliente."""
from django.core.exceptions import ValidationError as DjangoValidationError

from apps.core.exceptions import (
    CPFDuplicadoError,
    CPFInvalidoError,
    EmailInvalidoError,
    EmailDuplicadoError,
    ClientePossuiVendasError,
)

from .repositories import ClienteRepository


def _traduzir_validation_error(e: DjangoValidationError):
    """Converte ValidationError do Django em DomainException."""
    erros = getattr(e, "message_dict", None) or {}
    if "cpf" in erros:
        raise CPFInvalidoError(detalhes={"cpf": erros["cpf"]})
    if "email" in erros:
        raise EmailInvalidoError(detalhes={"email": erros["email"]})
    msgs = getattr(e, "messages", None) or []
    if any("cpf" in str(m).lower() for m in msgs):
        raise CPFInvalidoError()
    raise


class ClienteService:

    def __init__(self, repo: ClienteRepository | None = None):
        self.repo = repo or ClienteRepository()

    def criar(self, dados: dict):
        if self.repo.cpf_existe(dados.get("cpf")):
            raise CPFDuplicadoError(detalhes={"cpf": dados.get("cpf")})
	email = dados.get("email")
	if email and self.repo.email_existe(email):
	    raise EmailDuplicadoError(detalhes={"email": email})
        try:
            return self.repo.criar(**dados)
        except DjangoValidationError as e:
            _traduzir_validation_error(e)

    def atualizar(self, cliente_id: int, dados: dict):
        cliente = self.repo.por_id(cliente_id)
        if not cliente:
            return None
        novo_cpf = dados.get("cpf")
        if novo_cpf and self.repo.cpf_existe(novo_cpf, excluir_id=cliente_id):
            raise CPFDuplicadoError(detalhes={"cpf": novo_cpf})
	email = dados.get("email")
	if email and self.repo.email_existe(email, excluir_id=cliente_id):
	    raise EmailDuplicadoError(detalhes={"email": email})
        try:
            return self.repo.atualizar(cliente, **dados)
        except DjangoValidationError as e:
            _traduzir_validation_error(e)

    def remover(self, cliente_id: int) -> bool:
        cliente = self.repo.por_id(cliente_id)
        if not cliente:
            return False
        if cliente.possui_vendas():
            raise ClientePossuiVendasError(
                detalhes={"cliente_id": cliente_id}
            )
        self.repo.remover(cliente)
        return True
