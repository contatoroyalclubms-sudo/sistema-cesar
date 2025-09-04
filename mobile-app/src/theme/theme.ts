import { MD3DarkTheme } from 'react-native-paper';
import { DefaultTheme } from '@react-navigation/native';

// Paleta de cores otimizada para uso noturno
export const colors = {
  // Cores principais
  primary: '#3b82f6',        // Azul confiável
  secondary: '#ec4899',      // Rosa neon destaque
  success: '#10b981',        // Verde confirmação
  warning: '#f59e0b',        // Laranja alerta
  danger: '#ef4444',         // Vermelho erro
  
  // Backgrounds
  background: '#1f2937',     // Fundo principal escuro
  surface: '#374151',        // Cards e superfícies
  surfaceVariant: '#4b5563', // Variação de superfície
  
  // Textos
  onSurface: '#f9fafb',      // Texto principal (branco)
  onSurfaceVariant: '#d1d5db', // Texto secundário
  onPrimary: '#ffffff',      // Texto em botões primários
  
  // Estados
  disabled: '#6b7280',       // Elementos desabilitados
  outline: '#9ca3af',        // Bordas
  
  // Categorias (para produtos)
  bebidas: '#3b82f6',
  drinks: '#ec4899',
  petiscos: '#f59e0b',
  pratos: '#10b981',
  narguile: '#8b5cf6',
  sobremesas: '#f43f5e',
  especiais: '#6366f1',
  promocoes: '#ef4444',
  
  // Estados NFC
  nfcActive: '#10b981',
  nfcReading: '#f59e0b',
  nfcError: '#ef4444',
  
  // Transparências
  overlay: 'rgba(0, 0, 0, 0.7)',
  ripple: 'rgba(255, 255, 255, 0.1)',
};

// Tema React Native Paper customizado
export const theme = {
  ...MD3DarkTheme,
  colors: {
    ...MD3DarkTheme.colors,
    primary: colors.primary,
    secondary: colors.secondary,
    background: colors.background,
    surface: colors.surface,
    surfaceVariant: colors.surfaceVariant,
    onSurface: colors.onSurface,
    onSurfaceVariant: colors.onSurfaceVariant,
    onPrimary: colors.onPrimary,
    outline: colors.outline,
    error: colors.danger,
    onError: colors.onPrimary,
  },
  fonts: {
    ...MD3DarkTheme.fonts,
    // Fontes otimizadas para touch
    displayLarge: {
      fontSize: 32,
      fontWeight: '800',
      lineHeight: 40,
    },
    displayMedium: {
      fontSize: 28,
      fontWeight: '700',
      lineHeight: 36,
    },
    headlineLarge: {
      fontSize: 24,
      fontWeight: '700',
      lineHeight: 32,
    },
    headlineMedium: {
      fontSize: 20,
      fontWeight: '600',
      lineHeight: 28,
    },
    titleLarge: {
      fontSize: 18,
      fontWeight: '600',
      lineHeight: 24,
    },
    titleMedium: {
      fontSize: 16,
      fontWeight: '600',
      lineHeight: 24,
    },
    labelLarge: {
      fontSize: 16,
      fontWeight: '600',
      lineHeight: 20,
    },
    bodyLarge: {
      fontSize: 16,
      fontWeight: '400',
      lineHeight: 24,
    },
    bodyMedium: {
      fontSize: 14,
      fontWeight: '400',
      lineHeight: 20,
    },
  },
};

// Tema para React Navigation
export const navigationTheme = {
  ...DefaultTheme,
  dark: true,
  colors: {
    ...DefaultTheme.colors,
    primary: colors.primary,
    background: colors.background,
    card: colors.surface,
    text: colors.onSurface,
    border: colors.outline,
    notification: colors.danger,
  },
};

// Estilos comuns
export const commonStyles = {
  // Containers
  container: {
    flex: 1,
    backgroundColor: colors.background,
  },
  centerContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: colors.background,
  },
  
  // Cards
  card: {
    backgroundColor: colors.surface,
    borderRadius: 12,
    padding: 16,
    marginVertical: 8,
    elevation: 2,
  },
  
  // Botões otimizados para touch
  primaryButton: {
    backgroundColor: colors.primary,
    borderRadius: 12,
    paddingVertical: 16,
    paddingHorizontal: 24,
    minHeight: 48,
    justifyContent: 'center',
    alignItems: 'center',
  },
  
  secondaryButton: {
    backgroundColor: 'transparent',
    borderWidth: 2,
    borderColor: colors.primary,
    borderRadius: 12,
    paddingVertical: 14,
    paddingHorizontal: 24,
    minHeight: 48,
    justifyContent: 'center',
    alignItems: 'center',
  },
  
  dangerButton: {
    backgroundColor: colors.danger,
    borderRadius: 12,
    paddingVertical: 16,
    paddingHorizontal: 24,
    minHeight: 48,
    justifyContent: 'center',
    alignItems: 'center',
  },
  
  // Touch targets (mínimo 44px para acessibilidade)
  touchTarget: {
    minWidth: 44,
    minHeight: 44,
    justifyContent: 'center',
    alignItems: 'center',
  },
  
  // Grid produtos
  productGrid: {
    flex: 1,
    padding: 8,
  },
  
  productCard: {
    flex: 1,
    backgroundColor: colors.surface,
    borderRadius: 12,
    margin: 6,
    padding: 12,
    minHeight: 120,
    justifyContent: 'space-between',
    elevation: 2,
  },
  
  // Inputs
  input: {
    backgroundColor: colors.surface,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: colors.outline,
    padding: 12,
    fontSize: 16,
    color: colors.onSurface,
    minHeight: 48,
  },
  
  // Shadows
  shadowSmall: {
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 1,
    },
    shadowOpacity: 0.22,
    shadowRadius: 2.22,
    elevation: 3,
  },
  
  shadowMedium: {
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.25,
    shadowRadius: 3.84,
    elevation: 5,
  },
  
  // Loading
  loadingOverlay: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: colors.overlay,
    justifyContent: 'center',
    alignItems: 'center',
    zIndex: 1000,
  },
  
  // Estados
  successState: {
    backgroundColor: colors.success,
    borderRadius: 8,
    padding: 12,
  },
  
  errorState: {
    backgroundColor: colors.danger,
    borderRadius: 8,
    padding: 12,
  },
  
  warningState: {
    backgroundColor: colors.warning,
    borderRadius: 8,
    padding: 12,
  },
};

// Dimensões padrão
export const dimensions = {
  // Spacing
  xs: 4,
  sm: 8,
  md: 16,
  lg: 24,
  xl: 32,
  xxl: 48,
  
  // Radius
  radiusSmall: 4,
  radiusMedium: 8,
  radiusLarge: 12,
  radiusXLarge: 16,
  
  // Touch targets
  touchTargetMinSize: 44,
  buttonHeight: 48,
  
  // Grid
  gridGap: 12,
  cardPadding: 16,
  
  // Header
  headerHeight: 56,
  
  // Bottom tabs
  tabBarHeight: 64,
};

// Animações
export const animations = {
  // Durações
  fast: 150,
  normal: 300,
  slow: 500,
  
  // Easing
  easeInOut: 'ease-in-out',
  easeOut: 'ease-out',
  easeIn: 'ease-in',
  
  // Springs (para React Native Reanimated)
  springConfig: {
    damping: 15,
    mass: 1,
    stiffness: 150,
  },
};

export default theme;
