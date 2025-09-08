import { useState, useEffect } from 'react';
import { Plus, Search, Edit, Trash2, Copy, Eye, EyeOff, QrCode, BarChart, Settings, Grid, List, ChevronRight, ChevronLeft, GripVertical, Clock, Tag, DollarSign, Image, AlertCircle, Check, X, Filter, Download, Upload, Share2, Globe, Smartphone, Monitor } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Textarea } from '@/components/ui/textarea';
import { Switch } from '@/components/ui/switch';
import { toast } from '@/components/ui/use-toast';
import { Progress } from '@/components/ui/progress';
import { Separator } from '@/components/ui/separator';
import { DragDropContext, Droppable, Draggable } from '@hello-pangea/dnd';
import { motion, AnimatePresence } from 'framer-motion';

interface Cardapio {
  id: number;
  evento_id: number;
  nome: string;
  descricao: string;
  tipo: 'principal' | 'bebidas' | 'sobremesas' | 'especial' | 'kids' | 'vegetariano' | 'fitness' | 'promocoes' | 'delivery';
  ativo: boolean;
  ordem: number;
  url_slug: string;
  qr_code_url?: string;
  moeda: string;
  taxa_servico: number;
  configuracoes: {
    cores: {
      primaria: string;
      secundaria: string;
      fundo: string;
      texto: string;
    };
    fontes: {
      titulo: string;
      corpo: string;
    };
    layout: 'grid' | 'lista' | 'card';
    mostrar_imagens: boolean;
    mostrar_precos: boolean;
    mostrar_descricoes: boolean;
    mostrar_tempo_preparo: boolean;
    mostrar_calorias: boolean;
    mostrar_alergenos: boolean;
    permitir_pedidos: boolean;
    horario_funcionamento?: {
      [dia: string]: { abertura: string; fechamento: string; };
    };
  };
  categorias_count: number;
  itens_count: number;
  views_total: number;
  vendas_total: number;
  criado_em: string;
  atualizado_em: string;
}

interface Categoria {
  id: number;
  cardapio_id: number;
  nome: string;
  descricao?: string;
  imagem_url?: string;
  ordem: number;
  ativo: boolean;
  itens_count: number;
}

interface Item {
  id: number;
  categoria_id: number;
  nome: string;
  descricao: string;
  preco: number;
  preco_promocional?: number;
  imagem_url?: string;
  tags: string[];
  alergenos: string[];
  calorias?: number;
  tempo_preparo?: number;
  disponivel: boolean;
  estoque?: number;
  ordem: number;
  vendas_total: number;
  avaliacao_media?: number;
  modificadores?: Modificador[];
}

interface Modificador {
  id: number;
  nome: string;
  preco_adicional: number;
  obrigatorio: boolean;
  opcoes: string[];
}

interface Analytics {
  periodo: string;
  visualizacoes_totais: number;
  conversoes_totais: number;
  taxa_conversao: number;
  media_visualizacoes_dia: number;
  itens_mais_populares: Array<{ item_id: string; views: number; }>;
}

const tiposCardapio = [
  { value: 'principal', label: 'Principal', icon: '🍽️' },
  { value: 'bebidas', label: 'Bebidas', icon: '🥤' },
  { value: 'sobremesas', label: 'Sobremesas', icon: '🍰' },
  { value: 'especial', label: 'Especial', icon: '⭐' },
  { value: 'kids', label: 'Kids', icon: '🧸' },
  { value: 'vegetariano', label: 'Vegetariano', icon: '🥗' },
  { value: 'fitness', label: 'Fitness', icon: '💪' },
  { value: 'promocoes', label: 'Promoções', icon: '🎯' },
  { value: 'delivery', label: 'Delivery', icon: '🚚' }
];

