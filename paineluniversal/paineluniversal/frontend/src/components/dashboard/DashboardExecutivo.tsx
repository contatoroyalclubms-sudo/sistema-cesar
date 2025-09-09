import React, { useState, useEffect } from 'react';
import { 
  Card, 
  CardContent, 
  CardHeader, 
  CardTitle 
} from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue
} from '@/components/ui/select';
import { Calendar } from '@/components/ui/calendar';
import { Progress } from '@/components/ui/progress';
import {
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger
} from '@/components/ui/tabs';
import {
  LineChart, 
  Line, 
  BarChart, 
  Bar,
  AreaChart,
  Area,
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  PieChart, 
  Pie, 
  Cell,
  ComposedChart,
  Legend,
  ScatterChart,
  Scatter
} from 'recharts';
import {
  TrendingUp,
  TrendingDown,
  DollarSign,
  Users,
  Calendar as CalendarIcon,
  Target,
  Award,
  Activity,
  BarChart3,
  PieChart as PieChartIcon,
  Globe,
  Star,
  AlertTriangle,
  CheckCircle,
  Clock,
  Zap,
  Download,
  RefreshCw,
  Filter,
  ArrowUp,
  ArrowDown,
  Minus
} from 'lucide-react';

interface KPICard {
  title: string;
  value: string | number;
  change: number;
  changeText: string;
  icon: React.ReactNode;
  trend: 'up' | 'down' | 'stable';
  color: string;
}

interface MetricasEvento {
  id: number;
  nome: string;
  data_inicio: string;
  data_fim: string;
  total_vendas: number;
  receita_total: number;
  participantes_checkin: number;
  capacidade: number;
  taxa_ocupacao: number;
  ticket_medio: number;
  margem_lucro: number;
  satisfacao_media: number;
  nps: number;
  status: 'planejamento' | 'andamento' | 'finalizado' | 'cancelado';
}

interface AnalisePeriodo {
  periodo: string;
  receita: number;
  vendas: number;
  participantes: number;
  eventos: number;
  crescimento_receita: number;
  crescimento_vendas: number;
  roi: number;
  margem: number;
}

interface MetricasGerais {
  receita_total_mes: number;
  crescimento_receita: number;
  total_eventos_mes: number;
  crescimento_eventos: number;
  total_participantes_mes: number;
  crescimento_participantes: number;
  ticket_medio_mes: number;
  crescimento_ticket_medio: number;
  margem_lucro_media: number;
  nps_medio: number;
  taxa_retencao: number;
  ltv_medio: number;
}

