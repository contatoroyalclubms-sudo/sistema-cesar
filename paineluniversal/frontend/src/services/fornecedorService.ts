/*
Serviço TypeScript para gestão de fornecedores
Comunicação com API e formatação de dados
*/

import { api } from '../api/api'

// ================================================================================
// INTERFACES E TYPES
// ================================================================================

export interface Fornecedor {
  id: number
  empresa_id: number
  nome: string
  tipo_pessoa: 'fisica' | 'juridica'
  documento: string
  email?: string
  telefone?: string
  endereco?: string
  cidade?: string
  estado?: string
  cep?: string
  tipo_fornecedor: TipoFornecedor
  status: StatusFornecedor
  observacoes?: string
  prazo_pagamento?: number
  limite_credito?: number
  pessoa_contato?: string
  site?: string
  avaliacao_media?: number
  ultima_avaliacao?: string
  criado_em: string
  atualizado_em?: string
  criado_por_id: number
}

export interface ProdutoFornecedor {
  id: number
  fornecedor_id: number
  produto_id: number
  codigo_fornecedor?: string
  preco_compra: number
  prazo_entrega?: number
  quantidade_minima?: number
  observacoes?: string
  preferencial: boolean
  ativo: boolean
  criado_em: string
  atualizado_em?: string
  criado_por_id: number
}

export interface CotacaoFornecedor {
  fornecedor: Fornecedor
  produto_fornecedor: ProdutoFornecedor
  economia: number
}

export interface PerformanceFornecedor {
  fornecedor_id: number
  nome: string
  total_compras: number
  valor_total: number
  atraso_medio_dias: number
  pontualidade_percentual: number
  classificacao: 'Excelente' | 'Bom' | 'Regular' | 'Ruim'
}

export interface DashboardFornecedores {
  total_fornecedores: number
  fornecedores_ativos: number
  compras_ultimo_mes: number
  top_fornecedores: Array<{
    nome: string
    valor: number
  }>
  distribuicao_tipos: Array<{
    tipo: TipoFornecedor
    quantidade: number
  }>
}

export interface AvaliacaoFornecedor {
  qualidade_produto: number
  prazo_entrega: number
  atendimento: number
  preco: number
  observacoes?: string
}

export interface FiltrosFornecedor {
  nome?: string
  tipo_fornecedor?: TipoFornecedor
  status?: StatusFornecedor
  cidade?: string
}

export enum TipoFornecedor {
  MATERIAL = 'material',
  SERVICO = 'servico',
  EQUIPAMENTO = 'equipamento',
  INSUMO = 'insumo',
  TERCEIRIZADO = 'terceirizado'
}

export enum StatusFornecedor {
  ATIVO = 'ativo',
  INATIVO = 'inativo',
  BLOQUEADO = 'bloqueado',
  PENDENTE = 'pendente'
}

// ================================================================================
// SERVIÇO PRINCIPAL
// ================================================================================

export class FornecedorService {
  private static readonly BASE_URL = '/fornecedores'

  // CRUD Básico
  static async criarFornecedor(dados: Omit<Fornecedor, 'id' | 'empresa_id' | 'criado_em' | 'criado_por_id'>): Promise<{ id: number; message: string }> {
    const response = await api.post(`${this.BASE_URL}/`, dados)
    return response.data
  }

  static async listarFornecedores(
    page: number = 1,
    size: number = 20,
    filtros?: FiltrosFornecedor
  ): Promise<{
    itens: Fornecedor[]
    total: number
    page: number
    size: number
    pages: number
  }> {
    const params = new URLSearchParams({
      page: page.toString(),
      size: size.toString(),
      ...filtros
    })

    const response = await api.get(`${this.BASE_URL}/?${params}`)
    return response.data
  }

  static async obterFornecedor(fornecedorId: number): Promise<{
    fornecedor: Fornecedor
    produtos: Array<{
      produto_fornecedor: ProdutoFornecedor
      produto: any
    }>
    estatisticas: {
      total_compras: number
      valor_total_compras: number
      ultima_compra?: string
      quantidade_produtos: number
    }
  }> {
    const response = await api.get(`${this.BASE_URL}/${fornecedorId}`)
    return response.data
  }

