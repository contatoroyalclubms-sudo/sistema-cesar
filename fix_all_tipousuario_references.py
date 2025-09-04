#!/usr/bin/env python3
"""
Script para corrigir todas as referências TipoUsuario no projeto
Remove imports e substitui por strings
"""

import os
import re
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fix_file_tipousuario_references(file_path):
    """Corrige um arquivo específico removendo referências ao TipoUsuario"""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        original_content = content
        
        # 1. Remover imports do TipoUsuario
        content = re.sub(r',\s*TipoUsuario', '', content)
        content = re.sub(r'TipoUsuario,\s*', '', content)
        content = re.sub(r'from\s+\S+\s+import\s+TipoUsuario\s*\n', '', content)
        content = re.sub(r'import\s+TipoUsuario\s*\n', '', content)
        
        # 2. Substituir referências TipoUsuario.VALOR por strings
        content = re.sub(r'TipoUsuario\.ADMIN', '"admin"', content)
        content = re.sub(r'TipoUsuario\.PROMOTER', '"promoter"', content)
        content = re.sub(r'TipoUsuario\.CLIENTE', '"cliente"', content)
        
        # 3. Substituir campo tipo= por tipo_usuario=
        content = re.sub(r'\btipo\s*=\s*', 'tipo_usuario=', content)
        
        # 4. Substituir Usuario.tipo por Usuario.tipo_usuario em queries
        content = re.sub(r'Usuario\.tipo\s*==', 'Usuario.tipo_usuario ==', content)
        content = re.sub(r'Usuario\.tipo\s*!=', 'Usuario.tipo_usuario !=', content)
        
        # 5. Corrigir type hints se houver
        content = re.sub(r':\s*TipoUsuario', ': str', content)
        
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(content)
            logger.info(f"✅ Corrigido: {file_path}")
            return True
        else:
            logger.info(f"ℹ️ Sem alterações necessárias: {file_path}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Erro ao processar {file_path}: {e}")
        return False

def find_and_fix_all_files():
    """Encontra e corrige todos os arquivos Python no projeto"""
    backend_dir = "backend"
    if not os.path.exists(backend_dir):
        backend_dir = "."
    
    fixed_files = []
    
    for root, dirs, files in os.walk(backend_dir):
        # Ignorar diretórios de cache e ambiente virtual
        dirs[:] = [d for d in dirs if d not in ['.venv', '__pycache__', '.pytest_cache', 'venv']]
        
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                if fix_file_tipousuario_references(file_path):
                    fixed_files.append(file_path)
    
    return fixed_files

def main():
    """Função principal"""
    logger.info("🔧 Iniciando correção em lote de referências TipoUsuario")
    
    fixed_files = find_and_fix_all_files()
    
    if fixed_files:
        logger.info(f"🎉 Correção concluída! {len(fixed_files)} arquivos corrigidos:")
        for file_path in fixed_files:
            logger.info(f"  - {file_path}")
    else:
        logger.info("ℹ️ Nenhum arquivo precisou de correção")
    
    logger.info("✅ Processo concluído")

if __name__ == "__main__":
    main()
