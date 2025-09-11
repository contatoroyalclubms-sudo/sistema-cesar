import api from './api';

export interface RecargaCashlessCreate {
  cartao_id: number;
  valor_recarga: number;
  forma_pagamento: string;
  cpf_cliente?: string;
  nome_cliente?: string;
  observacoes?: string;
  terminal_id?: string;
  cpf_operador?: string;
  nome_operador?: string;
}

export interface RecargaCashlessUpdate {
  status?: 'pendente' | 'aprovada' | 'cancelada' | 'estornada';
  observacoes?: string;
  aprovado_por?: number;
}

export interface MovimentacaoCashlessCreate {
  cartao_id: number;
  tipo_movimentacao: 'credito' | 'debito' | 'estorno' | 'bonus' | 'transferencia';
  valor: number;
  descricao?: string;
  referencia_id?: number;
  referencia_tipo?: string;
  referencia_numero?: string;
  terminal_id?: string;
  cpf_operador?: string;
  nome_operador?: string;
}

export interface ComandaDigitalCreate {
  numero_comanda: string;
  evento_id: number;
  empresa_id?: number;
  cartao_id?: number;
  mesa_id?: number;
  cliente_cpf?: string;
  cliente_nome?: string;
  cliente_telefone?: string;
  limite_credito?: number;
}

export interface PedidoComandaDigitalCreate {
  comanda_id: number;
  evento_id: number;
  empresa_id?: number;
  produtos: {
    produto_id: number;
    nome: string;
    quantidade: number;
    preco_unitario: number;
    observacoes?: string;
  }[];
  observacoes_cliente?: string;
}

export interface DashboardFilters {
  evento_id?: number;
  data_inicio?: string;
  data_fim?: string;
}

export interface ListFilters extends DashboardFilters {
  cartao_id?: number;
  status?: string;
  tipo_movimentacao?: string;
  limite?: number;
  offset?: number;
}

class CashlessService {
  private baseUrl = '/api/v1/cashless';

  // ================================================================================
  // RECARGAS
  // ================================================================================

  async createRecarga(data: RecargaCashlessCreate) {
    return api.post(`${this.baseUrl}/recargas`, data);
  }

