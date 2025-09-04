import React, { createContext, useContext, useState, useEffect } from 'react';

interface Evento {
  id: number;
  nome: string;
  empresa_id?: number;
}

interface EventoContextType {
  eventoAtual: Evento | null;
  setEventoAtual: (evento: Evento | null) => void;
  eventoId: number | null;
}

const EventoContext = createContext<EventoContextType | undefined>(undefined);

export const useEvento = () => {
  const context = useContext(EventoContext);
  if (context === undefined) {
    throw new Error('useEvento deve ser usado dentro de um EventoProvider');
  }
  return context;
};

interface EventoProviderProps {
  children: React.ReactNode;
}

export const EventoProvider: React.FC<EventoProviderProps> = ({ children }) => {
  const [eventoAtual, setEventoAtualState] = useState<Evento | null>(null);

  // Carregar evento do localStorage na inicialização
  useEffect(() => {
    const eventoSalvo = localStorage.getItem('evento_atual');
    if (eventoSalvo) {
      try {
        const evento = JSON.parse(eventoSalvo);
        setEventoAtualState(evento);
      } catch (error) {
        console.error('Erro ao carregar evento do localStorage:', error);
        localStorage.removeItem('evento_atual');
      }
    }
  }, []);

  const setEventoAtual = (evento: Evento | null) => {
    setEventoAtualState(evento);
    if (evento) {
      localStorage.setItem('evento_atual', JSON.stringify(evento));
      localStorage.setItem('evento_id', evento.id.toString());
    } else {
      localStorage.removeItem('evento_atual');
      localStorage.removeItem('evento_id');
    }
  };

  const eventoId = eventoAtual?.id || null;

  const value: EventoContextType = {
    eventoAtual,
    setEventoAtual,
    eventoId
  };

  return (
    <EventoContext.Provider value={value}>
      {children}
    </EventoContext.Provider>
  );
};

export default EventoContext;
