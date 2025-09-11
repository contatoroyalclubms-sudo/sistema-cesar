import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Printer,
  Plus,
  Edit2,
  Trash2,
  Wifi,
  WifiOff,
  Activity,
  Settings,
  FileText,
  Send,
  AlertCircle,
  CheckCircle,
  XCircle,
  RefreshCw,
  MoreVertical,
  Monitor,
  Smartphone,
  Tablet
} from 'lucide-react';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { Badge } from '@/components/ui/badge';
import { Switch } from '@/components/ui/switch';
import {
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
} from '@/components/ui/tabs';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { useToast } from '@/components/ui/use-toast';
import api from '@/lib/api';

interface Impressora {
  id: number;
  nome: string;
  ip: string;
  porta: number;
  tipo: string;
  modelo: string;
  status: 'online' | 'offline' | 'erro' | 'manutencao' | 'pausada';
  localizacao?: string;
  evento_id?: number;
  ativa: boolean;
  total_impressoes: number;
  ultima_impressao?: string;
  ultima_verificacao?: string;
  largura_papel: number;
  caracteres_linha: number;
  suporta_guilhotina: boolean;
  suporta_qrcode: boolean;
  suporta_codigo_barras: boolean;
  driver?: string;
}

interface ImpressoraInteligente {
  id: number;
  nome: string;
  impressora_id: number;
  tipo_impressao: string;
  local_origem?: string;
  categoria_produto?: string;
  prioridade: number;
  ativo: boolean;
  imprimir_logo: boolean;
  numero_vias: number;
  template_id?: number;
  hora_inicio?: string;
  hora_fim?: string;
  dias_semana?: string;
  evento_id?: number;
}

interface EquipamentoPDV {
  id: number;
  codigo: string;
  tipo: 'POS' | 'Totem' | 'Tablet' | 'Terminal' | 'Check';
  nome?: string;
  perfil_venda?: string;
  impressora_padrao_id?: number;
  operador_id?: number;
  licenciado: boolean;
  data_licenca_inicio?: string;
  data_licenca_fim?: string;
  status: string;
  localizacao?: string;
  evento_id?: number;
  versao_software?: string;
}

interface OperadorPDV {
  id: number;
  nome: string;
  cpf?: string;
  codigo_acesso?: string;
  comissao_percentual: number;
  comissao_fixa: number;
  pode_cancelar: boolean;
  pode_dar_desconto: boolean;
  desconto_maximo: number;
  ativo: boolean;
  total_vendas: number;
  valor_total_vendido: number;
}

