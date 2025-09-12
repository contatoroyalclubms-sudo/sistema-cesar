"""
MEEP Data Mapper - Normalização e Transformação
Kit Legal - Sem código proprietário
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, date
import re

def map_event(src: Dict[str, Any]) -> Dict[str, Any]:
    """Mapeia evento MEEP para formato interno"""
    return {
        "id": src.get("id"),
        "nome": src.get("name", src.get("title", "")),
        "descricao": src.get("description", ""),
        "data_inicio": parse_datetime(src.get("start_date", src.get("start"))),
        "data_fim": parse_datetime(src.get("end_date", src.get("end"))),
        "local": src.get("location", src.get("venue", "")),
        "capacidade": src.get("capacity", src.get("max_attendees", 0)),
        "tipo": map_event_type(src.get("type", src.get("category"))),
        "status": map_status(src.get("status", "active")),
        "organizador": src.get("organizer", {}).get("name", ""),
        "meta_data": {
            "meep_id": src.get("id"),
            "meep_url": src.get("url"),
            "meep_tags": src.get("tags", []),
            "meep_features": src.get("features", [])
        }
    }

def map_ticket(src: Dict[str, Any]) -> Dict[str, Any]:
    """Mapeia ingresso MEEP para formato interno"""
    return {
        "id": src.get("id"),
        "evento_id": src.get("event_id"),
        "nome": src.get("name", src.get("title")),
        "tipo": map_ticket_type(src.get("type")),
        "preco": float(src.get("price", 0)),
        "quantidade": src.get("quantity", src.get("available", 0)),
        "vendidos": src.get("sold", 0),
        "lote": src.get("batch", src.get("lot", 1)),
        "descricao": src.get("description", ""),
        "beneficios": src.get("benefits", []),
        "restricoes": src.get("restrictions", []),
        "data_inicio_vendas": parse_datetime(src.get("sales_start")),
        "data_fim_vendas": parse_datetime(src.get("sales_end")),
        "meta_data": {
            "meep_id": src.get("id"),
            "meep_sku": src.get("sku"),
            "meep_category": src.get("category")
        }
    }

def map_attendee(src: Dict[str, Any]) -> Dict[str, Any]:
    """Mapeia participante MEEP para formato interno"""
    cpf = extract_cpf(src)
    return {
        "cpf": cpf,
        "nome": src.get("name", src.get("full_name", "")),
        "email": src.get("email", ""),
        "telefone": normalize_phone(src.get("phone", src.get("mobile"))),
        "documento": cpf,  # CPF é o documento principal
        "tipo_documento": "CPF",
        "data_nascimento": parse_date(src.get("birth_date", src.get("dob"))),
        "genero": map_gender(src.get("gender")),
        "endereco": map_address(src.get("address", {})),
        "meta_data": {
            "meep_id": src.get("id"),
            "meep_user_id": src.get("user_id"),
            "meep_tags": src.get("tags", [])
        }
    }

def map_checkin(src: Dict[str, Any]) -> Dict[str, Any]:
    """Mapeia check-in MEEP para formato interno"""
    return {
        "id": src.get("id"),
        "evento_id": src.get("event_id"),
        "participante_cpf": extract_cpf(src.get("attendee", {})),
        "ingresso_id": src.get("ticket_id"),
        "data_hora": parse_datetime(src.get("checked_in_at", src.get("timestamp"))),
        "metodo": map_checkin_method(src.get("method", "qrcode")),
        "portao": src.get("gate", src.get("entrance", "Principal")),
        "operador": src.get("operator", {}).get("name", ""),
        "latitude": src.get("location", {}).get("lat"),
        "longitude": src.get("location", {}).get("lng"),
        "dispositivo": src.get("device", ""),
        "meta_data": {
            "meep_id": src.get("id"),
            "meep_session": src.get("session_id")
        }
    }

def map_transaction(src: Dict[str, Any]) -> Dict[str, Any]:
    """Mapeia transação MEEP para formato interno"""
    return {
        "id": src.get("id"),
        "codigo": src.get("code", src.get("reference")),
        "tipo": map_transaction_type(src.get("type")),
        "valor": float(src.get("amount", 0)),
        "taxa": float(src.get("fee", 0)),
        "valor_liquido": float(src.get("net_amount", src.get("amount", 0) - src.get("fee", 0))),
        "metodo_pagamento": map_payment_method(src.get("payment_method")),
        "status": map_payment_status(src.get("status")),
        "cliente_cpf": extract_cpf(src.get("customer", {})),
        "data_criacao": parse_datetime(src.get("created_at")),
        "data_pagamento": parse_datetime(src.get("paid_at")),
        "parcelas": src.get("installments", 1),
        "gateway": src.get("gateway", ""),
        "gateway_id": src.get("gateway_transaction_id"),
        "meta_data": {
            "meep_id": src.get("id"),
            "meep_order_id": src.get("order_id"),
            "meep_invoice_url": src.get("invoice_url")
        }
    }

def map_analytics(src: Dict[str, Any]) -> Dict[str, Any]:
    """Mapeia analytics MEEP para formato interno"""
    return {
        "evento_id": src.get("event_id"),
        "data": parse_date(src.get("date")),
        "metricas": {
            "vendas_total": src.get("sales", {}).get("total", 0),
            "vendas_hoje": src.get("sales", {}).get("today", 0),
            "receita_total": float(src.get("revenue", {}).get("total", 0)),
            "receita_hoje": float(src.get("revenue", {}).get("today", 0)),
            "checkins_total": src.get("checkins", {}).get("total", 0),
            "checkins_hoje": src.get("checkins", {}).get("today", 0),
            "taxa_conversao": float(src.get("conversion_rate", 0)),
            "ticket_medio": float(src.get("average_ticket", 0)),
            "ocupacao": float(src.get("occupancy_rate", 0))
        },
        "demograficos": {
            "genero": src.get("demographics", {}).get("gender", {}),
            "idade": src.get("demographics", {}).get("age_groups", {}),
            "cidade": src.get("demographics", {}).get("cities", {}),
            "estado": src.get("demographics", {}).get("states", {})
        },
        "canais": src.get("channels", {}),
        "horarios_pico": src.get("peak_hours", []),
        "meta_data": {
            "meep_report_id": src.get("report_id"),
            "meep_generated_at": src.get("generated_at")
        }
    }

# Funções auxiliares de parsing e normalização

def parse_datetime(value: Any) -> Optional[datetime]:
    """Converte string para datetime"""
    if not value:
        return None
    if isinstance(value, datetime):
        return value
    if isinstance(value, str):
        # Tenta diferentes formatos
        formats = [
            "%Y-%m-%dT%H:%M:%S.%fZ",
            "%Y-%m-%dT%H:%M:%SZ",
            "%Y-%m-%d %H:%M:%S",
            "%d/%m/%Y %H:%M:%S",
            "%d/%m/%Y %H:%M"
        ]
        for fmt in formats:
            try:
                return datetime.strptime(value, fmt)
            except ValueError:
                continue
    return None

def parse_date(value: Any) -> Optional[date]:
    """Converte string para date"""
    dt = parse_datetime(value)
    return dt.date() if dt else None

def extract_cpf(data: Dict[str, Any]) -> str:
    """Extrai e normaliza CPF de diferentes campos"""
    cpf = data.get("cpf", data.get("document", data.get("tax_id", "")))
    if isinstance(cpf, str):
        # Remove caracteres não numéricos
        cpf = re.sub(r'\D', '', cpf)
        # Garante 11 dígitos
        if len(cpf) == 11:
            return cpf
    return ""

def normalize_phone(phone: Any) -> str:
    """Normaliza número de telefone"""
    if not phone:
        return ""
    phone = str(phone)
    # Remove caracteres especiais
    phone = re.sub(r'\D', '', phone)
    # Adiciona código do país se necessário
    if len(phone) == 11 and phone[0] in '6789':
        phone = '55' + phone
    elif len(phone) == 10:
        phone = '55' + phone
    return phone

def map_event_type(type_str: Any) -> str:
    """Mapeia tipo de evento"""
    if not type_str:
        return "OUTROS"
    type_str = str(type_str).upper()
    mapping = {
        "CONFERENCE": "CONFERENCIA",
        "WORKSHOP": "WORKSHOP",
        "CONCERT": "SHOW",
        "FESTIVAL": "FESTIVAL",
        "PARTY": "FESTA",
        "CORPORATE": "CORPORATIVO",
        "SPORTS": "ESPORTIVO",
        "FAIR": "FEIRA"
    }
    return mapping.get(type_str, "OUTROS")

def map_ticket_type(type_str: Any) -> str:
    """Mapeia tipo de ingresso"""
    if not type_str:
        return "PAGANTE"
    type_str = str(type_str).upper()
    mapping = {
        "VIP": "VIP",
        "PREMIUM": "VIP",
        "STANDARD": "PAGANTE",
        "FREE": "FREE",
        "PROMOTIONAL": "PROMOCIONAL",
        "STUDENT": "ESTUDANTE",
        "SENIOR": "IDOSO"
    }
    return mapping.get(type_str, "PAGANTE")

def map_status(status: Any) -> str:
    """Mapeia status"""
    if not status:
        return "ATIVO"
    status = str(status).upper()
    mapping = {
        "ACTIVE": "ATIVO",
        "INACTIVE": "INATIVO",
        "DRAFT": "RASCUNHO",
        "PUBLISHED": "PUBLICADO",
        "CANCELLED": "CANCELADO",
        "COMPLETED": "CONCLUIDO",
        "PENDING": "PENDENTE"
    }
    return mapping.get(status, "ATIVO")

def map_gender(gender: Any) -> str:
    """Mapeia gênero"""
    if not gender:
        return "NAO_INFORMADO"
    gender = str(gender).upper()
    mapping = {
        "M": "MASCULINO",
        "MALE": "MASCULINO",
        "MASCULINO": "MASCULINO",
        "F": "FEMININO",
        "FEMALE": "FEMININO",
        "FEMININO": "FEMININO",
        "OTHER": "OUTRO",
        "OUTRO": "OUTRO"
    }
    return mapping.get(gender, "NAO_INFORMADO")

def map_address(addr: Dict[str, Any]) -> Dict[str, Any]:
    """Mapeia endereço"""
    return {
        "logradouro": addr.get("street", addr.get("address", "")),
        "numero": addr.get("number", ""),
        "complemento": addr.get("complement", addr.get("apartment", "")),
        "bairro": addr.get("neighborhood", addr.get("district", "")),
        "cidade": addr.get("city", ""),
        "estado": addr.get("state", addr.get("province", "")),
        "cep": re.sub(r'\D', '', str(addr.get("zip", addr.get("postal_code", ""))))
    }

def map_checkin_method(method: Any) -> str:
    """Mapeia método de check-in"""
    if not method:
        return "MANUAL"
    method = str(method).upper()
    mapping = {
        "QRCODE": "QRCODE",
        "QR": "QRCODE",
        "BARCODE": "CODIGO_BARRAS",
        "NFC": "NFC",
        "MANUAL": "MANUAL",
        "CPF": "CPF",
        "FACIAL": "FACIAL"
    }
    return mapping.get(method, "MANUAL")

def map_transaction_type(type_str: Any) -> str:
    """Mapeia tipo de transação"""
    if not type_str:
        return "VENDA"
    type_str = str(type_str).upper()
    mapping = {
        "SALE": "VENDA",
        "REFUND": "REEMBOLSO",
        "CANCELLATION": "CANCELAMENTO",
        "CHARGEBACK": "CHARGEBACK",
        "ADJUSTMENT": "AJUSTE"
    }
    return mapping.get(type_str, "VENDA")

def map_payment_method(method: Any) -> str:
    """Mapeia método de pagamento"""
    if not method:
        return "DINHEIRO"
    method = str(method).upper()
    mapping = {
        "CASH": "DINHEIRO",
        "CREDIT_CARD": "CARTAO_CREDITO",
        "DEBIT_CARD": "CARTAO_DEBITO",
        "PIX": "PIX",
        "BOLETO": "BOLETO",
        "TRANSFER": "TRANSFERENCIA",
        "VOUCHER": "VOUCHER"
    }
    return mapping.get(method, "OUTROS")

def map_payment_status(status: Any) -> str:
    """Mapeia status de pagamento"""
    if not status:
        return "PENDENTE"
    status = str(status).upper()
    mapping = {
        "PENDING": "PENDENTE",
        "PROCESSING": "PROCESSANDO",
        "PAID": "PAGO",
        "APPROVED": "APROVADO",
        "CANCELLED": "CANCELADO",
        "REFUSED": "RECUSADO",
        "REFUNDED": "REEMBOLSADO",
        "CHARGEBACK": "CHARGEBACK"
    }
    return mapping.get(status, "PENDENTE")

# Funções de mapeamento reverso (interno -> MEEP)

def reverse_map_event(internal: Dict[str, Any]) -> Dict[str, Any]:
    """Mapeia evento interno para formato MEEP"""
    return {
        "name": internal.get("nome"),
        "description": internal.get("descricao"),
        "start_date": internal.get("data_inicio").isoformat() if internal.get("data_inicio") else None,
        "end_date": internal.get("data_fim").isoformat() if internal.get("data_fim") else None,
        "location": internal.get("local"),
        "capacity": internal.get("capacidade"),
        "type": reverse_map_event_type(internal.get("tipo")),
        "status": reverse_map_status(internal.get("status")),
        "organizer": {"name": internal.get("organizador")}
    }

def reverse_map_event_type(type_str: str) -> str:
    """Mapeia tipo de evento interno para MEEP"""
    mapping = {
        "CONFERENCIA": "conference",
        "WORKSHOP": "workshop",
        "SHOW": "concert",
        "FESTIVAL": "festival",
        "FESTA": "party",
        "CORPORATIVO": "corporate",
        "ESPORTIVO": "sports",
        "FEIRA": "fair",
        "OUTROS": "other"
    }
    return mapping.get(type_str, "other")

def reverse_map_status(status: str) -> str:
    """Mapeia status interno para MEEP"""
    mapping = {
        "ATIVO": "active",
        "INATIVO": "inactive",
        "RASCUNHO": "draft",
        "PUBLICADO": "published",
        "CANCELADO": "cancelled",
        "CONCLUIDO": "completed",
        "PENDENTE": "pending"
    }
    return mapping.get(status, "active")

# Validação e sanitização

def validate_cpf(cpf: str) -> bool:
    """Valida CPF brasileiro"""
    if not cpf or len(cpf) != 11:
        return False
    
    # Verifica se todos os dígitos são iguais
    if len(set(cpf)) == 1:
        return False
    
    # CPF de teste 00000000000 é válido para testes
    if cpf == "00000000000":
        return True
    
    try:
        # Cálculo do primeiro dígito verificador
        sum_1 = sum(int(cpf[i]) * (10 - i) for i in range(9))
        digit_1 = (sum_1 * 10) % 11
        if digit_1 == 10:
            digit_1 = 0
        
        if int(cpf[9]) != digit_1:
            return False
        
        # Cálculo do segundo dígito verificador
        sum_2 = sum(int(cpf[i]) * (11 - i) for i in range(10))
        digit_2 = (sum_2 * 10) % 11
        if digit_2 == 10:
            digit_2 = 0
        
        return int(cpf[10]) == digit_2
    except (ValueError, IndexError):
        return False

def sanitize_string(value: Any, max_length: int = 255) -> str:
    """Sanitiza string removendo caracteres perigosos"""
    if not value:
        return ""
    value = str(value)
    # Remove caracteres de controle
    value = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', value)
    # Limita tamanho
    return value[:max_length].strip()

def batch_map(items: List[Dict[str, Any]], map_func: callable) -> List[Dict[str, Any]]:
    """Mapeia lista de items"""
    return [map_func(item) for item in items if item]