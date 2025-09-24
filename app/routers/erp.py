from fastapi import APIRouter, HTTPException, Depends, Query, Body, File, UploadFile
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime, date, timedelta
from pydantic import BaseModel
from app.database import get_db

router = APIRouter(prefix="/api/erp", tags=["Sistema ERP"])

# Schemas - Módulos ERP
class ModuloERP(BaseModel):
    id: Optional[int] = None
    nome: str
    descricao: Optional[str]
    versao: str
    ativo: bool = True
    configuracoes: Optional[Dict]
    permissoes: Optional[List[str]]

class IntegracaoERP(BaseModel):
    id: Optional[int] = None
    sistema: str  # SAP, TOTVS, ORACLE, DYNAMICS, SENIOR, etc
    tipo: str  # FISCAL, CONTABIL, ESTOQUE, FINANCEIRO, RH
    endpoint: str
    credenciais: Dict
    mapeamento: Dict
    ativo: bool = True
    ultima_sincronizacao: Optional[datetime]

class NotaFiscal(BaseModel):
    id: Optional[int] = None
    numero: str
    serie: str
    tipo: str  # NFE, NFCE, NFSE, CTE
    natureza_operacao: str
    cliente_fornecedor: Dict
    itens: List[Dict]
    valor_total: float
    impostos: Dict
    status: str  # RASCUNHO, AUTORIZADA, CANCELADA, DENEGADA
    xml: Optional[str]
    pdf_url: Optional[str]
    data_emissao: datetime
    chave_acesso: Optional[str]

class PlanoContas(BaseModel):
    id: Optional[int] = None
    codigo: str
    descricao: str
    tipo: str  # RECEITA, DESPESA, ATIVO, PASSIVO
    nivel: int
    conta_pai_id: Optional[int]
    natureza: str
    ativo: bool = True

class LancamentoContabil(BaseModel):
    id: Optional[int] = None
    data: date
    documento: str
    descricao: str
    conta_debito: str
    conta_credito: str
    valor: float
    historico: str
    centro_custo: Optional[str]
    conciliado: bool = False

class CentroCusto(BaseModel):
    id: Optional[int] = None
    codigo: str
    nome: str
    tipo: str  # PRODUCAO, ADMINISTRATIVO, COMERCIAL, OPERACIONAL
    responsavel: str
    orcamento_mensal: Optional[float]
    ativo: bool = True

class OrdemProducao(BaseModel):
    id: Optional[int] = None
    numero: str
    produto_id: int
    quantidade: float
    data_inicio: datetime
    data_prevista: datetime
    data_conclusao: Optional[datetime]
    status: str  # PLANEJADA, EM_PRODUCAO, PAUSADA, CONCLUIDA, CANCELADA
    custo_estimado: float
    custo_real: Optional[float]
    observacoes: Optional[str]

# Configuração e Módulos
@router.get("/modulos")
async def listar_modulos_erp(db: Session = Depends(get_db)):
    return [
        {
            "id": 1,
            "nome": "Fiscal",
            "descricao": "Módulo de gestão fiscal e tributária",
            "versao": "2.5.0",
            "ativo": True,
            "recursos": [
                "Emissão de NF-e/NFC-e",
                "Cálculo automático de impostos",
                "SPED Fiscal",
                "Livros fiscais"
            ],
            "status": "ATIVO"
        },
        {
            "id": 2,
            "nome": "Contábil",
            "descricao": "Módulo de contabilidade",
            "versao": "2.3.0",
            "ativo": True,
            "recursos": [
                "Plano de contas",
                "Lançamentos contábeis",
                "Balanço patrimonial",
                "DRE"
            ],
            "status": "ATIVO"
        },
        {
            "id": 3,
            "nome": "Produção",
            "descricao": "Módulo de controle de produção",
            "versao": "1.8.0",
            "ativo": True,
            "recursos": [
                "Ordens de produção",
                "Controle de processos",
                "Custo de produção",
                "MRP"
            ],
            "status": "ATIVO"
        },
        {
            "id": 4,
            "nome": "RH",
            "descricao": "Módulo de recursos humanos",
            "versao": "3.1.0",
            "ativo": True,
            "recursos": [
                "Folha de pagamento",
                "Ponto eletrônico",
                "Férias e benefícios",
                "eSocial"
            ],
            "status": "ATIVO"
        },
        {
            "id": 5,
            "nome": "CRM",
            "descricao": "Gestão de relacionamento com cliente",
            "versao": "2.0.0",
            "ativo": True,
            "recursos": [
                "Pipeline de vendas",
                "Gestão de leads",
                "Automação de marketing",
                "Análise de vendas"
            ],
            "status": "ATIVO"
        }
    ]

