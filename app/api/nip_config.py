# Configuração da API NIP - Sistema Baseado em Meep
# Estrutura padronizada para todos os módulos

from typing import Dict, List, Any, Optional
from pydantic import BaseModel
from enum import Enum

# =============================================================================
# CONSTANTES GLOBAIS
# =============================================================================

# Status padrão para responses
class APIStatus(str, Enum):
    SUCCESS = "success"
    ERROR = "error"
    PENDING = "pending"

# Códigos de resposta padronizados
STATUS_MESSAGES = {
    "complete": "✅ Completo",
    "partial": "🔄 Parcial", 
    "pending": "⏳ Pendente",
    "error": "❌ Erro"
}

# Parâmetros comuns
OWNER_ID_DESC = "ID do proprietário/empresa"
PAGE_DESC = "Número da página (inicia em 1)"
LIMIT_DESC = "Quantidade de itens por página (máximo 100)"
SEARCH_DESC = "Termo para busca textual"
SORT_DESC = "Campo para ordenação"
ORDER_DESC = "Direção da ordenação (asc/desc)"

# =============================================================================
# SCHEMAS BASE PARA RESPOSTAS
# =============================================================================

class PaginationMeta(BaseModel):
    page: int = 1
    limit: int = 20
    total: int = 0
    total_pages: int = 0
    has_next: bool = False
    has_prev: bool = False

class ResponseMeta(BaseModel):
    timestamp: str
    request_id: str
    pagination: Optional[PaginationMeta] = None

class APIResponse(BaseModel):
    status: APIStatus
    message: str = ""
    data: Any = None
    meta: Optional[ResponseMeta] = None
    
class ErrorDetail(BaseModel):
    field: str
    message: str
    
class ErrorResponse(BaseModel):
    status: APIStatus = APIStatus.ERROR
    message: str
    error_code: str = ""
    details: List[ErrorDetail] = []
    meta: Optional[ResponseMeta] = None

# =============================================================================
# ESTRUTURA DE MÓDULOS NIP 
# =============================================================================

NIP_MODULES = {
    "dashboard": {
        "name": "Dashboard",
        "slug": "dashboard", 
        "prefix": "/api/v1/dashboard",
        "submodules": {
            "overview": {"name": "Visão Geral", "slug": "overview"}
        }
    },
    "financeiro": {
        "name": "Financeiro",
        "slug": "financeiro",
        "prefix": "/api/v1/financeiro", 
        "submodules": {
            "conta-digital": {"name": "Conta Digital", "slug": "conta-digital"},
            "extrato": {"name": "Extrato", "slug": "extrato"},
            "instituicoes-bancarias": {"name": "Instituições Bancárias", "slug": "instituicoes-bancarias"},
            "cartoes": {"name": "Cartões", "slug": "cartoes"}
        }
    },
    "pdv": {
        "name": "PDV",
        "slug": "pdv",
        "prefix": "/api/v1/pdv",
        "submodules": {
            "equipamentos": {"name": "Equipamentos", "slug": "equipamentos"},
            "sessoes": {"name": "Sessões", "slug": "sessoes"}, 
            "operadores": {"name": "Operadores", "slug": "operadores"},
            "perfis": {"name": "Perfis", "slug": "perfis"}
        }
    },
    "gestao-venda": {
        "name": "Gestão de Venda",
        "slug": "gestao-venda",
        "prefix": "/api/v1/gestao-venda",
        "submodules": {
            "vendas": {"name": "Vendas", "slug": "vendas"},
            "transacoes": {"name": "Transações", "slug": "transacoes"},
            "produtos": {"name": "Produtos", "slug": "produtos"}
        }
    },
    "estoque": {
        "name": "Estoque", 
        "slug": "estoque",
        "prefix": "/api/v1/estoque",
        "submodules": {
            "produtos": {"name": "Produtos", "slug": "produtos"},
            "movimentacoes": {"name": "Movimentações", "slug": "movimentacoes"},
            "inventario": {"name": "Inventário", "slug": "inventario"},
            "fornecedores": {"name": "Fornecedores", "slug": "fornecedores"}
        }
    },
    "marketing": {
        "name": "Marketing",
        "slug": "marketing", 
        "prefix": "/api/v1/marketing",
        "submodules": {
            "fidelidade": {"name": "Fidelidade", "slug": "fidelidade"},
            "crm": {"name": "CRM", "slug": "crm"},
            "desconto": {"name": "Desconto", "slug": "desconto"},
            "cupons": {"name": "Cupons de desconto", "slug": "cupons"},
            "campanhas": {"name": "Campanhas", "slug": "campanhas"},
            "promocao": {"name": "Promoção", "slug": "promocao"}
        }
    },
    "bi": {
        "name": "BI",
        "slug": "bi",
        "prefix": "/api/v1/bi", 
        "submodules": {
            "dashboard": {"name": "Dashboard BI", "slug": "dashboard"},
            "relatorios": {"name": "Relatórios", "slug": "relatorios"},
            "metricas": {"name": "Métricas", "slug": "metricas"}
        }
    },
    "sistema-erp": {
        "name": "Sistema ERP",
        "slug": "sistema-erp",
        "prefix": "/api/v1/sistema-erp",
        "submodules": {
            "modulos": {"name": "Módulos", "slug": "modulos"},
            "configuracoes": {"name": "Configurações", "slug": "configuracoes"},
            "integracao": {"name": "Integração", "slug": "integracao"}
        }
    },
    "automacao": {
        "name": "Automação", 
        "slug": "automacao",
        "prefix": "/api/v1/automacao",
        "submodules": {
            "workflows": {"name": "Workflows", "slug": "workflows"},
            "regras": {"name": "Regras", "slug": "regras"},
            "triggers": {"name": "Triggers", "slug": "triggers"}
        }
    },
    "integracao": {
        "name": "Integração",
        "slug": "integracao", 
        "prefix": "/api/v1/integracao",
        "submodules": {
            "apis": {"name": "APIs", "slug": "apis"},
            "webhooks": {"name": "Webhooks", "slug": "webhooks"},
            "conectores": {"name": "Conectores", "slug": "conectores"}
        }
    },
    "usuarios": {
        "name": "Usuários",
        "slug": "usuarios",
        "prefix": "/api/v1/usuarios", 
        "submodules": {
            "usuarios": {"name": "Usuários", "slug": "usuarios"},
            "perfis": {"name": "Perfis", "slug": "perfis"},
            "grupos": {"name": "Grupos", "slug": "grupos"},
            "permissoes": {"name": "Permissões", "slug": "permissoes"}
        }
    },
    "configuracoes": {
        "name": "Configurações",
        "slug": "configuracoes",
        "prefix": "/api/v1/configuracoes",
        "submodules": {
            "geral": {"name": "Geral", "slug": "geral"},
            "seguranca": {"name": "Segurança", "slug": "seguranca"},
            "notificacoes": {"name": "Notificações", "slug": "notificacoes"},
            "backup": {"name": "Backup", "slug": "backup"}
        }
    }
}

