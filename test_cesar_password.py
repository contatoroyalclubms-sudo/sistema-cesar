#!/usr/bin/env python3
"""
Verificar senha do usuário César no banco SQLite
"""

import sqlite3
import sys
import os
sys.path.append('./backend')

from backend.app.auth import verificar_senha

def test_cesar_password():
    """Verificar senha do César no banco"""
    
    # Conectar ao banco
    conn = sqlite3.connect('paineluniversal.db')
    cursor = conn.cursor()

    # Buscar usuário César
    cursor.execute('SELECT cpf, nome, senha_hash, tipo, tipo_usuario FROM usuarios WHERE cpf = ?', ('06601206156',))
    result = cursor.fetchone()

    if result:
        cpf, nome, senha_hash, tipo, tipo_usuario = result
        print(f'👤 Usuário encontrado:')
        print(f'   CPF: {cpf}')
        print(f'   Nome: {nome}')
        print(f'   Tipo: {tipo}')
        print(f'   Tipo_usuario: {tipo_usuario}')
        print(f'   Hash senha: {senha_hash[:20]}...')
        
        # Testar senha
        print('\n🔐 Testando senhas:')
        senhas_teste = ['101112', '123456', 'admin123']
        
        for senha in senhas_teste:
            resultado = verificar_senha(senha, senha_hash)
            status = '✅' if resultado else '❌'
            print(f'   {status} Senha "{senha}": {resultado}')
            
    else:
        print('❌ Usuário César não encontrado')

    conn.close()

if __name__ == "__main__":
    test_cesar_password()
