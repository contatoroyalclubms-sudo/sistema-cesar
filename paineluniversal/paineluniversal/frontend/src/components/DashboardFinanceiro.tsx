import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  Tab,
  Tabs,
  MenuItem,
  Select,
  FormControl,
  InputLabel,
  Button,
  IconButton,
  Tooltip,
  Paper,
  CircularProgress,
  Alert,
  Chip
} from '@mui/material';
import {
  TrendingUp,
  TrendingDown,
  AttachMoney,
  ShoppingCart,
  People,
  Assessment,
  Refresh,
  Download,
  DateRange
} from '@mui/icons-material';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, Legend, ResponsiveContainer, BarChart, Bar, PieChart, Pie, Cell } from 'recharts';
import { format, startOfMonth, endOfMonth, startOfYear, endOfYear, subDays } from 'date-fns';
import { ptBR } from 'date-fns/locale';
import { DataGrid, GridColDef } from '@mui/x-data-grid';

// Interfaces para tipagem
interface KPIResumo {
  vendas_totais: number;
  ticket_medio: number;
  quantidade_vendas: number;
  produtos_vendidos: number;
  crescimento_percentual: number;
}

interface VendaPeriodo {
  periodo: string;
  vendas_brutas: number;
  vendas_liquidas: number;
  quantidade_vendas: number;
  ticket_medio: number;
  crescimento: number | null;
}

interface ProdutoPerformance {
  produto_id: number;
  nome: string;
  categoria: string | null;
  quantidade_vendida: number;
  valor_total: number;
  ticket_medio: number;
  margem_percentual: number | null;
  ranking: number;
}

interface FormaPagamento {
  forma_pagamento: string;
  valor_total: number;
  quantidade_transacoes: number;
  percentual_total: number;
  ticket_medio: number;
}

interface MetricasTempoReal {
  vendas_hoje: {
    total_vendas: number;
    valor_total: number;
    ticket_medio: number;
  };
  vendas_por_hora: Array<{
    hora: string;
    vendas: number;
    valor: number;
  }>;
  sistema_cashless: {
    cartoes_ativos: number;
    saldo_total_sistema: number;
  };
  ultima_atualizacao: string;
}

// Cores para gráficos
const CORES_GRAFICOS = [
  '#8884d8', '#82ca9d', '#ffc658', '#ff7300', '#00ff00', 
  '#ff0080', '#8800ff', '#00ffff', '#ff8000', '#8000ff'
];

// Serviço API
class DashboardFinanceiroService {
  private baseURL = '/api/v1/dashboard-financeiro';

  async obterResumo(params: any) {
    const query = new URLSearchParams(params).toString();
    const response = await fetch(`${this.baseURL}/resumo?${query}`);
    return response.json();
  }

  async obterVendasPorPeriodo(params: any) {
    const query = new URLSearchParams(params).toString();
    const response = await fetch(`${this.baseURL}/vendas-periodo?${query}`);
    return response.json();
  }

  async obterProdutosPerformance(params: any) {
    const query = new URLSearchParams(params).toString();
    const response = await fetch(`${this.baseURL}/produtos-performance?${query}`);
    return response.json();
  }

  async obterFormasPagamento(params: any) {
    const query = new URLSearchParams(params).toString();
    const response = await fetch(`${this.baseURL}/formas-pagamento?${query}`);
    return response.json();
  }

  async obterMetricasTempoReal(eventoId?: number) {
    const query = eventoId ? `?evento_id=${eventoId}` : '';
    const response = await fetch(`${this.baseURL}/metricas-tempo-real${query}`);
    return response.json();
  }
}

const dashboardService = new DashboardFinanceiroService();

