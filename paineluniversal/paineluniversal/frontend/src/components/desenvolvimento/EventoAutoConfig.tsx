import React, { useEffect } from 'react';
import { useEvento } from '../../contexts/EventoContext';

/**
 * Componente para auto-configurar evento para desenvolvimento/testes
 * Remove a necessidade de seleção manual de evento durante desenvolvimento
 */
const EventoAutoConfig: React.FC = () => {
  const { eventoAtual, setEventoAtual } = useEvento();

  useEffect(() => {
    // Se não há evento selecionado, configurar automaticamente
    if (!eventoAtual) {
      // Configurar evento padrão para desenvolvimento
      const eventoTeste = {
        id: 1,
        nome: 'Evento Teste',
        empresa_id: 1
      };
      
      console.log('🔧 Configurando evento automaticamente para desenvolvimento:', eventoTeste);
      setEventoAtual(eventoTeste);
    }
  }, [eventoAtual, setEventoAtual]);

  return null; // Componente invisible, apenas para configuração
};

export default EventoAutoConfig;
