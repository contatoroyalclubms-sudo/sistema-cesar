"""
Debug do problema de autenticação e Redis
"""
import os
import sys

# Configurar ambiente antes de importar qualquer coisa
os.environ["DISABLE_REDIS"] = "true"
os.environ["PYTHONDONTWRITEBYTECODE"] = "1"

# Adicionar diretório ao path
sys.path.insert(0, '.')

print("[DEBUG] Starting auth debug test...")
print(f"[DEBUG] DISABLE_REDIS = {os.environ.get('DISABLE_REDIS')}")

try:
    print("[DEBUG] Importing database...")
    from app.database import get_db, engine
    print("[SUCCESS] Database imported")
except Exception as e:
    print(f"[ERROR] Failed to import database: {e}")
    import traceback
    traceback.print_exc()

try:
    print("[DEBUG] Importing models...")
    from app.models import Usuario
    print("[SUCCESS] Models imported")
except Exception as e:
    print(f"[ERROR] Failed to import models: {e}")
    import traceback
    traceback.print_exc()

try:
    print("[DEBUG] Importing auth functions...")
    from app.auth_functions import autenticar_usuario, verificar_senha
    print("[SUCCESS] Auth functions imported")
except Exception as e:
    print(f"[ERROR] Failed to import auth functions: {e}")
    import traceback
    traceback.print_exc()

try:
    print("[DEBUG] Importing auth router...")
    from app.auth import router
    print("[SUCCESS] Auth router imported")
except Exception as e:
    print(f"[ERROR] Failed to import auth router: {e}")
    import traceback
    traceback.print_exc()

print("\n[DEBUG] Testing authentication flow...")

# Test authentication
from sqlalchemy.orm import Session

def test_auth():
    """Test authentication without Redis"""
    cpf = "06601206154"
    senha = "101112"
    
    # Get database session
    db = next(get_db())
    
    try:
        # Check if user exists
        print(f"[DEBUG] Looking for user with CPF: {cpf}")
        usuario = db.query(Usuario).filter(Usuario.cpf == cpf).first()
        
        if usuario:
            print(f"[SUCCESS] User found: {usuario.nome}")
            print(f"[DEBUG] User type: {usuario.tipo}")
            print(f"[DEBUG] User active: {usuario.ativo}")
            
            # Try to verify password
            print("[DEBUG] Testing password verification...")
            if verificar_senha(senha, usuario.senha_hash):
                print("[SUCCESS] Password is correct!")
            else:
                print("[ERROR] Password is incorrect")
        else:
            print(f"[ERROR] User not found with CPF: {cpf}")
            
            # List all users
            all_users = db.query(Usuario).all()
            print(f"\n[DEBUG] Total users in database: {len(all_users)}")
            for u in all_users[:5]:  # Show first 5 users
                print(f"  - CPF: {u.cpf}, Nome: {u.nome}, Tipo: {u.tipo}")
                
    finally:
        db.close()

if __name__ == "__main__":
    test_auth()