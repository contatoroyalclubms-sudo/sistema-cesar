import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  TextField,
  Button,
  Grid,
  Card,
  CardContent,
  CardActions,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  IconButton,
  Tooltip,
  Alert,
  Divider,
  LinearProgress
} from '@mui/material';
import {
  CreditCard,
  MonetizationOn,
  History,
  QrCode,
  AccountBalance,
  Refresh,
  Settings,
  Block,
  CheckCircle,
  Cancel,
  Receipt,
  TrendingUp,
  TrendingDown
} from '@mui/icons-material';
import { DataGrid, GridColDef } from '@mui/x-data-grid';
import { useSnackbar } from 'notistack';
import { formatCurrency, formatDate } from '../utils/formatters';
import { cashlessService } from '../services/cashlessService';

interface Recarga {
  id: number;
  numero_recarga: string;
  cartao_id: number;
  valor_recarga: number;
  valor_bonus: number;
  valor_total: number;
  forma_pagamento: string;
  status: 'pendente' | 'aprovada' | 'cancelada' | 'estornada';
  cpf_cliente?: string;
  nome_cliente?: string;
  criado_em: string;
  atualizado_em?: string;
}

interface Movimentacao {
  id: number;
  numero_movimento: string;
  cartao_id: number;
  tipo_movimentacao: 'credito' | 'debito' | 'estorno' | 'bonus';
  valor: number;
  saldo_anterior: number;
  saldo_posterior: number;
  descricao: string;
  criado_em: string;
}

interface DashboardData {
  recargas: {
    total_recargas: number;
    valor_total_recargas: number;
    valor_total_bonus: number;
    recargas_aprovadas: number;
    recargas_pendentes: number;
    recargas_canceladas: number;
    ticket_medio: number;
  };
  movimentacoes: {
    total_movimentacoes: number;
    valor_total_creditos: number;
    valor_total_debitos: number;
    saldo_atual_sistema: number;
    cartoes_ativos: number;
    cartoes_bloqueados: number;
  };
  eventos_ativos: number;
  terminais_online: number;
  comandas_abertas: number;
}

