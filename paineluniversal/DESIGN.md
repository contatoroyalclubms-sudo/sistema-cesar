# 🎨 Sistema Universal de Eventos - Guia de Design

## 📋 Resumo das Atualizações

O **Sistema Universal de Eventos - CPF Seguro** foi completamente modernizado com um design premium, responsivo e acessível, seguindo as melhores práticas de UX/UI.

### ✅ Implementações Concluídas

- ✅ **Modo Dark e Modo Claro** alternáveis pelo usuário
- ✅ **Layout totalmente responsivo** (desktop, tablet, mobile)
- ✅ **PWA otimizado** para acesso via celular
- ✅ **Componentes modernos** com animações suaves (Framer Motion)
- ✅ **Tipografia premium** (Inter + Poppins)
- ✅ **Design consistente** em todas as páginas
- ✅ **Cores otimizadas** para acessibilidade (WCAG 2.1)
- ✅ **Navegação retrátil** com sidebar colapsável
- ✅ **Dashboard visual** com gráficos dinâmicos
- ✅ **Interface 100% em português**

---

## 🎨 Sistema de Cores

### Paleta Principal
```css
/* Modo Claro */
:root {
  --primary: 221.2 83.2% 53.3%;        /* #007BFF - Azul principal */
  --background: 0 0% 100%;              /* #FFFFFF - Branco */
  --foreground: 224 71.4% 4.1%;         /* #0F172A - Azul escuro */
  --card: 0 0% 100%;                    /* #FFFFFF */
  --border: 214.3 31.8% 91.4%;          /* #E2E8F0 */
}

/* Modo Escuro */
.dark {
  --primary: 221.2 83.2% 53.3%;        /* #007BFF - Azul (mantém) */
  --background: 224 71.4% 4.1%;         /* #0F172A - Azul escuro */
  --foreground: 210 40% 98%;            /* #F8FAFC - Branco suave */
  --card: 224 71.4% 4.1%;               /* #0F172A */
  --border: 215 27.9% 16.9%;            /* #334155 */
}
```

### Como Alterar Cores
1. **Cor Principal (Azul)**: Altere `--primary` em `src/App.css`
2. **Cores de Fundo**: Modifique `--background` e `--card`
3. **Bordas**: Ajuste `--border` para elementos visuais
4. **Texto**: Configure `--foreground` e `--muted-foreground`

---

## 🎯 Tipografia

### Fontes Utilizadas
- **Headings**: `Poppins` (600, 700) - Para títulos e elementos de destaque
- **Body**: `Inter` (400, 500, 600) - Para texto geral e interface

### Como Alterar Fontes

1. **Instalar nova fonte**:
```bash
npm install @fontsource/sua-fonte
```

2. **Importar em App.css**:
```css
@import '@fontsource/sua-fonte/400.css';
```

3. **Configurar no Tailwind** (tailwind.config.js):
```javascript
fontFamily: {
  heading: ['Sua-Fonte', 'sans-serif'],
  body: ['Sua-Fonte', 'sans-serif'],
}
```

### Classes Disponíveis
- `.font-heading` - Para títulos (usa Poppins)
- `.font-body` - Para texto geral (usa Inter)

---

## 📐 Espaçamentos

### Sistema de Espaçamento (Tailwind)
```css
/* Pequeno */
gap-2, p-2, m-2    /* 8px */
gap-4, p-4, m-4    /* 16px */

/* Médio */
gap-6, p-6, m-6    /* 24px */
gap-8, p-8, m-8    /* 32px */

/* Grande */
gap-12, p-12, m-12 /* 48px */
gap-16, p-16, m-16 /* 64px */
```

### Como Alterar Espaçamentos
Modifique as classes Tailwind nos componentes:
- `gap-X` para espaços entre elementos
- `p-X` para padding interno
- `m-X` para margin externa

---

## 🎭 Animações e Transições

### Durações Configuradas
```css
:root {
  --animation-fast: 150ms;      /* Hover effects */
  --animation-normal: 300ms;    /* Transições gerais */
  --animation-slow: 500ms;      /* Animações complexas */
}
```

### Classes de Animação
- `.animate-fade-in` - Entrada suave
- `.animate-slide-in-right` - Deslizar da direita
- `.animate-slide-in-left` - Deslizar da esquerda
- `.premium-card` - Card com hover premium

### Como Customizar Animações
1. **Editar duração** em `src/App.css`
2. **Criar nova animação**:
```css
@keyframes minha-animacao {
  from { transform: scale(0.9); opacity: 0; }
  to { transform: scale(1); opacity: 1; }
}

.minha-classe {
  animation: minha-animacao 0.3s ease-out;
}
```

---

## 🎨 Componentes Premium

### Cards Premium
```jsx
<Card className="premium-card">
  <CardContent>
    {/* Conteúdo */}
  </CardContent>
</Card>
```
- **Efeito**: Sombra suave + hover elevation
- **Bordas**: Arredondadas (12px)
- **Background**: Translúcido com blur

### Botões com Gradiente
```jsx
<Button className="bg-gradient-to-r from-primary to-primary/90">
  Botão Premium
</Button>
```

### Sombras Personalizadas
- `.shadow-premium-sm` - Sombra pequena
- `.shadow-premium-md` - Sombra média
- `.shadow-premium-lg` - Sombra grande
- `.shadow-premium-xl` - Sombra extra grande

