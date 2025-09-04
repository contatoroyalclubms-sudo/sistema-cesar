import React from 'react';
import DashboardBI from '../../components/bi/DashboardBI';

export default function BiDashboardPage() {
  return (
    <div className="container mx-auto px-4 py-6">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900">Business Intelligence</h1>
        <p className="text-gray-600 mt-2">
          Análise de dados em tempo real do seu negócio
        </p>
      </div>
      
      <DashboardBI />
    </div>
  );
}
