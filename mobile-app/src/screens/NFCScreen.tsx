import React, { useState, useEffect, useRef } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  Alert,
  Vibration,
  Animated,
  ActivityIndicator,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useNavigation } from '@react-navigation/native';
import { Ionicons } from '@expo/vector-icons';
import { theme } from '../styles/theme';
import { nfcService, NFCData } from '../services/nfcService';
import { useAuth } from '../contexts/AuthContext';
import { apiService } from '../services/apiService';

const NFCScreen: React.FC = () => {
  const navigation = useNavigation();
  const { state: authState } = useAuth();
  const [isReading, setIsReading] = useState(false);
  const [isValidating, setIsValidating] = useState(false);
  const [lastReadData, setLastReadData] = useState<NFCData | null>(null);
  const [status, setStatus] = useState<'idle' | 'reading' | 'validating' | 'success' | 'error'>('idle');
  const [message, setMessage] = useState('Toque no botão para iniciar a leitura NFC');

  // Animações
  const pulseAnim = useRef(new Animated.Value(1)).current;
  const waveAnim = useRef(new Animated.Value(0)).current;

  useEffect(() => {
    // Inicializar NFC quando componente monta
    initializeNFC();

    return () => {
      // Cleanup quando componente desmonta
      cleanupNFC();
    };
  }, []);

  useEffect(() => {
    // Iniciar animações quando estiver lendo
    if (isReading) {
      startAnimations();
    } else {
      stopAnimations();
    }
  }, [isReading]);

  const initializeNFC = async () => {
    try {
      const initialized = await nfcService.initialize();
      
      if (!initialized) {
        setStatus('error');
        setMessage('NFC não está disponível neste dispositivo');
      } else {
        setMessage('Toque no botão para iniciar a leitura NFC');
      }
    } catch (error) {
      console.error('Erro ao inicializar NFC:', error);
      setStatus('error');
      setMessage('Erro ao inicializar NFC');
    }
  };

  const cleanupNFC = async () => {
    try {
      await nfcService.cleanup();
    } catch (error) {
      console.error('Erro no cleanup NFC:', error);
    }
  };

  const startAnimations = () => {
    // Animação de pulso
    Animated.loop(
      Animated.sequence([
        Animated.timing(pulseAnim, {
          toValue: 1.2,
          duration: 1000,
          useNativeDriver: true,
        }),
        Animated.timing(pulseAnim, {
          toValue: 1,
          duration: 1000,
          useNativeDriver: true,
        }),
      ])
    ).start();

    // Animação de onda
    Animated.loop(
      Animated.timing(waveAnim, {
        toValue: 1,
        duration: 2000,
        useNativeDriver: true,
      })
    ).start();
  };

  const stopAnimations = () => {
    pulseAnim.stopAnimation();
    waveAnim.stopAnimation();
    Animated.timing(pulseAnim, {
      toValue: 1,
      duration: 300,
      useNativeDriver: true,
    }).start();
  };

  const startReading = async () => {
    try {
      setIsReading(true);
      setStatus('reading');
      setMessage('Aproxime a comanda ou pulseira do celular...');
      setLastReadData(null);

      // Adicionar listener para detecção de tags
      const removeListener = nfcService.addListener(handleNFCRead);

      // Iniciar leitura
      await nfcService.startReading();

      // Auto-stop após 30 segundos
      setTimeout(() => {
        if (isReading) {
          stopReading();
          removeListener();
        }
      }, 30000);

    } catch (error: any) {
      console.error('Erro ao iniciar leitura NFC:', error);
      setStatus('error');
      setMessage(error.message || 'Erro ao iniciar leitura NFC');
      setIsReading(false);
    }
  };

  const stopReading = async () => {
    try {
      await nfcService.stopReading();
      setIsReading(false);
      setStatus('idle');
      setMessage('Toque no botão para iniciar a leitura NFC');
    } catch (error) {
      console.error('Erro ao parar leitura NFC:', error);
    }
  };

  const handleNFCRead = async (data: NFCData) => {
    try {
      console.log('NFC lido:', data);
      
      // Vibrar para feedback
      Vibration.vibrate(200);
      
      setLastReadData(data);
      setIsReading(false);
      setStatus('validating');
      setMessage('Validando dados...');
      setIsValidating(true);

      await nfcService.stopReading();

      // Validar dados no servidor
      await validateNFCData(data);

    } catch (error: any) {
      console.error('Erro ao processar NFC:', error);
      setStatus('error');
      setMessage(error.message || 'Erro ao processar dados NFC');
      setIsValidating(false);
    }
  };

  const validateNFCData = async (data: NFCData) => {
    try {
      const validationData = {
        nfc_id: data.id,
        tipo: data.type,
        dados: data.data || {},
        dados_brutos: data.rawData,
        timestamp: data.timestamp,
      };

      const response = await apiService.post('/pdv-mobile/nfc/validar', validationData);

      if (response.success) {
        setStatus('success');
        setMessage('NFC validado com sucesso!');

        // Vibrar para sucesso
        Vibration.vibrate([100, 50, 100]);

        // Navegar para próxima tela baseado no tipo
        setTimeout(() => {
          if (data.type === 'comanda') {
            navigation.navigate('OrderScreen', {
              nfcData: data,
              validationData: response,
            });
          } else if (data.type === 'pulseira') {
            navigation.navigate('CustomerScreen', {
              nfcData: data,
              validationData: response,
            });
          } else {
            // Tipo desconhecido, mostrar opções
            navigation.navigate('NFCTypeSelection', {
              nfcData: data,
              validationData: response,
            });
          }
        }, 1500);

      } else {
        throw new Error(response.message || 'Erro na validação');
      }

    } catch (error: any) {
      console.error('Erro na validação:', error);
      
      setStatus('error');
      
      let errorMessage = 'Erro ao validar NFC';
      if (error.response?.status === 404) {
        errorMessage = 'Comanda ou pulseira não encontrada';
      } else if (error.response?.status === 400) {
        errorMessage = error.response?.data?.detail || 'Dados NFC inválidos';
      } else if (error.message) {
        errorMessage = error.message;
      }
      
      setMessage(errorMessage);
      
      // Vibrar para erro
      Vibration.vibrate([200, 100, 200, 100, 200]);
    } finally {
      setIsValidating(false);
    }
  };

  const retryReading = () => {
    setStatus('idle');
    setMessage('Toque no botão para iniciar a leitura NFC');
    setLastReadData(null);
  };

  const getStatusColor = () => {
    switch (status) {
      case 'reading':
        return theme.colors.warning;
      case 'validating':
        return theme.colors.info;
      case 'success':
        return theme.colors.success;
      case 'error':
        return theme.colors.error;
      default:
        return theme.colors.primary;
    }
  };

  const getStatusIcon = () => {
    switch (status) {
      case 'reading':
        return 'radio-outline';
      case 'validating':
        return 'sync-outline';
      case 'success':
        return 'checkmark-circle-outline';
      case 'error':
        return 'alert-circle-outline';
      default:
        return 'nfc-outline';
    }
  };

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.content}>
        {/* Header */}
        <View style={styles.header}>
          <TouchableOpacity
            style={styles.backButton}
            onPress={() => navigation.goBack()}
          >
            <Ionicons name="arrow-back" size={24} color={theme.colors.text} />
          </TouchableOpacity>
          <Text style={styles.title}>Leitura NFC</Text>
        </View>

        {/* Status Area */}
        <View style={styles.statusContainer}>
          {/* Animação de ondas (apenas quando lendo) */}
          {isReading && (
            <View style={styles.waveContainer}>
              {[1, 2, 3].map((index) => (
                <Animated.View
                  key={index}
                  style={[
                    styles.wave,
                    {
                      opacity: waveAnim.interpolate({
                        inputRange: [0, 1],
                        outputRange: [0.3, 0],
                      }),
                      transform: [
                        {
                          scale: waveAnim.interpolate({
                            inputRange: [0, 1],
                            outputRange: [1, 2 + index * 0.5],
                          }),
                        },
                      ],
                    },
                  ]}
                />
              ))}
            </View>
          )}

          {/* Ícone principal */}
          <Animated.View
            style={[
              styles.iconContainer,
              {
                backgroundColor: getStatusColor(),
                transform: [{ scale: pulseAnim }],
              },
            ]}
          >
            {isValidating ? (
              <ActivityIndicator size="large" color={theme.colors.background} />
            ) : (
              <Ionicons
                name={getStatusIcon()}
                size={60}
                color={theme.colors.background}
              />
            )}
          </Animated.View>

          {/* Mensagem de status */}
          <Text style={[styles.statusMessage, { color: getStatusColor() }]}>
            {message}
          </Text>

          {/* Dados do último NFC lido */}
          {lastReadData && (
            <View style={styles.dataContainer}>
              <Text style={styles.dataTitle}>Dados Lidos:</Text>
              <Text style={styles.dataText}>ID: {lastReadData.id}</Text>
              <Text style={styles.dataText}>Tipo: {lastReadData.type}</Text>
              {lastReadData.data && (
                <Text style={styles.dataText}>
                  Dados: {JSON.stringify(lastReadData.data, null, 2)}
                </Text>
              )}
            </View>
          )}
        </View>

        {/* Botões de ação */}
        <View style={styles.buttonContainer}>
          {!isReading && !isValidating && status !== 'success' && (
            <TouchableOpacity
              style={[styles.actionButton, { backgroundColor: theme.colors.primary }]}
              onPress={startReading}
            >
              <Ionicons name="nfc" size={24} color={theme.colors.background} />
              <Text style={styles.actionButtonText}>
                {status === 'error' ? 'TENTAR NOVAMENTE' : 'INICIAR LEITURA'}
              </Text>
            </TouchableOpacity>
          )}

          {isReading && (
            <TouchableOpacity
              style={[styles.actionButton, { backgroundColor: theme.colors.error }]}
              onPress={stopReading}
            >
              <Ionicons name="stop" size={24} color={theme.colors.background} />
              <Text style={styles.actionButtonText}>PARAR LEITURA</Text>
            </TouchableOpacity>
          )}

          {status === 'success' && (
            <TouchableOpacity
              style={[styles.actionButton, { backgroundColor: theme.colors.primary }]}
              onPress={retryReading}
            >
              <Ionicons name="refresh" size={24} color={theme.colors.background} />
              <Text style={styles.actionButtonText}>LER OUTRO NFC</Text>
            </TouchableOpacity>
          )}
        </View>

        {/* Instruções */}
        <View style={styles.instructionsContainer}>
          <Text style={styles.instructionsTitle}>Instruções:</Text>
          <Text style={styles.instructionText}>
            • Mantenha o celular próximo à comanda ou pulseira
          </Text>
          <Text style={styles.instructionText}>
            • Aguarde a vibração indicando leitura bem-sucedida
          </Text>
          <Text style={styles.instructionText}>
            • Certifique-se de que o NFC está habilitado
          </Text>
        </View>
      </View>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: theme.colors.background,
  },
  content: {
    flex: 1,
    padding: theme.spacing.lg,
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: theme.spacing.xl,
  },
  backButton: {
    padding: theme.spacing.sm,
    marginRight: theme.spacing.md,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: theme.colors.text,
  },
  statusContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    position: 'relative',
  },
  waveContainer: {
    position: 'absolute',
    width: 300,
    height: 300,
    justifyContent: 'center',
    alignItems: 'center',
  },
  wave: {
    position: 'absolute',
    width: 200,
    height: 200,
    borderRadius: 100,
    borderWidth: 2,
    borderColor: theme.colors.primary,
  },
  iconContainer: {
    width: 120,
    height: 120,
    borderRadius: 60,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: theme.spacing.xl,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 4,
    },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 8,
  },
  statusMessage: {
    fontSize: 18,
    fontWeight: '600',
    textAlign: 'center',
    marginBottom: theme.spacing.lg,
  },
  dataContainer: {
    backgroundColor: theme.colors.surface,
    borderRadius: theme.borderRadius.md,
    padding: theme.spacing.md,
    width: '100%',
    maxWidth: 300,
  },
  dataTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: theme.colors.text,
    marginBottom: theme.spacing.sm,
  },
  dataText: {
    fontSize: 14,
    color: theme.colors.textSecondary,
    marginBottom: theme.spacing.xs,
  },
  buttonContainer: {
    alignItems: 'center',
    marginVertical: theme.spacing.xl,
  },
  actionButton: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: theme.spacing.xl,
    paddingVertical: theme.spacing.lg,
    borderRadius: theme.borderRadius.md,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.25,
    shadowRadius: 4,
    elevation: 5,
  },
  actionButtonText: {
    color: theme.colors.background,
    fontSize: 16,
    fontWeight: 'bold',
    marginLeft: theme.spacing.sm,
  },
  instructionsContainer: {
    backgroundColor: theme.colors.surface,
    borderRadius: theme.borderRadius.md,
    padding: theme.spacing.md,
  },
  instructionsTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: theme.colors.text,
    marginBottom: theme.spacing.sm,
  },
  instructionText: {
    fontSize: 14,
    color: theme.colors.textSecondary,
    marginBottom: theme.spacing.xs,
  },
});

export default NFCScreen;
