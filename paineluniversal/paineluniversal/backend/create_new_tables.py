#!/usr/bin/env python3
"""
Script para criar todas as novas tabelas no banco de dados
Executa migrations para os novos modelos adicionados
"""

import os
import sys
from pathlib import Path

# Adicionar o diretório pai ao path
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import create_engine, text, inspect
from sqlalchemy.exc import OperationalError, ProgrammingError
from app.database import engine, Base
from app.models import (
    # Importar todos os modelos para garantir que estão registrados
    Usuario, Empresa, Evento, Lista, Transacao,
    Checkin, Cupom, Gamificacao, FormaPagamento, Comanda, Venda,
    ItemVenda, Produto, CategoriaProduto, MovimentoCaixa,
    
    # Novos modelos de estoque
    ProdutoEstoque, MovimentoEstoque, LocalEstoque, CategoriaEstoque,
    AlertaEstoque, ContagemEstoque, ItemContagem,
    
    # Novos modelos de automação
    FluxoTrabalho, ExecucaoFluxo,
    
    # Novos modelos de integrações
    WebhookIntegracao,
    
    # Novos modelos de soluções online
    SolucaoOnline, RecursoApp,
    
    # Novos modelos de tickets
    TipoTicket, LoteTicket, Ticket, TransferenciaTicket,
    
    # Novos modelos de colaboradores
    EscalaTrabalho, TarefaColaborador,
    
    # Modelos de categorias de clientes
    CategoriaCliente, ClienteCategoria, HistoricoCategoriaCliente,
    
    # Modelos de pesquisa de satisfação
    PesquisaSatisfacao, PerguntaPesquisa, RespostaPesquisa, AvaliacaoEvento,
    
    # Modelos de fidelidade
    ProgramaFidelidade, CartaoFidelidade, TransacaoFidelidade, 
    RecompensaFidelidade, ResgateRecompensa
)

def create_tables():
    """Cria todas as tabelas que ainda não existem no banco"""
    
    print("🔄 Iniciando criação de tabelas no banco de dados...")
    
    try:
        # Verificar conexão com o banco
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("✅ Conexão com banco de dados estabelecida")
            
            # Obter inspector para verificar tabelas existentes
            inspector = inspect(engine)
            existing_tables = inspector.get_table_names()
            
            print(f"📊 Tabelas existentes: {len(existing_tables)}")
            
            # Criar todas as tabelas definidas nos modelos
            Base.metadata.create_all(bind=engine)
            
            # Verificar novas tabelas criadas
            inspector = inspect(engine)
            new_existing_tables = inspector.get_table_names()
            
            new_tables = set(new_existing_tables) - set(existing_tables)
            
            if new_tables:
                print(f"✨ Novas tabelas criadas: {len(new_tables)}")
                for table in sorted(new_tables):
                    print(f"   - {table}")
            else:
                print("ℹ️  Nenhuma nova tabela foi criada (todas já existem)")
            
            print(f"📊 Total de tabelas no banco: {len(new_existing_tables)}")
            
            # Listar todas as tabelas esperadas vs existentes
            expected_tables = [
                # Tabelas principais existentes
                'usuarios', 'empresas', 'eventos', 'listas', 'clientes_listas',
                'transacoes', 'checkins', 'cupons', 'gamificacao', 'formas_pagamento',
                'comandas', 'vendas', 'itens_venda', 'produtos', 'categorias_produto',
                'movimentos_caixa',
                
                # Novas tabelas de estoque
                'produtos_estoque', 'movimentos_estoque', 'locais_estoque', 
                'categorias_estoque', 'alertas_estoque', 'contagens_estoque', 
                'itens_contagem',
                
                # Novas tabelas de automação
                'fluxos_trabalho', 'execucoes_fluxo',
                
                # Novas tabelas de integrações
                'webhooks_integracao',
                
                # Novas tabelas de soluções online
                'solucoes_online', 'recursos_app',
                
                # Novas tabelas de tickets
                'tipos_ticket', 'lotes_ticket', 'tickets', 'transferencias_ticket',
                
                # Novas tabelas de colaboradores
                'escalas_trabalho', 'tarefas_colaborador',
                
                # Tabelas de categorias de clientes
                'categorias_cliente', 'clientes_categorias', 'historico_categoria_cliente',
                
                # Tabelas de pesquisa de satisfação
                'pesquisas_satisfacao', 'perguntas_pesquisa', 'respostas_pesquisa', 
                'avaliacoes_evento',
                
                # Tabelas de fidelidade
                'programas_fidelidade', 'cartoes_fidelidade', 'transacoes_fidelidade',
                'recompensas_fidelidade', 'resgates_recompensa'
            ]
            
            missing_tables = set(expected_tables) - set(new_existing_tables)
            if missing_tables:
                print("\n⚠️  Tabelas esperadas mas não encontradas:")
                for table in sorted(missing_tables):
                    print(f"   - {table}")
            
            print("\n✅ Processo de criação de tabelas concluído com sucesso!")
            return True
            
    except OperationalError as e:
        print(f"❌ Erro de conexão com banco de dados: {e}")
        return False
    except ProgrammingError as e:
        print(f"❌ Erro SQL: {e}")
        return False
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        import traceback
        traceback.print_exc()
        return False

