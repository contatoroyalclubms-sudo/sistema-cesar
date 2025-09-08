import React, { useState, useEffect, useCallback } from 'react';
import {
  Box,
  Paper,
  Typography,
  Grid,
  Card,
  CardContent,
  Button,
  Fab,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  MenuItem,
  Chip,
  Alert,
  Tabs,
  Tab,
  IconButton,
  Tooltip,
  CircularProgress,
  LinearProgress,
  Badge,
  Divider,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  ListItemSecondaryAction,
  Switch,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Select,
  FormControl,
  InputLabel,
  FormControlLabel,
  Checkbox,
  SpeedDial,
  SpeedDialAction,
  SpeedDialIcon
} from '@mui/material';
import {
  Add as AddIcon,
  PlayArrow as PlayIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Dashboard as DashboardIcon,
  BarChart as ChartIcon,
  TableChart as TableIcon,
  Assessment as ReportIcon,
  Download as DownloadIcon,
  Refresh as RefreshIcon,
  Schedule as ScheduleIcon,
  Share as ShareIcon,
  Visibility as ViewIcon,
  Settings as SettingsIcon,
  ExpandMore as ExpandMoreIcon,
  TrendingUp as TrendingUpIcon,
  FilterList as FilterIcon,
  Search as SearchIcon,
  Info as InfoIcon,
  Warning as WarningIcon,
  CheckCircle as CheckIcon,
  Error as ErrorIcon,
  Speed as SpeedIcon,
  Analytics as AnalyticsIcon,
  Widgets as WidgetIcon,
  Timeline as TimelineIcon,
  PieChart as PieChartIcon,
  ShowChart as LineChartIcon,
  DonutLarge as DonutIcon
} from '@mui/icons-material';
import { useSnackbar } from 'notistack';
import { format, parseISO, subDays } from 'date-fns';
import { ptBR } from 'date-fns/locale';

import {
  relatoriosService,
  ConfiguracaoRelatorio,
  ExecucaoRelatorio,
  DashboardExecutivo,
  WidgetDashboard,
  MetricaNegocio,
  DashboardRelatorios,
  TipoRelatorio,
  StatusRelatorio,
  StatusExecucao,
  TipoVisualizacao,
  TipoWidget,
  FormatoExportacao,
  NivelPermissao,
  CreateRelatorioRequest,
  ExecutarRelatorioRequest
} from '../services/relatoriosService';

// === INTERFACES LOCAIS ===

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`relatorios-tabpanel-${index}`}
      aria-labelledby={`relatorios-tab-${index}`}
      {...other}
    >
      {value === index && (
        <Box sx={{ p: 3 }}>
          {children}
        </Box>
      )}
    </div>
  );
}

// === COMPONENTE PRINCIPAL ===

