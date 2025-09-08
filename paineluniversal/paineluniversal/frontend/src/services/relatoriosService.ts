import { api } from './api';

// === INTERFACES ===

export interface ConfiguracaoRelatorio {
  id: number;
  nome: string;
  descricao?: string;
  tipo: TipoRelatorio;
  categoria?: string;
  query_sql: string;
  configuracao_visual: Record<string, any>;
  filtros_disponiveis: FiltroDisponivel[];
  parametros_padrao: Record<string, any>;
  cache_duracao: number;
  timeout_execucao: number;
  limite_registros: number;
  tags: string[];
  autor_nome?: string;
  status: StatusRelatorio;
  nivel_permissao: NivelPermissao;
  publico: boolean;
  total_execucoes: number;
  ultima_execucao?: string;
  tempo_medio_execucao: number;
  criado_em: string;
  atualizado_em?: string;
}

export interface ExecucaoRelatorio {
  id: number;
  status: StatusExecucao;
  iniciado_em: string;
  concluido_em?: string;
  tempo_execucao?: number;
  total_registros?: number;
  dados_resultado?: any[];
  arquivo_resultado?: string;
  erro_detalhes?: string;
}

export interface DashboardExecutivo {
  id: number;
  nome: string;
  descricao?: string;
  categoria?: string;
  layout_configuracao: Record<string, any>;
  configuracao_tema: Record<string, any>;
  auto_refresh: boolean;
  intervalo_refresh: number;
  publico: boolean;
  nivel_permissao: NivelPermissao;
  tags: string[];
  total_widgets: number;
  total_visualizacoes: number;
  ultima_visualizacao?: string;
  ativo: boolean;
  criado_em: string;
}

export interface WidgetDashboard {
  id: number;
  dashboard_id: number;
  nome: string;
  tipo: TipoWidget;
  descricao?: string;
  configuracao_relatorio_id?: number;
  query_customizada?: string;
  parametros: Record<string, any>;
  posicao_x: number;
  posicao_y: number;
  largura: number;
  altura: number;
  configuracao_visual: Record<string, any>;
  tipo_visualizacao?: TipoVisualizacao;
  auto_refresh: boolean;
  intervalo_refresh: number;
  dados?: any[];
  erro?: string;
  carregando?: boolean;
}

export interface MetricaNegocio {
  id: number;
  nome: string;
  codigo: string;
  descricao?: string;
  categoria?: string;
  formula_sql: string;
  unidade?: string;
  formato_exibicao?: string;
  meta_valor?: number;
  meta_tipo?: string;
  ultimo_valor?: number;
  ultimo_calculo?: string;
  alerta_habilitado: boolean;
  alerta_threshold?: number;
  frequencia_calculo: FrequenciaAgendamento;
  periodo_analise: string;
  manter_historico: boolean;
  dias_historico: number;
  ativo: boolean;
  criado_em: string;
}

export interface DashboardRelatorios {
  total_relatorios: number;
  relatorios_ativos: number;
  total_execucoes_mes: number;
  execucoes_hoje: number;
  tempo_medio_execucao: number;
  relatorios_mais_usados: Array<{
    nome: string;
    execucoes: number;
  }>;
  execucoes_por_tipo: Record<string, number>;
  status_execucoes: Record<string, number>;
  atividade_recente: Array<{
    tipo: string;
    relatorio: string;
    usuario: string;
    status: string;
    timestamp: string;
  }>;
}

export interface FiltroDisponivel {
  campo: string;
  tipo: 'texto' | 'numero' | 'data' | 'select' | 'boolean';
  label: string;
  obrigatorio?: boolean;
  opcoes?: Array<{ valor: any; texto: string }>;
  valor_padrao?: any;
  placeholder?: string;
  validacao?: {
    min?: number;
    max?: number;
    pattern?: string;
  };
}

export interface QueryBuilder {
  tabelas: string[];
  campos: Campo[];
  filtros: FiltroQuery[];
  agrupamentos: string[];
  ordenacao: OrdenacaoQuery[];
  limite?: number;
}

export interface Campo {
  tabela: string;
  campo: string;
  alias?: string;
  funcao?: 'COUNT' | 'SUM' | 'AVG' | 'MIN' | 'MAX';
}

