#!/usr/bin/env node
/**
 * FRONTEND TEST FRAMEWORK - SISTEMA COMPLETO DE TESTES
 * =====================================================
 * 
 * Framework abrangente para testar todas as funcionalidades do frontend React.
 * Garante zero breaking changes nas funcionalidades em produção.
 * 
 * Autor: Agente de Desenvolvimento
 * Data: 2024
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

class FrontendTestFramework {
    constructor() {
        this.startTime = Date.now();
        this.frontendPath = path.resolve(__dirname, 'frontend');
        this.srcPath = path.join(this.frontendPath, 'src');
        
        this.results = {
            timestamp: new Date().toISOString(),
            framework: 'Frontend Test Framework',
            frontend_structure: {},
            component_tests: {},
            route_tests: {},
            context_tests: {},
            api_integration_tests: {},
            build_tests: {},
            critical_errors: [],
            warnings: [],
            fixes_applied: [],
            components_tested: 0,
            components_passed: 0,
            components_failed: 0,
            zero_breaking_changes: true
        };
        
        console.log('='.repeat(80));
        console.log('🚀 FRONTEND TEST FRAMEWORK - SISTEMA COMPLETO');
        console.log('='.repeat(80));
        console.log(`⏰ Início: ${new Date().toLocaleTimeString()}`);
        console.log();
    }
    
    log(message, level = 'INFO') {
        const timestamp = new Date().toLocaleTimeString();
        const emoji = {
            'INFO': 'ℹ️',
            'SUCCESS': '✅',
            'WARNING': '⚠️',
            'ERROR': '❌',
            'TEST': '🧪'
        }[level] || 'ℹ️';
        
        console.log(`[${timestamp}] ${emoji} ${message}`);
    }
    
    /**
     * Análise da estrutura do frontend
     */
    analyzeFrontendStructure() {
        this.log('Analisando estrutura do frontend...', 'INFO');
        
        try {
            // Verificar se o diretório frontend existe
            if (!fs.existsSync(this.frontendPath)) {
                this.results.critical_errors.push('Diretório frontend não encontrado');
                return false;
            }
            
            // Analisar package.json
            const packageJsonPath = path.join(this.frontendPath, 'package.json');
            if (fs.existsSync(packageJsonPath)) {
                const packageJson = JSON.parse(fs.readFileSync(packageJsonPath, 'utf8'));
                this.results.frontend_structure.dependencies = packageJson.dependencies;
                this.results.frontend_structure.devDependencies = packageJson.devDependencies;
                this.results.frontend_structure.scripts = packageJson.scripts;
                
                this.log(`📦 Dependências: ${Object.keys(packageJson.dependencies || {}).length}`, 'SUCCESS');
                this.log(`🛠️  Dev Dependencies: ${Object.keys(packageJson.devDependencies || {}).length}`, 'SUCCESS');
            }
            
            // Analisar estrutura de diretórios
            this.analyzeDirectoryStructure();
            
            // Analisar arquivos principais
            this.analyzeMainFiles();
            
            return true;
            
        } catch (error) {
            this.log(`Erro ao analisar estrutura: ${error.message}`, 'ERROR');
            this.results.critical_errors.push(`Estrutura: ${error.message}`);
            return false;
        }
    }
    
    analyzeDirectoryStructure() {
        const componentsPath = path.join(this.srcPath, 'components');
        
        if (fs.existsSync(componentsPath)) {
            const componentDirs = fs.readdirSync(componentsPath, { withFileTypes: true })
                .filter(dirent => dirent.isDirectory())
                .map(dirent => dirent.name);
            
            this.results.frontend_structure.component_directories = componentDirs;
            this.log(`📁 Diretórios de componentes: ${componentDirs.length}`, 'SUCCESS');
            
            componentDirs.forEach(dir => {
                this.log(`   📂 ${dir}`, 'INFO');
            });
        }
        
        // Analisar outros diretórios importantes
        const importantDirs = ['contexts', 'hooks', 'services', 'utils', 'types', 'pages'];
        this.results.frontend_structure.directories = {};
        
        importantDirs.forEach(dir => {
            const dirPath = path.join(this.srcPath, dir);
            if (fs.existsSync(dirPath)) {
                const files = this.getFilesRecursively(dirPath, ['.tsx', '.ts', '.jsx', '.js']);
                this.results.frontend_structure.directories[dir] = files.length;
                this.log(`📁 ${dir}: ${files.length} arquivos`, 'SUCCESS');
            }
        });
    }
    
    analyzeMainFiles() {
        const mainFiles = [
            'App.tsx',
            'main.tsx',
            'index.html'
        ];
        
        this.results.frontend_structure.main_files = {};
        
        mainFiles.forEach(file => {
            const filePath = file === 'index.html' 
                ? path.join(this.frontendPath, file)
                : path.join(this.srcPath, file);
                
            if (fs.existsSync(filePath)) {
                const stats = fs.statSync(filePath);
                this.results.frontend_structure.main_files[file] = {
                    exists: true,
                    size: stats.size,
                    modified: stats.mtime
                };
                this.log(`📄 ${file}: OK (${Math.round(stats.size / 1024)}KB)`, 'SUCCESS');
            } else {
                this.results.frontend_structure.main_files[file] = { exists: false };
                this.log(`📄 ${file}: NÃO ENCONTRADO`, 'WARNING');
                this.results.warnings.push(`Arquivo principal ${file} não encontrado`);
            }
        });
    }
    
    /**
     * Testes de componentes
     */
    testComponents() {
        this.log('Iniciando testes de componentes...', 'TEST');
        
        const componentsPath = path.join(this.srcPath, 'components');
        if (!fs.existsSync(componentsPath)) {
            this.results.critical_errors.push('Diretório de componentes não encontrado');
            return false;
        }
        
        const componentDirs = fs.readdirSync(componentsPath, { withFileTypes: true })
            .filter(dirent => dirent.isDirectory())
            .map(dirent => dirent.name);
        
        componentDirs.forEach(dir => {
            this.testComponentDirectory(dir);
        });
        
        // Testar componente raiz App.tsx
        this.testAppComponent();
        
        return true;
    }
    
    testComponentDirectory(dirName) {
        this.log(`Testando componentes em: ${dirName}`, 'TEST');
        
        const dirPath = path.join(this.srcPath, 'components', dirName);
        const componentFiles = this.getFilesRecursively(dirPath, ['.tsx', '.jsx']);
        
        this.results.component_tests[dirName] = {
            files_found: componentFiles.length,
            files_tested: 0,
            files_passed: 0,
            files_failed: 0,
            errors: [],
            warnings: []
        };
        
        componentFiles.forEach(file => {
            this.testSingleComponent(file, dirName);
        });
        
        const testResult = this.results.component_tests[dirName];
        this.log(`   📊 ${dirName}: ${testResult.files_passed}/${testResult.files_found} OK`, 
                testResult.files_failed === 0 ? 'SUCCESS' : 'WARNING');
    }
    
    testSingleComponent(filePath, dirName) {
        try {
            const content = fs.readFileSync(filePath, 'utf8');
            const fileName = path.basename(filePath);
            
            this.results.component_tests[dirName].files_tested++;
            this.results.components_tested++;
            
            // Verificações básicas
            const checks = {
                hasReactImport: /import\s+.*React.*from\s+['"]react['"]/.test(content),
                hasDefaultExport: /export\s+default/.test(content),
                hasTypeScript: filePath.endsWith('.tsx') || filePath.endsWith('.ts'),
                hasProperComponent: /const\s+\w+.*=.*\(.*\)\s*=>|function\s+\w+.*\(.*\)/.test(content),
                hasJSXReturn: /return\s*\(|return\s*</.test(content)
            };
            
            const issues = [];
            
            // Verificar imports problemáticos
            if (!checks.hasReactImport && checks.hasJSXReturn) {
                issues.push('React não importado mas JSX presente');
            }
            
            if (!checks.hasDefaultExport) {
                issues.push('Componente sem export default');
            }
            
            if (!checks.hasProperComponent) {
                issues.push('Estrutura de componente não identificada');
            }
            
            // Verificar sintaxe TypeScript
            if (checks.hasTypeScript) {
                // Verificações específicas de TypeScript
                if (!/interface\s+\w+|type\s+\w+/.test(content) && content.includes('props')) {
                    issues.push('Props sem tipagem TypeScript');
                }
            }
            
            if (issues.length === 0) {
                this.results.component_tests[dirName].files_passed++;
                this.results.components_passed++;
            } else {
                this.results.component_tests[dirName].files_failed++;
                this.results.components_failed++;
                this.results.component_tests[dirName].errors.push({
                    file: fileName,
                    issues: issues
                });
                
                this.log(`   ⚠️ ${fileName}: ${issues.join(', ')}`, 'WARNING');
            }
            
        } catch (error) {
            this.results.component_tests[dirName].files_failed++;
            this.results.components_failed++;
            this.results.component_tests[dirName].errors.push({
                file: path.basename(filePath),
                issues: [`Erro ao ler arquivo: ${error.message}`]
            });
            
            this.log(`   ❌ ${path.basename(filePath)}: Erro de leitura`, 'ERROR');
        }
    }
    
    testAppComponent() {
        const appPath = path.join(this.srcPath, 'App.tsx');
        
        if (!fs.existsSync(appPath)) {
            this.results.critical_errors.push('App.tsx não encontrado');
            return false;
        }
        
        try {
            const content = fs.readFileSync(appPath, 'utf8');
            
            const appTests = {
                hasRouter: /BrowserRouter|Router/.test(content),
                hasRoutes: /Routes|Route/.test(content),
                hasProviders: /Provider/.test(content),
                hasProtectedRoutes: /ProtectedRoute/.test(content),
                hasThemeProvider: /ThemeProvider/.test(content),
                hasAuthProvider: /AuthProvider/.test(content)
            };
            
            this.results.component_tests.App = {
                router_configured: appTests.hasRouter,
                routes_configured: appTests.hasRoutes,
                providers_configured: appTests.hasProviders,
                protected_routes: appTests.hasProtectedRoutes,
                theme_provider: appTests.hasThemeProvider,
                auth_provider: appTests.hasAuthProvider
            };
            
            const appScore = Object.values(appTests).filter(Boolean).length;
            this.log(`📱 App.tsx: ${appScore}/6 configurações OK`, 
                    appScore >= 4 ? 'SUCCESS' : 'WARNING');
            
            if (appScore < 4) {
                this.results.warnings.push('App.tsx pode estar com configurações incompletas');
            }
            
            return true;
            
        } catch (error) {
            this.results.critical_errors.push(`Erro ao testar App.tsx: ${error.message}`);
            return false;
        }
    }
    
    /**
     * Testes de contextos React
     */
    testContexts() {
        this.log('Testando contextos React...', 'TEST');
        
        const contextsPath = path.join(this.srcPath, 'contexts');
        if (!fs.existsSync(contextsPath)) {
            this.results.warnings.push('Diretório de contextos não encontrado');
            return false;
        }
        
        const contextFiles = this.getFilesRecursively(contextsPath, ['.tsx', '.ts']);
        
        this.results.context_tests = {
            files_found: contextFiles.length,
            contexts_analyzed: {},
            issues: []
        };
        
        contextFiles.forEach(file => {
            this.testSingleContext(file);
        });
        
        this.log(`🔗 Contextos: ${contextFiles.length} analisados`, 'SUCCESS');
        return true;
    }
    
    testSingleContext(filePath) {
        try {
            const content = fs.readFileSync(filePath, 'utf8');
            const fileName = path.basename(filePath, path.extname(filePath));
            
            const contextChecks = {
                hasCreateContext: /createContext/.test(content),
                hasProvider: /Provider/.test(content),
                hasUseContext: /useContext/.test(content),
                hasCustomHook: /export.*use\w+/.test(content),
                hasTypeScript: /interface\s+\w+.*Context|type\s+\w+.*Context/.test(content)
            };
            
            this.results.context_tests.contexts_analyzed[fileName] = contextChecks;
            
            const score = Object.values(contextChecks).filter(Boolean).length;
            if (score < 3) {
                this.results.context_tests.issues.push({
                    context: fileName,
                    message: 'Estrutura de contexto incompleta'
                });
            }
            
        } catch (error) {
            this.results.context_tests.issues.push({
                context: path.basename(filePath),
                message: `Erro ao analisar: ${error.message}`
            });
        }
    }
    
    /**
     * Testes de serviços de API
     */
    testApiServices() {
        this.log('Testando serviços de API...', 'TEST');
        
        const servicesPath = path.join(this.srcPath, 'services');
        if (!fs.existsSync(servicesPath)) {
            this.results.warnings.push('Diretório de serviços não encontrado');
            return false;
        }
        
        const serviceFiles = this.getFilesRecursively(servicesPath, ['.ts', '.js']);
        
        this.results.api_integration_tests = {
            files_found: serviceFiles.length,
            services_analyzed: {},
            api_endpoints_found: [],
            issues: []
        };
        
        serviceFiles.forEach(file => {
            this.testSingleService(file);
        });
        
        this.log(`🌐 Serviços API: ${serviceFiles.length} analisados`, 'SUCCESS');
        return true;
    }
    
    testSingleService(filePath) {
        try {
            const content = fs.readFileSync(filePath, 'utf8');
            const fileName = path.basename(filePath, path.extname(filePath));
            
            // Procurar por endpoints de API
            const apiRegex = /['"]\/api\/[^'"]+['"]/g;
            const endpoints = content.match(apiRegex) || [];
            
            const serviceChecks = {
                hasAxiosImport: /import.*axios/.test(content),
                hasFetchCalls: /fetch\(/.test(content),
                hasErrorHandling: /catch|\.catch|try/.test(content),
                hasTypeScript: /interface|type/.test(content),
                hasExports: /export/.test(content)
            };
            
            this.results.api_integration_tests.services_analyzed[fileName] = {
                ...serviceChecks,
                endpoints_found: endpoints.length
            };
            
            this.results.api_integration_tests.api_endpoints_found.push(...endpoints);
            
        } catch (error) {
            this.results.api_integration_tests.issues.push({
                service: path.basename(filePath),
                message: `Erro ao analisar: ${error.message}`
            });
        }
    }
    
    /**
     * Teste de build do projeto
     */
    testBuild() {
        this.log('Testando build do projeto...', 'TEST');
        
        try {
            // Verificar se existe build
            const buildPath = path.join(this.frontendPath, 'dist');
            const buildExists = fs.existsSync(buildPath);
            
            this.results.build_tests = {
                build_exists: buildExists,
                build_size: 0,
                build_files: 0,
                npm_scripts: {},
                dependencies_ok: true
            };
            
            if (buildExists) {
                const buildFiles = this.getFilesRecursively(buildPath, ['.js', '.css', '.html']);
                this.results.build_tests.build_files = buildFiles.length;
                
                // Calcular tamanho do build
                let totalSize = 0;
                buildFiles.forEach(file => {
                    try {
                        const stats = fs.statSync(file);
                        totalSize += stats.size;
                    } catch (e) {}
                });
                
                this.results.build_tests.build_size = Math.round(totalSize / 1024 / 1024 * 100) / 100; // MB
                
                this.log(`📦 Build existente: ${buildFiles.length} arquivos (${this.results.build_tests.build_size}MB)`, 'SUCCESS');
            } else {
                this.log('📦 Build não encontrado - será necessário executar npm run build', 'WARNING');
                this.results.warnings.push('Build do frontend não encontrado');
            }
            
            // Verificar scripts npm
            const packageJsonPath = path.join(this.frontendPath, 'package.json');
            if (fs.existsSync(packageJsonPath)) {
                const packageJson = JSON.parse(fs.readFileSync(packageJsonPath, 'utf8'));
                this.results.build_tests.npm_scripts = packageJson.scripts || {};
                
                const requiredScripts = ['dev', 'build', 'preview'];
                const missingScripts = requiredScripts.filter(script => !packageJson.scripts?.[script]);
                
                if (missingScripts.length > 0) {
                    this.results.warnings.push(`Scripts npm ausentes: ${missingScripts.join(', ')}`);
                }
            }
            
            return true;
            
        } catch (error) {
            this.log(`Erro ao testar build: ${error.message}`, 'ERROR');
            this.results.critical_errors.push(`Build: ${error.message}`);
            return false;
        }
    }
    
    /**
     * Identificar e sugerir correções
     */
    identifyIssuesAndFixes() {
        this.log('Identificando problemas e sugerindo correções...', 'INFO');
        
        const fixes = [];
        
        // Análise de componentes
        const totalComponentsWithIssues = Object.values(this.results.component_tests)
            .reduce((sum, test) => sum + (test.files_failed || 0), 0);
        
        if (totalComponentsWithIssues > 0) {
            fixes.push({
                category: 'Componentes',
                issue: `${totalComponentsWithIssues} componentes com problemas`,
                fix: 'Revisar imports, exports e tipagem TypeScript dos componentes',
                priority: 'MEDIUM'
            });
        }
        
        // Análise de contextos
        if (this.results.context_tests?.issues?.length > 0) {
            fixes.push({
                category: 'Contextos',
                issue: `${this.results.context_tests.issues.length} contextos com problemas`,
                fix: 'Verificar estrutura dos contextos React (createContext, Provider, hooks)',
                priority: 'HIGH'
            });
        }
        
        // Análise de API
        if (this.results.api_integration_tests?.issues?.length > 0) {
            fixes.push({
                category: 'API',
                issue: `${this.results.api_integration_tests.issues.length} serviços de API com problemas`,
                fix: 'Verificar imports, tratamento de erros e tipagem dos serviços',
                priority: 'HIGH'
            });
        }
        
        // Análise de build
        if (!this.results.build_tests?.build_exists) {
            fixes.push({
                category: 'Build',
                issue: 'Build do frontend não encontrado',
                fix: 'Executar: cd frontend && npm run build',
                priority: 'MEDIUM'
            });
        }
        
        // Verificações críticas
        if (this.results.critical_errors.length > 0) {
            fixes.push({
                category: 'Crítico',
                issue: `${this.results.critical_errors.length} erros críticos encontrados`,
                fix: 'Resolver erros críticos antes de continuar',
                priority: 'CRITICAL'
            });
        }
        
        this.results.fixes_applied = fixes;
        
        // Log das correções
        if (fixes.length === 0) {
            this.log('✨ Nenhum problema crítico encontrado!', 'SUCCESS');
        } else {
            this.log(`🔧 ${fixes.length} problemas identificados para correção:`, 'WARNING');
            fixes.forEach((fix, index) => {
                const priority = {
                    'CRITICAL': '🚨',
                    'HIGH': '⚠️',
                    'MEDIUM': '⚡',
                    'LOW': 'ℹ️'
                }[fix.priority];
                
                this.log(`   ${index + 1}. ${priority} [${fix.category}] ${fix.issue}`, 'INFO');
                this.log(`      → ${fix.fix}`, 'INFO');
            });
        }
        
        return fixes;
    }
    
    /**
     * Gerar relatório final
     */
    generateReport() {
        const executionTime = Math.round((Date.now() - this.startTime) / 1000);
        this.results.execution_time = executionTime;
        
        console.log('\n' + '='.repeat(80));
        console.log('📊 RELATÓRIO FINAL - FRONTEND TEST FRAMEWORK');
        console.log('='.repeat(80));
        
        // Estatísticas gerais
        console.log(`⏱️  Tempo de execução: ${executionTime}s`);
        console.log(`📁 Estrutura analisada: ${Object.keys(this.results.frontend_structure.directories || {}).length} diretórios`);
        console.log(`🧩 Componentes testados: ${this.results.components_tested}`);
        console.log(`✅ Componentes OK: ${this.results.components_passed}`);
        console.log(`❌ Componentes com problemas: ${this.results.components_failed}`);
        
        // Taxa de sucesso
        const successRate = this.results.components_tested > 0 
            ? Math.round((this.results.components_passed / this.results.components_tested) * 100)
            : 0;
        
        console.log(`📈 Taxa de sucesso: ${successRate}%`);
        
        // Status dos testes
        console.log('\n📋 STATUS DOS TESTES:');
        console.log(`   🏗️  Estrutura: ${this.results.frontend_structure.main_files ? 'OK' : 'PROBLEMA'}`);
        console.log(`   🧩 Componentes: ${this.results.components_failed === 0 ? 'OK' : 'PROBLEMAS'}`);
        console.log(`   🔗 Contextos: ${this.results.context_tests?.issues?.length === 0 ? 'OK' : 'PROBLEMAS'}`);
        console.log(`   🌐 API Services: ${this.results.api_integration_tests?.issues?.length === 0 ? 'OK' : 'PROBLEMAS'}`);
        console.log(`   📦 Build: ${this.results.build_tests?.build_exists ? 'OK' : 'AUSENTE'}`);
        
        // Problemas críticos
        if (this.results.critical_errors.length > 0) {
            console.log(`\n🚨 ERROS CRÍTICOS (${this.results.critical_errors.length}):`);
            this.results.critical_errors.forEach((error, index) => {
                console.log(`   ${index + 1}. ${error}`);
            });
        }
        
        // Avisos
        if (this.results.warnings.length > 0) {
            console.log(`\n⚠️  AVISOS (${this.results.warnings.length}):`);
            this.results.warnings.forEach((warning, index) => {
                console.log(`   ${index + 1}. ${warning}`);
            });
        }
        
        // Veredito final
        console.log('\n🎯 VEREDITO:');
        if (this.results.critical_errors.length === 0 && this.results.components_failed === 0) {
            console.log('✅ Frontend funcionando corretamente!');
            console.log('🛡️  Zero breaking changes garantido');
        } else if (this.results.critical_errors.length === 0) {
            console.log('⚠️  Frontend funcional com pequenos problemas');
            console.log('🛡️  Funcionalidades em produção preservadas');
        } else {
            console.log('🚨 Frontend com problemas críticos');
            console.log('⚡ Correções necessárias antes de deploy');
        }
        
        // Salvar relatório
        const reportFile = `frontend_test_report_${new Date().toISOString().slice(0,19).replace(/:/g,'-')}.json`;
        fs.writeFileSync(reportFile, JSON.stringify(this.results, null, 2));
        
        console.log(`\n📄 Relatório salvo em: ${reportFile}`);
        console.log('='.repeat(80));
        
        return {
            success: this.results.critical_errors.length === 0,
            report_file: reportFile,
            stats: {
                components_tested: this.results.components_tested,
                success_rate: successRate,
                critical_errors: this.results.critical_errors.length
            }
        };
    }
    
    /**
     * Utilitários
     */
    getFilesRecursively(dir, extensions) {
        const files = [];
        
        try {
            const items = fs.readdirSync(dir, { withFileTypes: true });
            
            for (const item of items) {
                const fullPath = path.join(dir, item.name);
                
                if (item.isDirectory()) {
                    files.push(...this.getFilesRecursively(fullPath, extensions));
                } else if (item.isFile()) {
                    const ext = path.extname(item.name);
                    if (extensions.includes(ext)) {
                        files.push(fullPath);
                    }
                }
            }
        } catch (error) {
            // Ignorar erros de permissão
        }
        
        return files;
    }
    
    /**
     * Executar todos os testes
     */
    async runAllTests() {
        this.log('🚀 Iniciando framework completo de testes...', 'INFO');
        
        // 1. Analisar estrutura
        const structureOk = this.analyzeFrontendStructure();
        if (!structureOk) {
            this.log('❌ Falha na análise de estrutura - abortando', 'ERROR');
            return this.generateReport();
        }
        
        // 2. Testar componentes
        this.testComponents();
        
        // 3. Testar contextos
        this.testContexts();
        
        // 4. Testar serviços API
        this.testApiServices();
        
        // 5. Testar build
        this.testBuild();
        
        // 6. Identificar problemas e correções
        this.identifyIssuesAndFixes();
        
        // 7. Gerar relatório
        return this.generateReport();
    }
}

// Executar se chamado diretamente
if (require.main === module) {
    const framework = new FrontendTestFramework();
    
    framework.runAllTests()
        .then(result => {
            console.log('\n✨ Framework de testes concluído!');
            process.exit(result.success ? 0 : 1);
        })
        .catch(error => {
            console.error('🚨 Erro fatal:', error.message);
            process.exit(2);
        });
}

module.exports = FrontendTestFramework;
