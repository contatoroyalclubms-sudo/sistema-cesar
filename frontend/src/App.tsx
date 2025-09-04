import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import { ThemeProvider } from './contexts/ThemeContext';
import { EventoProvider } from './contexts/EventoContext';
import ProtectedRoute from './components/ProtectedRoute';
import Layout from './components/layout/Layout';
import LoginForm from './components/auth/LoginForm';
import Dashboard from './components/dashboard/Dashboard';
import SalesModule from './components/sales/SalesModule';
import CheckinModule from './components/checkin/CheckinModule';
import EventosModule from './components/EventosModule';
import EventosMEEPModule from './components/EventosMEEPModule';
import MobileCheckinModule from './components/mobile/MobileCheckinModule';
import PDVModule from './components/pdv/PDVModule';
import DashboardPDV from './components/pdv/DashboardPDV';
import DashboardAvancado from './components/dashboard/DashboardAvancado';
import ListasModule from './components/listas/ListasModule';
import CaixaEvento from './components/financeiro/CaixaEvento';
import RankingModule from './components/ranking/RankingModule';
import EstoqueModule from './components/estoque/EstoqueModule';
import { UsuariosModule } from './components/usuarios';
import PublicRegisterPage from './components/auth/PublicRegisterPage';
import LandingPage from './components/landing/LandingPage';
import ProdutosLayout from './components/produtos/ProdutosLayout';
import ProductsList from './components/produtos/ProductsList';
import CategoriasList from './components/produtos/CategoriasList';
import AgendamentosList from './components/produtos/AgendamentosList';
import ImportExportModule from './components/produtos/ImportExportModule';
import { MEEPDashboard, MEEPAnalytics, MEEPValidacaoCPF, MEEPEquipamentos } from './components/meep';
import ClientesModule from './components/clientes/ClientesModule';
import OperadoresModule from './components/operadores/OperadoresModule';
import ComandasModule from './components/comandas/ComandasModule';
import AuthDebugPage from './debug/AuthDebugPage';
import CadastroFormasPagamento from './components/cadastros/CadastroFormasPagamento';
import DiagnosticPage from './pages/DiagnosticPage';
import BiDashboardPage from './pages/bi/BiDashboardPage';
import SplitPagamentosPage from './pages/split/SplitPagamentosPage';
import './App.css';

