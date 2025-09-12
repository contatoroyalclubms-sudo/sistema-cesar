import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { Usuario } from '../types/main';
import { authService } from '../services';

interface AuthState {
  user: Usuario | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
}

interface AuthActions {
  login: (cpf: string, senha: string) => Promise<void>;
  register: (userData: RegisterData) => Promise<void>;
  logout: () => void;
  setUser: (user: Usuario) => void;
  setToken: (token: string) => void;
  revalidateUser: () => Promise<void>;
  initialize: () => Promise<void>;
  validateToken: () => Promise<void>;
}

interface RegisterData {
  nome: string;
  email: string;
  senha: string;
  tipo: 'admin' | 'promoter' | 'cliente';
}

export type AuthStore = AuthState & AuthActions;

export const useAuthStore = create<AuthStore>()(
  persist(
    (set, get) => ({
      // Estado inicial
      user: null,
      token: null,
      isAuthenticated: false,
      isLoading: true,

      // Ações
      login: async (cpf: string, senha: string) => {
        set({ isLoading: true });
        
        try {
          console.log('🔐 AuthStore: Iniciando login...');
          
          // Usar apenas CPF - sem detecção de email
          const response = await authService.login({
            cpf: cpf,
            senha
          });

          if (response.access_token) {
            console.log('✅ Token recebido, salvando estado...');
            set({
              token: response.access_token,
              user: response.usuario,
              isAuthenticated: true,
              isLoading: false
            });

            // Salvar no localStorage também (para compatibilidade)
            localStorage.setItem('token', response.access_token);
            localStorage.setItem('usuario', JSON.stringify(response.usuario));
            
            console.log('✅ Login completo!');
          } else {
            throw new Error('Token não recebido do servidor');
          }
        } catch (error: any) {
          console.error('❌ Erro no login:', error);
          set({ isLoading: false });
          throw error;
        }
      },

      register: async (userData: RegisterData) => {
        set({ isLoading: true });
        
        try {
          // Simular um CPF baseado no email para compatibilidade
          const mockCpf = userData.email.replace(/\D/g, '').padStart(11, '0').slice(0, 11);
          
          const response = await authService.register({
            cpf: mockCpf,
            // nome removido, não existe no tipo
            // email removido, não existe no tipo
            senha: userData.senha,
            tipo: userData.tipo
          });

          // Simular retorno de token para registro
          const tokenResponse = {
            access_token: 'mock_token_' + Date.now(),
            token_type: 'bearer',
            usuario: response
          };

          set({
            token: tokenResponse.access_token,
            user: tokenResponse.usuario,
            isAuthenticated: true,
            isLoading: false
          });

          // Salvar no localStorage
          localStorage.setItem('token', tokenResponse.access_token);
          localStorage.setItem('usuario', JSON.stringify(tokenResponse.usuario));
        } catch (error) {
          set({ isLoading: false });
          throw error;
        }
      },

      logout: () => {
        set({
          user: null,
          token: null,
          isAuthenticated: false,
          isLoading: false
        });

        // Limpar localStorage
        localStorage.removeItem('token');
        localStorage.removeItem('usuario');
        
        // Limpar storage do Zustand
        localStorage.removeItem('auth-storage');
      },

      setUser: (user: Usuario) => {
        set({ user });
        localStorage.setItem('usuario', JSON.stringify(user));
      },

      setToken: (token: string) => {
        set({ token, isAuthenticated: true });
        localStorage.setItem('token', token);
      },

      revalidateUser: async () => {
        const { token } = get();
        if (!token) return;

        try {
          const user = await authService.getProfile();
          set({ user });
        } catch (error) {
          console.error('Erro ao revalidar usuário:', error);
          // Se der erro, fazer logout
          get().logout();
        }
      },

      initialize: async () => {
        set({ isLoading: true });

        try {
          // Verificar se há token salvo
          const storedToken = localStorage.getItem('token');
          const storedUser = localStorage.getItem('usuario');

          if (storedToken && storedUser) {
            try {
              const parsedUser = JSON.parse(storedUser);
              
              // Tentar validar o token fazendo uma requisição
              await authService.getProfile();
              
              set({
                token: storedToken,
                user: parsedUser,
                isAuthenticated: true,
                isLoading: false
              });
            } catch (error) {
              // Token inválido, limpar dados
              get().logout();
            }
          } else {
            set({ isLoading: false });
          }
        } catch (error) {
          console.error('Erro ao inicializar auth:', error);
          set({ isLoading: false });
        }
      },

      validateToken: async () => {
        const { token } = get();
        if (!token) {
          set({ isLoading: false });
          return;
        }

        set({ isLoading: true });
        try {
          const user = await authService.getProfile();
          set({ 
            user, 
            isAuthenticated: true,
            isLoading: false 
          });
        } catch (error) {
          console.error('Token inválido:', error);
          get().logout();
        }
      }
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        user: state.user,
        token: state.token,
        isAuthenticated: state.isAuthenticated
      })
    }
  )
);
