import React, { useState, useEffect, useRef, useCallback } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Switch } from '@/components/ui/switch';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { 
  Table2, 
  Plus, 
  Edit,
  Trash2,
  Users,
  BarChart3,
  Layout,
  QrCode,
  Settings,
  Move,
  RotateCw,
  Copy,
  Maximize2,
  Minimize2,
  Grid3X3,
  Palette,
  Save,
  RefreshCw
} from 'lucide-react';
import { toast } from 'sonner';

// Types
interface Mesa {
  id: number;
  numero: string;
  nome: string;
  tipo: 'NORMAL' | 'VIP' | 'REDONDA' | 'RETANGULAR' | 'BALCAO' | 'EXTERNA';
  status: 'LIVRE' | 'OCUPADA' | 'RESERVADA' | 'MANUTENCAO' | 'INATIVA';
  capacidade: number;
  evento_id: number;
  posicao_x: number;
  posicao_y: number;
  largura: number;
  altura: number;
  rotacao?: number;
  cor?: string;
  ativo: boolean;
  created_at: string;
  ocupada_em?: string;
  liberada_em?: string;
  reservada_em?: string;
}

interface MesaForm {
  numero: string;
  nome: string;
  tipo: string;
  capacidade: number;
  evento_id: number;
  posicao_x: number;
  posicao_y: number;
  largura: number;
  altura: number;
  rotacao: number;
  cor: string;
  ativo: boolean;
}

interface LayoutTemplate {
  id: string;
  nome: string;
  descricao: string;
  mesas: any[];
}

