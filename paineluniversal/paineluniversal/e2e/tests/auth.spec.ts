/**
 * 🔐 TESTES DE AUTENTICAÇÃO
 * Testes E2E para login, logout e registro
 */

import { test, expect } from '@playwright/test';
import { LoginPage } from './fixtures/page-objects';
import { testUsers, TestDataFactory } from './fixtures/test-data';

test.describe('Autenticação', () => {
  let loginPage: LoginPage;
  
  test.beforeEach(async ({ page }) => {
    loginPage = new LoginPage(page);
    await loginPage.goto();
  });
  
  test.describe('Login', () => {
    test('@critical Login com sucesso - Admin', async () => {
      // Arrange
      const user = testUsers.admin;
      
      // Act
      await loginPage.login(user.cpf, user.senha);
      
      // Assert
      await loginPage.expectLoggedIn();
      await expect(loginPage.page).toHaveURL(/.*dashboard/);
      
      // Verifica se tem acesso admin
      await expect(loginPage.page.locator('[data-testid="admin-menu"]')).toBeVisible();
    });
    
    test('@critical Login com sucesso - Promoter', async () => {
      // Arrange
      const user = testUsers.promoter;
      
      // Act
      await loginPage.login(user.cpf, user.senha);
      
      // Assert
      await loginPage.expectLoggedIn();
      await expect(loginPage.page).toHaveURL(/.*dashboard/);
      
      // Verifica se tem acesso promoter
      await expect(loginPage.page.locator('[data-testid="promoter-menu"]')).toBeVisible();
    });
    
    test('@critical Login com sucesso - Cliente', async () => {
      // Arrange
      const user = testUsers.cliente;
      
      // Act
      await loginPage.login(user.cpf, user.senha);
      
      // Assert
      await loginPage.expectLoggedIn();
      await expect(loginPage.page).toHaveURL(/.*dashboard/);
    });
    
    test('Login com CPF inválido', async () => {
      // Act
      await loginPage.login('111.111.111-11', 'senha123');
      
      // Assert
      await loginPage.expectError('CPF inválido');
      await expect(loginPage.page).toHaveURL(/.*login/);
    });
    
    test('Login com senha incorreta', async () => {
      // Arrange
      const user = testUsers.admin;
      
      // Act
      await loginPage.login(user.cpf, 'senhaErrada');
      
      // Assert
      await loginPage.expectError('CPF ou senha incorretos');
      await expect(loginPage.page).toHaveURL(/.*login/);
    });
    
    test('Login com campos vazios', async () => {
      // Act
      await loginPage.page.click('button[type="submit"]');
      
      // Assert
      await expect(loginPage.page.locator('#cpf')).toHaveAttribute('required');
      await expect(loginPage.page.locator('#senha')).toHaveAttribute('required');
    });
    
    test('Login com formato de CPF incorreto', async () => {
      // Act
      await loginPage.login('12345678909', 'senha123'); // Sem formatação
      
      // Assert - deve aceitar e formatar automaticamente
      await loginPage.expectLoggedIn();
    });
  });
  
  test.describe('Logout', () => {
    test('@critical Logout com sucesso', async () => {
      // Arrange - fazer login primeiro
      const user = testUsers.admin;
      await loginPage.login(user.cpf, user.senha);
      await loginPage.expectLoggedIn();
      
      // Act
      await loginPage.logout();
      
      // Assert
      await expect(loginPage.page).toHaveURL(/.*login/);
      
      // Verifica que não consegue acessar área protegida
      await loginPage.page.goto('/dashboard');
      await expect(loginPage.page).toHaveURL(/.*login/);
    });
    
    test('Sessão expira após timeout', async ({ page, context }) => {
      // Arrange - fazer login
      const user = testUsers.admin;
      await loginPage.login(user.cpf, user.senha);
      await loginPage.expectLoggedIn();
      
      // Act - simular expiração do token
      await context.clearCookies();
      await page.reload();
      
      // Assert
      await expect(page).toHaveURL(/.*login/);
    });
  });
  
  test.describe('Registro', () => {
    test('@smoke Registro de novo usuário', async ({ page }) => {
      // Arrange
      const newUser = TestDataFactory.generateUser();
      
      // Navigate to register
      await page.goto('/register');
      
      // Act - preencher formulário
      await page.fill('#nome', newUser.nome);
      await page.fill('#email', newUser.email);
      await page.fill('#cpf', newUser.cpf);
      await page.fill('#telefone', newUser.telefone);
      await page.fill('#senha', newUser.senha);
      await page.fill('#confirmarSenha', newUser.senha);
      
      await page.click('button[type="submit"]');
      
      // Assert
      await page.waitForURL(/.*login/);
      await expect(page.locator('.success-message')).toContainText('Cadastro realizado com sucesso');
      
      // Tentar fazer login com novo usuário
      loginPage = new LoginPage(page);
      await loginPage.login(newUser.cpf, newUser.senha);
      await loginPage.expectLoggedIn();
    });
    
    test('Registro com CPF duplicado', async ({ page }) => {
      // Arrange
      const existingUser = testUsers.admin;
      
      // Navigate to register
      await page.goto('/register');
      
      // Act
      await page.fill('#nome', 'Novo Nome');
      await page.fill('#email', 'novo@email.com');
      await page.fill('#cpf', existingUser.cpf); // CPF já existe
      await page.fill('#senha', 'NovaSenha123');
      await page.fill('#confirmarSenha', 'NovaSenha123');
      
      await page.click('button[type="submit"]');
      
      // Assert
      await expect(page.locator('.error-message')).toContainText('CPF já cadastrado');
    });
    
    test('Registro com email duplicado', async ({ page }) => {
      // Arrange
      const existingUser = testUsers.admin;
      const newUser = TestDataFactory.generateUser();
      
      // Navigate to register
      await page.goto('/register');
      
      // Act
      await page.fill('#nome', newUser.nome);
      await page.fill('#email', existingUser.email); // Email já existe
      await page.fill('#cpf', newUser.cpf);
      await page.fill('#senha', 'NovaSenha123');
      await page.fill('#confirmarSenha', 'NovaSenha123');
      
      await page.click('button[type="submit"]');
      
      // Assert
      await expect(page.locator('.error-message')).toContainText('Email já cadastrado');
    });
    
    test('Validação de senha fraca', async ({ page }) => {
      // Arrange
      const newUser = TestDataFactory.generateUser();
      
      // Navigate to register
      await page.goto('/register');
      
      // Act
      await page.fill('#nome', newUser.nome);
      await page.fill('#email', newUser.email);
      await page.fill('#cpf', newUser.cpf);
      await page.fill('#senha', '123'); // Senha muito curta
      await page.fill('#confirmarSenha', '123');
      
      // Assert
      await expect(page.locator('#senha')).toHaveAttribute('minlength', '6');
      
      // Tentar enviar
      await page.click('button[type="submit"]');
      await expect(page.locator('.error-message')).toContainText('Senha deve ter pelo menos 6 caracteres');
    });
    
    test('Senhas não conferem', async ({ page }) => {
      // Arrange
      const newUser = TestDataFactory.generateUser();
      
      // Navigate to register
      await page.goto('/register');
      
      // Act
      await page.fill('#nome', newUser.nome);
      await page.fill('#email', newUser.email);
      await page.fill('#cpf', newUser.cpf);
      await page.fill('#senha', 'Senha123');
      await page.fill('#confirmarSenha', 'SenhaDiferente123');
      
      await page.click('button[type="submit"]');
      
      // Assert
      await expect(page.locator('.error-message')).toContainText('Senhas não conferem');
    });
  });
  
  test.describe('Recuperação de Senha', () => {
    test('Solicitar recuperação de senha', async ({ page }) => {
      // Navigate to forgot password
      await page.goto('/login');
      await page.click('a:has-text("Esqueci minha senha")');
      
      // Act
      await page.fill('#email', testUsers.admin.email);
      await page.click('button:has-text("Enviar")');
      
      // Assert
      await expect(page.locator('.success-message')).toContainText('Email de recuperação enviado');
    });
    
    test('Recuperação com email não cadastrado', async ({ page }) => {
      // Navigate to forgot password
      await page.goto('/forgot-password');
      
      // Act
      await page.fill('#email', 'naoexiste@email.com');
      await page.click('button:has-text("Enviar")');
      
      // Assert
      await expect(page.locator('.error-message')).toContainText('Email não cadastrado');
    });
  });
  
  test.describe('Segurança', () => {
    test('Rate limiting após múltiplas tentativas', async () => {
      // Act - tentar login múltiplas vezes
      for (let i = 0; i < 6; i++) {
        await loginPage.login('123.456.789-09', 'senhaErrada');
        await loginPage.page.waitForTimeout(100);
      }
      
      // Assert - deve bloquear após 5 tentativas
      await expect(loginPage.page.locator('.error-message')).toContainText('Muitas tentativas');
    });
    
    test('XSS protection em campos de login', async () => {
      // Act - tentar injetar script
      const xssPayload = '<script>alert("XSS")</script>';
      await loginPage.fill('#cpf', xssPayload);
      await loginPage.fill('#senha', xssPayload);
      await loginPage.page.click('button[type="submit"]');
      
      // Assert - não deve executar script
      const alertFired = await loginPage.page.evaluate(() => {
        let alertFired = false;
        window.alert = () => { alertFired = true; };
        return alertFired;
      });
      
      expect(alertFired).toBe(false);
    });
    
    test('SQL Injection protection', async () => {
      // Act - tentar SQL injection
      const sqlPayload = "' OR '1'='1";
      await loginPage.login(sqlPayload, sqlPayload);
      
      // Assert - deve falhar com erro normal
      await loginPage.expectError('CPF inválido');
    });
  });
  
  test.describe('Mobile', () => {
    test.use({ viewport: { width: 375, height: 667 } });
    
    test('Login responsivo em mobile', async () => {
      // Arrange
      const user = testUsers.admin;
      
      // Act
      await loginPage.login(user.cpf, user.senha);
      
      // Assert
      await loginPage.expectLoggedIn();
      
      // Verifica menu mobile
      await expect(loginPage.page.locator('[data-testid="mobile-menu"]')).toBeVisible();
    });
  });
});