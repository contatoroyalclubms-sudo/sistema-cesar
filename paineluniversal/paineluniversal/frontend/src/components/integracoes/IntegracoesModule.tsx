import React, { useState, useEffect } from 'react';
import { Link2, Webhook, ShoppingBag, Package, Settings, CheckCircle, XCircle, AlertCircle, Plus, RefreshCw, Code, Globe, Key, TestTube } from 'lucide-react';
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
import { toast } from '@/hooks/use-toast';
import api from '@/utils/api';
import { formatDistanceToNow } from 'date-fns';
import { ptBR } from 'date-fns/locale';

interface Integracao {
  id: number;
  nome: string;
  tipo: 'api' | 'webhook' | 'marketplace' | 'pagamento' | 'crm' | 'email' | 'sms';
  provedor: string;
  configuracao: {
    api_key?: string;
    webhook_url?: string;
    secret?: string;
    endpoint?: string;
    headers?: Record<string, string>;
  };
  ativo: boolean;
  status: 'conectado' | 'desconectado' | 'erro';
  ultima_sincronizacao?: string;
  criado_em: string;
  atualizado_em: string;
}

interface Webhook {
  id: number;
  nome: string;
  url: string;
  eventos: string[];
  headers?: Record<string, string>;
  secret?: string;
  ativo: boolean;
  tentativas_erro: number;
  ultima_execucao?: string;
  ultimo_status?: number;
  criado_em: string;
}

interface Marketplace {
  id: number;
  nome: string;
  plataforma: 'mercadolivre' | 'shopee' | 'amazon' | 'magalu' | 'americanas';
  credenciais: {
    client_id?: string;
    client_secret?: string;
    access_token?: string;
    refresh_token?: string;
  };
  sincronizacao_produtos: boolean;
  sincronizacao_pedidos: boolean;
  sincronizacao_estoque: boolean;
  ultima_sincronizacao?: string;
  status: 'ativo' | 'pausado' | 'erro';
}

interface LogIntegracao {
  id: number;
  integracao_id: number;
  tipo: 'request' | 'response' | 'erro';
  metodo?: string;
  url?: string;
  status_code?: number;
  payload?: any;
  resposta?: any;
  erro?: string;
  criado_em: string;
}

