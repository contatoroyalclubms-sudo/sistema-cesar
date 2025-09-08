import React, { useState, useEffect } from 'react';
import { Ticket, QrCode, Download, Upload, Plus, Edit, Trash2, Send, CheckCircle, XCircle, AlertCircle, Package, Users, TrendingUp, Calendar, Clock, DollarSign } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Textarea } from '@/components/ui/textarea';
import { Switch } from '@/components/ui/switch';
import { toast } from '@/hooks/use-toast';
import api from '@/utils/api';
import { format } from 'date-fns';
import { ptBR } from 'date-fns/locale';

interface TipoTicket {
  id: number;
  nome: string;
  descricao?: string;
  valor: number;
  taxa_servico: number;
  quantidade_total: number;
  quantidade_vendida: number;
  data_inicio_venda?: string;
  data_fim_venda?: string;
  minimo_compra: number;
  maximo_compra: number;
  ativo: boolean;
  evento_id: number;
  criado_em: string;
}

interface LoteTicket {
  id: number;
  nome: string;
  numero_lote: number;
  tipo_ticket_id: number;
  quantidade: number;
  quantidade_vendida: number;
  valor: number;
  data_inicio: string;
  data_fim: string;
  ativo: boolean;
  criado_em: string;
}

interface TicketVendido {
  id: number;
  codigo: string;
  tipo_ticket_id: number;
  lote_id?: number;
  cliente_id: number;
  valor_pago: number;
  status: 'pendente' | 'pago' | 'usado' | 'cancelado';
  data_compra: string;
  data_uso?: string;
  qrcode: string;
  cliente?: {
    nome: string;
    email: string;
    cpf: string;
  };
  tipo?: TipoTicket;
  lote?: LoteTicket;
}

interface TransferenciaTicket {
  id: number;
  ticket_id: number;
  cliente_origem_id: number;
  cliente_destino_id: number;
  status: 'pendente' | 'concluida' | 'cancelada';
  data_solicitacao: string;
  data_conclusao?: string;
  motivo?: string;
}

interface EstatisticasVenda {
  total_vendido: number;
  receita_total: number;
  tickets_vendidos: number;
  tickets_disponiveis: number;
  taxa_ocupacao: number;
  vendas_por_dia: Array<{ data: string; vendas: number; receita: number }>;
  vendas_por_tipo: Array<{ tipo: string; quantidade: number; receita: number }>;
}

