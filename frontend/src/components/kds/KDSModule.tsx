import React, { useState, useEffect, useRef } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Textarea } from '@/components/ui/textarea';
import { Switch } from '@/components/ui/switch';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { 
  Clock, 
  CheckCircle, 
  AlertCircle, 
  Settings, 
  Plus, 
  Edit,
  Trash2,
  Timer,
  Users,
  ChefHat,
  Package,
  BarChart3,
  RefreshCw,
  Volume2,
  VolumeX,
  Maximize2,
  Minimize2
} from 'lucide-react';
import { toast } from 'sonner';

// Types
interface EstacaoKDS {
  id: number;
  nome: string;
  tipo: 'COZINHA' | 'BAR' | 'EXPEDITOR' | 'ESPECIAL';
  descricao?: string;
  evento_id: number;
  ativo: boolean;
  ordem_exibicao: number;
  configuracoes?: Record<string, any>;
  created_at: string;
  updated_at: string;
}

interface PedidoKDS {
  id: number;
  numero_pedido: string;
  estacao_id: number;
  status: 'PENDENTE' | 'EM_PREPARO' | 'PRONTO' | 'ENTREGUE' | 'CANCELADO';
  tempo_estimado_minutos?: number;
  observacoes?: string;
  comanda_id?: number;
  venda_id?: number;
  prioridade: 'BAIXA' | 'NORMAL' | 'ALTA' | 'URGENTE';
  created_at: string;
  iniciado_em?: string;
  finalizado_em?: string;
  entregue_em?: string;
  itens: ItemPedidoKDS[];
}

interface ItemPedidoKDS {
  id: number;
  pedido_id: number;
  produto_id: number;
  produto_nome: string;
  quantidade: number;
  observacoes?: string;
  pronto: boolean;
}

interface EstacaoForm {
  nome: string;
  tipo: string;
  descricao: string;
  evento_id: number;
  ativo: boolean;
  ordem_exibicao: number;
}

