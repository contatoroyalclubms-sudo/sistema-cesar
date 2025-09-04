"""
Router para Sistema Cashless - Baseado na análise do sistema Meep
Implementa todas as funcionalidades avançadas de cartões, mesas, categorias e permissões
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc
from typing import List, Optional, Dict, Any
from datetime import datetime, date, timedelta
import uuid
import qrcode
import io
import base64

from ..database import get_db
from ..auth_functions import obter_usuario_atual as get_current_user
from ..models_cashless import *
from ..schemas_cashless import *
from ..models import Usuario

router = APIRouter(prefix="/api/cashless", tags=["Cashless System"])

# ================================================================================
# ENDPOINTS PARA CATEGORIAS DE CLIENTES
# ================================================================================

@router.get("/categorias-clientes", response_model=List[CategoriaCliente])
async def listar_categorias_clientes(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    filtros: FiltrosCategoriaClientes = Depends(),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Lista categorias de clientes com filtros avançados"""
    query = db.query(CategoriaCliente)
    
    # Aplicar filtros
    if filtros.nome:
        query = query.filter(CategoriaCliente.nome.ilike(f"%{filtros.nome}%"))
    if filtros.tipo:
        query = query.filter(CategoriaCliente.tipo == filtros.tipo)
    if filtros.status:
        query = query.filter(CategoriaCliente.status == filtros.status)
    if filtros.ativa is not None:
        query = query.filter(CategoriaCliente.ativa == filtros.ativa)
    
    # Ordenar por nome
    query = query.order_by(CategoriaCliente.nome)
    
    return query.offset(skip).limit(limit).all()

@router.post("/categorias-clientes", response_model=CategoriaCliente)
async def criar_categoria_cliente(
    categoria: CategoriaClienteCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Cria nova categoria de cliente"""
    # Verificar se categoria já existe
    existing = db.query(CategoriaCliente).filter(
        and_(
            CategoriaCliente.nome == categoria.nome,
            CategoriaCliente.empresa_id == categoria.empresa_id
        )
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Categoria com este nome já existe"
        )
    
    db_categoria = CategoriaCliente(**categoria.dict())
    db.add(db_categoria)
    db.commit()
    db.refresh(db_categoria)
    
    return db_categoria

@router.get("/categorias-clientes/{categoria_id}", response_model=CategoriaCliente)
async def obter_categoria_cliente(
    categoria_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Obtém categoria de cliente por ID"""
    categoria = db.query(CategoriaCliente).filter(CategoriaCliente.id == categoria_id).first()
    if not categoria:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Categoria não encontrada"
        )
    return categoria

@router.put("/categorias-clientes/{categoria_id}", response_model=CategoriaCliente)
async def atualizar_categoria_cliente(
    categoria_id: int,
    categoria_update: CategoriaClienteUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Atualiza categoria de cliente"""
    categoria = db.query(CategoriaCliente).filter(CategoriaCliente.id == categoria_id).first()
    if not categoria:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Categoria não encontrada"
        )
    
    # Atualizar campos
    for field, value in categoria_update.dict(exclude_unset=True).items():
        setattr(categoria, field, value)
    
    db.commit()
    db.refresh(categoria)
    return categoria

@router.delete("/categorias-clientes/{categoria_id}")
async def excluir_categoria_cliente(
    categoria_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Exclui categoria de cliente"""
    categoria = db.query(CategoriaCliente).filter(CategoriaCliente.id == categoria_id).first()
    if not categoria:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Categoria não encontrada"
        )
    
    # Verificar se há clientes vinculados
    clientes_vinculados = db.query(ClienteCategoria).filter(
        and_(
            ClienteCategoria.categoria_id == categoria_id,
            ClienteCategoria.ativa == True
        )
    ).count()
    
    if clientes_vinculados > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Não é possível excluir categoria com {clientes_vinculados} clientes vinculados"
        )
    
    db.delete(categoria)
    db.commit()
    return {"message": "Categoria excluída com sucesso"}

# ================================================================================
# ENDPOINTS PARA SISTEMA DE CARGOS E PERMISSÕES
# ================================================================================

