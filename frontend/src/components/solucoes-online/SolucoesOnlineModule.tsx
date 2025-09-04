import React, { useState, useEffect } from 'react';
import { Globe, Smartphone, AppWindow, Settings, Palette, Bell, Shield, Download, Upload, Eye, Code, Layers, Zap, CheckCircle } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Textarea } from '@/components/ui/textarea';
import { Switch } from '@/components/ui/switch';
import { Slider } from '@/components/ui/slider';
import { toast } from '@/hooks/use-toast';
import api from '@/utils/api';

interface ConfiguracaoApp {
  id: number;
  nome: string;
  tipo: 'pwa' | 'webapp' | 'mobile';
  configuracao: {
    nome_app: string;
    icone?: string;
    splash_screen?: string;
    cor_primaria: string;
    cor_secundaria: string;
    modo_offline: boolean;
    notificacoes_push: boolean;
    manifest?: any;
  };
  recursos_ativos: string[];
  publicado: boolean;
  url_acesso?: string;
  versao: string;
  criado_em: string;
  atualizado_em: string;
}

interface RecursoApp {
  id: string;
  nome: string;
  descricao: string;
  categoria: 'essencial' | 'engajamento' | 'monetizacao' | 'analytics';
  ativo: boolean;
  configuravel: boolean;
  configuracao?: any;
  icone: string;
}

interface TemplateApp {
  id: number;
  nome: string;
  descricao: string;
  categoria: string;
  preview_url?: string;
  recursos_incluidos: string[];
  preco?: number;
}

const recursosDisponiveis: RecursoApp[] = [
  {
    id: 'checkin',
    nome: 'Check-in Digital',
    descricao: 'Permite check-in por QR Code',
    categoria: 'essencial',
    ativo: true,
    configuravel: true,
    icone: '✅'
  },
  {
    id: 'lista_convidados',
    nome: 'Lista de Convidados',
    descricao: 'Visualização da lista do evento',
    categoria: 'essencial',
    ativo: true,
    configuravel: false,
    icone: '📝'
  },
  {
    id: 'notificacoes',
    nome: 'Notificações Push',
    descricao: 'Envio de avisos e atualizações',
    categoria: 'engajamento',
    ativo: false,
    configuravel: true,
    icone: '🔔'
  },
  {
    id: 'chat',
    nome: 'Chat do Evento',
    descricao: 'Comunicação entre participantes',
    categoria: 'engajamento',
    ativo: false,
    configuravel: true,
    icone: '💬'
  },
  {
    id: 'gamificacao',
    nome: 'Gamificação',
    descricao: 'Rankings e desafios',
    categoria: 'engajamento',
    ativo: false,
    configuravel: true,
    icone: '🎮'
  },
  {
    id: 'vendas',
    nome: 'Vendas In-App',
    descricao: 'Venda de produtos e ingressos',
    categoria: 'monetizacao',
    ativo: false,
    configuravel: true,
    icone: '💳'
  },
  {
    id: 'analytics',
    nome: 'Analytics',
    descricao: 'Métricas de uso do app',
    categoria: 'analytics',
    ativo: false,
    configuravel: true,
    icone: '📊'
  }
];

