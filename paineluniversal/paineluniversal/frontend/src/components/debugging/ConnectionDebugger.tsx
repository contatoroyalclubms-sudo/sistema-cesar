import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { getBackendStatus, forceBackendSwitch } from '@/lib/api';
import { authService } from '../../services';

interface ConnectionStatus {
  backend: string;
  status: 'online' | 'offline' | 'testing';
  responseTime?: number;
  error?: string;
}

export function ConnectionDebugger() {
  const [isVisible, setIsVisible] = useState(false);
  const [connections, setConnections] = useState<ConnectionStatus[]>([]);
  const [isTestingAll, setIsTestingAll] = useState(false);
  const [backendStatus, setBackendStatus] = useState<any>(null);

  // Mostrar debug apenas se estiver em desenvolvimento ou debug ativado
  useEffect(() => {
    const shouldShow = 
      !import.meta.env.PROD || 
      localStorage.getItem('debug_connections') === 'true' ||
      window.location.search.includes('debug=true');
    
    setIsVisible(shouldShow);
  }, []);

  // Teste individual de backend
  const testSingleBackend = async (backend: string): Promise<ConnectionStatus> => {
    try {
      const startTime = Date.now();
      const response = await fetch(`${backend}/healthz`, { 
        method: 'GET',
        signal: AbortSignal.timeout(5000)
      });
      const responseTime = Date.now() - startTime;
      
      if (response.ok) {
        return { backend, status: 'online', responseTime };
      } else {
        return { backend, status: 'offline', error: `HTTP ${response.status}` };
      }
    } catch (error: any) {
      return { 
        backend, 
        status: 'offline', 
        error: error.name === 'AbortError' ? 'Timeout' : error.message 
      };
    }
  };

  // Testar todos os backends
  const testAllBackends = async () => {
    setIsTestingAll(true);
    
    const backends = [
      'https://backend-painel-universal-production.up.railway.app',
      'https://paineluniversal-backend.up.railway.app',
      'https://backend-paineluniversal.up.railway.app',
      'https://api.paineluniversal.com',
      'http://localhost:8000'
    ];

    const results = await Promise.all(
      backends.map(backend => testSingleBackend(backend))
    );

    setConnections(results);
    setIsTestingAll(false);
  };

  // Atualizar status do sistema
  const updateBackendStatus = () => {
    const status = getBackendStatus();
    setBackendStatus(status);
  };

  // Teste de login completo
  const testFullLogin = async () => {
    try {
      console.log('🧪 Testando login completo...');
      
      // Testar com credenciais de teste
      const testCredentials = [
        { email: 'admin@teste.com', cpf: '00000000000', senha: '0000' },
        { email: '00000000000', cpf: '00000000000', senha: '0000' }
      ];

      for (const cred of testCredentials) {
        try {
          console.log(`🧪 Testando: ${cred.email}`);
          const result = await authService.login({
            cpf: cred.email,
            senha: cred.senha
          });
          console.log('✅ Login de teste bem-sucedido!', result);
          return;
        } catch (error) {
          console.log('❌ Falha no teste:', error);
        }
      }
    } catch (error) {
      console.error('❌ Erro no teste de login:', error);
    }
  };

  useEffect(() => {
    if (isVisible) {
      updateBackendStatus();
      testAllBackends();
      
      // Atualizar a cada 30 segundos
      const interval = setInterval(() => {
        updateBackendStatus();
        testAllBackends();
      }, 30000);

      return () => clearInterval(interval);
    }
  }, [isVisible]);

  if (!isVisible) {
    return (
      <Button 
        variant="outline" 
        size="sm" 
        onClick={() => setIsVisible(true)}
        className="fixed bottom-4 right-4 z-50"
      >
        🔧 Debug
      </Button>
    );
  }

  return (
    <Card className="fixed bottom-4 right-4 w-96 max-h-96 overflow-auto z-50 shadow-lg">
      <CardHeader className="pb-3">
        <div className="flex justify-between items-center">
          <CardTitle className="text-sm">🔧 Connection Debugger</CardTitle>
          <Button 
            variant="ghost" 
            size="sm" 
            onClick={() => setIsVisible(false)}
          >
            ✕
          </Button>
        </div>
      </CardHeader>
      
      <CardContent className="space-y-3">
        {/* Status Atual */}
        {backendStatus && (
          <div className="text-xs space-y-1">
            <div className="font-medium">📊 Status Atual:</div>
            <div>Backend: {backendStatus.currentBackend}</div>
            <div>Produção: {backendStatus.isProduction ? '✅' : '❌'}</div>
            <div>Health Check: {backendStatus.healthCheckActive ? '🔄' : '⏸️'}</div>
            <div>Fallbacks: {backendStatus.totalBackends - 1}</div>
          </div>
        )}

        {/* Lista de Backends */}
        <div className="space-y-2">
          <div className="flex justify-between items-center">
            <span className="text-xs font-medium">🌐 Backends:</span>
            <Button 
              size="sm" 
              variant="outline" 
              onClick={testAllBackends}
              disabled={isTestingAll}
              className="text-xs h-6 px-2"
            >
              {isTestingAll ? '⏳' : '🔄'} Test
            </Button>
          </div>
          
          <div className="space-y-1">
            {connections.map((conn, index) => (
              <div key={index} className="flex justify-between items-center text-xs">
                <span className="truncate flex-1 pr-2">
                  {conn.backend.replace('https://', '').replace('http://', '')}
                </span>
                <div className="flex items-center space-x-1">
                  {conn.responseTime && (
                    <span className="text-gray-500">{conn.responseTime}ms</span>
                  )}
                  <Badge 
                    variant={conn.status === 'online' ? 'default' : 'destructive'}
                    className="text-xs h-4 px-1"
                  >
                    {conn.status === 'online' ? '✅' : '❌'}
                  </Badge>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Ações de Debug */}
        <div className="space-y-2 pt-2 border-t">
          <Button 
            size="sm" 
            variant="outline" 
            onClick={forceBackendSwitch}
            className="w-full text-xs h-6"
          >
            🔄 Force Switch Backend
          </Button>
          
          <Button 
            size="sm" 
            variant="outline" 
            onClick={testFullLogin}
            className="w-full text-xs h-6"
          >
            🧪 Test Login Flow
          </Button>
          
          <Button 
            size="sm" 
            variant="outline" 
            onClick={() => {
              localStorage.setItem('debug_api', 'true');
              window.location.reload();
            }}
            className="w-full text-xs h-6"
          >
            🔍 Enable API Debug
          </Button>
        </div>

        {/* Info de Desenvolvimento */}
        <div className="text-xs text-gray-500 pt-2 border-t">
          <div>Ambiente: {import.meta.env.PROD ? 'Produção' : 'Desenvolvimento'}</div>
          <div>URL: {window.location.hostname}</div>
          <div>Auto-Recovery: {import.meta.env.PROD ? 'Ativo' : 'Limitado'}</div>
        </div>
      </CardContent>
    </Card>
  );
}

export default ConnectionDebugger;
