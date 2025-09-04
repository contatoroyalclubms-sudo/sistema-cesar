import { Alert, Platform } from 'react-native';
import NfcManager, { NfcTech, Ndef, NfcEvents } from 'react-native-nfc-manager';

export interface ComandaNFC {
  numeroComanda: string;
  mesaNumero: number;
  restauranteId: string;
  clienteNome?: string;
  observacoes?: string;
  dataHora?: string;
  status?: 'ativa' | 'finalizada' | 'cancelada';
}

export interface NFCReadResult {
  success: boolean;
  data?: ComandaNFC;
  error?: string;
  rawData?: any;
}

export interface NFCStatus {
  isSupported: boolean;
  isEnabled: boolean;
  message?: string;
}

// Legacy interface compatibility
export interface NFCResult {
  success: boolean;
  data?: string;
  error?: string;
}

class NFCService {
  private isInitialized = false;
  private isReading = false;

  /**
   * Inicializa o NFC Manager
   */
  async initialize(): Promise<boolean> {
    try {
      if (this.isInitialized) {
        return true;
      }

      console.log('🔄 Inicializando NFC Manager...');
      const supported = await NfcManager.isSupported();
      
      if (!supported) {
        console.warn('❌ NFC não suportado neste dispositivo');
        return false;
      }

      await NfcManager.start();
      this.isInitialized = true;
      console.log('✅ NFC Manager inicializado com sucesso');
      return true;

    } catch (error) {
      console.error('❌ Erro ao inicializar NFC:', error);
      return false;
    }
  }

  /**
   * Verifica status do NFC (disponibilidade e se está habilitado)
   */
  async checkNFCStatus(): Promise<NFCStatus> {
    try {
      // Inicializar se necessário
      if (!this.isInitialized) {
        const initialized = await this.initialize();
        if (!initialized) {
          return {
            isSupported: false,
            isEnabled: false,
            message: 'NFC não é suportado neste dispositivo'
          };
        }
      }

      const isSupported = await NfcManager.isSupported();
      
      if (!isSupported) {
        return {
          isSupported: false,
          isEnabled: false,
          message: 'Este dispositivo não possui hardware NFC'
        };
      }

      const isEnabled = await NfcManager.isEnabled();
      
      return {
        isSupported: true,
        isEnabled,
        message: isEnabled 
          ? 'NFC está ativo e pronto para uso' 
          : 'NFC está desabilitado. Ative nas configurações do dispositivo.'
      };

    } catch (error) {
      console.error('❌ Erro ao verificar status do NFC:', error);
      return {
        isSupported: false,
        isEnabled: false,
        message: `Erro ao verificar NFC: ${error}`
      };
    }
  }

  /**
   * Solicitar permissões necessárias (compatibility method)
   */
  async requestPermissions(): Promise<boolean> {
    try {
      const status = await this.checkNFCStatus();
      return status.isSupported && status.isEnabled;
    } catch (error) {
      console.error('❌ Erro ao solicitar permissões NFC:', error);
      return false;
    }
  }

  /**
   * Inicia a leitura de uma tag NFC
   */
  async startReading(): Promise<NFCReadResult> {
    try {
      if (this.isReading) {
        return {
          success: false,
          error: 'Leitura NFC já está em andamento'
        };
      }

      // Verificar status primeiro
      const status = await this.checkNFCStatus();
      if (!status.isSupported) {
        return {
          success: false,
          error: 'NFC não é suportado neste dispositivo'
        };
      }

      if (!status.isEnabled) {
        return {
          success: false,
          error: 'NFC está desabilitado. Ative nas configurações do dispositivo.'
        };
      }

      this.isReading = true;
      console.log('🔄 Iniciando leitura NFC...');

      // Configurar tecnologias NFC para leitura
      await NfcManager.requestTechnology(NfcTech.Ndef);

      // Ler a tag
      const tag = await NfcManager.getTag();
      console.log('📱 Tag NFC detectada:', tag);

      // Processar dados NDEF se disponíveis
      let comandaData: ComandaNFC | null = null;
      
      if (tag && tag.ndefMessage && tag.ndefMessage.length > 0) {
        comandaData = this.parseNdefMessage(tag.ndefMessage);
      }

      // Parar tecnologia NFC
      await NfcManager.cancelTechnologyRequest();
      this.isReading = false;

      if (comandaData) {
        console.log('✅ Dados da comanda extraídos:', comandaData);
        return {
          success: true,
          data: comandaData,
          rawData: tag
        };
      } else {
        return {
          success: false,
          error: 'Tag NFC não contém dados de comanda válidos',
          rawData: tag
        };
      }

    } catch (error: any) {
      console.error('❌ Erro na leitura NFC:', error);
      
      // Limpar estado
      this.isReading = false;
      try {
        await NfcManager.cancelTechnologyRequest();
      } catch (cleanupError) {
        console.warn('⚠️ Erro ao limpar tecnologia NFC:', cleanupError);
      }

      // Mapear erros específicos
      let errorMessage = 'Erro desconhecido na leitura NFC';
      
      if (error.message?.includes('cancelled') || error.message?.includes('timeout')) {
        errorMessage = 'Leitura cancelada ou timeout. Tente novamente.';
      } else if (error.message?.includes('not available')) {
        errorMessage = 'NFC não está disponível neste momento.';
      } else if (error.message?.includes('denied')) {
        errorMessage = 'Permissão NFC negada.';
      } else if (error.message) {
        errorMessage = error.message;
      }

      return {
        success: false,
        error: errorMessage,
        rawData: error
      };
    }
  }

