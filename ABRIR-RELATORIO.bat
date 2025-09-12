@echo off
REM =====================================================
REM  ABRIR-RELATORIO.bat
REM  Duplo-clique para abrir o relatório mais recente
REM  Sistema MEEP - Painel Universal
REM =====================================================

echo.
echo ========================================
echo    BUSCADOR DE RELATORIOS MEEP
echo ========================================
echo.

REM Executa o PowerShell script
powershell -ExecutionPolicy Bypass -File ".\scripts\FIND-REPORT.ps1"

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERRO] Nenhum relatorio encontrado!
    echo.
    echo Gerando novo relatorio agora...
    echo.
    
    REM Tenta gerar um novo relatório
    python SISTEMA_COMPLETO_MEEP.py
    
    REM Tenta abrir novamente
    powershell -ExecutionPolicy Bypass -File ".\scripts\FIND-REPORT.ps1"
)

echo.
pause