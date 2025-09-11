"""
Teste direto do endpoint de login para debug
"""
import os
import sys
os.environ["DISABLE_REDIS"] = "true"
sys.path.insert(0, '.')

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_login():
    """Teste direto do login"""
    print("[TEST] Testing login endpoint...")
    
    response = client.post(
        "/api/auth/login",
        json={"cpf": "06601206154", "senha": "101112"}
    )
    
    print(f"[RESULT] Status: {response.status_code}")
    print(f"[RESULT] Response: {response.text}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"[SUCCESS] Token: {data.get('access_token', 'N/A')[:50]}...")
        print(f"[SUCCESS] User: {data.get('usuario', {}).get('nome', 'N/A')}")
    else:
        print(f"[ERROR] Login failed")

if __name__ == "__main__":
    test_login()