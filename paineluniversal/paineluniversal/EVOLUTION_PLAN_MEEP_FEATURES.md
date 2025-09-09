# 🚀 PLANO DE EVOLUÇÃO: Sistema Universal → MEEP Premium

## 📋 Executive Summary
Transformar o Sistema Universal existente em uma plataforma competitiva com o MEEP, aproveitando 80% do código já desenvolvido e adicionando features premium de alto valor.

**Tempo Total Estimado**: 8-10 semanas
**ROI Esperado**: 300% em 6 meses
**Economia vs Recriar**: R$ 800k e 10 meses

---

## 🎯 FASE 1: CORREÇÕES CRÍTICAS (3-5 dias)
*Objetivo: Estabilizar o sistema atual para servir de base sólida*

### 1.1 Frontend - Resolver Dependências
```bash
# Comandos para executar
cd frontend
npm install clsx tailwind-merge
```

**Criar arquivos faltantes:**

```typescript
// frontend/src/lib/utils.ts
import { clsx, type ClassValue } from 'clsx'
import { twMerge } from 'tailwind-merge'

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}
```

```typescript
// frontend/src/lib/api.ts
import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export const api = axios.create({
  baseURL: `${API_URL}/api`,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Interceptor para adicionar token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})
```

### 1.2 Backend - Configurações de Produção
```python
# backend/app/main.py - Habilitar auto-migrations
if os.getenv("RAILWAY_ENVIRONMENT"):
    from app.migrations.auto_migrate import run_migrations
    run_migrations()  # Descomentar linha 49

# Configurar CORS adequadamente
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 1.3 Banco de Dados - Migrations Pendentes
```bash
cd backend
python apply_postgresql_migration.py
python migrate_production_railway.py
```

---

## 💰 FASE 2: SISTEMA DE SPLIT DE PAGAMENTOS (1 semana)
*Feature de alto valor do MEEP - Divisão automática de receitas*

### 2.1 Modelos de Dados
```python
# backend/app/models/split.py
from sqlalchemy import Column, String, Float, JSON, ForeignKey, Enum
from app.database import Base

class SplitRule(Base):
    __tablename__ = "split_rules"
    
    id = Column(String, primary_key=True)
    evento_id = Column(String, ForeignKey("eventos.id"))
    
    # Beneficiário
    beneficiario_tipo = Column(Enum("empresa", "fornecedor", "parceiro", "promoter"))
    beneficiario_id = Column(String)
    beneficiario_dados = Column(JSON)  # conta bancária, pix, etc
    
    # Regra de cálculo
    tipo_calculo = Column(Enum("percentual", "valor_fixo"))
    valor = Column(Float)
    
    # Condições
    condicoes = Column(JSON)  # produto_id, categoria, min_valor, etc
    prioridade = Column(Integer, default=0)
    ativo = Column(Boolean, default=True)

class SplitExecution(Base):
    __tablename__ = "split_executions"
    
    id = Column(String, primary_key=True)
    venda_id = Column(String, ForeignKey("vendas.id"))
    rule_id = Column(String, ForeignKey("split_rules.id"))
    
    valor_original = Column(Float)
    valor_split = Column(Float)
    status = Column(Enum("pendente", "processando", "pago", "erro"))
    gateway_response = Column(JSON)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    paid_at = Column(DateTime, nullable=True)
```

### 2.2 Service de Split
```python
# backend/app/services/split_service.py
from typing import List, Dict
from decimal import Decimal

class SplitService:
    def __init__(self):
        self.gateways = {
            'stripe': StripeGateway(),
            'pagseguro': PagSeguroGateway(),
            'mercadopago': MercadoPagoGateway()
        }
    
    async def calculate_splits(self, venda: Venda) -> List[Dict]:
        """Calcula divisão baseada nas regras configuradas"""
        rules = await self.get_active_rules(venda.evento_id)
        splits = []
        
        valor_restante = Decimal(str(venda.total))
        
        for rule in sorted(rules, key=lambda x: x.prioridade):
            if self.check_conditions(rule, venda):
                split_value = self.calculate_value(rule, venda, valor_restante)
                
                splits.append({
                    'rule_id': rule.id,
                    'beneficiario': rule.beneficiario_id,
                    'valor': float(split_value),
                    'tipo': rule.beneficiario_tipo
                })
                
                valor_restante -= split_value
        
        # Valor restante vai para o organizador
        if valor_restante > 0:
            splits.append({
                'rule_id': 'default',
                'beneficiario': venda.evento.empresa_id,
                'valor': float(valor_restante),
                'tipo': 'empresa'
            })
        
        return splits
    
    async def execute_splits(self, venda_id: str, splits: List[Dict]):
        """Executa transferências via gateway de pagamento"""
        for split in splits:
            execution = SplitExecution(
                venda_id=venda_id,
                rule_id=split['rule_id'],
                valor_original=split['valor'],
                valor_split=split['valor'],
                status='processando'
            )
            
            try:
                gateway = self.gateways[venda.gateway]
                response = await gateway.transfer(
                    amount=split['valor'],
                    destination=split['beneficiario'],
                    metadata={'venda_id': venda_id}
                )
                
                execution.status = 'pago'
                execution.gateway_response = response
                execution.paid_at = datetime.utcnow()
                
            except Exception as e:
                execution.status = 'erro'
                execution.gateway_response = {'error': str(e)}
            
            await execution.save()
```

### 2.3 API Endpoints
```python
# backend/app/routers/split.py
@router.post("/split/rules")
async def create_split_rule(rule: SplitRuleSchema):
    """Criar regra de split para evento"""
    return await SplitService().create_rule(rule)

@router.get("/split/simulate/{venda_id}")
async def simulate_split(venda_id: str):
    """Simular divisão antes de confirmar venda"""
    return await SplitService().simulate(venda_id)

