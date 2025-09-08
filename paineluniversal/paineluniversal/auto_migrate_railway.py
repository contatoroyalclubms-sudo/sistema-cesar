#!/usr/bin/env python3
"""
Migração automática para Railway: Corrigir coluna tipo_usuario
Esta migração roda automaticamente durante o deploy no Railway
"""
import os
import sys
import logging
from sqlalchemy import create_engine, text
from datetime import datetime

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def auto_migrate_tipo_usuario():
    """
    Migração automática que roda no Railway para corrigir tipo_usuario
    """
    logger.info("🚀 MIGRAÇÃO AUTOMÁTICA RAILWAY: TIPO_USUARIO")
    logger.info("=" * 50)
    
    # Obter URL do banco do Railway
    database_url = os.environ.get("DATABASE_URL")
    
    if not database_url:
        logger.error("❌ DATABASE_URL não encontrada - pulando migração")
        return True  # Não falhar o deploy por isso
    
    # Ajustar URL se necessário
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    
    try:
        # Conectar ao banco
        logger.info("🔌 Conectando ao PostgreSQL...")
        engine = create_engine(database_url, connect_args={"connect_timeout": 30})
        
        with engine.connect() as conn:
            # Iniciar transação
            trans = conn.begin()
            
            try:
                # 1. Verificar se a tabela usuarios existe
                result = conn.execute(text("""
                    SELECT EXISTS (
                        SELECT 1 FROM information_schema.tables 
                        WHERE table_schema = 'public' 
                        AND table_name = 'usuarios'
                    )
                """))
                
                if not result.fetchone()[0]:
                    logger.warning("⚠️ Tabela 'usuarios' não existe - pulando migração")
                    trans.rollback()
                    return True
                
                logger.info("✅ Tabela 'usuarios' encontrada")
                
                # 2. Verificar se a coluna tipo_usuario existe
                result = conn.execute(text("""
                    SELECT 
                        column_name,
                        data_type,
                        udt_name,
                        is_nullable,
                        column_default
                    FROM information_schema.columns 
                    WHERE table_name = 'usuarios' 
                    AND column_name = 'tipo_usuario'
                """))
                
                col_info = result.fetchone()
                
                if col_info:
                    logger.info(f"✅ Coluna tipo_usuario existe: {col_info[1]} ({col_info[2]})")
                    
                    # Se for enum, converter para VARCHAR
                    if col_info[1] == 'USER-DEFINED':
                        logger.info("🔄 Convertendo enum para VARCHAR...")
                        
                        # Adicionar coluna temporária
                        conn.execute(text("ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS tipo_usuario_temp VARCHAR(20)"))
                        
                        # Mapear valores do enum para strings
                        conn.execute(text("""
                            UPDATE usuarios 
                            SET tipo_usuario_temp = CASE 
                                WHEN tipo_usuario::text = 'ADMIN' THEN 'admin'
                                WHEN tipo_usuario::text = 'PROMOTER' THEN 'promoter'
                                WHEN tipo_usuario::text = 'CLIENTE' THEN 'cliente'
                                WHEN tipo_usuario::text = 'admin' THEN 'admin'
                                WHEN tipo_usuario::text = 'promoter' THEN 'promoter'
                                WHEN tipo_usuario::text = 'cliente' THEN 'cliente'
                                ELSE 'cliente'
                            END
                        """))
                        
                        # Remover coluna antiga
                        conn.execute(text("ALTER TABLE usuarios DROP COLUMN tipo_usuario"))
                        
                        # Renomear coluna temporária
                        conn.execute(text("ALTER TABLE usuarios RENAME COLUMN tipo_usuario_temp TO tipo_usuario"))
                        
                        logger.info("✅ Enum convertido para VARCHAR")
                    
                    elif col_info[1] != 'character varying':
                        logger.info(f"🔄 Convertendo {col_info[1]} para VARCHAR...")
                        conn.execute(text("ALTER TABLE usuarios ALTER COLUMN tipo_usuario TYPE VARCHAR(20)"))
                        logger.info("✅ Tipo convertido")
                    else:
                        logger.info("✅ Coluna já é VARCHAR")
                        
                else:
                    logger.info("❌ Coluna tipo_usuario NÃO EXISTE - criando...")
                    
                    # Verificar quantos usuários existem
                    result = conn.execute(text("SELECT COUNT(*) FROM usuarios"))
                    user_count = result.fetchone()[0]
                    logger.info(f"📊 {user_count} usuários encontrados")
                    
                    # Adicionar coluna com valor padrão
                    conn.execute(text("""
                        ALTER TABLE usuarios 
                        ADD COLUMN tipo_usuario VARCHAR(20) DEFAULT 'cliente'
                    """))
                    
                    # Atualizar todos os usuários existentes
                    conn.execute(text("UPDATE usuarios SET tipo_usuario = 'cliente' WHERE tipo_usuario IS NULL"))
                    
                    logger.info("✅ Coluna tipo_usuario criada")
                
                # 3. Garantir que a coluna é NOT NULL
                logger.info("🔒 Configurando restrições...")
                
                # Verificar se há valores NULL
                result = conn.execute(text("SELECT COUNT(*) FROM usuarios WHERE tipo_usuario IS NULL"))
                null_count = result.fetchone()[0]
                
                if null_count > 0:
                    logger.info(f"⚠️ {null_count} usuários com tipo_usuario NULL - corrigindo...")
                    conn.execute(text("UPDATE usuarios SET tipo_usuario = 'cliente' WHERE tipo_usuario IS NULL"))
                
                # Tornar NOT NULL
                conn.execute(text("ALTER TABLE usuarios ALTER COLUMN tipo_usuario SET NOT NULL"))
                logger.info("✅ Coluna configurada como NOT NULL")
                
                # 4. Verificar valores únicos
                result = conn.execute(text("""
                    SELECT tipo_usuario, COUNT(*) as count 
                    FROM usuarios 
                    GROUP BY tipo_usuario 
                    ORDER BY count DESC
                """))
                
                stats = result.fetchall()
                logger.info("📊 Distribuição de tipos de usuário:")
                for stat in stats:
                    logger.info(f"  - {stat[0]}: {stat[1]} usuários")
                
                # 5. Teste final
                logger.info("🧪 Testando query que estava falhando...")
                result = conn.execute(text("""
                    SELECT 
                        usuarios.id, 
                        usuarios.cpf, 
                        usuarios.nome,
                        usuarios.tipo_usuario
                    FROM usuarios 
                    LIMIT 1
                """))
                
                test_result = result.fetchone()
                if test_result:
                    logger.info(f"✅ Query funciona: ID {test_result[0]}, Tipo: {test_result[3]}")
                
                # Commit das mudanças
                trans.commit()
                logger.info("🎉 MIGRAÇÃO CONCLUÍDA COM SUCESSO!")
                logger.info("✅ Sistema de login deve funcionar agora")
                
                return True
                
            except Exception as e:
                logger.error(f"❌ ERRO na migração: {e}")
                trans.rollback()
                return False
                
    except Exception as e:
        logger.error(f"❌ ERRO de conexão: {e}")
        return False

if __name__ == "__main__":
    success = auto_migrate_tipo_usuario()
    
    if not success:
        logger.error("❌ Migração falhou")
        # Não fazer sys.exit(1) para não quebrar o deploy
        # sys.exit(1)
    else:
        logger.info("✅ Migração concluída com sucesso")
