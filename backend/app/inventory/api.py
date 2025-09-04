"""
Inventory API routes
"""
from datetime import date
from typing import List, Optional, Dict, Any

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth import get_current_user, require_permission
from app.inventory.services import InventoryService
from app.inventory.schemas import (
    # Movement schemas
    StockMovementCreate, StockMovementResponse,
    # Position schemas
    StockPositionFilter, StockPositionResponse,
    # Movement history schemas
    MovementHistoryFilter,
    # Management schemas
    CategoryCreate, CategoryUpdate, CategoryResponse,
    UnitCreate, UnitUpdate, UnitResponse,
    ProductCreate, ProductUpdate, ProductResponse,
    LocationCreate, LocationUpdate, LocationResponse,
    MovementReasonCreate, MovementReasonUpdate, MovementReasonResponse,
    # Generic responses
    PaginatedResponse
)

router = APIRouter(prefix="/inventory", tags=["inventory"])

# Dependencies
def get_inventory_service(db: Session = Depends(get_db)) -> InventoryService:
    return InventoryService(db)

def get_organization_id(current_user = Depends(get_current_user)) -> int:
    return current_user.organization_id

# ================== STOCK MOVEMENTS ==================

@router.post("/movements", response_model=StockMovementResponse)
async def create_stock_movement(
    movement_data: StockMovementCreate,
    service: InventoryService = Depends(get_inventory_service),
    organization_id: int = Depends(get_organization_id),
    current_user = Depends(require_permission("inventory:write"))
):
    """Create a new stock movement"""
    return service.create_stock_movement(movement_data, organization_id, current_user.id)

@router.get("/movements", response_model=PaginatedResponse[StockMovementResponse])
async def get_stock_movements(
    product_id: Optional[int] = Query(None, description="Filter by product"),
    location_id: Optional[int] = Query(None, description="Filter by location"),
    movement_type: Optional[str] = Query(None, description="Filter by movement type"),
    date_from: Optional[date] = Query(None, description="Filter movements from date"),
    date_to: Optional[date] = Query(None, description="Filter movements to date"),
    document_ref: Optional[str] = Query(None, description="Filter by document reference"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=500),
    service: InventoryService = Depends(get_inventory_service),
    organization_id: int = Depends(get_organization_id),
    current_user = Depends(require_permission("inventory:read"))
):
    """Get stock movements with filters and pagination"""
    filters = MovementHistoryFilter(
        product_id=product_id,
        location_id=location_id,
        movement_type=movement_type,
        date_from=date_from,
        date_to=date_to,
        document_ref=document_ref,
        page=page,
        page_size=page_size
    )
    
    movements, total = service.get_stock_movements(organization_id, filters)
    pages = (total + page_size - 1) // page_size
    
    return PaginatedResponse[StockMovementResponse](
        items=movements,
        total=total,
        page=page,
        page_size=page_size,
        pages=pages
    )

@router.get("/movements/{movement_id}", response_model=StockMovementResponse)
async def get_stock_movement(
    movement_id: int,
    service: InventoryService = Depends(get_inventory_service),
    organization_id: int = Depends(get_organization_id),
    current_user = Depends(require_permission("inventory:read"))
):
    """Get stock movement by ID"""
    movement = service.get_stock_movement_by_id(movement_id, organization_id)
    if not movement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Stock movement not found"
        )
    return movement

# ================== STOCK POSITION ==================

