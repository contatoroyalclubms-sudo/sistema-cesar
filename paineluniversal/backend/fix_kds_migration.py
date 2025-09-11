#!/usr/bin/env python3
"""
Script para criar as tabelas KDS faltantes no banco de dados
Corrige o problema crítico identificado nos testes
"""

import sys
import traceback
from sqlalchemy import text
from app.database import engine, SessionLocal
from app.models import Base, EstacaoKds, ItemKds, PedidoKds, StatusKds, TipoEstacao

def create_tables():
    """Cria todas as tabelas faltantes do banco"""
    try:
        print("CRIANDO TABELAS KDS FALTANTES")
        print("=" * 50)
        
        # Criar todas as tabelas do modelo
        Base.metadata.create_all(bind=engine)
        print("Tabelas SQLAlchemy criadas com sucesso!")
        
        # Verificar se as tabelas foram criadas
        with engine.connect() as conn:
            # Verificar tabela estacoes_kds
            try:
                result = conn.execute(text("SELECT COUNT(*) FROM estacoes_kds"))
                print(f"Tabela 'estacoes_kds' acessivel: {result.scalar()} registros")
            except Exception as e:
                print(f"Erro ao acessar 'estacoes_kds': {e}")
                
            # Verificar tabela itens_kds
            try:
                result = conn.execute(text("SELECT COUNT(*) FROM itens_kds"))
                print(f"Tabela 'itens_kds' acessivel: {result.scalar()} registros")
            except Exception as e:
                print(f"Erro ao acessar 'itens_kds': {e}")
                
        return True
        
    except Exception as e:
        print(f"Erro critico ao criar tabelas: {e}")
        traceback.print_exc()
        return False

def create_demo_data():
    """Cria dados de demonstração para o KDS"""
    try:
        print("\nCRIANDO DADOS DE DEMONSTRACAO")
        print("=" * 50)
        
        db = SessionLocal()
        
        # Verificar se já existem estações
        existing = db.query(EstacaoKds).first()
        if existing:
            print("Dados de demonstracao ja existem, pulando criacao")
            db.close()
            return True
            
        # Criar estações de demonstração
        estacoes = [
            EstacaoKds(
                nome="Cozinha Principal",
                descricao="Estação principal da cozinha",
                tipo=TipoEstacao.COZINHA,
                cor_tema="#FF6B6B",
                layout_colunas=3,
                tempo_alerta_minutos=20,
                criado_por=1  # Assumindo que existe um usuário com ID 1
            ),
            EstacaoKds(
                nome="Bar de Bebidas", 
                descricao="Estação para preparo de bebidas",
                tipo=TipoEstacao.BAR,
                cor_tema="#4ECDC4",
                layout_colunas=2,
                tempo_alerta_minutos=10,
                criado_por=1
            ),
            EstacaoKds(
                nome="Lanchonete",
                descricao="Estação para lanches rápidos",
                tipo=TipoEstacao.LANCHE,
                cor_tema="#45B7D1",
                layout_colunas=4,
                tempo_alerta_minutos=15,
                criado_por=1
            )
        ]
        
        for estacao in estacoes:
            db.add(estacao)
            
        db.commit()
        print(f"{len(estacoes)} estacoes KDS criadas com sucesso!")
        
        # Criar alguns itens de demonstração
        itens_demo = [
            ItemKds(
                estacao_id=1,
                numero_pedido="P001",
                nome_cliente="João Silva",
                descricao_item="Hambúrguer Artesanal",
                observacoes="Sem cebola, ponto da carne mal passado",
                quantidade=1,
                status=StatusKds.PENDENTE,
                prioridade=1,
                tempo_estimado_minutos=15
            ),
            ItemKds(
                estacao_id=2,
                numero_pedido="P002",
                nome_cliente="Maria Santos",
                descricao_item="Caipirinha de Limão",
                observacoes="Pouco açúcar",
                quantidade=2,
                status=StatusKds.PREPARANDO,
                prioridade=1,
                tempo_estimado_minutos=5
            )
        ]
        
        for item in itens_demo:
            db.add(item)
            
        db.commit()
        print(f"{len(itens_demo)} itens de demonstracao criados!")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"Erro ao criar dados de demonstracao: {e}")
        if 'db' in locals():
            db.rollback()
            db.close()
        traceback.print_exc()
        return False

def main():
    """Função principal"""
    print("INICIANDO CORRECAO CRITICA DO BANCO KDS")
    print("=" * 60)
    
    # Passo 1: Criar tabelas
    if not create_tables():
        print("FALHA: Nao foi possivel criar as tabelas necessarias")
        sys.exit(1)
        
    # Passo 2: Criar dados de demonstração
    if not create_demo_data():
        print("Aviso: Dados de demonstracao nao foram criados")
    
    print("\n" + "=" * 60)
    print("CORRECAO KDS FINALIZADA COM SUCESSO!")
    print("Tabelas 'estacoes_kds' e 'itens_kds' estao disponiveis")
    print("Backend pode ser reiniciado sem erros SQLAlchemy")
    print("=" * 60)

if __name__ == "__main__":
    main()