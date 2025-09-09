import React, { useState, useEffect, useMemo } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { DatePickerWithRange } from '@/components/ui/date-range-picker';
import { Progress } from '@/components/ui/progress';
import { Separator } from '@/components/ui/separator';
import {
  LineChart, Line, AreaChart, Area, BarChart, Bar, PieChart, Pie,
  RadarChart, Radar, PolarGrid, PolarAngleAxis, PolarRadiusAxis,
  ComposedChart, Scatter, Cell, XAxis, YAxis, CartesianGrid,
  Tooltip, Legend, ResponsiveContainer, ReferenceLine, Brush
} from 'recharts';
import {
  TrendingUp, TrendingDown, Users, ShoppingCart, DollarSign,
  Calendar, Clock, Target, Award, AlertTriangle, Activity,
  Download, Filter, RefreshCw, Settings, BarChart3, PieChartIcon,
  LineChartIcon, Map, Zap, Brain, Eye, Package, CreditCard,
  UserCheck, UserX, Star, ThumbsUp, MessageSquare, Percent
} from 'lucide-react';
import { format, subDays, startOfMonth, endOfMonth, eachDayOfInterval } from 'date-fns';
import { ptBR } from 'date-fns/locale';
import { cn } from '@/lib/utils';
import api from '@/lib/api';

interface MetricCard {
  title: string;
  value: string | number;
  change: number;
  icon: React.ReactNode;
  trend: 'up' | 'down' | 'neutral';
  subtitle?: string;
}

interface ChartData {
  name: string;
  value: number;
  [key: string]: any;
}

