import { api, publicApi } from './api';

interface DiagnosticResult {
  success: boolean;
  message: string;
  details?: any;
  timestamp: string;
}

interface DiagnosticReport {
  backend_status: DiagnosticResult;
  cors_test: DiagnosticResult;
  auth_status: DiagnosticResult;
  token_validation: DiagnosticResult;
  api_endpoints: {
    dashboard: DiagnosticResult;
    eventos: DiagnosticResult;
    usuarios: DiagnosticResult;
  };
  localStorage_status: DiagnosticResult;
  overall_status: 'HEALTHY' | 'WARNING' | 'CRITICAL';
  recommendations: string[];
}

export class ConnectivityDiagnostic {
  
  private createResult(success: boolean, message: string, details?: any): DiagnosticResult {
    return {
      success,
      message,
      details,
      timestamp: new Date().toISOString()
    };
  }

  async checkBackendHealth(): Promise<DiagnosticResult> {
    try {
      console.log('🏥 Verificando saúde do backend...');
      const response = await publicApi.get('/api/health', { timeout: 10000 });
      
      if (response.status === 200 && (response.data?.status === 'ok' || response.data?.status === 'healthy')) {
        return this.createResult(true, 'Backend funcionando corretamente', {
          service: response.data.service,
          version: response.data.version,
          environment: response.data.environment,
          database: response.data.database,
          timestamp: response.data.timestamp
        });
      }
      
      return this.createResult(false, 'Backend retornou resposta inesperada', response.data);
    } catch (error: any) {
      console.error('❌ Erro no backend:', error);
      return this.createResult(false, `Erro de conectividade: ${error.message}`, {
        code: error.code,
        status: error.response?.status
      });
    }
  }

  async checkCORS(): Promise<DiagnosticResult> {
    try {
      console.log('🔗 Verificando CORS...');
      const response = await publicApi.get('/api/cors-test', { timeout: 10000 });
      
      if (response.status === 200 && response.data?.success) {
        return this.createResult(true, 'CORS funcionando corretamente', {
          middleware: response.data.cors_info?.middleware,
          protection_level: response.data.cors_info?.protection_level
        });
      }
      
      return this.createResult(false, 'CORS com problemas', response.data);
    } catch (error: any) {
      console.error('❌ Erro de CORS:', error);
      return this.createResult(false, `Erro de CORS: ${error.message}`, {
        is_cors_error: error.message?.includes('CORS') || error.message?.includes('Access-Control')
      });
    }
  }

  checkLocalStorageAuth(): DiagnosticResult {
    try {
      console.log('💾 Verificando localStorage...');
      const token = localStorage.getItem('token');
      const usuario = localStorage.getItem('usuario');
      
      const hasToken = !!token && token !== 'undefined' && token !== 'null';
      const hasUsuario = !!usuario && usuario !== 'undefined' && usuario !== 'null';
      
      let usuarioData = null;
      if (hasUsuario) {
        try {
          usuarioData = JSON.parse(usuario);
        } catch (e) {
          return this.createResult(false, 'Dados do usuário corrompidos no localStorage', {
            has_token: hasToken,
            usuario_parse_error: e
          });
        }
      }
      
      if (hasToken) {
        return this.createResult(true, 'Dados de autenticação encontrados', {
          token_length: token?.length,
          has_usuario: hasUsuario,
          usuario_nome: usuarioData?.nome,
          usuario_tipo: usuarioData?.tipo
        });
      }
      
      return this.createResult(false, 'Nenhum token de autenticação encontrado', {
        has_token: hasToken,
        has_usuario: hasUsuario
      });
    } catch (error: any) {
      return this.createResult(false, `Erro ao verificar localStorage: ${error.message}`);
    }
  }

  async validateToken(): Promise<DiagnosticResult> {
    try {
      console.log('🔑 Validando token...');
      const token = localStorage.getItem('token');
      
      if (!token || token === 'undefined' || token === 'null') {
        return this.createResult(false, 'Token não encontrado');
      }
      
      // Tentar fazer uma requisição autenticada
      const response = await api.get('/api/auth/me', { timeout: 10000 });
      
      if (response.status === 200 && response.data) {
        return this.createResult(true, 'Token válido e usuário autenticado', {
          usuario_id: response.data.id,
          usuario_nome: response.data.nome,
          usuario_tipo: response.data.tipo
        });
      }
      
      return this.createResult(false, 'Token inválido ou resposta inesperada', response.data);
    } catch (error: any) {
      console.error('❌ Erro de validação de token:', error);
      
      if (error.response?.status === 401) {
        return this.createResult(false, 'Token expirado ou inválido (401)', {
          status: 401,
          detail: error.response.data?.detail
        });
      }
      
      return this.createResult(false, `Erro na validação: ${error.message}`, {
        status: error.response?.status,
        code: error.code
      });
    }
  }

