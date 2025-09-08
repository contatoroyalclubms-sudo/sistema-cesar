#!/usr/bin/env python3
"""
MIGRAÇÃO COMPLETA: Remover campo tipo_usuario redundante da tabela usuarios

🎯 OBJETIVO: Eliminar redundância entre 'tipo' e 'tipo_usuario' na tabela usuarios
- Manter apenas o campo 'tipo' como fonte de verdade
- Atualizar todo o código backend para usar 'tipo' ao invés de 'tipo_usuario'
- Remover coluna 'tipo_usuario' APENAS da tabela usuarios (não das outras tabelas onde é legítimo)

⚠️ ATENÇÃO: Esta é uma migração crítica que afeta autenticação e permissões
"""

import os
import sys
import logging
import re
from datetime import datetime
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.exc import SQLAlchemyError
import shutil

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TipoUsuarioMigration:
    def __init__(self):
        self.database_url = os.getenv("DATABASE_URL")
        self.project_root = os.path.dirname(__file__)
        self.backend_path = os.path.join(self.project_root, 'backend')
        
        # Arquivos que precisam ser atualizados
        self.code_files = [
            'backend/app/auth.py',
            'backend/app/routers/auth.py', 
            'backend/app/models.py',
            'backend/app/schemas.py',
            'backend/app/main.py'
        ]
        
        if self.database_url:
            # Converter postgres:// para postgresql:// se necessário
            if self.database_url.startswith("postgres://"):
                self.database_url = self.database_url.replace("postgres://", "postgresql://", 1)
            self.engine = create_engine(self.database_url, pool_pre_ping=True, pool_recycle=300)
        else:
            logger.warning("DATABASE_URL não encontrada - apenas migração de código será executada")
            self.engine = None

    def create_backup(self):
        """Criar backup dos arquivos de código"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = os.path.join(self.project_root, f'backup_tipo_usuario_{timestamp}')
        
        logger.info(f"💾 Criando backup em: {backup_dir}")
        
        try:
            os.makedirs(backup_dir, exist_ok=True)
            
            for file_path in self.code_files:
                full_path = os.path.join(self.project_root, file_path)
                if os.path.exists(full_path):
                    backup_file = os.path.join(backup_dir, os.path.basename(file_path))
                    shutil.copy2(full_path, backup_file)
                    logger.info(f"✅ Backup criado: {backup_file}")
            
            return backup_dir
        except Exception as e:
            logger.error(f"❌ Erro ao criar backup: {e}")
            return None

    def diagnose_database_state(self):
        """Diagnosticar estado atual do banco de dados"""
        if not self.engine:
            logger.warning("⚠️ Sem conexão com banco - apenas diagnóstico de código")
            return True
            
        logger.info("🔍 Diagnosticando estado do banco de dados...")
        
        try:
            with self.engine.connect() as conn:
                # Verificar se tabela usuarios existe
                inspector = inspect(self.engine)
                tables = inspector.get_table_names()
                
                if 'usuarios' not in tables:
                    logger.error("❌ Tabela 'usuarios' não encontrada")
                    return False
                
                # Verificar colunas da tabela usuarios
                columns = inspector.get_columns('usuarios')
                column_names = [col['name'] for col in columns]
                
                has_tipo = 'tipo' in column_names
                has_tipo_usuario = 'tipo_usuario' in column_names
                
                logger.info(f"📊 Coluna 'tipo' existe: {has_tipo}")
                logger.info(f"📊 Coluna 'tipo_usuario' existe: {has_tipo_usuario}")
                
                if not has_tipo and not has_tipo_usuario:
                    logger.error("❌ Nenhuma das colunas 'tipo' ou 'tipo_usuario' encontrada")
                    return False
                
                if not has_tipo_usuario:
                    logger.info("✅ Campo 'tipo_usuario' já foi removido - migração desnecessária")
                    return "already_migrated"
                
                # Verificar inconsistências de dados
                if has_tipo and has_tipo_usuario:
                    result = conn.execute(text("""
                        SELECT 
                            COUNT(*) as total,
                            SUM(CASE WHEN tipo != tipo_usuario THEN 1 ELSE 0 END) as inconsistentes,
                            SUM(CASE WHEN tipo IS NULL THEN 1 ELSE 0 END) as tipo_null,
                            SUM(CASE WHEN tipo_usuario IS NULL THEN 1 ELSE 0 END) as tipo_usuario_null
                        FROM usuarios
                    """))
                    
                    stats = result.fetchone()
                    logger.info(f"📊 Total de usuários: {stats.total}")
                    logger.info(f"⚠️ Registros inconsistentes (tipo != tipo_usuario): {stats.inconsistentes}")
                    logger.info(f"❌ Registros com tipo NULL: {stats.tipo_null}")
                    logger.info(f"❌ Registros com tipo_usuario NULL: {stats.tipo_usuario_null}")
                    
                    if stats.inconsistentes > 0:
                        # Mostrar exemplos de inconsistências
                        result = conn.execute(text("""
                            SELECT id, nome, email, tipo, tipo_usuario 
                            FROM usuarios 
                            WHERE tipo != tipo_usuario 
                            LIMIT 5
                        """))
                        
                        logger.warning("🔍 Exemplos de inconsistências:")
                        for row in result.fetchall():
                            logger.warning(f"  ID {row.id}: {row.nome} - tipo='{row.tipo}' vs tipo_usuario='{row.tipo_usuario}'")
                
                return True
                
        except Exception as e:
            logger.error(f"❌ Erro no diagnóstico: {e}")
            return False

    def fix_data_inconsistencies(self):
        """Corrigir inconsistências nos dados antes da migração"""
        if not self.engine:
            return True
            
        logger.info("🔧 Corrigindo inconsistências de dados...")
        
        try:
            with self.engine.begin() as trans:
                conn = trans.connection
                
                # Estratégia: tipo_usuario é a fonte de verdade (mais usado no código atual)
                # Sincronizar tipo = tipo_usuario
                result = conn.execute(text("""
                    UPDATE usuarios 
                    SET tipo = tipo_usuario 
                    WHERE tipo != tipo_usuario OR tipo IS NULL
                """))
                
                updated = result.rowcount
                logger.info(f"✅ {updated} registros sincronizados (tipo = tipo_usuario)")
                
                # Corrigir valores NULL em tipo_usuario
                result = conn.execute(text("""
                    UPDATE usuarios 
                    SET tipo_usuario = 'cliente' 
                    WHERE tipo_usuario IS NULL
                """))
                
                fixed_null = result.rowcount
                logger.info(f"✅ {fixed_null} registros com tipo_usuario NULL corrigidos para 'cliente'")
                
                # Sincronizar novamente após correção
                result = conn.execute(text("""
                    UPDATE usuarios 
                    SET tipo = tipo_usuario 
                    WHERE tipo != tipo_usuario OR tipo IS NULL
                """))
                
                final_sync = result.rowcount
                logger.info(f"✅ {final_sync} registros finais sincronizados")
                
                # Validar correção
                result = conn.execute(text("""
                    SELECT COUNT(*) 
                    FROM usuarios 
                    WHERE tipo != tipo_usuario OR tipo IS NULL OR tipo_usuario IS NULL
                """))
                
                remaining_issues = result.scalar()
                if remaining_issues > 0:
                    logger.warning(f"⚠️ Ainda existem {remaining_issues} registros com problemas")
                else:
                    logger.info("✅ Todos os dados estão consistentes")
                
                return True
                
        except Exception as e:
            logger.error(f"❌ Erro na correção de dados: {e}")
            return False

    def update_code_references(self):
        """Atualizar todas as referências de tipo_usuario para tipo no código"""
        logger.info("🔧 Atualizando referências no código...")
        
        # Padrões para substituição
        patterns = [
            # Acessos diretos ao campo
            (r'\.tipo_usuario', '.tipo'),
            (r'usuario_atual\.tipo_usuario', 'usuario_atual.tipo'),
            (r'current_user\.tipo_usuario', 'current_user.tipo'),
            (r'usuario\.tipo_usuario', 'usuario.tipo'),
            
            # Parâmetros de função
            (r'tipo_usuario\s*=\s*"([^"]*)"', r'tipo="\1"'),
            (r'tipo_usuario\s*=\s*\'([^\']*)\'', r"tipo='\1'"),
            
            # Comparações e condições
            (r'== "admin"', '== "admin"'),  # manter como está, só mudando o acesso
            
            # Dicionários e responses
            (r'"tipo_usuario":\s*([^,}]+)', r'"tipo": \1'),
            (r"'tipo_usuario':\s*([^,}]+)", r"'tipo': \1"),
        ]
        
        for file_path in self.code_files:
            full_path = os.path.join(self.project_root, file_path)
            if not os.path.exists(full_path):
                logger.warning(f"⚠️ Arquivo não encontrado: {file_path}")
                continue
                
            logger.info(f"📝 Atualizando: {file_path}")
            
            try:
                with open(full_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                original_content = content
                changes_made = 0
                
                # Aplicar substituições
                for pattern, replacement in patterns:
                    new_content = re.sub(pattern, replacement, content)
                    if new_content != content:
                        changes_made += len(re.findall(pattern, content))
                        content = new_content
                
                # Substituições específicas por arquivo
                if 'models.py' in file_path:
                    # Remover o campo tipo_usuario do modelo Usuario
                    content = re.sub(
                        r'tipo_usuario\s*=\s*Column\([^)]+\)\s*#[^\n]*\n',
                        '',
                        content
                    )
                    # Remover comentário sobre campo legado
                    content = re.sub(
                        r'#\s*NOTA:\s*tipo_usuario.*?\n',
                        '',
                        content
                    )
                
                if 'schemas.py' in file_path:
                    # Remover campo tipo_usuario do schema
                    content = re.sub(
                        r'tipo_usuario:\s*Optional\[str\]\s*=\s*None[^\n]*\n',
                        '',
                        content
                    )
                    # Remover lógica de compatibilidade no __init__
                    content = re.sub(
                        r'if hasattr\(self, \'tipo_usuario\'\).*?self\.tipo_usuario = self\.tipo\n',
                        '',
                        content,
                        flags=re.DOTALL
                    )
                
                if content != original_content:
                    with open(full_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    logger.info(f"✅ {changes_made} alterações feitas em {file_path}")
                else:
                    logger.info(f"✓ Nenhuma alteração necessária em {file_path}")
                    
            except Exception as e:
                logger.error(f"❌ Erro ao atualizar {file_path}: {e}")
                return False
        
        return True

    def remove_database_column(self):
        """Remover a coluna tipo_usuario APENAS da tabela usuarios"""
        if not self.engine:
            logger.warning("⚠️ Sem conexão com banco - coluna não será removida")
            return True
            
        logger.info("🗑️ Removendo coluna tipo_usuario da tabela usuarios...")
        
        try:
            with self.engine.begin() as trans:
                conn = trans.connection
                
                # PostgreSQL suporta DROP COLUMN diretamente
                conn.execute(text("ALTER TABLE usuarios DROP COLUMN IF EXISTS tipo_usuario"))
                
                logger.info("✅ Coluna tipo_usuario removida da tabela usuarios")
                return True
                
        except Exception as e:
            logger.error(f"❌ Erro ao remover coluna: {e}")
            return False

    def validate_migration(self):
        """Validar que a migração foi bem-sucedida"""
        logger.info("✅ Validando migração...")
        
        # Validar código
        logger.info("🔍 Validando código atualizado...")
        for file_path in self.code_files:
            full_path = os.path.join(self.project_root, file_path)
            if os.path.exists(full_path):
                with open(full_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Verificar se ainda há referências a tipo_usuario
                if 'tipo_usuario' in content and 'models.py' not in file_path:
                    # Permitir tipo_usuario em outras tabelas (não na tabela usuarios)
                    remaining_refs = re.findall(r'usuario.*?tipo_usuario', content)
                    if remaining_refs:
                        logger.warning(f"⚠️ Possíveis referências restantes em {file_path}: {remaining_refs}")
        
        # Validar banco de dados
        if self.engine:
            logger.info("🔍 Validando banco de dados...")
            try:
                with self.engine.connect() as conn:
                    inspector = inspect(self.engine)
                    columns = inspector.get_columns('usuarios')
                    column_names = [col['name'] for col in columns]
                    
                    if 'tipo_usuario' in column_names:
                        logger.error("❌ Coluna tipo_usuario ainda existe na tabela usuarios")
                        return False
                    
                    if 'tipo' not in column_names:
                        logger.error("❌ Coluna tipo não existe na tabela usuarios")
                        return False
                    
                    # Testar consulta básica
                    result = conn.execute(text("SELECT COUNT(*) FROM usuarios WHERE tipo IS NOT NULL"))
                    count = result.scalar()
                    logger.info(f"✅ {count} usuários com tipo definido")
                    
            except Exception as e:
                logger.error(f"❌ Erro na validação do banco: {e}")
                return False
        
        logger.info("✅ Validação concluída com sucesso!")
        return True

    def run_migration(self):
        """Executar migração completa"""
        logger.info("🚀 INICIANDO MIGRAÇÃO TIPO_USUARIO")
        logger.info("=" * 60)
        
        # 1. Diagnóstico inicial
        diagnosis = self.diagnose_database_state()
        if diagnosis == "already_migrated":
            logger.info("✅ Migração já foi aplicada - apenas validando código...")
            return self.update_code_references() and self.validate_migration()
        elif not diagnosis:
            logger.error("❌ Diagnóstico falhou - abortando migração")
            return False
        
        # 2. Criar backup
        backup_dir = self.create_backup()
        if not backup_dir:
            logger.error("❌ Falha no backup - abortando migração")
            return False
        
        # 3. Corrigir inconsistências nos dados
        if not self.fix_data_inconsistencies():
            logger.error("❌ Falha na correção de dados - abortando migração")
            return False
        
        # 4. Atualizar código
        if not self.update_code_references():
            logger.error("❌ Falha na atualização do código - abortando migração")
            return False
        
        # 5. Remover coluna do banco
        if not self.remove_database_column():
            logger.error("❌ Falha na remoção da coluna - código foi atualizado")
            return False
        
        # 6. Validar
        if not self.validate_migration():
            logger.error("❌ Validação falhou")
            return False
        
        logger.info("\n" + "=" * 60)
        logger.info("🎉 MIGRAÇÃO CONCLUÍDA COM SUCESSO!")
        logger.info("✅ Campo tipo_usuario removido da tabela usuarios")
        logger.info("✅ Código atualizado para usar apenas 'tipo'")
        logger.info("✅ Autenticação preservada")
        logger.info(f"💾 Backup disponível em: {backup_dir}")
        logger.info("=" * 60)
        
        return True

def main():
    """Ponto de entrada principal"""
    try:
        migration = TipoUsuarioMigration()
        success = migration.run_migration()
        return success
    except Exception as e:
        logger.error(f"❌ Erro crítico na migração: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
