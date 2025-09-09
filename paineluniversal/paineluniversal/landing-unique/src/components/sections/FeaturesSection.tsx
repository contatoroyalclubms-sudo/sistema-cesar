import React from 'react'
import { motion } from 'framer-motion'
import { 
  Zap, 
  Shield, 
  BarChart3, 
  CreditCard, 
  Users, 
  Smartphone,
  Cloud,
  Headphones,
  Globe,
  Lock,
  TrendingUp,
  Clock
} from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { useIntersectionObserver } from '@/hooks/useIntersectionObserver'

interface Feature {
  icon: React.ElementType
  title: string
  description: string
  color: string
  bgColor: string
}

const features: Feature[] = [
  {
    icon: Zap,
    title: 'Performance Ultra-Rápida',
    description: 'Sistema otimizado para alta velocidade, com carregamento instantâneo e resposta em tempo real.',
    color: 'text-yellow-600',
    bgColor: 'bg-yellow-500/10'
  },
  {
    icon: Shield,
    title: 'Segurança Avançada',
    description: 'Proteção de dados com criptografia de ponta e conformidade com LGPD e regulamentações internacionais.',
    color: 'text-blue-600',
    bgColor: 'bg-blue-500/10'
  },
  {
    icon: BarChart3,
    title: 'Analytics Inteligente',
    description: 'Relatórios detalhados e insights preditivos para otimizar seus eventos e maximizar resultados.',
    color: 'text-purple-600',
    bgColor: 'bg-purple-500/10'
  },
  {
    icon: CreditCard,
    title: 'Pagamentos Seguros',
    description: 'Integração com principais gateways de pagamento, parcelamento e múltiplas formas de pagamento.',
    color: 'text-green-600',
    bgColor: 'bg-green-500/10'
  },
  {
    icon: Users,
    title: 'Gestão de Equipes',
    description: 'Sistema completo de permissões, roles e colaboração em tempo real para sua equipe.',
    color: 'text-indigo-600',
    bgColor: 'bg-indigo-500/10'
  },
  {
    icon: Smartphone,
    title: 'Mobile First',
    description: 'Experiência otimizada para mobile com app nativo e interface responsiva perfeita.',
    color: 'text-pink-600',
    bgColor: 'bg-pink-500/10'
  },
  {
    icon: Cloud,
    title: 'Cloud Nativo',
    description: 'Infraestrutura 100% em nuvem com escalabilidade automática e backup contínuo.',
    color: 'text-cyan-600',
    bgColor: 'bg-cyan-500/10'
  },
  {
    icon: Headphones,
    title: 'Suporte 24/7',
    description: 'Atendimento especializado disponível 24 horas com chat, telefone e suporte técnico.',
    color: 'text-orange-600',
    bgColor: 'bg-orange-500/10'
  },
  {
    icon: Globe,
    title: 'Multi-idiomas',
    description: 'Suporte completo a múltiplos idiomas e moedas para eventos internacionais.',
    color: 'text-teal-600',
    bgColor: 'bg-teal-500/10'
  },
  {
    icon: Lock,
    title: 'Compliance Total',
    description: 'Certificações ISO, SOC2 e conformidade com LGPD para máxima confiança e segurança.',
    color: 'text-red-600',
    bgColor: 'bg-red-500/10'
  },
  {
    icon: TrendingUp,
    title: 'Growth Marketing',
    description: 'Ferramentas de marketing integradas para impulsionar vendas e engajamento.',
    color: 'text-violet-600',
    bgColor: 'bg-violet-500/10'
  },
  {
    icon: Clock,
    title: 'Tempo Real',
    description: 'Sincronização instantânea em todos os dispositivos com atualizações em tempo real.',
    color: 'text-emerald-600',
    bgColor: 'bg-emerald-500/10'
  }
]

