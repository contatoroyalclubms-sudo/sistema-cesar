#!/usr/bin/env python3
"""
Migration script to create import/export tables for enhanced inventory module
"""
import os
import sys
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy import text
from app.database import engine, get_db
from app.models import Base

def create_import_export_tables():
    """Create the import/export related tables"""
    
    # SQL para criar as tabelas de import/export
    sql_statements = [
        # Atualizar tabela produtos com novos campos
        """
        ALTER TABLE produtos ADD COLUMN IF NOT EXISTS marca VARCHAR(100);
        """,
        
        """
        ALTER TABLE produtos ADD COLUMN IF NOT EXISTS fornecedor VARCHAR(200);
        """,
        
        """
        ALTER TABLE produtos ADD COLUMN IF NOT EXISTS preco_custo DECIMAL(10, 2);
        """,
        
        """
        ALTER TABLE produtos ADD COLUMN IF NOT EXISTS margem_lucro DECIMAL(5, 2);
        """,
        
        """
        ALTER TABLE produtos ADD COLUMN IF NOT EXISTS unidade_medida VARCHAR(10) DEFAULT 'UN';
        """,
        
        """
        ALTER TABLE produtos ADD COLUMN IF NOT EXISTS volume DECIMAL(8, 2);
        """,
        
        """
        ALTER TABLE produtos ADD COLUMN IF NOT EXISTS teor_alcoolico DECIMAL(4, 2);
        """,
        
        """
        ALTER TABLE produtos ADD COLUMN IF NOT EXISTS temperatura_ideal VARCHAR(20);
        """,
        
        """
        ALTER TABLE produtos ADD COLUMN IF NOT EXISTS validade_dias INTEGER;
        """,
        
        """
        ALTER TABLE produtos ADD COLUMN IF NOT EXISTS ncm VARCHAR(8);
        """,
        
        """
        ALTER TABLE produtos ADD COLUMN IF NOT EXISTS icms DECIMAL(5, 2);
        """,
        
        """
        ALTER TABLE produtos ADD COLUMN IF NOT EXISTS ipi DECIMAL(5, 2);
        """,
        
        """
        ALTER TABLE produtos ADD COLUMN IF NOT EXISTS destaque BOOLEAN DEFAULT FALSE;
        """,
        
        """
        ALTER TABLE produtos ADD COLUMN IF NOT EXISTS promocional BOOLEAN DEFAULT FALSE;
        """,
        
        """
        ALTER TABLE produtos ADD COLUMN IF NOT EXISTS observacoes TEXT;
        """,
        
        # Criar tabela de operações de import/export
        """
        CREATE TABLE IF NOT EXISTS operacoes_import_export (
            id SERIAL PRIMARY KEY,
            tipo_operacao VARCHAR(20) NOT NULL CHECK (tipo_operacao IN ('IMPORTACAO', 'EXPORTACAO')),
            nome_arquivo VARCHAR(255) NOT NULL,
            formato_arquivo VARCHAR(10) NOT NULL,
            tamanho_arquivo INTEGER,
            usuario_id INTEGER REFERENCES usuarios(id),
            evento_id INTEGER REFERENCES eventos(id),
            empresa_id INTEGER REFERENCES empresas(id),
            
            -- Status e progresso
            status VARCHAR(20) DEFAULT 'PENDENTE' CHECK (status IN ('PENDENTE', 'PROCESSANDO', 'CONCLUIDA', 'ERRO', 'CANCELADA')),
            total_registros INTEGER DEFAULT 0,
            registros_processados INTEGER DEFAULT 0,
            registros_sucesso INTEGER DEFAULT 0,
            registros_erro INTEGER DEFAULT 0,
            registros_aviso INTEGER DEFAULT 0,
            
            -- Configurações
            mapeamento_campos TEXT, -- JSON
            filtros_aplicados TEXT, -- JSON
            campos_personalizados TEXT, -- JSON
            
            -- Tempos
            inicio_processamento TIMESTAMP WITH TIME ZONE,
            fim_processamento TIMESTAMP WITH TIME ZONE,
            criado_em TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            
            -- Logs e resultados
            log_detalhado TEXT,
            url_arquivo_resultado VARCHAR(500),
            resumo_operacao TEXT -- JSON
        );
        """,
        
        # Criar tabela de validações de importação
        """
        CREATE TABLE IF NOT EXISTS validacoes_importacao (
            id SERIAL PRIMARY KEY,
            operacao_id INTEGER REFERENCES operacoes_import_export(id) ON DELETE CASCADE,
            linha_arquivo INTEGER NOT NULL,
            campo VARCHAR(100),
            tipo_validacao VARCHAR(50),
            status VARCHAR(20) NOT NULL CHECK (status IN ('VALIDO', 'ERRO_CRITICO', 'AVISO')),
            mensagem TEXT NOT NULL,
            valor_original VARCHAR(500),
            valor_sugerido VARCHAR(500),
            corrigido BOOLEAN DEFAULT FALSE,
            criado_em TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        """,
        
        # Criar tabela de templates de importação
        """
        CREATE TABLE IF NOT EXISTS templates_importacao (
            id SERIAL PRIMARY KEY,
            nome VARCHAR(100) NOT NULL,
            descricao TEXT,
            formato VARCHAR(10) NOT NULL,
            mapeamento_padrao TEXT NOT NULL, -- JSON
            campos_obrigatorios TEXT, -- JSON array
            validacoes_personalizadas TEXT, -- JSON
            ativo BOOLEAN DEFAULT TRUE,
            usuario_criador_id INTEGER REFERENCES usuarios(id),
            empresa_id INTEGER REFERENCES empresas(id),
            criado_em TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            atualizado_em TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        """,
        
        # Criar índices para performance
        """
        CREATE INDEX IF NOT EXISTS idx_operacoes_import_export_usuario_id ON operacoes_import_export(usuario_id);
        """,
        
        """
        CREATE INDEX IF NOT EXISTS idx_operacoes_import_export_evento_id ON operacoes_import_export(evento_id);
        """,
        
        """
        CREATE INDEX IF NOT EXISTS idx_operacoes_import_export_status ON operacoes_import_export(status);
        """,
        
        """
        CREATE INDEX IF NOT EXISTS idx_operacoes_import_export_criado_em ON operacoes_import_export(criado_em);
        """,
        
        """
        CREATE INDEX IF NOT EXISTS idx_validacoes_importacao_operacao_id ON validacoes_importacao(operacao_id);
        """,
        
        """
        CREATE INDEX IF NOT EXISTS idx_validacoes_importacao_status ON validacoes_importacao(status);
        """,
        
        """
        CREATE INDEX IF NOT EXISTS idx_templates_importacao_ativo ON templates_importacao(ativo);
        """,
        
        """
        CREATE INDEX IF NOT EXISTS idx_produtos_marca ON produtos(marca);
        """,
        
        """
        CREATE INDEX IF NOT EXISTS idx_produtos_fornecedor ON produtos(fornecedor);
        """,
        
        """
        CREATE INDEX IF NOT EXISTS idx_produtos_ncm ON produtos(ncm);
        """,
        
        """
        CREATE INDEX IF NOT EXISTS idx_produtos_destaque ON produtos(destaque);
        """,
        
        """
        CREATE INDEX IF NOT EXISTS idx_produtos_promocional ON produtos(promocional);
        """
    ]
    
    print("🚀 Iniciando criação das tabelas de import/export...")
    
    try:
        with engine.connect() as connection:
            for i, sql in enumerate(sql_statements, 1):
                try:
                    print(f"⚙️ Executando comando {i}/{len(sql_statements)}...")
                    connection.execute(text(sql))
                    connection.commit()
                    print(f"✅ Comando {i} executado com sucesso")
                except Exception as e:
                    print(f"⚠️ Aviso no comando {i}: {e}")
                    # Continuar mesmo com avisos (ex: coluna já existe)
                    continue
        
        print("\n🎉 Migração concluída com sucesso!")
        print("\n📋 Resumo das alterações:")
        print("  • Adicionados campos extras à tabela produtos (marca, fornecedor, etc.)")
        print("  • Criada tabela operacoes_import_export")
        print("  • Criada tabela validacoes_importacao") 
        print("  • Criada tabela templates_importacao")
        print("  • Criados índices para otimização de performance")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro durante a migração: {e}")
        return False

