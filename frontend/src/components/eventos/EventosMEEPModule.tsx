/**
 * SISTEMA DE EVENTOS - NÍVEL MEEP
 * Implementação completa para igualar funcionalidades do MEEP
 */

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Label } from '../ui/label';
import { Textarea } from '../ui/textarea';
import { Badge } from '../ui/badge';
import { Alert, AlertDescription } from '../ui/alert';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs';
import { 
  Calendar, 
  MapPin, 
  Users, 
  DollarSign, 
  Plus, 
  Search, 
  Filter,
  Download,
  Edit,
  Trash2,
  Eye,
  UserPlus,
  Clock,
  Image,
  Settings,
  BarChart3,
  Share2,
  QrCode,
  Camera,
  TrendingUp,
  Target,
  CheckCircle,
  XCircle,
  AlertTriangle
} from 'lucide-react';

// Interfaces completas para eventos nível MEEP
interface EventoMEEP {
  id?: number;
  nome: string;
  descricao: string;
  data_evento: string;
  hora_inicio: string;
  hora_fim: string;
  local: string;
  endereco: string;
  cidade: string;
  estado: string;
  cep: string;
  coordenadas?: {
    lat: number;
    lng: number;
  };
  capacidade_maxima: number;
  limite_idade: number;
  status: 'rascunho' | 'publicado' | 'em_andamento' | 'finalizado' | 'cancelado';
  tipo_evento: 'festa' | 'show' | 'conferencia' | 'workshop' | 'corporativo' | 'outro';
  categoria: string;
  
  // Configurações de venda
  vendas_ativas: boolean;
  data_inicio_vendas: string;
  data_fim_vendas: string;
  permite_lista: boolean;
  permite_cortesia: boolean;
  permite_promocional: boolean;
  
  // Branding e mídia
  imagem_capa?: string;
  logo_evento?: string;
  cores_personalizadas?: {
    primaria: string;
    secundaria: string;
    fundo: string;
  };
  
  // Analytics e métricas
  total_vendas: number;
  total_checkins: number;
  total_no_shows: number;
  receita_total: number;
  taxa_conversao: number;
  
  // Configurações avançadas
  configuracoes: {
    permite_revendas: boolean;
    limite_por_cpf: number;
    exige_validacao_idade: boolean;
    permite_meia_entrada: boolean;
    taxa_conveniencia: number;
    politica_cancelamento: string;
  };
  
  // Integração e automação
  integracao_pix: boolean;
  whatsapp_ativo: boolean;
  email_confirmacao: boolean;
  lembrete_automatico: boolean;
  
  created_at?: string;
  updated_at?: string;
  criado_por?: number;
}

interface LoteEvento {
  id?: number;
  evento_id: number;
  nome: string;
  descricao: string;
  preco: number;
  quantidade_total: number;
  quantidade_vendida: number;
  data_inicio: string;
  data_fim: string;
  ativo: boolean;
  ordem: number;
  tipo: 'normal' | 'promocional' | 'vip' | 'backstage';
  permite_meia: boolean;
  taxa_adicional: number;
}

interface PromoterEvento {
  id?: number;
  evento_id: number;
  usuario_id: number;
  nome: string;
  email: string;
  telefone: string;
  comissao_percentual: number;
  meta_vendas: number;
  vendas_realizadas: number;
  link_personalizado: string;
  ativo: boolean;
  observacoes?: string;
}

interface CheckinEvento {
  id?: number;
  evento_id: number;
  ingresso_id: number;
  data_checkin: string;
  localização?: string;
  dispositivo?: string;
  operador?: string;
  observacoes?: string;
}

