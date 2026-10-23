"""factura_fel_estado_y_dte_nullable

Revision ID: 0009
Revises: 0008
Create Date: 2026-10-13

Crea el soporte de estados de certificación FEL en `factura_fel`:
- Nueva columna `estado` (Certificada | Pendiente DTE | Contingencia).
- Los campos del DTE (`numero_autorizacion_sat`, `serie`, `numero_dte`)
  pasan a ser NULLables para permitir facturas en contingencia sin número
  de autorización aún asignado.
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "0009"
down_revision: Union[str, None] = "0008"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("ALTER TABLE factura_fel ALTER COLUMN numero_autorizacion_sat DROP NOT NULL;")
    op.execute("ALTER TABLE factura_fel ALTER COLUMN serie DROP NOT NULL;")
    op.execute("ALTER TABLE factura_fel ALTER COLUMN numero_dte DROP NOT NULL;")
    op.execute(
        "ALTER TABLE factura_fel ADD COLUMN IF NOT EXISTS estado VARCHAR(20) NOT NULL DEFAULT 'Certificada';"
    )


def downgrade() -> None:
    op.execute("ALTER TABLE factura_fel DROP COLUMN IF EXISTS estado;")
    op.execute("ALTER TABLE factura_fel ALTER COLUMN numero_dte SET NOT NULL;")
    op.execute("ALTER TABLE factura_fel ALTER COLUMN serie SET NOT NULL;")
    op.execute("ALTER TABLE factura_fel ALTER COLUMN numero_autorizacion_sat SET NOT NULL;")
