import React, { createContext, useContext, useReducer, useEffect } from 'react';
import AsyncStorage from '@react-native-async-storage/async-storage';
import * as SecureStore from 'expo-secure-store';
import { apiService } from '../services/apiService';

interface User {
  id: number;
  nome: string;
  cpf: string;
  tipo: string;
}

interface Evento {
  id: number;
  nome: string;
  data_evento: string;
  local: string;
}

interface AuthState {
  isAuthenticated: boolean;
  user: User | null;
  evento: Evento | null;
  token: string | null;
  sessionId: string | null;
  isLoading: boolean;
  error: string | null;
}

type AuthAction =
  | { type: 'LOGIN_START' }
  | { type: 'LOGIN_SUCCESS'; payload: { user: User; evento: Evento; token: string; sessionId: string } }
  | { type: 'LOGIN_FAILURE'; payload: string }
  | { type: 'LOGOUT' }
  | { type: 'CLEAR_ERROR' }
  | { type: 'RESTORE_SESSION'; payload: { user: User; evento: Evento; token: string; sessionId: string } };

const initialState: AuthState = {
  isAuthenticated: false,
  user: null,
  evento: null,
  token: null,
  sessionId: null,
  isLoading: false,
  error: null,
};

const authReducer = (state: AuthState, action: AuthAction): AuthState => {
  switch (action.type) {
    case 'LOGIN_START':
      return {
        ...state,
        isLoading: true,
        error: null,
      };
    
    case 'LOGIN_SUCCESS':
      return {
        ...state,
        isAuthenticated: true,
        user: action.payload.user,
        evento: action.payload.evento,
        token: action.payload.token,
        sessionId: action.payload.sessionId,
        isLoading: false,
        error: null,
      };
    
    case 'LOGIN_FAILURE':
      return {
        ...state,
        isAuthenticated: false,
        user: null,
        evento: null,
        token: null,
        sessionId: null,
        isLoading: false,
        error: action.payload,
      };
    
    case 'LOGOUT':
      return {
        ...initialState,
      };
    
    case 'CLEAR_ERROR':
      return {
        ...state,
        error: null,
      };
    
    case 'RESTORE_SESSION':
      return {
        ...state,
        isAuthenticated: true,
        user: action.payload.user,
        evento: action.payload.evento,
        token: action.payload.token,
        sessionId: action.payload.sessionId,
        isLoading: false,
      };
    
    default:
      return state;
  }
};

interface AuthContextType {
  state: AuthState;
  login: (cpf: string, senha: string, eventoId: number, deviceInfo: any) => Promise<void>;
  logout: () => Promise<void>;
  clearError: () => void;
  sendHeartbeat: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth deve ser usado dentro de um AuthProvider');
  }
  return context;
};

interface AuthProviderProps {
  children: React.ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [state, dispatch] = useReducer(authReducer, initialState);

  // Restaurar sessão ao inicializar
  useEffect(() => {
    restoreSession();
  }, []);

  // Heartbeat automático a cada 5 minutos
  useEffect(() => {
    if (state.isAuthenticated && state.token) {
      const interval = setInterval(() => {
        sendHeartbeat();
      }, 5 * 60 * 1000); // 5 minutos

      return () => clearInterval(interval);
    }
  }, [state.isAuthenticated, state.token]);

  const restoreSession = async () => {
    try {
      const token = await SecureStore.getItemAsync('auth_token');
      const sessionId = await SecureStore.getItemAsync('session_id');
      const userStr = await AsyncStorage.getItem('user_data');
      const eventoStr = await AsyncStorage.getItem('evento_data');

      if (token && sessionId && userStr && eventoStr) {
        const user = JSON.parse(userStr);
        const evento = JSON.parse(eventoStr);

        // Configurar token no serviço API
        apiService.setAuthToken(token);

        dispatch({
          type: 'RESTORE_SESSION',
          payload: { user, evento, token, sessionId }
        });

        // Verificar se sessão ainda é válida
        await sendHeartbeat();
      }
    } catch (error) {
      console.error('Erro ao restaurar sessão:', error);
      await logout();
    }
  };

