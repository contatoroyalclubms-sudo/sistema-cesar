import React, { useState, useEffect } from 'react';
import { Routes, Route, useNavigate, useLocation } from 'react-router-dom';
import { BarChart3, LineChart, PieChart, TrendingUp, TrendingDown, Download, Filter, Calendar, RefreshCw, Target, Brain } from 'lucide-react';
import DashboardBI from '../bi/DashboardBI';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { DatePickerWithRange } from '@/components/ui/date-range-picker';
import { toast } from '@/hooks/use-toast';
import api from '@/utils/api';
import { BarChart, Bar, LineChart as RechartsLineChart, Line, PieChart as RechartsPieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, AreaChart, Area } from 'recharts';
import { format } from 'date-fns';
import { ptBR } from 'date-fns/locale';

interface Dashboard {
  id: number;
  nome: string;
  descricao?: string;
  configuracao: Record<string, any>;
  widgets: Widget[];
  criado_em: string;
  atualizado_em: string;
}

interface Widget {
  id: string;
  tipo: 'grafico_barras' | 'grafico_linha' | 'grafico_pizza' | 'metrica' | 'tabela';
  titulo: string;
  configuracao: Record<string, any>;
  dados?: any[];
}

interface Relatorio {
  id: number;
  nome: string;
  tipo: 'vendas' | 'checkin' | 'financeiro' | 'promoters' | 'personalizado';
  filtros: Record<string, any>;
  agendamento?: string;
  formato_saida: 'pdf' | 'excel' | 'csv';
  ultima_execucao?: string;
  criado_em: string;
}

interface AnalisePreditiva {
  id: number;
  tipo: 'previsao_vendas' | 'tendencia_checkin' | 'analise_comportamento';
  periodo: string;
  resultado: {
    previsao: number;
    confianca: number;
    tendencia: 'alta' | 'baixa' | 'estavel';
    insights: string[];
  };
  criado_em: string;
}

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8'];

