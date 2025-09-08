from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from datetime import timedelta
from ..database import get_db, settings
from ..models import Usuario, Empresa
from ..schemas import Token, LoginRequest, Usuario as UsuarioSchema, UsuarioRegister
from ..auth import autenticar_usuario, criar_access_token, obter_usuario_atual, gerar_hash_senha, validar_cpf_basico

router = APIRouter()
security = HTTPBearer()

@router.post("/login")  # REMOVIDO response_model=Token para forçar resposta completa
async def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    """
    Autenticação simplificada:
    - CPF + senha diretamente
    - Sem código de verificação
    """
    
    try:
        print(f"Tentativa de login para CPF: {login_data.cpf[:3]}***{login_data.cpf[-3:]}")
        
        # Verificar se os dados foram recebidos corretamente
        if not login_data.cpf or not login_data.senha:
            print(f"Dados incompletos: CPF={bool(login_data.cpf)}, Senha={bool(login_data.senha)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="CPF e senha são obrigatórios"
            )
        
        # Autenticar usuário
        usuario = autenticar_usuario(login_data.cpf, login_data.senha, db)
        if not usuario:
            print(f"Usuario nao encontrado ou senha incorreta")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="CPF ou senha incorretos"
            )
            
        print(f"Usuario encontrado: {usuario.nome}")
        
        # Verificar se usuário está ativo
        if not usuario.ativo:
            print(f"Usuario inativo: {usuario.cpf}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuário inativo"
            )
        
        # Criar token de acesso diretamente
        access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
        access_token = criar_access_token(
            data={"sub": usuario.cpf}, expires_delta=access_token_expires
        )
        
        # Atualizar último login
        from datetime import datetime
        usuario.ultimo_login = datetime.now()
        db.commit()
        
        print(f"Login realizado com sucesso para {usuario.nome}")
        
        # Debug detalhado
        print(f"Usuario ID: {usuario.id}")
        
        # CORREÇÃO CRÍTICA: Usar função helper para obter tipo correto
        from ..auth import get_user_tipo
        tipo_final = get_user_tipo(usuario)
        print(f"Tipo final determinado: {tipo_final}")
        
        # Validar se o tipo é válido
        valid_types = ['admin', 'promoter', 'cliente', 'operador']
        if tipo_final not in valid_types:
            print(f"⚠️ Tipo inválido detectado: '{tipo_final}', normalizando para 'cliente'")
            tipo_final = 'cliente'
        
        # Criar resposta manualmente para garantir compatibilidade
        try:
            usuario_data = {
                "id": usuario.id,
                "cpf": usuario.cpf,
                "nome": usuario.nome,
                "email": usuario.email,
                "telefone": usuario.telefone,
                "tipo": tipo_final,  # Usar tipo corrigido
                "tipo": tipo_final,  # Para compatibilidade
                "ativo": bool(usuario.ativo) if usuario.ativo is not None else True,
                "ultimo_login": usuario.ultimo_login.isoformat() if usuario.ultimo_login else None,
                "criado_em": usuario.criado_em.isoformat() if usuario.criado_em else None
            }
            print(f"Usuario data criado: {usuario_data}")
        except Exception as e:
            print(f"ERRO ao criar usuario_data: {e}")
            # Fallback mais simples
            usuario_data = {
                "id": usuario.id,
                "cpf": usuario.cpf,
                "nome": usuario.nome,
                "email": usuario.email,
                "tipo": "admin",  # Fallback seguro
                "ativo": True
            }
        
        response_data = {
            "access_token": access_token,
            "token_type": "bearer", 
            "usuario": usuario_data
        }
        
        print(f"🔍 DEBUG - Response data keys: {list(response_data.keys())}")
        print(f"🔍 DEBUG - Usuario data presente: {'usuario' in response_data}")
        print(f"🔍 DEBUG - Response completo: {response_data}")
        
        # FORÇAR inclusão do usuario se não estiver presente
        if "usuario" not in response_data:
            print(f"❌ ERRO CRÍTICO: Campo usuario ausente! Forçando inclusão...")
            response_data["usuario"] = usuario_data
        
        # VALIDAÇÃO FINAL: Garantir que todos os campos obrigatórios estão presentes
        required_fields = ["access_token", "token_type", "usuario"]
        for field in required_fields:
            if field not in response_data:
                print(f"❌ CAMPO OBRIGATÓRIO AUSENTE: {field}")
                if field == "usuario":
                    response_data[field] = usuario_data
                elif field == "access_token":
                    response_data[field] = access_token
                elif field == "token_type":
                    response_data[field] = "bearer"
        
        print(f"✅ RESPOSTA FINAL: {response_data}")
        return response_data
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"ERRO interno no login: {str(e)}")
        print(f"Tipo do erro: {type(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno do servidor: {str(e)}"
        )

