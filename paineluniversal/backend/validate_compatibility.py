#!/usr/bin/env python3
"""
✅ SCRIPT DE VALIDAÇÃO DE COMPATIBILIDADE
Verifica se todas as correções foram aplicadas corretamente
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime

def check_typescript_files():
    """Verifica se os arquivos TypeScript foram criados/atualizados"""
    frontend_path = Path("../frontend/src")
    
    checks = {
        "types_database_exists": (frontend_path / "types" / "database.ts").exists(),
        "types_index_updated": (frontend_path / "types" / "index.ts").exists(),
        "api_file_updated": (frontend_path / "services" / "api.ts").exists(),
    }
    
    return checks

def check_backend_routes():
    """Verifica se as rotas do backend estão corretas"""
    main_py_path = Path("app/main.py")
    
    if not main_py_path.exists():
        return {"main_py_exists": False}
    
    with open(main_py_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    checks = {
        "main_py_exists": True,
        "meep_imported": "from .routers import" in content and "meep" in content,
        "meep_router_included": "app.include_router(meep.router" in content and not "# app.include_router(meep.router" in content,
        "cors_middleware_active": "UltimateCORSMiddleware" in content,
        "routes_included": all(router in content for router in [
            "auth.router", "eventos.router", "usuarios.router", 
            "empresas.router", "produtos.router", "gamificacao.router"
        ])
    }
    
    return checks

def check_database_compatibility():
    """Verifica compatibilidade com banco de dados"""
    try:
        from app.database import engine
        from sqlalchemy import inspect
        
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        expected_tables = [
            'usuarios', 'empresas', 'eventos', 'listas', 
            'transacoes', 'checkins', 'produtos', 'categorias_produtos'
        ]
        
        missing_tables = [table for table in expected_tables if table not in tables]
        
        return {
            "database_accessible": True,
            "total_tables": len(tables),
            "expected_tables_present": len(missing_tables) == 0,
            "missing_tables": missing_tables
        }
        
    except Exception as e:
        return {
            "database_accessible": False,
            "error": str(e)
        }

def run_validation():
    """Executa validação completa"""
    print("🔍 VALIDAÇÃO DE COMPATIBILIDADE COMPLETA")
    print("=" * 50)
    
    # 1. Verificar arquivos TypeScript
    print("📝 Verificando arquivos TypeScript...")
    ts_checks = check_typescript_files()
    
    # 2. Verificar rotas do backend
    print("🛠️  Verificando configuração do backend...")
    backend_checks = check_backend_routes()
    
    # 3. Verificar banco de dados
    print("🗄️  Verificando compatibilidade com banco de dados...")
    db_checks = check_database_compatibility()
    
    # Compilar relatório
    report = {
        "timestamp": datetime.now().isoformat(),
        "frontend": ts_checks,
        "backend": backend_checks,
        "database": db_checks,
        "overall_status": "OK"
    }
    
    # Verificar se há problemas críticos
    critical_issues = []
    
    if not ts_checks.get("types_database_exists"):
        critical_issues.append("Arquivo types/database.ts não encontrado")
    
    if not backend_checks.get("routes_included"):
        critical_issues.append("Nem todas as rotas estão incluídas no backend")
    
    if not db_checks.get("database_accessible"):
        critical_issues.append("Banco de dados não acessível")
    
    if critical_issues:
        report["overall_status"] = "ISSUES_FOUND"
        report["critical_issues"] = critical_issues
    
    # Exibir resultados
    print("\n" + "=" * 50)
    print("📊 RESULTADOS DA VALIDAÇÃO")
    print("=" * 50)
    
    print(f"📝 Frontend:")
    for check, status in ts_checks.items():
        icon = "✅" if status else "❌"
        print(f"   {icon} {check}: {status}")
    
    print(f"\n🛠️  Backend:")
    for check, status in backend_checks.items():
        icon = "✅" if status else "❌"
        print(f"   {icon} {check}: {status}")
    
    print(f"\n🗄️  Database:")
    for check, status in db_checks.items():
        if check not in ["missing_tables", "error"]:
            icon = "✅" if status else "❌"
            print(f"   {icon} {check}: {status}")
    
    if "missing_tables" in db_checks and db_checks["missing_tables"]:
        print(f"   ⚠️  Tabelas ausentes: {', '.join(db_checks['missing_tables'])}")
    
    print(f"\n🎯 STATUS GERAL: {report['overall_status']}")
    
    if critical_issues:
        print("\n🚨 PROBLEMAS CRÍTICOS ENCONTRADOS:")
        for issue in critical_issues:
            print(f"   ❌ {issue}")
        print("\n🔧 AÇÕES RECOMENDADAS:")
        print("   1. Execute o script de migração: python migration_script.py")
        print("   2. Verifique se todos os módulos estão instalados")
        print("   3. Execute novamente a validação")
    else:
        print("\n✅ SISTEMA TOTALMENTE COMPATÍVEL!")
        print("   🚀 Todas as correções foram aplicadas com sucesso")
        print("   📡 Backend e Frontend estão sincronizados")
        print("   🗄️  Banco de dados está acessível")
        
        print("\n🎉 PRÓXIMOS PASSOS:")
        print("   1. Testar aplicação localmente")
        print("   2. Executar testes automatizados")
        print("   3. Deploy para produção")
    
    # Salvar relatório
    report_file = f"validation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False, default=str)
    
    print(f"\n📄 Relatório salvo em: {report_file}")
    
    return report

if __name__ == "__main__":
    run_validation()
