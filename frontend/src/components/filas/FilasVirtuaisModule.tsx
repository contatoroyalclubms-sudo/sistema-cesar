import React, { useState, useEffect, useRef } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Alert, AlertDescription } from '@/components/ui/alert';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  Table,
  TableBody,
  TableCaption,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { useToast } from '@/hooks/use-toast';
import { useEventoContext } from '@/contexts/EventoContext';
import api from '@/lib/api';
import {
  Users,
  Plus,
  QrCode,
  Clock,
  AlertTriangle,
  CheckCircle,
  XCircle,
  PhoneCall,
  MessageSquare,
  TrendingUp,
  RefreshCw,
  Settings,
  ChevronRight,
  Timer,
  UserCheck,
  UserX,
  Bell,
} from 'lucide-react';
import { format, formatDistanceToNow } from 'date-fns';
import { ptBR } from 'date-fns/locale';

interface FilaVirtual {
  id: number;
  evento_id: number;
  nome: string;
  descricao?: string;
  tipo: 'normal' | 'prioridade' | 'agendamento';
  status: 'ativa' | 'pausada' | 'finalizada';
  capacidade_maxima?: number;
  tempo_medio_atendimento: number;
  senha_atual: number;
  total_atendidos: number;
  total_desistentes: number;
  criado_em: string;
  atualizado_em?: string;
}

interface ParticipanteFila {
  id: number;
  fila_id: number;
  cpf: string;
  nome: string;
  telefone?: string;
  senha_gerada: string;
  prioridade: number;
  tempo_entrada: string;
  tempo_chamada?: string;
  tempo_atendimento?: string;
  status: 'aguardando' | 'chamado' | 'atendido' | 'desistente';
  notificado_via?: string;
  observacoes?: string;
}

interface FilaStats {
  total_na_fila: number;
  tempo_espera_medio: number;
  tempo_espera_maximo: number;
  taxa_desistencia: number;
  atendimentos_hora: number;
  satisfacao_media?: number;
}

