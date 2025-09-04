import React, { useState, useEffect } from 'react';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Badge } from '../ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '../ui/table';
import { Alert, AlertDescription } from '../ui/alert';
import { 
  User, 
  UserPlus, 
  Search, 
  Edit, 
  Trash2, 
  Eye, 
  EyeOff,
  Phone,
  Mail,
  Building,
  Filter
} from 'lucide-react';
import { api } from '../../services/api';
import CadastroUsuarioModal from './CadastroUsuarioModal';

interface Usuario {
  id?: number;
  cpf: string;
  nome: string;
  email: string;
  telefone: string;
  tipo: 'admin' | 'promoter' | 'cliente';
  empresa_id: number;
  empresa?: {
    id: number;
    nome: string;
  };
  ativo?: boolean;
  ultimo_login?: string;
  criado_em?: string;
}

interface UsuarioDetalhado extends Usuario {
  id: number;
  ativo: boolean;
  criado_em: string;
}

interface UsuarioCreate extends Usuario {
  senha: string;
}

const UsuariosModule: React.FC = () => {
  const [usuarios, setUsuarios] = useState<UsuarioDetalhado[]>([]);
  const [loading, setLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterTipo, setFilterTipo] = useState<string>('todos');
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedUsuario, setSelectedUsuario] = useState<UsuarioDetalhado | null>(null);
  const [error, setError] = useState('');

  useEffect(() => {
    loadUsuarios();
  }, []);

  const loadUsuarios = async () => {
    try {
      setLoading(true);
      setError('');
      const response = await api.get('/api/usuarios/');
      setUsuarios(response.data);
    } catch (error: any) {
      console.error('Erro ao carregar usuários:', error);
      setError('Erro ao carregar usuários');
    } finally {
      setLoading(false);
    }
  };

  const handleSaveUsuario = async (usuarioData: UsuarioCreate | Usuario) => {
    try {
      if (selectedUsuario) {
        // Editar usuário existente
        await api.put(`/api/usuarios/${selectedUsuario.id}`, usuarioData);
      } else {
        // Criar novo usuário
        await api.post('/api/usuarios/', usuarioData);
      }
      
      await loadUsuarios();
      setIsModalOpen(false);
      setSelectedUsuario(null);
    } catch (error: any) {
      console.error('Erro ao salvar usuário:', error);
      throw error; // Re-throw para o modal tratar
    }
  };

  const handleEditUsuario = (usuario: UsuarioDetalhado) => {
    setSelectedUsuario(usuario);
    setIsModalOpen(true);
  };

  const handleDeleteUsuario = async (usuario: UsuarioDetalhado) => {
    if (window.confirm(`Tem certeza que deseja excluir o usuário "${usuario.nome}"?`)) {
      try {
        await api.delete(`/api/usuarios/${usuario.id}`);
        await loadUsuarios();
      } catch (error: any) {
        console.error('Erro ao excluir usuário:', error);
        alert('Erro ao excluir usuário');
      }
    }
  };

  const handleToggleStatus = async (usuario: UsuarioDetalhado) => {
    try {
      await api.patch(`/api/usuarios/${usuario.id}/status`, {
        ativo: !usuario.ativo
      });
      await loadUsuarios();
    } catch (error: any) {
      console.error('Erro ao alterar status do usuário:', error);
      alert('Erro ao alterar status do usuário');
    }
  };

  const filteredUsuarios = usuarios.filter(usuario => {
    const matchesSearch = 
      usuario.nome.toLowerCase().includes(searchTerm.toLowerCase()) ||
      usuario.cpf.includes(searchTerm) ||
      usuario.email.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesFilter = filterTipo === 'todos' || usuario.tipo === filterTipo;
    
    return matchesSearch && matchesFilter;
  });

  const formatCPF = (cpf: string) => {
    if (!cpf) return '-';
    return cpf.replace(/(\d{3})(\d{3})(\d{3})(\d{2})/, '$1.$2.$3-$4');
  };

  const formatPhone = (phone: string) => {
    if (!phone) return '-';
    if (phone.length === 11) {
      return phone.replace(/(\d{2})(\d{5})(\d{4})/, '($1) $2-$3');
    } else if (phone.length === 10) {
      return phone.replace(/(\d{2})(\d{4})(\d{4})/, '($1) $2-$3');
    }
    return phone;
  };

  const getTipoBadgeColor = (tipo: string) => {
    switch (tipo) {
      case 'admin':
        return 'bg-destructive/10 text-destructive border-destructive/20';
      case 'promoter':
        return 'bg-primary/10 text-primary border-primary/20';
      case 'cliente':
        return 'bg-green-500/10 text-green-600 border-green-500/20';
      default:
        return 'bg-muted text-muted-foreground border-border';
    }
  };

  const getTipoLabel = (tipo: string) => {
    switch (tipo) {
      case 'admin':
        return 'Administrador';
      case 'promoter':
        return 'Promoter';
      case 'cliente':
        return 'Cliente';
      default:
        return tipo;
    }
  };

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold flex items-center gap-2">
            <User className="h-6 w-6" />
            Gerenciar Usuários
          </h1>
          <p className="text-muted-foreground">
            Cadastre e gerencie usuários do sistema
          </p>
        </div>
        <Button onClick={() => setIsModalOpen(true)} className="flex items-center gap-2">
          <UserPlus className="h-4 w-4" />
          Novo Usuário
        </Button>
      </div>

      {/* Filtros */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex gap-4 flex-wrap">
            <div className="flex-1 min-w-[200px]">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground h-4 w-4" />
                <Input
                  placeholder="Buscar por nome, CPF ou email..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>
            <div className="flex items-center gap-2">
              <Filter className="h-4 w-4 text-muted-foreground" />
              <select
                value={filterTipo}
                onChange={(e) => setFilterTipo(e.target.value)}
                className="border border-input rounded-md px-3 py-2 bg-background text-foreground focus:outline-none focus:ring-1 focus:ring-ring"
              >
                <option value="todos">Todos os tipos</option>
                <option value="admin">Administradores</option>
                <option value="promoter">Promoters</option>
                <option value="cliente">Clientes</option>
              </select>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Tabela de Usuários */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            <span>Usuários Cadastrados ({filteredUsuarios.length})</span>
            <Button variant="outline" size="sm" onClick={loadUsuarios}>
              Atualizar
            </Button>
          </CardTitle>
        </CardHeader>
        <CardContent>
          {error && (
            <Alert className="mb-4">
              <AlertDescription className="text-destructive">
                {error}
              </AlertDescription>
            </Alert>
          )}

          {loading ? (
            <div className="text-center py-8">
              <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
              <p className="mt-2 text-muted-foreground">Carregando usuários...</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Usuário</TableHead>
                    <TableHead>CPF</TableHead>
                    <TableHead>Contato</TableHead>
                    <TableHead>Tipo</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Último Login</TableHead>
                    <TableHead className="text-right">Ações</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {filteredUsuarios.length === 0 ? (
                    <TableRow>
                      <TableCell colSpan={7} className="text-center py-8 text-muted-foreground">
                        {searchTerm || filterTipo !== 'todos' 
                          ? 'Nenhum usuário encontrado com os filtros aplicados'
                          : 'Nenhum usuário cadastrado'
                        }
                      </TableCell>
                    </TableRow>
                  ) : (
                    filteredUsuarios.map((usuario) => (
                      <TableRow key={usuario.id}>
                        <TableCell>
                          <div className="flex items-center gap-3">
                            <div className="h-8 w-8 bg-primary/10 rounded-full flex items-center justify-center">
                              <User className="h-4 w-4 text-primary" />
                            </div>
                            <div>
                              <div className="font-medium">{usuario.nome}</div>
                              <div className="text-sm text-muted-foreground flex items-center gap-1">
                                <Mail className="h-3 w-3" />
                                {usuario.email}
                              </div>
                            </div>
                          </div>
                        </TableCell>
                        
                        <TableCell className="font-mono">
                          {formatCPF(usuario.cpf)}
                        </TableCell>
                        
                        <TableCell>
                          <div className="flex items-center gap-1 text-sm">
                            <Phone className="h-3 w-3" />
                            {formatPhone(usuario.telefone)}
                          </div>
                          {usuario.empresa && (
                            <div className="flex items-center gap-1 text-xs text-muted-foreground mt-1">
                              <Building className="h-3 w-3" />
                              {usuario.empresa.nome}
                            </div>
                          )}
                        </TableCell>
                        
                        <TableCell>
                          <Badge className={getTipoBadgeColor(usuario.tipo)}>
                            {getTipoLabel(usuario.tipo)}
                          </Badge>
                        </TableCell>
                        
                        <TableCell>
                          <div className="flex items-center gap-2">
                            <div className={`h-2 w-2 rounded-full ${usuario.ativo ? 'bg-green-500' : 'bg-red-500'}`}></div>
                            <span className={usuario.ativo ? 'text-green-700' : 'text-red-700'}>
                              {usuario.ativo ? 'Ativo' : 'Inativo'}
                            </span>
                          </div>
                        </TableCell>
                        
                        <TableCell className="text-sm text-muted-foreground">
                          {usuario.ultimo_login 
                            ? new Date(usuario.ultimo_login).toLocaleDateString('pt-BR')
                            : 'Nunca'
                          }
                        </TableCell>
                        
                        <TableCell className="text-right">
                          <div className="flex items-center justify-end gap-1">
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => handleEditUsuario(usuario)}
                              title="Editar usuário"
                            >
                              <Edit className="h-4 w-4" />
                            </Button>
                            
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => handleToggleStatus(usuario)}
                              title={usuario.ativo ? 'Desativar usuário' : 'Ativar usuário'}
                            >
                              {usuario.ativo ? (
                                <EyeOff className="h-4 w-4" />
                              ) : (
                                <Eye className="h-4 w-4" />
                              )}
                            </Button>
                            
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => handleDeleteUsuario(usuario)}
                              className="text-destructive hover:text-destructive hover:bg-destructive/10"
                              title="Excluir usuário"
                            >
                              <Trash2 className="h-4 w-4" />
                            </Button>
                          </div>
                        </TableCell>
                      </TableRow>
                    ))
                  )}
                </TableBody>
              </Table>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Modal de Cadastro/Edição */}
      <CadastroUsuarioModal
        usuario={selectedUsuario}
        isOpen={isModalOpen}
        onClose={() => {
          setIsModalOpen(false);
          setSelectedUsuario(null);
        }}
        onSave={handleSaveUsuario}
      />
    </div>
  );
};

export default UsuariosModule;
