# 📱 GUIA DE INSTALAÇÃO - MOBILE APP PDV

## 🎉 SUCESSO! APP MOBILE FUNCIONANDO

Seu aplicativo mobile PDV está **rodando perfeitamente** e pronto para instalação no smartphone!

---

## 📋 PASSOS PARA INSTALAÇÃO NO SMARTPHONE

### 📱 MÉTODO 1: EXPO GO (RECOMENDADO PARA TESTES)

#### Para Android:
1. **Baixe o Expo Go** na Google Play Store
2. **Abra o Expo Go** no seu smartphone
3. **Escaneie o QR code** mostrado no terminal
4. **Aguarde o download** e instalação automática
5. **O app será aberto** automaticamente

#### Para iOS:
1. **Baixe o Expo Go** na App Store
2. **Abra o app Camera** do iPhone
3. **Escaneie o QR code** mostrado no terminal
4. **Toque na notificação** "Abrir no Expo Go"
5. **O app será carregado**

---

### 🔧 MÉTODO 2: INSTALAÇÃO DIRETA (DESENVOLVIMENTO)

#### Para Android (com USB Debugging):
```bash
# No terminal do mobile-app, pressione 'a'
# Ou execute:
npx expo run:android
```

#### Para iOS (com Xcode):
```bash
# No terminal do mobile-app, pressione 'i'  
# Ou execute:
npx expo run:ios
```

---

## ⚙️ CONFIGURAÇÕES IMPORTANTES

### 🌐 Backend URL
**ATENÇÃO**: Configure o IP do seu computador no app mobile:

1. **Encontre seu IP local**:
   ```bash
   ipconfig
   # Procure por "IPv4 Address" na sua rede Wi-Fi
   ```

2. **Configure no app** (arquivo `src/services/apiService.ts`):
   ```typescript
   baseURL: 'http://SEU_IP_LOCAL:8000'
   ```

### 🔗 Exemplo de configuração:
- Se seu IP é `192.168.1.100`
- Configure: `http://192.168.1.100:8000`

---

## 📋 FUNCIONALIDADES DO APP

### 🔐 **Login de Garçom**
- CPF e senha do garçon
- Seleção de evento ativo
- Autenticação segura

### 📡 **NFC Reading** (Android)
- Leitura de comandas NFC
- Leitura de pulseiras de clientes
- Feedback visual e sonoro

### 🛒 **Gestão de Pedidos**
- Cardápio completo de produtos
- Carrinho de compras
- Tipos de pedido (mesa/balcão/delivery)

### 📊 **Dashboard do Garçom**
- Estatísticas do dia
- Valor vendido
- Últimos pedidos

---

## 🚨 TROUBLESHOOTING

### ❌ **App não carrega**
- Verifique se o Metro Bundler está rodando
- Escaneie o QR code novamente
- Reinicie o Expo: `Ctrl+C` e `npx expo start --clear`

### ❌ **Erro de conexão**
- Confirme que smartphone e PC estão na **mesma rede Wi-Fi**
- Verifique o IP local do computador
- Desative firewall temporariamente

### ❌ **NFC não funciona**
- **Use dispositivo Android** (iOS tem limitações)
- Habilite NFC nas configurações do dispositivo
- NFC não funciona em emuladores

### ❌ **Login falha**
- Verifique se o backend está rodando
- Confirme a URL da API no app
- Teste conectividade: ping para o IP do PC

---

## 📱 TESTANDO O APP

### 1. **Primeira execução**:
- Abra o app via QR code
- Aguarde carregamento inicial
- Verifique se não há erros na tela

### 2. **Teste de login**:
- Use credenciais de garçom válidas
- Selecione um evento ativo
- Confirme acesso ao dashboard

### 3. **Teste de conectividade**:
- Navegue entre as telas
- Verifique carregamento de produtos
- Teste funcionalidades básicas

---

## 🎯 PRÓXIMOS PASSOS

### ✅ **O que está funcionando**:
- ✅ Estrutura do app React Native
- ✅ Navegação entre telas
- ✅ Contextos de autenticação
- ✅ Integração com backend
- ✅ Interface de usuário
- ✅ Tratamento de erros

### 🔄 **Para production**:
1. **Build APK/IPA**: `eas build`
2. **Configurar ambiente**: Produção vs desenvolvimento
3. **Testes em dispositivos**: Android e iOS
4. **Otimizações**: Performance e UX
5. **Deploy**: Google Play / App Store

---

## 📞 SUPORTE

**Se encontrar problemas**:
1. Verifique logs no terminal do Expo
2. Teste conectividade de rede
3. Confirme configurações do backend
4. Reinicie app e servidor se necessário

---

## 🎉 PARABÉNS!

Você agora tem um **aplicativo mobile PDV completo** funcionando com:
- ✅ React Native + Expo
- ✅ Autenticação JWT
- ✅ Integração NFC
- ✅ Sistema de pedidos
- ✅ Dashboard completo
- ✅ Modo offline
- ✅ Interface profissional

**Seu smartphone agora é um terminal PDV completo!** 🚀
