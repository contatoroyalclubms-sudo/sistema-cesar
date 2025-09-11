"""
📝 SISTEMA DE AUDITORIA E LOGS ESTRUTURADOS
Rastreamento completo de todas as operações do sistema
Última atualização: 05/01/2025
"""

import logging
import json
import traceback
from typing import Optional, Dict, Any, List
from datetime import datetime, timezone
from enum import Enum
from sqlalchemy import Column, Integer, String, DateTime, Text, JSON, ForeignKey, Index
from sqlalchemy.orm import Session, relationship
from sqlalchemy.ext.declarative import declarative_base
from fastapi import Request, Response
from contextlib import contextmanager
import hashlib
import uuid
import os

# Import cache se disponível
try:
    from app.cache import cache
    CACHE_ENABLED = True
except ImportError:
    CACHE_ENABLED = False

logger = logging.getLogger(__name__)

# ===== MODELOS DE AUDITORIA =====

Base = declarative_base()

class AuditAction(Enum):
    """Tipos de ações auditáveis"""
    CREATE = "CREATE"
    READ = "READ"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    LOGIN = "LOGIN"
    LOGOUT = "LOGOUT"
    LOGIN_FAILED = "LOGIN_FAILED"
    PERMISSION_DENIED = "PERMISSION_DENIED"
    EXPORT = "EXPORT"
    IMPORT = "IMPORT"
    PAYMENT = "PAYMENT"
    CHECKIN = "CHECKIN"
    ERROR = "ERROR"
    WARNING = "WARNING"
    INFO = "INFO"

class AuditLog(Base):
    """Modelo de log de auditoria"""
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Identificação
    audit_id = Column(String(36), unique=True, index=True, default=lambda: str(uuid.uuid4()))
    timestamp = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)
    
    # Usuário
    user_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True, index=True)
    user_cpf = Column(String(14), index=True, nullable=True)
    user_name = Column(String(255), nullable=True)
    user_role = Column(String(50), nullable=True)
    
    # Ação
    action = Column(String(50), index=True, nullable=False)
    entity_type = Column(String(100), index=True, nullable=True)  # Ex: "evento", "usuario", "venda"
    entity_id = Column(String(100), index=True, nullable=True)
    entity_name = Column(String(255), nullable=True)
    
    # Detalhes
    description = Column(Text, nullable=True)
    old_values = Column(JSON, nullable=True)
    new_values = Column(JSON, nullable=True)
    changes = Column(JSON, nullable=True)  # Diferença entre old e new
    
    # Request info
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)
    method = Column(String(10), nullable=True)
    path = Column(String(500), nullable=True)
    query_params = Column(JSON, nullable=True)
    request_id = Column(String(36), index=True, nullable=True)
    
    # Response info
    status_code = Column(Integer, nullable=True)
    response_time_ms = Column(Integer, nullable=True)
    error_message = Column(Text, nullable=True)
    error_traceback = Column(Text, nullable=True)
    
    # Metadados
    session_id = Column(String(100), index=True, nullable=True)
    correlation_id = Column(String(36), index=True, nullable=True)
    tags = Column(JSON, nullable=True)  # Tags customizadas
    metadata = Column(JSON, nullable=True)  # Dados extras
    
    # Compliance
    data_classification = Column(String(50), nullable=True)  # "PUBLIC", "INTERNAL", "CONFIDENTIAL", "RESTRICTED"
    retention_days = Column(Integer, default=365)
    
    # Índices compostos para queries comuns
    __table_args__ = (
        Index('idx_user_action', 'user_id', 'action'),
        Index('idx_entity', 'entity_type', 'entity_id'),
        Index('idx_timestamp_action', 'timestamp', 'action'),
        Index('idx_session', 'session_id', 'timestamp'),
    )

class AuditEvent(Base):
    """Eventos de negócio auditáveis"""
    __tablename__ = "audit_events"
    
    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(String(36), unique=True, index=True, default=lambda: str(uuid.uuid4()))
    timestamp = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)
    
    event_type = Column(String(100), index=True, nullable=False)  # Ex: "venda_realizada", "checkin_confirmado"
    event_data = Column(JSON, nullable=False)
    
    # Relacionamentos
    user_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True)
    evento_id = Column(Integer, ForeignKey("eventos.id"), nullable=True)
    
    # Contexto
    source = Column(String(100), nullable=True)  # Sistema/módulo que gerou
    severity = Column(String(20), default="INFO")  # INFO, WARNING, ERROR, CRITICAL
    
    # Processamento
    processed = Column(DateTime(timezone=True), nullable=True)
    processed_by = Column(String(100), nullable=True)
    
    __table_args__ = (
        Index('idx_event_type_timestamp', 'event_type', 'timestamp'),
    )

