#!/usr/bin/env python3
"""
🔄 SCRIPT DE MIGRAÇÃO AUTOMÁTICA
Gerado em: 2025-08-27T00:59:28.730912

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
    
    print(f"✅ Backup criado em: {backup_dir}")
    return backup_dir

def apply_typescript_fixes():
    """Aplica correções nos tipos TypeScript"""
    frontend_types_dir = Path("../frontend/src/types")
    frontend_types_dir.mkdir(exist_ok=True)
    
    # Criar arquivo de tipos corretos
    types_content = '''// 🤖 GERADO AUTOMATICAMENTE - NÃO EDITAR MANUALMENTE
// Interfaces TypeScript sincronizadas com os modelos do backend
// Gerado em: 2025-08-27T00:59:28.735127

export type UserRole = 'admin' | 'promoter' | 'cliente' | 'operador';
export type StatusEvento = 'ATIVO' | 'INATIVO' | 'CANCELADO' | 'FINALIZADO';
export type TipoLista = 'VIP' | 'PREMIUM' | 'COMUM' | 'PROMOTER' | 'FREE';
export type StatusTransacao = 'PENDENTE' | 'APROVADA' | 'CANCELADA' | 'ESTORNADA';
export type TipoProduto = 'BEBIDA' | 'COMIDA' | 'INGRESSO' | 'FICHA' | 'COMBO' | 'VOUCHER';


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
    print(f"📁 Backup disponível em: {backup_dir}")

if __name__ == "__main__":
    main()
