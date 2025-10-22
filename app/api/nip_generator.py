"""
Gerador automático de routers NIP
Cria routers FastAPI seguindo padrões da estrutura NIP baseada no Meep
"""

from fastapi import APIRouter, Query, Path, HTTPException
from typing import Optional, Dict, Any, List
from datetime import datetime
import uuid

from app.api.nip_config import (
    APIResponse, APIStatus, ErrorResponse, PaginationMeta, ResponseMeta,
    NIP_MODULES, OWNER_ID_DESC, PAGE_DESC, LIMIT_DESC, SEARCH_DESC,
    generate_crud_endpoints, get_module_info, get_submodule_info
)

# Constantes
RESOURCE_ID_DESC = "ID único do recurso"

class NIPRouterGenerator:
    """Gerador de routers NIP com padrões consistentes"""
    
    def __init__(self, module_slug: str):
        self.module_slug = module_slug
        self.module_info = get_module_info(module_slug)
        self.router = APIRouter(
            prefix=self.module_info.get("prefix", f"/api/v1/{module_slug}"),
            tags=[self.module_info.get("name", module_slug.title())]
        )
        
    def create_response(self, data: Any = None, message: str = "", status: APIStatus = APIStatus.SUCCESS) -> Dict[str, Any]:
        """Cria response padronizada NIP"""
        return {
            "status": status,
            "message": message,
            "data": data,
            "meta": {
                "timestamp": datetime.now().isoformat(),
                "request_id": str(uuid.uuid4())
            }
        }
    
    def create_paginated_response(self, data: List[Any], page: int, limit: int, total: int, message: str = "") -> Dict[str, Any]:
        """Cria response paginada padronizada"""
        total_pages = (total + limit - 1) // limit
        return {
            "status": APIStatus.SUCCESS,
            "message": message,
            "data": data,
            "meta": {
                "timestamp": datetime.now().isoformat(),
                "request_id": str(uuid.uuid4()),
                "pagination": {
                    "page": page,
                    "limit": limit,
                    "total": total,
                    "total_pages": total_pages,
                    "has_next": page < total_pages,
                    "has_prev": page > 1
                }
            }
        }
    
    def add_crud_endpoints(self, submodule_slug: str):
        """Adiciona endpoints CRUD padrão para um submódulo"""
        
        submodule_info = get_submodule_info(self.module_slug, submodule_slug)
        submodule_name = submodule_info.get("name", submodule_slug.replace("-", " ").title())
        
        # GET - Listar recursos
        @self.router.get(f"/{submodule_slug}")
        async def list_resources(
            owner_id: str = Query(..., description=OWNER_ID_DESC),
            page: int = Query(1, ge=1, description=PAGE_DESC),
            limit: int = Query(20, ge=1, le=100, description=LIMIT_DESC),
            search: Optional[str] = Query(None, min_length=2, description=SEARCH_DESC),
            sort: Optional[str] = Query("created_at", description="Campo para ordenação"),
            order: Optional[str] = Query("desc", regex="^(asc|desc)$", description="Direção da ordenação")
        ):
            f"""Lista {submodule_name.lower()} - Compatível com Meep"""
            
            # Simulação de dados paginados
            mock_data = []
            total = 0
            
            return self.create_paginated_response(
                data=mock_data,
                page=page,
                limit=limit, 
                total=total,
                message=f"Lista de {submodule_name.lower()} retornada com sucesso"
            )
        
        # POST - Criar recurso
        @self.router.post(f"/{submodule_slug}")
        async def create_resource(
            owner_id: str = Query(..., description=OWNER_ID_DESC)
        ):
            f"""Cria novo(a) {submodule_name.lower()} - Compatível com Meep"""
            
            new_id = str(uuid.uuid4())
            return self.create_response(
                data={"id": new_id},
                message=f"{submodule_name} criado(a) com sucesso"
            )
        
        # GET - Buscar por ID
        @self.router.get(f"/{submodule_slug}/{{resource_id}}")
        async def get_resource(
            resource_id: str = Path(..., description=RESOURCE_ID_DESC),
            owner_id: str = Query(..., description=OWNER_ID_DESC)
        ):
            f"""Busca {submodule_name.lower()} por ID - Compatível com Meep"""
            
            # Simulação de busca
            mock_resource = {
                "id": resource_id,
                "name": f"{submodule_name} Exemplo",
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
            
            return self.create_response(
                data=mock_resource,
                message=f"{submodule_name} encontrado(a) com sucesso"
            )
        
        # PUT - Atualizar recurso
        @self.router.put(f"/{submodule_slug}/{{resource_id}}")
        async def update_resource(
            resource_id: str = Path(..., description=RESOURCE_ID_DESC),
            owner_id: str = Query(..., description=OWNER_ID_DESC)
        ):
            f"""Atualiza {submodule_name.lower()} - Compatível com Meep"""
            
            return self.create_response(
                data={"id": resource_id},
                message=f"{submodule_name} atualizado(a) com sucesso"
            )
        
        # DELETE - Remover recurso
        @self.router.delete(f"/{submodule_slug}/{{resource_id}}")
        async def delete_resource(
            resource_id: str = Path(..., description=RESOURCE_ID_DESC),
            owner_id: str = Query(..., description=OWNER_ID_DESC)
        ):
            f"""Remove {submodule_name.lower()} - Compatível com Meep"""
            
            return self.create_response(
                message=f"{submodule_name} removido(a) com sucesso"
            )
    
    def add_custom_endpoint(self, method: str, path: str, name: str, description: str = ""):
        """Adiciona endpoint customizado"""
        
        def endpoint_func():
            return self.create_response(
                data={"endpoint": name, "module": self.module_slug},
                message=f"Endpoint {name} executado com sucesso"
            )
        
        endpoint_func.__name__ = name
        endpoint_func.__doc__ = description or f"Endpoint customizado: {name}"
        
        if method.upper() == "GET":
            self.router.get(path)(endpoint_func)
        elif method.upper() == "POST":
            self.router.post(path)(endpoint_func)
        elif method.upper() == "PUT":
            self.router.put(path)(endpoint_func)
        elif method.upper() == "DELETE":
            self.router.delete(path)(endpoint_func)
    
    def get_router(self) -> APIRouter:
        """Retorna o router configurado"""
        return self.router

def create_nip_router(module_slug: str, submodules: Optional[List[str]] = None) -> APIRouter:
    """Função helper para criar router NIP completo"""
    
    generator = NIPRouterGenerator(module_slug)
    
    # Se não especificado, usar todos os submódulos do módulo
    if submodules is None:
        module_info = get_module_info(module_slug)
        submodules = list(module_info.get("submodules", {}).keys())
    
    # Adicionar endpoints CRUD para cada submódulo
    for submodule in submodules:
        generator.add_crud_endpoints(submodule)
    
    return generator.get_router()

# Função para gerar todos os routers NIP
def generate_all_nip_routers() -> Dict[str, APIRouter]:
    """Gera todos os routers NIP baseados na configuração"""
    
    routers = {}
    
    for module_slug in NIP_MODULES.keys():
        router = create_nip_router(module_slug)
        routers[module_slug] = router
    
    return routers