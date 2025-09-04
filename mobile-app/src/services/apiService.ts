import AsyncStorage from '@react-native-async-storage/async-storage';

interface RequestConfig {
  method: 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH';
  headers: Record<string, string>;
  body?: string;
}

interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  message?: string;
  error?: string;
  [key: string]: any;
}

class ApiService {
  private baseURL: string;
  private token: string | null = null;
  private retryAttempts = 3;
  private retryDelay = 1000; // 1 segundo

  constructor() {
    // URL base do backend - ajustar conforme necessário
    this.baseURL = __DEV__ 
      ? 'http://192.168.100.165:8000' // IP local da máquina
      : 'https://paineluniversal-production.up.railway.app';
  }

  setAuthToken(token: string | null) {
    this.token = token;
  }

  private getHeaders(): Record<string, string> {
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    };

    if (this.token) {
      headers['Authorization'] = `Bearer ${this.token}`;
    }

    return headers;
  }

  private async makeRequest<T>(
    endpoint: string, 
    config: Partial<RequestConfig> = {}
  ): Promise<T> {
    const url = `${this.baseURL}${endpoint}`;
    
    const requestConfig: RequestConfig = {
      method: 'GET',
      headers: this.getHeaders(),
      ...config,
    };

    let lastError: Error;

    for (let attempt = 0; attempt < this.retryAttempts; attempt++) {
      try {
        const response = await fetch(url, requestConfig);
        
        // Se sucesso, retornar dados
        if (response.ok) {
          const data = await response.json();
          return data;
        }

        // Se erro 401, limpar token e rejeitar imediatamente
        if (response.status === 401) {
          this.token = null;
          await AsyncStorage.removeItem('auth_token');
          throw new Error('Token expirado ou inválido');
        }

        // Se erro 4xx que não é 401, não tentar novamente
        if (response.status >= 400 && response.status < 500 && response.status !== 401) {
          const errorData = await response.json().catch(() => ({}));
          throw new Error(errorData.detail || errorData.message || `Erro ${response.status}`);
        }

        // Para outros erros, criar erro para retry
        const errorData = await response.json().catch(() => ({}));
        lastError = new Error(errorData.detail || errorData.message || `Erro ${response.status}`);

      } catch (error: any) {
        lastError = error;

        // Se é erro de rede ou timeout, tentar novamente
        if (error.name === 'TypeError' || error.name === 'NetworkError' || 
            error.message.includes('Failed to fetch') || 
            error.message.includes('Network request failed')) {
          
          if (attempt < this.retryAttempts - 1) {
            await this.delay(this.retryDelay * (attempt + 1));
            continue;
          }
        }

        // Se não é erro de rede ou já esgotou tentativas, rejeitar
        break;
      }
    }

    throw lastError!;
  }

  private delay(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  async get<T = any>(endpoint: string): Promise<T> {
    return this.makeRequest<T>(endpoint, { method: 'GET' });
  }

  async post<T = any>(endpoint: string, data?: any): Promise<T> {
    return this.makeRequest<T>(endpoint, {
      method: 'POST',
      body: data ? JSON.stringify(data) : undefined,
    });
  }

  async put<T = any>(endpoint: string, data?: any): Promise<T> {
    return this.makeRequest<T>(endpoint, {
      method: 'PUT',
      body: data ? JSON.stringify(data) : undefined,
    });
  }

  async patch<T = any>(endpoint: string, data?: any): Promise<T> {
    return this.makeRequest<T>(endpoint, {
      method: 'PATCH',
      body: data ? JSON.stringify(data) : undefined,
    });
  }

  async delete<T = any>(endpoint: string): Promise<T> {
    return this.makeRequest<T>(endpoint, { method: 'DELETE' });
  }

  // Métodos específicos para autenticação
  async login(cpf: string, senha: string): Promise<ApiResponse> {
    try {
      const response = await this.post('/login', { cpf, senha });
      
      if (response.access_token) {
        this.setAuthToken(response.access_token);
        return {
          success: true,
          token: response.access_token,
          user: response.user,
          message: 'Login realizado com sucesso',
        };
      }

      return {
        success: false,
        message: response.message || 'Erro no login',
      };

    } catch (error: any) {
      return {
        success: false,
        message: error.message || 'Erro de conexão',
        error: error.message,
      };
    }
  }

  async refreshToken(): Promise<boolean> {
    try {
      const response = await this.post('/refresh-token');
      
      if (response.access_token) {
        this.setAuthToken(response.access_token);
        await AsyncStorage.setItem('auth_token', response.access_token);
        return true;
      }

      return false;
    } catch (error) {
      return false;
    }
  }

  // Método para verificar conectividade
  async checkConnectivity(): Promise<boolean> {
    try {
      const response = await fetch(`${this.baseURL}/health`, {
        method: 'GET',
        timeout: 5000,
      } as any);
      
      return response.ok;
    } catch (error) {
      return false;
    }
  }

  // Método para fazer upload de arquivos
  async uploadFile(endpoint: string, file: any, fieldName = 'file'): Promise<ApiResponse> {
    try {
      const formData = new FormData();
      formData.append(fieldName, file);

      const headers = { ...this.getHeaders() };
      delete headers['Content-Type']; // Deixar o browser definir o Content-Type para FormData

      const response = await fetch(`${this.baseURL}${endpoint}`, {
        method: 'POST',
        headers,
        body: formData,
      });

      if (response.ok) {
        const data = await response.json();
        return { success: true, ...data };
      } else {
        const errorData = await response.json().catch(() => ({}));
        return {
          success: false,
          message: errorData.detail || errorData.message || 'Erro no upload',
        };
      }

    } catch (error: any) {
      return {
        success: false,
        message: error.message || 'Erro de conexão',
        error: error.message,
      };
    }
  }

  // Método para cancelar requests (para cleanup em componentes)
  createAbortController(): AbortController {
    return new AbortController();
  }

  async makeRequestWithAbort<T>(
    endpoint: string, 
    abortController: AbortController,
    config: Partial<RequestConfig> = {}
  ): Promise<T> {
    const url = `${this.baseURL}${endpoint}`;
    
    const requestConfig: RequestConfig & { signal?: AbortSignal } = {
      method: 'GET',
      headers: this.getHeaders(),
      signal: abortController.signal,
      ...config,
    };

    const response = await fetch(url, requestConfig);
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || errorData.message || `Erro ${response.status}`);
    }

    return response.json();
  }
}

export const apiService = new ApiService();
