#!/usr/bin/env python3
"""
Fix para problema de schema EventoCreate
"""

import sys
import os

# Adicionar o diretório do projeto ao path
project_root = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, project_root)

def fix_evento_schema():
    """Testa se o EventoCreate tem o atributo local"""
    
    try:
        from backend.app.schemas import EventoCreate
        from backend.app.models import StatusEvento
        from datetime import datetime
        
        print("🔍 Testando EventoCreate schema...")
        
        # Criar objeto de teste
        test_data = {
            "nome": "Teste",
            "local": "Local Teste",
            "data_evento": datetime.now(),
            "descricao": "Teste descrição",
            "endereco": "Endereço teste",
            "limite_idade": 18,
            "capacidade_maxima": 100
        }
        
        evento_create = EventoCreate(**test_data)
        
        print(f"✅ EventoCreate criado com sucesso!")
        print(f"📋 Campos do objeto:")
        for field, value in evento_create.dict().items():
            print(f"  {field}: {value}")
            
        print(f"🔍 Verificando se tem atributo 'local': {hasattr(evento_create, 'local')}")
        
        if hasattr(evento_create, 'local'):
            print(f"✅ Campo 'local' encontrado: {evento_create.local}")
        else:
            print(f"❌ Campo 'local' NÃO encontrado!")
            
        return True
        
    except Exception as e:
        print(f"❌ Erro ao testar EventoCreate: {e}")
        print(f"Tipo do erro: {type(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    fix_evento_schema()
