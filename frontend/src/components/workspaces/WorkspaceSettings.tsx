import React, { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Switch } from '@/components/ui/switch';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import {
  Table,
  TableBody,
  TableCaption,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import { useToast } from '@/hooks/use-toast';
import api from '@/lib/api';
import {
  Building2,
  Users,
  Calendar,
  CreditCard,
  Settings,
  Trash2,
  Plus,
  Edit,
  Shield,
  AlertTriangle,
  Check,
  X,
  Rocket,
  Crown,
  Briefcase,
} from 'lucide-react';
import { format } from 'date-fns';
import { ptBR } from 'date-fns/locale';

interface Workspace {
  id: number;
  nome: string;
  slug: string;
  logo_url?: string;
  plano: string;
  ativo: boolean;
  limite_usuarios?: number;
  limite_eventos?: number;
  limite_participantes?: number;
  trial_ate?: string;
  criado_em: string;
  atualizado_em?: string;
}

interface WorkspaceUser {
  id: number;
  usuario_id: number;
  usuario_nome: string;
  usuario_cpf: string;
  role: string;
  data_entrada: string;
  ativo: boolean;
}

interface WorkspaceStats {
  usuarios_ativos: number;
  eventos_ativos: number;
  participantes_total: number;
  vendas_mes: number;
  checkins_hoje: number;
  uso_armazenamento: number;
}

const planos = {
  free: {
    nome: 'Free',
    icon: Briefcase,
    color: 'text-gray-600',
    bgColor: 'bg-gray-100',
    limites: {
      usuarios: 3,
      eventos: 5,
      participantes: 100,
      armazenamento: 100, // MB
    },
    preco: 0,
  },
  starter: {
    nome: 'Starter',
    icon: Rocket,
    color: 'text-blue-600',
    bgColor: 'bg-blue-100',
    limites: {
      usuarios: 10,
      eventos: 20,
      participantes: 1000,
      armazenamento: 1000, // MB
    },
    preco: 99,
  },
  pro: {
    nome: 'Pro',
    icon: Crown,
    color: 'text-purple-600',
    bgColor: 'bg-purple-100',
    limites: {
      usuarios: 50,
      eventos: 100,
      participantes: 10000,
      armazenamento: 10000, // MB
    },
    preco: 299,
  },
  enterprise: {
    nome: 'Enterprise',
    icon: Building2,
    color: 'text-gold-600',
    bgColor: 'bg-gold-100',
    limites: {
      usuarios: null, // Ilimitado
      eventos: null,
      participantes: null,
      armazenamento: null,
    },
    preco: null, // Personalizado
  },
};

export default function WorkspaceSettings() {
  const [workspace, setWorkspace] = useState<Workspace | null>(null);
  const [users, setUsers] = useState<WorkspaceUser[]>([]);
  const [stats, setStats] = useState<WorkspaceStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [editingWorkspace, setEditingWorkspace] = useState(false);
  const [addingUser, setAddingUser] = useState(false);
  const [deletingWorkspace, setDeletingWorkspace] = useState(false);
  const [newUser, setNewUser] = useState({ cpf: '', role: 'membro' });
  const [updatedWorkspace, setUpdatedWorkspace] = useState({ nome: '', logo_url: '' });
  const { toast } = useToast();

  useEffect(() => {
    loadWorkspaceData();
  }, []);

  const loadWorkspaceData = async () => {
    try {
      setLoading(true);
      
      const workspaceResponse = await api.get('/api/workspaces/current');
      setWorkspace(workspaceResponse.data);
      setUpdatedWorkspace({
        nome: workspaceResponse.data.nome,
        logo_url: workspaceResponse.data.logo_url || '',
      });

      const statsResponse = await api.get(`/api/workspaces/${workspaceResponse.data.id}/stats`);
      setStats(statsResponse.data);

      const usersResponse = await api.get(`/api/workspaces/${workspaceResponse.data.id}/usuarios`);
      setUsers(usersResponse.data);
    } catch (error) {
      console.error('Erro ao carregar dados do workspace:', error);
      toast({
        variant: 'destructive',
        title: 'Erro',
        description: 'Não foi possível carregar os dados do workspace',
      });
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateWorkspace = async () => {
    if (!workspace) return;

    try {
      const response = await api.put(`/api/workspaces/${workspace.id}`, updatedWorkspace);
      setWorkspace(response.data);
      setEditingWorkspace(false);
      
      toast({
        title: 'Sucesso',
        description: 'Workspace atualizado com sucesso',
      });
    } catch (error: any) {
      toast({
        variant: 'destructive',
        title: 'Erro',
        description: error.response?.data?.detail || 'Erro ao atualizar workspace',
      });
    }
  };

  const handleAddUser = async () => {
    if (!workspace || !newUser.cpf) return;

    try {
      await api.post(`/api/workspaces/${workspace.id}/usuarios`, newUser);
      await loadWorkspaceData();
      setAddingUser(false);
      setNewUser({ cpf: '', role: 'membro' });
      
      toast({
        title: 'Sucesso',
        description: 'Usuário adicionado ao workspace',
      });
    } catch (error: any) {
      toast({
        variant: 'destructive',
        title: 'Erro',
        description: error.response?.data?.detail || 'Erro ao adicionar usuário',
      });
    }
  };

  const handleRemoveUser = async (userId: number) => {
    if (!workspace) return;

    try {
      await api.delete(`/api/workspaces/${workspace.id}/usuarios/${userId}`);
      await loadWorkspaceData();
      
      toast({
        title: 'Sucesso',
        description: 'Usuário removido do workspace',
      });
    } catch (error: any) {
      toast({
        variant: 'destructive',
        title: 'Erro',
        description: error.response?.data?.detail || 'Erro ao remover usuário',
      });
    }
  };

  const handleUpgradePlan = async (newPlan: string) => {
    if (!workspace) return;

    try {
      const response = await api.put(`/api/workspaces/${workspace.id}`, { plano: newPlan });
      setWorkspace(response.data);
      
      toast({
        title: 'Sucesso',
        description: `Plano atualizado para ${planos[newPlan].nome}`,
      });
    } catch (error: any) {
      toast({
        variant: 'destructive',
        title: 'Erro',
        description: error.response?.data?.detail || 'Erro ao atualizar plano',
      });
    }
  };

  if (loading || !workspace || !stats) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto"></div>
          <p className="mt-4 text-muted-foreground">Carregando configurações...</p>
        </div>
      </div>
    );
  }

  const planoAtual = planos[workspace.plano];
  const usagePercent = {
    usuarios: planoAtual.limites.usuarios
      ? (stats.usuarios_ativos / planoAtual.limites.usuarios) * 100
      : 0,
    eventos: planoAtual.limites.eventos
      ? (stats.eventos_ativos / planoAtual.limites.eventos) * 100
      : 0,
    participantes: planoAtual.limites.participantes
      ? (stats.participantes_total / planoAtual.limites.participantes) * 100
      : 0,
    armazenamento: planoAtual.limites.armazenamento
      ? (stats.uso_armazenamento / planoAtual.limites.armazenamento) * 100
      : 0,
  };

  return (
    <div className="container mx-auto p-6">
      <div className="mb-6">
        <h1 className="text-3xl font-bold">Configurações do Workspace</h1>
        <p className="text-muted-foreground">
          Gerencie as configurações e usuários do seu workspace
        </p>
      </div>

      <Tabs defaultValue="general" className="space-y-4">
        <TabsList>
          <TabsTrigger value="general">Geral</TabsTrigger>
          <TabsTrigger value="users">Usuários</TabsTrigger>
          <TabsTrigger value="billing">Plano & Faturamento</TabsTrigger>
          <TabsTrigger value="usage">Uso</TabsTrigger>
          <TabsTrigger value="danger">Zona de Perigo</TabsTrigger>
        </TabsList>

        <TabsContent value="general" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Informações do Workspace</CardTitle>
              <CardDescription>
                Atualize as informações básicas do seu workspace
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="nome">Nome do Workspace</Label>
                <Input
                  id="nome"
                  value={updatedWorkspace.nome}
                  onChange={(e) => setUpdatedWorkspace({ ...updatedWorkspace, nome: e.target.value })}
                  disabled={!editingWorkspace}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="slug">Slug (URL)</Label>
                <Input id="slug" value={workspace.slug} disabled />
              </div>
              <div className="space-y-2">
                <Label htmlFor="logo">URL do Logo</Label>
                <Input
                  id="logo"
                  value={updatedWorkspace.logo_url}
                  onChange={(e) => setUpdatedWorkspace({ ...updatedWorkspace, logo_url: e.target.value })}
                  disabled={!editingWorkspace}
                  placeholder="https://..."
                />
              </div>
              <div className="flex items-center justify-between">
                <div className="space-y-1">
                  <Label>Status</Label>
                  <Badge variant={workspace.ativo ? 'default' : 'secondary'}>
                    {workspace.ativo ? 'Ativo' : 'Inativo'}
                  </Badge>
                </div>
                <div className="space-y-1">
                  <Label>Criado em</Label>
                  <p className="text-sm text-muted-foreground">
                    {format(new Date(workspace.criado_em), 'dd/MM/yyyy', { locale: ptBR })}
                  </p>
                </div>
              </div>
            </CardContent>
            <CardFooter className="flex justify-between">
              {editingWorkspace ? (
                <>
                  <Button variant="outline" onClick={() => setEditingWorkspace(false)}>
                    Cancelar
                  </Button>
                  <Button onClick={handleUpdateWorkspace}>Salvar Alterações</Button>
                </>
              ) : (
                <Button onClick={() => setEditingWorkspace(true)}>
                  <Edit className="mr-2 h-4 w-4" />
                  Editar Informações
                </Button>
              )}
            </CardFooter>
          </Card>
        </TabsContent>

        <TabsContent value="users" className="space-y-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between">
              <div>
                <CardTitle>Usuários do Workspace</CardTitle>
                <CardDescription>
                  {stats.usuarios_ativos} de {planoAtual.limites.usuarios || '∞'} usuários
                </CardDescription>
              </div>
              <Dialog open={addingUser} onOpenChange={setAddingUser}>
                <DialogTrigger asChild>
                  <Button>
                    <Plus className="mr-2 h-4 w-4" />
                    Adicionar Usuário
                  </Button>
                </DialogTrigger>
                <DialogContent>
                  <DialogHeader>
                    <DialogTitle>Adicionar Usuário ao Workspace</DialogTitle>
                    <DialogDescription>
                      Convide um usuário existente para este workspace
                    </DialogDescription>
                  </DialogHeader>
                  <div className="grid gap-4 py-4">
                    <div className="grid grid-cols-4 items-center gap-4">
                      <Label htmlFor="cpf" className="text-right">
                        CPF
                      </Label>
                      <Input
                        id="cpf"
                        value={newUser.cpf}
                        onChange={(e) => setNewUser({ ...newUser, cpf: e.target.value })}
                        className="col-span-3"
                        placeholder="000.000.000-00"
                      />
                    </div>
                    <div className="grid grid-cols-4 items-center gap-4">
                      <Label htmlFor="role" className="text-right">
                        Função
                      </Label>
                      <Select
                        value={newUser.role}
                        onValueChange={(value) => setNewUser({ ...newUser, role: value })}
                      >
                        <SelectTrigger className="col-span-3">
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="owner">Proprietário</SelectItem>
                          <SelectItem value="admin">Administrador</SelectItem>
                          <SelectItem value="membro">Membro</SelectItem>
                          <SelectItem value="viewer">Visualizador</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                  </div>
                  <DialogFooter>
                    <Button onClick={handleAddUser}>Adicionar</Button>
                  </DialogFooter>
                </DialogContent>
              </Dialog>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Nome</TableHead>
                    <TableHead>CPF</TableHead>
                    <TableHead>Função</TableHead>
                    <TableHead>Entrada</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead className="text-right">Ações</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {users.map((user) => (
                    <TableRow key={user.id}>
                      <TableCell className="font-medium">{user.usuario_nome}</TableCell>
                      <TableCell>{user.usuario_cpf}</TableCell>
                      <TableCell>
                        <Badge variant="outline">{user.role}</Badge>
                      </TableCell>
                      <TableCell>
                        {format(new Date(user.data_entrada), 'dd/MM/yyyy', { locale: ptBR })}
                      </TableCell>
                      <TableCell>
                        <Badge variant={user.ativo ? 'default' : 'secondary'}>
                          {user.ativo ? 'Ativo' : 'Inativo'}
                        </Badge>
                      </TableCell>
                      <TableCell className="text-right">
                        {user.role !== 'owner' && (
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => handleRemoveUser(user.usuario_id)}
                          >
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        )}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="billing" className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            {Object.entries(planos).map(([key, plano]) => {
              const isCurrentPlan = key === workspace.plano;
              const Icon = plano.icon;
              
              return (
                <Card key={key} className={isCurrentPlan ? 'border-primary' : ''}>
                  <CardHeader>
                    <div className="flex items-center justify-between">
                      <Icon className={`h-6 w-6 ${plano.color}`} />
                      {isCurrentPlan && (
                        <Badge variant="default">Plano Atual</Badge>
                      )}
                    </div>
                    <CardTitle>{plano.nome}</CardTitle>
                    <CardDescription>
                      {plano.preco === null
                        ? 'Personalizado'
                        : plano.preco === 0
                        ? 'Grátis'
                        : `R$ ${plano.preco}/mês`}
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-2">
                    <div className="space-y-1 text-sm">
                      <div className="flex items-center gap-2">
                        <Users className="h-4 w-4" />
                        <span>
                          {plano.limites.usuarios || '∞'} usuários
                        </span>
                      </div>
                      <div className="flex items-center gap-2">
                        <Calendar className="h-4 w-4" />
                        <span>
                          {plano.limites.eventos || '∞'} eventos
                        </span>
                      </div>
                      <div className="flex items-center gap-2">
                        <Users className="h-4 w-4" />
                        <span>
                          {plano.limites.participantes
                            ? `${plano.limites.participantes.toLocaleString()} participantes`
                            : 'Participantes ilimitados'}
                        </span>
                      </div>
                    </div>
                  </CardContent>
                  {!isCurrentPlan && key !== 'free' && (
                    <CardFooter>
                      <Button
                        className="w-full"
                        variant={key === 'enterprise' ? 'default' : 'outline'}
                        onClick={() => handleUpgradePlan(key)}
                      >
                        {key === 'enterprise' ? 'Contatar Vendas' : 'Fazer Upgrade'}
                      </Button>
                    </CardFooter>
                  )}
                </Card>
              );
            })}
          </div>

          {workspace.trial_ate && (
            <Alert>
              <AlertTriangle className="h-4 w-4" />
              <AlertTitle>Período de Trial</AlertTitle>
              <AlertDescription>
                Seu período de teste termina em{' '}
                {format(new Date(workspace.trial_ate), 'dd/MM/yyyy', { locale: ptBR })}
              </AlertDescription>
            </Alert>
          )}
        </TabsContent>

        <TabsContent value="usage" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Uso de Recursos</CardTitle>
              <CardDescription>
                Acompanhe o uso dos recursos do seu workspace
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <Label>Usuários</Label>
                  <span className="text-sm text-muted-foreground">
                    {stats.usuarios_ativos}/{planoAtual.limites.usuarios || '∞'}
                  </span>
                </div>
                <Progress value={usagePercent.usuarios} className="h-2" />
              </div>

              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <Label>Eventos</Label>
                  <span className="text-sm text-muted-foreground">
                    {stats.eventos_ativos}/{planoAtual.limites.eventos || '∞'}
                  </span>
                </div>
                <Progress value={usagePercent.eventos} className="h-2" />
              </div>

              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <Label>Participantes</Label>
                  <span className="text-sm text-muted-foreground">
                    {stats.participantes_total.toLocaleString()}/
                    {planoAtual.limites.participantes?.toLocaleString() || '∞'}
                  </span>
                </div>
                <Progress value={usagePercent.participantes} className="h-2" />
              </div>

              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <Label>Armazenamento</Label>
                  <span className="text-sm text-muted-foreground">
                    {stats.uso_armazenamento} MB/{planoAtual.limites.armazenamento || '∞'} MB
                  </span>
                </div>
                <Progress value={usagePercent.armazenamento} className="h-2" />
              </div>
            </CardContent>
          </Card>

          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">
                  Vendas este mês
                </CardTitle>
                <CreditCard className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  R$ {stats.vendas_mes.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">
                  Check-ins hoje
                </CardTitle>
                <Users className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{stats.checkins_hoje}</div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">
                  Eventos ativos
                </CardTitle>
                <Calendar className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{stats.eventos_ativos}</div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="danger" className="space-y-4">
          <Alert variant="destructive">
            <AlertTriangle className="h-4 w-4" />
            <AlertTitle>Zona de Perigo</AlertTitle>
            <AlertDescription>
              Ações irreversíveis. Proceda com cautela.
            </AlertDescription>
          </Alert>

          <Card className="border-destructive">
            <CardHeader>
              <CardTitle className="text-destructive">Deletar Workspace</CardTitle>
              <CardDescription>
                Esta ação é permanente e não pode ser desfeita. Todos os dados serão perdidos.
              </CardDescription>
            </CardHeader>
            <CardFooter>
              <Dialog open={deletingWorkspace} onOpenChange={setDeletingWorkspace}>
                <DialogTrigger asChild>
                  <Button variant="destructive">
                    <Trash2 className="mr-2 h-4 w-4" />
                    Deletar Workspace
                  </Button>
                </DialogTrigger>
                <DialogContent>
                  <DialogHeader>
                    <DialogTitle>Tem certeza absoluta?</DialogTitle>
                    <DialogDescription>
                      Esta ação não pode ser desfeita. Isso irá permanentemente deletar o workspace
                      <span className="font-semibold"> {workspace.nome}</span> e remover todos os dados
                      associados.
                    </DialogDescription>
                  </DialogHeader>
                  <div className="bg-destructive/10 border border-destructive/20 p-4 rounded-md">
                    <p className="text-sm">
                      Digite <span className="font-mono font-semibold">{workspace.slug}</span> para confirmar:
                    </p>
                    <Input
                      className="mt-2"
                      placeholder="Digite o slug do workspace"
                    />
                  </div>
                  <DialogFooter className="gap-2">
                    <Button variant="outline" onClick={() => setDeletingWorkspace(false)}>
                      Cancelar
                    </Button>
                    <Button variant="destructive" disabled>
                      Deletar Permanentemente
                    </Button>
                  </DialogFooter>
                </DialogContent>
              </Dialog>
            </CardFooter>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}