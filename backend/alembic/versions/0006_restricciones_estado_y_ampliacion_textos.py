"""restricciones_estado_y_ampliacion_textos

Revision ID: 0006
Revises: 0005
Create Date: 2026-09-20

1. Agrega restricciones CHECK seguras en las columnas de tipo estado (VARCHAR(20))
   para blindar la base de datos contra valores inconsistentes o mal escritos,
   sin cambiar el tipo de dato de las columnas:
   - rol (Activo, Inactivo)
   - usuario (Activo, Inactivo)
   - sucursal (Activo, Inactivo)
   - categoria (Activo, Inactivo)
   - producto (Activo, Inactivo)
   - caja (Activa, Inactiva, Activo, Inactivo)
   - turno_caja (Abierto, Cerrado, Abierta, Cerrada)
   - venta (Completada, Anulada)
   - orden_compra (Emitida, Recibida, Cancelada)
   - alerta_stock (Pendiente, Atendida, Descartada)

2. Amplía las columnas de texto libre de VARCHAR(255) a TEXT para permitir explicaciones
   más extensas y evitar desbordamientos (en particular en notas de cierre de caja):
   - producto.descripcion
   - cierre_caja_ciegas.observaciones
   - turno_caja.notas
   - merma.observaciones
   - bitacora_auditoria.descripcion
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "0006"
down_revision: Union[str, None] = "0005"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_CHECK_CONSTRAINTS = [
    ("ck_rol_estado", "rol", "estado IN ('Activo', 'Inactivo')"),
    ("ck_usuario_estado", "usuario", "estado IN ('Activo', 'Inactivo')"),
    ("ck_sucursal_estado", "sucursal", "estado IN ('Activo', 'Inactivo')"),
    ("ck_categoria_estado", "categoria", "estado IN ('Activo', 'Inactivo')"),
    ("ck_producto_estado", "producto", "estado IN ('Activo', 'Inactivo')"),
    ("ck_caja_estado", "caja", "estado IN ('Activa', 'Inactiva', 'Activo', 'Inactivo')"),
    ("ck_turno_caja_estado", "turno_caja", "estado IN ('Abierto', 'Cerrado', 'Abierta', 'Cerrada')"),
    ("ck_venta_estado", "venta", "estado IN ('Completada', 'Anulada')"),
    ("ck_orden_compra_estado", "orden_compra", "estado IN ('Emitida', 'Recibida', 'Cancelada')"),
    ("ck_alerta_stock_estado", "alerta_stock", "estado IN ('Pendiente', 'Atendida', 'Descartada')"),
]

_TEXT_COLUMNS = [
    ("producto", "descripcion"),
    ("cierre_caja_ciegas", "observaciones"),
    ("turno_caja", "notas"),
    ("merma", "observaciones"),
    ("bitacora_auditoria", "descripcion"),
]


def upgrade() -> None:
    # 1. Crear restricciones CHECK de forma idempotente
    for ck_name, table_name, condition in _CHECK_CONSTRAINTS:
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

    # 2. Ampliar columnas de texto libre a TEXT
    for table_name, col_name in _TEXT_COLUMNS:
        op.execute(
            f"ALTER TABLE {table_name} ALTER COLUMN {col_name} TYPE TEXT;"
        )


def downgrade() -> None:
    # 1. Revertir columnas de texto a VARCHAR(255)
    for table_name, col_name in _TEXT_COLUMNS:
        op.execute(
            f"ALTER TABLE {table_name} ALTER COLUMN {col_name} TYPE VARCHAR(255);"
        )

    # 2. Eliminar restricciones CHECK
    for ck_name, table_name, _ in _CHECK_CONSTRAINTS:
        op.execute(
            f"ALTER TABLE {table_name} DROP CONSTRAINT IF EXISTS {ck_name};"
        )

