import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  Modal,
  TouchableOpacity,
  ActivityIndicator,
  Alert,
} from 'react-native';
import { useMesa } from '../context/MesaContext';
import { useCarrinho } from '../context/CarrinhoContext';
import NFCService from '../services/NFCService';

interface NFCModalProps {
  visible: boolean;
  onClose: () => void;
  onSuccess?: (comanda: any) => void;
}

export default function NFCModal({ visible, onClose, onSuccess }: NFCModalProps) {
  const [isReading, setIsReading] = useState(false);
  const [status, setStatus] = useState<'idle' | 'reading' | 'success' | 'error'>('idle');
  const [message, setMessage] = useState('');
  
  const { processarLeituraNFC, comandaAtual, mesaAtual } = useMesa();
  const { getTotalItens } = useCarrinho();

  useEffect(() => {
    if (visible) {
      setStatus('idle');
      setMessage('');
      setIsReading(false);
    }
  }, [visible]);

  const handleStartReading = async () => {
    try {
      setIsReading(true);
      setStatus('reading');
      setMessage('Aproxime o celular da tag NFC...');

      // Verificar status do NFC primeiro
      const nfcStatus = await NFCService.checkNFCStatus();
      
      if (!nfcStatus.isSupported) {
        throw new Error('NFC não é suportado neste dispositivo');
      }

      if (!nfcStatus.isEnabled) {
        throw new Error('NFC está desabilitado. Ative nas configurações do dispositivo.');
      }

      // Iniciar leitura
      const result = await NFCService.startReading();
      
      if (result.success && result.data) {
        // Processar dados no contexto
        const sucesso = await processarLeituraNFC(result.data);
        
        if (sucesso) {
          setStatus('success');
          setMessage('Comanda lida com sucesso!');
          
          // Callback opcional
          if (onSuccess) {
            onSuccess(comandaAtual);
          }
          
          // Fechar modal após delay
          setTimeout(() => {
            onClose();
          }, 2000);
        } else {
          throw new Error('Dados da comanda inválidos');
        }
      } else {
        throw new Error(result.error || 'Falha na leitura NFC');
      }

    } catch (error: any) {
      console.error('Erro na leitura NFC:', error);
      setStatus('error');
      setMessage(error.message || 'Erro desconhecido');
    } finally {
      setIsReading(false);
    }
  };

  const handleTestRead = async () => {
    try {
      setIsReading(true);
      setStatus('reading');
      setMessage('Simulando leitura NFC...');

      // Usar método de teste rápido
      const result = await NFCService.quickTest();
      
      if (result.success && result.data) {
        const sucesso = await processarLeituraNFC(result.data);
        
        if (sucesso) {
          setStatus('success');
          setMessage('Comanda de teste criada com sucesso!');
          
          if (onSuccess) {
            onSuccess(comandaAtual);
          }
          
          setTimeout(() => {
            onClose();
          }, 2000);
        } else {
          throw new Error('Falha ao processar dados de teste');
        }
      } else {
        throw new Error('Falha na simulação');
      }

    } catch (error: any) {
      console.error('Erro no teste:', error);
      setStatus('error');
      setMessage(error.message || 'Erro no teste');
    } finally {
      setIsReading(false);
    }
  };

  const handleCancel = async () => {
    if (isReading) {
      await NFCService.stopReading();
      setIsReading(false);
    }
    onClose();
  };

  const showInstructions = () => {
    NFCService.showInstructions();
  };

  const getStatusIcon = () => {
    switch (status) {
      case 'reading':
        return '📱';
      case 'success':
        return '✅';
      case 'error':
        return '❌';
      default:
        return '🏷️';
    }
  };

  const getStatusColor = () => {
    switch (status) {
      case 'reading':
        return '#3b82f6';
      case 'success':
        return '#059669';
      case 'error':
        return '#ef4444';
      default:
        return '#6b7280';
    }
  };

  return (
    <Modal
      visible={visible}
      transparent
      animationType="slide"
      onRequestClose={handleCancel}
    >
      <View style={styles.overlay}>
        <View style={styles.modal}>
          <View style={styles.header}>
            <Text style={styles.title}>📱 Leitura NFC</Text>
            <TouchableOpacity style={styles.closeButton} onPress={handleCancel}>
              <Text style={styles.closeButtonText}>✕</Text>
            </TouchableOpacity>
          </View>

          <View style={styles.content}>
            <View style={[styles.statusContainer, { borderColor: getStatusColor() }]}>
              <Text style={styles.statusIcon}>{getStatusIcon()}</Text>
              <Text style={[styles.statusMessage, { color: getStatusColor() }]}>
                {message || 'Pronto para ler comanda NFC'}
              </Text>
            </View>

            {mesaAtual && (
              <View style={styles.currentInfo}>
                <Text style={styles.currentTitle}>Mesa Atual:</Text>
                <Text style={styles.currentValue}>{mesaAtual.numero}</Text>
                {comandaAtual && (
                  <>
                    <Text style={styles.currentTitle}>Comanda:</Text>
                    <Text style={styles.currentValue}>{comandaAtual.numeroComanda}</Text>
                  </>
                )}
              </View>
            )}

            {getTotalItens() > 0 && (
              <View style={styles.warningContainer}>
                <Text style={styles.warningIcon}>⚠️</Text>
                <Text style={styles.warningText}>
                  Você tem {getTotalItens()} itens no carrinho. Eles serão associados à nova comanda.
                </Text>
              </View>
            )}

            {isReading && (
              <View style={styles.loadingContainer}>
                <ActivityIndicator size="large" color="#3b82f6" />
                <Text style={styles.loadingText}>Aguardando tag NFC...</Text>
              </View>
            )}
          </View>

          <View style={styles.actions}>
            <TouchableOpacity 
              style={styles.instructionsButton}
              onPress={showInstructions}
            >
              <Text style={styles.instructionsButtonText}>ℹ️ Como usar</Text>
            </TouchableOpacity>

            <TouchableOpacity 
              style={[styles.actionButton, styles.testButton]}
              onPress={handleTestRead}
              disabled={isReading}
            >
              <Text style={styles.testButtonText}>🧪 Teste Simulado</Text>
            </TouchableOpacity>

            <TouchableOpacity 
              style={[styles.actionButton, styles.readButton]}
              onPress={handleStartReading}
              disabled={isReading}
            >
              <Text style={styles.readButtonText}>
                {isReading ? 'Lendo...' : '📱 Ler NFC'}
              </Text>
            </TouchableOpacity>

            <TouchableOpacity 
              style={[styles.actionButton, styles.cancelButton]}
              onPress={handleCancel}
            >
              <Text style={styles.cancelButtonText}>Cancelar</Text>
            </TouchableOpacity>
          </View>
        </View>
      </View>
    </Modal>
  );
}

