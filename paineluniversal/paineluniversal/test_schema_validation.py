#!/usr/bin/env python3
"""
🧪 TESTE VALIDAÇÃO SCHEMA - UsuarioRegister
===========================================
"""

import sys
import os
sys.path.append('.')

from backend.app.schemas import UsuarioRegister
from backend.app.models import TipoUsuario
from pydantic import ValidationError
import json

def test_valid_data():
    """Teste com dados válidos"""
    print("🧪 TESTE SCHEMA USUARIOREGISTER")
    print("=" * 40)
    
    test_data = {
        'cpf': '12345678901',
        'nome': 'Teste Schema',
        'email': 'test@test.com',
        'telefone': '11999999999',
        'senha': '123456',
        'tipo': TipoUsuario.CLIENTE
    }
    
    try:
        user = UsuarioRegister(**test_data)
        print("✅ Validação OK!")
        print(f"📋 Dados: {user.model_dump()}")
        return True
    except ValidationError as e:
        print("❌ Erro de validação:")
        for error in e.errors():
            print(f"   - {error['loc']}: {error['msg']}")
        return False
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return False

def test_invalid_data():
    """Teste com dados inválidos"""
    print("\n🚨 TESTE DADOS INVÁLIDOS")
    print("-" * 40)
    
    invalid_cases = [
        {
            "name": "CPF curto",
            "data": {'cpf': '123', 'nome': 'Teste', 'email': 'test@test.com', 'senha': '123456'}
        },
        {
            "name": "Email inválido",
            "data": {'cpf': '12345678901', 'nome': 'Teste', 'email': 'email_ruim', 'senha': '123456'}
        },
        {
            "name": "Nome vazio",
            "data": {'cpf': '12345678901', 'nome': '', 'email': 'test@test.com', 'senha': '123456'}
        }
    ]
    
    for case in invalid_cases:
        print(f"\n🧪 {case['name']}:")
        try:
            # Adicionar tipo padrão se não existe
            if 'tipo' not in case['data']:
                case['data']['tipo'] = TipoUsuario.CLIENTE
                
            user = UsuarioRegister(**case['data'])
            print(f"   ⚠️ Passou inesperadamente: {user.model_dump()}")
        except ValidationError as e:
            print(f"   ✅ Rejeitado corretamente: {e.errors()[0]['msg']}")
        except Exception as e:
            print(f"   ❌ Erro inesperado: {e}")

if __name__ == "__main__":
    success = test_valid_data()
    test_invalid_data()
    
    print(f"\n📊 RESULTADO: {'✅ Schema funcionando' if success else '❌ Schema com problemas'}")
