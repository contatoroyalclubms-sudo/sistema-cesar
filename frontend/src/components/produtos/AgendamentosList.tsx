import React, { useState, useEffect } from 'react';
import { ColumnDef } from '@tanstack/react-table';
import { 
  Pencil, 
  Trash2,
  Plus,
  Download,
  Calendar,
  Clock,
  Users,
  TrendingUp
} from 'lucide-react';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';
import { AgendamentoProduto, AgendamentoFilter } from '../../types/produto';
import { DataTable } from '../shared/DataTable';
import StatusToggle from '../shared/StatusToggle';
import ActionButton from '../shared/ActionButton';
import AgendamentoForm from './AgendamentoForm';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from '../ui/alert-dialog';
import { format } from 'date-fns';
import { ptBR } from 'date-fns/locale';

const AgendamentosList: React.FC = () => {
  const [agendamentos, setAgendamentos] = useState<AgendamentoProduto[]>([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState<AgendamentoFilter>({
    nome: ''
  });
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [editingAgendamento, setEditingAgendamento] = useState<AgendamentoProduto | undefined>(undefined);

  useEffect(() => {
    loadAgendamentos();
  }, [filters]);

  const loadAgendamentos = async () => {
    setLoading(true);
    try {
      // TODO: Implementar chamada para API
      // const response = await api.get('/agendamentos', { params: filters });
      // setAgendamentos(response.data);
      
      // Mock data para desenvolvimento
      setAgendamentos([
        {
          id: '1',
          nome: 'Happy Hour Cerveja',
          regra: 'Segunda a Quinta - 18:00 às 20:00',
          periodo: {
            inicio: new Date('2024-01-01'),
            fim: new Date('2024-12-31')
          },
          produtos: [
            {
              id: '1',
              nome: 'Cerveja Heineken 600ml',
              codigo: 'CERV001',
              categoria_id: '1',
              valor: 8.50,
              destaque: true,
              habilitado: true,
              promocional: false,
              created_at: new Date(),
              updated_at: new Date()
            }
          ],
          ativo: true,
          tipo: 'promocao',
          created_at: new Date('2024-01-01'),
          updated_at: new Date()
        },
        {
          id: '2',
          nome: 'Drinks Especiais Sexta',
          regra: 'Sexta - 23:00 às 03:00',
          periodo: {
            inicio: new Date('2024-01-01'),
            fim: new Date('2024-06-30')
          },
          produtos: [
            {
              id: '2',
              nome: 'Caipirinha de Cachaça',
              codigo: 'DRINK001',
              categoria_id: '2',
              valor: 12.00,
              destaque: false,
              habilitado: true,
              promocional: true,
              created_at: new Date(),
              updated_at: new Date()
            }
          ],
          ativo: true,
          tipo: 'evento',
          created_at: new Date('2024-01-15'),
          updated_at: new Date()
        },
        {
          id: '3',
          nome: 'Temporada Verão',
          regra: 'Dezembro a Março - Dia todo',
          periodo: {
            inicio: new Date('2023-12-01'),
            fim: new Date('2024-03-31')
          },
          produtos: [
            {
              id: '3',
              nome: 'Açaí Especial',
              codigo: 'ACAI001',
              categoria_id: '3',
              valor: 15.00,
              destaque: true,
              habilitado: true,
              promocional: false,
              created_at: new Date(),
              updated_at: new Date()
            }
          ],
          ativo: false,
          tipo: 'sazonal',
          created_at: new Date('2023-11-01'),
          updated_at: new Date()
        }
      ]);
    } catch (error) {
      console.error('Erro ao carregar agendamentos:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleToggleAtivo = async (id: string, checked: boolean) => {
    try {
      // TODO: Implementar chamada para API
      // await api.patch(`/agendamentos/${id}`, { ativo: checked });
      setAgendamentos(prev => prev.map(a => a.id === id ? { ...a, ativo: checked } : a));
    } catch (error) {
      console.error('Erro ao atualizar status:', error);
    }
  };

  const handleEdit = (agendamento: AgendamentoProduto) => {
    setEditingAgendamento(agendamento);
  };

  const handleDelete = async (agendamento: AgendamentoProduto) => {
    try {
      // TODO: Implementar chamada para API
      // await api.delete(`/agendamentos/${agendamento.id}`);
      setAgendamentos(prev => prev.filter(a => a.id !== agendamento.id));
    } catch (error) {
      console.error('Erro ao excluir agendamento:', error);
    }
  };

  const handleExport = () => {
    console.log('Exportando agendamentos');
    // TODO: Implementar exportação
  };

  const handleSaveAgendamento = async (data: any) => {
    try {
      if (editingAgendamento) {
        // TODO: Implementar chamada para API de atualização
        console.log('Atualizando agendamento:', data);
      } else {
        // TODO: Implementar chamada para API de criação
        console.log('Criando agendamento:', data);
      }
      
      // Recarregar lista
      await loadAgendamentos();
    } catch (error) {
      console.error('Erro ao salvar agendamento:', error);
      throw error;
    }
  };

  const handleCloseModal = () => {
    setShowCreateModal(false);
    setEditingAgendamento(undefined);
  };

  const getTipoBadgeColor = (tipo: string) => {
    switch (tipo) {
      case 'promocao':
        return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200';
      case 'evento':
        return 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200';
      case 'sazonal':
        return 'bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200';
      default:
        return 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200';
    }
  };

  const formatDate = (date: Date) => {
    return format(date, 'dd/MM/yyyy', { locale: ptBR });
  };

  const columns: ColumnDef<AgendamentoProduto>[] = [
    {
      accessorKey: 'nome',
      header: 'Nome',
      cell: ({ row }) => (
        <div className="min-w-0">
          <div className="font-medium text-foreground">{row.original.nome}</div>
          <div className="text-sm text-muted-foreground flex items-center gap-1">
            <Badge className={getTipoBadgeColor(row.original.tipo)}>
              {row.original.tipo === 'promocao' ? 'Promoção' : 
               row.original.tipo === 'evento' ? 'Evento' : 'Sazonal'}
            </Badge>
          </div>
        </div>
      ),
    },
    {
      accessorKey: 'regra',
      header: 'Regra',
      cell: ({ getValue }) => (
        <div className="flex items-center gap-2">
          <Clock className="h-4 w-4 text-muted-foreground" />
          <span className="text-sm bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200 px-2 py-1 rounded">
            {getValue() as string}
          </span>
        </div>
      ),
    },
    {
      accessorKey: 'periodo',
      header: 'Período',
      cell: ({ row }) => (
        <div className="text-sm space-y-1">
          <div className="flex items-center gap-1">
            <Calendar className="h-3 w-3 text-green-500" />
            <span>Início: {formatDate(row.original.periodo.inicio)}</span>
          </div>
          <div className="flex items-center gap-1">
            <Calendar className="h-3 w-3 text-red-500" />
            <span>Fim: {formatDate(row.original.periodo.fim)}</span>
          </div>
        </div>
      ),
    },
    {
      accessorKey: 'produtos',
      header: 'Produtos',
      cell: ({ row }) => (
        <div className="text-sm space-y-1">
          {row.original.produtos.slice(0, 3).map(produto => (
            <div key={produto.id} className="truncate max-w-48">
              {produto.nome}
            </div>
          ))}
          {row.original.produtos.length > 3 && (
            <div className="text-muted-foreground">
              +{row.original.produtos.length - 3} mais
            </div>
          )}
        </div>
      ),
    },
    {
      accessorKey: 'ativo',
      header: 'Ativo',
      cell: ({ row }) => (
        <StatusToggle
          checked={row.original.ativo}
          onChange={(checked) => handleToggleAtivo(row.original.id, checked)}
          color="green"
          size="sm"
        />
      ),
    },
    {
      id: 'actions',
      header: 'Ações',
      cell: ({ row }) => (
        <div className="flex items-center space-x-2">
          <ActionButton
            icon={Pencil}
            tooltip="Editar"
            onClick={() => handleEdit(row.original)}
            color="blue"
            size="sm"
          />
          <AlertDialog>
            <AlertDialogTrigger asChild>
              <ActionButton
                icon={Trash2}
                tooltip="Excluir"
                onClick={() => {}}
                color="red"
                size="sm"
              />
            </AlertDialogTrigger>
            <AlertDialogContent>
              <AlertDialogHeader>
                <AlertDialogTitle>Confirmar exclusão</AlertDialogTitle>
                <AlertDialogDescription>
                  Tem certeza que deseja excluir o agendamento "{row.original.nome}"? 
                  Esta ação não pode ser desfeita.
                </AlertDialogDescription>
              </AlertDialogHeader>
              <AlertDialogFooter>
                <AlertDialogCancel>Cancelar</AlertDialogCancel>
                <AlertDialogAction 
                  onClick={() => handleDelete(row.original)}
                  className="bg-red-600 hover:bg-red-700"
                >
                  Excluir
                </AlertDialogAction>
              </AlertDialogFooter>
            </AlertDialogContent>
          </AlertDialog>
        </div>
      ),
      enableSorting: false,
    },
  ];

  const agendamentosAtivos = agendamentos.filter(a => a.ativo).length;
  const totalProdutos = agendamentos.reduce((sum, a) => sum + a.produtos.length, 0);

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex justify-between items-start">
        <div>
          <h1 className="text-3xl font-bold text-foreground">AGENDAMENTO DE PRODUTOS</h1>
          <p className="text-muted-foreground mt-1">
            Configure promoções e produtos sazonais automaticamente
          </p>
        </div>
        
        <div className="flex items-center space-x-3">
          <Button variant="outline" onClick={handleExport} className="gap-2">
            <Download className="h-4 w-4" />
            Exportar
          </Button>
          <Button onClick={() => setShowCreateModal(true)} className="gap-2">
            <Plus className="h-4 w-4" />
            Novo Agendamento
          </Button>
        </div>
      </div>

      {/* Estatísticas rápidas */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-card p-4 rounded-lg border">
          <div className="flex items-center space-x-2">
            <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
              <Calendar className="h-5 w-5 text-blue-600" />
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Total de Agendamentos</p>
              <p className="text-2xl font-bold">{agendamentos.length}</p>
            </div>
          </div>
        </div>
        
        <div className="bg-card p-4 rounded-lg border">
          <div className="flex items-center space-x-2">
            <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
              <TrendingUp className="h-5 w-5 text-green-600" />
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Ativos</p>
              <p className="text-2xl font-bold">{agendamentosAtivos}</p>
            </div>
          </div>
        </div>
        
        <div className="bg-card p-4 rounded-lg border">
          <div className="flex items-center space-x-2">
            <div className="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center">
              <Users className="h-5 w-5 text-purple-600" />
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Produtos Agendados</p>
              <p className="text-2xl font-bold">{totalProdutos}</p>
            </div>
          </div>
        </div>
        
        <div className="bg-card p-4 rounded-lg border">
          <div className="flex items-center space-x-2">
            <div className="w-10 h-10 bg-orange-100 rounded-lg flex items-center justify-center">
              <Clock className="h-5 w-5 text-orange-600" />
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Promoções</p>
              <p className="text-2xl font-bold">
                {agendamentos.filter(a => a.tipo === 'promocao').length}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Tabela */}
      <DataTable 
        columns={columns}
        data={agendamentos}
        loading={loading}
        pageSize={10}
      />

      {/* Modal de criação/edição */}
      <AgendamentoForm
        agendamento={editingAgendamento}
        open={showCreateModal || !!editingAgendamento}
        onClose={handleCloseModal}
        onSave={handleSaveAgendamento}
      />
    </div>
  );
};

export default AgendamentosList;