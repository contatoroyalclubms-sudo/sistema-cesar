const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

class MEEPDeepAnalyzer {
  constructor() {
    this.browser = null;
    this.page = null;
    this.analysis = {
      timestamp: new Date().toISOString(),
      loginStrategies: [],
      modules: [],
      apis: [],
      screenshots: [],
      techStack: {},
      uiPatterns: {},
      businessLogic: {},
      dataStructures: {},
      workflows: {},
      security: {},
      performance: {}
    };
    
    this.loginStrategies = [
      {
        name: 'Email Principal',
        email: 'toretomal@icloud.com',
        password: '10041210Cl@',
        selectors: [
          'input[type="email"]',
          'input[name="email"]',
          'input[name="login"]',
          'input[placeholder*="email" i]',
          'input[placeholder*="usuário" i]',
          'input[id="email"]',
          'input[id="login"]'
        ]
      },
      {
        name: 'Tentativa Alternativa',
        email: 'toretomal@icloud.com',
        password: '10041210Cl@',
        selectors: [
          '#username',
          '#user',
          '.email-input',
          '.login-input'
        ]
      }
    ];
  }

  async init() {
    console.log('🚀 Iniciando análise PROFUNDA do sistema MEEP...');
    this.browser = await chromium.launch({ 
      headless: false,
      slowMo: 1000,
      args: [
        '--disable-blink-features=AutomationControlled',
        '--no-first-run',
        '--disable-extensions',
        '--disable-default-apps'
      ]
    });
    
    const context = await this.browser.newContext({
      userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    });
    
    this.page = await context.newPage();
    
    // Monitoramento AVANÇADO de rede
    this.page.on('response', async (response) => {
      const url = response.url();
      const status = response.status();
      
      if (url.includes('api') || url.includes('.json') || status === 200) {
        console.log(`📡 API Discovery: ${status} ${url}`);
        
        try {
          const contentType = response.headers()['content-type'] || '';
          if (contentType.includes('application/json')) {
            const responseBody = await response.text();
            this.analysis.apis.push({
              url,
              status,
              method: 'DETECTED',
              contentType,
              timestamp: new Date().toISOString(),
              preview: responseBody.substring(0, 500)
            });
          }
        } catch (error) {
          console.log(`⚠️ Erro ao capturar response body: ${error.message}`);
        }
      }
    });
    
    // Interceptar requests
    this.page.on('request', (request) => {
      const url = request.url();
      if (url.includes('api') || url.includes('.json')) {
        console.log(`🔍 Request Intercepted: ${request.method()} ${url}`);
        this.analysis.apis.push({
          url,
          method: request.method(),
          headers: request.headers(),
          type: 'request',
          timestamp: new Date().toISOString()
        });
      }
    });
    
    return true;
  }

  async attemptAdvancedLogin() {
    console.log('🔐 Tentativa de login AVANÇADA no MEEP...');
    
    await this.page.goto('https://beta.portal.meep.com.br', { 
      waitUntil: 'networkidle',
      timeout: 30000
    });
    
    // Capturar screenshot da tela inicial
    await this.takeScreenshot('01-tela-inicial');
    
    for (let strategy of this.loginStrategies) {
      console.log(`🎯 Tentando estratégia: ${strategy.name}`);
      
      for (let emailSelector of strategy.selectors) {
        try {
          console.log(`🔍 Testando seletor: ${emailSelector}`);
          
          // Aguardar o seletor aparecer
          await this.page.waitForSelector(emailSelector, { timeout: 5000 });
          console.log(`✅ Seletor encontrado: ${emailSelector}`);
          
          // Preencher email
          await this.page.fill(emailSelector, strategy.email);
          console.log(`📧 Email preenchido: ${strategy.email}`);
          
          // Procurar campo de senha
          const passwordSelectors = [
            'input[type="password"]',
            'input[name="password"]',
            'input[name="senha"]',
            'input[placeholder*="senha" i]',
            'input[id="password"]',
            '#password'
          ];
          
          for (let passSelector of passwordSelectors) {
            try {
              await this.page.waitForSelector(passSelector, { timeout: 2000 });
              await this.page.fill(passSelector, strategy.password);
              console.log(`🔑 Senha preenchida`);
              
              // Capturar screenshot antes do submit
              await this.takeScreenshot('02-antes-submit');
              
              // Procurar botão de submit
              const submitSelectors = [
                'button[type="submit"]',
                'input[type="submit"]',
                'button:has-text("Entrar")',
                'button:has-text("Login")',
                'button:has-text("Acessar")',
                '.login-button',
                '.btn-login'
              ];
              
              for (let submitSelector of submitSelectors) {
                try {
                  await this.page.waitForSelector(submitSelector, { timeout: 2000 });
                  await this.page.click(submitSelector);
                  console.log(`🚀 Submit clicado: ${submitSelector}`);
                  
                  // Aguardar navegação ou mudança de URL
                  await this.page.waitForTimeout(3000);
                  
                  const currentUrl = this.page.url();
                  console.log(`🌐 URL atual: ${currentUrl}`);
                  
                  if (currentUrl.includes('dashboard') || 
                      currentUrl.includes('private') || 
                      currentUrl.includes('app') ||
                      currentUrl !== 'https://beta.portal.meep.com.br') {
                    console.log('🎉 LOGIN REALIZADO COM SUCESSO!');
                    await this.takeScreenshot('03-apos-login');
                    return true;
                  }
                  
                  break;
                } catch (submitError) {
                  console.log(`⚠️ Submit selector failed: ${submitSelector}`);
                }
              }
              
              break;
            } catch (passError) {
              console.log(`⚠️ Password selector failed: ${passSelector}`);
            }
          }
          
          break;
        } catch (emailError) {
          console.log(`⚠️ Email selector failed: ${emailSelector}`);
        }
      }
    }
    
    return false;
  }