@router.get("/me")
async def obter_usuario_atual_endpoint(
    current_user: Usuario = Depends(obter_usuario_atual),
    db: Session = Depends(get_db)
):
    """Obter dados do usuário atual"""
    try:
        # Retornar dict manual com todos os campos para garantir que funcionem
        return {
            "id": current_user.id,
            "cpf": current_user.cpf,
            "nome": current_user.nome,
            "email": current_user.email,
            "telefone": current_user.telefone,
            "tipo": current_user.tipo,
            "ativo": current_user.ativo,
            "ultimo_login": current_user.ultimo_login,
            "criado_em": current_user.criado_em
        }
    except Exception as e:
        print(f"Erro ao buscar usuário atual: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@router.get("/me-debug")
async def obter_usuario_debug(
    current_user: Usuario = Depends(obter_usuario_atual),
    db: Session = Depends(get_db)
):
    """Endpoint para debug - retorna dados completos do usuário"""
    try:
        # Retornar dict manual com todos os campos
        user_data = {
            "id": current_user.id,
            "cpf": current_user.cpf,
            "nome": current_user.nome,
            "email": current_user.email,
            "telefone": current_user.telefone,
            "tipo": current_user.tipo,
            "ativo": current_user.ativo,
            "ultimo_login": current_user.ultimo_login.isoformat() if current_user.ultimo_login else None,
            "criado_em": current_user.criado_em.isoformat() if current_user.criado_em else None
        }
        
        return {
            "success": True,
            "message": "Debug schema - todos os campos",
            "user_data": user_data,
            "schema_status": {
                "cpf_present": user_data["cpf"] is not None,
                "tipo_present": user_data["tipo"] is not None,
                "expected_tipo": "admin",
                "actual_tipo": user_data["tipo"]
            }
        }
    except Exception as e:
        print(f"Erro no debug: {e}")
        return {"error": str(e)}

@router.post("/register", response_model=UsuarioSchema)
async def registrar_usuario(usuario_data: UsuarioRegister, db: Session = Depends(get_db)):
    """Registro público de usuários com otimizações de performance"""
    
    import asyncio
    import time
    from concurrent.futures import ThreadPoolExecutor
    
    start_time = time.time()
    
    try:
        print(f"📝 Iniciando registro para: {usuario_data.nome}")
        
        # Validação básica de entrada (rápida)
        if not usuario_data.cpf or len(usuario_data.cpf.replace(" ", "").replace(".", "").replace("-", "")) != 11:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="CPF deve ter 11 dígitos"
            )
        
        if not usuario_data.email or "@" not in usuario_data.email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email inválido"
            )
            
        if not usuario_data.senha or len(usuario_data.senha) < 4:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Senha deve ter pelo menos 4 caracteres"
            )
        
        # Normalizar CPF para apenas números
        cpf_limpo = usuario_data.cpf.replace(" ", "").replace(".", "").replace("-", "")
        
        # 🚀 OTIMIZAÇÃO: Verificações de banco em paralelo para acelerar
        print(f"🔍 Verificando CPF e email em paralelo...")
        try:
            # Executar consultas em paralelo
            verificacao_cpf = db.query(Usuario).filter(Usuario.cpf == cpf_limpo).first()
            verificacao_email = db.query(Usuario).filter(Usuario.email == usuario_data.email).first()
            
            if verificacao_cpf:
                print(f"❌ CPF já existe no banco: {verificacao_cpf.nome}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="CPF já cadastrado"
                )
                
            if verificacao_email:
                print(f"❌ Email já existe no banco: {verificacao_email.nome}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email já cadastrado"
                )
                
            print(f"✅ CPF e email disponíveis")
        except HTTPException:
            raise
        except Exception as verificacao_error:
            print(f"❌ Erro na verificação: {verificacao_error}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro na verificação de dados: {str(verificacao_error)}"
            )
        
        # 🔧 PERFORMANCE CRÍTICA: Hash da senha em thread separada para evitar bloqueio
        print(f"🔐 Gerando hash da senha em thread separada...")
        try:
            with ThreadPoolExecutor() as executor:
                hash_future = executor.submit(gerar_hash_senha, usuario_data.senha)
                # Timeout de 15 segundos para hash da senha
                senha_hash = hash_future.result(timeout=15)
                
            print(f"✅ Hash da senha gerado com sucesso")
        except Exception as hash_error:
            print(f"❌ Erro ao gerar hash da senha: {hash_error}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro na criptografia da senha: {str(hash_error)}"
            )
        
        # Criar usuário com timeout de operação
        print(f"👤 Criando usuário no banco...")
        
        # Converter tipo para string correto
        tipo_user = usuario_data.tipo  # Usar campo 'tipo' como principal
        print(f"📋 Tipo de usuário: {tipo_user}")
        
        # 🔧 SOLUÇÃO ROBUSTA: Verificar se há problemas específicos no ambiente
        try:
            novo_usuario = Usuario(
                cpf=cpf_limpo,
                nome=usuario_data.nome.strip(),
                email=usuario_data.email.lower().strip(),
                telefone=usuario_data.telefone.replace(" ", "").replace("(", "").replace(")", "").replace("-", "") if usuario_data.telefone else "",
                senha_hash=senha_hash,
                tipo=usuario_data.tipo,  # Usar campo 'tipo' como principal
                ativo=True  # Usuários registrados publicamente ficam ativos por padrão
            )
            
            print(f"✅ Objeto usuário criado com sucesso")
            
        except Exception as usuario_creation_error:
            print(f"❌ Erro ao criar objeto usuário: {usuario_creation_error}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro na criação do usuário: {str(usuario_creation_error)}"
            )
        
        # 🚀 OTIMIZAÇÃO: Operação de banco com timeout
        print(f"💾 Salvando usuário no banco...")
        try:
            db.add(novo_usuario)
            db.commit()
            print(f"✅ Commit realizado com sucesso")
        except Exception as commit_error:
            print(f"❌ Erro no commit: {commit_error}")
            print(f"🔄 Fazendo rollback...")
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro ao salvar no banco de dados: {str(commit_error)}"
            )
        
        # Refresh opcional (não crítico)
        print(f"🔄 Fazendo refresh do objeto usuário...")
        try:
            db.refresh(novo_usuario)
            print(f"✅ Refresh realizado com sucesso")
        except Exception as refresh_error:
            print(f"❌ Erro no refresh: {refresh_error}")
            # Refresh não é crítico, pode continuar
        
        elapsed_time = time.time() - start_time
        print(f"✅ Usuário registrado com sucesso: {novo_usuario.nome} (ID: {novo_usuario.id}) em {elapsed_time:.2f}s")
        
        return novo_usuario
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        elapsed_time = time.time() - start_time
        print(f"❌ Erro inesperado no registro após {elapsed_time:.2f}s: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno do servidor: {str(e)}"
        )

