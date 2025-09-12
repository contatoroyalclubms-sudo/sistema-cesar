@echo off
color 0A
echo.
echo ============================================================
echo         INICIANDO SISTEMA PAINEL UNIVERSAL V6
echo ============================================================
echo.

REM Mata processos existentes
echo [1/5] Limpando processos anteriores...
taskkill /F /IM python.exe 2>nul
taskkill /F /IM node.exe 2>nul
timeout /t 2 /nobreak >nul

REM Inicia o backend principal
echo [2/5] Iniciando Backend Principal (porta 8003)...
cd /d "C:\Users\User\OneDrive\Desktop\sistema-v6-novo\paineluniversal\paineluniversal\backend"
start "Backend Auth Server - Porta 8003" cmd /k "color 0E && echo BACKEND PRINCIPAL - PORTA 8003 && echo ============================== && python auth_server.py"
timeout /t 3 /nobreak >nul

REM Opcional: Inicia o backend mock (comentado por padrao)
REM echo [3/5] Iniciando Backend Mock (porta 8000)...
REM start "Backend Mock - Porta 8000" cmd /k "color 0D && echo BACKEND MOCK - PORTA 8000 && echo ========================= && python local_auth_server.py"
REM timeout /t 3 /nobreak >nul

REM Inicia o frontend
echo [3/5] Iniciando Frontend (porta 5175)...
cd /d "C:\Users\User\OneDrive\Desktop\sistema-v6-novo\paineluniversal\paineluniversal\frontend"
start "Frontend Vite - Porta 5175" cmd /k "color 0B && echo FRONTEND VITE - PORTA 5175 && echo ========================== && npm run dev -- --port 5175"
timeout /t 5 /nobreak >nul

REM Verifica se o backend esta respondendo
echo [4/5] Verificando servicos...
curl -s http://localhost:8003/api/health >nul 2>&1
if %errorlevel% == 0 (
    echo   [OK] Backend respondendo na porta 8003
) else (
    echo   [AVISO] Backend ainda iniciando...
)

REM Abre o navegador
echo [5/5] Abrindo navegador...
timeout /t 2 /nobreak >nul
start http://localhost:5175

echo.
echo ============================================================
echo              SISTEMA INICIADO COM SUCESSO!
echo ============================================================
echo.
echo SERVICOS RODANDO:
echo   - Backend Principal: http://localhost:8003
echo   - Frontend:         http://localhost:5175
echo   - API Docs:         http://localhost:8003/docs
echo.
echo CREDENCIAIS DE LOGIN:
echo   - CPF:   00000000000
echo   - Senha: 0000
echo.
echo IMPORTANTE:
echo   - SEM Google Login (somente CPF + senha)
echo   - Frontend apontando para backend 8003
echo   - CORS configurado para todas as portas locais
echo.
echo ============================================================
echo.
echo Pressione qualquer tecla para fechar esta janela...
echo (Os servicos continuarao rodando em segundo plano)
echo.
pause >nul