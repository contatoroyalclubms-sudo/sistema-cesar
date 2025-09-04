import React, { useState } from 'react';
import { Card } from '../ui/card';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Label } from '../ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/select';
import { Plus, Trash2, Calculator, Check } from 'lucide-react';

interface RegraSplit {
  id: string;
  destinatario: string;
  tipo: 'percentual' | 'fixo';
  valor: number;
}

interface SplitCalculado {
  destinatario: string;
  valor: number;
  tipo: string;
}

export default function SplitPagamentos() {
  const [valorTotal, setValorTotal] = useState<number>(0);
  const [regras, setRegras] = useState<RegraSplit[]>([]);
  const [splitCalculado, setSplitCalculado] = useState<SplitCalculado[]>([]);
  const [novaRegra, setNovaRegra] = useState<Omit<RegraSplit, 'id'>>({
    destinatario: '',
    tipo: 'percentual',
    valor: 0
  });

  const adicionarRegra = () => {
    if (!novaRegra.destinatario || novaRegra.valor <= 0) {
      alert('Preencha o destinatário e valor da regra');
      return;
    }

    const novaRegraCompleta: RegraSplit = {
      ...novaRegra,
      id: Date.now().toString()
    };

    setRegras([...regras, novaRegraCompleta]);
    setNovaRegra({
      destinatario: '',
      tipo: 'percentual',
      valor: 0
    });
  };

  const removerRegra = (id: string) => {
    setRegras(regras.filter(regra => regra.id !== id));
  };

  const calcularSplit = () => {
    if (valorTotal <= 0) {
      alert('Informe um valor total válido');
      return;
    }

    const splits: SplitCalculado[] = [];
    let totalUtilizado = 0;

    for (const regra of regras) {
      let valorSplit = 0;

      if (regra.tipo === 'percentual') {
        valorSplit = valorTotal * (regra.valor / 100);
      } else {
        valorSplit = regra.valor;
      }

      splits.push({
        destinatario: regra.destinatario,
        valor: valorSplit,
        tipo: regra.tipo
      });

      totalUtilizado += valorSplit;
    }

    setSplitCalculado(splits);

    // Verificar se a soma está correta
    if (Math.abs(totalUtilizado - valorTotal) > 0.01) {
      alert(`Atenção: Total do split (R$ ${totalUtilizado.toFixed(2)}) difere do valor total (R$ ${valorTotal.toFixed(2)})`);
    }
  };

  const salvarConfiguracao = async () => {
    if (regras.length === 0) {
      alert('Adicione pelo menos uma regra de split');
      return;
    }

    try {
      // Simular chamada para API - implementar endpoint real
      const response = await fetch('/api/split/configuracoes/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          valor_total: valorTotal,
          regras: regras
        })
      });

      if (response.ok) {
        alert('Configuração de split salva com sucesso!');
      } else {
        throw new Error('Erro na resposta da API');
      }
    } catch (error) {
      console.error('Erro ao salvar:', error);
      alert('Erro ao salvar configuração - Funcionalidade em desenvolvimento');
    }
  };

  const totalPercentual = regras
    .filter(r => r.tipo === 'percentual')
    .reduce((sum, r) => sum + r.valor, 0);

  const totalFixo = regras
    .filter(r => r.tipo === 'fixo')
    .reduce((sum, r) => sum + r.valor, 0);

  return (
    <div className="space-y-6">
      {/* Configuração do Valor Total */}
      <Card className="p-6">
        <h2 className="text-xl font-semibold mb-4">Valor Total da Transação</h2>
        <div className="flex items-center space-x-4">
          <div className="flex-1">
            <Label htmlFor="valor-total">Valor Total (R$)</Label>
            <Input
              id="valor-total"
              type="number"
              step="0.01"
              value={valorTotal}
              onChange={(e) => setValorTotal(Number(e.target.value))}
              placeholder={novaRegra.tipo === 'percentual' ? '0.00' : '0.00'}
              className="text-lg"
            />
          </div>
          <Button onClick={calcularSplit} disabled={valorTotal <= 0 || regras.length === 0}>
            <Calculator className="h-4 w-4 mr-2" />
            Calcular Split
          </Button>
        </div>
      </Card>

      {/* Adicionar Nova Regra */}
      <Card className="p-6">
        <h2 className="text-xl font-semibold mb-4">Adicionar Regra de Split</h2>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div>
            <Label htmlFor="destinatario">Destinatário</Label>
            <Input
              id="destinatario"
              value={novaRegra.destinatario}
              onChange={(e) => setNovaRegra({...novaRegra, destinatario: e.target.value})}
              placeholder="Nome do destinatário"
            />
          </div>
          <div>
            <Label htmlFor="tipo">Tipo</Label>
            <Select 
              value={novaRegra.tipo} 
              onValueChange={(value: 'percentual' | 'fixo') => setNovaRegra({...novaRegra, tipo: value})}
            >
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="percentual">Percentual (%)</SelectItem>
                <SelectItem value="fixo">Valor Fixo (R$)</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div>
            <Label htmlFor="valor">
              {novaRegra.tipo === 'percentual' ? 'Percentual (%)' : 'Valor (R$)'}
            </Label>
            <Input
              id="valor"
              type="number"
              step="0.01"
              value={novaRegra.valor}
              onChange={(e) => setNovaRegra({...novaRegra, valor: Number(e.target.value)})}
              placeholder={novaRegra.tipo === 'percentual' ? '0.00' : '0.00'}
            />
          </div>
          <div className="flex items-end">
            <Button onClick={adicionarRegra} className="w-full">
              <Plus className="h-4 w-4 mr-2" />
              Adicionar
            </Button>
          </div>
        </div>
      </Card>

      {/* Lista de Regras */}
      {regras.length > 0 && (
        <Card className="p-6">
          <h2 className="text-xl font-semibold mb-4">Regras Configuradas</h2>
          <div className="space-y-3">
            {regras.map((regra) => (
              <div key={regra.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div>
                  <span className="font-medium">{regra.destinatario}</span>
                  <span className="text-gray-500 ml-2">
                    {regra.tipo === 'percentual' ? `${regra.valor}%` : `R$ ${regra.valor.toFixed(2)}`}
                  </span>
                </div>
                <Button 
                  variant="destructive" 
                  size="sm"
                  onClick={() => removerRegra(regra.id)}
                >
                  <Trash2 className="h-4 w-4" />
                </Button>
              </div>
            ))}
          </div>
          
          {/* Resumo */}
          <div className="mt-4 p-3 bg-blue-50 rounded-lg">
            <div className="text-sm text-gray-600">
              <div>Total Percentual: {totalPercentual}%</div>
              <div>Total Fixo: R$ {totalFixo.toFixed(2)}</div>
              {totalPercentual > 100 && (
                <div className="text-red-600 font-medium">
                  ⚠️ Atenção: Total percentual excede 100%
                </div>
              )}
            </div>
          </div>
        </Card>
      )}

      {/* Resultado do Split */}
      {splitCalculado.length > 0 && (
        <Card className="p-6">
          <h2 className="text-xl font-semibold mb-4">Resultado do Split</h2>
          <div className="space-y-3">
            {splitCalculado.map((split, index) => (
              <div key={`split-${split.destinatario}-${index}`} className="flex items-center justify-between p-3 bg-green-50 rounded-lg">
                <div>
                  <span className="font-medium">{split.destinatario}</span>
                  <span className="text-gray-500 ml-2 text-sm">
                    ({split.tipo})
                  </span>
                </div>
                <div className="text-lg font-bold text-green-700">
                  R$ {split.valor.toFixed(2)}
                </div>
              </div>
            ))}
          </div>
          
          <div className="mt-4 pt-4 border-t border-gray-200">
            <div className="flex justify-between items-center">
              <span className="text-lg font-semibold">Total:</span>
              <span className="text-xl font-bold">
                R$ {splitCalculado.reduce((sum, split) => sum + split.valor, 0).toFixed(2)}
              </span>
            </div>
          </div>

          <div className="mt-4">
            <Button onClick={salvarConfiguracao} className="w-full">
              <Check className="h-4 w-4 mr-2" />
              Salvar Configuração
            </Button>
          </div>
        </Card>
      )}
    </div>
  );
}
