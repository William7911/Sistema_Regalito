from datetime import date, datetime, time, timedelta
from decimal import Decimal
from typing import Dict, List, Optional, Tuple

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models import (
    Categoria,
    Cliente,
    ClienteContacto,
    Compra,
    DetalleMerma,
    DetalleVenta,
    InventarioSucursal,
    Merma,
    Municipio,
    Producto,
    Subcategoria,
    Usuario,
    VarianteProducto,
    Venta,
)

GUATEMALA_OFFSET = timedelta(hours=6)


def _rango_utc(inicio: date, fin: date) -> Tuple[datetime, datetime]:
    """Convierte un par de fechas locales (America/Guatemala, UTC-6) al rango
    UTC [inicio, fin] que las ventas usan en la base de datos.

    Los timestamps se guardan en UTC; el día calendario local comienza a las
    06:00 UTC (00:00 - 06:00) y termina a las 06:00 UTC del día siguiente.
    Se reutiliza la misma convención que dashboard_repository para que los
    totales del panel y los del módulo de reportes coincidan.
    """
    dt_inicio = datetime.combine(inicio, time.min) + GUATEMALA_OFFSET
    dt_fin = datetime.combine(fin, time.max) + GUATEMALA_OFFSET
    return dt_inicio, dt_fin


class ReporteRepositoryImpl:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_ventas_by_date(self, inicio: date, fin: date) -> List[Venta]:
        dt_inicio, dt_fin = _rango_utc(inicio, fin)
        stmt = (
            select(Venta)
            .options(selectinload(Venta.usuario))
            .where(Venta.fecha_venta >= dt_inicio, Venta.fecha_venta <= dt_fin)
            .order_by(Venta.fecha_venta.desc())
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_mermas_by_date(self, inicio: date, fin: date) -> List[Merma]:
        dt_inicio, dt_fin = _rango_utc(inicio, fin)
        stmt = (
            select(Merma)
            .options(
                selectinload(Merma.detalles),
                selectinload(Merma.usuario),
            )
            .where(Merma.fecha_merma >= dt_inicio, Merma.fecha_merma <= dt_fin)
            .order_by(Merma.fecha_merma.desc())
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_compras_by_date(self, inicio: date, fin: date) -> List[Compra]:
        stmt = (
            select(Compra)
            .options(
                selectinload(Compra.proveedor),
                selectinload(Compra.usuario),
            )
            .where(Compra.fecha_ingreso >= inicio, Compra.fecha_ingreso <= fin)
            .order_by(Compra.fecha_ingreso.desc())
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    # ---------------------------------------------------------------------------
    # Consultas para Reportes de Usuarios y Clientes
    # ---------------------------------------------------------------------------

    async def get_usuarios_reporte(
        self,
        estado: Optional[str] = None,
        fecha_desde: Optional[date] = None,
        fecha_hasta: Optional[date] = None,
    ) -> List[Usuario]:
        stmt = (
            select(Usuario)
            .options(selectinload(Usuario.rol))
            .order_by(Usuario.id_usuario.asc())
        )
        if estado:
            stmt = stmt.where(func.lower(Usuario.estado) == func.lower(estado))
        if fecha_desde:
            stmt = stmt.where(Usuario.fecha_creacion >= datetime.combine(fecha_desde, time.min))
        if fecha_hasta:
            stmt = stmt.where(Usuario.fecha_creacion <= datetime.combine(fecha_hasta, time.max))

        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_usuario_by_id(self, id_usuario: int) -> Optional[Usuario]:
        stmt = (
            select(Usuario)
            .options(selectinload(Usuario.rol))
            .where(Usuario.id_usuario == id_usuario)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_clientes_reporte(
        self,
        estado: Optional[str] = None,
        fecha_desde: Optional[date] = None,
        fecha_hasta: Optional[date] = None,
    ) -> List[Cliente]:
        stmt = (
            select(Cliente)
            .options(
                selectinload(Cliente.tipo_cliente),
                selectinload(Cliente.municipio).selectinload(Municipio.departamento),
                selectinload(Cliente.contactos),
            )
            .order_by(Cliente.id_cliente.asc())
        )
        if estado:
            stmt = stmt.where(func.lower(Cliente.estado) == func.lower(estado))
        if fecha_desde:
            stmt = stmt.where(Cliente.fecha_creacion >= datetime.combine(fecha_desde, time.min))
        if fecha_hasta:
            stmt = stmt.where(Cliente.fecha_creacion <= datetime.combine(fecha_hasta, time.max))

        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_cliente_by_id(self, id_cliente: int) -> Optional[Cliente]:
        stmt = (
            select(Cliente)
            .options(
                selectinload(Cliente.tipo_cliente),
                selectinload(Cliente.municipio).selectinload(Municipio.departamento),
                selectinload(Cliente.contactos),
            )
            .where(Cliente.id_cliente == id_cliente)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    # ---------------------------------------------------------------------------
    # KPI (Totales agregados SUM dentro del rango de fechas)
    # ---------------------------------------------------------------------------

    async def get_kpi_totales(self, inicio: date, fin: date) -> Dict[str, object]:
        """Totales agregados del período usando SUM/CUENTA en SQL.

        - Ventas: `SUM(total_venta)` de las ventas con estado 'Completada'
          (se ignoran anuladas/descuadradas para no inflar los ingresos).
        - Mermas: `SUM(costo_perdida)` del detalle de cada merma, filtrando
          por `fecha_merma` dentro del rango.
        - Compras: `SUM(total_compra)` de los gastos por mercadería.

        Devuelve un dict con las 6 claves que consume el DTO KPI.
        """
        dt_inicio, dt_fin = _rango_utc(inicio, fin)

        # 1) Ingresos (ventas netas) y número de transacciones del período.
        stmt_ventas = (
            select(
                func.coalesce(func.sum(Venta.total_venta), 0),
                func.count(Venta.id_venta),
            )
            .where(
                Venta.fecha_venta >= dt_inicio,
                Venta.fecha_venta <= dt_fin,
                Venta.estado == "Completada",
            )
        )
        total_ventas, count_ventas = (await self.db.execute(stmt_ventas)).one()

        # 2) Costo de mermas: se suma por cada línea de DetalleMerma. Como una
        #    merma puede tener N detalles, se cuenta DISTINCT(id_merma) para que
        #    el "nº de registros" refleje mermas y no líneas de detalle.
        stmt_mermas = (
            select(
                func.coalesce(func.sum(DetalleMerma.costo_perdida), 0),
                func.count(func.distinct(Merma.id_merma)),
            )
            .select_from(Merma)
            .join(DetalleMerma, Merma.id_merma == DetalleMerma.id_merma)
            .where(Merma.fecha_merma >= dt_inicio, Merma.fecha_merma <= dt_fin)
        )
        total_mermas, count_mermas = (await self.db.execute(stmt_mermas)).one()

        # 3) Gastos de compras dentro del período.
        stmt_compras = (
            select(
                func.coalesce(func.sum(Compra.total_compra), 0),
                func.count(Compra.id_compra),
            )
            .where(Compra.fecha_ingreso >= inicio, Compra.fecha_ingreso <= fin)
        )
        total_compras, count_compras = (await self.db.execute(stmt_compras)).one()

        return {
            "ventas": Decimal(str(total_ventas)),
            "count_ventas": int(count_ventas),
            "mermas": Decimal(str(total_mermas)),
            "count_mermas": int(count_mermas),
            "compras": Decimal(str(total_compras)),
            "count_compras": int(count_compras),
        }

    # ---------------------------------------------------------------------------
    # Gráficas (Tendencia / Categoría / Hora)
    # ---------------------------------------------------------------------------

    async def get_tendencia_ventas(self, inicio: date, fin: date) -> List[Tuple[date, Decimal]]:
        """Totales de ventas por día calendario local (America/Guatemala).

        Se traen solo las columnas mínimas (fecha + total) y se agrupan en
        Python restando GUATEMALA_OFFSET a cada timestamp UTC. Esto mantiene
        la consulta portable entre PostgreSQL (prod) y SQLite (tests), que no
        comparten funciones de fecha como date_trunc.
        """
        dt_inicio, dt_fin = _rango_utc(inicio, fin)
        stmt = (
            select(Venta.fecha_venta, Venta.total_venta)
            .where(
                Venta.fecha_venta >= dt_inicio,
                Venta.fecha_venta <= dt_fin,
                Venta.estado == "Completada",
            )
            .order_by(Venta.fecha_venta.asc())
        )
        rows = (await self.db.execute(stmt)).all()

        por_dia: Dict[date, Decimal] = {}
        for fecha_utc, total in rows:
            # Se convierte la hora UTC a hora local de Guatemala antes de extraer la fecha.
            fecha_local = (fecha_utc - GUATEMALA_OFFSET).date()
            por_dia[fecha_local] = por_dia.get(fecha_local, Decimal("0.00")) + Decimal(str(total))

        # Se devuelven ordenados ascendentemente; los días sin ventas no entran,
        # el frontend los completa si fuese necesario.
        return sorted(por_dia.items())

    async def get_ventas_por_categoria(self, inicio: date, fin: date) -> List[Tuple[str, Decimal]]:
        """Ingresos por categoría (dona): suma del importe neto de cada línea de
        detalle agrupada por Categoria.nombre.

        JOIN: detalle_venta -> venta (rango/estado) -> variante_producto ->
              producto -> subcategoria -> categoria.
        """
        dt_inicio, dt_fin = _rango_utc(inicio, fin)
        importe = func.coalesce(
            func.sum(DetalleVenta.subtotal - DetalleVenta.descuento_item), 0
        )
        stmt = (
            select(Categoria.nombre, importe)
            .select_from(DetalleVenta)
            .join(Venta, DetalleVenta.id_venta == Venta.id_venta)
            .join(VarianteProducto, DetalleVenta.id_variante == VarianteProducto.id_variante)
            .join(Producto, VarianteProducto.id_producto == Producto.id_producto)
            .join(Subcategoria, Producto.id_subcategoria == Subcategoria.id_subcategoria)
            .join(Categoria, Subcategoria.id_categoria == Categoria.id_categoria)
            .where(
                Venta.fecha_venta >= dt_inicio,
                Venta.fecha_venta <= dt_fin,
                Venta.estado == "Completada",
            )
            .group_by(Categoria.nombre)
            .order_by(importe.desc())
        )
        rows = (await self.db.execute(stmt)).all()
        return [(row[0], Decimal(str(row[1]))) for row in rows]

    async def get_ventas_por_hora(self, inicio: date, fin: date) -> List[Tuple[int, int]]:
        """Conteo de transacciones por hora pico (0-23 en hora local).

        Como la HORA debe medirse en la zona local del negocio, se traen las
        fechas UTC y se corre el offset en Python; luego se llenan las 24
        franjas horarias (las vacías quedan en cero para dibujar la barra).
        """
        dt_inicio, dt_fin = _rango_utc(inicio, fin)
        stmt = (
            select(Venta.fecha_venta)
            .where(
                Venta.fecha_venta >= dt_inicio,
                Venta.fecha_venta <= dt_fin,
                Venta.estado == "Completada",
            )
        )
        rows = (await self.db.execute(stmt)).all()

        por_hora = [0] * 24
        for (fecha_utc,) in rows:
            hora_local = (fecha_utc - GUATEMALA_OFFSET).hour
            por_hora[hora_local] += 1

        return [(hora, int(count)) for hora, count in enumerate(por_hora)]

    # ---------------------------------------------------------------------------
    # Widget de Rankings (Top Productos / Clientes / Estancados)
    # ---------------------------------------------------------------------------

    async def get_ranking_productos(self, inicio: date, fin: date, limite: int) -> List[Tuple[str, Decimal, int]]:
        """Top productos por monto vendido en el rango.

        Devuelve (nombre_producto, valor_vendido, unidades) ordenado por
        monto descendente con LIMIT `limite` (ORDER BY total DESC LIMIT X).
        """
        dt_inicio, dt_fin = _rango_utc(inicio, fin)
        valor = func.coalesce(
            func.sum(DetalleVenta.subtotal - DetalleVenta.descuento_item), 0
        )
        stmt = (
            select(
                Producto.nombre,
                valor,
                func.sum(DetalleVenta.cantidad),
            )
            .select_from(DetalleVenta)
            .join(Venta, DetalleVenta.id_venta == Venta.id_venta)
            .join(VarianteProducto, DetalleVenta.id_variante == VarianteProducto.id_variante)
            .join(Producto, VarianteProducto.id_producto == Producto.id_producto)
            .where(
                Venta.fecha_venta >= dt_inicio,
                Venta.fecha_venta <= dt_fin,
                Venta.estado == "Completada",
            )
            .group_by(Producto.id_producto, Producto.nombre)
            .order_by(valor.desc())
            .limit(limite)
        )
        rows = (await self.db.execute(stmt)).all()
        return [(row[0], Decimal(str(row[1])), int(row[2])) for row in rows]

    async def get_ranking_clientes(self, inicio: date, fin: date, limite: int) -> List[Tuple[str, Decimal, int]]:
        """Top clientes por monto de compras dentro del rango.

        Solo se consideran ventas 'Completada' que tengan cliente asignado.
        Devuelve (nombre_comercial, total_compras, nº_transacciones).
        """
        dt_inicio, dt_fin = _rango_utc(inicio, fin)
        stmt = (
            select(
                Cliente.nombre_comercial,
                func.coalesce(func.sum(Venta.total_venta), 0),
                func.count(Venta.id_venta),
            )
            .select_from(Venta)
            .join(Cliente, Venta.id_cliente == Cliente.id_cliente)
            .where(
                Venta.fecha_venta >= dt_inicio,
                Venta.fecha_venta <= dt_fin,
                Venta.estado == "Completada",
                Venta.id_cliente.isnot(None),
            )
            .group_by(Cliente.id_cliente, Cliente.nombre_comercial)
            .order_by(func.sum(Venta.total_venta).desc())
            .limit(limite)
        )
        rows = (await self.db.execute(stmt)).all()
        return [(row[0], Decimal(str(row[1])), int(row[2])) for row in rows]

    async def get_ranking_estancados(self, inicio: date, fin: date, limite: int) -> List[Tuple[str, Decimal, int]]:
        """Productos sin ventas en el rango (estancados), rankeados por el valor
        de inventario parado (stock_actual * costo_promedio).

        - Se obtiene la subconsulta de variantes que SÍ vendieron en el período.
        - Se devuelven las variantes AUSENTES de esa subconsulta, agrupando el
          stock disponible y valorizando el inventario con su costo promedio.
        Devuelve (nombre_variante, valor_inventario, unidades_stock).
        """
        dt_inicio, dt_fin = _rango_utc(inicio, fin)
        vendidos = (
            select(DetalleVenta.id_variante)
            .join(Venta, DetalleVenta.id_venta == Venta.id_venta)
            .where(
                Venta.fecha_venta >= dt_inicio,
                Venta.fecha_venta <= dt_fin,
                Venta.estado == "Completada",
            )
            .distinct()
        )
        stock_total = func.coalesce(func.sum(InventarioSucursal.stock_actual), 0)
        stmt = (
            select(
                VarianteProducto.id_variante,
                Producto.nombre,
                VarianteProducto.talla,
                VarianteProducto.color,
                VarianteProducto.costo_promedio,
                stock_total,
            )
            .select_from(VarianteProducto)
            .join(Producto, VarianteProducto.id_producto == Producto.id_producto)
            .outerjoin(InventarioSucursal, InventarioSucursal.id_variante == VarianteProducto.id_variante)
            .where(VarianteProducto.id_variante.not_in(vendidos))
            .group_by(
                VarianteProducto.id_variante,
                Producto.nombre,
                VarianteProducto.talla,
                VarianteProducto.color,
                VarianteProducto.costo_promedio,
            )
            .order_by(stock_total.desc(), Producto.nombre.asc())
            .limit(limite)
        )
        rows = (await self.db.execute(stmt)).all()

        # Se arma el nombre legible (producto + color/talla) y se valoriza el stock parado.
        resultados: List[Tuple[str, Decimal, int]] = []
        for id_variante, nombre, talla, color, costo, stock in rows:
            etiqueta = nombre
            if talla or color:
                variantes = " / ".join([x for x in (color, talla) if x])
                etiqueta = f"{nombre} ({variantes})"
            valor = (Decimal(str(stock)) * Decimal(str(costo))).quantize(Decimal("0.01"))
            resultados.append((etiqueta, valor, int(stock)))
        return resultados
