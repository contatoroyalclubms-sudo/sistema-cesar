#!/usr/bin/env python3
"""
Migração para adicionar Sistema Cashless - Implementação Completa Meep
Data: 2024

Adiciona as seguintes tabelas:
- categorias_clientes
- mesas
- cartoes_cashless
- grupos_cartoes
- permissoes
- cargos
- comandas_cashless
- transacoes_cashless
"""

import os
import sys
import logging
from sqlalchemy import text
from datetime import datetime

# Adicionar o diretório backend ao path
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_path)

from app.database import SessionLocal, engine
from app.models_cashless import (
    CategoriaCliente, Mesa, CartaoCashless, GrupoCartao, 
    Permissao, Cargo, ComandaCashless, TransacaoCashless,
    TipoPermissao, TipoCategoriaCliente, StatusCategoriaCliente
)
from app.models import Base, Usuario, Empresa

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_db_session():
    """Cria uma sessão de banco de dados"""
    return SessionLocal()

def verificar_conexao():
    """Verifica se consegue conectar ao banco de dados"""
    try:
        db = get_db_session()
        try:
            result = db.execute(text("SELECT 1"))
            logger.info("✅ Conexão com banco de dados estabelecida")
            return True
        finally:
            db.close()
    except Exception as e:
        logger.error(f"❌ Erro na conexão com banco: {e}")
        return False

def verificar_tabelas_existentes():
    """Verifica quais tabelas do sistema cashless já existem"""
    tabelas_cashless = [
        'categorias_clientes',
        'mesas',
        'cartoes_cashless', 
        'grupos_cartoes',
        'permissoes',
        'cargos',
        'comandas_cashless',
        'transacoes_cashless'
    ]
    
    tabelas_existentes = []
    
    try:
        db = get_db_session()
        try:
            for tabela in tabelas_cashless:
                try:
                    # Verificar se tabela existe
                    result = db.execute(text(f"SELECT COUNT(*) FROM information_schema.tables WHERE table_name = '{tabela}'"))
                    if result.scalar() > 0:
                        tabelas_existentes.append(tabela)
                        logger.info(f"📋 Tabela '{tabela}' já existe")
                    else:
                        logger.info(f"🔍 Tabela '{tabela}' não encontrada - será criada")
                except Exception as e:
                    logger.warning(f"⚠️ Erro verificando tabela '{tabela}': {e}")
        finally:
            db.close()
                    
        return tabelas_existentes
        
    except Exception as e:
        logger.error(f"❌ Erro verificando tabelas existentes: {e}")
        return []

def criar_tabelas_cashless():
    """Cria todas as tabelas do sistema cashless"""
    try:
        logger.info("🔧 Criando tabelas do Sistema Cashless...")
        
        # Criar todas as tabelas definidas nos modelos
        Base.metadata.create_all(bind=engine)
        
        logger.info("✅ Tabelas do Sistema Cashless criadas com sucesso!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro criando tabelas do Sistema Cashless: {e}")
        return False

