#!/usr/bin/env python3
"""
🔄 RESTAURAR BACKUPS - Reverter correções incorretas de importação
"""
import os
import shutil
import json
from datetime import datetime

def restore_backups():
    """Restaura todos os arquivos dos backups"""
    
    backup_dir = "backend/backups_import_fix"
    target_dir = "backend"
    
    print("🔄 RESTAURANDO BACKUPS DAS CORREÇÕES INCORRETAS")
    print("=" * 60)
    
    restored_count = 0
    
    # Restaurar arquivos do app/routers
    backup_routers = os.path.join(backup_dir, "app", "routers")
    target_routers = os.path.join(target_dir, "app", "routers")
    
    if os.path.exists(backup_routers):
        for filename in os.listdir(backup_routers):
            if filename.endswith('.py'):
                backup_file = os.path.join(backup_routers, filename)
                target_file = os.path.join(target_routers, filename)
                
                try:
                    shutil.copy2(backup_file, target_file)
                    print(f"✅ Restaurado: {filename}")
                    restored_count += 1
                except Exception as e:
                    print(f"❌ Erro ao restaurar {filename}: {e}")
    
    # Restaurar outros arquivos se existirem
    backup_app = os.path.join(backup_dir, "app")
    target_app = os.path.join(target_dir, "app") 
    
    if os.path.exists(backup_app):
        for filename in os.listdir(backup_app):
            if filename.endswith('.py') and filename != 'routers':
                backup_file = os.path.join(backup_app, filename)
                target_file = os.path.join(target_app, filename)
                
                if os.path.isfile(backup_file):
                    try:
                        shutil.copy2(backup_file, target_file)
                        print(f"✅ Restaurado: app/{filename}")
                        restored_count += 1
                    except Exception as e:
                        print(f"❌ Erro ao restaurar app/{filename}: {e}")
    
    print("=" * 60)
    print(f"🎯 RESTAURAÇÃO CONCLUÍDA: {restored_count} arquivos restaurados")
    print("📝 Agora os arquivos estão de volta ao estado original")
    print("🔍 Próximo passo: investigar o verdadeiro problema das importações")

if __name__ == "__main__":
    restore_backups()
