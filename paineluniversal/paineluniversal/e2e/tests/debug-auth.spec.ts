import { test, expect } from '@playwright/test';

test.describe('Debug Auth', () => {
  test('Login flow debug', async ({ page }) => {
    // 1. Navegar para login
    await page.goto('http://localhost:5173/login');
    await page.waitForLoadState('networkidle');
    
    // 2. Tirar screenshot inicial
    await page.screenshot({ path: 'test-results/debug-1-initial.png' });
    
    // 3. Verificar se está na página de login
    await expect(page).toHaveURL(/.*login/);
    console.log('✓ Página de login carregada');
    
    // 4. Preencher CPF
    const cpfInput = page.locator('#cpf');
    await cpfInput.waitFor({ state: 'visible', timeout: 5000 });
    await cpfInput.fill('000.000.000-00');
    console.log('✓ CPF preenchido');
    
    // 5. Preencher senha
    const senhaInput = page.locator('#senha');
    await senhaInput.waitFor({ state: 'visible', timeout: 5000 });
    await senhaInput.fill('admin123');
    console.log('✓ Senha preenchida');
    
    // 6. Tirar screenshot antes de clicar
    await page.screenshot({ path: 'test-results/debug-2-filled.png' });
    
    // 7. Clicar no botão de submit
    const submitButton = page.locator('button[type="submit"]').first();
    await submitButton.click();
    console.log('✓ Botão clicado');
    
    // 8. Aguardar alguma mudança
    await page.waitForTimeout(3000);
    
    // 9. Verificar URL atual
    const currentUrl = page.url();
    console.log('URL atual:', currentUrl);
    
    // 10. Tirar screenshot final
    await page.screenshot({ path: 'test-results/debug-3-after-login.png' });
    
    // 11. Verificar console logs
    page.on('console', msg => console.log('Browser log:', msg.text()));
    
    // 12. Verificar erros de rede
    page.on('requestfailed', request => {
      console.log('Request failed:', request.url(), request.failure()?.errorText);
    });
    
    // 13. Esperar mais um pouco e verificar novamente
    await page.waitForTimeout(2000);
    const finalUrl = page.url();
    console.log('URL final:', finalUrl);
    
    // 14. Verificar se existe alguma mensagem de erro
    const errorMessage = page.locator('.error-message');
    const hasError = await errorMessage.count() > 0;
    if (hasError) {
      const errorText = await errorMessage.textContent();
      console.log('Erro encontrado:', errorText);
    }
    
    // 15. Verificar se redirecionou
    if (finalUrl.includes('dashboard')) {
      console.log('✅ Login bem-sucedido! Redirecionou para dashboard');
    } else {
      console.log('❌ Login falhou. Ainda na página:', finalUrl);
    }
  });
});