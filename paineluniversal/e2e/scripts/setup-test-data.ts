/**
 * 🔧 SCRIPT DE SETUP DE DADOS DE TESTE
 * Cria dados necessários no banco para execução dos testes E2E
 */

import axios from 'axios';
import { testUsers, staticTestData, TestDataFactory } from '../tests/fixtures/test-data';

const API_URL = process.env.API_URL || 'http://localhost:8000/api';

interface SetupResult {
  success: boolean;
  message: string;
  data?: any;
}

class TestDataSetup {
  private token: string = '';
  
  /**
   * Executa setup completo
   */
  async setupAll(): Promise<void> {
    console.log('🚀 Iniciando setup de dados de teste...\n');
    
    try {
      // 1. Criar usuários de teste
      await this.setupUsers();
      
      // 2. Fazer login como admin
      await this.loginAsAdmin();
      
      // 3. Criar evento de teste
      await this.setupEvento();
      
      // 4. Criar produtos de teste
      await this.setupProdutos();
      
      // 5. Criar listas
      await this.setupListas();
      
      console.log('\n✅ Setup concluído com sucesso!');
      
    } catch (error) {
      console.error('\n❌ Erro no setup:', error);
      process.exit(1);
    }
  }
  
  /**
   * Cria usuários de teste
   */
  private async setupUsers(): Promise<void> {
    console.log('👥 Criando usuários de teste...');
    
    for (const [role, user] of Object.entries(testUsers)) {
      try {
        const response = await axios.post(`${API_URL}/auth/register`, {
          nome: user.nome,
          email: user.email,
          cpf: user.cpf,
          senha: user.senha,
          role: user.role
        });
        
        console.log(`   ✓ ${role}: ${user.email}`);
        
      } catch (error: any) {
        // Se usuário já existe, não é erro
        if (error.response?.status === 409) {
          console.log(`   ⚠ ${role}: já existe`);
        } else {
          throw error;
        }
      }
    }
  }
  
  /**
   * Faz login como admin
   */
  private async loginAsAdmin(): Promise<void> {
    console.log('\n🔐 Fazendo login como admin...');
    
    try {
      const response = await axios.post(`${API_URL}/auth/login`, {
        cpf: testUsers.admin.cpf,
        senha: testUsers.admin.senha
      });
      
      this.token = response.data.access_token;
      axios.defaults.headers.common['Authorization'] = `Bearer ${this.token}`;
      
      console.log('   ✓ Login realizado com sucesso');
      
    } catch (error) {
      console.error('   ✗ Erro no login:', error);
      throw error;
    }
  }
  
  /**
   * Cria evento de teste
   */
  private async setupEvento(): Promise<void> {
    console.log('\n📅 Criando evento de teste...');
    
    try {
      // Verificar se já existe
      const searchResponse = await axios.get(`${API_URL}/eventos`, {
        params: { search: staticTestData.defaultEvento.nome }
      });
      
      if (searchResponse.data.items?.length > 0) {
        console.log('   ⚠ Evento de teste já existe');
        return;
      }
      
      // Criar novo evento
      const response = await axios.post(
        `${API_URL}/eventos`,
        {
          ...staticTestData.defaultEvento,
          organizador_id: 1 // Admin ID
        },
        {
          headers: { Authorization: `Bearer ${this.token}` }
        }
      );
      
      console.log(`   ✓ Evento criado: ${response.data.nome}`);
      
    } catch (error: any) {
      if (error.response?.status === 409) {
        console.log('   ⚠ Evento já existe');
      } else {
        console.error('   ✗ Erro ao criar evento:', error.response?.data);
        throw error;
      }
    }
  }
  
  /**
   * Cria produtos de teste
   */
  private async setupProdutos(): Promise<void> {
    console.log('\n📦 Criando produtos de teste...');
    
    for (const produto of staticTestData.defaultProdutos) {
      try {
        const response = await axios.post(
          `${API_URL}/produtos`,
          {
            ...produto,
            estoque_inicial: 100,
            ativo: true
          },
          {
            headers: { Authorization: `Bearer ${this.token}` }
          }
        );
        
        console.log(`   ✓ Produto criado: ${produto.nome}`);
        
      } catch (error: any) {
        if (error.response?.status === 409) {
          console.log(`   ⚠ Produto já existe: ${produto.nome}`);
        } else {
          console.error(`   ✗ Erro ao criar produto:`, error.response?.data);
        }
      }
    }
  }
  