const EventosMEEPModule: React.FC = () => {
  const [eventos, setEventos] = useState<EventoMEEP[]>([]);
  const [eventoSelecionado, setEventoSelecionado] = useState<EventoMEEP | null>(null);
  const [lotes, setLotes] = useState<LoteEvento[]>([]);
  const [promoters, setPromoters] = useState<PromoterEvento[]>([]);
  const [checkins, setCheckins] = useState<CheckinEvento[]>([]);
  
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  
  const [modalAberto, setModalAberto] = useState(false);
  const [abaSelecionada, setAbaSelecionada] = useState('geral');
  const [busca, setBusca] = useState('');
  const [filtroStatus, setFiltroStatus] = useState<string>('todos');

  // Estado para novo evento
  const [novoEvento, setNovoEvento] = useState<Partial<EventoMEEP>>({
    nome: '',
    descricao: '',
    data_evento: '',
    hora_inicio: '',
    hora_fim: '',
    local: '',
    endereco: '',
    cidade: '',
    estado: '',
    cep: '',
    capacidade_maxima: 100,
    limite_idade: 18,
    status: 'rascunho',
    tipo_evento: 'festa',
    categoria: '',
    vendas_ativas: false,
    data_inicio_vendas: '',
    data_fim_vendas: '',
    permite_lista: true,
    permite_cortesia: true,
    permite_promocional: true,
    configuracoes: {
      permite_revendas: false,
      limite_por_cpf: 4,
      exige_validacao_idade: true,
      permite_meia_entrada: true,
      taxa_conveniencia: 10,
      politica_cancelamento: 'Não há reembolso após a compra'
    },
    integracao_pix: true,
    whatsapp_ativo: true,
    email_confirmacao: true,
    lembrete_automatico: true
  });

  useEffect(() => {
    carregarEventos();
  }, []);

  const carregarEventos = async () => {
    try {
      setLoading(true);
      // Simular dados do MEEP
      const eventosMock: EventoMEEP[] = [
        {
          id: 1,
          nome: "Festival de Música Eletrônica 2025",
          descricao: "O maior festival de música eletrônica do estado",
          data_evento: "2025-12-31",
          hora_inicio: "22:00",
          hora_fim: "06:00",
          local: "Arena Multiuso",
          endereco: "Rua das Flores, 123",
          cidade: "São Paulo",
          estado: "SP",
          cep: "01234-567",
          capacidade_maxima: 5000,
          limite_idade: 18,
          status: 'publicado',
          tipo_evento: 'festa',
          categoria: 'Música Eletrônica',
          vendas_ativas: true,
          data_inicio_vendas: "2025-09-01",
          data_fim_vendas: "2025-12-30",
          permite_lista: true,
          permite_cortesia: true,
          permite_promocional: true,
          total_vendas: 1250,
          total_checkins: 0,
          total_no_shows: 0,
          receita_total: 187500,
          taxa_conversao: 25,
          configuracoes: {
            permite_revendas: false,
            limite_por_cpf: 4,
            exige_validacao_idade: true,
            permite_meia_entrada: true,
            taxa_conveniencia: 10,
            politica_cancelamento: 'Reembolso até 48h antes do evento'
          },
          integracao_pix: true,
          whatsapp_ativo: true,
          email_confirmacao: true,
          lembrete_automatico: true,
          created_at: "2025-09-01T10:00:00Z"
        },
        {
          id: 2,
          nome: "Workshop de Empreendedorismo",
          descricao: "Aprenda as melhores estratégias para empreender",
          data_evento: "2025-10-15",
          hora_inicio: "14:00",
          hora_fim: "18:00",
          local: "Centro de Convenções",
          endereco: "Av. Principal, 456",
          cidade: "Rio de Janeiro",
          estado: "RJ",
          cep: "20000-000",
          capacidade_maxima: 200,
          limite_idade: 16,
          status: 'em_andamento',
          tipo_evento: 'workshop',
          categoria: 'Negócios',
          vendas_ativas: true,
          data_inicio_vendas: "2025-08-15",
          data_fim_vendas: "2025-10-14",
          permite_lista: false,
          permite_cortesia: true,
          permite_promocional: false,
          total_vendas: 156,
          total_checkins: 45,
          total_no_shows: 5,
          receita_total: 15600,
          taxa_conversao: 78,
          configuracoes: {
            permite_revendas: true,
            limite_por_cpf: 2,
            exige_validacao_idade: false,
            permite_meia_entrada: true,
            taxa_conveniencia: 5,
            politica_cancelamento: 'Reembolso integral até 7 dias antes'
          },
          integracao_pix: true,
          whatsapp_ativo: false,
          email_confirmacao: true,
          lembrete_automatico: true,
          created_at: "2025-08-15T09:00:00Z"
        }
      ];
      
      setEventos(eventosMock);
    } catch (err) {
      setError('Erro ao carregar eventos');
    } finally {
      setLoading(false);
    }
  };

  const salvarEvento = async () => {
    try {
      setError(null);
      
      // Validações
      if (!novoEvento.nome || !novoEvento.data_evento) {
        setError('Nome e data do evento são obrigatórios');
        return;
      }
      
      const evento: EventoMEEP = {
        ...novoEvento as EventoMEEP,
        id: eventoSelecionado?.id || Date.now(),
        total_vendas: 0,
        total_checkins: 0,
        total_no_shows: 0,
        receita_total: 0,
        taxa_conversao: 0,
        created_at: new Date().toISOString()
      };
      
      if (eventoSelecionado) {
        setEventos(eventos.map(e => e.id === evento.id ? evento : e));
        setSuccess('Evento atualizado com sucesso!');
      } else {
        setEventos([...eventos, evento]);
        setSuccess('Evento criado com sucesso!');
      }
      
      fecharModal();
      setTimeout(() => setSuccess(null), 3000);
      
    } catch (err) {
      setError('Erro ao salvar evento');
    }
  };

  const fecharModal = () => {
    setModalAberto(false);
    setEventoSelecionado(null);
    setNovoEvento({
      nome: '',
      descricao: '',
      data_evento: '',
      hora_inicio: '',
      hora_fim: '',
      local: '',
      endereco: '',
      cidade: '',
      estado: '',
      cep: '',
      capacidade_maxima: 100,
      limite_idade: 18,
      status: 'rascunho',
      tipo_evento: 'festa',
      categoria: '',
      vendas_ativas: false,
      data_inicio_vendas: '',
      data_fim_vendas: '',
      permite_lista: true,
      permite_cortesia: true,
      permite_promocional: true,
      configuracoes: {
        permite_revendas: false,
        limite_por_cpf: 4,
        exige_validacao_idade: true,
        permite_meia_entrada: true,
        taxa_conveniencia: 10,
        politica_cancelamento: 'Não há reembolso após a compra'
      },
      integracao_pix: true,
      whatsapp_ativo: true,
      email_confirmacao: true,
      lembrete_automatico: true
    });
  };

  const editarEvento = (evento: EventoMEEP) => {
    setEventoSelecionado(evento);
    setNovoEvento(evento);
    setModalAberto(true);
  };

  const excluirEvento = async (evento: EventoMEEP) => {
    if (!confirm(`Tem certeza que deseja excluir o evento "${evento.nome}"?`)) {
      return;
    }
    
    setEventos(eventos.filter(e => e.id !== evento.id));
    setSuccess('Evento excluído com sucesso!');
    setTimeout(() => setSuccess(null), 3000);
  };

  const getStatusBadge = (status: string) => {
    const statusConfig = {
      'rascunho': { color: 'bg-gray-500', text: 'Rascunho' },
      'publicado': { color: 'bg-green-500', text: 'Publicado' },
      'em_andamento': { color: 'bg-blue-500', text: 'Em Andamento' },
      'finalizado': { color: 'bg-purple-500', text: 'Finalizado' },
      'cancelado': { color: 'bg-red-500', text: 'Cancelado' }
    };
    
    const config = statusConfig[status as keyof typeof statusConfig] || statusConfig.rascunho;
    
    return (
      <Badge className={`${config.color} text-white`}>
        {config.text}
      </Badge>
    );
  };

  const eventosFiltrados = eventos.filter(evento => {
    const matchBusca = evento.nome.toLowerCase().includes(busca.toLowerCase()) ||
                     evento.local.toLowerCase().includes(busca.toLowerCase());
    const matchStatus = filtroStatus === 'todos' || evento.status === filtroStatus;
    
    return matchBusca && matchStatus;
  });

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-3xl font-bold">Gestão de Eventos</h2>
        <Button onClick={() => setModalAberto(true)}>
          <Plus className="w-4 h-4 mr-2" />
          Novo Evento
        </Button>
      </div>

      {error && (
        <Alert className="border-red-200 bg-red-50">
          <AlertTriangle className="h-4 w-4 text-red-600" />
          <AlertDescription className="text-red-700">{error}</AlertDescription>
        </Alert>
      )}

      {success && (
        <Alert className="border-green-200 bg-green-50">
          <CheckCircle className="h-4 w-4 text-green-600" />
          <AlertDescription className="text-green-700">{success}</AlertDescription>
        </Alert>
      )}

      {/* Filtros e Busca */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex gap-4 items-center">
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                <Input
                  placeholder="Buscar eventos..."
                  value={busca}
                  onChange={(e) => setBusca(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>
            <div>
              <select
                value={filtroStatus}
                onChange={(e) => setFiltroStatus(e.target.value)}
                className="border rounded-md px-3 py-2"
              >
                <option value="todos">Todos os Status</option>
                <option value="rascunho">Rascunho</option>
                <option value="publicado">Publicado</option>
                <option value="em_andamento">Em Andamento</option>
                <option value="finalizado">Finalizado</option>
                <option value="cancelado">Cancelado</option>
              </select>
            </div>
            <Button variant="outline">
              <Download className="w-4 h-4 mr-2" />
              Exportar
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Lista de Eventos */}
      <div className="grid gap-6">
        {loading ? (
          <div className="text-center py-8">Carregando eventos...</div>
        ) : eventosFiltrados.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            Nenhum evento encontrado
          </div>
        ) : (
          eventosFiltrados.map((evento) => (
            <Card key={evento.id} className="hover:shadow-lg transition-shadow">
              <CardContent className="pt-6">
                <div className="flex justify-between items-start mb-4">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <h3 className="text-xl font-semibold">{evento.nome}</h3>
                      {getStatusBadge(evento.status)}
                    </div>
                    <p className="text-gray-600 mb-3">{evento.descricao}</p>
                    
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                      <div className="flex items-center text-gray-600">
                        <Calendar className="w-4 h-4 mr-2" />
                        {new Date(evento.data_evento).toLocaleDateString('pt-BR')}
                      </div>
                      <div className="flex items-center text-gray-600">
                        <Clock className="w-4 h-4 mr-2" />
                        {evento.hora_inicio} - {evento.hora_fim}
                      </div>
                      <div className="flex items-center text-gray-600">
                        <MapPin className="w-4 h-4 mr-2" />
                        {evento.local}
                      </div>
                      <div className="flex items-center text-gray-600">
                        <Users className="w-4 h-4 mr-2" />
                        {evento.total_vendas}/{evento.capacidade_maxima}
                      </div>
                    </div>
                  </div>
                  
                  <div className="flex items-center gap-2 ml-4">
                    <Button variant="outline" size="sm" onClick={() => editarEvento(evento)}>
                      <Edit className="w-4 h-4" />
                    </Button>
                    <Button variant="outline" size="sm">
                      <Eye className="w-4 h-4" />
                    </Button>
                    <Button variant="outline" size="sm">
                      <BarChart3 className="w-4 h-4" />
                    </Button>
                    <Button variant="outline" size="sm" onClick={() => excluirEvento(evento)}>
                      <Trash2 className="w-4 h-4" />
                    </Button>
                  </div>
                </div>
                
                {/* Métricas do Evento */}
                <div className="border-t pt-4">
                  <div className="grid grid-cols-4 gap-4 text-center">
                    <div>
                      <div className="text-2xl font-bold text-blue-600">{evento.total_vendas}</div>
                      <div className="text-sm text-gray-500">Vendas</div>
                    </div>
                    <div>
                      <div className="text-2xl font-bold text-green-600">
                        R$ {evento.receita_total.toLocaleString('pt-BR')}
                      </div>
                      <div className="text-sm text-gray-500">Receita</div>
                    </div>
                    <div>
                      <div className="text-2xl font-bold text-purple-600">{evento.total_checkins}</div>
                      <div className="text-sm text-gray-500">Check-ins</div>
                    </div>
                    <div>
                      <div className="text-2xl font-bold text-orange-600">{evento.taxa_conversao}%</div>
                      <div className="text-sm text-gray-500">Conversão</div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))
        )}
      </div>

      {/* Modal de Evento */}
      {modalAberto && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6 border-b">
              <h2 className="text-2xl font-bold">
                {eventoSelecionado ? 'Editar Evento' : 'Novo Evento'}
              </h2>
            </div>
            
            <div className="p-6">
              <Tabs value={abaSelecionada} onValueChange={setAbaSelecionada}>
                <TabsList className="grid w-full grid-cols-5">
                  <TabsTrigger value="geral">Geral</TabsTrigger>
                  <TabsTrigger value="vendas">Vendas</TabsTrigger>
                  <TabsTrigger value="configuracoes">Configurações</TabsTrigger>
                  <TabsTrigger value="design">Design</TabsTrigger>
                  <TabsTrigger value="integracao">Integração</TabsTrigger>
                </TabsList>

                <TabsContent value="geral" className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <Label htmlFor="nome">Nome do Evento *</Label>
                      <Input
                        id="nome"
                        value={novoEvento.nome}
                        onChange={(e) => setNovoEvento({...novoEvento, nome: e.target.value})}
                        placeholder="Digite o nome do evento"
                      />
                    </div>
                    <div>
                      <Label htmlFor="categoria">Categoria</Label>
                      <Input
                        id="categoria"
                        value={novoEvento.categoria}
                        onChange={(e) => setNovoEvento({...novoEvento, categoria: e.target.value})}
                        placeholder="Ex: Música, Negócios, Esporte"
                      />
                    </div>
                  </div>

                  <div>
                    <Label htmlFor="descricao">Descrição</Label>
                    <Textarea
                      id="descricao"
                      value={novoEvento.descricao}
                      onChange={(e) => setNovoEvento({...novoEvento, descricao: e.target.value})}
                      placeholder="Descreva o evento"
                      rows={3}
                    />
                  </div>

                  <div className="grid grid-cols-3 gap-4">
                    <div>
                      <Label htmlFor="data_evento">Data do Evento *</Label>
                      <Input
                        id="data_evento"
                        type="date"
                        value={novoEvento.data_evento}
                        onChange={(e) => setNovoEvento({...novoEvento, data_evento: e.target.value})}
                      />
                    </div>
                    <div>
                      <Label htmlFor="hora_inicio">Hora Início</Label>
                      <Input
                        id="hora_inicio"
                        type="time"
                        value={novoEvento.hora_inicio}
                        onChange={(e) => setNovoEvento({...novoEvento, hora_inicio: e.target.value})}
                      />
                    </div>
                    <div>
                      <Label htmlFor="hora_fim">Hora Fim</Label>
                      <Input
                        id="hora_fim"
                        type="time"
                        value={novoEvento.hora_fim}
                        onChange={(e) => setNovoEvento({...novoEvento, hora_fim: e.target.value})}
                      />
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <Label htmlFor="local">Local</Label>
                      <Input
                        id="local"
                        value={novoEvento.local}
                        onChange={(e) => setNovoEvento({...novoEvento, local: e.target.value})}
                        placeholder="Nome do local"
                      />
                    </div>
                    <div>
                      <Label htmlFor="endereco">Endereço</Label>
                      <Input
                        id="endereco"
                        value={novoEvento.endereco}
                        onChange={(e) => setNovoEvento({...novoEvento, endereco: e.target.value})}
                        placeholder="Endereço completo"
                      />
                    </div>
                  </div>

                  <div className="grid grid-cols-3 gap-4">
                    <div>
                      <Label htmlFor="cidade">Cidade</Label>
                      <Input
                        id="cidade"
                        value={novoEvento.cidade}
                        onChange={(e) => setNovoEvento({...novoEvento, cidade: e.target.value})}
                        placeholder="Cidade"
                      />
                    </div>
                    <div>
                      <Label htmlFor="estado">Estado</Label>
                      <select
                        id="estado"
                        value={novoEvento.estado}
                        onChange={(e) => setNovoEvento({...novoEvento, estado: e.target.value})}
                        className="w-full border rounded-md px-3 py-2"
                      >
                        <option value="">Selecione</option>
                        <option value="SP">São Paulo</option>
                        <option value="RJ">Rio de Janeiro</option>
                        <option value="MG">Minas Gerais</option>
                        {/* Adicionar outros estados */}
                      </select>
                    </div>
                    <div>
                      <Label htmlFor="cep">CEP</Label>
                      <Input
                        id="cep"
                        value={novoEvento.cep}
                        onChange={(e) => setNovoEvento({...novoEvento, cep: e.target.value})}
                        placeholder="00000-000"
                      />
                    </div>
                  </div>

                  <div className="grid grid-cols-3 gap-4">
                    <div>
                      <Label htmlFor="capacidade_maxima">Capacidade Máxima</Label>
                      <Input
                        id="capacidade_maxima"
                        type="number"
                        value={novoEvento.capacidade_maxima}
                        onChange={(e) => setNovoEvento({...novoEvento, capacidade_maxima: parseInt(e.target.value)})}
                        min="1"
                      />
                    </div>
                    <div>
                      <Label htmlFor="limite_idade">Limite de Idade</Label>
                      <select
                        id="limite_idade"
                        value={novoEvento.limite_idade}
                        onChange={(e) => setNovoEvento({...novoEvento, limite_idade: parseInt(e.target.value)})}
                        className="w-full border rounded-md px-3 py-2"
                      >
                        <option value={0}>Livre</option>
                        <option value={16}>16 anos</option>
                        <option value={18}>18 anos</option>
                        <option value={21}>21 anos</option>
                      </select>
                    </div>
                    <div>
                      <Label htmlFor="tipo_evento">Tipo de Evento</Label>
                      <select
                        id="tipo_evento"
                        value={novoEvento.tipo_evento}
                        onChange={(e) => setNovoEvento({...novoEvento, tipo_evento: e.target.value as any})}
                        className="w-full border rounded-md px-3 py-2"
                      >
                        <option value="festa">Festa</option>
                        <option value="show">Show</option>
                        <option value="conferencia">Conferência</option>
                        <option value="workshop">Workshop</option>
                        <option value="corporativo">Corporativo</option>
                        <option value="outro">Outro</option>
                      </select>
                    </div>
                  </div>
                </TabsContent>

                <TabsContent value="vendas" className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <Label htmlFor="data_inicio_vendas">Início das Vendas</Label>
                      <Input
                        id="data_inicio_vendas"
                        type="datetime-local"
                        value={novoEvento.data_inicio_vendas}
                        onChange={(e) => setNovoEvento({...novoEvento, data_inicio_vendas: e.target.value})}
                      />
                    </div>
                    <div>
                      <Label htmlFor="data_fim_vendas">Fim das Vendas</Label>
                      <Input
                        id="data_fim_vendas"
                        type="datetime-local"
                        value={novoEvento.data_fim_vendas}
                        onChange={(e) => setNovoEvento({...novoEvento, data_fim_vendas: e.target.value})}
                      />
                    </div>
                  </div>

                  <div className="space-y-3">
                    <div className="flex items-center space-x-2">
                      <input
                        type="checkbox"
                        id="vendas_ativas"
                        checked={novoEvento.vendas_ativas}
                        onChange={(e) => setNovoEvento({...novoEvento, vendas_ativas: e.target.checked})}
                        className="rounded"
                      />
                      <Label htmlFor="vendas_ativas">Vendas Ativas</Label>
                    </div>

                    <div className="flex items-center space-x-2">
                      <input
                        type="checkbox"
                        id="permite_lista"
                        checked={novoEvento.permite_lista}
                        onChange={(e) => setNovoEvento({...novoEvento, permite_lista: e.target.checked})}
                        className="rounded"
                      />
                      <Label htmlFor="permite_lista">Permite Lista</Label>
                    </div>

                    <div className="flex items-center space-x-2">
                      <input
                        type="checkbox"
                        id="permite_cortesia"
                        checked={novoEvento.permite_cortesia}
                        onChange={(e) => setNovoEvento({...novoEvento, permite_cortesia: e.target.checked})}
                        className="rounded"
                      />
                      <Label htmlFor="permite_cortesia">Permite Cortesia</Label>
                    </div>

                    <div className="flex items-center space-x-2">
                      <input
                        type="checkbox"
                        id="permite_promocional"
                        checked={novoEvento.permite_promocional}
                        onChange={(e) => setNovoEvento({...novoEvento, permite_promocional: e.target.checked})}
                        className="rounded"
                      />
                      <Label htmlFor="permite_promocional">Permite Promocional</Label>
                    </div>
                  </div>
                </TabsContent>

                <TabsContent value="configuracoes" className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <Label htmlFor="limite_por_cpf">Limite por CPF</Label>
                      <Input
                        id="limite_por_cpf"
                        type="number"
                        value={novoEvento.configuracoes?.limite_por_cpf}
                        onChange={(e) => setNovoEvento({
                          ...novoEvento,
                          configuracoes: {
                            ...novoEvento.configuracoes!,
                            limite_por_cpf: parseInt(e.target.value)
                          }
                        })}
                        min="1"
                      />
                    </div>
                    <div>
                      <Label htmlFor="taxa_conveniencia">Taxa de Conveniência (%)</Label>
                      <Input
                        id="taxa_conveniencia"
                        type="number"
                        value={novoEvento.configuracoes?.taxa_conveniencia}
                        onChange={(e) => setNovoEvento({
                          ...novoEvento,
                          configuracoes: {
                            ...novoEvento.configuracoes!,
                            taxa_conveniencia: parseFloat(e.target.value)
                          }
                        })}
                        min="0"
                        step="0.1"
                      />
                    </div>
                  </div>

                  <div>
                    <Label htmlFor="politica_cancelamento">Política de Cancelamento</Label>
                    <Textarea
                      id="politica_cancelamento"
                      value={novoEvento.configuracoes?.politica_cancelamento}
                      onChange={(e) => setNovoEvento({
                        ...novoEvento,
                        configuracoes: {
                          ...novoEvento.configuracoes!,
                          politica_cancelamento: e.target.value
                        }
                      })}
                      rows={3}
                    />
                  </div>

                  <div className="space-y-3">
                    <div className="flex items-center space-x-2">
                      <input
                        type="checkbox"
                        id="permite_revendas"
                        checked={novoEvento.configuracoes?.permite_revendas}
                        onChange={(e) => setNovoEvento({
                          ...novoEvento,
                          configuracoes: {
                            ...novoEvento.configuracoes!,
                            permite_revendas: e.target.checked
                          }
                        })}
                        className="rounded"
                      />
                      <Label htmlFor="permite_revendas">Permite Revendas</Label>
                    </div>

                    <div className="flex items-center space-x-2">
                      <input
                        type="checkbox"
                        id="exige_validacao_idade"
                        checked={novoEvento.configuracoes?.exige_validacao_idade}
                        onChange={(e) => setNovoEvento({
                          ...novoEvento,
                          configuracoes: {
                            ...novoEvento.configuracoes!,
                            exige_validacao_idade: e.target.checked
                          }
                        })}
                        className="rounded"
                      />
                      <Label htmlFor="exige_validacao_idade">Exige Validação de Idade</Label>
                    </div>

                    <div className="flex items-center space-x-2">
                      <input
                        type="checkbox"
                        id="permite_meia_entrada"
                        checked={novoEvento.configuracoes?.permite_meia_entrada}
                        onChange={(e) => setNovoEvento({
                          ...novoEvento,
                          configuracoes: {
                            ...novoEvento.configuracoes!,
                            permite_meia_entrada: e.target.checked
                          }
                        })}
                        className="rounded"
                      />
                      <Label htmlFor="permite_meia_entrada">Permite Meia Entrada</Label>
                    </div>
                  </div>
                </TabsContent>

                <TabsContent value="design" className="space-y-4">
                  <div className="text-center py-8 text-gray-500">
                    <Image className="w-16 h-16 mx-auto mb-4 text-gray-300" />
                    <p>Funcionalidades de design em desenvolvimento</p>
                    <p className="text-sm">Upload de imagens, cores personalizadas, etc.</p>
                  </div>
                </TabsContent>

                <TabsContent value="integracao" className="space-y-4">
                  <div className="space-y-3">
                    <div className="flex items-center space-x-2">
                      <input
                        type="checkbox"
                        id="integracao_pix"
                        checked={novoEvento.integracao_pix}
                        onChange={(e) => setNovoEvento({...novoEvento, integracao_pix: e.target.checked})}
                        className="rounded"
                      />
                      <Label htmlFor="integracao_pix">Integração PIX</Label>
                    </div>

                    <div className="flex items-center space-x-2">
                      <input
                        type="checkbox"
                        id="whatsapp_ativo"
                        checked={novoEvento.whatsapp_ativo}
                        onChange={(e) => setNovoEvento({...novoEvento, whatsapp_ativo: e.target.checked})}
                        className="rounded"
                      />
                      <Label htmlFor="whatsapp_ativo">WhatsApp Ativo</Label>
                    </div>

                    <div className="flex items-center space-x-2">
                      <input
                        type="checkbox"
                        id="email_confirmacao"
                        checked={novoEvento.email_confirmacao}
                        onChange={(e) => setNovoEvento({...novoEvento, email_confirmacao: e.target.checked})}
                        className="rounded"
                      />
                      <Label htmlFor="email_confirmacao">Email de Confirmação</Label>
                    </div>

                    <div className="flex items-center space-x-2">
                      <input
                        type="checkbox"
                        id="lembrete_automatico"
                        checked={novoEvento.lembrete_automatico}
                        onChange={(e) => setNovoEvento({...novoEvento, lembrete_automatico: e.target.checked})}
                        className="rounded"
                      />
                      <Label htmlFor="lembrete_automatico">Lembrete Automático</Label>
                    </div>
                  </div>
                </TabsContent>
              </Tabs>
            </div>

            <div className="p-6 border-t flex justify-end gap-3">
              <Button variant="outline" onClick={fecharModal}>
                Cancelar
              </Button>
              <Button onClick={salvarEvento}>
                {eventoSelecionado ? 'Atualizar' : 'Criar'} Evento
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default EventosMEEPModule;
