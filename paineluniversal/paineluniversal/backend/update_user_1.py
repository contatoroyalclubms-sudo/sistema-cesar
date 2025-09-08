#!/usr/bin/env python3
"""
Script para atualizar o usuário ID 1 com tipo ADMIN
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import get_db
from app.models import Usuario
from sqlalchemy.orm import Session

def update_user_id_1():
    """Atualiza o usuário ID 1 para ter tipo ADMIN"""
    
    db = next(get_db())
    
    try:
        # Buscar usuário ID 1
        usuario = db.query(Usuario).filter(Usuario.id == 1).first()
        
        if usuario:
            print(f"👤 Usuário encontrado: {usuario.nome}")
            print(f"   ID: {usuario.id}")
            print(f"   CPF atual: {usuario.cpf}")
            print(f"   Tipo atual: {usuario.tipo}")
            
            # Atualizar para ADMIN
            usuario.tipo="admin"
            
            # Se não tem CPF correto, atualizar também
            if usuario.cpf != "06601206156":
                print(f"   Atualizando CPF de {usuario.cpf} para 06601206156")
                usuario.cpf = "06601206156"
            
            # Atualizar outros dados se necessário
            if usuario.nome != "César":
                print(f"   Atualizando nome de {usuario.nome} para César")
                usuario.nome = "César"
                
            if usuario.email != "rosemberg@gmail.com":
                print(f"   Atualizando email de {usuario.email} para rosemberg@gmail.com")
                usuario.email = "rosemberg@gmail.com"
            
            db.commit()
            db.refresh(usuario)
            
            print(f"\n✅ Usuário atualizado com sucesso!")
            print(f"   ID: {usuario.id}")
            print(f"   CPF: {usuario.cpf}")
            print(f"   Nome: {usuario.nome}")
            print(f"   Email: {usuario.email}")
            print(f"   Tipo: {usuario.tipo.value}")
            print(f"   Ativo: {usuario.ativo}")
            
        else:
            print("❌ Usuário ID 1 não encontrado")
            
    except Exception as e:
        print(f"❌ Erro ao atualizar usuário: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("🔧 Atualizando usuário ID 1...")
    update_user_id_1()
