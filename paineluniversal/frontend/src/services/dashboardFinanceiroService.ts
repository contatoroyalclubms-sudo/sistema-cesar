import { api } from './api';

export interface KPIResumo {
  vendas_totais: number;
  ticket_medio: number;
  quantidade_vendas: number;
  produtos_vendidos: number;
  crescimento_percentual: number;
}

export interface VendaPeriodo {
  periodo: string;
  vendas_brutas: number;
  vendas_liquidas: number;
  quantidade_vendas: number;
  ticket_medio: number;
  crescimento: number | null;
}

export interface ProdutoPerformance {
  produto_id: number;
  nome: string;
  categoria: string | null;
  quantidade_vendida: number;
  valor_total: number;
  ticket_medio: number;
  margem_percentual: number | null;
  ranking: number;
}

export interface FormaPagamentoAnalise {
  forma_pagamento: string;
  valor_total: number;
  quantidade_transacoes: number;
  percentual_total: number;
  ticket_medio: number;
}

export interface MetricasTempoReal {
  vendas_hoje: {
    total_vendas: number;
    valor_total: number;
    ticket_medio: number;
  };
  vendas_por_hora: Array<{
    hora: string;
    vendas: number;
    valor: number;
  }>;
  sistema_cashless: {
    cartoes_ativos: number;
    saldo_total_sistema: number;
  };
  ultima_atualizacao: string;
}

export interface DashboardFiltros {
  data_inicio?: string;
  data_fim?: string;
  evento_id?: number;
  empresa_id?: number;
  granularidade?: 'dia' | 'semana' | 'mes';
  limite?: number;
  ordenar_por?: 'valor_total' | 'quantidade' | 'ticket_medio';
}

class DashboardFinanceiroService {
  private readonly baseURL = '/api/v1/dashboard-financeiro';

  async obterResumo(filtros: DashboardFiltros = {}): Promise<{
    periodo: { data_inicio: string; data_fim: string };
    kpis: KPIResumo;
    comparacao_periodo_anterior: { vendas_anteriores: number; crescimento: number };
  }> {
    const response = await api.get(`${this.baseURL}/resumo`, { params: filtros });
    return response.data;
  }

  async obterVendasPorPeriodo(filtros: DashboardFiltros = {}): Promise<VendaPeriodo[]> {
    const response = await api.get(`${this.baseURL}/vendas-periodo`, { params: filtros });
    return response.data;
  }

  async obterProdutosPerformance(filtros: DashboardFiltros = {}): Promise<ProdutoPerformance[]> {
    const response = await api.get(`${this.baseURL}/produtos-performance`, { params: filtros });
    return response.data;
  }

  async obterFormasPagamento(filtros: DashboardFiltros = {}): Promise<FormaPagamentoAnalise[]> {
    const response = await api.get(`${this.baseURL}/formas-pagamento`, { params: filtros });
    return response.data;
  }

  async obterMetricasTempoReal(eventoId?: number): Promise<MetricasTempoReal> {
    const params = eventoId ? { evento_id: eventoId } : {};
    const response = await api.get(`${this.baseURL}/metricas-tempo-real`, { params });
    return response.data;
  }

  // Utilidades para formatação
  formatarMoeda(valor: number): string {
    return new Intl.NumberFormat('pt-BR', { 
      style: 'currency', 
      currency: 'BRL' 
    }).format(valor);
  }

  formatarNumero(valor: number): string {
    return new Intl.NumberFormat('pt-BR').format(valor);
  }

  formatarPercentual(valor: number): string {
    return `${valor.toFixed(1)}%`;
  }

  // Utilidades para filtros de data
  obterFiltroMesAtual(): { data_inicio: string; data_fim: string } {
    const agora = new Date();
    const inicioMes = new Date(agora.getFullYear(), agora.getMonth(), 1);
    const fimMes = new Date(agora.getFullYear(), agora.getMonth() + 1, 0);
    
    return {
      data_inicio: inicioMes.toISOString().split('T')[0],
      data_fim: fimMes.toISOString().split('T')[0]
    };
  }

  obterFiltroAnoAtual(): { data_inicio: string; data_fim: string } {
    const agora = new Date();
    const inicioAno = new Date(agora.getFullYear(), 0, 1);
    const fimAno = new Date(agora.getFullYear(), 11, 31);
    
    return {
      data_inicio: inicioAno.toISOString().split('T')[0],
      data_fim: fimAno.toISOString().split('T')[0]
    };
  }

  obterFiltroUltimos30Dias(): { data_inicio: string; data_fim: string } {
    const agora = new Date();
    const inicio = new Date(agora.getTime() - (30 * 24 * 60 * 60 * 1000));
    
    return {
      data_inicio: inicio.toISOString().split('T')[0],
      data_fim: agora.toISOString().split('T')[0]
    };
  }

  obterFiltroUltimos7Dias(): { data_inicio: string; data_fim: string } {
    const agora = new Date();
    const inicio = new Date(agora.getTime() - (7 * 24 * 60 * 60 * 1000));
    
    return {
      data_inicio: inicio.toISOString().split('T')[0],
      data_fim: agora.toISOString().split('T')[0]
    };
  }

  // Utilidades para análise de dados
  calcularTendencia(dados: VendaPeriodo[]): 'crescente' | 'decrescente' | 'estavel' {
    if (dados.length < 2) return 'estavel';
    
    const metadeInicial = dados.slice(0, Math.floor(dados.length / 2));
    const metadeFinal = dados.slice(Math.floor(dados.length / 2));
    
    const mediaInicial = metadeInicial.reduce((acc, curr) => acc + curr.vendas_brutas, 0) / metadeInicial.length;
    const mediaFinal = metadeFinal.reduce((acc, curr) => acc + curr.vendas_brutas, 0) / metadeFinal.length;
    
    const diferenca = ((mediaFinal - mediaInicial) / mediaInicial) * 100;
    
    if (diferenca > 5) return 'crescente';
    if (diferenca < -5) return 'decrescente';
    return 'estavel';
  }

  obterProdutoMaisVendido(produtos: ProdutoPerformance[]): ProdutoPerformance | null {
    if (produtos.length === 0) return null;
    return produtos.reduce((prev, current) => 
      current.quantidade_vendida > prev.quantidade_vendida ? current : prev
    );
  }

  obterProdutoMaisLucrativo(produtos: ProdutoPerformance[]): ProdutoPerformance | null {
    if (produtos.length === 0) return null;
    return produtos.reduce((prev, current) => 
      current.valor_total > prev.valor_total ? current : prev
    );
  }

  calcularDistribuicaoHoraria(metricas: MetricasTempoReal): {
    pico: { hora: string; vendas: number };
    vale: { hora: string; vendas: number };
    mediaHoraria: number;
  } {
    const vendas = metricas.vendas_por_hora;
    if (vendas.length === 0) {
      return {
        pico: { hora: '00:00', vendas: 0 },
        vale: { hora: '00:00', vendas: 0 },
        mediaHoraria: 0
      };
    }

    const pico = vendas.reduce((prev, current) => 
      current.vendas > prev.vendas ? current : prev
    );
    
    const vale = vendas.reduce((prev, current) => 
      current.vendas < prev.vendas ? current : prev
    );

    const mediaHoraria = vendas.reduce((acc, curr) => acc + curr.vendas, 0) / vendas.length;

    return { pico, vale, mediaHoraria };
  }
}

export const dashboardFinanceiroService = new DashboardFinanceiroService();