@router.post("/split/execute/{venda_id}")
async def execute_split(venda_id: str):
    """Executar split após confirmação de pagamento"""
    return await SplitService().execute(venda_id)
```

---

## 🍳 FASE 3: KDS - KITCHEN DISPLAY SYSTEM (1 semana)
*Sistema de gestão de pedidos em tempo real*

### 3.1 Backend WebSocket para KDS
```python
# backend/app/routers/kds.py
from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, List
import asyncio

class KDSManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}
        self.pedidos_queue: Dict[str, List[Pedido]] = {}
    
    async def connect(self, websocket: WebSocket, setor: str):
        await websocket.accept()
        if setor not in self.active_connections:
            self.active_connections[setor] = []
        self.active_connections[setor].append(websocket)
    
    async def broadcast_to_setor(self, setor: str, data: dict):
        if setor in self.active_connections:
            for connection in self.active_connections[setor]:
                try:
                    await connection.send_json(data)
                except:
                    self.active_connections[setor].remove(connection)

@router.websocket("/ws/kds/{setor}")
async def kds_websocket(websocket: WebSocket, setor: str):
    manager = KDSManager()
    await manager.connect(websocket, setor)
    
    try:
        while True:
            data = await websocket.receive_json()
            
            if data['action'] == 'update_status':
                pedido = await update_pedido_status(
                    pedido_id=data['pedido_id'],
                    item_id=data['item_id'],
                    status=data['status']
                )
                
                # Broadcast para todos os displays do setor
                await manager.broadcast_to_setor(setor, {
                    'type': 'pedido_updated',
                    'pedido': pedido.dict()
                })
                
            elif data['action'] == 'get_queue':
                queue = await get_setor_queue(setor)
                await websocket.send_json({
                    'type': 'queue',
                    'pedidos': queue
                })
                
    except WebSocketDisconnect:
        manager.disconnect(websocket, setor)
```

### 3.2 Frontend KDS Display
```tsx
// frontend/src/components/kds/KitchenDisplay.tsx
import React, { useState, useEffect } from 'react';
import { Card, Grid, Typography, Button, Chip } from '@mui/material';
import { Timer, CheckCircle, Warning } from '@mui/icons-material';

interface Pedido {
  id: string;
  numero: string;
  mesa?: string;
  itens: ItemPedido[];
  tempo_decorrido: number;
  prioridade: 'normal' | 'alta' | 'urgente';
  status: string;
}

const KitchenDisplay: React.FC<{ setor: string }> = ({ setor }) => {
  const [pedidos, setPedidos] = useState<Pedido[]>([]);
  const [ws, setWs] = useState<WebSocket | null>(null);

  useEffect(() => {
    const websocket = new WebSocket(`ws://localhost:8000/api/kds/ws/${setor}`);
    
    websocket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      
      if (data.type === 'queue') {
        setPedidos(data.pedidos);
      } else if (data.type === 'pedido_updated') {
        setPedidos(prev => 
          prev.map(p => p.id === data.pedido.id ? data.pedido : p)
        );
      } else if (data.type === 'new_pedido') {
        setPedidos(prev => [...prev, data.pedido]);
        // Som de notificação
        playNotificationSound();
      }
    };

    websocket.onopen = () => {
      websocket.send(JSON.stringify({ action: 'get_queue' }));
    };

    setWs(websocket);
    return () => websocket.close();
  }, [setor]);

  const updateItemStatus = (pedidoId: string, itemId: string, status: string) => {
    ws?.send(JSON.stringify({
      action: 'update_status',
      pedido_id: pedidoId,
      item_id: itemId,
      status
    }));
  };

  const getTempoColor = (minutos: number) => {
    if (minutos < 10) return 'success';
    if (minutos < 20) return 'warning';
    return 'error';
  };

  return (
    <Grid container spacing={2}>
      {pedidos.map(pedido => (
        <Grid item xs={12} md={4} key={pedido.id}>
          <Card 
            sx={{ 
              p: 2,
              border: pedido.prioridade === 'urgente' ? '2px solid red' : 'none',
              animation: pedido.prioridade === 'urgente' ? 'pulse 1s infinite' : 'none'
            }}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 10 }}>
              <Typography variant="h6">
                Pedido #{pedido.numero}
              </Typography>
              <Chip 
                icon={<Timer />}
                label={`${pedido.tempo_decorrido} min`}
                color={getTempoColor(pedido.tempo_decorrido)}
              />
            </div>
            
            {pedido.mesa && (
              <Typography variant="subtitle2" color="textSecondary">
                Mesa: {pedido.mesa}
              </Typography>
            )}

            <div style={{ marginTop: 15 }}>
              {pedido.itens.map(item => (
                <div 
                  key={item.id}
                  style={{ 
                    padding: 10,
                    marginBottom: 8,
                    borderLeft: `4px solid ${item.status === 'pronto' ? 'green' : 'orange'}`,
                    backgroundColor: item.status === 'pronto' ? '#f0f9ff' : '#fff9f0'
                  }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <div>
                      <Typography variant="body1">
                        {item.quantidade}x {item.nome}
                      </Typography>
                      {item.observacoes && (
                        <Typography variant="caption" color="error">
                          OBS: {item.observacoes}
                        </Typography>
                      )}
                    </div>
                    <Button
                      size="small"
                      variant={item.status === 'pronto' ? 'contained' : 'outlined'}
                      color={item.status === 'pronto' ? 'success' : 'primary'}
                      onClick={() => updateItemStatus(
                        pedido.id, 
                        item.id, 
                        item.status === 'pronto' ? 'preparando' : 'pronto'
                      )}
                    >
                      {item.status === 'pronto' ? <CheckCircle /> : 'Marcar Pronto'}
                    </Button>
                  </div>
                </div>
              ))}
            </div>

            <Button 
              fullWidth 
              variant="contained" 
              color="success"
              sx={{ mt: 2 }}
              onClick={() => finalizarPedido(pedido.id)}
            >
              FINALIZAR PEDIDO
            </Button>
          </Card>
        </Grid>
      ))}
    </Grid>
  );
};
```

---

## 🎁 FASE 4: PROGRAMA DE FIDELIDADE (1 semana)
*Sistema de pontos e recompensas com gamificação*

### 4.1 Modelos de Fidelidade
```python
# backend/app/models/fidelidade.py
class ProgramaFidelidade(Base):
    __tablename__ = "programa_fidelidade"
    
    id = Column(String, primary_key=True)
    empresa_id = Column(String, ForeignKey("empresas.id"))
    nome = Column(String)
    
    # Configuração de pontos
    real_para_ponto = Column(Float, default=1.0)  # R$ 1 = 1 ponto
    pontos_indicacao = Column(Integer, default=100)
    pontos_aniversario = Column(Integer, default=500)
    pontos_primeira_compra = Column(Integer, default=50)
    validade_pontos_dias = Column(Integer, default=365)
    
    # Níveis
    niveis = Column(JSON)  # [{nome, pontos_min, beneficios, multiplicador}]
    
