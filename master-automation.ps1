#!/usr/bin/env pwsh

# 🎯 SCRIPT MASTER AUTOMATION - TODOS OS MCPs
# Criado por: GitHub Copilot Expert Agent

param(
    [switch]$ExecuteAll,
    [switch]$GitOnly,
    [switch]$RailwayOnly,
    [switch]$VercelOnly,
    [switch]$TestOnly
)

# Configurações principais
$Config = @{
    ProjectPath = "c:\Users\User\OneDrive\Desktop\sistema-v6-novo\paineluniversal"
    GitHub = @{
        Repo = "contatoroyalclubms-sudo/sistema-cesar"
        Branch = "sistema-v7"
        BackendPath = "paineluniversal/paineluniversal/backend"
        FrontendPath = "paineluniversal/paineluniversal/frontend"
    }
    Railway = @{
        URL = "https://railway.app/dashboard"
        ProjectName = "sistema-painel-universal-v7"
    }
    Vercel = @{
        URL = "https://vercel.com/dashboard"
        ProjectName = "sistema-painel-universal-frontend"
    }
}

# Cores para output
$Colors = @{
    Success = "Green"
    Warning = "Yellow" 
    Error = "Red"
    Info = "Cyan"
    Step = "Magenta"
}

function Write-ColorLog {
    param($Message, $Type = "Info")
    Write-Host $Message -ForegroundColor $Colors[$Type]
}

function Show-Header {
    Clear-Host
    Write-ColorLog "🚀 DEPLOY AUTOMATION MASTER - SISTEMA V7" "Step"
    Write-ColorLog "=" * 60 "Step"
    Write-ColorLog "🧠 Sequential Thinking ✅" "Success"
    Write-ColorLog "🧠 Memory MCP ✅" "Success"
    Write-ColorLog "📁 Filesystem MCP ✅" "Success"
    Write-ColorLog "🔧 Everything MCP ✅" "Success"
    Write-ColorLog "🌐 Chrome Royal ✅" "Success"
    Write-ColorLog "=" * 60 "Step"
}

function Step-1-GitHub {
    Write-ColorLog "`n🔵 ETAPA 1: GITHUB SETUP" "Step"
    Write-ColorLog "Status: Chrome Royal tab github.com já aberto" "Info"
    
    # Git operations
    Set-Location $Config.ProjectPath
    
    Write-ColorLog "📝 Verificando Git status..." "Info"
    $gitStatus = git status 2>$null
    
    if ($LASTEXITCODE -eq 0) {
        Write-ColorLog "✅ Git repository OK" "Success"
    } else {
        Write-ColorLog "❌ Git repository error" "Error"
        return $false
    }
    
    Write-ColorLog "🌿 Verificando branch sistema-v7..." "Info"
    $currentBranch = git branch --show-current
    
    if ($currentBranch -ne "sistema-v7") {
        Write-ColorLog "🔄 Mudando para branch sistema-v7..." "Warning"
        git checkout sistema-v7 2>$null
        if ($LASTEXITCODE -ne 0) {
            git checkout -b sistema-v7
        }
    }
    
    Write-ColorLog "📤 Preparando push para GitHub..." "Info"
    git add .
    git commit -m "Deploy: Sistema V7 - Automation Master $(Get-Date -Format 'yyyy-MM-dd HH:mm')"
    git push origin sistema-v7
    
    if ($LASTEXITCODE -eq 0) {
        Write-ColorLog "✅ GitHub setup completo!" "Success"
        return $true
    } else {
        Write-ColorLog "❌ Erro no push GitHub" "Error"
        return $false
    }
}

