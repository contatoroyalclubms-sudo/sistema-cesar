/**
 * Componente de Cadastro de Formas de Pagamento
 * 
 * Este componente utiliza o CadastroModule genérico para gerenciar
 * o cadastro de formas de pagamento do sistema.
 */

import React from 'react';
import CadastroModule from '../common/CadastroModule';
import { formasPagamentoService } from '../../services/formasPagamentoService';

// Configuração inline para evitar problemas de build
const formasPagamentoConfig = {
  title: 'Formas de Pagamento',
  description: 'Gestão completa de formas de pagamento',
  icon: 'CreditCard',
  entityName: 'forma de pagamento',
  entityNamePlural: 'formas de pagamento',
  
  api: {
    basePath: '/api/formas-pagamento'
  },

  fields: [
    {
      name: 'id',
      label: 'ID',
      type: 'hidden',
      visible: false
    },
    {
      name: 'codigo',
      label: 'Código',
      type: 'number',
      required: true,
      placeholder: 'Ex: 001',
      validation: {
        required: 'Código é obrigatório',
        min: { value: 1, message: 'Código deve ser maior que 0' }
      },
      grid: { xs: 12, sm: 6, md: 3 }
    },
    {
      name: 'descricao',
      label: 'Descrição',
      type: 'text',
      required: true,
      placeholder: 'Ex: Cartão de Crédito Visa',
      validation: {
        required: 'Descrição é obrigatória',
        minLength: { value: 2, message: 'Descrição deve ter pelo menos 2 caracteres' },
        maxLength: { value: 100, message: 'Descrição deve ter no máximo 100 caracteres' }
      },
      grid: { xs: 12, sm: 6, md: 6 }
    },
    {
      name: 'tipo_pagamento',
      label: 'Tipo de Pagamento',
      type: 'select',
      required: true,
      options: [
        { value: 'Dinheiro', label: 'Dinheiro' },
        { value: 'Cartão de Crédito', label: 'Cartão de Crédito' },
        { value: 'Cartão de Débito', label: 'Cartão de Débito' },
        { value: 'PIX', label: 'PIX' },
        { value: 'Transferência Bancária', label: 'Transferência Bancária' },
        { value: 'Boleto', label: 'Boleto Bancário' },
        { value: 'Cheque', label: 'Cheque' },
        { value: 'Vale Refeição', label: 'Vale Refeição' },
        { value: 'Vale Alimentação', label: 'Vale Alimentação' },
        { value: 'Cashless', label: 'Cashless/Pulseira' },
        { value: 'Financiamento', label: 'Financiamento' },
        { value: 'Crediário', label: 'Crediário' },
        { value: 'Outro', label: 'Outro' }
      ],
      validation: { required: 'Tipo de pagamento é obrigatório' },
      grid: { xs: 12, sm: 6, md: 3 }
    },
    {
      name: 'taxa_percentual',
      label: 'Taxa Percentual (%)',
      type: 'number',
      step: '0.01',
      min: '0',
      max: '100',
      placeholder: 'Ex: 3.5',
      validation: {
        min: { value: 0, message: 'Taxa percentual deve ser maior ou igual a 0' },
        max: { value: 100, message: 'Taxa percentual deve ser menor ou igual a 100' }
      },
      grid: { xs: 12, sm: 6, md: 3 }
    },
    {
      name: 'taxa_fixa',
      label: 'Taxa Fixa (R$)',
      type: 'number',
      step: '0.01',
      min: '0',
      placeholder: 'Ex: 2.50',
      validation: {
        min: { value: 0, message: 'Taxa fixa deve ser maior ou igual a 0' }
      },
      grid: { xs: 12, sm: 6, md: 3 }
    },
    {
      name: 'aceita_parcelamento',
      label: 'Aceita Parcelamento',
      type: 'switch',
      defaultValue: false,
      grid: { xs: 12, sm: 6, md: 3 }
    },
    {
      name: 'max_parcelas',
      label: 'Máximo de Parcelas',
      type: 'number',
      min: '1',
      max: '48',
      defaultValue: 1,
      placeholder: 'Ex: 12',
      validation: {
        min: { value: 1, message: 'Deve ter pelo menos 1 parcela' },
        max: { value: 48, message: 'Máximo de 48 parcelas' }
      },
      conditional: { field: 'aceita_parcelamento', value: true },
      grid: { xs: 12, sm: 6, md: 3 }
    },
    {
      name: 'ativo',
      label: 'Ativo',
      type: 'switch',
      defaultValue: true,
      grid: { xs: 12, sm: 6, md: 3 }
    },
    {
      name: 'observacoes',
      label: 'Observações',
      type: 'textarea',
      placeholder: 'Observações adicionais sobre esta forma de pagamento...',
      rows: 3,
      validation: {
        maxLength: { value: 500, message: 'Observações deve ter no máximo 500 caracteres' }
      },
      grid: { xs: 12, sm: 12, md: 12 }
    }
  ],

  table: {
    columns: [
      { key: 'codigo', label: 'Código', sortable: true, width: '80px' },
      { key: 'descricao', label: 'Descrição', sortable: true, searchable: true },
      { key: 'tipo_pagamento', label: 'Tipo', sortable: true, searchable: true, width: '150px' },
      { key: 'taxa_percentual', label: 'Taxa %', sortable: true, align: 'right', width: '100px' },
      { key: 'taxa_fixa', label: 'Taxa Fixa', sortable: true, align: 'right', width: '100px' },
      { key: 'aceita_parcelamento', label: 'Parcelamento', sortable: true, align: 'center', width: '120px' },
      { key: 'status', label: 'Status', sortable: true, align: 'center', width: '100px' },
      { key: 'actions', label: 'Ações', sortable: false, align: 'center', width: '120px' }
    ],
    
    formatters: {
      tipo_pagamento: {
        render: (value) => {
          const colors = {
            'Dinheiro': 'text-green-600',
            'Cartão de Crédito': 'text-blue-600',
            'Cartão de Débito': 'text-purple-600',
            'PIX': 'text-orange-600',
            'Transferência Bancária': 'text-indigo-600',
            'Boleto': 'text-yellow-600',
            'Cheque': 'text-gray-600',
            'Vale Refeição': 'text-pink-600',
            'Vale Alimentação': 'text-green-500',
            'Cashless': 'text-purple-600',
            'Financiamento': 'text-red-600',
            'Crediário': 'text-blue-500',
            'Outro': 'text-gray-500'
          };
          return `<span class="${colors[value] || 'text-gray-600'}">${value}</span>`;
        }
      },
      taxa_percentual: {
        render: (value) => value ? `${value}%` : '0%'
      },
      taxa_fixa: {
        render: (value) => value ? `R$ ${parseFloat(value).toFixed(2)}` : 'R$ 0,00'
      },
      aceita_parcelamento: {
        render: (value) => value ? 
          '<span class="text-green-600">✓ Sim</span>' : 
          '<span class="text-red-600">✗ Não</span>'
      },
      status: {
        render: (value, row) => {
          const isActive = row.ativo !== undefined ? row.ativo : true;
          return isActive ? 
            '<span class="text-green-600 font-medium">Ativo</span>' : 
            '<span class="text-red-600 font-medium">Inativo</span>';
        }
      }
    }
  },

  search: {
    placeholder: 'Buscar por código, descrição ou tipo...',
    fields: ['codigo', 'descricao', 'tipo_pagamento']
  },

  filters: [
    {
      name: 'tipo_pagamento',
      label: 'Tipo de Pagamento',
      type: 'select',
      options: [
        { value: '', label: 'Todos os tipos' },
        { value: 'Dinheiro', label: 'Dinheiro' },
        { value: 'Cartão de Crédito', label: 'Cartão de Crédito' },
        { value: 'Cartão de Débito', label: 'Cartão de Débito' },
        { value: 'PIX', label: 'PIX' },
        { value: 'Transferência Bancária', label: 'Transferência Bancária' },
        { value: 'Boleto', label: 'Boleto Bancário' },
        { value: 'Cashless', label: 'Cashless/Pulseira' }
      ]
    },
    {
      name: 'aceita_parcelamento',
      label: 'Parcelamento',
      type: 'select',
      options: [
        { value: '', label: 'Todos' },
        { value: 'true', label: 'Aceita Parcelamento' },
        { value: 'false', label: 'Não Aceita Parcelamento' }
      ]
    },
    {
      name: 'ativo',
      label: 'Status',
      type: 'select',
      options: [
        { value: '', label: 'Todos' },
        { value: 'true', label: 'Ativo' },
        { value: 'false', label: 'Inativo' }
      ]
    }
  ],

  validation: {
    uniqueFields: ['codigo', 'descricao'],
    businessRules: [
      {
        field: 'max_parcelas',
        condition: (formData) => formData.aceita_parcelamento && !formData.max_parcelas,
        message: 'Número máximo de parcelas é obrigatório quando aceita parcelamento'
      }
    ]
  },

  permissions: {
    view: ['admin', 'promoter'],
    create: ['admin', 'promoter'],
    edit: ['admin', 'promoter'],
    delete: ['admin']
  },

  messages: {
    create: {
      success: 'Forma de pagamento criada com sucesso!',
      error: 'Erro ao criar forma de pagamento'
    },
    update: {
      success: 'Forma de pagamento atualizada com sucesso!',
      error: 'Erro ao atualizar forma de pagamento'
    },
    delete: {
      success: 'Forma de pagamento excluída com sucesso!',
      error: 'Erro ao excluir forma de pagamento',
      confirm: 'Tem certeza que deseja excluir esta forma de pagamento?'
    }
  }
};

const CadastroFormasPagamento = () => {
  return (
    <CadastroModule
      config={formasPagamentoConfig}
      apiService={formasPagamentoService}
    />
  );
};

export default CadastroFormasPagamento;
