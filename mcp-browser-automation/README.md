# MCP Browser Automation Server

Um servidor MCP (Model Context Protocol) completo para automação de navegador usando Playwright.

## Recursos

### Ferramentas Disponíveis

1. **browser_open** - Abre um novo navegador (Chrome, Firefox, Safari)
2. **browser_close** - Fecha o navegador
3. **page_navigate** - Navega para uma URL
4. **page_click** - Clica em elementos
5. **page_type** - Digita texto
6. **page_screenshot** - Tira screenshots
7. **page_extract_text** - Extrai texto de elementos
8. **page_wait** - Aguarda elementos ou tempo
9. **page_evaluate** - Executa JavaScript
10. **page_fill_form** - Preenche formulários
11. **page_download** - Baixa arquivos
12. **page_upload** - Faz upload de arquivos
13. **session_list** - Lista sessões ativas
14. **automation_login** - Automação de login para sites populares

## Instalação

```bash
# Instalar dependências
npm install

# Instalar navegadores do Playwright
npx playwright install
```

## Uso

### Como Servidor MCP

```bash
# Iniciar servidor
npm start
```

### Testes e Exemplos

```bash
# Executar testes básicos
npm test

# Executar automação do GitHub
node test-client.js github
```

## Exemplos de Uso

### 1. Abrir Navegador e Navegar

```javascript
// Abrir navegador
await callTool('browser_open', {
  sessionId: 'minha-sessao',
  browser: 'chromium',
  headless: false
});

// Navegar para site
await callTool('page_navigate', {
  sessionId: 'minha-sessao',
  url: 'https://example.com'
});
```

### 2. Preencher Formulário

```javascript
await callTool('page_fill_form', {
  sessionId: 'minha-sessao',
  fields: {
    '#username': 'meu-usuario',
    '#password': 'minha-senha',
    '#email': 'email@example.com'
  }
});
```

### 3. Automação de Login

```javascript
// GitHub
await callTool('automation_login', {
  sessionId: 'minha-sessao',
  site: 'github',
  username: 'usuario',
  password: 'senha'
});

// Site customizado
await callTool('automation_login', {
  sessionId: 'minha-sessao',
  site: 'custom',
  username: 'usuario',
  password: 'senha',
  customConfig: {
    loginUrl: 'https://meusite.com/login',
    usernameSelector: '#user',
    passwordSelector: '#pass',
    submitSelector: '#login-btn'
  }
});
```

### 4. Web Scraping

```javascript
// Extrair textos
const textos = await callTool('page_extract_text', {
  sessionId: 'minha-sessao',
  selector: 'h1, h2, p'
});

// Executar JavaScript
const dados = await callTool('page_evaluate', {
  sessionId: 'minha-sessao',
  script: `
    Array.from(document.querySelectorAll('.product')).map(el => ({
      nome: el.querySelector('.name')?.textContent,
      preco: el.querySelector('.price')?.textContent
    }))
  `
});
```

### 5. Screenshots

```javascript
// Screenshot completo
await callTool('page_screenshot', {
  sessionId: 'minha-sessao',
  fullPage: true,
  path: 'pagina-completa.png'
});
```

## Integração com Claude

Este servidor MCP pode ser integrado com o Claude Desktop app. Adicione ao seu `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "browser-automation": {
      "command": "node",
      "args": ["C:/caminho/para/mcp-browser-automation/server.js"]
    }
  }
}
```

## Sites Suportados para Login Automático

- GitHub
- Google
- LinkedIn
- Facebook
- Sites customizados (com configuração)

## Estrutura do Projeto

```
mcp-browser-automation/
├── server.js          # Servidor MCP principal
├── test-client.js     # Cliente de teste e exemplos
├── package.json       # Dependências
├── mcp.json          # Configuração MCP
└── README.md         # Documentação
```

## Troubleshooting

### Erro: "Navegador não abre"
- Certifique-se de ter instalado os navegadores: `npx playwright install`

### Erro: "Sessão não encontrada"
- Sempre use um sessionId único para cada navegador
- Verifique se o navegador não foi fechado acidentalmente

### Erro: "Elemento não encontrado"
- Use `page_wait` antes de interagir com elementos
- Verifique o seletor CSS está correto
- Tente diferentes estratégias de espera (visible, attached)

## Segurança

- Nunca hardcode senhas no código
- Use variáveis de ambiente para credenciais sensíveis
- Cuidado ao executar JavaScript arbitrário com `page_evaluate`

## Licença

MIT