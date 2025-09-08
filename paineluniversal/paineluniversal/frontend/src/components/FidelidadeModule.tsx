/*
Componente React para Sistema de Fidelidade Expandido
Interface completa para gestão de níveis, pontuação, campanhas e recompensas
*/

import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Autocomplete,
  Chip,
  Tab,
  Tabs,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  Alert,
  LinearProgress,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Switch,
  FormControlLabel,
  Tooltip,
  IconButton,
  Paper,
  Avatar,
  Badge,
  Divider
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Star as StarIcon,
  TrendingUp as TrendingUpIcon,
  People as PeopleIcon,
  CardGiftcard as GiftIcon,
  Campaign as CampaignIcon,
  Share as ShareIcon,
  Redeem as RedeemIcon,
  Analytics as AnalyticsIcon,
  EmojiEvents as TrophyIcon
} from '@mui/icons-material';

import {
  FidelidadeService,
  NivelFidelidade,
  CampanhaFidelidade,
  PontuacaoCliente,
  IndicacaoCliente,
  ResgateRecompensa,
  DashboardFidelidade,
  TipoNivelFidelidade,
  StatusCampanha,
  TipoRecompensa,
  TipoMovimentacaoPonto,
  NivelFidelidadeCreate,
  CampanhaFidelidadeCreate,
  MovimentacaoPontosCreate,
  IndicacaoCreate,
  ResgateRecompensaCreate
} from '../services/fidelidadeService';

// ================================================================================
// INTERFACES
// ================================================================================

interface FidelidadeModuleProps {
  empresaId: number;
}

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

// ================================================================================
// COMPONENTES AUXILIARES
// ================================================================================