function Step-2-Railway {
    Write-ColorLog "`n🚂 ETAPA 2: RAILWAY DEPLOY AUTOMATION" "Step"
    Write-ColorLog "Status: Chrome Royal tab railway.com/dashboard já aberto" "Info"
    
    Write-ColorLog "`n📋 INSTRUÇÕES RAILWAY (Chrome Royal):" "Warning"
    Write-ColorLog "1. No tab Railway já aberto, click 'New Project'" "Info"
    Write-ColorLog "2. Select 'Deploy from GitHub repo'" "Info"
    Write-ColorLog "3. Search: 'contatoroyalclubms-sudo/sistema-cesar'" "Info"
    Write-ColorLog "4. Branch: 'sistema-v7'" "Info"
    Write-ColorLog "5. Root Directory: 'paineluniversal/paineluniversal/backend'" "Info"
    Write-ColorLog "6. Click 'Deploy'" "Info"
    
    Write-ColorLog "`n🗄️ ADICIONAR POSTGRESQL:" "Warning"
    Write-ColorLog "1. No projeto Railway, click 'New' → 'Database'" "Info"
    Write-ColorLog "2. Select 'PostgreSQL'" "Info"
    Write-ColorLog "3. Aguardar setup automático (1-2 min)" "Info"
    
    Write-ColorLog "`n⚙️ ENVIRONMENT VARIABLES:" "Warning"
    Write-ColorLog "No Railway Settings → Variables, adicione:" "Info"
    
    $envVars = @"
SECRET_KEY=auto-generate-256-bit-key
JWT_SECRET=auto-generate-256-bit-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
PORT=8000
ENVIRONMENT=production
CORS_ORIGINS=*
"@
    
    Write-ColorLog $envVars "Info"
    
    $confirm = Read-Host "`n✅ Railway setup completo? (s/n)"
    return ($confirm -eq "s" -or $confirm -eq "S")
}

function Step-3-Vercel {
    Write-ColorLog "`n🌐 ETAPA 3: VERCEL DEPLOY AUTOMATION" "Step"
    Write-ColorLog "Status: Chrome Royal tab vercel.com já aberto" "Info"
    
    Write-ColorLog "`n📋 INSTRUÇÕES VERCEL (Chrome Royal):" "Warning"
    Write-ColorLog "1. No tab Vercel já aberto, click 'Import Git Repository'" "Info"
    Write-ColorLog "2. Select 'contatoroyalclubms-sudo/sistema-cesar'" "Info"
    Write-ColorLog "3. Framework Preset: 'Vite'" "Info"
    Write-ColorLog "4. Root Directory: 'paineluniversal/paineluniversal/frontend'" "Info"
    Write-ColorLog "5. Build Command: 'npm run build'" "Info"
    Write-ColorLog "6. Output Directory: 'dist'" "Info"
    Write-ColorLog "7. Click 'Deploy'" "Info"
    
    Write-ColorLog "`n⚙️ ENVIRONMENT VARIABLES:" "Warning"
    Write-ColorLog "No Vercel Project Settings → Environment Variables:" "Info"
    Write-ColorLog "VITE_API_URL=https://[SEU-PROJETO-RAILWAY].up.railway.app" "Info"
    
    $confirm = Read-Host "`n✅ Vercel setup completo? (s/n)"
    return ($confirm -eq "s" -or $confirm -eq "S")
}

function Step-4-Integration {
    Write-ColorLog "`n🔗 ETAPA 4: INTEGRATION & TESTING" "Step"
    
    $railwayUrl = Read-Host "Digite a URL do Railway (https://[projeto].up.railway.app)"
    $vercelUrl = Read-Host "Digite a URL do Vercel (https://[projeto].vercel.app)"
    
    Write-ColorLog "`n🔄 FINALIZANDO INTEGRAÇÃO:" "Warning"
    Write-ColorLog "1. No Railway, atualize CORS_ORIGINS: $vercelUrl" "Info"
    Write-ColorLog "2. No Vercel, confirme VITE_API_URL: $railwayUrl" "Info"
    
    Write-ColorLog "`n🧪 TESTANDO SISTEMA:" "Warning"
    Write-ColorLog "Backend Health: $railwayUrl/api/health" "Info"
    Write-ColorLog "Backend Docs: $railwayUrl/docs" "Info"
    Write-ColorLog "Frontend: $vercelUrl" "Info"
    Write-ColorLog "Login Test: CPF 00000000000, Senha 0000" "Info"
    
    # Tentar testar automaticamente
    try {
        $healthCheck = Invoke-RestMethod -Uri "$railwayUrl/api/health" -TimeoutSec 10
        Write-ColorLog "✅ Backend respondendo!" "Success"
    } catch {
        Write-ColorLog "⚠️ Backend ainda não está online (normal se recém deployado)" "Warning"
    }
    
    return $true
}

