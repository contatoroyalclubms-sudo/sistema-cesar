/**
 * Módulo de Comandas
 * 
 * Componente que implementa o sistema de cadastro de comandas
 * utilizando o CadastroModule genérico com configuração específica.
 */

import React from 'react';
import CadastroModule from '../common/CadastroModule';
import { comandasConfig } from '../../config/modules/comandasConfig';
import { comandasService } from '../../services/comandasService';

interface ComandasModuleProps {}

const ComandasModule: React.FC<ComandasModuleProps> = () => {
  return (
    <CadastroModule
      config={comandasConfig}
      title="Comandas"
      description="Gestão completa de comandas do sistema"
      apiService={comandasService}
    />
  );
};

export default ComandasModule;
