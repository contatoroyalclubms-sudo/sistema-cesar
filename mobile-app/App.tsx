import React from 'react';
import { Provider as PaperProvider } from 'react-native-paper';
import { NavigationContainer } from '@react-navigation/native';
import { StatusBar } from 'expo-status-bar';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import AppNavigator from './src/navigation/AppNavigator';
import { theme } from './src/theme/theme';
import { AuthProvider } from './src/contexts/AuthContext';
import { NFCProvider } from './src/contexts/NFCContext';
import { CartProvider } from './src/contexts/CartContext';
import { OfflineProvider } from './src/contexts/OfflineContext';
import ErrorBoundary from './src/components/ErrorBoundary';

export default function App() {
  return (
    <ErrorBoundary>
      <SafeAreaProvider>
        <PaperProvider theme={theme}>
          <AuthProvider>
            <NFCProvider>
              <CartProvider>
                <OfflineProvider>
                  <NavigationContainer theme={theme}>
                    <AppNavigator />
                    <StatusBar style="light" backgroundColor="#1f2937" />
                  </NavigationContainer>
                </OfflineProvider>
              </CartProvider>
            </NFCProvider>
          </AuthProvider>
        </PaperProvider>
      </SafeAreaProvider>
    </ErrorBoundary>
  );
}
