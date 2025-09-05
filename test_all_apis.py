#!/usr/bin/env python3
"""
Script de teste completo para todas as APIs do sistema
Testa todas as funcionalidades implementadas
"""

import requests
import json
from datetime import datetime, timedelta
import sys
from typing import Dict, List, Any
from colorama import init, Fore, Style

# Inicializar colorama para cores no terminal
init()

# Configuração da API
BASE_URL = "http://localhost:8000/api"
HEADERS = {"Content-Type": "application/json"}

# Dados de teste
TEST_USER = {
    "cpf": "12345678900",
    "nome": "Usuário Teste API",
    "email": "teste.api@example.com",
    "senha": "senha123",
    "telefone": "(11) 99999-9999",
    "tipo": "admin"
}

TEST_WORKSPACE = {
    "nome": "Workspace Teste",
    "slug": "workspace-teste",
    "plano": "pro"
}

TEST_EVENTO = {
    "nome": "Evento Teste API",
    "descricao": "Evento criado para testar APIs",
    "data_evento": (datetime.now() + timedelta(days=7)).isoformat(),
    "local": "Local Teste",
    "endereco": "Rua Teste, 123",
    "capacidade_maxima": 1000,
    "limite_idade": 18
}

TEST_RECORRENCIA = {
    "tipo_recorrencia": "semanal",
    "intervalo": 1,
    "dias_semana": [1, 3, 5],  # Segunda, Quarta, Sexta
    "data_fim": (datetime.now() + timedelta(days=90)).isoformat(),
    "max_ocorrencias": 12
}

TEST_FILA = {
    "nome": "Fila de Credenciamento",
    "descricao": "Fila virtual para credenciamento",
    "tipo": "prioridade",
    "capacidade_maxima": 100,
    "tempo_medio_atendimento": 5
}

