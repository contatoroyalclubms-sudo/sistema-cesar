#!/usr/bin/env python3
"""
Script para verificar e criar usuário CPF 06601206154 senha 101112
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import get_db
from app.models import Usuario
from app.auth_functions import gerar_hash_senha
from sqlalchemy.orm import Session

def main():
    db = next(get_db())
    
    try:
        # Verificar se usuário existe
        cpf_busca = "06601206154"
        usuario = db.query(Usuario).filter(Usuario.cpf == cpf_busca).first()
        
        if usuario:
            print(f"✅ Usuário encontrado:")
            print(f"   Nome: {usuario.nome}")
            print(f"   CPF: {usuario.cpf}")
            print(f"   Email: {usuario.email}")
            print(f"   Tipo: {usuario.tipo}")
            print(f"   Ativo: {usuario.ativo}")
            
            # Verificar senha
            from app.auth_functions import verificar_senha
            senha_correta = verificar_senha("101112", usuario.senha_hash)
            print(f"   Senha 101112 correta: {senha_correta}")
            
            if not senha_correta:
                print("🔄 Atualizando senha para 101112...")
                usuario.senha_hash = gerar_hash_senha("101112")
                db.commit()
                print("✅ Senha atualizada com sucesso!")
                
        else:
            print(f"❌ Usuário com CPF {cpf_busca} não encontrado")
            print("🔄 Criando usuário...")
            
            # Criar usuário
            novo_usuario = Usuario(
                cpf=cpf_busca,
                nome="Usuario Teste CPF 06601206154",
                email="usuario06601206154@teste.com",
                telefone="(11) 99999-0666",
                senha_hash=gerar_hash_senha("101112"),
                tipo="admin",
                ativo=True
            )
            
            db.add(novo_usuario)
            db.commit()
            db.refresh(novo_usuario)
            
            print(f"✅ Usuário criado com sucesso:")
            print(f"   ID: {novo_usuario.id}")
            print(f"   Nome: {novo_usuario.nome}")
            print(f"   CPF: {novo_usuario.cpf}")
            print(f"   Tipo: {novo_usuario.tipo}")
            
        # Listar todos os usuários
        print("\n📋 Todos os usuários no sistema:")
        usuarios = db.query(Usuario).all()
        for u in usuarios:
            print(f"   {u.id}: {u.nome} ({u.cpf}) - {u.tipo} - {'Ativo' if u.ativo else 'Inativo'}")
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    main()