const FeatureCard = ({ feature, index }: { feature: Feature; index: number }) => {
  const { ref, isIntersecting } = useIntersectionObserver({ threshold: 0.3 })

  return (
    <motion.div
      ref={ref}
      initial={{ opacity: 0, y: 50, scale: 0.9 }}
      animate={isIntersecting ? { opacity: 1, y: 0, scale: 1 } : {}}
      transition={{ duration: 0.6, delay: index * 0.1 }}
      whileHover={{ 
        scale: 1.05, 
        transition: { duration: 0.2 } 
      }}
      className="group"
    >
      <Card className="h-full border-2 border-transparent hover:border-primary/20 transition-all duration-300 hover:shadow-xl hover:shadow-primary/10">
        <CardHeader className="pb-4">
          <div className={`w-14 h-14 ${feature.bgColor} rounded-xl flex items-center justify-center mb-4 group-hover:scale-110 transition-transform duration-300`}>
            <feature.icon className={`h-7 w-7 ${feature.color}`} />
          </div>
          <CardTitle className="text-xl group-hover:text-primary transition-colors">
            {feature.title}
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-muted-foreground leading-relaxed">
            {feature.description}
          </p>
        </CardContent>
      </Card>
    </motion.div>
  )
}

const BenefitBanner = () => {
  const { ref, isIntersecting } = useIntersectionObserver({ threshold: 0.5 })
  
  return (
    <motion.div
      ref={ref}
      initial={{ opacity: 0, scale: 0.95 }}
      animate={isIntersecting ? { opacity: 1, scale: 1 } : {}}
      transition={{ duration: 0.8 }}
      className="relative overflow-hidden rounded-2xl bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 p-8 text-white"
    >
      <div className="absolute inset-0 bg-black/20" />
      <div className="relative z-10">
        <div className="grid lg:grid-cols-3 gap-8 items-center">
          <div className="lg:col-span-2">
            <h3 className="text-3xl font-bold mb-4">
              Mais que um Sistema, uma Revolução
            </h3>
            <p className="text-xl text-white/90 mb-6">
              Junte-se a mais de 10.000 organizadores que já descobriram o poder 
              do Unique para transformar eventos comuns em experiências inesquecíveis.
            </p>
            <div className="grid grid-cols-2 gap-6">
              <div>
                <div className="text-3xl font-bold mb-1">300%</div>
                <div className="text-white/80">Aumento médio em vendas</div>
              </div>
              <div>
                <div className="text-3xl font-bold mb-1">15min</div>
                <div className="text-white/80">Setup completo</div>
              </div>
            </div>
          </div>
          
          <div className="space-y-4">
            {[
              { icon: Zap, text: 'Implementação imediata' },
              { icon: TrendingUp, text: 'ROI comprovado' },
              { icon: Headphones, text: 'Suporte especializado' }
            ].map((item, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, x: 20 }}
                animate={isIntersecting ? { opacity: 1, x: 0 } : {}}
                transition={{ duration: 0.6, delay: 0.2 + index * 0.1 }}
                className="flex items-center gap-3 bg-white/10 rounded-lg p-3 backdrop-blur-sm"
              >
                <item.icon className="h-5 w-5" />
                <span>{item.text}</span>
              </motion.div>
            ))}
          </div>
        </div>
      </div>
      
      {/* Decorative elements */}
      <div className="absolute -top-20 -right-20 w-40 h-40 bg-white/10 rounded-full blur-3xl" />
      <div className="absolute -bottom-20 -left-20 w-40 h-40 bg-white/10 rounded-full blur-3xl" />
    </motion.div>
  )
}

export function FeaturesSection() {
  const { ref, isIntersecting } = useIntersectionObserver({ threshold: 0.1 })

  return (
    <section ref={ref} className="py-20 bg-muted/30">
      <div className="container mx-auto px-4">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={isIntersecting ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.8 }}
          className="text-center mb-16"
        >
          <span className="text-primary font-semibold text-sm uppercase tracking-wide mb-2 block">
            Recursos Avançados
          </span>
          <h2 className="text-4xl md:text-6xl font-bold font-display mb-6">
            Tecnologia que
            <span className="gradient-text"> Faz a Diferença</span>
          </h2>
          <p className="text-xl text-muted-foreground max-w-3xl mx-auto">
            Descubra os recursos revolucionários que tornam o Unique a escolha #1 
            dos profissionais mais exigentes do mercado de eventos.
          </p>
        </motion.div>

        {/* Features Grid */}
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8 mb-16">
          {features.map((feature, index) => (
            <FeatureCard key={feature.title} feature={feature} index={index} />
          ))}
        </div>

        {/* Benefit Banner */}
        <BenefitBanner />
      </div>
    </section>
  )
}