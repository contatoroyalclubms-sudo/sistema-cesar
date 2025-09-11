import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  TextInput,
  Alert,
  KeyboardAvoidingView,
  Platform,
  ScrollView,
  Image,
  ActivityIndicator,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useAuth } from '../contexts/AuthContext';
import { theme } from '../styles/theme';
import * as Device from 'expo-device';
import * as Application from 'expo-application';

const LoginScreen: React.FC = () => {
  const { login, state } = useAuth();
  const [cpf, setCpf] = useState('');
  const [senha, setSenha] = useState('');
  const [eventoId, setEventoId] = useState('1');
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    // Limpar erro quando componente monta
    if (state.error) {
      // clearError será implementado quando o contexto for atualizado
    }
  }, []);

  const formatCPF = (value: string): string => {
    // Remove todos os caracteres não numéricos
    const numbers = value.replace(/\D/g, '');
    
    // Aplica a máscara do CPF
    if (numbers.length <= 3) {
      return numbers;
    } else if (numbers.length <= 6) {
      return `${numbers.slice(0, 3)}.${numbers.slice(3)}`;
    } else if (numbers.length <= 9) {
      return `${numbers.slice(0, 3)}.${numbers.slice(3, 6)}.${numbers.slice(6)}`;
    } else {
      return `${numbers.slice(0, 3)}.${numbers.slice(3, 6)}.${numbers.slice(6, 9)}-${numbers.slice(9, 11)}`;
    }
  };

  const getDeviceInfo = async () => {
    try {
      return {
        deviceId: await Application.getAndroidId() || Device.osInternalBuildId || 'unknown',
        deviceName: Device.deviceName || 'Dispositivo Desconhecido',
        os: Platform.OS,
        osVersion: Device.osVersion || 'Unknown',
        appVersion: Application.nativeApplicationVersion || '1.0.0',
        buildVersion: Application.nativeBuildVersion || '1',
        modelName: Device.modelName || 'Unknown',
        brand: Device.brand || 'Unknown',
        timestamp: new Date().toISOString(),
      };
    } catch (error) {
      console.error('Erro ao obter informações do device:', error);
      return {
        deviceId: 'unknown',
        deviceName: 'Dispositivo Desconhecido',
        os: Platform.OS,
        osVersion: 'Unknown',
        appVersion: '1.0.0',
        buildVersion: '1',
        modelName: 'Unknown',
        brand: 'Unknown',
        timestamp: new Date().toISOString(),
      };
    }
  };

  const handleLogin = async () => {
    // Validações básicas
    if (!cpf.trim()) {
      Alert.alert('Erro', 'Por favor, digite seu CPF');
      return;
    }

    if (!senha.trim()) {
      Alert.alert('Erro', 'Por favor, digite sua senha');
      return;
    }

    // Remover formatação do CPF
    const cpfNumeros = cpf.replace(/\D/g, '');
    
    if (cpfNumeros.length !== 11) {
      Alert.alert('Erro', 'CPF deve ter 11 dígitos');
      return;
    }

    if (!eventoId.trim()) {
      Alert.alert('Erro', 'Por favor, selecione um evento');
      return;
    }

    setIsLoading(true);

    try {
      const deviceInfo = await getDeviceInfo();
      
      await login(cpfNumeros, senha, parseInt(eventoId), deviceInfo);
      
      // Se chegou até aqui, login foi bem-sucedido
      Alert.alert('Sucesso', 'Login realizado com sucesso!');

    } catch (error: any) {
      console.error('Erro no login:', error);
      
      let errorMessage = 'Erro no login. Tente novamente.';
      
      if (error.message) {
        errorMessage = error.message;
      } else if (typeof error === 'string') {
        errorMessage = error;
      }

      Alert.alert('Erro no Login', errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  const isFormValid = () => {
    const cpfNumeros = cpf.replace(/\D/g, '');
    return cpfNumeros.length === 11 && senha.length >= 3 && eventoId.trim();
  };

  return (
    <SafeAreaView style={styles.container}>
      <KeyboardAvoidingView 
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
        style={styles.keyboardContainer}
      >
        <ScrollView 
          contentContainerStyle={styles.scrollContainer}
          keyboardShouldPersistTaps="handled"
        >
          <View style={styles.content}>
            {/* Logo/Header */}
            <View style={styles.header}>
              <View style={styles.logoContainer}>
                <Text style={styles.logoText}>PDV</Text>
                <Text style={styles.logoSubtext}>MOBILE</Text>
              </View>
              <Text style={styles.subtitle}>Sistema para Garçons</Text>
            </View>

            {/* Formulário */}
            <View style={styles.form}>
              <View style={styles.inputContainer}>
                <Text style={styles.label}>CPF</Text>
                <TextInput
                  style={styles.input}
                  value={cpf}
                  onChangeText={(text) => setCpf(formatCPF(text))}
                  placeholder="000.000.000-00"
                  placeholderTextColor={theme.colors.textSecondary}
                  keyboardType="numeric"
                  maxLength={14}
                  autoCapitalize="none"
                  autoCorrect={false}
                />
              </View>

              <View style={styles.inputContainer}>
                <Text style={styles.label}>Senha</Text>
                <TextInput
                  style={styles.input}
                  value={senha}
                  onChangeText={setSenha}
                  placeholder="Digite sua senha"
                  placeholderTextColor={theme.colors.textSecondary}
                  secureTextEntry
                  autoCapitalize="none"
                  autoCorrect={false}
                />
              </View>

              <View style={styles.inputContainer}>
                <Text style={styles.label}>Evento ID</Text>
                <TextInput
                  style={styles.input}
                  value={eventoId}
                  onChangeText={setEventoId}
                  placeholder="ID do evento"
                  placeholderTextColor={theme.colors.textSecondary}
                  keyboardType="numeric"
                  autoCapitalize="none"
                  autoCorrect={false}
                />
              </View>

              {/* Mensagem de erro */}
              {state.error && (
                <View style={styles.errorContainer}>
                  <Text style={styles.errorText}>{state.error}</Text>
                </View>
              )}

              {/* Botão de login */}
              <TouchableOpacity
                style={[
                  styles.loginButton,
                  (!isFormValid() || isLoading || state.isLoading) && styles.loginButtonDisabled
                ]}
                onPress={handleLogin}
                disabled={!isFormValid() || isLoading || state.isLoading}
              >
                {(isLoading || state.isLoading) ? (
                  <ActivityIndicator color={theme.colors.background} size="small" />
                ) : (
                  <Text style={styles.loginButtonText}>ENTRAR</Text>
                )}
              </TouchableOpacity>
            </View>

            {/* Footer */}
            <View style={styles.footer}>
              <Text style={styles.footerText}>
                Sistema PDV Mobile v1.0
              </Text>
              <Text style={styles.footerSubtext}>
                Para garçons e atendentes
              </Text>
            </View>
          </View>
        </ScrollView>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: theme.colors.background,
  },
  keyboardContainer: {
    flex: 1,
  },
  scrollContainer: {
    flexGrow: 1,
    justifyContent: 'center',
    padding: theme.spacing.lg,
  },
  content: {
    flex: 1,
    justifyContent: 'center',
    maxWidth: 400,
    alignSelf: 'center',
    width: '100%',
  },
  header: {
    alignItems: 'center',
    marginBottom: theme.spacing.xl * 2,
  },
  logoContainer: {
    backgroundColor: theme.colors.primary,
    borderRadius: theme.borderRadius.lg,
    paddingHorizontal: theme.spacing.xl,
    paddingVertical: theme.spacing.lg,
    marginBottom: theme.spacing.md,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 4,
    },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 8,
  },
  logoText: {
    fontSize: 36,
    fontWeight: 'bold',
    color: theme.colors.background,
    textAlign: 'center',
    letterSpacing: 2,
  },
  logoSubtext: {
    fontSize: 14,
    color: theme.colors.background,
    textAlign: 'center',
    opacity: 0.9,
    letterSpacing: 1,
  },
  subtitle: {
    fontSize: 18,
    color: theme.colors.textSecondary,
    textAlign: 'center',
    fontWeight: '300',
  },
  form: {
    width: '100%',
  },
  inputContainer: {
    marginBottom: theme.spacing.lg,
  },
  label: {
    fontSize: 16,
    fontWeight: '600',
    color: theme.colors.text,
    marginBottom: theme.spacing.sm,
  },
  input: {
    backgroundColor: theme.colors.surface,
    borderRadius: theme.borderRadius.md,
    paddingHorizontal: theme.spacing.md,
    paddingVertical: theme.spacing.lg,
    fontSize: 16,
    color: theme.colors.text,
    borderWidth: 1,
    borderColor: theme.colors.border,
  },
  errorContainer: {
    backgroundColor: theme.colors.error + '20',
    borderRadius: theme.borderRadius.sm,
    padding: theme.spacing.md,
    marginBottom: theme.spacing.lg,
    borderLeftWidth: 4,
    borderLeftColor: theme.colors.error,
  },
  errorText: {
    color: theme.colors.error,
    fontSize: 14,
    fontWeight: '500',
  },
  loginButton: {
    backgroundColor: theme.colors.primary,
    borderRadius: theme.borderRadius.md,
    paddingVertical: theme.spacing.lg,
    alignItems: 'center',
    justifyContent: 'center',
    marginTop: theme.spacing.md,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.25,
    shadowRadius: 4,
    elevation: 5,
  },
  loginButtonDisabled: {
    backgroundColor: theme.colors.textSecondary,
    shadowOpacity: 0,
    elevation: 0,
  },
  loginButtonText: {
    color: theme.colors.background,
    fontSize: 18,
    fontWeight: 'bold',
    letterSpacing: 1,
  },
  footer: {
    alignItems: 'center',
    marginTop: theme.spacing.xl * 2,
  },
  footerText: {
    fontSize: 14,
    color: theme.colors.textSecondary,
    textAlign: 'center',
  },
  footerSubtext: {
    fontSize: 12,
    color: theme.colors.textSecondary,
    textAlign: 'center',
    marginTop: theme.spacing.xs,
    opacity: 0.7,
  },
});

export default LoginScreen;
