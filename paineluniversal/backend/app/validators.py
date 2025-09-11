"""
🛡️ VALIDADORES CENTRALIZADOS - BACKEND
Sistema completo de validação de dados
Última atualização: 05/01/2025
"""

import re
from typing import Optional, Union, Any, Dict, List
from datetime import datetime, date
from decimal import Decimal
from email_validator import validate_email, EmailNotValidError
from fastapi import HTTPException, status

# Import cache apenas se disponível
import os
if os.getenv("DISABLE_REDIS", "true").lower() == "true":
    CACHE_ENABLED = False
    ValidationCache = None
    cache = None
else:
    try:
        from app.cache import ValidationCache, cache
        CACHE_ENABLED = True
    except (ImportError, Exception):
        CACHE_ENABLED = False
        ValidationCache = None
        cache = None

# ===== VALIDADORES DE DOCUMENTOS =====

def validar_cpf(cpf: str, raise_error: bool = True) -> Optional[str]:
    """
    Valida CPF brasileiro com cache
    
    Args:
        cpf: String com o CPF
        raise_error: Se True, lança exceção em caso de erro
    
    Returns:
        CPF limpo (apenas números) se válido, None se inválido
    """
    # Remover caracteres não numéricos
    cpf_limpo = re.sub(r'\D', '', str(cpf))
    
    # Verificar cache primeiro se disponível
    if CACHE_ENABLED:
        cached_result = ValidationCache.get_cpf(cpf_limpo)
        if cached_result is not None:
            cache.increment("cache_hits", 1, "stats")
            if cached_result['valid']:
                return cpf_limpo  # Retorna apenas números
            else:
                if raise_error:
                    raise ValueError('CPF inválido (cached)')
                return None
        cache.increment("cache_misses", 1, "stats")
        cache.increment("validation_count", 1, "stats")
    
    # Verificar se tem 11 dígitos
    if len(cpf_limpo) != 11:
        if CACHE_ENABLED:
            ValidationCache.cache_cpf(cpf_limpo, False)
        if raise_error:
            raise ValueError('CPF deve ter 11 dígitos')
        return None
    
    # Verificar se todos os dígitos são iguais
    if cpf_limpo == cpf_limpo[0] * 11:
        if CACHE_ENABLED:
            ValidationCache.cache_cpf(cpf_limpo, False)
        if raise_error:
            raise ValueError('CPF inválido: todos os dígitos são iguais')
        return None
    
    # Calcular primeiro dígito verificador
    soma = sum(int(cpf_limpo[i]) * (10 - i) for i in range(9))
    digito1 = 11 - (soma % 11)
    digito1 = 0 if digito1 >= 10 else digito1
    
    # Calcular segundo dígito verificador
    soma = sum(int(cpf_limpo[i]) * (11 - i) for i in range(10))
    digito2 = 11 - (soma % 11)
    digito2 = 0 if digito2 >= 10 else digito2
    
    # Verificar se os dígitos calculados conferem
    if int(cpf_limpo[9]) != digito1 or int(cpf_limpo[10]) != digito2:
        if CACHE_ENABLED:
            ValidationCache.cache_cpf(cpf_limpo, False)
        if raise_error:
            raise ValueError('CPF inválido: dígitos verificadores incorretos')
        return None
    
    # CPF válido - armazena no cache
    if CACHE_ENABLED:
        formatted = formatar_cpf_display(cpf_limpo)
        ValidationCache.cache_cpf(cpf_limpo, True, formatted)
    
    return cpf_limpo

def formatar_cpf(cpf: str) -> str:
    """
    Formata CPF para exibição (XXX.XXX.XXX-XX)
    
    Args:
        cpf: String com o CPF
    
    Returns:
        CPF formatado
    """
    cpf_limpo = validar_cpf(cpf)
    if not cpf_limpo:
        return cpf
    
    return f"{cpf_limpo[:3]}.{cpf_limpo[3:6]}.{cpf_limpo[6:9]}-{cpf_limpo[9:]}"

def formatar_cpf_display(cpf: str) -> str:
    """Helper interno para formatar CPF sem revalidar"""
    cpf_limpo = re.sub(r'\D', '', str(cpf))
    if len(cpf_limpo) == 11:
        return f"{cpf_limpo[:3]}.{cpf_limpo[3:6]}.{cpf_limpo[6:9]}-{cpf_limpo[9:]}"
    return cpf

