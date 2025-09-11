import React, { useState, useEffect } from 'react';
import { 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  LineChart, Line, PieChart, Pie, Cell, Area, AreaChart
} from 'recharts';
import {
  TrendingUp, TrendingDown, Users, DollarSign, ShoppingCart, 
  Calendar, Eye, Target, Activity, Award
} from 'lucide-react';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '../ui/card';
import { Badge } from '../ui/badge';
import { Progress } from '../ui/progress';
import {
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
} from '../ui/tabs';

// MEEP-inspired Mock data - baseado na engenharia reversa do sistema MEEP
const mockDashboardData = {
  kpis: {
    totalRevenue: 23063.01, // Baseado nos dados reais MEEP
    totalCustomers: 7194, // Clientes fidelizados MEEP
    totalOrders: 1394, // Comandas ativas MEEP
    avgOrderValue: 198.82, // Ticket médio por conta MEEP
    revenueGrowth: 12.5,
    customerGrowth: 8.3,
    ordersGrowth: 15.2,
    avgGrowth: 5.7,
    taxaServico: 1486.25, // Taxa de serviço MEEP
    saldoDisponivel: 0.00,
    saldoRetido: 148.07,
    dinheiro: 22222.71,
    pix: 0.00,
    credito: 0.00,
    debito: 0.00,
    voucher: 0.00,
    outros: 840.30
  },
  revenueChart: [
    { month: 'Jan', revenue: 12000, orders: 150 },
    { month: 'Fev', revenue: 15000, orders: 180 },
    { month: 'Mar', revenue: 18000, orders: 220 },
    { month: 'Abr', revenue: 22000, orders: 280 },
    { month: 'Mai', revenue: 25000, orders: 320 },
    { month: 'Jun', revenue: 28000, orders: 353 }
  ],
  customerSegmentation: [
    { name: 'VIP', value: 35, color: '#8884d8' },
    { name: 'Premium', value: 45, color: '#82ca9d' },
    { name: 'Regular', value: 20, color: '#ffc658' }
  ],
  topProducts: [
    { name: 'Produto Premium A', sales: 1250, revenue: 62500 },
    { name: 'Produto Standard B', sales: 980, revenue: 39200 },
    { name: 'Produto Deluxe C', sales: 750, revenue: 52500 },
    { name: 'Produto Basic D', sales: 650, revenue: 19500 },
    { name: 'Produto Pro E', sales: 580, revenue: 34800 }
  ],
  realTimeMetrics: {
    activeUsers: 127,
    todayOrders: 43,
    todayRevenue: 4580.75,
    conversionRate: 3.2,
    // Métricas operacionais MEEP
    comandasAbertas: 0,
    comandasOcupadas: 2,
    comandasDisponiveis: 1394,
    percentualOcupacao: 0.1,
    comandasComTaxa: 84,
    comandasSemTaxa: 32,
    comandasFechadasManualmente: 6,
    comandasSemConsumo: 163
  }
};

