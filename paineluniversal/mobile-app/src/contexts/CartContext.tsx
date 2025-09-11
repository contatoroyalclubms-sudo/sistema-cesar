import React, { createContext, useContext, useReducer, useEffect } from 'react';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { apiService } from '../services/apiService';

interface CartItem {
  produto_id: number;
  nome: string;
  preco: number;
  quantidade: number;
  observacoes?: string;
  modificacoes?: string[];
  subtotal: number;
}

interface Order {
  id?: number;
  mesa?: string;
  nfc_id?: string;
  cpf_cliente?: string;
  nome_cliente?: string;
  itens: CartItem[];
  total: number;
  observacoes?: string;
  status: 'rascunho' | 'pendente' | 'preparando' | 'pronto' | 'entregue' | 'cancelado';
  created_at?: string;
  tipo_pedido: 'mesa' | 'balcao' | 'delivery';
  offline?: boolean;
}

interface CartState {
  items: CartItem[];
  total: number;
  currentOrder: Partial<Order>;
  isLoading: boolean;
  error: string | null;
  lastSave: Date | null;
  offlineOrders: Order[];
}

type CartAction =
  | { type: 'ADD_ITEM'; payload: { produto_id: number; nome: string; preco: number; observacoes?: string } }
  | { type: 'REMOVE_ITEM'; payload: number }
  | { type: 'UPDATE_QUANTITY'; payload: { produto_id: number; quantidade: number } }
  | { type: 'UPDATE_ITEM_NOTES'; payload: { produto_id: number; observacoes: string } }
  | { type: 'CLEAR_CART' }
  | { type: 'SET_ORDER_INFO'; payload: Partial<Order> }
  | { type: 'SAVE_OFFLINE_ORDER'; payload: Order }
  | { type: 'REMOVE_OFFLINE_ORDER'; payload: number }
  | { type: 'SET_LOADING'; payload: boolean }
  | { type: 'SET_ERROR'; payload: string | null }
  | { type: 'RESTORE_CART'; payload: { items: CartItem[]; currentOrder: Partial<Order> } };

const initialState: CartState = {
  items: [],
  total: 0,
  currentOrder: { tipo_pedido: 'mesa' },
  isLoading: false,
  error: null,
  lastSave: null,
  offlineOrders: [],
};

const cartReducer = (state: CartState, action: CartAction): CartState => {
  switch (action.type) {
    case 'ADD_ITEM': {
      const existingItemIndex = state.items.findIndex(
        item => item.produto_id === action.payload.produto_id
      );

      let newItems: CartItem[];
      
      if (existingItemIndex >= 0) {
        // Item já existe, incrementar quantidade
        newItems = state.items.map((item, index) => {
          if (index === existingItemIndex) {
            const newQuantity = item.quantidade + 1;
            return {
              ...item,
              quantidade: newQuantity,
              subtotal: item.preco * newQuantity,
            };
          }
          return item;
        });
      } else {
        // Novo item
        newItems = [
          ...state.items,
          {
            produto_id: action.payload.produto_id,
            nome: action.payload.nome,
            preco: action.payload.preco,
            quantidade: 1,
            observacoes: action.payload.observacoes,
            subtotal: action.payload.preco,
          },
        ];
      }

      const newTotal = newItems.reduce((sum, item) => sum + item.subtotal, 0);

      return {
        ...state,
        items: newItems,
        total: newTotal,
      };
    }

    case 'REMOVE_ITEM': {
      const newItems = state.items.filter(item => item.produto_id !== action.payload);
      const newTotal = newItems.reduce((sum, item) => sum + item.subtotal, 0);

      return {
        ...state,
        items: newItems,
        total: newTotal,
      };
    }

    case 'UPDATE_QUANTITY': {
      if (action.payload.quantidade <= 0) {
        return cartReducer(state, { type: 'REMOVE_ITEM', payload: action.payload.produto_id });
      }

      const newItems = state.items.map(item => {
        if (item.produto_id === action.payload.produto_id) {
          return {
            ...item,
            quantidade: action.payload.quantidade,
            subtotal: item.preco * action.payload.quantidade,
          };
        }
        return item;
      });

      const newTotal = newItems.reduce((sum, item) => sum + item.subtotal, 0);

      return {
        ...state,
        items: newItems,
        total: newTotal,
      };
    }

    case 'UPDATE_ITEM_NOTES': {
      const newItems = state.items.map(item => {
        if (item.produto_id === action.payload.produto_id) {
          return {
            ...item,
            observacoes: action.payload.observacoes,
          };
        }
        return item;
      });

      return {
        ...state,
        items: newItems,
      };
    }

    case 'CLEAR_CART':
      return {
        ...state,
        items: [],
        total: 0,
        currentOrder: { tipo_pedido: 'mesa' },
        error: null,
      };

    case 'SET_ORDER_INFO':
      return {
        ...state,
        currentOrder: { ...state.currentOrder, ...action.payload },
      };

    case 'SAVE_OFFLINE_ORDER':
      return {
        ...state,
        offlineOrders: [...state.offlineOrders, action.payload],
      };

    case 'REMOVE_OFFLINE_ORDER':
      return {
        ...state,
        offlineOrders: state.offlineOrders.filter(order => order.id !== action.payload),
      };

    case 'SET_LOADING':
      return {
        ...state,
        isLoading: action.payload,
      };

    case 'SET_ERROR':
      return {
        ...state,
        error: action.payload,
      };

    case 'RESTORE_CART':
      return {
        ...state,
        items: action.payload.items,
        currentOrder: action.payload.currentOrder,
        total: action.payload.items.reduce((sum, item) => sum + item.subtotal, 0),
      };

    default:
      return state;
  }
};

