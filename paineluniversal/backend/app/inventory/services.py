"""
Inventory business logic services
"""
import os
from datetime import datetime, date
from decimal import Decimal
from typing import List, Optional, Tuple, Dict, Any
import logging

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status

from app.inventory.repositories import InventoryRepository
from app.inventory.models import MovementTypeEnum, ReasonDirectionEnum
from app.inventory.schemas import (
    StockMovementCreate, StockPositionFilter, MovementHistoryFilter,
    StockPositionResponse, StockMovementResponse
)

logger = logging.getLogger(__name__)

# Configuration
FEATURE_INVENTORY = os.getenv("FEATURE_INVENTORY", "false").lower() == "true"
INVENTORY_BLOCK_NEGATIVE = os.getenv("INVENTORY_BLOCK_NEGATIVE", "true").lower() == "true"


class InventoryService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = InventoryRepository(db)

    def _check_feature_enabled(self):
        """Check if inventory feature is enabled"""
        if not FEATURE_INVENTORY:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Inventory feature is not enabled"
            )

    def _calculate_qty_base(self, qty: Decimal, unit_id: int) -> Decimal:
        """Convert quantity to base unit"""
        unit = self.repo.get_unit_by_id(unit_id)
        if not unit:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Unit {unit_id} not found"
            )
        return qty * unit.factor_to_base

    def _calculate_moving_average_cost(
        self, 
        current_qty: Decimal,
        current_cost: Decimal,
        incoming_qty: Decimal,
        incoming_cost: Decimal
    ) -> Decimal:
        """Calculate moving average cost for inbound movements"""
        if current_qty + incoming_qty == 0:
            return Decimal('0')
        
        total_value = (current_qty * current_cost) + (incoming_qty * incoming_cost)
        total_qty = current_qty + incoming_qty
        return total_value / total_qty

    def _validate_movement_data(self, movement_data: StockMovementCreate, organization_id: int):
        """Validate movement data before processing"""
        
        # Check if reason exists and is compatible
        if movement_data.reason_id:
            reason = self.repo.get_movement_reason_by_id(movement_data.reason_id, organization_id)
            if not reason:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Movement reason not found"
                )
            
            # Check reason direction compatibility
            movement_direction = None
            if movement_data.movement_type in [MovementTypeEnum.IN, MovementTypeEnum.ADJUSTMENT]:
                movement_direction = ReasonDirectionEnum.IN
            elif movement_data.movement_type == MovementTypeEnum.OUT:
                movement_direction = ReasonDirectionEnum.OUT
            
            if movement_direction and reason.direction not in [movement_direction, ReasonDirectionEnum.BOTH]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Reason '{reason.name}' is not compatible with {movement_data.movement_type} movement"
                )

        # Validate locations
        if movement_data.location_from_id:
            location_from = self.repo.get_location_by_id(movement_data.location_from_id, organization_id)
            if not location_from:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Source location not found"
                )

        if movement_data.location_to_id:
            location_to = self.repo.get_location_by_id(movement_data.location_to_id, organization_id)
            if not location_to:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Destination location not found"
                )

        # Validate products and units in lines
        for line in movement_data.lines:
            product = self.repo.get_product_by_id(line.product_id, organization_id, load_relations=False)
            if not product:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Product {line.product_id} not found"
                )
            
            unit = self.repo.get_unit_by_id(line.unit_id)
            if not unit:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Unit {line.unit_id} not found"
                )

    def _check_stock_availability(
        self, 
        organization_id: int,
        product_id: int,
        location_id: int,
        required_qty: Decimal
    ):
        """Check if there's enough stock for outbound movement"""
        if not INVENTORY_BLOCK_NEGATIVE:
            return
        
        stock_level = self.repo.get_stock_level(organization_id, product_id, location_id)
        available_qty = Decimal('0')
        
        if stock_level:
            available_qty = stock_level.on_hand - stock_level.reserved
        
        if available_qty < required_qty:
            product = self.repo.get_product_by_id(product_id, organization_id, load_relations=False)
            location = self.repo.get_location_by_id(location_id, organization_id)
            
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Insufficient stock for product '{product.name}' at location '{location.name}'. "
                       f"Available: {available_qty}, Required: {required_qty}"
            )

    def create_stock_movement(
        self, 
        movement_data: StockMovementCreate,
        organization_id: int,
        user_id: int
    ) -> StockMovementResponse:
        """Create a new stock movement and update stock levels"""
        self._check_feature_enabled()
        
        try:
            # Validate movement data
            self._validate_movement_data(movement_data, organization_id)
            
            # Check for duplicate document_ref
            if movement_data.document_ref:
                existing = self.repo.get_stock_movement_by_document_ref(
                    movement_data.document_ref, organization_id
                )
                if existing:
                    return StockMovementResponse.model_validate(existing)
            
            # Prepare movement header data
            movement_header = {
                'organization_id': organization_id,
                'movement_type': movement_data.movement_type,
                'reason_id': movement_data.reason_id,
                'document_ref': movement_data.document_ref,
                'document_date': movement_data.document_date,
                'location_from_id': movement_data.location_from_id,
                'location_to_id': movement_data.location_to_id,
                'notes': movement_data.notes,
                'created_by': user_id,
                'status': 'completed'
            }
            
            # Prepare movement lines data
            lines_data = []
            for line in movement_data.lines:
                qty_base = self._calculate_qty_base(line.qty, line.unit_id)
                value_total = None
                
                if line.unit_price:
                    value_total = line.qty * line.unit_price
                
                lines_data.append({
                    'product_id': line.product_id,
                    'unit_id': line.unit_id,
                    'qty': line.qty,
                    'unit_price': line.unit_price,
                    'qty_base': qty_base,
                    'value_total': value_total,
                    'notes': line.notes
                })
            
            # For outbound movements, check stock availability first
            if movement_data.movement_type in [MovementTypeEnum.OUT, MovementTypeEnum.TRANSFER]:
                for i, line in enumerate(movement_data.lines):
                    location_id = movement_data.location_from_id
                    if not location_id:
                        continue
                    
                    qty_base = lines_data[i]['qty_base']
                    self._check_stock_availability(
                        organization_id, line.product_id, location_id, qty_base
                    )
            
            # Create movement record
            movement = self.repo.create_stock_movement(movement_header, lines_data)
            
            # Update stock levels
            self._update_stock_levels(movement, organization_id)
            
            # Commit transaction
            self.repo.commit()
            
            # Reload movement with all relations
            movement = self.repo.get_stock_movement_by_id(movement.id, organization_id)
            
            # Log the movement
            logger.info(
                f"Stock movement created: ID={movement.id}, Type={movement.movement_type}, "
                f"Organization={organization_id}, User={user_id}"
            )
            
            return StockMovementResponse.model_validate(movement)
            
        except Exception as e:
            self.repo.rollback()
            logger.error(f"Error creating stock movement: {str(e)}")
            raise

    def _update_stock_levels(self, movement, organization_id: int):
        """Update stock levels based on movement type"""
        
        for line in movement.lines:
            if movement.movement_type == MovementTypeEnum.IN:
                self._process_inbound_line(line, movement.location_to_id, organization_id)
            
            elif movement.movement_type == MovementTypeEnum.OUT:
                self._process_outbound_line(line, movement.location_from_id, organization_id)
            
            elif movement.movement_type == MovementTypeEnum.TRANSFER:
                # Process as outbound from source
                self._process_outbound_line(line, movement.location_from_id, organization_id)
                # Process as inbound to destination (using same cost)
                self._process_transfer_inbound_line(line, movement.location_to_id, organization_id)
            
            elif movement.movement_type == MovementTypeEnum.ADJUSTMENT:
                self._process_adjustment_line(line, movement.location_to_id, organization_id)

    def _process_inbound_line(self, line, location_id: int, organization_id: int):
        """Process inbound movement line - increase stock and update average cost"""
        stock_level = self.repo.get_or_create_stock_level(
            organization_id, line.product_id, location_id, for_update=True
        )
        
        # Calculate new moving average cost if unit price is provided
        new_cost = stock_level.cost_avg
        if line.unit_price:
            new_cost = self._calculate_moving_average_cost(
                stock_level.on_hand,
                stock_level.cost_avg,
                line.qty_base,
                line.unit_price
            )
        
        # Update stock level
        self.repo.update_stock_level(stock_level, line.qty_base, new_cost)

    def _process_outbound_line(self, line, location_id: int, organization_id: int):
        """Process outbound movement line - decrease stock"""
        stock_level = self.repo.get_or_create_stock_level(
            organization_id, line.product_id, location_id, for_update=True
        )
        
        # Calculate CMV (Cost of Goods Sold) using current average cost
        if line.value_total is None:
            line.value_total = line.qty_base * stock_level.cost_avg
        
        # Update stock level
        self.repo.update_stock_level(stock_level, -line.qty_base)

    def _process_transfer_inbound_line(self, line, location_id: int, organization_id: int):
        """Process transfer inbound - use the cost from source location"""
        # Get source stock level to get the cost
        source_stock = self.repo.get_stock_level(
            organization_id, line.product_id, line.movement.location_from_id
        )
        
        transfer_cost = source_stock.cost_avg if source_stock else Decimal('0')
        
        stock_level = self.repo.get_or_create_stock_level(
            organization_id, line.product_id, location_id, for_update=True
        )
        
        # Calculate new moving average cost with transfer cost
        new_cost = self._calculate_moving_average_cost(
            stock_level.on_hand,
            stock_level.cost_avg,
            line.qty_base,
            transfer_cost
        )
        
        # Update stock level
        self.repo.update_stock_level(stock_level, line.qty_base, new_cost)

    def _process_adjustment_line(self, line, location_id: int, organization_id: int):
        """Process inventory adjustment - can be positive or negative"""
        stock_level = self.repo.get_or_create_stock_level(
            organization_id, line.product_id, location_id, for_update=True
        )
        
        # For adjustments, qty_base can be negative
        adjustment_qty = line.qty_base
        
        # If it's a positive adjustment with unit price, update cost
        new_cost = stock_level.cost_avg
        if adjustment_qty > 0 and line.unit_price:
            new_cost = self._calculate_moving_average_cost(
                stock_level.on_hand,
                stock_level.cost_avg,
                adjustment_qty,
                line.unit_price
            )
        
        # Update stock level
        self.repo.update_stock_level(stock_level, adjustment_qty, new_cost)

    def get_stock_position(
        self, 
        organization_id: int,
        filters: StockPositionFilter
    ) -> StockPositionResponse:
        """Get current stock position with filters and pagination"""
        self._check_feature_enabled()
        
        items, total = self.repo.get_stock_position(organization_id, filters)
        
        pages = (total + filters.page_size - 1) // filters.page_size
        
        return StockPositionResponse(
            items=items,
            total=total,
            page=filters.page,
            page_size=filters.page_size,
            pages=pages
        )

    def get_stock_movements(
        self, 
        organization_id: int,
        filters: MovementHistoryFilter
    ) -> Tuple[List[StockMovementResponse], int]:
        """Get stock movements with filters and pagination"""
        self._check_feature_enabled()
        
        movements, total = self.repo.get_stock_movements(organization_id, filters)
        
        movement_responses = []
        for movement in movements:
            movement_responses.append(StockMovementResponse.model_validate(movement))
        
        return movement_responses, total

    def get_stock_movement_by_id(
        self, 
        movement_id: int,
        organization_id: int
    ) -> Optional[StockMovementResponse]:
        """Get stock movement by ID"""
        self._check_feature_enabled()
        
        movement = self.repo.get_stock_movement_by_id(movement_id, organization_id)
        if not movement:
            return None
        
        return StockMovementResponse.model_validate(movement)

    # Catalog methods for autocomplete/dropdowns
    def get_categories(self, organization_id: int, q: Optional[str] = None):
        """Get categories for autocomplete"""
        return self.repo.get_categories(organization_id, is_active=True, q=q)

    def get_units(self, q: Optional[str] = None):
        """Get units for autocomplete"""
        return self.repo.get_units(is_active=True, q=q)

    def get_products(self, organization_id: int, q: Optional[str] = None):
        """Get products for autocomplete"""
        products, _ = self.repo.get_products(
            organization_id, is_active=True, q=q, page_size=100
        )
        return products

    def get_locations(self, organization_id: int, q: Optional[str] = None):
        """Get locations for autocomplete"""
        return self.repo.get_locations(organization_id, is_active=True, q=q)

    def get_movement_reasons(self, organization_id: int, direction: Optional[str] = None):
        """Get movement reasons for dropdowns"""
        direction_enum = None
        if direction:
            direction_enum = ReasonDirectionEnum(direction)
        
        return self.repo.get_movement_reasons(organization_id, direction_enum, is_active=True)
