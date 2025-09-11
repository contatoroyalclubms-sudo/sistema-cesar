import React, { useState, useEffect } from 'react';
import { Plus, Calendar, Search, Star, Users, Eye, Edit, UserPlus, Download, MapPin, Lock, ChevronLeft, ChevronRight, BarChart3, Clock, CheckCircle, XCircle, List, LogIn, DollarSign } from 'lucide-react';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Card, CardContent } from '../ui/card';
import { Alert, AlertDescription } from '../ui/alert';
import EventoModal from './EventoModal';
import EventoDetalhesModal from './EventoDetalhesModal';
import PromoterModal from './PromoterModal';
import ListaConvidados from './ListaConvidados';
import EventoCaixa from './EventoCaixa';

const EventosModule: React.FC = () => {
  const [eventos, setEventos] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [modalAberto, setModalAberto] = useState(false);
  const [detalhesModalAberto, setDetalhesModalAberto] = useState(false);
  const [promoterModalAberto, setPromoterModalAberto] = useState(false);
  const [listaConvidadosAberta, setListaConvidadosAberta] = useState(false);
  const [caixaAberto, setCaixaAberto] = useState(false);
  const [eventoSelecionado, setEventoSelecionado] = useState<any | null>(null);
  const [eventoDetalhado, setEventoDetalhado] = useState<any | null>(null);
  const [busca, setBusca] = useState('');
  const [statusSelecionado, setStatusSelecionado] = useState('Todos');
  const [anoAtual, setAnoAtual] = useState(new Date().getFullYear());
  const [mesAtual, setMesAtual] = useState(new Date().getMonth());
  
  const meses = [
    'Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun',
    'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez'
  ];

  const [estatisticas, setEstatisticas] = useState({
    totalEventos: 0,
    clientesMes: 0,
    faturamentoMes: 'R$ 0,00',
    ticketMedio: 'R$ 0,00'
  });

  useEffect(() => {
    carregarEventos();
    calcularEstatisticas();
  }, []);

  const carregarEventos = async () => {
    try {
      setLoading(true);
      const response = await fetch('http://localhost:8003/api/eventos/');
      if (!response.ok) {
        throw new Error(`Erro ao carregar eventos: ${response.status}`);
      }
      const data = await response.json();
      setEventos(data);
    } catch (error) {
      console.error('Erro ao carregar eventos:', error);
      setError('Erro ao carregar eventos. Tente novamente.');
    } finally {
      setLoading(false);
    }
  };

  const calcularEstatisticas = () => {
    const totalEventos = eventos.length;
    const clientesMes = eventos.reduce((acc, evento) => acc + (evento.participantes?.length || 0), 0);
    const faturamentoMes = eventos.reduce((acc, evento) => acc + (evento.valor_total || 0), 0);
    const ticketMedio = totalEventos > 0 ? faturamentoMes / totalEventos : 0;

    setEstatisticas({
      totalEventos,
      clientesMes,
      faturamentoMes: `R$ ${faturamentoMes.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}`,
      ticketMedio: `R$ ${ticketMedio.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}`
    });
  };

  const handleSalvarEvento = async (eventoData: any) => {
    try {
      setError(null);
      setSuccess(null);

      const url = eventoSelecionado
        ? `http://localhost:8003/api/eventos/${eventoSelecionado.id}`
        : 'http://localhost:8003/api/eventos/';

      const method = eventoSelecionado ? 'PUT' : 'POST';

      const response = await fetch(url, {
        method,
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(eventoData),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Erro ao salvar evento');
      }

      setSuccess(eventoSelecionado ? 'Evento atualizado com sucesso!' : 'Evento criado com sucesso!');
      setModalAberto(false);
      setEventoSelecionado(null);
      await carregarEventos();
      calcularEstatisticas();
    } catch (error) {
      console.error('Erro ao salvar evento:', error);
      setError(error instanceof Error ? error.message : 'Erro desconhecido ao salvar evento');
    }
  };

  const handleEditarEvento = (evento: any) => {
    setEventoSelecionado(evento);
    setModalAberto(true);
  };

  const handleVerDetalhes = (evento: any) => {
    setEventoDetalhado(evento);
    setDetalhesModalAberto(true);
  };

  const handleAbrirPromoters = (evento: any) => {
    setEventoSelecionado(evento);
    setPromoterModalAberto(true);
  };

  const handleAbrirListaConvidados = (evento: any) => {
    setEventoSelecionado(evento);
    setListaConvidadosAberta(true);
  };

  const handleEntrarCaixa = (evento: any) => {
    setEventoSelecionado(evento);
    setCaixaAberto(true);
  };

  const eventosFiltrados = eventos.filter(evento => {
    const matchBusca = busca === '' || 
      evento.nome?.toLowerCase().includes(busca.toLowerCase()) ||
      evento.descricao?.toLowerCase().includes(busca.toLowerCase());
    
    const matchStatus = statusSelecionado === 'Todos' || evento.status === statusSelecionado.toLowerCase();
    
    return matchBusca && matchStatus;
  });

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-lg">Carregando eventos...</div>
      </div>
    );
  }

  return (
    <div className="w-full h-full bg-gray-50 min-h-screen">
      {/* Header MEEP Style */}
      <div className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <h1 className="text-2xl font-semibold text-gray-800">Evento/Caixa</h1>
            <Star className="h-5 w-5 text-yellow-400 cursor-pointer" />
          </div>
          
          {/* Info Notice */}
          <div className="flex items-center gap-2 bg-blue-50 border border-blue-200 rounded-lg px-4 py-2">
            <div className="h-2 w-2 bg-blue-500 rounded-full"></div>
            <span className="text-sm text-blue-700">Bem-vindo à nova tela de eventos. Agora com navegação mais intuitiva.</span>
            <button className="text-blue-500 hover:text-blue-700">
              <Eye className="h-4 w-4" />
            </button>
          </div>
        </div>
        
        {/* Action Buttons */}
        <div className="flex items-center gap-4 mt-4">
          <Button
            onClick={() => setModalAberto(true)}
            className="bg-primary hover:bg-primary/90 text-primary-foreground px-6 py-2 rounded-lg font-medium"
          >
            <Plus className="h-4 w-4 mr-2" />
            Novo evento
          </Button>
          <Button
            variant="outline"
            className="border-gray-300 text-gray-700 hover:bg-gray-50 px-6 py-2 rounded-lg"
          >
            <Users className="h-4 w-4 mr-2" />
            Acesso a todos os eventos
          </Button>
        </div>
        
        {/* Search Bar */}
        <div className="mt-4 relative max-w-md">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
          <Input
            type="text"
            placeholder="Buscar"
            value={busca}
            onChange={(e) => setBusca(e.target.value)}
            className="pl-10 border-gray-300 rounded-lg"
          />
        </div>
      </div>

      {/* Calendar Navigation MEEP Style */}
      <div className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="flex items-center justify-center gap-4 mb-4">
          <button 
            onClick={() => setAnoAtual(anoAtual - 1)}
            className="p-1 hover:bg-gray-100 rounded"
          >
            <ChevronLeft className="h-4 w-4" />
          </button>
          <h2 className="text-xl font-semibold text-gray-800 min-w-[80px] text-center">
            {anoAtual}
          </h2>
          <button 
            onClick={() => setAnoAtual(anoAtual + 1)}
            className="p-1 hover:bg-gray-100 rounded"
          >
            <ChevronRight className="h-4 w-4" />
          </button>
        </div>
        
        {/* Month Grid */}
        <div className="grid grid-cols-4 gap-2 mb-6">
          {meses.map((mes, index) => (
            <button
              key={mes}
              onClick={() => setMesAtual(index)}
              className={`px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                index === mesAtual
                  ? 'bg-primary text-primary-foreground'
                  : 'text-gray-600 hover:bg-gray-100'
              }`}
            >
              {mes}
            </button>
          ))}
        </div>
      </div>

      {/* Statistics MEEP Style */}
      <div className="bg-white px-6 py-6">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
          <div className="text-center">
            <div className="text-2xl font-bold text-gray-800">{estatisticas.totalEventos}</div>
            <div className="text-sm text-gray-500">Eventos</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-gray-800">{estatisticas.clientesMes}</div>
            <div className="text-sm text-gray-500">Clientes do mês</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-gray-800">{estatisticas.faturamentoMes}</div>
            <div className="text-sm text-gray-500">Faturamento do mês</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-gray-800">{estatisticas.ticketMedio}</div>
            <div className="text-sm text-gray-500">Ticket médio de ingresso</div>
          </div>
        </div>
      </div>

      {/* Status Filter MEEP Style */}
      <div className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="flex items-center gap-4">
          {['Todos', 'Programado', 'Acontecendo', 'Encerrado'].map((status) => (
            <button
              key={status}
              onClick={() => setStatusSelecionado(status)}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                statusSelecionado === status
                  ? 'bg-primary/10 text-primary border border-primary/20'
                  : 'text-gray-600 hover:bg-gray-100'
              }`}
            >
              {status}
            </button>
          ))}
        </div>
      </div>

      {/* Events List MEEP Style */}
      <div className="px-6 py-6">
        {error && (
          <Alert variant="destructive" className="mb-4">
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {success && (
          <Alert className="mb-4 border-green-200 bg-green-50">
            <AlertDescription className="text-green-700">{success}</AlertDescription>
          </Alert>
        )}

        {/* Date Header */}
        <h3 className="text-lg font-medium text-gray-700 mb-4">
          {String(new Date().getDate()).padStart(2, '0')}/{String(mesAtual + 1).padStart(2, '0')}/{anoAtual}
        </h3>

        {/* Events Cards */}
        <div className="space-y-4">
          {eventosFiltrados.map((evento) => (
            <Card key={evento.id} className="bg-white border border-gray-200 hover:shadow-md transition-shadow">
              <CardContent className="p-6">
                <div className="flex items-start gap-4">
                  {/* Event Image */}
                  <div className="w-16 h-16 bg-gradient-to-br from-primary to-primary/80 rounded-lg flex items-center justify-center">
                    <Calendar className="h-8 w-8 text-white" />
                  </div>
                  
                  {/* Event Info */}
                  <div className="flex-1">
                    <div className="flex items-start justify-between">
                      <div>
                        <h4 className="text-lg font-semibold text-gray-800 mb-1">
                          {evento.nome}
                        </h4>
                        <div className="flex items-center gap-4 text-sm text-gray-600 mb-2">
                          <span>
                            {evento.data_inicio_evento ? new Date(evento.data_inicio_evento).toLocaleDateString('pt-BR') : 
                             evento.data_evento ? new Date(evento.data_evento).toLocaleDateString('pt-BR') : 'Data não definida'} - 
                            {evento.data_inicio_evento ? new Date(evento.data_inicio_evento).toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' }) : 
                             evento.data_evento ? new Date(evento.data_evento).toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' }) : '00:00'} até 
                            {evento.data_fim_evento ? new Date(evento.data_fim_evento).toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' }) : '23:59'}
                          </span>
                        </div>
                        <div className="flex items-center gap-4 text-sm text-gray-600">
                          <div className="flex items-center gap-1">
                            <MapPin className="h-4 w-4" />
                            <span>{evento.local || 'Local não definido'}</span>
                          </div>
                          <div className="flex items-center gap-1">
                            <Users className="h-4 w-4" />
                            <span>Limite: {evento.limite_idade || 18}+ | Capacidade: {evento.capacidade_maxima || 100}</span>
                          </div>
                        </div>
                        <p className="text-sm text-gray-600 mt-2">
                          {evento.descricao || 'Sem descrição'}
                        </p>
                        
                        {/* Estatísticas do Evento - Como no MEEP */}
                        <div className="mt-4 pt-4 border-t border-gray-100">
                          <div className="grid grid-cols-3 gap-4">
                            <div>
                              <p className="text-xs text-gray-500">Faturamento</p>
                              <p className="text-sm font-bold text-gray-800">
                                R$ {evento.faturamento || '0,00'}
                              </p>
                            </div>
                            <div>
                              <p className="text-xs text-gray-500">Ticket Médio</p>
                              <p className="text-sm font-bold text-gray-800">
                                R$ {evento.ticket_medio || '0,00'}
                              </p>
                            </div>
                            <div>
                              <p className="text-xs text-gray-500">Check-ins</p>
                              <p className="text-sm font-bold text-gray-800">
                                {evento.checkins_realizados || 0}/{evento.vendas_totais || 0}
                              </p>
                            </div>
                          </div>
                          
                          {/* Listas do Evento */}
                          <div className="mt-3 pt-3 border-t border-gray-100">
                            <div className="flex items-center justify-between text-xs">
                              <div>
                                <span className="text-gray-500">Entrada geral: </span>
                                <span className="font-semibold">{evento.entradas_vendidas || 0}</span>
                              </div>
                              <div>
                                <span className="text-gray-500">Nome na lista: </span>
                                <span className="font-semibold">{evento.lista_convidados || 0}</span>
                              </div>
                              <div>
                                <span className="text-gray-500">Total: </span>
                                <span className="font-semibold text-primary">{evento.total_participantes || 0}</span>
                              </div>
                            </div>
                          </div>
                        </div>
                      </div>
                      
                      {/* Status Badge */}
                      <div className="flex items-center gap-2">
                        <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                          evento.status === 'ativo' ? 'bg-green-100 text-green-700' :
                          evento.status === 'programado' ? 'bg-blue-100 text-blue-700' :
                          evento.status === 'encerrado' ? 'bg-gray-100 text-gray-700' :
                          'bg-yellow-100 text-yellow-700'
                        }`}>
                          {evento.status || 'planejamento'}
                        </span>
                        <Lock className="h-4 w-4 text-gray-400" />
                      </div>
                    </div>
                    
                    {/* Action Buttons */}
                    <div className="flex items-center justify-between mt-4">
                      <div className="flex items-center gap-2">
                        <Button
                          size="lg"
                          onClick={() => handleEntrarCaixa(evento)}
                          className="bg-primary hover:bg-primary/90 text-primary-foreground px-8"
                        >
                          <LogIn className="h-5 w-5 mr-2" />
                          Entrar
                        </Button>
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => handleVerDetalhes(evento)}
                          className="text-sm"
                        >
                          <Eye className="h-4 w-4 mr-1" />
                          Detalhes
                        </Button>
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => handleEditarEvento(evento)}
                          className="text-sm"
                        >
                          <Edit className="h-4 w-4 mr-1" />
                          Editar
                        </Button>
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => handleAbrirPromoters(evento)}
                          className="text-sm"
                        >
                          <UserPlus className="h-4 w-4 mr-1" />
                          Promoters
                        </Button>
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => handleAbrirListaConvidados(evento)}
                          className="text-sm"
                        >
                          <List className="h-4 w-4 mr-1" />
                          Lista
                        </Button>
                      </div>
                      
                      <div className="flex items-center gap-2">
                        <Button size="sm" variant="outline" className="text-sm">
                          <Download className="h-4 w-4 mr-1" />
                          CSV
                        </Button>
                        <Button size="sm" variant="outline" className="text-sm">
                          <Download className="h-4 w-4 mr-1" />
                          PDF
                        </Button>
                      </div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        {eventosFiltrados.length === 0 && !loading && (
          <div className="text-center py-12">
            <Calendar className="h-12 w-12 text-gray-300 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">Nenhum evento encontrado</h3>
            <p className="text-gray-500 mb-4">Comece criando seu primeiro evento.</p>
            <Button onClick={() => setModalAberto(true)} className="bg-primary hover:bg-primary/90">
              <Plus className="h-4 w-4 mr-2" />
              Criar Primeiro Evento
            </Button>
          </div>
        )}
      </div>

      {/* Modals */}
      <EventoModal
        isOpen={modalAberto}
        onClose={() => {
          setModalAberto(false);
          setEventoSelecionado(null);
        }}
        onSave={handleSalvarEvento}
        evento={eventoSelecionado}
      />

      <EventoDetalhesModal
        isOpen={detalhesModalAberto}
        onClose={() => {
          setDetalhesModalAberto(false);
          setEventoDetalhado(null);
        }}
        evento={eventoDetalhado}
      />

      <PromoterModal
        isOpen={promoterModalAberto}
        onClose={() => {
          setPromoterModalAberto(false);
          setEventoSelecionado(null);
        }}
        evento={eventoSelecionado}
        onUpdate={carregarEventos}
      />

      <ListaConvidados
        isOpen={listaConvidadosAberta}
        onClose={() => {
          setListaConvidadosAberta(false);
          setEventoSelecionado(null);
        }}
        eventoId={eventoSelecionado?.id}
        eventoNome={eventoSelecionado?.nome}
      />

      {/* Módulo de Caixa/PDV do Evento */}
      {caixaAberto && eventoSelecionado && (
        <div className="fixed inset-0 z-50 bg-background">
          <EventoCaixa
            eventoId={eventoSelecionado.id}
            eventoNome={eventoSelecionado.nome}
            onClose={() => {
              setCaixaAberto(false);
              setEventoSelecionado(null);
              carregarEventos(); // Recarregar eventos para atualizar estatísticas
            }}
          />
        </div>
      )}
    </div>
  );
};

export default EventosModule;