function BusinessIntelligenceMain() {
  const [dashboards, setDashboards] = useState<Dashboard[]>([]);
  const [relatorios, setRelatorios] = useState<Relatorio[]>([]);
  const [analisesPreditivas, setAnalisesPreditivas] = useState<AnalisePreditiva[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('dashboards');
  const [selectedDashboard, setSelectedDashboard] = useState<Dashboard | null>(null);
  const [showNovoRelatorio, setShowNovoRelatorio] = useState(false);
  const [dateRange, setDateRange] = useState<{from: Date | undefined, to: Date | undefined}>({
    from: undefined,
    to: undefined
  });
  const navigate = useNavigate();

  const [novoRelatorio, setNovoRelatorio] = useState({
    nome: '',
    tipo: 'vendas' as const,
    filtros: {},
    formato_saida: 'pdf' as const,
    agendamento: ''
  });

  const [metricas, setMetricas] = useState({
    vendas_total: 0,
    checkins_total: 0,
    receita_total: 0,
    taxa_conversao: 0,
    tendencia_vendas: 'estavel' as 'alta' | 'baixa' | 'estavel',
    tendencia_checkins: 'estavel' as 'alta' | 'baixa' | 'estavel'
  });

  useEffect(() => {
    carregarDados();
  }, [activeTab]);

  const carregarDados = async () => {
    setLoading(true);
    try {
      if (activeTab === 'dashboards') {
        const [dashboardsRes, metricasRes] = await Promise.all([
          api.get('/api/business-intelligence/dashboards'),
          api.get('/api/business-intelligence/metricas')
        ]);
        setDashboards(dashboardsRes.data);
        setMetricas(metricasRes.data);
        if (dashboardsRes.data.length > 0 && !selectedDashboard) {
          setSelectedDashboard(dashboardsRes.data[0]);
        }
      } else if (activeTab === 'relatorios') {
        const response = await api.get('/api/business-intelligence/relatorios');
        setRelatorios(response.data);
      } else if (activeTab === 'preditiva') {
        const response = await api.get('/api/business-intelligence/analise-preditiva');
        setAnalisesPreditivas(response.data);
      }
    } catch (error) {
      console.error('Erro ao carregar dados:', error);
      toast({
        title: "Erro",
        description: "Não foi possível carregar os dados",
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  };

  const criarRelatorio = async () => {
    try {
      await api.post('/api/business-intelligence/relatorios', novoRelatorio);
      toast({
        title: "Sucesso",
        description: "Relatório criado com sucesso"
      });
      setShowNovoRelatorio(false);
      setNovoRelatorio({
        nome: '',
        tipo: 'vendas',
        filtros: {},
        formato_saida: 'pdf',
        agendamento: ''
      });
      carregarDados();
    } catch (error) {
      console.error('Erro ao criar relatório:', error);
      toast({
        title: "Erro",
        description: "Não foi possível criar o relatório",
        variant: "destructive"
      });
    }
  };

  const executarRelatorio = async (relatorioId: number) => {
    try {
      const response = await api.post(`/api/business-intelligence/relatorios/${relatorioId}/executar`);
      const blob = new Blob([response.data]);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `relatorio_${relatorioId}_${Date.now()}.pdf`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
      
      toast({
        title: "Sucesso",
        description: "Relatório gerado e baixado com sucesso"
      });
    } catch (error) {
      console.error('Erro ao executar relatório:', error);
      toast({
        title: "Erro",
        description: "Não foi possível executar o relatório",
        variant: "destructive"
      });
    }
  };

  const executarAnalisePreditiva = async (tipo: string) => {
    try {
      await api.post('/api/business-intelligence/analise-preditiva', { tipo });
      toast({
        title: "Sucesso",
        description: "Análise preditiva iniciada. Os resultados estarão disponíveis em breve."
      });
      setTimeout(carregarDados, 3000);
    } catch (error) {
      console.error('Erro ao executar análise preditiva:', error);
      toast({
        title: "Erro",
        description: "Não foi possível executar a análise preditiva",
        variant: "destructive"
      });
    }
  };

  const renderWidget = (widget: Widget) => {
    switch (widget.tipo) {
      case 'metrica':
        return (
          <Card key={widget.id}>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium">{widget.titulo}</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{widget.configuracao.valor || 0}</div>
              {widget.configuracao.variacao && (
                <p className={`text-xs flex items-center gap-1 mt-2 ${widget.configuracao.variacao > 0 ? 'text-green-600' : 'text-red-600'}`}>
                  {widget.configuracao.variacao > 0 ? <TrendingUp className="h-3 w-3" /> : <TrendingDown className="h-3 w-3" />}
                  <span>{Math.abs(widget.configuracao.variacao)}%</span>
                </p>
              )}
            </CardContent>
          </Card>
        );

      case 'grafico_linha':
        return (
          <Card key={widget.id} className="col-span-2">
            <CardHeader>
              <CardTitle>{widget.titulo}</CardTitle>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <RechartsLineChart data={widget.dados || []}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Line type="monotone" dataKey="value" stroke="#8884d8" />
                </RechartsLineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        );

      case 'grafico_barras':
        return (
          <Card key={widget.id} className="col-span-2">
            <CardHeader>
              <CardTitle>{widget.titulo}</CardTitle>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={widget.dados || []}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="value" fill="#8884d8" />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        );

      case 'grafico_pizza':
        return (
          <Card key={widget.id}>
            <CardHeader>
              <CardTitle>{widget.titulo}</CardTitle>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={250}>
                <RechartsPieChart>
                  <Pie
                    data={widget.dados || []}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {(widget.dados || []).map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                </RechartsPieChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        );

      default:
        return null;
    }
  };

  return (
    <div className="container mx-auto py-6 space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">Business Intelligence</h1>
          <p className="text-muted-foreground">Análises, dashboards e insights do seu negócio</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={() => navigate('/app/bi/dashboard')}>
            <BarChart3 className="mr-2 h-4 w-4" />
            Dashboard Avançado
          </Button>
          <Button variant="outline" onClick={() => carregarDados()}>
            <RefreshCw className="mr-2 h-4 w-4" />
            Atualizar
          </Button>
          <DatePickerWithRange date={dateRange} onDateChange={setDateRange} />
        </div>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium">Vendas Totais</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">R$ {metricas.vendas_total.toLocaleString('pt-BR')}</div>
            <p className={`text-xs flex items-center gap-1 mt-2 ${metricas.tendencia_vendas === 'alta' ? 'text-green-600' : metricas.tendencia_vendas === 'baixa' ? 'text-red-600' : 'text-gray-600'}`}>
              {metricas.tendencia_vendas === 'alta' ? <TrendingUp className="h-3 w-3" /> : metricas.tendencia_vendas === 'baixa' ? <TrendingDown className="h-3 w-3" /> : <span className="h-3 w-3">→</span>}
              <span>Tendência {metricas.tendencia_vendas}</span>
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium">Check-ins</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{metricas.checkins_total.toLocaleString('pt-BR')}</div>
            <p className={`text-xs flex items-center gap-1 mt-2 ${metricas.tendencia_checkins === 'alta' ? 'text-green-600' : metricas.tendencia_checkins === 'baixa' ? 'text-red-600' : 'text-gray-600'}`}>
              {metricas.tendencia_checkins === 'alta' ? <TrendingUp className="h-3 w-3" /> : metricas.tendencia_checkins === 'baixa' ? <TrendingDown className="h-3 w-3" /> : <span className="h-3 w-3">→</span>}
              <span>Tendência {metricas.tendencia_checkins}</span>
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium">Receita Total</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">R$ {metricas.receita_total.toLocaleString('pt-BR')}</div>
            <p className="text-xs text-muted-foreground mt-2">Últimos 30 dias</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium">Taxa de Conversão</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{metricas.taxa_conversao}%</div>
            <p className="text-xs text-muted-foreground mt-2">Visitantes → Clientes</p>
          </CardContent>
        </Card>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="dashboards">Dashboards</TabsTrigger>
          <TabsTrigger value="relatorios">Relatórios</TabsTrigger>
          <TabsTrigger value="preditiva">Análise Preditiva</TabsTrigger>
        </TabsList>

        <TabsContent value="dashboards" className="space-y-4">
          <div className="flex gap-4">
            <Select 
              value={selectedDashboard?.id.toString()} 
              onValueChange={(value) => setSelectedDashboard(dashboards.find(d => d.id === parseInt(value)) || null)}
            >
              <SelectTrigger className="w-[250px]">
                <SelectValue placeholder="Selecione um dashboard" />
              </SelectTrigger>
              <SelectContent>
                {dashboards.map(dashboard => (
                  <SelectItem key={dashboard.id} value={dashboard.id.toString()}>
                    {dashboard.nome}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            <Button variant="outline">
              <Filter className="mr-2 h-4 w-4" />
              Filtros
            </Button>
            <Button variant="outline">
              <Download className="mr-2 h-4 w-4" />
              Exportar
            </Button>
          </div>

          {selectedDashboard && (
            <div>
              <h2 className="text-xl font-semibold mb-2">{selectedDashboard.nome}</h2>
              {selectedDashboard.descricao && (
                <p className="text-muted-foreground mb-4">{selectedDashboard.descricao}</p>
              )}
              <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                {selectedDashboard.widgets.map(widget => renderWidget(widget))}
              </div>
            </div>
          )}
        </TabsContent>

        <TabsContent value="relatorios" className="space-y-4">
          <div className="flex justify-between items-center">
            <h2 className="text-xl font-semibold">Relatórios Configurados</h2>
            <Dialog open={showNovoRelatorio} onOpenChange={setShowNovoRelatorio}>
              <DialogTrigger asChild>
                <Button>
                  <BarChart3 className="mr-2 h-4 w-4" />
                  Novo Relatório
                </Button>
              </DialogTrigger>
              <DialogContent className="sm:max-w-[500px]">
                <DialogHeader>
                  <DialogTitle>Criar Relatório</DialogTitle>
                  <DialogDescription>
                    Configure um novo relatório automatizado
                  </DialogDescription>
                </DialogHeader>
                <div className="grid gap-4 py-4">
                  <div className="grid gap-2">
                    <Label htmlFor="nome">Nome</Label>
                    <Input
                      id="nome"
                      value={novoRelatorio.nome}
                      onChange={(e) => setNovoRelatorio({...novoRelatorio, nome: e.target.value})}
                      placeholder="Ex: Relatório Mensal de Vendas"
                    />
                  </div>
                  <div className="grid gap-2">
                    <Label htmlFor="tipo">Tipo</Label>
                    <Select
                      value={novoRelatorio.tipo}
                      onValueChange={(value: any) => setNovoRelatorio({...novoRelatorio, tipo: value})}
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="vendas">Vendas</SelectItem>
                        <SelectItem value="checkin">Check-in</SelectItem>
                        <SelectItem value="financeiro">Financeiro</SelectItem>
                        <SelectItem value="promoters">Promoters</SelectItem>
                        <SelectItem value="personalizado">Personalizado</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="grid gap-2">
                    <Label htmlFor="formato">Formato de Saída</Label>
                    <Select
                      value={novoRelatorio.formato_saida}
                      onValueChange={(value: any) => setNovoRelatorio({...novoRelatorio, formato_saida: value})}
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="pdf">PDF</SelectItem>
                        <SelectItem value="excel">Excel</SelectItem>
                        <SelectItem value="csv">CSV</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="grid gap-2">
                    <Label htmlFor="agendamento">Agendamento (opcional)</Label>
                    <Input
                      id="agendamento"
                      value={novoRelatorio.agendamento}
                      onChange={(e) => setNovoRelatorio({...novoRelatorio, agendamento: e.target.value})}
                      placeholder="Ex: 0 9 * * 1 (toda segunda às 9h)"
                    />
                  </div>
                </div>
                <DialogFooter>
                  <Button variant="outline" onClick={() => setShowNovoRelatorio(false)}>
                    Cancelar
                  </Button>
                  <Button onClick={criarRelatorio}>Criar Relatório</Button>
                </DialogFooter>
              </DialogContent>
            </Dialog>
          </div>

          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {relatorios.map(relatorio => (
              <Card key={relatorio.id}>
                <CardHeader>
                  <CardTitle className="text-lg">{relatorio.nome}</CardTitle>
                  <CardDescription>
                    <Badge variant="outline">{relatorio.tipo}</Badge>
                    <Badge variant="secondary" className="ml-2">{relatorio.formato_saida.toUpperCase()}</Badge>
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  {relatorio.agendamento && (
                    <div className="flex items-center gap-2 text-sm text-muted-foreground mb-2">
                      <Calendar className="h-3 w-3" />
                      <span>Agendado</span>
                    </div>
                  )}
                  {relatorio.ultima_execucao && (
                    <div className="text-sm text-muted-foreground">
                      Última execução: {format(new Date(relatorio.ultima_execucao), "dd 'de' MMMM 'às' HH:mm", { locale: ptBR })}
                    </div>
                  )}
                </CardContent>
                <CardFooter>
                  <Button
                    variant="outline"
                    size="sm"
                    className="w-full"
                    onClick={() => executarRelatorio(relatorio.id)}
                  >
                    <Download className="mr-2 h-4 w-4" />
                    Gerar Agora
                  </Button>
                </CardFooter>
              </Card>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="preditiva" className="space-y-4">
          <div className="flex justify-between items-center">
            <h2 className="text-xl font-semibold">Análise Preditiva com IA</h2>
            <div className="flex gap-2">
              <Button 
                variant="outline"
                onClick={() => executarAnalisePreditiva('previsao_vendas')}
              >
                <Brain className="mr-2 h-4 w-4" />
                Nova Previsão
              </Button>
            </div>
          </div>

          <div className="grid gap-4">
            <Card>
              <CardHeader>
                <CardTitle>Previsões Disponíveis</CardTitle>
                <CardDescription>
                  Análises baseadas em machine learning e dados históricos
                </CardDescription>
              </CardHeader>
              <CardContent className="grid gap-4 md:grid-cols-3">
                <Button
                  variant="outline"
                  className="h-24 flex-col"
                  onClick={() => executarAnalisePreditiva('previsao_vendas')}
                >
                  <TrendingUp className="h-8 w-8 mb-2" />
                  <span>Previsão de Vendas</span>
                </Button>
                <Button
                  variant="outline"
                  className="h-24 flex-col"
                  onClick={() => executarAnalisePreditiva('tendencia_checkin')}
                >
                  <Target className="h-8 w-8 mb-2" />
                  <span>Tendência de Check-ins</span>
                </Button>
                <Button
                  variant="outline"
                  className="h-24 flex-col"
                  onClick={() => executarAnalisePreditiva('analise_comportamento')}
                >
                  <Brain className="h-8 w-8 mb-2" />
                  <span>Análise de Comportamento</span>
                </Button>
              </CardContent>
            </Card>

            {analisesPreditivas.length > 0 && (
              <Card>
                <CardHeader>
                  <CardTitle>Resultados das Análises</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  {analisesPreditivas.map(analise => (
                    <div key={analise.id} className="border rounded-lg p-4">
                      <div className="flex justify-between items-start mb-2">
                        <div>
                          <h3 className="font-semibold">{analise.tipo.replace(/_/g, ' ').toUpperCase()}</h3>
                          <p className="text-sm text-muted-foreground">
                            {format(new Date(analise.criado_em), "dd 'de' MMMM 'às' HH:mm", { locale: ptBR })}
                          </p>
                        </div>
                        <Badge variant={
                          analise.resultado.tendencia === 'alta' ? 'default' :
                          analise.resultado.tendencia === 'baixa' ? 'destructive' :
                          'secondary'
                        }>
                          {analise.resultado.tendencia}
                        </Badge>
                      </div>
                      <div className="grid gap-2">
                        <div className="flex justify-between">
                          <span className="text-sm font-medium">Previsão:</span>
                          <span className="text-sm">{analise.resultado.previsao}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-sm font-medium">Confiança:</span>
                          <span className="text-sm">{analise.resultado.confianca}%</span>
                        </div>
                      </div>
                      {analise.resultado.insights.length > 0 && (
                        <div className="mt-3 pt-3 border-t">
                          <p className="text-sm font-medium mb-1">Insights:</p>
                          <ul className="text-sm text-muted-foreground space-y-1">
                            {analise.resultado.insights.map((insight, idx) => (
                              <li key={idx}>• {insight}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>
                  ))}
                </CardContent>
              </Card>
            )}
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}

export default function BusinessIntelligenceModule() {
  return (
    <Routes>
      <Route path="/" element={<BusinessIntelligenceMain />} />
      <Route path="/dashboard" element={<DashboardBI />} />
    </Routes>
  );
}