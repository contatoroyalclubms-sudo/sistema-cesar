export interface Produto {
  id?: string;
  nome: string;
  codigo_interno?: string;
  categoria?: string;
  tipo: 'BEBIDA' | 'COMIDA' | 'INGRESSO' | 'FICHA' | 'COMBO' | 'VOUCHER';
  preco: number;
  descricao?: string;
  estoque_atual?: number;
  estoque_minimo?: number;
  estoque_maximo?: number;
  controla_estoque?: boolean;
  status?: 'ATIVO' | 'INATIVO' | 'ESGOTADO';
  imagem_url?: string;
  empresa_id?: string;
  criado_em?: Date;
  atualizado_em?: Date;
  
  // Campos antigos mantidos para compatibilidade (podem ser removidos depois)
  codigo?: string;
  categoria_id?: string;
  valor?: number;
  estoque?: number;
  imagem?: string;
  created_at?: Date;
  updated_at?: Date;
}

export interface ImportResult {
  total_linhas: number;
  produtos_criados: number;
  produtos_com_erro: number;
  detalhes_criados: Array<{
    linha: number;
    nome: string;
    id: number;
  }>;
  detalhes_erros: Array<{
    linha: number;
    erro: string;
  }>;
  campos_detectados: string[];
  campos_mapeados: Record<string, string>;
}

export interface Categoria {
  id: string;
  nome: string;
  mostrar_dashboard: boolean;
  mostrar_pos: boolean;
  maximo_composicao?: number;
  minimo_composicao?: number;
  cor?: string;
  icone?: string;
  ordem: number;
  produtos_count?: number;
  created_at: Date;
  updated_at: Date;
}

export interface AgendamentoProduto {
  id: string;
  nome: string;
  regra: string;
  periodo: {
    inicio: Date;
    fim: Date;
  };
  produtos: Produto[];
  ativo: boolean;
  tipo: 'promocao' | 'sazonal' | 'evento';
  created_at: Date;
  updated_at: Date;
}

export interface ProdutoFilter {
  nome?: string;
  categoria?: string;
  tipo?: string;
  habilitado?: 'all' | 'true' | 'false';
  destaque?: 'true' | 'false';
  marca?: string;
  fornecedor?: string;
}

export interface CategoriaFilter {
  nome?: string;
  mostrar_dashboard?: boolean;
  mostrar_pos?: boolean;
}

export interface AgendamentoFilter {
  nome?: string;
  tipo?: 'promocao' | 'sazonal' | 'evento';
  ativo?: boolean;
}

export interface ImportOperation {
  id: string;
  tipo_operacao: 'IMPORTACAO' | 'EXPORTACAO';
  nome_arquivo: string;
  formato_arquivo: 'csv' | 'xlsx' | 'json' | 'xml';
  tamanho_arquivo?: number;
  status: 'PENDENTE' | 'PROCESSANDO' | 'CONCLUIDA' | 'ERRO' | 'CANCELADA';
  total_registros: number;
  registros_processados: number;
  registros_sucesso: number;
  registros_erro: number;
  registros_aviso: number;
  mapeamento_campos?: Record<string, string>;
  filtros_aplicados?: Record<string, any>;
  inicio_processamento?: Date;
  fim_processamento?: Date;
  log_detalhado?: string;
  url_arquivo_resultado?: string;
  resumo_operacao?: string;
  created_at: Date;
}

export interface ValidationError {
  field: string;
  type: 'required' | 'unique' | 'pattern' | 'range' | 'type';
  message: string;
  severity: 'critical' | 'warning';
  linha_arquivo?: number;
  valor_original?: string;
  valor_sugerido?: string;
}