class ClienteFidelidade(Base):
    __tablename__ = "cliente_fidelidade"
    
    id = Column(String, primary_key=True)
    cliente_id = Column(String, ForeignKey("clientes.id"))
    programa_id = Column(String, ForeignKey("programa_fidelidade.id"))
    
    pontos_total = Column(Integer, default=0)
    pontos_disponiveis = Column(Integer, default=0)
    pontos_expirados = Column(Integer, default=0)
    
    nivel_atual = Column(String, default="bronze")
    data_proximo_nivel = Column(DateTime, nullable=True)
    
    # Métricas
    total_gasto = Column(Float, default=0)
    total_economizado = Column(Float, default=0)
    compras_realizadas = Column(Integer, default=0)
    
class MovimentoPontos(Base):
    __tablename__ = "movimento_pontos"
    
    id = Column(String, primary_key=True)
    cliente_fidelidade_id = Column(String, ForeignKey("cliente_fidelidade.id"))
    
    tipo = Column(Enum("credito", "debito", "expiracao"))
    pontos = Column(Integer)
    descricao = Column(String)
    
    # Referência
    origem_tipo = Column(String)  # venda, indicacao, aniversario, manual
    origem_id = Column(String, nullable=True)
    
    validade = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
```

### 4.2 Service de Fidelidade
```python
# backend/app/services/fidelidade_service.py
class FidelidadeService:
    async def adicionar_pontos(
        self, 
        cliente_id: str, 
        pontos: int, 
        origem: str,
        descricao: str
    ):
        """Adiciona pontos ao cliente com validade"""
        cliente_fidelidade = await self.get_or_create_cliente(cliente_id)
        programa = await self.get_programa(cliente_fidelidade.programa_id)
        
        # Calcular validade
        validade = datetime.utcnow() + timedelta(days=programa.validade_pontos_dias)
        
        # Registrar movimento
        movimento = MovimentoPontos(
            cliente_fidelidade_id=cliente_fidelidade.id,
            tipo='credito',
            pontos=pontos,
            descricao=descricao,
            origem_tipo=origem,
            validade=validade
        )
        await movimento.save()
        
        # Atualizar saldo
        cliente_fidelidade.pontos_total += pontos
        cliente_fidelidade.pontos_disponiveis += pontos
        
        # Verificar mudança de nível
        novo_nivel = self.calcular_nivel(cliente_fidelidade.pontos_total, programa.niveis)
        if novo_nivel != cliente_fidelidade.nivel_atual:
            await self.upgrade_nivel(cliente_fidelidade, novo_nivel)
            # Enviar notificação
            await self.notificar_upgrade(cliente_fidelidade, novo_nivel)
        
        await cliente_fidelidade.save()
        return movimento
    
    async def resgatar_pontos(
        self,
        cliente_id: str,
        pontos: int,
        recompensa_id: str
    ):
        """Resgata pontos por recompensa"""
        cliente_fidelidade = await self.get_cliente(cliente_id)
        
        if cliente_fidelidade.pontos_disponiveis < pontos:
            raise ValueError("Pontos insuficientes")
        
        recompensa = await self.get_recompensa(recompensa_id)
        
        # Criar cupom de desconto ou benefício
        cupom = await self.gerar_cupom_recompensa(recompensa)
        
        # Debitar pontos
        movimento = MovimentoPontos(
            cliente_fidelidade_id=cliente_fidelidade.id,
            tipo='debito',
            pontos=pontos,
            descricao=f"Resgate: {recompensa.nome}",
            origem_tipo='resgate',
            origem_id=cupom.id
        )
        await movimento.save()
        
        cliente_fidelidade.pontos_disponiveis -= pontos
        cliente_fidelidade.total_economizado += recompensa.valor_desconto
        await cliente_fidelidade.save()
        
        # Enviar cupom por email/WhatsApp
        await self.enviar_cupom(cliente_fidelidade.cliente, cupom)
        
        return cupom
    
    async def processar_venda_fidelidade(self, venda: Venda):
        """Processa pontos de uma venda"""
        if not venda.cliente_id:
            return
        
        programa = await self.get_programa_by_empresa(venda.empresa_id)
        if not programa:
            return
        
        # Calcular pontos base
        pontos_base = int(venda.total / programa.real_para_ponto)
        
        # Aplicar multiplicador do nível
        cliente_fidelidade = await self.get_cliente(venda.cliente_id)
        nivel = next(n for n in programa.niveis if n['nome'] == cliente_fidelidade.nivel_atual)
        pontos_final = int(pontos_base * nivel.get('multiplicador', 1.0))
        
        # Adicionar pontos
        await self.adicionar_pontos(
            cliente_id=venda.cliente_id,
            pontos=pontos_final,
            origem='venda',
            descricao=f"Compra #{venda.numero}"
        )
        
        # Verificar primeira compra
        if cliente_fidelidade.compras_realizadas == 0:
            await self.adicionar_pontos(
                cliente_id=venda.cliente_id,
                pontos=programa.pontos_primeira_compra,
                origem='bonus',
                descricao="Bônus de primeira compra"
            )
