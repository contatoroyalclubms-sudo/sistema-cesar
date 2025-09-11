#!/usr/bin/env python3
"""
Teste específico para investigar o problema de empresa_id
"""
import os
import sys

# Adicionar o diretório backend ao path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

def main():
    print("🕵️ INVESTIGAÇÃO: Problema empresa_id")
    print("=" * 50)
    
    try:
        print("1️⃣ Verificando modelo Usuario...")
        from app.models import Usuario
        
        # Verificar campos do modelo Usuario
        print("📋 Campos do modelo Usuario:")
        for attr_name in dir(Usuario):
            if not attr_name.startswith('_'):
                attr = getattr(Usuario, attr_name)
                if hasattr(attr, 'property'):
                    print(f"  - {attr_name}: {attr.property.columns[0].type}")
        
        print("\n2️⃣ Verificando se empresa_id está presente...")
        has_empresa_id = hasattr(Usuario, 'empresa_id')
        print(f"🔍 Usuario.empresa_id existe? {has_empresa_id}")
        
        if has_empresa_id:
            empresa_id_attr = getattr(Usuario, 'empresa_id')
            print(f"📊 Tipo: {empresa_id_attr.property.columns[0].type}")
            print(f"🔒 Nullable: {empresa_id_attr.property.columns[0].nullable}")
            print(f"🎯 Default: {empresa_id_attr.property.columns[0].default}")
        
        print("\n3️⃣ Verificando outros modelos com empresa_id...")
        from app import models
        
        models_with_empresa_id = []
        for attr_name in dir(models):
            attr = getattr(models, attr_name)
            if hasattr(attr, '__tablename__') and hasattr(attr, 'empresa_id'):
                models_with_empresa_id.append(attr_name)
        
        print(f"📊 Modelos com empresa_id: {models_with_empresa_id}")
        
        print("\n4️⃣ Verificando schema de registro...")
        from app.schemas.auth import UsuarioCreate
        
        print("📋 Campos do schema UsuarioCreate:")
        for field_name, field_info in UsuarioCreate.__fields__.items():
            print(f"  - {field_name}: {field_info.type_} (required: {field_info.required})")
        
        print("\n✅ Investigação concluída!")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
