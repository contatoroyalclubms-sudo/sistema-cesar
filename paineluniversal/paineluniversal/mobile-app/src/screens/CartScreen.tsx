import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  FlatList,
  TouchableOpacity,
  Alert,
  ActivityIndicator,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useNavigation } from '@react-navigation/native';
import { Ionicons } from '@expo/vector-icons';
import { theme } from '../styles/theme';
import { useCart } from '../contexts/CartContext';

interface CartItemProps {
  item: any;
  onUpdateQuantity: (productId: number, quantity: number) => void;
  onRemove: (productId: number) => void;
  onUpdateNotes: (productId: number, notes: string) => void;
}

const CartItem: React.FC<CartItemProps> = ({ 
  item, 
  onUpdateQuantity, 
  onRemove, 
  onUpdateNotes 
}) => {
  const formatPrice = (price: number): string => {
    return `R$ ${price.toFixed(2).replace('.', ',')}`;
  };

  return (
    <View style={styles.cartItem}>
      <View style={styles.itemInfo}>
        <Text style={styles.itemName}>{item.nome}</Text>
        <Text style={styles.itemPrice}>{formatPrice(item.preco)}</Text>
        {item.observacoes && (
          <Text style={styles.itemNotes}>Obs: {item.observacoes}</Text>
        )}
      </View>

      <View style={styles.itemActions}>
        <View style={styles.quantityControls}>
          <TouchableOpacity
            style={styles.quantityButton}
            onPress={() => onUpdateQuantity(item.produto_id, item.quantidade - 1)}
          >
            <Ionicons name="remove" size={16} color={theme.colors.text} />
          </TouchableOpacity>
          
          <Text style={styles.quantityText}>{item.quantidade}</Text>
          
          <TouchableOpacity
            style={styles.quantityButton}
            onPress={() => onUpdateQuantity(item.produto_id, item.quantidade + 1)}
          >
            <Ionicons name="add" size={16} color={theme.colors.text} />
          </TouchableOpacity>
        </View>

        <Text style={styles.subtotal}>{formatPrice(item.subtotal)}</Text>

        <TouchableOpacity
          style={styles.removeButton}
          onPress={() => onRemove(item.produto_id)}
        >
          <Ionicons name="trash-outline" size={16} color={theme.colors.error} />
        </TouchableOpacity>
      </View>
    </View>
  );
};

