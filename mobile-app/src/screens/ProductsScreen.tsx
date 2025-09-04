import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  FlatList,
  TouchableOpacity,
  TextInput,
  ActivityIndicator,
  RefreshControl,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useNavigation } from '@react-navigation/native';
import { Ionicons } from '@expo/vector-icons';
import { theme } from '../styles/theme';
import { useProducts } from '../contexts/ProductContext';
import { useCart } from '../contexts/CartContext';

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
}

interface Category {
  id: number;
  nome: string;
  produtos_count: number;
}

const ProductsScreen: React.FC = () => {
  const navigation = useNavigation();
  const { state: productsState, setSelectedCategory, searchProducts, syncProducts } = useProducts();
  const { addItem, getItemQuantity } = useCart();
  
  const [searchQuery, setSearchQuery] = useState('');
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    // Sincronizar produtos se necessário
    if (productsState.products.length === 0) {
      syncProducts();
    }
  }, []);

  const handleCategorySelect = (categoryId: number | null) => {
    setSelectedCategory(categoryId);
  };

  const handleSearch = (query: string) => {
    setSearchQuery(query);
    searchProducts(query);
  };

  const handleAddToCart = (product: Product) => {
    if (!product.disponivel) {
      return;
    }

    addItem(product.id, product.nome, product.preco);
    
    // Feedback visual (pode adicionar toast/snackbar aqui)
    console.log(`Produto ${product.nome} adicionado ao carrinho`);
  };

  const handleRefresh = async () => {
    setRefreshing(true);
    try {
      await syncProducts();
    } catch (error) {
      console.error('Erro ao atualizar produtos:', error);
    } finally {
      setRefreshing(false);
    }
  };

  const formatPrice = (price: number): string => {
    return `R$ ${price.toFixed(2).replace('.', ',')}`;
  };

  const renderProduct = ({ item: product }: { item: Product }) => {
    const quantity = getItemQuantity(product.id);
    
    return (
      <View style={[
        styles.productCard,
        !product.disponivel && styles.productUnavailable
      ]}>
        <View style={styles.productInfo}>
          <Text style={styles.productName}>{product.nome}</Text>
          <Text style={styles.productDescription} numberOfLines={2}>
            {product.descricao}
          </Text>
          <Text style={styles.productCategory}>{product.categoria_nome}</Text>
          
          <View style={styles.productFooter}>
            <Text style={styles.productPrice}>
              {formatPrice(product.preco)}
            </Text>
            
            {product.tempo_preparo && (
              <View style={styles.prepTimeContainer}>
                <Ionicons name="time-outline" size={14} color={theme.colors.textSecondary} />
                <Text style={styles.prepTimeText}>
                  {product.tempo_preparo}min
                </Text>
              </View>
            )}
          </View>
        </View>

        <View style={styles.productActions}>
          {!product.disponivel ? (
            <View style={styles.unavailableContainer}>
              <Text style={styles.unavailableText}>Indisponível</Text>
            </View>
          ) : (
            <>
              {quantity > 0 && (
                <View style={styles.quantityContainer}>
                  <Text style={styles.quantityText}>{quantity}</Text>
                </View>
              )}
              
              <TouchableOpacity
                style={styles.addButton}
                onPress={() => handleAddToCart(product)}
              >
                <Ionicons name="add" size={24} color={theme.colors.background} />
              </TouchableOpacity>
            </>
          )}
        </View>
      </View>
    );
  };

  const renderCategory = ({ item: category }: { item: Category }) => {
    const isSelected = productsState.selectedCategory === category.id;
    
    return (
      <TouchableOpacity
        style={[
          styles.categoryChip,
          isSelected && styles.categoryChipSelected
        ]}
        onPress={() => handleCategorySelect(category.id)}
      >
        <Text style={[
          styles.categoryChipText,
          isSelected && styles.categoryChipTextSelected
        ]}>
          {category.nome} ({category.produtos_count})
        </Text>
      </TouchableOpacity>
    );
  };

  if (productsState.isLoading && productsState.products.length === 0) {
    return (
      <SafeAreaView style={styles.container}>
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color={theme.colors.primary} />
          <Text style={styles.loadingText}>Carregando produtos...</Text>
        </View>
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <TouchableOpacity
          style={styles.backButton}
          onPress={() => navigation.goBack()}
        >
          <Ionicons name="arrow-back" size={24} color={theme.colors.text} />
        </TouchableOpacity>
        
        <Text style={styles.title}>Cardápio</Text>
        
        <TouchableOpacity
          style={styles.cartButton}
          onPress={() => navigation.navigate('CartScreen')}
        >
          <Ionicons name="basket-outline" size={24} color={theme.colors.text} />
          {/* Badge do carrinho pode ser adicionado aqui */}
        </TouchableOpacity>
      </View>

      {/* Barra de pesquisa */}
      <View style={styles.searchContainer}>
        <View style={styles.searchInputContainer}>
          <Ionicons name="search" size={20} color={theme.colors.textSecondary} />
          <TextInput
            style={styles.searchInput}
            placeholder="Pesquisar produtos..."
            placeholderTextColor={theme.colors.textSecondary}
            value={searchQuery}
            onChangeText={handleSearch}
          />
          {searchQuery.length > 0 && (
            <TouchableOpacity onPress={() => handleSearch('')}>
              <Ionicons name="close" size={20} color={theme.colors.textSecondary} />
            </TouchableOpacity>
          )}
        </View>
      </View>

      {/* Categorias */}
      <View style={styles.categoriesContainer}>
        <FlatList
          horizontal
          data={[
            { id: null, nome: 'Todos', produtos_count: productsState.products.length },
            ...productsState.categories
          ]}
          renderItem={({ item }) => (
            <TouchableOpacity
              style={[
                styles.categoryChip,
                productsState.selectedCategory === item.id && styles.categoryChipSelected
              ]}
              onPress={() => handleCategorySelect(item.id)}
            >
              <Text style={[
                styles.categoryChipText,
                productsState.selectedCategory === item.id && styles.categoryChipTextSelected
              ]}>
                {item.nome} ({item.produtos_count})
              </Text>
            </TouchableOpacity>
          )}
          keyExtractor={(item) => `category-${item.id || 'all'}`}
          showsHorizontalScrollIndicator={false}
          contentContainerStyle={styles.categoriesList}
        />
      </View>

      {/* Lista de produtos */}
      <FlatList
        data={productsState.filteredProducts}
        renderItem={renderProduct}
        keyExtractor={(item) => `product-${item.id}`}
        contentContainerStyle={styles.productsList}
        refreshControl={
          <RefreshControl
            refreshing={refreshing}
            onRefresh={handleRefresh}
            colors={[theme.colors.primary]}
          />
        }
        ListEmptyComponent={
          <View style={styles.emptyContainer}>
            <Ionicons name="restaurant-outline" size={64} color={theme.colors.textSecondary} />
            <Text style={styles.emptyText}>
              {searchQuery ? 'Nenhum produto encontrado' : 'Nenhum produto disponível'}
            </Text>
            {searchQuery && (
              <Text style={styles.emptySubtext}>
                Tente pesquisar com outras palavras
              </Text>
            )}
          </View>
        }
      />

      {/* Erro */}
      {productsState.error && (
        <View style={styles.errorContainer}>
          <Text style={styles.errorText}>{productsState.error}</Text>
          <TouchableOpacity
            style={styles.retryButton}
            onPress={() => syncProducts()}
          >
            <Text style={styles.retryButtonText}>Tentar novamente</Text>
          </TouchableOpacity>
        </View>
      )}
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: theme.colors.background,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  loadingText: {
    marginTop: theme.spacing.md,
    fontSize: 16,
    color: theme.colors.textSecondary,
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: theme.spacing.lg,
    paddingVertical: theme.spacing.md,
  },
  backButton: {
    padding: theme.spacing.sm,
  },
  title: {
    fontSize: 20,
    fontWeight: 'bold',
    color: theme.colors.text,
  },
  cartButton: {
    padding: theme.spacing.sm,
  },
  searchContainer: {
    paddingHorizontal: theme.spacing.lg,
    paddingBottom: theme.spacing.md,
  },
  searchInputContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: theme.colors.surface,
    borderRadius: theme.borderRadius.md,
    paddingHorizontal: theme.spacing.md,
    paddingVertical: theme.spacing.sm,
  },
  searchInput: {
    flex: 1,
    marginLeft: theme.spacing.sm,
    fontSize: 16,
    color: theme.colors.text,
  },
  categoriesContainer: {
    paddingBottom: theme.spacing.md,
  },
  categoriesList: {
    paddingHorizontal: theme.spacing.lg,
  },
  categoryChip: {
    backgroundColor: theme.colors.surface,
    borderRadius: theme.borderRadius.full,
    paddingHorizontal: theme.spacing.md,
    paddingVertical: theme.spacing.sm,
    marginRight: theme.spacing.sm,
    borderWidth: 1,
    borderColor: theme.colors.border,
  },
  categoryChipSelected: {
    backgroundColor: theme.colors.primary,
    borderColor: theme.colors.primary,
  },
  categoryChipText: {
    fontSize: 14,
    color: theme.colors.text,
    fontWeight: '500',
  },
  categoryChipTextSelected: {
    color: theme.colors.background,
  },
  productsList: {
    paddingHorizontal: theme.spacing.lg,
  },
  productCard: {
    backgroundColor: theme.colors.surface,
    borderRadius: theme.borderRadius.md,
    padding: theme.spacing.md,
    marginBottom: theme.spacing.md,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  productUnavailable: {
    opacity: 0.6,
  },
  productInfo: {
    flex: 1,
    marginRight: theme.spacing.md,
  },
  productName: {
    fontSize: 16,
    fontWeight: 'bold',
    color: theme.colors.text,
    marginBottom: theme.spacing.xs,
  },
  productDescription: {
    fontSize: 14,
    color: theme.colors.textSecondary,
    marginBottom: theme.spacing.xs,
  },
  productCategory: {
    fontSize: 12,
    color: theme.colors.primary,
    marginBottom: theme.spacing.sm,
  },
  productFooter: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
  },
  productPrice: {
    fontSize: 18,
    fontWeight: 'bold',
    color: theme.colors.success,
  },
  prepTimeContainer: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  prepTimeText: {
    fontSize: 12,
    color: theme.colors.textSecondary,
    marginLeft: theme.spacing.xs,
  },
  productActions: {
    alignItems: 'center',
  },
  unavailableContainer: {
    backgroundColor: theme.colors.error + '20',
    borderRadius: theme.borderRadius.sm,
    paddingHorizontal: theme.spacing.sm,
    paddingVertical: theme.spacing.xs,
  },
  unavailableText: {
    fontSize: 12,
    color: theme.colors.error,
    fontWeight: '600',
  },
  quantityContainer: {
    backgroundColor: theme.colors.primary,
    borderRadius: theme.borderRadius.full,
    width: 24,
    height: 24,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: theme.spacing.xs,
  },
  quantityText: {
    fontSize: 12,
    fontWeight: 'bold',
    color: theme.colors.background,
  },
  addButton: {
    backgroundColor: theme.colors.primary,
    borderRadius: theme.borderRadius.full,
    width: 40,
    height: 40,
    justifyContent: 'center',
    alignItems: 'center',
  },
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingVertical: theme.spacing.xl * 3,
  },
  emptyText: {
    fontSize: 18,
    color: theme.colors.textSecondary,
    textAlign: 'center',
    marginTop: theme.spacing.lg,
  },
  emptySubtext: {
    fontSize: 14,
    color: theme.colors.textSecondary,
    textAlign: 'center',
    marginTop: theme.spacing.sm,
  },
  errorContainer: {
    backgroundColor: theme.colors.error + '20',
    padding: theme.spacing.md,
    margin: theme.spacing.lg,
    borderRadius: theme.borderRadius.md,
    borderLeftWidth: 4,
    borderLeftColor: theme.colors.error,
  },
  errorText: {
    color: theme.colors.error,
    fontSize: 14,
    marginBottom: theme.spacing.sm,
  },
  retryButton: {
    alignSelf: 'flex-start',
  },
  retryButtonText: {
    color: theme.colors.primary,
    fontSize: 14,
    fontWeight: '600',
  },
});

export default ProductsScreen;
