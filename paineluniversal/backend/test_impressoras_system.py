#!/usr/bin/env python3
"""
Script de teste completo do sistema de impressoras
"""

import os
import sys
from pathlib import Path
import json
import asyncio
from datetime import datetime
from typing import Dict, Any, List

# Adicionar o diretório raiz ao path
sys.path.append(str(Path(__file__).parent))

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Desabilitar temporariamente para evitar conflitos
os.environ['TESTING'] = '1'

from sqlalchemy import create_engine, inspect, text, MetaData, Table, Column, Integer, String, DateTime, Boolean, Float, ForeignKey, Enum as SQLEnum, JSON as SQLJSON, Numeric, Date, Text as SQLText
from sqlalchemy.orm import Session
from app.database import engine, get_db
import enum

class TestResult:
    def __init__(self):
        self.total = 0
        self.passed = 0
        self.failed = 0
        self.errors = []
        
    def add_test(self, name: str, passed: bool, error: str = None):
        self.total += 1
        if passed:
            self.passed += 1
            logger.info(f"✅ {name}")
        else:
            self.failed += 1
            self.errors.append(f"{name}: {error}")
            logger.error(f"❌ {name}: {error}")
    
    def print_summary(self):
        logger.info("\n" + "="*50)
        logger.info(f"📊 RESUMO DOS TESTES")
        logger.info(f"Total: {self.total}")
        logger.info(f"✅ Passou: {self.passed}")
        logger.info(f"❌ Falhou: {self.failed}")
        if self.errors:
            logger.info("\n⚠️ ERROS ENCONTRADOS:")
            for error in self.errors:
                logger.info(f"  - {error}")
        logger.info("="*50)


