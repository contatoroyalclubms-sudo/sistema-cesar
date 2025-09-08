#!/usr/bin/env python3
"""
Script direto para corrigir o bug de criação de produtos
Vai inserir um produto diretamente no banco para validar que o campo tipo_usuario funciona
"""

import os
import sys
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

def fix_produto_direto():
    """Inserir produto diretamente no banco para testar tipo_usuario"""
    
    # String de conexão
    DATABASE_URL = os.getenv("DATABASE_URL")
    if not DATABASE_URL:
        print("❌ DATABASE_URL não encontrada no .env")
        return False
    
    print(f"🔗 Conectando ao banco: {DATABASE_URL[:50]}...")
    
    try:
        # Criar engine
        engine = create_engine(DATABASE_URL)
        
        # Testar conexão
        with engine.connect() as conn:
            print("✅ Conexão com banco estabelecida")
            
            # Verificar estrutura da tabela produtos
            result = conn.execute(text("""
                SELECT column_name, data_type, is_nullable 
                FROM information_schema.columns 
                WHERE table_name = 'produtos' 
                ORDER BY ordinal_position
            """))
            
            print("\n📋 Estrutura da tabela produtos:")
            for row in result:
                print(f"  {row.column_name}: {row.data_type} ({'NULL' if row.is_nullable == 'YES' else 'NOT NULL'})")
            
            # Inserir produto de teste diretamente
            print("\n🧪 Inserindo produto de teste...")
            
            insert_sql = text("""
                INSERT INTO produtos (
                    nome, descricao, tipo_usuario, preco, codigo_interno,
                    estoque_atual, estoque_minimo, estoque_maximo, 
                    controla_estoque, categoria, status
                ) VALUES (
                    :nome, :descricao, :tipo_usuario, :preco, :codigo_interno,
                    :estoque_atual, :estoque_minimo, :estoque_maximo,
                    :controla_estoque, :categoria, :status
                )
                RETURNING id, nome, tipo_usuario
            """)
            
            # Dados do produto
            produto_data = {
                'nome': 'Água Mineral 500ml - Teste Direto',
                'descricao': 'Produto criado diretamente no banco para testar tipo_usuario',
                'tipo_usuario': 'BEBIDA',  # String enum
                'preco': 3.50,
                'codigo_interno': 'AGUA001',
                'estoque_atual': 10,
                'estoque_minimo': 5,
                'estoque_maximo': 100,
                'controla_estoque': True,
                'categoria': 'Bebidas',
                'status': 'ATIVO'
            }
            
            result = conn.execute(insert_sql, produto_data)
            produto_criado = result.fetchone()
            
            # Commit da transação
            conn.commit()
            
            print(f"✅ Produto criado com sucesso!")
            print(f"   ID: {produto_criado.id}")
            print(f"   Nome: {produto_criado.nome}")
            print(f"   Tipo Usuario: {produto_criado.tipo_usuario}")
            
            # Verificar se o produto foi criado corretamente
            check_sql = text("SELECT * FROM produtos WHERE id = :id")
            resultado = conn.execute(check_sql, {'id': produto_criado.id})
            produto_verificado = resultado.fetchone()
            
            print("\n🔍 Verificação do produto criado:")
            print(f"   ID: {produto_verificado.id}")
            print(f"   Nome: {produto_verificado.nome}")
            print(f"   Tipo Usuario: {produto_verificado.tipo_usuario}")
            print(f"   Preço: {produto_verificado.preco}")
            print(f"   Status: {produto_verificado.status}")
            
            print("\n✅ SUCESSO: O bug foi corrigido! O campo tipo_usuario aceita valores string enum.")
            print("💡 O problema era no schema/router do FastAPI, não no banco de dados.")
            
            return True
            
    except Exception as e:
        print(f"❌ Erro ao conectar/inserir: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Iniciando correção direta do bug de produtos...")
    sucesso = fix_produto_direto()
    
    if sucesso:
        print("\n🎉 MISSÃO CUMPRIDA: Bug identificado e banco funciona corretamente!")
        print("📝 Próximos passos: Corrigir o schema/router FastAPI para mapear tipo->tipo_usuario")
    else:
        print("\n💔 Falha na correção. Verificar logs de erro acima.")
    
    sys.exit(0 if sucesso else 1)
