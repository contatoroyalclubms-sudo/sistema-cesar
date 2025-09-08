import React from 'react';
import DiagnosticComponent from '../components/diagnostic/DiagnosticComponent';

const DiagnosticPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-background p-4">
      <div className="max-w-6xl mx-auto">
        <div className="mb-6">
          <h1 className="text-3xl font-bold">Diagnóstico do Sistema</h1>
          <p className="text-muted-foreground mt-2">
            Use esta página para identificar e corrigir problemas de conectividade
          </p>
        </div>
        
        <DiagnosticComponent 
          onComplete={(success) => {
            if (success) {
              console.log('✅ Sistema funcionando corretamente!');
            } else {
              console.log('⚠️ Problemas identificados no sistema');
            }
          }}
        />
      </div>
    </div>
  );
};

export default DiagnosticPage;
