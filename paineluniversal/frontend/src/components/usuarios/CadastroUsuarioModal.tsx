import React, { useState, useEffect } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '../ui/dialog';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Label } from '../ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/select';
import { Alert, AlertDescription } from '../ui/alert';
import { Eye, EyeOff, User, Mail, Phone, CreditCard } from 'lucide-react';
import { api } from '../../services/api';

interface Usuario {
  id?: number;
  cpf: string;
  nome: string;
  email: string;
  telefone: string;
  tipo: 'admin' | 'promoter' | 'cliente';
  ativo?: boolean;
}

interface UsuarioCreate extends Usuario {
  senha: string;
}


interface CadastroUsuarioModalProps {
  usuario?: Usuario | null;
  isOpen: boolean;
  onClose: () => void;
  onSave: (usuario: UsuarioCreate | Usuario) => void;
}

const CadastroUsuarioModal: React.FC<CadastroUsuarioModalProps> = ({
  usuario,
  isOpen,
  onClose,
  onSave
}) => {
  const [formData, setFormData] = useState<UsuarioCreate>({
    cpf: '',
    nome: '',
    email: '',
    telefone: '',
    senha: '',
    tipo: 'cliente',
    ativo: true
  });
  
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);


  // Preencher formulário se estiver editando
  useEffect(() => {
    if (usuario) {
      setFormData({
        cpf: usuario.cpf,
        nome: usuario.nome,
        email: usuario.email,
        telefone: usuario.telefone || '',
        senha: '', // Não mostrar senha atual por segurança
        tipo: usuario.tipo,
        ativo: usuario.ativo ?? true
      });
    } else {
      // Reset para novo usuário
      setFormData({
        cpf: '',
        nome: '',
        email: '',
        telefone: '',
        senha: '',
        tipo: 'cliente',
        ativo: true
      });
    }
    setErrors({});
  }, [usuario, isOpen]);


  const formatCPF = (value: string) => {
    // Remove todos os caracteres não numéricos
    const numbers = value.replace(/\D/g, '');
    
    // Aplica a máscara XXX.XXX.XXX-XX
    if (numbers.length <= 11) {
      return numbers
        .replace(/(\d{3})(\d)/, '$1.$2')
        .replace(/(\d{3})(\d)/, '$1.$2')
        .replace(/(\d{3})(\d{1,2})/, '$1-$2');
    }
    return numbers.slice(0, 11);
  };

  const formatPhone = (value: string) => {
    // Remove todos os caracteres não numéricos
    const numbers = value.replace(/\D/g, '');
    
    // Aplica a máscara (XX) XXXXX-XXXX ou (XX) XXXX-XXXX
    if (numbers.length <= 11) {
      if (numbers.length <= 10) {
        return numbers
          .replace(/(\d{2})(\d)/, '($1) $2')
          .replace(/(\d{4})(\d{1,4})/, '$1-$2');
      } else {
        return numbers
          .replace(/(\d{2})(\d)/, '($1) $2')
          .replace(/(\d{5})(\d{1,4})/, '$1-$2');
      }
    }
    return numbers.slice(0, 11);
  };

  const validateForm = () => {
    const newErrors: Record<string, string> = {};
    
    // CPF obrigatório e deve ter 11 dígitos
    const cpfNumbers = formData.cpf.replace(/\D/g, '');
    if (!cpfNumbers) {
      newErrors.cpf = 'CPF é obrigatório';
    } else if (cpfNumbers.length !== 11) {
      newErrors.cpf = 'CPF deve ter 11 dígitos';
    }
    
    // Nome obrigatório
    if (!formData.nome.trim()) {
      newErrors.nome = 'Nome é obrigatório';
    }
    
    // Email obrigatório e formato válido
    if (!formData.email.trim()) {
      newErrors.email = 'Email é obrigatório';
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      newErrors.email = 'Email inválido';
    }
    
    // Senha obrigatória apenas para novos usuários
    if (!usuario && !formData.senha) {
      newErrors.senha = 'Senha é obrigatória';
    } else if (formData.senha && formData.senha.length < 4) {
      newErrors.senha = 'Senha deve ter pelo menos 4 caracteres';
    }
    
    // Telefone opcional, mas se preenchido deve ter formato válido
    if (formData.telefone) {
      const phoneNumbers = formData.telefone.replace(/\D/g, '');
      if (phoneNumbers.length < 10 || phoneNumbers.length > 11) {
        newErrors.telefone = 'Telefone deve ter 10 ou 11 dígitos';
      }
    }
    
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }
    
    try {
      setLoading(true);
      
      // Preparar dados para envio
      const dataToSend = {
        ...formData,
        cpf: formData.cpf.replace(/\D/g, ''), // Remover máscara do CPF
        telefone: formData.telefone.replace(/\D/g, '') // Remover máscara do telefone
      };
      
      // Se não há senha (editando), remover do objeto
      if (usuario && !dataToSend.senha) {
        delete dataToSend.senha;
      }
      
      onSave(dataToSend);
      onClose();
    } catch (error: any) {
      console.error('Erro ao salvar usuário:', error);
      if (error.response?.data?.detail) {
        if (typeof error.response.data.detail === 'string') {
          setErrors({ submit: error.response.data.detail });
        } else {
          setErrors({ submit: 'Erro ao salvar usuário' });
        }
      } else {
        setErrors({ submit: 'Erro interno do servidor' });
      }
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (field: keyof UsuarioCreate, value: string | number) => {
    if (field === 'cpf') {
      setFormData(prev => ({ ...prev, [field]: formatCPF(value as string) }));
    } else if (field === 'telefone') {
      setFormData(prev => ({ ...prev, [field]: formatPhone(value as string) }));
    } else {
      setFormData(prev => ({ ...prev, [field]: value }));
    }
    
    // Limpar erro do campo quando o usuário digitar
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: '' }));
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-md max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <User className="h-5 w-5" />
            {usuario ? 'Editar Usuário' : 'Cadastrar Novo Usuário'}
          </DialogTitle>
        </DialogHeader>
        
        <form onSubmit={handleSubmit} className="space-y-4">
          {/* CPF */}
          <div className="space-y-2">
            <Label htmlFor="cpf" className="flex items-center gap-2">
              <CreditCard className="h-4 w-4" />
              CPF
            </Label>
            <Input
              id="cpf"
              type="text"
              placeholder="000.000.000-00"
              value={formData.cpf}
              onChange={(e) => handleInputChange('cpf', e.target.value)}
              className={errors.cpf ? 'border-red-500' : ''}
              maxLength={14}
            />
            {errors.cpf && (
              <p className="text-sm text-red-500">{errors.cpf}</p>
            )}
          </div>

          {/* Nome */}
          <div className="space-y-2">
            <Label htmlFor="nome" className="flex items-center gap-2">
              <User className="h-4 w-4" />
              Nome Completo
            </Label>
            <Input
              id="nome"
              type="text"
              placeholder="Nome completo do usuário"
              value={formData.nome}
              onChange={(e) => handleInputChange('nome', e.target.value)}
              className={errors.nome ? 'border-red-500' : ''}
            />
            {errors.nome && (
              <p className="text-sm text-red-500">{errors.nome}</p>
            )}
          </div>

          {/* Email */}
          <div className="space-y-2">
            <Label htmlFor="email" className="flex items-center gap-2">
              <Mail className="h-4 w-4" />
              Email
            </Label>
            <Input
              id="email"
              type="email"
              placeholder="usuario@email.com"
              value={formData.email}
              onChange={(e) => handleInputChange('email', e.target.value)}
              className={errors.email ? 'border-red-500' : ''}
            />
            {errors.email && (
              <p className="text-sm text-red-500">{errors.email}</p>
            )}
          </div>

          {/* Telefone */}
          <div className="space-y-2">
            <Label htmlFor="telefone" className="flex items-center gap-2">
              <Phone className="h-4 w-4" />
              Telefone (Opcional)
            </Label>
            <Input
              id="telefone"
              type="text"
              placeholder="(11) 99999-9999"
              value={formData.telefone}
              onChange={(e) => handleInputChange('telefone', e.target.value)}
              className={errors.telefone ? 'border-red-500' : ''}
              maxLength={15}
            />
            {errors.telefone && (
              <p className="text-sm text-red-500">{errors.telefone}</p>
            )}
          </div>

          {/* Senha */}
          <div className="space-y-2">
            <Label htmlFor="senha" className="flex items-center gap-2">
              <Eye className="h-4 w-4" />
              {usuario ? 'Nova Senha (deixe vazio para manter)' : 'Senha'}
            </Label>
            <div className="relative">
              <Input
                id="senha"
                type={showPassword ? 'text' : 'password'}
                placeholder={usuario ? 'Nova senha...' : 'Senha do usuário'}
                value={formData.senha}
                onChange={(e) => handleInputChange('senha', e.target.value)}
                className={errors.senha ? 'border-red-500' : ''}
              />
              <Button
                type="button"
                variant="ghost"
                size="sm"
                className="absolute right-0 top-0 h-full px-3 py-2 hover:bg-transparent"
                onClick={() => setShowPassword(!showPassword)}
              >
                {showPassword ? (
                  <EyeOff className="h-4 w-4" />
                ) : (
                  <Eye className="h-4 w-4" />
                )}
              </Button>
            </div>
            {errors.senha && (
              <p className="text-sm text-red-500">{errors.senha}</p>
            )}
          </div>

          {/* Tipo de Usuário */}
          <div className="space-y-2">
            <Label htmlFor="tipo" className="flex items-center gap-2">
              <User className="h-4 w-4" />
              Tipo de Usuário
            </Label>
            <Select
              value={formData.tipo}
              onValueChange={(value) => handleInputChange('tipo', value)}
            >
              <SelectTrigger className={errors.tipo ? 'border-red-500' : ''}>
                <SelectValue placeholder="Selecione o tipo" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="admin">Administrador</SelectItem>
                <SelectItem value="promoter">Promoter</SelectItem>
                <SelectItem value="cliente">Cliente</SelectItem>
              </SelectContent>
            </Select>
            {errors.tipo && (
              <p className="text-sm text-red-500">{errors.tipo}</p>
            )}
          </div>


          {/* Erro geral */}
          {errors.submit && (
            <Alert>
              <AlertDescription className="text-red-600">
                {errors.submit}
              </AlertDescription>
            </Alert>
          )}

          {/* Botões */}
          <div className="flex gap-2 pt-4">
            <Button
              type="button"
              variant="outline"
              onClick={onClose}
              className="flex-1"
            >
              Cancelar
            </Button>
            <Button
              type="submit"
              disabled={loading}
              className="flex-1"
            >
              {loading ? 'Salvando...' : (usuario ? 'Atualizar' : 'Cadastrar')}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
};

export default CadastroUsuarioModal;
