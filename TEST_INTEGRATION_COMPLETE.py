#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste Completo da Integração MEEP
Com dados simulados do servidor mock
"""

import sys
import io
# Forçar UTF-8 no Windows
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

import httpx
import json
from datetime import datetime

def test_integration():
    """Testar integração completa"""
    print("\n" + "="*60)
    print("    TESTE COMPLETO DA INTEGRAÇÃO MEEP")
    print("="*60)
    
    base_url = "http://localhost:8000/api/meep"
    
    tests = []
    
    # 1. Health Check
    print("\n[1] Health Check...")
    try:
        response = httpx.get(f"{base_url}/health")
        data = response.json()
        print(f"   Status: {data['status']}")
        print(f"   MEEP API: {data['meep_api']}")
        print(f"   Database: {data['database']}")
        tests.append(("Health Check", response.status_code == 200))
    except Exception as e:
        print(f"   ERRO: {e}")
        tests.append(("Health Check", False))
    
    # 2. Status da Integração
    print("\n[2] Status da Integração...")
    try:
        response = httpx.get(f"{base_url}/status")
        data = response.json()
        print(f"   Conectado: {data.get('connected', False)}")
        print(f"   Última sync: {data.get('last_sync', 'Nunca')}")
        tests.append(("Status", response.status_code == 200))
    except Exception as e:
        print(f"   ERRO: {e}")
        tests.append(("Status", False))
    
    # 3. Listar Eventos (sem auth por enquanto)
    print("\n[3] Listar Eventos...")
    try:
        response = httpx.get(f"{base_url}/events")
        if response.status_code == 200:
            events = response.json()
            print(f"   Eventos encontrados: {len(events)}")
            for event in events[:3]:
                print(f"   - {event.get('name', 'Sem nome')}")
            tests.append(("Listar Eventos", True))
        else:
            print(f"   Status: {response.status_code}")
            print(f"   Erro: {response.text}")
            tests.append(("Listar Eventos", False))
    except Exception as e:
        print(f"   ERRO: {e}")
        tests.append(("Listar Eventos", False))
    
    # 4. Estatísticas
    print("\n[4] Estatísticas...")
    try:
        response = httpx.get(f"{base_url}/stats")
        if response.status_code == 200:
            stats = response.json()
            print(f"   Total de Eventos: {stats.get('total_events', 0)}")
            print(f"   Total de Participantes: {stats.get('total_attendees', 0)}")
            print(f"   Total de Check-ins: {stats.get('total_checkins', 0)}")
            print(f"   Receita Total: R$ {stats.get('total_revenue', 0):,.2f}")
            tests.append(("Estatísticas", True))
        else:
            print(f"   Status: {response.status_code}")
            tests.append(("Estatísticas", False))
    except Exception as e:
        print(f"   ERRO: {e}")
        tests.append(("Estatísticas", False))
    
    # 5. Dashboard Analytics
    print("\n[5] Dashboard Analytics...")
    try:
        response = httpx.get(f"{base_url}/analytics/dashboard")
        if response.status_code == 200:
            dashboard = response.json()
            metrics = dashboard.get('metrics', {})
            print(f"   Eventos Ativos: {metrics.get('active_events', 0)}")
            print(f"   Taxa de Ocupação: {metrics.get('average_occupancy', 0):.1f}%")
            print(f"   Taxa de Check-in: {metrics.get('average_checkin_rate', 0):.1f}%")
            tests.append(("Dashboard", True))
        else:
            print(f"   Status: {response.status_code}")
            tests.append(("Dashboard", False))
    except Exception as e:
        print(f"   ERRO: {e}")
        tests.append(("Dashboard", False))
    
    # 6. Auto Sync Status
    print("\n[6] Status da Sincronização Automática...")
    try:
        response = httpx.get(f"{base_url}/sync/auto/status")
        if response.status_code == 200:
            sync_status = response.json()
            print(f"   Rodando: {sync_status.get('running', False)}")
            print(f"   Intervalo: {sync_status.get('interval', 0)}s")
            print(f"   Última sync: {sync_status.get('last_sync', 'Nunca')}")
            tests.append(("Auto Sync", True))
        else:
            print(f"   Status: {response.status_code}")
            tests.append(("Auto Sync", False))
    except Exception as e:
        print(f"   ERRO: {e}")
        tests.append(("Auto Sync", False))
    
    # Resumo
    print("\n" + "="*60)
    print("    RESUMO DOS TESTES")
    print("="*60)
    
    passed = sum(1 for _, result in tests if result)
    total = len(tests)
    
    for test_name, result in tests:
        status = "✓ PASSOU" if result else "✗ FALHOU"
        print(f"   {test_name}: {status}")
    
    print(f"\n   Total: {passed}/{total} testes passaram")
    
    if passed == total:
        print("\n 🎉 INTEGRAÇÃO FUNCIONANDO PERFEITAMENTE!")
    elif passed > total / 2:
        print("\n ⚠️ INTEGRAÇÃO PARCIALMENTE FUNCIONAL")
    else:
        print("\n ❌ INTEGRAÇÃO COM PROBLEMAS")
    
    print("\n" + "="*60)
    
    return passed == total

if __name__ == "__main__":
    success = test_integration()
    sys.exit(0 if success else 1)