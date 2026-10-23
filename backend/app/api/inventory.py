from fastapi import APIRouter, Depends, Query
from typing import List, Optional
from app.api.deps import get_inventory_service, get_current_user, require_permission
from app.schemas.inventory_schema import InventoryResponse, InventoryUpdate, StockAdjustment, AlertaStockResponse
from app.services.inventory_service import ConcreteInventoryService
from app.db.models import Usuario

router = APIRouter(prefix="/api/inventory", tags=["Inventario"])

@router.get("/", response_model=List[InventoryResponse])
async def list_inventory(
    id_sucursal: Optional[int] = Query(None),
    low_stock_only: bool = Query(False),
    current_user: Usuario = Depends(require_permission("INV_VER")),
    service: ConcreteInventoryService = Depends(get_inventory_service)
):
    return await service.get_all_inventory(id_sucursal=id_sucursal, low_stock_only=low_stock_only)

@router.put("/{id_inventario}", response_model=InventoryResponse)
async def update_inventory(
    id_inventario: int,
    payload: InventoryUpdate,
    current_user: Usuario = Depends(require_permission("INV_MODIFICAR")),
    service: ConcreteInventoryService = Depends(get_inventory_service)
):
    return await service.update_inventory(id_inventario, payload, current_user)

@router.post("/{id_inventario}/adjust", response_model=InventoryResponse)
async def adjust_stock(
    id_inventario: int,
    payload: StockAdjustment,
    current_user: Usuario = Depends(require_permission("INV_AJUSTAR_STOCK")),
    service: ConcreteInventoryService = Depends(get_inventory_service)
):
    return await service.adjust_stock(id_inventario, payload, current_user)

@router.get("/alerts", response_model=List[AlertaStockResponse])
async def list_alerts(
    id_sucursal: Optional[int] = Query(None),
    current_user: Usuario = Depends(require_permission("INV_VER_ALERTAS")),
    service: ConcreteInventoryService = Depends(get_inventory_service)
):
    return await service.get_alerts(id_sucursal=id_sucursal)


# ============================================================================
# Campanita de notificaciones: alertas de stock pendientes para cualquier
# usuario autenticado (el badge del header es global, no depende de permisos).
# ============================================================================
inventario_router = APIRouter(prefix="/api/inventario", tags=["Inventario"])


@inventario_router.get("/alertas", response_model=List[AlertaStockResponse])
async def list_alertas_pendientes(
    current_user: Usuario = Depends(get_current_user),
    service: ConcreteInventoryService = Depends(get_inventory_service)
):
    """Devuelve las alertas de stock con estado 'Pendiente', enriquecidas con
    el nombre del producto y el código de barras (JOIN vía inventario_sucursal
    → variante_producto → producto). Se usa para el badge de notificaciones."""
    return await service.get_alerts()


@inventario_router.put("/alertas/{id_alerta}/atender", response_model=AlertaStockResponse)
async def atender_alerta_inventario(
    id_alerta: int,
    current_user: Usuario = Depends(require_permission("INV_INGRESAR_MERCADERIA")),
    service: ConcreteInventoryService = Depends(get_inventory_service),
):
    """Marca una alerta de stock como 'Atendida' registrando el evento en bitácora (INV_INGRESAR_MERCADERIA)."""
    return await service.atender_alerta(id_alerta, current_user)


@router.put("/alerts/{id_alerta}/atender", response_model=AlertaStockResponse)
async def atender_alerta_inventory(
    id_alerta: int,
    current_user: Usuario = Depends(require_permission("INV_INGRESAR_MERCADERIA")),
    service: ConcreteInventoryService = Depends(get_inventory_service),
):
    """Alias para marcar una alerta como 'Atendida'."""
    return await service.atender_alerta(id_alerta, current_user)
