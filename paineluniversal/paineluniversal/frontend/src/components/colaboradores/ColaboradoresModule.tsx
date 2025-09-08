import React, { useState, useEffect } from 'react';
import { Users, UserPlus, Calendar, Clock, Shield, Award, Briefcase, Mail, Phone, Edit, Trash2, CheckCircle, XCircle, AlertCircle, UserCheck } from 'lucide-react';
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
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { toast } from '@/hooks/use-toast';
import api from '@/utils/api';
import { format, addDays, startOfWeek, endOfWeek } from 'date-fns';
import { ptBR } from 'date-fns/locale';

interface Colaborador {
  id: number;
  nome: string;
  email: string;
  telefone: string;
  cpf: string;
  cargo: string;
  departamento: string;
  tipo: 'funcionario' | 'freelancer' | 'voluntario';
  status: 'ativo' | 'inativo' | 'ferias' | 'afastado';
  data_admissao: string;
  salario?: number;
  comissao_percentual?: number;
  foto?: string;
  habilidades: string[];
  certificacoes: string[];
  eventos_trabalhados: number;
  avaliacao_media: number;
  criado_em: string;
}

interface EscalaTrabalho {
  id: number;
  colaborador_id: number;
  evento_id: number;
  data_inicio: string;
  data_fim: string;
  turno: 'manha' | 'tarde' | 'noite' | 'integral';
  funcao: string;
  local?: string;
  observacoes?: string;
  status: 'confirmado' | 'pendente' | 'cancelado';
  colaborador?: Colaborador;
  evento?: {
    nome: string;
    local: string;
  };
}

interface TarefaColaborador {
  id: number;
  colaborador_id: number;
  titulo: string;
  descricao?: string;
  prioridade: 'baixa' | 'media' | 'alta' | 'urgente';
  status: 'pendente' | 'em_andamento' | 'concluida' | 'cancelada';
  prazo?: string;
  data_conclusao?: string;
  colaborador?: Colaborador;
}

interface Departamento {
  nome: string;
  colaboradores: number;
  responsavel?: string;
}

interface EstatisticasColaboradores {
  total_ativos: number;
  total_inativos: number;
  total_escalados: number;
  tarefas_pendentes: number;
  tarefas_concluidas: number;
  custo_mensal: number;
  departamentos: Departamento[];
}

