#!/usr/bin/env python3
"""
Criar dados de teste para o sistema de ranking e gamificação
"""
import sys
sys.path.append('backend')

from backend.app.database import get_db
from backend.app.models import Usuario, Evento, Lista, Transacao, Checkin, Conquista, TipoConquista, NivelBadge, TipoLista, StatusTransacao
from backend.app.auth_functions import gerar_hash_senha
from sqlalchemy.orm import Session
from datetime import datetime, date, timedelta
from decimal import Decimal
import random

def create_test_promoters():
    """Criar promoters de teste"""
    db = next(get_db())
    try:
        # Criar 5 promoters de teste
        promoters = [
            {
                "cpf": "12345678901",
                "nome": "Carlos Silva",
                "email": "carlos@promoter.com",
                "telefone": "(11) 99999-1111",
                "tipo": "promoter"
            },
            {
                "cpf": "23456789012", 
                "nome": "Ana Santos",
                "email": "ana@promoter.com",
                "telefone": "(11) 99999-2222",
                "tipo": "promoter"
            },
            {
                "cpf": "34567890123",
                "nome": "Pedro Costa",
                "email": "pedro@promoter.com", 
                "telefone": "(11) 99999-3333",
                "tipo": "promoter"
            },
            {
                "cpf": "45678901234",
                "nome": "Maria Oliveira",
                "email": "maria@promoter.com",
                "telefone": "(11) 99999-4444", 
                "tipo": "promoter"
            },
            {
                "cpf": "56789012345",
                "nome": "João Pereira",
                "email": "joao@promoter.com",
                "telefone": "(11) 99999-5555",
                "tipo": "promoter"
            }
        ]
        
        created_promoters = []
        
        for promoter_data in promoters:
            # Verificar se já existe
            existing = db.query(Usuario).filter(Usuario.cpf == promoter_data["cpf"]).first()
            if existing:
                print(f"👤 Promoter {promoter_data['nome']} já existe")
                created_promoters.append(existing)
                continue
                
            promoter = Usuario(
                cpf=promoter_data["cpf"],
                nome=promoter_data["nome"],
                email=promoter_data["email"],
                telefone=promoter_data["telefone"],
                senha_hash=gerar_hash_senha("123456"),  # Senha padrão
                tipo=promoter_data["tipo"],
                ativo=True
            )
            
            db.add(promoter)
            created_promoters.append(promoter)
            print(f"✅ Criado promoter: {promoter_data['nome']}")
        
        db.commit()
        
        # Buscar eventos existentes
        eventos = db.query(Evento).limit(3).all()
        if not eventos:
            print("❌ Não há eventos para criar listas")
            return
            
        # Criar listas para cada promoter em diferentes eventos
        for i, promoter in enumerate(created_promoters):
            for j, evento in enumerate(eventos[:2]):  # Máximo 2 eventos por promoter
                lista = Lista(
                    nome=f"Lista {promoter.nome} - {evento.nome[:15]}",
                    descricao=f"Lista promocional do {promoter.nome}",
                    promoter_id=promoter.id,
                    evento_id=evento.id,
                    ativa=True,
                    limite_vendas=100,
                    tipo=TipoLista.FREE,
                    preco=Decimal('0.00')
                )
                db.add(lista)
                print(f"📋 Criada lista para {promoter.nome} no evento {evento.nome}")
        
        db.commit()
        
        # Buscar listas criadas
        listas = db.query(Lista).filter(Lista.promoter_id.in_([p.id for p in created_promoters])).all()
        
        # Criar transações de teste
        cpfs_teste = [
            "98765432100", "87654321099", "76543210988", "65432109877", "54321098766",
            "43210987655", "32109876544", "21098765433", "10987654322", "09876543211"
        ]
        
        for lista in listas:
            # 5-15 transações por lista
            num_transacoes = random.randint(5, 15)
            
            for i in range(num_transacoes):
                transacao = Transacao(
                    lista_id=lista.id,
                    evento_id=lista.evento_id,
                    cpf_comprador=random.choice(cpfs_teste),
                    nome_comprador=f"Cliente {i+1}",
                    valor=Decimal(random.randint(50, 300)),
                    status=StatusTransacao.APROVADA,
                    criado_em=datetime.now() - timedelta(days=random.randint(1, 30))
                )
                db.add(transacao)
                
                # 70% de chance de ter check-in
                if random.random() < 0.7:
                    checkin = Checkin(
                        evento_id=lista.evento_id,
                        cpf=transacao.cpf_comprador,
                        nome=transacao.nome_comprador,
                        checkin_em=transacao.criado_em + timedelta(hours=random.randint(1, 24)),
                        usuario_id=1  # Admin que fez o checkin
                    )
                    db.add(checkin)
        
        db.commit()
        
        # Criar conquistas básicas
        conquistas_basicas = [
            {
                "nome": "Primeira Venda",
                "descricao": "Realize sua primeira venda",
                "tipo": TipoConquista.VENDAS,
                "criterio_valor": 1,
                "badge_nivel": NivelBadge.BRONZE,
                "icone": "🎯"
            },
            {
                "nome": "Vendedor Bronze",
                "descricao": "Realize 10 vendas",
                "tipo": TipoConquista.VENDAS, 
                "criterio_valor": 10,
                "badge_nivel": NivelBadge.BRONZE,
                "icone": "🥉"
            },
            {
                "nome": "Vendedor Prata",
                "descricao": "Realize 50 vendas",
                "tipo": TipoConquista.VENDAS,
                "criterio_valor": 50,
                "badge_nivel": NivelBadge.PRATA,
                "icone": "🥈"
            },
            {
                "nome": "Vendedor Ouro",
                "descricao": "Realize 100 vendas",
                "tipo": TipoConquista.VENDAS,
                "criterio_valor": 100,
                "badge_nivel": NivelBadge.OURO,
                "icone": "🥇"
            },
            {
                "nome": "Especialista em Presença",
                "descricao": "Mantenha 80% de taxa de presença",
                "tipo": TipoConquista.PRESENCA,
                "criterio_valor": 80,
                "badge_nivel": NivelBadge.PRATA,
                "icone": "✅"
            }
        ]
        
        for conquista_data in conquistas_basicas:
            existing = db.query(Conquista).filter(Conquista.nome == conquista_data["nome"]).first()
            if existing:
                print(f"🏆 Conquista {conquista_data['nome']} já existe")
                continue
                
            conquista = Conquista(**conquista_data)
            db.add(conquista)
            print(f"✅ Criada conquista: {conquista_data['nome']}")
        
        db.commit()
        
        print("\n" + "="*50)
        print("🎉 DADOS DE TESTE CRIADOS COM SUCESSO!")
        print("👤 5 promoters criados")
        print("📋 Listas criadas para cada promoter")
        print("💰 Transações geradas (5-15 por lista)")
        print("✅ Check-ins simulados (70% taxa)")
        print("🏆 5 conquistas básicas criadas")
        print("="*50)
        
    except Exception as e:
        print(f"❌ Erro ao criar dados: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_test_promoters()
