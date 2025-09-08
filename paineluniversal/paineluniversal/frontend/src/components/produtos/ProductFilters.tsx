import React, { useState, useEffect } from 'react';
import { Search } from 'lucide-react';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { 
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '../ui/select';
import { Badge } from '../ui/badge';
import { ProdutoFilter, Categoria } from '../../types/produto';

interface ProductFiltersProps {
  filters: ProdutoFilter;
  onChange: (filters: ProdutoFilter) => void;
}

interface FilterChipProps {
  label: string;
  active: boolean;
  onClick: () => void;
}

const FilterChip: React.FC<FilterChipProps> = ({ label, active, onClick }) => (
  <button
    onClick={onClick}
    className={`
      px-3 py-1.5 text-sm rounded-full border transition-colors
      ${active 
        ? 'bg-primary text-primary-foreground border-primary' 
        : 'bg-background text-foreground border-input hover:bg-muted'
      }
    `}
  >
    {label}
  </button>
);

const ProductFilters: React.FC<ProductFiltersProps> = ({ filters, onChange }) => {
  const [categorias, setCategorias] = useState<Categoria[]>([]);
  const [tipos, setTipos] = useState<{ value: string; label: string }[]>([]);

  useEffect(() => {
    loadCategorias();
    loadTipos();
  }, []);

  const loadCategorias = async () => {
    try {
      // TODO: Implementar chamada para API
      // const response = await api.get('/categorias');
      // setCategorias(response.data);
      
      // Mock data para desenvolvimento
      setCategorias([
        { id: '1', nome: 'CERVEJA', mostrar_dashboard: true, mostrar_pos: true, ordem: 1, created_at: new Date(), updated_at: new Date() },
        { id: '2', nome: 'DRINKS', mostrar_dashboard: true, mostrar_pos: true, ordem: 2, created_at: new Date(), updated_at: new Date() },
        { id: '3', nome: 'PETISCOS', mostrar_dashboard: true, mostrar_pos: true, ordem: 3, created_at: new Date(), updated_at: new Date() },
        { id: '4', nome: 'ENTRADA', mostrar_dashboard: false, mostrar_pos: true, ordem: 4, created_at: new Date(), updated_at: new Date() },
        { id: '5', nome: 'CAMAROTE', mostrar_dashboard: true, mostrar_pos: true, ordem: 5, created_at: new Date(), updated_at: new Date() }
      ]);
    } catch (error) {
      console.error('Erro ao carregar categorias:', error);
    }
  };

  const loadTipos = async () => {
    try {
      // Mock data para desenvolvimento
      setTipos([
        { value: 'bebida', label: 'Bebida' },
        { value: 'comida', label: 'Comida' },
        { value: 'ingresso', label: 'Ingresso' },
        { value: 'ficha', label: 'Ficha' },
        { value: 'combo', label: 'Combo' },
        { value: 'voucher', label: 'Voucher' }
      ]);
    } catch (error) {
      console.error('Erro ao carregar tipos:', error);
    }
  };

  const handleFilterChange = (field: keyof ProdutoFilter, value: string) => {
    // Converter "all" para string vazia para manter compatibilidade
    const filterValue = value === 'all' ? '' : value;
    onChange({ ...filters, [field]: filterValue });
  };

  const handleSearch = () => {
    // A pesquisa é realizada automaticamente através do useEffect na tela pai
    console.log('Executando busca com filtros:', filters);
  };

  const clearFilters = () => {
    onChange({
      nome: '',
      categoria: '',
      tipo: '',
      habilitado: 'all'
    });
  };

  return (
    <div className="bg-card p-6 rounded-lg border space-y-4">
      {/* Campos de filtro principais */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {/* Campo Nome */}
        <div>
          <label className="block text-sm font-medium text-foreground mb-2">
            Nome
          </label>
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Buscar por nome..."
              value={filters.nome || ''}
              onChange={(e) => handleFilterChange('nome', e.target.value)}
              className="pl-10"
            />
          </div>
        </div>

        {/* Filtro Categorias */}
        <div>
          <label className="block text-sm font-medium text-foreground mb-2">
            Categoria
          </label>
          <Select 
            value={filters.categoria || 'all'} 
            onValueChange={(value) => handleFilterChange('categoria', value)}
          >
            <SelectTrigger>
              <SelectValue placeholder="Filtre por categorias" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">Todas as categorias</SelectItem>
              {categorias.map(categoria => (
                <SelectItem key={categoria.id} value={categoria.id}>
                  {categoria.nome}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        {/* Filtro Tipo */}
        <div>
          <label className="block text-sm font-medium text-foreground mb-2">
            Tipo
          </label>
          <Select 
            value={filters.tipo || 'all'} 
            onValueChange={(value) => handleFilterChange('tipo', value)}
          >
            <SelectTrigger>
              <SelectValue placeholder="Filtre por tipo" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">Todos os tipos</SelectItem>
              {tipos.map(tipo => (
                <SelectItem key={tipo.value} value={tipo.value}>
                  {tipo.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        {/* Botão Buscar */}
        <div className="flex items-end">
          <Button 
            onClick={handleSearch}
            className="w-full bg-purple-600 hover:bg-purple-700"
          >
            BUSCAR
          </Button>
        </div>
      </div>

      {/* Filtros rápidos */}
      <div className="flex flex-wrap gap-2">
        <FilterChip
          label="Todos"
          active={filters.habilitado === 'all'}
          onClick={() => handleFilterChange('habilitado', 'all')}
        />
        <FilterChip
          label="Habilitados"
          active={filters.habilitado === 'true'}
          onClick={() => handleFilterChange('habilitado', 'true')}
        />
        <FilterChip
          label="Desabilitados"
          active={filters.habilitado === 'false'}
          onClick={() => handleFilterChange('habilitado', 'false')}
        />
        <FilterChip
          label="Em destaque"
          active={filters.destaque === 'true'}
          onClick={() => handleFilterChange('destaque', 'true')}
        />
        
        {/* Botão limpar filtros */}
        {(filters.nome || filters.categoria || filters.tipo || filters.habilitado !== 'all') && (
          <Button 
            variant="outline" 
            size="sm" 
            onClick={clearFilters}
            className="ml-auto"
          >
            Limpar filtros
          </Button>
        )}
      </div>

      {/* Contadores de filtros ativos */}
      {(filters.nome || filters.categoria || filters.tipo || filters.habilitado !== 'all') && (
        <div className="flex items-center space-x-2 text-sm text-muted-foreground">
          <span>Filtros ativos:</span>
          {filters.nome && <Badge variant="secondary">Nome: {filters.nome}</Badge>}
          {filters.categoria && (
            <Badge variant="secondary">
              Categoria: {categorias.find(c => c.id === filters.categoria)?.nome}
            </Badge>
          )}
          {filters.tipo && (
            <Badge variant="secondary">
              Tipo: {tipos.find(t => t.value === filters.tipo)?.label}
            </Badge>
          )}
          {filters.habilitado !== 'all' && (
            <Badge variant="secondary">
              Status: {filters.habilitado === 'true' ? 'Habilitados' : 'Desabilitados'}
            </Badge>
          )}
        </div>
      )}
    </div>
  );
};

export default ProductFilters;