def validar_cnpj(cnpj: str, raise_error: bool = True) -> Optional[str]:
    """
    Valida CNPJ brasileiro com cache
    
    Args:
        cnpj: String com o CNPJ
        raise_error: Se True, lança exceção em caso de erro
    
    Returns:
        CNPJ limpo (apenas números) se válido, None se inválido
    """
    # Remover caracteres não numéricos
    cnpj_limpo = re.sub(r'\D', '', str(cnpj))
    
    # Verificar cache primeiro se disponível
    if CACHE_ENABLED:
        cached_result = ValidationCache.get_cnpj(cnpj_limpo)
        if cached_result is not None:
            cache.increment("cache_hits", 1, "stats")
            if cached_result['valid']:
                return cnpj_limpo  # Retorna apenas números
            else:
                if raise_error:
                    raise ValueError('CNPJ inválido (cached)')
                return None
        cache.increment("cache_misses", 1, "stats")
        cache.increment("validation_count", 1, "stats")
    
    # Verificar se tem 14 dígitos
    if len(cnpj_limpo) != 14:
        if CACHE_ENABLED:
            ValidationCache.cache_cnpj(cnpj_limpo, False)
        if raise_error:
            raise ValueError('CNPJ deve ter 14 dígitos')
        return None
    
    # Verificar se todos os dígitos são iguais
    if cnpj_limpo == cnpj_limpo[0] * 14:
        if CACHE_ENABLED:
            ValidationCache.cache_cnpj(cnpj_limpo, False)
        if raise_error:
            raise ValueError('CNPJ inválido: todos os dígitos são iguais')
        return None
    
    # Validar dígitos verificadores
    multiplicadores1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    multiplicadores2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    
    # Calcular primeiro dígito
    soma = sum(int(cnpj_limpo[i]) * multiplicadores1[i] for i in range(12))
    digito1 = 11 - (soma % 11)
    digito1 = 0 if digito1 >= 10 else digito1
    
    # Calcular segundo dígito
    soma = sum(int(cnpj_limpo[i]) * multiplicadores2[i] for i in range(13))
    digito2 = 11 - (soma % 11)
    digito2 = 0 if digito2 >= 10 else digito2
    
    # Verificar se os dígitos calculados conferem
    if int(cnpj_limpo[12]) != digito1 or int(cnpj_limpo[13]) != digito2:
        if CACHE_ENABLED:
            ValidationCache.cache_cnpj(cnpj_limpo, False)
        if raise_error:
            raise ValueError('CNPJ inválido: dígitos verificadores incorretos')
        return None
    
    # CNPJ válido - armazena no cache
    if CACHE_ENABLED:
        formatted = formatar_cnpj_display(cnpj_limpo)
        ValidationCache.cache_cnpj(cnpj_limpo, True, formatted)
    
    return cnpj_limpo

def formatar_cnpj(cnpj: str) -> str:
    """
    Formata CNPJ para exibição (XX.XXX.XXX/XXXX-XX)
    
    Args:
        cnpj: String com o CNPJ
    
    Returns:
        CNPJ formatado
    """
    cnpj_limpo = validar_cnpj(cnpj)
    if not cnpj_limpo:
        return cnpj
    
    return f"{cnpj_limpo[:2]}.{cnpj_limpo[2:5]}.{cnpj_limpo[5:8]}/{cnpj_limpo[8:12]}-{cnpj_limpo[12:]}"

def formatar_cnpj_display(cnpj: str) -> str:
    """Helper interno para formatar CNPJ sem revalidar"""
    cnpj_limpo = re.sub(r'\D', '', str(cnpj))
    if len(cnpj_limpo) == 14:
        return f"{cnpj_limpo[:2]}.{cnpj_limpo[2:5]}.{cnpj_limpo[5:8]}/{cnpj_limpo[8:12]}-{cnpj_limpo[12:]}"
    return cnpj

# ===== VALIDADORES DE CONTATO =====

def validar_email_address(email: str, raise_error: bool = True) -> Optional[str]:
    """
    Valida endereço de email
    
    Args:
        email: String com o email
        raise_error: Se True, lança exceção em caso de erro
    
    Returns:
        Email normalizado se válido, None se inválido
    """
    try:
        # Validar e normalizar email
        validation = validate_email(email)
        return validation.email
    except EmailNotValidError as e:
        if raise_error:
            raise ValueError(f'Email inválido: {str(e)}')
        return None

