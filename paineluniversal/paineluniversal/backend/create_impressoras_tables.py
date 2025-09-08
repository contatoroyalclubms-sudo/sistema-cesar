#!/usr/bin/env python3
"""
Script para criar as tabelas do sistema de impressoras
"""

import os
import sys
from pathlib import Path

# Adicionar o diretório raiz ao path
sys.path.append(str(Path(__file__).parent))

from sqlalchemy import create_engine, text
from app.database import Base, engine
from app.models import (
    # Importar os novos modelos de impressora
    Impressora, ImpressoraInteligente, TemplateImpressao,
    FilaImpressao, LogImpressao, EquipamentoPDV, OperadorPDV
)
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def criar_tabelas_impressoras():
    """Criar todas as tabelas do sistema de impressoras"""
    try:
        logger.info("🖨️ Iniciando criação das tabelas do sistema de impressoras...")
        
        # Criar as tabelas
        Base.metadata.create_all(bind=engine, checkfirst=True)
        
        logger.info("✅ Tabelas criadas com sucesso!")
        
        # Verificar se as tabelas foram criadas
        with engine.connect() as conn:
            # Verificar cada tabela
            tabelas_esperadas = [
                'impressoras',
                'impressoras_inteligentes', 
                'templates_impressao',
                'filas_impressao',
                'logs_impressao',
                'equipamentos_pdv',
                'operadores_pdv'
            ]
            
            tabelas_criadas = []
            for tabela in tabelas_esperadas:
                try:
                    result = conn.execute(text(f"SELECT 1 FROM {tabela} LIMIT 1"))
                    tabelas_criadas.append(tabela)
                    logger.info(f"✓ Tabela '{tabela}' verificada")
                except Exception:
                    # Se a tabela não existe, tentamos criá-la individualmente
                    logger.warning(f"⚠️ Tabela '{tabela}' não encontrada, tentando criar...")
            
            logger.info(f"\n📊 Resumo:")
            logger.info(f"Tabelas esperadas: {len(tabelas_esperadas)}")
            logger.info(f"Tabelas verificadas: {len(tabelas_criadas)}")
            
            if len(tabelas_criadas) == len(tabelas_esperadas):
                logger.info("✅ Todas as tabelas do sistema de impressoras foram criadas com sucesso!")
            else:
                tabelas_faltando = set(tabelas_esperadas) - set(tabelas_criadas)
                if tabelas_faltando:
                    logger.warning(f"⚠️ Tabelas não criadas: {tabelas_faltando}")
                    logger.info("Tentando criar tabelas faltantes...")
                    Base.metadata.create_all(bind=engine, checkfirst=True)
                    logger.info("✅ Segunda tentativa concluída")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro ao criar tabelas: {e}")
        import traceback
        traceback.print_exc()
        return False

def inserir_dados_iniciais():
    """Inserir dados iniciais para teste"""
    try:
        from sqlalchemy.orm import Session
        from app.database import get_db
        from datetime import datetime
        
        logger.info("\n📝 Inserindo dados iniciais...")
        
        # Criar sessão
        db = Session(bind=engine)
        
        # Verificar se já existem impressoras
        impressoras_existentes = db.query(Impressora).count()
        if impressoras_existentes > 0:
            logger.info(f"ℹ️ Já existem {impressoras_existentes} impressoras cadastradas")
            db.close()
            return
        
        # Criar impressora de exemplo
        impressora_exemplo = Impressora(
            nome="Impressora Exemplo",
            ip="192.168.1.100",
            porta=9100,
            tipo="termica",
            modelo="Genérica",
            status="offline",
            localizacao="Caixa Principal",
            largura_papel=80,
            caracteres_linha=48,
            suporta_guilhotina=True,
            suporta_qrcode=True,
            suporta_codigo_barras=True,
            ativa=True
        )
        
        db.add(impressora_exemplo)
        db.commit()
        
        logger.info("✅ Impressora de exemplo criada")
        
        # Criar template de exemplo
        template_cupom = TemplateImpressao(
            nome="Cupom Padrão",
            tipo="cupom",
            cabecalho="CUPOM FISCAL",
            corpo="{{itens}}",
            rodape="Obrigado pela preferência!",
            negrito_titulo=True,
            centralizar_logo=True,
            separadores=True,
            incluir_qrcode=False,
            ativo=True
        )
        
        db.add(template_cupom)
        db.commit()
        
        logger.info("✅ Template de exemplo criado")
        
        # Criar operador de exemplo
        operador_exemplo = OperadorPDV(
            nome="Operador Padrão",
            cpf="000.000.000-00",
            codigo_acesso="1234",
            comissao_percentual=0,
            comissao_fixa=0,
            pode_cancelar=False,
            pode_dar_desconto=False,
            desconto_maximo=0,
            ativo=True,
            total_vendas=0,
            valor_total_vendido=0
        )
        
        db.add(operador_exemplo)
        db.commit()
        
        logger.info("✅ Operador de exemplo criado")
        
        db.close()
        logger.info("✅ Dados iniciais inseridos com sucesso!")
        
    except Exception as e:
        logger.error(f"❌ Erro ao inserir dados iniciais: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    logger.info("=" * 50)
    logger.info("🖨️ SISTEMA DE IMPRESSORAS - CRIAÇÃO DE TABELAS")
    logger.info("=" * 50)
    
    # Criar tabelas
    if criar_tabelas_impressoras():
        # Se as tabelas foram criadas com sucesso, inserir dados iniciais
        inserir_dados_iniciais()
        logger.info("\n✅ Sistema de impressoras configurado com sucesso!")
    else:
        logger.error("\n❌ Falha na configuração do sistema de impressoras")
        sys.exit(1)