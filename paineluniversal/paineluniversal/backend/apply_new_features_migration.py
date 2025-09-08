"""
Script para aplicar migrações das novas funcionalidades baseadas na engenharia reversa
"""

import os
import sys
import logging
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker

# Adicionar o diretório app ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.models import Base
from app.database import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_migration():
    """Executa a migração criando todas as tabelas necessárias"""
    try:
        # Criar engine
        engine = create_engine(settings.database_url)
        
        # Inspecionar tabelas existentes
        inspector = inspect(engine)
        existing_tables = inspector.get_table_names()
        
        logger.info(f"Tabelas existentes: {len(existing_tables)}")
        logger.info(f"Tabelas: {existing_tables}")
        
        # Lista de novas tabelas a serem criadas
        new_tables = [
            'categorias_clientes',
            'clientes_categorias',
            'pesquisas_satisfacao',
            'respostas_pesquisa',
            'programas_fidelidade',
            'niveis_fidelidade',
            'participantes_fidelidade',
            'movimentacoes_pontos',
            'automacoes',
            'logs_automacao',
            'dashboards_bi',
            'widgets_bi',
            'integracoes',
            'logs_integracao',
            'configuracoes_app',
            'cardapios_digitais',
            'eventos_tickets',
            'lotes_tickets',
            'vendas_tickets',
            'cargos',
            'permissoes',
            'permissoes_cargos',
            'colaboradores',
            'mapas_operacao',
            'elementos_mapa'
        ]
        
        # Verificar quais tabelas já existem
        tables_to_create = []
        for table in new_tables:
            if table not in existing_tables:
                tables_to_create.append(table)
                logger.info(f"Tabela {table} será criada")
            else:
                logger.info(f"Tabela {table} já existe")
        
        if tables_to_create:
            logger.info(f"\nCriando {len(tables_to_create)} novas tabelas...")
            
            # Criar todas as tabelas
            Base.metadata.create_all(bind=engine, checkfirst=True)
            
            # Verificar se as tabelas foram criadas
            inspector = inspect(engine)
            new_existing_tables = inspector.get_table_names()
            
            created_tables = []
            for table in tables_to_create:
                if table in new_existing_tables:
                    created_tables.append(table)
                    logger.info(f"✓ Tabela {table} criada com sucesso")
                else:
                    logger.warning(f"✗ Falha ao criar tabela {table}")
            
            logger.info(f"\n{len(created_tables)} tabelas criadas com sucesso!")
            
            # Adicionar índices adicionais se necessário
            with engine.connect() as conn:
                # Índices para performance
                indices = [
                    "CREATE INDEX IF NOT EXISTS idx_categoria_cliente_nome ON categorias_clientes(nome)",
                    "CREATE INDEX IF NOT EXISTS idx_cliente_categoria_cliente ON clientes_categorias(cliente_id)",
                    "CREATE INDEX IF NOT EXISTS idx_pesquisa_evento ON pesquisas_satisfacao(evento_id)",
                    "CREATE INDEX IF NOT EXISTS idx_resposta_pesquisa ON respostas_pesquisa(pesquisa_id)",
                    "CREATE INDEX IF NOT EXISTS idx_participante_programa ON participantes_fidelidade(programa_id)",
                    "CREATE INDEX IF NOT EXISTS idx_movimentacao_participante ON movimentacoes_pontos(participante_id)",
                    "CREATE INDEX IF NOT EXISTS idx_automacao_status ON automacoes(status)",
                    "CREATE INDEX IF NOT EXISTS idx_integracao_tipo ON integracoes(tipo)",
                    "CREATE INDEX IF NOT EXISTS idx_evento_ticket ON eventos_tickets(evento_id)",
                    "CREATE INDEX IF NOT EXISTS idx_venda_ticket ON vendas_tickets(evento_ticket_id)",
                    "CREATE INDEX IF NOT EXISTS idx_colaborador_usuario ON colaboradores(usuario_id)",
                    "CREATE INDEX IF NOT EXISTS idx_mapa_evento ON mapas_operacao(evento_id)"
                ]
                
                for idx_sql in indices:
                    try:
                        conn.execute(text(idx_sql))
                        conn.commit()
                        logger.info(f"Índice criado: {idx_sql.split('idx_')[1].split(' ')[0]}")
                    except Exception as e:
                        logger.warning(f"Não foi possível criar índice: {e}")
                
            # Inserir dados padrão para algumas tabelas
            Session = sessionmaker(bind=engine)
            session = Session()
            
            try:
                # Verificar se já existem permissões
                from app.models import Permissao
                
                permissoes_count = session.query(Permissao).count()
                if permissoes_count == 0:
                    logger.info("\nInserindo permissões padrão...")
                    
                    modulos = [
                        'dashboard', 'eventos', 'clientes', 'categorias_clientes', 
                        'pesquisas', 'fidelidade', 'vendas', 'estoque', 'financeiro',
                        'relatorios', 'configuracoes', 'usuarios', 'automacao', 'bi',
                        'integracoes', 'tickets', 'colaboradores', 'mapa_operacao'
                    ]
                    
                    acoes = ['visualizar', 'criar', 'editar', 'deletar', 'exportar']
                    
                    for modulo in modulos:
                        for acao in acoes:
                            permissao = Permissao(
                                modulo=modulo,
                                acao=acao,
                                descricao=f"Permissão para {acao} {modulo}"
                            )
                            session.add(permissao)
                    
                    session.commit()
                    logger.info(f"✓ {len(modulos) * len(acoes)} permissões padrão criadas")
                
                # Criar cargo ADMIN padrão se não existir
                from app.models import Cargo
                
                cargo_admin = session.query(Cargo).filter_by(nome='ADMIN').first()
                if not cargo_admin:
                    cargo_admin = Cargo(
                        nome='ADMIN',
                        descricao='Administrador do sistema com acesso total',
                        nivel_hierarquia=1,
                        ativo=True
                    )
                    session.add(cargo_admin)
                    session.commit()
                    logger.info("✓ Cargo ADMIN criado")
                    
                    # Atribuir todas as permissões ao ADMIN
                    from app.models import PermissaoCargo
                    
                    todas_permissoes = session.query(Permissao).all()
                    for permissao in todas_permissoes:
                        perm_cargo = PermissaoCargo(
                            cargo_id=cargo_admin.id,
                            permissao_id=permissao.id
                        )
                        session.add(perm_cargo)
                    
                    session.commit()
                    logger.info(f"✓ {len(todas_permissoes)} permissões atribuídas ao cargo ADMIN")
                
            except Exception as e:
                logger.error(f"Erro ao inserir dados padrão: {e}")
                session.rollback()
            finally:
                session.close()
            
        else:
            logger.info("\nTodas as tabelas já existem. Nenhuma migração necessária.")
        
        return True
        
    except Exception as e:
        logger.error(f"Erro durante a migração: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

if __name__ == "__main__":
    logger.info("=== INICIANDO MIGRAÇÃO DAS NOVAS FUNCIONALIDADES ===")
    logger.info(f"Database URL: {settings.database_url}")
    
    success = run_migration()
    
    if success:
        logger.info("\n✅ MIGRAÇÃO CONCLUÍDA COM SUCESSO!")
    else:
        logger.error("\n❌ MIGRAÇÃO FALHOU!")
        sys.exit(1)