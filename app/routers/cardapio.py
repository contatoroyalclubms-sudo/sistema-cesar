from fastapi import APIRouter, HTTPException, Depends, Query, File, UploadFile
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, date, time
from pydantic import BaseModel
from app.database import get_db

router = APIRouter(prefix="/api/cardapio", tags=["Cardápio"])

# Schemas
class CategoriaCardapio(BaseModel):
    id: Optional[int] = None
    nome: str
    descricao: Optional[str]
    ordem: int = 0
    icone: Optional[str]
    cor: Optional[str]
    ativo: bool = True
    imagem_url: Optional[str]

class ItemCardapio(BaseModel):
    id: Optional[int] = None
    codigo: str
    nome: str
    descricao: Optional[str]
    categoria_id: int
    preco: float
    preco_promocional: Optional[float]
    custo: Optional[float]
    tempo_preparo: Optional[int]  # em minutos
    calorias: Optional[int]
    serve_pessoas: Optional[int]
    ingredientes: Optional[List[str]]
    alergenos: Optional[List[str]]
    tags: Optional[List[str]]
    imagem_url: Optional[str]
    disponivel: bool = True
    destaque: bool = False
    ordem: int = 0

class ModificadorItem(BaseModel):
    id: Optional[int] = None
    nome: str
    tipo: str  # ADICIONAL, REMOCAO, SUBSTITUICAO
    preco: float
    disponivel: bool = True
    obrigatorio: bool = False
    minimo: int = 0
    maximo: int = 1

class GrupoModificadores(BaseModel):
    id: Optional[int] = None
    nome: str
    descricao: Optional[str]
    obrigatorio: bool = False
    minimo: int = 0
    maximo: int = 1
    modificadores: List[ModificadorItem]

class ComboCardapio(BaseModel):
    id: Optional[int] = None
    nome: str
    descricao: Optional[str]
    preco: float
    preco_original: float
    economia: float
    itens: List[int]  # IDs dos itens do cardápio
    imagem_url: Optional[str]
    disponivel: bool = True
    validade_inicio: Optional[datetime]
    validade_fim: Optional[datetime]

class MenuDiario(BaseModel):
    id: Optional[int] = None
    data: date
    tipo: str  # ALMOCO, JANTAR, ESPECIAL
    nome: str
    descricao: Optional[str]
    itens: List[int]
    preco_fixo: Optional[float]
    ativo: bool = True

class HorarioCardapio(BaseModel):
    id: Optional[int] = None
    dia_semana: int  # 0=domingo, 6=sábado
    hora_inicio: time
    hora_fim: time
    cardapio_especial_id: Optional[int]
    ativo: bool = True

# Categorias
@router.post("/categorias")
async def criar_categoria(categoria: CategoriaCardapio, db: Session = Depends(get_db)):
    return {
        "id": 1,
        **categoria.dict(),
        "created_at": datetime.now()
    }

@router.get("/categorias")
async def listar_categorias(
    ativo: bool = True,
    db: Session = Depends(get_db)
):
    return [
        {
            "id": 1,
            "nome": "Entradas",
            "descricao": "Pratos para começar",
            "ordem": 1,
            "icone": "🥗",
            "cor": "#4CAF50",
            "ativo": True,
            "itens_count": 15
        },
        {
            "id": 2,
            "nome": "Pratos Principais",
            "descricao": "Pratos principais",
            "ordem": 2,
            "icone": "🍽️",
            "cor": "#FF5722",
            "ativo": True,
            "itens_count": 25
        },
        {
            "id": 3,
            "nome": "Bebidas",
            "descricao": "Bebidas diversas",
            "ordem": 3,
            "icone": "🥤",
            "cor": "#2196F3",
            "ativo": True,
            "itens_count": 30
        },
        {
            "id": 4,
            "nome": "Sobremesas",
            "descricao": "Para finalizar",
            "ordem": 4,
            "icone": "🍰",
            "cor": "#E91E63",
            "ativo": True,
            "itens_count": 10
        }
    ]

@router.put("/categorias/{categoria_id}")
async def atualizar_categoria(
    categoria_id: int,
    categoria: CategoriaCardapio,
    db: Session = Depends(get_db)
):
    return {"id": categoria_id, **categoria.dict(), "updated_at": datetime.now()}

