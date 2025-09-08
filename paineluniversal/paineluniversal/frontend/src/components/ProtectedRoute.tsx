import React, { useEffect, useState } from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

interface ProtectedRouteProps {
  children: React.ReactNode;
  requiredRoles?: string[];
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ 
  children, 
  requiredRoles = [] 
}) => {
  const { isAuthenticated, usuario, loading, revalidateUser } = useAuth();
  const [userLoadTimeout, setUserLoadTimeout] = useState(false);

  // Timeout para evitar loading infinito
  useEffect(() => {
    if (isAuthenticated && !usuario && requiredRoles.length > 0) {
      // Tentar revalidar usuário
      revalidateUser();
      
      // Timeout de 10 segundos para evitar loading infinito
      const timeout = setTimeout(() => {
        console.warn('⚠️ ProtectedRoute: Timeout ao carregar dados do usuário');
        setUserLoadTimeout(true);
      }, 10000);

      return () => clearTimeout(timeout);
    }
  }, [isAuthenticated, usuario, requiredRoles.length, revalidateUser]);

  // Loading inicial do AuthContext
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Verificando autenticação...</p>
        </div>
      </div>
    );
  }

  // Não autenticado
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  // Usuário sem permissões adequadas
  if (requiredRoles.length > 0 && usuario && !requiredRoles.includes(usuario.tipo)) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-gray-900 mb-2">Acesso Negado</h1>
          <p className="text-gray-600">Você não tem permissão para acessar esta página.</p>
          <p className="text-sm text-gray-500 mt-2">
            Seu perfil: {usuario.tipo} | Requerido: {requiredRoles.join(', ')}
          </p>
        </div>
      </div>
    );
  }

  // Loading de dados do usuário com timeout
  if (requiredRoles.length > 0 && !usuario && isAuthenticated && !userLoadTimeout) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Carregando dados do usuário...</p>
        </div>
      </div>
    );
  }

  // Se houve timeout ou não há roles requeridas, permitir acesso
  // (componentes internos devem tratar a ausência de dados do usuário)
  if (userLoadTimeout && requiredRoles.length > 0) {
    console.warn('⚠️ ProtectedRoute: Permitindo acesso após timeout - dados do usuário podem estar indisponíveis');
  }

  return <>{children}</>;
};

export default ProtectedRoute;
