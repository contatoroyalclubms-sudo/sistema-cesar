#!/usr/bin/env python3
"""
Script para testar diretamente a serialização do usuário
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import get_db
from app.models import Usuario
from app.schemas import Usuario as UsuarioSchema
from sqlalchemy.orm import Session
import json

def test_user_serialization():
    """Testa a serialização do usuário"""
    
    # Obter sessão do banco
    db = next(get_db())
    
    try:
        # Buscar o usuário César
        usuario = db.query(Usuario).filter(Usuario.cpf == "06601206156").first()
        
        if not usuario:
            print("❌ Usuário não encontrado com CPF 06601206156")
            # Buscar qualquer usuário
            usuario = db.query(Usuario).first()
            
        if usuario:
            print(f"👤 Usuário encontrado: {usuario.nome}")
            print(f"   ID: {usuario.id}")
            print(f"   CPF: {usuario.cpf}")
            print(f"   Email: {usuario.email}")
            print(f"   Tipo (raw): {usuario.tipo}")
            print(f"   Tipo (value): {usuario.tipo.value if usuario.tipo else 'None'}")
            print(f"   Ativo: {usuario.ativo}")
            
            try:
                # Testar serialização com Pydantic
                usuario_serializado = UsuarioSchema.model_validate(usuario)
                print(f"\n✅ Serialização Pydantic bem-sucedida!")
                
                # Converter para dict
                usuario_dict = usuario_serializado.model_dump()
                print(f"📄 Dados serializados:")
                for key, value in usuario_dict.items():
                    print(f"   {key}: {value} ({type(value).__name__})")
                
                # Converter para JSON
                usuario_json = usuario_serializado.model_dump_json()
                print(f"\n📝 JSON resultante:")
                print(usuario_json)
                
            except Exception as e:
                print(f"❌ Erro na serialização Pydantic: {e}")
                
        else:
            print("❌ Nenhum usuário encontrado no banco")
            
    except Exception as e:
        print(f"❌ Erro: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    print("🔍 Testando serialização do usuário...")
    test_user_serialization()
