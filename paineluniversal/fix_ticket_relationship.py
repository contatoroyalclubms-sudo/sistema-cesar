#!/usr/bin/env python3
"""
Script para corrigir relacionamento específico entre TipoTicket e Ticket
"""

def fix_ticket_relationships():
    models_file = "backend/app/models.py"
    
    with open(models_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Comentar linha problemática do relacionamento lote em Ticket
    content = content.replace(
        'lote = relationship("LoteTicket", back_populates="tickets")',
        '# lote = relationship("LoteTicket", back_populates="tickets")  # COMENTADO - CONFLITO'
    )
    
    # Comentar relacionamento tickets em TipoTicket temporariamente
    content = content.replace(
        'tickets = relationship("Ticket", back_populates="tipo_ticket")  # TEMPORARIAMENTE COMENTADO',
        '# tickets = relationship("Ticket", back_populates="tipo_ticket")  # COMENTADO - CONFLITO'
    )
    
    # Comentar relacionamento tipo_ticket em Ticket temporariamente
    content = content.replace(
        'tipo_ticket = relationship("TipoTicket", back_populates="tickets")  # TEMPORARIAMENTE COMENTADO',
        '# tipo_ticket = relationship("TipoTicket", back_populates="tickets")  # COMENTADO - CONFLITO'
    )
    
    with open(models_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Relacionamentos TipoTicket/Ticket corrigidos")
    print("📝 Relacionamentos bidirecionais temporariamente desabilitados")

if __name__ == "__main__":
    fix_ticket_relationships()
