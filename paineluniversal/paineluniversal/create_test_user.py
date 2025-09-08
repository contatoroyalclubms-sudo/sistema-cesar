from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import os
import bcrypt

# Configurar conexão com banco
database_url = os.environ.get("DATABASE_URL", "sqlite:///./paineluniversal.db")
engine = create_engine(database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_test_user():
    """Criar usuário de teste com as credenciais fornecidas"""
    
    print("👤 Criando usuário de teste...")
    
    # Gerar hash da senha
    senha = "101112"
    senha_hash = bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    with SessionLocal() as db:
        # Verificar se usuário já existe
        result = db.execute(text("SELECT id FROM usuarios WHERE cpf = '06601206154'"))
        existing = result.fetchone()
        
        if existing:
            print("⚠️ Usuário já existe, atualizando...")
            db.execute(text("""
                UPDATE usuarios 
                SET nome = 'Admin Teste', 
                    email = 'admin@teste.com',
                    telefone = '11999999999',
                    senha_hash = :senha_hash,
                    tipo = 'admin',
                    ativo = 1
                WHERE cpf = '06601206154'
            """), {"senha_hash": senha_hash})
        else:
            print("✅ Criando novo usuário...")
            db.execute(text("""
                INSERT INTO usuarios (
                    cpf, nome, email, telefone, senha_hash, tipo, ativo, criado_em
                ) VALUES (
                    '06601206154', 'Admin Teste', 'admin@teste.com', '11999999999', 
                    :senha_hash, 'admin', 1, datetime('now')
                )
            """), {"senha_hash": senha_hash})
        
        db.commit()
        
        # Verificar se foi criado/atualizado
        result = db.execute(text("SELECT id, cpf, nome, tipo FROM usuarios WHERE cpf = '06601206154'"))
        user = result.fetchone()
        
        if user:
            print(f"✅ Usuário criado/atualizado: ID {user[0]}, CPF {user[1]}, Nome: {user[2]}, Tipo: {user[3]}")
        else:
            print("❌ Erro ao criar usuário")

if __name__ == "__main__":
    create_test_user()