interface CartContextType {
  state: CartState;
  addItem: (produto_id: number, nome: string, preco: number, observacoes?: string) => void;
  removeItem: (produto_id: number) => void;
  updateQuantity: (produto_id: number, quantidade: number) => void;
  updateItemNotes: (produto_id: number, observacoes: string) => void;
  clearCart: () => void;
  setOrderInfo: (info: Partial<Order>) => void;
  submitOrder: () => Promise<Order>;
  saveCartToStorage: () => Promise<void>;
  restoreCartFromStorage: () => Promise<void>;
  syncOfflineOrders: () => Promise<void>;
  getItemQuantity: (produto_id: number) => number;
  clearError: () => void;
}

const CartContext = createContext<CartContextType | undefined>(undefined);

export const useCart = () => {
  const context = useContext(CartContext);
  if (!context) {
    throw new Error('useCart deve ser usado dentro de um CartProvider');
  }
  return context;
};

interface CartProviderProps {
  children: React.ReactNode;
}

export const CartProvider: React.FC<CartProviderProps> = ({ children }) => {
  const [state, dispatch] = useReducer(cartReducer, initialState);

  // Restaurar carrinho ao inicializar
  useEffect(() => {
    restoreCartFromStorage();
    loadOfflineOrders();
  }, []);

  // Salvar carrinho automaticamente quando mudar
  useEffect(() => {
    if (state.items.length > 0 || Object.keys(state.currentOrder).length > 1) {
      saveCartToStorage();
    }
  }, [state.items, state.currentOrder]);

  const addItem = (produto_id: number, nome: string, preco: number, observacoes?: string) => {
    dispatch({
      type: 'ADD_ITEM',
      payload: { produto_id, nome, preco, observacoes },
    });
  };

  const removeItem = (produto_id: number) => {
    dispatch({ type: 'REMOVE_ITEM', payload: produto_id });
  };

  const updateQuantity = (produto_id: number, quantidade: number) => {
    dispatch({ type: 'UPDATE_QUANTITY', payload: { produto_id, quantidade } });
  };

  const updateItemNotes = (produto_id: number, observacoes: string) => {
    dispatch({ type: 'UPDATE_ITEM_NOTES', payload: { produto_id, observacoes } });
  };

  const clearCart = () => {
    dispatch({ type: 'CLEAR_CART' });
    AsyncStorage.removeItem('cart_data');
  };

  const setOrderInfo = (info: Partial<Order>) => {
    dispatch({ type: 'SET_ORDER_INFO', payload: info });
  };

  const submitOrder = async (): Promise<Order> => {
    dispatch({ type: 'SET_LOADING', payload: true });
    dispatch({ type: 'SET_ERROR', payload: null });

    try {
      const orderData = {
        ...state.currentOrder,
        itens: state.items,
        total: state.total,
        timestamp: new Date().toISOString(),
      };

      const response = await apiService.post('/pdv-mobile/pedidos', orderData);

      if (response.success) {
        // Limpar carrinho após sucesso
        clearCart();
        
        dispatch({ type: 'SET_LOADING', payload: false });
        return response.pedido;
      } else {
        throw new Error(response.message || 'Erro ao enviar pedido');
      }

    } catch (error: any) {
      console.error('Erro ao enviar pedido:', error);
      
      // Se erro de conectividade, salvar offline
      if (error.name === 'NetworkError' || !navigator.onLine) {
        const offlineOrder: Order = {
          id: Date.now(), // ID temporário
          ...state.currentOrder,
          itens: state.items,
          total: state.total,
          status: 'pendente',
          created_at: new Date().toISOString(),
          offline: true,
        } as Order;

        dispatch({ type: 'SAVE_OFFLINE_ORDER', payload: offlineOrder });
        await saveOfflineOrders([...state.offlineOrders, offlineOrder]);
        
        clearCart();
        
        dispatch({ type: 'SET_LOADING', payload: false });
        return offlineOrder;
      }

      const errorMessage = error.response?.data?.detail || error.message || 'Erro ao enviar pedido';
      dispatch({ type: 'SET_ERROR', payload: errorMessage });
      dispatch({ type: 'SET_LOADING', payload: false });
      
      throw error;
    }
  };

  const saveCartToStorage = async (): Promise<void> => {
    try {
      const cartData = {
        items: state.items,
        currentOrder: state.currentOrder,
        timestamp: new Date().toISOString(),
      };

      await AsyncStorage.setItem('cart_data', JSON.stringify(cartData));
    } catch (error) {
      console.error('Erro ao salvar carrinho:', error);
    }
  };

  const restoreCartFromStorage = async (): Promise<void> => {
    try {
      const cartData = await AsyncStorage.getItem('cart_data');
      
      if (cartData) {
        const parsed = JSON.parse(cartData);
        
        // Verificar se dados não são muito antigos (mais de 24h)
        const timestamp = new Date(parsed.timestamp);
        const now = new Date();
        const diffHours = (now.getTime() - timestamp.getTime()) / (1000 * 60 * 60);
        
        if (diffHours < 24) {
          dispatch({
            type: 'RESTORE_CART',
            payload: {
              items: parsed.items || [],
              currentOrder: parsed.currentOrder || { tipo_pedido: 'mesa' },
            },
          });
        }
      }
    } catch (error) {
      console.error('Erro ao restaurar carrinho:', error);
    }
  };

  const loadOfflineOrders = async () => {
    try {
      const offlineData = await AsyncStorage.getItem('offline_orders');
      
      if (offlineData) {
        const orders = JSON.parse(offlineData);
        
        for (const order of orders) {
          dispatch({ type: 'SAVE_OFFLINE_ORDER', payload: order });
        }
      }
    } catch (error) {
      console.error('Erro ao carregar pedidos offline:', error);
    }
  };

  const saveOfflineOrders = async (orders: Order[]) => {
    try {
      await AsyncStorage.setItem('offline_orders', JSON.stringify(orders));
    } catch (error) {
      console.error('Erro ao salvar pedidos offline:', error);
    }
  };

  const syncOfflineOrders = async (): Promise<void> => {
    if (state.offlineOrders.length === 0) {
      return;
    }

    for (const order of state.offlineOrders) {
      try {
        const response = await apiService.post('/pdv-mobile/pedidos', order);
        
        if (response.success) {
          dispatch({ type: 'REMOVE_OFFLINE_ORDER', payload: order.id! });
        }
      } catch (error) {
        console.error('Erro ao sincronizar pedido offline:', error);
        // Continuar tentando outros pedidos
      }
    }

    // Atualizar storage
    await saveOfflineOrders(state.offlineOrders);
  };

  const getItemQuantity = (produto_id: number): number => {
    const item = state.items.find(item => item.produto_id === produto_id);
    return item ? item.quantidade : 0;
  };

  const clearError = () => {
    dispatch({ type: 'SET_ERROR', payload: null });
  };

  const contextValue: CartContextType = {
    state,
    addItem,
    removeItem,
    updateQuantity,
    updateItemNotes,
    clearCart,
    setOrderInfo,
    submitOrder,
    saveCartToStorage,
    restoreCartFromStorage,
    syncOfflineOrders,
    getItemQuantity,
    clearError,
  };

  return (
    <CartContext.Provider value={contextValue}>
      {children}
    </CartContext.Provider>
  );
};
