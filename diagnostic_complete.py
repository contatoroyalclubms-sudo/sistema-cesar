#!/usr/bin/env python3
"""
Script de diagnóstico completo para problemas de cadastro de usuários.
Identifica e corrige discrepâncias entre Python e PostgreSQL.
"""

import os
import sys
import traceback

# Adicionar o diretório do projeto ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def diagnostic_complete():
    """Diagnóstico completo dos problemas de cadastro"""
    
    print("🔍 === DIAGNÓSTICO COMPLETO - CADASTRO DE USUÁRIOS ===\n")
    
    # 1. Verificar imports do Python
    print("1️⃣ VERIFICANDO ENUMS PYTHON:")
    try:
        from backend.app.models import TipoUsuario
        print(f"✅ TipoUsuario importado com sucesso")
        print(f"📋 Valores Python: {[(e.name, e.value) for e in TipoUsuario]}")
        
        # Testar criação de schema com cada valor
        from backend.app.schemas import UsuarioRegister
        print(f"✅ UsuarioRegister importado com sucesso")
        
        for tipo in TipoUsuario:
            try:
                user_test = UsuarioRegister(
                    cpf="12345678901",
                    nome="Teste User",
                    email="teste@teste.com", 
                    senha="senha123",
                    tipo=tipo
                )
                print(f"✅ Schema aceita tipo: {tipo.value} ({tipo.name})")
            except Exception as e:
                print(f"❌ Schema rejeita tipo {tipo.value}: {e}")
                
    except Exception as e:
        print(f"❌ Erro ao importar modelos Python: {e}")
        traceback.print_exc()
    
    print("\n2️⃣ VERIFICANDO ARQUIVOS FRONTEND:")
    
    # Listar arquivos relacionados ao cadastro
    frontend_files = [
        "frontend/src/components/auth/RegisterForm.tsx",
        "frontend/src/components/usuarios/CadastroUsuarioModal.tsx", 
        "frontend/src/types/database.ts",
        "frontend/src/services/api.ts",
        "frontend/src/services/api-new.ts"
    ]
    
    for file_path in frontend_files:
        full_path = os.path.join(os.path.dirname(__file__), file_path)
        if os.path.exists(full_path):
            print(f"✅ Encontrado: {file_path}")
            
            # Verificar se contém tipos de usuário
            try:
                with open(full_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if 'admin' in content and ('promoter' in content or 'cliente' in content):
                        print(f"   📋 Contém tipos de usuário: admin/promoter/cliente")
                    if "'admin'" in content:
                        lines_with_admin = [i+1 for i, line in enumerate(content.split('\n')) if "'admin'" in line]
                        print(f"   🔍 'admin' nas linhas: {lines_with_admin[:3]}...")  # Primeiras 3 linhas
            except Exception as e:
                print(f"   ❌ Erro ao ler arquivo: {e}")
        else:
            print(f"❌ Não encontrado: {file_path}")
    
    print("\n3️⃣ VERIFICANDO ARQUIVOS BACKEND:")
    
    backend_files = [
        "backend/app/models.py",
        "backend/app/schemas.py", 
        "backend/app/routers/auth.py",
        "backend/app/database.py"
    ]
    
    for file_path in backend_files:
        full_path = os.path.join(os.path.dirname(__file__), file_path)
        if os.path.exists(full_path):
            print(f"✅ Encontrado: {file_path}")
        else:
            print(f"❌ Não encontrado: {file_path}")
    
    print("\n4️⃣ IDENTIFICANDO ARQUIVOS DE MIGRAÇÃO:")
    
    migration_files = []
    for root, dirs, files in os.walk(os.path.dirname(__file__)):
        for file in files:
            if file.endswith('.sql') or 'migration' in file or 'migrate' in file:
                rel_path = os.path.relpath(os.path.join(root, file), os.path.dirname(__file__))
                migration_files.append(rel_path)
    
    print(f"📁 Arquivos de migração encontrados: {len(migration_files)}")
    for mf in migration_files[:10]:  # Primeiros 10
        print(f"   - {mf}")
    if len(migration_files) > 10:
        print(f"   ... e mais {len(migration_files) - 10} arquivos")
    
    print("\n5️⃣ PROPOSTA DE SOLUÇÃO:")
    print("📋 PASSOS PARA CORRIGIR O PROBLEMA:")
    print("1. ✅ Executar migração SQL: fix_enum_migration.sql")
    print("2. 🔄 Reiniciar o backend para aplicar mudanças")
    print("3. 🧪 Testar cadastro com valor 'admin'")
    print("4. 🛡️ Adicionar validação robusta no código")
    print("5. 📝 Monitorar logs para confirmar correção")
    
    print("\n6️⃣ AÇÕES RECOMENDADAS:")
    print("🚀 Execute os seguintes comandos:")
    print("   1. No terminal do PostgreSQL: \\i fix_enum_migration.sql")
    print("   2. Ou via psql: psql <DATABASE_URL> -f fix_enum_migration.sql")
    print("   3. Reiniciar o backend do Railway")
    print("   4. Testar cadastro via frontend")
    
    print("\n✅ DIAGNÓSTICO CONCLUÍDO!")

if __name__ == "__main__":
    diagnostic_complete()
