#!/usr/bin/env python3
"""
Script para criar usuário admin com hash correto (bcrypt)
"""

import sqlite3
from passlib.context import CryptContext
from datetime import datetime

# Usar o mesmo contexto de criptografia do backend
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_admin_user_correct():
    """Cria usuário admin com hash bcrypt correto"""
    
    # Dados do usuário admin
    cpf = "06601206154"
    nome = "Administrador"
    senha = "101112"
    email = "admin@sistema.com"
    telefone = "(11) 99999-9999"
    tipo_usuario = "admin"
    
    # Hash da senha usando bcrypt (igual ao backend)
    senha_hash = pwd_context.hash(senha)
    
    try:
        conn = sqlite3.connect('eventos.db')
        cursor = conn.cursor()
        
        # Deletar usuário existente se houver
        cursor.execute("DELETE FROM usuarios WHERE cpf = ?", (cpf,))
        print(f"🗑️ Usuário existente removido (se havia)")
        
        # Inserir usuário com hash correto
        query = """
        INSERT INTO usuarios (
            cpf, nome, senha_hash, email, telefone, tipo_usuario, 
            ativo, criado_em, atualizado_em
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        now = datetime.now().isoformat()
        
        cursor.execute(query, (
            cpf, nome, senha_hash, email, telefone, tipo_usuario,
            True, now, now
        ))
        
        conn.commit()
        
        print(f"✅ Usuário admin criado com hash bcrypt correto!")
        print(f"📋 CPF: {cpf}")
        print(f"📋 Senha: {senha}")
        print(f"📋 Hash bcrypt: {senha_hash[:30]}...")
        print(f"📋 Tipo: {tipo_usuario}")
        
        # Verificar se foi inserido
        cursor.execute("SELECT cpf, nome, tipo_usuario FROM usuarios WHERE cpf = ?", (cpf,))
        user = cursor.fetchone()
        if user:
            print(f"✅ Verificação: Usuário encontrado no banco: {user}")
        else:
            print("❌ Erro: Usuário não foi encontrado após inserção!")
        
        # Testar se o hash funciona
        test_verify = pwd_context.verify(senha, senha_hash)
        print(f"🔐 Teste de verificação de senha: {test_verify}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Erro ao criar usuário: {e}")

if __name__ == "__main__":
    create_admin_user_correct()
