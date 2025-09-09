# 🚀 Landing Page Unique - Sistema de Gestão de Eventos

## 📋 Visão Geral

Landing page moderna, responsiva e altamente criativa desenvolvida para o sistema Unique - a plataforma mais inovadora de gestão de eventos do Brasil. 

**Objetivo:** Maximizar a conversão de visitantes em leads qualificados através de uma experiência visual impactante, confiável e tecnologicamente avançada.

## ✨ Características Principais

### 🎨 Design Moderno
- **Layout Mobile First** com responsividade total
- **Sistema de Temas** Dark/Light alternável
- **Animações Suaves** com Framer Motion
- **Componentes Premium** usando Radix UI + Tailwind CSS
- **Tipografia Elegante** com Inter e Poppins

### 🔧 Tecnologias Utilizadas
- **React 18** + TypeScript
- **Vite** para build ultra-rápido
- **Tailwind CSS** + shadcn/ui para estilização
- **Framer Motion** para animações
- **Radix UI** para componentes acessíveis
- **React Helmet Async** para SEO
- **Zod** para validação de formulários

### 🎯 Seções Implementadas

1. **Hero Section** - Chamada principal com impacto visual
2. **Apresentação do Produto** - Mockups e demonstrações
3. **Benefícios & Funcionalidades** - Cards animados com recursos
4. **Depoimentos** - Testimoniais reais de clientes
5. **Formulário de Captura** - Lead form otimizado para conversão

## 🚀 Como Executar

### Pré-requisitos
- Node.js 18+ 
- npm ou yarn

### Instalação
```bash
cd landing-unique
npm install
```

### Desenvolvimento
```bash
npm run dev
```
A aplicação estará disponível em `http://localhost:5173`

### Build para Produção
```bash
npm run build
npm run preview  # Para visualizar o build
```

### Lint e Validação
```bash
npm run lint
```

## 📂 Estrutura do Projeto

```
landing-unique/
├── public/                    # Arquivos estáticos
│   ├── favicon.svg           # Favicon otimizado
│   ├── manifest.json         # PWA manifest
│   └── robots.txt           # SEO robots
├── src/
│   ├── components/          # Componentes React
│   │   ├── ui/             # Componentes base (shadcn/ui)
│   │   ├── sections/       # Seções da landing page
│   │   ├── Header.tsx      # Cabeçalho com navegação
│   │   ├── Footer.tsx      # Rodapé completo
│   │   ├── SEO.tsx         # Componente de SEO
│   │   └── ThemeToggle.tsx # Toggle de tema
│   ├── contexts/           # Contextos React
│   │   └── ThemeContext.tsx # Gerenciamento de tema
│   ├── hooks/              # Hooks customizados
│   │   └── useIntersectionObserver.ts # Hook para animações
│   ├── lib/                # Utilitários
│   │   └── utils.ts        # Funções auxiliares
│   ├── App.tsx             # Componente principal
│   ├── main.tsx            # Entrada da aplicação
│   └── index.css           # Estilos globais
├── package.json            # Dependências
├── tailwind.config.js      # Configuração Tailwind
├── tsconfig.json          # Configuração TypeScript
└── vite.config.ts         # Configuração Vite
```

## 🎨 Sistema de Temas