```

### 4.3 Frontend - Dashboard de Pontos
```tsx
// frontend/src/components/fidelidade/DashboardPontos.tsx
import React, { useState, useEffect } from 'react';
import { Card, Typography, Progress, Button, List, Badge } from 'antd';
import { Gift, Trophy, Star, TrendingUp } from 'lucide-react';

const DashboardPontos: React.FC<{ clienteId: string }> = ({ clienteId }) => {
  const [dados, setDados] = useState<any>(null);
  const [recompensas, setRecompensas] = useState<any[]>([]);

  useEffect(() => {
    fetchDadosFidelidade();
    fetchRecompensasDisponiveis();
  }, [clienteId]);

  const fetchDadosFidelidade = async () => {
    const response = await api.get(`/fidelidade/cliente/${clienteId}`);
    setDados(response.data);
  };

  const getNivelConfig = (nivel: string) => {
    const configs = {
      bronze: { color: '#cd7f32', icon: '🥉', next: 'prata' },
      prata: { color: '#c0c0c0', icon: '🥈', next: 'ouro' },
      ouro: { color: '#ffd700', icon: '🥇', next: 'diamante' },
      diamante: { color: '#b9f2ff', icon: '💎', next: null }
    };
    return configs[nivel] || configs.bronze;
  };

  const calcularProgressoNivel = () => {
    if (!dados) return 0;
    const proximoNivel = dados.pontos_proximo_nivel;
    const atualNivel = dados.pontos_nivel_atual;
    const progresso = ((dados.pontos_total - atualNivel) / (proximoNivel - atualNivel)) * 100;
    return Math.min(progresso, 100);
  };

  return (
    <div className="p-4">
      <Card className="mb-4">
        <div className="flex justify-between items-center mb-4">
          <div>
            <Typography.Title level={3}>
              Programa de Fidelidade
            </Typography.Title>
            <Typography.Text type="secondary">
              Cliente desde {new Date(dados?.data_cadastro).toLocaleDateString()}
            </Typography.Text>
          </div>
          <div className="text-center">
            <div style={{ fontSize: '3em' }}>
              {getNivelConfig(dados?.nivel_atual).icon}
            </div>
            <Typography.Text strong>
              Nível {dados?.nivel_atual?.toUpperCase()}
            </Typography.Text>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
          <Card size="small" className="text-center">
            <Star className="mx-auto mb-2" size={24} />
            <Typography.Title level={4}>
              {dados?.pontos_disponiveis || 0}
            </Typography.Title>
            <Typography.Text>Pontos Disponíveis</Typography.Text>
          </Card>

          <Card size="small" className="text-center">
            <Trophy className="mx-auto mb-2" size={24} />
            <Typography.Title level={4}>
              {dados?.pontos_total || 0}
            </Typography.Title>
            <Typography.Text>Pontos Totais</Typography.Text>
          </Card>

          <Card size="small" className="text-center">
            <TrendingUp className="mx-auto mb-2" size={24} />
            <Typography.Title level={4}>
              R$ {dados?.total_economizado || 0}
            </Typography.Title>
            <Typography.Text>Total Economizado</Typography.Text>
          </Card>
        </div>

        <div className="mb-4">
          <div className="flex justify-between mb-2">
            <Typography.Text>Progresso para {getNivelConfig(dados?.nivel_atual).next}</Typography.Text>
            <Typography.Text>{Math.round(calcularProgressoNivel())}%</Typography.Text>
          </div>
          <Progress 
            percent={calcularProgressoNivel()} 
            strokeColor={getNivelConfig(dados?.nivel_atual).color}
            showInfo={false}
          />
          <Typography.Text type="secondary" className="text-xs">
            Faltam {dados?.pontos_proximo_nivel - dados?.pontos_total} pontos
          </Typography.Text>
        </div>

        <div className="grid grid-cols-2 gap-2">
          {dados?.beneficios_nivel?.map((beneficio: string, index: number) => (
            <Badge key={index} count={<Gift size={16} />}>
              <Card size="small" className="w-full">
                <Typography.Text>{beneficio}</Typography.Text>
              </Card>
            </Badge>
          ))}
        </div>
      </Card>

      <Card title="Recompensas Disponíveis">
        <List
          dataSource={recompensas}
          renderItem={(recompensa) => (
            <List.Item
              actions={[
                <Button
                  type="primary"
                  disabled={dados?.pontos_disponiveis < recompensa.pontos_necessarios}
                  onClick={() => resgatarRecompensa(recompensa.id)}
                >
                  Resgatar ({recompensa.pontos_necessarios} pts)
                </Button>
              ]}
            >
              <List.Item.Meta
                avatar={<Gift size={32} />}
                title={recompensa.nome}
                description={recompensa.descricao}
              />
              <div className="text-right">
                <Typography.Title level={5} type="success">
                  {recompensa.tipo === 'desconto' 
                    ? `${recompensa.valor}% OFF` 
                    : `R$ ${recompensa.valor}`}
                </Typography.Title>
              </div>
            </List.Item>
          )}
        />
      </Card>
    </div>
  );
};
```

---

## 📊 FASE 5: DASHBOARD BI AVANÇADO (1 semana)
*Analytics e inteligência de negócios em tempo real*

### 5.1 Backend - Agregações e Métricas
```python
# backend/app/services/analytics_service.py
from typing import Dict, List, Any
import pandas as pd
from datetime import datetime, timedelta

