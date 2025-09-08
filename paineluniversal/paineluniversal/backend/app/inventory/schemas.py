"""
Pydantic schemas for inventory module
"""
from datetime import datetime, date
from decimal import Decimal
from typing import Optional, List, Union, Generic, TypeVar
from enum import Enum

from pydantic import BaseModel, Field, ConfigDict, field_validator

# Generic type for pagination
T = TypeVar('T')

class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response"""
    items: List[T]
    total: int
    page: int
    page_size: int
    pages: int
    
    model_config = ConfigDict(from_attributes=True)


class MovementTypeEnum(str, Enum):
    IN = "IN"
    OUT = "OUT"
    TRANSFER = "TRANSFER"
    ADJUSTMENT = "ADJUSTMENT"


class ReasonDirectionEnum(str, Enum):
    IN = "IN"
    OUT = "OUT"
    BOTH = "BOTH"


class LocationTypeEnum(str, Enum):
    PRINCIPAL = "principal"
    BAR = "bar"
    DEPOSITO = "deposito"


# Base schemas
class CategoryBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    is_active: bool = True


class CategoryCreate(CategoryBase):
    organization_id: int


class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    is_active: Optional[bool] = None


class CategoryResponse(CategoryBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    organization_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None


# Unit schemas
class UnitBase(BaseModel):
    code: str = Field(..., min_length=1, max_length=10)
    name: str = Field(..., min_length=1, max_length=100)
    factor_to_base: Decimal = Field(default=Decimal('1.0'), ge=Decimal('0.000001'))
    is_active: bool = True


class UnitCreate(UnitBase):
    pass


class UnitUpdate(BaseModel):
    code: Optional[str] = Field(None, min_length=1, max_length=10)
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    factor_to_base: Optional[Decimal] = Field(None, ge=Decimal('0.000001'))
    is_active: Optional[bool] = None


class UnitResponse(UnitBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    created_at: datetime


# Product schemas
class ProductBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    sku: Optional[str] = Field(None, max_length=100)
    category_id: int
    base_unit_id: int
    barcode: Optional[str] = Field(None, max_length=100)
    min_stock: Decimal = Field(default=Decimal('0'), ge=Decimal('0'))
    description: Optional[str] = None
    is_active: bool = True


class ProductCreate(ProductBase):
    organization_id: int


class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    sku: Optional[str] = Field(None, max_length=100)
    category_id: Optional[int] = None
    base_unit_id: Optional[int] = None
    barcode: Optional[str] = Field(None, max_length=100)
    min_stock: Optional[Decimal] = Field(None, ge=Decimal('0'))
    description: Optional[str] = None
    is_active: Optional[bool] = None


class ProductResponse(ProductBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    organization_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    category: Optional[CategoryResponse] = None
    base_unit: Optional[UnitResponse] = None


# Location schemas
class LocationBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    type: LocationTypeEnum
    description: Optional[str] = None
    is_active: bool = True


class LocationCreate(LocationBase):
    organization_id: int


class LocationUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    type: Optional[LocationTypeEnum] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class LocationResponse(LocationBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    organization_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None


# Movement Reason schemas
class MovementReasonBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    direction: ReasonDirectionEnum
    affects_cost: bool = True
    accounting_code: Optional[str] = Field(None, max_length=50)
    is_active: bool = True


class MovementReasonCreate(MovementReasonBase):
    organization_id: int


class MovementReasonUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    direction: Optional[ReasonDirectionEnum] = None
    affects_cost: Optional[bool] = None
    accounting_code: Optional[str] = Field(None, max_length=50)
    is_active: Optional[bool] = None


class MovementReasonResponse(MovementReasonBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    organization_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None


# Stock Movement Line schemas
class StockMovementLineBase(BaseModel):
    product_id: int
    unit_id: int
    qty: Decimal = Field(..., gt=Decimal('0'))
    unit_price: Optional[Decimal] = Field(None, ge=Decimal('0'))
    notes: Optional[str] = None


class StockMovementLineCreate(StockMovementLineBase):
    pass


class StockMovementLineResponse(StockMovementLineBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    movement_id: int
    qty_base: Decimal
    value_total: Optional[Decimal] = None
    product: Optional[ProductResponse] = None
    unit: Optional[UnitResponse] = None


# Stock Movement schemas
class StockMovementBase(BaseModel):
    movement_type: MovementTypeEnum
    reason_id: Optional[int] = None
    document_ref: Optional[str] = Field(None, max_length=100)
    document_date: date
    location_from_id: Optional[int] = None
    location_to_id: Optional[int] = None
    notes: Optional[str] = None


class StockMovementCreate(StockMovementBase):
    organization_id: int
    lines: List[StockMovementLineCreate] = Field(..., min_length=1)

    @field_validator('lines')
    @classmethod
    def validate_lines(cls, v):
        if not v:
            raise ValueError('At least one line is required')
        return v

    @field_validator('reason_id')
    @classmethod
    def validate_reason_for_adjustment(cls, v, info):
        if info.data.get('movement_type') == MovementTypeEnum.ADJUSTMENT and not v:
            raise ValueError('Reason is required for adjustment movements')
        return v

    @field_validator('location_from_id', 'location_to_id')
    @classmethod
    def validate_locations(cls, v, info):
        movement_type = info.data.get('movement_type')
        field_name = info.field_name
        
        if movement_type == MovementTypeEnum.TRANSFER:
            if field_name == 'location_from_id' and not v:
                raise ValueError('Source location is required for transfer')
            if field_name == 'location_to_id' and not v:
                raise ValueError('Destination location is required for transfer')
        elif movement_type == MovementTypeEnum.OUT:
            if field_name == 'location_from_id' and not v:
                raise ValueError('Source location is required for outbound movement')
        elif movement_type == MovementTypeEnum.IN:
            if field_name == 'location_to_id' and not v:
                raise ValueError('Destination location is required for inbound movement')
        
        return v


class StockMovementUpdate(BaseModel):
    notes: Optional[str] = None
    status: Optional[str] = None


class StockMovementResponse(StockMovementBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    organization_id: int
    created_by: int
    created_at: datetime
    status: str
    lines: List[StockMovementLineResponse] = []
    reason: Optional[MovementReasonResponse] = None
    location_from: Optional[LocationResponse] = None
    location_to: Optional[LocationResponse] = None


# Stock Level schemas
class StockLevelResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    organization_id: int
    product_id: int
    location_id: int
    on_hand: Decimal
    reserved: Decimal
    cost_avg: Decimal
    updated_at: datetime
    product: Optional[ProductResponse] = None
    location: Optional[LocationResponse] = None
    
    @property
    def available(self) -> Decimal:
        return self.on_hand - self.reserved
    
    @property
    def value_total(self) -> Decimal:
        return self.on_hand * self.cost_avg
    
    @property
    def is_below_min_stock(self) -> bool:
        return self.product and self.on_hand < self.product.min_stock


# Position/Report schemas
class StockPositionFilter(BaseModel):
    q: Optional[str] = None  # Search term
    category_id: Optional[int] = None
    location_id: Optional[int] = None
    as_of: Optional[date] = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=50, ge=1, le=1000)
    order_by: str = Field(default="product_name")
    order_dir: str = Field(default="asc", pattern="^(asc|desc)$")
    below_min_stock: Optional[bool] = None


class StockPositionItem(BaseModel):
    product_id: int
    product_name: str
    product_sku: Optional[str] = None
    product_barcode: Optional[str] = None
    category_name: str
    location_id: int
    location_name: str
    location_type: LocationTypeEnum
    base_unit_code: str
    base_unit_name: str
    on_hand: Decimal
    reserved: Decimal
    available: Decimal
    cost_avg: Decimal
    value_total: Decimal
    min_stock: Decimal
    is_below_min_stock: bool
    updated_at: datetime


class StockPositionResponse(BaseModel):
    items: List[StockPositionItem]
    total: int
    page: int
    page_size: int
    pages: int


# Movement history filters
class MovementHistoryFilter(BaseModel):
    movement_type: Optional[MovementTypeEnum] = None
    reason_id: Optional[int] = None
    location_from_id: Optional[int] = None
    location_to_id: Optional[int] = None
    product_id: Optional[int] = None
    document_ref: Optional[str] = None
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    created_by: Optional[int] = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=50, ge=1, le=1000)
    order_by: str = Field(default="created_at")
    order_dir: str = Field(default="desc", pattern="^(asc|desc)$")


# Error responses
class InventoryError(BaseModel):
    error: str
    message: str
    details: Optional[dict] = None


class ValidationError(BaseModel):
    field: str
    message: str
