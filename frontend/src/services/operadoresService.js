/**
 * Serviço de API para Operadores
 * 
 * Este serviço gerencia todas as operações relacionadas aos operadores do sistema,
 * utilizando o endpoint de usuários com filtro para o tipo 'promoter'.
 */

import { api } from './api';

class OperadoresService {
  constructor() {
    this.baseURL = '/api/usuarios';
  }

  /**
   * Busca todos os operadores
   */
  async getAll(params = {}) {
    try {
      // Adiciona filtro para tipo promoter
      const queryParams = {
        ...params,
        tipo: 'promoter'
      };

      const response = await api.get(this.baseURL, { params: queryParams });
      
      // Transformar dados para o formato esperado pelo frontend
      const data = response.data.map(user => ({
        id: user.id,
        nome: user.nome,
        cpf: user.cpf,
        email: user.email,
        telefone: user.telefone || '',
        comissao: user.comissao || '0.00',
        ativo: user.ativo,
        tipo: user.tipo,
        created_at: user.created_at,
        updated_at: user.updated_at
      }));

      return {
        data,
        total: data.length,
        page: params.page || 1,
        per_page: params.per_page || 25
      };
    } catch (error) {
      console.error('Erro ao buscar operadores:', error);
      throw new Error('Falha ao carregar operadores');
    }
  }

  /**
   * Busca operador por ID
   */
  async getById(id) {
    try {
      const response = await api.get(`${this.baseURL}/${id}`);
      
      // Verificar se é um operador
      if (response.data.tipo !== 'promoter') {
        throw new Error('Usuário não é um operador');
      }

      return response.data;
    } catch (error) {
      console.error('Erro ao buscar operador:', error);
      throw new Error('Operador não encontrado');
    }
  }

  /**
   * Cria novo operador
   */
  async create(operadorData) {
    try {
      // Garantir que o tipo seja promoter
      const data = {
        ...operadorData,
        tipo: 'promoter',
        comissao: parseFloat(operadorData.comissao || 0),
        ativo: operadorData.ativo !== undefined ? operadorData.ativo : true
      };

      const response = await api.post(this.baseURL, data);
      return response.data;
    } catch (error) {
      console.error('Erro ao criar operador:', error);
      
      if (error.response?.status === 400) {
        const message = error.response.data?.detail || 'Dados inválidos';
        throw new Error(message);
      }
      
      throw new Error('Falha ao criar operador');
    }
  }

  /**
   * Atualiza operador existente
   */
  async update(id, operadorData) {
    try {
      // Garantir que o tipo permaneça como promoter
      const data = {
        ...operadorData,
        tipo: 'promoter',
        comissao: parseFloat(operadorData.comissao || 0)
      };

      // Remove senha se estiver vazia (não atualizar senha)
      if (!data.senha || data.senha.trim() === '') {
        delete data.senha;
      }

      const response = await api.put(`${this.baseURL}/${id}`, data);
      return response.data;
    } catch (error) {
      console.error('Erro ao atualizar operador:', error);
      
      if (error.response?.status === 404) {
        throw new Error('Operador não encontrado');
      }
      
      if (error.response?.status === 400) {
        const message = error.response.data?.detail || 'Dados inválidos';
        throw new Error(message);
      }
      
      throw new Error('Falha ao atualizar operador');
    }
  }

  /**
   * Remove operador
   */
  async delete(id) {
    try {
      // Verificar se é um operador antes de deletar
      const operador = await this.getById(id);
      
      await api.delete(`${this.baseURL}/${id}`);
      return { success: true };
    } catch (error) {
      console.error('Erro ao deletar operador:', error);
      
      if (error.response?.status === 404) {
        throw new Error('Operador não encontrado');
      }
      
      throw new Error('Falha ao deletar operador');
    }
  }

  /**
   * Busca operador por CPF
   */
  async getByCpf(cpf) {
    try {
      const cpfFormatted = cpf.replace(/[^0-9]/g, '');
      const response = await api.get(`${this.baseURL}`, {
        params: { cpf: cpfFormatted, tipo: 'promoter' }
      });
      
      return response.data.length > 0 ? response.data[0] : null;
    } catch (error) {
      console.error('Erro ao buscar operador por CPF:', error);
      return null;
    }
  }

  /**
   * Busca operador por email
   */
  async getByEmail(email) {
    try {
      const response = await api.get(`${this.baseURL}`, {
        params: { email, tipo: 'promoter' }
      });
      
      return response.data.length > 0 ? response.data[0] : null;
    } catch (error) {
      console.error('Erro ao buscar operador por email:', error);
      return null;
    }
  }

  /**
   * Valida se um campo é único
   */
  async validateUnique(field, value, excludeId = null) {
    try {
      let operador = null;
      
      if (field === 'cpf') {
        operador = await this.getByCpf(value);
      } else if (field === 'email') {
        operador = await this.getByEmail(value);
      }
      
      // Se encontrou um operador e não é o mesmo que está sendo editado
      if (operador && operador.id != excludeId) {
        return { valid: false, message: `${field.toUpperCase()} já cadastrado` };
      }
      
      return { valid: true };
    } catch (error) {
      console.error('Erro ao validar unicidade:', error);
      return { valid: true }; // Em caso de erro, permite a validação
    }
  }

  /**
   * Exporta operadores para CSV
   */
  async exportToCSV() {
    try {
      const response = await this.getAll();
      const operadores = response.data;
      
      const headers = ['ID', 'Nome', 'CPF', 'Email', 'Telefone', 'Comissão (%)', 'Status'];
      const csvContent = [
        headers.join(','),
        ...operadores.map(op => [
          op.id,
          `"${op.nome}"`,
          op.cpf,
          op.email,
          op.telefone,
          op.comissao,
          op.ativo ? 'Ativo' : 'Inativo'
        ].join(','))
      ].join('\n');
      
      const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
      const link = document.createElement('a');
      const url = URL.createObjectURL(blob);
      
      link.setAttribute('href', url);
      link.setAttribute('download', `operadores_${new Date().toISOString().split('T')[0]}.csv`);
      link.style.visibility = 'hidden';
      
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      
      return { success: true };
    } catch (error) {
      console.error('Erro ao exportar operadores:', error);
      throw new Error('Falha ao exportar dados');
    }
  }

  /**
   * Busca operadores com filtros
   */
  async search(query, filters = {}) {
    try {
      const params = {
        ...filters,
        tipo: 'promoter'
      };
      
      if (query) {
        params.search = query;
      }
      
      return await this.getAll(params);
    } catch (error) {
      console.error('Erro ao buscar operadores:', error);
      throw new Error('Falha na busca');
    }
  }
}

export const operadoresService = new OperadoresService();
export default operadoresService;
