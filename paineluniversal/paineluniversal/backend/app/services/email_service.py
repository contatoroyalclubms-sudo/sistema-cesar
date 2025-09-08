import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from jinja2 import Template
from typing import Optional
import os

logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self):
        # Configurações de email usando variáveis de ambiente diretamente
        self.smtp_server = os.getenv("EMAIL_HOST", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("EMAIL_PORT", "587"))
        self.username = os.getenv("EMAIL_USER", "")
        self.password = os.getenv("EMAIL_PASSWORD", "")
        self.from_email = os.getenv("EMAIL_FROM", "") or self.username
        self.from_name = os.getenv("EMAIL_FROM_NAME", "Sistema Universal")
        self.use_tls = os.getenv("EMAIL_USE_TLS", "true").lower() == "true"
        
        # MODO TESTE ATIVADO - Email real desativado para testes
        self.test_mode = True

    async def send_verification_code(self, to_email: str, to_name: str, verification_code: str) -> bool:
        """Enviar código de verificação por email - MODO TESTE"""
        
        # MODO TESTE: Sempre mostra no console ao invés de enviar email real
        if self.test_mode or not self.username or not self.password:
            logger.info("📧 MODO TESTE - Email desativado")
            print(f"\n{'='*60}")
            print(f"📧 CÓDIGO DE VERIFICAÇÃO - MODO TESTE")
            print(f"{'='*60}")
            print(f"👤 Para: {to_name}")
            print(f"📩 Email: {to_email}")
            print(f"🔐 Código: {verification_code}")
            print(f"⏱️  Válido por: 10 minutos")
            print(f"{'='*60}\n")
            return True
        try:
            # CÓDIGO DE ENVIO REAL COMENTADO PARA TESTE
            # Descomente as linhas abaixo quando quiser ativar email real
            
            """
            # Template HTML para o email
            html_template = '''
            <!DOCTYPE html>
            <html lang="pt-BR">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Código de Verificação</title>
                <style>
                    body { font-family: Arial, sans-serif; background-color: #f4f4f4; margin: 0; padding: 20px; }
                    .container { max-width: 600px; margin: 0 auto; background-color: #ffffff; padding: 30px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); }
                    .header { text-align: center; margin-bottom: 30px; }
                    .logo { color: #2563eb; font-size: 24px; font-weight: bold; }
                    .content { text-align: center; }
                    .code-box { background-color: #f8f9fa; border: 2px dashed #2563eb; padding: 20px; margin: 20px 0; border-radius: 8px; }
                    .code { font-size: 32px; font-weight: bold; color: #2563eb; letter-spacing: 4px; }
                    .instructions { color: #6b7280; margin: 20px 0; line-height: 1.6; }
                    .footer { margin-top: 30px; padding-top: 20px; border-top: 1px solid #e5e7eb; text-align: center; color: #9ca3af; font-size: 14px; }
                    @media (max-width: 600px) { .container { padding: 20px; } .code { font-size: 28px; } }
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <div class="logo">🎉 Sistema Universal</div>
                        <h1 style="color: #1f2937; margin: 10px 0;">Código de Verificação</h1>
                    </div>
                    
                    <div class="content">
                        <p style="color: #374151; font-size: 16px;">Olá, <strong>{{ name }}</strong>!</p>
                        <p style="color: #6b7280;">Use o código abaixo para completar seu login:</p>
                        
                        <div class="code-box">
                            <div class="code">{{ code }}</div>
                        </div>
                        
                        <div class="instructions">
                            <p><strong>Instruções:</strong></p>
                            <p>• Digite este código na tela de login</p>
                            <p>• O código é válido por 10 minutos</p>
                            <p>• Por segurança, não compartilhe este código</p>
                        </div>
                        
                        <p style="color: #9ca3af; font-size: 14px;">
                            Se você não solicitou este código, ignore este email.
                        </p>
                    </div>
                    
                    <div class="footer">
                        <p>Este é um email automático, não responda.</p>
                        <p>© 2025 Sistema Universal - Gestão de Eventos</p>
                    </div>
                </div>
            </body>
            </html>
            '''
            
            # Renderizar template
            template = Template(html_template)
            html_content = template.render(name=to_name, code=verification_code)
            
            # Criar mensagem
            message = MIMEMultipart("alternative")
            message["Subject"] = f"Código de Verificação: {verification_code}"
            message["From"] = f"{self.from_name} <{self.from_email}>"
            message["To"] = to_email
            
            # Versão texto simples
            text_content = f'''
            Olá, {to_name}!
            
            Seu código de verificação é: {verification_code}
            
            Digite este código na tela de login para completar seu acesso.
            
            Este código é válido por 10 minutos.
            
            Se você não solicitou este código, ignore este email.
            
            ---
            Sistema Universal - Gestão de Eventos
            '''
            
            # Adicionar ambas as versões
            text_part = MIMEText(text_content, "plain")
            html_part = MIMEText(html_content, "html")
            
            message.attach(text_part)
            message.attach(html_part)
            
            # Enviar email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                if self.use_tls:
                    server.starttls()
                server.login(self.username, self.password)
                server.send_message(message)
            
            logger.info(f"Código de verificação enviado para {to_email}")
            """
            
            # RETORNA SEMPRE SUCESSO EM MODO TESTE
            return True
            
        except Exception as e:
            logger.error(f"Erro ao enviar email: {str(e)}")
            # Fallback: mostrar no console
            print(f"\n{'='*50}")
            print(f"⚠️  ERRO NO ENVIO - CÓDIGO PARA {to_name}")
            print(f"Email: {to_email}")
            print(f"Código: {verification_code}")
            print(f"Erro: {str(e)}")
            print(f"{'='*50}\n")
            return False

    async def send_welcome_email(self, to_email: str, to_name: str) -> bool:
        """Enviar email de boas-vindas para novos usuários - MODO TESTE"""
        
        # MODO TESTE: Apenas log no console
        if self.test_mode or not self.username or not self.password:
            logger.info("🎉 MODO TESTE - Email de boas-vindas desativado")
            print(f"\n{'='*50}")
            print(f"🎉 EMAIL DE BOAS-VINDAS - MODO TESTE")
            print(f"{'='*50}")
            print(f"👤 Para: {to_name}")
            print(f"📩 Email: {to_email}")
            print(f"📝 Mensagem: Conta criada com sucesso!")
            print(f"{'='*50}\n")
            return True
        
        # CÓDIGO DE ENVIO REAL COMENTADO
        """
        try:
            html_template = '''
            <!DOCTYPE html>
            <html lang="pt-BR">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Bem-vindo ao Sistema Universal</title>
                <style>
                    body { font-family: Arial, sans-serif; background-color: #f4f4f4; margin: 0; padding: 20px; }
                    .container { max-width: 600px; margin: 0 auto; background-color: #ffffff; padding: 30px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); }
                    .header { text-align: center; margin-bottom: 30px; }
                    .logo { color: #2563eb; font-size: 24px; font-weight: bold; }
                    .content { color: #374151; line-height: 1.6; }
                    .welcome-box { background: linear-gradient(135deg, #2563eb, #3b82f6); color: white; padding: 25px; border-radius: 8px; text-align: center; margin: 20px 0; }
                    .features { background-color: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0; }
                    .feature-item { margin: 10px 0; padding-left: 20px; position: relative; }
                    .feature-item:before { content: "✓"; position: absolute; left: 0; color: #10b981; font-weight: bold; }
                    .footer { margin-top: 30px; padding-top: 20px; border-top: 1px solid #e5e7eb; text-align: center; color: #9ca3af; font-size: 14px; }
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <div class="logo">🎉 Sistema Universal</div>
                    </div>
                    
                    <div class="welcome-box">
                        <h1 style="margin: 0 0 10px 0;">Bem-vindo, {{ name }}!</h1>
                        <p style="margin: 0; opacity: 0.9;">Sua conta foi criada com sucesso</p>
                    </div>
                    
                    <div class="content">
                        <p>Olá <strong>{{ name }}</strong>,</p>
                        <p>É um prazer tê-lo(a) conosco! Sua conta no Sistema Universal foi criada com sucesso e você já pode começar a aproveitar todos os recursos disponíveis.</p>
                        
                        <div class="features">
                            <h3 style="color: #1f2937; margin-top: 0;">O que você pode fazer agora:</h3>
                            <div class="feature-item">Gerenciar eventos e listas de convidados</div>
                            <div class="feature-item">Acompanhar vendas e check-ins em tempo real</div>
                            <div class="feature-item">Visualizar relatórios detalhados</div>
                            <div class="feature-item">Usar o sistema PDV integrado</div>
                            <div class="feature-item">Gerenciar promoters e comissões</div>
                        </div>
                        
                        <p>Se precisar de ajuda ou tiver alguma dúvida, nossa equipe de suporte está sempre disponível.</p>
                        <p>Desejamos muito sucesso em seus eventos!</p>
                    </div>
                    
                    <div class="footer">
                        <p>Este é um email automático, não responda.</p>
                        <p>© 2025 Sistema Universal - Gestão de Eventos</p>
                    </div>
                </div>
            </body>
            </html>
            '''
            
            template = Template(html_template)
            html_content = template.render(name=to_name)
            
            message = MIMEMultipart("alternative")
            message["Subject"] = "Bem-vindo ao Sistema Universal! 🎉"
            message["From"] = f"{self.from_name} <{self.from_email}>"
            message["To"] = to_email
            
            text_content = f'''
            Bem-vindo ao Sistema Universal, {to_name}!
            
            Sua conta foi criada com sucesso e você já pode começar a usar todos os recursos:
            
            • Gerenciar eventos e listas de convidados
            • Acompanhar vendas e check-ins em tempo real
            • Visualizar relatórios detalhados
            • Usar o sistema PDV integrado
            • Gerenciar promoters e comissões
            
            Se precisar de ajuda, nossa equipe está sempre disponível.
            
            Desejamos muito sucesso em seus eventos!
            
            ---
            Sistema Universal - Gestão de Eventos
            '''
            
            text_part = MIMEText(text_content, "plain")
            html_part = MIMEText(html_content, "html")
            
            message.attach(text_part)
            message.attach(html_part)
            
            if not self.username or not self.password:
                logger.info(f"Email de boas-vindas seria enviado para {to_email}")
                return True
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                if self.use_tls:
                    server.starttls()
                server.login(self.username, self.password)
                server.send_message(message)
            
            logger.info(f"Email de boas-vindas enviado para {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao enviar email de boas-vindas: {str(e)}")
            return False
        """
        
        # RETORNA SEMPRE SUCESSO EM MODO TESTE
        return True

# Instância global do serviço de email
email_service = EmailService()
