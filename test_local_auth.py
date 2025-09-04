#!/usr/bin/env python3
"""
Teste local para verificar funcionamento da correção
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.app.database import get_db
from backend.app.models import Usuario
from backend.app.auth import get_user_tipo, verificar_permissao_admin

def test_local_auth():
    print("🧪 TESTE LOCAL - VERIFICAÇÃO DE PERMISSÕES")
    print("=" * 50)
    
    db = next(get_db())
    
    # Buscar César
    cesar = db.query(Usuario).filter(Usuario.nome == 'César').first()
    if not cesar:
        print("❌ César não encontrado")
        return
        
    print(f"✅ César encontrado:")
    print(f"   ID: {cesar.id}")
    print(f"   Nome: {cesar.nome}")
    print(f"   CPF: {cesar.cpf}")
    print(f"   tipo (banco): '{cesar.tipo}'")
    print(f"   tipo_usuario (banco): '{cesar.tipo_usuario}'")
    print(f"   ativo: {cesar.ativo}")
    
    # Testar função helper
    tipo_detectado = get_user_tipo(cesar)
    print(f"\n🔍 Função get_user_tipo():")
    print(f"   Resultado: '{tipo_detectado}'")
    print(f"   É admin? {tipo_detectado == 'admin'}")
    
    # Simular verificação de permissão admin
    print(f"\n🛡️ Simulação verificar_permissao_admin:")
    try:
        if tipo_detectado == "admin":
            print(f"   ✅ SUCESSO - César tem permissões de admin")
        else:
            print(f"   ❌ FALHA - César não tem permissões de admin")
            print(f"   Tipo detectado: '{tipo_detectado}' != 'admin'")
    except Exception as e:
        print(f"   ❌ ERRO: {e}")
    
    # Verificar se o problema é específico do schema
    print(f"\n📋 Teste de serialização do schema:")
    try:
        from backend.app.schemas import Usuario as UsuarioSchema
        
        # Criar dicionário manual como no endpoint /me corrigido
        user_dict = {
            "id": cesar.id,
            "cpf": cesar.cpf,
            "nome": cesar.nome,
            "email": cesar.email,
            "telefone": cesar.telefone,
            "tipo": tipo_detectado,
            "tipo_usuario": tipo_detectado,
            "ativo": cesar.ativo,
            "ultimo_login": cesar.ultimo_login,
            "criado_em": cesar.criado_em,
            "atualizado_em": cesar.atualizado_em
        }
        
        # Validar com Pydantic
        usuario_schema = UsuarioSchema(**user_dict)
        print(f"   ✅ Schema válido:")
        print(f"   tipo: '{usuario_schema.tipo}'")
        print(f"   tipo_usuario: '{usuario_schema.tipo_usuario}'")
        
    except Exception as e:
        print(f"   ❌ Erro no schema: {e}")
    
    db.close()

if __name__ == "__main__":
    test_local_auth()
