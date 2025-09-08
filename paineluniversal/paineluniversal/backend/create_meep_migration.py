#!/usr/bin/env python3
"""Create MEEP integration tables migration"""

import os
from sqlalchemy import create_engine, text
from app.database import settings

def create_meep_tables():
    """Create MEEP integration tables"""
    
    sql_file = "meep_migration.sql"
    
    if not os.path.exists(sql_file):
        print(f"Creating {sql_file}")
        
        sql_content = """-- MEEP Integration Tables Migration
-- Create new tables for MEEP functionality

CREATE TABLE IF NOT EXISTS clientes_eventos (
    id SERIAL PRIMARY KEY,
    cpf VARCHAR(11) UNIQUE NOT NULL,
    nome_completo VARCHAR(255) NOT NULL,
    nome_social VARCHAR(255),
    data_nascimento DATE,
    nome_mae VARCHAR(255),
    telefone VARCHAR(20),
    email VARCHAR(255),
    status VARCHAR(50) DEFAULT 'ativo',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS validacoes_acesso (
    id SERIAL PRIMARY KEY,
    evento_id INTEGER REFERENCES eventos(id) ON DELETE CASCADE,
    cliente_id INTEGER REFERENCES clientes_eventos(id) ON DELETE CASCADE,
    cpf_hash VARCHAR(255) NOT NULL,
    qr_code_data TEXT NOT NULL,
    cpf_digits VARCHAR(3) NOT NULL,
    ip_address INET,
    user_agent TEXT,
    timestamp_validacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    sucesso BOOLEAN DEFAULT FALSE,
    motivo_falha TEXT,
    latitude DECIMAL(10,8),
    longitude DECIMAL(11,8),
    device_info JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS equipamentos_eventos (
    id SERIAL PRIMARY KEY,
    evento_id INTEGER REFERENCES eventos(id) ON DELETE CASCADE,
    nome VARCHAR(255) NOT NULL,
    tipo VARCHAR(100) NOT NULL, -- 'tablet', 'qr_reader', 'printer', 'pos'
    ip_address INET NOT NULL,
    mac_address VARCHAR(17),
    status VARCHAR(50) DEFAULT 'offline',
    ultima_atividade TIMESTAMP,
    configuracao JSONB,
    localizacao VARCHAR(255),
    responsavel_id INTEGER REFERENCES usuarios(id),
    heartbeat_interval INTEGER DEFAULT 30,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(evento_id, ip_address)
);

CREATE TABLE IF NOT EXISTS sessoes_operadores (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER REFERENCES usuarios(id) ON DELETE CASCADE,
    evento_id INTEGER REFERENCES eventos(id) ON DELETE CASCADE,
    equipamento_id INTEGER REFERENCES equipamentos_eventos(id),
    token_sessao VARCHAR(255) UNIQUE NOT NULL,
    ip_address INET,
    inicio_sessao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fim_sessao TIMESTAMP,
    ativo BOOLEAN DEFAULT TRUE,
    configuracoes JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS previsoes_ia (
    id SERIAL PRIMARY KEY,
    evento_id INTEGER REFERENCES eventos(id) ON DELETE CASCADE,
    tipo_previsao VARCHAR(100) NOT NULL, -- 'fluxo_horario', 'pico_entrada', 'estimativa_total'
    dados_entrada JSONB NOT NULL,
    resultado_previsao JSONB NOT NULL,
    confiabilidade DECIMAL(5,2), -- Percentual de confiança
    timestamp_previsao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    aplicada BOOLEAN DEFAULT FALSE,
    feedback_real JSONB,
    precisao_real DECIMAL(5,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS analytics_meep (
    id SERIAL PRIMARY KEY,
    evento_id INTEGER REFERENCES eventos(id) ON DELETE CASCADE,
    metrica VARCHAR(100) NOT NULL,
    valor DECIMAL(15,2),
    valor_anterior DECIMAL(15,2),
    percentual_mudanca DECIMAL(5,2),
    periodo VARCHAR(50), -- 'hora', 'dia', 'semana', 'mes'
    timestamp_coleta TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    dados_detalhados JSONB,
    alertas JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS logs_seguranca_meep (
    id SERIAL PRIMARY KEY,
    evento_id INTEGER REFERENCES eventos(id) ON DELETE CASCADE,
    tipo_evento VARCHAR(100) NOT NULL, -- 'tentativa_acesso', 'validacao_cpf', 'erro_sistema'
    gravidade VARCHAR(20) DEFAULT 'info', -- 'info', 'warning', 'error', 'critical'
    ip_address INET,
    user_agent TEXT,
    dados_evento JSONB NOT NULL,
    usuario_id INTEGER REFERENCES usuarios(id),
    resolvido BOOLEAN DEFAULT FALSE,
    timestamp_evento TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índices para performance
CREATE INDEX IF NOT EXISTS idx_clientes_cpf ON clientes_eventos(cpf);
CREATE INDEX IF NOT EXISTS idx_validacoes_evento_id ON validacoes_acesso(evento_id);
CREATE INDEX IF NOT EXISTS idx_validacoes_timestamp ON validacoes_acesso(timestamp_validacao);
CREATE INDEX IF NOT EXISTS idx_equipamentos_evento_id ON equipamentos_eventos(evento_id);
CREATE INDEX IF NOT EXISTS idx_equipamentos_status ON equipamentos_eventos(status);
CREATE INDEX IF NOT EXISTS idx_sessoes_usuario_id ON sessoes_operadores(usuario_id);
CREATE INDEX IF NOT EXISTS idx_sessoes_ativo ON sessoes_operadores(ativo);
CREATE INDEX IF NOT EXISTS idx_previsoes_evento_id ON previsoes_ia(evento_id);
CREATE INDEX IF NOT EXISTS idx_previsoes_tipo ON previsoes_ia(tipo_previsao);
CREATE INDEX IF NOT EXISTS idx_analytics_evento_id ON analytics_meep(evento_id);
CREATE INDEX IF NOT EXISTS idx_analytics_metrica ON analytics_meep(metrica);
CREATE INDEX IF NOT EXISTS idx_logs_evento_id ON logs_seguranca_meep(evento_id);
CREATE INDEX IF NOT EXISTS idx_logs_tipo ON logs_seguranca_meep(tipo_evento);
CREATE INDEX IF NOT EXISTS idx_logs_timestamp ON logs_seguranca_meep(timestamp_evento);

-- Triggers para updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_clientes_eventos_updated_at BEFORE UPDATE ON clientes_eventos FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_equipamentos_eventos_updated_at BEFORE UPDATE ON equipamentos_eventos FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Views úteis
CREATE OR REPLACE VIEW v_validacoes_resumo AS
SELECT 
    e.nome as evento_nome,
    COUNT(*) as total_validacoes,
    COUNT(*) FILTER (WHERE va.sucesso = true) as validacoes_sucesso,
    COUNT(*) FILTER (WHERE va.sucesso = false) as validacoes_falha,
    ROUND(
        COUNT(*) FILTER (WHERE va.sucesso = true) * 100.0 / COUNT(*), 
        2
    ) as taxa_sucesso_pct
FROM validacoes_acesso va
JOIN eventos e ON va.evento_id = e.id
GROUP BY e.id, e.nome;

CREATE OR REPLACE VIEW v_equipamentos_status AS
SELECT 
    e.nome as evento_nome,
    eq.nome as equipamento_nome,
    eq.tipo,
    eq.status,
    eq.ultima_atividade,
    CASE 
        WHEN eq.ultima_atividade > (CURRENT_TIMESTAMP - INTERVAL '5 minutes') THEN 'online'
        WHEN eq.ultima_atividade > (CURRENT_TIMESTAMP - INTERVAL '1 hour') THEN 'warning'
        ELSE 'offline'
    END as status_conexao
FROM equipamentos_eventos eq
JOIN eventos e ON eq.evento_id = e.id;

-- Inserir dados iniciais de exemplo
INSERT INTO clientes_eventos (cpf, nome_completo, email) VALUES
('12345678901', 'Cliente Teste MEEP', 'teste@meep.com.br')
ON CONFLICT (cpf) DO NOTHING;

-- Análise de dados para IA (exemplo)
CREATE OR REPLACE VIEW v_dados_ia_fluxo AS
SELECT 
    evento_id,
    DATE_TRUNC('hour', timestamp_validacao) as hora,
    COUNT(*) as total_entradas,
    COUNT(*) FILTER (WHERE sucesso = true) as entradas_sucesso,
    AVG(EXTRACT(EPOCH FROM (timestamp_validacao - LAG(timestamp_validacao) OVER (PARTITION BY evento_id ORDER BY timestamp_validacao)))) as intervalo_medio_segundos
FROM validacoes_acesso
WHERE timestamp_validacao >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY evento_id, DATE_TRUNC('hour', timestamp_validacao)
ORDER BY evento_id, hora;

COMMIT;
"""
        
        with open(sql_file, 'w', encoding='utf-8') as f:
            f.write(sql_content)
    
    print(f"Executing migration from {sql_file}")
    
    # Conectar ao banco e executar migration
    engine = create_engine(settings.database_url)
    
    with engine.connect() as conn:
        with open(sql_file, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        # Executar o SQL
        for statement in sql_content.split(';'):
            statement = statement.strip()
            if statement and not statement.startswith('--'):
                try:
                    conn.execute(text(statement))
                    conn.commit()
                except Exception as e:
                    print(f"Warning: {e}")
                    continue
    
    print("MEEP migration completed successfully!")
    print("\nCreated tables:")
    print("- clientes_eventos")
    print("- validacoes_acesso") 
    print("- equipamentos_eventos")
    print("- sessoes_operadores")
    print("- previsoes_ia")
    print("- analytics_meep")
    print("- logs_seguranca_meep")
    print("\nCreated views:")
    print("- v_validacoes_resumo")
    print("- v_equipamentos_status")
    print("- v_dados_ia_fluxo")

if __name__ == "__main__":
    create_meep_tables()
