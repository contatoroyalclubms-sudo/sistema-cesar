import React, { useState, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Textarea } from '../ui/textarea';
import { Checkbox } from '../ui/checkbox';
import { toast } from '../../hooks/use-toast';
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
import { Upload, X } from 'lucide-react';
import { Produto } from '../../types/produto';
import ImageUpload from './ImageUpload';

const produtoSchema = z.object({
  nome: z.string()
    .min(3, 'Nome deve ter pelo menos 3 caracteres')
    .max(255, 'Nome não pode ter mais de 255 caracteres'),
  
  codigo_interno: z.string()
    .max(20, 'Código interno não pode ter mais de 20 caracteres')
    .optional()
    .or(z.literal('')),
  
  categoria: z.string()
    .min(1, 'Categoria é obrigatória'),
  
  tipo: z.enum(['BEBIDA', 'COMIDA', 'INGRESSO', 'FICHA', 'COMBO', 'VOUCHER'])
    .refine((val) => val, { message: 'Tipo é obrigatório' }),
  
  preco: z.coerce.number()
    .min(0.01, 'Preço deve ser maior que zero'),
  
  descricao: z.string().max(1000).optional().or(z.literal('')),
  
  estoque_atual: z.coerce.number().min(0).optional(),
  estoque_minimo: z.coerce.number().min(0).optional(),
  estoque_maximo: z.coerce.number().min(0).optional(),
  controla_estoque: z.boolean().optional(),
  status: z.enum(['ATIVO', 'INATIVO', 'ESGOTADO']).optional(),
  imagem_url: z.string().max(500).optional().or(z.literal('')),
});

type ProdutoFormData = z.infer<typeof produtoSchema>;

interface ProductFormProps {
  produto?: Produto;
  open: boolean;
  onClose: () => void;
  onSave: (produto: ProdutoFormData, imageFile?: File) => Promise<void>;
}

