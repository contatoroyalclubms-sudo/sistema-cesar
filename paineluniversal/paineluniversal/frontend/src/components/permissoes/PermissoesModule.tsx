import { useState, useEffect } from 'react';
import { Shield, Users, Lock, Unlock, Plus, Search, Edit, Trash2, AlertTriangle, Check, X, ChevronRight, ChevronDown, Settings, Key, UserCheck, AlertCircle, Award, RefreshCw, Copy, Download, Upload } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Checkbox } from '@/components/ui/checkbox';
import { Switch } from '@/components/ui/switch';
import { toast } from '@/components/ui/use-toast';
import { Progress } from '@/components/ui/progress';
import { Separator } from '@/components/ui/separator';
import { ScrollArea } from '@/components/ui/scroll-area';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from '@/components/ui/accordion';

interface Cargo {
  id: number;
  nome: string;
  descricao: string;
  nivel_hierarquia: number;
  ativo: boolean;
  total_permissoes: number;
  total_colaboradores: number;
  criado_em: string;
}

interface Permissao {
  id: number;
  modulo: string;
  acao: string;
  descricao: string;
}

interface ModuloInfo {
  nome: string;
  descricao: string;
  acoes: string[];
}

interface MatrizPermissao {
  cargo: string;
  total_permissoes_atribuidas: number;
  total_permissoes_possiveis: number;
  matriz: {
    [modulo: string]: {
      nome: string;
      descricao: string;
      acoes: {
        [acao: string]: {
          permitido: boolean;
          permissao_id: number | null;
        };
      };
    };
  };
}

interface AuditInfo {
  estatisticas: {
    total_usuarios: number;
    total_cargos: number;
    total_permissoes_sistema: number;
    total_atribuicoes: number;
    media_permissoes_por_cargo: number;
  };
  alertas: {
    cargos_sem_permissoes: Array<{ id: number; nome: string }>;
    usuarios_sem_cargo: Array<{ id: number; nome: string }>;
  };
  top_permissoes: Array<{
    modulo: string;
    acao: string;
    atribuicoes: number;
  }>;
}

const nivelHierarquicoColors = {
  1: 'bg-purple-500',
  2: 'bg-blue-500',
  3: 'bg-green-500',
  4: 'bg-yellow-500',
  5: 'bg-orange-500',
};

const nivelHierarquicoLabels = {
  1: 'Direção',
  2: 'Gerência',
  3: 'Supervisão',
  4: 'Operação',
  5: 'Execução',
};

