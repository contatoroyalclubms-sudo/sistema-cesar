import React, { useState, useEffect } from 'react';
import { ColumnDef } from '@tanstack/react-table';
import { 
  Pencil, 
  Copy, 
  Lock, 
  Trash2,
  Plus,
  Download,
  Upload,
  Search
} from 'lucide-react';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';
import { Checkbox } from '../ui/checkbox';
import { Input } from '../ui/input';
import { toast } from '../../hooks/use-toast';
import { Produto, ProdutoFilter } from '../../types/produto';
import { DataTable } from '../shared/DataTable';
import StatusToggle from '../shared/StatusToggle';
import ActionButton from '../shared/ActionButton';
import ProductFilters from './ProductFilters';
import BulkActions from './BulkActions';
import ProductForm from './ProductForm';
import ProductImportModal from './ProductImportModal';
import { produtoService } from '../../services/api';
import { ProdutoCreate } from '../../types/database';
import { useEvento } from '../../contexts/EventoContext';
import EventoAutoConfig from '../desenvolvimento/EventoAutoConfig';

const ProductsList: React.FC = () => {
  const { eventoId } = useEvento();
  const [produtos, setProdutos] = useState<Produto[]>([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState<ProdutoFilter>({
    nome: '',
    categoria: '',
    tipo: '',
    habilitado: 'all'
  });
  const [selectedItems, setSelectedItems] = useState<Produto[]>([]);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [editingProduct, setEditingProduct] = useState<Produto | undefined>(undefined);
  const [productToDelete, setProductToDelete] = useState<Produto | null>(null);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [showImportModal, setShowImportModal] = useState(false);

  useEffect(() => {
    loadProdutos();
  }, [filters]);

  const loadProdutos = async () => {
    setLoading(true);
    try {
      // ✅ Produtos são globais - não precisamos mais do eventoId
      console.log('🔄 Carregando produtos globais...');
      const produtos = await produtoService.getAll();
      console.log('✅ Produtos carregados:', produtos.length);
      setProdutos(produtos);
    } catch (error) {
      console.error('❌ Erro ao carregar produtos:', error);
      toast({
        title: "Erro",
        description: "Erro ao carregar produtos. Verifique sua conexão.",
        variant: "destructive"
      });
      
      // Mock data como fallback se a API falhar
      setProdutos([
        {
          id: '1',
          nome: 'Cerveja Heineken 600ml',
          codigo: 'CERV001',
          tipo: 'BEBIDA',
          categoria_id: '1',
          categoria: { id: '1', nome: 'CERVEJA', mostrar_dashboard: true, mostrar_pos: true, ordem: 1, created_at: new Date(), updated_at: new Date() },
          ncm: '22030000',
          cfop: '5102',
          cest: '0300700',
          valor: 8.50,
          destaque: true,
          habilitado: true,
          descricao: 'Cerveja premium importada',
          estoque: 100,
          promocional: false,
          created_at: new Date(),
          updated_at: new Date()
        },
        {
          id: '2',
          nome: 'Caipirinha de Cachaça',
          codigo: 'DRINK001',
          tipo: 'BEBIDA',
          categoria_id: '2',
          categoria: { id: '2', nome: 'DRINKS', mostrar_dashboard: true, mostrar_pos: true, ordem: 2, created_at: new Date(), updated_at: new Date() },
          valor: 12.00,
          destaque: false,
          habilitado: true,
          descricao: 'Drink tradicional brasileiro',
          estoque: 0,
          promocional: true,
          created_at: new Date(),
          updated_at: new Date()
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleToggleDestaque = async (id: string, checked: boolean) => {
    try {
      // TODO: Implementar chamada para API
      // await api.patch(`/produtos/${id}`, { destaque: checked });
      setProdutos(prev => prev.map(p => p.id === id ? { ...p, destaque: checked } : p));
    } catch (error) {
      console.error('Erro ao atualizar destaque:', error);
    }
  };

  const handleToggleHabilitado = async (id: string, checked: boolean) => {
    try {
      // TODO: Implementar chamada para API
      // await api.patch(`/produtos/${id}`, { habilitado: checked });
      setProdutos(prev => prev.map(p => p.id === id ? { ...p, habilitado: checked } : p));
    } catch (error) {
      console.error('Erro ao atualizar status:', error);
    }
  };

  const handleEdit = (produto: Produto) => {
    setEditingProduct(produto);
  };

  const handleDuplicate = (produto: Produto) => {
    console.log('Duplicando produto:', produto);
    // TODO: Implementar duplicação
  };

  const handleLimitAccess = (produto: Produto) => {
    console.log('Limitando acesso:', produto);
    // TODO: Implementar limitação de acesso
  };

  const handleDelete = (produto: Produto) => {
    setProductToDelete(produto);
    setShowDeleteConfirm(true);
  };

  const confirmDelete = async () => {
    if (!productToDelete) return;
    
    try {
      await produtoService.delete(productToDelete.id);
      toast({
        title: "Produto excluído",
        description: `${productToDelete.nome} foi excluído com sucesso.`,
      });
      loadProdutos(); // Recarrega a lista
    } catch (error) {
      console.error('Erro ao excluir produto:', error);
      toast({
        title: "Erro ao excluir",
        description: "Ocorreu um erro ao excluir o produto. Tente novamente.",
        variant: "destructive",
      });
    } finally {
      setShowDeleteConfirm(false);
      setProductToDelete(null);
    }
  };

  const handleImport = () => {
    setShowImportModal(true);
  };

  const handleImportSuccess = () => {
    loadProdutos(); // Recarregar lista após importação
  };

  const handleExport = () => {
    console.log('Exportando produtos');
    // TODO: Implementar modal de exportação
  };

  const handleBulkDelete = () => {
    console.log('Excluindo em lote:', selectedItems);
    // TODO: Implementar exclusão em lote
  };

  const handleBulkEnable = () => {
    console.log('Habilitando em lote:', selectedItems);
    // TODO: Implementar habilitação em lote
  };

  const handleBulkDisable = () => {
    console.log('Desabilitando em lote:', selectedItems);
    // TODO: Implementar desabilitação em lote
  };

  const handleSaveProduct = async (data: any, imageFile?: File) => {
    try {
      console.log('💾 Dados recebidos do formulário:', data);

      // Converter os dados do formulário para o formato esperado pela API
      const produtoData: ProdutoCreate = {
        nome: data.nome,
        descricao: data.descricao || '',
        tipo: data.tipo,
        preco: data.preco, // ✅ Corrigido: campo correto
        categoria: data.categoria, // ✅ Corrigido: categoria como string, não ID
        codigo_interno: data.codigo_interno || undefined, // ✅ Corrigido: campo correto
        estoque_atual: data.estoque_atual || 0,
        estoque_minimo: data.estoque_minimo || 0,
        estoque_maximo: data.estoque_maximo || 1000,
        controla_estoque: data.controla_estoque !== false,
        status: data.status || 'ATIVO',
        imagem_url: data.imagem_url || undefined,
        // Campos adicionais opcionais
        marca: data.marca || undefined,
        fornecedor: data.fornecedor || undefined,
        preco_custo: data.preco_custo || undefined,
        margem_lucro: data.margem_lucro || undefined,
        unidade_medida: data.unidade_medida || 'UN',
        volume: data.volume || undefined,
        teor_alcoolico: data.teor_alcoolico || undefined,
        temperatura_ideal: data.temperatura_ideal || undefined,
        validade_dias: data.validade_dias || undefined,
        ncm: data.ncm || undefined,
        cfop: data.cfop || undefined,
        cest: data.cest || undefined,
        icms: data.icms || undefined,
        ipi: data.ipi || undefined,
        observacoes: data.observacoes || undefined,
      };

      if (editingProduct) {
        // Validar ID antes da conversão
        const productId = editingProduct.id;
        if (!productId) {
          throw new Error('ID do produto não encontrado');
        }
        
        // Conversão mais segura do ID
        let numericId: number;
        if (typeof productId === 'string') {
          numericId = parseInt(productId, 10);
          if (isNaN(numericId) || numericId <= 0) {
            throw new Error(`ID do produto inválido: "${productId}"`);
          }
        } else if (typeof productId === 'number') {
          numericId = productId;
          if (isNaN(numericId) || numericId <= 0) {
            throw new Error(`ID do produto inválido: ${productId}`);
          }
        } else {
          throw new Error(`Tipo de ID do produto inválido: ${typeof productId}`);
        }
        
        // Atualizar produto existente
        await produtoService.update(numericId, produtoData);
        toast({
          title: "Sucesso",
          description: "Produto atualizado com sucesso!",
        });
      } else {
        // Criar novo produto
        await produtoService.create(produtoData);
        toast({
          title: "Sucesso",
          description: "Produto criado com sucesso!",
        });
      }
      
      // Recarregar lista
      await loadProdutos();
    } catch (error: any) {
      console.error('Erro ao salvar produto:', error);
      
      let errorMessage = 'Erro desconhecido ao salvar produto.';
      if (error.response?.data?.detail) {
        errorMessage = error.response.data.detail;
      } else if (error.message) {
        errorMessage = error.message;
      }
      
      toast({
        title: "Erro",
        description: errorMessage,
        variant: "destructive"
      });
      throw error;
    }
  };

  const handleCloseModal = () => {
    setShowCreateModal(false);
    setEditingProduct(undefined);
  };

  const columns: ColumnDef<Produto>[] = [
    {
      id: 'select',
      header: ({ table }) => (
        <Checkbox
          checked={table.getIsAllPageRowsSelected()}
          onCheckedChange={(value) => table.toggleAllPageRowsSelected(!!value)}
          aria-label="Selecionar todos"
        />
      ),
      cell: ({ row }) => (
        <Checkbox
          checked={row.getIsSelected()}
          onCheckedChange={(value) => row.toggleSelected(!!value)}
          aria-label="Selecionar linha"
        />
      ),
      enableSorting: false,
      enableHiding: false,
    },
    {
      accessorKey: 'nome',
      header: 'Produto',
      cell: ({ row }) => (
        <div className="flex items-center space-x-3">
          {row.original.imagem && (
            <img 
              src={row.original.imagem} 
              alt={row.original.nome}
              className="w-10 h-10 rounded object-cover"
            />
          )}
          <div className="min-w-0">
            <div className="font-medium text-foreground truncate">{row.original.nome}</div>
            {row.original.codigo && (
              <div className="text-sm text-muted-foreground">{row.original.codigo}</div>
            )}
          </div>
        </div>
      ),
    },
    {
      accessorKey: 'id',
      header: 'Produto ID',
      cell: ({ getValue }) => (
        <span className="font-mono text-xs bg-muted px-2 py-1 rounded">
          {getValue() as string}
        </span>
      ),
    },
    {
      accessorKey: 'categoria',
      header: 'Categoria',
      cell: ({ row }) => (
        <Badge variant="outline">{row.original.categoria || 'Sem categoria'}</Badge>
      ),
    },
    {
      accessorKey: 'tipo',
      header: 'Tipo',
      cell: ({ getValue }) => getValue() || '-',
    },
    {
      accessorKey: 'estoque_atual',
      header: 'Estoque',
      cell: ({ getValue }) => (
        <span className="font-mono text-sm">
          {getValue() || 0}
        </span>
      ),
    },
    {
      accessorKey: 'ncm',
      header: 'NCM',
      cell: ({ getValue }) => getValue() || '-',
    },
    {
      accessorKey: 'cfop',
      header: 'CFOP',
      cell: ({ getValue }) => getValue() || '-',
    },
    {
      accessorKey: 'cest',
      header: 'CEST',
      cell: ({ getValue }) => getValue() || '-',
    },
    {
      accessorKey: 'preco',
      header: 'Valor',
      cell: ({ getValue }) => (
        <span className="font-semibold">
          R$ {Number(getValue()).toFixed(2)}
        </span>
      ),
    },
    {
      accessorKey: 'destaque',
      header: 'Destaque',
      cell: ({ row }) => (
        <StatusToggle
          checked={row.original.destaque}
          onChange={(checked) => handleToggleDestaque(row.original.id, checked)}
          color="yellow"
          size="sm"
        />
      ),
    },
    {
      accessorKey: 'habilitado',
      header: 'Habilitado?',
      cell: ({ row }) => (
        <StatusToggle
          checked={row.original.habilitado}
          onChange={(checked) => handleToggleHabilitado(row.original.id, checked)}
          color="green"
          size="sm"
        />
      ),
    },
    {
      id: 'actions',
      header: 'Ações',
      cell: ({ row }) => (
        <div className="flex items-center space-x-2">
          <ActionButton
            icon={Pencil}
            tooltip="Editar"
            onClick={() => handleEdit(row.original)}
            color="blue"
            size="sm"
          />
          <ActionButton
            icon={Copy}
            tooltip="Duplicar"
            onClick={() => handleDuplicate(row.original)}
            color="green"
            size="sm"
          />
          <ActionButton
            icon={Lock}
            tooltip="Limitar acesso"
            onClick={() => handleLimitAccess(row.original)}
            color="orange"
            size="sm"
          />
          <ActionButton
            icon={Trash2}
            tooltip="Excluir"
            onClick={() => handleDelete(row.original)}
            color="red"
            size="sm"
          />
        </div>
      ),
      enableSorting: false,
    },
  ];

  return (
    <div className="p-6 space-y-6">
      <EventoAutoConfig />
      
      {/* Header */}
      <div className="flex justify-between items-start">
        <div>
          <h1 className="text-3xl font-bold text-foreground">PRODUTOS</h1>
          <p className="text-muted-foreground mt-1">
            Gerencie todos os produtos do estabelecimento - Catálogo Global
          </p>
        </div>
        
        <div className="flex items-center space-x-3">
          <Button variant="outline" onClick={handleImport} className="gap-2">
            <Upload className="h-4 w-4" />
            Importar
          </Button>
          <Button variant="outline" onClick={handleExport} className="gap-2">
            <Download className="h-4 w-4" />
            Exportar
          </Button>
          <Button onClick={() => setShowCreateModal(true)} className="gap-2">
            <Plus className="h-4 w-4" />
            Novo produto
          </Button>
        </div>
      </div>

      {/* Filtros */}
      <ProductFilters filters={filters} onChange={setFilters} />

      {/* Ações em lote */}
      {selectedItems.length > 0 && (
        <BulkActions 
          selectedCount={selectedItems.length}
          onBulkDelete={handleBulkDelete}
          onBulkEnable={handleBulkEnable}
          onBulkDisable={handleBulkDisable}
        />
      )}

      {/* Tabela */}
      <DataTable 
        columns={columns}
        data={produtos}
        loading={loading}
        onSelectionChange={setSelectedItems}
        pageSize={10}
      />

      {/* Modal de criação/edição */}
      <ProductForm
        produto={showCreateModal ? undefined : editingProduct}
        open={showCreateModal || !!editingProduct}
        onClose={handleCloseModal}
        onSave={handleSaveProduct}
      />

      {/* Modal de importação */}
      <ProductImportModal
        open={showImportModal}
        onClose={() => setShowImportModal(false)}
        onSuccess={handleImportSuccess}
      />

      {/* Modal de confirmação de exclusão */}
      {showDeleteConfirm && productToDelete && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white p-6 rounded-lg shadow-lg max-w-md w-full mx-4">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              Confirmar exclusão
            </h3>
            <p className="text-gray-600 mb-6">
              Tem certeza que deseja excluir o produto <strong>{productToDelete.nome}</strong>? 
              Esta ação não pode ser desfeita.
            </p>
            <div className="flex space-x-3 justify-end">
              <Button 
                variant="outline" 
                onClick={() => {
                  setShowDeleteConfirm(false);
                  setProductToDelete(null);
                }}
              >
                Cancelar
              </Button>
              <Button 
                variant="destructive" 
                onClick={confirmDelete}
              >
                Excluir
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ProductsList;