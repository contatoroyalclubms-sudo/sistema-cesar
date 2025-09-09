import React, { useState } from 'react'
import { motion } from 'framer-motion'
import { 
  Send, 
  CheckCircle, 
  User, 
  Mail, 
  Phone, 
  FileText, 
  Building,
  Calendar,
  Users,
  Star,
  Shield,
  Zap
} from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { useIntersectionObserver } from '@/hooks/useIntersectionObserver'
import { validateCPF, validateEmail, formatCPF } from '@/lib/utils'

interface FormData {
  nome: string
  email: string
  cpf: string
  empresa?: string
  telefone?: string
  tipoEvento?: string
  frequenciaEventos?: string
}

const benefits = [
  {
    icon: Calendar,
    title: '30 Dias Grátis',
    description: 'Teste completo sem compromisso'
  },
  {
    icon: Users,
    title: 'Setup Gratuito',
    description: 'Implementação sem custos adicionais'
  },
  {
    icon: Star,
    title: 'Suporte Premium',
    description: 'Atendimento especializado 24/7'
  },
  {
    icon: Shield,
    title: '100% Seguro',
    description: 'Seus dados protegidos com criptografia'
  }
]

const trustedCompanies = [
  'Rock in Rio',
  'Lollapalooza Brasil', 
  'Comic Con Experience',
  'Campus Party',
  'Web Summit',
  'TED Talks'
]