export default function IntegracoesModule() {
  const [integracoes, setIntegracoes] = useState<Integracao[]>([]);
  const [webhooks, setWebhooks] = useState<Webhook[]>([]);
  const [marketplaces, setMarketplaces] = useState<Marketplace[]>([]);
  const [logs, setLogs] = useState<LogIntegracao[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('integracoes');
  const [showNovaIntegracao, setShowNovaIntegracao] = useState(false);
  const [showNovoWebhook, setShowNovoWebhook] = useState(false);
  const [showTesteWebhook, setShowTesteWebhook] = useState(false);
  const [webhookTeste, setWebhookTeste] = useState<Webhook | null>(null);

  const [novaIntegracao, setNovaIntegracao] = useState({
    nome: '',
    tipo: 'api' as const,
    provedor: '',
    configuracao: {
      api_key: '',
      endpoint: ''
    },
    ativo: true
  });

  const [novoWebhook, setNovoWebhook] = useState({
    nome: '',
    url: '',
    eventos: [] as string[],
    headers: {},
    secret: '',
    ativo: true
  });

  useEffect(() => {
    carregarDados();
  }, [activeTab]);

  const carregarDados = async () => {
    setLoading(true);
    try {
      if (activeTab === 'integracoes') {
        const response = await api.get('/api/integracoes');
        setIntegracoes(response.data);
      } else if (activeTab === 'webhooks') {
        const response = await api.get('/api/integracoes/webhooks');
        setWebhooks(response.data);
      } else if (activeTab === 'marketplace') {
        const response = await api.get('/api/integracoes/marketplace');
        setMarketplaces(response.data);
      } else if (activeTab === 'logs') {
        const response = await api.get('/api/integracoes/logs');
        setLogs(response.data);
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

  const criarIntegracao = async () => {
    try {
      await api.post('/api/integracoes', novaIntegracao);
      toast({
        title: "Sucesso",
        description: "Integração criada com sucesso"
      });
      setShowNovaIntegracao(false);
      setNovaIntegracao({
        nome: '',
        tipo: 'api',
        provedor: '',
        configuracao: {
          api_key: '',
          endpoint: ''
        },
        ativo: true
      });
      carregarDados();
    } catch (error) {
      console.error('Erro ao criar integração:', error);
      toast({
        title: "Erro",
        description: "Não foi possível criar a integração",
        variant: "destructive"
      });
    }
  };

  const criarWebhook = async () => {
    try {
      await api.post('/api/integracoes/webhooks', novoWebhook);
      toast({
        title: "Sucesso",
        description: "Webhook criado com sucesso"
      });
      setShowNovoWebhook(false);
      setNovoWebhook({
        nome: '',
        url: '',
        eventos: [],
        headers: {},
        secret: '',
        ativo: true
      });
      carregarDados();
    } catch (error) {
      console.error('Erro ao criar webhook:', error);
      toast({
        title: "Erro",
        description: "Não foi possível criar o webhook",
        variant: "destructive"
      });
    }
  };

  const testarIntegracao = async (integracaoId: number) => {
    try {
      const response = await api.post(`/api/integracoes/${integracaoId}/testar`);
      toast({
        title: "Sucesso",
        description: response.data.message || "Teste realizado com sucesso"
      });
      carregarDados();
    } catch (error) {
      console.error('Erro ao testar integração:', error);
      toast({
        title: "Erro",
        description: "Falha no teste da integração",
        variant: "destructive"
      });
    }
  };

  const testarWebhook = async () => {
    if (!webhookTeste) return;
    
    try {
      await api.post(`/api/integracoes/webhooks/${webhookTeste.id}/testar`);
      toast({
        title: "Sucesso",
        description: "Webhook testado com sucesso"
      });
      setShowTesteWebhook(false);
      setWebhookTeste(null);
    } catch (error) {
      console.error('Erro ao testar webhook:', error);
      toast({
        title: "Erro",
        description: "Falha no teste do webhook",
        variant: "destructive"
      });
    }
  };

  const sincronizarMarketplace = async (marketplaceId: number) => {
    try {
      await api.post(`/api/integracoes/marketplace/${marketplaceId}/sincronizar`);
      toast({
        title: "Sucesso",
        description: "Sincronização iniciada"
      });
      carregarDados();
    } catch (error) {
      console.error('Erro ao sincronizar marketplace:', error);
      toast({
        title: "Erro",
        description: "Não foi possível iniciar a sincronização",
        variant: "destructive"
      });
    }
  };

  const alternarIntegracao = async (integracaoId: number, ativo: boolean) => {
    try {
      await api.patch(`/api/integracoes/${integracaoId}`, { ativo });
      toast({
        title: "Sucesso",
        description: `Integração ${ativo ? 'ativada' : 'desativada'} com sucesso`
      });
      carregarDados();
    } catch (error) {
      console.error('Erro ao alterar integração:', error);
      toast({
        title: "Erro",
        description: "Não foi possível alterar o status da integração",
        variant: "destructive"
      });
    }
  };

  const alternarWebhook = async (webhookId: number, ativo: boolean) => {
    try {
      await api.patch(`/api/integracoes/webhooks/${webhookId}`, { ativo });
      toast({
        title: "Sucesso",
        description: `Webhook ${ativo ? 'ativado' : 'desativado'} com sucesso`
      });
      carregarDados();
    } catch (error) {
      console.error('Erro ao alterar webhook:', error);
      toast({
        title: "Erro",
        description: "Não foi possível alterar o status do webhook",
        variant: "destructive"
      });
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'conectado':
      case 'ativo':
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'desconectado':
      case 'pausado':
        return <XCircle className="h-4 w-4 text-gray-500" />;
      case 'erro':
        return <AlertCircle className="h-4 w-4 text-red-500" />;
      default:
        return null;
    }
  };

  const getProvedorIcon = (provedor: string) => {
    switch (provedor.toLowerCase()) {
      case 'stripe':
      case 'pagarme':
      case 'mercadopago':
        return '💳';
      case 'whatsapp':
      case 'telegram':
        return '💬';
      case 'sendgrid':
      case 'mailgun':
        return '📧';
      case 'twilio':
        return '📱';
      default:
        return '🔗';
    }
  };

  return (
    <div className="container mx-auto py-6 space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">Integrações</h1>
          <p className="text-muted-foreground">Conecte-se com serviços externos e APIs</p>
        </div>
        <div className="flex gap-2">
          <Dialog open={showNovaIntegracao} onOpenChange={setShowNovaIntegracao}>
            <DialogTrigger asChild>
              <Button>
                <Plus className="mr-2 h-4 w-4" />
                Nova Integração
              </Button>
            </DialogTrigger>
            <DialogContent className="sm:max-w-[500px]">
              <DialogHeader>
                <DialogTitle>Adicionar Integração</DialogTitle>
                <DialogDescription>
                  Configure uma nova integração com serviços externos
                </DialogDescription>
              </DialogHeader>
              <div className="grid gap-4 py-4">
                <div className="grid gap-2">
                  <Label htmlFor="nome">Nome</Label>
                  <Input
                    id="nome"
                    value={novaIntegracao.nome}
                    onChange={(e) => setNovaIntegracao({...novaIntegracao, nome: e.target.value})}
                    placeholder="Ex: Stripe Pagamentos"
                  />
                </div>
                <div className="grid gap-2">
                  <Label htmlFor="tipo">Tipo</Label>
                  <Select
                    value={novaIntegracao.tipo}
                    onValueChange={(value: any) => setNovaIntegracao({...novaIntegracao, tipo: value})}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="api">API REST</SelectItem>
                      <SelectItem value="webhook">Webhook</SelectItem>
                      <SelectItem value="marketplace">Marketplace</SelectItem>
                      <SelectItem value="pagamento">Pagamento</SelectItem>
                      <SelectItem value="crm">CRM</SelectItem>
                      <SelectItem value="email">Email</SelectItem>
                      <SelectItem value="sms">SMS</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="grid gap-2">
                  <Label htmlFor="provedor">Provedor</Label>
                  <Input
                    id="provedor"
                    value={novaIntegracao.provedor}
                    onChange={(e) => setNovaIntegracao({...novaIntegracao, provedor: e.target.value})}
                    placeholder="Ex: Stripe, MercadoPago, SendGrid"
                  />
                </div>
                <div className="grid gap-2">
                  <Label htmlFor="api_key">API Key</Label>
                  <Input
                    id="api_key"
                    type="password"
                    value={novaIntegracao.configuracao.api_key}
                    onChange={(e) => setNovaIntegracao({
                      ...novaIntegracao,
                      configuracao: {...novaIntegracao.configuracao, api_key: e.target.value}
                    })}
                    placeholder="sk_live_..."
                  />
                </div>
                <div className="grid gap-2">
                  <Label htmlFor="endpoint">Endpoint</Label>
                  <Input
                    id="endpoint"
                    value={novaIntegracao.configuracao.endpoint}
                    onChange={(e) => setNovaIntegracao({
                      ...novaIntegracao,
                      configuracao: {...novaIntegracao.configuracao, endpoint: e.target.value}
                    })}
                    placeholder="https://api.exemplo.com/v1"
                  />
                </div>
                <div className="flex items-center space-x-2">
                  <Switch
                    id="ativo"
                    checked={novaIntegracao.ativo}
                    onCheckedChange={(checked) => setNovaIntegracao({...novaIntegracao, ativo: checked})}
                  />
                  <Label htmlFor="ativo">Ativar imediatamente</Label>
                </div>
              </div>
              <DialogFooter>
                <Button variant="outline" onClick={() => setShowNovaIntegracao(false)}>
                  Cancelar
                </Button>
                <Button onClick={criarIntegracao}>Adicionar</Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>

          <Dialog open={showNovoWebhook} onOpenChange={setShowNovoWebhook}>
            <DialogTrigger asChild>
              <Button variant="outline">
                <Webhook className="mr-2 h-4 w-4" />
                Novo Webhook
              </Button>
            </DialogTrigger>
            <DialogContent className="sm:max-w-[500px]">
              <DialogHeader>
                <DialogTitle>Criar Webhook</DialogTitle>
                <DialogDescription>
                  Configure um endpoint para receber eventos
                </DialogDescription>
              </DialogHeader>
              <div className="grid gap-4 py-4">
                <div className="grid gap-2">
                  <Label htmlFor="nome-webhook">Nome</Label>
                  <Input
                    id="nome-webhook"
                    value={novoWebhook.nome}
                    onChange={(e) => setNovoWebhook({...novoWebhook, nome: e.target.value})}
                    placeholder="Ex: Notificação de Compra"
                  />
                </div>
                <div className="grid gap-2">
                  <Label htmlFor="url">URL</Label>
                  <Input
                    id="url"
                    value={novoWebhook.url}
                    onChange={(e) => setNovoWebhook({...novoWebhook, url: e.target.value})}
                    placeholder="https://seu-servidor.com/webhook"
                  />
                </div>
                <div className="grid gap-2">
                  <Label htmlFor="eventos">Eventos</Label>
                  <Input
                    id="eventos"
                    value={novoWebhook.eventos.join(', ')}
                    onChange={(e) => setNovoWebhook({...novoWebhook, eventos: e.target.value.split(',').map(s => s.trim())})}
                    placeholder="compra.criada, checkin.realizado"
                  />
                </div>
                <div className="grid gap-2">
                  <Label htmlFor="secret">Secret (opcional)</Label>
                  <Input
                    id="secret"
                    type="password"
                    value={novoWebhook.secret}
                    onChange={(e) => setNovoWebhook({...novoWebhook, secret: e.target.value})}
                    placeholder="Chave secreta para validação"
                  />
                </div>
                <div className="flex items-center space-x-2">
                  <Switch
                    id="ativo-webhook"
                    checked={novoWebhook.ativo}
                    onCheckedChange={(checked) => setNovoWebhook({...novoWebhook, ativo: checked})}
                  />
                  <Label htmlFor="ativo-webhook">Ativar imediatamente</Label>
                </div>
              </div>
              <DialogFooter>
                <Button variant="outline" onClick={() => setShowNovoWebhook(false)}>
                  Cancelar
                </Button>
                <Button onClick={criarWebhook}>Criar</Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>
        </div>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="integracoes">Integrações</TabsTrigger>
          <TabsTrigger value="webhooks">Webhooks</TabsTrigger>
          <TabsTrigger value="marketplace">Marketplace</TabsTrigger>
          <TabsTrigger value="logs">Logs</TabsTrigger>
        </TabsList>

        <TabsContent value="integracoes" className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {integracoes.map(integracao => (
              <Card key={integracao.id}>
                <CardHeader>
                  <div className="flex justify-between items-start">
                    <div className="space-y-1">
                      <CardTitle className="text-lg flex items-center gap-2">
                        <span className="text-2xl">{getProvedorIcon(integracao.provedor)}</span>
                        {integracao.nome}
                      </CardTitle>
                      <div className="flex gap-2">
                        <Badge variant="outline">{integracao.tipo}</Badge>
                        <Badge variant="secondary">{integracao.provedor}</Badge>
                      </div>
                    </div>
                    <Switch
                      checked={integracao.ativo}
                      onCheckedChange={(checked) => alternarIntegracao(integracao.id, checked)}
                    />
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="flex items-center gap-2 mb-2">
                    {getStatusIcon(integracao.status)}
                    <span className="text-sm capitalize">{integracao.status}</span>
                  </div>
                  {integracao.ultima_sincronizacao && (
                    <p className="text-sm text-muted-foreground">
                      Última sync: {formatDistanceToNow(new Date(integracao.ultima_sincronizacao), { addSuffix: true, locale: ptBR })}
                    </p>
                  )}
                  {integracao.configuracao.endpoint && (
                    <div className="mt-2 p-2 bg-muted rounded text-xs font-mono truncate">
                      {integracao.configuracao.endpoint}
                    </div>
                  )}
                </CardContent>
                <CardFooter className="flex gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => testarIntegracao(integracao.id)}
                  >
                    <TestTube className="mr-1 h-3 w-3" />
                    Testar
                  </Button>
                  <Button variant="outline" size="sm">
                    <Settings className="mr-1 h-3 w-3" />
                    Configurar
                  </Button>
                </CardFooter>
              </Card>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="webhooks" className="space-y-4">
          <div className="grid gap-4">
            {webhooks.map(webhook => (
              <Card key={webhook.id}>
                <CardHeader>
                  <div className="flex justify-between items-center">
                    <div>
                      <CardTitle className="text-lg">{webhook.nome}</CardTitle>
                      <CardDescription className="mt-1 font-mono text-xs">
                        {webhook.url}
                      </CardDescription>
                    </div>
                    <div className="flex items-center gap-2">
                      <Switch
                        checked={webhook.ativo}
                        onCheckedChange={(checked) => alternarWebhook(webhook.id, checked)}
                      />
                      {webhook.ativo ? (
                        <Badge className="bg-green-100 text-green-800">Ativo</Badge>
                      ) : (
                        <Badge variant="secondary">Inativo</Badge>
                      )}
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="grid gap-3">
                    <div>
                      <p className="text-sm font-medium mb-1">Eventos monitorados:</p>
                      <div className="flex flex-wrap gap-1">
                        {webhook.eventos.map(evento => (
                          <Badge key={evento} variant="outline" className="text-xs">
                            {evento}
                          </Badge>
                        ))}
                      </div>
                    </div>
                    <div className="grid grid-cols-2 gap-4 text-sm">
                      <div>
                        <p className="text-muted-foreground">Última execução:</p>
                        <p className="font-medium">
                          {webhook.ultima_execucao 
                            ? formatDistanceToNow(new Date(webhook.ultima_execucao), { addSuffix: true, locale: ptBR })
                            : 'Nunca'}
                        </p>
                      </div>
                      <div>
                        <p className="text-muted-foreground">Status:</p>
                        <p className="font-medium flex items-center gap-1">
                          {webhook.ultimo_status ? (
                            <>
                              {webhook.ultimo_status >= 200 && webhook.ultimo_status < 300 ? (
                                <CheckCircle className="h-3 w-3 text-green-500" />
                              ) : (
                                <XCircle className="h-3 w-3 text-red-500" />
                              )}
                              HTTP {webhook.ultimo_status}
                            </>
                          ) : (
                            'N/A'
                          )}
                        </p>
                      </div>
                    </div>
                    {webhook.tentativas_erro > 0 && (
                      <div className="flex items-center gap-2 text-sm text-red-600">
                        <AlertCircle className="h-4 w-4" />
                        <span>{webhook.tentativas_erro} tentativas com erro</span>
                      </div>
                    )}
                  </div>
                </CardContent>
                <CardFooter>
                  <Button
                    variant="outline"
                    size="sm"
                    className="w-full"
                    onClick={() => {
                      setWebhookTeste(webhook);
                      setShowTesteWebhook(true);
                    }}
                  >
                    <TestTube className="mr-2 h-4 w-4" />
                    Enviar Teste
                  </Button>
                </CardFooter>
              </Card>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="marketplace" className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2">
            {marketplaces.map(marketplace => (
              <Card key={marketplace.id}>
                <CardHeader>
                  <div className="flex justify-between items-start">
                    <div>
                      <CardTitle className="text-lg">{marketplace.nome}</CardTitle>
                      <Badge variant="outline" className="mt-1">
                        {marketplace.plataforma}
                      </Badge>
                    </div>
                    {getStatusIcon(marketplace.status)}
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    <div className="flex items-center justify-between text-sm">
                      <span>Sincronizar produtos</span>
                      <Switch checked={marketplace.sincronizacao_produtos} disabled />
                    </div>
                    <div className="flex items-center justify-between text-sm">
                      <span>Sincronizar pedidos</span>
                      <Switch checked={marketplace.sincronizacao_pedidos} disabled />
                    </div>
                    <div className="flex items-center justify-between text-sm">
                      <span>Sincronizar estoque</span>
                      <Switch checked={marketplace.sincronizacao_estoque} disabled />
                    </div>
                  </div>
                  {marketplace.ultima_sincronizacao && (
                    <p className="text-sm text-muted-foreground mt-3">
                      Última sync: {formatDistanceToNow(new Date(marketplace.ultima_sincronizacao), { addSuffix: true, locale: ptBR })}
                    </p>
                  )}
                </CardContent>
                <CardFooter className="flex gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => sincronizarMarketplace(marketplace.id)}
                  >
                    <RefreshCw className="mr-1 h-3 w-3" />
                    Sincronizar
                  </Button>
                  <Button variant="outline" size="sm">
                    <Settings className="mr-1 h-3 w-3" />
                    Configurar
                  </Button>
                </CardFooter>
              </Card>
            ))}
          </div>

          {marketplaces.length === 0 && (
            <Card>
              <CardContent className="text-center py-8">
                <ShoppingBag className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                <p className="text-muted-foreground">Nenhuma integração com marketplace configurada</p>
                <Button className="mt-4">
                  <Plus className="mr-2 h-4 w-4" />
                  Conectar Marketplace
                </Button>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        <TabsContent value="logs" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Logs de Integração</CardTitle>
              <CardDescription>
                Histórico de requisições e respostas das integrações
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {logs.map(log => (
                  <div key={log.id} className="flex items-center justify-between p-3 border rounded-lg">
                    <div className="flex items-center gap-3">
                      <div className={`p-2 rounded ${
                        log.tipo === 'erro' ? 'bg-red-100 text-red-600' :
                        log.tipo === 'request' ? 'bg-blue-100 text-blue-600' :
                        'bg-green-100 text-green-600'
                      }`}>
                        <Code className="h-4 w-4" />
                      </div>
                      <div>
                        <p className="font-medium text-sm">
                          {log.metodo} {log.url}
                        </p>
                        <p className="text-xs text-muted-foreground">
                          {formatDistanceToNow(new Date(log.criado_em), { addSuffix: true, locale: ptBR })}
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      {log.status_code && (
                        <Badge variant={log.status_code >= 200 && log.status_code < 300 ? 'default' : 'destructive'}>
                          {log.status_code}
                        </Badge>
                      )}
                      <Badge variant="outline">{log.tipo}</Badge>
                      <Button variant="ghost" size="sm">
                        Ver detalhes
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      <Dialog open={showTesteWebhook} onOpenChange={setShowTesteWebhook}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Testar Webhook</DialogTitle>
            <DialogDescription>
              Envie um evento de teste para {webhookTeste?.nome}
            </DialogDescription>
          </DialogHeader>
          <div className="py-4">
            <p className="text-sm text-muted-foreground mb-4">
              Um evento de teste será enviado para:
            </p>
            <div className="p-3 bg-muted rounded font-mono text-sm">
              {webhookTeste?.url}
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowTesteWebhook(false)}>
              Cancelar
            </Button>
            <Button onClick={testarWebhook}>
              Enviar Teste
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}