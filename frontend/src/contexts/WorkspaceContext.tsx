import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import api from '@/lib/api';
import { useToast } from '@/hooks/use-toast';

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

interface WorkspaceContextType {
  currentWorkspace: Workspace | null;
  workspaces: Workspace[];
  loading: boolean;
  switchWorkspace: (workspaceId: number) => Promise<void>;
  createWorkspace: (data: { nome: string; slug: string }) => Promise<Workspace>;
  updateWorkspace: (workspaceId: number, data: Partial<Workspace>) => Promise<void>;
  refreshWorkspaces: () => Promise<void>;
  canCreateResource: (resourceType: 'usuario' | 'evento' | 'participante') => boolean;
}

const WorkspaceContext = createContext<WorkspaceContextType | undefined>(undefined);

export const useWorkspace = () => {
  const context = useContext(WorkspaceContext);
  if (!context) {
    throw new Error('useWorkspace deve ser usado dentro de WorkspaceProvider');
  }
  return context;
};

interface WorkspaceProviderProps {
  children: ReactNode;
}

export const WorkspaceProvider: React.FC<WorkspaceProviderProps> = ({ children }) => {
  const [currentWorkspace, setCurrentWorkspace] = useState<Workspace | null>(null);
  const [workspaces, setWorkspaces] = useState<Workspace[]>([]);
  const [loading, setLoading] = useState(true);
  const { toast } = useToast();

  useEffect(() => {
    loadWorkspaces();
  }, []);

  const loadWorkspaces = async () => {
    try {
      setLoading(true);
      
      // Carregar lista de workspaces
      const workspacesResponse = await api.get('/api/workspaces');
      setWorkspaces(workspacesResponse.data);
      
      // Carregar workspace atual
      try {
        const currentResponse = await api.get('/api/workspaces/current');
        setCurrentWorkspace(currentResponse.data);
        
        // Adicionar workspace_id no header para todas as requisições
        if (currentResponse.data) {
          api.defaults.headers.common['X-Workspace-ID'] = currentResponse.data.id;
        }
      } catch (error) {
        // Se não houver workspace atual, usar o primeiro da lista
        if (workspacesResponse.data.length > 0) {
          await switchWorkspace(workspacesResponse.data[0].id);
        }
      }
    } catch (error) {
      console.error('Erro ao carregar workspaces:', error);
      // Em caso de erro, criar workspace padrão
      try {
        const defaultWorkspace = await createWorkspace({
          nome: 'Meu Workspace',
          slug: 'meu-workspace',
        });
        setCurrentWorkspace(defaultWorkspace);
        setWorkspaces([defaultWorkspace]);
      } catch (createError) {
        console.error('Erro ao criar workspace padrão:', createError);
      }
    } finally {
      setLoading(false);
    }
  };

  const refreshWorkspaces = async () => {
    await loadWorkspaces();
  };

  const switchWorkspace = async (workspaceId: number) => {
    try {
      const response = await api.post(`/api/workspaces/${workspaceId}/switch`);
      setCurrentWorkspace(response.data);
      
      // Atualizar header para futuras requisições
      api.defaults.headers.common['X-Workspace-ID'] = workspaceId;
      
      toast({
        title: 'Workspace alterado',
        description: `Você está agora em ${response.data.nome}`,
      });
      
      // Recarregar dados do novo workspace
      // Pequeno delay para garantir que o backend processou a mudança
      setTimeout(() => {
        window.location.reload();
      }, 500);
    } catch (error: any) {
      toast({
        variant: 'destructive',
        title: 'Erro ao trocar workspace',
        description: error.response?.data?.detail || 'Erro desconhecido',
      });
      throw error;
    }
  };

  const createWorkspace = async (data: { nome: string; slug: string }): Promise<Workspace> => {
    try {
      const response = await api.post('/api/workspaces', data);
      const newWorkspace = response.data;
      
      // Adicionar à lista de workspaces
      setWorkspaces([...workspaces, newWorkspace]);
      
      // Se for o primeiro workspace, definir como atual
      if (!currentWorkspace) {
        setCurrentWorkspace(newWorkspace);
        api.defaults.headers.common['X-Workspace-ID'] = newWorkspace.id;
      }
      
      toast({
        title: 'Workspace criado',
        description: `${data.nome} foi criado com sucesso`,
      });
      
      return newWorkspace;
    } catch (error: any) {
      toast({
        variant: 'destructive',
        title: 'Erro ao criar workspace',
        description: error.response?.data?.detail || 'Erro desconhecido',
      });
      throw error;
    }
  };

  const updateWorkspace = async (workspaceId: number, data: Partial<Workspace>) => {
    try {
      const response = await api.put(`/api/workspaces/${workspaceId}`, data);
      const updatedWorkspace = response.data;
      
      // Atualizar na lista
      setWorkspaces(workspaces.map(w => w.id === workspaceId ? updatedWorkspace : w));
      
      // Se for o workspace atual, atualizar também
      if (currentWorkspace?.id === workspaceId) {
        setCurrentWorkspace(updatedWorkspace);
      }
      
      toast({
        title: 'Workspace atualizado',
        description: 'As alterações foram salvas com sucesso',
      });
    } catch (error: any) {
      toast({
        variant: 'destructive',
        title: 'Erro ao atualizar workspace',
        description: error.response?.data?.detail || 'Erro desconhecido',
      });
      throw error;
    }
  };

  const canCreateResource = (resourceType: 'usuario' | 'evento' | 'participante'): boolean => {
    if (!currentWorkspace) return false;
    
    // Plano enterprise não tem limites
    if (currentWorkspace.plano === 'enterprise') return true;
    
    // Verificar limites baseado no tipo de recurso
    switch (resourceType) {
      case 'usuario':
        if (!currentWorkspace.limite_usuarios) return true;
        // Aqui precisaríamos verificar quantos usuários já existem
        return true; // Por enquanto, sempre permite
        
      case 'evento':
        if (!currentWorkspace.limite_eventos) return true;
        // Aqui precisaríamos verificar quantos eventos já existem
        return true; // Por enquanto, sempre permite
        
      case 'participante':
        if (!currentWorkspace.limite_participantes) return true;
        // Aqui precisaríamos verificar quantos participantes já existem
        return true; // Por enquanto, sempre permite
        
      default:
        return false;
    }
  };

  const value: WorkspaceContextType = {
    currentWorkspace,
    workspaces,
    loading,
    switchWorkspace,
    createWorkspace,
    updateWorkspace,
    refreshWorkspaces,
    canCreateResource,
  };

  return (
    <WorkspaceContext.Provider value={value}>
      {children}
    </WorkspaceContext.Provider>
  );
};