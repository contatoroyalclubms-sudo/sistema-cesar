import os
os.environ['DISABLE_REDIS'] = 'true'
os.environ['PYTHONIOENCODING'] = 'utf-8'

import uvicorn
from app.main import app

if __name__ == "__main__":
    print("Iniciando servidor de teste sem Redis...")
    print("Backend disponivel em http://localhost:8000")
    print("Documentacao em http://localhost:8000/docs")
    
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000,
        log_level="error",
        reload=False
    )
