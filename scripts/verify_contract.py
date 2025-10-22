#!/usr/bin/env python3
"""
Script de Verificação de Contrato API NIP
Valida se o OpenAPI spec está aderente aos padrões definidos.
"""

import sys
import yaml
import json
from pathlib import Path
from typing import Dict, List, Any, Tuple
import re

class APIContractVerifier:
    def __init__(self, spec_path: str):
        self.spec_path = Path(spec_path)
        self.spec = None
        self.errors = []
        self.warnings = []
        
    def load_spec(self) -> bool:
        """Carrega o arquivo OpenAPI spec"""
        try:
            if self.spec_path.suffix.lower() in ['.yaml', '.yml']:
                with open(self.spec_path, 'r', encoding='utf-8') as f:
                    self.spec = yaml.safe_load(f)
            else:
                with open(self.spec_path, 'r', encoding='utf-8') as f:
                    self.spec = json.load(f)
            return True
        except Exception as e:
            self.errors.append(f"❌ Erro ao carregar spec: {e}")
            return False
    
    def verify_basic_structure(self):
        """Verifica estrutura básica do OpenAPI"""
        if not self.spec.get('openapi'):
            self.errors.append("❌ Campo 'openapi' obrigatório")
            
        info = self.spec.get('info', {})
        if not info.get('title'):
            self.errors.append("❌ Campo 'info.title' obrigatório")
        if not info.get('version'):
            self.errors.append("❌ Campo 'info.version' obrigatório")
        elif not re.match(r'^\d+\.\d+\.\d+$', info['version']):
            self.warnings.append("⚠️ Versão deve seguir semver (x.y.z)")
            
        if not self.spec.get('paths'):
            self.errors.append("❌ Campo 'paths' obrigatório")
    
    def verify_security(self):
        """Verifica configuração de segurança JWT"""
        security = self.spec.get('security', [])
        if not security:
            self.errors.append("❌ Segurança global deve estar definida")
            
        security_schemes = self.spec.get('components', {}).get('securitySchemes', {})
        bearer_auth = security_schemes.get('bearerAuth')
        
        if not bearer_auth:
            self.errors.append("❌ bearerAuth deve estar definido em securitySchemes")
        elif bearer_auth.get('type') != 'http' or bearer_auth.get('scheme') != 'bearer':
            self.errors.append("❌ bearerAuth deve usar type: http, scheme: bearer")
    
    def verify_auth_endpoint(self):
        """Verifica endpoint de autenticação"""
        auth_path = self.spec.get('paths', {}).get('/api/auth/login')
        if not auth_path:
            self.errors.append("❌ Endpoint /api/auth/login não encontrado")
            return
            
        post_method = auth_path.get('post')
        if not post_method:
            self.errors.append("❌ /api/auth/login deve usar método POST")
            return
            
        # Verificar se é público (security: [])
        security = post_method.get('security', 'not_defined')
        if security != []:
            self.errors.append("❌ /api/auth/login deve ser público (security: [])")
            
        # Verificar requestBody
        if not post_method.get('requestBody'):
            self.errors.append("❌ /api/auth/login deve ter requestBody")
        
        # Verificar respostas
        responses = post_method.get('responses', {})
        if '200' not in responses:
            self.errors.append("❌ /api/auth/login deve ter resposta 200")
        if '401' not in responses:
            self.warnings.append("⚠️ /api/auth/login deveria ter resposta 401")
    
    def verify_rest_patterns(self):
        """Verifica padrões REST"""
        paths = self.spec.get('paths', {})
        
        for path, methods in paths.items():
            # Verificar verbos em paths
            if re.search(r'/(criar|listar|obter|atualizar|ativar|desativar|remover|deletar)', path):
                deprecated_found = False
                for method, details in methods.items():
                    if isinstance(details, dict) and details.get('deprecated'):
                        deprecated_found = True
                        break
                
                if not deprecated_found:
                    self.errors.append(f"❌ Path com verbo deve ser deprecated: {path}")
            
            # Verificar kebab-case
            if not re.match(r'^[/a-z0-9{}-]*$', path):
                self.warnings.append(f"⚠️ Path deve usar kebab-case: {path}")
            
            # Verificar métodos e status codes
            for method, details in methods.items():
                if not isinstance(details, dict):
                    continue
                    
                responses = details.get('responses', {})
                
                if method == 'post':
                    if '201' not in responses:
                        self.warnings.append(f"⚠️ POST {path} deveria retornar 201")
                    elif '201' in responses:
                        headers = responses['201'].get('headers', {})
                        if 'Location' not in headers:
                            self.warnings.append(f"⚠️ POST {path} 201 deveria ter header Location")
                
                if method == 'delete':
                    if '204' not in responses:
                        self.warnings.append(f"⚠️ DELETE {path} deveria retornar 204")
    
    def verify_pagination(self):
        """Verifica parâmetros de paginação"""
        paths = self.spec.get('paths', {})
        components_params = self.spec.get('components', {}).get('parameters', {})
        
        # Verificar se parâmetros de paginação estão definidos
        expected_params = ['Page', 'PageSize', 'Sort', 'Order', 'Search', 'DateFrom', 'DateTo']
        for param in expected_params:
            if param not in components_params:
                self.warnings.append(f"⚠️ Parâmetro reutilizável {param} não definido")
        
        # Verificar uso em endpoints de listagem
        for path, methods in paths.items():
            get_method = methods.get('get', {})
            if not get_method:
                continue
                
            summary = get_method.get('summary', '').lower()
            if 'listar' in summary or 'list' in summary:
                params = get_method.get('parameters', [])
                param_names = [p.get('name') for p in params if isinstance(p, dict)]
                
                if 'page' not in param_names and 'pageSize' not in param_names:
                    self.warnings.append(f"⚠️ Endpoint de listagem sem paginação: {path}")
    
    def verify_idempotency(self):
        """Verifica idempotência em endpoints financeiros"""
        paths = self.spec.get('paths', {})
        
        for path, methods in paths.items():
            if 'financeiro' in path.lower():
                post_method = methods.get('post')
                if post_method:
                    params = post_method.get('parameters', [])
                    idempotency_found = False
                    
                    for param in params:
                        if isinstance(param, dict) and param.get('name') == 'Idempotency-Key':
                            idempotency_found = True
                            break
                    
                    if not idempotency_found:
                        self.errors.append(f"❌ Endpoint financeiro sem Idempotency-Key: {path}")
                    
                    responses = post_method.get('responses', {})
                    if '409' not in responses:
                        self.warnings.append(f"⚠️ Endpoint com idempotência deveria ter resposta 409: {path}")
    
    def verify_documentation(self):
        """Verifica qualidade da documentação"""
        paths = self.spec.get('paths', {})
        
        for path, methods in paths.items():
            for method, details in methods.items():
                if not isinstance(details, dict):
                    continue
                
                if not details.get('summary'):
                    self.warnings.append(f"⚠️ Operação sem summary: {method.upper()} {path}")
                
                if not details.get('tags'):
                    self.warnings.append(f"⚠️ Operação sem tags: {method.upper()} {path}")
    
    def verify_schemas(self):
        """Verifica schemas e responses"""
        components = self.spec.get('components', {})
        schemas = components.get('schemas', {})
        
        # Verificar schemas essenciais
        essential_schemas = ['APIResponse', 'ErrorResponse', 'PaginationMeta']
        for schema_name in essential_schemas:
            if schema_name not in schemas:
                self.warnings.append(f"⚠️ Schema essencial não definido: {schema_name}")
        
        # Verificar responses com schema
        paths = self.spec.get('paths', {})
        for path, methods in paths.items():
            for method, details in methods.items():
                if not isinstance(details, dict):
                    continue
                
                responses = details.get('responses', {})
                for status, response in responses.items():
                    content = response.get('content', {}).get('application/json', {})
                    if content and not content.get('schema'):
                        self.warnings.append(f"⚠️ Response sem schema: {method.upper()} {path} {status}")
    
    def run_verification(self) -> bool:
        """Executa todas as verificações"""
        print("🔍 Iniciando verificação de contrato API...")
        print(f"📄 Arquivo: {self.spec_path}")
        print("-" * 60)
        
        if not self.load_spec():
            return False
        
        # Executar verificações
        self.verify_basic_structure()
        self.verify_security()
        self.verify_auth_endpoint()
        self.verify_rest_patterns()
        self.verify_pagination()
        self.verify_idempotency()
        self.verify_documentation()
        self.verify_schemas()
        
        # Apresentar resultados
        print(f"\n📊 RESULTADOS DA VERIFICAÇÃO")
        print("-" * 60)
        
        if self.errors:
            print(f"❌ ERROS ({len(self.errors)}):")
            for error in self.errors:
                print(f"  {error}")
        
        if self.warnings:
            print(f"\n⚠️ AVISOS ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"  {warning}")
        
        if not self.errors and not self.warnings:
            print("✅ Contrato válido! Nenhum problema encontrado.")
        elif not self.errors:
            print("✅ Contrato aprovado com avisos.")
        else:
            print("❌ Contrato rejeitado. Corrija os erros antes de prosseguir.")
        
        print(f"\n📈 RESUMO:")
        print(f"  • Erros: {len(self.errors)}")
        print(f"  • Avisos: {len(self.warnings)}")
        print(f"  • Status: {'❌ REJEITADO' if self.errors else '✅ APROVADO'}")
        
        return len(self.errors) == 0

def main():
    if len(sys.argv) != 2:
        print("Uso: python verify_contract.py <caminho_para_openapi.yaml>")
        sys.exit(1)
    
    spec_path = sys.argv[1]
    verifier = APIContractVerifier(spec_path)
    
    success = verifier.run_verification()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()