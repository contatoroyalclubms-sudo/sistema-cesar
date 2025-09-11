"""
Migração para remover coluna tipo_usuario duplicada
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import os
from datetime import datetime
import sys

class RemoveTipoUsuarioMigration:
    def __init__(self):
        # Detectar URL do banco (Railway ou local)
        self.database_url = (
            os.getenv("DATABASE_URL") or
            os.getenv("POSTGRES_URL") or  
            os.getenv("PGDATABASE_URL") or
            "postgresql://postgres:password@localhost:5432/paineluniversal"
        )
        
        self.backup_file = f"backup_tipo_usuario_{datetime.now().strftime('%Y%m%d_%H%M%S')}.sql"
        
    def log_step(self, message, status="INFO"):
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
    
    def check_table_structure(self, conn):
        """Verificar estrutura atual da tabela usuarios"""
        try:
            self.log_step("Verificando estrutura da tabela usuarios...", "PROCESS")
            
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT column_name, data_type, is_nullable, column_default
                    FROM information_schema.columns
                    WHERE table_name = 'usuarios'
                    ORDER BY ordinal_position;
                """)
                
                columns = cur.fetchall()
                
                # Verificar se tipo_usuario existe
                tipo_usuario_exists = any(col['column_name'] == 'tipo_usuario' for col in columns)
                tipo_exists = any(col['column_name'] == 'tipo' for col in columns)
                
                self.log_step(f"Coluna 'tipo' existe: {tipo_exists}", "INFO")
                self.log_step(f"Coluna 'tipo_usuario' existe: {tipo_usuario_exists}", "INFO")
                
                return {
                    'tipo_usuario_exists': tipo_usuario_exists,
                    'tipo_exists': tipo_exists,
                    'columns': columns
                }
                
        except Exception as e:
            self.log_step(f"Erro ao verificar estrutura: {e}", "ERROR")
            return None
    
    def backup_data(self, conn):
        """Backup dos dados antes da migração"""
        try:
            self.log_step("Fazendo backup dos dados...", "PROCESS")
            
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT id, cpf, nome, email, tipo, 
                           tipo_usuario
                    FROM usuarios
                    ORDER BY id;
                """)
                
                users = cur.fetchall()
                
                # Salvar backup em arquivo
                with open(self.backup_file, 'w', encoding='utf-8') as f:
                    f.write("-- Backup da tabela usuarios antes de remover tipo_usuario\\n")
                    f.write(f"-- Data: {datetime.now()}\\n\\n")
                    
                    for user in users:
                        f.write(f"-- Usuario ID: {user['id']}\\n")
                        f.write(f"-- CPF: {user['cpf']}, Nome: {user['nome']}\\n")
                        f.write(f"-- tipo: '{user['tipo']}', tipo_usuario: '{user.get('tipo_usuario', 'NULL')}'\\n\\n")
                
                self.log_step(f"Backup salvo em: {self.backup_file}", "SUCCESS")
                return users
                
        except Exception as e:
            self.log_step(f"Erro no backup: {e}", "ERROR")
            return None
    
    def migrate_data_if_needed(self, conn, users_data):
        """Migrar dados de tipo_usuario para tipo se necessário"""
        try:
            self.log_step("Verificando necessidade de migração de dados...", "PROCESS")
            
            # Verificar se há discrepâncias entre tipo e tipo_usuario
            discrepancies = []
            updates_needed = []
            
            for user in users_data:
                tipo = user.get('tipo')
                tipo_usuario = user.get('tipo_usuario')
                
                if tipo_usuario and tipo != tipo_usuario:
                    discrepancies.append({
                        'id': user['id'],
                        'cpf': user['cpf'],
                        'tipo': tipo,
                        'tipo_usuario': tipo_usuario
                    })
                    
                    # Se tipo está vazio mas tipo_usuario tem valor
                    if not tipo and tipo_usuario:
                        updates_needed.append({
                            'id': user['id'],
                            'new_tipo': tipo_usuario
                        })
            
            if discrepancies:
                self.log_step(f"Encontradas {len(discrepancies)} discrepâncias:", "WARNING")
                for disc in discrepancies:
                    self.log_step(f"  ID {disc['id']}: tipo='{disc['tipo']}' vs tipo_usuario='{disc['tipo_usuario']}'", "WARNING")
            
            if updates_needed:
                self.log_step(f"Atualizando {len(updates_needed)} registros...", "PROCESS")
                
                with conn.cursor() as cur:
                    for update in updates_needed:
                        cur.execute("""
                            UPDATE usuarios 
                            SET tipo = %s 
                            WHERE id = %s
                        """, (update['new_tipo'], update['id']))
                        
                        self.log_step(f"Atualizado usuario ID {update['id']} tipo='{update['new_tipo']}'", "SUCCESS")
            
            return True
            
        except Exception as e:
            self.log_step(f"Erro na migração de dados: {e}", "ERROR")
            return False
    
    def remove_tipo_usuario_column(self, conn):
        """Remover a coluna tipo_usuario"""
        try:
            self.log_step("Removendo coluna tipo_usuario...", "PROCESS")
            
            with conn.cursor() as cur:
                # Primeiro remover constraints se existirem
                cur.execute("""
                    ALTER TABLE usuarios 
                    DROP CONSTRAINT IF EXISTS check_tipo_usuario;
                """)
                self.log_step("Constraint check_tipo_usuario removida", "SUCCESS")
                
                # Remover a coluna
                cur.execute("""
                    ALTER TABLE usuarios 
                    DROP COLUMN IF EXISTS tipo_usuario;
                """)
                self.log_step("Coluna tipo_usuario removida com sucesso!", "SUCCESS")
                
                return True
                
        except Exception as e:
            self.log_step(f"Erro ao remover coluna: {e}", "ERROR")
            return False
    
    def verify_final_structure(self, conn):
        """Verificar estrutura final da tabela"""
        try:
            self.log_step("Verificando estrutura final...", "PROCESS")
            
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT column_name, data_type, is_nullable
                    FROM information_schema.columns
                    WHERE table_name = 'usuarios'
                    ORDER BY ordinal_position;
                """)
                
                columns = cur.fetchall()
                
                # Verificar que tipo existe e tipo_usuario não existe
                tipo_exists = any(col['column_name'] == 'tipo' for col in columns)
                tipo_usuario_exists = any(col['column_name'] == 'tipo_usuario' for col in columns)
                
                if tipo_exists and not tipo_usuario_exists:
                    self.log_step("✅ Estrutura final correta: apenas campo 'tipo' existe", "SUCCESS")
                    return True
                else:
                    self.log_step(f"❌ Estrutura incorreta: tipo={tipo_exists}, tipo_usuario={tipo_usuario_exists}", "ERROR")
                    return False
                    
        except Exception as e:
            self.log_step(f"Erro na verificação: {e}", "ERROR")
            return False
    
    def run_migration(self):
        """Executar migração completa"""
        self.log_step("=== INICIANDO MIGRAÇÃO: REMOÇÃO DE tipo_usuario ===", "PROCESS")
        
        # Conectar ao banco
        conn = self.connect_db()
        if not conn:
            return False
        
        try:
            # 1. Verificar estrutura atual
            structure = self.check_table_structure(conn)
            if not structure:
                return False
            
            if not structure['tipo_usuario_exists']:
                self.log_step("Coluna tipo_usuario não existe. Migração não necessária.", "INFO")
                return True
            
            if not structure['tipo_exists']:
                self.log_step("ERRO: Coluna 'tipo' não existe! Migração abortada.", "ERROR")
                return False
            
            # 2. Backup dos dados
            users_data = self.backup_data(conn)
            if not users_data:
                return False
            
            # 3. Migrar dados se necessário
            if not self.migrate_data_if_needed(conn, users_data):
                return False
            
            # 4. Remover coluna tipo_usuario
            if not self.remove_tipo_usuario_column(conn):
                return False
            
            # 5. Verificar estrutura final
            if not self.verify_final_structure(conn):
                return False
            
            self.log_step("=== MIGRAÇÃO CONCLUÍDA COM SUCESSO! ===", "SUCCESS")
            return True
            
        except Exception as e:
            self.log_step(f"Erro durante migração: {e}", "ERROR")
            return False
            
        finally:
            conn.close()

if __name__ == "__main__":
    migration = RemoveTipoUsuarioMigration()
    success = migration.run_migration()
    
    if success:
        print("\\n🎉 Migração executada com sucesso!")
        sys.exit(0)
    else:
        print("\\n❌ Migração falhou!")
        sys.exit(1)
