#!/usr/bin/env python3

"""Script para criar empresa padrão se não existir"""

import os
import sys

# Adicionar o diretório do projeto ao path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

try:
    from app.database import SessionLocal, engine
    from app.models import Base, Empresa
    from sqlalchemy.exc import IntegrityError
    
    # Criar tabelas se não existirem
    Base.metadata.create_all(bind=engine)
    
    def seed_empresa():
        db = SessionLocal()
        try:
            # Verificar se já existe alguma empresa
            empresa_existente = db.query(Empresa).first()
            
            if empresa_existente:
                print(f"✅ Empresa já existe: {empresa_existente.nome} (ID: {empresa_existente.id})")
                return empresa_existente
            
            # Criar empresa padrão
            empresa_padrao = Empresa(
                nome="Painel Universal",
                cnpj="00000000000100",
                email="contato@paineluniversal.com",
                telefone="(11) 99999-9999",
                endereco="Endereço padrão",
                ativa=True
            )
            
            db.add(empresa_padrao)
            db.commit()
            db.refresh(empresa_padrao)
            
            print(f"🏢 Empresa padrão criada: {empresa_padrao.nome} (ID: {empresa_padrao.id})")
            return empresa_padrao
            
        except IntegrityError as e:
            db.rollback()
            print(f"⚠️ Erro de integridade (empresa pode já existir): {e}")
            # Tentar buscar empresa existente
            empresa = db.query(Empresa).first()
            if empresa:
                print(f"🔍 Empresa encontrada: {empresa.nome} (ID: {empresa.id})")
                return empresa
        except Exception as e:
            db.rollback()
            print(f"❌ Erro ao criar empresa: {e}")
            import traceback
            traceback.print_exc()
        finally:
            db.close()
    
    if __name__ == "__main__":
        print("🚀 Executando seed de empresa...")
        seed_empresa()
        print("✅ Seed concluído!")
        
except ImportError as e:
    print(f"❌ Erro de importação: {e}")
    print("Verifique se todas as dependências estão instaladas")
except Exception as e:
    print(f"💥 Erro inesperado: {e}")
    import traceback
    traceback.print_exc()