def validar_telefone(telefone: str, raise_error: bool = True) -> Optional[str]:
    """
    Valida e formata telefone brasileiro
    
    Args:
        telefone: String com o telefone
        raise_error: Se True, lança exceção em caso de erro
    
    Returns:
        Telefone limpo (apenas números) se válido
    """
    # Remover caracteres não numéricos
    telefone_limpo = re.sub(r'\D', '', str(telefone))
    
    # Verificar comprimento (10 ou 11 dígitos com DDD)
    if len(telefone_limpo) < 10 or len(telefone_limpo) > 11:
        if raise_error:
            raise ValueError('Telefone deve ter 10 ou 11 dígitos (com DDD)')
        return None
    
    # Verificar se o DDD é válido (11-99)
    ddd = int(telefone_limpo[:2])
    if ddd < 11 or ddd > 99:
        if raise_error:
            raise ValueError('DDD inválido')
        return None
    
    # Se tem 11 dígitos, verificar se é celular (9 no início)
    if len(telefone_limpo) == 11 and telefone_limpo[2] != '9':
        if raise_error:
            raise ValueError('Celular deve começar com 9')
        return None
    
    return telefone_limpo

def formatar_telefone(telefone: str) -> str:
    """
    Formata telefone para exibição
    
    Args:
        telefone: String com o telefone
    
    Returns:
        Telefone formatado: (XX) XXXXX-XXXX ou (XX) XXXX-XXXX
    """
    telefone_limpo = validar_telefone(telefone)
    if not telefone_limpo:
        return telefone
    
    if len(telefone_limpo) == 11:
        return f"({telefone_limpo[:2]}) {telefone_limpo[2:7]}-{telefone_limpo[7:]}"
    else:
        return f"({telefone_limpo[:2]}) {telefone_limpo[2:6]}-{telefone_limpo[6:]}"

# ===== VALIDADORES DE TEXTO =====

def validar_nome(nome: str, min_length: int = 2, max_length: int = 255, raise_error: bool = True) -> Optional[str]:
    """
    Valida nome/texto
    
    Args:
        nome: String com o nome
        min_length: Comprimento mínimo
        max_length: Comprimento máximo
        raise_error: Se True, lança exceção em caso de erro
    
    Returns:
        Nome limpo e validado
    """
    if not nome or not nome.strip():
        if raise_error:
            raise ValueError('Nome é obrigatório e não pode estar vazio')
        return None
    
    nome_limpo = nome.strip()
    
    if len(nome_limpo) < min_length:
        if raise_error:
            raise ValueError(f'Nome deve ter pelo menos {min_length} caracteres')
        return None
    
    if len(nome_limpo) > max_length:
        if raise_error:
            raise ValueError(f'Nome não pode ter mais de {max_length} caracteres')
        return None
    
    # Verificar se contém apenas espaços ou caracteres especiais
    if not re.search(r'[a-zA-Z]', nome_limpo):
        if raise_error:
            raise ValueError('Nome deve conter pelo menos uma letra')
        return None
    
    return nome_limpo

def validar_senha(senha: str, min_length: int = 6, require_uppercase: bool = False, 
                  require_lowercase: bool = False, require_digit: bool = False, 
                  require_special: bool = False, raise_error: bool = True) -> Optional[str]:
    """
    Valida senha com critérios configuráveis
    
    Args:
        senha: String com a senha
        min_length: Comprimento mínimo
        require_uppercase: Exigir letra maiúscula
        require_lowercase: Exigir letra minúscula
        require_digit: Exigir número
        require_special: Exigir caractere especial
        raise_error: Se True, lança exceção em caso de erro
    
    Returns:
        Senha se válida, None se inválida
    """
    if not senha or len(senha) < min_length:
        if raise_error:
            raise ValueError(f'Senha deve ter pelo menos {min_length} caracteres')
        return None
    
    if require_uppercase and not re.search(r'[A-Z]', senha):
        if raise_error:
            raise ValueError('Senha deve conter pelo menos uma letra maiúscula')
        return None
    
    if require_lowercase and not re.search(r'[a-z]', senha):
        if raise_error:
            raise ValueError('Senha deve conter pelo menos uma letra minúscula')
        return None
    
    if require_digit and not re.search(r'\d', senha):
        if raise_error:
            raise ValueError('Senha deve conter pelo menos um número')
        return None
    
    if require_special and not re.search(r'[!@#$%^&*(),.?":{}|<>]', senha):
        if raise_error:
            raise ValueError('Senha deve conter pelo menos um caractere especial')
        return None
    
    return senha

