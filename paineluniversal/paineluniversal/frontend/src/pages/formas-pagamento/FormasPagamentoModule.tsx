import React from 'react';
import CadastroModule from '../../components/common/CadastroModule';
import { formasPagamentoConfig } from '../../config/modules/formasPagamentoConfig';

/**
 * Componente do módulo de Formas de Pagamento
 * 
 * Este componente utiliza o CadastroModule genérico configurado especificamente
 * para gerenciamento de formas de pagamento do sistema.
 */
function FormasPagamentoModule() {
  return (
    <CadastroModule
      config={formasPagamentoConfig}
      title="Formas de Pagamento"
      description="Gestão completa das formas de pagamento aceitas no sistema"
    />
  );
}

export default FormasPagamentoModule;
