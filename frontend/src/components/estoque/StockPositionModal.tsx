import React, { useState, useEffect } from 'react';

interface StockPositionModalProps {
  isOpen: boolean;
  onClose: () => void;
  onRefresh?: () => void;
}

export function StockPositionModal({ isOpen, onClose, onRefresh }: StockPositionModalProps) {
  console.log('🧪 StockPositionModal renderizado com isOpen:', isOpen);

  if (!isOpen) {
    console.log('🧪 Modal não está aberto, não renderizando');
    return null;
  }

  console.log('🧪 Modal está aberto, renderizando');

  return (
    <div 
      className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50"
      onClick={(e) => {
        if (e.target === e.currentTarget) {
          console.log('🧪 Clique fora do modal, fechando');
          onClose();
        }
      }}
    >
      <div className="bg-white p-6 rounded-lg shadow-xl max-w-4xl w-full mx-4 max-h-[90vh] overflow-y-auto">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-2xl font-bold">📦 Posição de Estoque</h2>
          <button 
            onClick={() => {
              console.log('🧪 Botão fechar clicado');
              onClose();
            }}
            className="text-gray-500 hover:text-gray-700 text-2xl font-bold"
          >
            ×
          </button>
        </div>
        
        <div className="space-y-4">
          <p className="text-gray-600">
            Este modal está funcionando corretamente! 🎉
          </p>
          
          <div className="border rounded-lg p-4">
            <h3 className="font-semibold mb-2">Posições de Estoque (Mock)</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="border rounded p-3">
                <h4 className="font-medium">Produto A</h4>
                <p className="text-sm text-gray-600">Local: Depósito Principal</p>
                <p className="text-lg font-bold text-green-600">150 unidades</p>
              </div>
              <div className="border rounded p-3">
                <h4 className="font-medium">Produto B</h4>
                <p className="text-sm text-gray-600">Local: Bar Principal</p>
                <p className="text-lg font-bold text-yellow-600">5 unidades</p>
              </div>
              <div className="border rounded p-3">
                <h4 className="font-medium">Produto C</h4>
                <p className="text-sm text-gray-600">Local: Cozinha</p>
                <p className="text-lg font-bold text-red-600">0 unidades</p>
              </div>
            </div>
          </div>
          
          <div className="flex gap-2 justify-end">
            <button 
              onClick={() => {
                console.log('🧪 Botão refresh clicado');
                onRefresh?.();
              }}
              className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
            >
              🔄 Atualizar
            </button>
            <button 
              onClick={() => {
                console.log('🧪 Botão fechar footer clicado');
                onClose();
              }}
              className="px-4 py-2 bg-gray-500 text-white rounded hover:bg-gray-600"
            >
              Fechar
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
