from fastapi import APIRouter, HTTPException, Depends, Query, Body
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime, date, timedelta
from decimal import Decimal
from pydantic import BaseModel
from database import get_db

router = APIRouter(prefix="/api/financeiro", tags=["Financeiro"])

# Schemas - Conta Digital
class ContaDigital(BaseModel):
    id: Optional[int] = None
    banco: str
    agencia: str
    conta: str
    tipo: str  # CORRENTE, POUPANCA, PAGAMENTO
    titular: str
    documento: str
    saldo_atual: float
    limite_credito: Optional[float]
    status: str  # ATIVA, INATIVA, BLOQUEADA
    integrada: bool = False
    token_api: Optional[str]

class TransacaoContaDigital(BaseModel):
    id: Optional[int] = None
    conta_id: int
    tipo: str  # PIX, TED, BOLETO, CARTAO
    operacao: str  # ENTRADA, SAIDA
    valor: float
    descricao: str
    destinatario: Optional[str]
    chave_pix: Optional[str]
    comprovante: Optional[str]
    status: str  # PENDENTE, PROCESSANDO, CONCLUIDA, FALHA
    data_transacao: datetime
    taxa: float = 0.0

# Schemas - Permutas
class Permuta(BaseModel):
    id: Optional[int] = None
    codigo: str
    tipo: str  # PRODUTO, SERVICO, MISTO
    parceiro: str
    documento_parceiro: str
    valor_entrada: float
    valor_saida: float
    saldo: float
    descricao: str
    validade: Optional[date]
    status: str  # ATIVA, UTILIZADA, EXPIRADA, CANCELADA
    contrato_url: Optional[str]

class MovimentoPermuta(BaseModel):
    id: Optional[int] = None
    permuta_id: int
    tipo: str  # UTILIZACAO, DEVOLUCAO, AJUSTE
    valor: float
    descricao: str
    responsavel: str
    data_movimento: datetime
    saldo_anterior: float
    saldo_atual: float

# Schemas - Antecipação de Recebíveis
class Antecipacao(BaseModel):
    id: Optional[int] = None
    tipo_recebiveis: str  # CARTAO_CREDITO, CARTAO_DEBITO, BOLETO, DUPLICATA
    valor_total: float
    valor_liquido: float
    taxa_antecipacao: float
    taxa_valor: float
    prazo_original: int  # dias
    data_vencimento_original: date
    data_antecipacao: date
    instituicao: str
    status: str  # SOLICITADA, APROVADA, LIQUIDADA, REJEITADA
    observacoes: Optional[str]

class SimulacaoAntecipacao(BaseModel):
    tipo_recebiveis: str
    valor_total: float
    prazo: int  # dias
    instituicao: Optional[str]

# Schemas - Taxas
class TaxaOperacao(BaseModel):
    id: Optional[int] = None
    nome: str
    tipo: str  # PERCENTUAL, FIXO
    categoria: str  # CARTAO, PIX, BOLETO, ANTECIPACAO
    valor: float
    valor_minimo: Optional[float]
    valor_maximo: Optional[float]
    vigencia_inicio: date
    vigencia_fim: Optional[date]
    fornecedor: Optional[str]
    ativo: bool = True

# Schemas - Split de Pagamento
class RegraSplit(BaseModel):
    id: Optional[int] = None
    nome: str
    tipo_divisao: str  # PERCENTUAL, VALOR_FIXO
    participantes: List[Dict[str, Any]]  # [{nome, documento, percentual/valor, conta_bancaria}]
    regra_padrao: bool = False
    categoria_aplicacao: Optional[str]  # EVENTOS, PRODUTOS, SERVICOS
    ativo: bool = True

class TransacaoSplit(BaseModel):
    id: Optional[int] = None
    transacao_original_id: int
    valor_total: float
    regra_split_id: int
    divisoes: List[Dict[str, Any]]
    status: str  # PENDENTE, PROCESSADO, ERRO
    data_processamento: Optional[datetime]

# Conta Digital
@router.post("/conta-digital/contas")
async def criar_conta_digital(conta: ContaDigital, db: Session = Depends(get_db)):
    return {
        "id": 1,
        **conta.dict(),
        "created_at": datetime.now()
    }

