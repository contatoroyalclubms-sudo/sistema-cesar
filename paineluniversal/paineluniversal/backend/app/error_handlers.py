"""
🛡️ SISTEMA DE TRATAMENTO DE ERROS - BACKEND
Handlers centralizados para exceções e erros
Última atualização: 05/01/2025
"""

from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from sqlalchemy.exc import SQLAlchemyError, IntegrityError, DataError
from pydantic import ValidationError
import logging
import traceback
from typing import Optional, Dict, Any, List
from datetime import datetime
import json

logger = logging.getLogger(__name__)

# ===== EXCEÇÕES CUSTOMIZADAS =====

class BusinessError(HTTPException):
    """Erro de regra de negócio"""
    def __init__(
        self,
        message: str,
        code: str = "BUSINESS_ERROR",
        status_code: int = status.HTTP_400_BAD_REQUEST,
        details: Optional[Dict[str, Any]] = None
    ):
        self.code = code
        self.details = details or {}
        super().__init__(
            status_code=status_code,
            detail={
                "error": message,
                "code": code,
                "details": details
            }
        )

class ValidationError(HTTPException):
    """Erro de validação de dados"""
    def __init__(
        self,
        field: str,
        message: str,
        code: str = "VALIDATION_ERROR"
    ):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "error": "Erro de validação",
                "code": code,
                "details": [
                    {
                        "field": field,
                        "message": message
                    }
                ]
            }
        )

class NotFoundError(HTTPException):
    """Recurso não encontrado"""
    def __init__(
        self,
        resource: str,
        identifier: Optional[Any] = None
    ):
        message = f"{resource} não encontrado"
        if identifier:
            message += f" (ID: {identifier})"
        
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": message,
                "code": "NOT_FOUND",
                "resource": resource,
                "identifier": identifier
            }
        )

class UnauthorizedError(HTTPException):
    """Erro de autenticação"""
    def __init__(
        self,
        message: str = "Não autorizado",
        code: str = "UNAUTHORIZED"
    ):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error": message,
                "code": code
            },
            headers={"WWW-Authenticate": "Bearer"}
        )

class ForbiddenError(HTTPException):
    """Erro de autorização/permissão"""
    def __init__(
        self,
        message: str = "Acesso negado",
        required_permission: Optional[str] = None
    ):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "error": message,
                "code": "FORBIDDEN",
                "required_permission": required_permission
            }
        )

class ConflictError(HTTPException):
    """Erro de conflito de dados"""
    def __init__(
        self,
        message: str,
        field: Optional[str] = None,
        existing_value: Optional[Any] = None
    ):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "error": message,
                "code": "CONFLICT",
                "field": field,
                "existing_value": existing_value
            }
        )

class RateLimitError(HTTPException):
    """Erro de limite de requisições"""
    def __init__(
        self,
        limit: int,
        window: str = "1 minuto",
        retry_after: Optional[int] = None
    ):
        headers = {}
        if retry_after:
            headers["Retry-After"] = str(retry_after)
        
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={
                "error": f"Limite de {limit} requisições por {window} excedido",
                "code": "RATE_LIMIT_EXCEEDED",
                "limit": limit,
                "window": window
            },
            headers=headers
        )

class ServiceUnavailableError(HTTPException):
    """Erro de serviço indisponível"""
    def __init__(
        self,
        service: str,
        message: Optional[str] = None
    ):
        error_message = f"Serviço '{service}' temporariamente indisponível"
        if message:
            error_message += f": {message}"
        
        super().__init__(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "error": error_message,
                "code": "SERVICE_UNAVAILABLE",
                "service": service
            }
        )

# ===== HANDLERS DE EXCEÇÃO =====

