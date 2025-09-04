// Debug script para identificar problema no menu lateral
console.log('🔍 DEBUG: Iniciando análise do menu lateral...');

// Verificar estado do usuário no localStorage
const token = localStorage.getItem('token');
const storedUsuario = localStorage.getItem('usuario');

console.log('📋 Estado do localStorage:', {
  hasToken: !!token,
  tokenLength: token?.length,
  hasUsuario: !!storedUsuario,
  usuarioType: typeof storedUsuario,
  usuarioContent: storedUsuario
});

// Tentar fazer parse do usuário
let parsedUsuario = null;
if (storedUsuario && storedUsuario !== 'undefined' && storedUsuario !== 'null') {
  try {
    parsedUsuario = JSON.parse(storedUsuario);
    console.log('✅ Usuário parseado com sucesso:', {
      id: parsedUsuario?.id,
      nome: parsedUsuario?.nome,
      tipo: parsedUsuario?.tipo,
      tipo_usuario: parsedUsuario?.tipo_usuario,
      keys: Object.keys(parsedUsuario || {})
    });
  } catch (error) {
    console.error('❌ Erro ao fazer parse do usuário:', error);
  }
}

// Simular lógica do filteredMenuItems
const menuItems = [
  { label: 'Dashboard', roles: ['admin', 'promoter', 'cliente'] },
  { label: 'Eventos', roles: ['admin', 'promoter'] },
  { label: 'Vendas', roles: ['admin', 'promoter', 'cliente'] },
  { label: 'Check-in Inteligente', roles: ['admin', 'promoter', 'cliente'] },
  { label: 'Check-in Mobile', roles: ['admin', 'promoter', 'cliente'] },
  { label: 'PDV', roles: ['admin', 'promoter'] },
  { label: 'Listas & Convidados', roles: ['admin', 'promoter'] },
  { label: 'Produtos', roles: ['admin', 'promoter'] },
  { label: 'Estoque', roles: ['admin'] },
  { label: 'Financeiro', roles: ['admin'] },
  { label: 'MEEP Integration', roles: ['admin'] },
  { label: 'Relatórios', roles: ['admin', 'promoter'] },
  { label: 'Cadastros', roles: ['admin'] },
  { label: 'Configurações', roles: ['admin'] }
];

console.log('📋 Total de menu items disponíveis:', menuItems.length);

// Simular lógica do Layout.tsx
const loading = false; // Assumindo que não está carregando

console.log('🧪 Testando condições do filteredMenuItems...');

// Condição 1: Usuário não está definido e não está carregando e não tem token
if (!parsedUsuario && !loading && !localStorage.getItem('token')) {
  console.log('❌ CONDIÇÃO 1: Usuário não autenticado (sem token)');
  const publicItems = [
    'Dashboard', 'Eventos', 'Vendas', 'Check-in Inteligente',
    'Check-in Mobile', 'PDV', 'Listas & Convidados', 'Produtos',
    'Estoque', 'MEEP Integration', 'Relatórios'
  ];
  const filtered = menuItems.filter(item => publicItems.includes(item.label));
  console.log('📋 Items públicos:', filtered.map(item => item.label));
}
// Condição 2: Usuário não está definido mas tem token
else if (!parsedUsuario && !loading && localStorage.getItem('token')) {
  console.log('⚠️ CONDIÇÃO 2: Token existe mas usuário não carregado');
  console.log('🔍 Esta pode ser a causa do problema!');
}
// Condição 3: Usuário está definido
else if (parsedUsuario) {
  console.log('✅ CONDIÇÃO 3: Usuário autenticado');
  
  // Detectar tipo do usuário
  const userType = (() => {
    if (parsedUsuario?.tipo) return parsedUsuario.tipo.toLowerCase().trim();
    if (parsedUsuario?.tipo_usuario) return parsedUsuario.tipo_usuario.toLowerCase().trim();
    if (parsedUsuario?.email?.includes('admin')) return 'admin';
    return 'cliente';
  })();
  
  console.log('👤 Tipo de usuário detectado:', userType);
  
  // Filtrar por roles
  const filtered = menuItems.filter(item => {
    if (!item.roles || item.roles.length === 0) return true;
    return item.roles.includes(userType);
  });
  
  console.log('📋 Items filtrados por role:', filtered.map(item => item.label));
  console.log('📊 Total de items visíveis:', filtered.length);
  
  // Verificar se caiu no fallback
  if (filtered.length === 0) {
    console.log('⚠️ FALLBACK ATIVADO: Nenhum item passou no filtro');
    const basicItemsForAuth = ['Dashboard', 'Eventos', 'Vendas', 'Check-in Inteligente', 'Check-in Mobile', 'PDV', 'Listas & Convidados'];
    const fallbackItems = menuItems.filter(item => basicItemsForAuth.includes(item.label));
    console.log('📋 Items do fallback:', fallbackItems.map(item => item.label));
  }
}

console.log('🔍 DEBUG: Análise concluída. Verifique os logs acima para identificar o problema.');