const MesasModule: React.FC = () => {
  const [mesas, setMesas] = useState<Mesa[]>([]);
  const [showMesaModal, setShowMesaModal] = useState(false);
  const [showBatchModal, setShowBatchModal] = useState(false);
  const [showTemplateModal, setShowTemplateModal] = useState(false);
  const [editingMesa, setEditingMesa] = useState<Mesa | null>(null);
  const [selectedMesas, setSelectedMesas] = useState<number[]>([]);
  const [modoLayoutDesigner, setModoLayoutDesigner] = useState(false);
  const [modoTelaCheiaLayout, setModoTelaCheiaLayout] = useState(false);
  const [loading, setLoading] = useState(false);
  const [analytics, setAnalytics] = useState<any>(null);
  const [templates, setTemplates] = useState<LayoutTemplate[]>([]);
  const [draggedMesa, setDraggedMesa] = useState<Mesa | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const ws = useRef<WebSocket | null>(null);
  const layoutRef = useRef<HTMLDivElement>(null);

  const [mesaForm, setMesaForm] = useState<MesaForm>({
    numero: '',
    nome: '',
    tipo: 'NORMAL',
    capacidade: 4,
    evento_id: 1,
    posicao_x: 100,
    posicao_y: 100,
    largura: 100,
    altura: 100,
    rotacao: 0,
    cor: '#3B82F6',
    ativo: true
  });

  const [batchForm, setBatchForm] = useState({
    quantidade: 10,
    tipo: 'NORMAL',
    capacidade: 4,
    prefixo: 'Mesa'
  });

  // WebSocket connection
  useEffect(() => {
    connectWebSocket();
    return () => {
      if (ws.current) {
        ws.current.close();
      }
    };
  }, []);

  const connectWebSocket = () => {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/api/mesas/ws/1`; // Default event ID
    
    ws.current = new WebSocket(wsUrl);
    
    ws.current.onopen = () => {
      console.log('WebSocket Mesas conectado');
    };
    
    ws.current.onmessage = (event) => {
      const data = JSON.parse(event.data);
      handleWebSocketMessage(data);
    };
    
    ws.current.onclose = () => {
      console.log('WebSocket Mesas desconectado');
      setTimeout(connectWebSocket, 3000);
    };
    
    ws.current.onerror = (error) => {
      console.error('Erro WebSocket Mesas:', error);
    };
  };

  const handleWebSocketMessage = (data: any) => {
    switch (data.type) {
      case 'new_table':
        loadMesas();
        toast.success(`Nova mesa criada: ${data.data.nome}`);
        break;
      case 'table_update':
        loadMesas();
        break;
      case 'table_deleted':
        loadMesas();
        toast.success('Mesa excluída');
        break;
      case 'layout_update':
        loadMesas();
        break;
      case 'batch_created':
        loadMesas();
        toast.success(`${data.quantidade} mesas criadas em lote`);
        break;
      case 'status_change':
        loadMesas();
        break;
    }
  };

  // Data loading
  const loadMesas = async () => {
    try {
      const response = await fetch('/api/mesas?evento_id=1'); // Default event ID
      if (response.ok) {
        const data = await response.json();
        setMesas(data);
      }
    } catch (error) {
      console.error('Erro ao carregar mesas:', error);
      toast.error('Erro ao carregar mesas');
    }
  };

  const loadAnalytics = async () => {
    try {
      const response = await fetch('/api/mesas/analytics/1'); // Default event ID
      if (response.ok) {
        const data = await response.json();
        setAnalytics(data);
      }
    } catch (error) {
      console.error('Erro ao carregar analytics:', error);
    }
  };

  const loadTemplates = async () => {
    try {
      const response = await fetch('/api/mesas/templates');
      if (response.ok) {
        const data = await response.json();
        setTemplates(data.templates);
      }
    } catch (error) {
      console.error('Erro ao carregar templates:', error);
    }
  };

  useEffect(() => {
    loadMesas();
    loadAnalytics();
    loadTemplates();
  }, []);

  // CRUD Operations
  const handleCreateMesa = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/mesas', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(mesaForm)
      });

      if (response.ok) {
        toast.success('Mesa criada com sucesso');
        setShowMesaModal(false);
        loadMesas();
        resetMesaForm();
      } else {
        const error = await response.json();
        toast.error(error.detail || 'Erro ao criar mesa');
      }
    } catch (error) {
      toast.error('Erro ao criar mesa');
    }
    setLoading(false);
  };

  const handleUpdateMesa = async () => {
    if (!editingMesa) return;

    setLoading(true);
    try {
      const response = await fetch(`/api/mesas/${editingMesa.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(mesaForm)
      });

      if (response.ok) {
        toast.success('Mesa atualizada com sucesso');
        setShowMesaModal(false);
        setEditingMesa(null);
        loadMesas();
        resetMesaForm();
      } else {
        const error = await response.json();
        toast.error(error.detail || 'Erro ao atualizar mesa');
      }
    } catch (error) {
      toast.error('Erro ao atualizar mesa');
    }
    setLoading(false);
  };

  const handleDeleteMesa = async (id: number) => {
    if (!confirm('Tem certeza que deseja excluir esta mesa?')) return;

    try {
      const response = await fetch(`/api/mesas/${id}`, {
        method: 'DELETE'
      });

      if (response.ok) {
        toast.success('Mesa excluída com sucesso');
        loadMesas();
      } else {
        const error = await response.json();
        toast.error(error.detail || 'Erro ao excluir mesa');
      }
    } catch (error) {
      toast.error('Erro ao excluir mesa');
    }
  };

  const handleBatchCreate = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/mesas/batch-create', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          evento_id: 1,
          ...batchForm
        })
      });

      if (response.ok) {
        const result = await response.json();
        toast.success(result.message);
        setShowBatchModal(false);
        loadMesas();
      } else {
        const error = await response.json();
        toast.error(error.detail || 'Erro ao criar mesas em lote');
      }
    } catch (error) {
      toast.error('Erro ao criar mesas em lote');
    }
    setLoading(false);
  };

  const handleStatusChange = async (mesaId: number, newStatus: string) => {
    try {
      const response = await fetch(`/api/mesas/${mesaId}/status`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status: newStatus })
      });

      if (response.ok) {
        toast.success(`Status alterado para ${newStatus}`);
        loadMesas();
      } else {
        const error = await response.json();
        toast.error(error.detail || 'Erro ao alterar status');
      }
    } catch (error) {
      toast.error('Erro ao alterar status da mesa');
    }
  };

  const handleApplyTemplate = async (templateId: string) => {
    if (!confirm('Isso irá substituir todas as mesas existentes. Continuar?')) return;

    try {
      const response = await fetch('/api/mesas/apply-template', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          evento_id: 1,
          template_id: templateId,
          clear_existing: true
        })
      });

      if (response.ok) {
        const result = await response.json();
        toast.success(result.message);
        setShowTemplateModal(false);
        loadMesas();
      } else {
        const error = await response.json();
        toast.error(error.detail || 'Erro ao aplicar template');
      }
    } catch (error) {
      toast.error('Erro ao aplicar template');
    }
  };

  // Layout Designer Functions
  const handleMouseDown = (mesa: Mesa, event: React.MouseEvent) => {
    if (!modoLayoutDesigner) return;
    
    event.preventDefault();
    setDraggedMesa(mesa);
    setIsDragging(true);
  };

  const handleMouseMove = useCallback((event: MouseEvent) => {
    if (!isDragging || !draggedMesa || !layoutRef.current) return;

    const rect = layoutRef.current.getBoundingClientRect();
    const x = event.clientX - rect.left;
    const y = event.clientY - rect.top;

    // Update mesa position visually (optimistic update)
    setMesas(prev => prev.map(mesa => 
      mesa.id === draggedMesa.id 
        ? { ...mesa, posicao_x: Math.max(0, x - 50), posicao_y: Math.max(0, y - 50) }
        : mesa
    ));
  }, [isDragging, draggedMesa]);

  const handleMouseUp = useCallback(async () => {
    if (!isDragging || !draggedMesa) return;

    setIsDragging(false);
    
    // Save position to backend
    const mesa = mesas.find(m => m.id === draggedMesa.id);
    if (mesa) {
      try {
        await fetch(`/api/mesas/${mesa.id}`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            posicao_x: mesa.posicao_x,
            posicao_y: mesa.posicao_y
          })
        });
      } catch (error) {
        console.error('Erro ao salvar posição:', error);
        toast.error('Erro ao salvar posição da mesa');
      }
    }
    
    setDraggedMesa(null);
  }, [isDragging, draggedMesa, mesas]);

  useEffect(() => {
    if (modoLayoutDesigner) {
      document.addEventListener('mousemove', handleMouseMove);
      document.addEventListener('mouseup', handleMouseUp);
      
      return () => {
        document.removeEventListener('mousemove', handleMouseMove);
        document.removeEventListener('mouseup', handleMouseUp);
      };
    }
  }, [modoLayoutDesigner, handleMouseMove, handleMouseUp]);

  // Utility functions
  const resetMesaForm = () => {
    setMesaForm({
      numero: '',
      nome: '',
      tipo: 'NORMAL',
      capacidade: 4,
      evento_id: 1,
      posicao_x: 100,
      posicao_y: 100,
      largura: 100,
      altura: 100,
      rotacao: 0,
      cor: '#3B82F6',
      ativo: true
    });
  };

  const openEditMesaModal = (mesa: Mesa) => {
    setEditingMesa(mesa);
    setMesaForm({
      numero: mesa.numero,
      nome: mesa.nome,
      tipo: mesa.tipo,
      capacidade: mesa.capacidade,
      evento_id: mesa.evento_id,
      posicao_x: mesa.posicao_x,
      posicao_y: mesa.posicao_y,
      largura: mesa.largura,
      altura: mesa.altura,
      rotacao: mesa.rotacao || 0,
      cor: mesa.cor || '#3B82F6',
      ativo: mesa.ativo
    });
    setShowMesaModal(true);
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'LIVRE': return 'bg-green-500';
      case 'OCUPADA': return 'bg-red-500';
      case 'RESERVADA': return 'bg-yellow-500';
      case 'MANUTENCAO': return 'bg-orange-500';
      case 'INATIVA': return 'bg-gray-500';
      default: return 'bg-gray-500';
    }
  };

  const getTipoIcon = (tipo: string) => {
    switch (tipo) {
      case 'REDONDA': return '⭕';
      case 'RETANGULAR': return '⬛';
      case 'BALCAO': return '▬';
      case 'VIP': return '⭐';
      case 'EXTERNA': return '🌿';
      default: return '⬜';
    }
  };

  // Layout Designer Component
  const LayoutDesigner = () => (
    <div 
      ref={layoutRef}
      className="relative w-full h-96 bg-gray-50 border-2 border-dashed border-gray-300 overflow-auto"
      style={{ minHeight: '600px' }}
    >
      {mesas.map((mesa) => (
        <div
          key={mesa.id}
          className={`absolute border-2 rounded-lg flex flex-col items-center justify-center text-white font-semibold cursor-${modoLayoutDesigner ? 'move' : 'pointer'} transition-all duration-200 hover:shadow-lg`}
          style={{
            left: mesa.posicao_x,
            top: mesa.posicao_y,
            width: mesa.largura,
            height: mesa.altura,
            backgroundColor: mesa.cor || '#3B82F6',
            transform: `rotate(${mesa.rotacao || 0}deg)`,
            borderColor: selectedMesas.includes(mesa.id) ? '#F59E0B' : mesa.cor || '#3B82F6',
            borderWidth: selectedMesas.includes(mesa.id) ? '3px' : '2px'
          }}
          onMouseDown={(e) => handleMouseDown(mesa, e)}
          onClick={() => {
            if (!modoLayoutDesigner) {
              if (selectedMesas.includes(mesa.id)) {
                setSelectedMesas(prev => prev.filter(id => id !== mesa.id));
              } else {
                setSelectedMesas(prev => [...prev, mesa.id]);
              }
            }
          }}
        >
          <div className="text-xs">{getTipoIcon(mesa.tipo)}</div>
          <div className="text-xs">{mesa.numero}</div>
          <div className="text-xs">{mesa.capacidade}p</div>
          <Badge 
            className={`absolute -top-2 -right-2 text-xs ${getStatusColor(mesa.status)} border-0`}
            style={{ fontSize: '10px', padding: '2px 4px' }}
          >
            {mesa.status.charAt(0)}
          </Badge>
        </div>
      ))}
    </div>
  );

  if (modoTelaCheiaLayout) {
    return (
      <div className="fixed inset-0 bg-white z-50 overflow-auto">
        <div className="p-4">
          <div className="flex justify-between items-center mb-6">
            <h1 className="text-3xl font-bold">Layout de Mesas - Modo Tela Cheia</h1>
            <div className="flex items-center space-x-4">
              <Button
                variant="outline"
                onClick={() => setModoLayoutDesigner(!modoLayoutDesigner)}
              >
                {modoLayoutDesigner ? <Save size={20} /> : <Edit size={20} />}
                {modoLayoutDesigner ? 'Salvar Layout' : 'Editar Layout'}
              </Button>
              <Button
                variant="outline"
                onClick={() => setModoTelaCheiaLayout(false)}
              >
                <Minimize2 size={20} />
                Sair Tela Cheia
              </Button>
            </div>
          </div>

          <div className="relative" style={{ minHeight: '800px' }}>
            <LayoutDesigner />
          </div>

          {selectedMesas.length > 0 && (
            <div className="fixed bottom-4 left-1/2 transform -translate-x-1/2 bg-white p-4 rounded-lg shadow-lg border">
              <div className="flex items-center space-x-4">
                <span>{selectedMesas.length} mesa(s) selecionada(s)</span>
                <Button size="sm" variant="outline">
                  <Move size={16} className="mr-2" />
                  Mover
                </Button>
                <Button size="sm" variant="outline">
                  <Copy size={16} className="mr-2" />
                  Duplicar
                </Button>
                <Button size="sm" variant="outline">
                  <Trash2 size={16} className="mr-2" />
                  Excluir
                </Button>
              </div>
            </div>
          )}
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Sistema de Mesas</h1>
        <div className="flex items-center space-x-2">
          <Button variant="outline" onClick={() => setShowTemplateModal(true)}>
            <Grid3X3 size={16} className="mr-2" />
            Templates
          </Button>
          <Button variant="outline" onClick={() => setShowBatchModal(true)}>
            <Copy size={16} className="mr-2" />
            Lote
          </Button>
          <Button onClick={() => setShowMesaModal(true)}>
            <Plus size={16} className="mr-2" />
            Nova Mesa
          </Button>
        </div>
      </div>

      <Tabs defaultValue="layout" className="w-full">
        <TabsList>
          <TabsTrigger value="layout">Layout</TabsTrigger>
          <TabsTrigger value="lista">Lista</TabsTrigger>
          <TabsTrigger value="analytics">Analytics</TabsTrigger>
        </TabsList>

        <TabsContent value="layout" className="space-y-4">
          <div className="flex justify-between items-center">
            <h2 className="text-xl font-semibold">Layout do Salão</h2>
            <div className="flex items-center space-x-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => setModoLayoutDesigner(!modoLayoutDesigner)}
              >
                {modoLayoutDesigner ? <Save size={16} /> : <Edit size={16} />}
                {modoLayoutDesigner ? 'Salvar' : 'Editar'}
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={() => setModoTelaCheiaLayout(true)}
              >
                <Maximize2 size={16} />
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={loadMesas}
              >
                <RefreshCw size={16} />
              </Button>
            </div>
          </div>

          <LayoutDesigner />

          {selectedMesas.length > 0 && (
            <Alert>
              <AlertDescription>
                {selectedMesas.length} mesa(s) selecionada(s). Use as ferramentas acima para realizar ações em lote.
              </AlertDescription>
            </Alert>
          )}
        </TabsContent>

        <TabsContent value="lista" className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
            {mesas.map((mesa) => (
              <Card key={mesa.id} className={`border-l-4 ${getStatusColor(mesa.status).replace('bg-', 'border-')}`}>
                <CardHeader className="pb-2">
                  <div className="flex justify-between items-center">
                    <CardTitle className="text-lg flex items-center">
                      <span className="mr-2">{getTipoIcon(mesa.tipo)}</span>
                      {mesa.nome}
                    </CardTitle>
                    <Badge className={`${getStatusColor(mesa.status)} text-white`}>
                      {mesa.status}
                    </Badge>
                  </div>
                  <div className="flex items-center text-sm text-gray-600">
                    <Users size={14} className="mr-1" />
                    {mesa.capacidade} pessoas
                  </div>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div className="text-sm">
                    <p><strong>Número:</strong> {mesa.numero}</p>
                    <p><strong>Tipo:</strong> {mesa.tipo}</p>
                    <p><strong>Posição:</strong> ({mesa.posicao_x}, {mesa.posicao_y})</p>
                  </div>

                  <div className="grid grid-cols-2 gap-2">
                    <Select
                      value={mesa.status}
                      onValueChange={(value) => handleStatusChange(mesa.id, value)}
                    >
                      <SelectTrigger className="text-xs">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="LIVRE">Livre</SelectItem>
                        <SelectItem value="OCUPADA">Ocupada</SelectItem>
                        <SelectItem value="RESERVADA">Reservada</SelectItem>
                        <SelectItem value="MANUTENCAO">Manutenção</SelectItem>
                        <SelectItem value="INATIVA">Inativa</SelectItem>
                      </SelectContent>
                    </Select>

                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => {
                        navigator.clipboard.writeText(`${window.location.origin}/menu/1?mesa=${mesa.id}`);
                        toast.success('Link QR Code copiado!');
                      }}
                    >
                      <QrCode size={14} />
                    </Button>
                  </div>

                  <div className="flex space-x-2">
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => openEditMesaModal(mesa)}
                      className="flex-1"
                    >
                      <Edit size={14} />
                    </Button>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => handleDeleteMesa(mesa.id)}
                      className="flex-1"
                    >
                      <Trash2 size={14} />
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="analytics" className="space-y-4">
          {analytics && (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center">
                    <Table2 size={20} className="mr-2" />
                    Total Mesas
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{analytics.total_mesas}</div>
                  <div className="text-sm text-gray-600">
                    {analytics.mesas_ativas} ativas
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center">
                    <BarChart3 size={20} className="mr-2" />
                    Taxa Ocupação
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{analytics.taxa_ocupacao}%</div>
                  <div className="text-sm text-gray-600">
                    {analytics.mesas_ocupadas} ocupadas
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center">
                    <Users size={20} className="mr-2" />
                    Capacidade Total
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{analytics.capacidade_total}</div>
                  <div className="text-sm text-gray-600">pessoas</div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Status das Mesas</CardTitle>
                </CardHeader>
                <CardContent className="space-y-2">
                  {Object.entries(analytics.por_status).map(([status, count]) => (
                    <div key={status} className="flex justify-between items-center">
                      <span className="text-sm">{status}</span>
                      <Badge variant="secondary">{count as number}</Badge>
                    </div>
                  ))}
                </CardContent>
              </Card>
            </div>
          )}
        </TabsContent>
      </Tabs>

      {/* Modal de Mesa */}
      <Dialog open={showMesaModal} onOpenChange={setShowMesaModal}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>
              {editingMesa ? 'Editar Mesa' : 'Nova Mesa'}
            </DialogTitle>
          </DialogHeader>
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-4">
              <div>
                <Label htmlFor="numero">Número da Mesa</Label>
                <Input
                  id="numero"
                  value={mesaForm.numero}
                  onChange={(e) => setMesaForm({ ...mesaForm, numero: e.target.value })}
                  placeholder="Ex: 01"
                />
              </div>

              <div>
                <Label htmlFor="nome">Nome da Mesa</Label>
                <Input
                  id="nome"
                  value={mesaForm.nome}
                  onChange={(e) => setMesaForm({ ...mesaForm, nome: e.target.value })}
                  placeholder="Ex: Mesa 01"
                />
              </div>

              <div>
                <Label htmlFor="tipo">Tipo</Label>
                <Select
                  value={mesaForm.tipo}
                  onValueChange={(value) => setMesaForm({ ...mesaForm, tipo: value })}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="NORMAL">Normal</SelectItem>
                    <SelectItem value="VIP">VIP</SelectItem>
                    <SelectItem value="REDONDA">Redonda</SelectItem>
                    <SelectItem value="RETANGULAR">Retangular</SelectItem>
                    <SelectItem value="BALCAO">Balcão</SelectItem>
                    <SelectItem value="EXTERNA">Externa</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div>
                <Label htmlFor="capacidade">Capacidade</Label>
                <Input
                  id="capacidade"
                  type="number"
                  value={mesaForm.capacidade}
                  onChange={(e) => setMesaForm({ ...mesaForm, capacidade: parseInt(e.target.value) })}
                />
              </div>
            </div>

            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-2">
                <div>
                  <Label htmlFor="posicao_x">Posição X</Label>
                  <Input
                    id="posicao_x"
                    type="number"
                    value={mesaForm.posicao_x}
                    onChange={(e) => setMesaForm({ ...mesaForm, posicao_x: parseInt(e.target.value) })}
                  />
                </div>
                <div>
                  <Label htmlFor="posicao_y">Posição Y</Label>
                  <Input
                    id="posicao_y"
                    type="number"
                    value={mesaForm.posicao_y}
                    onChange={(e) => setMesaForm({ ...mesaForm, posicao_y: parseInt(e.target.value) })}
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-2">
                <div>
                  <Label htmlFor="largura">Largura</Label>
                  <Input
                    id="largura"
                    type="number"
                    value={mesaForm.largura}
                    onChange={(e) => setMesaForm({ ...mesaForm, largura: parseInt(e.target.value) })}
                  />
                </div>
                <div>
                  <Label htmlFor="altura">Altura</Label>
                  <Input
                    id="altura"
                    type="number"
                    value={mesaForm.altura}
                    onChange={(e) => setMesaForm({ ...mesaForm, altura: parseInt(e.target.value) })}
                  />
                </div>
              </div>

              <div>
                <Label htmlFor="rotacao">Rotação (graus)</Label>
                <Input
                  id="rotacao"
                  type="number"
                  value={mesaForm.rotacao}
                  onChange={(e) => setMesaForm({ ...mesaForm, rotacao: parseInt(e.target.value) })}
                />
              </div>

              <div>
                <Label htmlFor="cor">Cor</Label>
                <Input
                  id="cor"
                  type="color"
                  value={mesaForm.cor}
                  onChange={(e) => setMesaForm({ ...mesaForm, cor: e.target.value })}
                />
              </div>

              <div className="flex items-center space-x-2">
                <Switch
                  id="ativo"
                  checked={mesaForm.ativo}
                  onCheckedChange={(checked) => setMesaForm({ ...mesaForm, ativo: checked })}
                />
                <Label htmlFor="ativo">Mesa Ativa</Label>
              </div>
            </div>
          </div>

          <div className="flex justify-end space-x-2 pt-4">
            <Button
              variant="outline"
              onClick={() => {
                setShowMesaModal(false);
                setEditingMesa(null);
                resetMesaForm();
              }}
            >
              Cancelar
            </Button>
            <Button
              onClick={editingMesa ? handleUpdateMesa : handleCreateMesa}
              disabled={loading || !mesaForm.numero}
            >
              {loading ? 'Salvando...' : editingMesa ? 'Atualizar' : 'Criar'}
            </Button>
          </div>
        </DialogContent>
      </Dialog>

      {/* Modal de Criação em Lote */}
      <Dialog open={showBatchModal} onOpenChange={setShowBatchModal}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle>Criar Mesas em Lote</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <Label htmlFor="quantidade">Quantidade</Label>
              <Input
                id="quantidade"
                type="number"
                value={batchForm.quantidade}
                onChange={(e) => setBatchForm({ ...batchForm, quantidade: parseInt(e.target.value) })}
                min="1"
                max="100"
              />
            </div>

            <div>
              <Label htmlFor="prefixo">Prefixo</Label>
              <Input
                id="prefixo"
                value={batchForm.prefixo}
                onChange={(e) => setBatchForm({ ...batchForm, prefixo: e.target.value })}
                placeholder="Ex: Mesa"
              />
            </div>

            <div>
              <Label htmlFor="tipo_batch">Tipo</Label>
              <Select
                value={batchForm.tipo}
                onValueChange={(value) => setBatchForm({ ...batchForm, tipo: value })}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="NORMAL">Normal</SelectItem>
                  <SelectItem value="VIP">VIP</SelectItem>
                  <SelectItem value="REDONDA">Redonda</SelectItem>
                  <SelectItem value="RETANGULAR">Retangular</SelectItem>
                  <SelectItem value="BALCAO">Balcão</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div>
              <Label htmlFor="capacidade_batch">Capacidade</Label>
              <Input
                id="capacidade_batch"
                type="number"
                value={batchForm.capacidade}
                onChange={(e) => setBatchForm({ ...batchForm, capacidade: parseInt(e.target.value) })}
              />
            </div>
          </div>

          <div className="flex justify-end space-x-2 pt-4">
            <Button variant="outline" onClick={() => setShowBatchModal(false)}>
              Cancelar
            </Button>
            <Button onClick={handleBatchCreate} disabled={loading}>
              {loading ? 'Criando...' : 'Criar Mesas'}
            </Button>
          </div>
        </DialogContent>
      </Dialog>

      {/* Modal de Templates */}
      <Dialog open={showTemplateModal} onOpenChange={setShowTemplateModal}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Templates de Layout</DialogTitle>
          </DialogHeader>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {templates.map((template) => (
              <Card key={template.id} className="cursor-pointer hover:shadow-md transition-shadow">
                <CardHeader>
                  <CardTitle className="text-lg">{template.nome}</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-gray-600 mb-4">{template.descricao}</p>
                  <Button
                    onClick={() => handleApplyTemplate(template.id)}
                    className="w-full"
                  >
                    Aplicar Template
                  </Button>
                </CardContent>
              </Card>
            ))}
          </div>

          <div className="flex justify-end pt-4">
            <Button variant="outline" onClick={() => setShowTemplateModal(false)}>
              Fechar
            </Button>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default MesasModule;