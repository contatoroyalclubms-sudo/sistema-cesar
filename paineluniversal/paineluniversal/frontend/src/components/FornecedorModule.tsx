/*
Componente React para gestão completa de fornecedores
Interface unificada para CRUD, cotações, performance e avaliações
*/

import React, { useState, useEffect } from 'react'
import {
  Box,
  Paper,
  Typography,
  Tabs,
  Tab,
  Button,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Grid,
  Card,
  CardContent,
  Alert,
  Tooltip,
  Rating,
  LinearProgress,
  Avatar,
  List,
  ListItem,
  ListItemText,
  Divider,
  Accordion,
  AccordionSummary,
  AccordionDetails
} from '@mui/material'
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Search as SearchIcon,
  Refresh as RefreshIcon,
  Assessment as AssessmentIcon,
  Star as StarIcon,
  TrendingUp as TrendingUpIcon,
  Business as BusinessIcon,
  Phone as PhoneIcon,
  Email as EmailIcon,
  AttachMoney as MoneyIcon,
  Schedule as ScheduleIcon,
  CheckCircle as CheckIcon,
  Cancel as CancelIcon,
  ExpandMore as ExpandMoreIcon,
  Compare as CompareIcon,
  Receipt as ReceiptIcon
} from '@mui/icons-material'

import {
  FornecedorService,
  Fornecedor,
  ProdutoFornecedor,
  TipoFornecedor,
  StatusFornecedor,
  PerformanceFornecedor,
  DashboardFornecedores,
  AvaliacaoFornecedor,
  FiltrosFornecedor,
  formatarDocumento,
  formatarValorMonetario,
  formatarTelefone,
  obterCorStatusFornecedor,
  obterCorClassificacao,
  formatarPrazoEntrega,
  TIPOS_FORNECEDOR_LABELS,
  STATUS_FORNECEDOR_LABELS
} from '../services/fornecedorService'

