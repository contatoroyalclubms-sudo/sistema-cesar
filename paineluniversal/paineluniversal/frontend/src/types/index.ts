// 🔄 ARQUIVO PRINCIPAL DE TIPOS - COMPATIBILIDADE TOTAL
// Importa todos os tipos do arquivo database.ts para centralizar as definições

// Re-export todos os tipos do arquivo database
export * from './database';

// Tipos específicos para o sistema que podem não estar no database
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

export interface AgendamentoProduto {
  id: string;
  nome: string;
  regra: string;
  periodo: {
    inicio: Date;
    fim: Date;
  };
  produtos: any[]; // Usando any para evitar dependência circular
  ativo: boolean;
  tipo: 'promocao' | 'sazonal' | 'evento';
  created_at: Date;
  updated_at: Date;
}

// Tipos para uploads e arquivos
export interface FileUpload {
  file: File;
  progress: number;
  status: 'pending' | 'uploading' | 'success' | 'error';
  error?: string;
}

// Tipos para notificações
export interface Notification {
  id: string;
  type: 'success' | 'error' | 'warning' | 'info';
  title: string;
  message: string;
  timestamp: Date;
  read: boolean;
  action?: {
    label: string;
    url: string;
  };
}

// Tipos para configurações avançadas
export interface ThemeConfig {
  mode: 'light' | 'dark' | 'auto';
  primaryColor: string;
  secondaryColor: string;
  fontSize: 'small' | 'medium' | 'large';
}

export interface LayoutConfig {
  sidebar: 'expanded' | 'collapsed' | 'hidden';
  header: 'fixed' | 'static';
  footer: 'visible' | 'hidden';
}

// Tipos para modais e formulários
export interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title?: string;
  size?: 'sm' | 'md' | 'lg' | 'xl' | 'full';
}

export interface FormProps<T = any> {
  initialData?: Partial<T>;
  onSubmit: (data: T) => Promise<void> | void;
  onCancel?: () => void;
  loading?: boolean;
  disabled?: boolean;
}

// Tipos para tabelas e listas
export interface TableColumn<T = any> {
  key: keyof T | string;
  label: string;
  sortable?: boolean;
  filterable?: boolean;
  render?: (value: any, row: T) => React.ReactNode;
  width?: string | number;
  align?: 'left' | 'center' | 'right';
}

export interface TableProps<T = any> {
  data: T[];
  columns: TableColumn<T>[];
  loading?: boolean;
  pagination?: {
    page: number;
    limit: number;
    total: number;
    onPageChange: (page: number) => void;
  };
  selection?: {
    selected: string[];
    onSelectionChange: (selected: string[]) => void;
  };
  actions?: {
    label: string;
    icon?: React.ReactNode;
    onClick: (row: T) => void;
    show?: (row: T) => boolean;
  }[];
}

// Tipos para gráficos e charts
export interface ChartData {
  labels: string[];
  datasets: {
    label: string;
    data: number[];
    backgroundColor?: string | string[];
    borderColor?: string | string[];
    borderWidth?: number;
  }[];
}

export interface ChartOptions {
  responsive?: boolean;
  maintainAspectRatio?: boolean;
  plugins?: {
    legend?: {
      display?: boolean;
      position?: 'top' | 'bottom' | 'left' | 'right';
    };
    title?: {
      display?: boolean;
      text?: string;
    };
  };
  scales?: {
    x?: {
      display?: boolean;
      title?: {
        display?: boolean;
        text?: string;
      };
    };
    y?: {
      display?: boolean;
      title?: {
        display?: boolean;
        text?: string;
      };
    };
  };
}

// Tipos para contextos React
export interface AuthContextType {
  user: any | null; // Usando database.Usuario seria ideal
  token: string | null;
  login: (cpf: string, senha: string) => Promise<void>;
  logout: () => void;
  loading: boolean;
  isAuthenticated: boolean;
}

export interface EventoContextType {
  eventoAtual: any | null; // Usando database.Evento seria ideal
  setEventoAtual: (evento: any | null) => void;
  eventoId: number | null;
}

// Tipos para hooks customizados
export interface UseApiResult<T> {
  data: T | null;
  loading: boolean;
  error: string | null;
  refetch: () => Promise<void>;
}

export interface UseFormResult<T> {
  values: T;
  errors: Partial<Record<keyof T, string>>;
  touched: Partial<Record<keyof T, boolean>>;
  isValid: boolean;
  isSubmitting: boolean;
  setFieldValue: (field: keyof T, value: any) => void;
  setFieldError: (field: keyof T, error: string) => void;
  setFieldTouched: (field: keyof T, touched: boolean) => void;
  handleSubmit: (e?: React.FormEvent) => void;
  resetForm: () => void;
}

// Tipos para utilitários
export interface SelectOption {
  value: string | number;
  label: string;
  disabled?: boolean;
  group?: string;
}

export interface BreadcrumbItem {
  label: string;
  href?: string;
  current?: boolean;
}

export interface MenuItem {
  id: string;
  label: string;
  icon?: React.ReactNode;
  href?: string;
  children?: MenuItem[];
  badge?: {
    text: string;
    variant: 'primary' | 'secondary' | 'success' | 'warning' | 'error';
  };
  permissions?: string[];
}

// Tipos para validações
export interface ValidationRule {
  required?: boolean;
  minLength?: number;
  maxLength?: number;
  pattern?: RegExp;
  custom?: (value: any) => string | null;
}

export type ValidationSchema<T> = {
  [K in keyof T]?: ValidationRule;
}

// Tipos para permissões e segurança
export interface Permission {
  action: string;
  resource: string;
  conditions?: Record<string, any>;
}

export interface Role {
  id: string;
  name: string;
  permissions: Permission[];
  description?: string;
}

// Export default para compatibilidade
export default {};