async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Handler para erros de validação do Pydantic"""
    
    errors = []
    for error in exc.errors():
        field = ".".join(str(loc) for loc in error["loc"][1:])  # Remove 'body' do path
        errors.append({
            "field": field or "unknown",
            "message": error["msg"],
            "type": error["type"]
        })
    
    # Log do erro
    logger.warning(
        f"Validation error on {request.method} {request.url.path}: {errors}",
        extra={
            "path": str(request.url.path),
            "method": request.method,
            "errors": errors
        }
    )
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "Erro de validação nos dados fornecidos",
            "code": "VALIDATION_ERROR",
            "details": errors,
            "timestamp": datetime.now().isoformat()
        }
    )

async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handler para exceções HTTP"""
    
    # Log do erro
    if exc.status_code >= 500:
        logger.error(
            f"HTTP {exc.status_code} on {request.method} {request.url.path}: {exc.detail}",
            extra={
                "path": str(request.url.path),
                "method": request.method,
                "status_code": exc.status_code
            }
        )
    else:
        logger.warning(
            f"HTTP {exc.status_code} on {request.method} {request.url.path}: {exc.detail}",
            extra={
                "path": str(request.url.path),
                "method": request.method,
                "status_code": exc.status_code
            }
        )
    
    # Formatar resposta
    if isinstance(exc.detail, dict):
        content = {
            **exc.detail,
            "timestamp": datetime.now().isoformat()
        }
    else:
        content = {
            "error": str(exc.detail),
            "code": "HTTP_ERROR",
            "status_code": exc.status_code,
            "timestamp": datetime.now().isoformat()
        }
    
    return JSONResponse(
        status_code=exc.status_code,
        content=content,
        headers=getattr(exc, "headers", None)
    )

async def database_exception_handler(request: Request, exc: SQLAlchemyError) -> JSONResponse:
    """Handler para erros do banco de dados"""
    
    # Log completo do erro
    logger.error(
        f"Database error on {request.method} {request.url.path}: {str(exc)}",
        exc_info=True,
        extra={
            "path": str(request.url.path),
            "method": request.method,
            "error_type": type(exc).__name__
        }
    )
    
    # Tratar tipos específicos de erro
    if isinstance(exc, IntegrityError):
        # Violação de constraint (unique, foreign key, etc)
        message = "Violação de integridade de dados"
        code = "INTEGRITY_ERROR"
        status_code = status.HTTP_409_CONFLICT
        
        # Tentar extrair informações específicas
        error_str = str(exc.orig) if hasattr(exc, 'orig') else str(exc)
        
        if "UNIQUE constraint failed" in error_str or "duplicate key" in error_str.lower():
            message = "Registro duplicado"
            code = "DUPLICATE_ENTRY"
        elif "FOREIGN KEY constraint failed" in error_str or "foreign key" in error_str.lower():
            message = "Referência inválida"
            code = "FOREIGN_KEY_ERROR"
        elif "NOT NULL constraint failed" in error_str or "null value" in error_str.lower():
            message = "Campo obrigatório não fornecido"
            code = "NULL_VALUE_ERROR"
    
    elif isinstance(exc, DataError):
        # Erro de tipo/formato de dados
        message = "Formato de dados inválido"
        code = "DATA_ERROR"
        status_code = status.HTTP_400_BAD_REQUEST
    
    else:
        # Erro genérico do banco
        message = "Erro ao processar operação no banco de dados"
        code = "DATABASE_ERROR"
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    
    return JSONResponse(
        status_code=status_code,
        content={
            "error": message,
            "code": code,
            "timestamp": datetime.now().isoformat()
        }
    )