export default function DashboardBI() {
  const [loading, setLoading] = useState(true);
  const [dateRange, setDateRange] = useState({
    from: startOfMonth(new Date()),
    to: endOfMonth(new Date())
  });
  const [selectedPeriod, setSelectedPeriod] = useState('month');
  const [selectedMetric, setSelectedMetric] = useState('revenue');
  const [refreshing, setRefreshing] = useState(false);

  // Estados para dados
  const [metricsData, setMetricsData] = useState<MetricCard[]>([]);
  const [revenueData, setRevenueData] = useState<ChartData[]>([]);
  const [salesData, setSalesData] = useState<ChartData[]>([]);
  const [customerData, setCustomerData] = useState<ChartData[]>([]);
  const [productData, setProductData] = useState<ChartData[]>([]);
  const [behaviorData, setBehaviorData] = useState<ChartData[]>([]);
  const [predictiveData, setPredictiveData] = useState<any>({});
  const [heatmapData, setHeatmapData] = useState<any[]>([]);

  // Cores personalizadas
  const COLORS = ['#8b5cf6', '#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#06b6d4', '#ec4899', '#84cc16'];

  useEffect(() => {
    loadDashboardData();
  }, [dateRange, selectedPeriod]);

  const loadDashboardData = async () => {
    setLoading(true);
    try {
      // Simular carregamento de dados
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Gerar dados mockados
      generateMockData();
    } catch (error) {
      console.error('Erro ao carregar dados:', error);
    } finally {
      setLoading(false);
    }
  };

  const generateMockData = () => {
    // Métricas principais
    setMetricsData([
      {
        title: 'Receita Total',
        value: 'R$ 125.750',
        change: 12.5,
        icon: <DollarSign className="h-4 w-4" />,
        trend: 'up',
        subtitle: 'vs mês anterior'
      },
      {
        title: 'Vendas',
        value: '1,234',
        change: 8.2,
        icon: <ShoppingCart className="h-4 w-4" />,
        trend: 'up',
        subtitle: '+98 hoje'
      },
      {
        title: 'Clientes Ativos',
        value: '3,456',
        change: -2.4,
        icon: <Users className="h-4 w-4" />,
        trend: 'down',
        subtitle: '89% de retenção'
      },
      {
        title: 'Ticket Médio',
        value: 'R$ 102',
        change: 5.7,
        icon: <CreditCard className="h-4 w-4" />,
        trend: 'up',
        subtitle: 'Melhor que a meta'
      },
      {
        title: 'Taxa de Conversão',
        value: '3.2%',
        change: 0.5,
        icon: <Percent className="h-4 w-4" />,
        trend: 'up',
        subtitle: 'De 15.6k visitas'
      },
      {
        title: 'NPS Score',
        value: 72,
        change: 3,
        icon: <Star className="h-4 w-4" />,
        trend: 'up',
        subtitle: 'Excelente'
      }
    ]);

    // Dados de receita
    const days = eachDayOfInterval({ start: dateRange.from, end: dateRange.to });
    setRevenueData(days.map(day => ({
      name: format(day, 'dd/MM'),
      receita: Math.floor(Math.random() * 5000) + 3000,
      vendas: Math.floor(Math.random() * 50) + 30,
      ticket: Math.floor(Math.random() * 50) + 80
    })));

    // Dados de vendas por categoria
    setSalesData([
      { name: 'Eletrônicos', value: 35, vendas: 420 },
      { name: 'Moda', value: 28, vendas: 336 },
      { name: 'Casa', value: 18, vendas: 216 },
      { name: 'Alimentos', value: 12, vendas: 144 },
      { name: 'Outros', value: 7, vendas: 84 }
    ]);

    // Dados de clientes
    setCustomerData([
      { name: 'Novos', value: 35, total: 1210 },
      { name: 'Recorrentes', value: 45, total: 1555 },
      { name: 'VIP', value: 15, total: 518 },
      { name: 'Inativos', value: 5, total: 173 }
    ]);

    // Top produtos
    setProductData([
      { name: 'iPhone 14', vendas: 89, receita: 89000, margem: 15 },
      { name: 'Samsung TV', vendas: 67, receita: 45000, margem: 18 },
      { name: 'Notebook Dell', vendas: 54, receita: 38000, margem: 12 },
      { name: 'AirPods', vendas: 123, receita: 25000, margem: 25 },
      { name: 'PlayStation 5', vendas: 34, receita: 20000, margem: 8 }
    ]);

    // Comportamento do usuário
    setBehaviorData([
      { hora: '00h', desktop: 20, mobile: 45, tablet: 10 },
      { hora: '06h', desktop: 35, mobile: 78, tablet: 15 },
      { hora: '12h', desktop: 89, mobile: 156, tablet: 34 },
      { hora: '18h', desktop: 120, mobile: 234, tablet: 45 },
      { hora: '21h', desktop: 78, mobile: 189, tablet: 28 }
    ]);

    // Dados preditivos
    setPredictiveData({
      proxima_semana: {
        receita_prevista: 142500,
        confianca: 85,
        vendas_previstas: 1456,
        produtos_em_alta: ['iPhone 14', 'Samsung TV', 'AirPods']
      },
      insights: [
        { tipo: 'oportunidade', mensagem: 'Aumento de 23% nas buscas por eletrônicos' },
        { tipo: 'alerta', mensagem: 'Estoque baixo em 3 produtos populares' },
        { tipo: 'tendencia', mensagem: 'Crescimento de 15% em vendas mobile' }
      ],
      segmentos_promissores: [
        { nome: 'Millennials Tech', potencial: 89 },
        { nome: 'Família Premium', potencial: 76 },
        { nome: 'Early Adopters', potencial: 82 }
      ]
    });

    // Heatmap de vendas por hora/dia
    const heatmap = [];
    const dias = ['Dom', 'Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb'];
    for (let d = 0; d < 7; d++) {
      for (let h = 0; h < 24; h++) {
        heatmap.push({
          dia: dias[d],
          hora: h,
          vendas: Math.floor(Math.random() * 100)
        });
      }
    }
    setHeatmapData(heatmap);
  };

  const handleRefresh = async () => {
    setRefreshing(true);
    await loadDashboardData();
    setRefreshing(false);
  };

  const handleExportData = () => {
    // Implementar exportação de dados
    console.log('Exportando dados...');
  };

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL'
    }).format(value);
  };

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white p-3 rounded-lg shadow-lg border">
          <p className="font-semibold">{label}</p>
          {payload.map((entry: any, index: number) => (
            <p key={index} style={{ color: entry.color }}>
              {entry.name}: {entry.name.includes('R$') ? formatCurrency(entry.value) : entry.value}
            </p>
          ))}
        </div>
      );
    }
    return null;
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800 p-6">
      {/* Header */}
      <div className="mb-6">
        <div className="flex justify-between items-start">
          <div>
            <h1 className="text-3xl font-bold bg-gradient-to-r from-violet-600 to-blue-600 bg-clip-text text-transparent">
              Dashboard Business Intelligence
            </h1>
            <p className="text-muted-foreground mt-1">
              Análises avançadas e insights em tempo real
            </p>
          </div>
          <div className="flex gap-2">
            <Button variant="outline" size="sm" onClick={handleRefresh} disabled={refreshing}>
              <RefreshCw className={cn("h-4 w-4 mr-1", refreshing && "animate-spin")} />
              Atualizar
            </Button>
            <Button variant="outline" size="sm" onClick={handleExportData}>
              <Download className="h-4 w-4 mr-1" />
              Exportar
            </Button>
            <Button variant="outline" size="sm">
              <Settings className="h-4 w-4 mr-1" />
              Configurar
            </Button>
          </div>
        </div>

        {/* Filtros */}
        <div className="mt-4 flex gap-4 flex-wrap">
          <DatePickerWithRange date={dateRange} setDate={setDateRange} />
          <Select value={selectedPeriod} onValueChange={setSelectedPeriod}>
            <SelectTrigger className="w-[150px]">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="day">Diário</SelectItem>
              <SelectItem value="week">Semanal</SelectItem>
              <SelectItem value="month">Mensal</SelectItem>
              <SelectItem value="quarter">Trimestral</SelectItem>
              <SelectItem value="year">Anual</SelectItem>
            </SelectContent>
          </Select>
          <Select value={selectedMetric} onValueChange={setSelectedMetric}>
            <SelectTrigger className="w-[150px]">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="revenue">Receita</SelectItem>
              <SelectItem value="sales">Vendas</SelectItem>
              <SelectItem value="customers">Clientes</SelectItem>
              <SelectItem value="products">Produtos</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>

      {/* KPIs Principais */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4 mb-6">
        {metricsData.map((metric, index) => (
          <Card key={index} className="hover:shadow-lg transition-shadow">
            <CardHeader className="pb-2">
              <div className="flex justify-between items-start">
                <div className="p-2 bg-violet-100 dark:bg-violet-900/20 rounded-lg">
                  {metric.icon}
                </div>
                <Badge
                  variant={metric.trend === 'up' ? 'success' : metric.trend === 'down' ? 'destructive' : 'secondary'}
                  className="text-xs"
                >
                  {metric.trend === 'up' ? <TrendingUp className="h-3 w-3 mr-1" /> : <TrendingDown className="h-3 w-3 mr-1" />}
                  {Math.abs(metric.change)}%
                </Badge>
              </div>
            </CardHeader>
            <CardContent>
              <p className="text-2xl font-bold">{metric.value}</p>
              <p className="text-xs text-muted-foreground mt-1">{metric.title}</p>
              {metric.subtitle && (
                <p className="text-xs text-muted-foreground mt-1">{metric.subtitle}</p>
              )}
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Tabs de Análises */}
      <Tabs defaultValue="overview" className="space-y-4">
        <TabsList className="grid w-full grid-cols-6">
          <TabsTrigger value="overview">Visão Geral</TabsTrigger>
          <TabsTrigger value="sales">Vendas</TabsTrigger>
          <TabsTrigger value="customers">Clientes</TabsTrigger>
          <TabsTrigger value="products">Produtos</TabsTrigger>
          <TabsTrigger value="behavior">Comportamento</TabsTrigger>
          <TabsTrigger value="predictive">Preditivo</TabsTrigger>
        </TabsList>

        {/* Tab Visão Geral */}
        <TabsContent value="overview" className="space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            {/* Gráfico de Receita */}
            <Card>
              <CardHeader>
                <CardTitle>Evolução da Receita</CardTitle>
                <CardDescription>Receita, vendas e ticket médio ao longo do tempo</CardDescription>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <ComposedChart data={revenueData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" />
                    <YAxis yAxisId="left" />
                    <YAxis yAxisId="right" orientation="right" />
                    <Tooltip content={<CustomTooltip />} />
                    <Legend />
                    <Area
                      yAxisId="left"
                      type="monotone"
                      dataKey="receita"
                      fill="#8b5cf6"
                      stroke="#8b5cf6"
                      fillOpacity={0.3}
                      name="Receita"
                    />
                    <Bar yAxisId="left" dataKey="vendas" fill="#3b82f6" name="Vendas" />
                    <Line
                      yAxisId="right"
                      type="monotone"
                      dataKey="ticket"
                      stroke="#10b981"
                      name="Ticket Médio"
                      strokeWidth={2}
                    />
                  </ComposedChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            {/* Distribuição de Vendas */}
            <Card>
              <CardHeader>
                <CardTitle>Distribuição por Categoria</CardTitle>
                <CardDescription>Percentual de vendas por categoria de produto</CardDescription>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={salesData}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="value"
                    >
                      {salesData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </div>

          {/* Insights e Alertas */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Brain className="h-5 w-5" />
                Insights Inteligentes
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {predictiveData.insights?.map((insight: any, index: number) => (
                  <div
                    key={index}
                    className={cn(
                      "p-4 rounded-lg border",
                      insight.tipo === 'oportunidade' && "bg-green-50 border-green-200 dark:bg-green-900/20",
                      insight.tipo === 'alerta' && "bg-yellow-50 border-yellow-200 dark:bg-yellow-900/20",
                      insight.tipo === 'tendencia' && "bg-blue-50 border-blue-200 dark:bg-blue-900/20"
                    )}
                  >
                    <div className="flex items-start gap-2">
                      {insight.tipo === 'oportunidade' && <Zap className="h-4 w-4 text-green-600 mt-0.5" />}
                      {insight.tipo === 'alerta' && <AlertTriangle className="h-4 w-4 text-yellow-600 mt-0.5" />}
                      {insight.tipo === 'tendencia' && <TrendingUp className="h-4 w-4 text-blue-600 mt-0.5" />}
                      <p className="text-sm">{insight.mensagem}</p>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Tab Vendas */}
        <TabsContent value="sales" className="space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            {/* Top Produtos */}
            <Card>
              <CardHeader>
                <CardTitle>Top 5 Produtos</CardTitle>
                <CardDescription>Produtos com maior volume de vendas</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {productData.map((product, index) => (
                    <div key={index}>
                      <div className="flex justify-between items-center mb-2">
                        <div className="flex items-center gap-2">
                          <Badge variant="outline">{index + 1}º</Badge>
                          <span className="font-medium">{product.name}</span>
                        </div>
                        <div className="text-right">
                          <p className="font-semibold">{formatCurrency(product.receita)}</p>
                          <p className="text-xs text-muted-foreground">{product.vendas} vendas</p>
                        </div>
                      </div>
                      <Progress value={(product.vendas / 150) * 100} className="h-2" />
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Margem de Lucro */}
            <Card>
              <CardHeader>
                <CardTitle>Análise de Margem</CardTitle>
                <CardDescription>Margem de lucro por produto</CardDescription>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <RadarChart data={productData}>
                    <PolarGrid />
                    <PolarAngleAxis dataKey="name" />
                    <PolarRadiusAxis angle={90} domain={[0, 30]} />
                    <Radar name="Margem %" dataKey="margem" stroke="#8b5cf6" fill="#8b5cf6" fillOpacity={0.6} />
                    <Tooltip />
                  </RadarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </div>

          {/* Heatmap de Vendas */}
          <Card>
            <CardHeader>
              <CardTitle>Mapa de Calor - Vendas por Hora</CardTitle>
              <CardDescription>Identifique os horários de pico de vendas durante a semana</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-25 gap-1">
                <div></div>
                {Array.from({ length: 24 }, (_, i) => (
                  <div key={i} className="text-xs text-center">{i}h</div>
                ))}
                {['Dom', 'Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb'].map(dia => (
                  <React.Fragment key={dia}>
                    <div className="text-xs text-right pr-2">{dia}</div>
                    {Array.from({ length: 24 }, (_, hora) => {
                      const vendas = heatmapData.find(h => h.dia === dia && h.hora === hora)?.vendas || 0;
                      const intensity = vendas / 100;
                      return (
                        <div
                          key={`${dia}-${hora}`}
                          className="w-full h-6 rounded"
                          style={{
                            backgroundColor: `rgba(139, 92, 246, ${intensity})`,
                          }}
                          title={`${dia} ${hora}h: ${vendas} vendas`}
                        />
                      );
                    })}
                  </React.Fragment>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Tab Clientes */}
        <TabsContent value="customers" className="space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
            {/* Segmentação de Clientes */}
            <Card>
              <CardHeader>
                <CardTitle>Segmentação</CardTitle>
                <CardDescription>Distribuição por tipo de cliente</CardDescription>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={250}>
                  <BarChart data={customerData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" />
                    <YAxis />
                    <Tooltip />
                    <Bar dataKey="total" fill="#8b5cf6">
                      {customerData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            {/* Taxa de Retenção */}
            <Card>
              <CardHeader>
                <CardTitle>Retenção de Clientes</CardTitle>
                <CardDescription>Taxa de retenção mensal</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex justify-between items-center">
                    <span>Taxa Atual</span>
                    <span className="text-2xl font-bold text-green-600">89%</span>
                  </div>
                  <Progress value={89} className="h-3" />
                  <div className="grid grid-cols-2 gap-4 pt-4">
                    <div className="text-center">
                      <UserCheck className="h-8 w-8 mx-auto text-green-600 mb-2" />
                      <p className="text-sm text-muted-foreground">Retornaram</p>
                      <p className="text-xl font-bold">3,078</p>
                    </div>
                    <div className="text-center">
                      <UserX className="h-8 w-8 mx-auto text-red-600 mb-2" />
                      <p className="text-sm text-muted-foreground">Churn</p>
                      <p className="text-xl font-bold">378</p>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Lifetime Value */}
            <Card>
              <CardHeader>
                <CardTitle>Customer Lifetime Value</CardTitle>
                <CardDescription>Valor médio por segmento</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex justify-between items-center p-3 bg-violet-50 dark:bg-violet-900/20 rounded-lg">
                    <span className="font-medium">VIP</span>
                    <span className="font-bold">{formatCurrency(8500)}</span>
                  </div>
                  <div className="flex justify-between items-center p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                    <span className="font-medium">Recorrentes</span>
                    <span className="font-bold">{formatCurrency(3200)}</span>
                  </div>
                  <div className="flex justify-between items-center p-3 bg-green-50 dark:bg-green-900/20 rounded-lg">
                    <span className="font-medium">Novos</span>
                    <span className="font-bold">{formatCurrency(850)}</span>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Análise de Comportamento */}
          <Card>
            <CardHeader>
              <CardTitle>Jornada do Cliente</CardTitle>
              <CardDescription>Taxa de conversão em cada etapa do funil</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {[
                  { etapa: 'Visitantes', total: 15600, percentual: 100 },
                  { etapa: 'Cadastrados', total: 4680, percentual: 30 },
                  { etapa: 'Primeira Compra', total: 1404, percentual: 9 },
                  { etapa: 'Cliente Recorrente', total: 561, percentual: 3.6 },
                  { etapa: 'Cliente VIP', total: 112, percentual: 0.7 }
                ].map((etapa, index) => (
                  <div key={index}>
                    <div className="flex justify-between items-center mb-2">
                      <span className="font-medium">{etapa.etapa}</span>
                      <div className="text-right">
                        <span className="font-bold">{etapa.total.toLocaleString()}</span>
                        <span className="text-sm text-muted-foreground ml-2">({etapa.percentual}%)</span>
                      </div>
                    </div>
                    <Progress value={etapa.percentual} className="h-2" />
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Tab Produtos */}
        <TabsContent value="products" className="space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            {/* Performance de Produtos */}
            <Card>
              <CardHeader>
                <CardTitle>Performance de Produtos</CardTitle>
                <CardDescription>Vendas vs Margem de lucro</CardDescription>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <ScatterChart>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="vendas" name="Vendas" />
                    <YAxis dataKey="margem" name="Margem %" />
                    <Tooltip cursor={{ strokeDasharray: '3 3' }} />
                    <Scatter name="Produtos" data={productData} fill="#8b5cf6">
                      {productData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Scatter>
                  </ScatterChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            {/* Estoque Crítico */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <AlertTriangle className="h-5 w-5 text-yellow-600" />
                  Alertas de Estoque
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {[
                    { produto: 'iPhone 14', estoque: 3, vendas_dia: 4, dias_restantes: 0.75, status: 'critico' },
                    { produto: 'AirPods', estoque: 12, vendas_dia: 8, dias_restantes: 1.5, status: 'baixo' },
                    { produto: 'Samsung TV', estoque: 8, vendas_dia: 3, dias_restantes: 2.7, status: 'atencao' }
                  ].map((item, index) => (
                    <div key={index} className="p-3 border rounded-lg">
                      <div className="flex justify-between items-start">
                        <div>
                          <p className="font-medium">{item.produto}</p>
                          <p className="text-sm text-muted-foreground">
                            {item.estoque} unidades • {item.vendas_dia}/dia
                          </p>
                        </div>
                        <Badge
                          variant={
                            item.status === 'critico' ? 'destructive' :
                            item.status === 'baixo' ? 'warning' : 'secondary'
                          }
                        >
                          {item.dias_restantes < 1 ? 'Urgente' : `${item.dias_restantes.toFixed(1)} dias`}
                        </Badge>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Análise ABC */}
          <Card>
            <CardHeader>
              <CardTitle>Análise ABC de Produtos</CardTitle>
              <CardDescription>Classificação por importância no faturamento</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="p-4 bg-green-50 dark:bg-green-900/20 rounded-lg">
                  <h3 className="font-semibold text-green-700 dark:text-green-400 mb-2">Classe A (80% receita)</h3>
                  <p className="text-2xl font-bold mb-2">12 produtos</p>
                  <p className="text-sm text-muted-foreground">Alta rotatividade, margem média</p>
                </div>
                <div className="p-4 bg-yellow-50 dark:bg-yellow-900/20 rounded-lg">
                  <h3 className="font-semibold text-yellow-700 dark:text-yellow-400 mb-2">Classe B (15% receita)</h3>
                  <p className="text-2xl font-bold mb-2">28 produtos</p>
                  <p className="text-sm text-muted-foreground">Rotatividade média, boa margem</p>
                </div>
                <div className="p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                  <h3 className="font-semibold text-blue-700 dark:text-blue-400 mb-2">Classe C (5% receita)</h3>
                  <p className="text-2xl font-bold mb-2">156 produtos</p>
                  <p className="text-sm text-muted-foreground">Baixa rotatividade, revisar portfolio</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Tab Comportamento */}
        <TabsContent value="behavior" className="space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            {/* Dispositivos */}
            <Card>
              <CardHeader>
                <CardTitle>Acesso por Dispositivo</CardTitle>
                <CardDescription>Distribuição de acessos por tipo de dispositivo</CardDescription>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <AreaChart data={behaviorData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="hora" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Area type="monotone" dataKey="mobile" stackId="1" stroke="#8b5cf6" fill="#8b5cf6" />
                    <Area type="monotone" dataKey="desktop" stackId="1" stroke="#3b82f6" fill="#3b82f6" />
                    <Area type="monotone" dataKey="tablet" stackId="1" stroke="#10b981" fill="#10b981" />
                  </AreaChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            {/* Taxa de Abandono */}
            <Card>
              <CardHeader>
                <CardTitle>Taxa de Abandono de Carrinho</CardTitle>
                <CardDescription>Motivos principais de abandono</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="text-center py-4">
                    <p className="text-4xl font-bold text-red-600">68%</p>
                    <p className="text-sm text-muted-foreground">Taxa de abandono geral</p>
                  </div>
                  <Separator />
                  <div className="space-y-3">
                    {[
                      { motivo: 'Frete alto', percentual: 35 },
                      { motivo: 'Processo complexo', percentual: 26 },
                      { motivo: 'Preço total', percentual: 17 },
                      { motivo: 'Prazo de entrega', percentual: 13 },
                      { motivo: 'Outros', percentual: 9 }
                    ].map((item, index) => (
                      <div key={index}>
                        <div className="flex justify-between mb-1">
                          <span className="text-sm">{item.motivo}</span>
                          <span className="text-sm font-medium">{item.percentual}%</span>
                        </div>
                        <Progress value={item.percentual} className="h-2" />
                      </div>
                    ))}
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Mapa de Calor de Cliques */}
          <Card>
            <CardHeader>
              <CardTitle>Engajamento por Seção</CardTitle>
              <CardDescription>Taxa de cliques e tempo médio por seção do site</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                {[
                  { secao: 'Hero Banner', cliques: 2340, tempo: '12s', taxa: 15 },
                  { secao: 'Produtos em Destaque', cliques: 5670, tempo: '45s', taxa: 37 },
                  { secao: 'Categorias', cliques: 3456, tempo: '23s', taxa: 22 },
                  { secao: 'Promoções', cliques: 4567, tempo: '34s', taxa: 29 },
                  { secao: 'Newsletter', cliques: 890, tempo: '8s', taxa: 6 },
                  { secao: 'Avaliações', cliques: 2345, tempo: '67s', taxa: 15 },
                  { secao: 'FAQ', cliques: 567, tempo: '89s', taxa: 4 },
                  { secao: 'Rodapé', cliques: 234, tempo: '5s', taxa: 2 }
                ].map((item, index) => (
                  <div
                    key={index}
                    className="p-4 border rounded-lg hover:shadow-md transition-shadow"
                    style={{
                      backgroundColor: `rgba(139, 92, 246, ${item.taxa / 100})`,
                    }}
                  >
                    <p className="font-medium text-sm">{item.secao}</p>
                    <p className="text-2xl font-bold">{item.cliques.toLocaleString()}</p>
                    <div className="flex justify-between mt-2">
                      <span className="text-xs">{item.tempo} médio</span>
                      <span className="text-xs font-medium">{item.taxa}% CTR</span>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Tab Preditivo */}
        <TabsContent value="predictive" className="space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            {/* Previsão de Vendas */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Brain className="h-5 w-5" />
                  Previsão para Próxima Semana
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="p-4 bg-gradient-to-r from-violet-50 to-blue-50 dark:from-violet-900/20 dark:to-blue-900/20 rounded-lg">
                    <p className="text-sm text-muted-foreground mb-1">Receita Prevista</p>
                    <p className="text-3xl font-bold">{formatCurrency(predictiveData.proxima_semana?.receita_prevista || 0)}</p>
                    <div className="flex items-center gap-2 mt-2">
                      <Progress value={predictiveData.proxima_semana?.confianca || 0} className="flex-1 h-2" />
                      <span className="text-sm font-medium">{predictiveData.proxima_semana?.confianca}% confiança</span>
                    </div>
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div className="p-3 border rounded-lg">
                      <p className="text-sm text-muted-foreground">Vendas Previstas</p>
                      <p className="text-xl font-bold">{predictiveData.proxima_semana?.vendas_previstas}</p>
                    </div>
                    <div className="p-3 border rounded-lg">
                      <p className="text-sm text-muted-foreground">Ticket Médio</p>
                      <p className="text-xl font-bold">R$ 108</p>
                    </div>
                  </div>
                  <div>
                    <p className="text-sm font-medium mb-2">Produtos em Alta</p>
                    <div className="flex flex-wrap gap-2">
                      {predictiveData.proxima_semana?.produtos_em_alta?.map((produto: string, index: number) => (
                        <Badge key={index} variant="secondary">{produto}</Badge>
                      ))}
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Segmentos Promissores */}
            <Card>
              <CardHeader>
                <CardTitle>Segmentos com Maior Potencial</CardTitle>
                <CardDescription>Oportunidades identificadas por IA</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {predictiveData.segmentos_promissores?.map((segmento: any, index: number) => (
                    <div key={index} className="flex items-center justify-between p-3 border rounded-lg">
                      <div className="flex items-center gap-3">
                        <div
                          className="w-12 h-12 rounded-full flex items-center justify-center text-white font-bold"
                          style={{ backgroundColor: COLORS[index % COLORS.length] }}
                        >
                          {segmento.potencial}%
                        </div>
                        <div>
                          <p className="font-medium">{segmento.nome}</p>
                          <p className="text-sm text-muted-foreground">Alto potencial de conversão</p>
                        </div>
                      </div>
                      <Button size="sm" variant="outline">
                        <Target className="h-4 w-4 mr-1" />
                        Criar Campanha
                      </Button>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Análise de Tendências */}
          <Card>
            <CardHeader>
              <CardTitle>Análise de Tendências e Padrões</CardTitle>
              <CardDescription>Insights descobertos através de machine learning</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <div className="p-4 border rounded-lg">
                  <Activity className="h-8 w-8 text-violet-600 mb-2" />
                  <p className="font-medium mb-1">Sazonalidade Detectada</p>
                  <p className="text-sm text-muted-foreground">
                    Aumento de 45% nas vendas às quintas-feiras
                  </p>
                </div>
                <div className="p-4 border rounded-lg">
                  <Users className="h-8 w-8 text-blue-600 mb-2" />
                  <p className="font-medium mb-1">Padrão de Compra</p>
                  <p className="text-sm text-muted-foreground">
                    Clientes VIP compram 3x ao mês em média
                  </p>
                </div>
                <div className="p-4 border rounded-lg">
                  <Package className="h-8 w-8 text-green-600 mb-2" />
                  <p className="font-medium mb-1">Cross-selling</p>
                  <p className="text-sm text-muted-foreground">
                    87% de chance de vender case com iPhone
                  </p>
                </div>
                <div className="p-4 border rounded-lg">
                  <Clock className="h-8 w-8 text-orange-600 mb-2" />
                  <p className="font-medium mb-1">Horário Ótimo</p>
                  <p className="text-sm text-muted-foreground">
                    19h-21h tem maior taxa de conversão
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Recomendações de Ação */}
          <Card>
            <CardHeader>
              <CardTitle>Recomendações de Ação</CardTitle>
              <CardDescription>Ações sugeridas baseadas em análise preditiva</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {[
                  {
                    prioridade: 'alta',
                    acao: 'Aumentar estoque de iPhone 14',
                    motivo: 'Previsão de aumento de 35% na demanda',
                    impacto: 'R$ 45.000 de receita adicional'
                  },
                  {
                    prioridade: 'media',
                    acao: 'Criar campanha para clientes inativos',
                    motivo: '234 clientes sem compras há 60 dias',
                    impacto: 'Recuperar R$ 18.000 em vendas'
                  },
                  {
                    prioridade: 'alta',
                    acao: 'Otimizar checkout mobile',
                    motivo: 'Taxa de abandono 15% maior que desktop',
                    impacto: 'Reduzir perda de R$ 8.500/mês'
                  }
                ].map((item, index) => (
                  <div key={index} className="flex items-start gap-3 p-3 border rounded-lg">
                    <Badge
                      variant={item.prioridade === 'alta' ? 'destructive' : 'secondary'}
                      className="mt-0.5"
                    >
                      {item.prioridade}
                    </Badge>
                    <div className="flex-1">
                      <p className="font-medium">{item.acao}</p>
                      <p className="text-sm text-muted-foreground mt-1">{item.motivo}</p>
                      <p className="text-sm font-medium text-green-600 mt-1">{item.impacto}</p>
                    </div>
                    <Button size="sm">Executar</Button>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}