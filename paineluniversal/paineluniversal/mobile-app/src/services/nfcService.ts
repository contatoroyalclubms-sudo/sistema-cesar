import NfcManager, { NfcTech, Ndef, NfcEvents } from 'react-native-nfc-manager';
import { Alert, Platform } from 'react-native';

export interface NFCData {
  id: string;
  type: 'comanda' | 'pulseira' | 'unknown';
  data?: Record<string, any>;
  rawData?: string;
  timestamp: string;
}

class NFCService {
  private isEnabled = false;
  private isReading = false;
  private listeners: Array<(data: NFCData) => void> = [];

  async initialize(): Promise<boolean> {
    try {
      // Verificar se NFC está disponível no dispositivo
      const isSupported = await NfcManager.isSupported();
      if (!isSupported) {
        Alert.alert('NFC não suportado', 'Este dispositivo não suporta NFC');
        return false;
      }

      // Verificar se NFC está habilitado
      const isEnabled = await NfcManager.isEnabled();
      if (!isEnabled) {
        Alert.alert(
          'NFC Desabilitado',
          'Por favor, habilite o NFC nas configurações do dispositivo',
          [
            { text: 'Cancelar', style: 'cancel' },
            { text: 'Abrir Configurações', onPress: () => NfcManager.goToNfcSetting() }
          ]
        );
        return false;
      }

      // Inicializar NFC Manager
      await NfcManager.start();
      this.isEnabled = true;

      console.log('NFC Service inicializado com sucesso');
      return true;

    } catch (error) {
      console.error('Erro ao inicializar NFC:', error);
      Alert.alert('Erro', 'Falha ao inicializar NFC');
      return false;
    }
  }

  async startReading(): Promise<void> {
    if (!this.isEnabled) {
      const initialized = await this.initialize();
      if (!initialized) {
        throw new Error('NFC não pôde ser inicializado');
      }
    }

    if (this.isReading) {
      console.log('NFC já está lendo');
      return;
    }

    try {
      this.isReading = true;

      // Configurar tecnologias NFC a serem lidas
      await NfcManager.requestTechnology([
        NfcTech.Ndef,
        NfcTech.NfcA,
        NfcTech.NfcB,
        NfcTech.NfcF,
        NfcTech.NfcV,
        NfcTech.MifareClassic,
        NfcTech.MifareUltralight,
      ]);

      // Configurar listener para detecção de tags
      NfcManager.setEventListener(NfcEvents.DiscoverTag, this.handleTagDetected.bind(this));

      console.log('NFC Service iniciado - aguardando leitura...');

    } catch (error) {
      this.isReading = false;
      console.error('Erro ao iniciar leitura NFC:', error);
      throw error;
    }
  }

  async stopReading(): Promise<void> {
    if (!this.isReading) {
      return;
    }

    try {
      // Remover listeners
      NfcManager.setEventListener(NfcEvents.DiscoverTag, null);
      
      // Cancelar tecnologia atual
      await NfcManager.cancelTechnologyRequest();
      
      this.isReading = false;
      console.log('NFC Service parado');

    } catch (error) {
      console.error('Erro ao parar leitura NFC:', error);
    }
  }

  private async handleTagDetected(tag: any): Promise<void> {
    console.log('Tag NFC detectada:', tag);

    try {
      const nfcData = await this.parseTagData(tag);
      
      // Notificar todos os listeners
      this.listeners.forEach(listener => {
        try {
          listener(nfcData);
        } catch (error) {
          console.error('Erro no listener NFC:', error);
        }
      });

    } catch (error) {
      console.error('Erro ao processar tag NFC:', error);
      
      // Notificar erro
      const errorData: NFCData = {
        id: tag.id || 'unknown',
        type: 'unknown',
        rawData: JSON.stringify(tag),
        timestamp: new Date().toISOString(),
      };

      this.listeners.forEach(listener => {
        try {
          listener(errorData);
        } catch (error) {
          console.error('Erro no listener NFC:', error);
        }
      });
    }
  }

