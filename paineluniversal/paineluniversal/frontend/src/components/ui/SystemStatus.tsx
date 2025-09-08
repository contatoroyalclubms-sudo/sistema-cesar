import React, { useState, useEffect } from 'react';
import { Alert, AlertDescription } from "../ui/alert";
import { Loader2, CheckCircle, AlertCircle, Clock } from 'lucide-react';
import { publicApi } from '../../services/api';

interface SystemStatusProps {
  onStatusChange?: (isOnline: boolean) => void;
}

const SystemStatus: React.FC<SystemStatusProps> = ({ onStatusChange }) => {
  const [status, setStatus] = useState<'checking' | 'online' | 'slow' | 'offline'>('checking');
  const [lastCheck, setLastCheck] = useState<Date | null>(null);

  const checkStatus = async () => {
    setStatus('checking');
    const startTime = Date.now();
    
    try {
      await publicApi.get('/healthz', { timeout: 5000 });
      const responseTime = Date.now() - startTime;
      
      if (responseTime > 3000) {
        setStatus('slow');
      } else {
        setStatus('online');
      }
      
      setLastCheck(new Date());
      onStatusChange?.(true);
      
    } catch (error) {
      console.error('Sistema offline:', error);
      setStatus('offline');
      onStatusChange?.(false);
    }
  };

  useEffect(() => {
    checkStatus();
    
    // Verificar status a cada 30 segundos
    const interval = setInterval(checkStatus, 30000);
    
    return () => clearInterval(interval);
  }, []);

  const getStatusConfig = () => {
    switch (status) {
      case 'checking':
        return {
          icon: <Loader2 className="h-4 w-4 animate-spin" />,
          color: 'bg-blue-50 border-blue-200 text-blue-700',
          message: 'Verificando status do sistema...'
        };
      case 'online':
        return {
          icon: <CheckCircle className="h-4 w-4" />,
          color: 'bg-green-50 border-green-200 text-green-700',
          message: 'Sistema funcionando normalmente'
        };
      case 'slow':
        return {
          icon: <Clock className="h-4 w-4" />,
          color: 'bg-yellow-50 border-yellow-200 text-yellow-700',
          message: 'Sistema respondendo lentamente'
        };
      case 'offline':
        return {
          icon: <AlertCircle className="h-4 w-4" />,
          color: 'bg-red-50 border-red-200 text-red-700',
          message: 'Sistema temporariamente indisponível'
        };
      default:
        return {
          icon: <AlertCircle className="h-4 w-4" />,
          color: 'bg-gray-50 border-gray-200 text-gray-700',
          message: 'Status desconhecido'
        };
    }
  };

  const config = getStatusConfig();

  if (status === 'online') {
    return null; // Não mostrar nada quando tudo está funcionando
  }

  return (
    <Alert className={`mb-4 ${config.color}`}>
      <div className="flex items-center gap-2">
        {config.icon}
        <AlertDescription>
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2">
            <span>{config.message}</span>
            {lastCheck && (
              <span className="text-xs opacity-75">
                Última verificação: {lastCheck.toLocaleTimeString()}
              </span>
            )}
          </div>
          {status === 'offline' && (
            <div className="mt-2 space-y-1 text-sm">
              <p>• Verifique sua conexão com a internet</p>
              <p>• Tente novamente em alguns minutos</p>
              <p>• Se o problema persistir, entre em contato com o suporte</p>
            </div>
          )}
          {status === 'slow' && (
            <div className="mt-2 text-sm">
              <p>O sistema pode demorar mais que o normal para responder.</p>
            </div>
          )}
        </AlertDescription>
      </div>
    </Alert>
  );
};

export default SystemStatus;
