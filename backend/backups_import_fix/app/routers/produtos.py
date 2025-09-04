from fastapi import APIRouter, HTTPException, Depends, status, Query, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc
from typing import List, Optional
from datetime import datetime
import logging
import pandas as pd
import io
from decimal import Decimal

from ..database import get_db
from ..models import Produto, Empresa, TipoProduto, StatusProduto
from ..schemas import (
    ProdutoCreate, ProdutoUpdate, ProdutoResponse, ProdutoList, ProdutoFilter
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/produtos", tags=["produtos"])

@router.get("/", response_model=ProdutoList)
async def listar_produtos(
    skip: int = Query(0, ge=0, description="Número de registros para pular"),
    limit: int = Query(100, ge=1, le=1000, description="Número máximo de registros"),
    nome: Optional[str] = Query(None, description="Filtrar por nome"),
    tipo: Optional[str] = Query(None, description="Filtrar por tipo"),
    categoria: Optional[str] = Query(None, description="Filtrar por categoria"),
    status: Optional[str] = Query(None, description="Filtrar por status"),
    estoque_baixo: Optional[bool] = Query(None, description="Produtos com estoque baixo"),
    db: Session = Depends(get_db)
):
    """Listar produtos com filtros e paginação"""
    try:
        # Query base
        query = db.query(Produto)
        
        # Aplicar filtros
        if nome:
            query = query.filter(Produto.nome.ilike(f"%{nome}%"))
        if tipo:
            query = query.filter(Produto.tipo_usuario== tipo)
        if categoria:
            query = query.filter(Produto.categoria.ilike(f"%{categoria}%"))
        if status:
            query = query.filter(Produto.status == status)
        if estoque_baixo:
            query = query.filter(Produto.estoque_atual <= Produto.estoque_minimo)
        
        # Contar total
        total = query.count()
        
        # Aplicar paginação e ordenação
        produtos = query.order_by(Produto.nome).offset(skip).limit(limit).all()
        
        # Calcular páginas
        pages = (total + limit - 1) // limit
        page = (skip // limit) + 1
        
        return ProdutoList(
            produtos=produtos,
            total=total,
            page=page,
            size=len(produtos),
            pages=pages
        )
        
    except Exception as e:
        logger.error(f"Erro ao listar produtos: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro interno: {str(e)}"
        )

@router.post("/", response_model=ProdutoResponse, status_code=status.HTTP_201_CREATED)
async def criar_produto(
    produto: ProdutoCreate,
    db: Session = Depends(get_db)
):
    """Criar novo produto (global, não atrelado a evento)"""
    try:
        # Verificar código interno único se fornecido
        if produto.codigo_interno:
            produto_existente = db.query(Produto).filter(
                Produto.codigo_interno == produto.codigo_interno
            ).first()
            if produto_existente:
                raise HTTPException(
                    status_code=400,
                    detail="Já existe um produto com este código interno"
                )
        
        # ✅ Criar produto global (sem evento_id)
        produto_data = produto.dict()
        # evento_id removido - produtos são globais
        db_produto = Produto(**produto_data)
        
        db.add(db_produto)
        db.commit()
        db.refresh(db_produto)
        
        logger.info(f"Produto global criado: {db_produto.nome} (ID: {db_produto.id})")
        return db_produto
        
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Erro ao criar produto: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro interno: {str(e)}"
        )

@router.get("/{produto_id}", response_model=ProdutoResponse)
async def obter_produto(
    produto_id: int,
    db: Session = Depends(get_db)
):
    """Obter produto por ID"""
    try:
        produto = db.query(Produto).filter(Produto.id == produto_id).first()
        if not produto:
            raise HTTPException(
                status_code=404,
                detail="Produto não encontrado"
            )
        
        return produto
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao obter produto {produto_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro interno: {str(e)}"
        )

@router.put("/{produto_id}", response_model=ProdutoResponse)
async def atualizar_produto(
    produto_id: int,
    produto: ProdutoUpdate,
    db: Session = Depends(get_db)
):
    """Atualizar produto"""
    try:
        # Buscar produto
        db_produto = db.query(Produto).filter(Produto.id == produto_id).first()
        if not db_produto:
            raise HTTPException(
                status_code=404,
                detail="Produto não encontrado"
            )
        
        # Verificar código interno único se alterado
        if produto.codigo_interno and produto.codigo_interno != db_produto.codigo_interno:
            produto_existente = db.query(Produto).filter(
                and_(
                    Produto.codigo_interno == produto.codigo_interno,
                    Produto.id != produto_id
                )
            ).first()
            if produto_existente:
                raise HTTPException(
                    status_code=400,
                    detail="Já existe um produto com este código interno"
                )
        
        # Atualizar campos
        produto_data = produto.dict(exclude_unset=True)
        for field, value in produto_data.items():
            setattr(db_produto, field, value)
        
        db_produto.atualizado_em = datetime.utcnow()
        db.commit()
        db.refresh(db_produto)
        
        logger.info(f"Produto atualizado: {db_produto.nome} (ID: {db_produto.id})")
        return db_produto
        
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Erro ao atualizar produto {produto_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro interno: {str(e)}"
        )

@router.delete("/{produto_id}")
async def deletar_produto(
    produto_id: int,
    db: Session = Depends(get_db)
):
    """Deletar produto (soft delete)"""
    try:
        # Buscar produto
        db_produto = db.query(Produto).filter(Produto.id == produto_id).first()
        if not db_produto:
            raise HTTPException(
                status_code=404,
                detail="Produto não encontrado"
            )
        
        # Soft delete
        db_produto.status = StatusProduto.INATIVO
        db_produto.atualizado_em = datetime.utcnow()
        db.commit()
        
        logger.info(f"Produto deletado: {db_produto.nome} (ID: {db_produto.id})")
        
        return {"message": "Produto deletado com sucesso"}
        
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Erro ao deletar produto {produto_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro interno: {str(e)}"
        )

@router.post("/import")
async def importar_produtos(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Importar produtos de arquivo CSV ou Excel"""
    try:
        # Verificar tipo do arquivo
        if not file.filename.endswith(('.csv', '.xlsx', '.xls')):
            raise HTTPException(
                status_code=400,
                detail="Formato não suportado. Use CSV ou Excel (.xlsx, .xls)"
            )
        
        # Ler arquivo
        contents = await file.read()
        
        # Processar baseado no tipo
        if file.filename.endswith('.csv'):
            # Tentar diferentes encodings
            try:
                df = pd.read_csv(io.StringIO(contents.decode('utf-8')))
            except UnicodeDecodeError:
                try:
                    df = pd.read_csv(io.StringIO(contents.decode('latin-1')))
                except UnicodeDecodeError:
                    df = pd.read_csv(io.StringIO(contents.decode('cp1252')))
        else:
            # Excel
            df = pd.read_excel(io.BytesIO(contents))
        
        # Mapear colunas para campos do modelo
        column_mapping = {
            # Nome variations
            'produto': 'nome',
            'nome': 'nome',
            'name': 'nome',
            'product': 'nome',
            'product_name': 'nome',
            
            # Preço variations
            'valor': 'preco',
            'preco': 'preco',
            'price': 'preco',
            'valor_unitario': 'preco',
            
            # Categoria variations
            'categoria': 'categoria',
            'category': 'categoria',
            'tipo_produto': 'categoria',
            
            # Código variations
            'codigo': 'codigo_interno',
            'codigo_interno': 'codigo_interno',
            'code': 'codigo_interno',
            'sku': 'codigo_interno',
            
            # Código de barras variations
            'codigo_barras': 'codigo_barras',
            'codigo_de_barras': 'codigo_barras',
            'barcode': 'codigo_barras',
            'ean': 'codigo_barras',
            
            # Estoque variations
            'estoque': 'estoque_atual',
            'estoque_atual': 'estoque_atual',
            'stock': 'estoque_atual',
            'quantidade': 'estoque_atual',
            
            # Descrição variations
            'descricao': 'descricao',
            'description': 'descricao',
            'observacoes': 'descricao',
            
            # Status/Habilitado variations
            'habilitado': 'status',
            'ativo': 'status',
            'status': 'status',
            'enabled': 'status',
            'active': 'status',
            
            # Campos fiscais
            'ncm': 'ncm',
            'cest': 'cest',
            'cfop': 'cfop'
        }
        
        # Normalizar nomes das colunas (minúsculo, sem espaços)
        df.columns = df.columns.str.lower().str.strip().str.replace(' ', '_')
        
        # Mapear colunas
        df_mapped = df.copy()
        for old_col, new_col in column_mapping.items():
            if old_col in df_mapped.columns:
                df_mapped = df_mapped.rename(columns={old_col: new_col})
        
        # Processar e validar dados
        produtos_criados = []
        produtos_erros = []
        
        for index, row in df_mapped.iterrows():
            try:
                # Extrair dados obrigatórios
                nome = str(row.get('nome', '')).strip()
                if not nome or nome == 'nan':
                    produtos_erros.append({
                        'linha': index + 2,  # +2 porque pandas index começa em 0 e tem header
                        'erro': 'Nome é obrigatório'
                    })
                    continue
                
                # Preço
                preco_raw = row.get('preco', 0)
                try:
                    if pd.isna(preco_raw):
                        preco = Decimal('0')
                    else:
                        # Remover formatação de moeda se existir
                        preco_str = str(preco_raw).replace('R$', '').replace('.', '').replace(',', '.').strip()
                        preco = Decimal(preco_str) if preco_str else Decimal('0')
                except (ValueError, TypeError):
                    preco = Decimal('0')
                
                # Categoria
                categoria = str(row.get('categoria', '')).strip()
                if categoria == 'nan':
                    categoria = None
                
                # Código interno
                codigo_interno = str(row.get('codigo_interno', '')).strip()
                if codigo_interno == 'nan':
                    codigo_interno = None
                
                # Estoque
                estoque_raw = row.get('estoque_atual', 0)
                try:
                    estoque_atual = int(float(estoque_raw)) if not pd.isna(estoque_raw) else 0
                except (ValueError, TypeError):
                    estoque_atual = 0
                
                # Descrição
                descricao = str(row.get('descricao', '')).strip()
                if descricao == 'nan':
                    descricao = None
                
                # Status - mapear habilitado/ativo para status
                status_raw = row.get('status', 'ATIVO')
                if pd.isna(status_raw):
                    status = StatusProduto.ATIVO
                else:
                    status_str = str(status_raw).strip().upper()
                    if status_str in ['SIM', 'TRUE', '1', 'ATIVO', 'HABILITADO']:
                        status = StatusProduto.ATIVO
                    elif status_str in ['NAO', 'NÃO', 'FALSE', '0', 'INATIVO', 'DESABILITADO']:
                        status = StatusProduto.INATIVO
                    else:
                        status = StatusProduto.ATIVO
                
                # Tipo - padrão BEBIDA se não especificado
                tipo_usuario=TipoProduto.BEBIDA
                
                # Criar produto
                produto_data = ProdutoCreate(
                    nome=nome,
                    descricao=descricao,
                    tipo_usuario=tipo,
                    preco=preco,
                    codigo_interno=codigo_interno,
                    estoque_atual=estoque_atual,
                    estoque_minimo=0,
                    estoque_maximo=1000,
                    controla_estoque=True,
                    categoria=categoria,
                    imagem_url=None
                )
                
                # Verificar se produto já existe (por nome ou código)
                existing = db.query(Produto).filter(
                    or_(
                        Produto.nome == nome,
                        and_(Produto.codigo_interno == codigo_interno, codigo_interno is not None)
                    )
                ).first()
                
                if existing:
                    produtos_erros.append({
                        'linha': index + 2,
                        'erro': f'Produto já existe: {nome}'
                    })
                    continue
                
                # Criar produto no banco
                db_produto = Produto(
                    nome=produto_data.nome,
                    descricao=produto_data.descricao,
                    tipo_usuario=produto_data.tipo,
                    preco=produto_data.preco,
                    codigo_interno=produto_data.codigo_interno,
                    estoque_atual=produto_data.estoque_atual,
                    estoque_minimo=produto_data.estoque_minimo,
                    estoque_maximo=produto_data.estoque_maximo,
                    controla_estoque=produto_data.controla_estoque,
                    categoria=produto_data.categoria,
                    imagem_url=produto_data.imagem_url,
                    status=status,
                    criado_em=datetime.utcnow()
                )
                
                db.add(db_produto)
                db.flush()  # Para obter o ID
                
                produtos_criados.append({
                    'linha': index + 2,
                    'nome': nome,
                    'id': db_produto.id
                })
                
            except Exception as e:
                produtos_erros.append({
                    'linha': index + 2,
                    'erro': str(e)
                })
        
        # Commit apenas se houve produtos criados
        if produtos_criados:
            db.commit()
        else:
            db.rollback()
        
        return {
            'total_linhas': len(df),
            'produtos_criados': len(produtos_criados),
            'produtos_com_erro': len(produtos_erros),
            'detalhes_criados': produtos_criados,
            'detalhes_erros': produtos_erros,
            'campos_detectados': list(df_mapped.columns),
            'campos_mapeados': {k: v for k, v in column_mapping.items() if k in df.columns}
        }
        
    except Exception as e:
        logger.error(f"Erro ao importar produtos: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao processar arquivo: {str(e)}"
        )

@router.get("/import/template")
async def download_template():
    """Download template CSV para importação"""
    template_data = {
        'nome': ['Heineken Long Neck', 'Coca-Cola 350ml', 'Hambúrguer Artesanal'],
        'categoria': ['Cervejas', 'Refrigerantes', 'Lanches'],
        'preco': ['12.50', '5.00', '25.90'],
        'codigo_interno': ['HEIN001', 'COCA001', 'BURG001'],
        'codigo_barras': ['7891149003792', '7894900011517', ''],
        'estoque_atual': ['100', '50', '20'],
        'descricao': ['Cerveja premium importada', 'Refrigerante gelado', 'Hambúrguer 180g com batata'],
        'habilitado': ['SIM', 'SIM', 'SIM']
    }
    
    df = pd.DataFrame(template_data)
    
    # Criar CSV em memória
    output = io.StringIO()
    df.to_csv(output, index=False, encoding='utf-8')
    csv_content = output.getvalue()
    
    return {
        'filename': 'template_importacao_produtos.csv',
        'content': csv_content,
        'content_type': 'text/csv'
    }
