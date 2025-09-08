"""
Serviço de Impressão - Backend
Gerencia toda a lógica de impressão, comunicação com impressoras e processamento de jobs
"""

import asyncio
import socket
import time
from typing import Dict, Any, Optional, List
from datetime import datetime
import json
import logging
from enum import Enum

from ..models import Impressora, FilaImpressao, TemplateImpressao, ImpressoraInteligente
from ..schemas.impressoras import StatusImpressoraEnum, ModeloImpressoraEnum

logger = logging.getLogger(__name__)


class ComandosESCPOS:
    """Comandos ESC/POS para impressoras térmicas"""
    
    # Inicialização
    INIT = b'\x1B\x40'  # Inicializar impressora
    
    # Controle de linha
    LF = b'\x0A'  # Line feed
    CR = b'\x0D'  # Carriage return
    
    # Formatação de texto
    BOLD_ON = b'\x1B\x45\x01'  # Negrito ON
    BOLD_OFF = b'\x1B\x45\x00'  # Negrito OFF
    UNDERLINE_ON = b'\x1B\x2D\x01'  # Sublinhado ON
    UNDERLINE_OFF = b'\x1B\x2D\x00'  # Sublinhado OFF
    
    # Alinhamento
    ALIGN_LEFT = b'\x1B\x61\x00'
    ALIGN_CENTER = b'\x1B\x61\x01'
    ALIGN_RIGHT = b'\x1B\x61\x02'
    
    # Tamanho de fonte
    FONT_NORMAL = b'\x1D\x21\x00'
    FONT_DOUBLE_HEIGHT = b'\x1D\x21\x11'
    FONT_DOUBLE_WIDTH = b'\x1D\x21\x20'
    FONT_DOUBLE = b'\x1D\x21\x30'
    
    # Guilhotina
    CUT_FULL = b'\x1D\x56\x00'  # Corte total
    CUT_PARTIAL = b'\x1D\x56\x01'  # Corte parcial
    
    # QR Code (simplificado)
    QR_CODE_MODEL = b'\x1D\x28\x6B\x04\x00\x31\x41\x32\x00'  # Modelo 2
    QR_CODE_SIZE = b'\x1D\x28\x6B\x03\x00\x31\x43'  # + tamanho (1-16)
    
    # Código de barras
    BARCODE_HEIGHT = b'\x1D\x68'  # + altura (1-255)
    BARCODE_WIDTH = b'\x1D\x77'  # + largura (2-6)
    BARCODE_EAN13 = b'\x1D\x6B\x02'  # + 13 bytes
    BARCODE_CODE128 = b'\x1D\x6B\x49'  # + tamanho + dados
    
    # Gaveta de dinheiro
    CASH_DRAWER = b'\x1B\x70\x00\x19\xFA'


