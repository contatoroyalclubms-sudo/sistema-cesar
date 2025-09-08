// Frontend Service para Sistema de Permissões e Roles Expandido
// Gestão completa de controle de acesso granular

import { api } from './api';

// ================================================================================
// INTERFACES E TIPOS
// ================================================================================

export enum TipoPermissao {
  CRIAR = 'criar',
  LER = 'ler',
  ATUALIZAR = 'atualizar',
  DELETAR = 'deletar',
  EXECUTAR = 'executar',
  APROVAR = 'aprovar',
  GERENCIAR = 'gerenciar'
}

export enum CategoriaPermissao {
  EVENTOS = 'eventos',
  USUARIOS = 'usuarios',
  FINANCEIRO = 'financeiro',
  ESTOQUE = 'estoque',
  VENDAS = 'vendas',
  RELATORIOS = 'relatorios',
  CONFIGURACOES = 'configuracoes',
  SISTEMA = 'sistema',
  FIDELIDADE = 'fidelidade',
  FORNECEDORES = 'fornecedores',
  COMPRAS = 'compras',
  CARDAPIOS = 'cardapios',
  CASHLESS = 'cashless',
  IMPRESSORAS = 'impressoras',
  KDS = 'kds',
  MESAS = 'mesas',
  DASHBOARD = 'dashboard'
}

export enum StatusRole {
  ATIVO = 'ativo',
  INATIVO = 'inativo',
  SUSPENSO = 'suspenso'
}

export interface Role {
  id: number;
  empresa_id: number;
  nome: string;
  descricao?: string;
  cor_hexadecimal: string;
  icone?: string;
  status: StatusRole;
  nivel_hierarquia: number;
  is_admin: boolean;
  is_sistema: boolean;
  acesso_total: boolean;
  criado_em: string;
  atualizado_em?: string;
  criado_por_id?: number;
}

export interface Permissao {
  id: number;
  codigo: string;
  nome: string;
  descricao?: string;
  categoria: CategoriaPermissao;
  tipo: TipoPermissao;
  ativo: boolean;
  is_sistema: boolean;
  requer_aprovacao: boolean;
  nivel_risco: number;
  criado_em: string;
  atualizado_em?: string;
}

export interface UsuarioRole {
  id: number;
  usuario_id: number;
  role_id: number;
  empresa_id: number;
  ativo: boolean;
  data_inicio: string;
  data_fim?: string;
  criado_em: string;
  criado_por_id?: number;
}

export interface RolePermissao {
  id: number;
  role_id: number;
  permissao_id: number;
  ativo: boolean;
  concedido: boolean;
  criado_em: string;
  criado_por_id?: number;
}

export interface LogAcesso {
  id: number;
  usuario_id?: number;
  empresa_id?: number;
  acao: string;
  recurso?: string;
  resultado: string;
  endpoint?: string;
  metodo_http?: string;
  ip_address?: string;
  user_agent?: string;
  detalhes?: string;
  dados_request?: string;
  tempo_execucao?: number;
  criado_em: string;
}

export interface SessaoUsuario {
  id: number;
  usuario_id: number;
  empresa_id: number;
  token_sessao: string;
  ip_address?: string;
  user_agent?: string;
  dispositivo?: string;
  ativa: boolean;
  ultimo_acesso: string;
  data_expiracao?: string;
  criado_em: string;
  encerrado_em?: string;
  motivo_encerramento?: string;
}

export interface RoleCreate {
  nome: string;
  descricao?: string;
  cor_hexadecimal?: string;
  icone?: string;
  nivel_hierarquia?: number;
  is_admin?: boolean;
  acesso_total?: boolean;
}

export interface RoleUpdate {
  nome?: string;
  descricao?: string;
  cor_hexadecimal?: string;
  icone?: string;
  nivel_hierarquia?: number;
  status?: StatusRole;
}

export interface PermissaoCreate {
  codigo: string;
  nome: string;
  descricao?: string;
  categoria: CategoriaPermissao;
  tipo: TipoPermissao;
  nivel_risco?: number;
  requer_aprovacao?: boolean;
}

export interface UsuarioRoleCreate {
  usuario_id: number;
  role_id: number;
  data_fim?: string;
}

export interface RolePermissaoCreate {
  role_id: number;
  permissao_ids: number[];
}

export interface DashboardPermissoes {
  total_usuarios: number;
  total_roles: number;
  total_permissoes: number;
  sessoes_ativas: number;
  distribuicao_roles: Array<{
    nome: string;
    cor: string;
    total_usuarios: number;
  }>;
  logs_recentes: Array<{
    log: LogAcesso;
  }>;
}

