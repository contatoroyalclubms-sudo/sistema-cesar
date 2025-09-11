import React, { useState, useEffect } from 'react';
import { Plus, Play, Pause, Edit, Trash2, Clock, CheckCircle, XCircle, GitBranch, Zap, Activity, AlertCircle } from 'lucide-react';
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
import { formatDistanceToNow } from 'date-fns';
import { ptBR } from 'date-fns/locale';

interface FluxoTrabalho {
  id: number;
  nome: string;
  descricao?: string;
  trigger_tipo: 'manual' | 'agendado' | 'evento' | 'webhook';
  configuracao: Record<string, any>;
  ativo: boolean;
  criado_em: string;
  atualizado_em: string;
  execucoes?: ExecucaoFluxo[];
}

interface ExecucaoFluxo {
  id: number;
  fluxo_id: number;
  status: 'em_execucao' | 'concluido' | 'erro' | 'cancelado';
  resultado?: Record<string, any>;
  erro?: string;
  iniciado_em: string;
  finalizado_em?: string;
  fluxo?: FluxoTrabalho;
}

interface Automacao {
  id: number;
  nome: string;
  tipo: 'email' | 'whatsapp' | 'sms' | 'webhook' | 'script';
  trigger: string;
  configuracao: Record<string, any>;
  ativo: boolean;
  ultima_execucao?: string;
  proxima_execucao?: string;
  execucoes_total: number;
  execucoes_sucesso: number;
  execucoes_erro: number;
}