const RelatoriosModule: React.FC = () => {
  const [activeTab, setActiveTab] = useState(0);
  const [loading, setLoading] = useState(false);
  const [dashboardData, setDashboardData] = useState<DashboardRelatorios | null>(null);
  
  // Estados dos relatórios
  const [configuracoes, setConfiguracoes] = useState<ConfiguracaoRelatorio[]>([]);
  const [execucoes, setExecucoes] = useState<ExecucaoRelatorio[]>([]);
  const [dashboards, setDashboards] = useState<DashboardExecutivo[]>([]);
  const [metricas, setMetricas] = useState<MetricaNegocio[]>([]);
  
  // Estados dos diálogos
  const [openCreateReport, setOpenCreateReport] = useState(false);
  const [openCreateDashboard, setOpenCreateDashboard] = useState(false);
  const [openCreateMetric, setOpenCreateMetric] = useState(false);
  const [openExecuteReport, setOpenExecuteReport] = useState(false);
  const [selectedReport, setSelectedReport] = useState<ConfiguracaoRelatorio | null>(null);
  
  // Estados de filtros
  const [filtroTipo, setFiltroTipo] = useState<TipoRelatorio | ''>('');
  const [filtroStatus, setFiltroStatus] = useState<StatusRelatorio | ''>('');
  const [filtroCategoria, setFiltroCategoria] = useState('');
  const [filtroBusca, setFiltroBusca] = useState('');
  
  // Estados de formulários
  const [formRelatorio, setFormRelatorio] = useState<CreateRelatorioRequest>({
    nome: '',
    descricao: '',
    tipo: TipoRelatorio.TABULAR,
    categoria: '',
    query_sql: '',
    configuracao_visual: {},
    filtros_disponiveis: [],
    parametros_padrao: {},
    cache_duracao: 300,
    timeout_execucao: 60,
    limite_registros: 10000,
    tags: [],
    nivel_permissao: NivelPermissao.EMPRESA,
    publico: false
  });
  
  const [parametrosExecucao, setParametrosExecucao] = useState<ExecutarRelatorioRequest>({
    parametros: {},
    filtros: {},
    formato_exportacao: FormatoExportacao.PDF,
    usar_cache: true
  });

  const { enqueueSnackbar } = useSnackbar();

  // === CARREGAMENTO INICIAL ===

  useEffect(() => {
    carregarDadosIniciais();
  }, []);

  const carregarDadosIniciais = async () => {
    setLoading(true);
    try {
      const [dashboardResp, configResp, dashboardsResp, metricasResp] = await Promise.all([
        relatoriosService.obterDashboardPrincipal(),
        relatoriosService.listarConfiguracoes(),
        relatoriosService.listarDashboards(),
        relatoriosService.listarMetricas()
      ]);

      setDashboardData(dashboardResp);
      setConfiguracoes(configResp);
      setDashboards(dashboardsResp);
      setMetricas(metricasResp);
    } catch (error: any) {
      enqueueSnackbar('Erro ao carregar dados dos relatórios', { variant: 'error' });
      console.error('Erro:', error);
    } finally {
      setLoading(false);
    }
  };

  // === FUNÇÕES DOS RELATÓRIOS ===

  const criarRelatorio = async () => {
    if (!formRelatorio.nome || !formRelatorio.query_sql) {
      enqueueSnackbar('Nome e query SQL são obrigatórios', { variant: 'warning' });
      return;
    }

    // Validar SQL
    const validacao = relatoriosService.validarQuery(formRelatorio.query_sql);
    if (!validacao.valida) {
      enqueueSnackbar(`Erro na query: ${validacao.erros.join(', ')}`, { variant: 'error' });
      return;
    }

    try {
      setLoading(true);
      await relatoriosService.criarConfiguracao(formRelatorio);
      
      enqueueSnackbar('Relatório criado com sucesso', { variant: 'success' });
      setOpenCreateReport(false);
      resetFormRelatorio();
      await carregarConfiguracoes();
    } catch (error: any) {
      enqueueSnackbar('Erro ao criar relatório', { variant: 'error' });
      console.error('Erro:', error);
    } finally {
      setLoading(false);
    }
  };

  const executarRelatorio = async () => {
    if (!selectedReport) return;

    try {
      setLoading(true);
      const resultado = await relatoriosService.executarRelatorio(
        selectedReport.id,
        parametrosExecucao
      );

      if (resultado.cache_hit) {
        enqueueSnackbar('Resultado obtido do cache', { variant: 'info' });
      } else {
        enqueueSnackbar('Relatório executado com sucesso', { variant: 'success' });
      }

      setOpenExecuteReport(false);
      await carregarExecucoes();
    } catch (error: any) {
      enqueueSnackbar('Erro ao executar relatório', { variant: 'error' });
      console.error('Erro:', error);
    } finally {
      setLoading(false);
    }
  };

  const carregarConfiguracoes = async () => {
    try {
      const configs = await relatoriosService.listarConfiguracoes({
        tipo: filtroTipo || undefined,
        status: filtroStatus || undefined,
        categoria: filtroCategoria || undefined
      });
      setConfiguracoes(configs);
    } catch (error) {
      enqueueSnackbar('Erro ao carregar configurações', { variant: 'error' });
    }
  };

  const carregarExecucoes = async () => {
    try {
      const execs = await relatoriosService.listarExecucoes();
      setExecucoes(execs);
    } catch (error) {
      enqueueSnackbar('Erro ao carregar execuções', { variant: 'error' });
    }
  };

  const inicializarTemplates = async () => {
    try {
      setLoading(true);
      const resultado = await relatoriosService.inicializarTemplates();
      enqueueSnackbar(resultado.message, { variant: 'success' });
      await carregarConfiguracoes();
    } catch (error) {
      enqueueSnackbar('Erro ao inicializar templates', { variant: 'error' });
    } finally {
      setLoading(false);
    }
  };

  const inicializarKpis = async () => {
    try {
      setLoading(true);
      const resultado = await relatoriosService.inicializarKpis();
      enqueueSnackbar(resultado.message, { variant: 'success' });
      await carregarMetricas();
    } catch (error) {
      enqueueSnackbar('Erro ao inicializar KPIs', { variant: 'error' });
    } finally {
      setLoading(false);
    }
  };

  const carregarMetricas = async () => {
    try {
      const metrics = await relatoriosService.listarMetricas();
      setMetricas(metrics);
    } catch (error) {
      enqueueSnackbar('Erro ao carregar métricas', { variant: 'error' });
    }
  };

  // === FUNÇÕES AUXILIARES ===

  const resetFormRelatorio = () => {
    setFormRelatorio({
      nome: '',
      descricao: '',
      tipo: TipoRelatorio.TABULAR,
      categoria: '',
      query_sql: '',
      configuracao_visual: {},
      filtros_disponiveis: [],
      parametros_padrao: {},
      cache_duracao: 300,
      timeout_execucao: 60,
      limite_registros: 10000,
      tags: [],
      nivel_permissao: NivelPermissao.EMPRESA,
      publico: false
    });
  };

  const getStatusColor = (status: StatusRelatorio | StatusExecucao) => {
    switch (status) {
      case StatusRelatorio.ATIVO:
      case StatusExecucao.CONCLUIDO:
        return 'success';
      case StatusRelatorio.INATIVO:
      case StatusExecucao.CANCELADO:
        return 'default';
      case StatusRelatorio.RASCUNHO:
      case StatusExecucao.PENDENTE:
        return 'warning';
      case StatusExecucao.EXECUTANDO:
        return 'info';
      case StatusExecucao.ERRO:
        return 'error';
      default:
        return 'default';
    }
  };

  const getTipoIcon = (tipo: TipoRelatorio) => {
    switch (tipo) {
      case TipoRelatorio.TABULAR:
        return <TableIcon />;
      case TipoRelatorio.GRAFICO:
        return <ChartIcon />;
      case TipoRelatorio.KPI:
        return <SpeedIcon />;
      case TipoRelatorio.DASHBOARD:
        return <DashboardIcon />;
      case TipoRelatorio.EXPORTACAO:
        return <DownloadIcon />;
      default:
        return <ReportIcon />;
    }
  };

  const filtrarConfiguracoes = useCallback(() => {
    return configuracoes.filter(config => {
      const matchBusca = !filtroBusca || 
        config.nome.toLowerCase().includes(filtroBusca.toLowerCase()) ||
        (config.descricao && config.descricao.toLowerCase().includes(filtroBusca.toLowerCase()));
      
      return matchBusca;
    });
  }, [configuracoes, filtroBusca]);

  // === RENDER DO DASHBOARD PRINCIPAL ===

  const renderDashboardPrincipal = () => (
    <Grid container spacing={3}>
      {/* Cards de estatísticas */}
      <Grid item xs={12} sm={6} md={3}>
        <Card>
          <CardContent>
            <Box display="flex" alignItems="center">
              <ReportIcon color="primary" sx={{ mr: 2 }} />
              <Box>
                <Typography variant="h4" component="div">
                  {dashboardData?.total_relatorios || 0}
                </Typography>
                <Typography color="text.secondary" gutterBottom>
                  Total de Relatórios
                </Typography>
              </Box>
            </Box>
          </CardContent>
        </Card>
      </Grid>

      <Grid item xs={12} sm={6} md={3}>
        <Card>
          <CardContent>
            <Box display="flex" alignItems="center">
              <CheckIcon color="success" sx={{ mr: 2 }} />
              <Box>
                <Typography variant="h4" component="div">
                  {dashboardData?.relatorios_ativos || 0}
                </Typography>
                <Typography color="text.secondary" gutterBottom>
                  Relatórios Ativos
                </Typography>
              </Box>
            </Box>
          </CardContent>
        </Card>
      </Grid>

      <Grid item xs={12} sm={6} md={3}>
        <Card>
          <CardContent>
            <Box display="flex" alignItems="center">
              <PlayIcon color="info" sx={{ mr: 2 }} />
              <Box>
                <Typography variant="h4" component="div">
                  {dashboardData?.execucoes_hoje || 0}
                </Typography>
                <Typography color="text.secondary" gutterBottom>
                  Execuções Hoje
                </Typography>
              </Box>
            </Box>
          </CardContent>
        </Card>
      </Grid>

      <Grid item xs={12} sm={6} md={3}>
        <Card>
          <CardContent>
            <Box display="flex" alignItems="center">
              <TimelineIcon color="warning" sx={{ mr: 2 }} />
              <Box>
                <Typography variant="h4" component="div">
                  {dashboardData?.tempo_medio_execucao?.toFixed(2) || '0.00'}s
                </Typography>
                <Typography color="text.secondary" gutterBottom>
                  Tempo Médio
                </Typography>
              </Box>
            </Box>
          </CardContent>
        </Card>
      </Grid>

      {/* Relatórios mais usados */}
      <Grid item xs={12} md={6}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Relatórios Mais Usados
            </Typography>
            <List>
              {dashboardData?.relatorios_mais_usados?.map((relatorio, index) => (
                <ListItem key={index}>
                  <ListItemIcon>
                    <TrendingUpIcon color="primary" />
                  </ListItemIcon>
                  <ListItemText
                    primary={relatorio.nome}
                    secondary={`${relatorio.execucoes} execuções`}
                  />
                </ListItem>
              ))}
            </List>
          </CardContent>
        </Card>
      </Grid>

      {/* Atividade recente */}
      <Grid item xs={12} md={6}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Atividade Recente
            </Typography>
            <List>
              {dashboardData?.atividade_recente?.map((atividade, index) => (
                <ListItem key={index}>
                  <ListItemIcon>
                    <InfoIcon />
                  </ListItemIcon>
                  <ListItemText
                    primary={atividade.relatorio}
                    secondary={
                      <Box>
                        <Typography variant="body2">
                          {atividade.usuario} - {atividade.status}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          {format(parseISO(atividade.timestamp), 'dd/MM/yyyy HH:mm', { locale: ptBR })}
                        </Typography>
                      </Box>
                    }
                  />
                  <ListItemSecondaryAction>
                    <Chip
                      size="small"
                      label={atividade.status}
                      color={getStatusColor(atividade.status as StatusExecucao) as any}
                    />
                  </ListItemSecondaryAction>
                </ListItem>
              ))}
            </List>
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  );

  // === RENDER DA LISTA DE RELATÓRIOS ===

  const renderListaRelatorios = () => (
    <Box>
      {/* Filtros */}
      <Paper sx={{ p: 2, mb: 3 }}>
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} sm={6} md={3}>
            <TextField
              fullWidth
              label="Buscar"
              value={filtroBusca}
              onChange={(e) => setFiltroBusca(e.target.value)}
              InputProps={{
                startAdornment: <SearchIcon color="action" sx={{ mr: 1 }} />
              }}
            />
          </Grid>
          
          <Grid item xs={12} sm={6} md={2}>
            <FormControl fullWidth>
              <InputLabel>Tipo</InputLabel>
              <Select
                value={filtroTipo}
                onChange={(e) => setFiltroTipo(e.target.value as TipoRelatorio)}
                label="Tipo"
              >
                <MenuItem value="">Todos</MenuItem>
                {Object.values(TipoRelatorio).map(tipo => (
                  <MenuItem key={tipo} value={tipo}>{tipo}</MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>

          <Grid item xs={12} sm={6} md={2}>
            <FormControl fullWidth>
              <InputLabel>Status</InputLabel>
              <Select
                value={filtroStatus}
                onChange={(e) => setFiltroStatus(e.target.value as StatusRelatorio)}
                label="Status"
              >
                <MenuItem value="">Todos</MenuItem>
                {Object.values(StatusRelatorio).map(status => (
                  <MenuItem key={status} value={status}>{status}</MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>

          <Grid item xs={12} sm={6} md={2}>
            <TextField
              fullWidth
              label="Categoria"
              value={filtroCategoria}
              onChange={(e) => setFiltroCategoria(e.target.value)}
            />
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Box display="flex" gap={1}>
              <Button
                variant="outlined"
                onClick={() => {
                  setFiltroTipo('');
                  setFiltroStatus('');
                  setFiltroCategoria('');
                  setFiltroBusca('');
                }}
              >
                Limpar
              </Button>
              <Button
                variant="contained"
                onClick={carregarConfiguracoes}
                startIcon={<RefreshIcon />}
              >
                Atualizar
              </Button>
            </Box>
          </Grid>
        </Grid>
      </Paper>

      {/* Lista de relatórios */}
      <Grid container spacing={2}>
        {filtrarConfiguracoes().map((config) => (
          <Grid item xs={12} md={6} lg={4} key={config.id}>
            <Card>
              <CardContent>
                <Box display="flex" alignItems="center" mb={2}>
                  {getTipoIcon(config.tipo)}
                  <Typography variant="h6" sx={{ ml: 1, flexGrow: 1 }}>
                    {config.nome}
                  </Typography>
                  <Chip
                    size="small"
                    label={config.status}
                    color={getStatusColor(config.status) as any}
                  />
                </Box>

                {config.descricao && (
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    {config.descricao}
                  </Typography>
                )}

                <Box display="flex" flexWrap="wrap" gap={0.5} mb={2}>
                  <Chip size="small" label={config.tipo} variant="outlined" />
                  {config.categoria && (
                    <Chip size="small" label={config.categoria} variant="outlined" />
                  )}
                  {config.publico && (
                    <Chip size="small" label="Público" color="info" />
                  )}
                </Box>

                <Typography variant="caption" color="text.secondary" display="block">
                  {config.total_execucoes} execuções • 
                  Média: {config.tempo_medio_execucao?.toFixed(2)}s
                </Typography>

                {config.ultima_execucao && (
                  <Typography variant="caption" color="text.secondary" display="block">
                    Última execução: {format(parseISO(config.ultima_execucao), 'dd/MM/yyyy HH:mm', { locale: ptBR })}
                  </Typography>
                )}

                <Box display="flex" justifyContent="space-between" mt={2}>
                  <Button
                    size="small"
                    startIcon={<PlayIcon />}
                    onClick={() => {
                      setSelectedReport(config);
                      setOpenExecuteReport(true);
                    }}
                    disabled={config.status !== StatusRelatorio.ATIVO}
                  >
                    Executar
                  </Button>
                  
                  <Box>
                    <IconButton size="small">
                      <ViewIcon />
                    </IconButton>
                    <IconButton size="small">
                      <EditIcon />
                    </IconButton>
                    <IconButton size="small">
                      <ShareIcon />
                    </IconButton>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      {filtrarConfiguracoes().length === 0 && (
        <Paper sx={{ p: 4, textAlign: 'center' }}>
          <ReportIcon sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
          <Typography variant="h6" color="text.secondary" gutterBottom>
            Nenhum relatório encontrado
          </Typography>
          <Typography variant="body2" color="text.secondary" mb={3}>
            Crie seu primeiro relatório ou ajuste os filtros de busca
          </Typography>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => setOpenCreateReport(true)}
          >
            Criar Relatório
          </Button>
        </Paper>
      )}
    </Box>
  );

  // === DIÁLOGO DE CRIAÇÃO DE RELATÓRIO ===

  const renderDialogCreateReport = () => (
    <Dialog
      open={openCreateReport}
      onClose={() => setOpenCreateReport(false)}
      maxWidth="md"
      fullWidth
    >
      <DialogTitle>Criar Novo Relatório</DialogTitle>
      <DialogContent>
        <Grid container spacing={2} sx={{ mt: 1 }}>
          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              label="Nome"
              required
              value={formRelatorio.nome}
              onChange={(e) => setFormRelatorio({ ...formRelatorio, nome: e.target.value })}
            />
          </Grid>

          <Grid item xs={12} sm={6}>
            <FormControl fullWidth required>
              <InputLabel>Tipo</InputLabel>
              <Select
                value={formRelatorio.tipo}
                onChange={(e) => setFormRelatorio({ ...formRelatorio, tipo: e.target.value as TipoRelatorio })}
                label="Tipo"
              >
                {Object.values(TipoRelatorio).map(tipo => (
                  <MenuItem key={tipo} value={tipo}>{tipo}</MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>

          <Grid item xs={12}>
            <TextField
              fullWidth
              label="Descrição"
              multiline
              rows={2}
              value={formRelatorio.descricao}
              onChange={(e) => setFormRelatorio({ ...formRelatorio, descricao: e.target.value })}
            />
          </Grid>

          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              label="Categoria"
              value={formRelatorio.categoria}
              onChange={(e) => setFormRelatorio({ ...formRelatorio, categoria: e.target.value })}
            />
          </Grid>

          <Grid item xs={12} sm={6}>
            <FormControl fullWidth>
              <InputLabel>Nível de Permissão</InputLabel>
              <Select
                value={formRelatorio.nivel_permissao}
                onChange={(e) => setFormRelatorio({ ...formRelatorio, nivel_permissao: e.target.value as NivelPermissao })}
                label="Nível de Permissão"
              >
                {Object.values(NivelPermissao).map(nivel => (
                  <MenuItem key={nivel} value={nivel}>{nivel}</MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>

          <Grid item xs={12}>
            <TextField
              fullWidth
              label="Query SQL"
              required
              multiline
              rows={6}
              value={formRelatorio.query_sql}
              onChange={(e) => setFormRelatorio({ ...formRelatorio, query_sql: e.target.value })}
              placeholder="SELECT * FROM tabela WHERE..."
              helperText="Digite a query SQL para o relatório. Apenas comandos SELECT são permitidos."
            />
          </Grid>

          <Grid item xs={12} sm={4}>
            <TextField
              fullWidth
              label="Cache (segundos)"
              type="number"
              value={formRelatorio.cache_duracao}
              onChange={(e) => setFormRelatorio({ ...formRelatorio, cache_duracao: parseInt(e.target.value) || 0 })}
            />
          </Grid>

          <Grid item xs={12} sm={4}>
            <TextField
              fullWidth
              label="Timeout (segundos)"
              type="number"
              value={formRelatorio.timeout_execucao}
              onChange={(e) => setFormRelatorio({ ...formRelatorio, timeout_execucao: parseInt(e.target.value) || 60 })}
            />
          </Grid>

          <Grid item xs={12} sm={4}>
            <TextField
              fullWidth
              label="Limite de Registros"
              type="number"
              value={formRelatorio.limite_registros}
              onChange={(e) => setFormRelatorio({ ...formRelatorio, limite_registros: parseInt(e.target.value) || 10000 })}
            />
          </Grid>

          <Grid item xs={12}>
            <FormControlLabel
              control={
                <Checkbox
                  checked={formRelatorio.publico}
                  onChange={(e) => setFormRelatorio({ ...formRelatorio, publico: e.target.checked })}
                />
              }
              label="Tornar público (visível para outras empresas)"
            />
          </Grid>
        </Grid>
      </DialogContent>
      <DialogActions>
        <Button onClick={() => setOpenCreateReport(false)}>
          Cancelar
        </Button>
        <Button
          onClick={criarRelatorio}
          variant="contained"
          disabled={loading}
        >
          {loading ? <CircularProgress size={24} /> : 'Criar'}
        </Button>
      </DialogActions>
    </Dialog>
  );

  // === DIÁLOGO DE EXECUÇÃO ===

  const renderDialogExecuteReport = () => (
    <Dialog
      open={openExecuteReport}
      onClose={() => setOpenExecuteReport(false)}
      maxWidth="sm"
      fullWidth
    >
      <DialogTitle>
        Executar Relatório: {selectedReport?.nome}
      </DialogTitle>
      <DialogContent>
        <Grid container spacing={2} sx={{ mt: 1 }}>
          <Grid item xs={12}>
            <FormControl fullWidth>
              <InputLabel>Formato de Exportação</InputLabel>
              <Select
                value={parametrosExecucao.formato_exportacao}
                onChange={(e) => setParametrosExecucao({ 
                  ...parametrosExecucao, 
                  formato_exportacao: e.target.value as FormatoExportacao 
                })}
                label="Formato de Exportação"
              >
                {Object.values(FormatoExportacao).map(formato => (
                  <MenuItem key={formato} value={formato}>{formato}</MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>

          <Grid item xs={12}>
            <FormControlLabel
              control={
                <Checkbox
                  checked={parametrosExecucao.usar_cache}
                  onChange={(e) => setParametrosExecucao({ 
                    ...parametrosExecucao, 
                    usar_cache: e.target.checked 
                  })}
                />
              }
              label="Usar cache (se disponível)"
            />
          </Grid>

          {/* Aqui seria renderizado o formulário dinâmico baseado nos filtros disponíveis */}
          {selectedReport?.filtros_disponiveis && selectedReport.filtros_disponiveis.length > 0 && (
            <Grid item xs={12}>
              <Typography variant="subtitle1" gutterBottom>
                Filtros
              </Typography>
              {/* Implementar renderização dinâmica dos filtros */}
            </Grid>
          )}
        </Grid>
      </DialogContent>
      <DialogActions>
        <Button onClick={() => setOpenExecuteReport(false)}>
          Cancelar
        </Button>
        <Button
          onClick={executarRelatorio}
          variant="contained"
          disabled={loading}
          startIcon={loading ? <CircularProgress size={16} /> : <PlayIcon />}
        >
          Executar
        </Button>
      </DialogActions>
    </Dialog>
  );

  // === SPEED DIAL ===

  const speedDialActions = [
    {
      icon: <ReportIcon />,
      name: 'Novo Relatório',
      onClick: () => setOpenCreateReport(true)
    },
    {
      icon: <DashboardIcon />,
      name: 'Novo Dashboard',
      onClick: () => setOpenCreateDashboard(true)
    },
    {
      icon: <SpeedIcon />,
      name: 'Nova Métrica',
      onClick: () => setOpenCreateMetric(true)
    },
    {
      icon: <DownloadIcon />,
      name: 'Templates Padrão',
      onClick: inicializarTemplates
    },
    {
      icon: <AnalyticsIcon />,
      name: 'KPIs Padrão',
      onClick: inicializarKpis
    }
  ];

  // === RENDER PRINCIPAL ===

  return (
    <Box>
      <Box display="flex" justifyContent="between" alignItems="center" mb={3}>
        <Typography variant="h4" component="h1">
          Sistema de Relatórios Avançados
        </Typography>
      </Box>

      {loading && <LinearProgress sx={{ mb: 2 }} />}

      <Tabs
        value={activeTab}
        onChange={(_, newValue) => setActiveTab(newValue)}
        sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}
      >
        <Tab
          icon={<DashboardIcon />}
          label="Dashboard"
          iconPosition="start"
        />
        <Tab
          icon={<ReportIcon />}
          label="Relatórios"
          iconPosition="start"
        />
        <Tab
          icon={<ChartIcon />}
          label="Dashboards"
          iconPosition="start"
        />
        <Tab
          icon={<SpeedIcon />}
          label="Métricas"
          iconPosition="start"
        />
        <Tab
          icon={<TimelineIcon />}
          label="Execuções"
          iconPosition="start"
        />
      </Tabs>

      <TabPanel value={activeTab} index={0}>
        {renderDashboardPrincipal()}
      </TabPanel>

      <TabPanel value={activeTab} index={1}>
        {renderListaRelatorios()}
      </TabPanel>

      <TabPanel value={activeTab} index={2}>
        <Alert severity="info">
          Interface de dashboards em desenvolvimento
        </Alert>
      </TabPanel>

      <TabPanel value={activeTab} index={3}>
        <Alert severity="info">
          Interface de métricas em desenvolvimento
        </Alert>
      </TabPanel>

      <TabPanel value={activeTab} index={4}>
        <Alert severity="info">
          Interface de execuções em desenvolvimento
        </Alert>
      </TabPanel>

      {/* Speed Dial */}
      <SpeedDial
        ariaLabel="Ações de relatórios"
        sx={{ position: 'fixed', bottom: 16, right: 16 }}
        icon={<SpeedDialIcon />}
      >
        {speedDialActions.map((action) => (
          <SpeedDialAction
            key={action.name}
            icon={action.icon}
            tooltipTitle={action.name}
            onClick={action.onClick}
          />
        ))}
      </SpeedDial>

      {/* Diálogos */}
      {renderDialogCreateReport()}
      {renderDialogExecuteReport()}
    </Box>
  );
};

export default RelatoriosModule;
