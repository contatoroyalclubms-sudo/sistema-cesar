import React, { createContext, useContext, useState, useEffect } from 'react';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { apiService } from '../services/apiService';

interface Product {
  id: number;
  nome: string;
  descricao: string;
  preco: number;
  categoria_id: number;
  categoria_nome: string;
  disponivel: boolean;
  tempo_preparo?: number;
  imagem_url?: string;
  ingredientes?: string[];
  alergenos?: string[];
  observacoes?: string;
}

interface Category {
  id: number;
  nome: string;
  descricao?: string;
  ordem: number;
  ativa: boolean;
  produtos_count: number;
}

interface ProductFilters {
  categoria_id?: number;
  search?: string;
  disponivel_apenas?: boolean;
  preco_min?: number;
  preco_max?: number;
}

interface ProductState {
  products: Product[];
  categories: Category[];
  filteredProducts: Product[];
  filters: ProductFilters;
  isLoading: boolean;
  error: string | null;
  lastSync: Date | null;
  selectedCategory: number | null;
}

const initialState: ProductState = {
  products: [],
  categories: [],
  filteredProducts: [],
  filters: {},
  isLoading: false,
  error: null,
  lastSync: null,
  selectedCategory: null,
};

interface ProductContextType {
  state: ProductState;
  loadProducts: (forceRefresh?: boolean) => Promise<void>;
  loadCategories: (forceRefresh?: boolean) => Promise<void>;
  setFilters: (filters: ProductFilters) => void;
  setSelectedCategory: (categoryId: number | null) => void;
  searchProducts: (query: string) => void;
  getProductById: (id: number) => Product | undefined;
  getCategoryById: (id: number) => Category | undefined;
  clearError: () => void;
  syncProducts: () => Promise<void>;
}

const ProductContext = createContext<ProductContextType | undefined>(undefined);

export const useProducts = () => {
  const context = useContext(ProductContext);
  if (!context) {
    throw new Error('useProducts deve ser usado dentro de um ProductProvider');
  }
  return context;
};

interface ProductProviderProps {
  children: React.ReactNode;
}

export const ProductProvider: React.FC<ProductProviderProps> = ({ children }) => {
  const [state, setState] = useState<ProductState>(initialState);

  // Carregar dados iniciais
  useEffect(() => {
    loadFromCache();
    loadCategories();
    loadProducts();
  }, []);

  // Aplicar filtros quando mudam
  useEffect(() => {
    applyFilters();
  }, [state.products, state.filters, state.selectedCategory]);

  const loadFromCache = async () => {
    try {
      const cachedProducts = await AsyncStorage.getItem('cached_products');
      const cachedCategories = await AsyncStorage.getItem('cached_categories');
      const lastSync = await AsyncStorage.getItem('products_last_sync');

      if (cachedProducts && cachedCategories) {
        setState(prev => ({
          ...prev,
          products: JSON.parse(cachedProducts),
          categories: JSON.parse(cachedCategories),
          lastSync: lastSync ? new Date(lastSync) : null,
        }));
      }
    } catch (error) {
      console.error('Erro ao carregar cache de produtos:', error);
    }
  };

  const loadProducts = async (forceRefresh = false): Promise<void> => {
    // Se não forçar refresh e já temos dados recentes, não recarregar
    if (!forceRefresh && state.products.length > 0 && state.lastSync) {
      const timeDiff = Date.now() - state.lastSync.getTime();
      if (timeDiff < 10 * 60 * 1000) { // 10 minutos
        return;
      }
    }

    setState(prev => ({ ...prev, isLoading: true, error: null }));

    try {
      const response = await apiService.get('/pdv-mobile/produtos');
      
      if (response.success) {
        const products = response.produtos || [];
        
        // Salvar no cache
        await AsyncStorage.setItem('cached_products', JSON.stringify(products));
        await AsyncStorage.setItem('products_last_sync', new Date().toISOString());

        setState(prev => ({
          ...prev,
          products,
          isLoading: false,
          lastSync: new Date(),
          error: null,
        }));
      } else {
        throw new Error(response.message || 'Erro ao carregar produtos');
      }
    } catch (error: any) {
      console.error('Erro ao carregar produtos:', error);
      setState(prev => ({
        ...prev,
        isLoading: false,
        error: error.message || 'Erro ao carregar produtos',
      }));
    }
  };

  const loadCategories = async (forceRefresh = false): Promise<void> => {
    // Se não forçar refresh e já temos categorias, não recarregar
    if (!forceRefresh && state.categories.length > 0) {
      return;
    }

    try {
      const response = await apiService.get('/pdv-mobile/categorias');
      
      if (response.success) {
        const categories = response.categorias || [];
        
        // Salvar no cache
        await AsyncStorage.setItem('cached_categories', JSON.stringify(categories));

        setState(prev => ({
          ...prev,
          categories,
        }));
      } else {
        throw new Error(response.message || 'Erro ao carregar categorias');
      }
    } catch (error: any) {
      console.error('Erro ao carregar categorias:', error);
      setState(prev => ({
        ...prev,
        error: error.message || 'Erro ao carregar categorias',
      }));
    }
  };

  const setFilters = (filters: ProductFilters) => {
    setState(prev => ({
      ...prev,
      filters: { ...prev.filters, ...filters },
    }));
  };

  const setSelectedCategory = (categoryId: number | null) => {
    setState(prev => ({
      ...prev,
      selectedCategory: categoryId,
      filters: {
        ...prev.filters,
        categoria_id: categoryId || undefined,
      },
    }));
  };

  const searchProducts = (query: string) => {
    setFilters({ search: query });
  };

  const applyFilters = () => {
    let filtered = [...state.products];

    // Filtro por categoria selecionada
    if (state.selectedCategory) {
      filtered = filtered.filter(product => product.categoria_id === state.selectedCategory);
    }

    // Filtro por busca de texto
    if (state.filters.search && state.filters.search.trim()) {
      const searchTerm = state.filters.search.toLowerCase().trim();
      filtered = filtered.filter(product =>
        product.nome.toLowerCase().includes(searchTerm) ||
        product.descricao.toLowerCase().includes(searchTerm) ||
        product.categoria_nome.toLowerCase().includes(searchTerm)
      );
    }

    // Filtro por disponibilidade
    if (state.filters.disponivel_apenas) {
      filtered = filtered.filter(product => product.disponivel);
    }

    // Filtro por preço mínimo
    if (state.filters.preco_min !== undefined) {
      filtered = filtered.filter(product => product.preco >= state.filters.preco_min!);
    }

    // Filtro por preço máximo
    if (state.filters.preco_max !== undefined) {
      filtered = filtered.filter(product => product.preco <= state.filters.preco_max!);
    }

    setState(prev => ({
      ...prev,
      filteredProducts: filtered,
    }));
  };

  const getProductById = (id: number): Product | undefined => {
    return state.products.find(product => product.id === id);
  };

  const getCategoryById = (id: number): Category | undefined => {
    return state.categories.find(category => category.id === id);
  };

  const clearError = () => {
    setState(prev => ({ ...prev, error: null }));
  };

  const syncProducts = async (): Promise<void> => {
    await Promise.all([
      loadCategories(true),
      loadProducts(true)
    ]);
  };

  const contextValue: ProductContextType = {
    state,
    loadProducts,
    loadCategories,
    setFilters,
    setSelectedCategory,
    searchProducts,
    getProductById,
    getCategoryById,
    clearError,
    syncProducts,
  };

  return (
    <ProductContext.Provider value={contextValue}>
      {children}
    </ProductContext.Provider>
  );
};
