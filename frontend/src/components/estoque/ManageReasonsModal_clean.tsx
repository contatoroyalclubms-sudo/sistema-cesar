import React, { useState } from 'react';

interface ManageReasonsModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess?: () => void;
}

interface Reason {
  id: string;
  name: string;
  type: 'entrada' | 'saida' | 'transferencia';
  description: string;
  active: boolean;
}

export function ManageReasonsModal({ isOpen, onClose, onSuccess }: ManageReasonsModalProps) {
  const [selectedReason, setSelectedReason] = useState<Reason | null>(null);
  const [isEditing, setIsEditing] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    type: 'entrada' as 'entrada' | 'saida' | 'transferencia',
    description: '',
    active: true
  });

  console.log('⚙️ ManageReasonsModal renderizado com isOpen:', isOpen);

  if (!isOpen) return null;

  // Mock data para demonstração
  const mockReasons: Reason[] = [
    { 
      id: '1', 
      name: 'Compra de mercadoria', 
      type: 'entrada', 
      description: 'Entrada de produtos através de compra', 
      active: true 
    },
    { 
      id: '2', 
      name: 'Venda no balcão', 
      type: 'saida', 
      description: 'Saída de produtos por venda direta', 
      active: true 
    },
    { 
      id: '3', 
      name: 'Transferência entre setores', 
      type: 'transferencia', 
      description: 'Movimentação interna entre locais', 
      active: true 
    },
    { 
      id: '4', 
      name: 'Perda por vencimento', 
      type: 'saida', 
      description: 'Baixa por produto vencido', 
      active: false 
    }
  ];

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    console.log('⚙️ Salvando motivo:', formData);
    alert(isEditing ? 'Motivo atualizado com sucesso! (Mock)' : 'Motivo criado com sucesso! (Mock)');
    setIsEditing(false);
    setSelectedReason(null);
    setFormData({ name: '', type: 'entrada', description: '', active: true });
    onSuccess?.();
  };

  const handleEdit = (reason: Reason) => {
    setSelectedReason(reason);
    setFormData({
      name: reason.name,
      type: reason.type,
      description: reason.description,
      active: reason.active
    });
    setIsEditing(true);
  };

  const handleDelete = (reason: Reason) => {
    if (confirm(`Deseja realmente excluir o motivo "${reason.name}"?`)) {
      console.log('🗑️ Excluindo motivo:', reason);
      alert('Motivo excluído com sucesso! (Mock)');
    }
  };

  const getTypeColor = (type: string) => {
    switch (type) {
      case 'entrada': return 'text-green-600 bg-green-100';
      case 'saida': return 'text-red-600 bg-red-100';
      case 'transferencia': return 'text-blue-600 bg-blue-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'entrada': return '📥';
      case 'saida': return '📤';
      case 'transferencia': return '🔄';
      default: return '📦';
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
      <div className="bg-white p-6 rounded-lg shadow-xl max-w-4xl w-full mx-4 max-h-[90vh] overflow-y-auto">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-2xl font-bold">⚙️ Gerenciar Motivos</h2>
          <button 
            onClick={onClose}
            className="text-gray-500 hover:text-gray-700 text-2xl font-bold"
          >
            ×
          </button>
        </div>
        
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Lista de motivos */}
          <div>
            <h3 className="text-lg font-semibold mb-3">📋 Motivos Cadastrados</h3>
            <div className="space-y-3 max-h-96 overflow-y-auto">
              {mockReasons.map((reason) => (
                <div 
                  key={reason.id} 
                  className={`border rounded-lg p-4 ${!reason.active ? 'bg-gray-50 opacity-60' : ''}`}
                >
                  <div className="flex justify-between items-start mb-2">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <h4 className="font-semibold">{reason.name}</h4>
                        <span className={`inline-flex items-center px-2 py-1 rounded text-xs font-medium ${getTypeColor(reason.type)}`}>
                          {getTypeIcon(reason.type)} {reason.type}
                        </span>
                        {!reason.active && (
                          <span className="text-xs text-gray-500 bg-gray-200 px-2 py-1 rounded">
                            Inativo
                          </span>
                        )}
                      </div>
                      <p className="text-sm text-gray-600">{reason.description}</p>
                    </div>
                    <div className="flex gap-1 ml-2">
                      <button
                        onClick={() => handleEdit(reason)}
                        className="text-blue-600 hover:text-blue-800 text-sm px-2 py-1 rounded border border-blue-300 hover:bg-blue-50"
                      >
                        ✏️ Editar
                      </button>
                      <button
                        onClick={() => handleDelete(reason)}
                        className="text-red-600 hover:text-red-800 text-sm px-2 py-1 rounded border border-red-300 hover:bg-red-50"
                      >
                        🗑️ Excluir
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Formulário */}
          <div>
            <h3 className="text-lg font-semibold mb-3">
              {isEditing ? '✏️ Editar Motivo' : '➕ Novo Motivo'}
            </h3>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-1">Nome do Motivo</label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData({...formData, name: e.target.value})}
                  className="w-full border rounded px-3 py-2"
                  placeholder="Ex: Compra de mercadoria"
                  required
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium mb-1">Tipo de Movimentação</label>
                <select
                  value={formData.type}
                  onChange={(e) => setFormData({...formData, type: e.target.value as any})}
                  className="w-full border rounded px-3 py-2"
                  required
                >
                  <option value="entrada">📥 Entrada</option>
                  <option value="saida">📤 Saída</option>
                  <option value="transferencia">🔄 Transferência</option>
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium mb-1">Descrição</label>
                <textarea
                  value={formData.description}
                  onChange={(e) => setFormData({...formData, description: e.target.value})}
                  className="w-full border rounded px-3 py-2"
                  placeholder="Descrição detalhada do motivo..."
                  rows={3}
                  required
                />
              </div>
              
              <div className="flex items-center gap-2">
                <input
                  type="checkbox"
                  id="active"
                  checked={formData.active}
                  onChange={(e) => setFormData({...formData, active: e.target.checked})}
                  className="rounded"
                />
                <label htmlFor="active" className="text-sm font-medium">
                  Motivo ativo
                </label>
              </div>
              
              <div className="bg-yellow-50 border border-yellow-200 p-3 rounded">
                <p className="text-sm text-yellow-800">
                  💡 Motivos inativos não aparecerão nos formulários de movimentação.
                </p>
              </div>
              
              <div className="flex gap-2">
                <button 
                  type="submit"
                  className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
                >
                  {isEditing ? 'Atualizar' : 'Criar'} Motivo
                </button>
                {isEditing && (
                  <button 
                    type="button"
                    onClick={() => {
                      setIsEditing(false);
                      setSelectedReason(null);
                      setFormData({ name: '', type: 'entrada', description: '', active: true });
                    }}
                    className="px-4 py-2 bg-gray-500 text-white rounded hover:bg-gray-600"
                  >
                    Cancelar
                  </button>
                )}
              </div>
            </form>
          </div>
        </div>
        
        <div className="flex justify-end mt-6">
          <button 
            onClick={onClose}
            className="px-4 py-2 bg-gray-500 text-white rounded hover:bg-gray-600"
          >
            Fechar
          </button>
        </div>
      </div>
    </div>
  );
}
