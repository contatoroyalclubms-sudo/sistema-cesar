#!/usr/bin/env python
"""
Migração do Banco de Dados - Sistema de Impressoras Térmicas
===========================================================

Script para adicionar as novas tabelas e enums do sistema de impressoras térmicas
ao banco de dados PostgreSQL.

Autor: Sistema Universal
Data: 2025
"""

import os
import logging
import traceback
from datetime import datetime
from sqlalchemy import create_engine, text, MetaData, inspect
from sqlalchemy.exc import SQLAlchemyError
import json

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class PrinterMigration:
    """Classe para executar a migração do sistema de impressoras"""
    
    def __init__(self):
        self.database_url = self._get_database_url()
        self.engine = create_engine(self.database_url)
        self.migration_log = {
            "inicio": datetime.now(),
            "etapas": [],
            "sucesso": False,
            "erros": []
        }
    
    def _get_database_url(self):
        """Obter URL do banco de dados"""
        database_url = os.getenv("DATABASE_URL", "sqlite:///./eventos.db")
        
        # Ajustar URL para PostgreSQL se necessário
        if database_url.startswith("postgres://"):
            database_url = database_url.replace("postgres://", "postgresql://", 1)
        
        return database_url
    
    def _log_etapa(self, nome: str, sucesso: bool, detalhes: str = ""):
        """Registrar etapa da migração"""
        etapa = {
            "nome": nome,
            "timestamp": datetime.now(),
            "sucesso": sucesso,
            "detalhes": detalhes
        }
        self.migration_log["etapas"].append(etapa)
        
        status = "✅" if sucesso else "❌"
        logger.info(f"{status} {nome}: {detalhes}")
    
    def verificar_conexao(self):
        """Verificar conexão com o banco de dados"""
        try:
            with self.engine.connect() as conn:
                if "sqlite" in self.database_url.lower():
                    result = conn.execute(text("SELECT sqlite_version()"))
                    version = result.scalar()
                    self._log_etapa(
                        "Verificação de Conexão",
                        True,
                        f"SQLite: {version}"
                    )
                else:
                    result = conn.execute(text("SELECT version()"))
                    version = result.scalar()
                    self._log_etapa(
                        "Verificação de Conexão",
                        True,
                        f"PostgreSQL: {version[:50]}..."
                    )
                return True
        except Exception as e:
            self._log_etapa(
                "Verificação de Conexão",
                False,
                f"Erro: {str(e)}"
            )
            return False
    
    def verificar_tabelas_existentes(self):
        """Verificar quais tabelas já existem"""
        try:
            inspector = inspect(self.engine)
            tabelas_existentes = inspector.get_table_names()
            
            tabelas_printer = [
                "impressoras", "print_templates", "print_jobs", "print_job_logs"
            ]
            
            tabelas_ja_existem = [t for t in tabelas_printer if t in tabelas_existentes]
            
            if tabelas_ja_existem:
                self._log_etapa(
                    "Verificação de Tabelas",
                    True,
                    f"Tabelas já existentes: {', '.join(tabelas_ja_existem)}"
                )
                return tabelas_ja_existem
            else:
                self._log_etapa(
                    "Verificação de Tabelas",
                    True,
                    "Nenhuma tabela de impressora encontrada - migração necessária"
                )
                return []
                
        except Exception as e:
            self._log_etapa(
                "Verificação de Tabelas",
                False,
                f"Erro: {str(e)}"
            )
            return None
    
    def criar_enums(self):
        """Criar tipos ENUM necessários (apenas para PostgreSQL)"""
        # Para SQLite, não precisamos criar ENUMs separados
        if "sqlite" in self.database_url.lower():
            self._log_etapa(
                "Criação de Enums",
                True,
                "SQLite detectado - ENUMs serão implementados como constraints"
            )
            return True
        
        enums_sql = [
            # Enum TipoImpressora
            """
            DO $$ 
            BEGIN
                IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'tipoimpressora') THEN
                    CREATE TYPE tipoimpressora AS ENUM ('TERMICA_58MM', 'TERMICA_80MM', 'MATRICIAL', 'JATO_TINTA');
                END IF;
            END $$;
            """,
            
            # Enum InterfaceImpressora
            """
            DO $$ 
            BEGIN
                IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'interfaceimpressora') THEN
                    CREATE TYPE interfaceimpressora AS ENUM ('USB', 'ETHERNET', 'WIFI', 'BLUETOOTH', 'PARALELA', 'SERIAL');
                END IF;
            END $$;
            """,
            
            # Enum StatusImpressora
            """
            DO $$ 
            BEGIN
                IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'statusimpressora') THEN
                    CREATE TYPE statusimpressora AS ENUM ('ONLINE', 'OFFLINE', 'ERRO_PAPEL', 'ERRO_CONEXAO', 'MANUTENCAO', 'DESCONHECIDO');
                END IF;
            END $$;
            """,
            
            # Enum TipoPrintJob
            """
            DO $$ 
            BEGIN
                IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'tipoprintjob') THEN
                    CREATE TYPE tipoprintjob AS ENUM ('RECIBO_CAIXA', 'PEDIDO_COZINHA', 'PEDIDO_BAR', 'COMANDA_RECARGA', 'COMANDA_FECHAMENTO', 'RELATORIO', 'TESTE');
                END IF;
            END $$;
            """,
            
            # Enum StatusPrintJob
            """
            DO $$ 
            BEGIN
                IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'statusprintjob') THEN
                    CREATE TYPE statusprintjob AS ENUM ('PENDENTE', 'PROCESSANDO', 'ENVIADO', 'IMPRESSO', 'ERRO', 'CANCELADO');
                END IF;
            END $$;
            """
        ]
        
        try:
            with self.engine.connect() as conn:
                for enum_sql in enums_sql:
                    conn.execute(text(enum_sql))
                conn.commit()
            
            self._log_etapa(
                "Criação de Enums",
                True,
                "5 tipos ENUM criados com sucesso"
            )
            return True
            
        except Exception as e:
            self._log_etapa(
                "Criação de Enums",
                False,
                f"Erro: {str(e)}"
            )
            return False
    
    def criar_tabela_impressoras(self):
        """Criar tabela impressoras"""
        # Escolher SQL baseado no tipo de banco
        if "sqlite" in self.database_url.lower():
            sql_commands = [
                """
                CREATE TABLE IF NOT EXISTS impressoras (
                    id VARCHAR(50) PRIMARY KEY,
                    nome VARCHAR(255) NOT NULL,
                    tipo VARCHAR(50) NOT NULL CHECK (tipo IN ('TERMICA_58MM', 'TERMICA_80MM', 'MATRICIAL', 'JATO_TINTA')),
                    interface VARCHAR(50) NOT NULL CHECK (interface IN ('USB', 'ETHERNET', 'WIFI', 'BLUETOOTH', 'PARALELA', 'SERIAL')),
                    endereco VARCHAR(500) NOT NULL,
                    porta INTEGER,
                    status VARCHAR(50) DEFAULT 'DESCONHECIDO' CHECK (status IN ('ONLINE', 'OFFLINE', 'ERRO_PAPEL', 'ERRO_CONEXAO', 'MANUTENCAO', 'DESCONHECIDO')),
                    configuracoes TEXT DEFAULT '{}',
                    estacao VARCHAR(100),
                    local_fisico VARCHAR(255),
                    ativo BOOLEAN DEFAULT 1,
                    densidade INTEGER DEFAULT 8,
                    velocidade INTEGER DEFAULT 100,
                    corte_automatico BOOLEAN DEFAULT 1,
                    evento_id INTEGER NOT NULL,
                    ip_bridge VARCHAR(45),
                    versao_driver VARCHAR(50),
                    ultimo_heartbeat TEXT,
                    criado_em TEXT DEFAULT CURRENT_TIMESTAMP,
                    atualizado_em TEXT DEFAULT CURRENT_TIMESTAMP,
                    
                    FOREIGN KEY (evento_id) REFERENCES eventos(id) ON DELETE CASCADE,
                    CHECK (porta IS NULL OR (porta >= 1 AND porta <= 65535)),
                    CHECK (densidade >= 1 AND densidade <= 15),
                    CHECK (velocidade >= 1 AND velocidade <= 200)
                )
                """,
                "CREATE INDEX IF NOT EXISTS idx_impressoras_evento_id ON impressoras(evento_id)",
                "CREATE INDEX IF NOT EXISTS idx_impressoras_status ON impressoras(status)",
                "CREATE INDEX IF NOT EXISTS idx_impressoras_ativo ON impressoras(ativo)",
                "CREATE INDEX IF NOT EXISTS idx_impressoras_estacao ON impressoras(estacao)",
                "CREATE UNIQUE INDEX IF NOT EXISTS idx_impressoras_endereco_evento ON impressoras(evento_id, endereco) WHERE ativo = 1"
            ]
        else:
            sql_commands = [
                """
                CREATE TABLE IF NOT EXISTS impressoras (
                    id VARCHAR(50) PRIMARY KEY,
                    nome VARCHAR(255) NOT NULL,
                    tipo tipoimpressora NOT NULL,
                    interface interfaceimpressora NOT NULL,
                    endereco VARCHAR(500) NOT NULL,
                    porta INTEGER,
                    status statusimpressora DEFAULT 'DESCONHECIDO',
                    configuracoes JSONB DEFAULT '{}',
                    estacao VARCHAR(100),
                    local_fisico VARCHAR(255),
                    ativo BOOLEAN DEFAULT true,
                    densidade INTEGER DEFAULT 8,
                    velocidade INTEGER DEFAULT 100,
                    corte_automatico BOOLEAN DEFAULT true,
                    evento_id INTEGER NOT NULL,
                    ip_bridge VARCHAR(45),
                    versao_driver VARCHAR(50),
                    ultimo_heartbeat TIMESTAMP WITH TIME ZONE,
                    criado_em TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    atualizado_em TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    
                    CONSTRAINT fk_impressoras_evento 
                        FOREIGN KEY (evento_id) REFERENCES eventos(id) ON DELETE CASCADE,
                    CONSTRAINT chk_porta_valida 
                        CHECK (porta IS NULL OR (porta >= 1 AND porta <= 65535)),
                    CONSTRAINT chk_densidade_valida 
                        CHECK (densidade >= 1 AND densidade <= 15),
                    CONSTRAINT chk_velocidade_valida 
                        CHECK (velocidade >= 1 AND velocidade <= 200)
                )
                """,
                "CREATE INDEX IF NOT EXISTS idx_impressoras_evento_id ON impressoras(evento_id)",
                "CREATE INDEX IF NOT EXISTS idx_impressoras_status ON impressoras(status)",
                "CREATE INDEX IF NOT EXISTS idx_impressoras_ativo ON impressoras(ativo)",
                "CREATE INDEX IF NOT EXISTS idx_impressoras_estacao ON impressoras(estacao)",
                "CREATE UNIQUE INDEX IF NOT EXISTS idx_impressoras_endereco_evento ON impressoras(evento_id, endereco) WHERE ativo = true"
            ]
        
        try:
            with self.engine.connect() as conn:
                for sql in sql_commands:
                    conn.execute(text(sql))
                conn.commit()
            
            self._log_etapa(
                "Tabela Impressoras",
                True,
                "Tabela criada com índices de otimização"
            )
            return True
            
        except Exception as e:
            self._log_etapa(
                "Tabela Impressoras",
                False,
                f"Erro: {str(e)}"
            )
            return False
    
    def criar_tabela_print_templates(self):
        """Criar tabela print_templates"""
        if "sqlite" in self.database_url.lower():
            sql_commands = [
                """
                CREATE TABLE IF NOT EXISTS print_templates (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome VARCHAR(255) NOT NULL,
                    tipo_job VARCHAR(50) NOT NULL CHECK (tipo_job IN ('RECIBO_CAIXA', 'PEDIDO_COZINHA', 'PEDIDO_BAR', 'COMANDA_RECARGA', 'COMANDA_FECHAMENTO', 'RELATORIO', 'TESTE')),
                    template_esc_pos TEXT NOT NULL,
                    variaveis TEXT DEFAULT '[]',
                    configuracoes TEXT DEFAULT '{}',
                    evento_id INTEGER NOT NULL,
                    ativo BOOLEAN DEFAULT 1,
                    criado_em TEXT DEFAULT CURRENT_TIMESTAMP,
                    atualizado_em TEXT DEFAULT CURRENT_TIMESTAMP,
                    
                    FOREIGN KEY (evento_id) REFERENCES eventos(id) ON DELETE CASCADE
                )
                """,
                "CREATE INDEX IF NOT EXISTS idx_print_templates_evento_id ON print_templates(evento_id)",
                "CREATE INDEX IF NOT EXISTS idx_print_templates_tipo_job ON print_templates(tipo_job)",
                "CREATE INDEX IF NOT EXISTS idx_print_templates_ativo ON print_templates(ativo)"
            ]
        else:
            sql_commands = [
                """
                CREATE TABLE IF NOT EXISTS print_templates (
                    id SERIAL PRIMARY KEY,
                    nome VARCHAR(255) NOT NULL,
                    tipo_job tipoprintjob NOT NULL,
                    template_esc_pos TEXT NOT NULL,
                    variaveis JSONB DEFAULT '[]',
                    configuracoes JSONB DEFAULT '{}',
                    evento_id INTEGER NOT NULL,
                    ativo BOOLEAN DEFAULT true,
                    criado_em TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    atualizado_em TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    
                    CONSTRAINT fk_print_templates_evento 
                        FOREIGN KEY (evento_id) REFERENCES eventos(id) ON DELETE CASCADE
                )
                """,
                "CREATE INDEX IF NOT EXISTS idx_print_templates_evento_id ON print_templates(evento_id)",
                "CREATE INDEX IF NOT EXISTS idx_print_templates_tipo_job ON print_templates(tipo_job)",
                "CREATE INDEX IF NOT EXISTS idx_print_templates_ativo ON print_templates(ativo)"
            ]
        
        try:
            with self.engine.connect() as conn:
                for sql in sql_commands:
                    conn.execute(text(sql))
                conn.commit()
            
            self._log_etapa(
                "Tabela Print Templates",
                True,
                "Tabela criada com sucesso"
            )
            return True
            
        except Exception as e:
            self._log_etapa(
                "Tabela Print Templates",
                False,
                f"Erro: {str(e)}"
            )
            return False
    
    def criar_tabela_print_jobs(self):
        """Criar tabela print_jobs"""
        if "sqlite" in self.database_url.lower():
            sql = """
            CREATE TABLE IF NOT EXISTS print_jobs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                impressora_id VARCHAR(50) NOT NULL,
                tipo VARCHAR(50) NOT NULL CHECK (tipo IN ('RECIBO_CAIXA', 'PEDIDO_COZINHA', 'PEDIDO_BAR', 'COMANDA_RECARGA', 'COMANDA_FECHAMENTO', 'RELATORIO', 'TESTE')),
                prioridade INTEGER DEFAULT 5,
                status VARCHAR(50) DEFAULT 'PENDENTE' CHECK (status IN ('PENDENTE', 'PROCESSANDO', 'ENVIADO', 'IMPRESSO', 'ERRO', 'CANCELADO')),
                payload TEXT NOT NULL,
                resultado TEXT,
                tentativas INTEGER DEFAULT 0,
                max_tentativas INTEGER DEFAULT 3,
                agendado_para TEXT,
                processado_em TEXT,
                finalizado_em TEXT,
                evento_id INTEGER NOT NULL,
                cpf_operador VARCHAR(14),
                usuario_id INTEGER,
                ip_cliente VARCHAR(45),
                erro_detalhes TEXT,
                criado_em TEXT DEFAULT CURRENT_TIMESTAMP,
                
                FOREIGN KEY (impressora_id) REFERENCES impressoras(id) ON DELETE CASCADE,
                FOREIGN KEY (evento_id) REFERENCES eventos(id) ON DELETE CASCADE,
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE SET NULL,
                CHECK (prioridade >= 1 AND prioridade <= 10),
                CHECK (tentativas >= 0 AND tentativas <= max_tentativas)
            );
            
            -- Índices para otimização de consultas
            CREATE INDEX IF NOT EXISTS idx_print_jobs_impressora_id ON print_jobs(impressora_id);
            CREATE INDEX IF NOT EXISTS idx_print_jobs_status ON print_jobs(status);
            CREATE INDEX IF NOT EXISTS idx_print_jobs_evento_id ON print_jobs(evento_id);
            CREATE INDEX IF NOT EXISTS idx_print_jobs_prioridade ON print_jobs(prioridade);
            CREATE INDEX IF NOT EXISTS idx_print_jobs_agendado_para ON print_jobs(agendado_para);
            CREATE INDEX IF NOT EXISTS idx_print_jobs_criado_em ON print_jobs(criado_em);
            """
        else:
            sql = """
            CREATE TABLE IF NOT EXISTS print_jobs (
                id SERIAL PRIMARY KEY,
                impressora_id VARCHAR(50) NOT NULL,
                tipo tipoprintjob NOT NULL,
                prioridade INTEGER DEFAULT 5,
                status statusprintjob DEFAULT 'PENDENTE',
                payload JSONB NOT NULL,
                resultado JSONB,
                tentativas INTEGER DEFAULT 0,
                max_tentativas INTEGER DEFAULT 3,
                agendado_para TIMESTAMP WITH TIME ZONE,
                processado_em TIMESTAMP WITH TIME ZONE,
                finalizado_em TIMESTAMP WITH TIME ZONE,
                evento_id INTEGER NOT NULL,
                cpf_operador VARCHAR(14),
                usuario_id INTEGER,
                ip_cliente VARCHAR(45),
                erro_detalhes TEXT,
                criado_em TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                
                CONSTRAINT fk_print_jobs_impressora 
                    FOREIGN KEY (impressora_id) REFERENCES impressoras(id) ON DELETE CASCADE,
                CONSTRAINT fk_print_jobs_evento 
                    FOREIGN KEY (evento_id) REFERENCES eventos(id) ON DELETE CASCADE,
                CONSTRAINT fk_print_jobs_usuario 
                    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE SET NULL,
                CONSTRAINT chk_prioridade_valida 
                    CHECK (prioridade >= 1 AND prioridade <= 10),
                CONSTRAINT chk_tentativas_validas 
                    CHECK (tentativas >= 0 AND tentativas <= max_tentativas)
            );
            
            -- Índices para otimização de consultas
            CREATE INDEX IF NOT EXISTS idx_print_jobs_impressora_id ON print_jobs(impressora_id);
            CREATE INDEX IF NOT EXISTS idx_print_jobs_status ON print_jobs(status);
            CREATE INDEX IF NOT EXISTS idx_print_jobs_evento_id ON print_jobs(evento_id);
            CREATE INDEX IF NOT EXISTS idx_print_jobs_prioridade ON print_jobs(prioridade);
            CREATE INDEX IF NOT EXISTS idx_print_jobs_agendado_para ON print_jobs(agendado_para);
            CREATE INDEX IF NOT EXISTS idx_print_jobs_criado_em ON print_jobs(criado_em);
            
            -- Índice composto para fila de processamento
            CREATE INDEX IF NOT EXISTS idx_print_jobs_fila_processamento 
                ON print_jobs(impressora_id, status, prioridade, agendado_para) 
                WHERE status IN ('PENDENTE', 'PROCESSANDO');
            """
        
        try:
            with self.engine.connect() as conn:
                conn.execute(text(sql))
                conn.commit()
            
            self._log_etapa(
                "Tabela Print Jobs",
                True,
                "Tabela criada com índices de performance"
            )
            return True
            
        except Exception as e:
            self._log_etapa(
                "Tabela Print Jobs",
                False,
                f"Erro: {str(e)}"
            )
            return False
    
    def criar_tabela_print_job_logs(self):
        """Criar tabela print_job_logs"""
        if "sqlite" in self.database_url.lower():
            sql = """
            CREATE TABLE IF NOT EXISTS print_job_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                print_job_id INTEGER NOT NULL,
                status_anterior VARCHAR(50) CHECK (status_anterior IN ('PENDENTE', 'PROCESSANDO', 'ENVIADO', 'IMPRESSO', 'ERRO', 'CANCELADO')),
                status_novo VARCHAR(50) NOT NULL CHECK (status_novo IN ('PENDENTE', 'PROCESSANDO', 'ENVIADO', 'IMPRESSO', 'ERRO', 'CANCELADO')),
                detalhes TEXT,
                erro_codigo VARCHAR(50),
                erro_mensagem TEXT,
                dados_adicionais TEXT,
                criado_em TEXT DEFAULT CURRENT_TIMESTAMP,
                
                FOREIGN KEY (print_job_id) REFERENCES print_jobs(id) ON DELETE CASCADE
            );
            
            -- Índices
            CREATE INDEX IF NOT EXISTS idx_print_job_logs_job_id ON print_job_logs(print_job_id);
            CREATE INDEX IF NOT EXISTS idx_print_job_logs_status_novo ON print_job_logs(status_novo);
            CREATE INDEX IF NOT EXISTS idx_print_job_logs_criado_em ON print_job_logs(criado_em);
            """
        else:
            sql = """
            CREATE TABLE IF NOT EXISTS print_job_logs (
                id SERIAL PRIMARY KEY,
                print_job_id INTEGER NOT NULL,
                status_anterior statusprintjob,
                status_novo statusprintjob NOT NULL,
                detalhes TEXT,
                erro_codigo VARCHAR(50),
                erro_mensagem TEXT,
                dados_adicionais JSONB,
                criado_em TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                
                CONSTRAINT fk_print_job_logs_job 
                    FOREIGN KEY (print_job_id) REFERENCES print_jobs(id) ON DELETE CASCADE
            );
            
            -- Índices
            CREATE INDEX IF NOT EXISTS idx_print_job_logs_job_id ON print_job_logs(print_job_id);
            CREATE INDEX IF NOT EXISTS idx_print_job_logs_status_novo ON print_job_logs(status_novo);
            CREATE INDEX IF NOT EXISTS idx_print_job_logs_criado_em ON print_job_logs(criado_em);
            """
        
        try:
            with self.engine.connect() as conn:
                conn.execute(text(sql))
                conn.commit()
            
            self._log_etapa(
                "Tabela Print Job Logs",
                True,
                "Tabela de auditoria criada"
            )
            return True
            
        except Exception as e:
            self._log_etapa(
                "Tabela Print Job Logs",
                False,
                f"Erro: {str(e)}"
            )
            return False
    
    def inserir_dados_iniciais(self):
        """Inserir dados iniciais e templates padrão"""
        
        # Template padrão para recibo de caixa
        template_recibo = """
        {nome_empresa}
        {endereco_empresa}
        CNPJ: {cnpj_empresa}
        --------------------------------
        RECIBO DE VENDA #{numero_venda}
        
        Data: {data_venda}
        Operador: {nome_operador}
        
        ================================
        ITENS:
        {itens_lista}
        ================================
        
        Subtotal: R$ {subtotal}
        Desconto: R$ {desconto}
        TOTAL: R$ {total}
        
        Forma Pagamento: {forma_pagamento}
        
        --------------------------------
        Obrigado pela preferência!
        {mensagem_rodape}
        """
        
        # Template padrão para pedido de cozinha
        template_cozinha = """
        *** PEDIDO COZINHA ***
        
        Mesa/Comanda: {mesa_comanda}
        Pedido #{numero_pedido}
        {data_hora}
        
        Operador: {operador}
        
        ========================
        {itens_cozinha}
        ========================
        
        OBS: {observacoes}
        
        >>> PREPARAR AGORA <<<
        """
        
        sql_templates = """
        INSERT INTO print_templates (nome, tipo_job, template_esc_pos, evento_id, variaveis, configuracoes)
        VALUES 
        ('Recibo Padrão', 'RECIBO_CAIXA', %(template_recibo)s, 1, 
         '["nome_empresa", "endereco_empresa", "cnpj_empresa", "numero_venda", "data_venda", "nome_operador", "itens_lista", "subtotal", "desconto", "total", "forma_pagamento", "mensagem_rodape"]'::jsonb,
         '{"margem_superior": 2, "margem_inferior": 3, "corte_automatico": true}'::jsonb),
        ('Pedido Cozinha Padrão', 'PEDIDO_COZINHA', %(template_cozinha)s, 1,
         '["mesa_comanda", "numero_pedido", "data_hora", "operador", "itens_cozinha", "observacoes"]'::jsonb,
         '{"margem_superior": 1, "margem_inferior": 2, "corte_automatico": true, "som_alerta": true}'::jsonb)
        ON CONFLICT DO NOTHING;
        """
        
        try:
            with self.engine.connect() as conn:
                conn.execute(text(sql_templates), {
                    'template_recibo': template_recibo.strip(),
                    'template_cozinha': template_cozinha.strip()
                })
                conn.commit()
            
            self._log_etapa(
                "Dados Iniciais",
                True,
                "Templates padrão inseridos"
            )
            return True
            
        except Exception as e:
            self._log_etapa(
                "Dados Iniciais",
                False,
                f"Erro: {str(e)}"
            )
            return False
    
    def executar_migracoes(self):
        """Executar todas as migrações"""
        logger.info("🚀 Iniciando migração do sistema de impressoras térmicas")
        
        etapas = [
            ("Verificar Conexão", self.verificar_conexao),
            ("Verificar Tabelas Existentes", self.verificar_tabelas_existentes),
            ("Criar Enums", self.criar_enums),
            ("Criar Tabela Impressoras", self.criar_tabela_impressoras),
            ("Criar Tabela Print Templates", self.criar_tabela_print_templates),
            ("Criar Tabela Print Jobs", self.criar_tabela_print_jobs),
            ("Criar Tabela Print Job Logs", self.criar_tabela_print_job_logs),
            ("Inserir Dados Iniciais", self.inserir_dados_iniciais)
        ]
        
        todas_sucessos = True
        
        for nome_etapa, funcao in etapas:
            try:
                logger.info(f"Executando: {nome_etapa}")
                resultado = funcao()
                if resultado is False:
                    todas_sucessos = False
                    logger.error(f"Falha em: {nome_etapa}")
                    break
            except Exception as e:
                logger.error(f"Erro crítico em {nome_etapa}: {str(e)}")
                logger.error(traceback.format_exc())
                todas_sucessos = False
                break
        
        self.migration_log["fim"] = datetime.now()
        self.migration_log["sucesso"] = todas_sucessos
        self.migration_log["duracao"] = (
            self.migration_log["fim"] - self.migration_log["inicio"]
        ).total_seconds()
        
        return todas_sucessos
    
    def gerar_relatorio(self):
        """Gerar relatório da migração"""
        filename = f"migration_printer_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                # Converter datetime para string para JSON
                log_copy = self.migration_log.copy()
                for key in ['inicio', 'fim']:
                    if key in log_copy:
                        log_copy[key] = log_copy[key].isoformat()
                
                for etapa in log_copy['etapas']:
                    if 'timestamp' in etapa:
                        etapa['timestamp'] = etapa['timestamp'].isoformat()
                
                json.dump(log_copy, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Relatório da migração salvo em: {filename}")
            return filename
            
        except Exception as e:
            logger.error(f"Erro ao gerar relatório: {str(e)}")
            return None

def main():
    """Função principal"""
    try:
        migrator = PrinterMigration()
        sucesso = migrator.executar_migracoes()
        
        if sucesso:
            logger.info("✅ Migração do sistema de impressoras concluída com sucesso!")
        else:
            logger.error("❌ Migração falhou. Verifique os logs acima.")
            exit(1)
        
        # Gerar relatório
        relatorio = migrator.gerar_relatorio()
        if relatorio:
            logger.info(f"📊 Relatório gerado: {relatorio}")
        
        return sucesso
        
    except Exception as e:
        logger.error(f"❌ Erro crítico na migração: {str(e)}")
        logger.error(traceback.format_exc())
        exit(1)

if __name__ == "__main__":
    main()