# ===== SERVIÇO DE AUDITORIA =====

class AuditService:
    """Serviço centralizado de auditoria"""
    
    def __init__(self):
        self.enabled = os.getenv("AUDIT_ENABLED", "true").lower() == "true"
        self.async_mode = os.getenv("AUDIT_ASYNC", "false").lower() == "true"
        self.sensitive_fields = [
            "senha", "password", "token", "secret", "key",
            "cvv", "card_number", "cpf", "rg"
        ]
    
    def log_action(
        self,
        db: Session,
        action: AuditAction,
        user: Optional[Dict[str, Any]] = None,
        entity_type: Optional[str] = None,
        entity_id: Optional[Any] = None,
        entity_name: Optional[str] = None,
        old_values: Optional[Dict[str, Any]] = None,
        new_values: Optional[Dict[str, Any]] = None,
        description: Optional[str] = None,
        request: Optional[Request] = None,
        response: Optional[Response] = None,
        error: Optional[Exception] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[AuditLog]:
        """
        Registra uma ação no log de auditoria
        
        Args:
            db: Sessão do banco
            action: Tipo de ação
            user: Dados do usuário
            entity_type: Tipo da entidade (ex: "evento", "usuario")
            entity_id: ID da entidade
            entity_name: Nome descritivo da entidade
            old_values: Valores anteriores (para UPDATE)
            new_values: Novos valores (para CREATE/UPDATE)
            description: Descrição da ação
            request: Request do FastAPI
            response: Response do FastAPI
            error: Exceção se houver erro
            metadata: Metadados adicionais
        
        Returns:
            AuditLog criado ou None se desabilitado
        """
        if not self.enabled:
            return None
        
        try:
            # Sanitizar dados sensíveis
            if old_values:
                old_values = self._sanitize_data(old_values)
            if new_values:
                new_values = self._sanitize_data(new_values)
            
            # Calcular mudanças
            changes = None
            if old_values and new_values:
                changes = self._calculate_changes(old_values, new_values)
            
            # Criar log
            audit_log = AuditLog(
                action=action.value,
                entity_type=entity_type,
                entity_id=str(entity_id) if entity_id else None,
                entity_name=entity_name,
                old_values=old_values,
                new_values=new_values,
                changes=changes,
                description=description,
                metadata=metadata
            )
            
            # Adicionar dados do usuário
            if user:
                audit_log.user_id = user.get("id")
                audit_log.user_cpf = user.get("cpf")
                audit_log.user_name = user.get("nome")
                audit_log.user_role = user.get("role")
            
            # Adicionar dados da request
            if request:
                audit_log.ip_address = self._get_client_ip(request)
                audit_log.user_agent = request.headers.get("User-Agent", "")[:500]
                audit_log.method = request.method
                audit_log.path = str(request.url.path)
                audit_log.query_params = dict(request.query_params) if request.query_params else None
                audit_log.request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
                audit_log.session_id = request.headers.get("X-Session-ID")
            
            # Adicionar dados da response
            if response:
                audit_log.status_code = response.status_code
            
            # Adicionar dados de erro
            if error:
                audit_log.error_message = str(error)
                audit_log.error_traceback = traceback.format_exc()
                if not audit_log.status_code:
                    audit_log.status_code = 500
            
            # Classificar dados
            audit_log.data_classification = self._classify_data(entity_type, action)
            
            # Salvar no banco
            db.add(audit_log)
            
            if not self.async_mode:
                db.commit()
            
            # Log também no arquivo
            self._log_to_file(audit_log)
            
            return audit_log
            
        except Exception as e:
            logger.error(f"Erro ao criar log de auditoria: {e}")
            return None
    
    def log_event(
        self,
        db: Session,
        event_type: str,
        event_data: Dict[str, Any],
        user_id: Optional[int] = None,
        evento_id: Optional[int] = None,
        source: Optional[str] = None,
        severity: str = "INFO"
    ) -> Optional[AuditEvent]:
        """
        Registra um evento de negócio
        
        Args:
            db: Sessão do banco
            event_type: Tipo do evento
            event_data: Dados do evento
            user_id: ID do usuário relacionado
            evento_id: ID do evento relacionado
            source: Sistema/módulo fonte
            severity: Severidade (INFO, WARNING, ERROR, CRITICAL)
        
        Returns:
            AuditEvent criado
        """
        if not self.enabled:
            return None
        
        try:
            # Sanitizar dados
            event_data = self._sanitize_data(event_data)
            
            # Criar evento
            audit_event = AuditEvent(
                event_type=event_type,
                event_data=event_data,
                user_id=user_id,
                evento_id=evento_id,
                source=source or "system",
                severity=severity
            )
            
            db.add(audit_event)
            
            if not self.async_mode:
                db.commit()
            
            # Notificar se crítico
            if severity == "CRITICAL":
                self._notify_critical_event(audit_event)
            
            return audit_event
            
        except Exception as e:
            logger.error(f"Erro ao criar evento de auditoria: {e}")
            return None
    
    def _sanitize_data(self, data: Any) -> Any:
        """Remove dados sensíveis"""
        if isinstance(data, dict):
            sanitized = {}
            for key, value in data.items():
                if any(field in key.lower() for field in self.sensitive_fields):
                    sanitized[key] = "***REDACTED***"
                else:
                    sanitized[key] = self._sanitize_data(value)
            return sanitized
        elif isinstance(data, list):
            return [self._sanitize_data(item) for item in data]
        else:
            return data
    
    def _calculate_changes(self, old: Dict, new: Dict) -> Dict:
        """Calcula diferenças entre valores antigos e novos"""
        changes = {}
        
        # Campos removidos
        for key in old:
            if key not in new:
                changes[key] = {"old": old[key], "new": None, "action": "removed"}
        
        # Campos adicionados ou modificados
        for key in new:
            if key not in old:
                changes[key] = {"old": None, "new": new[key], "action": "added"}
            elif old[key] != new[key]:
                changes[key] = {"old": old[key], "new": new[key], "action": "modified"}
        
        return changes if changes else None
    
    def _get_client_ip(self, request: Request) -> str:
        """Obtém IP real do cliente"""
        # Verificar headers de proxy
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        # IP direto
        if request.client:
            return request.client.host
        
        return "unknown"
    
    def _classify_data(self, entity_type: Optional[str], action: AuditAction) -> str:
        """Classifica dados para compliance"""
        # Dados sensíveis
        if entity_type in ["usuario", "pagamento", "cartao"]:
            return "CONFIDENTIAL"
        
        # Ações críticas
        if action in [AuditAction.DELETE, AuditAction.PAYMENT]:
            return "RESTRICTED"
        
        # Dados internos
        if entity_type in ["evento", "venda", "checkin"]:
            return "INTERNAL"
        
        return "PUBLIC"
    
    def _log_to_file(self, audit_log: AuditLog):
        """Grava log em arquivo para backup"""
        try:
            log_entry = {
                "timestamp": audit_log.timestamp.isoformat() if audit_log.timestamp else None,
                "audit_id": audit_log.audit_id,
                "user": f"{audit_log.user_name} ({audit_log.user_cpf})" if audit_log.user_name else "anonymous",
                "action": audit_log.action,
                "entity": f"{audit_log.entity_type}:{audit_log.entity_id}" if audit_log.entity_type else None,
                "description": audit_log.description,
                "ip": audit_log.ip_address,
                "path": audit_log.path,
                "status": audit_log.status_code
            }
            
            # Log estruturado
            logger.info(f"AUDIT: {json.dumps(log_entry, default=str)}")
            
        except Exception as e:
            logger.error(f"Erro ao gravar log em arquivo: {e}")
    
    def _notify_critical_event(self, event: AuditEvent):
        """Notifica eventos críticos"""
        try:
            logger.critical(f"CRITICAL EVENT: {event.event_type} - {json.dumps(event.event_data, default=str)}")
            
            # Aqui você pode adicionar:
            # - Envio de email
            # - Notificação Slack/Discord
            # - SMS para administradores
            # - Criação de ticket
            
        except Exception as e:
            logger.error(f"Erro ao notificar evento crítico: {e}")

# ===== CONSULTAS DE AUDITORIA =====

class AuditQuery:
    """Consultas otimizadas de auditoria"""
    
    @staticmethod
    def get_user_actions(
        db: Session,
        user_id: int,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        action: Optional[AuditAction] = None,
        limit: int = 100
    ) -> List[AuditLog]:
        """Busca ações de um usuário"""
        query = db.query(AuditLog).filter(AuditLog.user_id == user_id)
        
        if start_date:
            query = query.filter(AuditLog.timestamp >= start_date)
        if end_date:
            query = query.filter(AuditLog.timestamp <= end_date)
        if action:
            query = query.filter(AuditLog.action == action.value)
        
        return query.order_by(AuditLog.timestamp.desc()).limit(limit).all()
    
    @staticmethod
    def get_entity_history(
        db: Session,
        entity_type: str,
        entity_id: Any,
        limit: int = 50
    ) -> List[AuditLog]:
        """Busca histórico de uma entidade"""
        return db.query(AuditLog).filter(
            AuditLog.entity_type == entity_type,
            AuditLog.entity_id == str(entity_id)
        ).order_by(AuditLog.timestamp.desc()).limit(limit).all()
    
    @staticmethod
    def get_failed_logins(
        db: Session,
        hours: int = 24,
        min_attempts: int = 3
    ) -> Dict[str, int]:
        """Busca tentativas de login falhas"""
        cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
        
        results = db.query(
            AuditLog.user_cpf,
            func.count(AuditLog.id).label("attempts")
        ).filter(
            AuditLog.action == AuditAction.LOGIN_FAILED.value,
            AuditLog.timestamp >= cutoff
        ).group_by(
            AuditLog.user_cpf
        ).having(
            func.count(AuditLog.id) >= min_attempts
        ).all()
        
        return {cpf: attempts for cpf, attempts in results}
    
    @staticmethod
    def get_suspicious_activity(
        db: Session,
        hours: int = 1
    ) -> List[Dict[str, Any]]:
        """Detecta atividades suspeitas"""
        cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
        suspicious = []
        
        # Múltiplos IPs para mesmo usuário
        ip_changes = db.query(
            AuditLog.user_id,
            func.count(func.distinct(AuditLog.ip_address)).label("ip_count")
        ).filter(
            AuditLog.timestamp >= cutoff,
            AuditLog.user_id.isnot(None)
        ).group_by(
            AuditLog.user_id
        ).having(
            func.count(func.distinct(AuditLog.ip_address)) > 3
        ).all()
        
        for user_id, ip_count in ip_changes:
            suspicious.append({
                "type": "multiple_ips",
                "user_id": user_id,
                "ip_count": ip_count,
                "severity": "WARNING"
            })
        
        # Muitas ações de DELETE
        delete_actions = db.query(
            AuditLog.user_id,
            func.count(AuditLog.id).label("delete_count")
        ).filter(
            AuditLog.action == AuditAction.DELETE.value,
            AuditLog.timestamp >= cutoff
        ).group_by(
            AuditLog.user_id
        ).having(
            func.count(AuditLog.id) > 10
        ).all()
        
        for user_id, delete_count in delete_actions:
            suspicious.append({
                "type": "excessive_deletes",
                "user_id": user_id,
                "delete_count": delete_count,
                "severity": "HIGH"
            })
        
        return suspicious

# ===== MIDDLEWARE DE AUDITORIA =====

class AuditMiddleware:
    """Middleware para auditoria automática de requests"""
    
    def __init__(self, app):
        self.app = app
        self.service = AuditService()
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        request = Request(scope, receive=receive)
        start_time = datetime.now(timezone.utc)
        
        # Gerar request ID
        request_id = str(uuid.uuid4())
        
        # Log de início
        logger.debug(f"Request {request_id}: {request.method} {request.url.path}")
        
        # Interceptar response
        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                # Calcular tempo de resposta
                duration = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
                
                # Log de resposta
                status = message.get("status", 0)
                logger.debug(f"Response {request_id}: {status} in {duration:.2f}ms")
                
                # Adicionar header com request ID
                headers = dict(message.get("headers", []))
                headers[b"x-request-id"] = request_id.encode()
                message["headers"] = list(headers.items())
            
            await send(message)
        
        try:
            await self.app(scope, receive, send_wrapper)
        except Exception as e:
            # Log de erro
            logger.error(f"Error in request {request_id}: {e}")
            raise

# ===== DECORATORS PARA AUDITORIA =====

def audit_action(
    action: AuditAction,
    entity_type: Optional[str] = None,
    description: Optional[str] = None
):
    """
    Decorator para auditar ações automaticamente
    
    Exemplo:
        @audit_action(AuditAction.CREATE, "evento", "Criação de novo evento")
        async def criar_evento(...):
            ...
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Extrair informações dos argumentos
            request = None
            db = None
            user = None
            
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                elif isinstance(arg, Session):
                    db = arg
                elif isinstance(arg, dict) and "id" in arg and "cpf" in arg:
                    user = arg
            
            for key, value in kwargs.items():
                if key == "request":
                    request = value
                elif key == "db":
                    db = value
                elif key == "current_user":
                    user = value
            
            # Executar função
            result = None
            error = None
            try:
                result = await func(*args, **kwargs)
                
                # Extrair entity_id do resultado se possível
                entity_id = None
                if hasattr(result, "id"):
                    entity_id = result.id
                elif isinstance(result, dict) and "id" in result:
                    entity_id = result["id"]
                
                # Registrar auditoria de sucesso
                if db:
                    service = AuditService()
                    service.log_action(
                        db=db,
                        action=action,
                        user=user,
                        entity_type=entity_type,
                        entity_id=entity_id,
                        description=description or f"{action.value} {entity_type}",
                        request=request,
                        new_values=result if isinstance(result, dict) else None
                    )
                
                return result
                
            except Exception as e:
                error = e
                
                # Registrar auditoria de erro
                if db:
                    service = AuditService()
                    service.log_action(
                        db=db,
                        action=AuditAction.ERROR,
                        user=user,
                        entity_type=entity_type,
                        description=f"Erro em {action.value} {entity_type}: {str(e)}",
                        request=request,
                        error=e
                    )
                
                raise
        
        return wrapper
    return decorator

# ===== LIMPEZA DE LOGS ANTIGOS =====

def cleanup_old_logs(db: Session, days: int = 365):
    """
    Remove logs antigos baseado na política de retenção
    
    Args:
        db: Sessão do banco
        days: Dias de retenção padrão
    """
    try:
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        
        # Deletar logs antigos respeitando retention_days
        deleted = db.query(AuditLog).filter(
            or_(
                and_(
                    AuditLog.retention_days.isnot(None),
                    AuditLog.timestamp < datetime.now(timezone.utc) - timedelta(days=AuditLog.retention_days)
                ),
                and_(
                    AuditLog.retention_days.is_(None),
                    AuditLog.timestamp < cutoff
                )
            )
        ).delete()
        
        db.commit()
        
        logger.info(f"Removidos {deleted} logs de auditoria antigos")
        
        return deleted
        
    except Exception as e:
        logger.error(f"Erro ao limpar logs antigos: {e}")
        db.rollback()
        return 0

# ===== RELATÓRIOS DE AUDITORIA =====

class AuditReports:
    """Geração de relatórios de auditoria"""
    
    @staticmethod
    def user_activity_report(
        db: Session,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """Relatório de atividade de usuários"""
        # Ações por usuário
        user_actions = db.query(
            AuditLog.user_name,
            AuditLog.action,
            func.count(AuditLog.id).label("count")
        ).filter(
            AuditLog.timestamp.between(start_date, end_date)
        ).group_by(
            AuditLog.user_name,
            AuditLog.action
        ).all()
        
        # Horários de pico
        peak_hours = db.query(
            func.date_part("hour", AuditLog.timestamp).label("hour"),
            func.count(AuditLog.id).label("count")
        ).filter(
            AuditLog.timestamp.between(start_date, end_date)
        ).group_by("hour").order_by("count desc").limit(5).all()
        
        return {
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            },
            "user_actions": [
                {"user": name, "action": action, "count": count}
                for name, action, count in user_actions
            ],
            "peak_hours": [
                {"hour": int(hour), "count": count}
                for hour, count in peak_hours
            ]
        }
    
    @staticmethod
    def security_report(
        db: Session,
        hours: int = 24
    ) -> Dict[str, Any]:
        """Relatório de segurança"""
        query_service = AuditQuery()
        
        return {
            "period_hours": hours,
            "failed_logins": query_service.get_failed_logins(db, hours),
            "suspicious_activity": query_service.get_suspicious_activity(db, hours),
            "permission_denials": db.query(func.count(AuditLog.id)).filter(
                AuditLog.action == AuditAction.PERMISSION_DENIED.value,
                AuditLog.timestamp >= datetime.now(timezone.utc) - timedelta(hours=hours)
            ).scalar(),
            "errors": db.query(func.count(AuditLog.id)).filter(
                AuditLog.action == AuditAction.ERROR.value,
                AuditLog.timestamp >= datetime.now(timezone.utc) - timedelta(hours=hours)
            ).scalar()
        }

# Instância global do serviço
audit_service = AuditService()

# Exportar componentes principais
__all__ = [
    'AuditLog',
    'AuditEvent',
    'AuditAction',
    'AuditService',
    'AuditQuery',
    'AuditMiddleware',
    'AuditReports',
    'audit_action',
    'audit_service',
    'cleanup_old_logs'
]

# Importações necessárias
from sqlalchemy import func, or_, and_
from datetime import timedelta