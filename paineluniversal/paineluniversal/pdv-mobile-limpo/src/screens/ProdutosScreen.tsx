import React, { useState } from 'react';
import { View, Text, StyleSheet, ScrollView, TouchableOpacity, TextInput, Alert } from 'react-native';
import { useCarrinho, Produto } from '../context/CarrinhoContext';
import CategoriasFilter from '../components/CategoriasFilter';

export default function ProdutosScreen() {
  const [busca, setBusca] = useState('');
  const [categoriaFiltro, setCategoriaFiltro] = useState('');
  const { adicionarItem, getTotalItens } = useCarrinho();

  const produtos: Produto[] = [
    { id: 1, nome: 'Cerveja Heineken', preco: 12.50, categoria: 'Bebidas' },
    { id: 2, nome: 'Hambúrguer Artesanal', preco: 25.90, categoria: 'Lanches' },
    { id: 3, nome: 'Água Mineral', preco: 4.00, categoria: 'Bebidas' },
    { id: 4, nome: 'Batata Frita', preco: 15.00, categoria: 'Acompanhamentos' },
    { id: 5, nome: 'Refrigerante Coca-Cola', preco: 8.00, categoria: 'Bebidas' },
    { id: 6, nome: 'Pizza Margherita', preco: 35.00, categoria: 'Pizzas' },
    { id: 7, nome: 'Salada Caesar', preco: 18.50, categoria: 'Saladas' },
    { id: 8, nome: 'Café Expresso', preco: 6.00, categoria: 'Cafés' },
  ];

  const produtosFiltrados = produtos.filter(produto => {
    const matchBusca = produto.nome.toLowerCase().includes(busca.toLowerCase()) ||
                     produto.categoria.toLowerCase().includes(busca.toLowerCase());
    
    const matchCategoria = categoriaFiltro === '' || 
                          produto.categoria.toLowerCase() === categoriaFiltro.toLowerCase();
    
    return matchBusca && matchCategoria;
  });

  const handleAdicionarProduto = (produto: Produto) => {
    adicionarItem(produto);
    Alert.alert(
      'Produto Adicionado! ✅',
      `${produto.nome} foi adicionado ao carrinho`,
      [{ text: 'OK' }]
    );
  };

  const getCategoriaEmoji = (categoria: string) => {
    const emojiMap: { [key: string]: string } = {
      'Bebidas': '🍺',
      'Lanches': '🍔',
      'Acompanhamentos': '🍟',
      'Pizzas': '🍕',
      'Saladas': '🥗',
      'Cafés': '☕',
    };
    return emojiMap[categoria] || '📦';
  };

  return (
    <ScrollView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>📦 PRODUTOS</Text>
        <Text style={styles.subtitle}>Catálogo do Estabelecimento</Text>
        {getTotalItens() > 0 && (
          <View style={styles.cartBadge}>
            <Text style={styles.cartBadgeText}>{getTotalItens()} itens no carrinho</Text>
          </View>
        )}
      </View>

      <View style={styles.searchContainer}>
        <TextInput
          style={styles.searchInput}
          placeholder="🔍 Buscar produtos..."
          value={busca}
          onChangeText={setBusca}
          placeholderTextColor="#9ca3af"
        />
        {busca.length > 0 && (
          <TouchableOpacity 
            style={styles.clearSearchButton}
            onPress={() => setBusca('')}
          >
            <Text style={styles.clearSearchText}>✕</Text>
          </TouchableOpacity>
        )}
      </View>

      <CategoriasFilter onSelectCategory={setCategoriaFiltro} />

      {categoriaFiltro && (
        <View style={styles.activeFilterContainer}>
          <Text style={styles.activeFilterText}>
            Filtrando por: {categoriaFiltro}
          </Text>
          <TouchableOpacity 
            style={styles.clearFilterButton}
            onPress={() => setCategoriaFiltro('')}
          >
            <Text style={styles.clearFilterText}>Limpar filtro</Text>
          </TouchableOpacity>
        </View>
      )}

      <View style={styles.productsContainer}>
        {produtosFiltrados.length > 0 ? (
          produtosFiltrados.map((produto) => (
            <TouchableOpacity key={produto.id} style={styles.productCard}>
              <View style={styles.productInfo}>
                <Text style={styles.productCategory}>
                  {getCategoriaEmoji(produto.categoria)} {produto.categoria}
                </Text>
                <Text style={styles.productName}>{produto.nome}</Text>
                <Text style={styles.productPrice}>R$ {produto.preco.toFixed(2)}</Text>
              </View>
              
              <TouchableOpacity 
                style={styles.addButton}
                onPress={() => handleAdicionarProduto(produto)}
              >
                <Text style={styles.addButtonText}>+ ADICIONAR</Text>
              </TouchableOpacity>
            </TouchableOpacity>
          ))
        ) : (
          <View style={styles.noResultsContainer}>
            <Text style={styles.noResultsIcon}>🔍</Text>
            <Text style={styles.noResultsTitle}>Nenhum produto encontrado</Text>
            <Text style={styles.noResultsText}>
              {categoriaFiltro 
                ? `Nenhum produto encontrado na categoria "${categoriaFiltro}"`
                : 'Tente buscar por outro termo ou categoria'
              }
            </Text>
          </View>
        )}
      </View>

      <View style={styles.footer}>
        <Text style={styles.footerText}>
          {busca || categoriaFiltro 
            ? `${produtosFiltrados.length} de ${produtos.length} produtos` 
            : `Total: ${produtos.length} produtos disponíveis`
          }
        </Text>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f8fafc',
  },
  header: {
    backgroundColor: '#059669',
    padding: 20,
    paddingTop: 60,
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#ffffff',
    textAlign: 'center',
  },
  subtitle: {
    fontSize: 16,
    color: '#d1fae5',
    textAlign: 'center',
    marginTop: 5,
  },
  cartBadge: {
    backgroundColor: '#fbbf24',
    paddingHorizontal: 15,
    paddingVertical: 8,
    borderRadius: 20,
    alignSelf: 'center',
    marginTop: 10,
  },
  cartBadgeText: {
    color: '#374151',
    fontSize: 14,
    fontWeight: 'bold',
  },
  searchContainer: {
    padding: 20,
    position: 'relative',
  },
  searchInput: {
    backgroundColor: '#ffffff',
    padding: 15,
    borderRadius: 10,
    borderWidth: 1,
    borderColor: '#e5e7eb',
    fontSize: 16,
    color: '#374151',
  },
  clearSearchButton: {
    position: 'absolute',
    right: 30,
    top: 35,
    backgroundColor: '#ef4444',
    width: 24,
    height: 24,
    borderRadius: 12,
    justifyContent: 'center',
    alignItems: 'center',
  },
  clearSearchText: {
    color: '#ffffff',
    fontSize: 12,
    fontWeight: 'bold',
  },
  activeFilterContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginHorizontal: 20,
    marginBottom: 10,
    padding: 12,
    backgroundColor: '#dbeafe',
    borderRadius: 8,
    borderLeftWidth: 4,
    borderLeftColor: '#3b82f6',
  },
  activeFilterText: {
    fontSize: 14,
    color: '#1e40af',
    fontWeight: '600',
  },
  clearFilterButton: {
    backgroundColor: '#3b82f6',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 6,
  },
  clearFilterText: {
    color: '#ffffff',
    fontSize: 12,
    fontWeight: 'bold',
  },
  productsContainer: {
    padding: 20,
    paddingTop: 0,
  },
  productCard: {
    backgroundColor: '#ffffff',
    padding: 20,
    borderRadius: 12,
    marginBottom: 15,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  productInfo: {
    marginBottom: 15,
  },
  productCategory: {
    fontSize: 14,
    color: '#6b7280',
    marginBottom: 5,
  },
  productName: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#374151',
    marginBottom: 5,
  },
  productPrice: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#059669',
  },
  addButton: {
    backgroundColor: '#3b82f6',
    padding: 12,
    borderRadius: 8,
    alignItems: 'center',
  },
  addButtonText: {
    color: '#ffffff',
    fontSize: 14,
    fontWeight: 'bold',
  },
  noResultsContainer: {
    alignItems: 'center',
    padding: 40,
  },
  noResultsIcon: {
    fontSize: 64,
    marginBottom: 20,
  },
  noResultsTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#374151',
    marginBottom: 10,
  },
  noResultsText: {
    fontSize: 16,
    color: '#6b7280',
    textAlign: 'center',
  },
  footer: {
    padding: 20,
    alignItems: 'center',
  },
  footerText: {
    color: '#6b7280',
    fontSize: 14,
  },
});
