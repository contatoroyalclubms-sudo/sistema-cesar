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
import EventosModule from './components/eventos/EventosModule';
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
import PrinterManagement from './components/PrinterManagement';
import DiagnosticPage from './pages/DiagnosticPage';
import Empresas from './pages/Empresas';
// Novos módulos implementados
import CategoriasClientesModule from './components/categorias/CategoriasClientesModule';
import PesquisaSatisfacaoModule from './components/satisfacao/PesquisaSatisfacaoModule';
import FidelidadeModule from './components/fidelidade/FidelidadeModule';
import AutomacaoModule from './components/automacao/AutomacaoModule';
import BusinessIntelligenceModule from './components/business-intelligence/BusinessIntelligenceModule';
import IntegracoesModule from './components/integracoes/IntegracoesModule';
import SolucoesOnlineModule from './components/solucoes-online/SolucoesOnlineModule';
import TicketsModule from './components/tickets/TicketsModule';
import ColaboradoresModule from './components/colaboradores/ColaboradoresModule';
import MultiCardapioModule from './components/multi-cardapio/MultiCardapioModule';
import KDSModule from './components/kds/KDSModule';
import MesasModule from './components/mesas/MesasModule';
import ImpressorasModule from './components/impressoras/ImpressorasModule';
import './App.css';

function App() {
  return (
    <ThemeProvider defaultTheme="system" storageKey="universal-eventos-theme">
      <AuthProvider>
        <EventoProvider>
          <Router>
            <Routes>
              <Route path="/" element={<Navigate to="/login" replace />} />
              <Route path="/landing" element={<LandingPage />} />
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
                          <Empresas />
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
                      <Route path="cadastros/impressoras-legacy" element={
                        <ProtectedRoute requiredRoles={['admin', 'promoter']}>
                          <PrinterManagement />
                        </ProtectedRoute>
                      } />
                      <Route path="cadastros/impressoras" element={
                        <ProtectedRoute requiredRoles={['admin', 'promoter']}>
                          <ImpressorasModule />
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
                      
                      {/* Novos Módulos Implementados */}
                      <Route path="categorias-clientes" element={
                        <ProtectedRoute requiredRoles={['admin', 'promoter']}>
                          <CategoriasClientesModule />
                        </ProtectedRoute>
                      } />
                      <Route path="pesquisa-satisfacao" element={
                        <ProtectedRoute requiredRoles={['admin', 'promoter']}>
                          <PesquisaSatisfacaoModule />
                        </ProtectedRoute>
                      } />
                      <Route path="fidelidade" element={
                        <ProtectedRoute requiredRoles={['admin', 'promoter', 'cliente']}>
                          <FidelidadeModule />
                        </ProtectedRoute>
                      } />
                      
                      {/* Módulos Implementados */}
                      <Route path="automacao/*" element={
                        <ProtectedRoute requiredRoles={['admin', 'promoter']}>
                          <AutomacaoModule />
                        </ProtectedRoute>
                      } />
                      <Route path="bi/*" element={
                        <ProtectedRoute requiredRoles={['admin', 'promoter']}>
                          <BusinessIntelligenceModule />
                        </ProtectedRoute>
                      } />
                      <Route path="integracoes/*" element={
                        <ProtectedRoute requiredRoles={['admin']}>
                          <IntegracoesModule />
                        </ProtectedRoute>
                      } />
                      <Route path="solucoes-online/*" element={
                        <ProtectedRoute requiredRoles={['admin', 'promoter']}>
                          <SolucoesOnlineModule />
                        </ProtectedRoute>
                      } />
                      <Route path="tickets/*" element={
                        <ProtectedRoute requiredRoles={['admin', 'promoter', 'cliente']}>
                          <TicketsModule />
                        </ProtectedRoute>
                      } />
                      <Route path="colaboradores/*" element={
                        <ProtectedRoute requiredRoles={['admin', 'promoter']}>
                          <ColaboradoresModule />
                        </ProtectedRoute>
                      } />
                      <Route path="multi-cardapio/*" element={
                        <ProtectedRoute requiredRoles={['admin', 'promoter']}>
                          <MultiCardapioModule />
                        </ProtectedRoute>
                      } />
                      <Route path="kds" element={
                        <ProtectedRoute requiredRoles={['admin', 'promoter']}>
                          <KDSModule />
                        </ProtectedRoute>
                      } />
                      <Route path="mesas" element={
                        <ProtectedRoute requiredRoles={['admin', 'promoter']}>
                          <MesasModule />
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
