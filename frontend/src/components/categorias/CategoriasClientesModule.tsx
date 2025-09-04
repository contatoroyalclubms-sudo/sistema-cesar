import React, { useState, useEffect } from 'react';
import { Plus, Edit, Trash2, Users, Tag, Search } from 'lucide-react';
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
import { Switch } from '../ui/switch';
import { Badge } from '../ui/badge';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '../ui/dialog';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '../ui/table';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '../ui/select';
import { toast } from 'sonner';
import api from '../../lib/api';

interface CategoriaCliente {
  id: number;
  nome: string;
  descricao: string;
  icone: string;
  cor: string;
  lista_convidado: boolean;
  desconto_padrao: number;
  beneficios: any;
  ordem: number;
  ativo: boolean;
  total_clientes?: number;
  criado_em: string;
  atualizado_em?: string;
}

const CategoriasClientesModule: React.FC = () => {
  const [categorias, setCategorias] = useState<CategoriaCliente[]>([]);
  const [loading, setLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [showModal, setShowModal] = useState(false);
  const [editingCategoria, setEditingCategoria] = useState<CategoriaCliente | null>(null);
  const [formData, setFormData] = useState({
    nome: '',
    descricao: '',
    icone: 'tag',
    cor: '#3B82F6',
    lista_convidado: false,
    desconto_padrao: 0,
    beneficios: {},
    ordem: 0,
    ativo: true
  });

  const iconesDisponiveis = [
    'tag', 'star', 'crown', 'diamond', 'heart', 'users',
    'gift', 'trophy', 'award', 'medal', 'shield', 'zap'
  ];

  const coresDisponiveis = [
    '#3B82F6', '#EF4444', '#10B981', '#F59E0B', '#8B5CF6',
    '#EC4899', '#14B8A6', '#F97316', '#6366F1', '#84CC16'
  ];

  useEffect(() => {
    fetchCategorias();
  }, []);

  const fetchCategorias = async () => {
    setLoading(true);
    try {
      const response = await api.get('/categorias-clientes');
      setCategorias(response.data);
    } catch (error) {
      console.error('Erro ao buscar categorias:', error);
      toast.error('Erro ao carregar categorias');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    try {
      if (editingCategoria) {
        await api.put(`/categorias-clientes/${editingCategoria.id}`, formData);
        toast.success('Categoria atualizada com sucesso!');
      } else {
        await api.post('/categorias-clientes', formData);
        toast.success('Categoria criada com sucesso!');
      }
      
      setShowModal(false);
      resetForm();
      fetchCategorias();
    } catch (error: any) {
      console.error('Erro ao salvar categoria:', error);
      toast.error(error.response?.data?.detail || 'Erro ao salvar categoria');
    }
  };

  const handleEdit = (categoria: CategoriaCliente) => {
    setEditingCategoria(categoria);
    setFormData({
      nome: categoria.nome,
      descricao: categoria.descricao || '',
      icone: categoria.icone || 'tag',
      cor: categoria.cor || '#3B82F6',
      lista_convidado: categoria.lista_convidado,
      desconto_padrao: categoria.desconto_padrao || 0,
      beneficios: categoria.beneficios || {},
      ordem: categoria.ordem,
      ativo: categoria.ativo
    });
    setShowModal(true);
  };

  const handleDelete = async (id: number) => {
    if (!confirm('Tem certeza que deseja desativar esta categoria?')) return;
    
    try {
      await api.delete(`/categorias-clientes/${id}`);
      toast.success('Categoria desativada com sucesso!');
      fetchCategorias();
    } catch (error: any) {
      console.error('Erro ao desativar categoria:', error);
      toast.error(error.response?.data?.detail || 'Erro ao desativar categoria');
    }
  };

  const resetForm = () => {
    setEditingCategoria(null);
    setFormData({
      nome: '',
      descricao: '',
      icone: 'tag',
      cor: '#3B82F6',
      lista_convidado: false,
      desconto_padrao: 0,
      beneficios: {},
      ordem: 0,
      ativo: true
    });
  };

  const filteredCategorias = categorias.filter(cat =>
    cat.nome.toLowerCase().includes(searchTerm.toLowerCase()) ||
    cat.descricao?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="p-6 space-y-6">
      <Card>
        <CardHeader>
          <div className="flex justify-between items-center">
            <div>
              <CardTitle>Categorias de Clientes</CardTitle>
              <CardDescription>
                Crie categorias personalizadas e vincule seus clientes
              </CardDescription>
            </div>
            <Button onClick={() => setShowModal(true)}>
              <Plus className="h-4 w-4 mr-2" />
              Nova Categoria
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          <div className="mb-4">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
              <Input
                placeholder="Buscar categorias..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
              />
            </div>
          </div>

          {loading ? (
            <div className="text-center py-8">Carregando...</div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Categoria</TableHead>
                  <TableHead>Descrição</TableHead>
                  <TableHead>Clientes</TableHead>
                  <TableHead>Desconto</TableHead>
                  <TableHead>Lista Convidado</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Ações</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredCategorias.map((categoria) => (
                  <TableRow key={categoria.id}>
                    <TableCell>
                      <div className="flex items-center gap-2">
                        <div
                          className="w-8 h-8 rounded-full flex items-center justify-center"
                          style={{ backgroundColor: categoria.cor }}
                        >
                          <Tag className="h-4 w-4 text-white" />
                        </div>
                        <span className="font-medium">{categoria.nome}</span>
                      </div>
                    </TableCell>
                    <TableCell>{categoria.descricao || '-'}</TableCell>
                    <TableCell>
                      <Badge variant="secondary">
                        <Users className="h-3 w-3 mr-1" />
                        {categoria.total_clientes || 0}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      {categoria.desconto_padrao ? `${categoria.desconto_padrao}%` : '-'}
                    </TableCell>
                    <TableCell>
                      <Badge variant={categoria.lista_convidado ? 'default' : 'secondary'}>
                        {categoria.lista_convidado ? 'Sim' : 'Não'}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <Badge variant={categoria.ativo ? 'success' : 'destructive'}>
                        {categoria.ativo ? 'Ativo' : 'Inativo'}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <div className="flex gap-2">
                        <Button
                          size="sm"
                          variant="ghost"
                          onClick={() => handleEdit(categoria)}
                        >
                          <Edit className="h-4 w-4" />
                        </Button>
                        <Button
                          size="sm"
                          variant="ghost"
                          onClick={() => handleDelete(categoria.id)}
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>

      <Dialog open={showModal} onOpenChange={setShowModal}>
        <DialogContent className="max-w-2xl">
          <form onSubmit={handleSubmit}>
            <DialogHeader>
              <DialogTitle>
                {editingCategoria ? 'Editar Categoria' : 'Nova Categoria'}
              </DialogTitle>
              <DialogDescription>
                Defina as propriedades da categoria de clientes
              </DialogDescription>
            </DialogHeader>

            <div className="grid gap-4 py-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="nome">Nome da Categoria*</Label>
                  <Input
                    id="nome"
                    required
                    value={formData.nome}
                    onChange={(e) => setFormData({ ...formData, nome: e.target.value })}
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="ordem">Ordem de Exibição</Label>
                  <Input
                    id="ordem"
                    type="number"
                    value={formData.ordem}
                    onChange={(e) => setFormData({ ...formData, ordem: parseInt(e.target.value) })}
                  />
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="descricao">Descrição</Label>
                <Input
                  id="descricao"
                  value={formData.descricao}
                  onChange={(e) => setFormData({ ...formData, descricao: e.target.value })}
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="icone">Ícone</Label>
                  <Select
                    value={formData.icone}
                    onValueChange={(value) => setFormData({ ...formData, icone: value })}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {iconesDisponiveis.map(icone => (
                        <SelectItem key={icone} value={icone}>
                          {icone}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="cor">Cor</Label>
                  <div className="flex gap-2">
                    <Input
                      type="color"
                      value={formData.cor}
                      onChange={(e) => setFormData({ ...formData, cor: e.target.value })}
                      className="w-20"
                    />
                    <Input
                      value={formData.cor}
                      onChange={(e) => setFormData({ ...formData, cor: e.target.value })}
                      className="flex-1"
                    />
                  </div>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="desconto">Desconto Padrão (%)</Label>
                  <Input
                    id="desconto"
                    type="number"
                    min="0"
                    max="100"
                    value={formData.desconto_padrao}
                    onChange={(e) => setFormData({ ...formData, desconto_padrao: parseFloat(e.target.value) })}
                  />
                </div>

                <div className="flex items-center justify-between space-x-2">
                  <Label htmlFor="lista_convidado">Aparece em Lista de Convidados</Label>
                  <Switch
                    id="lista_convidado"
                    checked={formData.lista_convidado}
                    onCheckedChange={(checked) => setFormData({ ...formData, lista_convidado: checked })}
                  />
                </div>
              </div>

              <div className="flex items-center justify-between space-x-2">
                <Label htmlFor="ativo">Categoria Ativa</Label>
                <Switch
                  id="ativo"
                  checked={formData.ativo}
                  onCheckedChange={(checked) => setFormData({ ...formData, ativo: checked })}
                />
              </div>
            </div>

            <DialogFooter>
              <Button type="button" variant="outline" onClick={() => setShowModal(false)}>
                Cancelar
              </Button>
              <Button type="submit">
                {editingCategoria ? 'Atualizar' : 'Criar'} Categoria
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default CategoriasClientesModule;