  static async atualizarFornecedor(
    fornecedorId: number, 
    dados: Partial<Fornecedor>
  ): Promise<{ message: string }> {
    const response = await api.patch(`${this.BASE_URL}/${fornecedorId}`, dados)
    return response.data
  }

  static async excluirFornecedor(fornecedorId: number): Promise<{ message: string }> {
    const response = await api.delete(`${this.BASE_URL}/${fornecedorId}`)
    return response.data
  }

  // Gestão de Produtos
  static async adicionarProdutoFornecedor(
    fornecedorId: number,
    dados: Omit<ProdutoFornecedor, 'id' | 'fornecedor_id' | 'criado_em' | 'criado_por_id'>
  ): Promise<{ message: string }> {
    const response = await api.post(`${this.BASE_URL}/${fornecedorId}/produtos`, dados)
    return response.data
  }

  static async listarProdutosFornecedor(
    fornecedorId: number,
    ativo?: boolean
  ): Promise<Array<{
    produto_fornecedor: ProdutoFornecedor
    produto: any
  }>> {
    const params = ativo !== undefined ? `?ativo=${ativo}` : ''
    const response = await api.get(`${this.BASE_URL}/${fornecedorId}/produtos${params}`)
    return response.data
  }

  static async atualizarProdutoFornecedor(
    fornecedorId: number,
    produtoId: number,
    dados: Partial<ProdutoFornecedor>
  ): Promise<{ message: string }> {
    const response = await api.patch(`${this.BASE_URL}/${fornecedorId}/produtos/${produtoId}`, dados)
    return response.data
  }

  // Cotações e Comparações
  static async obterCotacoesProduto(produtoId: number): Promise<CotacaoFornecedor[]> {
    const response = await api.get(`${this.BASE_URL}/cotacao/produto/${produtoId}`)
    return response.data
  }

  static async obterMelhorPreco(produtoId: number): Promise<{
    fornecedor: Fornecedor
    produto_fornecedor: ProdutoFornecedor
  }> {
    const response = await api.get(`${this.BASE_URL}/melhor-preco/produto/${produtoId}`)
    return response.data
  }

  // Performance e Avaliações
  static async obterPerformanceFornecedores(periodoDias: number = 30): Promise<PerformanceFornecedor[]> {
    const response = await api.get(`${this.BASE_URL}/performance?periodo_dias=${periodoDias}`)
    return response.data
  }

  static async avaliarFornecedor(
    fornecedorId: number,
    avaliacao: AvaliacaoFornecedor
  ): Promise<{ message: string; media_geral: number }> {
    const response = await api.post(`${this.BASE_URL}/${fornecedorId}/avaliar`, avaliacao)
    return response.data
  }

  // Dashboard
  static async obterDashboard(): Promise<DashboardFornecedores> {
    const response = await api.get(`${this.BASE_URL}/dashboard/resumo`)
    return response.data
  }
}

// ================================================================================
// UTILITÁRIOS E FORMATAÇÃO
// ================================================================================

export const formatarDocumento = (documento: string, tipo: 'fisica' | 'juridica'): string => {
  const apenasNumeros = documento.replace(/\D/g, '')
  
  if (tipo === 'fisica' && apenasNumeros.length === 11) {
    // CPF: 000.000.000-00
    return apenasNumeros.replace(/(\d{3})(\d{3})(\d{3})(\d{2})/, '$1.$2.$3-$4')
  } else if (tipo === 'juridica' && apenasNumeros.length === 14) {
    // CNPJ: 00.000.000/0000-00
    return apenasNumeros.replace(/(\d{2})(\d{3})(\d{3})(\d{4})(\d{2})/, '$1.$2.$3/$4-$5')
  }
  
  return documento
}

