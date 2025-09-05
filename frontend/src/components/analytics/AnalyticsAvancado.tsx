import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Alert, AlertDescription } from '@/components/ui/alert';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  PieChart,
  Pie,
  AreaChart,
  Area,
  RadarChart,
  Radar,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Cell,
  Treemap,
  ScatterChart,
  Scatter,
} from 'recharts';
import { useToast } from '@/hooks/use-toast';
import { useEventoContext } from '@/contexts/EventoContext';
import api from '@/lib/api';
import {
  TrendingUp,
  TrendingDown,
  Users,
  DollarSign,
  Calendar,
  Clock,
  Activity,
  Target,
  Award,
  AlertTriangle,
  Filter,
  Download,
  RefreshCw,
  Map,
  ThermometerSun,
  UserCheck,
  ShoppingCart,
  Percent,
  Timer,
  Eye,
  MousePointer,
  Smartphone,
  Monitor,
  Globe,
} from 'lucide-react';
import { format, subDays, startOfWeek, endOfWeek } from 'date-fns';
import { ptBR } from 'date-fns/locale';

interface EventoAnalytics {
  id: number;
  evento_id: number;
  total_participantes: number;
  total_checkins: number;
  total_vendas: number;
  receita_total: number;
  taxa_conversao: number;
  tempo_medio_permanencia: number;
  pico_ocupacao: string;
  satisfacao_media: number;
  nps_score: number;
  engagement_rate: number;
  roi: number;
  data_analise: string;
}

interface Metrica {
  nome: string;
  valor: number;
  variacao: number;
  icon: any;
  color: string;
}

interface HeatmapData {
  hora: number;
  area: string;
  ocupacao: number;
}

interface PrevisaoData {
  data: string;
  vendas_previstas: number;
  participantes_previstos: number;
  receita_prevista: number;
  confianca: number;
}

const COLORS = ['#8884d8', '#82ca9d', '#ffc658', '#ff7c7c', '#8dd1e1', '#d084d0', '#ffb347', '#67b7dc'];

