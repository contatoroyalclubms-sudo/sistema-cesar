import { api } from './api';

export interface Categoria {
  id: number;
  nome: string;
  descricao?: string;
  cor?: string;
  ativo: boolean;
  criado_em: string;
  atualizado_em: string;
}

export interface CategoriaCreate {
  nome: string;
  descricao?: string;
  cor?: string;
}

export interface CategoriaUpdate {
  nome?: string;
  descricao?: string;
  cor?: string;
}

export const categoriaService = {
  async listar(): Promise<Categoria[]> {
    try {
      const response = await api.get('/produtos/categorias/');
      return response.data;
    } catch (error) {
      console.error('Erro ao listar categorias:', error);
      // Retornar dados mock em caso de erro
      return [
        {
          id: 1,
          nome: 'Bebidas',
          descricao: 'Bebidas alcoólicas e não alcoólicas',
          cor: '#10B981',
          ativo: true,
          criado_em: new Date().toISOString(),
          atualizado_em: new Date().toISOString()
        },
        {
          id: 2,
          nome: 'Comidas',
          descricao: 'Pratos principais e petiscos',
          cor: '#F59E0B',
          ativo: true,
          criado_em: new Date().toISOString(),
          atualizado_em: new Date().toISOString()
        }
      ];
    }
  },

  async criar(data: CategoriaCreate): Promise<Categoria> {
    try {
      const response = await api.post('/produtos/categorias/', data);
      return response.data;
    } catch (error) {
      console.error('Erro ao criar categoria:', error);
      // Simular criação para desenvolvimento
      const novaCategoria: Categoria = {
        id: Date.now(),
        nome: data.nome,
        descricao: data.descricao,
        cor: data.cor || '#3b82f6',
        ativo: true,
        criado_em: new Date().toISOString(),
        atualizado_em: new Date().toISOString()
      };
      return novaCategoria;
    }
  },

  async obter(id: number): Promise<Categoria> {
    try {
      const response = await api.get(`/produtos/categorias/${id}`);
      return response.data;
    } catch (error) {
      console.error('Erro ao obter categoria:', error);
      throw new Error('Categoria não encontrada');
    }
  },

  async atualizar(id: number, data: CategoriaUpdate): Promise<Categoria> {
    try {
      const response = await api.put(`/produtos/categorias/${id}`, data);
      return response.data;
    } catch (error) {
      console.error('Erro ao atualizar categoria:', error);
      throw new Error('Erro ao atualizar categoria');
    }
  },

  async deletar(id: number): Promise<void> {
    try {
      await api.delete(`/produtos/categorias/${id}`);
    } catch (error) {
      console.error('Erro ao deletar categoria:', error);
      throw new Error('Erro ao deletar categoria');
    }
  }
};
