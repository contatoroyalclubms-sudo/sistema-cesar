import React from 'react';
import SplitPagamentos from '../../components/split/SplitPagamentos';

export default function SplitPagamentosPage() {
  return (
    <div className="container mx-auto px-4 py-6">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900">Split de Pagamentos</h1>
        <p className="text-gray-600 mt-2">
          Configure e calcule a divisão automática de pagamentos entre destinatários
        </p>
      </div>
      
      <SplitPagamentos />
    </div>
  );
}
