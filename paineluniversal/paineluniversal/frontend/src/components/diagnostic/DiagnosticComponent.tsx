import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { AlertTriangle, CheckCircle, XCircle, RefreshCw, Zap } from 'lucide-react';
import { diagnosticService, runQuickDiagnostic, autoFix } from '../../services/diagnostic';

interface DiagnosticComponentProps {
  onComplete?: (success: boolean) => void;
}

const DiagnosticComponent: React.FC<DiagnosticComponentProps> = ({ onComplete }) => {
  const [isRunning, setIsRunning] = useState(false);
  const [isFixing, setIsFixing] = useState(false);
  const [report, setReport] = useState<any>(null);
  const [autoRunCompleted, setAutoRunCompleted] = useState(false);

  // Executar diagnóstico automaticamente na primeira carga
  useEffect(() => {
    if (!autoRunCompleted) {
      handleRunDiagnostic();
      setAutoRunCompleted(true);
    }
  }, [autoRunCompleted]);

  const handleRunDiagnostic = async () => {
    setIsRunning(true);
    try {
      console.log('🔍 Executando diagnóstico...');
      const result = await runQuickDiagnostic();
      setReport(result);
      
      if (onComplete) {
        onComplete(result.overall_status === 'HEALTHY');
      }
    } catch (error) {
      console.error('❌ Erro no diagnóstico:', error);
    } finally {
      setIsRunning(false);
    }
  };

  const handleAutoFix = async () => {
    setIsFixing(true);
    try {
      console.log('🔧 Executando auto-correção...');
      const fixed = await autoFix();
      
      if (fixed) {
        // Re-executar diagnóstico após correção
        await handleRunDiagnostic();
      }
    } catch (error) {
      console.error('❌ Erro na auto-correção:', error);
    } finally {
      setIsFixing(false);
    }
  };

  const getStatusIcon = (success: boolean) => {
    return success ? (
      <CheckCircle className="h-4 w-4 text-green-500" />
    ) : (
      <XCircle className="h-4 w-4 text-red-500" />
    );
  };

  const getOverallStatusColor = (status: string) => {
    switch (status) {
      case 'HEALTHY':
        return 'bg-green-500';
      case 'WARNING':
        return 'bg-yellow-500';
      case 'CRITICAL':
        return 'bg-red-500';
      default:
        return 'bg-gray-500';
    }
  };

  return (
    <div className="max-w-4xl mx-auto p-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Zap className="h-5 w-5" />
            Diagnóstico do Sistema
          </CardTitle>
          <CardDescription>
            Verificação completa da conectividade e funcionalidade do sistema
          </CardDescription>
        </CardHeader>
        
        <CardContent className="space-y-6">
          {/* Controles */}
          <div className="flex gap-3">
            <Button 
              onClick={handleRunDiagnostic} 
              disabled={isRunning || isFixing}
              className="flex items-center gap-2"
            >
              <RefreshCw className={`h-4 w-4 ${isRunning ? 'animate-spin' : ''}`} />
              {isRunning ? 'Diagnosticando...' : 'Executar Diagnóstico'}
            </Button>
            
            {report && report.overall_status !== 'HEALTHY' && (
              <Button 
                onClick={handleAutoFix} 
                disabled={isRunning || isFixing}
                variant="secondary"
                className="flex items-center gap-2"
              >
                <Zap className={`h-4 w-4 ${isFixing ? 'animate-pulse' : ''}`} />
                {isFixing ? 'Corrigindo...' : 'Auto-Correção'}
              </Button>
            )}
          </div>

          {report && (
            <>
              {/* Status Geral */}
              <div className="p-4 border rounded-lg">
                <div className="flex items-center justify-between mb-3">
                  <h3 className="text-lg font-semibold">Status Geral</h3>
                  <Badge className={getOverallStatusColor(report.overall_status)}>
                    {report.overall_status}
                  </Badge>
                </div>
                
                <div className="space-y-2">
                  {report.recommendations.map((rec: string, index: number) => (
                    <div key={index} className="flex items-start gap-2 text-sm">
                      {rec.startsWith('✅') ? (
                        <CheckCircle className="h-4 w-4 text-green-500 mt-0.5" />
                      ) : rec.startsWith('⚠️') ? (
                        <AlertTriangle className="h-4 w-4 text-yellow-500 mt-0.5" />
                      ) : (
                        <XCircle className="h-4 w-4 text-red-500 mt-0.5" />
                      )}
                      <span>{rec.replace(/^[✅⚠️❌]\s*/, '')}</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Testes Individuais */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* Backend */}
                <Card>
                  <CardHeader className="pb-3">
                    <CardTitle className="text-base flex items-center gap-2">
                      {getStatusIcon(report.backend_status.success)}
                      Backend
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-sm text-muted-foreground">
                      {report.backend_status.message}
                    </p>
                    {report.backend_status.details && (
                      <div className="mt-2 text-xs text-muted-foreground">
                        Ambiente: {report.backend_status.details.environment}
                      </div>
                    )}
                  </CardContent>
                </Card>

                {/* CORS */}
                <Card>
                  <CardHeader className="pb-3">
                    <CardTitle className="text-base flex items-center gap-2">
                      {getStatusIcon(report.cors_test.success)}
                      CORS
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-sm text-muted-foreground">
                      {report.cors_test.message}
                    </p>
                  </CardContent>
                </Card>

                {/* Autenticação */}
                <Card>
                  <CardHeader className="pb-3">
                    <CardTitle className="text-base flex items-center gap-2">
                      {getStatusIcon(report.auth_status.success)}
                      Autenticação
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-sm text-muted-foreground">
                      {report.auth_status.message}
                    </p>
                  </CardContent>
                </Card>

                {/* Token */}
                <Card>
                  <CardHeader className="pb-3">
                    <CardTitle className="text-base flex items-center gap-2">
                      {getStatusIcon(report.token_validation.success)}
                      Token
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-sm text-muted-foreground">
                      {report.token_validation.message}
                    </p>
                  </CardContent>
                </Card>
              </div>

              {/* Endpoints da API */}
              <div>
                <h3 className="text-lg font-semibold mb-3">Endpoints da API</h3>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  {Object.entries(report.api_endpoints).map(([key, endpoint]: [string, any]) => (
                    <Card key={key}>
                      <CardHeader className="pb-3">
                        <CardTitle className="text-sm flex items-center gap-2">
                          {getStatusIcon(endpoint.success)}
                          {key.charAt(0).toUpperCase() + key.slice(1)}
                        </CardTitle>
                      </CardHeader>
                      <CardContent>
                        <p className="text-xs text-muted-foreground">
                          {endpoint.message}
                        </p>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              </div>

              {/* Debug Info */}
              <details className="border rounded-lg p-4">
                <summary className="font-medium cursor-pointer">
                  Informações Técnicas (Debug)
                </summary>
                <pre className="mt-3 text-xs bg-muted p-3 rounded overflow-auto">
                  {JSON.stringify(report, null, 2)}
                </pre>
              </details>
            </>
          )}

          {!report && !isRunning && (
            <div className="text-center text-muted-foreground">
              Clique em "Executar Diagnóstico" para verificar o sistema
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default DiagnosticComponent;