export function LeadFormSection() {
  const { ref, isIntersecting } = useIntersectionObserver({ threshold: 0.2 })
  const [formData, setFormData] = useState<FormData>({
    nome: '',
    email: '',
    cpf: ''
  })
  const [errors, setErrors] = useState<Partial<FormData>>({})
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [isSubmitted, setIsSubmitted] = useState(false)

  const handleInputChange = (field: keyof FormData, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }))
    
    // Clear error when user starts typing
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: undefined }))
    }
  }

  const validateForm = (): boolean => {
    const newErrors: Partial<FormData> = {}

    if (!formData.nome.trim()) {
      newErrors.nome = 'Nome é obrigatório'
    }

    if (!formData.email.trim()) {
      newErrors.email = 'Email é obrigatório'
    } else if (!validateEmail(formData.email)) {
      newErrors.email = 'Email inválido'
    }

    if (!formData.cpf.trim()) {
      newErrors.cpf = 'CPF é obrigatório'
    } else if (!validateCPF(formData.cpf)) {
      newErrors.cpf = 'CPF inválido'
    }

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!validateForm()) return

    setIsSubmitting(true)

    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 2000))
      
      // Here you would normally send the data to your backend
      console.log('Form submitted:', formData)
      
      setIsSubmitted(true)
    } catch (error) {
      console.error('Submission error:', error)
    } finally {
      setIsSubmitting(false)
    }
  }

  const SuccessMessage = () => (
    <motion.div
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.6 }}
      className="text-center py-12"
    >
      <motion.div
        initial={{ scale: 0 }}
        animate={{ scale: 1 }}
        transition={{ delay: 0.2, type: "spring", stiffness: 200 }}
        className="w-20 h-20 bg-green-500/20 rounded-full flex items-center justify-center mx-auto mb-6"
      >
        <CheckCircle className="h-10 w-10 text-green-500" />
      </motion.div>
      
      <h3 className="text-2xl font-bold mb-4">Parabéns! 🎉</h3>
      <p className="text-lg text-muted-foreground mb-6">
        Seu acesso gratuito foi liberado! Em instantes você receberá um email com 
        suas credenciais e o link para começar.
      </p>
      
      <div className="bg-primary/5 rounded-lg p-6 border border-primary/20">
        <h4 className="font-semibold mb-3">Próximos passos:</h4>
        <ul className="text-left space-y-2 text-sm">
          <li className="flex items-center gap-2">
            <div className="w-1.5 h-1.5 bg-primary rounded-full" />
            Verifique seu email (pode estar na caixa de spam)
          </li>
          <li className="flex items-center gap-2">
            <div className="w-1.5 h-1.5 bg-primary rounded-full" />
            Acesse sua conta e explore o dashboard
          </li>
          <li className="flex items-center gap-2">
            <div className="w-1.5 h-1.5 bg-primary rounded-full" />
            Configure seu primeiro evento em minutos
          </li>
        </ul>
      </div>
    </motion.div>
  )

  return (
    <section id="lead-form" ref={ref} className="py-20 bg-muted/30">
      <div className="container mx-auto px-4">
        <div className="grid lg:grid-cols-2 gap-16 items-start">
          {/* Left Column - Information */}
          <motion.div
            initial={{ opacity: 0, x: -30 }}
            animate={isIntersecting ? { opacity: 1, x: 0 } : {}}
            transition={{ duration: 0.8 }}
            className="space-y-8"
          >
            <div>
              <span className="text-primary font-semibold text-sm uppercase tracking-wide mb-2 block">
                Teste Gratuito
              </span>
              <h2 className="text-4xl md:text-5xl font-bold font-display mb-6">
                Comece sua
                <span className="gradient-text"> Revolução</span> Hoje
              </h2>
              <p className="text-xl text-muted-foreground mb-8">
                30 dias grátis para descobrir por que o Unique é a escolha #1 
                dos organizadores mais exigentes do Brasil.
              </p>
            </div>

            {/* Benefits */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
              {benefits.map((benefit, index) => (
                <motion.div
                  key={benefit.title}
                  initial={{ opacity: 0, y: 20 }}
                  animate={isIntersecting ? { opacity: 1, y: 0 } : {}}
                  transition={{ duration: 0.6, delay: 0.2 + index * 0.1 }}
                  className="flex items-start gap-4 p-4 rounded-lg border border-primary/10 bg-background/50 hover:bg-background/80 transition-colors"
                >
                  <div className="w-10 h-10 bg-primary/10 rounded-lg flex items-center justify-center flex-shrink-0">
                    <benefit.icon className="h-5 w-5 text-primary" />
                  </div>
                  <div>
                    <h4 className="font-semibold mb-1">{benefit.title}</h4>
                    <p className="text-sm text-muted-foreground">{benefit.description}</p>
                  </div>
                </motion.div>
              ))}
            </div>

            {/* Trusted By */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={isIntersecting ? { opacity: 1, y: 0 } : {}}
              transition={{ duration: 0.6, delay: 0.8 }}
            >
              <p className="text-sm text-muted-foreground mb-4">
                Confiado por grandes eventos como:
              </p>
              <div className="flex flex-wrap gap-2">
                {trustedCompanies.map((company, index) => (
                  <span
                    key={company}
                    className="text-xs bg-primary/10 text-primary px-3 py-1 rounded-full font-medium"
                  >
                    {company}
                  </span>
                ))}
              </div>
            </motion.div>
          </motion.div>

          {/* Right Column - Form */}
          <motion.div
            initial={{ opacity: 0, x: 30 }}
            animate={isIntersecting ? { opacity: 1, x: 0 } : {}}
            transition={{ duration: 0.8, delay: 0.2 }}
          >
            <Card className="border-2 border-primary/20 shadow-2xl shadow-primary/10">
              <CardHeader className="pb-6">
                <CardTitle className="text-2xl text-center">
                  {isSubmitted ? 'Bem-vindo ao Unique!' : 'Acesso Gratuito por 30 Dias'}
                </CardTitle>
              </CardHeader>
              
              <CardContent>
                {isSubmitted ? (
                  <SuccessMessage />
                ) : (
                  <form onSubmit={handleSubmit} className="space-y-6">
                    {/* Nome */}
                    <div className="space-y-2">
                      <label className="text-sm font-medium flex items-center gap-2">
                        <User className="h-4 w-4" />
                        Nome Completo *
                      </label>
                      <Input
                        type="text"
                        placeholder="Seu nome completo"
                        value={formData.nome}
                        onChange={(e) => handleInputChange('nome', e.target.value)}
                        className={errors.nome ? 'border-red-500' : ''}
                      />
                      {errors.nome && (
                        <p className="text-red-500 text-sm">{errors.nome}</p>
                      )}
                    </div>

                    {/* Email */}
                    <div className="space-y-2">
                      <label className="text-sm font-medium flex items-center gap-2">
                        <Mail className="h-4 w-4" />
                        Email Profissional *
                      </label>
                      <Input
                        type="email"
                        placeholder="seu@email.com"
                        value={formData.email}
                        onChange={(e) => handleInputChange('email', e.target.value)}
                        className={errors.email ? 'border-red-500' : ''}
                      />
                      {errors.email && (
                        <p className="text-red-500 text-sm">{errors.email}</p>
                      )}
                    </div>

                    {/* CPF */}
                    <div className="space-y-2">
                      <label className="text-sm font-medium flex items-center gap-2">
                        <FileText className="h-4 w-4" />
                        CPF *
                      </label>
                      <Input
                        type="text"
                        placeholder="000.000.000-00"
                        value={formData.cpf}
                        onChange={(e) => handleInputChange('cpf', formatCPF(e.target.value))}
                        maxLength={14}
                        className={errors.cpf ? 'border-red-500' : ''}
                      />
                      {errors.cpf && (
                        <p className="text-red-500 text-sm">{errors.cpf}</p>
                      )}
                    </div>

                    {/* Empresa (Opcional) */}
                    <div className="space-y-2">
                      <label className="text-sm font-medium flex items-center gap-2">
                        <Building className="h-4 w-4" />
                        Empresa (Opcional)
                      </label>
                      <Input
                        type="text"
                        placeholder="Nome da sua empresa"
                        value={formData.empresa || ''}
                        onChange={(e) => handleInputChange('empresa', e.target.value)}
                      />
                    </div>

                    {/* Telefone (Opcional) */}
                    <div className="space-y-2">
                      <label className="text-sm font-medium flex items-center gap-2">
                        <Phone className="h-4 w-4" />
                        WhatsApp (Opcional)
                      </label>
                      <Input
                        type="tel"
                        placeholder="(11) 99999-9999"
                        value={formData.telefone || ''}
                        onChange={(e) => handleInputChange('telefone', e.target.value)}
                      />
                    </div>

                    <Button
                      type="submit"
                      size="lg"
                      variant="gradient"
                      className="w-full group"
                      disabled={isSubmitting}
                      loading={isSubmitting}
                    >
                      {isSubmitting ? (
                        'Criando sua conta...'
                      ) : (
                        <>
                          Começar Agora - Grátis
                          <Send className="ml-2 h-5 w-5 group-hover:translate-x-1 transition-transform" />
                        </>
                      )}
                    </Button>

                    <p className="text-xs text-muted-foreground text-center">
                      Ao continuar, você concorda com nossos{' '}
                      <a href="#" className="text-primary hover:underline">
                        Termos de Uso
                      </a>{' '}
                      e{' '}
                      <a href="#" className="text-primary hover:underline">
                        Política de Privacidade
                      </a>
                    </p>
                  </form>
                )}
              </CardContent>
            </Card>

            {/* Security Badge */}
            {!isSubmitted && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={isIntersecting ? { opacity: 1, y: 0 } : {}}
                transition={{ duration: 0.6, delay: 1.0 }}
                className="flex items-center justify-center gap-2 mt-6 text-sm text-muted-foreground"
              >
                <Shield className="h-4 w-4 text-green-500" />
                Seus dados estão protegidos com criptografia SSL 256-bit
              </motion.div>
            )}
          </motion.div>
        </div>
      </div>
    </section>
  )
}