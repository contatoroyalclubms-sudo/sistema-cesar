import React, { useState, useEffect } from 'react';
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { Switch } from "@/components/ui/switch";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Calendar, MapPin, Users, DollarSign, Eye, Share2, BarChart3, Plus, Edit, Save, Upload, Link } from 'lucide-react';
import { toast } from 'sonner';

// Interfaces MEEP
interface EventoMEEP {
  id?: number;
  nome: string;
  descricao?: string;
  data_inicio: string;
  data_fim?: string;
  local?: string;
  endereco?: string;
  categoria: string;
  tipo: string;
  capacidade_maxima?: number;
  preco_base: number;
  imagem_url?: string;
  publicado: boolean;
  lotes: LoteEvento[];
  configuracao?: ConfiguracaoEvento;
  analytics?: AnalyticsEvento;
}

interface LoteEvento {
  id?: number;
  nome: string;
  quantidade: number;
  preco: number;
  descricao?: string;
  vendas_inicio?: string;
  vendas_fim?: string;
  vendidos: number;
  ativo: boolean;
}

interface ConfiguracaoEvento {
  confirmacao_email: boolean;
  confirmacao_sms: boolean;
  compartilhamento_social: boolean;
  desconto_promocional: boolean;
  codigo_desconto?: string;
  percentual_desconto: number;
  limite_ingressos_pessoa: number;
  venda_no_local: boolean;
  meia_entrada: boolean;
  taxa_servico: number;
}

interface AnalyticsEvento {
  visualizacoes: number;
  compartilhamentos: number;
  conversao_vendas: number;
  receita_total: number;
  tickets_vendidos: number;
  data_atualizacao: string;
}

};

const eventoInicial: EventoMEEP = {
  nome: '',
  descricao: '',
  data_inicio: '',
  data_fim: '',
  local: '',
  endereco: '',
  categoria: 'Geral',
  tipo: 'presencial',
  capacidade_maxima: 100,
  preco_base: 0,
  publicado: false,
  lotes: [],
  configuracao: {
    confirmacao_email: true,
    confirmacao_sms: false,
    compartilhamento_social: true,
    desconto_promocional: false,
    percentual_desconto: 0,
    limite_ingressos_pessoa: 10,
    venda_no_local: false,
    meia_entrada: true,
    taxa_servico: 5.0
  }
};

