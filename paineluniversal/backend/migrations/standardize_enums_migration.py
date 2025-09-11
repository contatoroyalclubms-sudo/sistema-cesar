"""
Migration para padronizar todos os enums do sistema
Data: 05/01/2025
"""

import os
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.database import DATABASE_URL
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_database_url():
    """Obtém a URL do banco de dados"""
    return DATABASE_URL or os.getenv("DATABASE_URL", "sqlite:///./eventos.db")

def standardize_enums():
    """Padroniza todos os enums do banco de dados"""
    
    engine = create_engine(get_database_url())
    
    migrations = [
        # StatusEvento: minúsculo -> MAIÚSCULO
        {
            'table': 'eventos',
            'column': 'status',
            'conversions': [
                ('ativo', 'ATIVO'),
                ('inativo', 'INATIVO'),
                ('cancelado', 'CANCELADO'),
                ('finalizado', 'FINALIZADO'),
            ]
        },
        
        # TipoLista: minúsculo -> MAIÚSCULO
        {
            'table': 'listas',
            'column': 'tipo',
            'conversions': [
                ('vip', 'VIP'),
                ('free', 'FREE'),
                ('pagante', 'PAGANTE'),
                ('promoter', 'PROMOTER'),
                ('aniversario', 'ANIVERSARIO'),
                ('desconto', 'DESCONTO'),
                ('premium', 'PREMIUM'),
                ('comum', 'COMUM'),
            ]
        },
        
        # StatusTransacao: minúsculo -> MAIÚSCULO
        {
            'table': 'transacoes',
            'column': 'status',
            'conversions': [
                ('pendente', 'PENDENTE'),
                ('aprovada', 'APROVADA'),
                ('cancelada', 'CANCELADA'),
                ('estornada', 'ESTORNADA'),
            ]
        },
        
        # TipoProduto: já está em MAIÚSCULO no banco
        # StatusProduto: já está em MAIÚSCULO no banco
        
        # TipoComanda: minúsculo -> MAIÚSCULO
        {
            'table': 'comandas',
            'column': 'tipo',
            'conversions': [
                ('fisica', 'FISICA'),
                ('virtual', 'VIRTUAL'),
                ('rfid', 'RFID'),
                ('nfc', 'NFC'),
                ('qr_code', 'QR_CODE'),
            ]
        },
        
        # StatusComanda: já está em MAIÚSCULO no banco
        
        # StatusVendaPDV: já está em MAIÚSCULO no banco
        
        # TipoPagamentoPDV: já está em MAIÚSCULO no banco
        
        # TipoMovimentacaoFinanceira: minúsculo -> MAIÚSCULO
        {
            'table': 'movimentacoes_financeiras',
            'column': 'tipo',
            'conversions': [
                ('entrada', 'ENTRADA'),
                ('saida', 'SAIDA'),
                ('ajuste', 'AJUSTE'),
                ('repasse_promoter', 'REPASSE_PROMOTER'),
                ('receita_vendas', 'RECEITA_VENDAS'),
                ('receita_listas', 'RECEITA_LISTAS'),
            ]
        },
        
        # StatusMovimentacaoFinanceira: minúsculo -> MAIÚSCULO
        {
            'table': 'movimentacoes_financeiras',
            'column': 'status',
            'conversions': [
                ('pendente', 'PENDENTE'),
                ('aprovada', 'APROVADA'),
                ('cancelada', 'CANCELADA'),
            ]
        },
        
        # TipoConquista: minúsculo -> MAIÚSCULO
        {
            'table': 'conquistas',
            'column': 'tipo',
            'conversions': [
                ('vendas', 'VENDAS'),
                ('presenca', 'PRESENCA'),
                ('fidelidade', 'FIDELIDADE'),
                ('crescimento', 'CRESCIMENTO'),
                ('especial', 'ESPECIAL'),
            ]
        },
        
        # NivelBadge: minúsculo -> MAIÚSCULO
        {
            'table': 'conquistas',
            'column': 'badge_nivel',
            'conversions': [
                ('bronze', 'BRONZE'),
                ('prata', 'PRATA'),
                ('ouro', 'OURO'),
                ('platina', 'PLATINA'),
                ('diamante', 'DIAMANTE'),
                ('lenda', 'LENDA'),
            ]
        },
        
        # TipoImpressora: minúsculo -> MAIÚSCULO
        {
            'table': 'impressoras',
            'column': 'tipo',
            'conversions': [
                ('cozinha', 'COZINHA'),
                ('bar', 'BAR'),
                ('sobremesa', 'SOBREMESA'),
                ('caixa', 'CAIXA'),
                ('gerencial', 'GERENCIAL'),
            ]
        },
        
        # InterfaceImpressora: minúsculo -> MAIÚSCULO
        {
            'table': 'impressoras',
            'column': 'interface',
            'conversions': [
                ('usb', 'USB'),
                ('network', 'NETWORK'),
                ('bluetooth', 'BLUETOOTH'),
            ]
        },
        
        # StatusImpressora: minúsculo -> MAIÚSCULO
        {
            'table': 'impressoras',
            'column': 'status',
            'conversions': [
                ('online', 'ONLINE'),
                ('offline', 'OFFLINE'),
                ('erro', 'ERRO'),
                ('manutencao', 'MANUTENCAO'),
            ]
        },
    ]
    
    with engine.connect() as conn:
        for migration in migrations:
            table = migration['table']
            column = migration['column']
            
            # Verificar se a tabela existe
            check_table = text(f"""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name=:table_name
            """)
            
            result = conn.execute(check_table, {"table_name": table}).fetchone()
            
            if not result:
                logger.warning(f"Tabela '{table}' não encontrada, pulando...")
                continue
            
            # Aplicar conversões
            for old_value, new_value in migration['conversions']:
                update_query = text(f"""
                    UPDATE {table}
                    SET {column} = :new_value
                    WHERE {column} = :old_value
                """)
                
                result = conn.execute(update_query, {
                    "new_value": new_value,
                    "old_value": old_value
                })
                
                if result.rowcount > 0:
                    logger.info(f"✅ {table}.{column}: Convertido {result.rowcount} registros de '{old_value}' para '{new_value}'")
        
        conn.commit()
        logger.info("🎉 Migration de padronização de enums concluída com sucesso!")

def rollback_enums():
    """Reverte a padronização dos enums (rollback)"""
    
    engine = create_engine(get_database_url())
    
    rollbacks = [
        # StatusEvento: MAIÚSCULO -> minúsculo
        {
            'table': 'eventos',
            'column': 'status',
            'conversions': [
                ('ATIVO', 'ativo'),
                ('INATIVO', 'inativo'),
                ('CANCELADO', 'cancelado'),
                ('FINALIZADO', 'finalizado'),
            ]
        },
        # Adicionar outros rollbacks conforme necessário...
    ]
    
    with engine.connect() as conn:
        for rollback in rollbacks:
            table = rollback['table']
            column = rollback['column']
            
            for old_value, new_value in rollback['conversions']:
                update_query = text(f"""
                    UPDATE {table}
                    SET {column} = :new_value
                    WHERE {column} = :old_value
                """)
                
                result = conn.execute(update_query, {
                    "new_value": new_value,
                    "old_value": old_value
                })
                
                if result.rowcount > 0:
                    logger.info(f"↩️ {table}.{column}: Revertido {result.rowcount} registros de '{old_value}' para '{new_value}'")
        
        conn.commit()
        logger.info("✅ Rollback concluído!")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "rollback":
        print("🔄 Executando ROLLBACK da padronização de enums...")
        rollback_enums()
    else:
        print("🔧 Executando padronização de enums...")
        standardize_enums()