function TabPanel({ children, value, index, ...other }: TabPanelProps) {
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`fidelidade-tabpanel-${index}`}
      aria-labelledby={`fidelidade-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
}

function NivelChip({ nivel }: { nivel: NivelFidelidade }) {
  const cor = FidelidadeService.obterCorNivel(nivel.tipo);
  const icone = FidelidadeService.obterIconeNivel(nivel.tipo);

  return (
    <Chip
      icon={<span style={{ fontSize: '16px' }}>{icone}</span>}
      label={nivel.nome}
      sx={{
        backgroundColor: cor,
        color: '#fff',
        fontWeight: 'bold',
        textShadow: '1px 1px 2px rgba(0,0,0,0.5)'
      }}
    />
  );
}

// ================================================================================
// COMPONENTE PRINCIPAL
// ================================================================================

export const FidelidadeModule: React.FC<FidelidadeModuleProps> = ({ empresaId }) => {
  // ============================================================================
  // ESTADO
  // ============================================================================

  const [tabValue, setTabValue] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string>('');
  const [success, setSuccess] = useState<string>('');

  // Dashboard
  const [dashboard, setDashboard] = useState<DashboardFidelidade | null>(null);

  // Níveis
  const [niveis, setNiveis] = useState<Array<{ nivel: NivelFidelidade; total_clientes: number }>>([]);
  const [dialogNivel, setDialogNivel] = useState(false);
  const [nivelEdit, setNivelEdit] = useState<NivelFidelidade | null>(null);

  // Campanhas
  const [campanhas, setCampanhas] = useState<Array<{ campanha: CampanhaFidelidade }>>([]);
  const [dialogCampanha, setDialogCampanha] = useState(false);
  const [campanhaEdit, setCampanhaEdit] = useState<CampanhaFidelidade | null>(null);

  // Pontos
  const [dialogPontos, setDialogPontos] = useState(false);
  const [clienteSelecionado, setClienteSelecionado] = useState<any>(null);
  const [historicoPontos, setHistoricoPontos] = useState<Array<{
    movimentacao: PontuacaoCliente;
    saldo_periodo: number;
  }>>([]);

  // Indicações
  const [dialogIndicacao, setDialogIndicacao] = useState(false);

  // Resgates
  const [dialogResgate, setDialogResgate] = useState(false);

  // ============================================================================
  // EFFECTS
  // ============================================================================

  useEffect(() => {
    carregarDados();
  }, [empresaId]);

  useEffect(() => {
    if (tabValue === 0) {
      carregarDashboard();
    } else if (tabValue === 1) {
      carregarNiveis();
    } else if (tabValue === 2) {
      carregarCampanhas();
    }
  }, [tabValue]);

  // ============================================================================
  // CARREGAMENTO DE DADOS
  // ============================================================================

  const carregarDados = async () => {
    setLoading(true);
    try {
      await Promise.all([
        carregarDashboard(),
        carregarNiveis(),
        carregarCampanhas()
      ]);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const carregarDashboard = async () => {
    try {
      const data = await FidelidadeService.obterDashboardFidelidade();
      setDashboard(data);
    } catch (err: any) {
      console.error('Erro ao carregar dashboard:', err);
    }
  };

  const carregarNiveis = async () => {
    try {
      const data = await FidelidadeService.listarNiveisFidelidade();
      setNiveis(data);
    } catch (err: any) {
      console.error('Erro ao carregar níveis:', err);
    }
  };

  const carregarCampanhas = async () => {
    try {
      const data = await FidelidadeService.listarCampanhasFidelidade();
      setCampanhas(data);
    } catch (err: any) {
      console.error('Erro ao carregar campanhas:', err);
    }
  };

  const carregarHistoricoPontos = async (clienteId: number) => {
    try {
      const data = await FidelidadeService.obterHistoricoPontos(clienteId);
      setHistoricoPontos(data);
    } catch (err: any) {
      setError(err.message);
    }
  };

  // ============================================================================
  // HANDLERS
  // ============================================================================

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  const handleCriarNivel = async (dadosNivel: NivelFidelidadeCreate) => {
    try {
      setLoading(true);
      await FidelidadeService.criarNivelFidelidade(dadosNivel);
      setSuccess('Nível de fidelidade criado com sucesso!');
      setDialogNivel(false);
      await carregarNiveis();
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleCriarCampanha = async (dadosCampanha: CampanhaFidelidadeCreate) => {
    try {
      setLoading(true);
      const erros = FidelidadeService.validarCampanha(dadosCampanha);
      if (erros.length > 0) {
        setError(erros.join(', '));
        return;
      }
      
      await FidelidadeService.criarCampanhaFidelidade(dadosCampanha);
      setSuccess('Campanha de fidelidade criada com sucesso!');
      setDialogCampanha(false);
      await carregarCampanhas();
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleMovimentarPontos = async (dadosMovimentacao: MovimentacaoPontosCreate) => {
    try {
      setLoading(true);
      await FidelidadeService.criarMovimentacaoPontos(dadosMovimentacao);
      setSuccess('Pontos movimentados com sucesso!');
      setDialogPontos(false);
      if (clienteSelecionado) {
        await carregarHistoricoPontos(clienteSelecionado.id);
      }
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // ============================================================================
  // RENDER - DASHBOARD
  // ============================================================================

  const renderDashboard = () => (
    <Grid container spacing={3}>
      {/* KPIs Principais */}
      <Grid item xs={12} md={3}>
        <Card>
          <CardContent>
            <Box display="flex" alignItems="center">
              <PeopleIcon color="primary" sx={{ mr: 2, fontSize: 40 }} />
              <Box>
                <Typography variant="h4" component="div">
                  {dashboard?.total_clientes || 0}
                </Typography>
                <Typography color="text.secondary">
                  Total de Clientes
                </Typography>
              </Box>
            </Box>
          </CardContent>
        </Card>
      </Grid>

      <Grid item xs={12} md={3}>
        <Card>
          <CardContent>
            <Box display="flex" alignItems="center">
              <TrendingUpIcon color="success" sx={{ mr: 2, fontSize: 40 }} />
              <Box>
                <Typography variant="h4" component="div">
                  {dashboard?.clientes_ativos || 0}
                </Typography>
                <Typography color="text.secondary">
                  Clientes Ativos
                </Typography>
              </Box>
            </Box>
          </CardContent>
        </Card>
      </Grid>

      <Grid item xs={12} md={3}>
        <Card>
          <CardContent>
            <Box display="flex" alignItems="center">
              <StarIcon color="warning" sx={{ mr: 2, fontSize: 40 }} />
              <Box>
                <Typography variant="h4" component="div">
                  {FidelidadeService.formatarPontos(dashboard?.pontos_em_circulacao || 0)}
                </Typography>
                <Typography color="text.secondary">
                  Pontos em Circulação
                </Typography>
              </Box>
            </Box>
          </CardContent>
        </Card>
      </Grid>

      <Grid item xs={12} md={3}>
        <Card>
          <CardContent>
            <Box display="flex" alignItems="center">
              <CampaignIcon color="secondary" sx={{ mr: 2, fontSize: 40 }} />
              <Box>
                <Typography variant="h4" component="div">
                  {dashboard?.campanhas_ativas || 0}
                </Typography>
                <Typography color="text.secondary">
                  Campanhas Ativas
                </Typography>
              </Box>
            </Box>
          </CardContent>
        </Card>
      </Grid>

      {/* Distribuição por Níveis */}
      <Grid item xs={12} md={8}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Distribuição de Clientes por Nível
            </Typography>
            <Grid container spacing={2}>
              {dashboard?.distribuicao_niveis.map((distribuicao, index) => (
                <Grid item xs={12} sm={6} md={4} key={index}>
                  <Paper sx={{ p: 2, textAlign: 'center' }}>
                    <Box display="flex" alignItems="center" justifyContent="center" mb={1}>
                      <span style={{ fontSize: '24px', marginRight: '8px' }}>
                        {FidelidadeService.obterIconeNivel(distribuicao.tipo)}
                      </span>
                      <Typography variant="h6">{distribuicao.nome}</Typography>
                    </Box>
                    <Typography variant="h4" color="primary">
                      {distribuicao.quantidade}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      clientes
                    </Typography>
                  </Paper>
                </Grid>
              ))}
            </Grid>
          </CardContent>
        </Card>
      </Grid>

      {/* Top Clientes */}
      <Grid item xs={12} md={4}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              <TrophyIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
              Top Clientes
            </Typography>
            {dashboard?.top_clientes.slice(0, 5).map((cliente, index) => (
              <Box key={cliente.id} display="flex" alignItems="center" mb={1}>
                <Avatar sx={{ width: 24, height: 24, mr: 1, fontSize: 14 }}>
                  {index + 1}
                </Avatar>
                <Box flexGrow={1}>
                  <Typography variant="body2">{cliente.nome}</Typography>
                  <Typography variant="caption" color="text.secondary">
                    {cliente.nivel}
                  </Typography>
                </Box>
                <Typography variant="body2" color="primary">
                  {FidelidadeService.formatarPontos(cliente.pontos)} pts
                </Typography>
              </Box>
            ))}
          </CardContent>
        </Card>
      </Grid>

      {/* Movimentações do Mês */}
      <Grid item xs={12}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Movimentações dos Últimos 30 Dias
            </Typography>
            <Grid container spacing={3}>
              {dashboard?.movimentacoes_mes.map((movimentacao, index) => (
                <Grid item xs={12} sm={6} md={3} key={index}>
                  <Paper sx={{ p: 2, textAlign: 'center' }}>
                    <Typography variant="h6" color="primary">
                      {FidelidadeService.formatarPontos(movimentacao.total_pontos)}
                    </Typography>
                    <Typography variant="body2">
                      {FidelidadeService.obterDescricaoMovimentacao(movimentacao.tipo)}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      {movimentacao.total_movimentacoes} movimentações
                    </Typography>
                  </Paper>
                </Grid>
              ))}
            </Grid>
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  );

  // ============================================================================
  // RENDER - NÍVEIS
  // ============================================================================

  const renderNiveis = () => (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h5">Níveis de Fidelidade</Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => {
            setNivelEdit(null);
            setDialogNivel(true);
          }}
        >
          Novo Nível
        </Button>
      </Box>

      <Grid container spacing={3}>
        {niveis.map(({ nivel, total_clientes }) => (
          <Grid item xs={12} sm={6} md={4} key={nivel.id}>
            <Card>
              <CardContent>
                <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                  <NivelChip nivel={nivel} />
                  <Box>
                    <IconButton
                      size="small"
                      onClick={() => {
                        setNivelEdit(nivel);
                        setDialogNivel(true);
                      }}
                    >
                      <EditIcon />
                    </IconButton>
                  </Box>
                </Box>

                <Typography variant="body2" color="text.secondary" gutterBottom>
                  {nivel.descricao || 'Sem descrição'}
                </Typography>

                <Divider sx={{ my: 2 }} />

                <Box mb={2}>
                  <Typography variant="caption" color="text.secondary">
                    Critérios para atingir
                  </Typography>
                  <Typography variant="body2">
                    • {FidelidadeService.formatarPontos(nivel.pontos_minimos)} pontos
                  </Typography>
                  <Typography variant="body2">
                    • R$ {nivel.valor_gasto_minimo.toFixed(2)} gastos
                  </Typography>
                  <Typography variant="body2">
                    • {nivel.compras_minimas} compras
                  </Typography>
                </Box>

                <Box mb={2}>
                  <Typography variant="caption" color="text.secondary">
                    Benefícios
                  </Typography>
                  <Typography variant="body2">
                    • {(nivel.multiplicador_pontos * 100).toFixed(0)}% pontos por compra
                  </Typography>
                  {nivel.desconto_percentual > 0 && (
                    <Typography variant="body2">
                      • {nivel.desconto_percentual}% desconto
                    </Typography>
                  )}
                  {nivel.frete_gratis && (
                    <Typography variant="body2">
                      • Frete grátis
                    </Typography>
                  )}
                  {nivel.suporte_prioritario && (
                    <Typography variant="body2">
                      • Suporte prioritário
                    </Typography>
                  )}
                </Box>

                <Box display="flex" justifyContent="space-between" alignItems="center">
                  <Typography variant="h6" color="primary">
                    {total_clientes}
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    clientes neste nível
                  </Typography>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Box>
  );

  // ============================================================================
  // RENDER - CAMPANHAS
  // ============================================================================

  const renderCampanhas = () => (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h5">Campanhas de Fidelidade</Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => {
            setCampanhaEdit(null);
            setDialogCampanha(true);
          }}
        >
          Nova Campanha
        </Button>
      </Box>

      <Grid container spacing={3}>
        {campanhas.map(({ campanha }) => (
          <Grid item xs={12} md={6} lg={4} key={campanha.id}>
            <Card>
              <CardContent>
                <Box display="flex" justifyContent="between" alignItems="center" mb={2}>
                  <Typography variant="h6" noWrap>
                    {campanha.nome}
                  </Typography>
                  <Chip
                    label={campanha.status}
                    color={campanha.status === StatusCampanha.ATIVA ? 'success' : 'default'}
                    size="small"
                  />
                </Box>

                {campanha.descricao && (
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    {campanha.descricao}
                  </Typography>
                )}

                <Box mb={2}>
                  <Typography variant="caption" color="text.secondary">
                    Período
                  </Typography>
                  <Typography variant="body2">
                    {new Date(campanha.data_inicio).toLocaleDateString('pt-BR')} até{' '}
                    {new Date(campanha.data_fim).toLocaleDateString('pt-BR')}
                  </Typography>
                </Box>

                <Box mb={2}>
                  <Typography variant="caption" color="text.secondary">
                    Recompensas
                  </Typography>
                  {campanha.multiplicador_pontos > 1 && (
                    <Typography variant="body2">
                      • {(campanha.multiplicador_pontos * 100).toFixed(0)}% pontos por compra
                    </Typography>
                  )}
                  {campanha.pontos_bonus > 0 && (
                    <Typography variant="body2">
                      • {FidelidadeService.formatarPontos(campanha.pontos_bonus)} pontos bônus
                    </Typography>
                  )}
                  {campanha.valor_minimo_compra && (
                    <Typography variant="body2">
                      • Valor mínimo: R$ {campanha.valor_minimo_compra.toFixed(2)}
                    </Typography>
                  )}
                </Box>

                {campanha.limite_participantes && (
                  <Box>
                    <Typography variant="caption" color="text.secondary">
                      Participação
                    </Typography>
                    <LinearProgress
                      variant="determinate"
                      value={(campanha.participantes_atuais / campanha.limite_participantes) * 100}
                      sx={{ mt: 1 }}
                    />
                    <Typography variant="caption">
                      {campanha.participantes_atuais}/{campanha.limite_participantes} participantes
                    </Typography>
                  </Box>
                )}

                {campanha.codigo && (
                  <Box mt={2}>
                    <Chip
                      label={`Código: ${campanha.codigo}`}
                      variant="outlined"
                      size="small"
                    />
                  </Box>
                )}
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Box>
  );

  // ============================================================================
  // RENDER PRINCIPAL
  // ============================================================================

  return (
    <Box sx={{ width: '100%' }}>
      {/* Alerts */}
      {error && (
        <Alert severity="error" onClose={() => setError('')} sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}
      {success && (
        <Alert severity="success" onClose={() => setSuccess('')} sx={{ mb: 2 }}>
          {success}
        </Alert>
      )}

      {/* Header */}
      <Box mb={3}>
        <Typography variant="h4" component="h1" gutterBottom>
          Sistema de Fidelidade
        </Typography>
        <Typography variant="subtitle1" color="text.secondary">
          Gestão completa do programa de fidelidade e relacionamento com clientes
        </Typography>
      </Box>

      {/* Tabs */}
      <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
        <Tabs value={tabValue} onChange={handleTabChange}>
          <Tab
            label="Dashboard"
            icon={<AnalyticsIcon />}
            iconPosition="start"
          />
          <Tab
            label="Níveis"
            icon={<TrophyIcon />}
            iconPosition="start"
          />
          <Tab
            label="Campanhas"
            icon={<CampaignIcon />}
            iconPosition="start"
          />
          <Tab
            label="Pontos"
            icon={<StarIcon />}
            iconPosition="start"
          />
          <Tab
            label="Indicações"
            icon={<ShareIcon />}
            iconPosition="start"
          />
          <Tab
            label="Resgates"
            icon={<RedeemIcon />}
            iconPosition="start"
          />
        </Tabs>
      </Box>

      {/* Tab Panels */}
      <TabPanel value={tabValue} index={0}>
        {renderDashboard()}
      </TabPanel>

      <TabPanel value={tabValue} index={1}>
        {renderNiveis()}
      </TabPanel>

      <TabPanel value={tabValue} index={2}>
        {renderCampanhas()}
      </TabPanel>

      <TabPanel value={tabValue} index={3}>
        <Typography>Em desenvolvimento - Gestão de Pontos</Typography>
      </TabPanel>

      <TabPanel value={tabValue} index={4}>
        <Typography>Em desenvolvimento - Sistema de Indicações</Typography>
      </TabPanel>

      <TabPanel value={tabValue} index={5}>
        <Typography>Em desenvolvimento - Resgates e Recompensas</Typography>
      </TabPanel>

      {/* Loading Overlay */}
      {loading && (
        <Box
          position="fixed"
          top={0}
          left={0}
          right={0}
          bottom={0}
          bgcolor="rgba(0,0,0,0.5)"
          display="flex"
          alignItems="center"
          justifyContent="center"
          zIndex={9999}
        >
          <Paper sx={{ p: 3 }}>
            <Typography>Carregando...</Typography>
          </Paper>
        </Box>
      )}
    </Box>
  );
};
