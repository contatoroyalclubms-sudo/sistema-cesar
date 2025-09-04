#!/usr/bin/env python3
"""
Otimização do banco de dados - Adicionar índices para melhorar performance
"""
import os
import sqlite3
from datetime import datetime

def add_performance_indexes():
    """Adicionar índices para melhorar performance das consultas"""
    print("🚀 OTIMIZAÇÃO: Adicionando índices de performance")
    print("=" * 60)
    
    # Conectar ao banco
    backend_dir = os.path.join(os.path.dirname(__file__), 'backend')
    db_path = os.path.join(backend_dir, 'eventos.db')
    
    if not os.path.exists(db_path):
        print(f"❌ Banco não encontrado: {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("📊 Verificando índices existentes...")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='index'")
        existing_indexes = [row[0] for row in cursor.fetchall()]
        print(f"Índices existentes: {len(existing_indexes)}")
        
        # Verificar estrutura da tabela usuarios primeiro
        print("📋 Verificando estrutura da tabela usuarios...")
        cursor.execute("PRAGMA table_info(usuarios)")
        usuarios_columns = [col[1] for col in cursor.fetchall()]
        print(f"Colunas da tabela usuarios: {usuarios_columns}")
        
        # Verificar estrutura da tabela produtos
        print("📋 Verificando estrutura da tabela produtos...")
        cursor.execute("PRAGMA table_info(produtos)")
        produtos_columns = [col[1] for col in cursor.fetchall()]
        print(f"Colunas da tabela produtos: {produtos_columns}")
        
        # Índices críticos para performance de usuários (baseado nas colunas existentes)
        indices_criticos = [
            ("idx_usuarios_cpf", "CREATE INDEX IF NOT EXISTS idx_usuarios_cpf ON usuarios (cpf)"),
            ("idx_usuarios_email", "CREATE INDEX IF NOT EXISTS idx_usuarios_email ON usuarios (email)"),
            ("idx_usuarios_tipo", "CREATE INDEX IF NOT EXISTS idx_usuarios_tipo ON usuarios (tipo)"),
            ("idx_usuarios_ativo", "CREATE INDEX IF NOT EXISTS idx_usuarios_ativo ON usuarios (ativo)"),
        ]
        
        # Adicionar índice empresa_id apenas se a coluna existir
        if 'empresa_id' in usuarios_columns:
            indices_criticos.append(("idx_usuarios_empresa_id", "CREATE INDEX IF NOT EXISTS idx_usuarios_empresa_id ON usuarios (empresa_id)"))
        
        # Índices para produtos (baseado nas colunas existentes)
        if 'categoria' in produtos_columns:
            indices_criticos.append(("idx_produtos_categoria", "CREATE INDEX IF NOT EXISTS idx_produtos_categoria ON produtos (categoria)"))
        if 'tipo' in produtos_columns:
            indices_criticos.append(("idx_produtos_tipo", "CREATE INDEX IF NOT EXISTS idx_produtos_tipo ON produtos (tipo)"))
        if 'status' in produtos_columns:
            indices_criticos.append(("idx_produtos_status", "CREATE INDEX IF NOT EXISTS idx_produtos_status ON produtos (status)"))
        if 'empresa_id' in produtos_columns:
            indices_criticos.append(("idx_produtos_empresa_id", "CREATE INDEX IF NOT EXISTS idx_produtos_empresa_id ON produtos (empresa_id)"))
        
        # Verificar se tabela empresas existe
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='empresas'")
        empresas_exists = cursor.fetchone() is not None
        
        if empresas_exists:
            print("📋 Tabela empresas encontrada, adicionando índices...")
            cursor.execute("PRAGMA table_info(empresas)")
            empresas_columns = [col[1] for col in cursor.fetchall()]
            
            if 'cnpj' in empresas_columns:
                indices_criticos.append(("idx_empresas_cnpj", "CREATE INDEX IF NOT EXISTS idx_empresas_cnpj ON empresas (cnpj)"))
            if 'ativa' in empresas_columns:
                indices_criticos.append(("idx_empresas_ativa", "CREATE INDEX IF NOT EXISTS idx_empresas_ativa ON empresas (ativa)"))
        else:
            print("⚠️ Tabela empresas não encontrada, pulando índices relacionados")
        
        indices_criados = 0
        
        for nome_indice, sql_indice in indices_criticos:
            if nome_indice not in existing_indexes:
                print(f"➕ Criando índice: {nome_indice}")
                cursor.execute(sql_indice)
                indices_criados += 1
            else:
                print(f"✅ Índice já existe: {nome_indice}")
        
        conn.commit()
        
        print(f"\n📊 Resumo da otimização:")
        print(f"✅ Índices criados: {indices_criados}")
        print(f"📈 Total de índices: {len(existing_indexes) + indices_criados}")
        
        # Testar performance da consulta crítica
        print(f"\n🧪 Testando performance das consultas...")
        
        start_time = datetime.now()
        cursor.execute("SELECT COUNT(*) FROM usuarios WHERE cpf = '00000000000'")
        count = cursor.fetchone()[0]
        duration = (datetime.now() - start_time).total_seconds()
        
        print(f"⚡ Consulta por CPF: {duration:.3f}s ({count} resultados)")
        
        start_time = datetime.now()
        cursor.execute("SELECT COUNT(*) FROM usuarios WHERE email = 'admin@paineluniversal.com'")
        count = cursor.fetchone()[0]
        duration = (datetime.now() - start_time).total_seconds()
        
        print(f"⚡ Consulta por email: {duration:.3f}s ({count} resultados)")
        
        conn.close()
        
        print("\n🎉 OTIMIZAÇÃO CONCLUÍDA!")
        print("✅ Consultas de CPF e email agora são mais rápidas")
        print("✅ Registro de usuários deve ser mais eficiente")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro na otimização: {e}")
        return False

if __name__ == "__main__":
    success = add_performance_indexes()
    exit(0 if success else 1)