# ===== VALIDADORES DE NÚMEROS E VALORES =====

def validar_valor_monetario(valor: Union[str, float, Decimal], min_value: Decimal = Decimal('0'), 
                           max_value: Optional[Decimal] = None, raise_error: bool = True) -> Optional[Decimal]:
    """
    Valida valor monetário
    
    Args:
        valor: Valor a ser validado
        min_value: Valor mínimo permitido
        max_value: Valor máximo permitido (opcional)
        raise_error: Se True, lança exceção em caso de erro
    
    Returns:
        Valor como Decimal se válido
    """
    try:
        # Converter para Decimal
        if isinstance(valor, str):
            # Remover símbolos monetários e espaços
            valor_limpo = re.sub(r'[R$\s.]', '', valor).replace(',', '.')
            valor_decimal = Decimal(valor_limpo)
        else:
            valor_decimal = Decimal(str(valor))
        
        # Verificar valor mínimo
        if valor_decimal < min_value:
            if raise_error:
                raise ValueError(f'Valor deve ser maior ou igual a {min_value}')
            return None
        
        # Verificar valor máximo
        if max_value and valor_decimal > max_value:
            if raise_error:
                raise ValueError(f'Valor deve ser menor ou igual a {max_value}')
            return None
        
        # Arredondar para 2 casas decimais
        return valor_decimal.quantize(Decimal('0.01'))
        
    except (ValueError, TypeError) as e:
        if raise_error:
            raise ValueError(f'Valor monetário inválido: {str(e)}')
        return None

def validar_quantidade(quantidade: Union[str, int], min_value: int = 0, 
                       max_value: Optional[int] = None, raise_error: bool = True) -> Optional[int]:
    """
    Valida quantidade (número inteiro)
    
    Args:
        quantidade: Quantidade a ser validada
        min_value: Valor mínimo permitido
        max_value: Valor máximo permitido (opcional)
        raise_error: Se True, lança exceção em caso de erro
    
    Returns:
        Quantidade como int se válida
    """
    try:
        # Converter para int
        qty = int(quantidade)
        
        # Verificar valor mínimo
        if qty < min_value:
            if raise_error:
                raise ValueError(f'Quantidade deve ser maior ou igual a {min_value}')
            return None
        
        # Verificar valor máximo
        if max_value and qty > max_value:
            if raise_error:
                raise ValueError(f'Quantidade deve ser menor ou igual a {max_value}')
            return None
        
        return qty
        
    except (ValueError, TypeError) as e:
        if raise_error:
            raise ValueError(f'Quantidade inválida: {str(e)}')
        return None

def validar_percentual(percentual: Union[str, float, Decimal], raise_error: bool = True) -> Optional[Decimal]:
    """
    Valida valor percentual (0-100)
    
    Args:
        percentual: Percentual a ser validado
        raise_error: Se True, lança exceção em caso de erro
    
    Returns:
        Percentual como Decimal se válido
    """
    return validar_valor_monetario(percentual, Decimal('0'), Decimal('100'), raise_error)

# ===== VALIDADORES DE DATA E HORA =====

def validar_data(data: Union[str, date, datetime], formato: str = '%Y-%m-%d', 
                 min_date: Optional[date] = None, max_date: Optional[date] = None,
                 raise_error: bool = True) -> Optional[date]:
    """
    Valida data
    
    Args:
        data: Data a ser validada
        formato: Formato esperado da string de data
        min_date: Data mínima permitida
        max_date: Data máxima permitida
        raise_error: Se True, lança exceção em caso de erro
    
    Returns:
        Data como date se válida
    """
    try:
        # Converter para date
        if isinstance(data, str):
            data_obj = datetime.strptime(data, formato).date()
        elif isinstance(data, datetime):
            data_obj = data.date()
        else:
            data_obj = data
        
        # Verificar data mínima
        if min_date and data_obj < min_date:
            if raise_error:
                raise ValueError(f'Data deve ser posterior a {min_date}')
            return None
        
        # Verificar data máxima
        if max_date and data_obj > max_date:
            if raise_error:
                raise ValueError(f'Data deve ser anterior a {max_date}')
            return None
        
        return data_obj
        
    except (ValueError, TypeError) as e:
        if raise_error:
            raise ValueError(f'Data inválida: {str(e)}')
        return None

