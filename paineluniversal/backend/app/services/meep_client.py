import httpx
from typing import Optional, Dict, Any, List
from datetime import datetime
import asyncio
import json
import logging

logger = logging.getLogger(__name__)

class MEEPClient:
    def __init__(self):
        self.base_url = "https://beta.portal.meep.com.br"
        self.session = None
        self.cookies = {}
        
    async def __aenter__(self):
        self.session = httpx.AsyncClient(timeout=30.0, follow_redirects=True)
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.aclose()
            
    async def get_mock_eventos(self) -> List[Dict[str, Any]]:
        """Retorna eventos mock para teste"""
        return [
            {
                "meep_id": "MEEP001",
                "nome": "Tech Conference 2025",
                "data_inicio": "2025-02-15T09:00:00",
                "data_fim": "2025-02-15T18:00:00",
                "local": "Centro de Convencoes",
                "cidade": "Sao Paulo",
                "estado": "SP",
                "total_inscritos": 250,
                "total_presentes": 180,
                "total_vendas": 45000.00
            },
            {
                "meep_id": "MEEP002",
                "nome": "Workshop de Inovacao",
                "data_inicio": "2025-03-10T14:00:00",
                "data_fim": "2025-03-10T18:00:00",
                "local": "Hotel Plaza",
                "cidade": "Rio de Janeiro",
                "estado": "RJ",
                "total_inscritos": 80,
                "total_presentes": 65,
                "total_vendas": 12000.00
            }
        ]
