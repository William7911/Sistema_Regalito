-- Script de inicialización para Tienda el Regalito POS
-- Enfoque Database First — Diccionario de Datos DERCAS (42 tablas / 7 módulos)
-- Ejecuta SOLO la primera vez que se levanta el contenedor (volumen vacío).
-- Para re-aplicar sobre datos existentes, borrar el volumen (ver README al final).

-- ============================================================================
-- MÓDULO 1: SEGURIDAD Y AUDITORÍA
-- ============================================================================

CREATE TABLE rol (
    id_rol SERIAL PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL UNIQUE,
    descripcion VARCHAR(150),
    estado VARCHAR(20) NOT NULL CHECK (estado IN ('Activo', 'Inactivo'))
);

CREATE TABLE usuario (
    id_usuario SERIAL PRIMARY KEY,
    id_rol INT NOT NULL REFERENCES rol(id_rol),
    nombre_completo VARCHAR(100) NOT NULL,
    username VARCHAR(50) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    estado VARCHAR(20) NOT NULL CHECK (estado IN ('Activo', 'Inactivo')),
    fecha_creacion TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE permiso (
    id_permiso SERIAL PRIMARY KEY,
    modulo VARCHAR(50) NOT NULL,
    codigo VARCHAR(50) NOT NULL UNIQUE,
    descripcion VARCHAR(150)
);

CREATE TABLE rol_permiso (
    id_rol INT NOT NULL REFERENCES rol(id_rol),
    id_permiso INT NOT NULL REFERENCES permiso(id_permiso),
    PRIMARY KEY (id_rol, id_permiso)
);

CREATE TABLE sesion_usuario (
    id_sesion SERIAL PRIMARY KEY,
    id_usuario INT NOT NULL REFERENCES usuario(id_usuario),
    fecha_inicio TIMESTAMP NOT NULL,
    fecha_fin TIMESTAMP,
    ip_origen VARCHAR(45)
);

CREATE TABLE bitacora_auditoria (
    id_bitacora SERIAL PRIMARY KEY,
    id_usuario INT NOT NULL REFERENCES usuario(id_usuario),
    tabla_afectada VARCHAR(50) NOT NULL,
    accion VARCHAR(20) NOT NULL,
    descripcion TEXT NOT NULL,
    fecha_hora TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE parametro_sistema (
    id_parametro SERIAL PRIMARY KEY,
    clave VARCHAR(50) NOT NULL UNIQUE,
    valor VARCHAR(255) NOT NULL
);

CREATE TABLE intento_login (
    id_intento SERIAL PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    intentos_fallidos INT NOT NULL DEFAULT 0,
    bloqueado_hasta TIMESTAMP,
    ultimo_intento TIMESTAMP NOT NULL DEFAULT NOW()
);

-- ============================================================================
-- MÓDULO 2: SUCURSALES, UBICACIÓN Y CLIENTES
-- ============================================================================

CREATE TABLE sucursal (
    id_sucursal SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    direccion VARCHAR(200) NOT NULL,
    telefono VARCHAR(20),
    estado VARCHAR(20) NOT NULL CHECK (estado IN ('Activo', 'Inactivo')),
    fecha_creacion TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE area_bodega (
    id_area SERIAL PRIMARY KEY,
    id_sucursal INT NOT NULL REFERENCES sucursal(id_sucursal),
    nombre_area VARCHAR(50) NOT NULL,
    estado VARCHAR(20) NOT NULL DEFAULT 'Activo' CHECK (estado IN ('Activo', 'Inactivo'))
);

CREATE TABLE departamento_geografico (
    id_departamento SERIAL PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL UNIQUE,
    estado VARCHAR(20) NOT NULL DEFAULT 'Activo' CHECK (estado IN ('Activo', 'Inactivo'))
);

CREATE TABLE municipio (
    id_municipio SERIAL PRIMARY KEY,
    id_departamento INT NOT NULL REFERENCES departamento_geografico(id_departamento),
    nombre VARCHAR(50) NOT NULL,
    estado VARCHAR(20) NOT NULL DEFAULT 'Activo' CHECK (estado IN ('Activo', 'Inactivo')),
    CONSTRAINT uq_municipio_depto_nombre UNIQUE (id_departamento, nombre)
);

CREATE TABLE tipo_cliente (
    id_tipo_cliente SERIAL PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL,
    descuento_predeterminado DECIMAL(5,2),
    estado VARCHAR(20) NOT NULL DEFAULT 'Activo' CHECK (estado IN ('Activo', 'Inactivo'))
);

CREATE TABLE cliente (
    id_cliente SERIAL PRIMARY KEY,
    id_tipo_cliente INT NOT NULL REFERENCES tipo_cliente(id_tipo_cliente),
    id_municipio INT REFERENCES municipio(id_municipio),
    nit VARCHAR(15) NOT NULL,
    nombre_comercial VARCHAR(120) NOT NULL,
    direccion VARCHAR(200),
    estado VARCHAR(20) NOT NULL DEFAULT 'Activo' CHECK (estado IN ('Activo', 'Inactivo')),
    fecha_creacion TIMESTAMP NOT NULL DEFAULT NOW()
);
CREATE UNIQUE INDEX IF NOT EXISTS uq_cliente_nit_no_cf ON cliente (nit) WHERE nit <> 'CF';

CREATE TABLE cliente_contacto (
    id_contacto SERIAL PRIMARY KEY,
    id_cliente INT NOT NULL REFERENCES cliente(id_cliente),
    telefono VARCHAR(20),
    correo VARCHAR(100)
);

-- ============================================================================
-- MÓDULO 3: CATÁLOGO E INVENTARIO
-- ============================================================================

CREATE TABLE categoria (
    id_categoria SERIAL PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL UNIQUE,
    estado VARCHAR(20) NOT NULL CHECK (estado IN ('Activo', 'Inactivo'))
);

CREATE TABLE subcategoria (
    id_subcategoria SERIAL PRIMARY KEY,
    id_categoria INT NOT NULL REFERENCES categoria(id_categoria),
    nombre VARCHAR(50) NOT NULL,
    estado VARCHAR(20) NOT NULL DEFAULT 'Activo' CHECK (estado IN ('Activo', 'Inactivo')),
    CONSTRAINT uq_subcategoria_cat_nombre UNIQUE (id_categoria, nombre)
);

CREATE TABLE unidad_medida (
    id_unidad SERIAL PRIMARY KEY,
    codigo VARCHAR(10) NOT NULL UNIQUE,
    descripcion VARCHAR(50) NOT NULL,
    estado VARCHAR(20) NOT NULL DEFAULT 'Activo' CHECK (estado IN ('Activo', 'Inactivo'))
);

CREATE TABLE producto (
    id_producto SERIAL PRIMARY KEY,
    id_subcategoria INT NOT NULL REFERENCES subcategoria(id_subcategoria),
    id_unidad INT NOT NULL REFERENCES unidad_medida(id_unidad),
    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT,
    imagen_url VARCHAR(255),
    estado VARCHAR(20) NOT NULL CHECK (estado IN ('Activo', 'Inactivo')),
    fecha_creacion TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE variante_producto (
    id_variante SERIAL PRIMARY KEY,
    id_producto INT NOT NULL REFERENCES producto(id_producto),
    codigo_barras VARCHAR(50) UNIQUE,
    talla VARCHAR(20),
    color VARCHAR(30),
    precio_detalle DECIMAL(10,2) NOT NULL,
    precio_mayoreo DECIMAL(10,2) NOT NULL,
    costo_promedio DECIMAL(10,2) NOT NULL
);

CREATE TABLE inventario_sucursal (
    id_inventario SERIAL PRIMARY KEY,
    id_variante INT NOT NULL REFERENCES variante_producto(id_variante),
    id_sucursal INT NOT NULL REFERENCES sucursal(id_sucursal),
    id_area INT REFERENCES area_bodega(id_area),
    stock_actual INT NOT NULL CHECK (stock_actual >= 0),
    stock_minimo INT NOT NULL CHECK (stock_minimo >= 0),
    fecha_actualizacion TIMESTAMP NOT NULL
);

CREATE TABLE historial_precio (
    id_historial SERIAL PRIMARY KEY,
    id_variante INT NOT NULL REFERENCES variante_producto(id_variante),
    id_usuario INT NOT NULL REFERENCES usuario(id_usuario),
    precio_anterior DECIMAL(10,2) NOT NULL,
    precio_nuevo DECIMAL(10,2) NOT NULL,
    fecha_modificacion TIMESTAMP NOT NULL
);

CREATE TABLE alerta_stock (
    id_alerta SERIAL PRIMARY KEY,
    id_inventario INT NOT NULL REFERENCES inventario_sucursal(id_inventario),
    mensaje VARCHAR(150) NOT NULL,
    fecha_generacion TIMESTAMP NOT NULL,
    estado VARCHAR(20) NOT NULL CHECK (estado IN ('Pendiente', 'Atendida', 'Descartada'))
);

-- ============================================================================
-- MÓDULO 4: MOVIMIENTOS Y MERMAS
-- ============================================================================

CREATE TABLE motivo_merma (
    id_motivo SERIAL PRIMARY KEY,
    descripcion VARCHAR(100) NOT NULL,
    estado VARCHAR(20) NOT NULL DEFAULT 'Activo' CHECK (estado IN ('Activo', 'Inactivo'))
);

CREATE TABLE merma (
    id_merma SERIAL PRIMARY KEY,
    id_sucursal INT NOT NULL REFERENCES sucursal(id_sucursal),
    id_usuario INT NOT NULL REFERENCES usuario(id_usuario),
    fecha_merma TIMESTAMP NOT NULL,
    observaciones TEXT
);

CREATE TABLE detalle_merma (
    id_detalle_merma SERIAL PRIMARY KEY,
    id_merma INT NOT NULL REFERENCES merma(id_merma),
    id_variante INT NOT NULL REFERENCES variante_producto(id_variante),
    id_motivo INT NOT NULL REFERENCES motivo_merma(id_motivo),
    cantidad INT NOT NULL CHECK (cantidad >= 0),
    costo_perdida DECIMAL(10,2) NOT NULL
);

CREATE TABLE traslado_inventario (
    id_traslado SERIAL PRIMARY KEY,
    id_variante INT NOT NULL REFERENCES variante_producto(id_variante),
    id_sucursal_origen INT NOT NULL REFERENCES sucursal(id_sucursal),
    id_sucursal_destino INT NOT NULL REFERENCES sucursal(id_sucursal),
    cantidad INT NOT NULL CHECK (cantidad > 0),
    fecha_traslado TIMESTAMP NOT NULL DEFAULT NOW(),
    estado VARCHAR(20) NOT NULL DEFAULT 'En tránsito' CHECK (estado IN ('En tránsito', 'Recibido', 'Cancelado')),
    id_usuario_envia INT REFERENCES usuario(id_usuario),
    id_usuario_recibe INT REFERENCES usuario(id_usuario),
    fecha_recepcion TIMESTAMP,
    observaciones TEXT
);

-- ============================================================================
-- MÓDULO 5: CAJA, TURNOS Y TESORERÍA
-- ============================================================================

CREATE TABLE caja (
    id_caja SERIAL PRIMARY KEY,
    id_sucursal INT NOT NULL REFERENCES sucursal(id_sucursal),
    descripcion VARCHAR(50) NOT NULL,
    estado VARCHAR(20) NOT NULL CHECK (estado IN ('Activa', 'Inactiva', 'Activo', 'Inactivo'))
);

CREATE TABLE turno_caja (
    id_turno SERIAL PRIMARY KEY,
    id_caja INT NOT NULL REFERENCES caja(id_caja),
    id_usuario INT NOT NULL REFERENCES usuario(id_usuario),
    monto_apertura DECIMAL(10,2) NOT NULL,
    fecha_apertura TIMESTAMP NOT NULL,
    fecha_cierre TIMESTAMP,
    estado VARCHAR(20) NOT NULL CHECK (estado IN ('Abierto', 'Cerrado', 'Abierta', 'Cerrada')),
    monto_cierre DECIMAL(10,2),
    notas TEXT
);

CREATE TABLE tipo_movimiento_caja (
    id_tipo_movimiento SERIAL PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL
);

CREATE TABLE movimiento_caja (
    id_movimiento SERIAL PRIMARY KEY,
    id_turno INT NOT NULL REFERENCES turno_caja(id_turno),
    id_tipo_movimiento INT NOT NULL REFERENCES tipo_movimiento_caja(id_tipo_movimiento),
    id_usuario INT NOT NULL REFERENCES usuario(id_usuario),
    monto DECIMAL(10,2) NOT NULL,
    justificacion VARCHAR(255) NOT NULL,
    fecha_hora TIMESTAMP NOT NULL
);

CREATE TABLE cierre_caja_ciegas (
    id_cierre SERIAL PRIMARY KEY,
    id_turno INT NOT NULL REFERENCES turno_caja(id_turno),
    id_usuario_cajero INT NOT NULL REFERENCES usuario(id_usuario),
    id_usuario_supervisor INT NOT NULL REFERENCES usuario(id_usuario),
    total_contado_ciegas DECIMAL(10,2) NOT NULL,
    total_calculado_sistema DECIMAL(10,2) NOT NULL,
    diferencia DECIMAL(10,2) NOT NULL,
    observaciones TEXT,
    fecha_cierre TIMESTAMP NOT NULL
);

CREATE TABLE denominacion_efectivo (
    id_denominacion SERIAL PRIMARY KEY,
    valor DECIMAL(10,2) NOT NULL,
    tipo VARCHAR(15) NOT NULL
);

CREATE TABLE detalle_arqueo_efectivo (
    id_detalle_arqueo SERIAL PRIMARY KEY,
    id_cierre INT NOT NULL REFERENCES cierre_caja_ciegas(id_cierre),
    id_denominacion INT NOT NULL REFERENCES denominacion_efectivo(id_denominacion),
    cantidad_piezas INT NOT NULL CHECK (cantidad_piezas >= 0),
    subtotal DECIMAL(10,2) NOT NULL
);

-- ============================================================================
-- MÓDULO 6: VENTAS, COBROS Y FACTURACIÓN
-- ============================================================================

CREATE TABLE metodo_pago (
    id_metodo_pago SERIAL PRIMARY KEY,
    nombre VARCHAR(30) NOT NULL,
    estado VARCHAR(20) NOT NULL DEFAULT 'Activo' CHECK (estado IN ('Activo', 'Inactivo'))
);

CREATE TABLE venta (
    id_venta SERIAL PRIMARY KEY,
    id_turno INT NOT NULL REFERENCES turno_caja(id_turno),
    id_cliente INT REFERENCES cliente(id_cliente),
    id_usuario INT NOT NULL REFERENCES usuario(id_usuario),
    fecha_venta TIMESTAMP NOT NULL,
    subtotal DECIMAL(10,2) NOT NULL,
    descuento_total DECIMAL(10,2) NOT NULL,
    total_venta DECIMAL(10,2) NOT NULL,
    estado VARCHAR(20) NOT NULL CHECK (estado IN ('Completada', 'Anulada'))
);

CREATE TABLE detalle_venta (
    id_detalle_venta SERIAL PRIMARY KEY,
    id_venta INT NOT NULL REFERENCES venta(id_venta),
    id_variante INT NOT NULL REFERENCES variante_producto(id_variante),
    cantidad INT NOT NULL CHECK (cantidad >= 0),
    precio_unitario DECIMAL(10,2) NOT NULL,
    descuento_item DECIMAL(10,2) NOT NULL,
    subtotal DECIMAL(10,2) NOT NULL
);

CREATE TABLE pago_venta (
    id_pago SERIAL PRIMARY KEY,
    id_venta INT NOT NULL REFERENCES venta(id_venta),
    id_metodo_pago INT NOT NULL REFERENCES metodo_pago(id_metodo_pago),
    monto_recibido DECIMAL(10,2) NOT NULL,
    vuelto_entregado DECIMAL(10,2) NOT NULL
);

CREATE TABLE factura_fel (
    id_factura SERIAL PRIMARY KEY,
    id_venta INT NOT NULL REFERENCES venta(id_venta),
    numero_autorizacion_sat VARCHAR(50),
    serie VARCHAR(20),
    numero_dte VARCHAR(30) UNIQUE,
    fecha_certificacion TIMESTAMP,
    nit_receptor VARCHAR(15) NOT NULL,
    nombre_receptor VARCHAR(120) NOT NULL,
    total_facturado DECIMAL(10,2) NOT NULL,
    estado VARCHAR(20) NOT NULL DEFAULT 'Certificada'
);

-- ============================================================================
-- MÓDULO 7: COMPRAS Y PROVEEDORES
-- ============================================================================

CREATE TABLE proveedor (
    id_proveedor SERIAL PRIMARY KEY,
    nombre_contacto VARCHAR(100) NOT NULL,
    distribuidora VARCHAR(100) NOT NULL,
    telefono VARCHAR(20),
    correo VARCHAR(100),
    cuenta_bancaria VARCHAR(50),
    direccion VARCHAR(150),
    estado VARCHAR(20) NOT NULL DEFAULT 'Activo' CHECK (estado IN ('Activo', 'Inactivo')),
    fecha_creacion TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE orden_compra (
    id_orden SERIAL PRIMARY KEY,
    id_proveedor INT NOT NULL REFERENCES proveedor(id_proveedor),
    id_usuario INT NOT NULL REFERENCES usuario(id_usuario),
    fecha_emision DATE NOT NULL,
    total_estimado DECIMAL(10,2) NOT NULL,
    estado VARCHAR(20) NOT NULL CHECK (estado IN ('Emitida', 'Recibida', 'Cancelada'))
);

CREATE TABLE detalle_orden_compra (
    id_detalle_orden SERIAL PRIMARY KEY,
    id_orden INT NOT NULL REFERENCES orden_compra(id_orden),
    id_variante INT NOT NULL REFERENCES variante_producto(id_variante),
    cantidad_pedida INT NOT NULL CHECK (cantidad_pedida >= 0),
    costo_pactado DECIMAL(10,2) NOT NULL
);

CREATE TABLE compra (
    id_compra SERIAL PRIMARY KEY,
    id_orden INT REFERENCES orden_compra(id_orden),
    id_proveedor INT NOT NULL REFERENCES proveedor(id_proveedor),
    id_usuario INT NOT NULL REFERENCES usuario(id_usuario),
    numero_factura_proveedor VARCHAR(50) NOT NULL,
    fecha_ingreso DATE NOT NULL,
    subtotal_mercaderia DECIMAL(10,2) NOT NULL,
    gasto_flete DECIMAL(10,2) NOT NULL,
    gasto_cargadores DECIMAL(10,2) NOT NULL,
    total_compra DECIMAL(10,2) NOT NULL
);

CREATE TABLE detalle_compra (
    id_detalle_compra SERIAL PRIMARY KEY,
    id_compra INT NOT NULL REFERENCES compra(id_compra),
    id_variante INT NOT NULL REFERENCES variante_producto(id_variante),
    cantidad_recibida INT NOT NULL CHECK (cantidad_recibida >= 0),
    costo_unitario DECIMAL(10,2) NOT NULL,
    subtotal DECIMAL(10,2) NOT NULL
);



-- ============================================================================
-- MÓDULO 8: VISITAS DE SEGUIMIENTO
-- ============================================================================

CREATE TABLE IF NOT EXISTS visita_seguimiento (
    id_visita SERIAL PRIMARY KEY,
    id_cliente INT REFERENCES cliente(id_cliente),
    id_usuario INT NOT NULL REFERENCES usuario(id_usuario),
    fecha_visita DATE NOT NULL,
    lugar VARCHAR(150),
    nombre_representante VARCHAR(150),
    cargo_representante VARCHAR(100),
    calificacion_general SMALLINT CHECK (calificacion_general BETWEEN 1 AND 5),
    observaciones TEXT,
    estado VARCHAR(20) NOT NULL DEFAULT 'Borrador' CHECK (estado IN ('Borrador','Pendiente','Completada','Cancelada')),
    fecha_creacion TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS visita_modulo_evaluacion (
    id_modulo_eval SERIAL PRIMARY KEY,
    id_visita INT NOT NULL REFERENCES visita_seguimiento(id_visita) ON DELETE CASCADE,
    nombre_modulo VARCHAR(100) NOT NULL,
    resultado VARCHAR(20) CHECK (resultado IN ('Conforme','Modificar','Agregar')),
    calificacion SMALLINT CHECK (calificacion BETWEEN 1 AND 10),
    comentario TEXT,
    CONSTRAINT uq_visita_modulo UNIQUE (id_visita, nombre_modulo)
);

-- ============================================================================
-- ÍNDICES PARA LLAVES FORÁNEAS (OPTIMIZACIÓN DE CONSULTAS Y REPORTES)
-- ============================================================================

-- Por Usuario
CREATE INDEX IF NOT EXISTS idx_bitacora_auditoria_id_usuario ON bitacora_auditoria (id_usuario);
CREATE INDEX IF NOT EXISTS idx_cierre_ciegas_cajero ON cierre_caja_ciegas (id_usuario_cajero);
CREATE INDEX IF NOT EXISTS idx_cierre_ciegas_supervisor ON cierre_caja_ciegas (id_usuario_supervisor);
CREATE INDEX IF NOT EXISTS idx_compra_id_usuario ON compra (id_usuario);
CREATE INDEX IF NOT EXISTS idx_historial_precio_id_usuario ON historial_precio (id_usuario);
CREATE INDEX IF NOT EXISTS idx_merma_id_usuario ON merma (id_usuario);
CREATE INDEX IF NOT EXISTS idx_movimiento_caja_id_usuario ON movimiento_caja (id_usuario);
CREATE INDEX IF NOT EXISTS idx_orden_compra_id_usuario ON orden_compra (id_usuario);
CREATE INDEX IF NOT EXISTS idx_sesion_usuario_id_usuario ON sesion_usuario (id_usuario);
CREATE INDEX IF NOT EXISTS idx_turno_caja_id_usuario ON turno_caja (id_usuario);
CREATE INDEX IF NOT EXISTS idx_venta_id_usuario ON venta (id_usuario);

-- Por Variante de Producto
CREATE INDEX IF NOT EXISTS idx_inventario_sucursal_id_variante ON inventario_sucursal (id_variante);
CREATE INDEX IF NOT EXISTS idx_detalle_venta_id_variante ON detalle_venta (id_variante);
CREATE INDEX IF NOT EXISTS idx_detalle_compra_id_variante ON detalle_compra (id_variante);
CREATE INDEX IF NOT EXISTS idx_detalle_orden_compra_id_variante ON detalle_orden_compra (id_variante);
CREATE INDEX IF NOT EXISTS idx_detalle_merma_id_variante ON detalle_merma (id_variante);
CREATE INDEX IF NOT EXISTS idx_traslado_inventario_id_variante ON traslado_inventario (id_variante);
CREATE INDEX IF NOT EXISTS idx_historial_precio_id_variante ON historial_precio (id_variante);

-- Por Sucursal
CREATE INDEX IF NOT EXISTS idx_caja_id_sucursal ON caja (id_sucursal);
CREATE INDEX IF NOT EXISTS idx_area_bodega_id_sucursal ON area_bodega (id_sucursal);
CREATE INDEX IF NOT EXISTS idx_inventario_sucursal_id_sucursal ON inventario_sucursal (id_sucursal);
CREATE INDEX IF NOT EXISTS idx_merma_id_sucursal ON merma (id_sucursal);
CREATE INDEX IF NOT EXISTS idx_traslado_inventario_origen ON traslado_inventario (id_sucursal_origen);
CREATE INDEX IF NOT EXISTS idx_traslado_inventario_destino ON traslado_inventario (id_sucursal_destino);

-- Por Venta
CREATE INDEX IF NOT EXISTS idx_detalle_venta_id_venta ON detalle_venta (id_venta);
CREATE INDEX IF NOT EXISTS idx_pago_venta_id_venta ON pago_venta (id_venta);
CREATE INDEX IF NOT EXISTS idx_factura_fel_id_venta ON factura_fel (id_venta);

-- Por Turno de Caja
CREATE INDEX IF NOT EXISTS idx_venta_id_turno ON venta (id_turno);
CREATE INDEX IF NOT EXISTS idx_cierre_caja_ciegas_id_turno ON cierre_caja_ciegas (id_turno);
CREATE INDEX IF NOT EXISTS idx_movimiento_caja_id_turno ON movimiento_caja (id_turno);

-- Otras Llaves Foráneas Críticas
CREATE INDEX IF NOT EXISTS idx_usuario_id_rol ON usuario (id_rol);
CREATE INDEX IF NOT EXISTS idx_producto_id_subcategoria ON producto (id_subcategoria);
CREATE INDEX IF NOT EXISTS idx_producto_id_unidad ON producto (id_unidad);
CREATE INDEX IF NOT EXISTS idx_subcategoria_id_categoria ON subcategoria (id_categoria);
CREATE INDEX IF NOT EXISTS idx_variante_producto_id_producto ON variante_producto (id_producto);
CREATE INDEX IF NOT EXISTS idx_alerta_stock_id_inventario ON alerta_stock (id_inventario);
CREATE INDEX IF NOT EXISTS idx_turno_caja_id_caja ON turno_caja (id_caja);
CREATE INDEX IF NOT EXISTS idx_venta_id_cliente ON venta (id_cliente);
CREATE INDEX IF NOT EXISTS idx_cliente_id_tipo_cliente ON cliente (id_tipo_cliente);
CREATE INDEX IF NOT EXISTS idx_cliente_id_municipio ON cliente (id_municipio);
CREATE INDEX IF NOT EXISTS idx_cliente_contacto_id_cliente ON cliente_contacto (id_cliente);
CREATE INDEX IF NOT EXISTS idx_compra_id_orden ON compra (id_orden);
CREATE INDEX IF NOT EXISTS idx_compra_id_proveedor ON compra (id_proveedor);
CREATE INDEX IF NOT EXISTS idx_detalle_compra_id_compra ON detalle_compra (id_compra);
CREATE INDEX IF NOT EXISTS idx_detalle_orden_compra_id_orden ON detalle_orden_compra (id_orden);
CREATE INDEX IF NOT EXISTS idx_orden_compra_id_proveedor ON orden_compra (id_proveedor);
CREATE INDEX IF NOT EXISTS idx_detalle_merma_id_merma ON detalle_merma (id_merma);
CREATE INDEX IF NOT EXISTS idx_detalle_merma_id_motivo ON detalle_merma (id_motivo);
CREATE INDEX IF NOT EXISTS idx_detalle_arqueo_id_cierre ON detalle_arqueo_efectivo (id_cierre);
CREATE INDEX IF NOT EXISTS idx_detalle_arqueo_id_denominacion ON detalle_arqueo_efectivo (id_denominacion);
CREATE INDEX IF NOT EXISTS idx_pago_venta_id_metodo_pago ON pago_venta (id_metodo_pago);
CREATE INDEX IF NOT EXISTS idx_movimiento_caja_id_tipo_movimiento ON movimiento_caja (id_tipo_movimiento);
CREATE INDEX IF NOT EXISTS idx_municipio_id_departamento ON municipio (id_departamento);
CREATE INDEX IF NOT EXISTS idx_inventario_sucursal_id_area ON inventario_sucursal (id_area);

-- ============================================================================
-- DATOS SEMILLA (contextualizados: Cristalería, Ropa, Juguetes, Hogar)
-- ============================================================================

-- MÓDULO 1: Seguridad y Auditoría ------------------------------------------
INSERT INTO rol (id_rol, nombre, descripcion, estado) VALUES
(1, 'Administradora', 'Control total del sistema y arqueos de caja', 'Activo'),
(2, 'Cajero', 'Opera el punto de venta y cobros en mostrador', 'Activo'),
(3, 'Bodeguero', 'Gestiona inventario, mermas y traslados', 'Activo');

-- Contraseña por defecto: admin123 (hash bcrypt)
INSERT INTO usuario (id_usuario, id_rol, nombre_completo, username, password_hash, estado) VALUES
(1, 1, 'Propietaria Regalito', 'admin', '$2b$12$igeDz03pyYibOqQO3WJCY.a/XKMHvAAZ2sfh13w.YT7hurdmKFlpG', 'Activo'),
(2, 2, 'María Xicay', 'cajera', '$2b$12$igeDz03pyYibOqQO3WJCY.a/XKMHvAAZ2sfh13w.YT7hurdmKFlpG', 'Activo'),
(3, 3, 'Pedro Tzoc', 'bodega', '$2b$12$igeDz03pyYibOqQO3WJCY.a/XKMHvAAZ2sfh13w.YT7hurdmKFlpG', 'Activo');

INSERT INTO permiso (id_permiso, modulo, codigo, descripcion) VALUES
(1, 'Ventas', 'VENTA_COBRAR', 'Registrar cobros en mostrador'),
(2, 'Ventas', 'VENTA_APLICAR_DESCUENTO', 'Aplicar descuentos por volumen'),
(3, 'Inventario', 'INV_INGRESAR_MERCADERIA', 'Registrar ingreso de compras'),
(4, 'Caja', 'CAJA_CIERRE_CIEGAS', 'Ejecutar arqueo de caja a ciegas'),
(5, 'Compras', 'COMPRA_EMITIR_ORDEN', 'Emitir órdenes de compra'),
(6, 'Clientes', 'CLIENTE_ADMIN', 'Gestión completa de clientes'),
(7, 'Seguridad', 'BITACORA_CONSULTAR', 'Consultar bitácora de auditoría'),
(8, 'Reportes', 'REPORTE_VER', 'Ver reportes del sistema'),
(9, 'Catálogo', 'CATALOGO_ADMIN', 'Gestión completa de catálogos'),
(10, 'Visitas', 'VISITA_REGISTRAR', 'Registrar y consultar visitas de seguimiento'),
(11, 'Seguridad', 'ROL_ADMIN', 'Gestión completa de roles y permisos'),
(12, 'Seguridad', 'USUARIO_ADMIN', 'Gestión completa de usuarios');

INSERT INTO rol_permiso (id_rol, id_permiso) VALUES
(1,1),(1,2),(1,3),(1,4),(1,5),(1,6),(1,7),(1,8),(1,9),(1,10),(1,11),(1,12),
(2,1),(2,2),
(3,3);

INSERT INTO parametro_sistema (id_parametro, clave, valor) VALUES
(1, 'NIT_EMPRESA', '12345678-9'),
(2, 'IVA_PORCENTAJE', '12'),
(3, 'SERIE_DTE', 'A'),
(4, 'RUTA_LOGO', '/img/logo.png');

-- MÓDULO 2: Sucursales, Ubicación y Clientes -------------------------------
INSERT INTO sucursal (id_sucursal, nombre, direccion, telefono, estado) VALUES
(1, 'Tienda Central Panajachel', 'Callejón Don Fidel, zona 1', '7762-3456', 'Activo');

INSERT INTO area_bodega (id_area, id_sucursal, nombre_area) VALUES
(1, 1, 'Vitrina Principal'),
(2, 1, 'Bodega Fondo'),
(3, 1, 'Mostrador');

INSERT INTO departamento_geografico (id_departamento, nombre, estado) VALUES
(1, 'Sololá', 'Activo'),
(2, 'Quetzaltenango', 'Activo'),
(3, 'Alta Verapaz', 'Activo'),
(4, 'Baja Verapaz', 'Activo'),
(5, 'Chimaltenango', 'Activo'),
(6, 'Chiquimula', 'Activo'),
(7, 'El Progreso', 'Activo'),
(8, 'Escuintla', 'Activo'),
(9, 'Guatemala', 'Activo'),
(10, 'Huehuetenango', 'Activo'),
(11, 'Izabal', 'Activo'),
(12, 'Jalapa', 'Activo'),
(13, 'Jutiapa', 'Activo'),
(14, 'Petén', 'Activo'),
(16, 'Quiché', 'Activo'),
(17, 'Retalhuleu', 'Activo'),
(18, 'Sacatepéquez', 'Activo'),
(19, 'San Marcos', 'Activo'),
(20, 'Santa Rosa', 'Activo'),
(22, 'Suchitepéquez', 'Activo'),
(23, 'Totonicapán', 'Activo'),
(24, 'Zacapa', 'Activo');

INSERT INTO municipio (id_municipio, id_departamento, nombre, estado) VALUES
(1, 1, 'Panajachel', 'Activo'),
(2, 1, 'Sololá', 'Activo'),
(3, 2, 'Quetzaltenango', 'Activo'),
(4, 3, 'Cobán', 'Activo'),
(5, 3, 'Santa Cruz Verapaz', 'Activo'),
(6, 3, 'San Cristóbal Verapaz', 'Activo'),
(7, 3, 'Tactic', 'Activo'),
(8, 3, 'Tamahú', 'Activo'),
(9, 3, 'Tucurú', 'Activo'),
(10, 3, 'Panzós', 'Activo'),
(11, 3, 'Senahú', 'Activo'),
(12, 3, 'San Pedro Carchá', 'Activo'),
(13, 3, 'San Juan Chamelco', 'Activo'),
(14, 3, 'Lanquín', 'Activo'),
(15, 3, 'Cahabón', 'Activo'),
(16, 3, 'Chisec', 'Activo'),
(17, 3, 'Chahal', 'Activo'),
(18, 3, 'Fray Bartolomé de las Casas', 'Activo'),
(19, 3, 'Santa Catalina La Tinta', 'Activo'),
(20, 3, 'Raxruhá', 'Activo'),
(21, 4, 'Salamá', 'Activo'),
(22, 4, 'San Miguel Chicaj', 'Activo'),
(23, 4, 'Rabinal', 'Activo'),
(24, 4, 'Cubulco', 'Activo'),
(25, 4, 'Granados', 'Activo'),
(26, 4, 'El Chol', 'Activo'),
(27, 4, 'San Jerónimo', 'Activo'),
(28, 4, 'Purulhá', 'Activo'),
(29, 5, 'Chimaltenango', 'Activo'),
(30, 5, 'San José Poaquil', 'Activo'),
(31, 5, 'San Martín Jilotepeque', 'Activo'),
(32, 5, 'Comalapa', 'Activo'),
(33, 5, 'Santa Apolonia', 'Activo'),
(34, 5, 'Tecpán Guatemala', 'Activo'),
(35, 5, 'Patzún', 'Activo'),
(36, 5, 'Pochuta', 'Activo'),
(37, 5, 'Patzicía', 'Activo'),
(38, 5, 'Santa Cruz Balanyá', 'Activo'),
(39, 5, 'Acatenango', 'Activo'),
(40, 5, 'Yepocapa', 'Activo'),
(41, 5, 'San Andrés Itzapa', 'Activo'),
(42, 5, 'Parramos', 'Activo'),
(43, 5, 'Zaragoza', 'Activo'),
(44, 5, 'El Tejar', 'Activo'),
(45, 6, 'Chiquimula', 'Activo'),
(46, 6, 'San José La Arada', 'Activo'),
(47, 6, 'San Juan La Ermita', 'Activo'),
(48, 6, 'Jocotán', 'Activo'),
(49, 6, 'Camotán', 'Activo'),
(50, 6, 'Olopa', 'Activo'),
(51, 6, 'Esquipulas', 'Activo'),
(52, 6, 'Concepción Las Minas', 'Activo'),
(53, 6, 'Quezaltepeque', 'Activo'),
(54, 6, 'San Jacinto', 'Activo'),
(55, 6, 'Ipala', 'Activo'),
(56, 7, 'Guastatoya', 'Activo'),
(57, 7, 'Morazán', 'Activo'),
(58, 7, 'San Agustín Acasaguastlán', 'Activo'),
(59, 7, 'San Cristóbal Acasaguastlán', 'Activo'),
(60, 7, 'El Jícaro', 'Activo'),
(61, 7, 'Sansare', 'Activo'),
(62, 7, 'Sanarate', 'Activo'),
(63, 7, 'San Antonio La Paz', 'Activo'),
(64, 8, 'Escuintla', 'Activo'),
(65, 8, 'Santa Lucía Cotzumalguapa', 'Activo'),
(66, 8, 'La Democracia', 'Activo'),
(67, 8, 'Siquinalá', 'Activo'),
(68, 8, 'Masagua', 'Activo'),
(69, 8, 'Tiquisate', 'Activo'),
(70, 8, 'La Gomera', 'Activo'),
(71, 8, 'Guanagazapa', 'Activo'),
(72, 8, 'San José', 'Activo'),
(73, 8, 'Iztapa', 'Activo'),
(74, 8, 'Palín', 'Activo'),
(75, 8, 'San Vicente Pacaya', 'Activo'),
(76, 8, 'Nueva Concepción', 'Activo'),
(77, 9, 'Guatemala', 'Activo'),
(78, 9, 'Santa Catarina Pinula', 'Activo'),
(79, 9, 'San José Pinula', 'Activo'),
(80, 9, 'San José del Golfo', 'Activo'),
(81, 9, 'Palencia', 'Activo'),
(82, 9, 'Chinautla', 'Activo'),
(83, 9, 'San Pedro Ayampuc', 'Activo'),
(84, 9, 'Mixco', 'Activo'),
(85, 9, 'San Pedro Sacatepéquez', 'Activo'),
(86, 9, 'San Juan Sacatepéquez', 'Activo'),
(87, 9, 'San Raymundo', 'Activo'),
(88, 9, 'Chuarrancho', 'Activo'),
(89, 9, 'Fraijanes', 'Activo'),
(90, 9, 'Amatitlán', 'Activo'),
(91, 9, 'Villa Nueva', 'Activo'),
(92, 9, 'Villa Canales', 'Activo'),
(93, 9, 'San Miguel Petapa', 'Activo'),
(94, 10, 'Huehuetenango', 'Activo'),
(95, 10, 'Chiantla', 'Activo'),
(96, 10, 'Malacatancito', 'Activo'),
(97, 10, 'Cuilco', 'Activo'),
(98, 10, 'Nentón', 'Activo'),
(99, 10, 'San Pedro Necta', 'Activo'),
(100, 10, 'Jacaltenango', 'Activo'),
(101, 10, 'Soloma', 'Activo'),
(102, 10, 'Ixtahuacán', 'Activo'),
(103, 10, 'Santa Bárbara', 'Activo'),
(104, 10, 'La Libertad', 'Activo'),
(105, 10, 'La Democracia', 'Activo'),
(106, 10, 'San Miguel Acatán', 'Activo'),
(107, 10, 'San Rafael La Independencia', 'Activo'),
(108, 10, 'Todos Santos Cuchumatán', 'Activo'),
(109, 10, 'San Juan Atitán', 'Activo'),
(110, 10, 'Santa Eulalia', 'Activo'),
(111, 10, 'San Mateo Ixtatán', 'Activo'),
(112, 10, 'Colotenango', 'Activo'),
(113, 10, 'San Sebastián Huehuetenango', 'Activo'),
(114, 10, 'Tectitán', 'Activo'),
(115, 10, 'Concepción Huista', 'Activo'),
(116, 10, 'San Juan Ixcoy', 'Activo'),
(117, 10, 'San Antonio Huista', 'Activo'),
(118, 10, 'San Sebastián Coatán', 'Activo'),
(119, 10, 'Barillas', 'Activo'),
(120, 10, 'Aguacatán', 'Activo'),
(121, 10, 'San Rafael Petzal', 'Activo'),
(122, 10, 'San Gaspar Ixchil', 'Activo'),
(123, 10, 'Santiago Chimaltenango', 'Activo'),
(124, 10, 'Santa Ana Huista', 'Activo'),
(125, 10, 'Unión Cantinil', 'Activo'),
(126, 11, 'Puerto Barrios', 'Activo'),
(127, 11, 'Livingston', 'Activo'),
(128, 11, 'El Estor', 'Activo'),
(129, 11, 'Morales', 'Activo'),
(130, 11, 'Los Amates', 'Activo'),
(131, 12, 'Jalapa', 'Activo'),
(132, 12, 'San Pedro Pinula', 'Activo'),
(133, 12, 'San Luis Jilotepeque', 'Activo'),
(134, 12, 'San Manuel Chaparrón', 'Activo'),
(135, 12, 'San Carlos Alzatate', 'Activo'),
(136, 12, 'Monjas', 'Activo'),
(137, 12, 'Mataquescuintla', 'Activo'),
(138, 13, 'Jutiapa', 'Activo'),
(139, 13, 'El Progreso', 'Activo'),
(140, 13, 'Santa Catarina Mita', 'Activo'),
(141, 13, 'Agua Blanca', 'Activo'),
(142, 13, 'Asunción Mita', 'Activo'),
(143, 13, 'Yupiltepeque', 'Activo'),
(144, 13, 'Atescatempa', 'Activo'),
(145, 13, 'Jerez', 'Activo'),
(146, 13, 'El Adelanto', 'Activo'),
(147, 13, 'Zapotitlán', 'Activo'),
(148, 13, 'Comapa', 'Activo'),
(149, 13, 'Jalpatagua', 'Activo'),
(150, 13, 'Conguaco', 'Activo'),
(151, 13, 'Moyuta', 'Activo'),
(152, 13, 'Pasaco', 'Activo'),
(153, 13, 'San José Acatempa', 'Activo'),
(154, 13, 'Quesada', 'Activo'),
(155, 14, 'Flores', 'Activo'),
(156, 14, 'San José', 'Activo'),
(157, 14, 'San Benito', 'Activo'),
(158, 14, 'San Andrés', 'Activo'),
(159, 14, 'La Libertad', 'Activo'),
(160, 14, 'San Francisco', 'Activo'),
(161, 14, 'Santa Ana', 'Activo'),
(162, 14, 'Dolores', 'Activo'),
(163, 14, 'San Luis', 'Activo'),
(164, 14, 'Sayaxché', 'Activo'),
(165, 14, 'Melchor de Mencos', 'Activo'),
(166, 14, 'Poptún', 'Activo'),
(168, 2, 'Salcajá', 'Activo'),
(169, 2, 'Olintepeque', 'Activo'),
(170, 2, 'San Carlos Sija', 'Activo'),
(171, 2, 'Sibilia', 'Activo'),
(172, 2, 'Cabricán', 'Activo'),
(173, 2, 'Cajolá', 'Activo'),
(174, 2, 'San Miguel Sigüilá', 'Activo'),
(175, 2, 'Ostuncalco', 'Activo'),
(176, 2, 'San Mateo', 'Activo'),
(177, 2, 'Concepción Chiquirichapa', 'Activo'),
(178, 2, 'San Martín Sacatepéquez', 'Activo'),
(179, 2, 'Almolonga', 'Activo'),
(180, 2, 'Cantel', 'Activo'),
(181, 2, 'Huitán', 'Activo'),
(182, 2, 'Zunil', 'Activo'),
(183, 2, 'Colomba', 'Activo'),
(184, 2, 'San Francisco La Unión', 'Activo'),
(185, 2, 'El Palmar', 'Activo'),
(186, 2, 'Coatepeque', 'Activo'),
(187, 2, 'Génova', 'Activo'),
(188, 2, 'Flores Costa Cuca', 'Activo'),
(189, 2, 'La Esperanza', 'Activo'),
(190, 2, 'Palestina de Los Altos', 'Activo'),
(191, 16, 'Santa Cruz del Quiché', 'Activo'),
(192, 16, 'Chiché', 'Activo'),
(193, 16, 'Chinique', 'Activo'),
(194, 16, 'Zacualpa', 'Activo'),
(195, 16, 'Chajul', 'Activo'),
(196, 16, 'Chichicastenango', 'Activo'),
(197, 16, 'Patzité', 'Activo'),
(198, 16, 'San Antonio Ilotenango', 'Activo'),
(199, 16, 'San Pedro Jocopilas', 'Activo'),
(200, 16, 'Cunén', 'Activo'),
(201, 16, 'San Juan Cotzal', 'Activo'),
(202, 16, 'Joyabaj', 'Activo'),
(203, 16, 'Nebaj', 'Activo'),
(204, 16, 'San Andrés Sajcabajá', 'Activo'),
(205, 16, 'Uspantán', 'Activo'),
(206, 16, 'Sacapulas', 'Activo'),
(207, 16, 'San Bartolomé Jocotenango', 'Activo'),
(208, 16, 'Canillá', 'Activo'),
(209, 16, 'Chicamán', 'Activo'),
(210, 16, 'Ixcán', 'Activo'),
(211, 16, 'Pachalum', 'Activo'),
(212, 17, 'Retalhuleu', 'Activo'),
(213, 17, 'San Sebastián', 'Activo'),
(214, 17, 'Santa Cruz Muluá', 'Activo'),
(215, 17, 'San Martín Zapotitlán', 'Activo'),
(216, 17, 'San Felipe', 'Activo'),
(217, 17, 'San Andrés Villa Seca', 'Activo'),
(218, 17, 'Champerico', 'Activo'),
(219, 17, 'Nuevo San Carlos', 'Activo'),
(220, 17, 'El Asintal', 'Activo'),
(221, 18, 'Antigua Guatemala', 'Activo'),
(222, 18, 'Jocotenango', 'Activo'),
(223, 18, 'Pastores', 'Activo'),
(224, 18, 'Sumpango', 'Activo'),
(225, 18, 'Santo Domingo Xenacoj', 'Activo'),
(226, 18, 'Santiago Sacatepéquez', 'Activo'),
(227, 18, 'San Bartolomé Milpas Altas', 'Activo'),
(228, 18, 'San Lucas Sacatepéquez', 'Activo'),
(229, 18, 'Santa Lucía Milpas Altas', 'Activo'),
(230, 18, 'Magdalena Milpas Altas', 'Activo'),
(231, 18, 'Santa María de Jesús', 'Activo'),
(232, 18, 'Ciudad Vieja', 'Activo'),
(233, 18, 'San Miguel Dueñas', 'Activo'),
(234, 18, 'Alotenango', 'Activo'),
(235, 18, 'San Antonio Aguas Calientes', 'Activo'),
(236, 18, 'Santa Catarina Barahona', 'Activo'),
(237, 19, 'San Marcos', 'Activo'),
(238, 19, 'San Pedro Sacatepéquez', 'Activo'),
(239, 19, 'San Antonio Sacatepéquez', 'Activo'),
(240, 19, 'Comitancillo', 'Activo'),
(241, 19, 'San Miguel Ixtahuacán', 'Activo'),
(242, 19, 'Concepción Tutuapa', 'Activo'),
(243, 19, 'Tacaná', 'Activo'),
(244, 19, 'Sibinal', 'Activo'),
(245, 19, 'Tajumulco', 'Activo'),
(246, 19, 'Tejutla', 'Activo'),
(247, 19, 'San Rafael Pie de la Cuesta', 'Activo'),
(248, 19, 'Nuevo Progreso', 'Activo'),
(249, 19, 'El Tumbador', 'Activo'),
(250, 19, 'El Rodeo', 'Activo'),
(251, 19, 'Malacatán', 'Activo'),
(252, 19, 'Catarina', 'Activo'),
(253, 19, 'Ayutla', 'Activo'),
(254, 19, 'Ocós', 'Activo'),
(255, 19, 'San Pablo', 'Activo'),
(256, 19, 'El Quetzal', 'Activo'),
(257, 19, 'La Reforma', 'Activo'),
(258, 19, 'Pajapita', 'Activo'),
(259, 19, 'Ixchiguán', 'Activo'),
(260, 19, 'San José Ojetenam', 'Activo'),
(261, 19, 'San Cristóbal Cucho', 'Activo'),
(262, 19, 'Sipacapa', 'Activo'),
(263, 19, 'Esquipulas Palo Gordo', 'Activo'),
(264, 19, 'Río Blanco', 'Activo'),
(265, 19, 'San Lorenzo', 'Activo'),
(266, 19, 'La Blanca', 'Activo'),
(267, 20, 'Cuilapa', 'Activo'),
(268, 20, 'Barberena', 'Activo'),
(269, 20, 'Santa Rosa de Lima', 'Activo'),
(270, 20, 'Casillas', 'Activo'),
(271, 20, 'San Rafael Las Flores', 'Activo'),
(272, 20, 'Oratorio', 'Activo'),
(273, 20, 'San Juan Tecuaco', 'Activo'),
(274, 20, 'Chiquimulilla', 'Activo'),
(275, 20, 'Taxisco', 'Activo'),
(276, 20, 'Santa María Ixhuatán', 'Activo'),
(277, 20, 'Guazacapán', 'Activo'),
(278, 20, 'Santa Cruz Naranjo', 'Activo'),
(279, 20, 'Pueblo Nuevo Viñas', 'Activo'),
(280, 20, 'Nueva Santa Rosa', 'Activo'),
(282, 1, 'San José Chacayá', 'Activo'),
(283, 1, 'Santa María Visitación', 'Activo'),
(284, 1, 'Santa Lucía Utatlán', 'Activo'),
(285, 1, 'Nahualá', 'Activo'),
(286, 1, 'Santa Catarina Ixtahuacán', 'Activo'),
(287, 1, 'Santa Clara La Laguna', 'Activo'),
(288, 1, 'Concepción', 'Activo'),
(289, 1, 'San Andrés Semetabaj', 'Activo'),
(291, 1, 'Santa Catarina Palopó', 'Activo'),
(292, 1, 'San Antonio Palopó', 'Activo'),
(293, 1, 'San Lucas Tolimán', 'Activo'),
(294, 1, 'Santa Cruz La Laguna', 'Activo'),
(295, 1, 'San Pablo La Laguna', 'Activo'),
(296, 1, 'San Marcos La Laguna', 'Activo'),
(297, 1, 'San Juan La Laguna', 'Activo'),
(298, 1, 'San Pedro La Laguna', 'Activo'),
(299, 1, 'Santiago Atitlán', 'Activo'),
(300, 22, 'Mazatenango', 'Activo'),
(301, 22, 'Cuyotenango', 'Activo'),
(302, 22, 'San Francisco Zapotitlán', 'Activo'),
(303, 22, 'San Bernardino', 'Activo'),
(304, 22, 'San José El Ídolo', 'Activo'),
(305, 22, 'Santo Domingo Suchitepéquez', 'Activo'),
(306, 22, 'San Lorenzo', 'Activo'),
(307, 22, 'Samayac', 'Activo'),
(308, 22, 'San Pablo Jocopilas', 'Activo'),
(309, 22, 'San Antonio Suchitepéquez', 'Activo'),
(310, 22, 'San Miguel Panán', 'Activo'),
(311, 22, 'San Gabriel', 'Activo'),
(312, 22, 'Chicacao', 'Activo'),
(313, 22, 'Patulul', 'Activo'),
(314, 22, 'Santa Bárbara', 'Activo'),
(315, 22, 'San Juan Bautista', 'Activo'),
(316, 22, 'Santo Tomás La Unión', 'Activo'),
(317, 22, 'Zunilito', 'Activo'),
(318, 22, 'Pueblo Nuevo', 'Activo'),
(319, 22, 'Río Bravo', 'Activo'),
(320, 22, 'San José La Máquina', 'Activo'),
(321, 23, 'Totonicapán', 'Activo'),
(322, 23, 'San Cristóbal Totonicapán', 'Activo'),
(323, 23, 'San Francisco El Alto', 'Activo'),
(324, 23, 'San Andrés Xecul', 'Activo'),
(325, 23, 'Momostenango', 'Activo'),
(326, 23, 'Santa María Chiquimula', 'Activo'),
(327, 23, 'Santa Lucía La Reforma', 'Activo'),
(328, 23, 'San Bartolo', 'Activo'),
(329, 24, 'Zacapa', 'Activo'),
(330, 24, 'Estanzuela', 'Activo'),
(331, 24, 'Río Hondo', 'Activo'),
(332, 24, 'Gualán', 'Activo'),
(333, 24, 'Teculután', 'Activo'),
(334, 24, 'Usumatlán', 'Activo'),
(335, 24, 'Cabañas', 'Activo'),
(336, 24, 'San Diego', 'Activo'),
(337, 24, 'La Unión', 'Activo'),
(338, 24, 'Huité', 'Activo'),
(339, 24, 'San Jorge', 'Activo'),
(340, 10, 'Petatán', 'Activo'),
(341, 14, 'El Chal', 'Activo');

INSERT INTO tipo_cliente (id_tipo_cliente, nombre, descuento_predeterminado) VALUES
(1, 'Consumidor Final', 0.00),
(2, 'Minorista', 5.00),
(3, 'Mayorista', 10.00);

INSERT INTO cliente (id_cliente, id_tipo_cliente, id_municipio, nit, nombre_comercial, direccion) VALUES
(1, 1, 1, 'CF', 'Consumidor Final', NULL),
(2, 3, 1, '9876543-2', 'Tienda Suyapa', 'Calle Santander, Panajachel');

INSERT INTO cliente_contacto (id_contacto, id_cliente, telefono, correo) VALUES
(1, 2, '5522-3344', 'tienda.suyapa@mail.com');

-- MÓDULO 3: Catálogo e Inventario -------------------------------------------
INSERT INTO categoria (id_categoria, nombre, estado) VALUES
(1, 'Cristalería', 'Activo'),
(2, 'Ropa', 'Activo'),
(3, 'Juguetes', 'Activo'),
(4, 'Hogar', 'Activo');

INSERT INTO subcategoria (id_subcategoria, id_categoria, nombre) VALUES
(1, 1, 'Vasos'),
(2, 1, 'Floreros'),
(3, 2, 'Ropa Bebé'),
(4, 3, 'Muñecas'),
(5, 4, 'Deco Hogar');

INSERT INTO unidad_medida (id_unidad, codigo, descripcion) VALUES
(1, 'UND', 'Unidad'),
(2, 'PAR', 'Par'),
(3, 'DOC', 'Docena'),
(4, 'CJ', 'Caja cerrada');

INSERT INTO producto (id_producto, id_subcategoria, id_unidad, nombre, descripcion, imagen_url, estado) VALUES
(1, 1, 1, 'Juego de Vasos de Cristal', 'Set de 6 vasos de cristal templado para mesa', '/img/vasos-cristal.jpg', 'Activo'),
(2, 3, 1, 'Vestido de Niña 2T', 'Vestido de algodón con bordado guatemalteco', '/img/vestido-2t.jpg', 'Activo'),
(3, 4, 1, 'Muñeca de Trapo Artesanal', 'Muñeca de tela tejida a mano, vestido tradicional', '/img/muneca-trapo.jpg', 'Activo');

INSERT INTO variante_producto (id_variante, id_producto, codigo_barras, talla, color, precio_detalle, precio_mayoreo, costo_promedio) VALUES
(1, 1, '7401000000011', NULL, 'Transparente', 85.00, 75.00, 52.00),
(2, 2, '7401000000028', '2T', 'Rosado', 120.00, 105.00, 68.00),
(3, 2, '7401000000035', '4T', 'Azul', 120.00, 105.00, 68.00),
(4, 3, '7401000000042', NULL, 'Multicolor', 45.00, 38.00, 24.00);

INSERT INTO inventario_sucursal (id_inventario, id_variante, id_sucursal, id_area, stock_actual, stock_minimo, fecha_actualizacion) VALUES
(1, 1, 1, 1, 24, 8, CURRENT_TIMESTAMP),
(2, 2, 1, 1, 12, 5, CURRENT_TIMESTAMP),
(3, 3, 1, 2, 10, 5, CURRENT_TIMESTAMP),
(4, 4, 1, 1, 30, 10, CURRENT_TIMESTAMP);

INSERT INTO historial_precio (id_historial, id_variante, id_usuario, precio_anterior, precio_nuevo, fecha_modificacion) VALUES
(1, 1, 1, 80.00, 85.00, CURRENT_TIMESTAMP);

INSERT INTO alerta_stock (id_alerta, id_inventario, mensaje, fecha_generacion, estado) VALUES
(1, 2, 'Vestido de Niña 2T por debajo del stock mínimo', CURRENT_TIMESTAMP, 'Pendiente');

-- MÓDULO 4: Movimientos y Mermas --------------------------------------------
INSERT INTO motivo_merma (id_motivo, descripcion) VALUES
(1, 'Cristalería Quebrada'),
(2, 'Ropa Manchada'),
(3, 'Defecto Fábrica');

-- MÓDULO 5: Caja, Turnos y Tesorería ----------------------------------------
INSERT INTO caja (id_caja, id_sucursal, descripcion, estado) VALUES
(1, 1, 'Caja Principal Mostrador', 'Activa');

INSERT INTO tipo_movimiento_caja (id_tipo_movimiento, nombre) VALUES
(1, 'Ingreso Sencillo Extra'),
(2, 'Vale Caja Chica'),
(3, 'Flete');

INSERT INTO denominacion_efectivo (id_denominacion, valor, tipo) VALUES
(1, 200.00, 'Billete'),
(2, 100.00, 'Billete'),
(3, 50.00, 'Billete'),
(4, 20.00, 'Billete'),
(5, 10.00, 'Billete'),
(6, 5.00, 'Billete'),
(7, 1.00, 'Moneda'),
(8, 0.50, 'Moneda');

-- MÓDULO 6: Ventas, Cobros y Facturación ------------------------------------
INSERT INTO metodo_pago (id_metodo_pago, nombre) VALUES
(1, 'Efectivo'),
(2, 'Transferencia');

-- MÓDULO 7: Compras y Proveedores -------------------------------------------
INSERT INTO proveedor (id_proveedor, nombre_contacto, distribuidora, telefono, correo, cuenta_bancaria, direccion) VALUES
(1, 'Carlos Mendoza', 'Vidriería Lago S.A.', '5522-7788', 'ventas@vidrierialago.com', '3456-789012-3', 'Zona 3, Sololá'),
(2, 'Lucía Ramírez', 'Textiles del Altiplano', '5544-2233', 'pedidos@textilesaltiplano.com', '6789-012345-6', 'Zona 5, Quetzaltenango'),
(3, 'Ana Pérez', 'Juguetería Maya Distribuciones', '5500-1122', 'ventas@jugueteriamaya.com', '1234-567890-1', 'Zona 2, Panajachel');


-- ============================================================================
-- SINCRONIZACIÓN DE SECUENCIAS TRAS DATOS SEMILLA
-- ============================================================================
SELECT setval('rol_id_rol_seq', COALESCE((SELECT MAX(id_rol) FROM rol), 0) + 1, false);
SELECT setval('usuario_id_usuario_seq', COALESCE((SELECT MAX(id_usuario) FROM usuario), 0) + 1, false);
SELECT setval('intento_login_id_intento_seq', COALESCE((SELECT MAX(id_intento) FROM intento_login), 0) + 1, false);
SELECT setval('permiso_id_permiso_seq', COALESCE((SELECT MAX(id_permiso) FROM permiso), 0) + 1, false);
SELECT setval('parametro_sistema_id_parametro_seq', COALESCE((SELECT MAX(id_parametro) FROM parametro_sistema), 0) + 1, false);
SELECT setval('sucursal_id_sucursal_seq', COALESCE((SELECT MAX(id_sucursal) FROM sucursal), 0) + 1, false);
SELECT setval('area_bodega_id_area_seq', COALESCE((SELECT MAX(id_area) FROM area_bodega), 0) + 1, false);
SELECT setval('departamento_geografico_id_departamento_seq', COALESCE((SELECT MAX(id_departamento) FROM departamento_geografico), 0) + 1, false);
SELECT setval('municipio_id_municipio_seq', COALESCE((SELECT MAX(id_municipio) FROM municipio), 0) + 1, false);
SELECT setval('tipo_cliente_id_tipo_cliente_seq', COALESCE((SELECT MAX(id_tipo_cliente) FROM tipo_cliente), 0) + 1, false);
SELECT setval('cliente_id_cliente_seq', COALESCE((SELECT MAX(id_cliente) FROM cliente), 0) + 1, false);
SELECT setval('cliente_contacto_id_contacto_seq', COALESCE((SELECT MAX(id_contacto) FROM cliente_contacto), 0) + 1, false);
SELECT setval('categoria_id_categoria_seq', COALESCE((SELECT MAX(id_categoria) FROM categoria), 0) + 1, false);
SELECT setval('subcategoria_id_subcategoria_seq', COALESCE((SELECT MAX(id_subcategoria) FROM subcategoria), 0) + 1, false);
SELECT setval('unidad_medida_id_unidad_seq', COALESCE((SELECT MAX(id_unidad) FROM unidad_medida), 0) + 1, false);
SELECT setval('producto_id_producto_seq', COALESCE((SELECT MAX(id_producto) FROM producto), 0) + 1, false);
SELECT setval('variante_producto_id_variante_seq', COALESCE((SELECT MAX(id_variante) FROM variante_producto), 0) + 1, false);
SELECT setval('inventario_sucursal_id_inventario_seq', COALESCE((SELECT MAX(id_inventario) FROM inventario_sucursal), 0) + 1, false);
SELECT setval('historial_precio_id_historial_seq', COALESCE((SELECT MAX(id_historial) FROM historial_precio), 0) + 1, false);
SELECT setval('alerta_stock_id_alerta_seq', COALESCE((SELECT MAX(id_alerta) FROM alerta_stock), 0) + 1, false);
SELECT setval('motivo_merma_id_motivo_seq', COALESCE((SELECT MAX(id_motivo) FROM motivo_merma), 0) + 1, false);
SELECT setval('caja_id_caja_seq', COALESCE((SELECT MAX(id_caja) FROM caja), 0) + 1, false);
SELECT setval('tipo_movimiento_caja_id_tipo_movimiento_seq', COALESCE((SELECT MAX(id_tipo_movimiento) FROM tipo_movimiento_caja), 0) + 1, false);
SELECT setval('denominacion_efectivo_id_denominacion_seq', COALESCE((SELECT MAX(id_denominacion) FROM denominacion_efectivo), 0) + 1, false);
SELECT setval('metodo_pago_id_metodo_pago_seq', COALESCE((SELECT MAX(id_metodo_pago) FROM metodo_pago), 0) + 1, false);
SELECT setval('proveedor_id_proveedor_seq', COALESCE((SELECT MAX(id_proveedor) FROM proveedor), 0) + 1, false);
SELECT setval('visita_seguimiento_id_visita_seq', COALESCE((SELECT MAX(id_visita) FROM visita_seguimiento), 0) + 1, false);
SELECT setval('visita_modulo_evaluacion_id_modulo_eval_seq', COALESCE((SELECT MAX(id_modulo_eval) FROM visita_modulo_evaluacion), 0) + 1, false);


-- ============================================================================
-- NOTA DE DESPLIEGUE
-- Para limpiar el volumen y aplicar esta base nueva:
--   docker compose down -v
--   docker compose up -d db
-- (borra el volumen postgres_data y re-ejecuta este init.sql desde cero)
-- ============================================================================