def validar_datetime(dt: Union[str, datetime], formato: str = '%Y-%m-%dT%H:%M:%S',
                     min_datetime: Optional[datetime] = None, max_datetime: Optional[datetime] = None,
                     raise_error: bool = True) -> Optional[datetime]:
    """
    Valida datetime
    
    Args:
        dt: Datetime a ser validado
        formato: Formato esperado da string
        min_datetime: Datetime mínimo permitido
        max_datetime: Datetime máximo permitido
        raise_error: Se True, lança exceção em caso de erro
    
    Returns:
        Datetime se válido
    """
    try:
        # Converter para datetime
        if isinstance(dt, str):
            # Tentar diferentes formatos comuns
            formats = [
                formato,
                '%Y-%m-%dT%H:%M:%S.%f',
                '%Y-%m-%dT%H:%M:%SZ',
                '%Y-%m-%dT%H:%M:%S.%fZ',
                '%Y-%m-%d %H:%M:%S',
                '%d/%m/%Y %H:%M:%S',
            ]
            
            dt_obj = None
            for fmt in formats:
                try:
                    dt_obj = datetime.strptime(dt.replace('Z', '+00:00') if 'Z' in dt else dt, fmt)
                    break
                except ValueError:
                    continue
            
            if not dt_obj:
                raise ValueError(f'Formato de datetime não reconhecido: {dt}')
        else:
            dt_obj = dt
        
        # Verificar datetime mínimo
        if min_datetime and dt_obj < min_datetime:
            if raise_error:
                raise ValueError(f'Datetime deve ser posterior a {min_datetime}')
            return None
        
        # Verificar datetime máximo
        if max_datetime and dt_obj > max_datetime:
            if raise_error:
                raise ValueError(f'Datetime deve ser anterior a {max_datetime}')
            return None
        
        return dt_obj
        
    except (ValueError, TypeError) as e:
        if raise_error:
            raise ValueError(f'Datetime inválido: {str(e)}')
        return None

# ===== VALIDADORES DE COLEÇÕES =====

def validar_lista_ids(ids: List[Union[str, int]], min_items: int = 0, 
                     max_items: Optional[int] = None, raise_error: bool = True) -> Optional[List[int]]:
    """
    Valida lista de IDs
    
    Args:
        ids: Lista de IDs
        min_items: Número mínimo de itens
        max_items: Número máximo de itens
        raise_error: Se True, lança exceção em caso de erro
    
    Returns:
        Lista de IDs como int se válida
    """
    if not isinstance(ids, list):
        if raise_error:
            raise ValueError('Deve ser uma lista de IDs')
        return None
    
    # Verificar quantidade mínima
    if len(ids) < min_items:
        if raise_error:
            raise ValueError(f'Lista deve ter pelo menos {min_items} itens')
        return None
    
    # Verificar quantidade máxima
    if max_items and len(ids) > max_items:
        if raise_error:
            raise ValueError(f'Lista não pode ter mais de {max_items} itens')
        return None
    
    # Converter para int e validar
    try:
        ids_int = [int(id_val) for id_val in ids]
        
        # Verificar IDs duplicados
        if len(ids_int) != len(set(ids_int)):
            if raise_error:
                raise ValueError('Lista contém IDs duplicados')
            return None
        
        # Verificar IDs negativos
        if any(id_val <= 0 for id_val in ids_int):
            if raise_error:
                raise ValueError('IDs devem ser positivos')
            return None
        
        return ids_int
        
    except (ValueError, TypeError) as e:
        if raise_error:
            raise ValueError(f'ID inválido na lista: {str(e)}')
        return None

# ===== VALIDADORES COMPOSTOS =====

