"""
Inventory module for stock management
"""

# Simple router import to avoid circular dependencies
try:
    from .api import router as inventory_router
except ImportError:
    # Fallback empty router
    from fastapi import APIRouter
    inventory_router = APIRouter()

__all__ = ["inventory_router"]
