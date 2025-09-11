"""
CACHE COMPLETAMENTE DESABILITADO - Sem Redis
"""

from typing import Optional, Any, Callable
from functools import wraps

# Cache vazio que não faz nada
class DummyCache:
    """Cache fake que não faz nada"""
    def __init__(self):
        self.memory_cache = {}
        self.connected = False
        self.client = None
    
    def get(self, key: str, namespace: str = "default") -> Optional[Any]:
        return None
    
    def set(self, key: str, value: Any, ttl: int = 300, namespace: str = "default") -> bool:
        return True
    
    def delete(self, key: str, namespace: str = "default") -> bool:
        return True
    
    def flush(self, namespace: Optional[str] = None) -> int:
        return 0
    
    def increment(self, key: str, amount: int = 1, namespace: str = "default") -> int:
        return 0
    
    def exists(self, key: str, namespace: str = "default") -> bool:
        return False

# Usar DummyCache como padrão
RedisCache = DummyCache
MemoryCache = DummyCache
ValidationCache = DummyCache

# Instância global
cache = DummyCache()

# Decorator que não faz nada
def cached(ttl: int = 300, namespace: str = "default", key_prefix: str = None):
    """Decorator vazio"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        return wrapper
    return decorator

# Funções que não fazem nada
def cache_validation(validator_name: str, value: Any, is_valid: bool, ttl: int = 300):
    pass

def get_cached_validation(validator_name: str, value: Any) -> Optional[bool]:
    return None

def clear_validation_cache():
    pass