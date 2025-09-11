import React from 'react';
import CadastroModule from '../common/CadastroModule';
import { clientesConfig } from '../../config/modules/clientesConfig';

export default function ClientesModule() {
  return (
    <CadastroModule 
      config={clientesConfig}
      title="Gestão de Clientes"
      description="Gerenciar clientes do sistema"
    />
  );
}
