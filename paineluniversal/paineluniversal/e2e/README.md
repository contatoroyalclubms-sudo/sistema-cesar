# 🧪 Testes E2E com Playwright

Suíte completa de testes End-to-End para o Painel Universal.

## 🚀 Instalação

```bash
cd e2e
npm install
npx playwright install  # Instala navegadores
```

## ⚙️ Configuração

1. Copie o arquivo de ambiente:
```bash
cp .env.example .env
```

2. Configure as variáveis de ambiente conforme necessário.

## 🎯 Executando Testes

### Todos os testes
```bash
npm test
```

### Modo visual (com navegador aberto)
```bash
npm run test:headed
```

### Modo debug
```bash
npm run test:debug
```

### Interface gráfica
```bash
npm run test:ui
```

### Testes específicos por tag
```bash
npm run test:critical   # Apenas testes críticos
npm run test:smoke      # Apenas smoke tests
```

### Testes por módulo
```bash
npm run test:auth       # Testes de autenticação
npm run test:eventos    # Testes de eventos
npm run test:pdv        # Testes do PDV
npm run test:checkin    # Testes de check-in
npm run test:full       # Fluxo completo
```

### Testes por navegador
```bash
npm run test:chrome     # Chrome
npm run test:firefox    # Firefox
npm run test:safari     # Safari/WebKit
npm run test:mobile     # Mobile
```

## 📊 Relatórios

Após executar os testes:
```bash
npm run test:report
```

Os relatórios são gerados em:
- HTML: `playwright-report/index.html`
- JSON: `test-results/results.json`
- JUnit XML: `test-results/junit.xml`

## 🏷️ Tags de Teste

- `@critical` - Testes críticos que devem sempre passar
- `@smoke` - Testes rápidos de sanidade
- `@regression` - Testes de regressão completos
- `@visual` - Testes com comparação visual
- `@api` - Testes de API
- `@performance` - Testes de performance

## 📁 Estrutura

```
e2e/
├── tests/
│   ├── fixtures/
│   │   ├── test-data.ts      # Dados e factories
│   │   └── page-objects.ts   # Page Objects
│   ├── auth.spec.ts          # Testes de autenticação
│   ├── eventos.spec.ts       # Testes de eventos
│   ├── checkin.spec.ts       # Testes de check-in
│   ├── pdv.spec.ts           # Testes do PDV
│   └── full-flow.spec.ts     # Fluxo completo
├── test-results/              # Resultados dos testes
├── playwright-report/         # Relatório HTML
├── playwright.config.ts       # Configuração
└── package.json              # Dependências
```

## 🔧 Page Objects

Usamos o padrão Page Object para organizar os testes:

```typescript
// Exemplo de uso
import { LoginPage } from './fixtures/page-objects';

const loginPage = new LoginPage(page);
await loginPage.goto();
await loginPage.login('123.456.789-09', 'senha123');
await loginPage.expectLoggedIn();
```

## 🏭 Test Factories

Geramos dados aleatórios para testes:

```typescript
import { TestDataFactory } from './fixtures/test-data';

const user = TestDataFactory.generateUser();
const evento = TestDataFactory.generateEvento();
const produto = TestDataFactory.generateProduto();
```

## 🐛 Debug

### Pausar execução
```typescript
await page.pause();  // Pausa e abre inspector
```

### Screenshots
```typescript
await page.screenshot({ path: 'debug.png' });
```

### Traces
```bash
npx playwright show-trace trace.zip
```

## 🚦 CI/CD

### GitHub Actions
```yaml
- name: Run E2E tests
  run: |
    npm ci
    npx playwright install --with-deps
    npm run test:ci
```

### Docker
```dockerfile
FROM mcr.microsoft.com/playwright:v1.40.0-focal
WORKDIR /tests
COPY . .
RUN npm ci
CMD ["npm", "test"]
```

## 📈 Métricas de Teste

### Cobertura atual:
- **Autenticação**: 100% ✅
- **Eventos**: 85% 🟡
- **Check-in**: 90% 🟢
- **PDV**: 80% 🟡
- **Fluxo Completo**: 95% 🟢

### Tempo de execução:
- **Smoke Tests**: ~30s
- **Critical Tests**: ~2min
- **Full Suite**: ~10min
- **Parallel**: ~3min (4 workers)

## 🎯 Boas Práticas

1. **Use data-testid**: Para seletores estáveis
```html
<button data-testid="submit-button">Submit</button>
```

2. **Aguarde elementos**: Sempre use waitFor
```typescript
await page.waitForSelector('.elemento');
```

3. **Testes isolados**: Cada teste deve ser independente
```typescript
test.beforeEach(async () => {
  // Setup limpo
});
```

4. **Assertions claras**: Use expects descritivos
```typescript
await expect(page.locator('h1')).toHaveText('Dashboard');
```

## 🔍 Troubleshooting

### Erro: "Browser not installed"
```bash
npx playwright install
```

### Erro: "Timeout exceeded"
Aumente o timeout no config ou teste específico:
```typescript
test.setTimeout(60000);  // 60 segundos
```

### Erro: "Element not visible"
Verifique se o elemento está realmente visível:
```typescript
await page.waitForSelector('.elemento', { state: 'visible' });
```

## 📚 Recursos

- [Playwright Docs](https://playwright.dev)
- [Best Practices](https://playwright.dev/docs/best-practices)
- [API Reference](https://playwright.dev/docs/api/class-playwright)
- [VS Code Extension](https://marketplace.visualstudio.com/items?itemName=ms-playwright.playwright)

## 🤝 Contribuindo

1. Crie testes para novas features
2. Mantenha Page Objects atualizados
3. Use tags apropriadas (@critical, @smoke, etc)
4. Documente casos de teste complexos
5. Rode os testes antes de commitar

---

**Dica**: Use o Playwright Codegen para gerar testes rapidamente:
```bash
npm run test:codegen
```