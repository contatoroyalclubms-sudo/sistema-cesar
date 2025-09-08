"""
Sistema de Permissões e Roles
Modelos de dados para controle granular de acesso
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime, timezone
import enum

from .database import Base

# ================================================================================
# ENUMS
# ================================================================================

class TipoPermissao(enum.Enum):
    """Tipos de permissão disponíveis"""
    CRIAR = "criar"
    LER = "ler"
    ATUALIZAR = "atualizar"
    DELETAR = "deletar"
    EXECUTAR = "executar"
    APROVAR = "aprovar"
    GERENCIAR = "gerenciar"

class CategoriaPermissao(enum.Enum):
    """Categorias de funcionalidades do sistema"""
    EVENTOS = "eventos"
    USUARIOS = "usuarios"
    FINANCEIRO = "financeiro"
    ESTOQUE = "estoque"
    VENDAS = "vendas"
    RELATORIOS = "relatorios"
    CONFIGURACOES = "configuracoes"
    SISTEMA = "sistema"
    FIDELIDADE = "fidelidade"
    FORNECEDORES = "fornecedores"
    COMPRAS = "compras"
    CARDAPIOS = "cardapios"
    CASHLESS = "cashless"
    IMPRESSORAS = "impressoras"
    KDS = "kds"
    MESAS = "mesas"
    DASHBOARD = "dashboard"

class StatusRole(enum.Enum):
    """Status do role/perfil"""
    ATIVO = "ativo"
    INATIVO = "inativo"
    SUSPENSO = "suspenso"

# ================================================================================
# MODELOS
# ================================================================================

class Role(Base):
    """
    Modelo para roles/perfis de usuário
    Representa grupos de permissões que podem ser atribuídos a usuários
    """
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    empresa_id = Column(Integer, ForeignKey("empresas.id"), nullable=False, index=True)
    
    # Informações básicas
    nome = Column(String(100), nullable=False)
    descricao = Column(Text, nullable=True)
    cor_hexadecimal = Column(String(7), default="#6366f1")  # Para UI
    icone = Column(String(50), nullable=True)  # Material Icon name
    
    # Configurações
    status = Column(String(20), default=StatusRole.ATIVO.value)
    nivel_hierarquia = Column(Integer, default=0)  # 0=menor privilégio, 100=maior
    is_admin = Column(Boolean, default=False)  # Super admin
    is_sistema = Column(Boolean, default=False)  # Role do sistema (não editável)
    acesso_total = Column(Boolean, default=False)  # Acesso a todas as funcionalidades
    
    # Metadados
    criado_em = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    atualizado_em = Column(DateTime(timezone=True), nullable=True)
    criado_por_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True)
    
    # Relacionamentos
    empresa = relationship("Empresa", back_populates="roles")
    criado_por = relationship("Usuario", foreign_keys=[criado_por_id])
    usuarios = relationship("UsuarioRole", back_populates="role", cascade="all, delete-orphan")
    permissoes = relationship("RolePermissao", back_populates="role", cascade="all, delete-orphan")
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('empresa_id', 'nome', name='uq_role_nome_empresa'),
    )

class Permissao(Base):
    """
    Modelo para permissões do sistema
    Representa ações específicas que podem ser executadas
    """
    __tablename__ = "permissoes"

    id = Column(Integer, primary_key=True, index=True)
    
    # Identificação da permissão
    codigo = Column(String(100), unique=True, nullable=False, index=True)  # ex: eventos.criar
    nome = Column(String(200), nullable=False)
    descricao = Column(Text, nullable=True)
    
    # Categorização
    categoria = Column(String(50), nullable=False, index=True)  # CategoriaPermissao
    tipo = Column(String(20), nullable=False)  # TipoPermissao
    
    # Configurações
    ativo = Column(Boolean, default=True)
    is_sistema = Column(Boolean, default=False)  # Permissão do sistema (não editável)
    requer_aprovacao = Column(Boolean, default=False)  # Ação requer aprovação
    nivel_risco = Column(Integer, default=1)  # 1=baixo, 5=alto risco
    
    # Metadados
    criado_em = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    atualizado_em = Column(DateTime(timezone=True), nullable=True)
    
    # Relacionamentos
    roles = relationship("RolePermissao", back_populates="permissao", cascade="all, delete-orphan")

class UsuarioRole(Base):
    """
    Relacionamento N:N entre usuários e roles
    Um usuário pode ter múltiplos roles
    """
    __tablename__ = "usuarios_roles"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False, index=True)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False, index=True)
    empresa_id = Column(Integer, ForeignKey("empresas.id"), nullable=False, index=True)
    
    # Configurações específicas
    ativo = Column(Boolean, default=True)
    data_inicio = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    data_fim = Column(DateTime(timezone=True), nullable=True)
    
    # Metadados
    criado_em = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    criado_por_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True)
    
    # Relacionamentos
    usuario = relationship("Usuario", foreign_keys=[usuario_id])
    role = relationship("Role", back_populates="usuarios")
    empresa = relationship("Empresa")
    criado_por = relationship("Usuario", foreign_keys=[criado_por_id])
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('usuario_id', 'role_id', 'empresa_id', name='uq_usuario_role_empresa'),
    )

class RolePermissao(Base):
    """
    Relacionamento N:N entre roles e permissões
    Define quais permissões cada role possui
    """
    __tablename__ = "roles_permissoes"

    id = Column(Integer, primary_key=True, index=True)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False, index=True)
    permissao_id = Column(Integer, ForeignKey("permissoes.id"), nullable=False, index=True)
    
    # Configurações específicas
    ativo = Column(Boolean, default=True)
    concedido = Column(Boolean, default=True)  # True=permite, False=nega explicitamente
    
    # Metadados
    criado_em = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    criado_por_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True)
    
    # Relacionamentos
    role = relationship("Role", back_populates="permissoes")
    permissao = relationship("Permissao", back_populates="roles")
    criado_por = relationship("Usuario")
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('role_id', 'permissao_id', name='uq_role_permissao'),
    )

class LogAcesso(Base):
    """
    Log de auditoria para controle de acesso
    Registra todas as tentativas de acesso e ações executadas
    """
    __tablename__ = "logs_acesso"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True, index=True)
    empresa_id = Column(Integer, ForeignKey("empresas.id"), nullable=True, index=True)
    
    # Detalhes da ação
    acao = Column(String(100), nullable=False, index=True)  # ex: eventos.criar
    recurso = Column(String(200), nullable=True)  # Recurso específico acessado
    resultado = Column(String(20), nullable=False)  # sucesso, negado, erro
    
    # Contexto técnico
    endpoint = Column(String(200), nullable=True)
    metodo_http = Column(String(10), nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    
    # Detalhes adicionais
    detalhes = Column(Text, nullable=True)  # JSON com detalhes específicos
    dados_request = Column(Text, nullable=True)  # JSON dos dados enviados (sem dados sensíveis)
    tempo_execucao = Column(Integer, nullable=True)  # em milissegundos
    
    # Timestamp
    criado_em = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)
    
    # Relacionamentos
    usuario = relationship("Usuario")
    empresa = relationship("Empresa")

class SessaoUsuario(Base):
    """
    Controle de sessões de usuários
    Para rastreamento e controle de acesso simultâneo
    """
    __tablename__ = "sessoes_usuarios"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False, index=True)
    empresa_id = Column(Integer, ForeignKey("empresas.id"), nullable=False, index=True)
    
    # Identificação da sessão
    token_sessao = Column(String(255), unique=True, nullable=False, index=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    dispositivo = Column(String(200), nullable=True)
    
    # Controle de sessão
    ativa = Column(Boolean, default=True)
    ultimo_acesso = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    data_expiracao = Column(DateTime(timezone=True), nullable=True)
    
    # Metadados
    criado_em = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    encerrado_em = Column(DateTime(timezone=True), nullable=True)
    motivo_encerramento = Column(String(100), nullable=True)  # logout, timeout, revogado, etc.
    
    # Relacionamentos
    usuario = relationship("Usuario")
    empresa = relationship("Empresa")

# ================================================================================
# PERMISSÕES PADRÃO DO SISTEMA
# ================================================================================

PERMISSOES_SISTEMA = [
    # Eventos
    {"codigo": "eventos.criar", "nome": "Criar Eventos", "categoria": "eventos", "tipo": "criar"},
    {"codigo": "eventos.ler", "nome": "Visualizar Eventos", "categoria": "eventos", "tipo": "ler"},
    {"codigo": "eventos.atualizar", "nome": "Editar Eventos", "categoria": "eventos", "tipo": "atualizar"},
    {"codigo": "eventos.deletar", "nome": "Excluir Eventos", "categoria": "eventos", "tipo": "deletar"},
    {"codigo": "eventos.gerenciar", "nome": "Gerenciar Eventos", "categoria": "eventos", "tipo": "gerenciar"},
    
    # Usuários
    {"codigo": "usuarios.criar", "nome": "Criar Usuários", "categoria": "usuarios", "tipo": "criar"},
    {"codigo": "usuarios.ler", "nome": "Visualizar Usuários", "categoria": "usuarios", "tipo": "ler"},
    {"codigo": "usuarios.atualizar", "nome": "Editar Usuários", "categoria": "usuarios", "tipo": "atualizar"},
    {"codigo": "usuarios.deletar", "nome": "Excluir Usuários", "categoria": "usuarios", "tipo": "deletar"},
    {"codigo": "usuarios.gerenciar_roles", "nome": "Gerenciar Roles de Usuários", "categoria": "usuarios", "tipo": "gerenciar"},
    
    # Financeiro
    {"codigo": "financeiro.ler", "nome": "Visualizar Financeiro", "categoria": "financeiro", "tipo": "ler"},
    {"codigo": "financeiro.criar_transacao", "nome": "Criar Transações", "categoria": "financeiro", "tipo": "criar"},
    {"codigo": "financeiro.aprovar_transacao", "nome": "Aprovar Transações", "categoria": "financeiro", "tipo": "aprovar"},
    {"codigo": "financeiro.dashboard_completo", "nome": "Dashboard Financeiro Completo", "categoria": "financeiro", "tipo": "ler"},
    
    # Estoque
    {"codigo": "estoque.ler", "nome": "Visualizar Estoque", "categoria": "estoque", "tipo": "ler"},
    {"codigo": "estoque.atualizar", "nome": "Atualizar Estoque", "categoria": "estoque", "tipo": "atualizar"},
    {"codigo": "estoque.criar_produto", "nome": "Criar Produtos", "categoria": "estoque", "tipo": "criar"},
    {"codigo": "estoque.gerenciar", "nome": "Gerenciar Estoque", "categoria": "estoque", "tipo": "gerenciar"},
    
    # Vendas
    {"codigo": "vendas.criar", "nome": "Realizar Vendas", "categoria": "vendas", "tipo": "criar"},
    {"codigo": "vendas.ler", "nome": "Visualizar Vendas", "categoria": "vendas", "tipo": "ler"},
    {"codigo": "vendas.cancelar", "nome": "Cancelar Vendas", "categoria": "vendas", "tipo": "deletar"},
    {"codigo": "vendas.aprovar_desconto", "nome": "Aprovar Descontos", "categoria": "vendas", "tipo": "aprovar"},
    
    # Relatórios
    {"codigo": "relatorios.vendas", "nome": "Relatórios de Vendas", "categoria": "relatorios", "tipo": "ler"},
    {"codigo": "relatorios.financeiro", "nome": "Relatórios Financeiros", "categoria": "relatorios", "tipo": "ler"},
    {"codigo": "relatorios.estoque", "nome": "Relatórios de Estoque", "categoria": "relatorios", "tipo": "ler"},
    {"codigo": "relatorios.gerar_customizado", "nome": "Gerar Relatórios Customizados", "categoria": "relatorios", "tipo": "criar"},
    
    # Sistema
    {"codigo": "sistema.configuracoes", "nome": "Configurações do Sistema", "categoria": "sistema", "tipo": "gerenciar"},
    {"codigo": "sistema.backup", "nome": "Realizar Backup", "categoria": "sistema", "tipo": "executar"},
    {"codigo": "sistema.logs", "nome": "Visualizar Logs", "categoria": "sistema", "tipo": "ler"},
    {"codigo": "sistema.permissoes", "nome": "Gerenciar Permissões", "categoria": "sistema", "tipo": "gerenciar"},
    
    # Fidelidade
    {"codigo": "fidelidade.ler", "nome": "Visualizar Fidelidade", "categoria": "fidelidade", "tipo": "ler"},
    {"codigo": "fidelidade.gerenciar_niveis", "nome": "Gerenciar Níveis", "categoria": "fidelidade", "tipo": "gerenciar"},
    {"codigo": "fidelidade.gerenciar_campanhas", "nome": "Gerenciar Campanhas", "categoria": "fidelidade", "tipo": "gerenciar"},
    {"codigo": "fidelidade.movimentar_pontos", "nome": "Movimentar Pontos", "categoria": "fidelidade", "tipo": "criar"},
    
    # Fornecedores
    {"codigo": "fornecedores.criar", "nome": "Criar Fornecedores", "categoria": "fornecedores", "tipo": "criar"},
    {"codigo": "fornecedores.ler", "nome": "Visualizar Fornecedores", "categoria": "fornecedores", "tipo": "ler"},
    {"codigo": "fornecedores.atualizar", "nome": "Editar Fornecedores", "categoria": "fornecedores", "tipo": "atualizar"},
    {"codigo": "fornecedores.deletar", "nome": "Excluir Fornecedores", "categoria": "fornecedores", "tipo": "deletar"},
    
    # Compras
    {"codigo": "compras.criar", "nome": "Criar Ordens de Compra", "categoria": "compras", "tipo": "criar"},
    {"codigo": "compras.ler", "nome": "Visualizar Compras", "categoria": "compras", "tipo": "ler"},
    {"codigo": "compras.aprovar", "nome": "Aprovar Ordens de Compra", "categoria": "compras", "tipo": "aprovar"},
    {"codigo": "compras.receber", "nome": "Receber Mercadorias", "categoria": "compras", "tipo": "executar"},
]

# ================================================================================
# ROLES PADRÃO DO SISTEMA
# ================================================================================

ROLES_SISTEMA = [
    {
        "nome": "Super Admin",
        "descricao": "Acesso total ao sistema",
        "is_admin": True,
        "is_sistema": True,
        "acesso_total": True,
        "nivel_hierarquia": 100,
        "cor_hexadecimal": "#dc2626"
    },
    {
        "nome": "Administrador",
        "descricao": "Administrador da empresa com amplos privilégios",
        "is_admin": False,
        "is_sistema": True,
        "acesso_total": False,
        "nivel_hierarquia": 90,
        "cor_hexadecimal": "#ea580c"
    },
    {
        "nome": "Gerente",
        "descricao": "Gerente com acesso a relatórios e aprovações",
        "is_admin": False,
        "is_sistema": True,
        "acesso_total": False,
        "nivel_hierarquia": 70,
        "cor_hexadecimal": "#0ea5e9"
    },
    {
        "nome": "Operador",
        "descricao": "Operador com acesso às funcionalidades operacionais",
        "is_admin": False,
        "is_sistema": True,
        "acesso_total": False,
        "nivel_hierarquia": 50,
        "cor_hexadecimal": "#10b981"
    },
    {
        "nome": "Caixa",
        "descricao": "Operador de caixa com acesso limitado a vendas",
        "is_admin": False,
        "is_sistema": True,
        "acesso_total": False,
        "nivel_hierarquia": 30,
        "cor_hexadecimal": "#8b5cf6"
    },
    {
        "nome": "Visualizador",
        "descricao": "Acesso apenas para visualização",
        "is_admin": False,
        "is_sistema": True,
        "acesso_total": False,
        "nivel_hierarquia": 10,
        "cor_hexadecimal": "#6b7280"
    }
]
