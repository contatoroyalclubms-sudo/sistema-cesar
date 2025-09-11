import React from 'react'
import { motion } from 'framer-motion'
import { Monitor, Smartphone, Tablet, Play } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { useIntersectionObserver } from '@/hooks/useIntersectionObserver'

const DeviceFrame = ({ 
  children, 
  type = 'desktop' 
}: { 
  children: React.ReactNode
  type?: 'desktop' | 'mobile' | 'tablet'
}) => {
  const getFrameClass = () => {
    switch (type) {
      case 'mobile':
        return 'w-64 h-96 rounded-3xl border-8 border-gray-800 bg-black p-2'
      case 'tablet':
        return 'w-80 h-64 rounded-2xl border-6 border-gray-700 bg-black p-2'
      default:
        return 'w-full max-w-4xl h-64 rounded-lg border-4 border-gray-600 bg-black p-2'
    }
  }

  return (
    <div className={`${getFrameClass()} shadow-2xl mx-auto`}>
      <div className="w-full h-full bg-gradient-to-br from-blue-900 via-purple-900 to-pink-900 rounded-lg overflow-hidden">
        {children}
      </div>
    </div>
  )
}

const MockupContent = ({ type }: { type: 'dashboard' | 'mobile' | 'analytics' }) => {
  const getDashboardContent = () => (
    <div className="p-4 h-full">
      <div className="flex items-center gap-4 mb-4">
        <div className="w-8 h-8 bg-blue-500 rounded-full" />
        <div className="h-2 bg-white/20 rounded flex-1 max-w-32" />
      </div>
      <div className="grid grid-cols-3 gap-4 mb-4">
        {[1, 2, 3].map((i) => (
          <div key={i} className="bg-white/10 rounded-lg p-3">
            <div className="h-2 bg-blue-400 rounded mb-2" />
            <div className="h-6 bg-white/20 rounded" />
          </div>
        ))}
      </div>
      <div className="bg-white/10 rounded-lg p-4 flex-1">
        <div className="h-2 bg-purple-400 rounded mb-2" />
        <div className="space-y-2">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="flex gap-2">
              <div className="w-2 h-2 bg-white/30 rounded-full mt-1" />
              <div className="h-2 bg-white/20 rounded flex-1" />
            </div>
          ))}
        </div>
      </div>
    </div>
  )

  const getMobileContent = () => (
    <div className="p-3 h-full">
      <div className="flex items-center justify-between mb-3">
        <div className="w-6 h-6 bg-blue-500 rounded-full" />
        <div className="h-1.5 bg-white/20 rounded w-16" />
        <div className="w-6 h-6 bg-green-500 rounded-full" />
      </div>
      <div className="space-y-3">
        {[1, 2, 3, 4, 5].map((i) => (
          <div key={i} className="bg-white/10 rounded-lg p-3 flex items-center gap-3">
            <div className="w-8 h-8 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full" />
            <div className="flex-1">
              <div className="h-2 bg-white/30 rounded mb-1" />
              <div className="h-1.5 bg-white/20 rounded w-3/4" />
            </div>
          </div>
        ))}
      </div>
    </div>
  )

  const getAnalyticsContent = () => (
    <div className="p-4 h-full">
      <div className="grid grid-cols-2 gap-4 mb-4">
        <div className="bg-white/10 rounded-lg p-3">
          <div className="w-full h-16 bg-gradient-to-r from-blue-500 to-purple-500 rounded mb-2 relative">
            <div className="absolute inset-0 bg-white/20 rounded" />
          </div>
          <div className="h-1.5 bg-white/30 rounded" />
        </div>
        <div className="bg-white/10 rounded-lg p-3">
          <div className="w-full h-16 bg-gradient-to-r from-green-500 to-teal-500 rounded mb-2 relative">
            <div className="absolute inset-0 bg-white/20 rounded" />
          </div>
          <div className="h-1.5 bg-white/30 rounded" />
        </div>
      </div>
      <div className="bg-white/10 rounded-lg p-3">
        <div className="flex justify-between items-end h-20">
          {[60, 80, 45, 90, 70, 85, 65].map((height, i) => (
            <div
              key={i}
              className="bg-gradient-to-t from-blue-500 to-purple-500 rounded-t w-6"
              style={{ height: `${height}%` }}
            />
          ))}
        </div>
      </div>
    </div>
  )

  switch (type) {
    case 'mobile':
      return getMobileContent()
    case 'analytics':
      return getAnalyticsContent()
    default:
      return getDashboardContent()
  }
}

