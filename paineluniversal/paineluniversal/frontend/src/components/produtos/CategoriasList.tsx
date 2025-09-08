import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Plus, Search, Edit2, Trash2, X, Palette } from 'lucide-react';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Textarea } from '../ui/textarea';
import { Label } from '../ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Badge } from '../ui/badge';
import { useToast } from '../../hooks/use-toast';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '../ui/dialog';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '../ui/table';
import { categoriaService, Categoria, CategoriaCreate, CategoriaUpdate } from '../../services/categoria';

interface CategoriasListProps {
  onSelectCategoria?: (categoria: Categoria) => void;
  showActions?: boolean;
}

const CORES_PADRAO = [
  '#10B981', // Verde
  '#F59E0B', // Amarelo
  '#EF4444', // Vermelho
  '#3B82F6', // Azul
  '#8B5CF6', // Roxo
  '#F97316', // Laranja
  '#06B6D4', // Ciano
  '#84CC16', // Lima
  '#EC4899', // Rosa
  '#6B7280'  // Cinza
];

export const CategoriasList: React.FC<CategoriasListProps> = ({ 
  onSelectCategoria, 
  showActions = true 
}) => {
  const [categorias, setCategorias] = useState<Categoria[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [modalOpen, setModalOpen] = useState(false);
  const [editingCategoria, setEditingCategoria] = useState<Categoria | null>(null);
  const [formData, setFormData] = useState<CategoriaCreate>({
    nome: '',
    descricao: '',
    cor: CORES_PADRAO[0]
  });
  const { toast } = useToast();

  useEffect(() => {
    carregarCategorias();
  }, []);

  const carregarCategorias = async () => {
    try {
      setLoading(true);
      const data = await categoriaService.listar();
      setCategorias(data);
    } catch (error) {
      console.error('Erro ao carregar categorias:', error);
      toast({
        title: "Erro",
        description: "Não foi possível carregar as categorias",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!formData.nome.trim()) {
      toast({
        title: "Erro",
        description: "Nome da categoria é obrigatório",
        variant: "destructive",
      });
      return;
    }

    try {
      if (editingCategoria) {
        const categoriaAtualizada = await categoriaService.atualizar(editingCategoria.id, formData);
        setCategorias(prev => prev.map(cat => 
          cat.id === editingCategoria.id ? categoriaAtualizada : cat
        ));
        toast({
          title: "Sucesso",
          description: "Categoria atualizada com sucesso",
        });
      } else {
        const novaCategoria = await categoriaService.criar(formData);
        setCategorias(prev => [...prev, novaCategoria]);
        toast({
          title: "Sucesso",
          description: "Categoria criada com sucesso",
        });
      }
      
      resetForm();
    } catch (error) {
      console.error('Erro ao salvar categoria:', error);
      toast({
        title: "Erro",
        description: "Erro ao salvar categoria",
        variant: "destructive",
      });
    }
  };

  const handleEdit = (categoria: Categoria) => {
    setEditingCategoria(categoria);
    setFormData({
      nome: categoria.nome,
      descricao: categoria.descricao || '',
      cor: categoria.cor || CORES_PADRAO[0]
    });
    setModalOpen(true);
  };

  const handleDelete = async (categoria: Categoria) => {
    if (!window.confirm(`Tem certeza que deseja excluir a categoria "${categoria.nome}"?`)) {
      return;
    }

    try {
      await categoriaService.deletar(categoria.id);
      setCategorias(prev => prev.filter(cat => cat.id !== categoria.id));
      toast({
        title: "Sucesso",
        description: "Categoria excluída com sucesso",
      });
    } catch (error) {
      console.error('Erro ao excluir categoria:', error);
      toast({
        title: "Erro",
        description: "Erro ao excluir categoria",
        variant: "destructive",
      });
    }
  };

  const resetForm = () => {
    setFormData({
      nome: '',
      descricao: '',
      cor: CORES_PADRAO[0]
    });
    setEditingCategoria(null);
    setModalOpen(false);
  };

  const categoriasFiltradas = categorias.filter(categoria =>
    categoria.nome.toLowerCase().includes(searchTerm.toLowerCase()) ||
    categoria.descricao?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  if (loading) {
    return (
      <Card>
        <CardContent className="p-6">
          <div className="flex items-center justify-center h-32">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle>Categorias de Produtos</CardTitle>
            <CardDescription>
              Gerencie as categorias dos seus produtos
            </CardDescription>
          </div>
          
          {showActions && (
            <Dialog open={modalOpen} onOpenChange={setModalOpen}>
              <DialogTrigger asChild>
                <Button onClick={() => resetForm()}>
                  <Plus className="h-4 w-4 mr-2" />
                  Nova Categoria
                </Button>
              </DialogTrigger>
              
              <DialogContent className="sm:max-w-md">
                <DialogHeader>
                  <DialogTitle>
                    {editingCategoria ? 'Editar Categoria' : 'Nova Categoria'}
                  </DialogTitle>
                  <DialogDescription>
                    {editingCategoria 
                      ? 'Atualize as informações da categoria' 
                      : 'Crie uma nova categoria para organizar seus produtos'
                    }
                  </DialogDescription>
                </DialogHeader>
                
                <form onSubmit={handleSubmit} className="space-y-4">
                  <div>
                    <Label htmlFor="nome">Nome *</Label>
                    <Input
                      id="nome"
                      value={formData.nome}
                      onChange={(e) => setFormData({ ...formData, nome: e.target.value })}
                      placeholder="Nome da categoria"
                      required
                    />
                  </div>
                  
                  <div>
                    <Label htmlFor="descricao">Descrição</Label>
                    <Textarea
                      id="descricao"
                      value={formData.descricao}
                      onChange={(e) => setFormData({ ...formData, descricao: e.target.value })}
                      placeholder="Descrição da categoria (opcional)"
                      rows={3}
                    />
                  </div>
                  
                  <div>
                    <Label htmlFor="cor">Cor</Label>
                    <div className="flex flex-wrap gap-2 mt-2">
                      {CORES_PADRAO.map((cor) => (
                        <button
                          key={cor}
                          type="button"
                          onClick={() => setFormData({ ...formData, cor })}
                          className={`w-8 h-8 rounded-full border-2 transition-all ${
                            formData.cor === cor 
                              ? 'border-black dark:border-white scale-110' 
                              : 'border-gray-300 hover:scale-105'
                          }`}
                          style={{ backgroundColor: cor }}
                          title={cor}
                        />
                      ))}
                    </div>
                    <Input
                      id="cor"
                      type="color"
                      value={formData.cor}
                      onChange={(e) => setFormData({ ...formData, cor: e.target.value })}
                      className="mt-2 w-20 h-10"
                    />
                  </div>
                  
                  <div className="flex gap-2 pt-4">
                    <Button type="submit" className="flex-1">
                      {editingCategoria ? 'Atualizar' : 'Criar'} Categoria
                    </Button>
                    <Button 
                      type="button" 
                      variant="outline" 
                      onClick={resetForm}
                      className="flex-1"
                    >
                      Cancelar
                    </Button>
                  </div>
                </form>
              </DialogContent>
            </Dialog>
          )}
        </div>
        
        <div className="flex items-center space-x-2">
          <div className="relative flex-1 max-w-sm">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Buscar categorias..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10"
            />
          </div>
        </div>
      </CardHeader>
      
      <CardContent>
        {categoriasFiltradas.length === 0 ? (
          <div className="text-center py-8">
            <p className="text-muted-foreground">
              {searchTerm ? 'Nenhuma categoria encontrada' : 'Nenhuma categoria cadastrada'}
            </p>
            {!searchTerm && showActions && (
              <Button 
                variant="outline" 
                className="mt-4"
                onClick={() => setModalOpen(true)}
              >
                <Plus className="h-4 w-4 mr-2" />
                Criar primeira categoria
              </Button>
            )}
          </div>
        ) : (
          <div className="rounded-md border">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Categoria</TableHead>
                  <TableHead>Descrição</TableHead>
                  <TableHead>Status</TableHead>
                  {showActions && <TableHead className="text-right">Ações</TableHead>}
                </TableRow>
              </TableHeader>
              <TableBody>
                <AnimatePresence>
                  {categoriasFiltradas.map((categoria) => (
                    <motion.tr
                      key={categoria.id}
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -20 }}
                      className="cursor-pointer hover:bg-muted/50"
                      onClick={() => onSelectCategoria?.(categoria)}
                    >
                      <TableCell>
                        <div className="flex items-center space-x-3">
                          <div
                            className="w-4 h-4 rounded-full border"
                            style={{ backgroundColor: categoria.cor }}
                          />
                          <div>
                            <p className="font-medium">{categoria.nome}</p>
                            <p className="text-sm text-muted-foreground">
                              ID: {categoria.id}
                            </p>
                          </div>
                        </div>
                      </TableCell>
                      
                      <TableCell>
                        <p className="text-sm">
                          {categoria.descricao || 'Sem descrição'}
                        </p>
                      </TableCell>
                      
                      <TableCell>
                        <Badge variant={categoria.ativo ? 'default' : 'secondary'}>
                          {categoria.ativo ? 'Ativo' : 'Inativo'}
                        </Badge>
                      </TableCell>
                      
                      {showActions && (
                        <TableCell className="text-right">
                          <div className="flex items-center justify-end space-x-1">
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={(e) => {
                                e.stopPropagation();
                                handleEdit(categoria);
                              }}
                            >
                              <Edit2 className="h-4 w-4" />
                            </Button>
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={(e) => {
                                e.stopPropagation();
                                handleDelete(categoria);
                              }}
                              className="text-destructive hover:text-destructive"
                            >
                              <Trash2 className="h-4 w-4" />
                            </Button>
                          </div>
                        </TableCell>
                      )}
                    </motion.tr>
                  ))}
                </AnimatePresence>
              </TableBody>
            </Table>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default CategoriasList;
