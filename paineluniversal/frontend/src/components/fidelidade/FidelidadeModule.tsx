import React, { useState, useEffect } from 'react';
import { 
  Trophy, Plus, Edit, Trash2, Users, Gift, 
  TrendingUp, Award, Star, Coins, Crown
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
import { Progress } from '../ui/progress';
import { Textarea } from '../ui/textarea';
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
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '../ui/table';
import { toast } from 'sonner';
import api from '../../lib/api';

interface ProgramaFidelidade {
  id: number;
  nome: string;
  descricao?: string;
  tipo_programa?: string;
  ativo: boolean;
  criado_em: string;
  total_participantes?: number;
}

interface NivelFidelidade {
  id: number;
  programa_id: number;
  nome: string;
  pontos_minimos: number;
  pontos_maximos?: number;
  cor?: string;
  icone?: string;
  beneficios?: any;
  desconto_percentual?: number;
  multiplicador_pontos: number;
  ordem: number;
}

interface ParticipanteFidelidade {
  id: number;
  programa_id: number;
  cliente_id: number;
  nivel_atual_id?: number;
  pontos_totais: number;
  pontos_disponiveis: number;
  data_adesao: string;
  data_ultima_movimentacao?: string;
  nivel_atual?: NivelFidelidade;
}

const FidelidadeModule: React.FC = () => {
  const [programas, setProgramas] = useState<ProgramaFidelidade[]>([]);
  const [niveis, setNiveis] = useState<NivelFidelidade[]>([]);
  const [estatisticas, setEstatisticas] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('programas');
  const [showProgramaModal, setShowProgramaModal] = useState(false);
  const [showNivelModal, setShowNivelModal] = useState(false);
  const [showPontosModal, setShowPontosModal] = useState(false);
  const [selectedPrograma, setSelectedPrograma] = useState<ProgramaFidelidade | null>(null);
  const [editingPrograma, setEditingPrograma] = useState<ProgramaFidelidade | null>(null);
  const [editingNivel, setEditingNivel] = useState<NivelFidelidade | null>(null);
  
  const [formPrograma, setFormPrograma] = useState({
    nome: '',
    descricao: '',
    tipo_programa: 'pontos',
    ativo: true
  });

  const [formNivel, setFormNivel] = useState({
    nome: '',
    pontos_minimos: 0,
    pontos_maximos: null as number | null,
    cor: '#3B82F6',
    icone: 'star',
    beneficios: {},
    desconto_percentual: 0,
    multiplicador_pontos: 1,
    ordem: 0
  });

  const [formPontos, setFormPontos] = useState({
    participante_id: 0,
    tipo: 'credito',
    pontos: 0,
    descricao: '',
    referencia_tipo: 'manual'
  });

  useEffect(() => {
    fetchProgramas();
  }, []);

  const fetchProgramas = async () => {
    setLoading(true);
    try {
      const response = await api.get('/fidelidade/programas');
      setProgramas(response.data);
    } catch (error) {
      console.error('Erro ao buscar programas:', error);
      toast.error('Erro ao carregar programas de fidelidade');
    } finally {
      setLoading(false);
    }
  };

  const fetchNiveis = async (programaId: number) => {
    try {
      const response = await api.get(`/fidelidade/programas/${programaId}/niveis`);
      setNiveis(response.data);
    } catch (error) {
      console.error('Erro ao buscar níveis:', error);
      toast.error('Erro ao carregar níveis');
    }
  };

  const fetchEstatisticas = async (programaId: number) => {
    try {
      const response = await api.get(`/fidelidade/estatisticas/${programaId}`);
      setEstatisticas(response.data);
    } catch (error) {
      console.error('Erro ao buscar estatísticas:', error);
      toast.error('Erro ao carregar estatísticas');
    }
  };

  const handleSubmitPrograma = async (e: React.FormEvent) => {
    e.preventDefault();
    
    try {
      if (editingPrograma) {
        await api.put(`/fidelidade/programas/${editingPrograma.id}`, formPrograma);
        toast.success('Programa atualizado com sucesso!');
      } else {
        await api.post('/fidelidade/programas', formPrograma);
        toast.success('Programa criado com sucesso!');
      }
      
      setShowProgramaModal(false);
      resetFormPrograma();
      fetchProgramas();
    } catch (error: any) {
      console.error('Erro ao salvar programa:', error);
      toast.error(error.response?.data?.detail || 'Erro ao salvar programa');
    }
  };

  const handleSubmitNivel = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!selectedPrograma) return;
    
    try {
      if (editingNivel) {
        await api.put(`/fidelidade/niveis/${editingNivel.id}`, formNivel);
        toast.success('Nível atualizado com sucesso!');
      } else {
        await api.post(`/fidelidade/programas/${selectedPrograma.id}/niveis`, formNivel);
        toast.success('Nível criado com sucesso!');
      }
      
      setShowNivelModal(false);
      resetFormNivel();
      fetchNiveis(selectedPrograma.id);
    } catch (error: any) {
      console.error('Erro ao salvar nível:', error);
      toast.error(error.response?.data?.detail || 'Erro ao salvar nível');
    }
  };

  const handleSubmitPontos = async (e: React.FormEvent) => {
    e.preventDefault();
    
    try {
      await api.post('/fidelidade/pontos/adicionar', formPontos);
      toast.success('Pontos adicionados com sucesso!');
      
      setShowPontosModal(false);
      resetFormPontos();
      
      if (selectedPrograma) {
        fetchEstatisticas(selectedPrograma.id);
      }
    } catch (error: any) {
      console.error('Erro ao adicionar pontos:', error);
      toast.error(error.response?.data?.detail || 'Erro ao adicionar pontos');
    }
  };

  const handleEditPrograma = (programa: ProgramaFidelidade) => {
    setEditingPrograma(programa);
    setFormPrograma({
      nome: programa.nome,
      descricao: programa.descricao || '',
      tipo_programa: programa.tipo_programa || 'pontos',
      ativo: programa.ativo
    });
    setShowProgramaModal(true);
  };

  const handleViewPrograma = async (programa: ProgramaFidelidade) => {
    setSelectedPrograma(programa);
    setActiveTab('detalhes');
    await fetchNiveis(programa.id);
    await fetchEstatisticas(programa.id);
  };

  const resetFormPrograma = () => {
    setEditingPrograma(null);
    setFormPrograma({
      nome: '',
      descricao: '',
      tipo_programa: 'pontos',
      ativo: true
    });
  };

  const resetFormNivel = () => {
    setEditingNivel(null);
    setFormNivel({
      nome: '',
      pontos_minimos: 0,
      pontos_maximos: null,
      cor: '#3B82F6',
      icone: 'star',
      beneficios: {},
      desconto_percentual: 0,
      multiplicador_pontos: 1,
      ordem: 0
    });
  };

  const resetFormPontos = () => {
    setFormPontos({
      participante_id: 0,
      tipo: 'credito',
      pontos: 0,
      descricao: '',
      referencia_tipo: 'manual'
    });
  };

  const getNivelIcon = (nome: string) => {
    switch (nome.toLowerCase()) {
      case 'bronze':
        return <Trophy className="h-5 w-5" style={{ color: '#CD7F32' }} />;
      case 'prata':
        return <Trophy className="h-5 w-5" style={{ color: '#C0C0C0' }} />;
      case 'ouro':
        return <Trophy className="h-5 w-5" style={{ color: '#FFD700' }} />;
      case 'diamante':
        return <Crown className="h-5 w-5" style={{ color: '#B9F2FF' }} />;
      default:
        return <Star className="h-5 w-5" />;
    }
  };

  return (
    <div className="p-6 space-y-6">
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList>
          <TabsTrigger value="programas">Programas</TabsTrigger>
          <TabsTrigger value="detalhes">Detalhes</TabsTrigger>
          <TabsTrigger value="estatisticas">Estatísticas</TabsTrigger>
        </TabsList>

        <TabsContent value="programas" className="space-y-4">
          <Card>
            <CardHeader>
              <div className="flex justify-between items-center">
                <div>
                  <CardTitle>Programas de Fidelidade</CardTitle>
                  <CardDescription>
                    Gerencie seus programas de fidelidade e recompensas
                  </CardDescription>
                </div>
                <Button onClick={() => setShowProgramaModal(true)}>
                  <Plus className="h-4 w-4 mr-2" />
                  Novo Programa
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              {loading ? (
                <div className="text-center py-8">Carregando...</div>
              ) : (
                <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                  {programas.map((programa) => (
                    <Card key={programa.id} className="cursor-pointer hover:shadow-lg transition-shadow">
                      <CardHeader className="pb-4">
                        <div className="flex items-start justify-between">
                          <div>
                            <CardTitle className="text-lg">{programa.nome}</CardTitle>
                            <Badge variant={programa.ativo ? 'success' : 'secondary'} className="mt-2">
                              {programa.ativo ? 'Ativo' : 'Inativo'}
                            </Badge>
                          </div>
                          <div className="flex gap-1">
                            <Button
                              size="sm"
                              variant="ghost"
                              onClick={() => handleEditPrograma(programa)}
                            >
                              <Edit className="h-4 w-4" />
                            </Button>
                          </div>
                        </div>
                      </CardHeader>
                      <CardContent>
                        {programa.descricao && (
                          <p className="text-sm text-muted-foreground mb-4">
                            {programa.descricao}
                          </p>
                        )}
                        
                        <div className="space-y-2">
                          <div className="flex items-center justify-between">
                            <span className="text-sm text-muted-foreground">Tipo:</span>
                            <Badge variant="outline">
                              {programa.tipo_programa === 'pontos' && <Coins className="h-3 w-3 mr-1" />}
                              {programa.tipo_programa === 'niveis' && <Trophy className="h-3 w-3 mr-1" />}
                              {programa.tipo_programa === 'cashback' && <Gift className="h-3 w-3 mr-1" />}
                              {programa.tipo_programa || 'Pontos'}
                            </Badge>
                          </div>
                          
                          <div className="flex items-center justify-between">
                            <span className="text-sm text-muted-foreground">Participantes:</span>
                            <div className="flex items-center">
                              <Users className="h-4 w-4 mr-1 text-muted-foreground" />
                              <span className="font-medium">{programa.total_participantes || 0}</span>
                            </div>
                          </div>
                        </div>
                        
                        <Button 
                          className="w-full mt-4"
                          variant="outline"
                          onClick={() => handleViewPrograma(programa)}
                        >
                          Ver Detalhes
                        </Button>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="detalhes" className="space-y-4">
          {selectedPrograma ? (
            <>
              <Card>
                <CardHeader>
                  <div className="flex justify-between items-center">
                    <CardTitle>Níveis de Fidelidade - {selectedPrograma.nome}</CardTitle>
                    <Button onClick={() => setShowNivelModal(true)}>
                      <Plus className="h-4 w-4 mr-2" />
                      Novo Nível
                    </Button>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {niveis.map((nivel) => (
                      <Card key={nivel.id}>
                        <CardContent className="p-4">
                          <div className="flex items-center justify-between">
                            <div className="flex items-center gap-3">
                              {getNivelIcon(nivel.nome)}
                              <div>
                                <h4 className="font-semibold">{nivel.nome}</h4>
                                <div className="flex items-center gap-4 mt-1">
                                  <span className="text-sm text-muted-foreground">
                                    {nivel.pontos_minimos} - {nivel.pontos_maximos || '∞'} pontos
                                  </span>
                                  {nivel.desconto_percentual ? (
                                    <Badge variant="secondary">
                                      {nivel.desconto_percentual}% desconto
                                    </Badge>
                                  ) : null}
                                  {nivel.multiplicador_pontos !== 1 ? (
                                    <Badge variant="outline">
                                      {nivel.multiplicador_pontos}x pontos
                                    </Badge>
                                  ) : null}
                                </div>
                              </div>
                            </div>
                            <div
                              className="w-8 h-8 rounded-full"
                              style={{ backgroundColor: nivel.cor || '#3B82F6' }}
                            />
                          </div>
                        </CardContent>
                      </Card>
                    ))}
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Adicionar Pontos</CardTitle>
                  <CardDescription>
                    Adicione ou remova pontos de participantes do programa
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <Button onClick={() => setShowPontosModal(true)}>
                    <Coins className="h-4 w-4 mr-2" />
                    Gerenciar Pontos
                  </Button>
                </CardContent>
              </Card>
            </>
          ) : (
            <Card>
              <CardContent className="py-8 text-center text-muted-foreground">
                Selecione um programa para ver os detalhes
              </CardContent>
            </Card>
          )}
        </TabsContent>

        <TabsContent value="estatisticas" className="space-y-4">
          {estatisticas ? (
            <>
              <div className="grid gap-4 md:grid-cols-4">
                <Card>
                  <CardContent className="p-6">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm text-muted-foreground">Participantes</p>
                        <p className="text-2xl font-bold">
                          {estatisticas.estatisticas.total_participantes}
                        </p>
                      </div>
                      <Users className="h-8 w-8 text-muted-foreground" />
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardContent className="p-6">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm text-muted-foreground">Pontos Distribuídos</p>
                        <p className="text-2xl font-bold">
                          {estatisticas.estatisticas.pontos_distribuidos.toLocaleString()}
                        </p>
                      </div>
                      <TrendingUp className="h-8 w-8 text-green-500" />
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardContent className="p-6">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm text-muted-foreground">Pontos Resgatados</p>
                        <p className="text-2xl font-bold">
                          {estatisticas.estatisticas.pontos_resgatados.toLocaleString()}
                        </p>
                      </div>
                      <Gift className="h-8 w-8 text-blue-500" />
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardContent className="p-6">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm text-muted-foreground">Em Circulação</p>
                        <p className="text-2xl font-bold">
                          {estatisticas.estatisticas.pontos_em_circulacao.toLocaleString()}
                        </p>
                      </div>
                      <Coins className="h-8 w-8 text-yellow-500" />
                    </div>
                  </CardContent>
                </Card>
              </div>

              {estatisticas.estatisticas.distribuicao_niveis && (
                <Card>
                  <CardHeader>
                    <CardTitle>Distribuição por Nível</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      {Object.entries(estatisticas.estatisticas.distribuicao_niveis).map(([nivel, count]) => (
                        <div key={nivel} className="flex items-center gap-4">
                          <div className="flex items-center gap-2 w-24">
                            {getNivelIcon(nivel)}
                            <span className="font-medium">{nivel}</span>
                          </div>
                          <Progress 
                            value={(count as number / estatisticas.estatisticas.total_participantes) * 100} 
                            className="flex-1"
                          />
                          <span className="w-12 text-sm text-muted-foreground">{count}</span>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              )}

              {estatisticas.estatisticas.top_participantes && (
                <Card>
                  <CardHeader>
                    <CardTitle>Top Participantes</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <Table>
                      <TableHeader>
                        <TableRow>
                          <TableHead>Posição</TableHead>
                          <TableHead>Nome</TableHead>
                          <TableHead>Pontos Totais</TableHead>
                          <TableHead>Pontos Disponíveis</TableHead>
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {estatisticas.estatisticas.top_participantes.map((participante: any, index: number) => (
                          <TableRow key={index}>
                            <TableCell>
                              <div className="flex items-center gap-2">
                                {index === 0 && <Trophy className="h-4 w-4 text-yellow-500" />}
                                {index === 1 && <Trophy className="h-4 w-4 text-gray-400" />}
                                {index === 2 && <Trophy className="h-4 w-4 text-amber-600" />}
                                {index + 1}º
                              </div>
                            </TableCell>
                            <TableCell className="font-medium">{participante.nome}</TableCell>
                            <TableCell>{participante.pontos_totais.toLocaleString()}</TableCell>
                            <TableCell>{participante.pontos_disponiveis.toLocaleString()}</TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </CardContent>
                </Card>
              )}
            </>
          ) : (
            <Card>
              <CardContent className="py-8 text-center text-muted-foreground">
                Selecione um programa para ver as estatísticas
              </CardContent>
            </Card>
          )}
        </TabsContent>
      </Tabs>

      {/* Modal de Programa */}
      <Dialog open={showProgramaModal} onOpenChange={setShowProgramaModal}>
        <DialogContent className="max-w-2xl">
          <form onSubmit={handleSubmitPrograma}>
            <DialogHeader>
              <DialogTitle>
                {editingPrograma ? 'Editar Programa' : 'Novo Programa de Fidelidade'}
              </DialogTitle>
              <DialogDescription>
                Configure os detalhes do programa de fidelidade
              </DialogDescription>
            </DialogHeader>

            <div className="grid gap-4 py-4">
              <div className="space-y-2">
                <Label htmlFor="nome">Nome do Programa*</Label>
                <Input
                  id="nome"
                  required
                  value={formPrograma.nome}
                  onChange={(e) => setFormPrograma({ ...formPrograma, nome: e.target.value })}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="descricao">Descrição</Label>
                <Textarea
                  id="descricao"
                  value={formPrograma.descricao}
                  onChange={(e) => setFormPrograma({ ...formPrograma, descricao: e.target.value })}
                  rows={3}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="tipo">Tipo de Programa</Label>
                <Select
                  value={formPrograma.tipo_programa}
                  onValueChange={(value) => setFormPrograma({ ...formPrograma, tipo_programa: value })}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="pontos">Pontos</SelectItem>
                    <SelectItem value="niveis">Níveis</SelectItem>
                    <SelectItem value="cashback">Cashback</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="flex items-center justify-between space-x-2">
                <Label htmlFor="ativo">Programa Ativo</Label>
                <Switch
                  id="ativo"
                  checked={formPrograma.ativo}
                  onCheckedChange={(checked) => setFormPrograma({ ...formPrograma, ativo: checked })}
                />
              </div>
            </div>

            <DialogFooter>
              <Button type="button" variant="outline" onClick={() => setShowProgramaModal(false)}>
                Cancelar
              </Button>
              <Button type="submit">
                {editingPrograma ? 'Atualizar' : 'Criar'} Programa
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>

      {/* Modal de Nível */}
      <Dialog open={showNivelModal} onOpenChange={setShowNivelModal}>
        <DialogContent className="max-w-2xl">
          <form onSubmit={handleSubmitNivel}>
            <DialogHeader>
              <DialogTitle>
                {editingNivel ? 'Editar Nível' : 'Novo Nível de Fidelidade'}
              </DialogTitle>
              <DialogDescription>
                Configure os detalhes do nível de fidelidade
              </DialogDescription>
            </DialogHeader>

            <div className="grid gap-4 py-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="nome_nivel">Nome do Nível*</Label>
                  <Input
                    id="nome_nivel"
                    required
                    value={formNivel.nome}
                    onChange={(e) => setFormNivel({ ...formNivel, nome: e.target.value })}
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="cor_nivel">Cor</Label>
                  <div className="flex gap-2">
                    <Input
                      type="color"
                      value={formNivel.cor}
                      onChange={(e) => setFormNivel({ ...formNivel, cor: e.target.value })}
                      className="w-20"
                    />
                    <Input
                      value={formNivel.cor}
                      onChange={(e) => setFormNivel({ ...formNivel, cor: e.target.value })}
                      className="flex-1"
                    />
                  </div>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="pontos_minimos">Pontos Mínimos*</Label>
                  <Input
                    id="pontos_minimos"
                    type="number"
                    required
                    value={formNivel.pontos_minimos}
                    onChange={(e) => setFormNivel({ ...formNivel, pontos_minimos: parseInt(e.target.value) })}
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="pontos_maximos">Pontos Máximos</Label>
                  <Input
                    id="pontos_maximos"
                    type="number"
                    value={formNivel.pontos_maximos || ''}
                    onChange={(e) => setFormNivel({ 
                      ...formNivel, 
                      pontos_maximos: e.target.value ? parseInt(e.target.value) : null 
                    })}
                    placeholder="Ilimitado"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="desconto">Desconto (%)</Label>
                  <Input
                    id="desconto"
                    type="number"
                    min="0"
                    max="100"
                    value={formNivel.desconto_percentual}
                    onChange={(e) => setFormNivel({ ...formNivel, desconto_percentual: parseFloat(e.target.value) })}
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="multiplicador">Multiplicador de Pontos</Label>
                  <Input
                    id="multiplicador"
                    type="number"
                    min="1"
                    step="0.1"
                    value={formNivel.multiplicador_pontos}
                    onChange={(e) => setFormNivel({ ...formNivel, multiplicador_pontos: parseFloat(e.target.value) })}
                  />
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="ordem">Ordem</Label>
                <Input
                  id="ordem"
                  type="number"
                  value={formNivel.ordem}
                  onChange={(e) => setFormNivel({ ...formNivel, ordem: parseInt(e.target.value) })}
                />
              </div>
            </div>

            <DialogFooter>
              <Button type="button" variant="outline" onClick={() => setShowNivelModal(false)}>
                Cancelar
              </Button>
              <Button type="submit">
                {editingNivel ? 'Atualizar' : 'Criar'} Nível
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>

      {/* Modal de Pontos */}
      <Dialog open={showPontosModal} onOpenChange={setShowPontosModal}>
        <DialogContent>
          <form onSubmit={handleSubmitPontos}>
            <DialogHeader>
              <DialogTitle>Gerenciar Pontos</DialogTitle>
              <DialogDescription>
                Adicione ou remova pontos de um participante
              </DialogDescription>
            </DialogHeader>

            <div className="grid gap-4 py-4">
              <div className="space-y-2">
                <Label htmlFor="participante">ID do Participante*</Label>
                <Input
                  id="participante"
                  type="number"
                  required
                  value={formPontos.participante_id}
                  onChange={(e) => setFormPontos({ ...formPontos, participante_id: parseInt(e.target.value) })}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="tipo_pontos">Tipo de Operação</Label>
                <Select
                  value={formPontos.tipo}
                  onValueChange={(value) => setFormPontos({ ...formPontos, tipo: value })}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="credito">Crédito</SelectItem>
                    <SelectItem value="debito">Débito</SelectItem>
                    <SelectItem value="expiracao">Expiração</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="pontos">Quantidade de Pontos*</Label>
                <Input
                  id="pontos"
                  type="number"
                  min="1"
                  required
                  value={formPontos.pontos}
                  onChange={(e) => setFormPontos({ ...formPontos, pontos: parseInt(e.target.value) })}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="descricao_pontos">Descrição</Label>
                <Textarea
                  id="descricao_pontos"
                  value={formPontos.descricao}
                  onChange={(e) => setFormPontos({ ...formPontos, descricao: e.target.value })}
                  rows={2}
                />
              </div>
            </div>

            <DialogFooter>
              <Button type="button" variant="outline" onClick={() => setShowPontosModal(false)}>
                Cancelar
              </Button>
              <Button type="submit">
                Adicionar Pontos
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default FidelidadeModule;