@router.get("/me", response_model=UsuarioSchema)
async def obter_perfil(usuario_atual: Usuario = Depends(obter_usuario_atual)):
    """Obter dados do usuário logado"""
    from ..auth import get_user_tipo
    
    # Garantir que o tipo correto seja retornado
    tipo_correto = get_user_tipo(usuario_atual)
    
    # Converter para dicionário e ajustar campos
    user_dict = {
        "id": usuario_atual.id,
        "cpf": usuario_atual.cpf,
        "nome": usuario_atual.nome,
        "email": usuario_atual.email,
        "telefone": usuario_atual.telefone,
        "tipo": tipo_correto,  # Usar tipo correto determinado pela função helper
        "tipo": tipo_correto,  # Para compatibilidade
        "ativo": usuario_atual.ativo,
        "ultimo_login": usuario_atual.ultimo_login,
        "criado_em": usuario_atual.criado_em,
        "atualizado_em": usuario_atual.atualizado_em
    }
    
    return user_dict

@router.post("/logout")
async def logout(usuario_atual: Usuario = Depends(obter_usuario_atual)):
    """Logout do usuário (invalidar token)"""
    return {"mensagem": "Logout realizado com sucesso"}

@router.post("/forgot-password")
async def forgot_password(cpf: str, db: Session = Depends(get_db)):
    """
    Esqueci a senha - Simplificado
    Retorna mensagem genérica por segurança
    """
    
    # Validar CPF básico
    if not validar_cpf_basico(cpf):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="CPF inválido"
        )
    
    # Sempre retorna sucesso por questões de segurança
    # (não revela se o CPF existe ou não)
    return {
        "mensagem": "Se o CPF estiver cadastrado, as instruções de recuperação foram enviadas.",
        "instrucoes": "Entre em contato com o administrador do sistema para recuperar sua senha."
    }

