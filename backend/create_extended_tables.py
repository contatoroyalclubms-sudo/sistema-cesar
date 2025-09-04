#!/usr/bin/env python3
"""
Create extended tables that don't conflict with existing tables
"""

from app.database import engine, get_db
from app.models import Base
from sqlalchemy import text, MetaData, Table, Column, Integer, String, DateTime, Boolean, Text, ForeignKey, Numeric, Date, Float, JSON, Time
from sqlalchemy.sql import func
import enum

# Create KDS tables manually since they're new
def create_kds_tables():
    with engine.connect() as conn:
        conn.execute(text("""
            DO $$ 
            BEGIN
                IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'statuspeditokds') THEN
                    CREATE TYPE statuspeditokds AS ENUM ('PENDENTE', 'EM_PREPARO', 'PRONTO', 'ENTREGUE', 'CANCELADO');
                END IF;
                
                IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'tipoestacaokds') THEN
                    CREATE TYPE tipoestacaokds AS ENUM ('COZINHA', 'BAR', 'EXPEDITOR', 'ESPECIAL');
                END IF;
                
                IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'statusmesa') THEN
                    CREATE TYPE statusmesa AS ENUM ('LIVRE', 'OCUPADA', 'RESERVADA', 'MANUTENCAO', 'INATIVA');
                END IF;
                
                IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'tipomesa') THEN
                    CREATE TYPE tipomesa AS ENUM ('NORMAL', 'VIP', 'REDONDA', 'RETANGULAR', 'BALCAO', 'EXTERNA');
                END IF;
            EXCEPTION 
                WHEN others THEN
                    NULL; -- Ignore errors in SQLite
            END
            $$;
        """))
        
        # Create KDS Station table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS estacoes_kds (
                id SERIAL PRIMARY KEY,
                nome VARCHAR(100) NOT NULL,
                tipo VARCHAR(20) NOT NULL DEFAULT 'COZINHA',
                descricao TEXT,
                evento_id INTEGER NOT NULL REFERENCES eventos(id) ON DELETE CASCADE,
                ativo BOOLEAN DEFAULT TRUE,
                ordem_exibicao INTEGER DEFAULT 1,
                configuracoes JSON,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """))
        
        # Create KDS Orders table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS pedidos_kds (
                id SERIAL PRIMARY KEY,
                numero_pedido VARCHAR(50) NOT NULL,
                estacao_id INTEGER NOT NULL REFERENCES estacoes_kds(id) ON DELETE CASCADE,
                status VARCHAR(20) NOT NULL DEFAULT 'PENDENTE',
                tempo_estimado_minutos INTEGER,
                observacoes TEXT,
                comanda_id INTEGER,
                venda_id INTEGER,
                prioridade VARCHAR(20) DEFAULT 'NORMAL',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                iniciado_em TIMESTAMP,
                finalizado_em TIMESTAMP,
                entregue_em TIMESTAMP
            );
        """))
        
        # Create KDS Order Items table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS itens_pedido_kds (
                id SERIAL PRIMARY KEY,
                pedido_id INTEGER NOT NULL REFERENCES pedidos_kds(id) ON DELETE CASCADE,
                produto_id INTEGER NOT NULL REFERENCES produtos(id),
                produto_nome VARCHAR(200) NOT NULL,
                quantidade INTEGER NOT NULL DEFAULT 1,
                observacoes TEXT,
                pronto BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """))
        
        # Create Tables Management table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS mesas_evento (
                id SERIAL PRIMARY KEY,
                numero VARCHAR(20) NOT NULL,
                nome VARCHAR(100) NOT NULL,
                tipo VARCHAR(20) NOT NULL DEFAULT 'NORMAL',
                status VARCHAR(20) NOT NULL DEFAULT 'LIVRE',
                capacidade INTEGER NOT NULL DEFAULT 4,
                evento_id INTEGER NOT NULL REFERENCES eventos(id) ON DELETE CASCADE,
                posicao_x INTEGER DEFAULT 0,
                posicao_y INTEGER DEFAULT 0,
                largura INTEGER DEFAULT 100,
                altura INTEGER DEFAULT 100,
                rotacao INTEGER DEFAULT 0,
                cor VARCHAR(7) DEFAULT '#3B82F6',
                ativo BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ocupada_em TIMESTAMP,
                liberada_em TIMESTAMP,
                reservada_em TIMESTAMP,
                UNIQUE(numero, evento_id)
            );
        """))
        
        # Create indexes for performance
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_estacoes_kds_evento ON estacoes_kds(evento_id);"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_pedidos_kds_estacao ON pedidos_kds(estacao_id);"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_pedidos_kds_status ON pedidos_kds(status);"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_itens_pedido_kds_pedido ON itens_pedido_kds(pedido_id);"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_mesas_evento_evento ON mesas_evento(evento_id);"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_mesas_evento_status ON mesas_evento(status);"))
        
        conn.commit()

if __name__ == "__main__":
    print("Creating extended tables (KDS and Tables Management)...")
    
    try:
        create_kds_tables()
        print("SUCCESS: Extended tables created successfully")
        print("- estacoes_kds (KDS Stations)")
        print("- pedidos_kds (KDS Orders)")
        print("- itens_pedido_kds (KDS Order Items)")
        print("- mesas_evento (Tables Management)")
        
    except Exception as e:
        print(f"ERROR: {e}")
        print("Note: Some errors may be expected in SQLite environments")