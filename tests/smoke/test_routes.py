"""
Smoke Tests - Sistema NIP API
Testa existência de rotas principais e padrões de segurança.
"""

import pytest
import httpx
import asyncio
from typing import Dict, List
import os

# Configurações de teste
BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
TEST_TOKEN = os.getenv("TEST_TOKEN", "test-token-placeholder")

class TestSystemEndpoints:
    """Testa endpoints do sistema"""
    
    @pytest.mark.asyncio
    async def test_health_endpoint(self):
        """Health check deve estar acessível e público"""
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BASE_URL}/health")
            assert response.status_code == 200
            data = response.json()
            assert "status" in data
            assert data["status"] == "healthy"

class TestAuthenticationEndpoints:
    """Testa endpoints de autenticação"""
    
    @pytest.mark.asyncio
    async def test_login_endpoint_exists(self):
        """Endpoint de login deve existir como POST"""
        async with httpx.AsyncClient() as client:
            # Tenta POST (correto)
            response = await client.post(
                f"{BASE_URL}/api/auth/login",
                json={"email": "test@test.com", "senha": "test"}
            )
            # Aceita 200, 401 ou 422 (não 404 ou 405)
            assert response.status_code in [200, 401, 422]
            
    @pytest.mark.asyncio
    async def test_login_method_not_get(self):
        """Login não deve aceitar GET"""
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BASE_URL}/api/auth/login")
            # Deve retornar 405 (Method Not Allowed) ou 404
            assert response.status_code in [404, 405]

class TestSecurityPatterns:
    """Testa padrões de segurança"""
    
    @pytest.mark.asyncio
    async def test_protected_endpoints_require_auth(self):
        """Endpoints protegidos devem exigir autenticação"""
        protected_endpoints = [
            "/api/dashboard",
            "/api/empresas",
            "/api/financeiro/transacoes",
            "/api/marketing/campanhas"
        ]
        
        async with httpx.AsyncClient() as client:
            for endpoint in protected_endpoints:
                response = await client.get(f"{BASE_URL}{endpoint}")
                # Deve retornar 401 (Unauthorized) sem token
                assert response.status_code in [401, 403], f"Endpoint {endpoint} não está protegido"
    
    @pytest.mark.asyncio
    async def test_bearer_token_acceptance(self):
        """Endpoints devem aceitar Bearer token"""
        if TEST_TOKEN == "test-token-placeholder":
            pytest.skip("Token de teste não configurado")
            
        headers = {"Authorization": f"Bearer {TEST_TOKEN}"}
        
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BASE_URL}/api/dashboard", headers=headers)
            # Com token válido, não deve ser 401/403
            assert response.status_code not in [401, 403]

class TestRESTPatterns:
    """Testa padrões REST"""
    
    @pytest.mark.asyncio
    async def test_rest_endpoints_exist(self):
        """Endpoints REST principais devem existir"""
        rest_endpoints = [
            ("GET", "/api/empresas"),
            ("POST", "/api/empresas"),
            ("GET", "/api/financeiro/transacoes"),
            ("POST", "/api/financeiro/transacoes"),
            ("GET", "/api/marketing/campanhas"),
            ("POST", "/api/marketing/campanhas")
        ]
        
        headers = {"Authorization": f"Bearer {TEST_TOKEN}"} if TEST_TOKEN != "test-token-placeholder" else {}
        
        async with httpx.AsyncClient() as client:
            for method, endpoint in rest_endpoints:
                if method == "GET":
                    response = await client.get(f"{BASE_URL}{endpoint}", headers=headers)
                elif method == "POST":
                    response = await client.post(
                        f"{BASE_URL}{endpoint}", 
                        json={}, 
                        headers=headers
                    )
                
                # Não deve ser 404 (Not Found) - endpoint existe
                assert response.status_code != 404, f"{method} {endpoint} não encontrado"
    
    @pytest.mark.asyncio
    async def test_deprecated_routes_redirect_or_exist(self):
        """Rotas deprecated devem existir (compatibilidade) ou redirecionar"""
        deprecated_routes = [
            "/api/empresas/criar",
            "/api/empresas/listar",
            "/api/Proprietario/tipovinculo"
        ]
        
        async with httpx.AsyncClient() as client:
            for route in deprecated_routes:
                response = await client.get(f"{BASE_URL}{route}")
                # Deve existir (200, 301, 401, 403) ou estar deprecated, mas não 404
                assert response.status_code != 404, f"Rota deprecated {route} não encontrada"
                
                # Se redirecionar, deve ter header Location
                if response.status_code == 301:
                    assert "location" in response.headers.keys() or "Location" in response.headers.keys()

class TestPaginationSupport:
    """Testa suporte à paginação"""
    
    @pytest.mark.asyncio
    async def test_pagination_parameters_accepted(self):
        """Endpoints de listagem devem aceitar parâmetros de paginação"""
        list_endpoints = [
            "/api/empresas",
            "/api/financeiro/transacoes",
            "/api/marketing/campanhas"
        ]
        
        headers = {"Authorization": f"Bearer {TEST_TOKEN}"} if TEST_TOKEN != "test-token-placeholder" else {}
        
        async with httpx.AsyncClient() as client:
            for endpoint in list_endpoints:
                # Testa com parâmetros de paginação
                response = await client.get(
                    f"{BASE_URL}{endpoint}?page=1&pageSize=10", 
                    headers=headers
                )
                
                # Não deve dar erro de parâmetro inválido (400)
                assert response.status_code != 400, f"Endpoint {endpoint} não aceita paginação"

class TestErrorHandling:
    """Testa tratamento de erros"""
    
    @pytest.mark.asyncio
    async def test_not_found_returns_404(self):
        """Rotas inexistentes devem retornar 404"""
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BASE_URL}/api/inexistente")
            assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_method_not_allowed_returns_405(self):
        """Métodos não permitidos devem retornar 405"""
        async with httpx.AsyncClient() as client:
            # Tenta DELETE em endpoint que só aceita GET/POST
            response = await client.delete(f"{BASE_URL}/api/dashboard")
            assert response.status_code in [405, 401, 403]  # 401/403 por falta de auth é aceitável

class TestResponseFormats:
    """Testa formatos de resposta"""
    
    @pytest.mark.asyncio
    async def test_json_content_type(self):
        """Respostas devem ser JSON"""
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BASE_URL}/health")
            assert response.status_code == 200
            assert "application/json" in response.headers.get("content-type", "")
    
    @pytest.mark.asyncio
    async def test_error_responses_have_structure(self):
        """Respostas de erro devem ter estrutura padronizada"""
        async with httpx.AsyncClient() as client:
            # Força um erro 401
            response = await client.get(f"{BASE_URL}/api/dashboard")
            
            if response.status_code in [401, 403]:
                data = response.json()
                # Verifica estrutura mínima de erro
                assert "status" in data or "message" in data or "detail" in data

# Configurações de pytest
def pytest_configure(config):
    """Configuração do pytest"""
    config.addinivalue_line(
        "markers", "asyncio: marca testes como assíncronos"
    )

@pytest.fixture(scope="session")
def event_loop():
    """Fixture para loop de eventos assíncrono"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

# Executar testes específicos baseado em variáveis de ambiente
def pytest_collection_modifyitems(config, items):
    """Modifica execução de testes baseado no ambiente"""
    if os.getenv("SKIP_AUTH_TESTS") == "true":
        skip_auth = pytest.mark.skip(reason="Testes de auth desabilitados")
        for item in items:
            if "auth" in item.nodeid.lower() or "security" in item.nodeid.lower():
                item.add_marker(skip_auth)