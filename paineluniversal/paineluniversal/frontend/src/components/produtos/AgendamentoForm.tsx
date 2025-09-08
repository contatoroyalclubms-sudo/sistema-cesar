import React, { useState, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Textarea } from '../ui/textarea';
import {
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '../ui/form';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '../ui/select';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '../ui/dialog';
import { Checkbox } from '../ui/checkbox';
import { Calendar } from '../ui/calendar';
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from '../ui/popover';
import { cn } from '../../lib/utils';
import { format } from 'date-fns';
import { ptBR } from 'date-fns/locale';
import { CalendarIcon, Clock, Users, Tag, Package } from 'lucide-react';
import { AgendamentoProduto, Produto } from '../../types/produto';
import { Badge } from '../ui/badge';

const agendamentoSchema = z.object({
  nome: z.string()
    .min(3, 'Nome deve ter pelo menos 3 caracteres')
    .max(100, 'Nome não pode ter mais de 100 caracteres'),
  
  tipo: z.enum(['promocao', 'evento', 'sazonal']),
  
  regra: z.string()
    .min(5, 'Regra deve ter pelo menos 5 caracteres')
    .max(200, 'Regra não pode ter mais de 200 caracteres'),
  
  data_inicio: z.date(),
  
  data_fim: z.date(),
  
  produtos: z.array(z.string()).min(1, 'Selecione pelo menos um produto'),
  
  ativo: z.boolean(),
  
  descricao: z.string().max(500, 'Descrição não pode ter mais de 500 caracteres').optional(),
}).refine((data) => data.data_fim > data.data_inicio, {
  message: "Data de fim deve ser posterior à data de início",
  path: ["data_fim"],
});

interface AgendamentoFormProps {
  agendamento?: AgendamentoProduto;
  open: boolean;
  onClose: () => void;
  onSave: (data: any) => Promise<void>;
}

const AgendamentoForm: React.FC<AgendamentoFormProps> = ({
  agendamento,
  open,
  onClose,
  onSave,
}) => {
  const [loading, setLoading] = useState(false);
  const [produtos, setProdutos] = useState<Produto[]>([]);
  const [selectedProdutos, setSelectedProdutos] = useState<string[]>([]);

  const form = useForm<z.infer<typeof agendamentoSchema>>({
    resolver: zodResolver(agendamentoSchema),
    defaultValues: {
      nome: agendamento?.nome || '',
      tipo: agendamento?.tipo || 'promocao',
      regra: agendamento?.regra || '',
      data_inicio: agendamento?.periodo.inicio || new Date(),
      data_fim: agendamento?.periodo.fim || new Date(),
      produtos: agendamento?.produtos.map(p => p.id) || [],
      ativo: agendamento?.ativo ?? true,
      descricao: '',
    },
  });

  useEffect(() => {
    if (open) {
      loadProdutos();
      if (agendamento) {
        form.reset({
          nome: agendamento.nome,
          tipo: agendamento.tipo,
          regra: agendamento.regra,
          data_inicio: agendamento.periodo.inicio,
          data_fim: agendamento.periodo.fim,
          produtos: agendamento.produtos.map(p => p.id),
          ativo: agendamento.ativo,
          descricao: '',
        });
        setSelectedProdutos(agendamento.produtos.map(p => p.id));
      } else {
        form.reset({
          nome: '',
          tipo: 'promocao',
          regra: '',
          data_inicio: new Date(),
          data_fim: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000), // 30 dias
          produtos: [],
          ativo: true,
          descricao: '',
        });
        setSelectedProdutos([]);
      }
    }
  }, [open, agendamento, form]);

  const loadProdutos = async () => {
    try {
      // TODO: Implementar chamada para API
      // const response = await api.get('/produtos');
      // setProdutos(response.data);
      
      // Mock data para desenvolvimento
      setProdutos([
        {
          id: '1',
          nome: 'Cerveja Heineken 600ml',
          codigo: 'CERV001',
          categoria_id: '1',
          valor: 8.50,
          destaque: true,
          habilitado: true,
          promocional: false,
          created_at: new Date(),
          updated_at: new Date()
        },
        {
          id: '2',
          nome: 'Caipirinha de Cachaça',
          codigo: 'DRINK001',
          categoria_id: '2',
          valor: 12.00,
          destaque: false,
          habilitado: true,
          promocional: true,
          created_at: new Date(),
          updated_at: new Date()
        },
        {
          id: '3',
          nome: 'Açaí Especial',
          codigo: 'ACAI001',
          categoria_id: '3',
          valor: 15.00,
          destaque: true,
          habilitado: true,
          promocional: false,
          created_at: new Date(),
          updated_at: new Date()
        },
      ]);
    } catch (error) {
      console.error('Erro ao carregar produtos:', error);
    }
  };

  const handleSubmit = async (data: z.infer<typeof agendamentoSchema>) => {
    setLoading(true);
    try {
      const formData = {
        ...data,
        periodo: {
          inicio: data.data_inicio,
          fim: data.data_fim,
        },
        produtos: selectedProdutos,
      };
      
      await onSave(formData);
      onClose();
    } catch (error) {
      console.error('Erro ao salvar agendamento:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleProdutoToggle = (produtoId: string) => {
    setSelectedProdutos(prev => {
      const newSelection = prev.includes(produtoId)
        ? prev.filter(id => id !== produtoId)
        : [...prev, produtoId];
      
      form.setValue('produtos', newSelection);
      return newSelection;
    });
  };

  const tiposAgendamento = [
    {
      value: 'promocao',
      label: 'Promoção',
      description: 'Desconto ou preço especial por período',
      icon: Tag,
      color: 'text-green-600'
    },
    {
      value: 'evento',
      label: 'Evento Especial',
      description: 'Produtos exclusivos para eventos',
      icon: Users,
      color: 'text-blue-600'
    },
    {
      value: 'sazonal',
      label: 'Sazonal',
      description: 'Produtos de temporada específica',
      icon: Clock,
      color: 'text-orange-600'
    }
  ];

  const regrasExemplo = {
    promocao: [
      'Segunda a Quinta - 18:00 às 20:00',
      'Terça-feira - Dia todo',
      'Final de semana - 14:00 às 18:00'
    ],
    evento: [
      'Sexta - 23:00 às 03:00',
      'Sábado - 22:00 às 04:00',
      'Feriados - Dia todo'
    ],
    sazonal: [
      'Dezembro a Março - Dia todo',
      'Junho a Agosto - Dia todo',
      'Carnaval - Semana toda'
    ]
  };

  const selectedTipo = form.watch('tipo');

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Calendar className="h-5 w-5" />
            {agendamento ? 'Editar Agendamento' : 'Novo Agendamento'}
          </DialogTitle>
          <DialogDescription>
            Configure quando e quais produtos devem estar disponíveis automaticamente.
          </DialogDescription>
        </DialogHeader>

        <Form {...form}>
          <form onSubmit={form.handleSubmit(handleSubmit)} className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Coluna Esquerda - Informações Básicas */}
              <div className="space-y-4">
                <FormField
                  control={form.control}
                  name="nome"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Nome do Agendamento *</FormLabel>
                      <FormControl>
                        <Input placeholder="Ex: Happy Hour Cerveja" {...field} />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                <FormField
                  control={form.control}
                  name="tipo"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Tipo de Agendamento *</FormLabel>
                      <Select onValueChange={field.onChange} defaultValue={field.value}>
                        <FormControl>
                          <SelectTrigger>
                            <SelectValue placeholder="Selecione o tipo" />
                          </SelectTrigger>
                        </FormControl>
                        <SelectContent>
                          {tiposAgendamento.map((tipo) => (
                            <SelectItem key={tipo.value} value={tipo.value}>
                              <div className="flex items-center gap-2">
                                <tipo.icon className={`h-4 w-4 ${tipo.color}`} />
                                <div>
                                  <div className="font-medium">{tipo.label}</div>
                                  <div className="text-xs text-muted-foreground">
                                    {tipo.description}
                                  </div>
                                </div>
                              </div>
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                <FormField
                  control={form.control}
                  name="regra"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Regra de Aplicação *</FormLabel>
                      <FormControl>
                        <Input 
                          placeholder="Ex: Segunda a Quinta - 18:00 às 20:00" 
                          {...field} 
                        />
                      </FormControl>
                      <FormDescription>
                        <div className="mt-2">
                          <p className="text-xs font-medium">Exemplos para {selectedTipo}:</p>
                          <ul className="text-xs space-y-1 mt-1">
                            {regrasExemplo[selectedTipo]?.map((exemplo, index) => (
                              <li key={index} className="text-muted-foreground">
                                • {exemplo}
                              </li>
                            ))}
                          </ul>
                        </div>
                      </FormDescription>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                <div className="grid grid-cols-2 gap-4">
                  <FormField
                    control={form.control}
                    name="data_inicio"
                    render={({ field }) => (
                      <FormItem className="flex flex-col">
                        <FormLabel>Data de Início *</FormLabel>
                        <Popover>
                          <PopoverTrigger asChild>
                            <FormControl>
                              <Button
                                variant="outline"
                                className={cn(
                                  "pl-3 text-left font-normal",
                                  !field.value && "text-muted-foreground"
                                )}
                              >
                                {field.value ? (
                                  format(field.value, "dd/MM/yyyy", { locale: ptBR })
                                ) : (
                                  <span>Selecione</span>
                                )}
                                <CalendarIcon className="ml-auto h-4 w-4 opacity-50" />
                              </Button>
                            </FormControl>
                          </PopoverTrigger>
                          <PopoverContent className="w-auto p-0" align="start">
                            <Calendar
                              mode="single"
                              selected={field.value}
                              onSelect={field.onChange}
                              disabled={(date: Date) => date < new Date()}
                              initialFocus
                            />
                          </PopoverContent>
                        </Popover>
                        <FormMessage />
                      </FormItem>
                    )}
                  />

                  <FormField
                    control={form.control}
                    name="data_fim"
                    render={({ field }) => (
                      <FormItem className="flex flex-col">
                        <FormLabel>Data de Fim *</FormLabel>
                        <Popover>
                          <PopoverTrigger asChild>
                            <FormControl>
                              <Button
                                variant="outline"
                                className={cn(
                                  "pl-3 text-left font-normal",
                                  !field.value && "text-muted-foreground"
                                )}
                              >
                                {field.value ? (
                                  format(field.value, "dd/MM/yyyy", { locale: ptBR })
                                ) : (
                                  <span>Selecione</span>
                                )}
                                <CalendarIcon className="ml-auto h-4 w-4 opacity-50" />
                              </Button>
                            </FormControl>
                          </PopoverTrigger>
                          <PopoverContent className="w-auto p-0" align="start">
                            <Calendar
                              mode="single"
                              selected={field.value}
                              onSelect={field.onChange}
                              disabled={(date: Date) => date < new Date()}
                              initialFocus
                            />
                          </PopoverContent>
                        </Popover>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                </div>

                <FormField
                  control={form.control}
                  name="ativo"
                  render={({ field }) => (
                    <FormItem className="flex flex-row items-center space-x-3 space-y-0">
                      <FormControl>
                        <Checkbox
                          checked={field.value}
                          onCheckedChange={field.onChange}
                        />
                      </FormControl>
                      <div className="space-y-1 leading-none">
                        <FormLabel>Agendamento ativo</FormLabel>
                        <FormDescription>
                          O agendamento será aplicado automaticamente quando ativo
                        </FormDescription>
                      </div>
                    </FormItem>
                  )}
                />
              </div>

              {/* Coluna Direita - Seleção de Produtos */}
              <div className="space-y-4">
                <FormField
                  control={form.control}
                  name="produtos"
                  render={() => (
                    <FormItem>
                      <FormLabel className="flex items-center gap-2">
                        <Package className="h-4 w-4" />
                        Produtos Incluídos *
                      </FormLabel>
                      <FormDescription>
                        Selecione os produtos que serão afetados por este agendamento
                      </FormDescription>
                      <div className="border rounded-lg p-4 max-h-64 overflow-y-auto space-y-2">
                        {produtos.map((produto) => (
                          <div
                            key={produto.id}
                            className={cn(
                              "flex items-center space-x-3 p-3 rounded-lg border cursor-pointer transition-colors",
                              selectedProdutos.includes(produto.id)
                                ? "bg-primary/10 border-primary"
                                : "hover:bg-muted/50"
                            )}
                            onClick={() => handleProdutoToggle(produto.id)}
                          >
                            <Checkbox
                              checked={selectedProdutos.includes(produto.id)}
                              onChange={() => handleProdutoToggle(produto.id)}
                            />
                            <div className="flex-1 min-w-0">
                              <div className="font-medium text-sm">{produto.nome}</div>
                              <div className="text-xs text-muted-foreground">
                                {produto.codigo} • R$ {produto.valor.toFixed(2)}
                              </div>
                            </div>
                            {produto.destaque && (
                              <Badge variant="secondary" className="text-xs">
                                Destaque
                              </Badge>
                            )}
                          </div>
                        ))}
                      </div>
                      <div className="text-sm text-muted-foreground">
                        {selectedProdutos.length} produto(s) selecionado(s)
                      </div>
                      <FormMessage />
                    </FormItem>
                  )}
                />
              </div>
            </div>

            <DialogFooter>
              <Button type="button" variant="outline" onClick={onClose}>
                Cancelar
              </Button>
              <Button type="submit" disabled={loading}>
                {loading ? 'Salvando...' : agendamento ? 'Atualizar' : 'Criar'} Agendamento
              </Button>
            </DialogFooter>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  );
};

export default AgendamentoForm;