  /**
   * Cria listas de teste
   */
  private async setupListas(): Promise<void> {
    console.log('\n📋 Criando listas de teste...');
    
    // Buscar evento de teste
    const eventosResponse = await axios.get(`${API_URL}/eventos`, {
      params: { search: staticTestData.defaultEvento.nome },
      headers: { Authorization: `Bearer ${this.token}` }
    });
    
    if (eventosResponse.data.items?.length === 0) {
      console.log('   ⚠ Evento não encontrado, pulando listas');
      return;
    }
    
    const eventoId = eventosResponse.data.items[0].id;
    
    for (const [tipo, lista] of Object.entries(staticTestData.listas)) {
      try {
        const response = await axios.post(
          `${API_URL}/eventos/${eventoId}/listas`,
          lista,
          {
            headers: { Authorization: `Bearer ${this.token}` }
          }
        );
        
        console.log(`   ✓ Lista criada: ${lista.nome}`);
        
      } catch (error: any) {
        if (error.response?.status === 409) {
          console.log(`   ⚠ Lista já existe: ${lista.nome}`);
        } else {
          console.error(`   ✗ Erro ao criar lista:`, error.response?.data);
        }
      }
    }
  }
  
  /**
   * Limpa dados de teste
   */
  async cleanup(): Promise<void> {
    console.log('🧹 Limpando dados de teste...\n');
    
    try {
      await this.loginAsAdmin();
      
      // Buscar e deletar evento de teste
      const eventosResponse = await axios.get(`${API_URL}/eventos`, {
        params: { search: 'E2E' },
        headers: { Authorization: `Bearer ${this.token}` }
      });
      
      for (const evento of eventosResponse.data.items || []) {
        if (evento.nome.includes('E2E') || evento.nome.includes('Test')) {
          try {
            await axios.delete(`${API_URL}/eventos/${evento.id}`, {
              headers: { Authorization: `Bearer ${this.token}` }
            });
            console.log(`   ✓ Evento removido: ${evento.nome}`);
          } catch (error) {
            console.error(`   ✗ Erro ao remover evento: ${evento.nome}`);
          }
        }
      }
      
      console.log('\n✅ Limpeza concluída!');
      
    } catch (error) {
      console.error('\n❌ Erro na limpeza:', error);
    }
  }
  
  /**
   * Verifica saúde da API
   */
  async checkHealth(): Promise<boolean> {
    console.log('🏥 Verificando saúde da API...\n');
    
    try {
      const response = await axios.get(`${API_URL}/health`);
      
      if (response.data.status === 'healthy') {
        console.log('   ✓ API está saudável');
        
        // Verificar serviços
        for (const [service, status] of Object.entries(response.data.checks || {})) {
          console.log(`   ${status === 'healthy' ? '✓' : '✗'} ${service}: ${status}`);
        }
        
        return true;
      } else {
        console.log('   ⚠ API está degradada');
        return false;
      }
      
    } catch (error) {
      console.error('   ✗ API não está respondendo');
      return false;
    }
  }
}

// ===== EXECUÇÃO =====

async function main() {
  const setup = new TestDataSetup();
  
  // Verificar argumentos
  const args = process.argv.slice(2);
  const command = args[0];
  
  switch (command) {
    case 'cleanup':
      await setup.cleanup();
      break;
      
    case 'health':
      const healthy = await setup.checkHealth();
      process.exit(healthy ? 0 : 1);
      break;
      
    case 'setup':
    default:
      // Verificar saúde primeiro
      const apiHealthy = await setup.checkHealth();
      if (!apiHealthy) {
        console.error('\n❌ API não está saudável. Abortando setup.');
        process.exit(1);
      }
      
      // Executar setup
      await setup.setupAll();
      break;
  }
}

// Executar se chamado diretamente
if (require.main === module) {
  main().catch(error => {
    console.error('Erro fatal:', error);
    process.exit(1);
  });
}

export { TestDataSetup };