const KDSModule: React.FC = () => {
  const [estacoes, setEstacoes] = useState<EstacaoKDS[]>([]);
  const [pedidos, setPedidos] = useState<PedidoKDS[]>([]);
  const [estacaoAtiva, setEstacaoAtiva] = useState<EstacaoKDS | null>(null);
  const [showEstacaoModal, setShowEstacaoModal] = useState(false);
  const [editingEstacao, setEditingEstacao] = useState<EstacaoKDS | null>(null);
  const [modoTelaCheiaKDS, setModoTelaCheiaKDS] = useState(false);
  const [somHabilitado, setSomHabilitado] = useState(true);
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [loading, setLoading] = useState(false);
  const [analytics, setAnalytics] = useState<any>(null);
  const ws = useRef<WebSocket | null>(null);

  const [estacaoForm, setEstacaoForm] = useState<EstacaoForm>({
    nome: '',
    tipo: 'COZINHA',
    descricao: '',
    evento_id: 1,
    ativo: true,
    ordem_exibicao: 1
  });

  // WebSocket connection
  useEffect(() => {
    if (estacaoAtiva) {
      connectWebSocket();
    }
    return () => {
      if (ws.current) {
        ws.current.close();
      }
    };
  }, [estacaoAtiva]);

  const connectWebSocket = () => {
    if (!estacaoAtiva) return;

    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/api/kds/ws/${estacaoAtiva.id}`;
    
    ws.current = new WebSocket(wsUrl);
    
    ws.current.onopen = () => {
      console.log('WebSocket KDS conectado');
    };
    
    ws.current.onmessage = (event) => {
      const data = JSON.parse(event.data);
      handleWebSocketMessage(data);
    };
    
    ws.current.onclose = () => {
      console.log('WebSocket KDS desconectado');
      // Reconnect after 3 seconds
      if (estacaoAtiva) {
        setTimeout(connectWebSocket, 3000);
      }
    };
    
    ws.current.onerror = (error) => {
      console.error('Erro WebSocket KDS:', error);
    };
  };

  const handleWebSocketMessage = (data: any) => {
    switch (data.type) {
      case 'new_order':
        loadPedidos();
        if (somHabilitado) {
          playNotificationSound();
        }
        toast.success(`Novo pedido: ${data.data.numero_pedido}`);
        break;
      case 'status_change':
        loadPedidos();
        break;
      case 'new_item':
      case 'item_update':
        loadPedidos();
        break;
    }
  };

  const playNotificationSound = () => {
    const audio = new Audio('/api/static/notification.mp3');
    audio.play().catch(() => {
      // Fallback to system beep if audio file not available
      if ('speechSynthesis' in window) {
        const utterance = new SpeechSynthesisUtterance('Novo pedido');
        utterance.volume = 0.1;
        speechSynthesis.speak(utterance);
      }
    });
  };

  // Data loading
  const loadEstacoes = async () => {
    try {
      const response = await fetch('/api/kds/estacoes');
      if (response.ok) {
        const data = await response.json();
        setEstacoes(data);
      }
    } catch (error) {
      console.error('Erro ao carregar estações:', error);
      toast.error('Erro ao carregar estações KDS');
    }
  };

  const loadPedidos = async () => {
    if (!estacaoAtiva) return;

    try {
      const response = await fetch(`/api/kds/pedidos?estacao_id=${estacaoAtiva.id}`);
      if (response.ok) {
        const data = await response.json();
        setPedidos(data.filter((p: PedidoKDS) => 
          ['PENDENTE', 'EM_PREPARO', 'PRONTO'].includes(p.status)
        ));
      }
    } catch (error) {
      console.error('Erro ao carregar pedidos:', error);
    }
  };

  const loadAnalytics = async () => {
    try {
      const response = await fetch('/api/kds/analytics/tempos-preparo');
      if (response.ok) {
        const data = await response.json();
        setAnalytics(data);
      }
    } catch (error) {
      console.error('Erro ao carregar analytics:', error);
    }
  };

  useEffect(() => {
    loadEstacoes();
    loadAnalytics();
  }, []);

  useEffect(() => {
    loadPedidos();
  }, [estacaoAtiva]);

  // Auto refresh
  useEffect(() => {
    if (autoRefresh && estacaoAtiva) {
      const interval = setInterval(loadPedidos, 30000); // 30 seconds
      return () => clearInterval(interval);
    }
  }, [autoRefresh, estacaoAtiva]);

  // CRUD Operations
  const handleCreateEstacao = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/kds/estacoes', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(estacaoForm)
      });

      if (response.ok) {
        toast.success('Estação KDS criada com sucesso');
        setShowEstacaoModal(false);
        loadEstacoes();
        resetEstacaoForm();
      } else {
        const error = await response.json();
        toast.error(error.detail || 'Erro ao criar estação');
      }
    } catch (error) {
      toast.error('Erro ao criar estação KDS');
    }
    setLoading(false);
  };

  const handleUpdateEstacao = async () => {
    if (!editingEstacao) return;

    setLoading(true);
    try {
      const response = await fetch(`/api/kds/estacoes/${editingEstacao.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(estacaoForm)
      });

      if (response.ok) {
        toast.success('Estação KDS atualizada com sucesso');
        setShowEstacaoModal(false);
        setEditingEstacao(null);
        loadEstacoes();
        resetEstacaoForm();
      } else {
        const error = await response.json();
        toast.error(error.detail || 'Erro ao atualizar estação');
      }
    } catch (error) {
      toast.error('Erro ao atualizar estação KDS');
    }
    setLoading(false);
  };

  const handleDeleteEstacao = async (id: number) => {
    if (!confirm('Tem certeza que deseja excluir esta estação?')) return;

    try {
      const response = await fetch(`/api/kds/estacoes/${id}`, {
        method: 'DELETE'
      });

      if (response.ok) {
        toast.success('Estação KDS excluída com sucesso');
        loadEstacoes();
        if (estacaoAtiva?.id === id) {
          setEstacaoAtiva(null);
        }
      } else {
        const error = await response.json();
        toast.error(error.detail || 'Erro ao excluir estação');
      }
    } catch (error) {
      toast.error('Erro ao excluir estação KDS');
    }
  };

  const handleUpdatePedidoStatus = async (pedidoId: number, newStatus: string) => {
    try {
      const response = await fetch(`/api/kds/pedidos/${pedidoId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status: newStatus })
      });

      if (response.ok) {
        toast.success(`Pedido ${newStatus.toLowerCase()}`);
        loadPedidos();
      } else {
        const error = await response.json();
        toast.error(error.detail || 'Erro ao atualizar pedido');
      }
    } catch (error) {
      toast.error('Erro ao atualizar status do pedido');
    }
  };

  // Utility functions
  const resetEstacaoForm = () => {
    setEstacaoForm({
      nome: '',
      tipo: 'COZINHA',
      descricao: '',
      evento_id: 1,
      ativo: true,
      ordem_exibicao: 1
    });
  };

  const openEditEstacaoModal = (estacao: EstacaoKDS) => {
    setEditingEstacao(estacao);
    setEstacaoForm({
      nome: estacao.nome,
      tipo: estacao.tipo,
      descricao: estacao.descricao || '',
      evento_id: estacao.evento_id,
      ativo: estacao.ativo,
      ordem_exibicao: estacao.ordem_exibicao
    });
    setShowEstacaoModal(true);
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'PENDENTE': return 'bg-yellow-500';
      case 'EM_PREPARO': return 'bg-blue-500';
      case 'PRONTO': return 'bg-green-500';
      case 'ENTREGUE': return 'bg-gray-500';
      case 'CANCELADO': return 'bg-red-500';
      default: return 'bg-gray-500';
    }
  };

  const getPriorityColor = (prioridade: string) => {
    switch (prioridade) {
      case 'URGENTE': return 'bg-red-100 text-red-800 border-red-300';
      case 'ALTA': return 'bg-orange-100 text-orange-800 border-orange-300';
      case 'NORMAL': return 'bg-blue-100 text-blue-800 border-blue-300';
      case 'BAIXA': return 'bg-gray-100 text-gray-800 border-gray-300';
      default: return 'bg-gray-100 text-gray-800 border-gray-300';
    }
  };

  const formatTempo = (timestamp?: string) => {
    if (!timestamp) return '-';
    const diff = Math.floor((new Date().getTime() - new Date(timestamp).getTime()) / 60000);
    return `${diff}m`;
  };

  if (modoTelaCheiaKDS && estacaoAtiva) {
    return (
      <div className="fixed inset-0 bg-black text-white z-50 overflow-auto">
        <div className="p-4">
          <div className="flex justify-between items-center mb-6">
            <h1 className="text-3xl font-bold text-white">
              {estacaoAtiva.nome} - KDS
            </h1>
            <div className="flex items-center space-x-4">
              <Button
                variant="outline"
                onClick={() => setSomHabilitado(!somHabilitado)}
                className="text-white border-white hover:bg-white hover:text-black"
              >
                {somHabilitado ? <Volume2 size={20} /> : <VolumeX size={20} />}
              </Button>
              <Button
                variant="outline"
                onClick={() => setModoTelaCheiaKDS(false)}
                className="text-white border-white hover:bg-white hover:text-black"
              >
                <Minimize2 size={20} />
              </Button>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
            {pedidos.map((pedido) => (
              <Card key={pedido.id} className={`border-2 ${pedido.prioridade === 'URGENTE' ? 'border-red-500 shadow-red-500/20 shadow-lg' : 'border-gray-700'} bg-gray-800`}>
                <CardHeader className="pb-2">
                  <div className="flex justify-between items-center">
                    <CardTitle className="text-lg text-white">
                      #{pedido.numero_pedido}
                    </CardTitle>
                    <Badge className={`${getStatusColor(pedido.status)} text-white`}>
                      {pedido.status}
                    </Badge>
                  </div>
                  <div className="flex justify-between items-center text-sm">
                    <Badge className={getPriorityColor(pedido.prioridade)}>
                      {pedido.prioridade}
                    </Badge>
                    <span className="text-gray-400 flex items-center">
                      <Clock size={14} className="mr-1" />
                      {formatTempo(pedido.created_at)}
                    </span>
                  </div>
                </CardHeader>
                <CardContent className="space-y-2">
                  {pedido.itens.map((item) => (
                    <div key={item.id} className={`p-2 rounded border ${item.pronto ? 'bg-green-900 border-green-700' : 'bg-gray-700 border-gray-600'}`}>
                      <div className="flex justify-between items-center">
                        <span className="text-white font-medium">
                          {item.quantidade}x {item.produto_nome}
                        </span>
                        {item.pronto && <CheckCircle size={16} className="text-green-400" />}
                      </div>
                      {item.observacoes && (
                        <p className="text-sm text-gray-300 mt-1">{item.observacoes}</p>
                      )}
                    </div>
                  ))}

                  <div className="flex space-x-2 pt-2">
                    {pedido.status === 'PENDENTE' && (
                      <Button
                        size="sm"
                        onClick={() => handleUpdatePedidoStatus(pedido.id, 'EM_PREPARO')}
                        className="flex-1 bg-blue-600 hover:bg-blue-700 text-white"
                      >
                        <Timer size={14} className="mr-1" />
                        Iniciar
                      </Button>
                    )}
                    {pedido.status === 'EM_PREPARO' && (
                      <Button
                        size="sm"
                        onClick={() => handleUpdatePedidoStatus(pedido.id, 'PRONTO')}
                        className="flex-1 bg-green-600 hover:bg-green-700 text-white"
                      >
                        <CheckCircle size={14} className="mr-1" />
                        Pronto
                      </Button>
                    )}
                    {pedido.status === 'PRONTO' && (
                      <Button
                        size="sm"
                        onClick={() => handleUpdatePedidoStatus(pedido.id, 'ENTREGUE')}
                        className="flex-1 bg-gray-600 hover:bg-gray-700 text-white"
                      >
                        <Package size={14} className="mr-1" />
                        Entregue
                      </Button>
                    )}
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Sistema KDS (Kitchen Display)</h1>
        <div className="flex items-center space-x-2">
          <Button onClick={() => setShowEstacaoModal(true)}>
            <Plus size={16} className="mr-2" />
            Nova Estação
          </Button>
        </div>
      </div>

      <Tabs value={estacaoAtiva ? 'display' : 'estacoes'} className="w-full">
        <TabsList>
          <TabsTrigger value="estacoes">Estações</TabsTrigger>
          <TabsTrigger value="display" disabled={!estacaoAtiva}>
            Display KDS
          </TabsTrigger>
          <TabsTrigger value="analytics">Analytics</TabsTrigger>
        </TabsList>

        <TabsContent value="estacoes" className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {estacoes.map((estacao) => (
              <Card key={estacao.id}>
                <CardHeader>
                  <div className="flex justify-between items-center">
                    <CardTitle className="flex items-center">
                      <ChefHat size={20} className="mr-2" />
                      {estacao.nome}
                    </CardTitle>
                    <Badge variant={estacao.ativo ? 'default' : 'secondary'}>
                      {estacao.ativo ? 'Ativo' : 'Inativo'}
                    </Badge>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    <p className="text-sm text-gray-600">
                      <strong>Tipo:</strong> {estacao.tipo}
                    </p>
                    {estacao.descricao && (
                      <p className="text-sm text-gray-600">
                        <strong>Descrição:</strong> {estacao.descricao}
                      </p>
                    )}
                    <p className="text-sm text-gray-600">
                      <strong>Ordem:</strong> {estacao.ordem_exibicao}
                    </p>
                  </div>
                  
                  <div className="flex space-x-2 mt-4">
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => setEstacaoAtiva(estacao)}
                      disabled={!estacao.ativo}
                    >
                      Usar KDS
                    </Button>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => openEditEstacaoModal(estacao)}
                    >
                      <Edit size={14} />
                    </Button>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => handleDeleteEstacao(estacao.id)}
                    >
                      <Trash2 size={14} />
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="display" className="space-y-4">
          {estacaoAtiva && (
            <>
              <div className="flex justify-between items-center">
                <h2 className="text-xl font-semibold">
                  {estacaoAtiva.nome} - Display KDS
                </h2>
                <div className="flex items-center space-x-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setAutoRefresh(!autoRefresh)}
                  >
                    <RefreshCw size={16} className={autoRefresh ? 'animate-spin' : ''} />
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setSomHabilitado(!somHabilitado)}
                  >
                    {somHabilitado ? <Volume2 size={16} /> : <VolumeX size={16} />}
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setModoTelaCheiaKDS(true)}
                  >
                    <Maximize2 size={16} />
                  </Button>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {pedidos.map((pedido) => (
                  <Card key={pedido.id} className={`border-2 ${pedido.prioridade === 'URGENTE' ? 'border-red-500 shadow-red-500/20 shadow-lg' : ''}`}>
                    <CardHeader className="pb-2">
                      <div className="flex justify-between items-center">
                        <CardTitle className="text-lg">
                          #{pedido.numero_pedido}
                        </CardTitle>
                        <Badge className={`${getStatusColor(pedido.status)} text-white`}>
                          {pedido.status}
                        </Badge>
                      </div>
                      <div className="flex justify-between items-center text-sm">
                        <Badge className={getPriorityColor(pedido.prioridade)}>
                          {pedido.prioridade}
                        </Badge>
                        <span className="text-gray-500 flex items-center">
                          <Clock size={14} className="mr-1" />
                          {formatTempo(pedido.created_at)}
                        </span>
                      </div>
                    </CardHeader>
                    <CardContent className="space-y-2">
                      {pedido.itens.map((item) => (
                        <div key={item.id} className={`p-2 rounded border ${item.pronto ? 'bg-green-50 border-green-200' : 'bg-gray-50'}`}>
                          <div className="flex justify-between items-center">
                            <span className="font-medium">
                              {item.quantidade}x {item.produto_nome}
                            </span>
                            {item.pronto && <CheckCircle size={16} className="text-green-600" />}
                          </div>
                          {item.observacoes && (
                            <p className="text-sm text-gray-600 mt-1">{item.observacoes}</p>
                          )}
                        </div>
                      ))}

                      <div className="flex space-x-2 pt-2">
                        {pedido.status === 'PENDENTE' && (
                          <Button
                            size="sm"
                            onClick={() => handleUpdatePedidoStatus(pedido.id, 'EM_PREPARO')}
                            className="flex-1"
                          >
                            <Timer size={14} className="mr-1" />
                            Iniciar
                          </Button>
                        )}
                        {pedido.status === 'EM_PREPARO' && (
                          <Button
                            size="sm"
                            onClick={() => handleUpdatePedidoStatus(pedido.id, 'PRONTO')}
                            className="flex-1 bg-green-600 hover:bg-green-700"
                          >
                            <CheckCircle size={14} className="mr-1" />
                            Pronto
                          </Button>
                        )}
                        {pedido.status === 'PRONTO' && (
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => handleUpdatePedidoStatus(pedido.id, 'ENTREGUE')}
                            className="flex-1"
                          >
                            <Package size={14} className="mr-1" />
                            Entregue
                          </Button>
                        )}
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </>
          )}
        </TabsContent>

        <TabsContent value="analytics" className="space-y-4">
          {analytics && (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center">
                    <BarChart3 size={20} className="mr-2" />
                    Total de Pedidos
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{analytics.total_pedidos}</div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center">
                    <Timer size={20} className="mr-2" />
                    Tempo Médio
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">
                    {analytics.tempo_medio_preparo}min
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center">
                    <Users size={20} className="mr-2" />
                    Estações Ativas
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">
                    {estacoes.filter(e => e.ativo).length}
                  </div>
                </CardContent>
              </Card>
            </div>
          )}
        </TabsContent>
      </Tabs>

      {/* Modal de Estação */}
      <Dialog open={showEstacaoModal} onOpenChange={setShowEstacaoModal}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle>
              {editingEstacao ? 'Editar Estação KDS' : 'Nova Estação KDS'}
            </DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <Label htmlFor="nome">Nome da Estação</Label>
              <Input
                id="nome"
                value={estacaoForm.nome}
                onChange={(e) => setEstacaoForm({ ...estacaoForm, nome: e.target.value })}
                placeholder="Ex: Cozinha Principal"
              />
            </div>

            <div>
              <Label htmlFor="tipo">Tipo de Estação</Label>
              <Select
                value={estacaoForm.tipo}
                onValueChange={(value) => setEstacaoForm({ ...estacaoForm, tipo: value })}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Selecione o tipo" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="COZINHA">Cozinha</SelectItem>
                  <SelectItem value="BAR">Bar</SelectItem>
                  <SelectItem value="EXPEDITOR">Expeditor</SelectItem>
                  <SelectItem value="ESPECIAL">Especial</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div>
              <Label htmlFor="descricao">Descrição</Label>
              <Textarea
                id="descricao"
                value={estacaoForm.descricao}
                onChange={(e) => setEstacaoForm({ ...estacaoForm, descricao: e.target.value })}
                placeholder="Descrição opcional da estação"
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="ordem">Ordem</Label>
                <Input
                  id="ordem"
                  type="number"
                  value={estacaoForm.ordem_exibicao}
                  onChange={(e) => setEstacaoForm({ ...estacaoForm, ordem_exibicao: parseInt(e.target.value) })}
                />
              </div>

              <div className="flex items-center space-x-2 pt-6">
                <Switch
                  id="ativo"
                  checked={estacaoForm.ativo}
                  onCheckedChange={(checked) => setEstacaoForm({ ...estacaoForm, ativo: checked })}
                />
                <Label htmlFor="ativo">Ativa</Label>
              </div>
            </div>

            <div className="flex justify-end space-x-2 pt-4">
              <Button
                variant="outline"
                onClick={() => {
                  setShowEstacaoModal(false);
                  setEditingEstacao(null);
                  resetEstacaoForm();
                }}
              >
                Cancelar
              </Button>
              <Button
                onClick={editingEstacao ? handleUpdateEstacao : handleCreateEstacao}
                disabled={loading || !estacaoForm.nome}
              >
                {loading ? 'Salvando...' : editingEstacao ? 'Atualizar' : 'Criar'}
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default KDSModule;