---

## 📱 Responsividade

### Breakpoints Configurados
```css
/* Tailwind Breakpoints */
sm: 640px   /* Tablet pequeno */
md: 768px   /* Tablet */
lg: 1024px  /* Desktop pequeno */
xl: 1280px  /* Desktop */
2xl: 1536px /* Desktop grande */
```

### Classes Responsivas
```jsx
<div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4">
  {/* Mobile: 1 coluna, Tablet: 2 colunas, Desktop: 4 colunas */}
</div>
```

### Sidebar Retrátil
- **Desktop**: Sidebar fixa com botão de collapse
- **Mobile**: Sidebar overlay com backdrop
- **Estados**: Expandida (280px) / Colapsada (80px)

---

## 🌙 Tema Dark/Light

### Implementação
O sistema usa CSS variables e a classe `.dark` no elemento raiz:

```tsx
// Usar o hook
const { theme, effectiveTheme, setTheme, toggleTheme } = useTheme();

// Alternar tema
<ThemeToggle />
```

### Customização de Cores por Tema
```css
:root {
  --minha-cor-light: #ffffff;
}

.dark {
  --minha-cor-light: #000000;
}

.minha-classe {
  background-color: hsl(var(--minha-cor-light));
}
```

---

## ♿ Acessibilidade (WCAG 2.1)

### Implementações
- ✅ **Contraste adequado**: Ratio mínimo 4.5:1
- ✅ **Focus visível**: Outline azul em todos os elementos interativos
- ✅ **Navegação por teclado**: Tab navigation funcional
- ✅ **ARIA labels**: Labels descritivos em botões e inputs
- ✅ **Semantic HTML**: Uso correto de headings e landmarks

### Testes de Acessibilidade
```bash
# Instalar ferramenta de teste
npm install -g axe-cli

# Testar acessibilidade
axe http://localhost:5173
```

---

## 📱 PWA (Progressive Web App)

### Configurações
```typescript
// vite.config.ts
VitePWA({
  manifest: {
    name: 'Sistema Universal de Eventos - CPF Seguro',
    short_name: 'Eventos Universal',
    theme_color: '#007BFF',
    background_color: '#ffffff',
    display: 'standalone'
  }
})
```

### Recursos PWA
- ✅ **Instalável** no desktop e mobile
- ✅ **Offline cache** para recursos estáticos
- ✅ **Service worker** para atualizações automáticas
- ✅ **Ícones** otimizados para diferentes dispositivos

---

## 🎯 Gráficos e Visualizações

### Biblioteca: Recharts
```jsx
import { LineChart, BarChart, PieChart } from 'recharts';

// Configuração com tema
<ResponsiveContainer width="100%" height={300}>
  <AreaChart data={dados}>
    <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
    <XAxis stroke="hsl(var(--muted-foreground))" />
    <YAxis stroke="hsl(var(--muted-foreground))" />
    <Area
      type="monotone"
      dataKey="vendas"
      stroke="#007BFF"
      fill="url(#gradient)"
    />
  </AreaChart>
</ResponsiveContainer>
```

### Cores dos Gráficos
- **Primária**: `#007BFF` (azul sistema)
- **Secundária**: `#0056D6` (azul escuro)
- **Gradientes**: Configurados automaticamente

---

## 🔧 Manutenção e Customização

### Estrutura de Arquivos
```
src/
├── components/
│   ├── ui/              # Componentes base (shadcn/ui)
│   ├── theme/           # Sistema de temas
│   ├── layout/          # Layout e navegação
│   └── dashboard/       # Componentes específicos
├── contexts/
│   ├── AuthContext.tsx  # Autenticação
│   └── ThemeContext.tsx # Gerenciamento de tema
├── hooks/               # Hooks customizados
└── App.css             # Estilos globais e CSS variables
```

### Comandos Úteis
```bash
# Desenvolvimento
npm run dev

# Build de produção
npm run build

# Preview do build
npm run preview

# Linting
npm run lint
```

### Adicionando Novos Componentes
1. **Usar shadcn/ui**: `npx shadcn-ui add [componente]`
2. **Aplicar classes premium**: `.premium-card`, `.animate-fade-in`
3. **Seguir padrões**: TypeScript + Framer Motion + Tailwind

---

## 🚀 Performance

### Otimizações Implementadas
- ✅ **Code splitting** automático por rotas
- ✅ **Lazy loading** de componentes pesados
- ✅ **Compressão** de assets
- ✅ **Caching** otimizado (PWA)
- ✅ **Bundle analysis** para monitoramento

### Métricas Target
- **First Contentful Paint**: < 1.5s
- **Largest Contentful Paint**: < 2.5s
- **Cumulative Layout Shift**: < 0.1
- **Bundle size**: < 1MB comprimido

---

## 📞 Suporte

Para dúvidas sobre customização ou problemas:

1. **Documentação Tailwind**: https://tailwindcss.com/docs
2. **Framer Motion**: https://framer.com/motion
3. **Radix UI**: https://radix-ui.com
4. **Recharts**: https://recharts.org

---

*Documentação criada para o Sistema Universal de Eventos - CPF Seguro*  
*Design System Version 2.0 | Dezembro 2024*