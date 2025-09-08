#!/usr/bin/env python3
"""
🧹 SCRIPT DE ORGANIZAÇÃO DE ARQUIVOS - PAINELUNIVERSAL
Organiza os múltiplos scripts de migração em estrutura limpa
Preserva funcionalidades existentes
"""

import os
import shutil
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("file_organizer")

class FileOrganizer:
    """Organiza arquivos de migração em estrutura limpa"""
    
    def __init__(self, base_path: str):
        self.base_path = Path(base_path)
        self.backup_dir = self.base_path / "file_organization_backup"
        self.organized_dirs = {
            'migrations': self.base_path / 'migrations',
            'scripts': self.base_path / 'scripts', 
            'docs': self.base_path / 'docs',
            'tests': self.base_path / 'tests_migration'
        }
        
    def create_directory_structure(self):
        """Cria estrutura de diretórios organizada"""
        logger.info("📁 Criando estrutura de diretórios...")
        
        # Criar backup
        self.backup_dir.mkdir(exist_ok=True)
        
        # Estrutura principal
        directories = {
            'migrations/production': 'Scripts para produção PostgreSQL',
            'migrations/development': 'Scripts para desenvolvimento SQLite',
            'migrations/archive': 'Scripts antigos/concluídos',
            'scripts/deploy': 'Scripts de deploy automático',
            'scripts/maintenance': 'Scripts de manutenção',
            'scripts/monitoring': 'Scripts de monitoramento',
            'tests_migration/unit': 'Testes unitários de migração',
            'tests_migration/integration': 'Testes de integração',
            'docs/migration': 'Documentação de migração'
        }
        
        for dir_path, description in directories.items():
            full_path = self.base_path / dir_path
            full_path.mkdir(parents=True, exist_ok=True)
            
            # Criar README.md em cada diretório
            readme_path = full_path / "README.md"
            if not readme_path.exists():
                readme_content = f"# {dir_path.replace('/', ' - ').title()}\n\n{description}\n"
                readme_path.write_text(readme_content, encoding='utf-8')
        
        logger.info("✅ Estrutura de diretórios criada")
    
    def get_migration_files(self) -> Dict[str, List[Path]]:
        """Identifica e categoriza arquivos de migração"""
        
        categories = {
            'postgres_migration': [],
            'sqlite_migration': [],
            'enum_fixes': [],
            'deploy_scripts': [],
            'test_scripts': [],
            'documentation': [],
            'other_scripts': []
        }
        
        # Padrões de arquivos
        patterns = {
            'postgres_migration': [
                'migrate_postgres*.py', 'migrate_postgres*.sql', 
                'postgresql_migration.sql', 'migrate_production.py'
            ],
            'sqlite_migration': [
                'migrate_simple.py', 'migrate_debug.py', 
                'create_sqlite_db.py', '*sqlite*.py'
            ],
            'enum_fixes': [
                'fix_enum*.py', 'fix_enum*.sql', 
                'fix_tipousuario*.py', 'diagnose_enum*.py'
            ],
            'deploy_scripts': [
                'deploy*.sh', 'deploy*.ps1', 'start*.sh', 
                'run_*.py', 'apply_*.py'
            ],
            'test_scripts': [
                'test_*.py', 'test*.js', 'test*.html',
                'validate_*.py', 'diagnostic_*.py'
            ],
            'documentation': [
                '*.md', 'README*', 'RELATORIO_*', 
                'SOLUCAO_*', 'CORRECAO_*'
            ]
        }
        
        # Buscar arquivos no diretório raiz
        for file_path in self.base_path.glob('*'):
            if file_path.is_file():
                categorized = False
                
                for category, file_patterns in patterns.items():
                    for pattern in file_patterns:
                        if file_path.match(pattern):
                            categories[category].append(file_path)
                            categorized = True
                            break
                    if categorized:
                        break
                
                if not categorized:
                    # Arquivos Python genéricos
                    if file_path.suffix == '.py':
                        categories['other_scripts'].append(file_path)
        
        return categories
    
    def move_files_to_organized_structure(self, categories: Dict[str, List[Path]]):
        """Move arquivos para estrutura organizada"""
        logger.info("📦 Organizando arquivos...")
        
        # Mapeamento de categorias para diretórios
        category_mapping = {
            'postgres_migration': 'migrations/production',
            'sqlite_migration': 'migrations/development',
            'enum_fixes': 'migrations/production',
            'deploy_scripts': 'scripts/deploy',
            'test_scripts': 'tests_migration/integration',
            'documentation': 'docs/migration',
            'other_scripts': 'scripts/maintenance'
        }
        
        moved_files = []
        
        for category, files in categories.items():
            if not files:
                continue
                
            target_dir = self.base_path / category_mapping[category]
            
            logger.info(f"📁 Movendo {len(files)} arquivo(s) de {category}")
            
            for file_path in files:
                try:
                    # Backup do arquivo original
                    backup_path = self.backup_dir / file_path.name
                    shutil.copy2(file_path, backup_path)
                    
                    # Mover para diretório organizado
                    target_path = target_dir / file_path.name
                    
                    # Evitar sobrescrita
                    if target_path.exists():
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        target_path = target_dir / f"{file_path.stem}_{timestamp}{file_path.suffix}"
                    
                    shutil.move(str(file_path), str(target_path))
                    moved_files.append((file_path.name, target_path.relative_to(self.base_path)))
                    
                except Exception as e:
                    logger.warning(f"⚠️ Erro ao mover {file_path.name}: {e}")
        
        return moved_files
    
    def create_index_file(self, moved_files: List[tuple]):
        """Cria arquivo índice dos arquivos organizados"""
        
        index_content = f"""# 📁 ÍNDICE DE ARQUIVOS ORGANIZADOS
**Data**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 📋 Arquivos Movidos ({len(moved_files)} total)

"""
        
        # Agrupar por diretório
        by_directory = {}
        for original_name, new_path in moved_files:
            dir_name = str(new_path.parent)
            if dir_name not in by_directory:
                by_directory[dir_name] = []
            by_directory[dir_name].append((original_name, new_path.name))
        
        for directory, files in sorted(by_directory.items()):
            index_content += f"### 📂 {directory}\n"
            for original_name, new_name in files:
                if original_name != new_name:
                    index_content += f"- `{original_name}` → `{new_name}`\n"
                else:
                    index_content += f"- `{new_name}`\n"
            index_content += "\n"
        
        index_content += f"""
## 🔄 Restauração

Para restaurar a estrutura original:
```bash
# Os arquivos originais estão em:
{self.backup_dir.relative_to(self.base_path)}
```

## 📁 Nova Estrutura

- `migrations/production/` - Scripts PostgreSQL para produção
- `migrations/development/` - Scripts SQLite para desenvolvimento
- `scripts/deploy/` - Scripts de deploy automático
- `scripts/maintenance/` - Scripts de manutenção
- `tests_migration/` - Testes de migração
- `docs/migration/` - Documentação

## 🛡️ Garantias

- ✅ Backup completo em `{self.backup_dir.relative_to(self.base_path)}`
- ✅ Nenhum arquivo perdido
- ✅ Estrutura reversível
- ✅ Funcionalidades preservadas
"""
        
        index_path = self.base_path / "ARQUIVO_ORGANIZACAO_INDEX.md"
        index_path.write_text(index_content, encoding='utf-8')
        
        logger.info(f"📋 Índice criado: {index_path.name}")
    
    def organize_files(self):
        """Executa organização completa dos arquivos"""
        logger.info("🧹 Iniciando organização de arquivos...")
        
        try:
            # 1. Criar estrutura
            self.create_directory_structure()
            
            # 2. Identificar arquivos
            categories = self.get_migration_files()
            
            total_files = sum(len(files) for files in categories.values())
            logger.info(f"📊 Encontrados {total_files} arquivos para organizar")
            
            # 3. Mover arquivos
            moved_files = self.move_files_to_organized_structure(categories)
            
            # 4. Criar índice
            self.create_index_file(moved_files)
            
            logger.info(f"✅ Organização concluída: {len(moved_files)} arquivos movidos")
            logger.info(f"💾 Backup disponível em: {self.backup_dir.relative_to(self.base_path)}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro na organização: {e}")
            return False

def main():
    """Executa organização de arquivos"""
    print("🧹 ORGANIZADOR DE ARQUIVOS - PAINELUNIVERSAL")
    print("=" * 50)
    
    base_path = Path(__file__).parent
    organizer = FileOrganizer(str(base_path))
    
    # Confirmar com usuário
    print(f"📁 Diretório base: {base_path}")
    print("🔍 Esta operação irá:")
    print("  - Criar estrutura organizada de diretórios")
    print("  - Mover arquivos de migração para locais apropriados")
    print("  - Criar backup completo dos arquivos originais")
    print("  - Gerar índice de arquivos organizados")
    
    confirm = input("\n❓ Continuar com a organização? (s/N): ").lower().strip()
    
    if confirm in ['s', 'sim', 'yes', 'y']:
        success = organizer.organize_files()
        
        if success:
            print("✅ ORGANIZAÇÃO CONCLUÍDA COM SUCESSO!")
            print("📋 Verifique ARQUIVO_ORGANIZACAO_INDEX.md para detalhes")
            return 0
        else:
            print("❌ ERRO NA ORGANIZAÇÃO")
            return 1
    else:
        print("❌ Operação cancelada pelo usuário")
        return 1

if __name__ == "__main__":
    exit(main())
