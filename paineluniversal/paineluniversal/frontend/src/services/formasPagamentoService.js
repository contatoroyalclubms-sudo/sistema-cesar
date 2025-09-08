// Serviço para gerenciamento de formas de pagamento
import api from './api';

class FormasPagamentoService {
  /**
   * Lista todas as formas de pagamento com filtros e paginação
   * @param {Object} params - Parâmetros de busca
   * @returns {Promise<Object>} Lista paginada de formas de pagamento
   */
  async listar(params = {}) {
    try {
      const response = await api.get('/formas-pagamento', { params });
      return response.data;
    } catch (error) {
      console.error('Erro ao listar formas de pagamento:', error);
      throw error;
    }
  }

  /**
   * Busca uma forma de pagamento por ID
   * @param {number} id - ID da forma de pagamento
   * @returns {Promise<Object>} Dados da forma de pagamento
   */
  async buscarPorId(id) {
    try {
      const response = await api.get(`/formas-pagamento/${id}`);
      return response.data;
    } catch (error) {
      console.error('Erro ao buscar forma de pagamento:', error);
      throw error;
    }
  }

  /**
   * Cria uma nova forma de pagamento
   * @param {Object} dados - Dados da forma de pagamento
   * @returns {Promise<Object>} Forma de pagamento criada
   */
  async criar(dados) {
    try {
      // Validar configurações extras se for JSON
      if (dados.configuracoes_extras && typeof dados.configuracoes_extras === 'string') {
        try {
          JSON.parse(dados.configuracoes_extras);
        } catch (e) {
          throw new Error('Configurações extras devem estar em formato JSON válido');
        }
      }

      const response = await api.post('/formas-pagamento', dados);
      return response.data;
    } catch (error) {
      console.error('Erro ao criar forma de pagamento:', error);
      throw error;
    }
  }

  /**
   * Atualiza uma forma de pagamento existente
   * @param {number} id - ID da forma de pagamento
   * @param {Object} dados - Dados atualizados
   * @returns {Promise<Object>} Forma de pagamento atualizada
   */
  async atualizar(id, dados) {
    try {
      // Validar configurações extras se for JSON
      if (dados.configuracoes_extras && typeof dados.configuracoes_extras === 'string') {
        try {
          JSON.parse(dados.configuracoes_extras);
        } catch (e) {
          throw new Error('Configurações extras devem estar em formato JSON válido');
        }
      }

      const response = await api.put(`/formas-pagamento/${id}`, dados);
      return response.data;
    } catch (error) {
      console.error('Erro ao atualizar forma de pagamento:', error);
      throw error;
    }
  }

  /**
   * Remove uma forma de pagamento
   * @param {number} id - ID da forma de pagamento
   * @returns {Promise<void>}
   */
  async remover(id) {
    try {
      await api.delete(`/formas-pagamento/${id}`);
    } catch (error) {
      console.error('Erro ao remover forma de pagamento:', error);
      throw error;
    }
  }

  /**
   * Alterna o status ativo/inativo de uma forma de pagamento
   * @param {number} id - ID da forma de pagamento
   * @returns {Promise<Object>} Forma de pagamento atualizada
   */
  async alternarStatus(id) {
    try {
      const response = await api.patch(`/formas-pagamento/${id}/toggle-status`);
      return response.data;
    } catch (error) {
      console.error('Erro ao alternar status da forma de pagamento:', error);
      throw error;
    }
  }

  /**
   * Busca formas de pagamento ativas para uso em outros módulos
   * @returns {Promise<Array>} Lista de formas de pagamento ativas
   */
  async buscarAtivas() {
    try {
      const response = await api.get('/formas-pagamento', { 
        params: { 
          ativo: true, 
          status: 'ATIVO',
          limit: 1000  // Buscar todas as ativas
        }
      });
      return response.data.items || response.data;
    } catch (error) {
      console.error('Erro ao buscar formas de pagamento ativas:', error);
      throw error;
    }
  }

  /**
   * Calcula taxa total (percentual + fixa) para um valor
   * @param {Object} formaPagamento - Dados da forma de pagamento
   * @param {number} valor - Valor para calcular a taxa
   * @returns {Object} Cálculo detalhado das taxas
   */
  calcularTaxa(formaPagamento, valor) {
    const taxaPercentual = (formaPagamento.taxa_percentual || 0) / 100;
    const taxaFixa = formaPagamento.taxa_fixa || 0;
    
    const valorTaxaPercentual = valor * taxaPercentual;
    const taxaTotal = valorTaxaPercentual + taxaFixa;
    const valorLiquido = valor - taxaTotal;
    
    return {
      valorOriginal: valor,
      taxaPercentual: formaPagamento.taxa_percentual || 0,
      valorTaxaPercentual,
      taxaFixa,
      taxaTotal,
      valorLiquido,
      percentualTotal: (taxaTotal / valor) * 100
    };
  }

  /**
   * Valida se um valor está dentro dos limites da forma de pagamento
   * @param {Object} formaPagamento - Dados da forma de pagamento
   * @param {number} valor - Valor a ser validado
   * @returns {Object} Resultado da validação
   */
  validarLimites(formaPagamento, valor) {
    const erros = [];
    
    if (formaPagamento.limite_minimo && valor < formaPagamento.limite_minimo) {
      erros.push(`Valor mínimo: R$ ${formaPagamento.limite_minimo.toFixed(2)}`);
    }
    
    if (formaPagamento.limite_maximo && valor > formaPagamento.limite_maximo) {
      erros.push(`Valor máximo: R$ ${formaPagamento.limite_maximo.toFixed(2)}`);
    }
    
    return {
      valido: erros.length === 0,
      erros
    };
  }
}

// Instância singleton do serviço
const formasPagamentoService = new FormasPagamentoService();

export { formasPagamentoService };
export default formasPagamentoService;
