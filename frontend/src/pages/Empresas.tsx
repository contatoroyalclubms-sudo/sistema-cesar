import React from 'react';
import CadastroModule from '../components/common/CadastroModule';
import empresasService from '../services/empresasService';

const Empresas: React.FC = () => {
  const empresaConfig = {
    itemName: 'Empresa',
    createButtonText: 'Nova Empresa',
    emptyMessage: 'Nenhuma empresa cadastrada',
    
    columns: [
      { key: 'razao_social', label: 'Razão Social' },
      { key: 'nome_fantasia', label: 'Nome Fantasia' },
      { key: 'cnpj', label: 'CNPJ' },
      { key: 'email', label: 'E-mail' },
      { key: 'telefone', label: 'Telefone' },
      { key: 'cidade', label: 'Cidade' },
      { key: 'ativa', label: 'Status', type: 'status' }
    ],
    
    searchConfig: {
      placeholder: 'Buscar por razão social, CNPJ ou email...',
      searchableFields: ['razao_social', 'nome_fantasia', 'cnpj', 'email']
    },
    
    filters: [
      {
        key: 'ativa',
        type: 'select',
        placeholder: 'Status',
        options: [
          { value: '', label: 'Todos' },
          { value: 'true', label: 'Ativo' },
          { value: 'false', label: 'Inativo' }
        ]
      }
    ],
    
    formFields: [
      // Dados Básicos
      {
        key: 'razao_social',
        label: 'Razão Social',
        type: 'text',
        required: true,
        placeholder: 'Digite a razão social da empresa'
      },
      {
        key: 'nome_fantasia',
        label: 'Nome Fantasia',
        type: 'text',
        placeholder: 'Digite o nome fantasia (opcional)'
      },
      {
        key: 'cnpj',
        label: 'CNPJ',
        type: 'text',
        required: true,
        placeholder: '00.000.000/0000-00'
      },
      {
        key: 'inscricao_estadual',
        label: 'Inscrição Estadual',
        type: 'text',
        placeholder: 'Digite a inscrição estadual'
      },
      {
        key: 'inscricao_municipal',
        label: 'Inscrição Municipal',
        type: 'text',
        placeholder: 'Digite a inscrição municipal'
      },
      
      // Contato
      {
        key: 'email',
        label: 'E-mail',
        type: 'email',
        required: true,
        placeholder: 'contato@empresa.com'
      },
      {
        key: 'telefone',
        label: 'Telefone Principal',
        type: 'text',
        required: true,
        placeholder: '(11) 99999-9999'
      },
      {
        key: 'telefone_secundario',
        label: 'Telefone Secundário',
        type: 'text',
        placeholder: '(11) 99999-9999'
      },
      {
        key: 'whatsapp',
        label: 'WhatsApp',
        type: 'text',
        placeholder: '(11) 99999-9999'
      },
      {
        key: 'site',
        label: 'Site',
        type: 'text',
        placeholder: 'https://www.empresa.com'
      },
      
      // Endereço
      {
        key: 'cep',
        label: 'CEP',
        type: 'text',
        placeholder: '00000-000'
      },
      {
        key: 'logradouro',
        label: 'Logradouro',
        type: 'text',
        placeholder: 'Rua, Avenida, etc.'
      },
      {
        key: 'numero',
        label: 'Número',
        type: 'text',
        placeholder: '123'
      },
      {
        key: 'complemento',
        label: 'Complemento',
        type: 'text',
        placeholder: 'Apto, Sala, etc.'
      },
      {
        key: 'bairro',
        label: 'Bairro',
        type: 'text',
        placeholder: 'Nome do bairro'
      },
      {
        key: 'cidade',
        label: 'Cidade',
        type: 'text',
        placeholder: 'Nome da cidade'
      },
      {
        key: 'estado',
        label: 'Estado',
        type: 'select',
        options: [
          { value: '', label: 'Selecione...' },
          { value: 'SP', label: 'São Paulo' },
          { value: 'RJ', label: 'Rio de Janeiro' },
          { value: 'MG', label: 'Minas Gerais' },
          { value: 'RS', label: 'Rio Grande do Sul' },
          { value: 'PR', label: 'Paraná' },
          { value: 'SC', label: 'Santa Catarina' },
          { value: 'BA', label: 'Bahia' },
          { value: 'GO', label: 'Goiás' },
          { value: 'ES', label: 'Espírito Santo' },
          { value: 'PE', label: 'Pernambuco' },
          { value: 'CE', label: 'Ceará' },
          { value: 'DF', label: 'Distrito Federal' }
        ]
      },
      
      // Dados Bancários
      {
        key: 'banco',
        label: 'Banco',
        type: 'text',
        placeholder: 'Nome do banco'
      },
      {
        key: 'agencia',
        label: 'Agência',
        type: 'text',
        placeholder: '0000'
      },
      {
        key: 'conta',
        label: 'Conta',
        type: 'text',
        placeholder: '00000-0'
      },
      {
        key: 'tipo_conta',
        label: 'Tipo de Conta',
        type: 'select',
        options: [
          { value: '', label: 'Selecione...' },
          { value: 'corrente', label: 'Conta Corrente' },
          { value: 'poupanca', label: 'Conta Poupança' },
          { value: 'salario', label: 'Conta Salário' }
        ]
      },
      
      // Responsável
      {
        key: 'responsavel_nome',
        label: 'Nome do Responsável',
        type: 'text',
        placeholder: 'Nome completo'
      },
      {
        key: 'responsavel_cargo',
        label: 'Cargo do Responsável',
        type: 'text',
        placeholder: 'Diretor, Gerente, etc.'
      },
      {
        key: 'responsavel_email',
        label: 'E-mail do Responsável',
        type: 'email',
        placeholder: 'responsavel@empresa.com'
      },
      {
        key: 'responsavel_telefone',
        label: 'Telefone do Responsável',
        type: 'text',
        placeholder: '(11) 99999-9999'
      },
      
      // Observações
      {
        key: 'observacoes',
        label: 'Observações',
        type: 'textarea',
        placeholder: 'Informações adicionais sobre a empresa'
      },
      {
        key: 'ativa',
        label: 'Status',
        type: 'select',
        defaultValue: true,
        options: [
          { value: true, label: 'Ativo' },
          { value: false, label: 'Inativo' }
        ]
      }
    ],
    
    ui: {
      itemsPerPage: 25
    },
    
    showExportImport: true
  };

  return (
    <CadastroModule
      config={empresaConfig}
      title="Gerenciamento de Empresas"
      description="Cadastro e gestão completa de empresas do sistema"
      apiService={empresasService}
    />
  );
};

export default Empresas;
