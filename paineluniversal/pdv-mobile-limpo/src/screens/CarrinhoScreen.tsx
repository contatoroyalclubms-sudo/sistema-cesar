import React from 'react';
import { View, Text, StyleSheet, ScrollView, TouchableOpacity, Alert } from 'react-native';
import { useCarrinho } from '../context/CarrinhoContext';

export default function CarrinhoScreen() {
  const { 
    itens, 
    aumentarQuantidade, 
    diminuirQuantidade, 
    removerItem, 
    limparCarrinho, 
    getTotalValor 
  } = useCarrinho();

  const handleLimparCarrinho = () => {
    Alert.alert(
      'Limpar Carrinho',
      'Tem certeza que deseja remover todos os itens do carrinho?',
      [
        { text: 'Cancelar', style: 'cancel' },
        { 
          text: 'Limpar', 
          style: 'destructive',
          onPress: () => {
            limparCarrinho();
            Alert.alert('Carrinho Limpo! 🗑️', 'Todos os itens foram removidos');
          }
        },
      ]
    );
  };

  const handleFinalizarPedido = () => {
    if (itens.length === 0) {
      Alert.alert('Carrinho Vazio', 'Adicione produtos antes de finalizar o pedido');
      return;
    }

    Alert.alert(
      'Finalizar Pedido',
      `Total: R$ ${getTotalValor().toFixed(2)}\n\nDeseja confirmar o pedido?`,
      [
        { text: 'Cancelar', style: 'cancel' },
        { 
          text: 'Confirmar', 
          onPress: () => {
            Alert.alert(
              'Pedido Confirmado! ✅',
              'O pedido foi enviado para a cozinha',
              [{ text: 'OK', onPress: limparCarrinho }]
            );
          }
        },
      ]
    );
  };

  const handleRemoverItem = (itemId: number, nomeItem: string) => {
    Alert.alert(
      'Remover Item',
      `Deseja remover "${nomeItem}" do carrinho?`,
      [
        { text: 'Cancelar', style: 'cancel' },
        { 
          text: 'Remover', 
          style: 'destructive',
          onPress: () => removerItem(itemId)
        },
      ]
    );
  };

  return (
    <ScrollView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>🛒 CARRINHO</Text>
        <Text style={styles.subtitle}>Itens do Pedido Atual</Text>
        {itens.length > 0 && (
          <View style={styles.itemCountBadge}>
            <Text style={styles.itemCountText}>{itens.length} tipos de produtos</Text>
          </View>
        )}
      </View>

      {itens.length > 0 ? (
        <>
          <View style={styles.itemsContainer}>
            {itens.map((item) => (
              <View key={item.id} style={styles.itemCard}>
                <View style={styles.itemHeader}>
                  <View style={styles.itemInfo}>
                    <Text style={styles.itemCategory}>{item.categoria}</Text>
                    <Text style={styles.itemName}>{item.nome}</Text>
                    <Text style={styles.itemPrice}>R$ {item.preco.toFixed(2)} cada</Text>
                  </View>
                  
                  <TouchableOpacity 
                    style={styles.removeButton}
                    onPress={() => handleRemoverItem(item.id, item.nome)}
                  >
                    <Text style={styles.removeButtonText}>✕</Text>
                  </TouchableOpacity>
                </View>
                
                <View style={styles.quantityContainer}>
                  <TouchableOpacity 
                    style={styles.quantityButton}
                    onPress={() => diminuirQuantidade(item.id)}
                  >
                    <Text style={styles.quantityButtonText}>-</Text>
                  </TouchableOpacity>
                  
                  <Text style={styles.quantityText}>{item.quantidade}</Text>
                  
                  <TouchableOpacity 
                    style={styles.quantityButton}
                    onPress={() => aumentarQuantidade(item.id)}
                  >
                    <Text style={styles.quantityButtonText}>+</Text>
                  </TouchableOpacity>
                </View>

                <Text style={styles.itemTotal}>
                  Subtotal: R$ {(item.preco * item.quantidade).toFixed(2)}
                </Text>
              </View>
            ))}
          </View>

          <View style={styles.totalContainer}>
            <View style={styles.totalRow}>
              <Text style={styles.totalLabel}>Total do Pedido:</Text>
              <Text style={styles.totalValue}>R$ {getTotalValor().toFixed(2)}</Text>
            </View>
            <Text style={styles.totalItems}>
              {itens.reduce((total, item) => total + item.quantidade, 0)} itens
            </Text>
          </View>

          <View style={styles.actionsContainer}>
            <TouchableOpacity 
              style={styles.clearButton}
              onPress={handleLimparCarrinho}
            >
              <Text style={styles.clearButtonText}>🗑️ LIMPAR CARRINHO</Text>
            </TouchableOpacity>

            <TouchableOpacity 
              style={styles.checkoutButton}
              onPress={handleFinalizarPedido}
            >
              <Text style={styles.checkoutButtonText}>✅ FINALIZAR PEDIDO</Text>
            </TouchableOpacity>
          </View>
        </>
      ) : (
        <View style={styles.emptyContainer}>
          <Text style={styles.emptyIcon}>🛒</Text>
          <Text style={styles.emptyTitle}>Carrinho Vazio</Text>
          <Text style={styles.emptyText}>Adicione produtos na aba "Produtos" para começar um pedido</Text>
          <View style={styles.emptyTip}>
            <Text style={styles.emptyTipText}>💡 Dica: Use a busca para encontrar produtos rapidamente</Text>
          </View>
        </View>
      )}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f8fafc',
  },
  header: {
    backgroundColor: '#dc2626',
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
    color: '#fecaca',
    textAlign: 'center',
    marginTop: 5,
  },
  itemCountBadge: {
    backgroundColor: '#fbbf24',
    paddingHorizontal: 15,
    paddingVertical: 8,
    borderRadius: 20,
    alignSelf: 'center',
    marginTop: 10,
  },
  itemCountText: {
    color: '#374151',
    fontSize: 14,
    fontWeight: 'bold',
  },
  itemsContainer: {
    padding: 20,
  },
  itemCard: {
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
  itemHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: 15,
  },
  itemInfo: {
    flex: 1,
  },
  itemCategory: {
    fontSize: 14,
    color: '#6b7280',
    marginBottom: 5,
  },
  itemName: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#374151',
    marginBottom: 5,
  },
  itemPrice: {
    fontSize: 14,
    color: '#6b7280',
  },
  removeButton: {
    backgroundColor: '#ef4444',
    width: 30,
    height: 30,
    borderRadius: 15,
    justifyContent: 'center',
    alignItems: 'center',
  },
  removeButtonText: {
    color: '#ffffff',
    fontSize: 16,
    fontWeight: 'bold',
  },
  quantityContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginBottom: 10,
  },
  quantityButton: {
    backgroundColor: '#3b82f6',
    width: 40,
    height: 40,
    borderRadius: 20,
    justifyContent: 'center',
    alignItems: 'center',
  },
  quantityButtonText: {
    color: '#ffffff',
    fontSize: 18,
    fontWeight: 'bold',
  },
  quantityText: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#374151',
  },
  itemTotal: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#059669',
    textAlign: 'right',
  },
  totalContainer: {
    backgroundColor: '#ffffff',
    padding: 25,
    margin: 20,
    borderRadius: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  totalRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 5,
  },
  totalLabel: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#374151',
  },
  totalValue: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#059669',
  },
  totalItems: {
    fontSize: 14,
    color: '#6b7280',
    textAlign: 'center',
  },
  actionsContainer: {
    padding: 20,
    gap: 15,
  },
  clearButton: {
    backgroundColor: '#6b7280',
    padding: 18,
    borderRadius: 10,
    alignItems: 'center',
  },
  clearButtonText: {
    color: '#ffffff',
    fontSize: 16,
    fontWeight: 'bold',
  },
  checkoutButton: {
    backgroundColor: '#059669',
    padding: 18,
    borderRadius: 10,
    alignItems: 'center',
  },
  checkoutButtonText: {
    color: '#ffffff',
    fontSize: 18,
    fontWeight: 'bold',
  },
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 40,
  },
  emptyIcon: {
    fontSize: 64,
    marginBottom: 20,
  },
  emptyTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#374151',
    marginBottom: 10,
  },
  emptyText: {
    fontSize: 16,
    color: '#6b7280',
    textAlign: 'center',
    marginBottom: 20,
  },
  emptyTip: {
    backgroundColor: '#dbeafe',
    padding: 15,
    borderRadius: 10,
    borderLeftWidth: 4,
    borderLeftColor: '#3b82f6',
  },
  emptyTipText: {
    fontSize: 14,
    color: '#1e40af',
    fontStyle: 'italic',
    textAlign: 'center',
  },
});
