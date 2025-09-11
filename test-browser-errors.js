const puppeteer = require('puppeteer');

(async () => {
  console.log('🚀 Iniciando teste de erros do navegador...');
  
  const browser = await puppeteer.launch({ 
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });
  
  const page = await browser.newPage();
  
  // Capturar erros do console
  const errors = [];
  const logs = [];
  
  page.on('console', msg => {
    const type = msg.type();
    const text = msg.text();
    
    if (type === 'error') {
      errors.push(text);
      console.log('❌ ERRO:', text);
    } else {
      logs.push({ type, text });
      console.log(`📝 ${type.toUpperCase()}:`, text);
    }
  });
  
  page.on('pageerror', error => {
    errors.push(error.message);
    console.log('💥 ERRO DE PÁGINA:', error.message);
  });
  
  page.on('requestfailed', request => {
    console.log('⚠️ REQUEST FALHOU:', request.url());
  });
  
  try {
    console.log('\n📍 Navegando para http://localhost:5173...');
    await page.goto('http://localhost:5173', { 
      waitUntil: 'networkidle0',
      timeout: 30000 
    });
    
    // Aguardar um pouco para carregar
    await page.waitForTimeout(3000);
    
    // Verificar o título
    const title = await page.title();
    console.log('\n📄 Título da página:', title);
    
    // Verificar se existe conteúdo no root
    const rootContent = await page.evaluate(() => {
      const root = document.getElementById('root');
      return {
        exists: !!root,
        hasContent: root ? root.innerHTML.length > 0 : false,
        innerHTML: root ? root.innerHTML.substring(0, 200) : null
      };
    });
    
    console.log('\n🔍 Conteúdo do #root:');
    console.log('  - Existe:', rootContent.exists);
    console.log('  - Tem conteúdo:', rootContent.hasContent);
    if (rootContent.innerHTML) {
      console.log('  - HTML:', rootContent.innerHTML);
    }
    
    // Verificar se há algum formulário de login
    const loginForm = await page.evaluate(() => {
      const forms = document.querySelectorAll('form');
      const inputs = document.querySelectorAll('input');
      const buttons = document.querySelectorAll('button');
      
      return {
        formsCount: forms.length,
        inputsCount: inputs.length,
        buttonsCount: buttons.length,
        hasGoogleButton: Array.from(buttons).some(btn => 
          btn.textContent?.toLowerCase().includes('google') ||
          btn.className?.toLowerCase().includes('google')
        ),
        buttonTexts: Array.from(buttons).map(btn => btn.textContent)
      };
    });
    
    console.log('\n📋 Elementos do formulário:');
    console.log('  - Formulários:', loginForm.formsCount);
    console.log('  - Inputs:', loginForm.inputsCount);
    console.log('  - Botões:', loginForm.buttonsCount);
    console.log('  - Tem botão Google:', loginForm.hasGoogleButton);
    console.log('  - Textos dos botões:', loginForm.buttonTexts);
    
    // Tirar screenshot
    await page.screenshot({ path: 'test-browser-debug.png', fullPage: true });
    console.log('\n📸 Screenshot salvo em test-browser-debug.png');
    
    // Resumo
    console.log('\n📊 RESUMO:');
    console.log(`  - Erros encontrados: ${errors.length}`);
    if (errors.length > 0) {
      console.log('  - Lista de erros:');
      errors.forEach((err, i) => {
        console.log(`    ${i + 1}. ${err}`);
      });
    }
    
  } catch (error) {
    console.error('💥 Erro durante o teste:', error.message);
  } finally {
    await browser.close();
    console.log('\n✅ Teste concluído');
  }
})();