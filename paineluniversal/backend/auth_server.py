"""
Servidor de autenticação sem banco de dados
Sistema baseado em CPF sem Google Auth
"""
from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext

app = FastAPI(title="Sistema Universal v5 - Autenticação")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configurações
SECRET_KEY = "supersecretkey123"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440  # 24 horas

# Security
security = HTTPBearer()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Modelos
class LoginRequest(BaseModel):
    cpf: str
    senha: str

class Usuario:
    def __init__(self, id, cpf, nome, email, telefone, senha, tipo="cliente"):
        self.id = id
        self.cpf = cpf
        self.nome = nome
        self.email = email
        self.telefone = telefone
        self.senha = senha
        self.tipo = tipo
        self.ativo = True

# Banco de dados em memória
USUARIOS = {
    "00000000000": Usuario(1, "00000000000", "Administrador Sistema", "admin@sistema.com", "11999999999", "0000", "admin"),
    "11111111111": Usuario(2, "11111111111", "Cliente Teste", "cliente@sistema.com", "11888888888", "teste123", "cliente"),
    "22222222222": Usuario(3, "22222222222", "Promoter Teste", "promoter@sistema.com", "11777777777", "promoter123", "promoter"),
}

def verificar_senha(senha_plain: str, senha_armazenada: str) -> bool:
    """Verificação simples de senha"""
    return senha_plain == senha_armazenada

def criar_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Criar token JWT"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def obter_usuario_atual(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Obter usuário do token"""
    token = credentials.credentials
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token inválido",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        cpf: str = payload.get("sub")
        if cpf is None:
            raise credentials_exception
        
        usuario = USUARIOS.get(cpf)
        if usuario is None:
            raise credentials_exception
            
        return usuario
        
    except JWTError:
        raise credentials_exception

# Rotas
@app.get("/")
async def root():
    return {
        "sistema": "Sistema Universal v5 - Servidor de Autenticação",
        "status": "online",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/health")
async def health():
    return {"status": "healthy", "backend": "running", "version": "5.0", "timestamp": datetime.now().isoformat()}

@app.get("/health")
async def health_basic():
    return {"status": "ok", "timestamp": datetime.now().isoformat()}

@app.get("/healthz")
async def healthz():
    return {"status": "ok", "timestamp": datetime.now().isoformat()}

@app.post("/api/auth/login")
async def login(request: LoginRequest):
    """Login sem Google Auth - apenas CPF e senha"""
    print(f"[INFO] Login attempt for CPF: {request.cpf[:3]}***")
    
    # Limpar CPF
    cpf_clean = ''.join(filter(str.isdigit, request.cpf))
    
    # Buscar usuário
    usuario = USUARIOS.get(cpf_clean)
    
    if not usuario:
        print(f"[ERROR] User not found: {cpf_clean}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="CPF ou senha incorretos"
        )
    
    # Verificar senha
    if not verificar_senha(request.senha, usuario.senha):
        print(f"[ERROR] Invalid password for user: {cpf_clean}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="CPF ou senha incorretos"
        )
    
    print(f"[OK] Login successful for: {usuario.nome}")
    
    # Criar token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = criar_access_token(
        data={"sub": usuario.cpf},
        expires_delta=access_token_expires
    )
    
    # Resposta compatível com frontend
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "usuario": {
            "id": usuario.id,
            "cpf": usuario.cpf,
            "nome": usuario.nome,
            "email": usuario.email,
            "telefone": usuario.telefone,
            "tipo": usuario.tipo,
            "tipo_usuario": usuario.tipo,  # Compatibilidade
            "ativo": usuario.ativo
        },
        "user": {  # Compatibilidade adicional
            "id": usuario.id,
            "cpf": usuario.cpf,
            "nome": usuario.nome,
            "email": usuario.email,
            "tipo": usuario.tipo
        }
    }

@app.get("/api/auth/me")
async def get_current_user(usuario = Depends(obter_usuario_atual)):
    """Retorna usuário atual"""
    return {
        "id": usuario.id,
        "cpf": usuario.cpf,
        "nome": usuario.nome,
        "email": usuario.email,
        "telefone": usuario.telefone,
        "tipo": usuario.tipo,
        "tipo_usuario": usuario.tipo,
        "ativo": usuario.ativo
    }

@app.post("/api/auth/verify-token")
async def verify_token(usuario = Depends(obter_usuario_atual)):
    """Verifica token"""
    return {
        "valid": True,
        "user": {
            "id": usuario.id,
            "cpf": usuario.cpf,
            "nome": usuario.nome,
            "tipo": usuario.tipo
        }
    }

