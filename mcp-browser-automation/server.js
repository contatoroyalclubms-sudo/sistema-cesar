import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import { chromium, firefox, webkit } from 'playwright';
import { promises as fs } from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

class BrowserAutomationServer {
  constructor() {
    this.server = new Server(
      {
        name: 'browser-automation-mcp',
        version: '1.0.0'
      },
      {
        capabilities: {
          tools: {}
        }
      }
    );

    this.browsers = new Map();
    this.pages = new Map();
    this.setupTools();
  }

  setupTools() {
    // Ferramenta para abrir navegador
    this.server.setRequestHandler('tools/list', async () => ({
      tools: [
        {
          name: 'browser_open',
          description: 'Abre um novo navegador',
          inputSchema: {
            type: 'object',
            properties: {
              browser: {
                type: 'string',
                enum: ['chromium', 'firefox', 'webkit'],
                default: 'chromium'
              },
              headless: {
                type: 'boolean',
                default: false
              },
              sessionId: {
                type: 'string',
                description: 'ID único da sessão'
              }
            },
            required: ['sessionId']
          }
        },
        {
          name: 'browser_close',
          description: 'Fecha um navegador',
          inputSchema: {
            type: 'object',
            properties: {
              sessionId: {
                type: 'string',
                description: 'ID da sessão do navegador'
              }
            },
            required: ['sessionId']
          }
        },
        {
          name: 'page_navigate',
          description: 'Navega para uma URL',
          inputSchema: {
            type: 'object',
            properties: {
              sessionId: {
                type: 'string'
              },
              url: {
                type: 'string'
              },
              waitUntil: {
                type: 'string',
                enum: ['load', 'domcontentloaded', 'networkidle'],
                default: 'load'
              }
            },
            required: ['sessionId', 'url']
          }
        },
        {
          name: 'page_click',
          description: 'Clica em um elemento',
          inputSchema: {
            type: 'object',
            properties: {
              sessionId: {
                type: 'string'
              },
              selector: {
                type: 'string'
              },
              button: {
                type: 'string',
                enum: ['left', 'right', 'middle'],
                default: 'left'
              }
            },
            required: ['sessionId', 'selector']
          }
        },
        {
          name: 'page_type',
          description: 'Digita texto em um campo',
          inputSchema: {
            type: 'object',
            properties: {
              sessionId: {
                type: 'string'
              },
              selector: {
                type: 'string'
              },
              text: {
                type: 'string'
              },
              delay: {
                type: 'number',
                default: 0
              }
            },
            required: ['sessionId', 'selector', 'text']
          }
        },
        {
          name: 'page_screenshot',
          description: 'Tira screenshot da página',
          inputSchema: {
            type: 'object',
            properties: {
              sessionId: {
                type: 'string'
              },
              fullPage: {
                type: 'boolean',
                default: false
              },
              path: {
                type: 'string'
              }
            },
            required: ['sessionId']
          }
        },
        {
          name: 'page_extract_text',
          description: 'Extrai texto de elementos',
          inputSchema: {
            type: 'object',
            properties: {
              sessionId: {
                type: 'string'
              },
              selector: {
                type: 'string'
              }
            },
            required: ['sessionId', 'selector']
          }
        },
        {
          name: 'page_wait',
          description: 'Aguarda elemento ou tempo',
          inputSchema: {
            type: 'object',
            properties: {
              sessionId: {
                type: 'string'
              },
              selector: {
                type: 'string'
              },
              timeout: {
                type: 'number',
                default: 30000
              },
              state: {
                type: 'string',
                enum: ['attached', 'detached', 'visible', 'hidden'],
                default: 'visible'
              }
            },
            required: ['sessionId']
          }
        },
        {
          name: 'page_evaluate',
          description: 'Executa JavaScript na página',
          inputSchema: {
            type: 'object',
            properties: {
              sessionId: {
                type: 'string'
              },
              script: {
                type: 'string'
              }
            },
            required: ['sessionId', 'script']
          }
        },
        {
          name: 'page_fill_form',
          description: 'Preenche formulário automaticamente',
          inputSchema: {
            type: 'object',
            properties: {
              sessionId: {
                type: 'string'
              },
              fields: {
                type: 'object',
                description: 'Objeto com selector: valor'
              }
            },
            required: ['sessionId', 'fields']
          }
        },
        {
          name: 'page_download',
          description: 'Baixa arquivo de um link',
          inputSchema: {
            type: 'object',
            properties: {
              sessionId: {
                type: 'string'
              },
              selector: {
                type: 'string'
              },
              savePath: {
                type: 'string'
              }
            },
            required: ['sessionId', 'selector']
          }
        },
        {
          name: 'page_upload',
          description: 'Faz upload de arquivo',
          inputSchema: {
            type: 'object',
            properties: {
              sessionId: {
                type: 'string'
              },
              selector: {
                type: 'string'
              },
              filePath: {
                type: 'string'
              }
            },
            required: ['sessionId', 'selector', 'filePath']
          }
        },
        {
          name: 'session_list',
          description: 'Lista todas as sessões ativas',
          inputSchema: {
            type: 'object',
            properties: {}
          }
        },
        {
          name: 'automation_login',
          description: 'Automação completa de login',
          inputSchema: {
            type: 'object',
            properties: {
              sessionId: {
                type: 'string'
              },
              site: {
                type: 'string',
                enum: ['github', 'google', 'linkedin', 'facebook', 'custom']
              },
              username: {
                type: 'string'
              },
              password: {
                type: 'string'
              },
              customConfig: {
                type: 'object',
                properties: {
                  loginUrl: { type: 'string' },
                  usernameSelector: { type: 'string' },
                  passwordSelector: { type: 'string' },
                  submitSelector: { type: 'string' }
                }
              }
            },
            required: ['sessionId', 'site']
          }
        }
      ]
    }));

    // Handler para executar ferramentas
    this.server.setRequestHandler('tools/call', async (request) => {
      const { name, arguments: args } = request.params;

      try {
        switch (name) {
          case 'browser_open':
            return await this.openBrowser(args);
          case 'browser_close':
            return await this.closeBrowser(args);
          case 'page_navigate':
            return await this.navigatePage(args);
          case 'page_click':
            return await this.clickElement(args);
          case 'page_type':
            return await this.typeText(args);
          case 'page_screenshot':
            return await this.takeScreenshot(args);
          case 'page_extract_text':
            return await this.extractText(args);
          case 'page_wait':
            return await this.waitForElement(args);
          case 'page_evaluate':
            return await this.evaluateScript(args);
          case 'page_fill_form':
            return await this.fillForm(args);
          case 'page_download':
            return await this.downloadFile(args);
          case 'page_upload':
            return await this.uploadFile(args);
          case 'session_list':
            return await this.listSessions();
          case 'automation_login':
            return await this.automateLogin(args);
          default:
            throw new Error(`Ferramenta não encontrada: ${name}`);
        }
      } catch (error) {
        return {
          content: [
            {
              type: 'text',
              text: `Erro: ${error.message}`
            }
          ]
        };
      }
    });
  }

