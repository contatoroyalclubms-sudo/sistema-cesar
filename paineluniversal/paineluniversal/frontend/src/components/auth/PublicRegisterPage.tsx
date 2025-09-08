import React from 'react';
import { useNavigate } from 'react-router-dom';
import RegisterForm from './RegisterForm';
import { Button } from '../ui/button';
import { ArrowLeft, Calendar } from 'lucide-react';
import { useToast } from '../../hooks/use-toast';

const PublicRegisterPage: React.FC = () => {
  const navigate = useNavigate();
  const { toast } = useToast();

  const handleRegisterSuccess = () => {
    toast({
      title: "Conta criada com sucesso!",
      description: "Agora você pode fazer login com suas credenciais.",
      duration: 5000,
    });
    
    // Redirecionar para login após 2 segundos
    setTimeout(() => {
      navigate('/login');
    }, 2000);
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div className="text-center">
          <Calendar className="mx-auto h-12 w-12 text-blue-600" />
          <h2 className="mt-6 text-3xl font-extrabold text-gray-900">
            Sistema de Gestão de Eventos
          </h2>
          <p className="mt-2 text-sm text-gray-600">
            Crie sua conta para acessar o sistema
          </p>
        </div>

        <div className="flex justify-center">
          <Button
            variant="ghost"
            onClick={() => navigate('/login')}
            className="flex items-center gap-2 mb-4"
          >
            <ArrowLeft className="h-4 w-4" />
            Voltar para Login
          </Button>
        </div>

        <RegisterForm 
          onSuccess={handleRegisterSuccess}
        />
      </div>
    </div>
  );
};

export default PublicRegisterPage;