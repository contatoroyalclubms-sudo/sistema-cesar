#!/usr/bin/env python3
"""
Sistema de Migração Automática para Deploy
Remove automaticamente a coluna evento_id da tabela produtos
"""

import os
import logging
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.exc import SQLAlchemyError
import time
from datetime import datetime

logger = logging.getLogger(__name__)

class AutoMigration:
    def __init__(self):
        self.database_url = os.getenv("DATABASE_URL")
        if not self.database_url:
            raise ValueError("DATABASE_URL não encontrada nas variáveis de ambiente")
        
        # Converter postgres:// para postgresql:// se necessário
        if self.database_url.startswith("postgres://"):
            self.database_url = self.database_url.replace("postgres://", "postgresql://", 1)
        
        self.engine = create_engine(self.database_url, pool_pre_ping=True, pool_recycle=300)
    
    def check_tipousuario_enum(self):
        """Verifica se o enum tipousuario tem todos os valores necessários"""
        try:
            with self.engine.connect() as conn:
                # Verificar se o enum tipousuario existe
                result = conn.execute(text("""
                    SELECT EXISTS (
                        SELECT 1 FROM pg_type WHERE typname = 'tipousuario'
                    )
                """))
                
                if not result.scalar():
                    logger.info("️ Enum tipousuario não existe, será criado")
                    return False
                
                # Verificar valores existentes no enum
                result = conn.execute(text("""
                    SELECT enumlabel 
                    FROM pg_enum 
                    WHERE enumtypid = (SELECT oid FROM pg_type WHERE typname = 'tipousuario')
                    ORDER BY enumsortorder
                """))
                
                existing_values = [row[0] for row in result.fetchall()]
                required_values = ['admin', 'promoter', 'cliente']
                
                logger.info(f" Valores atuais do enum: {existing_values}")
                logger.info(f" Valores necessários: {required_values}")
                
                missing_values = [v for v in required_values if v not in existing_values]
                
                if missing_values:
                    logger.info(f"️ Valores faltando no enum: {missing_values}")
                    return False
                else:
                    logger.info(" Enum tipousuario está completo")
                    return True
                    
        except Exception as e:
            logger.error(f"Erro ao verificar enum tipousuario: {e}")
            return False
    
    def fix_tipousuario_enum(self):
        """Corrige o enum tipousuario adicionando valores faltantes e corrigindo case mismatch"""
        try:
            with self.engine.connect() as conn:
                trans = conn.begin()
                
                try:
                    logger.info(" Corrigindo enum tipousuario...")
                    
                    # Criar enum se não existir
                    conn.execute(text("""
                        DO $$
                        BEGIN
                            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'tipousuario') THEN
                                CREATE TYPE tipousuario AS ENUM ('admin', 'promoter', 'cliente');
                                RAISE NOTICE 'Enum tipousuario criado com valores: admin, promoter, cliente';
                            END IF;
                        END $$;
                    """))
                    
                    # Adicionar valores em lowercase (corrigindo case mismatch)
                    enum_corrections = [
                        ('admin', 'ADMIN'),
                        ('promoter', 'PROMOTER'), 
                        ('cliente', 'CLIENTE')
                    ]
                    
                    for lowercase_val, uppercase_val in enum_corrections:
                        try:
                            # Verificar se valor lowercase já existe
                            result = conn.execute(text("""
                                SELECT EXISTS(
                                    SELECT 1 FROM pg_enum 
                                    WHERE enumlabel = :value 
                                    AND enumtypid = (SELECT oid FROM pg_type WHERE typname = 'tipousuario')
                                )
                            """), {"value": lowercase_val})
                            
                            if not result.scalar():
                                # Valor lowercase não existe, adicionar
                                conn.execute(text(f"ALTER TYPE tipousuario ADD VALUE '{lowercase_val}'"))
                                logger.info(f" Valor '{lowercase_val}' adicionado ao enum tipousuario")
                            else:
                                logger.info(f" Valor '{lowercase_val}' já existe no enum")
                                
                        except Exception as e:
                            logger.warning(f"Aviso ao adicionar '{lowercase_val}': {e}")
                    
                    # Corrigir usuários existentes que podem ter valores em UPPERCASE
                    logger.info(" Corrigindo case de usuários existentes...")
                    
                    # Verificar se existem usuários com valores em UPPERCASE
                    result = conn.execute(text("""
                        SELECT COUNT(*) FROM usuarios 
                        WHERE tipo IN ('ADMIN', 'PROMOTER', 'CLIENTE')
                    """))
                    
                    uppercase_count = result.scalar()
                    
                    if uppercase_count > 0:
                        logger.info(f" Encontrados {uppercase_count} usuários com valores em UPPERCASE")
                        
                        # Atualizar para lowercase
                        update_queries = [
                            "UPDATE usuarios SET tipo='admin' WHERE tipo='ADMIN'",
                            "UPDATE usuarios SET tipo='promoter' WHERE tipo='PROMOTER'",
                            "UPDATE usuarios SET tipo='cliente' WHERE tipo='CLIENTE'"
                        ]
                        
                        for query in update_queries:
                            result = conn.execute(text(query))
                            updated_count = result.rowcount
                            if updated_count > 0:
                                tipo_atualizado = query.split('=')[1].strip().replace("'", "")
                                logger.info(f" {updated_count} usuário(s) atualizado(s): {tipo_atualizado}")
                    else:
                        logger.info(" Nenhum usuário com valores em UPPERCASE encontrado")
                    
                    trans.commit()
                    logger.info(" Enum tipousuario corrigido com sucesso (incluindo case mismatch)")
                    
                except Exception as e:
                    trans.rollback()
                    logger.error(f"Erro na correção do enum, rollback executado: {e}")
                    raise
                    
        except Exception as e:
            logger.error(f"Erro na correção do enum tipousuario: {e}")
            raise
    
    def validate_tipousuario_enum(self):
        """Valida se o enum tipousuario está funcionando corretamente"""
        try:
            with self.engine.connect() as conn:
                # Verificar valores finais do enum
                result = conn.execute(text("""
                    SELECT enumlabel 
                    FROM pg_enum 
                    WHERE enumtypid = (SELECT oid FROM pg_type WHERE typname = 'tipousuario')
                    ORDER BY enumsortorder
                """))
                
                values = [row[0] for row in result.fetchall()]
                required_values = ['admin', 'promoter', 'cliente']
                
                # Verificar se todos os valores necessários estão presentes
                missing = [v for v in required_values if v not in values]
                if missing:
                    logger.error(f" Valores ainda faltando: {missing}")
                    return False
                
                # Testar cada valor
                for value in required_values:
                    try:
                        conn.execute(text(f"SELECT '{value}'::tipousuario"))
                        logger.info(f" Valor '{value}' testado com sucesso")
                    except Exception as e:
                        logger.error(f" Erro ao testar valor '{value}': {e}")
                        return False
                
                logger.info(f" Enum tipousuario validado: {values}")
                return True
                
        except Exception as e:
            logger.error(f"Erro na validação do enum: {e}")
            return False

    def fix_user_types_and_passwords(self):
        """Corrige tipos de usuário e senhas com problemas de hash"""
        try:
            with self.engine.connect() as conn:
                trans = conn.begin()
                
                try:
                    logger.info(" Corrigindo tipos de usuário e senhas...")
                    
                    # 1. Padronizar tipos de usuário para lowercase
                    logger.info(" Padronizando tipos de usuário...")
                    result = conn.execute(text("""
                        UPDATE usuarios 
                        SET tipo = LOWER(TRIM(tipo)) 
                        WHERE tipo IS NOT NULL
                    """))
                    tipo_updates = result.rowcount
                    logger.info(f" {tipo_updates} tipos de usuário padronizados")
                    
                    # 2. Corrigir tipos inválidos para 'cliente'
                    result = conn.execute(text("""
                        UPDATE usuarios 
                        SET tipo = 'cliente' 
                        WHERE tipo IS NOT NULL 
                        AND tipo NOT IN ('admin', 'promoter', 'cliente', 'operador')
                    """))
                    invalid_updates = result.rowcount
                    logger.info(f" {invalid_updates} tipos inválidos corrigidos")
                    
                    # 3. Preencher campos NULL
                    result = conn.execute(text("""
                        UPDATE usuarios 
                        SET tipo = 'cliente' 
                        WHERE tipo IS NULL
                    """))
                    null_updates = result.rowcount
                    logger.info(f" {null_updates} campos NULL preenchidos")
                    
                    # 4. Verificar senhas que podem estar quebradas
                    logger.info(" Verificando integridade das senhas...")
                    result = conn.execute(text("""
                        SELECT id, nome, senha 
                        FROM usuarios 
                        WHERE senha IS NULL 
                        OR LENGTH(senha) < 8 
                        OR senha NOT LIKE '$2b$%'
                        LIMIT 10
                    """))
                    
                    problematic_passwords = result.fetchall()
                    
                    if problematic_passwords:
                        logger.info(f"️ Encontradas {len(problematic_passwords)} senhas com problemas")
                        
                        # Para senhas problemáticas, gerar hash padrão temporário
                        import bcrypt
                        temp_password = "TemporaryPassword123!"
                        temp_hash = bcrypt.hashpw(temp_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                        
                        for user_id, nome, senha in problematic_passwords:
                            conn.execute(text("""
                                UPDATE usuarios 
                                SET senha = :new_hash 
                                WHERE id = :user_id
                            """), {"new_hash": temp_hash, "user_id": user_id})
                            
                            logger.info(f" Senha temporária aplicada ao usuário: {nome} (ID: {user_id})")
                        
                        logger.warning(f"️ {len(problematic_passwords)} usuários receberam senha temporária: '{temp_password}'")
                        logger.warning("️ Notifique estes usuários para redefinir suas senhas!")
                    
                    # 5. Sincronizar coluna 'tipo' se existir
                    try:
                        result = conn.execute(text("SELECT tipo FROM usuarios LIMIT 1"))
                        # Se chegou até aqui, coluna existe
                        result = conn.execute(text("""
                            UPDATE usuarios 
                            SET tipo = tipo_usuario 
                            WHERE tipo != tipo_usuario OR tipo IS NULL
                        """))
                        sync_updates = result.rowcount
                        logger.info(f" {sync_updates} registros sincronizados entre 'tipo' e 'tipo_usuario'")
                    except Exception:
                        logger.info(" Coluna 'tipo' não existe - ok")
                    
                    trans.commit()
                    logger.info(" Correção de tipos e senhas concluída com sucesso")
                    
                except Exception as e:
                    trans.rollback()
                    logger.error(f"Erro na correção, rollback executado: {e}")
                    raise
                    
        except Exception as e:
            logger.error(f"Erro na correção de tipos e senhas: {e}")
            raise
    
    def validate_user_fixes(self):
        """Valida se as correções de usuário foram aplicadas corretamente"""
        try:
            with self.engine.connect() as conn:
                # Verificar tipos de usuário
                result = conn.execute(text("""
                    SELECT DISTINCT tipo_usuario, COUNT(*) 
                    FROM usuarios 
                    WHERE tipo_usuario IS NOT NULL
                    GROUP BY tipo_usuario
                    ORDER BY tipo_usuario
                """))
                
                user_types = result.fetchall()
                logger.info(" Distribuição final de tipos de usuário:")
                for tipo, count in user_types:
                    logger.info(f"  '{tipo}': {count} usuários")
                
                # Verificar se há tipos inválidos
                valid_types = {'admin', 'promoter', 'cliente', 'operador'}
                for tipo, count in user_types:
                    if tipo not in valid_types:
                        logger.warning(f"️ Tipo inválido ainda presente: '{tipo}' ({count} usuários)")
                        return False
                
                # Verificar senhas
                result = conn.execute(text("""
                    SELECT COUNT(*) FROM usuarios 
                    WHERE senha IS NULL OR LENGTH(senha) < 8
                """))
                
                invalid_passwords = result.scalar()
                if invalid_passwords > 0:
                    logger.warning(f"️ {invalid_passwords} usuários ainda com senhas inválidas")
                    return False
                
                logger.info(" Validação de usuários concluída com sucesso")
                return True
                
        except Exception as e:
            logger.error(f"Erro na validação de usuários: {e}")
            return False
        """Verifica se a coluna evento_id ainda existe na tabela produtos"""
        try:
            inspector = inspect(self.engine)
            
            # Verificar se tabela produtos existe
            tables = inspector.get_table_names()
            if 'produtos' not in tables:
                logger.warning("️ Tabela produtos não encontrada")
                return False
            
            columns = inspector.get_columns('produtos')
            evento_id_exists = any(col['name'] == 'evento_id' for col in columns)
            
            logger.info(f" Coluna evento_id existe: {evento_id_exists}")
            return evento_id_exists
            
        except Exception as e:
            logger.error(f"Erro ao verificar coluna evento_id: {e}")
            return False
    
    def backup_produtos_table(self):
        """Cria backup da tabela produtos"""
        try:
            with self.engine.connect() as conn:
                # Verificar se backup já existe
                result = conn.execute(text("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_name = 'produtos_backup_deploy'
                    )
                """))
                
                if not result.scalar():
                    # Criar backup
                    conn.execute(text("""
                        CREATE TABLE produtos_backup_deploy AS 
                        SELECT * FROM produtos
                    """))
                    conn.commit()
                    logger.info(" Backup da tabela produtos criado: produtos_backup_deploy")
                else:
                    logger.info(" Backup já existe, pulando criação...")
                    
        except Exception as e:
            logger.error(f"Erro ao criar backup: {e}")
            raise
    
    def remove_evento_id_column(self):
        """Remove a coluna evento_id da tabela produtos"""
        try:
            with self.engine.connect() as conn:
                trans = conn.begin()
                
                try:
                    # 1. Criar nova tabela sem evento_id
                    logger.info(" Criando nova estrutura da tabela produtos...")
                    conn.execute(text("""
                        CREATE TABLE produtos_new_deploy (
                            id SERIAL PRIMARY KEY,
                            nome VARCHAR(255) NOT NULL,
                            descricao TEXT,
                            preco NUMERIC(10,2) NOT NULL,
                            categoria VARCHAR(100),
                            tipo VARCHAR(50) NOT NULL,
                            codigo_interno VARCHAR(100),
                            imagem_url TEXT,
                            estoque_atual INTEGER DEFAULT 0,
                            estoque_minimo INTEGER DEFAULT 0,
                            estoque_maximo INTEGER DEFAULT 1000,
                            controla_estoque BOOLEAN DEFAULT FALSE,
                            status VARCHAR(20) DEFAULT 'ATIVO',
                            empresa_id INTEGER,
                            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        )
                    """))
                    
                    # 2. Copiar dados (excluindo evento_id)
                    logger.info(" Copiando dados sem coluna evento_id...")
                    conn.execute(text("""
                        INSERT INTO produtos_new_deploy 
                        (id, nome, descricao, preco, categoria, tipo, codigo_interno, 
                         imagem_url, estoque_atual, estoque_minimo, estoque_maximo, 
                         controla_estoque, status, empresa_id, criado_em, atualizado_em)
                        SELECT 
                         id, nome, descricao, preco, categoria, tipo, codigo_interno,
                         imagem_url, estoque_atual, estoque_minimo, estoque_maximo,
                         controla_estoque, status, empresa_id, criado_em, atualizado_em
                        FROM produtos
                    """))
                    
                    # 3. Renomear tabelas atomicamente
                    logger.info(" Aplicando mudanças atomicamente...")
                    conn.execute(text("ALTER TABLE produtos RENAME TO produtos_old_deploy"))
                    conn.execute(text("ALTER TABLE produtos_new_deploy RENAME TO produtos"))
                    
                    # 4. Atualizar sequence
                    conn.execute(text("""
                        SELECT setval('produtos_id_seq', (SELECT COALESCE(MAX(id), 1) FROM produtos))
                    """))
                    
                    # 5. Recriar índices
                    logger.info(" Recriando índices...")
                    indices = [
                        "CREATE INDEX IF NOT EXISTS idx_produtos_categoria ON produtos(categoria)",
                        "CREATE INDEX IF NOT EXISTS idx_produtos_tipo ON produtos(tipo)",
                        "CREATE INDEX IF NOT EXISTS idx_produtos_status ON produtos(status)",
                        "CREATE INDEX IF NOT EXISTS idx_produtos_empresa_id ON produtos(empresa_id)"
                    ]
                    
                    for index_sql in indices:
                        conn.execute(text(index_sql))
                    
                    trans.commit()
                    logger.info(" Migração concluída: evento_id removido da tabela produtos")
                    
                except Exception as e:
                    trans.rollback()
                    logger.error(f"Erro na migração, rollback executado: {e}")
                    raise
                    
        except Exception as e:
            logger.error(f"Erro na remoção da coluna evento_id: {e}")
            raise
    
    def validate_migration(self):
        """Valida se a migração foi bem-sucedida"""
        try:
            with self.engine.connect() as conn:
                # Verificar se evento_id foi removido
                inspector = inspect(self.engine)
                columns = inspector.get_columns('produtos')
                has_evento_id = any(col['name'] == 'evento_id' for col in columns)
                
                if has_evento_id:
                    raise Exception("evento_id ainda existe após migração!")
                
                # Verificar contagem de produtos
                result = conn.execute(text("SELECT COUNT(*) FROM produtos"))
                count = result.scalar()
                
                # Verificar se tabela está funcionando
                sample_result = conn.execute(text("SELECT id, nome, tipo FROM produtos LIMIT 1"))
                sample = sample_result.fetchone()
                
                logger.info(f" Validação bem-sucedida:")
                logger.info(f"   Total de produtos: {count}")
                if sample:
                    logger.info(f"   Exemplo: ID {sample[0]}, Nome: {sample[1]}, Tipo: {sample[2]}")
                
                return True
                
        except Exception as e:
            logger.error(f"Erro na validação: {e}")
            return False
    
    def cleanup_old_tables(self):
        """Remove tabelas antigas após migração bem-sucedida"""
        try:
            with self.engine.connect() as conn:
                # Verificar se tabela antiga existe
                result = conn.execute(text("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_name = 'produtos_old_deploy'
                    )
                """))
                
                if result.scalar():
                    conn.execute(text("DROP TABLE produtos_old_deploy"))
                    conn.commit()
                    logger.info(" Tabela antiga removida: produtos_old_deploy")
                    
        except Exception as e:
            logger.warning(f"Não foi possível remover tabela antiga: {e}")
    
    def run_migration(self):
        """Executa a migração completa"""
        start_time = time.time()
        
        try:
            logger.info(" Verificando migrações necessárias...")
            
            # 1. MIGRAÇÃO DOS TIPOS DE USUÁRIO E SENHAS (PRIORITÁRIA)
            logger.info(" Verificando tipos de usuário e senhas...")
            
            # Verificar se precisa corrigir tipos/senhas
            with self.engine.connect() as conn:
                # Verificar tipos problemáticos
                result = conn.execute(text("""
                    SELECT COUNT(*) FROM usuarios 
                    WHERE tipo IS NULL 
                    OR tipo != LOWER(TRIM(tipo))
                    OR tipo NOT IN ('admin', 'promoter', 'cliente', 'operador')
                """))
                problematic_types = result.scalar()
                
                # Verificar senhas problemáticas
                result = conn.execute(text("""
                    SELECT COUNT(*) FROM usuarios 
                    WHERE senha IS NULL 
                    OR LENGTH(senha) < 8 
                    OR senha NOT LIKE '$2b$%'
                """))
                problematic_passwords = result.scalar()
                
                if problematic_types > 0 or problematic_passwords > 0:
                    logger.info(f"️ Tipos problemáticos: {problematic_types}, Senhas problemáticas: {problematic_passwords}")
                    logger.info(" Executando correção de tipos e senhas...")
                    self.fix_user_types_and_passwords()
                    
                    if not self.validate_user_fixes():
                        raise Exception("Validação das correções de usuário falhou")
                    
                    logger.info(" Tipos de usuário e senhas corrigidos com sucesso")
                else:
                    logger.info(" Tipos de usuário e senhas já estão corretos")
            
            # 2. MIGRAÇÃO DO ENUM TIPOUSUARIO (SE POSTGRESQL)
            try:
                logger.info(" Verificando enum tipousuario...")
                if not self.check_tipousuario_enum():
                    logger.info("️ Enum tipousuario precisa ser corrigido...")
                    self.fix_tipousuario_enum()
                    
                    if not self.validate_tipousuario_enum():
                        raise Exception("Validação do enum tipousuario falhou")
                        
                    logger.info(" Enum tipousuario corrigido com sucesso")
                else:
                    logger.info(" Enum tipousuario já está correto")
            except Exception as e:
                # Se não for PostgreSQL ou enum não for necessário, continuar
                logger.info(f" Enum tipousuario não aplicável ou já correto: {e}")
            
            # 3. MIGRAÇÃO DA TABELA PRODUTOS (EXISTENTE)
            logger.info(" Verificando tabela produtos...")
            if not self.check_evento_id_exists():
                logger.info(" Coluna evento_id já foi removida, migração da tabela não necessária")
                produtos_migration_needed = False
            else:
                logger.info("️ Coluna evento_id encontrada, iniciando migração da tabela...")
                produtos_migration_needed = True
            
            if produtos_migration_needed:
                # Backup
                logger.info(" Criando backup da tabela produtos...")
                self.backup_produtos_table()
                
                # Migração
                logger.info(" Executando migração da tabela produtos...")
                self.remove_evento_id_column()
                
                # Validação
                logger.info(" Validando migração da tabela produtos...")
                if self.validate_migration():
                    # Limpeza (opcional)
                    self.cleanup_old_tables()
                    logger.info(" Migração da tabela produtos concluída")
                else:
                    raise Exception("Validação da migração da tabela produtos falhou")
            
            duration = time.time() - start_time
            logger.info(f" Todas as migrações concluídas com sucesso em {duration:.2f}s")
            return True
                
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f" Falha nas migrações após {duration:.2f}s: {e}")
            return False

