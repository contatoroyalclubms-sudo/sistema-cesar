import React from 'react';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { Text, View } from 'react-native';
import DashboardScreen from '../screens/DashboardScreen';
import ProdutosScreen from '../screens/ProdutosScreen';
import CarrinhoScreen from '../screens/CarrinhoScreen';
import { useCarrinho } from '../context/CarrinhoContext';

const Tab = createBottomTabNavigator();

export default function MainTabNavigator() {
  const { getTotalItens } = useCarrinho();
  const totalItens = getTotalItens();

  return (
    <Tab.Navigator
      screenOptions={{
        headerShown: false,
        tabBarStyle: {
          backgroundColor: '#ffffff',
          borderTopWidth: 1,
          borderTopColor: '#e5e7eb',
          paddingTop: 5,
          paddingBottom: 5,
          height: 60,
        },
        tabBarActiveTintColor: '#3b82f6',
        tabBarInactiveTintColor: '#6b7280',
        tabBarLabelStyle: {
          fontSize: 12,
          fontWeight: '600',
        },
      }}
    >
      <Tab.Screen 
        name="Dashboard" 
        component={DashboardScreen}
        options={{
          tabBarLabel: 'Início',
          tabBarIcon: ({ color, focused }) => (
            <TabIcon icon="🏠" color={color} focused={focused} />
          ),
        }}
      />
      
      <Tab.Screen 
        name="Produtos" 
        component={ProdutosScreen}
        options={{
          tabBarLabel: 'Produtos',
          tabBarIcon: ({ color, focused }) => (
            <TabIcon icon="📦" color={color} focused={focused} />
          ),
        }}
      />
      
      <Tab.Screen 
        name="Carrinho" 
        component={CarrinhoScreen}
        options={{
          tabBarLabel: 'Carrinho',
          tabBarIcon: ({ color, focused }) => (
            <View style={{ position: 'relative' }}>
              <TabIcon icon="🛒" color={color} focused={focused} />
              {totalItens > 0 && (
                <View style={{
                  position: 'absolute',
                  right: -8,
                  top: -5,
                  backgroundColor: '#ef4444',
                  borderRadius: 10,
                  minWidth: 20,
                  height: 20,
                  justifyContent: 'center',
                  alignItems: 'center',
                  paddingHorizontal: 4,
                }}>
                  <Text style={{
                    color: '#ffffff',
                    fontSize: 12,
                    fontWeight: 'bold',
                  }}>
                    {totalItens > 99 ? '99+' : totalItens}
                  </Text>
                </View>
              )}
            </View>
          ),
        }}
      />
    </Tab.Navigator>
  );
}

// Componente simples para ícones das tabs
function TabIcon({ icon, color, focused }: { icon: string; color: string; focused: boolean }) {
  return (
    <Text style={{ 
      fontSize: focused ? 24 : 20, 
      color 
    }}>
      {icon}
    </Text>
  );
}