@router.put("/modulos/{modulo_id}/configurar")
async def configurar_modulo(
    modulo_id: int,
    configuracoes: Dict,
    db: Session = Depends(get_db)
):
    return {
        "modulo_id": modulo_id,
        "configuracoes": configuracoes,
        "aplicado": True,
        "updated_at": datetime.now()
    }

# Integrações
@router.post("/integracoes")
async def criar_integracao(integracao: IntegracaoERP, db: Session = Depends(get_db)):
    return {
        "id": 1,
        **integracao.dict(),
        "teste_conexao": "SUCESSO",
        "created_at": datetime.now()
    }

@router.get("/integracoes")
async def listar_integracoes(
    ativo: bool = True,
    db: Session = Depends(get_db)
):
    return [
        {
            "id": 1,
            "sistema": "TOTVS Protheus",
            "tipo": "COMPLETA",
            "modulos": ["Fiscal", "Contábil", "Estoque", "Financeiro"],
            "status_conexao": "ONLINE",
            "ultima_sincronizacao": "2024-01-15T22:00:00",
            "registros_sincronizados": {
                "produtos": 1250,
                "clientes": 3100,
                "notas_fiscais": 450,
                "lancamentos": 2300
            },
            "ativo": True
        },
        {
            "id": 2,
            "sistema": "SAP Business One",
            "tipo": "FINANCEIRO",
            "modulos": ["Contas a Pagar", "Contas a Receber"],
            "status_conexao": "ONLINE",
            "ultima_sincronizacao": "2024-01-15T21:30:00",
            "ativo": True
        }
    ]

@router.post("/integracoes/{integracao_id}/sincronizar")
async def sincronizar_integracao(
    integracao_id: int,
    tipo_sincronizacao: str = Body(...),  # COMPLETA, INCREMENTAL, ESPECIFICA
    entidades: Optional[List[str]] = Body(None),
    db: Session = Depends(get_db)
):
    return {
        "integracao_id": integracao_id,
        "tipo": tipo_sincronizacao,
        "inicio": datetime.now(),
        "status": "EM_ANDAMENTO",
        "estimativa_minutos": 15,
        "job_id": "SYNC-2024-001"
    }

@router.get("/integracoes/{integracao_id}/log")
async def obter_log_integracao(
    integracao_id: int,
    data_inicio: Optional[date] = None,
    data_fim: Optional[date] = None,
    db: Session = Depends(get_db)
):
    return [
        {
            "id": 1,
            "timestamp": "2024-01-15T22:00:00",
            "tipo": "SINCRONIZACAO",
            "status": "SUCESSO",
            "mensagem": "Sincronização completa realizada",
            "detalhes": {
                "produtos_atualizados": 45,
                "clientes_novos": 12,
                "erros": 0
            }
        },
        {
            "id": 2,
            "timestamp": "2024-01-15T21:45:00",
            "tipo": "ERRO",
            "status": "FALHA",
            "mensagem": "Falha na conexão com servidor",
            "detalhes": {"erro": "Timeout na conexão"}
        }
    ]

# Fiscal - Notas Fiscais
@router.post("/fiscal/notas")
async def emitir_nota_fiscal(nota: NotaFiscal, db: Session = Depends(get_db)):
    return {
        "id": 1,
        **nota.dict(),
        "protocolo_autorizacao": "123456789",
        "chave_acesso": "35240112345678901234550010000001234123456789",
        "qrcode": "https://nfe.fazenda.gov.br/qrcode?...",
        "created_at": datetime.now()
    }

