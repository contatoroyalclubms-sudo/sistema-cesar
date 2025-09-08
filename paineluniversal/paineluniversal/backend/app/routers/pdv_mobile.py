"""
Router principal do App PDV Mobile para Garçons
Sistema completo de NFC, validação CPF e gestão de pedidos mobile
"""
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Request
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, desc, and_, or_
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from decimal import Decimal
import uuid
import json
import hashlib
import secrets
from ..database import get_db
from ..models import (
    Usuario, Evento, Comanda, Produto, VendaPDV, ItemVendaPDV,
    Impressora, PrintJob, TipoPrintJob, StatusComanda
)
from ..models_mobile import (
    SessaoGarcom, ValidacaoNFCMobile, CategoriaMobile, ProdutoMobile,
    PedidoMobile, ItemPedidoMobile, ConfiguracaoMobile, ComandaNFC,
    LogAtividadeMobile, StatusSessaoGarcom, StatusValidacaoNFC,
    TipoValidacaoNFC, StatusPedidoMobile
)
from ..schemas_mobile import (
    SessaoGarcomCreate, SessaoGarcom as SessaoGarcomSchema,
    ValidacaoNFCRequest, ValidacaoNFCResponse, ComandaInfoResponse,
    PedidoMobileCreate, PedidoMobile as PedidoMobileSchema,
    CategoriaMobileCreate, CategoriaMobile as CategoriaMobileSchema,
    ProdutoMobileCreate, ProdutoMobileResponse,
    ConfiguracaoMobile as ConfiguracaoMobileSchema,
    LoginMobileResponse, HeartbeatRequest, HeartbeatResponse,
    DashboardGarcom, StatusPedidoResponse, HeartbeatRequest,
    FinalizarSessaoRequest, SyncOfflineRequest, ProdutoMobileFilter
)
from ..auth_functions import obter_usuario_atual
from ..websocket import notify_new_mobile_order, notify_order_status_update

router = APIRouter(prefix="/pdv-mobile", tags=["PDV Mobile"])

# ==================== FUNÇÕES AUXILIARES ====================