def validar_dados_usuario(dados: Dict[str, Any], is_update: bool = False) -> Dict[str, Any]:
    """
    Valida dados completos de usuário
    
    Args:
        dados: Dicionário com dados do usuário
        is_update: Se True, campos são opcionais
    
    Returns:
        Dados validados e formatados
    """
    validated = {}
    
    # CPF
    if 'cpf' in dados or not is_update:
        cpf = dados.get('cpf')
        if not cpf and not is_update:
            raise ValueError('CPF é obrigatório')
        if cpf:
            validated['cpf'] = formatar_cpf(cpf)
    
    # Nome
    if 'nome' in dados or not is_update:
        nome = dados.get('nome')
        if not nome and not is_update:
            raise ValueError('Nome é obrigatório')
        if nome:
            validated['nome'] = validar_nome(nome)
    
    # Email
    if 'email' in dados or not is_update:
        email = dados.get('email')
        if not email and not is_update:
            raise ValueError('Email é obrigatório')
        if email:
            validated['email'] = validar_email_address(email)
    
    # Telefone (opcional)
    if 'telefone' in dados:
        telefone = dados.get('telefone')
        if telefone:
            validated['telefone'] = formatar_telefone(telefone)
    
    # Senha
    if 'senha' in dados:
        senha = dados.get('senha')
        if senha:
            validated['senha'] = validar_senha(senha, min_length=6)
    
    # Tipo de usuário
    if 'tipo' in dados or 'tipo_usuario' in dados:
        tipo = dados.get('tipo') or dados.get('tipo_usuario')
        if tipo:
            tipos_validos = ['admin', 'promoter', 'cliente', 'operador', 'vendedor', 'gestor']
            if tipo not in tipos_validos:
                raise ValueError(f'Tipo de usuário deve ser um dos: {", ".join(tipos_validos)}')
            validated['tipo'] = tipo
    
    return validated

def validar_dados_evento(dados: Dict[str, Any], is_update: bool = False) -> Dict[str, Any]:
    """
    Valida dados completos de evento
    
    Args:
        dados: Dicionário com dados do evento
        is_update: Se True, campos são opcionais
    
    Returns:
        Dados validados e formatados
    """
    validated = {}
    
    # Nome
    if 'nome' in dados or not is_update:
        nome = dados.get('nome')
        if not nome and not is_update:
            raise ValueError('Nome do evento é obrigatório')
        if nome:
            validated['nome'] = validar_nome(nome, min_length=3)
    
    # Data do evento
    if 'data_evento' in dados or not is_update:
        data_evento = dados.get('data_evento')
        if not data_evento and not is_update:
            raise ValueError('Data do evento é obrigatória')
        if data_evento:
            validated['data_evento'] = validar_datetime(
                data_evento,
                min_datetime=datetime.now()
            )
    
    # Local
    if 'local' in dados or not is_update:
        local = dados.get('local')
        if not local and not is_update:
            raise ValueError('Local do evento é obrigatório')
        if local:
            validated['local'] = validar_nome(local, min_length=3)
    
    # Capacidade máxima (opcional)
    if 'capacidade_maxima' in dados:
        capacidade = dados.get('capacidade_maxima')
        if capacidade:
            validated['capacidade_maxima'] = validar_quantidade(capacidade, min_value=1, max_value=1000000)
    
    # Limite de idade (opcional)
    if 'limite_idade' in dados:
        limite = dados.get('limite_idade')
        if limite:
            validated['limite_idade'] = validar_quantidade(limite, min_value=0, max_value=120)
    
    return validated

# ===== CLASSE DE VALIDAÇÃO PARA FASTAPI =====

class Validator:
    """Classe auxiliar para validações no FastAPI"""
    
    @staticmethod
    def validate_cpf(cpf: str) -> str:
        """Valida e retorna CPF formatado"""
        try:
            return formatar_cpf(cpf)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={"field": "cpf", "message": str(e)}
            )
    
    @staticmethod
    def validate_cnpj(cnpj: str) -> str:
        """Valida e retorna CNPJ formatado"""
        try:
            return formatar_cnpj(cnpj)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={"field": "cnpj", "message": str(e)}
            )
    
    @staticmethod
    def validate_email(email: str) -> str:
        """Valida e retorna email normalizado"""
        try:
            return validar_email_address(email)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={"field": "email", "message": str(e)}
            )
    
    @staticmethod
    def validate_phone(telefone: str) -> str:
        """Valida e retorna telefone formatado"""
        try:
            return formatar_telefone(telefone)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={"field": "telefone", "message": str(e)}
            )

# Exportar tudo
__all__ = [
    # Documentos
    'validar_cpf', 'formatar_cpf', 'validar_cnpj', 'formatar_cnpj',
    # Contato
    'validar_email_address', 'validar_telefone', 'formatar_telefone',
    # Texto
    'validar_nome', 'validar_senha',
    # Números
    'validar_valor_monetario', 'validar_quantidade', 'validar_percentual',
    # Data/Hora
    'validar_data', 'validar_datetime',
    # Coleções
    'validar_lista_ids',
    # Compostos
    'validar_dados_usuario', 'validar_dados_evento',
    # Classe FastAPI
    'Validator'
]