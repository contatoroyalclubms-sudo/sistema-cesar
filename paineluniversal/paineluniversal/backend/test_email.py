#!/usr/bin/env python3
"""
Script para testar o envio de email
"""
import asyncio
import sys
import os

# Adicionar o diretório atual ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.email_service import email_service

async def test_email():
    """Testar o serviço de email"""
    print("🧪 Testando serviço de email...")
    
    # Teste 1: Código de verificação
    print("\n📧 Teste 1: Enviando código de verificação...")
    result1 = await email_service.send_verification_code(
        to_email="teste@example.com",
        to_name="Usuário Teste",
        verification_code="123456"
    )
    print(f"Resultado: {'✅ Sucesso' if result1 else '❌ Falhou'}")
    
    # Teste 2: Email de boas-vindas
    print("\n🎉 Teste 2: Enviando email de boas-vindas...")
    result2 = await email_service.send_welcome_email(
        to_email="teste@example.com",
        to_name="Usuário Teste"
    )
    print(f"Resultado: {'✅ Sucesso' if result2 else '❌ Falhou'}")
    
    print("\n✨ Testes concluídos!")

if __name__ == "__main__":
    asyncio.run(test_email())
