#!/usr/bin/env python3
"""
Script para limpar caracteres null do arquivo schemas.py
"""

def clean_schemas():
    # Ler o arquivo com problemas
    with open('schemas.py', 'rb') as f:
        content = f.read()
    
    print(f"Original size: {len(content)} bytes")
    null_bytes = content.count(b'\x00')
    print(f"Null bytes found: {null_bytes} occurrences")
    
    # Remover caracteres null
    clean_content = content.replace(b'\x00', b'')
    
    print(f"Clean size: {len(clean_content)} bytes")
    
    # Fazer backup do arquivo original
    with open('schemas_backup.py', 'wb') as f:
        f.write(content)
    
    # Sobrescrever o arquivo original com versão limpa
    with open('schemas.py', 'wb') as f:
        f.write(clean_content)
    
    print("✅ Arquivo schemas.py limpo com sucesso!")
    print("💾 Backup salvo como schemas_backup.py")

if __name__ == "__main__":
    clean_schemas()
