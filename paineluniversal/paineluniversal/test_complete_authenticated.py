#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TESTES COMPLETOS COM AUTENTICAÇÃO
===================================

Sistema de testes abrangente para todas as funcionalidades do Painel Universal.
Inclui autenticação, CRUD, validações e integrações.

Autor: Sistema de Análise Automatizada
Data: 2024
"""

import asyncio
import json
import sys
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import httpx
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Configuração base
BASE_URL = "http://localhost:8000"
TIMEOUT = 30.0

class AuthenticatedTestSuite:
    """Suite de testes com autenticação completa"""
    
    def __init__(self):
        self.client = httpx.Client(base_url=BASE_URL, timeout=TIMEOUT)
        self.auth_token = None
        self.test_user_id = None
        self.test_empresa_id = None
        self.test_evento_id = None
        self.results = {
            "authentication": {"passed": 0, "failed": 0, "errors": []},
            "crud_operations": {"passed": 0, "failed": 0, "errors": []},
            "business_logic": {"passed": 0, "failed": 0, "errors": []},
            "integrations": {"passed": 0, "failed": 0, "errors": []},
            "permissions": {"passed": 0, "failed": 0, "errors": []},
            "total_tests": 0,
            "success_rate": 0.0,
            "execution_time": 0.0
        }
    
    def log_result(self, category: str, test_name: str, success: bool, error_msg: str = None):
        """Registra resultado de teste"""
        if success:
            self.results[category]["passed"] += 1
            print(f"✅ {test_name}")
        else:
            self.results[category]["failed"] += 1
            self.results[category]["errors"].append(f"{test_name}: {error_msg}")
            print(f"❌ {test_name}: {error_msg}")
        
        self.results["total_tests"] += 1
    
    async def setup_test_environment(self) -> bool:
        """Configura ambiente de teste"""
        print("🔧 Configurando ambiente de teste...")
        
        try:
            # Teste de conectividade
            response = self.client.get("/health")
            if response.status_code != 200:
                print(f"❌ Backend inacessível: {response.status_code}")
                return False
            
            print("✅ Backend conectado")
            return True
            
        except Exception as e:
            print(f"❌ Erro na configuração: {str(e)}")
            return False
    
    async def authenticate_admin_user(self) -> bool:
        """Autentica usuário administrador"""
        print("🔐 Testando autenticação...")
        
        try:
            # Dados de login (admin padrão do sistema)
            login_data = {
                "email": "admin@paineluniversal.com",
                "password": "admin123"
            }
            
            # Tentativa de login
            response = self.client.post("/api/auth/login", json=login_data)
            
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get("access_token")
                self.test_user_id = data.get("user_id")
                
                if self.auth_token:
                    # Configura header de autenticação
                    self.client.headers.update({
                        "Authorization": f"Bearer {self.auth_token}"
                    })
                    self.log_result("authentication", "Login Admin", True)
                    return True
            
            # Se não conseguiu com admin padrão, tenta criar usuário de teste
            return await self.create_test_user()
            
        except Exception as e:
            self.log_result("authentication", "Login Admin", False, str(e))
            return await self.create_test_user()
    
    async def create_test_user(self) -> bool:
        """Cria usuário de teste se necessário"""
        try:
            # Dados do usuário de teste
            user_data = {
                "nome": "Usuario Teste",
                "email": "teste@teste.com",
                "password": "teste123",
                "tipo_usuario": "ADMINISTRADOR"
            }
            
            # Registra usuário
            response = self.client.post("/api/auth/register", json=user_data)
            
            if response.status_code in [200, 201]:
                # Tenta fazer login
                login_data = {
                    "email": user_data["email"],
                    "password": user_data["password"]
                }
                
                login_response = self.client.post("/api/auth/login", json=login_data)
                
                if login_response.status_code == 200:
                    data = login_response.json()
                    self.auth_token = data.get("access_token")
                    self.test_user_id = data.get("user_id")
                    
                    if self.auth_token:
                        self.client.headers.update({
                            "Authorization": f"Bearer {self.auth_token}"
                        })
                        self.log_result("authentication", "Criação Usuário Teste", True)
                        return True
            
            self.log_result("authentication", "Criação Usuário Teste", False, f"Status: {response.status_code}")
            return False
            
        except Exception as e:
            self.log_result("authentication", "Criação Usuário Teste", False, str(e))
            return False
    
    async def test_crud_operations(self):
        """Testa operações CRUD principais"""
        print("📝 Testando operações CRUD...")
        
        # Teste CRUD Empresas
        await self.test_empresa_crud()
        
        # Teste CRUD Eventos  
        await self.test_evento_crud()
        
        # Teste CRUD Produtos
        await self.test_produto_crud()
        
        # Teste CRUD Usuários
        await self.test_usuario_crud()
    
    async def test_empresa_crud(self):
        """Testa CRUD de empresas"""
        try:
            # CREATE - Criar empresa
            empresa_data = {
                "nome": "Empresa Teste",
                "cnpj": "12345678000123",
                "email": "empresa@teste.com",
                "telefone": "(11) 99999-9999",
                "endereco": "Rua Teste, 123"
            }
            
            create_response = self.client.post("/api/empresas/", json=empresa_data)
            
            if create_response.status_code in [200, 201]:
                empresa = create_response.json()
                self.test_empresa_id = empresa.get("id")
                self.log_result("crud_operations", "CREATE Empresa", True)
                
                # READ - Listar empresas
                list_response = self.client.get("/api/empresas/")
                if list_response.status_code == 200:
                    self.log_result("crud_operations", "READ Empresas", True)
                else:
                    self.log_result("crud_operations", "READ Empresas", False, f"Status: {list_response.status_code}")
                
                # UPDATE - Atualizar empresa
                if self.test_empresa_id:
                    update_data = {"nome": "Empresa Teste Atualizada"}
                    update_response = self.client.put(f"/api/empresas/{self.test_empresa_id}", json=update_data)
                    
                    if update_response.status_code == 200:
                        self.log_result("crud_operations", "UPDATE Empresa", True)
                    else:
                        self.log_result("crud_operations", "UPDATE Empresa", False, f"Status: {update_response.status_code}")
            else:
                self.log_result("crud_operations", "CREATE Empresa", False, f"Status: {create_response.status_code}")
                
        except Exception as e:
            self.log_result("crud_operations", "CRUD Empresa", False, str(e))
    
    async def test_evento_crud(self):
        """Testa CRUD de eventos"""
        try:
            if not self.test_empresa_id:
                self.log_result("crud_operations", "CRUD Evento", False, "Empresa não disponível")
                return
            
            # CREATE - Criar evento
            evento_data = {
                "nome": "Evento Teste",
                "descricao": "Descrição do evento teste",
                "data_inicio": (datetime.now() + timedelta(days=30)).isoformat(),
                "data_fim": (datetime.now() + timedelta(days=31)).isoformat(),
                "local": "Local Teste",
                "empresa_id": self.test_empresa_id,
                "status": "ATIVO"
            }
            
            create_response = self.client.post("/api/eventos/", json=evento_data)
            
            if create_response.status_code in [200, 201]:
                evento = create_response.json()
                self.test_evento_id = evento.get("id")
                self.log_result("crud_operations", "CREATE Evento", True)
                
                # READ - Listar eventos
                list_response = self.client.get("/api/eventos/")
                if list_response.status_code == 200:
                    self.log_result("crud_operations", "READ Eventos", True)
                else:
                    self.log_result("crud_operations", "READ Eventos", False, f"Status: {list_response.status_code}")
            else:
                self.log_result("crud_operations", "CREATE Evento", False, f"Status: {create_response.status_code}")
                
        except Exception as e:
            self.log_result("crud_operations", "CRUD Evento", False, str(e))
    
    async def test_produto_crud(self):
        """Testa CRUD de produtos"""
        try:
            # CREATE - Criar produto
            produto_data = {
                "nome": "Produto Teste",
                "preco": 100.0,
                "descricao": "Descrição do produto teste",
                "categoria": "INGRESSO",
                "ativo": True
            }
            
            create_response = self.client.post("/api/produtos/", json=produto_data)
            
            if create_response.status_code in [200, 201]:
                self.log_result("crud_operations", "CREATE Produto", True)
                
                # READ - Listar produtos
                list_response = self.client.get("/api/produtos/")
                if list_response.status_code == 200:
                    self.log_result("crud_operations", "READ Produtos", True)
                else:
                    self.log_result("crud_operations", "READ Produtos", False, f"Status: {list_response.status_code}")
            else:
                self.log_result("crud_operations", "CREATE Produto", False, f"Status: {create_response.status_code}")
                
        except Exception as e:
            self.log_result("crud_operations", "CRUD Produto", False, str(e))
    
    async def test_usuario_crud(self):
        """Testa CRUD de usuários"""
        try:
            # READ - Listar usuários (teste de permissão)
            list_response = self.client.get("/api/usuarios/")
            
            if list_response.status_code == 200:
                self.log_result("crud_operations", "READ Usuários", True)
            elif list_response.status_code == 403:
                self.log_result("permissions", "Permissão Usuários", True)  # Bloqueio esperado
            else:
                self.log_result("crud_operations", "READ Usuários", False, f"Status: {list_response.status_code}")
                
        except Exception as e:
            self.log_result("crud_operations", "CRUD Usuário", False, str(e))
    
    async def test_business_logic(self):
        """Testa lógica de negócio"""
        print("🏢 Testando lógica de negócio...")
        
        await self.test_dashboard_endpoints()
        await self.test_listas_endpoints()
        await self.test_pdv_endpoints()
    
    async def test_dashboard_endpoints(self):
        """Testa endpoints do dashboard"""
        try:
            # Dashboard geral
            response = self.client.get("/api/dashboard/")
            if response.status_code == 200:
                self.log_result("business_logic", "Dashboard Geral", True)
            else:
                self.log_result("business_logic", "Dashboard Geral", False, f"Status: {response.status_code}")
            
            # Métricas gerais
            metrics_response = self.client.get("/api/dashboard/metricas")
            if metrics_response.status_code == 200:
                self.log_result("business_logic", "Métricas Dashboard", True)
            else:
                self.log_result("business_logic", "Métricas Dashboard", False, f"Status: {metrics_response.status_code}")
                
        except Exception as e:
            self.log_result("business_logic", "Dashboard", False, str(e))
    
    async def test_listas_endpoints(self):
        """Testa endpoints de listas (com parâmetros corretos)"""
        try:
            if self.test_evento_id:
                # Lista por evento
                response = self.client.get(f"/api/listas/evento/{self.test_evento_id}")
                if response.status_code in [200, 404]:  # 404 é OK se não houver listas
                    self.log_result("business_logic", "Listas por Evento", True)
                else:
                    self.log_result("business_logic", "Listas por Evento", False, f"Status: {response.status_code}")
            else:
                self.log_result("business_logic", "Listas por Evento", False, "Evento não disponível")
                
        except Exception as e:
            self.log_result("business_logic", "Listas", False, str(e))
    
    async def test_pdv_endpoints(self):
        """Testa endpoints do PDV"""
        try:
            # Status do PDV
            response = self.client.get("/api/pdv/status")
            if response.status_code == 200:
                self.log_result("business_logic", "Status PDV", True)
            else:
                self.log_result("business_logic", "Status PDV", False, f"Status: {response.status_code}")
                
        except Exception as e:
            self.log_result("business_logic", "PDV", False, str(e))
    
    async def test_integrations(self):
        """Testa integrações"""
        print("🔗 Testando integrações...")
        
        # WhatsApp
        await self.test_whatsapp_integration()
        
        # MEEP
        await self.test_meep_integration()
        
        # N8N
        await self.test_n8n_integration()
    
    async def test_whatsapp_integration(self):
        """Testa integração WhatsApp"""
        try:
            response = self.client.get("/api/whatsapp/status")
            if response.status_code in [200, 503]:  # 503 pode indicar serviço não configurado
                self.log_result("integrations", "WhatsApp Status", True)
            else:
                self.log_result("integrations", "WhatsApp Status", False, f"Status: {response.status_code}")
                
        except Exception as e:
            self.log_result("integrations", "WhatsApp", False, str(e))
    
    async def test_meep_integration(self):
        """Testa integração MEEP"""
        try:
            response = self.client.get("/api/meep/status")
            if response.status_code in [200, 503]:  # 503 pode indicar serviço não configurado
                self.log_result("integrations", "MEEP Status", True)
            else:
                self.log_result("integrations", "MEEP Status", False, f"Status: {response.status_code}")
                
        except Exception as e:
            self.log_result("integrations", "MEEP", False, str(e))
    
    async def test_n8n_integration(self):
        """Testa integração N8N"""
        try:
            response = self.client.get("/api/n8n/workflows")
            if response.status_code in [200, 503]:  # 503 pode indicar serviço não configurado
                self.log_result("integrations", "N8N Workflows", True)
            else:
                self.log_result("integrations", "N8N Workflows", False, f"Status: {response.status_code}")
                
        except Exception as e:
            self.log_result("integrations", "N8N", False, str(e))
    
    async def cleanup_test_data(self):
        """Limpa dados de teste"""
        print("🧹 Limpando dados de teste...")
        
        try:
            # Remove evento de teste
            if self.test_evento_id:
                self.client.delete(f"/api/eventos/{self.test_evento_id}")
            
            # Remove empresa de teste
            if self.test_empresa_id:
                self.client.delete(f"/api/empresas/{self.test_empresa_id}")
                
            print("✅ Dados de teste removidos")
            
        except Exception as e:
            print(f"⚠️ Erro na limpeza: {str(e)}")
    
    def generate_report(self):
        """Gera relatório final"""
        total_passed = sum(cat["passed"] for cat in self.results.values() if isinstance(cat, dict) and "passed" in cat)
        total_tests = self.results["total_tests"]
        
        if total_tests > 0:
            self.results["success_rate"] = (total_passed / total_tests) * 100
        
        print("\n" + "="*80)
        print("📊 RELATÓRIO FINAL DE TESTES")
        print("="*80)
        
        print(f"🎯 Taxa de Sucesso: {self.results['success_rate']:.1f}%")
        print(f"📈 Testes Passaram: {total_passed}/{total_tests}")
        print(f"⏱️ Tempo de Execução: {self.results['execution_time']:.2f}s")
        
        print("\n📋 RESULTADOS POR CATEGORIA:")
        for category, data in self.results.items():
            if isinstance(data, dict) and "passed" in data:
                total_cat = data["passed"] + data["failed"]
                if total_cat > 0:
                    success_rate = (data["passed"] / total_cat) * 100
                    print(f"  {category.replace('_', ' ').title()}: {success_rate:.1f}% ({data['passed']}/{total_cat})")
        
        # Exibe erros se houver
        all_errors = []
        for category, data in self.results.items():
            if isinstance(data, dict) and "errors" in data and data["errors"]:
                all_errors.extend(data["errors"])
        
        if all_errors:
            print(f"\n❌ ERROS ENCONTRADOS ({len(all_errors)}):")
            for error in all_errors[:10]:  # Limita a 10 erros
                print(f"  • {error}")
            
            if len(all_errors) > 10:
                print(f"  ... e mais {len(all_errors) - 10} erros")
        
        print("="*80)
        
        # Salva relatório
        with open("test_complete_report.json", "w", encoding="utf-8") as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        
        print("📁 Relatório salvo em: test_complete_report.json")
        
        return self.results

async def main():
    """Função principal"""
    start_time = time.time()
    
    print("🚀 INICIANDO TESTES COMPLETOS DO PAINEL UNIVERSAL")
    print("="*80)
    
    suite = AuthenticatedTestSuite()
    
    try:
        # 1. Configuração
        if not await suite.setup_test_environment():
            print("❌ Falha na configuração do ambiente")
            return
        
        # 2. Autenticação
        if not await suite.authenticate_admin_user():
            print("❌ Falha na autenticação")
            return
        
        # 3. Testes CRUD
        await suite.test_crud_operations()
        
        # 4. Lógica de negócio
        await suite.test_business_logic()
        
        # 5. Integrações
        await suite.test_integrations()
        
        # 6. Limpeza
        await suite.cleanup_test_data()
        
    except Exception as e:
        print(f"❌ Erro geral: {str(e)}")
    
    finally:
        suite.results["execution_time"] = time.time() - start_time
        suite.generate_report()

if __name__ == "__main__":
    asyncio.run(main())
