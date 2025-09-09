import React, { createContext, useContext, useState, ReactNode } from 'react';

export interface Mesa {
  id: number;
  numero: string;
  nome?: string;
  capacidade?: number;
  status: 'livre' | 'ocupada' | 'reservada';
}

export interface Comanda {
  id: string;
  mesaId: number;
  numeroComanda: string;
  clienteNome?: string;
  dataAbertura: Date;
  status: 'ativa' | 'fechada' | 'cancelada';
  garcomId?: string;
  observacoes?: string;
}

export interface ComandaNFC {
  id: string;
  mesaId: number;
  numeroMesa: string;
  numeroComanda: string;
  clienteNome?: string;
  tagData: string;
}

interface MesaContextType {
  mesaAtual: Mesa | null;
  comandaAtual: Comanda | null;
  isLendoNFC: boolean;
  ultimaLeituraNFC: ComandaNFC | null;
  
  // Métodos para gerenciar mesa
  selecionarMesa: (mesa: Mesa) => void;
  limparMesa: () => void;
  
  // Métodos para gerenciar comanda
  criarComanda: (comanda: Omit<Comanda, 'id' | 'dataAbertura'>) => void;
  atualizarComanda: (comanda: Partial<Comanda>) => void;
  fecharComanda: () => void;
  
  // Métodos para NFC
  iniciarLeituraNFC: () => void;
  pararLeituraNFC: () => void;
  processarLeituraNFC: (nfcData: string) => Promise<boolean>;
  
  // Histórico
  historicoComandas: ComandaNFC[];
  adicionarAoHistorico: (comandaNFC: ComandaNFC) => void;
}

const MesaContext = createContext<MesaContextType | undefined>(undefined);

export function MesaProvider({ children }: { children: ReactNode }) {
  const [mesaAtual, setMesaAtual] = useState<Mesa | null>(null);
  const [comandaAtual, setComandaAtual] = useState<Comanda | null>(null);
  const [isLendoNFC, setIsLendoNFC] = useState(false);
  const [ultimaLeituraNFC, setUltimaLeituraNFC] = useState<ComandaNFC | null>(null);
  const [historicoComandas, setHistoricoComandas] = useState<ComandaNFC[]>([]);

  const selecionarMesa = (mesa: Mesa) => {
    setMesaAtual(mesa);
  };

  const limparMesa = () => {
    setMesaAtual(null);
    setComandaAtual(null);
    setUltimaLeituraNFC(null);
  };

  const criarComanda = (dadosComanda: Omit<Comanda, 'id' | 'dataAbertura'>) => {
    const novaComanda: Comanda = {
      ...dadosComanda,
      id: `cmd_${Date.now()}`,
      dataAbertura: new Date(),
    };
    setComandaAtual(novaComanda);
  };

  const atualizarComanda = (dadosAtualizacao: Partial<Comanda>) => {
    if (comandaAtual) {
      setComandaAtual({ ...comandaAtual, ...dadosAtualizacao });
    }
  };

  const fecharComanda = () => {
    if (comandaAtual) {
      setComandaAtual({ ...comandaAtual, status: 'fechada' });
    }
  };

  const iniciarLeituraNFC = () => {
    setIsLendoNFC(true);
  };

  const pararLeituraNFC = () => {
    setIsLendoNFC(false);
  };

  const processarLeituraNFC = async (nfcData: string): Promise<boolean> => {
    try {
      // Simular processamento dos dados NFC
      // Em um cenário real, aqui seria feita a validação e parsing dos dados
      const dados = JSON.parse(nfcData);
      
      if (dados.tipo === 'comanda' && dados.mesaId && dados.numeroComanda) {
        const comandaNFC: ComandaNFC = {
          id: `nfc_${Date.now()}`,
          mesaId: dados.mesaId,
          numeroMesa: dados.numeroMesa || `Mesa ${dados.mesaId}`,
          numeroComanda: dados.numeroComanda,
          clienteNome: dados.clienteNome,
          tagData: nfcData,
        };

        // Atualizar mesa atual
        const mesa: Mesa = {
          id: dados.mesaId,
          numero: dados.numeroMesa || `Mesa ${dados.mesaId}`,
          status: 'ocupada',
        };

        // Criar nova comanda
        const comanda: Omit<Comanda, 'id' | 'dataAbertura'> = {
          mesaId: dados.mesaId,
          numeroComanda: dados.numeroComanda,
          clienteNome: dados.clienteNome,
          status: 'ativa',
        };

        setMesaAtual(mesa);
        criarComanda(comanda);
        setUltimaLeituraNFC(comandaNFC);
        adicionarAoHistorico(comandaNFC);
        
        return true;
      }
      
      return false;
    } catch (error) {
      console.error('Erro ao processar dados NFC:', error);
      return false;
    } finally {
      setIsLendoNFC(false);
    }
  };

  const adicionarAoHistorico = (comandaNFC: ComandaNFC) => {
    setHistoricoComandas(prev => [comandaNFC, ...prev.slice(0, 9)]); // Manter apenas 10 últimas
  };

  return (
    <MesaContext.Provider
      value={{
        mesaAtual,
        comandaAtual,
        isLendoNFC,
        ultimaLeituraNFC,
        selecionarMesa,
        limparMesa,
        criarComanda,
        atualizarComanda,
        fecharComanda,
        iniciarLeituraNFC,
        pararLeituraNFC,
        processarLeituraNFC,
        historicoComandas,
        adicionarAoHistorico,
      }}
    >
      {children}
    </MesaContext.Provider>
  );
}

export function useMesa() {
  const context = useContext(MesaContext);
  if (context === undefined) {
    throw new Error('useMesa deve ser usado dentro de um MesaProvider');
  }
  return context;
}