@app.get("/api/auth/verify-token")
async def verify_token_get(usuario = Depends(obter_usuario_atual)):
    """Verifica token (GET)"""
    return {
        "valid": True,
        "user": {
            "id": usuario.id,
            "cpf": usuario.cpf,
            "nome": usuario.nome,
            "tipo": usuario.tipo
        }
    }

@app.post("/api/auth/logout")
async def logout():
    """Logout"""
    return {"message": "Logout realizado com sucesso"}

# Endpoints esperados pelo frontend
@app.get("/api/notifications")
async def get_notifications():
    return []

@app.get("/api/notifications/preferencias")
async def get_notification_preferences():
    return {"email": True, "push": False}

@app.get("/api/workspaces")
async def get_workspaces():
    return []

@app.get("/api/workspaces/current")
async def get_current_workspace():
    return {
        "id": 1,
        "name": "Workspace Principal",
        "created": datetime.now().isoformat(),
        "active": True
    }

@app.post("/api/workspaces")
async def create_workspace(data: dict):
    return {
        "id": 1,
        "name": data.get("name", "Workspace"),
        "created": datetime.now().isoformat()
    }

# ========================================
# ENDPOINTS PARA MÓDULOS FUNCIONAIS
# ========================================

# Checkins Endpoints
@app.get("/api/checkins/dashboard/{evento_id}")
async def get_checkins_dashboard(evento_id: int):
    """Dashboard de check-ins para um evento"""
    return {
        "evento_id": evento_id,
        "total_checkins": 150,
        "checkins_hoje": 45,
        "checkins_pendentes": 25,
        "taxa_comparecimento": 85.5,
        "ultima_atualizacao": datetime.now().isoformat()
    }

@app.get("/api/checkins/evento/{evento_id}")
async def get_checkins_evento(evento_id: int):
    """Lista de check-ins de um evento"""
    return {
        "evento_id": evento_id,
        "checkins": [
            {
                "id": 1,
                "participante": "João Silva",
                "cpf": "12345678901",
                "data_checkin": "2025-09-09T08:30:00",
                "status": "confirmado"
            },
            {
                "id": 2,
                "participante": "Maria Santos",
                "cpf": "98765432109", 
                "data_checkin": "2025-09-09T09:15:00",
                "status": "confirmado"
            }
        ],
        "total": 2
    }

# KDS (Kitchen Display System) Endpoints
@app.get("/api/kds/estacoes")
async def get_kds_estacoes():
    """Lista estações do KDS"""
    return [
        {
            "id": 1,
            "nome": "Cozinha Principal",
            "status": "ativa",
            "pedidos_fila": 8,
            "tempo_medio": 12.5
        },
        {
            "id": 2,
            "nome": "Bar",
            "status": "ativa",
            "pedidos_fila": 3,
            "tempo_medio": 5.2
        }
    ]

@app.get("/api/kds/analytics/tempos-preparo")
async def get_kds_analytics():
    """Análises de tempos de preparo do KDS"""
    return {
        "tempo_medio_geral": 10.8,
        "tempo_medio_hoje": 11.2,
        "pedidos_concluidos": 95,
        "pedidos_pendentes": 12,
        "eficiencia": 87.5,
        "estacoes": [
            {"nome": "Cozinha", "tempo_medio": 12.5, "pedidos": 65},
            {"nome": "Bar", "tempo_medio": 5.2, "pedidos": 30}
        ]
    }

# Mesas Endpoints
@app.get("/api/mesas")
async def get_mesas(evento_id: int = None):
    """Lista mesas do evento"""
    return {
        "evento_id": evento_id,
        "mesas": [
            {
                "id": 1,
                "numero": "001",
                "capacidade": 4,
                "status": "ocupada",
                "garcom": "Carlos",
                "conta_total": 150.50
            },
            {
                "id": 2,
                "numero": "002", 
                "capacidade": 6,
                "status": "disponivel",
                "garcom": None,
                "conta_total": 0.0
            }
        ],
        "total": 2
    }

@app.get("/api/mesas/analytics/{evento_id}")
async def get_mesas_analytics(evento_id: int):
    """Analytics das mesas"""
    return {
        "evento_id": evento_id,
        "mesas_ocupadas": 8,
        "mesas_disponiveis": 4,
        "taxa_ocupacao": 66.7,
        "faturamento_total": 2450.75,
        "ticket_medio": 306.34,
        "tempo_medio_permanencia": 85.5
    }

@app.get("/api/mesas/templates")
async def get_mesas_templates():
    """Templates de layout de mesas"""
    return [
        {
            "id": 1,
            "nome": "Layout Padrão",
            "descricao": "Layout tradicional para eventos",
            "mesas": 12,
            "capacidade_total": 48
        },
        {
            "id": 2,
            "nome": "Layout Coquetel",
            "descricao": "Layout para eventos de networking",
            "mesas": 20,
            "capacidade_total": 60
        }
    ]

