#!/usr/bin/env node
/**
 * One-Click MEEP Auditoria Automation
 * Executa captura completa, análise e geração de relatórios
 */

import { chromium } from 'playwright';
import fs from 'fs/promises';
import path from 'path';
import dotenv from 'dotenv';

// Carregar configurações
dotenv.config();

const CONFIG = {
    targetUrl: process.env.TARGET_URL || 'https://beta.portal.meep.com.br',
    projectName: process.env.PROJECT_NAME || 'MEEP_AUDITORIA',
    outputDir: process.env.OUTPUT_DIR || './data',
    loginUser: process.env.LOGIN_USER || '',
    loginPass: process.env.LOGIN_PASS || '',
    captureMode: process.env.CAPTURE_MODE || 'full'
};

// Criar estrutura de diretórios
async function setupDirectories() {
    const dirs = [
        'data/captures',
        'data/reports',
        'data/postman',
        'data/screenshots',
        'data/diffs'
    ];
    
    for (const dir of dirs) {
        await fs.mkdir(dir, { recursive: true });
    }
    console.log('✅ Diretórios criados');
}

// Capturar HAR e screenshots
async function captureHAR() {
    console.log('🔍 Iniciando captura HAR...');
    
    const browser = await chromium.launch({ 
        headless: false,
        args: ['--start-maximized']
    });
    
    const context = await browser.newContext({
        recordHar: { path: `data/captures/${CONFIG.projectName}_${Date.now()}.har` },
        viewport: { width: 1920, height: 1080 }
    });
    
    const page = await context.newPage();
    
    try {
        // Navegar para o site
        await page.goto(CONFIG.targetUrl);
        await page.screenshot({ path: 'data/screenshots/01_login_page.png' });
        
        // Fazer login se configurado
        if (CONFIG.loginUser && CONFIG.loginPass) {
            await page.fill('input[type="email"], input[name="email"], input[name="username"]', CONFIG.loginUser);
            await page.fill('input[type="password"], input[name="password"]', CONFIG.loginPass);
            await page.screenshot({ path: 'data/screenshots/02_login_filled.png' });
            
            await page.click('button[type="submit"], button:has-text("Entrar"), button:has-text("Login")');
            await page.waitForLoadState('networkidle');
            await page.screenshot({ path: 'data/screenshots/03_after_login.png' });
        }
        
        // Navegar por páginas principais
        const pages = [
            '/dashboard',
            '/eventos',
            '/relatorios',
            '/configuracoes'
        ];
        
        for (let i = 0; i < pages.length; i++) {
            try {
                await page.goto(CONFIG.targetUrl + pages[i]);
                await page.waitForLoadState('networkidle');
                await page.screenshot({ 
                    path: `data/screenshots/page_${i + 4}_${pages[i].replace('/', '')}.png` 
                });
            } catch (e) {
                console.log(`⚠️ Página ${pages[i]} não acessível`);
            }
        }
        
    } catch (error) {
        console.error('❌ Erro na captura:', error);
    } finally {
        await context.close();
        await browser.close();
    }
    
    console.log('✅ Captura HAR concluída');
}

