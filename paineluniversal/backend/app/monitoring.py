"""
📊 SISTEMA DE OBSERVABILIDADE E MÉTRICAS
Monitoramento completo com Prometheus, traces e health checks
Última atualização: 05/01/2025
"""

import time
import psutil
import logging
import json
from typing import Optional, Dict, Any, List, Callable
from datetime import datetime, timedelta
from contextlib import asynccontextmanager
from functools import wraps
import asyncio
import os

from fastapi import Request, Response, HTTPException, status
from fastapi.responses import JSONResponse, PlainTextResponse
from prometheus_client import (
    Counter, Histogram, Gauge, Summary, Info,
    generate_latest, CONTENT_TYPE_LATEST,
    CollectorRegistry, push_to_gateway
)
from opentelemetry import trace, metrics
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor

# Import cache se disponível
try:
    from app.cache import cache, get_cache_metrics
    CACHE_ENABLED = True
except ImportError:
    CACHE_ENABLED = False

logger = logging.getLogger(__name__)

# ===== CONFIGURAÇÃO DO PROMETHEUS =====

# Registry customizado para isolar métricas
registry = CollectorRegistry()

# Contadores
http_requests_total = Counter(
    'http_requests_total',
    'Total de requisições HTTP',
    ['method', 'endpoint', 'status'],
    registry=registry
)

http_errors_total = Counter(
    'http_errors_total',
    'Total de erros HTTP',
    ['method', 'endpoint', 'status'],
    registry=registry
)

business_operations_total = Counter(
    'business_operations_total',
    'Total de operações de negócio',
    ['operation', 'status'],
    registry=registry
)

# Histogramas
http_request_duration_seconds = Histogram(
    'http_request_duration_seconds',
    'Duração das requisições HTTP em segundos',
    ['method', 'endpoint'],
    buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5, 10),
    registry=registry
)

db_query_duration_seconds = Histogram(
    'db_query_duration_seconds',
    'Duração das queries do banco em segundos',
    ['operation', 'table'],
    buckets=(0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1, 5),
    registry=registry
)

# Gauges
active_connections = Gauge(
    'active_connections',
    'Número de conexões ativas',
    ['type'],
    registry=registry
)

memory_usage_bytes = Gauge(
    'memory_usage_bytes',
    'Uso de memória em bytes',
    ['type'],
    registry=registry
)

cpu_usage_percent = Gauge(
    'cpu_usage_percent',
    'Uso de CPU em porcentagem',
    registry=registry
)

# Summaries
api_response_size_bytes = Summary(
    'api_response_size_bytes',
    'Tamanho das respostas da API em bytes',
    ['endpoint'],
    registry=registry
)

# Info
app_info = Info(
    'app',
    'Informações da aplicação',
    registry=registry
)

# ===== COLETOR DE MÉTRICAS DO SISTEMA =====

class SystemMetricsCollector:
    """Coleta métricas do sistema operacional"""
    
    def __init__(self):
        self.process = psutil.Process()
        self.last_collection = None
        self.collection_interval = 30  # segundos
    
    def collect(self):
        """Coleta métricas do sistema"""
        try:
            # CPU
            cpu_usage_percent.set(psutil.cpu_percent(interval=1))
            
            # Memória
            memory = psutil.virtual_memory()
            memory_usage_bytes.labels(type='total').set(memory.total)
            memory_usage_bytes.labels(type='used').set(memory.used)
            memory_usage_bytes.labels(type='available').set(memory.available)
            memory_usage_bytes.labels(type='percent').set(memory.percent)
            
            # Processo
            process_memory = self.process.memory_info()
            memory_usage_bytes.labels(type='process_rss').set(process_memory.rss)
            memory_usage_bytes.labels(type='process_vms').set(process_memory.vms)
            
            # Disco
            disk = psutil.disk_usage('/')
            memory_usage_bytes.labels(type='disk_total').set(disk.total)
            memory_usage_bytes.labels(type='disk_used').set(disk.used)
            memory_usage_bytes.labels(type='disk_free').set(disk.free)
            
            # Conexões de rede
            connections = len(self.process.connections())
            active_connections.labels(type='process').set(connections)
            
            self.last_collection = datetime.now()
            
        except Exception as e:
            logger.error(f"Erro ao coletar métricas do sistema: {e}")
    
    def should_collect(self) -> bool:
        """Verifica se deve coletar métricas"""
        if not self.last_collection:
            return True
        
        elapsed = (datetime.now() - self.last_collection).total_seconds()
        return elapsed >= self.collection_interval