export interface FiltroQuery {
  campo: string;
  operador: 'IGUAL' | 'DIFERENTE' | 'MAIOR' | 'MENOR' | 'MAIOR_IGUAL' | 'MENOR_IGUAL' | 'CONTEM' | 'INICIA' | 'TERMINA' | 'ENTRE' | 'IN' | 'NOT_IN' | 'IS_NULL' | 'IS_NOT_NULL';
  valor: any;
  valor2?: any; // Para operador ENTRE
  tipo_dado: 'texto' | 'numero' | 'data' | 'boolean';
}

export interface OrdenacaoQuery {
  campo: string;
  direcao: 'ASC' | 'DESC';
}

// === ENUMS ===

export enum TipoRelatorio {
  TABULAR = 'TABULAR',
  GRAFICO = 'GRAFICO',
  KPI = 'KPI',
  DASHBOARD = 'DASHBOARD',
  EXPORTACAO = 'EXPORTACAO'
}

export enum StatusRelatorio {
  ATIVO = 'ATIVO',
  INATIVO = 'INATIVO',
  RASCUNHO = 'RASCUNHO'
}

export enum StatusExecucao {
  PENDENTE = 'PENDENTE',
  EXECUTANDO = 'EXECUTANDO',
  CONCLUIDO = 'CONCLUIDO',
  ERRO = 'ERRO',
  CANCELADO = 'CANCELADO'
}

export enum FormatoExportacao {
  PDF = 'PDF',
  EXCEL = 'EXCEL',
  CSV = 'CSV',
  JSON = 'JSON'
}

export enum TipoVisualizacao {
  TABELA = 'TABELA',
  LINHA = 'LINHA',
  BARRA = 'BARRA',
  PIZZA = 'PIZZA',
  AREA = 'AREA',
  SCATTER = 'SCATTER',
  DONUT = 'DONUT',
  GAUGE = 'GAUGE',
  MAPA = 'MAPA'
}

export enum FrequenciaAgendamento {
  MINUTOS = 'MINUTOS',
  HORARIO = 'HORARIO',
  DIARIO = 'DIARIO',
  SEMANAL = 'SEMANAL',
  MENSAL = 'MENSAL',
  TRIMESTRAL = 'TRIMESTRAL',
  ANUAL = 'ANUAL',
  CUSTOMIZADO = 'CUSTOMIZADO'
}

export enum TipoWidget {
  RELATORIO = 'RELATORIO',
  METRICA = 'METRICA',
  GRAFICO = 'GRAFICO',
  TABELA = 'TABELA',
  KPI = 'KPI',
  MAPA = 'MAPA',
  CALENDARIO = 'CALENDARIO',
  FILTRO = 'FILTRO'
}

export enum NivelPermissao {
  PRIVADO = 'PRIVADO',
  EQUIPE = 'EQUIPE',
  EMPRESA = 'EMPRESA',
  PUBLICO = 'PUBLICO'
}

// === REQUESTS ===

export interface CreateRelatorioRequest {
  nome: string;
  descricao?: string;
  tipo: TipoRelatorio;
  categoria?: string;
  query_sql: string;
  configuracao_visual?: Record<string, any>;
  filtros_disponiveis?: FiltroDisponivel[];
  parametros_padrao?: Record<string, any>;
  cache_duracao?: number;
  timeout_execucao?: number;
  limite_registros?: number;
  tags?: string[];
  nivel_permissao?: NivelPermissao;
  publico?: boolean;
}

export interface UpdateRelatorioRequest {
  nome?: string;
  descricao?: string;
  categoria?: string;
  query_sql?: string;
  configuracao_visual?: Record<string, any>;
  filtros_disponiveis?: FiltroDisponivel[];
  parametros_padrao?: Record<string, any>;
  cache_duracao?: number;
  timeout_execucao?: number;
  limite_registros?: number;
  tags?: string[];
  nivel_permissao?: NivelPermissao;
  publico?: boolean;
  status?: StatusRelatorio;
}

export interface ExecutarRelatorioRequest {
  parametros?: Record<string, any>;
  filtros?: Record<string, any>;
  formato_exportacao?: FormatoExportacao;
  usar_cache?: boolean;
}

