/**
 * Serviço de API para Comandas
 * 
 * Este serviço gerencia todas as operações relacionadas às comandas do sistema,
 * incluindo geração de QR codes e funcionalidades específicas.
 */

import { api } from './api';

class ComandasService {
  constructor() {
    this.baseURL = '/api/comandas';
  }

  /**
   * Busca todas as comandas
   */
  async getAll(params = {}) {
    try {
      const response = await api.get(this.baseURL, { params });
      
      // Transformar dados para o formato esperado pelo frontend
      const data = response.data.map(comanda => ({
        id: comanda.id,
        numero: comanda.numero,
        cardapio_digital: comanda.cardapio_digital || false,
        qr_code: comanda.qr_code || '',
        ativo: comanda.ativo !== undefined ? comanda.ativo : true,
        status: comanda.ativo ? 'Ativo' : 'Inativo',
        observacoes: comanda.observacoes || '',
        created_at: comanda.created_at,
        updated_at: comanda.updated_at
      }));

      return {
        data,
        total: data.length,
        page: params.page || 1,
        per_page: params.per_page || 25
      };
    } catch (error) {
      console.error('Erro ao buscar comandas:', error);
      throw new Error('Falha ao carregar comandas');
    }
  }

  /**
   * Busca comanda por ID
   */
  async getById(id) {
    try {
      const response = await api.get(`${this.baseURL}/${id}`);
      return response.data;
    } catch (error) {
      console.error('Erro ao buscar comanda:', error);
      throw new Error('Comanda não encontrada');
    }
  }

  /**
   * Cria nova comanda
   */
  async create(comandaData) {
    try {
      const data = {
        ...comandaData,
        cardapio_digital: comandaData.cardapio_digital !== undefined ? comandaData.cardapio_digital : true,
        ativo: comandaData.ativo !== undefined ? comandaData.ativo : true,
        // QR Code será gerado automaticamente no backend
        qr_code: this.generateQRCode(comandaData.numero)
      };

      const response = await api.post(this.baseURL, data);
      return response.data;
    } catch (error) {
      console.error('Erro ao criar comanda:', error);
      
      if (error.response?.status === 400) {
        const message = error.response.data?.detail || 'Dados inválidos';
        throw new Error(message);
      }
      
      throw new Error('Falha ao criar comanda');
    }
  }

  /**
   * Atualiza comanda existente
   */
  async update(id, comandaData) {
    try {
      const data = {
        ...comandaData
      };

      const response = await api.put(`${this.baseURL}/${id}`, data);
      return response.data;
    } catch (error) {
      console.error('Erro ao atualizar comanda:', error);
      
      if (error.response?.status === 404) {
        throw new Error('Comanda não encontrada');
      }
      
      if (error.response?.status === 400) {
        const message = error.response.data?.detail || 'Dados inválidos';
        throw new Error(message);
      }
      
      throw new Error('Falha ao atualizar comanda');
    }
  }

  /**
   * Remove comanda
   */
  async delete(id) {
    try {
      await api.delete(`${this.baseURL}/${id}`);
      return { success: true };
    } catch (error) {
      console.error('Erro ao deletar comanda:', error);
      
      if (error.response?.status === 404) {
        throw new Error('Comanda não encontrada');
      }
      
      throw new Error('Falha ao deletar comanda');
    }
  }

  /**
   * Busca comanda por número
   */
  async getByNumero(numero) {
    try {
      const response = await api.get(`${this.baseURL}`, {
        params: { numero }
      });
      
      return response.data.length > 0 ? response.data[0] : null;
    } catch (error) {
      console.error('Erro ao buscar comanda por número:', error);
      return null;
    }
  }

