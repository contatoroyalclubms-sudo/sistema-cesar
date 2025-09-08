"""
Serviço de Import/Export para o módulo de estoque
"""
import io
import json
import csv
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple, Union
from pathlib import Path
import pandas as pd
import openpyxl
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from fastapi import HTTPException, UploadFile
from fastapi.responses import StreamingResponse

from app.models import (
    Produto, OperacaoImportExport, ValidacaoImportacao, TemplateImportacao,
    StatusImportacao, TipoOperacao, StatusValidacao, TipoProduto, StatusProduto
)
from app.schemas_import_export import (
    ProdutoImportacao, ConfiguracaoImportacao, ValidacaoImportacaoResponse,
    PreviewImportacao, FiltroExportacao, ConfiguracaoExportacao,
    PreviewExportacao, ResultadoValidacao, RegraValidacao,
    FormatoArquivo, TipoExportacao, StatusImportacao as StatusImportacaoEnum
)


class ImportExportService:
    """Serviço principal para operações de import/export"""
    
    def __init__(self, db: Session):
        self.db = db
        self.chunk_size = 100  # Processar em lotes de 100 registros
        
        # Regras de validação padrão
        self.validation_rules = {
            'codigo': {
                'required': True,
                'unique': True,
                'max_length': 50,
                'pattern': r'^[A-Z0-9_-]+$',
                'message': 'Código deve ser único e conter apenas letras, números, _ ou -'
            },
            'nome': {
                'required': True,
                'min_length': 3,
                'max_length': 100,
                'message': 'Nome deve ter entre 3 e 100 caracteres'
            },
            'preco_venda': {
                'required': True,
                'type': 'number',
                'min': 0.01,
                'message': 'Preço deve ser maior que zero'
            },
            'categoria': {
                'required': True,
                'message': 'Categoria é obrigatória'
            },
            'codigo_barras': {
                'pattern': r'^\d{8,14}$',
                'unique': True,
                'message': 'Código de barras deve ter 8-14 dígitos e ser único'
            },
            'ncm': {
                'pattern': r'^\d{8}$',
                'message': 'NCM deve ter exatamente 8 dígitos'
            }
        }

    # ==================== MÉTODOS DE IMPORTAÇÃO ====================
    
    async def upload_file(self, file: UploadFile, user_id: int) -> Dict[str, Any]:
        """Upload e análise inicial do arquivo"""
        # Validar tipo de arquivo
        formato = self._get_file_format(file.filename)
        if not formato:
            raise HTTPException(status_code=400, detail="Formato de arquivo não suportado")
        
        # Ler conteúdo do arquivo
        content = await file.read()
        
        # Criar registro da operação
        operacao = OperacaoImportExport(
            tipo_operacao=TipoOperacao.IMPORTACAO,
            nome_arquivo=file.filename,
            formato_arquivo=formato,
            tamanho_arquivo=len(content),
            usuario_id=user_id,
            evento_id=None,  # Produtos são globais, não atrelados a eventos
            status=StatusImportacao.PENDENTE
        )
        
        self.db.add(operacao)
        self.db.commit()
        self.db.refresh(operacao)
        
        # Analisar estrutura do arquivo
        try:
            headers, sample_data = self._analyze_file_structure(content, formato)
            
            # Atualizar registro com informações iniciais
            operacao.total_registros = len(sample_data)
            self.db.commit()
            
            return {
                'operacao_id': operacao.id,
                'headers': headers,
                'sample_data': sample_data[:5],  # Primeiras 5 linhas
                'total_rows': len(sample_data),
                'suggested_mapping': self._suggest_field_mapping(headers)
            }
            
        except Exception as e:
            operacao.status = StatusImportacao.ERRO
            operacao.log_detalhado = str(e)
            self.db.commit()
            raise HTTPException(status_code=400, detail=f"Erro ao analisar arquivo: {str(e)}")

    def _get_file_format(self, filename: str) -> Optional[str]:
        """Detectar formato do arquivo"""
        if not filename:
            return None
            
        extension = Path(filename).suffix.lower()
        format_map = {
            '.csv': 'csv',
            '.xlsx': 'xlsx',
            '.xls': 'xlsx',
            '.json': 'json'
        }
        return format_map.get(extension)

    def _analyze_file_structure(self, content: bytes, formato: str) -> Tuple[List[str], List[Dict]]:
        """Analisar estrutura do arquivo e extrair cabeçalhos e dados de exemplo"""
        if formato == 'csv':
            return self._analyze_csv(content)
        elif formato == 'xlsx':
            return self._analyze_excel(content)
        elif formato == 'json':
            return self._analyze_json(content)
        else:
            raise ValueError(f"Formato {formato} não suportado")

    def _analyze_csv(self, content: bytes) -> Tuple[List[str], List[Dict]]:
        """Analisar arquivo CSV"""
        try:
            # Tentar diferentes encodings
            for encoding in ['utf-8', 'latin-1', 'cp1252']:
                try:
                    text = content.decode(encoding)
                    break
                except UnicodeDecodeError:
                    continue
            else:
                raise ValueError("Não foi possível decodificar o arquivo")
            
            # Detectar separador
            sniffer = csv.Sniffer()
            sample = text[:1024]
            delimiter = sniffer.sniff(sample).delimiter
            
            # Ler dados
            reader = csv.DictReader(io.StringIO(text), delimiter=delimiter)
            headers = reader.fieldnames or []
            data = [row for row in reader]
            
            return headers, data
            
        except Exception as e:
            raise ValueError(f"Erro ao ler CSV: {str(e)}")

    def _analyze_excel(self, content: bytes) -> Tuple[List[str], List[Dict]]:
        """Analisar arquivo Excel"""
        try:
            # Usar pandas para ler Excel
            df = pd.read_excel(io.BytesIO(content), nrows=1000)  # Limitar a 1000 linhas
            
            headers = df.columns.tolist()
            data = df.to_dict('records')
            
            return headers, data
            
        except Exception as e:
            raise ValueError(f"Erro ao ler Excel: {str(e)}")

    def _analyze_json(self, content: bytes) -> Tuple[List[str], List[Dict]]:
        """Analisar arquivo JSON"""
        try:
            text = content.decode('utf-8')
            data = json.loads(text)
            
            if not isinstance(data, list):
                raise ValueError("JSON deve ser um array de objetos")
            
            if not data:
                return [], []
            
            # Extrair cabeçalhos do primeiro objeto
            headers = list(data[0].keys()) if data else []
            
            return headers, data
            
        except Exception as e:
            raise ValueError(f"Erro ao ler JSON: {str(e)}")

    def _suggest_field_mapping(self, headers: List[str]) -> Dict[str, str]:
        """Sugerir mapeamento de campos baseado nos cabeçalhos"""
        mapping = {}
        
        # Dicionário de aliases para mapeamento automático
        aliases = {
            'codigo': ['codigo', 'code', 'sku', 'cod', 'id'],
            'nome': ['nome', 'name', 'produto', 'product', 'title'],
            'categoria': ['categoria', 'category', 'cat', 'tipo'],
            'preco_venda': ['preco', 'price', 'valor', 'preco_venda', 'selling_price'],
            'preco_custo': ['custo', 'cost', 'preco_custo', 'cost_price'],
            'codigo_barras': ['barras', 'barcode', 'ean', 'gtin'],
            'estoque_atual': ['estoque', 'stock', 'quantidade', 'qty'],
            'marca': ['marca', 'brand'],
            'fornecedor': ['fornecedor', 'supplier', 'vendor']
        }
        
        for header in headers:
            header_lower = header.lower().strip()
            
            for field, field_aliases in aliases.items():
                if header_lower in field_aliases:
                    mapping[header] = field
                    break
        
        return mapping

    async def validate_import_data(self, operacao_id: int, mapeamento: Dict[str, str]) -> ResultadoValidacao:
        """Validar dados antes da importação"""
        operacao = self.db.query(OperacaoImportExport).filter(
            OperacaoImportExport.id == operacao_id
        ).first()
        
        if not operacao:
            raise HTTPException(status_code=404, detail="Operação não encontrada")
        
        # Recarregar dados do arquivo
        # Aqui você precisaria implementar a lógica para recarregar os dados
        # Para este exemplo, vamos simular
        
        validacoes = []
        total_linhas = operacao.total_registros
        linhas_validas = 0
        linhas_com_erro = 0
        linhas_com_aviso = 0
        
        # Simular validação de algumas linhas
        for i in range(min(100, total_linhas)):  # Validar primeiras 100 linhas
            linha_validacoes = self._validate_row(i + 1, {}, mapeamento)
            validacoes.extend(linha_validacoes)
            
            has_critical = any(v.status == StatusValidacao.ERRO_CRITICO for v in linha_validacoes)
            has_warning = any(v.status == StatusValidacao.AVISO for v in linha_validacoes)
            
            if has_critical:
                linhas_com_erro += 1
            elif has_warning:
                linhas_com_aviso += 1
            else:
                linhas_validas += 1
        
        # Agrupar erros por tipo
        resumo_erros = {}
        for validacao in validacoes:
            if validacao.status == StatusValidacao.ERRO_CRITICO:
                resumo_erros[validacao.tipo_validacao] = resumo_erros.get(validacao.tipo_validacao, 0) + 1
        
        resultado = ResultadoValidacao(
            total_linhas=total_linhas,
            linhas_validas=linhas_validas,
            linhas_com_erro=linhas_com_erro,
            linhas_com_aviso=linhas_com_aviso,
            pode_importar=linhas_com_erro == 0,
            resumo_erros=resumo_erros,
            detalhes=validacoes
        )
        
        return resultado

    def _validate_row(self, linha: int, dados: Dict[str, Any], mapeamento: Dict[str, str]) -> List[ValidacaoImportacaoResponse]:
        """Validar uma linha de dados"""
        validacoes = []
        
        # Mapear dados conforme mapeamento
        dados_mapeados = {}
        for campo_arquivo, campo_sistema in mapeamento.items():
            if campo_arquivo in dados:
                dados_mapeados[campo_sistema] = dados[campo_arquivo]
        
        # Aplicar regras de validação
        for campo, regras in self.validation_rules.items():
            valor = dados_mapeados.get(campo)
            
            # Validação de campo obrigatório
            if regras.get('required') and (not valor or str(valor).strip() == ''):
                validacoes.append(ValidacaoImportacaoResponse(
                    linha=linha,
                    campo=campo,
                    tipo_validacao='required',
                    status=StatusValidacao.ERRO_CRITICO,
                    mensagem=f'{campo} é obrigatório',
                    valor_original=str(valor) if valor is not None else '',
                    valor_sugerido=None
                ))
                continue
            
            if not valor:
                continue  # Pular outras validações se campo vazio e não obrigatório
            
            # Validação de tipo
            if regras.get('type') == 'number':
                try:
                    float(valor)
                except (ValueError, TypeError):
                    validacoes.append(ValidacaoImportacaoResponse(
                        linha=linha,
                        campo=campo,
                        tipo_validacao='type',
                        status=StatusValidacao.ERRO_CRITICO,
                        mensagem=f'{campo} deve ser um número',
                        valor_original=str(valor),
                        valor_sugerido=None
                    ))
                    continue
            
            # Validação de padrão
            if regras.get('pattern'):
                import re
                if not re.match(regras['pattern'], str(valor)):
                    validacoes.append(ValidacaoImportacaoResponse(
                        linha=linha,
                        campo=campo,
                        tipo_validacao='pattern',
                        status=StatusValidacao.AVISO,
                        mensagem=regras.get('message', f'{campo} não atende ao padrão esperado'),
                        valor_original=str(valor),
                        valor_sugerido=None
                    ))
        
        return validacoes

    async def execute_import(self, operacao_id: int, mapeamento: Dict[str, str]) -> Dict[str, Any]:
        """Executar importação dos dados"""
        operacao = self.db.query(OperacaoImportExport).filter(
            OperacaoImportExport.id == operacao_id
        ).first()
        
        if not operacao:
            raise HTTPException(status_code=404, detail="Operação não encontrada")
        
        # Atualizar status
        operacao.status = StatusImportacao.PROCESSANDO
        operacao.inicio_processamento = datetime.utcnow()
        operacao.mapeamento_campos = json.dumps(mapeamento)
        self.db.commit()
        
        try:
            # Aqui você implementaria a lógica real de importação
            # Por enquanto, vamos simular o processo
            
            await asyncio.sleep(2)  # Simular processamento
            
            # Atualizar resultado
            operacao.status = StatusImportacao.CONCLUIDA
            operacao.fim_processamento = datetime.utcnow()
            operacao.registros_processados = operacao.total_registros
            operacao.registros_sucesso = operacao.total_registros - 5  # Simular alguns erros
            operacao.registros_erro = 3
            operacao.registros_aviso = 2
            
            resumo = {
                'total_processados': operacao.registros_processados,
                'sucessos': operacao.registros_sucesso,
                'erros': operacao.registros_erro,
                'avisos': operacao.registros_aviso,
                'tempo_processamento': 2.0,
                'produtos_criados': operacao.registros_sucesso,
                'produtos_atualizados': 0
            }
            
            operacao.resumo_operacao = json.dumps(resumo)
            self.db.commit()
            
            return resumo
            
        except Exception as e:
            operacao.status = StatusImportacao.ERRO
            operacao.fim_processamento = datetime.utcnow()
            operacao.log_detalhado = str(e)
            self.db.commit()
            raise HTTPException(status_code=500, detail=f"Erro durante importação: {str(e)}")

    # ==================== MÉTODOS DE EXPORTAÇÃO ====================
    
    async def preview_export(self, config: ConfiguracaoExportacao) -> PreviewExportacao:
        """Gerar preview da exportação"""
        # Query produtos globais (todos os produtos são globais agora)
        query = self.db.query(Produto).filter(
            Produto.status.in_([StatusProduto.ATIVO, StatusProduto.INATIVO])
        )
        
        # Aplicar filtros
        if config.filtros:
            query = self._apply_export_filters(query, config.filtros)
        
        # Contar registros
        total_registros = query.count()
        
        # Determinar campos incluídos
        campos_incluidos = self._get_export_fields(config.tipo_exportacao, config.campos_personalizados)
        
        # Obter primeiras linhas para preview
        produtos = query.limit(10).all()
        primeiras_linhas = [self._produto_to_dict(p, campos_incluidos) for p in produtos]
        
        # Estimar tamanho do arquivo
        tamanho_estimado = self._estimate_file_size(total_registros, len(campos_incluidos), config.formato)
        
        return PreviewExportacao(
            total_registros=total_registros,
            campos_incluidos=campos_incluidos,
            primeiras_linhas=primeiras_linhas,
            tamanho_estimado=tamanho_estimado
        )

    def _apply_export_filters(self, query, filtros: FiltroExportacao):
        """Aplicar filtros à query de exportação"""
        if filtros.categorias:
            query = query.filter(Produto.categoria.in_(filtros.categorias))
        
        if filtros.apenas_ativos:
            query = query.filter(Produto.status == StatusProduto.ATIVO)
        
        if filtros.apenas_com_estoque:
            query = query.filter(Produto.estoque_atual > 0)
        
        if filtros.preco_min is not None:
            query = query.filter(Produto.preco >= filtros.preco_min)
        
        if filtros.preco_max is not None:
            query = query.filter(Produto.preco <= filtros.preco_max)
        
        return query

    def _get_export_fields(self, tipo: TipoExportacao, campos_personalizados: Optional[List[str]]) -> List[str]:
        """Determinar campos a serem incluídos na exportação"""
        if campos_personalizados:
            return campos_personalizados
        
        field_sets = {
            TipoExportacao.ESTOQUE_COMPLETO: [
                'codigo_interno', 'nome', 'categoria', 'preco', 'estoque_atual',
                'estoque_minimo', 'marca', 'fornecedor', 'status'
            ],
            TipoExportacao.ESTOQUE_BAIXO: [
                'codigo_interno', 'nome', 'estoque_atual', 'estoque_minimo'
            ],
            TipoExportacao.LISTA_PRECOS: [
                'codigo_interno', 'nome', 'preco_custo', 'preco', 'margem_lucro'
            ],
            TipoExportacao.FISCAL: [
                'codigo_interno', 'nome', 'ncm', 'icms', 'ipi', 'preco'
            ]
        }
        
        return field_sets.get(tipo, field_sets[TipoExportacao.ESTOQUE_COMPLETO])

    def _produto_to_dict(self, produto: Produto, campos: List[str]) -> Dict[str, Any]:
        """Converter produto para dicionário com campos específicos"""
        data = {}
        for campo in campos:
            value = getattr(produto, campo, None)
            if value is not None:
                data[campo] = str(value) if not isinstance(value, (int, float, bool)) else value
            else:
                data[campo] = ''
        return data

    def _estimate_file_size(self, num_records: int, num_fields: int, formato: FormatoArquivo) -> str:
        """Estimar tamanho do arquivo"""
        # Estimativa básica baseada no formato
        bytes_per_record = {
            FormatoArquivo.CSV: num_fields * 20,  # ~20 bytes por campo
            FormatoArquivo.XLSX: num_fields * 30,  # ~30 bytes por campo
            FormatoArquivo.JSON: num_fields * 40,  # ~40 bytes por campo
            FormatoArquivo.PDF: num_fields * 50   # ~50 bytes por campo
        }
        
        total_bytes = num_records * bytes_per_record.get(formato, 30)
        
        if total_bytes < 1024:
            return f"{total_bytes} bytes"
        elif total_bytes < 1024 * 1024:
            return f"{total_bytes / 1024:.1f} KB"
        else:
            return f"{total_bytes / (1024 * 1024):.1f} MB"

    async def execute_export(self, config: ConfiguracaoExportacao, user_id: int) -> StreamingResponse:
        """Executar exportação"""
        # Criar registro da operação
        operacao = OperacaoImportExport(
            tipo_operacao=TipoOperacao.EXPORTACAO,
            nome_arquivo=f"export_{config.tipo_exportacao}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{config.formato}",
            formato_arquivo=config.formato,
            usuario_id=user_id,
            evento_id=None,  # Produtos são globais
            status=StatusImportacao.PROCESSANDO,
            filtros_aplicados=json.dumps(config.filtros.dict() if config.filtros else {}),
            campos_personalizados=json.dumps(config.campos_personalizados or [])
        )
        
        self.db.add(operacao)
        self.db.commit()
        
        try:
            # Buscar dados - todos os produtos são globais agora
            query = self.db.query(Produto).filter(
                Produto.status.in_([StatusProduto.ATIVO, StatusProduto.INATIVO])
            )
            
            if config.filtros:
                query = self._apply_export_filters(query, config.filtros)
            
            produtos = query.all()
            operacao.total_registros = len(produtos)
            
            # Gerar arquivo
            campos = self._get_export_fields(config.tipo_exportacao, config.campos_personalizados)
            
            if config.formato == FormatoArquivo.CSV:
                content = self._generate_csv(produtos, campos, config)
                media_type = "text/csv"
            elif config.formato == FormatoArquivo.XLSX:
                content = self._generate_excel(produtos, campos, config)
                media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            elif config.formato == FormatoArquivo.JSON:
                content = self._generate_json(produtos, campos)
                media_type = "application/json"
            elif config.formato == FormatoArquivo.PDF:
                content = self._generate_pdf(produtos, campos, config)
                media_type = "application/pdf"
            else:
                raise ValueError(f"Formato {config.formato} não suportado")
            
            # Atualizar operação
            operacao.status = StatusImportacao.CONCLUIDA
            operacao.registros_processados = len(produtos)
            operacao.registros_sucesso = len(produtos)
            operacao.fim_processamento = datetime.utcnow()
            self.db.commit()
            
            # Retornar arquivo
            return StreamingResponse(
                io.BytesIO(content),
                media_type=media_type,
                headers={"Content-Disposition": f"attachment; filename={operacao.nome_arquivo}"}
            )
            
        except Exception as e:
            operacao.status = StatusImportacao.ERRO
            operacao.log_detalhado = str(e)
            operacao.fim_processamento = datetime.utcnow()
            self.db.commit()
            raise HTTPException(status_code=500, detail=f"Erro durante exportação: {str(e)}")

    def _generate_csv(self, produtos: List[Produto], campos: List[str], config: ConfiguracaoExportacao) -> bytes:
        """Gerar arquivo CSV"""
        output = io.StringIO()
        writer = csv.DictWriter(
            output, 
            fieldnames=campos, 
            delimiter=config.separador_csv or ',',
            quoting=csv.QUOTE_MINIMAL
        )
        
        if config.incluir_cabecalho:
            writer.writeheader()
        
        for produto in produtos:
            row = self._produto_to_dict(produto, campos)
            writer.writerow(row)
        
        return output.getvalue().encode(config.encoding or 'utf-8')

    def _generate_excel(self, produtos: List[Produto], campos: List[str], config: ConfiguracaoExportacao) -> bytes:
        """Gerar arquivo Excel"""
        # Preparar dados
        data = []
        if config.incluir_cabecalho:
            data.append(campos)
        
        for produto in produtos:
            row = [self._produto_to_dict(produto, campos).get(campo, '') for campo in campos]
            data.append(row)
        
        # Criar Excel
        df = pd.DataFrame(data[1:] if config.incluir_cabecalho else data, 
                         columns=data[0] if config.incluir_cabecalho else None)
        
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Produtos')
        
        return output.getvalue()

    def _generate_json(self, produtos: List[Produto], campos: List[str]) -> bytes:
        """Gerar arquivo JSON"""
        data = []
        for produto in produtos:
            data.append(self._produto_to_dict(produto, campos))
        
        return json.dumps(data, ensure_ascii=False, indent=2).encode('utf-8')

    def _generate_pdf(self, produtos: List[Produto], campos: List[str], config: ConfiguracaoExportacao) -> bytes:
        """Gerar arquivo PDF"""
        output = io.BytesIO()
        doc = SimpleDocTemplate(output, pagesize=A4)
        
        # Estilos
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            spaceAfter=30,
            alignment=1  # Centralizado
        )
        
        # Conteúdo
        story = []
        
        # Título
        title = Paragraph("Relatório de Produtos", title_style)
        story.append(title)
        story.append(Spacer(1, 20))
        
        # Tabela
        table_data = []
        
        # Cabeçalho
        if config.incluir_cabecalho:
            table_data.append(campos)
        
        # Dados (limitando a 50 registros para PDF)
        for produto in produtos[:50]:
            row = [str(self._produto_to_dict(produto, campos).get(campo, '')) for campo in campos]
            table_data.append(row)
        
        # Criar tabela
        table = Table(table_data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(table)
        
        # Construir PDF
        doc.build(story)
        
        return output.getvalue()

    # ==================== MÉTODOS DE RELATÓRIOS ====================
    
    def get_dashboard_stats(self) -> Dict[str, Any]:
        """Obter estatísticas do dashboard"""
        today = datetime.utcnow().date()
        
        # Operações hoje (globais, não por evento)
        importacoes_hoje = self.db.query(OperacaoImportExport).filter(
            and_(
                func.date(OperacaoImportExport.criado_em) == today,
                OperacaoImportExport.tipo_operacao == TipoOperacao.IMPORTACAO
            )
        ).count()
        
        # Produtos atualizados hoje (globais)
        produtos_atualizados = self.db.query(Produto).filter(
            func.date(Produto.atualizado_em) == today
        ).count()
        
        # Último import com erros (global)
        ultimo_import = self.db.query(OperacaoImportExport).filter(
            OperacaoImportExport.tipo_operacao == TipoOperacao.IMPORTACAO
        ).order_by(OperacaoImportExport.criado_em.desc()).first()
        
        ultimo_import_erros = ultimo_import.registros_erro if ultimo_import else 0
        
        # Tempo médio de processamento (global)
        operacoes_recentes = self.db.query(OperacaoImportExport).filter(
            and_(
                OperacaoImportExport.status == StatusImportacao.CONCLUIDA,
                OperacaoImportExport.inicio_processamento.isnot(None),
                OperacaoImportExport.fim_processamento.isnot(None)
            )
        ).order_by(OperacaoImportExport.criado_em.desc()).limit(10).all()
        
        tempos = []
        for op in operacoes_recentes:
            if op.inicio_processamento and op.fim_processamento:
                tempo = (op.fim_processamento - op.inicio_processamento).total_seconds()
                tempos.append(tempo)
        
        tempo_medio = sum(tempos) / len(tempos) if tempos else 0
        
        return {
            'importacoes_hoje': importacoes_hoje,
            'produtos_atualizados': produtos_atualizados,
            'ultimo_import_erros': ultimo_import_erros,
            'tempo_medio_processo': tempo_medio
        }

    def get_recent_operations(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Obter operações recentes (globais)"""
        operacoes = self.db.query(OperacaoImportExport).order_by(
            OperacaoImportExport.criado_em.desc()
        ).limit(limit).all()
        
        return [
            {
                'id': op.id,
                'tipo': op.tipo_operacao.value,
                'arquivo': op.nome_arquivo,
                'status': op.status.value,
                'registros': op.total_registros,
                'data': op.criado_em.isoformat(),
                'sucesso': op.registros_sucesso,
                'erros': op.registros_erro
            }
            for op in operacoes
        ]