# =============================================================================
# HELPERS PARA GERAÇÃO DE ENDPOINTS
# =============================================================================

def generate_crud_endpoints(module_name: str, resource_name: str) -> Dict[str, str]:
    """Gera endpoints CRUD padrão para um recurso"""
    base_path = f"/api/v1/{module_name}/{resource_name}"
    return {
        "list": f"GET {base_path}",
        "create": f"POST {base_path}", 
        "get": f"GET {base_path}/{{id}}",
        "update": f"PUT {base_path}/{{id}}",
        "delete": f"DELETE {base_path}/{{id}}"
    }

def get_module_info(module_slug: str) -> Dict[str, Any]:
    """Retorna informações de um módulo pela slug"""
    return NIP_MODULES.get(module_slug, {})

def get_submodule_info(module_slug: str, submodule_slug: str) -> Dict[str, Any]:
    """Retorna informações de um submódulo"""
    module = NIP_MODULES.get(module_slug, {})
    return module.get("submodules", {}).get(submodule_slug, {})

# =============================================================================
# METADADOS DA API
# =============================================================================

API_METADATA = {
    "title": "Sistema NIP - API Completa",
    "description": """
    API completa do Sistema NIP baseada na análise do Portal Meep.
    Implementa todos os módulos e submódulos com padrões CRUD consistentes.
    
    **Características:**
    - JWT Bearer Authentication
    - Paginação padrão para listagens  
    - Envelope de resposta consistente
    - Códigos de erro padronizados
    - Suporte completo a operações CRUD
    
    **Módulos Implementados:**
    Dashboard, Financeiro, PDV, Gestão de Venda, Estoque, 
    Marketing, BI, Sistema ERP, Automação, Integração, 
    Usuários, Configurações
    """,
    "version": "1.0.0",
    "contact": {
        "name": "Sistema NIP",
        "email": "api@sistema-nip.com"
    },
    "license": {
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT"
    }
}

# =============================================================================
# MAPEAMENTO MEEP → NIP 
# =============================================================================

MEEP_TO_NIP_MAPPING = {
    # Financeiro
    "/app-prd-portal-v4-api/DigitalAccount": "/api/v1/financeiro/conta-digital",
    "/app-prd-portal-v4-api/Extract": "/api/v1/financeiro/extrato", 
    "/app-prd-portal-v4-api/BankingInstitutions": "/api/v1/financeiro/instituicoes-bancarias",
    
    # PDV
    "/app-prd-portal-v4-api/PdvEquipment": "/api/v1/pdv/equipamentos",
    "/app-prd-portal-v4-api/PdvSession": "/api/v1/pdv/sessoes",
    "/app-prd-portal-v4-api/PdvOperator": "/api/v1/pdv/operadores",
    
    # Marketing
    "/fidelity-api/api/Customers": "/api/v1/marketing/fidelidade",
    "/crm-api/api/Customers": "/api/v1/marketing/crm",
    "/crm-api/api/Campaigns": "/api/v1/marketing/campanhas",
    
    # Estoque
    "/app-prd-portal-v4-api/Stock": "/api/v1/estoque/produtos",
    "/app-prd-portal-v4-api/Product": "/api/v1/estoque/produtos"
}