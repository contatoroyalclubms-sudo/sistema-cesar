import React, { useState, useEffect } from 'react';
import { 
  CreditCard, Plus, Minus, RefreshCw, Wallet, History, 
  QrCode, Smartphone, AlertTriangle, Check, X, Eye, Download
} from 'lucide-react';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '../ui/card';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Label } from '../ui/label';
import { Badge } from '../ui/badge';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '../ui/dialog';
import {
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
} from '../ui/tabs';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '../ui/select';
import { toast } from 'sonner';
import { api } from '@/lib/api';

interface CashlessCard {
  id: string;
  numero: string;
  cliente_cpf?: string;
  cliente_nome?: string;
  saldo: number;
  status: 'ativo' | 'bloqueado' | 'cancelado';
  created_at: string;
  last_transaction?: string;
}

interface Transaction {
  id: string;
  card_id: string;
  tipo: 'recarga' | 'compra' | 'estorno';
  valor: number;
  descricao: string;
  created_at: string;
  operador?: string;
}

// Mock data - será substituído pelas APIs reais do Cloud_01
const mockCards: CashlessCard[] = [
  {
    id: '1',
    numero: '1001',
    cliente_cpf: '12345678901',
    cliente_nome: 'João Silva',
    saldo: 150.75,
    status: 'ativo',
    created_at: '2024-09-01T10:00:00Z',
    last_transaction: '2024-09-10T15:30:00Z'
  },
  {
    id: '2', 
    numero: '1002',
    cliente_cpf: '98765432109',
    cliente_nome: 'Maria Santos',
    saldo: 89.50,
    status: 'ativo',
    created_at: '2024-09-02T14:20:00Z',
    last_transaction: '2024-09-10T12:15:00Z'
  }
];

const mockTransactions: Transaction[] = [
  {
    id: '1',
    card_id: '1',
    tipo: 'recarga',
    valor: 100.00,
    descricao: 'Recarga manual',
    created_at: '2024-09-10T15:30:00Z',
    operador: 'Admin'
  },
  {
    id: '2',
    card_id: '1', 
    tipo: 'compra',
    valor: -25.50,
    descricao: 'Compra Lanche Combo',
    created_at: '2024-09-10T14:45:00Z'
  }
];