@router.delete("/categorias/{categoria_id}")
async def deletar_categoria(categoria_id: int, db: Session = Depends(get_db)):
    return {"message": "Categoria deletada com sucesso"}

# Itens do Cardápio
@router.post("/itens")
async def criar_item(item: ItemCardapio, db: Session = Depends(get_db)):
    return {
        "id": 1,
        **item.dict(),
        "margem_lucro": ((item.preco - (item.custo or 0)) / item.preco) * 100 if item.custo else None,
        "created_at": datetime.now()
    }

@router.get("/itens")
async def listar_itens(
    categoria_id: Optional[int] = None,
    disponivel: Optional[bool] = True,
    destaque: Optional[bool] = None,
    busca: Optional[str] = None,
    ordem: str = "nome",
    db: Session = Depends(get_db)
):
    itens = [
        {
            "id": 1,
            "codigo": "ENT001",
            "nome": "Bruschetta Italiana",
            "descricao": "Pão italiano com tomate, manjericão e azeite",
            "categoria_id": 1,
            "categoria": "Entradas",
            "preco": 28.00,
            "preco_promocional": None,
            "tempo_preparo": 15,
            "calorias": 280,
            "ingredientes": ["Pão", "Tomate", "Manjericão", "Azeite", "Alho"],
            "disponivel": True,
            "destaque": True,
            "avaliacao": 4.8,
            "pedidos_hoje": 12
        },
        {
            "id": 2,
            "codigo": "PRT001",
            "nome": "Filé à Parmegiana",
            "descricao": "Filé empanado com molho de tomate e queijo gratinado",
            "categoria_id": 2,
            "categoria": "Pratos Principais",
            "preco": 65.00,
            "preco_promocional": 58.00,
            "tempo_preparo": 35,
            "calorias": 850,
            "serve_pessoas": 1,
            "ingredientes": ["Filé mignon", "Molho de tomate", "Queijo", "Farinha"],
            "disponivel": True,
            "destaque": False,
            "avaliacao": 4.9,
            "pedidos_hoje": 25
        },
        {
            "id": 3,
            "codigo": "BEB001",
            "nome": "Suco Natural de Laranja",
            "descricao": "Suco natural feito na hora",
            "categoria_id": 3,
            "categoria": "Bebidas",
            "preco": 12.00,
            "tempo_preparo": 5,
            "calorias": 150,
            "disponivel": True,
            "destaque": False,
            "avaliacao": 4.7,
            "pedidos_hoje": 45
        }
    ]

    if categoria_id:
        itens = [i for i in itens if i["categoria_id"] == categoria_id]
    if disponivel is not None:
        itens = [i for i in itens if i["disponivel"] == disponivel]
    if destaque is not None:
        itens = [i for i in itens if i["destaque"] == destaque]
    if busca:
        itens = [i for i in itens if busca.lower() in i["nome"].lower() or busca.lower() in i.get("descricao", "").lower()]

    return itens

@router.get("/itens/{item_id}")
async def obter_item(item_id: int, db: Session = Depends(get_db)):
    return {
        "id": item_id,
        "codigo": "PRT001",
        "nome": "Filé à Parmegiana",
        "descricao": "Filé empanado com molho de tomate e queijo gratinado",
        "categoria_id": 2,
        "preco": 65.00,
        "preco_promocional": 58.00,
        "custo": 22.00,
        "margem_lucro": 66.15,
        "tempo_preparo": 35,
        "calorias": 850,
        "serve_pessoas": 1,
        "ingredientes": ["Filé mignon", "Molho de tomate", "Queijo", "Farinha"],
        "alergenos": ["Glúten", "Lactose"],
        "tags": ["Mais vendido", "Chef recomenda"],
        "disponivel": True,
        "grupos_modificadores": [
            {
                "id": 1,
                "nome": "Acompanhamentos",
                "obrigatorio": True,
                "minimo": 1,
                "maximo": 2,
                "modificadores": [
                    {"id": 1, "nome": "Arroz branco", "preco": 0.00, "disponivel": True},
                    {"id": 2, "nome": "Batata frita", "preco": 5.00, "disponivel": True},
                    {"id": 3, "nome": "Salada", "preco": 0.00, "disponivel": True}
                ]
            }
        ]
    }

