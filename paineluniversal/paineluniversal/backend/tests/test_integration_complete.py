"""
🧪 TESTES DE INTEGRAÇÃO COMPLETOS - BACKEND
Testes end-to-end para validar toda a refatoração
Última atualização: 05/01/2025
"""

import pytest
import asyncio
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
from decimal import Decimal
import os
import sys
from pathlib import Path

# Adicionar path do projeto
sys.path.append(str(Path(__file__).parent.parent))

from app.main import app
from app.database import Base, get_db
from app.models import Usuario, Evento, Produto, Lista
from app.auth import create_access_token, get_password_hash
from app.validators import formatar_cpf, formatar_cnpj
from app.enums import (
    StatusEvento, TipoLista, TipoProduto, StatusProduto,
    StatusTransacao, TipoPagamentoPDV
)

# ===== CONFIGURAÇÃO DE TESTE =====

# Criar banco de dados de teste em memória
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Override da dependência de banco de dados
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

# Cliente de teste
client = TestClient(app)

# ===== FIXTURES =====

@pytest.fixture(scope="function")
def setup_database():
    """Cria e limpa o banco de dados para cada teste"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def admin_user(setup_database):
    """Cria um usuário admin para testes"""
    db = TestingSessionLocal()
    try:
        user = Usuario(
            cpf=formatar_cpf("12345678901"),
            nome="Admin Teste",
            email="admin@teste.com",
            telefone="(11) 98765-4321",
            senha_hash=get_password_hash("senha123"),
            tipo="admin",
            ativo=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    finally:
        db.close()

@pytest.fixture
def admin_token(admin_user):
    """Gera token JWT para usuário admin"""
    return create_access_token(data={"sub": admin_user.cpf})

@pytest.fixture
def auth_headers(admin_token):
    """Headers de autenticação para requisições"""
    return {"Authorization": f"Bearer {admin_token}"}

# ===== TESTES DE VALIDAÇÃO =====

class TestValidators:
    """Testes dos validadores centralizados"""
    
    def test_cpf_validation(self):
        """Testa validação de CPF"""
        # CPF válido
        response = client.post(
            "/api/auth/register",
            json={
                "cpf": "123.456.789-09",  # CPF válido formatado
                "nome": "Teste Silva",
                "email": "teste@example.com",
                "senha": "senha123",
                "tipo": "cliente"
            }
        )
        assert response.status_code in [200, 201, 409]  # 409 se já existe
        
        # CPF inválido
        response = client.post(
            "/api/auth/register",
            json={
                "cpf": "111.111.111-11",  # CPF inválido
                "nome": "Teste Silva",
                "email": "teste2@example.com",
                "senha": "senha123"
            }
        )
        assert response.status_code == 422
        assert "cpf" in str(response.json()).lower()
    
    def test_email_validation(self):
        """Testa validação de email"""
        # Email inválido
        response = client.post(
            "/api/auth/register",
            json={
                "cpf": "987.654.321-00",
                "nome": "Teste Silva",
                "email": "email_invalido",  # Email inválido
                "senha": "senha123"
            }
        )
        assert response.status_code == 422
        assert "email" in str(response.json()).lower()
    
    def test_phone_validation(self, setup_database):
        """Testa validação de telefone"""
        # Telefone válido
        response = client.post(
            "/api/auth/register",
            json={
                "cpf": "147.258.369-00",
                "nome": "Teste Silva",
                "email": "teste3@example.com",
                "telefone": "(11) 98765-4321",  # Formato válido
                "senha": "senha123"
            }
        )
        assert response.status_code in [200, 201]
        
        # Telefone inválido
        response = client.post(
            "/api/auth/register",
            json={
                "cpf": "258.369.147-00",
                "nome": "Teste Silva",
                "email": "teste4@example.com",
                "telefone": "123",  # Telefone inválido
                "senha": "senha123"
            }
        )
        assert response.status_code == 422

# ===== TESTES DE ENUMS =====

class TestEnums:
    """Testes dos enums padronizados"""
    
    def test_status_evento_enum(self, setup_database, auth_headers):
        """Testa enum StatusEvento"""
        # Criar evento com enum válido
        response = client.post(
            "/api/eventos",
            json={
                "nome": "Evento Teste",
                "descricao": "Teste de enum",
                "data_evento": (datetime.now() + timedelta(days=30)).isoformat(),
                "local": "Local Teste",
                "limite_idade": 18,
                "capacidade_maxima": 100
            },
            headers=auth_headers
        )
        assert response.status_code in [200, 201]
        evento_id = response.json()["id"]
        
        # Atualizar com status válido
        response = client.put(
            f"/api/eventos/{evento_id}",
            json={"status": "ATIVO"},  # Enum em MAIÚSCULO
            headers=auth_headers
        )
        assert response.status_code == 200
        
        # Tentar atualizar com status inválido
        response = client.put(
            f"/api/eventos/{evento_id}",
            json={"status": "invalido"},
            headers=auth_headers
        )
        assert response.status_code == 422
    
    def test_tipo_produto_enum(self, setup_database, auth_headers):
        """Testa enum TipoProduto"""
        # Criar produto com tipo válido
        response = client.post(
            "/api/produtos",
            json={
                "nome": "Produto Teste",
                "tipo": "BEBIDA",  # Enum em MAIÚSCULO
                "preco": 10.50,
                "categoria": "Teste",
                "estoque_atual": 100
            },
            headers=auth_headers
        )
        assert response.status_code in [200, 201]
        
        # Tentar criar com tipo inválido
        response = client.post(
            "/api/produtos",
            json={
                "nome": "Produto Teste 2",
                "tipo": "tipo_invalido",
                "preco": 10.50
            },
            headers=auth_headers
        )
        assert response.status_code == 422

# ===== TESTES DE SCHEMAS =====

class TestSchemas:
    """Testes dos schemas sincronizados"""
    
    def test_usuario_create_schema(self, setup_database):
        """Testa schema UsuarioCreate"""
        # Dados completos e válidos
        response = client.post(
            "/api/auth/register",
            json={
                "cpf": "369.258.147-00",
                "nome": "Usuario Completo",
                "email": "completo@example.com",
                "telefone": "(21) 98765-4321",
                "senha": "senha_segura_123",
                "tipo": "promoter"
            }
        )
        assert response.status_code in [200, 201]
        data = response.json()
        assert "user" in data or "id" in data
        
        # Campos obrigatórios faltando
        response = client.post(
            "/api/auth/register",
            json={
                "cpf": "456.789.123-00",
                # nome faltando
                "email": "sem_nome@example.com",
                "senha": "senha123"
            }
        )
        assert response.status_code == 422
        assert "nome" in str(response.json()).lower()
    
    def test_evento_create_schema(self, setup_database, auth_headers):
        """Testa schema EventoCreate"""
        # Dados completos e válidos
        evento_data = {
            "nome": "Evento Schema Test",
            "descricao": "Testando schema completo",
            "data_evento": (datetime.now() + timedelta(days=60)).isoformat(),
            "local": "Local do Evento",
            "endereco": "Rua Teste, 123",
            "limite_idade": 21,
            "capacidade_maxima": 500,
            "empresa_id": None  # Campo opcional
        }
        
        response = client.post(
            "/api/eventos",
            json=evento_data,
            headers=auth_headers
        )
        assert response.status_code in [200, 201]
        data = response.json()
        assert data["nome"] == evento_data["nome"]
        assert data["status"] in ["ATIVO", "RASCUNHO"]
    
    def test_produto_create_schema(self, setup_database, auth_headers):
        """Testa schema ProdutoCreate"""
        produto_data = {
            "nome": "Cerveja Premium",
            "descricao": "Cerveja artesanal importada",
            "tipo": "BEBIDA",
            "preco": 15.90,
            "codigo_interno": "CERV001",
            "categoria": "Bebidas Alcoólicas",
            "estoque_atual": 50,
            "estoque_minimo": 10,
            "estoque_maximo": 200,
            "controla_estoque": True,
            "imagem_url": "https://example.com/cerveja.jpg"
        }
        
        response = client.post(
            "/api/produtos",
            json=produto_data,
            headers=auth_headers
        )
        assert response.status_code in [200, 201]
        data = response.json()
        assert data["nome"] == produto_data["nome"]
        assert data["status"] == "ATIVO"
        assert data["estoque_atual"] == 50

# ===== TESTES DE TRATAMENTO DE ERROS =====

class TestErrorHandling:
    """Testes do sistema de tratamento de erros"""
    
    def test_validation_error(self, setup_database):
        """Testa erro de validação"""
        response = client.post(
            "/api/auth/register",
            json={
                "cpf": "invalido",
                "nome": "T",  # Nome muito curto
                "email": "email_invalido",
                "senha": "123"  # Senha muito curta
            }
        )
        assert response.status_code == 422
        data = response.json()
        assert "error" in data or "detail" in data
        
        # Deve ter detalhes dos campos com erro
        if "details" in data:
            assert isinstance(data["details"], list)
            assert len(data["details"]) > 0
    
    def test_not_found_error(self, setup_database, auth_headers):
        """Testa erro 404 Not Found"""
        response = client.get(
            "/api/eventos/999999",  # ID inexistente
            headers=auth_headers
        )
        assert response.status_code == 404
        data = response.json()
        assert "error" in data or "detail" in data
    
    def test_unauthorized_error(self, setup_database):
        """Testa erro 401 Unauthorized"""
        # Tentar acessar rota protegida sem token
        response = client.get("/api/eventos")
        assert response.status_code == 401
        
        # Tentar com token inválido
        response = client.get(
            "/api/eventos",
            headers={"Authorization": "Bearer token_invalido"}
        )
        assert response.status_code == 401
    
    def test_conflict_error(self, setup_database, admin_user):
        """Testa erro 409 Conflict"""
        # Tentar criar usuário com CPF duplicado
        response = client.post(
            "/api/auth/register",
            json={
                "cpf": admin_user.cpf,  # CPF já existe
                "nome": "Outro Nome",
                "email": "outro@example.com",
                "senha": "senha123"
            }
        )
        assert response.status_code == 409
        data = response.json()
        assert "error" in data or "detail" in data

# ===== TESTES DE FLUXO COMPLETO =====

class TestCompleteFlow:
    """Testes de fluxo completo end-to-end"""
    
    def test_complete_event_flow(self, setup_database, auth_headers):
        """Testa fluxo completo de criação de evento com listas"""
        # 1. Criar evento
        evento_response = client.post(
            "/api/eventos",
            json={
                "nome": "Festival de Verão 2025",
                "descricao": "O maior festival do verão",
                "data_evento": "2025-07-15T18:00:00Z",
                "local": "Praia de Copacabana",
                "endereco": "Av. Atlântica, Rio de Janeiro",
                "limite_idade": 18,
                "capacidade_maxima": 5000
            },
            headers=auth_headers
        )
        assert evento_response.status_code in [200, 201]
        evento = evento_response.json()
        evento_id = evento["id"]
        
        # 2. Criar listas para o evento
        lista_vip = client.post(
            "/api/listas",
            json={
                "nome": "Lista VIP",
                "tipo": "VIP",
                "preco": 150.00,
                "limite_vendas": 100,
                "evento_id": evento_id,
                "descricao": "Acesso VIP com open bar"
            },
            headers=auth_headers
        )
        assert lista_vip.status_code in [200, 201]
        
        lista_normal = client.post(
            "/api/listas",
            json={
                "nome": "Lista Normal",
                "tipo": "PAGANTE",
                "preco": 80.00,
                "limite_vendas": 500,
                "evento_id": evento_id
            },
            headers=auth_headers
        )
        assert lista_normal.status_code in [200, 201]
        
        # 3. Buscar evento com listas
        evento_completo = client.get(
            f"/api/eventos/{evento_id}",
            headers=auth_headers
        )
        assert evento_completo.status_code == 200
        data = evento_completo.json()
        
        # Verificar se tem as listas (se a API retornar)
        if "listas" in data:
            assert len(data["listas"]) == 2
    
    def test_complete_pdv_flow(self, setup_database, auth_headers):
        """Testa fluxo completo de PDV"""
        # 1. Criar produtos
        produtos = []
        for i in range(3):
            response = client.post(
                "/api/produtos",
                json={
                    "nome": f"Produto {i+1}",
                    "tipo": ["BEBIDA", "COMIDA", "OUTROS"][i],
                    "preco": 10.00 * (i + 1),
                    "categoria": "Teste",
                    "estoque_atual": 100
                },
                headers=auth_headers
            )
            assert response.status_code in [200, 201]
            produtos.append(response.json())
        
        # 2. Criar evento
        evento_response = client.post(
            "/api/eventos",
            json={
                "nome": "Evento PDV Test",
                "data_evento": (datetime.now() + timedelta(days=1)).isoformat(),
                "local": "Local Test"
            },
            headers=auth_headers
        )
        assert evento_response.status_code in [200, 201]
        evento_id = evento_response.json()["id"]
        
        # 3. Criar venda PDV
        venda_response = client.post(
            "/api/pdv/vendas",
            json={
                "evento_id": evento_id,
                "cpf_cliente": "123.456.789-09",
                "nome_cliente": "Cliente Teste",
                "tipo_pagamento": "DINHEIRO",
                "itens": [
                    {
                        "produto_id": produtos[0]["id"],
                        "quantidade": 2,
                        "preco_unitario": produtos[0]["preco"]
                    },
                    {
                        "produto_id": produtos[1]["id"],
                        "quantidade": 1,
                        "preco_unitario": produtos[1]["preco"]
                    }
                ],
                "observacoes": "Venda de teste"
            },
            headers=auth_headers
        )
        assert venda_response.status_code in [200, 201]
        venda = venda_response.json()
        
        # Verificar cálculo do total
        valor_esperado = (produtos[0]["preco"] * 2) + produtos[1]["preco"]
        assert abs(float(venda.get("valor_total", venda.get("valor_final", 0))) - valor_esperado) < 0.01
    
    def test_complete_financial_flow(self, setup_database, auth_headers):
        """Testa fluxo financeiro completo"""
        # 1. Criar evento
        evento_response = client.post(
            "/api/eventos",
            json={
                "nome": "Evento Financeiro",
                "data_evento": (datetime.now() + timedelta(days=7)).isoformat(),
                "local": "Local Finance"
            },
            headers=auth_headers
        )
        assert evento_response.status_code in [200, 201]
        evento_id = evento_response.json()["id"]
        
        # 2. Abrir caixa
        caixa_response = client.post(
            "/api/financeiro/caixa/abrir",
            json={
                "evento_id": evento_id,
                "saldo_inicial": 500.00,
                "observacoes_abertura": "Abertura de caixa teste"
            },
            headers=auth_headers
        )
        assert caixa_response.status_code in [200, 201]
        caixa_id = caixa_response.json()["id"]
        
        # 3. Criar movimentações
        entrada = client.post(
            "/api/financeiro/movimentacoes",
            json={
                "evento_id": evento_id,
                "tipo": "ENTRADA",
                "categoria": "Vendas",
                "descricao": "Venda de ingressos",
                "valor": 1500.00,
                "metodo_pagamento": "PIX"
            },
            headers=auth_headers
        )
        assert entrada.status_code in [200, 201]
        
        saida = client.post(
            "/api/financeiro/movimentacoes",
            json={
                "evento_id": evento_id,
                "tipo": "SAIDA",
                "categoria": "Fornecedor",
                "descricao": "Pagamento bebidas",
                "valor": 800.00,
                "metodo_pagamento": "TRANSFERENCIA"
            },
            headers=auth_headers
        )
        assert saida.status_code in [200, 201]
        
        # 4. Consultar dashboard financeiro
        dashboard = client.get(
            f"/api/financeiro/dashboard/{evento_id}",
            headers=auth_headers
        )
        assert dashboard.status_code == 200
        data = dashboard.json()
        
        # Verificar saldo
        if "saldo_atual" in data:
            # saldo_inicial (500) + entrada (1500) - saida (800) = 1200
            assert abs(float(data["saldo_atual"]) - 1200.00) < 0.01

# ===== TESTES DE PERFORMANCE =====

class TestPerformance:
    """Testes de performance e carga"""
    
    def test_bulk_insert_performance(self, setup_database, auth_headers):
        """Testa performance de inserção em massa"""
        import time
        
        # Criar 100 produtos
        start_time = time.time()
        
        for i in range(100):
            response = client.post(
                "/api/produtos",
                json={
                    "nome": f"Produto Bulk {i}",
                    "tipo": "OUTROS",
                    "preco": 10.00 + i,
                    "categoria": "Bulk Test",
                    "estoque_atual": 100
                },
                headers=auth_headers
            )
            assert response.status_code in [200, 201]
        
        elapsed_time = time.time() - start_time
        
        # Deve criar 100 produtos em menos de 30 segundos
        assert elapsed_time < 30
        
        # Verificar se todos foram criados
        response = client.get(
            "/api/produtos?limit=200",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        
        # Se a resposta é paginada
        if isinstance(data, dict) and "items" in data:
            assert len(data["items"]) >= 100
        # Se retorna lista direto
        elif isinstance(data, list):
            assert len(data) >= 100
    
    def test_concurrent_requests(self, setup_database, auth_headers):
        """Testa requisições concorrentes"""
        import threading
        import time
        
        results = []
        errors = []
        
        def make_request(index):
            try:
                response = client.get(
                    "/api/eventos",
                    headers=auth_headers
                )
                results.append(response.status_code)
            except Exception as e:
                errors.append(str(e))
        
        # Criar 50 threads fazendo requisições simultâneas
        threads = []
        for i in range(50):
            t = threading.Thread(target=make_request, args=(i,))
            threads.append(t)
            t.start()
        
        # Aguardar todas as threads
        for t in threads:
            t.join(timeout=10)
        
        # Verificar resultados
        assert len(errors) == 0, f"Erros encontrados: {errors}"
        assert all(status in [200, 201, 204] for status in results)

# ===== EXECUTAR TESTES =====

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])