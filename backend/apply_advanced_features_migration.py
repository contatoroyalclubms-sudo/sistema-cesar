#!/usr/bin/env python3
"""
Script para aplicar migrações das funcionalidades avançadas no banco de dados
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from app.database import engine
from app.models import Base
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_advanced_tables():
    """Cria as novas tabelas avançadas no banco de dados"""
    
    try:
        # Criar todas as tabelas definidas nos modelos
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Tabelas base criadas/atualizadas com sucesso")
        
        # Adicionar índices extras para performance
        with engine.connect() as conn:
            # Índices para Workspace
            indices = [
                "CREATE INDEX IF NOT EXISTS idx_workspaces_slug ON workspaces(slug);",
                "CREATE INDEX IF NOT EXISTS idx_workspaces_ativo ON workspaces(ativo);",
                
                # Índices para UsuarioWorkspace
                "CREATE INDEX IF NOT EXISTS idx_usuarios_workspaces_usuario ON usuarios_workspaces(usuario_id);",
                "CREATE INDEX IF NOT EXISTS idx_usuarios_workspaces_workspace ON usuarios_workspaces(workspace_id);",
                "CREATE INDEX IF NOT EXISTS idx_usuarios_workspaces_padrao ON usuarios_workspaces(workspace_padrao);",
                
                # Índices para EventoRecorrencia
                "CREATE INDEX IF NOT EXISTS idx_eventos_recorrencia_evento ON eventos_recorrencia(evento_pai_id);",
                "CREATE INDEX IF NOT EXISTS idx_eventos_recorrencia_ativo ON eventos_recorrencia(ativo);",
                
                # Índices para FilaVirtual
                "CREATE INDEX IF NOT EXISTS idx_filas_virtuais_evento ON filas_virtuais(evento_id);",
                "CREATE INDEX IF NOT EXISTS idx_filas_virtuais_ativa ON filas_virtuais(ativa);",
                
                # Índices para ParticipanteFila
                "CREATE INDEX IF NOT EXISTS idx_participantes_fila_fila ON participantes_fila(fila_id);",
                "CREATE INDEX IF NOT EXISTS idx_participantes_fila_cpf ON participantes_fila(cpf);",
                "CREATE INDEX IF NOT EXISTS idx_participantes_fila_status ON participantes_fila(status);",
                
                # Índices para EventoAnalytics
                "CREATE INDEX IF NOT EXISTS idx_eventos_analytics_evento ON eventos_analytics(evento_id);",
                "CREATE INDEX IF NOT EXISTS idx_eventos_analytics_data ON eventos_analytics(data_analise);",
                
                # Índices para CampanhaMarketing
                "CREATE INDEX IF NOT EXISTS idx_campanhas_marketing_evento ON campanhas_marketing(evento_id);",
                "CREATE INDEX IF NOT EXISTS idx_campanhas_marketing_workspace ON campanhas_marketing(workspace_id);",
                "CREATE INDEX IF NOT EXISTS idx_campanhas_marketing_status ON campanhas_marketing(status);",
                
                # Índices para AuditLog
                "CREATE INDEX IF NOT EXISTS idx_audit_logs_usuario ON audit_logs(usuario_id);",
                "CREATE INDEX IF NOT EXISTS idx_audit_logs_workspace ON audit_logs(workspace_id);",
                "CREATE INDEX IF NOT EXISTS idx_audit_logs_entidade ON audit_logs(entidade);",
                "CREATE INDEX IF NOT EXISTS idx_audit_logs_acao ON audit_logs(acao);",
                "CREATE INDEX IF NOT EXISTS idx_audit_logs_criado ON audit_logs(criado_em);",
                
                # Índices para TransferenciaIngresso
                "CREATE INDEX IF NOT EXISTS idx_transferencias_ingresso_transacao ON transferencias_ingresso(transacao_original_id);",
                "CREATE INDEX IF NOT EXISTS idx_transferencias_ingresso_codigo ON transferencias_ingresso(codigo_autorizacao);",
                
                # Índices para Anuncio
                "CREATE INDEX IF NOT EXISTS idx_anuncios_evento ON anuncios(evento_id);",
                "CREATE INDEX IF NOT EXISTS idx_anuncios_workspace ON anuncios(workspace_id);",
                "CREATE INDEX IF NOT EXISTS idx_anuncios_ativo ON anuncios(ativo);",
                
                # Índices para ListaEspera
                "CREATE INDEX IF NOT EXISTS idx_listas_espera_evento ON listas_espera(evento_id);",
                "CREATE INDEX IF NOT EXISTS idx_listas_espera_lista ON listas_espera(lista_id);",
                "CREATE INDEX IF NOT EXISTS idx_listas_espera_cpf ON listas_espera(cpf);",
                "CREATE INDEX IF NOT EXISTS idx_listas_espera_convertido ON listas_espera(convertido);",
                
                # Índices para NetworkingPerfil
                "CREATE INDEX IF NOT EXISTS idx_networking_perfis_usuario ON networking_perfis(usuario_id);",
                "CREATE INDEX IF NOT EXISTS idx_networking_perfis_evento ON networking_perfis(evento_id);",
                "CREATE INDEX IF NOT EXISTS idx_networking_perfis_disponivel ON networking_perfis(disponivel_networking);",
                
                # Índices para NetworkingConexao
                "CREATE INDEX IF NOT EXISTS idx_networking_conexoes_evento ON networking_conexoes(evento_id);",
                "CREATE INDEX IF NOT EXISTS idx_networking_conexoes_origem ON networking_conexoes(perfil_origem_id);",
                "CREATE INDEX IF NOT EXISTS idx_networking_conexoes_destino ON networking_conexoes(perfil_destino_id);",
                
                # Índices para EventoOnline
                "CREATE INDEX IF NOT EXISTS idx_eventos_online_evento ON eventos_online(evento_id);"
            ]
            
            for idx_sql in indices:
                try:
                    conn.execute(text(idx_sql))
                    conn.commit()
                except Exception as e:
                    logger.warning(f"Aviso ao criar índice: {e}")
            
            logger.info("✅ Índices de performance criados")
    
    except Exception as e:
        logger.error(f"❌ Erro ao criar tabelas: {e}")
        raise

def add_workspace_to_existing_tables():
    """Adiciona campo workspace_id às tabelas existentes que precisam"""
    
    try:
        with engine.connect() as conn:
            # Adicionar workspace_id onde necessário
            alter_statements = [
                # Adicionar workspace_id ao Evento (se ainda não tiver)
                """
                ALTER TABLE eventos 
                ADD COLUMN IF NOT EXISTS workspace_id INTEGER 
                REFERENCES workspaces(id);
                """,
                
                # Adicionar workspace_id ao Produto (se ainda não tiver)
                """
                ALTER TABLE produtos 
                ADD COLUMN IF NOT EXISTS workspace_id INTEGER 
                REFERENCES workspaces(id);
                """,
                
                # Adicionar workspace_id às Transações
                """
                ALTER TABLE transacoes 
                ADD COLUMN IF NOT EXISTS workspace_id INTEGER 
                REFERENCES workspaces(id);
                """,
                
                # Adicionar workspace_id ao VendaPDV
                """
                ALTER TABLE vendas_pdv 
                ADD COLUMN IF NOT EXISTS workspace_id INTEGER 
                REFERENCES workspaces(id);
                """
            ]
            
            for stmt in alter_statements:
                try:
                    conn.execute(text(stmt))
                    conn.commit()
                except Exception as e:
                    logger.warning(f"Aviso ao adicionar workspace_id: {e}")
            
            logger.info("✅ Campos workspace_id adicionados onde necessário")
    
    except Exception as e:
        logger.error(f"❌ Erro ao adicionar campos workspace: {e}")

def create_default_workspace():
    """Cria workspace padrão para dados existentes"""
    
    try:
        from app.models import Workspace, UsuarioWorkspace, Usuario
        from app.database import SessionLocal
        
        db = SessionLocal()
        
        # Verificar se já existe workspace padrão
        default_workspace = db.query(Workspace).filter(Workspace.slug == "default").first()
        
        if not default_workspace:
            # Criar workspace padrão
            default_workspace = Workspace(
                nome="Workspace Principal",
                slug="default",
                plano="pro",
                limite_usuarios=100,
                limite_eventos=1000,
                limite_vendas_mes=50000,
                features_habilitadas='["eventos", "checkin", "pdv", "relatorios", "analytics", "marketing", "filas", "networking"]',
                configuracoes='{}',
                ativo=True
            )
            db.add(default_workspace)
            db.flush()
            
            # Associar todos os usuários admin ao workspace padrão
            admins = db.query(Usuario).filter(Usuario.tipo == "admin").all()
            
            for admin in admins:
                user_workspace = UsuarioWorkspace(
                    usuario_id=admin.id,
                    workspace_id=default_workspace.id,
                    papel="owner" if admins.index(admin) == 0 else "admin",
                    permissoes='["*"]',
                    workspace_padrao=True
                )
                db.add(user_workspace)
            
            db.commit()
            logger.info(f"✅ Workspace padrão criado: {default_workspace.slug}")
            
            # Atualizar registros existentes para usar workspace padrão
            with engine.connect() as conn:
                updates = [
                    f"UPDATE empresas SET workspace_id = {default_workspace.id} WHERE workspace_id IS NULL;",
                    f"UPDATE eventos SET workspace_id = {default_workspace.id} WHERE workspace_id IS NULL;",
                    f"UPDATE produtos SET workspace_id = {default_workspace.id} WHERE workspace_id IS NULL;"
                ]
                
                for update in updates:
                    try:
                        conn.execute(text(update))
                        conn.commit()
                    except Exception as e:
                        logger.warning(f"Aviso ao atualizar workspace_id: {e}")
        
        else:
            logger.info("✅ Workspace padrão já existe")
        
        db.close()
    
    except Exception as e:
        logger.error(f"❌ Erro ao criar workspace padrão: {e}")

def add_sample_data():
    """Adiciona dados de exemplo para teste"""
    
    try:
        from app.models import FilaVirtual, Evento
        from app.database import SessionLocal
        from datetime import datetime, timedelta
        
        db = SessionLocal()
        
        # Buscar um evento para teste
        evento = db.query(Evento).first()
        
        if evento:
            # Verificar se já existe fila de exemplo
            fila_exemplo = db.query(FilaVirtual).filter(
                FilaVirtual.nome == "Fila de Credenciamento"
            ).first()
            
            if not fila_exemplo:
                # Criar fila de exemplo
                fila_exemplo = FilaVirtual(
                    evento_id=evento.id,
                    nome="Fila de Credenciamento",
                    descricao="Fila para retirada de credenciais",
                    capacidade_maxima=100,
                    tempo_estimado_atendimento=3,
                    prioridade_habilitada=True,
                    ativa=True,
                    qr_code_acesso="FILA_CRED_001"
                )
                db.add(fila_exemplo)
                db.commit()
                logger.info("✅ Dados de exemplo criados")
            else:
                logger.info("✅ Dados de exemplo já existem")
        
        db.close()
    
    except Exception as e:
        logger.warning(f"Aviso ao criar dados de exemplo: {e}")

def main():
    """Executa todas as migrações"""
    
    logger.info("🚀 Iniciando migração de funcionalidades avançadas...")
    
    # 1. Criar novas tabelas
    logger.info("\n1️⃣ Criando novas tabelas...")
    create_advanced_tables()
    
    # 2. Adicionar workspace_id às tabelas existentes
    logger.info("\n2️⃣ Adicionando suporte a workspace...")
    add_workspace_to_existing_tables()
    
    # 3. Criar workspace padrão
    logger.info("\n3️⃣ Criando workspace padrão...")
    create_default_workspace()
    
    # 4. Adicionar dados de exemplo
    logger.info("\n4️⃣ Adicionando dados de exemplo...")
    add_sample_data()
    
    logger.info("\n✅ Migração concluída com sucesso!")
    logger.info("\n📝 Novas funcionalidades disponíveis:")
    logger.info("  - Sistema de Workspaces (Multi-tenant)")
    logger.info("  - Eventos Recorrentes")
    logger.info("  - Filas Virtuais")
    logger.info("  - Analytics Avançado")
    logger.info("  - Campanhas de Marketing")
    logger.info("  - Audit Trail Completo")
    logger.info("  - Transferência de Ingressos")
    logger.info("  - Sistema de Anúncios")
    logger.info("  - Lista de Espera")
    logger.info("  - Networking para Eventos")
    logger.info("  - Eventos Online/Híbridos")
    
    logger.info("\n🔗 Endpoints disponíveis:")
    logger.info("  - /api/workspaces")
    logger.info("  - /api/eventos/recorrencia")
    logger.info("  - /api/filas")
    logger.info("  - /api/analytics")
    logger.info("  - /api/campanhas")
    logger.info("  - /api/audit")
    logger.info("  - /api/transferencias")
    logger.info("  - /api/anuncios")
    logger.info("  - /api/lista-espera")
    logger.info("  - /api/networking")
    logger.info("  - /api/eventos-online")

if __name__ == "__main__":
    main()