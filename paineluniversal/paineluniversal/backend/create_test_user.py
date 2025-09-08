"""
Criar usuário de teste no banco de dados
"""
import os
import sys

# Configurar ambiente
os.environ["DISABLE_REDIS"] = "true"
sys.path.insert(0, '.')

from app.database import engine, SessionLocal
from app.models import Usuario
from app.auth_functions import gerar_hash_senha
from datetime import datetime

def create_test_user():
    """Criar usuário de teste"""
    db = SessionLocal()
    
    try:
        # CPF e senha do teste
        cpf = "06601206154"
        senha = "101112"
        
        # Verificar se usuário já existe
        existing = db.query(Usuario).filter(Usuario.cpf == cpf).first()
        
        if existing:
            print(f"[INFO] Usuário já existe: {existing.nome}")
            # Atualizar senha
            existing.senha_hash = gerar_hash_senha(senha)
            existing.ativo = True
            existing.tipo = "admin"
            db.commit()
            print(f"[SUCCESS] Senha atualizada para usuário {cpf}")
        else:
            # Criar novo usuário
            new_user = Usuario(
                cpf=cpf,
                nome="Usuário Teste",
                email="teste@example.com",
                telefone="11999999999",
                senha_hash=gerar_hash_senha(senha),
                tipo="admin",
                ativo=True,
                criado_em=datetime.now()
            )
            db.add(new_user)
            db.commit()
            print(f"[SUCCESS] Usuário criado: CPF={cpf}, Senha={senha}")
            
        # Verificar se foi criado/atualizado
        user = db.query(Usuario).filter(Usuario.cpf == cpf).first()
        if user:
            print(f"\n[INFO] Usuário no banco:")
            print(f"  ID: {user.id}")
            print(f"  Nome: {user.nome}")
            print(f"  CPF: {user.cpf}")
            print(f"  Email: {user.email}")
            print(f"  Tipo: {user.tipo}")
            print(f"  Ativo: {user.ativo}")
            
    except Exception as e:
        print(f"[ERROR] Erro ao criar usuário: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_test_user()