  private async parseTagData(tag: any): Promise<NFCData> {
    const nfcData: NFCData = {
      id: tag.id || '',
      type: 'unknown',
      timestamp: new Date().toISOString(),
    };

    try {
      // Tentar ler dados NDEF se disponível
      if (tag.ndefMessage && tag.ndefMessage.length > 0) {
        const ndefRecord = tag.ndefMessage[0];
        
        if (ndefRecord.payload) {
          const payload = String.fromCharCode(...ndefRecord.payload);
          console.log('NDEF Payload:', payload);
          
          // Tentar parsear como JSON
          try {
            const jsonData = JSON.parse(payload);
            nfcData.data = jsonData;
            
            // Determinar tipo baseado nos dados
            if (jsonData.tipo === 'comanda' || jsonData.comanda_id) {
              nfcData.type = 'comanda';
            } else if (jsonData.tipo === 'pulseira' || jsonData.pulseira_id) {
              nfcData.type = 'pulseira';
            }
          } catch (parseError) {
            // Se não é JSON, tratar como string
            nfcData.rawData = payload;
            
            // Tentar identificar tipo por padrões na string
            if (payload.includes('comanda') || payload.includes('CMD')) {
              nfcData.type = 'comanda';
            } else if (payload.includes('pulseira') || payload.includes('PUL')) {
              nfcData.type = 'pulseira';
            }
          }
        }
      }

      // Se não conseguiu identificar o tipo, usar ID para determinar
      if (nfcData.type === 'unknown' && nfcData.id) {
        const idStr = nfcData.id.toLowerCase();
        if (idStr.includes('cmd') || idStr.startsWith('c')) {
          nfcData.type = 'comanda';
        } else if (idStr.includes('pul') || idStr.startsWith('p')) {
          nfcData.type = 'pulseira';
        }
      }

      // Salvar dados brutos para debug
      nfcData.rawData = JSON.stringify(tag);

      console.log('Dados NFC processados:', nfcData);
      return nfcData;

    } catch (error) {
      console.error('Erro ao parsear dados NFC:', error);
      nfcData.rawData = JSON.stringify(tag);
      return nfcData;
    }
  }

  addListener(callback: (data: NFCData) => void): () => void {
    this.listeners.push(callback);
    
    // Retornar função para remover listener
    return () => {
      const index = this.listeners.indexOf(callback);
      if (index > -1) {
        this.listeners.splice(index, 1);
      }
    };
  }

  removeAllListeners(): void {
    this.listeners = [];
  }

  async readSingleTag(timeout = 10000): Promise<NFCData> {
    return new Promise(async (resolve, reject) => {
      let timeoutId: NodeJS.Timeout;
      let removeListener: (() => void) | null = null;

      try {
        // Configurar timeout
        timeoutId = setTimeout(() => {
          if (removeListener) removeListener();
          reject(new Error('Timeout na leitura NFC'));
        }, timeout);

        // Adicionar listener temporário
        removeListener = this.addListener((data) => {
          clearTimeout(timeoutId);
          if (removeListener) removeListener();
          resolve(data);
        });

        // Iniciar leitura
        await this.startReading();

      } catch (error) {
        clearTimeout(timeoutId!);
        if (removeListener) removeListener();
        reject(error);
      }
    });
  }

  async writeTag(data: Record<string, any>): Promise<boolean> {
    try {
      if (!this.isEnabled) {
        await this.initialize();
      }

      await NfcManager.requestTechnology(NfcTech.Ndef);

      const bytes = Ndef.encodeMessage([
        Ndef.textRecord(JSON.stringify(data))
      ]);

      await NfcManager.ndefHandler.writeNdefMessage(bytes);
      await NfcManager.cancelTechnologyRequest();

      console.log('Dados escritos na tag NFC com sucesso');
      return true;

    } catch (error) {
      console.error('Erro ao escrever na tag NFC:', error);
      await NfcManager.cancelTechnologyRequest();
      throw error;
    }
  }

  getIsReading(): boolean {
    return this.isReading;
  }

  getIsEnabled(): boolean {
    return this.isEnabled;
  }

  async cleanup(): Promise<void> {
    try {
      await this.stopReading();
      this.removeAllListeners();
      
      if (this.isEnabled) {
        await NfcManager.stop();
        this.isEnabled = false;
      }
    } catch (error) {
      console.error('Erro no cleanup do NFC Service:', error);
    }
  }
}

export const nfcService = new NFCService();
