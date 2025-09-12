@echo off
echo ================================================================================
echo                        MEEP TOTAL CAPTURE - BATCH VERSION
echo ================================================================================
echo.

set TIMESTAMP=%date:~-4%%date:~3,2%%date:~0,2%_%time:~0,2%%time:~3,2%%time:~6,2%
set TIMESTAMP=%TIMESTAMP: =0%
set OUTPUT_DIR=meep-capture-%TIMESTAMP%

echo [+] Criando estrutura de diretorios...
mkdir %OUTPUT_DIR%\screenshots 2>nul
mkdir %OUTPUT_DIR%\har 2>nul
mkdir %OUTPUT_DIR%\postman 2>nul
mkdir %OUTPUT_DIR%\curl 2>nul
mkdir %OUTPUT_DIR%\reports 2>nul

echo [+] Executando captura com Playwright...

echo const { chromium } = require('playwright'); > %OUTPUT_DIR%\capture.js
echo. >> %OUTPUT_DIR%\capture.js
echo (async () =^> { >> %OUTPUT_DIR%\capture.js
echo     console.log('Iniciando captura MEEP...'); >> %OUTPUT_DIR%\capture.js
echo     const browser = await chromium.launch({ headless: false }); >> %OUTPUT_DIR%\capture.js
echo     const context = await browser.newContext({ >> %OUTPUT_DIR%\capture.js
echo         recordHar: { path: 'har/capture.har', mode: 'full' }, >> %OUTPUT_DIR%\capture.js
echo         recordVideo: { dir: 'videos/' } >> %OUTPUT_DIR%\capture.js
echo     }); >> %OUTPUT_DIR%\capture.js
echo     const page = await context.newPage(); >> %OUTPUT_DIR%\capture.js
echo. >> %OUTPUT_DIR%\capture.js
echo     // Capturar requisicoes >> %OUTPUT_DIR%\capture.js
echo     const requests = []; >> %OUTPUT_DIR%\capture.js
echo     page.on('request', request =^> { >> %OUTPUT_DIR%\capture.js
echo         requests.push({ >> %OUTPUT_DIR%\capture.js
echo             url: request.url(), >> %OUTPUT_DIR%\capture.js
echo             method: request.method(), >> %OUTPUT_DIR%\capture.js
echo             headers: request.headers() >> %OUTPUT_DIR%\capture.js
echo         }); >> %OUTPUT_DIR%\capture.js
echo     }); >> %OUTPUT_DIR%\capture.js
echo. >> %OUTPUT_DIR%\capture.js
echo     // Navegar para MEEP >> %OUTPUT_DIR%\capture.js
echo     await page.goto('https://beta.portal.meep.com.br'); >> %OUTPUT_DIR%\capture.js
echo     await page.screenshot({ path: 'screenshots/1-home.png' }); >> %OUTPUT_DIR%\capture.js
echo. >> %OUTPUT_DIR%\capture.js
echo     // Tentar login >> %OUTPUT_DIR%\capture.js
echo     try { >> %OUTPUT_DIR%\capture.js
echo         await page.fill('input[type="email"]', 'toretomal@icloud.com'); >> %OUTPUT_DIR%\capture.js
echo         await page.fill('input[type="password"]', '10041210Cl@'); >> %OUTPUT_DIR%\capture.js
echo         await page.screenshot({ path: 'screenshots/2-filled.png' }); >> %OUTPUT_DIR%\capture.js
echo         await page.click('button[type="submit"]'); >> %OUTPUT_DIR%\capture.js
echo         await page.waitForTimeout(5000); >> %OUTPUT_DIR%\capture.js
echo         await page.screenshot({ path: 'screenshots/3-after.png' }); >> %OUTPUT_DIR%\capture.js
echo     } catch (e) { >> %OUTPUT_DIR%\capture.js
echo         console.log('Erro no login:', e.message); >> %OUTPUT_DIR%\capture.js
echo     } >> %OUTPUT_DIR%\capture.js
echo. >> %OUTPUT_DIR%\capture.js
echo     // Salvar dados >> %OUTPUT_DIR%\capture.js
echo     const fs = require('fs'); >> %OUTPUT_DIR%\capture.js
echo     fs.writeFileSync('reports/requests.json', JSON.stringify(requests, null, 2)); >> %OUTPUT_DIR%\capture.js
echo. >> %OUTPUT_DIR%\capture.js
echo     // Gerar comandos cURL >> %OUTPUT_DIR%\capture.js
echo     const curls = requests.map(req =^> { >> %OUTPUT_DIR%\capture.js
echo         let curl = `curl -X ${req.method} "${req.url}"`; >> %OUTPUT_DIR%\capture.js
echo         for (const [key, value] of Object.entries(req.headers)) { >> %OUTPUT_DIR%\capture.js
echo             curl += ` -H "${key}: ${value}"`; >> %OUTPUT_DIR%\capture.js
echo         } >> %OUTPUT_DIR%\capture.js
echo         return curl; >> %OUTPUT_DIR%\capture.js
echo     }); >> %OUTPUT_DIR%\capture.js
echo     fs.writeFileSync('curl/commands.sh', curls.join('\n\n')); >> %OUTPUT_DIR%\capture.js
echo. >> %OUTPUT_DIR%\capture.js
echo     console.log(`Capturadas ${requests.length} requisicoes`); >> %OUTPUT_DIR%\capture.js
echo     console.log('Screenshots salvos em screenshots/'); >> %OUTPUT_DIR%\capture.js
echo     console.log('Comandos cURL salvos em curl/commands.sh'); >> %OUTPUT_DIR%\capture.js
echo. >> %OUTPUT_DIR%\capture.js
echo     await context.close(); >> %OUTPUT_DIR%\capture.js
echo     await browser.close(); >> %OUTPUT_DIR%\capture.js
echo })(); >> %OUTPUT_DIR%\capture.js

cd %OUTPUT_DIR%
echo [+] Instalando dependencias...
call npm init -y >nul 2>&1
call npm install playwright >nul 2>&1
echo [+] Instalando browsers...
call npx playwright install chromium >nul 2>&1

echo [+] Executando captura...
node capture.js

echo.
echo ================================================================================
echo                            CAPTURA COMPLETA!
echo ================================================================================
echo.
echo Resultados salvos em: %OUTPUT_DIR%
echo   - Screenshots: %OUTPUT_DIR%\screenshots\
echo   - HAR: %OUTPUT_DIR%\har\capture.har
echo   - cURL: %OUTPUT_DIR%\curl\commands.sh
echo   - Relatorio: %OUTPUT_DIR%\reports\requests.json
echo.

pause