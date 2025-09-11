import React, { useState, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Textarea } from '../ui/textarea';
import { Checkbox } from '../ui/checkbox';
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
import { Palette, Smile } from 'lucide-react';
import { Categoria } from '../../types/produto';

const categoriaSchema = z.object({
  nome: z.string()
    .min(2, 'Nome deve ter pelo menos 2 caracteres')
    .max(50, 'Nome não pode ter mais de 50 caracteres')
    .regex(/^[A-Z\s]+$/, 'Nome deve conter apenas letras maiúsculas'),
  
  mostrar_dashboard: z.boolean(),
  mostrar_pos: z.boolean(),
  
  maximo_composicao: z.coerce.number()
    .min(1, 'Mínimo 1')
    .max(100, 'Máximo 100')
    .optional(),
  
  minimo_composicao: z.coerce.number()
    .min(1, 'Mínimo 1')
    .max(100, 'Máximo 100')
    .optional(),
  
  cor: z.string().optional(),
  icone: z.string().optional(),
  ordem: z.coerce.number().min(1).max(999),
  
}).refine((data) => {
  if (data.maximo_composicao && data.minimo_composicao) {
    return data.maximo_composicao >= data.minimo_composicao;
  }
  return true;
}, {
  message: "Máximo deve ser maior ou igual ao mínimo",
  path: ["maximo_composicao"],
});

type CategoriaFormData = z.infer<typeof categoriaSchema>;

interface CategoriaFormProps {
  categoria?: Categoria;
  open: boolean;
  onClose: () => void;
  onSave: (categoria: CategoriaFormData) => Promise<void>;
}

const predefinedColors = [
  { name: 'Azul', value: '#3b82f6' },
  { name: 'Verde', value: '#22c55e' },
  { name: 'Vermelho', value: '#ef4444' },
  { name: 'Amarelo', value: '#fbbf24' },
  { name: 'Roxo', value: '#8b5cf6' },
  { name: 'Rosa', value: '#ec4899' },
  { name: 'Laranja', value: '#f59e0b' },
  { name: 'Cinza', value: '#6b7280' },
  { name: 'Indigo', value: '#6366f1' },
  { name: 'Teal', value: '#14b8a6' },
];

const predefinedIcons = [
  '🍺', '🍻', '🍷', '🥂', '🍸', '🍹', '🧊',
  '🍔', '🍟', '🍕', '🌭', '🥙', '🌮', '🥗',
  '🎫', '🎪', '🎭', '🎨', '🎵', '🎤', '🎧',
  '👑', '💎', '⭐', '🏆', '🥇', '🎯', '🔥',
  '📦', '🛍️', '🏪', '🏬', '🏢', '🏠', '🎪'
];