  /**
   * Para a leitura NFC em andamento
   */
  async stopReading(): Promise<void> {
    try {
      if (this.isReading) {
        console.log('🛑 Parando leitura NFC...');
        await NfcManager.cancelTechnologyRequest();
        this.isReading = false;
        console.log('✅ Leitura NFC parada');
      }
    } catch (error) {
      console.error('❌ Erro ao parar leitura NFC:', error);
      this.isReading = false;
    }
  }

  /**
   * Processa mensagem NDEF da tag para extrair dados da comanda
   */
  private parseNdefMessage(ndefMessage: any[]): ComandaNFC | null {
    try {
      for (const record of ndefMessage) {
        // Verificar se é um record de texto
        if (record.type && record.payload) {
          const payload = record.payload;
          
          // Converter payload para string
          let textData = '';
          
          if (payload instanceof Array) {
            // Skip language code (primeiro byte) e extrair texto
            const languageCodeLength = payload[0] || 0;
            const textBytes = payload.slice(languageCodeLength + 1);
            textData = String.fromCharCode.apply(null, textBytes);
          } else if (typeof payload === 'string') {
            textData = payload;
          }

          console.log('📄 Dados extraídos da tag:', textData);

          // Tentar parsear como JSON
          try {
            const jsonData = JSON.parse(textData);
            
            // Validar estrutura da comanda
            if (this.validateComandaData(jsonData)) {
              return jsonData as ComandaNFC;
            }
          } catch (parseError) {
            console.warn('⚠️ Dados não são JSON válido:', parseError);
          }

          // Tentar interpretar como texto estruturado
          const parsedData = this.parseStructuredText(textData);
          if (parsedData) {
            return parsedData;
          }
        }
      }

      console.warn('⚠️ Nenhum dado de comanda válido encontrado na tag');
      return null;

    } catch (error) {
      console.error('❌ Erro ao processar mensagem NDEF:', error);
      return null;
    }
  }

  /**
   * Valida se os dados extraídos têm a estrutura correta de uma comanda
   */
  private validateComandaData(data: any): boolean {
    if (!data || typeof data !== 'object') {
      return false;
    }

    // Campos obrigatórios
    const requiredFields = ['numeroComanda', 'mesaNumero', 'restauranteId'];
    
    for (const field of requiredFields) {
      if (!(field in data) || data[field] === null || data[field] === undefined) {
        console.warn(`⚠️ Campo obrigatório ausente: ${field}`);
        return false;
      }
    }

    // Validações específicas
    if (typeof data.numeroComanda !== 'string' || data.numeroComanda.trim() === '') {
      console.warn('⚠️ numeroComanda deve ser uma string não vazia');
      return false;
    }

    if (typeof data.mesaNumero !== 'number' || data.mesaNumero <= 0) {
      console.warn('⚠️ mesaNumero deve ser um número positivo');
      return false;
    }

    if (typeof data.restauranteId !== 'string' || data.restauranteId.trim() === '') {
      console.warn('⚠️ restauranteId deve ser uma string não vazia');
      return false;
    }

    console.log('✅ Dados da comanda válidos');
    return true;
  }

