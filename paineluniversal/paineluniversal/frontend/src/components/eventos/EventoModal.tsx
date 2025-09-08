import React, { useState, useEffect } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '../ui/dialog';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Label } from '../ui/label';
import { Textarea } from '../ui/textarea';
import { Alert, AlertDescription } from '../ui/alert';
import { Evento, EventoCreate } from '../../services/api';
import { useAuth } from '../../contexts/AuthContext';

interface EventoModalProps {
  evento?: Evento | null;
  isOpen: boolean;
  onClose: () => void;
  onSave: (evento: EventoCreate) => void;
}

const EventoModal: React.FC<EventoModalProps> = ({
  evento,
  isOpen,
  onClose,
  onSave
}) => {
  const { usuario, token, isAuthenticated } = useAuth();
  
  const [formData, setFormData] = useState<EventoCreate>({
    nome: '',
    descricao: '',
    data_evento: '',
    local: '',
    endereco: '',
    limite_idade: 18,
    capacidade_maxima: 100
  });
  
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);

  useEffect(() => {
    if (evento) {
      const dataEvento = new Date(evento.data_evento);
      const dataFormatada = new Date(dataEvento.getTime() - (dataEvento.getTimezoneOffset() * 60000))
        .toISOString()
        .slice(0, 16);
      
      setFormData({
        nome: evento.nome,
        descricao: evento.descricao || '',
        data_evento: dataFormatada,
        local: evento.local,
        endereco: evento.endereco || '',
        limite_idade: evento.limite_idade || 18,
        capacidade_maxima: evento.capacidade_maxima || 100
        // empresa_id removido - não é mais obrigatório
      });
    } else {
      // Para novo evento, usar uma data padrão (1 hora no futuro)
      const agora = new Date();
      agora.setHours(agora.getHours() + 1);
      const dataDefault = agora.toISOString().slice(0, 16);
      
      setFormData({
        nome: '',
        descricao: '',
        data_evento: dataDefault,
        local: '',
        endereco: '',
        limite_idade: 18,
        capacidade_maxima: 100
      });
    }
    setErrors({});
    setSubmitError(null);
  }, [evento, isOpen]);

  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (!formData.nome.trim()) {
      newErrors.nome = 'Nome é obrigatório';
    }

    console.log('🔍 Validando data do evento:', {
      data_evento: formData.data_evento,
      isEmpty: !formData.data_evento,
      isTrimmedEmpty: !formData.data_evento?.trim()
    });

    if (!formData.data_evento || !formData.data_evento.trim()) {
      newErrors.data_evento = 'Data do evento é obrigatória';
    } else {
      const dataEvento = new Date(formData.data_evento);
      const agora = new Date();
      
      if (isNaN(dataEvento.getTime())) {
        newErrors.data_evento = 'Data inválida. Verifique se preencheu corretamente dia, mês, ano, hora e minutos.';
      } else if (dataEvento <= agora) {
        newErrors.data_evento = 'Data do evento deve ser futura';
      }
    }

    if (!formData.local.trim()) {
      newErrors.local = 'Local é obrigatório';
    }

    if (formData.limite_idade < 0 || formData.limite_idade > 100) {
      newErrors.limite_idade = 'Limite de idade deve estar entre 0 e 100 anos';
    }

    if (formData.capacidade_maxima !== undefined && formData.capacidade_maxima <= 0) {
      newErrors.capacidade_maxima = 'Capacidade máxima deve ser maior que zero';
    }

    console.log('📝 Erros de validação encontrados:', newErrors);
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    console.log('🚀 Iniciando submissão do formulário');
    console.log('📝 FormData antes da validação:', formData);
    
    // Verificar autenticação usando contexto
    console.log('🔐 Status autenticação:', {
      isAuthenticated,
      hasToken: !!token,
      hasUsuario: !!usuario,
      usuarioTipo: usuario?.tipo
    });
    
    if (!isAuthenticated || !token) {
      setSubmitError('Você precisa estar logado para criar eventos');
      return;
    }
    
    // Verificar permissão do usuário
    if (usuario?.tipo && !['admin', 'promoter'].includes(usuario.tipo)) {
      setSubmitError('Apenas admins e promoters podem criar eventos');
      return;
    }
    
    // Garantir que temos uma data válida antes da validação
    if (!formData.data_evento) {
      const agora = new Date();
      agora.setHours(agora.getHours() + 1);
      const dataDefault = agora.toISOString().slice(0, 16);
      setFormData(prev => ({ ...prev, data_evento: dataDefault }));
      console.log('📅 Data padrão definida:', dataDefault);
      return; // Vai submeter novamente com a data preenchida
    }
    
    if (!validateForm()) {
      console.log('❌ Validação falhou');
      return;
    }

    setLoading(true);
    setSubmitError(null);
    
    try {
      const dataEvento = new Date(formData.data_evento);
      
      console.log('🔄 Convertendo data:', {
        original: formData.data_evento,
        parsed: dataEvento,
        iso: dataEvento.toISOString(),
        isValid: !isNaN(dataEvento.getTime())
      });
      
      if (isNaN(dataEvento.getTime())) {
        throw new Error('Data inválida');
      }
      
      // Preparar dados limpos para envio - garantir formato datetime correto
      const eventoData: any = {
        nome: formData.nome.trim(),
        descricao: formData.descricao?.trim() || undefined,
        data_evento: dataEvento.toISOString(),
        local: formData.local.trim(),
        endereco: formData.endereco?.trim() || undefined,
        limite_idade: Number(formData.limite_idade) || 18,
        capacidade_maxima: formData.capacidade_maxima && formData.capacidade_maxima > 0 ? Number(formData.capacidade_maxima) : undefined
      };

      // Remover campos undefined para enviar payload limpo
      Object.keys(eventoData).forEach(key => {
        if (eventoData[key] === undefined) {
          delete eventoData[key];
        }
      });
      
      console.log('📤 Dados finais sendo enviados:', eventoData);
      
      // Log da requisição que será enviada
      console.log('🌐 Fazendo requisição para:', 'https://backend-painel-universal-production.up.railway.app/api/eventos/');
      console.log('🔑 Token sendo usado:', token ? `${token.substring(0, 20)}...` : 'NENHUM');
      
      await onSave(eventoData);
      console.log('✅ Evento salvo com sucesso!');
      
    } catch (error: any) {
      console.error('❌ Erro ao salvar evento:', error);
      console.error('📊 Detalhes do erro:', {
        status: error.response?.status,
        statusText: error.response?.statusText,
        data: error.response?.data,
        message: error.message
      });
      
      let errorMessage = 'Erro ao salvar evento';
      
      if (error.response?.data?.detail) {
        errorMessage = error.response.data.detail;
      } else if (error.message) {
        errorMessage = error.message;
      }
      
      setSubmitError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (field: string, value: any) => {
    console.log(`🔄 Campo alterado: ${field} = ${value}`);
    setFormData(prev => ({ ...prev, [field]: value }));
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: '' }));
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>
            {evento ? 'Editar Evento' : 'Novo Evento'}
          </DialogTitle>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-4">
          {!isAuthenticated && (
            <Alert variant="destructive">
              <AlertDescription>Você precisa estar logado para criar eventos</AlertDescription>
            </Alert>
          )}
          
          {submitError && (
            <Alert variant="destructive">
              <AlertDescription>{submitError}</AlertDescription>
            </Alert>
          )}

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <Label htmlFor="nome">Nome do Evento *</Label>
              <Input
                id="nome"
                value={formData.nome}
                onChange={(e) => handleInputChange('nome', e.target.value)}
                className={errors.nome ? 'border-red-500' : ''}
                placeholder="Digite o nome do evento"
              />
              {errors.nome && (
                <p className="text-sm text-red-500 mt-1">{errors.nome}</p>
              )}
            </div>

            <div>
              <Label htmlFor="data_evento">Data e Hora *</Label>
              <Input
                id="data_evento"
                type="datetime-local"
                value={formData.data_evento}
                min={new Date().toISOString().slice(0, 16)}
                onChange={(e) => handleInputChange('data_evento', e.target.value)}
                className={errors.data_evento ? 'border-red-500' : ''}
              />
              {errors.data_evento && (
                <p className="text-sm text-red-500 mt-1">{errors.data_evento}</p>
              )}
            </div>

            <div>
              <Label htmlFor="local">Local *</Label>
              <Input
                id="local"
                value={formData.local}
                onChange={(e) => handleInputChange('local', e.target.value)}
                className={errors.local ? 'border-red-500' : ''}
                placeholder="Local do evento"
              />
              {errors.local && (
                <p className="text-sm text-red-500 mt-1">{errors.local}</p>
              )}
            </div>

            <div>
              <Label htmlFor="endereco">Endereço</Label>
              <Input
                id="endereco"
                value={formData.endereco}
                onChange={(e) => handleInputChange('endereco', e.target.value)}
                placeholder="Endereço completo (opcional)"
              />
            </div>

            <div>
              <Label htmlFor="limite_idade">Limite de Idade</Label>
              <Input
                id="limite_idade"
                type="number"
                min="0"
                max="100"
                value={formData.limite_idade}
                onChange={(e) => handleInputChange('limite_idade', parseInt(e.target.value) || 0)}
                className={errors.limite_idade ? 'border-red-500' : ''}
              />
              {errors.limite_idade && (
                <p className="text-sm text-red-500 mt-1">{errors.limite_idade}</p>
              )}
            </div>

            <div>
              <Label htmlFor="capacidade_maxima">Capacidade Máxima</Label>
              <Input
                id="capacidade_maxima"
                type="number"
                min="1"
                value={formData.capacidade_maxima}
                onChange={(e) => handleInputChange('capacidade_maxima', parseInt(e.target.value) || 1)}
                className={errors.capacidade_maxima ? 'border-red-500' : ''}
              />
              {errors.capacidade_maxima && (
                <p className="text-sm text-red-500 mt-1">{errors.capacidade_maxima}</p>
              )}
            </div>
          </div>

          <div>
            <Label htmlFor="descricao">Descrição</Label>
            <Textarea
              id="descricao"
              value={formData.descricao}
              onChange={(e) => handleInputChange('descricao', e.target.value)}
              placeholder="Descrição do evento (opcional)"
              rows={3}
            />
          </div>

          <div className="flex justify-end space-x-2 pt-4">
            <Button
              type="button"
              variant="outline"
              onClick={onClose}
              disabled={loading}
            >
              Cancelar
            </Button>
            <Button
              type="submit"
              disabled={loading || !isAuthenticated}
            >
              {loading ? 'Salvando...' : (evento ? 'Atualizar' : 'Criar')}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
};

export default EventoModal;