class AnalyticsService:
    async def get_dashboard_metrics(
        self, 
        evento_id: str, 
        periodo: str = '7d'
    ) -> Dict[str, Any]:
        """Retorna métricas completas para dashboard"""
        
        # Calcular período
        end_date = datetime.utcnow()
        if periodo == '7d':
            start_date = end_date - timedelta(days=7)
        elif periodo == '30d':
            start_date = end_date - timedelta(days=30)
        else:
            start_date = datetime.strptime(periodo.split(',')[0], '%Y-%m-%d')
            end_date = datetime.strptime(periodo.split(',')[1], '%Y-%m-%d')
        
        metrics = {}
        
        # KPIs Principais
        metrics['kpis'] = await self.calculate_kpis(evento_id, start_date, end_date)
        
        # Análise de Vendas
        metrics['vendas'] = await self.analyze_sales(evento_id, start_date, end_date)
        
        # Análise de Clientes
        metrics['clientes'] = await self.analyze_customers(evento_id, start_date, end_date)
        
        # Análise de Produtos
        metrics['produtos'] = await self.analyze_products(evento_id, start_date, end_date)
        
        # Análise Temporal
        metrics['temporal'] = await self.analyze_temporal(evento_id, start_date, end_date)
        
        # Previsões
        metrics['previsoes'] = await self.generate_predictions(evento_id)
        
        return metrics
    
    async def calculate_kpis(self, evento_id: str, start_date: datetime, end_date: datetime):
        """Calcula KPIs principais"""
        
        # Query agregada para performance
        query = """
        WITH vendas_periodo AS (
            SELECT 
                COUNT(*) as total_vendas,
                SUM(total) as faturamento,
                AVG(total) as ticket_medio,
                COUNT(DISTINCT cliente_id) as clientes_unicos
            FROM vendas
            WHERE evento_id = :evento_id
                AND data_venda BETWEEN :start_date AND :end_date
                AND status = 'pago'
        ),
        vendas_anterior AS (
            SELECT 
                COUNT(*) as total_vendas,
                SUM(total) as faturamento
            FROM vendas
            WHERE evento_id = :evento_id
                AND data_venda BETWEEN :prev_start AND :prev_end
                AND status = 'pago'
        )
        SELECT 
            vp.*,
            va.total_vendas as vendas_anterior,
            va.faturamento as faturamento_anterior,
            CASE 
                WHEN va.faturamento > 0 
                THEN ((vp.faturamento - va.faturamento) / va.faturamento * 100)
                ELSE 0 
            END as crescimento_percentual
        FROM vendas_periodo vp, vendas_anterior va
        """
        
        # Calcular período anterior para comparação
        period_days = (end_date - start_date).days
        prev_start = start_date - timedelta(days=period_days)
        prev_end = start_date
        
        result = await db.execute(query, {
            'evento_id': evento_id,
            'start_date': start_date,
            'end_date': end_date,
            'prev_start': prev_start,
            'prev_end': prev_end
        })
        
        return result.first()
    
    async def analyze_temporal(self, evento_id: str, start_date: datetime, end_date: datetime):
        """Análise temporal de vendas"""
        
        # Vendas por hora do dia
        hourly = await db.execute("""
            SELECT 
                EXTRACT(HOUR FROM data_venda) as hora,
                COUNT(*) as vendas,
                SUM(total) as faturamento
            FROM vendas
            WHERE evento_id = :evento_id
                AND data_venda BETWEEN :start_date AND :end_date
            GROUP BY hora
            ORDER BY hora
        """, {'evento_id': evento_id, 'start_date': start_date, 'end_date': end_date})
        
        # Vendas por dia da semana
        weekly = await db.execute("""
            SELECT 
                EXTRACT(DOW FROM data_venda) as dia_semana,
                COUNT(*) as vendas,
                SUM(total) as faturamento
            FROM vendas
            WHERE evento_id = :evento_id
                AND data_venda BETWEEN :start_date AND :end_date
            GROUP BY dia_semana
            ORDER BY dia_semana
        """, {'evento_id': evento_id, 'start_date': start_date, 'end_date': end_date})
        
        return {
            'por_hora': hourly.all(),
            'por_dia_semana': weekly.all(),
            'horario_pico': max(hourly.all(), key=lambda x: x['vendas'])['hora'],
            'melhor_dia': max(weekly.all(), key=lambda x: x['faturamento'])['dia_semana']
        }
    
    async def generate_predictions(self, evento_id: str):
        """Gera previsões usando ML simples"""
        
        # Buscar histórico de vendas
        vendas_historico = await db.execute("""
            SELECT 
                DATE(data_venda) as data,
                COUNT(*) as vendas,
                SUM(total) as faturamento
            FROM vendas
            WHERE evento_id = :evento_id
            GROUP BY DATE(data_venda)
            ORDER BY data
        """, {'evento_id': evento_id})
        
        df = pd.DataFrame(vendas_historico.all())
        
        if len(df) < 7:
            return {'status': 'insufficient_data'}
        
        # Calcular média móvel e tendência
        df['ma7'] = df['faturamento'].rolling(window=7).mean()
        df['trend'] = df['faturamento'].pct_change(periods=7)
        
        # Previsão simples para próximos 7 dias
        last_ma = df['ma7'].iloc[-1]
        last_trend = df['trend'].iloc[-1:].mean()
        
        predictions = []
        for i in range(1, 8):
            predicted_value = last_ma * (1 + last_trend * i)
            predictions.append({
                'dia': i,
                'faturamento_previsto': round(predicted_value, 2),
                'confianca': max(0.5, 1 - (i * 0.1))  # Confiança diminui com o tempo
            })
        
        return {
            'status': 'success',
            'tendencia': 'alta' if last_trend > 0 else 'baixa',
            'crescimento_esperado': f"{last_trend * 100:.1f}%",
            'previsoes': predictions
        }