def verify_tables():
    """Verifica e lista todas as tabelas criadas"""
    
    print("\n📋 Verificando tabelas criadas...")
    
    try:
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        print(f"\n📊 Total de {len(tables)} tabelas no banco:")
        
        # Agrupar tabelas por categoria
        categories = {
            'Core': ['usuarios', 'empresas', 'eventos'],
            'Listas e Check-ins': ['listas', 'clientes_listas', 'checkins', 'transacoes'],
            'PDV e Vendas': ['produtos', 'categorias_produto', 'vendas', 'itens_venda', 'comandas'],
            'Financeiro': ['formas_pagamento', 'movimentos_caixa'],
            'Estoque': ['produtos_estoque', 'movimentos_estoque', 'locais_estoque', 'categorias_estoque', 
                       'alertas_estoque', 'contagens_estoque', 'itens_contagem'],
            'Automação': ['fluxos_trabalho', 'execucoes_fluxo'],
            'Integrações': ['webhooks_integracao'],
            'Soluções Online': ['solucoes_online', 'recursos_app'],
            'Tickets': ['tipos_ticket', 'lotes_ticket', 'tickets', 'transferencias_ticket'],
            'Colaboradores': ['escalas_trabalho', 'tarefas_colaborador'],
            'CRM': ['categorias_cliente', 'clientes_categorias', 'historico_categoria_cliente'],
            'Satisfação': ['pesquisas_satisfacao', 'perguntas_pesquisa', 'respostas_pesquisa', 'avaliacoes_evento'],
            'Fidelidade': ['programas_fidelidade', 'cartoes_fidelidade', 'transacoes_fidelidade', 
                          'recompensas_fidelidade', 'resgates_recompensa'],
            'Outros': ['cupons', 'gamificacao']
        }
        
        for category, expected_tables in categories.items():
            existing = [t for t in expected_tables if t in tables]
            if existing:
                print(f"\n{category}:")
                for table in existing:
                    # Contar registros se possível
                    try:
                        with engine.connect() as conn:
                            count = conn.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar()
                            print(f"   ✅ {table} ({count} registros)")
                    except:
                        print(f"   ✅ {table}")
        
        # Tabelas não categorizadas
        all_expected = []
        for tables_list in categories.values():
            all_expected.extend(tables_list)
        
        uncategorized = set(tables) - set(all_expected)
        if uncategorized:
            print("\nNão categorizadas:")
            for table in sorted(uncategorized):
                print(f"   - {table}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao verificar tabelas: {e}")
        return False

def main():
    """Função principal"""
    
    print("=" * 60)
    print("🚀 SISTEMA DE MIGRAÇÃO DE BANCO DE DADOS")
    print("=" * 60)
    
    # Verificar variável de ambiente DATABASE_URL
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        print(f"📝 Usando banco de dados: {database_url.split('@')[1] if '@' in database_url else 'local'}")
    else:
        print("📝 Usando banco de dados SQLite local")
    
    # Criar tabelas
    if create_tables():
        # Verificar resultado
        verify_tables()
        print("\n✅ Migração concluída com sucesso!")
    else:
        print("\n❌ Falha na migração. Verifique os erros acima.")
        sys.exit(1)

if __name__ == "__main__":
    main()