export default function PermissoesModule() {
  const [cargos, setCargos] = useState<Cargo[]>([]);
  const [selectedCargo, setSelectedCargo] = useState<Cargo | null>(null);
  const [modulos, setModulos] = useState<{ [key: string]: ModuloInfo }>({});
  const [matrizPermissao, setMatrizPermissao] = useState<MatrizPermissao | null>(null);
  const [auditInfo, setAuditInfo] = useState<AuditInfo | null>(null);
  const [loading, setLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [activeTab, setActiveTab] = useState('cargos');
  const [showCreateDialog, setShowCreateDialog] = useState(false);
  const [showMatrizDialog, setShowMatrizDialog] = useState(false);
  const [expandedModulos, setExpandedModulos] = useState<string[]>([]);
  const [permissoesAlteradas, setPermissoesAlteradas] = useState<{ [key: string]: boolean }>({});
  const [initializingPermissions, setInitializingPermissions] = useState(false);

  // Mock data
  useEffect(() => {
    // Mock cargos
    const mockCargos: Cargo[] = [
      {
        id: 1,
        nome: 'Administrador',
        descricao: 'Acesso total ao sistema',
        nivel_hierarquia: 1,
        ativo: true,
        total_permissoes: 132,
        total_colaboradores: 2,
        criado_em: '2024-01-01'
      },
      {
        id: 2,
        nome: 'Gerente',
        descricao: 'Gerenciamento operacional',
        nivel_hierarquia: 2,
        ativo: true,
        total_permissoes: 87,
        total_colaboradores: 5,
        criado_em: '2024-01-02'
      },
      {
        id: 3,
        nome: 'Supervisor',
        descricao: 'Supervisão de operações',
        nivel_hierarquia: 3,
        ativo: true,
        total_permissoes: 54,
        total_colaboradores: 8,
        criado_em: '2024-01-03'
      },
      {
        id: 4,
        nome: 'Operador PDV',
        descricao: 'Operação de ponto de venda',
        nivel_hierarquia: 4,
        ativo: true,
        total_permissoes: 18,
        total_colaboradores: 15,
        criado_em: '2024-01-04'
      },
      {
        id: 5,
        nome: 'Caixa',
        descricao: 'Operações de caixa',
        nivel_hierarquia: 4,
        ativo: true,
        total_permissoes: 12,
        total_colaboradores: 10,
        criado_em: '2024-01-05'
      },
      {
        id: 6,
        nome: 'Recepcionista',
        descricao: 'Recepção e check-in',
        nivel_hierarquia: 5,
        ativo: true,
        total_permissoes: 8,
        total_colaboradores: 6,
        criado_em: '2024-01-06'
      }
    ];
    setCargos(mockCargos);

    // Mock módulos
    const mockModulos = {
      dashboard: {
        nome: 'Dashboard',
        descricao: 'Painel principal e métricas',
        acoes: ['visualizar', 'exportar', 'personalizar']
      },
      eventos: {
        nome: 'Eventos',
        descricao: 'Gestão de eventos',
        acoes: ['visualizar', 'criar', 'editar', 'deletar', 'publicar', 'arquivar', 'clonar']
      },
      vendas: {
        nome: 'Vendas',
        descricao: 'Vendas e transações',
        acoes: ['visualizar', 'criar', 'editar', 'cancelar', 'estornar', 'aprovar', 'relatorio']
      },
      pdv: {
        nome: 'PDV',
        descricao: 'Ponto de venda',
        acoes: ['visualizar', 'vender', 'cancelar', 'desconto', 'fechar_caixa', 'sangria', 'suprimento']
      },
      comandas: {
        nome: 'Comandas',
        descricao: 'Gestão de comandas',
        acoes: ['visualizar', 'criar', 'recarregar', 'bloquear', 'transferir', 'fechar', 'relatorio']
      },
      estoque: {
        nome: 'Estoque',
        descricao: 'Controle de estoque',
        acoes: ['visualizar', 'entrada', 'saida', 'ajustar', 'transferir', 'inventario', 'relatorio']
      },
      financeiro: {
        nome: 'Financeiro',
        descricao: 'Gestão financeira',
        acoes: ['visualizar', 'lancar', 'aprovar', 'relatorio', 'exportar', 'conciliar', 'fechar_periodo']
      },
      usuarios: {
        nome: 'Usuários',
        descricao: 'Controle de usuários',
        acoes: ['visualizar', 'criar', 'editar', 'deletar', 'resetar_senha', 'bloquear', 'permissoes']
      }
    };
    setModulos(mockModulos);

    // Mock audit info
    const mockAudit: AuditInfo = {
      estatisticas: {
        total_usuarios: 58,
        total_cargos: 7,
        total_permissoes_sistema: 132,
        total_atribuicoes: 298,
        media_permissoes_por_cargo: 42.6
      },
      alertas: {
        cargos_sem_permissoes: [],
        usuarios_sem_cargo: [
          { id: 23, nome: 'João Silva' },
          { id: 45, nome: 'Maria Santos' }
        ]
      },
      top_permissoes: [
        { modulo: 'dashboard', acao: 'visualizar', atribuicoes: 7 },
        { modulo: 'pdv', acao: 'vender', atribuicoes: 5 },
        { modulo: 'comandas', acao: 'visualizar', atribuicoes: 5 }
      ]
    };
    setAuditInfo(mockAudit);
  }, []);

  const handleInitializePermissions = async () => {
    setInitializingPermissions(true);
    // Simular inicialização
    await new Promise(resolve => setTimeout(resolve, 2000));
    toast({
      title: 'Permissões Inicializadas',
      description: '132 permissões foram criadas no sistema.',
    });
    setInitializingPermissions(false);
  };

  const handleCreatePresets = async () => {
    setLoading(true);
    await new Promise(resolve => setTimeout(resolve, 1500));
    toast({
      title: 'Cargos Pré-definidos Criados',
      description: '7 cargos com permissões padrão foram criados.',
    });
    setLoading(false);
  };

  const handleTogglePermissao = (modulo: string, acao: string) => {
    if (!matrizPermissao) return;
    
    const key = `${modulo}_${acao}`;
    const currentState = matrizPermissao.matriz[modulo].acoes[acao].permitido;
    
    setMatrizPermissao(prev => {
      if (!prev) return prev;
      return {
        ...prev,
        matriz: {
          ...prev.matriz,
          [modulo]: {
            ...prev.matriz[modulo],
            acoes: {
              ...prev.matriz[modulo].acoes,
              [acao]: {
                ...prev.matriz[modulo].acoes[acao],
                permitido: !currentState
              }
            }
          }
        }
      };
    });
    
    setPermissoesAlteradas(prev => ({
      ...prev,
      [key]: true
    }));
  };

  const handleSavePermissoes = async () => {
    setLoading(true);
    await new Promise(resolve => setTimeout(resolve, 1000));
    toast({
      title: 'Permissões Salvas',
      description: `${Object.keys(permissoesAlteradas).length} permissões foram atualizadas.`,
    });
    setPermissoesAlteradas({});
    setLoading(false);
    setShowMatrizDialog(false);
  };

  const toggleModulo = (modulo: string) => {
    setExpandedModulos(prev =>
      prev.includes(modulo)
        ? prev.filter(m => m !== modulo)
        : [...prev, modulo]
    );
  };

  const renderCargoCard = (cargo: Cargo) => (
    <motion.div
      key={cargo.id}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
    >
      <Card className={`cursor-pointer transition-all hover:shadow-lg ${selectedCargo?.id === cargo.id ? 'ring-2 ring-primary' : ''}`}>
        <CardHeader className="pb-3">
          <div className="flex items-start justify-between">
            <div>
              <CardTitle className="text-lg flex items-center gap-2">
                <Shield className="h-5 w-5" />
                {cargo.nome}
              </CardTitle>
              <p className="text-sm text-muted-foreground mt-1">{cargo.descricao}</p>
            </div>
            <div className="flex flex-col items-end gap-1">
              <Badge className={`${nivelHierarquicoColors[cargo.nivel_hierarquia as keyof typeof nivelHierarquicoColors]} text-white`}>
                {nivelHierarquicoLabels[cargo.nivel_hierarquia as keyof typeof nivelHierarquicoLabels]}
              </Badge>
              <Badge variant={cargo.ativo ? 'default' : 'secondary'}>
                {cargo.ativo ? 'Ativo' : 'Inativo'}
              </Badge>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 gap-4 mb-3">
            <div className="flex items-center gap-2">
              <Key className="h-4 w-4 text-muted-foreground" />
              <div>
                <p className="text-2xl font-bold">{cargo.total_permissoes}</p>
                <p className="text-xs text-muted-foreground">Permissões</p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <Users className="h-4 w-4 text-muted-foreground" />
              <div>
                <p className="text-2xl font-bold">{cargo.total_colaboradores}</p>
                <p className="text-xs text-muted-foreground">Colaboradores</p>
              </div>
            </div>
          </div>
          
          <Progress value={(cargo.total_permissoes / 132) * 100} className="h-2 mb-3" />
          <p className="text-xs text-muted-foreground mb-3">
            {((cargo.total_permissoes / 132) * 100).toFixed(1)}% das permissões disponíveis
          </p>

          <div className="flex gap-1">
            <Button 
              size="sm" 
              variant="outline" 
              className="flex-1"
              onClick={(e) => {
                e.stopPropagation();
                setSelectedCargo(cargo);
                // Mock matriz
                const mockMatriz: MatrizPermissao = {
                  cargo: cargo.nome,
                  total_permissoes_atribuidas: cargo.total_permissoes,
                  total_permissoes_possiveis: 132,
                  matriz: Object.entries(modulos).reduce((acc, [key, value]) => {
                    acc[key] = {
                      nome: value.nome,
                      descricao: value.descricao,
                      acoes: value.acoes.reduce((acoes, acao) => {
                        acoes[acao] = {
                          permitido: Math.random() > 0.5,
                          permissao_id: Math.floor(Math.random() * 1000)
                        };
                        return acoes;
                      }, {} as any)
                    };
                    return acc;
                  }, {} as any)
                };
                setMatrizPermissao(mockMatriz);
                setShowMatrizDialog(true);
              }}
            >
              <Settings className="h-3 w-3 mr-1" />
              Configurar
            </Button>
            <Button size="sm" variant="outline">
              <Copy className="h-3 w-3" />
            </Button>
            <Button size="sm" variant="outline">
              <Edit className="h-3 w-3" />
            </Button>
          </div>
        </CardContent>
      </Card>
    </motion.div>
  );

  return (
    <div className="container mx-auto p-6 max-w-7xl">
      <div className="mb-6">
        <h1 className="text-3xl font-bold mb-2 flex items-center gap-2">
          <Shield className="h-8 w-8" />
          Sistema de Permissões Granular
        </h1>
        <p className="text-muted-foreground">
          Gerencie 132+ permissões distribuídas em 32 módulos do sistema
        </p>
      </div>

      {/* Cards de estatísticas */}
      {auditInfo && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Total Usuários</p>
                  <p className="text-2xl font-bold">{auditInfo.estatisticas.total_usuarios}</p>
                </div>
                <Users className="h-8 w-8 text-muted-foreground" />
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Total Cargos</p>
                  <p className="text-2xl font-bold">{auditInfo.estatisticas.total_cargos}</p>
                </div>
                <Award className="h-8 w-8 text-muted-foreground" />
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Permissões Sistema</p>
                  <p className="text-2xl font-bold">{auditInfo.estatisticas.total_permissoes_sistema}</p>
                </div>
                <Key className="h-8 w-8 text-muted-foreground" />
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Média por Cargo</p>
                  <p className="text-2xl font-bold">{auditInfo.estatisticas.media_permissoes_por_cargo.toFixed(1)}</p>
                </div>
                <Shield className="h-8 w-8 text-muted-foreground" />
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Alertas */}
      {auditInfo && auditInfo.alertas.usuarios_sem_cargo.length > 0 && (
        <div className="mb-4 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
          <div className="flex items-center gap-2 mb-2">
            <AlertTriangle className="h-5 w-5 text-yellow-600" />
            <span className="font-medium">Atenção: Usuários sem cargo definido</span>
          </div>
          <p className="text-sm text-muted-foreground">
            {auditInfo.alertas.usuarios_sem_cargo.length} usuários não possuem cargo atribuído e podem ter permissões limitadas.
          </p>
        </div>
      )}

      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-4">
        <TabsList className="grid grid-cols-4 w-full max-w-xl">
          <TabsTrigger value="cargos">Cargos</TabsTrigger>
          <TabsTrigger value="modulos">Módulos</TabsTrigger>
          <TabsTrigger value="usuarios">Usuários</TabsTrigger>
          <TabsTrigger value="auditoria">Auditoria</TabsTrigger>
        </TabsList>

        <TabsContent value="cargos" className="space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="Buscar cargos..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10 w-64"
                />
              </div>
              <Select defaultValue="todos">
                <SelectTrigger className="w-40">
                  <SelectValue placeholder="Nível" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="todos">Todos</SelectItem>
                  <SelectItem value="1">Direção</SelectItem>
                  <SelectItem value="2">Gerência</SelectItem>
                  <SelectItem value="3">Supervisão</SelectItem>
                  <SelectItem value="4">Operação</SelectItem>
                  <SelectItem value="5">Execução</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="flex gap-2">
              <Button 
                variant="outline"
                onClick={handleInitializePermissions}
                disabled={initializingPermissions}
              >
                {initializingPermissions ? (
                  <>
                    <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                    Inicializando...
                  </>
                ) : (
                  <>
                    <RefreshCw className="h-4 w-4 mr-2" />
                    Inicializar Sistema
                  </>
                )}
              </Button>
              <Button 
                variant="outline"
                onClick={handleCreatePresets}
                disabled={loading}
              >
                <Award className="h-4 w-4 mr-2" />
                Criar Presets
              </Button>
              <Button onClick={() => setShowCreateDialog(true)}>
                <Plus className="h-4 w-4 mr-2" />
                Novo Cargo
              </Button>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {cargos
              .filter(c => c.nome.toLowerCase().includes(searchTerm.toLowerCase()))
              .map(cargo => renderCargoCard(cargo))}
          </div>
        </TabsContent>

        <TabsContent value="modulos" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Módulos e Ações Disponíveis</CardTitle>
              <p className="text-sm text-muted-foreground">
                32 módulos com total de 132+ permissões configuráveis
              </p>
            </CardHeader>
            <CardContent>
              <ScrollArea className="h-[600px] pr-4">
                <Accordion type="multiple" value={expandedModulos}>
                  {Object.entries(modulos).map(([key, modulo]) => (
                    <AccordionItem key={key} value={key}>
                      <AccordionTrigger 
                        onClick={() => toggleModulo(key)}
                        className="hover:no-underline"
                      >
                        <div className="flex items-center justify-between w-full pr-4">
                          <div className="flex items-center gap-2">
                            <Shield className="h-4 w-4" />
                            <span className="font-medium">{modulo.nome}</span>
                          </div>
                          <div className="flex items-center gap-2">
                            <Badge variant="secondary">
                              {modulo.acoes.length} ações
                            </Badge>
                          </div>
                        </div>
                      </AccordionTrigger>
                      <AccordionContent>
                        <div className="pl-6 space-y-2">
                          <p className="text-sm text-muted-foreground mb-3">
                            {modulo.descricao}
                          </p>
                          <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
                            {modulo.acoes.map(acao => (
                              <div key={acao} className="flex items-center gap-2 p-2 rounded-lg bg-muted">
                                <Check className="h-3 w-3 text-green-500" />
                                <span className="text-sm">{acao}</span>
                              </div>
                            ))}
                          </div>
                        </div>
                      </AccordionContent>
                    </AccordionItem>
                  ))}
                </Accordion>
              </ScrollArea>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="usuarios" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Permissões por Usuário</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-center py-12">
                <UserCheck className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                <h3 className="text-lg font-medium mb-2">Visualização de Permissões</h3>
                <p className="text-sm text-muted-foreground mb-4">
                  Selecione um usuário para visualizar suas permissões
                </p>
                <Button variant="outline">
                  <Search className="h-4 w-4 mr-2" />
                  Buscar Usuário
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="auditoria" className="space-y-4">
          {auditInfo && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <Card>
                <CardHeader>
                  <CardTitle>Top Permissões Utilizadas</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    {auditInfo.top_permissoes.map((perm, index) => (
                      <div key={index} className="flex items-center justify-between p-2 rounded-lg bg-muted">
                        <div className="flex items-center gap-2">
                          <Badge variant="outline">{index + 1}</Badge>
                          <span className="text-sm font-medium">
                            {perm.modulo}/{perm.acao}
                          </span>
                        </div>
                        <Badge>{perm.atribuicoes} cargos</Badge>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Resumo de Auditoria</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex items-center justify-between">
                    <span className="text-sm">Total de Atribuições</span>
                    <Badge variant="outline">{auditInfo.estatisticas.total_atribuicoes}</Badge>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm">Cobertura do Sistema</span>
                    <Progress value={75} className="w-24" />
                  </div>
                  <Separator />
                  <div>
                    <p className="text-sm font-medium mb-2">Ações Recomendadas</p>
                    <div className="space-y-1">
                      <div className="flex items-center gap-2 text-sm">
                        <AlertCircle className="h-4 w-4 text-yellow-500" />
                        <span>Revisar usuários sem cargo</span>
                      </div>
                      <div className="flex items-center gap-2 text-sm">
                        <Check className="h-4 w-4 text-green-500" />
                        <span>Todos os cargos têm permissões</span>
                      </div>
                    </div>
                  </div>
                  <Button className="w-full" variant="outline">
                    <Download className="h-4 w-4 mr-2" />
                    Exportar Relatório
                  </Button>
                </CardContent>
              </Card>
            </div>
          )}
        </TabsContent>
      </Tabs>

      {/* Dialog Matriz de Permissões */}
      <Dialog open={showMatrizDialog} onOpenChange={setShowMatrizDialog}>
        <DialogContent className="max-w-5xl max-h-[80vh]">
          <DialogHeader>
            <DialogTitle>Matriz de Permissões - {selectedCargo?.nome}</DialogTitle>
          </DialogHeader>
          {matrizPermissao && (
            <div>
              <div className="flex items-center justify-between mb-4">
                <div>
                  <p className="text-sm text-muted-foreground">
                    {matrizPermissao.total_permissoes_atribuidas} de {matrizPermissao.total_permissoes_possiveis} permissões
                  </p>
                  <Progress 
                    value={(matrizPermissao.total_permissoes_atribuidas / matrizPermissao.total_permissoes_possiveis) * 100} 
                    className="w-64 h-2 mt-1"
                  />
                </div>
                {Object.keys(permissoesAlteradas).length > 0 && (
                  <div className="flex items-center gap-2">
                    <Badge variant="outline">
                      {Object.keys(permissoesAlteradas).length} alterações pendentes
                    </Badge>
                    <Button onClick={handleSavePermissoes} disabled={loading}>
                      {loading ? 'Salvando...' : 'Salvar Alterações'}
                    </Button>
                  </div>
                )}
              </div>

              <ScrollArea className="h-[500px]">
                <div className="space-y-4">
                  {Object.entries(matrizPermissao.matriz).map(([moduloKey, moduloData]) => (
                    <Card key={moduloKey}>
                      <CardHeader className="pb-3">
                        <div className="flex items-center justify-between">
                          <div>
                            <h4 className="font-medium">{moduloData.nome}</h4>
                            <p className="text-xs text-muted-foreground">{moduloData.descricao}</p>
                          </div>
                          <Badge variant="secondary">
                            {Object.values(moduloData.acoes).filter(a => a.permitido).length}/
                            {Object.keys(moduloData.acoes).length}
                          </Badge>
                        </div>
                      </CardHeader>
                      <CardContent>
                        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
                          {Object.entries(moduloData.acoes).map(([acao, config]) => (
                            <div 
                              key={acao}
                              className={`flex items-center gap-2 p-2 rounded-lg border cursor-pointer transition-colors ${
                                config.permitido ? 'bg-green-50 border-green-200' : 'bg-gray-50 border-gray-200'
                              }`}
                              onClick={() => handleTogglePermissao(moduloKey, acao)}
                            >
                              <Checkbox checked={config.permitido} />
                              <span className="text-sm">{acao}</span>
                              {permissoesAlteradas[`${moduloKey}_${acao}`] && (
                                <Badge variant="outline" className="ml-auto text-xs">
                                  •
                                </Badge>
                              )}
                            </div>
                          ))}
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              </ScrollArea>
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
}