@router.get("/permissoes", response_model=List[Permissao])
async def listar_permissoes(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Lista todas as permissões disponíveis"""
    return db.query(Permissao).filter(Permissao.ativa == True).order_by(Permissao.modulo, Permissao.nome).all()

@router.get("/cargos", response_model=List[CargoComContadores])
async def listar_cargos(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Lista cargos com contadores de permissões e colaboradores"""
    cargos = db.query(Cargo).filter(Cargo.ativo == True).order_by(Cargo.nome).offset(skip).limit(limit).all()
    
    result = []
    for cargo in cargos:
        # Contar permissões
        total_permissoes = db.query(CargoPermissao).filter(CargoPermissao.cargo_id == cargo.id).count()
        
        # Contar colaboradores
        total_colaboradores = db.query(UsuarioCargo).filter(
            and_(
                UsuarioCargo.cargo_id == cargo.id,
                UsuarioCargo.ativo == True
            )
        ).count()
        
        cargo_dict = cargo.__dict__.copy()
        cargo_dict['total_permissoes'] = total_permissoes
        cargo_dict['total_colaboradores'] = total_colaboradores
        
        result.append(CargoComContadores(**cargo_dict))
    
    return result

@router.post("/cargos", response_model=Cargo)
async def criar_cargo(
    cargo: CargoCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Cria novo cargo com permissões"""
    # Verificar se cargo já existe
    existing = db.query(Cargo).filter(Cargo.nome == cargo.nome).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cargo com este nome já existe"
        )
    
    # Criar cargo
    cargo_data = cargo.dict()
    permissoes_ids = cargo_data.pop('permissoes_ids', [])
    
    db_cargo = Cargo(**cargo_data)
    db.add(db_cargo)
    db.commit()
    db.refresh(db_cargo)
    
    # Adicionar permissões
    for permissao_id in permissoes_ids:
        cargo_permissao = CargoPermissao(
            cargo_id=db_cargo.id,
            permissao_id=permissao_id,
            concedida_por=current_user.id
        )
        db.add(cargo_permissao)
    
    db.commit()
    return db_cargo

@router.get("/cargos/{cargo_id}", response_model=Cargo)
async def obter_cargo(
    cargo_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Obtém cargo por ID com suas permissões"""
    cargo = db.query(Cargo).filter(Cargo.id == cargo_id).first()
    if not cargo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cargo não encontrado"
        )
    
    # Carregar permissões
    permissoes = db.query(Permissao).join(CargoPermissao).filter(
        CargoPermissao.cargo_id == cargo_id
    ).all()
    
    cargo.permissoes = permissoes
    return cargo

# ================================================================================
# ENDPOINTS PARA SISTEMA DE MESAS
# ================================================================================

@router.get("/mesas", response_model=List[MesaComStatus])
async def listar_mesas(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    filtros: FiltrosMesas = Depends(),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Lista mesas com informações de status operacional"""
    query = db.query(Mesa)
    
    # Aplicar filtros
    if filtros.numero:
        query = query.filter(Mesa.numero.ilike(f"%{filtros.numero}%"))
    if filtros.tipo:
        query = query.filter(Mesa.tipo == filtros.tipo)
    if filtros.status:
        query = query.filter(Mesa.status == filtros.status)
    if filtros.area:
        query = query.filter(Mesa.area.ilike(f"%{filtros.area}%"))
    if filtros.ativa is not None:
        query = query.filter(Mesa.ativa == filtros.ativa)
    if filtros.disponivel:
        query = query.filter(Mesa.status == StatusMesa.DISPONIVEL)
    
    # Ordenar por número
    query = query.order_by(Mesa.numero)
    
    mesas = query.offset(skip).limit(limit).all()
    
    # Adicionar informações de status operacional
    result = []
    for mesa in mesas:
        mesa_dict = mesa.__dict__.copy()
        
        # Buscar comanda ativa na mesa
        comanda_ativa = db.query(ComandaCashless).filter(
            and_(
                ComandaCashless.mesa_id == mesa.id,
                ComandaCashless.status == "ativa"
            )
        ).first()
        
        if comanda_ativa:
            mesa_dict['comanda_ativa'] = comanda_ativa.id
            mesa_dict['cliente_atual'] = comanda_ativa.nome_cliente
            mesa_dict['valor_conta'] = comanda_ativa.saldo_atual
            
            # Calcular tempo de ocupação
            if comanda_ativa.aberta_em:
                tempo_ocupacao = (datetime.now() - comanda_ativa.aberta_em).total_seconds() / 60
                mesa_dict['tempo_ocupacao'] = int(tempo_ocupacao)
        
        result.append(MesaComStatus(**mesa_dict))
    
    return result

@router.post("/mesas", response_model=Mesa)
async def criar_mesa(
    mesa: MesaCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Cria nova mesa"""
    # Verificar se mesa já existe
    existing = db.query(Mesa).filter(
        and_(
            Mesa.numero == mesa.numero,
            Mesa.empresa_id == mesa.empresa_id
        )
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mesa com este número já existe"
        )
    
    # Gerar códigos únicos
    mesa_data = mesa.dict()
    mesa_data['qr_code_mesa'] = str(uuid.uuid4())
    mesa_data['codigo_identificacao'] = f"MESA_{mesa.numero}_{datetime.now().strftime('%Y%m%d')}"
    
    db_mesa = Mesa(**mesa_data)
    db.add(db_mesa)
    db.commit()
    db.refresh(db_mesa)
    
    return db_mesa

@router.get("/mesas/{mesa_id}", response_model=MesaComStatus)
async def obter_mesa(
    mesa_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Obtém mesa por ID com status operacional"""
    mesa = db.query(Mesa).filter(Mesa.id == mesa_id).first()
    if not mesa:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mesa não encontrada"
        )
    
    # Adicionar informações de status
    mesa_dict = mesa.__dict__.copy()
    
    comanda_ativa = db.query(ComandaCashless).filter(
        and_(
            ComandaCashless.mesa_id == mesa.id,
            ComandaCashless.status == "ativa"
        )
    ).first()
    
    if comanda_ativa:
        mesa_dict['comanda_ativa'] = comanda_ativa.id
        mesa_dict['cliente_atual'] = comanda_ativa.nome_cliente
        mesa_dict['valor_conta'] = comanda_ativa.saldo_atual
        
        if comanda_ativa.aberta_em:
            tempo_ocupacao = (datetime.now() - comanda_ativa.aberta_em).total_seconds() / 60
            mesa_dict['tempo_ocupacao'] = int(tempo_ocupacao)
    
    return MesaComStatus(**mesa_dict)

@router.put("/mesas/{mesa_id}", response_model=Mesa)
async def atualizar_mesa(
    mesa_id: int,
    mesa_update: MesaUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Atualiza mesa"""
    mesa = db.query(Mesa).filter(Mesa.id == mesa_id).first()
    if not mesa:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mesa não encontrada"
        )
    
    # Atualizar campos
    for field, value in mesa_update.dict(exclude_unset=True).items():
        setattr(mesa, field, value)
    
    db.commit()
    db.refresh(mesa)
    return mesa

@router.delete("/mesas/{mesa_id}")
async def excluir_mesa(
    mesa_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Exclui mesa"""
    mesa = db.query(Mesa).filter(Mesa.id == mesa_id).first()
    if not mesa:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mesa não encontrada"
        )
    
    # Verificar se há comandas ativas
    comandas_ativas = db.query(ComandaCashless).filter(
        and_(
            ComandaCashless.mesa_id == mesa_id,
            ComandaCashless.status == "ativa"
        )
    ).count()
    
    if comandas_ativas > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Não é possível excluir mesa com comandas ativas"
        )
    
    db.delete(mesa)
    db.commit()
    return {"message": "Mesa excluída com sucesso"}

# ================================================================================
# ENDPOINTS PARA GRUPOS DE CARTÕES
# ================================================================================

@router.get("/grupos-cartoes", response_model=List[GrupoCartao])
async def listar_grupos_cartoes(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Lista grupos de cartões"""
    return db.query(GrupoCartao).filter(
        GrupoCartao.status == StatusGrupoCartao.ATIVO
    ).order_by(GrupoCartao.nome).offset(skip).limit(limit).all()

@router.post("/grupos-cartoes", response_model=GrupoCartao)
async def criar_grupo_cartao(
    grupo: GrupoCartaoCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Cria novo grupo de cartões"""
    # Verificar se grupo já existe
    existing = db.query(GrupoCartao).filter(GrupoCartao.nome == grupo.nome).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Grupo com este nome já existe"
        )
    
    db_grupo = GrupoCartao(**grupo.dict())
    db.add(db_grupo)
    db.commit()
    db.refresh(db_grupo)
    
    return db_grupo

# ================================================================================
# ENDPOINTS PARA CARTÕES CASHLESS
# ================================================================================

@router.get("/cartoes", response_model=List[CartaoCashless])
async def listar_cartoes(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    filtros: FiltrosCartaoCashless = Depends(),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Lista cartões cashless com filtros avançados"""
    query = db.query(CartaoCashless)
    
    # Aplicar filtros
    if filtros.cpf_portador:
        query = query.filter(CartaoCashless.cpf_portador == filtros.cpf_portador)
    if filtros.nome_portador:
        query = query.filter(CartaoCashless.nome_portador.ilike(f"%{filtros.nome_portador}%"))
    if filtros.numero_cartao:
        query = query.filter(CartaoCashless.numero_cartao.ilike(f"%{filtros.numero_cartao}%"))
    if filtros.status:
        query = query.filter(CartaoCashless.status == filtros.status)
    if filtros.grupo_id:
        query = query.filter(CartaoCashless.grupo_id == filtros.grupo_id)
    if filtros.ativo is not None:
        if filtros.ativo:
            query = query.filter(CartaoCashless.status == StatusCartaoCashless.ATIVO)
        else:
            query = query.filter(CartaoCashless.status != StatusCartaoCashless.ATIVO)
    if filtros.com_saldo:
        query = query.filter(CartaoCashless.saldo_atual > 0)
    if filtros.data_inicio:
        query = query.filter(func.date(CartaoCashless.criado_em) >= filtros.data_inicio)
    if filtros.data_fim:
        query = query.filter(func.date(CartaoCashless.criado_em) <= filtros.data_fim)
    
    # Ordenar por data de criação (mais recentes primeiro)
    query = query.order_by(desc(CartaoCashless.criado_em))
    
    return query.offset(skip).limit(limit).all()

@router.post("/cartoes", response_model=CartaoCashless)
async def criar_cartao_cashless(
    cartao: CartaoCashlessCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Cria novo cartão cashless"""
    # Verificar se cartão já existe
    existing = db.query(CartaoCashless).filter(
        CartaoCashless.numero_cartao == cartao.numero_cartao
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cartão com este número já existe"
        )
    
    # Criar cartão
    cartao_data = cartao.dict()
    saldo_inicial = cartao_data.pop('saldo_inicial', 0)
    
    # Gerar códigos únicos baseados no tipo
    if cartao.tipo == TipoCartaoCashlessEnum.RFID:
        cartao_data['codigo_rfid'] = f"RFID_{uuid.uuid4().hex[:8].upper()}"
    elif cartao.tipo == TipoCartaoCashlessEnum.NFC:
        cartao_data['codigo_nfc'] = f"NFC_{uuid.uuid4().hex[:8].upper()}"
    elif cartao.tipo == TipoCartaoCashlessEnum.QR_CODE:
        cartao_data['qr_code'] = str(uuid.uuid4())
    elif cartao.tipo == TipoCartaoCashlessEnum.CODIGO_BARRAS:
        cartao_data['codigo_barras'] = f"BAR{datetime.now().strftime('%Y%m%d')}{uuid.uuid4().hex[:6].upper()}"
    
    cartao_data['saldo_atual'] = saldo_inicial
    
    db_cartao = CartaoCashless(**cartao_data)
    db.add(db_cartao)
    db.commit()
    db.refresh(db_cartao)
    
    return db_cartao

@router.get("/cartoes/{cartao_id}", response_model=CartaoCashless)
async def obter_cartao(
    cartao_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Obtém cartão por ID"""
    cartao = db.query(CartaoCashless).filter(CartaoCashless.id == cartao_id).first()
    if not cartao:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cartão não encontrado"
        )
    return cartao

@router.put("/cartoes/{cartao_id}/bloquear")
async def bloquear_cartao(
    cartao_id: int,
    motivo: str = Query(..., description="Motivo do bloqueio"),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Bloqueia cartão cashless"""
    cartao = db.query(CartaoCashless).filter(CartaoCashless.id == cartao_id).first()
    if not cartao:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cartão não encontrado"
        )
    
    cartao.status = StatusCartaoCashless.BLOQUEADO
    db.commit()
    
    return {"message": f"Cartão bloqueado com sucesso. Motivo: {motivo}"}

@router.put("/cartoes/{cartao_id}/desbloquear")
async def desbloquear_cartao(
    cartao_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Desbloqueia cartão cashless"""
    cartao = db.query(CartaoCashless).filter(CartaoCashless.id == cartao_id).first()
    if not cartao:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cartão não encontrado"
        )
    
    cartao.status = StatusCartaoCashless.ATIVO
    db.commit()
    
    return {"message": "Cartão desbloqueado com sucesso"}

# ================================================================================
# ENDPOINTS PARA PRÉ-ATIVAÇÃO DE CARTÕES
# ================================================================================

@router.get("/pre-ativacoes", response_model=List[PreAtivacaoCartao])
async def listar_pre_ativacoes(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    cpf_cliente: Optional[str] = Query(None),
    ativado: Optional[bool] = Query(None),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Lista pré-ativações de cartões"""
    query = db.query(PreAtivacaoCartao)
    
    if cpf_cliente:
        query = query.filter(PreAtivacaoCartao.cpf_cliente == cpf_cliente)
    if ativado is not None:
        query = query.filter(PreAtivacaoCartao.ativado == ativado)
    
    return query.order_by(desc(PreAtivacaoCartao.vinculado_em)).offset(skip).limit(limit).all()

@router.post("/pre-ativacoes", response_model=PreAtivacaoCartao)
async def criar_pre_ativacao(
    pre_ativacao: PreAtivacaoCartaoCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Cria pré-ativação de cartão"""
    # Verificar se cartão já foi pré-ativado
    existing = db.query(PreAtivacaoCartao).filter(
        PreAtivacaoCartao.numero_cartao == pre_ativacao.numero_cartao
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cartão já possui pré-ativação"
        )
    
    pre_ativacao_data = pre_ativacao.dict()
    pre_ativacao_data['vinculado_por'] = current_user.id
    
    db_pre_ativacao = PreAtivacaoCartao(**pre_ativacao_data)
    db.add(db_pre_ativacao)
    db.commit()
    db.refresh(db_pre_ativacao)
    
    return db_pre_ativacao

# ================================================================================
# ENDPOINTS PARA RECARGAS
# ================================================================================

@router.post("/cartoes/{cartao_id}/recarregar", response_model=RecargaCashless)
async def recarregar_cartao(
    cartao_id: int,
    recarga: RecargaCashlessCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Realiza recarga em cartão cashless"""
    cartao = db.query(CartaoCashless).filter(CartaoCashless.id == cartao_id).first()
    if not cartao:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cartão não encontrado"
        )
    
    if cartao.status != StatusCartaoCashless.ATIVO:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cartão não está ativo para recarga"
        )
    
    # Criar recarga
    recarga_data = recarga.dict()
    recarga_data['cartao_id'] = cartao_id
    recarga_data['operador_id'] = current_user.id
    recarga_data['codigo_transacao_pagamento'] = f"REC_{datetime.now().strftime('%Y%m%d%H%M%S')}_{cartao_id}"
    recarga_data['status_pagamento'] = "aprovado"  # Simplificado para demo
    
    db_recarga = RecargaCashless(**recarga_data)
    db.add(db_recarga)
    
    # Atualizar saldo do cartão
    cartao.saldo_atual += recarga.valor_recarga
    cartao.saldo_bonus += recarga.valor_bonus
    cartao.data_ultimo_uso = datetime.now()
    
    db.commit()
    db.refresh(db_recarga)
    
    return db_recarga

# ================================================================================
# ENDPOINTS PARA TRANSAÇÕES
# ================================================================================

@router.post("/cartoes/{cartao_id}/transacao", response_model=TransacaoCashless)
async def realizar_transacao(
    cartao_id: int,
    transacao: TransacaoCashlessCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Realiza transação com cartão cashless"""
    cartao = db.query(CartaoCashless).filter(CartaoCashless.id == cartao_id).first()
    if not cartao:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cartão não encontrado"
        )
    
    if cartao.status != StatusCartaoCashless.ATIVO:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cartão não está ativo para transações"
        )
    
    valor_final = transacao.valor_transacao - transacao.valor_desconto
    
    if cartao.saldo_atual < valor_final:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Saldo insuficiente para realizar transação"
        )
    
    # Criar transação
    transacao_data = transacao.dict()
    transacao_data['cartao_id'] = cartao_id
    transacao_data['valor_final'] = valor_final
    transacao_data['operador_id'] = current_user.id
    
    db_transacao = TransacaoCashless(**transacao_data)
    db.add(db_transacao)
    
    # Debitar do cartão
    cartao.saldo_atual -= valor_final
    cartao.data_ultimo_uso = datetime.now()
    
    db.commit()
    db.refresh(db_transacao)
    
    return db_transacao

# ================================================================================
# ENDPOINTS PARA ESTATÍSTICAS E DASHBOARD
# ================================================================================

@router.get("/dashboard", response_model=DashboardCashless)
async def obter_dashboard_cashless(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Obtém dados do dashboard cashless"""
    hoje = date.today()
    
    # Estatísticas de cartões
    total_cartoes = db.query(CartaoCashless).count()
    cartoes_ativos = db.query(CartaoCashless).filter(
        CartaoCashless.status == StatusCartaoCashless.ATIVO
    ).count()
    cartoes_bloqueados = db.query(CartaoCashless).filter(
        CartaoCashless.status == StatusCartaoCashless.BLOQUEADO
    ).count()
    
    saldo_total = db.query(func.sum(CartaoCashless.saldo_atual)).scalar() or 0
    
    # Recargas de hoje
    recargas_hoje = db.query(RecargaCashless).filter(
        func.date(RecargaCashless.criado_em) == hoje
    ).count()
    
    valor_recargas_hoje = db.query(func.sum(RecargaCashless.valor_recarga)).filter(
        func.date(RecargaCashless.criado_em) == hoje
    ).scalar() or 0
    
    # Transações de hoje
    transacoes_hoje = db.query(TransacaoCashless).filter(
        func.date(TransacaoCashless.criado_em) == hoje
    ).count()
    
    valor_transacoes_hoje = db.query(func.sum(TransacaoCashless.valor_final)).filter(
        func.date(TransacaoCashless.criado_em) == hoje
    ).scalar() or 0
    
    # Estatísticas de mesas
    total_mesas = db.query(Mesa).filter(Mesa.ativa == True).count()
    mesas_disponiveis = db.query(Mesa).filter(
        and_(Mesa.ativa == True, Mesa.status == StatusMesa.DISPONIVEL)
    ).count()
    mesas_ocupadas = db.query(Mesa).filter(
        and_(Mesa.ativa == True, Mesa.status == StatusMesa.OCUPADA)
    ).count()
    mesas_reservadas = db.query(Mesa).filter(
        and_(Mesa.ativa == True, Mesa.status == StatusMesa.RESERVADA)
    ).count()
    
    taxa_ocupacao = (mesas_ocupadas / total_mesas * 100) if total_mesas > 0 else 0
    
    # Contadores adicionais
    categorias_clientes_count = db.query(CategoriaCliente).filter(
        CategoriaCliente.ativa == True
    ).count()
    grupos_cartoes_count = db.query(GrupoCartao).filter(
        GrupoCartao.status == StatusGrupoCartao.ATIVO
    ).count()
    cardapios_digitais_count = db.query(CardapioDigital).filter(
        CardapioDigital.ativo == True
    ).count()
    
    return DashboardCashless(
        estatisticas_cartoes=EstatisticasCartoes(
            total_cartoes=total_cartoes,
            cartoes_ativos=cartoes_ativos,
            cartoes_bloqueados=cartoes_bloqueados,
            saldo_total=saldo_total,
            recargas_hoje=recargas_hoje,
            valor_recargas_hoje=valor_recargas_hoje,
            transacoes_hoje=transacoes_hoje,
            valor_transacoes_hoje=valor_transacoes_hoje
        ),
        estatisticas_mesas=EstatisticasMesas(
            total_mesas=total_mesas,
            mesas_disponiveis=mesas_disponiveis,
            mesas_ocupadas=mesas_ocupadas,
            mesas_reservadas=mesas_reservadas,
            taxa_ocupacao=taxa_ocupacao
        ),
        categorias_clientes_count=categorias_clientes_count,
        grupos_cartoes_count=grupos_cartoes_count,
        cardapios_digitais_count=cardapios_digitais_count,
        ultima_atualizacao=datetime.now()
    )

@router.get("/mesas/estatisticas", response_model=EstatisticasMesas)
async def obter_estatisticas_mesas(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Obtém estatísticas detalhadas das mesas"""
    total_mesas = db.query(Mesa).filter(Mesa.ativa == True).count()
    mesas_disponiveis = db.query(Mesa).filter(
        and_(Mesa.ativa == True, Mesa.status == StatusMesa.DISPONIVEL)
    ).count()
    mesas_ocupadas = db.query(Mesa).filter(
        and_(Mesa.ativa == True, Mesa.status == StatusMesa.OCUPADA)
    ).count()
    mesas_reservadas = db.query(Mesa).filter(
        and_(Mesa.ativa == True, Mesa.status == StatusMesa.RESERVADA)
    ).count()
    
    taxa_ocupacao = (mesas_ocupadas / total_mesas * 100) if total_mesas > 0 else 0
    
    return EstatisticasMesas(
        total_mesas=total_mesas,
        mesas_disponiveis=mesas_disponiveis,
        mesas_ocupadas=mesas_ocupadas,
        mesas_reservadas=mesas_reservadas,
        taxa_ocupacao=taxa_ocupacao
    )
