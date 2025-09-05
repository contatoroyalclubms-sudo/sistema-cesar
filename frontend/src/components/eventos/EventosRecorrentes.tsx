import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { Checkbox } from '@/components/ui/checkbox';
import { Calendar } from '@/components/ui/calendar';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Alert, AlertDescription } from '@/components/ui/alert';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from '@/components/ui/popover';
import { useToast } from '@/hooks/use-toast';
import api from '@/lib/api';
import {
  CalendarDays,
  Plus,
  Repeat,
  Clock,
  Calendar as CalendarIcon,
  AlertTriangle,
  CheckCircle,
  XCircle,
  Settings,
  Trash2,
  Edit,
  Eye,
  CalendarX,
} from 'lucide-react';
import { format, addDays, addWeeks, addMonths, addYears, isBefore, isAfter } from 'date-fns';
import { ptBR } from 'date-fns/locale';
import { cn } from '@/lib/utils';

interface EventoRecorrencia {
  id: number;
  evento_pai_id: number;
  tipo_recorrencia: 'diario' | 'semanal' | 'mensal' | 'anual';
  intervalo: number;
  dias_semana?: number[];
  dia_mes?: number;
  data_fim?: string;
  max_ocorrencias?: number;
  excecoes: string[];
  ativo: boolean;
  ocorrencias_criadas: number;
  criado_em: string;
  atualizado_em?: string;
}

interface ProximaOcorrencia {
  data: string;
  nome: string;
  local: string;
  status: string;
}

interface EventoRecorrenteProps {
  evento: any;
  onClose?: () => void;
}

const diasSemana = [
  { value: 0, label: 'Dom', short: 'D' },
  { value: 1, label: 'Seg', short: 'S' },
  { value: 2, label: 'Ter', short: 'T' },
  { value: 3, label: 'Qua', short: 'Q' },
  { value: 4, label: 'Qui', short: 'Q' },
  { value: 5, label: 'Sex', short: 'S' },
  { value: 6, label: 'Sáb', short: 'S' },
];

