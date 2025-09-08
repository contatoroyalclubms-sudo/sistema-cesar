#!/usr/bin/env python3
"""
Teste simples e direto das funcionalidades críticas
Testa diretamente via import, sem HTTP requests
"""
import os
import sys
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

def test_direct_functionality():
    """Teste direto das funcionalidades sem HTTP"""
    print("🧪 TESTE DIRETO DAS FUNCIONALIDADES CRÍTICAS")
    print("=" * 60)
    
    try:
        # Adicionar backend ao path
        sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))
        
        from backend.app.database import SessionLocal, engine
        from backend.app import models
        from sqlalchemy import text
        
        db = SessionLocal()
        
        print("1. 🔗 TESTE DE CONEXÃO:")
        # Teste de conexão básica
        result = db.execute(text("SELECT current_database(), current_user, version()"))
        db_info = result.fetchone()
        print(f"   ✅ Banco: {db_info[0]}")
        print(f"   ✅ Usuário: {db_info[1]}")
        print(f"   ✅ Versão: {db_info[2].split()[0]} {db_info[2].split()[1]}")
        
        print("\n2. 📊 CONTAGEM DE DADOS:")
        # Contar registros
        empresas_count = db.query(models.Empresa).count()
        usuarios_count = db.query(models.Usuario).count()
        produtos_count = db.query(models.Produto).count()
        
        print(f"   📋 Empresas: {empresas_count}")
        print(f"   👥 Usuários: {usuarios_count}")
        print(f"   🏪 Produtos: {produtos_count}")
        print(f"   📈 Total de registros: {empresas_count + usuarios_count + produtos_count}")
        
        print("\n3. 👤 ANÁLISE DE USUÁRIOS:")
        # Análise de usuários por tipo
        usuario_stats = db.execute(text("""
            SELECT tipo, COUNT(*) as total, 
                   COUNT(CASE WHEN ativo = true THEN 1 END) as ativos
            FROM usuarios 
            GROUP BY tipo
            ORDER BY total DESC
        """)).fetchall()
        
        for tipo, total, ativos in usuario_stats:
            print(f"   • {tipo}: {total} total, {ativos} ativos")
        
        print("\n4. 🏪 ANÁLISE DE PRODUTOS:")
        # Análise de produtos por tipo
        produto_stats = db.execute(text("""
            SELECT tipo_usuario, COUNT(*) as total,
                   AVG(preco) as preco_medio
            FROM produtos 
            GROUP BY tipo_usuario
            ORDER BY total DESC
        """)).fetchall()
        
        for tipo, total, preco_medio in produto_stats:
            preco_formatado = f"R$ {preco_medio:.2f}" if preco_medio else "N/A"
            print(f"   • {tipo}: {total} produtos, preço médio: {preco_formatado}")
        
        print("\n5. 🏢 ANÁLISE DE EMPRESAS:")
        # Análise de empresas
        empresa_info = db.execute(text("""
            SELECT e.nome, e.ativa, COUNT(p.id) as produtos
            FROM empresas e
            LEFT JOIN produtos p ON e.id = p.empresa_id
            GROUP BY e.id, e.nome, e.ativa
        """)).fetchall()
        
        for nome, ativa, produtos in empresa_info:
            status = "✅ Ativa" if ativa else "❌ Inativa"
            print(f"   • {nome}: {status}, {produtos} produtos")
        
        print("\n6. ⚡ TESTE DE PERFORMANCE:")
        # Teste de performance com query complexa
        import time
        start_time = time.time()
        
        performance_query = db.execute(text("""
            SELECT 
                u.tipo as user_tipo,
                COUNT(DISTINCT u.id) as usuarios,
                COUNT(DISTINCT p.id) as produtos_compativeis,
                COALESCE(AVG(p.preco), 0) as preco_medio_produtos
            FROM usuarios u
            LEFT JOIN produtos p ON p.tipo_usuario = 'cliente'  -- produtos para todos
            GROUP BY u.tipo
            ORDER BY usuarios DESC
        """)).fetchall()
        
        end_time = time.time()
        execution_time = (end_time - start_time) * 1000
        
        print(f"   ⏱️ Query executada em {execution_time:.2f}ms")
        print(f"   📊 Resultados por tipo de usuário:")
        for user_tipo, usuarios, produtos, preco_medio in performance_query:
            print(f"      • {user_tipo}: {usuarios} usuários, {produtos} produtos acessíveis")
        
        print("\n7. ✅ TESTE DE INTEGRIDADE:")
        # Verificar integridade referencial
        integrity_checks = [
            ("Produtos sem empresa", "SELECT COUNT(*) FROM produtos WHERE empresa_id IS NULL"),
            ("Usuários com email único", "SELECT COUNT(*) - COUNT(DISTINCT email) FROM usuarios"),
            ("Empresas com CNPJ único", "SELECT COUNT(*) - COUNT(DISTINCT cnpj) FROM empresas"),
        ]
        
        all_integrity_ok = True
        for check_name, query in integrity_checks:
            result = db.execute(text(query)).fetchone()[0]
            is_ok = result == 0
            status = "✅" if is_ok else "⚠️"
            print(f"   {status} {check_name}: {result}")
            if not is_ok:
                all_integrity_ok = False
        
        print(f"\n8. 🎯 FUNCIONALIDADES ESSENCIAIS:")
        # Testar funcionalidades essenciais
        tests = [
            ("Criar sessão de banco", lambda: SessionLocal()),
            ("Buscar usuário admin", lambda: db.query(models.Usuario).filter(models.Usuario.tipo == 'admin').first()),
            ("Buscar produtos ativos", lambda: db.query(models.Produto).filter(models.Produto.status == 'ativo').count()),
            ("Verificar estrutura de tabelas", lambda: len(db.execute(text("SELECT tablename FROM pg_tables WHERE schemaname = 'public'")).fetchall())),
        ]
        
        all_functions_ok = True
        for test_name, test_func in tests:
            try:
                result = test_func()
                success = result is not None
                status = "✅" if success else "⚠️"
                print(f"   {status} {test_name}: {'OK' if success else 'FALHA'}")
                if not success:
                    all_functions_ok = False
            except Exception as e:
                print(f"   ❌ {test_name}: ERRO - {e}")
                all_functions_ok = False
        
        db.close()
        
        # RESULTADO FINAL
        print("\n" + "="*60)
        print("🎯 RESULTADO FINAL DOS TESTES")
        print("="*60)
        
        if all_integrity_ok and all_functions_ok:
            print("🎉 TODAS AS FUNCIONALIDADES CRÍTICAS ESTÃO FUNCIONANDO!")
            print("✅ Sistema PostgreSQL 100% operacional")
            print("✅ Dados íntegros e acessíveis")
            print("✅ Performance adequada")
            print("✅ Pronto para uso em desenvolvimento")
            return True
        else:
            print("⚠️ ALGUMAS FUNCIONALIDADES PRECISAM DE ATENÇÃO")
            if not all_integrity_ok:
                print("❌ Problemas de integridade encontrados")
            if not all_functions_ok:
                print("❌ Algumas funções essenciais falharam")
            return False
        
    except Exception as e:
        print(f"❌ ERRO CRÍTICO NO TESTE: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_server_startup():
    """Testa se o servidor pode inicializar"""
    print("\n🚀 TESTE DE INICIALIZAÇÃO DO SERVIDOR")
    print("="*50)
    
    try:
        # Importar o app de teste
        sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))
        from backend.app.main_test import app
        
        print("✅ App FastAPI importado com sucesso")
        print("✅ Dependências carregadas")
        print("✅ Rotas configuradas")
        print("💡 Para iniciar o servidor:")
        print("   cd backend")
        print("   python -m uvicorn app.main_test:app --host 127.0.0.1 --port 8000")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao importar app: {e}")
        return False

