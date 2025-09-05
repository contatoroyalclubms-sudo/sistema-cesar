#!/usr/bin/env python3
"""
Script para analisar a estrutura completa do projeto de gestão de eventos
e identificar funcionalidades implementadas vs. faltantes
"""
import os
import json
import re
from pathlib import Path
from typing import Dict, List, Set

class ProjectAnalyzer:
    def __init__(self, base_path: str = "."):
        self.base_path = Path(base_path)
        self.analysis = {
            "backend": {
                "models": {},
                "routers": {},
                "schemas": {},
                "services": {},
                "migrations": []
            },
            "frontend": {
                "components": {},
                "pages": {},
                "contexts": {},
                "services": {},
                "types": {}
            },
            "database": {
                "tables": [],
                "relationships": [],
                "enums": []
            }
        }
    
    def analyze_backend_models(self):
        """Analisa todos os modelos do backend"""
        models_path = self.base_path / "backend" / "app"
        model_files = list(models_path.glob("models*.py"))
        
        for model_file in model_files:
            with open(model_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
                # Encontrar classes que herdam de Base
                classes = re.findall(r'class\s+(\w+)\(Base\):', content)
                
                # Encontrar enums
                enums = re.findall(r'class\s+(\w+)\(enum\.Enum\):', content)
                
                # Encontrar relacionamentos
                relationships = re.findall(r'relationship\("(\w+)"', content)
                
                self.analysis["backend"]["models"][model_file.name] = {
                    "tables": classes,
                    "enums": enums,
                    "relationships": relationships
                }
                
                self.analysis["database"]["tables"].extend(classes)
                self.analysis["database"]["enums"].extend(enums)
    
    def analyze_backend_routers(self):
        """Analisa todos os routers do backend"""
        routers_path = self.base_path / "backend" / "app" / "routers"
        
        if routers_path.exists():
            router_files = list(routers_path.glob("*.py"))
            
            for router_file in router_files:
                if router_file.name == "__init__.py":
                    continue
                    
                with open(router_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                    # Encontrar endpoints
                    endpoints = re.findall(r'@router\.(get|post|put|delete|patch)\("([^"]+)"', content)
                    
                    # Encontrar dependências de autenticação
                    auth_deps = re.findall(r'Depends\((\w+)\)', content)
                    
                    self.analysis["backend"]["routers"][router_file.stem] = {
                        "endpoints": endpoints,
                        "auth_required": "get_current_user" in auth_deps or "require_admin" in auth_deps
                    }
    
    def analyze_backend_schemas(self):
        """Analisa todos os schemas do backend"""
        schemas_path = self.base_path / "backend" / "app"
        schema_files = list(schemas_path.glob("schemas*.py"))
        
        for schema_file in schema_files:
            try:
                with open(schema_file, 'r', encoding='utf-8') as f:
                    content = f.read()
            except UnicodeDecodeError:
                with open(schema_file, 'r', encoding='latin-1') as f:
                    content = f.read()
            
            # Encontrar classes Pydantic
            pydantic_classes = re.findall(r'class\s+(\w+)\((?:BaseModel|BaseSchema|.*Schema|.*Base)\):', content)
            
            self.analysis["backend"]["schemas"][schema_file.name] = pydantic_classes
    
    def analyze_backend_services(self):
        """Analisa todos os serviços do backend"""
        services_path = self.base_path / "backend" / "app" / "services"
        
        if services_path.exists():
            service_files = list(services_path.glob("*.py"))
            
            for service_file in service_files:
                if service_file.name == "__init__.py":
                    continue
                    
                with open(service_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                    # Encontrar funções e classes
                    functions = re.findall(r'def\s+(\w+)\s*\(', content)
                    classes = re.findall(r'class\s+(\w+)\s*(?:\(|:)', content)
                    
                    self.analysis["backend"]["services"][service_file.stem] = {
                        "functions": functions,
                        "classes": classes
                    }
    
    def analyze_frontend(self):
        """Analisa estrutura do frontend"""
        frontend_path = self.base_path / "frontend" / "src"
        
        if not frontend_path.exists():
            return
        
        # Componentes
        components_path = frontend_path / "components"
        if components_path.exists():
            for comp_dir in components_path.iterdir():
                if comp_dir.is_dir():
                    comp_files = list(comp_dir.glob("*.tsx")) + list(comp_dir.glob("*.ts"))
                    self.analysis["frontend"]["components"][comp_dir.name] = [f.name for f in comp_files]
        
        # Páginas
        pages_path = frontend_path / "pages"
        if pages_path.exists():
            page_files = list(pages_path.glob("*.tsx"))
            self.analysis["frontend"]["pages"] = [f.stem for f in page_files]
        
        # Contexts
        contexts_path = frontend_path / "contexts"
        if contexts_path.exists():
            context_files = list(contexts_path.glob("*.tsx"))
            self.analysis["frontend"]["contexts"] = [f.stem for f in context_files]
        
        # Services
        services_path = frontend_path / "services"
        if services_path.exists():
            service_files = list(services_path.glob("*.ts"))
            self.analysis["frontend"]["services"] = [f.stem for f in service_files]
        
        # Types
        types_path = frontend_path / "types"
        if types_path.exists():
            type_files = list(types_path.glob("*.ts"))
            self.analysis["frontend"]["types"] = [f.stem for f in type_files]
    
    def generate_report(self):
        """Gera relatório da análise"""
        self.analyze_backend_models()
        self.analyze_backend_routers()
        self.analyze_backend_schemas()
        self.analyze_backend_services()
        self.analyze_frontend()
        
        # Contar estatísticas
        stats = {
            "total_tables": len(set(self.analysis["database"]["tables"])),
            "total_enums": len(set(self.analysis["database"]["enums"])),
            "total_routers": len(self.analysis["backend"]["routers"]),
            "total_services": len(self.analysis["backend"]["services"]),
            "total_frontend_components": sum(len(files) for files in self.analysis["frontend"]["components"].values())
        }
        
        return {
            "statistics": stats,
            "analysis": self.analysis
        }

if __name__ == "__main__":
    analyzer = ProjectAnalyzer()
    report = analyzer.generate_report()
    
    # Salvar relatório
    with open("project_analysis.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print("Análise completa!")
    print(f"\nEstatísticas:")
    for key, value in report["statistics"].items():
        print(f"  {key}: {value}")
    
    print(f"\nTabelas encontradas: {len(set(report['analysis']['database']['tables']))}")
    print(f"Routers encontrados: {len(report['analysis']['backend']['routers'])}")
    print(f"Services encontrados: {len(report['analysis']['backend']['services'])}")