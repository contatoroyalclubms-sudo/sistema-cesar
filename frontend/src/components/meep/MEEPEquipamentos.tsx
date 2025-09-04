import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { 
  Smartphone, 
  Tablet, 
  Printer, 
  Camera, 
  Wifi, 
  WifiOff,
  AlertTriangle,
  CheckCircle,
  XCircle,
  Plus,
  Settings,
  Activity,
  MapPin,
  Clock,
  RefreshCw
} from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';
import { Input } from '../ui/input';
import { Label } from '../ui/label';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '../ui/dialog';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/select';
import { useToast } from '../../hooks/use-toast';

interface Equipamento {
  id: number;
  nome: string;
  tipo: 'tablet' | 'qr_reader' | 'printer' | 'pos' | 'camera' | 'sensor';
  ipAddress: string;
  macAddress?: string;
  localizacao?: string;
  status: 'online' | 'offline' | 'warning' | 'maintenance';
  ultimaAtividade: string;
  eventoId: number;
  configuracoes?: {
    firmware?: string;
    bateria?: number;
    temperatura?: number;
    utilizacao?: number;
  };
}

const MEEPEquipamentos: React.FC = () => {
  const [equipamentos, setEquipamentos] = useState<Equipamento[]>([]);
  const [loading, setLoading] = useState(true);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [novoEquipamento, setNovoEquipamento] = useState({
    nome: '',
    tipo: '',
    ipAddress: '',
    macAddress: '',
    localizacao: '',
    eventoId: 1
  });
  const { toast } = useToast();

  // Mock data para demonstração
  const mockEquipamentos: Equipamento[] = [
    {
      id: 1,
      nome: 'Tablet Check-in Principal',
      tipo: 'tablet',
      ipAddress: '192.168.1.101',
      macAddress: '00:1B:44:11:3A:B7',
      localizacao: 'Entrada Principal',
      status: 'online',
      ultimaAtividade: '2 min atrás',
      eventoId: 1,
      configuracoes: {
        firmware: 'v2.1.3',
        bateria: 87,
        temperatura: 35,
        utilizacao: 23
      }
    },
    {
      id: 2,
      nome: 'QR Scanner Secundário',
      tipo: 'qr_reader',
      ipAddress: '192.168.1.102',
      macAddress: '00:1B:44:11:3A:B8',
      localizacao: 'Entrada VIP',
      status: 'online',
      ultimaAtividade: '1 min atrás',
      eventoId: 1,
      configuracoes: {
        firmware: 'v1.8.2',
        bateria: 92,
        temperatura: 42,
        utilizacao: 15
      }
    },
    {
      id: 3,
      nome: 'Tablet Check-in Lateral',
      tipo: 'tablet',
      ipAddress: '192.168.1.103',
      macAddress: '00:1B:44:11:3A:B9',
      localizacao: 'Entrada Lateral',
      status: 'offline',
      ultimaAtividade: '15 min atrás',
      eventoId: 1,
      configuracoes: {
        firmware: 'v2.1.1',
        bateria: 12,
        temperatura: 28,
        utilizacao: 0
      }
    },
    {
      id: 4,
      nome: 'Impressora de Tickets',
      tipo: 'printer',
      ipAddress: '192.168.1.104',
      macAddress: '00:1B:44:11:3A:C0',
      localizacao: 'Balcão de Atendimento',
      status: 'warning',
      ultimaAtividade: '5 min atrás',
      eventoId: 1,
      configuracoes: {
        firmware: 'v3.2.1',
        utilizacao: 78
      }
    },
    {
      id: 5,
      nome: 'Camera de Segurança 01',
      tipo: 'camera',
      ipAddress: '192.168.1.105',
      localizacao: 'Hall Principal',
      status: 'online',
      ultimaAtividade: '30 seg atrás',
      eventoId: 1,
      configuracoes: {
        firmware: 'v4.1.0',
        utilizacao: 45
      }
    }
  ];

  useEffect(() => {
    const fetchEquipamentos = async () => {
      setLoading(true);
      try {
        // Simular carregamento
        await new Promise(resolve => setTimeout(resolve, 1000));
        setEquipamentos(mockEquipamentos);
      } catch (error) {
        toast({
          title: "Erro ao carregar equipamentos",
          description: "Não foi possível carregar a lista de equipamentos",
          variant: "destructive",
        });
      } finally {
        setLoading(false);
      }
    };

    fetchEquipamentos();
  }, [toast]);

  const getIconByType = (tipo: string) => {
    const icons = {
      tablet: Tablet,
      qr_reader: Camera,
      printer: Printer,
      pos: Smartphone,
      camera: Camera,
      sensor: Activity
    };
    const Icon = icons[tipo as keyof typeof icons] || Activity;
    return <Icon className="h-5 w-5" />;
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'online': return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'offline': return <XCircle className="h-4 w-4 text-red-500" />;
      case 'warning': return <AlertTriangle className="h-4 w-4 text-yellow-500" />;
      case 'maintenance': return <Settings className="h-4 w-4 text-blue-500" />;
      default: return <Activity className="h-4 w-4 text-gray-500" />;
    }
  };

  const getStatusBadge = (status: string) => {
    const variants = {
      online: 'default',
      offline: 'destructive',
      warning: 'secondary',
      maintenance: 'outline'
    } as const;
    
    return <Badge variant={variants[status as keyof typeof variants] || 'outline'}>{status}</Badge>;
  };

  const getConnectivityIcon = (status: string) => {
    return status === 'online' ? 
      <Wifi className="h-4 w-4 text-green-500" /> : 
      <WifiOff className="h-4 w-4 text-red-500" />;
  };

  const handleAddEquipamento = async () => {
    if (!novoEquipamento.nome || !novoEquipamento.tipo || !novoEquipamento.ipAddress) {
      toast({
        title: "Campos obrigatórios",
        description: "Preencha todos os campos obrigatórios",
        variant: "destructive",
      });
      return;
    }

    try {
      // Simular adição
      const newEquip: Equipamento = {
        id: Date.now(),
        ...novoEquipamento,
        tipo: novoEquipamento.tipo as any,
        status: 'offline',
        ultimaAtividade: 'Nunca',
        configuracoes: {
          firmware: 'v1.0.0',
          utilizacao: 0
        }
      };

      setEquipamentos(prev => [...prev, newEquip]);
      setDialogOpen(false);
      setNovoEquipamento({
        nome: '',
        tipo: '',
        ipAddress: '',
        macAddress: '',
        localizacao: '',
        eventoId: 1
      });

      toast({
        title: "Equipamento adicionado",
        description: "Equipamento registrado com sucesso",
      });
    } catch (error) {
      toast({
        title: "Erro ao adicionar",
        description: "Não foi possível adicionar o equipamento",
        variant: "destructive",
      });
    }
  };

  const removerEquipamento = (id: number) => {
    setEquipamentos(prev => prev.filter(eq => eq.id !== id));
    toast({
      title: "Equipamento removido",
      description: "Equipamento removido com sucesso",
    });
  };

  const estatisticas = {
    total: equipamentos.length,
    online: equipamentos.filter(eq => eq.status === 'online').length,
    offline: equipamentos.filter(eq => eq.status === 'offline').length,
    warning: equipamentos.filter(eq => eq.status === 'warning').length
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <RefreshCw className="h-8 w-8 animate-spin text-primary" />
        <span className="ml-2 text-lg">Carregando equipamentos...</span>
      </div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-6"
    >
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-foreground">MEEP Equipamentos</h1>
          <p className="text-muted-foreground">
            Gestão e monitoramento de equipamentos do evento
          </p>
        </div>
        
        <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
          <DialogTrigger asChild>
            <Button>
              <Plus className="h-4 w-4 mr-2" />
              Adicionar Equipamento
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Novo Equipamento</DialogTitle>
              <DialogDescription>
                Registre um novo equipamento para o evento
              </DialogDescription>
            </DialogHeader>
            <div className="space-y-4">
              <div>
                <Label htmlFor="nome">Nome do Equipamento</Label>
                <Input
                  id="nome"
                  value={novoEquipamento.nome}
                  onChange={(e) => setNovoEquipamento(prev => ({ ...prev, nome: e.target.value }))}
                  placeholder="Ex: Tablet Check-in 01"
                />
              </div>
              
              <div>
                <Label htmlFor="tipo">Tipo</Label>
                <Select onValueChange={(value) => setNovoEquipamento(prev => ({ ...prev, tipo: value }))}>
                  <SelectTrigger>
                    <SelectValue placeholder="Selecione o tipo" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="tablet">Tablet</SelectItem>
                    <SelectItem value="qr_reader">QR Reader</SelectItem>
                    <SelectItem value="printer">Impressora</SelectItem>
                    <SelectItem value="pos">POS Terminal</SelectItem>
                    <SelectItem value="camera">Câmera</SelectItem>
                    <SelectItem value="sensor">Sensor</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              
              <div>
                <Label htmlFor="ip">Endereço IP</Label>
                <Input
                  id="ip"
                  value={novoEquipamento.ipAddress}
                  onChange={(e) => setNovoEquipamento(prev => ({ ...prev, ipAddress: e.target.value }))}
                  placeholder="192.168.1.100"
                />
              </div>
              
              <div>
                <Label htmlFor="mac">MAC Address (Opcional)</Label>
                <Input
                  id="mac"
                  value={novoEquipamento.macAddress}
                  onChange={(e) => setNovoEquipamento(prev => ({ ...prev, macAddress: e.target.value }))}
                  placeholder="00:1B:44:11:3A:B7"
                />
              </div>
              
              <div>
                <Label htmlFor="localizacao">Localização (Opcional)</Label>
                <Input
                  id="localizacao"
                  value={novoEquipamento.localizacao}
                  onChange={(e) => setNovoEquipamento(prev => ({ ...prev, localizacao: e.target.value }))}
                  placeholder="Ex: Entrada Principal"
                />
              </div>
              
              <Button onClick={handleAddEquipamento} className="w-full">
                Registrar Equipamento
              </Button>
            </div>
          </DialogContent>
        </Dialog>
      </div>

      {/* Estatísticas */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Equipamentos</CardTitle>
            <Activity className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{estatisticas.total}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Online</CardTitle>
            <CheckCircle className="h-4 w-4 text-green-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">{estatisticas.online}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Offline</CardTitle>
            <XCircle className="h-4 w-4 text-red-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-600">{estatisticas.offline}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Alertas</CardTitle>
            <AlertTriangle className="h-4 w-4 text-yellow-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-yellow-600">{estatisticas.warning}</div>
          </CardContent>
        </Card>
      </div>

      {/* Lista de Equipamentos */}
      <Tabs defaultValue="grid" className="w-full">
        <TabsList>
          <TabsTrigger value="grid">Visualização em Grid</TabsTrigger>
          <TabsTrigger value="list">Visualização em Lista</TabsTrigger>
        </TabsList>

        <TabsContent value="grid" className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {equipamentos.map((equipamento) => (
              <motion.div
                key={equipamento.id}
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.2 }}
              >
                <Card className={`relative ${
                  equipamento.status === 'offline' ? 'bg-red-50 border-red-200' :
                  equipamento.status === 'warning' ? 'bg-yellow-50 border-yellow-200' :
                  'bg-green-50 border-green-200'
                }`}>
                  <CardHeader className="pb-2">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-2">
                        {getIconByType(equipamento.tipo)}
                        <CardTitle className="text-lg">{equipamento.nome}</CardTitle>
                      </div>
                      {getStatusBadge(equipamento.status)}
                    </div>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-muted-foreground">Conectividade:</span>
                      <div className="flex items-center space-x-1">
                        {getConnectivityIcon(equipamento.status)}
                        <span>{equipamento.ipAddress}</span>
                      </div>
                    </div>
                    
                    {equipamento.localizacao && (
                      <div className="flex items-center justify-between text-sm">
                        <span className="text-muted-foreground">Localização:</span>
                        <div className="flex items-center space-x-1">
                          <MapPin className="h-3 w-3" />
                          <span>{equipamento.localizacao}</span>
                        </div>
                      </div>
                    )}
                    
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-muted-foreground">Última atividade:</span>
                      <div className="flex items-center space-x-1">
                        <Clock className="h-3 w-3" />
                        <span>{equipamento.ultimaAtividade}</span>
                      </div>
                    </div>
                    
                    {equipamento.configuracoes && (
                      <div className="pt-2 border-t space-y-2">
                        {equipamento.configuracoes.bateria && (
                          <div className="flex justify-between text-sm">
                            <span>Bateria:</span>
                            <span className={`font-medium ${
                              equipamento.configuracoes.bateria > 50 ? 'text-green-600' :
                              equipamento.configuracoes.bateria > 20 ? 'text-yellow-600' : 'text-red-600'
                            }`}>
                              {equipamento.configuracoes.bateria}%
                            </span>
                          </div>
                        )}
                        
                        {equipamento.configuracoes.utilizacao !== undefined && (
                          <div className="flex justify-between text-sm">
                            <span>Utilização:</span>
                            <span className="font-medium">{equipamento.configuracoes.utilizacao}%</span>
                          </div>
                        )}
                        
                        {equipamento.configuracoes.firmware && (
                          <div className="flex justify-between text-sm">
                            <span>Firmware:</span>
                            <span className="font-mono text-xs">{equipamento.configuracoes.firmware}</span>
                          </div>
                        )}
                      </div>
                    )}
                    
                    <div className="flex space-x-2 pt-2">
                      <Button variant="outline" size="sm" className="flex-1">
                        <Settings className="h-3 w-3 mr-1" />
                        Configurar
                      </Button>
                      <Button 
                        variant="destructive" 
                        size="sm"
                        onClick={() => removerEquipamento(equipamento.id)}
                      >
                        Remover
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              </motion.div>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="list" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Lista de Equipamentos</CardTitle>
              <CardDescription>
                Visualização detalhada de todos os equipamentos
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {equipamentos.map((equipamento, index) => (
                  <motion.div
                    key={equipamento.id}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.1 }}
                    className="flex items-center justify-between p-4 border rounded-lg hover:bg-muted/50 transition-colors"
                  >
                    <div className="flex items-center space-x-4">
                      <div className="flex items-center space-x-2">
                        {getIconByType(equipamento.tipo)}
                        {getStatusIcon(equipamento.status)}
                      </div>
                      <div>
                        <div className="font-medium">{equipamento.nome}</div>
                        <div className="text-sm text-muted-foreground">
                          {equipamento.ipAddress} • {equipamento.localizacao}
                        </div>
                      </div>
                    </div>
                    
                    <div className="flex items-center space-x-4">
                      <div className="text-right">
                        <div className="text-sm">{getStatusBadge(equipamento.status)}</div>
                        <div className="text-xs text-muted-foreground">
                          {equipamento.ultimaAtividade}
                        </div>
                      </div>
                      <Button variant="outline" size="sm">
                        <Settings className="h-4 w-4" />
                      </Button>
                    </div>
                  </motion.div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </motion.div>
  );
};

export default MEEPEquipamentos;