// Analisar HAR e gerar relatórios
async function analyzeHAR() {
    console.log('📊 Analisando HAR...');
    
    const harFiles = await fs.readdir('data/captures');
    const latestHAR = harFiles.filter(f => f.endsWith('.har')).sort().pop();
    
    if (!latestHAR) {
        console.error('❌ Nenhum arquivo HAR encontrado');
        return;
    }
    
    const harContent = await fs.readFile(`data/captures/${latestHAR}`, 'utf8');
    const har = JSON.parse(harContent);
    
    // Análise de APIs
    const apis = {};
    const endpoints = new Set();
    
    har.log.entries.forEach(entry => {
        const url = new URL(entry.request.url);
        const endpoint = `${entry.request.method} ${url.pathname}`;
        
        endpoints.add(endpoint);
        
        if (!apis[url.hostname]) {
            apis[url.hostname] = [];
        }
        
        apis[url.hostname].push({
            method: entry.request.method,
            path: url.pathname,
            status: entry.response.status,
            time: entry.time,
            size: entry.response.content.size
        });
    });
    
    // Gerar relatório JSON
    const report = {
        timestamp: new Date().toISOString(),
        project: CONFIG.projectName,
        target: CONFIG.targetUrl,
        summary: {
            totalRequests: har.log.entries.length,
            uniqueEndpoints: endpoints.size,
            domains: Object.keys(apis).length,
            avgResponseTime: har.log.entries.reduce((acc, e) => acc + e.time, 0) / har.log.entries.length
        },
        apis: apis,
        endpoints: Array.from(endpoints)
    };
    
    await fs.writeFile(
        `data/reports/${CONFIG.projectName}_report_${Date.now()}.json`,
        JSON.stringify(report, null, 2)
    );
    
    console.log('✅ Relatório JSON gerado');
    
    // Gerar Markdown
    let markdown = `# Relatório de Auditoria - ${CONFIG.projectName}\n\n`;
    markdown += `**Data**: ${new Date().toLocaleString()}\n`;
    markdown += `**Target**: ${CONFIG.targetUrl}\n\n`;
    markdown += `## Resumo\n`;
    markdown += `- Total de Requisições: ${report.summary.totalRequests}\n`;
    markdown += `- Endpoints Únicos: ${report.summary.uniqueEndpoints}\n`;
    markdown += `- Domínios: ${report.summary.domains}\n`;
    markdown += `- Tempo Médio de Resposta: ${report.summary.avgResponseTime.toFixed(2)}ms\n\n`;
    markdown += `## Endpoints Capturados\n\n`;
    
    report.endpoints.forEach(endpoint => {
        markdown += `- \`${endpoint}\`\n`;
    });
    
    await fs.writeFile(
        `data/reports/${CONFIG.projectName}_report_${Date.now()}.md`,
        markdown
    );
    
    console.log('✅ Relatório Markdown gerado');
    
    return report;
}

// Gerar coleção Postman
async function generatePostman(report) {
    console.log('📮 Gerando coleção Postman...');
    
    const collection = {
        info: {
            name: `${CONFIG.projectName} - API Collection`,
            description: `Coleção gerada automaticamente em ${new Date().toISOString()}`,
            schema: "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
        },
        item: []
    };
    
    // Agrupar por domínio
    Object.entries(report.apis).forEach(([domain, requests]) => {
        const folder = {
            name: domain,
            item: []
        };
        
        // Criar requisições únicas
        const uniqueRequests = {};
        requests.forEach(req => {
            const key = `${req.method}_${req.path}`;
            if (!uniqueRequests[key]) {
                uniqueRequests[key] = req;
            }
        });
        
        Object.values(uniqueRequests).forEach(req => {
            folder.item.push({
                name: `${req.method} ${req.path}`,
                request: {
                    method: req.method,
                    header: [],
                    url: {
                        raw: `https://${domain}${req.path}`,
                        protocol: "https",
                        host: domain.split('.'),
                        path: req.path.split('/').filter(p => p)
                    }
                }
            });
        });
        
        collection.item.push(folder);
    });
    
    await fs.writeFile(
        `data/postman/${CONFIG.projectName}_collection_${Date.now()}.json`,
        JSON.stringify(collection, null, 2)
    );
    
    console.log('✅ Coleção Postman gerada');
}

// Executar pipeline completo
async function main() {
    console.log('🚀 Iniciando MEEP Auditoria One-Click');
    console.log(`📍 Target: ${CONFIG.targetUrl}`);
    console.log(`📁 Projeto: ${CONFIG.projectName}`);
    console.log('');
    
    try {
        await setupDirectories();
        await captureHAR();
        const report = await analyzeHAR();
        
        if (report) {
            await generatePostman(report);
        }
        
        console.log('\n✨ Auditoria concluída com sucesso!');
        console.log('📂 Artefatos salvos em ./data/');
        
        // Listar arquivos gerados
        const files = {
            captures: await fs.readdir('data/captures'),
            reports: await fs.readdir('data/reports'),
            postman: await fs.readdir('data/postman'),
            screenshots: await fs.readdir('data/screenshots')
        };
        
        console.log('\n📋 Arquivos gerados:');
        Object.entries(files).forEach(([dir, list]) => {
            console.log(`\n${dir}:`);
            list.forEach(file => console.log(`  - ${file}`));
        });
        
    } catch (error) {
        console.error('❌ Erro na execução:', error);
        process.exit(1);
    }
}

// Executar se chamado diretamente
if (import.meta.url === `file://${process.argv[1]}`) {
    main();
}

export { main, captureHAR, analyzeHAR, generatePostman };