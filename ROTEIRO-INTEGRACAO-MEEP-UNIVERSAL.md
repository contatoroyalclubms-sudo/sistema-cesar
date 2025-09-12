# 🚀 ROTEIRO DE INTEGRAÇÃO MEEP-UNIVERSAL - IMPLEMENTAÇÃO COMPLETA

## 📋 ÍNDICE DE IMPLEMENTAÇÃO

1. [Preparação do Ambiente](#1-preparação-do-ambiente)
2. [Backend - Modelos de Dados](#2-backend---modelos-de-dados)
3. [Backend - Schemas e Validação](#3-backend---schemas-e-validação)
4. [Backend - Serviços MEEP](#4-backend---serviços-meep)
5. [Backend - Rotas da API](#5-backend---rotas-da-api)
6. [Frontend - Configuração Base](#6-frontend---configuração-base)
7. [Frontend - Componentes MEEP](#7-frontend---componentes-meep)
8. [Frontend - Dashboard Analítico](#8-frontend---dashboard-analítico)
9. [Captura de Dados - Scripts](#9-captura-de-dados---scripts)
10. [Testes e Validação](#10-testes-e-validação)
11. [Deploy e Monitoramento](#11-deploy-e-monitoramento)
12. [Checklist Final](#12-checklist-final)

---

## 1. PREPARAÇÃO DO AMBIENTE

### 1.1 Instalação de Dependências

#### Backend (Python)
```bash
cd paineluniversal/backend
poetry add httpx beautifulsoup4 lxml pandas numpy scikit-learn
poetry add celery redis python-dotenv
poetry add --dev pytest pytest-asyncio pytest-cov
```

#### Frontend (React)
```bash
cd paineluniversal/frontend
npm install recharts date-fns axios-retry lodash
npm install @tanstack/react-query zustand
npm install --save-dev @types/lodash
```

#### Captura (Node.js)
```bash
cd paineluniversal
mkdir meep-capture && cd meep-capture
npm init -y
npm install puppeteer cheerio axios dotenv
npm install node-cron winston
```

### 1.2 Variáveis de Ambiente

**paineluniversal/backend/.env**
```env
# MEEP Configuration
MEEP_API_URL=https://beta.portal.meep.com.br
MEEP_USERNAME=seu_usuario
MEEP_PASSWORD=sua_senha
MEEP_SYNC_INTERVAL=300  # 5 minutos
MEEP_CAPTURE_ENABLED=true
MEEP_WEBHOOK_SECRET=meep_webhook_secret_2025

# Cache Configuration
REDIS_MEEP_TTL=3600  # 1 hora
MEEP_BATCH_SIZE=100
MEEP_MAX_RETRIES=3
```

---

## 2. BACKEND - MODELOS DE DADOS

### 2.1 Criar Modelo MEEPEvento

**paineluniversal/backend/app/models/meep_models.py**
```python
from sqlalchemy import Column, Integer, String, DateTime, Float, JSON, Boolean, ForeignKey, Text, Index
from sqlalchemy.orm import relationship
from datetime import datetime
from ..database import Base

class MEEPEvento(Base):
    __tablename__ = "meep_eventos"
    
    id = Column(Integer, primary_key=True, index=True)
    meep_id = Column(String(100), unique=True, index=True)
    evento_id = Column(Integer, ForeignKey("eventos.id"), nullable=True)
    
    # Dados do MEEP
    nome = Column(String(255), nullable=False)
    data_inicio = Column(DateTime, nullable=False)
    data_fim = Column(DateTime, nullable=False)
    local = Column(String(500))
    cidade = Column(String(100))
    estado = Column(String(2))
    
    # Métricas
    total_inscritos = Column(Integer, default=0)
    total_presentes = Column(Integer, default=0)
    total_vendas = Column(Float, default=0.0)
    taxa_conversao = Column(Float, default=0.0)
    
    # Dados JSON flexíveis
    dados_completos = Column(JSON)
    metricas_detalhadas = Column(JSON)
    
    # Controle
    ultima_sincronizacao = Column(DateTime, default=datetime.utcnow)
    sincronizado = Column(Boolean, default=False)
    erro_sincronizacao = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    evento = relationship("Evento", back_populates="meep_evento")
    participantes = relationship("MEEPParticipante", back_populates="meep_evento")
    capturas = relationship("MEEPCaptura", back_populates="meep_evento")
    
    # Índices compostos
    __table_args__ = (
        Index('idx_meep_evento_data', 'data_inicio', 'data_fim'),
        Index('idx_meep_evento_local', 'cidade', 'estado'),
    )


class MEEPParticipante(Base):
    __tablename__ = "meep_participantes"
    
    id = Column(Integer, primary_key=True, index=True)
    meep_evento_id = Column(Integer, ForeignKey("meep_eventos.id"))
    
    # Dados do participante
    cpf = Column(String(11), index=True)
    nome = Column(String(255))
    email = Column(String(255))
    telefone = Column(String(20))
    
    # Status
    inscrito = Column(Boolean, default=True)
    presente = Column(Boolean, default=False)
    pagamento_status = Column(String(50))
    valor_pago = Column(Float, default=0.0)
    
    # Dados adicionais
    dados_extras = Column(JSON)
    
    # Timestamps
    data_inscricao = Column(DateTime)
    data_checkin = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    meep_evento = relationship("MEEPEvento", back_populates="participantes")
    
    # Índice único
    __table_args__ = (
        Index('idx_unique_participante', 'meep_evento_id', 'cpf', unique=True),
    )


class MEEPCaptura(Base):
    __tablename__ = "meep_capturas"
    
    id = Column(Integer, primary_key=True, index=True)
    meep_evento_id = Column(Integer, ForeignKey("meep_eventos.id"))
    
    # Dados da captura
    tipo = Column(String(50))  # 'lista_eventos', 'detalhes_evento', 'participantes'
    url = Column(String(500))
    status = Column(String(50))  # 'pendente', 'processando', 'concluido', 'erro'
    
    # Resultados
    total_registros = Column(Integer, default=0)
    registros_processados = Column(Integer, default=0)
    dados_capturados = Column(JSON)
    
    # Controle
    iniciado_em = Column(DateTime)
    finalizado_em = Column(DateTime)
    erro_mensagem = Column(Text)
    tentativas = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    meep_evento = relationship("MEEPEvento", back_populates="capturas")


class MEEPAnalytics(Base):
    __tablename__ = "meep_analytics"
    
    id = Column(Integer, primary_key=True, index=True)
    evento_id = Column(Integer, ForeignKey("eventos.id"))
    
    # Métricas agregadas
    periodo = Column(String(50))  # 'diario', 'semanal', 'mensal'
    data_referencia = Column(DateTime)
    
    # KPIs
    total_eventos = Column(Integer, default=0)
    total_participantes = Column(Integer, default=0)
    taxa_ocupacao = Column(Float, default=0.0)
    receita_total = Column(Float, default=0.0)
    ticket_medio = Column(Float, default=0.0)
    
    # Análises
    analise_demografica = Column(JSON)
    analise_geografica = Column(JSON)
    analise_temporal = Column(JSON)
    previsoes = Column(JSON)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Índices
    __table_args__ = (
        Index('idx_analytics_periodo', 'periodo', 'data_referencia'),
    )
```

### 2.2 Atualizar Modelo Evento Principal

**paineluniversal/backend/app/models.py** (adicionar ao modelo Evento existente)
```python
# Adicionar no modelo Evento
meep_evento = relationship("MEEPEvento", back_populates="evento", uselist=False)
meep_analytics = relationship("MEEPAnalytics", back_populates="evento")
```

---

## 3. BACKEND - SCHEMAS E VALIDAÇÃO

### 3.1 Criar Schemas Pydantic

**paineluniversal/backend/app/schemas/meep_schemas.py**
```python
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime

class MEEPEventoBase(BaseModel):
    meep_id: str
    nome: str
    data_inicio: datetime
    data_fim: datetime
    local: Optional[str] = None
    cidade: Optional[str] = None
    estado: Optional[str] = None

class MEEPEventoCreate(MEEPEventoBase):
    evento_id: Optional[int] = None
    dados_completos: Optional[Dict[str, Any]] = None

class MEEPEventoUpdate(BaseModel):
    total_inscritos: Optional[int] = None
    total_presentes: Optional[int] = None
    total_vendas: Optional[float] = None
    taxa_conversao: Optional[float] = None
    metricas_detalhadas: Optional[Dict[str, Any]] = None

class MEEPEventoResponse(MEEPEventoBase):
    id: int
    evento_id: Optional[int]
    total_inscritos: int
    total_presentes: int
    total_vendas: float
    taxa_conversao: float
    ultima_sincronizacao: datetime
    sincronizado: bool
    
    class Config:
        from_attributes = True

class MEEPParticipanteBase(BaseModel):
    cpf: str = Field(..., min_length=11, max_length=11)
    nome: str
    email: Optional[str] = None
    telefone: Optional[str] = None
    
    @validator('cpf')
    def validate_cpf(cls, v):
        # Remove caracteres não numéricos
        cpf = ''.join(filter(str.isdigit, v))
        if len(cpf) != 11:
            raise ValueError('CPF deve ter 11 dígitos')
        return cpf

class MEEPParticipanteCreate(MEEPParticipanteBase):
    meep_evento_id: int
    inscrito: bool = True
    presente: bool = False
    pagamento_status: Optional[str] = None
    valor_pago: float = 0.0

class MEEPParticipanteResponse(MEEPParticipanteBase):
    id: int
    meep_evento_id: int
    inscrito: bool
    presente: bool
    pagamento_status: Optional[str]
    valor_pago: float
    data_inscricao: Optional[datetime]
    data_checkin: Optional[datetime]
    
    class Config:
        from_attributes = True

class MEEPCapturaCreate(BaseModel):
    meep_evento_id: Optional[int] = None
    tipo: str = Field(..., pattern="^(lista_eventos|detalhes_evento|participantes)$")
    url: str

class MEEPCapturaStatus(BaseModel):
    id: int
    tipo: str
    status: str
    total_registros: int
    registros_processados: int
    iniciado_em: Optional[datetime]
    finalizado_em: Optional[datetime]
    erro_mensagem: Optional[str]
    
    class Config:
        from_attributes = True

class MEEPAnalyticsRequest(BaseModel):
    evento_id: Optional[int] = None
    periodo: str = Field(default="diario", pattern="^(diario|semanal|mensal)$")
    data_inicio: Optional[datetime] = None
    data_fim: Optional[datetime] = None

class MEEPAnalyticsResponse(BaseModel):
    periodo: str
    data_referencia: datetime
    total_eventos: int
    total_participantes: int
    taxa_ocupacao: float
    receita_total: float
    ticket_medio: float
    analise_demografica: Optional[Dict[str, Any]]
    analise_geografica: Optional[Dict[str, Any]]
    analise_temporal: Optional[Dict[str, Any]]
    
    class Config:
        from_attributes = True

class MEEPSyncRequest(BaseModel):
    force: bool = False
    evento_ids: Optional[List[int]] = None
    data_inicio: Optional[datetime] = None
    data_fim: Optional[datetime] = None

class MEEPSyncResponse(BaseModel):
    status: str
    eventos_sincronizados: int
    participantes_sincronizados: int
    erros: List[str] = []
    tempo_execucao: float
```

---

## 4. BACKEND - SERVIÇOS MEEP

### 4.1 Cliente MEEP

**paineluniversal/backend/app/services/meep_client.py**
```python
import httpx
from typing import Optional, Dict, Any, List
from datetime import datetime
import asyncio
from bs4 import BeautifulSoup
import json
import logging
from ..config import settings

logger = logging.getLogger(__name__)

class MEEPClient:
    def __init__(self):
        self.base_url = settings.MEEP_API_URL
        self.username = settings.MEEP_USERNAME
        self.password = settings.MEEP_PASSWORD
        self.session = None
        self.cookies = {}
        
    async def __aenter__(self):
        self.session = httpx.AsyncClient(
            timeout=30.0,
            follow_redirects=True,
            verify=False  # Apenas para desenvolvimento
        )
        await self.login()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.aclose()
            
    async def login(self):
        """Realiza login no MEEP"""
        try:
            login_data = {
                "username": self.username,
                "password": self.password
            }
            
            response = await self.session.post(
                f"{self.base_url}/login",
                data=login_data
            )
            
            if response.status_code == 200:
                self.cookies = response.cookies
                logger.info("Login MEEP realizado com sucesso")
                return True
            else:
                logger.error(f"Erro no login MEEP: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Erro ao fazer login no MEEP: {str(e)}")
            return False
            
    async def get_eventos(self, data_inicio: Optional[datetime] = None, 
                         data_fim: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """Busca lista de eventos do MEEP"""
        try:
            params = {}
            if data_inicio:
                params["data_inicio"] = data_inicio.strftime("%Y-%m-%d")
            if data_fim:
                params["data_fim"] = data_fim.strftime("%Y-%m-%d")
                
            response = await self.session.get(
                f"{self.base_url}/eventos",
                params=params,
                cookies=self.cookies
            )
            
            if response.status_code == 200:
                # Parse HTML ou JSON dependendo da resposta
                if "application/json" in response.headers.get("content-type", ""):
                    return response.json()
                else:
                    return self._parse_eventos_html(response.text)
            else:
                logger.error(f"Erro ao buscar eventos: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Erro ao buscar eventos do MEEP: {str(e)}")
            return []
            
    def _parse_eventos_html(self, html: str) -> List[Dict[str, Any]]:
        """Parse HTML para extrair eventos"""
        soup = BeautifulSoup(html, 'html.parser')
        eventos = []
        
        # Adaptar seletores conforme estrutura real do MEEP
        for evento_div in soup.select('.evento-item'):
            evento = {
                'meep_id': evento_div.get('data-id'),
                'nome': evento_div.select_one('.evento-nome').text.strip(),
                'data_inicio': evento_div.select_one('.evento-data-inicio').text.strip(),
                'local': evento_div.select_one('.evento-local').text.strip(),
                'total_inscritos': int(evento_div.select_one('.total-inscritos').text.strip())
            }
            eventos.append(evento)
            
        return eventos
        
    async def get_evento_detalhes(self, meep_id: str) -> Optional[Dict[str, Any]]:
        """Busca detalhes de um evento específico"""
        try:
            response = await self.session.get(
                f"{self.base_url}/eventos/{meep_id}",
                cookies=self.cookies
            )
            
            if response.status_code == 200:
                if "application/json" in response.headers.get("content-type", ""):
                    return response.json()
                else:
                    return self._parse_evento_detalhes_html(response.text)
            else:
                logger.error(f"Erro ao buscar detalhes do evento {meep_id}: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Erro ao buscar detalhes do evento {meep_id}: {str(e)}")
            return None
            
    def _parse_evento_detalhes_html(self, html: str) -> Dict[str, Any]:
        """Parse HTML para extrair detalhes do evento"""
        soup = BeautifulSoup(html, 'html.parser')
        
        # Adaptar seletores conforme estrutura real
        detalhes = {
            'nome': soup.select_one('h1.evento-titulo').text.strip(),
            'descricao': soup.select_one('.evento-descricao').text.strip(),
            'data_inicio': soup.select_one('.data-inicio').text.strip(),
            'data_fim': soup.select_one('.data-fim').text.strip(),
            'local': soup.select_one('.local-completo').text.strip(),
            'total_inscritos': int(soup.select_one('.stat-inscritos').text.strip()),
            'total_presentes': int(soup.select_one('.stat-presentes').text.strip()),
            'total_vendas': float(soup.select_one('.stat-vendas').text.replace('R$', '').replace(',', '.').strip())
        }
        
        return detalhes
        
    async def get_participantes(self, meep_id: str, pagina: int = 1, 
                               por_pagina: int = 100) -> List[Dict[str, Any]]:
        """Busca participantes de um evento"""
        try:
            params = {
                'page': pagina,
                'per_page': por_pagina
            }
            
            response = await self.session.get(
                f"{self.base_url}/eventos/{meep_id}/participantes",
                params=params,
                cookies=self.cookies
            )
            
            if response.status_code == 200:
                if "application/json" in response.headers.get("content-type", ""):
                    return response.json()
                else:
                    return self._parse_participantes_html(response.text)
            else:
                logger.error(f"Erro ao buscar participantes: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Erro ao buscar participantes: {str(e)}")
            return []
            
    def _parse_participantes_html(self, html: str) -> List[Dict[str, Any]]:
        """Parse HTML para extrair participantes"""
        soup = BeautifulSoup(html, 'html.parser')
        participantes = []
        
        # Adaptar seletores conforme estrutura real
        for row in soup.select('tr.participante-row'):
            participante = {
                'cpf': row.select_one('.cpf').text.strip(),
                'nome': row.select_one('.nome').text.strip(),
                'email': row.select_one('.email').text.strip(),
                'telefone': row.select_one('.telefone').text.strip(),
                'status': row.select_one('.status').text.strip(),
                'presente': 'presente' in row.get('class', [])
            }
            participantes.append(participante)
            
        return participantes
```

### 4.2 Serviço de Sincronização

**paineluniversal/backend/app/services/meep_sync.py**
```python
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
import asyncio
import logging
from ..models.meep_models import MEEPEvento, MEEPParticipante, MEEPCaptura
from ..services.meep_client import MEEPClient
from ..database import get_db
from ..config import settings
import redis
import json

logger = logging.getLogger(__name__)

class MEEPSyncService:
    def __init__(self, db: Session):
        self.db = db
        self.client = None
        self.redis_client = redis.Redis.from_url(
            settings.REDIS_URL,
            decode_responses=True
        ) if settings.REDIS_URL else None
        
    async def sync_eventos(self, force: bool = False, 
                          evento_ids: Optional[List[int]] = None) -> Dict[str, Any]:
        """Sincroniza eventos do MEEP"""
        start_time = datetime.utcnow()
        resultado = {
            'status': 'iniciado',
            'eventos_sincronizados': 0,
            'participantes_sincronizados': 0,
            'erros': []
        }
        
        try:
            async with MEEPClient() as client:
                self.client = client
                
                # Buscar eventos para sincronizar
                if evento_ids:
                    meep_eventos = self.db.query(MEEPEvento).filter(
                        MEEPEvento.evento_id.in_(evento_ids)
                    ).all()
                else:
                    # Sincronizar eventos não sincronizados ou antigos
                    cutoff_time = datetime.utcnow() - timedelta(
                        seconds=settings.MEEP_SYNC_INTERVAL
                    )
                    
                    query = self.db.query(MEEPEvento)
                    if not force:
                        query = query.filter(
                            or_(
                                MEEPEvento.sincronizado == False,
                                MEEPEvento.ultima_sincronizacao < cutoff_time
                            )
                        )
                    
                    meep_eventos = query.all()
                
                # Se não houver eventos locais, buscar do MEEP
                if not meep_eventos and not evento_ids:
                    await self._importar_novos_eventos()
                    meep_eventos = self.db.query(MEEPEvento).all()
                
                # Sincronizar cada evento
                for meep_evento in meep_eventos:
                    try:
                        await self._sync_evento(meep_evento)
                        resultado['eventos_sincronizados'] += 1
                        
                        # Sincronizar participantes
                        participantes_count = await self._sync_participantes(meep_evento)
                        resultado['participantes_sincronizados'] += participantes_count
                        
                    except Exception as e:
                        erro = f"Erro ao sincronizar evento {meep_evento.meep_id}: {str(e)}"
                        logger.error(erro)
                        resultado['erros'].append(erro)
                
                self.db.commit()
                resultado['status'] = 'concluido'
                
        except Exception as e:
            erro = f"Erro geral na sincronização: {str(e)}"
            logger.error(erro)
            resultado['status'] = 'erro'
            resultado['erros'].append(erro)
            self.db.rollback()
        
        # Calcular tempo de execução
        resultado['tempo_execucao'] = (datetime.utcnow() - start_time).total_seconds()
        
        # Salvar no cache
        if self.redis_client:
            cache_key = f"meep:sync:ultimo_resultado"
            self.redis_client.setex(
                cache_key,
                3600,
                json.dumps(resultado, default=str)
            )
        
        return resultado
    
    async def _importar_novos_eventos(self):
        """Importa novos eventos do MEEP"""
        logger.info("Importando novos eventos do MEEP...")
        
        # Buscar eventos dos últimos 30 dias
        data_inicio = datetime.utcnow() - timedelta(days=30)
        eventos = await self.client.get_eventos(data_inicio=data_inicio)
        
        for evento_data in eventos:
            # Verificar se já existe
            meep_id = evento_data.get('meep_id')
            if not meep_id:
                continue
                
            existe = self.db.query(MEEPEvento).filter(
                MEEPEvento.meep_id == meep_id
            ).first()
            
            if not existe:
                # Criar novo evento
                meep_evento = MEEPEvento(
                    meep_id=meep_id,
                    nome=evento_data.get('nome'),
                    data_inicio=self._parse_datetime(evento_data.get('data_inicio')),
                    data_fim=self._parse_datetime(evento_data.get('data_fim')),
                    local=evento_data.get('local'),
                    cidade=evento_data.get('cidade'),
                    estado=evento_data.get('estado'),
                    dados_completos=evento_data
                )
                self.db.add(meep_evento)
                
        self.db.commit()
        
    async def _sync_evento(self, meep_evento: MEEPEvento):
        """Sincroniza um evento específico"""
        logger.info(f"Sincronizando evento {meep_evento.meep_id}...")
        
        # Buscar detalhes atualizados
        detalhes = await self.client.get_evento_detalhes(meep_evento.meep_id)
        
        if detalhes:
            # Atualizar dados do evento
            meep_evento.nome = detalhes.get('nome', meep_evento.nome)
            meep_evento.local = detalhes.get('local', meep_evento.local)
            meep_evento.total_inscritos = detalhes.get('total_inscritos', 0)
            meep_evento.total_presentes = detalhes.get('total_presentes', 0)
            meep_evento.total_vendas = detalhes.get('total_vendas', 0.0)
            
            # Calcular taxa de conversão
            if meep_evento.total_inscritos > 0:
                meep_evento.taxa_conversao = (
                    meep_evento.total_presentes / meep_evento.total_inscritos * 100
                )
            
            # Salvar dados completos
            meep_evento.dados_completos = detalhes
            meep_evento.ultima_sincronizacao = datetime.utcnow()
            meep_evento.sincronizado = True
            meep_evento.erro_sincronizacao = None
            
            # Criar captura de registro
            captura = MEEPCaptura(
                meep_evento_id=meep_evento.id,
                tipo='detalhes_evento',
                url=f"{settings.MEEP_API_URL}/eventos/{meep_evento.meep_id}",
                status='concluido',
                total_registros=1,
                registros_processados=1,
                iniciado_em=datetime.utcnow(),
                finalizado_em=datetime.utcnow()
            )
            self.db.add(captura)
            
    async def _sync_participantes(self, meep_evento: MEEPEvento) -> int:
        """Sincroniza participantes de um evento"""
        logger.info(f"Sincronizando participantes do evento {meep_evento.meep_id}...")
        
        total_sincronizados = 0
        pagina = 1
        
        while True:
            participantes = await self.client.get_participantes(
                meep_evento.meep_id,
                pagina=pagina
            )
            
            if not participantes:
                break
                
            for part_data in participantes:
                cpf = part_data.get('cpf', '').replace('.', '').replace('-', '')
                
                if not cpf:
                    continue
                    
                # Verificar se já existe
                participante = self.db.query(MEEPParticipante).filter(
                    and_(
                        MEEPParticipante.meep_evento_id == meep_evento.id,
                        MEEPParticipante.cpf == cpf
                    )
                ).first()
                
                if participante:
                    # Atualizar
                    participante.presente = part_data.get('presente', False)
                    participante.pagamento_status = part_data.get('status')
                    participante.dados_extras = part_data
                else:
                    # Criar novo
                    participante = MEEPParticipante(
                        meep_evento_id=meep_evento.id,
                        cpf=cpf,
                        nome=part_data.get('nome'),
                        email=part_data.get('email'),
                        telefone=part_data.get('telefone'),
                        presente=part_data.get('presente', False),
                        pagamento_status=part_data.get('status'),
                        valor_pago=part_data.get('valor_pago', 0.0),
                        dados_extras=part_data
                    )
                    self.db.add(participante)
                
                total_sincronizados += 1
            
            # Próxima página
            if len(participantes) < 100:
                break
            pagina += 1
            
        return total_sincronizados
        
    def _parse_datetime(self, date_str: str) -> Optional[datetime]:
        """Parse de string para datetime"""
        if not date_str:
            return None
            
        formats = [
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d",
            "%d/%m/%Y %H:%M",
            "%d/%m/%Y"
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except:
                continue
                
        return None
```

---

## 5. BACKEND - ROTAS DA API

### 5.1 Router Principal MEEP

**paineluniversal/backend/app/routers/meep_integration.py**
```python
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from ..database import get_db
from ..auth import get_current_user
from ..models import Usuario
from ..models.meep_models import MEEPEvento, MEEPParticipante, MEEPAnalytics
from ..schemas.meep_schemas import (
    MEEPEventoResponse,
    MEEPParticipanteResponse,
    MEEPSyncRequest,
    MEEPSyncResponse,
    MEEPAnalyticsRequest,
    MEEPAnalyticsResponse,
    MEEPCapturaStatus
)
from ..services.meep_sync import MEEPSyncService
from ..services.meep_analytics import MEEPAnalyticsService

router = APIRouter(prefix="/api/meep", tags=["MEEP Integration"])

@router.get("/eventos", response_model=List[MEEPEventoResponse])
async def listar_eventos_meep(
    sincronizado: Optional[bool] = None,
    data_inicio: Optional[datetime] = None,
    data_fim: Optional[datetime] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Lista eventos do MEEP"""
    query = db.query(MEEPEvento)
    
    if sincronizado is not None:
        query = query.filter(MEEPEvento.sincronizado == sincronizado)
    
    if data_inicio:
        query = query.filter(MEEPEvento.data_inicio >= data_inicio)
    
    if data_fim:
        query = query.filter(MEEPEvento.data_fim <= data_fim)
    
    total = query.count()
    eventos = query.offset(skip).limit(limit).all()
    
    return eventos

@router.get("/eventos/{meep_id}", response_model=MEEPEventoResponse)
async def obter_evento_meep(
    meep_id: str,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Obtém detalhes de um evento MEEP"""
    evento = db.query(MEEPEvento).filter(
        MEEPEvento.meep_id == meep_id
    ).first()
    
    if not evento:
        raise HTTPException(status_code=404, detail="Evento não encontrado")
    
    return evento

@router.get("/eventos/{meep_id}/participantes", 
           response_model=List[MEEPParticipanteResponse])
async def listar_participantes_meep(
    meep_id: str,
    presente: Optional[bool] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Lista participantes de um evento MEEP"""
    # Buscar evento
    evento = db.query(MEEPEvento).filter(
        MEEPEvento.meep_id == meep_id
    ).first()
    
    if not evento:
        raise HTTPException(status_code=404, detail="Evento não encontrado")
    
    query = db.query(MEEPParticipante).filter(
        MEEPParticipante.meep_evento_id == evento.id
    )
    
    if presente is not None:
        query = query.filter(MEEPParticipante.presente == presente)
    
    participantes = query.offset(skip).limit(limit).all()
    
    return participantes

@router.post("/sync", response_model=MEEPSyncResponse)
async def sincronizar_meep(
    request: MEEPSyncRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Inicia sincronização com MEEP"""
    if current_user.tipo != "admin":
        raise HTTPException(
            status_code=403,
            detail="Apenas administradores podem sincronizar"
        )
    
    sync_service = MEEPSyncService(db)
    
    # Executar em background
    background_tasks.add_task(
        sync_service.sync_eventos,
        force=request.force,
        evento_ids=request.evento_ids
    )
    
    return {
        "status": "sincronização iniciada",
        "eventos_sincronizados": 0,
        "participantes_sincronizados": 0,
        "erros": [],
        "tempo_execucao": 0
    }

@router.get("/sync/status", response_model=MEEPSyncResponse)
async def status_sincronizacao(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Verifica status da última sincronização"""
    import redis
    import json
    from ..config import settings
    
    if settings.REDIS_URL:
        r = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)
        cache_key = "meep:sync:ultimo_resultado"
        resultado = r.get(cache_key)
        
        if resultado:
            return json.loads(resultado)
    
    return {
        "status": "nenhuma sincronização recente",
        "eventos_sincronizados": 0,
        "participantes_sincronizados": 0,
        "erros": [],
        "tempo_execucao": 0
    }

@router.get("/analytics", response_model=List[MEEPAnalyticsResponse])
async def obter_analytics(
    request: MEEPAnalyticsRequest = Depends(),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Obtém analytics do MEEP"""
    analytics_service = MEEPAnalyticsService(db)
    
    return await analytics_service.gerar_analytics(
        evento_id=request.evento_id,
        periodo=request.periodo,
        data_inicio=request.data_inicio,
        data_fim=request.data_fim
    )

@router.post("/analytics/generate")
async def gerar_analytics(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Gera analytics para todos os eventos"""
    if current_user.tipo != "admin":
        raise HTTPException(
            status_code=403,
            detail="Apenas administradores podem gerar analytics"
        )
    
    analytics_service = MEEPAnalyticsService(db)
    background_tasks.add_task(analytics_service.processar_todos_analytics)
    
    return {"message": "Geração de analytics iniciada"}

@router.get("/capturas", response_model=List[MEEPCapturaStatus])
async def listar_capturas(
    status: Optional[str] = None,
    tipo: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Lista capturas realizadas"""
    from ..models.meep_models import MEEPCaptura
    
    query = db.query(MEEPCaptura)
    
    if status:
        query = query.filter(MEEPCaptura.status == status)
    
    if tipo:
        query = query.filter(MEEPCaptura.tipo == tipo)
    
    query = query.order_by(MEEPCaptura.created_at.desc())
    
    capturas = query.offset(skip).limit(limit).all()
    
    return capturas

@router.post("/webhook")
async def webhook_meep(
    data: dict,
    db: Session = Depends(get_db)
):
    """Recebe webhooks do MEEP"""
    # Validar assinatura do webhook
    # Processar dados recebidos
    
    tipo_evento = data.get("tipo")
    
    if tipo_evento == "novo_inscrito":
        # Processar novo inscrito
        pass
    elif tipo_evento == "checkin":
        # Processar checkin
        pass
    
    return {"status": "recebido"}
```

### 5.2 Atualizar main.py

**paineluniversal/backend/app/main.py** (adicionar)
```python
# Importar novo router
from .routers import meep_integration

# Adicionar ao app
app.include_router(meep_integration.router)

# Adicionar tabelas MEEP ao criar banco
from .models.meep_models import MEEPEvento, MEEPParticipante, MEEPCaptura, MEEPAnalytics
```

---

## 6. FRONTEND - CONFIGURAÇÃO BASE

### 6.1 API Client MEEP

**paineluniversal/frontend/src/services/meepApi.ts**
```typescript
import axios from 'axios';
import { format } from 'date-fns';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8003';

const meepApi = axios.create({
  baseURL: `${API_BASE}/api/meep`,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor para adicionar token
meepApi.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Tipos TypeScript
export interface MEEPEvento {
  id: number;
  meep_id: string;
  nome: string;
  data_inicio: string;
  data_fim: string;
  local?: string;
  cidade?: string;
  estado?: string;
  total_inscritos: number;
  total_presentes: number;
  total_vendas: number;
  taxa_conversao: number;
  sincronizado: boolean;
  ultima_sincronizacao: string;
}

export interface MEEPParticipante {
  id: number;
  cpf: string;
  nome: string;
  email?: string;
  telefone?: string;
  inscrito: boolean;
  presente: boolean;
  pagamento_status?: string;
  valor_pago: number;
}

export interface MEEPAnalytics {
  periodo: string;
  data_referencia: string;
  total_eventos: number;
  total_participantes: number;
  taxa_ocupacao: number;
  receita_total: number;
  ticket_medio: number;
  analise_demografica?: any;
  analise_geografica?: any;
  analise_temporal?: any;
}

// Funções da API
export const meepService = {
  // Eventos
  async getEventos(params?: {
    sincronizado?: boolean;
    data_inicio?: Date;
    data_fim?: Date;
  }) {
    const queryParams = new URLSearchParams();
    if (params?.sincronizado !== undefined) {
      queryParams.append('sincronizado', params.sincronizado.toString());
    }
    if (params?.data_inicio) {
      queryParams.append('data_inicio', format(params.data_inicio, 'yyyy-MM-dd'));
    }
    if (params?.data_fim) {
      queryParams.append('data_fim', format(params.data_fim, 'yyyy-MM-dd'));
    }
    
    const response = await meepApi.get<MEEPEvento[]>(`/eventos?${queryParams}`);
    return response.data;
  },

  async getEvento(meepId: string) {
    const response = await meepApi.get<MEEPEvento>(`/eventos/${meepId}`);
    return response.data;
  },

  // Participantes
  async getParticipantes(meepId: string, presente?: boolean) {
    const params = presente !== undefined ? { presente } : {};
    const response = await meepApi.get<MEEPParticipante[]>(
      `/eventos/${meepId}/participantes`,
      { params }
    );
    return response.data;
  },

  // Sincronização
  async sincronizar(params?: {
    force?: boolean;
    evento_ids?: number[];
  }) {
    const response = await meepApi.post('/sync', params || {});
    return response.data;
  },

  async getSyncStatus() {
    const response = await meepApi.get('/sync/status');
    return response.data;
  },

  // Analytics
  async getAnalytics(params?: {
    evento_id?: number;
    periodo?: 'diario' | 'semanal' | 'mensal';
    data_inicio?: Date;
    data_fim?: Date;
  }) {
    const response = await meepApi.get<MEEPAnalytics[]>('/analytics', { params });
    return response.data;
  },

  async generateAnalytics() {
    const response = await meepApi.post('/analytics/generate');
    return response.data;
  },

  // Capturas
  async getCapturas(params?: {
    status?: string;
    tipo?: string;
  }) {
    const response = await meepApi.get('/capturas', { params });
    return response.data;
  }
};
```

---

## 7. FRONTEND - COMPONENTES MEEP

### 7.1 Dashboard Principal MEEP

**paineluniversal/frontend/src/components/meep/MEEPDashboard.tsx**
```tsx
import React, { useState, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Alert, AlertDescription } from '@/components/ui/alert';
import {
  BarChart,
  Bar,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import { 
  RefreshCw, 
  Calendar, 
  Users, 
  TrendingUp, 
  DollarSign,
  CheckCircle,
  XCircle,
  Clock,
  Activity
} from 'lucide-react';
import { format } from 'date-fns';
import { ptBR } from 'date-fns/locale';
import { meepService, MEEPEvento, MEEPAnalytics } from '@/services/meepApi';
import { toast } from '@/components/ui/use-toast';

export function MEEPDashboard() {
  const [selectedPeriodo, setSelectedPeriodo] = useState<'diario' | 'semanal' | 'mensal'>('diario');
  const queryClient = useQueryClient();

  // Query para buscar eventos
  const { data: eventos, isLoading: loadingEventos } = useQuery({
    queryKey: ['meep-eventos'],
    queryFn: () => meepService.getEventos(),
    refetchInterval: 60000, // Atualizar a cada minuto
  });

  // Query para buscar analytics
  const { data: analytics, isLoading: loadingAnalytics } = useQuery({
    queryKey: ['meep-analytics', selectedPeriodo],
    queryFn: () => meepService.getAnalytics({ periodo: selectedPeriodo }),
  });

  // Query para status de sincronização
  const { data: syncStatus } = useQuery({
    queryKey: ['meep-sync-status'],
    queryFn: () => meepService.getSyncStatus(),
    refetchInterval: 5000, // Atualizar a cada 5 segundos
  });

  // Mutation para sincronizar
  const syncMutation = useMutation({
    mutationFn: meepService.sincronizar,
    onSuccess: () => {
      toast({
        title: 'Sincronização iniciada',
        description: 'Os dados estão sendo sincronizados com o MEEP',
      });
      queryClient.invalidateQueries({ queryKey: ['meep-sync-status'] });
    },
    onError: () => {
      toast({
        title: 'Erro na sincronização',
        description: 'Não foi possível iniciar a sincronização',
        variant: 'destructive',
      });
    },
  });

  // Calcular estatísticas
  const stats = React.useMemo(() => {
    if (!eventos) return null;

    const totalEventos = eventos.length;
    const eventosSincronizados = eventos.filter(e => e.sincronizado).length;
    const totalInscritos = eventos.reduce((acc, e) => acc + e.total_inscritos, 0);
    const totalPresentes = eventos.reduce((acc, e) => acc + e.total_presentes, 0);
    const totalVendas = eventos.reduce((acc, e) => acc + e.total_vendas, 0);
    const taxaConversaoMedia = totalInscritos > 0 
      ? (totalPresentes / totalInscritos * 100).toFixed(1)
      : '0';

    return {
      totalEventos,
      eventosSincronizados,
      totalInscritos,
      totalPresentes,
      totalVendas,
      taxaConversaoMedia,
    };
  }, [eventos]);

  // Preparar dados para gráficos
  const chartData = React.useMemo(() => {
    if (!analytics || analytics.length === 0) return null;

    // Dados para gráfico de linha (evolução temporal)
    const evolucaoTemporal = analytics.map(a => ({
      data: format(new Date(a.data_referencia), 'dd/MM', { locale: ptBR }),
      participantes: a.total_participantes,
      receita: a.receita_total,
      ocupacao: a.taxa_ocupacao,
    }));

    // Dados para gráfico de pizza (distribuição)
    const distribuicao = [
      { name: 'Presentes', value: stats?.totalPresentes || 0, color: '#10b981' },
      { name: 'Ausentes', value: (stats?.totalInscritos || 0) - (stats?.totalPresentes || 0), color: '#ef4444' },
    ];

    return {
      evolucaoTemporal,
      distribuicao,
    };
  }, [analytics, stats]);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">Dashboard MEEP</h1>
          <p className="text-muted-foreground">
            Integração com o sistema MEEP para análise de eventos
          </p>
        </div>
        <div className="flex gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => queryClient.invalidateQueries()}
          >
            <RefreshCw className="h-4 w-4 mr-2" />
            Atualizar
          </Button>
          <Button
            size="sm"
            onClick={() => syncMutation.mutate({ force: false })}
            disabled={syncMutation.isPending}
          >
            {syncMutation.isPending ? (
              <>
                <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                Sincronizando...
              </>
            ) : (
              <>
                <Activity className="h-4 w-4 mr-2" />
                Sincronizar
              </>
            )}
          </Button>
        </div>
      </div>

      {/* Status de Sincronização */}
      {syncStatus && syncStatus.status !== 'nenhuma sincronização recente' && (
        <Alert>
          <AlertDescription className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              {syncStatus.status === 'concluido' ? (
                <CheckCircle className="h-4 w-4 text-green-500" />
              ) : syncStatus.status === 'erro' ? (
                <XCircle className="h-4 w-4 text-red-500" />
              ) : (
                <Clock className="h-4 w-4 text-yellow-500 animate-pulse" />
              )}
              <span>
                Status: {syncStatus.status} | 
                Eventos: {syncStatus.eventos_sincronizados} | 
                Participantes: {syncStatus.participantes_sincronizados}
              </span>
            </div>
            {syncStatus.tempo_execucao > 0 && (
              <span className="text-sm text-muted-foreground">
                Tempo: {syncStatus.tempo_execucao.toFixed(2)}s
              </span>
            )}
          </AlertDescription>
        </Alert>
      )}

      {/* Cards de Estatísticas */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total de Eventos</CardTitle>
            <Calendar className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats?.totalEventos || 0}</div>
            <p className="text-xs text-muted-foreground">
              {stats?.eventosSincronizados || 0} sincronizados
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total de Inscritos</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats?.totalInscritos || 0}</div>
            <p className="text-xs text-muted-foreground">
              {stats?.totalPresentes || 0} presentes
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Taxa de Conversão</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats?.taxaConversaoMedia || 0}%</div>
            <p className="text-xs text-muted-foreground">
              Média de presença
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Vendas Totais</CardTitle>
            <DollarSign className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              R$ {(stats?.totalVendas || 0).toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
            </div>
            <p className="text-xs text-muted-foreground">
              Receita acumulada
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Tabs com Gráficos */}
      <Tabs defaultValue="overview" className="space-y-4">
        <TabsList>
          <TabsTrigger value="overview">Visão Geral</TabsTrigger>
          <TabsTrigger value="eventos">Eventos</TabsTrigger>
          <TabsTrigger value="analytics">Analytics</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            {/* Gráfico de Evolução */}
            <Card>
              <CardHeader>
                <CardTitle>Evolução Temporal</CardTitle>
                <CardDescription>
                  Participantes e receita ao longo do tempo
                </CardDescription>
              </CardHeader>
              <CardContent>
                {chartData?.evolucaoTemporal && (
                  <ResponsiveContainer width="100%" height={300}>
                    <LineChart data={chartData.evolucaoTemporal}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="data" />
                      <YAxis yAxisId="left" />
                      <YAxis yAxisId="right" orientation="right" />
                      <Tooltip />
                      <Legend />
                      <Line
                        yAxisId="left"
                        type="monotone"
                        dataKey="participantes"
                        stroke="#3b82f6"
                        name="Participantes"
                      />
                      <Line
                        yAxisId="right"
                        type="monotone"
                        dataKey="receita"
                        stroke="#10b981"
                        name="Receita (R$)"
                      />
                    </LineChart>
                  </ResponsiveContainer>
                )}
              </CardContent>
            </Card>

            {/* Gráfico de Pizza */}
            <Card>
              <CardHeader>
                <CardTitle>Taxa de Presença</CardTitle>
                <CardDescription>
                  Distribuição de presentes vs ausentes
                </CardDescription>
              </CardHeader>
              <CardContent>
                {chartData?.distribuicao && (
                  <ResponsiveContainer width="100%" height={300}>
                    <PieChart>
                      <Pie
                        data={chartData.distribuicao}
                        cx="50%"
                        cy="50%"
                        labelLine={false}
                        label={(entry) => `${entry.name}: ${entry.value}`}
                        outerRadius={80}
                        fill="#8884d8"
                        dataKey="value"
                      >
                        {chartData.distribuicao.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={entry.color} />
                        ))}
                      </Pie>
                      <Tooltip />
                    </PieChart>
                  </ResponsiveContainer>
                )}
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="eventos" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Lista de Eventos MEEP</CardTitle>
              <CardDescription>
                Eventos sincronizados do sistema MEEP
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {loadingEventos ? (
                  <p>Carregando eventos...</p>
                ) : eventos && eventos.length > 0 ? (
                  eventos.map((evento) => (
                    <div
                      key={evento.id}
                      className="flex items-center justify-between p-3 border rounded-lg"
                    >
                      <div className="flex-1">
                        <div className="flex items-center gap-2">
                          <span className="font-medium">{evento.nome}</span>
                          {evento.sincronizado ? (
                            <Badge variant="success">Sincronizado</Badge>
                          ) : (
                            <Badge variant="secondary">Pendente</Badge>
                          )}
                        </div>
                        <div className="text-sm text-muted-foreground mt-1">
                          {evento.local && `${evento.local} • `}
                          {evento.cidade && `${evento.cidade}/${evento.estado} • `}
                          {format(new Date(evento.data_inicio), 'dd/MM/yyyy')}
                        </div>
                      </div>
                      <div className="text-right">
                        <div className="text-sm">
                          <span className="font-medium">{evento.total_inscritos}</span> inscritos
                        </div>
                        <div className="text-sm text-muted-foreground">
                          <span className="font-medium">{evento.total_presentes}</span> presentes
                        </div>
                        <div className="text-sm text-green-600">
                          R$ {evento.total_vendas.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
                        </div>
                      </div>
                    </div>
                  ))
                ) : (
                  <p>Nenhum evento encontrado</p>
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="analytics" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Analytics Detalhado</CardTitle>
              <CardDescription>
                Análise detalhada dos eventos MEEP
              </CardDescription>
              <div className="flex gap-2 mt-2">
                <Button
                  size="sm"
                  variant={selectedPeriodo === 'diario' ? 'default' : 'outline'}
                  onClick={() => setSelectedPeriodo('diario')}
                >
                  Diário
                </Button>
                <Button
                  size="sm"
                  variant={selectedPeriodo === 'semanal' ? 'default' : 'outline'}
                  onClick={() => setSelectedPeriodo('semanal')}
                >
                  Semanal
                </Button>
                <Button
                  size="sm"
                  variant={selectedPeriodo === 'mensal' ? 'default' : 'outline'}
                  onClick={() => setSelectedPeriodo('mensal')}
                >
                  Mensal
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              {loadingAnalytics ? (
                <p>Carregando analytics...</p>
              ) : analytics && analytics.length > 0 ? (
                <div className="space-y-4">
                  {/* Gráfico de barras com métricas */}
                  <ResponsiveContainer width="100%" height={400}>
                    <BarChart data={analytics}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis 
                        dataKey="data_referencia" 
                        tickFormatter={(value) => format(new Date(value), 'dd/MM')}
                      />
                      <YAxis />
                      <Tooltip 
                        labelFormatter={(value) => format(new Date(value), 'dd/MM/yyyy')}
                      />
                      <Legend />
                      <Bar dataKey="total_eventos" fill="#3b82f6" name="Eventos" />
                      <Bar dataKey="total_participantes" fill="#10b981" name="Participantes" />
                      <Bar dataKey="taxa_ocupacao" fill="#f59e0b" name="Taxa Ocupação (%)" />
                    </BarChart>
                  </ResponsiveContainer>

                  {/* Tabela com detalhes */}
                  <div className="overflow-x-auto">
                    <table className="w-full text-sm">
                      <thead>
                        <tr className="border-b">
                          <th className="text-left p-2">Data</th>
                          <th className="text-right p-2">Eventos</th>
                          <th className="text-right p-2">Participantes</th>
                          <th className="text-right p-2">Taxa Ocupação</th>
                          <th className="text-right p-2">Receita</th>
                          <th className="text-right p-2">Ticket Médio</th>
                        </tr>
                      </thead>
                      <tbody>
                        {analytics.map((item, index) => (
                          <tr key={index} className="border-b">
                            <td className="p-2">
                              {format(new Date(item.data_referencia), 'dd/MM/yyyy')}
                            </td>
                            <td className="text-right p-2">{item.total_eventos}</td>
                            <td className="text-right p-2">{item.total_participantes}</td>
                            <td className="text-right p-2">{item.taxa_ocupacao.toFixed(1)}%</td>
                            <td className="text-right p-2">
                              R$ {item.receita_total.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
                            </td>
                            <td className="text-right p-2">
                              R$ {item.ticket_medio.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              ) : (
                <p>Nenhum dado de analytics disponível</p>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
```

---

## 8. FRONTEND - DASHBOARD ANALÍTICO

### 8.1 Adicionar Rota no App.tsx

**paineluniversal/frontend/src/App.tsx** (adicionar)
```tsx
import { MEEPDashboard } from '@/components/meep/MEEPDashboard';

// Adicionar na seção de rotas protegidas
<Route path="/meep" element={
  <ProtectedRoute allowedRoles={['admin', 'promoter']}>
    <MEEPDashboard />
  </ProtectedRoute>
} />
```

### 8.2 Adicionar Menu de Navegação

**paineluniversal/frontend/src/components/layout/Sidebar.tsx** (adicionar)
```tsx
import { Activity } from 'lucide-react';

// Adicionar item no menu
{
  label: 'MEEP Analytics',
  icon: Activity,
  href: '/meep',
  roles: ['admin', 'promoter'],
}
```

---

## 9. CAPTURA DE DADOS - SCRIPTS

### 9.1 Script de Captura com Puppeteer

**paineluniversal/meep-capture/capture.js**
```javascript
const puppeteer = require('puppeteer');
const axios = require('axios');
require('dotenv').config();

class MEEPCapture {
  constructor() {
    this.baseUrl = process.env.MEEP_URL || 'https://beta.portal.meep.com.br';
    this.username = process.env.MEEP_USERNAME;
    this.password = process.env.MEEP_PASSWORD;
    this.apiUrl = process.env.API_URL || 'http://localhost:8003/api/meep';
    this.apiToken = process.env.API_TOKEN;
    this.browser = null;
    this.page = null;
  }

  async init() {
    this.browser = await puppeteer.launch({
      headless: true,
      args: ['--no-sandbox', '--disable-setuid-sandbox']
    });
    this.page = await this.browser.newPage();
    await this.page.setViewport({ width: 1920, height: 1080 });
  }

  async login() {
    console.log('Fazendo login no MEEP...');
    await this.page.goto(`${this.baseUrl}/login`, { waitUntil: 'networkidle2' });
    
    // Preencher formulário de login
    await this.page.type('#username', this.username);
    await this.page.type('#password', this.password);
    await this.page.click('#login-button');
    
    // Aguardar redirecionamento
    await this.page.waitForNavigation({ waitUntil: 'networkidle2' });
    console.log('Login realizado com sucesso');
  }

  async captureEventos() {
    console.log('Capturando lista de eventos...');
    await this.page.goto(`${this.baseUrl}/eventos`, { waitUntil: 'networkidle2' });
    
    // Aguardar lista carregar
    await this.page.waitForSelector('.evento-item', { timeout: 10000 });
    
    // Extrair dados dos eventos
    const eventos = await this.page.evaluate(() => {
      const items = document.querySelectorAll('.evento-item');
      return Array.from(items).map(item => ({
        meep_id: item.getAttribute('data-id'),
        nome: item.querySelector('.evento-nome')?.textContent?.trim(),
        data_inicio: item.querySelector('.evento-data-inicio')?.textContent?.trim(),
        local: item.querySelector('.evento-local')?.textContent?.trim(),
        total_inscritos: parseInt(item.querySelector('.total-inscritos')?.textContent?.trim() || '0')
      }));
    });
    
    console.log(`Capturados ${eventos.length} eventos`);
    return eventos;
  }

  async captureEventoDetalhes(meepId) {
    console.log(`Capturando detalhes do evento ${meepId}...`);
    await this.page.goto(`${this.baseUrl}/eventos/${meepId}`, { waitUntil: 'networkidle2' });
    
    // Aguardar página carregar
    await this.page.waitForSelector('.evento-titulo', { timeout: 10000 });
    
    // Extrair detalhes
    const detalhes = await this.page.evaluate(() => {
      return {
        nome: document.querySelector('.evento-titulo')?.textContent?.trim(),
        descricao: document.querySelector('.evento-descricao')?.textContent?.trim(),
        data_inicio: document.querySelector('.data-inicio')?.textContent?.trim(),
        data_fim: document.querySelector('.data-fim')?.textContent?.trim(),
        local: document.querySelector('.local-completo')?.textContent?.trim(),
        cidade: document.querySelector('.cidade')?.textContent?.trim(),
        estado: document.querySelector('.estado')?.textContent?.trim(),
        total_inscritos: parseInt(document.querySelector('.stat-inscritos')?.textContent?.trim() || '0'),
        total_presentes: parseInt(document.querySelector('.stat-presentes')?.textContent?.trim() || '0'),
        total_vendas: parseFloat(
          document.querySelector('.stat-vendas')?.textContent
            ?.replace('R$', '')
            ?.replace('.', '')
            ?.replace(',', '.')
            ?.trim() || '0'
        )
      };
    });
    
    return detalhes;
  }

  async captureParticipantes(meepId) {
    console.log(`Capturando participantes do evento ${meepId}...`);
    const participantes = [];
    let pagina = 1;
    let temMais = true;
    
    while (temMais) {
      await this.page.goto(
        `${this.baseUrl}/eventos/${meepId}/participantes?page=${pagina}`,
        { waitUntil: 'networkidle2' }
      );
      
      // Verificar se há participantes
      const temParticipantes = await this.page.$('.participante-row');
      if (!temParticipantes) {
        temMais = false;
        break;
      }
      
      // Extrair participantes da página
      const participantesPagina = await this.page.evaluate(() => {
        const rows = document.querySelectorAll('.participante-row');
        return Array.from(rows).map(row => ({
          cpf: row.querySelector('.cpf')?.textContent?.trim(),
          nome: row.querySelector('.nome')?.textContent?.trim(),
          email: row.querySelector('.email')?.textContent?.trim(),
          telefone: row.querySelector('.telefone')?.textContent?.trim(),
          status: row.querySelector('.status')?.textContent?.trim(),
          presente: row.classList.contains('presente'),
          valor_pago: parseFloat(
            row.querySelector('.valor-pago')?.textContent
              ?.replace('R$', '')
              ?.replace('.', '')
              ?.replace(',', '.')
              ?.trim() || '0'
          )
        }));
      });
      
      participantes.push(...participantesPagina);
      
      // Verificar se há próxima página
      const proximaPagina = await this.page.$('.pagination .next:not(.disabled)');
      if (!proximaPagina || participantesPagina.length < 50) {
        temMais = false;
      } else {
        pagina++;
      }
    }
    
    console.log(`Capturados ${participantes.length} participantes`);
    return participantes;
  }

  async enviarParaAPI(endpoint, data) {
    try {
      const response = await axios.post(
        `${this.apiUrl}${endpoint}`,
        data,
        {
          headers: {
            'Authorization': `Bearer ${this.apiToken}`,
            'Content-Type': 'application/json'
          }
        }
      );
      return response.data;
    } catch (error) {
      console.error(`Erro ao enviar para API: ${error.message}`);
      throw error;
    }
  }

  async processarCaptura() {
    try {
      await this.init();
      await this.login();
      
      // Capturar eventos
      const eventos = await this.captureEventos();
      
      for (const evento of eventos) {
        // Capturar detalhes
        const detalhes = await this.captureEventoDetalhes(evento.meep_id);
        
        // Enviar para API
        await this.enviarParaAPI('/eventos', {
          ...evento,
          ...detalhes
        });
        
        // Capturar participantes
        const participantes = await this.captureParticipantes(evento.meep_id);
        
        // Enviar participantes em lotes
        const batchSize = 100;
        for (let i = 0; i < participantes.length; i += batchSize) {
          const batch = participantes.slice(i, i + batchSize);
          await this.enviarParaAPI(`/eventos/${evento.meep_id}/participantes`, {
            participantes: batch
          });
        }
        
        // Aguardar um pouco entre eventos para não sobrecarregar
        await new Promise(resolve => setTimeout(resolve, 2000));
      }
      
      console.log('Captura concluída com sucesso');
      
    } catch (error) {
      console.error('Erro na captura:', error);
      throw error;
    } finally {
      if (this.browser) {
        await this.browser.close();
      }
    }
  }
}

// Executar captura
if (require.main === module) {
  const capture = new MEEPCapture();
  capture.processarCaptura()
    .then(() => {
      console.log('Processo finalizado');
      process.exit(0);
    })
    .catch(error => {
      console.error('Erro fatal:', error);
      process.exit(1);
    });
}

module.exports = MEEPCapture;
```

### 9.2 Agendador de Captura

**paineluniversal/meep-capture/scheduler.js**
```javascript
const cron = require('node-cron');
const MEEPCapture = require('./capture');
const winston = require('winston');

// Configurar logger
const logger = winston.createLogger({
  level: 'info',
  format: winston.format.combine(
    winston.format.timestamp(),
    winston.format.json()
  ),
  transports: [
    new winston.transports.File({ filename: 'error.log', level: 'error' }),
    new winston.transports.File({ filename: 'combined.log' }),
    new winston.transports.Console({
      format: winston.format.simple()
    })
  ]
});

// Função para executar captura
async function executarCaptura() {
  logger.info('Iniciando captura agendada');
  const capture = new MEEPCapture();
  
  try {
    await capture.processarCaptura();
    logger.info('Captura concluída com sucesso');
  } catch (error) {
    logger.error('Erro na captura:', error);
  }
}

// Agendar captura a cada 5 minutos
cron.schedule('*/5 * * * *', () => {
  executarCaptura();
});

// Agendar captura completa diária às 2h da manhã
cron.schedule('0 2 * * *', () => {
  logger.info('Executando captura completa diária');
  executarCaptura();
});

logger.info('Agendador MEEP iniciado');
logger.info('Captura a cada 5 minutos');
logger.info('Captura completa diária às 2h');

// Manter processo rodando
process.on('SIGINT', () => {
  logger.info('Encerrando agendador');
  process.exit(0);
});
```

---

## 10. TESTES E VALIDAÇÃO

### 10.1 Testes do Backend

**paineluniversal/backend/tests/test_meep_integration.py**
```python
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import Base, get_db
from app.models.meep_models import MEEPEvento, MEEPParticipante
from datetime import datetime

# Setup de teste
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

class TestMEEPIntegration:
    
    def test_listar_eventos_vazio(self):
        response = client.get("/api/meep/eventos")
        assert response.status_code == 200
        assert response.json() == []
    
    def test_criar_evento_meep(self):
        evento_data = {
            "meep_id": "MEEP001",
            "nome": "Evento Teste",
            "data_inicio": "2024-01-01T10:00:00",
            "data_fim": "2024-01-01T18:00:00",
            "local": "Centro de Convenções",
            "cidade": "São Paulo",
            "estado": "SP"
        }
        
        # Criar via API interna
        db = TestingSessionLocal()
        evento = MEEPEvento(**evento_data)
        db.add(evento)
        db.commit()
        db.close()
        
        # Verificar listagem
        response = client.get("/api/meep/eventos")
        assert response.status_code == 200
        assert len(response.json()) == 1
        assert response.json()[0]["meep_id"] == "MEEP001"
    
    def test_obter_evento_especifico(self):
        response = client.get("/api/meep/eventos/MEEP001")
        assert response.status_code == 200
        assert response.json()["nome"] == "Evento Teste"
    
    def test_sincronizacao(self):
        response = client.post("/api/meep/sync", json={"force": False})
        assert response.status_code == 200
        assert "status" in response.json()
    
    def test_analytics(self):
        response = client.get("/api/meep/analytics?periodo=diario")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

@pytest.fixture(autouse=True)
def cleanup():
    yield
    # Limpar banco após testes
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
```

### 10.2 Script de Teste Manual

**paineluniversal/test_meep_integration.py**
```python
import asyncio
import httpx
from datetime import datetime
import json

async def test_meep_integration():
    """Testa integração MEEP completa"""
    
    base_url = "http://localhost:8003/api"
    
    # 1. Login
    print("1. Fazendo login...")
    async with httpx.AsyncClient() as client:
        login_response = await client.post(
            f"{base_url}/auth/login",
            json={"cpf": "00000000000", "senha": "0000"}
        )
        
        if login_response.status_code != 200:
            print(f"Erro no login: {login_response.text}")
            return
        
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # 2. Listar eventos MEEP
        print("\n2. Listando eventos MEEP...")
        eventos_response = await client.get(
            f"{base_url}/meep/eventos",
            headers=headers
        )
        print(f"Eventos encontrados: {len(eventos_response.json())}")
        
        # 3. Iniciar sincronização
        print("\n3. Iniciando sincronização...")
        sync_response = await client.post(
            f"{base_url}/meep/sync",
            headers=headers,
            json={"force": False}
        )
        print(f"Sincronização: {sync_response.json()}")
        
        # 4. Verificar status
        print("\n4. Verificando status da sincronização...")
        await asyncio.sleep(2)
        status_response = await client.get(
            f"{base_url}/meep/sync/status",
            headers=headers
        )
        print(f"Status: {json.dumps(status_response.json(), indent=2)}")
        
        # 5. Buscar analytics
        print("\n5. Buscando analytics...")
        analytics_response = await client.get(
            f"{base_url}/meep/analytics?periodo=diario",
            headers=headers
        )
        print(f"Analytics: {len(analytics_response.json())} registros")
        
        print("\n✅ Teste concluído com sucesso!")

if __name__ == "__main__":
    asyncio.run(test_meep_integration())
```

---

## 11. DEPLOY E MONITORAMENTO

### 11.1 Docker Compose

**paineluniversal/docker-compose.meep.yml**
```yaml
version: '3.8'

services:
  meep-capture:
    build:
      context: ./meep-capture
      dockerfile: Dockerfile
    environment:
      - MEEP_URL=${MEEP_URL}
      - MEEP_USERNAME=${MEEP_USERNAME}
      - MEEP_PASSWORD=${MEEP_PASSWORD}
      - API_URL=http://backend:8000/api/meep
      - API_TOKEN=${API_TOKEN}
    depends_on:
      - backend
      - redis
    restart: unless-stopped
    
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped

volumes:
  redis_data:
```

### 11.2 Dockerfile para Captura

**paineluniversal/meep-capture/Dockerfile**
```dockerfile
FROM node:18-slim

# Instalar Chromium para Puppeteer
RUN apt-get update && apt-get install -y \
    chromium \
    fonts-liberation \
    libnss3 \
    libxss1 \
    libasound2 \
    && rm -rf /var/lib/apt/lists/*

ENV PUPPETEER_SKIP_CHROMIUM_DOWNLOAD=true
ENV PUPPETEER_EXECUTABLE_PATH=/usr/bin/chromium

WORKDIR /app

COPY package*.json ./
RUN npm ci --only=production

COPY . .

CMD ["node", "scheduler.js"]
```

---

## 12. CHECKLIST FINAL

### ✅ Backend
- [ ] Modelos MEEP criados (`meep_models.py`)
- [ ] Schemas Pydantic definidos (`meep_schemas.py`)
- [ ] Cliente MEEP implementado (`meep_client.py`)
- [ ] Serviço de sincronização (`meep_sync.py`)
- [ ] Rotas da API (`meep_integration.py`)
- [ ] Migrations aplicadas
- [ ] Variáveis de ambiente configuradas
- [ ] Testes unitários escritos

### ✅ Frontend
- [ ] API Client configurado (`meepApi.ts`)
- [ ] Dashboard MEEP implementado (`MEEPDashboard.tsx`)
- [ ] Rotas adicionadas ao App.tsx
- [ ] Menu de navegação atualizado
- [ ] Gráficos e visualizações funcionando
- [ ] Responsividade testada

### ✅ Captura
- [ ] Script Puppeteer configurado
- [ ] Agendador cron implementado
- [ ] Logs configurados
- [ ] Docker configurado
- [ ] Testes de captura realizados

### ✅ Integração
- [ ] Comunicação Backend-Frontend OK
- [ ] Sincronização automática funcionando
- [ ] Webhooks configurados
- [ ] Cache Redis operacional
- [ ] Monitoramento ativo

### ✅ Deploy
- [ ] Docker Compose configurado
- [ ] Variáveis de produção definidas
- [ ] Scripts de deploy criados
- [ ] Backup configurado
- [ ] Documentação completa

---

## 📝 NOTAS IMPORTANTES

1. **Segurança**: Sempre use HTTPS em produção e valide certificados SSL
2. **Rate Limiting**: Implemente limites de requisições para evitar bloqueios
3. **Backup**: Configure backup automático dos dados capturados
4. **Monitoramento**: Use ferramentas como Grafana/Prometheus para acompanhar
5. **Logs**: Centralize logs com ELK Stack ou similar
6. **Testes**: Execute testes antes de cada deploy
7. **Documentação**: Mantenha a documentação atualizada

---

## 🚀 COMANDOS PARA COMEÇAR

```bash
# 1. Backend - Instalar dependências
cd paineluniversal/backend
poetry add httpx beautifulsoup4 lxml pandas numpy scikit-learn celery redis

# 2. Backend - Aplicar migrations
python -c "from app.database import engine; from app.models.meep_models import *; from app.models import Base; Base.metadata.create_all(bind=engine)"

# 3. Frontend - Instalar dependências
cd paineluniversal/frontend
npm install recharts date-fns axios-retry lodash @tanstack/react-query zustand

# 4. Captura - Configurar
cd paineluniversal
mkdir meep-capture && cd meep-capture
npm init -y
npm install puppeteer cheerio axios dotenv node-cron winston

# 5. Iniciar serviços
cd paineluniversal/backend && poetry run uvicorn app.main:app --reload --port 8003 &
cd paineluniversal/frontend && npm run dev &
cd paineluniversal/meep-capture && node scheduler.js &

# 6. Testar integração
cd paineluniversal
python test_meep_integration.py
```

---

**IMPLEMENTAÇÃO CONCLUÍDA! 🎉**

Este roteiro fornece todos os passos necessários para integrar completamente o MEEP ao Painel Universal. Siga cada etapa sequencialmente para garantir uma implementação bem-sucedida.