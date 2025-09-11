import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Label } from '../ui/label';
import { Alert, AlertDescription } from '../ui/alert';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '../ui/dialog';
import { 
  ShoppingCart, 
  Plus, 
  Minus, 
  CreditCard, 
  DollarSign,
  Users,
  Ticket,
  TrendingUp,
  Calendar,
  Clock,
  CheckCircle,
  XCircle,
  QrCode,
  Search,
  UserCheck,
  Star,
  Gift,
  Percent
} from 'lucide-react';

interface EventoCaixaProps {
  eventoId: number;
  eventoNome: string;
  onClose?: () => void;
}

interface ItemVenda {
  id: string;
  tipo: 'entrada' | 'vip' | 'promoter' | 'consumo';
  nome: string;
  preco: number;
  quantidade: number;
  desconto?: number;
}

const EventoCaixa: React.FC<EventoCaixaProps> = ({ eventoId, eventoNome, onClose }) => {
  const [carrinho, setCarrinho] = useState<ItemVenda[]>([]);
  const [cpfCliente, setCpfCliente] = useState('');
  const [nomeCliente, setNomeCliente] = useState('');
  const [modalPagamento, setModalPagamento] = useState(false);
  const [formaPagamento, setFormaPagamento] = useState<'dinheiro' | 'cartao' | 'pix'>('cartao');
  const [processando, setProcessando] = useState(false);
  const [sucesso, setSucesso] = useState('');
  const [erro, setErro] = useState('');
  
  // Estatísticas do evento
  const [estatisticas, setEstatisticas] = useState({
    faturamento: 0,
    ticketMedio: 0,
    ticketMedioConsumo: 0,
    ticketMedioTotal: 0,
    entradasVendidas: 0,
    checkinsRealizados: 0
  });

  // Tipos de ingresso disponíveis
  const tiposIngresso = [
    { id: 'entrada', nome: 'Entrada Geral', preco: 50.00, icone: Ticket },
    { id: 'vip', nome: 'VIP Exclusivo', preco: 150.00, icone: Star },
    { id: 'promoter', nome: 'Lista Promoter', preco: 30.00, icone: Gift },
    { id: 'consumo', nome: 'Consumação', preco: 20.00, icone: DollarSign }
  ];

  useEffect(() => {
    carregarEstatisticas();
  }, [eventoId]);

  const carregarEstatisticas = async () => {
    try {
      const response = await fetch(`http://localhost:8003/api/eventos/${eventoId}/estatisticas`);
      if (response.ok) {
        const data = await response.json();
        setEstatisticas(data);
      }
    } catch (error) {
      console.error('Erro ao carregar estatísticas:', error);
    }
  };

  const adicionarAoCarrinho = (tipo: string) => {
    const tipoIngresso = tiposIngresso.find(t => t.id === tipo);
    if (!tipoIngresso) return;

    const itemExistente = carrinho.find(item => item.id === tipo);
    
    if (itemExistente) {
      setCarrinho(carrinho.map(item => 
        item.id === tipo 
          ? { ...item, quantidade: item.quantidade + 1 }
          : item
      ));
    } else {
      setCarrinho([...carrinho, {
        id: tipo,
        tipo: tipo as any,
        nome: tipoIngresso.nome,
        preco: tipoIngresso.preco,
        quantidade: 1
      }]);
    }
  };

  const removerDoCarrinho = (tipo: string) => {
    const item = carrinho.find(i => i.id === tipo);
    if (!item) return;

    if (item.quantidade > 1) {
      setCarrinho(carrinho.map(i => 
        i.id === tipo 
          ? { ...i, quantidade: i.quantidade - 1 }
          : i
      ));
    } else {
      setCarrinho(carrinho.filter(i => i.id !== tipo));
    }
  };

  const calcularTotal = () => {
    return carrinho.reduce((total, item) => {
      const desconto = item.desconto || 0;
      const precoComDesconto = item.preco * (1 - desconto / 100);
      return total + (precoComDesconto * item.quantidade);
    }, 0);
  };

  const finalizarVenda = async () => {
    if (carrinho.length === 0) {
      setErro('Adicione pelo menos um item ao carrinho');
      return;
    }

    if (!cpfCliente) {
      setErro('CPF do cliente é obrigatório');
      return;
    }

    setProcessando(true);
    setErro('');

    try {
      const response = await fetch(`http://localhost:8003/api/eventos/${eventoId}/vendas`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          cpf_cliente: cpfCliente,
          nome_cliente: nomeCliente,
          itens: carrinho,
          forma_pagamento: formaPagamento,
          total: calcularTotal()
        })
      });

      if (response.ok) {
        setSucesso('Venda realizada com sucesso!');
        setCarrinho([]);
        setCpfCliente('');
        setNomeCliente('');
        setModalPagamento(false);
        carregarEstatisticas();
        
        setTimeout(() => setSucesso(''), 3000);
      } else {
        throw new Error('Erro ao processar venda');
      }
    } catch (error) {
      setErro('Erro ao processar venda. Tente novamente.');
    } finally {
      setProcessando(false);
    }
  };

  const formatarMoeda = (valor: number) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL'
    }).format(valor);
  };

  const formatarCPF = (cpf: string) => {
    const numeros = cpf.replace(/\D/g, '');
    if (numeros.length <= 11) {
      return numeros.replace(/(\d{3})(\d{3})(\d{3})(\d{2})/, '$1.$2.$3-$4');
    }
    return numeros;
  };

  return (
    <div className="min-h-screen bg-background p-4">
      {/* Header com informações do evento */}
      <div className="mb-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold">PDV - {eventoNome}</h1>
            <p className="text-muted-foreground">Sistema de vendas integrado</p>
          </div>
          {onClose && (
            <Button variant="outline" onClick={onClose}>
              <XCircle className="h-4 w-4 mr-2" />
              Fechar Caixa
            </Button>
          )}
        </div>
      </div>

      {/* Estatísticas do Evento */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Faturamento</p>
                <p className="text-xl font-bold">{formatarMoeda(estatisticas.faturamento)}</p>
              </div>
              <TrendingUp className="h-8 w-8 text-primary/20" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Ticket Médio</p>
                <p className="text-xl font-bold">{formatarMoeda(estatisticas.ticketMedio)}</p>
              </div>
              <DollarSign className="h-8 w-8 text-primary/20" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Entradas Vendidas</p>
                <p className="text-xl font-bold">{estatisticas.entradasVendidas}</p>
              </div>
              <Ticket className="h-8 w-8 text-primary/20" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Check-ins</p>
                <p className="text-xl font-bold">{estatisticas.checkinsRealizados}</p>
              </div>
              <UserCheck className="h-8 w-8 text-primary/20" />
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Área de Produtos */}
        <div>
          <Card>
            <CardHeader>
              <CardTitle>Tipos de Ingresso</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 gap-4">
                {tiposIngresso.map(tipo => {
                  const Icon = tipo.icone;
                  const itemNoCarrinho = carrinho.find(i => i.id === tipo.id);
                  
                  return (
                    <div
                      key={tipo.id}
                      className="border rounded-lg p-4 hover:bg-accent/50 transition-colors cursor-pointer"
                      onClick={() => adicionarAoCarrinho(tipo.id)}
                    >
                      <div className="flex items-center justify-between mb-2">
                        <Icon className="h-6 w-6 text-primary" />
                        {itemNoCarrinho && (
                          <span className="bg-primary text-primary-foreground rounded-full px-2 py-1 text-xs">
                            {itemNoCarrinho.quantidade}
                          </span>
                        )}
                      </div>
                      <h3 className="font-semibold text-sm">{tipo.nome}</h3>
                      <p className="text-lg font-bold text-primary">
                        {formatarMoeda(tipo.preco)}
                      </p>
                    </div>
                  );
                })}
              </div>

              {/* Identificação do Cliente */}
              <div className="mt-6 space-y-4">
                <div>
                  <Label htmlFor="cpf">CPF do Cliente *</Label>
                  <Input
                    id="cpf"
                    placeholder="000.000.000-00"
                    value={cpfCliente}
                    onChange={(e) => setCpfCliente(formatarCPF(e.target.value))}
                    maxLength={14}
                  />
                </div>
                <div>
                  <Label htmlFor="nome">Nome do Cliente</Label>
                  <Input
                    id="nome"
                    placeholder="Nome completo"
                    value={nomeCliente}
                    onChange={(e) => setNomeCliente(e.target.value)}
                  />
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Carrinho */}
        <div>
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <ShoppingCart className="h-5 w-5" />
                Carrinho de Vendas
              </CardTitle>
            </CardHeader>
            <CardContent>
              {carrinho.length === 0 ? (
                <div className="text-center py-8 text-muted-foreground">
                  <ShoppingCart className="h-12 w-12 mx-auto mb-4 opacity-20" />
                  <p>Carrinho vazio</p>
                  <p className="text-sm">Selecione os ingressos ao lado</p>
                </div>
              ) : (
                <div className="space-y-4">
                  {carrinho.map(item => (
                    <div key={item.id} className="flex items-center justify-between border-b pb-2">
                      <div className="flex-1">
                        <p className="font-semibold">{item.nome}</p>
                        <p className="text-sm text-muted-foreground">
                          {formatarMoeda(item.preco)} x {item.quantidade}
                        </p>
                      </div>
                      <div className="flex items-center gap-2">
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={(e) => {
                            e.stopPropagation();
                            removerDoCarrinho(item.id);
                          }}
                        >
                          <Minus className="h-4 w-4" />
                        </Button>
                        <span className="w-8 text-center">{item.quantidade}</span>
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={(e) => {
                            e.stopPropagation();
                            adicionarAoCarrinho(item.id);
                          }}
                        >
                          <Plus className="h-4 w-4" />
                        </Button>
                      </div>
                    </div>
                  ))}

                  {/* Total */}
                  <div className="pt-4 border-t">
                    <div className="flex justify-between items-center text-xl font-bold">
                      <span>Total:</span>
                      <span className="text-primary">{formatarMoeda(calcularTotal())}</span>
                    </div>
                  </div>

                  {/* Botão Finalizar */}
                  <Button 
                    className="w-full" 
                    size="lg"
                    onClick={() => setModalPagamento(true)}
                    disabled={processando}
                  >
                    <CreditCard className="h-5 w-5 mr-2" />
                    Finalizar Venda
                  </Button>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Alertas */}
          {sucesso && (
            <Alert className="mt-4 border-green-200 bg-green-50">
              <CheckCircle className="h-4 w-4 text-green-600" />
              <AlertDescription className="text-green-800">{sucesso}</AlertDescription>
            </Alert>
          )}

          {erro && (
            <Alert className="mt-4 border-red-200 bg-red-50">
              <XCircle className="h-4 w-4 text-red-600" />
              <AlertDescription className="text-red-800">{erro}</AlertDescription>
            </Alert>
          )}
        </div>
      </div>

      {/* Modal de Pagamento */}
      <Dialog open={modalPagamento} onOpenChange={setModalPagamento}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Finalizar Pagamento</DialogTitle>
          </DialogHeader>
          
          <div className="space-y-4">
            <div>
              <p className="text-sm text-muted-foreground">Total a pagar:</p>
              <p className="text-2xl font-bold text-primary">{formatarMoeda(calcularTotal())}</p>
            </div>

            <div>
              <Label>Forma de Pagamento</Label>
              <div className="grid grid-cols-3 gap-2 mt-2">
                <Button
                  variant={formaPagamento === 'dinheiro' ? 'default' : 'outline'}
                  onClick={() => setFormaPagamento('dinheiro')}
                >
                  <DollarSign className="h-4 w-4 mr-2" />
                  Dinheiro
                </Button>
                <Button
                  variant={formaPagamento === 'cartao' ? 'default' : 'outline'}
                  onClick={() => setFormaPagamento('cartao')}
                >
                  <CreditCard className="h-4 w-4 mr-2" />
                  Cartão
                </Button>
                <Button
                  variant={formaPagamento === 'pix' ? 'default' : 'outline'}
                  onClick={() => setFormaPagamento('pix')}
                >
                  <QrCode className="h-4 w-4 mr-2" />
                  PIX
                </Button>
              </div>
            </div>

            <div className="flex gap-2">
              <Button
                variant="outline"
                className="flex-1"
                onClick={() => setModalPagamento(false)}
                disabled={processando}
              >
                Cancelar
              </Button>
              <Button
                className="flex-1"
                onClick={finalizarVenda}
                disabled={processando}
              >
                {processando ? 'Processando...' : 'Confirmar Pagamento'}
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default EventoCaixa;