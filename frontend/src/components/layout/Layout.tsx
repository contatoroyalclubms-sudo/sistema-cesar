import React, { useState } from 'react';
import { Outlet, Link, useNavigate, useLocation } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { useAuth } from '../../contexts/AuthContext';
import { ThemeToggle } from '../theme/ThemeToggle';
import { useToast } from '../../hooks/use-toast';
import { 
  Calendar, 
  Users, 
  Building2, 
  BarChart3, 
  FileText, 
  Settings, 
  LogOut,
  Menu,
  X,
  ShoppingCart,
  UserCheck,
  Smartphone,
  DollarSign,
  Trophy,
  ChevronDown,
  Bell,
  Search,
  Package,
  Shield,
  Zap,
  Activity,
  Database,
  Tablet,
  Star,
  MessageSquare,
  Tag,
  Cpu,
  TrendingUp,
  Globe,
  Ticket,
  UserCog,
  Briefcase,
  Link2
} from 'lucide-react';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { 
  DropdownMenu, 
  DropdownMenuContent, 
  DropdownMenuItem, 
  DropdownMenuSeparator, 
  DropdownMenuTrigger 
} from '../ui/dropdown-menu';
import { Avatar, AvatarFallback } from '../ui/avatar';
import { Badge } from '../ui/badge';

interface LayoutProps {
  children?: React.ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const { usuario, logout, revalidateUser, loading } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const { toast } = useToast();
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [expandedMenus, setExpandedMenus] = useState<Record<string, boolean>>({
    'Produtos': location.pathname.startsWith('/app/produtos'),
    'Automação': location.pathname.startsWith('/app/automacao'),
    'Business Intelligence': location.pathname.startsWith('/app/bi'),
    'Integrações': location.pathname.startsWith('/app/integracoes'),
    'Soluções Online': location.pathname.startsWith('/app/solucoes-online'),
    'Tickets e Ingressos': location.pathname.startsWith('/app/tickets'),
    'Colaboradores': location.pathname.startsWith('/app/colaboradores'),
    'MEEP Integration': location.pathname.startsWith('/app/meep'),
    'Cadastros': location.pathname.startsWith('/app/cadastros')
  });

  // Revalidar usuário se necessário
  React.useEffect(() => {
    // Se há token mas não há usuário, tentar revalidar
    if (!usuario && localStorage.getItem('token')) {
      revalidateUser();
    }
  }, [usuario, revalidateUser]);

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const handleNotifications = () => {
    toast({
      title: "Notificações",
      description: "Você tem 3 notificações não lidas",
      duration: 3000,
    });
    // TODO: Implementar painel de notificações
  };

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (!searchTerm.trim()) return;
    
