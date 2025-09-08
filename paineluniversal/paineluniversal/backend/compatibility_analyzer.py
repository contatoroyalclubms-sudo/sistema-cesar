#!/usr/bin/env python3
"""
🔍 ANALISADOR DE COMPATIBILIDADE COMPLETO
Sistema de análise e correção automática de compatibilidade entre Backend ↔ Frontend ↔ Database

Este script identifica e corrige incompatibilidades sem quebrar funcionalidades existentes.
"""

import os
import sys
import json
import re
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
from sqlalchemy import inspect, create_engine
from sqlalchemy.orm import sessionmaker

# Adicionar o diretório raiz ao path para importar módulos
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    from app.database import engine, get_db
    from app.models import *
    from app.schemas import *
except ImportError as e:
    print(f"❌ Erro ao importar módulos: {e}")
    print("ℹ️  Execute o script a partir do diretório backend/")
    sys.exit(1)

class CompatibilityAnalyzer:
    """Analisador completo de compatibilidade do sistema"""
    
    def __init__(self):
        self.issues = []
        self.warnings = []
        self.fixes_applied = []
        self.frontend_path = project_root.parent / "frontend"
        
    def log_issue(self, category: str, description: str, severity: str = "medium"):
        """Registra um problema encontrado"""
        self.issues.append({
            "category": category,
            "description": description,
            "severity": severity,
            "timestamp": datetime.now().isoformat()
        })
        
    def log_warning(self, description: str):
        """Registra um aviso"""
        self.warnings.append({
            "description": description,
            "timestamp": datetime.now().isoformat()
        })
        
    def log_fix(self, description: str):
        """Registra uma correção aplicada"""
        self.fixes_applied.append({
            "description": description,
            "timestamp": datetime.now().isoformat()
        })

    def analyze_database_schema(self) -> Dict[str, Any]:
        """Analisa o schema do banco de dados"""
        print("🔍 Analisando schema do banco de dados...")
        
        try:
            inspector = inspect(engine)
            tables = inspector.get_table_names()
            
            schema_info = {}
            for table_name in tables:
                columns = inspector.get_columns(table_name)
                foreign_keys = inspector.get_foreign_keys(table_name)
                indexes = inspector.get_indexes(table_name)
                
                schema_info[table_name] = {
                    "columns": [
                        {
                            "name": col["name"],
                            "type": str(col["type"]),
                            "nullable": col["nullable"],
                            "default": col.get("default"),
                            "primary_key": col.get("primary_key", False)
                        }
                        for col in columns
                    ],
                    "foreign_keys": [
                        {
                            "constrained_columns": fk["constrained_columns"],
                            "referred_table": fk["referred_table"],
                            "referred_columns": fk["referred_columns"]
                        }
                        for fk in foreign_keys
                    ],
                    "indexes": [
                        {
                            "name": idx["name"],
                            "column_names": idx["column_names"],
                            "unique": idx["unique"]
                        }
                        for idx in indexes
                    ]
                }
            
            print(f"✅ Schema analisado: {len(tables)} tabelas encontradas")
            return schema_info
            
        except Exception as e:
            self.log_issue("database", f"Erro ao analisar schema: {e}", "high")
            return {}

    def analyze_backend_models(self) -> Dict[str, Any]:
        """Analisa os modelos SQLAlchemy do backend"""
        print("🔍 Analisando modelos do backend...")
        
        models_info = {}
        
        # Mapear modelos conhecidos
        known_models = {
            "Usuario": Usuario,
            "Empresa": Empresa,
            "Evento": Evento,
            "Lista": Lista,
            "Transacao": Transacao,
            "Checkin": Checkin,
            "PromoterEvento": PromoterEvento,
            "Produto": Produto,
            "CategoriaProduto": CategoriaProduto,
            "Comanda": Comanda,
            "VendaPDV": VendaPDV,
            "ClienteEvento": ClienteEvento,
            "EquipamentoEvento": EquipamentoEvento,
            "SessaoOperador": SessaoOperador,
            "LogAuditoria": LogAuditoria
        }
        
        for model_name, model_class in known_models.items():
            try:
                # Analisar colunas do modelo
                columns = {}
                relationships = {}
                
                for attr_name in dir(model_class):
                    attr = getattr(model_class, attr_name)
                    
                    # Verificar se é uma coluna
                    if hasattr(attr, 'property') and hasattr(attr.property, 'columns'):
                        column = attr.property.columns[0]
                        columns[attr_name] = {
                            "type": str(column.type),
                            "nullable": column.nullable,
                            "primary_key": column.primary_key,
                            "foreign_key": bool(column.foreign_keys),
                            "default": str(column.default) if column.default else None
                        }
                    
                    # Verificar se é um relacionamento
                    elif hasattr(attr, 'property') and hasattr(attr.property, 'mapper'):
                        relationships[attr_name] = {
                            "target_class": attr.property.mapper.class_.__name__,
                            "back_populates": getattr(attr.property, 'back_populates', None)
                        }
                
                models_info[model_name] = {
                    "table_name": model_class.__tablename__,
                    "columns": columns,
                    "relationships": relationships
                }
                
            except Exception as e:
                self.log_warning(f"Erro ao analisar modelo {model_name}: {e}")
        
        print(f"✅ Modelos analisados: {len(models_info)} modelos")
        return models_info

    def analyze_frontend_types(self) -> Dict[str, Any]:
        """Analisa os tipos TypeScript do frontend"""
        print("🔍 Analisando tipos do frontend...")
        
        frontend_types = {}
        
        # Arquivos de tipos para analisar
        type_files = [
            self.frontend_path / "src" / "services" / "api.ts",
            self.frontend_path / "src" / "types" / "produto.ts",
            self.frontend_path / "src" / "services" / "api-new.ts",
            self.frontend_path / "src" / "components" / "usuarios" / "UsuariosModule.tsx"
        ]
        
        for file_path in type_files:
            if file_path.exists():
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Extrair interfaces TypeScript
                    interface_pattern = r'interface\s+(\w+)\s*{([^}]+)}'
                    interfaces = re.findall(interface_pattern, content, re.DOTALL)
                    
                    for interface_name, interface_body in interfaces:
                        # Extrair propriedades da interface
                        prop_pattern = r'(\w+)(\?)?\s*:\s*([^;]+);?'
                        properties = re.findall(prop_pattern, interface_body)
                        
                        frontend_types[interface_name] = {
                            "file": str(file_path.relative_to(self.frontend_path)),
                            "properties": {
                                prop_name: {
                                    "type": prop_type.strip(),
                                    "optional": bool(optional)
                                }
                                for prop_name, optional, prop_type in properties
                            }
                        }
                        
                except Exception as e:
                    self.log_warning(f"Erro ao analisar {file_path}: {e}")
        
        print(f"✅ Tipos frontend analisados: {len(frontend_types)} interfaces")
        return frontend_types

    def compare_backend_frontend_types(self, backend_models: Dict, frontend_types: Dict) -> List[Dict]:
        """Compara tipos entre backend e frontend"""
        print("🔍 Comparando compatibilidade Backend ↔ Frontend...")
        
        incompatibilities = []
        
        # Mapear modelos backend para interfaces frontend
        model_interface_mapping = {
            "Usuario": ["Usuario", "UsuarioCreate", "UsuarioDetalhado"],
            "Empresa": ["Empresa", "EmpresaCreate"],
            "Evento": ["Evento", "EventoCreate"],
            "Produto": ["Produto", "ProdutoCreate"],
            "Lista": ["Lista", "ListaCreate"],
            "Transacao": ["Transacao", "TransacaoCreate"],
            "Checkin": ["Checkin", "CheckinCreate"]
        }
        
        for model_name, interface_names in model_interface_mapping.items():
            if model_name not in backend_models:
                continue
                
            backend_model = backend_models[model_name]
            backend_columns = backend_model["columns"]
            
            for interface_name in interface_names:
                if interface_name not in frontend_types:
                    incompatibilities.append({
                        "type": "missing_interface",
                        "model": model_name,
                        "interface": interface_name,
                        "severity": "medium",
                        "description": f"Interface {interface_name} não encontrada no frontend"
                    })
                    continue
                
                frontend_interface = frontend_types[interface_name]
                frontend_props = frontend_interface["properties"]
                
                # Verificar campos obrigatórios do backend
                for col_name, col_info in backend_columns.items():
                    if col_name in ["id", "criado_em", "atualizado_em"]:
                        continue  # Campos automáticos
                    
                    if not col_info["nullable"] and col_info["default"] is None:
                        # Campo obrigatório no backend
                        if col_name not in frontend_props:
                            incompatibilities.append({
                                "type": "missing_required_field",
                                "model": model_name,
                                "interface": interface_name,
                                "field": col_name,
                                "severity": "high",
                                "description": f"Campo obrigatório '{col_name}' ausente em {interface_name}"
                            })
                        elif frontend_props[col_name]["optional"]:
                            incompatibilities.append({
                                "type": "required_field_optional",
                                "model": model_name,
                                "interface": interface_name,
                                "field": col_name,
                                "severity": "medium",
                                "description": f"Campo '{col_name}' é obrigatório no backend mas opcional no frontend"
                            })
                
                # Verificar tipos incompatíveis
                for prop_name, prop_info in frontend_props.items():
                    if prop_name in backend_columns:
                        backend_type = backend_columns[prop_name]["type"]
                        frontend_type = prop_info["type"]
                        
                        # Verificar incompatibilidades de tipo básicas
                        type_incompatible = self._check_type_compatibility(backend_type, frontend_type)
                        if type_incompatible:
                            incompatibilities.append({
                                "type": "type_mismatch",
                                "model": model_name,
                                "interface": interface_name,
                                "field": prop_name,
                                "backend_type": backend_type,
                                "frontend_type": frontend_type,
                                "severity": "medium",
                                "description": f"Incompatibilidade de tipo: {prop_name} ({backend_type} vs {frontend_type})"
                            })
        
        print(f"⚠️  Incompatibilidades encontradas: {len(incompatibilities)}")
        return incompatibilities

    def _check_type_compatibility(self, backend_type: str, frontend_type: str) -> bool:
        """Verifica se há incompatibilidade entre tipos backend e frontend"""
        # Mapeamento básico de tipos
        type_mappings = {
            "INTEGER": ["number", "int"],
            "VARCHAR": ["string"],
            "TEXT": ["string"],
            "BOOLEAN": ["boolean", "bool"],
            "DATETIME": ["string", "Date"],
            "NUMERIC": ["number", "Decimal"],
            "DECIMAL": ["number", "Decimal"]
        }
        
        # Normalizar tipos
        backend_normalized = backend_type.upper().split("(")[0]  # Remove parâmetros como VARCHAR(255)
        frontend_normalized = frontend_type.strip().replace("?", "")  # Remove optional marker
        
        if backend_normalized in type_mappings:
            compatible_types = type_mappings[backend_normalized]
            return frontend_normalized not in compatible_types
        
        return False  # Se não conhecemos o tipo, assumir compatível

    def generate_typescript_interfaces(self, backend_models: Dict) -> str:
        """Gera interfaces TypeScript baseadas nos modelos backend"""
        print("🔧 Gerando interfaces TypeScript corretas...")
        
        typescript_code = '''// 🤖 GERADO AUTOMATICAMENTE - NÃO EDITAR MANUALMENTE
// Interfaces TypeScript sincronizadas com os modelos do backend
// Gerado em: ''' + datetime.now().isoformat() + '''

export type UserRole = 'admin' | 'promoter' | 'cliente' | 'operador';
export type StatusEvento = 'ATIVO' | 'INATIVO' | 'CANCELADO' | 'FINALIZADO';
export type TipoLista = 'VIP' | 'PREMIUM' | 'COMUM' | 'PROMOTER' | 'FREE';
export type StatusTransacao = 'PENDENTE' | 'APROVADA' | 'CANCELADA' | 'ESTORNADA';
export type TipoProduto = 'BEBIDA' | 'COMIDA' | 'INGRESSO' | 'FICHA' | 'COMBO' | 'VOUCHER';

'''
        
        # Mapear modelos para interfaces
        interface_mappings = {
            "Usuario": {
                "interface_name": "Usuario",
                "exclude_fields": ["senha_hash"],
                "optional_fields": ["id", "ativo", "ultimo_login", "criado_em", "atualizado_em", "empresa_id"]
            },
            "Empresa": {
                "interface_name": "Empresa", 
                "exclude_fields": [],
                "optional_fields": ["id", "ativa", "criado_em", "atualizado_em", "telefone", "endereco"]
            },
            "Evento": {
                "interface_name": "Evento",
                "exclude_fields": [],
                "optional_fields": ["id", "descricao", "endereco", "limite_idade", "capacidade_maxima", "status", "empresa_id", "criador_id", "criado_em", "atualizado_em"]
            },
            "Produto": {
                "interface_name": "Produto",
                "exclude_fields": [],
                "optional_fields": ["id", "codigo_interno", "categoria_id", "codigo_barras", "estoque_atual", "destaque", "habilitado", "promocional", "ativo", "criado_em", "atualizado_em"]
            }
        }
        
        for model_name, config in interface_mappings.items():
            if model_name not in backend_models:
                continue
                
            model = backend_models[model_name]
            interface_name = config["interface_name"]
            exclude_fields = config["exclude_fields"]
            optional_fields = config["optional_fields"]
            
            typescript_code += f"\nexport interface {interface_name} {{\n"
            
            for col_name, col_info in model["columns"].items():
                if col_name in exclude_fields:
                    continue
                
                # Mapear tipo SQL para TypeScript
                ts_type = self._sql_to_typescript_type(col_info["type"])
                optional_marker = "?" if col_name in optional_fields else ""
                
                typescript_code += f"  {col_name}{optional_marker}: {ts_type};\n"
            
            typescript_code += "}\n"
            
            # Gerar interface de criação
            if interface_name not in ["UsuarioCreate", "EmpresaCreate", "EventoCreate"]:
                create_interface_name = f"{interface_name}Create"
                typescript_code += f"\nexport interface {create_interface_name} extends Omit<{interface_name}, 'id' | 'criado_em' | 'atualizado_em'> {{\n"
                typescript_code += "  // Campos específicos para criação podem ser adicionados aqui\n"
                typescript_code += "}\n"
        
        # Adicionar interfaces de resposta da API
        typescript_code += '''
// Interfaces de resposta da API
export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  message?: string;
  errors?: string[];
}

export interface PaginatedResponse<T = any> {
  items: T[];
  total: number;
  page: number;
  limit: number;
  has_next: boolean;
  has_prev: boolean;
}

export interface LoginRequest {
  cpf: string;
  senha: string;
  codigo_verificacao?: string;
}

export interface Token {
  access_token: string;
  token_type: string;
  usuario: Usuario;
}
'''
        
        return typescript_code

    def _sql_to_typescript_type(self, sql_type: str) -> str:
        """Converte tipo SQL para TypeScript"""
        type_map = {
            "INTEGER": "number",
            "VARCHAR": "string", 
            "TEXT": "string",
            "BOOLEAN": "boolean",
            "DATETIME": "string",  # ISO string
            "NUMERIC": "number",
            "DECIMAL": "number",
            "DATE": "string",
            "TIMESTAMP": "string"
        }
        
        # Normalizar tipo (remover parâmetros)
        normalized_type = sql_type.upper().split("(")[0]
        
        # Verificar enums
        if "ENUM" in sql_type.upper():
            if "TipoUsuario" in sql_type:
                return "UserRole"
            elif "StatusEvento" in sql_type:
                return "StatusEvento"
            elif "TipoLista" in sql_type:
                return "TipoLista"
            elif "StatusTransacao" in sql_type:
                return "StatusTransacao"
            elif "TipoProduto" in sql_type:
                return "TipoProduto"
        
        return type_map.get(normalized_type, "any")

    def create_compatibility_fixes(self, incompatibilities: List[Dict]) -> List[str]:
        """Cria correções para as incompatibilidades encontradas"""
        print("🔧 Criando correções de compatibilidade...")
        
        fixes = []
        
        # Agrupar incompatibilidades por tipo
        by_type = {}
        for incomp in incompatibilities:
            incomp_type = incomp["type"]
            if incomp_type not in by_type:
                by_type[incomp_type] = []
            by_type[incomp_type].append(incomp)
        
        # Gerar correções por tipo
        for incomp_type, incomps in by_type.items():
            if incomp_type == "missing_interface":
                for incomp in incomps:
                    fix = f"Criar interface {incomp['interface']} baseada no modelo {incomp['model']}"
                    fixes.append(fix)
            
            elif incomp_type == "missing_required_field":
                for incomp in incomps:
                    fix = f"Adicionar campo obrigatório '{incomp['field']}' à interface {incomp['interface']}"
                    fixes.append(fix)
            
            elif incomp_type == "required_field_optional":
                for incomp in incomps:
                    fix = f"Remover '?' do campo '{incomp['field']}' na interface {incomp['interface']}"
                    fixes.append(fix)
            
            elif incomp_type == "type_mismatch":
                for incomp in incomps:
                    fix = f"Corrigir tipo do campo '{incomp['field']}' de {incomp['frontend_type']} para {incomp['backend_type']}"
                    fixes.append(fix)
        
        print(f"🔧 Correções identificadas: {len(fixes)}")
        return fixes

    def validate_backend_routes(self) -> Dict[str, Any]:
        """Valida se as rotas do backend estão funcionais"""
        print("🔍 Validando rotas do backend...")
        
        # Analisar routers incluídos no main.py
        main_py_path = project_root / "app" / "main.py"
        
        routes_info = {
            "included_routers": [],
            "commented_routers": [],
            "missing_routers": []
        }
        
        try:
            with open(main_py_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Encontrar routers incluídos
            include_pattern = r'app\.include_router\((\w+)\.router'
            included = re.findall(include_pattern, content)
            routes_info["included_routers"] = included
            
            # Encontrar routers comentados
            commented_pattern = r'#\s*app\.include_router\((\w+)\.router'
            commented = re.findall(commented_pattern, content)
            routes_info["commented_routers"] = commented
            
            # Verificar se router MEEP está comentado
            if "meep" in commented:
                self.log_issue("routes", "Router MEEP está comentado", "medium")
            
        except Exception as e:
            self.log_issue("routes", f"Erro ao analisar main.py: {e}", "high")
        
        return routes_info

    def generate_migration_script(self, incompatibilities: List[Dict]) -> str:
        """Gera script de migração segura"""
        print("📋 Gerando script de migração...")
        
        migration_script = f'''#!/usr/bin/env python3
"""
🔄 SCRIPT DE MIGRAÇÃO AUTOMÁTICA
Gerado em: {datetime.now().isoformat()}

Este script aplica correções de compatibilidade de forma segura,
mantendo funcionalidades existentes.
"""

import os
import shutil
from datetime import datetime
from pathlib import Path

def backup_files():
    """Cria backup dos arquivos que serão modificados"""
    backup_dir = Path("backup_compatibility_" + datetime.now().strftime("%Y%m%d_%H%M%S"))
    backup_dir.mkdir(exist_ok=True)
    
    # Backup do frontend
    frontend_src = Path("../frontend/src")
    if frontend_src.exists():
        shutil.copytree(frontend_src, backup_dir / "frontend_src")
    
    print(f"✅ Backup criado em: {{backup_dir}}")
    return backup_dir

def apply_typescript_fixes():
    """Aplica correções nos tipos TypeScript"""
    frontend_types_dir = Path("../frontend/src/types")
    frontend_types_dir.mkdir(exist_ok=True)
    
    # Criar arquivo de tipos corretos
    types_content = \'\'\'{self.generate_typescript_interfaces(self.analyze_backend_models())}\'\'\'
    
    with open(frontend_types_dir / "database.ts", "w", encoding="utf-8") as f:
        f.write(types_content)
    
    print("✅ Tipos TypeScript atualizados")

def main():
    """Executa migração completa"""
    print("🚀 Iniciando migração de compatibilidade...")
    
    # 1. Backup
    backup_dir = backup_files()
    
    # 2. Aplicar correções
    apply_typescript_fixes()
    
    print("✅ Migração concluída com sucesso!")
    print(f"📁 Backup disponível em: {{backup_dir}}")

if __name__ == "__main__":
    main()
'''
        
        return migration_script

    def run_complete_analysis(self) -> Dict[str, Any]:
        """Executa análise completa do sistema"""
        print("🔍 INICIANDO ANÁLISE COMPLETA DE COMPATIBILIDADE")
        print("=" * 60)
        
        # 1. Analisar banco de dados
        database_schema = self.analyze_database_schema()
        
        # 2. Analisar modelos backend
        backend_models = self.analyze_backend_models()
        
        # 3. Analisar tipos frontend
        frontend_types = self.analyze_frontend_types()
        
        # 4. Comparar compatibilidade
        incompatibilities = self.compare_backend_frontend_types(backend_models, frontend_types)
        
        # 5. Validar rotas
        routes_info = self.validate_backend_routes()
        
        # 6. Gerar correções
        fixes = self.create_compatibility_fixes(incompatibilities)
        
        # 7. Gerar TypeScript correto
        typescript_interfaces = self.generate_typescript_interfaces(backend_models)
        
        # 8. Gerar script de migração
        migration_script = self.generate_migration_script(incompatibilities)
        
        # Compilar relatório final
        report = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "database_tables": len(database_schema),
                "backend_models": len(backend_models),
                "frontend_interfaces": len(frontend_types),
                "incompatibilities_found": len(incompatibilities),
                "fixes_available": len(fixes),
                "issues": len(self.issues),
                "warnings": len(self.warnings)
            },
            "database_schema": database_schema,
            "backend_models": backend_models,
            "frontend_types": frontend_types,
            "incompatibilities": incompatibilities,
            "routes_info": routes_info,
            "fixes": fixes,
            "issues": self.issues,
            "warnings": self.warnings,
            "typescript_interfaces": typescript_interfaces,
            "migration_script": migration_script
        }
        
        return report