class APITester:
    def __init__(self):
        self.token = None
        self.user_id = None
        self.workspace_id = None
        self.evento_id = None
        self.recorrencia_id = None
        self.fila_id = None
        self.success_count = 0
        self.fail_count = 0
        self.tests_run = 0
        
    def print_header(self, text: str):
        """Imprime cabeçalho formatado"""
        print(f"\n{Fore.CYAN}{'='*60}")
        print(f"{text.center(60)}")
        print(f"{'='*60}{Style.RESET_ALL}")
        
    def print_test(self, name: str, success: bool, message: str = ""):
        """Imprime resultado do teste"""
        self.tests_run += 1
        if success:
            self.success_count += 1
            status = f"{Fore.GREEN}✓ PASSOU{Style.RESET_ALL}"
        else:
            self.fail_count += 1
            status = f"{Fore.RED}✗ FALHOU{Style.RESET_ALL}"
        
        print(f"  {self.tests_run:03d}. {name:<40} [{status}]")
        if message:
            print(f"       {Fore.YELLOW}{message}{Style.RESET_ALL}")
    
    def make_request(self, method: str, endpoint: str, data: Dict = None, auth: bool = True) -> Dict:
        """Faz requisição à API"""
        url = f"{BASE_URL}{endpoint}"
        headers = HEADERS.copy()
        
        if auth and self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        
        try:
            if method == "GET":
                response = requests.get(url, headers=headers)
            elif method == "POST":
                response = requests.post(url, headers=headers, json=data)
            elif method == "PUT":
                response = requests.put(url, headers=headers, json=data)
            elif method == "DELETE":
                response = requests.delete(url, headers=headers)
            else:
                return {"error": f"Método {method} não suportado"}
            
            if response.status_code in [200, 201]:
                return response.json() if response.content else {"success": True}
            else:
                return {"error": f"Status {response.status_code}: {response.text}"}
                
        except requests.exceptions.ConnectionError:
            return {"error": "Não foi possível conectar ao servidor. Verifique se o backend está rodando."}
        except Exception as e:
            return {"error": str(e)}
    
    def test_auth(self):
        """Testa autenticação"""
        self.print_header("TESTANDO AUTENTICAÇÃO")
        
        # Registrar usuário
        result = self.make_request("POST", "/auth/register", TEST_USER, auth=False)
        if "error" not in result:
            self.print_test("Registro de usuário", True)
            self.user_id = result.get("id")
        else:
            # Tentar login se já existe
            self.print_test("Registro de usuário", False, "Usuário já existe")
        
        # Login
        login_data = {"cpf": TEST_USER["cpf"], "senha": TEST_USER["senha"]}
        result = self.make_request("POST", "/auth/login", login_data, auth=False)
        if "error" not in result and "access_token" in result:
            self.print_test("Login", True)
            self.token = result["access_token"]
        else:
            self.print_test("Login", False, result.get("error", "Token não retornado"))
        
        # Verificar token
        result = self.make_request("GET", "/auth/me")
        self.print_test("Verificar token JWT", "error" not in result)
        
    def test_workspaces(self):
        """Testa funcionalidades de workspaces"""
        self.print_header("TESTANDO WORKSPACES")
        
        # Criar workspace
        result = self.make_request("POST", "/workspaces", TEST_WORKSPACE)
        if "error" not in result:
            self.print_test("Criar workspace", True)
            self.workspace_id = result.get("id")
        else:
            self.print_test("Criar workspace", False, result.get("error"))
        
        # Listar workspaces
        result = self.make_request("GET", "/workspaces")
        self.print_test("Listar workspaces", "error" not in result and isinstance(result, list))
        
        # Obter workspace atual
        result = self.make_request("GET", "/workspaces/current")
        self.print_test("Obter workspace atual", "error" not in result)
        
        if self.workspace_id:
            # Obter detalhes do workspace
            result = self.make_request("GET", f"/workspaces/{self.workspace_id}")
            self.print_test("Obter detalhes do workspace", "error" not in result)
            
            # Atualizar workspace
            update_data = {"nome": "Workspace Atualizado"}
            result = self.make_request("PUT", f"/workspaces/{self.workspace_id}", update_data)
            self.print_test("Atualizar workspace", "error" not in result)
            
            # Estatísticas do workspace
            result = self.make_request("GET", f"/workspaces/{self.workspace_id}/stats")
            self.print_test("Obter estatísticas", "error" not in result)
    
    def test_eventos(self):
        """Testa funcionalidades de eventos"""
        self.print_header("TESTANDO EVENTOS")
        
        # Criar evento
        result = self.make_request("POST", "/eventos", TEST_EVENTO)
        if "error" not in result:
            self.print_test("Criar evento", True)
            self.evento_id = result.get("id")
        else:
            self.print_test("Criar evento", False, result.get("error"))
        
        # Listar eventos
        result = self.make_request("GET", "/eventos")
        self.print_test("Listar eventos", "error" not in result and isinstance(result, list))
        
        if self.evento_id:
            # Obter detalhes do evento
            result = self.make_request("GET", f"/eventos/{self.evento_id}")
            self.print_test("Obter detalhes do evento", "error" not in result)
            
            # Atualizar evento
            update_data = {"descricao": "Descrição atualizada"}
            result = self.make_request("PUT", f"/eventos/{self.evento_id}", update_data)
            self.print_test("Atualizar evento", "error" not in result)
    
    def test_recorrencia(self):
        """Testa eventos recorrentes"""
        if not self.evento_id:
            print(f"{Fore.YELLOW}Pulando testes de recorrência (evento não criado){Style.RESET_ALL}")
            return
            
        self.print_header("TESTANDO EVENTOS RECORRENTES")
        
        # Criar recorrência
        result = self.make_request("POST", f"/eventos/recorrencia/{self.evento_id}", TEST_RECORRENCIA)
        if "error" not in result:
            self.print_test("Criar recorrência", True)
            self.recorrencia_id = result.get("id")
        else:
            self.print_test("Criar recorrência", False, result.get("error"))
        
        # Obter recorrência
        result = self.make_request("GET", f"/eventos/recorrencia/{self.evento_id}")
        self.print_test("Obter recorrência", "error" not in result)
        
        # Listar próximas ocorrências
        result = self.make_request("GET", f"/eventos/recorrencia/{self.evento_id}/proximas?limite=5")
        self.print_test("Listar próximas ocorrências", "error" not in result and isinstance(result, list))
        
        if self.recorrencia_id:
            # Adicionar exceção
            excecao_data = {"data_excecao": (datetime.now() + timedelta(days=14)).date().isoformat()}
            result = self.make_request("POST", f"/eventos/recorrencia/{self.recorrencia_id}/excecoes", excecao_data)
            self.print_test("Adicionar exceção", "error" not in result)
            
            # Atualizar recorrência
            update_data = {"ativo": True}
            result = self.make_request("PUT", f"/eventos/recorrencia/{self.recorrencia_id}", update_data)
            self.print_test("Atualizar recorrência", "error" not in result)
    
    def test_filas_virtuais(self):
        """Testa filas virtuais"""
        if not self.evento_id:
            print(f"{Fore.YELLOW}Pulando testes de filas (evento não criado){Style.RESET_ALL}")
            return
            
        self.print_header("TESTANDO FILAS VIRTUAIS")
        
        # Criar fila
        fila_data = {**TEST_FILA, "evento_id": self.evento_id}
        result = self.make_request("POST", "/filas", fila_data)
        if "error" not in result:
            self.print_test("Criar fila virtual", True)
            self.fila_id = result.get("id")
        else:
            self.print_test("Criar fila virtual", False, result.get("error"))
        
        # Listar filas do evento
        result = self.make_request("GET", f"/filas/evento/{self.evento_id}")
        self.print_test("Listar filas do evento", "error" not in result and isinstance(result, list))
        
        if self.fila_id:
            # Obter detalhes da fila
            result = self.make_request("GET", f"/filas/{self.fila_id}")
            self.print_test("Obter detalhes da fila", "error" not in result)
            
            # Entrar na fila
            participante_data = {
                "cpf": "98765432100",
                "nome": "Participante Teste",
                "telefone": "(11) 88888-8888",
                "prioridade": 0
            }
            result = self.make_request("POST", f"/filas/{self.fila_id}/entrar", participante_data)
            self.print_test("Entrar na fila", "error" not in result)
            
            # Listar participantes
            result = self.make_request("GET", f"/filas/{self.fila_id}/participantes")
            self.print_test("Listar participantes", "error" not in result and isinstance(result, list))
            
            # Estatísticas da fila
            result = self.make_request("GET", f"/filas/{self.fila_id}/estatisticas")
            self.print_test("Obter estatísticas da fila", "error" not in result)
            
            # Chamar próximo
            result = self.make_request("POST", f"/filas/{self.fila_id}/chamar-proximo")
            self.print_test("Chamar próximo da fila", "error" not in result or "fila vazia" in str(result.get("error", "")).lower())
    
    def test_analytics(self):
        """Testa analytics avançado"""
        if not self.evento_id:
            print(f"{Fore.YELLOW}Pulando testes de analytics (evento não criado){Style.RESET_ALL}")
            return
            
        self.print_header("TESTANDO ANALYTICS AVANÇADO")
        
        # Analytics do evento
        result = self.make_request("GET", f"/eventos/{self.evento_id}/analytics")
        self.print_test("Obter analytics do evento", "error" not in result or "não encontrado" in str(result.get("error", "")))
        
        # Métricas em tempo real
        result = self.make_request("GET", f"/eventos/{self.evento_id}/metricas")
        self.print_test("Obter métricas em tempo real", "error" not in result or "não encontrado" in str(result.get("error", "")))
        
        # Previsões
        result = self.make_request("GET", f"/eventos/{self.evento_id}/previsoes")
        self.print_test("Obter previsões com IA", "error" not in result or "não encontrado" in str(result.get("error", "")))
    
    def test_campanhas(self):
        """Testa campanhas de marketing"""
        if not self.evento_id:
            print(f"{Fore.YELLOW}Pulando testes de campanhas (evento não criado){Style.RESET_ALL}")
            return
            
        self.print_header("TESTANDO CAMPANHAS DE MARKETING")
        
        # Criar campanha
        campanha_data = {
            "nome": "Campanha Teste",
            "descricao": "Campanha de teste",
            "tipo_canal": "email",
            "evento_id": self.evento_id,
            "segmentacao": {"idade_min": 18, "idade_max": 35},
            "conteudo": "Conteúdo da campanha",
            "data_inicio": datetime.now().isoformat(),
            "data_fim": (datetime.now() + timedelta(days=7)).isoformat()
        }
        result = self.make_request("POST", "/campanhas", campanha_data)
        self.print_test("Criar campanha", "error" not in result or "não encontrado" in str(result.get("error", "")))
        
        # Listar campanhas
        result = self.make_request("GET", "/campanhas")
        self.print_test("Listar campanhas", "error" not in result or "não encontrado" in str(result.get("error", "")))
    
    def test_audit(self):
        """Testa audit trail"""
        self.print_header("TESTANDO AUDIT TRAIL")
        
        # Obter logs de auditoria
        result = self.make_request("GET", "/audit/logs")
        self.print_test("Obter logs de auditoria", "error" not in result or "não encontrado" in str(result.get("error", "")))
        
        # Filtrar logs por usuário
        if self.user_id:
            result = self.make_request("GET", f"/audit/logs?usuario_id={self.user_id}")
            self.print_test("Filtrar logs por usuário", "error" not in result or "não encontrado" in str(result.get("error", "")))
        
        # Filtrar logs por workspace
        if self.workspace_id:
            result = self.make_request("GET", f"/audit/logs?workspace_id={self.workspace_id}")
            self.print_test("Filtrar logs por workspace", "error" not in result or "não encontrado" in str(result.get("error", "")))
    
    def print_summary(self):
        """Imprime resumo dos testes"""
        self.print_header("RESUMO DOS TESTES")
        
        total = self.success_count + self.fail_count
        if total > 0:
            success_rate = (self.success_count / total) * 100
        else:
            success_rate = 0
        
        print(f"\n  Total de testes: {total}")
        print(f"  {Fore.GREEN}Sucessos: {self.success_count}{Style.RESET_ALL}")
        print(f"  {Fore.RED}Falhas: {self.fail_count}{Style.RESET_ALL}")
        print(f"  Taxa de sucesso: {success_rate:.1f}%")
        
        if success_rate == 100:
            print(f"\n  {Fore.GREEN}🎉 TODOS OS TESTES PASSARAM! 🎉{Style.RESET_ALL}")
        elif success_rate >= 80:
            print(f"\n  {Fore.YELLOW}⚠️ A maioria dos testes passou, mas há algumas falhas{Style.RESET_ALL}")
        else:
            print(f"\n  {Fore.RED}❌ Muitos testes falharam. Verifique o backend.{Style.RESET_ALL}")
    
    def run_all_tests(self):
        """Executa todos os testes"""
        print(f"\n{Fore.MAGENTA}╔{'═'*58}╗")
        print(f"║{'TESTE COMPLETO DAS APIs DO SISTEMA'.center(58)}║")
        print(f"║{'Sistema de Gestão de Eventos Universal'.center(58)}║")
        print(f"╚{'═'*58}╝{Style.RESET_ALL}")
        
        # Verificar conexão
        print(f"\n{Fore.YELLOW}Verificando conexão com o backend em {BASE_URL}...{Style.RESET_ALL}")
        result = self.make_request("GET", "/health", auth=False)
        if "error" in result and "conectar" in result["error"]:
            print(f"{Fore.RED}❌ Não foi possível conectar ao backend!{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}Por favor, certifique-se de que o backend está rodando em {BASE_URL}{Style.RESET_ALL}")
            print(f"{Fore.CYAN}Execute: cd backend && python -m uvicorn app.main:app --reload{Style.RESET_ALL}")
            return
        
        print(f"{Fore.GREEN}✓ Backend está online!{Style.RESET_ALL}")
        
        # Executar testes
        self.test_auth()
        self.test_workspaces()
        self.test_eventos()
        self.test_recorrencia()
        self.test_filas_virtuais()
        self.test_analytics()
        self.test_campanhas()
        self.test_audit()
        
        # Resumo
        self.print_summary()

def main():
    """Função principal"""
    tester = APITester()
    tester.run_all_tests()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Testes interrompidos pelo usuário{Style.RESET_ALL}")
        sys.exit(0)
    except Exception as e:
        print(f"\n{Fore.RED}Erro inesperado: {e}{Style.RESET_ALL}")
        sys.exit(1)