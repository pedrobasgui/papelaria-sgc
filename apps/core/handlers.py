"""
Handler global de exceções para o DRF.

Captura DomainException (regras de negócio) e converte em respostas
JSON padronizadas. Mantém o handler default do DRF para os outros casos.
"""
import logging
from rest_framework.views import exception_handler
from rest_framework.response import Response

from .exceptions import DomainException

logger = logging.getLogger(__name__)

def custom_exception_handler(exc, context):
    """
    Padroniza o formato de resposta de erros.

    Formato:
        {
            "erro": "MENSAGEM_PARA_USUARIO",
            "codigo": "CODIGO_INTERNO",
            "detalhes": { ... }
        }
    """
    # Tratamento de DomainException
    if isinstance(exc, DomainException):
        logger.warning("DomainException: %s", exc.message)
        return Response(
            {
                "erro": exc.message,
                "codigo": exc.error_code,
                "detalhes": exc.details or {},
            },
            status=exc.status_code,
        )

    # Delega para o handler padrão do DRF (validação, auth, etc)
    response = exception_handler(exc, context)

    if response is not None:
        # Padroniza erros do DRF
        data = response.data
        if isinstance(data, dict) and "detail" in data:
            response.data = {
                "erro": str(data["detail"]),
                "codigo": getattr(exc, "default_code", "ERROR").upper(),
                "detalhes": {},
            }
        elif isinstance(data, dict):
            response.data = {
                "erro": "Erro de validação",
                "codigo": "VALIDATION_ERROR",
                "detalhes": data,
            }
        return response

    # Erro não tratado - log e 500
    logger.exception("Erro não tratado: %s", exc)
    return Response(
        {
            "erro": "Ocorreu um erro interno no servidor.",
            "codigo": "INTERNAL_ERROR",
            "detalhes": {},
        },
        status=500,
    )
