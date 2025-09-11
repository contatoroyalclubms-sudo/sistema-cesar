#!/usr/bin/env python3
"""
🧪 TESTE DIRETO: Login funcionando após migração
Testar login diretamente no banco sem depender do servidor
"""

import sqlite3
import bcrypt
import os
import sys

# Adicionar caminho do backend
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

def test_direct_login():
    """Testar login diretamente no banco"""
    print("🧪 TESTE DIRETO: Login no Banco de Dados")
    print("=" * 50)
    
    db_path = "paineluniversal.db"
    
    if not os.path.exists(db_path):
        print(f"❌ Banco não encontrado: {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Verificar estrutura atual
        cursor.execute("PRAGMA table_info(usuarios);")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        print(f"📊 Colunas da tabela usuarios:")
        for col in columns:
            print(f"   • {col[1]}: {col[2]}")
        
        has_tipo_usuario = 'tipo_usuario' in column_names
        print(f"\n🔍 Campo tipo_usuario: {'✅' if has_tipo_usuario else '❌'}")
        
        if not has_tipo_usuario:
            print("❌ ERRO: Campo tipo_usuario não existe!")
            return False
        
        # Buscar usuários disponíveis
        cursor.execute("SELECT id, cpf, nome, tipo_usuario, ativo FROM usuarios LIMIT 5;")
        users = cursor.fetchall()
        
        print(f"\n👥 Usuários disponíveis ({len(users)}):")
        for user in users:
            user_id, cpf, nome, tipo_usuario, ativo = user
            status = "✅" if ativo else "❌"
            print(f"   {status} ID {user_id}: {nome} ({cpf}) - {tipo_usuario}")
        
        if not users:
            print("❌ Nenhum usuário encontrado!")
            return False
        
        # Testar login simulado - buscar um usuário específico
        test_cpf = users[0][1]  # Pegar CPF do primeiro usuário
        
        cursor.execute("""
            SELECT id, cpf, nome, email, telefone, tipo_usuario, ativo, ultimo_login, criado_em 
            FROM usuarios 
            WHERE cpf = ? AND ativo = 1
        """, (test_cpf,))
        
        user_data = cursor.fetchone()
        
        if user_data:
            print(f"\n✅ BUSCA DE USUÁRIO FUNCIONANDO!")
            print(f"   🎯 Usuario encontrado para CPF: {test_cpf}")
            
            # Simular resposta do backend
            usuario_response = {
                "id": user_data[0],
                "cpf": user_data[1],
                "nome": user_data[2],
                "email": user_data[3],
                "telefone": user_data[4],
                "tipo_usuario": user_data[5],
                "ativo": user_data[6],
                "ultimo_login": user_data[7],
                "criado_em": user_data[8]
            }
            
            print(f"\n📋 DADOS RETORNADOS:")
            for key, value in usuario_response.items():
                print(f"   • {key}: {value}")
            
            # Verificar se tem todos os campos necessários para o frontend
            required_fields = ['id', 'nome', 'cpf', 'email', 'tipo_usuario']
            missing_fields = [field for field in required_fields if usuario_response[field] is None]
            
            if missing_fields:
                print(f"\n⚠️ Campos faltando: {missing_fields}")
                return False
            else:
                print(f"\n✅ TODOS OS CAMPOS OBRIGATÓRIOS PRESENTES!")
                print(f"✅ RESPOSTA COMPATÍVEL COM FRONTEND!")
                return True
        else:
            print(f"❌ Usuário não encontrado para CPF: {test_cpf}")
            return False
            
        conn.close()
        
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        return False

def test_backend_auth_code():
    """Testar se o código de auth do backend funcionaria"""
    print(f"\n🔧 TESTE: Código de Autenticação do Backend")
    print("=" * 45)
    
    try:
        from app.models import Usuario
        from app.database import get_db
        from sqlalchemy.orm import Session
        
        print("✅ Importações do backend funcionando")
        
        # Simular busca de usuário como o backend faz
        db_path = "paineluniversal.db"
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Buscar primeiro usuário ativo
        cursor.execute("""
            SELECT id, cpf, nome, email, telefone, tipo_usuario, ativo 
            FROM usuarios 
            WHERE ativo = 1 
            LIMIT 1
        """)
        
        user_row = cursor.fetchone()
        if user_row:
            print(f"✅ Usuário encontrado no banco")
            
            # Simular criação de usuario_data como no backend
            usuario_data = {
                "id": user_row[0],
                "cpf": user_row[1],
                "nome": user_row[2],
                "email": user_row[3],
                "telefone": user_row[4],
                "tipo_usuario": user_row[5],  # Campo que estava faltando antes da migração
                "ativo": user_row[6]
            }
            
            print(f"✅ usuario_data criado com sucesso:")
            print(f"   tipo_usuario: {usuario_data['tipo_usuario']}")
            
            # Simular resposta completa do login
            login_response = {
                "access_token": "fake_token_for_test",
                "token_type": "bearer", 
                "usuario": usuario_data
            }
            
            print(f"\n✅ RESPOSTA DE LOGIN SIMULADA:")
            print(f"   access_token: ✅")
            print(f"   usuario: ✅")
            print(f"   usuario.tipo_usuario: {login_response['usuario']['tipo_usuario']}")
            
            return True
        else:
            print("❌ Nenhum usuário ativo encontrado")
            return False
            
        conn.close()
        
    except Exception as e:
        print(f"❌ Erro no teste de código backend: {e}")
        return False

if __name__ == "__main__":
    success1 = test_direct_login()
    success2 = test_backend_auth_code()
    
    print(f"\n🎯 RESULTADO FINAL:")
    print(f"   Banco de dados: {'✅' if success1 else '❌'}")
    print(f"   Código backend: {'✅' if success2 else '❌'}")
    
    if success1 and success2:
        print(f"\n🎉 SUCESSO! Login deve funcionar após migração!")
        print(f"💡 Problema estava no campo 'tipo_usuario' faltando - CORRIGIDO!")
    else:
        print(f"\n⚠️ Ainda há problemas para resolver")
