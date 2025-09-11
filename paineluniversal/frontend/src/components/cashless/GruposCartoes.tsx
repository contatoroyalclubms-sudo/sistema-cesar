import React, { useState, useEffect } from 'react';
import {
  Users, Plus, Search, Edit3, Trash2, CreditCard,
  RefreshCw, Settings, Tag, Eye, MoreVertical
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
import { Label } from '../ui/label';
import { Badge } from '../ui/badge';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '../ui/dialog';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '../ui/dropdown-menu';
import { toast } from 'sonner';
import { api } from '@/lib/api';

interface GrupoCartao {
  id: string;
  nome: string;
  descricao?: string;
  cor?: string;
  cartoes_count: number;
  created_at: string;
  updated_at?: string;
  ativo: boolean;
}

// MEEP-inspired mock data - baseado na engenharia reversa
const mockGrupos: GrupoCartao[] = [
  {
    id: '1',
    nome: 'VIP Premium',
    descricao: 'Grupo exclusivo para clientes VIP com benefícios especiais',
    cor: '#8B5CF6',
    cartoes_count: 45,
    created_at: '2025-09-01T10:00:00Z',
    updated_at: '2025-09-10T08:30:00Z',
    ativo: true
  },
  {
    id: '2',
    nome: 'Sócios Gold',
    descricao: 'Cartões para sócios com acesso diferenciado',
    cor: '#F59E0B',
    cartoes_count: 128,
    created_at: '2025-09-05T14:20:00Z',
    ativo: true
  },
  {
    id: '3',
    nome: 'Staff',
    descricao: 'Equipe interna e colaboradores',
    cor: '#10B981',
    cartoes_count: 12,
    created_at: '2025-09-08T09:15:00Z',
    ativo: true
  },
  {
    id: '4',
    nome: 'Promoção Especial',
    descricao: 'Grupo temporário para campanha promocional',
    cor: '#EF4444',
    cartoes_count: 67,
    created_at: '2025-08-20T16:45:00Z',
    ativo: false
  }
];

const GruposCartoes: React.FC = () => {
  const [grupos, setGrupos] = useState<GrupoCartao[]>(mockGrupos);
  const [loading, setLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedGrupo, setSelectedGrupo] = useState<GrupoCartao | null>(null);
  const [showNovoGrupo, setShowNovoGrupo] = useState(false);
  const [showEditGrupo, setShowEditGrupo] = useState(false);
  
  // Estados para formulários
  const [grupoData, setGrupoData] = useState({
    nome: '',
    descricao: '',
    cor: '#8B5CF6'
  });

  // Carregar grupos (MEEP-style)
  const loadGrupos = async () => {
    setLoading(true);
    try {
      // TODO: Implementar chamada real para a API
      // const response = await api.get('/cashless/grupos');
      // setGrupos(response.data);
      
      // Simulando carregamento MEEP-style
      setTimeout(() => {
        setGrupos(mockGrupos);
        setLoading(false);
      }, 600);
    } catch (error) {
      console.error('Erro ao carregar grupos:', error);
      toast.error('Erro ao carregar grupos de cartões');
      setLoading(false);
    }
  };

  // Criar novo grupo
  const criarGrupo = async () => {
    if (!grupoData.nome.trim()) {
      toast.error('Nome do grupo é obrigatório');
      return;
    }

    setLoading(true);
    try {
      // TODO: Implementar chamada real para API
      // const response = await api.post('/cashless/grupos', grupoData);
      
      const novoGrupo: GrupoCartao = {
        id: Date.now().toString(),
        ...grupoData,
        cartoes_count: 0,
        created_at: new Date().toISOString(),
        ativo: true
      };
      
      setGrupos([...grupos, novoGrupo]);
      setGrupoData({ nome: '', descricao: '', cor: '#8B5CF6' });
      setShowNovoGrupo(false);
      toast.success('Grupo criado com sucesso!');
      setLoading(false);
    } catch (error) {
      console.error('Erro ao criar grupo:', error);
      toast.error('Erro ao criar grupo de cartões');
      setLoading(false);
    }
  };

  // Editar grupo
  const editarGrupo = async () => {
    if (!selectedGrupo || !grupoData.nome.trim()) return;

    setLoading(true);
    try {
      // TODO: Implementar chamada real para API
      // await api.put(`/cashless/grupos/${selectedGrupo.id}`, grupoData);
      
      const gruposAtualizados = grupos.map(grupo =>
        grupo.id === selectedGrupo.id
          ? { ...grupo, ...grupoData, updated_at: new Date().toISOString() }
          : grupo
      );
      
      setGrupos(gruposAtualizados);
      setShowEditGrupo(false);
      setSelectedGrupo(null);
      setGrupoData({ nome: '', descricao: '', cor: '#8B5CF6' });
      toast.success('Grupo atualizado com sucesso!');
      setLoading(false);
    } catch (error) {
      console.error('Erro ao editar grupo:', error);
      toast.error('Erro ao atualizar grupo');
      setLoading(false);
    }
  };

  // Excluir grupo
  const excluirGrupo = async (grupo: GrupoCartao) => {
    if (grupo.cartoes_count > 0) {
      toast.error('Não é possível excluir grupo com cartões vinculados');
      return;
    }

    setLoading(true);
    try {
      // TODO: Implementar chamada real para API
      // await api.delete(`/cashless/grupos/${grupo.id}`);
      
      const gruposAtualizados = grupos.filter(g => g.id !== grupo.id);
      setGrupos(gruposAtualizados);
      toast.success('Grupo excluído com sucesso!');
      setLoading(false);
    } catch (error) {
      console.error('Erro ao excluir grupo:', error);
      toast.error('Erro ao excluir grupo');
      setLoading(false);
    }
  };

  // Toggle ativo/inativo
  const toggleGrupoStatus = async (grupo: GrupoCartao) => {
    setLoading(true);
    try {
      // TODO: Implementar chamada real para API
      // await api.patch(`/cashless/grupos/${grupo.id}/toggle-status`);
      
      const gruposAtualizados = grupos.map(g =>
        g.id === grupo.id ? { ...g, ativo: !g.ativo } : g
      );
      
      setGrupos(gruposAtualizados);
      toast.success(`Grupo ${!grupo.ativo ? 'ativado' : 'desativado'} com sucesso!`);
      setLoading(false);
    } catch (error) {
      console.error('Erro ao alterar status do grupo:', error);
      toast.error('Erro ao alterar status do grupo');
      setLoading(false);
    }
  };

  useEffect(() => {
    loadGrupos();
  }, []);

  // Filtrar grupos por busca
  const filteredGrupos = grupos.filter(grupo =>
    grupo.nome.toLowerCase().includes(searchTerm.toLowerCase()) ||
    grupo.descricao?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  // Preparar dados para edição
  const handleEditClick = (grupo: GrupoCartao) => {
    setSelectedGrupo(grupo);
    setGrupoData({
      nome: grupo.nome,
      descricao: grupo.descricao || '',
      cor: grupo.cor || '#8B5CF6'
    });
    setShowEditGrupo(true);
  };

  const cores = [
    { value: '#8B5CF6', name: 'Roxo' },
    { value: '#F59E0B', name: 'Dourado' },
    { value: '#10B981', name: 'Verde' },
    { value: '#EF4444', name: 'Vermelho' },
    { value: '#3B82F6', name: 'Azul' },
    { value: '#F97316', name: 'Laranja' },
    { value: '#06B6D4', name: 'Ciano' },
    { value: '#84CC16', name: 'Lima' }
  ];

  return (
    <div className="flex-1 space-y-4 p-4 pt-6">
      {/* Header MEEP-inspired */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold tracking-tight">Grupos de Cartões</h2>
          <p className="text-muted-foreground">
            Organize cartões cashless em grupos para melhor gestão
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <Button onClick={() => setShowNovoGrupo(true)}>
            <Plus className="mr-2 h-4 w-4" />
            Adicionar Grupo
          </Button>
          <Button variant="outline" onClick={loadGrupos}>
            <RefreshCw className="mr-2 h-4 w-4" />
            Atualizar
          </Button>
        </div>
      </div>

      {/* Busca */}
      <Card>
        <CardContent className="pt-6">
          <div className="relative max-w-sm">
            <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Buscar pelo nome do grupo..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10"
            />
          </div>
        </CardContent>
      </Card>

      {/* Conteúdo principal */}
      {filteredGrupos.length === 0 && searchTerm === '' ? (
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-12">
            <div className="text-center space-y-4">
              <div className="mx-auto w-12 h-12 bg-gray-100 rounded-full flex items-center justify-center">
                <Users className="h-6 w-6 text-gray-600" />
              </div>
              <div>
                <h3 className="text-lg font-medium">
                  Ops, parece que você ainda não tem nenhum grupo de cartão para ser mostrado aqui!
                </h3>
                <p className="text-muted-foreground">
                  Crie seu primeiro grupo para organizar os cartões cashless
                </p>
              </div>
              <Button onClick={() => setShowNovoGrupo(true)}>
                <Plus className="mr-2 h-4 w-4" />
                Criar Primeiro Grupo
              </Button>
            </div>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-4">
          {/* Grid de grupos */}
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {filteredGrupos.map((grupo) => (
              <Card key={grupo.id} className="hover:shadow-lg transition-shadow">
                <CardHeader className="pb-3">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <div 
                        className="w-4 h-4 rounded-full"
                        style={{ backgroundColor: grupo.cor }}
                      />
                      <CardTitle className="text-lg">{grupo.nome}</CardTitle>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Badge variant={grupo.ativo ? 'default' : 'secondary'}>
                        {grupo.ativo ? 'Ativo' : 'Inativo'}
                      </Badge>
                      <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                          <Button variant="ghost" size="sm">
                            <MoreVertical className="h-4 w-4" />
                          </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="end">
                          <DropdownMenuItem onClick={() => handleEditClick(grupo)}>
                            <Edit3 className="mr-2 h-4 w-4" />
                            Editar
                          </DropdownMenuItem>
                          <DropdownMenuItem onClick={() => toggleGrupoStatus(grupo)}>
                            <Settings className="mr-2 h-4 w-4" />
                            {grupo.ativo ? 'Desativar' : 'Ativar'}
                          </DropdownMenuItem>
                          {grupo.cartoes_count === 0 && (
                            <DropdownMenuItem 
                              onClick={() => excluirGrupo(grupo)}
                              className="text-red-600"
                            >
                              <Trash2 className="mr-2 h-4 w-4" />
                              Excluir
                            </DropdownMenuItem>
                          )}
                        </DropdownMenuContent>
                      </DropdownMenu>
                    </div>
                  </div>
                  {grupo.descricao && (
                    <CardDescription className="mt-2">
                      {grupo.descricao}
                    </CardDescription>
                  )}
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      <CreditCard className="h-4 w-4 text-muted-foreground" />
                      <span className="text-sm text-muted-foreground">Cartões:</span>
                    </div>
                    <span className="text-2xl font-bold text-blue-600">
                      {grupo.cartoes_count}
                    </span>
                  </div>
                  
                  <div className="flex items-center justify-between text-sm text-muted-foreground">
                    <span>Criado em:</span>
                    <span>{new Date(grupo.created_at).toLocaleDateString('pt-BR')}</span>
                  </div>
                  
                  {grupo.updated_at && (
                    <div className="flex items-center justify-between text-sm text-muted-foreground">
                      <span>Atualizado:</span>
                      <span>{new Date(grupo.updated_at).toLocaleDateString('pt-BR')}</span>
                    </div>
                  )}
                </CardContent>
              </Card>
            ))}
          </div>

          {/* Estatísticas */}
          <div className="grid gap-4 md:grid-cols-4">
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-base">Total de Grupos</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-2xl font-bold text-blue-600">
                  {grupos.length}
                </p>
              </CardContent>
            </Card>
            
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-base">Grupos Ativos</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-2xl font-bold text-green-600">
                  {grupos.filter(g => g.ativo).length}
                </p>
              </CardContent>
            </Card>
            
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-base">Total de Cartões</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-2xl font-bold text-purple-600">
                  {grupos.reduce((total, grupo) => total + grupo.cartoes_count, 0)}
                </p>
              </CardContent>
            </Card>
            
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-base">Média por Grupo</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-2xl font-bold text-orange-600">
                  {grupos.length > 0 
                    ? Math.round(grupos.reduce((total, grupo) => total + grupo.cartoes_count, 0) / grupos.length)
                    : 0
                  }
                </p>
              </CardContent>
            </Card>
          </div>
        </div>
      )}

      {/* Modal Novo Grupo */}
      <Dialog open={showNovoGrupo} onOpenChange={setShowNovoGrupo}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Novo Grupo de Cartões</DialogTitle>
            <DialogDescription>
              Crie um novo grupo para organizar seus cartões cashless
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <Label htmlFor="nome">Nome do Grupo *</Label>
              <Input
                id="nome"
                value={grupoData.nome}
                onChange={(e) => setGrupoData({...grupoData, nome: e.target.value})}
                placeholder="Ex: VIP Premium"
              />
            </div>
            
            <div>
              <Label htmlFor="descricao">Descrição</Label>
              <Input
                id="descricao"
                value={grupoData.descricao}
                onChange={(e) => setGrupoData({...grupoData, descricao: e.target.value})}
                placeholder="Descrição opcional do grupo"
              />
            </div>
            
            <div>
              <Label>Cor do Grupo</Label>
              <div className="flex flex-wrap gap-2 mt-2">
                {cores.map((cor) => (
                  <button
                    key={cor.value}
                    type="button"
                    className={`w-8 h-8 rounded-full border-2 ${
                      grupoData.cor === cor.value ? 'border-gray-400' : 'border-gray-200'
                    }`}
                    style={{ backgroundColor: cor.value }}
                    onClick={() => setGrupoData({...grupoData, cor: cor.value})}
                    title={cor.name}
                  />
                ))}
              </div>
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowNovoGrupo(false)}>
              Cancelar
            </Button>
            <Button onClick={criarGrupo} disabled={loading || !grupoData.nome.trim()}>
              {loading ? 'Criando...' : 'Criar Grupo'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Modal Editar Grupo */}
      <Dialog open={showEditGrupo} onOpenChange={setShowEditGrupo}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Editar Grupo de Cartões</DialogTitle>
            <DialogDescription>
              Atualize as informações do grupo selecionado
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <Label htmlFor="edit_nome">Nome do Grupo *</Label>
              <Input
                id="edit_nome"
                value={grupoData.nome}
                onChange={(e) => setGrupoData({...grupoData, nome: e.target.value})}
                placeholder="Ex: VIP Premium"
              />
            </div>
            
            <div>
              <Label htmlFor="edit_descricao">Descrição</Label>
              <Input
                id="edit_descricao"
                value={grupoData.descricao}
                onChange={(e) => setGrupoData({...grupoData, descricao: e.target.value})}
                placeholder="Descrição opcional do grupo"
              />
            </div>
            
            <div>
              <Label>Cor do Grupo</Label>
              <div className="flex flex-wrap gap-2 mt-2">
                {cores.map((cor) => (
                  <button
                    key={cor.value}
                    type="button"
                    className={`w-8 h-8 rounded-full border-2 ${
                      grupoData.cor === cor.value ? 'border-gray-400' : 'border-gray-200'
                    }`}
                    style={{ backgroundColor: cor.value }}
                    onClick={() => setGrupoData({...grupoData, cor: cor.value})}
                    title={cor.name}
                  />
                ))}
              </div>
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowEditGrupo(false)}>
              Cancelar
            </Button>
            <Button onClick={editarGrupo} disabled={loading || !grupoData.nome.trim()}>
              {loading ? 'Salvando...' : 'Salvar Alterações'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default GruposCartoes;