export function ProductSection() {
  const { ref, isIntersecting } = useIntersectionObserver({ threshold: 0.2 })

  return (
    <section id="product-demo" ref={ref} className="py-20 bg-background">
      <div className="container mx-auto px-4">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={isIntersecting ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.8 }}
          className="text-center mb-16"
        >
          <span className="text-primary font-semibold text-sm uppercase tracking-wide mb-2 block">
            Plataforma Completa
          </span>
          <h2 className="text-4xl md:text-6xl font-bold font-display mb-6">
            Uma Solução,
            <span className="gradient-text"> Infinitas Possibilidades</span>
          </h2>
          <p className="text-xl text-muted-foreground max-w-3xl mx-auto">
            Descubra como o Unique revoluciona a gestão de eventos com tecnologia de ponta, 
            interface intuitiva e recursos que realmente fazem a diferença.
          </p>
        </motion.div>

        <div className="space-y-20">
          {/* Desktop Dashboard */}
          <motion.div
            initial={{ opacity: 0, y: 50 }}
            animate={isIntersecting ? { opacity: 1, y: 0 } : {}}
            transition={{ duration: 0.8, delay: 0.2 }}
            className="grid lg:grid-cols-2 gap-12 items-center"
          >
            <div className="space-y-6">
              <div className="flex items-center gap-3 mb-4">
                <div className="w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center">
                  <Monitor className="h-6 w-6 text-primary" />
                </div>
                <span className="text-primary font-semibold">Dashboard Avançado</span>
              </div>
              
              <h3 className="text-3xl font-bold">
                Controle Total em Tempo Real
              </h3>
              
              <p className="text-lg text-muted-foreground">
                Monitore vendas, check-ins, receita e muito mais através de um dashboard 
                intuitivo e poderoso. Tome decisões baseadas em dados reais e atualizados 
                em tempo real.
              </p>
              
              <ul className="space-y-3">
                {[
                  'Analytics avançados com visualizações interativas',
                  'Relatórios personalizados e exportação automática',
                  'Alertas inteligentes e notificações em tempo real',
                  'Integração com ferramentas de gestão'
                ].map((feature, index) => (
                  <li key={index} className="flex items-start gap-3">
                    <div className="w-1.5 h-1.5 bg-primary rounded-full mt-3" />
                    <span className="text-muted-foreground">{feature}</span>
                  </li>
                ))}
              </ul>
            </div>
            
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={isIntersecting ? { opacity: 1, scale: 1 } : {}}
              transition={{ duration: 0.8, delay: 0.4 }}
            >
              <DeviceFrame type="desktop">
                <MockupContent type="dashboard" />
              </DeviceFrame>
            </motion.div>
          </motion.div>

          {/* Mobile Experience */}
          <motion.div
            initial={{ opacity: 0, y: 50 }}
            animate={isIntersecting ? { opacity: 1, y: 0 } : {}}
            transition={{ duration: 0.8, delay: 0.6 }}
            className="grid lg:grid-cols-2 gap-12 items-center"
          >
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={isIntersecting ? { opacity: 1, scale: 1 } : {}}
              transition={{ duration: 0.8, delay: 0.8 }}
              className="order-2 lg:order-1"
            >
              <DeviceFrame type="mobile">
                <MockupContent type="mobile" />
              </DeviceFrame>
            </motion.div>
            
            <div className="space-y-6 order-1 lg:order-2">
              <div className="flex items-center gap-3 mb-4">
                <div className="w-12 h-12 bg-green-500/10 rounded-lg flex items-center justify-center">
                  <Smartphone className="h-6 w-6 text-green-600" />
                </div>
                <span className="text-green-600 font-semibold">Check-in Móvel</span>
              </div>
              
              <h3 className="text-3xl font-bold">
                Check-in Inteligente e Rápido
              </h3>
              
              <p className="text-lg text-muted-foreground">
                Sistema de check-in otimizado para mobile com QR Code, validação de CPF 
                e interface ultra-responsiva. Sem filas, sem complicações.
              </p>
              
              <ul className="space-y-3">
                {[
                  'QR Code único e seguro para cada participante',
                  'Validação instantânea por CPF ou documento',
                  'Modo offline com sincronização automática',
                  'Interface otimizada para equipes de campo'
                ].map((feature, index) => (
                  <li key={index} className="flex items-start gap-3">
                    <div className="w-1.5 h-1.5 bg-green-600 rounded-full mt-3" />
                    <span className="text-muted-foreground">{feature}</span>
                  </li>
                ))}
              </ul>
            </div>
          </motion.div>

          {/* Analytics */}
          <motion.div
            initial={{ opacity: 0, y: 50 }}
            animate={isIntersecting ? { opacity: 1, y: 0 } : {}}
            transition={{ duration: 0.8, delay: 1.0 }}
            className="grid lg:grid-cols-2 gap-12 items-center"
          >
            <div className="space-y-6">
              <div className="flex items-center gap-3 mb-4">
                <div className="w-12 h-12 bg-purple-500/10 rounded-lg flex items-center justify-center">
                  <Tablet className="h-6 w-6 text-purple-600" />
                </div>
                <span className="text-purple-600 font-semibold">Analytics Avançados</span>
              </div>
              
              <h3 className="text-3xl font-bold">
                Inteligência de Dados
              </h3>
              
              <p className="text-lg text-muted-foreground">
                Transforme dados em insights valiosos com nossos relatórios inteligentes. 
                Entenda seu público, otimize vendas e maximize o ROI dos seus eventos.
              </p>
              
              <ul className="space-y-3">
                {[
                  'Métricas de engajamento e conversão',
                  'Análise preditiva de vendas',
                  'Segmentação avançada de público',
                  'Comparativos e benchmarks do mercado'
                ].map((feature, index) => (
                  <li key={index} className="flex items-start gap-3">
                    <div className="w-1.5 h-1.5 bg-purple-600 rounded-full mt-3" />
                    <span className="text-muted-foreground">{feature}</span>
                  </li>
                ))}
              </ul>
            </div>
            
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={isIntersecting ? { opacity: 1, scale: 1 } : {}}
              transition={{ duration: 0.8, delay: 1.2 }}
            >
              <DeviceFrame type="tablet">
                <MockupContent type="analytics" />
              </DeviceFrame>
            </motion.div>
          </motion.div>
        </div>

        {/* CTA */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={isIntersecting ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.8, delay: 1.4 }}
          className="text-center mt-20"
        >
          <Card className="max-w-2xl mx-auto border-2 border-primary/20 bg-gradient-to-r from-primary/5 to-purple-500/5">
            <CardContent className="p-8">
              <h3 className="text-2xl font-bold mb-4">
                Pronto para revolucionar seus eventos?
              </h3>
              <p className="text-muted-foreground mb-6">
                Experimente gratuitamente por 30 dias e descubra por que somos a escolha #1 
                dos organizadores de eventos mais exigentes.
              </p>
              <Button size="lg" variant="gradient" className="group">
                <Play className="mr-2 h-5 w-5 group-hover:scale-110 transition-transform" />
                Iniciar Teste Gratuito
              </Button>
            </CardContent>
          </Card>
        </motion.div>
      </div>
    </section>
  )
}