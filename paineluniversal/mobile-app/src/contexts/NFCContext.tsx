import React, { createContext, useContext, useState, useEffect } from 'react';
import NfcManager, { NfcTech, Ndef } from 'react-native-nfc-manager';
import * as Haptics from 'expo-haptics';
import { Platform } from 'react-native';

interface NFCData {
  id: string;
  type: 'comanda' | 'pulseira' | 'unknown';
  data: any;
  timestamp: string;
}

interface NFCState {
  isEnabled: boolean;
  isScanning: boolean;
  lastScan: NFCData | null;
  error: string | null;
  supportedTechnologies: string[];
}

interface NFCContextType {
  state: NFCState;
  initNFC: () => Promise<boolean>;
  startScan: () => Promise<void>;
  stopScan: () => Promise<void>;
  clearError: () => void;
  clearLastScan: () => void;
}

const initialState: NFCState = {
  isEnabled: false,
  isScanning: false,
  lastScan: null,
  error: null,
  supportedTechnologies: [],
};

const NFCContext = createContext<NFCContextType | undefined>(undefined);

export const useNFC = () => {
  const context = useContext(NFCContext);
  if (!context) {
    throw new Error('useNFC deve ser usado dentro de um NFCProvider');
  }
  return context;
};

interface NFCProviderProps {
  children: React.ReactNode;
}

export const NFCProvider: React.FC<NFCProviderProps> = ({ children }) => {
  const [state, setState] = useState<NFCState>(initialState);

  useEffect(() => {
    // Inicializar NFC ao montar o componente
    initNFC();

    // Cleanup ao desmontar
    return () => {
      stopScan();
      NfcManager.stop();
    };
  }, []);

  const initNFC = async (): Promise<boolean> => {
    try {
      // Verificar se o dispositivo suporta NFC
      if (Platform.OS === 'ios') {
        // iOS tem limitações de NFC
        setState(prev => ({
          ...prev,
          error: 'NFC limitado no iOS. Use um dispositivo Android para melhor experiência.',
        }));
        return false;
      }

      // Inicializar NFC Manager
      const isSupported = await NfcManager.isSupported();
      
      if (!isSupported) {
        setState(prev => ({
          ...prev,
          error: 'Dispositivo não suporta NFC',
        }));
        return false;
      }

      await NfcManager.start();

      // Verificar se NFC está habilitado
      const isEnabled = await NfcManager.isEnabled();

      // Obter tecnologias suportadas
      const technologies = await NfcManager.getSupportedTechnologies();

      setState(prev => ({
        ...prev,
        isEnabled,
        supportedTechnologies: technologies,
        error: isEnabled ? null : 'NFC está desabilitado. Habilite nas configurações do dispositivo.',
      }));

      return isEnabled;

    } catch (error: any) {
      console.error('Erro ao inicializar NFC:', error);
      setState(prev => ({
        ...prev,
        error: `Erro ao inicializar NFC: ${error.message}`,
      }));
      return false;
    }
  };

  const startScan = async (): Promise<void> => {
    try {
      if (!state.isEnabled) {
        await initNFC();
        if (!state.isEnabled) {
          throw new Error('NFC não está disponível');
        }
      }

      setState(prev => ({
        ...prev,
        isScanning: true,
        error: null,
      }));

      // Configurar tecnologias para escaneamento
      await NfcManager.requestTechnology([
        NfcTech.Ndef,
        NfcTech.NfcA,
        NfcTech.NfcB,
        NfcTech.NfcF,
        NfcTech.NfcV,
        NfcTech.IsoDep,
        NfcTech.MifareClassic,
        NfcTech.MifareUltralight,
      ]);

      // Ler dados da tag
      const tag = await NfcManager.getTag();
      console.log('Tag detectada:', tag);

      // Tentar ler dados NDEF se disponível
      let ndefData = null;
      try {
        ndefData = await NfcManager.getNdefMessage();
      } catch (ndefError) {
        console.log('Tag não contém dados NDEF ou erro ao ler:', ndefError);
      }

      // Processar dados da tag
      const processedData = processNFCTag(tag, ndefData);

      setState(prev => ({
        ...prev,
        lastScan: processedData,
        isScanning: false,
      }));

      // Feedback háptico de sucesso
      await Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);

    } catch (error: any) {
      console.error('Erro no escaneamento NFC:', error);
      
      setState(prev => ({
        ...prev,
        isScanning: false,
        error: error.message === 'cancelled' 
          ? 'Escaneamento cancelado' 
          : `Erro no escaneamento: ${error.message}`,
      }));

      // Feedback háptico de erro
      await Haptics.notificationAsync(Haptics.NotificationFeedbackType.Error);
    }
  };

  const stopScan = async (): Promise<void> => {
    try {
      await NfcManager.cancelTechnologyRequest();
      setState(prev => ({
        ...prev,
        isScanning: false,
      }));
    } catch (error: any) {
      console.error('Erro ao parar escaneamento:', error);
    }
  };

  const clearError = (): void => {
    setState(prev => ({
      ...prev,
      error: null,
    }));
  };

  const clearLastScan = (): void => {
    setState(prev => ({
      ...prev,
      lastScan: null,
    }));
  };

  const processNFCTag = (tag: any, ndefData: any): NFCData => {
    const timestamp = new Date().toISOString();
    
    // Identificar tipo de tag baseado nos dados
    let type: 'comanda' | 'pulseira' | 'unknown' = 'unknown';
    let processedData: any = {
      tagId: tag.id,
      techList: tag.techList,
      rawData: tag,
    };

    // Se há dados NDEF, processar
    if (ndefData && ndefData.length > 0) {
      const ndefRecord = ndefData[0];
      if (ndefRecord.payload) {
        try {
          // Tentar decodificar payload como texto
          const payload = String.fromCharCode.apply(null, ndefRecord.payload);
          processedData.ndefPayload = payload;
          
          // Determinar tipo baseado no conteúdo
          if (payload.includes('comanda') || payload.includes('mesa')) {
            type = 'comanda';
          } else if (payload.includes('pulseira') || payload.includes('cliente')) {
            type = 'pulseira';
          }
        } catch (decodeError) {
          console.error('Erro ao decodificar NDEF:', decodeError);
        }
      }
    }

    // Se não conseguiu determinar pelo NDEF, usar heurísticas baseadas no ID
    if (type === 'unknown' && tag.id) {
      const tagIdHex = tag.id.toLowerCase();
      
      // Heurísticas simples baseadas em padrões comuns
      if (tagIdHex.startsWith('04') || tagIdHex.length === 14) {
        type = 'pulseira'; // Mifare Ultralight comum em pulseiras
      } else if (tagIdHex.length === 8) {
        type = 'comanda'; // Mifare Classic comum em comandas
      }
    }

    return {
      id: tag.id || 'unknown',
      type,
      data: processedData,
      timestamp,
    };
  };

  const contextValue: NFCContextType = {
    state,
    initNFC,
    startScan,
    stopScan,
    clearError,
    clearLastScan,
  };

  return (
    <NFCContext.Provider value={contextValue}>
      {children}
    </NFCContext.Provider>
  );
};
