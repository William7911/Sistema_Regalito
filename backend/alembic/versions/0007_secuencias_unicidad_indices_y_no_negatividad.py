"""secuencias_unicidad_indices_y_no_negatividad

Revision ID: 0007
Revises: 0006
Create Date: 2026-09-20

1. Generación automática de IDs mediante secuencias PostgreSQL para 32 tablas con PK INT:
   Elimina riesgo de colisión de IDs en inserciones concurrentes.
2. Restricciones UNIQUE a nivel de base de datos para campos tratados como únicos en la lógica:
   usuario.username, variante_producto.codigo_barras, factura_fel.numero_dte, etc.
3. Índices en columnas de llaves foráneas frecuentemente consultadas en filtros y reportes:
   usuario, variante de producto, sucursal, venta, turno de caja, etc.
4. Restricciones CHECK de no negatividad (>= 0) en campos numéricos de cantidad y stock:
   inventario_sucursal, detalle_venta, detalle_merma, traslado, ordenes, compras, arqueo.
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "0007"
down_revision: Union[str, None] = "0006"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_TABLE_SEQUENCES = [
    ("alerta_stock", "id_alerta"),
    ("area_bodega", "id_area"),
    ("bitacora_auditoria", "id_bitacora"),
    ("categoria", "id_categoria"),
    ("cliente", "id_cliente"),
    ("cliente_contacto", "id_contacto"),
    ("compra", "id_compra"),
    ("denominacion_efectivo", "id_denominacion"),
    ("departamento_geografico", "id_departamento"),
    ("detalle_compra", "id_detalle_compra"),
    ("detalle_orden_compra", "id_detalle_orden"),
    ("factura_fel", "id_factura"),
    ("historial_precio", "id_historial"),
    ("inventario_sucursal", "id_inventario"),
    ("metodo_pago", "id_metodo_pago"),
    ("motivo_merma", "id_motivo"),
    ("municipio", "id_municipio"),
    ("orden_compra", "id_orden"),
    ("parametro_sistema", "id_parametro"),
    ("permiso", "id_permiso"),
    ("producto", "id_producto"),
    ("proveedor", "id_proveedor"),
    ("rol", "id_rol"),
    ("sesion_usuario", "id_sesion"),
    ("subcategoria", "id_subcategoria"),
    ("sucursal", "id_sucursal"),
    ("tipo_cliente", "id_tipo_cliente"),
    ("tipo_movimiento_caja", "id_tipo_movimiento"),
    ("traslado_inventario", "id_traslado"),
    ("unidad_medida", "id_unidad"),
    ("usuario", "id_usuario"),
    ("variante_producto", "id_variante"),
]

_UNIQUE_CONSTRAINTS = [
    ("uq_usuario_username", "usuario", "username"),
    ("uq_variante_codigo_barras", "variante_producto", "codigo_barras"),
    ("uq_factura_fel_numero_dte", "factura_fel", "numero_dte"),
    ("uq_rol_nombre", "rol", "nombre"),
    ("uq_categoria_nombre", "categoria", "nombre"),
    ("uq_departamento_geografico_nombre", "departamento_geografico", "nombre"),
    ("uq_permiso_codigo", "permiso", "codigo"),
    ("uq_parametro_sistema_clave", "parametro_sistema", "clave"),
    ("uq_unidad_medida_codigo", "unidad_medida", "codigo"),
]

_FK_INDEXES = [
    # id_usuario
    ("idx_bitacora_auditoria_id_usuario", "bitacora_auditoria", "id_usuario"),
    ("idx_cierre_ciegas_cajero", "cierre_caja_ciegas", "id_usuario_cajero"),
    ("idx_cierre_ciegas_supervisor", "cierre_caja_ciegas", "id_usuario_supervisor"),
    ("idx_compra_id_usuario", "compra", "id_usuario"),
    ("idx_historial_precio_id_usuario", "historial_precio", "id_usuario"),
    ("idx_merma_id_usuario", "merma", "id_usuario"),
    ("idx_movimiento_caja_id_usuario", "movimiento_caja", "id_usuario"),
    ("idx_orden_compra_id_usuario", "orden_compra", "id_usuario"),
    ("idx_sesion_usuario_id_usuario", "sesion_usuario", "id_usuario"),
    ("idx_turno_caja_id_usuario", "turno_caja", "id_usuario"),
    ("idx_venta_id_usuario", "venta", "id_usuario"),
    # id_variante
    ("idx_inventario_sucursal_id_variante", "inventario_sucursal", "id_variante"),
    ("idx_detalle_venta_id_variante", "detalle_venta", "id_variante"),
    ("idx_detalle_compra_id_variante", "detalle_compra", "id_variante"),
    ("idx_detalle_orden_compra_id_variante", "detalle_orden_compra", "id_variante"),
    ("idx_detalle_merma_id_variante", "detalle_merma", "id_variante"),
    ("idx_traslado_inventario_id_variante", "traslado_inventario", "id_variante"),
    ("idx_historial_precio_id_variante", "historial_precio", "id_variante"),
    # id_sucursal
    ("idx_caja_id_sucursal", "caja", "id_sucursal"),
    ("idx_area_bodega_id_sucursal", "area_bodega", "id_sucursal"),
    ("idx_inventario_sucursal_id_sucursal", "inventario_sucursal", "id_sucursal"),
    ("idx_merma_id_sucursal", "merma", "id_sucursal"),
    ("idx_traslado_inventario_origen", "traslado_inventario", "id_sucursal_origen"),
    ("idx_traslado_inventario_destino", "traslado_inventario", "id_sucursal_destino"),
    # id_venta
    ("idx_detalle_venta_id_venta", "detalle_venta", "id_venta"),
    ("idx_pago_venta_id_venta", "pago_venta", "id_venta"),
    ("idx_factura_fel_id_venta", "factura_fel", "id_venta"),
    # id_turno
    ("idx_venta_id_turno", "venta", "id_turno"),
    ("idx_cierre_caja_ciegas_id_turno", "cierre_caja_ciegas", "id_turno"),
    ("idx_movimiento_caja_id_turno", "movimiento_caja", "id_turno"),
    # Catálogo, Compras, Caja y Geografía
    ("idx_usuario_id_rol", "usuario", "id_rol"),
    ("idx_producto_id_subcategoria", "producto", "id_subcategoria"),
    ("idx_producto_id_unidad", "producto", "id_unidad"),
    ("idx_subcategoria_id_categoria", "subcategoria", "id_categoria"),
    ("idx_variante_producto_id_producto", "variante_producto", "id_producto"),
    ("idx_alerta_stock_id_inventario", "alerta_stock", "id_inventario"),
    ("idx_turno_caja_id_caja", "turno_caja", "id_caja"),
    ("idx_venta_id_cliente", "venta", "id_cliente"),
    ("idx_cliente_id_tipo_cliente", "cliente", "id_tipo_cliente"),
    ("idx_cliente_id_municipio", "cliente", "id_municipio"),
    ("idx_cliente_contacto_id_cliente", "cliente_contacto", "id_cliente"),
    ("idx_compra_id_orden", "compra", "id_orden"),
    ("idx_compra_id_proveedor", "compra", "id_proveedor"),
    ("idx_detalle_compra_id_compra", "detalle_compra", "id_compra"),
    ("idx_detalle_orden_compra_id_orden", "detalle_orden_compra", "id_orden"),
    ("idx_orden_compra_id_proveedor", "orden_compra", "id_proveedor"),
    ("idx_detalle_merma_id_merma", "detalle_merma", "id_merma"),
    ("idx_detalle_merma_id_motivo", "detalle_merma", "id_motivo"),
    ("idx_detalle_arqueo_id_cierre", "detalle_arqueo_efectivo", "id_cierre"),
    ("idx_detalle_arqueo_id_denominacion", "detalle_arqueo_efectivo", "id_denominacion"),
    ("idx_pago_venta_id_metodo_pago", "pago_venta", "id_metodo_pago"),
    ("idx_movimiento_caja_id_tipo_movimiento", "movimiento_caja", "id_tipo_movimiento"),
    ("idx_municipio_id_departamento", "municipio", "id_departamento"),
    ("idx_inventario_sucursal_id_area", "inventario_sucursal", "id_area"),
]

_CHECK_NON_NEGATIVE = [
    ("ck_inventario_stock_actual_positivo", "inventario_sucursal", "stock_actual >= 0"),
    ("ck_inventario_stock_minimo_positivo", "inventario_sucursal", "stock_minimo >= 0"),
    ("ck_detalle_venta_cantidad_positiva", "detalle_venta", "cantidad >= 0"),
    ("ck_detalle_merma_cantidad_positiva", "detalle_merma", "cantidad >= 0"),
    ("ck_traslado_inventario_cantidad_positiva", "traslado_inventario", "cantidad >= 0"),
    ("ck_detalle_arqueo_cantidad_piezas_positiva", "detalle_arqueo_efectivo", "cantidad_piezas >= 0"),
    ("ck_detalle_orden_compra_cantidad_positiva", "detalle_orden_compra", "cantidad_pedida >= 0"),
    ("ck_detalle_compra_cantidad_recibida_positiva", "detalle_compra", "cantidad_recibida >= 0"),
]


def upgrade() -> None:
    # 1. Crear secuencias automáticas para las 32 tablas con PK INT
    for table_name, pk_name in _TABLE_SEQUENCES:
        seq_name = f"{table_name}_{pk_name}_seq"
        op.execute(
            f"""
            DO $$
            BEGIN
                IF NOT EXISTS (SELECT 1 FROM pg_class WHERE relname = '{seq_name}') THEN
                    CREATE SEQUENCE {seq_name};
                    ALTER TABLE {table_name} ALTER COLUMN {pk_name} SET DEFAULT nextval('{seq_name}');
                    ALTER SEQUENCE {seq_name} OWNED BY {table_name}.{pk_name};
                    PERFORM setval('{seq_name}', COALESCE((SELECT MAX({pk_name}) FROM {table_name}), 0) + 1, false);
                END IF;
            END $$;
            """
        )

    # 2. Agregar restricciones de unicidad (UNIQUE)
    for uq_name, table_name, col_name in _UNIQUE_CONSTRAINTS:
        op.execute(
            f"""
            DO $$
            BEGIN
                IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = '{uq_name}') THEN
                    ALTER TABLE {table_name} ADD CONSTRAINT {uq_name} UNIQUE ({col_name});
                END IF;
            END $$;
            """
        )

    # 3. Crear índices en columnas de llaves foráneas frecuentemente consultadas
    for idx_name, table_name, col_name in _FK_INDEXES:
        op.execute(
            f"CREATE INDEX IF NOT EXISTS {idx_name} ON {table_name} ({col_name});"
        )

    # 4. Agregar restricciones CHECK de no negatividad en stock y cantidades
    for ck_name, table_name, condition in _CHECK_NON_NEGATIVE:
        op.execute(
            f"""
            DO $$
            BEGIN
                IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = '{ck_name}') THEN
                    ALTER TABLE {table_name} ADD CONSTRAINT {ck_name} CHECK ({condition});
                END IF;
            END $$;
            """
        )


def downgrade() -> None:
    # 4. Eliminar restricciones CHECK de no negatividad
    for ck_name, table_name, _ in _CHECK_NON_NEGATIVE:
        op.execute(f"ALTER TABLE {table_name} DROP CONSTRAINT IF EXISTS {ck_name};")

    # 3. Eliminar índices en llaves foráneas
    for idx_name, _, _ in _FK_INDEXES:
        op.execute(f"DROP INDEX IF EXISTS {idx_name};")

    # 2. Eliminar restricciones de unicidad
    for uq_name, table_name, _ in _UNIQUE_CONSTRAINTS:
        op.execute(f"ALTER TABLE {table_name} DROP CONSTRAINT IF EXISTS {uq_name};")

    # 1. Eliminar secuencias y defaults de las 32 tablas
    for table_name, pk_name in _TABLE_SEQUENCES:
        seq_name = f"{table_name}_{pk_name}_seq"
        op.execute(f"ALTER TABLE {table_name} ALTER COLUMN {pk_name} DROP DEFAULT;")
        op.execute(f"DROP SEQUENCE IF EXISTS {seq_name} CASCADE;")