export default function TicketsModule() {
  const [tiposTicket, setTiposTicket] = useState<TipoTicket[]>([]);
  const [lotes, setLotes] = useState<LoteTicket[]>([]);
  const [ticketsVendidos, setTicketsVendidos] = useState<TicketVendido[]>([]);
  const [transferencias, setTransferencias] = useState<TransferenciaTicket[]>([]);
  const [estatisticas, setEstatisticas] = useState<EstatisticasVenda | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('tipos');
  const [showNovoTipo, setShowNovoTipo] = useState(false);
  const [showNovoLote, setShowNovoLote] = useState(false);
  const [selectedEvento, setSelectedEvento] = useState<number | null>(null);
  const [filtroStatus, setFiltroStatus] = useState('todos');

  const [novoTipo, setNovoTipo] = useState({
    nome: '',
    descricao: '',
    valor: 0,
    taxa_servico: 0,
    quantidade_total: 0,
    minimo_compra: 1,
    maximo_compra: 10,
    ativo: true,
    evento_id: selectedEvento || 0
  });

  const [novoLote, setNovoLote] = useState({
    nome: '',
    numero_lote: 1,
    tipo_ticket_id: 0,
    quantidade: 0,
    valor: 0,
    data_inicio: '',
    data_fim: '',
    ativo: true
  });

  useEffect(() => {
    carregarDados();
  }, [activeTab, selectedEvento]);

  const carregarDados = async () => {
    setLoading(true);
    try {
      if (activeTab === 'tipos') {
        const response = await api.get('/api/tickets/tipos', {
          params: selectedEvento ? { evento_id: selectedEvento } : {}
        });
        setTiposTicket(response.data);
      } else if (activeTab === 'lotes') {
        const response = await api.get('/api/tickets/lotes', {
          params: selectedEvento ? { evento_id: selectedEvento } : {}
        });
        setLotes(response.data);
      } else if (activeTab === 'vendidos') {
        const response = await api.get('/api/tickets/vendidos', {
          params: selectedEvento ? { evento_id: selectedEvento } : {}
        });
        setTicketsVendidos(response.data);
      } else if (activeTab === 'transferencias') {
        const response = await api.get('/api/tickets/transferencias');
        setTransferencias(response.data);
      } else if (activeTab === 'estatisticas') {
        const response = await api.get('/api/tickets/estatisticas', {
          params: selectedEvento ? { evento_id: selectedEvento } : {}
        });
        setEstatisticas(response.data);
      }
    } catch (error) {
      console.error('Erro ao carregar dados:', error);
      toast({
        title: "Erro",
        description: "Não foi possível carregar os dados",
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  };

  const criarTipoTicket = async () => {
    try {
      await api.post('/api/tickets/tipos', novoTipo);
      toast({
        title: "Sucesso",
        description: "Tipo de ticket criado com sucesso"
      });
      setShowNovoTipo(false);
      setNovoTipo({
        nome: '',
        descricao: '',
        valor: 0,
        taxa_servico: 0,
        quantidade_total: 0,
        minimo_compra: 1,
        maximo_compra: 10,
        ativo: true,
        evento_id: selectedEvento || 0
      });
      carregarDados();
    } catch (error) {
      console.error('Erro ao criar tipo de ticket:', error);
      toast({
        title: "Erro",
        description: "Não foi possível criar o tipo de ticket",
        variant: "destructive"
      });
    }
  };

  const criarLote = async () => {
    try {
      await api.post('/api/tickets/lotes', novoLote);
      toast({
        title: "Sucesso",
        description: "Lote criado com sucesso"
      });
      setShowNovoLote(false);
      setNovoLote({
        nome: '',
        numero_lote: 1,
        tipo_ticket_id: 0,
        quantidade: 0,
        valor: 0,
        data_inicio: '',
        data_fim: '',
        ativo: true
      });
      carregarDados();
    } catch (error) {
      console.error('Erro ao criar lote:', error);
      toast({
        title: "Erro",
        description: "Não foi possível criar o lote",
        variant: "destructive"
      });
    }
  };

  const validarTicket = async (codigo: string) => {
    try {
      const response = await api.post('/api/tickets/validar', { codigo });
      toast({
        title: "Sucesso",
        description: response.data.message || "Ticket validado com sucesso"
      });
      carregarDados();
    } catch (error) {
      console.error('Erro ao validar ticket:', error);
      toast({
        title: "Erro",
        description: "Ticket inválido ou já utilizado",
        variant: "destructive"
      });
    }
  };

  const enviarTicket = async (ticketId: number) => {
    try {
      await api.post(`/api/tickets/${ticketId}/enviar`);
      toast({
        title: "Sucesso",
        description: "Ticket enviado por email com sucesso"
      });
    } catch (error) {
      console.error('Erro ao enviar ticket:', error);
      toast({
        title: "Erro",
        description: "Não foi possível enviar o ticket",
        variant: "destructive"
      });
    }
  };

  const cancelarTicket = async (ticketId: number) => {
    if (!confirm('Tem certeza que deseja cancelar este ticket?')) return;
    
    try {
      await api.post(`/api/tickets/${ticketId}/cancelar`);
      toast({
        title: "Sucesso",
        description: "Ticket cancelado com sucesso"
      });
      carregarDados();
    } catch (error) {
      console.error('Erro ao cancelar ticket:', error);
      toast({
        title: "Erro",
        description: "Não foi possível cancelar o ticket",
        variant: "destructive"
      });
    }
  };

  const aprovarTransferencia = async (transferenciaId: number) => {
    try {
      await api.post(`/api/tickets/transferencias/${transferenciaId}/aprovar`);
      toast({
        title: "Sucesso",
        description: "Transferência aprovada com sucesso"
      });
      carregarDados();
    } catch (error) {
      console.error('Erro ao aprovar transferência:', error);
      toast({
        title: "Erro",
        description: "Não foi possível aprovar a transferência",
        variant: "destructive"
      });
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'pago':
      case 'concluida':
        return <Badge className="bg-green-100 text-green-800">
{status}</Badge>;
      case 'pendente':
        return <Badge variant="secondary">{status}</Badge>;
      case 'usado':
        return <Badge className="bg-blue-100 text-blue-800">{status}</Badge>;
      case 'cancelado':
      case 'cancelada':
        return <Badge variant="destructive">{status}</Badge>;
      default:
        return <Badge variant="outline">{status}</Badge>;
    }
  };

  const getDisponibilidade = (tipo: TipoTicket) => {
    const disponivel = tipo.quantidade_total - tipo.quantidade_vendida;
    const percentual = (tipo.quantidade_vendida / tipo.quantidade_total) * 100;
    
    if (percentual >= 90) {
      return { cor: 'text-red-600', texto: `Últimas ${disponivel} unidades!` };
    } else if (percentual >= 70) {
      return { cor: 'text-yellow-600', texto: `${disponivel} disponíveis` };
    } else {
      return { cor: 'text-green-600', texto: `${disponivel} disponíveis` };
    }
  };

  return (
    <div className="container mx-auto py-6 space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">Tickets e Ingressos</h1>
          <p className="text-muted-foreground">Gerencie a venda e controle de ingressos</p>
        </div>
        <div className="flex gap-2">
          <Select value={selectedEvento?.toString() || ''} onValueChange={(value) => setSelectedEvento(value ? parseInt(value) : null)}>
            <SelectTrigger className="w-[200px]">
              <SelectValue placeholder="Selecione um evento" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="">Todos os eventos</SelectItem>
              <SelectItem value="1">Evento 1</SelectItem>
              <SelectItem value="2">Evento 2</SelectItem>
            </SelectContent>
          </Select>
          <Dialog open={showNovoTipo} onOpenChange={setShowNovoTipo}>
            <DialogTrigger asChild>
              <Button>
                <Plus className="mr-2 h-4 w-4" />
                Novo Tipo
              </Button>
            </DialogTrigger>
            <DialogContent className="sm:max-w-[500px]">
              <DialogHeader>
                <DialogTitle>Criar Tipo de Ticket</DialogTitle>
                <DialogDescription>
                  Configure um novo tipo de ingresso
                </DialogDescription>
              </DialogHeader>
              <div className="grid gap-4 py-4">
                <div className="grid gap-2">
                  <Label htmlFor="nome">Nome</Label>
                  <Input
                    id="nome"
                    value={novoTipo.nome}
                    onChange={(e) => setNovoTipo({...novoTipo, nome: e.target.value})}
                    placeholder="Ex: Pista, VIP, Camarote"
                  />
                </div>
                <div className="grid gap-2">
                  <Label htmlFor="descricao">Descrição</Label>
                  <Textarea
                    id="descricao"
                    value={novoTipo.descricao}
                    onChange={(e) => setNovoTipo({...novoTipo, descricao: e.target.value})}
                    placeholder="Benefícios e detalhes do ingresso"
                  />
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div className="grid gap-2">
                    <Label htmlFor="valor">Valor (R$)</Label>
                    <Input
                      id="valor"
                      type="number"
                      value={novoTipo.valor}
                      onChange={(e) => setNovoTipo({...novoTipo, valor: parseFloat(e.target.value)})}
                      placeholder="0.00"
                    />
                  </div>
                  <div className="grid gap-2">
                    <Label htmlFor="taxa">Taxa de Serviço (R$)</Label>
                    <Input
                      id="taxa"
                      type="number"
                      value={novoTipo.taxa_servico}
                      onChange={(e) => setNovoTipo({...novoTipo, taxa_servico: parseFloat(e.target.value)})}
                      placeholder="0.00"
                    />
                  </div>
                </div>
                <div className="grid gap-2">
                  <Label htmlFor="quantidade">Quantidade Total</Label>
                  <Input
                    id="quantidade"
                    type="number"
                    value={novoTipo.quantidade_total}
                    onChange={(e) => setNovoTipo({...novoTipo, quantidade_total: parseInt(e.target.value)})}
                    placeholder="100"
                  />
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div className="grid gap-2">
                    <Label htmlFor="minimo">Mínimo por Compra</Label>
                    <Input
                      id="minimo"
                      type="number"
                      value={novoTipo.minimo_compra}
                      onChange={(e) => setNovoTipo({...novoTipo, minimo_compra: parseInt(e.target.value)})}
                      placeholder="1"
                    />
                  </div>
                  <div className="grid gap-2">
                    <Label htmlFor="maximo">Máximo por Compra</Label>
                    <Input
                      id="maximo"
                      type="number"
                      value={novoTipo.maximo_compra}
                      onChange={(e) => setNovoTipo({...novoTipo, maximo_compra: parseInt(e.target.value)})}
                      placeholder="10"
                    />
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  <Switch
                    id="ativo"
                    checked={novoTipo.ativo}
                    onCheckedChange={(checked) => setNovoTipo({...novoTipo, ativo: checked})}
                  />
                  <Label htmlFor="ativo">Ativar vendas imediatamente</Label>
                </div>
              </div>
              <DialogFooter>
                <Button variant="outline" onClick={() => setShowNovoTipo(false)}>
                  Cancelar
                </Button>
                <Button onClick={criarTipoTicket}>Criar Tipo</Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>
        </div>
      </div>

      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium">Total Vendido</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              R$ {estatisticas?.receita_total.toLocaleString('pt-BR') || '0'}
            </div>
            <p className="text-xs text-muted-foreground mt-1">
              {estatisticas?.tickets_vendidos || 0} tickets
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium">Disponíveis</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {estatisticas?.tickets_disponiveis || 0}
            </div>
            <p className="text-xs text-muted-foreground mt-1">
              {estatisticas?.taxa_ocupacao || 0}% vendido
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium">Ticket Médio</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              R$ {estatisticas && estatisticas.tickets_vendidos > 0 
                ? (estatisticas.receita_total / estatisticas.tickets_vendidos).toFixed(2)
                : '0'}
            </div>
            <p className="text-xs text-muted-foreground mt-1">
              Por ingresso
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium">Check-ins</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {ticketsVendidos.filter(t => t.status === 'usado').length}
            </div>
            <p className="text-xs text-muted-foreground mt-1">
              Tickets validados
            </p>
          </CardContent>
        </Card>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <TabsList className="grid w-full grid-cols-5">
          <TabsTrigger value="tipos">Tipos de Tickets</TabsTrigger>
          <TabsTrigger value="lotes">Lotes</TabsTrigger>
          <TabsTrigger value="vendidos">Vendidos</TabsTrigger>
          <TabsTrigger value="transferencias">Transferências</TabsTrigger>
          <TabsTrigger value="estatisticas">Estatísticas</TabsTrigger>
        </TabsList>

        <TabsContent value="tipos" className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {tiposTicket.map(tipo => {
              const disponibilidade = getDisponibilidade(tipo);
              return (
                <Card key={tipo.id}>
                  <CardHeader>
                    <div className="flex justify-between items-start">
                      <div>
                        <CardTitle className="text-lg">{tipo.nome}</CardTitle>
                        <CardDescription>{tipo.descricao}</CardDescription>
                      </div>
                      <Badge variant={tipo.ativo ? 'default' : 'secondary'}>
                        {tipo.ativo ? 'Ativo' : 'Inativo'}
                      </Badge>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-2">
                      <div className="flex justify-between text-sm">
                        <span>Valor:</span>
                        <span className="font-bold">R$ {tipo.valor.toFixed(2)}</span>
                      </div>
                      <div className="flex justify-between text-sm">
                        <span>Taxa:</span>
                        <span>R$ {tipo.taxa_servico.toFixed(2)}</span>
                      </div>
                      <div className="flex justify-between text-sm">
                        <span>Total:</span>
                        <span className="font-bold">R$ {(tipo.valor + tipo.taxa_servico).toFixed(2)}</span>
                      </div>
                      <div className="pt-2 border-t">
                        <div className="flex justify-between text-sm">
                          <span>Vendidos:</span>
                          <span>{tipo.quantidade_vendida} / {tipo.quantidade_total}</span>
                        </div>
                        <p className={`text-xs mt-1 ${disponibilidade.cor}`}>
                          {disponibilidade.texto}
                        </p>
                      </div>
                      <div className="pt-2">
                        <div className="w-full bg-gray-200 rounded-full h-2">
                          <div 
                            className="bg-blue-600 h-2 rounded-full"
                            style={{ width: `${(tipo.quantidade_vendida / tipo.quantidade_total) * 100}%` }}
                          />
                        </div>
                      </div>
                    </div>
                  </CardContent>
                  <CardFooter className="flex gap-2">
                    <Button variant="outline" size="sm" className="flex-1">
                      <Edit className="mr-1 h-3 w-3" />
                      Editar
                    </Button>
                    <Button variant="outline" size="sm" className="flex-1">
                      <Package className="mr-1 h-3 w-3" />
                      Lotes
                    </Button>
                  </CardFooter>
                </Card>
              );
            })}
          </div>
        </TabsContent>

        <TabsContent value="lotes" className="space-y-4">
          <div className="flex justify-end mb-4">
            <Dialog open={showNovoLote} onOpenChange={setShowNovoLote}>
              <DialogTrigger asChild>
                <Button variant="outline">
                  <Plus className="mr-2 h-4 w-4" />
                  Novo Lote
                </Button>
              </DialogTrigger>
              <DialogContent>
                <DialogHeader>
                  <DialogTitle>Criar Lote</DialogTitle>
                  <DialogDescription>
                    Configure um novo lote de vendas
                  </DialogDescription>
                </DialogHeader>
                <div className="grid gap-4 py-4">
                  <div className="grid gap-2">
                    <Label>Nome do Lote</Label>
                    <Input
                      value={novoLote.nome}
                      onChange={(e) => setNovoLote({...novoLote, nome: e.target.value})}
                      placeholder="Ex: 1º Lote"
                    />
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div className="grid gap-2">
                      <Label>Número</Label>
                      <Input
                        type="number"
                        value={novoLote.numero_lote}
                        onChange={(e) => setNovoLote({...novoLote, numero_lote: parseInt(e.target.value)})}
                      />
                    </div>
                    <div className="grid gap-2">
                      <Label>Quantidade</Label>
                      <Input
                        type="number"
                        value={novoLote.quantidade}
                        onChange={(e) => setNovoLote({...novoLote, quantidade: parseInt(e.target.value)})}
                      />
                    </div>
                  </div>
                  <div className="grid gap-2">
                    <Label>Valor (R$)</Label>
                    <Input
                      type="number"
                      value={novoLote.valor}
                      onChange={(e) => setNovoLote({...novoLote, valor: parseFloat(e.target.value)})}
                    />
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div className="grid gap-2">
                      <Label>Data Início</Label>
                      <Input
                        type="datetime-local"
                        value={novoLote.data_inicio}
                        onChange={(e) => setNovoLote({...novoLote, data_inicio: e.target.value})}
                      />
                    </div>
                    <div className="grid gap-2">
                      <Label>Data Fim</Label>
                      <Input
                        type="datetime-local"
                        value={novoLote.data_fim}
                        onChange={(e) => setNovoLote({...novoLote, data_fim: e.target.value})}
                      />
                    </div>
                  </div>
                </div>
                <DialogFooter>
                  <Button variant="outline" onClick={() => setShowNovoLote(false)}>
                    Cancelar
                  </Button>
                  <Button onClick={criarLote}>Criar Lote</Button>
                </DialogFooter>
              </DialogContent>
            </Dialog>
          </div>

          <div className="grid gap-4">
            {lotes.map(lote => (
              <Card key={lote.id}>
                <CardHeader>
                  <div className="flex justify-between items-center">
                    <div>
                      <CardTitle className="text-lg">{lote.nome}</CardTitle>
                      <CardDescription>Lote #{lote.numero_lote}</CardDescription>
                    </div>
                    <Badge variant={lote.ativo ? 'default' : 'secondary'}>
                      {lote.ativo ? 'Ativo' : 'Inativo'}
                    </Badge>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div>
                      <p className="text-sm text-muted-foreground">Valor</p>
                      <p className="font-bold">R$ {lote.valor.toFixed(2)}</p>
                    </div>
                    <div>
                      <p className="text-sm text-muted-foreground">Vendidos</p>
                      <p className="font-bold">{lote.quantidade_vendida} / {lote.quantidade}</p>
                    </div>
                    <div>
                      <p className="text-sm text-muted-foreground">Início</p>
                      <p className="text-sm">{format(new Date(lote.data_inicio), 'dd/MM HH:mm')}</p>
                    </div>
                    <div>
                      <p className="text-sm text-muted-foreground">Fim</p>
                      <p className="text-sm">{format(new Date(lote.data_fim), 'dd/MM HH:mm')}</p>
                    </div>
                  </div>
                  <div className="mt-4">
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div 
                        className="bg-green-600 h-2 rounded-full"
                        style={{ width: `${(lote.quantidade_vendida / lote.quantidade) * 100}%` }}
                      />
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="vendidos" className="space-y-4">
          <div className="flex gap-4 items-center mb-4">
            <Input
              placeholder="Buscar por código, nome ou CPF..."
              className="max-w-sm"
            />
            <Select value={filtroStatus} onValueChange={setFiltroStatus}>
              <SelectTrigger className="w-[180px]">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="todos">Todos</SelectItem>
                <SelectItem value="pendente">Pendente</SelectItem>
                <SelectItem value="pago">Pago</SelectItem>
                <SelectItem value="usado">Usado</SelectItem>
                <SelectItem value="cancelado">Cancelado</SelectItem>
              </SelectContent>
            </Select>
            <Button variant="outline">
              <Download className="mr-2 h-4 w-4" />
              Exportar
            </Button>
          </div>

          <Card>
            <CardContent className="p-0">
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="border-b">
                    <tr>
                      <th className="text-left p-4">Código</th>
                      <th className="text-left p-4">Cliente</th>
                      <th className="text-left p-4">Tipo</th>
                      <th className="text-left p-4">Valor</th>
                      <th className="text-left p-4">Data Compra</th>
                      <th className="text-left p-4">Status</th>
                      <th className="text-left p-4">Ações</th>
                    </tr>
                  </thead>
                  <tbody>
                    {ticketsVendidos
                      .filter(t => filtroStatus === 'todos' || t.status === filtroStatus)
                      .map(ticket => (
                        <tr key={ticket.id} className="border-b">
                          <td className="p-4 font-mono text-sm">{ticket.codigo}</td>
                          <td className="p-4">
                            <div>
                              <p className="font-medium">{ticket.cliente?.nome}</p>
                              <p className="text-sm text-muted-foreground">{ticket.cliente?.cpf}</p>
                            </div>
                          </td>
                          <td className="p-4">{ticket.tipo?.nome}</td>
                          <td className="p-4">R$ {ticket.valor_pago.toFixed(2)}</td>
                          <td className="p-4 text-sm">
                            {format(new Date(ticket.data_compra), 'dd/MM/yyyy HH:mm')}
                          </td>
                          <td className="p-4">{getStatusBadge(ticket.status)}</td>
                          <td className="p-4">
                            <div className="flex gap-1">
                              <Button 
                                variant="ghost" 
                                size="icon"
                                onClick={() => enviarTicket(ticket.id)}
                              >
                                <Send className="h-4 w-4" />
                              </Button>
                              <Button variant="ghost" size="icon">
                                <QrCode className="h-4 w-4" />
                              </Button>
                              {ticket.status === 'pago' && (
                                <Button 
                                  variant="ghost" 
                                  size="icon"
                                  onClick={() => cancelarTicket(ticket.id)}
                                >
                                  <XCircle className="h-4 w-4" />
                                </Button>
                              )}
                            </div>
                          </td>
                        </tr>
                      ))}
                  </tbody>
                </table>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="transferencias" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Transferências de Tickets</CardTitle>
              <CardDescription>
                Gerencie as solicitações de transferência entre clientes
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {transferencias.map(transferencia => (
                  <div key={transferencia.id} className="flex items-center justify-between p-4 border rounded-lg">
                    <div>
                      <p className="font-medium">Ticket #{transferencia.ticket_id}</p>
                      <p className="text-sm text-muted-foreground">
                        Solicitado em {format(new Date(transferencia.data_solicitacao), 'dd/MM/yyyy HH:mm')}
                      </p>
                      {transferencia.motivo && (
                        <p className="text-sm mt-1">Motivo: {transferencia.motivo}</p>
                      )}
                    </div>
                    <div className="flex items-center gap-2">
                      {getStatusBadge(transferencia.status)}
                      {transferencia.status === 'pendente' && (
                        <>
                          <Button 
                            variant="outline" 
                            size="sm"
                            onClick={() => aprovarTransferencia(transferencia.id)}
                          >
                            <CheckCircle className="mr-1 h-3 w-3" />
                            Aprovar
                          </Button>
                          <Button variant="outline" size="sm">
                            <XCircle className="mr-1 h-3 w-3" />
                            Recusar
                          </Button>
                        </>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="estatisticas" className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle>Vendas por Tipo</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {estatisticas?.vendas_por_tipo.map(tipo => (
                    <div key={tipo.tipo} className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <Ticket className="h-4 w-4 text-muted-foreground" />
                        <div>
                          <p className="font-medium">{tipo.tipo}</p>
                          <p className="text-sm text-muted-foreground">{tipo.quantidade} vendidos</p>
                        </div>
                      </div>
                      <p className="font-bold">R$ {tipo.receita.toFixed(2)}</p>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Vendas Diárias</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {estatisticas?.vendas_por_dia.slice(0, 5).map(dia => (
                    <div key={dia.data} className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <Calendar className="h-4 w-4 text-muted-foreground" />
                        <div>
                          <p className="font-medium">{format(new Date(dia.data), 'dd/MM')}</p>
                          <p className="text-sm text-muted-foreground">{dia.vendas} tickets</p>
                        </div>
                      </div>
                      <p className="font-bold">R$ {dia.receita.toFixed(2)}</p>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}