def main():
    """Função principal"""
    print("🚀 SISTEMA DE ANÁLISE DE COMPATIBILIDADE")
    print("=" * 50)
    
    analyzer = CompatibilityAnalyzer()
    report = analyzer.run_complete_analysis()
    
    # Salvar relatório
    report_file = f"compatibility_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False, default=str)
    
    # Salvar interfaces TypeScript
    ts_file = "generated_types.ts"
    with open(ts_file, 'w', encoding='utf-8') as f:
        f.write(report["typescript_interfaces"])
    
    # Salvar script de migração
    migration_file = "migration_script.py"
    with open(migration_file, 'w', encoding='utf-8') as f:
        f.write(report["migration_script"])
    
    # Exibir resumo
    print("\n" + "=" * 60)
    print("📊 RESUMO DA ANÁLISE")
    print("=" * 60)
    print(f"📋 Tabelas no banco: {report['summary']['database_tables']}")
    print(f"🏗️  Modelos backend: {report['summary']['backend_models']}")
    print(f"📝 Interfaces frontend: {report['summary']['frontend_interfaces']}")
    print(f"⚠️  Incompatibilidades: {report['summary']['incompatibilities_found']}")
    print(f"🔧 Correções disponíveis: {report['summary']['fixes_available']}")
    print(f"🚨 Issues encontradas: {report['summary']['issues']}")
    print(f"⚠️  Warnings: {report['summary']['warnings']}")
    
    print("\n📁 ARQUIVOS GERADOS:")
    print(f"   📊 {report_file}")
    print(f"   📝 {ts_file}")
    print(f"   🔄 {migration_file}")
    
    if report['summary']['incompatibilities_found'] > 0:
        print("\n🚨 AÇÃO REQUERIDA:")
        print("   Execute o script de migração para corrigir incompatibilidades")
        print(f"   Comando: python {migration_file}")
    else:
        print("\n✅ SISTEMA COMPATÍVEL:")
        print("   Nenhuma incompatibilidade crítica encontrada")
    
    return report

if __name__ == "__main__":
    main()