def run_auto_migration():
    """Função principal para executar migração automática"""
    try:
        logger.info(" Iniciando migração automática...")
        migration = AutoMigration()
        return migration.run_migration()
    except ValueError as e:
        logger.warning(f"️ Configuração de migração: {e}")
        return False
    except Exception as e:
        logger.error(f"Erro fatal na migração: {e}")
        return False

class DeployMonitoring:
    def __init__(self):
        self.logger = logging.getLogger("deploy_monitoring")
        
    def log_startup_info(self):
        """Log informações do startup"""
        self.logger.info("=" * 60)
        self.logger.info(" RAILWAY DEPLOY STARTUP")
        self.logger.info(f" Time: {datetime.now()}")
        self.logger.info(f" Environment: {os.getenv('RAILWAY_ENVIRONMENT', 'unknown')}")
        
        db_url = os.getenv('DATABASE_URL', 'not set')
        if db_url != 'not set':
            # Mascarar senha na URL para logs
            db_display = db_url.split('@')[1] if '@' in db_url else 'unknown'
            self.logger.info(f" Database: ...@{db_display}")
        else:
            self.logger.info(" Database: not set")
            
        self.logger.info("=" * 60)
    
    def log_migration_status(self, success: bool, duration: float):
        """Log status da migração"""
        if success:
            self.logger.info(f" MIGRAÇÃO AUTOMÁTICA: Sucesso em {duration:.2f}s")
        else:
            self.logger.error(f" MIGRAÇÃO AUTOMÁTICA: Falhou após {duration:.2f}s")

# Instância global para uso no startup
deploy_monitor = DeployMonitoring()