const DashboardAnalyticsModule: React.FC = () => {
  const [data, setData] = useState(mockDashboardData);
  const [loading, setLoading] = useState(false);

  // Função para carregar dados reais (será implementada quando APIs estiverem funcionais)
  const loadDashboardData = async () => {
    setLoading(true);
    try {
      // TODO: Substituir por chamadas reais às APIs do Cloud_01
      // const response = await api.get('/dashboard-analytics/general');
      // setData(response.data);
      
      // Por enquanto, simula carregamento
      setTimeout(() => {
        setData(mockDashboardData);
        setLoading(false);
      }, 1000);
    } catch (error) {
      console.error('Erro ao carregar dados do dashboard:', error);
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDashboardData();
    
    // Atualização em tempo real a cada 30 segundos
    const interval = setInterval(loadDashboardData, 30000);
    return () => clearInterval(interval);
  }, []);

  const KPICard: React.FC<{
    title: string;
    value: string | number;
    growth: number;
    icon: React.ReactNode;
    format?: 'currency' | 'number' | 'percentage';
  }> = ({ title, value, growth, icon, format = 'number' }) => {
    const formatValue = (val: string | number) => {
      if (format === 'currency') {
        return `R$ ${Number(val).toLocaleString('pt-BR', { minimumFractionDigits: 2 })}`;
      }
      if (format === 'percentage') {
        return `${val}%`;
      }
      return Number(val).toLocaleString('pt-BR');
    };

    return (
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">{title}</CardTitle>
          {icon}
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{formatValue(value)}</div>
          <div className="flex items-center text-xs text-muted-foreground">
            {growth > 0 ? (
              <TrendingUp className="mr-1 h-3 w-3 text-green-500" />
            ) : (
              <TrendingDown className="mr-1 h-3 w-3 text-red-500" />
            )}
            <span className={growth > 0 ? 'text-green-500' : 'text-red-500'}>
              {Math.abs(growth)}% em relação ao mês anterior
            </span>
          </div>
        </CardContent>
      </Card>
    );
  };

  return (
    <div className="flex-1 space-y-4 p-4 pt-6">
      <div className="flex items-center justify-between space-y-2">
        <h2 className="text-3xl font-bold tracking-tight">Dashboard Analytics</h2>
        <div className="flex items-center space-x-2">
          <Badge variant="outline" className="bg-green-50 text-green-700">
            <Activity className="mr-1 h-3 w-3" />
            Sistema Ativo
          </Badge>
          <Badge variant="outline">
            {data.realTimeMetrics.activeUsers} usuários online
          </Badge>
        </div>
      </div>

      <Tabs defaultValue="overview" className="space-y-4">
        <TabsList>
          <TabsTrigger value="overview">Visão Geral</TabsTrigger>
          <TabsTrigger value="revenue">Receita</TabsTrigger>
          <TabsTrigger value="customers">Clientes</TabsTrigger>
          <TabsTrigger value="products">Produtos</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-4">
          {/* KPIs Grid */}
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            <KPICard
              title="Receita Total"
              value={data.kpis.totalRevenue}
              growth={data.kpis.revenueGrowth}
              icon={<DollarSign className="h-4 w-4 text-muted-foreground" />}
              format="currency"
            />
            <KPICard
              title="Total de Clientes"
              value={data.kpis.totalCustomers}
              growth={data.kpis.customerGrowth}
              icon={<Users className="h-4 w-4 text-muted-foreground" />}
            />
            <KPICard
              title="Comandas Ativas"
              value={data.kpis.totalOrders}
              growth={data.kpis.ordersGrowth}
              icon={<ShoppingCart className="h-4 w-4 text-muted-foreground" />}
            />
            <KPICard
              title="Ticket Médio"
              value={data.kpis.avgOrderValue}
              growth={data.kpis.avgGrowth}
              icon={<Target className="h-4 w-4 text-muted-foreground" />}
              format="currency"
            />
          </div>

          {/* Revenue Chart */}
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-7">
            <Card className="col-span-4">
              <CardHeader>
                <CardTitle>Evolução da Receita</CardTitle>
                <CardDescription>
                  Receita e pedidos nos últimos 6 meses
                </CardDescription>
              </CardHeader>
              <CardContent className="pl-2">
                <ResponsiveContainer width="100%" height={350}>
                  <AreaChart data={data.revenueChart}>
                    <defs>
                      <linearGradient id="colorRevenue" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#8884d8" stopOpacity={0.8}/>
                        <stop offset="95%" stopColor="#8884d8" stopOpacity={0}/>
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="month" />
                    <YAxis />
                    <Tooltip 
                      formatter={(value, name) => [
                        name === 'revenue' ? `R$ ${Number(value).toLocaleString('pt-BR')}` : value,
                        name === 'revenue' ? 'Receita' : 'Pedidos'
                      ]}
                    />
                    <Area 
                      type="monotone" 
                      dataKey="revenue" 
                      stroke="#8884d8" 
                      fillOpacity={1} 
                      fill="url(#colorRevenue)" 
                    />
                  </AreaChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            <Card className="col-span-3">
              <CardHeader>
                <CardTitle>Segmentação de Clientes</CardTitle>
                <CardDescription>
                  Distribuição por categoria
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={data.customerSegmentation}
                      cx="50%"
                      cy="50%"
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="value"
                      label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                    >
                      {data.customerSegmentation.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </div>

          {/* Métricas Operacionais MEEP-style */}
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Activity className="mr-2 h-5 w-5" />
                  Centro de Controle Operacional
                </CardTitle>
                <CardDescription>Monitoramento em tempo real</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div className="flex justify-between items-center">
                    <span className="text-sm font-medium">Disponíveis</span>
                    <span className="text-lg font-bold text-green-600">
                      {data.realTimeMetrics.comandasDisponiveis} (99.9%)
                    </span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm font-medium">Ocupadas</span>
                    <span className="text-lg font-bold text-blue-600">
                      {data.realTimeMetrics.comandasOcupadas} (0.1%)
                    </span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm font-medium">Ociosas</span>
                    <span className="text-lg font-bold text-gray-600">
                      0 (0.0%)
                    </span>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Formas de Pagamento</CardTitle>
                <CardDescription>Distribuição por tipo</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <div className="flex justify-between items-center">
                    <span className="text-sm">💰 Dinheiro</span>
                    <span className="text-sm font-medium">
                      R$ {data.kpis.dinheiro.toLocaleString('pt-BR')}
                    </span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm">📱 PIX</span>
                    <span className="text-sm font-medium">
                      R$ {data.kpis.pix.toLocaleString('pt-BR')}
                    </span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm">💳 Crédito</span>
                    <span className="text-sm font-medium">
                      R$ {data.kpis.credito.toLocaleString('pt-BR')}
                    </span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm">🎟️ Voucher</span>
                    <span className="text-sm font-medium">
                      R$ {data.kpis.voucher.toLocaleString('pt-BR')}
                    </span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm">🔄 Outros</span>
                    <span className="text-sm font-medium">
                      R$ {data.kpis.outros.toLocaleString('pt-BR')}
                    </span>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Análise Pós-Pago</CardTitle>
                <CardDescription>Comandas e taxa de serviço</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div className="space-y-2">
                    <div className="flex justify-between items-center">
                      <span className="text-sm">Com taxa de serviço</span>
                      <span className="text-sm font-bold text-green-600">
                        {data.realTimeMetrics.comandasComTaxa} comandas
                      </span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm">Sem taxa de serviço</span>
                      <span className="text-sm font-medium">
                        {data.realTimeMetrics.comandasSemTaxa} comandas
                      </span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm">Fechadas manualmente</span>
                      <span className="text-sm font-medium">
                        {data.realTimeMetrics.comandasFechadasManualmente} comandas
                      </span>
                    </div>
                  </div>
                  <div className="pt-2 border-t">
                    <div className="flex justify-between items-center">
                      <span className="text-sm font-medium">Taxa Arrecadada</span>
                      <span className="text-lg font-bold text-purple-600">
                        R$ {data.kpis.taxaServico.toLocaleString('pt-BR')}
                      </span>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Saldos Financeiros */}
          <Card>
            <CardHeader>
              <CardTitle>Informações da Conta</CardTitle>
              <CardDescription>Saldos e movimentações financeiras</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid gap-4 md:grid-cols-3">
                <div className="space-y-2">
                  <p className="text-sm font-medium">Saldo Disponível</p>
                  <p className="text-2xl font-bold text-green-600">
                    R$ {data.kpis.saldoDisponivel.toFixed(2)}
                  </p>
                </div>
                <div className="space-y-2">
                  <p className="text-sm font-medium">Saldo a Liberar</p>
                  <p className="text-2xl font-bold text-blue-600">
                    R$ 0,00
                  </p>
                </div>
                <div className="space-y-2">
                  <p className="text-sm font-medium">Saldo Retido</p>
                  <p className="text-2xl font-bold text-orange-600">
                    R$ {data.kpis.saldoRetido.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="revenue" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Análise Detalhada de Receita</CardTitle>
              <CardDescription>
                Performance financeira e tendências
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={400}>
                <LineChart data={data.revenueChart}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="month" />
                  <YAxis />
                  <Tooltip 
                    formatter={(value) => [`R$ ${Number(value).toLocaleString('pt-BR')}`, 'Receita']}
                  />
                  <Line 
                    type="monotone" 
                    dataKey="revenue" 
                    stroke="#8884d8" 
                    strokeWidth={3}
                    dot={{ fill: '#8884d8', strokeWidth: 2, r: 6 }}
                  />
                </LineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="customers" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Análise de Clientes</CardTitle>
              <CardDescription>
                Comportamento e segmentação de clientes
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {data.customerSegmentation.map((segment, index) => (
                  <div key={index} className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <div 
                        className="w-4 h-4 rounded-full" 
                        style={{ backgroundColor: segment.color }}
                      />
                      <span className="font-medium">{segment.name}</span>
                    </div>
                    <div className="flex items-center space-x-4">
                      <Progress value={segment.value} className="w-32" />
                      <span className="text-sm font-medium w-12">{segment.value}%</span>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="products" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Top Produtos</CardTitle>
              <CardDescription>
                Produtos mais vendidos por receita
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {data.topProducts.map((product, index) => (
                  <div key={index} className="flex items-center justify-between p-4 border rounded-lg">
                    <div className="space-y-1">
                      <p className="font-medium">{product.name}</p>
                      <p className="text-sm text-muted-foreground">
                        {product.sales} vendas
                      </p>
                    </div>
                    <div className="text-right">
                      <p className="font-bold text-green-600">
                        R$ {product.revenue.toLocaleString('pt-BR')}
                      </p>
                      <p className="text-sm text-muted-foreground">
                        R$ {(product.revenue / product.sales).toFixed(2)} /unidade
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default DashboardAnalyticsModule;