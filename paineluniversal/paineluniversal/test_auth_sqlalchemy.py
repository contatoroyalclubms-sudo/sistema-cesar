import sqlite3
from passlib.context import CryptContext
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Configurar SQLAlchemy como o backend
DATABASE_URL = "sqlite:///./eventos.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Configurar passlib como no backend
pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

# Simular a função de autenticação do backend
def test_autenticacao():
    db = SessionLocal()
    
    # Import do modelo (simulação)
    from backend.app.models import Usuario
    
    cpf = '06601206154'
    senha = '101112'
    
    print(f"Testando autenticação para CPF: {cpf}")
    
    # Buscar usuário
    usuario = db.query(Usuario).filter(Usuario.cpf == cpf).first()
    
    if not usuario:
        print("❌ Usuário não encontrado")
        return False
        
    print(f"✅ Usuário encontrado: {usuario.nome}, Tipo: {usuario.tipo}")
    print(f"Hash no banco: {usuario.senha_hash[:50]}...")
    
    # Verificar senha
    if pwd_context.verify(senha, usuario.senha_hash):
        print("✅ Senha verificada com sucesso!")
        return True
    else:
        print("❌ Senha incorreta!")
        return False
    
    db.close()

if __name__ == "__main__":
    test_autenticacao()
