"""
🛡️ VALIDADORES SEM CACHE - VERSÃO TEMPORÁRIA PARA TESTES
"""

import re
from typing import Optional
from datetime import datetime, date
from decimal import Decimal
from email_validator import validate_email, EmailNotValidError
from fastapi import HTTPException, status

# ===== VALIDADORES DE DOCUMENTOS =====

def validar_cpf(cpf: str, raise_error: bool = True) -> Optional[str]:
    """
    Valida CPF brasileiro SEM cache
    """
    if not cpf:
        if raise_error:
            raise ValueError('CPF é obrigatório')
        return None
    
    # Remove caracteres não numéricos
    cpf_limpo = re.sub(r'\D', '', cpf)
    
    # Verifica se tem 11 dígitos
    if len(cpf_limpo) != 11:
        if raise_error:
            raise ValueError(f'CPF deve ter 11 dígitos. Recebido: {len(cpf_limpo)}')
        return None
    
    # Verifica se todos os dígitos são iguais
    if len(set(cpf_limpo)) == 1:
        if raise_error:
            raise ValueError('CPF inválido: todos os dígitos são iguais')
        return None
    
    # Calcula o primeiro dígito verificador
    soma = sum(int(cpf_limpo[i]) * (10 - i) for i in range(9))
    resto = soma % 11
    digito1 = 0 if resto < 2 else 11 - resto
    
    # Calcula o segundo dígito verificador
    soma = sum(int(cpf_limpo[i]) * (11 - i) for i in range(10))
    resto = soma % 11
    digito2 = 0 if resto < 2 else 11 - resto
    
    # Verifica se os dígitos verificadores estão corretos
    if not (int(cpf_limpo[9]) == digito1 and int(cpf_limpo[10]) == digito2):
        if raise_error:
            raise ValueError('CPF inválido: dígitos verificadores incorretos')
        return None
    
    # CPF válido - retorna formatado
    formatted = f"{cpf_limpo[:3]}.{cpf_limpo[3:6]}.{cpf_limpo[6:9]}-{cpf_limpo[9:]}"
    return formatted


def validar_cnpj(cnpj: str, raise_error: bool = True) -> Optional[str]:
    """
    Valida CNPJ brasileiro SEM cache
    """
    if not cnpj:
        if raise_error:
            raise ValueError('CNPJ é obrigatório')
        return None
    
    # Remove caracteres não numéricos
    cnpj_limpo = re.sub(r'\D', '', cnpj)
    
    # Verifica se tem 14 dígitos
    if len(cnpj_limpo) != 14:
        if raise_error:
            raise ValueError(f'CNPJ deve ter 14 dígitos. Recebido: {len(cnpj_limpo)}')
        return None
    
    # Verifica se todos os dígitos são iguais
    if len(set(cnpj_limpo)) == 1:
        if raise_error:
            raise ValueError('CNPJ inválido: todos os dígitos são iguais')
        return None
    
    # Calcula o primeiro dígito verificador
    multiplicadores1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    soma = sum(int(cnpj_limpo[i]) * multiplicadores1[i] for i in range(12))
    resto = soma % 11
    digito1 = 0 if resto < 2 else 11 - resto
    
    # Calcula o segundo dígito verificador
    multiplicadores2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    soma = sum(int(cnpj_limpo[i]) * multiplicadores2[i] for i in range(13))
    resto = soma % 11
    digito2 = 0 if resto < 2 else 11 - resto
    
    # Verifica se os dígitos verificadores estão corretos
    if not (int(cnpj_limpo[12]) == digito1 and int(cnpj_limpo[13]) == digito2):
        if raise_error:
            raise ValueError('CNPJ inválido: dígitos verificadores incorretos')
        return None
    
    # CNPJ válido - retorna formatado
    formatted = f"{cnpj_limpo[:2]}.{cnpj_limpo[2:5]}.{cnpj_limpo[5:8]}/{cnpj_limpo[8:12]}-{cnpj_limpo[12:]}"
    return formatted


# ===== VALIDADORES DE TIPOS DE DADOS =====

def validar_email(email: str, raise_error: bool = True) -> Optional[str]:
    """Valida email"""
    if not email:
        if raise_error:
            raise ValueError('Email é obrigatório')
        return None
    
    try:
        # Usa a biblioteca email-validator
        validation = validate_email(email)
        return validation.email
    except EmailNotValidError as e:
        if raise_error:
            raise ValueError(f'Email inválido: {str(e)}')
        return None


def validar_telefone(telefone: str, raise_error: bool = True) -> Optional[str]:
    """Valida telefone brasileiro"""
    if not telefone:
        return None
    
    # Remove caracteres não numéricos
    tel_limpo = re.sub(r'\D', '', telefone)
    
    # Verifica se tem 10 ou 11 dígitos (com DDD)
    if len(tel_limpo) < 10 or len(tel_limpo) > 11:
        if raise_error:
            raise ValueError(f'Telefone deve ter 10 ou 11 dígitos. Recebido: {len(tel_limpo)}')
        return None
    
    # Formata o telefone
    if len(tel_limpo) == 10:
        formatted = f"({tel_limpo[:2]}) {tel_limpo[2:6]}-{tel_limpo[6:]}"
    else:
        formatted = f"({tel_limpo[:2]}) {tel_limpo[2:7]}-{tel_limpo[7:]}"
    
    return formatted


