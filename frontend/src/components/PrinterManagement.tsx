import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  Button,
  TextField,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Switch,
  FormControlLabel,
  Chip,
  Alert,
  IconButton,
  Tooltip,
  Divider,
  Paper,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  CircularProgress,
  Fab
} from '@mui/material';
import {
  Add as AddIcon,
  Print as PrintIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Refresh as RefreshIcon,
  PlayArrow as TestIcon,
  Settings as SettingsIcon,
  CheckCircle as OnlineIcon,
  Error as ErrorIcon,
  Warning as WarningIcon
} from '@mui/icons-material';
import { useSnackbar } from 'notistack';
import { api } from '../services/api';

// Tipos TypeScript
interface Impressora {
  id: string;
  nome: string;
  tipo: 'TERMICA_58MM' | 'TERMICA_80MM' | 'MATRICIAL' | 'JATO_TINTA';
  interface: 'USB' | 'ETHERNET' | 'WIFI' | 'BLUETOOTH' | 'PARALELA' | 'SERIAL';
  endereco: string;
  porta?: number;
  status: 'ONLINE' | 'OFFLINE' | 'ERRO_PAPEL' | 'ERRO_CONEXAO' | 'MANUTENCAO' | 'DESCONHECIDO';
  estacao?: string;
  local_fisico?: string;
  ativo: boolean;
  densidade: number;
  velocidade: number;
  corte_automatico: boolean;
  evento_id: number;
  ip_bridge?: string;
  versao_driver?: string;
  ultimo_heartbeat?: string;
  criado_em: string;
  atualizado_em: string;
}

interface NovaImpressora {
  nome: string;
  tipo: string;
  interface: string;
  endereco: string;
  porta?: number;
  estacao?: string;
  local_fisico?: string;
  densidade: number;
  velocidade: number;
  corte_automatico: boolean;
  evento_id: number;
}

interface StatusImpressoras {
  total_impressoras: number;
  online: number;
  offline: number;
  com_erro: number;
  jobs_pendentes: number;
  jobs_processando: number;
}

