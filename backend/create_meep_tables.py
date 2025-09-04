#!/usr/bin/env python3
"""
Script para criar todas as tabelas MEEP no banco de dados
Funciona tanto com SQLite quanto PostgreSQL
"""

import os
import sys
from datetime import datetime
from sqlalchemy import create_engine, text, MetaData, inspect
from sqlalchemy.exc import SQLAlchemyError
import json

# Adicionar o diretrio do app ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# SQL para criar as tabelas MEEP
MEEP_TABLES_SQL = """
-- Tabela de clientes para eventos (LGPD compliant)
CREATE TABLE IF NOT EXISTS clientes_eventos (
    id SERIAL PRIMARY KEY,
    cpf VARCHAR(11) UNIQUE NOT NULL,
    nome_completo VARCHAR(255),
    email VARCHAR(255),
    telefone VARCHAR(20),
    data_nascimento DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de validaes de acesso (check-in multi-fator)
CREATE TABLE IF NOT EXISTS validacoes_acesso (
    id SERIAL PRIMARY KEY,
    evento_id INTEGER,
    cliente_id INTEGER REFERENCES clientes_eventos(id),
    cpf_hash VARCHAR(64),
    qr_code_data TEXT,
    cpf_digits VARCHAR(3),
    ip_address VARCHAR(45),
    user_agent TEXT,
    sucesso BOOLEAN DEFAULT FALSE,
    motivo_falha VARCHAR(255),
    timestamp_validacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (evento_id) REFERENCES eventos(id) ON DELETE CASCADE
);

-- Tabela de equipamentos para monitoramento
CREATE TABLE IF NOT EXISTS equipamentos_eventos (
    id SERIAL PRIMARY KEY,
    evento_id INTEGER,
    nome VARCHAR(100) NOT NULL,
    tipo VARCHAR(50),
    codigo VARCHAR(50) UNIQUE,
    localizacao VARCHAR(255),
    status VARCHAR(20) DEFAULT 'offline',
    ultima_atividade TIMESTAMP,
    configuracoes JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (evento_id) REFERENCES eventos(id) ON DELETE CASCADE
);

-- Tabela de sesses de operadores
CREATE TABLE IF NOT EXISTS sessoes_operadores (
    id SERIAL PRIMARY KEY,
    operador_id INTEGER,
    evento_id INTEGER,
    equipamento_id INTEGER REFERENCES equipamentos_eventos(id),
    token_sessao VARCHAR(255) UNIQUE NOT NULL,
    ip_address VARCHAR(45),
    user_agent TEXT,
    inicio_sessao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fim_sessao TIMESTAMP,
    ativo BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (operador_id) REFERENCES usuarios(id) ON DELETE CASCADE,
    FOREIGN KEY (evento_id) REFERENCES eventos(id) ON DELETE CASCADE
);

-- Tabela de previses de IA
CREATE TABLE IF NOT EXISTS previsoes_ia (
    id SERIAL PRIMARY KEY,
    evento_id INTEGER,
    tipo_previsao VARCHAR(50),
    dados_entrada JSON,
    resultado_previsao JSON,
    confiabilidade FLOAT,
    timestamp_previsao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    valido_ate TIMESTAMP,
    usado BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (evento_id) REFERENCES eventos(id) ON DELETE CASCADE
);

-- Tabela de analytics MEEP
CREATE TABLE IF NOT EXISTS analytics_meep (
    id SERIAL PRIMARY KEY,
    evento_id INTEGER,
    tipo_metrica VARCHAR(50),
    valor_metrico JSON,
    periodo VARCHAR(20),
    timestamp_coleta TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    processado BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (evento_id) REFERENCES eventos(id) ON DELETE CASCADE
);

-- Tabela de logs de segurana MEEP
CREATE TABLE IF NOT EXISTS logs_seguranca_meep (
    id SERIAL PRIMARY KEY,
    evento_id INTEGER,
    tipo_evento VARCHAR(100),
    gravidade VARCHAR(20),
    descricao TEXT,
    ip_address VARCHAR(45),
    user_agent TEXT,
    dados_evento JSON,
    timestamp_evento TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolvido BOOLEAN DEFAULT FALSE,
    resolvido_por INTEGER,
    resolvido_em TIMESTAMP,
    FOREIGN KEY (evento_id) REFERENCES eventos(id) ON DELETE CASCADE,
    FOREIGN KEY (resolvido_por) REFERENCES usuarios(id)
);

-- Criar ndices para melhor performance
CREATE INDEX IF NOT EXISTS idx_clientes_cpf ON clientes_eventos(cpf);
CREATE INDEX IF NOT EXISTS idx_validacoes_evento ON validacoes_acesso(evento_id);
CREATE INDEX IF NOT EXISTS idx_validacoes_timestamp ON validacoes_acesso(timestamp_validacao);
CREATE INDEX IF NOT EXISTS idx_equipamentos_evento ON equipamentos_eventos(evento_id);
CREATE INDEX IF NOT EXISTS idx_equipamentos_status ON equipamentos_eventos(status);
CREATE INDEX IF NOT EXISTS idx_sessoes_ativo ON sessoes_operadores(ativo);
CREATE INDEX IF NOT EXISTS idx_previsoes_evento ON previsoes_ia(evento_id);
CREATE INDEX IF NOT EXISTS idx_analytics_evento ON analytics_meep(evento_id);
CREATE INDEX IF NOT EXISTS idx_logs_evento ON logs_seguranca_meep(evento_id);
CREATE INDEX IF NOT EXISTS idx_logs_gravidade ON logs_seguranca_meep(gravidade);
"""