# ===== MIDDLEWARE DE MÉTRICAS =====

class MetricsMiddleware:
    """Middleware para coletar métricas de requisições"""
    
    def __init__(self, app):
        self.app = app
        self.system_collector = SystemMetricsCollector()
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        request = Request(scope, receive=receive)
        method = request.method
        path = request.url.path
        
        # Ignorar endpoints de métricas
        if path in ["/metrics", "/health", "/ready"]:
            await self.app(scope, receive, send)
            return
        
        # Normalizar path (remover IDs)
        endpoint = self._normalize_path(path)
        
        # Incrementar conexões ativas
        active_connections.labels(type='http').inc()
        
        # Medir tempo
        start_time = time.time()
        
        # Variáveis para capturar resposta
        status_code = 500
        response_size = 0
        
        async def send_wrapper(message):
            nonlocal status_code, response_size
            
            if message["type"] == "http.response.start":
                status_code = message.get("status", 500)
            elif message["type"] == "http.response.body":
                body = message.get("body", b"")
                response_size += len(body)
            
            await send(message)
        
        try:
            # Processar requisição
            await self.app(scope, receive, send_wrapper)
            
        except Exception as e:
            # Registrar erro
            http_errors_total.labels(
                method=method,
                endpoint=endpoint,
                status=status_code
            ).inc()
            raise
        
        finally:
            # Calcular duração
            duration = time.time() - start_time
            
            # Registrar métricas
            http_requests_total.labels(
                method=method,
                endpoint=endpoint,
                status=status_code
            ).inc()
            
            http_request_duration_seconds.labels(
                method=method,
                endpoint=endpoint
            ).observe(duration)
            
            if response_size > 0:
                api_response_size_bytes.labels(
                    endpoint=endpoint
                ).observe(response_size)
            
            # Decrementar conexões ativas
            active_connections.labels(type='http').dec()
            
            # Coletar métricas do sistema periodicamente
            if self.system_collector.should_collect():
                self.system_collector.collect()
            
            # Log de métricas
            logger.debug(
                f"Request metrics - {method} {endpoint}: "
                f"status={status_code}, duration={duration:.3f}s, size={response_size}B"
            )
    
    def _normalize_path(self, path: str) -> str:
        """Normaliza path removendo IDs para agregação"""
        import re
        
        # Remover UUIDs
        path = re.sub(r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}', '{id}', path)
        
        # Remover números (IDs)
        path = re.sub(r'/\d+', '/{id}', path)
        
        return path

# ===== OPENTELEMETRY TRACING =====

