#!/usr/bin/env python3
"""
Script para corrigir usuários sem tipo definido
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import get_db
from app.models import Usuario
from sqlalchemy.orm import Session

def fix_user_types():
    """Corrige usuários sem tipo definido"""
    
    # Obter sessão do banco
    db = next(get_db())
    
    try:
        # Buscar usuários sem tipo ou com tipo None
        usuarios_sem_tipo = db.query(Usuario).filter(
            (Usuario.tipo.is_(None)) | 
            (Usuario.tipo_usuario== "")
        ).all()
        
        print(f"🔍 Encontrados {len(usuarios_sem_tipo)} usuários sem tipo definido")
        
        for usuario in usuarios_sem_tipo:
            print(f"\n👤 Usuário: {usuario.nome} (ID: {usuario.id})")
            print(f"   Email: {usuario.email}")
            print(f"   CPF: {usuario.cpf}")
            print(f"   Tipo atual: {usuario.tipo}")
            
            # Definir tipo baseado no usuário
            if usuario.id == 1 or usuario.nome.lower() in ['césar', 'cesar', 'admin']:
                novo_tipo = "admin"
                print(f"   ✅ Definindo como ADMIN")
            else:
                novo_tipo = "promoter"
                print(f"   ✅ Definindo como PROMOTER")
            
            # Atualizar usuário
            usuario.tipo_usuario=novo_tipo
            
        # Salvar alterações
        db.commit()
        
        print(f"\n🎉 Correção concluída!")
        print(f"📊 Total de usuários corrigidos: {len(usuarios_sem_tipo)}")
        
        # Verificar resultado
        print(f"\n🔍 Verificando resultado...")
        todos_usuarios = db.query(Usuario).all()
        
        for usuario in todos_usuarios:
            print(f"👤 {usuario.nome} (ID: {usuario.id}) - Tipo: {usuario.tipo.value if usuario.tipo else 'None'}")
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("🔧 Iniciando correção de tipos de usuário...")
    fix_user_types()
