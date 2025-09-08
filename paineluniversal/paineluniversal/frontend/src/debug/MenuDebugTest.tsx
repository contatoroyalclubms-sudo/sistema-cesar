import React from 'react';
import { BarChart3, Calendar, ShoppingCart, UserCheck, QrCode, Users, Layers, Package, Boxes, GitMerge, FileText, Settings } from 'lucide-react';

interface MenuTestProps {
  usuario?: any;
  token?: string;
}

export function MenuDebugTest({ usuario, token }: MenuTestProps) {
  const menuItems = [
    { 
      icon: BarChart3, 
      label: 'Dashboard', 
      path: '/app/dashboard', 
      roles: ['admin', 'promoter', 'cliente'],
      description: 'Visão geral do sistema'
    },
    { 
      icon: Calendar, 
      label: 'Eventos', 
      path: '/app/eventos', 
      roles: ['admin', 'promoter'],
      description: 'Gerenciar eventos'
    },
    { 
      icon: ShoppingCart, 
      label: 'Vendas', 
      path: '/app/vendas', 
      roles: ['admin', 'promoter', 'cliente'],
      description: 'Sistema de vendas'
    },
    { 
      icon: UserCheck, 
      label: 'Check-in Inteligente', 
      path: '/app/checkin', 
      roles: ['admin', 'promoter', 'cliente'],
      description: 'Check-in de participantes'
    },
    { 
      icon: QrCode, 
      label: 'Check-in Mobile', 
      path: '/app/checkin-mobile', 
      roles: ['admin', 'promoter', 'cliente'],
      description: 'Check-in via QR Code'
    },
    { 
      icon: ShoppingCart, 
      label: 'PDV', 
      path: '/app/pdv', 
      roles: ['admin', 'operador'],
      description: 'Ponto de Venda'
    },
    { 
      icon: Users, 
      label: 'Listas & Convidados', 
      path: '/app/listas', 
      roles: ['admin', 'promoter'],
      description: 'Gestão de listas'
    },
    {
      icon: Package,
      label: 'Produtos',
      path: '/app/produtos',
      roles: ['admin', 'operador'],
      hasSubmenu: true,
      description: 'Gestão de produtos'
    },
    { 
      icon: Boxes, 
      label: 'Estoque', 
      path: '/app/estoque', 
      roles: ['admin', 'operador'],
      description: 'Controle de estoque'
    },
    { 
      icon: GitMerge, 
      label: 'MEEP Integration', 
      path: '/app/meep', 
      roles: ['admin'],
      description: 'Integração MEEP'
    },
    { 
      icon: FileText, 
      label: 'Relatórios', 
      path: '/app/relatorios', 
      roles: ['admin', 'promoter'],
      description: 'Relatórios do sistema'
    },
    { 
      icon: Settings, 
      label: 'Configurações', 
      path: '/app/configuracoes', 
      roles: ['admin'],
      description: 'Configurações do sistema'
    },
  ];

  // Replicar a mesma lógica do Layout.tsx
  const filteredMenuItems = (() => {
    // Se o usuário não está carregado ou não há token, mostrar mais itens para melhor experiência
    if (!usuario || !token) {
      // Mostrar funcionalidades básicas + MEEP para demonstração
      const publicItems = [
        'Dashboard', 
        'Eventos', 
        'Vendas', 
        'Check-in Inteligente',
        'Check-in Mobile',
        'PDV', 
        'Listas & Convidados',
        'Produtos',
        'Estoque',
        'MEEP Integration',
        'Relatórios'
      ];
      return menuItems.filter(item => publicItems.includes(item.label));
    }
    
    // Se usuário está autenticado, filtrar por roles
    const userType = (() => {
      // Primeiro, tentar campo 'tipo'
      if (usuario.tipo) return usuario.tipo;
      // Fallback para 'tipo_usuario'
      if (usuario.tipo_usuario) return usuario.tipo_usuario;
      // Fallback final baseado em outras propriedades do usuário
      if (usuario.email?.includes('admin')) return 'admin';
      // Fallback padrão
      return 'promoter';
    })();
    
    console.log('🔍 MenuDebugTest: Tipo de usuário detectado:', userType, {
      tipo: usuario.tipo,
      tipo_usuario: usuario.tipo_usuario,
      usuario: usuario,
      fallbackUsed: !usuario.tipo && !usuario.tipo_usuario
    });
    
    const filtered = menuItems.filter(item => item.roles.includes(userType));
    console.log('🔍 MenuDebugTest: Items filtrados:', filtered.length, filtered.map(i => i.label));
    
    return filtered;
  })();

  return (
    <div className="p-6 bg-white border rounded-lg shadow">
      <h2 className="text-xl font-bold mb-4">🔍 Debug do Menu Lateral</h2>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Estado do Usuário */}
        <div>
          <h3 className="font-semibold mb-2">📊 Estado Atual:</h3>
          <div className="space-y-2 text-sm">
            <div>
              <strong>Token:</strong> {token ? '✅ Presente' : '❌ Ausente'}
            </div>
            <div>
              <strong>Usuário:</strong> {usuario ? '✅ Presente' : '❌ Ausente'}
            </div>
            {usuario && (
              <>
                <div>
                  <strong>ID:</strong> {usuario.id || 'N/A'}
                </div>
                <div>
                  <strong>Nome:</strong> {usuario.nome || 'N/A'}
                </div>
                <div>
                  <strong>Email:</strong> {usuario.email || 'N/A'}
                </div>
                <div>
                  <strong>Tipo:</strong> {usuario.tipo || 'N/A'}
                </div>
                <div>
                  <strong>Tipo_usuario:</strong> {usuario.tipo_usuario || 'N/A'}
                </div>
                <div>
                  <strong>Ativo:</strong> {usuario.ativo ? '✅' : '❌'}
                </div>
              </>
            )}
          </div>
        </div>

        {/* Items Filtrados */}
        <div>
          <h3 className="font-semibold mb-2">📋 Items do Menu ({filteredMenuItems.length}):</h3>
          <div className="space-y-1 text-sm max-h-64 overflow-y-auto">
            {filteredMenuItems.length === 0 ? (
              <div className="text-red-500">❌ Nenhum item filtrado - FALLBACK será usado</div>
            ) : (
              filteredMenuItems.map((item, index) => (
                <div key={index} className="flex items-center gap-2">
                  <item.icon className="h-4 w-4" />
                  <span>{item.label}</span>
                  <span className="text-gray-500 text-xs">({item.roles.join(', ')})</span>
                </div>
              ))
            )}
          </div>
        </div>
      </div>

      {/* Simulações */}
      <div className="mt-6">
        <h3 className="font-semibold mb-2">🧪 Simulações de Teste:</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* Sem usuário */}
          <div className="p-3 border rounded">
            <h4 className="font-medium">Sem Usuário</h4>
            <MenuDebugTest usuario={undefined} token={undefined} />
          </div>

          {/* Admin */}
          <div className="p-3 border rounded">
            <h4 className="font-medium">Admin</h4>
            <MenuDebugTest 
              usuario={{ 
                id: 1, 
                nome: 'Admin', 
                email: 'admin@test.com', 
                tipo: 'admin',
                tipo_usuario: 'admin',
                ativo: true 
              }} 
              token="fake-token" 
            />
          </div>

          {/* Promoter */}
          <div className="p-3 border rounded">
            <h4 className="font-medium">Promoter</h4>
            <MenuDebugTest 
              usuario={{ 
                id: 2, 
                nome: 'Promoter', 
                email: 'promoter@test.com', 
                tipo: 'promoter',
                tipo_usuario: 'promoter',
                ativo: true 
              }} 
              token="fake-token" 
            />
          </div>
        </div>
      </div>
    </div>
  );
}

export default MenuDebugTest;
