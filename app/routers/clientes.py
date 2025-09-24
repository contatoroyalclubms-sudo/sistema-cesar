from fastapi import APIRouter, HTTPException, Depends, Query, Body, File, UploadFile
from sqlalchemy.orm import Session
from typing import List, Optional, Dict
from datetime import datetime, date, timedelta
from pydantic import BaseModel, EmailStr
from app.database import get_db

router = APIRouter(prefix="/api/clientes", tags=["Clientes"])

# Schemas
class CategoriaCliente(BaseModel):
    id: Optional[int] = None
    nome: str
    descricao: Optional[str]
    cor: Optional[str]
    icone: Optional[str]
    criterios: Dict  # {"idade_min": 18, "compras_min": 5, "valor_min": 1000}
    beneficios: Optional[List[str]]
    desconto_padrao: Optional[float]
    ativo: bool = True

class Cliente(BaseModel):
    id: Optional[int] = None
    codigo: Optional[str]
    nome: str
    documento: str  # CPF ou CNPJ
    tipo_pessoa: str  # FISICA, JURIDICA
    email: Optional[EmailStr]
    telefone: Optional[str]
    celular: Optional[str]
    data_nascimento: Optional[date]
    genero: Optional[str]
    endereco: Optional[Dict]
    categoria_id: Optional[int]
    tags: Optional[List[str]]
    observacoes: Optional[str]
    ativo: bool = True
    aceita_marketing: bool = True

class HistoricoCliente(BaseModel):
    cliente_id: int
    tipo: str  # COMPRA, ATENDIMENTO, RECLAMACAO, ELOGIO, TROCA_CATEGORIA
    descricao: str
    valor: Optional[float]
    data: datetime
    usuario_responsavel: Optional[str]

class PesquisaSatisfacao(BaseModel):
    id: Optional[int] = None
    titulo: str
    descricao: Optional[str]
    tipo: str  # NPS, CSAT, CES, CUSTOMIZADA
    perguntas: List[Dict]
    publico_alvo: Optional[str]  # TODOS, CATEGORIA, ESPECIFICO
    categoria_ids: Optional[List[int]]
    cliente_ids: Optional[List[int]]
    data_inicio: datetime
    data_fim: Optional[datetime]
    ativa: bool = True

class RespostaPesquisa(BaseModel):
    id: Optional[int] = None
    pesquisa_id: int
    cliente_id: int
    respostas: Dict
    nota_geral: Optional[int]
    comentarios: Optional[str]
    data_resposta: datetime
    canal: str  # EMAIL, SMS, WHATSAPP, APP, SITE

class SegmentoCliente(BaseModel):
    id: Optional[int] = None
    nome: str
    descricao: Optional[str]
    criterios: Dict
    clientes_count: Optional[int]
    automatico: bool = True

class CampanhaCliente(BaseModel):
    id: Optional[int] = None
    nome: str
    tipo: str  # EMAIL, SMS, WHATSAPP, PUSH
    segmento_id: Optional[int]
    categoria_id: Optional[int]
    mensagem: str
    data_envio: datetime
    status: str  # RASCUNHO, AGENDADA, ENVIANDO, CONCLUIDA

# Categorias de Clientes
@router.post("/categorias")
async def criar_categoria_cliente(categoria: CategoriaCliente, db: Session = Depends(get_db)):
    return {
        "id": 1,
        **categoria.dict(),
        "created_at": datetime.now()
    }

