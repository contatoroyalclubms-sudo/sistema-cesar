import api from './api';

export interface Empresa {
  id: number;
  razao_social: string;
  nome_fantasia?: string;
  cnpj: string;
  inscricao_estadual?: string;
  inscricao_municipal?: string;
  email: string;
  telefone: string;
  telefone_secundario?: string;
  whatsapp?: string;
  site?: string;
  responsavel_nome?: string;
  responsavel_cargo?: string;
  responsavel_email?: string;
  responsavel_telefone?: string;
  cep?: string;
  logradouro?: string;
  numero?: string;
  complemento?: string;
  bairro?: string;
  cidade?: string;
  estado?: string;
  banco?: string;
  agencia?: string;
  conta?: string;
  tipo_conta?: string;
  observacoes?: string;
  ativa: boolean;
  criado_em: string;
  atualizado_em?: string;
}

export interface EmpresaCreate {
  razao_social: string;
  nome_fantasia?: string;
  cnpj: string;
  inscricao_estadual?: string;
  inscricao_municipal?: string;
  email: string;
  telefone: string;
  telefone_secundario?: string;
  whatsapp?: string;
  site?: string;
  responsavel_nome?: string;
  responsavel_cargo?: string;
  responsavel_email?: string;
  responsavel_telefone?: string;
  cep?: string;
  logradouro?: string;
  numero?: string;
  complemento?: string;
  bairro?: string;
  cidade?: string;
  estado?: string;
  banco?: string;
  agencia?: string;
  conta?: string;
  tipo_conta?: string;
  observacoes?: string;
}

export interface EmpresaUpdate extends Partial<EmpresaCreate> {
  ativa?: boolean;
}

export interface EmpresaFilters {
  search?: string;
  ativa?: boolean;
  skip?: number;
  limit?: number;
}

const empresasService = {
  // Listar empresas com filtros
  async list(filters: EmpresaFilters = {}): Promise<Empresa[]> {
    const params = new URLSearchParams();
    
    if (filters.search) params.append('search', filters.search);
    if (filters.ativa !== undefined) params.append('ativa', filters.ativa.toString());
    if (filters.skip !== undefined) params.append('skip', filters.skip.toString());
    if (filters.limit !== undefined) params.append('limit', filters.limit.toString());

    const response = await api.get(`/api/empresas?${params.toString()}`);
    return response.data;
  },

  // Alias para list() - compatibilidade com CadastroModule
  async getAll(params: any = {}): Promise<Empresa[]> {
    return this.list(params);
  },

  // Obter empresa por ID
  async getById(id: number): Promise<Empresa> {
    const response = await api.get(`/api/empresas/${id}`);
    return response.data;
  },

  // Criar nova empresa
  async create(empresa: EmpresaCreate): Promise<Empresa> {
    const response = await api.post('/api/empresas', empresa);
    return response.data;
  },

  // Atualizar empresa
  async update(id: number, empresa: EmpresaUpdate): Promise<Empresa> {
    const response = await api.put(`/api/empresas/${id}`, empresa);
    return response.data;
  },

  // Desativar empresa (soft delete)
  async delete(id: number): Promise<{ mensagem: string }> {
    const response = await api.delete(`/api/empresas/${id}`);
    return response.data;
  },

  // Ativar empresa
  async activate(id: number): Promise<{ mensagem: string }> {
    const response = await api.patch(`/api/empresas/${id}/ativar`);
    return response.data;
  },

  // Buscar empresas por termo
  async search(term: string, limit: number = 10): Promise<Empresa[]> {
    return this.list({ search: term, limit });
  },

  // Verificar se CNPJ já existe
  async checkCnpjExists(cnpj: string, excludeId?: number): Promise<boolean> {
    try {
      const empresas = await this.list({ search: cnpj });
      return empresas.some(empresa => 
        empresa.cnpj === cnpj && (!excludeId || empresa.id !== excludeId)
      );
    } catch (error) {
      console.error('Erro ao verificar CNPJ:', error);
      return false;
    }
  },

  // Verificar se email já existe  
  async checkEmailExists(email: string, excludeId?: number): Promise<boolean> {
    try {
      const empresas = await this.list({ search: email });
      return empresas.some(empresa => 
        empresa.email === email && (!excludeId || empresa.id !== excludeId)
      );
    } catch (error) {
      console.error('Erro ao verificar email:', error);
      return false;
    }
  },

  // Formatar CNPJ para exibição
  formatCnpj(cnpj: string): string {
    if (!cnpj) return '';
    // Remove tudo que não é dígito
    const digits = cnpj.replace(/\D/g, '');
    // Aplica a máscara 00.000.000/0000-00
    if (digits.length === 14) {
      return digits.replace(/(\d{2})(\d{3})(\d{3})(\d{4})(\d{2})/, '$1.$2.$3/$4-$5');
    }
    return cnpj;
  },

  // Formatar telefone para exibição
  formatPhone(phone: string): string {
    if (!phone) return '';
    const digits = phone.replace(/\D/g, '');
    if (digits.length === 11) {
      return digits.replace(/(\d{2})(\d{5})(\d{4})/, '($1) $2-$3');
    } else if (digits.length === 10) {
      return digits.replace(/(\d{2})(\d{4})(\d{4})/, '($1) $2-$3');
    }
    return phone;
  },

  // Formatar CEP para exibição
  formatCep(cep: string): string {
    if (!cep) return '';
    const digits = cep.replace(/\D/g, '');
    if (digits.length === 8) {
      return digits.replace(/(\d{5})(\d{3})/, '$1-$2');
    }
    return cep;
  },

  // Remover máscaras para salvar
  removeFormatting(data: any): any {
    const cleaned = { ...data };
    
    // Remove máscara do CNPJ
    if (cleaned.cnpj) {
      cleaned.cnpj = cleaned.cnpj.replace(/\D/g, '');
    }
    
    // Remove máscaras dos telefones
    ['telefone', 'telefone_secundario', 'whatsapp', 'responsavel_telefone'].forEach(field => {
      if (cleaned[field]) {
        cleaned[field] = cleaned[field].replace(/\D/g, '');
      }
    });
    
    // Remove máscara do CEP
    if (cleaned.cep) {
      cleaned.cep = cleaned.cep.replace(/\D/g, '');
    }
    
    return cleaned;
  },

  // Aplicar formatação para exibição
  applyFormatting(data: any): any {
    const formatted = { ...data };
    
    // Formatar CNPJ
    if (formatted.cnpj) {
      formatted.cnpj = this.formatCnpj(formatted.cnpj);
    }
    
    // Formatar telefones
    ['telefone', 'telefone_secundario', 'whatsapp', 'responsavel_telefone'].forEach(field => {
      if (formatted[field]) {
        formatted[field] = this.formatPhone(formatted[field]);
      }
    });
    
    // Formatar CEP
    if (formatted.cep) {
      formatted.cep = this.formatCep(formatted.cep);
    }
    
    return formatted;
  }
};

export default empresasService;
