#!/usr/bin/env python3
"""
Script para verificar dados do usuário César
"""

from backend.app.database import get_db
from backend.app.models import Usuario

def check_cesar():
    db = next(get_db())
    
    cesar = db.query(Usuario).filter(Usuario.nome == 'César').first()
    if cesar:
        print(f'ID: {cesar.id}')
        print(f'Nome: {cesar.nome}')
        print(f'CPF: {cesar.cpf}')
        print(f'tipo: "{cesar.tipo}"')
        print(f'tipo_usuario: "{cesar.tipo_usuario}"')
        print(f'ativo: {cesar.ativo}')
        
        # Testar nossa função helper
        from backend.app.auth import get_user_tipo
        tipo_detectado = get_user_tipo(cesar)
        print(f'get_user_tipo(): "{tipo_detectado}"')
        print(f'Tipo normalizado: "{tipo_detectado}" == "admin"? {tipo_detectado == "admin"}')
        
        # Testar se verificação admin funcionaria
        try:
            from backend.app.auth import verificar_permissao_admin
            print('Testando verificar_permissao_admin...')
            # Não podemos chamar diretamente pois usa Depends, mas podemos simular
            if tipo_detectado == "admin":
                print('✅ verificar_permissao_admin: SUCESSO')
            else:
                print('❌ verificar_permissao_admin: FALHA')
        except Exception as e:
            print(f'❌ Erro ao testar verificar_permissao_admin: {e}')
        
    else:
        print('❌ César não encontrado')
    
    db.close()

if __name__ == "__main__":
    check_cesar()
