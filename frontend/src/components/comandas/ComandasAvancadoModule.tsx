import React, { useState, useEffect, useCallback } from 'react';
import { Search, Filter, UserCheck, CreditCard, Lock, Ban, AlertCircle, DollarSign, Clock, Activity, CheckCircle, XCircle, RefreshCw, Download, Upload, Users, Tag, Hash, Calendar, TrendingUp } from 'lucide-react';
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
import { Checkbox } from '@/components/ui/checkbox';
import { DatePickerWithRange } from '@/components/ui/date-range-picker';
import { toast } from '@/hooks/use-toast';
import { formatDistanceToNow, format } from 'date-fns';
import { ptBR } from 'date-fns/locale';
import api from '@/utils/api';

interface Comanda {
  id: number;
  numero_comanda: string;
  cpf_cliente?: string;
  nome_cliente?: string;
  tipo: 'FISICA' | 'VIRTUAL' | 'RFID' | 'NFC' | 'TAG';
  codigo_rfid?: string;
  qr_code?: string;
  tag_numero?: string;
  saldo_atual: number;
  saldo_bloqueado: number;
  saldo_total_gasto: number;
  status: 'ATIVA' | 'BLOQUEADA' | 'CANCELADA' | 'FINALIZADA';
  evento_id: number;
  mesa_vinculada?: string;
  grupo_id?: number;
  ultima_transacao?: string;
  total_transacoes: number;
  criado_em: string;
  atualizado_em: string;
  
  // Campos adicionados para funcionalidades avançadas
  pre_ativada?: boolean;
  data_pre_ativacao?: string;
  limite_credito?: number;
  desconto_aplicado?: number;
  observacoes?: string;
  historico_consumo?: ConsumoItem[];
  alertas?: AlertaComanda[];
}

interface ConsumoItem {
  id: number;
  produto: string;
  quantidade: number;
  valor_unitario: number;
  valor_total: number;
  data_consumo: string;
  operador?: string;
}

interface AlertaComanda {
  tipo: 'limite_atingido' | 'tentativa_bloqueio' | 'consumo_anormal';
  mensagem: string;
  data: string;
}

interface FiltrosComanda {
  busca: string;
  tipo_busca: 'cpf' | 'tag' | 'numero' | 'nome' | 'todos';
  status: string[];
  periodo?: { from: Date | undefined; to: Date | undefined };
  caixa?: string;
  apenas_ativas: boolean;
  apenas_abertas: boolean;
  apenas_bloqueadas: boolean;
  com_consumo: boolean;
  sem_consumo: boolean;
}

interface GrupoComandas {
  id: number;
  nome: string;
  descricao?: string;
  total_comandas: number;
  comandas_ativas: number;
  saldo_total: number;
  criado_em: string;
}

interface EstatisticasComandas {
  total: number;
  ativas: number;
  bloqueadas: number;
  finalizadas: number;
  saldo_total: number;
  ticket_medio: number;
  comandas_com_consumo: number;
  comandas_sem_consumo: number;
}