const ImpressorasModule: React.FC = () => {
  const navigate = useNavigate();
  const { toast } = useToast();
  const [activeTab, setActiveTab] = useState('impressoras');
  
  // Estados para Impressoras
  const [impressoras, setImpressoras] = useState<Impressora[]>([]);
  const [loadingImpressoras, setLoadingImpressoras] = useState(false);
  const [modalImpressoraAberto, setModalImpressoraAberto] = useState(false);
  const [impressoraSelecionada, setImpressoraSelecionada] = useState<Impressora | null>(null);
  const [formImpressora, setFormImpressora] = useState({
    nome: '',
    ip: '',
    porta: 9100,
    tipo: 'termica',
    modelo: 'Genérica',
    localizacao: '',
    largura_papel: 80,
    caracteres_linha: 48,
    suporta_guilhotina: true,
    suporta_qrcode: true,
    suporta_codigo_barras: true,
    driver: '',
    ativa: true
  });
  
  // Estados para Impressoras Inteligentes
  const [roteamentos, setRoteamentos] = useState<ImpressoraInteligente[]>([]);
  const [modalRoteamentoAberto, setModalRoteamentoAberto] = useState(false);
  const [formRoteamento, setFormRoteamento] = useState({
    nome: '',
    impressora_id: 0,
    tipo_impressao: 'pedidos',
    local_origem: '',
    categoria_produto: '',
    prioridade: 0,
    ativo: true,
    imprimir_logo: false,
    numero_vias: 1,
    hora_inicio: '',
    hora_fim: '',
    dias_semana: ''
  });
  
  // Estados para Equipamentos
  const [equipamentos, setEquipamentos] = useState<EquipamentoPDV[]>([]);
  const [modalEquipamentoAberto, setModalEquipamentoAberto] = useState(false);
  const [formEquipamento, setFormEquipamento] = useState({
    codigo: '',
    tipo: 'POS' as const,
    nome: '',
    perfil_venda: '',
    impressora_padrao_id: 0,
    operador_id: 0,
    localizacao: '',
    versao_software: ''
  });
  
  // Estados para Operadores
  const [operadores, setOperadores] = useState<OperadorPDV[]>([]);
  const [modalOperadorAberto, setModalOperadorAberto] = useState(false);
  const [formOperador, setFormOperador] = useState({
    nome: '',
    cpf: '',
    codigo_acesso: '',
    comissao_percentual: 0,
    comissao_fixa: 0,
    pode_cancelar: false,
    pode_dar_desconto: false,
    desconto_maximo: 0,
    ativo: true
  });
  
  // Estados de teste
  const [testandoImpressora, setTestandoImpressora] = useState<number | null>(null);
  const [modalTesteAberto, setModalTesteAberto] = useState(false);
  const [tipoTeste, setTipoTeste] = useState('simples');
  const [mensagemTeste, setMensagemTeste] = useState('');
  
  // Buscar dados ao montar
  useEffect(() => {
    carregarImpressoras();
    carregarRoteamentos();
    carregarEquipamentos();
    carregarOperadores();
  }, []);
  
  // Funções de carregamento
  const carregarImpressoras = async () => {
    setLoadingImpressoras(true);
    try {
      const response = await api.get('/api/impressoras/');
      setImpressoras(response.data);
    } catch (error) {
      console.error('Erro ao carregar impressoras:', error);
      toast({
        title: 'Erro',
        description: 'Não foi possível carregar as impressoras',
        variant: 'destructive'
      });
    } finally {
      setLoadingImpressoras(false);
    }
  };
  
  const carregarRoteamentos = async () => {
    try {
      const response = await api.get('/api/impressoras/inteligentes/');
      setRoteamentos(response.data);
    } catch (error) {
      console.error('Erro ao carregar roteamentos:', error);
    }
  };
  
  const carregarEquipamentos = async () => {
    try {
      const response = await api.get('/api/impressoras/equipamentos/');
      setEquipamentos(response.data);
    } catch (error) {
      console.error('Erro ao carregar equipamentos:', error);
    }
  };
  
  const carregarOperadores = async () => {
    try {
      const response = await api.get('/api/impressoras/operadores/');
      setOperadores(response.data);
    } catch (error) {
      console.error('Erro ao carregar operadores:', error);
    }
  };
  
  // Funções de CRUD Impressoras
  const salvarImpressora = async () => {
    try {
      if (impressoraSelecionada) {
        await api.put(`/api/impressoras/${impressoraSelecionada.id}`, formImpressora);
        toast({
          title: 'Sucesso',
          description: 'Impressora atualizada com sucesso'
        });
      } else {
        await api.post('/api/impressoras/', formImpressora);
        toast({
          title: 'Sucesso',
          description: 'Impressora cadastrada com sucesso'
        });
      }
      
      setModalImpressoraAberto(false);
      setImpressoraSelecionada(null);
      setFormImpressora({
        nome: '',
        ip: '',
        porta: 9100,
        tipo: 'termica',
        modelo: 'Genérica',
        localizacao: '',
        largura_papel: 80,
        caracteres_linha: 48,
        suporta_guilhotina: true,
        suporta_qrcode: true,
        suporta_codigo_barras: true,
        driver: '',
        ativa: true
      });
      carregarImpressoras();
    } catch (error: any) {
      toast({
        title: 'Erro',
        description: error.response?.data?.detail || 'Erro ao salvar impressora',
        variant: 'destructive'
      });
    }
  };
  
  const excluirImpressora = async (id: number) => {
    if (confirm('Deseja realmente excluir esta impressora?')) {
      try {
        await api.delete(`/api/impressoras/${id}`);
        toast({
          title: 'Sucesso',
          description: 'Impressora excluída com sucesso'
        });
        carregarImpressoras();
      } catch (error: any) {
        toast({
          title: 'Erro',
          description: error.response?.data?.detail || 'Erro ao excluir impressora',
          variant: 'destructive'
        });
      }
    }
  };
  
  const verificarStatus = async (id: number) => {
    try {
      const response = await api.get(`/api/impressoras/${id}/status`);
      const impressora = impressoras.find(i => i.id === id);
      
      toast({
        title: response.data.online ? 'Online' : 'Offline',
        description: `${impressora?.nome}: ${response.data.mensagem}`
      });
      
      carregarImpressoras(); // Recarregar para atualizar status
    } catch (error) {
      toast({
        title: 'Erro',
        description: 'Não foi possível verificar o status',
        variant: 'destructive'
      });
    }
  };
  
  const testarImpressora = async () => {
    if (!testandoImpressora) return;
    
    try {
      const response = await api.post(`/api/impressoras/${testandoImpressora}/teste`, {
        tipo_teste: tipoTeste,
        mensagem_customizada: mensagemTeste || undefined
      });
      
      toast({
        title: response.data.sucesso ? 'Teste enviado' : 'Falha no teste',
        description: response.data.mensagem
      });
      
      setModalTesteAberto(false);
      setTestandoImpressora(null);
      setTipoTeste('simples');
      setMensagemTeste('');
    } catch (error: any) {
      toast({
        title: 'Erro',
        description: error.response?.data?.detail || 'Erro ao enviar teste',
        variant: 'destructive'
      });
    }
  };
  
  // Função para obter ícone do status
  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'online':
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'offline':
        return <XCircle className="h-4 w-4 text-gray-500" />;
      case 'erro':
        return <AlertCircle className="h-4 w-4 text-red-500" />;
      case 'manutencao':
        return <Settings className="h-4 w-4 text-yellow-500" />;
      case 'pausada':
        return <Activity className="h-4 w-4 text-blue-500" />;
      default:
        return <AlertCircle className="h-4 w-4 text-gray-500" />;
    }
  };
  
  // Função para obter ícone do tipo de equipamento
  const getEquipamentoIcon = (tipo: string) => {
    switch (tipo) {
      case 'POS':
        return <Monitor className="h-4 w-4" />;
      case 'Tablet':
        return <Tablet className="h-4 w-4" />;
      case 'Totem':
        return <Monitor className="h-4 w-4" />;
      case 'Terminal':
        return <Smartphone className="h-4 w-4" />;
      default:
        return <Monitor className="h-4 w-4" />;
    }
  };
  
  return (
    <div className="container mx-auto py-6 space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">Sistema de Impressoras</h1>
          <p className="text-muted-foreground">
            Gerencie impressoras, roteamentos inteligentes e equipamentos PDV
          </p>
        </div>
      </div>
      
      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="impressoras">Impressoras</TabsTrigger>
          <TabsTrigger value="inteligente">Roteamento Inteligente</TabsTrigger>
          <TabsTrigger value="equipamentos">Equipamentos</TabsTrigger>
          <TabsTrigger value="operadores">Operadores</TabsTrigger>
        </TabsList>
        
        <TabsContent value="impressoras" className="space-y-4">
          <Card>
            <CardHeader>
              <div className="flex justify-between items-center">
                <div>
                  <CardTitle>Cadastro de Impressoras</CardTitle>
                  <CardDescription>
                    Gerencie as impressoras disponíveis no sistema
                  </CardDescription>
                </div>
                <Button
                  onClick={() => {
                    setImpressoraSelecionada(null);
                    setFormImpressora({
                      nome: '',
                      ip: '',
                      porta: 9100,
                      tipo: 'termica',
                      modelo: 'Genérica',
                      localizacao: '',
                      largura_papel: 80,
                      caracteres_linha: 48,
                      suporta_guilhotina: true,
                      suporta_qrcode: true,
                      suporta_codigo_barras: true,
                      driver: '',
                      ativa: true
                    });
                    setModalImpressoraAberto(true);
                  }}
                >
                  <Plus className="mr-2 h-4 w-4" />
                  Adicionar Impressora
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              {loadingImpressoras ? (
                <div className="flex justify-center py-8">
                  <RefreshCw className="h-8 w-8 animate-spin" />
                </div>
              ) : impressoras.length === 0 ? (
                <Alert>
                  <AlertCircle className="h-4 w-4" />
                  <AlertDescription>
                    Nenhuma impressora cadastrada. Adicione a primeira impressora para começar.
                  </AlertDescription>
                </Alert>
              ) : (
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Status</TableHead>
                      <TableHead>Nome</TableHead>
                      <TableHead>IP</TableHead>
                      <TableHead>Tipo</TableHead>
                      <TableHead>Modelo</TableHead>
                      <TableHead>Localização</TableHead>
                      <TableHead>Impressões</TableHead>
                      <TableHead>Última Impressão</TableHead>
                      <TableHead>Ações</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {impressoras.map((impressora) => (
                      <TableRow key={impressora.id}>
                        <TableCell>
                          <div className="flex items-center gap-2">
                            {getStatusIcon(impressora.status)}
                            <Badge variant={impressora.status === 'online' ? 'default' : 'secondary'}>
                              {impressora.status}
                            </Badge>
                          </div>
                        </TableCell>
                        <TableCell className="font-medium">{impressora.nome}</TableCell>
                        <TableCell>{impressora.ip}:{impressora.porta}</TableCell>
                        <TableCell>{impressora.tipo}</TableCell>
                        <TableCell>{impressora.modelo}</TableCell>
                        <TableCell>{impressora.localizacao || '-'}</TableCell>
                        <TableCell>{impressora.total_impressoes}</TableCell>
                        <TableCell>
                          {impressora.ultima_impressao
                            ? new Date(impressora.ultima_impressao).toLocaleString('pt-BR')
                            : '-'}
                        </TableCell>
                        <TableCell>
                          <DropdownMenu>
                            <DropdownMenuTrigger asChild>
                              <Button variant="ghost" className="h-8 w-8 p-0">
                                <MoreVertical className="h-4 w-4" />
                              </Button>
                            </DropdownMenuTrigger>
                            <DropdownMenuContent align="end">
                              <DropdownMenuLabel>Ações</DropdownMenuLabel>
                              <DropdownMenuItem onClick={() => verificarStatus(impressora.id)}>
                                <Wifi className="mr-2 h-4 w-4" />
                                Verificar Status
                              </DropdownMenuItem>
                              <DropdownMenuItem
                                onClick={() => {
                                  setTestandoImpressora(impressora.id);
                                  setModalTesteAberto(true);
                                }}
                              >
                                <Printer className="mr-2 h-4 w-4" />
                                Testar Impressão
                              </DropdownMenuItem>
                              <DropdownMenuSeparator />
                              <DropdownMenuItem
                                onClick={() => {
                                  setImpressoraSelecionada(impressora);
                                  setFormImpressora({
                                    nome: impressora.nome,
                                    ip: impressora.ip,
                                    porta: impressora.porta,
                                    tipo: impressora.tipo,
                                    modelo: impressora.modelo,
                                    localizacao: impressora.localizacao || '',
                                    largura_papel: impressora.largura_papel,
                                    caracteres_linha: impressora.caracteres_linha,
                                    suporta_guilhotina: impressora.suporta_guilhotina,
                                    suporta_qrcode: impressora.suporta_qrcode,
                                    suporta_codigo_barras: impressora.suporta_codigo_barras,
                                    driver: impressora.driver || '',
                                    ativa: impressora.ativa
                                  });
                                  setModalImpressoraAberto(true);
                                }}
                              >
                                <Edit2 className="mr-2 h-4 w-4" />
                                Editar
                              </DropdownMenuItem>
                              <DropdownMenuItem
                                className="text-red-600"
                                onClick={() => excluirImpressora(impressora.id)}
                              >
                                <Trash2 className="mr-2 h-4 w-4" />
                                Excluir
                              </DropdownMenuItem>
                            </DropdownMenuContent>
                          </DropdownMenu>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              )}
            </CardContent>
          </Card>
        </TabsContent>
        
        <TabsContent value="inteligente" className="space-y-4">
          <Card>
            <CardHeader>
              <div className="flex justify-between items-center">
                <div>
                  <CardTitle>Impressoras Inteligentes</CardTitle>
                  <CardDescription>
                    Configure o roteamento automático de impressões baseado em regras
                  </CardDescription>
                </div>
                <Button
                  onClick={() => {
                    setFormRoteamento({
                      nome: '',
                      impressora_id: impressoras[0]?.id || 0,
                      tipo_impressao: 'pedidos',
                      local_origem: '',
                      categoria_produto: '',
                      prioridade: 0,
                      ativo: true,
                      imprimir_logo: false,
                      numero_vias: 1,
                      hora_inicio: '',
                      hora_fim: '',
                      dias_semana: ''
                    });
                    setModalRoteamentoAberto(true);
                  }}
                >
                  <Plus className="mr-2 h-4 w-4" />
                  Nova Impressão
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              {roteamentos.length === 0 ? (
                <Alert>
                  <AlertCircle className="h-4 w-4" />
                  <AlertDescription>
                    Para utilizar essa funcionalidade, é necessário ter impressoras configuradas.
                    Configure regras de roteamento para direcionar impressões automaticamente.
                  </AlertDescription>
                </Alert>
              ) : (
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Nome</TableHead>
                      <TableHead>Impressora</TableHead>
                      <TableHead>Tipo de Impressão</TableHead>
                      <TableHead>Local</TableHead>
                      <TableHead>Categoria</TableHead>
                      <TableHead>Prioridade</TableHead>
                      <TableHead>Status</TableHead>
                      <TableHead>Ações</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {roteamentos.map((roteamento) => {
                      const impressora = impressoras.find(i => i.id === roteamento.impressora_id);
                      return (
                        <TableRow key={roteamento.id}>
                          <TableCell className="font-medium">{roteamento.nome}</TableCell>
                          <TableCell>{impressora?.nome || 'N/A'}</TableCell>
                          <TableCell>{roteamento.tipo_impressao}</TableCell>
                          <TableCell>{roteamento.local_origem || '-'}</TableCell>
                          <TableCell>{roteamento.categoria_produto || '-'}</TableCell>
                          <TableCell>{roteamento.prioridade}</TableCell>
                          <TableCell>
                            <Badge variant={roteamento.ativo ? 'default' : 'secondary'}>
                              {roteamento.ativo ? 'Ativo' : 'Inativo'}
                            </Badge>
                          </TableCell>
                          <TableCell>
                            <div className="flex gap-2">
                              <Button
                                size="sm"
                                variant="ghost"
                                onClick={() => {/* Editar */}}
                              >
                                <Edit2 className="h-4 w-4" />
                              </Button>
                              <Button
                                size="sm"
                                variant="ghost"
                                className="text-red-600"
                                onClick={() => {/* Excluir */}}
                              >
                                <Trash2 className="h-4 w-4" />
                              </Button>
                            </div>
                          </TableCell>
                        </TableRow>
                      );
                    })}
                  </TableBody>
                </Table>
              )}
            </CardContent>
          </Card>
        </TabsContent>
        
        <TabsContent value="equipamentos" className="space-y-4">
          <Card>
            <CardHeader>
              <div className="flex justify-between items-center">
                <div>
                  <CardTitle>Equipamentos PDV</CardTitle>
                  <CardDescription>
                    Gerencie dispositivos POS, totens, tablets e terminais
                  </CardDescription>
                </div>
                <Button
                  onClick={() => {
                    setFormEquipamento({
                      codigo: '',
                      tipo: 'POS',
                      nome: '',
                      perfil_venda: '',
                      impressora_padrao_id: impressoras[0]?.id || 0,
                      operador_id: operadores[0]?.id || 0,
                      localizacao: '',
                      versao_software: ''
                    });
                    setModalEquipamentoAberto(true);
                  }}
                >
                  <Plus className="mr-2 h-4 w-4" />
                  Adicionar Equipamento
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              {equipamentos.length === 0 ? (
                <Alert>
                  <AlertCircle className="h-4 w-4" />
                  <AlertDescription>
                    Nenhum equipamento cadastrado. Adicione dispositivos PDV para começar.
                  </AlertDescription>
                </Alert>
              ) : (
                <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                  {equipamentos.map((equipamento) => (
                    <Card key={equipamento.id}>
                      <CardHeader className="pb-3">
                        <div className="flex justify-between items-start">
                          <div className="flex items-center gap-2">
                            {getEquipamentoIcon(equipamento.tipo)}
                            <div>
                              <CardTitle className="text-lg">
                                {equipamento.codigo}
                              </CardTitle>
                              <CardDescription>
                                {equipamento.nome || equipamento.tipo}
                              </CardDescription>
                            </div>
                          </div>
                          <Badge variant={equipamento.licenciado ? 'default' : 'destructive'}>
                            {equipamento.licenciado ? 'Licenciado' : 'Sem licença'}
                          </Badge>
                        </div>
                      </CardHeader>
                      <CardContent className="space-y-2">
                        <div className="text-sm">
                          <span className="text-muted-foreground">Perfil:</span>{' '}
                          {equipamento.perfil_venda || 'Sem perfil'}
                        </div>
                        <div className="text-sm">
                          <span className="text-muted-foreground">Local:</span>{' '}
                          {equipamento.localizacao || 'N/A'}
                        </div>
                        {equipamento.data_licenca_fim && (
                          <div className="text-sm">
                            <span className="text-muted-foreground">Licença até:</span>{' '}
                            {new Date(equipamento.data_licenca_fim).toLocaleDateString('pt-BR')}
                          </div>
                        )}
                        <div className="flex gap-2 pt-2">
                          <Button size="sm" variant="outline" className="flex-1">
                            <Edit2 className="h-3 w-3 mr-1" />
                            Editar
                          </Button>
                          <Button size="sm" variant="outline" className="flex-1">
                            <Settings className="h-3 w-3 mr-1" />
                            Configurar
                          </Button>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
        
        <TabsContent value="operadores" className="space-y-4">
          <Card>
            <CardHeader>
              <div className="flex justify-between items-center">
                <div>
                  <CardTitle>Operadores PDV</CardTitle>
                  <CardDescription>
                    Gerencie operadores e suas permissões de acesso
                  </CardDescription>
                </div>
                <Button
                  onClick={() => {
                    setFormOperador({
                      nome: '',
                      cpf: '',
                      codigo_acesso: '',
                      comissao_percentual: 0,
                      comissao_fixa: 0,
                      pode_cancelar: false,
                      pode_dar_desconto: false,
                      desconto_maximo: 0,
                      ativo: true
                    });
                    setModalOperadorAberto(true);
                  }}
                >
                  <Plus className="mr-2 h-4 w-4" />
                  Adicionar Operador
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              {operadores.length === 0 ? (
                <Alert>
                  <AlertCircle className="h-4 w-4" />
                  <AlertDescription>
                    Nenhum operador cadastrado. Operadores são utilizados nos dispositivos PDV.
                  </AlertDescription>
                </Alert>
              ) : (
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Nome</TableHead>
                      <TableHead>CPF</TableHead>
                      <TableHead>Comissão</TableHead>
                      <TableHead>Vendas</TableHead>
                      <TableHead>Total Vendido</TableHead>
                      <TableHead>Permissões</TableHead>
                      <TableHead>Status</TableHead>
                      <TableHead>Ações</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {operadores.map((operador) => (
                      <TableRow key={operador.id}>
                        <TableCell className="font-medium">{operador.nome}</TableCell>
                        <TableCell>{operador.cpf || '-'}</TableCell>
                        <TableCell>
                          {operador.comissao_percentual > 0 && `${operador.comissao_percentual}%`}
                          {operador.comissao_percentual > 0 && operador.comissao_fixa > 0 && ' + '}
                          {operador.comissao_fixa > 0 && `R$ ${operador.comissao_fixa.toFixed(2)}`}
                          {operador.comissao_percentual === 0 && operador.comissao_fixa === 0 && '-'}
                        </TableCell>
                        <TableCell>{operador.total_vendas}</TableCell>
                        <TableCell>R$ {operador.valor_total_vendido.toFixed(2)}</TableCell>
                        <TableCell>
                          <div className="flex gap-1">
                            {operador.pode_cancelar && (
                              <Badge variant="outline" className="text-xs">Cancelar</Badge>
                            )}
                            {operador.pode_dar_desconto && (
                              <Badge variant="outline" className="text-xs">
                                Desconto {operador.desconto_maximo}%
                              </Badge>
                            )}
                          </div>
                        </TableCell>
                        <TableCell>
                          <Badge variant={operador.ativo ? 'default' : 'secondary'}>
                            {operador.ativo ? 'Ativo' : 'Inativo'}
                          </Badge>
                        </TableCell>
                        <TableCell>
                          <div className="flex gap-2">
                            <Button size="sm" variant="ghost">
                              <Edit2 className="h-4 w-4" />
                            </Button>
                            <Button size="sm" variant="ghost" className="text-red-600">
                              <Trash2 className="h-4 w-4" />
                            </Button>
                          </div>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
      
      {/* Modal de Adicionar/Editar Impressora */}
      <Dialog open={modalImpressoraAberto} onOpenChange={setModalImpressoraAberto}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>
              {impressoraSelecionada ? 'Editar' : 'Adicionar'} Impressora
            </DialogTitle>
            <DialogDescription>
              Preencha os dados da impressora
            </DialogDescription>
          </DialogHeader>
          
          <div className="grid gap-4 py-4">
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="nome">Nome *</Label>
                <Input
                  id="nome"
                  value={formImpressora.nome}
                  onChange={(e) => setFormImpressora({ ...formImpressora, nome: e.target.value })}
                  placeholder="Ex: Impressora Cozinha"
                />
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="ip">IP *</Label>
                <Input
                  id="ip"
                  value={formImpressora.ip}
                  onChange={(e) => setFormImpressora({ ...formImpressora, ip: e.target.value })}
                  placeholder="Ex: 192.168.1.100"
                />
              </div>
            </div>
            
            <div className="grid grid-cols-3 gap-4">
              <div className="space-y-2">
                <Label htmlFor="porta">Porta</Label>
                <Input
                  id="porta"
                  type="number"
                  value={formImpressora.porta}
                  onChange={(e) => setFormImpressora({ ...formImpressora, porta: parseInt(e.target.value) })}
                />
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="tipo">Tipo</Label>
                <Select
                  value={formImpressora.tipo}
                  onValueChange={(value) => setFormImpressora({ ...formImpressora, tipo: value })}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="termica">Térmica</SelectItem>
                    <SelectItem value="fiscal">Fiscal</SelectItem>
                    <SelectItem value="etiqueta">Etiqueta</SelectItem>
                    <SelectItem value="matricial">Matricial</SelectItem>
                    <SelectItem value="laser">Laser</SelectItem>
                    <SelectItem value="pos">POS</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="modelo">Modelo</Label>
                <Select
                  value={formImpressora.modelo}
                  onValueChange={(value) => setFormImpressora({ ...formImpressora, modelo: value })}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="Genérica">Genérica</SelectItem>
                    <SelectItem value="Epson TM-T20">Epson TM-T20</SelectItem>
                    <SelectItem value="Epson TM-T20x">Epson TM-T20x</SelectItem>
                    <SelectItem value="Bematech MP-4200">Bematech MP-4200</SelectItem>
                    <SelectItem value="Elgin i8">Elgin i8</SelectItem>
                    <SelectItem value="Elgin i9">Elgin i9</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
            
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="localizacao">Localização</Label>
                <Input
                  id="localizacao"
                  value={formImpressora.localizacao}
                  onChange={(e) => setFormImpressora({ ...formImpressora, localizacao: e.target.value })}
                  placeholder="Ex: Cozinha, Bar, Caixa"
                />
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="driver">Driver</Label>
                <Input
                  id="driver"
                  value={formImpressora.driver}
                  onChange={(e) => setFormImpressora({ ...formImpressora, driver: e.target.value })}
                  placeholder="Driver específico (opcional)"
                />
              </div>
            </div>
            
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="largura">Largura do papel (mm)</Label>
                <Input
                  id="largura"
                  type="number"
                  value={formImpressora.largura_papel}
                  onChange={(e) => setFormImpressora({ ...formImpressora, largura_papel: parseInt(e.target.value) })}
                />
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="caracteres">Caracteres por linha</Label>
                <Input
                  id="caracteres"
                  type="number"
                  value={formImpressora.caracteres_linha}
                  onChange={(e) => setFormImpressora({ ...formImpressora, caracteres_linha: parseInt(e.target.value) })}
                />
              </div>
            </div>
            
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <Label htmlFor="guilhotina">Suporta guilhotina</Label>
                <Switch
                  id="guilhotina"
                  checked={formImpressora.suporta_guilhotina}
                  onCheckedChange={(checked) => setFormImpressora({ ...formImpressora, suporta_guilhotina: checked })}
                />
              </div>
              
              <div className="flex items-center justify-between">
                <Label htmlFor="qrcode">Suporta QR Code</Label>
                <Switch
                  id="qrcode"
                  checked={formImpressora.suporta_qrcode}
                  onCheckedChange={(checked) => setFormImpressora({ ...formImpressora, suporta_qrcode: checked })}
                />
              </div>
              
              <div className="flex items-center justify-between">
                <Label htmlFor="barcode">Suporta código de barras</Label>
                <Switch
                  id="barcode"
                  checked={formImpressora.suporta_codigo_barras}
                  onCheckedChange={(checked) => setFormImpressora({ ...formImpressora, suporta_codigo_barras: checked })}
                />
              </div>
              
              <div className="flex items-center justify-between">
                <Label htmlFor="ativa">Impressora ativa</Label>
                <Switch
                  id="ativa"
                  checked={formImpressora.ativa}
                  onCheckedChange={(checked) => setFormImpressora({ ...formImpressora, ativa: checked })}
                />
              </div>
            </div>
          </div>
          
          <DialogFooter>
            <Button variant="outline" onClick={() => setModalImpressoraAberto(false)}>
              Cancelar
            </Button>
            <Button onClick={salvarImpressora}>
              {impressoraSelecionada ? 'Salvar' : 'Adicionar'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
      
      {/* Modal de Teste de Impressão */}
      <Dialog open={modalTesteAberto} onOpenChange={setModalTesteAberto}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Testar Impressão</DialogTitle>
            <DialogDescription>
              Escolha o tipo de teste e envie para a impressora
            </DialogDescription>
          </DialogHeader>
          
          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <Label>Tipo de teste</Label>
              <Select value={tipoTeste} onValueChange={setTipoTeste}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="simples">Teste Simples</SelectItem>
                  <SelectItem value="completo">Teste Completo</SelectItem>
                  <SelectItem value="guilhotina">Teste de Guilhotina</SelectItem>
                  <SelectItem value="qrcode">Teste de QR Code</SelectItem>
                </SelectContent>
              </Select>
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="mensagem">Mensagem customizada (opcional)</Label>
              <Input
                id="mensagem"
                value={mensagemTeste}
                onChange={(e) => setMensagemTeste(e.target.value)}
                placeholder="Digite uma mensagem para incluir no teste"
              />
            </div>
          </div>
          
          <DialogFooter>
            <Button variant="outline" onClick={() => setModalTesteAberto(false)}>
              Cancelar
            </Button>
            <Button onClick={testarImpressora}>
              <Send className="mr-2 h-4 w-4" />
              Enviar Teste
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default ImpressorasModule;