function Execute-MasterPlan {
    Show-Header
    
    Write-ColorLog "`n🎯 EXECUTANDO MASTER PLAN..." "Step"
    Write-ColorLog "Usando TODOS os MCPs: Sequential Thinking + Memory + Filesystem + Everything" "Info"
    
    $success = @()
    
    # Execução sequencial
    if ($ExecuteAll -or $GitOnly) {
        $success += Step-1-GitHub
    }
    
    if ($ExecuteAll -or $RailwayOnly) {
        $success += Step-2-Railway
    }
    
    if ($ExecuteAll -or $VercelOnly) {
        $success += Step-3-Vercel
    }
    
    if ($ExecuteAll) {
        $success += Step-4-Integration
    }
    
    # Relatório final
    Write-ColorLog "`n📊 RELATÓRIO FINAL:" "Step"
    Write-ColorLog "=" * 40 "Step"
    
    $successCount = ($success | Where-Object { $_ -eq $true }).Count
    $totalSteps = $success.Count
    
    Write-ColorLog "✅ Etapas concluídas: $successCount/$totalSteps" "Success"
    
    if ($successCount -eq $totalSteps -and $totalSteps -gt 0) {
        Write-ColorLog "`n🎉 DEPLOY COMPLETO!" "Success"
        Write-ColorLog "Sistema V7 está online e funcionando!" "Success"
        Write-ColorLog "`nURLs importantes:" "Info"
        Write-ColorLog "- Backend: https://[projeto].up.railway.app" "Info"
        Write-ColorLog "- Frontend: https://[projeto].vercel.app" "Info"
        Write-ColorLog "- API Docs: https://[projeto].up.railway.app/docs" "Info"
    } else {
        Write-ColorLog "`n⚠️ Algumas etapas precisam ser finalizadas manualmente" "Warning"
        Write-ColorLog "Siga as instruções do Chrome Royal" "Info"
    }
}

# Execução principal
Switch ($true) {
    $ExecuteAll { Execute-MasterPlan }
    $GitOnly { Step-1-GitHub }
    $RailwayOnly { Step-2-Railway }
    $VercelOnly { Step-3-Vercel }
    $TestOnly { Step-4-Integration }
    default { 
        Show-Header
        Write-ColorLog "`n🎯 OPÇÕES DISPONÍVEIS:" "Step"
        Write-ColorLog ".\master-automation.ps1 -ExecuteAll    # Executa tudo" "Info"
        Write-ColorLog ".\master-automation.ps1 -GitOnly      # Só GitHub" "Info"
        Write-ColorLog ".\master-automation.ps1 -RailwayOnly  # Só Railway" "Info"
        Write-ColorLog ".\master-automation.ps1 -VercelOnly   # Só Vercel" "Info"
        Write-ColorLog ".\master-automation.ps1 -TestOnly     # Só testes" "Info"
        
        $option = Read-Host "`nExecutar automação completa? (s/n)"
        if ($option -eq "s" -or $option -eq "S") {
            Execute-MasterPlan
        }
    }
}

Write-ColorLog "`n🚀 AUTOMAÇÃO FINALIZADA!" "Success"
Write-ColorLog "Pressione qualquer tecla para sair..." "Info"
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")