  async getRecargas(filters: ListFilters = {}) {
    const params = new URLSearchParams();
    
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '') {
        params.append(key, value.toString());
      }
    });

    return api.get(`${this.baseUrl}/recargas?${params.toString()}`);
  }

  async getRecarga(id: number) {
    return api.get(`${this.baseUrl}/recargas/${id}`);
  }

  async updateRecarga(id: number, data: RecargaCashlessUpdate) {
    return api.put(`${this.baseUrl}/recargas/${id}`, data);
  }

  async aprovarRecarga(id: number) {
    return this.updateRecarga(id, { status: 'aprovada' });
  }

  async cancelarRecarga(id: number) {
    return this.updateRecarga(id, { status: 'cancelada' });
  }

  // ================================================================================
  // MOVIMENTAÇÕES
  // ================================================================================

  async createMovimentacao(data: MovimentacaoCashlessCreate) {
    return api.post(`${this.baseUrl}/movimentacoes`, data);
  }

  async getMovimentacoes(filters: ListFilters = {}) {
    const params = new URLSearchParams();
    
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '') {
        params.append(key, value.toString());
      }
    });

    return api.get(`${this.baseUrl}/movimentacoes?${params.toString()}`);
  }

  async getMovimentacao(id: number) {
    return api.get(`${this.baseUrl}/movimentacoes/${id}`);
  }

  async estornarMovimentacao(id: number, motivo: string) {
    return api.post(`${this.baseUrl}/movimentacoes/${id}/estorno`, { motivo });
  }

  // ================================================================================
  // COMANDAS DIGITAIS
  // ================================================================================

  async createComanda(data: ComandaDigitalCreate) {
    return api.post(`${this.baseUrl}/comandas`, data);
  }

  async getComandasAbertas(evento_id?: number) {
    const params = evento_id ? `?evento_id=${evento_id}` : '';
    return api.get(`${this.baseUrl}/comandas${params}`);
  }

  async getComandaByUuid(uuid: string) {
    return api.get(`${this.baseUrl}/comandas/${uuid}`);
  }

  async updateComanda(id: number, data: { status?: string; observacoes?: string }) {
    return api.put(`${this.baseUrl}/comandas/${id}`, data);
  }

  async fecharComanda(id: number) {
    return this.updateComanda(id, { status: 'fechada' });
  }

  async cancelarComanda(id: number) {
    return this.updateComanda(id, { status: 'cancelada' });
  }

  // ================================================================================
  // PEDIDOS COMANDA DIGITAL
  // ================================================================================

  async createPedido(data: PedidoComandaDigitalCreate) {
    return api.post(`${this.baseUrl}/comandas/${data.comanda_id}/pedidos`, data);
  }

  async getPedidosComanda(comanda_id: number) {
    return api.get(`${this.baseUrl}/comandas/${comanda_id}/pedidos`);
  }

  async updatePedido(id: number, data: { status?: string; observacoes_cozinha?: string }) {
    return api.put(`${this.baseUrl}/pedidos/${id}`, data);
  }

  async cancelarPedido(id: number) {
    return this.updatePedido(id, { status: 'cancelado' });
  }

  // ================================================================================
  // DASHBOARD E RELATÓRIOS
  // ================================================================================

  async getDashboard(filters: DashboardFilters = {}) {
    const params = new URLSearchParams();
    
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '') {
        params.append(key, value.toString());
      }
    });

    return api.get(`${this.baseUrl}/dashboard?${params.toString()}`);
  }

  async getRelatorioRecargas(filters: ListFilters = {}) {
    const params = new URLSearchParams();
    
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '') {
        params.append(key, value.toString());
      }
    });

    return api.get(`${this.baseUrl}/relatorios/recargas?${params.toString()}`);
  }

  async getRelatorioMovimentacoes(filters: ListFilters = {}) {
    const params = new URLSearchParams();
    
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '') {
        params.append(key, value.toString());
      }
    });

    return api.get(`${this.baseUrl}/relatorios/movimentacoes?${params.toString()}`);
  }

  async exportarRelatorio(tipo: 'recargas' | 'movimentacoes', filters: ListFilters = {}, formato: 'excel' | 'pdf' = 'excel') {
    const params = new URLSearchParams();
    
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '') {
        params.append(key, value.toString());
      }
    });

    params.append('formato', formato);

    return api.get(`${this.baseUrl}/relatorios/${tipo}/export?${params.toString()}`, {
      responseType: 'blob'
    });
  }

  // ================================================================================
  // CONFIGURAÇÕES
  // ================================================================================

  async getConfiguracoes(evento_id: number) {
    return api.get(`${this.baseUrl}/configuracoes/${evento_id}`);
  }

  async updateConfiguracoes(evento_id: number, configuracoes: any) {
    return api.put(`${this.baseUrl}/configuracoes/${evento_id}`, configuracoes);
  }

  async criarConfiguracoesPadrao(evento_id: number) {
    return api.post(`${this.baseUrl}/configuracoes`, { evento_id });
  }

  // ================================================================================
  // TERMINAIS
  // ================================================================================

  async getTerminais(evento_id?: number) {
    const params = evento_id ? `?evento_id=${evento_id}` : '';
    return api.get(`${this.baseUrl}/terminais${params}`);
  }

  async createTerminal(data: any) {
    return api.post(`${this.baseUrl}/terminais`, data);
  }

  async updateTerminal(id: number, data: any) {
    return api.put(`${this.baseUrl}/terminais/${id}`, data);
  }

  async ativarTerminal(id: number) {
    return this.updateTerminal(id, { ativo: true });
  }

  async desativarTerminal(id: number) {
    return this.updateTerminal(id, { ativo: false });
  }

  // ================================================================================
  // CARTÕES CASHLESS
  // ================================================================================

  async getCartoes(filters: { evento_id?: number; status?: string; cpf_cliente?: string } = {}) {
    const params = new URLSearchParams();
    
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '') {
        params.append(key, value.toString());
      }
    });

    return api.get(`${this.baseUrl}/cartoes?${params.toString()}`);
  }

  async getCartao(id: number) {
    return api.get(`${this.baseUrl}/cartoes/${id}`);
  }

  async getCartaoByCpf(cpf: string, evento_id: number) {
    return api.get(`${this.baseUrl}/cartoes/cpf/${cpf}?evento_id=${evento_id}`);
  }

  async createCartao(data: any) {
    return api.post(`${this.baseUrl}/cartoes`, data);
  }

  async updateCartao(id: number, data: any) {
    return api.put(`${this.baseUrl}/cartoes/${id}`, data);
  }

  async bloquearCartao(id: number, motivo: string) {
    return this.updateCartao(id, { status: 'bloqueado', observacoes: motivo });
  }

  async desbloquearCartao(id: number) {
    return this.updateCartao(id, { status: 'ativo' });
  }

  async cancelarCartao(id: number, motivo: string) {
    return this.updateCartao(id, { status: 'cancelado', observacoes: motivo });
  }

  // ================================================================================
  // OPERAÇÕES ESPECIAIS
  // ================================================================================

  async transferirSaldo(origem_cartao_id: number, destino_cartao_id: number, valor: number, motivo: string) {
    return api.post(`${this.baseUrl}/transferencias`, {
      origem_cartao_id,
      destino_cartao_id,
      valor,
      motivo
    });
  }

  async estornarVenda(venda_id: number, motivo: string) {
    return api.post(`${this.baseUrl}/estornos/venda`, {
      venda_id,
      motivo
    });
  }

  async recarregaRapida(cartao_id: number, valor: number) {
    return this.createRecarga({
      cartao_id,
      valor_recarga: valor,
      forma_pagamento: 'DINHEIRO'
    });
  }

  // ================================================================================
  // INTEGRAÇÃO COM QR CODE
  // ================================================================================

  async gerarQrCodeComanda(comanda_id: number) {
    return api.get(`${this.baseUrl}/comandas/${comanda_id}/qrcode`, {
      responseType: 'blob'
    });
  }

  async gerarQrCodeCartao(cartao_id: number) {
    return api.get(`${this.baseUrl}/cartoes/${cartao_id}/qrcode`, {
      responseType: 'blob'
    });
  }

  // ================================================================================
  // MONITORAMENTO EM TEMPO REAL
  // ================================================================================

  async getStatusSistema() {
    return api.get(`${this.baseUrl}/status`);
  }

  async getNotificacoesPendentes() {
    return api.get(`${this.baseUrl}/notificacoes`);
  }

  async marcarNotificacaoLida(id: number) {
    return api.put(`${this.baseUrl}/notificacoes/${id}/lida`);
  }

  // ================================================================================
  // UTILITÁRIOS
  // ================================================================================

  formatCurrency(value: number): string {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL'
    }).format(value);
  }

  formatDate(date: string): string {
    return new Intl.DateTimeFormat('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    }).format(new Date(date));
  }

  calcularBonus(valor: number, percentual: number): number {
    return (valor * percentual) / 100;
  }

  validarCpf(cpf: string): boolean {
    // Remove caracteres não numéricos
    cpf = cpf.replace(/\D/g, '');
    
    // Verifica se tem 11 dígitos
    if (cpf.length !== 11) return false;
    
    // Verifica se todos os dígitos são iguais
    if (/^(\d)\1{10}$/.test(cpf)) return false;
    
    // Validação do CPF
    let soma = 0;
    for (let i = 0; i < 9; i++) {
      soma += parseInt(cpf.charAt(i)) * (10 - i);
    }
    let resto = 11 - (soma % 11);
    if (resto === 10 || resto === 11) resto = 0;
    if (resto !== parseInt(cpf.charAt(9))) return false;
    
    soma = 0;
    for (let i = 0; i < 10; i++) {
      soma += parseInt(cpf.charAt(i)) * (11 - i);
    }
    resto = 11 - (soma % 11);
    if (resto === 10 || resto === 11) resto = 0;
    if (resto !== parseInt(cpf.charAt(10))) return false;
    
    return true;
  }

  formatarCpf(cpf: string): string {
    cpf = cpf.replace(/\D/g, '');
    return cpf.replace(/(\d{3})(\d{3})(\d{3})(\d{2})/, '$1.$2.$3-$4');
  }

  gerarNumeroCartao(): string {
    const timestamp = Date.now().toString();
    const random = Math.floor(Math.random() * 1000).toString().padStart(3, '0');
    return `CARD${timestamp.slice(-8)}${random}`;
  }

  gerarNumeroComanda(): string {
    const timestamp = Date.now().toString();
    const random = Math.floor(Math.random() * 100).toString().padStart(2, '0');
    return `CMD${timestamp.slice(-6)}${random}`;
  }
}

export const cashlessService = new CashlessService();
export default cashlessService;
