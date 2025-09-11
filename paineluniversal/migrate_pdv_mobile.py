#!/usr/bin/env python3
"""
Migração para criar tabelas do App PDV Mobile
Adiciona todas as tabelas necessárias para funcionalidade mobile com NFC
"""
import os
import sys
from pathlib import Path

# Adicionar o diretório raiz ao path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from backend.app.database import DATABASE_URL, get_db
from backend.app.models import Base
from backend.app.models_mobile import *  # Importar todos os modelos mobile
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_mobile_tables():
    """Criar tabelas específicas do app mobile"""
    try:
        logger.info("🚀 Iniciando migração do App PDV Mobile...")
        
        # Criar engine
        engine = create_engine(DATABASE_URL)
        
        # Criar todas as tabelas mobile
        logger.info("📊 Criando tabelas mobile...")
        Base.metadata.create_all(bind=engine, tables=[
            SessaoGarcom.__table__,
            ValidacaoNFCMobile.__table__,
            CategoriaMobile.__table__,
            ProdutoMobile.__table__,
            PedidoMobile.__table__,
            ItemPedidoMobile.__table__,
            ConfiguracaoMobile.__table__,
            ComandaNFC.__table__,
            LogAtividadeMobile.__table__,
            ImpressaoPedidoMobile.__table__
        ])
        
        logger.info("✅ Tabelas mobile criadas com sucesso!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro ao criar tabelas mobile: {e}")
        return False

def create_mobile_indexes():
    """Criar índices para performance"""
    try:
        logger.info("🔍 Criando índices para performance...")
        
        engine = create_engine(DATABASE_URL)
        
        with engine.connect() as conn:
            # Índices para tabelas principais
            indexes = [
                # Sessões de garçom
                "CREATE INDEX IF NOT EXISTS idx_sessoes_garcom_token ON sessoes_garcom(token_sessao);",
                "CREATE INDEX IF NOT EXISTS idx_sessoes_garcom_garcom_evento ON sessoes_garcom(garcom_id, evento_id);",
                "CREATE INDEX IF NOT EXISTS idx_sessoes_garcom_status ON sessoes_garcom(status);",
                
                # Validações NFC
                "CREATE INDEX IF NOT EXISTS idx_validacoes_nfc_uid ON validacoes_nfc_mobile(nfc_uid);",
                "CREATE INDEX IF NOT EXISTS idx_validacoes_nfc_sessao ON validacoes_nfc_mobile(sessao_id);",
                "CREATE INDEX IF NOT EXISTS idx_validacoes_nfc_timestamp ON validacoes_nfc_mobile(timestamp_validacao);",
                
                # Pedidos mobile
                "CREATE INDEX IF NOT EXISTS idx_pedidos_mobile_sessao ON pedidos_mobile(sessao_id);",
                "CREATE INDEX IF NOT EXISTS idx_pedidos_mobile_comanda ON pedidos_mobile(comanda_id);",
                "CREATE INDEX IF NOT EXISTS idx_pedidos_mobile_status ON pedidos_mobile(status);",
                "CREATE INDEX IF NOT EXISTS idx_pedidos_mobile_numero ON pedidos_mobile(numero_pedido);",
                
                # Produtos mobile
                "CREATE INDEX IF NOT EXISTS idx_produtos_mobile_categoria ON produtos_mobile(categoria_mobile_id);",
                "CREATE INDEX IF NOT EXISTS idx_produtos_mobile_produto ON produtos_mobile(produto_id);",
                "CREATE INDEX IF NOT EXISTS idx_produtos_mobile_ativo ON produtos_mobile(ativo_mobile);",
                
                # Comandas NFC
                "CREATE INDEX IF NOT EXISTS idx_comandas_nfc_uid ON comandas_nfc(nfc_uid);",
                "CREATE INDEX IF NOT EXISTS idx_comandas_nfc_comanda ON comandas_nfc(comanda_id);",
                
                # Logs de atividade
                "CREATE INDEX IF NOT EXISTS idx_logs_atividade_sessao ON logs_atividade_mobile(sessao_id);",
                "CREATE INDEX IF NOT EXISTS idx_logs_atividade_timestamp ON logs_atividade_mobile(timestamp);",
                "CREATE INDEX IF NOT EXISTS idx_logs_atividade_acao ON logs_atividade_mobile(acao);"
            ]
            
            for index_sql in indexes:
                try:
                    conn.execute(text(index_sql))
                    logger.info(f"✅ Índice criado: {index_sql.split('idx_')[1].split(' ')[0]}")
                except Exception as e:
                    logger.warning(f"⚠️ Erro ao criar índice: {e}")
            
            conn.commit()
        
        logger.info("✅ Índices criados com sucesso!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro ao criar índices: {e}")
        return False

