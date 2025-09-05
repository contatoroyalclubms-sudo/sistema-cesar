"""
Serviço de Audit Trail para rastreamento de ações no sistema
"""
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from datetime import datetime
import json

from app.models import AuditLog

class AuditService:
    """Serviço para registrar ações de auditoria"""
    
    @staticmethod
    def log_action(
        db: Session,
        usuario_id: Optional[int],
        workspace_id: Optional[int],
        acao: str,
        entidade: str,
        entidade_id: Optional[int] = None,
        dados_anteriores: Optional[Dict[str, Any]] = None,
        dados_novos: Optional[Dict[str, Any]] = None,
        ip_origem: Optional[str] = None,
        user_agent: Optional[str] = None,
        metadados: Optional[Dict[str, Any]] = None
    ) -> AuditLog:
        """
        Registra uma ação no audit trail
        
        Args:
            db: Sessão do banco de dados
            usuario_id: ID do usuário que executou a ação
            workspace_id: ID do workspace onde a ação ocorreu
            acao: Tipo de ação (create, update, delete, login, export, etc)
            entidade: Tipo de entidade afetada (evento, usuario, produto, etc)
            entidade_id: ID da entidade afetada
            dados_anteriores: Estado anterior da entidade (para updates)
            dados_novos: Novo estado da entidade
            ip_origem: IP de origem da requisição
            user_agent: User agent do navegador/app
            metadados: Dados adicionais relevantes
        
        Returns:
            AuditLog: Registro de auditoria criado
        """
        audit_log = AuditLog(
            usuario_id=usuario_id,
            workspace_id=workspace_id,
            acao=acao,
            entidade=entidade,
            entidade_id=entidade_id,
            dados_anteriores=json.dumps(dados_anteriores, default=str) if dados_anteriores else None,
            dados_novos=json.dumps(dados_novos, default=str) if dados_novos else None,
            ip_origem=ip_origem,
            user_agent=user_agent[:500] if user_agent else None,  # Limitar tamanho
            metadados=json.dumps(metadados, default=str) if metadados else None
        )
        
        db.add(audit_log)
        db.commit()
        
        return audit_log
    
    @staticmethod
    def log_login(
        db: Session,
        usuario_id: int,
        workspace_id: Optional[int],
        sucesso: bool,
        ip_origem: Optional[str] = None,
        user_agent: Optional[str] = None,
        metodo_login: str = "password"
    ) -> AuditLog:
        """
        Registra tentativa de login
        
        Args:
            db: Sessão do banco de dados
            usuario_id: ID do usuário
            workspace_id: ID do workspace
            sucesso: Se o login foi bem-sucedido
            ip_origem: IP de origem
            user_agent: User agent
            metodo_login: Método de login (password, google, etc)
        
        Returns:
            AuditLog: Registro de auditoria criado
        """
        return AuditService.log_action(
            db=db,
            usuario_id=usuario_id,
            workspace_id=workspace_id,
            acao="login" if sucesso else "login_failed",
            entidade="usuario",
            entidade_id=usuario_id,
            metadados={
                "metodo": metodo_login,
                "timestamp": datetime.utcnow().isoformat()
            },
            ip_origem=ip_origem,
            user_agent=user_agent
        )
    
    @staticmethod
    def log_export(
        db: Session,
        usuario_id: int,
        workspace_id: Optional[int],
        tipo_export: str,
        formato: str,
        filtros: Optional[Dict[str, Any]] = None,
        total_registros: int = 0,
        ip_origem: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> AuditLog:
        """
        Registra exportação de dados
        
        Args:
            db: Sessão do banco de dados
            usuario_id: ID do usuário
            workspace_id: ID do workspace
            tipo_export: Tipo de dados exportados (eventos, usuarios, vendas, etc)
            formato: Formato de exportação (csv, excel, pdf, etc)
            filtros: Filtros aplicados na exportação
            total_registros: Número de registros exportados
            ip_origem: IP de origem
            user_agent: User agent
        
        Returns:
            AuditLog: Registro de auditoria criado
        """
        return AuditService.log_action(
            db=db,
            usuario_id=usuario_id,
            workspace_id=workspace_id,
            acao="export",
            entidade=tipo_export,
            metadados={
                "formato": formato,
                "filtros": filtros,
                "total_registros": total_registros,
                "timestamp": datetime.utcnow().isoformat()
            },
            ip_origem=ip_origem,
            user_agent=user_agent
        )
    
    @staticmethod
    def log_permission_change(
        db: Session,
        usuario_id: int,
        workspace_id: Optional[int],
        usuario_alvo_id: int,
        papel_anterior: str,
        papel_novo: str,
        ip_origem: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> AuditLog:
        """
        Registra mudança de permissões/papel de usuário
        
        Args:
            db: Sessão do banco de dados
            usuario_id: ID do usuário que fez a mudança
            workspace_id: ID do workspace
            usuario_alvo_id: ID do usuário que teve permissões alteradas
            papel_anterior: Papel anterior
            papel_novo: Novo papel
            ip_origem: IP de origem
            user_agent: User agent
        
        Returns:
            AuditLog: Registro de auditoria criado
        """
        return AuditService.log_action(
            db=db,
            usuario_id=usuario_id,
            workspace_id=workspace_id,
            acao="permission_change",
            entidade="usuario",
            entidade_id=usuario_alvo_id,
            dados_anteriores={"papel": papel_anterior},
            dados_novos={"papel": papel_novo},
            ip_origem=ip_origem,
            user_agent=user_agent
        )
    
    @staticmethod
    def log_financial_operation(
        db: Session,
        usuario_id: int,
        workspace_id: Optional[int],
        tipo_operacao: str,
        valor: float,
        detalhes: Dict[str, Any],
        ip_origem: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> AuditLog:
        """
        Registra operação financeira
        
        Args:
            db: Sessão do banco de dados
            usuario_id: ID do usuário
            workspace_id: ID do workspace
            tipo_operacao: Tipo de operação (venda, estorno, recarga, etc)
            valor: Valor da operação
            detalhes: Detalhes adicionais da operação
            ip_origem: IP de origem
            user_agent: User agent
        
        Returns:
            AuditLog: Registro de auditoria criado
        """
        return AuditService.log_action(
            db=db,
            usuario_id=usuario_id,
            workspace_id=workspace_id,
            acao=tipo_operacao,
            entidade="financeiro",
            dados_novos={
                "valor": valor,
                **detalhes
            },
            metadados={
                "timestamp": datetime.utcnow().isoformat(),
                "valor": valor
            },
            ip_origem=ip_origem,
            user_agent=user_agent
        )
    
    @staticmethod
    def get_audit_logs(
        db: Session,
        workspace_id: Optional[int] = None,
        usuario_id: Optional[int] = None,
        entidade: Optional[str] = None,
        acao: Optional[str] = None,
        data_inicio: Optional[datetime] = None,
        data_fim: Optional[datetime] = None,
        limite: int = 100,
        offset: int = 0
    ) -> list:
        """
        Busca logs de auditoria com filtros
        
        Args:
            db: Sessão do banco de dados
            workspace_id: Filtrar por workspace
            usuario_id: Filtrar por usuário
            entidade: Filtrar por tipo de entidade
            acao: Filtrar por tipo de ação
            data_inicio: Data inicial do período
            data_fim: Data final do período
            limite: Número máximo de registros
            offset: Offset para paginação
        
        Returns:
            Lista de logs de auditoria
        """
        query = db.query(AuditLog)
        
        if workspace_id:
            query = query.filter(AuditLog.workspace_id == workspace_id)
        
        if usuario_id:
            query = query.filter(AuditLog.usuario_id == usuario_id)
        
        if entidade:
            query = query.filter(AuditLog.entidade == entidade)
        
        if acao:
            query = query.filter(AuditLog.acao == acao)
        
        if data_inicio:
            query = query.filter(AuditLog.criado_em >= data_inicio)
        
        if data_fim:
            query = query.filter(AuditLog.criado_em <= data_fim)
        
        # Ordenar por data decrescente (mais recentes primeiro)
        query = query.order_by(AuditLog.criado_em.desc())
        
        # Aplicar limite e offset
        query = query.limit(limite).offset(offset)
        
        logs = query.all()
        
        # Converter JSON strings para objetos
        for log in logs:
            if log.dados_anteriores:
                log.dados_anteriores = json.loads(log.dados_anteriores)
            if log.dados_novos:
                log.dados_novos = json.loads(log.dados_novos)
            if log.metadados:
                log.metadados = json.loads(log.metadados)
        
        return logs
    
    @staticmethod
    def get_user_activity(
        db: Session,
        usuario_id: int,
        dias: int = 30,
        limite: int = 100
    ) -> list:
        """
        Obtém atividade recente de um usuário
        
        Args:
            db: Sessão do banco de dados
            usuario_id: ID do usuário
            dias: Número de dias para buscar (padrão 30)
            limite: Número máximo de registros
        
        Returns:
            Lista de atividades do usuário
        """
        from datetime import timedelta
        
        data_inicio = datetime.utcnow() - timedelta(days=dias)
        
        return AuditService.get_audit_logs(
            db=db,
            usuario_id=usuario_id,
            data_inicio=data_inicio,
            limite=limite
        )
    
    @staticmethod
    def get_entity_history(
        db: Session,
        entidade: str,
        entidade_id: int,
        limite: int = 50
    ) -> list:
        """
        Obtém histórico de mudanças de uma entidade específica
        
        Args:
            db: Sessão do banco de dados
            entidade: Tipo de entidade
            entidade_id: ID da entidade
            limite: Número máximo de registros
        
        Returns:
            Lista de mudanças da entidade
        """
        logs = db.query(AuditLog).filter(
            AuditLog.entidade == entidade,
            AuditLog.entidade_id == entidade_id
        ).order_by(AuditLog.criado_em.desc()).limit(limite).all()
        
        # Converter JSON strings para objetos
        for log in logs:
            if log.dados_anteriores:
                log.dados_anteriores = json.loads(log.dados_anteriores)
            if log.dados_novos:
                log.dados_novos = json.loads(log.dados_novos)
            if log.metadados:
                log.metadados = json.loads(log.metadados)
        
        return logs