#!/usr/bin/env python3
"""
🔧 CORREÇÃO AUTOMÁTICA DE IMPORTAÇÕES - SISTEMA PAINEL UNIVERSAL
Script para corrigir importações relativas incorretas automaticamente
"""
import os
import re
import shutil
from datetime import datetime
from pathlib import Path

class ImportFixerTool:
    """Ferramenta para corrigir importações automaticamente"""
    
    def __init__(self, backend_path: str):
        self.backend_path = Path(backend_path)
        self.fixes_made = []
        self.errors = []
        
    def backup_file(self, file_path: Path) -> Path:
        """Criar backup do arquivo antes da modificação"""
        backup_dir = self.backend_path / "backups_import_fix"
        backup_dir.mkdir(exist_ok=True)
        
        # Criar estrutura de diretórios no backup
        relative_path = file_path.relative_to(self.backend_path)
        backup_file = backup_dir / relative_path
        backup_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Copiar arquivo
        shutil.copy2(file_path, backup_file)
        return backup_file
        
    def analyze_file(self, file_path: Path) -> dict:
        """Analisar arquivo e encontrar importações problemáticas"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Padrões de importações problemáticas
            patterns = [
                (r'from \.\.database import', 'from .database import'),
                (r'from \.\.models import', 'from .models import'),
                (r'from \.\.schemas import', 'from .schemas import'),
                (r'from \.\.auth import', 'from .auth import'),
                (r'from \.\.auth_functions import', 'from .auth_functions import'),
                (r'from \.\.services import', 'from .services import'),
                (r'from \.\.middleware import', 'from .middleware import'),
                (r'from \.\.utils import', 'from .utils import'),
                (r'from \.\.routers import', 'from .routers import'),
                (r'from \.\.migrations import', 'from .migrations import'),
                (r'from \.\.websocket import', 'from .websocket import'),
                (r'from \.\.scheduler import', 'from .scheduler import'),
            ]
            
            issues = []
            fixed_content = content
            
            for old_pattern, new_pattern in patterns:
                matches = re.findall(old_pattern, content)
                if matches:
                    issues.append({
                        'pattern': old_pattern,
                        'replacement': new_pattern,
                        'count': len(matches)
                    })
                    # Aplicar correção
                    fixed_content = re.sub(old_pattern, new_pattern, fixed_content)
            
            return {
                'file': file_path,
                'issues': issues,
                'original_content': content,
                'fixed_content': fixed_content,
                'needs_fix': len(issues) > 0
            }
            
        except Exception as e:
            self.errors.append(f"Erro ao analisar {file_path}: {str(e)}")
            return {'file': file_path, 'error': str(e)}
    
    def fix_file(self, analysis: dict, dry_run: bool = False) -> bool:
        """Aplicar correções ao arquivo"""
        if not analysis.get('needs_fix', False):
            return False
            
        file_path = analysis['file']
        
        try:
            if not dry_run:
                # Criar backup
                backup_path = self.backup_file(file_path)
                
                # Aplicar correções
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(analysis['fixed_content'])
                
                self.fixes_made.append({
                    'file': str(file_path),
                    'backup': str(backup_path),
                    'issues_fixed': len(analysis['issues']),
                    'issues': analysis['issues'],
                    'timestamp': datetime.now().isoformat()
                })
                
                print(f"✅ Corrigido: {file_path.name} ({len(analysis['issues'])} problemas)")
            else:
                print(f"🔍 [DRY RUN] Seria corrigido: {file_path.name} ({len(analysis['issues'])} problemas)")
                for issue in analysis['issues']:
                    print(f"    • {issue['pattern']} → {issue['replacement']} ({issue['count']}x)")
            
            return True
            
        except Exception as e:
            error_msg = f"Erro ao corrigir {file_path}: {str(e)}"
            self.errors.append(error_msg)
            print(f"❌ {error_msg}")
            return False
    
    def scan_and_fix(self, dry_run: bool = False):
        """Escanear todos os arquivos Python e aplicar correções"""
        print("🔍 ESCANEANDO ARQUIVOS PYTHON PARA PROBLEMAS DE IMPORTAÇÃO")
        print("=" * 70)
        
        # Encontrar todos os arquivos Python
        python_files = []
        for pattern in ['**/*.py']:
            python_files.extend(self.backend_path.glob(pattern))
        
        print(f"📁 Encontrados {len(python_files)} arquivos Python")
        print()
        
        # Analisar arquivos
        files_to_fix = []
        total_issues = 0
        
        for file_path in python_files:
            # Pular backups e __pycache__
            if 'backup' in str(file_path) or '__pycache__' in str(file_path):
                continue
                
            analysis = self.analyze_file(file_path)
            
            if analysis.get('needs_fix', False):
                files_to_fix.append(analysis)
                total_issues += len(analysis['issues'])
        
        print(f"🚨 PROBLEMAS ENCONTRADOS:")
        print(f"   📄 Arquivos com problemas: {len(files_to_fix)}")
        print(f"   🔧 Total de importações a corrigir: {total_issues}")
        print()
        
        if not files_to_fix:
            print("✅ Nenhum problema de importação encontrado!")
            return
        
        # Mostrar resumo dos problemas
        print("📋 ARQUIVOS QUE PRECISAM DE CORREÇÃO:")
        for analysis in files_to_fix:
            print(f"   • {analysis['file'].name} - {len(analysis['issues'])} problemas")
        print()
        
        if dry_run:
            print("🧪 EXECUTANDO EM MODO DRY RUN (sem alterações)")
        else:
            print("🔧 APLICANDO CORREÇÕES...")
        print("-" * 70)
        
        # Aplicar correções
        success_count = 0
        for analysis in files_to_fix:
            if self.fix_file(analysis, dry_run):
                success_count += 1
        
        # Relatório final
        print()
        print("=" * 70)
        print("📊 RELATÓRIO DE CORREÇÕES")
        print("=" * 70)
        print(f"✅ Arquivos corrigidos: {success_count}/{len(files_to_fix)}")
        print(f"❌ Erros: {len(self.errors)}")
        
        if self.errors:
            print("\n🚨 ERROS ENCONTRADOS:")
            for error in self.errors:
                print(f"   • {error}")
        
        if not dry_run and self.fixes_made:
            print(f"\n💾 Backups salvos em: {self.backend_path}/backups_import_fix/")
            print(f"📅 Total de correções aplicadas: {len(self.fixes_made)}")
            
            # Salvar relatório
            report_file = self.backend_path / f"import_fix_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            import json
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'timestamp': datetime.now().isoformat(),
                    'fixes_made': self.fixes_made,
                    'errors': self.errors,
                    'summary': {
                        'files_processed': len(files_to_fix),
                        'files_fixed': success_count,
                        'total_issues_fixed': sum(fix['issues_fixed'] for fix in self.fixes_made)
                    }
                }, f, indent=2, ensure_ascii=False)
            
            print(f"📋 Relatório detalhado salvo em: {report_file.name}")

def main():
    """Função principal"""
    print("🔧 FERRAMENTA DE CORREÇÃO DE IMPORTAÇÕES")
    print("🎯 Sistema: Painel Universal")
    print("📅 Data:", datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
    print()
    
    backend_path = "backend"
    
    # Verificar se o diretório existe
    if not os.path.exists(backend_path):
        print(f"❌ Diretório {backend_path} não encontrado!")
        return
    
    # Criar ferramenta
    fixer = ImportFixerTool(backend_path)
    
    # Primeiro executar em dry run
    print("🧪 FASE 1: ANÁLISE (DRY RUN)")
    print("-" * 50)
    fixer.scan_and_fix(dry_run=True)
    
    print("\n" + "="*50)
    response = input("Deseja aplicar as correções? (s/N): ").strip().lower()
    
    if response in ['s', 'sim', 'y', 'yes']:
        print("\n🔧 FASE 2: APLICANDO CORREÇÕES")
        print("-" * 50)
        fixer.scan_and_fix(dry_run=False)
        print("\n🎉 CORREÇÕES CONCLUÍDAS!")
    else:
        print("\n❌ Correções canceladas pelo usuário.")

if __name__ == "__main__":
    main()