export default function EventosMEEPModule() {
  const [eventos, setEventos] = useState<EventoMEEP[]>([]);
  const [eventoSelecionado, setEventoSelecionado] = useState<EventoMEEP>(eventoInicial);
  const [modalAberto, setModalAberto] = useState(false);
  const [modoEdicao, setModoEdicao] = useState(false);
  const [loading, setLoading] = useState(false);

  // Dados demo para demonstração
  useEffect(() => {
    const eventosDemo: EventoMEEP[] = [
      {
        id: 1,
        nome: 'Festival de Música Eletrônica MEEP',
        descricao: 'Uma noite inesquecível com os melhores DJs',
        data_inicio: '2024-02-15T20:00',
        data_fim: '2024-02-16T06:00',
        local: 'Espaço das Américas',
        endereco: 'Rua Tagipuru, 795 - São Paulo',
        categoria: 'Música',
        tipo: 'presencial',
        capacidade_maxima: 2000,
        preco_base: 80.00,
        publicado: true,
        lotes: [
          {
            id: 1,
            nome: '1º Lote',
            quantidade: 500,
            preco: 60.00,
            vendidos: 450,
            ativo: false
          },
          {
            id: 2,
            nome: '2º Lote',
            quantidade: 800,
            preco: 80.00,
            vendidos: 320,
            ativo: true
          }
        ],
        configuracao: {
          confirmacao_email: true,
          confirmacao_sms: true,
          compartilhamento_social: true,
          desconto_promocional: true,
          codigo_desconto: 'MUSIC10',
          percentual_desconto: 10,
          limite_ingressos_pessoa: 6,
          venda_no_local: true,
          meia_entrada: true,
          taxa_servico: 5.0
        },
        analytics: {
          visualizacoes: 15420,
          compartilhamentos: 342,
          conversao_vendas: 5.2,
          receita_total: 52800.00,
          tickets_vendidos: 770,
          data_atualizacao: '2024-01-15T14:30:00'
        }
      }
    ];
    
    setEventos(eventosDemo);
  }, []);

  // Salvar evento
  const salvarEvento = async () => {
    try {
      setLoading(true);
      
      // Simular chamada API
      if (modoEdicao) {
        setEventos(prev => prev.map(e => e.id === eventoSelecionado.id ? eventoSelecionado : e));
        toast.success('Evento atualizado com sucesso!');
      } else {
        const novoEvento = { 
          ...eventoSelecionado, 
          id: Date.now(),
          analytics: {
            visualizacoes: 0,
            compartilhamentos: 0,
            conversao_vendas: 0,
            receita_total: 0,
            tickets_vendidos: 0,
            data_atualizacao: new Date().toISOString()
          }
        };
        setEventos(prev => [...prev, novoEvento]);
        toast.success('Evento criado com sucesso!');
      }
      
      setModalAberto(false);
      setEventoSelecionado(eventoInicial);
      setModoEdicao(false);
    } catch (error) {
      console.error('Erro:', error);
      toast.error('Erro ao salvar evento');
    } finally {
      setLoading(false);
    }
  };

  const categorias = [
    'Música', 'Teatro', 'Esportes', 'Tecnologia', 'Gastronomia',
    'Arte', 'Educação', 'Negócios', 'Saúde', 'Turismo', 'Religioso', 'Geral'
  ];

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Eventos MEEP</h1>
          <p className="text-gray-600">Sistema completo de gestão de eventos nível MEEP</p>
        </div>
        
        <Dialog open={modalAberto} onOpenChange={setModalAberto}>
          <DialogTrigger asChild>
            <Button 
              onClick={() => {
                setEventoSelecionado(eventoInicial);
                setModoEdicao(false);
              }}
              className="bg-blue-600 hover:bg-blue-700"
            >
              <Plus className="w-4 h-4 mr-2" />
              Novo Evento MEEP
            </Button>
          </DialogTrigger>
          
          <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
            <DialogHeader>
              <DialogTitle>
                {modoEdicao ? 'Editar Evento MEEP' : 'Novo Evento MEEP'}
              </DialogTitle>
            </DialogHeader>

            <Tabs defaultValue="geral" className="w-full">
              <TabsList className="grid w-full grid-cols-5">
                <TabsTrigger value="geral">Geral</TabsTrigger>
                <TabsTrigger value="vendas">Vendas</TabsTrigger>
                <TabsTrigger value="configuracoes">Configurações</TabsTrigger>
                <TabsTrigger value="design">Design</TabsTrigger>
                <TabsTrigger value="integracao">Integração</TabsTrigger>
              </TabsList>

              {/* Tab Geral */}
              <TabsContent value="geral" className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="nome">Nome do Evento *</Label>
                    <Input
                      id="nome"
                      value={eventoSelecionado.nome}
                      onChange={(e) => setEventoSelecionado(prev => ({ ...prev, nome: e.target.value }))}
                      placeholder="Digite o nome do evento"
                    />
                  </div>
                  
                  <div>
                    <Label htmlFor="categoria">Categoria</Label>
                    <Select 
                      value={eventoSelecionado.categoria} 
                      onValueChange={(value) => setEventoSelecionado(prev => ({ ...prev, categoria: value }))}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Selecione uma categoria" />
                      </SelectTrigger>
                      <SelectContent>
                        {categorias.map(cat => (
                          <SelectItem key={cat} value={cat}>{cat}</SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                </div>

                <div>
                  <Label htmlFor="descricao">Descrição</Label>
                  <Textarea
                    id="descricao"
                    value={eventoSelecionado.descricao || ''}
                    onChange={(e) => setEventoSelecionado(prev => ({ ...prev, descricao: e.target.value }))}
                    placeholder="Descrição detalhada do evento"
                    rows={3}
                  />
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="data_inicio">Data de Início *</Label>
                    <Input
                      id="data_inicio"
                      type="datetime-local"
                      value={eventoSelecionado.data_inicio}
                      onChange={(e) => setEventoSelecionado(prev => ({ ...prev, data_inicio: e.target.value }))}
                    />
                  </div>
                  
                  <div>
                    <Label htmlFor="data_fim">Data de Fim</Label>
                    <Input
                      id="data_fim"
                      type="datetime-local"
                      value={eventoSelecionado.data_fim || ''}
                      onChange={(e) => setEventoSelecionado(prev => ({ ...prev, data_fim: e.target.value }))}
                    />
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="local">Local</Label>
                    <Input
                      id="local"
                      value={eventoSelecionado.local || ''}
                      onChange={(e) => setEventoSelecionado(prev => ({ ...prev, local: e.target.value }))}
                      placeholder="Nome do local"
                    />
                  </div>
                  
                  <div>
                    <Label htmlFor="endereco">Endereço</Label>
                    <Input
                      id="endereco"
                      value={eventoSelecionado.endereco || ''}
                      onChange={(e) => setEventoSelecionado(prev => ({ ...prev, endereco: e.target.value }))}
                      placeholder="Endereço completo"
                    />
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="capacidade">Capacidade Máxima</Label>
                    <Input
                      id="capacidade"
                      type="number"
                      value={eventoSelecionado.capacidade_maxima || ''}
                      onChange={(e) => setEventoSelecionado(prev => ({ ...prev, capacidade_maxima: parseInt(e.target.value) || 0 }))}
                      placeholder="Número máximo de participantes"
                    />
                  </div>
                  
                  <div>
                    <Label htmlFor="preco_base">Preço Base (R$)</Label>
                    <Input
                      id="preco_base"
                      type="number"
                      step="0.01"
                      value={eventoSelecionado.preco_base}
                      onChange={(e) => setEventoSelecionado(prev => ({ ...prev, preco_base: parseFloat(e.target.value) || 0 }))}
                      placeholder="0.00"
                    />
                  </div>
                </div>

                <div className="flex items-center space-x-2">
                  <Switch
                    id="publicado"
                    checked={eventoSelecionado.publicado}
                    onCheckedChange={(checked) => setEventoSelecionado(prev => ({ ...prev, publicado: checked }))}
                  />
                  <Label htmlFor="publicado">Publicar evento</Label>
                </div>
              </TabsContent>

              {/* Tab Vendas */}
              <TabsContent value="vendas" className="space-y-4">
                <div className="flex justify-between items-center">
                  <h3 className="text-lg font-semibold">Lotes de Venda</h3>
                  <Button size="sm" variant="outline">
                    <Plus className="w-4 h-4 mr-2" />
                    Adicionar Lote
                  </Button>
                </div>
                
                <Card>
                  <CardContent className="p-6">
                    <p className="text-gray-500 text-center">
                      Configure os lotes de venda para controlar preços e disponibilidade por período.
                    </p>
                  </CardContent>
                </Card>
              </TabsContent>

              {/* Tab Configurações */}
              <TabsContent value="configuracoes" className="space-y-4">
                <div className="space-y-4">
                  <h3 className="text-lg font-semibold">Configurações Avançadas</h3>
                  
                  <div className="grid grid-cols-2 gap-6">
                    <div className="space-y-4">
                      <div className="flex items-center justify-between">
                        <Label>Confirmação por E-mail</Label>
                        <Switch 
                          checked={eventoSelecionado.configuracao?.confirmacao_email}
                          onCheckedChange={(checked) => setEventoSelecionado(prev => ({
                            ...prev,
                            configuracao: { ...prev.configuracao!, confirmacao_email: checked }
                          }))}
                        />
                      </div>
                      
                      <div className="flex items-center justify-between">
                        <Label>Confirmação por SMS</Label>
                        <Switch 
                          checked={eventoSelecionado.configuracao?.confirmacao_sms}
                          onCheckedChange={(checked) => setEventoSelecionado(prev => ({
                            ...prev,
                            configuracao: { ...prev.configuracao!, confirmacao_sms: checked }
                          }))}
                        />
                      </div>
                      
                      <div className="flex items-center justify-between">
                        <Label>Compartilhamento Social</Label>
                        <Switch 
                          checked={eventoSelecionado.configuracao?.compartilhamento_social}
                          onCheckedChange={(checked) => setEventoSelecionado(prev => ({
                            ...prev,
                            configuracao: { ...prev.configuracao!, compartilhamento_social: checked }
                          }))}
                        />
                      </div>
                      
                      <div className="flex items-center justify-between">
                        <Label>Meia Entrada</Label>
                        <Switch 
                          checked={eventoSelecionado.configuracao?.meia_entrada}
                          onCheckedChange={(checked) => setEventoSelecionado(prev => ({
                            ...prev,
                            configuracao: { ...prev.configuracao!, meia_entrada: checked }
                          }))}
                        />
                      </div>
                    </div>
                    
                    <div className="space-y-4">
                      <div>
                        <Label>Limite de Ingressos por Pessoa</Label>
                        <Input
                          type="number"
                          value={eventoSelecionado.configuracao?.limite_ingressos_pessoa}
                          onChange={(e) => setEventoSelecionado(prev => ({
                            ...prev,
                            configuracao: { ...prev.configuracao!, limite_ingressos_pessoa: parseInt(e.target.value) || 10 }
                          }))}
                        />
                      </div>
                      
                      <div>
                        <Label>Taxa de Serviço (%)</Label>
                        <Input
                          type="number"
                          step="0.1"
                          value={eventoSelecionado.configuracao?.taxa_servico}
                          onChange={(e) => setEventoSelecionado(prev => ({
                            ...prev,
                            configuracao: { ...prev.configuracao!, taxa_servico: parseFloat(e.target.value) || 5.0 }
                          }))}
                        />
                      </div>
                    </div>
                  </div>
                </div>
              </TabsContent>

              {/* Tab Design */}
              <TabsContent value="design" className="space-y-4">
                <div className="space-y-4">
                  <h3 className="text-lg font-semibold">Design e Personalização</h3>
                  
                  <div>
                    <Label>Imagem Principal do Evento</Label>
                    <div className="mt-2 border-2 border-dashed border-gray-300 rounded-lg p-6 text-center">
                      <Upload className="mx-auto h-12 w-12 text-gray-400" />
                      <div className="mt-2">
                        <Button variant="outline" size="sm">
                          Upload da Imagem
                        </Button>
                      </div>
                      <p className="text-sm text-gray-500 mt-2">
                        PNG, JPG até 10MB
                      </p>
                    </div>
                  </div>
                </div>
              </TabsContent>

              {/* Tab Integração */}
              <TabsContent value="integracao" className="space-y-4">
                <div className="space-y-4">
                  <h3 className="text-lg font-semibold">Integrações e APIs</h3>
                  
                  <Card>
                    <CardHeader>
                      <CardTitle className="flex items-center text-base">
                        <Link className="w-4 h-4 mr-2" />
                        Link de Compartilhamento
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <Input 
                        value={`https://seusite.com/evento/${eventoSelecionado.id}`} 
                        readOnly 
                      />
                    </CardContent>
                  </Card>
                </div>
              </TabsContent>
            </Tabs>

            <div className="flex justify-end space-x-2 pt-4 border-t">
              <Button variant="outline" onClick={() => setModalAberto(false)}>
                Cancelar
              </Button>
              <Button onClick={salvarEvento} disabled={loading}>
                <Save className="w-4 h-4 mr-2" />
                {loading ? 'Salvando...' : 'Salvar Evento'}
              </Button>
            </div>
          </DialogContent>
        </Dialog>
      </div>

      {/* Lista de Eventos */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {eventos.length === 0 ? (
          <div className="col-span-full text-center py-8 text-gray-500">
            Nenhum evento encontrado. Crie seu primeiro evento MEEP!
          </div>
        ) : (
          eventos.map((evento) => (
            <Card key={evento.id} className="hover:shadow-lg transition-shadow">
              <CardHeader>
                <div className="flex justify-between items-start">
                  <div>
                    <CardTitle className="text-lg">{evento.nome}</CardTitle>
                    <Badge variant={evento.publicado ? "default" : "secondary"}>
                      {evento.publicado ? "Publicado" : "Rascunho"}
                    </Badge>
                  </div>
                  <div className="flex space-x-1">
                    <Button size="sm" variant="ghost">
                      <Eye className="w-4 h-4" />
                    </Button>
                    <Button size="sm" variant="ghost" onClick={() => {
                      setEventoSelecionado(evento);
                      setModoEdicao(true);
                      setModalAberto(true);
                    }}>
                      <Edit className="w-4 h-4" />
                    </Button>
                  </div>
                </div>
              </CardHeader>
              
              <CardContent className="space-y-3">
                <div className="flex items-center text-sm text-gray-600">
                  <Calendar className="w-4 h-4 mr-2" />
                  {new Date(evento.data_inicio).toLocaleDateString('pt-BR')}
                </div>
                
                {evento.local && (
                  <div className="flex items-center text-sm text-gray-600">
                    <MapPin className="w-4 h-4 mr-2" />
                    {evento.local}
                  </div>
                )}
                
                <div className="flex items-center text-sm text-gray-600">
                  <DollarSign className="w-4 h-4 mr-2" />
                  R$ {evento.preco_base.toFixed(2)}
                </div>
                
                {evento.capacidade_maxima && (
                  <div className="flex items-center text-sm text-gray-600">
                    <Users className="w-4 h-4 mr-2" />
                    {evento.capacidade_maxima} vagas
                  </div>
                )}
                
                <Separator />
                
                <div className="flex justify-between items-center">
                  <div className="flex space-x-1">
                    <Button size="sm" variant="outline">
                      <Share2 className="w-4 h-4" />
                    </Button>
                    <Button size="sm" variant="outline">
                      <BarChart3 className="w-4 h-4" />
                    </Button>
                  </div>
                  
                  <Badge variant="outline">
                    {evento.categoria}
                  </Badge>
                </div>
              </CardContent>
            </Card>
          ))
        )}
      </div>
    </div>
  );
}
