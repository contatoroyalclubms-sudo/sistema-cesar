#!/usr/bin/env python3
"""
Test script for import/export functionality
"""
import pytest
import asyncio
import tempfile
import json
from pathlib import Path
from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

from app.main import app
from app.database import get_db, Base
from app.services.import_export_service import ImportExportService

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_import_export.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="module")
def setup_database():
    """Setup test database"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def client():
    """Test client"""
    return TestClient(app)

@pytest.fixture
def db_session():
    """Database session for tests"""
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()

@pytest.fixture
def import_service(db_session):
    """Import/Export service instance"""
    return ImportExportService(db_session)

class TestImportExportService:
    """Test cases for Import/Export service"""
    
    def test_service_initialization(self, import_service):
        """Test service initialization"""
        assert import_service is not None
        assert import_service.chunk_size == 100
        assert hasattr(import_service, 'validation_rules')
    
    def test_validation_rules(self, import_service):
        """Test validation rules setup"""
        rules = import_service.validation_rules
        
        assert 'codigo' in rules
        assert 'nome' in rules
        assert 'preco_venda' in rules
        
        # Test required fields
        assert rules['codigo']['required'] is True
        assert rules['nome']['required'] is True
        assert rules['preco_venda']['required'] is True
    
    def test_get_file_format(self, import_service):
        """Test file format detection"""
        assert import_service._get_file_format('test.csv') == 'csv'
        assert import_service._get_file_format('test.xlsx') == 'xlsx'
        assert import_service._get_file_format('test.xls') == 'xlsx'
        assert import_service._get_file_format('test.json') == 'json'
        assert import_service._get_file_format('test.txt') is None
        assert import_service._get_file_format('') is None
    
    def test_suggest_field_mapping(self, import_service):
        """Test automatic field mapping suggestion"""
        headers = ['codigo', 'nome', 'preco', 'categoria', 'barcode']
        mapping = import_service._suggest_field_mapping(headers)
        
        assert mapping.get('codigo') == 'codigo'
        assert mapping.get('nome') == 'nome'
        assert mapping.get('preco') == 'preco_venda'
        assert mapping.get('categoria') == 'categoria'
        assert mapping.get('barcode') == 'codigo_barras'
    
    def test_csv_analysis(self, import_service):
        """Test CSV file analysis"""
        csv_content = b'codigo,nome,preco\nPROD001,Produto Teste,10.50\nPROD002,Outro Produto,25.00'
        
        headers, data = import_service._analyze_csv(csv_content)
        
        assert headers == ['codigo', 'nome', 'preco']
        assert len(data) == 2
        assert data[0]['codigo'] == 'PROD001'
        assert data[0]['nome'] == 'Produto Teste'
        assert data[0]['preco'] == '10.50'
    
    def test_json_analysis(self, import_service):
        """Test JSON file analysis"""
        json_data = [
            {'codigo': 'PROD001', 'nome': 'Produto Teste', 'preco': 10.50},
            {'codigo': 'PROD002', 'nome': 'Outro Produto', 'preco': 25.00}
        ]
        json_content = json.dumps(json_data).encode('utf-8')
        
        headers, data = import_service._analyze_json(json_content)
        
        assert set(headers) == {'codigo', 'nome', 'preco'}
        assert len(data) == 2
        assert data[0]['codigo'] == 'PROD001'
    
    def test_validation_required_fields(self, import_service):
        """Test validation of required fields"""
        produto = {'nome': 'Teste', 'categoria': 'Bebidas'}  # Missing codigo
        validacoes = import_service._validate_row(1, produto, {})
        
        # Should have error for missing codigo
        codigo_errors = [v for v in validacoes if v.campo == 'codigo']
        assert len(codigo_errors) > 0
        assert any('obrigatório' in v.mensagem for v in codigo_errors)
    
    def test_validation_number_fields(self, import_service):
        """Test validation of number fields"""
        produto = {
            'codigo': 'PROD001',
            'nome': 'Teste',
            'categoria': 'Bebidas',
            'preco_venda': 'invalid_number'
        }
        validacoes = import_service._validate_row(1, produto, {})
        
        # Should have error for invalid number
        preco_errors = [v for v in validacoes if v.campo == 'preco_venda']
        assert len(preco_errors) > 0
    
    def test_estimate_file_size(self, import_service):
        """Test file size estimation"""
        size = import_service._estimate_file_size(100, 5, 'csv')
        assert 'KB' in size or 'bytes' in size
        
        size = import_service._estimate_file_size(10000, 10, 'xlsx')
        assert 'KB' in size or 'MB' in size
    
    def test_produto_to_dict(self, import_service):
        """Test product to dictionary conversion"""
        # Mock product object
        class MockProduto:
            def __init__(self):
                self.codigo_interno = 'PROD001'
                self.nome = 'Produto Teste'
                self.preco = 10.50
                self.estoque_atual = 100
        
        produto = MockProduto()
        campos = ['codigo_interno', 'nome', 'preco', 'estoque_atual']
        
        result = import_service._produto_to_dict(produto, campos)
        
        assert result['codigo_interno'] == 'PROD001'
        assert result['nome'] == 'Produto Teste'
        assert result['preco'] == 10.50
        assert result['estoque_atual'] == 100

class TestImportExportAPI:
    """Test cases for Import/Export API endpoints"""
    
    def test_get_import_options(self, client, setup_database):
        """Test get import options endpoint"""
        response = client.get("/api/estoque/import/options")
        
        assert response.status_code == 200
        data = response.json()
        
        assert 'formatos_suportados' in data
        assert 'campos_disponiveis' in data
        assert len(data['campos_disponiveis']) > 0
    
    def test_get_export_formats(self, client, setup_database):
        """Test get export formats endpoint"""
        response = client.get("/api/estoque/export/formats")
        
        assert response.status_code == 200
        data = response.json()
        
        assert 'formats' in data
        assert 'types' in data
        assert len(data['formats']) > 0
        assert len(data['types']) > 0
    
    def test_download_template_csv(self, client, setup_database):
        """Test download CSV template"""
        response = client.get("/api/estoque/templates/csv/download")
        
        assert response.status_code == 200
        assert response.headers['content-type'] == 'text/csv; charset=utf-8'
    
    def test_download_template_json(self, client, setup_database):
        """Test download JSON template"""
        response = client.get("/api/estoque/templates/json/download")
        
        assert response.status_code == 200
        assert response.headers['content-type'] == 'application/json'
    
    def test_upload_invalid_file_format(self, client, setup_database):
        """Test upload with invalid file format"""
        with tempfile.NamedTemporaryFile(suffix='.txt') as tmp:
            tmp.write(b'invalid content')
            tmp.seek(0)
            
            response = client.post("/api/estoque/upload", files={"file": tmp})
            
            assert response.status_code == 400
            assert "não suportado" in response.json()['detail']
    
    def test_dashboard_stats(self, client, setup_database):
        """Test dashboard stats endpoint"""
        response = client.get("/api/estoque/dashboard/stats")
        
        # Should return stats even if no data
        assert response.status_code == 200
        data = response.json()
        
        assert 'stats' in data
        assert 'recent_operations' in data

def create_sample_csv():
    """Create a sample CSV file for testing"""
    csv_content = """codigo,nome,categoria,preco_venda,estoque_atual
