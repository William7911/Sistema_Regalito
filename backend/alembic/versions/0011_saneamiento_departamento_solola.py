"""saneamiento_departamento_solola

Revision ID: 0011
Revises: 0010
Create Date: 2026-10-21

Sanea y unifica cualquier registro de departamento corrupto (como 'Solol??' por codificación legacy)
hacia 'Sololá', reasignando los municipios vinculados para evitar datos huérfanos.
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "0011"
down_revision: Union[str, None] = "0010"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
        DO $$
        DECLARE
            id_corrupto INT;
            id_bueno INT;
        BEGIN
            SELECT id_departamento INTO id_corrupto FROM departamento_geografico
            WHERE nombre LIKE 'Solol%' AND nombre <> 'Sololá' LIMIT 1;

            SELECT id_departamento INTO id_bueno FROM departamento_geografico
            WHERE nombre = 'Sololá' LIMIT 1;

            IF id_corrupto IS NOT NULL THEN
                IF id_bueno IS NOT NULL THEN
                    UPDATE municipio SET id_departamento = id_bueno WHERE id_departamento = id_corrupto;
                    DELETE FROM departamento_geografico WHERE id_departamento = id_corrupto;
                ELSE
                    UPDATE departamento_geografico SET nombre = 'Sololá' WHERE id_departamento = id_corrupto;
                END IF;
            END IF;
        END$$;
    """)


def downgrade() -> None:
    # Es una operación de saneamiento y consolidación de datos; no requiere acción destructiva en downgrade
    pass

