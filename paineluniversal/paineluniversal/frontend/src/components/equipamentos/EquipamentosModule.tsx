import React, { useState, useEffect } from 'react';
import { 
  Card, 
  CardContent, 
  CardHeader, 
  CardTitle 
} from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { 
  Tabs, 
  TabsContent, 
  TabsList, 
  TabsTrigger 
} from '@/components/ui/tabs';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow
} from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter
} from '@/components/ui/dialog';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue
} from '@/components/ui/select';
import { Switch } from '@/components/ui/switch';
import { toast } from '@/components/ui/use-toast';
import { Alert, AlertDescription } from '@/components/ui/alert';
import {
  LineChart, 
  Line, 
  BarChart, 
  Bar,
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  PieChart, 
  Pie, 
  Cell
} from 'recharts';
import {
  QrCode,
  Scan,
  Settings,
  Activity,
  MapPin,
  Users,
  AlertTriangle,
  Plus,
  Search,
  Filter,
  Download,
  RefreshCw
} from 'lucide-react';

interface LeitorQR {
  id: number;
  codigo_equipamento: string;
  nome: string;
  tipo_leitor: string;
  marca: string;
  modelo: string;
  status: string;
  localizacao: string;
  total_leituras: number;
  leituras_sucesso: number;
  leituras_erro: number;
  tempo_medio_leitura: number;
  ultimo_heartbeat: string;
  nivel_bateria?: number;
}

interface PontoAcesso {
  id: number;
  nome: string;
  codigo: string;
  tipo_ponto: string;
  localizacao_descricao: string;
  capacidade_maxima: number;
  contagem_atual: number;
  total_entradas: number;
  total_saidas: number;
  ativo: boolean;
  percentual_alerta: number;
}

interface HistoricoLeitura {
  id: number;
  codigo_lido: string;
  valido: boolean;
  tipo_validacao: string;
  resultado_validacao: string;
  timestamp_leitura: string;
  participante_nome?: string;
  tempo_leitura?: number;
}

interface StatusSistema {
  total_leitores: number;
  leitores_ativos: number;
  leitores_inativos: number;
  leitores_manutencao: number;
  total_pontos_acesso: number;
  pontos_ativos: number;
  ocupacao_total: number;
  alertas_capacidade: number;
}

