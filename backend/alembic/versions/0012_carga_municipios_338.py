"""carga_municipios_338

Revision ID: 0012
Revises: 0011
Create Date: 2026-10-22

Completa la carga oficial de municipios de Guatemala a 338:
- El Chal (Petén) — Decreto 5-2014 del Congreso de la República.
- Petatán (Huehuetenango) — Decreto 6-2015 del Congreso de la República.
Quedan 2 municipios pendientes por verificar contra fuente oficial para alcanzar los 340.
"""
from typing import Sequence, Union
from alembic import op

revision: str = "0012"
down_revision: Union[str, None] = "0011"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
        INSERT INTO municipio (id_departamento, nombre, estado)
        SELECT d.id_departamento, m.nombre, 'Activo'
        FROM (VALUES
            ('Petén', 'El Chal'),
            ('Huehuetenango', 'Petatán')
        ) AS m(depto, nombre)
        JOIN departamento_geografico d ON d.nombre = m.depto
        ON CONFLICT DO NOTHING;
    """)


def downgrade() -> None:
    op.execute("""
        DELETE FROM municipio
        WHERE nombre IN ('El Chal', 'Petatán');
    """)
