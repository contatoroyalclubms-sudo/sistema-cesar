#!/usr/bin/env python3
import psycopg2
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

def corrigir_colunas_tipo():
    """Corrige todas as colunas tipo_usuario para tipo"""
    
    # Conectar ao PostgreSQL
    try:
        conn = psycopg2.connect(
            host="localhost",
            database="paineluniversal",
            user="painel_user",
            password="painel123"
        )
        
        cursor = conn.cursor()
        
        # Verificar todas as tabelas que podem ter colunas tipo_usuario
        tabelas_para_verificar = ['usuarios', 'listas', 'eventos']
        
        for tabela in tabelas_para_verificar:
            print(f"\n🔍 Verificando tabela {tabela}...")
            
            # Verificar se a tabela existe
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = %s
                );
            """, (tabela,))
            
            resultado = cursor.fetchone()
            if not resultado or not resultado[0]:
                print(f"⚠️ Tabela {tabela} não existe")
                continue
            
            # Verificar colunas tipo relacionadas
            cursor.execute("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = %s AND column_name LIKE '%tipo%';
            """, (tabela,))
            
            colunas = cursor.fetchall()
            print(f"📊 Colunas tipo encontradas em {tabela}: {colunas}")
            
            # Verificar especificamente tipo_usuario e tipo
            cursor.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = %s AND column_name IN ('tipo', 'tipo_usuario');
            """, (tabela,))
            
            colunas_especificas = [col[0] for col in cursor.fetchall()]
            
            tem_tipo_usuario = 'tipo_usuario' in colunas_especificas
            tem_tipo = 'tipo' in colunas_especificas
            
            if tem_tipo_usuario and not tem_tipo:
                print(f"🔄 Renomeando tipo_usuario para tipo na tabela {tabela}...")
                cursor.execute(f'ALTER TABLE {tabela} RENAME COLUMN tipo_usuario TO tipo;')
                conn.commit()
                print(f"✅ Coluna renomeada em {tabela}!")
                
            elif tem_tipo and not tem_tipo_usuario:
                print(f"✅ Tabela {tabela} já tem coluna 'tipo' correta!")
                
            elif tem_tipo and tem_tipo_usuario:
                print(f"⚠️ Tabela {tabela} tem ambas as colunas. Removendo tipo_usuario...")
                cursor.execute(f'ALTER TABLE {tabela} DROP COLUMN tipo_usuario;')
                conn.commit()
                print(f"✅ Coluna tipo_usuario removida de {tabela}!")
                
            else:
                print(f"ℹ️ Tabela {tabela} não tem colunas tipo relevantes")
        
        # Verificar estrutura final
        for tabela in tabelas_para_verificar:
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = %s
                );
            """, (tabela,))
            
            resultado = cursor.fetchone()
            if resultado and resultado[0]:
                cursor.execute("""
                    SELECT column_name, data_type, is_nullable, column_default
                    FROM information_schema.columns 
                    WHERE table_name = %s AND column_name LIKE '%tipo%'
                    ORDER BY ordinal_position;
                """, (tabela,))
                
                print(f"\n📋 Colunas tipo na tabela {tabela}:")
                for col in cursor.fetchall():
                    print(f"  - {col[0]}: {col[1]} (nullable: {col[2]}, default: {col[3]})")
        
        cursor.close()
        conn.close()
        
        print("\n🎉 Correção de colunas tipo_usuario concluída com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro na correção: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("🚀 Iniciando correção de colunas tipo_usuario para tipo...")
    corrigir_colunas_tipo()
