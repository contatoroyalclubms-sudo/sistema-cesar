import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { 
  BarChart3, 
  TrendingUp, 
  Users, 
  Clock, 
  Shield, 
  Activity,
  AlertTriangle,
  CheckCircle,
  XCircle,
  RefreshCw
} from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs';
import { useToast } from '../../hooks/use-toast';

interface MEEPAnalyticsProps {
  eventoId?: number;
}

interface AnalyticsData {
  fluxoHorario: Array<{ hora: string; entradas: number; saidas: number }>;
  equipamentos: Array<{ nome: string; status: string; ultimaAtividade: string }>;
  seguranca: {
    totalValidacoes: number;
    validacoesValidas: number;
    tentativasInvalidas: number;
    alertas: Array<{ tipo: string; descricao: string; timestamp: string }>;
  };
  metricas: {
    totalParticipantes: number;
    presencaAtual: number;
    taxaOcupacao: number;
    tempoMedioCheckin: number;
  };
}

const MEEPAnalytics: React.FC<MEEPAnalyticsProps> = ({ eventoId = 1 }) => {
  const [loading, setLoading] = useState(true);
  const [analytics, setAnalytics] = useState<AnalyticsData | null>(null);
  const [periodo, setPeriodo] = useState('24h');
  const { toast } = useToast();

  // Mock data para demonstração
  const mockData: AnalyticsData = {
    fluxoHorario: [
      { hora: '08:00', entradas: 12, saidas: 2 },
      { hora: '09:00', entradas: 25, saidas: 5 },
      { hora: '10:00', entradas: 48, saidas: 8 },
      { hora: '11:00', entradas: 62, saidas: 15 },
      { hora: '12:00', entradas: 35, saidas: 28 },
      { hora: '13:00', entradas: 18, saidas: 12 },
      { hora: '14:00', entradas: 45, saidas: 22 },
      { hora: '15:00', entradas: 38, saidas: 18 },
    ],
    equipamentos: [
      { nome: 'Tablet Check-in 01', status: 'online', ultimaAtividade: '2 min atrás' },
      { nome: 'QR Scanner 02', status: 'online', ultimaAtividade: '1 min atrás' },
      { nome: 'Tablet Check-in 03', status: 'offline', ultimaAtividade: '15 min atrás' },
      { nome: 'Impressora Tickets', status: 'warning', ultimaAtividade: '5 min atrás' },
    ],
    seguranca: {
      totalValidacoes: 287,
      validacoesValidas: 275,
      tentativasInvalidas: 12,
      alertas: [
        { tipo: 'warning', descricao: 'Múltiplas tentativas de acesso com CPF inválido', timestamp: '10:45' },
        { tipo: 'info', descricao: 'Pico de acesso detectado', timestamp: '11:20' },
        { tipo: 'error', descricao: 'Equipamento #3 offline', timestamp: '14:30' },
      ]
    },
    metricas: {
      totalParticipantes: 275,
      presencaAtual: 163,
      taxaOcupacao: 65.2,
      tempoMedioCheckin: 23
    }
  };

  useEffect(() => {
    const fetchAnalytics = async () => {
      setLoading(true);
      try {
        // Simular carregamento de dados
        await new Promise(resolve => setTimeout(resolve, 1000));
        setAnalytics(mockData);
      } catch (error) {
        toast({
          title: "Erro ao carregar analytics",
          description: "Não foi possível carregar os dados do MEEP Analytics",
          variant: "destructive",
        });
      } finally {
        setLoading(false);
      }
    };

    fetchAnalytics();
  }, [periodo, eventoId, toast]);

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'online': return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'offline': return <XCircle className="h-4 w-4 text-red-500" />;
      case 'warning': return <AlertTriangle className="h-4 w-4 text-yellow-500" />;
      default: return <Activity className="h-4 w-4 text-gray-500" />;
    }
  };

  const getStatusBadge = (status: string) => {
    const variants = {
      online: 'default',
      offline: 'destructive',
      warning: 'secondary',
    } as const;
    
    return <Badge variant={variants[status as keyof typeof variants] || 'outline'}>{status}</Badge>;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <RefreshCw className="h-8 w-8 animate-spin text-primary" />
        <span className="ml-2 text-lg">Carregando analytics MEEP...</span>
      </div>
    );
  }

  if (!analytics) {
    return (
      <div className="text-center py-12">
        <AlertTriangle className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
        <h3 className="text-lg font-semibold">Dados não disponíveis</h3>
        <p className="text-muted-foreground">Não foi possível carregar os analytics MEEP</p>
      </div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-6"
    >
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-foreground">MEEP Analytics</h1>
          <p className="text-muted-foreground">
            Analytics avançado com insights em tempo real
          </p>
        </div>
        
        <div className="flex gap-2">
          <Button 
            variant="outline" 
            onClick={() => window.location.reload()}
          >
            <RefreshCw className="h-4 w-4 mr-2" />
            Atualizar
          </Button>
        </div>
      </div>

      {/* Métricas Principais */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Participantes</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{analytics.metricas.totalParticipantes}</div>
            <p className="text-xs text-muted-foreground">
              +12% desde ontem
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Presença Atual</CardTitle>
            <Activity className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{analytics.metricas.presencaAtual}</div>
            <p className="text-xs text-muted-foreground">
              {analytics.metricas.taxaOcupacao}% de ocupação
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Tempo Médio Check-in</CardTitle>
            <Clock className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{analytics.metricas.tempoMedioCheckin}s</div>
            <p className="text-xs text-muted-foreground">
              -3s desde ontem
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Taxa de Sucesso</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {((analytics.seguranca.validacoesValidas / analytics.seguranca.totalValidacoes) * 100).toFixed(1)}%
            </div>
            <p className="text-xs text-muted-foreground">
              {analytics.seguranca.validacoesValidas} de {analytics.seguranca.totalValidacoes} validações
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Tabs com diferentes visualizações */}
      <Tabs defaultValue="fluxo" className="w-full">
        <TabsList>
          <TabsTrigger value="fluxo">Fluxo Horário</TabsTrigger>
          <TabsTrigger value="equipamentos">Equipamentos</TabsTrigger>
          <TabsTrigger value="seguranca">Segurança</TabsTrigger>
        </TabsList>

        <TabsContent value="fluxo" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Fluxo de Participantes por Hora</CardTitle>
              <CardDescription>
                Entradas e saídas do evento nas últimas 24 horas
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {analytics.fluxoHorario.map((item, index) => (
                  <div key={index} className="flex items-center justify-between p-3 border rounded-lg">
                    <div className="flex items-center space-x-3">
                      <Clock className="h-4 w-4 text-muted-foreground" />
                      <span className="font-medium">{item.hora}</span>
                    </div>
                    <div className="flex space-x-6 text-sm">
                      <span className="text-green-600">↗ {item.entradas} entradas</span>
                      <span className="text-red-600">↙ {item.saidas} saídas</span>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="equipamentos" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Status dos Equipamentos</CardTitle>
              <CardDescription>
                Monitoramento em tempo real dos dispositivos MEEP
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {analytics.equipamentos.map((equipamento, index) => (
                  <div key={index} className="flex items-center justify-between p-3 border rounded-lg">
                    <div className="flex items-center space-x-3">
                      {getStatusIcon(equipamento.status)}
                      <div>
                        <p className="font-medium">{equipamento.nome}</p>
                        <p className="text-sm text-muted-foreground">
                          Última atividade: {equipamento.ultimaAtividade}
                        </p>
                      </div>
                    </div>
                    {getStatusBadge(equipamento.status)}
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="seguranca" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Logs de Segurança</CardTitle>
              <CardDescription>
                Alertas e eventos de segurança do sistema MEEP
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="grid grid-cols-3 gap-4 mb-6">
                  <div className="text-center p-3 border rounded-lg">
                    <div className="text-2xl font-bold text-green-600">
                      {analytics.seguranca.validacoesValidas}
                    </div>
                    <div className="text-sm text-muted-foreground">Validações Válidas</div>
                  </div>
                  <div className="text-center p-3 border rounded-lg">
                    <div className="text-2xl font-bold text-red-600">
                      {analytics.seguranca.tentativasInvalidas}
                    </div>
                    <div className="text-sm text-muted-foreground">Tentativas Inválidas</div>
                  </div>
                  <div className="text-center p-3 border rounded-lg">
                    <div className="text-2xl font-bold text-blue-600">
                      {analytics.seguranca.alertas.length}
                    </div>
                    <div className="text-sm text-muted-foreground">Alertas Ativos</div>
                  </div>
                </div>

                {analytics.seguranca.alertas.map((alerta, index) => (
                  <div key={index} className="flex items-center space-x-3 p-3 border rounded-lg">
                    <Shield className={`h-4 w-4 ${
                      alerta.tipo === 'error' ? 'text-red-500' :
                      alerta.tipo === 'warning' ? 'text-yellow-500' : 'text-blue-500'
                    }`} />
                    <div className="flex-1">
                      <p className="font-medium">{alerta.descricao}</p>
                      <p className="text-sm text-muted-foreground">{alerta.timestamp}</p>
                    </div>
                    <Badge variant={
                      alerta.tipo === 'error' ? 'destructive' :
                      alerta.tipo === 'warning' ? 'secondary' : 'default'
                    }>
                      {alerta.tipo}
                    </Badge>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </motion.div>
  );
};

export default MEEPAnalytics;