interface TabPanelProps {
  children?: React.ReactNode
  index: number
  value: number
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`fornecedor-tabpanel-${index}`}
      aria-labelledby={`fornecedor-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  )
}

const FornecedorModule: React.FC = () => {
  // Estados principais
  const [tabValue, setTabValue] = useState(0)
  const [fornecedores, setFornecedores] = useState<Fornecedor[]>([])
  const [dashboard, setDashboard] = useState<DashboardFornecedores | null>(null)
  const [performance, setPerformance] = useState<PerformanceFornecedor[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // Estados de filtros e busca
  const [filtros, setFiltros] = useState<FiltrosFornecedor>({})
  const [page, setPage] = useState(1)
  const [totalPages, setTotalPages] = useState(1)

  // Estados de modais
  const [modalFornecedor, setModalFornecedor] = useState(false)
  const [modalProduto, setModalProduto] = useState(false)
  const [modalAvaliacao, setModalAvaliacao] = useState(false)
  const [modalCotacao, setModalCotacao] = useState(false)
  const [fornecedorSelecionado, setFornecedorSelecionado] = useState<Fornecedor | null>(null)
  const [produtoSelecionado, setProdutoSelecionado] = useState<any>(null)

  // Estados de formulários
  const [formFornecedor, setFormFornecedor] = useState<Partial<Fornecedor>>({
    tipo_pessoa: 'juridica',
    tipo_fornecedor: TipoFornecedor.MATERIAL,
    status: StatusFornecedor.ATIVO
  })
  const [formProduto, setFormProduto] = useState<Partial<ProdutoFornecedor>>({
    preferencial: false,
    ativo: true
  })
  const [formAvaliacao, setFormAvaliacao] = useState<AvaliacaoFornecedor>({
    qualidade_produto: 5,
    prazo_entrega: 5,
    atendimento: 5,
    preco: 5
  })

  // Carregar dados iniciais
  useEffect(() => {
    carregarDados()
  }, [])

  const carregarDados = async () => {
    setLoading(true)
    try {
      await Promise.all([
        carregarFornecedores(),
        carregarDashboard(),
        carregarPerformance()
      ])
    } catch (err) {
      setError('Erro ao carregar dados')
    } finally {
      setLoading(false)
    }
  }

  const carregarFornecedores = async () => {
    try {
      const response = await FornecedorService.listarFornecedores(page, 20, filtros)
      setFornecedores(response.itens)
      setTotalPages(response.pages)
    } catch (err) {
      setError('Erro ao carregar fornecedores')
    }
  }

  const carregarDashboard = async () => {
    try {
      const data = await FornecedorService.obterDashboard()
      setDashboard(data)
    } catch (err) {
      console.error('Erro ao carregar dashboard:', err)
    }
  }

  const carregarPerformance = async () => {
    try {
      const data = await FornecedorService.obterPerformanceFornecedores(30)
      setPerformance(data)
    } catch (err) {
      console.error('Erro ao carregar performance:', err)
    }
  }

  const handleSalvarFornecedor = async () => {
    try {
      if (fornecedorSelecionado) {
        await FornecedorService.atualizarFornecedor(fornecedorSelecionado.id, formFornecedor)
      } else {
        await FornecedorService.criarFornecedor(formFornecedor as any)
      }
      
      setModalFornecedor(false)
      setFormFornecedor({
        tipo_pessoa: 'juridica',
        tipo_fornecedor: TipoFornecedor.MATERIAL,
        status: StatusFornecedor.ATIVO
      })
      setFornecedorSelecionado(null)
      await carregarFornecedores()
    } catch (err) {
      setError('Erro ao salvar fornecedor')
    }
  }

  const handleExcluirFornecedor = async (id: number) => {
    if (window.confirm('Tem certeza que deseja excluir este fornecedor?')) {
      try {
        await FornecedorService.excluirFornecedor(id)
        await carregarFornecedores()
      } catch (err) {
        setError('Erro ao excluir fornecedor')
      }
    }
  }

  const handleAvaliarFornecedor = async () => {
    if (!fornecedorSelecionado) return

    try {
      await FornecedorService.avaliarFornecedor(fornecedorSelecionado.id, formAvaliacao)
      setModalAvaliacao(false)
      setFormAvaliacao({
        qualidade_produto: 5,
        prazo_entrega: 5,
        atendimento: 5,
        preco: 5
      })
      await carregarFornecedores()
    } catch (err) {
      setError('Erro ao avaliar fornecedor')
    }
  }

  const abrirModalEdicao = (fornecedor: Fornecedor) => {
    setFornecedorSelecionado(fornecedor)
    setFormFornecedor(fornecedor)
    setModalFornecedor(true)
  }

  const abrirModalAvaliacao = (fornecedor: Fornecedor) => {
    setFornecedorSelecionado(fornecedor)
    setModalAvaliacao(true)
  }

  // Renderizar Dashboard
  const renderDashboard = () => (
    <Grid container spacing={3}>
      {/* KPIs Principais */}
      <Grid item xs={12} md={3}>
        <Card>
          <CardContent>
            <Box display="flex" alignItems="center">
              <BusinessIcon color="primary" sx={{ mr: 2 }} />
              <Box>
                <Typography variant="h4">{dashboard?.total_fornecedores || 0}</Typography>
                <Typography color="textSecondary">Total Fornecedores</Typography>
              </Box>
            </Box>
          </CardContent>
        </Card>
      </Grid>

      <Grid item xs={12} md={3}>
        <Card>
          <CardContent>
            <Box display="flex" alignItems="center">
              <CheckIcon color="success" sx={{ mr: 2 }} />
              <Box>
                <Typography variant="h4">{dashboard?.fornecedores_ativos || 0}</Typography>
                <Typography color="textSecondary">Fornecedores Ativos</Typography>
              </Box>
            </Box>
          </CardContent>
        </Card>
      </Grid>

      <Grid item xs={12} md={3}>
        <Card>
          <CardContent>
            <Box display="flex" alignItems="center">
              <MoneyIcon color="warning" sx={{ mr: 2 }} />
              <Box>
                <Typography variant="h4">
                  {formatarValorMonetario(dashboard?.compras_ultimo_mes || 0)}
                </Typography>
                <Typography color="textSecondary">Compras Último Mês</Typography>
              </Box>
            </Box>
          </CardContent>
        </Card>
      </Grid>

      <Grid item xs={12} md={3}>
        <Card>
          <CardContent>
            <Box display="flex" alignItems="center">
              <TrendingUpIcon color="info" sx={{ mr: 2 }} />
              <Box>
                <Typography variant="h4">{dashboard?.top_fornecedores.length || 0}</Typography>
                <Typography color="textSecondary">Top Fornecedores</Typography>
              </Box>
            </Box>
          </CardContent>
        </Card>
      </Grid>

      {/* Top Fornecedores */}
      <Grid item xs={12} md={8}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Top Fornecedores (Último Mês)
            </Typography>
            <List>
              {dashboard?.top_fornecedores.map((item, index) => (
                <React.Fragment key={index}>
                  <ListItem>
                    <Avatar sx={{ mr: 2, bgcolor: 'primary.main' }}>
                      {index + 1}
                    </Avatar>
                    <ListItemText
                      primary={item.nome}
                      secondary={formatarValorMonetario(item.valor)}
                    />
                  </ListItem>
                  {index < dashboard.top_fornecedores.length - 1 && <Divider />}
                </React.Fragment>
              ))}
            </List>
          </CardContent>
        </Card>
      </Grid>

      {/* Distribuição por Tipo */}
      <Grid item xs={12} md={4}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Distribuição por Tipo
            </Typography>
            {dashboard?.distribuicao_tipos.map((item, index) => (
              <Box key={index} mb={2}>
                <Box display="flex" justifyContent="space-between" mb={1}>
                  <Typography variant="body2">
                    {TIPOS_FORNECEDOR_LABELS[item.tipo]}
                  </Typography>
                  <Typography variant="body2">{item.quantidade}</Typography>
                </Box>
                <LinearProgress
                  variant="determinate"
                  value={(item.quantidade / (dashboard.total_fornecedores || 1)) * 100}
                />
              </Box>
            ))}
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  )

  // Renderizar Lista de Fornecedores
  const renderListaFornecedores = () => (
    <Box>
      {/* Filtros e Ações */}
      <Paper sx={{ p: 2, mb: 3 }}>
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} md={3}>
            <TextField
              fullWidth
              placeholder="Buscar por nome..."
              value={filtros.nome || ''}
              onChange={(e) => setFiltros({ ...filtros, nome: e.target.value })}
              InputProps={{
                startAdornment: <SearchIcon sx={{ mr: 1, color: 'text.secondary' }} />
              }}
            />
          </Grid>

          <Grid item xs={12} md={2}>
            <FormControl fullWidth>
              <InputLabel>Tipo</InputLabel>
              <Select
                value={filtros.tipo_fornecedor || ''}
                onChange={(e) => setFiltros({ 
                  ...filtros, 
                  tipo_fornecedor: e.target.value as TipoFornecedor 
                })}
              >
                <MenuItem value="">Todos</MenuItem>
                {Object.entries(TIPOS_FORNECEDOR_LABELS).map(([key, label]) => (
                  <MenuItem key={key} value={key}>{label}</MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>

          <Grid item xs={12} md={2}>
            <FormControl fullWidth>
              <InputLabel>Status</InputLabel>
              <Select
                value={filtros.status || ''}
                onChange={(e) => setFiltros({ 
                  ...filtros, 
                  status: e.target.value as StatusFornecedor 
                })}
              >
                <MenuItem value="">Todos</MenuItem>
                {Object.entries(STATUS_FORNECEDOR_LABELS).map(([key, label]) => (
                  <MenuItem key={key} value={key}>{label}</MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>

          <Grid item xs={12} md={2}>
            <TextField
              fullWidth
              placeholder="Cidade"
              value={filtros.cidade || ''}
              onChange={(e) => setFiltros({ ...filtros, cidade: e.target.value })}
            />
          </Grid>

          <Grid item xs={12} md={3}>
            <Box display="flex" gap={1}>
              <Button
                variant="outlined"
                startIcon={<SearchIcon />}
                onClick={carregarFornecedores}
              >
                Buscar
              </Button>
              <Button
                variant="contained"
                startIcon={<AddIcon />}
                onClick={() => setModalFornecedor(true)}
              >
                Novo Fornecedor
              </Button>
            </Box>
          </Grid>
        </Grid>
      </Paper>

      {/* Tabela de Fornecedores */}
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Nome</TableCell>
              <TableCell>Documento</TableCell>
              <TableCell>Tipo</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Avaliação</TableCell>
              <TableCell>Contato</TableCell>
              <TableCell>Ações</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {fornecedores.map((fornecedor) => (
              <TableRow key={fornecedor.id}>
                <TableCell>
                  <Box>
                    <Typography variant="subtitle2">{fornecedor.nome}</Typography>
                    <Typography variant="caption" color="textSecondary">
                      {fornecedor.cidade} - {fornecedor.estado}
                    </Typography>
                  </Box>
                </TableCell>
                <TableCell>
                  {formatarDocumento(fornecedor.documento, fornecedor.tipo_pessoa)}
                </TableCell>
                <TableCell>
                  <Chip
                    label={TIPOS_FORNECEDOR_LABELS[fornecedor.tipo_fornecedor]}
                    size="small"
                    variant="outlined"
                  />
                </TableCell>
                <TableCell>
                  <Chip
                    label={STATUS_FORNECEDOR_LABELS[fornecedor.status]}
                    size="small"
                    style={{ 
                      backgroundColor: obterCorStatusFornecedor(fornecedor.status),
                      color: 'white'
                    }}
                  />
                </TableCell>
                <TableCell>
                  {fornecedor.avaliacao_media ? (
                    <Box display="flex" alignItems="center">
                      <Rating value={fornecedor.avaliacao_media} readOnly size="small" />
                      <Typography variant="caption" sx={{ ml: 1 }}>
                        ({fornecedor.avaliacao_media.toFixed(1)})
                      </Typography>
                    </Box>
                  ) : (
                    <Typography variant="caption" color="textSecondary">
                      Não avaliado
                    </Typography>
                  )}
                </TableCell>
                <TableCell>
                  <Box>
                    {fornecedor.telefone && (
                      <Box display="flex" alignItems="center" mb={0.5}>
                        <PhoneIcon fontSize="small" sx={{ mr: 0.5 }} />
                        <Typography variant="caption">
                          {formatarTelefone(fornecedor.telefone)}
                        </Typography>
                      </Box>
                    )}
                    {fornecedor.email && (
                      <Box display="flex" alignItems="center">
                        <EmailIcon fontSize="small" sx={{ mr: 0.5 }} />
                        <Typography variant="caption">{fornecedor.email}</Typography>
                      </Box>
                    )}
                  </Box>
                </TableCell>
                <TableCell>
                  <Box display="flex" gap={1}>
                    <Tooltip title="Editar">
                      <IconButton
                        size="small"
                        onClick={() => abrirModalEdicao(fornecedor)}
                      >
                        <EditIcon />
                      </IconButton>
                    </Tooltip>
                    <Tooltip title="Avaliar">
                      <IconButton
                        size="small"
                        onClick={() => abrirModalAvaliacao(fornecedor)}
                      >
                        <StarIcon />
                      </IconButton>
                    </Tooltip>
                    <Tooltip title="Excluir">
                      <IconButton
                        size="small"
                        color="error"
                        onClick={() => handleExcluirFornecedor(fornecedor.id)}
                      >
                        <DeleteIcon />
                      </IconButton>
                    </Tooltip>
                  </Box>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  )

  // Renderizar Performance
  const renderPerformance = () => (
    <Grid container spacing={3}>
      <Grid item xs={12}>
        <Paper sx={{ p: 2 }}>
          <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
            <Typography variant="h6">Performance dos Fornecedores</Typography>
            <Button
              variant="outlined"
              startIcon={<RefreshIcon />}
              onClick={carregarPerformance}
            >
              Atualizar
            </Button>
          </Box>

          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Fornecedor</TableCell>
                  <TableCell align="center">Compras</TableCell>
                  <TableCell align="center">Valor Total</TableCell>
                  <TableCell align="center">Pontualidade</TableCell>
                  <TableCell align="center">Atraso Médio</TableCell>
                  <TableCell align="center">Classificação</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {performance.map((perf) => (
                  <TableRow key={perf.fornecedor_id}>
                    <TableCell>{perf.nome}</TableCell>
                    <TableCell align="center">{perf.total_compras}</TableCell>
                    <TableCell align="center">
                      {formatarValorMonetario(perf.valor_total)}
                    </TableCell>
                    <TableCell align="center">
                      <Box display="flex" alignItems="center" justifyContent="center">
                        <LinearProgress
                          variant="determinate"
                          value={perf.pontualidade_percentual}
                          sx={{ width: 60, mr: 1 }}
                        />
                        <Typography variant="body2">
                          {perf.pontualidade_percentual.toFixed(1)}%
                        </Typography>
                      </Box>
                    </TableCell>
                    <TableCell align="center">
                      {perf.atraso_medio_dias.toFixed(1)} dias
                    </TableCell>
                    <TableCell align="center">
                      <Chip
                        label={perf.classificacao}
                        size="small"
                        style={{ 
                          backgroundColor: obterCorClassificacao(perf.classificacao),
                          color: 'white'
                        }}
                      />
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </Paper>
      </Grid>
    </Grid>
  )

  // Modal de Fornecedor
  const modalFornecedorDialog = (
    <Dialog open={modalFornecedor} onClose={() => setModalFornecedor(false)} maxWidth="md" fullWidth>
      <DialogTitle>
        {fornecedorSelecionado ? 'Editar Fornecedor' : 'Novo Fornecedor'}
      </DialogTitle>
      <DialogContent>
        <Grid container spacing={2} sx={{ mt: 1 }}>
          <Grid item xs={12} md={8}>
            <TextField
              fullWidth
              label="Nome"
              value={formFornecedor.nome || ''}
              onChange={(e) => setFormFornecedor({ ...formFornecedor, nome: e.target.value })}
            />
          </Grid>
          
          <Grid item xs={12} md={4}>
            <FormControl fullWidth>
              <InputLabel>Tipo de Pessoa</InputLabel>
              <Select
                value={formFornecedor.tipo_pessoa || 'juridica'}
                onChange={(e) => setFormFornecedor({ 
                  ...formFornecedor, 
                  tipo_pessoa: e.target.value as 'fisica' | 'juridica'
                })}
              >
                <MenuItem value="fisica">Pessoa Física</MenuItem>
                <MenuItem value="juridica">Pessoa Jurídica</MenuItem>
              </Select>
            </FormControl>
          </Grid>

          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label={formFornecedor.tipo_pessoa === 'fisica' ? 'CPF' : 'CNPJ'}
              value={formFornecedor.documento || ''}
              onChange={(e) => setFormFornecedor({ ...formFornecedor, documento: e.target.value })}
            />
          </Grid>

          <Grid item xs={12} md={6}>
            <FormControl fullWidth>
              <InputLabel>Tipo de Fornecedor</InputLabel>
              <Select
                value={formFornecedor.tipo_fornecedor || TipoFornecedor.MATERIAL}
                onChange={(e) => setFormFornecedor({ 
                  ...formFornecedor, 
                  tipo_fornecedor: e.target.value as TipoFornecedor
                })}
              >
                {Object.entries(TIPOS_FORNECEDOR_LABELS).map(([key, label]) => (
                  <MenuItem key={key} value={key}>{label}</MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>

          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="Email"
              type="email"
              value={formFornecedor.email || ''}
              onChange={(e) => setFormFornecedor({ ...formFornecedor, email: e.target.value })}
            />
          </Grid>

          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="Telefone"
              value={formFornecedor.telefone || ''}
              onChange={(e) => setFormFornecedor({ ...formFornecedor, telefone: e.target.value })}
            />
          </Grid>

          <Grid item xs={12}>
            <TextField
              fullWidth
              label="Endereço"
              value={formFornecedor.endereco || ''}
              onChange={(e) => setFormFornecedor({ ...formFornecedor, endereco: e.target.value })}
            />
          </Grid>

          <Grid item xs={12} md={4}>
            <TextField
              fullWidth
              label="Cidade"
              value={formFornecedor.cidade || ''}
              onChange={(e) => setFormFornecedor({ ...formFornecedor, cidade: e.target.value })}
            />
          </Grid>

          <Grid item xs={12} md={4}>
            <TextField
              fullWidth
              label="Estado"
              value={formFornecedor.estado || ''}
              onChange={(e) => setFormFornecedor({ ...formFornecedor, estado: e.target.value })}
            />
          </Grid>

          <Grid item xs={12} md={4}>
            <TextField
              fullWidth
              label="CEP"
              value={formFornecedor.cep || ''}
              onChange={(e) => setFormFornecedor({ ...formFornecedor, cep: e.target.value })}
            />
          </Grid>

          <Grid item xs={12}>
            <TextField
              fullWidth
              label="Observações"
              multiline
              rows={3}
              value={formFornecedor.observacoes || ''}
              onChange={(e) => setFormFornecedor({ ...formFornecedor, observacoes: e.target.value })}
            />
          </Grid>
        </Grid>
      </DialogContent>
      <DialogActions>
        <Button onClick={() => setModalFornecedor(false)}>Cancelar</Button>
        <Button variant="contained" onClick={handleSalvarFornecedor}>
          Salvar
        </Button>
      </DialogActions>
    </Dialog>
  )

  // Modal de Avaliação
  const modalAvaliacaoDialog = (
    <Dialog open={modalAvaliacao} onClose={() => setModalAvaliacao(false)} maxWidth="sm" fullWidth>
      <DialogTitle>Avaliar Fornecedor</DialogTitle>
      <DialogContent>
        <Grid container spacing={3} sx={{ mt: 1 }}>
          <Grid item xs={12}>
            <Box display="flex" alignItems="center" justifyContent="space-between">
              <Typography>Qualidade do Produto:</Typography>
              <Rating
                value={formAvaliacao.qualidade_produto}
                onChange={(_, newValue) => setFormAvaliacao({
                  ...formAvaliacao,
                  qualidade_produto: newValue || 1
                })}
              />
            </Box>
          </Grid>

          <Grid item xs={12}>
            <Box display="flex" alignItems="center" justifyContent="space-between">
              <Typography>Prazo de Entrega:</Typography>
              <Rating
                value={formAvaliacao.prazo_entrega}
                onChange={(_, newValue) => setFormAvaliacao({
                  ...formAvaliacao,
                  prazo_entrega: newValue || 1
                })}
              />
            </Box>
          </Grid>

          <Grid item xs={12}>
            <Box display="flex" alignItems="center" justifyContent="space-between">
              <Typography>Atendimento:</Typography>
              <Rating
                value={formAvaliacao.atendimento}
                onChange={(_, newValue) => setFormAvaliacao({
                  ...formAvaliacao,
                  atendimento: newValue || 1
                })}
              />
            </Box>
          </Grid>

          <Grid item xs={12}>
            <Box display="flex" alignItems="center" justifyContent="space-between">
              <Typography>Preço:</Typography>
              <Rating
                value={formAvaliacao.preco}
                onChange={(_, newValue) => setFormAvaliacao({
                  ...formAvaliacao,
                  preco: newValue || 1
                })}
              />
            </Box>
          </Grid>

          <Grid item xs={12}>
            <TextField
              fullWidth
              label="Observações"
              multiline
              rows={3}
              value={formAvaliacao.observacoes || ''}
              onChange={(e) => setFormAvaliacao({
                ...formAvaliacao,
                observacoes: e.target.value
              })}
            />
          </Grid>
        </Grid>
      </DialogContent>
      <DialogActions>
        <Button onClick={() => setModalAvaliacao(false)}>Cancelar</Button>
        <Button variant="contained" onClick={handleAvaliarFornecedor}>
          Avaliar
        </Button>
      </DialogActions>
    </Dialog>
  )

  return (
    <Box>
      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {loading && <LinearProgress sx={{ mb: 2 }} />}

      <Paper sx={{ width: '100%' }}>
        <Tabs value={tabValue} onChange={(_, newValue) => setTabValue(newValue)}>
          <Tab label="Dashboard" icon={<AssessmentIcon />} />
          <Tab label="Fornecedores" icon={<BusinessIcon />} />
          <Tab label="Performance" icon={<TrendingUpIcon />} />
        </Tabs>

        <TabPanel value={tabValue} index={0}>
          {renderDashboard()}
        </TabPanel>

        <TabPanel value={tabValue} index={1}>
          {renderListaFornecedores()}
        </TabPanel>

        <TabPanel value={tabValue} index={2}>
          {renderPerformance()}
        </TabPanel>
      </Paper>

      {modalFornecedorDialog}
      {modalAvaliacaoDialog}
    </Box>
  )
}

export default FornecedorModule