# SQL especfico para SQLite (ajustes necessrios)
SQLITE_ADJUSTMENTS = """
-- SQLite no suporta SERIAL, usar INTEGER PRIMARY KEY AUTOINCREMENT
-- SQLite no suporta JSON nativo em verses antigas, usar TEXT
-- Ajustes so feitos dinamicamente no cdigo
"""

def get_database_url():
    """Obtm a URL do banco de dados"""
    return os.getenv('DATABASE_URL', 'sqlite:///./paineluniversal.db')

def is_sqlite(url):
    """Verifica se  SQLite"""
    return 'sqlite' in url

def adapt_sql_for_sqlite(sql):
    """Adapta SQL para SQLite"""
    sql = sql.replace('SERIAL PRIMARY KEY', 'INTEGER PRIMARY KEY AUTOINCREMENT')
    sql = sql.replace('JSON', 'TEXT')
    sql = sql.replace('BOOLEAN', 'INTEGER')
    # SQLite no precisa de ON DELETE CASCADE na definio
    sql = sql.replace(' ON DELETE CASCADE', '')
    return sql

def create_meep_tables():
    """Cria todas as tabelas MEEP"""
    database_url = get_database_url()
    print(f"[INFO] Conectando ao banco de dados: {database_url[:30]}...")
    
    try:
        # Criar engine
        engine = create_engine(database_url)
        inspector = inspect(engine)
        existing_tables = inspector.get_table_names()
        
        print(f"[INFO] Tabelas existentes: {len(existing_tables)}")
        
        # Adaptar SQL se for SQLite
        sql_to_execute = MEEP_TABLES_SQL
        if is_sqlite(database_url):
            print(" Adaptando SQL para SQLite...")
            sql_to_execute = adapt_sql_for_sqlite(sql_to_execute)
        
        # Executar SQL
        with engine.connect() as conn:
            # Dividir o SQL em comandos individuais
            commands = [cmd.strip() for cmd in sql_to_execute.split(';') if cmd.strip()]
            
            created_tables = []
            created_indexes = []
            
            for command in commands:
                if command:
                    try:
                        conn.execute(text(command))
                        conn.commit()
                        
                        # Identificar o que foi criado
                        if 'CREATE TABLE' in command:
                            table_name = command.split('EXISTS')[1].split('(')[0].strip()
                            created_tables.append(table_name)
                            print(f"   Tabela criada: {table_name}")
                        elif 'CREATE INDEX' in command:
                            index_name = command.split('EXISTS')[1].split('ON')[0].strip()
                            created_indexes.append(index_name)
                            print(f"   ndice criado: {index_name}")
                            
                    except Exception as e:
                        if 'already exists' not in str(e).lower():
                            print(f"   Aviso: {str(e)[:100]}")
            
            print(f"\n Migrao MEEP concluda!")
            print(f"   Tabelas criadas/verificadas: {len(created_tables)}")
            print(f"   ndices criados/verificados: {len(created_indexes)}")
            
            # Verificar tabelas finais
            inspector = inspect(engine)
            meep_tables = [t for t in inspector.get_table_names() if 'meep' in t or 'clientes' in t or 'validacoes' in t or 'equipamentos' in t or 'sessoes' in t or 'previsoes' in t or 'analytics' in t]
            
            print(f"\n Tabelas MEEP no banco:")
            for table in meep_tables:
                columns = inspector.get_columns(table)
                print(f"   {table} ({len(columns)} colunas)")
            
            return True
            
    except SQLAlchemyError as e:
        print(f" Erro ao criar tabelas: {e}")
        return False
    except Exception as e:
        print(f" Erro inesperado: {e}")
        return False