@router.get("/categorias")
async def listar_categorias_clientes(
    ativo: bool = True,
    db: Session = Depends(get_db)
):
    return [
        {
            "id": 1,
            "nome": "VIP Gold",
            "descricao": "Clientes mais valiosos",
            "cor": "#FFD700",
            "icone": "⭐",
            "criterios": {
                "valor_min_anual": 50000,
                "compras_min": 20,
                "tempo_cliente_meses": 12
            },
            "beneficios": [
                "20% desconto em todos produtos",
                "Frete grátis",
                "Atendimento prioritário",
                "Acesso antecipado a lançamentos"
            ],
            "desconto_padrao": 20,
            "clientes_count": 150,
            "ativo": True
        },
        {
            "id": 2,
            "nome": "VIP Silver",
            "descricao": "Clientes frequentes",
            "cor": "#C0C0C0",
            "icone": "⭐",
            "criterios": {
                "valor_min_anual": 20000,
                "compras_min": 10,
                "tempo_cliente_meses": 6
            },
            "beneficios": [
                "10% desconto em todos produtos",
                "Frete reduzido",
                "Ofertas exclusivas"
            ],
            "desconto_padrao": 10,
            "clientes_count": 450,
            "ativo": True
        },
        {
            "id": 3,
            "nome": "Regular",
            "descricao": "Clientes padrão",
            "cor": "#808080",
            "criterios": {},
            "beneficios": ["Programa de pontos", "Ofertas mensais"],
            "clientes_count": 2500,
            "ativo": True
        }
    ]

@router.put("/categorias/{categoria_id}")
async def atualizar_categoria_cliente(
    categoria_id: int,
    categoria: CategoriaCliente,
    db: Session = Depends(get_db)
):
    return {"id": categoria_id, **categoria.dict(), "updated_at": datetime.now()}

@router.post("/categorias/{categoria_id}/reclassificar")
async def reclassificar_clientes(categoria_id: int, db: Session = Depends(get_db)):
    return {
        "categoria_id": categoria_id,
        "clientes_analisados": 3100,
        "movidos_para_categoria": 45,
        "removidos_da_categoria": 12,
        "mantidos": 138,
        "processado_em": datetime.now()
    }