export default function AutomacaoModule() {
  const [fluxos, setFluxos] = useState<FluxoTrabalho[]>([]);
  const [automacoes, setAutomacoes] = useState<Automacao[]>([]);
  const [execucoes, setExecucoes] = useState<ExecucaoFluxo[]>([]);
  const [loading, setLoading] = useState(true);
  const [showNovoFluxo, setShowNovoFluxo] = useState(false);
  const [showNovaAutomacao, setShowNovaAutomacao] = useState(false);
  const [activeTab, setActiveTab] = useState('fluxos');
  const [filtroStatus, setFiltroStatus] = useState<string>('todos');
  const [busca, setBusca] = useState('');

  const [novoFluxo, setNovoFluxo] = useState({
    nome: '',
    descricao: '',
    trigger_tipo: 'manual' as const,
    configuracao: {},
    ativo: true
  });

  const [novaAutomacao, setNovaAutomacao] = useState({
    nome: '',
    tipo: 'email' as const,
    trigger: '',
    configuracao: {},
    ativo: true
  });

  useEffect(() => {
    carregarDados();
  }, [activeTab]);

  const carregarDados = async () => {
    setLoading(true);
    try {
      if (activeTab === 'fluxos') {
        const response = await api.get('/api/automacao/fluxos');
        setFluxos(response.data);
      } else if (activeTab === 'automacoes') {
        const response = await api.get('/api/automacao/automacoes');
        setAutomacoes(response.data);
      } else if (activeTab === 'execucoes') {
        const response = await api.get('/api/automacao/execucoes');
        setExecucoes(response.data);
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

  const criarFluxo = async () => {
    try {
      await api.post('/api/automacao/fluxos', novoFluxo);
      toast({
        title: "Sucesso",
        description: "Fluxo de trabalho criado com sucesso"
      });
      setShowNovoFluxo(false);
      setNovoFluxo({
        nome: '',
        descricao: '',
        trigger_tipo: 'manual',
        configuracao: {},
        ativo: true
      });
      carregarDados();
    } catch (error) {
      console.error('Erro ao criar fluxo:', error);
      toast({
        title: "Erro",
        description: "Não foi possível criar o fluxo",
        variant: "destructive"
      });
    }
  };

  const criarAutomacao = async () => {
    try {
      await api.post('/api/automacao/automacoes', novaAutomacao);
      toast({
        title: "Sucesso",
        description: "Automação criada com sucesso"
      });
      setShowNovaAutomacao(false);
      setNovaAutomacao({
        nome: '',
        tipo: 'email',
        trigger: '',
        configuracao: {},
        ativo: true
      });
      carregarDados();
    } catch (error) {
      console.error('Erro ao criar automação:', error);
      toast({
        title: "Erro",
        description: "Não foi possível criar a automação",
        variant: "destructive"
      });
    }
  };

  const executarFluxo = async (fluxoId: number) => {
    try {
      await api.post(`/api/automacao/fluxos/${fluxoId}/executar`);
      toast({
        title: "Sucesso",
        description: "Fluxo iniciado com sucesso"
      });
      carregarDados();
    } catch (error) {
      console.error('Erro ao executar fluxo:', error);
      toast({
        title: "Erro",
        description: "Não foi possível executar o fluxo",
        variant: "destructive"
      });
    }
  };

  const alternarFluxo = async (fluxoId: number, ativo: boolean) => {
    try {
      await api.patch(`/api/automacao/fluxos/${fluxoId}`, { ativo });
      toast({
        title: "Sucesso",
        description: `Fluxo ${ativo ? 'ativado' : 'desativado'} com sucesso`
      });
      carregarDados();
    } catch (error) {
      console.error('Erro ao alterar fluxo:', error);
      toast({
        title: "Erro",
        description: "Não foi possível alterar o status do fluxo",
        variant: "destructive"
      });
    }
  };

  const alternarAutomacao = async (automacaoId: number, ativo: boolean) => {
    try {
      await api.patch(`/api/automacao/automacoes/${automacaoId}`, { ativo });
      toast({
        title: "Sucesso",
        description: `Automação ${ativo ? 'ativada' : 'desativada'} com sucesso`
      });
      carregarDados();
    } catch (error) {
      console.error('Erro ao alterar automação:', error);
      toast({
        title: "Erro",
        description: "Não foi possível alterar o status da automação",
        variant: "destructive"
      });
    }
  };

  const deletarFluxo = async (fluxoId: number) => {
    if (!confirm('Tem certeza que deseja excluir este fluxo?')) return;
    
    try {
      await api.delete(`/api/automacao/fluxos/${fluxoId}`);
      toast({
        title: "Sucesso",
        description: "Fluxo excluído com sucesso"
      });
      carregarDados();
    } catch (error) {
      console.error('Erro ao deletar fluxo:', error);
      toast({
        title: "Erro",
        description: "Não foi possível excluir o fluxo",
        variant: "destructive"
      });
    }
  };

  const deletarAutomacao = async (automacaoId: number) => {
    if (!confirm('Tem certeza que deseja excluir esta automação?')) return;
    
    try {
      await api.delete(`/api/automacao/automacoes/${automacaoId}`);
      toast({
        title: "Sucesso",
        description: "Automação excluída com sucesso"
      });
      carregarDados();
    } catch (error) {
      console.error('Erro ao deletar automação:', error);
      toast({
        title: "Erro",
        description: "Não foi possível excluir a automação",
        variant: "destructive"
      });
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'em_execucao':
        return <Clock className="h-4 w-4 text-blue-500" />;
      case 'concluido':
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'erro':
        return <XCircle className="h-4 w-4 text-red-500" />;
      case 'cancelado':
        return <AlertCircle className="h-4 w-4 text-yellow-500" />;
      default:
        return null;
    }
  };

  const getTriggerBadgeColor = (trigger: string) => {
    switch (trigger) {
      case 'manual':
        return 'default';
      case 'agendado':
        return 'secondary';
      case 'evento':
        return 'outline';
      case 'webhook':
        return 'destructive';
      default:
        return 'default';
    }
  };

  return (
    <div className="container mx-auto py-6 space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">Automação</h1>
          <p className="text-muted-foreground">Gerencie fluxos de trabalho e automações</p>
        </div>
        <div className="flex gap-2">
          <Dialog open={showNovoFluxo} onOpenChange={setShowNovoFluxo}>
            <DialogTrigger asChild>
              <Button>
                <GitBranch className="mr-2 h-4 w-4" />
                Novo Fluxo
              </Button>
            </DialogTrigger>
            <DialogContent className="sm:max-w-[500px]">
              <DialogHeader>
                <DialogTitle>Criar Fluxo de Trabalho</DialogTitle>
                <DialogDescription>
                  Configure um novo fluxo automatizado
                </DialogDescription>
              </DialogHeader>
              <div className="grid gap-4 py-4">
                <div className="grid gap-2">
                  <Label htmlFor="nome">Nome</Label>
                  <Input
                    id="nome"
                    value={novoFluxo.nome}
                    onChange={(e) => setNovoFluxo({...novoFluxo, nome: e.target.value})}
                    placeholder="Ex: Boas-vindas a novos clientes"
                  />
                </div>
                <div className="grid gap-2">
                  <Label htmlFor="descricao">Descrição</Label>
                  <Textarea
                    id="descricao"
                    value={novoFluxo.descricao}
                    onChange={(e) => setNovoFluxo({...novoFluxo, descricao: e.target.value})}
                    placeholder="Descreva o que este fluxo faz"
                  />
                </div>
                <div className="grid gap-2">
                  <Label htmlFor="trigger">Tipo de Trigger</Label>
                  <Select
                    value={novoFluxo.trigger_tipo}
                    onValueChange={(value: any) => setNovoFluxo({...novoFluxo, trigger_tipo: value})}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="manual">Manual</SelectItem>
                      <SelectItem value="agendado">Agendado</SelectItem>
                      <SelectItem value="evento">Evento</SelectItem>
                      <SelectItem value="webhook">Webhook</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="flex items-center space-x-2">
                  <Switch
                    id="ativo"
                    checked={novoFluxo.ativo}
                    onCheckedChange={(checked) => setNovoFluxo({...novoFluxo, ativo: checked})}
                  />
                  <Label htmlFor="ativo">Ativar imediatamente</Label>
                </div>
              </div>
              <DialogFooter>
                <Button variant="outline" onClick={() => setShowNovoFluxo(false)}>
                  Cancelar
                </Button>
                <Button onClick={criarFluxo}>Criar Fluxo</Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>

          <Dialog open={showNovaAutomacao} onOpenChange={setShowNovaAutomacao}>
            <DialogTrigger asChild>
              <Button variant="outline">
                <Zap className="mr-2 h-4 w-4" />
                Nova Automação
              </Button>
            </DialogTrigger>
            <DialogContent className="sm:max-w-[500px]">
              <DialogHeader>
                <DialogTitle>Criar Automação</DialogTitle>
                <DialogDescription>
                  Configure uma nova automação
                </DialogDescription>
              </DialogHeader>
              <div className="grid gap-4 py-4">
                <div className="grid gap-2">
                  <Label htmlFor="nome-auto">Nome</Label>
                  <Input
                    id="nome-auto"
                    value={novaAutomacao.nome}
                    onChange={(e) => setNovaAutomacao({...novaAutomacao, nome: e.target.value})}
                    placeholder="Ex: Email de confirmação"
                  />
                </div>
                <div className="grid gap-2">
                  <Label htmlFor="tipo">Tipo</Label>
                  <Select
                    value={novaAutomacao.tipo}
                    onValueChange={(value: any) => setNovaAutomacao({...novaAutomacao, tipo: value})}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="email">Email</SelectItem>
                      <SelectItem value="whatsapp">WhatsApp</SelectItem>
                      <SelectItem value="sms">SMS</SelectItem>
                      <SelectItem value="webhook">Webhook</SelectItem>
                      <SelectItem value="script">Script</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="grid gap-2">
                  <Label htmlFor="trigger-auto">Trigger</Label>
                  <Input
                    id="trigger-auto"
                    value={novaAutomacao.trigger}
                    onChange={(e) => setNovaAutomacao({...novaAutomacao, trigger: e.target.value})}
                    placeholder="Ex: novo_cadastro, compra_aprovada"
                  />
                </div>
                <div className="flex items-center space-x-2">
                  <Switch
                    id="ativo-auto"
                    checked={novaAutomacao.ativo}
                    onCheckedChange={(checked) => setNovaAutomacao({...novaAutomacao, ativo: checked})}
                  />
                  <Label htmlFor="ativo-auto">Ativar imediatamente</Label>
                </div>
              </div>
              <DialogFooter>
                <Button variant="outline" onClick={() => setShowNovaAutomacao(false)}>
                  Cancelar
                </Button>
                <Button onClick={criarAutomacao}>Criar Automação</Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>
        </div>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="fluxos">Fluxos de Trabalho</TabsTrigger>
          <TabsTrigger value="automacoes">Automações</TabsTrigger>
          <TabsTrigger value="execucoes">Histórico de Execuções</TabsTrigger>
        </TabsList>

        <TabsContent value="fluxos" className="space-y-4">
          <div className="flex gap-4 items-center">
            <Input
              placeholder="Buscar fluxos..."
              value={busca}
              onChange={(e) => setBusca(e.target.value)}
              className="max-w-sm"
            />
            <Select value={filtroStatus} onValueChange={setFiltroStatus}>
              <SelectTrigger className="w-[180px]">
                <SelectValue placeholder="Filtrar por status" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="todos">Todos</SelectItem>
                <SelectItem value="ativos">Ativos</SelectItem>
                <SelectItem value="inativos">Inativos</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {fluxos
              .filter(fluxo => 
                fluxo.nome.toLowerCase().includes(busca.toLowerCase()) &&
                (filtroStatus === 'todos' || 
                 (filtroStatus === 'ativos' && fluxo.ativo) ||
                 (filtroStatus === 'inativos' && !fluxo.ativo))
              )
              .map(fluxo => (
                <Card key={fluxo.id}>
                  <CardHeader>
                    <div className="flex justify-between items-start">
                      <div className="space-y-1">
                        <CardTitle className="text-lg">{fluxo.nome}</CardTitle>
                        <div className="flex gap-2">
                          <Badge variant={getTriggerBadgeColor(fluxo.trigger_tipo)}>
                            {fluxo.trigger_tipo}
                          </Badge>
                          {fluxo.ativo ? (
                            <Badge className="bg-green-100 text-green-800">Ativo</Badge>
                          ) : (
                            <Badge variant="secondary">Inativo</Badge>
                          )}
                        </div>
                      </div>
                      <Switch
                        checked={fluxo.ativo}
                        onCheckedChange={(checked) => alternarFluxo(fluxo.id, checked)}
                      />
                    </div>
                    {fluxo.descricao && (
                      <CardDescription>{fluxo.descricao}</CardDescription>
                    )}
                  </CardHeader>
                  <CardContent>
                    <div className="text-sm text-muted-foreground">
                      Criado {formatDistanceToNow(new Date(fluxo.criado_em), { addSuffix: true, locale: ptBR })}
                    </div>
                  </CardContent>
                  <CardFooter className="flex justify-between">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => executarFluxo(fluxo.id)}
                      disabled={!fluxo.ativo}
                    >
                      <Play className="mr-1 h-3 w-3" />
                      Executar
                    </Button>
                    <div className="flex gap-1">
                      <Button variant="ghost" size="icon">
                        <Edit className="h-4 w-4" />
                      </Button>
                      <Button 
                        variant="ghost" 
                        size="icon"
                        onClick={() => deletarFluxo(fluxo.id)}
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                  </CardFooter>
                </Card>
              ))}
          </div>
        </TabsContent>

        <TabsContent value="automacoes" className="space-y-4">
          <div className="flex gap-4 items-center">
            <Input
              placeholder="Buscar automações..."
              value={busca}
              onChange={(e) => setBusca(e.target.value)}
              className="max-w-sm"
            />
            <Select value={filtroStatus} onValueChange={setFiltroStatus}>
              <SelectTrigger className="w-[180px]">
                <SelectValue placeholder="Filtrar por status" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="todos">Todas</SelectItem>
                <SelectItem value="ativas">Ativas</SelectItem>
                <SelectItem value="inativas">Inativas</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {automacoes
              .filter(auto => 
                auto.nome.toLowerCase().includes(busca.toLowerCase()) &&
                (filtroStatus === 'todos' || 
                 (filtroStatus === 'ativas' && auto.ativo) ||
                 (filtroStatus === 'inativas' && !auto.ativo))
              )
              .map(auto => (
                <Card key={auto.id}>
                  <CardHeader>
                    <div className="flex justify-between items-start">
                      <div className="space-y-1">
                        <CardTitle className="text-lg">{auto.nome}</CardTitle>
                        <div className="flex gap-2">
                          <Badge>{auto.tipo}</Badge>
                          {auto.ativo ? (
                            <Badge className="bg-green-100 text-green-800">Ativa</Badge>
                          ) : (
                            <Badge variant="secondary">Inativa</Badge>
                          )}
                        </div>
                      </div>
                      <Switch
                        checked={auto.ativo}
                        onCheckedChange={(checked) => alternarAutomacao(auto.id, checked)}
                      />
                    </div>
                    <CardDescription>Trigger: {auto.trigger}</CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span className="text-muted-foreground">Total execuções:</span>
                      <span className="font-medium">{auto.execucoes_total}</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-muted-foreground">Sucesso:</span>
                      <span className="font-medium text-green-600">{auto.execucoes_sucesso}</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-muted-foreground">Erros:</span>
                      <span className="font-medium text-red-600">{auto.execucoes_erro}</span>
                    </div>
                    {auto.ultima_execucao && (
                      <div className="text-xs text-muted-foreground pt-2">
                        Última execução: {formatDistanceToNow(new Date(auto.ultima_execucao), { addSuffix: true, locale: ptBR })}
                      </div>
                    )}
                  </CardContent>
                  <CardFooter className="flex justify-between">
                    <Button variant="outline" size="sm">
                      <Activity className="mr-1 h-3 w-3" />
                      Logs
                    </Button>
                    <div className="flex gap-1">
                      <Button variant="ghost" size="icon">
                        <Edit className="h-4 w-4" />
                      </Button>
                      <Button 
                        variant="ghost" 
                        size="icon"
                        onClick={() => deletarAutomacao(auto.id)}
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                  </CardFooter>
                </Card>
              ))}
          </div>
        </TabsContent>

        <TabsContent value="execucoes" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Histórico de Execuções</CardTitle>
              <CardDescription>
                Acompanhe todas as execuções de fluxos e automações
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {execucoes.map(exec => (
                  <div key={exec.id} className="flex items-center justify-between p-3 border rounded-lg">
                    <div className="flex items-center gap-3">
                      {getStatusIcon(exec.status)}
                      <div>
                        <p className="font-medium">{exec.fluxo?.nome || `Execução #${exec.id}`}</p>
                        <p className="text-sm text-muted-foreground">
                          Iniciado {formatDistanceToNow(new Date(exec.iniciado_em), { addSuffix: true, locale: ptBR })}
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <Badge variant={
                        exec.status === 'concluido' ? 'default' :
                        exec.status === 'erro' ? 'destructive' :
                        exec.status === 'em_execucao' ? 'secondary' :
                        'outline'
                      }>
                        {exec.status.replace('_', ' ')}
                      </Badge>
                      {exec.erro && (
                        <Button variant="ghost" size="sm">
                          Ver erro
                        </Button>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}