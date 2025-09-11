#!/usr/bin/env python3
"""
Script para criar apenas as tabelas KDS críticas que estão faltando
Foco em resolver problemas específicos identificados pelos testes
"""

import sys
import traceback
from sqlalchemy import text, create_engine
from app.database import engine

# SQLs para criar as tabelas faltantes manualmente
CREATE_ESTACOES_KDS = """
CREATE TABLE IF NOT EXISTS estacoes_kds (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome VARCHAR(100) NOT NULL,
    descricao TEXT,
    tipo VARCHAR(20) DEFAULT 'principal',
    cor_tema VARCHAR(7) DEFAULT '#1E40AF',
    layout_colunas INTEGER DEFAULT 3,
    tempo_alerta_minutos INTEGER DEFAULT 15,
    ativa BOOLEAN DEFAULT 1,
    auto_atualizacao BOOLEAN DEFAULT 1,
    som_notificacao BOOLEAN DEFAULT 1,
    criado_em DATETIME DEFAULT CURRENT_TIMESTAMP,
    atualizado_em DATETIME,
    criado_por INTEGER REFERENCES usuarios(id)
);
"""

CREATE_PEDIDOS_KDS = """
CREATE TABLE IF NOT EXISTS pedidos_kds (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    numero_pedido VARCHAR(50) NOT NULL UNIQUE,
    nome_cliente VARCHAR(100),
    telefone_cliente VARCHAR(20),
    status VARCHAR(20) DEFAULT 'pendente',
    prioridade INTEGER DEFAULT 1,
    valor_total DECIMAL(10,2) DEFAULT 0,
    forma_pagamento VARCHAR(50),
    solicitado_em DATETIME DEFAULT CURRENT_TIMESTAMP,
    estimativa_entrega DATETIME,
    finalizado_em DATETIME,
    entregue_em DATETIME,
    observacoes TEXT,
    origem VARCHAR(20) DEFAULT 'balcao'
);
"""

CREATE_ITENS_KDS = """
CREATE TABLE IF NOT EXISTS itens_kds (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pedido_id INTEGER NOT NULL REFERENCES pedidos_kds(id),
    estacao_id INTEGER NOT NULL REFERENCES estacoes_kds(id),
    nome_produto VARCHAR(200) NOT NULL,
    descricao_item TEXT NOT NULL,
    observacoes TEXT,
    quantidade INTEGER DEFAULT 1,
    valor_unitario DECIMAL(10,2) DEFAULT 0,
    status VARCHAR(20) DEFAULT 'pendente',
    prioridade INTEGER DEFAULT 1,
    tempo_estimado_minutos INTEGER DEFAULT 10,
    solicitado_em DATETIME DEFAULT CURRENT_TIMESTAMP,
    iniciado_em DATETIME,
    finalizado_em DATETIME,
    entregue_em DATETIME
);
"""

# Tabela para resolver problema com fluxos
CREATE_FLUXOS_KDS_SIMPLE = """
CREATE TABLE IF NOT EXISTS fluxos_kds_temp (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome VARCHAR(100) NOT NULL,
    descricao TEXT,
    ativo BOOLEAN DEFAULT 1,
    criado_em DATETIME DEFAULT CURRENT_TIMESTAMP
);
"""

def create_critical_tables():
    """Cria apenas as tabelas críticas que estão faltando"""
    try:
        print("CRIANDO TABELAS CRITICAS KDS")
        print("=" * 50)
        
        with engine.connect() as conn:
            # Criar tabelas em ordem de dependência
            print("Criando tabela estacoes_kds...")
            conn.execute(text(CREATE_ESTACOES_KDS))
            
            print("Criando tabela pedidos_kds...")
            conn.execute(text(CREATE_PEDIDOS_KDS))
            
            print("Criando tabela itens_kds...")
            conn.execute(text(CREATE_ITENS_KDS))
            
            # Commit das mudanças
            conn.commit()
            
            # Verificar se foram criadas
            try:
                result = conn.execute(text("SELECT COUNT(*) FROM estacoes_kds"))
                print(f"Tabela 'estacoes_kds': {result.scalar()} registros")
            except Exception as e:
                print(f"Erro verificando estacoes_kds: {e}")
                
            try:
                result = conn.execute(text("SELECT COUNT(*) FROM pedidos_kds"))
                print(f"Tabela 'pedidos_kds': {result.scalar()} registros")
            except Exception as e:
                print(f"Erro verificando pedidos_kds: {e}")
                
            try:
                result = conn.execute(text("SELECT COUNT(*) FROM itens_kds"))
                print(f"Tabela 'itens_kds': {result.scalar()} registros")
            except Exception as e:
                print(f"Erro verificando itens_kds: {e}")
                
        print("TABELAS CRITICAS CRIADAS COM SUCESSO!")
        return True
        
    except Exception as e:
        print(f"Erro critico ao criar tabelas: {e}")
        traceback.print_exc()
        return False

def create_demo_data():
    """Cria dados básicos de demonstração"""
    try:
        print("\nCRIANDO DADOS BASICOS DE DEMONSTRACAO")
        print("=" * 50)
        
        with engine.connect() as conn:
            # Verificar se já existem dados
            result = conn.execute(text("SELECT COUNT(*) FROM estacoes_kds"))
            if result.scalar() > 0:
                print("Dados ja existem, pulando criacao")
                return True
                
            # Inserir estações básicas
            conn.execute(text("""
                INSERT INTO estacoes_kds (nome, descricao, tipo, cor_tema, criado_por)
                VALUES 
                    ('Cozinha Principal', 'Estacao principal da cozinha', 'cozinha', '#FF6B6B', 1),
                    ('Bar', 'Estacao para bebidas', 'bar', '#4ECDC4', 1),
                    ('Lanchonete', 'Estacao de lanches rapidos', 'lanche', '#45B7D1', 1)
            """))
            
            # Inserir pedido de exemplo
            conn.execute(text("""
                INSERT INTO pedidos_kds (numero_pedido, nome_cliente, status, valor_total)
                VALUES ('P001', 'Cliente Teste', 'pendente', 25.50)
            """))
            
            # Inserir item de exemplo
            conn.execute(text("""
                INSERT INTO itens_kds (pedido_id, estacao_id, nome_produto, descricao_item, quantidade)
                VALUES (1, 1, 'Hamburguer', 'Hamburguer artesanal com fritas', 1)
            """))
            
            conn.commit()
            print("Dados de demonstracao criados com sucesso!")
            return True
            
    except Exception as e:
        print(f"Erro ao criar dados de demonstracao: {e}")
        traceback.print_exc()
        return False

def main():
    """Função principal"""
    print("INICIANDO CORRECAO CRITICA - TABELAS KDS ESSENCIAIS")
    print("=" * 60)
    
    # Passo 1: Criar tabelas críticas
    if not create_critical_tables():
        print("FALHA: Nao foi possivel criar as tabelas criticas")
        sys.exit(1)
        
    # Passo 2: Criar dados básicos
    if not create_demo_data():
        print("Aviso: Dados de demonstracao nao foram criados")
    
    print("\n" + "=" * 60)
    print("CORRECAO CRITICA FINALIZADA!")
    print("Tabelas KDS essenciais estao disponiveis")
    print("Backend pode ser reiniciado")
    print("=" * 60)

if __name__ == "__main__":
    main()