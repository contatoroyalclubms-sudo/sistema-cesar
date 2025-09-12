<#
  FIND-REPORT.ps1
  Varre o projeto e abre o relatório mais recente (HTML ou PDF).
  Sistema MEEP - Painel Universal
#>

param(
  # Raiz a partir da qual procurar (por padrão, pasta atual)
  [string]$Root = ".",
  # Extensões aceitas
  [string[]]$Ext = @("*.html","*.pdf"),
  # Subpastas principais onde normalmente salvamos
  [string[]]$Prefer = @("data","reports","meep-reports","meep-ultimate","captures","data\reports","data\screenshots")
)

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   BUSCADOR DE RELATÓRIOS MEEP" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

function Get-CandidateFiles {
  param([string]$base, [string[]]$patterns)
  $files = @()
  foreach ($p in $patterns) {
    $files += Get-ChildItem -Path $base -Recurse -Include $p -ErrorAction SilentlyContinue
  }
  return $files
}

# 1) Tenta nas pastas preferidas (mais rápido)
Write-Host "[1] Procurando nas pastas prioritárias..." -ForegroundColor Yellow
$candidates = @()
foreach ($sub in $Prefer) {
  $path = Join-Path $Root $sub
  if (Test-Path $path) {
    Write-Host "    Verificando: $path" -ForegroundColor Gray
    $candidates += Get-CandidateFiles -base $path -patterns $Ext
  }
}

# 2) Se não achou nada, varre tudo (fallback total)
if (-not $candidates -or $candidates.Count -eq 0) {
  Write-Host ""
  Write-Host "[2] Nenhum relatório nas pastas preferidas." -ForegroundColor Yellow
  Write-Host "    Iniciando varredura completa..." -ForegroundColor Yellow
  $candidates = Get-CandidateFiles -base $Root -patterns $Ext
}

if (-not $candidates -or $candidates.Count -eq 0) {
  Write-Host ""
  Write-Host "[ERRO] Nenhum relatorio HTML ou PDF encontrado!" -ForegroundColor Red
  Write-Host ""
  Write-Host "Dica: Execute primeiro o sistema MEEP para gerar relatórios:" -ForegroundColor Yellow
  Write-Host "  python SISTEMA_COMPLETO_MEEP.py" -ForegroundColor White
  Write-Host ""
  exit 1
}

# 3) Pega o mais recente por LastWriteTime
$latest = $candidates | Sort-Object LastWriteTime -Descending | Select-Object -First 1

Write-Host ""
Write-Host "[OK] RELATORIO ENCONTRADO!" -ForegroundColor Green
Write-Host ""
Write-Host "Arquivo: $($latest.Name)" -ForegroundColor White
Write-Host "Caminho: $($latest.DirectoryName)" -ForegroundColor Gray
Write-Host "Modificado: $($latest.LastWriteTime)" -ForegroundColor Gray
Write-Host "Tamanho: $([math]::Round($latest.Length/1KB, 2)) KB" -ForegroundColor Gray
Write-Host ""

# Lista outros relatórios encontrados
if ($candidates.Count -gt 1) {
  Write-Host "Outros relatórios disponíveis:" -ForegroundColor Cyan
  $others = $candidates | Sort-Object LastWriteTime -Descending | Select-Object -Skip 1 -First 5
  foreach ($file in $others) {
    Write-Host "  - $($file.Name) [$($file.LastWriteTime)]" -ForegroundColor Gray
  }
  Write-Host ""
}

Write-Host "Abrindo relatorio no navegador..." -ForegroundColor Green
Write-Host ""

# 4) Abre com app padrão do sistema
Start-Process $latest.FullName

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   RELATÓRIO ABERTO COM SUCESSO!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""