@router.get("/fiscal/notas")
async def listar_notas_fiscais(
    tipo: Optional[str] = None,
    status: Optional[str] = None,
    data_inicio: Optional[date] = None,
    data_fim: Optional[date] = None,
    db: Session = Depends(get_db)
):
    return [
        {
            "id": 1,
            "numero": "001234",
            "serie": "1",
            "tipo": "NFE",
            "cliente": "Cliente ABC LTDA",
            "valor_total": 5000.00,
            "status": "AUTORIZADA",
            "data_emissao": "2024-01-15T10:30:00",
            "chave_acesso": "35240112345678901234550010000001234123456789"
        },
        {
            "id": 2,
            "numero": "001235",
            "serie": "1",
            "tipo": "NFCE",
            "cliente": "João Silva",
            "valor_total": 150.00,
            "status": "AUTORIZADA",
            "data_emissao": "2024-01-15T14:20:00"
        }
    ]

@router.post("/fiscal/notas/{nota_id}/cancelar")
async def cancelar_nota_fiscal(
    nota_id: int,
    justificativa: str = Body(...),
    db: Session = Depends(get_db)
):
    return {
        "nota_id": nota_id,
        "protocolo_cancelamento": "987654321",
        "status": "CANCELADA",
        "data_cancelamento": datetime.now()
    }

@router.get("/fiscal/impostos/calcular")
async def calcular_impostos(
    valor_base: float = Query(...),
    tipo_operacao: str = Query(...),
    estado_destino: str = Query(...),
    db: Session = Depends(get_db)
):
    return {
        "valor_base": valor_base,
        "impostos": {
            "icms": {
                "aliquota": 18.0,
                "valor": valor_base * 0.18,
                "base_calculo": valor_base
            },
            "pis": {
                "aliquota": 1.65,
                "valor": valor_base * 0.0165
            },
            "cofins": {
                "aliquota": 7.6,
                "valor": valor_base * 0.076
            },
            "ipi": {
                "aliquota": 5.0,
                "valor": valor_base * 0.05
            }
        },
        "valor_total_impostos": valor_base * 0.3215,
        "valor_final": valor_base * 1.3215
    }

@router.get("/fiscal/sped")
async def gerar_sped(
    tipo: str = Query(...),  # EFD_ICMS_IPI, EFD_CONTRIBUICOES
    mes: int = Query(...),
    ano: int = Query(...),
    db: Session = Depends(get_db)
):
    return {
        "arquivo": f"SPED_{tipo}_{mes:02d}{ano}.txt",
        "registros": 15234,
        "tamanho": "2.3 MB",
        "hash": "a1b2c3d4e5f6",
        "url_download": f"https://meep.com.br/sped/{tipo}_{mes:02d}{ano}.txt",
        "validade": "7 dias"
    }

# Contábil
@router.post("/contabil/plano-contas")
async def criar_conta_contabil(conta: PlanoContas, db: Session = Depends(get_db)):
    return {
        "id": 1,
        **conta.dict(),
        "created_at": datetime.now()
    }

@router.get("/contabil/plano-contas")
async def listar_plano_contas(
    tipo: Optional[str] = None,
    db: Session = Depends(get_db)
):
    return [
        {
            "id": 1,
            "codigo": "1.1.01",
            "descricao": "Caixa",
            "tipo": "ATIVO",
            "nivel": 3,
            "natureza": "DEVEDORA",
            "saldo_atual": 45678.90
        },
        {
            "id": 2,
            "codigo": "3.1.01",
            "descricao": "Receita de Vendas",
            "tipo": "RECEITA",
            "nivel": 3,
            "natureza": "CREDORA",
            "saldo_atual": 195000.00
        }
    ]

@router.post("/contabil/lancamentos")
async def criar_lancamento_contabil(
    lancamento: LancamentoContabil,
    db: Session = Depends(get_db)
):
    return {
        "id": 1,
        **lancamento.dict(),
        "numero_partida": "2024010001",
        "created_at": datetime.now()
    }

@router.get("/contabil/lancamentos")
async def listar_lancamentos_contabeis(
    data_inicio: Optional[date] = None,
    data_fim: Optional[date] = None,
    conta: Optional[str] = None,
    db: Session = Depends(get_db)
):
    return [
        {
            "id": 1,
            "data": "2024-01-15",
            "documento": "NF-001234",
            "descricao": "Venda de mercadorias",
            "conta_debito": "1.1.02",
            "conta_credito": "3.1.01",
            "valor": 5000.00,
            "historico": "Venda conforme NF 001234"
        }
    ]