### Tema Claro
- **Cor Primária:** Azul (#3B82F6)
- **Background:** Branco (#FFFFFF)
- **Texto:** Cinza escuro (#1F2937)

### Tema Escuro
- **Cor Primária:** Azul claro (#60A5FA)
- **Background:** Cinza escuro (#0F172A)
- **Texto:** Branco (#F8FAFC)

### Como Personalizar Cores
Edite o arquivo `src/index.css` nas variáveis CSS:

```css
:root {
  --primary: 221.2 83.2% 53.3%;      /* Azul primário */
  --background: 0 0% 100%;            /* Fundo branco */
  --foreground: 222.2 84% 4.9%;      /* Texto escuro */
  /* ... outras variáveis */
}

.dark {
  --primary: 217.2 91.2% 59.8%;      /* Azul claro */
  --background: 222.2 84% 4.9%;      /* Fundo escuro */
  --foreground: 210 40% 98%;         /* Texto claro */
  /* ... outras variáveis */
}
```

## 📝 Personalizando Conteúdo

### 1. Textos e Títulos
Edite os arquivos em `src/components/sections/`:

**Hero Section** (`HeroSection.tsx`):
```typescript
// Alterar título principal
<h1 className="text-5xl md:text-7xl font-bold font-display mb-6 leading-tight">
  Seu Novo Título
  <span className="gradient-text">Aqui</span>
</h1>
```

**Benefícios** (`FeaturesSection.tsx`):
```typescript
// Modificar features array
const features: Feature[] = [
  {
    icon: Zap,
    title: 'Seu Benefício',
    description: 'Sua descrição aqui...',
    color: 'text-yellow-600',
    bgColor: 'bg-yellow-500/10'
  }
  // ...
]
```

### 2. Imagens e Logos
Substitua as imagens em `public/`:
- `favicon.svg` - Ícone do site
- `logo.png` - Logo da empresa
- `og-image.png` - Imagem para redes sociais

### 3. Informações de Contato
Edite o arquivo `Footer.tsx`:
```typescript
const contactInfo = [
  {
    icon: Phone,
    text: 'Seu telefone',
    href: 'tel:seunumero'
  }
  // ...
]
```

### 4. Depoimentos
Modifique o array `testimonials` em `TestimonialsSection.tsx`:
```typescript
const testimonials: Testimonial[] = [
  {
    name: 'Nome do Cliente',
    role: 'Cargo',
    company: 'Empresa',
    content: 'Depoimento...',
    rating: 5,
    avatar: 'url-da-foto'
  }
  // ...
]
```

## 🔧 Configurações Avançadas

### SEO e Meta Tags
Configure SEO em `src/components/SEO.tsx`:
```typescript
const defaultSEO = {
  title: 'Seu Título',
  description: 'Sua descrição...',
  keywords: 'suas, palavras, chave',
  image: '/sua-imagem.png',
  url: 'https://seusite.com'
}
```

### Performance
Para otimizar ainda mais:

1. **Lazy Loading**: Já implementado para imagens
2. **Code Splitting**: Configurado no Vite
3. **Fonts**: Use fonts do Google Fonts já pré-carregadas
4. **Images**: Otimize imagens antes de adicionar (WebP recomendado)

### Analytics
Para adicionar Google Analytics ou similar:

1. Instale a biblioteca:
```bash
npm install @gtag/lib
```

2. Configure no `index.html`:
```html
<!-- Google Analytics -->
<script async src="https://www.googletagmanager.com/gtag/js?id=GA_TRACKING_ID"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'GA_TRACKING_ID');
</script>
```

## 📊 Métricas de Performance

### Lighthouse Score Esperado
- **Performance:** 95+
- **Accessibility:** 100
- **Best Practices:** 100
- **SEO:** 100

### Otimizações Implementadas
- ✅ Lazy loading de imagens
- ✅ Code splitting automático
- ✅ Compressão de assets
- ✅ Preload de fonts críticas
- ✅ Meta tags completas
- ✅ Structured data (JSON-LD)
- ✅ Manifest PWA
- ✅ Service Worker ready

## 🐛 Troubleshooting

### Problemas Comuns

**1. Erro de build com TypeScript**
```bash
# Limpar cache e reinstalar
rm -rf node_modules package-lock.json
npm install
```

**2. Animações não funcionando**
Verifique se o Framer Motion foi instalado:
```bash
npm install framer-motion
```

**3. Estilos não aplicados**
Certifique-se que o Tailwind está configurado:
```bash
npm run build
```

**4. Tema não alternando**
Verifique se o ThemeProvider está envolvendo a aplicação em `App.tsx`.

## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📜 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

## 📞 Suporte

Para dúvidas ou suporte:
- 📧 Email: contato@unique.com.br
- 💬 WhatsApp: (11) 99999-9999
- 🌐 Website: https://unique-events.com

---

**Desenvolvido com ❤️ para revolucionar eventos no Brasil**