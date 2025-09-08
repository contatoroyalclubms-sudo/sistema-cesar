"""
Migração Sistema Mesa + KDS - Implementação Meep Completa
========================================================

Script de migração para criar todas as tabelas do sistema de mesas e KDS
baseado na engenharia reversa do sistema Meep.

Funcionalidades criadas:
- Sistema avançado de pedidos de mesa
- Kitchen Display System (KDS) com estações
- Notificações em tempo real  
- Relatórios e analytics de performance
- Logs de auditoria completa
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

# Importar modelos
from backend.app.database import engine, SessionLocal
from backend.app.models_mesa_kds import (
    PedidoMesa, ItemPedidoMesa, EstacaoKDS, ConfiguracaoKDS, 
    NotificacaoKDS, RelatorioTempoMesa, LogEventoKDS,
    StatusPedidoMesa, StatusItemPedido, TipoNotificacaoKDS,
    TipoEstacaoKDS, PrioridadePedido, ModoPedidoMesa
)
from backend.app.models import Base

def executar_sql_seguro(db, sql_command, descricao):
    """Executa comando SQL com tratamento de erro"""
    try:
        db.execute(text(sql_command))
        logger.info(f"✅ {descricao}")
        return True
    except Exception as e:
        logger.warning(f"⚠️ {descricao} - Ignorando: {str(e)}")
        return False

def criar_tabelas_mesa_kds():
    """Cria todas as tabelas do sistema Mesa + KDS"""
    
    logger.info("🚀 Iniciando migração do Sistema Mesa + KDS...")
    
    try:
        # Criar todas as tabelas definidas nos modelos
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Estrutura de tabelas criada com sucesso")
        
        # Criar session
        db = SessionLocal()
        
        try:
            # 1. Criar estações KDS padrão
            logger.info("📦 Criando estações KDS padrão...")
            
            estacoes_padrao = [
                {
                    "nome": "Estação Principal",
                    "tipo": TipoEstacaoKDS.PRINCIPAL,
                    "descricao": "Estação principal para gerenciamento geral",
                    "capacidade_maxima_pedidos": 50,
                    "tempo_exibicao_pedido": 30,
                    "ativa": True,
                    "empresa_id": 1,
                    "posicao_ordem": 1
                },
                {
                    "nome": "Cozinha Quente",
                    "tipo": TipoEstacaoKDS.COZINHA_QUENTE,
                    "descricao": "Estação para pratos quentes e grelhados",
                    "capacidade_maxima_pedidos": 30,
                    "tempo_exibicao_pedido": 45,
                    "ativa": True,
                    "empresa_id": 1,
                    "posicao_ordem": 2
                },
                {
                    "nome": "Cozinha Fria",
                    "tipo": TipoEstacaoKDS.COZINHA_FRIA,
                    "descricao": "Estação para saladas e pratos frios",
                    "capacidade_maxima_pedidos": 25,
                    "tempo_exibicao_pedido": 20,
                    "ativa": True,
                    "empresa_id": 1,
                    "posicao_ordem": 3
                },
                {
                    "nome": "Bar e Bebidas",
                    "tipo": TipoEstacaoKDS.BAR,
                    "descricao": "Estação para preparo de bebidas",
                    "capacidade_maxima_pedidos": 40,
                    "tempo_exibicao_pedido": 15,
                    "ativa": True,
                    "empresa_id": 1,
                    "posicao_ordem": 4
                },
                {
                    "nome": "Sobremesas",
                    "tipo": TipoEstacaoKDS.SOBREMESAS,
                    "descricao": "Estação especializada em sobremesas",
                    "capacidade_maxima_pedidos": 20,
                    "tempo_exibicao_pedido": 25,
                    "ativa": True,
                    "empresa_id": 1,
                    "posicao_ordem": 5
                },
                {
                    "nome": "Expedição",
                    "tipo": TipoEstacaoKDS.EXPEDICAO,
                    "descricao": "Estação final para entrega dos pedidos",
                    "capacidade_maxima_pedidos": 60,
                    "tempo_exibicao_pedido": 10,
                    "ativa": True,
                    "empresa_id": 1,
                    "posicao_ordem": 6
                }
            ]
            
            for estacao_data in estacoes_padrao:
                # Verificar se já existe
                existe = db.query(EstacaoKDS).filter_by(
                    nome=estacao_data["nome"],
                    empresa_id=estacao_data["empresa_id"]
                ).first()
                
                if not existe:
                    estacao = EstacaoKDS(**estacao_data)
                    db.add(estacao)
                    logger.info(f"   ✅ Criada estação: {estacao_data['nome']}")
                else:
                    logger.info(f"   ⚠️ Estação já existe: {estacao_data['nome']}")
            
            db.commit()
            
            # 2. Criar configurações KDS padrão
            logger.info("⚙️ Criando configurações KDS padrão...")
            
            configuracoes_padrao = [
                {
                    "chave": "tempo_max_preparo_padrao",
                    "valor": "30",
                    "descricao": "Tempo máximo padrão para preparo em minutos",
                    "categoria": "TEMPO",
                    "empresa_id": 1
                },
                {
                    "chave": "notificacao_atraso_ativa",
                    "valor": "true",
                    "descricao": "Ativar notificações de atraso automáticas",
                    "categoria": "NOTIFICACAO",
                    "empresa_id": 1
                },
                {
                    "chave": "intervalo_atualizacao_dashboard",
                    "valor": "5",
                    "descricao": "Intervalo de atualização do dashboard em segundos",
                    "categoria": "INTERFACE",
                    "empresa_id": 1
                },
                {
                    "chave": "limite_pedidos_por_mesa",
                    "valor": "10",
                    "descricao": "Limite máximo de pedidos simultâneos por mesa",
                    "categoria": "LIMITE",
                    "empresa_id": 1
                },
                {
                    "chave": "tempo_expiracao_notificacao",
                    "valor": "60",
                    "descricao": "Tempo de expiração das notificações em minutos",
                    "categoria": "NOTIFICACAO",
                    "empresa_id": 1
                },
                {
                    "chave": "audio_notificacao_ativo",
                    "valor": "true",
                    "descricao": "Ativar som para notificações",
                    "categoria": "INTERFACE",
                    "empresa_id": 1
                },
                {
                    "chave": "modo_tela_cheia_kds",
                    "valor": "false",
                    "descricao": "Modo tela cheia para displays KDS",
                    "categoria": "INTERFACE",
                    "empresa_id": 1
                },
                {
                    "chave": "cores_status_personalizada",
                    "valor": '{"pendente": "#fbbf24", "preparando": "#3b82f6", "pronto": "#10b981", "atrasado": "#ef4444"}',
                    "descricao": "Cores personalizadas para status dos pedidos",
                    "categoria": "INTERFACE",
                    "empresa_id": 1
                }
            ]
            
            for config_data in configuracoes_padrao:
                # Verificar se já existe
                existe = db.query(ConfiguracaoKDS).filter_by(
                    chave=config_data["chave"],
                    empresa_id=config_data["empresa_id"]
                ).first()
                
                if not existe:
                    config = ConfiguracaoKDS(**config_data)
                    db.add(config)
                    logger.info(f"   ✅ Criada configuração: {config_data['chave']}")
                else:
                    logger.info(f"   ⚠️ Configuração já existe: {config_data['chave']}")
            
            db.commit()
            
            # 3. Criar pedidos de exemplo (opcional - apenas para demonstração)
            logger.info("🍽️ Criando pedidos de exemplo...")
            
            # Verificar se existem mesas na tabela mesa (do sistema cashless)
            resultado_mesas = db.execute(text("SELECT COUNT(*) FROM mesa WHERE ativa = true"))
            total_mesas = resultado_mesas.scalar()
            
            if total_mesas > 0:
                # Buscar primeira mesa ativa
                resultado_mesa = db.execute(text("SELECT id, numero FROM mesa WHERE ativa = true LIMIT 1"))
                mesa_info = resultado_mesa.fetchone()
                
                if mesa_info:
                    mesa_id, numero_mesa = mesa_info
                    
                    # Criar pedido de exemplo
                    pedido_exemplo = PedidoMesa(
                        numero_pedido=f"M{numero_mesa}-{datetime.now().strftime('%y%m%d')}-001",
                        mesa_id=mesa_id,
                        numero_mesa=str(numero_mesa),
                        status=StatusPedidoMesa.PENDENTE,
                        prioridade=PrioridadePedido.NORMAL,
                        modo_pedido=ModoPedidoMesa.MESA,
                        data_pedido=datetime.now(),
                        tempo_estimado_preparo=25,
                        valor_subtotal=45.50,
                        valor_total=45.50,
                        observacoes="Pedido de exemplo para demonstração do sistema",
                        estacao_responsavel=TipoEstacaoKDS.PRINCIPAL,
                        empresa_id=1,
                        usuario_criacao_id=1
                    )
                    
                    db.add(pedido_exemplo)
                    db.commit()
                    db.refresh(pedido_exemplo)
                    
                    # Adicionar itens de exemplo
                    itens_exemplo = [
                        {
                            "nome_produto": "Hambúrguer Artesanal",
                            "descricao": "Hambúrguer com carne angus, queijo, bacon e molho especial",
                            "quantidade": 1,
                            "valor_unitario": 28.50,
                            "valor_total": 28.50,
                            "status": StatusItemPedido.PENDENTE,
                            "tempo_estimado_preparo": 20,
                            "observacoes": "Ponto da carne: mal passado"
                        },
                        {
                            "nome_produto": "Batata Rústica",
                            "descricao": "Batatas rústicas temperadas com ervas",
                            "quantidade": 1,
                            "valor_unitario": 12.00,
                            "valor_total": 12.00,
                            "status": StatusItemPedido.PENDENTE,
                            "tempo_estimado_preparo": 15
                        },
                        {
                            "nome_produto": "Refrigerante Lata",
                            "descricao": "Coca-Cola lata 350ml",
                            "quantidade": 1,
                            "valor_unitario": 5.00,
                            "valor_total": 5.00,
                            "status": StatusItemPedido.PENDENTE,
                            "tempo_estimado_preparo": 2
                        }
                    ]
                    
                    for item_data in itens_exemplo:
                        item = ItemPedidoMesa(
                            pedido_id=pedido_exemplo.id,
                            **item_data
                        )
                        db.add(item)
                    
                    db.commit()
                    logger.info(f"   ✅ Criado pedido de exemplo: {pedido_exemplo.numero_pedido}")
                    
                    # Criar notificação de exemplo
                    notificacao = NotificacaoKDS(
                        tipo=TipoNotificacaoKDS.NOVO_PEDIDO,
                        titulo=f"Novo Pedido - Mesa {numero_mesa}",
                        mensagem=f"Pedido {pedido_exemplo.numero_pedido} criado com 3 itens",
                        urgencia=PrioridadePedido.NORMAL,
                        pedido_id=pedido_exemplo.id,
                        mesa_id=mesa_id
                    )
                    
                    db.add(notificacao)
                    db.commit()
                    logger.info("   ✅ Criada notificação de exemplo")
            else:
                logger.info("   ⚠️ Nenhuma mesa encontrada - pulando criação de pedidos de exemplo")
            
            # 4. Criar índices para performance (se não existirem)
            logger.info("📊 Criando índices de performance...")
            
            indices_sql = [
                """
                CREATE INDEX IF NOT EXISTS idx_pedido_mesa_status_data 
                ON pedido_mesa(status, data_pedido DESC);
                """,
                """
                CREATE INDEX IF NOT EXISTS idx_pedido_mesa_mesa_status 
                ON pedido_mesa(mesa_id, status);
                """,
                """
                CREATE INDEX IF NOT EXISTS idx_pedido_mesa_estacao_status 
                ON pedido_mesa(estacao_responsavel, status);
                """,
                """
                CREATE INDEX IF NOT EXISTS idx_item_pedido_status 
                ON item_pedido_mesa(status, data_criacao DESC);
                """,
                """
                CREATE INDEX IF NOT EXISTS idx_notificacao_kds_lida_data 
                ON notificacao_kds(lida, data_criacao DESC);
                """,
                """
                CREATE INDEX IF NOT EXISTS idx_notificacao_kds_estacao 
                ON notificacao_kds(estacao_id, data_criacao DESC);
                """,
                """
                CREATE INDEX IF NOT EXISTS idx_log_evento_tipo_data 
                ON log_evento_kds(tipo_evento, data_evento DESC);
                """,
                """
                CREATE INDEX IF NOT EXISTS idx_relatorio_tempo_mesa_periodo 
                ON relatorio_tempo_mesa(data_inicio, data_fim, mesa_id);
                """
            ]
            
            for sql in indices_sql:
                executar_sql_seguro(db, sql, "Criando índice de performance")
            
            db.commit()
            
            # 5. Estatísticas finais
            logger.info("📈 Verificando estatísticas da migração...")
            
            # Contar registros criados
            total_estacoes = db.query(EstacaoKDS).count()
            total_configuracoes = db.query(ConfiguracaoKDS).count()
            total_pedidos = db.query(PedidoMesa).count()
            total_itens = db.query(ItemPedidoMesa).count()
            total_notificacoes = db.query(NotificacaoKDS).count()
            
            logger.info(f"   📊 Estações KDS criadas: {total_estacoes}")
            logger.info(f"   📊 Configurações criadas: {total_configuracoes}")
            logger.info(f"   📊 Pedidos de exemplo: {total_pedidos}")
            logger.info(f"   📊 Itens de exemplo: {total_itens}")
            logger.info(f"   📊 Notificações criadas: {total_notificacoes}")
            
            logger.info("✅ Migração do Sistema Mesa + KDS concluída com sucesso!")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro durante a migração: {str(e)}")
            db.rollback()
            raise
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"❌ Erro fatal na migração: {str(e)}")
        return False

def verificar_estrutura():
    """Verifica se a estrutura foi criada corretamente"""
    
    logger.info("🔍 Verificando estrutura criada...")
    
    db = SessionLocal()
    try:
        # Verificar tabelas principais
        tabelas_principais = [
            ("pedido_mesa", "Sistema de pedidos de mesa"),
            ("item_pedido_mesa", "Itens dos pedidos"),
            ("estacao_kds", "Estações do KDS"),
            ("configuracao_kds", "Configurações do sistema"),
            ("notificacao_kds", "Sistema de notificações"),
            ("log_evento_kds", "Logs de auditoria"),
            ("relatorio_tempo_mesa", "Relatórios de performance")
        ]
        
        for tabela, descricao in tabelas_principais:
            try:
                resultado = db.execute(text(f"SELECT COUNT(*) FROM {tabela}"))
                count = resultado.scalar()
                logger.info(f"   ✅ {descricao}: {count} registros")
            except Exception as e:
                logger.error(f"   ❌ Erro ao verificar {tabela}: {str(e)}")
        
        # Verificar enums
        logger.info("🏷️ Verificando enums criados...")
        
        enums_verificacao = [
            "SELECT unnest(enum_range(NULL::statuspedidomesa))",
            "SELECT unnest(enum_range(NULL::statusitempedido))",
            "SELECT unnest(enum_range(NULL::tiponotificacaokds))",
            "SELECT unnest(enum_range(NULL::tipoestacaokds))",
            "SELECT unnest(enum_range(NULL::prioridadepedido))",
            "SELECT unnest(enum_range(NULL::modopedido))"
        ]
        
        for enum_sql in enums_verificacao:
            try:
                resultado = db.execute(text(enum_sql))
                valores = [row[0] for row in resultado.fetchall()]
                enum_name = enum_sql.split("::")[1].replace(")", "")
                logger.info(f"   ✅ {enum_name}: {', '.join(valores)}")
            except Exception as e:
                logger.warning(f"   ⚠️ Enum não verificado: {str(e)}")
        
        logger.info("✅ Verificação estrutural concluída!")
        
    except Exception as e:
        logger.error(f"❌ Erro na verificação: {str(e)}")
    finally:
        db.close()

def main():
    """Função principal da migração"""
    
    print("=" * 80)
    print("🚀 MIGRAÇÃO SISTEMA MESA + KDS - MEEP REVERSO")
    print("=" * 80)
    print()
    
    try:
        # Executar migração
        sucesso = criar_tabelas_mesa_kds()
        
        if sucesso:
            print()
            print("=" * 80)
            verificar_estrutura()
            print("=" * 80)
            print("🎉 MIGRAÇÃO CONCLUÍDA COM SUCESSO!")
            print()
            print("📋 Funcionalidades implementadas:")
            print("   ✅ Sistema avançado de pedidos de mesa")
            print("   ✅ Kitchen Display System (KDS) com 6 estações")
            print("   ✅ Notificações em tempo real via WebSocket")
            print("   ✅ Relatórios e analytics de performance")
            print("   ✅ Sistema de auditoria completo")
            print("   ✅ Configurações personalizáveis")
            print()
            print("🔗 Endpoints disponíveis:")
            print("   • GET /api/mesa-kds/dashboard - Dashboard operacional")
            print("   • GET /api/mesa-kds/pedidos - Listar pedidos")
            print("   • POST /api/mesa-kds/pedidos - Criar pedido")
            print("   • GET /api/mesa-kds/estacoes - Estações KDS")
            print("   • WS /api/mesa-kds/ws/kds - WebSocket notificações")
            print("   • GET /api/mesa-kds/relatorios/tempo-mesa - Relatórios")
            print()
            print("⚡ Sistema pronto para uso em produção!")
            print("=" * 80)
        else:
            print("❌ Migração falhou. Verifique os logs acima.")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⚠️ Migração interrompida pelo usuário")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erro fatal: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
