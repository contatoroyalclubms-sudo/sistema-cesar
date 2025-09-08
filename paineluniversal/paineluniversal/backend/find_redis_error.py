"""
Encontrar onde o Redis está sendo chamado
"""
import sys
import os
import importlib
import traceback

# Interceptar qualquer tentativa de conectar ao Redis
original_import = __builtins__.__import__

def mock_import(name, *args, **kwargs):
    if 'redis' in name.lower():
        print(f"[INTERCEPTED] Import of {name}")
        traceback.print_stack()
    return original_import(name, *args, **kwargs)

__builtins__.__import__ = mock_import

# Agora importar o app
os.environ["DISABLE_REDIS"] = "true"
sys.path.insert(0, '.')

try:
    print("[TESTING] Importing app.main...")
    from app.main import app
    print("[SUCCESS] App imported without Redis connection")
    
    # Simular uma requisição de login
    print("\n[TESTING] Simulating login request...")
    from fastapi.testclient import TestClient
    client = TestClient(app)
    
    response = client.post(
        "/api/auth/login",
        json={"cpf": "06601206154", "senha": "101112"}
    )
    
    print(f"[RESULT] Status: {response.status_code}")
    if response.status_code == 200:
        print("[SUCCESS] Login works!")
    else:
        print(f"[ERROR] Login failed: {response.text}")
        
except Exception as e:
    print(f"[ERROR] {e}")
    traceback.print_exc()