  /**
   * Tenta interpretar texto estruturado como dados de comanda
   */
  private parseStructuredText(text: string): ComandaNFC | null {
    try {
      // Formatos possíveis:
      // "MESA:5|COMANDA:C001|RESTAURANTE:REST001"
      // "Mesa 5 - Comanda C001 - Restaurant REST001"
      
      const data: Partial<ComandaNFC> = {};
      
      // Padrão com separadores |
      if (text.includes('|')) {
        const parts = text.split('|');
        for (const part of parts) {
          const [key, value] = part.split(':').map(s => s.trim());
          
          switch (key?.toUpperCase()) {
            case 'MESA':
              data.mesaNumero = parseInt(value);
              break;
            case 'COMANDA':
              data.numeroComanda = value;
              break;
            case 'RESTAURANTE':
            case 'REST':
              data.restauranteId = value;
              break;
            case 'CLIENTE':
              data.clienteNome = value;
              break;
          }
        }
      }
      
      // Verificar se temos dados suficientes
      if (data.numeroComanda && data.mesaNumero && data.restauranteId) {
        const comandaData: ComandaNFC = {
          numeroComanda: data.numeroComanda,
          mesaNumero: data.mesaNumero,
          restauranteId: data.restauranteId,
          clienteNome: data.clienteNome,
          status: 'ativa'
        };
        
        console.log('✅ Dados estruturados interpretados:', comandaData);
        return comandaData;
      }

      return null;

    } catch (error) {
      console.error('❌ Erro ao interpretar texto estruturado:', error);
      return null;
    }
  }

  /**
   * Verificar se está lendo atualmente (compatibility method)
   */
  isCurrentlyReading(): boolean {
    return this.isReading;
  }

  /**
   * Gerar dados mock para desenvolvimento (compatibility method)
   */
  generateMockNFCData(mesaId?: number): string {
    const mockData = {
      numeroComanda: `C${Date.now().toString().slice(-4)}`,
      mesaNumero: mesaId || Math.floor(Math.random() * 20) + 1,
      restauranteId: 'PDV-UNIVERSAL-001',
      clienteNome: 'Cliente Teste',
      dataHora: new Date().toISOString(),
      status: 'ativa'
    };
    
    return JSON.stringify(mockData);
  }

  /**
   * Teste rápido com dados simulados (para desenvolvimento e fallback)
   */
  async quickTest(mesaId?: number): Promise<NFCReadResult> {
    console.log('🧪 Executando teste rápido...');
    
    // Simular delay de leitura
    await new Promise(resolve => setTimeout(resolve, 1500));
    
    const testData: ComandaNFC = {
      numeroComanda: `C${Date.now().toString().slice(-4)}`,
      mesaNumero: mesaId || Math.floor(Math.random() * 20) + 1,
      restauranteId: 'PDV-UNIVERSAL-001',
      clienteNome: 'Cliente Teste',
      dataHora: new Date().toISOString(),
      status: 'ativa'
    };

    console.log('✅ Dados de teste gerados:', testData);
    
    return {
      success: true,
      data: testData
    };
  }

  /**
   * Mostra instruções de uso do NFC
   */
  showInstructions(): void {
    const instructions = Platform.select({
      ios: `📱 COMO USAR NFC NO iOS:

1. Certifique-se que o NFC está habilitado nas Configurações
2. Toque em "Ler NFC" 
3. Aproxime a parte superior do iPhone da tag NFC
4. Aguarde a vibração/som de confirmação

⚠️ Nota: iPhone 7/7+ ou superior necessário

🏷️ FORMATO DA TAG NFC:
A tag deve conter dados JSON com:
- numeroComanda: string
- mesaNumero: number  
- restauranteId: string
- clienteNome: string (opcional)`,

      android: `📱 COMO USAR NFC NO ANDROID:

1. Ative o NFC nas Configurações do dispositivo
2. Toque em "Ler NFC"
3. Aproxime a parte traseira do telefone da tag NFC
4. Mantenha próximo até ler os dados

⚠️ Nota: Nem todos os dispositivos Android possuem NFC

🏷️ FORMATO DA TAG NFC:
A tag deve conter dados JSON com:
- numeroComanda: string
- mesaNumero: number
- restauranteId: string  
- clienteNome: string (opcional)`,

      default: `📱 COMO USAR NFC:

1. Certifique-se que o NFC está habilitado
2. Toque em "Ler NFC"
3. Aproxime o dispositivo da tag NFC
4. Aguarde a leitura dos dados

🏷️ FORMATO DA TAG NFC:
A tag deve conter dados JSON com os campos da comanda.`
    });

    Alert.alert('📖 Instruções NFC', instructions, [
      { text: 'Entendi', style: 'default' }
    ]);
  }

  /**
   * Cleanup - para ser chamado quando o componente for desmontado
   */
  async cleanup(): Promise<void> {
    try {
      if (this.isReading) {
        await this.stopReading();
      }
      
      if (this.isInitialized) {
        console.log('🧹 Limpeza do NFC Manager...');
        await NfcManager.stop();
        this.isInitialized = false;
        console.log('✅ NFC Manager finalizado');
      }
    } catch (error) {
      console.error('❌ Erro na limpeza do NFC:', error);
    }
  }
}

// Instância singleton
const nfcService = new NFCService();

export default nfcService;