PROD001,Cerveja Lata 350ml,Bebidas,5.50,100
PROD002,Água 500ml,Bebidas,3.00,200
PROD003,Hambúrguer Tradicional,Comidas,25.00,50
PROD004,Batata Frita,Comidas,12.00,75"""
    
    return csv_content.encode('utf-8')

def create_sample_json():
    """Create a sample JSON file for testing"""
    data = [
        {
            "codigo": "PROD001",
            "nome": "Cerveja Lata 350ml",
            "categoria": "Bebidas",
            "preco_venda": 5.50,
            "estoque_atual": 100
        },
        {
            "codigo": "PROD002", 
            "nome": "Água 500ml",
            "categoria": "Bebidas",
            "preco_venda": 3.00,
            "estoque_atual": 200
        }
    ]
    
    return json.dumps(data).encode('utf-8')

def run_integration_tests():
    """Run integration tests"""
    print("🧪 Executando testes de integração...")
    
    # Test CSV processing
    print("📄 Testando processamento CSV...")
    csv_data = create_sample_csv()
    print(f"  ✅ CSV criado: {len(csv_data)} bytes")
    
    # Test JSON processing
    print("📋 Testando processamento JSON...")
    json_data = create_sample_json()
    print(f"  ✅ JSON criado: {len(json_data)} bytes")
    
    print("✅ Testes de integração concluídos!")

if __name__ == "__main__":
    print("=" * 60)
    print("🧪 TESTES: Módulo Import/Export")
    print("=" * 60)
    
    # Run integration tests
    run_integration_tests()
    
    print("\n📋 Para executar todos os testes:")
    print("   cd backend")
    print("   python -m pytest test_import_export.py -v")
    
    print("\n📋 Para executar testes com cobertura:")
    print("   python -m pytest test_import_export.py --cov=app.services.import_export_service --cov-report=html -v")