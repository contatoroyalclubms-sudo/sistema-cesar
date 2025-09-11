import React, { useState, useEffect, useRef } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '../ui/dialog';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Label } from '../ui/label';
import { Textarea } from '../ui/textarea';
import { Alert, AlertDescription } from '../ui/alert';
import { Evento, EventoCreate } from '../../services/api';
import { useAuth } from '../../contexts/AuthContext';
import { Upload, X, Image as ImageIcon, Calendar, Clock, Ticket } from 'lucide-react';

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
  const fileInputRef = useRef<HTMLInputElement>(null);
  
  const [formData, setFormData] = useState<EventoCreate>({
    nome: '',
    descricao: '',
    // Período do evento
    data_inicio_evento: '',
    data_fim_evento: '',
    // Período de vendas
    data_inicio_vendas: '',
    data_fim_vendas: '',
    // Campos tradicionais
    local: '',
    endereco: '',
    limite_idade: 18,
    capacidade_maxima: '',
    // Manter compatibilidade
    data_evento: ''
  });
  
  const [imageFile, setImageFile] = useState<File | null>(null);
  const [imagePreview, setImagePreview] = useState<string | null>(null);
  const [uploadProgress, setUploadProgress] = useState<number>(0);
  
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);

  useEffect(() => {
    if (evento) {
      // Se há dados do evento existente, mapear para novo formato
      const agora = new Date();
      const inicioEvento = evento.data_inicio_evento 
        ? new Date(evento.data_inicio_evento)
        : evento.data_evento 
          ? new Date(evento.data_evento)
          : new Date(agora.getTime() + 60 * 60 * 1000); // 1 hora no futuro
      
      const fimEvento = evento.data_fim_evento 
        ? new Date(evento.data_fim_evento)
        : new Date(inicioEvento.getTime() + 2 * 60 * 60 * 1000); // 2 horas após início
      
      const inicioVendas = evento.data_inicio_vendas 
        ? new Date(evento.data_inicio_vendas)
        : new Date(agora.getTime() + 30 * 60 * 1000); // 30 minutos no futuro
      
      const fimVendas = evento.data_fim_vendas 
        ? new Date(evento.data_fim_vendas)
        : new Date(inicioEvento.getTime() - 5 * 60 * 1000); // 5 minutos antes do evento
      
      setFormData({
        nome: evento.nome,
        descricao: evento.descricao || '',
        // Período do evento
        data_inicio_evento: new Date(inicioEvento.getTime() - (inicioEvento.getTimezoneOffset() * 60000))
          .toISOString().slice(0, 16),
        data_fim_evento: new Date(fimEvento.getTime() - (fimEvento.getTimezoneOffset() * 60000))
          .toISOString().slice(0, 16),
        // Período de vendas
        data_inicio_vendas: new Date(inicioVendas.getTime() - (inicioVendas.getTimezoneOffset() * 60000))
          .toISOString().slice(0, 16),
        data_fim_vendas: new Date(fimVendas.getTime() - (fimVendas.getTimezoneOffset() * 60000))
          .toISOString().slice(0, 16),
        // Campos existentes
        local: evento.local,
        endereco: evento.endereco || '',
        limite_idade: evento.limite_idade || 18,
        capacidade_maxima: evento.capacidade_maxima || 100,
        // Manter compatibilidade
        data_evento: evento.data_evento || inicioEvento.toISOString().slice(0, 16)
      });
    } else {
      // Para novo evento, definir horários padrão
      const agora = new Date();
      const inicioVendas = new Date(agora.getTime() + 30 * 60 * 1000); // 30 min no futuro
      const inicioEvento = new Date(agora.getTime() + 90 * 60 * 1000); // 1h30 no futuro
      const fimVendas = new Date(inicioEvento.getTime() - 10 * 60 * 1000); // 10 min antes do evento
      const fimEvento = new Date(inicioEvento.getTime() + 2 * 60 * 60 * 1000); // 2 horas depois
      
      setFormData({
        nome: '',
        descricao: '',
        // Período do evento
        data_inicio_evento: inicioEvento.toISOString().slice(0, 16),
        data_fim_evento: fimEvento.toISOString().slice(0, 16),
        // Período de vendas
        data_inicio_vendas: inicioVendas.toISOString().slice(0, 16),
        data_fim_vendas: fimVendas.toISOString().slice(0, 16),
        // Campos existentes
        local: '',
        endereco: '',
        limite_idade: 18,
        capacidade_maxima: '',
        // Manter compatibilidade
        data_evento: inicioEvento.toISOString().slice(0, 16)
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

    // Validar período do evento
    if (!formData.data_inicio_evento || !formData.data_inicio_evento.trim()) {
      newErrors.data_inicio_evento = 'Data de início do evento é obrigatória';
    }

    if (!formData.data_fim_evento || !formData.data_fim_evento.trim()) {
      newErrors.data_fim_evento = 'Data de fim do evento é obrigatória';
    }

    // Validar período de vendas
    if (!formData.data_inicio_vendas || !formData.data_inicio_vendas.trim()) {
      newErrors.data_inicio_vendas = 'Data de início das vendas é obrigatória';
    }

    if (!formData.data_fim_vendas || !formData.data_fim_vendas.trim()) {
      newErrors.data_fim_vendas = 'Data de fim das vendas é obrigatória';
    }

    // Validar datas se todas estão preenchidas
    if (formData.data_inicio_evento && formData.data_fim_evento && 
        formData.data_inicio_vendas && formData.data_fim_vendas) {
      
      const inicioEvento = new Date(formData.data_inicio_evento);
      const fimEvento = new Date(formData.data_fim_evento);
      const inicioVendas = new Date(formData.data_inicio_vendas);
      const fimVendas = new Date(formData.data_fim_vendas);
      const agora = new Date();

      // Validar se as datas são válidas
      if (isNaN(inicioEvento.getTime())) {
        newErrors.data_inicio_evento = 'Data de início do evento inválida';
      }
      if (isNaN(fimEvento.getTime())) {
        newErrors.data_fim_evento = 'Data de fim do evento inválida';
      }
      if (isNaN(inicioVendas.getTime())) {
        newErrors.data_inicio_vendas = 'Data de início das vendas inválida';
      }
      if (isNaN(fimVendas.getTime())) {
        newErrors.data_fim_vendas = 'Data de fim das vendas inválida';
      }

      // Validar regras de negócio
      if (!Object.keys(newErrors).length) {
        // Vendas devem começar no futuro (pode ser 1 minuto antes)
        if (inicioVendas <= new Date(agora.getTime() - 60000)) {
          newErrors.data_inicio_vendas = 'Vendas devem começar no futuro';
        }

        // Vendas devem terminar antes do evento
        if (fimVendas >= inicioEvento) {
          newErrors.data_fim_vendas = 'Vendas devem terminar antes do início do evento';
        }

        // Início das vendas deve ser antes do fim
        if (inicioVendas >= fimVendas) {
          newErrors.data_inicio_vendas = 'Início das vendas deve ser antes do fim';
        }

        // Início do evento deve ser antes do fim
        if (inicioEvento >= fimEvento) {
          newErrors.data_inicio_evento = 'Início do evento deve ser antes do fim';
        }

        // Evento deve começar no futuro (pode ser 1 minuto antes)
        if (inicioEvento <= new Date(agora.getTime() - 60000)) {
          newErrors.data_inicio_evento = 'Evento deve começar no futuro';
        }
      }
    }

    if (!formData.local.trim()) {
      newErrors.local = 'Local é obrigatório';
    }

    if (formData.limite_idade < 0 || formData.limite_idade > 100) {
      newErrors.limite_idade = 'Limite de idade deve estar entre 0 e 100 anos';
    }

    // Validar capacidade máxima apenas se foi preenchida
    if (formData.capacidade_maxima !== '' && 
        formData.capacidade_maxima !== null && 
        formData.capacidade_maxima !== undefined) {
      const capacidade = Number(formData.capacidade_maxima);
      if (isNaN(capacidade) || capacidade <= 0) {
        newErrors.capacidade_maxima = 'Capacidade máxima deve ser um número maior que zero';
      }
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
    
    // Garantir que temos datas válidas antes da validação
    if (!formData.data_inicio_evento || !formData.data_fim_evento || 
        !formData.data_inicio_vendas || !formData.data_fim_vendas) {
      const agora = new Date();
      const inicioVendas = new Date(agora.getTime() + 30 * 60 * 1000); // 30 min no futuro
      const inicioEvento = new Date(agora.getTime() + 90 * 60 * 1000); // 1h30 no futuro
      const fimVendas = new Date(inicioEvento.getTime() - 10 * 60 * 1000); // 10 min antes do evento
      const fimEvento = new Date(inicioEvento.getTime() + 2 * 60 * 60 * 1000); // 2 horas depois
      
      setFormData(prev => ({ 
        ...prev, 
        data_inicio_evento: formData.data_inicio_evento || inicioEvento.toISOString().slice(0, 16),
        data_fim_evento: formData.data_fim_evento || fimEvento.toISOString().slice(0, 16),
        data_inicio_vendas: formData.data_inicio_vendas || inicioVendas.toISOString().slice(0, 16),
        data_fim_vendas: formData.data_fim_vendas || fimVendas.toISOString().slice(0, 16),
        data_evento: formData.data_evento || inicioEvento.toISOString().slice(0, 16)
      }));
      console.log('📅 Datas padrão definidas');
      return; // Vai submeter novamente com as datas preenchidas
    }
    
    if (!validateForm()) {
      console.log('❌ Validação falhou');
      return;
    }

    setLoading(true);
    setSubmitError(null);
    
    try {
      const inicioEvento = new Date(formData.data_inicio_evento);
      const fimEvento = new Date(formData.data_fim_evento);
      const inicioVendas = new Date(formData.data_inicio_vendas);
      const fimVendas = new Date(formData.data_fim_vendas);
      
      console.log('🔄 Convertendo datas:', {
        inicio_evento: { original: formData.data_inicio_evento, parsed: inicioEvento },
        fim_evento: { original: formData.data_fim_evento, parsed: fimEvento },
        inicio_vendas: { original: formData.data_inicio_vendas, parsed: inicioVendas },
        fim_vendas: { original: formData.data_fim_vendas, parsed: fimVendas }
      });
      
      if (isNaN(inicioEvento.getTime()) || isNaN(fimEvento.getTime()) || 
          isNaN(inicioVendas.getTime()) || isNaN(fimVendas.getTime())) {
        throw new Error('Uma ou mais datas são inválidas');
      }
      
      // Preparar dados com novos campos do período de vendas
      const eventoData: EventoCreate = {
        nome: formData.nome.trim(),
        descricao: formData.descricao?.trim() || undefined,
        // Período do evento
        data_inicio_evento: inicioEvento.toISOString(),
        data_fim_evento: fimEvento.toISOString(),
        // Período de vendas
        data_inicio_vendas: inicioVendas.toISOString(),
        data_fim_vendas: fimVendas.toISOString(),
        // Campos existentes
        local: formData.local.trim(),
        endereco: formData.endereco?.trim() || undefined,
        limite_idade: Number(formData.limite_idade) || 18,
        capacidade_maxima: formData.capacidade_maxima && formData.capacidade_maxima !== '' ? Number(formData.capacidade_maxima) : undefined,
        // Manter compatibilidade com sistema antigo
        data_evento: inicioEvento.toISOString()
      };

      // Remover campos undefined para enviar payload limpo
      Object.keys(eventoData).forEach(key => {
        if ((eventoData as any)[key] === undefined) {
          delete (eventoData as any)[key];
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

  const handleInputChange = (field: string, value: string | number) => {
    console.log(`🔄 Campo alterado: ${field} = ${value}`);
    setFormData((prev: EventoCreate) => ({ ...prev, [field]: value }));
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: '' }));
    }
  };

  const handleImageSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      // Validar tipo de arquivo
      if (!file.type.startsWith('image/')) {
        alert('Por favor, selecione apenas arquivos de imagem.');
        return;
      }
      
      // Validar tamanho (max 5MB)
      if (file.size > 5 * 1024 * 1024) {
        alert('A imagem deve ter no máximo 5MB.');
        return;
      }
      
      setImageFile(file);
      
      // Criar preview
      const reader = new FileReader();
      reader.onload = (e) => {
        setImagePreview(e.target?.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  const removeImage = () => {
    setImageFile(null);
    setImagePreview(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
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

          {/* Seção de Upload de Imagem - Estilo MEEP */}
          <div className="bg-gradient-to-r from-secondary to-accent p-6 rounded-lg border border-border">
            <div className="flex items-center gap-2 mb-4">
              <ImageIcon className="h-5 w-5 text-purple-600" />
              <Label className="text-lg font-semibold text-purple-900">Imagem do Evento</Label>
            </div>
            
            <div className="space-y-4">
              {!imagePreview ? (
                <div 
                  className="border-2 border-dashed border-primary/30 rounded-lg p-8 text-center cursor-pointer hover:border-primary/50 hover:bg-primary/5 transition-colors"
                  onClick={() => fileInputRef.current?.click()}
                >
                  <Upload className="mx-auto h-12 w-12 text-purple-400 mb-3" />
                  <p className="text-purple-700 font-medium">Clique para selecionar uma imagem</p>
                  <p className="text-purple-500 text-sm mt-1">PNG, JPG até 5MB</p>
                </div>
              ) : (
                <div className="relative">
                  <img 
                    src={imagePreview} 
                    alt="Preview do evento" 
                    className="w-full h-48 object-cover rounded-lg shadow-md"
                  />
                  <button
                    type="button"
                    onClick={removeImage}
                    className="absolute top-2 right-2 bg-red-500 hover:bg-red-600 text-white p-1 rounded-full shadow-lg transition-colors"
                  >
                    <X className="h-4 w-4" />
                  </button>
                </div>
              )}
              
              <input
                ref={fileInputRef}
                type="file"
                accept="image/*"
                onChange={handleImageSelect}
                className="hidden"
              />
              
              {uploadProgress > 0 && uploadProgress < 100 && (
                <div className="w-full bg-primary/20 rounded-full h-2">
                  <div 
                    className="bg-primary h-2 rounded-full transition-all duration-300" 
                    style={{ width: `${uploadProgress}%` }}
                  ></div>
                </div>
              )}
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="md:col-span-2">
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
                value={formData.capacidade_maxima || ''}
                onChange={(e) => {
                  const value = e.target.value;
                  if (value === '') {
                    handleInputChange('capacidade_maxima', '');
                  } else {
                    const numValue = parseInt(value);
                    if (!isNaN(numValue) && numValue > 0) {
                      handleInputChange('capacidade_maxima', numValue);
                    }
                  }
                }}
                className={errors.capacidade_maxima ? 'border-red-500' : ''}
                placeholder="Digite a capacidade máxima"
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

          {/* Seção do Período do Evento */}
          <div className="bg-gray-50 p-6 rounded-lg border">
            <div className="flex items-center gap-2 mb-4">
              <Calendar className="h-5 w-5 text-gray-600" />
              <h3 className="font-semibold text-lg text-gray-900">Período do Evento</h3>
            </div>
            <p className="text-sm text-gray-600 mb-4">Defina quando o evento irá acontecer</p>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <Label htmlFor="data_inicio_evento">Início do Evento *</Label>
                <Input
                  id="data_inicio_evento"
                  type="datetime-local"
                  value={formData.data_inicio_evento}
                  min={new Date().toISOString().slice(0, 16)}
                  onChange={(e) => handleInputChange('data_inicio_evento', e.target.value)}
                  className={errors.data_inicio_evento ? 'border-red-500' : ''}
                />
                {errors.data_inicio_evento && (
                  <p className="text-sm text-red-500 mt-1">{errors.data_inicio_evento}</p>
                )}
              </div>

              <div>
                <Label htmlFor="data_fim_evento">Fim do Evento *</Label>
                <Input
                  id="data_fim_evento"
                  type="datetime-local"
                  value={formData.data_fim_evento}
                  min={formData.data_inicio_evento || new Date().toISOString().slice(0, 16)}
                  onChange={(e) => handleInputChange('data_fim_evento', e.target.value)}
                  className={errors.data_fim_evento ? 'border-red-500' : ''}
                />
                {errors.data_fim_evento && (
                  <p className="text-sm text-red-500 mt-1">{errors.data_fim_evento}</p>
                )}
              </div>
            </div>
          </div>

          {/* Seção do Período de Vendas */}
          <div className="bg-gradient-to-r from-green-50 to-emerald-50 p-6 rounded-lg border border-green-200">
            <div className="flex items-center gap-2 mb-4">
              <Ticket className="h-5 w-5 text-green-600" />
              <h3 className="font-semibold text-lg text-green-900">Período de Vendas</h3>
            </div>
            <p className="text-sm text-green-700 mb-4">Configure quando as vendas dos ingressos estarão disponíveis</p>
            <div className="bg-amber-50 border border-amber-200 rounded-md p-3 mb-4">
              <p className="text-sm text-amber-800">⚠️ <strong>Importante:</strong> As vendas devem terminar antes do início do evento</p>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <Label htmlFor="data_inicio_vendas">Início das Vendas *</Label>
                <Input
                  id="data_inicio_vendas"
                  type="datetime-local"
                  value={formData.data_inicio_vendas}
                  min={new Date().toISOString().slice(0, 16)}
                  onChange={(e) => handleInputChange('data_inicio_vendas', e.target.value)}
                  className={errors.data_inicio_vendas ? 'border-red-500' : ''}
                />
                {errors.data_inicio_vendas && (
                  <p className="text-sm text-red-500 mt-1">{errors.data_inicio_vendas}</p>
                )}
              </div>

              <div>
                <Label htmlFor="data_fim_vendas">Fim das Vendas *</Label>
                <Input
                  id="data_fim_vendas"
                  type="datetime-local"
                  value={formData.data_fim_vendas}
                  max={formData.data_inicio_evento}
                  onChange={(e) => handleInputChange('data_fim_vendas', e.target.value)}
                  className={errors.data_fim_vendas ? 'border-red-500' : ''}
                />
                {errors.data_fim_vendas && (
                  <p className="text-sm text-red-500 mt-1">{errors.data_fim_vendas}</p>
                )}
                <p className="text-xs text-green-600 mt-1">As vendas devem terminar antes do início do evento</p>
              </div>
            </div>
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