@router.get("/contabil/balancete")
async def gerar_balancete(
    mes: int = Query(...),
    ano: int = Query(...),
    nivel: int = 3,
    db: Session = Depends(get_db)
):
    return {
        "periodo": f"{mes:02d}/{ano}",
        "contas": [
            {
                "codigo": "1",
                "descricao": "ATIVO",
                "saldo_anterior": 500000.00,
                "debito": 125000.00,
                "credito": 98000.00,
                "saldo_atual": 527000.00
            },
            {
                "codigo": "2",
                "descricao": "PASSIVO",
                "saldo_anterior": 300000.00,
                "debito": 45000.00,
                "credito": 52000.00,
                "saldo_atual": 307000.00
            },
            {
                "codigo": "3",
                "descricao": "RECEITAS",
                "saldo_anterior": 0.00,
                "debito": 0.00,
                "credito": 195000.00,
                "saldo_atual": 195000.00
            },
            {
                "codigo": "4",
                "descricao": "DESPESAS",
                "saldo_anterior": 0.00,
                "debito": 145000.00,
                "credito": 0.00,
                "saldo_atual": 145000.00
            }
        ],
        "resultado": 50000.00
    }

@router.get("/contabil/dre")
async def gerar_dre(
    mes: int = Query(...),
    ano: int = Query(...),
    db: Session = Depends(get_db)
):
    return {
        "periodo": f"{mes:02d}/{ano}",
        "demonstracao": {
            "receita_bruta": 195000.00,
            "deducoes": 19500.00,
            "receita_liquida": 175500.00,
            "cmv": 70200.00,
            "lucro_bruto": 105300.00,
            "despesas_operacionais": {
                "vendas": 21060.00,
                "administrativas": 31590.00,
                "financeiras": 5265.00
            },
            "lucro_operacional": 47385.00,
            "outras_receitas": 2000.00,
            "outras_despesas": 1500.00,
            "lucro_antes_ir": 47885.00,
            "ir_csll": 11971.25,
            "lucro_liquido": 35913.75,
            "margem_liquida": 18.42
        }
    }

# Centro de Custo
@router.post("/centros-custo")
async def criar_centro_custo(centro: CentroCusto, db: Session = Depends(get_db)):
    return {
        "id": 1,
        **centro.dict(),
        "created_at": datetime.now()
    }

@router.get("/centros-custo")
async def listar_centros_custo(
    tipo: Optional[str] = None,
    ativo: bool = True,
    db: Session = Depends(get_db)
):
    return [
        {
            "id": 1,
            "codigo": "CC001",
            "nome": "Produção",
            "tipo": "PRODUCAO",
            "responsavel": "João Silva",
            "orcamento_mensal": 50000.00,
            "gasto_atual": 35000.00,
            "percentual_usado": 70,
            "ativo": True
        },
        {
            "id": 2,
            "codigo": "CC002",
            "nome": "Administrativo",
            "tipo": "ADMINISTRATIVO",
            "responsavel": "Maria Santos",
            "orcamento_mensal": 30000.00,
            "gasto_atual": 28500.00,
            "percentual_usado": 95,
            "ativo": True
        }
    ]

@router.get("/centros-custo/{centro_id}/analise")
async def analisar_centro_custo(
    centro_id: int,
    mes: int = Query(...),
    ano: int = Query(...),
    db: Session = Depends(get_db)
):
    return {
        "centro_id": centro_id,
        "periodo": f"{mes:02d}/{ano}",
        "orcamento": 50000.00,
        "realizado": 35000.00,
        "variacao": -15000.00,
        "percentual": 70,
        "despesas_por_categoria": [
            {"categoria": "Matéria Prima", "valor": 20000.00, "percentual": 57.14},
            {"categoria": "Mão de Obra", "valor": 10000.00, "percentual": 28.57},
            {"categoria": "Energia", "valor": 5000.00, "percentual": 14.29}
        ],
        "evolucao_mensal": [
            {"mes": 1, "orcado": 50000.00, "realizado": 45000.00},
            {"mes": 2, "orcado": 50000.00, "realizado": 48000.00}
        ]
    }

# Produção
@router.post("/producao/ordens")
async def criar_ordem_producao(ordem: OrdemProducao, db: Session = Depends(get_db)):
    return {
        "id": 1,
        **ordem.dict(),
        "created_at": datetime.now()
    }