const CategoriaForm: React.FC<CategoriaFormProps> = ({
  categoria,
  open,
  onClose,
  onSave
}) => {
  const [loading, setLoading] = useState(false);
  const [selectedColor, setSelectedColor] = useState<string>('#3b82f6');
  const [selectedIcon, setSelectedIcon] = useState<string>('📦');

  const form = useForm<CategoriaFormData>({
    resolver: zodResolver(categoriaSchema),
    defaultValues: {
      nome: '',
      mostrar_dashboard: true,
      mostrar_pos: true,
      ordem: 1,
      cor: '#3b82f6',
      icone: '📦'
    }
  });

  useEffect(() => {
    if (categoria) {
      form.reset({
        nome: categoria.nome,
        mostrar_dashboard: categoria.mostrar_dashboard,
        mostrar_pos: categoria.mostrar_pos,
        maximo_composicao: categoria.maximo_composicao,
        minimo_composicao: categoria.minimo_composicao,
        cor: categoria.cor || '#3b82f6',
        icone: categoria.icone || '📦',
        ordem: categoria.ordem
      });
      setSelectedColor(categoria.cor || '#3b82f6');
      setSelectedIcon(categoria.icone || '📦');
    }
  }, [categoria, form]);

  const onSubmit = async (data: CategoriaFormData) => {
    setLoading(true);
    try {
      await onSave(data);
      onClose();
      form.reset();
    } catch (error) {
      console.error('Erro ao salvar categoria:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleClose = () => {
    onClose();
    form.reset();
    setSelectedColor('#3b82f6');
    setSelectedIcon('📦');
  };

  const handleColorSelect = (color: string) => {
    setSelectedColor(color);
    form.setValue('cor', color);
  };

  const handleIconSelect = (icon: string) => {
    setSelectedIcon(icon);
    form.setValue('icone', icon);
  };

  return (
    <Dialog open={open} onOpenChange={handleClose}>
      <DialogContent className="max-w-2xl">
        <DialogHeader>
          <DialogTitle>
            {categoria ? 'Editar Categoria' : 'Nova Categoria'}
          </DialogTitle>
          <DialogDescription>
            {categoria 
              ? 'Atualize as informações da categoria abaixo.' 
              : 'Preencha as informações para criar uma nova categoria.'
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
                      <FormLabel>Nome da Categoria *</FormLabel>
                      <FormControl>
                        <Input 
                          placeholder="Ex: CERVEJA" 
                          {...field}
                          onChange={(e) => field.onChange(e.target.value.toUpperCase())}
                        />
                      </FormControl>
                      <FormDescription>
                        Use apenas letras maiúsculas
                      </FormDescription>
                      <FormMessage />
                    </FormItem>
                  )}
                />
                
                <FormField
                  control={form.control}
                  name="ordem"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Ordem de Exibição *</FormLabel>
                      <FormControl>
                        <Input 
                          type="number" 
                          min="1"
                          max="999"
                          placeholder="1" 
                          {...field}
                        />
                      </FormControl>
                      <FormDescription>
                        Ordem em que aparece nos menus
                      </FormDescription>
                      <FormMessage />
                    </FormItem>
                  )}
                />
                
                <div className="grid grid-cols-2 gap-3">
                  <FormField
                    control={form.control}
                    name="minimo_composicao"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Mín. em Combos</FormLabel>
                        <FormControl>
                          <Input 
                            type="number" 
                            min="1"
                            max="100"
                            placeholder="1" 
                            {...field}
                          />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                  
                  <FormField
                    control={form.control}
                    name="maximo_composicao"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Máx. em Combos</FormLabel>
                        <FormControl>
                          <Input 
                            type="number" 
                            min="1"
                            max="100"
                            placeholder="10" 
                            {...field}
                          />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                </div>
                
                <div className="space-y-3">
                  <FormField
                    control={form.control}
                    name="mostrar_dashboard"
                    render={({ field }) => (
                      <FormItem className="flex flex-row items-start space-x-3 space-y-0">
                        <FormControl>
                          <Checkbox
                            checked={field.value}
                            onCheckedChange={field.onChange}
                          />
                        </FormControl>
                        <div className="space-y-1 leading-none">
                          <FormLabel>Mostrar no Dashboard</FormLabel>
                          <FormDescription>
                            Aparece nas estatísticas do dashboard
                          </FormDescription>
                        </div>
                      </FormItem>
                    )}
                  />
                  
                  <FormField
                    control={form.control}
                    name="mostrar_pos"
                    render={({ field }) => (
                      <FormItem className="flex flex-row items-start space-x-3 space-y-0">
                        <FormControl>
                          <Checkbox
                            checked={field.value}
                            onCheckedChange={field.onChange}
                          />
                        </FormControl>
                        <div className="space-y-1 leading-none">
                          <FormLabel>Mostrar no POS</FormLabel>
                          <FormDescription>
                            Disponível no ponto de venda
                          </FormDescription>
                        </div>
                      </FormItem>
                    )}
                  />
                </div>
              </div>

              {/* Coluna Direita */}
              <div className="space-y-4">
                {/* Preview da categoria */}
                <div className="p-4 border rounded-lg bg-muted/50">
                  <h4 className="text-sm font-medium mb-3">Preview</h4>
                  <div className="flex items-center space-x-3">
                    <div 
                      className="w-12 h-12 rounded-full flex items-center justify-center text-2xl"
                      style={{ backgroundColor: selectedColor }}
                    >
                      {selectedIcon}
                    </div>
                    <div>
                      <div className="font-medium">{form.watch('nome') || 'CATEGORIA'}</div>
                      <div className="text-sm text-muted-foreground">Ordem: {form.watch('ordem') || 1}</div>
                    </div>
                  </div>
                </div>

                {/* Seleção de Cor */}
                <div>
                  <FormLabel className="flex items-center gap-2 mb-3">
                    <Palette className="h-4 w-4" />
                    Cor da Categoria
                  </FormLabel>
                  <div className="grid grid-cols-5 gap-2">
                    {predefinedColors.map((color) => (
                      <button
                        key={color.value}
                        type="button"
                        className={`w-8 h-8 rounded-full border-2 transition-all ${
                          selectedColor === color.value 
                            ? 'border-foreground scale-110' 
                            : 'border-muted hover:border-muted-foreground'
                        }`}
                        style={{ backgroundColor: color.value }}
                        onClick={() => handleColorSelect(color.value)}
                        title={color.name}
                      />
                    ))}
                  </div>
                </div>

                {/* Seleção de Ícone */}
                <div>
                  <FormLabel className="flex items-center gap-2 mb-3">
                    <Smile className="h-4 w-4" />
                    Ícone da Categoria
                  </FormLabel>
                  <div className="grid grid-cols-7 gap-2 max-h-32 overflow-y-auto">
                    {predefinedIcons.map((icon) => (
                      <button
                        key={icon}
                        type="button"
                        className={`w-8 h-8 rounded border text-lg hover:bg-muted transition-colors ${
                          selectedIcon === icon 
                            ? 'bg-primary text-primary-foreground' 
                            : 'bg-background'
                        }`}
                        onClick={() => handleIconSelect(icon)}
                      >
                        {icon}
                      </button>
                    ))}
                  </div>
                </div>
              </div>
            </div>

            <DialogFooter>
              <Button variant="outline" onClick={handleClose} disabled={loading}>
                Cancelar
              </Button>
              <Button type="submit" disabled={loading}>
                {loading ? 'Salvando...' : (categoria ? 'Atualizar Categoria' : 'Criar Categoria')}
              </Button>
            </DialogFooter>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  );
};

export default CategoriaForm;