export interface CreateDashboardRequest {
  nome: string;
  descricao?: string;
  categoria?: string;
  layout_configuracao?: Record<string, any>;
  configuracao_tema?: Record<string, any>;
  auto_refresh?: boolean;
  intervalo_refresh?: number;
  publico?: boolean;
  nivel_permissao?: NivelPermissao;
  tags?: string[];
}

export interface CreateWidgetRequest {
  dashboard_id: number;
  nome: string;
  tipo: TipoWidget;
  descricao?: string;
  configuracao_relatorio_id?: number;
  query_customizada?: string;
  parametros?: Record<string, any>;
  posicao_x?: number;
  posicao_y?: number;
  largura?: number;
  altura?: number;
  configuracao_visual?: Record<string, any>;
  tipo_visualizacao?: TipoVisualizacao;
  auto_refresh?: boolean;
  intervalo_refresh?: number;
}

export interface CreateMetricaRequest {
  nome: string;
  codigo: string;
  descricao?: string;
  categoria?: string;
  formula_sql: string;
  unidade?: string;
  formato_exibicao?: string;
  meta_valor?: number;
  meta_tipo?: string;
  alerta_habilitado?: boolean;
  alerta_threshold?: number;
  frequencia_calculo?: FrequenciaAgendamento;
  periodo_analise?: string;
  manter_historico?: boolean;
  dias_historico?: number;
}

// === SERVIÇO PRINCIPAL ===

export class RelatoriosService {
  private readonly baseUrl = '/api/relatorios';

  // === CONFIGURAÇÕES DE RELATÓRIOS ===

  async criarConfiguracao(data: CreateRelatorioRequest): Promise<{ id: number; message: string }> {
    const response = await api.post(`${this.baseUrl}/configuracoes`, data);
    return response.data;
  }

  async listarConfiguracoes(params?: {
    tipo?: TipoRelatorio;
    status?: StatusRelatorio;
    categoria?: string;
    publico?: boolean;
    autor_id?: number;
    tags?: string;
    skip?: number;
    limit?: number;
  }): Promise<ConfiguracaoRelatorio[]> {
    const response = await api.get(`${this.baseUrl}/configuracoes`, { params });
    return response.data;
  }

  async obterConfiguracao(id: number): Promise<ConfiguracaoRelatorio> {
    const response = await api.get(`${this.baseUrl}/configuracoes/${id}`);
    return response.data;
  }

  async atualizarConfiguracao(id: number, data: UpdateRelatorioRequest): Promise<{ message: string }> {
    const response = await api.put(`${this.baseUrl}/configuracoes/${id}`, data);
    return response.data;
  }

  async deletarConfiguracao(id: number): Promise<{ message: string }> {
    const response = await api.delete(`${this.baseUrl}/configuracoes/${id}`);
    return response.data;
  }

  // === EXECUÇÃO DE RELATÓRIOS ===

  async executarRelatorio(id: number, data: ExecutarRelatorioRequest): Promise<{
    id: number;
    message: string;
    cache_hit: boolean;
    dados?: any[];
  }> {
    const response = await api.post(`${this.baseUrl}/configuracoes/${id}/executar`, data);
    return response.data;
  }

  async obterExecucao(id: number): Promise<ExecucaoRelatorio> {
    const response = await api.get(`${this.baseUrl}/execucoes/${id}`);
    return response.data;
  }

  async listarExecucoes(params?: {
    configuracao_id?: number;
    status?: StatusExecucao;
    skip?: number;
    limit?: number;
  }): Promise<ExecucaoRelatorio[]> {
    const response = await api.get(`${this.baseUrl}/execucoes`, { params });
    return response.data;
  }

  // === DASHBOARDS ===

  async criarDashboard(data: CreateDashboardRequest): Promise<{ id: number; message: string }> {
    const response = await api.post(`${this.baseUrl}/dashboards`, data);
    return response.data;
  }

  async listarDashboards(params?: {
    publico?: boolean;
    categoria?: string;
  }): Promise<DashboardExecutivo[]> {
    const response = await api.get(`${this.baseUrl}/dashboards`, { params });
    return response.data;
  }

