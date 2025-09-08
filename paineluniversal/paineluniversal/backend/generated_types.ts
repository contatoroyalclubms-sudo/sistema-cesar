// 🤖 GERADO AUTOMATICAMENTE - NÃO EDITAR MANUALMENTE
// Interfaces TypeScript sincronizadas com os modelos do backend
// Gerado em: 2025-08-27T00:59:28.730912

export type UserRole = 'admin' | 'promoter' | 'cliente' | 'operador';
export type StatusEvento = 'ATIVO' | 'INATIVO' | 'CANCELADO' | 'FINALIZADO';
export type TipoLista = 'VIP' | 'PREMIUM' | 'COMUM' | 'PROMOTER' | 'FREE';
export type StatusTransacao = 'PENDENTE' | 'APROVADA' | 'CANCELADA' | 'ESTORNADA';
export type TipoProduto = 'BEBIDA' | 'COMIDA' | 'INGRESSO' | 'FICHA' | 'COMBO' | 'VOUCHER';


// Interfaces de resposta da API
export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  message?: string;
  errors?: string[];
}

export interface PaginatedResponse<T = any> {
  items: T[];
  total: number;
  page: number;
  limit: number;
  has_next: boolean;
  has_prev: boolean;
}

export interface LoginRequest {
  cpf: string;
  senha: string;
  codigo_verificacao?: string;
}

export interface Token {
  access_token: string;
  token_type: string;
  usuario: Usuario;
}