def populate_initial_data():
    """Popular dados iniciais para o app mobile"""
    try:
        logger.info("📝 Populando dados iniciais...")
        
        from sqlalchemy.orm import sessionmaker
        engine = create_engine(DATABASE_URL)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        try:
            # Buscar eventos existentes para criar configurações mobile
            from backend.app.models import Evento
            eventos = db.query(Evento).all()
            
            for evento in eventos:
                # Criar configuração mobile padrão se não existir
                config_existente = db.query(ConfiguracaoMobile).filter(
                    ConfiguracaoMobile.evento_id == evento.id
                ).first()
                
                if not config_existente:
                    config = ConfiguracaoMobile(
                        evento_id=evento.id,
                        nfc_habilitado=True,
                        nfc_timeout_segundos=30,
                        cpf_max_tentativas=3,
                        tema_escuro=True,
                        tamanho_fonte="normal",
                        vibrar_feedback=True,
                        som_notificacao=False,
                        modo_offline=True,
                        sync_automatico=True,
                        backup_local=True,
                        valor_maximo_pedido=1000.00,
                        itens_maximos_pedido=50,
                        timeout_sessao_minutos=480,  # 8 horas
                        impressao_automatica=True,
                        impressao_duplicada=False,
                        impressao_prioritaria=False
                    )
                    db.add(config)
                    logger.info(f"✅ Configuração mobile criada para evento: {evento.nome}")
                
                # Criar categorias mobile padrão se não existirem
                categorias_existentes = db.query(CategoriaMobile).filter(
                    CategoriaMobile.evento_id == evento.id
                ).count()
                
                if categorias_existentes == 0:
                    categorias_padrao = [
                        {
                            "nome": "Bebidas",
                            "icone": "🍺",
                            "cor": "#3b82f6",
                            "ordem_exibicao": 1,
                            "destino_impressao": "bar",
                            "tempo_preparo_medio": 5
                        },
                        {
                            "nome": "Drinks",
                            "icone": "🍹",
                            "cor": "#ec4899",
                            "ordem_exibicao": 2,
                            "destino_impressao": "bar",
                            "tempo_preparo_medio": 8
                        },
                        {
                            "nome": "Petiscos",
                            "icone": "🍟",
                            "cor": "#f59e0b",
                            "ordem_exibicao": 3,
                            "destino_impressao": "cozinha",
                            "tempo_preparo_medio": 15
                        },
                        {
                            "nome": "Pratos",
                            "icone": "🍖",
                            "cor": "#10b981",
                            "ordem_exibicao": 4,
                            "destino_impressao": "cozinha",
                            "tempo_preparo_medio": 25
                        },
                        {
                            "nome": "Narguilé",
                            "icone": "💨",
                            "cor": "#8b5cf6",
                            "ordem_exibicao": 5,
                            "destino_impressao": "narguile",
                            "tempo_preparo_medio": 10
                        },
                        {
                            "nome": "Sobremesas",
                            "icone": "🍰",
                            "cor": "#f43f5e",
                            "ordem_exibicao": 6,
                            "destino_impressao": "sobremesa",
                            "tempo_preparo_medio": 12
                        },
                        {
                            "nome": "Especiais",
                            "icone": "⭐",
                            "cor": "#6366f1",
                            "ordem_exibicao": 7,
                            "destino_impressao": "cozinha",
                            "tempo_preparo_medio": 20
                        },
                        {
                            "nome": "Promoções",
                            "icone": "🔥",
                            "cor": "#ef4444",
                            "ordem_exibicao": 8,
                            "destino_impressao": "bar",
                            "tempo_preparo_medio": 10
                        }
                    ]
                    
                    for cat_data in categorias_padrao:
                        categoria = CategoriaMobile(
                            evento_id=evento.id,
                            **cat_data
                        )
                        db.add(categoria)
                    
                    logger.info(f"✅ Categorias mobile criadas para evento: {evento.nome}")
            
            db.commit()
            logger.info("✅ Dados iniciais populados com sucesso!")
            
        finally:
            db.close()
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro ao popular dados iniciais: {e}")
        return False

def verify_migration():
    """Verificar se a migração foi bem-sucedida"""
    try:
        logger.info("🔍 Verificando migração...")
        
        engine = create_engine(DATABASE_URL)
        
        # Verificar se as tabelas foram criadas
        tabelas_mobile = [
            'sessoes_garcom',
            'validacoes_nfc_mobile', 
            'categorias_mobile',
            'produtos_mobile',
            'pedidos_mobile',
            'itens_pedido_mobile',
            'configuracoes_mobile',
            'comandas_nfc',
            'logs_atividade_mobile',
            'impressoes_pedido_mobile'
        ]
        
        with engine.connect() as conn:
            for tabela in tabelas_mobile:
                result = conn.execute(text(f"""
                    SELECT COUNT(*) 
                    FROM information_schema.tables 
                    WHERE table_name = '{tabela}'
                """))
                
                count = result.scalar()
                if count > 0:
                    logger.info(f"✅ Tabela {tabela} criada com sucesso")
                else:
                    logger.error(f"❌ Tabela {tabela} não encontrada")
                    return False
        
        logger.info("✅ Verificação de migração concluída com sucesso!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro na verificação da migração: {e}")
        return False

def main():
    """Executar migração completa"""
    logger.info("🚀 MIGRAÇÃO APP PDV MOBILE - INICIANDO")
    logger.info("=" * 60)
    
    success = True
    
    # Passo 1: Criar tabelas
    if not create_mobile_tables():
        success = False
    
    # Passo 2: Criar índices
    if success and not create_mobile_indexes():
        success = False
    
    # Passo 3: Popular dados iniciais
    if success and not populate_initial_data():
        success = False
    
    # Passo 4: Verificar migração
    if success and not verify_migration():
        success = False
    
    if success:
        logger.info("=" * 60)
        logger.info("🎉 MIGRAÇÃO CONCLUÍDA COM SUCESSO!")
        logger.info("📱 App PDV Mobile pronto para uso")
        logger.info("=" * 60)
    else:
        logger.error("=" * 60)
        logger.error("❌ MIGRAÇÃO FALHOU!")
        logger.error("Verifique os logs acima para detalhes")
        logger.error("=" * 60)
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