  async obterDashboard(id: number): Promise<DashboardExecutivo> {
    const response = await api.get(`${this.baseUrl}/dashboards/${id}`);
    return response.data;
  }

  async atualizarDashboard(id: number, data: Partial<CreateDashboardRequest>): Promise<{ message: string }> {
    const response = await api.put(`${this.baseUrl}/dashboards/${id}`, data);
    return response.data;
  }

  async deletarDashboard(id: number): Promise<{ message: string }> {
    const response = await api.delete(`${this.baseUrl}/dashboards/${id}`);
    return response.data;
  }

  // === WIDGETS ===

  async criarWidget(data: CreateWidgetRequest): Promise<{ id: number; message: string }> {
    const response = await api.post(`${this.baseUrl}/widgets`, data);
    return response.data;
  }

  async listarWidgets(dashboardId: number): Promise<WidgetDashboard[]> {
    const response = await api.get(`${this.baseUrl}/dashboards/${dashboardId}/widgets`);
    return response.data;
  }

  async obterWidget(id: number): Promise<WidgetDashboard> {
    const response = await api.get(`${this.baseUrl}/widgets/${id}`);
    return response.data;
  }

  async atualizarWidget(id: number, data: Partial<CreateWidgetRequest>): Promise<{ message: string }> {
    const response = await api.put(`${this.baseUrl}/widgets/${id}`, data);
    return response.data;
  }

  async deletarWidget(id: number): Promise<{ message: string }> {
    const response = await api.delete(`${this.baseUrl}/widgets/${id}`);
    return response.data;
  }

  async executarWidget(id: number): Promise<any[]> {
    const response = await api.post(`${this.baseUrl}/widgets/${id}/executar`);
    return response.data;
  }

  // === MÉTRICAS ===

  async criarMetrica(data: CreateMetricaRequest): Promise<{ id: number; message: string }> {
    const response = await api.post(`${this.baseUrl}/metricas`, data);
    return response.data;
  }

  async listarMetricas(params?: {
    categoria?: string;
    ativo?: boolean;
  }): Promise<MetricaNegocio[]> {
    const response = await api.get(`${this.baseUrl}/metricas`, { params });
    return response.data;
  }

  async obterMetrica(id: number): Promise<MetricaNegocio> {
    const response = await api.get(`${this.baseUrl}/metricas/${id}`);
    return response.data;
  }

  async atualizarMetrica(id: number, data: Partial<CreateMetricaRequest>): Promise<{ message: string }> {
    const response = await api.put(`${this.baseUrl}/metricas/${id}`, data);
    return response.data;
  }

  async deletarMetrica(id: number): Promise<{ message: string }> {
    const response = await api.delete(`${this.baseUrl}/metricas/${id}`);
    return response.data;
  }

  async calcularMetrica(id: number, dataReferencia?: string): Promise<{
    metrica_id: number;
    valor: number;
    unidade?: string;
    meta_valor?: number;
    meta_atingida?: boolean;
    data_referencia: string;
    calculado_em: string;
  }> {
    const params = dataReferencia ? { data_referencia: dataReferencia } : {};
    const response = await api.get(`${this.baseUrl}/metricas/calcular/${id}`, { params });
    return response.data;
  }

  async obterHistoricoMetrica(id: number, params?: {
    data_inicio?: string;
    data_fim?: string;
    limit?: number;
  }): Promise<Array<{
    data_referencia: string;
    valor: number;
    meta_atingida?: boolean;
  }>> {
    const response = await api.get(`${this.baseUrl}/metricas/${id}/historico`, { params });
    return response.data;
  }

  // === DASHBOARD PRINCIPAL ===

  async obterDashboardPrincipal(): Promise<DashboardRelatorios> {
    const response = await api.get(`${this.baseUrl}/dashboard`);
    return response.data;
  }

  // === INICIALIZAÇÃO ===

  async inicializarTemplates(): Promise<{ message: string; templates_criados: number }> {
    const response = await api.post(`${this.baseUrl}/inicializar-templates`);
    return response.data;
  }

  async inicializarKpis(): Promise<{ message: string; kpis_criados: number }> {
    const response = await api.post(`${this.baseUrl}/inicializar-kpis`);
    return response.data;
  }

  // === QUERY BUILDER ===

