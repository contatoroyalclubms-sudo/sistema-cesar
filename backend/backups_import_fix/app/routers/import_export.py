"""
API endpoints para funcionalidades de Import/Export
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query, Form, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from ..database import get_db
from ..auth_functions import obter_usuario_atual
from ..services.import_export_service import ImportExportService
from ..schemas_import_export import (
    OperacaoImportacaoCreate, OperacaoImportacaoResponse,
    ConfiguracaoImportacao, ConfiguracaoExportacao,
    PreviewImportacao, PreviewExportacao, ResultadoValidacao,
    TemplateImportacaoCreate, TemplateImportacaoResponse,
    EstatisticasImportExport, FormatoArquivo, TipoExportacao,
    OpcoesImportacao, CampoDisponivel
)

router = APIRouter(prefix="/api/estoque", tags=["import-export"])

# Dependencies
def get_import_export_service(db: Session = Depends(get_db)) -> ImportExportService:
    return ImportExportService(db)

def get_evento_id(current_user = Depends(obter_usuario_atual)) -> int:
    # Por simplicidade, vamos usar um evento padrão
    # Em produção, isso viria do contexto do usuário ou parâmetro
    return 1  # Ou extrair do current_user


# ==================== ENDPOINTS DE IMPORTAÇÃO ====================

@router.get("/import/options", response_model=OpcoesImportacao)
async def get_import_options(
    service: ImportExportService = Depends(get_import_export_service),
    current_user = Depends(obter_usuario_atual)
):
    """Obter opções disponíveis para importação"""
    
    # Campos disponíveis para mapeamento
    campos_disponiveis = [
        CampoDisponivel(
            nome="codigo",
            tipo_usuario="string",
            obrigatorio=True,
            descricao="Código/SKU único do produto",
            aliases=["codigo", "code", "sku", "cod", "id"],
            validacoes=["required", "unique", "max_length:50"]
        ),
        CampoDisponivel(
            nome="nome",
            tipo_usuario="string",
            obrigatorio=True,
            descricao="Nome do produto",
            aliases=["nome", "name", "produto", "product", "title"],
            validacoes=["required", "min_length:3", "max_length:255"]
        ),
        CampoDisponivel(
            nome="categoria",
            tipo_usuario="string",
            obrigatorio=True,
            descricao="Categoria do produto",
            aliases=["categoria", "category", "cat", "tipo"],
            validacoes=["required"]
        ),
        CampoDisponivel(
            nome="preco_venda",
            tipo_usuario="number",
            obrigatorio=True,
            descricao="Preço de venda",
            aliases=["preco", "price", "valor", "preco_venda"],
            validacoes=["required", "min:0.01"]
        ),
        CampoDisponivel(
            nome="codigo_barras",
            tipo_usuario="string",
            obrigatorio=False,
            descricao="Código de barras EAN",
            aliases=["barras", "barcode", "ean", "gtin"],
            validacoes=["pattern:digits", "length:8-14", "unique"]
        ),
        CampoDisponivel(
            nome="marca",
            tipo_usuario="string",
            obrigatorio=False,
            descricao="Marca do produto",
            aliases=["marca", "brand"],
            validacoes=["max_length:100"]
        ),
        CampoDisponivel(
            nome="fornecedor",
            tipo_usuario="string",
            obrigatorio=False,
            descricao="Fornecedor do produto",
            aliases=["fornecedor", "supplier", "vendor"],
            validacoes=["max_length:200"]
        ),
        CampoDisponivel(
            nome="preco_custo",
            tipo_usuario="number",
            obrigatorio=False,
            descricao="Preço de custo",
            aliases=["custo", "cost", "preco_custo"],
            validacoes=["min:0"]
        ),
        CampoDisponivel(
            nome="estoque_atual",
            tipo_usuario="integer",
            obrigatorio=False,
            descricao="Quantidade em estoque",
            aliases=["estoque", "stock", "quantidade", "qty"],
            validacoes=["min:0"]
        ),
        CampoDisponivel(
            nome="estoque_minimo",
            tipo_usuario="integer",
            obrigatorio=False,
            descricao="Estoque mínimo para alerta",
            aliases=["estoque_min", "min_stock"],
            validacoes=["min:0"]
        )
    ]
    
    # Templates disponíveis (simulado)
    templates_disponiveis = []
    
    # Categorias existentes (simulado)
    categorias_existentes = ["Bebidas", "Comidas", "Combos", "Fichas"]
    
    # Fornecedores existentes (simulado)
    fornecedores_existentes = ["Fornecedor A", "Fornecedor B", "Fornecedor C"]
    
    return OpcoesImportacao(
        formatos_suportados=[FormatoArquivo.CSV, FormatoArquivo.XLSX, FormatoArquivo.JSON],
        campos_disponiveis=campos_disponiveis,
        templates_disponiveis=templates_disponiveis,
        categorias_existentes=categorias_existentes,
        fornecedores_existentes=fornecedores_existentes
    )


@router.post("/upload")
async def upload_import_file(
    file: UploadFile = File(...),
    service: ImportExportService = Depends(get_import_export_service),
    evento_id: int = Depends(get_evento_id),
    current_user = Depends(obter_usuario_atual)
):
    """Upload arquivo para importação"""
    
    # Validar tamanho do arquivo (10MB)
    if file.size and file.size > 10 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="Arquivo muito grande. Tamanho máximo: 10MB"
        )
    
    # Validar tipo de arquivo
    allowed_extensions = ['.csv', '.xlsx', '.xls', '.json']
    if not any(file.filename.lower().endswith(ext) for ext in allowed_extensions):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Formato de arquivo não suportado. Use: CSV, Excel ou JSON"
        )
    
    result = await service.upload_file(file, current_user.id, evento_id)
    return result


@router.post("/validate/{operacao_id}")
async def validate_import_data(
    operacao_id: int,
    mapeamento: Dict[str, str],
    service: ImportExportService = Depends(get_import_export_service),
    current_user = Depends(obter_usuario_atual)
):
    """Validar dados antes da importação"""
    
    resultado = await service.validate_import_data(operacao_id, mapeamento)
    return resultado


@router.post("/import/{operacao_id}")
async def execute_import(
    operacao_id: int,
    mapeamento: Dict[str, str],
    service: ImportExportService = Depends(get_import_export_service),
    current_user = Depends(obter_usuario_atual)
):
    """Executar importação dos dados"""
    
    resultado = await service.execute_import(operacao_id, mapeamento)
    return resultado


@router.get("/import/{operacao_id}/status")
async def get_import_status(
    operacao_id: int,
    service: ImportExportService = Depends(get_import_export_service),
    current_user = Depends(obter_usuario_atual)
):
    """Obter status da importação"""
    
    from app.models import OperacaoImportExport
    
    operacao = service.db.query(OperacaoImportExport).filter(
        OperacaoImportExport.id == operacao_id
    ).first()
    
    if not operacao:
        raise HTTPException(status_code=404, detail="Operação não encontrada")
    
    return {
        'id': operacao.id,
        'status': operacao.status.value,
        'progresso': {
            'total': operacao.total_registros,
            'processados': operacao.registros_processados,
            'sucessos': operacao.registros_sucesso,
            'erros': operacao.registros_erro,
            'avisos': operacao.registros_aviso
        },
        'tempo_decorrido': (
            (operacao.fim_processamento or datetime.utcnow()) - 
            (operacao.inicio_processamento or operacao.criado_em)
        ).total_seconds() if operacao.inicio_processamento else 0,
        'log': operacao.log_detalhado
    }


# ==================== ENDPOINTS DE EXPORTAÇÃO ====================

@router.post("/export/preview")
async def preview_export(
    config: ConfiguracaoExportacao,
    service: ImportExportService = Depends(get_import_export_service),
    evento_id: int = Depends(get_evento_id),
    current_user = Depends(obter_usuario_atual)
):
    """Gerar preview da exportação"""
    
    preview = await service.preview_export(config, evento_id)
    return preview


@router.post("/export")
async def export_data(
    config: ConfiguracaoExportacao,
    service: ImportExportService = Depends(get_import_export_service),
    evento_id: int = Depends(get_evento_id),
    current_user = Depends(obter_usuario_atual)
):
    """Executar exportação de dados"""
    
    return await service.execute_export(config, evento_id, current_user.id)


@router.get("/export/formats")
async def get_export_formats():
    """Obter formatos disponíveis para exportação"""
    
    return {
        'formats': [
            {
                'format': FormatoArquivo.CSV,
                'name': 'CSV',
                'description': 'Valores separados por vírgula - universal',
                'icon': '📄',
                'extensions': ['.csv']
            },
            {
                'format': FormatoArquivo.XLSX,
                'name': 'Excel',
                'description': 'Planilha Excel - melhor para análise',
                'icon': '📊',
                'extensions': ['.xlsx']
            },
            {
                'format': FormatoArquivo.JSON,
                'name': 'JSON',
                'description': 'Formato JSON - para integrações',
                'icon': '⚡',
                'extensions': ['.json']
            },
            {
                'format': FormatoArquivo.PDF,
                'name': 'PDF',
                'description': 'Relatório PDF - para impressão',
                'icon': '📑',
                'extensions': ['.pdf']
            }
        ],
        'types': [
            {
                'type': TipoExportacao.ESTOQUE_COMPLETO,
                'name': 'Estoque Completo',
                'description': 'Todos os produtos com informações detalhadas'
            },
            {
                'type': TipoExportacao.ESTOQUE_BAIXO,
                'name': 'Produtos em Baixa',
                'description': 'Apenas produtos com estoque abaixo do mínimo'
            },
            {
                'type': TipoExportacao.LISTA_PRECOS,
                'name': 'Lista de Preços',
                'description': 'Código, nome e preços para fornecedores'
            },
            {
                'type': TipoExportacao.FISCAL,
                'name': 'Relatório Fiscal',
                'description': 'Dados para contabilidade e impostos'
            },
            {
                'type': TipoExportacao.INVENTARIO,
                'name': 'Inventário',
                'description': 'Para contagem física de estoque'
            }
        ]
    }


# ==================== ENDPOINTS DE TEMPLATES ====================

@router.get("/templates", response_model=List[TemplateImportacaoResponse])
async def get_import_templates(
    service: ImportExportService = Depends(get_import_export_service),
    current_user = Depends(obter_usuario_atual)
):
    """Obter templates de importação disponíveis"""
    
    from app.models import TemplateImportacao
    
    templates = service.db.query(TemplateImportacao).filter(
        TemplateImportacao.ativo == True
    ).all()
    
    return templates


@router.post("/templates", response_model=TemplateImportacaoResponse)
async def create_import_template(
    template_data: TemplateImportacaoCreate,
    service: ImportExportService = Depends(get_import_export_service),
    current_user = Depends(obter_usuario_atual)
):
    """Criar novo template de importação"""
    
    from app.models import TemplateImportacao
    import json
    
    template = TemplateImportacao(
        nome=template_data.nome,
        descricao=template_data.descricao,
        formato=template_data.formato,
        mapeamento_padrao=json.dumps(template_data.mapeamento_padrao),
        campos_obrigatorios=json.dumps(template_data.campos_obrigatorios),
        validacoes_personalizadas=json.dumps(template_data.validacoes_personalizadas or {}),
        usuario_criador_id=current_user.id
    )
    
    service.db.add(template)
    service.db.commit()
    service.db.refresh(template)
    
    return template


@router.get("/templates/{format}/download")
async def download_template(
    format: FormatoArquivo,
    current_user = Depends(obter_usuario_atual)
):
    """Download template vazio para importação"""
    
    import io
    import csv
    import json
    import pandas as pd
    
    # Campos padrão do template
    campos = [
        'codigo', 'nome', 'categoria', 'preco_venda', 'codigo_barras',
        'marca', 'fornecedor', 'preco_custo', 'estoque_atual', 'estoque_minimo'
    ]
    
    # Exemplo de dados
    exemplo = {
        'codigo': 'PROD001',
        'nome': 'Produto Exemplo',
        'categoria': 'Bebidas',
        'preco_venda': '10.50',
        'codigo_barras': '1234567890123',
        'marca': 'Marca Exemplo',
        'fornecedor': 'Fornecedor Exemplo',
        'preco_custo': '7.00',
        'estoque_atual': '100',
        'estoque_minimo': '10'
    }
    
    if format == FormatoArquivo.CSV:
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=campos)
        writer.writeheader()
        writer.writerow(exemplo)
        
        content = output.getvalue().encode('utf-8')
        media_type = "text/csv"
        filename = "template_produtos.csv"
        
    elif format == FormatoArquivo.XLSX:
        df = pd.DataFrame([exemplo])
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Produtos')
        
        content = output.getvalue()
        media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        filename = "template_produtos.xlsx"
        
    elif format == FormatoArquivo.JSON:
        data = [exemplo]
        content = json.dumps(data, ensure_ascii=False, indent=2).encode('utf-8')
        media_type = "application/json"
        filename = "template_produtos.json"
        
    else:
        raise HTTPException(status_code=400, detail="Formato não suportado para template")
    
    return StreamingResponse(
        io.BytesIO(content),
        media_type=media_type,
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


# ==================== ENDPOINTS DE MONITORAMENTO ====================

@router.get("/dashboard/stats")
async def get_dashboard_stats(
    service: ImportExportService = Depends(get_import_export_service),
    evento_id: int = Depends(get_evento_id),
    current_user = Depends(obter_usuario_atual)
):
    """Obter estatísticas do dashboard de import/export"""
    
    stats = service.get_dashboard_stats(evento_id)
    recent_operations = service.get_recent_operations(evento_id, 10)
    
    return {
        'stats': stats,
        'recent_operations': recent_operations
    }


@router.get("/jobs")
async def get_import_export_jobs(
    limit: int = Query(20, ge=1, le=100),
    status_filter: Optional[str] = Query(None),
    service: ImportExportService = Depends(get_import_export_service),
    evento_id: int = Depends(get_evento_id),
    current_user = Depends(obter_usuario_atual)
):
    """Listar jobs de import/export"""
    
    from app.models import OperacaoImportExport, StatusImportacao
    
    query = service.db.query(OperacaoImportExport).filter(
        OperacaoImportExport.evento_id == evento_id
    )
    
    if status_filter:
        try:
            status_enum = StatusImportacao(status_filter)
            query = query.filter(OperacaoImportExport.status == status_enum)
        except ValueError:
            raise HTTPException(status_code=400, detail="Status inválido")
    
    jobs = query.order_by(OperacaoImportExport.criado_em.desc()).limit(limit).all()
    
    return [
        {
            'id': job.id,
            'tipo': job.tipo_operacao.value,
            'arquivo': job.nome_arquivo,
            'status': job.status.value,
            'total_registros': job.total_registros,
            'registros_sucesso': job.registros_sucesso,
            'registros_erro': job.registros_erro,
            'criado_em': job.criado_em.isoformat(),
            'inicio_processamento': job.inicio_processamento.isoformat() if job.inicio_processamento else None,
            'fim_processamento': job.fim_processamento.isoformat() if job.fim_processamento else None
        }
        for job in jobs
    ]


@router.delete("/jobs/{job_id}")
async def cancel_job(
    job_id: int,
    service: ImportExportService = Depends(get_import_export_service),
    current_user = Depends(obter_usuario_atual)
):
    """Cancelar job de import/export"""
    
    from app.models import OperacaoImportExport, StatusImportacao
    
    job = service.db.query(OperacaoImportExport).filter(
        OperacaoImportExport.id == job_id
    ).first()
    
    if not job:
        raise HTTPException(status_code=404, detail="Job não encontrado")
    
    if job.status not in [StatusImportacao.PENDENTE, StatusImportacao.PROCESSANDO]:
        raise HTTPException(status_code=400, detail="Job não pode ser cancelado")
    
    job.status = StatusImportacao.CANCELADA
    job.fim_processamento = datetime.utcnow()
    service.db.commit()
    
    return {"message": "Job cancelado com sucesso"}


# ==================== ENDPOINTS DE RELATÓRIOS ====================

@router.get("/reports/giro")
async def relatorio_giro_estoque(
    periodo: int = Query(30, ge=1, le=365, description="Período em dias"),
    service: ImportExportService = Depends(get_import_export_service),
    evento_id: int = Depends(get_evento_id),
    current_user = Depends(obter_usuario_atual)
):
    """Relatório de giro de estoque"""
    
    # Simulação do relatório - em produção seria implementado no service
    return {
        'periodo_dias': periodo,
        'produtos': [
            {
                'codigo': 'PROD001',
                'nome': 'Produto A',
                'categoria': 'Bebidas',
                'estoque_medio': 50.0,
                'vendas_periodo': 30,
                'giro': 0.6
            },
            {
                'codigo': 'PROD002',
                'nome': 'Produto B',
                'categoria': 'Comidas',
                'estoque_medio': 25.0,
                'vendas_periodo': 45,
                'giro': 1.8
            }
        ]
    }


@router.get("/reports/abc")
async def relatorio_analise_abc(
    service: ImportExportService = Depends(get_import_export_service),
    evento_id: int = Depends(get_evento_id),
    current_user = Depends(obter_usuario_atual)
):
    """Análise ABC de produtos"""
    
    # Simulação do relatório - em produção seria implementado no service
    return {
        'analise': [
            {
                'produto_id': 1,
                'nome': 'Produto Top',
                'faturamento': 15000.0,
                'classe': 'A',
                'percentual_acumulado': 30.0
            },
            {
                'produto_id': 2,
                'nome': 'Produto Médio',
                'faturamento': 8000.0,
                'classe': 'B',
                'percentual_acumulado': 60.0
            },
            {
                'produto_id': 3,
                'nome': 'Produto Baixo',
                'faturamento': 2000.0,
                'classe': 'C',
                'percentual_acumulado': 85.0
            }
        ]
    }


@router.get("/reports/perdas")
async def relatorio_perdas(
    periodo: int = Query(30, ge=1, le=365, description="Período em dias"),
    service: ImportExportService = Depends(get_import_export_service),
    evento_id: int = Depends(get_evento_id),
    current_user = Depends(obter_usuario_atual)
):
    """Relatório de perdas"""
    
    # Simulação do relatório - em produção seria implementado no service
    return {
        'periodo_dias': periodo,
        'perdas': [
            {
                'nome_produto': 'Produto X',
                'motivo': 'Validade',
                'quantidade_perdida': 5,
                'valor_perdido': 125.0
            },
            {
                'nome_produto': 'Produto Y',
                'motivo': 'Quebra',
                'quantidade_perdida': 3,
                'valor_perdido': 90.0
            }
        ],
        'total_perdido': 215.0
    }


@router.get("/health")
async def health_check():
    """Health check do módulo import/export"""
    return {
        "status": "healthy",
        "module": "import-export",
        "timestamp": datetime.utcnow().isoformat()
    }
