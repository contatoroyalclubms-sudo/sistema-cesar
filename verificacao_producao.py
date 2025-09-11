#!/usr/bin/env python3
"""
🔍 VERIFICAÇÃO PÓS-DEPLOY - Sistema V7
Script para testar sistema em produção após deploy
"""

import asyncio
import aiohttp
import json
from datetime import datetime

class VerificacaoProducao:
    def __init__(self, railway_url: str, vercel_url: str):
        self.railway_url = railway_url.rstrip('/')
        self.vercel_url = vercel_url.rstrip('/')
        self.resultados = []
    
    def log_resultado(self, teste: str, status: bool, detalhes: str = ""):
        timestamp = datetime.now().strftime("%H:%M:%S")
        status_icon = "✅" if status else "❌"
        
        resultado = {
            "teste": teste,
            "status": status,
            "detalhes": detalhes,
            "timestamp": timestamp
        }
        
        self.resultados.append(resultado)
        print(f"{status_icon} [{timestamp}] {teste}: {detalhes}")
        return status
    
    async def test_railway_health(self):
        """Testar health do backend Railway"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.railway_url}/api/health", timeout=30) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self.log_resultado("Railway Health", True, f"Backend online: {data}")
                    else:
                        return self.log_resultado("Railway Health", False, f"Status: {response.status}")
        except Exception as e:
            return self.log_resultado("Railway Health", False, f"Erro: {e}")
    
    async def test_railway_login(self):
        """Testar login Railway"""
        try:
            login_data = {"cpf": "00000000000", "senha": "0000"}
            async with aiohttp.ClientSession() as session:
                async with session.post(f"{self.railway_url}/api/auth/login", 
                                      json=login_data, timeout=30) as response:
                    if response.status == 200:
                        return self.log_resultado("Railway Login", True, "Login funcional")
                    else:
                        return self.log_resultado("Railway Login", False, f"Status: {response.status}")
        except Exception as e:
            return self.log_resultado("Railway Login", False, f"Erro: {e}")
    
    async def test_vercel_frontend(self):
        """Testar frontend Vercel"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.vercel_url, timeout=30) as response:
                    if response.status == 200:
                        content = await response.text()
                        has_react = "react" in content.lower() or "vite" in content.lower()
                        return self.log_resultado("Vercel Frontend", True, f"Site carregado (React: {has_react})")
                    else:
                        return self.log_resultado("Vercel Frontend", False, f"Status: {response.status}")
        except Exception as e:
            return self.log_resultado("Vercel Frontend", False, f"Erro: {e}")
    
    async def test_integration(self):
        """Testar integração backend-frontend"""
        try:
            # Simular requisição do frontend para backend
            headers = {"Origin": self.vercel_url}
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.railway_url}/api/health", 
                                     headers=headers, timeout=30) as response:
                    if response.status == 200:
                        return self.log_resultado("Integração CORS", True, "Frontend pode acessar backend")
                    else:
                        return self.log_resultado("Integração CORS", False, f"Status: {response.status}")
        except Exception as e:
            return self.log_resultado("Integração CORS", False, f"Erro: {e}")
    
    def gerar_relatorio_final(self):
        """Gerar relatório final da verificação"""
        total = len(self.resultados)
        sucessos = sum(1 for r in self.resultados if r["status"])
        taxa = (sucessos / total * 100) if total > 0 else 0
        
        status_geral = "🎯 DEPLOY SUCESSO!" if taxa >= 75 else "⚠️ REQUER ATENÇÃO"
        
        relatorio = f"""
🔍 RELATÓRIO DE VERIFICAÇÃO PÓS-DEPLOY
=====================================

📊 RESUMO:
URLs Testadas:
- Railway Backend: {self.railway_url}
- Vercel Frontend: {self.vercel_url}

Resultados: {sucessos}/{total} sucessos ({taxa:.1f}%)
Status: {status_geral}

📋 DETALHES DOS TESTES:
"""
        
        for resultado in self.resultados:
            status_icon = "✅" if resultado["status"] else "❌"
            relatorio += f"{status_icon} [{resultado['timestamp']}] {resultado['teste']}: {resultado['detalhes']}\n"
        
        relatorio += f"""
🎯 CONCLUSÃO:
{status_geral}

Se taxa < 75%: Verificar logs do Railway/Vercel e configurações.
Se taxa >= 75%: Sistema funcionando em produção!

Verificado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        print(relatorio)
        return relatorio, taxa
    
    async def executar_verificacao(self):
        """Executar verificação completa"""
        print("🔍 INICIANDO VERIFICAÇÃO PÓS-DEPLOY")
        print("=" * 40)
        
        await self.test_railway_health()
        await self.test_railway_login()
        await self.test_vercel_frontend()
        await self.test_integration()
        
        relatorio, taxa = self.gerar_relatorio_final()
        return taxa >= 75

# Exemplo de uso:
# python verificacao_producao.py
# Substitua pelas URLs reais após deploy

if __name__ == "__main__":
    print("🔍 VERIFICAÇÃO PÓS-DEPLOY SISTEMA V7")
    print("=====================================")
    print()
    print("Para usar este script:")
    print("1. Faça deploy no Railway e Vercel")
    print("2. Obtenha as URLs de produção")
    print("3. Execute: python verificacao_producao.py")
    print()
    print("Exemplo:")
    print('railway_url = "https://sistema-production.up.railway.app"')
    print('vercel_url = "https://sistema-v7.vercel.app"')
    print()
    print("verificacao = VerificacaoProducao(railway_url, vercel_url)")
    print("asyncio.run(verificacao.executar_verificacao())")