  gerarQuerySql(queryBuilder: QueryBuilder): string {
    let sql = 'SELECT ';
    
    // Campos
    const campos = queryBuilder.campos.map(campo => {
      let campoSql = `${campo.tabela}.${campo.campo}`;
      if (campo.funcao) {
        campoSql = `${campo.funcao}(${campoSql})`;
      }
      if (campo.alias) {
        campoSql += ` AS ${campo.alias}`;
      }
      return campoSql;
    });
    
    sql += campos.join(', ');
    
    // FROM
    sql += ` FROM ${queryBuilder.tabelas.join(', ')}`;
    
    // WHERE
    if (queryBuilder.filtros.length > 0) {
      const condicoes = queryBuilder.filtros.map(filtro => {
        return this.gerarCondicaoFiltro(filtro);
      });
      sql += ` WHERE ${condicoes.join(' AND ')}`;
    }
    
    // GROUP BY
    if (queryBuilder.agrupamentos.length > 0) {
      sql += ` GROUP BY ${queryBuilder.agrupamentos.join(', ')}`;
    }
    
    // ORDER BY
    if (queryBuilder.ordenacao.length > 0) {
      const ordenacao = queryBuilder.ordenacao.map(ord => 
        `${ord.campo} ${ord.direcao}`
      );
      sql += ` ORDER BY ${ordenacao.join(', ')}`;
    }
    
    // LIMIT
    if (queryBuilder.limite) {
      sql += ` LIMIT ${queryBuilder.limite}`;
    }
    
    return sql;
  }

  private gerarCondicaoFiltro(filtro: FiltroQuery): string {
    const { campo, operador, valor, valor2, tipo_dado } = filtro;
    
    switch (operador) {
      case 'IGUAL':
        return `${campo} = ${this.formatarValor(valor, tipo_dado)}`;
      case 'DIFERENTE':
        return `${campo} != ${this.formatarValor(valor, tipo_dado)}`;
      case 'MAIOR':
        return `${campo} > ${this.formatarValor(valor, tipo_dado)}`;
      case 'MENOR':
        return `${campo} < ${this.formatarValor(valor, tipo_dado)}`;
      case 'MAIOR_IGUAL':
        return `${campo} >= ${this.formatarValor(valor, tipo_dado)}`;
      case 'MENOR_IGUAL':
        return `${campo} <= ${this.formatarValor(valor, tipo_dado)}`;
      case 'CONTEM':
        return `${campo} LIKE '%${valor}%'`;
      case 'INICIA':
        return `${campo} LIKE '${valor}%'`;
      case 'TERMINA':
        return `${campo} LIKE '%${valor}'`;
      case 'ENTRE':
        return `${campo} BETWEEN ${this.formatarValor(valor, tipo_dado)} AND ${this.formatarValor(valor2, tipo_dado)}`;
      case 'IN':
        const valores = Array.isArray(valor) ? valor : [valor];
        const valoresFormatados = valores.map(v => this.formatarValor(v, tipo_dado));
        return `${campo} IN (${valoresFormatados.join(', ')})`;
      case 'NOT_IN':
        const valoresNot = Array.isArray(valor) ? valor : [valor];
        const valoresNotFormatados = valoresNot.map(v => this.formatarValor(v, tipo_dado));
        return `${campo} NOT IN (${valoresNotFormatados.join(', ')})`;
      case 'IS_NULL':
        return `${campo} IS NULL`;
      case 'IS_NOT_NULL':
        return `${campo} IS NOT NULL`;
      default:
        return `${campo} = ${this.formatarValor(valor, tipo_dado)}`;
    }
  }

  private formatarValor(valor: any, tipoDado: string): string {
    if (valor === null || valor === undefined) {
      return 'NULL';
    }
    
    switch (tipoDado) {
      case 'texto':
        return `'${valor.toString().replace(/'/g, "''")}'`;
      case 'numero':
        return valor.toString();
      case 'data':
        return `'${valor}'`;
      case 'boolean':
        return valor ? 'TRUE' : 'FALSE';
      default:
        return `'${valor}'`;
    }
  }

  // === VALIDAÇÕES ===

