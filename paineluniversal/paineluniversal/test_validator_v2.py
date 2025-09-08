#!/usr/bin/env python3
"""
🧪 TESTE VALIDATOR PYDANTIC V2 - Isolado
========================================
"""

from pydantic import BaseModel, EmailStr, field_validator, ValidationError
from enum import Enum
import re

class TipoUsuario(str, Enum):
    ADMIN = "admin"
    PROMOTER = "promoter"
    CLIENTE = "cliente"

class UsuarioRegisterTest(BaseModel):
    cpf: str
    nome: str
    email: EmailStr
    telefone: str = None
    senha: str
    tipo: TipoUsuario = TipoUsuario.CLIENTE
    
    @field_validator('cpf')
    @classmethod
    def validar_cpf(cls, v):
        print(f"🔍 Validator executando para CPF: '{v}'")
        cpf = re.sub(r'\D', '', v)
        print(f"   CPF limpo: '{cpf}' (length: {len(cpf)})")
        if len(cpf) != 11:
            raise ValueError(f'CPF deve ter 11 dígitos, recebido: {len(cpf)}')
        return cpf
    
    @field_validator('nome')
    @classmethod 
    def validar_nome(cls, v):
        print(f"🔍 Validator executando para nome: '{v}'")
        if not v or not v.strip():
            raise ValueError('Nome não pode estar vazio')
        return v.strip()

def test_new_validator():
    """Teste com validator Pydantic v2"""
    print("🧪 TESTE VALIDATOR PYDANTIC V2")
    print("=" * 40)
    
    # Teste 1: Dados válidos
    print("\n1️⃣ Dados válidos:")
    try:
        user = UsuarioRegisterTest(
            cpf='12345678901',
            nome='Teste Valid',
            email='test@test.com',
            senha='123456'
        )
        print(f"✅ Sucesso: {user.model_dump()}")
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
    
    # Teste 2: CPF inválido
    print("\n2️⃣ CPF inválido (123):")
    try:
        user = UsuarioRegisterTest(
            cpf='123',
            nome='Teste',
            email='test@test.com',
            senha='123456'
        )
        print(f"❌ PROBLEMA: Passou quando deveria falhar: {user.model_dump()}")
    except ValidationError as e:
        print(f"✅ Rejeitado corretamente: {e.errors()}")
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
    
    # Teste 3: Nome vazio
    print("\n3️⃣ Nome vazio:")
    try:
        user = UsuarioRegisterTest(
            cpf='12345678901',
            nome='',
            email='test@test.com',
            senha='123456'
        )
        print(f"❌ PROBLEMA: Passou quando deveria falhar: {user.model_dump()}")
    except ValidationError as e:
        print(f"✅ Rejeitado corretamente: {e.errors()}")
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")

if __name__ == "__main__":
    test_new_validator()
