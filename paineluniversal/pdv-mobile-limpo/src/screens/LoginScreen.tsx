import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';

export default function LoginScreen({ navigation }) {
  const handleLogin = () => {
    // Simular login bem-sucedido
    navigation.replace('MainTabs');
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>🔐 PDV LOGIN</Text>
      <Text style={styles.subtitle}>Sistema Point of Sale</Text>
      
      <View style={styles.form}>
        <View style={styles.inputContainer}>
          <Text style={styles.label}>👤 CPF do Garçom</Text>
          <View style={styles.input}>
            <Text style={styles.placeholder}>000.000.000-00</Text>
          </View>
        </View>

        <View style={styles.inputContainer}>
          <Text style={styles.label}>🔑 Senha</Text>
          <View style={styles.input}>
            <Text style={styles.placeholder}>••••••••</Text>
          </View>
        </View>

        <TouchableOpacity style={styles.loginButton} onPress={handleLogin}>
          <Text style={styles.loginButtonText}>ENTRAR NO SISTEMA</Text>
        </TouchableOpacity>
      </View>

      <View style={styles.footer}>
        <Text style={styles.footerText}>PainelUniversal PDV v1.0</Text>
        <Text style={styles.footerText}>Modo: Desenvolvimento</Text>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#1f2937',
    justifyContent: 'center',
    padding: 20,
  },
  title: {
    fontSize: 32,
    fontWeight: 'bold',
    color: '#ffffff',
    textAlign: 'center',
    marginBottom: 10,
  },
  subtitle: {
    fontSize: 18,
    color: '#9ca3af',
    textAlign: 'center',
    marginBottom: 40,
  },
  form: {
    backgroundColor: '#374151',
    padding: 30,
    borderRadius: 15,
    marginBottom: 30,
  },
  inputContainer: {
    marginBottom: 20,
  },
  label: {
    fontSize: 16,
    color: '#e5e7eb',
    marginBottom: 8,
    fontWeight: '600',
  },
  input: {
    backgroundColor: '#4b5563',
    padding: 15,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#6b7280',
  },
  placeholder: {
    color: '#9ca3af',
    fontSize: 16,
  },
  loginButton: {
    backgroundColor: '#3b82f6',
    padding: 18,
    borderRadius: 10,
    marginTop: 10,
  },
  loginButtonText: {
    color: '#ffffff',
    fontSize: 18,
    fontWeight: 'bold',
    textAlign: 'center',
  },
  footer: {
    alignItems: 'center',
  },
  footerText: {
    color: '#6b7280',
    fontSize: 14,
    marginBottom: 5,
  },
});