export default function AnalyticsAvancado() {
  const [analytics, setAnalytics] = useState<EventoAnalytics | null>(null);
  const [metricas, setMetricas] = useState<Metrica[]>([]);
  const [vendasPorHora, setVendasPorHora] = useState<any[]>([]);
  const [vendasPorCategoria, setVendasPorCategoria] = useState<any[]>([]);
  const [fluxoPorArea, setFluxoPorArea] = useState<any[]>([]);
  const [heatmapData, setHeatmapData] = useState<HeatmapData[]>([]);
  const [previsoes, setPrevisoes] = useState<PrevisaoData[]>([]);
  const [demograficos, setDemograficos] = useState<any[]>([]);
  const [dispositivoData, setDispositivoData] = useState<any[]>([]);
  const [engagementData, setEngagementData] = useState<any[]>([]);
  const [periodo, setPeriodo] = useState('hoje');
  const [loading, setLoading] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const { eventoSelecionado } = useEventoContext();
  const { toast } = useToast();

  useEffect(() => {
    if (eventoSelecionado) {
      loadAnalytics();
    }
  }, [eventoSelecionado, periodo]);

  const loadAnalytics = async () => {
    if (!eventoSelecionado) return;

    try {
      setLoading(true);
      
      // Simular dados para demonstração
      const mockAnalytics: EventoAnalytics = {
        id: 1,
        evento_id: eventoSelecionado.id,
        total_participantes: 1250,
        total_checkins: 1180,
        total_vendas: 3450,
        receita_total: 125000,
        taxa_conversao: 68.5,
        tempo_medio_permanencia: 240,
        pico_ocupacao: '22:00',
        satisfacao_media: 4.7,
        nps_score: 72,
        engagement_rate: 85.3,
        roi: 245,
        data_analise: new Date().toISOString(),
      };
      
      setAnalytics(mockAnalytics);
      
      // Calcular métricas
      const metricasCalculadas: Metrica[] = [
        {
          nome: 'Total Participantes',
          valor: mockAnalytics.total_participantes,
          variacao: 12.5,
          icon: Users,
          color: 'text-blue-600',
        },
        {
          nome: 'Receita Total',
          valor: mockAnalytics.receita_total,
          variacao: 18.3,
          icon: DollarSign,
          color: 'text-green-600',
        },
        {
          nome: 'Taxa de Check-in',
          valor: (mockAnalytics.total_checkins / mockAnalytics.total_participantes) * 100,
          variacao: 5.2,
          icon: UserCheck,
          color: 'text-purple-600',
        },
        {
          nome: 'Engagement',
          valor: mockAnalytics.engagement_rate,
          variacao: -2.1,
          icon: Activity,
          color: 'text-orange-600',
        },
      ];
      
      setMetricas(metricasCalculadas);
      
      // Vendas por hora
      const vendasHora = Array.from({ length: 24 }, (_, i) => ({
        hora: `${i}:00`,
        vendas: Math.floor(Math.random() * 200) + 50,
        checkins: Math.floor(Math.random() * 100) + 20,
      }));
      setVendasPorHora(vendasHora);
      
      // Vendas por categoria
      const categorias = [
        { nome: 'Bebidas', vendas: 1250, valor: 45000 },
        { nome: 'Comidas', vendas: 890, valor: 35000 },
        { nome: 'Merchandising', vendas: 450, valor: 15000 },
        { nome: 'Ingressos VIP', vendas: 320, valor: 25000 },
        { nome: 'Estacionamento', vendas: 540, valor: 5000 },
      ];
      setVendasPorCategoria(categorias);
      
      // Fluxo por área
      const areas = [
        { area: 'Entrada', fluxo: 1250, capacidade: 1500 },
        { area: 'Palco Principal', fluxo: 850, capacidade: 1000 },
        { area: 'Área VIP', fluxo: 120, capacidade: 200 },
        { area: 'Praça Alimentação', fluxo: 450, capacidade: 500 },
        { area: 'Banheiros', fluxo: 80, capacidade: 100 },
      ];
      setFluxoPorArea(areas);
      
      // Heatmap de ocupação
      const heatmap: HeatmapData[] = [];
      ['Entrada', 'Palco', 'VIP', 'Alimentação', 'Bar'].forEach(area => {
        for (let hora = 18; hora <= 23; hora++) {
          heatmap.push({
            hora,
            area,
            ocupacao: Math.floor(Math.random() * 100),
          });
        }
      });
      setHeatmapData(heatmap);
      
      // Previsões
      const previsoesDados: PrevisaoData[] = Array.from({ length: 7 }, (_, i) => ({
        data: format(new Date(Date.now() + i * 24 * 60 * 60 * 1000), 'dd/MM'),
        vendas_previstas: Math.floor(Math.random() * 500) + 300,
        participantes_previstos: Math.floor(Math.random() * 200) + 100,
        receita_prevista: Math.floor(Math.random() * 20000) + 10000,
        confianca: 85 + Math.random() * 10,
      }));
      setPrevisoes(previsoesDados);
      
      // Dados demográficos
      const demograficosDados = [
        { faixa: '18-24', quantidade: 350, porcentagem: 28 },
        { faixa: '25-34', quantidade: 450, porcentagem: 36 },
        { faixa: '35-44', quantidade: 280, porcentagem: 22.4 },
        { faixa: '45-54', quantidade: 120, porcentagem: 9.6 },
        { faixa: '55+', quantidade: 50, porcentagem: 4 },
      ];
      setDemograficos(demograficosDados);
      
      // Dispositivos
      const dispositivos = [
        { tipo: 'Mobile', usuarios: 750, porcentagem: 60 },
        { tipo: 'Desktop', usuarios: 375, porcentagem: 30 },
        { tipo: 'Tablet', usuarios: 125, porcentagem: 10 },
      ];
      setDispositivoData(dispositivos);
      
      // Engagement por canal
      const engagement = [
        { canal: 'Instagram', alcance: 15000, engagement: 8.5 },
        { canal: 'Facebook', alcance: 12000, engagement: 5.2 },
        { canal: 'WhatsApp', alcance: 8000, engagement: 12.3 },
        { canal: 'Email', alcance: 5000, engagement: 25.4 },
        { canal: 'SMS', alcance: 3000, engagement: 18.7 },
      ];
      setEngagementData(engagement);
      
    } catch (error) {
      console.error('Erro ao carregar analytics:', error);
      toast({
        variant: 'destructive',
        title: 'Erro',
        description: 'Não foi possível carregar os dados analíticos',
      });
    } finally {
      setLoading(false);
    }
  };

  const handleRefresh = async () => {
    setRefreshing(true);
    await loadAnalytics();
    setRefreshing(false);
    
    toast({
      title: 'Dados atualizados',
      description: 'Analytics atualizado com sucesso',
    });
  };

  const handleExportData = () => {
    // Implementar exportação de dados
    toast({
      title: 'Exportando dados',
      description: 'Preparando arquivo para download...',
    });
  };

  const getVariacaoIcon = (variacao: number) => {
    if (variacao > 0) {
      return <TrendingUp className="h-4 w-4 text-green-600" />;
    } else if (variacao < 0) {
      return <TrendingDown className="h-4 w-4 text-red-600" />;
    }
    return null;
  };

  const getOcupacaoColor = (ocupacao: number) => {
    if (ocupacao < 30) return '#4ade80'; // Verde
    if (ocupacao < 60) return '#facc15'; // Amarelo
    if (ocupacao < 80) return '#fb923c'; // Laranja
    return '#ef4444'; // Vermelho
  };

  if (!eventoSelecionado) {
    return (
      <div className="container mx-auto p-6">
        <Alert>
          <AlertTriangle className="h-4 w-4" />
          <AlertDescription>
            Selecione um evento para visualizar analytics
          </AlertDescription>
        </Alert>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="container mx-auto p-6">
        <div className="flex items-center justify-center h-96">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-6 space-y-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-3xl font-bold">Analytics Avançado</h1>
          <p className="text-muted-foreground">
            Análise completa de {eventoSelecionado.nome}
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Select value={periodo} onValueChange={setPeriodo}>
            <SelectTrigger className="w-[180px]">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="hoje">Hoje</SelectItem>
              <SelectItem value="ontem">Ontem</SelectItem>
              <SelectItem value="7dias">Últimos 7 dias</SelectItem>
              <SelectItem value="30dias">Últimos 30 dias</SelectItem>
              <SelectItem value="total">Total</SelectItem>
            </SelectContent>
          </Select>
          <Button onClick={handleRefresh} variant="outline" disabled={refreshing}>
            <RefreshCw className={`mr-2 h-4 w-4 ${refreshing ? 'animate-spin' : ''}`} />
            Atualizar
          </Button>
          <Button onClick={handleExportData}>
            <Download className="mr-2 h-4 w-4" />
            Exportar
          </Button>
        </div>
      </div>

      {/* KPIs Principais */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {metricas.map((metrica) => {
          const Icon = metrica.icon;
          return (
            <Card key={metrica.nome}>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">
                  {metrica.nome}
                </CardTitle>
                <Icon className={`h-4 w-4 ${metrica.color}`} />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {metrica.nome.includes('Receita') 
                    ? `R$ ${metrica.valor.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}`
                    : metrica.nome.includes('Taxa') || metrica.nome.includes('Engagement')
                    ? `${metrica.valor.toFixed(1)}%`
                    : metrica.valor.toLocaleString('pt-BR')}
                </div>
                <div className="flex items-center gap-1 mt-1">
                  {getVariacaoIcon(metrica.variacao)}
                  <span className={`text-xs ${metrica.variacao > 0 ? 'text-green-600' : 'text-red-600'}`}>
                    {Math.abs(metrica.variacao).toFixed(1)}% vs período anterior
                  </span>
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>

      <Tabs defaultValue="vendas" className="space-y-4">
        <TabsList className="grid w-full grid-cols-6">
          <TabsTrigger value="vendas">Vendas</TabsTrigger>
          <TabsTrigger value="ocupacao">Ocupação</TabsTrigger>
          <TabsTrigger value="demografico">Demográfico</TabsTrigger>
          <TabsTrigger value="engagement">Engagement</TabsTrigger>
          <TabsTrigger value="previsoes">Previsões</TabsTrigger>
          <TabsTrigger value="heatmap">Heatmap</TabsTrigger>
        </TabsList>

        <TabsContent value="vendas" className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle>Vendas por Hora</CardTitle>
                <CardDescription>
                  Distribuição de vendas e check-ins ao longo do dia
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <AreaChart data={vendasPorHora}>
                    <defs>
                      <linearGradient id="colorVendas" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#8884d8" stopOpacity={0.8}/>
                        <stop offset="95%" stopColor="#8884d8" stopOpacity={0}/>
                      </linearGradient>
                      <linearGradient id="colorCheckins" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#82ca9d" stopOpacity={0.8}/>
                        <stop offset="95%" stopColor="#82ca9d" stopOpacity={0}/>
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="hora" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Area
                      type="monotone"
                      dataKey="vendas"
                      stroke="#8884d8"
                      fillOpacity={1}
                      fill="url(#colorVendas)"
                    />
                    <Area
                      type="monotone"
                      dataKey="checkins"
                      stroke="#82ca9d"
                      fillOpacity={1}
                      fill="url(#colorCheckins)"
                    />
                  </AreaChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Vendas por Categoria</CardTitle>
                <CardDescription>
                  Distribuição de vendas por tipo de produto
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={vendasPorCategoria}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={(entry) => `${entry.nome}: ${entry.vendas}`}
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="vendas"
                    >
                      {vendasPorCategoria.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </div>

          <Card>
            <CardHeader>
              <CardTitle>Top Produtos</CardTitle>
              <CardDescription>
                Produtos mais vendidos no evento
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {vendasPorCategoria.map((categoria, index) => (
                  <div key={categoria.nome} className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <div
                        className="w-3 h-3 rounded-full"
                        style={{ backgroundColor: COLORS[index % COLORS.length] }}
                      />
                      <span className="font-medium">{categoria.nome}</span>
                    </div>
                    <div className="flex items-center gap-4">
                      <span className="text-sm text-muted-foreground">
                        {categoria.vendas} vendas
                      </span>
                      <span className="font-medium">
                        R$ {categoria.valor.toLocaleString('pt-BR')}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="ocupacao" className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle>Ocupação por Área</CardTitle>
                <CardDescription>
                  Taxa de ocupação atual vs capacidade máxima
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={fluxoPorArea}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="area" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Bar dataKey="fluxo" fill="#8884d8" name="Ocupação Atual" />
                    <Bar dataKey="capacidade" fill="#82ca9d" name="Capacidade" />
                  </BarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Taxa de Ocupação</CardTitle>
                <CardDescription>
                  Percentual de ocupação por área
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                {fluxoPorArea.map((area) => {
                  const taxa = (area.fluxo / area.capacidade) * 100;
                  return (
                    <div key={area.area} className="space-y-2">
                      <div className="flex items-center justify-between">
                        <span className="text-sm font-medium">{area.area}</span>
                        <span className="text-sm text-muted-foreground">
                          {area.fluxo}/{area.capacidade}
                        </span>
                      </div>
                      <Progress value={taxa} className="h-2" />
                      <div className="flex items-center justify-between">
                        <Badge
                          variant={taxa > 80 ? 'destructive' : taxa > 60 ? 'secondary' : 'default'}
                        >
                          {taxa.toFixed(1)}%
                        </Badge>
                        {taxa > 80 && (
                          <span className="text-xs text-destructive flex items-center gap-1">
                            <AlertTriangle className="h-3 w-3" />
                            Área lotada
                          </span>
                        )}
                      </div>
                    </div>
                  );
                })}
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="demografico" className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle>Faixa Etária</CardTitle>
                <CardDescription>
                  Distribuição de participantes por idade
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={demograficos}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="faixa" />
                    <YAxis />
                    <Tooltip />
                    <Bar dataKey="quantidade" fill="#8884d8">
                      {demograficos.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Dispositivos</CardTitle>
                <CardDescription>
                  Tipos de dispositivos utilizados
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={dispositivoData}
                      cx="50%"
                      cy="50%"
                      innerRadius={60}
                      outerRadius={80}
                      fill="#8884d8"
                      paddingAngle={5}
                      dataKey="usuarios"
                    >
                      {dispositivoData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
                <div className="mt-4 space-y-2">
                  {dispositivoData.map((dispositivo, index) => (
                    <div key={dispositivo.tipo} className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <div
                          className="w-3 h-3 rounded-full"
                          style={{ backgroundColor: COLORS[index % COLORS.length] }}
                        />
                        <span className="text-sm">{dispositivo.tipo}</span>
                      </div>
                      <span className="text-sm font-medium">
                        {dispositivo.porcentagem}%
                      </span>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="engagement" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Engagement por Canal</CardTitle>
              <CardDescription>
                Taxa de engajamento em diferentes canais de comunicação
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={400}>
                <RadarChart data={engagementData}>
                  <PolarGrid />
                  <PolarAngleAxis dataKey="canal" />
                  <PolarRadiusAxis />
                  <Radar
                    name="Alcance (mil)"
                    dataKey="alcance"
                    stroke="#8884d8"
                    fill="#8884d8"
                    fillOpacity={0.6}
                  />
                  <Radar
                    name="Engagement (%)"
                    dataKey="engagement"
                    stroke="#82ca9d"
                    fill="#82ca9d"
                    fillOpacity={0.6}
                  />
                  <Legend />
                </RadarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>

          <div className="grid gap-4 md:grid-cols-3">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">
                  NPS Score
                </CardTitle>
                <Award className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{analytics?.nps_score}</div>
                <Progress value={analytics?.nps_score || 0} className="mt-2" />
                <p className="text-xs text-muted-foreground mt-2">
                  Excelente pontuação de satisfação
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">
                  Satisfação Média
                </CardTitle>
                <Target className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {analytics?.satisfacao_media.toFixed(1)}/5.0
                </div>
                <div className="flex gap-1 mt-2">
                  {[...Array(5)].map((_, i) => (
                    <div
                      key={i}
                      className={`w-6 h-6 rounded ${
                        i < Math.floor(analytics?.satisfacao_media || 0)
                          ? 'bg-yellow-400'
                          : 'bg-gray-200'
                      }`}
                    />
                  ))}
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">
                  ROI do Evento
                </CardTitle>
                <TrendingUp className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-green-600">
                  {analytics?.roi}%
                </div>
                <p className="text-xs text-muted-foreground mt-2">
                  Retorno sobre investimento
                </p>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="previsoes" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Previsões com IA</CardTitle>
              <CardDescription>
                Projeções baseadas em machine learning para os próximos dias
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={400}>
                <LineChart data={previsoes}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="data" />
                  <YAxis yAxisId="left" />
                  <YAxis yAxisId="right" orientation="right" />
                  <Tooltip />
                  <Legend />
                  <Line
                    yAxisId="left"
                    type="monotone"
                    dataKey="vendas_previstas"
                    stroke="#8884d8"
                    name="Vendas"
                    strokeDasharray="5 5"
                  />
                  <Line
                    yAxisId="left"
                    type="monotone"
                    dataKey="participantes_previstos"
                    stroke="#82ca9d"
                    name="Participantes"
                    strokeDasharray="5 5"
                  />
                  <Line
                    yAxisId="right"
                    type="monotone"
                    dataKey="receita_prevista"
                    stroke="#ffc658"
                    name="Receita (R$)"
                    strokeDasharray="5 5"
                  />
                </LineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>

          <div className="grid gap-4 md:grid-cols-2">
            {previsoes.slice(0, 2).map((previsao) => (
              <Card key={previsao.data}>
                <CardHeader>
                  <CardTitle className="text-lg">
                    Previsão para {previsao.data}
                  </CardTitle>
                  <CardDescription>
                    Confiança: {previsao.confianca.toFixed(1)}%
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-sm">Vendas esperadas</span>
                    <span className="font-medium">{previsao.vendas_previstas}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm">Participantes esperados</span>
                    <span className="font-medium">{previsao.participantes_previstos}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm">Receita esperada</span>
                    <span className="font-medium">
                      R$ {previsao.receita_prevista.toLocaleString('pt-BR')}
                    </span>
                  </div>
                  <Progress value={previsao.confianca} className="mt-2" />
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="heatmap" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Mapa de Calor - Ocupação</CardTitle>
              <CardDescription>
                Visualização da ocupação por área e horário
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-7 gap-2">
                <div></div>
                {[18, 19, 20, 21, 22, 23].map(hora => (
                  <div key={hora} className="text-center text-sm font-medium">
                    {hora}:00
                  </div>
                ))}
                
                {['Entrada', 'Palco', 'VIP', 'Alimentação', 'Bar'].map(area => (
                  <React.Fragment key={area}>
                    <div className="text-sm font-medium flex items-center">
                      {area}
                    </div>
                    {[18, 19, 20, 21, 22, 23].map(hora => {
                      const data = heatmapData.find(d => d.area === area && d.hora === hora);
                      const ocupacao = data?.ocupacao || 0;
                      return (
                        <div
                          key={`${area}-${hora}`}
                          className="h-12 rounded flex items-center justify-center text-xs font-medium"
                          style={{
                            backgroundColor: getOcupacaoColor(ocupacao),
                            color: ocupacao > 60 ? 'white' : 'black',
                          }}
                        >
                          {ocupacao}%
                        </div>
                      );
                    })}
                  </React.Fragment>
                ))}
              </div>
              
              <div className="flex items-center justify-center gap-4 mt-6">
                <div className="flex items-center gap-2">
                  <div className="w-4 h-4 rounded" style={{ backgroundColor: '#4ade80' }} />
                  <span className="text-sm">Baixa (0-30%)</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-4 h-4 rounded" style={{ backgroundColor: '#facc15' }} />
                  <span className="text-sm">Média (30-60%)</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-4 h-4 rounded" style={{ backgroundColor: '#fb923c' }} />
                  <span className="text-sm">Alta (60-80%)</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-4 h-4 rounded" style={{ backgroundColor: '#ef4444' }} />
                  <span className="text-sm">Lotado (80%+)</span>
                </div>
              </div>
            </CardContent>
          </Card>

          {analytics && (
            <Alert>
              <ThermometerSun className="h-4 w-4" />
              <AlertDescription>
                <strong>Pico de ocupação:</strong> {analytics.pico_ocupacao} - 
                Considere reforçar equipe e segurança neste horário
              </AlertDescription>
            </Alert>
          )}
        </TabsContent>
      </Tabs>
    </div>
  );
}