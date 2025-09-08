#!/usr/bin/env python3
"""
Test script to check inventory imports
"""

try:
    print("Testing inventory imports...")
    
    # Test individual imports
    print("1. Testing models...")
    from app.inventory.models import Category, Unit, Product
    print("   ✅ Models imported successfully")
    
    print("2. Testing schemas...")
    from app.inventory.schemas import StockMovementCreate, PaginatedResponse
    print("   ✅ Schemas imported successfully")
    
    print("3. Testing repositories...")
    from app.inventory.repositories import InventoryRepository
    print("   ✅ Repository imported successfully")
    
    print("4. Testing services...")
    from app.inventory.services import InventoryService
    print("   ✅ Services imported successfully")
    
    print("5. Testing API router...")
    from app.inventory.api import router
    print("   ✅ API router imported successfully")
    
    print("6. Testing main inventory import...")
    from app.inventory import inventory_router
    print("   ✅ Main inventory import successful")
    
    print("\n🎉 All inventory imports working correctly!")
    
except Exception as e:
    print(f"❌ Import error: {e}")
    import traceback
    traceback.print_exc()
