#!/usr/bin/env python3
"""
Corrigir temporariamente todos os relacionamentos SQLAlchemy problemáticos
"""

import re

def corrigir_models():
    """Comentar todos os relacionamentos problemáticos temporariamente"""
    
    file_path = "backend/app/models.py"
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Padrões de relacionamentos problemáticos
    patterns_to_comment = [
        r'(\s+)tickets = relationship\("Ticket".*?\)',
        r'(\s+)lote = relationship\("TipoTicket".*?\)',
        r'(\s+)tipo_ticket = relationship\("TipoTicket".*?\)',
        r'(\s+)evento_ticket = relationship\("EventoTicket".*?\)',
        r'(\s+)vendas = relationship\("VendaTicket".*?\)',
    ]
    
    for pattern in patterns_to_comment:
        content = re.sub(pattern, r'\1# \g<0>  # TEMPORARIAMENTE COMENTADO', content)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Relacionamentos problemáticos comentados temporariamente")

if __name__ == "__main__":
    print("🔧 Corrigindo relacionamentos SQLAlchemy...")
    corrigir_models()
    print("✅ Correção concluída!")
