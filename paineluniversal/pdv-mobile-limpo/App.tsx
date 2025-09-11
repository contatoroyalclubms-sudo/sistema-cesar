import React from 'react';
import { StatusBar } from 'expo-status-bar';
import AppNavigator from './src/navigation/AppNavigator';
import { CarrinhoProvider } from './src/context/CarrinhoContext';
import { MesaProvider } from './src/context/MesaContext';

export default function App() {
  return (
    <MesaProvider>
      <CarrinhoProvider>
        <StatusBar style="auto" />
        <AppNavigator />
      </CarrinhoProvider>
    </MesaProvider>
  );
}