@router.get("/producao/ordens")
async def listar_ordens_producao(
    status: Optional[str] = None,
    data_inicio: Optional[date] = None,
    data_fim: Optional[date] = None,
    db: Session = Depends(get_db)
):
    return [
        {
            "id": 1,
            "numero": "OP-2024-001",
            "produto": "Produto A",
            "quantidade": 1000,
            "quantidade_produzida": 750,
            "percentual_concluido": 75,
            "data_inicio": "2024-01-10T08:00:00",
            "data_prevista": "2024-01-20T18:00:00",
            "status": "EM_PRODUCAO",
            "custo_estimado": 15000.00,
            "custo_real": 11500.00
        }
    ]

@router.put("/producao/ordens/{ordem_id}/status")
async def atualizar_status_ordem(
    ordem_id: int,
    status: str = Body(...),
    observacao: Optional[str] = Body(None),
    db: Session = Depends(get_db)
):
    return {
        "ordem_id": ordem_id,
        "status": status,
        "observacao": observacao,
        "updated_at": datetime.now()
    }

@router.get("/producao/mrp")
async def calcular_mrp(
    produto_id: Optional[int] = None,
    horizonte_dias: int = 30,
    db: Session = Depends(get_db)
):
    return {
        "horizonte": f"{horizonte_dias} dias",
        "necessidades": [
            {
                "produto": "Matéria Prima A",
                "quantidade_necessaria": 5000,
                "estoque_atual": 2000,
                "comprar": 3000,
                "data_necessidade": "2024-01-25",
                "fornecedor_sugerido": "Fornecedor X",
                "custo_estimado": 15000.00
            },
            {
                "produto": "Componente B",
                "quantidade_necessaria": 1000,
                "estoque_atual": 1200,
                "comprar": 0,
                "observacao": "Estoque suficiente"
            }
        ],
        "ordens_sugeridas": [
            {
                "tipo": "COMPRA",
                "produto": "Matéria Prima A",
                "quantidade": 3000,
                "data_sugerida": "2024-01-20"
            }
        ]
    }

# Recursos Humanos
@router.get("/rh/funcionarios")
async def listar_funcionarios(
    departamento: Optional[str] = None,
    ativo: bool = True,
    db: Session = Depends(get_db)
):
    return [
        {
            "id": 1,
            "matricula": "0001",
            "nome": "João Silva",
            "cargo": "Gerente de Produção",
            "departamento": "Produção",
            "admissao": "2020-03-15",
            "salario_base": 8500.00,
            "status": "ATIVO"
        },
        {
            "id": 2,
            "matricula": "0002",
            "nome": "Maria Santos",
            "cargo": "Analista Contábil",
            "departamento": "Financeiro",
            "admissao": "2021-06-01",
            "salario_base": 5500.00,
            "status": "ATIVO"
        }
    ]

@router.get("/rh/folha-pagamento")
async def gerar_folha_pagamento(
    mes: int = Query(...),
    ano: int = Query(...),
    db: Session = Depends(get_db)
):
    return {
        "periodo": f"{mes:02d}/{ano}",
        "funcionarios": 45,
        "resumo": {
            "salarios": 285000.00,
            "horas_extras": 12500.00,
            "beneficios": 35000.00,
            "descontos": 42500.00,
            "liquido": 290000.00,
            "encargos": 95000.00,
            "total_custo": 427500.00
        },
        "detalhamento": [
            {
                "funcionario": "João Silva",
                "salario_base": 8500.00,
                "horas_extras": 850.00,
                "beneficios": 1200.00,
                "inss": 935.00,
                "irrf": 1157.50,
                "liquido": 8457.50
            }
        ]
    }

@router.get("/rh/ponto")
async def obter_registro_ponto(
    funcionario_id: Optional[int] = None,
    data_inicio: date = Query(...),
    data_fim: date = Query(...),
    db: Session = Depends(get_db)
):
    return {
        "periodo": f"{data_inicio} a {data_fim}",
        "registros": [
            {
                "funcionario": "João Silva",
                "data": "2024-01-15",
                "entrada": "08:00",
                "saida_almoco": "12:00",
                "retorno_almoco": "13:00",
                "saida": "18:00",
                "horas_trabalhadas": "8:00",
                "horas_extras": "0:00"
            }
        ],
        "resumo": {
            "dias_trabalhados": 20,
            "horas_normais": 160,
            "horas_extras": 12,
            "faltas": 0,
            "atrasos": 2
        }
    }