@router.put("/itens/{item_id}")
async def atualizar_item(
    item_id: int,
    item: ItemCardapio,
    db: Session = Depends(get_db)
):
    return {"id": item_id, **item.dict(), "updated_at": datetime.now()}

@router.patch("/itens/{item_id}/disponibilidade")
async def alterar_disponibilidade(
    item_id: int,
    disponivel: bool,
    db: Session = Depends(get_db)
):
    return {
        "id": item_id,
        "disponivel": disponivel,
        "updated_at": datetime.now()
    }

@router.post("/itens/{item_id}/imagem")
async def upload_imagem_item(
    item_id: int,
    imagem: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    return {
        "item_id": item_id,
        "imagem_url": f"/media/cardapio/item_{item_id}_{imagem.filename}",
        "uploaded_at": datetime.now()
    }

# Modificadores
@router.post("/itens/{item_id}/modificadores")
async def adicionar_grupo_modificadores(
    item_id: int,
    grupo: GrupoModificadores,
    db: Session = Depends(get_db)
):
    return {
        "id": 1,
        "item_id": item_id,
        **grupo.dict(),
        "created_at": datetime.now()
    }

@router.get("/modificadores/grupos")
async def listar_grupos_modificadores(db: Session = Depends(get_db)):
    return [
        {
            "id": 1,
            "nome": "Acompanhamentos",
            "itens_vinculados": 15,
            "modificadores_count": 8
        },
        {
            "id": 2,
            "nome": "Adicionais",
            "itens_vinculados": 20,
            "modificadores_count": 12
        },
        {
            "id": 3,
            "nome": "Ponto da Carne",
            "itens_vinculados": 8,
            "modificadores_count": 5
        }
    ]

# Combos
@router.post("/combos")
async def criar_combo(combo: ComboCardapio, db: Session = Depends(get_db)):
    return {
        "id": 1,
        **combo.dict(),
        "created_at": datetime.now()
    }

@router.get("/combos")
async def listar_combos(
    disponivel: Optional[bool] = True,
    vigente: bool = True,
    db: Session = Depends(get_db)
):
    return [
        {
            "id": 1,
            "nome": "Combo Executivo",
            "descricao": "Prato + Bebida + Sobremesa",
            "preco": 45.00,
            "preco_original": 55.00,
            "economia": 10.00,
            "percentual_desconto": 18.18,
            "itens": [
                {"nome": "Filé Grelhado", "categoria": "Pratos Principais"},
                {"nome": "Suco Natural", "categoria": "Bebidas"},
                {"nome": "Petit Gateau", "categoria": "Sobremesas"}
            ],
            "disponivel": True,
            "vendas_hoje": 8
        }
    ]

# Menu do Dia
@router.post("/menu-diario")
async def criar_menu_diario(menu: MenuDiario, db: Session = Depends(get_db)):
    return {
        "id": 1,
        **menu.dict(),
        "created_at": datetime.now()
    }

@router.get("/menu-diario/hoje")
async def obter_menu_hoje(db: Session = Depends(get_db)):
    return {
        "almoco": {
            "id": 1,
            "nome": "Menu Executivo",
            "descricao": "Menu especial de almoço",
            "preco_fixo": 35.00,
            "itens": [
                {"nome": "Salada Caesar", "categoria": "Entradas"},
                {"nome": "Frango Grelhado", "categoria": "Pratos Principais"},
                {"nome": "Arroz e Feijão", "categoria": "Acompanhamentos"},
                {"nome": "Pudim", "categoria": "Sobremesas"}
            ],
            "horario": "11:30 - 15:00"
        },
        "jantar": None
    }

@router.get("/menu-diario")
async def listar_menu_semanal(
    semana_atual: bool = True,
    db: Session = Depends(get_db)
):
    return [
        {
            "data": "2024-01-15",
            "dia_semana": "Segunda-feira",
            "almoco": {"nome": "Menu Executivo", "preco": 35.00},
            "jantar": {"nome": "Menu Especial", "preco": 55.00}
        },
        {
            "data": "2024-01-16",
            "dia_semana": "Terça-feira",
            "almoco": {"nome": "Menu Light", "preco": 32.00},
            "jantar": None
        }
    ]

# Horários
@router.post("/horarios")
async def configurar_horario(horario: HorarioCardapio, db: Session = Depends(get_db)):
    return {
        "id": 1,
        **horario.dict(),
        "created_at": datetime.now()
    }

@router.get("/horarios")
async def listar_horarios(db: Session = Depends(get_db)):
    return [
        {
            "id": 1,
            "dia_semana": 1,
            "dia_nome": "Segunda",
            "hora_inicio": "11:30",
            "hora_fim": "15:00",
            "cardapio_especial": "Almoço Executivo",
            "ativo": True
        },
        {
            "id": 2,
            "dia_semana": 1,
            "dia_nome": "Segunda",
            "hora_inicio": "19:00",
            "hora_fim": "23:00",
            "cardapio_especial": None,
            "ativo": True
        }
    ]

# Estatísticas
@router.get("/estatisticas/vendas")
async def estatisticas_vendas(
    periodo: str = "hoje",  # hoje, semana, mes
    db: Session = Depends(get_db)
):
    return {
        "periodo": periodo,
        "mais_vendidos": [
            {
                "posicao": 1,
                "item": "Filé à Parmegiana",
                "categoria": "Pratos Principais",
                "quantidade": 45,
                "receita": 2925.00,
                "variacao": "+15%"
            },
            {
                "posicao": 2,
                "item": "Suco Natural de Laranja",
                "categoria": "Bebidas",
                "quantidade": 78,
                "receita": 936.00,
                "variacao": "+8%"
            }
        ],
        "menos_vendidos": [
            {
                "item": "Salada Tropical",
                "quantidade": 2,
                "sugestao": "Considere promoção ou remoção"
            }
        ],
        "categorias_performance": [
            {
                "categoria": "Pratos Principais",
                "vendas": 125,
                "receita": 8125.00,
                "ticket_medio": 65.00
            }
        ]
    }

@router.get("/estatisticas/avaliacoes")
async def estatisticas_avaliacoes(db: Session = Depends(get_db)):
    return {
        "media_geral": 4.7,
        "total_avaliacoes": 1250,
        "melhores_avaliados": [
            {"item": "Filé à Parmegiana", "nota": 4.9, "avaliacoes": 156},
            {"item": "Bruschetta Italiana", "nota": 4.8, "avaliacoes": 98}
        ],
        "precisam_atencao": [
            {"item": "Salada Caesar", "nota": 3.2, "principal_reclamacao": "Pouco tempero"}
        ]
    }

# Relatórios
@router.get("/relatorios/performance")
async def relatorio_performance(
    data_inicio: date = Query(...),
    data_fim: date = Query(...),
    db: Session = Depends(get_db)
):
    return {
        "periodo": f"{data_inicio} a {data_fim}",
        "total_vendas": 3250,
        "receita_total": 195000.00,
        "ticket_medio": 60.00,
        "itens_vendidos": 4500,
        "categorias": [
            {
                "categoria": "Pratos Principais",
                "percentual_vendas": 45,
                "percentual_receita": 55,
                "margem_media": 65
            }
        ],
        "evolucao_diaria": [
            {"data": "2024-01-15", "vendas": 450, "receita": 27000.00}
        ]
    }

@router.get("/relatorios/margem")
async def relatorio_margem(db: Session = Depends(get_db)):
    return {
        "margem_media_geral": 68.5,
        "maior_margem": [
            {"item": "Suco Natural", "margem": 85, "preco": 12.00, "custo": 1.80}
        ],
        "menor_margem": [
            {"item": "Picanha Grelhada", "margem": 45, "preco": 95.00, "custo": 52.25}
        ],
        "sugestoes_preco": [
            {
                "item": "Salada Caesar",
                "preco_atual": 28.00,
                "preco_sugerido": 32.00,
                "aumento_margem": "+8%"
            }
        ]
    }

# Configurações
@router.get("/configuracoes")
async def obter_configuracoes_cardapio(db: Session = Depends(get_db)):
    return {
        "moeda": "BRL",
        "formato_preco": "R$ #,##0.00",
        "mostrar_tempo_preparo": True,
        "mostrar_calorias": True,
        "permitir_observacoes": True,
        "limite_modificadores": 5,
        "taxa_servico": 10.0,
        "incluir_taxa_preco": False
    }

@router.put("/configuracoes")
async def atualizar_configuracoes_cardapio(
    configuracoes: dict,
    db: Session = Depends(get_db)
):
    return {**configuracoes, "updated_at": datetime.now()}