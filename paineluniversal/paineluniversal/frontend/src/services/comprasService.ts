/*
Serviço TypeScript para gestão de compras e ordens de compra
Comunicação com API e formatação de dados
*/

import { api } from './api'

// ================================================================================
// INTERFACES E TYPES
// ================================================================================

export interface OrdemCompra {
  id: number
  empresa_id: number
  fornecedor_id: number
  numero_ordem: string
  data_pedido: string
  data_entrega_prevista: string
  data_entrega_real?: string
  data_aprovacao?: string
  valor_total: number
  status: StatusOrdemCompra
  observacoes?: string
  observacoes_aprovacao?: string
  criado_por_id: number
  aprovado_por_id?: number
  criado_em: string
  atualizado_em?: string
}

export interface ItemOrdemCompra {
  id: number
  ordem_compra_id: number
  produto_id: number
  quantidade: number
  preco_unitario: number
  valor_total: number
  observacoes?: string
}

export interface RecebimentoMercadoria {
  id: number
  empresa_id: number
  ordem_compra_id: number
  numero_recebimento: string
  data_recebimento: string
  numero_nota_fiscal?: string
  valor_frete?: number
  status: StatusRecebimento
  observacoes?: string
  criado_por_id: number
  criado_em: string
  atualizado_em?: string
}

export interface ItemRecebimento {
  id: number
  recebimento_id: number
  item_ordem_compra_id: number
  quantidade_recebida: number
  preco_unitario_real?: number
  qualidade_aprovada: boolean
  observacoes_qualidade?: string
}

export interface SugestaoCompra {
  produto: any
  estoque_atual: number
  estoque_minimo: number
  fornecedor: any
  produto_fornecedor: any
  quantidade_sugerida: number
  valor_estimado: number
}

export interface DashboardCompras {
  total_ordens: number
  ordens_pendentes: number
  compras_mes: number
  status_distribuicao: Array<{
    status: StatusOrdemCompra
    quantidade: number
  }>
  top_fornecedores: Array<{
    nome: string
    valor: number
    quantidade_ordens: number
  }>
}

export interface ItemCompraCreate {
  produto_id: number
  quantidade: number
  preco_unitario: number
  observacoes?: string
}

export interface OrdemCompraCreate {
  fornecedor_id: number
  data_entrega_prevista: string
  observacoes?: string
  itens: ItemCompraCreate[]
}

export interface ItemRecebimentoCreate {
  item_ordem_compra_id: number
  quantidade_recebida: number
  preco_unitario_real?: number
  qualidade_aprovada: boolean
  observacoes_qualidade?: string
}

export interface RecebimentoCreate {
  ordem_compra_id: number
  data_recebimento: string
  numero_nota_fiscal?: string
  valor_frete?: number
  observacoes?: string
  itens: ItemRecebimentoCreate[]
}

export interface FiltrosCompra {
  status?: StatusOrdemCompra
  fornecedor_id?: number
  data_inicio?: string
  data_fim?: string
}

export enum StatusOrdemCompra {
  PENDENTE = 'pendente',
  APROVADA = 'aprovada',
  FINALIZADA = 'finalizada',
  CANCELADA = 'cancelada'
}

export enum StatusRecebimento {
  PENDENTE = 'pendente',
  CONCLUIDO = 'concluido',
  CANCELADO = 'cancelado'
}

// ================================================================================
// SERVIÇO PRINCIPAL
// ================================================================================

export class ComprasService {
  private static readonly BASE_URL = '/compras'

  // CRUD de Ordens de Compra
  static async criarOrdemCompra(dados: OrdemCompraCreate): Promise<{
    id: number
    numero_ordem: string
    message: string
  }> {
    const response = await api.post(`${this.BASE_URL}/`, dados)
    return response.data
  }