# Dashboards e KPIs
@router.get("/dashboard/geral")
async def dashboard_geral(db: Session = Depends(get_db)):
    return {
        "faturamento": {
            "mes_atual": 195000.00,
            "mes_anterior": 180000.00,
            "variacao": 8.33,
            "meta": 200000.00,
            "percentual_meta": 97.5
        },
        "custos": {
            "mes_atual": 145000.00,
            "mes_anterior": 138000.00,
            "variacao": 5.07
        },
        "lucro": {
            "mes_atual": 50000.00,
            "mes_anterior": 42000.00,
            "variacao": 19.05,
            "margem": 25.64
        },
        "producao": {
            "ordens_abertas": 12,
            "ordens_concluidas": 45,
            "eficiencia": 92.5,
            "ociosidade": 7.5
        },
        "estoque": {
            "valor_total": 125000.00,
            "giro": 2.5,
            "itens_criticos": 12
        },
        "financeiro": {
            "contas_receber": 75000.00,
            "contas_pagar": 45000.00,
            "fluxo_caixa": 30000.00
        },
        "alertas": [
            {"tipo": "CRITICO", "mensagem": "5 notas fiscais pendentes de aprovação"},
            {"tipo": "AVISO", "mensagem": "Backup do ERP agendado para hoje 22h"},
            {"tipo": "INFO", "mensagem": "Nova versão do módulo fiscal disponível"}
        ]
    }

@router.get("/dashboard/kpis")
async def obter_kpis(db: Session = Depends(get_db)):
    return {
        "operacionais": [
            {"indicador": "OEE", "valor": 85, "meta": 90, "unidade": "%"},
            {"indicador": "Lead Time", "valor": 3.5, "meta": 3, "unidade": "dias"},
            {"indicador": "OTIF", "valor": 92, "meta": 95, "unidade": "%"}
        ],
        "financeiros": [
            {"indicador": "ROI", "valor": 22.5, "meta": 20, "unidade": "%"},
            {"indicador": "EBITDA", "valor": 65000, "meta": 60000, "unidade": "R$"},
            {"indicador": "Margem EBITDA", "valor": 33.3, "meta": 30, "unidade": "%"}
        ],
        "qualidade": [
            {"indicador": "Defeitos PPM", "valor": 150, "meta": 100, "unidade": "ppm"},
            {"indicador": "First Pass Yield", "valor": 98.5, "meta": 99, "unidade": "%"},
            {"indicador": "Reclamações", "valor": 3, "meta": 5, "unidade": "un"}
        ]
    }

# Auditoria e Compliance
@router.get("/auditoria/logs")
async def obter_logs_auditoria(
    modulo: Optional[str] = None,
    usuario: Optional[str] = None,
    data_inicio: Optional[date] = None,
    data_fim: Optional[date] = None,
    db: Session = Depends(get_db)
):
    return [
        {
            "id": 1,
            "timestamp": "2024-01-15T10:30:00",
            "usuario": "admin",
            "modulo": "Fiscal",
            "acao": "EMISSAO_NFE",
            "detalhes": "Nota Fiscal 001234 emitida",
            "ip": "192.168.1.100",
            "sucesso": True
        },
        {
            "id": 2,
            "timestamp": "2024-01-15T11:45:00",
            "usuario": "contador",
            "modulo": "Contábil",
            "acao": "LANCAMENTO",
            "detalhes": "Lançamento contábil realizado",
            "ip": "192.168.1.101",
            "sucesso": True
        }
    ]

@router.get("/compliance/verificar")
async def verificar_compliance(db: Session = Depends(get_db)):
    return {
        "data_verificacao": datetime.now(),
        "conformidades": [
            {
                "area": "Fiscal",
                "item": "SPED Fiscal",
                "status": "CONFORME",
                "ultima_entrega": "2024-01-10"
            },
            {
                "area": "Trabalhista",
                "item": "eSocial",
                "status": "CONFORME",
                "ultima_entrega": "2024-01-15"
            },
            {
                "area": "Contábil",
                "item": "ECD",
                "status": "PENDENTE",
                "prazo": "2024-05-31"
            }
        ],
        "pendencias": [
            {
                "tipo": "OBRIGACAO",
                "descricao": "Entrega ECD 2023",
                "prazo": "2024-05-31",
                "dias_restantes": 136
            }
        ],
        "score_compliance": 92
    }