  async exploreSystem() {
    console.log('🕵️ Explorando sistema MEEP em detalhes...');
    
    // Aguardar carregar completamente
    await this.page.waitForTimeout(5000);
    
    // Capturar informações do DOM
    const domInfo = await this.page.evaluate(() => {
      return {
        title: document.title,
        scripts: Array.from(document.scripts).map(s => ({ src: s.src, content: s.innerHTML.substring(0, 200) })),
        stylesheets: Array.from(document.styleSheets).map(s => ({ href: s.href })),
        elements: {
          buttons: Array.from(document.querySelectorAll('button')).length,
          forms: Array.from(document.querySelectorAll('form')).length,
          tables: Array.from(document.querySelectorAll('table')).length,
          inputs: Array.from(document.querySelectorAll('input')).length,
          divs: Array.from(document.querySelectorAll('div')).length
        },
        frameworks: {
          react: !!window.React || document.querySelector('[data-reactroot]') || document.querySelector('div[id="root"]'),
          angular: !!window.angular || document.querySelector('[ng-app]'),
          vue: !!window.Vue || document.querySelector('[data-v-]'),
          jquery: !!window.jQuery || !!window.$,
          bootstrap: !!document.querySelector('.container') || !!document.querySelector('.btn'),
          materialui: !!document.querySelector('[class*="Mui"]') || !!document.querySelector('[class*="MuiButton"]')
        },
        meepSpecific: {
          apiCalls: window.fetch ? 'fetch available' : 'no fetch',
          localStorageItems: Object.keys(localStorage).length,
          sessionStorageItems: Object.keys(sessionStorage).length
        }
      };
    });
    
    this.analysis.techStack = domInfo;
    console.log('💻 Tech Stack detectado:', JSON.stringify(domInfo.frameworks, null, 2));
    
    // Buscar por módulos/menu
    await this.findModules();
    
    // Buscar padrões de UI
    await this.analyzeUIPatterns();
    
    // Tentar navegar por diferentes seções
    await this.navigateSystem();
    
    return true;
  }

  async findModules() {
    console.log('🔍 Buscando módulos do sistema...');
    
    const moduleSelectors = [
      'nav a',
      '.menu a',
      '.sidebar a',
      '[role="menuitem"]',
      '.nav-link',
      '.menu-item',
      'button[aria-label]',
      '[href*="dashboard"]',
      '[href*="usuario"]',
      '[href*="produto"]',
      '[href*="evento"]',
      '[href*="relatorio"]',
      '[href*="financeiro"]',
      '[href*="cashless"]'
    ];
    
    for (let selector of moduleSelectors) {
      try {
        const elements = await this.page.$$(selector);
        if (elements.length > 0) {
          console.log(`📋 Encontrados ${elements.length} elementos com seletor: ${selector}`);
          
          for (let element of elements) {
            const text = await element.textContent();
            const href = await element.getAttribute('href');
            const ariaLabel = await element.getAttribute('aria-label');
            
            if (text && text.trim().length > 0) {
              this.analysis.modules.push({
                text: text.trim(),
                href,
                ariaLabel,
                selector,
                found: true
              });
            }
          }
        }
      } catch (error) {
        // Continuar tentando outros seletores
      }
    }
    
    console.log(`✅ Total de módulos encontrados: ${this.analysis.modules.length}`);
  }