@router.get("/conta-digital/contas")
async def listar_contas_digitais(
    status: Optional[str] = None,
    integrada: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    contas = [
        {
            "id": 1,
            "banco": "Banco Inter",
            "agencia": "0001",
            "conta": "123456-7",
            "tipo": "CORRENTE",
            "titular": "Empresa XYZ LTDA",
            "saldo_atual": 45678.90,
            "limite_credito": 10000.00,
            "status": "ATIVA",
            "integrada": True
        },
        {
            "id": 2,
            "banco": "Nubank",
            "agencia": "0001",
            "conta": "987654-3",
            "tipo": "PAGAMENTO",
            "titular": "Empresa XYZ LTDA",
            "saldo_atual": 12345.67,
            "status": "ATIVA",
            "integrada": True
        }
    ]

    if status:
        contas = [c for c in contas if c["status"] == status]

    return contas

@router.get("/conta-digital/contas/{conta_id}/saldo")
async def obter_saldo_conta(conta_id: int, db: Session = Depends(get_db)):
    return {
        "conta_id": conta_id,
        "saldo_disponivel": 45678.90,
        "saldo_bloqueado": 1500.00,
        "limite_disponivel": 8500.00,
        "limite_total": 10000.00,
        "atualizado_em": datetime.now()
    }

@router.post("/conta-digital/transacoes")
async def criar_transacao(transacao: TransacaoContaDigital, db: Session = Depends(get_db)):
    return {
        "id": 1,
        **transacao.dict(),
        "numero_protocolo": "TRX202401150001",
        "created_at": datetime.now()
    }

@router.get("/conta-digital/transacoes")
async def listar_transacoes_conta(
    conta_id: Optional[int] = None,
    tipo: Optional[str] = None,
    operacao: Optional[str] = None,
    data_inicio: Optional[date] = None,
    data_fim: Optional[date] = None,
    db: Session = Depends(get_db)
):
    return [
        {
            "id": 1,
            "conta": "Banco Inter - 123456-7",
            "tipo": "PIX",
            "operacao": "ENTRADA",
            "valor": 1500.00,
            "descricao": "Pagamento Cliente ABC",
            "chave_pix": "empresa@email.com",
            "status": "CONCLUIDA",
            "data_transacao": "2024-01-15T10:30:00",
            "taxa": 0.00
        },
        {
            "id": 2,
            "conta": "Banco Inter - 123456-7",
            "tipo": "TED",
            "operacao": "SAIDA",
            "valor": 5000.00,
            "descricao": "Pagamento Fornecedor XYZ",
            "destinatario": "Fornecedor XYZ LTDA",
            "status": "CONCLUIDA",
            "data_transacao": "2024-01-15T14:20:00",
            "taxa": 15.90
        }
    ]

@router.post("/conta-digital/pix")
async def realizar_pix(
    conta_id: int = Body(...),
    valor: float = Body(...),
    chave_pix: str = Body(...),
    descricao: str = Body(...),
    db: Session = Depends(get_db)
):
    return {
        "transacao_id": "PIX202401150001",
        "status": "PROCESSANDO",
        "valor": valor,
        "chave_pix": chave_pix,
        "tempo_estimado": "Instantâneo",
        "taxa": 0.00
    }

@router.get("/conta-digital/extrato")
async def obter_extrato(
    conta_id: int,
    data_inicio: date = Query(...),
    data_fim: date = Query(...),
    db: Session = Depends(get_db)
):
    return {
        "conta_id": conta_id,
        "periodo": f"{data_inicio} a {data_fim}",
        "saldo_inicial": 40000.00,
        "saldo_final": 45678.90,
        "total_entradas": 15000.00,
        "total_saidas": 9321.10,
        "transacoes": [
            {
                "data": "2024-01-15",
                "descricao": "PIX Recebido",
                "valor": 1500.00,
                "saldo": 41500.00
            }
        ]
    }

# Permutas
@router.post("/permutas")
async def criar_permuta(permuta: Permuta, db: Session = Depends(get_db)):
    return {
        "id": 1,
        **permuta.dict(),
        "created_at": datetime.now()
    }

@router.get("/permutas")
async def listar_permutas(
    status: Optional[str] = None,
    tipo: Optional[str] = None,
    vencidas: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    permutas = [
        {
            "id": 1,
            "codigo": "PERM-2024-001",
            "tipo": "SERVICO",
            "parceiro": "Agência de Marketing ABC",
            "valor_entrada": 10000.00,
            "valor_saida": 2500.00,
            "saldo": 7500.00,
            "percentual_utilizado": 25,
            "descricao": "Permuta de serviços de marketing",
            "validade": "2024-12-31",
            "status": "ATIVA"
        },
        {
            "id": 2,
            "codigo": "PERM-2024-002",
            "tipo": "PRODUTO",
            "parceiro": "Fornecedor XYZ",
            "valor_entrada": 5000.00,
            "valor_saida": 5000.00,
            "saldo": 0.00,
            "percentual_utilizado": 100,
            "descricao": "Permuta de produtos",
            "status": "UTILIZADA"
        }
    ]

    if status:
        permutas = [p for p in permutas if p["status"] == status]

    return permutas

@router.post("/permutas/{permuta_id}/movimentos")
async def registrar_movimento_permuta(
    permuta_id: int,
    movimento: MovimentoPermuta,
    db: Session = Depends(get_db)
):
    return {
        "id": 1,
        "permuta_id": permuta_id,
        **movimento.dict(),
        "created_at": datetime.now()
    }

@router.get("/permutas/{permuta_id}/historico")
async def obter_historico_permuta(permuta_id: int, db: Session = Depends(get_db)):
    return {
        "permuta_id": permuta_id,
        "codigo": "PERM-2024-001",
        "saldo_atual": 7500.00,
        "movimentos": [
            {
                "id": 1,
                "tipo": "UTILIZACAO",
                "valor": 2500.00,
                "descricao": "Pagamento parcial de serviços",
                "data": "2024-01-10T15:30:00",
                "responsavel": "João Silva",
                "saldo_apos": 7500.00
            }
        ]
    }

# Antecipação de Recebíveis
@router.post("/antecipacao/simular")
async def simular_antecipacao(simulacao: SimulacaoAntecipacao, db: Session = Depends(get_db)):
    taxa_base = 2.5  # % ao mês
    taxa_dia = taxa_base / 30
    taxa_total = (taxa_dia * simulacao.prazo) / 100
    valor_taxa = simulacao.valor_total * taxa_total
    valor_liquido = simulacao.valor_total - valor_taxa

    return {
        "valor_total": simulacao.valor_total,
        "prazo_dias": simulacao.prazo,
        "taxa_aplicada": f"{taxa_dia * simulacao.prazo:.2f}%",
        "valor_taxa": round(valor_taxa, 2),
        "valor_liquido": round(valor_liquido, 2),
        "data_credito": date.today() + timedelta(days=1),
        "instituicoes_disponiveis": [
            {
                "nome": "Banco A",
                "taxa": f"{taxa_base}%",
                "valor_liquido": round(valor_liquido, 2),
                "prazo_credito": "1 dia útil"
            },
            {
                "nome": "Banco B",
                "taxa": f"{taxa_base - 0.3}%",
                "valor_liquido": round(simulacao.valor_total * (1 - ((taxa_base - 0.3) / 30 * simulacao.prazo / 100)), 2),
                "prazo_credito": "2 dias úteis"
            }
        ]
    }

@router.post("/antecipacao")
async def solicitar_antecipacao(antecipacao: Antecipacao, db: Session = Depends(get_db)):
    return {
        "id": 1,
        **antecipacao.dict(),
        "protocolo": "ANT202401150001",
        "previsao_credito": date.today() + timedelta(days=1),
        "created_at": datetime.now()
    }

@router.get("/antecipacao")
async def listar_antecipacoes(
    status: Optional[str] = None,
    tipo_recebiveis: Optional[str] = None,
    data_inicio: Optional[date] = None,
    data_fim: Optional[date] = None,
    db: Session = Depends(get_db)
):
    return [
        {
            "id": 1,
            "protocolo": "ANT202401100001",
            "tipo_recebiveis": "CARTAO_CREDITO",
            "valor_total": 50000.00,
            "valor_liquido": 48500.00,
            "taxa_valor": 1500.00,
            "taxa_percentual": 3.0,
            "prazo_original": 30,
            "data_antecipacao": "2024-01-10",
            "instituicao": "Banco A",
            "status": "LIQUIDADA"
        }
    ]

@router.get("/antecipacao/limites")
async def obter_limites_antecipacao(db: Session = Depends(get_db)):
    return {
        "limite_total": 500000.00,
        "limite_utilizado": 150000.00,
        "limite_disponivel": 350000.00,
        "limites_por_tipo": [
            {
                "tipo": "CARTAO_CREDITO",
                "limite": 300000.00,
                "utilizado": 100000.00,
                "disponivel": 200000.00
            },
            {
                "tipo": "CARTAO_DEBITO",
                "limite": 100000.00,
                "utilizado": 30000.00,
                "disponivel": 70000.00
            },
            {
                "tipo": "BOLETO",
                "limite": 100000.00,
                "utilizado": 20000.00,
                "disponivel": 80000.00
            }
        ]
    }

# Taxas
@router.post("/taxas")
async def criar_taxa(taxa: TaxaOperacao, db: Session = Depends(get_db)):
    return {
        "id": 1,
        **taxa.dict(),
        "created_at": datetime.now()
    }

@router.get("/taxas")
async def listar_taxas(
    categoria: Optional[str] = None,
    ativo: bool = True,
    db: Session = Depends(get_db)
):
    taxas = [
        {
            "id": 1,
            "nome": "Taxa PIX",
            "tipo": "FIXO",
            "categoria": "PIX",
            "valor": 0.00,
            "fornecedor": "Banco Inter",
            "ativo": True
        },
        {
            "id": 2,
            "nome": "Taxa Cartão Crédito",
            "tipo": "PERCENTUAL",
            "categoria": "CARTAO",
            "valor": 2.99,
            "fornecedor": "Stone",
            "ativo": True
        },
        {
            "id": 3,
            "nome": "Taxa Cartão Débito",
            "tipo": "PERCENTUAL",
            "categoria": "CARTAO",
            "valor": 1.49,
            "fornecedor": "Stone",
            "ativo": True
        },
        {
            "id": 4,
            "nome": "Taxa Antecipação",
            "tipo": "PERCENTUAL",
            "categoria": "ANTECIPACAO",
            "valor": 2.5,
            "observacao": "Por mês",
            "ativo": True
        }
    ]

    if categoria:
        taxas = [t for t in taxas if t["categoria"] == categoria]

    return taxas

@router.get("/taxas/calcular")
async def calcular_taxa(
    tipo_operacao: str = Query(...),
    valor: float = Query(...),
    prazo: Optional[int] = None,
    db: Session = Depends(get_db)
):
    taxas_map = {
        "PIX": 0.00,
        "CARTAO_CREDITO": 2.99,
        "CARTAO_DEBITO": 1.49,
        "BOLETO": 3.49,
        "TED": 15.90
    }

    if tipo_operacao == "ANTECIPACAO" and prazo:
        taxa_mes = 2.5
        taxa_total = (taxa_mes / 30) * prazo
        valor_taxa = valor * (taxa_total / 100)
    elif tipo_operacao in ["TED"]:
        valor_taxa = taxas_map.get(tipo_operacao, 0)
    else:
        taxa_percentual = taxas_map.get(tipo_operacao, 0)
        valor_taxa = valor * (taxa_percentual / 100)

    return {
        "tipo_operacao": tipo_operacao,
        "valor_operacao": valor,
        "taxa_aplicada": taxas_map.get(tipo_operacao, 0),
        "valor_taxa": round(valor_taxa, 2),
        "valor_liquido": round(valor - valor_taxa, 2)
    }

# Split de Pagamento
@router.post("/split/regras")
async def criar_regra_split(regra: RegraSplit, db: Session = Depends(get_db)):
    return {
        "id": 1,
        **regra.dict(),
        "created_at": datetime.now()
    }

@router.get("/split/regras")
async def listar_regras_split(
    ativo: bool = True,
    categoria: Optional[str] = None,
    db: Session = Depends(get_db)
):
    return [
        {
            "id": 1,
            "nome": "Split Padrão Eventos",
            "tipo_divisao": "PERCENTUAL",
            "categoria_aplicacao": "EVENTOS",
            "participantes": [
                {"nome": "Organizador Principal", "percentual": 70},
                {"nome": "Plataforma", "percentual": 20},
                {"nome": "Produtor", "percentual": 10}
            ],
            "regra_padrao": True,
            "ativo": True
        },
        {
            "id": 2,
            "nome": "Split Bar Premium",
            "tipo_divisao": "PERCENTUAL",
            "categoria_aplicacao": "PRODUTOS",
            "participantes": [
                {"nome": "Casa", "percentual": 60},
                {"nome": "Bartender", "percentual": 40}
            ],
            "ativo": True
        }
    ]

@router.post("/split/processar")
async def processar_split(
    transacao_id: int = Body(...),
    regra_id: int = Body(...),
    valor_total: float = Body(...),
    db: Session = Depends(get_db)
):
    return {
        "transacao_split_id": 1,
        "transacao_original_id": transacao_id,
        "valor_total": valor_total,
        "divisoes": [
            {
                "participante": "Organizador Principal",
                "valor": valor_total * 0.7,
                "status": "PROCESSADO",
                "conta_credito": "123456-7"
            },
            {
                "participante": "Plataforma",
                "valor": valor_total * 0.2,
                "status": "PROCESSADO",
                "conta_credito": "987654-3"
            },
            {
                "participante": "Produtor",
                "valor": valor_total * 0.1,
                "status": "PENDENTE",
                "conta_credito": "456789-0"
            }
        ],
        "status": "PROCESSADO",
        "data_processamento": datetime.now()
    }

@router.get("/split/transacoes")
async def listar_transacoes_split(
    status: Optional[str] = None,
    data_inicio: Optional[date] = None,
    data_fim: Optional[date] = None,
    db: Session = Depends(get_db)
):
    return [
        {
            "id": 1,
            "transacao_original": "TRX-2024-001",
            "valor_total": 1000.00,
            "regra": "Split Padrão Eventos",
            "participantes": 3,
            "status": "PROCESSADO",
            "data": "2024-01-15T20:30:00"
        }
    ]

# Direcionamento de Transações
@router.post("/direcionamento/configurar")
async def configurar_direcionamento(
    tipo_transacao: str = Body(...),
    conta_destino_id: int = Body(...),
    condicoes: Optional[Dict] = Body(None),
    db: Session = Depends(get_db)
):
    return {
        "id": 1,
        "tipo_transacao": tipo_transacao,
        "conta_destino_id": conta_destino_id,
        "condicoes": condicoes,
        "ativo": True,
        "created_at": datetime.now()
    }

@router.get("/direcionamento/regras")
async def listar_regras_direcionamento(db: Session = Depends(get_db)):
    return [
        {
            "id": 1,
            "tipo_transacao": "PIX_ENTRADA",
            "conta_destino": "Banco Inter - 123456-7",
            "condicoes": {"valor_minimo": 100.00},
            "ativo": True
        },
        {
            "id": 2,
            "tipo_transacao": "CARTAO_CREDITO",
            "conta_destino": "Stone - Conta Pagamento",
            "ativo": True
        }
    ]

# Link de Pagamento
@router.post("/links-pagamento")
async def criar_link_pagamento(
    valor: float = Body(...),
    descricao: str = Body(...),
    vencimento: Optional[date] = Body(None),
    split_id: Optional[int] = Body(None),
    db: Session = Depends(get_db)
):
    return {
        "id": 1,
        "codigo": "LINK-2024-0001",
        "url": "https://pay.meep.com.br/LINK-2024-0001",
        "qrcode": "data:image/png;base64,iVBORw0KGgoAAAANS...",
        "valor": valor,
        "descricao": descricao,
        "vencimento": vencimento,
        "status": "ATIVO",
        "created_at": datetime.now()
    }

@router.get("/links-pagamento")
async def listar_links_pagamento(
    status: Optional[str] = None,
    vencidos: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    return [
        {
            "id": 1,
            "codigo": "LINK-2024-0001",
            "descricao": "Pagamento Evento XYZ",
            "valor": 150.00,
            "valor_pago": 0.00,
            "status": "ATIVO",
            "vencimento": "2024-01-30",
            "criado_em": "2024-01-15T10:00:00",
            "acessos": 5
        }
    ]

@router.get("/links-pagamento/{link_id}/transacoes")
async def obter_transacoes_link(link_id: int, db: Session = Depends(get_db)):
    return {
        "link_id": link_id,
        "total_pago": 150.00,
        "quantidade_pagamentos": 1,
        "transacoes": [
            {
                "id": 1,
                "data": "2024-01-16T14:30:00",
                "valor": 150.00,
                "forma_pagamento": "PIX",
                "pagador": "João Silva",
                "status": "APROVADO"
            }
        ]
    }

# Estorno de Transações
@router.post("/estornos")
async def solicitar_estorno(
    transacao_id: int = Body(...),
    motivo: str = Body(...),
    valor_parcial: Optional[float] = Body(None),
    db: Session = Depends(get_db)
):
    return {
        "id": 1,
        "transacao_id": transacao_id,
        "protocolo": "EST-2024-0001",
        "valor_estorno": valor_parcial or 150.00,
        "motivo": motivo,
        "status": "PROCESSANDO",
        "previsao_conclusao": datetime.now() + timedelta(days=3),
        "created_at": datetime.now()
    }

@router.get("/estornos")
async def listar_estornos(
    status: Optional[str] = None,
    data_inicio: Optional[date] = None,
    data_fim: Optional[date] = None,
    db: Session = Depends(get_db)
):
    return [
        {
            "id": 1,
            "protocolo": "EST-2024-0001",
            "transacao": "TRX-2024-001",
            "valor_original": 150.00,
            "valor_estorno": 150.00,
            "tipo": "TOTAL",
            "motivo": "Cliente solicitou cancelamento",
            "status": "CONCLUIDO",
            "data_solicitacao": "2024-01-15T16:00:00",
            "data_conclusao": "2024-01-16T10:00:00"
        }
    ]

# Faturas
@router.get("/faturas")
async def listar_faturas(
    status: Optional[str] = None,
    vencimento_inicio: Optional[date] = None,
    vencimento_fim: Optional[date] = None,
    db: Session = Depends(get_db)
):
    return [
        {
            "id": 1,
            "numero": "FAT-2024-001",
            "cliente": "Cliente ABC",
            "valor_total": 5000.00,
            "valor_pago": 2500.00,
            "valor_pendente": 2500.00,
            "vencimento": "2024-01-31",
            "status": "PARCIALMENTE_PAGO",
            "dias_atraso": 0
        }
    ]

@router.post("/faturas/{fatura_id}/pagamento")
async def registrar_pagamento_fatura(
    fatura_id: int,
    valor: float = Body(...),
    forma_pagamento: str = Body(...),
    db: Session = Depends(get_db)
):
    return {
        "fatura_id": fatura_id,
        "pagamento_id": 1,
        "valor": valor,
        "forma_pagamento": forma_pagamento,
        "saldo_restante": 0.00,
        "status_fatura": "PAGO",
        "data_pagamento": datetime.now()
    }

# Relatórios Financeiros
@router.get("/relatorios/fluxo-caixa")
async def relatorio_fluxo_caixa(
    data_inicio: date = Query(...),
    data_fim: date = Query(...),
    db: Session = Depends(get_db)
):
    return {
        "periodo": f"{data_inicio} a {data_fim}",
        "saldo_inicial": 45000.00,
        "total_entradas": 125000.00,
        "total_saidas": 98000.00,
        "saldo_final": 72000.00,
        "fluxo_diario": [
            {
                "data": "2024-01-15",
                "entradas": 15000.00,
                "saidas": 8500.00,
                "saldo": 51500.00
            }
        ],
        "categorias_entrada": [
            {"categoria": "Vendas", "valor": 100000.00, "percentual": 80},
            {"categoria": "Serviços", "valor": 25000.00, "percentual": 20}
        ],
        "categorias_saida": [
            {"categoria": "Fornecedores", "valor": 45000.00, "percentual": 45.9},
            {"categoria": "Folha", "valor": 30000.00, "percentual": 30.6},
            {"categoria": "Impostos", "valor": 23000.00, "percentual": 23.5}
        ]
    }

@router.get("/relatorios/dre")
async def relatorio_dre(
    mes: int = Query(...),
    ano: int = Query(...),
    db: Session = Depends(get_db)
):
    return {
        "periodo": f"{mes}/{ano}",
        "receita_bruta": 150000.00,
        "deducoes": 15000.00,
        "receita_liquida": 135000.00,
        "custo_produtos": 45000.00,
        "lucro_bruto": 90000.00,
        "despesas_operacionais": {
            "vendas": 15000.00,
            "administrativas": 20000.00,
            "financeiras": 5000.00
        },
        "lucro_operacional": 50000.00,
        "impostos": 15000.00,
        "lucro_liquido": 35000.00,
        "margem_liquida": 23.33
    }

@router.get("/relatorios/contas-pagar-receber")
async def relatorio_contas(
    tipo: str = Query(...),  # PAGAR, RECEBER
    db: Session = Depends(get_db)
):
    if tipo == "RECEBER":
        return {
            "total_receber": 75000.00,
            "vencidas": 5000.00,
            "a_vencer_30_dias": 25000.00,
            "a_vencer_60_dias": 45000.00,
            "idade_media": 35,
            "principais_devedores": [
                {"cliente": "Cliente A", "valor": 15000.00, "dias_atraso": 5}
            ]
        }
    else:
        return {
            "total_pagar": 45000.00,
            "vencidas": 2000.00,
            "a_vencer_30_dias": 20000.00,
            "a_vencer_60_dias": 23000.00,
            "principais_credores": [
                {"fornecedor": "Fornecedor X", "valor": 10000.00, "vencimento": "2024-01-25"}
            ]
        }