  static async listarOrdensCompra(
    page: number = 1,
    size: number = 20,
    filtros?: FiltrosCompra
  ): Promise<{
    itens: Array<{
      ordem: OrdemCompra
      fornecedor: any
    }>
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

  static async obterOrdemCompra(ordemId: number): Promise<{
    ordem: OrdemCompra
    fornecedor: any
    itens: Array<{
      item: ItemOrdemCompra
      produto: any
    }>
    recebimentos: RecebimentoMercadoria[]
  }> {
    const response = await api.get(`${this.BASE_URL}/${ordemId}`)
    return response.data
  }

  static async atualizarOrdemCompra(
    ordemId: number,
    dados: Partial<OrdemCompra>
  ): Promise<{ message: string }> {
    const response = await api.patch(`${this.BASE_URL}/${ordemId}`, dados)
    return response.data
  }

  static async excluirOrdemCompra(ordemId: number): Promise<{ message: string }> {
    const response = await api.delete(`${this.BASE_URL}/${ordemId}`)
    return response.data
  }

  // Workflow de Aprovação
  static async aprovarOrdemCompra(
    ordemId: number,
    observacoes?: string
  ): Promise<{ message: string }> {
    const response = await api.post(`${this.BASE_URL}/${ordemId}/aprovar`, {
      observacoes_aprovacao: observacoes
    })
    return response.data
  }

  static async rejeitarOrdemCompra(
    ordemId: number,
    observacoes?: string
  ): Promise<{ message: string }> {
    const response = await api.post(`${this.BASE_URL}/${ordemId}/rejeitar`, {
      observacoes_aprovacao: observacoes
    })
    return response.data
  }

  // Recebimento de Mercadorias
  static async criarRecebimento(
    ordemId: number,
    dados: RecebimentoCreate
  ): Promise<{
    id: number
    numero_recebimento: string
    message: string
  }> {
    const response = await api.post(`${this.BASE_URL}/${ordemId}/recebimentos`, dados)
    return response.data
  }

  static async listarRecebimentos(ordemId: number): Promise<RecebimentoMercadoria[]> {
    const response = await api.get(`${this.BASE_URL}/${ordemId}/recebimentos`)
    return response.data
  }

  // Sugestões e Dashboard
  static async obterSugestoesCompra(): Promise<SugestaoCompra[]> {
    const response = await api.get(`${this.BASE_URL}/sugestoes/automaticas`)
    return response.data
  }

  static async obterDashboardCompras(): Promise<DashboardCompras> {
    const response = await api.get(`${this.BASE_URL}/dashboard/resumo`)
    return response.data
  }
}

// ================================================================================
// UTILITÁRIOS E FORMATAÇÃO
// ================================================================================

export const formatarValorMonetario = (valor: number): string => {
  return new Intl.NumberFormat('pt-BR', {
    style: 'currency',
    currency: 'BRL'
  }).format(valor)
}

export const formatarData = (data: string): string => {
  return new Date(data).toLocaleDateString('pt-BR')
}

export const formatarDataHora = (data: string): string => {
  return new Date(data).toLocaleString('pt-BR')
}

export const obterCorStatusOrdem = (status: StatusOrdemCompra): string => {
  const cores = {
    [StatusOrdemCompra.PENDENTE]: '#ff9800',
    [StatusOrdemCompra.APROVADA]: '#2196f3',
    [StatusOrdemCompra.FINALIZADA]: '#4caf50',
    [StatusOrdemCompra.CANCELADA]: '#f44336'
  }
  
  return cores[status] || '#9e9e9e'
}

export const obterCorStatusRecebimento = (status: StatusRecebimento): string => {
  const cores = {
    [StatusRecebimento.PENDENTE]: '#ff9800',
    [StatusRecebimento.CONCLUIDO]: '#4caf50',
    [StatusRecebimento.CANCELADO]: '#f44336'
  }
  
  return cores[status] || '#9e9e9e'
}

export const calcularTotalItens = (itens: ItemCompraCreate[]): number => {
  return itens.reduce((total, item) => total + (item.quantidade * item.preco_unitario), 0)
}

export const calcularDiasAtraso = (dataEntregaPrevista: string, dataEntregaReal?: string): number => {
  const prevista = new Date(dataEntregaPrevista)
  const real = dataEntregaReal ? new Date(dataEntregaReal) : new Date()
  
  const diffTime = real.getTime() - prevista.getTime()
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
  
  return Math.max(0, diffDays)
}

export const obterIconeStatus = (status: StatusOrdemCompra): string => {
  const icones = {
    [StatusOrdemCompra.PENDENTE]: 'pending',
    [StatusOrdemCompra.APROVADA]: 'approved',
    [StatusOrdemCompra.FINALIZADA]: 'check_circle',
    [StatusOrdemCompra.CANCELADA]: 'cancel'
  }
  
  return icones[status] || 'help'
}

export const validarOrdemCompra = (ordem: OrdemCompraCreate): string[] => {
  const erros: string[] = []
  
  if (!ordem.fornecedor_id) {
    erros.push('Fornecedor é obrigatório')
  }
  
  if (!ordem.data_entrega_prevista) {
    erros.push('Data de entrega prevista é obrigatória')
  }
  
  if (!ordem.itens || ordem.itens.length === 0) {
    erros.push('Ordem deve ter pelo menos um item')
  }
  
  ordem.itens?.forEach((item, index) => {
    if (!item.produto_id) {
      erros.push(`Item ${index + 1}: Produto é obrigatório`)
    }
    if (!item.quantidade || item.quantidade <= 0) {
      erros.push(`Item ${index + 1}: Quantidade deve ser maior que zero`)
    }
    if (!item.preco_unitario || item.preco_unitario <= 0) {
      erros.push(`Item ${index + 1}: Preço unitário deve ser maior que zero`)
    }
  })
  
  return erros
}

export const gerarRelatorioCompras = (ordens: OrdemCompra[]): string => {
  let relatorio = 'RELATÓRIO DE COMPRAS\n'
  relatorio += '===================\n\n'
  
  const totalGeral = ordens.reduce((total, ordem) => total + ordem.valor_total, 0)
  
  relatorio += `Total de Ordens: ${ordens.length}\n`
  relatorio += `Valor Total: ${formatarValorMonetario(totalGeral)}\n\n`
  
  // Agrupar por status
  const porStatus = ordens.reduce((acc, ordem) => {
    if (!acc[ordem.status]) {
      acc[ordem.status] = { quantidade: 0, valor: 0 }
    }
    acc[ordem.status].quantidade++
    acc[ordem.status].valor += ordem.valor_total
    return acc
  }, {} as Record<string, { quantidade: number; valor: number }>)
  
  relatorio += 'POR STATUS:\n'
  Object.entries(porStatus).forEach(([status, dados]) => {
    relatorio += `${status.toUpperCase()}: ${dados.quantidade} ordens - ${formatarValorMonetario(dados.valor)}\n`
  })
  
  relatorio += '\nDETALHES:\n'
  ordens.forEach((ordem, index) => {
    relatorio += `${index + 1}. ${ordem.numero_ordem}\n`
    relatorio += `   Data: ${formatarData(ordem.data_pedido)}\n`
    relatorio += `   Valor: ${formatarValorMonetario(ordem.valor_total)}\n`
    relatorio += `   Status: ${ordem.status}\n\n`
  })
  
  return relatorio
}

// Constantes
export const STATUS_ORDEM_LABELS = {
  [StatusOrdemCompra.PENDENTE]: 'Pendente',
  [StatusOrdemCompra.APROVADA]: 'Aprovada',
  [StatusOrdemCompra.FINALIZADA]: 'Finalizada',
  [StatusOrdemCompra.CANCELADA]: 'Cancelada'
}

export const STATUS_RECEBIMENTO_LABELS = {
  [StatusRecebimento.PENDENTE]: 'Pendente',
  [StatusRecebimento.CONCLUIDO]: 'Concluído',
  [StatusRecebimento.CANCELADO]: 'Cancelado'
}

export const PRIORIDADES_URGENCIA = [
  { value: 'baixa', label: 'Baixa', color: '#4caf50' },
  { value: 'media', label: 'Média', color: '#ff9800' },
  { value: 'alta', label: 'Alta', color: '#f44336' },
  { value: 'critica', label: 'Crítica', color: '#9c27b0' }
]
