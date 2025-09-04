import React, { createContext, useContext, useState, useEffect } from 'react';
import AsyncStorage from '@react-native-async-storage/async-storage';
// Simplificado - sem NetInfo por enquanto

interface OfflineState {
  isConnected: boolean;
  pendingSync: any[];
  lastSyncTime: string | null;
  syncInProgress: boolean;
  error: string | null;
}

interface OfflineContextType {
  state: OfflineState;
  addToSyncQueue: (data: any) => Promise<void>;
  syncPendingData: () => Promise<void>;
  clearSyncQueue: () => Promise<void>;
  clearError: () => void;
}

const initialState: OfflineState = {
  isConnected: true,
  pendingSync: [],
  lastSyncTime: null,
  syncInProgress: false,
  error: null,
};

const OfflineContext = createContext<OfflineContextType | undefined>(undefined);

export const useOffline = () => {
  const context = useContext(OfflineContext);
  if (!context) {
    throw new Error('useOffline deve ser usado dentro de um OfflineProvider');
  }
  return context;
};

interface OfflineProviderProps {
  children: React.ReactNode;
}

export const OfflineProvider: React.FC<OfflineProviderProps> = ({ children }) => {
  const [state, setState] = useState<OfflineState>(initialState);

  useEffect(() => {
    // Por enquanto, assumir sempre conectado
    // TODO: Implementar detecção de conectividade real
    setState(prev => ({
      ...prev,
      isConnected: true,
    }));

    // Carregar dados de sincronização pendentes
    loadPendingSync();
  }, []);

  const loadPendingSync = async (): Promise<void> => {
    try {
      const pendingData = await AsyncStorage.getItem('pending_sync');
      const lastSync = await AsyncStorage.getItem('last_sync_time');
      
      setState(prev => ({
        ...prev,
        pendingSync: pendingData ? JSON.parse(pendingData) : [],
        lastSyncTime: lastSync,
      }));
    } catch (error: any) {
      console.error('Erro ao carregar dados offline:', error);
      setState(prev => ({
        ...prev,
        error: `Erro ao carregar dados offline: ${error.message}`,
      }));
    }
  };

  const addToSyncQueue = async (data: any): Promise<void> => {
    try {
      const newItem = {
        id: `${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
        data,
        timestamp: new Date().toISOString(),
        attempts: 0,
        maxAttempts: 3,
      };

      const updatedQueue = [...state.pendingSync, newItem];
      
      setState(prev => ({
        ...prev,
        pendingSync: updatedQueue,
      }));

      await AsyncStorage.setItem('pending_sync', JSON.stringify(updatedQueue));

      // Se está conectado, tentar sincronizar imediatamente
      if (state.isConnected) {
        await syncPendingData();
      }

    } catch (error: any) {
      console.error('Erro ao adicionar à fila de sincronização:', error);
      setState(prev => ({
        ...prev,
        error: `Erro ao salvar dados offline: ${error.message}`,
      }));
    }
  };

  const syncPendingData = async (): Promise<void> => {
    if (!state.isConnected || state.syncInProgress || state.pendingSync.length === 0) {
      return;
    }

    setState(prev => ({
      ...prev,
      syncInProgress: true,
      error: null,
    }));

    try {
      const successfulSync: string[] = [];
      const failedSync: any[] = [];

      for (const item of state.pendingSync) {
        try {
          // Aqui você implementaria a lógica específica de sincronização
          // baseada no tipo de dados
          await syncSingleItem(item);
          successfulSync.push(item.id);
        } catch (syncError: any) {
          console.error(`Erro ao sincronizar item ${item.id}:`, syncError);
          
          // Incrementar tentativas
          item.attempts += 1;
          
          // Se não excedeu o máximo de tentativas, manter na fila
          if (item.attempts < item.maxAttempts) {
            failedSync.push(item);
          } else {
            console.warn(`Item ${item.id} descartado após ${item.maxAttempts} tentativas`);
          }
        }
      }

      // Atualizar fila com apenas os itens que falharam
      setState(prev => ({
        ...prev,
        pendingSync: failedSync,
        lastSyncTime: new Date().toISOString(),
        syncInProgress: false,
      }));

      await AsyncStorage.setItem('pending_sync', JSON.stringify(failedSync));
      await AsyncStorage.setItem('last_sync_time', new Date().toISOString());

      console.log(`Sincronização concluída: ${successfulSync.length} sucessos, ${failedSync.length} falhas`);

    } catch (error: any) {
      console.error('Erro durante sincronização:', error);
      setState(prev => ({
        ...prev,
        syncInProgress: false,
        error: `Erro na sincronização: ${error.message}`,
      }));
    }
  };

  const syncSingleItem = async (item: any): Promise<void> => {
    // Implementar lógica específica baseada no tipo de dados
    const { data } = item;
    
    switch (data.type) {
      case 'pedido':
        // Sincronizar pedido
        // await apiService.post('/pdv-mobile/pedidos', data.payload);
        break;
      
      case 'nfc_read':
        // Sincronizar leitura NFC
        // await apiService.post('/pdv-mobile/nfc/sync', data.payload);
        break;
      
      case 'heartbeat':
        // Sincronizar heartbeat
        // await apiService.post('/pdv-mobile/heartbeat', data.payload);
        break;
      
      default:
        console.warn(`Tipo de dados desconhecido para sincronização: ${data.type}`);
    }
  };

  const clearSyncQueue = async (): Promise<void> => {
    try {
      setState(prev => ({
        ...prev,
        pendingSync: [],
      }));

      await AsyncStorage.removeItem('pending_sync');
    } catch (error: any) {
      console.error('Erro ao limpar fila de sincronização:', error);
      setState(prev => ({
        ...prev,
        error: `Erro ao limpar dados offline: ${error.message}`,
      }));
    }
  };

  const clearError = (): void => {
    setState(prev => ({
      ...prev,
      error: null,
    }));
  };

  const contextValue: OfflineContextType = {
    state,
    addToSyncQueue,
    syncPendingData,
    clearSyncQueue,
    clearError,
  };

  return (
    <OfflineContext.Provider value={contextValue}>
      {children}
    </OfflineContext.Provider>
  );
};