const EquipamentosModule: React.FC = () => {
  const [leitoresQR, setLeitoresQR] = useState<LeitorQR[]>([]);
  const [pontosAcesso, setPontosAcesso] = useState<PontoAcesso[]>([]);
  const [historicoLeituras, setHistoricoLeituras] = useState<HistoricoLeitura[]>([]);
  const [statusSistema, setStatusSistema] = useState<StatusSistema | null>(null);
  
  const [dialogoAberto, setDialogoAberto] = useState(false);
  const [tipoDialogo, setTipoDialogo] = useState<'leitor' | 'ponto'>('leitor');
  const [itemEdicao, setItemEdicao] = useState<any>(null);
  
  const [filtroStatus, setFiltroStatus] = useState<string>('');
  const [filtroTipo, setFiltroTipo] = useState<string>('');
  const [buscaTexto, setBuscaTexto] = useState<string>('');
  
  const [loading, setLoading] = useState(false);
  const [webSocket, setWebSocket] = useState<WebSocket | null>(null);

  // Status colors
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'ativo': return 'bg-green-100 text-green-800';
      case 'inativo': return 'bg-gray-100 text-gray-800';
      case 'manutencao': return 'bg-yellow-100 text-yellow-800';
      case 'erro': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getBatteryColor = (nivel?: number) => {
    if (!nivel) return 'text-gray-400';
    if (nivel > 50) return 'text-green-600';
    if (nivel > 20) return 'text-yellow-600';
    return 'text-red-600';
  };

  // Data loading
  const carregarDados = async () => {
    setLoading(true);
    try {
      const [leitoresRes, pontosRes, historicoRes, statusRes] = await Promise.all([
        fetch('/api/equipamentos/leitores-qr'),
        fetch('/api/equipamentos/pontos-acesso'),
        fetch('/api/equipamentos/leituras-qr?limit=50'),
        fetch('/api/equipamentos/status-sistema')
      ]);

      if (leitoresRes.ok) {
        setLeitoresQR(await leitoresRes.json());
      }
      if (pontosRes.ok) {
        setPontosAcesso(await pontosRes.json());
      }
      if (historicoRes.ok) {
        setHistoricoLeituras(await historicoRes.json());
      }
      if (statusRes.ok) {
        setStatusSistema(await statusRes.json());
      }
    } catch (error) {
      toast({
        title: "Erro",
        description: "Erro ao carregar dados dos equipamentos",
        variant: "destructive"
      });
    }
    setLoading(false);
  };

  // WebSocket connection
  const conectarWebSocket = () => {
    const wsUrl = `ws://localhost:8000/api/equipamentos/ws/monitoramento/1`;
    const ws = new WebSocket(wsUrl);

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === 'status_sistema') {
        setStatusSistema(data.data);
      }
    };

    ws.onclose = () => {
      setTimeout(conectarWebSocket, 5000);
    };

    setWebSocket(ws);
  };

  useEffect(() => {
    carregarDados();
    conectarWebSocket();

    return () => {
      if (webSocket) {
        webSocket.close();
      }
    };
  }, []);

  // Form handling
  const abrirDialogo = (tipo: 'leitor' | 'ponto', item?: any) => {
    setTipoDialogo(tipo);
    setItemEdicao(item || null);
    setDialogoAberto(true);
  };

  const salvarItem = async (dados: any) => {
    try {
      const endpoint = tipoDialogo === 'leitor' ? 'leitores-qr' : 'pontos-acesso';
      const method = itemEdicao ? 'PUT' : 'POST';
      const url = itemEdicao 
        ? `/api/equipamentos/${endpoint}/${itemEdicao.id}`
        : `/api/equipamentos/${endpoint}`;

      const response = await fetch(url, {
        method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(dados)
      });

      if (response.ok) {
        toast({
          title: "Sucesso",
          description: `${tipoDialogo === 'leitor' ? 'Leitor QR' : 'Ponto de acesso'} ${itemEdicao ? 'atualizado' : 'criado'} com sucesso`
        });
        setDialogoAberto(false);
        carregarDados();
      } else {
        throw new Error('Erro na requisição');
      }
    } catch (error) {
      toast({
        title: "Erro",
        description: `Erro ao ${itemEdicao ? 'atualizar' : 'criar'} ${tipoDialogo === 'leitor' ? 'leitor QR' : 'ponto de acesso'}`,
        variant: "destructive"
      });
    }
  };

  // Filter functions
  const leitoresFiltrados = leitoresQR.filter(leitor => {
    return (!filtroStatus || leitor.status === filtroStatus) &&
           (!filtroTipo || leitor.tipo_leitor === filtroTipo) &&
           (!buscaTexto || 
            leitor.nome.toLowerCase().includes(buscaTexto.toLowerCase()) ||
            leitor.codigo_equipamento.toLowerCase().includes(buscaTexto.toLowerCase()));
  });

  const pontosFiltrados = pontosAcesso.filter(ponto => {
    return (!buscaTexto || 
            ponto.nome.toLowerCase().includes(buscaTexto.toLowerCase()) ||
            ponto.codigo.toLowerCase().includes(buscaTexto.toLowerCase()));
  });

  // Chart data
  const dadosGraficoLeituras = leitoresQR.map(leitor => ({
    nome: leitor.nome,
    sucessos: leitor.leituras_sucesso,
    erros: leitor.leituras_erro,
    total: leitor.total_leituras
  }));

  const dadosGraficoOcupacao = pontosAcesso.map(ponto => ({
    nome: ponto.nome,
    atual: ponto.contagem_atual,
    capacidade: ponto.capacidade_maxima || 0,
    percentual: ponto.capacidade_maxima ? (ponto.contagem_atual / ponto.capacidade_maxima * 100) : 0
  }));

  const statusDistribution = statusSistema ? [
    { name: 'Ativos', value: statusSistema.leitores_ativos, color: '#10b981' },
    { name: 'Inativos', value: statusSistema.leitores_inativos, color: '#6b7280' },
    { name: 'Manutenção', value: statusSistema.leitores_manutencao, color: '#f59e0b' }
  ] : [];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Equipamentos</h1>
          <p className="text-muted-foreground">
            Gestão de leitores QR Code e pontos de acesso
          </p>
        </div>
        <div className="flex gap-2">
          <Button onClick={carregarDados} variant="outline" disabled={loading}>
            <RefreshCw className="h-4 w-4 mr-2" />
            Atualizar
          </Button>
        </div>
      </div>

      {/* Status Cards */}
      {statusSistema && (
        <div className="grid gap-4 md:grid-cols-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Leitores QR</CardTitle>
              <QrCode className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{statusSistema.total_leitores}</div>
              <p className="text-xs text-muted-foreground">
                {statusSistema.leitores_ativos} ativos
              </p>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Pontos de Acesso</CardTitle>
              <MapPin className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{statusSistema.total_pontos_acesso}</div>
              <p className="text-xs text-muted-foreground">
                {statusSistema.pontos_ativos} ativos
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Ocupação Total</CardTitle>
              <Users className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{statusSistema.ocupacao_total}</div>
              <p className="text-xs text-muted-foreground">
                pessoas nos pontos
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Alertas</CardTitle>
              <AlertTriangle className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{statusSistema.alertas_capacidade}</div>
              <p className="text-xs text-muted-foreground">
                alertas de capacidade
              </p>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Main Tabs */}
      <Tabs defaultValue="leitores" className="space-y-4">
        <TabsList>
          <TabsTrigger value="leitores">Leitores QR</TabsTrigger>
          <TabsTrigger value="pontos">Pontos de Acesso</TabsTrigger>
          <TabsTrigger value="historico">Histórico</TabsTrigger>
          <TabsTrigger value="dashboard">Dashboard</TabsTrigger>
        </TabsList>

        {/* Leitores QR Tab */}
        <TabsContent value="leitores">
          <Card>
            <CardHeader>
              <div className="flex justify-between items-center">
                <CardTitle>Leitores QR Code</CardTitle>
                <Button onClick={() => abrirDialogo('leitor')}>
                  <Plus className="h-4 w-4 mr-2" />
                  Novo Leitor
                </Button>
              </div>
              
              {/* Filters */}
              <div className="flex gap-4 mt-4">
                <div className="flex-1">
                  <Input
                    placeholder="Buscar por nome ou código..."
                    value={buscaTexto}
                    onChange={(e) => setBuscaTexto(e.target.value)}
                  />
                </div>
                <Select value={filtroStatus} onValueChange={setFiltroStatus}>
                  <SelectTrigger className="w-[150px]">
                    <SelectValue placeholder="Status" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="">Todos</SelectItem>
                    <SelectItem value="ativo">Ativo</SelectItem>
                    <SelectItem value="inativo">Inativo</SelectItem>
                    <SelectItem value="manutencao">Manutenção</SelectItem>
                    <SelectItem value="erro">Erro</SelectItem>
                  </SelectContent>
                </Select>
                <Select value={filtroTipo} onValueChange={setFiltroTipo}>
                  <SelectTrigger className="w-[150px]">
                    <SelectValue placeholder="Tipo" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="">Todos</SelectItem>
                    <SelectItem value="fixo">Fixo</SelectItem>
                    <SelectItem value="mobile">Mobile</SelectItem>
                    <SelectItem value="totem">Totem</SelectItem>
                    <SelectItem value="handheld">Handheld</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </CardHeader>
            
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Equipamento</TableHead>
                    <TableHead>Tipo</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Localização</TableHead>
                    <TableHead>Leituras</TableHead>
                    <TableHead>Taxa Sucesso</TableHead>
                    <TableHead>Bateria</TableHead>
                    <TableHead>Última Atividade</TableHead>
                    <TableHead>Ações</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {leitoresFiltrados.map((leitor) => (
                    <TableRow key={leitor.id}>
                      <TableCell>
                        <div>
                          <div className="font-medium">{leitor.nome}</div>
                          <div className="text-sm text-muted-foreground">
                            {leitor.codigo_equipamento}
                          </div>
                        </div>
                      </TableCell>
                      <TableCell>
                        <Badge variant="secondary">
                          {leitor.tipo_leitor}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        <Badge className={getStatusColor(leitor.status)}>
                          {leitor.status}
                        </Badge>
                      </TableCell>
                      <TableCell>{leitor.localizacao}</TableCell>
                      <TableCell>
                        <div className="text-sm">
                          <div>Total: {leitor.total_leituras}</div>
                          <div className="text-green-600">✓ {leitor.leituras_sucesso}</div>
                          <div className="text-red-600">✗ {leitor.leituras_erro}</div>
                        </div>
                      </TableCell>
                      <TableCell>
                        {leitor.total_leituras > 0 
                          ? Math.round((leitor.leituras_sucesso / leitor.total_leituras) * 100)
                          : 0
                        }%
                      </TableCell>
                      <TableCell>
                        {leitor.nivel_bateria && (
                          <span className={getBatteryColor(leitor.nivel_bateria)}>
                            {leitor.nivel_bateria}%
                          </span>
                        )}
                      </TableCell>
                      <TableCell>
                        {leitor.ultimo_heartbeat 
                          ? new Date(leitor.ultimo_heartbeat).toLocaleString()
                          : 'Nunca'
                        }
                      </TableCell>
                      <TableCell>
                        <Button 
                          variant="ghost" 
                          size="sm"
                          onClick={() => abrirDialogo('leitor', leitor)}
                        >
                          <Settings className="h-4 w-4" />
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Pontos de Acesso Tab */}
        <TabsContent value="pontos">
          <Card>
            <CardHeader>
              <div className="flex justify-between items-center">
                <CardTitle>Pontos de Acesso</CardTitle>
                <Button onClick={() => abrirDialogo('ponto')}>
                  <Plus className="h-4 w-4 mr-2" />
                  Novo Ponto
                </Button>
              </div>
            </CardHeader>
            
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Ponto</TableHead>
                    <TableHead>Tipo</TableHead>
                    <TableHead>Localização</TableHead>
                    <TableHead>Ocupação</TableHead>
                    <TableHead>Capacidade</TableHead>
                    <TableHead>Entradas/Saídas</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Ações</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {pontosFiltrados.map((ponto) => (
                    <TableRow key={ponto.id}>
                      <TableCell>
                        <div>
                          <div className="font-medium">{ponto.nome}</div>
                          <div className="text-sm text-muted-foreground">
                            {ponto.codigo}
                          </div>
                        </div>
                      </TableCell>
                      <TableCell>
                        <Badge variant="secondary">
                          {ponto.tipo_ponto}
                        </Badge>
                      </TableCell>
                      <TableCell>{ponto.localizacao_descricao}</TableCell>
                      <TableCell>
                        <div className="flex items-center gap-2">
                          <span className="font-medium">{ponto.contagem_atual}</span>
                          {ponto.capacidade_maxima > 0 && (
                            <span className="text-sm text-muted-foreground">
                              ({Math.round((ponto.contagem_atual / ponto.capacidade_maxima) * 100)}%)
                            </span>
                          )}
                        </div>
                      </TableCell>
                      <TableCell>{ponto.capacidade_maxima}</TableCell>
                      <TableCell>
                        <div className="text-sm">
                          <div className="text-green-600">↗ {ponto.total_entradas}</div>
                          <div className="text-red-600">↖ {ponto.total_saidas}</div>
                        </div>
                      </TableCell>
                      <TableCell>
                        <Badge className={ponto.ativo ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}>
                          {ponto.ativo ? 'Ativo' : 'Inativo'}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        <Button 
                          variant="ghost" 
                          size="sm"
                          onClick={() => abrirDialogo('ponto', ponto)}
                        >
                          <Settings className="h-4 w-4" />
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Histórico Tab */}
        <TabsContent value="historico">
          <Card>
            <CardHeader>
              <CardTitle>Histórico de Leituras</CardTitle>
            </CardHeader>
            
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Data/Hora</TableHead>
                    <TableHead>Código</TableHead>
                    <TableHead>Tipo</TableHead>
                    <TableHead>Resultado</TableHead>
                    <TableHead>Participante</TableHead>
                    <TableHead>Tempo</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {historicoLeituras.map((leitura) => (
                    <TableRow key={leitura.id}>
                      <TableCell>
                        {new Date(leitura.timestamp_leitura).toLocaleString()}
                      </TableCell>
                      <TableCell className="font-mono">
                        {leitura.codigo_lido.substring(0, 20)}...
                      </TableCell>
                      <TableCell>
                        <Badge variant="secondary">
                          {leitura.tipo_validacao}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        <Badge className={
                          leitura.valido 
                            ? 'bg-green-100 text-green-800'
                            : 'bg-red-100 text-red-800'
                        }>
                          {leitura.resultado_validacao}
                        </Badge>
                      </TableCell>
                      <TableCell>{leitura.participante_nome || '-'}</TableCell>
                      <TableCell>
                        {leitura.tempo_leitura ? `${leitura.tempo_leitura}ms` : '-'}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Dashboard Tab */}
        <TabsContent value="dashboard">
          <div className="grid gap-4 md:grid-cols-2">
            {/* Performance dos Leitores */}
            <Card>
              <CardHeader>
                <CardTitle>Performance dos Leitores</CardTitle>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={dadosGraficoLeituras}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="nome" />
                    <YAxis />
                    <Tooltip />
                    <Bar dataKey="sucessos" fill="#10b981" />
                    <Bar dataKey="erros" fill="#ef4444" />
                  </BarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            {/* Ocupação dos Pontos */}
            <Card>
              <CardHeader>
                <CardTitle>Ocupação dos Pontos</CardTitle>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={dadosGraficoOcupacao}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="nome" />
                    <YAxis />
                    <Tooltip />
                    <Bar dataKey="percentual" fill="#3b82f6" />
                  </BarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            {/* Distribuição de Status */}
            <Card>
              <CardHeader>
                <CardTitle>Status dos Equipamentos</CardTitle>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={statusDistribution}
                      cx="50%"
                      cy="50%"
                      outerRadius={100}
                      fill="#8884d8"
                      dataKey="value"
                      label={({ name, value }) => `${name}: ${value}`}
                    >
                      {statusDistribution.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            {/* Alertas e Notificações */}
            <Card>
              <CardHeader>
                <CardTitle>Alertas Ativos</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {statusSistema?.alertas_capacidade > 0 && (
                    <Alert>
                      <AlertTriangle className="h-4 w-4" />
                      <AlertDescription>
                        {statusSistema.alertas_capacidade} ponto(s) com alerta de capacidade
                      </AlertDescription>
                    </Alert>
                  )}
                  
                  {statusSistema?.leitores_manutencao > 0 && (
                    <Alert>
                      <Settings className="h-4 w-4" />
                      <AlertDescription>
                        {statusSistema.leitores_manutencao} leitor(es) em manutenção
                      </AlertDescription>
                    </Alert>
                  )}
                  
                  {statusSistema?.leitores_inativos > 0 && (
                    <Alert>
                      <Activity className="h-4 w-4" />
                      <AlertDescription>
                        {statusSistema.leitores_inativos} leitor(es) inativo(s)
                      </AlertDescription>
                    </Alert>
                  )}
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>

      {/* Dialog for Add/Edit */}
      <Dialog open={dialogoAberto} onOpenChange={setDialogoAberto}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle>
              {itemEdicao ? 'Editar' : 'Novo'} {tipoDialogo === 'leitor' ? 'Leitor QR' : 'Ponto de Acesso'}
            </DialogTitle>
          </DialogHeader>
          
          {tipoDialogo === 'leitor' ? (
            <LeitorQRForm item={itemEdicao} onSave={salvarItem} />
          ) : (
            <PontoAcessoForm item={itemEdicao} onSave={salvarItem} />
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
};

// Leitor QR Form Component
const LeitorQRForm: React.FC<{ item?: any; onSave: (data: any) => void }> = ({ item, onSave }) => {
  const [formData, setFormData] = useState({
    codigo_equipamento: item?.codigo_equipamento || '',
    nome: item?.nome || '',
    tipo_leitor: item?.tipo_leitor || 'fixo',
    marca: item?.marca || '',
    modelo: item?.modelo || '',
    localizacao: item?.localizacao || '',
    status: item?.status || 'inativo',
    endereco_ip: item?.endereco_ip || '',
    sensibilidade: item?.sensibilidade || 3,
    timeout_leitura: item?.timeout_leitura || 5000
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSave(formData);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <Label htmlFor="codigo_equipamento">Código do Equipamento</Label>
        <Input
          id="codigo_equipamento"
          value={formData.codigo_equipamento}
          onChange={(e) => setFormData({...formData, codigo_equipamento: e.target.value})}
          required
        />
      </div>
      
      <div>
        <Label htmlFor="nome">Nome</Label>
        <Input
          id="nome"
          value={formData.nome}
          onChange={(e) => setFormData({...formData, nome: e.target.value})}
          required
        />
      </div>
      
      <div className="grid grid-cols-2 gap-2">
        <div>
          <Label htmlFor="tipo_leitor">Tipo</Label>
          <Select 
            value={formData.tipo_leitor} 
            onValueChange={(value) => setFormData({...formData, tipo_leitor: value})}
          >
            <SelectTrigger>
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="fixo">Fixo</SelectItem>
              <SelectItem value="mobile">Mobile</SelectItem>
              <SelectItem value="totem">Totem</SelectItem>
              <SelectItem value="handheld">Handheld</SelectItem>
            </SelectContent>
          </Select>
        </div>
        
        <div>
          <Label htmlFor="status">Status</Label>
          <Select 
            value={formData.status} 
            onValueChange={(value) => setFormData({...formData, status: value})}
          >
            <SelectTrigger>
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="ativo">Ativo</SelectItem>
              <SelectItem value="inativo">Inativo</SelectItem>
              <SelectItem value="manutencao">Manutenção</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>
      
      <div>
        <Label htmlFor="localizacao">Localização</Label>
        <Input
          id="localizacao"
          value={formData.localizacao}
          onChange={(e) => setFormData({...formData, localizacao: e.target.value})}
        />
      </div>

      <DialogFooter>
        <Button type="submit">Salvar</Button>
      </DialogFooter>
    </form>
  );
};

// Ponto Acesso Form Component
const PontoAcessoForm: React.FC<{ item?: any; onSave: (data: any) => void }> = ({ item, onSave }) => {
  const [formData, setFormData] = useState({
    codigo: item?.codigo || '',
    nome: item?.nome || '',
    tipo_ponto: item?.tipo_ponto || 'entrada',
    localizacao_descricao: item?.localizacao_descricao || '',
    capacidade_maxima: item?.capacidade_maxima || '',
    ativo: item?.ativo ?? true
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSave(formData);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <Label htmlFor="codigo">Código</Label>
        <Input
          id="codigo"
          value={formData.codigo}
          onChange={(e) => setFormData({...formData, codigo: e.target.value})}
          required
        />
      </div>
      
      <div>
        <Label htmlFor="nome">Nome</Label>
        <Input
          id="nome"
          value={formData.nome}
          onChange={(e) => setFormData({...formData, nome: e.target.value})}
          required
        />
      </div>
      
      <div>
        <Label htmlFor="tipo_ponto">Tipo</Label>
        <Select 
          value={formData.tipo_ponto} 
          onValueChange={(value) => setFormData({...formData, tipo_ponto: value})}
        >
          <SelectTrigger>
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="entrada">Entrada</SelectItem>
            <SelectItem value="saida">Saída</SelectItem>
            <SelectItem value="bidirecional">Bidirecional</SelectItem>
            <SelectItem value="vip">VIP</SelectItem>
          </SelectContent>
        </Select>
      </div>
      
      <div>
        <Label htmlFor="localizacao_descricao">Localização</Label>
        <Textarea
          id="localizacao_descricao"
          value={formData.localizacao_descricao}
          onChange={(e) => setFormData({...formData, localizacao_descricao: e.target.value})}
          rows={3}
        />
      </div>
      
      <div>
        <Label htmlFor="capacidade_maxima">Capacidade Máxima</Label>
        <Input
          id="capacidade_maxima"
          type="number"
          value={formData.capacidade_maxima}
          onChange={(e) => setFormData({...formData, capacidade_maxima: parseInt(e.target.value) || ''})}
        />
      </div>
      
      <div className="flex items-center space-x-2">
        <Switch
          id="ativo"
          checked={formData.ativo}
          onCheckedChange={(checked) => setFormData({...formData, ativo: checked})}
        />
        <Label htmlFor="ativo">Ativo</Label>
      </div>

      <DialogFooter>
        <Button type="submit">Salvar</Button>
      </DialogFooter>
    </form>
  );
};

export default EquipamentosModule;