export default function SolucoesOnlineModule() {
  const [configuracoes, setConfiguracoes] = useState<ConfiguracaoApp[]>([]);
  const [templates, setTemplates] = useState<TemplateApp[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('configuracao');
  const [showNovaConfig, setShowNovaConfig] = useState(false);
  const [showPublicar, setShowPublicar] = useState(false);
  const [selectedConfig, setSelectedConfig] = useState<ConfiguracaoApp | null>(null);
  const [previewMode, setPreviewMode] = useState(false);

  const [novaConfig, setNovaConfig] = useState({
    nome: '',
    tipo: 'pwa' as const,
    configuracao: {
      nome_app: '',
      cor_primaria: '#007bff',
      cor_secundaria: '#6c757d',
      modo_offline: true,
      notificacoes_push: false
    },
    recursos_ativos: ['checkin', 'lista_convidados']
  });

  const [recursos, setRecursos] = useState<RecursoApp[]>(recursosDisponiveis);

  useEffect(() => {
    carregarDados();
  }, [activeTab]);

  const carregarDados = async () => {
    setLoading(true);
    try {
      if (activeTab === 'configuracao' || activeTab === 'recursos') {
        const response = await api.get('/api/solucoes-online/configuracoes');
        setConfiguracoes(response.data);
        if (response.data.length > 0 && !selectedConfig) {
          setSelectedConfig(response.data[0]);
        }
      } else if (activeTab === 'templates') {
        const response = await api.get('/api/solucoes-online/templates');
        setTemplates(response.data);
      }
    } catch (error) {
      console.error('Erro ao carregar dados:', error);
      toast({
        title: "Erro",
        description: "Não foi possível carregar os dados",
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  };

  const criarConfiguracao = async () => {
    try {
      await api.post('/api/solucoes-online/configuracoes', novaConfig);
      toast({
        title: "Sucesso",
        description: "Configuração criada com sucesso"
      });
      setShowNovaConfig(false);
      setNovaConfig({
        nome: '',
        tipo: 'pwa',
        configuracao: {
          nome_app: '',
          cor_primaria: '#007bff',
          cor_secundaria: '#6c757d',
          modo_offline: true,
          notificacoes_push: false
        },
        recursos_ativos: ['checkin', 'lista_convidados']
      });
      carregarDados();
    } catch (error) {
      console.error('Erro ao criar configuração:', error);
      toast({
        title: "Erro",
        description: "Não foi possível criar a configuração",
        variant: "destructive"
      });
    }
  };

  const publicarApp = async () => {
    if (!selectedConfig) return;
    
    try {
      const response = await api.post(`/api/solucoes-online/configuracoes/${selectedConfig.id}/publicar`);
      toast({
        title: "Sucesso",
        description: "App publicado com sucesso!"
      });
      setShowPublicar(false);
      carregarDados();
    } catch (error) {
      console.error('Erro ao publicar app:', error);
      toast({
        title: "Erro",
        description: "Não foi possível publicar o app",
        variant: "destructive"
      });
    }
  };

  const alternarRecurso = async (recursoId: string) => {
    if (!selectedConfig) return;
    
    const recursosAtualizados = selectedConfig.recursos_ativos.includes(recursoId)
      ? selectedConfig.recursos_ativos.filter(r => r !== recursoId)
      : [...selectedConfig.recursos_ativos, recursoId];
    
    try {
      await api.patch(`/api/solucoes-online/configuracoes/${selectedConfig.id}`, {
        recursos_ativos: recursosAtualizados
      });
      toast({
        title: "Sucesso",
        description: "Recurso atualizado com sucesso"
      });
      carregarDados();
    } catch (error) {
      console.error('Erro ao alterar recurso:', error);
      toast({
        title: "Erro",
        description: "Não foi possível alterar o recurso",
        variant: "destructive"
      });
    }
  };

  const gerarPWA = async () => {
    if (!selectedConfig) return;
    
    try {
      const response = await api.post(`/api/solucoes-online/configuracoes/${selectedConfig.id}/gerar-pwa`);
      const blob = new Blob([response.data]);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${selectedConfig.nome}_pwa.zip`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
      
      toast({
        title: "Sucesso",
        description: "PWA gerado e baixado com sucesso"
      });
    } catch (error) {
      console.error('Erro ao gerar PWA:', error);
      toast({
        title: "Erro",
        description: "Não foi possível gerar o PWA",
        variant: "destructive"
      });
    }
  };

  const aplicarTemplate = async (templateId: number) => {
    try {
      await api.post(`/api/solucoes-online/templates/${templateId}/aplicar`);
      toast({
        title: "Sucesso",
        description: "Template aplicado com sucesso"
      });
      carregarDados();
    } catch (error) {
      console.error('Erro ao aplicar template:', error);
      toast({
        title: "Erro",
        description: "Não foi possível aplicar o template",
        variant: "destructive"
      });
    }
  };

  const getCategoriaColor = (categoria: string) => {
    switch (categoria) {
      case 'essencial':
        return 'bg-blue-100 text-blue-800';
      case 'engajamento':
        return 'bg-green-100 text-green-800';
      case 'monetizacao':
        return 'bg-yellow-100 text-yellow-800';
      case 'analytics':
        return 'bg-purple-100 text-purple-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="container mx-auto py-6 space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">Soluções Online</h1>
          <p className="text-muted-foreground">Configure e gerencie seus aplicativos e PWAs</p>
        </div>
        <div className="flex gap-2">
          <Dialog open={showNovaConfig} onOpenChange={setShowNovaConfig}>
            <DialogTrigger asChild>
              <Button>
                <AppWindow className="mr-2 h-4 w-4" />
                Nova Configuração
              </Button>
            </DialogTrigger>
            <DialogContent className="sm:max-w-[600px]">
              <DialogHeader>
                <DialogTitle>Criar Nova Configuração</DialogTitle>
                <DialogDescription>
                  Configure um novo aplicativo para seus eventos
                </DialogDescription>
              </DialogHeader>
              <div className="grid gap-4 py-4">
                <div className="grid gap-2">
                  <Label htmlFor="nome">Nome da Configuração</Label>
                  <Input
                    id="nome"
                    value={novaConfig.nome}
                    onChange={(e) => setNovaConfig({...novaConfig, nome: e.target.value})}
                    placeholder="Ex: App Eventos 2024"
                  />
                </div>
                <div className="grid gap-2">
                  <Label htmlFor="nome_app">Nome do Aplicativo</Label>
                  <Input
                    id="nome_app"
                    value={novaConfig.configuracao.nome_app}
                    onChange={(e) => setNovaConfig({
                      ...novaConfig,
                      configuracao: {...novaConfig.configuracao, nome_app: e.target.value}
                    })}
                    placeholder="Ex: Meu Evento"
                  />
                </div>
                <div className="grid gap-2">
                  <Label htmlFor="tipo">Tipo</Label>
                  <Select
                    value={novaConfig.tipo}
                    onValueChange={(value: any) => setNovaConfig({...novaConfig, tipo: value})}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="pwa">Progressive Web App (PWA)</SelectItem>
                      <SelectItem value="webapp">Web App</SelectItem>
                      <SelectItem value="mobile">App Mobile Nativo</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div className="grid gap-2">
                    <Label htmlFor="cor_primaria">Cor Primária</Label>
                    <div className="flex gap-2">
                      <Input
                        type="color"
                        id="cor_primaria"
                        value={novaConfig.configuracao.cor_primaria}
                        onChange={(e) => setNovaConfig({
                          ...novaConfig,
                          configuracao: {...novaConfig.configuracao, cor_primaria: e.target.value}
                        })}
                        className="w-16 h-10"
                      />
                      <Input
                        value={novaConfig.configuracao.cor_primaria}
                        onChange={(e) => setNovaConfig({
                          ...novaConfig,
                          configuracao: {...novaConfig.configuracao, cor_primaria: e.target.value}
                        })}
                        placeholder="#007bff"
                      />
                    </div>
                  </div>
                  <div className="grid gap-2">
                    <Label htmlFor="cor_secundaria">Cor Secundária</Label>
                    <div className="flex gap-2">
                      <Input
                        type="color"
                        id="cor_secundaria"
                        value={novaConfig.configuracao.cor_secundaria}
                        onChange={(e) => setNovaConfig({
                          ...novaConfig,
                          configuracao: {...novaConfig.configuracao, cor_secundaria: e.target.value}
                        })}
                        className="w-16 h-10"
                      />
                      <Input
                        value={novaConfig.configuracao.cor_secundaria}
                        onChange={(e) => setNovaConfig({
                          ...novaConfig,
                          configuracao: {...novaConfig.configuracao, cor_secundaria: e.target.value}
                        })}
                        placeholder="#6c757d"
                      />
                    </div>
                  </div>
                </div>
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <Label htmlFor="offline">Modo Offline</Label>
                    <Switch
                      id="offline"
                      checked={novaConfig.configuracao.modo_offline}
                      onCheckedChange={(checked) => setNovaConfig({
                        ...novaConfig,
                        configuracao: {...novaConfig.configuracao, modo_offline: checked}
                      })}
                    />
                  </div>
                  <div className="flex items-center justify-between">
                    <Label htmlFor="push">Notificações Push</Label>
                    <Switch
                      id="push"
                      checked={novaConfig.configuracao.notificacoes_push}
                      onCheckedChange={(checked) => setNovaConfig({
                        ...novaConfig,
                        configuracao: {...novaConfig.configuracao, notificacoes_push: checked}
                      })}
                    />
                  </div>
                </div>
              </div>
              <DialogFooter>
                <Button variant="outline" onClick={() => setShowNovaConfig(false)}>
                  Cancelar
                </Button>
                <Button onClick={criarConfiguracao}>Criar Configuração</Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>

          {selectedConfig && (
            <Button 
              variant="outline"
              onClick={() => setPreviewMode(!previewMode)}
            >
              <Eye className="mr-2 h-4 w-4" />
              {previewMode ? 'Sair do Preview' : 'Preview'}
            </Button>
          )}
        </div>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="configuracao">Configuração</TabsTrigger>
          <TabsTrigger value="recursos">Recursos</TabsTrigger>
          <TabsTrigger value="templates">Templates</TabsTrigger>
          <TabsTrigger value="publicacao">Publicação</TabsTrigger>
        </TabsList>

        <TabsContent value="configuracao" className="space-y-4">
          {selectedConfig ? (
            <div className="grid gap-6 md:grid-cols-2">
              <Card>
                <CardHeader>
                  <CardTitle>Informações Gerais</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid gap-2">
                    <Label>Nome da Configuração</Label>
                    <Input value={selectedConfig.nome} readOnly />
                  </div>
                  <div className="grid gap-2">
                    <Label>Nome do Aplicativo</Label>
                    <Input value={selectedConfig.configuracao.nome_app} />
                  </div>
                  <div className="grid gap-2">
                    <Label>Tipo</Label>
                    <Select value={selectedConfig.tipo} disabled>
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="pwa">Progressive Web App</SelectItem>
                        <SelectItem value="webapp">Web App</SelectItem>
                        <SelectItem value="mobile">App Mobile</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="grid gap-2">
                    <Label>Versão</Label>
                    <Input value={selectedConfig.versao} readOnly />
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Aparência</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid gap-2">
                    <Label>Cor Primária</Label>
                    <div className="flex gap-2">
                      <Input
                        type="color"
                        value={selectedConfig.configuracao.cor_primaria}
                        className="w-16 h-10"
                      />
                      <Input value={selectedConfig.configuracao.cor_primaria} />
                    </div>
                  </div>
                  <div className="grid gap-2">
                    <Label>Cor Secundária</Label>
                    <div className="flex gap-2">
                      <Input
                        type="color"
                        value={selectedConfig.configuracao.cor_secundaria}
                        className="w-16 h-10"
                      />
                      <Input value={selectedConfig.configuracao.cor_secundaria} />
                    </div>
                  </div>
                  <div className="grid gap-2">
                    <Label>Ícone do App</Label>
                    <div className="flex gap-2">
                      <Button variant="outline" size="sm">
                        <Upload className="mr-2 h-4 w-4" />
                        Upload
                      </Button>
                      {selectedConfig.configuracao.icone && (
                        <img 
                          src={selectedConfig.configuracao.icone} 
                          alt="App Icon" 
                          className="h-10 w-10 rounded"
                        />
                      )}
                    </div>
                  </div>
                  <div className="grid gap-2">
                    <Label>Splash Screen</Label>
                    <Button variant="outline" size="sm">
                      <Upload className="mr-2 h-4 w-4" />
                      Upload Splash
                    </Button>
                  </div>
                </CardContent>
              </Card>

              <Card className="md:col-span-2">
                <CardHeader>
                  <CardTitle>Configurações Avançadas</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid gap-4 md:grid-cols-2">
                    <div className="flex items-center justify-between">
                      <div>
                        <Label>Modo Offline</Label>
                        <p className="text-sm text-muted-foreground">Permite uso sem internet</p>
                      </div>
                      <Switch checked={selectedConfig.configuracao.modo_offline} />
                    </div>
                    <div className="flex items-center justify-between">
                      <div>
                        <Label>Notificações Push</Label>
                        <p className="text-sm text-muted-foreground">Enviar notificações</p>
                      </div>
                      <Switch checked={selectedConfig.configuracao.notificacoes_push} />
                    </div>
                  </div>
                </CardContent>
                <CardFooter>
                  <Button className="w-full">
                    Salvar Configurações
                  </Button>
                </CardFooter>
              </Card>
            </div>
          ) : (
            <Card>
              <CardContent className="text-center py-8">
                <AppWindow className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                <p className="text-muted-foreground">Nenhuma configuração selecionada</p>
                <Button 
                  className="mt-4"
                  onClick={() => setShowNovaConfig(true)}
                >
                  Criar Primeira Configuração
                </Button>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        <TabsContent value="recursos" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Recursos do Aplicativo</CardTitle>
              <CardDescription>
                Ative ou desative funcionalidades do seu app
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid gap-4 md:grid-cols-2">
                {recursos.map(recurso => (
                  <div key={recurso.id} className="flex items-center justify-between p-4 border rounded-lg">
                    <div className="flex items-start gap-3">
                      <span className="text-2xl">{recurso.icone}</span>
                      <div>
                        <h4 className="font-medium">{recurso.nome}</h4>
                        <p className="text-sm text-muted-foreground">{recurso.descricao}</p>
                        <Badge className={`mt-1 ${getCategoriaColor(recurso.categoria)}`}>
                          {recurso.categoria}
                        </Badge>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      {recurso.configuravel && (
                        <Button variant="ghost" size="icon">
                          <Settings className="h-4 w-4" />
                        </Button>
                      )}
                      <Switch
                        checked={selectedConfig?.recursos_ativos.includes(recurso.id) || false}
                        onCheckedChange={() => alternarRecurso(recurso.id)}
                        disabled={!selectedConfig}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="templates" className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {templates.map(template => (
              <Card key={template.id}>
                <CardHeader>
                  <CardTitle className="text-lg">{template.nome}</CardTitle>
                  <Badge variant="outline">{template.categoria}</Badge>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-muted-foreground mb-3">{template.descricao}</p>
                  <div className="space-y-2">
                    <p className="text-sm font-medium">Recursos incluídos:</p>
                    <div className="flex flex-wrap gap-1">
                      {template.recursos_incluidos.map(recurso => (
                        <Badge key={recurso} variant="secondary" className="text-xs">
                          {recurso}
                        </Badge>
                      ))}
                    </div>
                  </div>
                  {template.preco && (
                    <p className="mt-3 text-lg font-bold">R$ {template.preco.toFixed(2)}</p>
                  )}
                </CardContent>
                <CardFooter className="flex gap-2">
                  {template.preview_url && (
                    <Button variant="outline" size="sm" className="flex-1">
                      <Eye className="mr-1 h-3 w-3" />
                      Preview
                    </Button>
                  )}
                  <Button 
                    size="sm" 
                    className="flex-1"
                    onClick={() => aplicarTemplate(template.id)}
                  >
                    Usar Template
                  </Button>
                </CardFooter>
              </Card>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="publicacao" className="space-y-4">
          {selectedConfig ? (
            <div className="grid gap-6">
              <Card>
                <CardHeader>
                  <CardTitle>Status da Publicação</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="flex items-center justify-between p-4 border rounded-lg">
                    <div className="flex items-center gap-3">
                      {selectedConfig.publicado ? (
                        <CheckCircle className="h-8 w-8 text-green-500" />
                      ) : (
                        <Globe className="h-8 w-8 text-gray-400" />
                      )}
                      <div>
                        <p className="font-medium">
                          {selectedConfig.publicado ? 'Aplicativo Publicado' : 'Aplicativo Não Publicado'}
                        </p>
                        {selectedConfig.url_acesso && (
                          <a 
                            href={selectedConfig.url_acesso} 
                            target="_blank" 
                            rel="noopener noreferrer"
                            className="text-sm text-blue-500 hover:underline"
                          >
                            {selectedConfig.url_acesso}
                          </a>
                        )}
                      </div>
                    </div>
                    <Dialog open={showPublicar} onOpenChange={setShowPublicar}>
                      <DialogTrigger asChild>
                        <Button variant={selectedConfig.publicado ? 'outline' : 'default'}>
                          {selectedConfig.publicado ? 'Atualizar' : 'Publicar'}
                        </Button>
                      </DialogTrigger>
                      <DialogContent>
                        <DialogHeader>
                          <DialogTitle>Publicar Aplicativo</DialogTitle>
                          <DialogDescription>
                            Seu aplicativo será disponibilizado online
                          </DialogDescription>
                        </DialogHeader>
                        <div className="py-4">
                          <p className="text-sm text-muted-foreground">
                            Ao publicar, seu aplicativo ficará disponível em:
                          </p>
                          <div className="mt-2 p-3 bg-muted rounded font-mono text-sm">
                            https://app.seudominio.com/{selectedConfig.nome.toLowerCase().replace(/\s+/g, '-')}
                          </div>
                        </div>
                        <DialogFooter>
                          <Button variant="outline" onClick={() => setShowPublicar(false)}>
                            Cancelar
                          </Button>
                          <Button onClick={publicarApp}>
                            Confirmar Publicação
                          </Button>
                        </DialogFooter>
                      </DialogContent>
                    </Dialog>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Opções de Download</CardTitle>
                  <CardDescription>
                    Exporte seu aplicativo para diferentes plataformas
                  </CardDescription>
                </CardHeader>
                <CardContent className="grid gap-3 md:grid-cols-3">
                  <Button 
                    variant="outline" 
                    className="h-24 flex-col"
                    onClick={gerarPWA}
                  >
                    <Smartphone className="h-8 w-8 mb-2" />
                    <span>Gerar PWA</span>
                  </Button>
                  <Button variant="outline" className="h-24 flex-col" disabled>
                    <Download className="h-8 w-8 mb-2" />
                    <span>Exportar Código</span>
                  </Button>
                  <Button variant="outline" className="h-24 flex-col" disabled>
                    <Code className="h-8 w-8 mb-2" />
                    <span>API Docs</span>
                  </Button>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Instalação PWA</CardTitle>
                  <CardDescription>
                    Instruções para instalar o app em dispositivos
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <h4 className="font-medium mb-2">Android / Chrome</h4>
                    <ol className="text-sm text-muted-foreground space-y-1 list-decimal list-inside">
                      <li>Acesse o link do aplicativo no Chrome</li>
                      <li>Toque no menu (3 pontos) no canto superior</li>
                      <li>Selecione "Adicionar à tela inicial"</li>
                      <li>Confirme a instalação</li>
                    </ol>
                  </div>
                  <div>
                    <h4 className="font-medium mb-2">iOS / Safari</h4>
                    <ol className="text-sm text-muted-foreground space-y-1 list-decimal list-inside">
                      <li>Acesse o link do aplicativo no Safari</li>
                      <li>Toque no botão de compartilhamento</li>
                      <li>Selecione "Adicionar à Tela de Início"</li>
                      <li>Confirme a instalação</li>
                    </ol>
                  </div>
                </CardContent>
              </Card>
            </div>
          ) : (
            <Card>
              <CardContent className="text-center py-8">
                <Globe className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                <p className="text-muted-foreground">Selecione uma configuração para publicar</p>
              </CardContent>
            </Card>
          )}
        </TabsContent>
      </Tabs>
    </div>
  );
}