function App() {
  return (
    <ThemeProvider defaultTheme="system" storageKey="universal-eventos-theme">
      <AuthProvider>
        <EventoProvider>
          <Router>
            <Routes>
              <Route path="/" element={<LandingPage />} />
              <Route path="/login" element={<LoginForm />} />
              <Route path="/register" element={<PublicRegisterPage />} />
              <Route path="/diagnostic" element={<DiagnosticPage />} />
              <Route
                path="/app/*"
                element={
                  <ProtectedRoute>
                    <Layout>
                      <Routes>
                      <Route path="dashboard" element={<Dashboard />} />
                      <Route path="/" element={<Navigate to="dashboard" replace />} />
                      <Route path="eventos" element={
                        <ProtectedRoute requiredRoles={['admin', 'promoter']}>
                          <EventosModule />
                        </ProtectedRoute>
                      } />
                      <Route path="eventos-meep" element={
                        <ProtectedRoute requiredRoles={['admin', 'promoter']}>
                          <EventosMEEPModule />
                        </ProtectedRoute>
                      } />
                      <Route path="vendas" element={
                        <ProtectedRoute requiredRoles={['admin', 'promoter', 'cliente']}>
                          <SalesModule />
                        </ProtectedRoute>
                      } />
                      <Route path="checkin" element={
                        <ProtectedRoute requiredRoles={['admin', 'promoter', 'cliente']}>
                          <CheckinModule />
                        </ProtectedRoute>
                      } />
                      <Route path="checkin-inteligente" element={
                        <ProtectedRoute requiredRoles={['admin', 'promoter', 'cliente']}>
                          <CheckinModule />
                        </ProtectedRoute>
                      } />
                      <Route path="mobile-checkin" element={
                        <ProtectedRoute requiredRoles={['admin', 'promoter', 'cliente']}>
                          <MobileCheckinModule />
                        </ProtectedRoute>
                      } />
                      <Route path="pdv" element={
                        <ProtectedRoute requiredRoles={['admin', 'promoter']}>
                          <PDVModule />
                        </ProtectedRoute>
                      } />
                      <Route path="pdv/dashboard" element={
                        <ProtectedRoute requiredRoles={['admin', 'promoter']}>
                          <DashboardPDV eventoId={1} />
                        </ProtectedRoute>
                      } />
                      <Route path="usuarios" element={
                        <ProtectedRoute requiredRoles={['admin']}>
                          <UsuariosModule />
                        </ProtectedRoute>
                      } />
                      <Route path="empresas" element={
                        <ProtectedRoute requiredRoles={['admin']}>
                          <div className="p-8 text-center animate-fade-in">
                            <h1 className="text-2xl font-heading font-bold text-foreground">Módulo de Empresas</h1>
                            <p className="text-muted-foreground mt-2">Em desenvolvimento</p>
                          </div>
                        </ProtectedRoute>
                      } />
                      <Route path="listas" element={
                        <ProtectedRoute requiredRoles={['admin', 'promoter']}>
                          <ListasModule />
                        </ProtectedRoute>
                      } />
                      <Route path="produtos/*" element={
                        <ProtectedRoute requiredRoles={['admin', 'promoter']}>
                          <ProdutosLayout />
                        </ProtectedRoute>
                      }>
                        <Route index element={<ProductsList />} />
                        <Route path="categorias" element={<CategoriasList />} />
                        <Route path="agendamento" element={<AgendamentosList />} />
                        <Route path="importexport" element={<ImportExportModule />} />
                        <Route path="lista" element={
                          <div className="p-8 text-center">
                            <h1 className="text-2xl font-bold">Lista</h1>
                            <p className="text-muted-foreground mt-2">Em desenvolvimento</p>
                          </div>
                        } />
                        <Route path="acesso" element={
                          <div className="p-8 text-center">
                            <h1 className="text-2xl font-bold">Limitar Acesso</h1>
                            <p className="text-muted-foreground mt-2">Em desenvolvimento</p>
                          </div>
                        } />
                        <Route path="ignorados" element={
                          <div className="p-8 text-center">
                            <h1 className="text-2xl font-bold">Produtos Ignorados</h1>
                            <p className="text-muted-foreground mt-2">Em desenvolvimento</p>
                          </div>
                        } />
                      </Route>
                      <Route path="estoque" element={
                        <ProtectedRoute requiredRoles={['admin', 'promoter']}>
                          <EstoqueModule />
                        </ProtectedRoute>
                      } />
                      <Route path="financeiro" element={
                        <ProtectedRoute requiredRoles={['admin', 'promoter']}>
                          <CaixaEvento />
                        </ProtectedRoute>
                      } />
                      <Route path="ranking" element={
                        <ProtectedRoute requiredRoles={['admin', 'promoter']}>
                          <RankingModule />
                        </ProtectedRoute>
                      } />
                      <Route path="relatorios" element={
                        <ProtectedRoute requiredRoles={['admin', 'promoter']}>
                          <DashboardAvancado />
                        </ProtectedRoute>
                      } />
                      <Route path="bi" element={
                        <ProtectedRoute requiredRoles={['admin', 'promoter']}>
                          <BiDashboardPage />
                        </ProtectedRoute>
                      } />
                      <Route path="split" element={
                        <ProtectedRoute requiredRoles={['admin', 'promoter']}>
                          <SplitPagamentosPage />
                        </ProtectedRoute>
                      } />
                      <Route path="configuracoes" element={
                        <ProtectedRoute requiredRoles={['admin']}>
                          <div className="p-8 text-center animate-fade-in">
                            <h1 className="text-2xl font-heading font-bold text-foreground">Configurações</h1>
                            <p className="text-muted-foreground mt-2">Em desenvolvimento</p>
                          </div>
                        </ProtectedRoute>
                      } />
                      <Route path="meep/dashboard" element={
                        <ProtectedRoute requiredRoles={['admin', 'promoter']}>
                          <MEEPDashboard />
                        </ProtectedRoute>
                      } />
                      <Route path="meep/analytics" element={
                        <ProtectedRoute requiredRoles={['admin', 'promoter']}>
                          <MEEPAnalytics />
                        </ProtectedRoute>
                      } />
                      <Route path="meep/validacao-cpf" element={
                        <ProtectedRoute requiredRoles={['admin', 'promoter']}>
                          <MEEPValidacaoCPF />
                        </ProtectedRoute>
                      } />
                      <Route path="meep/equipamentos" element={
                        <ProtectedRoute requiredRoles={['admin', 'promoter']}>
                          <MEEPEquipamentos />
                        </ProtectedRoute>
                      } />
                      <Route path="cadastros/clientes" element={
                        <ProtectedRoute requiredRoles={['admin', 'promoter']}>
                          <ClientesModule />
                        </ProtectedRoute>
                      } />
                      <Route path="cadastros/operadores" element={
                        <ProtectedRoute requiredRoles={['admin']}>
                          <OperadoresModule />
                        </ProtectedRoute>
                      } />
                      <Route path="cadastros/comandas" element={
                        <ProtectedRoute requiredRoles={['admin', 'promoter']}>
                          <ComandasModule />
                        </ProtectedRoute>
                      } />
                      <Route path="cadastros/formas-pagamento" element={
                        <ProtectedRoute requiredRoles={['admin', 'promoter']}>
                          <CadastroFormasPagamento />
                        </ProtectedRoute>
                      } />
                      <Route path="cadastros/*" element={
                        <ProtectedRoute requiredRoles={['admin', 'promoter']}>
                          <div className="p-8 text-center animate-fade-in">
                            <h1 className="text-2xl font-heading font-bold text-foreground">Módulos de Cadastro</h1>
                            <p className="text-muted-foreground mt-2">Outros módulos em desenvolvimento</p>
                          </div>
                        </ProtectedRoute>
                      } />
                      <Route path="debug-auth" element={<AuthDebugPage />} />
                    </Routes>
                  </Layout>
                </ProtectedRoute>
              }
            />
          </Routes>
        </Router>
      </EventoProvider>
    </AuthProvider>
  </ThemeProvider>
  );
}

export default App;
