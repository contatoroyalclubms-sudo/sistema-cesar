import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Tabs,
  Tab,
  Grid,
  Alert,
  Chip,
  Button,
  IconButton,
  TextField,
  MenuItem,
  FormControl,
  InputLabel,
  Select,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  CircularProgress,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Tooltip,
  Badge,
  LinearProgress
} from '@mui/material';
import {
  Inventory,
  TrendingUp,
  TrendingDown,
  Warning,
  Error,
  CheckCircle,
  Add,
  Refresh,
  FilterList,
  Search,
  Assessment,
  ShoppingCart,
  LocalShipping,
  Archive,
  Edit,
  Delete,
  Visibility
} from '@mui/icons-material';
import { format } from 'date-fns';
import { ptBR } from 'date-fns/locale';

import {
  estoqueService,
  EstoqueProduto,
  LocalEstoque,
  MovimentacaoEstoque,
  AlertaEstoque,
  DashboardEstoque,
  SugestaoCompra,
  formatarQuantidade,
  formatarValor,
  obterCorStatusEstoque,
  obterTextoStatusEstoque,
  formatarDataMovimentacao,
  obterIconeMovimentacao,
  tiposMovimentacao,
  tiposLocal,
  metodosControle
} from '../services/estoqueService';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel({ children, value, index }: TabPanelProps) {
  return (
    <div role="tabpanel" hidden={value !== index}>
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
}

export default function EstoqueModule() {
  // ================================================================================
  // ESTADOS PRINCIPAIS
  // ================================================================================
  
  const [tabAtual, setTabAtual] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  // Estados do Dashboard
  const [dashboardData, setDashboardData] = useState<DashboardEstoque | null>(null);
  const [alertas, setAlertas] = useState<AlertaEstoque | null>(null);
  
  // Estados das Posições de Estoque
  const [posicoes, setPosicoes] = useState<EstoqueProduto[]>([]);
  const [totalPosicoes, setTotalPosicoes] = useState(0);
  const [paginaPosicoes, setPaginaPosicoes] = useState(1);
  
  // Estados das Movimentações
  const [movimentacoes, setMovimentacoes] = useState<MovimentacaoEstoque[]>([]);
  const [totalMovimentacoes, setTotalMovimentacoes] = useState(0);
  const [paginaMovimentacoes, setPaginaMovimentacoes] = useState(1);
  
  // Estados dos Locais
  const [locais, setLocais] = useState<LocalEstoque[]>([]);
  const [localSelecionado, setLocalSelecionado] = useState<number | ''>('');
  
  // Estados de Filtros
  const [filtroStatus, setFiltroStatus] = useState<string>('todos');
  const [filtroCategoria, setFiltroCategoria] = useState<string>('');
  const [termoBusca, setTermoBusca] = useState('');
  
  // Estados dos Modais
  const [modalMovimentacao, setModalMovimentacao] = useState(false);
  const [modalLocal, setModalLocal] = useState(false);
  const [modalDetalhes, setModalDetalhes] = useState(false);
  const [itemSelecionado, setItemSelecionado] = useState<any>(null);
  
  // Dados da nova movimentação
  const [novaMovimentacao, setNovaMovimentacao] = useState({
    produto_id: '',
    local_id: '',
    tipo_movimentacao: '',
    quantidade: '',
    valor_unitario: '',
    numero_documento: '',
    observacoes: ''
  });
  
  // Dados do novo local
  const [novoLocal, setNovoLocal] = useState({
    nome: '',
    descricao: '',
    tipo_local: 'deposito',
    endereco: '',
    responsavel_id: '',
    permite_venda: false,
    permite_compra: true,
    permite_transferencia: true
  });

  // ================================================================================
  // EFEITOS
  // ================================================================================
  
  useEffect(() => {
    carregarDadosIniciais();
  }, []);

  useEffect(() => {
    if (tabAtual === 0) {
      carregarDashboard();
    } else if (tabAtual === 1) {
      carregarPosicoes();
    } else if (tabAtual === 2) {
      carregarMovimentacoes();
    } else if (tabAtual === 3) {
      carregarLocais();
    }
  }, [tabAtual, localSelecionado]);

  // ================================================================================
  // FUNÇÕES DE CARREGAMENTO
  // ================================================================================
  
  const carregarDadosIniciais = async () => {
    try {
      setLoading(true);
      const locaisData = await estoqueService.listarLocaisEstoque();
      setLocais(locaisData);
      
      if (locaisData.length > 0) {
        setLocalSelecionado(locaisData[0].id);
      }
    } catch (err) {
      setError('Erro ao carregar dados iniciais');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const carregarDashboard = async () => {
    if (!localSelecionado) return;
    
    try {
      setLoading(true);
      const [dashboardResult, alertasResult] = await Promise.all([
        estoqueService.obterDashboardEstoque(Number(localSelecionado)),
        estoqueService.obterAlertasEstoque(Number(localSelecionado))
      ]);
      
      setDashboardData(dashboardResult);
      setAlertas(alertasResult);
    } catch (err) {
      setError('Erro ao carregar dashboard');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const carregarPosicoes = async () => {
    if (!localSelecionado) return;
    
    try {
      setLoading(true);
      const filtros = {
        local_id: Number(localSelecionado),
        status: filtroStatus !== 'todos' ? filtroStatus : undefined,
        page: paginaPosicoes,
        size: 20
      };
      
      const result = await estoqueService.obterPosicaoEstoque(filtros);
      setPosicoes(result.itens);
      setTotalPosicoes(result.total);
    } catch (err) {
      setError('Erro ao carregar posições de estoque');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const carregarMovimentacoes = async () => {
    if (!localSelecionado) return;
    
    try {
      setLoading(true);
      const filtros = {
        local_id: Number(localSelecionado),
        page: paginaMovimentacoes,
        size: 20
      };
      
      const result = await estoqueService.listarMovimentacoes(filtros);
      setMovimentacoes(result.itens);
      setTotalMovimentacoes(result.total);
    } catch (err) {
      setError('Erro ao carregar movimentações');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const carregarLocais = async () => {
    try {
      setLoading(true);
      const result = await estoqueService.listarLocaisEstoque();
      setLocais(result);
    } catch (err) {
      setError('Erro ao carregar locais');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  // ================================================================================
  // FUNÇÕES DE AÇÕES
  // ================================================================================
  
  const criarMovimentacao = async () => {
    try {
      setLoading(true);
      await estoqueService.criarMovimentacao({
        produto_id: Number(novaMovimentacao.produto_id),
        local_id: Number(novaMovimentacao.local_id),
        tipo_movimentacao: novaMovimentacao.tipo_movimentacao,
        quantidade: Number(novaMovimentacao.quantidade),
        valor_unitario: novaMovimentacao.valor_unitario ? Number(novaMovimentacao.valor_unitario) : undefined,
        numero_documento: novaMovimentacao.numero_documento || undefined,
        observacoes: novaMovimentacao.observacoes || undefined
      });
      
      setModalMovimentacao(false);
      setNovaMovimentacao({
        produto_id: '',
        local_id: '',
        tipo_movimentacao: '',
        quantidade: '',
        valor_unitario: '',
        numero_documento: '',
        observacoes: ''
      });
      
      if (tabAtual === 1) carregarPosicoes();
      else if (tabAtual === 2) carregarMovimentacoes();
      else carregarDashboard();
      
    } catch (err) {
      setError('Erro ao criar movimentação');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const criarLocal = async () => {
    try {
      setLoading(true);
      await estoqueService.criarLocalEstoque(novoLocal);
      
      setModalLocal(false);
      setNovoLocal({
        nome: '',
        descricao: '',
        tipo_local: 'deposito',
        endereco: '',
        responsavel_id: '',
        permite_venda: false,
        permite_compra: true,
        permite_transferencia: true
      });
      
      carregarLocais();
      
    } catch (err) {
      setError('Erro ao criar local');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const atualizarEstatisticas = async () => {
    try {
      setLoading(true);
      await estoqueService.atualizarEstatisticasEstoque();
      
      if (tabAtual === 0) carregarDashboard();
      else if (tabAtual === 1) carregarPosicoes();
      
    } catch (err) {
      setError('Erro ao atualizar estatísticas');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  // ================================================================================
  // COMPONENTES DE RENDERIZAÇÃO
  // ================================================================================

  const renderDashboard = () => (
    <Grid container spacing={3}>
      {/* KPIs Principais */}
      <Grid item xs={12} sm={6} md={3}>
        <Card>
          <CardContent sx={{ textAlign: 'center' }}>
            <Inventory sx={{ fontSize: 40, color: 'primary.main', mb: 1 }} />
            <Typography variant="h6" color="textSecondary">
              Valor Total
            </Typography>
            <Typography variant="h4" color="primary">
              {dashboardData ? formatarValor(dashboardData.valor_total_estoque) : '-'}
            </Typography>
          </CardContent>
        </Card>
      </Grid>

      <Grid item xs={12} sm={6} md={3}>
        <Card>
          <CardContent sx={{ textAlign: 'center' }}>
            <Assessment sx={{ fontSize: 40, color: 'success.main', mb: 1 }} />
            <Typography variant="h6" color="textSecondary">
              Total Produtos
            </Typography>
            <Typography variant="h4" color="success.main">
              {dashboardData?.quantidade_total_produtos || 0}
            </Typography>
          </CardContent>
        </Card>
      </Grid>

      <Grid item xs={12} sm={6} md={3}>
        <Card>
          <CardContent sx={{ textAlign: 'center' }}>
            <Warning sx={{ fontSize: 40, color: 'warning.main', mb: 1 }} />
            <Typography variant="h6" color="textSecondary">
              Estoque Baixo
            </Typography>
            <Typography variant="h4" color="warning.main">
              {dashboardData?.produtos_com_estoque_baixo || 0}
            </Typography>
          </CardContent>
        </Card>
      </Grid>

      <Grid item xs={12} sm={6} md={3}>
        <Card>
          <CardContent sx={{ textAlign: 'center' }}>
            <Error sx={{ fontSize: 40, color: 'error.main', mb: 1 }} />
            <Typography variant="h6" color="textSecondary">
              Sem Estoque
            </Typography>
            <Typography variant="h4" color="error.main">
              {dashboardData?.produtos_sem_estoque || 0}
            </Typography>
          </CardContent>
        </Card>
      </Grid>

      {/* Alertas */}
      {alertas && (
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Alertas de Estoque
              </Typography>
              
              {alertas.estoque_zerado.length > 0 && (
                <Alert severity="error" sx={{ mb: 2 }}>
                  <Typography variant="subtitle2">
                    {alertas.estoque_zerado.length} produtos sem estoque
                  </Typography>
                  {alertas.estoque_zerado.slice(0, 3).map((item, index) => (
                    <Typography key={index} variant="body2">
                      • {item.produto_nome}
                    </Typography>
                  ))}
                  {alertas.estoque_zerado.length > 3 && (
                    <Typography variant="body2">
                      ... e mais {alertas.estoque_zerado.length - 3} produtos
                    </Typography>
                  )}
                </Alert>
              )}

              {alertas.estoque_baixo.length > 0 && (
                <Alert severity="warning" sx={{ mb: 2 }}>
                  <Typography variant="subtitle2">
                    {alertas.estoque_baixo.length} produtos com estoque baixo
                  </Typography>
                  {alertas.estoque_baixo.slice(0, 3).map((item, index) => (
                    <Typography key={index} variant="body2">
                      • {item.produto_nome}: {formatarQuantidade(item.quantidade_atual)} (mín: {formatarQuantidade(item.estoque_minimo)})
                    </Typography>
                  ))}
                  {alertas.estoque_baixo.length > 3 && (
                    <Typography variant="body2">
                      ... e mais {alertas.estoque_baixo.length - 3} produtos
                    </Typography>
                  )}
                </Alert>
              )}

              {alertas.estoque_alto.length > 0 && (
                <Alert severity="info">
                  <Typography variant="subtitle2">
                    {alertas.estoque_alto.length} produtos com estoque alto
                  </Typography>
                  {alertas.estoque_alto.slice(0, 3).map((item, index) => (
                    <Typography key={index} variant="body2">
                      • {item.produto_nome}: {formatarQuantidade(item.quantidade_atual)} (máx: {formatarQuantidade(item.estoque_maximo)})
                    </Typography>
                  ))}
                  {alertas.estoque_alto.length > 3 && (
                    <Typography variant="body2">
                      ... e mais {alertas.estoque_alto.length - 3} produtos
                    </Typography>
                  )}
                </Alert>
              )}

              {alertas.estoque_zerado.length === 0 && 
               alertas.estoque_baixo.length === 0 && 
               alertas.estoque_alto.length === 0 && (
                <Alert severity="success">
                  <Typography variant="body1">
                    Não há alertas críticos de estoque no momento.
                  </Typography>
                </Alert>
              )}
            </CardContent>
          </Card>
        </Grid>
      )}

      {/* Movimentações Recentes */}
      <Grid item xs={12}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Movimentações Recentes
            </Typography>
            <TableContainer>
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell>Data</TableCell>
                    <TableCell>Produto</TableCell>
                    <TableCell>Tipo</TableCell>
                    <TableCell align="right">Quantidade</TableCell>
                    <TableCell align="right">Valor</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {dashboardData?.movimentacoes_recentes?.slice(0, 5).map((mov) => (
                    <TableRow key={mov.id}>
                      <TableCell>
                        {formatarDataMovimentacao(mov.data_movimento)}
                      </TableCell>
                      <TableCell>{mov.produto?.nome}</TableCell>
                      <TableCell>
                        <Chip
                          size="small"
                          label={obterIconeMovimentacao(mov.tipo_movimentacao) + ' ' + mov.tipo_movimentacao.replace('_', ' ')}
                          color={mov.tipo_movimentacao.includes('entrada') ? 'success' : 'warning'}
                        />
                      </TableCell>
                      <TableCell align="right">
                        {formatarQuantidade(mov.quantidade)}
                      </TableCell>
                      <TableCell align="right">
                        {mov.valor_total ? formatarValor(mov.valor_total) : '-'}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  );

  const renderPosicoes = () => (
    <Box>
      {/* Filtros */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Grid container spacing={2} alignItems="center">
            <Grid item xs={12} sm={6} md={3}>
              <FormControl fullWidth size="small">
                <InputLabel>Status</InputLabel>
                <Select
                  value={filtroStatus}
                  onChange={(e) => setFiltroStatus(e.target.value)}
                  label="Status"
                >
                  <MenuItem value="todos">Todos</MenuItem>
                  <MenuItem value="com_estoque">Com Estoque</MenuItem>
                  <MenuItem value="estoque_baixo">Estoque Baixo</MenuItem>
                  <MenuItem value="sem_estoque">Sem Estoque</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <TextField
                fullWidth
                size="small"
                label="Buscar produto"
                value={termoBusca}
                onChange={(e) => setTermoBusca(e.target.value)}
                InputProps={{
                  startAdornment: <Search />
                }}
              />
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Button
                variant="outlined"
                onClick={carregarPosicoes}
                startIcon={<FilterList />}
                fullWidth
              >
                Filtrar
              </Button>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Button
                variant="contained"
                onClick={() => setModalMovimentacao(true)}
                startIcon={<Add />}
                fullWidth
              >
                Nova Movimentação
              </Button>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Tabela de Posições */}
      <Card>
        <CardContent>
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Produto</TableCell>
                  <TableCell align="right">Disponível</TableCell>
                  <TableCell align="right">Reservado</TableCell>
                  <TableCell align="right">Total</TableCell>
                  <TableCell align="center">Status</TableCell>
                  <TableCell align="right">Custo Médio</TableCell>
                  <TableCell align="right">Giro</TableCell>
                  <TableCell align="center">Ações</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {posicoes.map((posicao) => (
                  <TableRow key={`${posicao.produto_id}-${posicao.local_id}`}>
                    <TableCell>
                      <Box>
                        <Typography variant="subtitle2">
                          {posicao.produto?.nome}
                        </Typography>
                        <Typography variant="caption" color="textSecondary">
                          {posicao.produto?.codigo}
                        </Typography>
                      </Box>
                    </TableCell>
                    <TableCell align="right">
                      {formatarQuantidade(posicao.quantidade_disponivel, posicao.produto?.unidade_medida)}
                    </TableCell>
                    <TableCell align="right">
                      {formatarQuantidade(posicao.quantidade_reservada, posicao.produto?.unidade_medida)}
                    </TableCell>
                    <TableCell align="right">
                      <Typography variant="subtitle2">
                        {formatarQuantidade(posicao.quantidade_atual, posicao.produto?.unidade_medida)}
                      </Typography>
                    </TableCell>
                    <TableCell align="center">
                      <Chip
                        size="small"
                        label={obterTextoStatusEstoque(posicao)}
                        color={obterCorStatusEstoque(posicao) as any}
                      />
                    </TableCell>
                    <TableCell align="right">
                      {formatarValor(posicao.custo_medio)}
                    </TableCell>
                    <TableCell align="right">
                      <Tooltip title={`${posicao.cobertura_dias} dias de cobertura`}>
                        <Chip
                          size="small"
                          label={`${posicao.giro_estoque.toFixed(1)}x`}
                          color={posicao.giro_estoque >= 3 ? 'success' : posicao.giro_estoque >= 1 ? 'warning' : 'error'}
                        />
                      </Tooltip>
                    </TableCell>
                    <TableCell align="center">
                      <IconButton
                        size="small"
                        onClick={() => {
                          setItemSelecionado(posicao);
                          setModalDetalhes(true);
                        }}
                      >
                        <Visibility />
                      </IconButton>
                      <IconButton size="small">
                        <Edit />
                      </IconButton>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
          
          {loading && <LinearProgress />}
        </CardContent>
      </Card>
    </Box>
  );

  const renderMovimentacoes = () => (
    <Box>
      {/* Cabeçalho */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h5">Movimentações de Estoque</Typography>
        <Button
          variant="contained"
          onClick={() => setModalMovimentacao(true)}
          startIcon={<Add />}
        >
          Nova Movimentação
        </Button>
      </Box>

      {/* Tabela de Movimentações */}
      <Card>
        <CardContent>
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Data/Hora</TableCell>
                  <TableCell>Produto</TableCell>
                  <TableCell>Tipo</TableCell>
                  <TableCell align="right">Quantidade</TableCell>
                  <TableCell align="right">Valor Unit.</TableCell>
                  <TableCell align="right">Saldo Anterior</TableCell>
                  <TableCell align="right">Saldo Atual</TableCell>
                  <TableCell>Documento</TableCell>
                  <TableCell align="center">Ações</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {movimentacoes.map((mov) => (
                  <TableRow key={mov.id}>
                    <TableCell>
                      <Typography variant="body2">
                        {formatarDataMovimentacao(mov.data_movimento)}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Box>
                        <Typography variant="subtitle2">
                          {mov.produto?.nome}
                        </Typography>
                        <Typography variant="caption" color="textSecondary">
                          {mov.produto?.codigo}
                        </Typography>
                      </Box>
                    </TableCell>
                    <TableCell>
                      <Chip
                        size="small"
                        label={obterIconeMovimentacao(mov.tipo_movimentacao) + ' ' + mov.tipo_movimentacao.replace('_', ' ')}
                        color={mov.tipo_movimentacao.includes('entrada') ? 'success' : 'warning'}
                      />
                    </TableCell>
                    <TableCell align="right">
                      {formatarQuantidade(mov.quantidade, mov.produto?.unidade_medida)}
                    </TableCell>
                    <TableCell align="right">
                      {mov.valor_unitario ? formatarValor(mov.valor_unitario) : '-'}
                    </TableCell>
                    <TableCell align="right">
                      {formatarQuantidade(mov.saldo_anterior, mov.produto?.unidade_medida)}
                    </TableCell>
                    <TableCell align="right">
                      <Typography variant="subtitle2">
                        {formatarQuantidade(mov.saldo_atual, mov.produto?.unidade_medida)}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Typography variant="caption">
                        {mov.numero_documento || '-'}
                      </Typography>
                    </TableCell>
                    <TableCell align="center">
                      <IconButton
                        size="small"
                        onClick={() => {
                          setItemSelecionado(mov);
                          setModalDetalhes(true);
                        }}
                      >
                        <Visibility />
                      </IconButton>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
          
          {loading && <LinearProgress />}
        </CardContent>
      </Card>
    </Box>
  );

  const renderLocais = () => (
    <Box>
      {/* Cabeçalho */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h5">Locais de Estoque</Typography>
        <Button
          variant="contained"
          onClick={() => setModalLocal(true)}
          startIcon={<Add />}
        >
          Novo Local
        </Button>
      </Box>

      {/* Grid de Locais */}
      <Grid container spacing={3}>
        {locais.map((local) => (
          <Grid item xs={12} sm={6} md={4} key={local.id}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
                  <Typography variant="h6">{local.nome}</Typography>
                  <Chip
                    size="small"
                    label={tiposLocal.find(t => t.value === local.tipo_local)?.label || local.tipo_local}
                    color="primary"
                  />
                </Box>
                
                {local.descricao && (
                  <Typography variant="body2" color="textSecondary" sx={{ mb: 2 }}>
                    {local.descricao}
                  </Typography>
                )}
                
                <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
                  {local.permite_venda && (
                    <Chip size="small" label="Venda" color="success" />
                  )}
                  {local.permite_compra && (
                    <Chip size="small" label="Compra" color="info" />
                  )}
                  {local.permite_transferencia && (
                    <Chip size="small" label="Transferência" color="warning" />
                  )}
                </Box>
                
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <Chip
                    size="small"
                    label={local.ativo ? 'Ativo' : 'Inativo'}
                    color={local.ativo ? 'success' : 'default'}
                  />
                  <Box>
                    <IconButton size="small">
                      <Edit />
                    </IconButton>
                    <IconButton size="small" color="error">
                      <Delete />
                    </IconButton>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Box>
  );

  // ================================================================================
  // MODAL DE NOVA MOVIMENTAÇÃO
  // ================================================================================
  
  const renderModalMovimentacao = () => (
    <Dialog open={modalMovimentacao} onClose={() => setModalMovimentacao(false)} maxWidth="md" fullWidth>
      <DialogTitle>Nova Movimentação de Estoque</DialogTitle>
      <DialogContent>
        <Grid container spacing={2} sx={{ mt: 1 }}>
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="Produto ID"
              value={novaMovimentacao.produto_id}
              onChange={(e) => setNovaMovimentacao(prev => ({ ...prev, produto_id: e.target.value }))}
              type="number"
            />
          </Grid>
          <Grid item xs={12} md={6}>
            <FormControl fullWidth>
              <InputLabel>Local</InputLabel>
              <Select
                value={novaMovimentacao.local_id}
                onChange={(e) => setNovaMovimentacao(prev => ({ ...prev, local_id: e.target.value }))}
                label="Local"
              >
                {locais.map((local) => (
                  <MenuItem key={local.id} value={local.id}>
                    {local.nome}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} md={6}>
            <FormControl fullWidth>
              <InputLabel>Tipo de Movimentação</InputLabel>
              <Select
                value={novaMovimentacao.tipo_movimentacao}
                onChange={(e) => setNovaMovimentacao(prev => ({ ...prev, tipo_movimentacao: e.target.value }))}
                label="Tipo de Movimentação"
              >
                {tiposMovimentacao.map((tipo) => (
                  <MenuItem key={tipo.value} value={tipo.value}>
                    {tipo.icon} {tipo.label}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="Quantidade"
              value={novaMovimentacao.quantidade}
              onChange={(e) => setNovaMovimentacao(prev => ({ ...prev, quantidade: e.target.value }))}
              type="number"
              inputProps={{ step: 0.001 }}
            />
          </Grid>
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="Valor Unitário"
              value={novaMovimentacao.valor_unitario}
              onChange={(e) => setNovaMovimentacao(prev => ({ ...prev, valor_unitario: e.target.value }))}
              type="number"
              inputProps={{ step: 0.01 }}
            />
          </Grid>
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="Número do Documento"
              value={novaMovimentacao.numero_documento}
              onChange={(e) => setNovaMovimentacao(prev => ({ ...prev, numero_documento: e.target.value }))}
            />
          </Grid>
          <Grid item xs={12}>
            <TextField
              fullWidth
              label="Observações"
              value={novaMovimentacao.observacoes}
              onChange={(e) => setNovaMovimentacao(prev => ({ ...prev, observacoes: e.target.value }))}
              multiline
              rows={3}
            />
          </Grid>
        </Grid>
      </DialogContent>
      <DialogActions>
        <Button onClick={() => setModalMovimentacao(false)}>Cancelar</Button>
        <Button
          onClick={criarMovimentacao}
          variant="contained"
          disabled={!novaMovimentacao.produto_id || !novaMovimentacao.local_id || !novaMovimentacao.tipo_movimentacao || !novaMovimentacao.quantidade}
        >
          Criar Movimentação
        </Button>
      </DialogActions>
    </Dialog>
  );

  // ================================================================================
  // MODAL DE NOVO LOCAL
  // ================================================================================
  
  const renderModalLocal = () => (
    <Dialog open={modalLocal} onClose={() => setModalLocal(false)} maxWidth="md" fullWidth>
      <DialogTitle>Novo Local de Estoque</DialogTitle>
      <DialogContent>
        <Grid container spacing={2} sx={{ mt: 1 }}>
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="Nome"
              value={novoLocal.nome}
              onChange={(e) => setNovoLocal(prev => ({ ...prev, nome: e.target.value }))}
            />
          </Grid>
          <Grid item xs={12} md={6}>
            <FormControl fullWidth>
              <InputLabel>Tipo de Local</InputLabel>
              <Select
                value={novoLocal.tipo_local}
                onChange={(e) => setNovoLocal(prev => ({ ...prev, tipo_local: e.target.value }))}
                label="Tipo de Local"
              >
                {tiposLocal.map((tipo) => (
                  <MenuItem key={tipo.value} value={tipo.value}>
                    {tipo.label}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12}>
            <TextField
              fullWidth
              label="Descrição"
              value={novoLocal.descricao}
              onChange={(e) => setNovoLocal(prev => ({ ...prev, descricao: e.target.value }))}
              multiline
              rows={2}
            />
          </Grid>
          <Grid item xs={12}>
            <TextField
              fullWidth
              label="Endereço"
              value={novoLocal.endereco}
              onChange={(e) => setNovoLocal(prev => ({ ...prev, endereco: e.target.value }))}
            />
          </Grid>
          <Grid item xs={12} md={4}>
            <FormControl fullWidth>
              <label>
                <input
                  type="checkbox"
                  checked={novoLocal.permite_venda}
                  onChange={(e) => setNovoLocal(prev => ({ ...prev, permite_venda: e.target.checked }))}
                />
                Permite Venda
              </label>
            </FormControl>
          </Grid>
          <Grid item xs={12} md={4}>
            <FormControl fullWidth>
              <label>
                <input
                  type="checkbox"
                  checked={novoLocal.permite_compra}
                  onChange={(e) => setNovoLocal(prev => ({ ...prev, permite_compra: e.target.checked }))}
                />
                Permite Compra
              </label>
            </FormControl>
          </Grid>
          <Grid item xs={12} md={4}>
            <FormControl fullWidth>
              <label>
                <input
                  type="checkbox"
                  checked={novoLocal.permite_transferencia}
                  onChange={(e) => setNovoLocal(prev => ({ ...prev, permite_transferencia: e.target.checked }))}
                />
                Permite Transferência
              </label>
            </FormControl>
          </Grid>
        </Grid>
      </DialogContent>
      <DialogActions>
        <Button onClick={() => setModalLocal(false)}>Cancelar</Button>
        <Button
          onClick={criarLocal}
          variant="contained"
          disabled={!novoLocal.nome || !novoLocal.tipo_local}
        >
          Criar Local
        </Button>
      </DialogActions>
    </Dialog>
  );

  // ================================================================================
  // RENDER PRINCIPAL
  // ================================================================================

  return (
    <Box sx={{ p: 3 }}>
      {/* Cabeçalho */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1">
          Sistema de Estoque
        </Typography>
        <Box sx={{ display: 'flex', gap: 2 }}>
          <FormControl size="small" sx={{ minWidth: 200 }}>
            <InputLabel>Local</InputLabel>
            <Select
              value={localSelecionado}
              onChange={(e) => setLocalSelecionado(e.target.value)}
              label="Local"
            >
              {locais.map((local) => (
                <MenuItem key={local.id} value={local.id}>
                  {local.nome}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
          <Button
            variant="outlined"
            onClick={atualizarEstatisticas}
            startIcon={<Refresh />}
            disabled={loading}
          >
            Atualizar
          </Button>
        </Box>
      </Box>

      {/* Mensagem de Erro */}
      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {/* Tabs */}
      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
        <Tabs value={tabAtual} onChange={(e, newValue) => setTabAtual(newValue)}>
          <Tab 
            label={
              <Badge badgeContent={alertas ? (alertas.estoque_zerado.length + alertas.estoque_baixo.length) : 0} color="error">
                Dashboard
              </Badge>
            } 
            icon={<Assessment />} 
          />
          <Tab label="Posições" icon={<Inventory />} />
          <Tab label="Movimentações" icon={<TrendingUp />} />
          <Tab label="Locais" icon={<Archive />} />
        </Tabs>
      </Box>

      {/* Conteúdo das Tabs */}
      <TabPanel value={tabAtual} index={0}>
        {renderDashboard()}
      </TabPanel>
      
      <TabPanel value={tabAtual} index={1}>
        {renderPosicoes()}
      </TabPanel>
      
      <TabPanel value={tabAtual} index={2}>
        {renderMovimentacoes()}
      </TabPanel>
      
      <TabPanel value={tabAtual} index={3}>
        {renderLocais()}
      </TabPanel>

      {/* Modais */}
      {renderModalMovimentacao()}
      {renderModalLocal()}
      
      {/* Loading Global */}
      {loading && (
        <Box sx={{ position: 'fixed', top: 0, left: 0, right: 0, zIndex: 9999 }}>
          <LinearProgress />
        </Box>
      )}
    </Box>
  );
}