class TracingService:
    """Serviço de distributed tracing"""
    
    def __init__(self):
        self.enabled = os.getenv("TRACING_ENABLED", "false").lower() == "true"
        self.endpoint = os.getenv("OTLP_ENDPOINT", "localhost:4317")
        self.service_name = os.getenv("SERVICE_NAME", "painel-universal")
        
        if self.enabled:
            self._setup_tracing()
    
    def _setup_tracing(self):
        """Configura OpenTelemetry tracing"""
        try:
            # Configurar provider
            trace.set_tracer_provider(TracerProvider())
            tracer_provider = trace.get_tracer_provider()
            
            # Configurar exporter
            otlp_exporter = OTLPSpanExporter(
                endpoint=self.endpoint,
                insecure=True
            )
            
            # Adicionar processor
            span_processor = BatchSpanProcessor(otlp_exporter)
            tracer_provider.add_span_processor(span_processor)
            
            # Instrumentar FastAPI
            FastAPIInstrumentor.instrument(
                service_name=self.service_name,
                span_details_callback=self._span_details_callback
            )
            
            # Instrumentar SQLAlchemy
            SQLAlchemyInstrumentor().instrument(
                service_name=f"{self.service_name}-db"
            )
            
            logger.info(f"✅ Tracing configurado: {self.endpoint}")
            
        except Exception as e:
            logger.error(f"Erro ao configurar tracing: {e}")
            self.enabled = False
    
    def _span_details_callback(self, span, request):
        """Adiciona detalhes customizados ao span"""
        if request:
            # Adicionar user_id se disponível
            if hasattr(request.state, "user"):
                span.set_attribute("user.id", request.state.user.get("id"))
                span.set_attribute("user.role", request.state.user.get("role"))
            
            # Adicionar headers úteis
            span.set_attribute("http.user_agent", request.headers.get("User-Agent", ""))
            span.set_attribute("http.x_forwarded_for", request.headers.get("X-Forwarded-For", ""))
    
    def create_span(self, name: str, attributes: Optional[Dict[str, Any]] = None):
        """Cria um span customizado"""
        if not self.enabled:
            return None
        
        tracer = trace.get_tracer(self.service_name)
        span = tracer.start_span(name)
        
        if attributes:
            for key, value in attributes.items():
                span.set_attribute(key, str(value))
        
        return span

# Instância global do tracing
tracing = TracingService()

# ===== DECORATORS PARA MÉTRICAS =====

def track_operation(operation_name: str):
    """
    Decorator para rastrear operações de negócio
    
    Exemplo:
        @track_operation("criar_evento")
        async def criar_evento(...):
            ...
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            status = "success"
            span = None
            
            try:
                # Criar span se tracing habilitado
                if tracing.enabled:
                    span = tracing.create_span(
                        f"operation.{operation_name}",
                        {"operation": operation_name}
                    )
                
                # Executar função
                result = await func(*args, **kwargs) if asyncio.iscoroutinefunction(func) else func(*args, **kwargs)
                
                return result
                
            except Exception as e:
                status = "error"
                if span:
                    span.set_attribute("error", True)
                    span.set_attribute("error.message", str(e))
                raise
                
            finally:
                # Registrar métrica
                business_operations_total.labels(
                    operation=operation_name,
                    status=status
                ).inc()
                
                # Fechar span
                if span:
                    span.end()
                
                # Log
                duration = time.time() - start_time
                logger.debug(f"Operation {operation_name}: status={status}, duration={duration:.3f}s")
        
        return wrapper
    return decorator

def track_db_operation(table: str, operation: str):
    """
    Decorator para rastrear operações do banco
    
    Exemplo:
        @track_db_operation("eventos", "select")
        async def buscar_eventos(...):
            ...
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            
            try:
                result = await func(*args, **kwargs) if asyncio.iscoroutinefunction(func) else func(*args, **kwargs)
                return result
                
            finally:
                duration = time.time() - start_time
                db_query_duration_seconds.labels(
                    operation=operation,
                    table=table
                ).observe(duration)
        
        return wrapper
    return decorator

# ===== HEALTH CHECKS =====

