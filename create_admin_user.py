#!/usr/bin/env python3
"""
Script para criar usuário admin no banco de dados
"""

import sqlite3
import hashlib
from datetime import datetime

def hash_password(password: str) -> str:
    """Gera hash da senha usando o mesmo método do backend"""
    return hashlib.sha256(password.encode()).hexdigest()

def create_admin_user():
    """Cria usuário admin no banco"""
    
    # Dados do usuário admin
    cpf = "06601206154"
    nome = "Administrador"
    senha = "101112"
    email = "admin@sistema.com"
    telefone = "(11) 99999-9999"
    tipo_usuario = "admin"
    
    # Hash da senha
    senha_hash = hash_password(senha)
    
    try:
        conn = sqlite3.connect('eventos.db')
        cursor = conn.cursor()
        
        # Verificar se usuário já existe
        cursor.execute("SELECT cpf FROM usuarios WHERE cpf = ?", (cpf,))
        exists = cursor.fetchone()
        
        if exists:
            print(f"⚠️ Usuário {cpf} já existe!")
            return
        
        # Verificar estrutura da tabela
        cursor.execute("PRAGMA table_info(usuarios)")
        columns = cursor.fetchall()
        print("📋 Estrutura da tabela usuarios:")
        for col in columns:
            print(f"  {col[1]} ({col[2]})")
        
        # Inserir usuário
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
        
        print(f"✅ Usuário admin criado com sucesso!")
        print(f"📋 CPF: {cpf}")
        print(f"📋 Senha: {senha}")
        print(f"📋 Hash: {senha_hash[:30]}...")
        print(f"📋 Tipo: {tipo_usuario}")
        
        # Verificar se foi inserido
        cursor.execute("SELECT cpf, nome, tipo_usuario FROM usuarios WHERE cpf = ?", (cpf,))
        user = cursor.fetchone()
        if user:
            print(f"✅ Verificação: Usuário encontrado no banco: {user}")
        else:
            print("❌ Erro: Usuário não foi encontrado após inserção!")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Erro ao criar usuário: {e}")

if __name__ == "__main__":
    create_admin_user()
