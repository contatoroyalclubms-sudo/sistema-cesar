import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ScrollView,
  ActivityIndicator,
  RefreshControl,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useNavigation } from '@react-navigation/native';
import { Ionicons } from '@expo/vector-icons';
import { theme } from '../styles/theme';
import { useAuth } from '../contexts/AuthContext';
import { useCart } from '../contexts/CartContext';
import { apiService } from '../services/apiService';

interface DashboardStats {
  pedidos_hoje: number;
  valor_vendido_hoje: number;
  mesas_atendidas: number;
  tempo_sessao: string;
  ultimo_pedido?: {
    id: number;
    mesa: string;
    total: number;
    status: string;
    created_at: string;
  };
}

const DashboardScreen: React.FC = () => {
  const navigation = useNavigation();
  const { state: authState, logout, sendHeartbeat } = useAuth();
  const { state: cartState, syncOfflineOrders } = useCart();
  
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [currentTime, setCurrentTime] = useState(new Date());

  useEffect(() => {
    loadDashboardData();
    
    // Atualizar horário a cada minuto
    const timeInterval = setInterval(() => {
      setCurrentTime(new Date());
    }, 60000);

    // Heartbeat a cada 5 minutos
    const heartbeatInterval = setInterval(() => {
      sendHeartbeat();
    }, 5 * 60 * 1000);

    return () => {
      clearInterval(timeInterval);
      clearInterval(heartbeatInterval);
    };
  }, []);

  const loadDashboardData = async () => {
    try {
      const response = await apiService.get('/pdv-mobile/dashboard');
      
      if (response.success) {
        setStats(response.dados);
      }
    } catch (error) {
      console.error('Erro ao carregar dashboard:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleRefresh = async () => {
    setRefreshing(true);
    
    try {
      await Promise.all([
        loadDashboardData(),
        syncOfflineOrders(),
        sendHeartbeat()
      ]);
    } catch (error) {
      console.error('Erro ao atualizar dashboard:', error);
    } finally {
      setRefreshing(false);
    }
  };

  const handleLogout = async () => {
    try {
      await logout();
    } catch (error) {
      console.error('Erro no logout:', error);
    }
  };

  const formatPrice = (price: number): string => {
    return `R$ ${price.toFixed(2).replace('.', ',')}`;
  };

  const formatTime = (date: Date): string => {
    return date.toLocaleTimeString('pt-BR', {
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const formatDate = (date: Date): string => {
    return date.toLocaleDateString('pt-BR', {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  const quickActions = [
    {
      title: 'Ler NFC',
      subtitle: 'Comandas e Pulseiras',
      icon: 'nfc-outline',
      color: theme.colors.primary,
      onPress: () => navigation.navigate('NFCScreen'),
    },
    {
      title: 'Cardápio',
      subtitle: 'Ver Produtos',
      icon: 'restaurant-outline',
      color: theme.colors.info,
      onPress: () => navigation.navigate('ProductsScreen'),
    },
    {
      title: 'Carrinho',
      subtitle: `${cartState.items.length} itens`,
      icon: 'basket-outline',
      color: theme.colors.warning,
      badge: cartState.items.length > 0 ? cartState.items.length : undefined,
      onPress: () => navigation.navigate('CartScreen'),
    },
    {
      title: 'Pedidos',
      subtitle: 'Histórico',
      icon: 'list-outline',
      color: theme.colors.success,
      onPress: () => navigation.navigate('OrdersScreen'),
    },
  ];

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView
        style={styles.scrollContainer}
        refreshControl={
          <RefreshControl
            refreshing={refreshing}
            onRefresh={handleRefresh}
            colors={[theme.colors.primary]}
          />
        }
      >
        {/* Header */}
        <View style={styles.header}>
          <View style={styles.userInfo}>
            <Text style={styles.greeting}>Olá,</Text>
            <Text style={styles.userName}>{authState.user?.nome}</Text>
            <Text style={styles.eventName}>{authState.evento?.nome}</Text>
          </View>
          
          <TouchableOpacity style={styles.logoutButton} onPress={handleLogout}>
            <Ionicons name="log-out-outline" size={24} color={theme.colors.error} />
          </TouchableOpacity>
        </View>

        {/* Data e Hora */}
        <View style={styles.timeContainer}>
          <Text style={styles.currentTime}>{formatTime(currentTime)}</Text>
          <Text style={styles.currentDate}>{formatDate(currentTime)}</Text>
        </View>

        {/* Estatísticas */}
        {isLoading ? (
          <View style={styles.loadingContainer}>
            <ActivityIndicator size="large" color={theme.colors.primary} />
            <Text style={styles.loadingText}>Carregando estatísticas...</Text>
          </View>
        ) : stats ? (
          <View style={styles.statsContainer}>
            <View style={styles.statsGrid}>
              <View style={[styles.statCard, { backgroundColor: theme.colors.primary + '20' }]}>
                <Ionicons name="receipt-outline" size={24} color={theme.colors.primary} />
                <Text style={styles.statValue}>{stats.pedidos_hoje}</Text>
                <Text style={styles.statLabel}>Pedidos Hoje</Text>
              </View>

              <View style={[styles.statCard, { backgroundColor: theme.colors.success + '20' }]}>
                <Ionicons name="cash-outline" size={24} color={theme.colors.success} />
                <Text style={styles.statValue}>{formatPrice(stats.valor_vendido_hoje)}</Text>
                <Text style={styles.statLabel}>Vendido Hoje</Text>
              </View>

              <View style={[styles.statCard, { backgroundColor: theme.colors.info + '20' }]}>
                <Ionicons name="restaurant-outline" size={24} color={theme.colors.info} />
                <Text style={styles.statValue}>{stats.mesas_atendidas}</Text>
                <Text style={styles.statLabel}>Mesas Atendidas</Text>
              </View>

              <View style={[styles.statCard, { backgroundColor: theme.colors.warning + '20' }]}>
                <Ionicons name="time-outline" size={24} color={theme.colors.warning} />
                <Text style={styles.statValue}>{stats.tempo_sessao}</Text>
                <Text style={styles.statLabel}>Tempo Online</Text>
              </View>
            </View>
          </View>
        ) : (
          <View style={styles.errorContainer}>
            <Text style={styles.errorText}>Erro ao carregar estatísticas</Text>
            <TouchableOpacity onPress={loadDashboardData}>
              <Text style={styles.retryText}>Tentar novamente</Text>
            </TouchableOpacity>
          </View>
        )}

        {/* Ações Rápidas */}
        <View style={styles.quickActionsContainer}>
          <Text style={styles.sectionTitle}>Ações Rápidas</Text>
          
          <View style={styles.actionsGrid}>
            {quickActions.map((action, index) => (
              <TouchableOpacity
                key={index}
                style={[styles.actionCard, { borderLeftColor: action.color }]}
                onPress={action.onPress}
              >
                <View style={styles.actionIcon}>
                  <Ionicons name={action.icon as any} size={28} color={action.color} />
                  {action.badge && (
                    <View style={[styles.badge, { backgroundColor: action.color }]}>
                      <Text style={styles.badgeText}>{action.badge}</Text>
                    </View>
                  )}
                </View>
                
                <View style={styles.actionInfo}>
                  <Text style={styles.actionTitle}>{action.title}</Text>
                  <Text style={styles.actionSubtitle}>{action.subtitle}</Text>
                </View>

                <Ionicons name="chevron-forward" size={20} color={theme.colors.textSecondary} />
              </TouchableOpacity>
            ))}
          </View>
        </View>

        {/* Último Pedido */}
        {stats?.ultimo_pedido && (
          <View style={styles.lastOrderContainer}>
            <Text style={styles.sectionTitle}>Último Pedido</Text>
            
            <View style={styles.lastOrderCard}>
              <View style={styles.lastOrderHeader}>
                <Text style={styles.lastOrderId}>Pedido #{stats.ultimo_pedido.id}</Text>
                <Text style={styles.lastOrderStatus}>{stats.ultimo_pedido.status}</Text>
              </View>
              
              <View style={styles.lastOrderDetails}>
                <View style={styles.lastOrderInfo}>
                  <Text style={styles.lastOrderMesa}>Mesa {stats.ultimo_pedido.mesa}</Text>
                  <Text style={styles.lastOrderTime}>
                    {new Date(stats.ultimo_pedido.created_at).toLocaleTimeString('pt-BR')}
                  </Text>
                </View>
                
                <Text style={styles.lastOrderTotal}>
                  {formatPrice(stats.ultimo_pedido.total)}
                </Text>
              </View>
            </View>
          </View>
        )}

        {/* Informações Offline */}
        {cartState.offlineOrders.length > 0 && (
          <View style={styles.offlineContainer}>
            <View style={styles.offlineHeader}>
              <Ionicons name="cloud-offline-outline" size={20} color={theme.colors.warning} />
              <Text style={styles.offlineTitle}>
                {cartState.offlineOrders.length} pedidos offline
              </Text>
            </View>
            <Text style={styles.offlineSubtext}>
              Serão enviados quando a conexão for reestabelecida
            </Text>
          </View>
        )}
      </ScrollView>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: theme.colors.background,
  },
  scrollContainer: {
    flex: 1,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: theme.spacing.lg,
  },
  userInfo: {
    flex: 1,
  },
  greeting: {
    fontSize: 16,
    color: theme.colors.textSecondary,
  },
  userName: {
    fontSize: 24,
    fontWeight: 'bold',
    color: theme.colors.text,
  },
  eventName: {
    fontSize: 14,
    color: theme.colors.primary,
    fontWeight: '500',
  },
  logoutButton: {
    padding: theme.spacing.sm,
  },
  timeContainer: {
    alignItems: 'center',
    paddingHorizontal: theme.spacing.lg,
    paddingBottom: theme.spacing.lg,
  },
  currentTime: {
    fontSize: 32,
    fontWeight: 'bold',
    color: theme.colors.text,
  },
  currentDate: {
    fontSize: 14,
    color: theme.colors.textSecondary,
    textTransform: 'capitalize',
  },
  loadingContainer: {
    alignItems: 'center',
    paddingVertical: theme.spacing.xl,
  },
  loadingText: {
    marginTop: theme.spacing.md,
    color: theme.colors.textSecondary,
  },
  statsContainer: {
    paddingHorizontal: theme.spacing.lg,
    paddingBottom: theme.spacing.lg,
  },
  statsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
  },
  statCard: {
    width: '48%',
    backgroundColor: theme.colors.surface,
    borderRadius: theme.borderRadius.md,
    padding: theme.spacing.md,
    alignItems: 'center',
    marginBottom: theme.spacing.md,
  },
  statValue: {
    fontSize: 20,
    fontWeight: 'bold',
    color: theme.colors.text,
    marginTop: theme.spacing.sm,
  },
  statLabel: {
    fontSize: 12,
    color: theme.colors.textSecondary,
    textAlign: 'center',
    marginTop: theme.spacing.xs,
  },
  errorContainer: {
    alignItems: 'center',
    paddingVertical: theme.spacing.xl,
  },
  errorText: {
    color: theme.colors.error,
    marginBottom: theme.spacing.sm,
  },
  retryText: {
    color: theme.colors.primary,
    fontWeight: '600',
  },
  quickActionsContainer: {
    paddingHorizontal: theme.spacing.lg,
    paddingBottom: theme.spacing.lg,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: theme.colors.text,
    marginBottom: theme.spacing.md,
  },
  actionsGrid: {
    gap: theme.spacing.sm,
  },
  actionCard: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: theme.colors.surface,
    borderRadius: theme.borderRadius.md,
    padding: theme.spacing.md,
    borderLeftWidth: 4,
  },
  actionIcon: {
    position: 'relative',
    marginRight: theme.spacing.md,
  },
  badge: {
    position: 'absolute',
    top: -8,
    right: -8,
    borderRadius: theme.borderRadius.full,
    minWidth: 20,
    height: 20,
    justifyContent: 'center',
    alignItems: 'center',
  },
  badgeText: {
    color: theme.colors.background,
    fontSize: 12,
    fontWeight: 'bold',
  },
  actionInfo: {
    flex: 1,
  },
  actionTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: theme.colors.text,
  },
  actionSubtitle: {
    fontSize: 14,
    color: theme.colors.textSecondary,
  },
  lastOrderContainer: {
    paddingHorizontal: theme.spacing.lg,
    paddingBottom: theme.spacing.lg,
  },
  lastOrderCard: {
    backgroundColor: theme.colors.surface,
    borderRadius: theme.borderRadius.md,
    padding: theme.spacing.md,
  },
  lastOrderHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: theme.spacing.sm,
  },
  lastOrderId: {
    fontSize: 16,
    fontWeight: 'bold',
    color: theme.colors.text,
  },
  lastOrderStatus: {
    fontSize: 12,
    color: theme.colors.success,
    fontWeight: '600',
    textTransform: 'uppercase',
  },
  lastOrderDetails: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  lastOrderInfo: {
    flex: 1,
  },
  lastOrderMesa: {
    fontSize: 14,
    color: theme.colors.text,
  },
  lastOrderTime: {
    fontSize: 12,
    color: theme.colors.textSecondary,
  },
  lastOrderTotal: {
    fontSize: 18,
    fontWeight: 'bold',
    color: theme.colors.success,
  },
  offlineContainer: {
    backgroundColor: theme.colors.warning + '20',
    margin: theme.spacing.lg,
    padding: theme.spacing.md,
    borderRadius: theme.borderRadius.md,
    borderLeftWidth: 4,
    borderLeftColor: theme.colors.warning,
  },
  offlineHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: theme.spacing.xs,
  },
  offlineTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: theme.colors.warning,
    marginLeft: theme.spacing.sm,
  },
  offlineSubtext: {
    fontSize: 12,
    color: theme.colors.textSecondary,
  },
});

export default DashboardScreen;