const PrinterManagement: React.FC = () => {
  // Estados principais
  const [impressoras, setImpressoras] = useState<Impressora[]>([]);
  const [statusGeral, setStatusGeral] = useState<StatusImpressoras | null>(null);
  const [loading, setLoading] = useState(true);
  const [dialogAberto, setDialogAberto] = useState(false);
  const [impressoraSelecionada, setImpressoraSelecionada] = useState<Impressora | null>(null);
  const [modoEdicao, setModoEdicao] = useState(false);
  const [filtroStatus, setFiltroStatus] = useState<string>('todos');
  const [filtroTipo, setFiltroTipo] = useState<string>('todos');

  const { enqueueSnackbar } = useSnackbar();

  // Estados para formulário
  const [novaImpressora, setNovaImpressora] = useState<NovaImpressora>({
    nome: '',
    tipo: 'TERMICA_80MM',
    interface: 'ETHERNET',
    endereco: '',
    porta: 9100,
    estacao: '',
    local_fisico: '',
    densidade: 8,
    velocidade: 100,
    corte_automatico: true,
    evento_id: 1 // TODO: pegar do contexto
  });

  // Carregar dados iniciais
  useEffect(() => {
    carregarDados();
    const interval = setInterval(carregarStatusGeral, 30000); // Atualizar status a cada 30s
    return () => clearInterval(interval);
  }, []);

  const carregarDados = async () => {
    try {
      setLoading(true);
      await Promise.all([
        carregarImpressoras(),
        carregarStatusGeral()
      ]);
    } catch (error) {
      console.error('Erro ao carregar dados:', error);
      enqueueSnackbar('Erro ao carregar dados das impressoras', { variant: 'error' });
    } finally {
      setLoading(false);
    }
  };

  const carregarImpressoras = async () => {
    try {
      const response = await api.get('/api/printer/impressoras');
      setImpressoras(response.data);
    } catch (error) {
      console.error('Erro ao carregar impressoras:', error);
      throw error;
    }
  };

  const carregarStatusGeral = async () => {
    try {
      const response = await api.get('/api/printer/status');
      setStatusGeral(response.data);
    } catch (error) {
      console.error('Erro ao carregar status geral:', error);
    }
  };

  const handleSalvarImpressora = async () => {
    try {
      if (modoEdicao && impressoraSelecionada) {
        // Atualizar impressora existente
        await api.put(`/api/printer/impressoras/${impressoraSelecionada.id}`, novaImpressora);
        enqueueSnackbar('Impressora atualizada com sucesso', { variant: 'success' });
      } else {
        // Criar nova impressora
        await api.post('/api/printer/impressoras', novaImpressora);
        enqueueSnackbar('Impressora criada com sucesso', { variant: 'success' });
      }
      
      setDialogAberto(false);
      await carregarImpressoras();
      resetarFormulario();
    } catch (error: any) {
      console.error('Erro ao salvar impressora:', error);
      const message = error.response?.data?.detail || 'Erro ao salvar impressora';
      enqueueSnackbar(message, { variant: 'error' });
    }
  };

  const handleEditarImpressora = (impressora: Impressora) => {
    setImpressoraSelecionada(impressora);
    setNovaImpressora({
      nome: impressora.nome,
      tipo: impressora.tipo,
      interface: impressora.interface,
      endereco: impressora.endereco,
      porta: impressora.porta,
      estacao: impressora.estacao || '',
      local_fisico: impressora.local_fisico || '',
      densidade: impressora.densidade,
      velocidade: impressora.velocidade,
      corte_automatico: impressora.corte_automatico,
      evento_id: impressora.evento_id
    });
    setModoEdicao(true);
    setDialogAberto(true);
  };

  const handleDeletarImpressora = async (impressora: Impressora) => {
    if (window.confirm(`Tem certeza que deseja deletar a impressora "${impressora.nome}"?`)) {
      try {
        await api.delete(`/api/printer/impressoras/${impressora.id}`);
        enqueueSnackbar('Impressora deletada com sucesso', { variant: 'success' });
        await carregarImpressoras();
      } catch (error: any) {
        console.error('Erro ao deletar impressora:', error);
        const message = error.response?.data?.detail || 'Erro ao deletar impressora';
        enqueueSnackbar(message, { variant: 'error' });
      }
    }
  };

  const handleTestarImpressora = async (impressora: Impressora) => {
    try {
      await api.post(`/api/printer/impressoras/${impressora.id}/teste`);
      enqueueSnackbar('Teste de impressão enviado', { variant: 'success' });
    } catch (error: any) {
      console.error('Erro ao testar impressora:', error);
      const message = error.response?.data?.detail || 'Erro ao enviar teste';
      enqueueSnackbar(message, { variant: 'error' });
    }
  };

  const resetarFormulario = () => {
    setNovaImpressora({
      nome: '',
      tipo: 'TERMICA_80MM',
      interface: 'ETHERNET',
      endereco: '',
      porta: 9100,
      estacao: '',
      local_fisico: '',
      densidade: 8,
      velocidade: 100,
      corte_automatico: true,
      evento_id: 1
    });
    setImpressoraSelecionada(null);
    setModoEdicao(false);
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'ONLINE':
        return <OnlineIcon color="success" />;
      case 'OFFLINE':
        return <ErrorIcon color="error" />;
      case 'ERRO_PAPEL':
      case 'ERRO_CONEXAO':
        return <ErrorIcon color="error" />;
      case 'MANUTENCAO':
        return <WarningIcon color="warning" />;
      default:
        return <WarningIcon color="disabled" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'ONLINE': return 'success';
      case 'OFFLINE': return 'error';
      case 'ERRO_PAPEL':
      case 'ERRO_CONEXAO': return 'error';
      case 'MANUTENCAO': return 'warning';
      default: return 'default';
    }
  };

  const impressorasFiltradas = impressoras.filter(impressora => {
    const statusMatch = filtroStatus === 'todos' || impressora.status === filtroStatus;
    const tipoMatch = filtroTipo === 'todos' || impressora.tipo === filtroTipo;
    return statusMatch && tipoMatch;
  });

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box p={3}>
      {/* Header com status geral */}
      <Paper elevation={2} sx={{ p: 2, mb: 3 }}>
        <Typography variant="h4" gutterBottom>
          Gerenciamento de Impressoras Térmicas
        </Typography>
        
        {statusGeral && (
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12} sm={6} md={2}>
              <Card>
                <CardContent>
                  <Typography color="textSecondary" gutterBottom>
                    Total
                  </Typography>
                  <Typography variant="h5">
                    {statusGeral.total_impressoras}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} sm={6} md={2}>
              <Card>
                <CardContent>
                  <Typography color="textSecondary" gutterBottom>
                    Online
                  </Typography>
                  <Typography variant="h5" color="success.main">
                    {statusGeral.online}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} sm={6} md={2}>
              <Card>
                <CardContent>
                  <Typography color="textSecondary" gutterBottom>
                    Offline
                  </Typography>
                  <Typography variant="h5" color="error.main">
                    {statusGeral.offline}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} sm={6} md={2}>
              <Card>
                <CardContent>
                  <Typography color="textSecondary" gutterBottom>
                    Com Erro
                  </Typography>
                  <Typography variant="h5" color="warning.main">
                    {statusGeral.com_erro}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} sm={6} md={2}>
              <Card>
                <CardContent>
                  <Typography color="textSecondary" gutterBottom>
                    Jobs Pendentes
                  </Typography>
                  <Typography variant="h5">
                    {statusGeral.jobs_pendentes}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} sm={6} md={2}>
              <Card>
                <CardContent>
                  <Typography color="textSecondary" gutterBottom>
                    Processando
                  </Typography>
                  <Typography variant="h5" color="info.main">
                    {statusGeral.jobs_processando}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        )}
      </Paper>

      {/* Filtros e ações */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Box display="flex" gap={2}>
          <FormControl size="small" sx={{ minWidth: 120 }}>
            <InputLabel>Status</InputLabel>
            <Select
              value={filtroStatus}
              label="Status"
              onChange={(e) => setFiltroStatus(e.target.value)}
            >
              <MenuItem value="todos">Todos</MenuItem>
              <MenuItem value="ONLINE">Online</MenuItem>
              <MenuItem value="OFFLINE">Offline</MenuItem>
              <MenuItem value="ERRO_PAPEL">Erro Papel</MenuItem>
              <MenuItem value="ERRO_CONEXAO">Erro Conexão</MenuItem>
              <MenuItem value="MANUTENCAO">Manutenção</MenuItem>
            </Select>
          </FormControl>

          <FormControl size="small" sx={{ minWidth: 120 }}>
            <InputLabel>Tipo</InputLabel>
            <Select
              value={filtroTipo}
              label="Tipo"
              onChange={(e) => setFiltroTipo(e.target.value)}
            >
              <MenuItem value="todos">Todos</MenuItem>
              <MenuItem value="TERMICA_58MM">Térmica 58mm</MenuItem>
              <MenuItem value="TERMICA_80MM">Térmica 80mm</MenuItem>
              <MenuItem value="MATRICIAL">Matricial</MenuItem>
              <MenuItem value="JATO_TINTA">Jato de Tinta</MenuItem>
            </Select>
          </FormControl>
        </Box>

        <Box display="flex" gap={1}>
          <Button
            variant="outlined"
            startIcon={<RefreshIcon />}
            onClick={carregarDados}
          >
            Atualizar
          </Button>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => {
              resetarFormulario();
              setDialogAberto(true);
            }}
          >
            Nova Impressora
          </Button>
        </Box>
      </Box>

      {/* Lista de impressoras */}
      <Grid container spacing={2}>
        {impressorasFiltradas.map((impressora) => (
          <Grid item xs={12} md={6} lg={4} key={impressora.id}>
            <Card>
              <CardContent>
                <Box display="flex" justifyContent="space-between" alignItems="flex-start" mb={2}>
                  <Typography variant="h6" component="div">
                    {impressora.nome}
                  </Typography>
                  <Box display="flex" alignItems="center" gap={1}>
                    {getStatusIcon(impressora.status)}
                    <Chip
                      label={impressora.status}
                      color={getStatusColor(impressora.status) as any}
                      size="small"
                    />
                  </Box>
                </Box>

                <Typography variant="body2" color="text.secondary" gutterBottom>
                  {impressora.tipo} • {impressora.interface}
                </Typography>

                <Typography variant="body2" gutterBottom>
                  <strong>Endereço:</strong> {impressora.endereco}
                  {impressora.porta && `:${impressora.porta}`}
                </Typography>

                {impressora.estacao && (
                  <Typography variant="body2" gutterBottom>
                    <strong>Estação:</strong> {impressora.estacao}
                  </Typography>
                )}

                {impressora.local_fisico && (
                  <Typography variant="body2" gutterBottom>
                    <strong>Local:</strong> {impressora.local_fisico}
                  </Typography>
                )}

                <Divider sx={{ my: 2 }} />

                <Box display="flex" justifyContent="space-between" alignItems="center">
                  <FormControlLabel
                    control={<Switch checked={impressora.ativo} disabled />}
                    label="Ativa"
                  />
                  
                  <Box>
                    <Tooltip title="Testar Impressora">
                      <IconButton 
                        size="small" 
                        onClick={() => handleTestarImpressora(impressora)}
                        disabled={impressora.status !== 'ONLINE'}
                      >
                        <TestIcon />
                      </IconButton>
                    </Tooltip>
                    <Tooltip title="Editar">
                      <IconButton 
                        size="small" 
                        onClick={() => handleEditarImpressora(impressora)}
                      >
                        <EditIcon />
                      </IconButton>
                    </Tooltip>
                    <Tooltip title="Deletar">
                      <IconButton 
                        size="small" 
                        onClick={() => handleDeletarImpressora(impressora)}
                      >
                        <DeleteIcon />
                      </IconButton>
                    </Tooltip>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      {impressorasFiltradas.length === 0 && (
        <Alert severity="info" sx={{ mt: 2 }}>
          Nenhuma impressora encontrada com os filtros aplicados.
        </Alert>
      )}

      {/* Dialog para criar/editar impressora */}
      <Dialog 
        open={dialogAberto} 
        onClose={() => setDialogAberto(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          {modoEdicao ? 'Editar Impressora' : 'Nova Impressora'}
        </DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Nome da Impressora"
                value={novaImpressora.nome}
                onChange={(e) => setNovaImpressora({ ...novaImpressora, nome: e.target.value })}
                required
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth required>
                <InputLabel>Tipo</InputLabel>
                <Select
                  value={novaImpressora.tipo}
                  label="Tipo"
                  onChange={(e) => setNovaImpressora({ ...novaImpressora, tipo: e.target.value })}
                >
                  <MenuItem value="TERMICA_58MM">Térmica 58mm</MenuItem>
                  <MenuItem value="TERMICA_80MM">Térmica 80mm</MenuItem>
                  <MenuItem value="MATRICIAL">Matricial</MenuItem>
                  <MenuItem value="JATO_TINTA">Jato de Tinta</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth required>
                <InputLabel>Interface</InputLabel>
                <Select
                  value={novaImpressora.interface}
                  label="Interface"
                  onChange={(e) => setNovaImpressora({ ...novaImpressora, interface: e.target.value })}
                >
                  <MenuItem value="USB">USB</MenuItem>
                  <MenuItem value="ETHERNET">Ethernet</MenuItem>
                  <MenuItem value="WIFI">Wi-Fi</MenuItem>
                  <MenuItem value="BLUETOOTH">Bluetooth</MenuItem>
                  <MenuItem value="PARALELA">Paralela</MenuItem>
                  <MenuItem value="SERIAL">Serial</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Endereço"
                value={novaImpressora.endereco}
                onChange={(e) => setNovaImpressora({ ...novaImpressora, endereco: e.target.value })}
                required
                helperText="IP para Ethernet/Wi-Fi, Caminho para USB, MAC para Bluetooth"
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Porta"
                type="number"
                value={novaImpressora.porta || ''}
                onChange={(e) => setNovaImpressora({ ...novaImpressora, porta: e.target.value ? parseInt(e.target.value) : undefined })}
                helperText="Padrão: 9100 para Ethernet"
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Estação/Setor"
                value={novaImpressora.estacao}
                onChange={(e) => setNovaImpressora({ ...novaImpressora, estacao: e.target.value })}
                helperText="Ex: COZINHA, BAR, CAIXA"
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Local Físico"
                value={novaImpressora.local_fisico}
                onChange={(e) => setNovaImpressora({ ...novaImpressora, local_fisico: e.target.value })}
                helperText="Descrição da localização física"
              />
            </Grid>
            <Grid item xs={12} sm={4}>
              <TextField
                fullWidth
                label="Densidade"
                type="number"
                value={novaImpressora.densidade}
                onChange={(e) => setNovaImpressora({ ...novaImpressora, densidade: parseInt(e.target.value) })}
                inputProps={{ min: 1, max: 15 }}
                helperText="1-15 (padrão: 8)"
              />
            </Grid>
            <Grid item xs={12} sm={4}>
              <TextField
                fullWidth
                label="Velocidade"
                type="number"
                value={novaImpressora.velocidade}
                onChange={(e) => setNovaImpressora({ ...novaImpressora, velocidade: parseInt(e.target.value) })}
                inputProps={{ min: 1, max: 200 }}
                helperText="1-200% (padrão: 100)"
              />
            </Grid>
            <Grid item xs={12} sm={4}>
              <FormControlLabel
                control={
                  <Switch
                    checked={novaImpressora.corte_automatico}
                    onChange={(e) => setNovaImpressora({ ...novaImpressora, corte_automatico: e.target.checked })}
                  />
                }
                label="Corte Automático"
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDialogAberto(false)}>
            Cancelar
          </Button>
          <Button 
            onClick={handleSalvarImpressora}
            variant="contained"
            disabled={!novaImpressora.nome || !novaImpressora.endereco}
          >
            {modoEdicao ? 'Atualizar' : 'Criar'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default PrinterManagement;