  async testApiEndpoint(endpoint: string, description: string): Promise<DiagnosticResult> {
    try {
      console.log(`🧪 Testando endpoint: ${endpoint}`);
      const response = await api.get(endpoint, { timeout: 10000 });
      
      if (response.status === 200) {
        return this.createResult(true, `${description} funcionando`, {
          status: response.status,
          data_type: typeof response.data,
          has_data: !!response.data
        });
      }
      
      return this.createResult(false, `${description} retornou status ${response.status}`, {
        status: response.status,
        data: response.data
      });
    } catch (error: any) {
      console.error(`❌ Erro no endpoint ${endpoint}:`, error);
      
      if (error.response?.status === 401) {
        return this.createResult(false, `${description} - Não autenticado (401)`, {
          status: 401,
          auth_error: true
        });
      }
      
      return this.createResult(false, `${description} - Erro: ${error.message}`, {
        status: error.response?.status,
        code: error.code
      });
    }
  }

  async runFullDiagnostic(): Promise<DiagnosticReport> {
    console.log('🔍 Iniciando diagnóstico completo...');
    
    const report: DiagnosticReport = {
      backend_status: await this.checkBackendHealth(),
      cors_test: await this.checkCORS(),
      auth_status: this.checkLocalStorageAuth(),
      token_validation: await this.validateToken(),
      api_endpoints: {
        dashboard: await this.testApiEndpoint('/api/dashboard/avancado', 'Dashboard'),
        eventos: await this.testApiEndpoint('/api/eventos/', 'Eventos'),
        usuarios: await this.testApiEndpoint('/api/usuarios/', 'Usuários')
      },
      localStorage_status: this.checkLocalStorageAuth(),
      overall_status: 'CRITICAL',
      recommendations: []
    };

    // Determinar status geral e recomendações
    if (!report.backend_status.success) {
      report.overall_status = 'CRITICAL';
      report.recommendations.push('❌ Backend não está funcionando - verifique a conexão de rede');
    } else if (!report.cors_test.success) {
      report.overall_status = 'CRITICAL';
      report.recommendations.push('❌ Problemas de CORS - verifique a configuração do servidor');
    } else if (!report.auth_status.success) {
      report.overall_status = 'WARNING';
      report.recommendations.push('⚠️ Usuário não autenticado - faça login novamente');
    } else if (!report.token_validation.success) {
      report.overall_status = 'WARNING';
      report.recommendations.push('⚠️ Token inválido ou expirado - faça login novamente');
    } else if (Object.values(report.api_endpoints).some(endpoint => !endpoint.success)) {
      report.overall_status = 'WARNING';
      report.recommendations.push('⚠️ Alguns endpoints com problemas - verifique permissões');
    } else {
      report.overall_status = 'HEALTHY';
      report.recommendations.push('✅ Sistema funcionando corretamente');
    }

    console.log('📊 Diagnóstico completo:', report);
    return report;
  }

  async fixCommonIssues(): Promise<boolean> {
    console.log('🔧 Tentando corrigir problemas comuns...');
    
    try {
      // 1. Limpar dados corrompidos
      const token = localStorage.getItem('token');
      const usuario = localStorage.getItem('usuario');
      
      if (token === 'undefined' || usuario === 'undefined') {
        console.log('🧹 Limpando dados corrompidos...');
        localStorage.removeItem('token');
        localStorage.removeItem('usuario');
      }
      
      // 2. Validar JSON do usuário
      if (usuario && usuario !== 'null') {
        try {
          JSON.parse(usuario);
        } catch (e) {
          console.log('🧹 Removendo dados de usuário corrompidos...');
          localStorage.removeItem('usuario');
        }
      }
      
      // 3. Verificar se o token ainda é válido
      if (token && token !== 'null') {
        try {
          await api.get('/api/auth/me');
          console.log('✅ Token validado com sucesso');
          return true;
        } catch (error: any) {
          if (error.response?.status === 401) {
            console.log('🧹 Removendo token expirado...');
            localStorage.removeItem('token');
            localStorage.removeItem('usuario');
          }
        }
      }
      
      return false;
    } catch (error) {
      console.error('❌ Erro ao tentar corrigir problemas:', error);
      return false;
    }
  }
}

// Instância singleton
export const diagnosticService = new ConnectivityDiagnostic();

// Função helper para uso rápido
export const runQuickDiagnostic = async () => {
  const diagnostic = new ConnectivityDiagnostic();
  return await diagnostic.runFullDiagnostic();
};

// Função para auto-correção
export const autoFix = async () => {
  const diagnostic = new ConnectivityDiagnostic();
  return await diagnostic.fixCommonIssues();
};

export default diagnosticService;
