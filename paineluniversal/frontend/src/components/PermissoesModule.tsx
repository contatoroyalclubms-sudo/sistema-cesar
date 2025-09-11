import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Card,
  CardHeader,
  CardContent,
  Typography,
  Tab,
  Tabs,
  Button,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  IconButton,
  Alert,
  LinearProgress,
  FormControlLabel,
  Switch,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  Checkbox,
  Tooltip,
  Badge,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Avatar
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Security as SecurityIcon,
  Group as GroupIcon,
  VpnKey as KeyIcon,
  AdminPanelSettings as AdminIcon,
  Assignment as AssignmentIcon,
  History as HistoryIcon,
  Dashboard as DashboardIcon,
  ExpandMore as ExpandMoreIcon,
  Search as SearchIcon,
  CheckCircle as CheckCircleIcon,
  Cancel as CancelIcon,
  Warning as WarningIcon,
  Info as InfoIcon
} from '@mui/icons-material';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import { ptBR } from 'date-fns/locale';
import { 
  permissoesService, 
  Role, 
  Permissao, 
  UsuarioRole, 
  LogAcesso, 
  DashboardPermissoes,
  CreateRoleRequest,
  AssignRoleRequest,
  AssignPermissaoRequest,
  TipoPermissao,
  StatusRole
} from '../services/permissoesService';

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
      id={`permissoes-tabpanel-${index}`}
      aria-labelledby={`permissoes-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
}

export default function PermissoesModule() {
  const [tabValue, setTabValue] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  // Estados do Dashboard
  const [dashboard, setDashboard] = useState<DashboardPermissoes | null>(null);

  // Estados das Roles
  const [roles, setRoles] = useState<Role[]>([]);
  const [openRoleDialog, setOpenRoleDialog] = useState(false);
  const [editingRole, setEditingRole] = useState<Role | null>(null);
  const [newRole, setNewRole] = useState<CreateRoleRequest>({
    nome: '',
    descricao: '',
    nivel_hierarquico: 1,
    ativo: true
  });

  // Estados das Permissões
  const [permissoes, setPermissoes] = useState<Permissao[]>([]);
  const [openPermissaoDialog, setOpenPermissaoDialog] = useState(false);
  const [selectedRole, setSelectedRole] = useState<Role | null>(null);
  const [rolePermissoes, setRolePermissoes] = useState<Permissao[]>([]);

  // Estados dos Usuários
  const [usuarioRoles, setUsuarioRoles] = useState<UsuarioRole[]>([]);
  const [openUsuarioDialog, setOpenUsuarioDialog] = useState(false);
  const [selectedUsuario, setSelectedUsuario] = useState<any>(null);

  // Estados dos Logs
  const [logs, setLogs] = useState<LogAcesso[]>([]);
  const [filtroLogs, setFiltroLogs] = useState({
    usuario_id: '',
    data_inicio: null as Date | null,
    data_fim: null as Date | null,
    sucesso: null as boolean | null
  });

  // Estados de pesquisa
  const [searchRole, setSearchRole] = useState('');
  const [searchUsuario, setSearchUsuario] = useState('');

  useEffect(() => {
    loadInitialData();
  }, []);

  const loadInitialData = async () => {
    try {
      setLoading(true);
      await Promise.all([
        loadDashboard(),
        loadRoles(),
        loadPermissoes(),
        loadUsuarioRoles(),
        loadLogs()
      ]);
    } catch (err) {
      setError('Erro ao carregar dados iniciais');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const loadDashboard = async () => {
    try {
      const data = await permissoesService.getDashboard();
      setDashboard(data);
    } catch (err) {
      console.error('Erro ao carregar dashboard:', err);
    }
  };

  const loadRoles = async () => {
    try {
      const data = await permissoesService.listarRoles();
      setRoles(data);
    } catch (err) {
      console.error('Erro ao carregar roles:', err);
    }
  };

  const loadPermissoes = async () => {
    try {
      const data = await permissoesService.listarPermissoes();
      setPermissoes(data);
    } catch (err) {
      console.error('Erro ao carregar permissões:', err);
    }
  };

  const loadUsuarioRoles = async () => {
    try {
      const data = await permissoesService.listarUsuarioRoles();
      setUsuarioRoles(data);
    } catch (err) {
      console.error('Erro ao carregar usuário roles:', err);
    }
  };

  const loadLogs = async () => {
    try {
      const data = await permissoesService.listarLogs({
        ...filtroLogs,
        data_inicio: filtroLogs.data_inicio ? filtroLogs.data_inicio.toISOString().split('T')[0] : undefined,
        data_fim: filtroLogs.data_fim ? filtroLogs.data_fim.toISOString().split('T')[0] : undefined
      });
      setLogs(data);
    } catch (err) {
      console.error('Erro ao carregar logs:', err);
    }
  };

  const handleCreateRole = async () => {
    try {
      setLoading(true);
      await permissoesService.criarRole(newRole);
      setSuccess('Role criada com sucesso!');
      setOpenRoleDialog(false);
      setNewRole({
        nome: '',
        descricao: '',
        nivel_hierarquico: 1,
        ativo: true
      });
      await loadRoles();
      await loadDashboard();
    } catch (err) {
      setError('Erro ao criar role');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateRole = async () => {
    if (!editingRole) return;
    
    try {
      setLoading(true);
      await permissoesService.atualizarRole(editingRole.id, {
        nome: editingRole.nome,
        descricao: editingRole.descricao,
        nivel_hierarquico: editingRole.nivel_hierarquico,
        ativo: editingRole.ativo
      });
      setSuccess('Role atualizada com sucesso!');
      setEditingRole(null);
      await loadRoles();
      await loadDashboard();
    } catch (err) {
      setError('Erro ao atualizar role');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleAssignPermissaoToRole = async (permissaoId: number) => {
    if (!selectedRole) return;

    try {
      setLoading(true);
      await permissoesService.atribuirPermissaoRole({
        role_id: selectedRole.id,
        permissao_id: permissaoId
      });
      setSuccess('Permissão atribuída com sucesso!');
      await loadRolePermissoes(selectedRole.id);
      await loadDashboard();
    } catch (err) {
      setError('Erro ao atribuir permissão');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleRemovePermissaoFromRole = async (permissaoId: number) => {
    if (!selectedRole) return;

    try {
      setLoading(true);
      await permissoesService.removerPermissaoRole(selectedRole.id, permissaoId);
      setSuccess('Permissão removida com sucesso!');
      await loadRolePermissoes(selectedRole.id);
      await loadDashboard();
    } catch (err) {
      setError('Erro ao remover permissão');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const loadRolePermissoes = async (roleId: number) => {
    try {
      const data = await permissoesService.obterPermissoesRole(roleId);
      setRolePermissoes(data);
    } catch (err) {
      console.error('Erro ao carregar permissões da role:', err);
    }
  };

  const getStatusColor = (status: StatusRole) => {
    switch (status) {
      case 'ativo': return 'success';
      case 'inativo': return 'error';
      case 'suspenso': return 'warning';
      default: return 'default';
    }
  };

  const getTipoPermissaoColor = (tipo: TipoPermissao) => {
    switch (tipo) {
      case 'leitura': return 'info';
      case 'escrita': return 'warning';
      case 'exclusao': return 'error';
      case 'admin': return 'secondary';
      default: return 'default';
    }
  };

  const filteredRoles = roles.filter(role => 
    role.nome.toLowerCase().includes(searchRole.toLowerCase()) ||
    role.descricao?.toLowerCase().includes(searchRole.toLowerCase())
  );

  const renderDashboard = () => (
    <Grid container spacing={3}>
      <Grid item xs={12} md={3}>
        <Card>
          <CardContent>
            <Box display="flex" alignItems="center">
              <Avatar sx={{ bgcolor: 'primary.main', mr: 2 }}>
                <GroupIcon />
              </Avatar>
              <Box>
                <Typography variant="h4">{dashboard?.total_roles || 0}</Typography>
                <Typography color="textSecondary">Total de Roles</Typography>
              </Box>
            </Box>
          </CardContent>
        </Card>
      </Grid>

      <Grid item xs={12} md={3}>
        <Card>
          <CardContent>
            <Box display="flex" alignItems="center">
              <Avatar sx={{ bgcolor: 'secondary.main', mr: 2 }}>
                <KeyIcon />
              </Avatar>
              <Box>
                <Typography variant="h4">{dashboard?.total_permissoes || 0}</Typography>
                <Typography color="textSecondary">Total de Permissões</Typography>
              </Box>
            </Box>
          </CardContent>
        </Card>
      </Grid>

      <Grid item xs={12} md={3}>
        <Card>
          <CardContent>
            <Box display="flex" alignItems="center">
              <Avatar sx={{ bgcolor: 'info.main', mr: 2 }}>
                <AssignmentIcon />
              </Avatar>
              <Box>
                <Typography variant="h4">{dashboard?.usuarios_com_roles || 0}</Typography>
                <Typography color="textSecondary">Usuários com Roles</Typography>
              </Box>
            </Box>
          </CardContent>
        </Card>
      </Grid>

      <Grid item xs={12} md={3}>
        <Card>
          <CardContent>
            <Box display="flex" alignItems="center">
              <Avatar sx={{ bgcolor: 'success.main', mr: 2 }}>
                <HistoryIcon />
              </Avatar>
              <Box>
                <Typography variant="h4">{dashboard?.acessos_ultimo_mes || 0}</Typography>
                <Typography color="textSecondary">Acessos no Mês</Typography>
              </Box>
            </Box>
          </CardContent>
        </Card>
      </Grid>

      {dashboard?.roles_mais_usadas && dashboard.roles_mais_usadas.length > 0 && (
        <Grid item xs={12} md={6}>
          <Card>
            <CardHeader title="Roles Mais Utilizadas" />
            <CardContent>
              <List>
                {dashboard.roles_mais_usadas.map((item, index) => (
                  <ListItem key={index}>
                    <ListItemText
                      primary={item.nome}
                      secondary={`${item.total_usuarios} usuários`}
                    />
                    <Badge badgeContent={item.total_usuarios} color="primary" />
                  </ListItem>
                ))}
              </List>
            </CardContent>
          </Card>
        </Grid>
      )}

      {dashboard?.atividade_recente && dashboard.atividade_recente.length > 0 && (
        <Grid item xs={12} md={6}>
          <Card>
            <CardHeader title="Atividade Recente" />
            <CardContent>
              <List>
                {dashboard.atividade_recente.map((log, index) => (
                  <ListItem key={index}>
                    <ListItemText
                      primary={`${log.acao} - ${log.modulo}`}
                      secondary={`${log.usuario_nome} - ${new Date(log.data_acesso).toLocaleDateString('pt-BR')}`}
                    />
                    <Chip
                      size="small"
                      color={log.sucesso ? 'success' : 'error'}
                      icon={log.sucesso ? <CheckCircleIcon /> : <CancelIcon />}
                      label={log.sucesso ? 'Sucesso' : 'Erro'}
                    />
                  </ListItem>
                ))}
              </List>
            </CardContent>
          </Card>
        </Grid>
      )}
    </Grid>
  );

  const renderRolesManagement = () => (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h5">Gestão de Roles</Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => setOpenRoleDialog(true)}
        >
          Nova Role
        </Button>
      </Box>

      <Box mb={3}>
        <TextField
          fullWidth
          placeholder="Pesquisar roles..."
          value={searchRole}
          onChange={(e) => setSearchRole(e.target.value)}
          InputProps={{
            startAdornment: <SearchIcon color="action" />
          }}
        />
      </Box>

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Nome</TableCell>
              <TableCell>Descrição</TableCell>
              <TableCell>Nível</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Criada em</TableCell>
              <TableCell>Ações</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {filteredRoles.map((role) => (
              <TableRow key={role.id}>
                <TableCell>
                  <Box display="flex" alignItems="center">
                    <SecurityIcon color="primary" sx={{ mr: 1 }} />
                    {role.nome}
                  </Box>
                </TableCell>
                <TableCell>{role.descricao}</TableCell>
                <TableCell>{role.nivel_hierarquico}</TableCell>
                <TableCell>
                  <Chip
                    size="small"
                    color={getStatusColor(role.ativo ? 'ativo' : 'inativo')}
                    label={role.ativo ? 'Ativo' : 'Inativo'}
                  />
                </TableCell>
                <TableCell>
                  {new Date(role.criado_em).toLocaleDateString('pt-BR')}
                </TableCell>
                <TableCell>
                  <Tooltip title="Editar">
                    <IconButton
                      size="small"
                      onClick={() => {
                        setEditingRole(role);
                      }}
                    >
                      <EditIcon />
                    </IconButton>
                  </Tooltip>
                  <Tooltip title="Gerenciar Permissões">
                    <IconButton
                      size="small"
                      onClick={async () => {
                        setSelectedRole(role);
                        await loadRolePermissoes(role.id);
                        setOpenPermissaoDialog(true);
                      }}
                    >
                      <KeyIcon />
                    </IconButton>
                  </Tooltip>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      {/* Dialog para criar/editar role */}
      <Dialog open={openRoleDialog || !!editingRole} onClose={() => {
        setOpenRoleDialog(false);
        setEditingRole(null);
      }}>
        <DialogTitle>
          {editingRole ? 'Editar Role' : 'Nova Role'}
        </DialogTitle>
        <DialogContent>
          <TextField
            fullWidth
            label="Nome"
            margin="normal"
            value={editingRole ? editingRole.nome : newRole.nome}
            onChange={(e) => {
              if (editingRole) {
                setEditingRole({ ...editingRole, nome: e.target.value });
              } else {
                setNewRole({ ...newRole, nome: e.target.value });
              }
            }}
          />
          <TextField
            fullWidth
            label="Descrição"
            margin="normal"
            multiline
            rows={3}
            value={editingRole ? editingRole.descricao : newRole.descricao}
            onChange={(e) => {
              if (editingRole) {
                setEditingRole({ ...editingRole, descricao: e.target.value });
              } else {
                setNewRole({ ...newRole, descricao: e.target.value });
              }
            }}
          />
          <TextField
            fullWidth
            label="Nível Hierárquico"
            type="number"
            margin="normal"
            value={editingRole ? editingRole.nivel_hierarquico : newRole.nivel_hierarquico}
            onChange={(e) => {
              const value = parseInt(e.target.value);
              if (editingRole) {
                setEditingRole({ ...editingRole, nivel_hierarquico: value });
              } else {
                setNewRole({ ...newRole, nivel_hierarquico: value });
              }
            }}
          />
          <FormControlLabel
            control={
              <Switch
                checked={editingRole ? editingRole.ativo : newRole.ativo}
                onChange={(e) => {
                  if (editingRole) {
                    setEditingRole({ ...editingRole, ativo: e.target.checked });
                  } else {
                    setNewRole({ ...newRole, ativo: e.target.checked });
                  }
                }}
              />
            }
            label="Ativo"
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => {
            setOpenRoleDialog(false);
            setEditingRole(null);
          }}>
            Cancelar
          </Button>
          <Button 
            variant="contained" 
            onClick={editingRole ? handleUpdateRole : handleCreateRole}
            disabled={loading}
          >
            {editingRole ? 'Atualizar' : 'Criar'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Dialog para gerenciar permissões da role */}
      <Dialog 
        open={openPermissaoDialog} 
        onClose={() => setOpenPermissaoDialog(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          Permissões da Role: {selectedRole?.nome}
        </DialogTitle>
        <DialogContent>
          <Typography variant="h6" gutterBottom>
            Permissões Atribuídas
          </Typography>
          {rolePermissoes.length > 0 ? (
            <List>
              {rolePermissoes.map((permissao) => (
                <ListItem key={permissao.id}>
                  <ListItemText
                    primary={permissao.nome}
                    secondary={`${permissao.modulo} - ${permissao.descricao}`}
                  />
                  <Chip
                    size="small"
                    color={getTipoPermissaoColor(permissao.tipo)}
                    label={permissao.tipo}
                  />
                  <ListItemSecondaryAction>
                    <IconButton 
                      edge="end" 
                      onClick={() => handleRemovePermissaoFromRole(permissao.id)}
                    >
                      <DeleteIcon />
                    </IconButton>
                  </ListItemSecondaryAction>
                </ListItem>
              ))}
            </List>
          ) : (
            <Alert severity="info">Nenhuma permissão atribuída</Alert>
          )}

          <Typography variant="h6" gutterBottom sx={{ mt: 3 }}>
            Permissões Disponíveis
          </Typography>
          <List>
            {permissoes
              .filter(p => !rolePermissoes.find(rp => rp.id === p.id))
              .map((permissao) => (
                <ListItem key={permissao.id}>
                  <ListItemText
                    primary={permissao.nome}
                    secondary={`${permissao.modulo} - ${permissao.descricao}`}
                  />
                  <Chip
                    size="small"
                    color={getTipoPermissaoColor(permissao.tipo)}
                    label={permissao.tipo}
                  />
                  <ListItemSecondaryAction>
                    <IconButton 
                      edge="end" 
                      onClick={() => handleAssignPermissaoToRole(permissao.id)}
                    >
                      <AddIcon />
                    </IconButton>
                  </ListItemSecondaryAction>
                </ListItem>
              ))}
          </List>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenPermissaoDialog(false)}>
            Fechar
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );

  const renderUsuarioRoles = () => (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h5">Usuários e Roles</Typography>
        <Button
          variant="contained"
          startIcon={<AssignmentIcon />}
          onClick={() => setOpenUsuarioDialog(true)}
        >
          Atribuir Role
        </Button>
      </Box>

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Usuário</TableCell>
              <TableCell>Role</TableCell>
              <TableCell>Atribuído em</TableCell>
              <TableCell>Ações</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {usuarioRoles.map((usuarioRole) => (
              <TableRow key={usuarioRole.id}>
                <TableCell>{usuarioRole.usuario_nome}</TableCell>
                <TableCell>
                  <Chip
                    color="primary"
                    label={usuarioRole.role_nome}
                    icon={<SecurityIcon />}
                  />
                </TableCell>
                <TableCell>
                  {new Date(usuarioRole.atribuido_em).toLocaleDateString('pt-BR')}
                </TableCell>
                <TableCell>
                  <Tooltip title="Remover Role">
                    <IconButton
                      size="small"
                      color="error"
                      onClick={async () => {
                        try {
                          setLoading(true);
                          await permissoesService.removerRoleUsuario(usuarioRole.usuario_id, usuarioRole.role_id);
                          setSuccess('Role removida do usuário com sucesso!');
                          await loadUsuarioRoles();
                          await loadDashboard();
                        } catch (err) {
                          setError('Erro ao remover role do usuário');
                          console.error(err);
                        } finally {
                          setLoading(false);
                        }
                      }}
                    >
                      <DeleteIcon />
                    </IconButton>
                  </Tooltip>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );

  const renderLogs = () => (
    <Box>
      <Typography variant="h5" gutterBottom>
        Logs de Acesso
      </Typography>

      {/* Filtros */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Grid container spacing={2}>
            <Grid item xs={12} md={3}>
              <TextField
                fullWidth
                label="ID do Usuário"
                value={filtroLogs.usuario_id}
                onChange={(e) => setFiltroLogs({ ...filtroLogs, usuario_id: e.target.value })}
              />
            </Grid>
            <Grid item xs={12} md={3}>
              <LocalizationProvider dateAdapter={AdapterDateFns} adapterLocale={ptBR}>
                <DatePicker
                  label="Data Início"
                  value={filtroLogs.data_inicio}
                  onChange={(date) => setFiltroLogs({ ...filtroLogs, data_inicio: date })}
                  slotProps={{ textField: { fullWidth: true } }}
                />
              </LocalizationProvider>
            </Grid>
            <Grid item xs={12} md={3}>
              <LocalizationProvider dateAdapter={AdapterDateFns} adapterLocale={ptBR}>
                <DatePicker
                  label="Data Fim"
                  value={filtroLogs.data_fim}
                  onChange={(date) => setFiltroLogs({ ...filtroLogs, data_fim: date })}
                  slotProps={{ textField: { fullWidth: true } }}
                />
              </LocalizationProvider>
            </Grid>
            <Grid item xs={12} md={3}>
              <FormControl fullWidth>
                <InputLabel>Status</InputLabel>
                <Select
                  value={filtroLogs.sucesso === null ? '' : filtroLogs.sucesso.toString()}
                  onChange={(e) => {
                    const value = e.target.value;
                    setFiltroLogs({ 
                      ...filtroLogs, 
                      sucesso: value === '' ? null : value === 'true' 
                    });
                  }}
                >
                  <MenuItem value="">Todos</MenuItem>
                  <MenuItem value="true">Sucesso</MenuItem>
                  <MenuItem value="false">Erro</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12}>
              <Button
                variant="contained"
                onClick={loadLogs}
                startIcon={<SearchIcon />}
              >
                Filtrar
              </Button>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Data/Hora</TableCell>
              <TableCell>Usuário</TableCell>
              <TableCell>Módulo</TableCell>
              <TableCell>Ação</TableCell>
              <TableCell>IP</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Detalhes</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {logs.map((log) => (
              <TableRow key={log.id}>
                <TableCell>
                  {new Date(log.data_acesso).toLocaleString('pt-BR')}
                </TableCell>
                <TableCell>{log.usuario_nome}</TableCell>
                <TableCell>{log.modulo}</TableCell>
                <TableCell>{log.acao}</TableCell>
                <TableCell>{log.ip_address}</TableCell>
                <TableCell>
                  <Chip
                    size="small"
                    color={log.sucesso ? 'success' : 'error'}
                    icon={log.sucesso ? <CheckCircleIcon /> : <CancelIcon />}
                    label={log.sucesso ? 'Sucesso' : 'Erro'}
                  />
                </TableCell>
                <TableCell>
                  {log.detalhes && (
                    <Tooltip title={log.detalhes}>
                      <IconButton size="small">
                        <InfoIcon />
                      </IconButton>
                    </Tooltip>
                  )}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );

  return (
    <LocalizationProvider dateAdapter={AdapterDateFns} adapterLocale={ptBR}>
      <Box sx={{ width: '100%' }}>
        {loading && <LinearProgress />}
        
        {error && (
          <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
            {error}
          </Alert>
        )}
        
        {success && (
          <Alert severity="success" sx={{ mb: 2 }} onClose={() => setSuccess(null)}>
            {success}
          </Alert>
        )}

        <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
          <Tabs value={tabValue} onChange={(_, newValue) => setTabValue(newValue)}>
            <Tab 
              label="Dashboard" 
              icon={<DashboardIcon />}
              iconPosition="start"
            />
            <Tab 
              label="Roles" 
              icon={<GroupIcon />}
              iconPosition="start"
            />
            <Tab 
              label="Usuários" 
              icon={<AssignmentIcon />}
              iconPosition="start"
            />
            <Tab 
              label="Logs" 
              icon={<HistoryIcon />}
              iconPosition="start"
            />
          </Tabs>
        </Box>

        <TabPanel value={tabValue} index={0}>
          {renderDashboard()}
        </TabPanel>

        <TabPanel value={tabValue} index={1}>
          {renderRolesManagement()}
        </TabPanel>

        <TabPanel value={tabValue} index={2}>
          {renderUsuarioRoles()}
        </TabPanel>

        <TabPanel value={tabValue} index={3}>
          {renderLogs()}
        </TabPanel>
      </Box>
    </LocalizationProvider>
  );
}