  async analyzeUIPatterns() {
    console.log('🎨 Analisando padrões de UI...');
    
    const uiAnalysis = await this.page.evaluate(() => {
      const getStyles = (element) => {
        const computed = window.getComputedStyle(element);
        return {
          backgroundColor: computed.backgroundColor,
          color: computed.color,
          fontSize: computed.fontSize,
          fontFamily: computed.fontFamily,
          borderRadius: computed.borderRadius,
          padding: computed.padding,
          margin: computed.margin
        };
      };
      
      return {
        buttons: Array.from(document.querySelectorAll('button')).slice(0, 10).map(btn => ({
          text: btn.textContent?.trim(),
          styles: getStyles(btn),
          classes: btn.className
        })),
        forms: Array.from(document.querySelectorAll('form')).length,
        colorScheme: {
          primaryColors: Array.from(new Set(
            Array.from(document.querySelectorAll('*'))
              .map(el => window.getComputedStyle(el).backgroundColor)
              .filter(color => color !== 'rgba(0, 0, 0, 0)' && color !== 'transparent')
          )).slice(0, 10)
        }
      };
    });
    
    this.analysis.uiPatterns = uiAnalysis;
    console.log('🎨 Padrões UI capturados:', Object.keys(uiAnalysis));
  }

  async navigateSystem() {
    console.log('🗺️ Navegando pelo sistema...');
    
    // Tentar clicar em diferentes seções e capturar screenshots
    const moduleLinks = this.analysis.modules.filter(m => m.href && !m.href.startsWith('#'));
    
    for (let i = 0; i < Math.min(moduleLinks.length, 5); i++) {
      const module = moduleLinks[i];
      try {
        console.log(`🔗 Navegando para: ${module.text} - ${module.href}`);
        
        if (module.href.startsWith('http')) {
          await this.page.goto(module.href, { waitUntil: 'networkidle', timeout: 15000 });
        } else {
          await this.page.click(`[href="${module.href}"]`);
          await this.page.waitForTimeout(3000);
        }
        
        await this.takeScreenshot(`04-modulo-${i+1}-${module.text.replace(/[^a-zA-Z0-9]/g, '-')}`);
        
        // Capturar dados específicos desta página
        const pageData = await this.page.evaluate(() => {
          return {
            url: window.location.href,
            title: document.title,
            tables: Array.from(document.querySelectorAll('table')).length,
            forms: Array.from(document.querySelectorAll('form')).length,
            charts: Array.from(document.querySelectorAll('canvas, svg')).length,
            apiElements: Array.from(document.querySelectorAll('[data-api], [data-endpoint]')).length
          };
        });
        
        this.analysis.workflows[module.text] = pageData;
        
      } catch (error) {
        console.log(`❌ Erro ao navegar para ${module.text}: ${error.message}`);
      }
    }
  }

  async takeScreenshot(name) {
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const filename = `meep-${name}-${timestamp}.png`;
    const filepath = path.join(__dirname, 'screenshots', filename);
    
    // Criar diretório se não existir
    const dir = path.dirname(filepath);
    if (!fs.existsSync(dir)) {
      fs.mkdirSync(dir, { recursive: true });
    }
    
    await this.page.screenshot({ path: filepath, fullPage: true });
    this.analysis.screenshots.push({
      name,
      filename,
      filepath,
      timestamp
    });
    
    console.log(`📸 Screenshot salva: ${filename}`);
  }

  async performDeepAnalysis() {
    try {
      await this.init();
      
      const loginSuccess = await this.attemptAdvancedLogin();
      
      if (loginSuccess) {
        await this.exploreSystem();
      } else {
        console.log('⚠️ Login não realizado, mas continuando análise...');
        // Mesmo sem login, podemos analisar a página de login
        await this.analyzeUIPatterns();
        await this.takeScreenshot('05-analise-sem-login');
      }
      
      await this.generateComprehensiveReport();
      
    } catch (error) {
      console.error('💥 Erro na análise profunda:', error.message);
      await this.takeScreenshot('99-error-state');
    } finally {
      if (this.browser) {
        await this.browser.close();
      }
    }
  }

  async generateComprehensiveReport() {
    console.log('📊 Gerando relatório ABRANGENTE...');
    
    // Relatório JSON detalhado
    const reportPath = path.join(__dirname, 'MEEP_DEEP_ANALYSIS_REPORT.json');
    fs.writeFileSync(reportPath, JSON.stringify(this.analysis, null, 2), 'utf8');
    
    // Relatório markdown executivo
    const markdownReport = this.generateMarkdownReport();
    const markdownPath = path.join(__dirname, 'MEEP_DEEP_ANALYSIS_SUMMARY.md');
    fs.writeFileSync(markdownPath, markdownReport, 'utf8');
    
    // Relatório de implementação
    const implementationReport = this.generateImplementationGuide();
    const implementationPath = path.join(__dirname, 'MEEP_IMPLEMENTATION_GUIDE.md');
    fs.writeFileSync(implementationPath, implementationReport, 'utf8');
    
    console.log('✅ Relatórios salvos:');
    console.log(`   📄 JSON: ${reportPath}`);
    console.log(`   📋 Summary: ${markdownPath}`);
    console.log(`   🔧 Implementation: ${implementationPath}`);
  }