const ProductForm: React.FC<ProductFormProps> = ({
  produto,
  open,
  onClose,
  onSave
}) => {
  const [loading, setLoading] = useState(false);
  const [imageFile, setImageFile] = useState<File | null>(null);
  const [showAdvanced, setShowAdvanced] = useState(false);
  
  // Categorias fixas - não precisamos mais carregar da API
  const categorias = [
    'Bebidas',
    'Comidas', 
    'Petiscos',
    'Sobremesas',
    'Drinks',
    'Cervejas',
    'Vinhos',
    'Destilados'
  ];

  const form = useForm<ProdutoFormData>({
    resolver: zodResolver(produtoSchema),
    defaultValues: {
      nome: '',
      codigo_interno: '',
      categoria: '',
      tipo: 'BEBIDA',
      preco: 0,
      descricao: '',
      estoque_atual: 0,
      estoque_minimo: 0,
      estoque_maximo: 1000,
      controla_estoque: true,
      status: 'ATIVO',
      imagem_url: ''
    }
  });

  useEffect(() => {
    if (produto) {
      form.reset({
        nome: produto.nome,
        codigo_interno: produto.codigo || '',
        categoria: produto.categoria?.nome || '',
        tipo: produto.tipo || 'BEBIDA',
        preco: produto.valor,
        descricao: produto.descricao || '',
        estoque_atual: produto.estoque,
        imagem_url: produto.imagem_url || ''
      });
    }
  }, [produto, form]);

  const onSubmit = async (data: ProdutoFormData) => {
    setLoading(true);
    try {
      await onSave(data, imageFile || undefined);
      onClose();
      form.reset();
      setImageFile(null);
    } catch (error) {
      console.error('Erro ao salvar produto:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleClose = () => {
    onClose();
    form.reset();
    setImageFile(null);
    setShowAdvanced(false);
  };

  return (
    <Dialog open={open} onOpenChange={handleClose}>
      <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>
            {produto ? 'Editar Produto' : 'Novo Produto'}
          </DialogTitle>
          <DialogDescription>
            {produto 
              ? 'Atualize as informações do produto abaixo.' 
              : 'Preencha as informações para criar um novo produto.'
            }
          </DialogDescription>
        </DialogHeader>

        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
            <div className="grid grid-cols-2 gap-6">
              {/* Coluna Esquerda */}
              <div className="space-y-4">
                <FormField
                  control={form.control}
                  name="nome"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Nome do Produto *</FormLabel>
                      <FormControl>
                        <Input placeholder="Ex: Cerveja Heineken 600ml" {...field} />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
                
                <FormField
                  control={form.control}
                  name="codigo"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Código/SKU</FormLabel>
                      <FormControl>
                        <Input placeholder="Ex: CERV001" {...field} />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
                
                <FormField
                  control={form.control}
                  name="categoria_id"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Categoria *</FormLabel>
                      <Select onValueChange={field.onChange} value={field.value}>
                        <FormControl>
                          <SelectTrigger>
                            <SelectValue placeholder="Selecione uma categoria" />
                          </SelectTrigger>
                        </FormControl>
                        <SelectContent>
                          {categorias.map((categoria) => (
                            <SelectItem key={categoria.id} value={categoria.id}>
                              {categoria.nome}
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
                  name="tipo"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Tipo *</FormLabel>
                      <Select onValueChange={field.onChange} value={field.value}>
                        <FormControl>
                          <SelectTrigger>
                            <SelectValue placeholder="Selecione o tipo" />
                          </SelectTrigger>
                        </FormControl>
                        <SelectContent>
                          <SelectItem value="BEBIDA">Bebida</SelectItem>
                          <SelectItem value="COMIDA">Comida</SelectItem>
                          <SelectItem value="INGRESSO">Ingresso</SelectItem>
                          <SelectItem value="FICHA">Ficha</SelectItem>
                          <SelectItem value="COMBO">Combo</SelectItem>
                          <SelectItem value="VOUCHER">Voucher</SelectItem>
                        </SelectContent>
                      </Select>
                      <FormMessage />
                    </FormItem>
                  )}
                />
                
                <FormField
                  control={form.control}
                  name="valor"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Valor de Venda *</FormLabel>
                      <FormControl>
                        <Input 
                          type="number" 
                          step="0.01" 
                          placeholder="0,00" 
                          {...field}
                        />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
                
                <div className="grid grid-cols-3 gap-3">
                  <FormField
                    control={form.control}
                    name="ncm"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>NCM</FormLabel>
                        <FormControl>
                          <Input placeholder="00000000" maxLength={8} {...field} />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                  
                  <FormField
                    control={form.control}
                    name="cfop"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>CFOP</FormLabel>
                        <FormControl>
                          <Input placeholder="0000" maxLength={4} {...field} />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                  
                  <FormField
                    control={form.control}
                    name="cest"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>CEST</FormLabel>
                        <FormControl>
                          <Input placeholder="0000000" maxLength={7} {...field} />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                </div>
              </div>

              {/* Coluna Direita */}
              <div className="space-y-4">
                <ImageUpload
                  value={imageFile}
                  onChange={setImageFile}
                  preview={produto?.imagem}
                />
                
                <FormField
                  control={form.control}
                  name="descricao"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Descrição</FormLabel>
                      <FormControl>
                        <Textarea 
                          placeholder="Descrição detalhada do produto..."
                          rows={4}
                          {...field}
                        />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
                
                <div className="space-y-3">
                  <FormField
                    control={form.control}
                    name="destaque"
                    render={({ field }) => (
                      <FormItem className="flex flex-row items-start space-x-3 space-y-0">
                        <FormControl>
                          <Checkbox
                            checked={field.value}
                            onCheckedChange={field.onChange}
                          />
                        </FormControl>
                        <div className="space-y-1 leading-none">
                          <FormLabel>Produto em destaque</FormLabel>
                          <FormDescription>
                            Aparecerá destacado no PDV
                          </FormDescription>
                        </div>
                      </FormItem>
                    )}
                  />
                  
                  <FormField
                    control={form.control}
                    name="habilitado"
                    render={({ field }) => (
                      <FormItem className="flex flex-row items-start space-x-3 space-y-0">
                        <FormControl>
                          <Checkbox
                            checked={field.value}
                            onCheckedChange={field.onChange}
                          />
                        </FormControl>
                        <div className="space-y-1 leading-none">
                          <FormLabel>Produto habilitado</FormLabel>
                          <FormDescription>
                            Produto estará disponível para venda
                          </FormDescription>
                        </div>
                      </FormItem>
                    )}
                  />
                  
                  <FormField
                    control={form.control}
                    name="promocional"
                    render={({ field }) => (
                      <FormItem className="flex flex-row items-start space-x-3 space-y-0">
                        <FormControl>
                          <Checkbox
                            checked={field.value}
                            onCheckedChange={field.onChange}
                          />
                        </FormControl>
                        <div className="space-y-1 leading-none">
                          <FormLabel>Produto promocional</FormLabel>
                          <FormDescription>
                            Produto em promoção especial
                          </FormDescription>
                        </div>
                      </FormItem>
                    )}
                  />
                </div>
              </div>
            </div>

            {/* Campos Avançados */}
            <div className="border-t pt-6">
              <Button
                type="button"
                variant="ghost"
                onClick={() => setShowAdvanced(!showAdvanced)}
                className="mb-4"
              >
                {showAdvanced ? 'Ocultar' : 'Mostrar'} campos avançados
              </Button>
              
              {showAdvanced && (
                <div className="grid grid-cols-2 gap-6">
                  <div className="space-y-4">
                    <FormField
                      control={form.control}
                      name="marca"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Marca</FormLabel>
                          <FormControl>
                            <Input placeholder="Ex: Heineken" {...field} />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                    
                    <FormField
                      control={form.control}
                      name="fornecedor"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Fornecedor</FormLabel>
                          <FormControl>
                            <Input placeholder="Nome do fornecedor" {...field} />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                    
                    <div className="grid grid-cols-2 gap-3">
                      <FormField
                        control={form.control}
                        name="preco_custo"
                        render={({ field }) => (
                          <FormItem>
                            <FormLabel>Preço de Custo</FormLabel>
                            <FormControl>
                              <Input type="number" step="0.01" {...field} />
                            </FormControl>
                            <FormMessage />
                          </FormItem>
                        )}
                      />
                      
                      <FormField
                        control={form.control}
                        name="margem_lucro"
                        render={({ field }) => (
                          <FormItem>
                            <FormLabel>Margem (%)</FormLabel>
                            <FormControl>
                              <Input type="number" step="0.1" {...field} />
                            </FormControl>
                            <FormMessage />
                          </FormItem>
                        )}
                      />
                    </div>
                  </div>
                  
                  <div className="space-y-4">
                    <div className="grid grid-cols-2 gap-3">
                      <FormField
                        control={form.control}
                        name="unidade_medida"
                        render={({ field }) => (
                          <FormItem>
                            <FormLabel>Unidade</FormLabel>
                            <Select onValueChange={field.onChange} value={field.value}>
                              <FormControl>
                                <SelectTrigger>
                                  <SelectValue />
                                </SelectTrigger>
                              </FormControl>
                              <SelectContent>
                                <SelectItem value="UN">Unidade</SelectItem>
                                <SelectItem value="LT">Litro</SelectItem>
                                <SelectItem value="ML">Mililitro</SelectItem>
                                <SelectItem value="KG">Quilograma</SelectItem>
                                <SelectItem value="G">Grama</SelectItem>
                              </SelectContent>
                            </Select>
                            <FormMessage />
                          </FormItem>
                        )}
                      />
                      
                      <FormField
                        control={form.control}
                        name="volume"
                        render={({ field }) => (
                          <FormItem>
                            <FormLabel>Volume (ml)</FormLabel>
                            <FormControl>
                              <Input type="number" {...field} />
                            </FormControl>
                            <FormMessage />
                          </FormItem>
                        )}
                      />
                    </div>
                    
                    <div className="grid grid-cols-2 gap-3">
                      <FormField
                        control={form.control}
                        name="teor_alcoolico"
                        render={({ field }) => (
                          <FormItem>
                            <FormLabel>Teor Alcoólico (%)</FormLabel>
                            <FormControl>
                              <Input type="number" step="0.1" {...field} />
                            </FormControl>
                            <FormMessage />
                          </FormItem>
                        )}
                      />
                      
                      <FormField
                        control={form.control}
                        name="validade_dias"
                        render={({ field }) => (
                          <FormItem>
                            <FormLabel>Validade (dias)</FormLabel>
                            <FormControl>
                              <Input type="number" {...field} />
                            </FormControl>
                            <FormMessage />
                          </FormItem>
                        )}
                      />
                    </div>
                    
                    <FormField
                      control={form.control}
                      name="observacoes"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Observações</FormLabel>
                          <FormControl>
                            <Textarea 
                              placeholder="Observações adicionais..."
                              rows={3}
                              {...field}
                            />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                  </div>
                </div>
              )}
            </div>

            <DialogFooter>
              <Button variant="outline" onClick={handleClose} disabled={loading}>
                Cancelar
              </Button>
              <Button type="submit" disabled={loading}>
                {loading ? 'Salvando...' : (produto ? 'Atualizar Produto' : 'Criar Produto')}
              </Button>
            </DialogFooter>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  );
};

export default ProductForm;