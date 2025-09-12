import React, { useState, useEffect } from 'react';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import {
  Activity,
  AlertCircle,
  CheckCircle,
  Clock,
  Cloud,
  Database,
  Download,
  PlayCircle,
  RefreshCw,
  Settings,
  StopCircle,
  TrendingUp,
  Users,
  Zap,
} from 'lucide-react';
import api from '@/lib/api';

interface SyncStatus {
  running: boolean;
  interval: number;
  last_sync: string | null;
  next_sync: string | null;
  stats: {
    total_syncs: number;
    successful_syncs: number;
    failed_syncs: number;
    last_error: string | null;
  };
}

interface IntegrationStatus {
  connected: boolean;
  last_sync: string | null;
  sync_status: string | null;
  total_events: number;
  total_attendees: number;
  total_checkins: number;
  total_transactions: number;
  errors: string[];
  warnings: string[];
}

interface HealthStatus {
  status: string;
  meep_api: boolean;
  database: boolean;
  cache: boolean;
  version: string;
  timestamp: string;
}

const MEEPDashboardComplete: React.FC = () => {
  const [syncStatus, setSyncStatus] = useState<SyncStatus | null>(null);
  const [integrationStatus, setIntegrationStatus] = useState<IntegrationStatus | null>(null);
  const [healthStatus, setHealthStatus] = useState<HealthStatus | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSyncing, setIsSyncing] = useState(false);
  const [analyticsData, setAnalyticsData] = useState<any>(null);
  const [recentEvents, setRecentEvents] = useState<any[]>([]);

  // Cores para gráficos
  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8'];

  useEffect(() => {
    loadDashboardData();
    const interval = setInterval(loadDashboardData, 30000); // Atualizar a cada 30 segundos
    return () => clearInterval(interval);
  }, []);

  const loadDashboardData = async () => {
    try {
      const [sync, integration, health, analytics] = await Promise.all([
        api.get('/api/meep/sync/auto/status'),
        api.get('/api/meep/status'),
        api.get('/api/meep/health'),
        api.get('/api/meep/analytics/dashboard?period=week'),
      ]);

      setSyncStatus(sync.data);
      setIntegrationStatus(integration.data);
      setHealthStatus(health.data);
      setAnalyticsData(analytics.data);

      // Buscar eventos recentes
      const events = await api.get('/api/meep/events?limit=5');
      setRecentEvents(events.data);
    } catch (error) {
      console.error('Erro ao carregar dashboard:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleStartSync = async () => {
    try {
      await api.post('/api/meep/sync/auto/start');
      await loadDashboardData();
    } catch (error) {
      console.error('Erro ao iniciar sincronização:', error);
    }
  };

  const handleStopSync = async () => {
    try {
      await api.post('/api/meep/sync/auto/stop');
      await loadDashboardData();
    } catch (error) {
      console.error('Erro ao parar sincronização:', error);
    }
  };

  const handleForceSync = async () => {
    setIsSyncing(true);
    try {
      await api.post('/api/meep/sync/auto/force');
      setTimeout(() => {
        loadDashboardData();
        setIsSyncing(false);
      }, 3000);
    } catch (error) {
      console.error('Erro ao forçar sincronização:', error);
      setIsSyncing(false);
    }
  };

  const formatDateTime = (dateString: string | null) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleString('pt-BR');
  };

  const getHealthBadge = () => {
    if (!healthStatus) return null;
    
    const statusColors = {
      healthy: 'bg-green-500',
      degraded: 'bg-yellow-500',
      unhealthy: 'bg-red-500',
    };

    return (
      <Badge className={`${statusColors[healthStatus.status as keyof typeof statusColors]} text-white`}>
        {healthStatus.status.toUpperCase()}
      </Badge>
    );
  };

  const getSyncProgress = () => {
    if (!syncStatus?.stats) return 0;
    const { total_syncs, successful_syncs } = syncStatus.stats;
    if (total_syncs === 0) return 0;
    return (successful_syncs / total_syncs) * 100;
  };

  const prepareChartData = () => {
    if (!analyticsData) return [];
    
    // Dados fictícios para demonstração
    return [
      { name: 'Seg', eventos: 4, participantes: 24, checkins: 18 },
      { name: 'Ter', eventos: 3, participantes: 18, checkins: 12 },
      { name: 'Qua', eventos: 5, participantes: 30, checkins: 25 },
      { name: 'Qui', eventos: 2, participantes: 15, checkins: 10 },
      { name: 'Sex', eventos: 6, participantes: 40, checkins: 35 },
      { name: 'Sáb', eventos: 8, participantes: 60, checkins: 55 },
      { name: 'Dom', eventos: 4, participantes: 25, checkins: 20 },
    ];
  };

  const preparePieData = () => {
    if (!integrationStatus) return [];
    
    return [
      { name: 'Eventos', value: integrationStatus.total_events },
      { name: 'Participantes', value: integrationStatus.total_attendees },
      { name: 'Check-ins', value: integrationStatus.total_checkins },
      { name: 'Transações', value: integrationStatus.total_transactions },
    ];
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-96">
        <RefreshCw className="h-8 w-8 animate-spin" />
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">Dashboard MEEP Integration</h1>
          <p className="text-gray-500">Monitor e controle da integração com o portal MEEP</p>
        </div>
        <div className="flex gap-2">
          <Button onClick={loadDashboardData} variant="outline">
            <RefreshCw className="h-4 w-4 mr-2" />
            Atualizar
          </Button>
          <Button onClick={() => window.open('/api/meep/docs', '_blank')} variant="outline">
            <Settings className="h-4 w-4 mr-2" />
            API Docs
          </Button>
        </div>
      </div>

      {/* Status Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Health Status</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center justify-between">
              {getHealthBadge()}
              <div className="flex items-center gap-2">
                {healthStatus?.meep_api ? (
                  <Cloud className="h-5 w-5 text-green-500" />
                ) : (
                  <Cloud className="h-5 w-5 text-red-500" />
                )}
                {healthStatus?.database ? (
                  <Database className="h-5 w-5 text-green-500" />
                ) : (
                  <Database className="h-5 w-5 text-red-500" />
                )}
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Sincronização</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center justify-between">
              {syncStatus?.running ? (
                <Badge className="bg-green-500 text-white">
                  <Activity className="h-3 w-3 mr-1" />
                  ATIVA
                </Badge>
              ) : (
                <Badge variant="secondary">
                  <StopCircle className="h-3 w-3 mr-1" />
                  PARADA
                </Badge>
              )}
              <span className="text-xs text-gray-500">
                {syncStatus?.interval ? `${syncStatus.interval}s` : 'N/A'}
              </span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Taxa de Sucesso</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span>{syncStatus?.stats?.successful_syncs || 0}</span>
                <span className="text-gray-500">de {syncStatus?.stats?.total_syncs || 0}</span>
              </div>
              <Progress value={getSyncProgress()} className="h-2" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Última Sync</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <Clock className="h-4 w-4 text-gray-500" />
              <span className="text-sm">
                {syncStatus?.last_sync ? formatDateTime(syncStatus.last_sync) : 'Nunca'}
              </span>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Sync Controls */}
      <Card>
        <CardHeader>
          <CardTitle>Controle de Sincronização</CardTitle>
          <CardDescription>
            Gerencie a sincronização automática com o portal MEEP
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex gap-4">
            {!syncStatus?.running ? (
              <Button onClick={handleStartSync} className="bg-green-600 hover:bg-green-700">
                <PlayCircle className="h-4 w-4 mr-2" />
                Iniciar Sincronização
              </Button>
            ) : (
              <Button onClick={handleStopSync} variant="destructive">
                <StopCircle className="h-4 w-4 mr-2" />
                Parar Sincronização
              </Button>
            )}
            
            <Button
              onClick={handleForceSync}
              variant="outline"
              disabled={isSyncing}
            >
              {isSyncing ? (
                <>
                  <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                  Sincronizando...
                </>
              ) : (
                <>
                  <Zap className="h-4 w-4 mr-2" />
                  Forçar Sync Agora
                </>
              )}
            </Button>
          </div>

          {syncStatus?.stats?.last_error && (
            <Alert className="mt-4" variant="destructive">
              <AlertCircle className="h-4 w-4" />
              <AlertTitle>Último Erro</AlertTitle>
              <AlertDescription>{syncStatus.stats.last_error}</AlertDescription>
            </Alert>
          )}

          {syncStatus?.next_sync && syncStatus.running && (
            <div className="mt-4 p-3 bg-blue-50 rounded-lg">
              <div className="flex items-center gap-2">
                <Clock className="h-4 w-4 text-blue-600" />
                <span className="text-sm text-blue-800">
                  Próxima sincronização: {formatDateTime(syncStatus.next_sync)}
                </span>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Analytics Tabs */}
      <Tabs defaultValue="overview" className="space-y-4">
        <TabsList>
          <TabsTrigger value="overview">Visão Geral</TabsTrigger>
          <TabsTrigger value="events">Eventos</TabsTrigger>
          <TabsTrigger value="metrics">Métricas</TabsTrigger>
          <TabsTrigger value="logs">Logs</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Line Chart */}
            <Card>
              <CardHeader>
                <CardTitle>Atividade Semanal</CardTitle>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={prepareChartData()}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Line type="monotone" dataKey="participantes" stroke="#8884d8" />
                    <Line type="monotone" dataKey="checkins" stroke="#82ca9d" />
                  </LineChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            {/* Pie Chart */}
            <Card>
              <CardHeader>
                <CardTitle>Distribuição de Dados</CardTitle>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={preparePieData()}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={(entry) => `${entry.name}: ${entry.value}`}
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="value"
                    >
                      {preparePieData().map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </div>

          {/* Stats Grid */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <Card>
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-500">Total Eventos</p>
                    <p className="text-2xl font-bold">{integrationStatus?.total_events || 0}</p>
                  </div>
                  <TrendingUp className="h-8 w-8 text-blue-500" />
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-500">Participantes</p>
                    <p className="text-2xl font-bold">{integrationStatus?.total_attendees || 0}</p>
                  </div>
                  <Users className="h-8 w-8 text-green-500" />
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-500">Check-ins</p>
                    <p className="text-2xl font-bold">{integrationStatus?.total_checkins || 0}</p>
                  </div>
                  <CheckCircle className="h-8 w-8 text-purple-500" />
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-500">Transações</p>
                    <p className="text-2xl font-bold">{integrationStatus?.total_transactions || 0}</p>
                  </div>
                  <Activity className="h-8 w-8 text-orange-500" />
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="events" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Eventos Recentes</CardTitle>
              <CardDescription>Eventos sincronizados do portal MEEP</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {recentEvents.map((event, index) => (
                  <div key={index} className="flex items-center justify-between p-4 border rounded-lg">
                    <div>
                      <h3 className="font-semibold">{event.nome || 'Evento sem nome'}</h3>
                      <p className="text-sm text-gray-500">{event.local || 'Local não definido'}</p>
                      <p className="text-xs text-gray-400">
                        {event.data_inicio ? formatDateTime(event.data_inicio) : 'Data não definida'}
                      </p>
                    </div>
                    <div className="flex items-center gap-2">
                      <Badge>{event.tipo || 'OUTROS'}</Badge>
                      <Badge variant={event.status === 'ATIVO' ? 'default' : 'secondary'}>
                        {event.status || 'INATIVO'}
                      </Badge>
                    </div>
                  </div>
                ))}
                {recentEvents.length === 0 && (
                  <div className="text-center py-8 text-gray-500">
                    Nenhum evento encontrado
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="metrics" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Métricas de Sincronização</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="grid grid-cols-3 gap-4">
                  <div className="text-center">
                    <p className="text-3xl font-bold text-green-600">
                      {syncStatus?.stats?.successful_syncs || 0}
                    </p>
                    <p className="text-sm text-gray-500">Sincronizações Bem-sucedidas</p>
                  </div>
                  <div className="text-center">
                    <p className="text-3xl font-bold text-red-600">
                      {syncStatus?.stats?.failed_syncs || 0}
                    </p>
                    <p className="text-sm text-gray-500">Sincronizações Falhadas</p>
                  </div>
                  <div className="text-center">
                    <p className="text-3xl font-bold text-blue-600">
                      {syncStatus?.stats?.total_syncs || 0}
                    </p>
                    <p className="text-sm text-gray-500">Total de Sincronizações</p>
                  </div>
                </div>

                <div className="pt-4">
                  <ResponsiveContainer width="100%" height={200}>
                    <BarChart data={[
                      { name: 'Sucesso', value: syncStatus?.stats?.successful_syncs || 0 },
                      { name: 'Falha', value: syncStatus?.stats?.failed_syncs || 0 },
                    ]}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="name" />
                      <YAxis />
                      <Tooltip />
                      <Bar dataKey="value" fill="#8884d8" />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="logs" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Logs de Integração</CardTitle>
              <CardDescription>Histórico de operações e erros</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {integrationStatus?.errors && integrationStatus.errors.length > 0 ? (
                  integrationStatus.errors.map((error, index) => (
                    <Alert key={index} variant="destructive">
                      <AlertCircle className="h-4 w-4" />
                      <AlertDescription>{error}</AlertDescription>
                    </Alert>
                  ))
                ) : (
                  <div className="text-center py-8 text-gray-500">
                    Nenhum erro registrado
                  </div>
                )}
              </div>

              {integrationStatus?.warnings && integrationStatus.warnings.length > 0 && (
                <div className="mt-4 space-y-2">
                  <h3 className="font-semibold">Avisos</h3>
                  {integrationStatus.warnings.map((warning, index) => (
                    <Alert key={index}>
                      <AlertCircle className="h-4 w-4" />
                      <AlertDescription>{warning}</AlertDescription>
                    </Alert>
                  ))}
                </div>
              )}

              <div className="mt-4 flex justify-end">
                <Button variant="outline" size="sm">
                  <Download className="h-4 w-4 mr-2" />
                  Exportar Logs
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default MEEPDashboardComplete;