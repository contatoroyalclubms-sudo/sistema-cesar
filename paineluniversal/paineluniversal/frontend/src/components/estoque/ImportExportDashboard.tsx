import React, { useState, useEffect } from 'react';
import { Activity, TrendingUp, AlertTriangle, Clock, Upload, Download, FileText, RefreshCw, Trash2 } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';
import { Alert, AlertDescription } from '../ui/alert';
import { Progress } from '../ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/select';
import { inventoryService } from '../../services/inventory';

interface DashboardStats {
  importacoes_hoje: number;
  produtos_atualizados: number;
  ultimo_import_erros: number;
  tempo_medio_processo: number;
}

interface RecentOperation {
  id: number;
  tipo: 'IMPORTACAO' | 'EXPORTACAO';
  arquivo: string;
  status: 'PENDENTE' | 'PROCESSANDO' | 'CONCLUIDA' | 'ERRO' | 'CANCELADA';
  total_registros: number;
  registros_sucesso: number;
  registros_erro: number;
  criado_em: string;
  inicio_processamento?: string;
  fim_processamento?: string;
}

const STATUS_COLORS = {
  PENDENTE: 'bg-yellow-100 text-yellow-800',
  PROCESSANDO: 'bg-blue-100 text-blue-800',
  CONCLUIDA: 'bg-green-100 text-green-800',
  ERRO: 'bg-red-100 text-red-800',
  CANCELADA: 'bg-gray-100 text-gray-800'
};

const STATUS_ICONS = {
  PENDENTE: Clock,
  PROCESSANDO: RefreshCw,
  CONCLUIDA: FileText,
  ERRO: AlertTriangle,
  CANCELADA: Trash2
};

