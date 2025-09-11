#!/usr/bin/env python3
"""
SCRIPT DEFINITIVO: Remove campo tipo_usuario e corrige toda a aplicação
"""

import os
import sys
import sqlite3
import re
from pathlib import Path
import shutil
import json

class RemoveTipoUsuarioDefinitivo:
    def __init__(self):
        self.backend_path = Path('./backend')
        self.db_path = './paineluniversal.db'  # SQLite principal
        self.eventos_db_path = './eventos.db'  # SQLite secundário
        
    def step1_backup_database(self):
        """Fazer backup do banco antes de qualquer alteração"""
        print("🔄 Fazendo backup do banco de dados...")
        
        backup_created = False
        
        # Backup paineluniversal.db
        if os.path.exists(self.db_path):
            backup_path = f"{self.db_path}.backup_remove_tipo_usuario"
            shutil.copy2(self.db_path, backup_path)
            print(f"✅ Backup criado: {backup_path}")
            backup_created = True
        
        # Backup eventos.db 
        if os.path.exists(self.eventos_db_path):
            backup_path = f"{self.eventos_db_path}.backup_remove_tipo_usuario"
            shutil.copy2(self.eventos_db_path, backup_path)
            print(f"✅ Backup criado: {backup_path}")
            backup_created = True
            
        # Backup banco no backend se existir
        backend_db = self.backend_path / 'eventos.db'
        if backend_db.exists():
            backup_path = f"{backend_db}.backup_remove_tipo_usuario"
            shutil.copy2(backend_db, backup_path)
            print(f"✅ Backup criado: {backup_path}")
            backup_created = True
        
        if not backup_created:
            print("⚠️ Nenhum banco de dados encontrado - será criado limpo")
        
        return True
    
    def fix_database_schema(self, db_path):
        """Corrigir schema de um banco específico"""
        if not os.path.exists(db_path):
            print(f"⚠️ Banco {db_path} não existe")
            return True
        
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Verificar se tipo_usuario existe
            cursor.execute("PRAGMA table_info(usuarios)")
            columns = cursor.fetchall()
            has_tipo_usuario = any(col[1] == 'tipo_usuario' for col in columns)
            
            if not has_tipo_usuario:
                print(f"✅ Campo tipo_usuario já não existe em {db_path}")
                conn.close()
                return True
            
            print(f"🔄 Removendo campo tipo_usuario de {db_path}...")
            
            # Criar nova tabela sem tipo_usuario
            cursor.execute('''
                CREATE TABLE usuarios_new (
                    id INTEGER PRIMARY KEY,
                    cpf VARCHAR(14) UNIQUE NOT NULL,
                    nome VARCHAR(255) NOT NULL,
                    email VARCHAR(255) UNIQUE NOT NULL,
                    telefone VARCHAR(20),
                    senha_hash VARCHAR(255) NOT NULL,
                    tipo VARCHAR(20) NOT NULL DEFAULT 'cliente',
                    ativo BOOLEAN DEFAULT 1,
                    ultimo_login DATETIME,
                    criado_em DATETIME DEFAULT CURRENT_TIMESTAMP,
                    atualizado_em DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Copiar dados (sem tipo_usuario)
            cursor.execute('''
                INSERT INTO usuarios_new (id, cpf, nome, email, telefone, senha_hash, tipo, ativo, ultimo_login, criado_em, atualizado_em)
                SELECT id, cpf, nome, email, telefone, senha_hash, 
                       COALESCE(tipo, 'cliente') as tipo, 
                       ativo, ultimo_login, criado_em, atualizado_em
                FROM usuarios
            ''')
            
            # Verificar integridade
            cursor.execute("SELECT COUNT(*) FROM usuarios")
            count_old = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM usuarios_new")
            count_new = cursor.fetchone()[0]
            
            if count_old != count_new:
                raise Exception(f"Erro na migração: {count_old} != {count_new}")
            
            # Aplicar mudanças
            cursor.execute("DROP TABLE usuarios")
            cursor.execute("ALTER TABLE usuarios_new RENAME TO usuarios")
            
            conn.commit()
            conn.close()
            print(f"✅ Campo tipo_usuario removido de {db_path}")
            return True
            
        except Exception as e:
            print(f"❌ Erro na migração do banco {db_path}: {e}")
            if conn:
                conn.rollback()
                conn.close()
            return False
    
    def step2_fix_database_schema(self):
        """Corrigir schema de todos os bancos"""
        print("🔧 Corrigindo schema dos bancos de dados...")
        
        success = True
        
        # Corrigir todos os bancos encontrados
        for db_path in [self.db_path, self.eventos_db_path, self.backend_path / 'eventos.db']:
            if os.path.exists(db_path):
                if not self.fix_database_schema(str(db_path)):
                    success = False
        
        return success
    
    def step3_fix_backend_models(self):
        """Corrigir modelos do backend"""
        print("🔧 Corrigindo modelos do backend...")
        
        models_file = self.backend_path / 'app' / 'models.py'
        
        if not models_file.exists():
            print("⚠️ Arquivo models.py não encontrado")
            return True
        
        with open(models_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Verificar se já está correto
        if 'tipo_usuario' not in content:
            print("✅ models.py já está correto")
            return True
        
        # Remover qualquer referência a tipo_usuario na classe Usuario
        original_content = content
        
        # Remover linhas com tipo_usuario = Column(...)
        content = re.sub(
            r'\s*tipo_usuario\s*=\s*Column\([^)]+\)[^\n]*\n?',
            '',
            content,
            flags=re.MULTILINE
        )
        
        # Remover tipo_usuario de outros modelos que não devem ter
        # Manter apenas nas tabelas que realmente precisam (como Lista, etc)
        
        if content != original_content:
            with open(models_file, 'w', encoding='utf-8') as f:
                f.write(content)
            print("✅ Modelos do backend corrigidos")
        else:
            print("✅ Modelos já estavam corretos")
        
        return True
    
    def step4_fix_backend_files(self):
        """Corrigir todos os arquivos do backend"""
        print("🔧 Corrigindo arquivos do backend...")
        
        files_to_check = [
            self.backend_path / 'app' / 'schemas.py',
            self.backend_path / 'app' / 'auth.py',
            self.backend_path / 'app' / 'main.py',
        ]
        
        # Adicionar arquivos de rotas
        routers_dir = self.backend_path / 'app' / 'routers'
        if routers_dir.exists():
            files_to_check.extend(routers_dir.glob('*.py'))
        
        fixed_files = []
        
        for file_path in files_to_check:
            if not file_path.exists():
                continue
                
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # Substituir tipo_usuario por tipo apenas em contextos de Usuario
            # Ser cuidadoso para não quebrar outros modelos que podem usar tipo_usuario legitimamente
            patterns = [
                (r'usuario\.tipo_usuario', 'usuario.tipo'),
                (r'user\.tipo_usuario', 'user.tipo'),
                (r'current_user\.tipo_usuario', 'current_user.tipo'),
                (r'db_user\.tipo_usuario', 'db_user.tipo'),
                (r'"tipo_usuario":\s*"([^"]*)"', r'"tipo": "\1"'),
                (r"'tipo_usuario':\s*'([^']*)'", r"'tipo': '\1'"),
            ]
            
            for pattern, replacement in patterns:
                content = re.sub(pattern, replacement, content)
            
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                fixed_files.append(file_path.name)
        
        if fixed_files:
            print(f"✅ Arquivos corrigidos: {', '.join(fixed_files)}")
        else:
            print("✅ Todos os arquivos já estavam corretos")
        
        return True
    
    def step5_fix_root_scripts(self):
        """Corrigir scripts na raiz do projeto"""
        print("🔧 Corrigindo scripts na raiz...")
        
        root_scripts = [
            Path('./create_cesar_local.py'),
            Path('./init_users.py'),
            Path('./create_admin_user.py'),
        ]
        
        # Procurar outros scripts Python na raiz
        for py_file in Path('.').glob('*.py'):
            if py_file not in root_scripts:
                root_scripts.append(py_file)
        
        fixed_files = []
        
        for script_path in root_scripts:
            if not script_path.exists():
                continue
                
            with open(script_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # Substituições específicas para scripts de usuário
            patterns = [
                (r'tipo_usuario\s*=\s*[\'"]([^\'"]*)[\'"]', r'tipo = "\1"'),
                (r'\.tipo_usuario', '.tipo'),
                (r'"tipo_usuario"', '"tipo"'),
                (r"'tipo_usuario'", "'tipo'"),
            ]
            
            for pattern, replacement in patterns:
                content = re.sub(pattern, replacement, content)
            
            if content != original_content:
                with open(script_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                fixed_files.append(script_path.name)
        
        if fixed_files:
            print(f"✅ Scripts corrigidos: {', '.join(fixed_files)}")
        else:
            print("✅ Todos os scripts já estavam corretos")
        
        return True
    
    def step6_create_clean_cesar(self):
        """Criar usuário César com schema limpo"""
        print("👤 Criando usuário César com schema correto...")
        
        try:
            # Adicionar backend ao path
            if str(self.backend_path) not in sys.path:
                sys.path.insert(0, str(self.backend_path))
            
            from app.database import get_db
            from app.models import Usuario
            from app.auth import gerar_hash_senha
            
            db = next(get_db())
            
            # Verificar se já existe
            existing = db.query(Usuario).filter(Usuario.cpf == '06601206156').first()
            if existing:
                print(f"✅ Usuário César já existe (Tipo: {existing.tipo})")
                if existing.tipo != 'admin':
                    existing.tipo = 'admin'
                    db.commit()
                    print("✅ Tipo atualizado para admin")
                db.close()
                return True
            
            # Criar novo
            senha_hash = gerar_hash_senha('101112')
            
            novo_usuario = Usuario(
                cpf='06601206156',
                nome='César',
                email='rosemberg@gmail.com',
                senha_hash=senha_hash,
                tipo='admin',  # APENAS este campo
                ativo=True
            )
            
            db.add(novo_usuario)
            db.commit()
            db.refresh(novo_usuario)
            
            print(f"✅ Usuário César criado:")
            print(f"   ID: {novo_usuario.id}")
            print(f"   Nome: {novo_usuario.nome}")
            print(f"   Tipo: {novo_usuario.tipo}")
            
            db.close()
            return True
            
        except Exception as e:
            print(f"❌ Erro ao criar César: {e}")
            print(f"   Detalhes: {str(e)}")
            return False
    
    def step7_test_backend_import(self):
        """Testar se modelos carregam sem erros"""
        print("🧪 Testando importação dos modelos...")
        
        try:
            # Limpar sys.path e modules para reimportar
            modules_to_remove = [key for key in sys.modules.keys() if key.startswith('app.')]
            for module in modules_to_remove:
                del sys.modules[module]
            
            # Adicionar backend ao path se não estiver
            backend_path = str(self.backend_path)
            if backend_path not in sys.path:
                sys.path.insert(0, backend_path)
            
            # Tentar importar modelos
            from app.models import Usuario, Evento, Lista
            print("✅ Modelos importados sem erro")
            
            # Verificar estrutura da classe Usuario
            user_fields = [attr for attr in dir(Usuario) if not attr.startswith('_')]
            has_tipo = 'tipo' in str(Usuario.__table__.columns)
            has_tipo_usuario = 'tipo_usuario' in str(Usuario.__table__.columns)
            
            print(f"✅ Usuario.tipo existe: {has_tipo}")
            print(f"✅ Usuario.tipo_usuario removido: {not has_tipo_usuario}")
            
            if has_tipo and not has_tipo_usuario:
                print("✅ Estrutura da classe Usuario está correta")
                return True
            else:
                print("❌ Estrutura da classe Usuario ainda tem problemas")
                return False
                
        except Exception as e:
            print(f"❌ Erro ao importar modelos: {e}")
            print(f"   Tipo do erro: {type(e).__name__}")
            print(f"   Detalhes: {str(e)}")
            return False
    
    def step8_cleanup_migration_files(self):
        """Limpar arquivos de migração antigos se necessário"""
        print("🧹 Limpando arquivos de migração antigos...")
        
        old_migration_files = [
            'migrate_debug.py',
            'migrate_simple.py', 
            'migrate_production.py',
            'auto_migrate_railway.py',
            'remove_evento_id_migration.py'
        ]
        
        cleaned_files = []
        for filename in old_migration_files:
            filepath = Path(filename)
            if filepath.exists():
                # Fazer backup antes de remover
                backup_name = f"{filename}.backup"
                shutil.move(str(filepath), backup_name)
                cleaned_files.append(filename)
        
        if cleaned_files:
            print(f"✅ Arquivos movidos para backup: {', '.join(cleaned_files)}")
        else:
            print("✅ Nenhum arquivo antigo encontrado")
        
        return True
    
    def step9_create_status_report(self):
        """Criar relatório de status da correção"""
        print("📋 Criando relatório de status...")
        
        status = {
            "timestamp": str(datetime.now()),
            "tipo_usuario_removal": {
                "databases_processed": [],
                "files_corrected": [],
                "backend_import_test": False,
                "cesar_user_created": False
            }
        }
        
        # Verificar bancos processados
        for db_path in [self.db_path, self.eventos_db_path]:
            if os.path.exists(db_path):
                status["tipo_usuario_removal"]["databases_processed"].append(db_path)
        
        # Testar importação final
        try:
            backend_path = str(self.backend_path)
            if backend_path not in sys.path:
                sys.path.insert(0, backend_path)
            
            from app.models import Usuario
            has_tipo_usuario = 'tipo_usuario' in str(Usuario.__table__.columns)
            status["tipo_usuario_removal"]["backend_import_test"] = not has_tipo_usuario
        except:
            status["tipo_usuario_removal"]["backend_import_test"] = False
        
        # Salvar relatório
        with open('tipo_usuario_removal_report.json', 'w') as f:
            json.dump(status, f, indent=2)
        
        print("✅ Relatório salvo em: tipo_usuario_removal_report.json")
        return True
    
    def execute(self):
        """Executar todos os passos da correção"""
        print("🚀 INICIANDO REMOÇÃO DEFINITIVA DO CAMPO tipo_usuario")
        print("=" * 60)
        
        steps = [
            ("Backup dos bancos de dados", self.step1_backup_database),
            ("Corrigir schema dos bancos", self.step2_fix_database_schema),
            ("Corrigir modelos do backend", self.step3_fix_backend_models),
            ("Corrigir arquivos do backend", self.step4_fix_backend_files),
            ("Corrigir scripts da raiz", self.step5_fix_root_scripts),
            ("Criar usuário César limpo", self.step6_create_clean_cesar),
            ("Testar importação do backend", self.step7_test_backend_import),
            ("Limpar arquivos antigos", self.step8_cleanup_migration_files),
            ("Criar relatório de status", self.step9_create_status_report),
        ]
        
        failed_steps = []
        
        for i, (description, step_func) in enumerate(steps, 1):
            print(f"\n📋 Passo {i}/9: {description}")
            try:
                success = step_func()
                if not success:
                    print(f"❌ Falha no passo {i}: {description}")
                    failed_steps.append(description)
                else:
                    print(f"✅ Passo {i} concluído com sucesso")
            except Exception as e:
                print(f"❌ Erro no passo {i}: {e}")
                failed_steps.append(f"{description} (Erro: {e})")
        
        print("\n" + "=" * 60)
        
        if not failed_steps:
            print("🎉 REMOÇÃO CONCLUÍDA COM SUCESSO!")
            print("\n📋 PRÓXIMOS PASSOS:")
            print("1. Reinicie o backend: cd backend && python -m uvicorn app.main:app --reload")
            print("2. Teste login com: CPF: 06601206156 | Senha: 101112")
            print("3. Verifique se não há mais erros relacionados a tipo_usuario")
            return True
        else:
            print("⚠️ REMOÇÃO CONCLUÍDA COM ALGUNS PROBLEMAS:")
            for failed in failed_steps:
                print(f"   - {failed}")
            print("\n📋 RECOMENDAÇÕES:")
            print("1. Revise os erros acima")
            print("2. Execute manualmente os passos que falharam")
            print("3. Teste o backend para verificar se funciona mesmo assim")
            return False

def main():
    """Função principal"""
    print("🎯 SCRIPT DE CORREÇÃO DEFINITIVA - tipo_usuario")
    print("Este script irá:")
    print("- Remover campo tipo_usuario de todos os bancos SQLite")
    print("- Corrigir todos os arquivos Python do projeto")
    print("- Recriar usuário César com schema limpo")
    print("- Testar se tudo funciona corretamente")
    
    resposta = input("\n❓ Continuar com a correção? (s/N): ").lower()
    if resposta not in ['s', 'sim', 'y', 'yes']:
        print("❌ Operação cancelada pelo usuário")
        return False
    
    remover = RemoveTipoUsuarioDefinitivo()
    success = remover.execute()
    
    return success

if __name__ == "__main__":
    success = main()
    
    if success:
        print("\n✅ Processo concluído com sucesso!")
        sys.exit(0)
    else:
        print("\n❌ Processo teve problemas. Verifique os logs acima.")
        sys.exit(1)