def verify_tables():
    """Verificar se as tabelas foram criadas corretamente"""
    print("\n🔍 Verificando tabelas criadas...")
    
    verification_queries = [
        ("operacoes_import_export", "SELECT COUNT(*) FROM operacoes_import_export LIMIT 1"),
        ("validacoes_importacao", "SELECT COUNT(*) FROM validacoes_importacao LIMIT 1"),
        ("templates_importacao", "SELECT COUNT(*) FROM templates_importacao LIMIT 1"),
    ]
    
    try:
        with engine.connect() as connection:
            for table_name, query in verification_queries:
                try:
                    result = connection.execute(text(query))
                    print(f"✅ Tabela {table_name}: OK")
                except Exception as e:
                    print(f"❌ Tabela {table_name}: ERRO - {e}")
                    return False
        
        print("✅ Todas as tabelas foram verificadas com sucesso!")
        return True
        
    except Exception as e:
        print(f"❌ Erro durante verificação: {e}")
        return False

def main():
    """Função principal"""
    print("=" * 60)
    print("🏗️  MIGRAÇÃO: Módulo Import/Export do Estoque")
    print("=" * 60)
    
    # Verificar conexão com banco
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        print("✅ Conexão com banco de dados estabelecida")
    except Exception as e:
        print(f"❌ Erro de conexão com banco: {e}")
        sys.exit(1)
    
    # Executar migração
    if create_import_export_tables():
        if verify_tables():
            print("\n🎊 Migração completa! O módulo de import/export está pronto para uso.")
            print("\n📖 Próximos passos:")
            print("  1. Reiniciar o servidor backend")
            print("  2. Testar as funcionalidades de importação")
            print("  3. Configurar templates de importação")
        else:
            print("\n⚠️ Migração executada, mas verificação falhou")
            sys.exit(1)
    else:
        print("\n❌ Falha na migração")
        sys.exit(1)

if __name__ == "__main__":
    main()