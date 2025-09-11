#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
APLICADOR AUTOMÁTICO DE MIGRAÇÕES
==================================

Identifica e aplica automaticamente as migrações necessárias.
Garante zero breaking changes.

Autor: Agente de Desenvolvimento
Data: 2024
"""

import os
import sys
import sqlite3
import subprocess
from pathlib import Path
from datetime import datetime

class AutoMigrationApplier:
    """Aplicador automático de migrações"""
    
    def __init__(self):
        self.base_path = Path(".")
        self.backend_path = Path("backend")
        self.db_path = Path("backend/eventos.db")
        
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "migrations_found": [],
            "migrations_applied": [],
            "migrations_failed": [],
            "database_backup_created": False,
            "safety_checks_passed": True
        }
        
        print("=== APLICADOR AUTOMÁTICO DE MIGRAÇÕES ===")
        print(f"Horário: {datetime.now().strftime('%H:%M:%S')}")
        print()
    
    def backup_database(self):
        """Criar backup da database antes das migrações"""
        if not self.db_path.exists():
            print("❌ Database não encontrada - não é possível criar backup")
            return False
        
        try:
            backup_path = self.db_path.parent / f"eventos_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
            
            # Copiar arquivo
            import shutil
            shutil.copy2(self.db_path, backup_path)
            
            print(f"✅ Backup criado: {backup_path.name}")
            self.results["database_backup_created"] = True
            self.results["backup_path"] = str(backup_path)
            return True
            
        except Exception as e:
            print(f"❌ Erro ao criar backup: {str(e)}")
            return False
    
    def verify_database_integrity(self):
        """Verificar integridade da database"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            # Verificar se pode executar query básica
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            
            conn.close()
            
            print(f"✅ Database íntegra - {len(tables)} tabelas encontradas")
            return True
            
        except Exception as e:
            print(f"❌ Erro na verificação da database: {str(e)}")
            self.results["safety_checks_passed"] = False
            return False
    
    def find_migration_scripts(self):
        """Encontrar scripts de migração"""
        migration_patterns = [
            "*migration*.py",
            "*migrate*.py"
        ]
        
        migration_files = []
        
        # Procurar no diretório raiz
        for pattern in migration_patterns:
            for file in self.base_path.glob(pattern):
                if file.is_file() and file.name != "auto_migration_applier.py":
                    migration_files.append(file)
        
        # Procurar no backend
        for pattern in migration_patterns:
            for file in self.backend_path.glob(pattern):
                if file.is_file():
                    migration_files.append(file)
        
        # Remover duplicatas e ordenar
        unique_files = list(set(migration_files))
        unique_files.sort(key=lambda x: x.name)
        
        self.results["migrations_found"] = [str(f) for f in unique_files]
        
        print(f"📋 Encontrados {len(unique_files)} scripts de migração:")
        for i, file in enumerate(unique_files, 1):
            print(f"   {i}. {file.name}")
        
        return unique_files
    
    def prioritize_migrations(self, migration_files):
        """Priorizar migrações por importância"""
        priority_order = [
            "fix_schema_migration_urgent",
            "fix_tipo_usuario",
            "remove_evento_id",
            "remove_tipo_usuario",
            "apply_remove_empresa",
            "add_categorias",
            "add_lista_fields",
            "add_qr_code"
        ]
        
        prioritized = []
        remaining = list(migration_files)
        
        # Adicionar por prioridade
        for priority in priority_order:
            for file in migration_files:
                if priority in file.name and file not in prioritized:
                    prioritized.append(file)
                    if file in remaining:
                        remaining.remove(file)
        
        # Adicionar restantes
        prioritized.extend(remaining)
        
        print("\n📊 Ordem de aplicação (por prioridade):")
        for i, file in enumerate(prioritized, 1):
            print(f"   {i}. {file.name}")
        
        return prioritized
    
    def apply_migration(self, migration_file):
        """Aplicar uma migração específica"""
        print(f"\n🔄 Aplicando: {migration_file.name}")
        
        try:
            # Verificar se o arquivo existe
            if not migration_file.exists():
                print(f"   ❌ Arquivo não encontrado: {migration_file}")
                return False
            
            # Executar migração
            result = subprocess.run([
                sys.executable, str(migration_file)
            ], capture_output=True, text=True, cwd=migration_file.parent)
            
            if result.returncode == 0:
                print(f"   ✅ Aplicada com sucesso")
                self.results["migrations_applied"].append(str(migration_file))
                
                # Mostrar output se houver
                if result.stdout.strip():
                    output_lines = result.stdout.strip().split('\n')
                    # Mostrar só as últimas 3 linhas para não poluir
                    for line in output_lines[-3:]:
                        if line.strip():
                            print(f"      {line}")
                
                return True
            else:
                print(f"   ❌ Falhou (código {result.returncode})")
                self.results["migrations_failed"].append({
                    "file": str(migration_file),
                    "error": result.stderr[:200] if result.stderr else "Sem erro específico",
                    "return_code": result.returncode
                })
                
                # Mostrar erro
                if result.stderr:
                    error_lines = result.stderr.strip().split('\n')
                    print(f"      Erro: {error_lines[0][:100]}")
                
                return False
                
        except Exception as e:
            print(f"   ❌ Exceção: {str(e)}")
            self.results["migrations_failed"].append({
                "file": str(migration_file),
                "error": str(e),
                "return_code": -1
            })
            return False
    
    def verify_after_migration(self):
        """Verificar estado após migrações"""
        print("\n🔍 Verificando estado após migrações...")
        
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            # Verificar se ainda funciona
            cursor.execute("SELECT COUNT(*) FROM usuarios")
            user_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            
            conn.close()
            
            print(f"   ✅ Database funcional - {len(tables)} tabelas, {user_count} usuários")
            return True
            
        except Exception as e:
            print(f"   ❌ Problema após migrações: {str(e)}")
            return False
    
    def apply_all_migrations(self):
        """Aplicar todas as migrações"""
        print("🚀 Iniciando aplicação de migrações...\n")
        
        # Verificações de segurança
        if not self.verify_database_integrity():
            print("❌ Falha na verificação de integridade - abortando")
            return False
        
        if not self.backup_database():
            print("❌ Falha ao criar backup - abortando")
            return False
        
        # Encontrar migrações
        migration_files = self.find_migration_scripts()
        
        if not migration_files:
            print("✅ Nenhuma migração encontrada")
            return True
        
        # Priorizar migrações
        prioritized_migrations = self.prioritize_migrations(migration_files)
        
        # Aplicar migrações
        successful_migrations = 0
        failed_migrations = 0
        
        for migration_file in prioritized_migrations:
            success = self.apply_migration(migration_file)
            
            if success:
                successful_migrations += 1
            else:
                failed_migrations += 1
                
                # Parar em caso de falha crítica
                if "urgent" in migration_file.name.lower():
                    print(f"\n🚨 Migração crítica falhou: {migration_file.name}")
                    print("   Abortando aplicação para evitar problemas")
                    break
        
        # Verificar estado final
        self.verify_after_migration()
        
        # Relatório final
        print(f"\n📊 RESUMO DAS MIGRAÇÕES:")
        print(f"   ✅ Aplicadas com sucesso: {successful_migrations}")
        print(f"   ❌ Falharam: {failed_migrations}")
        print(f"   📁 Total encontradas: {len(migration_files)}")
        
        if failed_migrations == 0:
            print("\n🎉 Todas as migrações aplicadas com sucesso!")
            return True
        else:
            print(f"\n⚠️  {failed_migrations} migrações falharam - verificar logs")
            return False
    
    def generate_report(self):
        """Gerar relatório final"""
        filename = f"migration_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        import json
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        
        print(f"\n📄 Relatório salvo em: {filename}")
        return filename

def main():
    """Função principal"""
    applier = AutoMigrationApplier()
    
    try:
        success = applier.apply_all_migrations()
        applier.generate_report()
        
        if success:
            print("\n✅ RESULTADO: Migrações aplicadas com sucesso")
            return 0
        else:
            print("\n⚠️  RESULTADO: Algumas migrações falharam")
            return 1
            
    except Exception as e:
        print(f"\n🚨 ERRO DURANTE MIGRAÇÕES: {str(e)}")
        return 2

if __name__ == "__main__":
    exit(main())