class ImpressaoService:
    """Serviço principal de impressão"""
    
    def __init__(self):
        self.comandos = ComandosESCPOS()
        self.timeout_conexao = 5  # segundos
        self.timeout_impressao = 30  # segundos
    
    async def verificar_conectividade(
        self, 
        ip: str, 
        porta: int, 
        timeout: Optional[int] = None
    ) -> bool:
        """Verificar se a impressora está acessível na rede"""
        timeout = timeout or self.timeout_conexao
        
        try:
            # Criar socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            
            # Tentar conectar
            resultado = sock.connect_ex((ip, porta))
            sock.close()
            
            return resultado == 0
            
        except Exception as e:
            logger.error(f"Erro ao verificar conectividade: {e}")
            return False
    
    async def enviar_comandos(
        self,
        ip: str,
        porta: int,
        comandos: bytes,
        timeout: Optional[int] = None
    ) -> Dict[str, Any]:
        """Enviar comandos para a impressora"""
        timeout = timeout or self.timeout_impressao
        
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            
            # Conectar
            sock.connect((ip, porta))
            
            # Enviar comandos
            sock.sendall(comandos)
            
            # Aguardar processamento
            await asyncio.sleep(0.5)
            
            sock.close()
            
            return {
                'sucesso': True,
                'mensagem': 'Comandos enviados com sucesso'
            }
            
        except socket.timeout:
            return {
                'sucesso': False,
                'erro': 'Timeout na comunicação com a impressora'
            }
        except ConnectionRefusedError:
            return {
                'sucesso': False,
                'erro': 'Conexão recusada pela impressora'
            }
        except Exception as e:
            return {
                'sucesso': False,
                'erro': f'Erro ao enviar comandos: {str(e)}'
            }
    
    async def enviar_teste_impressao(
        self,
        impressora: Impressora,
        tipo_teste: str = "completo",
        mensagem_customizada: Optional[str] = None
    ) -> Dict[str, Any]:
        """Enviar teste de impressão"""
        inicio = time.time()
        
        try:
            # Construir comandos do teste
            comandos = self.comandos.INIT
            
            if tipo_teste == "simples":
                comandos += self._criar_teste_simples(impressora, mensagem_customizada)
            elif tipo_teste == "completo":
                comandos += self._criar_teste_completo(impressora, mensagem_customizada)
            elif tipo_teste == "guilhotina":
                comandos += self._criar_teste_guilhotina(impressora)
            elif tipo_teste == "qrcode":
                comandos += self._criar_teste_qrcode(impressora)
            
            # Enviar para impressora
            resultado = await self.enviar_comandos(
                impressora.ip,
                impressora.porta,
                comandos
            )
            
            tempo_resposta = time.time() - inicio
            
            if resultado['sucesso']:
                return {
                    'sucesso': True,
                    'tempo_resposta': tempo_resposta,
                    'mensagem': f'Teste "{tipo_teste}" enviado com sucesso',
                    'detalhes': {
                        'tipo_teste': tipo_teste,
                        'impressora': impressora.nome,
                        'modelo': impressora.modelo.value if impressora.modelo else 'Genérica'
                    }
                }
            else:
                return {
                    'sucesso': False,
                    'tempo_resposta': tempo_resposta,
                    'mensagem': f'Falha no teste: {resultado["erro"]}',
                    'erro': resultado['erro']
                }
                
        except Exception as e:
            tempo_resposta = time.time() - inicio
            return {
                'sucesso': False,
                'tempo_resposta': tempo_resposta,
                'mensagem': f'Erro ao processar teste: {str(e)}',
                'erro': str(e)
            }
    
    def _criar_teste_simples(
        self, 
        impressora: Impressora, 
        mensagem: Optional[str] = None
    ) -> bytes:
        """Criar comandos para teste simples"""
        comandos = b''
        
        # Cabeçalho
        comandos += self.comandos.ALIGN_CENTER
        comandos += self.comandos.FONT_DOUBLE
        comandos += b'TESTE DE IMPRESSAO\n'
        comandos += self.comandos.FONT_NORMAL
        comandos += b'\n'
        
        # Informações da impressora
        comandos += self.comandos.ALIGN_LEFT
        comandos += f'Impressora: {impressora.nome}\n'.encode('utf-8')
        comandos += f'IP: {impressora.ip}:{impressora.porta}\n'.encode('utf-8')
        comandos += f'Modelo: {impressora.modelo.value if impressora.modelo else "Genérica"}\n'.encode('utf-8')
        comandos += b'\n'
        
        # Mensagem customizada
        if mensagem:
            comandos += self.comandos.ALIGN_CENTER
            comandos += b'-' * 32 + b'\n'
            comandos += mensagem.encode('utf-8') + b'\n'
            comandos += b'-' * 32 + b'\n'
            comandos += b'\n'
        
        # Data/hora
        comandos += self.comandos.ALIGN_CENTER
        comandos += datetime.now().strftime('%d/%m/%Y %H:%M:%S').encode('utf-8')
        comandos += b'\n' * 3
        
        # Corte
        if impressora.suporta_guilhotina:
            comandos += self.comandos.CUT_PARTIAL
        
        return comandos
    
    def _criar_teste_completo(
        self, 
        impressora: Impressora, 
        mensagem: Optional[str] = None
    ) -> bytes:
        """Criar comandos para teste completo"""
        comandos = b''
        
        # Cabeçalho grande
        comandos += self.comandos.ALIGN_CENTER
        comandos += self.comandos.FONT_DOUBLE
        comandos += self.comandos.BOLD_ON
        comandos += b'TESTE COMPLETO\n'
        comandos += self.comandos.BOLD_OFF
        comandos += self.comandos.FONT_NORMAL
        comandos += b'=' * 48 + b'\n\n'
        
        # Teste de formatações
        comandos += self.comandos.ALIGN_LEFT
        comandos += self.comandos.BOLD_ON
        comandos += b'TESTE DE FORMATACAO:\n'
        comandos += self.comandos.BOLD_OFF
        
        comandos += b'Texto normal\n'
        comandos += self.comandos.BOLD_ON
        comandos += b'Texto em NEGRITO\n'
        comandos += self.comandos.BOLD_OFF
        comandos += self.comandos.UNDERLINE_ON
        comandos += b'Texto sublinhado\n'
        comandos += self.comandos.UNDERLINE_OFF
        comandos += b'\n'
        
        # Teste de alinhamentos
        comandos += self.comandos.BOLD_ON
        comandos += b'TESTE DE ALINHAMENTO:\n'
        comandos += self.comandos.BOLD_OFF
        
        comandos += self.comandos.ALIGN_LEFT
        comandos += b'Alinhado a esquerda\n'
        comandos += self.comandos.ALIGN_CENTER
        comandos += b'Centralizado\n'
        comandos += self.comandos.ALIGN_RIGHT
        comandos += b'Alinhado a direita\n'
        comandos += self.comandos.ALIGN_LEFT
        comandos += b'\n'
        
        # Teste de tamanhos
        comandos += self.comandos.BOLD_ON
        comandos += b'TESTE DE TAMANHOS:\n'
        comandos += self.comandos.BOLD_OFF
        
        comandos += self.comandos.FONT_NORMAL
        comandos += b'Normal\n'
        comandos += self.comandos.FONT_DOUBLE_HEIGHT
        comandos += b'Altura dupla\n'
        comandos += self.comandos.FONT_DOUBLE_WIDTH
        comandos += b'Largura dupla\n'
        comandos += self.comandos.FONT_DOUBLE
        comandos += b'Duplo\n'
        comandos += self.comandos.FONT_NORMAL
        comandos += b'\n'
        
        # Teste de caracteres especiais
        comandos += self.comandos.BOLD_ON
        comandos += b'CARACTERES ESPECIAIS:\n'
        comandos += self.comandos.BOLD_OFF
        comandos += 'àáãâéêíóõôúç ÀÁÃÂÉÊÍÓÕÔÚÇ\n'.encode('utf-8')
        comandos += '!@#$%&*()[]{}+-*/=\n'.encode('utf-8')
        comandos += b'\n'
        
        # Informações da impressora
        comandos += self.comandos.ALIGN_CENTER
        comandos += b'-' * 48 + b'\n'
        comandos += self.comandos.ALIGN_LEFT
        comandos += self.comandos.BOLD_ON
        comandos += b'INFORMACOES DO DISPOSITIVO:\n'
        comandos += self.comandos.BOLD_OFF
        comandos += f'Nome: {impressora.nome}\n'.encode('utf-8')
        comandos += f'IP: {impressora.ip}:{impressora.porta}\n'.encode('utf-8')
        comandos += f'Modelo: {impressora.modelo.value if impressora.modelo else "Genérica"}\n'.encode('utf-8')
        comandos += f'Tipo: {impressora.tipo.value if impressora.tipo else "POS"}\n'.encode('utf-8')
        comandos += f'Largura papel: {impressora.largura_papel}mm\n'.encode('utf-8')
        comandos += f'Caracteres/linha: {impressora.caracteres_linha}\n'.encode('utf-8')
        comandos += b'\n'
        
        # Capacidades
        comandos += self.comandos.BOLD_ON
        comandos += b'CAPACIDADES:\n'
        comandos += self.comandos.BOLD_OFF
        comandos += f'Guilhotina: {"SIM" if impressora.suporta_guilhotina else "NAO"}\n'.encode('utf-8')
        comandos += f'QR Code: {"SIM" if impressora.suporta_qrcode else "NAO"}\n'.encode('utf-8')
        comandos += f'Código de Barras: {"SIM" if impressora.suporta_codigo_barras else "NAO"}\n'.encode('utf-8')
        comandos += b'\n'
        
        # Mensagem customizada
        if mensagem:
            comandos += self.comandos.ALIGN_CENTER
            comandos += b'=' * 48 + b'\n'
            comandos += self.comandos.FONT_DOUBLE_HEIGHT
            comandos += mensagem.encode('utf-8') + b'\n'
            comandos += self.comandos.FONT_NORMAL
            comandos += b'=' * 48 + b'\n'
            comandos += b'\n'
        
        # Rodapé
        comandos += self.comandos.ALIGN_CENTER
        comandos += b'-' * 48 + b'\n'
        comandos += b'Sistema de Gestao de Eventos\n'
        comandos += datetime.now().strftime('%d/%m/%Y %H:%M:%S').encode('utf-8')
        comandos += b'\n' * 4
        
        # Corte
        if impressora.suporta_guilhotina:
            comandos += self.comandos.CUT_PARTIAL
        
        return comandos
    
    def _criar_teste_guilhotina(self, impressora: Impressora) -> bytes:
        """Criar teste de guilhotina"""
        comandos = b''
        
        comandos += self.comandos.ALIGN_CENTER
        comandos += b'TESTE DE GUILHOTINA\n'
        comandos += b'\n'
        comandos += b'Este papel deve ser cortado\n'
        comandos += b'automaticamente apos a impressao\n'
        comandos += b'\n' * 3
        
        if impressora.suporta_guilhotina:
            comandos += self.comandos.CUT_FULL
        else:
            comandos += b'\n'
            comandos += b'GUILHOTINA NAO SUPORTADA\n'
            comandos += b'\n' * 3
        
        return comandos
    
    def _criar_teste_qrcode(self, impressora: Impressora) -> bytes:
        """Criar teste de QR Code"""
        comandos = b''
        
        comandos += self.comandos.ALIGN_CENTER
        comandos += b'TESTE DE QR CODE\n'
        comandos += b'\n'
        
        if impressora.suporta_qrcode:
            # QR Code simples com URL
            url = "https://sistema-eventos.com"
            comandos += self._gerar_qrcode(url)
            comandos += b'\n'
            comandos += b'Escaneie o QR Code acima\n'
            comandos += url.encode('utf-8') + b'\n'
        else:
            comandos += b'QR CODE NAO SUPORTADO\n'
        
        comandos += b'\n' * 3
        
        if impressora.suporta_guilhotina:
            comandos += self.comandos.CUT_PARTIAL
        
        return comandos
    
    def _gerar_qrcode(self, dados: str, tamanho: int = 6) -> bytes:
        """Gerar comandos para QR Code"""
        comandos = b''
        
        # Modelo
        comandos += self.comandos.QR_CODE_MODEL
        
        # Tamanho (1-16)
        comandos += self.comandos.QR_CODE_SIZE + bytes([tamanho])
        
        # Dados
        dados_bytes = dados.encode('utf-8')
        tamanho_dados = len(dados_bytes) + 3
        comandos += b'\x1D\x28\x6B'
        comandos += bytes([tamanho_dados % 256, tamanho_dados // 256])
        comandos += b'\x31\x50\x30'
        comandos += dados_bytes
        
        # Imprimir
        comandos += b'\x1D\x28\x6B\x03\x00\x31\x51\x30'
        
        return comandos
    
    def _gerar_codigo_barras(
        self, 
        dados: str, 
        tipo: str = "EAN13",
        altura: int = 50,
        largura: int = 2
    ) -> bytes:
        """Gerar comandos para código de barras"""
        comandos = b''
        
        # Configurar altura
        comandos += self.comandos.BARCODE_HEIGHT + bytes([altura])
        
        # Configurar largura
        comandos += self.comandos.BARCODE_WIDTH + bytes([largura])
        
        if tipo == "EAN13":
            # EAN-13 (13 dígitos)
            if len(dados) == 13 and dados.isdigit():
                comandos += self.comandos.BARCODE_EAN13
                comandos += dados.encode('ascii')
        elif tipo == "CODE128":
            # Code 128
            dados_bytes = dados.encode('ascii')
            comandos += self.comandos.BARCODE_CODE128
            comandos += bytes([len(dados_bytes)])
            comandos += dados_bytes
        
        return comandos
    
    async def processar_job(
        self, 
        impressora: Impressora, 
        job: FilaImpressao
    ) -> Dict[str, Any]:
        """Processar job de impressão da fila"""
        try:
            # Converter conteúdo do job em comandos
            comandos = self.comandos.INIT
            
            # Se for texto simples, apenas enviar
            if job.tipo_documento == "texto":
                comandos += job.conteudo.encode('utf-8')
                comandos += b'\n' * 3
                if impressora.suporta_guilhotina:
                    comandos += self.comandos.CUT_PARTIAL
            
            # Se for JSON com formatação
            elif job.tipo_documento in ["cupom", "pedido", "comanda"]:
                try:
                    dados = json.loads(job.conteudo)
                    comandos += self._processar_documento_estruturado(
                        impressora, 
                        job.tipo_documento, 
                        dados
                    )
                except json.JSONDecodeError:
                    # Se não for JSON válido, tratar como texto
                    comandos += job.conteudo.encode('utf-8')
                    comandos += b'\n' * 3
                    if impressora.suporta_guilhotina:
                        comandos += self.comandos.CUT_PARTIAL
            
            # Outros tipos
            else:
                comandos += job.conteudo.encode('utf-8')
                comandos += b'\n' * 3
                if impressora.suporta_guilhotina:
                    comandos += self.comandos.CUT_PARTIAL
            
            # Enviar para impressora
            resultado = await self.enviar_comandos(
                impressora.ip,
                impressora.porta,
                comandos
            )
            
            return resultado
            
        except Exception as e:
            logger.error(f"Erro ao processar job {job.id}: {e}")
            return {
                'sucesso': False,
                'erro': str(e)
            }
    
    def _processar_documento_estruturado(
        self, 
        impressora: Impressora,
        tipo: str,
        dados: Dict[str, Any]
    ) -> bytes:
        """Processar documento estruturado (cupom, pedido, etc)"""
        comandos = b''
        
        # Cabeçalho
        if 'cabecalho' in dados:
            comandos += self.comandos.ALIGN_CENTER
            comandos += self.comandos.FONT_DOUBLE
            comandos += dados['cabecalho'].encode('utf-8') + b'\n'
            comandos += self.comandos.FONT_NORMAL
            comandos += b'\n'
        
        # Informações do estabelecimento
        if 'estabelecimento' in dados:
            est = dados['estabelecimento']
            comandos += self.comandos.ALIGN_CENTER
            if 'nome' in est:
                comandos += self.comandos.BOLD_ON
                comandos += est['nome'].encode('utf-8') + b'\n'
                comandos += self.comandos.BOLD_OFF
            if 'cnpj' in est:
                comandos += f"CNPJ: {est['cnpj']}\n".encode('utf-8')
            if 'endereco' in est:
                comandos += est['endereco'].encode('utf-8') + b'\n'
            if 'telefone' in est:
                comandos += f"Tel: {est['telefone']}\n".encode('utf-8')
            comandos += b'\n'
        
        # Linha separadora
        comandos += self.comandos.ALIGN_LEFT
        comandos += b'-' * impressora.caracteres_linha + b'\n'
        
        # Dados do pedido/venda
        if 'numero' in dados:
            comandos += self.comandos.BOLD_ON
            comandos += f"Pedido: {dados['numero']}\n".encode('utf-8')
            comandos += self.comandos.BOLD_OFF
        
        if 'data' in dados:
            comandos += f"Data: {dados['data']}\n".encode('utf-8')
        
        if 'cliente' in dados:
            comandos += f"Cliente: {dados['cliente']}\n".encode('utf-8')
        
        if 'mesa' in dados:
            comandos += f"Mesa: {dados['mesa']}\n".encode('utf-8')
        
        if 'atendente' in dados:
            comandos += f"Atendente: {dados['atendente']}\n".encode('utf-8')
        
        comandos += b'-' * impressora.caracteres_linha + b'\n'
        
        # Itens
        if 'itens' in dados:
            comandos += self.comandos.BOLD_ON
            comandos += b'ITENS:\n'
            comandos += self.comandos.BOLD_OFF
            
            for item in dados['itens']:
                # Linha do item
                qtd = str(item.get('quantidade', 1))
                nome = item.get('nome', 'Item')
                valor_unit = item.get('valor_unitario', 0)
                valor_total = item.get('valor_total', valor_unit)
                
                # Formatar linha
                linha = f"{qtd:3} x {nome}"
                valor_str = f"R$ {valor_total:.2f}"
                espacos = impressora.caracteres_linha - len(linha) - len(valor_str)
                linha += ' ' * max(1, espacos) + valor_str
                
                comandos += linha.encode('utf-8') + b'\n'
                
                # Observações do item
                if 'observacoes' in item and item['observacoes']:
                    comandos += f"    Obs: {item['observacoes']}\n".encode('utf-8')
            
            comandos += b'-' * impressora.caracteres_linha + b'\n'
        
        # Totais
        if 'totais' in dados:
            totais = dados['totais']
            
            if 'subtotal' in totais:
                linha = "Subtotal:"
                valor = f"R$ {totais['subtotal']:.2f}"
                espacos = impressora.caracteres_linha - len(linha) - len(valor)
                comandos += (linha + ' ' * espacos + valor).encode('utf-8') + b'\n'
            
            if 'desconto' in totais and totais['desconto'] > 0:
                linha = "Desconto:"
                valor = f"R$ {totais['desconto']:.2f}"
                espacos = impressora.caracteres_linha - len(linha) - len(valor)
                comandos += (linha + ' ' * espacos + valor).encode('utf-8') + b'\n'
            
            if 'acrescimo' in totais and totais['acrescimo'] > 0:
                linha = "Acréscimo:"
                valor = f"R$ {totais['acrescimo']:.2f}"
                espacos = impressora.caracteres_linha - len(linha) - len(valor)
                comandos += (linha + ' ' * espacos + valor).encode('utf-8') + b'\n'
            
            if 'total' in totais:
                comandos += self.comandos.FONT_DOUBLE_HEIGHT
                comandos += self.comandos.BOLD_ON
                linha = "TOTAL:"
                valor = f"R$ {totais['total']:.2f}"
                espacos = max(1, (impressora.caracteres_linha // 2) - len(linha) - len(valor))
                comandos += (linha + ' ' * espacos + valor).encode('utf-8') + b'\n'
                comandos += self.comandos.BOLD_OFF
                comandos += self.comandos.FONT_NORMAL
        
        comandos += b'-' * impressora.caracteres_linha + b'\n'
        
        # Forma de pagamento
        if 'pagamento' in dados:
            pag = dados['pagamento']
            comandos += f"Forma de Pagamento: {pag.get('forma', 'N/A')}\n".encode('utf-8')
            if 'valor_pago' in pag:
                comandos += f"Valor Pago: R$ {pag['valor_pago']:.2f}\n".encode('utf-8')
            if 'troco' in pag and pag['troco'] > 0:
                comandos += f"Troco: R$ {pag['troco']:.2f}\n".encode('utf-8')
            comandos += b'\n'
        
        # QR Code
        if 'qrcode' in dados and impressora.suporta_qrcode:
            comandos += self.comandos.ALIGN_CENTER
            comandos += self._gerar_qrcode(dados['qrcode'])
            comandos += b'\n'
        
        # Código de barras
        if 'codigo_barras' in dados and impressora.suporta_codigo_barras:
            comandos += self.comandos.ALIGN_CENTER
            comandos += self._gerar_codigo_barras(
                dados['codigo_barras'],
                dados.get('tipo_codigo_barras', 'EAN13')
            )
            comandos += b'\n'
        
        # Mensagem final
        if 'mensagem_final' in dados:
            comandos += self.comandos.ALIGN_CENTER
            comandos += b'\n'
            for linha in dados['mensagem_final'].split('\n'):
                comandos += linha.encode('utf-8') + b'\n'
        
        # Espaço e corte
        comandos += b'\n' * 4
        if impressora.suporta_guilhotina:
            comandos += self.comandos.CUT_PARTIAL
        
        return comandos
    
    async def processar_roteamento_inteligente(
        self,
        tipo_impressao: str,
        local_origem: Optional[str] = None,
        categoria_produto: Optional[str] = None,
        evento_id: Optional[int] = None,
        db: Any = None
    ) -> Optional[ImpressoraInteligente]:
        """Encontrar melhor impressora baseado em regras de roteamento"""
        from sqlalchemy import and_, or_
        
        query = db.query(ImpressoraInteligente).filter(
            ImpressoraInteligente.ativo == True,
            ImpressoraInteligente.tipo_impressao == tipo_impressao
        )
        
        if evento_id:
            query = query.filter(ImpressoraInteligente.evento_id == evento_id)
        
        # Filtrar por local e categoria se especificados
        conditions = []
        if local_origem:
            conditions.append(
                or_(
                    ImpressoraInteligente.local_origem == local_origem,
                    ImpressoraInteligente.local_origem == None
                )
            )
        if categoria_produto:
            conditions.append(
                or_(
                    ImpressoraInteligente.categoria_produto == categoria_produto,
                    ImpressoraInteligente.categoria_produto == None
                )
            )
        
        if conditions:
            query = query.filter(and_(*conditions))
        
        # Ordenar por prioridade (maior primeiro)
        query = query.order_by(ImpressoraInteligente.prioridade.desc())
        
        # Verificar horário de funcionamento
        hora_atual = datetime.now().strftime("%H:%M")
        dia_semana = datetime.now().strftime("%a").lower()[:3]  # seg, ter, qua, etc
        
        roteamentos = query.all()
        
        for roteamento in roteamentos:
            # Verificar se está no horário de funcionamento
            if roteamento.hora_inicio and roteamento.hora_fim:
                if not (roteamento.hora_inicio <= hora_atual <= roteamento.hora_fim):
                    continue
            
            # Verificar dia da semana
            if roteamento.dias_semana:
                if dia_semana not in roteamento.dias_semana.lower():
                    continue
            
            # Este roteamento está válido
            return roteamento
        
        return None
    
    def formatar_cupom_venda(
        self,
        venda: Dict[str, Any],
        template: Optional[TemplateImpressao] = None
    ) -> str:
        """Formatar cupom de venda como JSON estruturado"""
        cupom = {
            'cabecalho': 'CUPOM FISCAL',
            'numero': venda.get('id', 'N/A'),
            'data': venda.get('data', datetime.now().strftime('%d/%m/%Y %H:%M')),
            'cliente': venda.get('cliente_nome', 'Consumidor'),
            'atendente': venda.get('operador_nome', 'Sistema'),
            'itens': [],
            'totais': {
                'subtotal': 0,
                'desconto': venda.get('desconto', 0),
                'total': venda.get('valor_total', 0)
            },
            'pagamento': {
                'forma': venda.get('forma_pagamento', 'Dinheiro'),
                'valor_pago': venda.get('valor_pago', 0),
                'troco': venda.get('troco', 0)
            }
        }
        
        # Adicionar itens
        for item in venda.get('itens', []):
            cupom['itens'].append({
                'quantidade': item.get('quantidade', 1),
                'nome': item.get('produto_nome', 'Produto'),
                'valor_unitario': item.get('valor_unitario', 0),
                'valor_total': item.get('valor_total', 0),
                'observacoes': item.get('observacoes', '')
            })
            cupom['totais']['subtotal'] += item.get('valor_total', 0)
        
        # Aplicar template se fornecido
        if template:
            if template.cabecalho:
                cupom['cabecalho'] = template.cabecalho
            if template.rodape:
                cupom['mensagem_final'] = template.rodape
            if template.incluir_qrcode and template.qrcode_conteudo:
                cupom['qrcode'] = template.qrcode_conteudo.format(**venda)
            if template.incluir_codigo_barras:
                cupom['codigo_barras'] = str(venda.get('id', '0000000000000')).zfill(13)
                cupom['tipo_codigo_barras'] = template.codigo_barras_tipo or 'EAN13'
        
        return json.dumps(cupom, ensure_ascii=False)