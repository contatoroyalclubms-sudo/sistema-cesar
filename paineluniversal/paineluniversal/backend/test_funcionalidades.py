#!/usr/bin/env python3
"""
Teste completo das funcionalidades de cadastro do sistema
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import get_db
from app.models import Usuario, Empresa, Evento
from app.auth import gerar_hash_senha
from app.schemas import UsuarioCreate, EventoCreate
import uuid
from datetime import datetime, timezone, timedelta

def test_user_creation():
    """Testar criação de usuários"""
    print("\n=== TESTE: CRIACAO DE USUARIOS ===")
    
    db = next(get_db())
    
    try:
        # Teste 1: Criar usuário cliente
        email_unico = f"cliente_{uuid.uuid4().hex[:8]}@teste.com"
        cpf_unico = f"{uuid.uuid4().hex[:11]}"[:11]
        
        usuario_cliente = Usuario(
            cpf=cpf_unico,
            nome="Cliente Teste",
            email=email_unico,
            telefone="11999999999",
            senha_hash=gerar_hash_senha("cliente123"),
            tipo="cliente",
            ativo=True
        )
        
        db.add(usuario_cliente)
        db.commit()
        db.refresh(usuario_cliente)
        
        print(f"OK Cliente criado: ID {usuario_cliente.id}")
        
        # Teste 2: Criar usuário promoter
        email_promoter = f"promoter_{uuid.uuid4().hex[:8]}@teste.com"
        cpf_promoter = f"{uuid.uuid4().hex[:11]}"[:11]
        
        usuario_promoter = Usuario(
            cpf=cpf_promoter,
            nome="Promoter Teste",
            email=email_promoter,
            telefone="11888888888",
            senha_hash=gerar_hash_senha("promoter123"),
            tipo="promoter",
            ativo=True
        )
        
        db.add(usuario_promoter)
        db.commit()
        db.refresh(usuario_promoter)
        
        print(f"OK Promoter criado: ID {usuario_promoter.id}")
        
        # Teste 3: Verificar se podem fazer login (autenticar)
        from app.auth import autenticar_usuario
        
        auth_cliente = autenticar_usuario(cpf_unico, "cliente123", db)
        auth_promoter = autenticar_usuario(cpf_promoter, "promoter123", db)
        
        if auth_cliente:
            print("OK Autenticacao do cliente funcionando")
        else:
            print("ERRO Autenticacao do cliente falhou")
            
        if auth_promoter:
            print("OK Autenticacao do promoter funcionando")
        else:
            print("ERRO Autenticacao do promoter falhou")
        
        # Limpar testes
        db.delete(usuario_cliente)
        db.delete(usuario_promoter)
        db.commit()
        print("OK Usuarios de teste removidos")
        
    except Exception as e:
        print(f"ERRO no teste de usuarios: {e}")
        db.rollback()
    finally:
        db.close()

def test_event_creation():
    """Testar criação de eventos"""
    print("\n=== TESTE: CRIACAO DE EVENTOS ===")
    
    db = next(get_db())
    
    try:
        # Buscar um usuário admin/promoter existente para usar como criador
        criador = db.query(Usuario).filter(Usuario.tipo.in_(["admin".PROMOTER])).first()
        
        if not criador:
            print("✗ Nenhum usuário admin/promoter encontrado para teste")
            return
        
        # Buscar empresa existente
        empresa = db.query(Empresa).filter(Empresa.ativa == True).first()
        empresa_id = empresa.id if empresa else None
        
        # Criar evento de teste
        data_futura = datetime.now(timezone.utc) + timedelta(days=30)
        
        evento_teste = Evento(
            nome="Evento Teste",
            descricao="Descrição do evento teste",
            data_evento=data_futura,
            local="Local Teste",
            endereco="Endereço Teste, 123",
            limite_idade=18,
            capacidade_maxima=100,
            empresa_id=empresa_id,
            criador_id=criador.id
        )
        
        db.add(evento_teste)
        db.commit()
        db.refresh(evento_teste)
        
        print(f"OK Evento criado: ID {evento_teste.id}")
        print(f"  Nome: {evento_teste.nome}")
        print(f"  Data: {evento_teste.data_evento}")
        print(f"  Criador: {criador.nome}")
        print(f"  Empresa: {empresa.nome if empresa else 'N/A'}")
        
        # Limpar teste
        db.delete(evento_teste)
        db.commit()
        print("OK Evento de teste removido")
        
    except Exception as e:
        print(f"ERRO no teste de eventos: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

def test_admin_permissions():
    """Testar permissões de admin"""
    print("\n=== TESTE: PERMISSOES DE ADMIN ===")
    
    db = next(get_db())
    
    try:
        # Buscar usuário admin
        admin = db.query(Usuario).filter(Usuario.tipo == "admin").first()
        
        if admin:
            print(f"OK Admin encontrado: {admin.nome}")
            print(f"  CPF: {admin.cpf}")
            print(f"  Email: {admin.email}")
            print(f"  Ativo: {admin.ativo}")
            
            # Testar autenticação (assumindo senha padrão)
            from app.auth import autenticar_usuario
            
            # Tentar senhas comuns de admin
            senhas_teste = ["admin123", "123456", "admin"]
            autenticado = False
            
            for senha in senhas_teste:
                if autenticar_usuario(admin.cpf, senha, db):
                    print(f"OK Admin pode fazer login com senha: {senha}")
                    autenticado = True
                    break
            
            if not autenticado:
                print("AVISO Admin existe mas senha nao conhecida")
                
        else:
            print("ERRO Nenhum usuario admin encontrado")
            
    except Exception as e:
        print(f"ERRO no teste de admin: {e}")
    finally:
        db.close()

def test_database_state():
    """Verificar estado geral do banco"""
    print("\n=== TESTE: ESTADO DO BANCO ===")
    
    db = next(get_db())
    
    try:
        # Contar registros
        total_usuarios = db.query(Usuario).count()
        total_empresas = db.query(Empresa).count()
        total_eventos = db.query(Evento).count()
        
        print(f"Total de usuários: {total_usuarios}")
        print(f"Total de empresas: {total_empresas}")
        print(f"Total de eventos: {total_eventos}")
        
        # Verificar usuários por tipo
        admins = db.query(Usuario).filter(Usuario.tipo == "admin").count()
        promoters = db.query(Usuario).filter(Usuario.tipo == "promoter").count()
        clientes = db.query(Usuario).filter(Usuario.tipo == "cliente").count()
        
        print(f"  - Admins: {admins}")
        print(f"  - Promoters: {promoters}")
        print(f"  - Clientes: {clientes}")
        
        # Verificar usuários ativos
        usuarios_ativos = db.query(Usuario).filter(Usuario.ativo == True).count()
        print(f"  - Usuários ativos: {usuarios_ativos}")
        
    except Exception as e:
        print(f"ERRO ao verificar estado do banco: {e}")
    finally:
        db.close()

def main():
    """Executar todos os testes"""
    print("INICIANDO TESTES DE FUNCIONALIDADES DE CADASTRO")
    print("=" * 50)
    
    test_database_state()
    test_admin_permissions()
    test_user_creation()
    test_event_creation()
    
    print("\n" + "=" * 50)
    print("TESTES CONCLUIDOS")

if __name__ == "__main__":
    main()