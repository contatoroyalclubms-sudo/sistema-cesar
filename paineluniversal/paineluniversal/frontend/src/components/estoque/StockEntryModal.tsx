import React, { useState } from 'react';

interface StockEntryModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess?: () => void;
}

export function StockEntryModal({ isOpen, onClose, onSuccess }: StockEntryModalProps) {
  const [formData, setFormData] = useState({
    reference: '',
    product: '',
    quantity: '',
    location: ''
  });

  console.log('📥 StockEntryModal renderizado com isOpen:', isOpen);

  if (!isOpen) return null;

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    console.log('📥 Formulário de entrada submetido:', formData);
    alert('Entrada registrada com sucesso! (Mock)');
    onSuccess?.();
    onClose();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
      <div className="bg-white p-6 rounded-lg shadow-xl max-w-md w-full mx-4">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-2xl font-bold">📥 Nova Entrada</h2>
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
              placeholder="Ex: ENT 001234"
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
          
          <div>
            <label className="block text-sm font-medium mb-1">Local</label>
            <select
              value={formData.location}
              onChange={(e) => setFormData({...formData, location: e.target.value})}
              className="w-full border rounded px-3 py-2"
              required
            >
              <option value="">Selecione o local</option>
              <option value="deposito">Depósito Principal</option>
              <option value="bar">Bar Principal</option>
              <option value="cozinha">Cozinha</option>
            </select>
          </div>
          
          <div className="bg-green-50 border border-green-200 p-3 rounded">
            <p className="text-sm text-green-800">
              ✅ A entrada será adicionada ao estoque atual do produto.
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
              className="px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600"
            >
              Registrar Entrada
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