  validarQuery(query: string): { valida: boolean; erros: string[] } {
    const erros: string[] = [];
    const queryUpper = query.toUpperCase().trim();
    
    // Verificar comandos proibidos
    const comandosProibidos = [
      'DROP', 'DELETE', 'INSERT', 'UPDATE', 'ALTER', 'CREATE',
      'TRUNCATE', 'GRANT', 'REVOKE', 'EXEC', 'EXECUTE'
    ];
    
    for (const comando of comandosProibidos) {
      if (queryUpper.includes(comando)) {
        erros.push(`Comando '${comando}' não é permitido`);
      }
    }
    
    // Verificar se é uma query SELECT
    if (!queryUpper.startsWith('SELECT')) {
      erros.push('Apenas queries SELECT são permitidas');
    }
    
    // Verificar sintaxe básica
    if (!queryUpper.includes('FROM')) {
      erros.push('Query deve conter cláusula FROM');
    }
    
    return {
      valida: erros.length === 0,
      erros
    };
  }

  // === UTILITÁRIOS ===

  formatarValorMetrica(valor: number, formato?: string, unidade?: string): string {
    let valorFormatado = valor.toString();
    
    if (formato) {
      switch (formato) {
        case 'moeda':
          valorFormatado = new Intl.NumberFormat('pt-BR', {
            style: 'currency',
            currency: 'BRL'
          }).format(valor);
          break;
        case 'percentual':
          valorFormatado = new Intl.NumberFormat('pt-BR', {
            style: 'percent',
            minimumFractionDigits: 2
          }).format(valor / 100);
          break;
        case 'decimal':
          valorFormatado = new Intl.NumberFormat('pt-BR', {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
          }).format(valor);
          break;
        case 'inteiro':
          valorFormatado = new Intl.NumberFormat('pt-BR', {
            maximumFractionDigits: 0
          }).format(valor);
          break;
      }
    }
    
    if (unidade) {
      valorFormatado += ` ${unidade}`;
    }
    
    return valorFormatado;
  }

  obterCorStatusExecucao(status: StatusExecucao): string {
    switch (status) {
      case StatusExecucao.PENDENTE:
        return '#fbbf24'; // amarelo
      case StatusExecucao.EXECUTANDO:
        return '#3b82f6'; // azul
      case StatusExecucao.CONCLUIDO:
        return '#10b981'; // verde
      case StatusExecucao.ERRO:
        return '#ef4444'; // vermelho
      case StatusExecucao.CANCELADO:
        return '#6b7280'; // cinza
      default:
        return '#6b7280';
    }
  }

  obterIconeTipoRelatorio(tipo: TipoRelatorio): string {
    switch (tipo) {
      case TipoRelatorio.TABULAR:
        return 'table';
      case TipoRelatorio.GRAFICO:
        return 'chart-bar';
      case TipoRelatorio.KPI:
        return 'speedometer';
      case TipoRelatorio.DASHBOARD:
        return 'dashboard';
      case TipoRelatorio.EXPORTACAO:
        return 'download';
      default:
        return 'document';
    }
  }

  exportarConfiguracaoJson(configuracao: ConfiguracaoRelatorio): string {
    const config = {
      nome: configuracao.nome,
      descricao: configuracao.descricao,
      tipo: configuracao.tipo,
      categoria: configuracao.categoria,
      query_sql: configuracao.query_sql,
      configuracao_visual: configuracao.configuracao_visual,
      filtros_disponiveis: configuracao.filtros_disponiveis,
      parametros_padrao: configuracao.parametros_padrao,
      tags: configuracao.tags
    };
    
    return JSON.stringify(config, null, 2);
  }

  importarConfiguracaoJson(json: string): CreateRelatorioRequest {
    try {
      const config = JSON.parse(json);
      return {
        nome: config.nome,
        descricao: config.descricao,
        tipo: config.tipo,
        categoria: config.categoria,
        query_sql: config.query_sql,
        configuracao_visual: config.configuracao_visual || {},
        filtros_disponiveis: config.filtros_disponiveis || [],
        parametros_padrao: config.parametros_padrao || {},
        tags: config.tags || []
      };
    } catch (error) {
      throw new Error('JSON inválido para importação');
    }
  }
}

export const relatoriosService = new RelatoriosService();
