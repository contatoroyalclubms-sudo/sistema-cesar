import React, { useState, useEffect } from 'react';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
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
  DialogTrigger,
} from '@/components/ui/dialog';
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
import { Switch } from '@/components/ui/switch';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  Plus, 
  Edit, 
  Trash2, 
  DollarSign, 
  Percent,
  Package,
  Users,
  Building,
  UserCheck,
  AlertCircle,
  CheckCircle,
  Clock
} from 'lucide-react';
import { useToast } from '@/components/ui/use-toast';
import api from '@/lib/api';

interface SplitRule {
  id: number;
  nome: string;
  descricao: string;
  beneficiario_tipo: string;
  beneficiario_nome: string;
  tipo_calculo: 'percentual' | 'valor_fixo' | 'valor_por_item';
  valor: number;
  prioridade: number;
  ativo: boolean;
  total_execucoes?: number;
  valor_total_processado?: number;
}

interface DadosPagamento {
  tipo: 'pix' | 'conta_bancaria';
  chave_pix?: string;
  tipo_chave_pix?: string;
  banco?: string;
  agencia?: string;
  conta?: string;
  tipo_conta?: string;
  cpf_cnpj?: string;
  nome_completo?: string;
}

export default function SplitRulesConfig({ eventoId }: { eventoId?: number }) {
  const [rules, setRules] = useState<SplitRule[]>([]);
  const [loading, setLoading] = useState(true);
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [editingRule, setEditingRule] = useState<SplitRule | null>(null);
  const { toast } = useToast();

  // Estados do formulário
  const [formData, setFormData] = useState({
    nome: '',
    descricao: '',
    beneficiario_tipo: 'parceiro',
    beneficiario_id: '',
    beneficiario_nome: '',
    tipo_calculo: 'percentual',
    valor: 0,
    prioridade: 0,
    ativo: true,
    dados_pagamento: {
      tipo: 'pix',
      chave_pix: '',
      tipo_chave_pix: 'cpf',
      cpf_cnpj: '',
      nome_completo: ''
    } as DadosPagamento,
    condicoes: {
      min_valor: undefined as number | undefined,
      max_valor: undefined as number | undefined,
      produto_ids: [] as number[],
      categoria_ids: [] as number[]
    }
  });

  useEffect(() => {
    fetchRules();
  }, [eventoId]);

  const fetchRules = async () => {
    try {
      setLoading(true);
      const params = eventoId ? { evento_id: eventoId } : {};
      const response = await api.get('/api/split/rules', { params });
      setRules(response.data);
    } catch (error) {
      toast({
        title: "Erro",
        description: "Não foi possível carregar as regras de split",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async () => {
    try {
      const payload = {
        ...formData,
        evento_id: eventoId,
        valor: parseFloat(formData.valor.toString())
      };

      if (editingRule) {
        await api.put(`/api/split/rules/${editingRule.id}`, payload);
        toast({
          title: "Sucesso",
          description: "Regra atualizada com sucesso",
        });
      } else {
        await api.post('/api/split/rules', payload);
        toast({
          title: "Sucesso",
          description: "Regra criada com sucesso",
        });
      }

      setIsDialogOpen(false);
      resetForm();
      fetchRules();
    } catch (error) {
      toast({
        title: "Erro",
        description: "Não foi possível salvar a regra",
        variant: "destructive",
      });
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm('Tem certeza que deseja desativar esta regra?')) return;

    try {
      await api.delete(`/api/split/rules/${id}`);
      toast({
        title: "Sucesso",
        description: "Regra desativada com sucesso",
      });
      fetchRules();
    } catch (error) {
      toast({
        title: "Erro",
        description: "Não foi possível desativar a regra",
        variant: "destructive",
      });
    }
  };

  const resetForm = () => {
    setFormData({
      nome: '',
      descricao: '',
      beneficiario_tipo: 'parceiro',
      beneficiario_id: '',
      beneficiario_nome: '',
      tipo_calculo: 'percentual',
      valor: 0,
      prioridade: 0,
      ativo: true,
      dados_pagamento: {
        tipo: 'pix',
        chave_pix: '',
        tipo_chave_pix: 'cpf',
        cpf_cnpj: '',
        nome_completo: ''
      },
      condicoes: {
        min_valor: undefined,
        max_valor: undefined,
        produto_ids: [],
        categoria_ids: []
      }
    });
    setEditingRule(null);
  };

  const getTipoCalculoIcon = (tipo: string) => {
    switch (tipo) {
      case 'percentual':
        return <Percent className="h-4 w-4" />;
      case 'valor_fixo':
        return <DollarSign className="h-4 w-4" />;
      case 'valor_por_item':
        return <Package className="h-4 w-4" />;
      default:
        return null;
    }
  };

  const getBeneficiarioIcon = (tipo: string) => {
    switch (tipo) {
      case 'empresa':
        return <Building className="h-4 w-4" />;
      case 'parceiro':
        return <Users className="h-4 w-4" />;
      case 'promoter':
      case 'vendedor':
        return <UserCheck className="h-4 w-4" />;
      default:
        return <Users className="h-4 w-4" />;
    }
  };

  const formatValue = (rule: SplitRule) => {
    if (rule.tipo_calculo === 'percentual') {
      return `${rule.valor}%`;
    }
    return `R$ ${rule.valor.toFixed(2)}`;
  };

  return (
    <Card>
      <CardHeader>
        <div className="flex justify-between items-center">
          <div>
            <CardTitle>Regras de Split de Pagamento</CardTitle>
            <CardDescription>
              Configure como as receitas serão divididas entre os beneficiários
            </CardDescription>
          </div>
          <Button onClick={() => setIsDialogOpen(true)}>
            <Plus className="mr-2 h-4 w-4" />
            Nova Regra
          </Button>
        </div>
      </CardHeader>
      <CardContent>
        {loading ? (
          <div className="text-center py-8">Carregando...</div>
        ) : rules.length === 0 ? (
          <div className="text-center py-8 text-muted-foreground">
            <DollarSign className="mx-auto h-12 w-12 mb-4 opacity-50" />
            <p>Nenhuma regra de split configurada</p>
            <p className="text-sm mt-2">Crie a primeira regra para começar a dividir receitas</p>
          </div>
        ) : (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Regra</TableHead>
                <TableHead>Beneficiário</TableHead>
                <TableHead>Cálculo</TableHead>
                <TableHead>Valor</TableHead>
                <TableHead>Prioridade</TableHead>
                <TableHead>Execuções</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Ações</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {rules.map((rule) => (
                <TableRow key={rule.id}>
                  <TableCell>
                    <div>
                      <p className="font-medium">{rule.nome}</p>
                      {rule.descricao && (
                        <p className="text-sm text-muted-foreground">{rule.descricao}</p>
                      )}
                    </div>
                  </TableCell>
                  <TableCell>
                    <div className="flex items-center gap-2">
                      {getBeneficiarioIcon(rule.beneficiario_tipo)}
                      <div>
                        <p className="text-sm">{rule.beneficiario_nome}</p>
                        <p className="text-xs text-muted-foreground">{rule.beneficiario_tipo}</p>
                      </div>
                    </div>
                  </TableCell>
                  <TableCell>
                    <div className="flex items-center gap-2">
                      {getTipoCalculoIcon(rule.tipo_calculo)}
                      <span className="text-sm">{rule.tipo_calculo}</span>
                    </div>
                  </TableCell>
                  <TableCell className="font-medium">
                    {formatValue(rule)}
                  </TableCell>
                  <TableCell>
                    <Badge variant="outline">{rule.prioridade}</Badge>
                  </TableCell>
                  <TableCell>
                    {rule.total_execucoes ? (
                      <div className="text-sm">
                        <p>{rule.total_execucoes} splits</p>
                        <p className="text-muted-foreground">
                          R$ {(rule.valor_total_processado || 0).toFixed(2)}
                        </p>
                      </div>
                    ) : (
                      <span className="text-sm text-muted-foreground">-</span>
                    )}
                  </TableCell>
                  <TableCell>
                    <Badge variant={rule.ativo ? "success" : "secondary"}>
                      {rule.ativo ? "Ativo" : "Inativo"}
                    </Badge>
                  </TableCell>
                  <TableCell>
                    <div className="flex gap-2">
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => {
                          setEditingRule(rule);
                          setFormData({
                            ...rule,
                            dados_pagamento: formData.dados_pagamento,
                            condicoes: formData.condicoes
                          } as any);
                          setIsDialogOpen(true);
                        }}
                      >
                        <Edit className="h-4 w-4" />
                      </Button>
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => handleDelete(rule.id)}
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        )}

        {/* Dialog para criar/editar regra */}
        <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
          <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
            <DialogHeader>
              <DialogTitle>
                {editingRule ? 'Editar Regra de Split' : 'Nova Regra de Split'}
              </DialogTitle>
              <DialogDescription>
                Configure como esta receita será dividida
              </DialogDescription>
            </DialogHeader>

            <Tabs defaultValue="basico" className="mt-4">
              <TabsList className="grid w-full grid-cols-3">
                <TabsTrigger value="basico">Informações Básicas</TabsTrigger>
                <TabsTrigger value="pagamento">Dados de Pagamento</TabsTrigger>
                <TabsTrigger value="condicoes">Condições</TabsTrigger>
              </TabsList>

              <TabsContent value="basico" className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="nome">Nome da Regra</Label>
                    <Input
                      id="nome"
                      value={formData.nome}
                      onChange={(e) => setFormData({...formData, nome: e.target.value})}
                      placeholder="Ex: Comissão Vendedor"
                    />
                  </div>
                  <div>
                    <Label htmlFor="prioridade">Prioridade</Label>
                    <Input
                      id="prioridade"
                      type="number"
                      min="0"
                      max="999"
                      value={formData.prioridade}
                      onChange={(e) => setFormData({...formData, prioridade: parseInt(e.target.value)})}
                    />
                  </div>
                </div>

                <div>
                  <Label htmlFor="descricao">Descrição</Label>
                  <Input
                    id="descricao"
                    value={formData.descricao}
                    onChange={(e) => setFormData({...formData, descricao: e.target.value})}
                    placeholder="Descrição opcional da regra"
                  />
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="beneficiario_tipo">Tipo de Beneficiário</Label>
                    <Select
                      value={formData.beneficiario_tipo}
                      onValueChange={(value) => setFormData({...formData, beneficiario_tipo: value})}
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="empresa">Empresa</SelectItem>
                        <SelectItem value="fornecedor">Fornecedor</SelectItem>
                        <SelectItem value="parceiro">Parceiro</SelectItem>
                        <SelectItem value="promoter">Promoter</SelectItem>
                        <SelectItem value="vendedor">Vendedor</SelectItem>
                        <SelectItem value="afiliado">Afiliado</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div>
                    <Label htmlFor="beneficiario_nome">Nome do Beneficiário</Label>
                    <Input
                      id="beneficiario_nome"
                      value={formData.beneficiario_nome}
                      onChange={(e) => setFormData({...formData, beneficiario_nome: e.target.value})}
                      placeholder="Nome completo"
                    />
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="tipo_calculo">Tipo de Cálculo</Label>
                    <Select
                      value={formData.tipo_calculo}
                      onValueChange={(value) => setFormData({...formData, tipo_calculo: value as any})}
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="percentual">Percentual</SelectItem>
                        <SelectItem value="valor_fixo">Valor Fixo</SelectItem>
                        <SelectItem value="valor_por_item">Valor por Item</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div>
                    <Label htmlFor="valor">
                      {formData.tipo_calculo === 'percentual' ? 'Percentual (%)' : 'Valor (R$)'}
                    </Label>
                    <Input
                      id="valor"
                      type="number"
                      step="0.01"
                      min="0"
                      max={formData.tipo_calculo === 'percentual' ? "100" : undefined}
                      value={formData.valor}
                      onChange={(e) => setFormData({...formData, valor: parseFloat(e.target.value)})}
                    />
                  </div>
                </div>

                <div className="flex items-center space-x-2">
                  <Switch
                    id="ativo"
                    checked={formData.ativo}
                    onCheckedChange={(checked) => setFormData({...formData, ativo: checked})}
                  />
                  <Label htmlFor="ativo">Regra ativa</Label>
                </div>
              </TabsContent>

              <TabsContent value="pagamento" className="space-y-4">
                <div>
                  <Label htmlFor="tipo_pagamento">Tipo de Pagamento</Label>
                  <Select
                    value={formData.dados_pagamento.tipo}
                    onValueChange={(value) => setFormData({
                      ...formData,
                      dados_pagamento: {...formData.dados_pagamento, tipo: value as any}
                    })}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="pix">PIX</SelectItem>
                      <SelectItem value="conta_bancaria">Conta Bancária</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                {formData.dados_pagamento.tipo === 'pix' ? (
                  <>
                    <div>
                      <Label htmlFor="tipo_chave_pix">Tipo de Chave PIX</Label>
                      <Select
                        value={formData.dados_pagamento.tipo_chave_pix}
                        onValueChange={(value) => setFormData({
                          ...formData,
                          dados_pagamento: {...formData.dados_pagamento, tipo_chave_pix: value}
                        })}
                      >
                        <SelectTrigger>
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="cpf">CPF</SelectItem>
                          <SelectItem value="cnpj">CNPJ</SelectItem>
                          <SelectItem value="email">E-mail</SelectItem>
                          <SelectItem value="telefone">Telefone</SelectItem>
                          <SelectItem value="aleatorio">Chave Aleatória</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                    <div>
                      <Label htmlFor="chave_pix">Chave PIX</Label>
                      <Input
                        id="chave_pix"
                        value={formData.dados_pagamento.chave_pix}
                        onChange={(e) => setFormData({
                          ...formData,
                          dados_pagamento: {...formData.dados_pagamento, chave_pix: e.target.value}
                        })}
                        placeholder="Digite a chave PIX"
                      />
                    </div>
                  </>
                ) : (
                  <>
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <Label htmlFor="banco">Banco</Label>
                        <Input
                          id="banco"
                          value={formData.dados_pagamento.banco}
                          onChange={(e) => setFormData({
                            ...formData,
                            dados_pagamento: {...formData.dados_pagamento, banco: e.target.value}
                          })}
                          placeholder="Ex: 001"
                        />
                      </div>
                      <div>
                        <Label htmlFor="agencia">Agência</Label>
                        <Input
                          id="agencia"
                          value={formData.dados_pagamento.agencia}
                          onChange={(e) => setFormData({
                            ...formData,
                            dados_pagamento: {...formData.dados_pagamento, agencia: e.target.value}
                          })}
                          placeholder="Ex: 1234"
                        />
                      </div>
                    </div>
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <Label htmlFor="conta">Conta</Label>
                        <Input
                          id="conta"
                          value={formData.dados_pagamento.conta}
                          onChange={(e) => setFormData({
                            ...formData,
                            dados_pagamento: {...formData.dados_pagamento, conta: e.target.value}
                          })}
                          placeholder="Ex: 12345-6"
                        />
                      </div>
                      <div>
                        <Label htmlFor="tipo_conta">Tipo de Conta</Label>
                        <Select
                          value={formData.dados_pagamento.tipo_conta}
                          onValueChange={(value) => setFormData({
                            ...formData,
                            dados_pagamento: {...formData.dados_pagamento, tipo_conta: value}
                          })}
                        >
                          <SelectTrigger>
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="corrente">Corrente</SelectItem>
                            <SelectItem value="poupanca">Poupança</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>
                    </div>
                  </>
                )}

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="cpf_cnpj">CPF/CNPJ</Label>
                    <Input
                      id="cpf_cnpj"
                      value={formData.dados_pagamento.cpf_cnpj}
                      onChange={(e) => setFormData({
                        ...formData,
                        dados_pagamento: {...formData.dados_pagamento, cpf_cnpj: e.target.value}
                      })}
                      placeholder="Digite o CPF ou CNPJ"
                    />
                  </div>
                  <div>
                    <Label htmlFor="nome_completo">Nome Completo</Label>
                    <Input
                      id="nome_completo"
                      value={formData.dados_pagamento.nome_completo}
                      onChange={(e) => setFormData({
                        ...formData,
                        dados_pagamento: {...formData.dados_pagamento, nome_completo: e.target.value}
                      })}
                      placeholder="Nome completo do beneficiário"
                    />
                  </div>
                </div>
              </TabsContent>

              <TabsContent value="condicoes" className="space-y-4">
                <div className="space-y-4">
                  <p className="text-sm text-muted-foreground">
                    Configure condições opcionais para quando esta regra deve ser aplicada
                  </p>
                  
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <Label htmlFor="min_valor">Valor Mínimo da Venda (R$)</Label>
                      <Input
                        id="min_valor"
                        type="number"
                        step="0.01"
                        value={formData.condicoes.min_valor || ''}
                        onChange={(e) => setFormData({
                          ...formData,
                          condicoes: {
                            ...formData.condicoes,
                            min_valor: e.target.value ? parseFloat(e.target.value) : undefined
                          }
                        })}
                        placeholder="Opcional"
                      />
                    </div>
                    <div>
                      <Label htmlFor="max_valor">Valor Máximo da Venda (R$)</Label>
                      <Input
                        id="max_valor"
                        type="number"
                        step="0.01"
                        value={formData.condicoes.max_valor || ''}
                        onChange={(e) => setFormData({
                          ...formData,
                          condicoes: {
                            ...formData.condicoes,
                            max_valor: e.target.value ? parseFloat(e.target.value) : undefined
                          }
                        })}
                        placeholder="Opcional"
                      />
                    </div>
                  </div>

                  <div className="p-4 bg-muted rounded-lg">
                    <p className="text-sm font-medium mb-2">Condições Avançadas</p>
                    <p className="text-xs text-muted-foreground">
                      Funcionalidades como restrição por produtos, categorias, dias da semana e horários 
                      serão implementadas em breve.
                    </p>
                  </div>
                </div>
              </TabsContent>
            </Tabs>

            <DialogFooter>
              <Button variant="outline" onClick={() => {
                setIsDialogOpen(false);
                resetForm();
              }}>
                Cancelar
              </Button>
              <Button onClick={handleSubmit}>
                {editingRule ? 'Salvar Alterações' : 'Criar Regra'}
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </CardContent>
    </Card>
  );
}