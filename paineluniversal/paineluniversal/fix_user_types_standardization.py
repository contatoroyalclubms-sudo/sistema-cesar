#!/usr/bin/env python3
"""
🔧 CORREÇÃO CRÍTICA: Padronização de Tipos de Usuário
Corrigir inconsistências de case nos tipos após migração ENUM->VARCHAR
"""

import sqlite3
import os
import shutil
from datetime import datetime

def standardize_user_types(db_path):
    """Padronizar tipos de usuário para minúsculas"""
    print(f"\n🔧 Padronizando tipos em {db_path}...")
    
    try:
        # Criar backup
        backup_path = f"{db_path}.backup_types_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        shutil.copy2(db_path, backup_path)
        print(f"✅ Backup criado: {backup_path}")
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Verificar estado atual
        cursor.execute("SELECT id, nome, tipo, tipo_usuario FROM usuarios LIMIT 10;")
        users_before = cursor.fetchall()
        
        print(f"   📊 Estado ANTES da padronização:")
        for user in users_before:
            user_id, nome, tipo, tipo_usuario = user
            print(f"      ID {user_id}: {nome} | tipo='{tipo}' | tipo_usuario='{tipo_usuario}'")
        
        # Mapeamento de padronização (maiúsculas -> minúsculas)
        type_mapping = {
            'ADMIN': 'admin',
            'PROMOTER': 'promoter', 
            'CLIENTE': 'cliente',
            'OPERADOR': 'operador',
            'admin': 'admin',
            'promoter': 'promoter',
            'cliente': 'cliente',
            'operador': 'operador'
        }
        
        # Atualizar campo 'tipo' para minúsculas
        print(f"   🔄 Padronizando campo 'tipo'...")
        for old_type, new_type in type_mapping.items():
            cursor.execute("UPDATE usuarios SET tipo = ? WHERE tipo = ?", (new_type, old_type))
            updated = cursor.rowcount
            if updated > 0:
                print(f"      '{old_type}' -> '{new_type}': {updated} registros")
        
        # Garantir que tipo_usuario seja preenchido corretamente
        print(f"   🔄 Sincronizando tipo_usuario...")
        
        # Se tipo_usuario está NULL, copiar de tipo
        cursor.execute("UPDATE usuarios SET tipo_usuario = tipo WHERE tipo_usuario IS NULL")
        null_fixed = cursor.rowcount
        if null_fixed > 0:
            print(f"      Preenchidos {null_fixed} campos tipo_usuario que estavam NULL")
        
        # Padronizar tipo_usuario também
        for old_type, new_type in type_mapping.items():
            cursor.execute("UPDATE usuarios SET tipo_usuario = ? WHERE tipo_usuario = ?", (new_type, old_type))
            updated = cursor.rowcount
            if updated > 0:
                print(f"      tipo_usuario '{old_type}' -> '{new_type}': {updated} registros")
        
        # Verificar resultado final
        cursor.execute("SELECT id, nome, tipo, tipo_usuario FROM usuarios LIMIT 10;")
        users_after = cursor.fetchall()
        
        print(f"   📊 Estado DEPOIS da padronização:")
        for user in users_after:
            user_id, nome, tipo, tipo_usuario = user
            print(f"      ID {user_id}: {nome} | tipo='{tipo}' | tipo_usuario='{tipo_usuario}'")
        
        # Validar que todos os tipos são válidos
        cursor.execute("SELECT DISTINCT tipo FROM usuarios;")
        tipos_distintos = [row[0] for row in cursor.fetchall()]
        
        cursor.execute("SELECT DISTINCT tipo_usuario FROM usuarios WHERE tipo_usuario IS NOT NULL;")
        tipos_usuario_distintos = [row[0] for row in cursor.fetchall()]
        
        valid_types = ['admin', 'promoter', 'cliente', 'operador']
        invalid_tipos = [t for t in tipos_distintos if t not in valid_types]
        invalid_tipos_usuario = [t for t in tipos_usuario_distintos if t not in valid_types]
        
        if invalid_tipos:
            print(f"   ⚠️ TIPOS INVÁLIDOS encontrados em 'tipo': {invalid_tipos}")
        else:
            print(f"   ✅ Todos os tipos são válidos: {tipos_distintos}")
            
        if invalid_tipos_usuario:
            print(f"   ⚠️ TIPOS INVÁLIDOS encontrados em 'tipo_usuario': {invalid_tipos_usuario}")
        else:
            print(f"   ✅ Todos os tipos_usuario são válidos: {tipos_usuario_distintos}")
        
        conn.commit()
        conn.close()
        print(f"   ✅ Padronização concluída para {db_path}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Erro na padronização de {db_path}: {e}")
        # Restaurar backup em caso de erro
        if 'backup_path' in locals():
            shutil.copy2(backup_path, db_path)
            print(f"   🔄 Backup restaurado")
        return False

def update_backend_auth_validation():
    """Atualizar validação no backend para ser case-insensitive"""
    print(f"\n🔧 AJUSTE NO BACKEND: Validação case-insensitive")
    
    auth_file = "backend/app/routers/auth.py"
    
    if not os.path.exists(auth_file):
        print(f"❌ Arquivo não encontrado: {auth_file}")
        return False
    
    try:
        with open(auth_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Verificar se já tem normalização
        if 'lower()' in content and 'tipo_usuario' in content:
            print("✅ Backend já tem normalização case-insensitive")
            return True
        
        print("💡 Sugestão de código para adicionar ao backend:")
        print("""
# No auth.py, após buscar o usuário:
if usuario:
    # Normalizar tipo_usuario para minúsculas
    if usuario.tipo_usuario:
        usuario.tipo_usuario = usuario.tipo_usuario.lower()
    
    # Garantir tipos válidos
    valid_types = ['admin', 'promoter', 'cliente', 'operador']
    if usuario.tipo_usuario not in valid_types:
        print(f"⚠️ Tipo inválido detectado: {usuario.tipo_usuario}, normalizando para 'cliente'")
        usuario.tipo_usuario = 'cliente'
""")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao verificar backend: {e}")
        return False

def main():
    """Executar padronização completa"""
    print("🚀 CORREÇÃO CRÍTICA: Padronização de Tipos de Usuário")
    print("=" * 60)
    
    databases = [
        "paineluniversal.db",
        "backend/eventos.db"
    ]
    
    success_count = 0
    for db_path in databases:
        if os.path.exists(db_path):
            if standardize_user_types(db_path):
                success_count += 1
        else:
            print(f"❌ Banco não encontrado: {db_path}")
    
    # Atualizar backend
    update_backend_auth_validation()
    
    print(f"\n🎯 RESULTADO FINAL:")
    print(f"   Bancos corrigidos: {success_count}/{len([db for db in databases if os.path.exists(db)])}")
    
    if success_count > 0:
        print(f"\n✅ PRÓXIMOS PASSOS:")
        print("1. Testar login com os tipos padronizados")
        print("2. Verificar se o frontend recebe os dados corretos")  
        print("3. Aplicar mesma correção no PostgreSQL de produção")
        print("4. Monitorar logs para garantir que não há mais erros de tipo")
        
        print(f"\n🧪 TESTE IMEDIATO:")
        print("Execute: python test_login_after_migration.py")
    else:
        print(f"\n⚠️ Nenhum banco foi corrigido - verificar problemas")

if __name__ == "__main__":
    main()
