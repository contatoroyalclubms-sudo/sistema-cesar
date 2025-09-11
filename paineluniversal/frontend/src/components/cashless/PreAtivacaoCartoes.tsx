import React, { useState, useEffect } from 'react';
import {
  CreditCard, Link2, Search, Calendar, User, Tag,
  AlertTriangle, Check, X, RefreshCw, Download, Filter
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
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '../ui/select';
import { toast } from 'sonner';
import { api } from '@/lib/api';

interface PreAtivacaoCartao {
  id: string;
  tag: string;
  vinculado_por?: string;
  vinculado_em?: string;
  cliente_nome?: string;
  cliente_cpf?: string;
  status: 'pendente' | 'vinculado' | 'ativo' | 'cancelado';
  created_at: string;
}

// MEEP-inspired mock data baseado na engenharia reversa
const mockPreAtivacoes: PreAtivacaoCartao[] = [
  {
    id: '1',
    tag: 'TAG001234',
    vinculado_por: 'João Operador',
    vinculado_em: '2025-09-10T10:30:00Z',
    cliente_nome: 'BIANCA CAROLINE',
    cliente_cpf: '12345678901',
    status: 'vinculado',
    created_at: '2025-09-10T09:00:00Z'
  },
  {
    id: '2',
    tag: 'TAG005678',
    vinculado_por: 'Maria Santos',
    vinculado_em: '2025-09-10T11:15:00Z',
    cliente_nome: 'FELIPE NICHOLAS',
    cliente_cpf: '98765432109',
    status: 'ativo',
    created_at: '2025-09-10T10:00:00Z'
  },
  {
    id: '3',
    tag: 'TAG009012',
    status: 'pendente',
    created_at: '2025-09-10T08:45:00Z'
  }
];

const PreAtivacaoCartoes: React.FC = () => {
  const [preAtivacoes, setPreAtivacoes] = useState<PreAtivacaoCartao[]>(mockPreAtivacoes);
  const [loading, setLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterStatus, setFilterStatus] = useState<string>('todos');
  const [selectedPreAtivacao, setSelectedPreAtivacao] = useState<PreAtivacaoCartao | null>(null);
  const [showVinculacao, setShowVinculacao] = useState(false);
  
  // Estados para vinculação
  const [vinculacaoData, setVinculacaoData] = useState({
    tag: '',
    vinculado_por: '',
    vinculado_em: new Date().toISOString().split('T')[0]
  });

  // Carregar pré-ativações (MEEP-style)
  const loadPreAtivacoes = async () => {
    setLoading(true);
    try {
      // TODO: Implementar chamada real para a API
      // const response = await api.get('/cashless/pre-ativacao');
      // setPreAtivacoes(response.data);
      
      // Simulando carregamento MEEP-style
      setTimeout(() => {
        setPreAtivacoes(mockPreAtivacoes);
        setLoading(false);
      }, 800);
    } catch (error) {
      console.error('Erro ao carregar pré-ativações:', error);
      toast.error('Erro ao carregar vinculações de cartões');
      setLoading(false);
    }
  };

  // Vincular cartão (baseado no sistema MEEP)
  const vincularCartao = async () => {
    if (!selectedPreAtivacao) return;
    
    setLoading(true);
    try {
      // TODO: Implementar chamada real para API
      // await api.post(`/cashless/pre-ativacao/${selectedPreAtivacao.id}/vincular`, vinculacaoData);
      
      const updatedPreAtivacoes = preAtivacoes.map(item =>
        item.id === selectedPreAtivacao.id
          ? {
              ...item,
              ...vinculacaoData,
              status: 'vinculado' as const,
              vinculado_em: new Date().toISOString()
            }
          : item
      );
      
      setPreAtivacoes(updatedPreAtivacoes);
      setShowVinculacao(false);
      setVinculacaoData({ tag: '', vinculado_por: '', vinculado_em: new Date().toISOString().split('T')[0] });
      toast.success('Cartão vinculado com sucesso!');
      setLoading(false);
    } catch (error) {
      console.error('Erro ao vincular cartão:', error);
      toast.error('Erro ao vincular cartão');
      setLoading(false);
    }
  };

  useEffect(() => {
    loadPreAtivacoes();
  }, []);

  // Filtrar pré-ativações
  const filteredPreAtivacoes = preAtivacoes.filter(item => {
    const matchesSearch = 
      item.tag.toLowerCase().includes(searchTerm.toLowerCase()) ||
      item.vinculado_por?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      item.cliente_nome?.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesStatus = filterStatus === 'todos' || item.status === filterStatus;
    
    return matchesSearch && matchesStatus;
  });

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'vinculado': return 'bg-blue-100 text-blue-800';
      case 'ativo': return 'bg-green-100 text-green-800';
      case 'pendente': return 'bg-yellow-100 text-yellow-800';
      case 'cancelado': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'vinculado': return <Link2 className="h-3 w-3" />;
      case 'ativo': return <Check className="h-3 w-3" />;
      case 'pendente': return <AlertTriangle className="h-3 w-3" />;
      case 'cancelado': return <X className="h-3 w-3" />;
      default: return null;
    }
  };

  return (
    <div className="flex-1 space-y-4 p-4 pt-6">
      {/* Header MEEP-inspired */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold tracking-tight">Pré-ativação de Cartões</h2>
          <p className="text-muted-foreground">
            Gerencie a vinculação de cartões cashless - Sistema baseado no MEEP
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <Button onClick={() => setShowVinculacao(true)}>
            <Link2 className="mr-2 h-4 w-4" />
            Vincular Cartões
          </Button>
          <Button variant="outline" onClick={loadPreAtivacoes}>
            <RefreshCw className="mr-2 h-4 w-4" />
            Atualizar
          </Button>
        </div>
      </div>

      {/* Filtros avançados MEEP-style */}
      <Card>
        <CardContent className="pt-6">
          <div className="grid gap-4 md:grid-cols-3">
            <div className="space-y-2">
              <Label htmlFor="search-tag">Insira a tag</Label>
              <div className="relative">
                <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                <Input
                  id="search-tag"
                  placeholder="Buscar por tag, nome ou usuário..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>

            <div className="space-y-2">
              <Label>Vinculado por (Nome do usuário)</Label>
              <Select value={filterStatus} onValueChange={setFilterStatus}>
                <SelectTrigger>
                  <SelectValue placeholder="Filtrar por status" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="todos">Todos os status</SelectItem>
                  <SelectItem value="pendente">Pendente</SelectItem>
                  <SelectItem value="vinculado">Vinculado</SelectItem>
                  <SelectItem value="ativo">Ativo</SelectItem>
                  <SelectItem value="cancelado">Cancelado</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label>Vinculado em</Label>
              <Input
                type="date"
                placeholder="DD/MM/AAAA"
                className="text-muted-foreground"
              />
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Conteúdo principal */}
      {filteredPreAtivacoes.length === 0 ? (
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-12">
            <div className="text-center space-y-4">
              <div className="mx-auto w-12 h-12 bg-gray-100 rounded-full flex items-center justify-center">
                <CreditCard className="h-6 w-6 text-gray-600" />
              </div>
              <div>
                <h3 className="text-lg font-medium">Seu estabelecimento ainda não possui vínculo de cartões</h3>
                <p className="text-muted-foreground">
                  Comece vinculando cartões para habilitar o sistema cashless
                </p>
              </div>
              <Button onClick={() => setShowVinculacao(true)}>
                <Link2 className="mr-2 h-4 w-4" />
                Vincular Primeiro Cartão
              </Button>
            </div>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-4">
          {/* Tabela de pré-ativações */}
          <Card>
            <CardHeader>
              <CardTitle>Histórico de Vinculações</CardTitle>
              <CardDescription>
                {filteredPreAtivacoes.length} vinculação(ões) encontrada(s)
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {filteredPreAtivacoes.map((item) => (
                  <div key={item.id} className="flex items-center justify-between p-4 border rounded-lg hover:bg-gray-50">
                    <div className="flex items-center space-x-4">
                      <div className="p-2 bg-blue-100 rounded-full">
                        <Tag className="h-4 w-4 text-blue-600" />
                      </div>
                      
                      <div className="space-y-1">
                        <div className="flex items-center space-x-2">
                          <p className="font-medium">{item.tag}</p>
                          <Badge className={getStatusColor(item.status)}>
                            {getStatusIcon(item.status)}
                            <span className="ml-1 capitalize">{item.status}</span>
                          </Badge>
                        </div>
                        
                        {item.cliente_nome && (
                          <p className="text-sm text-muted-foreground">
                            Cliente: {item.cliente_nome}
                          </p>
                        )}
                        
                        {item.vinculado_por && (
                          <p className="text-sm text-muted-foreground">
                            Vinculado por: {item.vinculado_por}
                          </p>
                        )}
                      </div>
                    </div>
                    
                    <div className="text-right space-y-1">
                      {item.vinculado_em && (
                        <p className="text-sm font-medium">
                          {new Date(item.vinculado_em).toLocaleDateString('pt-BR')}
                        </p>
                      )}
                      <p className="text-xs text-muted-foreground">
                        Criado: {new Date(item.created_at).toLocaleDateString('pt-BR')}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Estatísticas */}
          <div className="grid gap-4 md:grid-cols-4">
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-base">Total de Tags</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-2xl font-bold text-blue-600">
                  {preAtivacoes.length}
                </p>
              </CardContent>
            </Card>
            
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-base">Vinculados</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-2xl font-bold text-green-600">
                  {preAtivacoes.filter(item => item.status === 'vinculado' || item.status === 'ativo').length}
                </p>
              </CardContent>
            </Card>
            
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-base">Pendentes</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-2xl font-bold text-yellow-600">
                  {preAtivacoes.filter(item => item.status === 'pendente').length}
                </p>
              </CardContent>
            </Card>
            
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-base">Taxa de Vinculação</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-2xl font-bold text-purple-600">
                  {preAtivacoes.length > 0 
                    ? Math.round((preAtivacoes.filter(item => item.status !== 'pendente').length / preAtivacoes.length) * 100)
                    : 0
                  }%
                </p>
              </CardContent>
            </Card>
          </div>
        </div>
      )}

      {/* Modal Vinculação */}
      <Dialog open={showVinculacao} onOpenChange={setShowVinculacao}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle>Vincular Cartão</DialogTitle>
            <DialogDescription>
              Configure a vinculação de um novo cartão cashless
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <Label htmlFor="tag">Tag do Cartão</Label>
              <Input
                id="tag"
                value={vinculacaoData.tag}
                onChange={(e) => setVinculacaoData({...vinculacaoData, tag: e.target.value})}
                placeholder="Ex: TAG001234"
              />
            </div>
            
            <div>
              <Label htmlFor="vinculado_por">Vinculado por</Label>
              <Input
                id="vinculado_por"
                value={vinculacaoData.vinculado_por}
                onChange={(e) => setVinculacaoData({...vinculacaoData, vinculado_por: e.target.value})}
                placeholder="Nome do operador"
              />
            </div>
            
            <div>
              <Label htmlFor="vinculado_em">Data de Vinculação</Label>
              <Input
                id="vinculado_em"
                type="date"
                value={vinculacaoData.vinculado_em}
                onChange={(e) => setVinculacaoData({...vinculacaoData, vinculado_em: e.target.value})}
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowVinculacao(false)}>
              Cancelar
            </Button>
            <Button 
              onClick={vincularCartao} 
              disabled={loading || !vinculacaoData.tag || !vinculacaoData.vinculado_por}
            >
              {loading ? 'Vinculando...' : 'Vincular'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default PreAtivacaoCartoes;