import React from 'react';
import { View, Text, StyleSheet, ScrollView } from 'react-native';
import { StatusBar } from 'expo-status-bar';

export default function App() {
  return (
    <View style={styles.container}>
      <StatusBar style="auto" />
      <ScrollView contentContainerStyle={styles.content}>
        <Text style={styles.title}>🎉 EXPO GO FUNCIONANDO!</Text>
        <Text style={styles.subtitle}>PDV Mobile - Versão Debug</Text>
        
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>📱 Teste Básico</Text>
          <Text style={styles.text}>✅ React Native funcionando</Text>
          <Text style={styles.text}>✅ Expo SDK carregado</Text>
          <Text style={styles.text}>✅ StatusBar configurada</Text>
          <Text style={styles.text}>✅ ScrollView responsiva</Text>
        </View>

        <View style={styles.section}>
          <Text style={styles.sectionTitle}>🚀 Próximos Passos</Text>
          <Text style={styles.text}>1. Confirmar que este teste funciona</Text>
          <Text style={styles.text}>2. Adicionar navegação gradualmente</Text>
          <Text style={styles.text}>3. Incluir contextos um por vez</Text>
          <Text style={styles.text}>4. Testar funcionalidades específicas</Text>
        </View>

        <View style={styles.section}>
          <Text style={styles.sectionTitle}>📋 Informações</Text>
          <Text style={styles.text}>Projeto: Painel Universal PDV</Text>
          <Text style={styles.text}>Plataforma: React Native + Expo</Text>
          <Text style={styles.text}>Status: Diagnóstico Inicial</Text>
        </View>
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f8fafc',
  },
  content: {
    flexGrow: 1,
    padding: 20,
    paddingTop: 60,
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#1f2937',
    textAlign: 'center',
    marginBottom: 10,
  },
  subtitle: {
    fontSize: 18,
    color: '#6b7280',
    textAlign: 'center',
    marginBottom: 30,
  },
  section: {
    backgroundColor: '#ffffff',
    padding: 20,
    borderRadius: 12,
    marginBottom: 20,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#374151',
    marginBottom: 15,
  },
  text: {
    fontSize: 16,
    color: '#4b5563',
    lineHeight: 24,
    marginBottom: 8,
  },
});