// Componente principal
const DashboardFinanceiro: React.FC = () => {
  const [tabAtiva, setTabAtiva] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  // Estados dos dados
  const [resumo, setResumo] = useState<any>(null);
  const [vendasPorPeriodo, setVendasPorPeriodo] = useState<VendaPeriodo[]>([]);
  const [produtosPerformance, setProdutosPerformance] = useState<ProdutoPerformance[]>([]);
  const [formasPagamento, setFormasPagamento] = useState<FormaPagamento[]>([]);
  const [metricasTempoReal, setMetricasTempoReal] = useState<MetricasTempoReal | null>(null);
  
  // Estados dos filtros
  const [dataInicio, setDataInicio] = useState<Date>(startOfMonth(new Date()));
  const [dataFim, setDataFim] = useState<Date>(endOfMonth(new Date()));
  const [granularidade, setGranularidade] = useState('dia');
  const [eventoId, setEventoId] = useState<number | null>(null);
  const [empresaId, setEmpresaId] = useState<number | null>(null);

  // Carregar dados
  const carregarDados = async () => {
    try {
      setLoading(true);
      setError(null);

      const params = {
        data_inicio: format(dataInicio, 'yyyy-MM-dd'),
        data_fim: format(dataFim, 'yyyy-MM-dd'),
        ...(eventoId && { evento_id: eventoId }),
        ...(empresaId && { empresa_id: empresaId })
      };

      const [resumoData, vendasData, produtosData, formasData, metricasData] = await Promise.all([
        dashboardService.obterResumo(params),
        dashboardService.obterVendasPorPeriodo({ ...params, granularidade }),
        dashboardService.obterProdutosPerformance({ ...params, limite: 10 }),
        dashboardService.obterFormasPagamento(params),
        dashboardService.obterMetricasTempoReal(eventoId || undefined)
      ]);

      setResumo(resumoData);
      setVendasPorPeriodo(vendasData);
      setProdutosPerformance(produtosData);
      setFormasPagamento(formasData);
      setMetricasTempoReal(metricasData);
    } catch (err) {
      setError('Erro ao carregar dados do dashboard');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    carregarDados();
  }, [dataInicio, dataFim, granularidade, eventoId, empresaId]);

  // Componente KPI Card
  const KPICard: React.FC<{
    titulo: string;
    valor: number | string;
    icone: React.ReactNode;
    crescimento?: number;
    formato?: 'moeda' | 'numero' | 'percentual';
  }> = ({ titulo, valor, icone, crescimento, formato = 'numero' }) => {
    const formatarValor = (val: number | string) => {
      if (typeof val === 'string') return val;
      
      switch (formato) {
        case 'moeda':
          return new Intl.NumberFormat('pt-BR', { 
            style: 'currency', 
            currency: 'BRL' 
          }).format(val);
        case 'percentual':
          return `${val.toFixed(1)}%`;
        default:
          return new Intl.NumberFormat('pt-BR').format(val);
      }
    };

    return (
      <Card>
        <CardContent>
          <Box display="flex" alignItems="center" justifyContent="space-between">
            <Box>
              <Typography color="textSecondary" gutterBottom variant="body2">
                {titulo}
              </Typography>
              <Typography variant="h5" component="h2">
                {formatarValor(valor)}
              </Typography>
              {crescimento !== undefined && (
                <Box display="flex" alignItems="center" mt={1}>
                  {crescimento >= 0 ? (
                    <TrendingUp color="success" fontSize="small" />
                  ) : (
                    <TrendingDown color="error" fontSize="small" />
                  )}
                  <Typography 
                    variant="body2" 
                    color={crescimento >= 0 ? "success.main" : "error.main"}
                    ml={0.5}
                  >
                    {crescimento.toFixed(1)}%
                  </Typography>
                </Box>
              )}
            </Box>
            <Box color="primary.main">
              {icone}
            </Box>
          </Box>
        </CardContent>
      </Card>
    );
  };

  // Aba de Visão Geral
  const VisaoGeral = () => (
    <Grid container spacing={3}>
      {/* KPIs */}
      <Grid item xs={12} sm={6} md={3}>
        <KPICard
          titulo="Vendas Totais"
          valor={resumo?.kpis?.vendas_totais || 0}
          icone={<AttachMoney fontSize="large" />}
          crescimento={resumo?.kpis?.crescimento_percentual}
          formato="moeda"
        />
      </Grid>
      <Grid item xs={12} sm={6} md={3}>
        <KPICard
          titulo="Ticket Médio"
          valor={resumo?.kpis?.ticket_medio || 0}
          icone={<ShoppingCart fontSize="large" />}
          formato="moeda"
        />
      </Grid>
      <Grid item xs={12} sm={6} md={3}>
        <KPICard
          titulo="Quantidade de Vendas"
          valor={resumo?.kpis?.quantidade_vendas || 0}
          icone={<Assessment fontSize="large" />}
        />
      </Grid>
      <Grid item xs={12} sm={6} md={3}>
        <KPICard
          titulo="Produtos Vendidos"
          valor={resumo?.kpis?.produtos_vendidos || 0}
          icone={<People fontSize="large" />}
        />
      </Grid>

      {/* Gráfico de Vendas por Período */}
      <Grid item xs={12} md={8}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Vendas por Período
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={vendasPorPeriodo}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="periodo" />
                <YAxis />
                <RechartsTooltip formatter={(value: any) => [
                  new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(value),
                  'Vendas'
                ]} />
                <Legend />
                <Line 
                  type="monotone" 
                  dataKey="vendas_brutas" 
                  stroke="#8884d8" 
                  name="Vendas Brutas"
                />
                <Line 
                  type="monotone" 
                  dataKey="vendas_liquidas" 
                  stroke="#82ca9d" 
                  name="Vendas Líquidas"
                />
              </LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </Grid>

      {/* Formas de Pagamento */}
      <Grid item xs={12} md={4}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Formas de Pagamento
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={formasPagamento}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={(entry) => `${entry.forma_pagamento} (${entry.percentual_total.toFixed(1)}%)`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="valor_total"
                >
                  {formasPagamento.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={CORES_GRAFICOS[index % CORES_GRAFICOS.length]} />
                  ))}
                </Pie>
                <RechartsTooltip formatter={(value: any) => [
                  new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(value),
                  'Valor'
                ]} />
              </PieChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  );

  // Aba de Produtos
  const AnalyseProdutos = () => {
    const colunasProdutos: GridColDef[] = [
      { field: 'ranking', headerName: '#', width: 60 },
      { field: 'nome', headerName: 'Produto', width: 200, flex: 1 },
      { field: 'categoria', headerName: 'Categoria', width: 150 },
      { 
        field: 'quantidade_vendida', 
        headerName: 'Quantidade', 
        width: 120,
        type: 'number'
      },
      { 
        field: 'valor_total', 
        headerName: 'Valor Total', 
        width: 150,
        valueFormatter: (params) => 
          new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(params.value)
      },
      { 
        field: 'ticket_medio', 
        headerName: 'Ticket Médio', 
        width: 150,
        valueFormatter: (params) => 
          new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(params.value)
      },
      { 
        field: 'margem_percentual', 
        headerName: 'Margem %', 
        width: 120,
        valueFormatter: (params) => params.value ? `${params.value.toFixed(1)}%` : 'N/A'
      }
    ];

    return (
      <Box>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Performance dos Produtos
            </Typography>
            <DataGrid
              rows={produtosPerformance.map(p => ({ ...p, id: p.produto_id }))}
              columns={colunasProdutos}
              pageSize={10}
              rowsPerPageOptions={[5, 10, 25]}
              disableSelectionOnClick
              autoHeight
            />
          </CardContent>
        </Card>
      </Box>
    );
  };

  // Aba de Tempo Real
  const TempoReal = () => (
    <Grid container spacing={3}>
      {/* Métricas do Dia */}
      <Grid item xs={12} sm={4}>
        <KPICard
          titulo="Vendas Hoje"
          valor={metricasTempoReal?.vendas_hoje?.total_vendas || 0}
          icone={<ShoppingCart fontSize="large" />}
        />
      </Grid>
      <Grid item xs={12} sm={4}>
        <KPICard
          titulo="Valor Hoje"
          valor={metricasTempoReal?.vendas_hoje?.valor_total || 0}
          icone={<AttachMoney fontSize="large" />}
          formato="moeda"
        />
      </Grid>
      <Grid item xs={12} sm={4}>
        <KPICard
          titulo="Cartões Ativos"
          valor={metricasTempoReal?.sistema_cashless?.cartoes_ativos || 0}
          icone={<People fontSize="large" />}
        />
      </Grid>

      {/* Vendas por Hora */}
      <Grid item xs={12}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Vendas por Hora (Últimas 24h)
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={metricasTempoReal?.vendas_por_hora || []}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="hora" />
                <YAxis />
                <RechartsTooltip />
                <Bar dataKey="vendas" fill="#8884d8" name="Vendas" />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  );

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Alert severity="error" sx={{ m: 2 }}>
        {error}
        <Button onClick={carregarDados} sx={{ ml: 2 }}>
          Tentar Novamente
        </Button>
      </Alert>
    );
  }

  return (
    <Box sx={{ width: '100%', p: 3 }}>
      {/* Cabeçalho com Filtros */}
      <Paper sx={{ p: 2, mb: 3 }}>
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} md={2}>
            <DatePicker
              label="Data Início"
              value={dataInicio}
              onChange={(date) => date && setDataInicio(date)}
              format="dd/MM/yyyy"
              slotProps={{ textField: { size: 'small', fullWidth: true } }}
            />
          </Grid>
          <Grid item xs={12} md={2}>
            <DatePicker
              label="Data Fim"
              value={dataFim}
              onChange={(date) => date && setDataFim(date)}
              format="dd/MM/yyyy"
              slotProps={{ textField: { size: 'small', fullWidth: true } }}
            />
          </Grid>
          <Grid item xs={12} md={2}>
            <FormControl size="small" fullWidth>
              <InputLabel>Granularidade</InputLabel>
              <Select
                value={granularidade}
                onChange={(e) => setGranularidade(e.target.value)}
                label="Granularidade"
              >
                <MenuItem value="dia">Dia</MenuItem>
                <MenuItem value="semana">Semana</MenuItem>
                <MenuItem value="mes">Mês</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} md={2}>
            <Button
              variant="outlined"
              onClick={() => {
                setDataInicio(startOfMonth(new Date()));
                setDataFim(endOfMonth(new Date()));
              }}
              fullWidth
              size="small"
            >
              Este Mês
            </Button>
          </Grid>
          <Grid item xs={12} md={2}>
            <Button
              variant="outlined"
              onClick={() => {
                setDataInicio(startOfYear(new Date()));
                setDataFim(endOfYear(new Date()));
              }}
              fullWidth
              size="small"
            >
              Este Ano
            </Button>
          </Grid>
          <Grid item xs={12} md={2}>
            <Tooltip title="Atualizar dados">
              <IconButton onClick={carregarDados} color="primary">
                <Refresh />
              </IconButton>
            </Tooltip>
          </Grid>
        </Grid>
      </Paper>

      {/* Abas */}
      <Paper sx={{ width: '100%' }}>
        <Tabs
          value={tabAtiva}
          onChange={(_, newValue) => setTabAtiva(newValue)}
          aria-label="Dashboard tabs"
        >
          <Tab label="Visão Geral" />
          <Tab label="Produtos" />
          <Tab label="Tempo Real" />
        </Tabs>

        <Box sx={{ p: 3 }}>
          {tabAtiva === 0 && <VisaoGeral />}
          {tabAtiva === 1 && <AnalyseProdutos />}
          {tabAtiva === 2 && <TempoReal />}
        </Box>
      </Paper>
    </Box>
  );
};

export default DashboardFinanceiro;
