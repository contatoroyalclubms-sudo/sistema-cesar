#!/usr/bin/env python3
import psycopg2
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

def executar_migração():
    """Executa a migração para renomear tipo_usuario para tipo na tabela listas"""
    
    # Conectar ao PostgreSQL
    try:
        conn = psycopg2.connect(
            host="localhost",
            database="paineluniversal",
            user="painel_user",
            password="painel123"
        )
        
        cursor = conn.cursor()
        
        print("🔍 Verificando estrutura atual da tabela listas...")
        
        # Verificar se a coluna tipo_usuario existe
        cursor.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'listas' AND column_name IN ('tipo', 'tipo_usuario');
        """)
        
        colunas = cursor.fetchall()
        print(f"📊 Colunas encontradas: {colunas}")
        
        tem_tipo_usuario = any(col[0] == 'tipo_usuario' for col in colunas)
        tem_tipo = any(col[0] == 'tipo' for col in colunas)
        
        if tem_tipo_usuario and not tem_tipo:
            print("🔄 Renomeando coluna tipo_usuario para tipo...")
            cursor.execute('ALTER TABLE listas RENAME COLUMN tipo_usuario TO tipo;')
            conn.commit()
            print("✅ Coluna renomeada com sucesso!")
            
        elif tem_tipo and not tem_tipo_usuario:
            print("✅ Coluna 'tipo' já existe e está correta!")
            
        elif tem_tipo and tem_tipo_usuario:
            print("⚠️ Ambas as colunas existem. Removendo tipo_usuario...")
            cursor.execute('ALTER TABLE listas DROP COLUMN tipo_usuario;')
            conn.commit()
            print("✅ Coluna tipo_usuario removida!")
            
        else:
            print("❌ Nenhuma das colunas encontrada. Criando coluna 'tipo'...")
            cursor.execute("ALTER TABLE listas ADD COLUMN tipo VARCHAR(50) DEFAULT 'VIP';")
            conn.commit()
            print("✅ Coluna 'tipo' criada!")
        
        # Verificar resultado final
        cursor.execute("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_name = 'listas'
            ORDER BY ordinal_position;
        """)
        
        print("\n📋 Estrutura final da tabela listas:")
        for col in cursor.fetchall():
            print(f"  - {col[0]}: {col[1]} (nullable: {col[2]}, default: {col[3]})")
            
        cursor.close()
        conn.close()
        
        print("\n🎉 Migração PostgreSQL concluída com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro na migração: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("🚀 Iniciando migração PostgreSQL para coluna 'tipo' da tabela listas...")
    executar_migração()
