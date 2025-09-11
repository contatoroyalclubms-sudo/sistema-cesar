import { api } from './api';

class ClientesService {
  async getAll(params = {}) {
    const response = await api.get('/api/meep/clientes', { params });
    return response.data;
  }

  async getById(id) {
    const response = await api.get(`/api/meep/clientes/${id}`);
    return response.data;
  }

  async getByCpf(cpf) {
    const response = await api.get(`/api/meep/clientes/${cpf}`);
    return response.data;
  }

  async create(cliente) {
    const response = await api.post('/api/meep/clientes', cliente);
    return response.data;
  }

  async update(id, cliente) {
    const response = await api.put(`/api/meep/clientes/${id}`, cliente);
    return response.data;
  }

  async delete(id) {
    const response = await api.delete(`/api/meep/clientes/${id}`);
    return response.data;
  }

  async validateUnique(field, value) {
    try {
      // Para CPF e email, vamos verificar se já existe fazendo uma busca
      if (field === 'cpf') {
        await this.getByCpf(value);
        return { valid: false }; // Se achou, já existe
      }
      // Para outros campos, assumir que é válido por enquanto
      return { valid: true };
    } catch (error) {
      if (error.response?.status === 404) {
        return { valid: true }; // Não existe, é válido
      }
      throw error;
    }
  }
}

export default new ClientesService();