export default function EventosRecorrentes({ evento, onClose }: EventoRecorrenteProps) {
  const [recorrencia, setRecorrencia] = useState<EventoRecorrencia | null>(null);
  const [proximasOcorrencias, setProximasOcorrencias] = useState<ProximaOcorrencia[]>([]);
  const [loading, setLoading] = useState(false);
  const [criandoRecorrencia, setCriandoRecorrencia] = useState(false);
  const [editandoRecorrencia, setEditandoRecorrencia] = useState(false);
  const [adicionandoExcecao, setAdicionandoExcecao] = useState(false);
  const [dataExcecao, setDataExcecao] = useState<Date | undefined>();
  const { toast } = useToast();

  const [novaRecorrencia, setNovaRecorrencia] = useState({
    tipo_recorrencia: 'semanal',
    intervalo: 1,
    dias_semana: [new Date(evento.data_evento).getDay()],
    dia_mes: new Date(evento.data_evento).getDate(),
    data_fim: undefined as Date | undefined,
    max_ocorrencias: '',
    excecoes: [] as string[],
  });

  useEffect(() => {
    if (evento) {
      loadRecorrencia();
    }
  }, [evento]);

  const loadRecorrencia = async () => {
    try {
      setLoading(true);
      const response = await api.get(`/api/eventos/recorrencia/${evento.id}`);
      setRecorrencia(response.data);
      
      if (response.data) {
        loadProximasOcorrencias();
      }
    } catch (error: any) {
      if (error.response?.status !== 404) {
        console.error('Erro ao carregar recorrência:', error);
      }
    } finally {
      setLoading(false);
    }
  };

  const loadProximasOcorrencias = async () => {
    try {
      const response = await api.get(`/api/eventos/recorrencia/${evento.id}/proximas`);
      setProximasOcorrencias(response.data);
    } catch (error) {
      console.error('Erro ao carregar próximas ocorrências:', error);
    }
  };

  const handleCreateRecorrencia = async () => {
    try {
      const payload = {
        ...novaRecorrencia,
        max_ocorrencias: novaRecorrencia.max_ocorrencias ? parseInt(novaRecorrencia.max_ocorrencias) : null,
        data_fim: novaRecorrencia.data_fim?.toISOString(),
      };

      const response = await api.post(`/api/eventos/recorrencia/${evento.id}`, payload);
      setRecorrencia(response.data);
      setCriandoRecorrencia(false);
      
      toast({
        title: 'Sucesso',
        description: 'Recorrência criada com sucesso',
      });

      loadProximasOcorrencias();
    } catch (error: any) {
      toast({
        variant: 'destructive',
        title: 'Erro',
        description: error.response?.data?.detail || 'Erro ao criar recorrência',
      });
    }
  };

  const handleUpdateRecorrencia = async () => {
    if (!recorrencia) return;

    try {
      const payload = {
        ativo: recorrencia.ativo,
        data_fim: recorrencia.data_fim,
        excecoes: recorrencia.excecoes,
      };

      const response = await api.put(`/api/eventos/recorrencia/${recorrencia.id}`, payload);
      setRecorrencia(response.data);
      setEditandoRecorrencia(false);
      
      toast({
        title: 'Sucesso',
        description: 'Recorrência atualizada com sucesso',
      });

      loadProximasOcorrencias();
    } catch (error: any) {
      toast({
        variant: 'destructive',
        title: 'Erro',
        description: error.response?.data?.detail || 'Erro ao atualizar recorrência',
      });
    }
  };

  const handleCancelRecorrencia = async (deletarFuturos: boolean = false) => {
    if (!recorrencia) return;

    try {
      await api.delete(`/api/eventos/recorrencia/${recorrencia.id}?deletar_futuros=${deletarFuturos}`);
      setRecorrencia(null);
      setProximasOcorrencias([]);
      
      toast({
        title: 'Sucesso',
        description: 'Recorrência cancelada com sucesso',
      });
    } catch (error: any) {
      toast({
        variant: 'destructive',
        title: 'Erro',
        description: error.response?.data?.detail || 'Erro ao cancelar recorrência',
      });
    }
  };

  const handleAddExcecao = async () => {
    if (!recorrencia || !dataExcecao) return;

    try {
      await api.post(`/api/eventos/recorrencia/${recorrencia.id}/excecoes`, {
        data_excecao: format(dataExcecao, 'yyyy-MM-dd'),
      });

      setAdicionandoExcecao(false);
      setDataExcecao(undefined);
      
      toast({
        title: 'Sucesso',
        description: 'Data de exceção adicionada',
      });

      loadRecorrencia();
      loadProximasOcorrencias();
    } catch (error: any) {
      toast({
        variant: 'destructive',
        title: 'Erro',
        description: error.response?.data?.detail || 'Erro ao adicionar exceção',
      });
    }
  };

  const getTipoRecorrenciaLabel = (tipo: string) => {
    const labels = {
      diario: 'Diário',
      semanal: 'Semanal',
      mensal: 'Mensal',
      anual: 'Anual',
    };
    return labels[tipo] || tipo;
  };

  const getRecorrenciaDescription = () => {
    if (!recorrencia) return '';

    let desc = `Repete ${getTipoRecorrenciaLabel(recorrencia.tipo_recorrencia).toLowerCase()}`;
    
    if (recorrencia.intervalo > 1) {
      desc += ` a cada ${recorrencia.intervalo} ${recorrencia.tipo_recorrencia === 'diario' ? 'dias' : 
                recorrencia.tipo_recorrencia === 'semanal' ? 'semanas' : 
                recorrencia.tipo_recorrencia === 'mensal' ? 'meses' : 'anos'}`;
    }

    if (recorrencia.tipo_recorrencia === 'semanal' && recorrencia.dias_semana) {
      const diasNomes = recorrencia.dias_semana.map(d => diasSemana.find(ds => ds.value === d)?.label).join(', ');
      desc += ` nas ${diasNomes}`;
    }

    if (recorrencia.tipo_recorrencia === 'mensal' && recorrencia.dia_mes) {
      desc += ` no dia ${recorrencia.dia_mes}`;
    }

    if (recorrencia.data_fim) {
      desc += ` até ${format(new Date(recorrencia.data_fim), 'dd/MM/yyyy', { locale: ptBR })}`;
    } else if (recorrencia.max_ocorrencias) {
      desc += ` por ${recorrencia.max_ocorrencias} ocorrências`;
    }

    return desc;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    );
  }

  if (!recorrencia && !criandoRecorrencia) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Evento Único</CardTitle>
          <CardDescription>
            Este evento não possui recorrência configurada
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-between p-4 border rounded-lg bg-muted/50">
            <div className="flex items-center gap-4">
              <CalendarIcon className="h-8 w-8 text-muted-foreground" />
              <div>
                <p className="font-medium">{evento.nome}</p>
                <p className="text-sm text-muted-foreground">
                  {format(new Date(evento.data_evento), "dd 'de' MMMM 'de' yyyy", { locale: ptBR })}
                </p>
              </div>
            </div>
            <Button onClick={() => setCriandoRecorrencia(true)}>
              <Repeat className="mr-2 h-4 w-4" />
              Tornar Recorrente
            </Button>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (criandoRecorrencia) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Configurar Recorrência</CardTitle>
          <CardDescription>
            Define como este evento deve se repetir
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label>Tipo de Recorrência</Label>
                <Select
                  value={novaRecorrencia.tipo_recorrencia}
                  onValueChange={(value) => setNovaRecorrencia({ ...novaRecorrencia, tipo_recorrencia: value })}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="diario">Diário</SelectItem>
                    <SelectItem value="semanal">Semanal</SelectItem>
                    <SelectItem value="mensal">Mensal</SelectItem>
                    <SelectItem value="anual">Anual</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label>Intervalo</Label>
                <Input
                  type="number"
                  min="1"
                  value={novaRecorrencia.intervalo}
                  onChange={(e) => setNovaRecorrencia({ ...novaRecorrencia, intervalo: parseInt(e.target.value) || 1 })}
                />
              </div>
            </div>

            {novaRecorrencia.tipo_recorrencia === 'semanal' && (
              <div className="space-y-2">
                <Label>Dias da Semana</Label>
                <div className="flex gap-2">
                  {diasSemana.map((dia) => (
                    <Button
                      key={dia.value}
                      variant={novaRecorrencia.dias_semana.includes(dia.value) ? 'default' : 'outline'}
                      size="sm"
                      className="w-10 h-10 p-0"
                      onClick={() => {
                        const newDias = novaRecorrencia.dias_semana.includes(dia.value)
                          ? novaRecorrencia.dias_semana.filter(d => d !== dia.value)
                          : [...novaRecorrencia.dias_semana, dia.value];
                        setNovaRecorrencia({ ...novaRecorrencia, dias_semana: newDias });
                      }}
                    >
                      {dia.short}
                    </Button>
                  ))}
                </div>
              </div>
            )}

            {novaRecorrencia.tipo_recorrencia === 'mensal' && (
              <div className="space-y-2">
                <Label>Dia do Mês</Label>
                <Input
                  type="number"
                  min="1"
                  max="31"
                  value={novaRecorrencia.dia_mes}
                  onChange={(e) => setNovaRecorrencia({ ...novaRecorrencia, dia_mes: parseInt(e.target.value) || 1 })}
                />
              </div>
            )}

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label>Data de Término (opcional)</Label>
                <Popover>
                  <PopoverTrigger asChild>
                    <Button
                      variant="outline"
                      className={cn(
                        "w-full justify-start text-left font-normal",
                        !novaRecorrencia.data_fim && "text-muted-foreground"
                      )}
                    >
                      <CalendarIcon className="mr-2 h-4 w-4" />
                      {novaRecorrencia.data_fim ? (
                        format(novaRecorrencia.data_fim, 'dd/MM/yyyy', { locale: ptBR })
                      ) : (
                        <span>Selecione uma data</span>
                      )}
                    </Button>
                  </PopoverTrigger>
                  <PopoverContent className="w-auto p-0">
                    <Calendar
                      mode="single"
                      selected={novaRecorrencia.data_fim}
                      onSelect={(date) => setNovaRecorrencia({ ...novaRecorrencia, data_fim: date })}
                      initialFocus
                      locale={ptBR}
                      disabled={(date) => isBefore(date, new Date(evento.data_evento))}
                    />
                  </PopoverContent>
                </Popover>
              </div>

              <div className="space-y-2">
                <Label>Máximo de Ocorrências (opcional)</Label>
                <Input
                  type="number"
                  min="1"
                  placeholder="Ex: 10"
                  value={novaRecorrencia.max_ocorrencias}
                  onChange={(e) => setNovaRecorrencia({ ...novaRecorrencia, max_ocorrencias: e.target.value })}
                  disabled={!!novaRecorrencia.data_fim}
                />
              </div>
            </div>

            <Alert>
              <AlertTriangle className="h-4 w-4" />
              <AlertDescription>
                Serão criados eventos automáticos baseados nesta configuração de recorrência
              </AlertDescription>
            </Alert>
          </div>

          <div className="flex justify-end gap-2">
            <Button variant="outline" onClick={() => setCriandoRecorrencia(false)}>
              Cancelar
            </Button>
            <Button onClick={handleCreateRecorrencia}>
              Criar Recorrência
            </Button>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>Evento Recorrente</CardTitle>
              <CardDescription>{getRecorrenciaDescription()}</CardDescription>
            </div>
            <Badge variant={recorrencia?.ativo ? 'default' : 'secondary'}>
              {recorrencia?.ativo ? 'Ativo' : 'Inativo'}
            </Badge>
          </div>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-3">
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-sm font-medium">
                  Tipo de Recorrência
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex items-center gap-2">
                  <Repeat className="h-4 w-4 text-muted-foreground" />
                  <span className="font-medium">
                    {getTipoRecorrenciaLabel(recorrencia?.tipo_recorrencia || '')}
                  </span>
                </div>
                {recorrencia?.intervalo && recorrencia.intervalo > 1 && (
                  <p className="text-sm text-muted-foreground mt-1">
                    A cada {recorrencia.intervalo} {recorrencia.tipo_recorrencia === 'diario' ? 'dias' : 
                             recorrencia.tipo_recorrencia === 'semanal' ? 'semanas' : 
                             recorrencia.tipo_recorrencia === 'mensal' ? 'meses' : 'anos'}
                  </p>
                )}
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-sm font-medium">
                  Ocorrências
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex items-center gap-2">
                  <CalendarDays className="h-4 w-4 text-muted-foreground" />
                  <span className="font-medium">{recorrencia?.ocorrencias_criadas || 0}</span>
                </div>
                <p className="text-sm text-muted-foreground mt-1">
                  eventos criados
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-sm font-medium">
                  Exceções
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex items-center gap-2">
                  <CalendarX className="h-4 w-4 text-muted-foreground" />
                  <span className="font-medium">{recorrencia?.excecoes?.length || 0}</span>
                </div>
                <p className="text-sm text-muted-foreground mt-1">
                  datas puladas
                </p>
              </CardContent>
            </Card>
          </div>

          <div className="flex justify-end gap-2 mt-4">
            <Button
              variant="outline"
              onClick={() => setAdicionandoExcecao(true)}
            >
              <CalendarX className="mr-2 h-4 w-4" />
              Adicionar Exceção
            </Button>
            <Button
              variant="outline"
              onClick={() => setEditandoRecorrencia(true)}
            >
              <Edit className="mr-2 h-4 w-4" />
              Editar
            </Button>
            <Button
              variant="destructive"
              onClick={() => handleCancelRecorrencia(false)}
            >
              <XCircle className="mr-2 h-4 w-4" />
              Cancelar Recorrência
            </Button>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Próximas Ocorrências</CardTitle>
          <CardDescription>
            Eventos que serão criados automaticamente
          </CardDescription>
        </CardHeader>
        <CardContent>
          {proximasOcorrencias.length > 0 ? (
            <div className="space-y-2">
              {proximasOcorrencias.map((ocorrencia, index) => (
                <div
                  key={index}
                  className="flex items-center justify-between p-3 border rounded-lg"
                >
                  <div className="flex items-center gap-3">
                    <CalendarIcon className="h-4 w-4 text-muted-foreground" />
                    <div>
                      <p className="font-medium">
                        {format(new Date(ocorrencia.data), "dd 'de' MMMM 'de' yyyy", { locale: ptBR })}
                      </p>
                      <p className="text-sm text-muted-foreground">
                        {format(new Date(ocorrencia.data), "EEEE 'às' HH:mm", { locale: ptBR })}
                      </p>
                    </div>
                  </div>
                  <Badge variant="outline">{ocorrencia.status}</Badge>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8">
              <CalendarX className="mx-auto h-12 w-12 text-muted-foreground" />
              <p className="mt-2 text-sm text-muted-foreground">
                Nenhuma ocorrência futura programada
              </p>
            </div>
          )}
        </CardContent>
      </Card>

      <Dialog open={adicionandoExcecao} onOpenChange={setAdicionandoExcecao}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Adicionar Exceção</DialogTitle>
            <DialogDescription>
              Selecione uma data para pular nesta recorrência
            </DialogDescription>
          </DialogHeader>
          <div className="py-4">
            <Calendar
              mode="single"
              selected={dataExcecao}
              onSelect={setDataExcecao}
              initialFocus
              locale={ptBR}
              disabled={(date) => isBefore(date, new Date())}
            />
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setAdicionandoExcecao(false)}>
              Cancelar
            </Button>
            <Button onClick={handleAddExcecao} disabled={!dataExcecao}>
              Adicionar Exceção
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      <Dialog open={editandoRecorrencia} onOpenChange={setEditandoRecorrencia}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Editar Recorrência</DialogTitle>
            <DialogDescription>
              Modifique as configurações de recorrência
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div className="flex items-center justify-between">
              <Label htmlFor="ativo">Status da Recorrência</Label>
              <Checkbox
                id="ativo"
                checked={recorrencia?.ativo}
                onCheckedChange={(checked) => 
                  setRecorrencia({ ...recorrencia!, ativo: checked as boolean })
                }
              />
            </div>
            <Alert>
              <AlertTriangle className="h-4 w-4" />
              <AlertDescription>
                Pausar a recorrência não afeta eventos já criados
              </AlertDescription>
            </Alert>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setEditandoRecorrencia(false)}>
              Cancelar
            </Button>
            <Button onClick={handleUpdateRecorrencia}>
              Salvar Alterações
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}