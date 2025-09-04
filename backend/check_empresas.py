#!/usr/bin/env python3

"""Script para verificar empresas no banco de dados"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app.models import Empresa

def main():
    db = SessionLocal()
    try:
        empresas = db.query(Empresa).all()
        print(f'📊 Total de empresas no banco: {len(empresas)}')
        
        for empresa in empresas:
            print(f'🏢 Empresa ID {empresa.id}: {empresa.nome}')
            print(f'   CNPJ: {empresa.cnpj}')
            print(f'   Ativa: {empresa.ativa}')
            print(f'   Email: {empresa.email}')
            print('---')
            
        if len(empresas) == 0:
            print('❌ Nenhuma empresa encontrada no banco!')
            print('🔧 Criando empresa padrão...')
            
            empresa_padrao = Empresa(
                nome="Empresa Padrão",
                cnpj="00000000000100",
                email="contato@paineluniversal.com",
                telefone="(11) 99999-9999",
                ativa=True
            )
            db.add(empresa_padrao)
            db.commit()
            db.refresh(empresa_padrao)
            print(f'✅ Empresa padrão criada com ID {empresa_padrao.id}')
        
    except Exception as e:
        print(f'💥 Erro ao verificar empresas: {e}')
    finally:
        db.close()

if __name__ == "__main__":
    main()