export const ImportExportDashboard: React.FC = () => {
  const [stats, setStats] = useState<DashboardStats>({
    importacoes_hoje: 0,
    produtos_atualizados: 0,
    ultimo_import_erros: 0,
    tempo_medio_processo: 0
  });
  
  const [recentOperations, setRecentOperations] = useState<RecentOperation[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [statusFilter, setStatusFilter] = useState<string>('');

  useEffect(() => {
    loadDashboardData();
    
    // Atualizar dados a cada 30 segundos
    const interval = setInterval(loadDashboardData, 30000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    loadRecentOperations();
  }, [statusFilter]);

  const loadDashboardData = async () => {
    try {
      const response = await inventoryService.getDashboardStats();
      setStats(response.stats);
      setRecentOperations(response.recent_operations);
    } catch (error: any) {
      setError(error.message || 'Erro ao carregar dados do dashboard');
      console.error('Erro no dashboard:', error);
      
      // Fallback com dados mockados
      setStats({
        importacoes_hoje: 12,
        produtos_atualizados: 245,
        ultimo_import_erros: 3,
        tempo_medio_processo: 45.2
      });
      
      setRecentOperations([
        {
          id: 1,
          tipo: 'IMPORTACAO',
          arquivo: 'produtos_bebidas.xlsx',
          status: 'CONCLUIDA',
          total_registros: 150,
          registros_sucesso: 147,
          registros_erro: 3,
          criado_em: new Date().toISOString()
        },
        {
          id: 2,
          tipo: 'EXPORTACAO',
          arquivo: 'estoque_completo.csv',
          status: 'CONCLUIDA',
          total_registros: 1247,
          registros_sucesso: 1247,
          registros_erro: 0,
          criado_em: new Date(Date.now() - 3600000).toISOString()
        },
        {
          id: 3,
          tipo: 'IMPORTACAO',
          arquivo: 'produtos_comidas.csv',
          status: 'PROCESSANDO',
          total_registros: 89,
          registros_sucesso: 45,
          registros_erro: 0,
          criado_em: new Date(Date.now() - 1800000).toISOString()
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  const loadRecentOperations = async () => {
    try {
      const operations = await inventoryService.getImportExportJobs(20, statusFilter);
      setRecentOperations(operations);
    } catch (error: any) {
      console.error('Erro ao carregar operações:', error);
    }
  };

  const cancelJob = async (jobId: number) => {
    try {
      await inventoryService.cancelJob(jobId);
      loadRecentOperations();
    } catch (error: any) {
      setError(error.message || 'Erro ao cancelar operação');
    }
  };

  const formatDuration = (startTime?: string, endTime?: string) => {
    if (!startTime) return '-';
    
    const start = new Date(startTime);
    const end = endTime ? new Date(endTime) : new Date();
    const diffMs = end.getTime() - start.getTime();
    const diffSeconds = Math.floor(diffMs / 1000);
    
    if (diffSeconds < 60) {
      return `${diffSeconds}s`;
    } else if (diffSeconds < 3600) {
      return `${Math.floor(diffSeconds / 60)}m ${diffSeconds % 60}s`;
    } else {
      const hours = Math.floor(diffSeconds / 3600);
      const minutes = Math.floor((diffSeconds % 3600) / 60);
      return `${hours}h ${minutes}m`;
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  const getProgressPercentage = (operation: RecentOperation) => {
    if (operation.status === 'CONCLUIDA') return 100;
    if (operation.status === 'ERRO' || operation.status === 'CANCELADA') return 0;
    if (operation.total_registros === 0) return 0;
    
    const processedRecords = operation.registros_sucesso + operation.registros_erro;
    return Math.floor((processedRecords / operation.total_registros) * 100);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <RefreshCw className="w-6 h-6 animate-spin" />
        <span className="ml-2">Carregando...</span>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {error && (
        <Alert variant="destructive">
          <AlertTriangle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/* Estatísticas */}
      <div className="grid grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Importações Hoje</p>
                <p className="text-2xl font-bold text-blue-600">{stats.importacoes_hoje}</p>
              </div>
              <div className="h-8 w-8 bg-blue-100 rounded-full flex items-center justify-center">
                <Upload className="h-4 w-4 text-blue-600" />
              </div>
            </div>
            <div className="flex items-center mt-2">
              <TrendingUp className="h-3 w-3 text-green-500 mr-1" />
              <span className="text-xs text-green-600">+12% vs ontem</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Produtos Atualizados</p>
                <p className="text-2xl font-bold text-green-600">{stats.produtos_atualizados}</p>
              </div>
              <div className="h-8 w-8 bg-green-100 rounded-full flex items-center justify-center">
                <Activity className="h-4 w-4 text-green-600" />
              </div>
            </div>
            <div className="flex items-center mt-2">
              <TrendingUp className="h-3 w-3 text-green-500 mr-1" />
              <span className="text-xs text-green-600">+5% vs ontem</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Erros Último Import</p>
                <p className="text-2xl font-bold text-red-600">{stats.ultimo_import_erros}</p>
              </div>
              <div className="h-8 w-8 bg-red-100 rounded-full flex items-center justify-center">
                <AlertTriangle className="h-4 w-4 text-red-600" />
              </div>
            </div>
            <div className="flex items-center mt-2">
              <span className="text-xs text-red-600">-3 vs importação anterior</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Tempo Médio</p>
                <p className="text-2xl font-bold text-purple-600">
                  {stats.tempo_medio_processo.toFixed(1)}s
                </p>
              </div>
              <div className="h-8 w-8 bg-purple-100 rounded-full flex items-center justify-center">
                <Clock className="h-4 w-4 text-purple-600" />
              </div>
            </div>
            <div className="flex items-center mt-2">
              <span className="text-xs text-green-600">-8% vs média anterior</span>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Operações Recentes */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle>Operações Recentes</CardTitle>
            <div className="flex items-center gap-2">
              <Select value={statusFilter} onValueChange={setStatusFilter}>
                <SelectTrigger className="w-40">
                  <SelectValue placeholder="Todos os status" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="">Todos</SelectItem>
                  <SelectItem value="PENDENTE">Pendente</SelectItem>
                  <SelectItem value="PROCESSANDO">Processando</SelectItem>
                  <SelectItem value="CONCLUIDA">Concluída</SelectItem>
                  <SelectItem value="ERRO">Erro</SelectItem>
                  <SelectItem value="CANCELADA">Cancelada</SelectItem>
                </SelectContent>
              </Select>
              <Button variant="outline" size="sm" onClick={loadDashboardData}>
                <RefreshCw className="w-4 h-4" />
              </Button>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {recentOperations.length === 0 ? (
              <div className="text-center py-8 text-gray-500">
                Nenhuma operação encontrada
              </div>
            ) : (
              recentOperations.map((operation) => {
                const StatusIcon = STATUS_ICONS[operation.status];
                const progress = getProgressPercentage(operation);
                
                return (
                  <div key={operation.id} className="flex items-center justify-between p-4 border rounded-lg">
                    <div className="flex items-center gap-4">
                      <div className="flex items-center gap-2">
                        {operation.tipo === 'IMPORTACAO' ? (
                          <Upload className="w-4 h-4 text-blue-600" />
                        ) : (
                          <Download className="w-4 h-4 text-green-600" />
                        )}
                        <StatusIcon className={`w-4 h-4 ${
                          operation.status === 'PROCESSANDO' ? 'animate-spin' : ''
                        }`} />
                      </div>
                      
                      <div className="min-w-0 flex-1">
                        <div className="flex items-center gap-2">
                          <p className="font-medium truncate">{operation.arquivo}</p>
                          <Badge className={STATUS_COLORS[operation.status]}>
                            {operation.status}
                          </Badge>
                        </div>
                        
                        <div className="flex items-center gap-4 text-sm text-gray-600 mt-1">
                          <span>{operation.total_registros} registros</span>
                          {operation.registros_sucesso > 0 && (
                            <span className="text-green-600">
                              {operation.registros_sucesso} sucessos
                            </span>
                          )}
                          {operation.registros_erro > 0 && (
                            <span className="text-red-600">
                              {operation.registros_erro} erros
                            </span>
                          )}
                          <span>
                            {formatDuration(operation.inicio_processamento, operation.fim_processamento)}
                          </span>
                        </div>
                        
                        {operation.status === 'PROCESSANDO' && (
                          <div className="mt-2">
                            <Progress value={progress} className="h-2" />
                            <span className="text-xs text-gray-500">{progress}% concluído</span>
                          </div>
                        )}
                      </div>
                    </div>
                    
                    <div className="flex items-center gap-2">
                      <span className="text-xs text-gray-500">
                        {new Date(operation.criado_em).toLocaleString()}
                      </span>
                      
                      {(operation.status === 'PENDENTE' || operation.status === 'PROCESSANDO') && (
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => cancelJob(operation.id)}
                          className="text-red-600 hover:text-red-700"
                        >
                          <Trash2 className="w-3 h-3" />
                        </Button>
                      )}
                    </div>
                  </div>
                );
              })
            )}
          </div>
        </CardContent>
      </Card>

      {/* Ações Rápidas */}
      <Card>
        <CardHeader>
          <CardTitle>Ações Rápidas</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-4 gap-4">
            <Button variant="outline" className="h-20 flex flex-col items-center gap-2">
              <Upload className="w-6 h-6" />
              <span className="text-sm">Importar CSV</span>
            </Button>
            <Button variant="outline" className="h-20 flex flex-col items-center gap-2">
              <Download className="w-6 h-6" />
              <span className="text-sm">Exportar Excel</span>
            </Button>
            <Button variant="outline" className="h-20 flex flex-col items-center gap-2">
              <FileText className="w-6 h-6" />
              <span className="text-sm">Templates</span>
            </Button>
            <Button variant="outline" className="h-20 flex flex-col items-center gap-2">
              <Activity className="w-6 h-6" />
              <span className="text-sm">Relatórios</span>
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};