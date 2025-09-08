import React, { useState } from 'react';

interface TransferModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess?: () => void;
}

export function TransferModal({ isOpen, onClose, onSuccess }: TransferModalProps) {
  const [formData, setFormData] = useState({
    reference: '',
    product: '',
    quantity: '',
    fromLocation: '',
    toLocation: '',
    notes: ''
  });

  console.log('🔄 TransferModal renderizado com isOpen:', isOpen);

  if (!isOpen) return null;

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    console.log('🔄 Formulário de transferência submetido:', formData);
    alert('Transferência realizada com sucesso! (Mock)');
    onSuccess?.();
    onClose();
  };

  const locations = [
    { value: 'deposito', label: 'Depósito Principal' },
    { value: 'bar', label: 'Bar Principal' },
    { value: 'cozinha', label: 'Cozinha' },
    { value: 'bar-secundario', label: 'Bar Secundário' },
    { value: 'almoxarifado', label: 'Almoxarifado' }
  ];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
      <div className="bg-white p-6 rounded-lg shadow-xl max-w-md w-full mx-4">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-2xl font-bold">🔄 Nova Transferência</h2>
          <button 
            onClick={onClose}
            className="text-gray-500 hover:text-gray-700 text-2xl font-bold"
          >
            ×
          </button>
        </div>
        
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-1">Referência</label>
            <input
              type="text"
              value={formData.reference}
              onChange={(e) => setFormData({...formData, reference: e.target.value})}
              className="w-full border rounded px-3 py-2"
              placeholder="Ex: TRF 001234"
              required
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium mb-1">Produto</label>
            <input
              type="text"
              value={formData.product}
              onChange={(e) => setFormData({...formData, product: e.target.value})}
              className="w-full border rounded px-3 py-2"
              placeholder="Nome do produto"
              required
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium mb-1">Quantidade</label>
            <input
              type="number"
              value={formData.quantity}
              onChange={(e) => setFormData({...formData, quantity: e.target.value})}
              className="w-full border rounded px-3 py-2"
              placeholder="0"
              min="0"
              required
            />
          </div>
          
          <div className="grid grid-cols-2 gap-2">
            <div>
              <label className="block text-sm font-medium mb-1">De</label>
              <select
                value={formData.fromLocation}
                onChange={(e) => setFormData({...formData, fromLocation: e.target.value})}
                className="w-full border rounded px-3 py-2"
                required
              >
                <option value="">Origem</option>
                {locations.map(location => (
                  <option key={location.value} value={location.value}>
                    {location.label}
                  </option>
                ))}
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-medium mb-1">Para</label>
              <select
                value={formData.toLocation}
                onChange={(e) => setFormData({...formData, toLocation: e.target.value})}
                className="w-full border rounded px-3 py-2"
                required
              >
                <option value="">Destino</option>
                {locations.map(location => (
                  <option key={location.value} value={location.value}>
                    {location.label}
                  </option>
                ))}
              </select>
            </div>
          </div>
          
          <div>
            <label className="block text-sm font-medium mb-1">Observações</label>
            <textarea
              value={formData.notes}
              onChange={(e) => setFormData({...formData, notes: e.target.value})}
              className="w-full border rounded px-3 py-2"
              placeholder="Motivo da transferência..."
              rows={3}
            />
          </div>
          
          <div className="bg-blue-50 border border-blue-200 p-3 rounded">
            <p className="text-sm text-blue-800">
              📦 A transferência será registrada em ambos os locais automaticamente.
            </p>
          </div>
          
          <div className="flex gap-2 justify-end">
            <button 
              type="button"
              onClick={onClose}
              className="px-4 py-2 bg-gray-500 text-white rounded hover:bg-gray-600"
            >
              Cancelar
            </button>
            <button 
              type="submit"
              className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
            >
              Transferir
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
