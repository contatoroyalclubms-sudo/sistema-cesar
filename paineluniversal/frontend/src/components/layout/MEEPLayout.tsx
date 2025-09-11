import React, { useState } from 'react';
import { Outlet, Link, useNavigate, useLocation } from 'react-router-dom';
import { motion } from 'framer-motion';
import { useAuth } from '../../contexts/AuthContext';
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
  Bell,
  Search,
  Package,
  ChevronRight,
  Home,
  PlusCircle,
  Star,
  MessageSquare,
  Tag,
  TrendingUp,
  Globe,
  Ticket,
  UserCog,
  ChefHat,
  Table2,
  CreditCard
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

interface MEEPLayoutProps {
  children?: React.ReactNode;
}

const MEEPLayout: React.FC<MEEPLayoutProps> = ({ children }) => {
  const { usuario, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  // Estrutura de navegação MEEP-style
  const navigationSections = [
    {
      title: "Principal",
      items: [
        { 
          icon: Home, 
          label: 'Dashboard', 
          path: '/app/dashboard',
          description: 'Visão geral'
        },
        { 
          icon: Calendar, 
          label: 'Eventos', 
          path: '/app/eventos',
          description: 'Gerenciar eventos',
          active: location.pathname.includes('/eventos')
        }
      ]
    },
    {
      title: "Vendas & Check-in",
      items: [
        { 
          icon: ShoppingCart, 
          label: 'Vendas', 
          path: '/app/vendas',
          description: 'Sistema de vendas'
        },
        { 
          icon: UserCheck, 
          label: 'Check-in', 
          path: '/app/checkin',
          description: 'Check-in participantes'
        },
        { 
          icon: CreditCard, 
          label: 'PDV', 
          path: '/app/pdv',
          description: 'Ponto de venda'
        }
      ]
    },
    {
      title: "Gestão",
      items: [
        { 
          icon: Users, 
          label: 'Listas & Convidados', 
          path: '/app/listas',
          description: 'Gerenciar listas'
        },
        { 
          icon: Package, 
          label: 'Produtos', 
          path: '/app/produtos',
          description: 'Gestão de produtos'
        },
        { 
          icon: Package, 
          label: 'Estoque', 
          path: '/app/estoque',
          description: 'Controle de estoque'
        }
      ]
    },
    {
      title: "Financeiro & Relatórios",
      items: [
        { 
          icon: DollarSign, 
          label: 'Financeiro', 
          path: '/app/financeiro',
          description: 'Controle financeiro'
        },
        { 
          icon: FileText, 
          label: 'Relatórios', 
          path: '/app/relatorios',
          description: 'Relatórios e análises'
        },
        { 
          icon: TrendingUp, 
          label: 'Business Intelligence', 
          path: '/app/bi',
          description: 'Dashboards e BI'
        }
      ]
    },
    {
      title: "Configurações",
      items: [
        { 
          icon: Building2, 
          label: 'Empresas', 
          path: '/app/empresas',
          description: 'Gerenciar empresas'
        },
        { 
          icon: UserCog, 
          label: 'Usuários', 
          path: '/app/usuarios',
          description: 'Gerenciar usuários'
        },
        { 
          icon: Settings, 
          label: 'Configurações', 
          path: '/app/configuracoes',
          description: 'Configurações gerais'
        }
      ]
    }
  ];

  // Gerar breadcrumbs baseado na rota atual
  const generateBreadcrumbs = () => {
    const pathSegments = location.pathname.split('/').filter(Boolean);
    const breadcrumbs = [];
    
    // Sempre começar com Dashboard
    breadcrumbs.push({ label: 'Dashboard', path: '/app/dashboard' });
    
    // Mapear segmentos para labels
    const segmentLabels: Record<string, string> = {
      'eventos': 'Eventos',
      'vendas': 'Vendas',
      'checkin': 'Check-in',
      'pdv': 'PDV',
      'listas': 'Listas & Convidados',
      'produtos': 'Produtos',
      'estoque': 'Estoque',
      'financeiro': 'Financeiro',
      'relatorios': 'Relatórios',
      'bi': 'Business Intelligence',
      'empresas': 'Empresas',
      'usuarios': 'Usuários',
      'configuracoes': 'Configurações'
    };

    let currentPath = '';
    pathSegments.slice(1).forEach(segment => { // Skip 'app'
      currentPath += `/${segment}`;
      const fullPath = `/app${currentPath}`;
      const label = segmentLabels[segment] || segment.charAt(0).toUpperCase() + segment.slice(1);
      breadcrumbs.push({ label, path: fullPath });
    });

    return breadcrumbs;
  };

  const breadcrumbs = generateBreadcrumbs();

  return (
    <div className="min-h-screen bg-gray-50 flex">
      {/* Sidebar MEEP-style */}
      <div className={`
        fixed inset-y-0 left-0 z-50 w-64 bg-white shadow-lg transform
        ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'}
        lg:translate-x-0 lg:static lg:z-auto
        border-r border-gray-200
      `}>
        {/* Header da Sidebar */}
        <div className="flex items-center justify-between h-16 px-6 border-b border-gray-200">
          <div className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
              <Calendar className="h-4 w-4 text-white" />
            </div>
            <div>
              <h1 className="text-lg font-bold text-gray-900">Sistema Universal</h1>
              <p className="text-xs text-gray-500">MEEP Style</p>
            </div>
          </div>
          
          <button
            onClick={() => setSidebarOpen(false)}
            className="lg:hidden p-2 rounded-md text-gray-400 hover:text-gray-600"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Navegação */}
        <div className="flex-1 overflow-y-auto py-4">
          {navigationSections.map((section, sectionIndex) => (
            <div key={sectionIndex} className="mb-6">
              <h3 className="px-6 text-xs font-semibold text-gray-500 uppercase tracking-wide mb-2">
                {section.title}
              </h3>
              <nav className="space-y-1 px-3">
                {section.items.map((item) => {
                  const isActive = item.active || location.pathname === item.path;
                  const Icon = item.icon;
                  
                  return (
                    <Link
                      key={item.path}
                      to={item.path}
                      className={`
                        group flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors
                        ${isActive 
                          ? 'bg-blue-50 text-blue-700 border-r-2 border-blue-700' 
                          : 'text-gray-700 hover:bg-gray-50 hover:text-gray-900'
                        }
                      `}
                    >
                      <Icon className={`
                        mr-3 h-5 w-5 flex-shrink-0
                        ${isActive ? 'text-blue-700' : 'text-gray-400 group-hover:text-gray-500'}
                      `} />
                      <span className="truncate">{item.label}</span>
                      {isActive && (
                        <ChevronRight className="ml-auto h-4 w-4 text-blue-700" />
                      )}
                    </Link>
                  );
                })}
              </nav>
            </div>
          ))}
        </div>

        {/* Footer da Sidebar */}
        <div className="border-t border-gray-200 p-4">
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" className="w-full justify-start">
                <Avatar className="h-8 w-8 mr-3">
                  <AvatarFallback>
                    {usuario?.nome?.charAt(0)?.toUpperCase() || 'U'}
                  </AvatarFallback>
                </Avatar>
                <div className="flex-1 text-left">
                  <p className="text-sm font-medium">{usuario?.nome || 'Usuário'}</p>
                  <p className="text-xs text-gray-500">{usuario?.email}</p>
                </div>
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-56">
              <DropdownMenuItem>
                <Settings className="mr-2 h-4 w-4" />
                Configurações
              </DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem onClick={handleLogout}>
                <LogOut className="mr-2 h-4 w-4" />
                Sair
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </div>

      {/* Overlay para mobile */}
      {sidebarOpen && (
        <div 
          className="fixed inset-0 z-40 bg-black bg-opacity-50 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Conteúdo Principal */}
      <div className="flex-1 lg:ml-0">
        {/* Header Principal */}
        <header className="bg-white shadow-sm border-b border-gray-200">
          <div className="flex items-center justify-between h-16 px-6">
            {/* Botão Menu Mobile + Breadcrumbs */}
            <div className="flex items-center space-x-4">
              <button
                onClick={() => setSidebarOpen(true)}
                className="lg:hidden p-2 rounded-md text-gray-400 hover:text-gray-600"
              >
                <Menu className="h-5 w-5" />
              </button>
              
              {/* Breadcrumbs MEEP-style */}
              <nav className="flex items-center space-x-2 text-sm">
                {breadcrumbs.map((breadcrumb, index) => (
                  <React.Fragment key={breadcrumb.path}>
                    {index > 0 && (
                      <ChevronRight className="h-4 w-4 text-gray-400" />
                    )}
                    <Link
                      to={breadcrumb.path}
                      className={`
                        ${index === breadcrumbs.length - 1 
                          ? 'text-gray-900 font-medium' 
                          : 'text-gray-500 hover:text-gray-700'
                        }
                      `}
                    >
                      {breadcrumb.label}
                    </Link>
                  </React.Fragment>
                ))}
              </nav>
            </div>

            {/* Barra de Busca e Ações */}
            <div className="flex items-center space-x-4">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                <Input
                  type="text"
                  placeholder="Buscar..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10 w-64"
                />
              </div>
              
              <Button variant="ghost" size="icon">
                <Bell className="h-5 w-5" />
              </Button>
            </div>
          </div>
        </header>

        {/* Área de Conteúdo */}
        <main className="flex-1 p-6">
          {children || <Outlet />}
        </main>
      </div>
    </div>
  );
};

export default MEEPLayout;