# Eventos Endpoints Básicos
@app.get("/api/eventos")
async def get_eventos():
    """Lista eventos"""
    # Retornar eventos em memória se houver
    if eventos_db:
        return eventos_db
    
    # Caso contrário, retornar eventos de exemplo
    return [
        {
            "id": 1,
            "nome": "Evento Teste MEEP",
            "data_inicio": "2025-09-15T19:00:00",
            "data_fim": "2025-09-15T23:00:00",
            "local": "Centro de Convenções",
            "status": "ativo",
            "participantes": 150,
            "capacidade": 200
        },
        {
            "id": 2,
            "nome": "Workshop de Tecnologia",
            "data_inicio": "2025-09-20T14:00:00", 
            "data_fim": "2025-09-20T18:00:00",
            "local": "Auditório Tech",
            "status": "planejamento",
            "participantes": 0,
            "capacidade": 100
        }
    ]

@app.get("/api/eventos/{evento_id}")
async def get_evento(evento_id: int):
    """Detalhes de um evento específico"""
    return {
        "id": evento_id,
        "nome": "Evento Teste MEEP",
        "descricao": "Evento de demonstração das funcionalidades do sistema",
        "data_inicio": "2025-09-15T19:00:00",
        "data_fim": "2025-09-15T23:00:00",
        "local": "Centro de Convenções - Sala Principal",
        "endereco": "Rua das Flores, 123 - São Paulo/SP",
        "status": "ativo",
        "participantes_confirmados": 150,
        "capacidade_maxima": 200,
        "organizador": "Sistema Universal",
        "categoria": "Corporativo",
        "preco": 0.0,
        "created_at": "2025-09-01T10:00:00",
        "updated_at": "2025-09-09T08:00:00"
    }

# Lista de eventos em memória
eventos_db = []
evento_id_counter = 3  # Começamos com 3 pois já temos 2 eventos de exemplo

# Vendas em memória
vendas_db = []
venda_id_counter = 1

@app.post("/api/eventos")
async def criar_evento(evento: dict):
    """Criar novo evento"""
    global evento_id_counter
    
    # Criar novo evento com ID único
    novo_evento = {
        "id": evento_id_counter,
        "nome": evento.get("nome", "Evento Sem Nome"),
        "descricao": evento.get("descricao", ""),
        "local": evento.get("local", ""),
        "endereco": evento.get("endereco", ""),
        "data_inicio_evento": evento.get("data_inicio_evento"),
        "data_fim_evento": evento.get("data_fim_evento"),
        "data_inicio_vendas": evento.get("data_inicio_vendas"),
        "data_fim_vendas": evento.get("data_fim_vendas"),
        "data_evento": evento.get("data_evento"),
        "capacidade_maxima": evento.get("capacidade_maxima", 100),
        "limite_idade": evento.get("limite_idade", 18),
        "status": "ativo",
        "participantes": 0,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }
    
    eventos_db.append(novo_evento)
    evento_id_counter += 1
    
    print(f"[OK] Evento criado: {novo_evento['nome']} (ID: {novo_evento['id']})")
    
    return novo_evento

@app.put("/api/eventos/{evento_id}")
async def atualizar_evento(evento_id: int, evento: dict):
    """Atualizar evento existente"""
    for i, ev in enumerate(eventos_db):
        if ev["id"] == evento_id:
            eventos_db[i].update(evento)
            eventos_db[i]["updated_at"] = datetime.now().isoformat()
            print(f"[OK] Evento atualizado: ID {evento_id}")
            return eventos_db[i]
    
    # Se não encontrou, cria novo
    return await criar_evento(evento)

@app.delete("/api/eventos/{evento_id}")
async def deletar_evento(evento_id: int):
    """Deletar evento"""
    global eventos_db
    eventos_db = [ev for ev in eventos_db if ev["id"] != evento_id]
    print(f"[OK] Evento deletado: ID {evento_id}")
    return {"message": "Evento deletado com sucesso"}

# ========================================
# ENDPOINTS DE VENDAS E ESTATÍSTICAS
# ========================================

