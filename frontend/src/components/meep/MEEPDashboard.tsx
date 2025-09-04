import React from 'react';
import { motion } from 'framer-motion';
import { 
  Shield, 
  Zap, 
  Activity, 
  BarChart3,
  Smartphone,
  CheckCircle,
  Users,
  Clock
} from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs';

const MEEPDashboard: React.FC = () => {
  const metricas = {
    validacoesCPF: 1247,
    checkinsSucesso: 1186,
    equipamentosOnline: 8,
    alertasSeguranca: 3,
    tempoMedioCheckin: 18,
    taxaSucesso: 95.1
  };

  const modulosAtivos = [
    {
      nome: 'Validação CPF',
      status: 'ativo',
      descricao: 'Integração com Receita Federal',
      icon: Shield,
      color: 'text-green-600'
    },
    {
      nome: 'Check-in Multi-fator',
      status: 'ativo', 
      descricao: 'QR Code + 3 dígitos CPF',
      icon: Smartphone,
      color: 'text-blue-600'
    },
    {
      nome: 'Analytics IA',
      status: 'ativo',
      descricao: 'Insights em tempo real',
      icon: BarChart3,
      color: 'text-purple-600'
    },
    {
      nome: 'Gestão Equipamentos',
      status: 'ativo',
      descricao: 'Monitoramento de dispositivos',
      icon: Activity,
      color: 'text-orange-600'
    }
  ];

  const alertasRecentes = [
    {
      tipo: 'info',
      mensagem: 'Pico de acesso detectado às 14:30',
      timestamp: '15 min atrás'
    },
    {
      tipo: 'warning',
      mensagem: 'Equipamento Tablet-03 com bateria baixa',
      timestamp: '23 min atrás'
    },
    {
      tipo: 'success',
      mensagem: 'Meta de 1000 check-ins alcançada',
      timestamp: '1 hora atrás'
    }
  ];

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-6"
    >
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-foreground">MEEP Dashboard</h1>
          <p className="text-muted-foreground">
            Monitoramento, Eventos, Engajamento e Performance
          </p>
        </div>
        
        <div className="flex items-center space-x-2">
          <Badge variant="default" className="bg-green-100 text-green-800">
            <Zap className="h-3 w-3 mr-1" />
            Sistema Ativo
          </Badge>
        </div>
      </div>

      {/* Métricas Principais */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Validações CPF</CardTitle>
            <Shield className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{metricas.validacoesCPF.toLocaleString()}</div>
            <p className="text-xs text-muted-foreground">
              +{Math.round(metricas.validacoesCPF * 0.12)} desde ontem
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Check-ins Realizados</CardTitle>
            <CheckCircle className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{metricas.checkinsSucesso.toLocaleString()}</div>
            <p className="text-xs text-muted-foreground">
              Taxa de sucesso: {metricas.taxaSucesso}%
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Equipamentos Online</CardTitle>
            <Activity className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{metricas.equipamentosOnline}/10</div>
            <p className="text-xs text-muted-foreground">
              80% dos equipamentos ativos
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Tempo Médio Check-in</CardTitle>
            <Clock className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{metricas.tempoMedioCheckin}s</div>
            <p className="text-xs text-muted-foreground">
              -2s desde a última semana
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Participantes Ativos</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">847</div>
            <p className="text-xs text-muted-foreground">
              71% de ocupação máxima
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Alertas de Segurança</CardTitle>
            <Shield className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-yellow-600">{metricas.alertasSeguranca}</div>
            <p className="text-xs text-muted-foreground">
              Requer atenção
            </p>
          </CardContent>
        </Card>
      </div>

      <Tabs defaultValue="modulos" className="w-full">
        <TabsList>
          <TabsTrigger value="modulos">Módulos MEEP</TabsTrigger>
          <TabsTrigger value="alertas">Alertas Recentes</TabsTrigger>
          <TabsTrigger value="performance">Performance</TabsTrigger>
        </TabsList>

        <TabsContent value="modulos" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Módulos MEEP Ativos</CardTitle>
              <CardDescription>
                Status dos módulos principais do sistema MEEP
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {modulosAtivos.map((modulo, index) => (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, scale: 0.95 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ delay: index * 0.1 }}
                    className="flex items-center space-x-3 p-4 border rounded-lg hover:bg-muted/50 transition-colors"
                  >
                    <modulo.icon className={`h-8 w-8 ${modulo.color}`} />
                    <div className="flex-1">
                      <div className="font-medium">{modulo.nome}</div>
                      <div className="text-sm text-muted-foreground">{modulo.descricao}</div>
                    </div>
                    <Badge variant="default" className="bg-green-100 text-green-800">
                      {modulo.status}
                    </Badge>
                  </motion.div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="alertas" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Alertas e Notificações</CardTitle>
              <CardDescription>
                Últimas atividades e alertas do sistema
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {alertasRecentes.map((alerta, index) => (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.1 }}
                    className="flex items-center space-x-3 p-3 border rounded-lg"
                  >
                    <div className={`h-3 w-3 rounded-full ${
                      alerta.tipo === 'success' ? 'bg-green-500' :
                      alerta.tipo === 'warning' ? 'bg-yellow-500' :
                      alerta.tipo === 'error' ? 'bg-red-500' : 'bg-blue-500'
                    }`} />
                    <div className="flex-1">
                      <div className="text-sm">{alerta.mensagem}</div>
                      <div className="text-xs text-muted-foreground">{alerta.timestamp}</div>
                    </div>
                  </motion.div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="performance" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Métricas de Performance</CardTitle>
              <CardDescription>
                Indicadores de performance do sistema MEEP
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-6">
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span>Taxa de Sucesso Check-in</span>
                    <span className="font-medium">{metricas.taxaSucesso}%</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div 
                      className="bg-green-600 h-2 rounded-full" 
                      style={{ width: `${metricas.taxaSucesso}%` }}
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span>Disponibilidade de Equipamentos</span>
                    <span className="font-medium">80%</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div 
                      className="bg-blue-600 h-2 rounded-full" 
                      style={{ width: '80%' }}
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span>Performance Validação CPF</span>
                    <span className="font-medium">94%</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div 
                      className="bg-purple-600 h-2 rounded-full" 
                      style={{ width: '94%' }}
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span>Satisfação do Usuário</span>
                    <span className="font-medium">92%</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div 
                      className="bg-orange-600 h-2 rounded-full" 
                      style={{ width: '92%' }}
                    />
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Call to Action */}
      <Card className="bg-gradient-to-r from-blue-50 to-purple-50 border-blue-200">
        <CardContent className="pt-6">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-lg font-semibold text-blue-900">
                Sistema MEEP Ativo e Funcionando
              </h3>
              <p className="text-blue-700 mt-1">
                Todos os módulos principais estão operacionais. Explore as funcionalidades avançadas.
              </p>
            </div>
            <div className="flex space-x-2">
              <Button variant="outline">
                Ver Relatórios
              </Button>
              <Button>
                Analytics Avançado
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
    </motion.div>
  );
};

export default MEEPDashboard;
