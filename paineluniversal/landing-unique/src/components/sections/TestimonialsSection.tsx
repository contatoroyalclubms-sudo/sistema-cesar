import React from 'react'
import { motion } from 'framer-motion'
import { Star, Quote, ArrowRight } from 'lucide-react'
import { Card, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { useIntersectionObserver } from '@/hooks/useIntersectionObserver'

interface Testimonial {
  name: string
  role: string
  company: string
  content: string
  rating: number
  avatar: string
  companyLogo?: string
  metrics?: {
    label: string
    value: string
  }
}

const testimonials: Testimonial[] = [
  {
    name: 'Ana Carolina Santos',
    role: 'Diretora de Eventos',
    company: 'EventMaster Brasil',
    content: 'O Unique transformou completamente nossa operação. Em 6 meses, aumentamos nossa receita em 280% e reduzimos o tempo de setup dos eventos em 70%. A plataforma é intuitiva e o suporte é excepcional.',
    rating: 5,
    avatar: 'https://images.unsplash.com/photo-1494790108755-2616b612b5c2?w=150&h=150&fit=crop&crop=face',
    metrics: {
      label: 'Aumento em receita',
      value: '+280%'
    }
  },
  {
    name: 'Roberto Silva',
    role: 'CEO',
    company: 'Mega Eventos',
    content: 'Testamos várias plataformas antes do Unique. A diferença é gritante: interface moderna, funcionalidades avançadas e, principalmente, resultados reais. Nossos clientes ficaram impressionados com a experiência.',
    rating: 5,
    avatar: 'https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=150&h=150&fit=crop&crop=face',
    metrics: {
      label: 'NPS Score',
      value: '96'
    }
  },
  {
    name: 'Mariana Oliveira',
    role: 'Coordenadora de Marketing',
    company: 'Live Experience',
    content: 'A automação do Unique nos permitiu focar no que realmente importa: criar experiências únicas. Os relatórios em tempo real são um game-changer para tomada de decisões estratégicas.',
    rating: 5,
    avatar: 'https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=150&h=150&fit=crop&crop=face',
    metrics: {
      label: 'Tempo economizado',
      value: '15h/semana'
    }
  },
  {
    name: 'Carlos Eduardo',
    role: 'Gerente de Operações',
    company: 'Show Time Eventos',
    content: 'Implementamos o Unique em apenas 2 dias e já no primeiro evento vimos a diferença. Check-in mais rápido, vendas online integradas e controle total. Simplesmente revolucionário!',
    rating: 5,
    avatar: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150&h=150&fit=crop&crop=face',
    metrics: {
      label: 'Redução no check-in',
      value: '85%'
    }
  },
  {
    name: 'Júlia Mendes',
    role: 'Produtora Executiva',
    company: 'Premium Events',
    content: 'O ROI do Unique é impressionante. Em 3 meses, pagamos o investimento e ainda tivemos lucro 200% superior aos eventos anteriores. A ferramenta é essencial para qualquer produtor sério.',
    rating: 5,
    avatar: 'https://images.unsplash.com/photo-1534751516642-a1af1ef26a56?w=150&h=150&fit=crop&crop=face',
    metrics: {
      label: 'ROI em 3 meses',
      value: '+200%'
    }
  },
  {
    name: 'Fernando Costa',
    role: 'Diretor Comercial',
    company: 'Excellence Congressos',
    content: 'Unique não é apenas um sistema, é um parceiro estratégico. A equipe de suporte é extraordinária e as funcionalidades atendem 100% das nossas necessidades. Recomendo sem hesitar.',
    rating: 5,
    avatar: 'https://images.unsplash.com/photo-1560250097-0b93528c311a?w=150&h=150&fit=crop&crop=face',
    metrics: {
      label: 'Satisfação da equipe',
      value: '100%'
    }
  }
]

const TestimonialCard = ({ testimonial, index }: { testimonial: Testimonial; index: number }) => {
  const { ref, isIntersecting } = useIntersectionObserver({ threshold: 0.3 })

  return (
    <motion.div
      ref={ref}
      initial={{ opacity: 0, y: 50, rotateY: -10 }}
      animate={isIntersecting ? { opacity: 1, y: 0, rotateY: 0 } : {}}
      transition={{ duration: 0.8, delay: index * 0.15 }}
      whileHover={{ 
        scale: 1.02,
        rotateY: 2,
        transition: { duration: 0.3 }
      }}
      className="group perspective-1000"
    >
      <Card className="h-full border-2 border-transparent hover:border-primary/20 transition-all duration-300 hover:shadow-2xl hover:shadow-primary/10 transform-gpu">
        <CardContent className="p-8">
          {/* Quote Icon */}
          <Quote className="h-8 w-8 text-primary/30 mb-4 group-hover:text-primary/60 transition-colors" />
          
          {/* Rating */}
          <div className="flex items-center gap-1 mb-4">
            {[...Array(testimonial.rating)].map((_, i) => (
              <Star key={i} className="h-4 w-4 fill-yellow-400 text-yellow-400" />
            ))}
          </div>
          
          {/* Content */}
          <p className="text-muted-foreground mb-6 leading-relaxed text-lg">
            "{testimonial.content}"
          </p>
          
          {/* Metrics */}
          {testimonial.metrics && (
            <div className="bg-primary/5 rounded-lg p-4 mb-6 border border-primary/10">
              <div className="text-2xl font-bold text-primary mb-1">
                {testimonial.metrics.value}
              </div>
              <div className="text-sm text-muted-foreground">
                {testimonial.metrics.label}
              </div>
            </div>
          )}
          
          {/* Author */}
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 rounded-full overflow-hidden ring-2 ring-primary/20 group-hover:ring-primary/40 transition-all">
              <img 
                src={testimonial.avatar} 
                alt={testimonial.name}
                className="w-full h-full object-cover"
                loading="lazy"
              />
            </div>
            <div>
              <div className="font-semibold text-foreground group-hover:text-primary transition-colors">
                {testimonial.name}
              </div>
              <div className="text-sm text-muted-foreground">
                {testimonial.role}
              </div>
              <div className="text-sm font-medium text-primary">
                {testimonial.company}
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </motion.div>
  )
}

const TrustBadges = () => {
  const { ref, isIntersecting } = useIntersectionObserver({ threshold: 0.5 })
  
  const stats = [
    { value: '50,000+', label: 'Eventos Realizados' },
    { value: '2.5M+', label: 'Ingressos Processados' },
    { value: '98.7%', label: 'Satisfação dos Clientes' },
    { value: '24/7', label: 'Suporte Especializado' }
  ]

  return (
    <motion.div
      ref={ref}
      initial={{ opacity: 0, y: 30 }}
      animate={isIntersecting ? { opacity: 1, y: 0 } : {}}
      transition={{ duration: 0.8 }}
      className="text-center"
    >
      <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
        {stats.map((stat, index) => (
          <motion.div
            key={stat.label}
            initial={{ opacity: 0, scale: 0.8 }}
            animate={isIntersecting ? { opacity: 1, scale: 1 } : {}}
            transition={{ duration: 0.6, delay: index * 0.1 }}
            className="group"
          >
            <div className="text-4xl font-bold text-primary mb-2 group-hover:scale-110 transition-transform">
              {stat.value}
            </div>
            <div className="text-muted-foreground">{stat.label}</div>
          </motion.div>
        ))}
      </div>
    </motion.div>
  )
}

export function TestimonialsSection() {
  const { ref, isIntersecting } = useIntersectionObserver({ threshold: 0.1 })

  return (
    <section ref={ref} className="py-20 bg-background">
      <div className="container mx-auto px-4">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={isIntersecting ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.8 }}
          className="text-center mb-16"
        >
          <span className="text-primary font-semibold text-sm uppercase tracking-wide mb-2 block">
            Depoimentos Reais
          </span>
          <h2 className="text-4xl md:text-6xl font-bold font-display mb-6">
            O que Nossos
            <span className="gradient-text"> Clientes Dizem</span>
          </h2>
          <p className="text-xl text-muted-foreground max-w-3xl mx-auto">
            Histórias reais de transformação e sucesso. Descubra por que mais de 10.000 
            organizadores confiam no Unique para revolucionar seus eventos.
          </p>
        </motion.div>

        {/* Trust Badges */}
        <div className="mb-16">
          <TrustBadges />
        </div>

        {/* Testimonials Grid */}
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8 mb-16">
          {testimonials.map((testimonial, index) => (
            <TestimonialCard 
              key={`${testimonial.name}-${testimonial.company}`} 
              testimonial={testimonial} 
              index={index} 
            />
          ))}
        </div>

        {/* CTA */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={isIntersecting ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.8, delay: 0.5 }}
          className="text-center"
        >
          <Card className="max-w-2xl mx-auto border-2 border-primary/20 bg-gradient-to-br from-primary/5 via-purple-500/5 to-pink-500/5 overflow-hidden">
            <div className="absolute inset-0 bg-gradient-to-br from-primary/10 to-transparent opacity-50" />
            <CardContent className="relative p-8">
              <h3 className="text-2xl font-bold mb-4">
                Junte-se aos Líderes do Mercado
              </h3>
              <p className="text-muted-foreground mb-6 text-lg">
                Mais de 10.000 organizadores já descobriram o poder do Unique. 
                Seja o próximo a revolucionar seus eventos!
              </p>
              <div className="flex flex-col sm:flex-row gap-4 justify-center">
                <Button size="lg" variant="gradient" className="group">
                  Começar Agora
                  <ArrowRight className="ml-2 h-5 w-5 group-hover:translate-x-1 transition-transform" />
                </Button>
                <Button size="lg" variant="outline">
                  Falar com Especialista
                </Button>
              </div>
            </CardContent>
          </Card>
        </motion.div>
      </div>
    </section>
  )
}