  const login = async (
    cpf: string, 
    senha: string, 
    eventoId: number, 
    deviceInfo: any
  ): Promise<void> => {
    dispatch({ type: 'LOGIN_START' });

    try {
      // Primeiro fazer login normal
      const authResponse = await apiService.login(cpf, senha);
      
      if (!authResponse.success) {
        throw new Error(authResponse.message || 'Erro no login');
      }

      // Configurar token no serviço API
      apiService.setAuthToken(authResponse.token);

      // Fazer login mobile específico
      const mobileLoginResponse = await apiService.post('/pdv-mobile/login', {
        evento_id: eventoId,
        device_id: deviceInfo.deviceId,
        app_version: deviceInfo.appVersion,
        device_info: deviceInfo,
      });

      // Salvar dados de autenticação
      await SecureStore.setItemAsync('auth_token', mobileLoginResponse.token);
      await SecureStore.setItemAsync('session_id', mobileLoginResponse.sessao_id);
      await AsyncStorage.setItem('user_data', JSON.stringify(mobileLoginResponse.garcom));
      await AsyncStorage.setItem('evento_data', JSON.stringify(mobileLoginResponse.evento));

      dispatch({
        type: 'LOGIN_SUCCESS',
        payload: {
          user: mobileLoginResponse.garcom,
          evento: mobileLoginResponse.evento,
          token: mobileLoginResponse.token,
          sessionId: mobileLoginResponse.sessao_id,
        }
      });

    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || error.message || 'Erro no login';
      dispatch({ type: 'LOGIN_FAILURE', payload: errorMessage });
      throw error;
    }
  };

  const logout = async (): Promise<void> => {
    try {
      // Tentar finalizar sessão no servidor
      if (state.sessionId) {
        await apiService.post('/pdv-mobile/logout', {
          motivo: 'logout_manual',
          observacoes: 'Logout realizado pelo usuário'
        });
      }
    } catch (error) {
      console.error('Erro ao finalizar sessão no servidor:', error);
    }

    // Limpar dados locais
    await SecureStore.deleteItemAsync('auth_token');
    await SecureStore.deleteItemAsync('session_id');
    await AsyncStorage.removeItem('user_data');
    await AsyncStorage.removeItem('evento_data');
    await AsyncStorage.removeItem('cart_data');
    await AsyncStorage.removeItem('offline_data');

    // Limpar token do serviço API
    apiService.setAuthToken(null);

    dispatch({ type: 'LOGOUT' });
  };

  const clearError = (): void => {
    dispatch({ type: 'CLEAR_ERROR' });
  };

  const sendHeartbeat = async (): Promise<void> => {
    if (!state.token || !state.sessionId) {
      return;
    }

    try {
      const deviceInfo = {
        timestamp: new Date().toISOString(),
        status_app: 'ativo',
        // Adicionar mais informações do device se necessário
      };

      const response = await apiService.post('/pdv-mobile/heartbeat', deviceInfo);

      if (!response.success || !response.sessao_ativa) {
        // Sessão expirada, fazer logout
        await logout();
      }

      // Se configuração foi atualizada, recarregar
      if (response.configuracao_atualizada && response.nova_configuracao) {
        await AsyncStorage.setItem(
          'configuracao_mobile', 
          JSON.stringify(response.nova_configuracao)
        );
      }

    } catch (error: any) {
      console.error('Erro no heartbeat:', error);
      
      // Se erro de autenticação, fazer logout
      if (error.response?.status === 401) {
        await logout();
      }
    }
  };

  const contextValue: AuthContextType = {
    state,
    login,
    logout,
    clearError,
    sendHeartbeat,
  };

  return (
    <AuthContext.Provider value={contextValue}>
      {children}
    </AuthContext.Provider>
  );
};
