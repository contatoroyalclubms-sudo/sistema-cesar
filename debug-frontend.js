const { chromium } = require('playwright');

(async () => {
  console.log('🚀 Iniciando debug do frontend...\n');
  
  const browser = await chromium.launch({ 
    headless: false,  // Mostrar navegador
    devtools: true    // Abrir DevTools automaticamente
  });
  
  const context = await browser.newContext();
  const page = await context.newPage();
  
  // Capturar logs do console
  page.on('console', msg => {
    const type = msg.type();
    const text = msg.text();
    
    if (type === 'error') {
      console.log('❌ ERRO:', text);
      // Tentar obter mais detalhes
      msg.args().forEach(async (arg, i) => {
        try {
          const val = await arg.jsonValue();
          console.log(`   Arg[${i}]:`, val);
        } catch (e) {
          // Ignorar se não conseguir serializar
        }
      });
    } else if (type === 'warning') {
      console.log('⚠️ AVISO:', text);
    } else {
      console.log(`📝 ${type.toUpperCase()}:`, text);
    }
  });
  
  page.on('pageerror', error => {
    console.log('💥 ERRO DE PÁGINA:', error.message);
    console.log('   Stack:', error.stack);
  });
  
  page.on('requestfailed', request => {
    console.log('⚠️ REQUEST FALHOU:', request.url());
    console.log('   Erro:', request.failure()?.errorText);
  });
  
  console.log('📍 Navegando para http://localhost:5174...\n');
  
  try {
    await page.goto('http://localhost:5174', { 
      waitUntil: 'domcontentloaded',
      timeout: 30000 
    });
    
    console.log('✅ Página carregada\n');
    
    // Aguardar um pouco
    await page.waitForTimeout(3000);
    
    // Verificar o conteúdo do root
    const rootInfo = await page.evaluate(() => {
      const root = document.getElementById('root');
      if (!root) return { exists: false };
      
      return {
        exists: true,
        hasContent: root.innerHTML.length > 0,
        childrenCount: root.children.length,
        innerHTML: root.innerHTML.substring(0, 500)
      };
    });
    
    console.log('\n🔍 Informações do #root:');
    console.log('   Existe:', rootInfo.exists);
    console.log('   Tem conteúdo:', rootInfo.hasContent);
    console.log('   Número de filhos:', rootInfo.childrenCount);
    
    if (rootInfo.innerHTML) {
      console.log('\n📄 Primeiros 500 caracteres do HTML:');
      console.log(rootInfo.innerHTML);
    }
    
    // Verificar se React está carregado
    const reactInfo = await page.evaluate(() => {
      return {
        hasReact: typeof window.React !== 'undefined',
        hasReactDOM: typeof window.ReactDOM !== 'undefined',
        reactVersion: window.React?.version || 'N/A'
      };
    });
    
    console.log('\n⚛️ Informações do React:');
    console.log('   React carregado:', reactInfo.hasReact);
    console.log('   ReactDOM carregado:', reactInfo.hasReactDOM);
    console.log('   Versão:', reactInfo.reactVersion);
    
    // Tentar executar comandos no console
    const moduleErrors = await page.evaluate(() => {
      const errors = [];
      
      // Verificar se os módulos estão carregando
      try {
        // Tentar acessar o módulo principal
        const mainModule = document.querySelector('script[type="module"][src*="main"]');
        if (mainModule) {
          errors.push(`Main module src: ${mainModule.src}`);
        }
      } catch (e) {
        errors.push(`Error checking modules: ${e.message}`);
      }
      
      return errors;
    });
    
    if (moduleErrors.length > 0) {
      console.log('\n📦 Informações dos módulos:');
      moduleErrors.forEach(err => console.log('   ', err));
    }
    
    console.log('\n⏸️ Navegador permanecerá aberto. Pressione Ctrl+C para fechar.');
    
    // Manter navegador aberto
    await new Promise(() => {});
    
  } catch (error) {
    console.error('💥 Erro durante navegação:', error.message);
  }
})();