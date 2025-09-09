import React, { useState, useEffect, useRef, useCallback } from 'react';
import { Card, CardContent, CardHeader } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Alert, AlertDescription } from '@/components/ui/alert';
import {
  Clock,
  CheckCircle,
  AlertTriangle,
  ChefHat,
  Eye,
  Play,
  Check,
  X,
  Bell,
  Timer,
  Package,
  Users,
  Coffee,
  Utensils,
  Wine,
  IceCream
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { useToast } from '@/components/ui/use-toast';

interface ItemPedido {
  id: number;
  produto_nome: string;
  quantidade: number;
  modificacoes?: string[];
  observacoes?: string;
  status: 'pendente' | 'preparando' | 'pronto' | 'entregue' | 'cancelado';
  setor?: string;
  tempo_estimado: number;
  tempo_decorrido: number;
}

interface Pedido {
  id: number;
  numero_pedido: string;
  tipo: 'balcao' | 'mesa' | 'delivery' | 'retirada';
  cliente_nome: string;
  mesa_numero?: string;
  status: 'recebido' | 'visualizado' | 'preparando' | 'pronto' | 'entregue' | 'cancelado';
  prioridade: 'baixa' | 'normal' | 'alta' | 'urgente';
  observacoes?: string;
  tempo_estimado: number;
  tempo_decorrido: number;
  alerta_atraso: boolean;
  data_pedido: string;
  itens: ItemPedido[];
}

interface KitchenDisplayProps {
  setorId: number;
  setorNome?: string;
  terminalId: string;
}

export default function KitchenDisplay({ setorId, setorNome = "Cozinha", terminalId }: KitchenDisplayProps) {
  const [pedidos, setPedidos] = useState<Pedido[]>([]);
  const [selectedPedido, setSelectedPedido] = useState<Pedido | null>(null);
  const [connected, setConnected] = useState(false);
  const [soundEnabled, setSoundEnabled] = useState(true);
  const ws = useRef<WebSocket | null>(null);
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const { toast } = useToast();

  // Conectar WebSocket
  useEffect(() => {
    const connectWebSocket = () => {
      const wsUrl = `ws://localhost:8000/api/kds/ws/${setorId}/${terminalId}`;
      ws.current = new WebSocket(wsUrl);

      ws.current.onopen = () => {
        setConnected(true);
        console.log('KDS conectado ao servidor');
        
        // Enviar heartbeat inicial
        ws.current?.send(JSON.stringify({ type: 'heartbeat' }));
      };

      ws.current.onmessage = (event) => {
        const data = JSON.parse(event.data);
        handleWebSocketMessage(data);
      };

      ws.current.onerror = (error) => {
        console.error('Erro WebSocket:', error);
        setConnected(false);
      };

      ws.current.onclose = () => {
        setConnected(false);
        console.log('Conexão WebSocket fechada, reconectando...');
        
        // Reconectar após 3 segundos
        setTimeout(connectWebSocket, 3000);
      };
    };

    connectWebSocket();

    // Heartbeat a cada 30 segundos
    const heartbeatInterval = setInterval(() => {
      if (ws.current?.readyState === WebSocket.OPEN) {
        ws.current.send(JSON.stringify({ type: 'heartbeat' }));
      }
    }, 30000);

    // Atualizar tempos a cada minuto
    const updateInterval = setInterval(() => {
      setPedidos(prev => prev.map(pedido => ({
        ...pedido,
        tempo_decorrido: Math.floor((Date.now() - new Date(pedido.data_pedido).getTime()) / 60000)
      })));
    }, 60000);

    return () => {
      clearInterval(heartbeatInterval);
      clearInterval(updateInterval);
      ws.current?.close();
    };
  }, [setorId, terminalId]);

  const handleWebSocketMessage = (data: any) => {
    switch (data.type) {
      case 'novo_pedido':
        setPedidos(prev => [...prev, data.pedido]);
        playSound('new_order.mp3');
        toast({
          title: "Novo Pedido!",
          description: `Pedido #${data.pedido.numero_pedido} recebido`,
        });
        break;
      
      case 'pedido_atualizado':
        setPedidos(prev => prev.map(p => 
          p.id === data.pedido_id 
            ? { ...p, status: data.status, ...data.detalhes }
            : p
        ));
        break;
      
      case 'item_pronto':
        setPedidos(prev => prev.map(p => {
          if (p.id === data.pedido_id) {
            const updatedItens = p.itens.map(item =>
              item.id === data.item_id
                ? { ...item, status: 'pronto' as const }
                : item
            );
            
            // Verificar se todos os itens estão prontos
            const todosProntos = updatedItens.every(item => 
              item.status === 'pronto' || item.status === 'cancelado'
            );
            
            return {
              ...p,
              itens: updatedItens,
              status: todosProntos ? 'pronto' as const : p.status
            };
          }
          return p;
        }));
        playSound('item_ready.mp3');
        break;
      
      case 'alerta_atraso':
        setPedidos(prev => prev.map(p =>
          p.id === data.pedido_id
            ? { ...p, alerta_atraso: true }
            : p
        ));
        playSound('alert.mp3');
        toast({
          title: "Pedido Atrasado!",
          description: `Pedido #${data.pedido_id} está atrasado`,
          variant: "destructive"
        });
        break;
    }
  };

  const playSound = (soundFile: string) => {
    if (soundEnabled && audioRef.current) {
      audioRef.current.src = `/sounds/${soundFile}`;
      audioRef.current.play().catch(e => console.error('Erro ao tocar som:', e));
    }
  };

  const sendCommand = (command: any) => {
    if (ws.current?.readyState === WebSocket.OPEN) {
      ws.current.send(JSON.stringify(command));
    }
  };

  const marcarVisualizado = (pedidoId: number) => {
    sendCommand({
      type: 'marcar_visualizado',
      pedido_id: pedidoId
    });
    
    setPedidos(prev => prev.map(p =>
      p.id === pedidoId
        ? { ...p, status: 'visualizado' as const }
        : p
    ));
  };

  const iniciarPreparo = (pedidoId: number, itemId?: number) => {
    sendCommand({
      type: 'iniciar_preparo',
      pedido_id: pedidoId,
      item_id: itemId
    });
    
    if (itemId) {
      setPedidos(prev => prev.map(p => {
        if (p.id === pedidoId) {
          return {
            ...p,
            status: p.status === 'recebido' || p.status === 'visualizado' 
              ? 'preparando' as const 
              : p.status,
            itens: p.itens.map(item =>
              item.id === itemId
                ? { ...item, status: 'preparando' as const }
                : item
            )
          };
        }
        return p;
      }));
    } else {
      setPedidos(prev => prev.map(p =>
        p.id === pedidoId
          ? { 
              ...p, 
              status: 'preparando' as const,
              itens: p.itens.map(item => ({ ...item, status: 'preparando' as const }))
            }
          : p
      ));
    }
  };

  const marcarItemPronto = (pedidoId: number, itemId: number) => {
    sendCommand({
      type: 'marcar_pronto',
      pedido_id: pedidoId,
      item_id: itemId
    });
  };

  const marcarEntregue = (pedidoId: number) => {
    sendCommand({
      type: 'marcar_entregue',
      pedido_id: pedidoId
    });
    
    setPedidos(prev => prev.filter(p => p.id !== pedidoId));
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'recebido': return 'bg-blue-500';
      case 'visualizado': return 'bg-purple-500';
      case 'preparando': return 'bg-yellow-500';
      case 'pronto': return 'bg-green-500';
      case 'cancelado': return 'bg-red-500';
      default: return 'bg-gray-500';
    }
  };

  const getPrioridadeColor = (prioridade: string) => {
    switch (prioridade) {
      case 'urgente': return 'text-red-600 animate-pulse';
      case 'alta': return 'text-orange-600';
      case 'normal': return 'text-blue-600';
      case 'baixa': return 'text-gray-600';
      default: return 'text-gray-600';
    }
  };

  const getTempoColor = (tempoDecorrido: number, tempoEstimado: number) => {
    const percentual = (tempoDecorrido / tempoEstimado) * 100;
    if (percentual < 70) return 'text-green-600';
    if (percentual < 100) return 'text-yellow-600';
    return 'text-red-600 font-bold';
  };

  const getTipoIcon = (tipo: string) => {
    switch (tipo) {
      case 'mesa': return <Users className="h-4 w-4" />;
      case 'delivery': return <Package className="h-4 w-4" />;
      case 'balcao': return <Coffee className="h-4 w-4" />;
      default: return <Utensils className="h-4 w-4" />;
    }
  };

  const getSetorIcon = (setor?: string) => {
    switch (setor?.toLowerCase()) {
      case 'cozinha': return <ChefHat className="h-4 w-4" />;
      case 'bar': return <Wine className="h-4 w-4" />;
      case 'sobremesas': return <IceCream className="h-4 w-4" />;
      default: return <Utensils className="h-4 w-4" />;
    }
  };

  return (
    <div className="h-screen bg-gray-100 p-4">
      {/* Header */}
      <div className="mb-4 flex justify-between items-center bg-white rounded-lg shadow p-4">
        <div className="flex items-center gap-4">
          <h1 className="text-2xl font-bold flex items-center gap-2">
            {getSetorIcon(setorNome)}
            {setorNome}
          </h1>
          <Badge variant={connected ? "success" : "destructive"}>
            {connected ? "Online" : "Offline"}
          </Badge>
          <Badge variant="outline">
            {pedidos.length} pedidos
          </Badge>
        </div>
        
        <div className="flex gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => setSoundEnabled(!soundEnabled)}
          >
            <Bell className={cn("h-4 w-4", !soundEnabled && "line-through")} />
          </Button>
        </div>
      </div>

      {/* Grid de Pedidos */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4 h-[calc(100vh-120px)] overflow-auto">
        {pedidos.map((pedido) => (
          <Card
            key={pedido.id}
            className={cn(
              "cursor-pointer transition-all hover:shadow-lg",
              pedido.alerta_atraso && "ring-2 ring-red-500 animate-pulse",
              pedido.prioridade === 'urgente' && "ring-2 ring-orange-500",
              selectedPedido?.id === pedido.id && "ring-2 ring-blue-500"
            )}
            onClick={() => setSelectedPedido(pedido)}
          >
            <CardHeader className="pb-3">
              <div className="flex justify-between items-start">
                <div className="flex items-center gap-2">
                  <Badge className={getStatusColor(pedido.status)}>
                    {pedido.status}
                  </Badge>
                  {getTipoIcon(pedido.tipo)}
                </div>
                <div className={cn("text-2xl font-bold", getPrioridadeColor(pedido.prioridade))}>
                  #{pedido.numero_pedido.split('-')[1]}
                </div>
              </div>
              
              <div className="mt-2 flex justify-between items-center">
                <div>
                  <p className="font-semibold">{pedido.cliente_nome}</p>
                  {pedido.mesa_numero && (
                    <p className="text-sm text-muted-foreground">Mesa {pedido.mesa_numero}</p>
                  )}
                </div>
                <div className={cn("text-sm", getTempoColor(pedido.tempo_decorrido, pedido.tempo_estimado))}>
                  <Timer className="h-4 w-4 inline mr-1" />
                  {pedido.tempo_decorrido}min
                </div>
              </div>
            </CardHeader>

            <CardContent>
              <ScrollArea className="h-40">
                {pedido.itens.map((item) => (
                  <div
                    key={item.id}
                    className={cn(
                      "mb-2 p-2 rounded",
                      item.status === 'pronto' && "bg-green-50 line-through",
                      item.status === 'preparando' && "bg-yellow-50",
                      item.status === 'cancelado' && "bg-red-50 line-through"
                    )}
                  >
                    <div className="flex justify-between items-start">
                      <div className="flex-1">
                        <p className="font-medium">
                          {item.quantidade}x {item.produto_nome}
                        </p>
                        {item.modificacoes && item.modificacoes.length > 0 && (
                          <p className="text-xs text-red-600 mt-1">
                            {item.modificacoes.join(', ')}
                          </p>
                        )}
                        {item.observacoes && (
                          <p className="text-xs text-muted-foreground mt-1">
                            {item.observacoes}
                          </p>
                        )}
                      </div>
                      <div className="flex gap-1">
                        {item.status === 'pendente' && (
                          <Button
                            size="sm"
                            variant="ghost"
                            onClick={(e) => {
                              e.stopPropagation();
                              iniciarPreparo(pedido.id, item.id);
                            }}
                          >
                            <Play className="h-3 w-3" />
                          </Button>
                        )}
                        {item.status === 'preparando' && (
                          <Button
                            size="sm"
                            variant="ghost"
                            onClick={(e) => {
                              e.stopPropagation();
                              marcarItemPronto(pedido.id, item.id);
                            }}
                          >
                            <Check className="h-3 w-3" />
                          </Button>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </ScrollArea>

              {pedido.observacoes && (
                <Alert className="mt-2">
                  <AlertTriangle className="h-4 w-4" />
                  <AlertDescription className="text-xs">
                    {pedido.observacoes}
                  </AlertDescription>
                </Alert>
              )}

              <div className="mt-3 flex gap-2">
                {pedido.status === 'recebido' && (
                  <Button
                    size="sm"
                    variant="outline"
                    className="flex-1"
                    onClick={(e) => {
                      e.stopPropagation();
                      marcarVisualizado(pedido.id);
                    }}
                  >
                    <Eye className="h-4 w-4 mr-1" />
                    Visualizar
                  </Button>
                )}
                
                {(pedido.status === 'visualizado' || pedido.status === 'recebido') && (
                  <Button
                    size="sm"
                    className="flex-1"
                    onClick={(e) => {
                      e.stopPropagation();
                      iniciarPreparo(pedido.id);
                    }}
                  >
                    <Play className="h-4 w-4 mr-1" />
                    Iniciar
                  </Button>
                )}
                
                {pedido.status === 'pronto' && (
                  <Button
                    size="sm"
                    variant="success"
                    className="flex-1"
                    onClick={(e) => {
                      e.stopPropagation();
                      marcarEntregue(pedido.id);
                    }}
                  >
                    <CheckCircle className="h-4 w-4 mr-1" />
                    Entregar
                  </Button>
                )}
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Audio element for sounds */}
      <audio ref={audioRef} />
    </div>
  );
}