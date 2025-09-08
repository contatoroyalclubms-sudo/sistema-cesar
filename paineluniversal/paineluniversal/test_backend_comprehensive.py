import requests
import json
import sys
from datetime import datetime

def test_backend_endpoints():
    """
    Testa sistematicamente todos os endpoints que estão falhando em produção
    """
    
    # URLs base para teste
    base_urls = [
        "https://backend-painel-universal-production.up.railway.app",
        "http://localhost:8000"
    ]
    
    # Endpoints que estão falhando baseado nos screenshots
    endpoints = [
        "/",
        "/health",
        "/api/auth/me",
        "/api/dashboard/resumo", 
        "/api/eventos",
        "/api/eventos/1",
        "/api/produtos",
        "/api/pdv"
    ]
    
    # Headers típicos do frontend
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Origin": "https://frontend-painel-universal-production.up.railway.app",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    print("🔍 Testando conectividade do backend...")
    print(f"⏰ Horário: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    results = {}
    
    for base_url in base_urls:
        print(f"\n🌐 Testando: {base_url}")
        results[base_url] = {}
        
        for endpoint in endpoints:
            url = f"{base_url}{endpoint}"
            
            try:
                print(f"   📡 GET {endpoint}... ", end="")
                response = requests.get(url, headers=headers, timeout=10)
                
                status = response.status_code
                results[base_url][endpoint] = {
                    "status": status,
                    "success": status < 400,
                    "response_size": len(response.content),
                    "content_type": response.headers.get("content-type", ""),
                    "error": None
                }
                
                if status == 200:
                    print(f"✅ {status} OK")
                elif status == 401:
                    print(f"🔐 {status} Unauthorized (esperado)")
                elif status == 404:
                    print(f"❓ {status} Not Found")
                elif status >= 500:
                    print(f"❌ {status} Server Error")
                    try:
                        error_detail = response.json()
                        results[base_url][endpoint]["error"] = error_detail
                        print(f"      Error: {error_detail}")
                    except:
                        error_text = response.text[:200]
                        results[base_url][endpoint]["error"] = error_text
                        print(f"      Error: {error_text}")
                else:
                    print(f"⚠️ {status}")
                    
            except requests.exceptions.ConnectionError:
                print("❌ Connection Error")
                results[base_url][endpoint] = {
                    "status": 0,
                    "success": False,
                    "error": "Connection Error"
                }
            except requests.exceptions.Timeout:
                print("⏱️ Timeout")
                results[base_url][endpoint] = {
                    "status": 0,
                    "success": False,
                    "error": "Timeout"
                }
            except Exception as e:
                print(f"❌ Error: {str(e)}")
                results[base_url][endpoint] = {
                    "status": 0,
                    "success": False,
                    "error": str(e)
                }
    
    # Resumo
    print("\n" + "=" * 80)
    print("📊 RESUMO DOS TESTES")
    print("=" * 80)
    
    for base_url, endpoints_result in results.items():
        print(f"\n🌐 {base_url}:")
        success_count = sum(1 for r in endpoints_result.values() if r["success"])
        total_count = len(endpoints_result)
        print(f"   ✅ {success_count}/{total_count} endpoints funcionando")
        
        # Mostrar problemas
        problems = [(endpoint, result) for endpoint, result in endpoints_result.items() if not result["success"]]
        if problems:
            print("   🚨 Problemas encontrados:")
            for endpoint, result in problems:
                status = result["status"]
                error = result.get("error", "")
                print(f"      • {endpoint}: {status} - {error}")
    
    # Diagnóstico
    print("\n" + "=" * 80)
    print("🔧 DIAGNÓSTICO E RECOMENDAÇÕES")
    print("=" * 80)
    
    # Verificar se produção está funcionando
    prod_url = "https://backend-painel-universal-production.up.railway.app"
    if prod_url in results:
        prod_results = results[prod_url]
        health_ok = prod_results.get("/health", {}).get("success", False)
        root_ok = prod_results.get("/", {}).get("success", False)
        
        if not health_ok and not root_ok:
            print("❌ PROBLEMA CRÍTICO: Backend em produção não responde")
            print("   💡 Recomendação: Verificar logs do Railway e restart do serviço")
        elif health_ok or root_ok:
            print("✅ Backend em produção está respondendo")
            
            # Verificar APIs específicas
            api_endpoints = [k for k in prod_results.keys() if k.startswith("/api")]
            failed_apis = [k for k in api_endpoints if not prod_results[k]["success"]]
            
            if failed_apis:
                print(f"⚠️ {len(failed_apis)} APIs falhando:")
                for api in failed_apis:
                    status = prod_results[api]["status"]
                    print(f"   • {api}: {status}")
                print("   💡 Recomendação: Verificar logs específicos destas APIs")
    
    return results

if __name__ == "__main__":
    results = test_backend_endpoints()
    
    # Salvar resultados para análise
    with open("backend_test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\n💾 Resultados salvos em: backend_test_results.json")
