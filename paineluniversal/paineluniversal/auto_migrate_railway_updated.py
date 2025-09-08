"""
Auto migração Railway - VERSÃO ATUALIZADA
Remover funcionalidade de criação do campo tipo_usuario
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import os
from datetime import datetime

class RailwayAutoMigrate:
    def __init__(self):
        self.database_url = self._get_database_url()
        self.verbose = True
        
    def _get_database_url(self):
        """Detectar URL do banco (Railway ou local)"""
        return (
            os.getenv("DATABASE_URL") or
            os.getenv("POSTGRES_URL") or  
            os.getenv("PGDATABASE_URL") or
            "postgresql://postgres:password@localhost:5432/paineluniversal"
        )
        
    def log_step(self, message, status="INFO"):
        if not self.verbose:
            return
            
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        status_icon = {
            "INFO": "ℹ️",
            "SUCCESS": "✅", 
            "WARNING": "⚠️",
            "ERROR": "❌",
            "PROCESS": "🔄"
        }.get(status, "📝")
        
        print(f"[{timestamp}] {status_icon} {message}")
        
    def connect_db(self):
        """Conectar ao banco PostgreSQL"""
        try:
            self.log_step("Conectando ao banco PostgreSQL...", "PROCESS")
            
            conn = psycopg2.connect(self.database_url)
            conn.autocommit = True
            
            self.log_step("Conexão estabelecida com sucesso!", "SUCCESS")
            return conn
            
        except Exception as e:
            self.log_step(f"Erro ao conectar: {e}", "ERROR")
            return None
    
    def check_usuarios_table(self):
        """Verificar se a tabela usuarios existe e está correta"""
        conn = self.connect_db()
        if not conn:
            return False
            
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                # Verificar se tabela existe
                cur.execute("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_schema = 'public' 
                        AND table_name = 'usuarios'
                    );
                """)
                
                table_exists = cur.fetchone()[0]
                
                if not table_exists:
                    self.log_step("Tabela usuarios não existe!", "ERROR")
                    return False
                
                # Verificar colunas
                cur.execute("""
                    SELECT column_name, data_type, is_nullable, column_default
                    FROM information_schema.columns
                    WHERE table_name = 'usuarios'
                    ORDER BY ordinal_position;
                """)
                
                columns = cur.fetchall()
                column_names = [col['column_name'] for col in columns]
                
                # Verificar se tipo existe
                if 'tipo' not in column_names:
                    self.log_step("Coluna 'tipo' não existe! Estrutura incorreta.", "ERROR")
                    return False
                
                # Verificar se tipo_usuario foi removido
                if 'tipo_usuario' in column_names:
                    self.log_step("⚠️ Coluna 'tipo_usuario' ainda existe! Execute remove_tipo_usuario_migration.py", "WARNING")
                    return False
                
                self.log_step("✅ Estrutura da tabela usuarios está correta", "SUCCESS")
                return True
                
        except Exception as e:
            self.log_step(f"Erro ao verificar tabela: {e}", "ERROR")
            return False
            
        finally:
            conn.close()
    
    def ensure_tipo_constraints(self):
        """Garantir que o campo tipo tem as constraints corretas"""
        conn = self.connect_db()
        if not conn:
            return False
            
        try:
            with conn.cursor() as cur:
                # Remover constraint antiga se existir
                cur.execute("""
                    ALTER TABLE usuarios 
                    DROP CONSTRAINT IF EXISTS check_tipo_usuario;
                """)
                
                # Adicionar constraint para campo tipo
                cur.execute("""
                    ALTER TABLE usuarios 
                    DROP CONSTRAINT IF EXISTS check_tipo;
                """)
                
                cur.execute("""
                    ALTER TABLE usuarios 
                    ADD CONSTRAINT check_tipo 
                    CHECK (tipo IN ('admin', 'promoter', 'cliente', 'operador'));
                """)
                
                self.log_step("✅ Constraints do campo 'tipo' atualizadas", "SUCCESS")
                return True
                
        except Exception as e:
            self.log_step(f"Erro ao configurar constraints: {e}", "ERROR")
            return False
            
        finally:
            conn.close()
    
    def run_migration(self):
        """Executar verificações e correções necessárias"""
        self.log_step("=== AUTO MIGRAÇÃO RAILWAY - ATUALIZADA ===", "PROCESS")
        
        # 1. Verificar estrutura da tabela usuarios
        if not self.check_usuarios_table():
            self.log_step("❌ Estrutura da tabela usuarios incorreta", "ERROR")
            return False
        
        # 2. Garantir constraints corretas
        if not self.ensure_tipo_constraints():
            self.log_step("❌ Falha ao configurar constraints", "ERROR")
            return False
        
        self.log_step("✅ Auto migração concluída com sucesso!", "SUCCESS")
        return True

if __name__ == "__main__":
    migrator = RailwayAutoMigrate()
    success = migrator.run_migration()
    
    if not success:
        exit(1)
