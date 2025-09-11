import React, { useState, useEffect } from 'react';
import {
  Users, Clock, DollarSign, Utensils, Coffee, Wine,
  UserPlus, CheckCircle, AlertTriangle, XCircle, MoreHorizontal,
  Maximize2, Eye, Edit2, Trash2, ShoppingBag, Receipt,
  Timer, MapPin, Settings, Filter, Search, RotateCcw,
  Calendar, User, Hash, Phone, Mail
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
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '../ui/dialog';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '../ui/dropdown-menu';
import { Label } from '../ui/label';
import { Textarea } from '../ui/textarea';
import { toast } from 'sonner';

// MEEP-inspired Professional Mesa Management
interface Mesa {
  id: string;
  numero: number;
  nome?: string;
  capacidade: number;
  status: 'livre' | 'ocupada' | 'reservada' | 'limpeza' | 'manutencao';
  posicao: { x: number; y: number };
  area: 'interno' | 'externo' | 'varanda' | 'vip' | 'privativo';
  tipo: 'redonda' | 'quadrada' | 'retangular' | 'alta' | 'bancada';
  cliente?: ClienteMesa;
  comanda?: ComandaMesa;
  garcom?: string;
  horaAbertura?: string;
  tempoOcupacao?: number; // minutos
  valorTotal?: number;
  observacoes?: string;
}

interface ClienteMesa {
  nome: string;
  cpf?: string;
  telefone?: string;
  email?: string;
  pessoas: number;
  observacoes?: string;
}

interface ComandaMesa {
  id: string;
  numero: number;
  itens: number;
  valor: number;
  status: 'aberta' | 'aguardando' | 'finalizada';
  metodoPagamento?: string;
}

// Mock data MEEP-inspired (60+ mesas)
const generateMockMesas = (): Mesa[] => {
  const mesas: Mesa[] = [];
  const areas: Mesa['area'][] = ['interno', 'externo', 'varanda', 'vip', 'privativo'];
  const tipos: Mesa['tipo'][] = ['redonda', 'quadrada', 'retangular', 'alta', 'bancada'];
  const status: Mesa['status'][] = ['livre', 'ocupada', 'reservada', 'limpeza'];
  const garcons = ['João Silva', 'Maria Santos', 'Pedro Costa', 'Ana Oliveira', 'Carlos Lima'];
  
  for (let i = 1; i <= 60; i++) {
    const isOcupada = Math.random() < 0.3; // 30% ocupadas
    const isReservada = Math.random() < 0.15; // 15% reservadas
    
    const mesa: Mesa = {
      id: `mesa-${i}`,
      numero: i,
      capacidade: Math.floor(Math.random() * 8) + 2, // 2-10 pessoas
      status: isOcupada ? 'ocupada' : isReservada ? 'reservada' : status[Math.floor(Math.random() * status.length)],
      posicao: {
        x: Math.floor(Math.random() * 800) + 50,
        y: Math.floor(Math.random() * 600) + 50
      },
      area: areas[Math.floor(Math.random() * areas.length)],
      tipo: tipos[Math.floor(Math.random() * tipos.length)],
      garcom: isOcupada ? garcons[Math.floor(Math.random() * garcons.length)] : undefined,
    };
    
    if (isOcupada) {
      mesa.cliente = {
        nome: `Cliente Mesa ${i}`,
        cpf: `${Math.floor(Math.random() * 100000000000).toString().padStart(11, '0')}`,
        telefone: `(11) 9${Math.floor(Math.random() * 10000000).toString().padStart(8, '0')}`,
        pessoas: Math.floor(Math.random() * mesa.capacidade) + 1
      };
      
      mesa.comanda = {
        id: `comanda-${i}`,
        numero: 1000 + i,
        itens: Math.floor(Math.random() * 15) + 1,
        valor: Math.random() * 300 + 50,
        status: 'aberta'
      };
      
      mesa.horaAbertura = new Date(Date.now() - Math.random() * 240 * 60000).toISOString();
      mesa.tempoOcupacao = Math.floor((Date.now() - new Date(mesa.horaAbertura).getTime()) / 60000);
      mesa.valorTotal = mesa.comanda.valor;
    }
    
    if (isReservada) {
      mesa.cliente = {
        nome: `Reserva Mesa ${i}`,
        telefone: `(11) 9${Math.floor(Math.random() * 10000000).toString().padStart(8, '0')}`,
        pessoas: Math.floor(Math.random() * mesa.capacidade) + 1
      };
    }
    
    if (Math.random() < 0.1) {
      mesa.nome = `Mesa ${['VIP', 'Premium', 'Romântica', 'Família', 'Executiva'][Math.floor(Math.random() * 5)]}`;
    }
    
    mesas.push(mesa);
  }
  
  return mesas;
};

const GestaoMesasProfessional: React.FC = () => {
  const [mesas, setMesas] = useState<Mesa[]>(generateMockMesas);
  const [filtroStatus, setFiltroStatus] = useState<string>('todas');
  const [filtroArea, setFiltroArea] = useState<string>('todas');
  const [busca, setBusca] = useState('');
  const [selectedMesa, setSelectedMesa] = useState<Mesa | null>(null);
  const [showDetalhes, setShowDetalhes] = useState(false);
  const [showNovaReserva, setShowNovaReserva] = useState(false);
  const [viewMode, setViewMode] = useState<'grid' | 'mapa'>('grid');
  const [autoRefresh, setAutoRefresh] = useState(true);
  
  // Estados para nova reserva
  const [novaReserva, setNovaReserva] = useState({
    mesaId: '',
    clienteNome: '',
    clienteTelefone: '',
    clienteEmail: '',
    pessoas: 2,
    dataReserva: new Date().toISOString().split('T')[0],
    horaReserva: '19:00',
    observacoes: ''
  });

  // Atualização em tempo real
  useEffect(() => {
    if (!autoRefresh) return;
    
    const interval = setInterval(() => {
      setMesas(prev => prev.map(mesa => {
        if (mesa.status === 'ocupada' && mesa.horaAbertura) {
          const tempoOcupacao = Math.floor((Date.now() - new Date(mesa.horaAbertura).getTime()) / 60000);
          return { ...mesa, tempoOcupacao };
        }
        return mesa;
      }));
    }, 60000);
    
    return () => clearInterval(interval);
  }, [autoRefresh]);

  const filteredMesas = mesas.filter(mesa => {
    const matchStatus = filtroStatus === 'todas' || mesa.status === filtroStatus;
    const matchArea = filtroArea === 'todas' || mesa.area === filtroArea;
    const matchBusca = busca === '' || 
      mesa.numero.toString().includes(busca) ||
      mesa.nome?.toLowerCase().includes(busca.toLowerCase()) ||
      mesa.cliente?.nome.toLowerCase().includes(busca.toLowerCase()) ||
      mesa.garcom?.toLowerCase().includes(busca.toLowerCase());
    
    return matchStatus && matchArea && matchBusca;
  });

  const updateMesaStatus = (mesaId: string, newStatus: Mesa['status']) => {
    setMesas(prev => prev.map(mesa => {
      if (mesa.id === mesaId) {
        const updatedMesa = { ...mesa, status: newStatus };
        
        if (newStatus === 'livre') {
          // Limpar dados da mesa
          updatedMesa.cliente = undefined;
          updatedMesa.comanda = undefined;
          updatedMesa.garcom = undefined;
          updatedMesa.horaAbertura = undefined;
          updatedMesa.tempoOcupacao = undefined;
          updatedMesa.valorTotal = undefined;
        }
        
        return updatedMesa;
      }
      return mesa;
    }));
    
    toast.success(`Mesa ${mesas.find(m => m.id === mesaId)?.numero} alterada para ${newStatus}`);
  };

  const criarReserva = () => {
    if (!novaReserva.mesaId || !novaReserva.clienteNome || !novaReserva.clienteTelefone) {
      toast.error('Preencha todos os campos obrigatórios');
      return;
    }
    
    setMesas(prev => prev.map(mesa => {
      if (mesa.id === novaReserva.mesaId) {
        return {
          ...mesa,
          status: 'reservada' as const,
          cliente: {
            nome: novaReserva.clienteNome,
            telefone: novaReserva.clienteTelefone,
            email: novaReserva.clienteEmail,
            pessoas: novaReserva.pessoas,
            observacoes: novaReserva.observacoes
          }
        };
      }
      return mesa;
    }));
    
    setShowNovaReserva(false);
    setNovaReserva({
      mesaId: '',
      clienteNome: '',
      clienteTelefone: '',
      clienteEmail: '',
      pessoas: 2,
      dataReserva: new Date().toISOString().split('T')[0],
      horaReserva: '19:00',
      observacoes: ''
    });
    
    toast.success('Reserva criada com sucesso!');
  };

  const getStatusColor = (status: Mesa['status']) => {
    switch (status) {
      case 'livre': return 'bg-green-100 text-green-800';
      case 'ocupada': return 'bg-red-100 text-red-800';
      case 'reservada': return 'bg-yellow-100 text-yellow-800';
      case 'limpeza': return 'bg-blue-100 text-blue-800';
      case 'manutencao': return 'bg-gray-100 text-gray-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusIcon = (status: Mesa['status']) => {
    switch (status) {
      case 'livre': return <CheckCircle className="h-3 w-3" />;
      case 'ocupada': return <Users className="h-3 w-3" />;
      case 'reservada': return <Calendar className="h-3 w-3" />;
      case 'limpeza': return <Settings className="h-3 w-3" />;
      case 'manutencao': return <AlertTriangle className="h-3 w-3" />;
      default: return null;
    }
  };

  const getTipoIcon = (tipo: Mesa['tipo']) => {
    switch (tipo) {
      case 'redonda': return '⭕';
      case 'quadrada': return '⬜';
      case 'retangular': return '▬';
      case 'alta': return '🏛️';
      case 'bancada': return '━';
      default: return '⬜';
    }
  };

  const stats = {
    total: mesas.length,
    livres: mesas.filter(m => m.status === 'livre').length,
    ocupadas: mesas.filter(m => m.status === 'ocupada').length,
    reservadas: mesas.filter(m => m.status === 'reservada').length,
    faturamento: mesas.reduce((acc, m) => acc + (m.valorTotal || 0), 0),
    ocupacao: Math.round((mesas.filter(m => m.status === 'ocupada').length / mesas.length) * 100),
    tempoMedio: mesas.filter(m => m.tempoOcupacao).length > 0 
      ? Math.round(mesas.reduce((acc, m) => acc + (m.tempoOcupacao || 0), 0) / mesas.filter(m => m.tempoOcupacao).length) 
      : 0
  };

  return (
    <div className="flex-1 space-y-4 p-4 pt-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold tracking-tight flex items-center">
            <Utensils className="mr-3 h-8 w-8 text-orange-600" />
            Gestão de Mesas Professional
          </h2>
          <p className="text-muted-foreground">
            Sistema completo de gerenciamento de mesas - Baseado no MEEP Pro
          </p>
        </div>
        
        <div className="flex items-center space-x-2">
          <Select value={viewMode} onValueChange={(value: 'grid' | 'mapa') => setViewMode(value)}>
            <SelectTrigger className="w-32">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="grid">Grade</SelectItem>
              <SelectItem value="mapa">Mapa</SelectItem>
            </SelectContent>
          </Select>
          
          <Button onClick={() => setShowNovaReserva(true)}>
            <UserPlus className="mr-2 h-4 w-4" />
            Nova Reserva
          </Button>
          
          <Button
            variant={autoRefresh ? "default" : "outline"}
            size="sm"
            onClick={() => setAutoRefresh(!autoRefresh)}
          >
            <RotateCcw className="h-4 w-4" />
          </Button>
        </div>
      </div>

      {/* Stats Dashboard */}
      <div className="grid gap-4 md:grid-cols-7">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Total Mesas</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-blue-600">{stats.total}</div>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Livres</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">{stats.livres}</div>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Ocupadas</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-600">{stats.ocupadas}</div>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Reservadas</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-yellow-600">{stats.reservadas}</div>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Ocupação</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-purple-600">{stats.ocupacao}%</div>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Tempo Médio</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-orange-600">{stats.tempoMedio}min</div>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Faturamento</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">
              R$ {stats.faturamento.toFixed(0)}
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
                  placeholder="Buscar mesa, cliente, garçom..."
                  value={busca}
                  onChange={(e) => setBusca(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>
            
            <Select value={filtroStatus} onValueChange={setFiltroStatus}>
              <SelectTrigger>
                <SelectValue placeholder="Status" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="todas">Todos os Status</SelectItem>
                <SelectItem value="livre">Livres</SelectItem>
                <SelectItem value="ocupada">Ocupadas</SelectItem>
                <SelectItem value="reservada">Reservadas</SelectItem>
                <SelectItem value="limpeza">Limpeza</SelectItem>
                <SelectItem value="manutencao">Manutenção</SelectItem>
              </SelectContent>
            </Select>
            
            <Select value={filtroArea} onValueChange={setFiltroArea}>
              <SelectTrigger>
                <SelectValue placeholder="Área" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="todas">Todas as Áreas</SelectItem>
                <SelectItem value="interno">Interno</SelectItem>
                <SelectItem value="externo">Externo</SelectItem>
                <SelectItem value="varanda">Varanda</SelectItem>
                <SelectItem value="vip">VIP</SelectItem>
                <SelectItem value="privativo">Privativo</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      {/* Grid/Mapa de Mesas */}
      {viewMode === 'grid' ? (
        <div className="grid gap-4 md:grid-cols-4 lg:grid-cols-6">
          {filteredMesas.map((mesa) => (
            <Card 
              key={mesa.id} 
              className={`relative cursor-pointer transition-all hover:shadow-lg ${
                mesa.status === 'ocupada' ? 'border-red-200' :
                mesa.status === 'reservada' ? 'border-yellow-200' :
                mesa.status === 'livre' ? 'border-green-200' :
                'border-gray-200'
              }`}
              onClick={() => {
                setSelectedMesa(mesa);
                setShowDetalhes(true);
              }}
            >
              <CardHeader className="pb-2">
                <div className="flex items-center justify-between">
                  <CardTitle className="text-lg flex items-center">
                    <span className="mr-2 text-xl">{getTipoIcon(mesa.tipo)}</span>
                    {mesa.nome || `Mesa ${mesa.numero}`}
                  </CardTitle>
                  
                  <DropdownMenu>
                    <DropdownMenuTrigger asChild onClick={(e) => e.stopPropagation()}>
                      <Button variant="ghost" size="sm">
                        <MoreHorizontal className="h-4 w-4" />
                      </Button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent>
                      <DropdownMenuLabel>Ações</DropdownMenuLabel>
                      <DropdownMenuSeparator />
                      <DropdownMenuItem onClick={(e) => {
                        e.stopPropagation();
                        updateMesaStatus(mesa.id, 'ocupada');
                      }}>
                        <Users className="mr-2 h-4 w-4" />
                        Ocupar
                      </DropdownMenuItem>
                      <DropdownMenuItem onClick={(e) => {
                        e.stopPropagation();
                        updateMesaStatus(mesa.id, 'livre');
                      }}>
                        <CheckCircle className="mr-2 h-4 w-4" />
                        Liberar
                      </DropdownMenuItem>
                      <DropdownMenuItem onClick={(e) => {
                        e.stopPropagation();
                        updateMesaStatus(mesa.id, 'limpeza');
                      }}>
                        <Settings className="mr-2 h-4 w-4" />
                        Limpeza
                      </DropdownMenuItem>
                    </DropdownMenuContent>
                  </DropdownMenu>
                </div>
                
                <div className="flex justify-center">
                  <Badge className={getStatusColor(mesa.status)} variant="secondary">
                    {getStatusIcon(mesa.status)}
                    <span className="ml-1">{mesa.status.toUpperCase()}</span>
                  </Badge>
                </div>
              </CardHeader>
              
              <CardContent className="space-y-2">
                <div className="text-center space-y-1">
                  <p className="text-sm text-muted-foreground">
                    👥 {mesa.capacidade} pessoas | 📍 {mesa.area}
                  </p>
                  
                  {mesa.cliente && (
                    <div className="text-sm space-y-1">
                      <p className="font-medium">{mesa.cliente.nome}</p>
                      <p className="text-muted-foreground">
                        {mesa.cliente.pessoas} pessoas
                      </p>
                    </div>
                  )}
                  
                  {mesa.comanda && (
                    <div className="text-sm space-y-1 pt-2 border-t">
                      <p>Comanda #{mesa.comanda.numero}</p>
                      <p className="font-bold text-green-600">
                        R$ {mesa.comanda.valor.toFixed(2)}
                      </p>
                    </div>
                  )}
                  
                  {mesa.tempoOcupacao && (
                    <div className="flex items-center justify-center text-sm text-muted-foreground pt-1">
                      <Clock className="h-3 w-3 mr-1" />
                      {mesa.tempoOcupacao}min
                    </div>
                  )}
                  
                  {mesa.garcom && (
                    <p className="text-xs text-muted-foreground">
                      🍽️ {mesa.garcom}
                    </p>
                  )}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      ) : (
        <Card className="h-[600px]">
          <CardContent className="p-6">
            <div className="relative w-full h-full bg-gray-50 rounded-lg overflow-hidden">
              <div className="absolute inset-0 p-4">
                <h3 className="text-lg font-semibold mb-4">Layout do Salão</h3>
                {filteredMesas.map((mesa) => (
                  <div
                    key={mesa.id}
                    className={`absolute w-16 h-16 rounded-lg border-2 flex items-center justify-center text-xs font-bold cursor-pointer transition-all hover:scale-110 ${
                      mesa.status === 'livre' ? 'bg-green-100 border-green-500 text-green-800' :
                      mesa.status === 'ocupada' ? 'bg-red-100 border-red-500 text-red-800' :
                      mesa.status === 'reservada' ? 'bg-yellow-100 border-yellow-500 text-yellow-800' :
                      'bg-gray-100 border-gray-500 text-gray-800'
                    }`}
                    style={{
                      left: `${(mesa.posicao.x / 800) * 100}%`,
                      top: `${(mesa.posicao.y / 600) * 100}%`
                    }}
                    onClick={() => {
                      setSelectedMesa(mesa);
                      setShowDetalhes(true);
                    }}
                  >
                    {mesa.numero}
                  </div>
                ))}
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Dialog Nova Reserva */}
      <Dialog open={showNovaReserva} onOpenChange={setShowNovaReserva}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle>Nova Reserva</DialogTitle>
            <DialogDescription>
              Criar uma nova reserva de mesa
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <Label htmlFor="mesa">Mesa</Label>
              <Select value={novaReserva.mesaId} onValueChange={(value) => 
                setNovaReserva({...novaReserva, mesaId: value})
              }>
                <SelectTrigger>
                  <SelectValue placeholder="Selecione uma mesa" />
                </SelectTrigger>
                <SelectContent>
                  {mesas.filter(m => m.status === 'livre').map(mesa => (
                    <SelectItem key={mesa.id} value={mesa.id}>
                      Mesa {mesa.numero} ({mesa.capacidade} pessoas - {mesa.area})
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            
            <div>
              <Label htmlFor="clienteNome">Nome do Cliente</Label>
              <Input
                id="clienteNome"
                value={novaReserva.clienteNome}
                onChange={(e) => setNovaReserva({...novaReserva, clienteNome: e.target.value})}
                placeholder="Nome completo"
              />
            </div>
            
            <div>
              <Label htmlFor="clienteTelefone">Telefone</Label>
              <Input
                id="clienteTelefone"
                value={novaReserva.clienteTelefone}
                onChange={(e) => setNovaReserva({...novaReserva, clienteTelefone: e.target.value})}
                placeholder="(11) 99999-9999"
              />
            </div>
            
            <div>
              <Label htmlFor="pessoas">Número de Pessoas</Label>
              <Input
                id="pessoas"
                type="number"
                min="1"
                value={novaReserva.pessoas}
                onChange={(e) => setNovaReserva({...novaReserva, pessoas: parseInt(e.target.value)})}
              />
            </div>
            
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="dataReserva">Data</Label>
                <Input
                  id="dataReserva"
                  type="date"
                  value={novaReserva.dataReserva}
                  onChange={(e) => setNovaReserva({...novaReserva, dataReserva: e.target.value})}
                />
              </div>
              
              <div>
                <Label htmlFor="horaReserva">Hora</Label>
                <Input
                  id="horaReserva"
                  type="time"
                  value={novaReserva.horaReserva}
                  onChange={(e) => setNovaReserva({...novaReserva, horaReserva: e.target.value})}
                />
              </div>
            </div>
            
            <div>
              <Label htmlFor="observacoes">Observações</Label>
              <Textarea
                id="observacoes"
                value={novaReserva.observacoes}
                onChange={(e) => setNovaReserva({...novaReserva, observacoes: e.target.value})}
                placeholder="Observações especiais..."
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowNovaReserva(false)}>
              Cancelar
            </Button>
            <Button onClick={criarReserva}>
              Criar Reserva
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Dialog Detalhes da Mesa */}
      <Dialog open={showDetalhes} onOpenChange={setShowDetalhes}>
        <DialogContent className="max-w-lg">
          {selectedMesa && (
            <>
              <DialogHeader>
                <DialogTitle>
                  {selectedMesa.nome || `Mesa ${selectedMesa.numero}`}
                </DialogTitle>
                <DialogDescription>
                  Detalhes completos da mesa
                </DialogDescription>
              </DialogHeader>
              <div className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <h4 className="font-semibold">Informações Básicas</h4>
                    <div className="text-sm space-y-1 mt-2">
                      <p>📊 Capacidade: {selectedMesa.capacidade} pessoas</p>
                      <p>📍 Área: {selectedMesa.area}</p>
                      <p>🔲 Tipo: {selectedMesa.tipo}</p>
                      <p>📈 Status: {selectedMesa.status}</p>
                    </div>
                  </div>
                  
                  {selectedMesa.cliente && (
                    <div>
                      <h4 className="font-semibold">Cliente</h4>
                      <div className="text-sm space-y-1 mt-2">
                        <p>👤 {selectedMesa.cliente.nome}</p>
                        <p>👥 {selectedMesa.cliente.pessoas} pessoas</p>
                        {selectedMesa.cliente.telefone && (
                          <p>📞 {selectedMesa.cliente.telefone}</p>
                        )}
                      </div>
                    </div>
                  )}
                </div>
                
                {selectedMesa.comanda && (
                  <div>
                    <h4 className="font-semibold">Comanda</h4>
                    <div className="text-sm space-y-1 mt-2">
                      <p>🧾 Número: #{selectedMesa.comanda.numero}</p>
                      <p>📦 Itens: {selectedMesa.comanda.itens}</p>
                      <p>💰 Valor: R$ {selectedMesa.comanda.valor.toFixed(2)}</p>
                      <p>📊 Status: {selectedMesa.comanda.status}</p>
                    </div>
                  </div>
                )}
                
                {selectedMesa.status === 'ocupada' && (
                  <div>
                    <h4 className="font-semibold">Ocupação</h4>
                    <div className="text-sm space-y-1 mt-2">
                      {selectedMesa.horaAbertura && (
                        <p>⏰ Aberta às: {new Date(selectedMesa.horaAbertura).toLocaleTimeString('pt-BR')}</p>
                      )}
                      {selectedMesa.tempoOcupacao && (
                        <p>⏱️ Tempo: {selectedMesa.tempoOcupacao} minutos</p>
                      )}
                      {selectedMesa.garcom && (
                        <p>🍽️ Garçom: {selectedMesa.garcom}</p>
                      )}
                    </div>
                  </div>
                )}
              </div>
              <DialogFooter>
                <div className="flex space-x-2">
                  {selectedMesa.status === 'livre' && (
                    <Button onClick={() => updateMesaStatus(selectedMesa.id, 'ocupada')}>
                      <Users className="mr-2 h-4 w-4" />
                      Ocupar
                    </Button>
                  )}
                  
                  {selectedMesa.status === 'ocupada' && (
                    <Button onClick={() => updateMesaStatus(selectedMesa.id, 'livre')}>
                      <CheckCircle className="mr-2 h-4 w-4" />
                      Finalizar
                    </Button>
                  )}
                  
                  <Button variant="outline" onClick={() => setShowDetalhes(false)}>
                    Fechar
                  </Button>
                </div>
              </DialogFooter>
            </>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default GestaoMesasProfessional;