def criar_permissoes_padroes():
    """Cria permissões padrão do sistema cashless"""
    permissoes_padroes = [
        # Permissões de Cashless
        {"codigo": "cashless_visualizar", "nome": "cashless.visualizar", "descricao": "Visualizar sistema cashless", "modulo": "cashless", "tipo": TipoPermissao.GESTAO_CARTOES, "nivel_critico": 1},
        {"codigo": "cashless_gerenciar", "nome": "cashless.gerenciar", "descricao": "Gerenciar sistema cashless", "modulo": "cashless", "tipo": TipoPermissao.GESTAO_CARTOES, "nivel_critico": 3},
        {"codigo": "cashless_transacoes", "nome": "cashless.transacoes", "descricao": "Realizar transações cashless", "modulo": "cashless", "tipo": TipoPermissao.RECARREGAR_CARTAO, "nivel_critico": 5},
        {"codigo": "cashless_relatorios", "nome": "cashless.relatorios", "descricao": "Acessar relatórios cashless", "modulo": "cashless", "tipo": TipoPermissao.RELATORIO_VENDAS, "nivel_critico": 2},
        
        # Permissões de Categorias de Clientes
        {"codigo": "categorias_visualizar", "nome": "categorias.visualizar", "descricao": "Visualizar categorias de clientes", "modulo": "categorias", "tipo": TipoPermissao.VISUALIZAR_EVENTO, "nivel_critico": 1},
        {"codigo": "categorias_gerenciar", "nome": "categorias.gerenciar", "descricao": "Gerenciar categorias de clientes", "modulo": "categorias", "tipo": TipoPermissao.GESTAO_USUARIOS, "nivel_critico": 2},
        
        # Permissões de Mesas
        {"codigo": "mesas_visualizar", "nome": "mesas.visualizar", "descricao": "Visualizar mesas", "modulo": "mesas", "tipo": TipoPermissao.GESTAO_MESAS, "nivel_critico": 1},
        {"codigo": "mesas_gerenciar", "nome": "mesas.gerenciar", "descricao": "Gerenciar mesas", "modulo": "mesas", "tipo": TipoPermissao.GESTAO_MESAS, "nivel_critico": 2},
        {"codigo": "mesas_transferir", "nome": "mesas.transferir", "descricao": "Transferir itens entre mesas", "modulo": "mesas", "tipo": TipoPermissao.TRANSFERIR_MESA, "nivel_critico": 3},
        
        # Permissões de Cartões
        {"codigo": "cartoes_visualizar", "nome": "cartoes.visualizar", "descricao": "Visualizar cartões cashless", "modulo": "cartoes", "tipo": TipoPermissao.EXTRATO_CARTAO, "nivel_critico": 1},
        {"codigo": "cartoes_gerenciar", "nome": "cartoes.gerenciar", "descricao": "Gerenciar cartões cashless", "modulo": "cartoes", "tipo": TipoPermissao.GESTAO_CARTOES, "nivel_critico": 2},
        {"codigo": "cartoes_creditar", "nome": "cartoes.creditar", "descricao": "Creditar valor em cartões", "modulo": "cartoes", "tipo": TipoPermissao.RECARREGAR_CARTAO, "nivel_critico": 4},
        {"codigo": "cartoes_debitar", "nome": "cartoes.debitar", "descricao": "Debitar valor de cartões", "modulo": "cartoes", "tipo": TipoPermissao.BLOQUEAR_CARTAO, "nivel_critico": 5},
        
        # Permissões de Comandas
        {"codigo": "comandas_visualizar", "nome": "comandas.visualizar", "descricao": "Visualizar comandas", "modulo": "comandas", "tipo": TipoPermissao.ABRIR_MESA, "nivel_critico": 1},
        {"codigo": "comandas_gerenciar", "nome": "comandas.gerenciar", "descricao": "Gerenciar comandas", "modulo": "comandas", "tipo": TipoPermissao.GESTAO_MESAS, "nivel_critico": 2},
        {"codigo": "comandas_fechar", "nome": "comandas.fechar", "descricao": "Fechar comandas", "modulo": "comandas", "tipo": TipoPermissao.FECHAR_MESA, "nivel_critico": 3},
        
        # Permissões Administrativas
        {"codigo": "admin_permissoes", "nome": "admin.permissoes", "descricao": "Gerenciar permissões", "modulo": "admin", "tipo": TipoPermissao.ADMIN_TOTAL, "nivel_critico": 10},
        {"codigo": "admin_cargos", "nome": "admin.cargos", "descricao": "Gerenciar cargos", "modulo": "admin", "tipo": TipoPermissao.GESTAO_USUARIOS, "nivel_critico": 8},
        {"codigo": "admin_configuracoes", "nome": "admin.configuracoes", "descricao": "Acessar configurações avançadas", "modulo": "admin", "tipo": TipoPermissao.ADMIN_TOTAL, "nivel_critico": 9},
    ]
    
    try:
        db = get_db_session()
        try:
            for perm_data in permissoes_padroes:
                # Verificar se permissão já existe
                permissao_existente = db.query(Permissao).filter_by(nome=perm_data["nome"]).first()
                
                if not permissao_existente:
                    nova_permissao = Permissao(**perm_data)
                    db.add(nova_permissao)
                    logger.info(f"➕ Permissão criada: {perm_data['nome']}")
                else:
                    logger.info(f"📋 Permissão já existe: {perm_data['nome']}")
            
            db.commit()
            logger.info("✅ Permissões padrão configuradas com sucesso!")
            return True
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"❌ Erro criando permissões padrão: {e}")
        return False

def criar_cargos_padroes():
    """Cria cargos padrão do sistema cashless"""
    cargos_padroes = [
        {
            "nome": "Administrador Cashless",
            "descricao": "Acesso total ao sistema cashless",
            "nivel_hierarquia": 10
        },
        {
            "nome": "Gerente Cashless", 
            "descricao": "Gerenciamento completo do cashless",
            "nivel_hierarquia": 8
        },
        {
            "nome": "Operador Cashless",
            "descricao": "Operação básica do sistema cashless", 
            "nivel_hierarquia": 5
        },
        {
            "nome": "Caixa Cashless",
            "descricao": "Apenas transações e consultas",
            "nivel_hierarquia": 3
        }
    ]
    
    try:
        db = get_db_session()
        try:
            for cargo_data in cargos_padroes:
                # Verificar se cargo já existe
                cargo_existente = db.query(Cargo).filter_by(nome=cargo_data["nome"]).first()
                
                if not cargo_existente:
                    novo_cargo = Cargo(**cargo_data)
                    db.add(novo_cargo)
                    logger.info(f"➕ Cargo criado: {cargo_data['nome']}")
                else:
                    logger.info(f"📋 Cargo já existe: {cargo_data['nome']}")
            
            db.commit()
            logger.info("✅ Cargos padrão configurados com sucesso!")
            return True
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"❌ Erro criando cargos padrão: {e}")
        return False