    toast({
      title: "Busca",
      description: `Buscando por: ${searchTerm}`,
      duration: 2000,
    });
    // TODO: Implementar funcionalidade de busca global
  };

  // Auto-expandir menus quando navegar para suas seções
  React.useEffect(() => {
    const pathMappings = {
      '/app/produtos': 'Produtos',
      '/app/automacao': 'Automação',
      '/app/bi': 'Business Intelligence',
      '/app/integracoes': 'Integrações',
      '/app/solucoes-online': 'Soluções Online',
      '/app/tickets': 'Tickets e Ingressos',
      '/app/colaboradores': 'Colaboradores',
      '/app/meep': 'MEEP Integration',
      '/app/cadastros': 'Cadastros'
    };

    const expandedMenu = Object.entries(pathMappings).find(([path]) => 
      location.pathname.startsWith(path)
    );

    if (expandedMenu) {
      setExpandedMenus(prev => ({
        ...prev,
        [expandedMenu[1]]: true
      }));
    }
  }, [location.pathname]);

  const toggleSubmenu = (menuLabel: string) => {
    setExpandedMenus(prev => ({
      ...prev,
      [menuLabel]: !prev[menuLabel]
    }));
  };

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
      icon: Smartphone, 
      label: 'Check-in Mobile', 
      path: '/app/mobile-checkin', 
      roles: ['admin', 'promoter', 'cliente'],
      description: 'Check-in via dispositivos móveis'
    },
    { 
      icon: ShoppingCart, 
      label: 'PDV', 
      path: '/app/pdv', 
      roles: ['admin', 'promoter'],
      description: 'Ponto de venda'
    },
    { 
      icon: Users, 
      label: 'Listas & Convidados', 
      path: '/app/listas', 
      roles: ['admin', 'promoter'],
      description: 'Gerenciar listas de convidados'
    },
    { 
      icon: Package, 
      label: 'Produtos', 
      path: '/app/produtos', 
      roles: ['admin', 'promoter'],
      description: 'Gestão completa de produtos',
      hasSubmenu: true,
      submenu: [
        { label: 'Produtos', path: '/app/produtos', description: 'Gestão completa de produtos' },
        { label: 'Categorias', path: '/app/produtos/categorias', description: 'Gestão de categorias de produtos' },
        { label: 'Agendamento', path: '/app/produtos/agendamento', description: 'Agendamento automático de produtos' },
        { label: 'Import/Export', path: '/app/produtos/importexport', description: 'Importar e exportar dados em massa' },
        { label: 'Lista', path: '/app/produtos/lista', description: 'Listas de produtos personalizadas' },
        { label: 'Limitar Acesso', path: '/app/produtos/acesso', description: 'Controle de acesso por função' },
        { label: 'Produtos Ignorados', path: '/app/produtos/ignorados', description: 'Produtos desabilitados' }
      ]
    },
    { 
      icon: Package, 
      label: 'Estoque', 
      path: '/app/estoque', 
      roles: ['admin', 'promoter'],
      description: 'Controle de estoque e inventário'
    },
    { 
      icon: DollarSign, 
      label: 'Caixa & Financeiro', 
      path: '/app/financeiro', 
      roles: ['admin', 'promoter'],
      description: 'Controle financeiro'
    },
    { 
      icon: Trophy, 
      label: 'Ranking & Gamificação', 
      path: '/app/ranking', 
      roles: ['admin', 'promoter'],
      description: 'Sistema de pontuação'
    },
    // === MÓDULOS MEEP ===
    { 
      icon: Shield, 
      label: 'MEEP Integration', 
      path: '/app/meep', 
      roles: ['admin', 'promoter'],
      description: 'Monitoramento, Eventos, Engajamento e Performance',
      hasSubmenu: true,
      submenu: [
        { label: 'Dashboard MEEP', path: '/app/meep/dashboard', description: 'Painel principal MEEP' },
        { label: 'Analytics Avançado', path: '/app/meep/analytics', description: 'Analytics com IA e insights' },
        { label: 'Validação CPF', path: '/app/meep/validacao-cpf', description: 'Validação CPF com Receita Federal' },
        { label: 'Equipamentos', path: '/app/meep/equipamentos', description: 'Gestão de equipamentos do evento' }
      ]
    },
    { 
      icon: Users, 
      label: 'Usuários', 
      path: '/app/usuarios', 
      roles: ['admin'],
      description: 'Gerenciar usuários do sistema'
    },
    { 
      icon: Building2, 
      label: 'Empresas', 
      path: '/app/empresas', 
      roles: ['admin'],
      description: 'Gerenciar empresas'
    },
    { 
      icon: FileText, 
      label: 'Relatórios', 
      path: '/app/relatorios', 
      roles: ['admin', 'promoter'],
      description: 'Relatórios e análises'
    },
    { 
      icon: Database, 
      label: 'Cadastros', 
      path: '/app/cadastros', 
      roles: ['admin', 'promoter'],
      description: 'Gestão de cadastros',
      hasSubmenu: true,
      submenu: [
        { 
          path: '/app/cadastros/clientes', 
          label: 'Clientes', 
          description: 'Gestão de clientes' 
        },
        { 
          path: '/app/cadastros/operadores', 
          label: 'Operadores', 
          description: 'Gestão de operadores' 
        },
        { 
          path: '/app/cadastros/promocoes', 
          label: 'Promoções', 
          description: 'Gestão de promoções' 
        },
        { 
          path: '/app/cadastros/planos', 
          label: 'Planos', 
          description: 'Gestão de planos' 
        },
        { 
          path: '/app/cadastros/comandas', 
          label: 'Comandas', 
          description: 'Gestão de comandas' 
        },
        { 
          path: '/app/cadastros/impressoras', 
          label: 'Impressoras', 
          description: 'Gestão de impressoras' 
        },
        { 
          path: '/app/cadastros/formas-pagamento', 
          label: 'Formas de Pagamento', 
          description: 'Gestão de formas de pagamento' 
        },
        { 
          path: '/app/cadastros/lojas', 
          label: 'Lojas', 
          description: 'Gestão de lojas' 
        },
        { 
          path: '/app/cadastros/link-pagamento', 
          label: 'Link de Pagamento', 
          description: 'Gestão de links de pagamento' 
        }
      ]
    },
    // === NOVOS MÓDULOS IMPLEMENTADOS ===
    { 
      icon: Tag, 
      label: 'Categorias de Clientes', 
      path: '/app/categorias-clientes', 
      roles: ['admin', 'promoter'],
      description: 'Gestão de categorias e segmentação de clientes'
    },
    { 
      icon: MessageSquare, 
      label: 'Pesquisa de Satisfação', 
      path: '/app/pesquisa-satisfacao', 
      roles: ['admin', 'promoter'],
      description: 'Pesquisas de satisfação e NPS'
    },
    { 
      icon: Star, 
      label: 'Programa de Fidelidade', 
      path: '/app/fidelidade', 
      roles: ['admin', 'promoter', 'cliente'],
      description: 'Sistema de pontos e recompensas'
    },
    { 
      icon: Cpu, 
      label: 'Automação', 
      path: '/app/automacao', 
      roles: ['admin', 'promoter'],
      description: 'Automação de processos e fluxos de trabalho',
      hasSubmenu: true,
      submenu: [
        { label: 'Automações', path: '/app/automacao', description: 'Gestão de automações' },
        { label: 'Fluxos de Trabalho', path: '/app/automacao/fluxos', description: 'Fluxos e processos' },
        { label: 'Logs de Execução', path: '/app/automacao/logs', description: 'Histórico de execuções' }
      ]
    },
    { 
      icon: TrendingUp, 
      label: 'Business Intelligence', 
      path: '/app/bi', 
      roles: ['admin', 'promoter'],
      description: 'Dashboards e análise de dados',
      hasSubmenu: true,
      submenu: [
        { label: 'Dashboards', path: '/app/bi/dashboards', description: 'Painéis customizados' },
        { label: 'Relatórios BI', path: '/app/bi/relatorios', description: 'Relatórios avançados' },
        { label: 'Análise Preditiva', path: '/app/bi/preditiva', description: 'Previsões com IA' },
        { label: 'Métricas em Tempo Real', path: '/app/bi/tempo-real', description: 'KPIs ao vivo' }
      ]
    },
    { 
      icon: Link2, 
      label: 'Integrações', 
      path: '/app/integracoes', 
      roles: ['admin'],
      description: 'Integrações com sistemas externos',
      hasSubmenu: true,
      submenu: [
        { label: 'Integrações Ativas', path: '/app/integracoes', description: 'Gerenciar integrações' },
        { label: 'Marketplace', path: '/app/integracoes/marketplace', description: 'Novas integrações' },
        { label: 'Webhooks', path: '/app/integracoes/webhooks', description: 'Gestão de webhooks' },
        { label: 'Logs', path: '/app/integracoes/logs', description: 'Histórico de integrações' }
      ]
    },
    { 
      icon: Globe, 
      label: 'Soluções Online', 
      path: '/app/solucoes-online', 
      roles: ['admin', 'promoter'],
      description: 'Apps e configurações online',
      hasSubmenu: true,
      submenu: [
        { label: 'Configuração de Apps', path: '/app/solucoes-online/apps', description: 'Configurar aplicativos' },
        { label: 'PWA Manager', path: '/app/solucoes-online/pwa', description: 'Progressive Web Apps' },
        { label: 'Recursos', path: '/app/solucoes-online/recursos', description: 'Biblioteca de recursos' },
        { label: 'Templates', path: '/app/solucoes-online/templates', description: 'Templates prontos' }
      ]
    },
    { 
      icon: Ticket, 
      label: 'Tickets e Ingressos', 
      path: '/app/tickets', 
      roles: ['admin', 'promoter', 'cliente'],
      description: 'Sistema completo de ingressos',
      hasSubmenu: true,
      submenu: [
        { label: 'Tipos de Ticket', path: '/app/tickets/tipos', description: 'Configurar tipos' },
        { label: 'Lotes', path: '/app/tickets/lotes', description: 'Gestão de lotes' },
        { label: 'Vendas', path: '/app/tickets/vendas', description: 'Venda de ingressos' },
        { label: 'Validação', path: '/app/tickets/validacao', description: 'Validar ingressos' },
        { label: 'Transferências', path: '/app/tickets/transferencias', description: 'Transferir ingressos' },
        { label: 'Relatórios', path: '/app/tickets/relatorios', description: 'Relatórios de vendas' }
      ]
    },
    { 
      icon: UserCog, 
      label: 'Colaboradores', 
      path: '/app/colaboradores', 
      roles: ['admin', 'promoter'],
      description: 'Gestão de equipe e RH',
      hasSubmenu: true,
      submenu: [
        { label: 'Colaboradores', path: '/app/colaboradores', description: 'Listar colaboradores' },
        { label: 'Cargos', path: '/app/colaboradores/cargos', description: 'Gestão de cargos' },
        { label: 'Escalas', path: '/app/colaboradores/escalas', description: 'Escalas de trabalho' },
        { label: 'Tarefas', path: '/app/colaboradores/tarefas', description: 'Atribuir tarefas' },
        { label: 'Ponto', path: '/app/colaboradores/ponto', description: 'Controle de ponto' },
        { label: 'Relatórios RH', path: '/app/colaboradores/relatorios', description: 'Relatórios de RH' }
      ]
    },
    { 
      icon: Settings, 
      label: 'Configurações', 
      path: '/app/configuracoes', 
      roles: ['admin'],
      description: 'Configurações do sistema'
    },
  ];

  const filteredMenuItems = (() => {
    // 🔧 CORREÇÃO CRÍTICA: Priorizar verificação do token sobre estado do usuário
    const hasToken = !!localStorage.getItem('token');
    
    console.log('🔍 Layout: Estado de autenticação:', {
      hasToken,
      hasUsuario: !!usuario,
      loading,
      userType: usuario?.tipo || usuario?.tipo_usuario || 'não detectado'
    });
    
    // Se está carregando, mostrar loading state
    if (loading && hasToken) {
      console.log('⏳ Layout: Carregando dados do usuário...');
      return []; // Mostra loading enquanto carrega
    }
    
    // Se não tem token, é definitivamente usuário não autenticado
    if (!hasToken) {
      console.log('👤 Layout: Usuário não autenticado (sem token)');
      // Mostrar apenas funcionalidades básicas para demonstração
      const publicItems = [
        'Dashboard', 
        'Eventos', 
        'Vendas', 
        'Check-in Mobile'
      ];
      return menuItems.filter(item => publicItems.includes(item.label));
    }
    
    // 🔧 CORREÇÃO CRÍTICA: Se tem token, tratar como usuário autenticado
    // mesmo que os dados do usuário ainda não tenham carregado completamente
    if (hasToken) {
      // Detectar tipo do usuário de forma robusta
      const userType = (() => {
        // Se temos dados do usuário, usar eles
        if (usuario?.tipo) return usuario.tipo.toLowerCase().trim();
        if (usuario?.tipo_usuario) return usuario.tipo_usuario.toLowerCase().trim();
        if (usuario?.email?.includes('admin')) return 'admin';
        
        // 🔧 FALLBACK INTELIGENTE: Se tem token mas não tem dados do usuário ainda,
        // usar dados do localStorage temporariamente
        try {
          const storedUsuario = localStorage.getItem('usuario');
          if (storedUsuario && storedUsuario !== 'undefined' && storedUsuario !== 'null') {
            const parsedUsuario = JSON.parse(storedUsuario);
            if (parsedUsuario?.tipo) return parsedUsuario.tipo.toLowerCase().trim();
            if (parsedUsuario?.tipo_usuario) return parsedUsuario.tipo_usuario.toLowerCase().trim();
          }
        } catch (error) {
          console.warn('⚠️ Layout: Erro ao acessar dados do localStorage:', error);
        }
        
        // Fallback final: se tem token, assumir pelo menos cliente
        console.log('⚠️ Layout: Tipo de usuário não detectado, usando fallback cliente para usuário com token');
        return 'cliente';
      })();
      
      console.log('🔍 Layout: Tipo de usuário detectado:', userType, {
        fonte: usuario ? 'AuthContext' : 'localStorage fallback',
        tipo: usuario?.tipo,
        tipo_usuario: usuario?.tipo_usuario
      });
      
      // Filtrar menu por roles
      const filtered = menuItems.filter(item => {
        if (!item.roles || item.roles.length === 0) return true; // Items sem restrição
        return item.roles.includes(userType);
      });
      
      console.log('🔍 Layout: Filtro aplicado:', { 
        userType, 
        filteredCount: filtered.length,
        totalMenuItems: menuItems.length,
        filteredItems: filtered.map(item => item.label)
      });
      
      // 🔧 SEGURANÇA: Se filtro resulta em poucos items, garantir pelo menos itens básicos
      if (filtered.length < 5) {
        console.log('⚠️ Layout: Filtro resultou em poucos items, aplicando fallback expandido');
        const expandedItems = ['Dashboard', 'Eventos', 'Vendas', 'Check-in Inteligente', 'Check-in Mobile', 'PDV', 'Listas & Convidados'];
        const fallbackFiltered = menuItems.filter(item => 
          expandedItems.includes(item.label) || 
          !item.roles || 
          item.roles.length === 0 ||
          item.roles.includes(userType)
        );
        return fallbackFiltered;
      }
      
      return filtered;
    }
    
    // Fallback final (não deveria chegar aqui)
    console.warn('⚠️ Layout: Fallback final ativado - condição inesperada');
    return menuItems.filter(item => ['Dashboard', 'Eventos'].includes(item.label));
  })();

  const getInitials = (name: string) => {
    return name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2);
  };

  return (
    <div className="min-h-screen bg-background flex">
      {/* Mobile sidebar backdrop */}
      <AnimatePresence>
        {sidebarOpen && (
          <motion.div 
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-40 bg-black/50 backdrop-blur-sm lg:hidden"
            onClick={() => setSidebarOpen(false)}
          />
        )}
      </AnimatePresence>

      <div className="w-full flex min-h-screen">
        {/* Sidebar */}
        <aside 
          className={`
            ${sidebarCollapsed ? 'w-20' : 'w-70'} 
            bg-sidebar border-r border-sidebar-border shadow-lg
            transition-all duration-300 ease-in-out 
            flex flex-col shrink-0
            fixed inset-y-0 left-0 z-50 transform
            ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'}
            lg:translate-x-0 lg:relative lg:z-auto
          `}
        >
        {/* Header */}
        <div className="flex items-center justify-between h-16 px-6 border-b border-sidebar-border">
          {!sidebarCollapsed && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="flex items-center space-x-2"
            >
              <div className="w-8 h-8 bg-gradient-to-br from-primary to-primary/80 rounded-lg flex items-center justify-center">
                <Calendar className="h-4 w-4 text-primary-foreground" />
              </div>
              <div>
                <h1 className="text-lg font-heading font-bold text-sidebar-foreground">
                  Sistema Universal
                </h1>
                <p className="text-xs text-sidebar-foreground/60">
                  de Eventos
                </p>
              </div>
            </motion.div>
          )}
          
          <div className="flex items-center space-x-2">
            {!sidebarCollapsed && (
              <button
                onClick={() => setSidebarOpen(false)}
                className="lg:hidden p-2 rounded-md text-sidebar-foreground/60 hover:text-sidebar-foreground hover:bg-sidebar-accent transition-colors"
              >
                <X className="h-5 w-5" />
              </button>
            )}
            
            <button
              onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
              className="hidden lg:flex p-2 rounded-md text-sidebar-foreground/60 hover:text-sidebar-foreground hover:bg-sidebar-accent transition-colors"
            >
              <Menu className="h-4 w-4" />
            </button>
          </div>
        </div>

        {/* Navigation */}
        <nav className="flex-1 px-4 py-6 overflow-y-auto">
          <div className="space-y-2">
            {/* 🔧 CORREÇÃO: Usar filteredMenuItems sempre, sem fallback limitado */}
            {filteredMenuItems.map((item) => {
              const isActive = item.hasSubmenu 
                ? location.pathname.startsWith(item.path)
                : location.pathname === item.path;
              const isExpanded = expandedMenus[item.label];
              
              return (
                <div key={item.path}>
                  <motion.div
                    whileHover={{ x: 2 }}
                    whileTap={{ scale: 0.98 }}
                  >
                    <Link
                      to={item.hasSubmenu ? '#' : item.path}
                      className={`
                        group flex items-center justify-between px-3 py-3 text-sm font-medium rounded-lg transition-all duration-200 relative overflow-hidden
                        ${isActive 
                          ? 'bg-sidebar-primary text-sidebar-primary-foreground shadow-premium-md' 
                          : 'text-sidebar-foreground hover:bg-sidebar-accent hover:text-sidebar-accent-foreground'
                        }
                      `}
                      onClick={(e) => {
                        if (item.hasSubmenu) {
                          e.preventDefault();
                          toggleSubmenu(item.label);
                          if (!isExpanded) {
                            // Apenas expande o menu
                          } else {
                            // Se já está expandido, navega para a página principal
                            navigate(item.path);
                          }
                        }
                        setSidebarOpen(false);
                      }}
                      title={sidebarCollapsed ? item.label : undefined}
                    >
                      {isActive && (
                        <motion.div
                          className="absolute inset-0 bg-gradient-to-r from-primary to-primary/80"
                          layoutId="activeTab"
                          initial={false}
                          transition={{
                            type: "spring",
                            stiffness: 500,
                            damping: 30
                          }}
                        />
                      )}
                      
                      <div className="relative z-10 flex items-center flex-1">
                        <item.icon className={`
                          ${sidebarCollapsed ? 'mx-auto' : 'mr-3'} h-5 w-5 transition-colors
                          ${isActive ? 'text-sidebar-primary-foreground' : 'group-hover:text-primary'}
                        `} />
                        
                        {!sidebarCollapsed && (
                          <motion.div
                            initial={{ opacity: 0, x: -10 }}
                            animate={{ opacity: 1, x: 0 }}
                            className="flex-1 min-w-0"
                          >
                            <div className="truncate">{item.label}</div>
                            {!isActive && (
                              <div className="text-xs opacity-60 truncate mt-0.5">
                                {item.description}
                              </div>
                            )}
                          </motion.div>
                        )}
                      </div>
                      
                      {item.hasSubmenu && !sidebarCollapsed && (
                        <motion.div
                          animate={{ rotate: isExpanded ? 180 : 0 }}
                          transition={{ duration: 0.2 }}
                          className="relative z-10"
                        >
                          <ChevronDown className={`h-4 w-4 transition-colors ${
                            isActive ? 'text-sidebar-primary-foreground' : 'text-sidebar-foreground/60'
                          }`} />
                        </motion.div>
                      )}
                    </Link>
                  </motion.div>
                  
                  {/* Submenu */}
                  {item.hasSubmenu && isExpanded && !sidebarCollapsed && (
                    <motion.div
                      initial={{ opacity: 0, height: 0 }}
                      animate={{ opacity: 1, height: 'auto' }}
                      exit={{ opacity: 0, height: 0 }}
                      transition={{ duration: 0.2 }}
                      className="ml-4 mt-1 space-y-1 bg-sidebar-accent/30 rounded-lg p-2"
                    >
                      {item.submenu?.map((subItem) => {
                        const isSubActive = location.pathname === subItem.path;
                        return (
                          <Link
                            key={subItem.path}
                            to={subItem.path}
                            className={`
                              block py-2 px-3 text-sm rounded-md transition-colors
                              ${isSubActive
                                ? 'bg-sidebar-primary text-sidebar-primary-foreground font-medium'
                                : 'text-sidebar-foreground/80 hover:bg-sidebar-accent hover:text-sidebar-foreground'
                              }
                            `}
                            onClick={() => setSidebarOpen(false)}
                          >
                            <div className="truncate">{subItem.label}</div>
                            <div className="text-xs opacity-60 truncate mt-0.5">
                              {subItem.description}
                            </div>
                          </Link>
                        );
                      })}
                    </motion.div>
                  )}
                </div>
              );
            })}
          </div>
        </nav>

        {/* User Profile */}
        {!sidebarCollapsed && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="p-4 border-t border-sidebar-border"
          >
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <button className="flex items-center w-full p-3 text-sm bg-sidebar-accent rounded-lg hover:bg-sidebar-accent/80 transition-colors group">
                  <Avatar className="h-8 w-8 mr-3">
                    <AvatarFallback className="bg-primary text-primary-foreground text-xs">
                      {getInitials(usuario?.nome || '')}
                    </AvatarFallback>
                  </Avatar>
                  
                  <div className="flex-1 min-w-0 text-left">
                    <p className="text-sm font-medium text-sidebar-foreground truncate">
                      {usuario?.nome}
                    </p>
                    <div className="flex items-center space-x-2">
                      <Badge variant="secondary" className="text-xs px-1.5 py-0.5">
                        {usuario?.tipo}
                      </Badge>
                    </div>
                  </div>
                  
                  <ChevronDown className="h-4 w-4 text-sidebar-foreground/60 group-hover:text-sidebar-foreground transition-colors" />
                </button>
              </DropdownMenuTrigger>
              
              <DropdownMenuContent align="end" className="w-56">
                <div className="px-2 py-1.5">
                  <p className="text-sm text-muted-foreground">
                    {usuario?.email}
                  </p>
                  <p className="text-xs text-muted-foreground">
                    Sistema Universal de Eventos
                  </p>
                </div>
                
                <DropdownMenuSeparator />
                
                <DropdownMenuItem>
                  <Settings className="mr-2 h-4 w-4" />
                  Configurações
                </DropdownMenuItem>
                
                <DropdownMenuSeparator />
                
                <DropdownMenuItem 
                  onClick={handleLogout}
                  className="text-destructive focus:text-destructive"
                >
                  <LogOut className="mr-2 h-4 w-4" />
                  Sair
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </motion.div>
        )}
      </aside>

      {/* Main content area */}
      <div className={`flex-1 flex flex-col min-h-screen transition-all duration-300 ease-in-out`}>
        {/* Top bar */}
        <header className="sticky top-0 z-30 bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 border-b border-border">
          <div className="flex items-center justify-between h-16 px-4 sm:px-6 lg:px-8">
            <div className="flex items-center space-x-4">
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setSidebarOpen(true)}
                className="lg:hidden"
              >
                <Menu className="h-5 w-5" />
              </Button>
              
              <form onSubmit={handleSearch} className="hidden sm:flex items-center space-x-2 max-w-sm">
                <div className="relative flex-1">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                  <Input
                    placeholder="Buscar..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="pl-10 h-9 bg-muted/50 border-0 focus:bg-background"
                  />
                </div>
              </form>
            </div>
            
            <div className="flex items-center space-x-2">
              <Button 
                variant="ghost" 
                size="sm" 
                className="relative" 
                onClick={handleNotifications}
                title="Ver notificações"
              >
                <Bell className="h-5 w-5" />
                <span className="absolute -top-1 -right-1 h-4 w-4 bg-destructive text-destructive-foreground rounded-full text-xs flex items-center justify-center">
                  3
                </span>
              </Button>
              
              <ThemeToggle />
              
              <div className="hidden sm:block text-sm text-muted-foreground">
                Sistema Universal de Eventos
              </div>
            </div>
          </div>
        </header>

        {/* Page content */}
        <main className="flex-1 overflow-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3, ease: "easeOut" }}
            className="h-full"
          >
            {children || <Outlet />}
          </motion.div>
        </main>
      </div>
      </div>
    </div>
  );
};

export default Layout;