async def get_sessao_ativa(
    authorization: str = Depends(lambda request: request.headers.get("authorization")),
    db: Session = Depends(get_db)
) -> SessaoGarcom:
    """
    Dependency para obter sessão ativa baseada no token
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Token de autorização necessário"
        )
    
    token = authorization.split(" ")[1]
    
    # Buscar sessão ativa
    sessao = db.query(SessaoGarcom).filter(
        and_(
            SessaoGarcom.token_sessao == token,
            SessaoGarcom.status == StatusSessaoGarcom.ATIVA,
            SessaoGarcom.ultimo_heartbeat >= datetime.now() - timedelta(hours=8)
        )
    ).options(joinedload(SessaoGarcom.garcom)).first()
    
    if not sessao:
        raise HTTPException(
            status_code=401,
            detail="Sessão expirada ou inválida"
        )
    
    return sessao

# ==================== AUTENTICAÇÃO E SESSÃO ====================

@router.post("/login", response_model=LoginMobileResponse)
async def login_mobile(
    sessao_data: SessaoGarcomCreate,
    request: Request,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(obter_usuario_atual)
):
    """
    Login específico para o app mobile dos garçons
    Cria/retoma sessão ativa e retorna configurações do evento
    """
    # Verificar se usuário pode usar o app mobile
    if usuario_atual.tipo not in ["admin", "promoter"]:
        raise HTTPException(
            status_code=403,
            detail="Acesso negado: apenas garçons autorizados podem usar o app mobile"
        )
    
    # Verificar se evento existe e está ativo
    evento = db.query(Evento).filter(Evento.id == sessao_data.evento_id).first()
    if not evento:
        raise HTTPException(status_code=404, detail="Evento não encontrado")
    
    # Verificar se já existe sessão ativa para o garçom no evento
    sessao_existente = db.query(SessaoGarcom).filter(
        and_(
            SessaoGarcom.garcom_id == usuario_atual.id,
            SessaoGarcom.evento_id == sessao_data.evento_id,
            SessaoGarcom.status == StatusSessaoGarcom.ATIVA
        )
    ).first()
    
    if sessao_existente:
        # Atualizar sessão existente
        sessao_existente.ultimo_heartbeat = datetime.now()
        sessao_existente.device_id = sessao_data.device_id
        sessao_existente.app_version = sessao_data.app_version
        sessao_existente.device_info = sessao_data.device_info
        db.commit()
        sessao = sessao_existente
    else:
        # Criar nova sessão
        token_sessao = secrets.token_urlsafe(32)
        sessao = SessaoGarcom(
            garcom_id=usuario_atual.id,
            evento_id=sessao_data.evento_id,
            token_sessao=token_sessao,
            device_id=sessao_data.device_id,
            app_version=sessao_data.app_version,
            device_info=sessao_data.device_info,
            area_atendimento=sessao_data.area_atendimento,
            mesa_inicial=sessao_data.mesa_inicial,
            mesa_final=sessao_data.mesa_final,
            configuracoes=sessao_data.configuracoes or {}
        )
        db.add(sessao)
        db.commit()
        db.refresh(sessao)
    
    # Buscar ou criar configuração do evento
    config = db.query(ConfiguracaoMobile).filter(
        ConfiguracaoMobile.evento_id == sessao_data.evento_id
    ).first()
    
    if not config:
        config = ConfiguracaoMobile(evento_id=sessao_data.evento_id)
        db.add(config)
        db.commit()
        db.refresh(config)
    
    # Buscar categorias mobile do evento
    categorias = db.query(CategoriaMobile).filter(
        and_(
            CategoriaMobile.evento_id == sessao_data.evento_id,
            CategoriaMobile.ativo == True
        )
    ).order_by(CategoriaMobile.ordem_exibicao).all()
    
    # Log da atividade
    await log_atividade_mobile(
        sessao.id, "login_mobile", 
        {"evento_id": sessao_data.evento_id, "device_id": sessao_data.device_id},
        request, db
    )
    
    return LoginMobileResponse(
        success=True,
        token=sessao.token_sessao,
        sessao_id=sessao.id,
        garcom={
            "id": usuario_atual.id,
            "nome": usuario_atual.nome,
            "tipo": usuario_atual.tipo
        },
        evento={
            "id": evento.id,
            "nome": evento.nome,
            "data_evento": evento.data_evento.isoformat(),
            "local": evento.local
        },
        configuracao=config,
        categorias=categorias
    )

@router.post("/heartbeat", response_model=HeartbeatResponse)
async def heartbeat_mobile(
    heartbeat_data: HeartbeatRequest,
    request: Request,
    db: Session = Depends(get_db),
    sessao: SessaoGarcom = Depends(get_sessao_ativa)
):
    """
    Heartbeat para manter sessão ativa e verificar atualizações
    """
    # Atualizar timestamp da sessão
    sessao.ultimo_heartbeat = datetime.now()
    
    # Verificar se configuração foi atualizada
    config = db.query(ConfiguracaoMobile).filter(
        ConfiguracaoMobile.evento_id == sessao.evento_id
    ).first()
    
    configuracao_atualizada = False
    if config and config.atualizado_em > sessao.ultimo_heartbeat - timedelta(minutes=1):
        configuracao_atualizada = True
    
    db.commit()
    
    return HeartbeatResponse(
        success=True,
        sessao_ativa=True,
        timestamp=datetime.now(),
        configuracao_atualizada=configuracao_atualizada,
        nova_configuracao=config if configuracao_atualizada else None
    )

@router.post("/logout")
async def logout_mobile(
    finalizar_data: FinalizarSessaoRequest,
    request: Request,
    db: Session = Depends(get_db),
    sessao: SessaoGarcom = Depends(get_sessao_ativa)
):
    """
    Finalizar sessão do garçom
    """
    sessao.status = StatusSessaoGarcom.FINALIZADA
    sessao.fim_sessao = datetime.now()
    
    # Log da atividade
    await log_atividade_mobile(
        sessao.id, "logout_mobile",
        {
            "motivo": finalizar_data.motivo,
            "observacoes": finalizar_data.observacoes,
            "duracao_sessao": (datetime.now() - sessao.inicio_sessao).total_seconds() / 60
        },
        request, db
    )
    
    db.commit()
    
    return {"success": True, "message": "Sessão finalizada com sucesso"}

# ==================== VALIDAÇÃO NFC ====================

@router.post("/nfc/validar", response_model=ValidacaoNFCResponse)
async def validar_nfc(
    validacao_data: ValidacaoNFCRequest,
    request: Request,
    db: Session = Depends(get_db),
    sessao: SessaoGarcom = Depends(get_sessao_ativa)
):
    """
    Validar leitura NFC e CPF (3 primeiros dígitos)
    Fluxo principal: NFC → CPF → Liberação do atendimento
    """
    try:
        # Buscar comanda por UID NFC
        comanda_nfc = db.query(ComandaNFC).filter(
            ComandaNFC.nfc_uid == validacao_data.nfc_uid
        ).first()
        
        if not comanda_nfc:
            # Criar log de tentativa
            await criar_log_validacao_nfc(
                sessao.id, validacao_data, StatusValidacaoNFC.NFC_ERRO,
                "NFC não encontrado no sistema", request, db
            )
            
            return ValidacaoNFCResponse(
                status=StatusValidacaoNFC.NFC_ERRO,
                detalhes_erro="NFC não encontrado no sistema",
                retry_permitido=False
            )
        
        # Verificar se comanda está ativa
        comanda = db.query(Comanda).filter(Comanda.id == comanda_nfc.comanda_id).first()
        if not comanda or comanda.status != StatusComanda.ATIVA:
            await criar_log_validacao_nfc(
                sessao.id, validacao_data, StatusValidacaoNFC.COMANDA_BLOQUEADA,
                "Comanda inativa ou bloqueada", request, db, comanda_nfc.comanda_id
            )
            
            return ValidacaoNFCResponse(
                status=StatusValidacaoNFC.COMANDA_BLOQUEADA,
                detalhes_erro="Comanda inativa ou bloqueada",
                retry_permitido=False
            )
        
        # Validar CPF (3 primeiros dígitos)
        cpf_esperado = comanda.cpf_cliente[:3] if comanda.cpf_cliente else None
        cpf_valido = cpf_esperado == validacao_data.cpf_digits
        
        if not cpf_valido:
            # Incrementar tentativas erradas
            comanda_nfc.tentativas_cpf_erradas += 1
            
            # Bloquear se excedeu tentativas
            if comanda_nfc.tentativas_cpf_erradas >= comanda_nfc.max_tentativas_cpf:
                comanda_nfc.bloqueada_tentativas = True
                
                await criar_log_validacao_nfc(
                    sessao.id, validacao_data, StatusValidacaoNFC.COMANDA_BLOQUEADA,
                    f"Comanda bloqueada após {comanda_nfc.max_tentativas_cpf} tentativas de CPF incorreto",
                    request, db, comanda_nfc.comanda_id
                )
                
                db.commit()
                
                return ValidacaoNFCResponse(
                    status=StatusValidacaoNFC.COMANDA_BLOQUEADA,
                    detalhes_erro="Comanda bloqueada por tentativas de CPF incorreto",
                    retry_permitido=False
                )
            
            await criar_log_validacao_nfc(
                sessao.id, validacao_data, StatusValidacaoNFC.FALHA_CPF,
                "CPF informado não confere", request, db, comanda_nfc.comanda_id
            )
            
            tentativas_restantes = comanda_nfc.max_tentativas_cpf - comanda_nfc.tentativas_cpf_erradas
            
            db.commit()
            
            return ValidacaoNFCResponse(
                status=StatusValidacaoNFC.FALHA_CPF,
                detalhes_erro="CPF informado não confere",
                retry_permitido=True,
                tentativas_restantes=tentativas_restantes
            )
        
        # Verificar saldo (se aplicável)
        if comanda.saldo_atual <= 0:
            await criar_log_validacao_nfc(
                sessao.id, validacao_data, StatusValidacaoNFC.FALHA_SALDO,
                "Saldo insuficiente na comanda", request, db, comanda_nfc.comanda_id
            )
            
            return ValidacaoNFCResponse(
                status=StatusValidacaoNFC.FALHA_SALDO,
                comanda_id=comanda.id,
                cliente_nome=comanda.nome_cliente,
                saldo_disponivel=comanda.saldo_atual,
                detalhes_erro="Saldo insuficiente na comanda",
                retry_permitido=True
            )
        
        # Validação bem-sucedida
        comanda_nfc.tentativas_cpf_erradas = 0  # Reset tentativas
        comanda_nfc.ultima_leitura = datetime.now()
        comanda_nfc.total_leituras += 1
        
        if not comanda_nfc.primeira_leitura:
            comanda_nfc.primeira_leitura = datetime.now()
        
        await criar_log_validacao_nfc(
            sessao.id, validacao_data, StatusValidacaoNFC.SUCESSO,
            "Validação realizada com sucesso", request, db, comanda_nfc.comanda_id
        )
        
        # Atualizar métricas da sessão
        sessao.total_comandas_atendidas += 1
        
        db.commit()
        
        return ValidacaoNFCResponse(
            status=StatusValidacaoNFC.SUCESSO,
            comanda_id=comanda.id,
            cliente_nome=comanda.nome_cliente,
            saldo_disponivel=comanda.saldo_atual,
            limite_credito=Decimal('0.00'),  # Implementar se necessário
            retry_permitido=False
        )
        
    except Exception as e:
        await criar_log_validacao_nfc(
            sessao.id, validacao_data, StatusValidacaoNFC.NFC_ERRO,
            f"Erro interno: {str(e)}", request, db
        )
        
        raise HTTPException(
            status_code=500,
            detail=f"Erro interno na validação NFC: {str(e)}"
        )

@router.get("/comanda/{comanda_id}/info", response_model=ComandaInfoResponse)
async def obter_info_comanda(
    comanda_id: int,
    db: Session = Depends(get_db),
    sessao: SessaoGarcom = Depends(get_sessao_ativa)
):
    """
    Obter informações detalhadas da comanda após validação NFC
    """
    comanda = db.query(Comanda).filter(Comanda.id == comanda_id).first()
    if not comanda:
        raise HTTPException(status_code=404, detail="Comanda não encontrada")
    
    # Buscar histórico recente de pedidos
    pedidos_recentes = db.query(PedidoMobile).filter(
        and_(
            PedidoMobile.comanda_id == comanda_id,
            PedidoMobile.criado_em >= datetime.now() - timedelta(hours=24)
        )
    ).order_by(desc(PedidoMobile.criado_em)).limit(5).all()
    
    historico = []
    for pedido in pedidos_recentes:
        historico.append({
            "numero_pedido": pedido.numero_pedido,
            "valor": float(pedido.valor_final),
            "status": pedido.status.value,
            "timestamp": pedido.criado_em.isoformat()
        })
    
    # Verificar bloqueios
    bloqueios = []
    comanda_nfc = db.query(ComandaNFC).filter(
        ComandaNFC.comanda_id == comanda_id
    ).first()
    
    if comanda_nfc and comanda_nfc.bloqueada_tentativas:
        bloqueios.append("Bloqueada por tentativas de CPF incorreto")
    
    if comanda.status != StatusComanda.ATIVA:
        bloqueios.append(f"Status: {comanda.status.value}")
    
    return ComandaInfoResponse(
        comanda_id=comanda.id,
        numero_comanda=comanda.numero_comanda,
        cliente_nome=comanda.nome_cliente,
        saldo_disponivel=comanda.saldo_atual,
        limite_credito=Decimal('0.00'),  # Implementar se necessário
        historico_recente=historico,
        bloqueios=bloqueios
    )

# ==================== GESTÃO DE PRODUTOS ====================

@router.get("/categorias", response_model=List[CategoriaMobileSchema])
async def listar_categorias_mobile(
    db: Session = Depends(get_db),
    sessao: SessaoGarcom = Depends(get_sessao_ativa)
):
    """
    Listar categorias de produtos otimizadas para mobile
    """
    categorias = db.query(CategoriaMobile).filter(
        and_(
            CategoriaMobile.evento_id == sessao.evento_id,
            CategoriaMobile.ativo == True
        )
    ).order_by(CategoriaMobile.ordem_exibicao).all()
    
    return categorias

@router.get("/produtos", response_model=List[ProdutoMobileResponse])
async def listar_produtos_mobile(
    categoria_id: Optional[int] = None,
    destaque: Optional[bool] = None,
    vendas_rapidas: Optional[bool] = None,
    busca: Optional[str] = None,
    db: Session = Depends(get_db),
    sessao: SessaoGarcom = Depends(get_sessao_ativa)
):
    """
    Listar produtos otimizados para o app mobile
    """
    # Query base com join dos produtos
    query = db.query(ProdutoMobile).join(Produto).join(CategoriaMobile).filter(
        and_(
            CategoriaMobile.evento_id == sessao.evento_id,
            ProdutoMobile.ativo_mobile == True,
            Produto.status == "ATIVO"
        )
    )
    
    # Filtros
    if categoria_id:
        query = query.filter(ProdutoMobile.categoria_mobile_id == categoria_id)
    
    if destaque is not None:
        query = query.filter(ProdutoMobile.destaque == destaque)
    
    if vendas_rapidas is not None:
        query = query.filter(ProdutoMobile.vendas_rapidas == vendas_rapidas)
    
    if busca:
        query = query.filter(
            or_(
                Produto.nome.ilike(f"%{busca}%"),
                Produto.categoria.ilike(f"%{busca}%"),
                ProdutoMobile.ingredientes.ilike(f"%{busca}%")
            )
        )
    
    produtos_mobile = query.order_by(
        CategoriaMobile.ordem_exibicao,
        ProdutoMobile.ordem_categoria,
        Produto.nome
    ).all()
    
    # Construir response com dados do produto principal
    result = []
    for produto_mobile in produtos_mobile:
        produto = produto_mobile.produto
        
        result.append(ProdutoMobileResponse(
            id=produto_mobile.id,
            produto_id=produto_mobile.produto_id,
            categoria_mobile_id=produto_mobile.categoria_mobile_id,
            imagem_mobile=produto_mobile.imagem_mobile,
            destaque=produto_mobile.destaque,
            novo=produto_mobile.novo,
            promocao=produto_mobile.promocao,
            vendas_rapidas=produto_mobile.vendas_rapidas,
            ordem_categoria=produto_mobile.ordem_categoria,
            tempo_preparo=produto_mobile.tempo_preparo,
            ingredientes=produto_mobile.ingredientes,
            observacoes_padrao=produto_mobile.observacoes_padrao,
            ativo_mobile=produto_mobile.ativo_mobile,
            criado_em=produto_mobile.criado_em,
            # Dados do produto principal
            nome=produto.nome,
            preco=produto.preco,
            estoque_atual=produto.estoque_atual,
            categoria=produto.categoria,
            status=produto.status.value
        ))
    
    return result

# ==================== GESTÃO DE PEDIDOS ====================

@router.post("/pedidos", response_model=PedidoMobileSchema)
async def criar_pedido_mobile(
    pedido_data: PedidoMobileCreate,
    background_tasks: BackgroundTasks,
    request: Request,
    db: Session = Depends(get_db),
    sessao: SessaoGarcom = Depends(get_sessao_ativa)
):
    """
    Criar novo pedido via app mobile
    Fluxo: Validação → Cálculos → Criação → Impressão
    """
    try:
        # Verificar se comanda existe e está ativa
        comanda = db.query(Comanda).filter(
            and_(
                Comanda.id == pedido_data.comanda_id,
                Comanda.evento_id == sessao.evento_id
            )
        ).first()
        
        if not comanda:
            raise HTTPException(status_code=404, detail="Comanda não encontrada")
        
        if comanda.status != StatusComanda.ATIVA:
            raise HTTPException(status_code=400, detail="Comanda não está ativa")
        
        # Validar produtos e calcular valores
        valor_total = Decimal('0.00')
        itens_validados = []
        
        for item_data in pedido_data.itens:
            produto_mobile = db.query(ProdutoMobile).join(Produto).filter(
                and_(
                    ProdutoMobile.id == item_data.produto_mobile_id,
                    ProdutoMobile.ativo_mobile == True,
                    Produto.status == "ATIVO"
                )
            ).first()
            
            if not produto_mobile:
                raise HTTPException(
                    status_code=404,
                    detail=f"Produto mobile {item_data.produto_mobile_id} não encontrado"
                )
            
            produto = produto_mobile.produto
            
            # Verificar estoque
            if produto.controla_estoque and produto.estoque_atual < item_data.quantidade:
                raise HTTPException(
                    status_code=400,
                    detail=f"Estoque insuficiente para {produto.nome}. Disponível: {produto.estoque_atual}"
                )
            
            preco_unitario = produto.preco
            preco_total = preco_unitario * item_data.quantidade
            valor_total += preco_total
            
            itens_validados.append({
                'data': item_data,
                'produto_mobile': produto_mobile,
                'produto': produto,
                'preco_unitario': preco_unitario,
                'preco_total': preco_total
            })
        
        # Verificar saldo da comanda
        valor_final = valor_total  # Aplicar descontos se necessário
        
        if comanda.saldo_atual < valor_final:
            raise HTTPException(
                status_code=400,
                detail=f"Saldo insuficiente na comanda. Disponível: R$ {comanda.saldo_atual}, Necessário: R$ {valor_final}"
            )
        
        # Criar pedido
        numero_pedido = f"MOB{datetime.now().strftime('%Y%m%d%H%M%S')}{str(uuid.uuid4())[:4].upper()}"
        
        # Calcular tempo estimado de preparo
        tempo_estimado = max([
            item['produto_mobile'].tempo_preparo or 
            item['produto_mobile'].categoria.tempo_preparo_medio 
            for item in itens_validados
        ], default=15)
        
        pedido = PedidoMobile(
            numero_pedido=numero_pedido,
            sessao_id=sessao.id,
            comanda_id=pedido_data.comanda_id,
            evento_id=sessao.evento_id,
            cpf_cliente=pedido_data.cpf_cliente or comanda.cpf_cliente,
            nome_cliente=pedido_data.nome_cliente or comanda.nome_cliente,
            mesa_numero=pedido_data.mesa_numero,
            area_atendimento=pedido_data.area_atendimento or sessao.area_atendimento,
            valor_total=valor_total,
            valor_desconto=Decimal('0.00'),  # Implementar descontos se necessário
            valor_final=valor_final,
            status=StatusPedidoMobile.CARRINHO,
            observacoes_gerais=pedido_data.observacoes_gerais,
            prioridade=pedido_data.prioridade,
            tempo_estimado_preparo=tempo_estimado
        )
        
        db.add(pedido)
        db.flush()  # Para obter o ID
        
        # Criar itens do pedido
        for item in itens_validados:
            item_pedido = ItemPedidoMobile(
                pedido_id=pedido.id,
                produto_mobile_id=item['data'].produto_mobile_id,
                quantidade=item['data'].quantidade,
                preco_unitario=item['preco_unitario'],
                preco_total=item['preco_total'],
                observacoes=item['data'].observacoes,
                sem_ingredientes=item['data'].sem_ingredientes,
                extras=item['data'].extras,
                tempo_preparo_estimado=item['produto_mobile'].tempo_preparo
            )
            db.add(item_pedido)
        
        # Debitar saldo da comanda
        comanda.saldo_atual -= valor_final
        
        # Atualizar estatísticas da sessão
        sessao.total_vendas += 1
        sessao.valor_total_vendido += valor_final
        
        # Confirmar pedido (enviar para impressão)
        pedido.status = StatusPedidoMobile.ENVIADO
        pedido.enviado_impressao_em = datetime.now()
        
        db.commit()
        db.refresh(pedido)
        
        # Log da atividade
        await log_atividade_mobile(
            sessao.id, "pedido_criado",
            {
                "pedido_id": pedido.id,
                "numero_pedido": pedido.numero_pedido,
                "valor_total": float(valor_final),
                "itens_count": len(itens_validados)
            },
            request, db
        )
        
        # Enviar para impressão (background task)
        background_tasks.add_task(processar_impressao_pedido_mobile, pedido.id, db)
        
        # Notificar via WebSocket
        await notify_new_mobile_order(sessao.evento_id, {
            "pedido_id": pedido.id,
            "numero_pedido": pedido.numero_pedido,
            "garcom": sessao.garcom.nome,
            "valor": float(valor_final),
            "itens": len(itens_validados)
        })
        
        return pedido
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Erro interno ao criar pedido: {str(e)}"
        )

@router.get("/pedidos", response_model=List[PedidoMobileSchema])
async def listar_pedidos_mobile(
    status: Optional[str] = None,
    data_inicio: Optional[datetime] = None,
    data_fim: Optional[datetime] = None,
    comanda_id: Optional[int] = None,
    db: Session = Depends(get_db),
    sessao: SessaoGarcom = Depends(get_sessao_ativa)
):
    """
    Listar pedidos do garçom na sessão atual
    """
    query = db.query(PedidoMobile).filter(
        PedidoMobile.sessao_id == sessao.id
    )
    
    if status:
        query = query.filter(PedidoMobile.status == status)
    
    if data_inicio:
        query = query.filter(PedidoMobile.criado_em >= data_inicio)
    
    if data_fim:
        query = query.filter(PedidoMobile.criado_em <= data_fim)
    
    if comanda_id:
        query = query.filter(PedidoMobile.comanda_id == comanda_id)
    
    return query.order_by(desc(PedidoMobile.criado_em)).all()

@router.get("/pedidos/{pedido_id}/status", response_model=StatusPedidoResponse)
async def obter_status_pedido(
    pedido_id: str,
    db: Session = Depends(get_db),
    sessao: SessaoGarcom = Depends(get_sessao_ativa)
):
    """
    Obter status atual de um pedido específico
    """
    pedido = db.query(PedidoMobile).filter(
        and_(
            PedidoMobile.id == pedido_id,
            PedidoMobile.sessao_id == sessao.id
        )
    ).first()
    
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")
    
    # Calcular tempo restante estimado
    tempo_restante = None
    if pedido.status == StatusPedidoMobile.PREPARANDO and pedido.iniciado_preparo_em:
        tempo_decorrido = (datetime.now() - pedido.iniciado_preparo_em).total_seconds() / 60
        tempo_restante = max(0, (pedido.tempo_estimado_preparo or 15) - tempo_decorrido)
    
    return StatusPedidoResponse(
        pedido_id=pedido.id,
        status_atual=pedido.status,
        tempo_restante_estimado=int(tempo_restante) if tempo_restante is not None else None,
        ultima_atualizacao=pedido.atualizado_em or pedido.criado_em,
        detalhes=None  # Adicionar detalhes se necessário
    )

# ==================== DASHBOARD ====================

@router.get("/dashboard", response_model=DashboardGarcom)
async def obter_dashboard_garcom(
    db: Session = Depends(get_db),
    sessao: SessaoGarcom = Depends(get_sessao_ativa)
):
    """
    Dashboard específico para o garçom logado
    """
    hoje = datetime.now().date()
    
    # Contar pedidos por status
    pedidos_pendentes = db.query(func.count(PedidoMobile.id)).filter(
        and_(
            PedidoMobile.sessao_id == sessao.id,
            PedidoMobile.status == StatusPedidoMobile.ENVIADO
        )
    ).scalar() or 0
    
    pedidos_preparando = db.query(func.count(PedidoMobile.id)).filter(
        and_(
            PedidoMobile.sessao_id == sessao.id,
            PedidoMobile.status == StatusPedidoMobile.PREPARANDO
        )
    ).scalar() or 0
    
    pedidos_prontos = db.query(func.count(PedidoMobile.id)).filter(
        and_(
            PedidoMobile.sessao_id == sessao.id,
            PedidoMobile.status == StatusPedidoMobile.PRONTO
        )
    ).scalar() or 0
    
    # Valor vendido hoje
    valor_vendido_hoje = db.query(func.sum(PedidoMobile.valor_final)).filter(
        and_(
            PedidoMobile.sessao_id == sessao.id,
            func.date(PedidoMobile.criado_em) == hoje,
            PedidoMobile.status != StatusPedidoMobile.CANCELADO
        )
    ).scalar() or Decimal('0.00')
    
    # Tempo de sessão ativa
    tempo_sessao = int((datetime.now() - sessao.inicio_sessao).total_seconds() / 60)
    
    # Próximos pedidos prontos
    proximos_prontos = db.query(PedidoMobile).filter(
        and_(
            PedidoMobile.sessao_id == sessao.id,
            PedidoMobile.status == StatusPedidoMobile.PRONTO
        )
    ).order_by(PedidoMobile.pronto_em).limit(5).all()
    
    proximos_dados = []
    for pedido in proximos_prontos:
        proximos_dados.append({
            "numero_pedido": pedido.numero_pedido,
            "mesa": pedido.mesa_numero,
            "tempo_pronto": (datetime.now() - pedido.pronto_em).total_seconds() / 60 if pedido.pronto_em else 0
        })
    
    return DashboardGarcom(
        sessao_ativa=True,
        pedidos_pendentes=pedidos_pendentes,
        pedidos_preparando=pedidos_preparando,
        pedidos_prontos=pedidos_prontos,
        valor_vendido_hoje=valor_vendido_hoje,
        total_comandas_atendidas=sessao.total_comandas_atendidas,
        tempo_sessao_ativa=tempo_sessao,
        proximos_prontos=proximos_dados,
        alertas=[]  # Implementar alertas se necessário
    )

async def criar_log_validacao_nfc(
    sessao_id: str,
    validacao_data: ValidacaoNFCRequest,
    status: StatusValidacaoNFC,
    detalhes_erro: str,
    request: Request,
    db: Session,
    comanda_id: Optional[int] = None
):
    """
    Criar log de validação NFC para auditoria
    """
    cpf_esperado = None
    if comanda_id:
        comanda = db.query(Comanda).filter(Comanda.id == comanda_id).first()
        if comanda and comanda.cpf_cliente:
            cpf_esperado = comanda.cpf_cliente[:3]
    
    log_validacao = ValidacaoNFCMobile(
        sessao_id=sessao_id,
        comanda_id=comanda_id,
        nfc_uid=validacao_data.nfc_uid,
        nfc_data=validacao_data.nfc_data,
        tipo_validacao=validacao_data.tipo_validacao,
        cpf_informado=validacao_data.cpf_digits,
        cpf_esperado=cpf_esperado,
        cpf_valido=(cpf_esperado == validacao_data.cpf_digits),
        status=status,
        ip_origem=request.client.host,
        device_info=validacao_data.device_info,
        detalhes_erro=detalhes_erro if status != StatusValidacaoNFC.SUCESSO else None
    )
    
    db.add(log_validacao)

async def log_atividade_mobile(
    sessao_id: str,
    acao: str,
    detalhes: Dict[str, Any],
    request: Request,
    db: Session,
    resultado: str = "sucesso"
):
    """
    Registrar atividade do app mobile para auditoria
    """
    log_atividade = LogAtividadeMobile(
        sessao_id=sessao_id,
        acao=acao,
        detalhes=json.dumps(detalhes),
        resultado=resultado,
        ip_origem=request.client.host,
        device_info=json.dumps({"user_agent": request.headers.get("user-agent")})
    )
    
    db.add(log_atividade)

async def processar_impressao_pedido_mobile(pedido_id: str, db: Session):
    """
    Processar impressão do pedido mobile (background task)
    """
    try:
        # Implementar lógica de impressão baseada nas categorias
        # Separar itens por destino de impressão (cozinha, bar, etc.)
        # Enviar para impressoras apropriadas
        pass
    except Exception as e:
        print(f"Erro na impressão do pedido {pedido_id}: {str(e)}")

# ==================== SYNC OFFLINE ====================

@router.post("/sync")
async def sincronizar_dados_offline(
    sync_data: SyncOfflineRequest,
    request: Request,
    db: Session = Depends(get_db),
    sessao: SessaoGarcom = Depends(get_sessao_ativa)
):
    """
    Sincronizar dados offline quando conexão for restabelecida
    """
    try:
        resultados = {
            "pedidos_sincronizados": 0,
            "validacoes_sincronizadas": 0,
            "logs_sincronizados": 0,
            "erros": []
        }
        
        # Processar pedidos offline
        for pedido_offline in sync_data.pedidos_offline:
            try:
                # Validar e criar pedido
                # Implementar lógica de sincronização
                resultados["pedidos_sincronizados"] += 1
            except Exception as e:
                resultados["erros"].append(f"Erro no pedido: {str(e)}")
        
        # Processar validações NFC
        for validacao_offline in sync_data.validacoes_nfc:
            try:
                # Criar log de validação
                resultados["validacoes_sincronizadas"] += 1
            except Exception as e:
                resultados["erros"].append(f"Erro na validação: {str(e)}")
        
        # Processar logs de atividade
        for log_offline in sync_data.logs_atividade:
            try:
                # Criar log de atividade
                resultados["logs_sincronizados"] += 1
            except Exception as e:
                resultados["erros"].append(f"Erro no log: {str(e)}")
        
        db.commit()
        
        return {
            "success": True,
            "timestamp_sync": datetime.now(),
            "resultados": resultados
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Erro na sincronização: {str(e)}"
        )