def criar_categorias_padroes():
    """Cria categorias de clientes padrão"""
    try:
        db = get_db_session()
        try:
            # Buscar primeira empresa usando apenas colunas que existem
            from sqlalchemy import text
            result = db.execute(text("SELECT id, nome FROM empresas WHERE ativa = true LIMIT 1"))
            empresa_row = result.fetchone()
            
            if not empresa_row:
                logger.warning("⚠️ Nenhuma empresa ativa encontrada - categorias não serão criadas")
                return True
            
            empresa_id = empresa_row[0]
            logger.info(f"📋 Usando empresa: {empresa_row[1]} (ID: {empresa_id})")
            
            categorias_padroes = [
                {
                    "nome": "VIP",
                    "descricao": "Clientes VIP com desconto especial",
                    "tipo": TipoCategoriaCliente.VIP,
                    "cor": "#FFD700",
                    "desconto_percentual": 15.0,
                    "prioridade_atendimento": True,
                    "acesso_areas_vip": True,
                    "cashback_percentual": 5.0,
                    "empresa_id": empresa_id
                },
                {
                    "nome": "Premium", 
                    "descricao": "Clientes premium com benefícios",
                    "tipo": TipoCategoriaCliente.PREMIUM,
                    "cor": "#C0C0C0",
                    "desconto_percentual": 10.0,
                    "prioridade_atendimento": True,
                    "acesso_areas_vip": False,
                    "cashback_percentual": 3.0,
                    "empresa_id": empresa_id
                },
                {
                    "nome": "Regular",
                    "descricao": "Clientes regulares",
                    "tipo": TipoCategoriaCliente.REGULAR,
                    "cor": "#87CEEB",
                    "desconto_percentual": 0.0,
                    "prioridade_atendimento": False,
                    "acesso_areas_vip": False,
                    "cashback_percentual": 1.0,
                    "empresa_id": empresa_id
                }
            ]
            
            for cat_data in categorias_padroes:
                categoria_existente = db.query(CategoriaCliente).filter_by(
                    nome=cat_data["nome"],
                    empresa_id=empresa_id
                ).first()
                
                if not categoria_existente:
                    nova_categoria = CategoriaCliente(**cat_data)
                    db.add(nova_categoria)
                    logger.info(f"➕ Categoria criada: {cat_data['nome']}")
                else:
                    logger.info(f"📋 Categoria já existe: {cat_data['nome']}")
            
            db.commit()
            logger.info("✅ Categorias padrão configuradas com sucesso!")
            return True
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"❌ Erro criando categorias padrão: {e}")
        return False

def executar_migracao():
    """Executa toda a migração do sistema cashless"""
    logger.info("🚀 Iniciando migração do Sistema Cashless...")
    logger.info(f"📅 Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 1. Verificar conexão
    if not verificar_conexao():
        logger.error("❌ Falha na conexão com banco de dados")
        return False
    
    # 2. Verificar tabelas existentes
    tabelas_existentes = verificar_tabelas_existentes()
    logger.info(f"📊 Tabelas encontradas: {len(tabelas_existentes)}")
    
    # 3. Criar tabelas
    if not criar_tabelas_cashless():
        logger.error("❌ Falha na criação de tabelas")
        return False
    
    # 4. Criar permissões padrão
    if not criar_permissoes_padroes():
        logger.error("❌ Falha na criação de permissões")
        return False
    
    # 5. Criar cargos padrão
    if not criar_cargos_padroes():
        logger.error("❌ Falha na criação de cargos")
        return False
    
    # 6. Criar categorias padrão
    if not criar_categorias_padroes():
        logger.error("❌ Falha na criação de categorias")
        return False
    
    logger.info("🎉 Migração do Sistema Cashless concluída com sucesso!")
    logger.info("🔧 Sistema Cashless agora está disponível em /api/cashless")
    return True

if __name__ == "__main__":
    print("=" * 60)
    print("🏪 MIGRAÇÃO SISTEMA CASHLESS - IMPLEMENTAÇÃO MEEP")
    print("=" * 60)
    
    sucesso = executar_migracao()
    
    if sucesso:
        print("\n✅ MIGRAÇÃO CONCLUÍDA COM SUCESSO!")
        print("📋 Próximos passos:")
        print("   1. Reiniciar o servidor backend")
        print("   2. Acessar /docs para ver novos endpoints")
        print("   3. Implementar components React para o frontend")
    else:
        print("\n❌ MIGRAÇÃO FALHOU!")
        print("🔍 Verifique os logs acima para detalhes")
        sys.exit(1)
