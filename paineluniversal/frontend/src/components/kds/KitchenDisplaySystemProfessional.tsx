import React, { useState, useEffect } from 'react';
import {
  Clock, Bell, ChefHat, AlertCircle, CheckCircle, XCircle,
  Timer, Users, Flame, ShoppingBag, Eye, MoreHorizontal,
  Zap, Volume2, VolumeX, Filter, Search, RotateCcw
} from 'lucide-react';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '../ui/card';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Badge } from '../ui/badge';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '../ui/select';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '../ui/dialog';
import { toast } from 'sonner';

// MEEP-inspired Professional KDS System
interface PedidoKDS {
  id: string;
  numero: number;
  mesa?: string;
  cliente?: string;
  status: 'novo' | 'preparando' | 'pronto' | 'entregue' | 'cancelado';
  prioridade: 'normal' | 'urgente' | 'express';
  tempoPedido: string;
  tempoEspera: number; // minutos
  items: ItemPedidoKDS[];
  observacoes?: string;
  garcom?: string;
  valorTotal: number;
  metodoPagamento: string;
}

interface ItemPedidoKDS {
  id: string;
  nome: string;
  quantidade: number;
  categoria: string;
  tempoPreparoEstimado: number; // minutos
  observacoes?: string;
  status: 'pendente' | 'preparando' | 'pronto';
  ingredientesEspeciais?: string[];
}

// Mock data baseado na estrutura MEEP
const mockPedidosKDS: PedidoKDS[] = [
  {
    id: '1',
    numero: 1001,
    mesa: 'Mesa 15',
    cliente: 'João Silva',
    status: 'novo',
    prioridade: 'normal',
    tempoPedido: new Date(Date.now() - 5 * 60000).toISOString(),
    tempoEspera: 5,
    valorTotal: 89.50,
    metodoPagamento: 'PIX',
    garcom: 'Maria Santos',
    items: [
      {
        id: '1-1',
        nome: 'Hambúrguer Artesanal',
        quantidade: 2,
        categoria: 'Lanches',
        tempoPreparoEstimado: 15,
        status: 'pendente',
        observacoes: 'Sem cebola, molho à parte',
        ingredientesEspeciais: ['Queijo Brie', 'Rúcula']
      },
      {
        id: '1-2',
        nome: 'Batata Rústica',
        quantidade: 1,
        categoria: 'Acompanhamentos',
        tempoPreparoEstimado: 10,
        status: 'pendente'
      }
    ]
  },
  {
    id: '2',
    numero: 1002,
    mesa: 'Balcão 3',
    status: 'preparando',
    prioridade: 'urgente',
    tempoPedido: new Date(Date.now() - 12 * 60000).toISOString(),
    tempoEspera: 12,
    valorTotal: 45.00,
    metodoPagamento: 'Cartão',
    items: [
      {
        id: '2-1',
        nome: 'Pizza Margherita',
        quantidade: 1,
        categoria: 'Pizzas',
        tempoPreparoEstimado: 20,
        status: 'preparando'
      }
    ]
  },
  {
    id: '3',
    numero: 1003,
    cliente: 'Ana Costa (Delivery)',
    status: 'pronto',
    prioridade: 'express',
    tempoPedido: new Date(Date.now() - 20 * 60000).toISOString(),
    tempoEspera: 20,
    valorTotal: 67.90,
    metodoPagamento: 'Dinheiro',
    items: [
      {
        id: '3-1',
        nome: 'Salada Caesar',
        quantidade: 1,
        categoria: 'Saladas',
        tempoPreparoEstimado: 8,
        status: 'pronto'
      },
      {
        id: '3-2',
        nome: 'Suco Natural',
        quantidade: 2,
        categoria: 'Bebidas',
        tempoPreparoEstimado: 3,
        status: 'pronto'
      }
    ]
  }
];