def validar_cep(cep: str, raise_error: bool = True) -> Optional[str]:
    """Valida CEP brasileiro"""
    if not cep:
        return None
    
    # Remove caracteres não numéricos
    cep_limpo = re.sub(r'\D', '', cep)
    
    # Verifica se tem 8 dígitos
    if len(cep_limpo) != 8:
        if raise_error:
            raise ValueError(f'CEP deve ter 8 dígitos. Recebido: {len(cep_limpo)}')
        return None
    
    # Formata o CEP
    formatted = f"{cep_limpo[:5]}-{cep_limpo[5:]}"
    return formatted


def validar_data(data: str, formato: str = '%d/%m/%Y', raise_error: bool = True) -> Optional[date]:
    """Valida e converte data"""
    if not data:
        return None
    
    try:
        if isinstance(data, date):
            return data
        
        dt = datetime.strptime(data, formato)
        return dt.date()
    except (ValueError, TypeError) as e:
        if raise_error:
            raise ValueError(f'Data inválida: {data}. Formato esperado: {formato}')
        return None


def validar_valor(valor: any, min_valor: float = 0, max_valor: float = None, raise_error: bool = True) -> Optional[Decimal]:
    """Valida valor monetário"""
    if valor is None:
        return None
    
    try:
        # Converte para Decimal
        if isinstance(valor, str):
            # Remove símbolos monetários
            valor_limpo = re.sub(r'[R$\s.]', '', valor).replace(',', '.')
            valor_decimal = Decimal(valor_limpo)
        else:
            valor_decimal = Decimal(str(valor))
        
        # Valida intervalo
        if valor_decimal < min_valor:
            if raise_error:
                raise ValueError(f'Valor deve ser maior ou igual a {min_valor}')
            return None
        
        if max_valor is not None and valor_decimal > max_valor:
            if raise_error:
                raise ValueError(f'Valor deve ser menor ou igual a {max_valor}')
            return None
        
        return valor_decimal
        
    except (ValueError, TypeError, InvalidOperation) as e:
        if raise_error:
            raise ValueError(f'Valor inválido: {valor}')
        return None


# ===== VALIDADORES DE NEGÓCIO =====

def validar_senha(senha: str, min_length: int = 6, raise_error: bool = True) -> bool:
    """Valida força da senha"""
    if not senha:
        if raise_error:
            raise ValueError('Senha é obrigatória')
        return False
    
    if len(senha) < min_length:
        if raise_error:
            raise ValueError(f'Senha deve ter no mínimo {min_length} caracteres')
        return False
    
    return True


def validar_idade(data_nascimento: date, idade_minima: int = 18, raise_error: bool = True) -> bool:
    """Valida se pessoa tem idade mínima"""
    if not data_nascimento:
        if raise_error:
            raise ValueError('Data de nascimento é obrigatória')
        return False
    
    hoje = date.today()
    idade = hoje.year - data_nascimento.year
    
    # Ajusta se ainda não fez aniversário este ano
    if hoje.month < data_nascimento.month or (hoje.month == data_nascimento.month and hoje.day < data_nascimento.day):
        idade -= 1
    
    if idade < idade_minima:
        if raise_error:
            raise ValueError(f'Idade mínima é {idade_minima} anos')
        return False
    
    return True


# ===== FUNÇÕES AUXILIARES =====

def limpar_string(texto: str) -> str:
    """Remove espaços extras e normaliza string"""
    if not texto:
        return ""
    return " ".join(texto.split())


def normalizar_nome(nome: str) -> str:
    """Normaliza nome próprio"""
    if not nome:
        return ""
    
    # Limpa e capitaliza
    palavras = nome.strip().split()
    palavras_normalizadas = []
    
    preposicoes = ['de', 'da', 'do', 'das', 'dos', 'e']
    
    for palavra in palavras:
        if palavra.lower() in preposicoes:
            palavras_normalizadas.append(palavra.lower())
        else:
            palavras_normalizadas.append(palavra.capitalize())
    
    return " ".join(palavras_normalizadas)


# ===== VALIDADOR HTTP =====

def validar_request(data: dict, campos_obrigatorios: list, raise_error: bool = True) -> bool:
    """Valida se request contém campos obrigatórios"""
    campos_faltando = []
    
    for campo in campos_obrigatorios:
        if campo not in data or data[campo] is None or data[campo] == "":
            campos_faltando.append(campo)
    
    if campos_faltando:
        if raise_error:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Campos obrigatórios faltando: {', '.join(campos_faltando)}"
            )
        return False
    
    return True


# Import de InvalidOperation que estava faltando
try:
    from decimal import InvalidOperation
except ImportError:
    InvalidOperation = ValueError