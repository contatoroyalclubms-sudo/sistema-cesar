#!/usr/bin/env python3
"""
Teste para verificar se os validators Pydantic v2 estão funcionando corretamente
após as edições manuais do usuário.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_validators():
    try:
        # Importar diretamente do arquivo schemas.py, evitando o __init__.py
        import importlib.util
        import os
        
        schemas_path = os.path.join(os.path.dirname(__file__), 'backend', 'app', 'schemas.py')
        spec = importlib.util.spec_from_file_location("schemas", schemas_path)
        schemas_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(schemas_module)
        
        UsuarioRegister = schemas_module.UsuarioRegister
        EmpresaCreate = schemas_module.EmpresaCreate
        
        from backend.app.models import TipoUsuario
        from pydantic import ValidationError
        
        print("=== TESTE VALIDATORS PYDANTIC V2 ===")
        print("Importações realizadas com sucesso!")
        
        # Teste 1: CPF inválido (muito curto)
        print("\n1. Testando CPF inválido (123)...")
        try:
            user = UsuarioRegister(
                cpf='123', 
                nome='Test', 
                email='test@test.com', 
                senha='123',
                tipo=TipoUsuario.CLIENTE
            )
            print("❌ FALHOU: aceitou CPF inválido '123'")
            return False
        except ValidationError as e:
            print("✅ SUCESSO: rejeitou CPF inválido")
            print(f"   Erro: {e.errors()[0]['msg']}")
        except Exception as e:
            print(f"⚠️ ERRO INESPERADO: {e}")
            return False
        
        # Teste 2: CPF válido
        print("\n2. Testando CPF válido...")
        try:
            user = UsuarioRegister(
                cpf='12345678901', 
                nome='Test User', 
                email='test@test.com', 
                senha='senha123',
                tipo=TipoUsuario.CLIENTE
            )
            print("✅ SUCESSO: aceitou CPF válido")
            print(f"   CPF processado: {user.cpf}")
        except Exception as e:
            print(f"❌ FALHOU: rejeitou CPF válido - {e}")
            return False
        
        # Teste 3: Email inválido
        print("\n3. Testando email inválido...")
        try:
            user = UsuarioRegister(
                cpf='12345678901', 
                nome='Test', 
                email='email_invalido', 
                senha='123',
                tipo=TipoUsuario.CLIENTE
            )
            print("❌ FALHOU: aceitou email inválido")
            return False
        except ValidationError as e:
            print("✅ SUCESSO: rejeitou email inválido")
            print(f"   Erro: {e.errors()[0]['msg']}")
        except Exception as e:
            print(f"⚠️ ERRO INESPERADO: {e}")
            return False
        
        # Teste 4: Nome vazio
        print("\n4. Testando nome vazio...")
        try:
            user = UsuarioRegister(
                cpf='12345678901', 
                nome='', 
                email='test@test.com', 
                senha='123',
                tipo=TipoUsuario.CLIENTE
            )
            print("❌ FALHOU: aceitou nome vazio")
            return False
        except ValidationError as e:
            print("✅ SUCESSO: rejeitou nome vazio")
            print(f"   Erro: {e.errors()[0]['msg']}")
        except Exception as e:
            print(f"⚠️ ERRO INESPERADO: {e}")
            return False
        
        # Teste 5: EmpresaCreate CNPJ
        print("\n5. Testando CNPJ inválido...")
        try:
            empresa = EmpresaCreate(
                nome='Empresa Test',
                cnpj='123',
                email='empresa@test.com'
            )
            print("❌ FALHOU: aceitou CNPJ inválido")
            return False
        except ValidationError as e:
            print("✅ SUCESSO: rejeitou CNPJ inválido")
            print(f"   Erro: {e.errors()[0]['msg']}")
        except Exception as e:
            print(f"⚠️ ERRO INESPERADO: {e}")
            return False
        
        print("\n=== RESULTADO FINAL ===")
        print("✅ TODOS OS TESTES PASSARAM!")
        print("✅ Validators Pydantic v2 funcionando corretamente!")
        return True
        
    except ImportError as e:
        print(f"❌ ERRO DE IMPORTAÇÃO: {e}")
        return False
    except Exception as e:
        print(f"❌ ERRO GERAL: {e}")
        return False

if __name__ == "__main__":
    success = test_validators()
    sys.exit(0 if success else 1)
