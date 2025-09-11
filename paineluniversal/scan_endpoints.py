#!/usr/bin/env python3
"""
🔍 SCANNER DE ENDPOINTS - Mapeamento completo da API
Analisa todos os routers e identifica endpoints exatos disponíveis
"""
import os
import sys
import json
import re
import traceback
from datetime import datetime
from typing import Dict, List, Any

def scan_router_file(file_path: str) -> Dict[str, Any]:
    """Escanear um arquivo de router para extrair informações"""
    router_info = {
        "file": file_path,
        "prefix": None,
        "tags": [],
        "endpoints": [],
        "errors": []
    }
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Extrair prefix do router
        prefix_match = re.search(r'router\s*=\s*APIRouter\([^)]*prefix=["\'](.*?)["\']', content)
        if prefix_match:
            router_info["prefix"] = prefix_match.group(1)
            
        # Extrair tags
        tags_match = re.search(r'router\s*=\s*APIRouter\([^)]*tags=\[(.*?)\]', content)
        if tags_match:
            tags_str = tags_match.group(1)
            # Extrair strings entre aspas
            tag_matches = re.findall(r'["\'](.*?)["\']', tags_str)
            router_info["tags"] = tag_matches
            
        # Encontrar todos os endpoints
        endpoint_patterns = [
            r'@router\.(get|post|put|delete|patch)\(["\'](.*?)["\']',
            r'@router\.(get|post|put|delete|patch)\(\s*["\'](.*?)["\']'
        ]
        
        for pattern in endpoint_patterns:
            matches = re.findall(pattern, content)
            for method, path in matches:
                router_info["endpoints"].append({
                    "method": method.upper(),
                    "path": path,
                    "full_path": f"{router_info['prefix'] or ''}{path}"
                })
        
    except Exception as e:
        router_info["errors"].append(str(e))
        
    return router_info

def scan_main_py_includes(main_file: str) -> Dict[str, Any]:
    """Escanear main.py para ver como os routers são incluídos"""
    includes = []
    
    try:
        with open(main_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Procurar por app.include_router
        include_pattern = r'app\.include_router\(([^)]+)\)'
        matches = re.findall(include_pattern, content)
        
        for match in matches:
            # Extrair informações do include_router
            router_match = re.search(r'(\w+)\.router', match)
            prefix_match = re.search(r'prefix=["\'](.*?)["\']', match)
            tags_match = re.search(r'tags=\[(.*?)\]', match)
            
            include_info = {
                "router_name": router_match.group(1) if router_match else "unknown",
                "prefix": prefix_match.group(1) if prefix_match else None,
                "tags": [],
                "raw": match.strip()
            }
            
            if tags_match:
                tags_str = tags_match.group(1)
                tag_matches = re.findall(r'["\'](.*?)["\']', tags_str)
                include_info["tags"] = tag_matches
                
            includes.append(include_info)
            
    except Exception as e:
        return {"error": str(e)}
        
    return {"includes": includes}

def generate_endpoint_map():
    """Gerar mapeamento completo de endpoints"""
    print("🔍 ESCANEANDO ESTRUTURA COMPLETA DE ENDPOINTS")
    print("=" * 60)
    
    # Escanear routers
    routers_dir = "backend/app/routers"
    router_files = []
    
    if os.path.exists(routers_dir):
        for file in os.listdir(routers_dir):
            if file.endswith('.py') and file != '__init__.py':
                router_files.append(os.path.join(routers_dir, file))
    
    router_data = {}
    for router_file in router_files:
        router_name = os.path.basename(router_file).replace('.py', '')
        router_data[router_name] = scan_router_file(router_file)
        print(f"📄 Escaneado: {router_name}")
    
    # Escanear main.py
    main_file = "backend/app/main.py"
    main_data = {}
    if os.path.exists(main_file):
        main_data = scan_main_py_includes(main_file)
        print(f"📄 Escaneado: main.py")
    
    # Combinar informações
    endpoint_map = {
        "timestamp": datetime.now().isoformat(),
        "routers": router_data,
        "main_includes": main_data,
        "endpoint_summary": []
    }
    
    # Gerar resumo de endpoints
    if "includes" in main_data:
        for include in main_data["includes"]:
            router_name = include["router_name"]
            main_prefix = include["prefix"] or ""
            
            if router_name in router_data:
                router_info = router_data[router_name]
                router_prefix = router_info["prefix"] or ""
                
                for endpoint in router_info["endpoints"]:
                    full_endpoint = {
                        "router": router_name,
                        "method": endpoint["method"],
                        "router_path": endpoint["path"],
                        "router_prefix": router_prefix,
                        "main_prefix": main_prefix,
                        "full_url": f"{main_prefix}{router_prefix}{endpoint['path']}",
                        "tags": include["tags"]
                    }
                    endpoint_map["endpoint_summary"].append(full_endpoint)
    
    # Salvar resultado
    report_file = f"endpoint_map_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(endpoint_map, f, indent=2, ensure_ascii=False)
    
    print("=" * 60)
    print(f"✅ ESCANEAMENTO COMPLETO!")
    print(f"📊 {len(router_data)} routers escaneados")
    print(f"📊 {len(endpoint_map['endpoint_summary'])} endpoints mapeados")
    print(f"💾 Relatório salvo: {report_file}")
    
    # Mostrar resumo dos endpoints principais
    print("\n🎯 ENDPOINTS PRINCIPAIS IDENTIFICADOS:")
    print("-" * 40)
    
    method_groups = {}
    for endpoint in endpoint_map["endpoint_summary"]:
        method = endpoint["method"]
        if method not in method_groups:
            method_groups[method] = []
        method_groups[method].append(endpoint["full_url"])
    
    for method in ["GET", "POST", "PUT", "DELETE"]:
        if method in method_groups:
            print(f"\n{method} ENDPOINTS:")
            for url in sorted(set(method_groups[method])):
                print(f"  {url}")
    
    return endpoint_map

if __name__ == "__main__":
    endpoint_map = generate_endpoint_map()