export const validarDocumento = (documento: string, tipo: 'fisica' | 'juridica'): boolean => {
  const apenasNumeros = documento.replace(/\D/g, '')
  
  if (tipo === 'fisica') {
    return apenasNumeros.length === 11
  } else if (tipo === 'juridica') {
    return apenasNumeros.length === 14
  }
  
  return false
}

export const formatarValorMonetario = (valor: number): string => {
  return new Intl.NumberFormat('pt-BR', {
    style: 'currency',
    currency: 'BRL'
  }).format(valor)
}

export const formatarTelefone = (telefone: string): string => {
  const apenasNumeros = telefone.replace(/\D/g, '')
  
  if (apenasNumeros.length === 11) {
    // Celular: (00) 00000-0000
    return apenasNumeros.replace(/(\d{2})(\d{5})(\d{4})/, '($1) $2-$3')
  } else if (apenasNumeros.length === 10) {
    // Fixo: (00) 0000-0000
    return apenasNumeros.replace(/(\d{2})(\d{4})(\d{4})/, '($1) $2-$3')
  }
  
  return telefone
}

export const obterCorStatusFornecedor = (status: StatusFornecedor): string => {
  const cores = {
    [StatusFornecedor.ATIVO]: '#4caf50',
    [StatusFornecedor.INATIVO]: '#9e9e9e',
    [StatusFornecedor.BLOQUEADO]: '#f44336',
    [StatusFornecedor.PENDENTE]: '#ff9800'
  }
  
  return cores[status] || '#9e9e9e'
}

export const obterCorClassificacao = (classificacao: string): string => {
  const cores = {
    'Excelente': '#4caf50',
    'Bom': '#8bc34a',
    'Regular': '#ff9800',
    'Ruim': '#f44336'
  }
  
  return cores[classificacao] || '#9e9e9e'
}

export const calcularIdadeFornecedor = (criadoEm: string): number => {
  const criacao = new Date(criadoEm)
  const agora = new Date()
  const diferenca = agora.getTime() - criacao.getTime()
  return Math.floor(diferenca / (1000 * 60 * 60 * 24)) // dias
}

export const formatarPrazoEntrega = (prazo?: number): string => {
  if (!prazo) return 'Não informado'
  
  if (prazo === 1) return '1 dia'
  if (prazo < 7) return `${prazo} dias`
  if (prazo === 7) return '1 semana'
  if (prazo < 30) return `${Math.floor(prazo / 7)} semanas`
  if (prazo === 30) return '1 mês'
  return `${Math.floor(prazo / 30)} meses`
}

export const gerarRelatorioPerformance = (performance: PerformanceFornecedor[]): string => {
  let relatorio = 'RELATÓRIO DE PERFORMANCE DOS FORNECEDORES\n'
  relatorio += '================================================\n\n'
  
  performance.forEach((p, index) => {
    relatorio += `${index + 1}. ${p.nome}\n`
    relatorio += `   Compras: ${p.total_compras}\n`
    relatorio += `   Valor Total: ${formatarValorMonetario(p.valor_total)}\n`
    relatorio += `   Pontualidade: ${p.pontualidade_percentual.toFixed(1)}%\n`
    relatorio += `   Atraso Médio: ${p.atraso_medio_dias.toFixed(1)} dias\n`
    relatorio += `   Classificação: ${p.classificacao}\n\n`
  })
  
  return relatorio
}

// Constantes
export const TIPOS_FORNECEDOR_LABELS = {
  [TipoFornecedor.MATERIAL]: 'Material',
  [TipoFornecedor.SERVICO]: 'Serviço',
  [TipoFornecedor.EQUIPAMENTO]: 'Equipamento',
  [TipoFornecedor.INSUMO]: 'Insumo',
  [TipoFornecedor.TERCEIRIZADO]: 'Terceirizado'
}

export const STATUS_FORNECEDOR_LABELS = {
  [StatusFornecedor.ATIVO]: 'Ativo',
  [StatusFornecedor.INATIVO]: 'Inativo',
  [StatusFornecedor.BLOQUEADO]: 'Bloqueado',
  [StatusFornecedor.PENDENTE]: 'Pendente'
}
