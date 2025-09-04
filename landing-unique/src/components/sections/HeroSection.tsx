import React from 'react'
import { motion } from 'framer-motion'
import { ArrowRight, Play, Star, Zap, Users, BarChart3 } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { useIntersectionObserver } from '@/hooks/useIntersectionObserver'

const FloatingIcon = ({ children, delay = 0 }: { children: React.ReactNode; delay?: number }) => (
  <motion.div
    initial={{ opacity: 0, y: 20 }}
    animate={{ opacity: 1, y: 0 }}
    transition={{ duration: 0.6, delay }}
    className="absolute"
  >
    <motion.div
      animate={{ 
        y: [-10, 10, -10],
        rotate: [0, 5, -5, 0]
      }}
      transition={{ 
        duration: 6, 
        repeat: Infinity, 
        ease: "easeInOut" 
      }}
      className="p-3 bg-white/10 backdrop-blur-lg rounded-full border border-white/20 shadow-lg"
    >
      {children}
    </motion.div>
  </motion.div>
)

export function HeroSection() {
  const { ref, isIntersecting } = useIntersectionObserver({ threshold: 0.3 })

  const scrollToSection = (sectionId: string) => {
    const element = document.getElementById(sectionId)
    element?.scrollIntoView({ behavior: 'smooth' })
  }

  return (
    <section 
      ref={ref}
      className="relative min-h-screen flex items-center justify-center overflow-hidden hero-bg"
    >
      {/* Background Elements */}
      <div className="absolute inset-0">
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-blue-500/30 rounded-full blur-3xl animate-pulse" />
        <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-purple-500/30 rounded-full blur-3xl animate-pulse" />
        <div className="absolute top-1/2 left-1/2 w-64 h-64 bg-pink-500/20 rounded-full blur-2xl animate-pulse" />
      </div>

      {/* Floating Icons */}
      <FloatingIcon delay={0.2}>
        <Zap className="h-6 w-6 text-white" />
      </FloatingIcon>
      
      <FloatingIcon delay={0.4}>
        <Users className="h-6 w-6 text-white" />
      </FloatingIcon>
      
      <FloatingIcon delay={0.6}>
        <BarChart3 className="h-6 w-6 text-white" />
      </FloatingIcon>

      {/* Content */}
      <div className="relative z-10 container mx-auto px-4 text-center text-white">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={isIntersecting ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.8, delay: 0.2 }}
          className="flex items-center justify-center gap-2 mb-6"
        >
          <div className="flex">
            {[1, 2, 3, 4, 5].map((star) => (
              <Star key={star} className="h-5 w-5 fill-yellow-400 text-yellow-400" />
            ))}
          </div>
          <span className="text-sm font-medium bg-white/20 px-3 py-1 rounded-full backdrop-blur-sm">
            #1 Sistema de Gestão de Eventos
          </span>
        </motion.div>

        <motion.h1
          initial={{ opacity: 0, y: 30 }}
          animate={isIntersecting ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.8, delay: 0.4 }}
          className="text-5xl md:text-7xl font-bold font-display mb-6 leading-tight"
        >
          O Futuro dos
          <br />
          <span className="bg-gradient-to-r from-blue-200 via-purple-200 to-pink-200 bg-clip-text text-transparent">
            Eventos é Unique
          </span>
        </motion.h1>

        <motion.p
          initial={{ opacity: 0, y: 30 }}
          animate={isIntersecting ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.8, delay: 0.6 }}
          className="text-xl md:text-2xl mb-8 max-w-3xl mx-auto leading-relaxed text-white/90"
        >
          Transforme seus eventos com nossa plataforma revolucionária. 
          <strong> Gestão completa, vendas em tempo real, check-in inteligente</strong> 
          e analytics avançados em uma única solução.
        </motion.p>

        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={isIntersecting ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.8, delay: 0.8 }}
          className="flex flex-col sm:flex-row gap-4 justify-center items-center mb-12"
        >
          <Button 
            size="xl" 
            variant="default"
            onClick={() => scrollToSection('lead-form')}
            className="bg-white text-blue-600 hover:bg-white/90 shadow-xl hover:shadow-2xl transition-all duration-300 group"
          >
            Começar Agora
            <ArrowRight className="ml-2 h-5 w-5 group-hover:translate-x-1 transition-transform" />
          </Button>
          
          <Button 
            size="xl" 
            variant="outline"
            onClick={() => scrollToSection('product-demo')}
            className="border-white/30 text-white hover:bg-white/10 backdrop-blur-sm group"
          >
            <Play className="mr-2 h-5 w-5 group-hover:scale-110 transition-transform" />
            Ver Demo
          </Button>
        </motion.div>

        {/* Stats */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={isIntersecting ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.8, delay: 1.0 }}
          className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-4xl mx-auto"
        >
          {[
            { number: '50K+', label: 'Eventos Realizados', icon: Zap },
            { number: '2M+', label: 'Ingressos Vendidos', icon: Users },
            { number: '98%', label: 'Satisfação dos Clientes', icon: Star },
          ].map((stat, index) => (
            <motion.div
              key={stat.label}
              initial={{ opacity: 0, scale: 0.9 }}
              animate={isIntersecting ? { opacity: 1, scale: 1 } : {}}
              transition={{ duration: 0.6, delay: 1.2 + index * 0.1 }}
              className="glass-card p-6 hover:scale-105 transition-all duration-300"
            >
              <stat.icon className="h-8 w-8 text-blue-300 mx-auto mb-2" />
              <div className="text-3xl font-bold mb-1">{stat.number}</div>
              <div className="text-white/70">{stat.label}</div>
            </motion.div>
          ))}
        </motion.div>
      </div>

      {/* Scroll Indicator */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={isIntersecting ? { opacity: 1 } : {}}
        transition={{ duration: 1, delay: 1.5 }}
        className="absolute bottom-8 left-1/2 transform -translate-x-1/2"
      >
        <motion.div
          animate={{ y: [0, 10, 0] }}
          transition={{ duration: 2, repeat: Infinity }}
          className="w-6 h-10 border-2 border-white/50 rounded-full flex justify-center"
        >
          <motion.div
            animate={{ y: [0, 12, 0] }}
            transition={{ duration: 2, repeat: Infinity }}
            className="w-1 h-3 bg-white/70 rounded-full mt-2"
          />
        </motion.div>
      </motion.div>
    </section>
  )
}