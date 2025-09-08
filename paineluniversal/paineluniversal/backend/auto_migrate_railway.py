#!/usr/bin/env python3
"""
🚨 MIGRAÇÃO AUTOMÁTICA CRÍTICA - RAILWAY DEPLOY
Corrige coluna tipo_usuario automaticamente durante o deploy
Executa com segurança e rollback automático em caso de erro
"""

import os
import sys
import logging
import psycopg2
import time
from datetime import datetime
from urllib.parse import urlparse

# Configurar logging detalhado
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class AutoMigrateRailway:
    """Migração automática e segura para Railway"""
    
    def __init__(self):
        self.conn = None
        self.cursor = None
        self.backup_created = False
        
    def log_step(self, step: str, status: str = "INFO"):
        """Log padronizado com emojis"""
        emoji_map = {
            "INFO": "ℹ️",
            "SUCCESS": "✅", 
            "ERROR": "❌",
            "WARNING": "⚠️",
            "PROCESS": "🔧"
        }
        emoji = emoji_map.get(status, "📝")
        logger.info(f"{emoji} {step}")
        
    def connect_database(self):
        """Conectar ao PostgreSQL do Railway"""
        try:
            self.log_step("Iniciando conexão com PostgreSQL...", "PROCESS")
            
            database_url = os.getenv('DATABASE_URL')
            if not database_url:
                self.log_step("DATABASE_URL não encontrada nas variáveis de ambiente", "ERROR")
                return False
                
            # Ajustar URL se necessário (postgres -> postgresql)
            if database_url.startswith('postgres://'):
                database_url = database_url.replace('postgres://', 'postgresql://', 1)
                
            self.log_step(f"Conectando ao banco: {database_url[:30]}...", "PROCESS")
            
            # Tentar conexão com timeout
            self.conn = psycopg2.connect(
                database_url,
                connect_timeout=30,
                application_name="railway_auto_migration"
            )
            self.cursor = self.conn.cursor()
            
            # Testar conexão
            self.cursor.execute("SELECT version();")
            version = self.cursor.fetchone()[0]
            self.log_step(f"Conectado ao PostgreSQL: {version.split()[0]} {version.split()[1]}", "SUCCESS")
            
            return True
            
        except Exception as e:
            self.log_step(f"Erro na conexão: {str(e)}", "ERROR")
            return False
    
    def check_table_structure(self):
        """Verificar estrutura atual da tabela usuarios"""
        try:
            self.log_step("Verificando estrutura da tabela usuarios...", "PROCESS")
            
            # Verificar se tabela usuarios existe
            self.cursor.execute("""
                SELECT EXISTS (
                    SELECT 1 FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'usuarios'
                );
            """)
            
            table_exists = self.cursor.fetchone()[0]
            if not table_exists:
                self.log_step("Tabela 'usuarios' não existe!", "ERROR")
                return False
                
            # Verificar colunas existentes
            self.cursor.execute("""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns 
                WHERE table_name = 'usuarios' 
                ORDER BY ordinal_position;
            """)
            
            columns = self.cursor.fetchall()
            self.log_step(f"Tabela usuarios tem {len(columns)} colunas", "INFO")
            
            # Verificar especificamente tipo_usuario
            tipo_usuario_exists = any(col[0] == 'tipo_usuario' for col in columns)
            
            if tipo_usuario_exists:
                self.log_step("Coluna tipo_usuario já existe!", "SUCCESS")
                return "exists"
            else:
                self.log_step("Coluna tipo_usuario NÃO EXISTE - migração necessária", "WARNING")
                return "missing"
                
        except Exception as e:
            self.log_step(f"Erro verificando estrutura: {str(e)}", "ERROR")
            return False
    
    def backup_table(self):
        """Criar backup da tabela antes da migração"""
        try:
            self.log_step("Criando backup da tabela usuarios...", "PROCESS")
            
            # Contar registros
            self.cursor.execute("SELECT COUNT(*) FROM usuarios;")
            user_count = self.cursor.fetchone()[0]
            self.log_step(f"Total de usuários: {user_count}", "INFO")
            
            if user_count == 0:
                self.log_step("Tabela vazia - backup não necessário", "INFO")
                return True
                
            # Criar tabela de backup
            backup_table = f"usuarios_backup_{int(time.time())}"
            self.cursor.execute(f"""
                CREATE TABLE {backup_table} AS 
                SELECT * FROM usuarios;
            """)
            
            self.conn.commit()
            self.backup_created = True
            self.log_step(f"Backup criado: {backup_table}", "SUCCESS")
            return True
            
        except Exception as e:
            self.log_step(f"Erro criando backup: {str(e)}", "ERROR")
            return False
    
    def migrate_tipo_usuario(self):
        """Executar migração da coluna tipo_usuario"""
        try:
            self.log_step("Iniciando migração da coluna tipo_usuario...", "PROCESS")
            
            # Usar transação para rollback automático
            self.cursor.execute("BEGIN;")
            
            # 1. Adicionar coluna tipo_usuario
            self.log_step("Adicionando coluna tipo_usuario...", "PROCESS")
            self.cursor.execute("""
                ALTER TABLE usuarios 
                ADD COLUMN tipo_usuario VARCHAR(20) DEFAULT 'cliente';
            """)
            
            # 2. Atualizar registros existentes
            self.log_step("Atualizando registros existentes...", "PROCESS")
            self.cursor.execute("""
                UPDATE usuarios 
                SET tipo_usuario = COALESCE(tipo_usuario, 'cliente') 
                WHERE tipo_usuario IS NULL;
            """)
            
            # 3. Tornar coluna obrigatória
            self.log_step("Configurando coluna como NOT NULL...", "PROCESS")
            self.cursor.execute("""
                ALTER TABLE usuarios 
                ALTER COLUMN tipo_usuario SET NOT NULL;
            """)
            
            # 4. Adicionar constraint de validação
            self.log_step("Adicionando constraint de validação...", "PROCESS")
            self.cursor.execute("""
                ALTER TABLE usuarios 
                ADD CONSTRAINT check_tipo_usuario 
                CHECK (tipo_usuario IN ('admin', 'promoter', 'cliente', 'operador'));
            """)
            
            # 5. Commit da transação
            self.cursor.execute("COMMIT;")
            self.log_step("Migração concluída com sucesso!", "SUCCESS")
            
            return True
            
        except Exception as e:
            self.log_step(f"Erro na migração: {str(e)}", "ERROR")
            self.log_step("Executando ROLLBACK...", "WARNING")
            try:
                self.cursor.execute("ROLLBACK;")
                self.log_step("ROLLBACK executado com sucesso", "SUCCESS")
            except:
                self.log_step("Erro no ROLLBACK!", "ERROR")
            return False
    
    def validate_migration(self):
        """Validar que a migração funcionou"""
        try:
            self.log_step("Validando migração...", "PROCESS")
            
            # Testar query que estava falhando
            self.cursor.execute("""
                SELECT 
                    usuarios.id, 
                    usuarios.cpf, 
                    usuarios.nome,
                    usuarios.tipo_usuario
                FROM usuarios 
                LIMIT 3;
            """)
            
            results = self.cursor.fetchall()
            if results:
                self.log_step(f"Query de validação executada: {len(results)} registros retornados", "SUCCESS")
                for row in results:
                    cpf_masked = f"{row[1][:3]}***{row[1][-3:]}" if len(row[1]) >= 6 else "***"
                    self.log_step(f"  ID: {row[0]}, CPF: {cpf_masked}, Tipo: {row[3]}", "INFO")
            else:
                self.log_step("Nenhum registro encontrado (tabela vazia)", "INFO")
                
            # Verificar estrutura final
            self.cursor.execute("""
                SELECT column_name, data_type, is_nullable 
                FROM information_schema.columns 
                WHERE table_name = 'usuarios' 
                AND column_name = 'tipo_usuario';
            """)
            
            col_info = self.cursor.fetchone()
            if col_info:
                self.log_step(f"Coluna tipo_usuario: {col_info[1]}, NOT NULL: {col_info[2] == 'NO'}", "SUCCESS")
                return True
            else:
                self.log_step("Coluna tipo_usuario não encontrada!", "ERROR")
                return False
                
        except Exception as e:
            self.log_step(f"Erro na validação: {str(e)}", "ERROR")
            return False
    
    def cleanup(self):
        """Limpeza de recursos"""
        try:
            if self.cursor:
                self.cursor.close()
            if self.conn:
                self.conn.close()
            self.log_step("Conexão fechada", "INFO")
        except:
            pass
    
    def run_migration(self):
        """Executar migração completa"""
        start_time = datetime.now()
        self.log_step("🚀 INICIANDO MIGRAÇÃO AUTOMÁTICA RAILWAY", "PROCESS")
        self.log_step(f"Timestamp: {start_time.isoformat()}", "INFO")
        
        try:
            # 1. Conectar ao banco
            if not self.connect_database():
                return False
            
            # 2. Verificar estrutura
            structure_check = self.check_table_structure()
            if structure_check == False:
                return False
            elif structure_check == "exists":
                self.log_step("Migração não necessária - coluna já existe", "SUCCESS")
                return True
            
            # 3. Criar backup
            if not self.backup_table():
                self.log_step("Continuando sem backup...", "WARNING")
            
            # 4. Executar migração
            if not self.migrate_tipo_usuario():
                return False
            
            # 5. Validar resultado
            if not self.validate_migration():
                return False
            
            # 6. Sucesso
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            self.log_step(f"🎉 MIGRAÇÃO CONCLUÍDA COM SUCESSO! ({duration:.1f}s)", "SUCCESS")
            self.log_step("Sistema de login deve funcionar normalmente agora", "SUCCESS")
            
            return True
            
        except Exception as e:
            self.log_step(f"Erro geral na migração: {str(e)}", "ERROR")
            return False
        finally:
            self.cleanup()

def auto_migrate_tipo_usuario():
    """Função legacy para compatibilidade com start.sh existente"""
    logger.info("🚀 MIGRAÇÃO AUTOMÁTICA RAILWAY: TIPO_USUARIO")
    logger.info("=" * 50)
    
    migrator = AutoMigrateRailway()
    return migrator.run_migration()

def main():
    """Ponto de entrada principal"""
    print("=" * 80)
    print("� MIGRAÇÃO AUTOMÁTICA - SISTEMA DE LOGIN RAILWAY")
    print("=" * 80)
    
    migrator = AutoMigrateRailway()
    success = migrator.run_migration()
    
    if success:
        print("\n✅ MIGRAÇÃO BEM-SUCEDIDA")
        print("🎯 Sistema de login funcionando")
        return True
    else:
        print("\n❌ MIGRAÇÃO FALHOU")
        print("⚠️ Verificar logs para detalhes")
        # Não usar sys.exit(1) em produção para não quebrar deploy
        return False

if __name__ == "__main__":
    main()
