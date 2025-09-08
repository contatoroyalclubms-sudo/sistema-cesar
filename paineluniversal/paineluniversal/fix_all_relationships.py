#!/usr/bin/env python3
"""
Script para corrigir TODOS os relacionamentos problemáticos de uma vez
"""

def fix_all_relationships():
    models_file = "backend/app/models.py"
    
    with open(models_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Comentar TODOS os relacionamentos que podem estar causando problemas
    relationship_patterns = [
        'relationship("Ticket", back_populates="',
        'relationship("TipoTicket", back_populates="',
        'relationship("LoteTicket", back_populates="',
        ', back_populates="lote"',
        ', back_populates="tickets"',
        ', back_populates="lotes"',
    ]
    
    for pattern in relationship_patterns:
        lines = content.split('\n')
        new_lines = []
        
        for line in lines:
            if pattern in line and not line.strip().startswith('#'):
                # Se a linha contém o padrão e não está comentada, comentar
                indentation = len(line) - len(line.lstrip())
                new_lines.append(' ' * indentation + '# ' + line.strip() + '  # COMENTADO - CONFLITO RELACIONAMENTO')
            else:
                new_lines.append(line)
        
        content = '\n'.join(new_lines)
    
    # Também vamos comentar qualquer linha que contenha "back_populates" com "ticket" ou "lote"
    lines = content.split('\n')
    new_lines = []
    
    for line in lines:
        if ('back_populates' in line and ('ticket' in line.lower() or 'lote' in line.lower()) 
            and not line.strip().startswith('#')):
            indentation = len(line) - len(line.lstrip())
            new_lines.append(' ' * indentation + '# ' + line.strip() + '  # COMENTADO - CONFLITO BACK_POPULATES')
        else:
            new_lines.append(line)
    
    content = '\n'.join(new_lines)
    
    with open(models_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ TODOS os relacionamentos problemáticos foram comentados")
    print("📝 Backend deve iniciar sem conflitos de relacionamento")

if __name__ == "__main__":
    fix_all_relationships()
