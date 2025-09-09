import React, { createContext, useContext, useState, ReactNode } from 'react';

export interface Produto {
  id: number;
  nome: string;
  preco: number;
  categoria: string;
}

export interface ItemCarrinho extends Produto {
  quantidade: number;
}

interface CarrinhoContextType {
  itens: ItemCarrinho[];
  adicionarItem: (produto: Produto) => void;
  removerItem: (produtoId: number) => void;
  aumentarQuantidade: (produtoId: number) => void;
  diminuirQuantidade: (produtoId: number) => void;
  limparCarrinho: () => void;
  getTotalItens: () => number;
  getTotalValor: () => number;
}

const CarrinhoContext = createContext<CarrinhoContextType | undefined>(undefined);

export function CarrinhoProvider({ children }: { children: ReactNode }) {
  const [itens, setItens] = useState<ItemCarrinho[]>([]);

  const adicionarItem = (produto: Produto) => {
    setItens(prevItens => {
      const itemExistente = prevItens.find(item => item.id === produto.id);
      
      if (itemExistente) {
        return prevItens.map(item =>
          item.id === produto.id
            ? { ...item, quantidade: item.quantidade + 1 }
            : item
        );
      } else {
        return [...prevItens, { ...produto, quantidade: 1 }];
      }
    });
  };

  const removerItem = (produtoId: number) => {
    setItens(prevItens => prevItens.filter(item => item.id !== produtoId));
  };

  const aumentarQuantidade = (produtoId: number) => {
    setItens(prevItens =>
      prevItens.map(item =>
        item.id === produtoId
          ? { ...item, quantidade: item.quantidade + 1 }
          : item
      )
    );
  };

  const diminuirQuantidade = (produtoId: number) => {
    setItens(prevItens =>
      prevItens.map(item =>
        item.id === produtoId && item.quantidade > 1
          ? { ...item, quantidade: item.quantidade - 1 }
          : item
      ).filter(item => item.quantidade > 0)
    );
  };

  const limparCarrinho = () => {
    setItens([]);
  };

  const getTotalItens = () => {
    return itens.reduce((total, item) => total + item.quantidade, 0);
  };

  const getTotalValor = () => {
    return itens.reduce((total, item) => total + (item.preco * item.quantidade), 0);
  };

  return (
    <CarrinhoContext.Provider
      value={{
        itens,
        adicionarItem,
        removerItem,
        aumentarQuantidade,
        diminuirQuantidade,
        limparCarrinho,
        getTotalItens,
        getTotalValor,
      }}
    >
      {children}
    </CarrinhoContext.Provider>
  );
}

export function useCarrinho() {
  const context = useContext(CarrinhoContext);
  if (context === undefined) {
    throw new Error('useCarrinho deve ser usado dentro de um CarrinhoProvider');
  }
  return context;
}
