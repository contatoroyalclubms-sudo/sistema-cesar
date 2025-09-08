#!/usr/bin/env python3
"""
Script para remover todas as referências a usuario.empresa_id no backend
"""
import re
import os

def update_file(file_path, old_pattern, new_text):
    """Substitui padrão em arquivo"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Substituir padrões
        new_content = re.sub(old_pattern, new_text, content, flags=re.MULTILINE | re.DOTALL)
        
        if new_content != content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"✅ {file_path} atualizado")
            return True
        else:
            print(f"ℹ️  {file_path} não precisou ser alterado")
            return False
    except Exception as e:
        print(f"❌ Erro ao atualizar {file_path}: {e}")
        return False

def remove_empresa_id_references():
    """Remove todas as referências a usuario.empresa_id"""
    
    # Mapear arquivos e suas substituições necessárias
    updates = [
        {
            'file': 'app/routers/listas.py',
            'pattern': r'if \(usuario_atual\.tipo\.value != "admin" and\s+usuario_atual\.empresa_id != evento\.empresa_id\):\s+raise HTTPException\(status_code=403, detail="Acesso negado"\)',
            'replacement': 'if usuario_atual.tipo.value not in ["admin", "promoter"]:\n        raise HTTPException(status_code=403, detail="Acesso negado")'
        },
        {
            'file': 'app/routers/pdv.py',
            'pattern': r'empresa_id=usuario_atual\.empresa_id,',
            'replacement': '# empresa_id removido'
        },
        {
            'file': 'app/routers/pdv.py',
            'pattern': r'usuario_atual\.empresa_id != comanda\.empresa_id',
            'replacement': 'False  # empresa_id removido'
        },
        {
            'file': 'app/routers/dashboard.py',
            'pattern': r'usuario_atual\.empresa_id != evento\.empresa_id',
            'replacement': 'False  # empresa_id removido'
        },
        {
            'file': 'app/routers/relatorios.py',
            'pattern': r'usuario_atual\.empresa_id != evento\.empresa_id',
            'replacement': 'False  # empresa_id removido'
        },
        {
            'file': 'app/services/alert_service.py',
            'pattern': r'Usuario\.empresa_id == evento\.empresa_id,',
            'replacement': '# Usuario.empresa_id removido'
        }
    ]
    
    updated_files = 0
    
    for update in updates:
        file_path = update['file']
        if os.path.exists(file_path):
            if update_file(file_path, update['pattern'], update['replacement']):
                updated_files += 1
        else:
            print(f"⚠️  Arquivo não encontrado: {file_path}")
    
    print(f"\n🎉 {updated_files} arquivos atualizados")
    return updated_files > 0

if __name__ == "__main__":
    print("🚀 Removendo referências a usuario.empresa_id...")
    success = remove_empresa_id_references()
    
    if success:
        print("\n✅ Remoção concluída!")
    else:
        print("\n ℹ️  Nenhuma alteração necessária.")
