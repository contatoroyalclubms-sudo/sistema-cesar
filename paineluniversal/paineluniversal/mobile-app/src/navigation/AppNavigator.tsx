import React from 'react';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import Icon from 'react-native-vector-icons/MaterialIcons';
import { useAuth } from '../contexts/AuthContext';

// Importar telas
import LoginScreen from '../screens/LoginScreen';
import DashboardScreen from '../screens/DashboardScreen';
import NFCScreen from '../screens/NFCScreen';
import ProductsScreen from '../screens/ProductsScreen';
import CartScreen from '../screens/CartScreen';

// Definir tipos de navegação
export type RootStackParamList = {
  Login: undefined;
  Main: undefined;
};

export type TabParamList = {
  Dashboard: undefined;
  NFC: undefined;
  Products: undefined;
  Cart: undefined;
};

const Stack = createNativeStackNavigator<RootStackParamList>();
const Tab = createBottomTabNavigator<TabParamList>();

// Navegação por abas (quando autenticado)
function TabNavigator() {
  return (
    <Tab.Navigator
      screenOptions={({ route }) => ({
        tabBarIcon: ({ focused, color, size }) => {
          let iconName: string;

          switch (route.name) {
            case 'Dashboard':
              iconName = 'dashboard';
              break;
            case 'NFC':
              iconName = 'nfc';
              break;
            case 'Products':
              iconName = 'restaurant-menu';
              break;
            case 'Cart':
              iconName = 'shopping-cart';
              break;
            default:
              iconName = 'circle';
          }

          return <Icon name={iconName} size={size} color={color} />;
        },
        tabBarActiveTintColor: '#10b981',
        tabBarInactiveTintColor: '#6b7280',
        tabBarStyle: {
          backgroundColor: '#1f2937',
          borderTopColor: '#374151',
        },
        headerStyle: {
          backgroundColor: '#1f2937',
        },
        headerTintColor: '#ffffff',
        headerTitleStyle: {
          fontWeight: 'bold',
        },
      })}
    >
      <Tab.Screen 
        name="Dashboard" 
        component={DashboardScreen}
        options={{
          title: 'Dashboard',
          tabBarLabel: 'Início',
        }}
      />
      <Tab.Screen 
        name="NFC" 
        component={NFCScreen}
        options={{
          title: 'Leitura NFC',
          tabBarLabel: 'NFC',
        }}
      />
      <Tab.Screen 
        name="Products" 
        component={ProductsScreen}
        options={{
          title: 'Produtos',
          tabBarLabel: 'Cardápio',
        }}
      />
      <Tab.Screen 
        name="Cart" 
        component={CartScreen}
        options={{
          title: 'Carrinho',
          tabBarLabel: 'Pedido',
        }}
      />
    </Tab.Navigator>
  );
}

// Navegação principal
export default function AppNavigator() {
  const { state } = useAuth();

  return (
    <Stack.Navigator
      screenOptions={{
        headerShown: false,
      }}
    >
      {state.isAuthenticated ? (
        <Stack.Screen name="Main" component={TabNavigator} />
      ) : (
        <Stack.Screen name="Login" component={LoginScreen} />
      )}
    </Stack.Navigator>
  );
}