// ================================================================================
// SERVIÇO PRINCIPAL
// ================================================================================

export class PermissoesService {

  // ============================================================================
  // INICIALIZAÇÃO
  // ============================================================================

  static async inicializarSistema(): Promise<{
    message: string;
    permissoes_criadas: number;
    roles_criados: number;
  }> {
    try {
      const response = await api.post('/api/permissoes-expandido/inicializar');
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || 'Erro ao inicializar sistema de permissões');
    }
  }

  // ============================================================================
  // GESTÃO DE ROLES
  // ============================================================================

  static async criarRole(dados: RoleCreate): Promise<{ id: number; message: string }> {
    try {
      const response = await api.post('/api/permissoes-expandido/roles', dados);
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || 'Erro ao criar role');
    }
  }

  static async listarRoles(
    ativo?: boolean,
    isSistema?: boolean
  ): Promise<Array<{
    role: Role;
    total_usuarios: number;
    total_permissoes: number;
  }>> {
    try {
      const params: any = {};
      if (ativo !== undefined) params.ativo = ativo;
      if (isSistema !== undefined) params.is_sistema = isSistema;
      
      const response = await api.get('/api/permissoes-expandido/roles', { params });
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || 'Erro ao listar roles');
    }
  }

  static async obterRole(roleId: number): Promise<{
    role: Role;
    permissoes: Array<{
      permissao: Permissao;
      concedido: boolean;
    }>;
    usuarios: Array<{
      usuario: any;
      ativo: boolean;
      data_inicio: string;
      data_fim?: string;
    }>;
  }> {
    try {
      const response = await api.get(`/api/permissoes-expandido/roles/${roleId}`);
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || 'Erro ao obter role');
    }
  }

  static async atualizarRole(roleId: number, dados: RoleUpdate): Promise<{ message: string }> {
    try {
      const response = await api.patch(`/api/permissoes-expandido/roles/${roleId}`, dados);
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || 'Erro ao atualizar role');
    }
  }

  // ============================================================================
  // GESTÃO DE PERMISSÕES
  // ============================================================================

  static async listarPermissoes(
    categoria?: CategoriaPermissao,
    tipo?: TipoPermissao,
    ativo?: boolean
  ): Promise<Array<{
    categoria: string;
    permissoes: Permissao[];
  }>> {
    try {
      const params: any = {};
      if (categoria) params.categoria = categoria;
      if (tipo) params.tipo = tipo;
      if (ativo !== undefined) params.ativo = ativo;
      
      const response = await api.get('/api/permissoes-expandido/permissoes', { params });
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || 'Erro ao listar permissões');
    }
  }

  static async criarPermissao(dados: PermissaoCreate): Promise<{ id: number; message: string }> {
    try {
      const response = await api.post('/api/permissoes-expandido/permissoes', dados);
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || 'Erro ao criar permissão');
    }
  }

  // ============================================================================
  // ATRIBUIÇÃO DE ROLES E PERMISSÕES
  // ============================================================================

  static async atribuirRoleUsuario(usuarioId: number, dados: UsuarioRoleCreate): Promise<{ message: string }> {
    try {
      const response = await api.post(`/api/permissoes-expandido/usuarios/${usuarioId}/roles`, dados);
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || 'Erro ao atribuir role ao usuário');
    }
  }

  static async atribuirPermissoesRole(roleId: number, dados: RolePermissaoCreate): Promise<{ message: string }> {
    try {
      const response = await api.post(`/api/permissoes-expandido/roles/${roleId}/permissoes`, dados);
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || 'Erro ao atribuir permissões ao role');
    }
  }

  // ============================================================================
  // VERIFICAÇÃO DE PERMISSÕES
  // ============================================================================

  static async obterPermissoesUsuario(usuarioId: number): Promise<string[]> {
    try {
      const response = await api.get(`/api/permissoes-expandido/usuarios/${usuarioId}/permissoes`);
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || 'Erro ao obter permissões do usuário');
    }
  }

  static async verificarPermissao(acao: string, usuarioId?: number): Promise<{
    tem_permissao: boolean;
    acao: string;
    usuario_id: number;
  }> {
    try {
      const params: any = { acao };
      if (usuarioId) params.usuario_id = usuarioId;
      
      const response = await api.post('/api/permissoes-expandido/verificar-permissao', params);
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || 'Erro ao verificar permissão');
    }
  }

  // ============================================================================
  // DASHBOARD
  // ============================================================================

  static async obterDashboard(): Promise<DashboardPermissoes> {
    try {
      const response = await api.get('/api/permissoes-expandido/dashboard');
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || 'Erro ao obter dashboard de permissões');
    }
  }

  // ============================================================================
  // UTILITÁRIOS
  // ============================================================================

  static obterCorNivelHierarquia(nivel: number): string {
    if (nivel >= 90) return '#dc2626'; // Vermelho para alta hierarquia
    if (nivel >= 70) return '#ea580c'; // Laranja para gerência
    if (nivel >= 50) return '#0ea5e9'; // Azul para operacional
    if (nivel >= 30) return '#10b981'; // Verde para básico
    return '#6b7280'; // Cinza para baixo nível
  }

  static obterIconeCategoria(categoria: CategoriaPermissao): string {
    const icones = {
      [CategoriaPermissao.EVENTOS]: '🎉',
      [CategoriaPermissao.USUARIOS]: '👥',
      [CategoriaPermissao.FINANCEIRO]: '💰',
      [CategoriaPermissao.ESTOQUE]: '📦',
      [CategoriaPermissao.VENDAS]: '🛒',
      [CategoriaPermissao.RELATORIOS]: '📊',
      [CategoriaPermissao.CONFIGURACOES]: '⚙️',
      [CategoriaPermissao.SISTEMA]: '🔧',
      [CategoriaPermissao.FIDELIDADE]: '⭐',
      [CategoriaPermissao.FORNECEDORES]: '🏢',
      [CategoriaPermissao.COMPRAS]: '📋',
      [CategoriaPermissao.CARDAPIOS]: '🍽️',
      [CategoriaPermissao.CASHLESS]: '💳',
      [CategoriaPermissao.IMPRESSORAS]: '🖨️',
      [CategoriaPermissao.KDS]: '📺',
      [CategoriaPermissao.MESAS]: '🪑',
      [CategoriaPermissao.DASHBOARD]: '📈'
    };
    return icones[categoria] || '🔒';
  }

  static obterDescricaoTipo(tipo: TipoPermissao): string {
    const descricoes = {
      [TipoPermissao.CRIAR]: 'Criar novos registros',
      [TipoPermissao.LER]: 'Visualizar informações',
      [TipoPermissao.ATUALIZAR]: 'Editar registros existentes',
      [TipoPermissao.DELETAR]: 'Excluir registros',
      [TipoPermissao.EXECUTAR]: 'Executar ações específicas',
      [TipoPermissao.APROVAR]: 'Aprovar operações',
      [TipoPermissao.GERENCIAR]: 'Gestão completa do módulo'
    };
    return descricoes[tipo] || 'Ação específica';
  }

  static obterCorNivelRisco(nivel: number): string {
    if (nivel >= 4) return '#dc2626'; // Alto risco - vermelho
    if (nivel >= 3) return '#ea580c'; // Médio-alto - laranja
    if (nivel >= 2) return '#eab308'; // Médio - amarelo
    return '#10b981'; // Baixo risco - verde
  }

  static obterDescricaoNivelRisco(nivel: number): string {
    if (nivel >= 4) return 'Alto Risco';
    if (nivel >= 3) return 'Médio-Alto Risco';
    if (nivel >= 2) return 'Médio Risco';
    return 'Baixo Risco';
  }

  static validarRole(role: RoleCreate): string[] {
    const erros: string[] = [];

    if (!role.nome.trim()) {
      erros.push('Nome do role é obrigatório');
    }

    if (role.nome.length < 3) {
      erros.push('Nome do role deve ter pelo menos 3 caracteres');
    }

    if (role.nivel_hierarquia && (role.nivel_hierarquia < 0 || role.nivel_hierarquia > 100)) {
      erros.push('Nível de hierarquia deve estar entre 0 e 100');
    }

    if (role.cor_hexadecimal && !/^#[0-9A-Fa-f]{6}$/.test(role.cor_hexadecimal)) {
      erros.push('Cor deve estar no formato hexadecimal (#RRGGBB)');
    }

    return erros;
  }

  static validarPermissao(permissao: PermissaoCreate): string[] {
    const erros: string[] = [];

    if (!permissao.codigo.trim()) {
      erros.push('Código da permissão é obrigatório');
    }

    if (!/^[a-z_]+\.[a-z_]+$/.test(permissao.codigo)) {
      erros.push('Código deve estar no formato "categoria.acao" (ex: eventos.criar)');
    }

    if (!permissao.nome.trim()) {
      erros.push('Nome da permissão é obrigatório');
    }

    if (permissao.nivel_risco && (permissao.nivel_risco < 1 || permissao.nivel_risco > 5)) {
      erros.push('Nível de risco deve estar entre 1 e 5');
    }

    return erros;
  }

  static formatarDataUltimoAcesso(data: string): string {
    const agora = new Date();
    const dataAcesso = new Date(data);
    const diffMs = agora.getTime() - dataAcesso.getTime();
    const diffMinutos = Math.floor(diffMs / (1000 * 60));

    if (diffMinutos < 1) return 'Agora';
    if (diffMinutos < 60) return `${diffMinutos} min atrás`;
    
    const diffHoras = Math.floor(diffMinutos / 60);
    if (diffHoras < 24) return `${diffHoras}h atrás`;
    
    const diffDias = Math.floor(diffHoras / 24);
    if (diffDias < 7) return `${diffDias} dias atrás`;
    
    return new Intl.DateTimeFormat('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric'
    }).format(dataAcesso);
  }

  static gerarRelatorioPermissoes(roles: Array<{ role: Role; total_usuarios: number; total_permissoes: number }>): {
    total_usuarios_com_role: number;
    role_mais_utilizado: string;
    distribuicao_hierarquia: { [key: string]: number };
    cobertura_permissoes: number;
  } {
    const totalUsuariosComRole = roles.reduce((total, r) => total + r.total_usuarios, 0);
    
    const roleMaisUtilizado = roles
      .sort((a, b) => b.total_usuarios - a.total_usuarios)[0]?.role?.nome || 'N/A';
    
    const distribuicaoHierarquia: { [key: string]: number } = {};
    roles.forEach(r => {
      const nivel = r.role.nivel_hierarquia;
      const categoria = nivel >= 90 ? 'Alta' : nivel >= 50 ? 'Média' : 'Baixa';
      distribuicaoHierarquia[categoria] = (distribuicaoHierarquia[categoria] || 0) + r.total_usuarios;
    });
    
    const totalPermissoesPossiveis = roles.length * 50; // Estimativa
    const totalPermissoesAtribuidas = roles.reduce((total, r) => total + r.total_permissoes, 0);
    const coberturaPermissoes = totalPermissoesPossiveis > 0 ? 
      Math.round((totalPermissoesAtribuidas / totalPermissoesPossiveis) * 100) : 0;

    return {
      total_usuarios_com_role: totalUsuariosComRole,
      role_mais_utilizado: roleMaisUtilizado,
      distribuicao_hierarquia: distribuicaoHierarquia,
      cobertura_permissoes: coberturaPermissoes
    };
  }

  static verificarConsistenciaPermissoes(permissoes: string[]): {
    permissoes_conflitantes: string[];
    permissoes_redundantes: string[];
    sugestoes: string[];
  } {
    const conflitantes: string[] = [];
    const redundantes: string[] = [];
    const sugestoes: string[] = [];

    // Verificar conflitos (ex: ter deletar sem ter ler)
    const temDeletar = permissoes.filter(p => p.endsWith('.deletar'));
    temDeletar.forEach(delPerm => {
      const modulo = delPerm.split('.')[0];
      const lerPerm = `${modulo}.ler`;
      if (!permissoes.includes(lerPerm)) {
        conflitantes.push(`${delPerm} requer ${lerPerm}`);
      }
    });

    // Verificar redundâncias (gerenciar inclui outras)
    const temGerenciar = permissoes.filter(p => p.endsWith('.gerenciar'));
    temGerenciar.forEach(gerPerm => {
      const modulo = gerPerm.split('.')[0];
      const outrasPermissoes = permissoes.filter(p => p.startsWith(`${modulo}.`) && !p.endsWith('.gerenciar'));
      if (outrasPermissoes.length > 0) {
        redundantes.push(`${gerPerm} torna desnecessárias: ${outrasPermissoes.join(', ')}`);
      }
    });

    // Sugestões baseadas em padrões comuns
    if (permissoes.includes('vendas.criar') && !permissoes.includes('estoque.ler')) {
      sugestoes.push('Usuários que criam vendas geralmente precisam visualizar o estoque');
    }

    if (permissoes.includes('relatorios.financeiro') && !permissoes.includes('financeiro.ler')) {
      sugestoes.push('Relatórios financeiros requerem acesso aos dados financeiros');
    }

    return {
      permissoes_conflitantes: conflitantes,
      permissoes_redundantes: redundantes,
      sugestoes
    };
  }
}