@router.get("/position", response_model=StockPositionResponse)
async def get_stock_position(
    product_id: Optional[int] = Query(None, description="Filter by product"),
    category_id: Optional[int] = Query(None, description="Filter by category"),
    location_id: Optional[int] = Query(None, description="Filter by location"),
    q: Optional[str] = Query(None, description="Search products by name or code"),
    with_zero_stock: bool = Query(False, description="Include products with zero stock"),
    only_negative: bool = Query(False, description="Show only negative stock"),
    page: int = Query(1, ge=1),
    page_size: int = Query(100, ge=1, le=500),
    service: InventoryService = Depends(get_inventory_service),
    organization_id: int = Depends(get_organization_id),
    current_user = Depends(require_permission("inventory:read"))
):
    """Get current stock position with filters"""
    filters = StockPositionFilter(
        product_id=product_id,
        category_id=category_id,
        location_id=location_id,
        q=q,
        with_zero_stock=with_zero_stock,
        only_negative=only_negative,
        page=page,
        page_size=page_size
    )
    
    return service.get_stock_position(organization_id, filters)

# ================== AUTOCOMPLETE ENDPOINTS ==================

@router.get("/autocomplete/categories", response_model=List[CategoryResponse])
async def autocomplete_categories(
    q: Optional[str] = Query(None, min_length=1),
    service: InventoryService = Depends(get_inventory_service),
    organization_id: int = Depends(get_organization_id),
    current_user = Depends(require_permission("inventory:read"))
):
    """Get categories for autocomplete"""
    return service.get_categories(organization_id, q)

@router.get("/autocomplete/units", response_model=List[UnitResponse])
async def autocomplete_units(
    q: Optional[str] = Query(None, min_length=1),
    service: InventoryService = Depends(get_inventory_service),
    current_user = Depends(require_permission("inventory:read"))
):
    """Get units for autocomplete"""
    return service.get_units(q)

@router.get("/autocomplete/products", response_model=List[ProductResponse])
async def autocomplete_products(
    q: Optional[str] = Query(None, min_length=1),
    service: InventoryService = Depends(get_inventory_service),
    organization_id: int = Depends(get_organization_id),
    current_user = Depends(require_permission("inventory:read"))
):
    """Get products for autocomplete"""
    return service.get_products(organization_id, q)

@router.get("/autocomplete/locations", response_model=List[LocationResponse])
async def autocomplete_locations(
    q: Optional[str] = Query(None, min_length=1),
    service: InventoryService = Depends(get_inventory_service),
    organization_id: int = Depends(get_organization_id),
    current_user = Depends(require_permission("inventory:read"))
):
    """Get locations for autocomplete"""
    return service.get_locations(organization_id, q)

@router.get("/autocomplete/reasons", response_model=List[MovementReasonResponse])
async def autocomplete_movement_reasons(
    direction: Optional[str] = Query(None, description="Filter by direction: in, out, both"),
    service: InventoryService = Depends(get_inventory_service),
    organization_id: int = Depends(get_organization_id),
    current_user = Depends(require_permission("inventory:read"))
):
    """Get movement reasons for dropdowns"""
    return service.get_movement_reasons(organization_id, direction)

# ================== MANAGEMENT ENDPOINTS ==================

# Categories
@router.get("/categories", response_model=List[CategoryResponse])
async def get_categories(
    service: InventoryService = Depends(get_inventory_service),
    organization_id: int = Depends(get_organization_id),
    current_user = Depends(require_permission("inventory:read"))
):
    """Get all categories"""
    return service.get_categories(organization_id)

@router.post("/categories", response_model=CategoryResponse)
async def create_category(
    category_data: CategoryCreate,
    service: InventoryService = Depends(get_inventory_service),
    organization_id: int = Depends(get_organization_id),
    current_user = Depends(require_permission("inventory:write"))
):
    """Create a new category"""
    return service.repo.create_category({
        **category_data.model_dump(),
        'organization_id': organization_id,
        'created_by': current_user.id
    })

# Units
@router.get("/units", response_model=List[UnitResponse])
async def get_units(
    service: InventoryService = Depends(get_inventory_service),
    current_user = Depends(require_permission("inventory:read"))
):
    """Get all units"""
    return service.get_units()

@router.post("/units", response_model=UnitResponse)
async def create_unit(
    unit_data: UnitCreate,
    service: InventoryService = Depends(get_inventory_service),
    current_user = Depends(require_permission("inventory:admin"))
):
    """Create a new unit (admin only)"""
    return service.repo.create_unit({
        **unit_data.model_dump(),
        'created_by': current_user.id
    })

