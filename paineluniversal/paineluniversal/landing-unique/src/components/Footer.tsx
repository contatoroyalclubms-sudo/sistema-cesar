import React from 'react'
import { motion } from 'framer-motion'
import { 
  Zap, 
  Mail, 
  Phone, 
  MapPin, 
  Facebook, 
  Twitter, 
  Instagram, 
  Linkedin,
  Youtube,
  ArrowRight,
  Heart
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { useIntersectionObserver } from '@/hooks/useIntersectionObserver'

const footerSections = {
  produto: {
    title: 'Produto',
    links: [
      { name: 'Recursos', href: '#features' },
      { name: 'Preços', href: '#pricing' },
      { name: 'Demo', href: '#product-demo' },
      { name: 'Integrações', href: '#integrations' },
      { name: 'API', href: '#api' }
    ]
  },
  empresa: {
    title: 'Empresa',
    links: [
      { name: 'Sobre nós', href: '#about' },
      { name: 'Carreiras', href: '#careers' },
      { name: 'Imprensa', href: '#press' },
      { name: 'Parcerias', href: '#partners' },
      { name: 'Blog', href: '#blog' }
    ]
  },
  suporte: {
    title: 'Suporte',
    links: [
      { name: 'Central de Ajuda', href: '#help' },
      { name: 'Documentação', href: '#docs' },
      { name: 'Status', href: '#status' },
      { name: 'Contato', href: '#contact' },
      { name: 'Comunidade', href: '#community' }
    ]
  },
  legal: {
    title: 'Legal',
    links: [
      { name: 'Termos de Uso', href: '#terms' },
      { name: 'Política de Privacidade', href: '#privacy' },
      { name: 'Cookies', href: '#cookies' },
      { name: 'LGPD', href: '#lgpd' },
      { name: 'Compliance', href: '#compliance' }
    ]
  }
}

const socialLinks = [
  { icon: Facebook, href: '#', label: 'Facebook' },
  { icon: Twitter, href: '#', label: 'Twitter' },
  { icon: Instagram, href: '#', label: 'Instagram' },
  { icon: Linkedin, href: '#', label: 'LinkedIn' },
  { icon: Youtube, href: '#', label: 'YouTube' }
]

const contactInfo = [
  {
    icon: Phone,
    text: '+55 (11) 99999-9999',
    href: 'tel:+5511999999999'
  },
  {
    icon: Mail,
    text: 'contato@unique.com.br',
    href: 'mailto:contato@unique.com.br'
  },
  {
    icon: MapPin,
    text: 'São Paulo, SP - Brasil',
    href: '#'
  }
]

export function Footer() {
  const { ref, isIntersecting } = useIntersectionObserver({ threshold: 0.2 })

  const scrollToSection = (href: string) => {
    if (href.startsWith('#')) {
      const elementId = href.replace('#', '')
      const element = document.getElementById(elementId)
      element?.scrollIntoView({ behavior: 'smooth' })
    }
  }

  return (
    <footer ref={ref} className="bg-background border-t border-border">
      {/* Newsletter Section */}
      <motion.div
        initial={{ opacity: 0, y: 30 }}
        animate={isIntersecting ? { opacity: 1, y: 0 } : {}}
        transition={{ duration: 0.8 }}
        className="border-b border-border py-12"
      >
        <div className="container mx-auto px-4">
          <div className="max-w-4xl mx-auto text-center">
            <h3 className="text-2xl md:text-3xl font-bold mb-4">
              Fique por dentro das novidades
            </h3>
            <p className="text-muted-foreground mb-8 text-lg">
              Receba dicas exclusivas, atualizações de produto e insights do mercado 
              diretamente no seu email.
            </p>
            
            <div className="flex flex-col sm:flex-row gap-4 max-w-md mx-auto">
              <Input
                type="email"
                placeholder="Seu melhor email"
                className="flex-1"
              />
              <Button variant="gradient" className="group">
                Inscrever-se
                <ArrowRight className="ml-2 h-4 w-4 group-hover:translate-x-1 transition-transform" />
              </Button>
            </div>
            
            <p className="text-xs text-muted-foreground mt-4">
              Sem spam. Cancele a qualquer momento.
            </p>
          </div>
        </div>
      </motion.div>

      {/* Main Footer Content */}
      <div className="py-16">
        <div className="container mx-auto px-4">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-6 gap-8">
            {/* Brand Section */}
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              animate={isIntersecting ? { opacity: 1, y: 0 } : {}}
              transition={{ duration: 0.8, delay: 0.1 }}
              className="lg:col-span-2"
            >
              <div className="flex items-center gap-2 mb-4">
                <div className="w-8 h-8 bg-gradient-to-br from-blue-600 to-purple-600 rounded-lg flex items-center justify-center">
                  <Zap className="h-5 w-5 text-white" />
                </div>
                <span className="text-xl font-bold font-display">
                  Unique
                </span>
              </div>
              
              <p className="text-muted-foreground mb-6 leading-relaxed">
                A plataforma mais avançada para gestão de eventos. 
                Transformamos ideias em experiências inesquecíveis com 
                tecnologia de ponta e suporte excepcional.
              </p>

              {/* Contact Info */}
              <div className="space-y-3">
                {contactInfo.map((contact, index) => (
                  <motion.a
                    key={index}
                    href={contact.href}
                    initial={{ opacity: 0, x: -20 }}
                    animate={isIntersecting ? { opacity: 1, x: 0 } : {}}
                    transition={{ duration: 0.6, delay: 0.2 + index * 0.1 }}
                    className="flex items-center gap-3 text-sm text-muted-foreground hover:text-foreground transition-colors"
                  >
                    <contact.icon className="h-4 w-4" />
                    {contact.text}
                  </motion.a>
                ))}
              </div>

              {/* Social Links */}
              <div className="flex items-center gap-3 mt-6">
                {socialLinks.map((social, index) => (
                  <motion.a
                    key={social.label}
                    href={social.href}
                    initial={{ opacity: 0, scale: 0.8 }}
                    animate={isIntersecting ? { opacity: 1, scale: 1 } : {}}
                    transition={{ duration: 0.4, delay: 0.5 + index * 0.1 }}
                    className="w-10 h-10 bg-muted hover:bg-primary hover:text-primary-foreground rounded-lg flex items-center justify-center transition-all duration-300 hover:scale-110"
                    aria-label={social.label}
                  >
                    <social.icon className="h-4 w-4" />
                  </motion.a>
                ))}
              </div>
            </motion.div>

            {/* Links Sections */}
            {Object.entries(footerSections).map(([key, section], sectionIndex) => (
              <motion.div
                key={key}
                initial={{ opacity: 0, y: 30 }}
                animate={isIntersecting ? { opacity: 1, y: 0 } : {}}
                transition={{ duration: 0.8, delay: 0.2 + sectionIndex * 0.1 }}
              >
                <h4 className="font-semibold text-foreground mb-4">
                  {section.title}
                </h4>
                <ul className="space-y-3">
                  {section.links.map((link, linkIndex) => (
                    <li key={link.name}>
                      <motion.button
                        initial={{ opacity: 0, x: -10 }}
                        animate={isIntersecting ? { opacity: 1, x: 0 } : {}}
                        transition={{ 
                          duration: 0.4, 
                          delay: 0.3 + sectionIndex * 0.1 + linkIndex * 0.05 
                        }}
                        onClick={() => scrollToSection(link.href)}
                        className="text-sm text-muted-foreground hover:text-foreground transition-colors"
                      >
                        {link.name}
                      </motion.button>
                    </li>
                  ))}
                </ul>
              </motion.div>
            ))}
          </div>
        </div>
      </div>

      {/* Bottom Bar */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={isIntersecting ? { opacity: 1, y: 0 } : {}}
        transition={{ duration: 0.8, delay: 0.6 }}
        className="border-t border-border py-6"
      >
        <div className="container mx-auto px-4">
          <div className="flex flex-col md:flex-row items-center justify-between gap-4">
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <span>© 2024 Unique Events.</span>
              <span>Feito com</span>
              <Heart className="h-4 w-4 text-red-500 fill-current" />
              <span>no Brasil</span>
            </div>
            
            <div className="flex items-center gap-6 text-sm text-muted-foreground">
              <button 
                onClick={() => scrollToSection('#terms')}
                className="hover:text-foreground transition-colors"
              >
                Termos
              </button>
              <button 
                onClick={() => scrollToSection('#privacy')}
                className="hover:text-foreground transition-colors"
              >
                Privacidade
              </button>
              <button 
                onClick={() => scrollToSection('#cookies')}
                className="hover:text-foreground transition-colors"
              >
                Cookies
              </button>
            </div>
          </div>
        </div>
      </motion.div>
    </footer>
  )
}