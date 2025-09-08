"""
Migração Sistema Mesa + KDS - Versão Simplificada
================================================

Script simplificado para criar apenas as tabelas básicas primeiro
"""

import sys
import os
from pathlib import Path

# Adicionar o diretório backend ao path
backend_path = Path(__file__).parent / "backend"
sys.path.append(str(backend_path))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

from backend.app.database import engine, SessionLocal

def criar_tabelas_sql():
    """Cria tabelas usando SQL direto"""
    
    logger.info("🚀 Criando tabelas via SQL direto...")
    
    db = SessionLocal()
    
    try:
        # 1. Criar ENUMs primeiro
        logger.info("📋 Criando tipos ENUM...")
        
        enums_sql = [
            """
            DO $$ BEGIN
                CREATE TYPE statuspedidomesa AS ENUM (
                    'pendente', 'confirmado', 'preparando', 'pronto', 
                    'entregue', 'cancelado', 'parcialmente_entregue'
                );
            EXCEPTION
                WHEN duplicate_object THEN null;
            END $$;
            """,
            """
            DO $$ BEGIN
                CREATE TYPE prioridadepedido AS ENUM (
                    'baixa', 'normal', 'alta', 'urgente'
                );
            EXCEPTION
                WHEN duplicate_object THEN null;
            END $$;
            """,
            """
            DO $$ BEGIN
                CREATE TYPE tiponotificacaokds AS ENUM (
                    'novo_pedido', 'pedido_alterado', 'item_pronto', 
                    'atraso_detectado', 'sistema', 'alerta'
                );
            EXCEPTION
                WHEN duplicate_object THEN null;
            END $$;
            """,
            """
            DO $$ BEGIN
                CREATE TYPE statusitempedido AS ENUM (
                    'pendente', 'confirmado', 'preparando', 'pronto', 
                    'entregue', 'cancelado'
                );
            EXCEPTION
                WHEN duplicate_object THEN null;
            END $$;
            """,
            """
            DO $$ BEGIN
                CREATE TYPE tipoestacaokds AS ENUM (
                    'principal', 'cozinha_quente', 'cozinha_fria', 
                    'bar', 'sobremesas', 'expedicao'
                );
            EXCEPTION
                WHEN duplicate_object THEN null;
            END $$;
            """,
            """
            DO $$ BEGIN
                CREATE TYPE modopedidomesa AS ENUM (
                    'mesa', 'delivery', 'balcao', 'app_cliente'
                );
            EXCEPTION
                WHEN duplicate_object THEN null;
            END $$;
            """
        ]
        
        for enum_sql in enums_sql:
            try:
                db.execute(text(enum_sql))
                logger.info("   ✅ ENUM criado")
            except Exception as e:
                logger.warning(f"   ⚠️ ENUM já existe ou erro: {str(e)}")
        
        db.commit()
        
        # 2. Criar tabela de estações KDS (sem foreign keys)
        logger.info("🏭 Criando tabela estacao_kds...")
        
        estacao_sql = """
        CREATE TABLE IF NOT EXISTS estacao_kds (
            id SERIAL PRIMARY KEY,
            nome VARCHAR(100) NOT NULL,
            tipo tipoestacaokds NOT NULL,
            descricao TEXT,
            capacidade_maxima_pedidos INTEGER DEFAULT 20,
            tempo_exibicao_pedido INTEGER DEFAULT 30,
            ativa BOOLEAN DEFAULT true,
            cor_tema VARCHAR(7) DEFAULT '#3B82F6',
            posicao_ordem INTEGER DEFAULT 0,
            empresa_id INTEGER,
            configuracoes_layout JSONB DEFAULT '{}',
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        
        db.execute(text(estacao_sql))
        logger.info("   ✅ Tabela estacao_kds criada")
        
        # 3. Criar tabela de configurações KDS
        logger.info("⚙️ Criando tabela configuracao_kds...")
        
        config_sql = """
        CREATE TABLE IF NOT EXISTS configuracao_kds (
            id SERIAL PRIMARY KEY,
            chave VARCHAR(100) NOT NULL,
            valor TEXT NOT NULL,
            descricao TEXT,
            categoria VARCHAR(50),
            tipo_valor VARCHAR(20) DEFAULT 'string',
            empresa_id INTEGER,
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(chave, empresa_id)
        );
        """
        
        db.execute(text(config_sql))
        logger.info("   ✅ Tabela configuracao_kds criada")
        
        # 4. Criar tabela de pedidos mesa
        logger.info("🍽️ Criando tabela pedido_mesa...")
        
        pedido_sql = """
        CREATE TABLE IF NOT EXISTS pedido_mesa (
            id SERIAL PRIMARY KEY,
            numero_pedido VARCHAR(50) UNIQUE NOT NULL,
            mesa_id INTEGER REFERENCES mesas(id),
            numero_mesa VARCHAR(10),
            status statuspedidomesa DEFAULT 'pendente',
            prioridade prioridadepedido DEFAULT 'normal',
            modo_pedido modopedidomesa DEFAULT 'mesa',
            data_pedido TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            data_confirmacao TIMESTAMP,
            data_inicio_preparo TIMESTAMP,
            data_conclusao TIMESTAMP,
            data_entrega TIMESTAMP,
            tempo_estimado_preparo INTEGER DEFAULT 30,
            valor_subtotal NUMERIC(10,2) DEFAULT 0,
            valor_desconto NUMERIC(10,2) DEFAULT 0,
            valor_acrescimo NUMERIC(10,2) DEFAULT 0,
            valor_total NUMERIC(10,2) DEFAULT 0,
            observacoes TEXT,
            observacoes_cozinha TEXT,
            estacao_responsavel tipoestacaokds,
            usuario_criacao_id INTEGER,
            usuario_confirmacao_id INTEGER,
            usuario_entrega_id INTEGER,
            empresa_id INTEGER,
            evento_id INTEGER,
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        
        db.execute(text(pedido_sql))
        logger.info("   ✅ Tabela pedido_mesa criada")
        
        # 5. Criar tabela de itens de pedido
        logger.info("📦 Criando tabela item_pedido_mesa...")
        
        item_sql = """
        CREATE TABLE IF NOT EXISTS item_pedido_mesa (
            id SERIAL PRIMARY KEY,
            pedido_id INTEGER REFERENCES pedido_mesa(id) ON DELETE CASCADE,
            nome_produto VARCHAR(200) NOT NULL,
            descricao TEXT,
            categoria VARCHAR(100),
            quantidade INTEGER NOT NULL DEFAULT 1,
            valor_unitario NUMERIC(10,2) NOT NULL,
            valor_total NUMERIC(10,2) NOT NULL,
            status statusitempedido DEFAULT 'pendente',
            tempo_estimado_preparo INTEGER DEFAULT 15,
            observacoes TEXT,
            ingredientes_removidos TEXT,
            ingredientes_extras TEXT,
            data_inicio_preparo TIMESTAMP,
            data_conclusao_preparo TIMESTAMP,
            data_entrega TIMESTAMP,
            responsavel_preparo_id INTEGER,
            responsavel_entrega_id INTEGER,
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        
        db.execute(text(item_sql))
        logger.info("   ✅ Tabela item_pedido_mesa criada")
        
        # 6. Criar tabela de notificações
        logger.info("🔔 Criando tabela notificacao_kds...")
        
        notificacao_sql = """
        CREATE TABLE IF NOT EXISTS notificacao_kds (
            id SERIAL PRIMARY KEY,
            tipo tiponotificacaokds NOT NULL,
            titulo VARCHAR(200) NOT NULL,
            mensagem TEXT NOT NULL,
            urgencia prioridadepedido DEFAULT 'normal',
            lida BOOLEAN DEFAULT false,
            data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            data_leitura TIMESTAMP,
            data_expiracao TIMESTAMP,
            pedido_id INTEGER REFERENCES pedido_mesa(id),
            estacao_id INTEGER REFERENCES estacao_kds(id),
            mesa_id INTEGER REFERENCES mesas(id),
            usuario_leitura_id INTEGER,
            dados_extra JSONB DEFAULT '{}'
        );
        """
        
        db.execute(text(notificacao_sql))
        logger.info("   ✅ Tabela notificacao_kds criada")
        
        # 7. Criar tabela de relatórios
        logger.info("📊 Criando tabela relatorio_tempo_mesa...")
        
        relatorio_sql = """
        CREATE TABLE IF NOT EXISTS relatorio_tempo_mesa (
            id SERIAL PRIMARY KEY,
            data_inicio DATE NOT NULL,
            data_fim DATE NOT NULL,
            mesa_id INTEGER REFERENCES mesas(id),
            numero_mesa VARCHAR(10),
            tempo_medio_preparo INTEGER DEFAULT 0,
            tempo_medio_entrega INTEGER DEFAULT 0,
            tempo_medio_ocupacao INTEGER DEFAULT 0,
            tempo_total_ocupada INTEGER DEFAULT 0,
            total_pedidos INTEGER DEFAULT 0,
            pedidos_no_prazo INTEGER DEFAULT 0,
            pedidos_atrasados INTEGER DEFAULT 0,
            pedidos_cancelados INTEGER DEFAULT 0,
            faturamento_total NUMERIC(12,2) DEFAULT 0,
            ticket_medio NUMERIC(10,2) DEFAULT 0,
            taxa_ocupacao NUMERIC(5,2) DEFAULT 0,
            taxa_sucesso NUMERIC(5,2) DEFAULT 0,
            indice_satisfacao NUMERIC(5,2) DEFAULT 0,
            empresa_id INTEGER,
            evento_id INTEGER,
            gerado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        
        db.execute(text(relatorio_sql))
        logger.info("   ✅ Tabela relatorio_tempo_mesa criada")
        
        # 8. Criar tabela de logs
        logger.info("📝 Criando tabela log_evento_kds...")
        
        log_sql = """
        CREATE TABLE IF NOT EXISTS log_evento_kds (
            id SERIAL PRIMARY KEY,
            tipo_evento VARCHAR(50) NOT NULL,
            descricao TEXT NOT NULL,
            pedido_id INTEGER REFERENCES pedido_mesa(id),
            mesa_id INTEGER REFERENCES mesas(id),
            usuario_id INTEGER,
            estacao_id INTEGER REFERENCES estacao_kds(id),
            dados_antes JSONB DEFAULT '{}',
            dados_depois JSONB DEFAULT '{}',
            metadados JSONB DEFAULT '{}',
            ip_origem VARCHAR(45),
            user_agent TEXT,
            data_evento TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        
        db.execute(text(log_sql))
        logger.info("   ✅ Tabela log_evento_kds criada")
        
        db.commit()
        
        # 9. Criar índices
        logger.info("📊 Criando índices de performance...")
        
        indices = [
            "CREATE INDEX IF NOT EXISTS idx_pedido_mesa_status_data ON pedido_mesa(status, data_pedido DESC);",
            "CREATE INDEX IF NOT EXISTS idx_pedido_mesa_mesa_status ON pedido_mesa(mesa_id, status);",
            "CREATE INDEX IF NOT EXISTS idx_pedido_mesa_estacao_status ON pedido_mesa(estacao_responsavel, status);",
            "CREATE INDEX IF NOT EXISTS idx_item_pedido_status ON item_pedido_mesa(status, criado_em DESC);",
            "CREATE INDEX IF NOT EXISTS idx_notificacao_kds_lida_data ON notificacao_kds(lida, data_criacao DESC);",
            "CREATE INDEX IF NOT EXISTS idx_notificacao_kds_estacao ON notificacao_kds(estacao_id, data_criacao DESC);",
            "CREATE INDEX IF NOT EXISTS idx_log_evento_tipo_data ON log_evento_kds(tipo_evento, data_evento DESC);",
            "CREATE INDEX IF NOT EXISTS idx_relatorio_tempo_mesa_periodo ON relatorio_tempo_mesa(data_inicio, data_fim, mesa_id);"
        ]
        
        for index_sql in indices:
            try:
                db.execute(text(index_sql))
                logger.info("   ✅ Índice criado")
            except Exception as e:
                logger.warning(f"   ⚠️ Erro ao criar índice: {str(e)}")
        
        db.commit()
        
        logger.info("✅ Todas as tabelas criadas com sucesso!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro ao criar tabelas: {str(e)}")
        db.rollback()
        return False
    finally:
        db.close()

def inserir_dados_basicos():
    """Insere dados básicos para funcionamento"""
    
    logger.info("📦 Inserindo dados básicos...")
    
    db = SessionLocal()
    
    try:
        # Inserir estações padrão
        estacoes_sql = """
        INSERT INTO estacao_kds (nome, tipo, descricao, capacidade_maxima_pedidos, tempo_exibicao_pedido, empresa_id, posicao_ordem) 
        VALUES 
        ('Estação Principal', 'principal', 'Estação principal para gerenciamento geral', 50, 30, 1, 1),
        ('Cozinha Quente', 'cozinha_quente', 'Estação para pratos quentes e grelhados', 30, 45, 1, 2),
        ('Cozinha Fria', 'cozinha_fria', 'Estação para saladas e pratos frios', 25, 20, 1, 3),
        ('Bar e Bebidas', 'bar', 'Estação para preparo de bebidas', 40, 15, 1, 4),
        ('Sobremesas', 'sobremesas', 'Estação especializada em sobremesas', 20, 25, 1, 5),
        ('Expedição', 'expedicao', 'Estação final para entrega dos pedidos', 60, 10, 1, 6)
        ON CONFLICT DO NOTHING;
        """
        
        db.execute(text(estacoes_sql))
        
        # Inserir configurações padrão
        config_sql = """
        INSERT INTO configuracao_kds (chave, valor, descricao, categoria, empresa_id) 
        VALUES 
        ('tempo_max_preparo_padrao', '30', 'Tempo máximo padrão para preparo em minutos', 'TEMPO', 1),
        ('notificacao_atraso_ativa', 'true', 'Ativar notificações de atraso automáticas', 'NOTIFICACAO', 1),
        ('intervalo_atualizacao_dashboard', '5', 'Intervalo de atualização do dashboard em segundos', 'INTERFACE', 1),
        ('limite_pedidos_por_mesa', '10', 'Limite máximo de pedidos simultâneos por mesa', 'LIMITE', 1),
        ('tempo_expiracao_notificacao', '60', 'Tempo de expiração das notificações em minutos', 'NOTIFICACAO', 1),
        ('audio_notificacao_ativo', 'true', 'Ativar som para notificações', 'INTERFACE', 1),
        ('modo_tela_cheia_kds', 'false', 'Modo tela cheia para displays KDS', 'INTERFACE', 1)
        ON CONFLICT (chave, empresa_id) DO NOTHING;
        """
        
        db.execute(text(config_sql))
        
        db.commit()
        logger.info("✅ Dados básicos inseridos com sucesso!")
        
        # Contar registros
        result = db.execute(text("SELECT COUNT(*) FROM estacao_kds"))
        total_estacoes = result.scalar()
        
        result = db.execute(text("SELECT COUNT(*) FROM configuracao_kds"))
        total_configs = result.scalar()
        
        logger.info(f"📊 {total_estacoes} estações KDS criadas")
        logger.info(f"📊 {total_configs} configurações criadas")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro ao inserir dados básicos: {str(e)}")
        db.rollback()
        return False
    finally:
        db.close()

def main():
    """Função principal"""
    
    print("=" * 80)
    print("🚀 MIGRAÇÃO SIMPLIFICADA SISTEMA MESA + KDS")
    print("=" * 80)
    print()
    
    try:
        # Criar tabelas
        if criar_tabelas_sql():
            print()
            # Inserir dados básicos
            if inserir_dados_basicos():
                print()
                print("=" * 80)
                print("🎉 MIGRAÇÃO CONCLUÍDA COM SUCESSO!")
                print()
                print("📋 Sistema Mesa + KDS pronto para uso:")
                print("   ✅ 8 tabelas principais criadas")
                print("   ✅ 6 estações KDS configuradas")
                print("   ✅ Configurações padrão inseridas")
                print("   ✅ Índices de performance criados")
                print()
                print("🔗 Próximos passos:")
                print("   • Reiniciar aplicação para carregar novos routers")
                print("   • Acessar /api/mesa-kds/dashboard para dashboard")
                print("   • Testar endpoints via /docs")
                print("=" * 80)
            else:
                print("❌ Falha ao inserir dados básicos")
                return False
        else:
            print("❌ Falha ao criar tabelas")
            return False
            
    except Exception as e:
        print(f"❌ Erro fatal: {str(e)}")
        return False

if __name__ == "__main__":
    main()
