import React, { useState } from 'react';

interface MovementHistoryModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export function MovementHistoryModal({ isOpen, onClose }: MovementHistoryModalProps) {
  const [filters, setFilters] = useState({
    startDate: '',
    endDate: '',
    product: '',
    type: '',
    location: ''
  });

  console.log('📋 MovementHistoryModal renderizado com isOpen:', isOpen);

  if (!isOpen) return null;

  // Mock data para demonstração
  const mockMovements = [
    {
      id: '1',
      date: '2024-01-15',
      reference: 'ENT001',
      product: 'Cerveja Heineken 350ml',
      type: 'entrada',
      quantity: 50,
      location: 'Depósito Principal',
      user: 'João Silva'
    },
    {
      id: '2',
      date: '2024-01-14',
      reference: 'SAI002',
      product: 'Vodka Absolut 1L',
      type: 'saida',
      quantity: -10,
      location: 'Bar Principal',
      user: 'Maria Santos'
    },
    {
      id: '3',
      date: '2024-01-13',
      reference: 'TRF003',
      product: 'Whisky Jack Daniels',
      type: 'transferencia',
      quantity: 5,
      location: 'Cozinha → Bar',
      user: 'Pedro Costa'
    }
  ];

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

  const handleExport = () => {
    console.log('📊 Exportando histórico com filtros:', filters);
    alert('Histórico exportado! (Mock)');
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
      <div className="bg-white p-6 rounded-lg shadow-xl max-w-4xl w-full mx-4 max-h-[90vh] overflow-y-auto">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-2xl font-bold">📋 Histórico de Movimentações</h2>
          <button 
            onClick={onClose}
            className="text-gray-500 hover:text-gray-700 text-2xl font-bold"
          >
            ×
          </button>
        </div>
        
        {/* Filtros */}
        <div className="bg-gray-50 p-4 rounded-lg mb-4">
          <h3 className="font-semibold mb-3">🔍 Filtros</h3>
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-3">
            <div>
              <label className="block text-xs font-medium mb-1">Data Início</label>
              <input
                type="date"
                value={filters.startDate}
                onChange={(e) => setFilters({...filters, startDate: e.target.value})}
                className="w-full border rounded px-2 py-1 text-sm"
              />
            </div>
            <div>
              <label className="block text-xs font-medium mb-1">Data Fim</label>
              <input
                type="date"
                value={filters.endDate}
                onChange={(e) => setFilters({...filters, endDate: e.target.value})}
                className="w-full border rounded px-2 py-1 text-sm"
              />
            </div>
            <div>
              <label className="block text-xs font-medium mb-1">Produto</label>
              <input
                type="text"
                value={filters.product}
                onChange={(e) => setFilters({...filters, product: e.target.value})}
                className="w-full border rounded px-2 py-1 text-sm"
                placeholder="Nome do produto"
              />
            </div>
            <div>
              <label className="block text-xs font-medium mb-1">Tipo</label>
              <select
                value={filters.type}
                onChange={(e) => setFilters({...filters, type: e.target.value})}
                className="w-full border rounded px-2 py-1 text-sm"
              >
                <option value="">Todos</option>
                <option value="entrada">Entrada</option>
                <option value="saida">Saída</option>
                <option value="transferencia">Transferência</option>
              </select>
            </div>
            <div>
              <label className="block text-xs font-medium mb-1">Local</label>
              <select
                value={filters.location}
                onChange={(e) => setFilters({...filters, location: e.target.value})}
                className="w-full border rounded px-2 py-1 text-sm"
              >
                <option value="">Todos</option>
                <option value="deposito">Depósito</option>
                <option value="bar">Bar</option>
                <option value="cozinha">Cozinha</option>
              </select>
            </div>
          </div>
        </div>

        {/* Tabela de movimentações */}
        <div className="overflow-x-auto">
          <table className="w-full border-collapse border border-gray-300">
            <thead>
              <tr className="bg-gray-100">
                <th className="border border-gray-300 px-3 py-2 text-left">Data</th>
                <th className="border border-gray-300 px-3 py-2 text-left">Referência</th>
                <th className="border border-gray-300 px-3 py-2 text-left">Produto</th>
                <th className="border border-gray-300 px-3 py-2 text-left">Tipo</th>
                <th className="border border-gray-300 px-3 py-2 text-right">Quantidade</th>
                <th className="border border-gray-300 px-3 py-2 text-left">Local</th>
                <th className="border border-gray-300 px-3 py-2 text-left">Usuário</th>
              </tr>
            </thead>
            <tbody>
              {mockMovements.map((movement) => (
                <tr key={movement.id} className="hover:bg-gray-50">
                  <td className="border border-gray-300 px-3 py-2 text-sm">
                    {new Date(movement.date).toLocaleDateString('pt-BR')}
                  </td>
                  <td className="border border-gray-300 px-3 py-2 text-sm font-mono">
                    {movement.reference}
                  </td>
                  <td className="border border-gray-300 px-3 py-2 text-sm">
                    {movement.product}
                  </td>
                  <td className="border border-gray-300 px-3 py-2">
                    <span className={`inline-flex items-center px-2 py-1 rounded text-xs font-medium ${getTypeColor(movement.type)}`}>
                      {getTypeIcon(movement.type)} {movement.type}
                    </span>
                  </td>
                  <td className={`border border-gray-300 px-3 py-2 text-sm text-right font-medium ${
                    movement.quantity > 0 ? 'text-green-600' : 'text-red-600'
                  }`}>
                    {movement.quantity > 0 ? '+' : ''}{movement.quantity}
                  </td>
                  <td className="border border-gray-300 px-3 py-2 text-sm">
                    {movement.location}
                  </td>
                  <td className="border border-gray-300 px-3 py-2 text-sm">
                    {movement.user}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <div className="bg-blue-50 border border-blue-200 p-3 rounded mt-4">
          <p className="text-sm text-blue-800">
            📊 Exibindo {mockMovements.length} movimentações. Use os filtros para refinar a busca.
          </p>
        </div>
        
        <div className="flex gap-2 justify-end mt-4">
          <button 
            onClick={handleExport}
            className="px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600"
          >
            📊 Exportar
          </button>
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