```

### 5.2 Frontend - Dashboard Interativo
```tsx
// frontend/src/components/bi/DashboardBI.tsx
import React, { useState, useEffect } from 'react';
import { Grid, Card, Select, DatePicker, Statistic, Alert } from 'antd';
import { 
  LineChart, Line, BarChart, Bar, PieChart, Pie, 
  AreaChart, Area, XAxis, YAxis, CartesianGrid, 
  Tooltip, Legend, ResponsiveContainer 
} from 'recharts';
import { ArrowUpOutlined, ArrowDownOutlined } from '@ant-design/icons';

const DashboardBI: React.FC = () => {
  const [metrics, setMetrics] = useState<any>(null);
  const [periodo, setPeriodo] = useState('7d');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchMetrics();
    
    // Atualizar a cada 30 segundos
    const interval = setInterval(fetchMetrics, 30000);
    return () => clearInterval(interval);
  }, [periodo]);

  const fetchMetrics = async () => {
    setLoading(true);
    try {
      const response = await api.get(`/bi/dashboard/metrics?periodo=${periodo}`);
      setMetrics(response.data);
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL'
    }).format(value);
  };

  return (
    <div className="p-4">
      {/* Header com Filtros */}
      <Card className="mb-4">
        <div className="flex justify-between items-center">
          <h2 className="text-2xl font-bold">Dashboard Analytics</h2>
          <Select
            value={periodo}
            onChange={setPeriodo}
            style={{ width: 200 }}
            options={[
              { label: 'Últimos 7 dias', value: '7d' },
              { label: 'Últimos 30 dias', value: '30d' },
              { label: 'Este mês', value: 'month' },
              { label: 'Personalizado', value: 'custom' }
            ]}
          />
        </div>
      </Card>

      {/* KPIs Principais */}
      <Grid container spacing={3} className="mb-4">
        <Grid item xs={12} md={3}>
          <Card>
            <Statistic
              title="Faturamento"
              value={metrics?.kpis?.faturamento || 0}
              precision={2}
              formatter={(value) => formatCurrency(Number(value))}
              valueStyle={{ color: '#3f8600' }}
              prefix={metrics?.kpis?.crescimento_percentual > 0 ? <ArrowUpOutlined /> : <ArrowDownOutlined />}
              suffix={
                <span style={{ fontSize: 14 }}>
                  {metrics?.kpis?.crescimento_percentual > 0 ? '+' : ''}
                  {metrics?.kpis?.crescimento_percentual?.toFixed(1)}%
                </span>
              }
            />
          </Card>
        </Grid>

        <Grid item xs={12} md={3}>
          <Card>
            <Statistic
              title="Total de Vendas"
              value={metrics?.kpis?.total_vendas || 0}
              suffix="vendas"
            />
          </Card>
        </Grid>

        <Grid item xs={12} md={3}>
          <Card>
            <Statistic
              title="Ticket Médio"
              value={metrics?.kpis?.ticket_medio || 0}
              precision={2}
              formatter={(value) => formatCurrency(Number(value))}
            />
          </Card>
        </Grid>

        <Grid item xs={12} md={3}>
          <Card>
            <Statistic
              title="Clientes Únicos"
              value={metrics?.kpis?.clientes_unicos || 0}
              suffix="clientes"
            />
          </Card>
        </Grid>
      </Grid>

      {/* Gráfico de Vendas */}
      <Grid container spacing={3} className="mb-4">
        <Grid item xs={12} md={8}>
          <Card title="Evolução de Vendas">
            <ResponsiveContainer width="100%" height={300}>
              <AreaChart data={metrics?.vendas?.evolucao || []}>
                <defs>
                  <linearGradient id="colorVendas" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#8884d8" stopOpacity={0.8}/>
                    <stop offset="95%" stopColor="#8884d8" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="data" />
                <YAxis />
                <Tooltip formatter={(value) => formatCurrency(Number(value))} />
                <Area 
                  type="monotone" 
                  dataKey="faturamento" 
                  stroke="#8884d8" 
                  fillOpacity={1} 
                  fill="url(#colorVendas)" 
                />
              </AreaChart>
            </ResponsiveContainer>
          </Card>
        </Grid>

        <Grid item xs={12} md={4}>
          <Card title="Vendas por Categoria">
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={metrics?.produtos?.por_categoria || []}
                  dataKey="valor"
                  nameKey="categoria"
                  cx="50%"
                  cy="50%"
                  outerRadius={80}
                  fill="#8884d8"
                  label
                />
                <Tooltip formatter={(value) => formatCurrency(Number(value))} />
              </PieChart>
            </ResponsiveContainer>
          </Card>
        </Grid>
      </Grid>

      {/* Análise Temporal */}
      <Grid container spacing={3} className="mb-4">
        <Grid item xs={12} md={6}>
          <Card title="Vendas por Hora do Dia">
            <ResponsiveContainer width="100%" height={250}>
              <BarChart data={metrics?.temporal?.por_hora || []}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="hora" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="vendas" fill="#82ca9d" />
              </BarChart>
            </ResponsiveContainer>
            <Alert
              message={`Horário de pico: ${metrics?.temporal?.horario_pico}h`}
              type="info"
              showIcon
              className="mt-2"
            />
          </Card>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card title="Vendas por Dia da Semana">
            <ResponsiveContainer width="100%" height={250}>
              <BarChart data={metrics?.temporal?.por_dia_semana || []}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="dia_semana" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="faturamento" fill="#ffc658" />
              </BarChart>
            </ResponsiveContainer>
          </Card>
        </Grid>
      </Grid>

      {/* Previsões */}
      {metrics?.previsoes?.status === 'success' && (
        <Card title="Previsões para Próximos 7 Dias">
          <Alert
            message={`Tendência: ${metrics.previsoes.tendencia} (${metrics.previsoes.crescimento_esperado})`}
            type={metrics.previsoes.tendencia === 'alta' ? 'success' : 'warning'}
            showIcon
            className="mb-3"
          />
          <ResponsiveContainer width="100%" height={200}>
            <LineChart data={metrics?.previsoes?.previsoes || []}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="dia" />
              <YAxis />
              <Tooltip formatter={(value) => formatCurrency(Number(value))} />
              <Line 
                type="monotone" 
                dataKey="faturamento_previsto" 
                stroke="#ff7300" 
                strokeDasharray="5 5"
              />
            </LineChart>
          </ResponsiveContainer>
        </Card>
      )}
    </div>
  );
};
```

---

## ⚡ FASE 6: OTIMIZAÇÕES DE PERFORMANCE (3-5 dias)

### 6.1 Implementar Cache Redis
```python
# backend/app/core/cache.py
import redis
import json
from typing import Optional, Any
from functools import wraps

