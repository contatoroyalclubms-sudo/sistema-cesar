"""
Middleware de debug para rastrear onde o Redis está sendo chamado
"""
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
import traceback
import json

class DebugMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        method = request.method
        
        print(f"[DEBUG MIDDLEWARE] {method} {path}")
        
        # Se for login, rastrear detalhadamente
        if "/auth/login" in path:
            print("[DEBUG] Login request intercepted!")
            print(f"[DEBUG] Headers: {dict(request.headers)}")
            
            try:
                # Processar requisição
                response = await call_next(request)
                print(f"[DEBUG] Response status: {response.status_code}")
                return response
                
            except Exception as e:
                print(f"[DEBUG ERROR] Exception in login: {str(e)}")
                print(f"[DEBUG ERROR] Exception type: {type(e)}")
                print(f"[DEBUG ERROR] Traceback:")
                traceback.print_exc()
                
                # Verificar se é erro de Redis
                if "6379" in str(e) or "redis" in str(e).lower():
                    print("[DEBUG] REDIS ERROR DETECTED!")
                    print("[DEBUG] Stack trace for Redis error:")
                    import sys
                    for frame_info in traceback.extract_stack():
                        if "redis" in frame_info.filename.lower() or "cache" in frame_info.filename.lower():
                            print(f"  -> {frame_info.filename}:{frame_info.lineno} in {frame_info.name}")
                
                # Re-raise para manter comportamento normal
                raise
        
        # Outras requisições processam normalmente
        return await call_next(request)