# Listagem de Clientes
@router.get("")
async def listar_clientes(
    categoria_id: Optional[int] = None,
    busca: Optional[str] = None,
    tipo_pessoa: Optional[str] = None,
    ativo: bool = True,
    ordenar_por: str = "nome",
    limite: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    return {
        "total": 3100,
        "clientes": [
            {
                "id": 1,
                "codigo": "CLI001",
                "nome": "João Silva Santos",
                "documento": "123.456.789-00",
                "tipo_pessoa": "FISICA",
                "email": "joao.silva@email.com",
                "telefone": "(11) 98765-4321",
                "categoria": "VIP Gold",
                "total_compras": 125,
                "valor_total": 85000.00,
                "ultima_compra": "2024-01-14",
                "score": 950,
                "ativo": True
            },
            {
                "id": 2,
                "codigo": "CLI002",
                "nome": "Empresa ABC LTDA",
                "documento": "12.345.678/0001-90",
                "tipo_pessoa": "JURIDICA",
                "email": "contato@empresaabc.com",
                "telefone": "(11) 3456-7890",
                "categoria": "VIP Silver",
                "total_compras": 89,
                "valor_total": 45000.00,
                "ultima_compra": "2024-01-10",
                "score": 820,
                "ativo": True
            }
        ]
    }

@router.get("/{cliente_id}")
async def obter_cliente_detalhado(cliente_id: int, db: Session = Depends(get_db)):
    return {
        "id": cliente_id,
        "codigo": "CLI001",
        "nome": "João Silva Santos",
        "documento": "123.456.789-00",
        "tipo_pessoa": "FISICA",
        "email": "joao.silva@email.com",
        "telefone": "(11) 3456-7890",
        "celular": "(11) 98765-4321",
        "data_nascimento": "1985-05-15",
        "idade": 38,
        "genero": "Masculino",
        "endereco": {
            "cep": "01234-567",
            "logradouro": "Rua das Flores",
            "numero": "123",
            "complemento": "Apto 45",
            "bairro": "Jardim América",
            "cidade": "São Paulo",
            "estado": "SP"
        },
        "categoria": {
            "id": 1,
            "nome": "VIP Gold",
            "beneficios": ["20% desconto", "Frete grátis"]
        },
        "tags": ["Cliente fiel", "Comprador frequente", "Alto ticket"],
        "estatisticas": {
            "primeira_compra": "2020-03-15",
            "ultima_compra": "2024-01-14",
            "total_compras": 125,
            "valor_total": 85000.00,
            "ticket_medio": 680.00,
            "frequencia_media_dias": 12,
            "produtos_favoritos": [
                {"nome": "Produto A", "quantidade": 45},
                {"nome": "Produto B", "quantidade": 32}
            ]
        },
        "score_credito": 950,
        "risco": "BAIXO",
        "aceita_marketing": True,
        "canais_preferidos": ["Email", "WhatsApp"],
        "observacoes": "Cliente preferencial, sempre paga em dia",
        "ativo": True
    }

@router.post("")
async def criar_cliente(cliente: Cliente, db: Session = Depends(get_db)):
    return {
        "id": 1,
        "codigo": "CLI003",
        **cliente.dict(),
        "created_at": datetime.now()
    }

@router.put("/{cliente_id}")
async def atualizar_cliente(
    cliente_id: int,
    cliente: Cliente,
    db: Session = Depends(get_db)
):
    return {"id": cliente_id, **cliente.dict(), "updated_at": datetime.now()}

@router.post("/{cliente_id}/historico")
async def adicionar_historico_cliente(
    cliente_id: int,
    historico: HistoricoCliente,
    db: Session = Depends(get_db)
):
    return {
        "id": 1,
        "cliente_id": cliente_id,
        **historico.dict(),
        "created_at": datetime.now()
    }

@router.get("/{cliente_id}/historico")
async def obter_historico_cliente(
    cliente_id: int,
    tipo: Optional[str] = None,
    db: Session = Depends(get_db)
):
    historico = [
        {
            "id": 1,
            "tipo": "COMPRA",
            "descricao": "Compra realizada - Pedido #12345",
            "valor": 1500.00,
            "data": "2024-01-14T15:30:00",
            "usuario_responsavel": "Sistema"
        },
        {
            "id": 2,
            "tipo": "ATENDIMENTO",
            "descricao": "Atendimento via WhatsApp - Dúvida sobre produto",
            "data": "2024-01-10T10:15:00",
            "usuario_responsavel": "Maria Santos"
        },
        {
            "id": 3,
            "tipo": "TROCA_CATEGORIA",
            "descricao": "Promovido de VIP Silver para VIP Gold",
            "data": "2024-01-01T00:00:00",
            "usuario_responsavel": "Sistema"
        }
    ]

    if tipo:
        historico = [h for h in historico if h["tipo"] == tipo]

    return historico

# Pesquisa de Satisfação
@router.post("/pesquisas")
async def criar_pesquisa_satisfacao(pesquisa: PesquisaSatisfacao, db: Session = Depends(get_db)):
    return {
        "id": 1,
        **pesquisa.dict(),
        "url_resposta": "https://meep.com.br/pesquisa/1",
        "created_at": datetime.now()
    }

@router.get("/pesquisas")
async def listar_pesquisas(
    ativa: Optional[bool] = None,
    tipo: Optional[str] = None,
    db: Session = Depends(get_db)
):
    return [
        {
            "id": 1,
            "titulo": "Pesquisa NPS Mensal",
            "tipo": "NPS",
            "perguntas_count": 3,
            "publico_alvo": "TODOS",
            "data_inicio": "2024-01-01",
            "data_fim": "2024-01-31",
            "total_enviadas": 1500,
            "total_respondidas": 450,
            "taxa_resposta": 30,
            "nota_media": 8.5,
            "nps_score": 45,
            "ativa": True
        },
        {
            "id": 2,
            "titulo": "Satisfação Pós-Compra",
            "tipo": "CSAT",
            "perguntas_count": 5,
            "publico_alvo": "CATEGORIA",
            "categorias": ["VIP Gold", "VIP Silver"],
            "data_inicio": "2024-01-10",
            "total_enviadas": 200,
            "total_respondidas": 120,
            "taxa_resposta": 60,
            "nota_media": 4.5,
            "ativa": True
        }
    ]

@router.get("/pesquisas/{pesquisa_id}")
async def obter_pesquisa_detalhada(pesquisa_id: int, db: Session = Depends(get_db)):
    return {
        "id": pesquisa_id,
        "titulo": "Pesquisa NPS Mensal",
        "descricao": "Pesquisa mensal para medir satisfação dos clientes",
        "tipo": "NPS",
        "perguntas": [
            {
                "id": 1,
                "pergunta": "De 0 a 10, o quanto você recomendaria nossa empresa?",
                "tipo": "ESCALA",
                "obrigatoria": True,
                "opcoes": list(range(11))
            },
            {
                "id": 2,
                "pergunta": "O que mais você gosta em nossos serviços?",
                "tipo": "TEXTO",
                "obrigatoria": False
            },
            {
                "id": 3,
                "pergunta": "Como podemos melhorar?",
                "tipo": "TEXTO",
                "obrigatoria": False
            }
        ],
        "estatisticas": {
            "total_enviadas": 1500,
            "total_respondidas": 450,
            "taxa_resposta": 30,
            "tempo_medio_resposta": "3 minutos",
            "canais": {
                "email": 250,
                "whatsapp": 150,
                "sms": 50
            },
            "nps": {
                "promotores": 225,
                "neutros": 135,
                "detratores": 90,
                "score": 45
            }
        },
        "ativa": True
    }

@router.post("/pesquisas/{pesquisa_id}/enviar")
async def enviar_pesquisa(
    pesquisa_id: int,
    canal: str = Body(...),  # EMAIL, SMS, WHATSAPP
    cliente_ids: Optional[List[int]] = Body(None),
    db: Session = Depends(get_db)
):
    return {
        "pesquisa_id": pesquisa_id,
        "envios": {
            "total": 150,
            "sucesso": 148,
            "falha": 2,
            "canal": canal
        },
        "previsao_resposta": "30% em 48 horas",
        "enviado_em": datetime.now()
    }

@router.post("/pesquisas/{pesquisa_id}/respostas")
async def registrar_resposta_pesquisa(
    pesquisa_id: int,
    resposta: RespostaPesquisa,
    db: Session = Depends(get_db)
):
    return {
        "id": 1,
        "pesquisa_id": pesquisa_id,
        **resposta.dict(),
        "classificacao_nps": "Promotor" if resposta.nota_geral >= 9 else "Neutro",
        "created_at": datetime.now()
    }

@router.get("/pesquisas/{pesquisa_id}/respostas")
async def listar_respostas_pesquisa(
    pesquisa_id: int,
    cliente_id: Optional[int] = None,
    nota_min: Optional[int] = None,
    db: Session = Depends(get_db)
):
    return [
        {
            "id": 1,
            "cliente": "João Silva",
            "nota_geral": 9,
            "classificacao": "Promotor",
            "respostas": {
                "recomendacao": 9,
                "o_que_gosta": "Atendimento excelente",
                "melhorias": "Mais opções de pagamento"
            },
            "data_resposta": "2024-01-15T14:30:00",
            "canal": "EMAIL"
        }
    ]

@router.get("/pesquisas/{pesquisa_id}/relatorio")
async def relatorio_pesquisa(pesquisa_id: int, db: Session = Depends(get_db)):
    return {
        "pesquisa_id": pesquisa_id,
        "titulo": "Pesquisa NPS Mensal",
        "periodo": "01/01/2024 a 31/01/2024",
        "metricas_gerais": {
            "total_enviadas": 1500,
            "total_respondidas": 450,
            "taxa_resposta": 30,
            "nps_score": 45,
            "csat_score": 4.5,
            "tempo_medio_resposta": "3 minutos"
        },
        "distribuicao_notas": {
            "0-6": 90,
            "7-8": 135,
            "9-10": 225
        },
        "principais_elogios": [
            {"tema": "Atendimento", "mencoes": 180},
            {"tema": "Qualidade", "mencoes": 150},
            {"tema": "Rapidez", "mencoes": 120}
        ],
        "principais_criticas": [
            {"tema": "Preço", "mencoes": 45},
            {"tema": "Prazo entrega", "mencoes": 30},
            {"tema": "Variedade", "mencoes": 25}
        ],
        "evolucao_temporal": [
            {"semana": 1, "nps": 42},
            {"semana": 2, "nps": 45},
            {"semana": 3, "nps": 48},
            {"semana": 4, "nps": 45}
        ],
        "segmentacao": {
            "por_categoria": [
                {"categoria": "VIP Gold", "nps": 65, "respondentes": 150},
                {"categoria": "VIP Silver", "nps": 45, "respondentes": 200},
                {"categoria": "Regular", "nps": 35, "respondentes": 100}
            ],
            "por_canal": [
                {"canal": "Email", "nps": 48, "respondentes": 250},
                {"canal": "WhatsApp", "nps": 42, "respondentes": 150},
                {"canal": "SMS", "nps": 40, "respondentes": 50}
            ]
        }
    }

# Segmentação
@router.post("/segmentos")
async def criar_segmento(segmento: SegmentoCliente, db: Session = Depends(get_db)):
    return {
        "id": 1,
        **segmento.dict(),
        "clientes_count": 450,
        "created_at": datetime.now()
    }

@router.get("/segmentos")
async def listar_segmentos(db: Session = Depends(get_db)):
    return [
        {
            "id": 1,
            "nome": "Compradores Frequentes",
            "descricao": "Clientes que compram pelo menos 1x por mês",
            "criterios": {"compras_ultimos_30_dias": {"min": 1}},
            "clientes_count": 890,
            "automatico": True
        },
        {
            "id": 2,
            "nome": "Alto Valor",
            "descricao": "Clientes com ticket médio acima de R$ 500",
            "criterios": {"ticket_medio": {"min": 500}},
            "clientes_count": 345,
            "automatico": True
        },
        {
            "id": 3,
            "nome": "Inativos",
            "descricao": "Sem compras há mais de 90 dias",
            "criterios": {"dias_sem_compra": {"min": 90}},
            "clientes_count": 567,
            "automatico": True
        }
    ]

@router.post("/segmentos/{segmento_id}/atualizar")
async def atualizar_segmento_clientes(segmento_id: int, db: Session = Depends(get_db)):
    return {
        "segmento_id": segmento_id,
        "clientes_analisados": 3100,
        "adicionados": 45,
        "removidos": 23,
        "total_segmento": 912,
        "atualizado_em": datetime.now()
    }

# Campanhas
@router.post("/campanhas")
async def criar_campanha(campanha: CampanhaCliente, db: Session = Depends(get_db)):
    return {
        "id": 1,
        **campanha.dict(),
        "publico_estimado": 450,
        "created_at": datetime.now()
    }

@router.get("/campanhas")
async def listar_campanhas(
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    return [
        {
            "id": 1,
            "nome": "Black Friday VIPs",
            "tipo": "EMAIL",
            "segmento": "VIP Gold",
            "publico": 150,
            "data_envio": "2024-11-20T10:00:00",
            "status": "AGENDADA",
            "metricas": {
                "enviados": 0,
                "abertos": 0,
                "cliques": 0,
                "conversoes": 0
            }
        },
        {
            "id": 2,
            "nome": "Reativação Inativos",
            "tipo": "WHATSAPP",
            "segmento": "Inativos",
            "publico": 567,
            "data_envio": "2024-01-10T14:00:00",
            "status": "CONCLUIDA",
            "metricas": {
                "enviados": 567,
                "abertos": 234,
                "cliques": 89,
                "conversoes": 23
            }
        }
    ]

# Análises e Relatórios
@router.get("/analises/rfm")
async def analise_rfm(db: Session = Depends(get_db)):
    return {
        "data_analise": datetime.now(),
        "total_clientes": 3100,
        "segmentos": [
            {
                "segmento": "Champions",
                "descricao": "Compram com frequência e gastam muito",
                "clientes": 150,
                "percentual": 4.8,
                "valor_medio": 2500.00,
                "acoes_recomendadas": ["Programa VIP", "Ofertas exclusivas"]
            },
            {
                "segmento": "Loyal Customers",
                "descricao": "Clientes fiéis",
                "clientes": 450,
                "percentual": 14.5,
                "valor_medio": 1200.00,
                "acoes_recomendadas": ["Programa de fidelidade", "Upsell"]
            },
            {
                "segmento": "At Risk",
                "descricao": "Eram bons clientes mas não compram há tempo",
                "clientes": 320,
                "percentual": 10.3,
                "valor_medio": 800.00,
                "acoes_recomendadas": ["Campanhas de reativação", "Ofertas especiais"]
            },
            {
                "segmento": "Lost",
                "descricao": "Não compram há muito tempo",
                "clientes": 567,
                "percentual": 18.3,
                "valor_medio": 300.00,
                "acoes_recomendadas": ["Pesquisa de satisfação", "Descontos agressivos"]
            }
        ]
    }

@router.get("/analises/ltv")
async def analise_ltv(db: Session = Depends(get_db)):
    return {
        "ltv_medio_geral": 3500.00,
        "por_categoria": [
            {"categoria": "VIP Gold", "ltv_medio": 12000.00, "clientes": 150},
            {"categoria": "VIP Silver", "ltv_medio": 5500.00, "clientes": 450},
            {"categoria": "Regular", "ltv_medio": 1800.00, "clientes": 2500}
        ],
        "por_cohort": [
            {"mes_aquisicao": "2023-01", "ltv_12_meses": 2800.00, "retencao": 65},
            {"mes_aquisicao": "2023-06", "ltv_6_meses": 1500.00, "retencao": 55}
        ],
        "previsao_proximos_12_meses": 8500000.00
    }

@router.get("/analises/churn")
async def analise_churn(db: Session = Depends(get_db)):
    return {
        "taxa_churn_mensal": 5.2,
        "taxa_churn_anual": 45.8,
        "clientes_risco_churn": 320,
        "principais_motivos": [
            {"motivo": "Preço", "percentual": 35},
            {"motivo": "Atendimento", "percentual": 25},
            {"motivo": "Concorrência", "percentual": 20},
            {"motivo": "Qualidade", "percentual": 20}
        ],
        "acoes_preventivas": [
            "Programa de retenção para clientes de risco",
            "Melhoria no atendimento",
            "Revisão de preços para clientes fiéis"
        ]
    }

# Importação/Exportação
@router.post("/importar")
async def importar_clientes(
    arquivo: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    return {
        "arquivo": arquivo.filename,
        "total_linhas": 500,
        "importados": 485,
        "erros": 15,
        "detalhes_erros": [
            {"linha": 45, "erro": "CPF inválido"},
            {"linha": 123, "erro": "Email duplicado"}
        ],
        "processado_em": datetime.now()
    }

@router.get("/exportar")
async def exportar_clientes(
    formato: str = Query(...),  # CSV, EXCEL, JSON
    categoria_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    return {
        "url_download": f"https://meep.com.br/exports/clientes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{formato}",
        "total_registros": 3100,
        "tamanho_arquivo": "2.5 MB",
        "validade_link": "24 horas"
    }