const CashlessModule: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'dashboard' | 'recargas' | 'movimentacoes' | 'comandas'>('dashboard');
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null);
  const [recargas, setRecargas] = useState<Recarga[]>([]);
  const [movimentacoes, setMovimentacoes] = useState<Movimentacao[]>([]);
  const [loading, setLoading] = useState(false);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [dialogType, setDialogType] = useState<'recarga' | 'movimentacao' | 'config'>('recarga');
  const [selectedItem, setSelectedItem] = useState<any>(null);
  const [filters, setFilters] = useState({
    evento_id: '',
    data_inicio: '',
    data_fim: '',
    status: ''
  });

  const { enqueueSnackbar } = useSnackbar();

  // Carregar dados do dashboard
  const loadDashboard = async () => {
    try {
      setLoading(true);
      const response = await cashlessService.getDashboard(filters);
      setDashboardData(response.data);
    } catch (error) {
      enqueueSnackbar('Erro ao carregar dashboard', { variant: 'error' });
    } finally {
      setLoading(false);
    }
  };

  // Carregar recargas
  const loadRecargas = async () => {
    try {
      setLoading(true);
      const response = await cashlessService.getRecargas(filters);
      setRecargas(response.data);
    } catch (error) {
      enqueueSnackbar('Erro ao carregar recargas', { variant: 'error' });
    } finally {
      setLoading(false);
    }
  };

  // Carregar movimentações
  const loadMovimentacoes = async () => {
    try {
      setLoading(true);
      const response = await cashlessService.getMovimentacoes(filters);
      setMovimentacoes(response.data);
    } catch (error) {
      enqueueSnackbar('Erro ao carregar movimentações', { variant: 'error' });
    } finally {
      setLoading(false);
    }
  };

  // Aprovar recarga
  const aprovarRecarga = async (recargaId: number) => {
    try {
      await cashlessService.updateRecarga(recargaId, { status: 'aprovada' });
      enqueueSnackbar('Recarga aprovada com sucesso', { variant: 'success' });
      loadRecargas();
      loadDashboard();
    } catch (error) {
      enqueueSnackbar('Erro ao aprovar recarga', { variant: 'error' });
    }
  };

  // Cancelar recarga
  const cancelarRecarga = async (recargaId: number) => {
    try {
      await cashlessService.updateRecarga(recargaId, { status: 'cancelada' });
      enqueueSnackbar('Recarga cancelada', { variant: 'warning' });
      loadRecargas();
      loadDashboard();
    } catch (error) {
      enqueueSnackbar('Erro ao cancelar recarga', { variant: 'error' });
    }
  };

  useEffect(() => {
    loadDashboard();
  }, [filters]);

  useEffect(() => {
    if (activeTab === 'recargas') {
      loadRecargas();
    } else if (activeTab === 'movimentacoes') {
      loadMovimentacoes();
    }
  }, [activeTab, filters]);

  // Configurar colunas das recargas
  const recargasColumns: GridColDef[] = [
    { 
      field: 'numero_recarga', 
      headerName: 'Número', 
      width: 150,
      renderCell: (params) => (
        <Typography variant="body2" fontFamily="monospace">
          {params.value}
        </Typography>
      )
    },
    { 
      field: 'nome_cliente', 
      headerName: 'Cliente', 
      width: 200 
    },
    { 
      field: 'valor_recarga', 
      headerName: 'Valor', 
      width: 120,
      renderCell: (params) => formatCurrency(params.value)
    },
    { 
      field: 'valor_bonus', 
      headerName: 'Bônus', 
      width: 120,
      renderCell: (params) => formatCurrency(params.value)
    },
    { 
      field: 'valor_total', 
      headerName: 'Total', 
      width: 120,
      renderCell: (params) => (
        <Typography variant="body2" fontWeight="bold">
          {formatCurrency(params.value)}
        </Typography>
      )
    },
    { 
      field: 'forma_pagamento', 
      headerName: 'Forma Pagamento', 
      width: 150 
    },
    { 
      field: 'status', 
      headerName: 'Status', 
      width: 120,
      renderCell: (params) => {
        const colors = {
          pendente: 'warning',
          aprovada: 'success',
          cancelada: 'error',
          estornada: 'default'
        } as const;
        
        return (
          <Chip 
            label={params.value} 
            color={colors[params.value as keyof typeof colors]}
            size="small"
          />
        );
      }
    },
    { 
      field: 'criado_em', 
      headerName: 'Data', 
      width: 160,
      renderCell: (params) => formatDate(params.value)
    },
    {
      field: 'actions',
      headerName: 'Ações',
      width: 150,
      renderCell: (params) => (
        <Box>
          {params.row.status === 'pendente' && (
            <>
              <Tooltip title="Aprovar">
                <IconButton 
                  size="small" 
                  color="success"
                  onClick={() => aprovarRecarga(params.row.id)}
                >
                  <CheckCircle />
                </IconButton>
              </Tooltip>
              <Tooltip title="Cancelar">
                <IconButton 
                  size="small" 
                  color="error"
                  onClick={() => cancelarRecarga(params.row.id)}
                >
                  <Cancel />
                </IconButton>
              </Tooltip>
            </>
          )}
          <Tooltip title="Detalhes">
            <IconButton 
              size="small"
              onClick={() => {
                setSelectedItem(params.row);
                setDialogType('recarga');
                setDialogOpen(true);
              }}
            >
              <Receipt />
            </IconButton>
          </Tooltip>
        </Box>
      )
    }
  ];

  // Configurar colunas das movimentações
  const movimentacoesColumns: GridColDef[] = [
    { 
      field: 'numero_movimento', 
      headerName: 'Número', 
      width: 150,
      renderCell: (params) => (
        <Typography variant="body2" fontFamily="monospace">
          {params.value}
        </Typography>
      )
    },
    { 
      field: 'tipo_movimentacao', 
      headerName: 'Tipo', 
      width: 120,
      renderCell: (params) => {
        const colors = {
          credito: 'success',
          debito: 'error',
          estorno: 'warning',
          bonus: 'info'
        } as const;
        
        const icons = {
          credito: <TrendingUp />,
          debito: <TrendingDown />,
          estorno: <Refresh />,
          bonus: <MonetizationOn />
        };
        
        return (
          <Chip 
            icon={icons[params.value as keyof typeof icons]}
            label={params.value} 
            color={colors[params.value as keyof typeof colors]}
            size="small"
          />
        );
      }
    },
    { 
      field: 'valor', 
      headerName: 'Valor', 
      width: 120,
      renderCell: (params) => (
        <Typography 
          variant="body2" 
          color={params.row.tipo_movimentacao === 'credito' ? 'success.main' : 'error.main'}
          fontWeight="bold"
        >
          {params.row.tipo_movimentacao === 'credito' ? '+' : '-'}
          {formatCurrency(params.value)}
        </Typography>
      )
    },
    { 
      field: 'saldo_posterior', 
      headerName: 'Saldo Final', 
      width: 120,
      renderCell: (params) => formatCurrency(params.value)
    },
    { 
      field: 'descricao', 
      headerName: 'Descrição', 
      width: 250 
    },
    { 
      field: 'criado_em', 
      headerName: 'Data', 
      width: 160,
      renderCell: (params) => formatDate(params.value)
    }
  ];

  const renderDashboard = () => (
    <Grid container spacing={3}>
      {/* Cards de resumo */}
      <Grid item xs={12} md={3}>
        <Card>
          <CardContent>
            <Box display="flex" alignItems="center" mb={2}>
              <MonetizationOn color="primary" sx={{ mr: 1 }} />
              <Typography variant="h6">Recargas</Typography>
            </Box>
            <Typography variant="h4" color="primary">
              {dashboardData?.recargas.total_recargas || 0}
            </Typography>
            <Typography variant="body2" color="textSecondary">
              {formatCurrency(dashboardData?.recargas.valor_total_recargas || 0)}
            </Typography>
          </CardContent>
        </Card>
      </Grid>

      <Grid item xs={12} md={3}>
        <Card>
          <CardContent>
            <Box display="flex" alignItems="center" mb={2}>
              <AccountBalance color="success" sx={{ mr: 1 }} />
              <Typography variant="h6">Saldo Sistema</Typography>
            </Box>
            <Typography variant="h4" color="success.main">
              {formatCurrency(dashboardData?.movimentacoes.saldo_atual_sistema || 0)}
            </Typography>
            <Typography variant="body2" color="textSecondary">
              Em {dashboardData?.movimentacoes.cartoes_ativos || 0} cartões
            </Typography>
          </CardContent>
        </Card>
      </Grid>

      <Grid item xs={12} md={3}>
        <Card>
          <CardContent>
            <Box display="flex" alignItems="center" mb={2}>
              <CreditCard color="info" sx={{ mr: 1 }} />
              <Typography variant="h6">Cartões Ativos</Typography>
            </Box>
            <Typography variant="h4" color="info.main">
              {dashboardData?.movimentacoes.cartoes_ativos || 0}
            </Typography>
            <Typography variant="body2" color="textSecondary">
              {dashboardData?.movimentacoes.cartoes_bloqueados || 0} bloqueados
            </Typography>
          </CardContent>
        </Card>
      </Grid>

      <Grid item xs={12} md={3}>
        <Card>
          <CardContent>
            <Box display="flex" alignItems="center" mb={2}>
              <QrCode color="warning" sx={{ mr: 1 }} />
              <Typography variant="h6">Comandas Abertas</Typography>
            </Box>
            <Typography variant="h4" color="warning.main">
              {dashboardData?.comandas_abertas || 0}
            </Typography>
            <Typography variant="body2" color="textSecondary">
              Digitais ativas
            </Typography>
          </CardContent>
        </Card>
      </Grid>

      {/* Gráficos e estatísticas */}
      <Grid item xs={12} md={6}>
        <Paper sx={{ p: 3 }}>
          <Typography variant="h6" mb={2}>Resumo de Recargas</Typography>
          <Grid container spacing={2}>
            <Grid item xs={6}>
              <Box textAlign="center">
                <Typography variant="h4" color="success.main">
                  {dashboardData?.recargas.recargas_aprovadas || 0}
                </Typography>
                <Typography variant="body2">Aprovadas</Typography>
              </Box>
            </Grid>
            <Grid item xs={6}>
              <Box textAlign="center">
                <Typography variant="h4" color="warning.main">
                  {dashboardData?.recargas.recargas_pendentes || 0}
                </Typography>
                <Typography variant="body2">Pendentes</Typography>
              </Box>
            </Grid>
          </Grid>
          <Divider sx={{ my: 2 }} />
          <Typography variant="body1">
            Ticket Médio: <strong>{formatCurrency(dashboardData?.recargas.ticket_medio || 0)}</strong>
          </Typography>
          <Typography variant="body1">
            Total Bônus: <strong>{formatCurrency(dashboardData?.recargas.valor_total_bonus || 0)}</strong>
          </Typography>
        </Paper>
      </Grid>

      <Grid item xs={12} md={6}>
        <Paper sx={{ p: 3 }}>
          <Typography variant="h6" mb={2}>Movimentações Financeiras</Typography>
          <Grid container spacing={2}>
            <Grid item xs={6}>
              <Box textAlign="center">
                <Typography variant="h4" color="success.main">
                  {formatCurrency(dashboardData?.movimentacoes.valor_total_creditos || 0)}
                </Typography>
                <Typography variant="body2">Total Créditos</Typography>
              </Box>
            </Grid>
            <Grid item xs={6}>
              <Box textAlign="center">
                <Typography variant="h4" color="error.main">
                  {formatCurrency(dashboardData?.movimentacoes.valor_total_debitos || 0)}
                </Typography>
                <Typography variant="body2">Total Débitos</Typography>
              </Box>
            </Grid>
          </Grid>
          <Divider sx={{ my: 2 }} />
          <Typography variant="body1">
            Total Movimentações: <strong>{dashboardData?.movimentacoes.total_movimentacoes || 0}</strong>
          </Typography>
        </Paper>
      </Grid>
    </Grid>
  );

  const renderTabContent = () => {
    switch (activeTab) {
      case 'dashboard':
        return renderDashboard();
      case 'recargas':
        return (
          <Paper sx={{ height: 600, width: '100%' }}>
            <DataGrid
              rows={recargas}
              columns={recargasColumns}
              loading={loading}
              pageSizeOptions={[25, 50, 100]}
              initialState={{
                pagination: { paginationModel: { pageSize: 25 } }
              }}
            />
          </Paper>
        );
      case 'movimentacoes':
        return (
          <Paper sx={{ height: 600, width: '100%' }}>
            <DataGrid
              rows={movimentacoes}
              columns={movimentacoesColumns}
              loading={loading}
              pageSizeOptions={[25, 50, 100]}
              initialState={{
                pagination: { paginationModel: { pageSize: 25 } }
              }}
            />
          </Paper>
        );
      default:
        return null;
    }
  };

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" fontWeight="bold">
          Sistema Cashless
        </Typography>
        <Box>
          <Button
            variant="outlined"
            startIcon={<Refresh />}
            onClick={() => {
              loadDashboard();
              if (activeTab === 'recargas') loadRecargas();
              if (activeTab === 'movimentacoes') loadMovimentacoes();
            }}
            sx={{ mr: 1 }}
          >
            Atualizar
          </Button>
          <Button
            variant="contained"
            startIcon={<Settings />}
            onClick={() => {
              setDialogType('config');
              setDialogOpen(true);
            }}
          >
            Configurações
          </Button>
        </Box>
      </Box>

      {/* Filtros */}
      <Paper sx={{ p: 2, mb: 3 }}>
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} md={3}>
            <TextField
              fullWidth
              type="date"
              label="Data Início"
              value={filters.data_inicio}
              onChange={(e) => setFilters({ ...filters, data_inicio: e.target.value })}
              InputLabelProps={{ shrink: true }}
            />
          </Grid>
          <Grid item xs={12} md={3}>
            <TextField
              fullWidth
              type="date"
              label="Data Fim"
              value={filters.data_fim}
              onChange={(e) => setFilters({ ...filters, data_fim: e.target.value })}
              InputLabelProps={{ shrink: true }}
            />
          </Grid>
          <Grid item xs={12} md={3}>
            <FormControl fullWidth>
              <InputLabel>Status</InputLabel>
              <Select
                value={filters.status}
                onChange={(e) => setFilters({ ...filters, status: e.target.value })}
              >
                <MenuItem value="">Todos</MenuItem>
                <MenuItem value="pendente">Pendente</MenuItem>
                <MenuItem value="aprovada">Aprovada</MenuItem>
                <MenuItem value="cancelada">Cancelada</MenuItem>
              </Select>
            </FormControl>
          </Grid>
        </Grid>
      </Paper>

      {/* Navegação por abas */}
      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
        <Grid container spacing={1}>
          {[
            { key: 'dashboard', label: 'Dashboard', icon: <TrendingUp /> },
            { key: 'recargas', label: 'Recargas', icon: <MonetizationOn /> },
            { key: 'movimentacoes', label: 'Movimentações', icon: <History /> },
            { key: 'comandas', label: 'Comandas', icon: <QrCode /> }
          ].map((tab) => (
            <Grid item key={tab.key}>
              <Button
                variant={activeTab === tab.key ? 'contained' : 'outlined'}
                startIcon={tab.icon}
                onClick={() => setActiveTab(tab.key as any)}
                sx={{ mr: 1 }}
              >
                {tab.label}
              </Button>
            </Grid>
          ))}
        </Grid>
      </Box>

      {/* Conteúdo da aba */}
      {loading && <LinearProgress sx={{ mb: 2 }} />}
      {renderTabContent()}

      {/* Dialog para detalhes/configurações */}
      <Dialog 
        open={dialogOpen} 
        onClose={() => setDialogOpen(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          {dialogType === 'recarga' && 'Detalhes da Recarga'}
          {dialogType === 'movimentacao' && 'Detalhes da Movimentação'}
          {dialogType === 'config' && 'Configurações do Sistema'}
        </DialogTitle>
        <DialogContent>
          {selectedItem && dialogType === 'recarga' && (
            <Grid container spacing={2}>
              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  label="Número da Recarga"
                  value={selectedItem.numero_recarga}
                  disabled
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  label="Status"
                  value={selectedItem.status}
                  disabled
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  label="Cliente"
                  value={selectedItem.nome_cliente || 'N/A'}
                  disabled
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  label="Forma de Pagamento"
                  value={selectedItem.forma_pagamento}
                  disabled
                />
              </Grid>
              <Grid item xs={12} md={4}>
                <TextField
                  fullWidth
                  label="Valor Recarga"
                  value={formatCurrency(selectedItem.valor_recarga)}
                  disabled
                />
              </Grid>
              <Grid item xs={12} md={4}>
                <TextField
                  fullWidth
                  label="Valor Bônus"
                  value={formatCurrency(selectedItem.valor_bonus)}
                  disabled
                />
              </Grid>
              <Grid item xs={12} md={4}>
                <TextField
                  fullWidth
                  label="Valor Total"
                  value={formatCurrency(selectedItem.valor_total)}
                  disabled
                />
              </Grid>
            </Grid>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDialogOpen(false)}>
            Fechar
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default CashlessModule;
