"""
Middleware para conversão automática entre snake_case e camelCase
"""
from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import json
import re
from typing import Any, Dict

def snake_to_camel(snake_str: str) -> str:
    """Converter snake_case para camelCase"""
    components = snake_str.split('_')
    return components[0] + ''.join(x.title() for x in components[1:])

def camel_to_snake(camel_str: str) -> str:
    """Converter camelCase para snake_case"""
    pattern = re.compile(r'(?<!^)(?=[A-Z])')
    return pattern.sub('_', camel_str).lower()

def convert_dict_keys(data: Any, converter_func) -> Any:
    """Converter chaves de dicionário recursivamente"""
    if isinstance(data, dict):
        return {
            converter_func(key): convert_dict_keys(value, converter_func)
            for key, value in data.items()
        }
    elif isinstance(data, list):
        return [convert_dict_keys(item, converter_func) for item in data]
    else:
        return data

class CaseConverterMiddleware(BaseHTTPMiddleware):
    """
    Middleware que converte automaticamente entre snake_case (backend) e camelCase (frontend)
    """
    
    def __init__(self, app, enabled: bool = True, exclude_paths: list = None):
        super().__init__(app)
        self.enabled = enabled
        self.exclude_paths = exclude_paths or ["/docs", "/redoc", "/openapi.json", "/healthz"]
    
    async def dispatch(self, request: Request, call_next):
        # Verificar se deve processar este caminho
        path = request.url.path
        if not self.enabled or any(path.startswith(p) for p in self.exclude_paths):
            return await call_next(request)
        
        # Converter request body de camelCase para snake_case
        if request.method in ["POST", "PUT", "PATCH"]:
            try:
                # Ler body original
                body = await request.body()
                if body:
                    # Converter para dict
                    data = json.loads(body)
                    # Converter chaves para snake_case
                    converted_data = convert_dict_keys(data, camel_to_snake)
                    # Reconstruir request com dados convertidos
                    request._body = json.dumps(converted_data).encode()
                    
                    # Atualizar headers se necessário
                    if "content-length" in request.headers:
                        request.headers.__dict__["_list"] = [
                            (k.encode(), v.encode()) if k != b"content-length" 
                            else (k, str(len(request._body)).encode())
                            for k, v in request.headers.raw
                        ]
            except (json.JSONDecodeError, UnicodeDecodeError):
                # Se não for JSON válido, deixar passar
                pass
        
        # Processar request
        response = await call_next(request)
        
        # Converter response body de snake_case para camelCase
        if response.status_code < 400:  # Apenas respostas bem-sucedidas
            # Capturar body da resposta
            response_body = b""
            async for chunk in response.body_iterator:
                response_body += chunk
            
            try:
                # Tentar decodificar como JSON
                data = json.loads(response_body)
                # Converter chaves para camelCase
                converted_data = convert_dict_keys(data, snake_to_camel)
                # Criar nova resposta com dados convertidos
                return JSONResponse(
                    content=converted_data,
                    status_code=response.status_code,
                    headers=dict(response.headers)
                )
            except (json.JSONDecodeError, UnicodeDecodeError):
                # Se não for JSON, retornar resposta original
                return Response(
                    content=response_body,
                    status_code=response.status_code,
                    headers=dict(response.headers),
                    media_type=response.media_type
                )
        
        return response

# Função helper para aplicar middleware condicionalmente
def apply_case_converter(app, enable_for_routes: list = None):
    """
    Aplicar o middleware de conversão de case apenas para rotas específicas
    
    Args:
        app: Instância FastAPI
        enable_for_routes: Lista de prefixos de rota para habilitar conversão
    """
    if enable_for_routes is None:
        # Por padrão, habilitar para todas as rotas de API
        enable_for_routes = ["/api/"]
    
    # Criar lista de exclusão baseada em rotas não habilitadas
    exclude_paths = []
    
    # Adicionar rotas técnicas que nunca devem ser convertidas
    exclude_paths.extend([
        "/docs",
        "/redoc", 
        "/openapi.json",
        "/healthz",
        "/api/health",
        "/api/cors-test",
        "/setup-inicial",
        "/uploads",  # Arquivos estáticos
        "/api/ws",   # WebSockets
    ])
    
    return CaseConverterMiddleware(
        app,
        enabled=True,
        exclude_paths=exclude_paths
    )