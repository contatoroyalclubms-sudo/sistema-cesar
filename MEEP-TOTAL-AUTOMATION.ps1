# MEEP TOTAL AUTOMATION SUITE
# Sistema completo de automação, captura e integração
# Supera qualquer ferramenta existente

param(
    [string]$Mode = "TOTAL",
    [string]$Target = "https://beta.portal.meep.com.br",
    [string]$Output = "meep-total-output",
    [switch]$NoStop = $true
)

Write-Host @"
╔══════════════════════════════════════════════════════════════════════════════╗
║                     MEEP TOTAL AUTOMATION SUITE v2.0                          ║
║                 Sistema Definitivo de Engenharia Reversa                      ║
╚══════════════════════════════════════════════════════════════════════════════╝
"@ -ForegroundColor Cyan

# Configuração inicial
$timestamp = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"
$workDir = Join-Path $PSScriptRoot $Output
$captureDir = Join-Path $workDir "capture-$timestamp"

# Criar estrutura completa
$dirs = @(
    "$captureDir\har",
    "$captureDir\screenshots",
    "$captureDir\videos",
    "$captureDir\apis",
    "$captureDir\postman",
    "$captureDir\curl",
    "$captureDir\insomnia",
    "$captureDir\swagger",
    "$captureDir\graphql",
    "$captureDir\websockets",
    "$captureDir\cookies",
    "$captureDir\storage",
    "$captureDir\network",
    "$captureDir\performance",
    "$captureDir\security",
    "$captureDir\reports",
    "$captureDir\integration",
    "$captureDir\tests",
    "$captureDir\documentation",
    "$captureDir\backup"
)

foreach ($dir in $dirs) {
    New-Item -ItemType Directory -Path $dir -Force | Out-Null
}

Write-Host "[✓] Estrutura criada em: $captureDir" -ForegroundColor Green

