#!/usr/bin/env python3
"""
🔧 CORREÇÃO CRÍTICA: Senhas com Hash Inválido
Corrigir senhas que estão em formato incorreto no banco
"""

import sqlite3
import os
import bcrypt
import hashlib
from datetime import datetime

def check_and_fix_password_hashes(db_path):
    """Verificar e corrigir hashes de senha inválidos"""
    print(f"\n🔧 Verificando hashes de senha em {db_path}...")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Buscar todos os usuários
        cursor.execute("SELECT id, nome, cpf, senha_hash FROM usuarios;")
        users = cursor.fetchall()
        
        print(f"   📊 Verificando {len(users)} usuários:")
        
        for user in users:
            user_id, nome, cpf, senha_hash = user
            print(f"      ID {user_id}: {nome} ({cpf})")
            print(f"         Hash atual: {senha_hash[:20]}...")
            
            # Verificar se o hash é válido
            is_valid_hash = False
            hash_type = "desconhecido"
            
            if senha_hash.startswith('$2b$') or senha_hash.startswith('$2a$'):
                hash_type = "bcrypt"
                is_valid_hash = True
            elif senha_hash.startswith('pbkdf2'):
                hash_type = "pbkdf2"
                is_valid_hash = True
            elif len(senha_hash) == 32 and all(c in '0123456789abcdef' for c in senha_hash.lower()):
                hash_type = "md5"
                is_valid_hash = False  # MD5 não é seguro
            elif len(senha_hash) == 64 and all(c in '0123456789abcdef' for c in senha_hash.lower()):
                hash_type = "sha256"
                is_valid_hash = False  # SHA256 sem salt não é seguro
            elif len(senha_hash) < 20:
                hash_type = "texto_plano"
                is_valid_hash = False
            
            print(f"         Tipo: {hash_type}")
            print(f"         Válido: {'✅' if is_valid_hash else '❌'}")
            
            # Se hash inválido, gerar novo hash para senha padrão
            if not is_valid_hash:
                print(f"         🔄 Gerando novo hash bcrypt...")
                
                # Usar senha padrão baseada no tipo ou CPF
                if cpf == "12345678901":  # Admin
                    nova_senha = "admin123"
                elif cpf == "11111111111":  # Promoter
                    nova_senha = "promoter123"
                elif cpf == "22222222222":  # Cliente
                    nova_senha = "cliente123"
                else:
                    nova_senha = "123456"  # Senha padrão para outros
                
                # Gerar hash bcrypt
                salt = bcrypt.gensalt()
                novo_hash = bcrypt.hashpw(nova_senha.encode('utf-8'), salt).decode('utf-8')
                
                # Atualizar no banco
                cursor.execute("UPDATE usuarios SET senha_hash = ? WHERE id = ?", (novo_hash, user_id))
                
                print(f"         ✅ Hash atualizado (senha: {nova_senha})")
                print(f"         Novo hash: {novo_hash[:20]}...")
            else:
                print(f"         ✅ Hash já é válido")
            
            print()
        
        conn.commit()
        conn.close()
        
        print(f"   ✅ Verificação concluída para {db_path}")
        return True
        
    except Exception as e:
        print(f"   ❌ Erro na verificação de {db_path}: {e}")
        return False

def create_test_users_with_correct_hashes(db_path):
    """Criar usuários de teste com hashes corretos"""
    print(f"\n🔧 Criando usuários de teste em {db_path}...")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Usuários de teste com senhas corretas
        test_users = [
            {
                "cpf": "12345678901",
                "nome": "Admin Teste",
                "email": "admin@teste.com",
                "telefone": "11999999999",
                "senha": "admin123",
                "tipo_usuario": "admin"
            },
            {
                "cpf": "11111111111", 
                "nome": "Promoter Teste",
                "email": "promoter@teste.com",
                "telefone": "11888888888",
                "senha": "promoter123",
                "tipo_usuario": "promoter"
            },
            {
                "cpf": "22222222222",
                "nome": "Cliente Teste", 
                "email": "cliente@teste.com",
                "telefone": "11777777777",
                "senha": "cliente123",
                "tipo_usuario": "cliente"
            }
        ]
        
        for user_data in test_users:
            # Verificar se usuário já existe
            cursor.execute("SELECT id FROM usuarios WHERE cpf = ?", (user_data["cpf"],))
            existing = cursor.fetchone()
            
            if existing:
                print(f"   📝 Atualizando usuário existente: {user_data['nome']}")
                # Gerar hash bcrypt
                salt = bcrypt.gensalt()
                senha_hash = bcrypt.hashpw(user_data["senha"].encode('utf-8'), salt).decode('utf-8')
                
                cursor.execute("""
                    UPDATE usuarios 
                    SET senha_hash = ?, nome = ?, email = ?, telefone = ?, tipo_usuario = ?
                    WHERE cpf = ?
                """, (senha_hash, user_data["nome"], user_data["email"], 
                     user_data["telefone"], user_data["tipo_usuario"], user_data["cpf"]))
            else:
                print(f"   ➕ Criando novo usuário: {user_data['nome']}")
                # Gerar hash bcrypt
                salt = bcrypt.gensalt()
                senha_hash = bcrypt.hashpw(user_data["senha"].encode('utf-8'), salt).decode('utf-8')
                
                cursor.execute("""
                    INSERT INTO usuarios (cpf, nome, email, telefone, senha_hash, tipo_usuario, ativo)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (user_data["cpf"], user_data["nome"], user_data["email"],
                     user_data["telefone"], senha_hash, user_data["tipo_usuario"], True))
            
            print(f"      ✅ {user_data['nome']} - CPF: {user_data['cpf']} - Senha: {user_data['senha']}")
        
        conn.commit()
        conn.close()
        
        print(f"   ✅ Usuários de teste criados/atualizados")
        return True
        
    except Exception as e:
        print(f"   ❌ Erro ao criar usuários de teste: {e}")
        return False

def main():
    """Executar correção completa das senhas"""
    print("🚀 CORREÇÃO CRÍTICA: Hashes de Senha")
    print("=" * 50)
    
    databases = [
        "paineluniversal.db",
        "backend/eventos.db"
    ]
    
    for db_path in databases:
        if os.path.exists(db_path):
            # Backup
            backup_path = f"{db_path}.backup_passwords_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            import shutil
            shutil.copy2(db_path, backup_path)
            print(f"✅ Backup criado: {backup_path}")
            
            # Corrigir hashes
            check_and_fix_password_hashes(db_path)
            
            # Criar/atualizar usuários de teste
            create_test_users_with_correct_hashes(db_path)
        else:
            print(f"❌ Banco não encontrado: {db_path}")
    
    print(f"\n🎯 CREDENCIAIS PARA TESTE:")
    print("   Admin: CPF 12345678901, Senha: admin123")
    print("   Promoter: CPF 11111111111, Senha: promoter123") 
    print("   Cliente: CPF 22222222222, Senha: cliente123")
    
    print(f"\n🧪 TESTE IMEDIATO:")
    print("Execute: python test_login_after_migration.py")

if __name__ == "__main__":
    main()
