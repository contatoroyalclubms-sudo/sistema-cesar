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
  
  preco: z.number()
    .min(0.01, 'Preço deve ser maior que zero'),
  
  descricao: z.string().max(1000).optional().or(z.literal('')),
  
  estoque_atual: z.number().min(0).optional(),
  estoque_minimo: z.number().min(0).optional(),
  estoque_maximo: z.number().min(0).optional(),
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
      // Corrigindo o mapeamento dos campos para compatibilidade
      let categoria = '';
      if (typeof produto.categoria === 'string') {
        categoria = produto.categoria;
      } else if (produto.categoria && typeof produto.categoria === 'object' && 'nome' in produto.categoria) {
        categoria = (produto.categoria as any).nome;
      }
        
      form.reset({
        nome: produto.nome,
        codigo_interno: produto.codigo_interno || produto.codigo || '',
        categoria: categoria,
        tipo: produto.tipo || 'BEBIDA',
        preco: produto.preco || produto.valor || 0,
        descricao: produto.descricao || '',
        estoque_atual: produto.estoque_atual || produto.estoque || 0,
        estoque_minimo: 0,
        estoque_maximo: 1000,
        controla_estoque: true,
        status: 'ATIVO',
        imagem_url: produto.imagem_url || produto.imagem || ''
      });
    } else {
      // Reset para valores padrão quando não há produto (novo cadastro)
      form.reset({
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
            {/* Nome */}
            <FormField
              control={form.control}
              name="nome"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Nome *</FormLabel>
                  <FormControl>
                    <Input placeholder="Nome do produto" {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            {/* Código Interno */}
            <FormField
              control={form.control}
              name="codigo_interno"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Código Interno</FormLabel>
                  <FormControl>
                    <Input placeholder="Ex: CERV001" {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            {/* Categoria */}
            <FormField
              control={form.control}
              name="categoria"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Categoria *</FormLabel>
                  <FormControl>
                    <Select onValueChange={field.onChange} value={field.value}>
                      <SelectTrigger>
                        <SelectValue placeholder="Selecione uma categoria" />
                      </SelectTrigger>
                      <SelectContent>
                        {categorias.map((categoria) => (
                          <SelectItem key={categoria} value={categoria}>
                            {categoria}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            {/* Tipo */}
            <FormField
              control={form.control}
              name="tipo"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Tipo *</FormLabel>
                  <FormControl>
                    <Select onValueChange={field.onChange} value={field.value}>
                      <SelectTrigger>
                        <SelectValue placeholder="Selecione o tipo" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="BEBIDA">Bebida</SelectItem>
                        <SelectItem value="COMIDA">Comida</SelectItem>
                        <SelectItem value="INGRESSO">Ingresso</SelectItem>
                        <SelectItem value="FICHA">Ficha</SelectItem>
                        <SelectItem value="COMBO">Combo</SelectItem>
                        <SelectItem value="VOUCHER">Voucher</SelectItem>
                      </SelectContent>
                    </Select>
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            {/* Preço */}
            <FormField
              control={form.control}
              name="preco"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Preço *</FormLabel>
                  <FormControl>
                    <Input
                      type="number"
                      step="0.01"
                      placeholder="0,00"
                      value={field.value || ''}
                      onChange={(e) => field.onChange(parseFloat(e.target.value) || 0)}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            {/* Descrição */}
            <FormField
              control={form.control}
              name="descricao"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Descrição</FormLabel>
                  <FormControl>
                    <Textarea
                      placeholder="Descrição do produto"
                      className="resize-none"
                      {...field}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            {/* Controla Estoque */}
            <FormField
              control={form.control}
              name="controla_estoque"
              render={({ field }) => (
                <FormItem className="flex flex-row items-start space-x-3 space-y-0">
                  <FormControl>
                    <Checkbox
                      checked={field.value}
                      onCheckedChange={field.onChange}
                    />
                  </FormControl>
                  <div className="space-y-1 leading-none">
                    <FormLabel>Controlar Estoque</FormLabel>
                    <FormDescription>
                      Marque para controlar o estoque deste produto
                    </FormDescription>
                  </div>
                </FormItem>
              )}
            />

            {/* Campos de estoque - só aparece se controla_estoque for true */}
            {form.watch('controla_estoque') && (
              <div className="grid grid-cols-3 gap-4">
                <FormField
                  control={form.control}
                  name="estoque_atual"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Estoque Atual</FormLabel>
                      <FormControl>
                        <Input 
                          type="number" 
                          value={field.value || ''} 
                          onChange={(e) => field.onChange(parseInt(e.target.value) || 0)}
                        />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                <FormField
                  control={form.control}
                  name="estoque_minimo"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Estoque Mínimo</FormLabel>
                      <FormControl>
                        <Input 
                          type="number" 
                          value={field.value || ''} 
                          onChange={(e) => field.onChange(parseInt(e.target.value) || 0)}
                        />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                <FormField
                  control={form.control}
                  name="estoque_maximo"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Estoque Máximo</FormLabel>
                      <FormControl>
                        <Input 
                          type="number" 
                          value={field.value || ''} 
                          onChange={(e) => field.onChange(parseInt(e.target.value) || 0)}
                        />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
              </div>
            )}

            {/* Status */}
            <FormField
              control={form.control}
              name="status"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Status</FormLabel>
                  <FormControl>
                    <Select onValueChange={field.onChange} value={field.value || 'ATIVO'}>
                      <SelectTrigger>
                        <SelectValue placeholder="Selecione o status" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="ATIVO">Ativo</SelectItem>
                        <SelectItem value="INATIVO">Inativo</SelectItem>
                        <SelectItem value="ESGOTADO">Esgotado</SelectItem>
                      </SelectContent>
                    </Select>
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            {/* Imagem */}
            <FormField
              control={form.control}
              name="imagem_url"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Imagem</FormLabel>
                  <FormControl>
                    <ImageUpload
                      value={imageFile}
                      onChange={(file) => {
                        setImageFile(file);
                        // Se um arquivo for selecionado, limpa a URL
                        if (file) {
                          field.onChange('');
                        }
                      }}
                      preview={field.value}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <DialogFooter>
              <Button variant="outline" onClick={handleClose} disabled={loading}>
                Cancelar
              </Button>
              <Button type="submit" disabled={loading}>
                {loading ? 'Salvando...' : produto ? 'Atualizar' : 'Criar'}
              </Button>
            </DialogFooter>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  );
};

export default ProductForm;
