import requests
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import os

# Configurar conexão com banco (usando as mesmas configurações do backend)
database_url = os.environ.get("DATABASE_URL", "sqlite:///./paineluniversal.db")
engine = create_engine(database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def debug_usuario():
    """Debug da estrutura e dados do usuário"""
    
    print("🔍 Verificando estrutura da tabela usuarios...")
    
    with SessionLocal() as db:
        # Verificar estrutura da tabela
        result = db.execute(text("PRAGMA table_info(usuarios)"))
        columns = result.fetchall()
        
        print("📋 Estrutura da tabela usuarios:")
        for col in columns:
            print(f"  - {col[1]} ({col[2]}) - PK: {bool(col[5])}")
        
        print("\n🔍 Verificando dados do usuário com CPF 06601206154...")
        
        # Buscar usuário específico
        result = db.execute(text("SELECT * FROM usuarios WHERE cpf = '06601206154'"))
        user = result.fetchone()
        
        if user:
            print(f"✅ Usuário encontrado:")
            for i, col in enumerate(columns):
                print(f"  - {col[1]}: {user[i]}")
        else:
            print("❌ Usuário não encontrado")
            
        print("\n🔍 Verificando todos os usuários...")
        result = db.execute(text("SELECT id, cpf, nome, tipo FROM usuarios LIMIT 5"))
        users = result.fetchall()
        
        print("📋 Usuários na base:")
        for user in users:
            print(f"  ID: {user[0]}, CPF: {user[1]}, Nome: {user[2]}, Tipo: {user[3]}")

if __name__ == "__main__":
    debug_usuario()