const styles = StyleSheet.create({
  overlay: {
    flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  },
  modal: {
    backgroundColor: '#ffffff',
    borderRadius: 20,
    padding: 0,
    width: '100%',
    maxWidth: 400,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 8,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    backgroundColor: '#3b82f6',
    padding: 20,
    borderTopLeftRadius: 20,
    borderTopRightRadius: 20,
  },
  title: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#ffffff',
  },
  closeButton: {
    backgroundColor: 'rgba(255, 255, 255, 0.2)',
    width: 30,
    height: 30,
    borderRadius: 15,
    justifyContent: 'center',
    alignItems: 'center',
  },
  closeButtonText: {
    color: '#ffffff',
    fontSize: 16,
    fontWeight: 'bold',
  },
  content: {
    padding: 20,
  },
  statusContainer: {
    borderWidth: 2,
    borderRadius: 12,
    padding: 20,
    alignItems: 'center',
    marginBottom: 20,
  },
  statusIcon: {
    fontSize: 48,
    marginBottom: 10,
  },
  statusMessage: {
    fontSize: 16,
    textAlign: 'center',
    fontWeight: '600',
  },
  currentInfo: {
    backgroundColor: '#f8fafc',
    padding: 15,
    borderRadius: 10,
    marginBottom: 15,
  },
  currentTitle: {
    fontSize: 14,
    color: '#6b7280',
    fontWeight: '600',
  },
  currentValue: {
    fontSize: 16,
    color: '#374151',
    fontWeight: 'bold',
    marginBottom: 5,
  },
  warningContainer: {
    backgroundColor: '#fef3c7',
    padding: 12,
    borderRadius: 8,
    flexDirection: 'row',
    alignItems: 'flex-start',
    marginBottom: 15,
    borderLeftWidth: 4,
    borderLeftColor: '#f59e0b',
  },
  warningIcon: {
    fontSize: 16,
    marginRight: 8,
  },
  warningText: {
    color: '#92400e',
    fontSize: 14,
    flex: 1,
  },
  loadingContainer: {
    alignItems: 'center',
    padding: 20,
  },
  loadingText: {
    marginTop: 10,
    color: '#6b7280',
    fontSize: 14,
  },
  actions: {
    padding: 20,
    gap: 12,
  },
  instructionsButton: {
    backgroundColor: '#f3f4f6',
    padding: 12,
    borderRadius: 8,
    alignItems: 'center',
  },
  instructionsButtonText: {
    color: '#374151',
    fontSize: 14,
    fontWeight: '600',
  },
  actionButton: {
    padding: 15,
    borderRadius: 10,
    alignItems: 'center',
  },
  testButton: {
    backgroundColor: '#8b5cf6',
  },
  testButtonText: {
    color: '#ffffff',
    fontSize: 16,
    fontWeight: 'bold',
  },
  readButton: {
    backgroundColor: '#3b82f6',
  },
  readButtonText: {
    color: '#ffffff',
    fontSize: 18,
    fontWeight: 'bold',
  },
  cancelButton: {
    backgroundColor: '#6b7280',
  },
  cancelButtonText: {
    color: '#ffffff',
    fontSize: 16,
    fontWeight: 'bold',
  },
});