redis_client = redis.Redis(
    host=os.getenv('REDIS_HOST', 'localhost'),
    port=int(os.getenv('REDIS_PORT', 6379)),
    db=0,
    decode_responses=True
)

def cache_key_wrapper(prefix: str, ttl: int = 300):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Gerar chave única baseada nos argumentos
            cache_key = f"{prefix}:{':'.join(map(str, args))}:{':'.join(f'{k}={v}' for k, v in kwargs.items())}"
            
            # Tentar buscar do cache
            cached = redis_client.get(cache_key)
            if cached:
                return json.loads(cached)
            
            # Executar função e cachear resultado
            result = await func(*args, **kwargs)
            redis_client.setex(cache_key, ttl, json.dumps(result, default=str))
            
            return result
        return wrapper
    return decorator

# Uso em endpoints
@router.get("/dashboard/metrics")
@cache_key_wrapper("dashboard", ttl=60)  # Cache por 1 minuto
async def get_dashboard_metrics(evento_id: str):
    # Lógica pesada aqui
    pass
```

### 6.2 WebSocket para Real-time
```python
# backend/app/core/websocket_manager.py
from typing import Dict, List
from fastapi import WebSocket
import json

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, channel: str):
        await websocket.accept()
        if channel not in self.active_connections:
            self.active_connections[channel] = []
        self.active_connections[channel].append(websocket)
    
    def disconnect(self, websocket: WebSocket, channel: str):
        if channel in self.active_connections:
            self.active_connections[channel].remove(websocket)
    
    async def broadcast(self, channel: str, message: dict):
        if channel in self.active_connections:
            for connection in self.active_connections[channel]:
                try:
                    await connection.send_json(message)
                except:
                    # Remove conexão morta
                    self.active_connections[channel].remove(connection)

manager = ConnectionManager()

# Em vendas
async def processar_venda(venda: Venda):
    # ... lógica de venda
    
    # Broadcast para dashboard
    await manager.broadcast(f"evento:{venda.evento_id}", {
        "type": "nova_venda",
        "venda": venda.dict(),
        "timestamp": datetime.utcnow().isoformat()
    })
```

---

## 🤖 FASE 7: FEATURES PREMIUM (2 semanas)

### 7.1 IA para Previsão de Demanda
```python
# backend/app/services/ai_service.py
from sklearn.ensemble import RandomForestRegressor
import numpy as np

class DemandPredictionService:
    def __init__(self):
        self.model = RandomForestRegressor(n_estimators=100)
    
    async def train_model(self, evento_id: str):
        """Treina modelo com dados históricos"""
        # Buscar dados históricos
        vendas = await db.execute("""
            SELECT 
                DATE(data_venda) as data,
                EXTRACT(DOW FROM data_venda) as dia_semana,
                EXTRACT(HOUR FROM data_venda) as hora,
                COUNT(*) as vendas,
                SUM(total) as faturamento,
                AVG(temperatura) as temperatura,
                COUNT(DISTINCT cliente_id) as clientes
            FROM vendas
            LEFT JOIN weather_data USING(data)
            WHERE evento_id = :evento_id
            GROUP BY DATE(data_venda), hora
        """, {'evento_id': evento_id})
        
        df = pd.DataFrame(vendas.all())
        
        # Features
        X = df[['dia_semana', 'hora', 'temperatura', 'clientes']].values
        y = df['vendas'].values
        
        # Treinar
        self.model.fit(X, y)
        
        # Salvar modelo
        joblib.dump(self.model, f'models/demand_{evento_id}.pkl')
    
    async def predict_demand(
        self, 
        evento_id: str, 
        data: datetime, 
        hora: int
    ) -> Dict:
        """Prevê demanda para data/hora específica"""
        
        # Carregar modelo
        self.model = joblib.load(f'models/demand_{evento_id}.pkl')
        
        # Features
        features = np.array([[
            data.weekday(),
            hora,
            await self.get_weather_forecast(data),
            await self.estimate_attendance(evento_id, data)
        ]])
        
        # Prever
        prediction = self.model.predict(features)[0]
        confidence = self.model.score(features, [prediction])
        
        return {
            'data': data.isoformat(),
            'hora': hora,
            'demanda_prevista': int(prediction),
            'confianca': confidence,
            'recomendacoes': self.gerar_recomendacoes(prediction)
        }
    
    def gerar_recomendacoes(self, demanda: int) -> List[str]:
        """Gera recomendações baseadas na demanda"""
        recomendacoes = []
        
        if demanda > 100:
            recomendacoes.append("Aumentar equipe de atendimento")
            recomendacoes.append("Preparar estoque adicional")
        
        if demanda > 200:
            recomendacoes.append("Abrir caixas adicionais")
            recomendacoes.append("Ativar modo de fila rápida")
        
        return recomendacoes
```

### 7.2 Reconhecimento Facial para Check-in
```python
# backend/app/services/facial_recognition.py
import face_recognition
import numpy as np
from typing import Optional