# Products
@router.get("/products", response_model=PaginatedResponse[ProductResponse])
async def get_products(
    category_id: Optional[int] = Query(None),
    q: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=500),
    service: InventoryService = Depends(get_inventory_service),
    organization_id: int = Depends(get_organization_id),
    current_user = Depends(require_permission("inventory:read"))
):
    """Get products with filters and pagination"""
    
    products, total = service.repo.get_products(
        organization_id,
        category_id=category_id,
        q=q,
        is_active=is_active,
        page=page,
        page_size=page_size
    )
    pages = (total + page_size - 1) // page_size
    
    return PaginatedResponse[ProductResponse](
        items=[ProductResponse.model_validate(p) for p in products],
        total=total,
        page=page,
        page_size=page_size,
        pages=pages
    )

@router.post("/products", response_model=ProductResponse)
async def create_product(
    product_data: ProductCreate,
    service: InventoryService = Depends(get_inventory_service),
    organization_id: int = Depends(get_organization_id),
    current_user = Depends(require_permission("inventory:write"))
):
    """Create a new product"""
    return service.repo.create_product({
        **product_data.model_dump(),
        'organization_id': organization_id,
        'created_by': current_user.id
    })

@router.get("/products/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: int,
    service: InventoryService = Depends(get_inventory_service),
    organization_id: int = Depends(get_organization_id),
    current_user = Depends(require_permission("inventory:read"))
):
    """Get product by ID"""
    product = service.repo.get_product_by_id(product_id, organization_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    return ProductResponse.model_validate(product)

@router.put("/products/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: int,
    product_data: ProductUpdate,
    service: InventoryService = Depends(get_inventory_service),
    organization_id: int = Depends(get_organization_id),
    current_user = Depends(require_permission("inventory:write"))
):
    """Update product"""
    product = service.repo.get_product_by_id(product_id, organization_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    updated_product = service.repo.update_product(product, product_data.model_dump(exclude_unset=True))
    return ProductResponse.model_validate(updated_product)

# Locations
@router.get("/locations", response_model=List[LocationResponse])
async def get_locations(
    service: InventoryService = Depends(get_inventory_service),
    organization_id: int = Depends(get_organization_id),
    current_user = Depends(require_permission("inventory:read"))
):
    """Get all locations"""
    return service.get_locations(organization_id)

@router.post("/locations", response_model=LocationResponse)
async def create_location(
    location_data: LocationCreate,
    service: InventoryService = Depends(get_inventory_service),
    organization_id: int = Depends(get_organization_id),
    current_user = Depends(require_permission("inventory:write"))
):
    """Create a new location"""
    return service.repo.create_location({
        **location_data.model_dump(),
        'organization_id': organization_id,
        'created_by': current_user.id
    })

# Movement Reasons
@router.get("/reasons", response_model=List[MovementReasonResponse])
async def get_movement_reasons(
    direction: Optional[str] = Query(None),
    service: InventoryService = Depends(get_inventory_service),
    organization_id: int = Depends(get_organization_id),
    current_user = Depends(require_permission("inventory:read"))
):
    """Get movement reasons"""
    return service.get_movement_reasons(organization_id, direction)

@router.post("/reasons", response_model=MovementReasonResponse)
async def create_movement_reason(
    reason_data: MovementReasonCreate,
    service: InventoryService = Depends(get_inventory_service),
    organization_id: int = Depends(get_organization_id),
    current_user = Depends(require_permission("inventory:write"))
):
    """Create a new movement reason"""
    return service.repo.create_movement_reason({
        **reason_data.model_dump(),
        'organization_id': organization_id,
        'created_by': current_user.id
    })

# ================== UTILITY ENDPOINTS ==================

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "feature": "inventory"}
