import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Label } from '../ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Alert, AlertDescription } from '../ui/alert';
import { Loader2, Calendar, UserPlus, LogIn } from 'lucide-react';
import RegisterForm from './RegisterForm';

const LoginForm: React.FC = () => {
  const [mode, setMode] = useState<'login' | 'register'>('login');
  const [cpf, setCpf] = useState('');
  const [senha, setSenha] = useState('');
  const [codigoVerificacao, setCodigoVerificacao] = useState('');
  const [needsVerification, setNeedsVerification] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [verificationMessage, setVerificationMessage] = useState('');

  const { login } = useAuth();
  const navigate = useNavigate();

  const formatCPF = (value: string) => {
    const numbers = value.replace(/\D/g, '');
    return numbers.replace(/(\d{3})(\d{3})(\d{3})(\d{2})/, '$1.$2.$3-$4');
  };

  const handleCpfChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const formatted = formatCPF(e.target.value);
    if (formatted.length <= 14) {
      setCpf(formatted);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const cpfNumbers = cpf.replace(/\D/g, '');
      
      if (cpfNumbers.length !== 11) {
        setError('CPF deve ter 11 dígitos');
        setLoading(false);
        return;
      }

      const result = await login(cpfNumbers, senha, codigoVerificacao);

      if (result.success) {
        navigate('/app/dashboard');
      } else if (result.needsVerification) {
        setNeedsVerification(true);
        setVerificationMessage(result.message);
      }
    } catch (error: any) {
      setError(error.response?.data?.detail || 'Erro ao fazer login');
    } finally {
      setLoading(false);
    }
  };

  const handleRegisterSuccess = () => {
    setMode('login');
    setError('');
    // Limpar campos
    setCpf('');
    setSenha('');
    setCodigoVerificacao('');
    setNeedsVerification(false);
    setVerificationMessage('');
    // Mostrar mensagem de sucesso
    alert('Conta criada com sucesso! Faça login para continuar.');
  };

  const handleToggleMode = () => {
    setMode(mode === 'login' ? 'register' : 'login');
    setError('');
    setNeedsVerification(false);
    setVerificationMessage('');
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-background py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div className="text-center">
          <Calendar className="mx-auto h-12 w-12 text-blue-600" />
          <h2 className="mt-6 text-3xl font-extrabold text-foreground">
            Sistema de Gestão de Eventos
          </h2>
          <p className="mt-2 text-sm text-muted-foreground">
            {mode === 'login' 
              ? 'Faça login para acessar o sistema'
              : 'Crie sua conta para acessar o sistema'
            }
          </p>
        </div>

        {mode === 'register' ? (
          <RegisterForm 
            onSuccess={handleRegisterSuccess}
            onToggleMode={handleToggleMode}
          />
        ) : (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <LogIn className="h-5 w-5" />
                Entrar
              </CardTitle>
              <CardDescription>
                {needsVerification 
                  ? 'Digite o código de verificação enviado'
                  : 'Digite suas credenciais para acessar'
                }
              </CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleSubmit} className="space-y-4">
                {!needsVerification ? (
                  <>
                    <div className="space-y-2">
                      <Label htmlFor="cpf">CPF</Label>
                      <Input
                        id="cpf"
                        type="text"
                        placeholder="000.000.000-00"
                        value={cpf}
                        onChange={handleCpfChange}
                        required
                        maxLength={14}
                      />
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="senha">Senha</Label>
                      <Input
                        id="senha"
                        type="password"
                        placeholder="Digite sua senha"
                        value={senha}
                        onChange={(e) => setSenha(e.target.value)}
                        required
                      />
                    </div>
                  </>
                ) : (
                  <>
                    {verificationMessage && (
                      <Alert>
                        <AlertDescription>
                          {verificationMessage}
                        </AlertDescription>
                      </Alert>
                    )}
                    
                    <div className="space-y-2">
                      <Label htmlFor="codigo">Código de Verificação</Label>
                      <Input
                        id="codigo"
                        type="text"
                        placeholder="Digite o código de 6 dígitos"
                        value={codigoVerificacao}
                        onChange={(e) => setCodigoVerificacao(e.target.value)}
                        required
                        maxLength={6}
                      />
                    </div>
                  </>
                )}

                {error && (
                  <Alert variant="destructive">
                    <AlertDescription>{error}</AlertDescription>
                  </Alert>
                )}

                <div className="space-y-2">
                  <Button 
                    type="submit" 
                    className="w-full"
                    disabled={loading}
                  >
                    {loading ? (
                      <>
                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                        {needsVerification ? 'Verificando...' : 'Entrando...'}
                      </>
                    ) : (
                      needsVerification ? 'Verificar' : 'Entrar'
                    )}
                  </Button>

                  {!needsVerification && (
                    <Button
                      type="button"
                      variant="ghost"
                      onClick={handleToggleMode}
                      className="w-full flex items-center gap-2"
                    >
                      <UserPlus className="h-4 w-4" />
                      Não tem uma conta? Criar conta
                    </Button>
                  )}

                  {needsVerification && (
                    <Button
                      type="button"
                      variant="ghost"
                      onClick={() => {
                        setNeedsVerification(false);
                        setCodigoVerificacao('');
                        setError('');
                        setVerificationMessage('');
                      }}
                      className="w-full"
                    >
                      Voltar
                    </Button>
                  )}
                </div>
              </form>
            </CardContent>
          </Card>
        )}

        {/* Informações adicionais para desenvolvimento */}
        <div className="text-center">
          <div className="text-xs text-muted-foreground space-y-1">
            <p><strong>Usuários para teste:</strong></p>
            <p>Admin: CPF 000.000.000-00, Senha: 0000</p>
            <p>Promoter: CPF 111.111.111-11, Senha: promoter123</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LoginForm;
