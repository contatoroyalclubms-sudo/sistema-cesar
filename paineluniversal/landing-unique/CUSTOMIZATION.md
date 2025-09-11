# 🎨 Guia de Personalização - Landing Page Unique

## 📋 Índice
- [Alterando Textos](#alterando-textos)
- [Modificando Imagens](#modificando-imagens)
- [Personalizando Cores](#personalizando-cores)
- [Configurando Formulários](#configurando-formulários)
- [Adicionando Seções](#adicionando-seções)
- [SEO e Meta Tags](#seo-e-meta-tags)

## 🔤 Alterando Textos

### Hero Section - Título Principal
**Arquivo:** `src/components/sections/HeroSection.tsx`
**Linha:** ~45-52

```typescript
<h1 className="text-5xl md:text-7xl font-bold font-display mb-6 leading-tight">
  SEU NOVO TÍTULO
  <br />
  <span className="bg-gradient-to-r from-blue-200 via-purple-200 to-pink-200 bg-clip-text text-transparent">
    TEXTO COM GRADIENTE
  </span>
</h1>
```

### Subtítulo e Descrição
**Linha:** ~54-59

```typescript
<p className="text-xl md:text-2xl mb-8 max-w-3xl mx-auto leading-relaxed text-white/90">
  Sua nova descrição aqui. Use <strong>negrito</strong> para destacar pontos importantes.
</p>
```

### Estatísticas
**Linha:** ~85-95

```typescript
{[
  { number: '50K+', label: 'Seus Eventos', icon: Zap },
  { number: '2M+', label: 'Seus Números', icon: Users },
  { number: '98%', label: 'Sua Taxa', icon: Star },
]}
```

## 🖼️ Modificando Imagens

### Logo e Favicon
1. **Favicon:** Substitua `public/favicon.svg`
2. **Logo no Header:** Modifique o ícone em `src/components/Header.tsx` linha ~35

```typescript
<div className="w-8 h-8 bg-gradient-to-br from-blue-600 to-purple-600 rounded-lg flex items-center justify-center">
  <SeuIcone className="h-5 w-5 text-white" />
</div>
```

### Imagens de Depoimentos
**Arquivo:** `src/components/sections/TestimonialsSection.tsx`

Substitua as URLs do Unsplash por suas próprias imagens:

```typescript
{
  name: 'Ana Carolina Santos',
  avatar: 'https://seusite.com/foto-ana.jpg', // ← Altere aqui
  // ...
}
```

**Dica:** Use imagens quadradas 150x150px para melhor resultado.

### Imagem Open Graph (Redes Sociais)
Substitua `public/og-image.png` por uma imagem 1200x630px com sua marca.

## 🎨 Personalizando Cores

### Esquema de Cores Principal
**Arquivo:** `src/index.css`
**Linhas:** 4-20 (light) e 22-38 (dark)

```css
:root {
  --primary: 221.2 83.2% 53.3%;     /* Cor principal (azul) */
  --secondary: 210 40% 96%;          /* Cor secundária */
  --accent: 210 40% 96%;             /* Cor de destaque */
  /* Para alterar: use o formato HSL (matiz saturação luminosidade) */
}
```

### Calculadora de Cores HSL
Use ferramentas online como:
- [HSL Color Picker](https://hslpicker.com/)
- [Coolors.co](https://coolors.co/)

**Exemplo - Mudando para Verde:**
```css
:root {
  --primary: 142 71% 45%;  /* Verde #16a085 */
}

.dark {
  --primary: 142 71% 65%;  /* Verde mais claro para dark mode */
}
```

### Gradientes Personalizados
**Arquivo:** `src/components/sections/HeroSection.tsx`

```typescript
// Altere as classes de gradiente
<span className="bg-gradient-to-r from-green-200 via-blue-200 to-purple-200 bg-clip-text text-transparent">
```

## 📝 Configurando Formulários

### Campos do Formulário de Lead
**Arquivo:** `src/components/sections/LeadFormSection.tsx`
**Linha:** ~215+

**Adicionando um novo campo:**

```typescript
{/* Novo campo - Empresa */}
<div className="space-y-2">
  <label className="text-sm font-medium flex items-center gap-2">
    <Building className="h-4 w-4" />
    Nome da Empresa *
  </label>
  <Input
    type="text"
    placeholder="Sua empresa"
    value={formData.empresa || ''}
    onChange={(e) => handleInputChange('empresa', e.target.value)}
    className={errors.empresa ? 'border-red-500' : ''}
  />
  {errors.empresa && (
    <p className="text-red-500 text-sm">{errors.empresa}</p>
  )}
</div>
```

**Não esqueça de:**
1. Adicionar o campo ao tipo `FormData` (linha ~25)
2. Adicionar validação se necessário

### Integrando com seu Backend
Modifique a função `handleSubmit` (linha ~90):

```typescript
const handleSubmit = async (e: React.FormEvent) => {
  e.preventDefault()
  
  if (!validateForm()) return
  setIsSubmitting(true)

  try {
    // Sua integração aqui
    const response = await fetch('https://seubackend.com/api/leads', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(formData),
    })
    
    if (response.ok) {
      setIsSubmitted(true)
    }
  } catch (error) {
    console.error('Erro ao enviar:', error)
  } finally {
    setIsSubmitting(false)
  }
}
```

## 🆕 Adicionando Seções

### Criando uma Nova Seção
1. **Crie o arquivo:** `src/components/sections/MinhaSecao.tsx`

```typescript
import React from 'react'
import { motion } from 'framer-motion'
import { useIntersectionObserver } from '@/hooks/useIntersectionObserver'

export function MinhaSecao() {
  const { ref, isIntersecting } = useIntersectionObserver({ threshold: 0.2 })

  return (
    <section ref={ref} className="py-20 bg-background">
      <div className="container mx-auto px-4">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={isIntersecting ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.8 }}
          className="text-center"
        >
          <h2 className="text-4xl font-bold mb-6">
            Minha Nova Seção
          </h2>
          <p className="text-muted-foreground text-lg">
            Conteúdo da seção aqui...
          </p>
        </motion.div>
      </div>
    </section>
  )
}
```

2. **Adicione ao App.tsx:**

```typescript
import { MinhaSecao } from '@/components/sections/MinhaSecao'

// Dentro do <main>:
<MinhaSecao />
```

3. **Adicione ao menu** (opcional) em `Header.tsx`:

```typescript
const navigation = [
  { name: 'Minha Seção', href: '#minha-secao' },
  // ...
]
```

### Padrões Recomendados
- Use sempre `useIntersectionObserver` para animações
- Mantenha `py-20` para espaçamento consistente
- Use `container mx-auto px-4` para largura responsiva
- Aplique `motion.div` para animações de entrada

## 🔍 SEO e Meta Tags

### Configuração Básica
**Arquivo:** `src/components/SEO.tsx`
**Linha:** ~15-22

```typescript
const defaultSEO = {
  title: 'Seu Título - Sua Empresa',
  description: 'Sua descrição otimizada para SEO com 150-160 caracteres',
  keywords: 'palavra1, palavra2, palavra3, long tail keywords',
  image: '/sua-og-image.png',
  url: 'https://seudominio.com',
  type: 'website'
}
```

### Meta Tags Específicas por Página
Se você adicionar outras páginas, pode usar o SEO assim:

```typescript
<SEO 
  title="Página Específica"
  description="Descrição específica desta página"
  keywords="palavras, especificas, desta, pagina"
/>
```

### Structured Data (Rich Snippets)
Já incluído no `SEO.tsx`, mas você pode personalizar (linha ~85):

```typescript
{
  "@context": "https://schema.org",
  "@type": "SoftwareApplication", // ou "Organization", "Product", etc.
  "name": "Seu Produto",
  "description": "Sua descrição",
  // ...
}
```

## 🎯 Dicas de Conversão

### Call-to-Action (CTA)
**Princípios para CTAs efetivos:**

1. **Verbos de ação:** "Começar", "Descobrir", "Transformar"
2. **Urgência:** "Agora", "Hoje", "Grátis por tempo limitado"
3. **Benefício claro:** "Teste grátis por 30 dias"

**Exemplo de CTA otimizado:**
```typescript
<Button size="xl" variant="gradient" className="group">
  Transformar Meus Eventos Agora
  <ArrowRight className="ml-2 h-5 w-5 group-hover:translate-x-1 transition-transform" />
</Button>
```

### Prova Social
Adicione números reais aos seus depoimentos e estatísticas:

```typescript
{
  name: 'João Silva',
  company: 'Rock Fest SP',
  content: 'Aumentamos nossas vendas em 340% no primeiro mês...',
  metrics: {
    label: 'Aumento real em vendas',
    value: '+340%'  // ← Use números reais e específicos
  }
}
```

## 📱 Responsividade

### Breakpoints Tailwind
- `sm:` - 640px+
- `md:` - 768px+
- `lg:` - 1024px+
- `xl:` - 1280px+
- `2xl:` - 1536px+

### Testando Responsividade
1. Use as ferramentas de desenvolvedor do navegador
2. Teste em dispositivos reais
3. Use ferramentas como [BrowserStack](https://browserstack.com)

### Exemplo de Classes Responsivas
```typescript
<h1 className="text-3xl sm:text-4xl md:text-5xl lg:text-6xl xl:text-7xl">
  Título que cresce conforme a tela
</h1>

<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
  {/* 1 coluna no mobile, 2 no tablet, 3 no desktop */}
</div>
```

## 🚀 Performance

### Otimizando Imagens
1. **Formato:** Use WebP quando possível
2. **Tamanho:** Máximo 1MB por imagem
3. **Dimensões:** Não exceda 1920px de largura
4. **Lazy Loading:** Já implementado automaticamente

### Fonts Optimization
As fontes já estão otimizadas, mas se adicionar novas:

```html
<!-- No index.html -->
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=SuaFont:wght@400;500;600;700&display=swap" rel="stylesheet">
```

## ❓ FAQ de Personalização

**P: Como alterar a fonte?**
R: Modifique a importação no `index.html` e atualize o `tailwind.config.js`

**P: Posso usar outras bibliotecas de ícones?**
R: Sim! Substitua Lucide React por Heroicons, React Icons, etc.

**P: Como adicionar um vídeo de fundo?**
R: Use o elemento `<video>` no Hero Section com autoplay muted

**P: Posso integrar com meu CRM?**
R: Sim! Modifique o `handleSubmit` do formulário para chamar sua API

**P: Como traduzir para outros idiomas?**
R: Use bibliotecas como `react-i18next` ou crie arquivos de tradução simples

---

**💡 Dica:** Sempre teste suas modificações em diferentes dispositivos e navegadores antes de publicar!

**🆘 Precisa de ajuda?** Entre em contato: contato@unique.com.br