export default function FilasVirtuaisModule() {
  const [filas, setFilas] = useState<FilaVirtual[]>([]);
  const [selectedFila, setSelectedFila] = useState<FilaVirtual | null>(null);
  const [participantes, setParticipantes] = useState<ParticipanteFila[]>([]);
  const [stats, setStats] = useState<FilaStats | null>(null);
  const [loading, setLoading] = useState(false);
  const [creatingFila, setCreatingFila] = useState(false);
  const [enteringFila, setEnteringFila] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);
  const { eventoSelecionado } = useEventoContext();
  const { toast } = useToast();

  const [novaFila, setNovaFila] = useState({
    nome: '',
    descricao: '',
    tipo: 'normal',
    capacidade_maxima: '',
    tempo_medio_atendimento: '5',
  });

  const [novoParticipante, setNovoParticipante] = useState({
    cpf: '',
    nome: '',
    telefone: '',
    prioridade: '0',
  });

  useEffect(() => {
    if (eventoSelecionado) {
      loadFilas();
    }
  }, [eventoSelecionado]);

  useEffect(() => {
    if (selectedFila && selectedFila.status === 'ativa') {
      connectWebSocket();
      return () => {
        if (wsRef.current) {
          wsRef.current.close();
        }
      };
    }
  }, [selectedFila]);

  const connectWebSocket = () => {
    if (!selectedFila) return;

    const wsUrl = `${process.env.VITE_WS_URL || 'ws://localhost:8000'}/api/filas/ws/${selectedFila.id}`;
    
    wsRef.current = new WebSocket(wsUrl);

    wsRef.current.onopen = () => {
      console.log('WebSocket conectado para fila:', selectedFila.nome);
    };

    wsRef.current.onmessage = (event) => {
      const data = JSON.parse(event.data);
      
      switch (data.tipo) {
        case 'novo_participante':
          setParticipantes(prev => [...prev, data.participante]);
          break;
        case 'participante_chamado':
          setParticipantes(prev =>
            prev.map(p =>
              p.id === data.participante_id
                ? { ...p, status: 'chamado', tempo_chamada: new Date().toISOString() }
                : p
            )
          );
          break;
        case 'participante_atendido':
          setParticipantes(prev =>
            prev.map(p =>
              p.id === data.participante_id
                ? { ...p, status: 'atendido', tempo_atendimento: new Date().toISOString() }
                : p
            )
          );
          break;
        case 'stats_update':
          setStats(data.stats);
          break;
      }
    };

    wsRef.current.onerror = (error) => {
      console.error('WebSocket erro:', error);
    };

    wsRef.current.onclose = () => {
      console.log('WebSocket desconectado');
    };
  };

  const loadFilas = async () => {
    if (!eventoSelecionado) return;

    try {
      setLoading(true);
      const response = await api.get(`/api/filas/evento/${eventoSelecionado.id}`);
      setFilas(response.data);
    } catch (error) {
      console.error('Erro ao carregar filas:', error);
      toast({
        variant: 'destructive',
        title: 'Erro',
        description: 'Não foi possível carregar as filas',
      });
    } finally {
      setLoading(false);
    }
  };

  const loadFilaDetails = async (fila: FilaVirtual) => {
    try {
      setLoading(true);
      
      const [filaResponse, participantesResponse, statsResponse] = await Promise.all([
        api.get(`/api/filas/${fila.id}`),
        api.get(`/api/filas/${fila.id}/participantes`),
        api.get(`/api/filas/${fila.id}/estatisticas`),
      ]);

      setSelectedFila(filaResponse.data);
      setParticipantes(participantesResponse.data);
      setStats(statsResponse.data);
    } catch (error) {
      console.error('Erro ao carregar detalhes da fila:', error);
      toast({
        variant: 'destructive',
        title: 'Erro',
        description: 'Não foi possível carregar os detalhes da fila',
      });
    } finally {
      setLoading(false);
    }
  };

  const handleCreateFila = async () => {
    if (!eventoSelecionado || !novaFila.nome) return;

    try {
      const response = await api.post('/api/filas', {
        ...novaFila,
        evento_id: eventoSelecionado.id,
        capacidade_maxima: novaFila.capacidade_maxima ? parseInt(novaFila.capacidade_maxima) : null,
        tempo_medio_atendimento: parseInt(novaFila.tempo_medio_atendimento),
      });

      setFilas([...filas, response.data]);
      setCreatingFila(false);
      setNovaFila({
        nome: '',
        descricao: '',
        tipo: 'normal',
        capacidade_maxima: '',
        tempo_medio_atendimento: '5',
      });

      toast({
        title: 'Sucesso',
        description: 'Fila criada com sucesso',
      });
    } catch (error: any) {
      toast({
        variant: 'destructive',
        title: 'Erro',
        description: error.response?.data?.detail || 'Erro ao criar fila',
      });
    }
  };

  const handleEnterFila = async () => {
    if (!selectedFila || !novoParticipante.cpf || !novoParticipante.nome) return;

    try {
      const response = await api.post(`/api/filas/${selectedFila.id}/entrar`, {
        ...novoParticipante,
        prioridade: parseInt(novoParticipante.prioridade),
      });

      toast({
        title: 'Sucesso',
        description: `Sua senha é: ${response.data.senha}`,
      });

      setEnteringFila(false);
      setNovoParticipante({
        cpf: '',
        nome: '',
        telefone: '',
        prioridade: '0',
      });

      // Recarregar participantes
      loadFilaDetails(selectedFila);
    } catch (error: any) {
      toast({
        variant: 'destructive',
        title: 'Erro',
        description: error.response?.data?.detail || 'Erro ao entrar na fila',
      });
    }
  };

  const handleCallNext = async () => {
    if (!selectedFila) return;

    try {
      const response = await api.post(`/api/filas/${selectedFila.id}/chamar-proximo`);
      
      toast({
        title: 'Próximo chamado',
        description: `Senha ${response.data.senha} - ${response.data.nome}`,
      });

      // Recarregar participantes
      loadFilaDetails(selectedFila);
    } catch (error: any) {
      toast({
        variant: 'destructive',
        title: 'Erro',
        description: error.response?.data?.detail || 'Erro ao chamar próximo',
      });
    }
  };

  const handleAttendParticipant = async (participanteId: number) => {
    if (!selectedFila) return;

    try {
      await api.post(`/api/filas/${selectedFila.id}/atender/${participanteId}`);
      
      toast({
        title: 'Sucesso',
        description: 'Participante atendido',
      });

      // Recarregar participantes
      loadFilaDetails(selectedFila);
    } catch (error: any) {
      toast({
        variant: 'destructive',
        title: 'Erro',
        description: error.response?.data?.detail || 'Erro ao atender participante',
      });
    }
  };

  const handleLeaveFila = async (cpf: string) => {
    if (!selectedFila) return;

    try {
      await api.delete(`/api/filas/${selectedFila.id}/sair/${cpf}`);
      
      toast({
        title: 'Sucesso',
        description: 'Saída da fila registrada',
      });

      // Recarregar participantes
      loadFilaDetails(selectedFila);
    } catch (error: any) {
      toast({
        variant: 'destructive',
        title: 'Erro',
        description: error.response?.data?.detail || 'Erro ao sair da fila',
      });
    }
  };

  const getStatusBadge = (status: string) => {
    const statusConfig = {
      ativa: { variant: 'default', icon: CheckCircle },
      pausada: { variant: 'secondary', icon: AlertTriangle },
      finalizada: { variant: 'outline', icon: XCircle },
      aguardando: { variant: 'secondary', icon: Clock },
      chamado: { variant: 'warning', icon: Bell },
      atendido: { variant: 'success', icon: UserCheck },
      desistente: { variant: 'destructive', icon: UserX },
    };

    const config = statusConfig[status] || statusConfig.ativa;
    const Icon = config.icon;

    return (
      <Badge variant={config.variant as any}>
        <Icon className="mr-1 h-3 w-3" />
        {status}
      </Badge>
    );
  };

  const formatTempo = (minutos: number) => {
    if (minutos < 60) return `${minutos} min`;
    const horas = Math.floor(minutos / 60);
    const mins = minutos % 60;
    return `${horas}h ${mins}min`;
  };

  if (!eventoSelecionado) {
    return (
      <div className="container mx-auto p-6">
        <Alert>
          <AlertTriangle className="h-4 w-4" />
          <AlertDescription>
            Selecione um evento para gerenciar as filas virtuais
          </AlertDescription>
        </Alert>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-6">
      <div className="mb-6">
        <h1 className="text-3xl font-bold">Filas Virtuais</h1>
        <p className="text-muted-foreground">
          Gerencie filas virtuais para {eventoSelecionado.nome}
        </p>
      </div>

      {!selectedFila ? (
        <>
          <div className="flex justify-between items-center mb-6">
            <div className="flex gap-2">
              <Button onClick={() => loadFilas()} variant="outline">
                <RefreshCw className="mr-2 h-4 w-4" />
                Atualizar
              </Button>
            </div>
            
            <Dialog open={creatingFila} onOpenChange={setCreatingFila}>
              <DialogTrigger asChild>
                <Button>
                  <Plus className="mr-2 h-4 w-4" />
                  Nova Fila
                </Button>
              </DialogTrigger>
              <DialogContent>
                <DialogHeader>
                  <DialogTitle>Criar Nova Fila Virtual</DialogTitle>
                  <DialogDescription>
                    Configure uma nova fila virtual para o evento
                  </DialogDescription>
                </DialogHeader>
                <div className="grid gap-4 py-4">
                  <div className="grid grid-cols-4 items-center gap-4">
                    <Label htmlFor="nome" className="text-right">
                      Nome
                    </Label>
                    <Input
                      id="nome"
                      value={novaFila.nome}
                      onChange={(e) => setNovaFila({ ...novaFila, nome: e.target.value })}
                      className="col-span-3"
                      placeholder="Ex: Credenciamento"
                    />
                  </div>
                  <div className="grid grid-cols-4 items-center gap-4">
                    <Label htmlFor="descricao" className="text-right">
                      Descrição
                    </Label>
                    <Input
                      id="descricao"
                      value={novaFila.descricao}
                      onChange={(e) => setNovaFila({ ...novaFila, descricao: e.target.value })}
                      className="col-span-3"
                      placeholder="Descrição opcional"
                    />
                  </div>
                  <div className="grid grid-cols-4 items-center gap-4">
                    <Label htmlFor="tipo" className="text-right">
                      Tipo
                    </Label>
                    <Select
                      value={novaFila.tipo}
                      onValueChange={(value) => setNovaFila({ ...novaFila, tipo: value })}
                    >
                      <SelectTrigger className="col-span-3">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="normal">Normal</SelectItem>
                        <SelectItem value="prioridade">Com Prioridade</SelectItem>
                        <SelectItem value="agendamento">Com Agendamento</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="grid grid-cols-4 items-center gap-4">
                    <Label htmlFor="capacidade" className="text-right">
                      Capacidade
                    </Label>
                    <Input
                      id="capacidade"
                      type="number"
                      value={novaFila.capacidade_maxima}
                      onChange={(e) => setNovaFila({ ...novaFila, capacidade_maxima: e.target.value })}
                      className="col-span-3"
                      placeholder="Deixe vazio para ilimitado"
                    />
                  </div>
                  <div className="grid grid-cols-4 items-center gap-4">
                    <Label htmlFor="tempo" className="text-right">
                      Tempo médio (min)
                    </Label>
                    <Input
                      id="tempo"
                      type="number"
                      value={novaFila.tempo_medio_atendimento}
                      onChange={(e) => setNovaFila({ ...novaFila, tempo_medio_atendimento: e.target.value })}
                      className="col-span-3"
                    />
                  </div>
                </div>
                <DialogFooter>
                  <Button onClick={handleCreateFila}>Criar Fila</Button>
                </DialogFooter>
              </DialogContent>
            </Dialog>
          </div>

          {loading ? (
            <div className="flex items-center justify-center h-64">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
            </div>
          ) : (
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              {filas.map((fila) => (
                <Card
                  key={fila.id}
                  className="cursor-pointer hover:shadow-lg transition-shadow"
                  onClick={() => loadFilaDetails(fila)}
                >
                  <CardHeader>
                    <div className="flex items-center justify-between">
                      <CardTitle>{fila.nome}</CardTitle>
                      {getStatusBadge(fila.status)}
                    </div>
                    <CardDescription>{fila.descricao || 'Sem descrição'}</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-2 text-sm">
                      <div className="flex items-center justify-between">
                        <span className="text-muted-foreground">Senha atual:</span>
                        <span className="font-semibold">#{fila.senha_atual}</span>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-muted-foreground">Atendidos:</span>
                        <span>{fila.total_atendidos}</span>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-muted-foreground">Tempo médio:</span>
                        <span>{formatTempo(fila.tempo_medio_atendimento)}</span>
                      </div>
                      {fila.capacidade_maxima && (
                        <div className="flex items-center justify-between">
                          <span className="text-muted-foreground">Capacidade:</span>
                          <span>{fila.capacidade_maxima} pessoas</span>
                        </div>
                      )}
                    </div>
                    <div className="mt-4">
                      <Button variant="outline" className="w-full">
                        <ChevronRight className="mr-2 h-4 w-4" />
                        Gerenciar Fila
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </>
      ) : (
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Button variant="outline" onClick={() => setSelectedFila(null)}>
                Voltar
              </Button>
              <h2 className="text-2xl font-bold">{selectedFila.nome}</h2>
              {getStatusBadge(selectedFila.status)}
            </div>
            <div className="flex gap-2">
              <Button onClick={() => loadFilaDetails(selectedFila)} variant="outline">
                <RefreshCw className="mr-2 h-4 w-4" />
                Atualizar
              </Button>
              <Dialog open={enteringFila} onOpenChange={setEnteringFila}>
                <DialogTrigger asChild>
                  <Button>
                    <Plus className="mr-2 h-4 w-4" />
                    Entrar na Fila
                  </Button>
                </DialogTrigger>
                <DialogContent>
                  <DialogHeader>
                    <DialogTitle>Entrar na Fila</DialogTitle>
                    <DialogDescription>
                      Preencha seus dados para entrar na fila
                    </DialogDescription>
                  </DialogHeader>
                  <div className="grid gap-4 py-4">
                    <div className="grid grid-cols-4 items-center gap-4">
                      <Label htmlFor="cpf" className="text-right">
                        CPF
                      </Label>
                      <Input
                        id="cpf"
                        value={novoParticipante.cpf}
                        onChange={(e) => setNovoParticipante({ ...novoParticipante, cpf: e.target.value })}
                        className="col-span-3"
                        placeholder="000.000.000-00"
                      />
                    </div>
                    <div className="grid grid-cols-4 items-center gap-4">
                      <Label htmlFor="nome" className="text-right">
                        Nome
                      </Label>
                      <Input
                        id="nome"
                        value={novoParticipante.nome}
                        onChange={(e) => setNovoParticipante({ ...novoParticipante, nome: e.target.value })}
                        className="col-span-3"
                      />
                    </div>
                    <div className="grid grid-cols-4 items-center gap-4">
                      <Label htmlFor="telefone" className="text-right">
                        Telefone
                      </Label>
                      <Input
                        id="telefone"
                        value={novoParticipante.telefone}
                        onChange={(e) => setNovoParticipante({ ...novoParticipante, telefone: e.target.value })}
                        className="col-span-3"
                        placeholder="(00) 00000-0000"
                      />
                    </div>
                    {selectedFila.tipo === 'prioridade' && (
                      <div className="grid grid-cols-4 items-center gap-4">
                        <Label htmlFor="prioridade" className="text-right">
                          Prioridade
                        </Label>
                        <Select
                          value={novoParticipante.prioridade}
                          onValueChange={(value) => setNovoParticipante({ ...novoParticipante, prioridade: value })}
                        >
                          <SelectTrigger className="col-span-3">
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="0">Normal</SelectItem>
                            <SelectItem value="1">Idoso (60+)</SelectItem>
                            <SelectItem value="2">PCD</SelectItem>
                            <SelectItem value="3">Gestante</SelectItem>
                            <SelectItem value="4">Com criança de colo</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>
                    )}
                  </div>
                  <DialogFooter>
                    <Button onClick={handleEnterFila}>Entrar na Fila</Button>
                  </DialogFooter>
                </DialogContent>
              </Dialog>
            </div>
          </div>

          {stats && (
            <div className="grid gap-4 md:grid-cols-5">
              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Na Fila</CardTitle>
                  <Users className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{stats.total_na_fila}</div>
                  <p className="text-xs text-muted-foreground">pessoas aguardando</p>
                </CardContent>
              </Card>
              
              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Tempo Médio</CardTitle>
                  <Clock className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{formatTempo(stats.tempo_espera_medio)}</div>
                  <p className="text-xs text-muted-foreground">de espera</p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Tempo Máximo</CardTitle>
                  <Timer className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{formatTempo(stats.tempo_espera_maximo)}</div>
                  <p className="text-xs text-muted-foreground">de espera</p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Atendimentos/h</CardTitle>
                  <TrendingUp className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{stats.atendimentos_hora}</div>
                  <p className="text-xs text-muted-foreground">pessoas por hora</p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Desistência</CardTitle>
                  <UserX className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{stats.taxa_desistencia.toFixed(1)}%</div>
                  <p className="text-xs text-muted-foreground">taxa de desistência</p>
                </CardContent>
              </Card>
            </div>
          )}

          <Tabs defaultValue="aguardando" className="space-y-4">
            <TabsList>
              <TabsTrigger value="aguardando">
                Aguardando ({participantes.filter(p => p.status === 'aguardando').length})
              </TabsTrigger>
              <TabsTrigger value="chamados">
                Chamados ({participantes.filter(p => p.status === 'chamado').length})
              </TabsTrigger>
              <TabsTrigger value="atendidos">
                Atendidos ({participantes.filter(p => p.status === 'atendido').length})
              </TabsTrigger>
              <TabsTrigger value="desistentes">
                Desistentes ({participantes.filter(p => p.status === 'desistente').length})
              </TabsTrigger>
            </TabsList>

            <TabsContent value="aguardando" className="space-y-4">
              {selectedFila.status === 'ativa' && (
                <div className="flex justify-end">
                  <Button onClick={handleCallNext} size="lg">
                    <PhoneCall className="mr-2 h-4 w-4" />
                    Chamar Próximo
                  </Button>
                </div>
              )}
              
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Senha</TableHead>
                    <TableHead>Nome</TableHead>
                    <TableHead>CPF</TableHead>
                    <TableHead>Telefone</TableHead>
                    <TableHead>Entrada</TableHead>
                    <TableHead>Tempo Esperando</TableHead>
                    <TableHead>Prioridade</TableHead>
                    <TableHead>Ações</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {participantes
                    .filter(p => p.status === 'aguardando')
                    .map((participante) => (
                      <TableRow key={participante.id}>
                        <TableCell className="font-mono font-bold">
                          {participante.senha_gerada}
                        </TableCell>
                        <TableCell>{participante.nome}</TableCell>
                        <TableCell>{participante.cpf}</TableCell>
                        <TableCell>{participante.telefone || '-'}</TableCell>
                        <TableCell>
                          {format(new Date(participante.tempo_entrada), 'HH:mm', { locale: ptBR })}
                        </TableCell>
                        <TableCell>
                          {formatDistanceToNow(new Date(participante.tempo_entrada), {
                            locale: ptBR,
                            addSuffix: false,
                          })}
                        </TableCell>
                        <TableCell>
                          {participante.prioridade > 0 ? (
                            <Badge variant="destructive">Prioridade {participante.prioridade}</Badge>
                          ) : (
                            <Badge variant="outline">Normal</Badge>
                          )}
                        </TableCell>
                        <TableCell>
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => handleLeaveFila(participante.cpf)}
                          >
                            Remover
                          </Button>
                        </TableCell>
                      </TableRow>
                    ))}
                </TableBody>
              </Table>
            </TabsContent>

            <TabsContent value="chamados" className="space-y-4">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Senha</TableHead>
                    <TableHead>Nome</TableHead>
                    <TableHead>CPF</TableHead>
                    <TableHead>Telefone</TableHead>
                    <TableHead>Chamado às</TableHead>
                    <TableHead>Ações</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {participantes
                    .filter(p => p.status === 'chamado')
                    .map((participante) => (
                      <TableRow key={participante.id}>
                        <TableCell className="font-mono font-bold">
                          {participante.senha_gerada}
                        </TableCell>
                        <TableCell>{participante.nome}</TableCell>
                        <TableCell>{participante.cpf}</TableCell>
                        <TableCell>{participante.telefone || '-'}</TableCell>
                        <TableCell>
                          {participante.tempo_chamada &&
                            format(new Date(participante.tempo_chamada), 'HH:mm', { locale: ptBR })}
                        </TableCell>
                        <TableCell>
                          <Button
                            size="sm"
                            onClick={() => handleAttendParticipant(participante.id)}
                          >
                            Atender
                          </Button>
                        </TableCell>
                      </TableRow>
                    ))}
                </TableBody>
              </Table>
            </TabsContent>

            <TabsContent value="atendidos" className="space-y-4">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Senha</TableHead>
                    <TableHead>Nome</TableHead>
                    <TableHead>CPF</TableHead>
                    <TableHead>Entrada</TableHead>
                    <TableHead>Atendido às</TableHead>
                    <TableHead>Tempo Total</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {participantes
                    .filter(p => p.status === 'atendido')
                    .map((participante) => (
                      <TableRow key={participante.id}>
                        <TableCell className="font-mono font-bold">
                          {participante.senha_gerada}
                        </TableCell>
                        <TableCell>{participante.nome}</TableCell>
                        <TableCell>{participante.cpf}</TableCell>
                        <TableCell>
                          {format(new Date(participante.tempo_entrada), 'HH:mm', { locale: ptBR })}
                        </TableCell>
                        <TableCell>
                          {participante.tempo_atendimento &&
                            format(new Date(participante.tempo_atendimento), 'HH:mm', { locale: ptBR })}
                        </TableCell>
                        <TableCell>
                          {participante.tempo_atendimento &&
                            formatDistanceToNow(new Date(participante.tempo_entrada), {
                              locale: ptBR,
                              addSuffix: false,
                            })}
                        </TableCell>
                      </TableRow>
                    ))}
                </TableBody>
              </Table>
            </TabsContent>

            <TabsContent value="desistentes" className="space-y-4">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Senha</TableHead>
                    <TableHead>Nome</TableHead>
                    <TableHead>CPF</TableHead>
                    <TableHead>Entrada</TableHead>
                    <TableHead>Tempo na Fila</TableHead>
                    <TableHead>Observações</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {participantes
                    .filter(p => p.status === 'desistente')
                    .map((participante) => (
                      <TableRow key={participante.id}>
                        <TableCell className="font-mono font-bold">
                          {participante.senha_gerada}
                        </TableCell>
                        <TableCell>{participante.nome}</TableCell>
                        <TableCell>{participante.cpf}</TableCell>
                        <TableCell>
                          {format(new Date(participante.tempo_entrada), 'HH:mm', { locale: ptBR })}
                        </TableCell>
                        <TableCell>
                          {formatDistanceToNow(new Date(participante.tempo_entrada), {
                            locale: ptBR,
                            addSuffix: false,
                          })}
                        </TableCell>
                        <TableCell>{participante.observacoes || '-'}</TableCell>
                      </TableRow>
                    ))}
                </TableBody>
              </Table>
            </TabsContent>
          </Tabs>
        </div>
      )}
    </div>
  );
}