const CartScreen: React.FC = () => {
  const navigation = useNavigation();
  const { 
    state: cartState, 
    updateQuantity, 
    removeItem, 
    clearCart, 
    submitOrder,
    setOrderInfo,
    updateItemNotes 
  } = useCart();

  const [isSubmitting, setIsSubmitting] = useState(false);
  const [orderType, setOrderType] = useState<'mesa' | 'balcao' | 'delivery'>('mesa');
  const [customerInfo, setCustomerInfo] = useState({
    mesa: '',
    cpf_cliente: '',
    nome_cliente: '',
    observacoes: '',
  });

  useEffect(() => {
    // Configurar informações do pedido
    setOrderInfo({
      tipo_pedido: orderType,
      ...customerInfo,
    });
  }, [orderType, customerInfo]);

  const handleUpdateQuantity = (productId: number, quantity: number) => {
    updateQuantity(productId, quantity);
  };

  const handleRemoveItem = (productId: number) => {
    Alert.alert(
      'Remover Item',
      'Deseja remover este item do carrinho?',
      [
        { text: 'Cancelar', style: 'cancel' },
        { text: 'Remover', style: 'destructive', onPress: () => removeItem(productId) }
      ]
    );
  };

  const handleClearCart = () => {
    Alert.alert(
      'Limpar Carrinho',
      'Deseja remover todos os itens do carrinho?',
      [
        { text: 'Cancelar', style: 'cancel' },
        { text: 'Limpar', style: 'destructive', onPress: clearCart }
      ]
    );
  };

  const handleSubmitOrder = async () => {
    if (cartState.items.length === 0) {
      Alert.alert('Erro', 'Carrinho está vazio');
      return;
    }

    // Validações baseadas no tipo de pedido
    if (orderType === 'mesa' && !customerInfo.mesa.trim()) {
      Alert.alert('Erro', 'Por favor, informe o número da mesa');
      return;
    }

    setIsSubmitting(true);

    try {
      const order = await submitOrder();
      
      Alert.alert(
        'Pedido Enviado!',
        `Pedido ${order.id || 'offline'} foi enviado com sucesso`,
        [
          { 
            text: 'OK', 
            onPress: () => navigation.navigate('OrderSuccess', { order })
          }
        ]
      );

    } catch (error: any) {
      console.error('Erro ao enviar pedido:', error);
      
      // Se foi salvo offline, mostrar mensagem apropriada
      if (error.message?.includes('offline')) {
        Alert.alert(
          'Pedido Salvo',
          'Sem conexão. O pedido foi salvo e será enviado quando a conexão for reestabelecida.',
          [{ text: 'OK' }]
        );
      } else {
        Alert.alert('Erro', error.message || 'Erro ao enviar pedido');
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  const formatPrice = (price: number): string => {
    return `R$ ${price.toFixed(2).replace('.', ',')}`;
  };

  if (cartState.items.length === 0) {
    return (
      <SafeAreaView style={styles.container}>
        <View style={styles.header}>
          <TouchableOpacity
            style={styles.backButton}
            onPress={() => navigation.goBack()}
          >
            <Ionicons name="arrow-back" size={24} color={theme.colors.text} />
          </TouchableOpacity>
          <Text style={styles.title}>Carrinho</Text>
        </View>

        <View style={styles.emptyContainer}>
          <Ionicons name="basket-outline" size={80} color={theme.colors.textSecondary} />
          <Text style={styles.emptyTitle}>Carrinho vazio</Text>
          <Text style={styles.emptySubtext}>
            Adicione produtos do cardápio para começar
          </Text>
          
          <TouchableOpacity
            style={styles.addProductsButton}
            onPress={() => navigation.navigate('ProductsScreen')}
          >
            <Text style={styles.addProductsButtonText}>Ver Cardápio</Text>
          </TouchableOpacity>
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
        
        <Text style={styles.title}>Carrinho ({cartState.items.length})</Text>
        
        <TouchableOpacity
          style={styles.clearButton}
          onPress={handleClearCart}
        >
          <Ionicons name="trash-outline" size={24} color={theme.colors.error} />
        </TouchableOpacity>
      </View>

      {/* Lista de itens */}
      <FlatList
        data={cartState.items}
        renderItem={({ item }) => (
          <CartItem
            item={item}
            onUpdateQuantity={handleUpdateQuantity}
            onRemove={handleRemoveItem}
            onUpdateNotes={updateItemNotes}
          />
        )}
        keyExtractor={(item) => `cart-${item.produto_id}`}
        contentContainerStyle={styles.itemsList}
      />

      {/* Tipo de pedido */}
      <View style={styles.orderTypeContainer}>
        <Text style={styles.sectionTitle}>Tipo de Pedido</Text>
        <View style={styles.orderTypeButtons}>
          {[
            { key: 'mesa', label: 'Mesa', icon: 'restaurant-outline' },
            { key: 'balcao', label: 'Balcão', icon: 'storefront-outline' },
            { key: 'delivery', label: 'Delivery', icon: 'bicycle-outline' },
          ].map((type) => (
            <TouchableOpacity
              key={type.key}
              style={[
                styles.orderTypeButton,
                orderType === type.key && styles.orderTypeButtonSelected
              ]}
              onPress={() => setOrderType(type.key as any)}
            >
              <Ionicons 
                name={type.icon as any} 
                size={20} 
                color={orderType === type.key ? theme.colors.background : theme.colors.text} 
              />
              <Text style={[
                styles.orderTypeButtonText,
                orderType === type.key && styles.orderTypeButtonTextSelected
              ]}>
                {type.label}
              </Text>
            </TouchableOpacity>
          ))}
        </View>
      </View>

      {/* Resumo e envio */}
      <View style={styles.summaryContainer}>
        <View style={styles.totalContainer}>
          <Text style={styles.totalLabel}>Total</Text>
          <Text style={styles.totalValue}>{formatPrice(cartState.total)}</Text>
        </View>

        {cartState.error && (
          <Text style={styles.errorText}>{cartState.error}</Text>
        )}

        <TouchableOpacity
          style={[
            styles.submitButton,
            (isSubmitting || cartState.isLoading) && styles.submitButtonDisabled
          ]}
          onPress={handleSubmitOrder}
          disabled={isSubmitting || cartState.isLoading}
        >
          {(isSubmitting || cartState.isLoading) ? (
            <ActivityIndicator color={theme.colors.background} size="small" />
          ) : (
            <>
              <Ionicons name="send" size={20} color={theme.colors.background} />
              <Text style={styles.submitButtonText}>Enviar Pedido</Text>
            </>
          )}
        </TouchableOpacity>
      </View>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: theme.colors.background,
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: theme.spacing.lg,
    paddingVertical: theme.spacing.md,
    borderBottomWidth: 1,
    borderBottomColor: theme.colors.border,
  },
  backButton: {
    padding: theme.spacing.sm,
  },
  title: {
    fontSize: 20,
    fontWeight: 'bold',
    color: theme.colors.text,
  },
  clearButton: {
    padding: theme.spacing.sm,
  },
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: theme.spacing.xl,
  },
  emptyTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: theme.colors.text,
    marginTop: theme.spacing.lg,
    marginBottom: theme.spacing.sm,
  },
  emptySubtext: {
    fontSize: 16,
    color: theme.colors.textSecondary,
    textAlign: 'center',
    marginBottom: theme.spacing.xl,
  },
  addProductsButton: {
    backgroundColor: theme.colors.primary,
    borderRadius: theme.borderRadius.md,
    paddingHorizontal: theme.spacing.xl,
    paddingVertical: theme.spacing.lg,
  },
  addProductsButtonText: {
    color: theme.colors.background,
    fontSize: 16,
    fontWeight: 'bold',
  },
  itemsList: {
    paddingHorizontal: theme.spacing.lg,
  },
  cartItem: {
    backgroundColor: theme.colors.surface,
    borderRadius: theme.borderRadius.md,
    padding: theme.spacing.md,
    marginVertical: theme.spacing.sm,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  itemInfo: {
    flex: 1,
    marginRight: theme.spacing.md,
  },
  itemName: {
    fontSize: 16,
    fontWeight: '600',
    color: theme.colors.text,
    marginBottom: theme.spacing.xs,
  },
  itemPrice: {
    fontSize: 14,
    color: theme.colors.textSecondary,
    marginBottom: theme.spacing.xs,
  },
  itemNotes: {
    fontSize: 12,
    color: theme.colors.info,
    fontStyle: 'italic',
  },
  itemActions: {
    alignItems: 'center',
  },
  quantityControls: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: theme.spacing.sm,
  },
  quantityButton: {
    backgroundColor: theme.colors.border,
    borderRadius: theme.borderRadius.sm,
    width: 30,
    height: 30,
    justifyContent: 'center',
    alignItems: 'center',
  },
  quantityText: {
    fontSize: 16,
    fontWeight: 'bold',
    color: theme.colors.text,
    marginHorizontal: theme.spacing.md,
    minWidth: 30,
    textAlign: 'center',
  },
  subtotal: {
    fontSize: 16,
    fontWeight: 'bold',
    color: theme.colors.success,
    marginBottom: theme.spacing.sm,
  },
  removeButton: {
    padding: theme.spacing.xs,
  },
  orderTypeContainer: {
    padding: theme.spacing.lg,
    borderTopWidth: 1,
    borderTopColor: theme.colors.border,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: theme.colors.text,
    marginBottom: theme.spacing.md,
  },
  orderTypeButtons: {
    flexDirection: 'row',
    justifyContent: 'space-around',
  },
  orderTypeButton: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: theme.colors.surface,
    borderRadius: theme.borderRadius.md,
    paddingVertical: theme.spacing.md,
    marginHorizontal: theme.spacing.sm,
    borderWidth: 1,
    borderColor: theme.colors.border,
  },
  orderTypeButtonSelected: {
    backgroundColor: theme.colors.primary,
    borderColor: theme.colors.primary,
  },
  orderTypeButtonText: {
    fontSize: 14,
    color: theme.colors.text,
    marginLeft: theme.spacing.xs,
    fontWeight: '500',
  },
  orderTypeButtonTextSelected: {
    color: theme.colors.background,
  },
  summaryContainer: {
    padding: theme.spacing.lg,
    borderTopWidth: 1,
    borderTopColor: theme.colors.border,
    backgroundColor: theme.colors.surface,
  },
  totalContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: theme.spacing.lg,
  },
  totalLabel: {
    fontSize: 20,
    fontWeight: 'bold',
    color: theme.colors.text,
  },
  totalValue: {
    fontSize: 24,
    fontWeight: 'bold',
    color: theme.colors.success,
  },
  errorText: {
    color: theme.colors.error,
    fontSize: 14,
    textAlign: 'center',
    marginBottom: theme.spacing.md,
  },
  submitButton: {
    backgroundColor: theme.colors.primary,
    borderRadius: theme.borderRadius.md,
    paddingVertical: theme.spacing.lg,
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
  },
  submitButtonDisabled: {
    backgroundColor: theme.colors.textSecondary,
  },
  submitButtonText: {
    color: theme.colors.background,
    fontSize: 18,
    fontWeight: 'bold',
    marginLeft: theme.spacing.sm,
  },
});

export default CartScreen;
