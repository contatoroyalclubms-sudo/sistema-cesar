import React, { useState, useEffect } from 'react';
import { 
  Plus, Edit, Trash2, Star, MessageSquare, QrCode, 
  ExternalLink, BarChart3, Users, TrendingUp, Download 
} from 'lucide-react';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '../ui/card';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Label } from '../ui/label';
import { Switch } from '../ui/switch';
import { Badge } from '../ui/badge';
import { Textarea } from '../ui/textarea';
import { Progress } from '../ui/progress';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '../ui/dialog';
import {
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
} from '../ui/tabs';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '../ui/select';
import { toast } from 'sonner';
import api from '../../lib/api';

interface PesquisaSatisfacao {
  id: number;
  evento_id?: number;
  titulo: string;
  descricao?: string;
  tipo_integracao?: string;
  url_pesquisa?: string;
  qr_code?: string;
  configuracoes?: any;
  ativa: boolean;
  data_inicio?: string;
  data_fim?: string;
  total_respostas: number;
  nota_media?: number;
  criado_em: string;
}

interface ParceiroIntegracao {
  id: string;
  nome: string;
  descricao: string;
  icone: string;
  status: string;
  recursos: string[];
}

const PesquisaSatisfacaoModule: React.FC = () => {
  const [pesquisas, setPesquisas] = useState<PesquisaSatisfacao[]>([]);
  const [parceiros, setParceiros] = useState<ParceiroIntegracao[]>([]);
  const [loading, setLoading] = useState(false);
  const [showModal, setShowModal] = useState(false);
  const [showStatsModal, setShowStatsModal] = useState(false);
  const [editingPesquisa, setEditingPesquisa] = useState<PesquisaSatisfacao | null>(null);
  const [selectedPesquisa, setSelectedPesquisa] = useState<PesquisaSatisfacao | null>(null);
  const [estatisticas, setEstatisticas] = useState<any>(null);
  const [activeTab, setActiveTab] = useState('pesquisas');
  
  const [formData, setFormData] = useState({
    titulo: '',
    descricao: '',
    tipo_integracao: 'interno',
    url_pesquisa: '',
    configuracoes: {},
    ativa: true,
    data_inicio: '',
    data_fim: '',
    evento_id: null as number | null
  });

  useEffect(() => {
    fetchPesquisas();
    fetchParceiros();
  }, []);

  const fetchPesquisas = async () => {
    setLoading(true);
    try {
      const response = await api.get('/pesquisas-satisfacao');
      setPesquisas(response.data);
    } catch (error) {
      console.error('Erro ao buscar pesquisas:', error);
      toast.error('Erro ao carregar pesquisas');
    } finally {
      setLoading(false);
    }
  };

  const fetchParceiros = async () => {
    try {
      const response = await api.get('/pesquisas-satisfacao/integracao/parceiros');
      setParceiros(response.data);
    } catch (error) {
      console.error('Erro ao buscar parceiros:', error);
    }
  };

  const fetchEstatisticas = async (pesquisaId: number) => {
    try {
      const response = await api.get(`/pesquisas-satisfacao/${pesquisaId}/estatisticas`);
      setEstatisticas(response.data);
      setShowStatsModal(true);
    } catch (error) {
      console.error('Erro ao buscar estatísticas:', error);
      toast.error('Erro ao carregar estatísticas');
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    try {
      if (editingPesquisa) {
        await api.put(`/pesquisas-satisfacao/${editingPesquisa.id}`, formData);
        toast.success('Pesquisa atualizada com sucesso!');
      } else {
        await api.post('/pesquisas-satisfacao', formData);
        toast.success('Pesquisa criada com sucesso!');
      }
      
      setShowModal(false);
      resetForm();
      fetchPesquisas();
    } catch (error: any) {
      console.error('Erro ao salvar pesquisa:', error);
      toast.error(error.response?.data?.detail || 'Erro ao salvar pesquisa');
    }
  };

  const handleEdit = (pesquisa: PesquisaSatisfacao) => {
    setEditingPesquisa(pesquisa);
    setFormData({
      titulo: pesquisa.titulo,
      descricao: pesquisa.descricao || '',
      tipo_integracao: pesquisa.tipo_integracao || 'interno',
      url_pesquisa: pesquisa.url_pesquisa || '',
      configuracoes: pesquisa.configuracoes || {},
      ativa: pesquisa.ativa,
      data_inicio: pesquisa.data_inicio || '',
      data_fim: pesquisa.data_fim || '',
      evento_id: pesquisa.evento_id || null
    });
    setShowModal(true);
  };

  const handleDelete = async (id: number) => {
    if (!confirm('Tem certeza que deseja desativar esta pesquisa?')) return;
    
    try {
      await api.delete(`/pesquisas-satisfacao/${id}`);
      toast.success('Pesquisa desativada com sucesso!');
      fetchPesquisas();
    } catch (error: any) {
      console.error('Erro ao desativar pesquisa:', error);
      toast.error(error.response?.data?.detail || 'Erro ao desativar pesquisa');
    }
  };

  const resetForm = () => {
    setEditingPesquisa(null);
    setFormData({
      titulo: '',
      descricao: '',
      tipo_integracao: 'interno',
      url_pesquisa: '',
      configuracoes: {},
      ativa: true,
      data_inicio: '',
      data_fim: '',
      evento_id: null
    });
  };

  const renderStars = (nota: number) => {
    const stars = [];
    for (let i = 1; i <= 10; i++) {
      stars.push(
        <Star 
          key={i}
          className={`h-4 w-4 ${i <= nota ? 'fill-yellow-400 text-yellow-400' : 'text-gray-300'}`}
        />
      );
    }
    return <div className="flex gap-0.5">{stars}</div>;
  };

  return (
    <div className="p-6 space-y-6">
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid grid-cols-2 w-[400px]">
          <TabsTrigger value="pesquisas">Pesquisas Ativas</TabsTrigger>
          <TabsTrigger value="parceiros">Integrações</TabsTrigger>
        </TabsList>

        <TabsContent value="pesquisas" className="space-y-4">
          <Card>
            <CardHeader>
              <div className="flex justify-between items-center">
                <div>
                  <CardTitle>Pesquisas de Satisfação</CardTitle>
                  <CardDescription>
                    Colete informações valiosas diretamente dos seus clientes
                  </CardDescription>
                </div>
                <Button onClick={() => setShowModal(true)}>
                  <Plus className="h-4 w-4 mr-2" />
                  Nova Pesquisa
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              {loading ? (
                <div className="text-center py-8">Carregando...</div>
              ) : (
                <div className="grid gap-4">
                  {pesquisas.map((pesquisa) => (
                    <Card key={pesquisa.id}>
                      <CardContent className="p-6">
                        <div className="flex justify-between items-start">
                          <div className="flex-1">
                            <div className="flex items-center gap-2 mb-2">
                              <h3 className="text-lg font-semibold">{pesquisa.titulo}</h3>
                              <Badge variant={pesquisa.ativa ? 'success' : 'secondary'}>
                                {pesquisa.ativa ? 'Ativa' : 'Inativa'}
                              </Badge>
                              {pesquisa.tipo_integracao && (
                                <Badge variant="outline">{pesquisa.tipo_integracao}</Badge>
                              )}
                            </div>
                            
                            {pesquisa.descricao && (
                              <p className="text-sm text-muted-foreground mb-4">
                                {pesquisa.descricao}
                              </p>
                            )}

                            <div className="grid grid-cols-4 gap-4 mb-4">
                              <div>
                                <p className="text-sm text-muted-foreground">Total Respostas</p>
                                <p className="text-xl font-semibold">{pesquisa.total_respostas}</p>
                              </div>
                              <div>
                                <p className="text-sm text-muted-foreground">Nota Média</p>
                                {pesquisa.nota_media ? (
                                  <div>
                                    <p className="text-xl font-semibold">{pesquisa.nota_media}/10</p>
                                    {renderStars(Math.round(pesquisa.nota_media))}
                                  </div>
                                ) : (
                                  <p className="text-xl font-semibold">-</p>
                                )}
                              </div>
                              <div>
                                <p className="text-sm text-muted-foreground">Período</p>
                                <p className="text-sm">
                                  {pesquisa.data_inicio ? new Date(pesquisa.data_inicio).toLocaleDateString() : 'Sem início'} - 
                                  {pesquisa.data_fim ? new Date(pesquisa.data_fim).toLocaleDateString() : 'Sem fim'}
                                </p>
                              </div>
                              <div>
                                <p className="text-sm text-muted-foreground">Criada em</p>
                                <p className="text-sm">{new Date(pesquisa.criado_em).toLocaleDateString()}</p>
                              </div>
                            </div>

                            {pesquisa.url_pesquisa && (
                              <div className="flex items-center gap-2 mb-2">
                                <ExternalLink className="h-4 w-4 text-muted-foreground" />
                                <a 
                                  href={pesquisa.url_pesquisa} 
                                  target="_blank" 
                                  rel="noopener noreferrer"
                                  className="text-sm text-primary hover:underline"
                                >
                                  {pesquisa.url_pesquisa}
                                </a>
                              </div>
                            )}
                          </div>

                          <div className="flex gap-2">
                            {pesquisa.qr_code && (
                              <Dialog>
                                <DialogTrigger asChild>
                                  <Button size="sm" variant="outline">
                                    <QrCode className="h-4 w-4" />
                                  </Button>
                                </DialogTrigger>
                                <DialogContent>
                                  <DialogHeader>
                                    <DialogTitle>QR Code da Pesquisa</DialogTitle>
                                  </DialogHeader>
                                  <div className="flex justify-center p-4">
                                    <img src={pesquisa.qr_code} alt="QR Code" className="max-w-xs" />
                                  </div>
                                </DialogContent>
                              </Dialog>
                            )}
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => fetchEstatisticas(pesquisa.id)}
                            >
                              <BarChart3 className="h-4 w-4" />
                            </Button>
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => handleEdit(pesquisa)}
                            >
                              <Edit className="h-4 w-4" />
                            </Button>
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => handleDelete(pesquisa.id)}
                            >
                              <Trash2 className="h-4 w-4" />
                            </Button>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="parceiros" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Parceiros de Integração</CardTitle>
              <CardDescription>
                Você está pronto para transformar a voz dos seus clientes em oportunidades de crescimento? 
                Integre com nossos parceiros e colete informações valiosas.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid gap-4">
                {parceiros.map((parceiro) => (
                  <Card key={parceiro.id}>
                    <CardContent className="p-6">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-2">
                            <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center">
                              {parceiro.icone === 'crown' && '👑'}
                              {parceiro.icone === 'description' && '📝'}
                              {parceiro.icone === 'poll' && '📊'}
                            </div>
                            <div>
                              <h3 className="font-semibold">{parceiro.nome}</h3>
                              <Badge variant={parceiro.status === 'ativo' ? 'success' : 'secondary'}>
                                {parceiro.status === 'ativo' ? 'Ativo' : 'Disponível'}
                              </Badge>
                            </div>
                          </div>
                          
                          <p className="text-sm text-muted-foreground mb-3">
                            {parceiro.descricao}
                          </p>
                          
                          <div className="space-y-1">
                            {parceiro.recursos.map((recurso, index) => (
                              <div key={index} className="flex items-center gap-2">
                                <div className="w-1.5 h-1.5 rounded-full bg-primary" />
                                <span className="text-sm">{recurso}</span>
                              </div>
                            ))}
                          </div>
                        </div>
                        
                        <Button variant={parceiro.status === 'ativo' ? 'default' : 'outline'}>
                          {parceiro.status === 'ativo' ? 'Configurar' : 'Integrar'}
                        </Button>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Modal de Formulário */}
      <Dialog open={showModal} onOpenChange={setShowModal}>
        <DialogContent className="max-w-2xl">
          <form onSubmit={handleSubmit}>
            <DialogHeader>
              <DialogTitle>
                {editingPesquisa ? 'Editar Pesquisa' : 'Nova Pesquisa de Satisfação'}
              </DialogTitle>
              <DialogDescription>
                Configure os detalhes da pesquisa de satisfação
              </DialogDescription>
            </DialogHeader>

            <div className="grid gap-4 py-4">
              <div className="space-y-2">
                <Label htmlFor="titulo">Título*</Label>
                <Input
                  id="titulo"
                  required
                  value={formData.titulo}
                  onChange={(e) => setFormData({ ...formData, titulo: e.target.value })}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="descricao">Descrição</Label>
                <Textarea
                  id="descricao"
                  value={formData.descricao}
                  onChange={(e) => setFormData({ ...formData, descricao: e.target.value })}
                  rows={3}
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="tipo">Tipo de Integração</Label>
                  <Select
                    value={formData.tipo_integracao}
                    onValueChange={(value) => setFormData({ ...formData, tipo_integracao: value })}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="interno">Sistema Interno</SelectItem>
                      <SelectItem value="track.co">Track.co</SelectItem>
                      <SelectItem value="google_forms">Google Forms</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="url">URL da Pesquisa</Label>
                  <Input
                    id="url"
                    type="url"
                    value={formData.url_pesquisa}
                    onChange={(e) => setFormData({ ...formData, url_pesquisa: e.target.value })}
                    placeholder="https://..."
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="data_inicio">Data de Início</Label>
                  <Input
                    id="data_inicio"
                    type="datetime-local"
                    value={formData.data_inicio}
                    onChange={(e) => setFormData({ ...formData, data_inicio: e.target.value })}
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="data_fim">Data de Fim</Label>
                  <Input
                    id="data_fim"
                    type="datetime-local"
                    value={formData.data_fim}
                    onChange={(e) => setFormData({ ...formData, data_fim: e.target.value })}
                  />
                </div>
              </div>

              <div className="flex items-center justify-between space-x-2">
                <Label htmlFor="ativa">Pesquisa Ativa</Label>
                <Switch
                  id="ativa"
                  checked={formData.ativa}
                  onCheckedChange={(checked) => setFormData({ ...formData, ativa: checked })}
                />
              </div>
            </div>

            <DialogFooter>
              <Button type="button" variant="outline" onClick={() => setShowModal(false)}>
                Cancelar
              </Button>
              <Button type="submit">
                {editingPesquisa ? 'Atualizar' : 'Criar'} Pesquisa
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>

      {/* Modal de Estatísticas */}
      <Dialog open={showStatsModal} onOpenChange={setShowStatsModal}>
        <DialogContent className="max-w-4xl">
          <DialogHeader>
            <DialogTitle>Estatísticas da Pesquisa</DialogTitle>
          </DialogHeader>
          
          {estatisticas && (
            <div className="space-y-4">
              <div className="grid grid-cols-4 gap-4">
                <Card>
                  <CardContent className="p-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm text-muted-foreground">Total Respostas</p>
                        <p className="text-2xl font-bold">{estatisticas.estatisticas.total_respostas}</p>
                      </div>
                      <MessageSquare className="h-8 w-8 text-muted-foreground" />
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardContent className="p-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm text-muted-foreground">Nota Média</p>
                        <p className="text-2xl font-bold">{estatisticas.estatisticas.nota_media.toFixed(1)}/10</p>
                      </div>
                      <Star className="h-8 w-8 text-yellow-400" />
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardContent className="p-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm text-muted-foreground">NPS Score</p>
                        <p className="text-2xl font-bold">{estatisticas.estatisticas.nps}%</p>
                      </div>
                      <TrendingUp className="h-8 w-8 text-green-500" />
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardContent className="p-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm text-muted-foreground">Comentários</p>
                        <p className="text-2xl font-bold">{estatisticas.estatisticas.total_comentarios}</p>
                      </div>
                      <MessageSquare className="h-8 w-8 text-blue-500" />
                    </div>
                  </CardContent>
                </Card>
              </div>

              <Card>
                <CardHeader>
                  <CardTitle>Distribuição de Notas</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    {Object.entries(estatisticas.estatisticas.distribuicao_notas).map(([nota, count]) => (
                      <div key={nota} className="flex items-center gap-4">
                        <span className="w-8 text-sm font-medium">{nota}</span>
                        <Progress 
                          value={(count as number / estatisticas.estatisticas.total_respostas) * 100} 
                          className="flex-1"
                        />
                        <span className="w-12 text-sm text-muted-foreground">{count}</span>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default PesquisaSatisfacaoModule;