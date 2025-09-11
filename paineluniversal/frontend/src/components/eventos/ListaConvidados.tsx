import React, { useState, useEffect } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '../ui/dialog';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Label } from '../ui/label';
import { Textarea } from '../ui/textarea';
import { Alert, AlertDescription } from '../ui/alert';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { 
  Plus, 
  Edit, 
  Trash2, 
  Copy, 
  Link, 
  Users, 
  Calendar,
  User,
  Gift,
  Share2,
  Eye,
  BarChart3
} from 'lucide-react';

interface ListaConvidado {
  id: string;
  nome: string;
  descricao: string;
  tipo: 'promoter' | 'aniversariante' | 'geral';
  promoter_responsavel?: string;
  quantidade_maxima: number;
  quantidade_atual: number;
  link_gerado: string;
  data_fechamento: string;
  ativo: boolean;
  exibir_no_app: boolean;
  vendas: number;
  checkins: number;
}

interface ListaConvidadosProps {
  eventoId: string;
  eventoNome: string;
  isOpen: boolean;
  onClose: () => void;
}

export const ListaConvidados: React.FC<ListaConvidadosProps> = ({
  eventoId,
  eventoNome,
  isOpen,
  onClose
}) => {
  const [listas, setListas] = useState<ListaConvidado[]>([]);
  const [showModal, setShowModal] = useState(false);
  const [editingLista, setEditingLista] = useState<ListaConvidado | null>(null);
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    nome: '',
    descricao: '',
    tipo: 'geral' as 'promoter' | 'aniversariante' | 'geral',
    promoter_responsavel: '',
    quantidade_maxima: 100,
    data_fechamento: '',
    exibir_no_app: true
  });

  // Carregar listas do evento
  useEffect(() => {
    if (isOpen && eventoId) {
      carregarListas();
    }
  }, [isOpen, eventoId]);

  const carregarListas = async () => {
    setLoading(true);
    try {
      const response = await fetch(`http://localhost:8000/api/eventos/${eventoId}/listas`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setListas(data.map((lista: any) => ({
          ...lista,
          id: lista.id.toString(),
          data_fechamento: lista.data_fechamento ? 
            new Date(lista.data_fechamento).toLocaleString('pt-BR') : 
            'Sem prazo'
        })));
      } else if (response.status === 404) {
        // Se não houver listas, usar array vazio
        setListas([]);
      } else {
        throw new Error('Erro ao carregar listas');
      }
    } catch (error) {
      console.error('Erro ao carregar listas:', error);
    }
    setLoading(false);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      const url = editingLista 
        ? `http://localhost:8000/api/eventos/${eventoId}/listas/${editingLista.id}`
        : `http://localhost:8000/api/eventos/${eventoId}/listas`;
      
      const method = editingLista ? 'PUT' : 'POST';
      
      const response = await fetch(url, {
        method,
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({
          nome: formData.nome,
          descricao: formData.descricao,
          tipo: formData.tipo,
          promoter_responsavel_nome: formData.promoter_responsavel,
          quantidade_maxima: formData.quantidade_maxima,
          data_fechamento: formData.data_fechamento ? new Date(formData.data_fechamento).toISOString() : null,
          exibir_no_app: formData.exibir_no_app,
          ativo: true,
          preco_entrada: 0,
          desconto_percentual: 0
        })
      });

      if (response.ok) {
        await carregarListas(); // Recarregar listas
        resetForm();
      } else {
        throw new Error('Erro ao salvar lista');
      }
    } catch (error) {
      console.error('Erro ao salvar lista:', error);
    }
    setLoading(false);
  };

  const resetForm = () => {
    setFormData({
      nome: '',
      descricao: '',
      tipo: 'geral',
      promoter_responsavel: '',
      quantidade_maxima: 100,
      data_fechamento: '',
      exibir_no_app: true
    });
    setEditingLista(null);
    setShowModal(false);
  };

  const handleEdit = (lista: ListaConvidado) => {
    setFormData({
      nome: lista.nome,
      descricao: lista.descricao,
      tipo: lista.tipo,
      promoter_responsavel: lista.promoter_responsavel || '',
      quantidade_maxima: lista.quantidade_maxima,
      data_fechamento: lista.data_fechamento,
      exibir_no_app: lista.exibir_no_app
    });
    setEditingLista(lista);
    setShowModal(true);
  };

  const handleDelete = async (id: string) => {
    if (confirm('Tem certeza que deseja excluir esta lista?')) {
      try {
        const response = await fetch(`http://localhost:8000/api/eventos/${eventoId}/listas/${id}`, {
          method: 'DELETE',
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        });
        
        if (response.ok) {
          await carregarListas(); // Recarregar listas
        } else {
          throw new Error('Erro ao excluir lista');
        }
      } catch (error) {
        console.error('Erro ao excluir lista:', error);
        alert('Erro ao excluir lista. Tente novamente.');
      }
    }
  };

  const copyLink = (link: string) => {
    navigator.clipboard.writeText(link);
    alert('Link copiado com sucesso!');
  };

  const getTipoIcon = (tipo: string) => {
    switch (tipo) {
      case 'promoter': return <Users className="h-4 w-4" />;
      case 'aniversariante': return <Gift className="h-4 w-4" />;
      default: return <User className="h-4 w-4" />;
    }
  };

  const getTipoColor = (tipo: string) => {
    switch (tipo) {
      case 'promoter': return 'bg-primary/10 text-primary';
      case 'aniversariante': return 'bg-pink-100 text-pink-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-7xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="text-2xl font-bold text-gray-800">
            Listas de Convidados - {eventoNome}
          </DialogTitle>
        </DialogHeader>

        <div className="space-y-6">
          {/* Cabeçalho com botão Adicionar */}
          <div className="flex justify-between items-center">
            <div className="text-sm text-gray-600">
              Gerencie as listas de convidados e links personalizados
            </div>
            <Button 
              onClick={() => setShowModal(true)}
              className="bg-primary hover:bg-primary/90 text-primary-foreground"
            >
              <Plus className="h-4 w-4 mr-2" />
              Adicionar lista
            </Button>
          </div>

          {/* Filtros MEEP-style */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 bg-gray-50 p-4 rounded-lg">
            <div>
              <Label className="text-sm text-gray-600">Data de fechamento</Label>
              <select className="w-full mt-1 p-2 border border-gray-300 rounded-md">
                <option>Data de fechamento</option>
              </select>
            </div>
            <div>
              <Label className="text-sm text-gray-600">Nome da lista</Label>
              <select className="w-full mt-1 p-2 border border-gray-300 rounded-md">
                <option>Digite o nome da lista</option>
              </select>
            </div>
            <div>
              <Label className="text-sm text-gray-600">Promoter responsável</Label>
              <select className="w-full mt-1 p-2 border border-gray-300 rounded-md">
                <option>Digite o nome da lista</option>
              </select>
            </div>
            <div>
              <Label className="text-sm text-gray-600">Lista de desconto</Label>
              <select className="w-full mt-1 p-2 border border-gray-300 rounded-md">
                <option>Digite o nome da lista</option>
              </select>
            </div>
          </div>

          {/* Lista de Cards */}
          <div className="space-y-4">
            {loading ? (
              <div className="text-center py-8">
                <div className="text-gray-500">Carregando listas...</div>
              </div>
            ) : listas.length === 0 ? (
              <div className="text-center py-8">
                <div className="text-gray-500">Nenhuma lista criada ainda</div>
              </div>
            ) : (
              listas.map((lista) => (
                <Card key={lista.id} className="border border-gray-200 shadow-sm">
                  <CardContent className="p-6">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-3 mb-2">
                          <div className={`inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium ${getTipoColor(lista.tipo)}`}>
                            {getTipoIcon(lista.tipo)}
                            {lista.tipo === 'promoter' ? 'Promoter' : lista.tipo === 'aniversariante' ? 'Aniversariante' : 'Geral'}
                          </div>
                          <h3 className="text-lg font-semibold text-gray-800">
                            {lista.nome}
                          </h3>
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm text-gray-600">
                          <div>
                            <span className="font-medium">Fechamento:</span> {lista.data_fechamento}
                          </div>
                          {lista.promoter_responsavel && (
                            <div>
                              <span className="font-medium">Promoter responsável:</span> {lista.promoter_responsavel}
                            </div>
                          )}
                          <div>
                            <span className="font-medium">Lista de desconto:</span> -
                          </div>
                        </div>

                        <div className="grid grid-cols-3 gap-6 mt-4 text-sm">
                          <div className="text-center">
                            <div className="text-2xl font-bold text-gray-800">{lista.quantidade_atual}</div>
                            <div className="text-gray-600">Convidados</div>
                          </div>
                          <div className="text-center">
                            <div className="text-2xl font-bold text-gray-800">{lista.vendas}</div>
                            <div className="text-gray-600">Vendas</div>
                          </div>
                          <div className="text-center">
                            <div className="text-2xl font-bold text-gray-800">{lista.checkins}</div>
                            <div className="text-gray-600">Check-in</div>
                          </div>
                        </div>
                      </div>

                      <div className="flex items-center gap-2 ml-4">
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => copyLink(lista.link_gerado)}
                          className="text-gray-600 hover:text-gray-800"
                        >
                          <Copy className="h-4 w-4" />
                        </Button>
                        <Button
                          variant="outline"
                          size="sm"
                          className="text-gray-600 hover:text-gray-800"
                        >
                          <Share2 className="h-4 w-4" />
                          Promoters
                        </Button>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleEdit(lista)}
                          className="text-gray-600 hover:text-gray-800"
                        >
                          <Edit className="h-4 w-4" />
                          Editar
                        </Button>
                        <Button
                          variant="outline"
                          size="sm"
                          className="text-gray-600 hover:text-gray-800"
                        >
                          <Users className="h-4 w-4" />
                          Convidados
                        </Button>
                      </div>
                    </div>

                    {/* Link gerado - estilo MEEP */}
                    <div className="mt-4 bg-primary text-primary-foreground p-3 rounded-lg flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <Link className="h-4 w-4" />
                        <span className="font-medium">Link: {lista.nome.split(' ')[0]}</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => copyLink(lista.link_gerado)}
                          className="text-primary-foreground hover:bg-primary/80"
                        >
                          <Copy className="h-4 w-4" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleEdit(lista)}
                          className="text-primary-foreground hover:bg-primary/80"
                        >
                          <Edit className="h-4 w-4" />
                        </Button>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))
            )}
          </div>
        </div>

        {/* Modal de Criação/Edição */}
        <Dialog open={showModal} onOpenChange={() => resetForm()}>
          <DialogContent className="max-w-2xl">
            <DialogHeader>
              <DialogTitle>
                {editingLista ? 'Editar Lista de Convidados' : 'Nova Lista de Convidados'}
              </DialogTitle>
            </DialogHeader>

            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="nome">Nome da Lista *</Label>
                  <Input
                    id="nome"
                    value={formData.nome}
                    onChange={(e) => setFormData({...formData, nome: e.target.value})}
                    placeholder="Ex: VIP Exclusivo..."
                    required
                  />
                </div>

                <div>
                  <Label htmlFor="tipo">Tipo de Lista *</Label>
                  <select
                    id="tipo"
                    value={formData.tipo}
                    onChange={(e) => setFormData({...formData, tipo: e.target.value as any})}
                    className="w-full p-2 border border-gray-300 rounded-md"
                    required
                  >
                    <option value="geral">Geral</option>
                    <option value="promoter">Promoter</option>
                    <option value="aniversariante">Aniversariante</option>
                  </select>
                </div>

                {formData.tipo === 'promoter' && (
                  <div>
                    <Label htmlFor="promoter_responsavel">Promoter Responsável</Label>
                    <Input
                      id="promoter_responsavel"
                      value={formData.promoter_responsavel}
                      onChange={(e) => setFormData({...formData, promoter_responsavel: e.target.value})}
                      placeholder="Nome do promoter"
                    />
                  </div>
                )}

                <div>
                  <Label htmlFor="quantidade_maxima">Quantidade Máxima de CPF pelo link</Label>
                  <Input
                    id="quantidade_maxima"
                    type="number"
                    min="1"
                    value={formData.quantidade_maxima}
                    onChange={(e) => setFormData({...formData, quantidade_maxima: parseInt(e.target.value) || 1})}
                  />
                </div>

                <div className="md:col-span-2">
                  <Label htmlFor="data_fechamento">Data de Fechamento</Label>
                  <Input
                    id="data_fechamento"
                    type="datetime-local"
                    value={formData.data_fechamento}
                    onChange={(e) => setFormData({...formData, data_fechamento: e.target.value})}
                  />
                </div>
              </div>

              <div>
                <Label htmlFor="descricao">Descrição da lista de convidados</Label>
                <Textarea
                  id="descricao"
                  value={formData.descricao}
                  onChange={(e) => setFormData({...formData, descricao: e.target.value})}
                  placeholder="Esta descrição aparecerá no link de convidados"
                  rows={3}
                />
              </div>

              <div className="space-y-2">
                <div className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    id="exibir_no_app"
                    checked={formData.exibir_no_app}
                    onChange={(e) => setFormData({...formData, exibir_no_app: e.target.checked})}
                    className="rounded"
                  />
                  <Label htmlFor="exibir_no_app">Lista ativa</Label>
                </div>
                
                <div className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    id="lista_fixa"
                    className="rounded"
                  />
                  <Label htmlFor="lista_fixa">Lista fixa para todos os eventos</Label>
                </div>
              </div>

              <div className="flex justify-end space-x-2 pt-4">
                <Button
                  type="button"
                  variant="outline"
                  onClick={resetForm}
                  disabled={loading}
                >
                  Cancelar
                </Button>
                <Button
                  type="submit"
                  disabled={loading}
                  className="bg-primary hover:bg-primary/90"
                >
                  {loading ? 'Salvando...' : (editingLista ? 'Salvar' : 'Criar Lista')}
                </Button>
              </div>
            </form>
          </DialogContent>
        </Dialog>
      </DialogContent>
    </Dialog>
  );
};

export default ListaConvidados;
