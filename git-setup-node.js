const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

console.log('🚀 Configuração Automática do Git - Sistema Cesar');
console.log('='.repeat(50));

const projectPath = 'c:\\Users\\User\\OneDrive\\Desktop\\sistema-v6-novo\\paineluniversal';

try {
    // Navegar para o diretório do projeto
    process.chdir(projectPath);
    console.log(`📁 Navegando para: ${projectPath}`);

    // Verificar se Git está instalado
    try {
        const gitVersion = execSync('git --version', { encoding: 'utf8' });
        console.log(`✅ Git encontrado: ${gitVersion.trim()}`);
    } catch (error) {
        console.log('❌ Git não encontrado! Instale o Git primeiro.');
        process.exit(1);
    }

    // Configurar credenciais globais
    console.log('🔧 Configurando credenciais globais...');
    execSync('git config --global user.name "contatoroyalclubms-sudo"');
    execSync('git config --global user.email "contatoroyalclubms@gmail.com"');
    console.log('✅ Credenciais configuradas!');

    // Inicializar repositório se não existir
    if (!fs.existsSync('.git')) {
        console.log('📁 Inicializando repositório Git...');
        execSync('git init');
        execSync('git branch -M main');
        console.log('✅ Repositório inicializado!');
    } else {
        console.log('✅ Repositório Git já existe');
    }

    // Configurar remote origin
    console.log('🔗 Configurando remote origin...');
    try {
        execSync('git remote remove origin', { stdio: 'ignore' });
    } catch (error) {
        // Remote não existe, tudo bem
    }
    execSync('git remote add origin https://github.com/contatoroyalclubms-sudo/sistema-cesar.git');
    console.log('✅ Remote origin configurado!');

    // Verificar remote
    const remotes = execSync('git remote -v', { encoding: 'utf8' });
    console.log('📋 Remotes configurados:');
    console.log(remotes);

    // Criar .gitignore se não existir
    if (!fs.existsSync('.gitignore')) {
        console.log('📝 Criando .gitignore...');
        const gitignoreContent = `# Dependências
node_modules/
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
pip-log.txt
pip-delete-this-directory.txt

# IDEs
.vscode/
.idea/
*.swp
*.swo
*~

# Logs
*.log
logs/

# Arquivos do sistema
.DS_Store
Thumbs.db

# Arquivos de ambiente
.env
.env.local
.env.development.local
.env.test.local
.env.production.local

# Build
dist/
build/
*.min.js
*.min.css

# Cache
.cache/
.parcel-cache/

# Arquivos temporários
*.tmp
*.temp
nul

# Screenshots de teste
*.png
!github-*.png

# Relatórios
MEEP_*.json
MEEP_*.md
*_REPORT.json
*_SUMMARY.md`;
        
        fs.writeFileSync('.gitignore', gitignoreContent);
        console.log('✅ .gitignore criado!');
    }

    // Adicionar arquivos
    console.log('📦 Adicionando arquivos...');
    execSync('git add .');
    console.log('✅ Arquivos adicionados!');

    // Fazer commit
    console.log('💾 Fazendo commit...');
    const commitMessage = `🚀 Deploy inicial do Sistema Cesar V7 - ${new Date().toISOString()}`;
    execSync(`git commit -m "${commitMessage}"`);
    console.log('✅ Commit realizado!');

    console.log('\n🎉 CONFIGURAÇÃO CONCLUÍDA COM SUCESSO!');
    console.log('🔗 Repositório: https://github.com/contatoroyalclubms-sudo/sistema-cesar');
    console.log('\n📋 Próximos passos:');
    console.log('   1. Push para o repositório: git push -u origin main');
    console.log('   2. Configurar GitHub Actions');
    console.log('   3. Configurar deploy automático');

} catch (error) {
    console.error('❌ Erro durante a configuração:', error.message);
    process.exit(1);
}
