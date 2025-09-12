import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { RefreshCw, Calendar, Users, TrendingUp, DollarSign } from 'lucide-react';
import { meepService, MEEPEvento } from '@/services/meepApi';

export function MEEPDashboard() {
  const [eventos, setEventos] = useState<MEEPEvento[]>([]);
  const [loading, setLoading] = useState(false);
  const [syncing, setSyncing] = useState(false);

  useEffect(() => {
    loadEventos();
  }, []);

  const loadEventos = async () => {
    setLoading(true);
    try {
      const data = await meepService.getEventos();
      setEventos(data);
    } catch (error) {
      console.error('Erro ao carregar eventos:', error);
    } finally {
      setLoading(false);
    }
  };

  const sincronizar = async () => {
    setSyncing(true);
    try {
      await meepService.sincronizar();
      await loadEventos();
    } catch (error) {
      console.error('Erro ao sincronizar:', error);
    } finally {
      setSyncing(false);
    }
  };

  const stats = {
    totalEventos: eventos.length,
    totalInscritos: eventos.reduce((acc, e) => acc + e.total_inscritos, 0),
    totalPresentes: eventos.reduce((acc, e) => acc + e.total_presentes, 0),
    totalVendas: eventos.reduce((acc, e) => acc + e.total_vendas, 0),
  };

  return (
    <div className="space-y-6 p-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">Dashboard MEEP</h1>
          <p className="text-muted-foreground">Integração com sistema MEEP</p>
        </div>
        <div className="flex gap-2">
          <Button onClick={loadEventos} variant="outline" disabled={loading}>
            <RefreshCw className={`h-4 w-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
            Atualizar
          </Button>
          <Button onClick={sincronizar} disabled={syncing}>
            <RefreshCw className={`h-4 w-4 mr-2 ${syncing ? 'animate-spin' : ''}`} />
            Sincronizar
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm">Total de Eventos</CardTitle>
            <Calendar className="h-4 w-4" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.totalEventos}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm">Total de Inscritos</CardTitle>
            <Users className="h-4 w-4" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.totalInscritos}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm">Total de Presentes</CardTitle>
            <TrendingUp className="h-4 w-4" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.totalPresentes}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm">Vendas Totais</CardTitle>
            <DollarSign className="h-4 w-4" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              R$ {stats.totalVendas.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
            </div>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Eventos MEEP</CardTitle>
        </CardHeader>
        <CardContent>
          {loading ? (
            <p>Carregando...</p>
          ) : eventos.length > 0 ? (
            <div className="space-y-2">
              {eventos.map((evento) => (
                <div key={evento.id} className="flex justify-between p-3 border rounded">
                  <div>
                    <div className="font-medium">{evento.nome}</div>
                    <div className="text-sm text-muted-foreground">
                      {evento.local} • {evento.cidade}/{evento.estado}
                    </div>
                  </div>
                  <div className="text-right">
                    <Badge>{evento.sincronizado ? 'Sincronizado' : 'Pendente'}</Badge>
                    <div className="text-sm mt-1">
                      {evento.total_inscritos} inscritos • {evento.total_presentes} presentes
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p>Nenhum evento encontrado. Clique em Sincronizar para importar.</p>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
