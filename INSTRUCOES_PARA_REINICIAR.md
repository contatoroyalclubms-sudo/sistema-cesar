# 🚀 INSTRUÇÕES PARA REINICIAR O SISTEMA

## ✅ SISTEMA FUNCIONANDO COM SUCESSO!

### 📁 CAMINHOS IMPORTANTES

**Backend:**
```
C:\Users\User\OneDrive\Desktop\sistema-v6-novo\paineluniversal\paineluniversal\backend
```

**Frontend:**
```
C:\Users\User\OneDrive\Desktop\sistema-v6-novo\paineluniversal\paineluniversal\frontend
```

---

## 🔧 COMANDOS PARA INICIAR

### 1️⃣ INICIAR O BACKEND (Terminal 1)

```bash
cd C:\Users\User\OneDrive\Desktop\sistema-v6-novo\paineluniversal\paineluniversal\backend
python auth_server.py
```

✅ **Backend rodando em:** http://localhost:8003

---

### 2️⃣ INICIAR O FRONTEND (Terminal 2)

```bash
cd C:\Users\User\OneDrive\Desktop\sistema-v6-novo\paineluniversal\paineluniversal\frontend
npm run dev
```

✅ **Frontend rodando em:** http://localhost:5174 (ou 5175 se 5174 estiver ocupada)

---

## 🔑 CREDENCIAIS DE LOGIN

| CPF | Senha | Tipo |
|-----|-------|------|
| **00000000000** | **0000** | Admin |

---

## 🌐 URLs PARA ACESSAR

- **Aplicação:** http://localhost:5174
- **Login direto:** http://localhost:5174/login
- **API Backend:** http://localhost:8003/api/health
- **Documentação API:** http://localhost:8003/docs

---

## 📝 PASSO A PASSO COMPLETO

1. **Abra 2 terminais** (CMD, PowerShell ou Terminal do VS Code)

2. **No primeiro terminal (Backend):**
   ```powershell
   cd C:\Users\User\OneDrive\Desktop\sistema-v6-novo\paineluniversal\paineluniversal\backend
   python auth_server.py
   ```
   
   Aguarde aparecer:
   ```
   INFO: Uvicorn running on http://0.0.0.0:8003
   ```

3. **No segundo terminal (Frontend):**
   ```powershell
   cd C:\Users\User\OneDrive\Desktop\sistema-v6-novo\paineluniversal\paineluniversal\frontend
   npm run dev
   ```
   
   Aguarde aparecer:
   ```
   VITE ready
   Local: http://localhost:5174/
   ```

4. **Abra o navegador e acesse:**
   ```
   http://localhost:5174
   ```

5. **Faça login com:**
   - CPF: `00000000000`
   - Senha: `0000`

---

## ⚠️ SOLUÇÃO DE PROBLEMAS

### Erro: "Porta já em uso"
- O sistema tentará automaticamente as portas 5174, 5175, 5176...
- Verifique no terminal qual porta foi usada

### Erro: "Cannot connect to backend"
- Certifique-se que o backend está rodando na porta 8003
- Verifique se apareceu a mensagem "Uvicorn running"

### Erro: "Invalid credentials"
- Use exatamente: CPF `00000000000` e senha `0000`
- Não adicione pontos ou traços no CPF

---

## 🎯 CONFIGURAÇÃO ATUAL

- **Backend:** Porta 8003 (auth_server.py)
- **Frontend:** Porta 5174 (Vite)
- **Proxy API:** Configurado no vite.config.ts
- **CORS:** Totalmente aberto para desenvolvimento
- **Autenticação:** JWT com CPF brasileiro

---

## 💡 DICAS

- Mantenha os dois terminais abertos enquanto usa o sistema
- Para parar: pressione `Ctrl+C` em cada terminal
- O sistema salva o token de login no localStorage do navegador
- Para fazer logout: clique no botão de logout ou limpe o localStorage

---

## ✨ PRONTO!

O sistema está configurado e funcionando corretamente.
Siga os passos acima sempre que precisar reiniciar.

**Última atualização:** 11/09/2025
**Status:** ✅ FUNCIONANDO