import React, { useState } from 'react';
import { Button } from '../ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { UserPlus, Users } from 'lucide-react';
import CadastroUsuarioModal from './CadastroUsuarioModal';

interface Usuario {
  id?: number;
  cpf: string;
  nome: string;
  email: string;
  telefone: string;
  tipo: 'admin' | 'promoter' | 'cliente';
  empresa_id: number;
  ativo?: boolean;
}

interface UsuarioCreate extends Usuario {
  senha: string;
}

const CadastroUsuarioPage: React.FC = () => {
  const [isModalOpen, setIsModalOpen] = useState(false);

  const handleSaveUsuario = (usuarioData: UsuarioCreate | Usuario) => {
    // Aqui você faria a chamada para a API
    console.log('Dados do usuário para salvar:', usuarioData);
    alert('Usuário cadastrado com sucesso! (Simulado)');
  };

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold flex items-center gap-2">
            <Users className="h-6 w-6" />
            Cadastro de Usuários
          </h1>
          <p className="text-muted-foreground">
            Demonstração do componente de cadastro de usuários
          </p>
        </div>
      </div>

      {/* Cards de Exemplo */}
      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-lg">
              <UserPlus className="h-5 w-5" />
              Novo Usuário
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-muted-foreground mb-4">
              Clique no botão abaixo para abrir o modal de cadastro de usuário.
            </p>
            <Button 
              onClick={() => setIsModalOpen(true)} 
              className="w-full"
            >
              Cadastrar Usuário
            </Button>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Campos Incluídos</CardTitle>
          </CardHeader>
          <CardContent>
            <ul className="text-sm space-y-1 text-muted-foreground">
              <li>• CPF (com máscara)</li>
              <li>• Nome completo</li>
              <li>• Email</li>
              <li>• Telefone (opcional)</li>
              <li>• Senha</li>
              <li>• Tipo (Admin/Promoter/Cliente)</li>
              <li>• Empresa</li>
            </ul>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Validações</CardTitle>
          </CardHeader>
          <CardContent>
            <ul className="text-sm space-y-1 text-muted-foreground">
              <li>• CPF obrigatório (11 dígitos)</li>
              <li>• Email válido obrigatório</li>
              <li>• Nome obrigatório</li>
              <li>• Senha mínima de 4 caracteres</li>
              <li>• Telefone opcional (10-11 dígitos)</li>
              <li>• Seleção de empresa obrigatória</li>
            </ul>
          </CardContent>
        </Card>
      </div>

      {/* Informações sobre o componente */}
      <Card>
        <CardHeader>
          <CardTitle>Sobre o Componente</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="prose prose-sm max-w-none">
            <p>
              O componente <code>CadastroUsuarioModal</code> foi criado baseado na estrutura 
              da tabela de usuários do banco de dados e inclui:
            </p>
            
            <h4 className="font-semibold mt-4 mb-2">Funcionalidades:</h4>
            <ul className="space-y-1">
              <li>• Modal responsivo com formulário completo</li>
              <li>• Máscaras automáticas para CPF e telefone</li>
              <li>• Validação em tempo real dos campos</li>
              <li>• Carregamento dinâmico da lista de empresas</li>
              <li>• Suporte para edição de usuários existentes</li>
              <li>• Controle de visibilidade da senha</li>
              <li>• Feedback visual de erros e loading</li>
            </ul>

            <h4 className="font-semibold mt-4 mb-2">Integração:</h4>
            <ul className="space-y-1">
              <li>• Compatible com a API do backend FastAPI</li>
              <li>• Usa os componentes UI do Radix/shadcn</li>
              <li>• Integrado com o sistema de autenticação</li>
              <li>• Respeita as permissões de usuário (admin only)</li>
            </ul>
          </div>
        </CardContent>
      </Card>

      {/* Modal de Cadastro */}
      <CadastroUsuarioModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onSave={handleSaveUsuario}
      />
    </div>
  );
};

export default CadastroUsuarioPage;
