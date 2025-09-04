import json
import asyncio
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from fastapi import HTTPException, status

from ..models import (
    Impressora, PrintJob, PrintTemplate, VendaPDV, Comanda,
    TipoImpressora, StatusImpressora, StatusPrintJob, TipoPrintJob
)
from ..schemas_printer import (
    PrintJobCreate, ImprimirReciboRequest, ImprimirPedidoRequest
)

class PrinterService:
    def __init__(self, db: Session):
        self.db = db
    
    async def criar_job_recibo_caixa(
        self, 
        request: ImprimirReciboRequest, 
        cpf_operador: str,
        usuario_id: int,
        evento_id: int,
        ip_cliente: Optional[str] = None
    ) -> PrintJob:
        """Criar job de impressão para recibo de caixa"""
        
        # Buscar venda
        venda = self.db.query(VendaPDV).filter(VendaPDV.id == request.venda_pdv_id).first()
        if not venda:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Venda não encontrada"
            )
        
        # Determinar impressora (automático ou manual)
        impressora = await self._determinar_impressora(
            evento_id=evento_id,
            tipo_impressora=TipoImpressora.CAIXA,
            impressora_id_preferida=request.impressora_id
        )
        
        # Buscar template padrão
        template = self._buscar_template(evento_id, TipoPrintJob.RECIBO_CAIXA)
        
        # Preparar payload para o template
        payload = {
            "venda": {
                "numero": venda.numero_venda,
                "valor_total": float(venda.valor_total),
                "valor_desconto": float(venda.valor_desconto),
                "valor_final": float(venda.valor_final),
                "tipo_pagamento": venda.tipo_pagamento.value,
                "data_venda": venda.criado_em.isoformat(),
                "cpf_cliente": venda.cpf_cliente,
                "nome_cliente": venda.nome_cliente
            },
            "itens": [
                {
                    "nome": item.produto_nome or "Produto",
                    "quantidade": item.quantidade,
                    "preco_unitario": float(item.preco_unitario),
                    "preco_total": float(item.preco_total),
                    "observacoes": item.observacoes
                }
                for item in venda.itens
            ],
            "pagamentos": [
                {
                    "tipo": pagamento.tipo_pagamento.value,
                    "valor": float(pagamento.valor),
                    "codigo_transacao": pagamento.codigo_transacao
                }
                for pagamento in venda.pagamentos
            ],
            "configuracoes": {
                "abrir_gaveta": request.abrir_gaveta,
                "corte_automatico": True,
                "densidade": impressora.densidade
            },
            "empresa": {
                "nome": "Nome da Empresa",  # Buscar dos dados do evento
                "cnpj": "00.000.000/0001-00",
                "endereco": "Endereço da empresa"
            }
        }
        
        # Criar job
        job = PrintJob(
            impressora_id=impressora.id,
            template_id=template.id if template else None,
            tipo=TipoPrintJob.RECIBO_CAIXA,
            prioridade=2,  # Alta prioridade para recibos
            payload=json.dumps(payload),
            venda_pdv_id=request.venda_pdv_id,
            evento_id=evento_id,
            cpf_operador=cpf_operador,
            usuario_id=usuario_id,
            ip_cliente=ip_cliente
        )
        
        self.db.add(job)
        self.db.commit()
        self.db.refresh(job)
        
        # Enviar para fila de processamento
        await self._enviar_para_fila(job.id)
        
        return job
    
    async def criar_job_pedido_cozinha(
        self,
        request: ImprimirPedidoRequest,
        cpf_operador: str,
        usuario_id: int,
        evento_id: int,
        ip_cliente: Optional[str] = None
    ) -> List[PrintJob]:
        """Criar jobs de impressão para pedidos (roteamento inteligente por estação)"""
        
        jobs_criados = []
        
        # Determinar dados do pedido
        if request.venda_pdv_id:
            venda = self.db.query(VendaPDV).filter(VendaPDV.id == request.venda_pdv_id).first()
            if not venda:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Venda não encontrada"
                )
            itens_pedido = venda.itens
        elif request.comanda_id:
            # Lógica para itens da comanda (implementar conforme necessário)
            itens_pedido = []
        else:
            itens_pedido = request.itens_personalizados or []
        
        # Agrupar itens por estação baseado em tags/categoria
        itens_por_estacao = await self._agrupar_itens_por_estacao(itens_pedido)
        
        # Criar um job para cada estação
        for tipo_estacao, itens in itens_por_estacao.items():
            if not itens:
                continue
                
            # Determinar impressora da estação
            impressora = await self._determinar_impressora(
                evento_id=evento_id,
                tipo_impressora=tipo_estacao
            )
            
            if not impressora:
                continue  # Pular se não há impressora configurada para a estação
            
            # Buscar template específico da estação
            tipo_job = self._mapear_estacao_para_tipo_job(tipo_estacao)
            template = self._buscar_template(evento_id, tipo_job)
            
            # Payload específico da estação
            payload = {
                "pedido": {
                    "numero": venda.numero_venda if request.venda_pdv_id else f"COMANDA-{request.comanda_id}",
                    "mesa": request.mesa_numero,
                    "observacoes": request.observacoes,
                    "horario": datetime.now().isoformat(),
                    "estacao": tipo_estacao.value
                },
                "itens": [
                    {
                        "nome": item.produto_nome if hasattr(item, 'produto_nome') else item.get('nome'),
                        "quantidade": item.quantidade if hasattr(item, 'quantidade') else item.get('quantidade'),
                        "observacoes": item.observacoes if hasattr(item, 'observacoes') else item.get('observacoes', '')
                    }
                    for item in itens
                ],
                "configuracoes": {
                    "corte_automatico": True,
                    "densidade": impressora.densidade,
                    "som_aviso": True
                }
            }
            
            # Criar job
            job = PrintJob(
                impressora_id=impressora.id,
                template_id=template.id if template else None,
                tipo=tipo_job,
                prioridade=1,  # Prioridade normal para pedidos
                payload=json.dumps(payload),
                venda_pdv_id=request.venda_pdv_id,
                comanda_id=request.comanda_id,
                evento_id=evento_id,
                cpf_operador=cpf_operador,
                usuario_id=usuario_id,
                ip_cliente=ip_cliente
            )
            
            self.db.add(job)
            jobs_criados.append(job)
        
        if jobs_criados:
            self.db.commit()
            
            # Enviar todos os jobs para processamento
            for job in jobs_criados:
                self.db.refresh(job)
                await self._enviar_para_fila(job.id)
        
        return jobs_criados
    
    async def _determinar_impressora(
        self,
        evento_id: int,
        tipo_impressora: TipoImpressora,
        impressora_id_preferida: Optional[str] = None
    ) -> Optional[Impressora]:
        """Determinar qual impressora usar (com fallback)"""
        
        # Se especificada, tentar usar a impressora preferida
        if impressora_id_preferida:
            impressora = self.db.query(Impressora).filter(
                and_(
                    Impressora.id == impressora_id_preferida,
                    Impressora.evento_id == evento_id,
                    Impressora.ativo == True
                )
            ).first()
            
            if impressora and impressora.status == StatusImpressora.ONLINE:
                return impressora
        
        # Buscar impressora disponível do tipo solicitado
        impressoras = self.db.query(Impressora).filter(
            and_(
                Impressora.evento_id == evento_id,
                Impressora.tipo == tipo_impressora,
                Impressora.ativo == True,
                Impressora.status == StatusImpressora.ONLINE
            )
        ).order_by(Impressora.ultimo_heartbeat.desc()).all()
        
        if impressoras:
            return impressoras[0]  # Primeira impressora online
        
        # Fallback: buscar impressora backup
        impressoras_backup = self.db.query(Impressora).filter(
            and_(
                Impressora.evento_id == evento_id,
                Impressora.tipo == tipo_impressora,
                Impressora.ativo == True
            )
        ).all()
        
        for impressora in impressoras_backup:
            if impressora.impressora_backup_id:
                backup = self.db.query(Impressora).filter(
                    Impressora.id == impressora.impressora_backup_id
                ).first()
                if backup and backup.status == StatusImpressora.ONLINE:
                    return backup
        
        return None
    
    def _buscar_template(self, evento_id: int, tipo_job: TipoPrintJob) -> Optional[PrintTemplate]:
        """Buscar template padrão para o tipo de job"""
        return self.db.query(PrintTemplate).filter(
            and_(
                PrintTemplate.evento_id == evento_id,
                PrintTemplate.tipo_job == tipo_job,
                PrintTemplate.ativo == True,
                PrintTemplate.padrao == True
            )
        ).first()
    
    async def _agrupar_itens_por_estacao(self, itens: List) -> Dict[TipoImpressora, List]:
        """Agrupar itens por estação baseado em tags/categoria do produto"""
        
        grupos = {
            TipoImpressora.COZINHA: [],
            TipoImpressora.BAR: [],
            TipoImpressora.SOBREMESA: []
        }
        
        for item in itens:
            # Lógica de classificação (implementar conforme regras de negócio)
            categoria = item.produto.categoria if hasattr(item, 'produto') else item.get('categoria', 'cozinha')
            
            if categoria.lower() in ['bebida', 'drink', 'cerveja', 'refrigerante']:
                grupos[TipoImpressora.BAR].append(item)
            elif categoria.lower() in ['sobremesa', 'doce', 'açaí', 'sorvete']:
                grupos[TipoImpressora.SOBREMESA].append(item)
            else:
                grupos[TipoImpressora.COZINHA].append(item)
        
        return grupos
    
    def _mapear_estacao_para_tipo_job(self, tipo_impressora: TipoImpressora) -> TipoPrintJob:
        """Mapear tipo de impressora para tipo de job"""
        mapeamento = {
            TipoImpressora.COZINHA: TipoPrintJob.PEDIDO_COZINHA,
            TipoImpressora.BAR: TipoPrintJob.PEDIDO_BAR,
            TipoImpressora.SOBREMESA: TipoPrintJob.PEDIDO_COZINHA,  # Usar mesmo template
            TipoImpressora.CAIXA: TipoPrintJob.RECIBO_CAIXA
        }
        return mapeamento.get(tipo_impressora, TipoPrintJob.PEDIDO_COZINHA)
    
    async def _enviar_para_fila(self, job_id: str):
        """Enviar job para fila de processamento (implementar com Redis/Celery)"""
        # Por enquanto, apenas log
        print(f"Job {job_id} enviado para fila de impressão")
        # TODO: Implementar envio para Redis/Celery ou processamento direto
    
    def listar_impressoras_evento(self, evento_id: int) -> List[Impressora]:
        """Listar impressoras de um evento"""
        return self.db.query(Impressora).filter(
            and_(
                Impressora.evento_id == evento_id,
                Impressora.ativo == True
            )
        ).all()
    
    def obter_status_fila(self, evento_id: int) -> Dict[str, Any]:
        """Obter status da fila de impressão"""
        impressoras = self.listar_impressoras_evento(evento_id)
        
        total_online = sum(1 for imp in impressoras if imp.status == StatusImpressora.ONLINE)
        total_offline = len(impressoras) - total_online
        
        jobs_pendentes = self.db.query(PrintJob).filter(
            and_(
                PrintJob.evento_id == evento_id,
                PrintJob.status.in_([StatusPrintJob.QUEUED, StatusPrintJob.PRINTING])
            )
        ).count()
        
        jobs_erro = self.db.query(PrintJob).filter(
            and_(
                PrintJob.evento_id == evento_id,
                PrintJob.status == StatusPrintJob.ERROR,
                PrintJob.criado_em >= datetime.now() - timedelta(hours=24)
            )
        ).count()
        
        return {
            "impressoras_online": total_online,
            "impressoras_offline": total_offline,
            "jobs_pendentes": jobs_pendentes,
            "jobs_erro": jobs_erro,
            "ultima_atualizacao": datetime.now()
        }