export default function MultiCardapioModule() {
  const [cardapios, setCardapios] = useState<Cardapio[]>([]);
  const [selectedCardapio, setSelectedCardapio] = useState<Cardapio | null>(null);
  const [categorias, setCategorias] = useState<Categoria[]>([]);
  const [selectedCategoria, setSelectedCategoria] = useState<Categoria | null>(null);
  const [itens, setItens] = useState<Item[]>([]);
  const [analytics, setAnalytics] = useState<Analytics | null>(null);
  const [loading, setLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
  const [showCreateDialog, setShowCreateDialog] = useState(false);
  const [showItemDialog, setShowItemDialog] = useState(false);
  const [showQRDialog, setShowQRDialog] = useState(false);
  const [showAnalyticsDialog, setShowAnalyticsDialog] = useState(false);
  const [activeTab, setActiveTab] = useState('cardapios');

  // Mock data
  useEffect(() => {
    const mockCardapios: Cardapio[] = [
      {
        id: 1,
        evento_id: 1,
        nome: 'Cardápio Principal',
        descricao: 'Menu completo do evento',
        tipo: 'principal',
        ativo: true,
        ordem: 1,
        url_slug: 'principal-2024',
        moeda: 'BRL',
        taxa_servico: 10,
        configuracoes: {
          cores: { primaria: '#FF6B6B', secundaria: '#4ECDC4', fundo: '#FFFFFF', texto: '#2D3748' },
          fontes: { titulo: 'Poppins', corpo: 'Inter' },
          layout: 'grid',
          mostrar_imagens: true,
          mostrar_precos: true,
          mostrar_descricoes: true,
          mostrar_tempo_preparo: true,
          mostrar_calorias: false,
          mostrar_alergenos: true,
          permitir_pedidos: true
        },
        categorias_count: 12,
        itens_count: 156,
        views_total: 4532,
        vendas_total: 89650.00,
        criado_em: '2024-01-15',
        atualizado_em: '2024-01-20'
      },
      {
        id: 2,
        evento_id: 1,
        nome: 'Bebidas & Cocktails',
        descricao: 'Carta de bebidas especiais',
        tipo: 'bebidas',
        ativo: true,
        ordem: 2,
        url_slug: 'bebidas-2024',
        moeda: 'BRL',
        taxa_servico: 10,
        configuracoes: {
          cores: { primaria: '#9B59B6', secundaria: '#3498DB', fundo: '#1A1A1A', texto: '#FFFFFF' },
          fontes: { titulo: 'Montserrat', corpo: 'Roboto' },
          layout: 'lista',
          mostrar_imagens: true,
          mostrar_precos: true,
          mostrar_descricoes: true,
          mostrar_tempo_preparo: false,
          mostrar_calorias: false,
          mostrar_alergenos: false,
          permitir_pedidos: true
        },
        categorias_count: 6,
        itens_count: 72,
        views_total: 2341,
        vendas_total: 45320.00,
        criado_em: '2024-01-16',
        atualizado_em: '2024-01-20'
      },
      {
        id: 3,
        evento_id: 1,
        nome: 'Menu Kids',
        descricao: 'Especial para crianças',
        tipo: 'kids',
        ativo: true,
        ordem: 3,
        url_slug: 'kids-2024',
        moeda: 'BRL',
        taxa_servico: 0,
        configuracoes: {
          cores: { primaria: '#FFD93D', secundaria: '#6BCB77', fundo: '#FFF5E4', texto: '#4D4D4D' },
          fontes: { titulo: 'Comic Sans MS', corpo: 'Arial' },
          layout: 'card',
          mostrar_imagens: true,
          mostrar_precos: false,
          mostrar_descricoes: true,
          mostrar_tempo_preparo: false,
          mostrar_calorias: false,
          mostrar_alergenos: true,
          permitir_pedidos: false
        },
        categorias_count: 4,
        itens_count: 28,
        views_total: 892,
        vendas_total: 12450.00,
        criado_em: '2024-01-17',
        atualizado_em: '2024-01-19'
      }
    ];
    setCardapios(mockCardapios);

    const mockCategorias: Categoria[] = [
      { id: 1, cardapio_id: 1, nome: 'Entradas', descricao: 'Pratos de entrada', ordem: 1, ativo: true, itens_count: 18 },
      { id: 2, cardapio_id: 1, nome: 'Pratos Principais', descricao: 'Carnes e massas', ordem: 2, ativo: true, itens_count: 32 },
      { id: 3, cardapio_id: 1, nome: 'Sobremesas', descricao: 'Doces e sobremesas', ordem: 3, ativo: true, itens_count: 15 },
      { id: 4, cardapio_id: 1, nome: 'Bebidas', descricao: 'Bebidas diversas', ordem: 4, ativo: true, itens_count: 28 }
    ];
    setCategorias(mockCategorias);

    const mockItens: Item[] = [
      {
        id: 1,
        categoria_id: 1,
        nome: 'Bruschetta Italiana',
        descricao: 'Pão italiano grelhado com tomate fresco, manjericão e azeite',
        preco: 28.90,
        imagem_url: '/api/placeholder/300/200',
        tags: ['Vegetariano', 'Entrada'],
        alergenos: ['Glúten'],
        tempo_preparo: 15,
        disponivel: true,
        estoque: 50,
        ordem: 1,
        vendas_total: 234,
        avaliacao_media: 4.8
      },
      {
        id: 2,
        categoria_id: 1,
        nome: 'Carpaccio de Salmão',
        descricao: 'Finas fatias de salmão com alcaparras e molho de mostarda',
        preco: 45.90,
        preco_promocional: 39.90,
        imagem_url: '/api/placeholder/300/200',
        tags: ['Peixe', 'Premium'],
        alergenos: ['Peixe', 'Mostarda'],
        tempo_preparo: 10,
        disponivel: true,
        estoque: 30,
        ordem: 2,
        vendas_total: 189,
        avaliacao_media: 4.9
      }
    ];
    setItens(mockItens);

    const mockAnalytics: Analytics = {
      periodo: 'Últimos 30 dias',
      visualizacoes_totais: 8765,
      conversoes_totais: 1234,
      taxa_conversao: 14.08,
      media_visualizacoes_dia: 292.17,
      itens_mais_populares: [
        { item_id: '1', views: 456 },
        { item_id: '2', views: 389 }
      ]
    };
    setAnalytics(mockAnalytics);
  }, []);

  const handleDragEnd = (result: any) => {
    if (!result.destination) return;

    const items = Array.from(categorias);
    const [reorderedItem] = items.splice(result.source.index, 1);
    items.splice(result.destination.index, 0, reorderedItem);

    const updatedItems = items.map((item, index) => ({
      ...item,
      ordem: index + 1
    }));

    setCategorias(updatedItems);
    toast({
      title: 'Categorias reordenadas',
      description: 'A ordem das categorias foi atualizada com sucesso.',
    });
  };

  const handleDuplicateCardapio = (cardapio: Cardapio) => {
    const newCardapio: Cardapio = {
      ...cardapio,
      id: cardapios.length + 1,
      nome: `${cardapio.nome} (Cópia)`,
      url_slug: `${cardapio.url_slug}-copy`,
      views_total: 0,
      vendas_total: 0,
      criado_em: new Date().toISOString(),
      atualizado_em: new Date().toISOString()
    };
    setCardapios([...cardapios, newCardapio]);
    toast({
      title: 'Cardápio duplicado',
      description: 'O cardápio foi duplicado com sucesso.',
    });
  };

  const handleToggleCardapio = (cardapio: Cardapio) => {
    const updated = cardapios.map(c => 
      c.id === cardapio.id ? { ...c, ativo: !c.ativo } : c
    );
    setCardapios(updated);
    toast({
      title: cardapio.ativo ? 'Cardápio desativado' : 'Cardápio ativado',
      description: `O cardápio foi ${cardapio.ativo ? 'desativado' : 'ativado'} com sucesso.`,
    });
  };

  const renderCardapioCard = (cardapio: Cardapio) => (
    <motion.div
      key={cardapio.id}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      className="relative"
    >
      <Card className={`cursor-pointer transition-all hover:shadow-lg ${selectedCardapio?.id === cardapio.id ? 'ring-2 ring-primary' : ''} ${!cardapio.ativo ? 'opacity-60' : ''}`}>
        <CardHeader className="pb-3">
          <div className="flex items-start justify-between">
            <div className="flex items-center gap-2">
              <span className="text-2xl">
                {tiposCardapio.find(t => t.value === cardapio.tipo)?.icon}
              </span>
              <div>
                <CardTitle className="text-lg">{cardapio.nome}</CardTitle>
                <Badge variant={cardapio.ativo ? 'default' : 'secondary'} className="mt-1">
                  {cardapio.ativo ? 'Ativo' : 'Inativo'}
                </Badge>
              </div>
            </div>
            <div className="flex gap-1">
              <Button 
                size="icon" 
                variant="ghost"
                onClick={(e) => {
                  e.stopPropagation();
                  handleToggleCardapio(cardapio);
                }}
              >
                {cardapio.ativo ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
              </Button>
              <Button 
                size="icon" 
                variant="ghost"
                onClick={(e) => {
                  e.stopPropagation();
                  handleDuplicateCardapio(cardapio);
                }}
              >
                <Copy className="h-4 w-4" />
              </Button>
              <Button 
                size="icon" 
                variant="ghost"
                onClick={(e) => {
                  e.stopPropagation();
                  setSelectedCardapio(cardapio);
                  setShowQRDialog(true);
                }}
              >
                <QrCode className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground mb-3">{cardapio.descricao}</p>
          
          <div className="grid grid-cols-2 gap-2 text-sm">
            <div>
              <span className="text-muted-foreground">Categorias:</span>
              <span className="ml-1 font-medium">{cardapio.categorias_count}</span>
            </div>
            <div>
              <span className="text-muted-foreground">Itens:</span>
              <span className="ml-1 font-medium">{cardapio.itens_count}</span>
            </div>
            <div>
              <span className="text-muted-foreground">Views:</span>
              <span className="ml-1 font-medium">{cardapio.views_total.toLocaleString()}</span>
            </div>
            <div>
              <span className="text-muted-foreground">Vendas:</span>
              <span className="ml-1 font-medium">R$ {cardapio.vendas_total.toLocaleString()}</span>
            </div>
          </div>

          <Separator className="my-3" />

          <div className="flex items-center justify-between">
            <div className="flex gap-1">
              <Badge variant="outline" className="text-xs">
                {cardapio.configuracoes.layout}
              </Badge>
              {cardapio.configuracoes.permitir_pedidos && (
                <Badge variant="outline" className="text-xs text-green-600">
                  Pedidos ON
                </Badge>
              )}
            </div>
            <div className="flex gap-1">
              <Button 
                size="sm" 
                variant="outline"
                onClick={(e) => {
                  e.stopPropagation();
                  setSelectedCardapio(cardapio);
                  setShowAnalyticsDialog(true);
                }}
              >
                <BarChart className="h-3 w-3 mr-1" />
                Analytics
              </Button>
              <Button 
                size="sm"
                onClick={(e) => {
                  e.stopPropagation();
                  setSelectedCardapio(cardapio);
                  setActiveTab('categorias');
                }}
              >
                <Settings className="h-3 w-3 mr-1" />
                Gerenciar
              </Button>
            </div>
          </div>

          <div className="mt-3 p-2 bg-muted rounded-md">
            <div className="flex items-center gap-2 text-xs">
              <Globe className="h-3 w-3" />
              <a 
                href={`/cardapio/${cardapio.url_slug}`}
                target="_blank"
                rel="noopener noreferrer"
                className="text-primary hover:underline"
                onClick={(e) => e.stopPropagation()}
              >
                /cardapio/{cardapio.url_slug}
              </a>
            </div>
          </div>
        </CardContent>
      </Card>
    </motion.div>
  );

  const renderCategoriaItem = (categoria: Categoria, index: number) => (
    <Draggable key={categoria.id} draggableId={String(categoria.id)} index={index}>
      {(provided) => (
        <div
          ref={provided.innerRef}
          {...provided.draggableProps}
          className={`p-4 bg-card rounded-lg border transition-all hover:shadow-md ${selectedCategoria?.id === categoria.id ? 'ring-2 ring-primary' : ''}`}
        >
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div {...provided.dragHandleProps}>
                <GripVertical className="h-4 w-4 text-muted-foreground" />
              </div>
              <div>
                <h4 className="font-medium">{categoria.nome}</h4>
                <p className="text-sm text-muted-foreground">{categoria.descricao}</p>
                <div className="flex items-center gap-3 mt-1">
                  <Badge variant="secondary">{categoria.itens_count} itens</Badge>
                  <Badge variant={categoria.ativo ? 'default' : 'outline'}>
                    {categoria.ativo ? 'Ativa' : 'Inativa'}
                  </Badge>
                </div>
              </div>
            </div>
            <div className="flex gap-1">
              <Button 
                size="icon" 
                variant="ghost"
                onClick={() => setSelectedCategoria(categoria)}
              >
                <Edit className="h-4 w-4" />
              </Button>
              <Button 
                size="icon" 
                variant="ghost"
                onClick={() => {
                  setSelectedCategoria(categoria);
                  setActiveTab('itens');
                }}
              >
                <ChevronRight className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </div>
      )}
    </Draggable>
  );

  const renderItemCard = (item: Item) => (
    <Card key={item.id} className="overflow-hidden">
      {item.imagem_url && (
        <div className="aspect-video relative">
          <img 
            src={item.imagem_url} 
            alt={item.nome}
            className="object-cover w-full h-full"
          />
          {item.preco_promocional && (
            <Badge className="absolute top-2 right-2 bg-red-500">
              Promoção
            </Badge>
          )}
          {!item.disponivel && (
            <div className="absolute inset-0 bg-black/50 flex items-center justify-center">
              <Badge variant="destructive">Indisponível</Badge>
            </div>
          )}
        </div>
      )}
      <CardContent className="p-4">
        <h4 className="font-medium mb-1">{item.nome}</h4>
        <p className="text-sm text-muted-foreground mb-2 line-clamp-2">{item.descricao}</p>
        
        <div className="flex flex-wrap gap-1 mb-2">
          {item.tags.map(tag => (
            <Badge key={tag} variant="secondary" className="text-xs">
              {tag}
            </Badge>
          ))}
        </div>

        <div className="flex items-center justify-between mb-2">
          <div>
            {item.preco_promocional ? (
              <div className="flex items-center gap-2">
                <span className="text-lg font-bold text-green-600">
                  R$ {item.preco_promocional.toFixed(2)}
                </span>
                <span className="text-sm text-muted-foreground line-through">
                  R$ {item.preco.toFixed(2)}
                </span>
              </div>
            ) : (
              <span className="text-lg font-bold">
                R$ {item.preco.toFixed(2)}
              </span>
            )}
          </div>
          {item.estoque !== undefined && (
            <Badge variant={item.estoque > 10 ? 'default' : 'destructive'}>
              {item.estoque} em estoque
            </Badge>
          )}
        </div>

        {(item.tempo_preparo || item.alergenos.length > 0) && (
          <div className="flex items-center gap-3 text-xs text-muted-foreground">
            {item.tempo_preparo && (
              <div className="flex items-center gap-1">
                <Clock className="h-3 w-3" />
                {item.tempo_preparo} min
              </div>
            )}
            {item.alergenos.length > 0 && (
              <div className="flex items-center gap-1">
                <AlertCircle className="h-3 w-3" />
                {item.alergenos.join(', ')}
              </div>
            )}
          </div>
        )}

        {item.avaliacao_media && (
          <div className="flex items-center gap-1 mt-2">
            <span className="text-yellow-500">★</span>
            <span className="text-sm font-medium">{item.avaliacao_media}</span>
            <span className="text-xs text-muted-foreground">({item.vendas_total} vendas)</span>
          </div>
        )}

        <Separator className="my-3" />

        <div className="flex gap-1">
          <Button size="sm" variant="outline" className="flex-1">
            <Edit className="h-3 w-3 mr-1" />
            Editar
          </Button>
          <Button size="sm" variant="outline">
            <Copy className="h-3 w-3" />
          </Button>
          <Button 
            size="sm" 
            variant={item.disponivel ? 'outline' : 'default'}
            onClick={() => {
              const updated = itens.map(i => 
                i.id === item.id ? { ...i, disponivel: !i.disponivel } : i
              );
              setItens(updated);
            }}
          >
            {item.disponivel ? <EyeOff className="h-3 w-3" /> : <Eye className="h-3 w-3" />}
          </Button>
        </div>
      </CardContent>
    </Card>
  );

  return (
    <div className="container mx-auto p-6 max-w-7xl">
      <div className="mb-6">
        <h1 className="text-3xl font-bold mb-2">Sistema Multi-Cardápio</h1>
        <p className="text-muted-foreground">
          Gerencie até 9 cardápios simultâneos com QR Codes individuais e URLs personalizadas
        </p>
      </div>

      {cardapios.length >= 9 && (
        <div className="mb-4 p-4 bg-yellow-50 border border-yellow-200 rounded-lg flex items-center gap-2">
          <AlertCircle className="h-5 w-5 text-yellow-600" />
          <span className="text-sm">Você atingiu o limite máximo de 9 cardápios por evento.</span>
        </div>
      )}

      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-4">
        <TabsList className="grid grid-cols-3 w-full max-w-md">
          <TabsTrigger value="cardapios">
            Cardápios ({cardapios.length}/9)
          </TabsTrigger>
          <TabsTrigger value="categorias" disabled={!selectedCardapio}>
            Categorias
          </TabsTrigger>
          <TabsTrigger value="itens" disabled={!selectedCategoria}>
            Itens
          </TabsTrigger>
        </TabsList>

        <TabsContent value="cardapios" className="space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="Buscar cardápios..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10 w-64"
                />
              </div>
              <Select defaultValue="todos">
                <SelectTrigger className="w-40">
                  <SelectValue placeholder="Filtrar por tipo" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="todos">Todos</SelectItem>
                  {tiposCardapio.map(tipo => (
                    <SelectItem key={tipo.value} value={tipo.value}>
                      {tipo.icon} {tipo.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              <div className="flex items-center gap-1 border rounded-lg p-1">
                <Button
                  size="icon"
                  variant={viewMode === 'grid' ? 'default' : 'ghost'}
                  onClick={() => setViewMode('grid')}
                  className="h-7 w-7"
                >
                  <Grid className="h-4 w-4" />
                </Button>
                <Button
                  size="icon"
                  variant={viewMode === 'list' ? 'default' : 'ghost'}
                  onClick={() => setViewMode('list')}
                  className="h-7 w-7"
                >
                  <List className="h-4 w-4" />
                </Button>
              </div>
            </div>
            <div className="flex gap-2">
              <Button variant="outline">
                <Upload className="h-4 w-4 mr-2" />
                Importar
              </Button>
              <Button 
                onClick={() => setShowCreateDialog(true)}
                disabled={cardapios.length >= 9}
              >
                <Plus className="h-4 w-4 mr-2" />
                Novo Cardápio
              </Button>
            </div>
          </div>

          <AnimatePresence mode="wait">
            <div className={viewMode === 'grid' ? 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4' : 'space-y-4'}>
              {cardapios
                .filter(c => c.nome.toLowerCase().includes(searchTerm.toLowerCase()))
                .map(cardapio => renderCardapioCard(cardapio))}
            </div>
          </AnimatePresence>
        </TabsContent>

        <TabsContent value="categorias" className="space-y-4">
          {selectedCardapio && (
            <>
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-2">
                  <Button 
                    variant="ghost" 
                    size="sm"
                    onClick={() => setActiveTab('cardapios')}
                  >
                    <ChevronLeft className="h-4 w-4 mr-1" />
                    Voltar
                  </Button>
                  <Separator orientation="vertical" className="h-6" />
                  <h3 className="text-lg font-semibold">
                    {selectedCardapio.nome} - Categorias
                  </h3>
                </div>
                <Button>
                  <Plus className="h-4 w-4 mr-2" />
                  Nova Categoria
                </Button>
              </div>

              <DragDropContext onDragEnd={handleDragEnd}>
                <Droppable droppableId="categorias">
                  {(provided) => (
                    <div
                      {...provided.droppableProps}
                      ref={provided.innerRef}
                      className="space-y-2"
                    >
                      {categorias
                        .filter(c => c.cardapio_id === selectedCardapio.id)
                        .sort((a, b) => a.ordem - b.ordem)
                        .map((categoria, index) => renderCategoriaItem(categoria, index))}
                      {provided.placeholder}
                    </div>
                  )}
                </Droppable>
              </DragDropContext>
            </>
          )}
        </TabsContent>

        <TabsContent value="itens" className="space-y-4">
          {selectedCategoria && (
            <>
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-2">
                  <Button 
                    variant="ghost" 
                    size="sm"
                    onClick={() => setActiveTab('categorias')}
                  >
                    <ChevronLeft className="h-4 w-4 mr-1" />
                    Voltar
                  </Button>
                  <Separator orientation="vertical" className="h-6" />
                  <h3 className="text-lg font-semibold">
                    {selectedCategoria.nome} - Itens
                  </h3>
                </div>
                <div className="flex gap-2">
                  <Button variant="outline">
                    <Upload className="h-4 w-4 mr-2" />
                    Importar Itens
                  </Button>
                  <Button onClick={() => setShowItemDialog(true)}>
                    <Plus className="h-4 w-4 mr-2" />
                    Novo Item
                  </Button>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
                {itens
                  .filter(i => i.categoria_id === selectedCategoria.id)
                  .sort((a, b) => a.ordem - b.ordem)
                  .map(item => renderItemCard(item))}
              </div>
            </>
          )}
        </TabsContent>
      </Tabs>

      {/* Dialog QR Code */}
      <Dialog open={showQRDialog} onOpenChange={setShowQRDialog}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle>QR Code - {selectedCardapio?.nome}</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <div className="bg-white p-8 rounded-lg flex justify-center">
              <div className="w-48 h-48 bg-gray-200 flex items-center justify-center">
                <QrCode className="h-32 w-32 text-gray-600" />
              </div>
            </div>
            <div className="space-y-2">
              <Label>URL do Cardápio</Label>
              <div className="flex gap-2">
                <Input 
                  value={`https://seu-dominio.com/cardapio/${selectedCardapio?.url_slug}`}
                  readOnly
                />
                <Button variant="outline">
                  <Copy className="h-4 w-4" />
                </Button>
              </div>
            </div>
            <div className="grid grid-cols-3 gap-2">
              <Button variant="outline" className="w-full">
                <Download className="h-4 w-4 mr-2" />
                PNG
              </Button>
              <Button variant="outline" className="w-full">
                <Download className="h-4 w-4 mr-2" />
                SVG
              </Button>
              <Button variant="outline" className="w-full">
                <Share2 className="h-4 w-4 mr-2" />
                Compartilhar
              </Button>
            </div>
            <div className="p-4 bg-muted rounded-lg">
              <h4 className="font-medium mb-2">Dispositivos Compatíveis</h4>
              <div className="grid grid-cols-3 gap-2 text-center">
                <div className="p-2">
                  <Smartphone className="h-8 w-8 mx-auto mb-1 text-green-600" />
                  <span className="text-xs">Mobile</span>
                </div>
                <div className="p-2">
                  <Monitor className="h-8 w-8 mx-auto mb-1 text-green-600" />
                  <span className="text-xs">Desktop</span>
                </div>
                <div className="p-2">
                  <Globe className="h-8 w-8 mx-auto mb-1 text-green-600" />
                  <span className="text-xs">Web</span>
                </div>
              </div>
            </div>
          </div>
        </DialogContent>
      </Dialog>

      {/* Dialog Analytics */}
      <Dialog open={showAnalyticsDialog} onOpenChange={setShowAnalyticsDialog}>
        <DialogContent className="max-w-3xl">
          <DialogHeader>
            <DialogTitle>Analytics - {selectedCardapio?.nome}</DialogTitle>
          </DialogHeader>
          {analytics && (
            <div className="space-y-4">
              <div className="grid grid-cols-4 gap-4">
                <Card>
                  <CardContent className="p-4">
                    <div className="text-2xl font-bold">{analytics.visualizacoes_totais.toLocaleString()}</div>
                    <p className="text-xs text-muted-foreground">Visualizações</p>
                  </CardContent>
                </Card>
                <Card>
                  <CardContent className="p-4">
                    <div className="text-2xl font-bold">{analytics.conversoes_totais.toLocaleString()}</div>
                    <p className="text-xs text-muted-foreground">Conversões</p>
                  </CardContent>
                </Card>
                <Card>
                  <CardContent className="p-4">
                    <div className="text-2xl font-bold">{analytics.taxa_conversao}%</div>
                    <p className="text-xs text-muted-foreground">Taxa de Conversão</p>
                  </CardContent>
                </Card>
                <Card>
                  <CardContent className="p-4">
                    <div className="text-2xl font-bold">{Math.round(analytics.media_visualizacoes_dia)}</div>
                    <p className="text-xs text-muted-foreground">Views/Dia</p>
                  </CardContent>
                </Card>
              </div>
              
              <Card>
                <CardHeader>
                  <CardTitle className="text-base">Itens Mais Populares</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    {analytics.itens_mais_populares.slice(0, 5).map((item, index) => (
                      <div key={item.item_id} className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <span className="text-sm font-medium">#{index + 1}</span>
                          <span className="text-sm">Item {item.item_id}</span>
                        </div>
                        <Badge variant="secondary">{item.views} views</Badge>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
}