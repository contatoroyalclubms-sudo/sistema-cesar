import React, { useState, useEffect } from 'react';
import { 
  Chart as ChartJS, 
  CategoryScale, 
  LinearScale, 
  BarElement, 
  Title, 
  Tooltip, 
  Legend,
  ArcElement,
  LineElement,
  PointElement
} from 'chart.js';
import { Bar, Pie, Line } from 'react-chartjs-2';
import { Card } from '../ui/card';
import { Loader2, TrendingUp, TrendingDown, DollarSign, ShoppingCart, Users, Target } from 'lucide-react';

ChartJS.register(
  CategoryScale, 
  LinearScale, 
  BarElement, 
  LineElement,
  PointElement,
  Title, 
  Tooltip, 
  Legend, 
  ArcElement
);

interface MetricasBI {
  vendas_hoje: number;
  ticket_medio: number;
  crescimento: number;
  comandas_ativas: number;
  vendas_mes: number;
  meta_mensal: number;
  crescimento_mes: number;
  produtos_vendidos: number;
}

interface GraficoDados {
  vendas_por_hora: {
    labels: string[];
    data: number[];
  };
  formas_pagamento: {
    labels: string[];
    data: number[];
  };
  produtos_mais_vendidos: {
    labels: string[];
    data: number[];
  };
  evolucao_vendas: {
    labels: string[];
    data: number[];
  };
}