@app.get("/api/eventos/{evento_id}/estatisticas")
async def get_estatisticas_evento(evento_id: int):
    """Retorna estatísticas do evento"""
    # Calcular estatísticas baseadas nas vendas
    vendas_evento = [v for v in vendas_db if v.get("evento_id") == evento_id]
    
    faturamento = sum(v.get("total", 0) for v in vendas_evento)
    quantidade_vendas = len(vendas_evento)
    ticket_medio = faturamento / quantidade_vendas if quantidade_vendas > 0 else 0
    
    # Contar tipos de ingresso
    entradas_vendidas = sum(
        sum(item.get("quantidade", 0) for item in v.get("itens", []) 
            if item.get("tipo") == "entrada")
        for v in vendas_evento
    )
    
    checkins_realizados = sum(1 for v in vendas_evento if v.get("checkin_realizado"))
    
    return {
        "faturamento": faturamento,
        "ticketMedio": ticket_medio,
        "ticketMedioConsumo": ticket_medio * 0.3,  # Simulação
        "ticketMedioTotal": ticket_medio * 1.3,  # Simulação
        "entradasVendidas": entradas_vendidas,
        "checkinsRealizados": checkins_realizados,
        "vendasTotais": quantidade_vendas
    }

@app.post("/api/eventos/{evento_id}/vendas")
async def criar_venda(evento_id: int, venda: dict):
    """Criar nova venda para o evento"""
    global venda_id_counter
    
    nova_venda = {
        "id": venda_id_counter,
        "evento_id": evento_id,
        "cpf_cliente": venda.get("cpf_cliente"),
        "nome_cliente": venda.get("nome_cliente"),
        "itens": venda.get("itens", []),
        "forma_pagamento": venda.get("forma_pagamento"),
        "total": venda.get("total", 0),
        "checkin_realizado": False,
        "created_at": datetime.now().isoformat()
    }
    
    vendas_db.append(nova_venda)
    venda_id_counter += 1
    
    # Atualizar estatísticas do evento
    for evento in eventos_db:
        if evento["id"] == evento_id:
            evento["vendas_totais"] = evento.get("vendas_totais", 0) + 1
            evento["faturamento"] = f"{float(evento.get('faturamento', '0,00').replace(',', '.')) + nova_venda['total']:.2f}".replace('.', ',')
            
            # Calcular ticket médio
            if evento["vendas_totais"] > 0:
                faturamento_total = float(evento["faturamento"].replace(',', '.'))
                evento["ticket_medio"] = f"{faturamento_total / evento['vendas_totais']:.2f}".replace('.', ',')
            
            # Contar entradas vendidas
            entradas = sum(item.get("quantidade", 0) for item in nova_venda["itens"] if item.get("tipo") == "entrada")
            evento["entradas_vendidas"] = evento.get("entradas_vendidas", 0) + entradas
            evento["total_participantes"] = evento.get("total_participantes", 0) + entradas
            break
    
    print(f"[OK] Venda criada: ID {nova_venda['id']} para evento {evento_id}")
    return nova_venda

@app.get("/api/eventos/{evento_id}/vendas")
async def get_vendas_evento(evento_id: int):
    """Lista vendas do evento"""
    vendas_evento = [v for v in vendas_db if v.get("evento_id") == evento_id]
    return vendas_evento

@app.post("/api/eventos/{evento_id}/checkin/{venda_id}")
async def realizar_checkin(evento_id: int, venda_id: int):
    """Realizar check-in de uma venda"""
    for venda in vendas_db:
        if venda["id"] == venda_id and venda["evento_id"] == evento_id:
            if venda["checkin_realizado"]:
                return {"error": "Check-in já realizado"}, 400
            
            venda["checkin_realizado"] = True
            venda["checkin_at"] = datetime.now().isoformat()
            
            # Atualizar contador de check-ins do evento
            for evento in eventos_db:
                if evento["id"] == evento_id:
                    evento["checkins_realizados"] = evento.get("checkins_realizados", 0) + 1
                    break
            
            print(f"[OK] Check-in realizado: Venda {venda_id} no evento {evento_id}")
            return {"message": "Check-in realizado com sucesso", "venda": venda}
    
    return {"error": "Venda não encontrada"}, 404

# CORS Test Endpoint
@app.get("/api/cors-test")
async def cors_test():
    """Endpoint para teste de CORS"""
    return {
        "status": "CORS funcionando",
        "message": "Requisição cross-origin bem-sucedida",
        "timestamp": datetime.now().isoformat(),
        "server": "auth_server",
        "port": 8001
    }

if __name__ == "__main__":
    import uvicorn
    print("\n" + "="*60)
    print(">>> SISTEMA UNIVERSAL V5 - SERVIDOR DE AUTENTICACAO")
    print("="*60)
    print(">>> Servidor rodando em: http://localhost:8000")
    print(">>> Documentacao: http://localhost:8000/docs")
    print(">>> Usuarios de teste:")
    print("    Admin: CPF: 00000000000, Senha: 0000")
    print("    Cliente: CPF: 11111111111, Senha: teste123")
    print("    Promoter: CPF: 22222222222, Senha: promoter123")
    print("="*60 + "\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8003)# File update trigger