export default function ComandasAvancadoModule() {
  const [comandas, setComandas] = useState<Comanda[]>([]);
  const [grupos, setGrupos] = useState<GrupoComandas[]>([]);
  const [estatisticas, setEstatisticas] = useState<EstatisticasComandas | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('gerenciar');
  const [selectedComanda, setSelectedComanda] = useState<Comanda | null>(null);
  const [showDetalhes, setShowDetalhes] = useState(false);
  const [showBloqueio, setShowBloqueio] = useState(false);
  const [showRecarga, setShowRecarga] = useState(false);
  const [showImportacao, setShowImportacao] = useState(false);
  const [showGrupo, setShowGrupo] = useState(false);
  
  const [filtros, setFiltros] = useState<FiltrosComanda>({
    busca: '',
    tipo_busca: 'todos',
    status: [],
    apenas_ativas: false,
    apenas_abertas: false,
    apenas_bloqueadas: false,
    com_consumo: false,
    sem_consumo: false
  });

  const [novaRecarga, setNovaRecarga] = useState({
    valor: 0,
    forma_pagamento: 'PIX',
    observacao: ''
  });

  const [novoBloqueio, setNovoBloqueio] = useState({
    motivo: '',
    tipo: 'temporario',
    notificar_cliente: true
  });

  const [novoGrupo, setNovoGrupo] = useState({
    nome: '',
    descricao: '',
    comandas_ids: [] as number[]
  });

  // Carregar dados
  useEffect(() => {
    carregarDados();
    const interval = setInterval(carregarDados, 30000); // Atualizar a cada 30 segundos
    return () => clearInterval(interval);
  }, [activeTab, filtros]);

  const carregarDados = async () => {
    setLoading(true);
    try {
      const params = construirParametros();
      
      if (activeTab === 'gerenciar') {
        const [comandasRes, statsRes] = await Promise.all([
          api.get('/api/comandas', { params }),
          api.get('/api/comandas/estatisticas')
        ]);
        setComandas(comandasRes.data);
        setEstatisticas(statsRes.data);
      } else if (activeTab === 'grupos') {
        const response = await api.get('/api/comandas/grupos');
        setGrupos(response.data);
      } else if (activeTab === 'pre-ativacao') {
        const response = await api.get('/api/comandas/pre-ativadas');
        setComandas(response.data);
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

  const construirParametros = () => {
    const params: any = {};
    
    if (filtros.busca) {
      params.busca = filtros.busca;
      params.tipo_busca = filtros.tipo_busca;
    }
    
    if (filtros.status.length > 0) {
      params.status = filtros.status.join(',');
    }
    
    if (filtros.periodo?.from) {
      params.data_inicio = format(filtros.periodo.from, 'yyyy-MM-dd');
    }
    
    if (filtros.periodo?.to) {
      params.data_fim = format(filtros.periodo.to, 'yyyy-MM-dd');
    }
    
    if (filtros.caixa) {
      params.caixa = filtros.caixa;
    }
    
    // Filtros de checkbox
    params.apenas_ativas = filtros.apenas_ativas;
    params.apenas_abertas = filtros.apenas_abertas;
    params.apenas_bloqueadas = filtros.apenas_bloqueadas;
    params.com_consumo = filtros.com_consumo;
    params.sem_consumo = filtros.sem_consumo;
    
    return params;
  };

  // Busca avançada com debounce
  const buscarComandas = useCallback(
    debounce(async (termo: string, tipo: string) => {
      if (termo.length < 3 && tipo !== 'numero') return;
      
      try {
        const response = await api.get('/api/comandas/buscar', {
          params: { termo, tipo }
        });
        setComandas(response.data);
      } catch (error) {
        console.error('Erro na busca:', error);
      }
    }, 500),
    []
  );

  // Ações em comandas
  const recarregarComanda = async () => {
    if (!selectedComanda) return;
    
    try {
      await api.post(`/api/comandas/${selectedComanda.id}/recarregar`, novaRecarga);
      toast({
        title: "Sucesso",
        description: `Comanda recarregada com R$ ${novaRecarga.valor.toFixed(2)}`
      });
      setShowRecarga(false);
      setNovaRecarga({ valor: 0, forma_pagamento: 'PIX', observacao: '' });
      carregarDados();
    } catch (error) {
      console.error('Erro ao recarregar:', error);
      toast({
        title: "Erro",
        description: "Não foi possível recarregar a comanda",
        variant: "destructive"
      });
    }
  };

  const bloquearComanda = async () => {
    if (!selectedComanda) return;
    
    try {
      await api.post(`/api/comandas/${selectedComanda.id}/bloquear`, novoBloqueio);
      toast({
        title: "Comanda bloqueada",
        description: "A comanda foi bloqueada com sucesso"
      });
      setShowBloqueio(false);
      setNovoBloqueio({ motivo: '', tipo: 'temporario', notificar_cliente: true });
      carregarDados();
    } catch (error) {
      console.error('Erro ao bloquear:', error);
      toast({
        title: "Erro",
        description: "Não foi possível bloquear a comanda",
        variant: "destructive"
      });
    }
  };

  const desbloquearComanda = async (comandaId: number) => {
    try {
      await api.post(`/api/comandas/${comandaId}/desbloquear`);
      toast({
        title: "Comanda desbloqueada",
        description: "A comanda foi desbloqueada com sucesso"
      });
      carregarDados();
    } catch (error) {
      console.error('Erro ao desbloquear:', error);
      toast({
        title: "Erro",
        description: "Não foi possível desbloquear a comanda",
        variant: "destructive"
      });
    }
  };

  const finalizarComanda = async (comandaId: number) => {
    if (!confirm('Deseja realmente finalizar esta comanda?')) return;
    
    try {
      await api.post(`/api/comandas/${comandaId}/finalizar`);
      toast({
        title: "Comanda finalizada",
        description: "A comanda foi finalizada com sucesso"
      });
      carregarDados();
    } catch (error) {
      console.error('Erro ao finalizar:', error);
      toast({
        title: "Erro",
        description: "Não foi possível finalizar a comanda",
        variant: "destructive"
      });
    }
  };

  // Importação em lote
  const importarComandas = async (arquivo: File) => {
    const formData = new FormData();
    formData.append('arquivo', arquivo);
    
    try {
      const response = await api.post('/api/comandas/importar', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      toast({
        title: "Importação concluída",
        description: `${response.data.total} comandas importadas com sucesso`
      });
      setShowImportacao(false);
      carregarDados();
    } catch (error) {
      console.error('Erro na importação:', error);
      toast({
        title: "Erro na importação",
        description: "Verifique o arquivo e tente novamente",
        variant: "destructive"
      });
    }
  };

  // Criar grupo
  const criarGrupo = async () => {
    try {
      await api.post('/api/comandas/grupos', novoGrupo);
      toast({
        title: "Grupo criado",
        description: "O grupo de comandas foi criado com sucesso"
      });
      setShowGrupo(false);
      setNovoGrupo({ nome: '', descricao: '', comandas_ids: [] });
      carregarDados();
    } catch (error) {
      console.error('Erro ao criar grupo:', error);
      toast({
        title: "Erro",
        description: "Não foi possível criar o grupo",
        variant: "destructive"
      });
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'ATIVA': return 'bg-green-100 text-green-800';
      case 'BLOQUEADA': return 'bg-red-100 text-red-800';
      case 'CANCELADA': return 'bg-gray-100 text-gray-800';
      case 'FINALIZADA': return 'bg-blue-100 text-blue-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getTipoIcon = (tipo: string) => {
    switch (tipo) {
      case 'RFID': return '📡';
      case 'NFC': return '📱';
      case 'TAG': return '🏷️';
      case 'VIRTUAL': return '💳';
      case 'FISICA': return '🎫';
      default: return '🎫';
    }
  };

  return (
    <div className="container mx-auto py-6 space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">Gestão Avançada de Comandas</h1>
          <p className="text-muted-foreground">Sistema completo de controle e monitoramento</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={() => carregarDados()}>
            <RefreshCw className="mr-2 h-4 w-4" />
            Atualizar
          </Button>
          <Dialog open={showImportacao} onOpenChange={setShowImportacao}>
            <DialogTrigger asChild>
              <Button variant="outline">
                <Upload className="mr-2 h-4 w-4" />
                Importar
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Importar Comandas em Lote</DialogTitle>
                <DialogDescription>
                  Faça upload de um arquivo CSV ou Excel com as comandas
                </DialogDescription>
              </DialogHeader>
              <div className="grid gap-4 py-4">
                <div className="grid gap-2">
                  <Label>Arquivo</Label>
                  <Input
                    type="file"
                    accept=".csv,.xlsx"
                    onChange={(e) => {
                      const file = e.target.files?.[0];
                      if (file) importarComandas(file);
                    }}
                  />
                </div>
                <div className="text-sm text-muted-foreground">
                  <p>Formato esperado:</p>
                  <ul className="list-disc list-inside">
                    <li>Número, Nome, CPF, Tipo, Valor Inicial</li>
                    <li>Máximo 1000 comandas por arquivo</li>
                  </ul>
                </div>
              </div>
              <DialogFooter>
                <Button variant="outline" onClick={() => setShowImportacao(false)}>
                  Cancelar
                </Button>
                <Button variant="outline">
                  <Download className="mr-2 h-4 w-4" />
                  Baixar Modelo
                </Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>
        </div>
      </div>

      {/* Cards de Estatísticas */}
      {estatisticas && (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-5">
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium">Total</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{estatisticas.total}</div>
              <p className="text-xs text-muted-foreground mt-1">Comandas cadastradas</p>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium">Ativas</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-green-600">{estatisticas.ativas}</div>
              <p className="text-xs text-muted-foreground mt-1">Em uso no momento</p>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium">Saldo Total</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">R$ {estatisticas.saldo_total.toLocaleString('pt-BR')}</div>
              <p className="text-xs text-muted-foreground mt-1">Em todas as comandas</p>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium">Ticket Médio</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">R$ {estatisticas.ticket_medio.toFixed(2)}</div>
              <p className="text-xs text-muted-foreground mt-1">Por comanda</p>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium">Com Consumo</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {((estatisticas.comandas_com_consumo / estatisticas.total) * 100).toFixed(0)}%
              </div>
              <p className="text-xs text-muted-foreground mt-1">
                {estatisticas.comandas_com_consumo} comandas
              </p>
            </CardContent>
          </Card>
        </div>
      )}

      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="gerenciar">Gerenciar Comandas</TabsTrigger>
          <TabsTrigger value="grupos">Grupos</TabsTrigger>
          <TabsTrigger value="pre-ativacao">Pré-Ativação</TabsTrigger>
          <TabsTrigger value="mapa">Mapa de Comandas</TabsTrigger>
        </TabsList>

        <TabsContent value="gerenciar" className="space-y-4">
          {/* Filtros Avançados */}
          <Card>
            <CardHeader>
              <CardTitle>Busca Avançada</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid gap-4 md:grid-cols-4">
                <div className="md:col-span-2">
                  <Label>Buscar por</Label>
                  <div className="flex gap-2">
                    <Select value={filtros.tipo_busca} onValueChange={(v) => setFiltros({...filtros, tipo_busca: v as any})}>
                      <SelectTrigger className="w-[140px]">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="todos">Todos</SelectItem>
                        <SelectItem value="cpf">CPF</SelectItem>
                        <SelectItem value="tag">TAG</SelectItem>
                        <SelectItem value="numero">Número</SelectItem>
                        <SelectItem value="nome">Nome</SelectItem>
                      </SelectContent>
                    </Select>
                    <Input
                      placeholder={`Digite o ${filtros.tipo_busca}...`}
                      value={filtros.busca}
                      onChange={(e) => {
                        setFiltros({...filtros, busca: e.target.value});
                        buscarComandas(e.target.value, filtros.tipo_busca);
                      }}
                      className="flex-1"
                    />
                  </div>
                </div>
                
                <div>
                  <Label>Período</Label>
                  <DatePickerWithRange
                    date={filtros.periodo}
                    onDateChange={(range) => setFiltros({...filtros, periodo: range})}
                  />
                </div>
                
                <div>
                  <Label>Caixa</Label>
                  <Select value={filtros.caixa} onValueChange={(v) => setFiltros({...filtros, caixa: v})}>
                    <SelectTrigger>
                      <SelectValue placeholder="Todos os caixas" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="">Todos</SelectItem>
                      <SelectItem value="1">Caixa 1</SelectItem>
                      <SelectItem value="2">Caixa 2</SelectItem>
                      <SelectItem value="3">Caixa 3</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
              
              <div className="flex flex-wrap gap-4">
                <div className="flex items-center space-x-2">
                  <Checkbox
                    id="ativas"
                    checked={filtros.apenas_ativas}
                    onCheckedChange={(checked) => setFiltros({...filtros, apenas_ativas: !!checked})}
                  />
                  <Label htmlFor="ativas">Apenas Ativas</Label>
                </div>
                
                <div className="flex items-center space-x-2">
                  <Checkbox
                    id="abertas"
                    checked={filtros.apenas_abertas}
                    onCheckedChange={(checked) => setFiltros({...filtros, apenas_abertas: !!checked})}
                  />
                  <Label htmlFor="abertas">Apenas Abertas</Label>
                </div>
                
                <div className="flex items-center space-x-2">
                  <Checkbox
                    id="bloqueadas"
                    checked={filtros.apenas_bloqueadas}
                    onCheckedChange={(checked) => setFiltros({...filtros, apenas_bloqueadas: !!checked})}
                  />
                  <Label htmlFor="bloqueadas">Apenas Bloqueadas</Label>
                </div>
                
                <div className="flex items-center space-x-2">
                  <Checkbox
                    id="com-consumo"
                    checked={filtros.com_consumo}
                    onCheckedChange={(checked) => setFiltros({...filtros, com_consumo: !!checked})}
                  />
                  <Label htmlFor="com-consumo">Com Consumo</Label>
                </div>
                
                <div className="flex items-center space-x-2">
                  <Checkbox
                    id="sem-consumo"
                    checked={filtros.sem_consumo}
                    onCheckedChange={(checked) => setFiltros({...filtros, sem_consumo: !!checked})}
                  />
                  <Label htmlFor="sem-consumo">Sem Consumo</Label>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Lista de Comandas */}
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {comandas.map(comanda => (
              <Card key={comanda.id} className="hover:shadow-lg transition-shadow">
                <CardHeader>
                  <div className="flex justify-between items-start">
                    <div>
                      <CardTitle className="text-lg flex items-center gap-2">
                        <span className="text-2xl">{getTipoIcon(comanda.tipo)}</span>
                        {comanda.numero_comanda}
                      </CardTitle>
                      <CardDescription>
                        {comanda.nome_cliente || 'Cliente não identificado'}
                      </CardDescription>
                    </div>
                    <Badge className={getStatusColor(comanda.status)}>
                      {comanda.status}
                    </Badge>
                  </div>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <p className="text-muted-foreground">Saldo Atual</p>
                      <p className="font-bold text-lg">R$ {comanda.saldo_atual.toFixed(2)}</p>
                    </div>
                    <div>
                      <p className="text-muted-foreground">Total Gasto</p>
                      <p className="font-bold">R$ {comanda.saldo_total_gasto.toFixed(2)}</p>
                    </div>
                  </div>
                  
                  {comanda.cpf_cliente && (
                    <div className="flex items-center gap-2 text-sm">
                      <UserCheck className="h-4 w-4 text-muted-foreground" />
                      <span>CPF: {comanda.cpf_cliente}</span>
                    </div>
                  )}
                  
                  {comanda.tag_numero && (
                    <div className="flex items-center gap-2 text-sm">
                      <Tag className="h-4 w-4 text-muted-foreground" />
                      <span>TAG: {comanda.tag_numero}</span>
                    </div>
                  )}
                  
                  {comanda.mesa_vinculada && (
                    <div className="flex items-center gap-2 text-sm">
                      <Hash className="h-4 w-4 text-muted-foreground" />
                      <span>Mesa: {comanda.mesa_vinculada}</span>
                    </div>
                  )}
                  
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-muted-foreground">Transações: {comanda.total_transacoes}</span>
                    {comanda.ultima_transacao && (
                      <span className="text-muted-foreground">
                        {formatDistanceToNow(new Date(comanda.ultima_transacao), { 
                          addSuffix: true, 
                          locale: ptBR 
                        })}
                      </span>
                    )}
                  </div>
                  
                  {comanda.saldo_bloqueado > 0 && (
                    <div className="flex items-center gap-2 text-sm text-red-600">
                      <Lock className="h-4 w-4" />
                      <span>Saldo bloqueado: R$ {comanda.saldo_bloqueado.toFixed(2)}</span>
                    </div>
                  )}
                  
                  {comanda.alertas && comanda.alertas.length > 0 && (
                    <div className="flex items-center gap-2 text-sm text-yellow-600">
                      <AlertCircle className="h-4 w-4" />
                      <span>{comanda.alertas.length} alertas</span>
                    </div>
                  )}
                </CardContent>
                <CardFooter className="flex gap-2">
                  <Button 
                    variant="outline" 
                    size="sm"
                    onClick={() => {
                      setSelectedComanda(comanda);
                      setShowDetalhes(true);
                    }}
                  >
                    Detalhes
                  </Button>
                  
                  {comanda.status === 'ATIVA' && (
                    <>
                      <Button 
                        variant="outline" 
                        size="sm"
                        onClick={() => {
                          setSelectedComanda(comanda);
                          setShowRecarga(true);
                        }}
                      >
                        <DollarSign className="mr-1 h-3 w-3" />
                        Recarregar
                      </Button>
                      
                      <Button 
                        variant="outline" 
                        size="sm"
                        onClick={() => {
                          setSelectedComanda(comanda);
                          setShowBloqueio(true);
                        }}
                      >
                        <Lock className="mr-1 h-3 w-3" />
                        Bloquear
                      </Button>
                    </>
                  )}
                  
                  {comanda.status === 'BLOQUEADA' && (
                    <Button 
                      variant="outline" 
                      size="sm"
                      onClick={() => desbloquearComanda(comanda.id)}
                    >
                      Desbloquear
                    </Button>
                  )}
                </CardFooter>
              </Card>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="grupos" className="space-y-4">
          <div className="flex justify-between items-center">
            <h2 className="text-xl font-semibold">Grupos de Comandas</h2>
            <Dialog open={showGrupo} onOpenChange={setShowGrupo}>
              <DialogTrigger asChild>
                <Button>
                  <Users className="mr-2 h-4 w-4" />
                  Criar Grupo
                </Button>
              </DialogTrigger>
              <DialogContent>
                <DialogHeader>
                  <DialogTitle>Criar Grupo de Comandas</DialogTitle>
                  <DialogDescription>
                    Agrupe comandas para gerenciamento conjunto
                  </DialogDescription>
                </DialogHeader>
                <div className="grid gap-4 py-4">
                  <div className="grid gap-2">
                    <Label>Nome do Grupo</Label>
                    <Input
                      value={novoGrupo.nome}
                      onChange={(e) => setNovoGrupo({...novoGrupo, nome: e.target.value})}
                      placeholder="Ex: Mesa 10, Família Silva"
                    />
                  </div>
                  <div className="grid gap-2">
                    <Label>Descrição</Label>
                    <Textarea
                      value={novoGrupo.descricao}
                      onChange={(e) => setNovoGrupo({...novoGrupo, descricao: e.target.value})}
                      placeholder="Descrição opcional"
                    />
                  </div>
                </div>
                <DialogFooter>
                  <Button variant="outline" onClick={() => setShowGrupo(false)}>
                    Cancelar
                  </Button>
                  <Button onClick={criarGrupo}>Criar Grupo</Button>
                </DialogFooter>
              </DialogContent>
            </Dialog>
          </div>
          
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {grupos.map(grupo => (
              <Card key={grupo.id}>
                <CardHeader>
                  <CardTitle>{grupo.nome}</CardTitle>
                  <CardDescription>{grupo.descricao}</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span>Total de comandas:</span>
                      <span className="font-medium">{grupo.total_comandas}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Comandas ativas:</span>
                      <span className="font-medium">{grupo.comandas_ativas}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Saldo total:</span>
                      <span className="font-bold">R$ {grupo.saldo_total.toFixed(2)}</span>
                    </div>
                  </div>
                </CardContent>
                <CardFooter>
                  <Button variant="outline" size="sm" className="w-full">
                    Gerenciar Grupo
                  </Button>
                </CardFooter>
              </Card>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="pre-ativacao" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Pré-Ativação de Comandas</CardTitle>
              <CardDescription>
                Prepare comandas antecipadamente para agilizar o atendimento
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="grid gap-4 md:grid-cols-3">
                  <div>
                    <Label>Quantidade</Label>
                    <Input type="number" placeholder="Ex: 100" />
                  </div>
                  <div>
                    <Label>Tipo</Label>
                    <Select>
                      <SelectTrigger>
                        <SelectValue placeholder="Selecione o tipo" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="FISICA">Física</SelectItem>
                        <SelectItem value="VIRTUAL">Virtual</SelectItem>
                        <SelectItem value="RFID">RFID</SelectItem>
                        <SelectItem value="NFC">NFC</SelectItem>
                        <SelectItem value="TAG">TAG</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div>
                    <Label>Valor Inicial</Label>
                    <Input type="number" placeholder="R$ 0,00" />
                  </div>
                </div>
                
                <Button className="w-full">
                  Pré-Ativar Comandas
                </Button>
              </div>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader>
              <CardTitle>Comandas Pré-Ativadas</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {comandas.filter(c => c.pre_ativada).map(comanda => (
                  <div key={comanda.id} className="flex items-center justify-between p-3 border rounded">
                    <div className="flex items-center gap-3">
                      <span className="text-xl">{getTipoIcon(comanda.tipo)}</span>
                      <div>
                        <p className="font-medium">{comanda.numero_comanda}</p>
                        <p className="text-sm text-muted-foreground">
                          Pré-ativada em {format(new Date(comanda.data_pre_ativacao!), 'dd/MM/yyyy HH:mm')}
                        </p>
                      </div>
                    </div>
                    <Button size="sm" variant="outline">
                      Ativar Agora
                    </Button>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="mapa" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Mapa de Comandas em Tempo Real</CardTitle>
              <CardDescription>
                Visualização completa de todas as comandas ativas - Total: {comandas.filter(c => c.status === 'ATIVA').length} comandas
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-6 md:grid-cols-10 lg:grid-cols-15 gap-2">
                {comandas.filter(c => c.status === 'ATIVA').map(comanda => (
                  <div
                    key={comanda.id}
                    className={`
                      p-2 rounded text-center cursor-pointer transition-all hover:scale-105
                      ${comanda.saldo_atual > 100 ? 'bg-green-100' : 
                        comanda.saldo_atual > 50 ? 'bg-yellow-100' : 
                        comanda.saldo_atual > 0 ? 'bg-orange-100' : 'bg-gray-100'}
                    `}
                    title={`${comanda.nome_cliente || 'Sem nome'} - R$ ${comanda.saldo_atual.toFixed(2)}`}
                  >
                    <div className="text-xs font-bold">{comanda.numero_comanda}</div>
                    <div className="text-xs">R$ {comanda.saldo_atual.toFixed(0)}</div>
                  </div>
                ))}
              </div>
              
              <div className="flex gap-4 mt-4 text-sm">
                <div className="flex items-center gap-2">
                  <div className="w-4 h-4 bg-green-100 rounded"></div>
                  <span>Saldo Alto (&gt; R$ 100)</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-4 h-4 bg-yellow-100 rounded"></div>
                  <span>Saldo Médio (R$ 50-100)</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-4 h-4 bg-orange-100 rounded"></div>
                  <span>Saldo Baixo (&lt; R$ 50)</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-4 h-4 bg-gray-100 rounded"></div>
                  <span>Sem Saldo</span>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Modal de Recarga */}
      <Dialog open={showRecarga} onOpenChange={setShowRecarga}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Recarregar Comanda</DialogTitle>
            <DialogDescription>
              Comanda: {selectedComanda?.numero_comanda} - {selectedComanda?.nome_cliente}
            </DialogDescription>
          </DialogHeader>
          <div className="grid gap-4 py-4">
            <div className="grid gap-2">
              <Label>Valor da Recarga</Label>
              <Input
                type="number"
                value={novaRecarga.valor}
                onChange={(e) => setNovaRecarga({...novaRecarga, valor: parseFloat(e.target.value)})}
                placeholder="R$ 0,00"
              />
            </div>
            <div className="grid gap-2">
              <Label>Forma de Pagamento</Label>
              <Select 
                value={novaRecarga.forma_pagamento}
                onValueChange={(v) => setNovaRecarga({...novaRecarga, forma_pagamento: v})}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="PIX">PIX</SelectItem>
                  <SelectItem value="DINHEIRO">Dinheiro</SelectItem>
                  <SelectItem value="CARTAO_CREDITO">Cartão de Crédito</SelectItem>
                  <SelectItem value="CARTAO_DEBITO">Cartão de Débito</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="grid gap-2">
              <Label>Observação</Label>
              <Textarea
                value={novaRecarga.observacao}
                onChange={(e) => setNovaRecarga({...novaRecarga, observacao: e.target.value})}
                placeholder="Observação opcional"
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowRecarga(false)}>
              Cancelar
            </Button>
            <Button onClick={recarregarComanda}>
              Confirmar Recarga
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Modal de Bloqueio */}
      <Dialog open={showBloqueio} onOpenChange={setShowBloqueio}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Bloquear Comanda</DialogTitle>
            <DialogDescription>
              Comanda: {selectedComanda?.numero_comanda} - {selectedComanda?.nome_cliente}
            </DialogDescription>
          </DialogHeader>
          <div className="grid gap-4 py-4">
            <div className="grid gap-2">
              <Label>Motivo do Bloqueio</Label>
              <Textarea
                value={novoBloqueio.motivo}
                onChange={(e) => setNovoBloqueio({...novoBloqueio, motivo: e.target.value})}
                placeholder="Descreva o motivo do bloqueio"
                required
              />
            </div>
            <div className="grid gap-2">
              <Label>Tipo de Bloqueio</Label>
              <Select 
                value={novoBloqueio.tipo}
                onValueChange={(v) => setNovoBloqueio({...novoBloqueio, tipo: v})}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="temporario">Temporário</SelectItem>
                  <SelectItem value="permanente">Permanente</SelectItem>
                  <SelectItem value="investigacao">Sob Investigação</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="flex items-center space-x-2">
              <Switch
                id="notificar"
                checked={novoBloqueio.notificar_cliente}
                onCheckedChange={(checked) => setNovoBloqueio({...novoBloqueio, notificar_cliente: checked})}
              />
              <Label htmlFor="notificar">Notificar cliente</Label>
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowBloqueio(false)}>
              Cancelar
            </Button>
            <Button variant="destructive" onClick={bloquearComanda}>
              Confirmar Bloqueio
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}

// Função de debounce
function debounce<T extends (...args: any[]) => any>(
  func: T,
  wait: number
): (...args: Parameters<T>) => void {
  let timeout: NodeJS.Timeout | null = null;
  
  return function(...args: Parameters<T>) {
    if (timeout) clearTimeout(timeout);
    timeout = setTimeout(() => func(...args), wait);
  };
}