from decimal import Decimal
from typing import Optional, List, Tuple
from datetime import datetime
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.db.models import (
    Caja,
    TurnoCaja,
    Usuario,
    DenominacionEfectivo,
    CierreCajaCiegas,
    DetalleArqueoEfectivo,
    Venta,
    PagoVenta,
    MovimientoCaja,
)
from app.interfaces.repositories import CajaRepository, TurnoCajaRepository

_TURNO_LOADS = (
    selectinload(TurnoCaja.caja),
    selectinload(TurnoCaja.usuario),
)


class CajaRepositoryImpl(CajaRepository):
    """Acceso a datos async para Caja. No hace commit: el Unit of Work controla la transacción."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, caja_id: int) -> Optional[Caja]:
        result = await self.db.execute(
            select(Caja).where(Caja.id_caja == caja_id)
        )
        return result.scalar_one_or_none()

    async def list_all(self, include_inactive: bool = False) -> List[Caja]:
        stmt = select(Caja)
        if not include_inactive:
            stmt = stmt.where(Caja.estado.in_(["Activa", "Activo"]))
        stmt = stmt.order_by(Caja.id_caja.asc())
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def create(self, caja: Caja) -> Caja:
        self.db.add(caja)
        await self.db.flush()
        await self.db.refresh(caja)
        return caja

    async def update(self, caja: Caja) -> Caja:
        await self.db.flush()
        await self.db.refresh(caja)
        return caja


class TurnoCajaRepositoryImpl(TurnoCajaRepository):
    """Acceso a datos async para TurnoCaja. Carga ansiosa de `caja` y `usuario` para evitar MissingGreenlet.
    No hace commit: el Unit of Work controla la transacción."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, turno_id: int) -> Optional[TurnoCaja]:
        result = await self.db.execute(
            select(TurnoCaja).options(*_TURNO_LOADS).where(TurnoCaja.id_turno == turno_id)
        )
        return result.scalar_one_or_none()

    async def get_active_by_user(self, user_id: int) -> Optional[TurnoCaja]:
        result = await self.db.execute(
            select(TurnoCaja)
            .options(*_TURNO_LOADS)
            .where(
                TurnoCaja.id_usuario == user_id,
                TurnoCaja.estado.in_(["Abierto", "Abierta"]),
            )
        )
        return result.scalar_one_or_none()

    async def get_active_by_caja(self, caja_id: int) -> Optional[TurnoCaja]:
        result = await self.db.execute(
            select(TurnoCaja)
            .options(*_TURNO_LOADS)
            .where(
                TurnoCaja.id_caja == caja_id,
                TurnoCaja.estado.in_(["Abierto", "Abierta"]),
            )
        )
        return result.scalar_one_or_none()

    def _build_filters(
        self,
        fecha_desde: Optional[datetime] = None,
        fecha_hasta: Optional[datetime] = None,
        estado: Optional[str] = None,
        id_caja: Optional[int] = None,
        id_usuario: Optional[int] = None,
    ):
        conditions = []
        if fecha_desde is not None:
            conditions.append(TurnoCaja.fecha_apertura >= fecha_desde)
        if fecha_hasta is not None:
            conditions.append(TurnoCaja.fecha_apertura <= fecha_hasta)
        if estado:
            # Soporta normalización de Abierto/Abierta y Cerrado/Cerrada
            if estado.lower() in ("abierto", "abierta"):
                conditions.append(TurnoCaja.estado.in_(["Abierto", "Abierta"]))
            elif estado.lower() in ("cerrado", "cerrada"):
                conditions.append(TurnoCaja.estado.in_(["Cerrado", "Cerrada"]))
            else:
                conditions.append(TurnoCaja.estado == estado)
        if id_caja is not None:
            conditions.append(TurnoCaja.id_caja == id_caja)
        if id_usuario is not None:
            conditions.append(TurnoCaja.id_usuario == id_usuario)
        return conditions

    _SORTABLE = {
        "id_turno": TurnoCaja.id_turno,
        "monto_apertura": TurnoCaja.monto_apertura,
        "monto_cierre": TurnoCaja.monto_cierre,
        "fecha_apertura": TurnoCaja.fecha_apertura,
        "fecha_cierre": TurnoCaja.fecha_cierre,
        "estado": TurnoCaja.estado,
        "caja": Caja.descripcion,
        "usuario": Usuario.nombre_completo,
    }

    async def search(
        self,
        fecha_desde=None,
        fecha_hasta=None,
        estado: Optional[str] = None,
        id_caja: Optional[int] = None,
        id_usuario: Optional[int] = None,
        sort_by: Optional[str] = None,
        sort_dir: str = "desc",
        limit: int = 10,
        offset: int = 0,
    ) -> List[TurnoCaja]:
        conditions = self._build_filters(fecha_desde, fecha_hasta, estado, id_caja, id_usuario)
        stmt = select(TurnoCaja).options(*_TURNO_LOADS)

        if sort_by == "caja":
            stmt = stmt.join(TurnoCaja.caja)
        elif sort_by == "usuario":
            stmt = stmt.join(TurnoCaja.usuario)

        if conditions:
            stmt = stmt.where(*conditions)

        column = self._SORTABLE.get(sort_by, TurnoCaja.id_turno)
        if sort_dir == "desc":
            stmt = stmt.order_by(column.desc())
        else:
            stmt = stmt.order_by(column.asc())

        stmt = stmt.limit(limit).offset(offset)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def count_search(
        self,
        fecha_desde=None,
        fecha_hasta=None,
        estado: Optional[str] = None,
        id_caja: Optional[int] = None,
        id_usuario: Optional[int] = None,
    ) -> int:
        conditions = self._build_filters(fecha_desde, fecha_hasta, estado, id_caja, id_usuario)
        stmt = select(func.count()).select_from(TurnoCaja)
        if conditions:
            stmt = stmt.where(*conditions)
        result = await self.db.execute(stmt)
        return result.scalar_one()

    async def create(self, turno: TurnoCaja) -> TurnoCaja:
        self.db.add(turno)
        await self.db.flush()
        await self.db.refresh(turno)
        return turno

    async def update(self, turno: TurnoCaja) -> TurnoCaja:
        await self.db.flush()
        await self.db.refresh(turno)
        return turno

    async def get_denominaciones(self) -> List[DenominacionEfectivo]:
        stmt = select(DenominacionEfectivo).order_by(DenominacionEfectivo.valor.asc())
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_denominacion_by_id(self, id_denominacion: int) -> Optional[DenominacionEfectivo]:
        stmt = select(DenominacionEfectivo).where(DenominacionEfectivo.id_denominacion == id_denominacion)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_efectivo_ventas_turno(self, id_turno: int) -> Decimal:
        """Calcula el total neto en efectivo cobrado en las ventas del turno.
        (monto_recibido - vuelto_entregado) para método de pago en efectivo (id=1)."""
        stmt = (
            select(func.coalesce(func.sum(PagoVenta.monto_recibido - PagoVenta.vuelto_entregado), 0))
            .select_from(PagoVenta)
            .join(Venta, PagoVenta.id_venta == Venta.id_venta)
            .where(
                Venta.id_turno == id_turno,
                Venta.estado != "Anulada",
                PagoVenta.id_metodo_pago == 1,
            )
        )
        result = await self.db.execute(stmt)
        return Decimal(str(result.scalar_one()))

    async def get_movimientos_caja_turno(self, id_turno: int) -> Tuple[Decimal, Decimal]:
        """Calcula (total_entradas, total_salidas) de movimientos de caja para el turno."""
        # Suponiendo tipo_movimiento 1=Entrada, 2=Salida o según convención
        stmt_in = (
            select(func.coalesce(func.sum(MovimientoCaja.monto), 0))
            .select_from(MovimientoCaja)
            .where(MovimientoCaja.id_turno == id_turno, MovimientoCaja.id_tipo_movimiento == 1)
        )
        stmt_out = (
            select(func.coalesce(func.sum(MovimientoCaja.monto), 0))
            .select_from(MovimientoCaja)
            .where(MovimientoCaja.id_turno == id_turno, MovimientoCaja.id_tipo_movimiento == 2)
        )
        res_in = await self.db.execute(stmt_in)
        res_out = await self.db.execute(stmt_out)
        return Decimal(str(res_in.scalar_one())), Decimal(str(res_out.scalar_one()))

    async def create_cierre_ciegas(
        self, cierre: CierreCajaCiegas, detalles: List[DetalleArqueoEfectivo]
    ) -> CierreCajaCiegas:
        self.db.add(cierre)
        await self.db.flush()
        await self.db.refresh(cierre)

        for det in detalles:
            det.id_cierre = cierre.id_cierre
            self.db.add(det)

        await self.db.flush()
        return cierre

    async def get_cierre_ciegas_by_id(self, id_cierre: int) -> Optional[CierreCajaCiegas]:
        stmt = (
            select(CierreCajaCiegas)
            .options(
                selectinload(CierreCajaCiegas.detalles_arqueo).selectinload(DetalleArqueoEfectivo.denominacion),
                selectinload(CierreCajaCiegas.turno),
            )
            .where(CierreCajaCiegas.id_cierre == id_cierre)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

