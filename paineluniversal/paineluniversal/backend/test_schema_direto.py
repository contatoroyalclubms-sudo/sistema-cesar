#!/usr/bin/env python3
"""
Script para testar schema Usuario isoladamente
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from pydantic import BaseModel
from typing import Optional
from datetime import datetime
print('🔍 Testando criação direta do schema...')

# Definir schema simples para teste
class UsuarioTest(BaseModel):
    id: int
    cpf: str
    nome: str
    email: str
    telefone: Optional[str] = None
    tipo: str
    ativo: bool
    ultimo_login: Optional[datetime] = None
    criado_em: datetime
    
    class Config:
        from_attributes = True

# Dados de teste
dados_teste = {
    'id': 4,
    'cpf': '06601206156',
    'nome': 'César',
    'email': 'rosemberg@gmail.com',
    'telefone': None,
    'tipo': "admin",
    'ativo': True,
    'ultimo_login': None,
    'criado_em': datetime.now()
}

try:
    usuario_teste = UsuarioTest(**dados_teste)
    print('✅ Schema criado com sucesso!')
    
    dados_serializados = usuario_teste.model_dump()
    print('📄 Dados serializados:')
    for key, value in dados_serializados.items():
        print(f'   {key}: {value}')
        
    tipo_valor = dados_serializados.get('tipo')
    if tipo_valor:
        print(f'\n🎉 TIPO FUNCIONA: {tipo_valor}')
    
except Exception as e:
    print(f'❌ Erro: {e}')
    import traceback
    traceback.print_exc()