async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handler para exceções não tratadas"""
    
    # Log completo do erro com stack trace
    logger.critical(
        f"Unhandled exception on {request.method} {request.url.path}: {str(exc)}",
        exc_info=True,
        extra={
            "path": str(request.url.path),
            "method": request.method,
            "error_type": type(exc).__name__,
            "traceback": traceback.format_exc()
        }
    )
    
    # Em produção, não expor detalhes do erro
    if os.getenv("ENV", "development") == "production":
        message = "Erro interno do servidor"
        details = None
    else:
        message = f"Erro interno: {str(exc)}"
        details = {
            "type": type(exc).__name__,
            "traceback": traceback.format_exc().split('\n')
        }
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": message,
            "code": "INTERNAL_SERVER_ERROR",
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
    )

# ===== MIDDLEWARE DE TRATAMENTO DE ERROS =====

class ErrorHandlingMiddleware:
    """Middleware para capturar e tratar erros globalmente"""
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        async def send_wrapper(message):
            # Interceptar respostas de erro
            if message["type"] == "http.response.start":
                status = message.get("status", 200)
                
                # Log de respostas de erro
                if status >= 400:
                    path = scope.get("path", "unknown")
                    method = scope.get("method", "unknown")
                    
                    if status >= 500:
                        logger.error(f"Error response {status} for {method} {path}")
                    else:
                        logger.warning(f"Error response {status} for {method} {path}")
            
            await send(message)
        
        try:
            await self.app(scope, receive, send_wrapper)
        except Exception as exc:
            # Capturar exceções não tratadas
            logger.critical(
                f"Unhandled exception in middleware: {str(exc)}",
                exc_info=True
            )
            
            # Enviar resposta de erro
            await send({
                "type": "http.response.start",
                "status": 500,
                "headers": [[b"content-type", b"application/json"]],
            })
            
            error_response = {
                "error": "Erro interno do servidor",
                "code": "INTERNAL_SERVER_ERROR",
                "timestamp": datetime.now().isoformat()
            }
            
            await send({
                "type": "http.response.body",
                "body": json.dumps(error_response).encode("utf-8"),
            })

# ===== FUNÇÕES AUXILIARES =====

def format_sqlalchemy_error(exc: SQLAlchemyError) -> Dict[str, Any]:
    """Formata erro do SQLAlchemy para resposta amigável"""
    
    error_str = str(exc.orig) if hasattr(exc, 'orig') else str(exc)
    
    # Tentar extrair tabela e campo do erro
    table = None
    field = None
    
    if "table" in error_str.lower():
        # Tentar extrair nome da tabela
        import re
        table_match = re.search(r'table\s+"?(\w+)"?', error_str, re.IGNORECASE)
        if table_match:
            table = table_match.group(1)
    
    if "column" in error_str.lower():
        # Tentar extrair nome da coluna
        import re
        column_match = re.search(r'column\s+"?(\w+)"?', error_str, re.IGNORECASE)
        if column_match:
            field = column_match.group(1)
    
    return {
        "table": table,
        "field": field,
        "original_error": error_str[:500]  # Limitar tamanho
    }

def log_error_context(request: Request, exc: Exception, additional_context: Optional[Dict] = None):
    """Registra contexto completo do erro para debugging"""
    
    context = {
        "timestamp": datetime.now().isoformat(),
        "request": {
            "method": request.method,
            "url": str(request.url),
            "path": request.url.path,
            "query_params": dict(request.query_params),
            "headers": dict(request.headers),
            "client": {
                "host": request.client.host if request.client else None,
                "port": request.client.port if request.client else None
            }
        },
        "error": {
            "type": type(exc).__name__,
            "message": str(exc),
            "traceback": traceback.format_exc()
        }
    }
    
    if additional_context:
        context.update(additional_context)
    
    logger.error(
        f"Error context for {request.method} {request.url.path}",
        extra={"error_context": context}
    )
    
    return context

# ===== REGISTRO DOS HANDLERS NO APP =====

def register_error_handlers(app):
    """Registra todos os handlers de erro no app FastAPI"""
    
    # Handlers de exceção
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(SQLAlchemyError, database_exception_handler)
    app.add_exception_handler(Exception, generic_exception_handler)
    
    # Middleware de tratamento de erros
    app.add_middleware(ErrorHandlingMiddleware)
    
    logger.info("Error handlers registered successfully")

# Importar para uso nos routers
import os

__all__ = [
    # Exceções customizadas
    'BusinessError',
    'ValidationError', 
    'NotFoundError',
    'UnauthorizedError',
    'ForbiddenError',
    'ConflictError',
    'RateLimitError',
    'ServiceUnavailableError',
    # Handlers
    'validation_exception_handler',
    'http_exception_handler',
    'database_exception_handler',
    'generic_exception_handler',
    # Middleware
    'ErrorHandlingMiddleware',
    # Funções auxiliares
    'format_sqlalchemy_error',
    'log_error_context',
    'register_error_handlers'
]