  async openBrowser(args) {
    const { sessionId, browser = 'chromium', headless = false } = args;
    
    let browserInstance;
    switch (browser) {
      case 'firefox':
        browserInstance = await firefox.launch({ headless });
        break;
      case 'webkit':
        browserInstance = await webkit.launch({ headless });
        break;
      default:
        browserInstance = await chromium.launch({ 
          headless,
          args: ['--start-maximized']
        });
    }

    const page = await browserInstance.newPage();
    
    this.browsers.set(sessionId, browserInstance);
    this.pages.set(sessionId, page);

    return {
      content: [
        {
          type: 'text',
          text: `Navegador ${browser} aberto com sessão: ${sessionId}`
        }
      ]
    };
  }

  async closeBrowser(args) {
    const { sessionId } = args;
    const browser = this.browsers.get(sessionId);
    
    if (browser) {
      await browser.close();
      this.browsers.delete(sessionId);
      this.pages.delete(sessionId);
      return {
        content: [
          {
            type: 'text',
            text: `Navegador fechado: ${sessionId}`
          }
        ]
      };
    }
    
    throw new Error(`Sessão não encontrada: ${sessionId}`);
  }

  async navigatePage(args) {
    const { sessionId, url, waitUntil = 'load' } = args;
    const page = this.pages.get(sessionId);
    
    if (!page) throw new Error(`Sessão não encontrada: ${sessionId}`);
    
    await page.goto(url, { waitUntil });
    
    return {
      content: [
        {
          type: 'text',
          text: `Navegado para: ${url}`
        }
      ]
    };
  }

  async clickElement(args) {
    const { sessionId, selector, button = 'left' } = args;
    const page = this.pages.get(sessionId);
    
    if (!page) throw new Error(`Sessão não encontrada: ${sessionId}`);
    
    await page.click(selector, { button });
    
    return {
      content: [
        {
          type: 'text',
          text: `Clicado em: ${selector}`
        }
      ]
    };
  }

  async typeText(args) {
    const { sessionId, selector, text, delay = 0 } = args;
    const page = this.pages.get(sessionId);
    
    if (!page) throw new Error(`Sessão não encontrada: ${sessionId}`);
    
    await page.type(selector, text, { delay });
    
    return {
      content: [
        {
          type: 'text',
          text: `Texto digitado em: ${selector}`
        }
      ]
    };
  }

  async takeScreenshot(args) {
    const { sessionId, fullPage = false, path: screenshotPath } = args;
    const page = this.pages.get(sessionId);
    
    if (!page) throw new Error(`Sessão não encontrada: ${sessionId}`);
    
    const filename = screenshotPath || `screenshot-${Date.now()}.png`;
    const buffer = await page.screenshot({ fullPage });
    
    if (screenshotPath) {
      await fs.writeFile(screenshotPath, buffer);
    }
    
    return {
      content: [
        {
          type: 'text',
          text: `Screenshot salvo: ${filename}`
        }
      ]
    };
  }