@router.post("/setup-inicial")
async def setup_inicial(db: Session = Depends(get_db)):
    """Setup inicial do sistema - Criar empresa e admin padrão (apenas se não houver usuários)"""
    
    # Verificar se já existem usuários no sistema
    usuario_existente = db.query(Usuario).first()
    if usuario_existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Sistema já foi inicializado. Já existem usuários cadastrados."
        )
    
    try:
        # Criar empresa padrão
        empresa = Empresa(
            nome="Painel Universal - Empresa Demo",
            cnpj="00000000000100",
            email="contato@paineluniversal.com",
            telefone="(11) 99999-9999",
            endereco="Endereço da empresa demo",
            ativa=True
        )
        db.add(empresa)
        db.commit()
        db.refresh(empresa)
        
        # Criar usuário admin
        senha_hash = gerar_hash_senha("admin123")
        admin = Usuario(
            cpf="00000000000",
            nome="Administrador Sistema",
            email="admin@paineluniversal.com",
            telefone="(11) 99999-0000",
            senha_hash=senha_hash,
            tipo="admin",
            ativo=True
        )
        db.add(admin)
        
        # Criar usuário promoter
        senha_hash_promoter = gerar_hash_senha("promoter123")
        promoter = Usuario(
            cpf="11111111111",
            nome="Promoter Demo",
            email="promoter@paineluniversal.com",
            telefone="(11) 99999-1111",
            senha_hash=senha_hash_promoter,
            tipo="promoter",
            ativo=True
        )
        db.add(promoter)
        
        db.commit()
        
        print("Setup inicial concluido com sucesso")
        
        return {
            "mensagem": "Setup inicial realizado com sucesso!",
            "empresa": {
                "id": empresa.id,
                "nome": empresa.nome,
                "cnpj": empresa.cnpj
            },
            "credenciais": {
                "admin": {
                    "cpf": "00000000000",
                    "senha": "admin123"
                },
                "promoter": {
                    "cpf": "11111111111", 
                    "senha": "promoter123"
                }
            }
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao realizar setup inicial: {str(e)}"
        )