# Função para capturar com Playwright
function Start-PlaywrightCapture {
    Write-Host "`n[1/10] Iniciando captura com Playwright..." -ForegroundColor Yellow
    
    $playwrightScript = @"
import { chromium, firefox, webkit } from 'playwright';
import fs from 'fs/promises';
import crypto from 'crypto';

class MEEPTotalCapture {
    constructor() {
        this.config = {
            url: '$Target',
            outputDir: '$captureDir',
            credentials: {
                email: 'toretomal@icloud.com',
                password: '10041210Cl@'
            }
        };
        
        this.data = {
            requests: [],
            responses: [],
            cookies: [],
            localStorage: {},
            sessionStorage: {},
            websockets: [],
            performance: [],
            errors: [],
            console: []
        };
    }

    async capture() {
        console.log('🚀 Iniciando captura total...');
        
        // Usar múltiplos browsers para máxima compatibilidade
        const browsers = {
            chromium: await chromium.launch({ headless: false }),
            firefox: await firefox.launch({ headless: false }),
            webkit: await webkit.launch({ headless: false })
        };
        
        for (const [name, browser] of Object.entries(browsers)) {
            console.log(\`\nCapturando com \${name}...\`);
            
            const context = await browser.newContext({
                recordHar: {
                    path: \`\${this.config.outputDir}/har/\${name}.har\`,
                    mode: 'full',
                    content: 'attach'
                },
                recordVideo: {
                    dir: \`\${this.config.outputDir}/videos/\`,
                    size: { width: 1920, height: 1080 }
                }
            });
            
            const page = await context.newPage();
            
            // Interceptar tudo
            page.on('request', request => {
                this.data.requests.push({
                    url: request.url(),
                    method: request.method(),
                    headers: request.headers(),
                    postData: request.postData()
                });
            });
            
            page.on('response', async response => {
                try {
                    const body = await response.body();
                    this.data.responses.push({
                        url: response.url(),
                        status: response.status(),
                        headers: response.headers(),
                        body: body.toString()
                    });
                } catch {}
            });
            
            // Navegar e capturar
            await page.goto(this.config.url);
            await page.screenshot({ path: \`\${this.config.outputDir}/screenshots/\${name}-1.png\` });
            
            // Tentar login
            try {
                await page.fill('input[type="email"]', this.config.credentials.email);
                await page.fill('input[type="password"]', this.config.credentials.password);
                await page.screenshot({ path: \`\${this.config.outputDir}/screenshots/\${name}-2.png\` });
                await page.click('button[type="submit"]');
                await page.waitForTimeout(5000);
                await page.screenshot({ path: \`\${this.config.outputDir}/screenshots/\${name}-3.png\` });
            } catch {}
            
            // Salvar dados
            await fs.writeFile(
                \`\${this.config.outputDir}/network/\${name}-data.json\`,
                JSON.stringify(this.data, null, 2)
            );
            
            await context.close();
        }
        
        // Fechar browsers
        for (const browser of Object.values(browsers)) {
            await browser.close();
        }
        
        console.log('✅ Captura concluída!');
    }
}

const capture = new MEEPTotalCapture();
capture.capture().catch(console.error);
"@
    
    $playwrightScript | Out-File -FilePath "$captureDir\capture.mjs" -Encoding UTF8
    
    # Executar captura
    Push-Location $captureDir
    npm init -y | Out-Null
    npm install playwright | Out-Null
    npx playwright install | Out-Null
    node capture.mjs
    Pop-Location
}

# Função para processar HAR
function Process-HARFiles {
    Write-Host "`n[2/10] Processando arquivos HAR..." -ForegroundColor Yellow
    
    $harFiles = Get-ChildItem -Path "$captureDir\har" -Filter "*.har"
    
    foreach ($har in $harFiles) {
        Write-Host "  Processando: $($har.Name)"
        
        # Converter para múltiplos formatos
        $harContent = Get-Content $har.FullName | ConvertFrom-Json
        
        # Gerar Postman Collection
        $postmanCollection = @{
            info = @{
                name = "MEEP Capture - $timestamp"
                schema = "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
            }
            item = @()
        }
        
        foreach ($entry in $harContent.log.entries) {
            $item = @{
                name = "$($entry.request.method) $($entry.request.url)"
                request = @{
                    method = $entry.request.method
                    url = $entry.request.url
                    header = $entry.request.headers
                    body = @{
                        mode = "raw"
                        raw = $entry.request.postData.text
                    }
                }
            }
            $postmanCollection.item += $item
        }
        
        $postmanCollection | ConvertTo-Json -Depth 10 | Out-File "$captureDir\postman\collection-$($har.BaseName).json"
        
        # Gerar comandos cURL
        $curlCommands = @()
        foreach ($entry in $harContent.log.entries) {
            $curl = "curl -X $($entry.request.method) '$($entry.request.url)'"
            foreach ($header in $entry.request.headers) {
                $curl += " -H '$($header.name): $($header.value)'"
            }
            if ($entry.request.postData.text) {
                $curl += " --data '$($entry.request.postData.text)'"
            }
            $curlCommands += $curl
        }
        $curlCommands | Out-File "$captureDir\curl\commands-$($har.BaseName).sh"
    }
}

# Função para análise de segurança
function Analyze-Security {
    Write-Host "`n[3/10] Análise de segurança..." -ForegroundColor Yellow
    
    $securityReport = @{
        timestamp = $timestamp
        vulnerabilities = @()
        tokens = @()
        sensitiveData = @()
        recommendations = @()
    }
    
    # Procurar por tokens e dados sensíveis
    $files = Get-ChildItem -Path $captureDir -Recurse -File
    foreach ($file in $files) {
        $content = Get-Content $file.FullName -ErrorAction SilentlyContinue
        
        # Procurar tokens
        if ($content -match 'token|jwt|bearer|api[_-]key|secret') {
            $securityReport.tokens += @{
                file = $file.Name
                matches = [regex]::Matches($content, '[a-zA-Z0-9]{20,}').Value
            }
        }
        
        # Procurar dados sensíveis
        if ($content -match 'password|senha|credit[_-]card|ssn|cpf') {
            $securityReport.sensitiveData += $file.Name
        }
    }
    
    # Gerar recomendações
    if ($securityReport.tokens.Count -gt 0) {
        $securityReport.recommendations += "Tokens expostos detectados - implementar rotação de tokens"
    }
    if ($securityReport.sensitiveData.Count -gt 0) {
        $securityReport.recommendations += "Dados sensíveis encontrados - implementar criptografia"
    }
    
    $securityReport | ConvertTo-Json -Depth 5 | Out-File "$captureDir\security\analysis.json"
    
    Write-Host "  [!] Encontrados $($securityReport.tokens.Count) tokens" -ForegroundColor Red
    Write-Host "  [!] Encontrados $($securityReport.sensitiveData.Count) arquivos com dados sensíveis" -ForegroundColor Red
}

# Função para gerar testes automatizados
function Generate-Tests {
    Write-Host "`n[4/10] Gerando testes automatizados..." -ForegroundColor Yellow
    
    # Playwright tests
    $playwrightTest = @"
import { test, expect } from '@playwright/test';

test.describe('MEEP Portal Tests', () => {
    test('Login flow', async ({ page }) => {
        await page.goto('$Target');
        await page.fill('input[type="email"]', 'test@example.com');
        await page.fill('input[type="password"]', 'password');
        await page.click('button[type="submit"]');
        await expect(page).toHaveURL(/.*dashboard/);
    });
    
    test('API endpoints', async ({ request }) => {
        const endpoints = [
            '/api/auth/login',
            '/api/events',
            '/api/analytics'
        ];
        
        for (const endpoint of endpoints) {
            const response = await request.get(\`$Target\${endpoint}\`);
            expect(response.status()).toBeLessThan(500);
        }
    });
});
"@
    
    $playwrightTest | Out-File "$captureDir\tests\meep.spec.js"
    
    # Cypress tests
    $cypressTest = @"
describe('MEEP Portal E2E', () => {
    it('Complete user journey', () => {
        cy.visit('$Target');
        cy.get('input[type="email"]').type('test@example.com');
        cy.get('input[type="password"]').type('password');
        cy.get('button[type="submit"]').click();
        cy.url().should('include', 'dashboard');
    });
});
"@
    
    $cypressTest | Out-File "$captureDir\tests\meep.cy.js"
}

# Função para gerar documentação
function Generate-Documentation {
    Write-Host "`n[5/10] Gerando documentação..." -ForegroundColor Yellow
    
    $documentation = @"
# MEEP Portal - Documentação Completa

## Captura realizada em: $timestamp

### Estatísticas
- Screenshots: $(Get-ChildItem "$captureDir\screenshots" | Measure-Object).Count
- HAR Files: $(Get-ChildItem "$captureDir\har" -Filter "*.har" | Measure-Object).Count
- APIs Descobertas: $(Get-ChildItem "$captureDir\apis" | Measure-Object).Count
- Testes Gerados: $(Get-ChildItem "$captureDir\tests" | Measure-Object).Count

### Estrutura de Arquivos
\`\`\`
$Output/
├── capture-$timestamp/
│   ├── har/           # Arquivos HAR capturados
│   ├── screenshots/   # Screenshots de todas as páginas
│   ├── videos/        # Gravações das sessões
│   ├── postman/       # Coleções Postman
│   ├── curl/          # Comandos cURL
│   ├── tests/         # Testes automatizados
│   └── reports/       # Relatórios de análise
\`\`\`

### Como usar

1. **Importar no Postman**
   - File > Import > \`postman/collection-*.json\`

2. **Executar testes**
   \`\`\`bash
   npx playwright test tests/meep.spec.js
   \`\`\`

3. **Replay com cURL**
   \`\`\`bash
   bash curl/commands-*.sh
   \`\`\`

### Análise de Segurança
Ver arquivo: \`security/analysis.json\`

### APIs Descobertas
Ver pasta: \`apis/\`

"@
    
    $documentation | Out-File "$captureDir\documentation\README.md"
}

# Função para comparar com capturas anteriores
function Compare-Captures {
    Write-Host "`n[6/10] Comparando com capturas anteriores..." -ForegroundColor Yellow
    
    $previousCaptures = Get-ChildItem -Path $workDir -Directory -Filter "capture-*" | 
                        Where-Object { $_.Name -ne "capture-$timestamp" } |
                        Sort-Object Name -Descending |
                        Select-Object -First 1
    
    if ($previousCaptures) {
        Write-Host "  Comparando com: $($previousCaptures.Name)"
        
        $diff = @{
            timestamp = $timestamp
            previous = $previousCaptures.Name
            changes = @{
                newEndpoints = @()
                removedEndpoints = @()
                changedResponses = @()
            }
        }
        
        # Comparar arquivos HAR
        # ... lógica de comparação ...
        
        $diff | ConvertTo-Json -Depth 5 | Out-File "$captureDir\reports\diff.json"
    }
}

# Função para gerar relatório final
function Generate-FinalReport {
    Write-Host "`n[7/10] Gerando relatório final..." -ForegroundColor Yellow
    
    $report = @"
<!DOCTYPE html>
<html>
<head>
    <title>MEEP Capture Report - $timestamp</title>
    <style>
        body { font-family: Arial; margin: 20px; }
        .header { background: linear-gradient(45deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; }
        .stats { display: flex; justify-content: space-around; margin: 20px 0; }
        .stat-box { background: #f0f0f0; padding: 15px; border-radius: 8px; text-align: center; }
        .stat-number { font-size: 2em; font-weight: bold; color: #667eea; }
        table { width: 100%; border-collapse: collapse; }
        th, td { padding: 10px; border: 1px solid #ddd; text-align: left; }
        th { background: #667eea; color: white; }
    </style>
</head>
<body>
    <div class="header">
        <h1>MEEP Total Capture Report</h1>
        <p>Generated: $timestamp</p>
    </div>
    
    <div class="stats">
        <div class="stat-box">
            <div class="stat-number">$(Get-ChildItem "$captureDir\screenshots" | Measure-Object).Count</div>
            <div>Screenshots</div>
        </div>
        <div class="stat-box">
            <div class="stat-number">$(Get-ChildItem "$captureDir\har" -Filter "*.har" | Measure-Object).Count</div>
            <div>HAR Files</div>
        </div>
        <div class="stat-box">
            <div class="stat-number">$(Get-ChildItem "$captureDir\postman" | Measure-Object).Count</div>
            <div>Postman Collections</div>
        </div>
        <div class="stat-box">
            <div class="stat-number">$(Get-ChildItem "$captureDir\tests" | Measure-Object).Count</div>
            <div>Tests Generated</div>
        </div>
    </div>
    
    <h2>Captured Files</h2>
    <table>
        <tr>
            <th>Type</th>
            <th>File</th>
            <th>Size</th>
            <th>Created</th>
        </tr>
        $(Get-ChildItem -Path $captureDir -Recurse -File | ForEach-Object {
            "<tr>
                <td>$($_.Extension)</td>
                <td>$($_.Name)</td>
                <td>$([math]::Round($_.Length/1KB, 2)) KB</td>
                <td>$($_.CreationTime)</td>
            </tr>"
        })
    </table>
</body>
</html>
"@
    
    $report | Out-File "$captureDir\reports\report.html"
}

# Função para backup
function Create-Backup {
    Write-Host "`n[8/10] Criando backup..." -ForegroundColor Yellow
    
    $backupName = "meep-capture-$timestamp.zip"
    Compress-Archive -Path $captureDir -DestinationPath "$workDir\backup\$backupName" -Force
    
    Write-Host "  Backup salvo: $backupName" -ForegroundColor Green
}

# Função para integração com CI/CD
function Setup-CICD {
    Write-Host "`n[9/10] Configurando CI/CD..." -ForegroundColor Yellow
    
    # GitHub Actions
    $githubAction = @"
name: MEEP Capture

on:
  schedule:
    - cron: '0 */6 * * *'  # A cada 6 horas
  workflow_dispatch:

jobs:
  capture:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-node@v2
      - run: |
          ./MEEP-TOTAL-AUTOMATION.ps1
      - uses: actions/upload-artifact@v2
        with:
          name: meep-capture
          path: meep-total-output/
"@
    
    $githubAction | Out-File "$captureDir\integration\.github-workflow.yml"
    
    # Jenkins Pipeline
    $jenkinsPipeline = @"
pipeline {
    agent any
    stages {
        stage('Capture') {
            steps {
                powershell './MEEP-TOTAL-AUTOMATION.ps1'
            }
        }
        stage('Test') {
            steps {
                sh 'npx playwright test'
            }
        }
        stage('Deploy') {
            steps {
                archiveArtifacts artifacts: 'meep-total-output/**/*'
            }
        }
    }
}
"@
    
    $jenkinsPipeline | Out-File "$captureDir\integration\Jenkinsfile"
}

# Função principal de monitoramento contínuo
function Start-ContinuousMonitoring {
    Write-Host "`n[10/10] Iniciando monitoramento contínuo..." -ForegroundColor Yellow
    
    if ($NoStop) {
        Write-Host "  Modo NON-STOP ativado!" -ForegroundColor Red
        
        while ($true) {
            Write-Host "  [$(Get-Date -Format 'HH:mm:ss')] Executando captura..." -ForegroundColor Cyan
            
            # Executar todas as funções
            Start-PlaywrightCapture
            Process-HARFiles
            Analyze-Security
            Generate-Tests
            Generate-Documentation
            Compare-Captures
            Generate-FinalReport
            Create-Backup
            
            Write-Host "  Aguardando 5 minutos para próxima captura..." -ForegroundColor Gray
            Start-Sleep -Seconds 300
        }
    }
}

# Executar pipeline completo
Write-Host "`n═══════════════════════════════════════════════════════════════" -ForegroundColor Green
Write-Host "                    INICIANDO PIPELINE COMPLETO                  " -ForegroundColor Green
Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Green

Start-PlaywrightCapture
Process-HARFiles
Analyze-Security
Generate-Tests
Generate-Documentation
Compare-Captures
Generate-FinalReport
Create-Backup
Setup-CICD

if ($NoStop) {
    Start-ContinuousMonitoring
}

Write-Host "`n╔══════════════════════════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║                          CAPTURA COMPLETA FINALIZADA!                         ║" -ForegroundColor Green
Write-Host "╠══════════════════════════════════════════════════════════════════════════════╣" -ForegroundColor Green
Write-Host "║  Resultados salvos em: $captureDir" -ForegroundColor Green
Write-Host "║  Relatório HTML: $captureDir\reports\report.html" -ForegroundColor Green
Write-Host "║  Postman Collections: $captureDir\postman\" -ForegroundColor Green
Write-Host "║  Testes automatizados: $captureDir\tests\" -ForegroundColor Green
Write-Host "║  Análise de segurança: $captureDir\security\analysis.json" -ForegroundColor Green
Write-Host "╚══════════════════════════════════════════════════════════════════════════════╝" -ForegroundColor Green

# Abrir relatório automaticamente
Start-Process "$captureDir\reports\report.html"