const CashlessModule: React.FC = () => {
  const [cards, setCards] = useState<CashlessCard[]>(mockCards);
  const [transactions, setTransactions] = useState<Transaction[]>(mockTransactions);
  const [selectedCard, setSelectedCard] = useState<CashlessCard | null>(null);
  const [loading, setLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  
  // Estados para modais
  const [showNewCard, setShowNewCard] = useState(false);
  const [showRecharge, setShowRecharge] = useState(false);
  const [showTransactions, setShowTransactions] = useState(false);
  
  // Estados para formulários
  const [newCardData, setNewCardData] = useState({
    numero: '',
    cliente_cpf: '',
    cliente_nome: '',
    saldo_inicial: 0
  });
  const [rechargeAmount, setRechargeAmount] = useState('');

  // Carregar cartões (será implementado quando APIs estiverem funcionais)
  const loadCards = async () => {
    setLoading(true);
    try {
      // TODO: Substituir por chamada real à API do Cloud_01
      // const response = await api.get('/comandas-cashless/cards');
      // setCards(response.data);
      
      setTimeout(() => {
        setCards(mockCards);
        setLoading(false);
      }, 500);
    } catch (error) {
      console.error('Erro ao carregar cartões:', error);
      toast.error('Erro ao carregar cartões cashless');
      setLoading(false);
    }
  };

  // Criar novo cartão
  const createCard = async () => {
    setLoading(true);
    try {
      // TODO: Substituir por chamada real à API
      // const response = await api.post('/comandas-cashless/cards', newCardData);
      
      const newCard: CashlessCard = {
        id: Date.now().toString(),
        numero: newCardData.numero,
        cliente_cpf: newCardData.cliente_cpf,
        cliente_nome: newCardData.cliente_nome,
        saldo: newCardData.saldo_inicial,
        status: 'ativo',
        created_at: new Date().toISOString()
      };
      
      setCards([...cards, newCard]);
      setNewCardData({ numero: '', cliente_cpf: '', cliente_nome: '', saldo_inicial: 0 });
      setShowNewCard(false);
      toast.success('Cartão cashless criado com sucesso!');
      setLoading(false);
    } catch (error) {
      console.error('Erro ao criar cartão:', error);
      toast.error('Erro ao criar cartão cashless');
      setLoading(false);
    }
  };

  // Recarregar cartão
  const rechargeCard = async () => {
    if (!selectedCard || !rechargeAmount) return;
    
    setLoading(true);
    try {
      // TODO: Substituir por chamada real à API
      // await api.post(`/comandas-cashless/cards/${selectedCard.id}/recharge`, {
      //   valor: parseFloat(rechargeAmount)
      // });
      
      const updatedCards = cards.map(card =>
        card.id === selectedCard.id
          ? { ...card, saldo: card.saldo + parseFloat(rechargeAmount) }
          : card
      );
      
      setCards(updatedCards);
      setRechargeAmount('');
      setShowRecharge(false);
      toast.success(`Recarga de R$ ${rechargeAmount} realizada com sucesso!`);
      setLoading(false);
    } catch (error) {
      console.error('Erro ao recarregar cartão:', error);
      toast.error('Erro ao realizar recarga');
      setLoading(false);
    }
  };

  // Bloquear/desbloquear cartão
  const toggleCardStatus = async (card: CashlessCard) => {
    setLoading(true);
    try {
      const newStatus = card.status === 'ativo' ? 'bloqueado' : 'ativo';
      
      // TODO: Substituir por chamada real à API
      // await api.patch(`/comandas-cashless/cards/${card.id}/status`, { status: newStatus });
      
      const updatedCards = cards.map(c =>
        c.id === card.id ? { ...c, status: newStatus } : c
      );
      
      setCards(updatedCards);
      toast.success(`Cartão ${newStatus === 'ativo' ? 'desbloqueado' : 'bloqueado'} com sucesso!`);
      setLoading(false);
    } catch (error) {
      console.error('Erro ao alterar status do cartão:', error);
      toast.error('Erro ao alterar status do cartão');
      setLoading(false);
    }
  };

  useEffect(() => {
    loadCards();
  }, []);

  // Filtrar cartões por busca
  const filteredCards = cards.filter(card =>
    card.numero.toLowerCase().includes(searchTerm.toLowerCase()) ||
    card.cliente_nome?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    card.cliente_cpf?.includes(searchTerm)
  );

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'ativo': return 'bg-green-100 text-green-800';
      case 'bloqueado': return 'bg-yellow-100 text-yellow-800';  
      case 'cancelado': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'ativo': return <Check className="h-3 w-3" />;
      case 'bloqueado': return <AlertTriangle className="h-3 w-3" />;
      case 'cancelado': return <X className="h-3 w-3" />;
      default: return null;
    }
  };

  return (
    <div className="flex-1 space-y-4 p-4 pt-6">
      <div className="flex items-center justify-between">
        <h2 className="text-3xl font-bold tracking-tight">Sistema Cashless</h2>
        <div className="flex items-center space-x-2">
          <Button onClick={() => setShowNewCard(true)}>
            <Plus className="mr-2 h-4 w-4" />
            Novo Cartão
          </Button>
          <Button variant="outline" onClick={loadCards}>
            <RefreshCw className="mr-2 h-4 w-4" />
            Atualizar
          </Button>
        </div>
      </div>

      <Tabs defaultValue="cards" className="space-y-4">
        <TabsList>
          <TabsTrigger value="cards">Cartões</TabsTrigger>
          <TabsTrigger value="transactions">Transações</TabsTrigger>
          <TabsTrigger value="reports">Relatórios</TabsTrigger>
        </TabsList>

        <TabsContent value="cards" className="space-y-4">
          {/* Busca */}
          <div className="flex items-center space-x-2">
            <Input
              placeholder="Buscar por número, nome ou CPF..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="max-w-sm"
            />
          </div>

          {/* Grid de Cartões */}
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {filteredCards.map((card) => (
              <Card key={card.id} className="hover:shadow-lg transition-shadow">
                <CardHeader className="pb-3">
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-lg flex items-center">
                      <CreditCard className="mr-2 h-5 w-5" />
                      #{card.numero}
                    </CardTitle>
                    <Badge className={getStatusColor(card.status)}>
                      {getStatusIcon(card.status)}
                      <span className="ml-1 capitalize">{card.status}</span>
                    </Badge>
                  </div>
                  {card.cliente_nome && (
                    <CardDescription>{card.cliente_nome}</CardDescription>
                  )}
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="text-center">
                    <p className="text-2xl font-bold text-green-600">
                      R$ {card.saldo.toFixed(2)}
                    </p>
                    <p className="text-sm text-muted-foreground">Saldo atual</p>
                  </div>
                  
                  {card.cliente_cpf && (
                    <p className="text-sm text-muted-foreground">
                      CPF: {card.cliente_cpf}
                    </p>
                  )}
                  
                  <div className="flex space-x-2">
                    <Button 
                      size="sm" 
                      className="flex-1"
                      onClick={() => {
                        setSelectedCard(card);
                        setShowRecharge(true);
                      }}
                    >
                      <Plus className="mr-1 h-3 w-3" />
                      Recarregar
                    </Button>
                    <Button 
                      size="sm" 
                      variant="outline"
                      onClick={() => toggleCardStatus(card)}
                    >
                      {card.status === 'ativo' ? (
                        <AlertTriangle className="h-3 w-3" />
                      ) : (
                        <Check className="h-3 w-3" />
                      )}
                    </Button>
                    <Button 
                      size="sm" 
                      variant="outline"
                      onClick={() => {
                        setSelectedCard(card);
                        setShowTransactions(true);
                      }}
                    >
                      <History className="h-3 w-3" />
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="transactions" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Histórico de Transações</CardTitle>
              <CardDescription>
                Todas as transações cashless do sistema
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {mockTransactions.map((transaction) => (
                  <div key={transaction.id} className="flex items-center justify-between p-3 border rounded">
                    <div className="flex items-center space-x-3">
                      <div className={`p-2 rounded-full ${
                        transaction.tipo === 'recarga' ? 'bg-green-100' :
                        transaction.tipo === 'compra' ? 'bg-blue-100' : 'bg-yellow-100'
                      }`}>
                        {transaction.tipo === 'recarga' ? (
                          <Plus className="h-4 w-4 text-green-600" />
                        ) : transaction.tipo === 'compra' ? (
                          <Minus className="h-4 w-4 text-blue-600" />
                        ) : (
                          <RefreshCw className="h-4 w-4 text-yellow-600" />
                        )}
                      </div>
                      <div>
                        <p className="font-medium">{transaction.descricao}</p>
                        <p className="text-sm text-muted-foreground">
                          {new Date(transaction.created_at).toLocaleString('pt-BR')}
                          {transaction.operador && ` • ${transaction.operador}`}
                        </p>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className={`font-bold ${
                        transaction.valor > 0 ? 'text-green-600' : 'text-red-600'
                      }`}>
                        {transaction.valor > 0 ? '+' : ''}R$ {Math.abs(transaction.valor).toFixed(2)}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="reports" className="space-y-4">
          <div className="grid gap-4 md:grid-cols-3">
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-base">Total em Circulação</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-2xl font-bold text-blue-600">
                  R$ {cards.reduce((total, card) => total + card.saldo, 0).toFixed(2)}
                </p>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-base">Cartões Ativos</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-2xl font-bold text-green-600">
                  {cards.filter(card => card.status === 'ativo').length}
                </p>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-base">Transações Hoje</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-2xl font-bold text-purple-600">
                  {mockTransactions.length}
                </p>
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>

      {/* Modal Novo Cartão */}
      <Dialog open={showNewCard} onOpenChange={setShowNewCard}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Novo Cartão Cashless</DialogTitle>
            <DialogDescription>
              Crie um novo cartão cashless para um cliente
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <Label htmlFor="numero">Número do Cartão</Label>
              <Input
                id="numero"
                value={newCardData.numero}
                onChange={(e) => setNewCardData({...newCardData, numero: e.target.value})}
                placeholder="Ex: 1001"
              />
            </div>
            <div>
              <Label htmlFor="cliente_nome">Nome do Cliente</Label>
              <Input
                id="cliente_nome"
                value={newCardData.cliente_nome}
                onChange={(e) => setNewCardData({...newCardData, cliente_nome: e.target.value})}
                placeholder="Nome completo"
              />
            </div>
            <div>
              <Label htmlFor="cliente_cpf">CPF do Cliente</Label>
              <Input
                id="cliente_cpf"
                value={newCardData.cliente_cpf}
                onChange={(e) => setNewCardData({...newCardData, cliente_cpf: e.target.value})}
                placeholder="000.000.000-00"
              />
            </div>
            <div>
              <Label htmlFor="saldo_inicial">Saldo Inicial</Label>
              <Input
                id="saldo_inicial"
                type="number"
                value={newCardData.saldo_inicial}
                onChange={(e) => setNewCardData({...newCardData, saldo_inicial: parseFloat(e.target.value) || 0})}
                placeholder="0.00"
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowNewCard(false)}>
              Cancelar
            </Button>
            <Button onClick={createCard} disabled={loading}>
              {loading ? 'Criando...' : 'Criar Cartão'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Modal Recarga */}
      <Dialog open={showRecharge} onOpenChange={setShowRecharge}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Recarregar Cartão</DialogTitle>
            <DialogDescription>
              {selectedCard && `Cartão #${selectedCard.numero} - Saldo atual: R$ ${selectedCard.saldo.toFixed(2)}`}
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <Label htmlFor="recharge_amount">Valor da Recarga</Label>
              <Input
                id="recharge_amount"
                type="number"
                value={rechargeAmount}
                onChange={(e) => setRechargeAmount(e.target.value)}
                placeholder="0.00"
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowRecharge(false)}>
              Cancelar
            </Button>
            <Button onClick={rechargeCard} disabled={loading || !rechargeAmount}>
              {loading ? 'Processando...' : 'Recarregar'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default CashlessModule;