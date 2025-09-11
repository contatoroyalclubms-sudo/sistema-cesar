#!/usr/bin/env python3
"""
Criar dados simples para testar ranking
"""
import sys
sys.path.append('backend')

from backend.app.database import get_db
from backend.app.models import Usuario, Evento, Lista, Transacao, Checkin, TipoLista, StatusTransacao
from backend.app.auth_functions import gerar_hash_senha
from sqlalchemy.orm import Session
from datetime import datetime, date, timedelta
from decimal import Decimal
import random

def create_simple_ranking_data():
    """Criar dados simples para ranking"""
    db = next(get_db())
    try:
        print("🚀 Criando dados simples para ranking...")
        
        # Verificar dados existentes
        promoters = db.query(Usuario).filter(Usuario.tipo == "promoter").all()
        print(f"👤 Promoters existentes: {len(promoters)}")
        
        if len(promoters) == 0:
            print("❌ Não há promoters. Vou criar alguns básicos.")
            return
            
        # Buscar eventos
        eventos = db.query(Evento).limit(2).all()
        print(f"🎉 Eventos disponíveis: {len(eventos)}")
        
        # Buscar listas dos promoters
        listas = db.query(Lista).filter(Lista.promoter_id.in_([p.id for p in promoters])).all()
        print(f"📋 Listas existentes: {len(listas)}")
        
        if len(listas) == 0:
            print("❌ Não há listas. Ranking precisa de listas.")
            return
            
        # Criar transações simples
        cpfs_teste = [
            "11111111111", "22222222222", "33333333333", "44444444444", "55555555555"
        ]
        
        transacao_count = 0
        checkin_count = 0
        
        for lista in listas[:5]:  # Máximo 5 listas
            # 3-8 transações por lista
            num_transacoes = random.randint(3, 8)
            
            for i in range(num_transacoes):
                cpf = random.choice(cpfs_teste)
                
                transacao = Transacao(
                    lista_id=lista.id,
                    evento_id=lista.evento_id,
                    cpf_comprador=cpf,
                    nome_comprador=f"Cliente Teste {i+1}",
                    valor=Decimal(random.randint(50, 200)),
                    status=StatusTransacao.APROVADA,
                    criado_em=datetime.now() - timedelta(days=random.randint(1, 15))
                )
                db.add(transacao)
                transacao_count += 1
                
                # 60% chance de check-in
                if random.random() < 0.6:
                    checkin = Checkin(
                        evento_id=lista.evento_id,
                        cpf=cpf,
                        nome=f"Cliente Teste {i+1}",
                        checkin_em=transacao.criado_em + timedelta(hours=random.randint(1, 12)),
                        usuario_id=1  # Admin
                    )
                    db.add(checkin)
                    checkin_count += 1
        
        db.commit()
        
        print(f"✅ Criadas {transacao_count} transações")
        print(f"✅ Criados {checkin_count} check-ins")
        print("🎉 Dados básicos criados! Testando ranking...")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_simple_ranking_data()
