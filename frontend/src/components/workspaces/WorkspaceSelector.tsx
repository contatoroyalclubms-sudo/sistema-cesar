import React, { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import {
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectLabel,
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
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { useToast } from '@/hooks/use-toast';
import api from '@/lib/api';
import { Building2, Plus, Crown, Rocket, Briefcase, Users } from 'lucide-react';

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
  criado_em: string;
  usuarios?: number;
  eventos?: number;
}

const planoIcons = {
  free: Briefcase,
  starter: Rocket,
  pro: Crown,
  enterprise: Building2,
};

const planoColors = {
  free: 'bg-gray-500',
  starter: 'bg-blue-500',
  pro: 'bg-purple-500',
  enterprise: 'bg-gold-500',
};

export default function WorkspaceSelector() {
  const [workspaces, setWorkspaces] = useState<Workspace[]>([]);
  const [currentWorkspace, setCurrentWorkspace] = useState<Workspace | null>(null);
  const [isCreating, setIsCreating] = useState(false);
  const [loading, setLoading] = useState(true);
  const [newWorkspace, setNewWorkspace] = useState({
    nome: '',
    slug: '',
  });
  const { toast } = useToast();

  useEffect(() => {
    loadWorkspaces();
  }, []);

  const loadWorkspaces = async () => {
    try {
      const response = await api.get('/api/workspaces');
      setWorkspaces(response.data);
      
      const currentResponse = await api.get('/api/workspaces/current');
      setCurrentWorkspace(currentResponse.data);
    } catch (error) {
      console.error('Erro ao carregar workspaces:', error);
      toast({
        variant: 'destructive',
        title: 'Erro',
        description: 'Não foi possível carregar os workspaces',
      });
    } finally {
      setLoading(false);
    }
  };

  const handleCreateWorkspace = async () => {
    if (!newWorkspace.nome || !newWorkspace.slug) {
      toast({
        variant: 'destructive',
        title: 'Erro',
        description: 'Nome e slug são obrigatórios',
      });
      return;
    }

    try {
      const response = await api.post('/api/workspaces', newWorkspace);
      setWorkspaces([...workspaces, response.data]);
      setIsCreating(false);
      setNewWorkspace({ nome: '', slug: '' });
      
      toast({
        title: 'Sucesso',
        description: 'Workspace criado com sucesso',
      });
    } catch (error: any) {
      toast({
        variant: 'destructive',
        title: 'Erro',
        description: error.response?.data?.detail || 'Erro ao criar workspace',
      });
    }
  };

  const handleSwitchWorkspace = async (workspaceId: string) => {
    try {
      const response = await api.post(`/api/workspaces/${workspaceId}/switch`);
      setCurrentWorkspace(response.data);
      
      toast({
        title: 'Sucesso',
        description: `Mudado para ${response.data.nome}`,
      });
      
      // Recarregar a página para atualizar contexto
      setTimeout(() => {
        window.location.reload();
      }, 1000);
    } catch (error) {
      toast({
        variant: 'destructive',
        title: 'Erro',
        description: 'Não foi possível trocar de workspace',
      });
    }
  };

  const generateSlug = (nome: string) => {
    return nome
      .toLowerCase()
      .normalize('NFD')
      .replace(/[\u0300-\u036f]/g, '')
      .replace(/[^a-z0-9]+/g, '-')
      .replace(/^-+|-+$/g, '');
  };

  if (loading) {
    return <div>Carregando workspaces...</div>;
  }

  return (
    <div className="flex items-center gap-2">
      <Select value={currentWorkspace?.id.toString()} onValueChange={handleSwitchWorkspace}>
        <SelectTrigger className="w-[250px]">
          <SelectValue placeholder="Selecione um workspace">
            {currentWorkspace && (
              <div className="flex items-center gap-2">
                {currentWorkspace.logo_url ? (
                  <img
                    src={currentWorkspace.logo_url}
                    alt={currentWorkspace.nome}
                    className="w-5 h-5 rounded"
                  />
                ) : (
                  <Building2 className="w-5 h-5" />
                )}
                <span>{currentWorkspace.nome}</span>
                <Badge className={`ml-auto ${planoColors[currentWorkspace.plano]}`}>
                  {currentWorkspace.plano}
                </Badge>
              </div>
            )}
          </SelectValue>
        </SelectTrigger>
        <SelectContent>
          <SelectGroup>
            <SelectLabel>Seus Workspaces</SelectLabel>
            {workspaces.map((workspace) => {
              const Icon = planoIcons[workspace.plano] || Building2;
              return (
                <SelectItem key={workspace.id} value={workspace.id.toString()}>
                  <div className="flex items-center gap-2 w-full">
                    {workspace.logo_url ? (
                      <img
                        src={workspace.logo_url}
                        alt={workspace.nome}
                        className="w-5 h-5 rounded"
                      />
                    ) : (
                      <Icon className="w-5 h-5" />
                    )}
                    <span className="flex-1">{workspace.nome}</span>
                    <Badge variant="secondary" className="ml-2">
                      {workspace.plano}
                    </Badge>
                  </div>
                </SelectItem>
              );
            })}
          </SelectGroup>
        </SelectContent>
      </Select>

      <Dialog open={isCreating} onOpenChange={setIsCreating}>
        <DialogTrigger asChild>
          <Button variant="outline" size="icon">
            <Plus className="h-4 w-4" />
          </Button>
        </DialogTrigger>
        <DialogContent className="sm:max-w-[425px]">
          <DialogHeader>
            <DialogTitle>Criar Novo Workspace</DialogTitle>
            <DialogDescription>
              Crie um novo workspace para organizar seus eventos
            </DialogDescription>
          </DialogHeader>
          <div className="grid gap-4 py-4">
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="nome" className="text-right">
                Nome
              </Label>
              <Input
                id="nome"
                value={newWorkspace.nome}
                onChange={(e) => {
                  setNewWorkspace({
                    nome: e.target.value,
                    slug: generateSlug(e.target.value),
                  });
                }}
                className="col-span-3"
                placeholder="Minha Empresa"
              />
            </div>
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="slug" className="text-right">
                Slug
              </Label>
              <Input
                id="slug"
                value={newWorkspace.slug}
                onChange={(e) => setNewWorkspace({ ...newWorkspace, slug: e.target.value })}
                className="col-span-3"
                placeholder="minha-empresa"
              />
            </div>
          </div>
          <DialogFooter>
            <Button onClick={handleCreateWorkspace}>Criar Workspace</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {currentWorkspace && (
        <div className="hidden md:flex items-center gap-2 text-sm text-muted-foreground">
          <Users className="w-4 h-4" />
          <span>
            {currentWorkspace.usuarios || 0}/{currentWorkspace.limite_usuarios || '∞'}
          </span>
          <span className="mx-1">•</span>
          <span>
            {currentWorkspace.eventos || 0}/{currentWorkspace.limite_eventos || '∞'} eventos
          </span>
        </div>
      )}
    </div>
  );
}