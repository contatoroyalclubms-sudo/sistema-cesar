#!/usr/bin/env python3
"""
🧪 FRAMEWORK DE TESTES COMPLETO - SISTEMA PAINEL UNIVERSAL
Sistema abrangente de testes para todas as funcionalidades
"""
import os
import sys
import json
import time
import traceback
from datetime import datetime
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()

class TestFramework:
    """Framework principal de testes"""
    
    def __init__(self):
        self.results = {
            "start_time": datetime.now().isoformat(),
            "tests": {},
            "summary": {
                "total": 0,
                "passed": 0,
                "failed": 0,
                "skipped": 0,
                "errors": []
            }
        }
        self.current_phase = None
        
    def log(self, message: str, level: str = "INFO"):
        """Log com timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] [{level}] {message}")
        
    def start_phase(self, phase_name: str, description: str):
        """Iniciar nova fase de testes"""
        self.current_phase = phase_name
        self.results["tests"][phase_name] = {
            "description": description,
            "start_time": datetime.now().isoformat(),
            "tests": [],
            "summary": {"passed": 0, "failed": 0, "skipped": 0}
        }
        self.log(f"🚀 INICIANDO FASE: {phase_name}", "PHASE")
        self.log(f"📋 {description}", "INFO")
        print("=" * 80)
        
    def run_test(self, test_name: str, test_function, *args, **kwargs):
        """Executar um teste individual"""
        if not self.current_phase:
            raise ValueError("Nenhuma fase ativa. Chame start_phase() primeiro")
            
        test_start = time.time()
        test_result = {
            "name": test_name,
            "start_time": datetime.now().isoformat(),
            "status": "unknown",
            "duration": 0,
            "message": "",
            "details": {},
            "error": None
        }
        
        try:
            self.log(f"🔍 Testando: {test_name}")
            
            # Executar o teste
            result = test_function(*args, **kwargs)
            
            test_duration = time.time() - test_start
            test_result["duration"] = round(test_duration, 3)
            
            if isinstance(result, dict):
                test_result["status"] = result.get("status", "passed")
                test_result["message"] = result.get("message", "")
                test_result["details"] = result.get("details", {})
            elif result is True:
                test_result["status"] = "passed"
                test_result["message"] = "Teste passou"
            elif result is False:
                test_result["status"] = "failed"
                test_result["message"] = "Teste falhou"
            else:
                test_result["status"] = "passed"
                test_result["message"] = str(result)
                
            # Log do resultado
            status_icon = "✅" if test_result["status"] == "passed" else "❌"
            self.log(f"   {status_icon} {test_result['message']} ({test_duration:.3f}s)")
            
            # Atualizar contadores
            self.results["tests"][self.current_phase]["summary"][test_result["status"]] += 1
            self.results["summary"][test_result["status"]] += 1
            
        except Exception as e:
            test_duration = time.time() - test_start
            test_result["duration"] = round(test_duration, 3)
            test_result["status"] = "failed"
            test_result["message"] = f"Erro durante execução: {str(e)}"
            test_result["error"] = traceback.format_exc()
            
            self.log(f"   ❌ ERRO: {str(e)}", "ERROR")
            
            # Atualizar contadores
            self.results["tests"][self.current_phase]["summary"]["failed"] += 1
            self.results["summary"]["failed"] += 1
            self.results["summary"]["errors"].append({
                "phase": self.current_phase,
                "test": test_name,
                "error": str(e),
                "traceback": test_result["error"]
            })
        
        # Adicionar resultado à fase atual
        self.results["tests"][self.current_phase]["tests"].append(test_result)
        self.results["summary"]["total"] += 1
        
        return test_result
        
    def end_phase(self):
        """Finalizar fase atual"""
        if not self.current_phase:
            return
            
        phase_data = self.results["tests"][self.current_phase]
        phase_data["end_time"] = datetime.now().isoformat()
        
        summary = phase_data["summary"]
        total = sum(summary.values())
        success_rate = (summary["passed"] / total * 100) if total > 0 else 0
        
        print("=" * 80)
        self.log(f"📊 FASE CONCLUÍDA: {self.current_phase}")
        self.log(f"   ✅ Passou: {summary['passed']}")
        self.log(f"   ❌ Falhou: {summary['failed']}")
        self.log(f"   ⏭️ Pulou: {summary['skipped']}")
        self.log(f"   📈 Taxa de sucesso: {success_rate:.1f}%")
        print()
        
        self.current_phase = None
        
    def generate_report(self, save_to_file: bool = True):
        """Gerar relatório final"""
        self.results["end_time"] = datetime.now().isoformat()
        
        total_tests = self.results["summary"]["total"]
        passed = self.results["summary"]["passed"]
        failed = self.results["summary"]["failed"]
        success_rate = (passed / total_tests * 100) if total_tests > 0 else 0
        
        print("\n" + "="*100)
        print("🎯 RELATÓRIO FINAL DE TESTES - SISTEMA PAINEL UNIVERSAL")
        print("="*100)
        print(f"📅 Período: {self.results['start_time']} → {self.results['end_time']}")
        print(f"🧪 Total de testes: {total_tests}")
        print(f"✅ Passou: {passed}")
        print(f"❌ Falhou: {failed}")
        print(f"⏭️ Pulou: {self.results['summary']['skipped']}")
        print(f"📈 Taxa de sucesso geral: {success_rate:.1f}%")
        
        # Relatório por fase
        print(f"\n📊 RESULTADO POR FASE:")
        print("-" * 100)
        
        for phase_name, phase_data in self.results["tests"].items():
            summary = phase_data["summary"]
            phase_total = sum(summary.values())
            phase_success = (summary["passed"] / phase_total * 100) if phase_total > 0 else 0
            
            status = "🟢" if phase_success >= 80 else "🟡" if phase_success >= 60 else "🔴"
            
            print(f"{status} {phase_name}: {phase_success:.1f}% ({summary['passed']}/{phase_total})")
            
        # Erros críticos
        if self.results["summary"]["errors"]:
            print(f"\n🚨 ERROS CRÍTICOS ENCONTRADOS:")
            print("-" * 100)
            for i, error in enumerate(self.results["summary"]["errors"], 1):
                print(f"{i}. [{error['phase']}] {error['test']}")
                print(f"   Erro: {error['error']}")
                
        # Salvar arquivo
        if save_to_file:
            filename = f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.results, f, indent=2, ensure_ascii=False)
            print(f"\n💾 Relatório salvo em: {filename}")
            
        # Veredito final
        print(f"\n🎯 VEREDITO FINAL:")
        if success_rate >= 90:
            print("🟢 SISTEMA EXCELENTE - Pronto para produção")
        elif success_rate >= 80:
            print("🟡 SISTEMA BOM - Poucos ajustes necessários")
        elif success_rate >= 60:
            print("🟠 SISTEMA ADEQUADO - Vários ajustes necessários")
        else:
            print("🔴 SISTEMA CRÍTICO - Muitos problemas encontrados")
            
        print("="*100)
        
        return self.results

# Funções de teste específicas
def test_database_connection():
    """Testar conexão com banco de dados"""
    try:
        sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))
        from backend.app.database import SessionLocal
        from sqlalchemy import text
        
        db = SessionLocal()
        result = db.execute(text("SELECT 1")).fetchone()
        db.close()
        
        return {
            "status": "passed",
            "message": "Conexão com banco estabelecida",
            "details": {"result": result[0] if result else None}
        }
    except Exception as e:
        return {
            "status": "failed",
            "message": f"Falha na conexão: {str(e)}"
        }

def test_fastapi_import():
    """Testar importação do FastAPI"""
    try:
        sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))
        from backend.app.main import app
        
        return {
            "status": "passed",
            "message": "FastAPI app importada com sucesso",
            "details": {"title": app.title, "version": app.version}
        }
    except Exception as e:
        return {
            "status": "failed",
            "message": f"Falha na importação: {str(e)}"
        }

def test_models_import():
    """Testar importação dos modelos"""
    try:
        sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))
        from backend.app import models
        
        # Contar modelos
        model_classes = [attr for attr in dir(models) if attr[0].isupper()]
        
        return {
            "status": "passed",
            "message": f"Modelos importados: {len(model_classes)} classes",
            "details": {"models": model_classes[:10]}  # Primeiros 10
        }
    except Exception as e:
        return {
            "status": "failed",
            "message": f"Falha na importação de modelos: {str(e)}"
        }

def main():
    """Função principal de execução"""
    print("🧪 INICIANDO FRAMEWORK DE TESTES COMPLETO")
    print("🎯 Sistema: Painel Universal")
    print("📅 Data:", datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
    print()
    
    # Criar framework
    framework = TestFramework()
    
    # FASE 1: TESTES DE INFRAESTRUTURA
    framework.start_phase(
        "infraestrutura", 
        "Testes básicos de infraestrutura e conectividade"
    )
    
    framework.run_test("Conexão Database", test_database_connection)
    framework.run_test("Importação FastAPI", test_fastapi_import)
    framework.run_test("Importação Modelos", test_models_import)
    
    framework.end_phase()
    
    # Gerar relatório
    framework.generate_report()

if __name__ == "__main__":
    main()
