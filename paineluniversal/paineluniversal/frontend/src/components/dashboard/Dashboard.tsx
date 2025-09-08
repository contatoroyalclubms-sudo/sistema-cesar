import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { useAuth } from '../../contexts/AuthContext';
import { dashboardService, eventoService, Evento } from '../../services/api';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/select';
import { Progress } from '../ui/progress';
import { Badge } from '../ui/badge';
import { 
  Calendar, 
  Users, 
  DollarSign, 
  TrendingUp, 
  Clock,
  Trophy,
  BarChart3,
  ArrowUpIcon,
  ArrowDownIcon,
  RefreshCw,
  Eye,
  Activity,
  Zap
} from 'lucide-react';
import { 
  LineChart, 
  Line, 
  AreaChart, 
  Area, 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  Legend, 
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell
} from 'recharts';

interface DashboardData {
  total_eventos: number;
  total_vendas: number;
  total_checkins: number;
  receita_total: number;
  eventos_hoje: number;
  vendas_hoje: number;
}

interface RankingPromoter {
  promoter_id: number;
  nome_promoter: string;
  total_vendas: number;
  receita_gerada: number;
  posicao: number;
}

// Dados mock para gráficos
const vendasPorHora = [
  { hora: '00:00', vendas: 2 },
  { hora: '02:00', vendas: 1 },
  { hora: '04:00', vendas: 0 },
  { hora: '06:00', vendas: 1 },
  { hora: '08:00', vendas: 4 },
  { hora: '10:00', vendas: 8 },
  { hora: '12:00', vendas: 15 },
  { hora: '14:00', vendas: 22 },
  { hora: '16:00', vendas: 18 },
  { hora: '18:00', vendas: 35 },
  { hora: '20:00', vendas: 28 },
  { hora: '22:00', vendas: 12 },
];

const receitaUltimos7Dias = [
  { dia: 'Seg', receita: 2400 },
  { dia: 'Ter', receita: 1398 },
  { dia: 'Qua', receita: 9800 },
  { dia: 'Qui', receita: 3908 },
  { dia: 'Sex', receita: 4800 },
  { dia: 'Sáb', receita: 3800 },
  { dia: 'Dom', receita: 4300 },
];

const tiposEvento = [
  { name: 'Shows', value: 35, color: '#007BFF' },
  { name: 'Festas', value: 25, color: '#0056D6' },
  { name: 'Workshops', value: 20, color: '#3B82F6' },
  { name: 'Conferências', value: 20, color: '#60A5FA' },
];

