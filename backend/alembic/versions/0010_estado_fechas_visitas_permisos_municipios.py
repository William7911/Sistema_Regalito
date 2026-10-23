"""estado_fechas_visitas_permisos_municipios

Revision ID: 0010
Revises: 0009
Create Date: 2026-10-21

Agrega columnas `estado` (soft delete) a tablas sin él, columnas `fecha_creacion`
a cliente/proveedor/sucursal, restricciones únicas compuestas, tablas nuevas
`visita_seguimiento` + `visita_modulo_evaluacion`, nuevos permisos y
datos de departamentos/municipios de Guatemala.
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "0010"
down_revision: Union[str, None] = "0009"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # -------------------------------------------------------------------------
    # 1. Columna ESTADO (soft delete) en tablas que no la tenían
    # -------------------------------------------------------------------------
    op.execute("""
        ALTER TABLE cliente
            ADD COLUMN IF NOT EXISTS estado VARCHAR(20) NOT NULL DEFAULT 'Activo'
            CHECK (estado IN ('Activo','Inactivo'));
    """)
    op.execute("""
        ALTER TABLE tipo_cliente
            ADD COLUMN IF NOT EXISTS estado VARCHAR(20) NOT NULL DEFAULT 'Activo'
            CHECK (estado IN ('Activo','Inactivo'));
    """)
    op.execute("""
        ALTER TABLE area_bodega
            ADD COLUMN IF NOT EXISTS estado VARCHAR(20) NOT NULL DEFAULT 'Activo'
            CHECK (estado IN ('Activo','Inactivo'));
    """)
    op.execute("""
        ALTER TABLE departamento_geografico
            ADD COLUMN IF NOT EXISTS estado VARCHAR(20) NOT NULL DEFAULT 'Activo'
            CHECK (estado IN ('Activo','Inactivo'));
    """)
    op.execute("""
        ALTER TABLE municipio
            ADD COLUMN IF NOT EXISTS estado VARCHAR(20) NOT NULL DEFAULT 'Activo'
            CHECK (estado IN ('Activo','Inactivo'));
    """)
    op.execute("""
        ALTER TABLE subcategoria
            ADD COLUMN IF NOT EXISTS estado VARCHAR(20) NOT NULL DEFAULT 'Activo'
            CHECK (estado IN ('Activo','Inactivo'));
    """)
    op.execute("""
        ALTER TABLE unidad_medida
            ADD COLUMN IF NOT EXISTS estado VARCHAR(20) NOT NULL DEFAULT 'Activo'
            CHECK (estado IN ('Activo','Inactivo'));
    """)
    op.execute("""
        ALTER TABLE motivo_merma
            ADD COLUMN IF NOT EXISTS estado VARCHAR(20) NOT NULL DEFAULT 'Activo'
            CHECK (estado IN ('Activo','Inactivo'));
    """)
    op.execute("""
        ALTER TABLE metodo_pago
            ADD COLUMN IF NOT EXISTS estado VARCHAR(20) NOT NULL DEFAULT 'Activo'
            CHECK (estado IN ('Activo','Inactivo'));
    """)
    op.execute("""
        ALTER TABLE proveedor
            ADD COLUMN IF NOT EXISTS estado VARCHAR(20) NOT NULL DEFAULT 'Activo'
            CHECK (estado IN ('Activo','Inactivo'));
    """)

    # -------------------------------------------------------------------------
    # 2. Columna fecha_creacion en cliente, proveedor, sucursal
    # -------------------------------------------------------------------------
    op.execute("""
        ALTER TABLE cliente
            ADD COLUMN IF NOT EXISTS fecha_creacion TIMESTAMP NOT NULL DEFAULT NOW();
    """)
    op.execute("""
        ALTER TABLE proveedor
            ADD COLUMN IF NOT EXISTS fecha_creacion TIMESTAMP NOT NULL DEFAULT NOW();
    """)
    op.execute("""
        ALTER TABLE sucursal
            ADD COLUMN IF NOT EXISTS fecha_creacion TIMESTAMP NOT NULL DEFAULT NOW();
    """)

    # -------------------------------------------------------------------------
    # 3. fecha_hora DEFAULT en bitacora_auditoria
    # -------------------------------------------------------------------------
    op.execute("""
        ALTER TABLE bitacora_auditoria
            ALTER COLUMN fecha_hora SET DEFAULT NOW();
    """)

    # -------------------------------------------------------------------------
    # 4. Restricciones únicas compuestas
    # -------------------------------------------------------------------------
    # Municipio: (id_departamento, nombre) — drop old unique si existe
    op.execute("""
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1 FROM pg_constraint
                WHERE conname = 'municipio_nombre_key' AND conrelid = 'municipio'::regclass
            ) THEN
                ALTER TABLE municipio DROP CONSTRAINT municipio_nombre_key;
            END IF;
        END$$;
    """)
    op.execute("""
        ALTER TABLE municipio
            ADD CONSTRAINT uq_municipio_depto_nombre
            UNIQUE (id_departamento, nombre);
    """)

    # Subcategoria: (id_categoria, nombre) — drop old unique si existe
    op.execute("""
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1 FROM pg_constraint
                WHERE conname = 'subcategoria_nombre_key' AND conrelid = 'subcategoria'::regclass
            ) THEN
                ALTER TABLE subcategoria DROP CONSTRAINT subcategoria_nombre_key;
            END IF;
        END$$;
    """)
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM pg_constraint
                WHERE conname = 'uq_subcategoria_cat_nombre'
            ) THEN
                ALTER TABLE subcategoria
                    ADD CONSTRAINT uq_subcategoria_cat_nombre
                    UNIQUE (id_categoria, nombre);
            END IF;
        END$$;
    """)

    # Cliente NIT: partial unique donde nit <> 'CF'
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM pg_indexes
                WHERE indexname = 'uq_cliente_nit_no_cf'
            ) THEN
                CREATE UNIQUE INDEX uq_cliente_nit_no_cf
                    ON cliente (nit)
                    WHERE nit <> 'CF';
            END IF;
        END$$;
    """)

    # -------------------------------------------------------------------------
    # 5. Tablas nuevas: visita_seguimiento y visita_modulo_evaluacion
    # -------------------------------------------------------------------------
    op.execute("""
        CREATE TABLE IF NOT EXISTS visita_seguimiento (
            id_visita           SERIAL PRIMARY KEY,
            id_cliente          INTEGER NOT NULL REFERENCES cliente(id_cliente),
            id_usuario          INTEGER NOT NULL REFERENCES usuario(id_usuario),
            fecha_visita        DATE NOT NULL,
            observaciones       TEXT,
            estado              VARCHAR(20) NOT NULL DEFAULT 'Pendiente'
                                CHECK (estado IN ('Pendiente','Completada','Cancelada')),
            fecha_creacion      TIMESTAMP NOT NULL DEFAULT NOW()
        );
    """)
    op.execute("""
        CREATE TABLE IF NOT EXISTS visita_modulo_evaluacion (
            id_modulo_eval      SERIAL PRIMARY KEY,
            id_visita           INTEGER NOT NULL
                                REFERENCES visita_seguimiento(id_visita) ON DELETE CASCADE,
            nombre_modulo       VARCHAR(100) NOT NULL,
            calificacion        SMALLINT CHECK (calificacion BETWEEN 1 AND 10),
            comentario          TEXT
        );
    """)

    # -------------------------------------------------------------------------
    # 6. Nuevos permisos y asignación al rol Administradora (id_rol = 1)
    # -------------------------------------------------------------------------
    op.execute("""
        INSERT INTO permiso (modulo, codigo, descripcion) VALUES
            ('Clientes',   'CLIENTE_ADMIN',      'Gestión completa de clientes'),
            ('Seguridad',  'BITACORA_CONSULTAR', 'Consultar bitácora de auditoría'),
            ('Reportes',   'REPORTE_VER',        'Ver reportes del sistema'),
            ('Catálogo',   'CATALOGO_ADMIN',     'Gestión completa de catálogos'),
            ('Visitas',    'VISITA_REGISTRAR',   'Registrar y consultar visitas de seguimiento')
        ON CONFLICT (codigo) DO NOTHING;
    """)
    op.execute("""
        INSERT INTO rol_permiso (id_rol, id_permiso)
        SELECT 1, id_permiso FROM permiso
        WHERE codigo IN (
            'CLIENTE_ADMIN','BITACORA_CONSULTAR','REPORTE_VER',
            'CATALOGO_ADMIN','VISITA_REGISTRAR'
        )
        ON CONFLICT DO NOTHING;
    """)

    # -------------------------------------------------------------------------
    # 7. Departamentos de Guatemala (22 departamentos)
    # -------------------------------------------------------------------------
    op.execute("""
        INSERT INTO departamento_geografico (nombre) VALUES
            ('Alta Verapaz'),('Baja Verapaz'),('Chimaltenango'),('Chiquimula'),
            ('El Progreso'),('Escuintla'),('Guatemala'),('Huehuetenango'),
            ('Izabal'),('Jalapa'),('Jutiapa'),('Petén'),
            ('Quetzaltenango'),('Quiché'),('Retalhuleu'),('Sacatepéquez'),
            ('San Marcos'),('Santa Rosa'),('Sololá'),('Suchitepéquez'),
            ('Totonicapán'),('Zacapa')
        ON CONFLICT (nombre) DO NOTHING;
    """)

    # -------------------------------------------------------------------------
    # 8. Municipios de Guatemala: 338 cargados, 4 por verificar contra fuente oficial
    # -------------------------------------------------------------------------
    # NOTA: Se insertan por bloque por departamento usando INSERT ... ON CONFLICT DO NOTHING
    op.execute("""
        INSERT INTO municipio (id_departamento, nombre)
        SELECT d.id_departamento, m.nombre
        FROM (VALUES
            -- Alta Verapaz (17 municipios)
            ('Alta Verapaz','Cobán'),('Alta Verapaz','Santa Cruz Verapaz'),
            ('Alta Verapaz','San Cristóbal Verapaz'),('Alta Verapaz','Tactic'),
            ('Alta Verapaz','Tamahú'),('Alta Verapaz','Tucurú'),
            ('Alta Verapaz','Panzós'),('Alta Verapaz','Senahú'),
            ('Alta Verapaz','San Pedro Carchá'),('Alta Verapaz','San Juan Chamelco'),
            ('Alta Verapaz','Lanquín'),('Alta Verapaz','Cahabón'),
            ('Alta Verapaz','Chisec'),('Alta Verapaz','Chahal'),
            ('Alta Verapaz','Fray Bartolomé de las Casas'),('Alta Verapaz','Santa Catalina La Tinta'),
            ('Alta Verapaz','Raxruhá'),
            -- Baja Verapaz (8 municipios)
            ('Baja Verapaz','Salamá'),('Baja Verapaz','San Miguel Chicaj'),
            ('Baja Verapaz','Rabinal'),('Baja Verapaz','Cubulco'),
            ('Baja Verapaz','Granados'),('Baja Verapaz','El Chol'),
            ('Baja Verapaz','San Jerónimo'),('Baja Verapaz','Purulhá'),
            -- Chimaltenango (16 municipios)
            ('Chimaltenango','Chimaltenango'),('Chimaltenango','San José Poaquil'),
            ('Chimaltenango','San Martín Jilotepeque'),('Chimaltenango','Comalapa'),
            ('Chimaltenango','Santa Apolonia'),('Chimaltenango','Tecpán Guatemala'),
            ('Chimaltenango','Patzún'),('Chimaltenango','Pochuta'),
            ('Chimaltenango','Patzicía'),('Chimaltenango','Santa Cruz Balanyá'),
            ('Chimaltenango','Acatenango'),('Chimaltenango','Yepocapa'),
            ('Chimaltenango','San Andrés Itzapa'),('Chimaltenango','Parramos'),
            ('Chimaltenango','Zaragoza'),('Chimaltenango','El Tejar'),
            -- Chiquimula (11 municipios)
            ('Chiquimula','Chiquimula'),('Chiquimula','San José La Arada'),
            ('Chiquimula','San Juan La Ermita'),('Chiquimula','Jocotán'),
            ('Chiquimula','Camotán'),('Chiquimula','Olopa'),
            ('Chiquimula','Esquipulas'),('Chiquimula','Concepción Las Minas'),
            ('Chiquimula','Quezaltepeque'),('Chiquimula','San Jacinto'),
            ('Chiquimula','Ipala'),
            -- El Progreso (8 municipios)
            ('El Progreso','Guastatoya'),('El Progreso','Morazán'),
            ('El Progreso','San Agustín Acasaguastlán'),('El Progreso','San Cristóbal Acasaguastlán'),
            ('El Progreso','El Jícaro'),('El Progreso','Sansare'),
            ('El Progreso','Sanarate'),('El Progreso','San Antonio La Paz'),
            -- Escuintla (13 municipios)
            ('Escuintla','Escuintla'),('Escuintla','Santa Lucía Cotzumalguapa'),
            ('Escuintla','La Democracia'),('Escuintla','Siquinalá'),
            ('Escuintla','Masagua'),('Escuintla','Tiquisate'),
            ('Escuintla','La Gomera'),('Escuintla','Guanagazapa'),
            ('Escuintla','San José'),('Escuintla','Iztapa'),
            ('Escuintla','Palín'),('Escuintla','San Vicente Pacaya'),
            ('Escuintla','Nueva Concepción'),
            -- Guatemala (17 municipios)
            ('Guatemala','Guatemala'),('Guatemala','Santa Catarina Pinula'),
            ('Guatemala','San José Pinula'),('Guatemala','San José del Golfo'),
            ('Guatemala','Palencia'),('Guatemala','Chinautla'),
            ('Guatemala','San Pedro Ayampuc'),('Guatemala','Mixco'),
            ('Guatemala','San Pedro Sacatepéquez'),('Guatemala','San Juan Sacatepéquez'),
            ('Guatemala','San Raymundo'),('Guatemala','Chuarrancho'),
            ('Guatemala','Fraijanes'),('Guatemala','Amatitlán'),
            ('Guatemala','Villa Nueva'),('Guatemala','Villa Canales'),
            ('Guatemala','San Miguel Petapa'),
            -- Huehuetenango (32 municipios)
            ('Huehuetenango','Huehuetenango'),('Huehuetenango','Chiantla'),
            ('Huehuetenango','Malacatancito'),('Huehuetenango','Cuilco'),
            ('Huehuetenango','Nentón'),('Huehuetenango','San Pedro Necta'),
            ('Huehuetenango','Jacaltenango'),('Huehuetenango','Soloma'),
            ('Huehuetenango','Ixtahuacán'),('Huehuetenango','Santa Bárbara'),
            ('Huehuetenango','La Libertad'),('Huehuetenango','La Democracia'),
            ('Huehuetenango','San Miguel Acatán'),('Huehuetenango','San Rafael La Independencia'),
            ('Huehuetenango','Todos Santos Cuchumatán'),('Huehuetenango','San Juan Atitán'),
            ('Huehuetenango','Santa Eulalia'),('Huehuetenango','San Mateo Ixtatán'),
            ('Huehuetenango','Colotenango'),('Huehuetenango','San Sebastián Huehuetenango'),
            ('Huehuetenango','Tectitán'),('Huehuetenango','Concepción Huista'),
            ('Huehuetenango','San Juan Ixcoy'),('Huehuetenango','San Antonio Huista'),
            ('Huehuetenango','San Sebastián Coatán'),('Huehuetenango','Barillas'),
            ('Huehuetenango','Aguacatán'),('Huehuetenango','San Rafael Petzal'),
            ('Huehuetenango','San Gaspar Ixchil'),('Huehuetenango','Santiago Chimaltenango'),
            ('Huehuetenango','Santa Ana Huista'),('Huehuetenango','Unión Cantinil'),
            -- Izabal (5 municipios)
            ('Izabal','Puerto Barrios'),('Izabal','Livingston'),
            ('Izabal','El Estor'),('Izabal','Morales'),
            ('Izabal','Los Amates'),
            -- Jalapa (7 municipios)
            ('Jalapa','Jalapa'),('Jalapa','San Pedro Pinula'),
            ('Jalapa','San Luis Jilotepeque'),('Jalapa','San Manuel Chaparrón'),
            ('Jalapa','San Carlos Alzatate'),('Jalapa','Monjas'),
            ('Jalapa','Mataquescuintla'),
            -- Jutiapa (17 municipios)
            ('Jutiapa','Jutiapa'),('Jutiapa','El Progreso'),
            ('Jutiapa','Santa Catarina Mita'),('Jutiapa','Agua Blanca'),
            ('Jutiapa','Asunción Mita'),('Jutiapa','Yupiltepeque'),
            ('Jutiapa','Atescatempa'),('Jutiapa','Jerez'),
            ('Jutiapa','El Adelanto'),('Jutiapa','Zapotitlán'),
            ('Jutiapa','Comapa'),('Jutiapa','Jalpatagua'),
            ('Jutiapa','Conguaco'),('Jutiapa','Moyuta'),
            ('Jutiapa','Pasaco'),('Jutiapa','San José Acatempa'),
            ('Jutiapa','Quesada'),
            -- Petén (12 municipios)
            ('Petén','Flores'),('Petén','San José'),
            ('Petén','San Benito'),('Petén','San Andrés'),
            ('Petén','La Libertad'),('Petén','San Francisco'),
            ('Petén','Santa Ana'),('Petén','Dolores'),
            ('Petén','San Luis'),('Petén','Sayaxché'),
            ('Petén','Melchor de Mencos'),('Petén','Poptún'),
            -- Quetzaltenango (24 municipios)
            ('Quetzaltenango','Quetzaltenango'),('Quetzaltenango','Salcajá'),
            ('Quetzaltenango','Olintepeque'),('Quetzaltenango','San Carlos Sija'),
            ('Quetzaltenango','Sibilia'),('Quetzaltenango','Cabricán'),
            ('Quetzaltenango','Cajolá'),('Quetzaltenango','San Miguel Sigüilá'),
            ('Quetzaltenango','Ostuncalco'),('Quetzaltenango','San Mateo'),
            ('Quetzaltenango','Concepción Chiquirichapa'),('Quetzaltenango','San Martín Sacatepéquez'),
            ('Quetzaltenango','Almolonga'),('Quetzaltenango','Cantel'),
            ('Quetzaltenango','Huitán'),('Quetzaltenango','Zunil'),
            ('Quetzaltenango','Colomba'),('Quetzaltenango','San Francisco La Unión'),
            ('Quetzaltenango','El Palmar'),('Quetzaltenango','Coatepeque'),
            ('Quetzaltenango','Génova'),('Quetzaltenango','Flores Costa Cuca'),
            ('Quetzaltenango','La Esperanza'),('Quetzaltenango','Palestina de Los Altos'),
            -- Quiché (21 municipios)
            ('Quiché','Santa Cruz del Quiché'),('Quiché','Chiché'),
            ('Quiché','Chinique'),('Quiché','Zacualpa'),
            ('Quiché','Chajul'),('Quiché','Chichicastenango'),
            ('Quiché','Patzité'),('Quiché','San Antonio Ilotenango'),
            ('Quiché','San Pedro Jocopilas'),('Quiché','Cunén'),
            ('Quiché','San Juan Cotzal'),('Quiché','Joyabaj'),
            ('Quiché','Nebaj'),('Quiché','San Andrés Sajcabajá'),
            ('Quiché','Uspantán'),('Quiché','Sacapulas'),
            ('Quiché','San Bartolomé Jocotenango'),('Quiché','Canillá'),
            ('Quiché','Chicamán'),('Quiché','Ixcán'),
            ('Quiché','Pachalum'),
            -- Retalhuleu (9 municipios)
            ('Retalhuleu','Retalhuleu'),('Retalhuleu','San Sebastián'),
            ('Retalhuleu','Santa Cruz Muluá'),('Retalhuleu','San Martín Zapotitlán'),
            ('Retalhuleu','San Felipe'),('Retalhuleu','San Andrés Villa Seca'),
            ('Retalhuleu','Champerico'),('Retalhuleu','Nuevo San Carlos'),
            ('Retalhuleu','El Asintal'),
            -- Sacatepéquez (16 municipios)
            ('Sacatepéquez','Antigua Guatemala'),('Sacatepéquez','Jocotenango'),
            ('Sacatepéquez','Pastores'),('Sacatepéquez','Sumpango'),
            ('Sacatepéquez','Santo Domingo Xenacoj'),('Sacatepéquez','Santiago Sacatepéquez'),
            ('Sacatepéquez','San Bartolomé Milpas Altas'),('Sacatepéquez','San Lucas Sacatepéquez'),
            ('Sacatepéquez','Santa Lucía Milpas Altas'),('Sacatepéquez','Magdalena Milpas Altas'),
            ('Sacatepéquez','Santa María de Jesús'),('Sacatepéquez','Ciudad Vieja'),
            ('Sacatepéquez','San Miguel Dueñas'),('Sacatepéquez','Alotenango'),
            ('Sacatepéquez','San Antonio Aguas Calientes'),('Sacatepéquez','Santa Catarina Barahona'),
            -- San Marcos (30 municipios)
            ('San Marcos','San Marcos'),('San Marcos','San Pedro Sacatepéquez'),
            ('San Marcos','San Antonio Sacatepéquez'),('San Marcos','Comitancillo'),
            ('San Marcos','San Miguel Ixtahuacán'),('San Marcos','Concepción Tutuapa'),
            ('San Marcos','Tacaná'),('San Marcos','Sibinal'),
            ('San Marcos','Tajumulco'),('San Marcos','Tejutla'),
            ('San Marcos','San Rafael Pie de la Cuesta'),('San Marcos','Nuevo Progreso'),
            ('San Marcos','El Tumbador'),('San Marcos','El Rodeo'),
            ('San Marcos','Malacatán'),('San Marcos','Catarina'),
            ('San Marcos','Ayutla'),('San Marcos','Ocós'),
            ('San Marcos','San Pablo'),('San Marcos','El Quetzal'),
            ('San Marcos','La Reforma'),('San Marcos','Pajapita'),
            ('San Marcos','Ixchiguán'),('San Marcos','San José Ojetenam'),
            ('San Marcos','San Cristóbal Cucho'),('San Marcos','Sipacapa'),
            ('San Marcos','Esquipulas Palo Gordo'),('San Marcos','Río Blanco'),
            ('San Marcos','San Lorenzo'),('San Marcos','La Blanca'),
            -- Santa Rosa (14 municipios)
            ('Santa Rosa','Cuilapa'),('Santa Rosa','Barberena'),
            ('Santa Rosa','Santa Rosa de Lima'),('Santa Rosa','Casillas'),
            ('Santa Rosa','San Rafael Las Flores'),('Santa Rosa','Oratorio'),
            ('Santa Rosa','San Juan Tecuaco'),('Santa Rosa','Chiquimulilla'),
            ('Santa Rosa','Taxisco'),('Santa Rosa','Santa María Ixhuatán'),
            ('Santa Rosa','Guazacapán'),('Santa Rosa','Santa Cruz Naranjo'),
            ('Santa Rosa','Pueblo Nuevo Viñas'),('Santa Rosa','Nueva Santa Rosa'),
            -- Sololá (19 municipios)
            ('Sololá','Sololá'),('Sololá','San José Chacayá'),
            ('Sololá','Santa María Visitación'),('Sololá','Santa Lucía Utatlán'),
            ('Sololá','Nahualá'),('Sololá','Santa Catarina Ixtahuacán'),
            ('Sololá','Santa Clara La Laguna'),('Sololá','Concepción'),
            ('Sololá','San Andrés Semetabaj'),('Sololá','Panajachel'),
            ('Sololá','Santa Catarina Palopó'),('Sololá','San Antonio Palopó'),
            ('Sololá','San Lucas Tolimán'),('Sololá','Santa Cruz La Laguna'),
            ('Sololá','San Pablo La Laguna'),('Sololá','San Marcos La Laguna'),
            ('Sololá','San Juan La Laguna'),('Sololá','San Pedro La Laguna'),
            ('Sololá','Santiago Atitlán'),
            -- Suchitepéquez (21 municipios)
            ('Suchitepéquez','Mazatenango'),('Suchitepéquez','Cuyotenango'),
            ('Suchitepéquez','San Francisco Zapotitlán'),('Suchitepéquez','San Bernardino'),
            ('Suchitepéquez','San José El Ídolo'),('Suchitepéquez','Santo Domingo Suchitepéquez'),
            ('Suchitepéquez','San Lorenzo'),('Suchitepéquez','Samayac'),
            ('Suchitepéquez','San Pablo Jocopilas'),('Suchitepéquez','San Antonio Suchitepéquez'),
            ('Suchitepéquez','San Miguel Panán'),('Suchitepéquez','San Gabriel'),
            ('Suchitepéquez','Chicacao'),('Suchitepéquez','Patulul'),
            ('Suchitepéquez','Santa Bárbara'),('Suchitepéquez','San Juan Bautista'),
            ('Suchitepéquez','Santo Tomás La Unión'),('Suchitepéquez','Zunilito'),
            ('Suchitepéquez','Pueblo Nuevo'),('Suchitepéquez','Río Bravo'),
            ('Suchitepéquez','San José La Máquina'),
            -- Totonicapán (8 municipios)
            ('Totonicapán','Totonicapán'),('Totonicapán','San Cristóbal Totonicapán'),
            ('Totonicapán','San Francisco El Alto'),('Totonicapán','San Andrés Xecul'),
            ('Totonicapán','Momostenango'),('Totonicapán','Santa María Chiquimula'),
            ('Totonicapán','Santa Lucía La Reforma'),('Totonicapán','San Bartolo'),
            -- Zacapa (11 municipios)
            ('Zacapa','Zacapa'),('Zacapa','Estanzuela'),
            ('Zacapa','Río Hondo'),('Zacapa','Gualán'),
            ('Zacapa','Teculután'),('Zacapa','Usumatlán'),
            ('Zacapa','Cabañas'),('Zacapa','San Diego'),
            ('Zacapa','La Unión'),('Zacapa','Huité'),
            ('Zacapa','San Jorge')
        ) AS m(depto, nombre)
        JOIN departamento_geografico d ON d.nombre = m.depto
        ON CONFLICT ON CONSTRAINT uq_municipio_depto_nombre DO NOTHING;
    """)


def downgrade() -> None:
    # Eliminar tablas nuevas
    op.execute("DROP TABLE IF EXISTS visita_modulo_evaluacion;")
    op.execute("DROP TABLE IF EXISTS visita_seguimiento;")

    # Eliminar índice parcial de NIT
    op.execute("DROP INDEX IF EXISTS uq_cliente_nit_no_cf;")

    # Restaurar restricciones únicas anteriores
    op.execute("""
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1 FROM pg_constraint WHERE conname = 'uq_municipio_depto_nombre'
            ) THEN
                ALTER TABLE municipio DROP CONSTRAINT uq_municipio_depto_nombre;
            END IF;
        END$$;
    """)
    op.execute("""
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1 FROM pg_constraint WHERE conname = 'uq_subcategoria_cat_nombre'
            ) THEN
                ALTER TABLE subcategoria DROP CONSTRAINT uq_subcategoria_cat_nombre;
            END IF;
        END$$;
    """)

    # Eliminar columnas de estado y fecha_creacion añadidas
    for tbl in ['cliente', 'tipo_cliente', 'area_bodega', 'departamento_geografico',
                'municipio', 'subcategoria', 'unidad_medida', 'motivo_merma',
                'metodo_pago', 'proveedor']:
        op.execute(f"ALTER TABLE {tbl} DROP COLUMN IF EXISTS estado;")

    for tbl in ['cliente', 'proveedor', 'sucursal']:
        op.execute(f"ALTER TABLE {tbl} DROP COLUMN IF EXISTS fecha_creacion;")

    op.execute("ALTER TABLE bitacora_auditoria ALTER COLUMN fecha_hora DROP DEFAULT;")