const KitchenDisplaySystemProfessional: React.FC = () => {
  const [pedidos, setPedidos] = useState<PedidoKDS[]>(mockPedidosKDS);
  const [filtroStatus, setFiltroStatus] = useState<string>('todos');
  const [filtroPrioridade, setFiltroPrioridade] = useState<string>('todas');
  const [busca, setBusca] = useState('');
  const [audioAlerts, setAudioAlerts] = useState(true);
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [selectedPedido, setSelectedPedido] = useState<PedidoKDS | null>(null);
  const [isFullscreen, setIsFullscreen] = useState(false);

  // Simulação de atualização em tempo real
  useEffect(() => {
    if (!autoRefresh) return;
    
    const interval = setInterval(() => {
      setPedidos(prev => prev.map(pedido => ({
        ...pedido,
        tempoEspera: Math.floor((Date.now() - new Date(pedido.tempoPedido).getTime()) / 60000)
      })));
    }, 60000); // Atualizar a cada minuto
    
    return () => clearInterval(interval);
  }, [autoRefresh]);

  // Simulação de alertas sonoros
  useEffect(() => {
    const newOrders = pedidos.filter(p => p.status === 'novo' && p.tempoEspera < 1);
    const urgentOrders = pedidos.filter(p => p.tempoEspera > 15 && p.status !== 'pronto');
    
    if (audioAlerts && (newOrders.length > 0 || urgentOrders.length > 0)) {
      // Aqui seria implementado o som real
      console.log('🔔 Alerta sonoro ativo');
    }
  }, [pedidos, audioAlerts]);

  const filteredPedidos = pedidos.filter(pedido => {
    const matchStatus = filtroStatus === 'todos' || pedido.status === filtroStatus;
    const matchPrioridade = filtroPrioridade === 'todas' || pedido.prioridade === filtroPrioridade;
    const matchBusca = busca === '' || 
      pedido.numero.toString().includes(busca) ||
      pedido.mesa?.toLowerCase().includes(busca.toLowerCase()) ||
      pedido.cliente?.toLowerCase().includes(busca.toLowerCase());
    
    return matchStatus && matchPrioridade && matchBusca;
  });

  const updatePedidoStatus = (pedidoId: string, newStatus: PedidoKDS['status']) => {
    setPedidos(prev => prev.map(pedido => 
      pedido.id === pedidoId 
        ? { ...pedido, status: newStatus }
        : pedido
    ));
    
    const pedido = pedidos.find(p => p.id === pedidoId);
    if (pedido) {
      toast.success(`Pedido #${pedido.numero} marcado como ${newStatus}`);
    }
  };

  const updateItemStatus = (pedidoId: string, itemId: string, newStatus: ItemPedidoKDS['status']) => {
    setPedidos(prev => prev.map(pedido => 
      pedido.id === pedidoId 
        ? {
            ...pedido,
            items: pedido.items.map(item =>
              item.id === itemId ? { ...item, status: newStatus } : item
            )
          }
        : pedido
    ));
  };

  const getStatusColor = (status: PedidoKDS['status']) => {
    switch (status) {
      case 'novo': return 'bg-blue-100 text-blue-800';
      case 'preparando': return 'bg-yellow-100 text-yellow-800';
      case 'pronto': return 'bg-green-100 text-green-800';
      case 'entregue': return 'bg-gray-100 text-gray-800';
      case 'cancelado': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getPriorityColor = (prioridade: PedidoKDS['prioridade']) => {
    switch (prioridade) {
      case 'express': return 'bg-red-500 text-white';
      case 'urgente': return 'bg-orange-500 text-white';
      case 'normal': return 'bg-blue-500 text-white';
      default: return 'bg-gray-500 text-white';
    }
  };

  const getTimeColor = (tempoEspera: number) => {
    if (tempoEspera > 20) return 'text-red-600 font-bold';
    if (tempoEspera > 15) return 'text-orange-600 font-semibold';
    if (tempoEspera > 10) return 'text-yellow-600';
    return 'text-green-600';
  };

  const stats = {
    total: pedidos.length,
    novos: pedidos.filter(p => p.status === 'novo').length,
    preparando: pedidos.filter(p => p.status === 'preparando').length,
    prontos: pedidos.filter(p => p.status === 'pronto').length,
    tempoMedio: pedidos.length > 0 
      ? Math.round(pedidos.reduce((acc, p) => acc + p.tempoEspera, 0) / pedidos.length) 
      : 0,
    atrasados: pedidos.filter(p => p.tempoEspera > 15 && p.status !== 'pronto').length
  };

  return (
    <div className={`flex-1 space-y-4 p-4 pt-6 ${isFullscreen ? 'fixed inset-0 z-50 bg-white' : ''}`}>
      {/* Header KDS Professional */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold tracking-tight flex items-center">
            <ChefHat className="mr-3 h-8 w-8 text-orange-600" />
            KDS Professional
          </h2>
          <p className="text-muted-foreground">
            Sistema de Display de Cozinha - Baseado no MEEP Pro
          </p>
        </div>
        
        <div className="flex items-center space-x-2">
          <Button
            variant={audioAlerts ? "default" : "outline"}
            size="sm"
            onClick={() => setAudioAlerts(!audioAlerts)}
          >
            {audioAlerts ? <Volume2 className="h-4 w-4" /> : <VolumeX className="h-4 w-4" />}
          </Button>
          
          <Button
            variant={autoRefresh ? "default" : "outline"}
            size="sm"
            onClick={() => setAutoRefresh(!autoRefresh)}
          >
            <RotateCcw className="h-4 w-4" />
          </Button>
          
          <Button
            variant="outline"
            size="sm"
            onClick={() => setIsFullscreen(!isFullscreen)}
          >
            <Eye className="h-4 w-4" />
          </Button>
        </div>
      </div>

      {/* Stats Dashboard */}
      <div className="grid gap-4 md:grid-cols-6">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Total Pedidos</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-blue-600">{stats.total}</div>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Novos</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-blue-600 flex items-center">
              {stats.novos}
              {stats.novos > 0 && <Bell className="ml-1 h-4 w-4 animate-pulse" />}
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Preparando</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-yellow-600 flex items-center">
              {stats.preparando}
              {stats.preparando > 0 && <Flame className="ml-1 h-4 w-4" />}
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Prontos</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">{stats.prontos}</div>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Tempo Médio</CardTitle>
          </CardHeader>
          <CardContent>
            <div className={`text-2xl font-bold ${getTimeColor(stats.tempoMedio)}`}>
              {stats.tempoMedio}min
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Atrasados</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-600 flex items-center">
              {stats.atrasados}
              {stats.atrasados > 0 && <AlertCircle className="ml-1 h-4 w-4 animate-bounce" />}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Filtros */}
      <Card>
        <CardContent className="pt-6">
          <div className="grid gap-4 md:grid-cols-4">
            <div className="space-y-2">
              <div className="relative">
                <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="Buscar pedido, mesa, cliente..."
                  value={busca}
                  onChange={(e) => setBusca(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>
            
            <Select value={filtroStatus} onValueChange={setFiltroStatus}>
              <SelectTrigger>
                <SelectValue placeholder="Filtrar por status" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="todos">Todos os Status</SelectItem>
                <SelectItem value="novo">Novos</SelectItem>
                <SelectItem value="preparando">Preparando</SelectItem>
                <SelectItem value="pronto">Prontos</SelectItem>
                <SelectItem value="entregue">Entregues</SelectItem>
              </SelectContent>
            </Select>
            
            <Select value={filtroPrioridade} onValueChange={setFiltroPrioridade}>
              <SelectTrigger>
                <SelectValue placeholder="Filtrar por prioridade" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="todas">Todas as Prioridades</SelectItem>
                <SelectItem value="express">Express</SelectItem>
                <SelectItem value="urgente">Urgente</SelectItem>
                <SelectItem value="normal">Normal</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      {/* Grid de Pedidos */}
      <div className="grid gap-4 md:grid-cols-3 lg:grid-cols-4">
        {filteredPedidos.map((pedido) => (
          <Card 
            key={pedido.id} 
            className={`relative border-l-4 ${
              pedido.prioridade === 'express' ? 'border-l-red-500' :
              pedido.prioridade === 'urgente' ? 'border-l-orange-500' :
              'border-l-blue-500'
            } ${
              pedido.tempoEspera > 15 ? 'animate-pulse shadow-lg' : ''
            }`}
          >
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <CardTitle className="text-lg">#{pedido.numero}</CardTitle>
                  <Badge className={getPriorityColor(pedido.prioridade)}>
                    {pedido.prioridade}
                  </Badge>
                </div>
                
                <div className="flex items-center space-x-1">
                  <Clock className="h-4 w-4 text-muted-foreground" />
                  <span className={`text-sm font-semibold ${getTimeColor(pedido.tempoEspera)}`}>
                    {pedido.tempoEspera}min
                  </span>
                </div>
              </div>
              
              <div className="space-y-1">
                {pedido.mesa && (
                  <p className="text-sm text-muted-foreground">📍 {pedido.mesa}</p>
                )}
                {pedido.cliente && (
                  <p className="text-sm text-muted-foreground">👤 {pedido.cliente}</p>
                )}
                {pedido.garcom && (
                  <p className="text-sm text-muted-foreground">🍽️ {pedido.garcom}</p>
                )}
              </div>
            </CardHeader>
            
            <CardContent className="space-y-3">
              {/* Status Badge */}
              <div className="flex justify-center">
                <Badge className={getStatusColor(pedido.status)} variant="secondary">
                  {pedido.status.toUpperCase()}
                </Badge>
              </div>
              
              {/* Items */}
              <div className="space-y-2">
                {pedido.items.map((item) => (
                  <div key={item.id} className="flex items-center justify-between text-sm">
                    <div className="flex-1">
                      <span className="font-medium">{item.quantidade}x {item.nome}</span>
                      {item.observacoes && (
                        <p className="text-xs text-muted-foreground mt-1">
                          📝 {item.observacoes}
                        </p>
                      )}
                    </div>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => updateItemStatus(pedido.id, item.id, 
                        item.status === 'pendente' ? 'preparando' : 
                        item.status === 'preparando' ? 'pronto' : 'pendente'
                      )}
                      className="ml-2"
                    >
                      {item.status === 'pendente' && <Timer className="h-3 w-3" />}
                      {item.status === 'preparando' && <Flame className="h-3 w-3" />}
                      {item.status === 'pronto' && <CheckCircle className="h-3 w-3" />}
                    </Button>
                  </div>
                ))}
              </div>
              
              {/* Ações */}
              <div className="grid grid-cols-2 gap-2 pt-2">
                {pedido.status === 'novo' && (
                  <Button
                    size="sm"
                    onClick={() => updatePedidoStatus(pedido.id, 'preparando')}
                    className="bg-yellow-600 hover:bg-yellow-700"
                  >
                    <Flame className="h-3 w-3 mr-1" />
                    Preparar
                  </Button>
                )}
                
                {pedido.status === 'preparando' && (
                  <Button
                    size="sm"
                    onClick={() => updatePedidoStatus(pedido.id, 'pronto')}
                    className="bg-green-600 hover:bg-green-700"
                  >
                    <CheckCircle className="h-3 w-3 mr-1" />
                    Finalizar
                  </Button>
                )}
                
                {pedido.status === 'pronto' && (
                  <Button
                    size="sm"
                    onClick={() => updatePedidoStatus(pedido.id, 'entregue')}
                    className="bg-blue-600 hover:bg-blue-700"
                  >
                    <ShoppingBag className="h-3 w-3 mr-1" />
                    Entregar
                  </Button>
                )}
                
                <Dialog>
                  <DialogTrigger asChild>
                    <Button size="sm" variant="outline">
                      <Eye className="h-3 w-3 mr-1" />
                      Detalhes
                    </Button>
                  </DialogTrigger>
                  <DialogContent className="max-w-md">
                    <DialogHeader>
                      <DialogTitle>Pedido #{pedido.numero}</DialogTitle>
                      <DialogDescription>
                        Detalhes completos do pedido
                      </DialogDescription>
                    </DialogHeader>
                    <div className="space-y-4">
                      <div>
                        <h4 className="font-semibold">Informações Gerais</h4>
                        <div className="text-sm space-y-1 mt-2">
                          <p>💰 Total: R$ {pedido.valorTotal.toFixed(2)}</p>
                          <p>💳 Pagamento: {pedido.metodoPagamento}</p>
                          <p>⏰ Tempo: {pedido.tempoEspera} minutos</p>
                          <p>🚨 Prioridade: {pedido.prioridade}</p>
                        </div>
                      </div>
                      
                      {pedido.observacoes && (
                        <div>
                          <h4 className="font-semibold">Observações</h4>
                          <p className="text-sm text-muted-foreground mt-2">
                            {pedido.observacoes}
                          </p>
                        </div>
                      )}
                    </div>
                  </DialogContent>
                </Dialog>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
      
      {filteredPedidos.length === 0 && (
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-12">
            <ChefHat className="h-12 w-12 text-gray-400 mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              Nenhum pedido encontrado
            </h3>
            <p className="text-gray-500 text-center">
              Todos os pedidos foram processados ou não há pedidos com os filtros aplicados.
            </p>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default KitchenDisplaySystemProfessional;