  generateMarkdownReport() {
    return `# 🔍 ANÁLISE PROFUNDA SISTEMA MEEP
## Data: ${new Date().toLocaleDateString('pt-BR')}

## 🎯 RESUMO EXECUTIVO
- **Módulos Descobertos:** ${this.analysis.modules.length}
- **APIs Capturadas:** ${this.analysis.apis.length}
- **Screenshots:** ${this.analysis.screenshots.length}
- **Framework Principal:** ${this.analysis.techStack.frameworks?.react ? 'React' : 'Desconhecido'}

## 📋 MÓDULOS IDENTIFICADOS
${this.analysis.modules.map(m => `- **${m.text}** (${m.href || 'N/A'})`).join('\n')}

## 🔧 STACK TÉCNICO DETECTADO
- **React:** ${this.analysis.techStack.frameworks?.react ? '✅' : '❌'}
- **Angular:** ${this.analysis.techStack.frameworks?.angular ? '✅' : '❌'}
- **Vue:** ${this.analysis.techStack.frameworks?.vue ? '✅' : '❌'}
- **jQuery:** ${this.analysis.techStack.frameworks?.jquery ? '✅' : '❌'}
- **Bootstrap:** ${this.analysis.techStack.frameworks?.bootstrap ? '✅' : '❌'}
- **Material UI:** ${this.analysis.techStack.frameworks?.materialui ? '✅' : '❌'}

## 📡 APIs DESCOBERTAS
${this.analysis.apis.slice(0, 20).map(api => `- ${api.method || 'GET'} ${api.url} (${api.status || 'N/A'})`).join('\n')}

## 🎨 PADRÕES UI IDENTIFICADOS
- **Botões Encontrados:** ${this.analysis.uiPatterns.buttons?.length || 0}
- **Formulários:** ${this.analysis.uiPatterns.forms || 0}
- **Esquema de Cores:** ${this.analysis.uiPatterns.colorScheme?.primaryColors?.length || 0} cores primárias

## 📸 SCREENSHOTS CAPTURADAS
${this.analysis.screenshots.map(s => `- ${s.name} (${s.filename})`).join('\n')}

## 🗺️ FLUXOS DE TRABALHO
${Object.keys(this.analysis.workflows).map(key => `- **${key}:** ${JSON.stringify(this.analysis.workflows[key])}`).join('\n')}

---
*Análise gerada automaticamente pelo MEEP Deep Analyzer*`;
  }

  generateImplementationGuide() {
    return `# 🚀 GUIA DE IMPLEMENTAÇÃO BASEADO NA ANÁLISE MEEP

## 📋 MÓDULOS PARA IMPLEMENTAR
${this.analysis.modules.map(m => `
### ${m.text}
- **Rota sugerida:** /app/${m.text.toLowerCase().replace(/\s+/g, '-')}
- **Componente:** ${m.text.replace(/\s+/g, '')}Module.tsx
- **API Endpoint:** /api/${m.text.toLowerCase().replace(/\s+/g, '-')}
`).join('\n')}

## 🎨 COMPONENTES UI SUGERIDOS
${this.analysis.uiPatterns.buttons?.slice(0, 5).map((btn, i) => `
### Botão Tipo ${i + 1}
\`\`\`tsx
<Button 
  className="${btn.classes}"
  style={{ 
    backgroundColor: '${btn.styles.backgroundColor}',
    color: '${btn.styles.color}',
    fontSize: '${btn.styles.fontSize}',
    borderRadius: '${btn.styles.borderRadius}'
  }}
>
  ${btn.text}
</Button>
\`\`\`
`).join('\n') || 'Nenhum padrão de botão capturado'}

## 🔧 APIS PARA IMPLEMENTAR
${this.analysis.apis.filter(api => api.url.includes('api')).slice(0, 10).map(api => `
### ${api.url}
\`\`\`python
# FastAPI Implementation
@router.${(api.method || 'get').toLowerCase()}("${api.url.split('/api')[1] || '/endpoint'}")
async def endpoint_${api.url.split('/').pop().replace(/[^a-zA-Z0-9]/g, '_')}():
    # Implementation based on MEEP analysis
    return {"status": "success"}
\`\`\`
`).join('\n')}

---
*Guia gerado automaticamente para replicação das funcionalidades MEEP*`;
  }
}

// Executar análise
const analyzer = new MEEPDeepAnalyzer();
analyzer.performDeepAnalysis().then(() => {
  console.log('🎉 Análise PROFUNDA do MEEP concluída!');
}).catch(error => {
  console.error('💥 Erro fatal:', error);
  process.exit(1);
});