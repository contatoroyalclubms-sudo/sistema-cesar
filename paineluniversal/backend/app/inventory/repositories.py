"""
Repository layer for inventory operations
"""
from datetime import datetime, date
from decimal import Decimal
from typing import List, Optional, Tuple, Dict, Any
from sqlalchemy import and_, or_, desc, asc, func, select, text
from sqlalchemy.orm import Session, joinedload, selectinload
from sqlalchemy.exc import IntegrityError

from app.inventory.models import (
    Category, Unit, Product, Location, MovementReason,
    StockMovement, StockMovementLine, StockLevel,
    MovementTypeEnum, ReasonDirectionEnum, LocationTypeEnum
)
from app.inventory.schemas import (
    StockPositionFilter, MovementHistoryFilter, StockPositionItem
)


class InventoryRepository:
    def __init__(self, db: Session):
        self.db = db

    # Category operations
    def get_categories(
        self, 
        organization_id: int, 
        is_active: Optional[bool] = None,
        q: Optional[str] = None
    ) -> List[Category]:
        query = self.db.query(Category).filter(Category.organization_id == organization_id)
        
        if is_active is not None:
            query = query.filter(Category.is_active == is_active)
        
        if q:
            query = query.filter(Category.name.ilike(f"%{q}%"))
        
        return query.order_by(Category.name).all()

    def get_category_by_id(self, category_id: int, organization_id: int) -> Optional[Category]:
        return self.db.query(Category).filter(
            Category.id == category_id,
            Category.organization_id == organization_id
        ).first()

    def create_category(self, category_data: dict) -> Category:
        category = Category(**category_data)
        self.db.add(category)
        self.db.flush()
        return category

    def update_category(self, category: Category, update_data: dict) -> Category:
        for field, value in update_data.items():
            if hasattr(category, field):
                setattr(category, field, value)
        self.db.flush()
        return category

    def delete_category(self, category: Category) -> None:
        self.db.delete(category)
        self.db.flush()

    # Unit operations
    def get_units(self, is_active: Optional[bool] = None, q: Optional[str] = None) -> List[Unit]:
        query = self.db.query(Unit)
        
        if is_active is not None:
            query = query.filter(Unit.is_active == is_active)
        
        if q:
            query = query.filter(or_(
                Unit.code.ilike(f"%{q}%"),
                Unit.name.ilike(f"%{q}%")
            ))
        
        return query.order_by(Unit.name).all()

    def get_unit_by_id(self, unit_id: int) -> Optional[Unit]:
        return self.db.query(Unit).filter(Unit.id == unit_id).first()

    def get_unit_by_code(self, code: str) -> Optional[Unit]:
        return self.db.query(Unit).filter(Unit.code == code).first()

    def create_unit(self, unit_data: dict) -> Unit:
        unit = Unit(**unit_data)
        self.db.add(unit)
        self.db.flush()
        return unit

    def update_unit(self, unit: Unit, update_data: dict) -> Unit:
        for field, value in update_data.items():
            if hasattr(unit, field):
                setattr(unit, field, value)
        self.db.flush()
        return unit

    # Product operations
    def get_products(
        self, 
        organization_id: int,
        category_id: Optional[int] = None,
        is_active: Optional[bool] = None,
        q: Optional[str] = None,
        page: int = 1,
        page_size: int = 50
    ) -> Tuple[List[Product], int]:
        query = self.db.query(Product).filter(Product.organization_id == organization_id)
        
        if category_id:
            query = query.filter(Product.category_id == category_id)
        
        if is_active is not None:
            query = query.filter(Product.is_active == is_active)
        
        if q:
            query = query.filter(or_(
                Product.name.ilike(f"%{q}%"),
                Product.sku.ilike(f"%{q}%"),
                Product.barcode.ilike(f"%{q}%")
            ))
        
        # Count total
        total = query.count()
        
        # Apply pagination
        offset = (page - 1) * page_size
        products = query.options(
            joinedload(Product.category),
            joinedload(Product.base_unit)
        ).order_by(Product.name).offset(offset).limit(page_size).all()
        
        return products, total

    def get_product_by_id(
        self, 
        product_id: int, 
        organization_id: int,
        load_relations: bool = True
    ) -> Optional[Product]:
        query = self.db.query(Product).filter(
            Product.id == product_id,
            Product.organization_id == organization_id
        )
        
        if load_relations:
            query = query.options(
                joinedload(Product.category),
                joinedload(Product.base_unit)
            )
        
        return query.first()

    def get_product_by_sku(self, sku: str, organization_id: int) -> Optional[Product]:
        return self.db.query(Product).filter(
            Product.sku == sku,
            Product.organization_id == organization_id
        ).first()

    def get_product_by_barcode(self, barcode: str, organization_id: int) -> Optional[Product]:
        return self.db.query(Product).filter(
            Product.barcode == barcode,
            Product.organization_id == organization_id
        ).first()

    def create_product(self, product_data: dict) -> Product:
        product = Product(**product_data)
        self.db.add(product)
        self.db.flush()
        return product

    def update_product(self, product: Product, update_data: dict) -> Product:
        for field, value in update_data.items():
            if hasattr(product, field):
                setattr(product, field, value)
        self.db.flush()
        return product

    # Location operations
    def get_locations(
        self, 
        organization_id: int,
        location_type: Optional[LocationTypeEnum] = None,
        is_active: Optional[bool] = None,
        q: Optional[str] = None
    ) -> List[Location]:
        query = self.db.query(Location).filter(Location.organization_id == organization_id)
        
        if location_type:
            query = query.filter(Location.type == location_type)
        
        if is_active is not None:
            query = query.filter(Location.is_active == is_active)
        
        if q:
            query = query.filter(Location.name.ilike(f"%{q}%"))
        
        return query.order_by(Location.name).all()

    def get_location_by_id(self, location_id: int, organization_id: int) -> Optional[Location]:
        return self.db.query(Location).filter(
            Location.id == location_id,
            Location.organization_id == organization_id
        ).first()

    def create_location(self, location_data: dict) -> Location:
        location = Location(**location_data)
        self.db.add(location)
        self.db.flush()
        return location

    def update_location(self, location: Location, update_data: dict) -> Location:
        for field, value in update_data.items():
            if hasattr(location, field):
                setattr(location, field, value)
        self.db.flush()
        return location

    # Movement Reason operations
    def get_movement_reasons(
        self, 
        organization_id: int,
        direction: Optional[ReasonDirectionEnum] = None,
        is_active: Optional[bool] = None
    ) -> List[MovementReason]:
        query = self.db.query(MovementReason).filter(
            MovementReason.organization_id == organization_id
        )
        
        if direction:
            query = query.filter(or_(
                MovementReason.direction == direction,
                MovementReason.direction == ReasonDirectionEnum.BOTH
            ))
        
        if is_active is not None:
            query = query.filter(MovementReason.is_active == is_active)
        
        return query.order_by(MovementReason.name).all()

    def get_movement_reason_by_id(
        self, 
        reason_id: int, 
        organization_id: int
    ) -> Optional[MovementReason]:
        return self.db.query(MovementReason).filter(
            MovementReason.id == reason_id,
            MovementReason.organization_id == organization_id
        ).first()

    def create_movement_reason(self, reason_data: dict) -> MovementReason:
        reason = MovementReason(**reason_data)
        self.db.add(reason)
        self.db.flush()
        return reason

    def update_movement_reason(self, reason: MovementReason, update_data: dict) -> MovementReason:
        for field, value in update_data.items():
            if hasattr(reason, field):
                setattr(reason, field, value)
        self.db.flush()
        return reason

    # Stock Movement operations
    def get_stock_movements(
        self, 
        organization_id: int,
        filters: MovementHistoryFilter
    ) -> Tuple[List[StockMovement], int]:
        query = self.db.query(StockMovement).filter(
            StockMovement.organization_id == organization_id
        )
        
        # Apply filters
        if filters.movement_type:
            query = query.filter(StockMovement.movement_type == filters.movement_type)
        
        if filters.reason_id:
            query = query.filter(StockMovement.reason_id == filters.reason_id)
        
        if filters.location_from_id:
            query = query.filter(StockMovement.location_from_id == filters.location_from_id)
        
        if filters.location_to_id:
            query = query.filter(StockMovement.location_to_id == filters.location_to_id)
        
        if filters.document_ref:
            query = query.filter(StockMovement.document_ref.ilike(f"%{filters.document_ref}%"))
        
        if filters.date_from:
            query = query.filter(StockMovement.document_date >= filters.date_from)
        
        if filters.date_to:
            query = query.filter(StockMovement.document_date <= filters.date_to)
        
        if filters.created_by:
            query = query.filter(StockMovement.created_by == filters.created_by)
        
        # Filter by product in lines
        if filters.product_id:
            query = query.join(StockMovementLine).filter(
                StockMovementLine.product_id == filters.product_id
            )
        
        # Count total
        total = query.count()
        
        # Apply ordering
        order_column = getattr(StockMovement, filters.order_by, StockMovement.created_at)
        if filters.order_dir == "desc":
            order_column = desc(order_column)
        else:
            order_column = asc(order_column)
        
        # Apply pagination
        offset = (filters.page - 1) * filters.page_size
        movements = query.options(
            selectinload(StockMovement.lines).selectinload(StockMovementLine.product),
            selectinload(StockMovement.lines).selectinload(StockMovementLine.unit),
            joinedload(StockMovement.reason),
            joinedload(StockMovement.location_from),
            joinedload(StockMovement.location_to)
        ).order_by(order_column).offset(offset).limit(filters.page_size).all()
        
        return movements, total

    def get_stock_movement_by_id(
        self, 
        movement_id: int, 
        organization_id: int
    ) -> Optional[StockMovement]:
        return self.db.query(StockMovement).filter(
            StockMovement.id == movement_id,
            StockMovement.organization_id == organization_id
        ).options(
            selectinload(StockMovement.lines).selectinload(StockMovementLine.product),
            selectinload(StockMovement.lines).selectinload(StockMovementLine.unit),
            joinedload(StockMovement.reason),
            joinedload(StockMovement.location_from),
            joinedload(StockMovement.location_to)
        ).first()

    def get_stock_movement_by_document_ref(
        self, 
        document_ref: str, 
        organization_id: int
    ) -> Optional[StockMovement]:
        return self.db.query(StockMovement).filter(
            StockMovement.document_ref == document_ref,
            StockMovement.organization_id == organization_id
        ).first()

    def create_stock_movement(self, movement_data: dict, lines_data: List[dict]) -> StockMovement:
        # Create movement header
        movement = StockMovement(**movement_data)
        self.db.add(movement)
        self.db.flush()  # Get the ID
        
        # Create movement lines
        for line_data in lines_data:
            line_data['movement_id'] = movement.id
            line = StockMovementLine(**line_data)
            self.db.add(line)
        
        self.db.flush()
        return movement

    def update_stock_movement(self, movement: StockMovement, update_data: dict) -> StockMovement:
        for field, value in update_data.items():
            if hasattr(movement, field):
                setattr(movement, field, value)
        self.db.flush()
        return movement

    # Stock Level operations
    def get_stock_level(
        self, 
        organization_id: int,
        product_id: int,
        location_id: int,
        for_update: bool = False
    ) -> Optional[StockLevel]:
        query = self.db.query(StockLevel).filter(
            StockLevel.organization_id == organization_id,
            StockLevel.product_id == product_id,
            StockLevel.location_id == location_id
        )
        
        if for_update:
            query = query.with_for_update()
        
        return query.first()

    def get_or_create_stock_level(
        self, 
        organization_id: int,
        product_id: int,
        location_id: int,
        for_update: bool = True
    ) -> StockLevel:
        stock_level = self.get_stock_level(
            organization_id, product_id, location_id, for_update
        )
        
        if not stock_level:
            stock_level = StockLevel(
                organization_id=organization_id,
                product_id=product_id,
                location_id=location_id,
                on_hand=Decimal('0'),
                reserved=Decimal('0'),
                cost_avg=Decimal('0')
            )
            self.db.add(stock_level)
            self.db.flush()
        
        return stock_level

    def update_stock_level(
        self, 
        stock_level: StockLevel,
        qty_change: Decimal,
        new_cost: Optional[Decimal] = None
    ) -> StockLevel:
        """Update stock level with quantity change and optional cost update"""
        stock_level.on_hand += qty_change
        
        if new_cost is not None:
            stock_level.cost_avg = new_cost
        
        stock_level.updated_at = datetime.utcnow()
        self.db.flush()
        return stock_level

    def get_stock_position(
        self, 
        organization_id: int,
        filters: StockPositionFilter
    ) -> Tuple[List[StockPositionItem], int]:
        """Get current stock position with filters and pagination"""
        
        # Base query with joins
        query = (
            self.db.query(
                StockLevel.product_id,
                Product.name.label('product_name'),
                Product.sku.label('product_sku'),
                Product.barcode.label('product_barcode'),
                Category.name.label('category_name'),
                StockLevel.location_id,
                Location.name.label('location_name'),
                Location.type.label('location_type'),
                Unit.code.label('base_unit_code'),
                Unit.name.label('base_unit_name'),
                StockLevel.on_hand,
                StockLevel.reserved,
                (StockLevel.on_hand - StockLevel.reserved).label('available'),
                StockLevel.cost_avg,
                (StockLevel.on_hand * StockLevel.cost_avg).label('value_total'),
                Product.min_stock,
                (StockLevel.on_hand < Product.min_stock).label('is_below_min_stock'),
                StockLevel.updated_at
            )
            .join(Product, StockLevel.product_id == Product.id)
            .join(Category, Product.category_id == Category.id)
            .join(Location, StockLevel.location_id == Location.id)
            .join(Unit, Product.base_unit_id == Unit.id)
            .filter(StockLevel.organization_id == organization_id)
        )
        
        # Apply filters
        if filters.q:
            search_term = f"%{filters.q}%"
            query = query.filter(or_(
                Product.name.ilike(search_term),
                Product.sku.ilike(search_term),
                Product.barcode.ilike(search_term),
                Category.name.ilike(search_term)
            ))
        
        if filters.category_id:
            query = query.filter(Product.category_id == filters.category_id)
        
        if filters.location_id:
            query = query.filter(StockLevel.location_id == filters.location_id)
        
        if filters.below_min_stock:
            query = query.filter(StockLevel.on_hand < Product.min_stock)
        
        # Count total
        total = query.count()
        
        # Apply ordering
        order_map = {
            'product_name': Product.name,
            'category_name': Category.name,
            'location_name': Location.name,
            'on_hand': StockLevel.on_hand,
            'value_total': (StockLevel.on_hand * StockLevel.cost_avg),
            'updated_at': StockLevel.updated_at
        }
        
        order_column = order_map.get(filters.order_by, Product.name)
        if filters.order_dir == "desc":
            order_column = desc(order_column)
        
        # Apply pagination
        offset = (filters.page - 1) * filters.page_size
        results = query.order_by(order_column).offset(offset).limit(filters.page_size).all()
        
        # Convert to response objects
        items = []
        for row in results:
            items.append(StockPositionItem(
                product_id=row.product_id,
                product_name=row.product_name,
                product_sku=row.product_sku,
                product_barcode=row.product_barcode,
                category_name=row.category_name,
                location_id=row.location_id,
                location_name=row.location_name,
                location_type=row.location_type,
                base_unit_code=row.base_unit_code,
                base_unit_name=row.base_unit_name,
                on_hand=row.on_hand,
                reserved=row.reserved,
                available=row.available,
                cost_avg=row.cost_avg,
                value_total=row.value_total,
                min_stock=row.min_stock,
                is_below_min_stock=row.is_below_min_stock,
                updated_at=row.updated_at
            ))
        
        return items, total

    def commit(self) -> None:
        """Commit the current transaction"""
        self.db.commit()

    def rollback(self) -> None:
        """Rollback the current transaction"""
        self.db.rollback()
