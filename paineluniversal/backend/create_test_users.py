#!/usr/bin/env python3
"""
Criar usuários de teste para o sistema
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import get_db
from app.models import Usuario
from app.auth import gerar_hash_senha

def create_test_users():
    """Criar usuários de teste"""
    
    db = next(get_db())
    
    try:
        print("Criando usuarios de teste...")
        
        # Criar promoter de teste
        promoter_existente = db.query(Usuario).filter(Usuario.cpf == "11111111111").first()
        if not promoter_existente:
            promoter = Usuario(
                cpf="11111111111",
                nome="Promoter Teste",
                email="promoter@teste.com",
                telefone="(11) 99999-1111",
                senha_hash=gerar_hash_senha("123456"),
                tipo_usuario="promoter",
                ativo=True
            )
            db.add(promoter)
            print("Promoter de teste criado:")
            print(f"  CPF: 111.111.111-11")
            print(f"  Senha: 123456")
        else:
            print("Promoter de teste ja existe")
        
        # Criar cliente de teste
        cliente_existente = db.query(Usuario).filter(Usuario.cpf == "22222222222").first()
        if not cliente_existente:
            cliente = Usuario(
                cpf="22222222222",
                nome="Cliente Teste",
                email="cliente@teste.com",
                telefone="(11) 99999-2222",
                senha_hash=gerar_hash_senha("123456"),
                tipo_usuario="cliente",
                ativo=True
            )
            db.add(cliente)
            print("Cliente de teste criado:")
            print(f"  CPF: 222.222.222-22")
            print(f"  Senha: 123456")
        else:
            print("Cliente de teste ja existe")
        
        db.commit()
        
        print("\nCredenciais de teste disponiveis:")
        print("ADMIN:")
        print("  CPF: 000.000.000-00")
        print("  Senha: admin123")
        print("PROMOTER:")
        print("  CPF: 111.111.111-11")
        print("  Senha: 123456")
        print("CLIENTE:")
        print("  CPF: 222.222.222-22")
        print("  Senha: 123456")
        
    except Exception as e:
        print(f"ERRO ao criar usuarios de teste: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_test_users()