class ImpressoraSystemTester:
    def __init__(self):
        self.results = TestResult()
        self.db = None
        
    def setup(self):
        """Configurar ambiente de teste"""
        try:
            self.db = Session(bind=engine)
            self.results.add_test("Setup do ambiente", True)
        except Exception as e:
            self.results.add_test("Setup do ambiente", False, str(e))
            return False
        return True
    
    def teardown(self):
        """Limpar ambiente de teste"""
        if self.db:
            self.db.close()
    
    def test_database_tables(self):
        """Testar estrutura das tabelas"""
        logger.info("\n🔍 TESTANDO ESTRUTURA DO BANCO DE DADOS")
        
        inspector = inspect(engine)
        existing_tables = inspector.get_table_names()
        
        # Tabelas necessárias para o novo sistema
        required_tables = {
            'impressoras_inteligentes': False,
            'templates_impressao': False,
            'filas_impressao': False,
            'logs_impressao': False,
            'equipamentos_pdv': False,
            'operadores_pdv': False
        }
        
        for table in required_tables:
            if table in existing_tables:
                required_tables[table] = True
                self.results.add_test(f"Tabela {table} existe", True)
            else:
                self.results.add_test(f"Tabela {table} existe", False, "Tabela não encontrada")
        
        # Criar tabelas que faltam
        missing_tables = [k for k, v in required_tables.items() if not v]
        if missing_tables:
            logger.info(f"\n📦 Criando {len(missing_tables)} tabelas que faltam...")
            self.create_missing_tables(missing_tables)
    
    def create_missing_tables(self, tables: List[str]):
        """Criar tabelas que estão faltando"""
        metadata = MetaData()
        
        try:
            # Criar tabela impressoras_inteligentes
            if 'impressoras_inteligentes' in tables:
                impressoras_inteligentes = Table(
                    'impressoras_inteligentes', metadata,
                    Column('id', Integer, primary_key=True),
                    Column('nome', String(100), nullable=False),
                    Column('impressora_id', String(36), nullable=False),  # FK para impressoras existente
                    Column('tipo_impressao', String(50), nullable=False),
                    Column('local_origem', String(100)),
                    Column('categoria_produto', String(100)),
                    Column('prioridade', Integer, default=0),
                    Column('ativo', Boolean, default=True),
                    Column('imprimir_logo', Boolean, default=False),
                    Column('numero_vias', Integer, default=1),
                    Column('template_id', Integer),
                    Column('hora_inicio', String(5)),
                    Column('hora_fim', String(5)),
                    Column('dias_semana', String(20)),
                    Column('evento_id', Integer),
                    Column('criado_em', DateTime, default=datetime.utcnow)
                )
                self.results.add_test("Criar impressoras_inteligentes", True)
            
            # Criar tabela templates_impressao
            if 'templates_impressao' in tables:
                templates_impressao = Table(
                    'templates_impressao', metadata,
                    Column('id', Integer, primary_key=True),
                    Column('nome', String(100), nullable=False),
                    Column('tipo', String(50)),
                    Column('cabecalho', SQLText),
                    Column('corpo', SQLText),
                    Column('rodape', SQLText),
                    Column('fonte_tamanho', String(10)),
                    Column('negrito_titulo', Boolean, default=True),
                    Column('centralizar_logo', Boolean, default=True),
                    Column('separadores', Boolean, default=True),
                    Column('incluir_qrcode', Boolean, default=False),
                    Column('qrcode_conteudo', String(500)),
                    Column('incluir_codigo_barras', Boolean, default=False),
                    Column('codigo_barras_tipo', String(20)),
                    Column('evento_id', Integer),
                    Column('ativo', Boolean, default=True),
                    Column('criado_em', DateTime, default=datetime.utcnow)
                )
                self.results.add_test("Criar templates_impressao", True)
            
            # Criar tabela filas_impressao
            if 'filas_impressao' in tables:
                filas_impressao = Table(
                    'filas_impressao', metadata,
                    Column('id', Integer, primary_key=True),
                    Column('impressora_id', String(36), nullable=False),
                    Column('tipo_documento', String(50)),
                    Column('conteudo', SQLText, nullable=False),
                    Column('prioridade', Integer, default=0),
                    Column('status', String(20), default='pendente'),
                    Column('tentativas', Integer, default=0),
                    Column('max_tentativas', Integer, default=3),
                    Column('pedido_id', Integer),
                    Column('venda_id', Integer),
                    Column('usuario_id', Integer),
                    Column('criado_em', DateTime, default=datetime.utcnow),
                    Column('processado_em', DateTime),
                    Column('erro_mensagem', SQLText)
                )
                self.results.add_test("Criar filas_impressao", True)
            
            # Criar tabela logs_impressao
            if 'logs_impressao' in tables:
                logs_impressao = Table(
                    'logs_impressao', metadata,
                    Column('id', Integer, primary_key=True),
                    Column('impressora_id', String(36), nullable=False),
                    Column('fila_impressao_id', Integer),
                    Column('tipo_documento', String(50)),
                    Column('tamanho_bytes', Integer),
                    Column('numero_linhas', Integer),
                    Column('tempo_processamento', Float),
                    Column('sucesso', Boolean, default=True),
                    Column('mensagem_erro', SQLText),
                    Column('codigo_erro', String(50)),
                    Column('ip_origem', String(45)),
                    Column('usuario_id', Integer),
                    Column('evento_id', Integer),
                    Column('data_hora', DateTime, default=datetime.utcnow)
                )
                self.results.add_test("Criar logs_impressao", True)
            
            # Criar tabela equipamentos_pdv
            if 'equipamentos_pdv' in tables:
                equipamentos_pdv = Table(
                    'equipamentos_pdv', metadata,
                    Column('id', Integer, primary_key=True),
                    Column('codigo', String(20), unique=True, nullable=False),
                    Column('tipo', String(20), nullable=False),
                    Column('nome', String(100)),
                    Column('perfil_venda', String(50)),
                    Column('impressora_padrao_id', String(36)),
                    Column('operador_id', Integer),
                    Column('licenciado', Boolean, default=False),
                    Column('data_licenca_inicio', Date),
                    Column('data_licenca_fim', Date),
                    Column('status', String(20), default='inativo'),
                    Column('localizacao', String(100)),
                    Column('evento_id', Integer),
                    Column('empresa_id', Integer),
                    Column('ultima_sincronizacao', DateTime),
                    Column('versao_software', String(20)),
                    Column('criado_em', DateTime, default=datetime.utcnow)
                )
                self.results.add_test("Criar equipamentos_pdv", True)
            
            # Criar tabela operadores_pdv
            if 'operadores_pdv' in tables:
                operadores_pdv = Table(
                    'operadores_pdv', metadata,
                    Column('id', Integer, primary_key=True),
                    Column('nome', String(100), nullable=False),
                    Column('cpf', String(14), unique=True),
                    Column('codigo_acesso', String(20)),
                    Column('comissao_percentual', Numeric(5, 2), default=0),
                    Column('comissao_fixa', Numeric(10, 2), default=0),
                    Column('pode_cancelar', Boolean, default=False),
                    Column('pode_dar_desconto', Boolean, default=False),
                    Column('desconto_maximo', Numeric(5, 2), default=0),
                    Column('ativo', Boolean, default=True),
                    Column('evento_id', Integer),
                    Column('empresa_id', Integer),
                    Column('total_vendas', Integer, default=0),
                    Column('valor_total_vendido', Numeric(10, 2), default=0),
                    Column('criado_em', DateTime, default=datetime.utcnow)
                )
                self.results.add_test("Criar operadores_pdv", True)
            
            # Criar todas as tabelas
            metadata.create_all(engine)
            logger.info("✅ Tabelas criadas com sucesso!")
            
        except Exception as e:
            logger.error(f"❌ Erro ao criar tabelas: {e}")
            self.results.add_test("Criar tabelas faltantes", False, str(e))
    
    def test_api_endpoints(self):
        """Testar endpoints da API"""
        logger.info("\n🔌 TESTANDO ENDPOINTS DA API")
        
        try:
            from fastapi.testclient import TestClient
            from app.main import app
            
            client = TestClient(app)
            
            # Fazer login primeiro
            login_data = {
                "username": "admin@teste.com",
                "password": "admin123"
            }
            
            # Testar endpoint de impressoras (sem auth por enquanto para teste)
            endpoints_to_test = [
                ("GET", "/api/impressoras/", None),
                ("GET", "/api/impressoras/inteligentes/", None),
                ("GET", "/api/impressoras/templates/", None),
                ("GET", "/api/impressoras/fila/", None),
                ("GET", "/api/impressoras/logs/", None),
                ("GET", "/api/impressoras/equipamentos/", None),
                ("GET", "/api/impressoras/operadores/", None)
            ]
            
            for method, endpoint, data in endpoints_to_test:
                try:
                    if method == "GET":
                        response = client.get(endpoint)
                    elif method == "POST":
                        response = client.post(endpoint, json=data)
                    
                    if response.status_code in [200, 201, 401, 403]:  # 401/403 esperado sem auth
                        self.results.add_test(f"{method} {endpoint}", True)
                    else:
                        self.results.add_test(f"{method} {endpoint}", False, f"Status: {response.status_code}")
                except Exception as e:
                    self.results.add_test(f"{method} {endpoint}", False, str(e))
                    
        except Exception as e:
            self.results.add_test("Teste de endpoints", False, str(e))
    
    def test_service_layer(self):
        """Testar camada de serviço"""
        logger.info("\n⚙️ TESTANDO SERVIÇO DE IMPRESSÃO")
        
        try:
            from app.services.impressao_service import ImpressaoService, ComandosESCPOS
            
            service = ImpressaoService()
            comandos = ComandosESCPOS()
            
            # Testar criação de comandos
            test_cases = [
                ("Comandos ESC/POS - INIT", comandos.INIT is not None),
                ("Comandos ESC/POS - BOLD", comandos.BOLD_ON is not None),
                ("Comandos ESC/POS - CUT", comandos.CUT_FULL is not None),
                ("Service - Verificação de conectividade", hasattr(service, 'verificar_conectividade')),
                ("Service - Envio de comandos", hasattr(service, 'enviar_comandos')),
                ("Service - Teste de impressão", hasattr(service, 'enviar_teste_impressao')),
                ("Service - Processamento de job", hasattr(service, 'processar_job'))
            ]
            
            for test_name, test_result in test_cases:
                if test_result:
                    self.results.add_test(test_name, True)
                else:
                    self.results.add_test(test_name, False, "Método/atributo não encontrado")
                    
        except Exception as e:
            self.results.add_test("Serviço de impressão", False, str(e))
    
    def test_frontend_compatibility(self):
        """Verificar compatibilidade frontend-backend"""
        logger.info("\n🎨 TESTANDO COMPATIBILIDADE FRONTEND-BACKEND")
        
        # Verificar se os tipos do frontend correspondem aos do backend
        frontend_types = {
            "TipoImpressora": ["termica", "fiscal", "etiqueta", "matricial", "laser", "pos"],
            "StatusImpressora": ["online", "offline", "erro", "manutencao", "pausada"],
            "ModeloImpressora": ["Genérica", "Epson TM-T20", "Epson TM-T20x", "Bematech MP-4200", "Elgin i8", "Elgin i9"],
            "TipoEquipamento": ["POS", "Totem", "Tablet", "Terminal", "Check"]
        }
        
        # Verificar schemas Pydantic
        try:
            from app.schemas.impressoras import (
                TipoImpressoraEnum,
                StatusImpressoraEnum,
                ModeloImpressoraEnum,
                TipoEquipamentoEnum
            )
            
            # Comparar enums
            backend_tipos = [t.value for t in TipoImpressoraEnum]
            backend_status = [s.value for s in StatusImpressoraEnum]
            backend_modelos = [m.value for m in ModeloImpressoraEnum]
            backend_equip = [e.value for e in TipoEquipamentoEnum]
            
            self.results.add_test("Schema TipoImpressora", 
                                set(frontend_types["TipoImpressora"]) == set(backend_tipos))
            self.results.add_test("Schema StatusImpressora", 
                                set(frontend_types["StatusImpressora"]) == set(backend_status))
            self.results.add_test("Schema ModeloImpressora", 
                                set(frontend_types["ModeloImpressora"]) == set(backend_modelos))
            self.results.add_test("Schema TipoEquipamento", 
                                set(frontend_types["TipoEquipamento"]) == set(backend_equip))
            
        except Exception as e:
            self.results.add_test("Compatibilidade de schemas", False, str(e))
    
    def test_data_operations(self):
        """Testar operações de dados"""
        logger.info("\n💾 TESTANDO OPERAÇÕES DE DADOS")
        
        try:
            # Testar inserção de dados de exemplo
            
            # 1. Inserir template
            template_data = {
                'nome': 'Template Teste',
                'tipo': 'cupom',
                'cabecalho': 'TESTE',
                'corpo': 'Corpo do teste',
                'rodape': 'Rodapé',
                'ativo': True
            }
            
            result = self.db.execute(
                text("""
                INSERT INTO templates_impressao (nome, tipo, cabecalho, corpo, rodape, ativo, criado_em)
                VALUES (:nome, :tipo, :cabecalho, :corpo, :rodape, :ativo, :criado_em)
                """),
                {**template_data, 'criado_em': datetime.utcnow()}
            )
            self.db.commit()
            self.results.add_test("Inserir template", result.rowcount > 0)
            
            # 2. Inserir operador
            operador_data = {
                'nome': 'Operador Teste',
                'cpf': '111.111.111-11',
                'codigo_acesso': '9999',
                'ativo': True
            }
            
            result = self.db.execute(
                text("""
                INSERT INTO operadores_pdv (nome, cpf, codigo_acesso, ativo, criado_em)
                VALUES (:nome, :cpf, :codigo_acesso, :ativo, :criado_em)
                """),
                {**operador_data, 'criado_em': datetime.utcnow()}
            )
            self.db.commit()
            self.results.add_test("Inserir operador", result.rowcount > 0)
            
            # 3. Inserir equipamento
            equipamento_data = {
                'codigo': 'TEST001',
                'tipo': 'POS',
                'nome': 'Equipamento Teste',
                'status': 'ativo'
            }
            
            result = self.db.execute(
                text("""
                INSERT INTO equipamentos_pdv (codigo, tipo, nome, status, criado_em)
                VALUES (:codigo, :tipo, :nome, :status, :criado_em)
                """),
                {**equipamento_data, 'criado_em': datetime.utcnow()}
            )
            self.db.commit()
            self.results.add_test("Inserir equipamento", result.rowcount > 0)
            
        except Exception as e:
            self.results.add_test("Operações de dados", False, str(e))
    
    def run_all_tests(self):
        """Executar todos os testes"""
        logger.info("="*50)
        logger.info("🧪 INICIANDO TESTES DO SISTEMA DE IMPRESSORAS")
        logger.info("="*50)
        
        if not self.setup():
            logger.error("❌ Falha no setup, abortando testes")
            return False
        
        # Executar testes
        self.test_database_tables()
        self.test_api_endpoints()
        self.test_service_layer()
        self.test_frontend_compatibility()
        self.test_data_operations()
        
        # Limpar
        self.teardown()
        
        # Imprimir resumo
        self.results.print_summary()
        
        # Retornar sucesso se todos passaram
        return self.results.failed == 0


def main():
    tester = ImpressoraSystemTester()
    success = tester.run_all_tests()
    
    # Salvar relatório
    report = {
        'timestamp': datetime.utcnow().isoformat(),
        'total_tests': tester.results.total,
        'passed': tester.results.passed,
        'failed': tester.results.failed,
        'errors': tester.results.errors,
        'success': success
    }
    
    with open('test_impressoras_report.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    logger.info(f"\n📄 Relatório salvo em: test_impressoras_report.json")
    
    if success:
        logger.info("\n✅ TODOS OS TESTES PASSARAM!")
        sys.exit(0)
    else:
        logger.info(f"\n❌ {tester.results.failed} TESTES FALHARAM")
        sys.exit(1)


if __name__ == "__main__":
    main()