  async extractText(args) {
    const { sessionId, selector } = args;
    const page = this.pages.get(sessionId);
    
    if (!page) throw new Error(`Sessão não encontrada: ${sessionId}`);
    
    const texts = await page.$$eval(selector, elements => 
      elements.map(el => el.textContent?.trim()).filter(Boolean)
    );
    
    return {
      content: [
        {
          type: 'text',
          text: JSON.stringify(texts, null, 2)
        }
      ]
    };
  }

  async waitForElement(args) {
    const { sessionId, selector, timeout = 30000, state = 'visible' } = args;
    const page = this.pages.get(sessionId);
    
    if (!page) throw new Error(`Sessão não encontrada: ${sessionId}`);
    
    if (selector) {
      await page.waitForSelector(selector, { timeout, state });
      return {
        content: [
          {
            type: 'text',
            text: `Elemento aguardado: ${selector} (${state})`
          }
        ]
      };
    } else {
      await page.waitForTimeout(timeout);
      return {
        content: [
          {
            type: 'text',
            text: `Aguardado ${timeout}ms`
          }
        ]
      };
    }
  }

  async evaluateScript(args) {
    const { sessionId, script } = args;
    const page = this.pages.get(sessionId);
    
    if (!page) throw new Error(`Sessão não encontrada: ${sessionId}`);
    
    const result = await page.evaluate(script);
    
    return {
      content: [
        {
          type: 'text',
          text: JSON.stringify(result, null, 2)
        }
      ]
    };
  }

  async fillForm(args) {
    const { sessionId, fields } = args;
    const page = this.pages.get(sessionId);
    
    if (!page) throw new Error(`Sessão não encontrada: ${sessionId}`);
    
    for (const [selector, value] of Object.entries(fields)) {
      await page.fill(selector, value);
    }
    
    return {
      content: [
        {
          type: 'text',
          text: `Formulário preenchido com ${Object.keys(fields).length} campos`
        }
      ]
    };
  }

  async downloadFile(args) {
    const { sessionId, selector, savePath } = args;
    const page = this.pages.get(sessionId);
    
    if (!page) throw new Error(`Sessão não encontrada: ${sessionId}`);
    
    const downloadPromise = page.waitForEvent('download');
    await page.click(selector);
    const download = await downloadPromise;
    
    if (savePath) {
      await download.saveAs(savePath);
    }
    
    return {
      content: [
        {
          type: 'text',
          text: `Arquivo baixado: ${savePath || download.suggestedFilename()}`
        }
      ]
    };
  }

  async uploadFile(args) {
    const { sessionId, selector, filePath } = args;
    const page = this.pages.get(sessionId);
    
    if (!page) throw new Error(`Sessão não encontrada: ${sessionId}`);
    
    await page.setInputFiles(selector, filePath);
    
    return {
      content: [
        {
          type: 'text',
          text: `Arquivo enviado: ${filePath}`
        }
      ]
    };
  }

  async listSessions() {
    const sessions = Array.from(this.browsers.keys());
    
    return {
      content: [
        {
          type: 'text',
          text: `Sessões ativas: ${JSON.stringify(sessions, null, 2)}`
        }
      ]
    };
  }

  async automateLogin(args) {
    const { sessionId, site, username, password, customConfig } = args;
    const page = this.pages.get(sessionId);
    
    if (!page) throw new Error(`Sessão não encontrada: ${sessionId}`);
    
    const loginConfigs = {
      github: {
        loginUrl: 'https://github.com/login',
        usernameSelector: '#login_field',
        passwordSelector: '#password',
        submitSelector: 'input[type="submit"]'
      },
      google: {
        loginUrl: 'https://accounts.google.com',
        usernameSelector: 'input[type="email"]',
        passwordSelector: 'input[type="password"]',
        submitSelector: '#passwordNext'
      },
      linkedin: {
        loginUrl: 'https://www.linkedin.com/login',
        usernameSelector: '#username',
        passwordSelector: '#password',
        submitSelector: 'button[type="submit"]'
      },
      facebook: {
        loginUrl: 'https://www.facebook.com',
        usernameSelector: '#email',
        passwordSelector: '#pass',
        submitSelector: 'button[name="login"]'
      },
      custom: customConfig
    };
    
    const config = loginConfigs[site];
    if (!config) throw new Error(`Site não suportado: ${site}`);
    
    // Navegar para página de login
    await page.goto(config.loginUrl, { waitUntil: 'networkidle' });
    
    // Preencher credenciais
    if (username) {
      await page.fill(config.usernameSelector, username);
    }
    
    if (password) {
      await page.fill(config.passwordSelector, password);
    }
    
    // Clicar em login
    if (username && password) {
      await page.click(config.submitSelector);
      await page.waitForLoadState('networkidle');
    }
    
    return {
      content: [
        {
          type: 'text',
          text: `Login automatizado para ${site} ${username ? 'com credenciais' : 'preparado para preenchimento manual'}`
        }
      ]
    };
  }

  async run() {
    const transport = new StdioServerTransport();
    await this.server.connect(transport);
    console.error('MCP Browser Automation Server iniciado');
  }
}

// Iniciar servidor
const server = new BrowserAutomationServer();
server.run().catch(console.error);