def insert_demo_data():
    """Insere dados de demonstrao"""
    database_url = get_database_url()
    
    try:
        engine = create_engine(database_url)
        
        with engine.connect() as conn:
            # Verificar se j existem dados
            result = conn.execute(text("SELECT COUNT(*) FROM clientes_eventos"))
            count = result.scalar()
            
            if count > 0:
                print(f" Banco j possui {count} clientes. Pulando insero de dados demo.")
                return
            
            print("\n Inserindo dados de demonstrao...")
            
            # Inserir clientes demo
            demo_clientes = [
                ('12345678901', 'Joo Silva MEEP', 'joao@meep.com', '11999998888'),
                ('98765432109', 'Maria Analytics', 'maria@meep.com', '11888887777'),
                ('11122233344', 'Pedro Check-in', 'pedro@meep.com', '11777776666'),
                ('55566677788', 'Ana Dashboard', 'ana@meep.com', '11666665555'),
                ('99988877766', 'Carlos IA', 'carlos@meep.com', '11555554444')
            ]
            
            for cpf, nome, email, telefone in demo_clientes:
                try:
                    conn.execute(text("""
                        INSERT INTO clientes_eventos (cpf, nome_completo, email, telefone)
                        VALUES (:cpf, :nome, :email, :telefone)
                    """), {'cpf': cpf, 'nome': nome, 'email': email, 'telefone': telefone})
                    print(f"   Cliente inserido: {nome}")
                except:
                    pass  # Ignorar se j existe
            
            conn.commit()
            
            # Inserir equipamentos demo (se houver evento)
            result = conn.execute(text("SELECT id FROM eventos LIMIT 1"))
            evento = result.first()
            
            if evento:
                evento_id = evento[0]
                
                demo_equipamentos = [
                    ('Catraca Principal', 'catraca', 'CTR-001', 'Entrada Principal'),
                    ('Leitor QR Mobile', 'mobile', 'MOB-001', 'rea VIP'),
                    ('Terminal PDV 1', 'pdv', 'PDV-001', 'Bar Principal'),
                    ('Camera Fluxo', 'camera', 'CAM-001', 'Entrada'),
                    ('Sensor Ocupao', 'sensor', 'SNS-001', 'Pista')
                ]
                
                for nome, tipo, codigo, local in demo_equipamentos:
                    try:
                        conn.execute(text("""
                            INSERT INTO equipamentos_eventos (evento_id, nome, tipo, codigo, localizacao, status)
                            VALUES (:evento_id, :nome, :tipo, :codigo, :local, 'online')
                        """), {
                            'evento_id': evento_id,
                            'nome': nome,
                            'tipo': tipo,
                            'codigo': codigo,
                            'local': local
                        })
                        print(f"   Equipamento inserido: {nome}")
                    except:
                        pass
                
                conn.commit()
                
            print("\n[SUCESSO] Dados de demonstracao inseridos com sucesso!")
            
    except Exception as e:
        print(f" Erro ao inserir dados demo: {e}")

def main():
    print("""
========================================================
          CRIACAO DE TABELAS MEEP - v2.0              
     Sistema Completo de Analytics e Check-in         
========================================================
    """)
    
    # Criar tabelas
    success = create_meep_tables()
    
    if success:
        # Inserir dados demo
        insert_demo_data()
        
        print("\n SISTEMA MEEP PREPARADO COM SUCESSO!")
        print("\n Tabelas criadas:")
        print("   clientes_eventos - Registro de clientes")
        print("   validacoes_acesso - Log de check-ins")
        print("   equipamentos_eventos - Monitoramento")
        print("   sessoes_operadores - Controle de sesses")
        print("   previsoes_ia - Armazenamento de IA")
        print("   analytics_meep - Mtricas agregadas")
        print("   logs_seguranca_meep - Auditoria")
        
    else:
        print("\n Falha na criao das tabelas MEEP")
        sys.exit(1)

if __name__ == "__main__":
    main()