  /**
   * Valida se um campo é único
   */
  async validateUnique(field, value, excludeId = null) {
    try {
      let comanda = null;
      
      if (field === 'numero') {
        comanda = await this.getByNumero(value);
      }
      
      // Se encontrou uma comanda e não é a mesma que está sendo editada
      if (comanda && comanda.id != excludeId) {
        return { valid: false, message: `${field.toUpperCase()} já cadastrado` };
      }
      
      return { valid: true };
    } catch (error) {
      console.error('Erro ao validar unicidade:', error);
      return { valid: true }; // Em caso de erro, permite a validação
    }
  }

  /**
   * Gera QR Code para a comanda
   */
  generateQRCode(numero) {
    // URL base para acesso ao cardápio digital
    const baseURL = window.location.origin;
    return `${baseURL}/cardapio/comanda/${numero}`;
  }

  /**
   * Regenera QR Code para uma comanda
   */
  async regenerateQRCode(id) {
    try {
      const response = await api.post(`${this.baseURL}/${id}/generate-qr`);
      return response.data;
    } catch (error) {
      console.error('Erro ao regenerar QR Code:', error);
      throw new Error('Falha ao regenerar QR Code');
    }
  }

  /**
   * Exporta comandas para CSV
   */
  async exportToCSV() {
    try {
      const response = await this.getAll();
      const comandas = response.data;
      
      const headers = ['ID', 'Número', 'Cardápio Digital', 'QR Code', 'Status', 'Observações'];
      const csvContent = [
        headers.join(','),
        ...comandas.map(cmd => [
          cmd.id,
          cmd.numero,
          cmd.cardapio_digital ? 'Habilitado' : 'Desabilitado',
          `"${cmd.qr_code}"`,
          cmd.ativo ? 'Ativo' : 'Inativo',
          `"${cmd.observacoes || ''}"`
        ].join(','))
      ].join('\n');
      
      const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
      const link = document.createElement('a');
      const url = URL.createObjectURL(blob);
      
      link.setAttribute('href', url);
      link.setAttribute('download', `comandas_${new Date().toISOString().split('T')[0]}.csv`);
      link.style.visibility = 'hidden';
      
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      
      return { success: true };
    } catch (error) {
      console.error('Erro ao exportar comandas:', error);
      throw new Error('Falha ao exportar dados');
    }
  }

  /**
   * Busca comandas com filtros
   */
  async search(query, filters = {}) {
    try {
      const params = {
        ...filters
      };
      
      if (query) {
        params.search = query;
      }
      
      return await this.getAll(params);
    } catch (error) {
      console.error('Erro ao buscar comandas:', error);
      throw new Error('Falha na busca');
    }
  }

  /**
   * Gera QR codes em lote
   */
  async bulkGenerateQR(comandaIds) {
    try {
      const response = await api.post(`${this.baseURL}/bulk-generate-qr`, {
        comanda_ids: comandaIds
      });
      return response.data;
    } catch (error) {
      console.error('Erro ao gerar QR codes em lote:', error);
      throw new Error('Falha ao gerar QR codes');
    }
  }

  /**
   * Imprime QR codes
   */
  async printQRCodes(comandaIds) {
    try {
      // Simular impressão - implementar conforme necessário
      const comandas = await Promise.all(
        comandaIds.map(id => this.getById(id))
      );
      
      // Abrir janela de impressão com QR codes
      const printWindow = window.open('', '_blank');
      const qrCodesHTML = comandas.map(comanda => `
        <div style="page-break-after: always; text-align: center; padding: 20px;">
          <h2>Comanda #${comanda.numero}</h2>
          <img src="https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=${encodeURIComponent(comanda.qr_code)}" />
          <p>Escaneie para acessar o cardápio</p>
        </div>
      `).join('');
      
      printWindow.document.write(`
        <html>
          <head><title>QR Codes - Comandas</title></head>
          <body>${qrCodesHTML}</body>
        </html>
      `);
      printWindow.document.close();
      printWindow.print();
      
      return { success: true };
    } catch (error) {
      console.error('Erro ao imprimir QR codes:', error);
      throw new Error('Falha ao imprimir QR codes');
    }
  }
}

export const comandasService = new ComandasService();
export default comandasService;