const Dashboard: React.FC = () => {
  const { usuario } = useAuth();
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null);
  const [ranking, setRanking] = useState<RankingPromoter[]>([]);
  const [eventos, setEventos] = useState<Evento[]>([]);
  const [eventoSelecionado, setEventoSelecionado] = useState<string>('todos');
  const [loading, setLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);

  useEffect(() => {
    carregarDados();
    carregarEventos();
  }, []);

  useEffect(() => {
    if (eventoSelecionado && eventoSelecionado !== 'todos') {
      carregarDadosEvento(parseInt(eventoSelecionado));
    } else {
      carregarDados();
    }
  }, [eventoSelecionado]);

  const carregarDados = async () => {
    try {
      setLoading(true);
      const [stats, eventosProximos, resumoFinanceiro] = await Promise.all([
        dashboardService.getStats(),
        dashboardService.getEventosProximos(),
        dashboardService.getResumoFinanceiro()
      ]);
      
      setDashboardData({
        total_eventos: stats.total_eventos || 0,
        total_vendas: stats.total_vendas || 0,
        total_checkins: stats.total_checkins || 0,
        receita_total: resumoFinanceiro.receita_total || 0,
        eventos_hoje: stats.eventos_hoje || 0,
        vendas_hoje: stats.vendas_hoje || 0,
      });
      
      setRanking([]);
    } catch (error) {
      console.error('Erro ao carregar dados do dashboard:', error);
      setDashboardData({
        total_eventos: 0,
        total_vendas: 0,
        total_checkins: 0,
        receita_total: 0,
        eventos_hoje: 0,
        vendas_hoje: 0,
      });
    } finally {
      setLoading(false);
    }
  };

  const carregarDadosEvento = async (eventoId: number) => {
    try {
      setLoading(true);
      await carregarDados();
    } catch (error) {
      console.error('Erro ao carregar dados do evento:', error);
    } finally {
      setLoading(false);
    }
  };

  const carregarEventos = async () => {
    try {
      const eventosData = await eventoService.getAll();
      setEventos(eventosData);
    } catch (error) {
      console.error('Erro ao carregar eventos:', error);
    }
  };

  const handleRefresh = async () => {
    setIsRefreshing(true);
    await carregarDados();
    setTimeout(() => setIsRefreshing(false), 1000);
  };

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL'
    }).format(value);
  };

  const getGreeting = () => {
    const hour = new Date().getHours();
    if (hour < 12) return 'Bom dia';
    if (hour < 18) return 'Boa tarde';
    return 'Boa noite';
  };

  const cardVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: (i: number) => ({
      opacity: 1,
      y: 0,
      transition: {
        delay: i * 0.1,
        duration: 0.4,
        ease: "easeOut"
      }
    })
  };

  if (loading) {
    return (
      <div className="space-y-6 animate-fade-in">
        <div className="flex items-center justify-between">
          <div className="space-y-2">
            <div className="skeleton h-8 w-48"></div>
            <div className="skeleton h-4 w-96"></div>
          </div>
          <div className="skeleton h-10 w-32"></div>
        </div>
        
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          {[1, 2, 3, 4].map((i) => (
            <Card key={i} className="premium-card">
              <CardContent className="p-6">
                <div className="skeleton h-4 w-24 mb-2"></div>
                <div className="skeleton h-8 w-16 mb-2"></div>
                <div className="skeleton h-3 w-32"></div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="w-full h-full p-4 sm:p-6 lg:p-8 space-y-6">
      {/* Header */}
      <motion.div 
        className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4"
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
      >
        <div className="space-y-1">
          <h1 className="text-2xl sm:text-3xl font-heading font-bold text-foreground">
            {getGreeting()}, {usuario?.nome}! 👋
          </h1>
          <p className="text-sm sm:text-base text-muted-foreground">
            Aqui está o resumo das suas atividades no Sistema Universal de Eventos.
          </p>
        </div>
        
        <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-3">
          <Select value={eventoSelecionado} onValueChange={setEventoSelecionado}>
            <SelectTrigger className="w-full sm:w-64 bg-background">
              <SelectValue placeholder="Todos os eventos" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="todos">Todos os eventos</SelectItem>
              {eventos.map((evento) => (
                <SelectItem key={evento.id} value={evento.id?.toString() || ''}>
                  {evento.nome}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          
          <Button 
            onClick={handleRefresh} 
            variant="outline" 
            size="sm"
            disabled={isRefreshing}
            className="shrink-0"
          >
            <RefreshCw className={`h-4 w-4 mr-2 ${isRefreshing ? 'animate-spin' : ''}`} />
            Atualizar
          </Button>
        </div>
      </motion.div>

      {/* KPI Cards */}
      {/* Métricas Principais */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6">
        {[
          {
            title: 'Total de Eventos',
            value: dashboardData?.total_eventos || 0,
            subtitle: `${dashboardData?.eventos_hoje || 0} eventos hoje`,
            icon: Calendar,
            trend: '+12%',
            trendUp: true,
            gradient: 'from-blue-500 to-cyan-500'
          },
          {
            title: 'Total de Vendas',
            value: dashboardData?.total_vendas || 0,
            subtitle: `${dashboardData?.vendas_hoje || 0} vendas hoje`,
            icon: TrendingUp,
            trend: '+23%',
            trendUp: true,
            gradient: 'from-green-500 to-emerald-500'
          },
          {
            title: 'Check-ins Realizados',
            value: dashboardData?.total_checkins || 0,
            subtitle: 'Pessoas presentes',
            icon: Users,
            trend: '+8%',
            trendUp: true,
            gradient: 'from-purple-500 to-pink-500'
          },
          {
            title: 'Receita Total',
            value: formatCurrency(dashboardData?.receita_total || 0),
            subtitle: 'Faturamento acumulado',
            icon: DollarSign,
            trend: '+18%',
            trendUp: true,
            gradient: 'from-orange-500 to-red-500'
          }
        ].map((card, index) => (
          <motion.div
            key={card.title}
            custom={index}
            variants={cardVariants}
            initial="hidden"
            animate="visible"
            whileHover={{ scale: 1.02, transition: { duration: 0.2 } }}
          >
            <Card className="relative overflow-hidden border border-border bg-card shadow-lg hover:shadow-xl transition-all duration-300 hover:scale-[1.02]">
              <div className={`absolute inset-0 bg-gradient-to-br ${card.gradient} opacity-5`} />
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2 relative z-10">
                <CardTitle className="text-sm font-medium text-muted-foreground">
                  {card.title}
                </CardTitle>
                <div className={`p-2 rounded-lg bg-gradient-to-br ${card.gradient} bg-opacity-10`}>
                  <card.icon className={`h-4 w-4 bg-gradient-to-br ${card.gradient} bg-clip-text text-transparent`} />
                </div>
              </CardHeader>
              <CardContent className="relative z-10">
                <div className="text-2xl sm:text-3xl font-heading font-bold text-foreground mb-1">
                  {typeof card.value === 'string' ? card.value : card.value.toLocaleString()}
                </div>
                <div className="flex items-center justify-between">
                  <p className="text-xs text-muted-foreground">
                    {card.subtitle}
                  </p>
                  <div className="flex items-center text-xs">
                    {card.trendUp ? (
                      <ArrowUpIcon className="h-3 w-3 text-green-500 mr-1" />
                    ) : (
                      <ArrowDownIcon className="h-3 w-3 text-red-500 mr-1" />
                    )}
                    <span className={card.trendUp ? 'text-green-600' : 'text-red-600'}>
                      {card.trend}
                    </span>
                  </div>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        ))}
      </div>

      {/* Charts Section */}
      <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
      {/* Gráficos e Análises */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 sm:gap-6">
        {/* Vendas por Hora */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.4, duration: 0.5 }}
        >
          <Card className="bg-card border border-border shadow-lg">
            <CardHeader>
              <CardTitle className="flex items-center text-foreground">
                <Activity className="h-5 w-5 mr-2 text-primary" />
                Vendas nas Últimas 24h
              </CardTitle>
              <CardDescription>
                Distribuição de vendas por hora do dia
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={250}>
                <AreaChart data={vendasPorHora}>
                  <defs>
                    <linearGradient id="vendas" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#007BFF" stopOpacity={0.3}/>
                      <stop offset="95%" stopColor="#007BFF" stopOpacity={0}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                  <XAxis 
                    dataKey="hora" 
                    stroke="hsl(var(--muted-foreground))"
                    fontSize={12}
                  />
                  <YAxis stroke="hsl(var(--muted-foreground))" fontSize={12} />
                  <Tooltip 
                    contentStyle={{
                      backgroundColor: 'hsl(var(--card))',
                      border: '1px solid hsl(var(--border))',
                      borderRadius: '8px'
                    }}
                  />
                  <Area
                    type="monotone"
                    dataKey="vendas"
                    stroke="#007BFF"
                    strokeWidth={2}
                    fillOpacity={1}
                    fill="url(#vendas)"
                  />
                </AreaChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </motion.div>

        {/* Receita Últimos 7 Dias */}
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.5, duration: 0.5 }}
        >
          <Card className="bg-card border border-border shadow-lg">
            <CardHeader>
              <CardTitle className="flex items-center text-foreground">
                <BarChart3 className="h-5 w-5 mr-2 text-primary" />
                Receita - Últimos 7 Dias
              </CardTitle>
              <CardDescription>
                Evolução da receita diária
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={receitaUltimos7Dias}>
                  <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                  <XAxis 
                    dataKey="dia" 
                    stroke="hsl(var(--muted-foreground))"
                    fontSize={12}
                  />
                  <YAxis stroke="hsl(var(--muted-foreground))" fontSize={12} />
                  <Tooltip 
                    formatter={(value) => [formatCurrency(Number(value)), 'Receita']}
                    contentStyle={{
                      backgroundColor: 'hsl(var(--card))',
                      border: '1px solid hsl(var(--border))',
                      borderRadius: '8px'
                    }}
                  />
                  <Bar 
                    dataKey="receita" 
                    fill="url(#barGradient)"
                    radius={[4, 4, 0, 0]}
                  />
                  <defs>
                    <linearGradient id="barGradient" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#007BFF" stopOpacity={0.8}/>
                      <stop offset="95%" stopColor="#007BFF" stopOpacity={0.3}/>
                    </linearGradient>
                  </defs>
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </motion.div>
      </div>
      </div>

      {/* Additional Info Section */}
      <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
        {/* Tipos de Evento */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6, duration: 0.5 }}
        >
          <Card className="bg-card border border-border shadow-lg">
            <CardHeader>
              <CardTitle className="flex items-center">
                <Zap className="h-5 w-5 mr-2 text-primary" />
                Tipos de Eventos
              </CardTitle>
              <CardDescription>
                Distribuição por categoria
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={250}>
                <PieChart>
                  <Pie
                    data={tiposEvento}
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={100}
                    paddingAngle={5}
                    dataKey="value"
                  >
                    {tiposEvento.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
              <div className="mt-4 space-y-2">
                {tiposEvento.map((tipo) => (
                  <div key={tipo.name} className="flex items-center justify-between">
                    <div className="flex items-center">
                      <div 
                        className="w-3 h-3 rounded-full mr-2" 
                        style={{ backgroundColor: tipo.color }}
                      />
                      <span className="text-sm text-muted-foreground">{tipo.name}</span>
                    </div>
                    <span className="text-sm font-medium">{tipo.value}%</span>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </motion.div>

        {/* Ranking de Promoters */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.7, duration: 0.5 }}
        >
          <Card className="bg-card border border-border shadow-lg">
            <CardHeader>
              <CardTitle className="flex items-center text-foreground">
                <Trophy className="h-5 w-5 mr-2 text-primary" />
                Top Promoters
              </CardTitle>
              <CardDescription>
                Ranking por vendas
              </CardDescription>
            </CardHeader>
            <CardContent>
              {ranking.length > 0 ? (
                <div className="space-y-4">
                  {ranking.slice(0, 5).map((promoter, index) => (
                    <motion.div 
                      key={promoter.promoter_id} 
                      className="flex items-center justify-between p-3 rounded-lg bg-muted/30 hover:bg-muted/50 transition-colors"
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: 0.8 + index * 0.1 }}
                    >
                      <div className="flex items-center space-x-3">
                        <Badge variant={index === 0 ? 'default' : 'secondary'} className="w-8 h-8 rounded-full flex items-center justify-center">
                          {promoter.posicao}
                        </Badge>
                        <div>
                          <p className="font-medium text-foreground">{promoter.nome_promoter}</p>
                          <p className="text-sm text-muted-foreground">
                            {promoter.total_vendas} vendas
                          </p>
                        </div>
                      </div>
                      <div className="text-right">
                        <p className="font-medium text-foreground">
                          {formatCurrency(promoter.receita_gerada)}
                        </p>
                      </div>
                    </motion.div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8 text-muted-foreground">
                  <Eye className="h-12 w-12 mx-auto mb-2 opacity-50" />
                  <p>Nenhum dado disponível</p>
                </div>
              )}
            </CardContent>
          </Card>
        </motion.div>

        {/* Status do Sistema */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.8, duration: 0.5 }}
        >
          <Card className="bg-card border border-border shadow-lg">
            <CardHeader>
              <CardTitle className="flex items-center text-foreground">
                <Activity className="h-5 w-5 mr-2 text-primary" />
                Status do Sistema
              </CardTitle>
              <CardDescription>
                Performance atual
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <div className="flex justify-between text-sm mb-2">
                  <span className="text-muted-foreground">CPU</span>
                  <span className="text-foreground font-medium">45%</span>
                </div>
                <Progress value={45} className="h-2" />
              </div>
              
              <div>
                <div className="flex justify-between text-sm mb-2">
                  <span className="text-muted-foreground">Memória</span>
                  <span className="text-foreground font-medium">62%</span>
                </div>
                <Progress value={62} className="h-2" />
              </div>
              
              <div>
                <div className="flex justify-between text-sm mb-2">
                  <span className="text-muted-foreground">Storage</span>
                  <span className="text-foreground font-medium">28%</span>
                </div>
                <Progress value={28} className="h-2" />
              </div>
              
              <div className="pt-4 border-t border-border">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-muted-foreground">Status Geral</span>
                  <Badge variant="default" className="bg-green-500 hover:bg-green-600">
                    Operacional
                  </Badge>
                </div>
              </div>
            </CardContent>
          </Card>
        </motion.div>
      </div>

      {/* Eventos Recentes */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.9, duration: 0.5 }}
      >
        <Card className="bg-card border border-border shadow-lg">
          <CardHeader>
            <CardTitle className="flex items-center text-foreground">
              <Calendar className="h-5 w-5 mr-2 text-primary" />
              Eventos Recentes
            </CardTitle>
            <CardDescription>
              Últimos eventos criados no sistema
            </CardDescription>
          </CardHeader>
          <CardContent>
            {eventos.length > 0 ? (
              <div className="space-y-4">
                {eventos.slice(0, 5).map((evento, index) => (
                  <motion.div 
                    key={evento.id} 
                    className="flex flex-col sm:flex-row sm:items-center justify-between p-4 rounded-lg border border-border bg-card/50 hover:bg-card transition-colors gap-3"
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 1 + index * 0.1 }}
                  >
                    <div className="flex items-center space-x-4">
                      <div className="w-10 h-10 sm:w-12 sm:h-12 bg-gradient-to-br from-primary to-primary/80 rounded-lg flex items-center justify-center shrink-0">
                        <Calendar className="h-5 w-5 sm:h-6 sm:w-6 text-primary-foreground" />
                      </div>
                      <div className="min-w-0 flex-1">
                        <h3 className="font-medium text-foreground truncate">{evento.nome}</h3>
                        <p className="text-sm text-muted-foreground truncate">{evento.local}</p>
                        <p className="text-xs text-muted-foreground">
                          {new Date(evento.data_evento).toLocaleDateString('pt-BR')}
                        </p>
                      </div>
                    </div>
                    
                    <div className="text-right space-y-1">
                      <Badge variant={
                        evento.status === 'ativo' ? 'default' : 
                        evento.status === 'cancelado' ? 'destructive' : 'secondary'
                      }>
                        {evento.status}
                      </Badge>
                      {evento.capacidade_maxima && (
                        <p className="text-xs text-muted-foreground">
                          {evento.capacidade_maxima} pessoas
                        </p>
                      )}
                    </div>
                  </motion.div>
                ))}
              </div>
            ) : (
              <div className="text-center py-12 text-muted-foreground">
                <Calendar className="h-16 w-16 mx-auto mb-4 opacity-20" />
                <p className="text-lg font-medium mb-2">Nenhum evento encontrado</p>
                <p className="text-sm">Crie seu primeiro evento para começar</p>
              </div>
            )}
          </CardContent>
        </Card>
      </motion.div>
    </div>
  );
};

export default Dashboard;