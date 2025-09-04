#!/usr/bin/env python3
"""
Script para criar o usuário César no banco SQLite local como admin
"""

import sys
import os
sys.path.append('.')
sys.path.append('./backend')

from backend.app.database import get_db
from backend.app.models import Usuario
from backend.app.auth import gerar_hash_senha

def create_cesar_local():
    """Cria o usuário César no banco SQLite local como admin"""
    
    print('🔧 Criando usuário César no banco local SQLite...')
    
    db = next(get_db())
    try:
        # Verificar se já existe
        existing_user = db.query(Usuario).filter(Usuario.cpf == '06601206156').first()
        if existing_user:
            print(f'✅ Usuário já existe: {existing_user.nome} (Tipo: {existing_user.tipo})')
            
            # Atualizar para admin se não for
            if existing_user.tipo != 'admin':
                existing_user.tipo = 'admin'
                db.commit()
                print(f'✅ Tipo atualizado para: {existing_user.tipo}')
            else:
                print('✅ Usuário já é admin')
            return
        
        # Criar hash da senha
        print('🔐 Gerando hash da senha...')
        senha_hash = gerar_hash_senha('101112')
        
        # Criar novo usuário
        print('👤 Criando usuário no banco...')
        novo_usuario = Usuario(
            cpf='06601206156',
            nome='César',
            email='rosemberg@gmail.com',
            telefone=None,
            senha_hash=senha_hash,
            tipo='admin',  # Campo único para tipo de usuário
            ativo=True
        )
        
        db.add(novo_usuario)
        db.commit()
        db.refresh(novo_usuario)
        
        print(f'✅ Usuário César criado com sucesso!')
        print(f'   ID: {novo_usuario.id}')
        print(f'   Nome: {novo_usuario.nome}')
        print(f'   CPF: {novo_usuario.cpf}')
        print(f'   Tipo: {novo_usuario.tipo}')
        print(f'   Email: {novo_usuario.email}')
        print(f'   Ativo: {novo_usuario.ativo}')
        
    except Exception as e:
        print(f'❌ Erro ao criar usuário: {e}')
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    create_cesar_local()