const DashboardExecutivo: React.FC = () => {
  const [metricas, setMetricas] = useState<MetricasGerais | null>(null);
  const [eventosRecentes, setEventosRecentes] = useState<MetricasEvento[]>([]);
  const [dadosHistoricos, setDadosHistoricos] = useState<AnalisePeriodo[]>([]);
  const [periodoSelecionado, setPeriodoSelecionado] = useState('mes');
  const [loading, setLoading] = useState(false);

  // Mock data - Em produção, viria da API
  useEffect(() => {
    const mockMetricas: MetricasGerais = {
      receita_total_mes: 2847650.00,
      crescimento_receita: 23.5,
      total_eventos_mes: 47,
      crescimento_eventos: 12.3,
      total_participantes_mes: 18542,
      crescimento_participantes: 18.7,
      ticket_medio_mes: 153.67,
      crescimento_ticket_medio: 8.2,
      margem_lucro_media: 34.2,
      nps_medio: 72.8,
      taxa_retencao: 68.4,
      ltv_medio: 2847.30
    };

    const mockEventos: MetricasEvento[] = [
      {
        id: 1,
        nome: "Festival de Tecnologia 2024",
        data_inicio: "2024-01-15",
        data_fim: "2024-01-17",
        total_vendas: 2450,
        receita_total: 367500.00,
        participantes_checkin: 2380,
        capacidade: 2500,
        taxa_ocupacao: 95.2,
        ticket_medio: 150.00,
        margem_lucro: 38.5,
        satisfacao_media: 4.6,
        nps: 78,
        status: 'finalizado'
      },
      {
        id: 2,
        nome: "Conferência Empresarial Q1",
        data_inicio: "2024-01-20",
        data_fim: "2024-01-22",
        total_vendas: 1847,
        receita_total: 553000.00,
        participantes_checkin: 1820,
        capacidade: 2000,
        taxa_ocupacao: 91.0,
        ticket_medio: 299.46,
        margem_lucro: 42.1,
        satisfacao_media: 4.8,
        nps: 84,
        status: 'finalizado'
      },
      {
        id: 3,
        nome: "Workshop Inovação Digital",
        data_inicio: "2024-02-05",
        data_fim: "2024-02-05",
        total_vendas: 890,
        receita_total: 89000.00,
        participantes_checkin: 876,
        capacidade: 1000,
        taxa_ocupacao: 87.6,
        ticket_medio: 100.00,
        margem_lucro: 28.7,
        satisfacao_media: 4.4,
        nps: 65,
        status: 'finalizado'
      }
    ];

    const mockHistorico: AnalisePeriodo[] = [
      { periodo: 'Jan 2024', receita: 2847650, vendas: 5187, participantes: 18542, eventos: 47, crescimento_receita: 23.5, crescimento_vendas: 18.2, roi: 3.4, margem: 34.2 },
      { periodo: 'Dez 2023', receita: 2310400, vendas: 4392, participantes: 15650, eventos: 42, crescimento_receita: 15.8, crescimento_vendas: 12.1, roi: 2.9, margem: 32.1 },
      { periodo: 'Nov 2023', receita: 1995800, vendas: 3921, participantes: 14230, eventos: 38, crescimento_receita: 8.7, crescimento_vendas: 6.4, roi: 2.7, margem: 31.8 },
      { periodo: 'Out 2023', receita: 1836200, vendas: 3684, participantes: 13180, eventos: 35, crescimento_receita: 12.3, crescimento_vendas: 9.8, roi: 2.8, margem: 30.9 },
      { periodo: 'Set 2023', receita: 1635400, vendas: 3356, participantes: 12010, eventos: 32, crescimento_receita: 5.4, crescimento_vendas: 4.2, roi: 2.5, margem: 29.8 },
      { periodo: 'Ago 2023', receita: 1551200, vendas: 3221, participantes: 11540, eventos: 31, crescimento_receita: 18.9, crescimento_vendas: 15.7, roi: 3.1, margem: 33.2 }
    ];

    setMetricas(mockMetricas);
    setEventosRecentes(mockEventos);
    setDadosHistoricos(mockHistorico);
  }, []);

  const kpiCards: KPICard[] = metricas ? [
    {
      title: 'Receita Total',
      value: `R$ ${(metricas.receita_total_mes / 1000000).toFixed(2)}M`,
      change: metricas.crescimento_receita,
      changeText: 'vs mês anterior',
      icon: <DollarSign className="h-4 w-4" />,
      trend: metricas.crescimento_receita > 0 ? 'up' : metricas.crescimento_receita < 0 ? 'down' : 'stable',
      color: 'text-green-600'
    },
    {
      title: 'Eventos Realizados',
      value: metricas.total_eventos_mes,
      change: metricas.crescimento_eventos,
      changeText: 'vs mês anterior',
      icon: <CalendarIcon className="h-4 w-4" />,
      trend: metricas.crescimento_eventos > 0 ? 'up' : metricas.crescimento_eventos < 0 ? 'down' : 'stable',
      color: 'text-blue-600'
    },
    {
      title: 'Participantes',
      value: metricas.total_participantes_mes.toLocaleString(),
      change: metricas.crescimento_participantes,
      changeText: 'vs mês anterior',
      icon: <Users className="h-4 w-4" />,
      trend: metricas.crescimento_participantes > 0 ? 'up' : metricas.crescimento_participantes < 0 ? 'down' : 'stable',
      color: 'text-purple-600'
    },
    {
      title: 'Ticket Médio',
      value: `R$ ${metricas.ticket_medio_mes.toFixed(2)}`,
      change: metricas.crescimento_ticket_medio,
      changeText: 'vs mês anterior',
      icon: <Target className="h-4 w-4" />,
      trend: metricas.crescimento_ticket_medio > 0 ? 'up' : metricas.crescimento_ticket_medio < 0 ? 'down' : 'stable',
      color: 'text-orange-600'
    },
    {
      title: 'Margem de Lucro',
      value: `${metricas.margem_lucro_media.toFixed(1)}%`,
      change: 0, // Mockado como estável
      changeText: 'média do período',
      icon: <TrendingUp className="h-4 w-4" />,
      trend: 'stable',
      color: 'text-emerald-600'
    },
    {
      title: 'NPS Médio',
      value: metricas.nps_medio.toFixed(1),
      change: 0, // Mockado como estável
      changeText: 'satisfação geral',
      icon: <Star className="h-4 w-4" />,
      trend: 'stable',
      color: 'text-yellow-600'
    }
  ] : [];

  const getTrendIcon = (trend: 'up' | 'down' | 'stable') => {
    switch (trend) {
      case 'up': return <ArrowUp className="h-3 w-3 text-green-600" />;
      case 'down': return <ArrowDown className="h-3 w-3 text-red-600" />;
      case 'stable': return <Minus className="h-3 w-3 text-gray-600" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'finalizado': return 'bg-green-100 text-green-800';
      case 'andamento': return 'bg-blue-100 text-blue-800';
      case 'planejamento': return 'bg-yellow-100 text-yellow-800';
      case 'cancelado': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(value);
  };

  // Dados para gráficos
  const receitaPorMes = dadosHistoricos.map(item => ({
    mes: item.periodo,
    receita: item.receita / 1000000, // Em milhões
    vendas: item.vendas,
    crescimento: item.crescimento_receita
  }));

  const performanceEventos = eventosRecentes.map(evento => ({
    nome: evento.nome.substring(0, 20) + '...',
    ocupacao: evento.taxa_ocupacao,
    satisfacao: evento.satisfacao_media * 20, // Converter para escala 0-100
    receita: evento.receita_total / 1000, // Em milhares
    nps: evento.nps
  }));

  const margemRoi = dadosHistoricos.map(item => ({
    periodo: item.periodo,
    margem: item.margem,
    roi: item.roi * 10 // Ajustar escala para visualização
  }));

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Dashboard Executivo</h1>
          <p className="text-muted-foreground">
            Visão estratégica e insights de performance
          </p>
        </div>
        <div className="flex gap-2">
          <Select value={periodoSelecionado} onValueChange={setPeriodoSelecionado}>
            <SelectTrigger className="w-[150px]">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="semana">Esta Semana</SelectItem>
              <SelectItem value="mes">Este Mês</SelectItem>
              <SelectItem value="trimestre">Este Trimestre</SelectItem>
              <SelectItem value="ano">Este Ano</SelectItem>
            </SelectContent>
          </Select>
          <Button variant="outline" disabled={loading}>
            <RefreshCw className="h-4 w-4 mr-2" />
            Atualizar
          </Button>
          <Button variant="outline">
            <Download className="h-4 w-4 mr-2" />
            Exportar
          </Button>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid gap-4 md:grid-cols-3 lg:grid-cols-6">
        {kpiCards.map((kpi, index) => (
          <Card key={index}>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">
                {kpi.title}
              </CardTitle>
              <div className={kpi.color}>
                {kpi.icon}
              </div>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{kpi.value}</div>
              <div className="flex items-center text-xs text-muted-foreground">
                {getTrendIcon(kpi.trend)}
                <span className={`ml-1 ${
                  kpi.trend === 'up' ? 'text-green-600' : 
                  kpi.trend === 'down' ? 'text-red-600' : 'text-gray-600'
                }`}>
                  {kpi.change !== 0 && `${kpi.change > 0 ? '+' : ''}${kpi.change.toFixed(1)}%`}
                </span>
                <span className="ml-1">{kpi.changeText}</span>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      <Tabs defaultValue="visao-geral" className="space-y-4">
        <TabsList>
          <TabsTrigger value="visao-geral">Visão Geral</TabsTrigger>
          <TabsTrigger value="receita">Receita & Performance</TabsTrigger>
          <TabsTrigger value="eventos">Análise de Eventos</TabsTrigger>
          <TabsTrigger value="participantes">Participantes & Satisfação</TabsTrigger>
        </TabsList>

        {/* Visão Geral Tab */}
        <TabsContent value="visao-geral" className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2">
            {/* Receita por Período */}
            <Card>
              <CardHeader>
                <CardTitle>Evolução da Receita</CardTitle>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <AreaChart data={receitaPorMes}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="mes" />
                    <YAxis />
                    <Tooltip 
                      formatter={(value: any, name: string) => [
                        name === 'receita' ? `R$ ${value.toFixed(2)}M` : value,
                        name === 'receita' ? 'Receita' : 'Vendas'
                      ]}
                    />
                    <Area 
                      type="monotone" 
                      dataKey="receita" 
                      stroke="#3b82f6" 
                      fill="#3b82f6" 
                      fillOpacity={0.2}
                    />
                  </AreaChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            {/* Performance dos Eventos */}
            <Card>
              <CardHeader>
                <CardTitle>Performance de Eventos Recentes</CardTitle>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={performanceEventos}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="nome" />
                    <YAxis />
                    <Tooltip />
                    <Bar dataKey="ocupacao" fill="#10b981" />
                  </BarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </div>

          {/* Métricas Chave */}
          <div className="grid gap-4 md:grid-cols-4">
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-base">Taxa de Retenção</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{metricas?.taxa_retencao.toFixed(1)}%</div>
                <Progress value={metricas?.taxa_retencao} className="mt-2" />
                <p className="text-xs text-muted-foreground mt-1">
                  Meta: 70%
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-base">LTV Médio</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {formatCurrency(metricas?.ltv_medio || 0)}
                </div>
                <p className="text-xs text-muted-foreground mt-1">
                  Valor por cliente
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-base">ROI Médio</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">3.2x</div>
                <p className="text-xs text-muted-foreground mt-1">
                  Retorno sobre investimento
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-base">Crescimento</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-green-600">
                  +{metricas?.crescimento_receita.toFixed(1)}%
                </div>
                <p className="text-xs text-muted-foreground mt-1">
                  Receita vs período anterior
                </p>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Receita & Performance Tab */}
        <TabsContent value="receita" className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2">
            {/* Receita vs Vendas */}
            <Card>
              <CardHeader>
                <CardTitle>Receita vs Volume de Vendas</CardTitle>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={350}>
                  <ComposedChart data={receitaPorMes}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="mes" />
                    <YAxis yAxisId="left" />
                    <YAxis yAxisId="right" orientation="right" />
                    <Tooltip />
                    <Legend />
                    <Bar yAxisId="left" dataKey="receita" fill="#3b82f6" name="Receita (M)" />
                    <Line yAxisId="right" type="monotone" dataKey="vendas" stroke="#ef4444" name="Vendas" />
                  </ComposedChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            {/* Margem vs ROI */}
            <Card>
              <CardHeader>
                <CardTitle>Margem de Lucro vs ROI</CardTitle>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={350}>
                  <LineChart data={margemRoi}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="periodo" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Line type="monotone" dataKey="margem" stroke="#10b981" name="Margem %" strokeWidth={2} />
                    <Line type="monotone" dataKey="roi" stroke="#f59e0b" name="ROI x10" strokeWidth={2} />
                  </LineChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </div>

          {/* Análise Financeira Detalhada */}
          <Card>
            <CardHeader>
              <CardTitle>Análise Financeira por Período</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b">
                      <th className="text-left p-2">Período</th>
                      <th className="text-right p-2">Receita</th>
                      <th className="text-right p-2">Vendas</th>
                      <th className="text-right p-2">Ticket Médio</th>
                      <th className="text-right p-2">Margem</th>
                      <th className="text-right p-2">ROI</th>
                      <th className="text-right p-2">Crescimento</th>
                    </tr>
                  </thead>
                  <tbody>
                    {dadosHistoricos.map((periodo, index) => (
                      <tr key={index} className="border-b">
                        <td className="p-2 font-medium">{periodo.periodo}</td>
                        <td className="text-right p-2">{formatCurrency(periodo.receita)}</td>
                        <td className="text-right p-2">{periodo.vendas.toLocaleString()}</td>
                        <td className="text-right p-2">
                          {formatCurrency(periodo.receita / periodo.vendas)}
                        </td>
                        <td className="text-right p-2">{periodo.margem.toFixed(1)}%</td>
                        <td className="text-right p-2">{periodo.roi.toFixed(1)}x</td>
                        <td className={`text-right p-2 ${
                          periodo.crescimento_receita > 0 ? 'text-green-600' : 
                          periodo.crescimento_receita < 0 ? 'text-red-600' : 'text-gray-600'
                        }`}>
                          {periodo.crescimento_receita > 0 ? '+' : ''}{periodo.crescimento_receita.toFixed(1)}%
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Análise de Eventos Tab */}
        <TabsContent value="eventos" className="space-y-4">
          {/* Top Eventos */}
          <Card>
            <CardHeader>
              <CardTitle>Eventos com Melhor Performance</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {eventosRecentes
                  .sort((a, b) => b.receita_total - a.receita_total)
                  .slice(0, 5)
                  .map((evento, index) => (
                    <div key={evento.id} className="flex items-center justify-between p-3 border rounded-lg">
                      <div className="flex-1">
                        <div className="flex items-center gap-3">
                          <Badge className="bg-blue-100 text-blue-800">#{index + 1}</Badge>
                          <div>
                            <h4 className="font-medium">{evento.nome}</h4>
                            <p className="text-sm text-muted-foreground">
                              {new Date(evento.data_inicio).toLocaleDateString()} - 
                              {new Date(evento.data_fim).toLocaleDateString()}
                            </p>
                          </div>
                        </div>
                      </div>
                      <div className="text-right">
                        <div className="font-semibold text-lg">
                          {formatCurrency(evento.receita_total)}
                        </div>
                        <div className="text-sm text-muted-foreground">
                          {evento.total_vendas} vendas
                        </div>
                      </div>
                      <div className="text-right ml-6">
                        <Badge className={getStatusColor(evento.status)}>
                          {evento.status}
                        </Badge>
                        <div className="text-sm text-muted-foreground mt-1">
                          {evento.taxa_ocupacao.toFixed(1)}% ocupação
                        </div>
                      </div>
                    </div>
                  ))
                }
              </div>
            </CardContent>
          </Card>

          {/* Distribuição por Categoria */}
          <div className="grid gap-4 md:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle>Satisfação vs Taxa de Ocupação</CardTitle>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <ScatterChart data={performanceEventos}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="ocupacao" name="Ocupação %" />
                    <YAxis dataKey="satisfacao" name="Satisfação" />
                    <Tooltip 
                      formatter={(value: any, name: string) => [
                        name === 'ocupacao' ? `${value}%` : value.toFixed(1),
                        name === 'ocupacao' ? 'Taxa de Ocupação' : 'Satisfação'
                      ]}
                    />
                    <Scatter dataKey="satisfacao" fill="#8884d8" />
                  </ScatterChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Métricas de Eventos</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex justify-between items-center">
                    <span className="text-sm font-medium">Taxa média de ocupação</span>
                    <span className="text-2xl font-bold">91.3%</span>
                  </div>
                  <Progress value={91.3} />
                  
                  <div className="flex justify-between items-center">
                    <span className="text-sm font-medium">Satisfação média</span>
                    <span className="text-2xl font-bold">4.6/5.0</span>
                  </div>
                  <Progress value={92} />
                  
                  <div className="flex justify-between items-center">
                    <span className="text-sm font-medium">NPS médio</span>
                    <span className="text-2xl font-bold">75.7</span>
                  </div>
                  <Progress value={75.7} />
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Participantes & Satisfação Tab */}
        <TabsContent value="participantes" className="space-y-4">
          <div className="grid gap-4 md:grid-cols-3">
            {/* Participantes por Evento */}
            <Card>
              <CardHeader>
                <CardTitle>Participantes por Evento</CardTitle>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={250}>
                  <BarChart data={eventosRecentes}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="nome" hide />
                    <YAxis />
                    <Tooltip />
                    <Bar dataKey="participantes_checkin" fill="#6366f1" />
                  </BarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            {/* NPS Score */}
            <Card>
              <CardHeader>
                <CardTitle>Distribuição NPS</CardTitle>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={250}>
                  <PieChart>
                    <Pie
                      data={[
                        { name: 'Promotores', value: 65, fill: '#10b981' },
                        { name: 'Neutros', value: 23, fill: '#f59e0b' },
                        { name: 'Detratores', value: 12, fill: '#ef4444' }
                      ]}
                      cx="50%"
                      cy="50%"
                      innerRadius={60}
                      outerRadius={100}
                      dataKey="value"
                      label={({ name, value }) => `${name}: ${value}%`}
                    />
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            {/* Estatísticas Gerais */}
            <Card>
              <CardHeader>
                <CardTitle>Estatísticas de Satisfação</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="text-center">
                    <div className="text-3xl font-bold text-green-600">72.8</div>
                    <div className="text-sm text-muted-foreground">NPS Médio</div>
                  </div>
                  
                  <div className="text-center">
                    <div className="text-3xl font-bold text-blue-600">4.6/5.0</div>
                    <div className="text-sm text-muted-foreground">Avaliação Média</div>
                  </div>
                  
                  <div className="text-center">
                    <div className="text-3xl font-bold text-purple-600">68.4%</div>
                    <div className="text-sm text-muted-foreground">Taxa de Retorno</div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Feedback e Melhorias */}
          <Card>
            <CardHeader>
              <CardTitle>Insights e Recomendações</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid gap-4 md:grid-cols-2">
                <div className="space-y-3">
                  <h4 className="font-semibold text-green-600">✅ Pontos Fortes</h4>
                  <ul className="space-y-2 text-sm">
                    <li>• Taxa de ocupação média de 91.3% (acima da meta)</li>
                    <li>• NPS médio de 72.8 (considerado excelente)</li>
                    <li>• Crescimento de receita de 23.5% no período</li>
                    <li>• Ticket médio em crescimento constante</li>
                  </ul>
                </div>
                
                <div className="space-y-3">
                  <h4 className="font-semibold text-orange-600">🔄 Oportunidades</h4>
                  <ul className="space-y-2 text-sm">
                    <li>• Aumentar taxa de retenção para 75%</li>
                    <li>• Melhorar performance em eventos menores</li>
                    <li>• Diversificar portfolio de eventos</li>
                    <li>• Implementar programa de fidelidade</li>
                  </ul>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default DashboardExecutivo;