export default function ColaboradoresModule() {
  const [colaboradores, setColaboradores] = useState<Colaborador[]>([]);
  const [escalas, setEscalas] = useState<EscalaTrabalho[]>([]);
  const [tarefas, setTarefas] = useState<TarefaColaborador[]>([]);
  const [estatisticas, setEstatisticas] = useState<EstatisticasColaboradores | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('colaboradores');
  const [showNovoColaborador, setShowNovoColaborador] = useState(false);
  const [showNovaEscala, setShowNovaEscala] = useState(false);
  const [showNovaTarefa, setShowNovaTarefa] = useState(false);
  const [selectedColaborador, setSelectedColaborador] = useState<Colaborador | null>(null);
  const [filtroStatus, setFiltroStatus] = useState('todos');
  const [busca, setBusca] = useState('');

  const [novoColaborador, setNovoColaborador] = useState({
    nome: '',
    email: '',
    telefone: '',
    cpf: '',
    cargo: '',
    departamento: '',
    tipo: 'funcionario' as const,
    status: 'ativo' as const,
    data_admissao: format(new Date(), 'yyyy-MM-dd'),
    salario: 0,
    comissao_percentual: 0,
    habilidades: [] as string[],
    certificacoes: [] as string[]
  });

  const [novaEscala, setNovaEscala] = useState({
    colaborador_id: 0,
    evento_id: 0,
    data_inicio: '',
    data_fim: '',
    turno: 'integral' as const,
    funcao: '',
    local: '',
    observacoes: '',
    status: 'confirmado' as const
  });

  const [novaTarefa, setNovaTarefa] = useState({
    colaborador_id: 0,
    titulo: '',
    descricao: '',
    prioridade: 'media' as const,
    status: 'pendente' as const,
    prazo: ''
  });

  useEffect(() => {
    carregarDados();
  }, [activeTab]);

  const carregarDados = async () => {
    setLoading(true);
    try {
      if (activeTab === 'colaboradores') {
        const [colaboradoresRes, estatisticasRes] = await Promise.all([
          api.get('/api/colaboradores'),
          api.get('/api/colaboradores/estatisticas')
        ]);
        setColaboradores(colaboradoresRes.data);
        setEstatisticas(estatisticasRes.data);
      } else if (activeTab === 'escala') {
        const response = await api.get('/api/colaboradores/escalas');
        setEscalas(response.data);
      } else if (activeTab === 'tarefas') {
        const response = await api.get('/api/colaboradores/tarefas');
        setTarefas(response.data);
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

  const criarColaborador = async () => {
    try {
      await api.post('/api/colaboradores', novoColaborador);
      toast({
        title: "Sucesso",
        description: "Colaborador cadastrado com sucesso"
      });
      setShowNovoColaborador(false);
      setNovoColaborador({
        nome: '',
        email: '',
        telefone: '',
        cpf: '',
        cargo: '',
        departamento: '',
        tipo: 'funcionario',
        status: 'ativo',
        data_admissao: format(new Date(), 'yyyy-MM-dd'),
        salario: 0,
        comissao_percentual: 0,
        habilidades: [],
        certificacoes: []
      });
      carregarDados();
    } catch (error) {
      console.error('Erro ao criar colaborador:', error);
      toast({
        title: "Erro",
        description: "Não foi possível cadastrar o colaborador",
        variant: "destructive"
      });
    }
  };

  const criarEscala = async () => {
    try {
      await api.post('/api/colaboradores/escalas', novaEscala);
      toast({
        title: "Sucesso",
        description: "Escala criada com sucesso"
      });
      setShowNovaEscala(false);
      setNovaEscala({
        colaborador_id: 0,
        evento_id: 0,
        data_inicio: '',
        data_fim: '',
        turno: 'integral',
        funcao: '',
        local: '',
        observacoes: '',
        status: 'confirmado'
      });
      carregarDados();
    } catch (error) {
      console.error('Erro ao criar escala:', error);
      toast({
        title: "Erro",
        description: "Não foi possível criar a escala",
        variant: "destructive"
      });
    }
  };

  const criarTarefa = async () => {
    try {
      await api.post('/api/colaboradores/tarefas', novaTarefa);
      toast({
        title: "Sucesso",
        description: "Tarefa criada com sucesso"
      });
      setShowNovaTarefa(false);
      setNovaTarefa({
        colaborador_id: 0,
        titulo: '',
        descricao: '',
        prioridade: 'media',
        status: 'pendente',
        prazo: ''
      });
      carregarDados();
    } catch (error) {
      console.error('Erro ao criar tarefa:', error);
      toast({
        title: "Erro",
        description: "Não foi possível criar a tarefa",
        variant: "destructive"
      });
    }
  };

  const atualizarStatusColaborador = async (colaboradorId: number, status: string) => {
    try {
      await api.patch(`/api/colaboradores/${colaboradorId}`, { status });
      toast({
        title: "Sucesso",
        description: "Status atualizado com sucesso"
      });
      carregarDados();
    } catch (error) {
      console.error('Erro ao atualizar status:', error);
      toast({
        title: "Erro",
        description: "Não foi possível atualizar o status",
        variant: "destructive"
      });
    }
  };

  const atualizarStatusTarefa = async (tarefaId: number, status: string) => {
    try {
      await api.patch(`/api/colaboradores/tarefas/${tarefaId}`, { status });
      toast({
        title: "Sucesso",
        description: "Tarefa atualizada com sucesso"
      });
      carregarDados();
    } catch (error) {
      console.error('Erro ao atualizar tarefa:', error);
      toast({
        title: "Erro",
        description: "Não foi possível atualizar a tarefa",
        variant: "destructive"
      });
    }
  };

  const deletarColaborador = async (colaboradorId: number) => {
    if (!confirm('Tem certeza que deseja excluir este colaborador?')) return;
    
    try {
      await api.delete(`/api/colaboradores/${colaboradorId}`);
      toast({
        title: "Sucesso",
        description: "Colaborador excluído com sucesso"
      });
      carregarDados();
    } catch (error) {
      console.error('Erro ao deletar colaborador:', error);
      toast({
        title: "Erro",
        description: "Não foi possível excluir o colaborador",
        variant: "destructive"
      });
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'ativo':
      case 'confirmado':
      case 'concluida':
        return 'bg-green-100 text-green-800';
      case 'inativo':
      case 'cancelado':
      case 'cancelada':
        return 'bg-red-100 text-red-800';
      case 'ferias':
      case 'pendente':
        return 'bg-yellow-100 text-yellow-800';
      case 'afastado':
      case 'em_andamento':
        return 'bg-blue-100 text-blue-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getPrioridadeColor = (prioridade: string) => {
    switch (prioridade) {
      case 'urgente':
        return 'destructive';
      case 'alta':
        return 'default';
      case 'media':
        return 'secondary';
      case 'baixa':
        return 'outline';
      default:
        return 'outline';
    }
  };

  const getTurnoIcon = (turno: string) => {
    switch (turno) {
      case 'manha':
        return '🌅';
      case 'tarde':
        return '☀️';
      case 'noite':
        return '🌙';
      case 'integral':
        return '📅';
      default:
        return '📅';
    }
  };

  return (
    <div className="container mx-auto py-6 space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">Gestão de Colaboradores</h1>
          <p className="text-muted-foreground">Gerencie sua equipe e escalas de trabalho</p>
        </div>
        <div className="flex gap-2">
          <Dialog open={showNovoColaborador} onOpenChange={setShowNovoColaborador}>
            <DialogTrigger asChild>
              <Button>
                <UserPlus className="mr-2 h-4 w-4" />
                Novo Colaborador
              </Button>
            </DialogTrigger>
            <DialogContent className="sm:max-w-[600px]">
              <DialogHeader>
                <DialogTitle>Cadastrar Colaborador</DialogTitle>
                <DialogDescription>
                  Adicione um novo membro à equipe
                </DialogDescription>
              </DialogHeader>
              <div className="grid gap-4 py-4 max-h-[60vh] overflow-y-auto">
                <div className="grid grid-cols-2 gap-4">
                  <div className="grid gap-2">
                    <Label htmlFor="nome">Nome Completo</Label>
                    <Input
                      id="nome"
                      value={novoColaborador.nome}
                      onChange={(e) => setNovoColaborador({...novoColaborador, nome: e.target.value})}
                    />
                  </div>
                  <div className="grid gap-2">
                    <Label htmlFor="cpf">CPF</Label>
                    <Input
                      id="cpf"
                      value={novoColaborador.cpf}
                      onChange={(e) => setNovoColaborador({...novoColaborador, cpf: e.target.value})}
                    />
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div className="grid gap-2">
                    <Label htmlFor="email">Email</Label>
                    <Input
                      id="email"
                      type="email"
                      value={novoColaborador.email}
                      onChange={(e) => setNovoColaborador({...novoColaborador, email: e.target.value})}
                    />
                  </div>
                  <div className="grid gap-2">
                    <Label htmlFor="telefone">Telefone</Label>
                    <Input
                      id="telefone"
                      value={novoColaborador.telefone}
                      onChange={(e) => setNovoColaborador({...novoColaborador, telefone: e.target.value})}
                    />
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div className="grid gap-2">
                    <Label htmlFor="cargo">Cargo</Label>
                    <Input
                      id="cargo"
                      value={novoColaborador.cargo}
                      onChange={(e) => setNovoColaborador({...novoColaborador, cargo: e.target.value})}
                      placeholder="Ex: Coordenador, Promoter"
                    />
                  </div>
                  <div className="grid gap-2">
                    <Label htmlFor="departamento">Departamento</Label>
                    <Input
                      id="departamento"
                      value={novoColaborador.departamento}
                      onChange={(e) => setNovoColaborador({...novoColaborador, departamento: e.target.value})}
                      placeholder="Ex: Produção, Marketing"
                    />
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div className="grid gap-2">
                    <Label htmlFor="tipo">Tipo</Label>
                    <Select
                      value={novoColaborador.tipo}
                      onValueChange={(value: any) => setNovoColaborador({...novoColaborador, tipo: value})}
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="funcionario">Funcionário</SelectItem>
                        <SelectItem value="freelancer">Freelancer</SelectItem>
                        <SelectItem value="voluntario">Voluntário</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="grid gap-2">
                    <Label htmlFor="data_admissao">Data de Admissão</Label>
                    <Input
                      id="data_admissao"
                      type="date"
                      value={novoColaborador.data_admissao}
                      onChange={(e) => setNovoColaborador({...novoColaborador, data_admissao: e.target.value})}
                    />
                  </div>
                </div>
                {novoColaborador.tipo !== 'voluntario' && (
                  <div className="grid grid-cols-2 gap-4">
                    <div className="grid gap-2">
                      <Label htmlFor="salario">Salário (R$)</Label>
                      <Input
                        id="salario"
                        type="number"
                        value={novoColaborador.salario}
                        onChange={(e) => setNovoColaborador({...novoColaborador, salario: parseFloat(e.target.value)})}
                      />
                    </div>
                    <div className="grid gap-2">
                      <Label htmlFor="comissao">Comissão (%)</Label>
                      <Input
                        id="comissao"
                        type="number"
                        value={novoColaborador.comissao_percentual}
                        onChange={(e) => setNovoColaborador({...novoColaborador, comissao_percentual: parseFloat(e.target.value)})}
                      />
                    </div>
                  </div>
                )}
                <div className="grid gap-2">
                  <Label htmlFor="habilidades">Habilidades (separadas por vírgula)</Label>
                  <Input
                    id="habilidades"
                    value={novoColaborador.habilidades.join(', ')}
                    onChange={(e) => setNovoColaborador({
                      ...novoColaborador, 
                      habilidades: e.target.value.split(',').map(s => s.trim()).filter(s => s)
                    })}
                    placeholder="Ex: Atendimento, Vendas, Organização"
                  />
                </div>
              </div>
              <DialogFooter>
                <Button variant="outline" onClick={() => setShowNovoColaborador(false)}>
                  Cancelar
                </Button>
                <Button onClick={criarColaborador}>Cadastrar</Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>
        </div>
      </div>

      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium">Total Ativos</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{estatisticas?.total_ativos || 0}</div>
            <p className="text-xs text-muted-foreground mt-1">Colaboradores</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium">Escalados</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{estatisticas?.total_escalados || 0}</div>
            <p className="text-xs text-muted-foreground mt-1">Para próximos eventos</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium">Tarefas Pendentes</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{estatisticas?.tarefas_pendentes || 0}</div>
            <p className="text-xs text-muted-foreground mt-1">Aguardando conclusão</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium">Custo Mensal</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              R$ {estatisticas?.custo_mensal.toLocaleString('pt-BR') || '0'}
            </div>
            <p className="text-xs text-muted-foreground mt-1">Folha de pagamento</p>
          </CardContent>
        </Card>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="colaboradores">Colaboradores</TabsTrigger>
          <TabsTrigger value="escala">Escalas</TabsTrigger>
          <TabsTrigger value="tarefas">Tarefas</TabsTrigger>
          <TabsTrigger value="departamentos">Departamentos</TabsTrigger>
        </TabsList>

        <TabsContent value="colaboradores" className="space-y-4">
          <div className="flex gap-4 items-center">
            <Input
              placeholder="Buscar por nome, cargo ou departamento..."
              value={busca}
              onChange={(e) => setBusca(e.target.value)}
              className="max-w-sm"
            />
            <Select value={filtroStatus} onValueChange={setFiltroStatus}>
              <SelectTrigger className="w-[180px]">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="todos">Todos</SelectItem>
                <SelectItem value="ativo">Ativos</SelectItem>
                <SelectItem value="inativo">Inativos</SelectItem>
                <SelectItem value="ferias">Férias</SelectItem>
                <SelectItem value="afastado">Afastados</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {colaboradores
              .filter(colab => 
                (colab.nome.toLowerCase().includes(busca.toLowerCase()) ||
                 colab.cargo.toLowerCase().includes(busca.toLowerCase()) ||
                 colab.departamento.toLowerCase().includes(busca.toLowerCase())) &&
                (filtroStatus === 'todos' || colab.status === filtroStatus)
              )
              .map(colaborador => (
                <Card key={colaborador.id}>
                  <CardHeader>
                    <div className="flex items-start justify-between">
                      <div className="flex items-center gap-3">
                        <Avatar>
                          <AvatarImage src={colaborador.foto} />
                          <AvatarFallback>{colaborador.nome.split(' ').map(n => n[0]).join('')}</AvatarFallback>
                        </Avatar>
                        <div>
                          <CardTitle className="text-lg">{colaborador.nome}</CardTitle>
                          <CardDescription>{colaborador.cargo}</CardDescription>
                        </div>
                      </div>
                      <Badge className={getStatusColor(colaborador.status)}>
                        {colaborador.status}
                      </Badge>
                    </div>
                  </CardHeader>
                  <CardContent className="space-y-2">
                    <div className="flex items-center gap-2 text-sm">
                      <Briefcase className="h-3 w-3 text-muted-foreground" />
                      <span>{colaborador.departamento}</span>
                    </div>
                    <div className="flex items-center gap-2 text-sm">
                      <Mail className="h-3 w-3 text-muted-foreground" />
                      <span>{colaborador.email}</span>
                    </div>
                    <div className="flex items-center gap-2 text-sm">
                      <Phone className="h-3 w-3 text-muted-foreground" />
                      <span>{colaborador.telefone}</span>
                    </div>
                    {colaborador.habilidades.length > 0 && (
                      <div className="flex flex-wrap gap-1 pt-2">
                        {colaborador.habilidades.slice(0, 3).map(hab => (
                          <Badge key={hab} variant="outline" className="text-xs">
                            {hab}
                          </Badge>
                        ))}
                        {colaborador.habilidades.length > 3 && (
                          <Badge variant="outline" className="text-xs">
                            +{colaborador.habilidades.length - 3}
                          </Badge>
                        )}
                      </div>
                    )}
                    <div className="flex items-center justify-between pt-2 border-t">
                      <div className="flex items-center gap-1">
                        <Award className="h-3 w-3 text-yellow-500" />
                        <span className="text-sm font-medium">{colaborador.avaliacao_media.toFixed(1)}</span>
                      </div>
                      <span className="text-xs text-muted-foreground">
                        {colaborador.eventos_trabalhados} eventos
                      </span>
                    </div>
                  </CardContent>
                  <CardFooter className="flex gap-2">
                    <Button 
                      variant="outline" 
                      size="sm"
                      onClick={() => setSelectedColaborador(colaborador)}
                    >
                      <Edit className="mr-1 h-3 w-3" />
                      Editar
                    </Button>
                    <Button 
                      variant="outline" 
                      size="sm"
                      onClick={() => deletarColaborador(colaborador.id)}
                    >
                      <Trash2 className="mr-1 h-3 w-3" />
                      Excluir
                    </Button>
                  </CardFooter>
                </Card>
              ))}
          </div>
        </TabsContent>

        <TabsContent value="escala" className="space-y-4">
          <div className="flex justify-between items-center">
            <h2 className="text-xl font-semibold">Escalas de Trabalho</h2>
            <Dialog open={showNovaEscala} onOpenChange={setShowNovaEscala}>
              <DialogTrigger asChild>
                <Button>
                  <Calendar className="mr-2 h-4 w-4" />
                  Nova Escala
                </Button>
              </DialogTrigger>
              <DialogContent>
                <DialogHeader>
                  <DialogTitle>Criar Escala</DialogTitle>
                  <DialogDescription>
                    Agende um colaborador para um evento
                  </DialogDescription>
                </DialogHeader>
                <div className="grid gap-4 py-4">
                  <div className="grid gap-2">
                    <Label>Colaborador</Label>
                    <Select
                      value={novaEscala.colaborador_id.toString()}
                      onValueChange={(value) => setNovaEscala({...novaEscala, colaborador_id: parseInt(value)})}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Selecione um colaborador" />
                      </SelectTrigger>
                      <SelectContent>
                        {colaboradores.filter(c => c.status === 'ativo').map(colab => (
                          <SelectItem key={colab.id} value={colab.id.toString()}>
                            {colab.nome} - {colab.cargo}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div className="grid gap-2">
                      <Label>Data Início</Label>
                      <Input
                        type="datetime-local"
                        value={novaEscala.data_inicio}
                        onChange={(e) => setNovaEscala({...novaEscala, data_inicio: e.target.value})}
                      />
                    </div>
                    <div className="grid gap-2">
                      <Label>Data Fim</Label>
                      <Input
                        type="datetime-local"
                        value={novaEscala.data_fim}
                        onChange={(e) => setNovaEscala({...novaEscala, data_fim: e.target.value})}
                      />
                    </div>
                  </div>
                  <div className="grid gap-2">
                    <Label>Turno</Label>
                    <Select
                      value={novaEscala.turno}
                      onValueChange={(value: any) => setNovaEscala({...novaEscala, turno: value})}
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="manha">Manhã</SelectItem>
                        <SelectItem value="tarde">Tarde</SelectItem>
                        <SelectItem value="noite">Noite</SelectItem>
                        <SelectItem value="integral">Integral</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="grid gap-2">
                    <Label>Função</Label>
                    <Input
                      value={novaEscala.funcao}
                      onChange={(e) => setNovaEscala({...novaEscala, funcao: e.target.value})}
                      placeholder="Ex: Coordenação, Apoio, Segurança"
                    />
                  </div>
                  <div className="grid gap-2">
                    <Label>Local</Label>
                    <Input
                      value={novaEscala.local}
                      onChange={(e) => setNovaEscala({...novaEscala, local: e.target.value})}
                      placeholder="Ex: Entrada principal, Bar, Backstage"
                    />
                  </div>
                </div>
                <DialogFooter>
                  <Button variant="outline" onClick={() => setShowNovaEscala(false)}>
                    Cancelar
                  </Button>
                  <Button onClick={criarEscala}>Criar Escala</Button>
                </DialogFooter>
              </DialogContent>
            </Dialog>
          </div>

          <div className="grid gap-4">
            {escalas.map(escala => (
              <Card key={escala.id}>
                <CardHeader>
                  <div className="flex justify-between items-center">
                    <div>
                      <CardTitle className="text-lg">
                        {escala.colaborador?.nome} - {escala.funcao}
                      </CardTitle>
                      <CardDescription>
                        {escala.evento?.nome} • {escala.local || escala.evento?.local}
                      </CardDescription>
                    </div>
                    <Badge className={getStatusColor(escala.status)}>
                      {escala.status}
                    </Badge>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                    <div>
                      <p className="text-muted-foreground">Início</p>
                      <p className="font-medium">
                        {format(new Date(escala.data_inicio), 'dd/MM HH:mm')}
                      </p>
                    </div>
                    <div>
                      <p className="text-muted-foreground">Fim</p>
                      <p className="font-medium">
                        {format(new Date(escala.data_fim), 'dd/MM HH:mm')}
                      </p>
                    </div>
                    <div>
                      <p className="text-muted-foreground">Turno</p>
                      <p className="font-medium flex items-center gap-1">
                        <span>{getTurnoIcon(escala.turno)}</span>
                        {escala.turno}
                      </p>
                    </div>
                    <div>
                      <p className="text-muted-foreground">Colaborador</p>
                      <p className="font-medium">{escala.colaborador?.cargo}</p>
                    </div>
                  </div>
                  {escala.observacoes && (
                    <div className="mt-3 pt-3 border-t">
                      <p className="text-sm text-muted-foreground">Observações:</p>
                      <p className="text-sm">{escala.observacoes}</p>
                    </div>
                  )}
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="tarefas" className="space-y-4">
          <div className="flex justify-between items-center">
            <h2 className="text-xl font-semibold">Tarefas</h2>
            <Dialog open={showNovaTarefa} onOpenChange={setShowNovaTarefa}>
              <DialogTrigger asChild>
                <Button>
                  <Plus className="mr-2 h-4 w-4" />
                  Nova Tarefa
                </Button>
              </DialogTrigger>
              <DialogContent>
                <DialogHeader>
                  <DialogTitle>Criar Tarefa</DialogTitle>
                  <DialogDescription>
                    Atribua uma tarefa a um colaborador
                  </DialogDescription>
                </DialogHeader>
                <div className="grid gap-4 py-4">
                  <div className="grid gap-2">
                    <Label>Colaborador</Label>
                    <Select
                      value={novaTarefa.colaborador_id.toString()}
                      onValueChange={(value) => setNovaTarefa({...novaTarefa, colaborador_id: parseInt(value)})}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Selecione um colaborador" />
                      </SelectTrigger>
                      <SelectContent>
                        {colaboradores.filter(c => c.status === 'ativo').map(colab => (
                          <SelectItem key={colab.id} value={colab.id.toString()}>
                            {colab.nome}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="grid gap-2">
                    <Label>Título</Label>
                    <Input
                      value={novaTarefa.titulo}
                      onChange={(e) => setNovaTarefa({...novaTarefa, titulo: e.target.value})}
                      placeholder="Ex: Verificar equipamentos de som"
                    />
                  </div>
                  <div className="grid gap-2">
                    <Label>Descrição</Label>
                    <Textarea
                      value={novaTarefa.descricao}
                      onChange={(e) => setNovaTarefa({...novaTarefa, descricao: e.target.value})}
                      placeholder="Detalhes da tarefa..."
                    />
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div className="grid gap-2">
                      <Label>Prioridade</Label>
                      <Select
                        value={novaTarefa.prioridade}
                        onValueChange={(value: any) => setNovaTarefa({...novaTarefa, prioridade: value})}
                      >
                        <SelectTrigger>
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="baixa">Baixa</SelectItem>
                          <SelectItem value="media">Média</SelectItem>
                          <SelectItem value="alta">Alta</SelectItem>
                          <SelectItem value="urgente">Urgente</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                    <div className="grid gap-2">
                      <Label>Prazo</Label>
                      <Input
                        type="datetime-local"
                        value={novaTarefa.prazo}
                        onChange={(e) => setNovaTarefa({...novaTarefa, prazo: e.target.value})}
                      />
                    </div>
                  </div>
                </div>
                <DialogFooter>
                  <Button variant="outline" onClick={() => setShowNovaTarefa(false)}>
                    Cancelar
                  </Button>
                  <Button onClick={criarTarefa}>Criar Tarefa</Button>
                </DialogFooter>
              </DialogContent>
            </Dialog>
          </div>

          <div className="grid gap-3">
            {tarefas.map(tarefa => (
              <Card key={tarefa.id}>
                <CardHeader className="pb-3">
                  <div className="flex justify-between items-start">
                    <div>
                      <CardTitle className="text-base">{tarefa.titulo}</CardTitle>
                      <CardDescription>
                        {tarefa.colaborador?.nome} • {tarefa.colaborador?.cargo}
                      </CardDescription>
                    </div>
                    <div className="flex gap-2">
                      <Badge variant={getPrioridadeColor(tarefa.prioridade)}>
                        {tarefa.prioridade}
                      </Badge>
                      <Badge className={getStatusColor(tarefa.status)}>
                        {tarefa.status.replace('_', ' ')}
                      </Badge>
                    </div>
                  </div>
                </CardHeader>
                {tarefa.descricao && (
                  <CardContent>
                    <p className="text-sm text-muted-foreground">{tarefa.descricao}</p>
                  </CardContent>
                )}
                <CardFooter className="flex justify-between">
                  <div className="flex items-center gap-2 text-sm text-muted-foreground">
                    <Clock className="h-3 w-3" />
                    {tarefa.prazo && (
                      <span>Prazo: {format(new Date(tarefa.prazo), 'dd/MM HH:mm')}</span>
                    )}
                  </div>
                  {tarefa.status !== 'concluida' && (
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => atualizarStatusTarefa(tarefa.id, 
                        tarefa.status === 'pendente' ? 'em_andamento' : 'concluida'
                      )}
                    >
                      {tarefa.status === 'pendente' ? 'Iniciar' : 'Concluir'}
                    </Button>
                  )}
                </CardFooter>
              </Card>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="departamentos" className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {estatisticas?.departamentos.map(dept => (
              <Card key={dept.nome}>
                <CardHeader>
                  <CardTitle className="text-lg">{dept.nome}</CardTitle>
                  {dept.responsavel && (
                    <CardDescription>Responsável: {dept.responsavel}</CardDescription>
                  )}
                </CardHeader>
                <CardContent>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <Users className="h-4 w-4 text-muted-foreground" />
                      <span className="text-2xl font-bold">{dept.colaboradores}</span>
                    </div>
                    <span className="text-sm text-muted-foreground">colaboradores</span>
                  </div>
                </CardContent>
                <CardFooter>
                  <Button variant="outline" size="sm" className="w-full">
                    Ver Equipe
                  </Button>
                </CardFooter>
              </Card>
            ))}
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}