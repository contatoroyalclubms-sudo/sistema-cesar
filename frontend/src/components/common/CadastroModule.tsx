import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Badge } from '../ui/badge';
import { 
  Table, 
  TableBody, 
  TableCell, 
  TableHead, 
  TableHeader, 
  TableRow 
} from '../ui/table';
import { 
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '../ui/dialog';
import { useToast } from '../../hooks/use-toast';
import { 
  Plus, 
  Search, 
  Edit, 
  Trash2, 
  Download, 
  Upload,
  Filter,
  MoreHorizontal
} from 'lucide-react';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '../ui/dropdown-menu';
import clientesService from '../../services/clientesService';

const CadastroModule = ({ config, title, description, apiService = null }) => {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [filters, setFilters] = useState({});
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingItem, setEditingItem] = useState(null);
  const [formData, setFormData] = useState({});
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const { toast } = useToast();

  const itemsPerPage = config.ui?.itemsPerPage || 25;

  // Usar apiService se fornecido, senão usar clientesService como fallback
  const service = apiService || clientesService;

  // Carregar dados
  const loadData = async () => {
    setLoading(true);
    try {
      const params = {
        skip: (currentPage - 1) * itemsPerPage,
        limit: itemsPerPage,
        ...filters,
        ...(searchTerm && { nome: searchTerm })
      };

      const data = await service.getAll(params);
      setItems(Array.isArray(data) ? data : []);
      setTotalPages(Math.ceil((data.length || 0) / itemsPerPage));
    } catch (error) {
      console.error('Erro ao carregar dados:', error);
      toast({
        title: "Erro",
        description: "Erro ao carregar dados",
        variant: "destructive",
      });
      setItems([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [currentPage, searchTerm, filters]);

  // Filtrar dados localmente também
  const filteredItems = items.filter(item => {
    const matchesSearch = !searchTerm || 
      config.searchConfig?.searchableFields?.some(field => 
        item[field]?.toString().toLowerCase().includes(searchTerm.toLowerCase())
      );
    
    const matchesFilters = Object.entries(filters).every(([key, value]) => 
      !value || item[key]?.toString().toLowerCase().includes(value.toLowerCase())
    );
    
    return matchesSearch && matchesFilters;
  });

  // Abrir modal para criar/editar
  const openModal = (item = null) => {
    setEditingItem(item);
    setFormData(item ? { ...item } : {});
    setIsModalOpen(true);
  };

  // Atualizar dados do formulário
  const updateFormData = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  // Salvar item
  const handleSave = async (e) => {
    e.preventDefault();
    try {
      if (editingItem) {
        await clientesService.update(editingItem.id, formData);
        toast({
          title: "Sucesso",
          description: `${config.itemName} atualizado com sucesso`,
        });
      } else {
        await clientesService.create(formData);
        toast({
          title: "Sucesso", 
          description: `${config.itemName} criado com sucesso`,
        });
      }
      setIsModalOpen(false);
      setFormData({});
      loadData();
    } catch (error) {
      console.error('Erro ao salvar:', error);
      toast({
        title: "Erro",
        description: error.response?.data?.detail || `Erro ao salvar ${config.itemName.toLowerCase()}`,
        variant: "destructive",
      });
    }
  };

  // Excluir item
  const handleDelete = async (id) => {
    if (window.confirm(`Confirma a exclusão deste ${config.itemName.toLowerCase()}?`)) {
      try {
        await service.delete(id);
        toast({
          title: "Sucesso",
          description: `${config.itemName} excluído com sucesso`,
        });
        loadData();
      } catch (error) {
        console.error('Erro ao excluir:', error);
        toast({
          title: "Erro",
          description: `Erro ao excluir ${config.itemName.toLowerCase()}`,
          variant: "destructive",
        });
      }
    }
  };

  // Renderizar valor da célula
  const renderCellValue = (item, column) => {
    const value = item[column.key];
    
    switch (column.type) {
      case 'status':
        return (
          <Badge variant={value === 'ativo' ? 'default' : 'secondary'}>
            {value?.toUpperCase()}
          </Badge>
        );
      case 'date':
        return value ? new Date(value).toLocaleDateString('pt-BR') : '-';
      case 'cpf':
        return value?.replace(/(\d{3})(\d{3})(\d{3})(\d{2})/, '$1.$2.$3-$4') || '-';
      case 'phone':
        return value?.replace(/(\d{2})(\d{5})(\d{4})/, '($1) $2-$3') || '-';
      default:
        return value || '-';
    }
  };

  // Renderizar campo do formulário
  const renderFormField = (field) => {
    const value = formData[field.key] || field.defaultValue || '';
    
    switch (field.type) {
      case 'select':
        return (
          <select 
            className="w-full p-2 border rounded-md"
            value={value}
            onChange={(e) => updateFormData(field.key, e.target.value)}
            required={field.required}
          >
            <option value="">Selecione...</option>
            {field.options?.map(option => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        );
      case 'date':
        return (
          <Input
            type="date"
            value={value}
            onChange={(e) => updateFormData(field.key, e.target.value)}
            placeholder={field.placeholder}
            required={field.required}
          />
        );
      case 'hidden':
        return null;
      default:
        return (
          <Input
            type={field.type === 'email' ? 'email' : 'text'}
            value={value}
            onChange={(e) => updateFormData(field.key, e.target.value)}
            placeholder={field.placeholder}
            required={field.required}
          />
        );
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-heading font-bold text-foreground">{title}</h1>
          <p className="text-muted-foreground">{description}</p>
        </div>
        <Button onClick={() => openModal()}>
          <Plus className="w-4 h-4 mr-2" />
          {config.createButtonText || `Novo ${config.itemName}`}
        </Button>
      </div>

      {/* Filtros e busca */}
      <Card>
        <CardContent className="p-4">
          <div className="flex gap-4">
            {/* Busca */}
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder={config.searchConfig?.placeholder || 'Buscar...'}
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-9"
                />
              </div>
            </div>

            {/* Filtros */}
            {config.filters?.map(filter => (
              <div key={filter.key} className="min-w-40">
                {filter.type === 'select' ? (
                  <select 
                    className="w-full p-2 border rounded-md"
                    value={filters[filter.key] || ''}
                    onChange={(e) => setFilters(prev => ({
                      ...prev,
                      [filter.key]: e.target.value
                    }))}
                  >
                    {filter.options?.map(option => (
                      <option key={option.value} value={option.value}>
                        {option.label}
                      </option>
                    ))}
                  </select>
                ) : (
                  <Input
                    placeholder={filter.placeholder}
                    value={filters[filter.key] || ''}
                    onChange={(e) => setFilters(prev => ({
                      ...prev,
                      [filter.key]: e.target.value
                    }))}
                  />
                )}
              </div>
            ))}

            {/* Ações */}
            {config.showExportImport && (
              <div className="flex gap-2">
                <Button variant="outline" size="sm">
                  <Download className="w-4 h-4 mr-2" />
                  Exportar
                </Button>
                <Button variant="outline" size="sm">
                  <Upload className="w-4 h-4 mr-2" />
                  Importar
                </Button>
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Tabela */}
      <Card>
        <CardContent className="p-0">
          <Table>
            <TableHeader>
              <TableRow>
                {config.columns.map(column => (
                  <TableHead key={column.key}>{column.label}</TableHead>
                ))}
                <TableHead className="w-20">AÇÕES</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {loading ? (
                <TableRow>
                  <TableCell colSpan={config.columns.length + 1} className="text-center">
                    Carregando...
                  </TableCell>
                </TableRow>
              ) : filteredItems.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={config.columns.length + 1} className="text-center">
                    {config.emptyMessage || 'Nenhum item encontrado'}
                  </TableCell>
                </TableRow>
              ) : (
                filteredItems.map(item => (
                  <TableRow key={item.id}>
                    {config.columns.map(column => (
                      <TableCell key={column.key}>
                        {renderCellValue(item, column)}
                      </TableCell>
                    ))}
                    <TableCell>
                      <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                          <Button variant="ghost" className="h-8 w-8 p-0">
                            <MoreHorizontal className="h-4 w-4" />
                          </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="end">
                          <DropdownMenuItem onClick={() => openModal(item)}>
                            <Edit className="mr-2 h-4 w-4" />
                            Editar
                          </DropdownMenuItem>
                          <DropdownMenuItem 
                            onClick={() => handleDelete(item.id)}
                            className="text-destructive"
                          >
                            <Trash2 className="mr-2 h-4 w-4" />
                            Excluir
                          </DropdownMenuItem>
                        </DropdownMenuContent>
                      </DropdownMenu>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      {/* Modal de formulário */}
      <Dialog open={isModalOpen} onOpenChange={setIsModalOpen}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>
              {editingItem ? `Editar ${config.itemName}` : `Novo ${config.itemName}`}
            </DialogTitle>
          </DialogHeader>
          
          <form onSubmit={handleSave} className="space-y-4">
            {config.formFields.filter(field => field.type !== 'hidden').map(field => (
              <div key={field.key} className="space-y-2">
                <label className="text-sm font-medium">
                  {field.label}
                  {field.required && <span className="text-destructive ml-1">*</span>}
                </label>
                {renderFormField(field)}
              </div>
            ))}
            
            <div className="flex justify-end gap-2 pt-4">
              <Button 
                type="button" 
                variant="outline" 
                onClick={() => setIsModalOpen(false)}
              >
                Cancelar
              </Button>
              <Button type="submit">
                Salvar
              </Button>
            </div>
          </form>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default CadastroModule;