export default function DashboardBI() {
  const [metricas, setMetricas] = useState<MetricasBI | null>(null);
  const [graficos, setGraficos] = useState<GraficoDados | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = async () => {
    try {
      setLoading(true);
      
      // Simular dados enquanto API não está pronta
      const mockMetricas: MetricasBI = {
        vendas_hoje: 23063.01,
        ticket_medio: 85.50,
        crescimento: 12.5,
        comandas_ativas: 37,
        vendas_mes: 450000,
        meta_mensal: 500000,
        crescimento_mes: 8.3,
        produtos_vendidos: 1247
      };

      const mockGraficos: GraficoDados = {
        vendas_por_hora: {
          labels: ['08:00', '09:00', '10:00', '11:00', '12:00', '13:00', '14:00', '15:00', '16:00', '17:00', '18:00', '19:00'],
          data: [150, 300, 450, 600, 1200, 1800, 1500, 900, 1100, 1400, 1600, 800]
        },
        formas_pagamento: {
          labels: ['PIX', 'Cartão Débito', 'Cartão Crédito', 'Dinheiro', 'Outros'],
          data: [45, 25, 20, 8, 2]
        },
        produtos_mais_vendidos: {
          labels: ['Café Expresso', 'Cappuccino', 'Açaí 300ml', 'Sanduíche Natural', 'Croissant'],
          data: [89, 76, 65, 54, 43]
        },
        evolucao_vendas: {
          labels: ['01/09', '02/09', '03/09', '04/09', '05/09', '06/09', '07/09'],
          data: [18500, 21000, 19800, 23500, 22000, 25000, 23063]
        }
      };

      setMetricas(mockMetricas);
      setGraficos(mockGraficos);
      
      // TODO: Substituir por chamada real da API
      // const response = await fetch('/api/bi/metricas-tempo-real');
      // const data = await response.json();
      // setMetricas(data);
      
    } catch (err) {
      setError('Erro ao carregar dados do BI');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
    
    // Atualizar dados a cada 30 segundos
    const interval = setInterval(fetchData, 30000);
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="h-8 w-8 animate-spin" />
        <span className="ml-2">Carregando Business Intelligence...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-64 text-red-600">
        <span>⚠️ {error}</span>
      </div>
    );
  }

  if (!metricas || !graficos) return null;

  // Configurações dos gráficos
  const vendasPorHoraConfig = {
    labels: graficos.vendas_por_hora.labels,
    datasets: [
      {
        label: 'Vendas por Hora (R$)',
        data: graficos.vendas_por_hora.data,
        backgroundColor: 'rgba(59, 130, 246, 0.8)',
        borderColor: 'rgba(59, 130, 246, 1)',
        borderWidth: 1,
      },
    ],
  };

  const formasPagamentoConfig = {
    labels: graficos.formas_pagamento.labels,
    datasets: [
      {
        data: graficos.formas_pagamento.data,
        backgroundColor: [
          '#10B981',
          '#3B82F6', 
          '#8B5CF6',
          '#F59E0B',
          '#6B7280'
        ],
      },
    ],
  };

  const evolucaoVendasConfig = {
    labels: graficos.evolucao_vendas.labels,
    datasets: [
      {
        label: 'Evolução das Vendas (R$)',
        data: graficos.evolucao_vendas.data,
        borderColor: 'rgb(59, 130, 246)',
        backgroundColor: 'rgba(59, 130, 246, 0.1)',
        tension: 0.4,
      },
    ],
  };

  const produtosMaisVendidosConfig = {
    labels: graficos.produtos_mais_vendidos.labels,
    datasets: [
      {
        label: 'Produtos Mais Vendidos',
        data: graficos.produtos_mais_vendidos.data,
        backgroundColor: 'rgba(16, 185, 129, 0.8)',
        borderColor: 'rgba(16, 185, 129, 1)',
        borderWidth: 1,
      },
    ],
  };

  const chartOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top' as const,
      },
    },
  };

  const pieOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'right' as const,
      },
    },
  };

  return (
    <div className="space-y-6">
      {/* Métricas Principais */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-sm font-medium text-gray-500">Vendas Hoje</h3>
              <p className="text-2xl font-bold text-gray-900">
                R$ {metricas.vendas_hoje.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
              </p>
              <p className="flex items-center text-sm mt-1">
                {metricas.crescimento > 0 ? (
                  <TrendingUp className="h-4 w-4 text-green-600 mr-1" />
                ) : (
                  <TrendingDown className="h-4 w-4 text-red-600 mr-1" />
                )}
                <span className={metricas.crescimento > 0 ? 'text-green-600' : 'text-red-600'}>
                  {metricas.crescimento.toFixed(1)}%
                </span>
                <span className="text-gray-500 ml-1">vs ontem</span>
              </p>
            </div>
            <DollarSign className="h-8 w-8 text-blue-600" />
          </div>
        </Card>

        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-sm font-medium text-gray-500">Ticket Médio</h3>
              <p className="text-2xl font-bold text-gray-900">
                R$ {metricas.ticket_medio.toFixed(2)}
              </p>
              <p className="text-sm text-gray-500 mt-1">
                {metricas.produtos_vendidos} produtos vendidos
              </p>
            </div>
            <ShoppingCart className="h-8 w-8 text-green-600" />
          </div>
        </Card>

        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-sm font-medium text-gray-500">Comandas Ativas</h3>
              <p className="text-2xl font-bold text-gray-900">
                {metricas.comandas_ativas}
              </p>
              <p className="text-sm text-gray-500 mt-1">
                Em andamento
              </p>
            </div>
            <Users className="h-8 w-8 text-orange-600" />
          </div>
        </Card>

        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-sm font-medium text-gray-500">Meta Mensal</h3>
              <p className="text-2xl font-bold text-gray-900">
                {((metricas.vendas_mes / metricas.meta_mensal) * 100).toFixed(1)}%
              </p>
              <p className="text-sm text-gray-500 mt-1">
                R$ {metricas.vendas_mes.toLocaleString('pt-BR')} / R$ {metricas.meta_mensal.toLocaleString('pt-BR')}
              </p>
            </div>
            <Target className="h-8 w-8 text-purple-600" />
          </div>
        </Card>
      </div>

      {/* Gráficos */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card className="p-6">
          <h3 className="text-lg font-semibold mb-4">Vendas por Hora</h3>
          <Bar data={vendasPorHoraConfig} options={chartOptions} />
        </Card>

        <Card className="p-6">
          <h3 className="text-lg font-semibold mb-4">Formas de Pagamento</h3>
          <Pie data={formasPagamentoConfig} options={pieOptions} />
        </Card>

        <Card className="p-6">
          <h3 className="text-lg font-semibold mb-4">Evolução das Vendas (7 dias)</h3>
          <Line data={evolucaoVendasConfig} options={chartOptions} />
        </Card>

        <Card className="p-6">
          <h3 className="text-lg font-semibold mb-4">Produtos Mais Vendidos</h3>
          <Bar data={produtosMaisVendidosConfig} options={chartOptions} />
        </Card>
      </div>
    </div>
  );
}