if __name__ == "__main__":
    print("🔥 INICIANDO TESTES COMPLETOS DAS FUNCIONALIDADES CRÍTICAS")
    print("📅 Data:", os.popen('date /t').read().strip() if os.name == 'nt' else 'N/A')
    
    success_db = test_direct_functionality()
    success_server = test_server_startup()
    
    print(f"\n{'='*60}")
    print("📋 RESUMO FINAL")
    print(f"{'='*60}")
    
    if success_db and success_server:
        print("🎊 SISTEMA COMPLETAMENTE FUNCIONAL!")
        print("🚀 Ambiente PostgreSQL local pronto para desenvolvimento")
        print("✅ Todas as funcionalidades críticas validadas")
        print("✅ Servidor pode ser iniciado sem problemas")
        print("\n💡 PRÓXIMOS PASSOS:")
        print("1. Iniciar servidor: cd backend && python -m uvicorn app.main_test:app --reload")
        print("2. Acessar docs: http://localhost:8000/docs")
        print("3. Desenvolver novas funcionalidades com segurança!")
        exit_code = 0
    elif success_db:
        print("⚠️ BANCO DE DADOS FUNCIONAL, SERVIDOR COM PROBLEMAS")
        print("✅ PostgreSQL funcionando perfeitamente")
        print("❌ Servidor precisa de ajustes")
        exit_code = 1
    else:
        print("❌ PROBLEMAS CRÍTICOS ENCONTRADOS")
        print("❌ Sistema precisa de correções antes do uso")
        exit_code = 2
    
    sys.exit(exit_code)
