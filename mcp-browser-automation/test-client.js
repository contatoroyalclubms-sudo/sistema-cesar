import { Client } from '@modelcontextprotocol/sdk/client/index.js';
import { StdioClientTransport } from '@modelcontextprotocol/sdk/client/stdio.js';
import { spawn } from 'child_process';

// Cliente de teste para o MCP Browser Automation
class BrowserAutomationClient {
  constructor() {
    this.client = new Client(
      {
        name: 'browser-automation-test-client',
        version: '1.0.0'
      },
      {
        capabilities: {}
      }
    );
  }

  async connect() {
    const serverProcess = spawn('node', ['server.js'], {
      cwd: process.cwd(),
      env: process.env
    });

    const transport = new StdioClientTransport({
      command: 'node',
      args: ['server.js']
    });

    await this.client.connect(transport);
    console.log('✅ Conectado ao servidor MCP');
    
    return this;
  }

  async callTool(toolName, args) {
    try {
      const result = await this.client.request(
        {
          method: 'tools/call',
          params: {
            name: toolName,
            arguments: args
          }
        },
        {}
      );
      
      return result;
    } catch (error) {
      console.error(`❌ Erro ao chamar ${toolName}:`, error);
      throw error;
    }
  }

  async listTools() {
    const result = await this.client.request(
      {
        method: 'tools/list',
        params: {}
      },
      {}
    );
    
    return result.tools;
  }
}

// Exemplos de uso
async function exemplosDeUso() {
  console.log('🚀 Iniciando testes do MCP Browser Automation\n');
  
  const client = new BrowserAutomationClient();
  await client.connect();
  
  const sessionId = `session-${Date.now()}`;
  
  try {
    // Exemplo 1: Abrir navegador
    console.log('📌 Teste 1: Abrindo navegador...');
    await client.callTool('browser_open', {
      sessionId,
      browser: 'chromium',
      headless: false
    });
    
    // Exemplo 2: Navegar para GitHub
    console.log('📌 Teste 2: Navegando para GitHub...');
    await client.callTool('page_navigate', {
      sessionId,
      url: 'https://github.com',
      waitUntil: 'networkidle'
    });
    
    // Exemplo 3: Screenshot
    console.log('📌 Teste 3: Tirando screenshot...');
    await client.callTool('page_screenshot', {
      sessionId,
      fullPage: false,
      path: 'github-homepage.png'
    });
    
    // Exemplo 4: Extrair texto
    console.log('📌 Teste 4: Extraindo títulos...');
    const textos = await client.callTool('page_extract_text', {
      sessionId,
      selector: 'h1, h2'
    });
    console.log('Textos encontrados:', textos);
    
    // Exemplo 5: Automação de login (preparação)
    console.log('📌 Teste 5: Preparando login no GitHub...');
    await client.callTool('automation_login', {
      sessionId,
      site: 'github',
      // Deixar vazio para preenchimento manual
      // username: 'seu-usuario',
      // password: 'sua-senha'
    });
    
    // Aguardar um pouco
    await client.callTool('page_wait', {
      sessionId,
      timeout: 5000
    });
    
    // Exemplo 6: Executar JavaScript
    console.log('📌 Teste 6: Executando JavaScript...');
    const jsResult = await client.callTool('page_evaluate', {
      sessionId,
      script: 'document.title'
    });
    console.log('Título da página:', jsResult);
    
    // Exemplo 7: Listar sessões ativas
    console.log('📌 Teste 7: Listando sessões...');
    const sessions = await client.callTool('session_list', {});
    console.log('Sessões ativas:', sessions);
    
    console.log('\n✅ Testes concluídos com sucesso!');
    console.log('⏳ Navegador permanecerá aberto por 30 segundos...');
    
    // Manter aberto por 30 segundos
    await new Promise(resolve => setTimeout(resolve, 30000));
    
    // Fechar navegador
    console.log('🔚 Fechando navegador...');
    await client.callTool('browser_close', {
      sessionId
    });
    
  } catch (error) {
    console.error('❌ Erro durante os testes:', error);
  }
  
  process.exit(0);
}

// Exemplo de automação completa do GitHub
async function automacaoGitHub() {
  const client = new BrowserAutomationClient();
  await client.connect();
  
  const sessionId = `github-${Date.now()}`;
  
  console.log('🔧 Automação GitHub iniciando...\n');
  
  try {
    // Abrir navegador
    await client.callTool('browser_open', {
      sessionId,
      browser: 'chromium',
      headless: false
    });
    
    // Navegar para GitHub
    await client.callTool('page_navigate', {
      sessionId,
      url: 'https://github.com',
      waitUntil: 'networkidle'
    });
    
    // Screenshot inicial
    await client.callTool('page_screenshot', {
      sessionId,
      path: 'github-01-home.png'
    });
    
    // Clicar em Sign in
    await client.callTool('page_click', {
      sessionId,
      selector: 'a[href="/login"]'
    });
    
    // Aguardar página de login
    await client.callTool('page_wait', {
      sessionId,
      selector: '#login_field',
      timeout: 5000
    });
    
    // Screenshot da página de login
    await client.callTool('page_screenshot', {
      sessionId,
      path: 'github-02-login.png'
    });
    
    // Preencher formulário (exemplo)
    await client.callTool('page_fill_form', {
      sessionId,
      fields: {
        '#login_field': 'contato.royalclubms@gmail.com',
        '#password': '352162Cl'
      }
    });
    
    console.log('✅ Formulário preenchido');
    console.log('⏸️ Clique manualmente em Sign in para continuar...');
    
    // Aguardar 60 segundos para interação manual
    await new Promise(resolve => setTimeout(resolve, 60000));
    
    // Navegar para repositório específico
    await client.callTool('page_navigate', {
      sessionId,
      url: 'https://github.com/contatoroyalclubms-sudo/sistema-cesar',
      waitUntil: 'networkidle'
    });
    
    // Screenshot final
    await client.callTool('page_screenshot', {
      sessionId,
      path: 'github-03-repository.png'
    });
    
    console.log('✅ Automação concluída!');
    console.log('📁 Screenshots salvos');
    console.log('🌐 Navegador permanecerá aberto...');
    
  } catch (error) {
    console.error('❌ Erro na automação:', error);
  }
}

// Executar exemplo escolhido
const args = process.argv.slice(2);
const exemplo = args[0] || 'teste';

switch (exemplo) {
  case 'github':
    automacaoGitHub().catch(console.error);
    break;
  case 'teste':
  default:
    exemplosDeUso().catch(console.error);
    break;
}

// Uso:
// node test-client.js        - Executa testes básicos
// node test-client.js github - Executa automação do GitHub