class HealthCheck:
    """Sistema de health checks"""
    
    def __init__(self):
        self.checks = {}
        self.last_check_time = {}
        self.check_results = {}
    
    def register_check(self, name: str, check_func: Callable, critical: bool = False):
        """
        Registra um health check
        
        Args:
            name: Nome do check
            check_func: Função que retorna (healthy: bool, details: dict)
            critical: Se o check é crítico para o funcionamento
        """
        self.checks[name] = {
            "func": check_func,
            "critical": critical
        }
    
    async def run_checks(self) -> Dict[str, Any]:
        """Executa todos os health checks"""
        results = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "checks": {}
        }
        
        has_critical_failure = False
        
        for name, check in self.checks.items():
            try:
                # Executar check
                if asyncio.iscoroutinefunction(check["func"]):
                    healthy, details = await check["func"]()
                else:
                    healthy, details = check["func"]()
                
                # Registrar resultado
                self.check_results[name] = {
                    "healthy": healthy,
                    "details": details,
                    "last_check": datetime.now()
                }
                
                results["checks"][name] = {
                    "status": "healthy" if healthy else "unhealthy",
                    "critical": check["critical"],
                    **details
                }
                
                # Verificar falha crítica
                if not healthy and check["critical"]:
                    has_critical_failure = True
                    
            except Exception as e:
                results["checks"][name] = {
                    "status": "error",
                    "critical": check["critical"],
                    "error": str(e)
                }
                
                if check["critical"]:
                    has_critical_failure = True
        
        # Status geral
        if has_critical_failure:
            results["status"] = "unhealthy"
        elif any(not c.get("healthy", True) for c in results["checks"].values()):
            results["status"] = "degraded"
        
        return results
    
    def get_readiness(self) -> Dict[str, Any]:
        """Verifica se o serviço está pronto para receber tráfego"""
        # Verificar apenas checks críticos
        critical_checks = {
            name: result 
            for name, result in self.check_results.items() 
            if self.checks[name]["critical"]
        }
        
        all_healthy = all(
            check.get("healthy", False) 
            for check in critical_checks.values()
        )
        
        return {
            "ready": all_healthy,
            "timestamp": datetime.now().isoformat(),
            "checks": critical_checks
        }
    
    def get_liveness(self) -> Dict[str, Any]:
        """Verifica se o serviço está vivo"""
        return {
            "alive": True,
            "timestamp": datetime.now().isoformat(),
            "uptime": self._get_uptime()
        }
    
    def _get_uptime(self) -> str:
        """Calcula uptime do processo"""
        try:
            process = psutil.Process()
            create_time = datetime.fromtimestamp(process.create_time())
            uptime = datetime.now() - create_time
            
            days = uptime.days
            hours, remainder = divmod(uptime.seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            
            return f"{days}d {hours}h {minutes}m {seconds}s"
            
        except Exception:
            return "unknown"

# Instância global do health check
health_check = HealthCheck()

# ===== CHECKS PADRÃO =====

def database_check():
    """Check de conectividade com o banco"""
    try:
        from app.database import engine
        from sqlalchemy import text
        
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            return True, {"response_time_ms": 0}
            
    except Exception as e:
        return False, {"error": str(e)}

def cache_check():
    """Check de conectividade com o cache"""
    if not CACHE_ENABLED:
        return True, {"status": "disabled"}
    
    try:
        metrics = get_cache_metrics()
        return metrics.get("connected", False), metrics
        
    except Exception as e:
        return False, {"error": str(e)}

def disk_space_check():
    """Check de espaço em disco"""
    try:
        disk = psutil.disk_usage('/')
        free_gb = disk.free / (1024 ** 3)
        
        healthy = free_gb > 1  # Mínimo 1GB livre
        
        return healthy, {
            "free_gb": round(free_gb, 2),
            "used_percent": disk.percent
        }
        
    except Exception as e:
        return False, {"error": str(e)}

def memory_check():
    """Check de memória disponível"""
    try:
        memory = psutil.virtual_memory()
        available_gb = memory.available / (1024 ** 3)
        
        healthy = memory.percent < 90  # Máximo 90% de uso
        
        return healthy, {
            "available_gb": round(available_gb, 2),
            "used_percent": memory.percent
        }
        
    except Exception as e:
        return False, {"error": str(e)}

# Registrar checks padrão
health_check.register_check("database", database_check, critical=True)
health_check.register_check("cache", cache_check, critical=False)
health_check.register_check("disk_space", disk_space_check, critical=False)
health_check.register_check("memory", memory_check, critical=False)

# ===== ENDPOINTS DE MONITORAMENTO =====

async def metrics_endpoint(request: Request) -> Response:
    """Endpoint para métricas Prometheus"""
    # Coletar métricas do sistema
    system_collector = SystemMetricsCollector()
    system_collector.collect()
    
    # Gerar métricas
    metrics_data = generate_latest(registry)
    
    return Response(
        content=metrics_data,
        media_type=CONTENT_TYPE_LATEST
    )

async def health_endpoint(request: Request) -> JSONResponse:
    """Endpoint de health check completo"""
    results = await health_check.run_checks()
    
    status_code = 200 if results["status"] == "healthy" else 503
    
    return JSONResponse(
        status_code=status_code,
        content=results
    )

async def ready_endpoint(request: Request) -> JSONResponse:
    """Endpoint de readiness (pronto para tráfego)"""
    results = health_check.get_readiness()
    
    status_code = 200 if results["ready"] else 503
    
    return JSONResponse(
        status_code=status_code,
        content=results
    )

async def live_endpoint(request: Request) -> PlainTextResponse:
    """Endpoint de liveness (processo vivo)"""
    results = health_check.get_liveness()
    
    return PlainTextResponse(
        status_code=200,
        content="OK"
    )

# ===== DASHBOARD DE MÉTRICAS =====

async def metrics_dashboard(request: Request) -> JSONResponse:
    """Dashboard JSON com métricas consolidadas"""
    try:
        # Coletar métricas do sistema
        process = psutil.Process()
        
        dashboard = {
            "timestamp": datetime.now().isoformat(),
            "system": {
                "cpu_percent": psutil.cpu_percent(interval=1),
                "memory": {
                    "total_gb": round(psutil.virtual_memory().total / (1024**3), 2),
                    "used_gb": round(psutil.virtual_memory().used / (1024**3), 2),
                    "percent": psutil.virtual_memory().percent
                },
                "disk": {
                    "total_gb": round(psutil.disk_usage('/').total / (1024**3), 2),
                    "used_gb": round(psutil.disk_usage('/').used / (1024**3), 2),
                    "percent": psutil.disk_usage('/').percent
                },
                "network_connections": len(process.connections()),
                "uptime": health_check._get_uptime()
            },
            "application": {
                "version": app_info._value.get("version", "unknown"),
                "environment": os.getenv("ENV", "development")
            },
            "health": await health_check.run_checks()
        }
        
        # Adicionar métricas de cache se disponível
        if CACHE_ENABLED:
            dashboard["cache"] = get_cache_metrics()
        
        return JSONResponse(content=dashboard)
        
    except Exception as e:
        logger.error(f"Erro ao gerar dashboard: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )

# ===== CONFIGURAÇÃO PARA FASTAPI =====

def setup_monitoring(app):
    """
    Configura monitoramento no app FastAPI
    
    Args:
        app: Instância do FastAPI
    """
    # Adicionar middleware de métricas
    app.add_middleware(MetricsMiddleware)
    
    # Adicionar endpoints
    app.add_api_route("/metrics", metrics_endpoint, methods=["GET"], include_in_schema=False)
    app.add_api_route("/health", health_endpoint, methods=["GET"], tags=["Monitoring"])
    app.add_api_route("/ready", ready_endpoint, methods=["GET"], include_in_schema=False)
    app.add_api_route("/live", live_endpoint, methods=["GET"], include_in_schema=False)
    app.add_api_route("/dashboard/metrics", metrics_dashboard, methods=["GET"], tags=["Monitoring"])
    
    # Configurar info da aplicação
    app_info.info({
        "version": "2.0.0",
        "name": "painel-universal",
        "environment": os.getenv("ENV", "development"),
        "started": datetime.now().isoformat()
    })
    
    logger.info("✅ Sistema de monitoramento configurado")

# Exportar componentes principais
__all__ = [
    'MetricsMiddleware',
    'TracingService',
    'HealthCheck',
    'SystemMetricsCollector',
    'track_operation',
    'track_db_operation',
    'health_check',
    'tracing',
    'setup_monitoring',
    'http_requests_total',
    'http_request_duration_seconds',
    'business_operations_total'
]