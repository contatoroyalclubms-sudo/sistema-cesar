import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.app.database import SessionLocal, engine
from backend.app.models import Usuario, Base
from backend.app.auth_functions import gerar_hash_senha
from datetime import datetime

# Criar todas as tabelas
Base.metadata.create_all(bind=engine)

# Criar sessão
db = SessionLocal()

try:
    # Verificar se usuário já existe
    usuario_existente = db.query(Usuario).filter(Usuario.cpf == "06601206154").first()
    if usuario_existente:
        print("Usuário já existe, removendo...")
        db.delete(usuario_existente)
        db.commit()
    
    usuario_existente2 = db.query(Usuario).filter(Usuario.cpf == "00000000000").first()
    if usuario_existente2:
        print("Usuário admin padrão já existe, removendo...")
        db.delete(usuario_existente2)
        db.commit()
    
    # Criar usuário principal para testes
    hash_senha = gerar_hash_senha("101112")
    novo_usuario = Usuario(
        cpf="06601206154",
        nome="Admin Teste",
        email="admin@teste.com",
        telefone="11999999999",
        senha_hash=hash_senha,
        tipo="admin",
        ativo=True,
        criado_em=datetime.now(),
        atualizado_em=datetime.now()
    )
    
    # Criar usuário padrão também
    hash_senha2 = gerar_hash_senha("0000")
    novo_usuario2 = Usuario(
        cpf="00000000000",
        nome="Admin Demo",
        email="admin@demo.com",
        telefone="11999999999",
        senha_hash=hash_senha2,
        tipo="admin",
        ativo=True,
        criado_em=datetime.now(),
        atualizado_em=datetime.now()
    )
    
    db.add(novo_usuario)
    db.add(novo_usuario2)
    db.commit()
    
    print("✅ Usuários criados via SQLAlchemy:")
    print(f"   CPF: 06601206154, Senha: 101112, Nome: {novo_usuario.nome}")
    print(f"   CPF: 00000000000, Senha: 0000, Nome: {novo_usuario2.nome}")
    
    # Verificar se consegue encontrar
    usuario_teste = db.query(Usuario).filter(Usuario.cpf == "06601206154").first()
    if usuario_teste:
        print(f"✅ Usuário encontrado via SQLAlchemy: {usuario_teste.nome}")
    else:
        print("❌ Usuário não encontrado via SQLAlchemy")
        
except Exception as e:
    print(f"Erro: {e}")
    db.rollback()
finally:
    db.close()
