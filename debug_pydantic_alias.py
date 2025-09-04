#!/usr/bin/env python3
"""Script para debugar o comportamento do Pydantic Field alias"""

from pydantic import BaseModel, Field
from enum import Enum
import json

class TipoProduto(str, Enum):
    BEBIDA = "BEBIDA"
    COMIDA = "COMIDA"
    INGRESSO = "INGRESSO"
    FICHA = "FICHA"
    COMBO = "COMBO"
    VOUCHER = "VOUCHER"

class StatusProduto(str, Enum):
    ATIVO = "ATIVO"
    INATIVO = "INATIVO"

class ProdutoBase(BaseModel):
    nome: str
    descricao: str | None = None
    preco: float | None = None
    estoque: int | None = 0
    tipo_usuario: TipoProduto = Field(alias="tipo")  # Mudamos para alias apenas
    status: StatusProduto = StatusProduto.ATIVO
    codigo_barras: str | None = None
    categoria: str | None = None
    observacoes: str | None = None

    class Config:
        populate_by_name = True
        
class ProdutoCreate(ProdutoBase):
    evento_id: int | None = None

def test_pydantic_alias():
    print("🧪 Testando Pydantic Field alias...")
    
    # Dados simulando o que vem do frontend
    frontend_data = {
        "nome": "Pizza Debug",
        "descricao": "Teste de produto",
        "preco": 25.50,
        "estoque": 10,
        "tipo": "COMIDA",  # Frontend envia "tipo"
        "status": "ATIVO"
    }
    
    print("\n📥 Dados do frontend:")
    print(json.dumps(frontend_data, indent=2))
    
    try:
        # Tentativa 1: Parse direto
        print("\n🔄 Teste 1: Parse direto dos dados...")
        produto = ProdutoCreate(**frontend_data)
        print(f"✅ Parse OK: {produto}")
        print(f"📊 tipo_usuario value: {produto.tipo_usuario}")
        
        # Tentativa 2: Verificar dict()
        print("\n🔄 Teste 2: produto.dict()...")
        dict_normal = produto.dict()
        print(f"📋 Dict normal: {dict_normal}")
        
        # Tentativa 3: Verificar dict(by_alias=True)
        print("\n🔄 Teste 3: produto.dict(by_alias=True)...")
        dict_alias = produto.dict(by_alias=True)
        print(f"📋 Dict by_alias: {dict_alias}")
        
        # Tentativa 4: Verificar model_dump()
        print("\n🔄 Teste 4: produto.model_dump()...")
        dump_normal = produto.model_dump()
        print(f"📋 Dump normal: {dump_normal}")
        
        # Tentativa 5: Verificar model_dump(by_alias=True)
        print("\n🔄 Teste 5: produto.model_dump(by_alias=True)...")
        dump_alias = produto.model_dump(by_alias=True)
        print(f"📋 Dump by_alias: {dump_alias}")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        print(f"📝 Tipo do erro: {type(e)}")
        
        # Tentar parse com model_validate
        print("\n🔄 Teste alternativo: model_validate...")
        try:
            produto_alt = ProdutoCreate.model_validate(frontend_data)
            print(f"✅ model_validate OK: {produto_alt}")
        except Exception as e2:
            print(f"❌ model_validate falhou: {e2}")

if __name__ == "__main__":
    test_pydantic_alias()
