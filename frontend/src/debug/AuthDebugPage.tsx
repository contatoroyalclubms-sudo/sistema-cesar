import React from 'react';
import { useAuth } from '../contexts/AuthContext';
import MenuDebugTest from './MenuDebugTest';

export function AuthDebugPage() {
  const { usuario, isAuthenticated, loading } = useAuth();

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-6xl mx-auto">
        <h1 className="text-3xl font-bold mb-6">🔍 Debug do Sistema de Autenticação</h1>
        
        {/* Estado do AuthContext */}
        <div className="bg-white p-6 rounded-lg shadow mb-6">
          <h2 className="text-xl font-semibold mb-4">📊 Estado do AuthContext</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <strong>Loading:</strong> {loading ? '⏳ Sim' : '✅ Não'}
            </div>
            <div>
              <strong>Autenticado:</strong> {isAuthenticated ? '✅ Sim' : '❌ Não'}
            </div>
            <div>
              <strong>Token:</strong> {localStorage.getItem('token') ? '✅ Presente' : '❌ Ausente'}
            </div>
          </div>
          
          {usuario && (
            <div className="mt-4">
              <h3 className="font-semibold">👤 Dados do Usuário:</h3>
              <pre className="bg-gray-100 p-3 rounded text-sm overflow-auto">
                {JSON.stringify(usuario, null, 2)}
              </pre>
            </div>
          )}
        </div>

        {/* LocalStorage Debug */}
        <div className="bg-white p-6 rounded-lg shadow mb-6">
          <h2 className="text-xl font-semibold mb-4">💾 LocalStorage Debug</h2>
          <div className="space-y-2">
            <div>
              <strong>Token:</strong>
              <pre className="bg-gray-100 p-2 rounded text-sm">
                {localStorage.getItem('token') || 'null'}
              </pre>
            </div>
            <div>
              <strong>Usuario:</strong>
              <pre className="bg-gray-100 p-2 rounded text-sm">
                {localStorage.getItem('usuario') || 'null'}
              </pre>
            </div>
          </div>
        </div>

        {/* Menu Debug Component */}
        <MenuDebugTest 
          usuario={usuario} 
          token={localStorage.getItem('token') || undefined} 
        />

        {/* Ações de Debug */}
        <div className="bg-white p-6 rounded-lg shadow mt-6">
          <h2 className="text-xl font-semibold mb-4">🔧 Ações de Debug</h2>
          <div className="space-x-4">
            <button
              onClick={() => {
                console.log('🔍 AuthContext State:', { usuario, isAuthenticated, loading });
                console.log('🔍 LocalStorage:', {
                  token: localStorage.getItem('token'),
                  usuario: localStorage.getItem('usuario')
                });
              }}
              className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
            >
              Log no Console
            </button>
            
            <button
              onClick={() => {
                localStorage.removeItem('token');
                localStorage.removeItem('usuario');
                window.location.reload();
              }}
              className="bg-red-500 text-white px-4 py-2 rounded hover:bg-red-600"
            >
              Limpar e Recarregar
            </button>
            
            <button
              onClick={() => {
                // Simular dados de usuário admin
                const fakeAdmin = {
                  id: 999,
                  nome: 'Debug Admin',
                  email: 'debug@admin.com',
                  tipo: 'admin',
                  tipo_usuario: 'admin',
                  ativo: true
                };
                localStorage.setItem('usuario', JSON.stringify(fakeAdmin));
                localStorage.setItem('token', 'fake-debug-token');
                window.location.reload();
              }}
              className="bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600"
            >
              Simular Admin
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default AuthDebugPage;
