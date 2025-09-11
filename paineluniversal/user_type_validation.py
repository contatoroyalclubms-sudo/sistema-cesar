
"""
Validação robusta para tipos de usuário.
Adicione este código ao auth.py para validação extra.
"""

def validate_user_type(tipo_str: str) -> str:
    """
    Valida e normaliza tipo de usuário.
    Garante compatibilidade entre frontend e backend.
    """
    # Normalizar entrada
    tipo_normalizado = tipo_str.lower().strip()
    
    # Mapeamento de valores válidos
    valid_types = {
        'admin': 'admin',
        'administrador': 'admin', 
        'administrator': 'admin',
        'promoter': 'promoter',
        'promotor': 'promoter',
        'cliente': 'cliente',
        'client': 'cliente',
        'user': 'cliente',
        'usuario': 'cliente'
    }
    
    if tipo_normalizado not in valid_types:
        raise ValueError(f"Tipo de usuário inválido: {tipo_str}. Valores aceitos: {list(valid_types.keys())}")
    
    return valid_types[tipo_normalizado]

# Uso no endpoint register:
# tipo_validado = validate_user_type(usuario_data.tipo.value)
