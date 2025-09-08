"""
Script de validação completa do sistema após remoção de tipo_usuario
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import os
from datetime import datetime
import sys

class SystemValidation:
    def __init__(self):
        self.database_url = self._get_database_url()
        
    def _get_database_url(self):
        """Detectar URL do banco"""
        return (
            os.getenv("DATABASE_URL") or
            os.getenv("POSTGRES_URL") or  
            os.getenv("PGDATABASE_URL") or
            "postgresql://postgres:password@localhost:5432/paineluniversal"
        )
        
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
            conn = psycopg2.connect(self.database_url)
            conn.autocommit = True
            return conn
        except Exception as e:
            self.log_step(f"Erro ao conectar: {e}", "ERROR")
            return None
    
    def validate_usuarios_table(self, conn):
        """Validar estrutura da tabela usuarios"""
        try:
            self.log_step("Validando tabela usuarios...", "PROCESS")
            
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                # Verificar colunas
                cur.execute("""
                    SELECT column_name, data_type, is_nullable, column_default
                    FROM information_schema.columns
                    WHERE table_name = 'usuarios'
                    ORDER BY ordinal_position;
                """)
                
                columns = cur.fetchall()
                column_names = [col['column_name'] for col in columns]
                
                # Verificações essenciais
                required_columns = ['id', 'cpf', 'nome', 'email', 'tipo', 'senha_hash']
                forbidden_columns = ['tipo_usuario']
                
                missing_columns = [col for col in required_columns if col not in column_names]
                forbidden_present = [col for col in forbidden_columns if col in column_names]
                
                if missing_columns:
                    self.log_step(f"❌ Colunas obrigatórias faltando: {missing_columns}", "ERROR")
                    return False
                
                if forbidden_present:
                    self.log_step(f"❌ Colunas proibidas presentes: {forbidden_present}", "ERROR")
                    return False
                
                # Verificar tipo de dados do campo tipo
                tipo_column = next((col for col in columns if col['column_name'] == 'tipo'), None)
                if tipo_column:
                    self.log_step(f"✅ Campo 'tipo': {tipo_column['data_type']}", "SUCCESS")
                
                # Verificar constraints
                cur.execute("""
                    SELECT constraint_name, check_clause
                    FROM information_schema.check_constraints
                    WHERE constraint_schema = 'public'
                    AND constraint_name LIKE '%tipo%';
                """)
                
                constraints = cur.fetchall()
                
                valid_constraints = []
                invalid_constraints = []
                
                for constraint in constraints:
                    if 'check_tipo_usuario' in constraint['constraint_name']:
                        invalid_constraints.append(constraint['constraint_name'])
                    elif 'check_tipo' in constraint['constraint_name']:
                        valid_constraints.append(constraint['constraint_name'])
                
                if invalid_constraints:
                    self.log_step(f"❌ Constraints inválidas: {invalid_constraints}", "ERROR")
                    return False
                
                if valid_constraints:
                    self.log_step(f"✅ Constraints válidas: {valid_constraints}", "SUCCESS")
                
                self.log_step("✅ Tabela usuarios validada com sucesso", "SUCCESS")
                return True
                
        except Exception as e:
            self.log_step(f"Erro na validação: {e}", "ERROR")
            return False
    
    def validate_data_integrity(self, conn):
        """Validar integridade dos dados de usuários"""
        try:
            self.log_step("Validando integridade dos dados...", "PROCESS")
            
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                # Verificar se todos os usuários têm tipo válido
                cur.execute("""
                    SELECT COUNT(*) as total,
                           COUNT(CASE WHEN tipo IN ('admin', 'promoter', 'cliente', 'operador') THEN 1 END) as valid_tipos,
                           COUNT(CASE WHEN tipo IS NULL THEN 1 END) as null_tipos
                    FROM usuarios;
                """)
                
                stats = cur.fetchone()
                
                self.log_step(f"📊 Total usuários: {stats['total']}", "INFO")
                self.log_step(f"📊 Tipos válidos: {stats['valid_tipos']}", "INFO")
                self.log_step(f"📊 Tipos NULL: {stats['null_tipos']}", "INFO")
                
                if stats['null_tipos'] > 0:
                    self.log_step(f"❌ {stats['null_tipos']} usuários com tipo NULL", "ERROR")
                    return False
                
                if stats['valid_tipos'] != stats['total']:
                    # Verificar tipos inválidos
                    cur.execute("""
                        SELECT id, cpf, nome, tipo
                        FROM usuarios
                        WHERE tipo NOT IN ('admin', 'promoter', 'cliente', 'operador')
                        OR tipo IS NULL;
                    """)
                    
                    invalid_users = cur.fetchall()
                    
                    self.log_step(f"❌ Usuários com tipos inválidos:", "ERROR")
                    for user in invalid_users:
                        self.log_step(f"   ID: {user['id']}, CPF: {user['cpf']}, Tipo: '{user['tipo']}'", "ERROR")
                    
                    return False
                
                # Verificar distribuição de tipos
                cur.execute("""
                    SELECT tipo, COUNT(*) as count
                    FROM usuarios
                    GROUP BY tipo
                    ORDER BY count DESC;
                """)
                
                distribution = cur.fetchall()
                
                self.log_step("📊 Distribuição de tipos de usuário:", "INFO")
                for dist in distribution:
                    self.log_step(f"   {dist['tipo']}: {dist['count']} usuários", "INFO")
                
                self.log_step("✅ Integridade dos dados validada", "SUCCESS")
                return True
                
        except Exception as e:
            self.log_step(f"Erro na validação de dados: {e}", "ERROR")
            return False
    
    def validate_other_tables(self, conn):
        """Validar que outras tabelas não foram afetadas"""
        try:
            self.log_step("Validando outras tabelas...", "PROCESS")
            
            # Tabelas que devem ter tipo_usuario legitimamente
            expected_tables = {
                'listas': 'TipoLista enum',
                'produtos': 'TipoProduto enum', 
                'comandas': 'TipoComanda enum',
                'formas_pagamento': 'TipoFormaPagamento enum'
            }
            
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                for table_name, description in expected_tables.items():
                    cur.execute("""
                        SELECT EXISTS (
                            SELECT FROM information_schema.columns
                            WHERE table_name = %s
                            AND column_name = 'tipo_usuario'
                        );
                    """, (table_name,))
                    
                    exists = cur.fetchone()[0]
                    
                    if exists:
                        self.log_step(f"✅ Tabela {table_name}: tipo_usuario presente ({description})", "SUCCESS")
                    else:
                        self.log_step(f"⚠️ Tabela {table_name}: tipo_usuario ausente", "WARNING")
            
            self.log_step("✅ Outras tabelas validadas", "SUCCESS")
            return True
            
        except Exception as e:
            self.log_step(f"Erro na validação de outras tabelas: {e}", "ERROR")
            return False
    
    def run_full_validation(self):
        """Executar validação completa do sistema"""
        self.log_step("=== VALIDAÇÃO COMPLETA DO SISTEMA ===", "PROCESS")
        
        conn = self.connect_db()
        if not conn:
            return False
        
        try:
            # 1. Validar estrutura da tabela usuarios
            if not self.validate_usuarios_table(conn):
                self.log_step("❌ Falha na validação da tabela usuarios", "ERROR")
                return False
            
            # 2. Validar integridade dos dados
            if not self.validate_data_integrity(conn):
                self.log_step("❌ Falha na validação de integridade", "ERROR")
                return False
            
            # 3. Validar outras tabelas
            if not self.validate_other_tables(conn):
                self.log_step("❌ Falha na validação de outras tabelas", "ERROR")
                return False
            
            self.log_step("🎉 SISTEMA COMPLETAMENTE VALIDADO!", "SUCCESS")
            self.log_step("✅ Pronto para deploy em produção", "SUCCESS")
            return True
            
        except Exception as e:
            self.log_step(f"Erro durante validação: {e}", "ERROR")
            return False
            
        finally:
            conn.close()

if __name__ == "__main__":
    validator = SystemValidation()
    success = validator.run_full_validation()
    
    if success:
        print("\\n🎉 Validação concluída com sucesso!")
        print("✅ Sistema pronto para deploy")
        sys.exit(0)
    else:
        print("\\n❌ Validação falhou!")
        print("⚠️ Corrija os problemas antes do deploy")
        sys.exit(1)