class FacialRecognitionService:
    def __init__(self):
        self.known_faces = {}  # Cache de encodings
    
    async def register_face(
        self, 
        cliente_id: str, 
        image_path: str
    ) -> bool:
        """Registra face do cliente"""
        try:
            # Carregar imagem
            image = face_recognition.load_image_file(image_path)
            
            # Extrair encoding
            encodings = face_recognition.face_encodings(image)
            
            if len(encodings) == 0:
                raise ValueError("Nenhuma face detectada")
            
            # Salvar no banco
            await db.execute("""
                INSERT INTO facial_encodings (cliente_id, encoding)
                VALUES (:cliente_id, :encoding)
                ON CONFLICT (cliente_id) 
                DO UPDATE SET encoding = :encoding
            """, {
                'cliente_id': cliente_id,
                'encoding': encodings[0].tobytes()
            })
            
            # Atualizar cache
            self.known_faces[cliente_id] = encodings[0]
            
            return True
            
        except Exception as e:
            logger.error(f"Erro ao registrar face: {e}")
            return False
    
    async def identify_face(
        self, 
        image_path: str
    ) -> Optional[str]:
        """Identifica cliente pela face"""
        try:
            # Carregar imagem
            unknown_image = face_recognition.load_image_file(image_path)
            unknown_encoding = face_recognition.face_encodings(unknown_image)[0]
            
            # Carregar faces conhecidas se não estiver em cache
            if not self.known_faces:
                await self.load_known_faces()
            
            # Comparar com faces conhecidas
            for cliente_id, known_encoding in self.known_faces.items():
                matches = face_recognition.compare_faces(
                    [known_encoding], 
                    unknown_encoding,
                    tolerance=0.6
                )
                
                if matches[0]:
                    # Calcular distância para confiança
                    distance = face_recognition.face_distance(
                        [known_encoding], 
                        unknown_encoding
                    )[0]
                    
                    confidence = (1 - distance) * 100
                    
                    if confidence > 70:  # Threshold de confiança
                        return cliente_id
            
            return None
            
        except Exception as e:
            logger.error(f"Erro na identificação facial: {e}")
            return None
```

---

## 📈 FASE 8: MONITORAMENTO E DEPLOY (3-5 dias)

### 8.1 Configurar Monitoramento
```python
# backend/app/core/monitoring.py
from prometheus_client import Counter, Histogram, Gauge
import time

# Métricas
request_count = Counter('app_requests_total', 'Total requests', ['method', 'endpoint'])
request_duration = Histogram('app_request_duration_seconds', 'Request duration')
active_users = Gauge('app_active_users', 'Active users')

# Middleware de monitoramento
@app.middleware("http")
async def monitoring_middleware(request: Request, call_next):
    start_time = time.time()
    
    # Incrementar contador
    request_count.labels(
        method=request.method,
        endpoint=request.url.path
    ).inc()
    
    # Processar request
    response = await call_next(request)
    
    # Medir duração
    duration = time.time() - start_time
    request_duration.observe(duration)
    
    # Adicionar headers de monitoramento
    response.headers["X-Process-Time"] = str(duration)
    
    return response

# Endpoint de métricas
@app.get("/metrics")
async def get_metrics():
    from prometheus_client import generate_latest
    return Response(generate_latest(), media_type="text/plain")
```

### 8.2 Docker Compose para Deploy
```yaml
# docker-compose.yml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@postgres:5432/meep
      - REDIS_URL=redis://redis:6379
      - SECRET_KEY=${SECRET_KEY}
    depends_on:
      - postgres
      - redis
    volumes:
      - ./backend:/app
    command: uvicorn app.main:app --host 0.0.0.0 --reload

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - VITE_API_URL=http://backend:8000
    volumes:
      - ./frontend:/app
      - /app/node_modules
    command: npm run dev

  postgres:
    image: postgres:14-alpine
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
      - POSTGRES_DB=meep
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - backend
      - frontend

volumes:
  postgres_data:
  redis_data:
```

---

## 📊 MÉTRICAS DE SUCESSO

### KPIs para Acompanhar
1. **Performance**
   - Tempo de resposta API < 200ms (P95)
   - Uptime > 99.9%
   - Conversão de vendas > 70%

2. **Negócio**
   - Aumento de 40% no ticket médio com fidelidade
   - Redução de 30% no tempo de check-in
   - ROI de 300% em 6 meses

3. **Técnico**
   - Cobertura de testes > 80%
   - Zero vulnerabilidades críticas
   - Deploy automatizado < 10 minutos

---

## 🎯 CRONOGRAMA RESUMIDO

| Fase | Duração | Entregáveis | Impacto |
|------|---------|-------------|---------|
| **Fase 1** | 3-5 dias | Sistema estável | Base sólida |
| **Fase 2** | 1 semana | Split de pagamentos | +Revenue sharing |
| **Fase 3** | 1 semana | KDS completo | +Eficiência operacional |
| **Fase 4** | 1 semana | Fidelidade | +Retenção clientes |
| **Fase 5** | 1 semana | Dashboard BI | +Inteligência negócio |
| **Fase 6** | 3-5 dias | Otimizações | +Performance 3x |
| **Fase 7** | 2 semanas | Features Premium | +Diferenciação |
| **Fase 8** | 3-5 dias | Deploy/Monitor | +Confiabilidade |

**TOTAL: 8-10 semanas**

---

## ✅ PRÓXIMOS PASSOS IMEDIATOS

1. **Hoje**: Aplicar correções da Fase 1
2. **Amanhã**: Começar implementação do Split
3. **Semana 1**: Completar Split + KDS
4. **Semana 2**: Fidelidade + BI
5. **Semana 3-4**: Otimizações + Premium
6. **Semana 5**: Deploy em produção

---

## 💡 RECOMENDAÇÕES FINAIS

1. **Priorize features que geram receita** (Split, Fidelidade)
2. **Implemente em produção incremental** (feature flags)
3. **Monitore métricas desde o início**
4. **Automatize testes e deploy**
5. **Documente as APIs novas**

Este plano transforma seu sistema em uma **plataforma premium** competitiva com o MEEP, aproveitando sua base sólida e economizando meses de desenvolvimento!