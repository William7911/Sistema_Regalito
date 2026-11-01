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
    email VARCHAR(100) UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    estado VARCHAR(20) NOT NULL CHECK (estado IN ('Activo', 'Inactivo')),
    fecha_creacion TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE codigo_recuperacion (
    id_codigo SERIAL PRIMARY KEY,
    id_usuario INT NOT NULL REFERENCES usuario(id_usuario) ON DELETE CASCADE,
    codigo VARCHAR(6) NOT NULL,
    expira_en TIMESTAMP NOT NULL,
    usado BOOLEAN NOT NULL DEFAULT FALSE,
    fecha_creacion TIMESTAMP NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_codigo_recuperacion_usuario ON codigo_recuperacion(id_usuario);
CREATE INDEX idx_codigo_recuperacion_codigo ON codigo_recuperacion(codigo);

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
-- MÓDULO 9: SINCRONIZACIÓN Y CONTINGENCIA OFFLINE
-- ============================================================================

CREATE TABLE IF NOT EXISTS sync_cache_metadata (
    id_sync SERIAL PRIMARY KEY,
    tabla VARCHAR(50) NOT NULL UNIQUE,
    registros_sincronizados INT NOT NULL DEFAULT 0,
    fecha_sincronizacion TIMESTAMP NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_sync_cache_metadata_tabla ON sync_cache_metadata (tabla);

CREATE TABLE IF NOT EXISTS sync_queue (
    id_sync SERIAL PRIMARY KEY,
    idempotency_key VARCHAR(36) NOT NULL UNIQUE,
    entidad VARCHAR(50) NOT NULL,
    entidad_id INT NOT NULL,
    operacion VARCHAR(20) NOT NULL,
    payload TEXT NOT NULL,
    estado VARCHAR(20) NOT NULL DEFAULT 'PENDIENTE',
    intentos INT DEFAULT 0,
    ultimo_error TEXT,
    creado_en TIMESTAMP DEFAULT NOW(),
    actualizado_en TIMESTAMP DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_sync_queue_idempotency ON sync_queue (idempotency_key);
CREATE INDEX IF NOT EXISTS idx_sync_queue_estado ON sync_queue (estado);

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
INSERT INTO usuario (id_usuario, id_rol, nombre_completo, username, email, password_hash, estado) VALUES
(1, 1, 'Propietaria Regalito', 'admin', 'abimaely3@gmail.com', '$2b$12$igeDz03pyYibOqQO3WJCY.a/XKMHvAAZ2sfh13w.YT7hurdmKFlpG', 'Activo'),
(2, 2, 'María Xicay', 'cajera', 'cajera@tiendaelregalito.gt', '$2b$12$igeDz03pyYibOqQO3WJCY.a/XKMHvAAZ2sfh13w.YT7hurdmKFlpG', 'Activo'),
(3, 3, 'Pedro Tzoc', 'bodega', 'bodega@tiendaelregalito.gt', '$2b$12$igeDz03pyYibOqQO3WJCY.a/XKMHvAAZ2sfh13w.YT7hurdmKFlpG', 'Activo');

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
(2,1),(2,2),(2,4),
(3,3),(3,5),(3,9);

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
(3, 'Ana Pérez', 'Juguetería Maya Distribuciones', '5500-1122', 'ventas@jugueteriamaya.com', '1234-567890-1', 'Zona 2, Panajachel'),
(4, 'General', 'Proveedor General / Sin especificar', '0000-0000', 'general@tiendaelregalito.com', NULL, 'Local');



-- DATOS DE DEMOSTRACIÓN COMPLETOS
-- ============================================================================
-- SEED DEMO DATA: CATÁLOGOS, 100 PRODUCTOS, 10 CLIENTES Y COMPRAS ASOCIADAS
-- ============================================================================

-- 1. Unidades de Medida adicionales
INSERT INTO unidad_medida (codigo, descripcion, estado)
VALUES ('SET', 'Juego o Set', 'Activo'), ('PKT', 'Paquete', 'Activo')
ON CONFLICT (codigo) DO NOTHING;

-- 2. Categorías (Catálogos)
INSERT INTO categoria (nombre, estado) VALUES ('Cristalería', 'Activo') ON CONFLICT (nombre) DO NOTHING;
INSERT INTO categoria (nombre, estado) VALUES ('Ropa', 'Activo') ON CONFLICT (nombre) DO NOTHING;
INSERT INTO categoria (nombre, estado) VALUES ('Juguetes', 'Activo') ON CONFLICT (nombre) DO NOTHING;
INSERT INTO categoria (nombre, estado) VALUES ('Hogar', 'Activo') ON CONFLICT (nombre) DO NOTHING;
INSERT INTO categoria (nombre, estado) VALUES ('Accesorios y Marroquinería', 'Activo') ON CONFLICT (nombre) DO NOTHING;
INSERT INTO categoria (nombre, estado) VALUES ('Cuidado Personal y Limpieza', 'Activo') ON CONFLICT (nombre) DO NOTHING;

-- 3. Subcategorías (Subcatálogos)
INSERT INTO subcategoria (id_categoria, nombre, estado)
SELECT c.id_categoria, 'Platos y Vajillas', 'Activo'
FROM categoria c WHERE c.nombre = 'Cristalería'
ON CONFLICT (id_categoria, nombre) DO NOTHING;
INSERT INTO subcategoria (id_categoria, nombre, estado)
SELECT c.id_categoria, 'Chamarras y Abrigos', 'Activo'
FROM categoria c WHERE c.nombre = 'Ropa'
ON CONFLICT (id_categoria, nombre) DO NOTHING;
INSERT INTO subcategoria (id_categoria, nombre, estado)
SELECT c.id_categoria, 'Peluches', 'Activo'
FROM categoria c WHERE c.nombre = 'Juguetes'
ON CONFLICT (id_categoria, nombre) DO NOTHING;
INSERT INTO subcategoria (id_categoria, nombre, estado)
SELECT c.id_categoria, 'Juguetes Educativos y Figuras', 'Activo'
FROM categoria c WHERE c.nombre = 'Juguetes'
ON CONFLICT (id_categoria, nombre) DO NOTHING;
INSERT INTO subcategoria (id_categoria, nombre, estado)
SELECT c.id_categoria, 'Toallas y Blancos', 'Activo'
FROM categoria c WHERE c.nombre = 'Hogar'
ON CONFLICT (id_categoria, nombre) DO NOTHING;
INSERT INTO subcategoria (id_categoria, nombre, estado)
SELECT c.id_categoria, 'Ollas y Baterías de Cocina', 'Activo'
FROM categoria c WHERE c.nombre = 'Hogar'
ON CONFLICT (id_categoria, nombre) DO NOTHING;
INSERT INTO subcategoria (id_categoria, nombre, estado)
SELECT c.id_categoria, 'Servilletas y Mantelería', 'Activo'
FROM categoria c WHERE c.nombre = 'Hogar'
ON CONFLICT (id_categoria, nombre) DO NOTHING;
INSERT INTO subcategoria (id_categoria, nombre, estado)
SELECT c.id_categoria, 'Bolsas y Mochilas', 'Activo'
FROM categoria c WHERE c.nombre = 'Accesorios y Marroquinería'
ON CONFLICT (id_categoria, nombre) DO NOTHING;
INSERT INTO subcategoria (id_categoria, nombre, estado)
SELECT c.id_categoria, 'Carteras y Billeteras', 'Activo'
FROM categoria c WHERE c.nombre = 'Accesorios y Marroquinería'
ON CONFLICT (id_categoria, nombre) DO NOTHING;
INSERT INTO subcategoria (id_categoria, nombre, estado)
SELECT c.id_categoria, 'Desodorantes e Higiene Corporal', 'Activo'
FROM categoria c WHERE c.nombre = 'Cuidado Personal y Limpieza'
ON CONFLICT (id_categoria, nombre) DO NOTHING;

-- 4. Proveedores
INSERT INTO proveedor (nombre_contacto, distribuidora, telefono, correo, cuenta_bancaria, direccion, estado)
VALUES ('Carlos Enrique Gómez', 'Distribuidora Menaje y Hogar S.A.', '7762-1122', 'ventas@menajeyhogar.com.gt', '4567-890123-4', 'Km 138 Carretera Interamericana, Sololá', 'Activo')
ON CONFLICT DO NOTHING;
INSERT INTO proveedor (nombre_contacto, distribuidora, telefono, correo, cuenta_bancaria, direccion, estado)
VALUES ('Marta Lidia Morales', 'Industrias Textiles del Lago', '7765-8899', 'pedidos@textilesdellago.gt', '1234-987654-1', 'Calle Real de la Laguna, Panajachel, Sololá', 'Activo')
ON CONFLICT DO NOTHING;
INSERT INTO proveedor (nombre_contacto, distribuidora, telefono, correo, cuenta_bancaria, direccion, estado)
VALUES ('Jorge Mario Soto', 'Importadora Cristalería y Porcelana Maya', '2334-5566', 'ventas@cristaleriamaya.com.gt', '7890-123456-2', 'Zona 12 Industrial, Ciudad de Guatemala', 'Activo')
ON CONFLICT DO NOTHING;
INSERT INTO proveedor (nombre_contacto, distribuidora, telefono, correo, cuenta_bancaria, direccion, estado)
VALUES ('Patricia Elizabeth Ruiz', 'Distribuidora de Cuidado y Cosméticos El Quetzal', '7761-4433', 'contacto@cosmeticoselquetzal.gt', '3456-112233-5', 'Zona 3 Las Rosas, Quetzaltenango', 'Activo')
ON CONFLICT DO NOTHING;
INSERT INTO proveedor (nombre_contacto, distribuidora, telefono, correo, cuenta_bancaria, direccion, estado)
VALUES ('Roberto Vásquez Fuentes', 'Marroquinería y Accesorios Chapines', '7832-1144', 'ventas@marroquineriachapina.gt', '9012-334455-8', 'Calle del Arco No. 25, Antigua Guatemala', 'Activo')
ON CONFLICT DO NOTHING;
INSERT INTO proveedor (nombre_contacto, distribuidora, telefono, correo, cuenta_bancaria, direccion, estado)
VALUES ('Lorena Astrid Estrada', 'Juguetes Educativos y Novedades del Altiplano', '7763-9988', 'info@juguetesaltiplano.gt', '5678-223344-9', 'Zona 1 Centro, Quetzaltenango', 'Activo')
ON CONFLICT DO NOTHING;

-- 5. Clientes de Ejemplo
DO $$
DECLARE
    v_id_cliente INT;
BEGIN
    SELECT id_cliente INTO v_id_cliente FROM cliente WHERE nit = 'CF-1001';
    IF v_id_cliente IS NULL THEN
        INSERT INTO cliente (id_tipo_cliente, id_municipio, nit, nombre_comercial, direccion, estado)
        VALUES (1, 1, 'CF-1001', 'Consumidor Final Mostrador Panajachel', 'Calle Santander, Panajachel', 'Activo')
        RETURNING id_cliente INTO v_id_cliente;

        INSERT INTO cliente_contacto (id_cliente, telefono, correo)
        VALUES (v_id_cliente, '5522-1001', 'cf.panajachel@cliente.gt');
    END IF;
END $$;
DO $$
DECLARE
    v_id_cliente INT;
BEGIN
    SELECT id_cliente INTO v_id_cliente FROM cliente WHERE nit = '5489623-1';
    IF v_id_cliente IS NULL THEN
        INSERT INTO cliente (id_tipo_cliente, id_municipio, nit, nombre_comercial, direccion, estado)
        VALUES (2, 1, '5489623-1', 'Abarrotería y Variedades El Atardecer', 'Calle Principal Callejón Don Fidel, Panajachel', 'Activo')
        RETURNING id_cliente INTO v_id_cliente;

        INSERT INTO cliente_contacto (id_cliente, telefono, correo)
        VALUES (v_id_cliente, '7762-4411', 'atardecer.ventas@gmail.com');
    END IF;
END $$;
DO $$
DECLARE
    v_id_cliente INT;
BEGIN
    SELECT id_cliente INTO v_id_cliente FROM cliente WHERE nit = '8912345-6';
    IF v_id_cliente IS NULL THEN
        INSERT INTO cliente (id_tipo_cliente, id_municipio, nit, nombre_comercial, direccion, estado)
        VALUES (3, 1, '8912345-6', 'Hotel y Restaurante Jardines de Atitlán', 'Playa Pública Sector Poniente, Panajachel', 'Activo')
        RETURNING id_cliente INTO v_id_cliente;

        INSERT INTO cliente_contacto (id_cliente, telefono, correo)
        VALUES (v_id_cliente, '7762-2890', 'compras@jardinesatitlan.com');
    END IF;
END $$;
DO $$
DECLARE
    v_id_cliente INT;
BEGIN
    SELECT id_cliente INTO v_id_cliente FROM cliente WHERE nit = '4521789-0';
    IF v_id_cliente IS NULL THEN
        INSERT INTO cliente (id_tipo_cliente, id_municipio, nit, nombre_comercial, direccion, estado)
        VALUES (3, 2, '4521789-0', 'Comercial La Bendición de Occidente', '4ta Avenida y 3ra Calle Zona 1, Sololá', 'Activo')
        RETURNING id_cliente INTO v_id_cliente;

        INSERT INTO cliente_contacto (id_cliente, telefono, correo)
        VALUES (v_id_cliente, '7765-3312', 'labendicion.solola@yahoo.com');
    END IF;
END $$;
DO $$
DECLARE
    v_id_cliente INT;
BEGIN
    SELECT id_cliente INTO v_id_cliente FROM cliente WHERE nit = '7823419-4';
    IF v_id_cliente IS NULL THEN
        INSERT INTO cliente (id_tipo_cliente, id_municipio, nit, nombre_comercial, direccion, estado)
        VALUES (2, 3, '7823419-4', 'Novedades y Regalos San Antonio', '12 Avenida 5-20 Zona 1, Quetzaltenango', 'Activo')
        RETURNING id_cliente INTO v_id_cliente;

        INSERT INTO cliente_contacto (id_cliente, telefono, correo)
        VALUES (v_id_cliente, '7761-8844', 'novedades.sanantonio@xela.gt');
    END IF;
END $$;
DO $$
DECLARE
    v_id_cliente INT;
BEGIN
    SELECT id_cliente INTO v_id_cliente FROM cliente WHERE nit = '3165489-7';
    IF v_id_cliente IS NULL THEN
        INSERT INTO cliente (id_tipo_cliente, id_municipio, nit, nombre_comercial, direccion, estado)
        VALUES (2, 29, '3165489-7', 'Cristalería y Hogar Doña Elena', 'Calle Real del Comercio Zona 2, Chimaltenango', 'Activo')
        RETURNING id_cliente INTO v_id_cliente;

        INSERT INTO cliente_contacto (id_cliente, telefono, correo)
        VALUES (v_id_cliente, '7839-5566', 'cristaleria.donaelena@gmail.com');
    END IF;
END $$;
DO $$
DECLARE
    v_id_cliente INT;
BEGIN
    SELECT id_cliente INTO v_id_cliente FROM cliente WHERE nit = '6291845-2';
    IF v_id_cliente IS NULL THEN
        INSERT INTO cliente (id_tipo_cliente, id_municipio, nit, nombre_comercial, direccion, estado)
        VALUES (3, 221, '6291845-2', 'Hotel Posada Los Volcanes S.A.', '5ta Avenida Norte No. 14, Antigua Guatemala', 'Activo')
        RETURNING id_cliente INTO v_id_cliente;

        INSERT INTO cliente_contacto (id_cliente, telefono, correo)
        VALUES (v_id_cliente, '7832-7799', 'adquisiciones@posadavolcanes.gt');
    END IF;
END $$;
DO $$
DECLARE
    v_id_cliente INT;
BEGIN
    SELECT id_cliente INTO v_id_cliente FROM cliente WHERE nit = '9134782-8';
    IF v_id_cliente IS NULL THEN
        INSERT INTO cliente (id_tipo_cliente, id_municipio, nit, nombre_comercial, direccion, estado)
        VALUES (3, 77, '9134782-8', 'Distribuidora El Regalito Metropolitano', 'Calzada Roosevelt 22-50 Zona 11, Ciudad de Guatemala', 'Activo')
        RETURNING id_cliente INTO v_id_cliente;

        INSERT INTO cliente_contacto (id_cliente, telefono, correo)
        VALUES (v_id_cliente, '2471-9900', 'contacto@regalitometro.com.gt');
    END IF;
END $$;
DO $$
DECLARE
    v_id_cliente INT;
BEGIN
    SELECT id_cliente INTO v_id_cliente FROM cliente WHERE nit = '1029384-5';
    IF v_id_cliente IS NULL THEN
        INSERT INTO cliente (id_tipo_cliente, id_municipio, nit, nombre_comercial, direccion, estado)
        VALUES (1, 1, '1029384-5', 'Carmen Alicia Xicay Mendoza', 'Barrio Monterrey, Panajachel, Sololá', 'Activo')
        RETURNING id_cliente INTO v_id_cliente;

        INSERT INTO cliente_contacto (id_cliente, telefono, correo)
        VALUES (v_id_cliente, '5899-4412', 'carmen.xicay@gmail.com');
    END IF;
END $$;
DO $$
DECLARE
    v_id_cliente INT;
BEGIN
    SELECT id_cliente INTO v_id_cliente FROM cliente WHERE nit = '7349182-3';
    IF v_id_cliente IS NULL THEN
        INSERT INTO cliente (id_tipo_cliente, id_municipio, nit, nombre_comercial, direccion, estado)
        VALUES (1, 2, '7349182-3', 'Mario Roberto Tzunún Cabrera', 'Cantón San Bartolo, Sololá', 'Activo')
        RETURNING id_cliente INTO v_id_cliente;

        INSERT INTO cliente_contacto (id_cliente, telefono, correo)
        VALUES (v_id_cliente, '4211-7788', 'mario.tzunun@outlook.com');
    END IF;
END $$;

-- 6. 100 Productos (10 por cada subcatálogo)
-- --- Subcatálogo: Toallas y Blancos (10 productos) ---
DO $$
DECLARE
    v_id_sub INT;
    v_id_uni INT;
    v_id_prod INT;
    v_id_var INT;
BEGIN
    SELECT id_subcategoria INTO v_id_sub FROM subcategoria WHERE nombre = 'Toallas y Blancos' LIMIT 1;
    SELECT id_unidad INTO v_id_uni FROM unidad_medida WHERE codigo = 'UND' LIMIT 1;
    IF v_id_uni IS NULL THEN
        SELECT id_unidad INTO v_id_uni FROM unidad_medida WHERE codigo = 'UND' LIMIT 1;
    END IF;

    SELECT id_producto INTO v_id_prod FROM producto WHERE nombre = 'Toalla de Baño Cuerpo Entero 100% Algodón';
    IF v_id_prod IS NULL THEN
        INSERT INTO producto (id_subcategoria, id_unidad, nombre, descripcion, imagen_url, estado, fecha_creacion)
        VALUES (v_id_sub, v_id_uni, 'Toalla de Baño Cuerpo Entero 100% Algodón', 'Toalla de felpa gruesa 70x140cm máxima absorción', NULL, 'Activo', NOW())
        RETURNING id_producto INTO v_id_prod;

        INSERT INTO variante_producto (id_producto, codigo_barras, talla, color, precio_detalle, precio_mayoreo, costo_promedio)
        VALUES (v_id_prod, '7401202601001', '70x140cm', 'Blanco', 75.0, 65.0, 45.0)
        RETURNING id_variante INTO v_id_var;

        INSERT INTO inventario_sucursal (id_variante, id_sucursal, id_area, stock_actual, stock_minimo, fecha_actualizacion)
        VALUES (v_id_var, 1, 1, 35, 10, NOW());

        INSERT INTO historial_precio (id_variante, id_usuario, precio_anterior, precio_nuevo, fecha_modificacion)
        VALUES (v_id_var, 1, 45.0, 75.0, NOW());
    END IF;
END $$;
DO $$
DECLARE
    v_id_sub INT;
    v_id_uni INT;
    v_id_prod INT;
    v_id_var INT;
BEGIN
    SELECT id_subcategoria INTO v_id_sub FROM subcategoria WHERE nombre = 'Toallas y Blancos' LIMIT 1;
    SELECT id_unidad INTO v_id_uni FROM unidad_medida WHERE codigo = 'UND' LIMIT 1;
    IF v_id_uni IS NULL THEN
        SELECT id_unidad INTO v_id_uni FROM unidad_medida WHERE codigo = 'UND' LIMIT 1;
    END IF;

    SELECT id_producto INTO v_id_prod FROM producto WHERE nombre = 'Toalla de Mano Felpa Hotelera';
    IF v_id_prod IS NULL THEN
        INSERT INTO producto (id_subcategoria, id_unidad, nombre, descripcion, imagen_url, estado, fecha_creacion)
        VALUES (v_id_sub, v_id_uni, 'Toalla de Mano Felpa Hotelera', 'Toalla suave para manos y tocador 40x70cm', NULL, 'Activo', NOW())
        RETURNING id_producto INTO v_id_prod;

        INSERT INTO variante_producto (id_producto, codigo_barras, talla, color, precio_detalle, precio_mayoreo, costo_promedio)
        VALUES (v_id_prod, '7401202601002', '40x70cm', 'Azul Marino', 30.0, 26.0, 18.0)
        RETURNING id_variante INTO v_id_var;

        INSERT INTO inventario_sucursal (id_variante, id_sucursal, id_area, stock_actual, stock_minimo, fecha_actualizacion)
        VALUES (v_id_var, 1, 1, 40, 10, NOW());

        INSERT INTO historial_precio (id_variante, id_usuario, precio_anterior, precio_nuevo, fecha_modificacion)
        VALUES (v_id_var, 1, 18.0, 30.0, NOW());
    END IF;
END $$;
DO $$
DECLARE
    v_id_sub INT;
    v_id_uni INT;
    v_id_prod INT;
    v_id_var INT;
BEGIN
    SELECT id_subcategoria INTO v_id_sub FROM subcategoria WHERE nombre = 'Toallas y Blancos' LIMIT 1;
    SELECT id_unidad INTO v_id_uni FROM unidad_medida WHERE codigo = 'UND' LIMIT 1;
    IF v_id_uni IS NULL THEN
        SELECT id_unidad INTO v_id_uni FROM unidad_medida WHERE codigo = 'UND' LIMIT 1;
    END IF;

    SELECT id_producto INTO v_id_prod FROM producto WHERE nombre = 'Toalla Facial Microfibra Extra Suave';
    IF v_id_prod IS NULL THEN
        INSERT INTO producto (id_subcategoria, id_unidad, nombre, descripcion, imagen_url, estado, fecha_creacion)
        VALUES (v_id_sub, v_id_uni, 'Toalla Facial Microfibra Extra Suave', 'Toalla para rostro delicado de secado ultra rápido', NULL, 'Activo', NOW())
        RETURNING id_producto INTO v_id_prod;

        INSERT INTO variante_producto (id_producto, codigo_barras, talla, color, precio_detalle, precio_mayoreo, costo_promedio)
        VALUES (v_id_prod, '7401202601003', '30x30cm', 'Celeste', 15.0, 12.0, 8.0)
        RETURNING id_variante INTO v_id_var;

        INSERT INTO inventario_sucursal (id_variante, id_sucursal, id_area, stock_actual, stock_minimo, fecha_actualizacion)
        VALUES (v_id_var, 1, 1, 50, 15, NOW());

        INSERT INTO historial_precio (id_variante, id_usuario, precio_anterior, precio_nuevo, fecha_modificacion)
        VALUES (v_id_var, 1, 8.0, 15.0, NOW());
    END IF;
END $$;
DO $$
DECLARE
    v_id_sub INT;
    v_id_uni INT;
    v_id_prod INT;
    v_id_var INT;
BEGIN
    SELECT id_subcategoria INTO v_id_sub FROM subcategoria WHERE nombre = 'Toallas y Blancos' LIMIT 1;
    SELECT id_unidad INTO v_id_uni FROM unidad_medida WHERE codigo = 'UND' LIMIT 1;
    IF v_id_uni IS NULL THEN
        SELECT id_unidad INTO v_id_uni FROM unidad_medida WHERE codigo = 'UND' LIMIT 1;
    END IF;

    SELECT id_producto INTO v_id_prod FROM producto WHERE nombre = 'Toalla Playera Grande Estampado Atitlán';
    IF v_id_prod IS NULL THEN
        INSERT INTO producto (id_subcategoria, id_unidad, nombre, descripcion, imagen_url, estado, fecha_creacion)
        VALUES (v_id_sub, v_id_uni, 'Toalla Playera Grande Estampado Atitlán', 'Toalla playera 90x170cm con diseño colorido del Lago de Atitlán', NULL, 'Activo', NOW())
        RETURNING id_producto INTO v_id_prod;

        INSERT INTO variante_producto (id_producto, codigo_barras, talla, color, precio_detalle, precio_mayoreo, costo_promedio)
        VALUES (v_id_prod, '7401202601004', '90x170cm', 'Multicolor', 98.0, 85.0, 60.0)
        RETURNING id_variante INTO v_id_var;

        INSERT INTO inventario_sucursal (id_variante, id_sucursal, id_area, stock_actual, stock_minimo, fecha_actualizacion)
        VALUES (v_id_var, 1, 1, 25, 8, NOW());

        INSERT INTO historial_precio (id_variante, id_usuario, precio_anterior, precio_nuevo, fecha_modificacion)
        VALUES (v_id_var, 1, 60.0, 98.0, NOW());
    END IF;
END $$;
DO $$
DECLARE
    v_id_sub INT;
    v_id_uni INT;
    v_id_prod INT;
    v_id_var INT;
BEGIN
    SELECT id_subcategoria INTO v_id_sub FROM subcategoria WHERE nombre = 'Toallas y Blancos' LIMIT 1;
    SELECT id_unidad INTO v_id_uni FROM unidad_medida WHERE codigo = 'SET' LIMIT 1;
    IF v_id_uni IS NULL THEN
        SELECT id_unidad INTO v_id_uni FROM unidad_medida WHERE codigo = 'UND' LIMIT 1;
    END IF;

    SELECT id_producto INTO v_id_prod FROM producto WHERE nombre = 'Set de Toallas Familiar 3 Piezas';
    IF v_id_prod IS NULL THEN
        INSERT INTO producto (id_subcategoria, id_unidad, nombre, descripcion, imagen_url, estado, fecha_creacion)
        VALUES (v_id_sub, v_id_uni, 'Set de Toallas Familiar 3 Piezas', 'Juego coordinado: cuerpo, mano y facial en caja de regalo', NULL, 'Activo', NOW())
        RETURNING id_producto INTO v_id_prod;

        INSERT INTO variante_producto (id_producto, codigo_barras, talla, color, precio_detalle, precio_mayoreo, costo_promedio)
        VALUES (v_id_prod, '7401202601005', 'Set 3pz', 'Beige', 115.0, 95.0, 70.0)
        RETURNING id_variante INTO v_id_var;

        INSERT INTO inventario_sucursal (id_variante, id_sucursal, id_area, stock_actual, stock_minimo, fecha_actualizacion)
        VALUES (v_id_var, 1, 2, 20, 5, NOW());

        INSERT INTO historial_precio (id_variante, id_usuario, precio_anterior, precio_nuevo, fecha_modificacion)
        VALUES (v_id_var, 1, 70.0, 115.0, NOW());
    END IF;
END $$;
DO $$
DECLARE
    v_id_sub INT;
    v_id_uni INT;
    v_id_prod INT;
    v_id_var INT;
BEGIN
    SELECT id_subcategoria INTO v_id_sub FROM subcategoria WHERE nombre = 'Toallas y Blancos' LIMIT 1;
    SELECT id_unidad INTO v_id_uni FROM unidad_medida WHERE codigo = 'UND' LIMIT 1;
    IF v_id_uni IS NULL THEN
        SELECT id_unidad INTO v_id_uni FROM unidad_medida WHERE codigo = 'UND' LIMIT 1;
    END IF;

    SELECT id_producto INTO v_id_prod FROM producto WHERE nombre = 'Toalla para Cabello Tipo Turbante';
    IF v_id_prod IS NULL THEN
        INSERT INTO producto (id_subcategoria, id_unidad, nombre, descripcion, imagen_url, estado, fecha_creacion)
        VALUES (v_id_sub, v_id_uni, 'Toalla para Cabello Tipo Turbante', 'Turbante de microfibra absorbente con botón de seguridad', NULL, 'Activo', NOW())
        RETURNING id_producto INTO v_id_prod;

        INSERT INTO variante_producto (id_producto, codigo_barras, talla, color, precio_detalle, precio_mayoreo, costo_promedio)
        VALUES (v_id_prod, '7401202601006', 'Unitalla', 'Rosa Pastel', 28.0, 22.0, 15.0)
        RETURNING id_variante INTO v_id_var;

        INSERT INTO inventario_sucursal (id_variante, id_sucursal, id_area, stock_actual, stock_minimo, fecha_actualizacion)
        VALUES (v_id_var, 1, 1, 30, 10, NOW());

        INSERT INTO historial_precio (id_variante, id_usuario, precio_anterior, precio_nuevo, fecha_modificacion)
        VALUES (v_id_var, 1, 15.0, 28.0, NOW());
    END IF;
END $$;
DO $$
DECLARE
    v_id_sub INT;
    v_id_uni INT;
    v_id_prod INT;
    v_id_var INT;
BEGIN
    SELECT id_subcategoria INTO v_id_sub FROM subcategoria WHERE nombre = 'Toallas y Blancos' LIMIT 1;
    SELECT id_unidad INTO v_id_uni FROM unidad_medida WHERE codigo = 'PKT' LIMIT 1;
    IF v_id_uni IS NULL THEN
        SELECT id_unidad INTO v_id_uni FROM unidad_medida WHERE codigo = 'UND' LIMIT 1;
    END IF;

    SELECT id_producto INTO v_id_prod FROM producto WHERE nombre = 'Toalla de Cocina Absorbente Pack x3';
    IF v_id_prod IS NULL THEN
        INSERT INTO producto (id_subcategoria, id_unidad, nombre, descripcion, imagen_url, estado, fecha_creacion)
        VALUES (v_id_sub, v_id_uni, 'Toalla de Cocina Absorbente Pack x3', 'Paquete de 3 paños de cocina resistentes con cenefa decorativa', NULL, 'Activo', NOW())
        RETURNING id_producto INTO v_id_prod;

        INSERT INTO variante_producto (id_producto, codigo_barras, talla, color, precio_detalle, precio_mayoreo, costo_promedio)
        VALUES (v_id_prod, '7401202601007', 'Pack 3', 'Estampado Frutas', 38.0, 32.0, 22.0)
        RETURNING id_variante INTO v_id_var;

        INSERT INTO inventario_sucursal (id_variante, id_sucursal, id_area, stock_actual, stock_minimo, fecha_actualizacion)
        VALUES (v_id_var, 1, 1, 45, 12, NOW());

        INSERT INTO historial_precio (id_variante, id_usuario, precio_anterior, precio_nuevo, fecha_modificacion)
        VALUES (v_id_var, 1, 22.0, 38.0, NOW());
    END IF;
END $$;
DO $$
DECLARE
    v_id_sub INT;
    v_id_uni INT;
    v_id_prod INT;
    v_id_var INT;
BEGIN
    SELECT id_subcategoria INTO v_id_sub FROM subcategoria WHERE nombre = 'Toallas y Blancos' LIMIT 1;
    SELECT id_unidad INTO v_id_uni FROM unidad_medida WHERE codigo = 'UND' LIMIT 1;
    IF v_id_uni IS NULL THEN
        SELECT id_unidad INTO v_id_uni FROM unidad_medida WHERE codigo = 'UND' LIMIT 1;
    END IF;

    SELECT id_producto INTO v_id_prod FROM producto WHERE nombre = 'Toalla Deportiva Microfibra con Estuche';
    IF v_id_prod IS NULL THEN
        INSERT INTO producto (id_subcategoria, id_unidad, nombre, descripcion, imagen_url, estado, fecha_creacion)
        VALUES (v_id_sub, v_id_uni, 'Toalla Deportiva Microfibra con Estuche', 'Toalla compacta para gimnasio y viaje con funda de transporte', NULL, 'Activo', NOW())
        RETURNING id_producto INTO v_id_prod;

        INSERT INTO variante_producto (id_producto, codigo_barras, talla, color, precio_detalle, precio_mayoreo, costo_promedio)
        VALUES (v_id_prod, '7401202601008', '50x100cm', 'Gris/Verde', 42.0, 36.0, 25.0)
        RETURNING id_variante INTO v_id_var;

        INSERT INTO inventario_sucursal (id_variante, id_sucursal, id_area, stock_actual, stock_minimo, fecha_actualizacion)
        VALUES (v_id_var, 1, 1, 30, 8, NOW());

        INSERT INTO historial_precio (id_variante, id_usuario, precio_anterior, precio_nuevo, fecha_modificacion)
        VALUES (v_id_var, 1, 25.0, 42.0, NOW());
    END IF;
END $$;
DO $$
DECLARE
    v_id_sub INT;
    v_id_uni INT;
    v_id_prod INT;
    v_id_var INT;
BEGIN
    SELECT id_subcategoria INTO v_id_sub FROM subcategoria WHERE nombre = 'Toallas y Blancos' LIMIT 1;
    SELECT id_unidad INTO v_id_uni FROM unidad_medida WHERE codigo = 'UND' LIMIT 1;
    IF v_id_uni IS NULL THEN
        SELECT id_unidad INTO v_id_uni FROM unidad_medida WHERE codigo = 'UND' LIMIT 1;
    END IF;

    SELECT id_producto INTO v_id_prod FROM producto WHERE nombre = 'Toalla Infantil con Capucha Bordada Oso';
    IF v_id_prod IS NULL THEN
        INSERT INTO producto (id_subcategoria, id_unidad, nombre, descripcion, imagen_url, estado, fecha_creacion)
        VALUES (v_id_sub, v_id_uni, 'Toalla Infantil con Capucha Bordada Oso', 'Toalla poncho para niños de felpa suave con orejitas', NULL, 'Activo', NOW())
        RETURNING id_producto INTO v_id_prod;

        INSERT INTO variante_producto (id_producto, codigo_barras, talla, color, precio_detalle, precio_mayoreo, costo_promedio)
        VALUES (v_id_prod, '7401202601009', 'Infantil', 'Amarillo', 55.0, 48.0, 35.0)
        RETURNING id_variante INTO v_id_var;

        INSERT INTO inventario_sucursal (id_variante, id_sucursal, id_area, stock_actual, stock_minimo, fecha_actualizacion)
        VALUES (v_id_var, 1, 1, 25, 6, NOW());

        INSERT INTO historial_precio (id_variante, id_usuario, precio_anterior, precio_nuevo, fecha_modificacion)
        VALUES (v_id_var, 1, 35.0, 55.0, NOW());
    END IF;
END $$;
DO $$
DECLARE
    v_id_sub INT;
    v_id_uni INT;
    v_id_prod INT;
    v_id_var INT;
BEGIN
    SELECT id_subcategoria INTO v_id_sub FROM subcategoria WHERE nombre = 'Toallas y Blancos' LIMIT 1;
    SELECT id_unidad INTO v_id_uni FROM unidad_medida WHERE codigo = 'UND' LIMIT 1;
    IF v_id_uni IS NULL THEN
        SELECT id_unidad INTO v_id_uni FROM unidad_medida WHERE codigo = 'UND' LIMIT 1;
    END IF;

    SELECT id_producto INTO v_id_prod FROM producto WHERE nombre = 'Toalla Tapete de Baño Antideslizante';
    IF v_id_prod IS NULL THEN
        INSERT INTO producto (id_subcategoria, id_unidad, nombre, descripcion, imagen_url, estado, fecha_creacion)
        VALUES (v_id_sub, v_id_uni, 'Toalla Tapete de Baño Antideslizante', 'Piso de toalla afelpado para salida de regadera', NULL, 'Activo', NOW())
        RETURNING id_producto INTO v_id_prod;

        INSERT INTO variante_producto (id_producto, codigo_barras, talla, color, precio_detalle, precio_mayoreo, costo_promedio)
        VALUES (v_id_prod, '7401202601010', '50x80cm', 'Gris Oxford', 48.0, 40.0, 28.0)
        RETURNING id_variante INTO v_id_var;

        INSERT INTO inventario_sucursal (id_variante, id_sucursal, id_area, stock_actual, stock_minimo, fecha_actualizacion)
        VALUES (v_id_var, 1, 2, 30, 8, NOW());

        INSERT INTO historial_precio (id_variante, id_usuario, precio_anterior, precio_nuevo, fecha_modificacion)
        VALUES (v_id_var, 1, 28.0, 48.0, NOW());
    END IF;
END $$;

-- --- Subcatálogo: Peluches (10 productos) ---
DO $$
DECLARE
    v_id_sub INT;
    v_id_uni INT;
    v_id_prod INT;
    v_id_var INT;
BEGIN
    SELECT id_subcategoria INTO v_id_sub FROM subcategoria WHERE nombre = 'Peluches' LIMIT 1;
    SELECT id_unidad INTO v_id_uni FROM unidad_medida WHERE codigo = 'UND' LIMIT 1;
    IF v_id_uni IS NULL THEN
        SELECT id_unidad INTO v_id_uni FROM unidad_medida WHERE codigo = 'UND' LIMIT 1;
    END IF;

    SELECT id_producto INTO v_id_prod FROM producto WHERE nombre = 'Oso de Peluche Gigante 1 Metro con Moño';
    IF v_id_prod IS NULL THEN
        INSERT INTO producto (id_subcategoria, id_unidad, nombre, descripcion, imagen_url, estado, fecha_creacion)
        VALUES (v_id_sub, v_id_uni, 'Oso de Peluche Gigante 1 Metro con Moño', 'Peluche de felpa extra suave premium relleno siliconado', NULL, 'Activo', NOW())
        RETURNING id_producto INTO v_id_prod;

        INSERT INTO variante_producto (id_producto, codigo_barras, talla, color, precio_detalle, precio_mayoreo, costo_promedio)
        VALUES (v_id_prod, '7401202601011', '100cm', 'Café Claro', 195.0, 165.0, 120.0)
        RETURNING id_variante INTO v_id_var;

        INSERT INTO inventario_sucursal (id_variante, id_sucursal, id_area, stock_actual, stock_minimo, fecha_actualizacion)
        VALUES (v_id_var, 1, 1, 15, 4, NOW());

        INSERT INTO historial_precio (id_variante, id_usuario, precio_anterior, precio_nuevo, fecha_modificacion)
        VALUES (v_id_var, 1, 120.0, 195.0, NOW());
    END IF;
END $$;
DO $$
DECLARE
    v_id_sub INT;
    v_id_uni INT;
    v_id_prod INT;
    v_id_var INT;
BEGIN
    SELECT id_subcategoria INTO v_id_sub FROM subcategoria WHERE nombre = 'Peluches' LIMIT 1;
    SELECT id_unidad INTO v_id_uni FROM unidad_medida WHERE codigo = 'UND' LIMIT 1;
    IF v_id_uni IS NULL THEN
        SELECT id_unidad INTO v_id_uni FROM unidad_medida WHERE codigo = 'UND' LIMIT 1;
    END IF;

    SELECT id_producto INTO v_id_prod FROM producto WHERE nombre = 'Peluche de Unicornio Mágico con Alas Tornasol';
    IF v_id_prod IS NULL THEN
        INSERT INTO producto (id_subcategoria, id_unidad, nombre, descripcion, imagen_url, estado, fecha_creacion)
        VALUES (v_id_sub, v_id_uni, 'Peluche de Unicornio Mágico con Alas Tornasol', 'Unicornio con detalles bordados y cuerno brillante', NULL, 'Activo', NOW())
        RETURNING id_producto INTO v_id_prod;

        INSERT INTO variante_producto (id_producto, codigo_barras, talla, color, precio_detalle, precio_mayoreo, costo_promedio)
        VALUES (v_id_prod, '7401202601012', '45cm', 'Blanco/Rosa', 78.0, 68.0, 48.0)
        RETURNING id_variante INTO v_id_var;

        INSERT INTO inventario_sucursal (id_variante, id_sucursal, id_area, stock_actual, stock_minimo, fecha_actualizacion)
        VALUES (v_id_var, 1, 1, 24, 6, NOW());

        INSERT INTO historial_precio (id_variante, id_usuario, precio_anterior, precio_nuevo, fecha_modificacion)
        VALUES (v_id_var, 1, 48.0, 78.0, NOW());
    END IF;
END $$;
DO $$
DECLARE
    v_id_sub INT;
    v_id_uni INT;
    v_id_prod INT;
    v_id_var INT;
BEGIN
    SELECT id_subcategoria INTO v_id_sub FROM subcategoria WHERE nombre = 'Peluches' LIMIT 1;
    SELECT id_unidad INTO v_id_uni FROM unidad_medida WHERE codigo = 'UND' LIMIT 1;
    IF v_id_uni IS NULL THEN
        SELECT id_unidad INTO v_id_uni FROM unidad_medida WHERE codigo = 'UND' LIMIT 1;
    END IF;

    SELECT id_producto INTO v_id_prod FROM producto WHERE nombre = 'Peluche de Perro San Bernardo Pelaje Largo';
    IF v_id_prod IS NULL THEN
        INSERT INTO producto (id_subcategoria, id_unidad, nombre, descripcion, imagen_url, estado, fecha_creacion)
        VALUES (v_id_sub, v_id_uni, 'Peluche de Perro San Bernardo Pelaje Largo', 'Cachorro San Bernardo realista antialérgico', NULL, 'Activo', NOW())
        RETURNING id_producto INTO v_id_prod;

        INSERT INTO variante_producto (id_producto, codigo_barras, talla, color, precio_detalle, precio_mayoreo, costo_promedio)
        VALUES (v_id_prod, '7401202601013', '40cm', 'Blanco/Café', 85.0, 72.0, 52.0)
        RETURNING id_variante INTO v_id_var;

        INSERT INTO inventario_sucursal (id_variante, id_sucursal, id_area, stock_actual, stock_minimo, fecha_actualizacion)
        VALUES (v_id_var, 1, 1, 20, 5, NOW());

        INSERT INTO historial_precio (id_variante, id_usuario, precio_anterior, precio_nuevo, fecha_modificacion)
        VALUES (v_id_var, 1, 52.0, 85.0, NOW());
    END IF;
END $$;
DO $$
DECLARE
    v_id_sub INT;
    v_id_uni INT;
    v_id_prod INT;
    v_id_var INT;
BEGIN
    SELECT id_subcategoria INTO v_id_sub FROM subcategoria WHERE nombre = 'Peluches' LIMIT 1;
    SELECT id_unidad INTO v_id_uni FROM unidad_medida WHERE codigo = 'UND' LIMIT 1;
    IF v_id_uni IS NULL THEN
        SELECT id_unidad INTO v_id_uni FROM unidad_medida WHERE codigo = 'UND' LIMIT 1;
    END IF;

    SELECT id_producto INTO v_id_prod FROM producto WHERE nombre = 'Peluche Stitch Travieso 35cm';
    IF v_id_prod IS NULL THEN
        INSERT INTO producto (id_subcategoria, id_unidad, nombre, descripcion, imagen_url, estado, fecha_creacion)
        VALUES (v_id_sub, v_id_uni, 'Peluche Stitch Travieso 35cm', 'Personaje Stitch clásico con orejas flexibles aterciopelado', NULL, 'Activo', NOW())
        RETURNING id_producto INTO v_id_prod;

        INSERT INTO variante_producto (id_producto, codigo_barras, talla, color, precio_detalle, precio_mayoreo, costo_promedio)
        VALUES (v_id_prod, '7401202601014', '35cm', 'Azul', 72.0, 62.0, 45.0)
        RETURNING id_variante INTO v_id_var;

        INSERT INTO inventario_sucursal (id_variante, id_sucursal, id_area, stock_actual, stock_minimo, fecha_actualizacion)
        VALUES (v_id_var, 1, 1, 30, 8, NOW());

        INSERT INTO historial_precio (id_variante, id_usuario, precio_anterior, precio_nuevo, fecha_modificacion)
        VALUES (v_id_var, 1, 45.0, 72.0, NOW());
    END IF;
END $$;
DO $$
DECLARE
    v_id_sub INT;
    v_id_uni INT;
    v_id_prod INT;
    v_id_var INT;
BEGIN
    SELECT id_subcategoria INTO v_id_sub FROM subcategoria WHERE nombre = 'Peluches' LIMIT 1;
    SELECT id_unidad INTO v_id_uni FROM unidad_medida WHERE codigo = 'UND' LIMIT 1;
    IF v_id_uni IS NULL THEN
        SELECT id_unidad INTO v_id_uni FROM unidad_medida WHERE codigo = 'UND' LIMIT 1;
    END IF;

    SELECT id_producto INTO v_id_prod FROM producto WHERE nombre = 'Peluche Pulpo Reversible de Emociones';
    IF v_id_prod IS NULL THEN
        INSERT INTO producto (id_subcategoria, id_unidad, nombre, descripcion, imagen_url, estado, fecha_creacion)
        VALUES (v_id_sub, v_id_uni, 'Peluche Pulpo Reversible de Emociones', 'Pulpo reversible feliz / enojado de felpa suave', NULL, 'Activo', NOW())
        RETURNING id_producto INTO v_id_prod;

        INSERT INTO variante_producto (id_producto, codigo_barras, talla, color, precio_detalle, precio_mayoreo, costo_promedio)
        VALUES (v_id_prod, '7401202601015', '20cm', 'Rosa/Azul', 32.0, 26.0, 18.0)
        RETURNING id_variante INTO v_id_var;

        INSERT INTO inventario_sucursal (id_variante, id_sucursal, id_area, stock_actual, stock_minimo, fecha_actualizacion)
        VALUES (v_id_var, 1, 3, 50, 15, NOW());

        INSERT INTO historial_precio (id_variante, id_usuario, precio_anterior, precio_nuevo, fecha_modificacion)
        VALUES (v_id_var, 1, 18.0, 32.0, NOW());
    END IF;
END $$;
DO $$
DECLARE
    v_id_sub INT;
    v_id_uni INT;
    v_id_prod INT;
    v_id_var INT;
BEGIN
    SELECT id_subcategoria INTO v_id_sub FROM subcategoria WHERE nombre = 'Peluches' LIMIT 1;
    SELECT id_unidad INTO v_id_uni FROM unidad_medida WHERE codigo = 'UND' LIMIT 1;
    IF v_id_uni IS NULL THEN
        SELECT id_unidad INTO v_id_uni FROM unidad_medida WHERE codigo = 'UND' LIMIT 1;
    END IF;

    SELECT id_producto INTO v_id_prod FROM producto WHERE nombre = 'Peluche de Dinosaurio T-Rex Infantil';
    IF v_id_prod IS NULL THEN
        INSERT INTO producto (id_subcategoria, id_unidad, nombre, descripcion, imagen_url, estado, fecha_creacion)
        VALUES (v_id_sub, v_id_uni, 'Peluche de Dinosaurio T-Rex Infantil', 'Dinosaurio verde amigable y blandito para niños', NULL, 'Activo', NOW())
        RETURNING id_producto INTO v_id_prod;

        INSERT INTO variante_producto (id_producto, codigo_barras, talla, color, precio_detalle, precio_mayoreo, costo_promedio)
        VALUES (v_id_prod, '7401202601016', '38cm', 'Verde', 60.0, 52.0, 38.0)
        RETURNING id_variante INTO v_id_var;

        INSERT INTO inventario_sucursal (id_variante, id_sucursal, id_area, stock_actual, stock_minimo, fecha_actualizacion)
        VALUES (v_id_var, 1, 1, 22, 6, NOW());

        INSERT INTO historial_precio (id_variante, id_usuario, precio_anterior, precio_nuevo, fecha_modificacion)
        VALUES (v_id_var, 1, 38.0, 60.0, NOW());
    END IF;
END $$;
DO $$
DECLARE
    v_id_sub INT;
    v_id_uni INT;
    v_id_prod INT;
    v_id_var INT;
BEGIN
    SELECT id_subcategoria INTO v_id_sub FROM subcategoria WHERE nombre = 'Peluches' LIMIT 1;
    SELECT id_unidad INTO v_id_uni FROM unidad_medida WHERE codigo = 'UND' LIMIT 1;
    IF v_id_uni IS NULL THEN
        SELECT id_unidad INTO v_id_uni FROM unidad_medida WHERE codigo = 'UND' LIMIT 1;
    END IF;

    SELECT id_producto INTO v_id_prod FROM producto WHERE nombre = 'Peluche de Gato Dormilón Afelpado';
    IF v_id_prod IS NULL THEN
        INSERT INTO producto (id_subcategoria, id_unidad, nombre, descripcion, imagen_url, estado, fecha_creacion)
        VALUES (v_id_sub, v_id_uni, 'Peluche de Gato Dormilón Afelpado', 'Gatito echado suave ideal para almohada o decoración', NULL, 'Activo', NOW())
        RETURNING id_producto INTO v_id_prod;

        INSERT INTO variante_producto (id_producto, codigo_barras, talla, color, precio_detalle, precio_mayoreo, costo_promedio)
        VALUES (v_id_prod, '7401202601017', '50cm', 'Gris Atigrado', 68.0, 58.0, 42.0)
        RETURNING id_variante INTO v_id_var;

        INSERT INTO inventario_sucursal (id_variante, id_sucursal, id_area, stock_actual, stock_minimo, fecha_actualizacion)
        VALUES (v_id_var, 1, 1, 25, 6, NOW());

        INSERT INTO historial_precio (id_variante, id_usuario, precio_anterior, precio_nuevo, fecha_modificacion)
        VALUES (v_id_var, 1, 42.0, 68.0, NOW());
    END IF;
END $$;
DO $$
DECLARE
    v_id_sub INT;
    v_id_uni INT;
    v_id_prod INT;
    v_id_var INT;
BEGIN
    SELECT id_subcategoria INTO v_id_sub FROM subcategoria WHERE nombre = 'Peluches' LIMIT 1;
    SELECT id_unidad INTO v_id_uni FROM unidad_medida WHERE codigo = 'UND' LIMIT 1;
    IF v_id_uni IS NULL THEN
        SELECT id_unidad INTO v_id_uni FROM unidad_medida WHERE codigo = 'UND' LIMIT 1;
    END IF;

    SELECT id_producto INTO v_id_prod FROM producto WHERE nombre = 'Peluche Conejo Orejas Caídas con Suéter';
    IF v_id_prod IS NULL THEN
        INSERT INTO producto (id_subcategoria, id_unidad, nombre, descripcion, imagen_url, estado, fecha_creacion)
        VALUES (v_id_sub, v_id_uni, 'Peluche Conejo Orejas Caídas con Suéter', 'Conejito tierno con vestimenta tejida desmontable', NULL, 'Activo', NOW())
        RETURNING id_producto INTO v_id_prod;

        INSERT INTO variante_producto (id_producto, codigo_barras, talla, color, precio_detalle, precio_mayoreo, costo_promedio)
        VALUES (v_id_prod, '7401202601018', '32cm', 'Crema', 58.0, 50.0, 36.0)
        RETURNING id_variante INTO v_id_var;

        INSERT INTO inventario_sucursal (id_variante, id_sucursal, id_area, stock_actual, stock_minimo, fecha_actualizacion)
        VALUES (v_id_var, 1, 1, 28, 6, NOW());

        INSERT INTO historial_precio (id_variante, id_usuario, precio_anterior, precio_nuevo, fecha_modificacion)
        VALUES (v_id_var, 1, 36.0, 58.0, NOW());
    END IF;
END $$;
DO $$
DECLARE
    v_id_sub INT;
    v_id_uni INT;
    v_id_prod INT;
    v_id_var INT;
BEGIN
    SELECT id_subcategoria INTO v_id_sub FROM subcategoria WHERE nombre = 'Peluches' LIMIT 1;
    SELECT id_unidad INTO v_id_uni FROM unidad_medida WHERE codigo = 'UND' LIMIT 1;
    IF v_id_uni IS NULL THEN
        SELECT id_unidad INTO v_id_uni FROM unidad_medida WHERE codigo = 'UND' LIMIT 1;
    END IF;

    SELECT id_producto INTO v_id_prod FROM producto WHERE nombre = 'Peluche Ave Quetzal Guatemalteco 30cm';
    IF v_id_prod IS NULL THEN
        INSERT INTO producto (id_subcategoria, id_unidad, nombre, descripcion, imagen_url, estado, fecha_creacion)
        VALUES (v_id_sub, v_id_uni, 'Peluche Ave Quetzal Guatemalteco 30cm', 'Quetzal representativo con cola larga y colores vivos', NULL, 'Activo', NOW())
        RETURNING id_producto INTO v_id_prod;

        INSERT INTO variante_producto (id_producto, codigo_barras, talla, color, precio_detalle, precio_mayoreo, costo_promedio)
        VALUES (v_id_prod, '7401202601019', '30cm', 'Verde/Rojo', 55.0, 48.0, 35.0)
        RETURNING id_variante INTO v_id_var;

        INSERT INTO inventario_sucursal (id_variante, id_sucursal, id_area, stock_actual, stock_minimo, fecha_actualizacion)
        VALUES (v_id_var, 1, 1, 35, 10, NOW());

        INSERT INTO historial_precio (id_variante, id_usuario, precio_anterior, precio_nuevo, fecha_modificacion)
        VALUES (v_id_var, 1, 35.0, 55.0, NOW());
    END IF;
END $$;
DO $$
DECLARE
    v_id_sub INT;
    v_id_uni INT;
    v_id_prod INT;
    v_id_var INT;
BEGIN
    SELECT id_subcategoria INTO v_id_sub FROM subcategoria WHERE nombre = 'Peluches' LIMIT 1;
    SELECT id_unidad INTO v_id_uni FROM unidad_medida WHERE codigo = 'UND' LIMIT 1;
    IF v_id_uni IS NULL THEN
        SELECT id_unidad INTO v_id_uni FROM unidad_medida WHERE codigo = 'UND' LIMIT 1;
    END IF;

    SELECT id_producto INTO v_id_prod FROM producto WHERE nombre = 'Peluche Elefante con Cobija para Bebé';
    IF v_id_prod IS NULL THEN
        INSERT INTO producto (id_subcategoria, id_unidad, nombre, descripcion, imagen_url, estado, fecha_creacion)
        VALUES (v_id_sub, v_id_uni, 'Peluche Elefante con Cobija para Bebé', 'Elefantito afelpado con mantita térmica abrazable', NULL, 'Activo', NOW())
        RETURNING id_producto INTO v_id_prod;

        INSERT INTO variante_producto (id_producto, codigo_barras, talla, color, precio_detalle, precio_mayoreo, costo_promedio)
        VALUES (v_id_prod, '7401202601020', '30cm', 'Gris/Celeste', 88.0, 75.0, 55.0)
        RETURNING id_variante INTO v_id_var;

        INSERT INTO inventario_sucursal (id_variante, id_sucursal, id_area, stock_actual, stock_minimo, fecha_actualizacion)
        VALUES (v_id_var, 1, 1, 18, 5, NOW());

        INSERT INTO historial_precio (id_variante, id_usuario, precio_anterior, precio_nuevo, fecha_modificacion)
        VALUES (v_id_var, 1, 55.0, 88.0, NOW());
    END IF;
END $$;

-- --- Subcatálogo: Servilletas y Mantelería (10 productos) ---
DO $$
DECLARE
    v_id_sub INT;
    v_id_uni INT;
    v_id_prod INT;
    v_id_var INT;
BEGIN
    SELECT id_subcategoria INTO v_id_sub FROM subcategoria WHERE nombre = 'Servilletas y Mantelería' LIMIT 1;
    SELECT id_unidad INTO v_id_uni FROM unidad_medida WHERE codigo = 'PKT' LIMIT 1;
    IF v_id_uni IS NULL THEN
        SELECT id_unidad INTO v_id_uni FROM unidad_medida WHERE codigo = 'UND' LIMIT 1;
    END IF;

    SELECT id_producto INTO v_id_prod FROM producto WHERE nombre = 'Servilletas de Papel Doble Hoja Pack 100u';
    IF v_id_prod IS NULL THEN
        INSERT INTO producto (id_subcategoria, id_unidad, nombre, descripcion, imagen_url, estado, fecha_creacion)
        VALUES (v_id_sub, v_id_uni, 'Servilletas de Papel Doble Hoja Pack 100u', 'Servilletas absorbentes texturizadas de celulosa pura', NULL, 'Activo', NOW())
        RETURNING id_producto INTO v_id_prod;

        INSERT INTO variante_producto (id_producto, codigo_barras, talla, color, precio_detalle, precio_mayoreo, costo_promedio)
        VALUES (v_id_prod, '7401202601021', 'Pack 100', 'Blanco', 11.0, 9.0, 6.5)
        RETURNING id_variante INTO v_id_var;

        INSERT INTO inventario_sucursal (id_variante, id_sucursal, id_area, stock_actual, stock_minimo, fecha_actualizacion)
        VALUES (v_id_var, 1, 2, 60, 20, NOW());

        INSERT INTO historial_precio (id_variante, id_usuario, precio_anterior, precio_nuevo, fecha_modificacion)
        VALUES (v_id_var, 1, 6.5, 11.0, NOW());
    END IF;
END $$;
DO $$
DECLARE
    v_id_sub INT;
    v_id_uni INT;
    v_id_prod INT;
    v_id_var INT;
BEGIN
    SELECT id_subcategoria INTO v_id_sub FROM subcategoria WHERE nombre = 'Servilletas y Mantelería' LIMIT 1;
    SELECT id_unidad INTO v_id_uni FROM unidad_medida WHERE codigo = 'SET' LIMIT 1;
    IF v_id_uni IS NULL THEN
        SELECT id_unidad INTO v_id_uni FROM unidad_medida WHERE codigo = 'UND' LIMIT 1;
    END IF;

    SELECT id_producto INTO v_id_prod FROM producto WHERE nombre = 'Servilletas de Tela Algodón para Mesa Pack x6';
    IF v_id_prod IS NULL THEN
        INSERT INTO producto (id_subcategoria, id_unidad, nombre, descripcion, imagen_url, estado, fecha_creacion)
        VALUES (v_id_sub, v_id_uni, 'Servilletas de Tela Algodón para Mesa Pack x6', 'Juego de 6 servilletas de tela lavable con dobladillo fino', NULL, 'Activo', NOW())
        RETURNING id_producto INTO v_id_prod;

        INSERT INTO variante_producto (id_producto, codigo_barras, talla, color, precio_detalle, precio_mayoreo, costo_promedio)
        VALUES (v_id_prod, '7401202601022', '45x45cm', 'Beige', 55.0, 45.0, 32.0)
        RETURNING id_variante INTO v_id_var;

        INSERT INTO inventario_sucursal (id_variante, id_sucursal, id_area, stock_actual, stock_minimo, fecha_actualizacion)
        VALUES (v_id_var, 1, 1, 30, 8, NOW());

        INSERT INTO historial_precio (id_variante, id_usuario, precio_anterior, precio_nuevo, fecha_modificacion)
        VALUES (v_id_var, 1, 32.0, 55.0, NOW());
    END IF;
END $$;
DO $$
DECLARE
    v_id_sub INT;
    v_id_uni INT;
    v_id_prod INT;
    v_id_var INT;
BEGIN
    SELECT id_subcategoria INTO v_id_sub FROM subcategoria WHERE nombre = 'Servilletas y Mantelería' LIMIT 1;
    SELECT id_unidad INTO v_id_uni FROM unidad_medida WHERE codigo = 'PKT' LIMIT 1;
    IF v_id_uni IS NULL THEN
        SELECT id_unidad INTO v_id_uni FROM unidad_medida WHERE codigo = 'UND' LIMIT 1;
    END IF;

    SELECT id_producto INTO v_id_prod FROM producto WHERE nombre = 'Servilletas Decorativas Festivas Pack 50u';
    IF v_id_prod IS NULL THEN
        INSERT INTO producto (id_subcategoria, id_unidad, nombre, descripcion, imagen_url, estado, fecha_creacion)
        VALUES (v_id_sub, v_id_uni, 'Servilletas Decorativas Festivas Pack 50u', 'Servilletas con estampados coloridos para fiestas y reuniones', NULL, 'Activo', NOW())
        RETURNING id_producto INTO v_id_prod;

        INSERT INTO variante_producto (id_producto, codigo_barras, talla, color, precio_detalle, precio_mayoreo, costo_promedio)
        VALUES (v_id_prod, '7401202601023', 'Pack 50', 'Multicolor', 15.0, 12.0, 8.0)
        RETURNING id_variante INTO v_id_var;

        INSERT INTO inventario_sucursal (id_variante, id_sucursal, id_area, stock_actual, stock_minimo, fecha_actualizacion)
        VALUES (v_id_var, 1, 1, 45, 10, NOW());

        INSERT INTO historial_precio (id_variante, id_usuario, precio_anterior, precio_nuevo, fecha_modificacion)
        VALUES (v_id_var, 1, 8.0, 15.0, NOW());
    END IF;
END $$;
DO $$
DECLARE
    v_id_sub INT;
    v_id_uni INT;
    v_id_prod INT;
    v_id_var INT;
BEGIN
    SELECT id_subcategoria INTO v_id_sub FROM subcategoria WHERE nombre = 'Servilletas y Mantelería' LIMIT 1;
    SELECT id_unidad INTO v_id_uni FROM unidad_medida WHERE codigo = 'SET' LIMIT 1;
    IF v_id_uni IS NULL THEN
        SELECT id_unidad INTO v_id_uni FROM unidad_medida WHERE codigo = 'UND' LIMIT 1;
    END IF;

    SELECT id_producto INTO v_id_prod FROM producto WHERE nombre = 'Servilletas de Lino Fino para Eventos Pack x4';
    IF v_id_prod IS NULL THEN
        INSERT INTO producto (id_subcategoria, id_unidad, nombre, descripcion, imagen_url, estado, fecha_creacion)
        VALUES (v_id_sub, v_id_uni, 'Servilletas de Lino Fino para Eventos Pack x4', 'Servilletas elegantes de lino ideales para cenas formales', NULL, 'Activo', NOW())
        RETURNING id_producto INTO v_id_prod;

        INSERT INTO variante_producto (id_producto, codigo_barras, talla, color, precio_detalle, precio_mayoreo, costo_promedio)
        VALUES (v_id_prod, '7401202601024', '50x50cm', 'Blanco Hueso', 68.0, 56.0, 40.0)
        RETURNING id_variante INTO v_id_var;

        INSERT INTO inventario_sucursal (id_variante, id_sucursal, id_area, stock_actual, stock_minimo, fecha_actualizacion)
        VALUES (v_id_var, 1, 1, 25, 6, NOW());

        INSERT INTO historial_precio (id_variante, id_usuario, precio_anterior, precio_nuevo, fecha_modificacion)
        VALUES (v_id_var, 1, 40.0, 68.0, NOW());
    END IF;
END $$;
DO $$
DECLARE
    v_id_sub INT;
    v_id_uni INT;
    v_id_prod INT;
    v_id_var INT;
BEGIN
    SELECT id_subcategoria INTO v_id_sub FROM subcategoria WHERE nombre = 'Servilletas y Mantelería' LIMIT 1;
    SELECT id_unidad INTO v_id_uni FROM unidad_medida WHERE codigo = 'PKT' LIMIT 1;
    IF v_id_uni IS NULL THEN
        SELECT id_unidad INTO v_id_uni FROM unidad_medida WHERE codigo = 'UND' LIMIT 1;
    END IF;

    SELECT id_producto INTO v_id_prod FROM producto WHERE nombre = 'Servilletas Cocktail Bar & Café Pack 100u';
    IF v_id_prod IS NULL THEN
        INSERT INTO producto (id_subcategoria, id_unidad, nombre, descripcion, imagen_url, estado, fecha_creacion)
        VALUES (v_id_sub, v_id_uni, 'Servilletas Cocktail Bar & Café Pack 100u', 'Servilletas pequeñas cuadradas para bocadillos y bebidas', NULL, 'Activo', NOW())
        RETURNING id_producto INTO v_id_prod;

        INSERT INTO variante_producto (id_producto, codigo_barras, talla, color, precio_detalle, precio_mayoreo, costo_promedio)
        VALUES (v_id_prod, '7401202601025', '25x25cm', 'Negro', 13.0, 10.5, 7.5)
        RETURNING id_variante INTO v_id_var;

        INSERT INTO inventario_sucursal (id_variante, id_sucursal, id_area, stock_actual, stock_minimo, fecha_actualizacion)
        VALUES (v_id_var, 1, 3, 50, 15, NOW());

        INSERT INTO historial_precio (id_variante, id_usuario, precio_anterior, precio_nuevo, fecha_modificacion)
        VALUES (v_id_var, 1, 7.5, 13.0, NOW());
    END IF;
END $$;
DO $$
DECLARE
    v_id_sub INT;
    v_id_uni INT;
    v_id_prod INT;
    v_id_var INT;
BEGIN
    SELECT id_subcategoria INTO v_id_sub FROM subcategoria WHERE nombre = 'Servilletas y Mantelería' LIMIT 1;
    SELECT id_unidad INTO v_id_uni FROM unidad_medida WHERE codigo = 'UND' LIMIT 1;
    IF v_id_uni IS NULL THEN
        SELECT id_unidad INTO v_id_uni FROM unidad_medida WHERE codigo = 'UND' LIMIT 1;
    END IF;

    SELECT id_producto INTO v_id_prod FROM producto WHERE nombre = 'Servilletas de Cocina Rollo Jumbo Absorbente';
    IF v_id_prod IS NULL THEN
        INSERT INTO producto (id_subcategoria, id_unidad, nombre, descripcion, imagen_url, estado, fecha_creacion)
        VALUES (v_id_sub, v_id_uni, 'Servilletas de Cocina Rollo Jumbo Absorbente', 'Toallín de cocina doble hoja resistente a líquidos y grasas', NULL, 'Activo', NOW())
        RETURNING id_producto INTO v_id_prod;

        INSERT INTO variante_producto (id_producto, codigo_barras, talla, color, precio_detalle, precio_mayoreo, costo_promedio)
        VALUES (v_id_prod, '7401202601026', 'Jumbo 200h', 'Blanco', 19.5, 16.5, 12.0)
        RETURNING id_variante INTO v_id_var;

        INSERT INTO inventario_sucursal (id_variante, id_sucursal, id_area, stock_actual, stock_minimo, fecha_actualizacion)
        VALUES (v_id_var, 1, 2, 40, 10, NOW());

        INSERT INTO historial_precio (id_variante, id_usuario, precio_anterior, precio_nuevo, fecha_modificacion)
        VALUES (v_id_var, 1, 12.0, 19.5, NOW());
    END IF;
END $$;
DO $$
DECLARE
    v_id_sub INT;
    v_id_uni INT;
    v_id_prod INT;
    v_id_var INT;
BEGIN
    SELECT id_subcategoria INTO v_id_sub FROM subcategoria WHERE nombre = 'Servilletas y Mantelería' LIMIT 1;
    SELECT id_unidad INTO v_id_uni FROM unidad_medida WHERE codigo = 'PKT' LIMIT 1;
    IF v_id_uni IS NULL THEN
        SELECT id_unidad INTO v_id_uni FROM unidad_medida WHERE codigo = 'UND' LIMIT 1;
    END IF;

    SELECT id_producto INTO v_id_prod FROM producto WHERE nombre = 'Servilletas Kraft Ecológicas Biodegradables 200u';
    IF v_id_prod IS NULL THEN
        INSERT INTO producto (id_subcategoria, id_unidad, nombre, descripcion, imagen_url, estado, fecha_creacion)
        VALUES (v_id_sub, v_id_uni, 'Servilletas Kraft Ecológicas Biodegradables 200u', 'Servilletas 100% recicladas sin blanqueadores químicos', NULL, 'Activo', NOW())
        RETURNING id_producto INTO v_id_prod;

        INSERT INTO variante_producto (id_producto, codigo_barras, talla, color, precio_detalle, precio_mayoreo, costo_promedio)
        VALUES (v_id_prod, '7401202601027', 'Pack 200', 'Café Kraft', 24.0, 19.0, 14.0)
        RETURNING id_variante INTO v_id_var;

        INSERT INTO inventario_sucursal (id_variante, id_sucursal, id_area, stock_actual, stock_minimo, fecha_actualizacion)
        VALUES (v_id_var, 1, 2, 35, 10, NOW());

        INSERT INTO historial_precio (id_variante, id_usuario, precio_anterior, precio_nuevo, fecha_modificacion)
        VALUES (v_id_var, 1, 14.0, 24.0, NOW());
    END IF;
END $$;
DO $$
DECLARE
    v_id_sub INT;
    v_id_uni INT;
    v_id_prod INT;
    v_id_var INT;
BEGIN
    SELECT id_subcategoria INTO v_id_sub FROM subcategoria WHERE nombre = 'Servilletas y Mantelería' LIMIT 1;
    SELECT id_unidad INTO v_id_uni FROM unidad_medida WHERE codigo = 'SET' LIMIT 1;
    IF v_id_uni IS NULL THEN
        SELECT id_unidad INTO v_id_uni FROM unidad_medida WHERE codigo = 'UND' LIMIT 1;
    END IF;

    SELECT id_producto INTO v_id_prod FROM producto WHERE nombre = 'Servilletas Navideñas Tradicionales Pack x6';
    IF v_id_prod IS NULL THEN
        INSERT INTO producto (id_subcategoria, id_unidad, nombre, descripcion, imagen_url, estado, fecha_creacion)
        VALUES (v_id_sub, v_id_uni, 'Servilletas Navideñas Tradicionales Pack x6', 'Servilletas de tela con motivos navideños bordados', NULL, 'Activo', NOW())
        RETURNING id_producto INTO v_id_prod;

        INSERT INTO variante_producto (id_producto, codigo_barras, talla, color, precio_detalle, precio_mayoreo, costo_promedio)
        VALUES (v_id_prod, '7401202601028', '40x40cm', 'Rojo/Verde', 58.0, 48.0, 35.0)
        RETURNING id_variante INTO v_id_var;

        INSERT INTO inventario_sucursal (id_variante, id_sucursal, id_area, stock_actual, stock_minimo, fecha_actualizacion)
        VALUES (v_id_var, 1, 1, 20, 5, NOW());

        INSERT INTO historial_precio (id_variante, id_usuario, precio_anterior, precio_nuevo, fecha_modificacion)
        VALUES (v_id_var, 1, 35.0, 58.0, NOW());
    END IF;
END $$;
DO $$
DECLARE
    v_id_sub INT;
    v_id_uni INT;
    v_id_prod INT;
    v_id_var INT;
BEGIN
    SELECT id_subcategoria INTO v_id_sub FROM subcategoria WHERE nombre = 'Servilletas y Mantelería' LIMIT 1;
    SELECT id_unidad INTO v_id_uni FROM unidad_medida WHERE codigo = 'PKT' LIMIT 1;
    IF v_id_uni IS NULL THEN
        SELECT id_unidad INTO v_id_uni FROM unidad_medida WHERE codigo = 'UND' LIMIT 1;
    END IF;

    SELECT id_producto INTO v_id_prod FROM producto WHERE nombre = 'Servilletas Dispensador Restaurante Paquete 500u';
    IF v_id_prod IS NULL THEN
        INSERT INTO producto (id_subcategoria, id_unidad, nombre, descripcion, imagen_url, estado, fecha_creacion)
        VALUES (v_id_sub, v_id_uni, 'Servilletas Dispensador Restaurante Paquete 500u', 'Servilleta doblada en V especial para dispensador de mesa', NULL, 'Activo', NOW())
        RETURNING id_producto INTO v_id_prod;

        INSERT INTO variante_producto (id_producto, codigo_barras, talla, color, precio_detalle, precio_mayoreo, costo_promedio)
        VALUES (v_id_prod, '7401202601029', 'Pack 500', 'Blanco', 36.0, 30.0, 22.0)
        RETURNING id_variante INTO v_id_var;

        INSERT INTO inventario_sucursal (id_variante, id_sucursal, id_area, stock_actual, stock_minimo, fecha_actualizacion)
        VALUES (v_id_var, 1, 2, 40, 10, NOW());

        INSERT INTO historial_precio (id_variante, id_usuario, precio_anterior, precio_nuevo, fecha_modificacion)
        VALUES (v_id_var, 1, 22.0, 36.0, NOW());
    END IF;
END $$;
DO $$
DECLARE
    v_id_sub INT;
    v_id_uni INT;
    v_id_prod INT;
    v_id_var INT;
BEGIN
    SELECT id_subcategoria INTO v_id_sub FROM subcategoria WHERE nombre = 'Servilletas y Mantelería' LIMIT 1;
    SELECT id_unidad INTO v_id_uni FROM unidad_medida WHERE codigo = 'SET' LIMIT 1;
    IF v_id_uni IS NULL THEN
        SELECT id_unidad INTO v_id_uni FROM unidad_medida WHERE codigo = 'UND' LIMIT 1;
    END IF;

    SELECT id_producto INTO v_id_prod FROM producto WHERE nombre = 'Servilletas Típicas Tejidas en Telar Pack x4';
    IF v_id_prod IS NULL THEN
        INSERT INTO producto (id_subcategoria, id_unidad, nombre, descripcion, imagen_url, estado, fecha_creacion)
        VALUES (v_id_sub, v_id_uni, 'Servilletas Típicas Tejidas en Telar Pack x4', 'Servilletas artesanales tejidas a mano por artesanas de Sololá', NULL, 'Activo', NOW())
        RETURNING id_producto INTO v_id_prod;

        INSERT INTO variante_producto (id_producto, codigo_barras, talla, color, precio_detalle, precio_mayoreo, costo_promedio)
        VALUES (v_id_prod, '7401202601030', '38x38cm', 'Típico Sololá', 65.0, 52.0, 38.0)
        RETURNING id_variante INTO v_id_var;

        INSERT INTO inventario_sucursal (id_variante, id_sucursal, id_area, stock_actual, stock_minimo, fecha_actualizacion)
        VALUES (v_id_var, 1, 1, 25, 6, NOW());

        INSERT INTO historial_precio (id_variante, id_usuario, precio_anterior, precio_nuevo, fecha_modificacion)
        VALUES (v_id_var, 1, 38.0, 65.0, NOW());
    END IF;
END $$;

-- --- Subcatálogo: Bolsas y Mochilas (10 productos) ---
DO $$
DECLARE
    v_id_sub INT;
    v_id_uni INT;
    v_id_prod INT;
    v_id_var INT;
BEGIN
    SELECT id_subcategoria INTO v_id_sub FROM subcategoria WHERE nombre = 'Bolsas y Mochilas' LIMIT 1;
    SELECT id_unidad INTO v_id_uni FROM unidad_medida WHERE codigo = 'UND' LIMIT 1;
    IF v_id_uni IS NULL THEN
        SELECT id_unidad INTO v_id_uni FROM unidad_medida WHERE codigo = 'UND' LIMIT 1;
    END IF;

    SELECT id_producto INTO v_id_prod FROM producto WHERE nombre = 'Bolsa de Tela Ecológica con Bordado Típico';
    IF v_id_prod IS NULL THEN
        INSERT INTO producto (id_subcategoria, id_unidad, nombre, descripcion, imagen_url, estado, fecha_creacion)
        VALUES (v_id_sub, v_id_uni, 'Bolsa de Tela Ecológica con Bordado Típico', 'Bolsa totebag reutilizable resistente para compras y paseo', NULL, 'Activo', NOW())
        RETURNING id_producto INTO v_id_prod;

        INSERT INTO variante_producto (id_producto, codigo_barras, talla, color, precio_detalle, precio_mayoreo, costo_promedio)
        VALUES (v_id_prod, '7401202601031', '40x38cm', 'Multicolor', 35.0, 28.0, 20.0)
        RETURNING id_variante INTO v_id_var;

        INSERT INTO inventario_sucursal (id_variante, id_sucursal, id_area, stock_actual, stock_minimo, fecha_actualizacion)
        VALUES (v_id_var, 1, 1, 50, 15, NOW());

        INSERT INTO historial_precio (id_variante, id_usuario, precio_anterior, precio_nuevo, fecha_modificacion)
        VALUES (v_id_var, 1, 20.0, 35.0, NOW());
    END IF;
END $$;
DO $$
DECLARE
    v_id_sub INT;
    v_id_uni INT;
    v_id_prod INT;
    v_id_var INT;
BEGIN
    SELECT id_subcategoria INTO v_id_sub FROM subcategoria WHERE nombre = 'Bolsas y Mochilas' LIMIT 1;
    SELECT id_unidad INTO v_id_uni FROM unidad_medida WHERE codigo = 'UND' LIMIT 1;
    IF v_id_uni IS NULL THEN
        SELECT id_unidad INTO v_id_uni FROM unidad_medida WHERE codigo = 'UND' LIMIT 1;
    END IF;

    SELECT id_producto INTO v_id_prod FROM producto WHERE nombre = 'Bolsa Térmica Lonchera Aislada';
    IF v_id_prod IS NULL THEN
        INSERT INTO producto (id_subcategoria, id_unidad, nombre, descripcion, imagen_url, estado, fecha_creacion)
        VALUES (v_id_sub, v_id_uni, 'Bolsa Térmica Lonchera Aislada', 'Bolsa portaalimentos impermeable que mantiene temperatura', NULL, 'Activo', NOW())
        RETURNING id_producto INTO v_id_prod;

        INSERT INTO variante_producto (id_producto, codigo_barras, talla, color, precio_detalle, precio_mayoreo, costo_promedio)
        VALUES (v_id_prod, '7401202601032', 'Mediana', 'Azul Marino', 45.0, 38.0, 28.0)
        RETURNING id_variante INTO v_id_var;

        INSERT INTO inventario_sucursal (id_variante, id_sucursal, id_area, stock_actual, stock_minimo, fecha_actualizacion)
        VALUES (v_id_var, 1, 1, 30, 8, NOW());

        INSERT INTO historial_precio (id_variante, id_usuario, precio_anterior, precio_nuevo, fecha_modificacion)
        VALUES (v_id_var, 1, 28.0, 45.0, NOW());
    END IF;
END $$;
DO $$
DECLARE
    v_id_sub INT;
    v_id_uni INT;
    v_id_prod INT;
    v_id_var INT;
BEGIN
    SELECT id_subcategoria INTO v_id_sub FROM subcategoria WHERE nombre = 'Bolsas y Mochilas' LIMIT 1;
    SELECT id_unidad INTO v_id_uni FROM unidad_medida WHERE codigo = 'UND' LIMIT 1;
    IF v_id_uni IS NULL THEN
        SELECT id_unidad INTO v_id_uni FROM unidad_medida WHERE codigo = 'UND' LIMIT 1;
    END IF;

    SELECT id_producto INTO v_id_prod FROM producto WHERE nombre = 'Mochila Juvenil de Lona Casual';
    IF v_id_prod IS NULL THEN
        INSERT INTO producto (id_subcategoria, id_unidad, nombre, descripcion, imagen_url, estado, fecha_creacion)
        VALUES (v_id_sub, v_id_uni, 'Mochila Juvenil de Lona Casual', 'Mochila resistente con compartimentos frontales para uso diario', NULL, 'Activo', NOW())
        RETURNING id_producto INTO v_id_prod;

        INSERT INTO variante_producto (id_producto, codigo_barras, talla, color, precio_detalle, precio_mayoreo, costo_promedio)
        VALUES (v_id_prod, '7401202601033', 'Grande', 'Negro', 125.0, 105.0, 75.0)
        RETURNING id_variante INTO v_id_var;

        INSERT INTO inventario_sucursal (id_variante, id_sucursal, id_area, stock_actual, stock_minimo, fecha_actualizacion)
        VALUES (v_id_var, 1, 1, 25, 6, NOW());

        INSERT INTO historial_precio (id_variante, id_usuario, precio_anterior, precio_nuevo, fecha_modificacion)
        VALUES (v_id_var, 1, 75.0, 125.0, NOW());
    END IF;
END $$;
DO $$
DECLARE
    v_id_sub INT;
    v_id_uni INT;
    v_id_prod INT;
    v_id_var INT;
BEGIN
    SELECT id_subcategoria INTO v_id_sub FROM subcategoria WHERE nombre = 'Bolsas y Mochilas' LIMIT 1;
    SELECT id_unidad INTO v_id_uni FROM unidad_medida WHERE codigo = 'UND' LIMIT 1;
    IF v_id_uni IS NULL THEN
        SELECT id_unidad INTO v_id_uni FROM unidad_medida WHERE codigo = 'UND' LIMIT 1;
    END IF;

    SELECT id_producto INTO v_id_prod FROM producto WHERE nombre = 'Bolsa de Malla Reforzada para Mercado';
    IF v_id_prod IS NULL THEN
        INSERT INTO producto (id_subcategoria, id_unidad, nombre, descripcion, imagen_url, estado, fecha_creacion)
        VALUES (v_id_sub, v_id_uni, 'Bolsa de Malla Reforzada para Mercado', 'Bolsa tradicional de plástico calado lavable de gran capacidad', NULL, 'Activo', NOW())
        RETURNING id_producto INTO v_id_prod;

        INSERT INTO variante_producto (id_producto, codigo_barras, talla, color, precio_detalle, precio_mayoreo, costo_promedio)
        VALUES (v_id_prod, '7401202601034', 'Grande', 'Verde', 28.0, 22.0, 15.0)
        RETURNING id_variante INTO v_id_var;

        INSERT INTO inventario_sucursal (id_variante, id_sucursal, id_area, stock_actual, stock_minimo, fecha_actualizacion)
        VALUES (v_id_var, 1, 2, 45, 10, NOW());

        INSERT INTO historial_precio (id_variante, id_usuario, precio_anterior, precio_nuevo, fecha_modificacion)
        VALUES (v_id_var, 1, 15.0, 28.0, NOW());
    END IF;
END $$;
DO $$
DECLARE
    v_id_sub INT;
    v_id_uni INT;
    v_id_prod INT;
    v_id_var INT;
BEGIN
    SELECT id_subcategoria INTO v_id_sub FROM subcategoria WHERE nombre = 'Bolsas y Mochilas' LIMIT 1;
    SELECT id_unidad INTO v_id_uni FROM unidad_medida WHERE codigo = 'UND' LIMIT 1;
    IF v_id_uni IS NULL THEN
        SELECT id_unidad INTO v_id_uni FROM unidad_medida WHERE codigo = 'UND' LIMIT 1;
    END IF;

    SELECT id_producto INTO v_id_prod FROM producto WHERE nombre = 'Bolsa de Regalo Premium Mate Grande';
    IF v_id_prod IS NULL THEN
        INSERT INTO producto (id_subcategoria, id_unidad, nombre, descripcion, imagen_url, estado, fecha_creacion)
        VALUES (v_id_sub, v_id_uni, 'Bolsa de Regalo Premium Mate Grande', 'Bolsa de cartón grueso laminado con cinta de seda y tarjeta', NULL, 'Activo', NOW())
        RETURNING id_producto INTO v_id_prod;

        INSERT INTO variante_producto (id_producto, codigo_barras, talla, color, precio_detalle, precio_mayoreo, costo_promedio)
        VALUES (v_id_prod, '7401202601035', '32x26x12cm', 'Dorado Mate', 14.0, 10.0, 7.0)
        RETURNING id_variante INTO v_id_var;

        INSERT INTO inventario_sucursal (id_variante, id_sucursal, id_area, stock_actual, stock_minimo, fecha_actualizacion)
        VALUES (v_id_var, 1, 3, 60, 20, NOW());

        INSERT INTO historial_precio (id_variante, id_usuario, precio_anterior, precio_nuevo, fecha_modificacion)
        VALUES (v_id_var, 1, 7.0, 14.0, NOW());
    END IF;
END $$;
DO $$
DECLARE
    v_id_sub INT;
    v_id_uni INT;
    v_id_prod INT;
    v_id_var INT;
BEGIN
    SELECT id_subcategoria INTO v_id_sub FROM subcategoria WHERE nombre = 'Bolsas y Mochilas' LIMIT 1;
    SELECT id_unidad INTO v_id_uni FROM unidad_medida WHERE codigo = 'UND' LIMIT 1;
    IF v_id_uni IS NULL THEN
        SELECT id_unidad INTO v_id_uni FROM unidad_medida WHERE codigo = 'UND' LIMIT 1;
    END IF;

    SELECT id_producto INTO v_id_prod FROM producto WHERE nombre = 'Bolso Playero Impermeable Rayado';
    IF v_id_prod IS NULL THEN
        INSERT INTO producto (id_subcategoria, id_unidad, nombre, descripcion, imagen_url, estado, fecha_creacion)
        VALUES (v_id_sub, v_id_uni, 'Bolso Playero Impermeable Rayado', 'Bolso amplio de lona náutica con cierre zipper y forro interior', NULL, 'Activo', NOW())
        RETURNING id_producto INTO v_id_prod;

        INSERT INTO variante_producto (id_producto, codigo_barras, talla, color, precio_detalle, precio_mayoreo, costo_promedio)
        VALUES (v_id_prod, '7401202601036', '50x35cm', 'Azul/Blanco', 75.0, 62.0, 45.0)
        RETURNING id_variante INTO v_id_var;

        INSERT INTO inventario_sucursal (id_variante, id_sucursal, id_area, stock_actual, stock_minimo, fecha_actualizacion)
        VALUES (v_id_var, 1, 1, 20, 5, NOW());

        INSERT INTO historial_precio (id_variante, id_usuario, precio_anterior, precio_nuevo, fecha_modificacion)
        VALUES (v_id_var, 1, 45.0, 75.0, NOW());
    END IF;
END $$;
DO $$
DECLARE
    v_id_sub INT;
    v_id_uni INT;
    v_id_prod INT;
    v_id_var INT;
BEGIN
    SELECT id_subcategoria INTO v_id_sub FROM subcategoria WHERE nombre = 'Bolsas y Mochilas' LIMIT 1;
    SELECT id_unidad INTO v_id_uni FROM unidad_medida WHERE codigo = 'UND' LIMIT 1;
    IF v_id_uni IS NULL THEN
        SELECT id_unidad INTO v_id_uni FROM unidad_medida WHERE codigo = 'UND' LIMIT 1;
    END IF;

    SELECT id_producto INTO v_id_prod FROM producto WHERE nombre = 'Bolsa Riñonera Cruzada Deportiva';
    IF v_id_prod IS NULL THEN
        INSERT INTO producto (id_subcategoria, id_unidad, nombre, descripcion, imagen_url, estado, fecha_creacion)
        VALUES (v_id_sub, v_id_uni, 'Bolsa Riñonera Cruzada Deportiva', 'Riñonera pechera impermeable con salida para audífonos', NULL, 'Activo', NOW())
        RETURNING id_producto INTO v_id_prod;

        INSERT INTO variante_producto (id_producto, codigo_barras, talla, color, precio_detalle, precio_mayoreo, costo_promedio)
        VALUES (v_id_prod, '7401202601037', 'Ajustable', 'Gris Carbón', 52.0, 44.0, 32.0)
        RETURNING id_variante INTO v_id_var;

        INSERT INTO inventario_sucursal (id_variante, id_sucursal, id_area, stock_actual, stock_minimo, fecha_actualizacion)
        VALUES (v_id_var, 1, 1, 35, 8, NOW());

        INSERT INTO historial_precio (id_variante, id_usuario, precio_anterior, precio_nuevo, fecha_modificacion)
        VALUES (v_id_var, 1, 32.0, 52.0, NOW());
    END IF;
END $$;
DO $$
DECLARE
    v_id_sub INT;
    v_id_uni INT;
    v_id_prod INT;
    v_id_var INT;
BEGIN
    SELECT id_subcategoria INTO v_id_sub FROM subcategoria WHERE nombre = 'Bolsas y Mochilas' LIMIT 1;
    SELECT id_unidad INTO v_id_uni FROM unidad_medida WHERE codigo = 'UND' LIMIT 1;
    IF v_id_uni IS NULL THEN
        SELECT id_unidad INTO v_id_uni FROM unidad_medida WHERE codigo = 'UND' LIMIT 1;
    END IF;

    SELECT id_producto INTO v_id_prod FROM producto WHERE nombre = 'Bolso Tote de Yute Natural con Asas Suaves';
    IF v_id_prod IS NULL THEN
        INSERT INTO producto (id_subcategoria, id_unidad, nombre, descripcion, imagen_url, estado, fecha_creacion)
        VALUES (v_id_sub, v_id_uni, 'Bolso Tote de Yute Natural con Asas Suaves', 'Bolso ecológico de fibra vegetal con base reforzada', NULL, 'Activo', NOW())
        RETURNING id_producto INTO v_id_prod;

        INSERT INTO variante_producto (id_producto, codigo_barras, talla, color, precio_detalle, precio_mayoreo, costo_promedio)
        VALUES (v_id_prod, '7401202601038', '42x35x15cm', 'Natural', 58.0, 48.0, 35.0)
        RETURNING id_variante INTO v_id_var;

        INSERT INTO inventario_sucursal (id_variante, id_sucursal, id_area, stock_actual, stock_minimo, fecha_actualizacion)
        VALUES (v_id_var, 1, 1, 28, 7, NOW());

        INSERT INTO historial_precio (id_variante, id_usuario, precio_anterior, precio_nuevo, fecha_modificacion)
        VALUES (v_id_var, 1, 35.0, 58.0, NOW());
    END IF;
END $$;
DO $$
DECLARE
    v_id_sub INT;
    v_id_uni INT;
    v_id_prod INT;
    v_id_var INT;
BEGIN
    SELECT id_subcategoria INTO v_id_sub FROM subcategoria WHERE nombre = 'Bolsas y Mochilas' LIMIT 1;
    SELECT id_unidad INTO v_id_uni FROM unidad_medida WHERE codigo = 'UND' LIMIT 1;
    IF v_id_uni IS NULL THEN
        SELECT id_unidad INTO v_id_uni FROM unidad_medida WHERE codigo = 'UND' LIMIT 1;
    END IF;

    SELECT id_producto INTO v_id_prod FROM producto WHERE nombre = 'Maletín Porta Laptop Acolchado 15.6 Pulgadas';
    IF v_id_prod IS NULL THEN
        INSERT INTO producto (id_subcategoria, id_unidad, nombre, descripcion, imagen_url, estado, fecha_creacion)
        VALUES (v_id_sub, v_id_uni, 'Maletín Porta Laptop Acolchado 15.6 Pulgadas', 'Funda maletín con protección antigolpes y correa al hombro', NULL, 'Activo', NOW())
        RETURNING id_producto INTO v_id_prod;

        INSERT INTO variante_producto (id_producto, codigo_barras, talla, color, precio_detalle, precio_mayoreo, costo_promedio)
        VALUES (v_id_prod, '7401202601039', '15.6 pulg', 'Negro/Gris', 115.0, 95.0, 68.0)
        RETURNING id_variante INTO v_id_var;

        INSERT INTO inventario_sucursal (id_variante, id_sucursal, id_area, stock_actual, stock_minimo, fecha_actualizacion)
        VALUES (v_id_var, 1, 1, 22, 5, NOW());

        INSERT INTO historial_precio (id_variante, id_usuario, precio_anterior, precio_nuevo, fecha_modificacion)
        VALUES (v_id_var, 1, 68.0, 115.0, NOW());
    END IF;
END $$;
DO $$
DECLARE
    v_id_sub INT;
    v_id_uni INT;
    v_id_prod INT;
    v_id_var INT;
BEGIN
    SELECT id_subcategoria INTO v_id_sub FROM subcategoria WHERE nombre = 'Bolsas y Mochilas' LIMIT 1;
    SELECT id_unidad INTO v_id_uni FROM unidad_medida WHERE codigo = 'UND' LIMIT 1;
    IF v_id_uni IS NULL THEN
        SELECT id_unidad INTO v_id_uni FROM unidad_medida WHERE codigo = 'UND' LIMIT 1;
    END IF;

    SELECT id_producto INTO v_id_prod FROM producto WHERE nombre = 'Bolsa Plegable Reutilizable de Bolsillo';
    IF v_id_prod IS NULL THEN
        INSERT INTO producto (id_subcategoria, id_unidad, nombre, descripcion, imagen_url, estado, fecha_creacion)
        VALUES (v_id_sub, v_id_uni, 'Bolsa Plegable Reutilizable de Bolsillo', 'Bolsa de nylon impermeable que se dobla en tamaño llavero', NULL, 'Activo', NOW())
        RETURNING id_producto INTO v_id_prod;

        INSERT INTO variante_producto (id_producto, codigo_barras, talla, color, precio_detalle, precio_mayoreo, costo_promedio)
        VALUES (v_id_prod, '7401202601040', 'Compacta', 'Estampado Flores', 16.0, 12.0, 8.0)
        RETURNING id_variante INTO v_id_var;

        INSERT INTO inventario_sucursal (id_variante, id_sucursal, id_area, stock_actual, stock_minimo, fecha_actualizacion)
        VALUES (v_id_var, 1, 3, 55, 15, NOW());

        INSERT INTO historial_precio (id_variante, id_usuario, precio_anterior, precio_nuevo, fecha_modificacion)
        VALUES (v_id_var, 1, 8.0, 16.0, NOW());
    END IF;
END $$;

-- --- Subcatálogo: Ollas y Baterías de Cocina (10 productos) ---
DO $$
DECLARE
    v_id_sub INT;
    v_id_uni INT;
    v_id_prod INT;
    v_id_var INT;
BEGIN
    SELECT id_subcategoria INTO v_id_sub FROM subcategoria WHERE nombre = 'Ollas y Baterías de Cocina' LIMIT 1;
    SELECT id_unidad INTO v_id_uni FROM unidad_medida WHERE codigo = 'UND' LIMIT 1;
    IF v_id_uni IS NULL THEN
        SELECT id_unidad INTO v_id_uni FROM unidad_medida WHERE codigo = 'UND' LIMIT 1;
    END IF;

    SELECT id_producto INTO v_id_prod FROM producto WHERE nombre = 'Olla de Presión de Aluminio Reforzado 6 Litros';
    IF v_id_prod IS NULL THEN
        INSERT INTO producto (id_subcategoria, id_unidad, nombre, descripcion, imagen_url, estado, fecha_creacion)
        VALUES (v_id_sub, v_id_uni, 'Olla de Presión de Aluminio Reforzado 6 Litros', 'Olla exprés con doble válvula de seguridad y asas frías', NULL, 'Activo', NOW())
        RETURNING id_producto INTO v_id_prod;

        INSERT INTO variante_producto (id_producto, codigo_barras, talla, color, precio_detalle, precio_mayoreo, costo_promedio)
        VALUES (v_id_prod, '7401202601041', '6 Litros', 'Plata', 225.0, 195.0, 145.0)
        RETURNING id_variante INTO v_id_var;

        INSERT INTO inventario_sucursal (id_variante, id_sucursal, id_area, stock_actual, stock_minimo, fecha_actualizacion)
        VALUES (v_id_var, 1, 1, 18, 5, NOW());

        INSERT INTO historial_precio (id_variante, id_usuario, precio_anterior, precio_nuevo, fecha_modificacion)
        VALUES (v_id_var, 1, 145.0, 225.0, NOW());
    END IF;
END $$;
DO $$
DECLARE
    v_id_sub INT;
    v_id_uni INT;
    v_id_prod INT;
    v_id_var INT;
BEGIN
    SELECT id_subcategoria INTO v_id_sub FROM subcategoria WHERE nombre = 'Ollas y Baterías de Cocina' LIMIT 1;
    SELECT id_unidad INTO v_id_uni FROM unidad_medida WHERE codigo = 'UND' LIMIT 1;
    IF v_id_uni IS NULL THEN
        SELECT id_unidad INTO v_id_uni FROM unidad_medida WHERE codigo = 'UND' LIMIT 1;
    END IF;

    SELECT id_producto INTO v_id_prod FROM producto WHERE nombre = 'Olla Arrocera Antiadherente con Tapa de Vidrio';
    IF v_id_prod IS NULL THEN
        INSERT INTO producto (id_subcategoria, id_unidad, nombre, descripcion, imagen_url, estado, fecha_creacion)
        VALUES (v_id_sub, v_id_uni, 'Olla Arrocera Antiadherente con Tapa de Vidrio', 'Olla con revestimiento de teflón y pomo aislante 24cm', NULL, 'Activo', NOW())
        RETURNING id_producto INTO v_id_prod;

        INSERT INTO variante_producto (id_producto, codigo_barras, talla, color, precio_detalle, precio_mayoreo, costo_promedio)
        VALUES (v_id_prod, '7401202601042', '24cm / 4L', 'Negro', 115.0, 98.0, 72.0)
        RETURNING id_variante INTO v_id_var;

        INSERT INTO inventario_sucursal (id_variante, id_sucursal, id_area, stock_actual, stock_minimo, fecha_actualizacion)
        VALUES (v_id_var, 1, 1, 20, 5, NOW());

        INSERT INTO historial_precio (id_variante, id_usuario, precio_anterior, precio_nuevo, fecha_modificacion)
        VALUES (v_id_var, 1, 72.0, 115.0, NOW());
    END IF;
END $$;
DO $$
DECLARE
    v_id_sub INT;
    v_id_uni INT;
    v_id_prod INT;
    v_id_var INT;
BEGIN
    SELECT id_subcategoria INTO v_id_sub FROM subcategoria WHERE nombre = 'Ollas y Baterías de Cocina' LIMIT 1;
    SELECT id_unidad INTO v_id_uni FROM unidad_medida WHERE codigo = 'UND' LIMIT 1;
    IF v_id_uni IS NULL THEN
        SELECT id_unidad INTO v_id_uni FROM unidad_medida WHERE codigo = 'UND' LIMIT 1;
    END IF;

    SELECT id_producto INTO v_id_prod FROM producto WHERE nombre = 'Olla Vaporera Tamalera de Gran Capacidad 20L';
    IF v_id_prod IS NULL THEN
        INSERT INTO producto (id_subcategoria, id_unidad, nombre, descripcion, imagen_url, estado, fecha_creacion)
        VALUES (v_id_sub, v_id_uni, 'Olla Vaporera Tamalera de Gran Capacidad 20L', 'Olla tamalera de aluminio con rejilla divisoria desmontable', NULL, 'Activo', NOW())
        RETURNING id_producto INTO v_id_prod;

        INSERT INTO variante_producto (id_producto, codigo_barras, talla, color, precio_detalle, precio_mayoreo, costo_promedio)
        VALUES (v_id_prod, '7401202601043', '20 Litros', 'Aluminio', 190.0, 165.0, 125.0)
        RETURNING id_variante INTO v_id_var;

        INSERT INTO inventario_sucursal (id_variante, id_sucursal, id_area, stock_actual, stock_minimo, fecha_actualizacion)
        VALUES (v_id_var, 1, 2, 15, 4, NOW());

        INSERT INTO historial_precio (id_variante, id_usuario, precio_anterior, precio_nuevo, fecha_modificacion)
        VALUES (v_id_var, 1, 125.0, 190.0, NOW());
    END IF;
END $$;
DO $$
DECLARE
    v_id_sub INT;
    v_id_uni INT;
    v_id_prod INT;
    v_id_var INT;
BEGIN
    SELECT id_subcategoria INTO v_id_sub FROM subcategoria WHERE nombre = 'Ollas y Baterías de Cocina' LIMIT 1;
    SELECT id_unidad INTO v_id_uni FROM unidad_medida WHERE codigo = 'SET' LIMIT 1;
    IF v_id_uni IS NULL THEN
        SELECT id_unidad INTO v_id_uni FROM unidad_medida WHERE codigo = 'UND' LIMIT 1;
    END IF;

    SELECT id_producto INTO v_id_prod FROM producto WHERE nombre = 'Batería de Ollas Acero Inoxidable 5 Piezas';
    IF v_id_prod IS NULL THEN
        INSERT INTO producto (id_subcategoria, id_unidad, nombre, descripcion, imagen_url, estado, fecha_creacion)
        VALUES (v_id_sub, v_id_uni, 'Batería de Ollas Acero Inoxidable 5 Piezas', 'Set de 3 ollas con tapas de vidrio templado y 2 cacerolas', NULL, 'Activo', NOW())
        RETURNING id_producto INTO v_id_prod;

        INSERT INTO variante_producto (id_producto, codigo_barras, talla, color, precio_detalle, precio_mayoreo, costo_promedio)
        VALUES (v_id_prod, '7401202601044', 'Batería 5pz', 'Acero Espejo', 335.0, 285.0, 210.0)
        RETURNING id_variante INTO v_id_var;

        INSERT INTO inventario_sucursal (id_variante, id_sucursal, id_area, stock_actual, stock_minimo, fecha_actualizacion)
        VALUES (v_id_var, 1, 1, 12, 3, NOW());

        INSERT INTO historial_precio (id_variante, id_usuario, precio_anterior, precio_nuevo, fecha_modificacion)
        VALUES (v_id_var, 1, 210.0, 335.0, NOW());
    END IF;
END $$;
DO $$
DECLARE
    v_id_sub INT;
    v_id_uni INT;
    v_id_prod INT;
    v_id_var INT;
BEGIN
    SELECT id_subcategoria INTO v_id_sub FROM subcategoria WHERE nombre = 'Ollas y Baterías de Cocina' LIMIT 1;
    SELECT id_unidad INTO v_id_uni FROM unidad_medida WHERE codigo = 'UND' LIMIT 1;
    IF v_id_uni IS NULL THEN
        SELECT id_unidad INTO v_id_uni FROM unidad_medida WHERE codigo = 'UND' LIMIT 1;
    END IF;

    SELECT id_producto INTO v_id_prod FROM producto WHERE nombre = 'Olla Sopera Alta 10 Litros para Caldos';
    IF v_id_prod IS NULL THEN
        INSERT INTO producto (id_subcategoria, id_unidad, nombre, descripcion, imagen_url, estado, fecha_creacion)
        VALUES (v_id_sub, v_id_uni, 'Olla Sopera Alta 10 Litros para Caldos', 'Olla comercial profunda con remaches dobles reforzados', NULL, 'Activo', NOW())
        RETURNING id_producto INTO v_id_prod;

        INSERT INTO variante_producto (id_producto, codigo_barras, talla, color, precio_detalle, precio_mayoreo, costo_promedio)
        VALUES (v_id_prod, '7401202601045', '10 Litros', 'Plata', 135.0, 115.0, 85.0)
        RETURNING id_variante INTO v_id_var;

        INSERT INTO inventario_sucursal (id_variante, id_sucursal, id_area, stock_actual, stock_minimo, fecha_actualizacion)
        VALUES (v_id_var, 1, 2, 18, 5, NOW());

        INSERT INTO historial_precio (id_variante, id_usuario, precio_anterior, precio_nuevo, fecha_modificacion)
        VALUES (v_id_var, 1, 85.0, 135.0, NOW());
    END IF;
END $$;
DO $$
DECLARE
    v_id_sub INT;
    v_id_uni INT;
    v_id_prod INT;
    v_id_var INT;
BEGIN
    SELECT id_subcategoria INTO v_id_sub FROM subcategoria WHERE nombre = 'Ollas y Baterías de Cocina' LIMIT 1;
    SELECT id_unidad INTO v_id_uni FROM unidad_medida WHERE codigo = 'UND' LIMIT 1;
    IF v_id_uni IS NULL THEN
        SELECT id_unidad INTO v_id_uni FROM unidad_medida WHERE codigo = 'UND' LIMIT 1;
    END IF;

    SELECT id_producto INTO v_id_prod FROM producto WHERE nombre = 'Olla Holandesa de Cerámica Esmaltada 4L';
    IF v_id_prod IS NULL THEN
        INSERT INTO producto (id_subcategoria, id_unidad, nombre, descripcion, imagen_url, estado, fecha_creacion)
        VALUES (v_id_sub, v_id_uni, 'Olla Holandesa de Cerámica Esmaltada 4L', 'Cacerola gruesa de hierro fundido esmaltado ideal para horno', NULL, 'Activo', NOW())
        RETURNING id_producto INTO v_id_prod;

        INSERT INTO variante_producto (id_producto, codigo_barras, talla, color, precio_detalle, precio_mayoreo, costo_promedio)
        VALUES (v_id_prod, '7401202601046', '4 Litros', 'Rojo Cereza', 250.0, 215.0, 160.0)
        RETURNING id_variante INTO v_id_var;

        INSERT INTO inventario_sucursal (id_variante, id_sucursal, id_area, stock_actual, stock_minimo, fecha_actualizacion)
        VALUES (v_id_var, 1, 1, 10, 3, NOW());

        INSERT INTO historial_precio (id_variante, id_usuario, precio_anterior, precio_nuevo, fecha_modificacion)
        VALUES (v_id_var, 1, 160.0, 250.0, NOW());
    END IF;
END $$;
DO $$
DECLARE
    v_id_sub INT;
    v_id_uni INT;
    v_id_prod INT;
    v_id_var INT;
BEGIN
    SELECT id_subcategoria INTO v_id_sub FROM subcategoria WHERE nombre = 'Ollas y Baterías de Cocina' LIMIT 1;
    SELECT id_unidad INTO v_id_uni FROM unidad_medida WHERE codigo = 'UND' LIMIT 1;
    IF v_id_uni IS NULL THEN
        SELECT id_unidad INTO v_id_uni FROM unidad_medida WHERE codigo = 'UND' LIMIT 1;
    END IF;

    SELECT id_producto INTO v_id_prod FROM producto WHERE nombre = 'Olla Sartén Wok Antiadherente 28cm';
    IF v_id_prod IS NULL THEN
        INSERT INTO producto (id_subcategoria, id_unidad, nombre, descripcion, imagen_url, estado, fecha_creacion)
        VALUES (v_id_sub, v_id_uni, 'Olla Sartén Wok Antiadherente 28cm', 'Wok hondo con fondo difusor de calor para salteados', NULL, 'Activo', NOW())
        RETURNING id_producto INTO v_id_prod;

        INSERT INTO variante_producto (id_producto, codigo_barras, talla, color, precio_detalle, precio_mayoreo, costo_promedio)
        VALUES (v_id_prod, '7401202601047', '28cm', 'Negro Granito', 105.0, 88.0, 65.0)
        RETURNING id_variante INTO v_id_var;

        INSERT INTO inventario_sucursal (id_variante, id_sucursal, id_area, stock_actual, stock_minimo, fecha_actualizacion)
        VALUES (v_id_var, 1, 1, 22, 6, NOW());

        INSERT INTO historial_precio (id_variante, id_usuario, precio_anterior, precio_nuevo, fecha_modificacion)
        VALUES (v_id_var, 1, 65.0, 105.0, NOW());
    END IF;
END $$;
DO $$
DECLARE
    v_id_sub INT;
    v_id_uni INT;
    v_id_prod INT;
    v_id_var INT;
BEGIN
    SELECT id_subcategoria INTO v_id_sub FROM subcategoria WHERE nombre = 'Ollas y Baterías de Cocina' LIMIT 1;
    SELECT id_unidad INTO v_id_uni FROM unidad_medida WHERE codigo = 'UND' LIMIT 1;
    IF v_id_uni IS NULL THEN
        SELECT id_unidad INTO v_id_uni FROM unidad_medida WHERE codigo = 'UND' LIMIT 1;
    END IF;

    SELECT id_producto INTO v_id_prod FROM producto WHERE nombre = 'Olla Lechera con Asa Aislante y Pico 2L';
    IF v_id_prod IS NULL THEN
        INSERT INTO producto (id_subcategoria, id_unidad, nombre, descripcion, imagen_url, estado, fecha_creacion)
        VALUES (v_id_sub, v_id_uni, 'Olla Lechera con Asa Aislante y Pico 2L', 'Pocillo lechero de aluminio inoxidable vertedor antigoteo', NULL, 'Activo', NOW())
        RETURNING id_producto INTO v_id_prod;

        INSERT INTO variante_producto (id_producto, codigo_barras, talla, color, precio_detalle, precio_mayoreo, costo_promedio)
        VALUES (v_id_prod, '7401202601048', '2 Litros', 'Acero', 46.0, 38.0, 28.0)
        RETURNING id_variante INTO v_id_var;

        INSERT INTO inventario_sucursal (id_variante, id_sucursal, id_area, stock_actual, stock_minimo, fecha_actualizacion)
        VALUES (v_id_var, 1, 1, 30, 8, NOW());

        INSERT INTO historial_precio (id_variante, id_usuario, precio_anterior, precio_nuevo, fecha_modificacion)
        VALUES (v_id_var, 1, 28.0, 46.0, NOW());
    END IF;
END $$;
DO $$
DECLARE
    v_id_sub INT;
    v_id_uni INT;
    v_id_prod INT;
    v_id_var INT;
BEGIN
    SELECT id_subcategoria INTO v_id_sub FROM subcategoria WHERE nombre = 'Ollas y Baterías de Cocina' LIMIT 1;
    SELECT id_unidad INTO v_id_uni FROM unidad_medida WHERE codigo = 'UND' LIMIT 1;
    IF v_id_uni IS NULL THEN
        SELECT id_unidad INTO v_id_uni FROM unidad_medida WHERE codigo = 'UND' LIMIT 1;
    END IF;

    SELECT id_producto INTO v_id_prod FROM producto WHERE nombre = 'Olla de Barro Curado Tradicional 5 Litros';
    IF v_id_prod IS NULL THEN
        INSERT INTO producto (id_subcategoria, id_unidad, nombre, descripcion, imagen_url, estado, fecha_creacion)
        VALUES (v_id_sub, v_id_uni, 'Olla de Barro Curado Tradicional 5 Litros', 'Olla artesanal curada para frijoles y cocidos típicos', NULL, 'Activo', NOW())
        RETURNING id_producto INTO v_id_prod;

        INSERT INTO variante_producto (id_producto, codigo_barras, talla, color, precio_detalle, precio_mayoreo, costo_promedio)
        VALUES (v_id_prod, '7401202601049', '5 Litros', 'Barro Natural', 75.0, 62.0, 45.0)
        RETURNING id_variante INTO v_id_var;

        INSERT INTO inventario_sucursal (id_variante, id_sucursal, id_area, stock_actual, stock_minimo, fecha_actualizacion)
        VALUES (v_id_var, 1, 2, 20, 5, NOW());

        INSERT INTO historial_precio (id_variante, id_usuario, precio_anterior, precio_nuevo, fecha_modificacion)
        VALUES (v_id_var, 1, 45.0, 75.0, NOW());
    END IF;
END $$;
DO $$
DECLARE
    v_id_sub INT;
    v_id_uni INT;
    v_id_prod INT;
    v_id_var INT;
BEGIN
    SELECT id_subcategoria INTO v_id_sub FROM subcategoria WHERE nombre = 'Ollas y Baterías de Cocina' LIMIT 1;
    SELECT id_unidad INTO v_id_uni FROM unidad_medida WHERE codigo = 'UND' LIMIT 1;
    IF v_id_uni IS NULL THEN
        SELECT id_unidad INTO v_id_uni FROM unidad_medida WHERE codigo = 'UND' LIMIT 1;
    END IF;

    SELECT id_producto INTO v_id_prod FROM producto WHERE nombre = 'Cacerola Olla de Granito con Mango Soft-Touch';
    IF v_id_prod IS NULL THEN
        INSERT INTO producto (id_subcategoria, id_unidad, nombre, descripcion, imagen_url, estado, fecha_creacion)
        VALUES (v_id_sub, v_id_uni, 'Cacerola Olla de Granito con Mango Soft-Touch', 'Olla mediana con revestimiento mineral piedra anti rayones', NULL, 'Activo', NOW())
        RETURNING id_producto INTO v_id_prod;

        INSERT INTO variante_producto (id_producto, codigo_barras, talla, color, precio_detalle, precio_mayoreo, costo_promedio)
        VALUES (v_id_prod, '7401202601050', '20cm / 2.5L', 'Gris Moteado', 89.0, 75.0, 55.0)
        RETURNING id_variante INTO v_id_var;

        INSERT INTO inventario_sucursal (id_variante, id_sucursal, id_area, stock_actual, stock_minimo, fecha_actualizacion)
        VALUES (v_id_var, 1, 1, 24, 6, NOW());

        INSERT INTO historial_precio (id_variante, id_usuario, precio_anterior, precio_nuevo, fecha_modificacion)
        VALUES (v_id_var, 1, 55.0, 89.0, NOW());
    END IF;
END $$;

-- --- Subcatálogo: Platos y Vajillas (10 productos) ---
DO $$
DECLARE
    v_id_sub INT;
    v_id_uni INT;
    v_id_prod INT;
    v_id_var INT;
BEGIN
    SELECT id_subcategoria INTO v_id_sub FROM subcategoria WHERE nombre = 'Platos y Vajillas' LIMIT 1;
    SELECT id_unidad INTO v_id_uni FROM unidad_medida WHERE codigo = 'SET' LIMIT 1;
    IF v_id_uni IS NULL THEN
        SELECT id_unidad INTO v_id_uni FROM unidad_medida WHERE codigo = 'UND' LIMIT 1;
    END IF;

    SELECT id_producto INTO v_id_prod FROM producto WHERE nombre = 'Juego de Platos Tendidos Porcelana Blanca 6pz';
    IF v_id_prod IS NULL THEN
        INSERT INTO producto (id_subcategoria, id_unidad, nombre, descripcion, imagen_url, estado, fecha_creacion)
        VALUES (v_id_sub, v_id_uni, 'Juego de Platos Tendidos Porcelana Blanca 6pz', 'Set de 6 platos extendidos de porcelana lisa para mesa formal', NULL, 'Activo', NOW())
        RETURNING id_producto INTO v_id_prod;

        INSERT INTO variante_producto (id_producto, codigo_barras, talla, color, precio_detalle, precio_mayoreo, costo_promedio)
        VALUES (v_id_prod, '7401202601051', '27cm x 6', 'Blanco', 105.0, 88.0, 65.0)
        RETURNING id_variante INTO v_id_var;

        INSERT INTO inventario_sucursal (id_variante, id_sucursal, id_area, stock_actual, stock_minimo, fecha_actualizacion)
        VALUES (v_id_var, 1, 1, 25, 6, NOW());

        INSERT INTO historial_precio (id_variante, id_usuario, precio_anterior, precio_nuevo, fecha_modificacion)
        VALUES (v_id_var, 1, 65.0, 105.0, NOW());
    END IF;
END $$;
DO $$
DECLARE
    v_id_sub INT;
    v_id_uni INT;
    v_id_prod INT;
    v_id_var INT;
BEGIN
    SELECT id_subcategoria INTO v_id_sub FROM subcategoria WHERE nombre = 'Platos y Vajillas' LIMIT 1;
    SELECT id_unidad INTO v_id_uni FROM unidad_medida WHERE codigo = 'UND' LIMIT 1;
    IF v_id_uni IS NULL THEN
        SELECT id_unidad INTO v_id_uni FROM unidad_medida WHERE codigo = 'UND' LIMIT 1;
    END IF;

    SELECT id_producto INTO v_id_prod FROM producto WHERE nombre = 'Plato Hondo Sencillo para Caldos y Sopas';
    IF v_id_prod IS NULL THEN
        INSERT INTO producto (id_subcategoria, id_unidad, nombre, descripcion, imagen_url, estado, fecha_creacion)
        VALUES (v_id_sub, v_id_uni, 'Plato Hondo Sencillo para Caldos y Sopas', 'Plato hondo hondo de porcelana apto para microondas y lavavajillas', NULL, 'Activo', NOW())
        RETURNING id_producto INTO v_id_prod;

        INSERT INTO variante_producto (id_producto, codigo_barras, talla, color, precio_detalle, precio_mayoreo, costo_promedio)
        VALUES (v_id_prod, '7401202601052', '22cm', 'Blanco', 16.0, 13.0, 9.0)
        RETURNING id_variante INTO v_id_var;

        INSERT INTO inventario_sucursal (id_variante, id_sucursal, id_area, stock_actual, stock_minimo, fecha_actualizacion)
        VALUES (v_id_var, 1, 1, 60, 15, NOW());

        INSERT INTO historial_precio (id_variante, id_usuario, precio_anterior, precio_nuevo, fecha_modificacion)
        VALUES (v_id_var, 1, 9.0, 16.0, NOW());
    END IF;
END $$;
DO $$
DECLARE
    v_id_sub INT;
    v_id_uni INT;
    v_id_prod INT;
    v_id_var INT;
BEGIN
    SELECT id_subcategoria INTO v_id_sub FROM subcategoria WHERE nombre = 'Platos y Vajillas' LIMIT 1;
    SELECT id_unidad INTO v_id_uni FROM unidad_medida WHERE codigo = 'UND' LIMIT 1;
    IF v_id_uni IS NULL THEN
        SELECT id_unidad INTO v_id_uni FROM unidad_medida WHERE codigo = 'UND' LIMIT 1;
    END IF;

    SELECT id_producto INTO v_id_prod FROM producto WHERE nombre = 'Plato Pastelero Cerámica con Filete Dorado';
    IF v_id_prod IS NULL THEN
        INSERT INTO producto (id_subcategoria, id_unidad, nombre, descripcion, imagen_url, estado, fecha_creacion)
        VALUES (v_id_sub, v_id_uni, 'Plato Pastelero Cerámica con Filete Dorado', 'Plato de postre fino con orilla decorada en oro', NULL, 'Activo', NOW())
        RETURNING id_producto INTO v_id_prod;

        INSERT INTO variante_producto (id_producto, codigo_barras, talla, color, precio_detalle, precio_mayoreo, costo_promedio)
        VALUES (v_id_prod, '7401202601053', '19cm', 'Blanco/Oro', 20.0, 16.0, 11.0)
        RETURNING id_variante INTO v_id_var;

        INSERT INTO inventario_sucursal (id_variante, id_sucursal, id_area, stock_actual, stock_minimo, fecha_actualizacion)
        VALUES (v_id_var, 1, 1, 45, 12, NOW());

        INSERT INTO historial_precio (id_variante, id_usuario, precio_anterior, precio_nuevo, fecha_modificacion)
        VALUES (v_id_var, 1, 11.0, 20.0, NOW());
    END IF;
END $$;
DO $$
DECLARE
    v_id_sub INT;
    v_id_uni INT;
    v_id_prod INT;
    v_id_var INT;
BEGIN
    SELECT id_subcategoria INTO v_id_sub FROM subcategoria WHERE nombre = 'Platos y Vajillas' LIMIT 1;
    SELECT id_unidad INTO v_id_uni FROM unidad_medida WHERE codigo = 'UND' LIMIT 1;
    IF v_id_uni IS NULL THEN
        SELECT id_unidad INTO v_id_uni FROM unidad_medida WHERE codigo = 'UND' LIMIT 1;
    END IF;

    SELECT id_producto INTO v_id_prod FROM producto WHERE nombre = 'Plato Base Decorativo de Melamina Labrada 33cm';
    IF v_id_prod IS NULL THEN
        INSERT INTO producto (id_subcategoria, id_unidad, nombre, descripcion, imagen_url, estado, fecha_creacion)
        VALUES (v_id_sub, v_id_uni, 'Plato Base Decorativo de Melamina Labrada 33cm', 'Bajo plato de presentación con relieve barroco para eventos', NULL, 'Activo', NOW())
        RETURNING id_producto INTO v_id_prod;

        INSERT INTO variante_producto (id_producto, codigo_barras, talla, color, precio_detalle, precio_mayoreo, costo_promedio)
        VALUES (v_id_prod, '7401202601054', '33cm', 'Dorado Metálico', 28.0, 23.0, 16.0)
        RETURNING id_variante INTO v_id_var;

        INSERT INTO inventario_sucursal (id_variante, id_sucursal, id_area, stock_actual, stock_minimo, fecha_actualizacion)
        VALUES (v_id_var, 1, 1, 40, 10, NOW());

        INSERT INTO historial_precio (id_variante, id_usuario, precio_anterior, precio_nuevo, fecha_modificacion)
        VALUES (v_id_var, 1, 16.0, 28.0, NOW());
    END IF;
END $$;
DO $$
DECLARE
    v_id_sub INT;
    v_id_uni INT;
    v_id_prod INT;
    v_id_var INT;
BEGIN
    SELECT id_subcategoria INTO v_id_sub FROM subcategoria WHERE nombre = 'Platos y Vajillas' LIMIT 1;
    SELECT id_unidad INTO v_id_uni FROM unidad_medida WHERE codigo = 'UND' LIMIT 1;
    IF v_id_uni IS NULL THEN
        SELECT id_unidad INTO v_id_uni FROM unidad_medida WHERE codigo = 'UND' LIMIT 1;
    END IF;

    SELECT id_producto INTO v_id_prod FROM producto WHERE nombre = 'Plato Botanero Dividido 3 Secciones Cerámica';
    IF v_id_prod IS NULL THEN
        INSERT INTO producto (id_subcategoria, id_unidad, nombre, descripcion, imagen_url, estado, fecha_creacion)
        VALUES (v_id_sub, v_id_uni, 'Plato Botanero Dividido 3 Secciones Cerámica', 'Plato para pasabocas, dips y boquitas con compartimentos', NULL, 'Activo', NOW())
        RETURNING id_producto INTO v_id_prod;

        INSERT INTO variante_producto (id_producto, codigo_barras, talla, color, precio_detalle, precio_mayoreo, costo_promedio)
        VALUES (v_id_prod, '7401202601055', '25x15cm', 'Blanco', 38.0, 30.0, 22.0)
        RETURNING id_variante INTO v_id_var;

        INSERT INTO inventario_sucursal (id_variante, id_sucursal, id_area, stock_actual, stock_minimo, fecha_actualizacion)
        VALUES (v_id_var, 1, 1, 30, 8, NOW());

        INSERT INTO historial_precio (id_variante, id_usuario, precio_anterior, precio_nuevo, fecha_modificacion)
        VALUES (v_id_var, 1, 22.0, 38.0, NOW());
    END IF;
END $$;
DO $$
DECLARE
    v_id_sub INT;
    v_id_uni INT;
    v_id_prod INT;
    v_id_var INT;
BEGIN
    SELECT id_subcategoria INTO v_id_sub FROM subcategoria WHERE nombre = 'Platos y Vajillas' LIMIT 1;
    SELECT id_unidad INTO v_id_uni FROM unidad_medida WHERE codigo = 'UND' LIMIT 1;
    IF v_id_uni IS NULL THEN
        SELECT id_unidad INTO v_id_uni FROM unidad_medida WHERE codigo = 'UND' LIMIT 1;
    END IF;

    SELECT id_producto INTO v_id_prod FROM producto WHERE nombre = 'Plato Infantil Anticaídas con Divisiones y Ventosa';
    IF v_id_prod IS NULL THEN
        INSERT INTO producto (id_subcategoria, id_unidad, nombre, descripcion, imagen_url, estado, fecha_creacion)
        VALUES (v_id_sub, v_id_uni, 'Plato Infantil Anticaídas con Divisiones y Ventosa', 'Plato de silicón grado alimentario con base fijadora antideslizante', NULL, 'Activo', NOW())
        RETURNING id_producto INTO v_id_prod;

        INSERT INTO variante_producto (id_producto, codigo_barras, talla, color, precio_detalle, precio_mayoreo, costo_promedio)
        VALUES (v_id_prod, '7401202601056', 'Infantil', 'Azul/Verde', 42.0, 35.0, 25.0)
        RETURNING id_variante INTO v_id_var;

        INSERT INTO inventario_sucursal (id_variante, id_sucursal, id_area, stock_actual, stock_minimo, fecha_actualizacion)
        VALUES (v_id_var, 1, 1, 28, 6, NOW());

        INSERT INTO historial_precio (id_variante, id_usuario, precio_anterior, precio_nuevo, fecha_modificacion)
        VALUES (v_id_var, 1, 25.0, 42.0, NOW());
    END IF;
END $$;
DO $$
DECLARE
    v_id_sub INT;
    v_id_uni INT;
    v_id_prod INT;
    v_id_var INT;
BEGIN
    SELECT id_subcategoria INTO v_id_sub FROM subcategoria WHERE nombre = 'Platos y Vajillas' LIMIT 1;
    SELECT id_unidad INTO v_id_uni FROM unidad_medida WHERE codigo = 'SET' LIMIT 1;
    IF v_id_uni IS NULL THEN
        SELECT id_unidad INTO v_id_uni FROM unidad_medida WHERE codigo = 'UND' LIMIT 1;
    END IF;

    SELECT id_producto INTO v_id_prod FROM producto WHERE nombre = 'Plato Trinche Melamina Comercial Pack x6';
    IF v_id_prod IS NULL THEN
        INSERT INTO producto (id_subcategoria, id_unidad, nombre, descripcion, imagen_url, estado, fecha_creacion)
        VALUES (v_id_sub, v_id_uni, 'Plato Trinche Melamina Comercial Pack x6', 'Platos irrompibles de alta resistencia para comedor y restaurante', NULL, 'Activo', NOW())
        RETURNING id_producto INTO v_id_prod;

        INSERT INTO variante_producto (id_producto, codigo_barras, talla, color, precio_detalle, precio_mayoreo, costo_promedio)
        VALUES (v_id_prod, '7401202601057', 'Pack 6pz', 'Blanco', 70.0, 58.0, 42.0)
        RETURNING id_variante INTO v_id_var;

        INSERT INTO inventario_sucursal (id_variante, id_sucursal, id_area, stock_actual, stock_minimo, fecha_actualizacion)
        VALUES (v_id_var, 1, 2, 35, 10, NOW());

        INSERT INTO historial_precio (id_variante, id_usuario, precio_anterior, precio_nuevo, fecha_modificacion)
        VALUES (v_id_var, 1, 42.0, 70.0, NOW());
    END IF;
END $$;
DO $$
DECLARE
    v_id_sub INT;
    v_id_uni INT;
    v_id_prod INT;
    v_id_var INT;
BEGIN
    SELECT id_subcategoria INTO v_id_sub FROM subcategoria WHERE nombre = 'Platos y Vajillas' LIMIT 1;
    SELECT id_unidad INTO v_id_uni FROM unidad_medida WHERE codigo = 'UND' LIMIT 1;
    IF v_id_uni IS NULL THEN
        SELECT id_unidad INTO v_id_uni FROM unidad_medida WHERE codigo = 'UND' LIMIT 1;
    END IF;

    SELECT id_producto INTO v_id_prod FROM producto WHERE nombre = 'Bandeja Plato de Servir Ovalado Porcelana 36cm';
    IF v_id_prod IS NULL THEN
        INSERT INTO producto (id_subcategoria, id_unidad, nombre, descripcion, imagen_url, estado, fecha_creacion)
        VALUES (v_id_sub, v_id_uni, 'Bandeja Plato de Servir Ovalado Porcelana 36cm', 'Fuente amplia para servir carnes, asados y ensaladas', NULL, 'Activo', NOW())
        RETURNING id_producto INTO v_id_prod;

        INSERT INTO variante_producto (id_producto, codigo_barras, talla, color, precio_detalle, precio_mayoreo, costo_promedio)
        VALUES (v_id_prod, '7401202601058', '36x24cm', 'Blanco', 52.0, 42.0, 30.0)
        RETURNING id_variante INTO v_id_var;

        INSERT INTO inventario_sucursal (id_variante, id_sucursal, id_area, stock_actual, stock_minimo, fecha_actualizacion)
        VALUES (v_id_var, 1, 1, 20, 5, NOW());

        INSERT INTO historial_precio (id_variante, id_usuario, precio_anterior, precio_nuevo, fecha_modificacion)
        VALUES (v_id_var, 1, 30.0, 52.0, NOW());
    END IF;
END $$;
DO $$
DECLARE
    v_id_sub INT;
    v_id_uni INT;
    v_id_prod INT;
    v_id_var INT;
BEGIN
    SELECT id_subcategoria INTO v_id_sub FROM subcategoria WHERE nombre = 'Platos y Vajillas' LIMIT 1;
    SELECT id_unidad INTO v_id_uni FROM unidad_medida WHERE codigo = 'UND' LIMIT 1;
    IF v_id_uni IS NULL THEN
        SELECT id_unidad INTO v_id_uni FROM unidad_medida WHERE codigo = 'UND' LIMIT 1;
    END IF;

    SELECT id_producto INTO v_id_prod FROM producto WHERE nombre = 'Plato Tendido Cuadrado Cerámica Contemporánea';
    IF v_id_prod IS NULL THEN
        INSERT INTO producto (id_subcategoria, id_unidad, nombre, descripcion, imagen_url, estado, fecha_creacion)
        VALUES (v_id_sub, v_id_uni, 'Plato Tendido Cuadrado Cerámica Contemporánea', 'Plato moderno con bordes rectos acabado negro mate', NULL, 'Activo', NOW())
        RETURNING id_producto INTO v_id_prod;

        INSERT INTO variante_producto (id_producto, codigo_barras, talla, color, precio_detalle, precio_mayoreo, costo_promedio)
        VALUES (v_id_prod, '7401202601059', '25x25cm', 'Negro Mate', 27.0, 22.0, 15.0)
        RETURNING id_variante INTO v_id_var;

        INSERT INTO inventario_sucursal (id_variante, id_sucursal, id_area, stock_actual, stock_minimo, fecha_actualizacion)
        VALUES (v_id_var, 1, 1, 35, 8, NOW());

        INSERT INTO historial_precio (id_variante, id_usuario, precio_anterior, precio_nuevo, fecha_modificacion)
        VALUES (v_id_var, 1, 15.0, 27.0, NOW());
    END IF;
END $$;
DO $$
DECLARE
    v_id_sub INT;
    v_id_uni INT;
    v_id_prod INT;
    v_id_var INT;
BEGIN
    SELECT id_subcategoria INTO v_id_sub FROM subcategoria WHERE nombre = 'Platos y Vajillas' LIMIT 1;
    SELECT id_unidad INTO v_id_uni FROM unidad_medida WHERE codigo = 'UND' LIMIT 1;
    IF v_id_uni IS NULL THEN
        SELECT id_unidad INTO v_id_uni FROM unidad_medida WHERE codigo = 'UND' LIMIT 1;
    END IF;

    SELECT id_producto INTO v_id_prod FROM producto WHERE nombre = 'Plato Hondo Artesanal de Barro Vidriado';
    IF v_id_prod IS NULL THEN
        INSERT INTO producto (id_subcategoria, id_unidad, nombre, descripcion, imagen_url, estado, fecha_creacion)
        VALUES (v_id_sub, v_id_uni, 'Plato Hondo Artesanal de Barro Vidriado', 'Plato rústico esmaltado libre de plomo para comida guatemalteca', NULL, 'Activo', NOW())
        RETURNING id_producto INTO v_id_prod;

        INSERT INTO variante_producto (id_producto, codigo_barras, talla, color, precio_detalle, precio_mayoreo, costo_promedio)
        VALUES (v_id_prod, '7401202601060', '20cm', 'Café Típico', 22.0, 17.0, 12.0)
        RETURNING id_variante INTO v_id_var;

        INSERT INTO inventario_sucursal (id_variante, id_sucursal, id_area, stock_actual, stock_minimo, fecha_actualizacion)
        VALUES (v_id_var, 1, 2, 40, 10, NOW());

        INSERT INTO historial_precio (id_variante, id_usuario, precio_anterior, precio_nuevo, fecha_modificacion)
        VALUES (v_id_var, 1, 12.0, 22.0, NOW());
    END IF;
END $$;

-- --- Subcatálogo: Chamarras y Abrigos (10 productos) ---
DO $$
DECLARE
    v_id_sub INT;
    v_id_uni INT;
    v_id_prod INT;
    v_id_var INT;
BEGIN
    SELECT id_subcategoria INTO v_id_sub FROM subcategoria WHERE nombre = 'Chamarras y Abrigos' LIMIT 1;
    SELECT id_unidad INTO v_id_uni FROM unidad_medida WHERE codigo = 'UND' LIMIT 1;
    IF v_id_uni IS NULL THEN
        SELECT id_unidad INTO v_id_uni FROM unidad_medida WHERE codigo = 'UND' LIMIT 1;
    END IF;

    SELECT id_producto INTO v_id_prod FROM producto WHERE nombre = 'Chamarra Rompevientos Impermeable con Capucha';
    IF v_id_prod IS NULL THEN
        INSERT INTO producto (id_subcategoria, id_unidad, nombre, descripcion, imagen_url, estado, fecha_creacion)
        VALUES (v_id_sub, v_id_uni, 'Chamarra Rompevientos Impermeable con Capucha', 'Chamarra ligera repelente al agua y viento con forro transpirable', NULL, 'Activo', NOW())
        RETURNING id_producto INTO v_id_prod;

        INSERT INTO variante_producto (id_producto, codigo_barras, talla, color, precio_detalle, precio_mayoreo, costo_promedio)
        VALUES (v_id_prod, '7401202601061', 'M', 'Azul Marino', 155.0, 130.0, 95.0)
        RETURNING id_variante INTO v_id_var;

        INSERT INTO inventario_sucursal (id_variante, id_sucursal, id_area, stock_actual, stock_minimo, fecha_actualizacion)
        VALUES (v_id_var, 1, 1, 24, 6, NOW());

        INSERT INTO historial_precio (id_variante, id_usuario, precio_anterior, precio_nuevo, fecha_modificacion)
        VALUES (v_id_var, 1, 95.0, 155.0, NOW());
    END IF;
END $$;
DO $$
DECLARE
    v_id_sub INT;
    v_id_uni INT;
    v_id_prod INT;
    v_id_var INT;
BEGIN
    SELECT id_subcategoria INTO v_id_sub FROM subcategoria WHERE nombre = 'Chamarras y Abrigos' LIMIT 1;
    SELECT id_unidad INTO v_id_uni FROM unidad_medida WHERE codigo = 'UND' LIMIT 1;
    IF v_id_uni IS NULL THEN
        SELECT id_unidad INTO v_id_uni FROM unidad_medida WHERE codigo = 'UND' LIMIT 1;
    END IF;

    SELECT id_producto INTO v_id_prod FROM producto WHERE nombre = 'Chamarra Térmica de Pluma Sintética Acolchada';
    IF v_id_prod IS NULL THEN
        INSERT INTO producto (id_subcategoria, id_unidad, nombre, descripcion, imagen_url, estado, fecha_creacion)
        VALUES (v_id_sub, v_id_uni, 'Chamarra Térmica de Pluma Sintética Acolchada', 'Chamarra acolchada ultraliviana para bajas temperaturas', NULL, 'Activo', NOW())
        RETURNING id_producto INTO v_id_prod;

        INSERT INTO variante_producto (id_producto, codigo_barras, talla, color, precio_detalle, precio_mayoreo, costo_promedio)
        VALUES (v_id_prod, '7401202601062', 'L', 'Negro', 210.0, 175.0, 130.0)
        RETURNING id_variante INTO v_id_var;

        INSERT INTO inventario_sucursal (id_variante, id_sucursal, id_area, stock_actual, stock_minimo, fecha_actualizacion)
        VALUES (v_id_var, 1, 1, 20, 5, NOW());

        INSERT INTO historial_precio (id_variante, id_usuario, precio_anterior, precio_nuevo, fecha_modificacion)
        VALUES (v_id_var, 1, 130.0, 210.0, NOW());
    END IF;
END $$;
DO $$
DECLARE
    v_id_sub INT;
    v_id_uni INT;
    v_id_prod INT;
    v_id_var INT;
BEGIN
    SELECT id_subcategoria INTO v_id_sub FROM subcategoria WHERE nombre = 'Chamarras y Abrigos' LIMIT 1;
    SELECT id_unidad INTO v_id_uni FROM unidad_medida WHERE codigo = 'UND' LIMIT 1;
    IF v_id_uni IS NULL THEN
        SELECT id_unidad INTO v_id_uni FROM unidad_medida WHERE codigo = 'UND' LIMIT 1;
    END IF;

    SELECT id_producto INTO v_id_prod FROM producto WHERE nombre = 'Chamarra Biker Cuero Sintético Unisex';
    IF v_id_prod IS NULL THEN
        INSERT INTO producto (id_subcategoria, id_unidad, nombre, descripcion, imagen_url, estado, fecha_creacion)
        VALUES (v_id_sub, v_id_uni, 'Chamarra Biker Cuero Sintético Unisex', 'Chamarra moderna estilo motociclista con broches y zipper', NULL, 'Activo', NOW())
        RETURNING id_producto INTO v_id_prod;

        INSERT INTO variante_producto (id_producto, codigo_barras, talla, color, precio_detalle, precio_mayoreo, costo_promedio)
        VALUES (v_id_prod, '7401202601063', 'M', 'Café Oscuro', 230.0, 190.0, 140.0)
        RETURNING id_variante INTO v_id_var;

        INSERT INTO inventario_sucursal (id_variante, id_sucursal, id_area, stock_actual, stock_minimo, fecha_actualizacion)
        VALUES (v_id_var, 1, 1, 18, 4, NOW());

        INSERT INTO historial_precio (id_variante, id_usuario, precio_anterior, precio_nuevo, fecha_modificacion)
        VALUES (v_id_var, 1, 140.0, 230.0, NOW());
    END IF;
END $$;
DO $$
DECLARE
    v_id_sub INT;
    v_id_uni INT;
    v_id_prod INT;
    v_id_var INT;
BEGIN
    SELECT id_subcategoria INTO v_id_sub FROM subcategoria WHERE nombre = 'Chamarras y Abrigos' LIMIT 1;
    SELECT id_unidad INTO v_id_uni FROM unidad_medida WHERE codigo = 'UND' LIMIT 1;
    IF v_id_uni IS NULL THEN
        SELECT id_unidad INTO v_id_uni FROM unidad_medida WHERE codigo = 'UND' LIMIT 1;
    END IF;

    SELECT id_producto INTO v_id_prod FROM producto WHERE nombre = 'Chamarra Deportiva Casual con Zipper Completo';
    IF v_id_prod IS NULL THEN
        INSERT INTO producto (id_subcategoria, id_unidad, nombre, descripcion, imagen_url, estado, fecha_creacion)
        VALUES (v_id_sub, v_id_uni, 'Chamarra Deportiva Casual con Zipper Completo', 'Chamarra de algodón perchado con puños y cintura elástica', NULL, 'Activo', NOW())
        RETURNING id_producto INTO v_id_prod;

        INSERT INTO variante_producto (id_producto, codigo_barras, talla, color, precio_detalle, precio_mayoreo, costo_promedio)
        VALUES (v_id_prod, '7401202601064', 'L', 'Gris Jaspe', 125.0, 105.0, 78.0)
        RETURNING id_variante INTO v_id_var;

        INSERT INTO inventario_sucursal (id_variante, id_sucursal, id_area, stock_actual, stock_minimo, fecha_actualizacion)
        VALUES (v_id_var, 1, 1, 25, 6, NOW());

        INSERT INTO historial_precio (id_variante, id_usuario, precio_anterior, precio_nuevo, fecha_modificacion)
        VALUES (v_id_var, 1, 78.0, 125.0, NOW());
    END IF;
END $$;
DO $$
DECLARE
    v_id_sub INT;
    v_id_uni INT;
    v_id_prod INT;
    v_id_var INT;
BEGIN
    SELECT id_subcategoria INTO v_id_sub FROM subcategoria WHERE nombre = 'Chamarras y Abrigos' LIMIT 1;
    SELECT id_unidad INTO v_id_uni FROM unidad_medida WHERE codigo = 'UND' LIMIT 1;
    IF v_id_uni IS NULL THEN
        SELECT id_unidad INTO v_id_uni FROM unidad_medida WHERE codigo = 'UND' LIMIT 1;
    END IF;

    SELECT id_producto INTO v_id_prod FROM producto WHERE nombre = 'Chamarra de Mezclilla Denim Tradicional Unisex';
    IF v_id_prod IS NULL THEN
        INSERT INTO producto (id_subcategoria, id_unidad, nombre, descripcion, imagen_url, estado, fecha_creacion)
        VALUES (v_id_sub, v_id_uni, 'Chamarra de Mezclilla Denim Tradicional Unisex', 'Chamarra de lona jeans resistente con botones metálicos', NULL, 'Activo', NOW())
        RETURNING id_producto INTO v_id_prod;

        INSERT INTO variante_producto (id_producto, codigo_barras, talla, color, precio_detalle, precio_mayoreo, costo_promedio)
        VALUES (v_id_prod, '7401202601065', 'M', 'Azul Clásico', 180.0, 150.0, 110.0)
        RETURNING id_variante INTO v_id_var;

        INSERT INTO inventario_sucursal (id_variante, id_sucursal, id_area, stock_actual, stock_minimo, fecha_actualizacion)
        VALUES (v_id_var, 1, 1, 22, 5, NOW());

        INSERT INTO historial_precio (id_variante, id_usuario, precio_anterior, precio_nuevo, fecha_modificacion)
        VALUES (v_id_var, 1, 110.0, 180.0, NOW());
    END IF;
END $$;
DO $$
DECLARE
    v_id_sub INT;
    v_id_uni INT;
    v_id_prod INT;
    v_id_var INT;
BEGIN
    SELECT id_subcategoria INTO v_id_sub FROM subcategoria WHERE nombre = 'Chamarras y Abrigos' LIMIT 1;
    SELECT id_unidad INTO v_id_uni FROM unidad_medida WHERE codigo = 'UND' LIMIT 1;
    IF v_id_uni IS NULL THEN
        SELECT id_unidad INTO v_id_uni FROM unidad_medida WHERE codigo = 'UND' LIMIT 1;
    END IF;

    SELECT id_producto INTO v_id_prod FROM producto WHERE nombre = 'Chamarra Polar Térmica Cuello Alto para Frío';
    IF v_id_prod IS NULL THEN
        INSERT INTO producto (id_subcategoria, id_unidad, nombre, descripcion, imagen_url, estado, fecha_creacion)
        VALUES (v_id_sub, v_id_uni, 'Chamarra Polar Térmica Cuello Alto para Frío', 'Chamarra de microfleece suave antipilling con bolsillos', NULL, 'Activo', NOW())
        RETURNING id_producto INTO v_id_prod;

        INSERT INTO variante_producto (id_producto, codigo_barras, talla, color, precio_detalle, precio_mayoreo, costo_promedio)
        VALUES (v_id_prod, '7401202601066', 'S', 'Vino Tinto', 110.0, 90.0, 65.0)
        RETURNING id_variante INTO v_id_var;

        INSERT INTO inventario_sucursal (id_variante, id_sucursal, id_area, stock_actual, stock_minimo, fecha_actualizacion)
        VALUES (v_id_var, 1, 1, 28, 7, NOW());

        INSERT INTO historial_precio (id_variante, id_usuario, precio_anterior, precio_nuevo, fecha_modificacion)
        VALUES (v_id_var, 1, 65.0, 110.0, NOW());
    END IF;
END $$;
DO $$
DECLARE
    v_id_sub INT;
    v_id_uni INT;
    v_id_prod INT;
    v_id_var INT;
BEGIN
    SELECT id_subcategoria INTO v_id_sub FROM subcategoria WHERE nombre = 'Chamarras y Abrigos' LIMIT 1;
    SELECT id_unidad INTO v_id_uni FROM unidad_medida WHERE codigo = 'UND' LIMIT 1;
    IF v_id_uni IS NULL THEN
        SELECT id_unidad INTO v_id_uni FROM unidad_medida WHERE codigo = 'UND' LIMIT 1;
    END IF;

    SELECT id_producto INTO v_id_prod FROM producto WHERE nombre = 'Chamarra Infantil Acolchada con Gorro de Orejitas';
    IF v_id_prod IS NULL THEN
        INSERT INTO producto (id_subcategoria, id_unidad, nombre, descripcion, imagen_url, estado, fecha_creacion)
        VALUES (v_id_sub, v_id_uni, 'Chamarra Infantil Acolchada con Gorro de Orejitas', 'Abrigo tierno para niños con forro suave antialérgico', NULL, 'Activo', NOW())
        RETURNING id_producto INTO v_id_prod;

        INSERT INTO variante_producto (id_producto, codigo_barras, talla, color, precio_detalle, precio_mayoreo, costo_promedio)
        VALUES (v_id_prod, '7401202601067', 'Talla 6', 'Amarillo Mostaza', 118.0, 98.0, 70.0)
        RETURNING id_variante INTO v_id_var;

        INSERT INTO inventario_sucursal (id_variante, id_sucursal, id_area, stock_actual, stock_minimo, fecha_actualizacion)
        VALUES (v_id_var, 1, 1, 20, 5, NOW());

        INSERT INTO historial_precio (id_variante, id_usuario, precio_anterior, precio_nuevo, fecha_modificacion)
        VALUES (v_id_var, 1, 70.0, 118.0, NOW());
    END IF;
END $$;
DO $$
DECLARE
    v_id_sub INT;
    v_id_uni INT;
    v_id_prod INT;
    v_id_var INT;
BEGIN
    SELECT id_subcategoria INTO v_id_sub FROM subcategoria WHERE nombre = 'Chamarras y Abrigos' LIMIT 1;
    SELECT id_unidad INTO v_id_uni FROM unidad_medida WHERE codigo = 'UND' LIMIT 1;
    IF v_id_uni IS NULL THEN
        SELECT id_unidad INTO v_id_uni FROM unidad_medida WHERE codigo = 'UND' LIMIT 1;
    END IF;

    SELECT id_producto INTO v_id_prod FROM producto WHERE nombre = 'Chaleco Chamarra Acolchado sin Mangas';
    IF v_id_prod IS NULL THEN
        INSERT INTO producto (id_subcategoria, id_unidad, nombre, descripcion, imagen_url, estado, fecha_creacion)
        VALUES (v_id_sub, v_id_uni, 'Chaleco Chamarra Acolchado sin Mangas', 'Chaleco abrigador repelente al agua para movilidad cómoda', NULL, 'Activo', NOW())
        RETURNING id_producto INTO v_id_prod;

        INSERT INTO variante_producto (id_producto, codigo_barras, talla, color, precio_detalle, precio_mayoreo, costo_promedio)
        VALUES (v_id_prod, '7401202601068', 'XL', 'Azul Petróleo', 125.0, 105.0, 75.0)
        RETURNING id_variante INTO v_id_var;

        INSERT INTO inventario_sucursal (id_variante, id_sucursal, id_area, stock_actual, stock_minimo, fecha_actualizacion)
        VALUES (v_id_var, 1, 1, 22, 6, NOW());

        INSERT INTO historial_precio (id_variante, id_usuario, precio_anterior, precio_nuevo, fecha_modificacion)
        VALUES (v_id_var, 1, 75.0, 125.0, NOW());
    END IF;
END $$;
DO $$
DECLARE
    v_id_sub INT;
    v_id_uni INT;
    v_id_prod INT;
    v_id_var INT;
BEGIN
    SELECT id_subcategoria INTO v_id_sub FROM subcategoria WHERE nombre = 'Chamarras y Abrigos' LIMIT 1;
    SELECT id_unidad INTO v_id_uni FROM unidad_medida WHERE codigo = 'UND' LIMIT 1;
    IF v_id_uni IS NULL THEN
        SELECT id_unidad INTO v_id_uni FROM unidad_medida WHERE codigo = 'UND' LIMIT 1;
    END IF;

    SELECT id_producto INTO v_id_prod FROM producto WHERE nombre = 'Chamarra Parka Larga con Forro de Borrego';
    IF v_id_prod IS NULL THEN
        INSERT INTO producto (id_subcategoria, id_unidad, nombre, descripcion, imagen_url, estado, fecha_creacion)
        VALUES (v_id_sub, v_id_uni, 'Chamarra Parka Larga con Forro de Borrego', 'Parka larga con forro afelpado interior para clima frío', NULL, 'Activo', NOW())
        RETURNING id_producto INTO v_id_prod;

        INSERT INTO variante_producto (id_producto, codigo_barras, talla, color, precio_detalle, precio_mayoreo, costo_promedio)
        VALUES (v_id_prod, '7401202601069', 'L', 'Verde Militar', 265.0, 225.0, 165.0)
        RETURNING id_variante INTO v_id_var;

        INSERT INTO inventario_sucursal (id_variante, id_sucursal, id_area, stock_actual, stock_minimo, fecha_actualizacion)
        VALUES (v_id_var, 1, 1, 15, 4, NOW());

        INSERT INTO historial_precio (id_variante, id_usuario, precio_anterior, precio_nuevo, fecha_modificacion)
        VALUES (v_id_var, 1, 165.0, 265.0, NOW());
    END IF;
END $$;
DO $$
DECLARE
    v_id_sub INT;
    v_id_uni INT;
    v_id_prod INT;
    v_id_var INT;
BEGIN
    SELECT id_subcategoria INTO v_id_sub FROM subcategoria WHERE nombre = 'Chamarras y Abrigos' LIMIT 1;
    SELECT id_unidad INTO v_id_uni FROM unidad_medida WHERE codigo = 'UND' LIMIT 1;
    IF v_id_uni IS NULL THEN
        SELECT id_unidad INTO v_id_uni FROM unidad_medida WHERE codigo = 'UND' LIMIT 1;
    END IF;

    SELECT id_producto INTO v_id_prod FROM producto WHERE nombre = 'Chamarra Suéter de Lana con Forro Interior';
    IF v_id_prod IS NULL THEN
        INSERT INTO producto (id_subcategoria, id_unidad, nombre, descripcion, imagen_url, estado, fecha_creacion)
        VALUES (v_id_sub, v_id_uni, 'Chamarra Suéter de Lana con Forro Interior', 'Prenda de lana tejida artesanal con botones de madera', NULL, 'Activo', NOW())
        RETURNING id_producto INTO v_id_prod;

        INSERT INTO variante_producto (id_producto, codigo_barras, talla, color, precio_detalle, precio_mayoreo, costo_promedio)
        VALUES (v_id_prod, '7401202601070', 'M', 'Gris/Blanco', 175.0, 145.0, 105.0)
        RETURNING id_variante INTO v_id_var;

        INSERT INTO inventario_sucursal (id_variante, id_sucursal, id_area, stock_actual, stock_minimo, fecha_actualizacion)
        VALUES (v_id_var, 1, 1, 20, 5, NOW());

        INSERT INTO historial_precio (id_variante, id_usuario, precio_anterior, precio_nuevo, fecha_modificacion)
        VALUES (v_id_var, 1, 105.0, 175.0, NOW());
    END IF;
END $$;

-- --- Subcatálogo: Desodorantes e Higiene Corporal (10 productos) ---
DO $$
DECLARE
    v_id_sub INT;
    v_id_uni INT;
    v_id_prod INT;
    v_id_var INT;
BEGIN
    SELECT id_subcategoria INTO v_id_sub FROM subcategoria WHERE nombre = 'Desodorantes e Higiene Corporal' LIMIT 1;
    SELECT id_unidad INTO v_id_uni FROM unidad_medida WHERE codigo = 'UND' LIMIT 1;
    IF v_id_uni IS NULL THEN
        SELECT id_unidad INTO v_id_uni FROM unidad_medida WHERE codigo = 'UND' LIMIT 1;
    END IF;

    SELECT id_producto INTO v_id_prod FROM producto WHERE nombre = 'Desodorante Antitranspirante Roll-On Clásico 50ml';
    IF v_id_prod IS NULL THEN
        INSERT INTO producto (id_subcategoria, id_unidad, nombre, descripcion, imagen_url, estado, fecha_creacion)
        VALUES (v_id_sub, v_id_uni, 'Desodorante Antitranspirante Roll-On Clásico 50ml', 'Protección contra sudor y mal olor durante 24 horas', NULL, 'Activo', NOW())
        RETURNING id_producto INTO v_id_prod;

        INSERT INTO variante_producto (id_producto, codigo_barras, talla, color, precio_detalle, precio_mayoreo, costo_promedio)
        VALUES (v_id_prod, '7401202601071', '50ml', 'Blanco', 20.0, 16.0, 11.5)
        RETURNING id_variante INTO v_id_var;

        INSERT INTO inventario_sucursal (id_variante, id_sucursal, id_area, stock_actual, stock_minimo, fecha_actualizacion)
        VALUES (v_id_var, 1, 3, 50, 15, NOW());

        INSERT INTO historial_precio (id_variante, id_usuario, precio_anterior, precio_nuevo, fecha_modificacion)
        VALUES (v_id_var, 1, 11.5, 20.0, NOW());
    END IF;
END $$;
DO $$
DECLARE
    v_id_sub INT;
    v_id_uni INT;
    v_id_prod INT;
    v_id_var INT;
BEGIN
    SELECT id_subcategoria INTO v_id_sub FROM subcategoria WHERE nombre = 'Desodorantes e Higiene Corporal' LIMIT 1;
    SELECT id_unidad INTO v_id_uni FROM unidad_medida WHERE codigo = 'UND' LIMIT 1;
    IF v_id_uni IS NULL THEN
        SELECT id_unidad INTO v_id_uni FROM unidad_medida WHERE codigo = 'UND' LIMIT 1;
    END IF;

    SELECT id_producto INTO v_id_prod FROM producto WHERE nombre = 'Desodorante en Aerosol Protección Seca 150ml';
    IF v_id_prod IS NULL THEN
        INSERT INTO producto (id_subcategoria, id_unidad, nombre, descripcion, imagen_url, estado, fecha_creacion)
        VALUES (v_id_sub, v_id_uni, 'Desodorante en Aerosol Protección Seca 150ml', 'Spray seco sin residuos blancos fragancia fresca', NULL, 'Activo', NOW())
        RETURNING id_producto INTO v_id_prod;

        INSERT INTO variante_producto (id_producto, codigo_barras, talla, color, precio_detalle, precio_mayoreo, costo_promedio)
        VALUES (v_id_prod, '7401202601072', '150ml', 'Azul', 30.0, 25.0, 18.0)
        RETURNING id_variante INTO v_id_var;

        INSERT INTO inventario_sucursal (id_variante, id_sucursal, id_area, stock_actual, stock_minimo, fecha_actualizacion)
        VALUES (v_id_var, 1, 1, 45, 12, NOW());

        INSERT INTO historial_precio (id_variante, id_usuario, precio_anterior, precio_nuevo, fecha_modificacion)
        VALUES (v_id_var, 1, 18.0, 30.0, NOW());
    END IF;
END $$;
DO $$
DECLARE
    v_id_sub INT;
    v_id_uni INT;
    v_id_prod INT;
    v_id_var INT;
BEGIN
    SELECT id_subcategoria INTO v_id_sub FROM subcategoria WHERE nombre = 'Desodorantes e Higiene Corporal' LIMIT 1;
    SELECT id_unidad INTO v_id_uni FROM unidad_medida WHERE codigo = 'UND' LIMIT 1;
    IF v_id_uni IS NULL THEN
        SELECT id_unidad INTO v_id_uni FROM unidad_medida WHERE codigo = 'UND' LIMIT 1;
    END IF;

    SELECT id_producto INTO v_id_prod FROM producto WHERE nombre = 'Desodorante en Barra Sport Duración 48h';
    IF v_id_prod IS NULL THEN
        INSERT INTO producto (id_subcategoria, id_unidad, nombre, descripcion, imagen_url, estado, fecha_creacion)
        VALUES (v_id_sub, v_id_uni, 'Desodorante en Barra Sport Duración 48h', 'Barra sólida masculina para deportistas máxima protección', NULL, 'Activo', NOW())
        RETURNING id_producto INTO v_id_prod;

        INSERT INTO variante_producto (id_producto, codigo_barras, talla, color, precio_detalle, precio_mayoreo, costo_promedio)
        VALUES (v_id_prod, '7401202601073', '85g', 'Verde Sport', 28.0, 23.0, 16.5)
        RETURNING id_variante INTO v_id_var;

        INSERT INTO inventario_sucursal (id_variante, id_sucursal, id_area, stock_actual, stock_minimo, fecha_actualizacion)
        VALUES (v_id_var, 1, 1, 40, 10, NOW());

        INSERT INTO historial_precio (id_variante, id_usuario, precio_anterior, precio_nuevo, fecha_modificacion)
        VALUES (v_id_var, 1, 16.5, 28.0, NOW());
    END IF;
END $$;
DO $$
DECLARE
    v_id_sub INT;
    v_id_uni INT;
    v_id_prod INT;
    v_id_var INT;
BEGIN
    SELECT id_subcategoria INTO v_id_sub FROM subcategoria WHERE nombre = 'Desodorantes e Higiene Corporal' LIMIT 1;
    SELECT id_unidad INTO v_id_uni FROM unidad_medida WHERE codigo = 'UND' LIMIT 1;
    IF v_id_uni IS NULL THEN
        SELECT id_unidad INTO v_id_uni FROM unidad_medida WHERE codigo = 'UND' LIMIT 1;
    END IF;

    SELECT id_producto INTO v_id_prod FROM producto WHERE nombre = 'Desodorante Natural Piedra de Alumbre 120g';
    IF v_id_prod IS NULL THEN
        INSERT INTO producto (id_subcategoria, id_unidad, nombre, descripcion, imagen_url, estado, fecha_creacion)
        VALUES (v_id_sub, v_id_uni, 'Desodorante Natural Piedra de Alumbre 120g', 'Cristal mineral 100% natural antibacterial sin químicos', NULL, 'Activo', NOW())
        RETURNING id_producto INTO v_id_prod;

        INSERT INTO variante_producto (id_producto, codigo_barras, talla, color, precio_detalle, precio_mayoreo, costo_promedio)
        VALUES (v_id_prod, '7401202601074', '120g', 'Transparente', 35.0, 27.0, 19.0)
        RETURNING id_variante INTO v_id_var;

        INSERT INTO inventario_sucursal (id_variante, id_sucursal, id_area, stock_actual, stock_minimo, fecha_actualizacion)
        VALUES (v_id_var, 1, 1, 35, 10, NOW());

        INSERT INTO historial_precio (id_variante, id_usuario, precio_anterior, precio_nuevo, fecha_modificacion)
        VALUES (v_id_var, 1, 19.0, 35.0, NOW());
    END IF;
END $$;
DO $$
DECLARE
    v_id_sub INT;
    v_id_uni INT;
    v_id_prod INT;
    v_id_var INT;
BEGIN
    SELECT id_subcategoria INTO v_id_sub FROM subcategoria WHERE nombre = 'Desodorantes e Higiene Corporal' LIMIT 1;
    SELECT id_unidad INTO v_id_uni FROM unidad_medida WHERE codigo = 'UND' LIMIT 1;
    IF v_id_uni IS NULL THEN
        SELECT id_unidad INTO v_id_uni FROM unidad_medida WHERE codigo = 'UND' LIMIT 1;
    END IF;

    SELECT id_producto INTO v_id_prod FROM producto WHERE nombre = 'Desodorante Roll-On Aclarador y Suavizante 50ml';
    IF v_id_prod IS NULL THEN
        INSERT INTO producto (id_subcategoria, id_unidad, nombre, descripcion, imagen_url, estado, fecha_creacion)
        VALUES (v_id_sub, v_id_uni, 'Desodorante Roll-On Aclarador y Suavizante 50ml', 'Fórmula con perla hidrolizada que unifica el tono de piel', NULL, 'Activo', NOW())
        RETURNING id_producto INTO v_id_prod;

        INSERT INTO variante_producto (id_producto, codigo_barras, talla, color, precio_detalle, precio_mayoreo, costo_promedio)
        VALUES (v_id_prod, '7401202601075', '50ml', 'Rosa', 22.0, 18.0, 13.0)
        RETURNING id_variante INTO v_id_var;

        INSERT INTO inventario_sucursal (id_variante, id_sucursal, id_area, stock_actual, stock_minimo, fecha_actualizacion)
        VALUES (v_id_var, 1, 1, 40, 10, NOW());

        INSERT INTO historial_precio (id_variante, id_usuario, precio_anterior, precio_nuevo, fecha_modificacion)
        VALUES (v_id_var, 1, 13.0, 22.0, NOW());
    END IF;
END $$;
DO $$
DECLARE
    v_id_sub INT;
    v_id_uni INT;
    v_id_prod INT;
    v_id_var INT;
BEGIN
    SELECT id_subcategoria INTO v_id_sub FROM subcategoria WHERE nombre = 'Desodorantes e Higiene Corporal' LIMIT 1;
    SELECT id_unidad INTO v_id_uni FROM unidad_medida WHERE codigo = 'UND' LIMIT 1;
    IF v_id_uni IS NULL THEN
        SELECT id_unidad INTO v_id_uni FROM unidad_medida WHERE codigo = 'UND' LIMIT 1;
    END IF;

    SELECT id_producto INTO v_id_prod FROM producto WHERE nombre = 'Desodorante en Gel Transparente Antitranspirante';
    IF v_id_prod IS NULL THEN
        INSERT INTO producto (id_subcategoria, id_unidad, nombre, descripcion, imagen_url, estado, fecha_creacion)
        VALUES (v_id_sub, v_id_uni, 'Desodorante en Gel Transparente Antitranspirante', 'Gel refrescante de secado instantáneo sin manchas en ropa', NULL, 'Activo', NOW())
        RETURNING id_producto INTO v_id_prod;

        INSERT INTO variante_producto (id_producto, codigo_barras, talla, color, precio_detalle, precio_mayoreo, costo_promedio)
        VALUES (v_id_prod, '7401202601076', '113g', 'Azul Claro', 34.0, 28.0, 20.0)
        RETURNING id_variante INTO v_id_var;

        INSERT INTO inventario_sucursal (id_variante, id_sucursal, id_area, stock_actual, stock_minimo, fecha_actualizacion)
        VALUES (v_id_var, 1, 1, 35, 10, NOW());

        INSERT INTO historial_precio (id_variante, id_usuario, precio_anterior, precio_nuevo, fecha_modificacion)
        VALUES (v_id_var, 1, 20.0, 34.0, NOW());
    END IF;
END $$;
DO $$
DECLARE
    v_id_sub INT;
    v_id_uni INT;
    v_id_prod INT;
    v_id_var INT;
BEGIN
    SELECT id_subcategoria INTO v_id_sub FROM subcategoria WHERE nombre = 'Desodorantes e Higiene Corporal' LIMIT 1;
    SELECT id_unidad INTO v_id_uni FROM unidad_medida WHERE codigo = 'UND' LIMIT 1;
    IF v_id_uni IS NULL THEN
        SELECT id_unidad INTO v_id_uni FROM unidad_medida WHERE codigo = 'UND' LIMIT 1;
    END IF;

    SELECT id_producto INTO v_id_prod FROM producto WHERE nombre = 'Body Spray Desodorante Fragancia Marina 200ml';
    IF v_id_prod IS NULL THEN
        INSERT INTO producto (id_subcategoria, id_unidad, nombre, descripcion, imagen_url, estado, fecha_creacion)
        VALUES (v_id_sub, v_id_uni, 'Body Spray Desodorante Fragancia Marina 200ml', 'Aerosol corporal diario aroma fresco masculino', NULL, 'Activo', NOW())
        RETURNING id_producto INTO v_id_prod;

        INSERT INTO variante_producto (id_producto, codigo_barras, talla, color, precio_detalle, precio_mayoreo, costo_promedio)
        VALUES (v_id_prod, '7401202601077', '200ml', 'Celeste', 26.0, 21.0, 15.0)
        RETURNING id_variante INTO v_id_var;

        INSERT INTO inventario_sucursal (id_variante, id_sucursal, id_area, stock_actual, stock_minimo, fecha_actualizacion)
        VALUES (v_id_var, 1, 1, 42, 10, NOW());

        INSERT INTO historial_precio (id_variante, id_usuario, precio_anterior, precio_nuevo, fecha_modificacion)
        VALUES (v_id_var, 1, 15.0, 26.0, NOW());
    END IF;
END $$;
DO $$
DECLARE
    v_id_sub INT;
    v_id_uni INT;
    v_id_prod INT;
    v_id_var INT;
BEGIN
    SELECT id_subcategoria INTO v_id_sub FROM subcategoria WHERE nombre = 'Desodorantes e Higiene Corporal' LIMIT 1;
    SELECT id_unidad INTO v_id_uni FROM unidad_medida WHERE codigo = 'UND' LIMIT 1;
    IF v_id_uni IS NULL THEN
        SELECT id_unidad INTO v_id_uni FROM unidad_medida WHERE codigo = 'UND' LIMIT 1;
    END IF;

    SELECT id_producto INTO v_id_prod FROM producto WHERE nombre = 'Desodorante Crema Antitranspirante Piel Sensible 60g';
    IF v_id_prod IS NULL THEN
        INSERT INTO producto (id_subcategoria, id_unidad, nombre, descripcion, imagen_url, estado, fecha_creacion)
        VALUES (v_id_sub, v_id_uni, 'Desodorante Crema Antitranspirante Piel Sensible 60g', 'Crema suave con aloe vera para pieles reactivas sin alcohol', NULL, 'Activo', NOW())
        RETURNING id_producto INTO v_id_prod;

        INSERT INTO variante_producto (id_producto, codigo_barras, talla, color, precio_detalle, precio_mayoreo, costo_promedio)
        VALUES (v_id_prod, '7401202601078', '60g', 'Blanco', 25.0, 20.0, 14.5)
        RETURNING id_variante INTO v_id_var;

        INSERT INTO inventario_sucursal (id_variante, id_sucursal, id_area, stock_actual, stock_minimo, fecha_actualizacion)
        VALUES (v_id_var, 1, 1, 38, 10, NOW());

        INSERT INTO historial_precio (id_variante, id_usuario, precio_anterior, precio_nuevo, fecha_modificacion)
        VALUES (v_id_var, 1, 14.5, 25.0, NOW());
    END IF;
END $$;
DO $$
DECLARE
    v_id_sub INT;
    v_id_uni INT;
    v_id_prod INT;
    v_id_var INT;
BEGIN
    SELECT id_subcategoria INTO v_id_sub FROM subcategoria WHERE nombre = 'Desodorantes e Higiene Corporal' LIMIT 1;
    SELECT id_unidad INTO v_id_uni FROM unidad_medida WHERE codigo = 'UND' LIMIT 1;
    IF v_id_uni IS NULL THEN
        SELECT id_unidad INTO v_id_uni FROM unidad_medida WHERE codigo = 'UND' LIMIT 1;
    END IF;

    SELECT id_producto INTO v_id_prod FROM producto WHERE nombre = 'Desodorante Roll-On Carbón Activado 50ml';
    IF v_id_prod IS NULL THEN
        INSERT INTO producto (id_subcategoria, id_unidad, nombre, descripcion, imagen_url, estado, fecha_creacion)
        VALUES (v_id_sub, v_id_uni, 'Desodorante Roll-On Carbón Activado 50ml', 'Fórmula purificante con carbón activado neutralizador de olor', NULL, 'Activo', NOW())
        RETURNING id_producto INTO v_id_prod;

        INSERT INTO variante_producto (id_producto, codigo_barras, talla, color, precio_detalle, precio_mayoreo, costo_promedio)
        VALUES (v_id_prod, '7401202601079', '50ml', 'Negro', 23.0, 19.0, 13.5)
        RETURNING id_variante INTO v_id_var;

        INSERT INTO inventario_sucursal (id_variante, id_sucursal, id_area, stock_actual, stock_minimo, fecha_actualizacion)
        VALUES (v_id_var, 1, 3, 45, 12, NOW());

        INSERT INTO historial_precio (id_variante, id_usuario, precio_anterior, precio_nuevo, fecha_modificacion)
        VALUES (v_id_var, 1, 13.5, 23.0, NOW());
    END IF;
END $$;
DO $$
DECLARE
    v_id_sub INT;
    v_id_uni INT;
    v_id_prod INT;
    v_id_var INT;
BEGIN
    SELECT id_subcategoria INTO v_id_sub FROM subcategoria WHERE nombre = 'Desodorantes e Higiene Corporal' LIMIT 1;
    SELECT id_unidad INTO v_id_uni FROM unidad_medida WHERE codigo = 'UND' LIMIT 1;
    IF v_id_uni IS NULL THEN
        SELECT id_unidad INTO v_id_uni FROM unidad_medida WHERE codigo = 'UND' LIMIT 1;
    END IF;

    SELECT id_producto INTO v_id_prod FROM producto WHERE nombre = 'Desodorante Hipoalergénico Cero Aluminio 75ml';
    IF v_id_prod IS NULL THEN
        INSERT INTO producto (id_subcategoria, id_unidad, nombre, descripcion, imagen_url, estado, fecha_creacion)
        VALUES (v_id_sub, v_id_uni, 'Desodorante Hipoalergénico Cero Aluminio 75ml', 'Roll-on orgánico con aceites esenciales naturales', NULL, 'Activo', NOW())
        RETURNING id_producto INTO v_id_prod;

        INSERT INTO variante_producto (id_producto, codigo_barras, talla, color, precio_detalle, precio_mayoreo, costo_promedio)
        VALUES (v_id_prod, '7401202601080', '75ml', 'Verde Menta', 30.0, 24.0, 17.0)
        RETURNING id_variante INTO v_id_var;

        INSERT INTO inventario_sucursal (id_variante, id_sucursal, id_area, stock_actual, stock_minimo, fecha_actualizacion)
        VALUES (v_id_var, 1, 1, 32, 8, NOW());

        INSERT INTO historial_precio (id_variante, id_usuario, precio_anterior, precio_nuevo, fecha_modificacion)
        VALUES (v_id_var, 1, 17.0, 30.0, NOW());
    END IF;
END $$;

-- --- Subcatálogo: Juguetes Educativos y Figuras (10 productos) ---
DO $$
DECLARE
    v_id_sub INT;
    v_id_uni INT;
    v_id_prod INT;
    v_id_var INT;
BEGIN
    SELECT id_subcategoria INTO v_id_sub FROM subcategoria WHERE nombre = 'Juguetes Educativos y Figuras' LIMIT 1;
    SELECT id_unidad INTO v_id_uni FROM unidad_medida WHERE codigo = 'UND' LIMIT 1;
    IF v_id_uni IS NULL THEN
        SELECT id_unidad INTO v_id_uni FROM unidad_medida WHERE codigo = 'UND' LIMIT 1;
    END IF;

    SELECT id_producto INTO v_id_prod FROM producto WHERE nombre = 'Juego de Bloques de Construcción Didácticos 150pz';
    IF v_id_prod IS NULL THEN
        INSERT INTO producto (id_subcategoria, id_unidad, nombre, descripcion, imagen_url, estado, fecha_creacion)
        VALUES (v_id_sub, v_id_uni, 'Juego de Bloques de Construcción Didácticos 150pz', 'Bloques plásticos de ensamble en balde plástico con tapa', NULL, 'Activo', NOW())
        RETURNING id_producto INTO v_id_prod;

        INSERT INTO variante_producto (id_producto, codigo_barras, talla, color, precio_detalle, precio_mayoreo, costo_promedio)
        VALUES (v_id_prod, '7401202601081', '150 Piezas', 'Multicolor', 78.0, 65.0, 45.0)
        RETURNING id_variante INTO v_id_var;

        INSERT INTO inventario_sucursal (id_variante, id_sucursal, id_area, stock_actual, stock_minimo, fecha_actualizacion)
        VALUES (v_id_var, 1, 1, 25, 6, NOW());

        INSERT INTO historial_precio (id_variante, id_usuario, precio_anterior, precio_nuevo, fecha_modificacion)
        VALUES (v_id_var, 1, 45.0, 78.0, NOW());
    END IF;
END $$;
DO $$
DECLARE
    v_id_sub INT;
    v_id_uni INT;
    v_id_prod INT;
    v_id_var INT;
BEGIN
    SELECT id_subcategoria INTO v_id_sub FROM subcategoria WHERE nombre = 'Juguetes Educativos y Figuras' LIMIT 1;
    SELECT id_unidad INTO v_id_uni FROM unidad_medida WHERE codigo = 'UND' LIMIT 1;
    IF v_id_uni IS NULL THEN
        SELECT id_unidad INTO v_id_uni FROM unidad_medida WHERE codigo = 'UND' LIMIT 1;
    END IF;

    SELECT id_producto INTO v_id_prod FROM producto WHERE nombre = 'Carro a Control Remoto Todo Terreno Recargable';
    IF v_id_prod IS NULL THEN
        INSERT INTO producto (id_subcategoria, id_unidad, nombre, descripcion, imagen_url, estado, fecha_creacion)
        VALUES (v_id_sub, v_id_uni, 'Carro a Control Remoto Todo Terreno Recargable', 'Vehículo 4x4 con suspensión alta y batería USB incluida', NULL, 'Activo', NOW())
        RETURNING id_producto INTO v_id_prod;

        INSERT INTO variante_producto (id_producto, codigo_barras, talla, color, precio_detalle, precio_mayoreo, costo_promedio)
        VALUES (v_id_prod, '7401202601082', 'Escala 1:16', 'Rojo Metálico', 150.0, 125.0, 90.0)
        RETURNING id_variante INTO v_id_var;

        INSERT INTO inventario_sucursal (id_variante, id_sucursal, id_area, stock_actual, stock_minimo, fecha_actualizacion)
        VALUES (v_id_var, 1, 1, 18, 5, NOW());

        INSERT INTO historial_precio (id_variante, id_usuario, precio_anterior, precio_nuevo, fecha_modificacion)
        VALUES (v_id_var, 1, 90.0, 150.0, NOW());
    END IF;
END $$;
DO $$
DECLARE
    v_id_sub INT;
    v_id_uni INT;
    v_id_prod INT;
    v_id_var INT;
BEGIN
    SELECT id_subcategoria INTO v_id_sub FROM subcategoria WHERE nombre = 'Juguetes Educativos y Figuras' LIMIT 1;
    SELECT id_unidad INTO v_id_uni FROM unidad_medida WHERE codigo = 'UND' LIMIT 1;
    IF v_id_uni IS NULL THEN
        SELECT id_unidad INTO v_id_uni FROM unidad_medida WHERE codigo = 'UND' LIMIT 1;
    END IF;

    SELECT id_producto INTO v_id_prod FROM producto WHERE nombre = 'Rompecabezas Didáctico de Madera Mapa de Guatemala';
    IF v_id_prod IS NULL THEN
        INSERT INTO producto (id_subcategoria, id_unidad, nombre, descripcion, imagen_url, estado, fecha_creacion)
        VALUES (v_id_sub, v_id_uni, 'Rompecabezas Didáctico de Madera Mapa de Guatemala', 'Puzzle de madera con los 22 departamentos y cabeceras', NULL, 'Activo', NOW())
        RETURNING id_producto INTO v_id_prod;

        INSERT INTO variante_producto (id_producto, codigo_barras, talla, color, precio_detalle, precio_mayoreo, costo_promedio)
        VALUES (v_id_prod, '7401202601083', '30x40cm', 'Multicolor', 40.0, 32.0, 22.0)
        RETURNING id_variante INTO v_id_var;

        INSERT INTO inventario_sucursal (id_variante, id_sucursal, id_area, stock_actual, stock_minimo, fecha_actualizacion)
        VALUES (v_id_var, 1, 1, 35, 10, NOW());

        INSERT INTO historial_precio (id_variante, id_usuario, precio_anterior, precio_nuevo, fecha_modificacion)
        VALUES (v_id_var, 1, 22.0, 40.0, NOW());
    END IF;
END $$;
DO $$
DECLARE
    v_id_sub INT;
    v_id_uni INT;
    v_id_prod INT;
    v_id_var INT;
BEGIN
    SELECT id_subcategoria INTO v_id_sub FROM subcategoria WHERE nombre = 'Juguetes Educativos y Figuras' LIMIT 1;
    SELECT id_unidad INTO v_id_uni FROM unidad_medida WHERE codigo = 'UND' LIMIT 1;
    IF v_id_uni IS NULL THEN
        SELECT id_unidad INTO v_id_uni FROM unidad_medida WHERE codigo = 'UND' LIMIT 1;
    END IF;

    SELECT id_producto INTO v_id_prod FROM producto WHERE nombre = 'Pista de Carreras con Lanzador y 2 Autos Metálicos';
    IF v_id_prod IS NULL THEN
        INSERT INTO producto (id_subcategoria, id_unidad, nombre, descripcion, imagen_url, estado, fecha_creacion)
        VALUES (v_id_sub, v_id_uni, 'Pista de Carreras con Lanzador y 2 Autos Metálicos', 'Pista con curva peraltada y doble loop para carritos de metal', NULL, 'Activo', NOW())
        RETURNING id_producto INTO v_id_prod;

        INSERT INTO variante_producto (id_producto, codigo_barras, talla, color, precio_detalle, precio_mayoreo, costo_promedio)
        VALUES (v_id_prod, '7401202601084', 'Pista 1.8m', 'Naranja/Azul', 95.0, 78.0, 55.0)
        RETURNING id_variante INTO v_id_var;

        INSERT INTO inventario_sucursal (id_variante, id_sucursal, id_area, stock_actual, stock_minimo, fecha_actualizacion)
        VALUES (v_id_var, 1, 1, 20, 5, NOW());

        INSERT INTO historial_precio (id_variante, id_usuario, precio_anterior, precio_nuevo, fecha_modificacion)
        VALUES (v_id_var, 1, 55.0, 95.0, NOW());
    END IF;
END $$;
DO $$
DECLARE
    v_id_sub INT;
    v_id_uni INT;
    v_id_prod INT;
    v_id_var INT;
BEGIN
    SELECT id_subcategoria INTO v_id_sub FROM subcategoria WHERE nombre = 'Juguetes Educativos y Figuras' LIMIT 1;
    SELECT id_unidad INTO v_id_uni FROM unidad_medida WHERE codigo = 'UND' LIMIT 1;
    IF v_id_uni IS NULL THEN
        SELECT id_unidad INTO v_id_uni FROM unidad_medida WHERE codigo = 'UND' LIMIT 1;
    END IF;

    SELECT id_producto INTO v_id_prod FROM producto WHERE nombre = 'Juego de Mesa de Estrategia Familiar';
    IF v_id_prod IS NULL THEN
        INSERT INTO producto (id_subcategoria, id_unidad, nombre, descripcion, imagen_url, estado, fecha_creacion)
        VALUES (v_id_sub, v_id_uni, 'Juego de Mesa de Estrategia Familiar', 'Juego de mesa clásico de finanzas y propiedades en español', NULL, 'Activo', NOW())
        RETURNING id_producto INTO v_id_prod;

        INSERT INTO variante_producto (id_producto, codigo_barras, talla, color, precio_detalle, precio_mayoreo, costo_promedio)
        VALUES (v_id_prod, '7401202601085', 'Caja Grande', 'Multicolor', 72.0, 60.0, 42.0)
        RETURNING id_variante INTO v_id_var;

        INSERT INTO inventario_sucursal (id_variante, id_sucursal, id_area, stock_actual, stock_minimo, fecha_actualizacion)
        VALUES (v_id_var, 1, 1, 24, 6, NOW());

        INSERT INTO historial_precio (id_variante, id_usuario, precio_anterior, precio_nuevo, fecha_modificacion)
        VALUES (v_id_var, 1, 42.0, 72.0, NOW());
    END IF;
END $$;
DO $$
DECLARE
    v_id_sub INT;
    v_id_uni INT;
    v_id_prod INT;
    v_id_var INT;
BEGIN
    SELECT id_subcategoria INTO v_id_sub FROM subcategoria WHERE nombre = 'Juguetes Educativos y Figuras' LIMIT 1;
    SELECT id_unidad INTO v_id_uni FROM unidad_medida WHERE codigo = 'SET' LIMIT 1;
    IF v_id_uni IS NULL THEN
        SELECT id_unidad INTO v_id_uni FROM unidad_medida WHERE codigo = 'UND' LIMIT 1;
    END IF;

    SELECT id_producto INTO v_id_prod FROM producto WHERE nombre = 'Set de Masa no Tóxica 12 Colores con Moldes';
    IF v_id_prod IS NULL THEN
        INSERT INTO producto (id_subcategoria, id_unidad, nombre, descripcion, imagen_url, estado, fecha_creacion)
        VALUES (v_id_sub, v_id_uni, 'Set de Masa no Tóxica 12 Colores con Moldes', 'Plastilina moldeable perfumada segura para niños pequeños', NULL, 'Activo', NOW())
        RETURNING id_producto INTO v_id_prod;

        INSERT INTO variante_producto (id_producto, codigo_barras, talla, color, precio_detalle, precio_mayoreo, costo_promedio)
        VALUES (v_id_prod, '7401202601086', 'Set Completo', '12 Colores', 32.0, 26.0, 18.0)
        RETURNING id_variante INTO v_id_var;

        INSERT INTO inventario_sucursal (id_variante, id_sucursal, id_area, stock_actual, stock_minimo, fecha_actualizacion)
        VALUES (v_id_var, 1, 1, 45, 12, NOW());

        INSERT INTO historial_precio (id_variante, id_usuario, precio_anterior, precio_nuevo, fecha_modificacion)
        VALUES (v_id_var, 1, 18.0, 32.0, NOW());
    END IF;
END $$;
DO $$
DECLARE
    v_id_sub INT;
    v_id_uni INT;
    v_id_prod INT;
    v_id_var INT;
BEGIN
    SELECT id_subcategoria INTO v_id_sub FROM subcategoria WHERE nombre = 'Juguetes Educativos y Figuras' LIMIT 1;
    SELECT id_unidad INTO v_id_uni FROM unidad_medida WHERE codigo = 'UND' LIMIT 1;
    IF v_id_uni IS NULL THEN
        SELECT id_unidad INTO v_id_uni FROM unidad_medida WHERE codigo = 'UND' LIMIT 1;
    END IF;

    SELECT id_producto INTO v_id_prod FROM producto WHERE nombre = 'Figura de Acción Súper Héroe Articulada 30cm';
    IF v_id_prod IS NULL THEN
        INSERT INTO producto (id_subcategoria, id_unidad, nombre, descripcion, imagen_url, estado, fecha_creacion)
        VALUES (v_id_sub, v_id_uni, 'Figura de Acción Súper Héroe Articulada 30cm', 'Muñeco articulado con luces y sonidos de combate', NULL, 'Activo', NOW())
        RETURNING id_producto INTO v_id_prod;

        INSERT INTO variante_producto (id_producto, codigo_barras, talla, color, precio_detalle, precio_mayoreo, costo_promedio)
        VALUES (v_id_prod, '7401202601087', '30cm', 'Azul/Rojo', 65.0, 52.0, 38.0)
        RETURNING id_variante INTO v_id_var;

        INSERT INTO inventario_sucursal (id_variante, id_sucursal, id_area, stock_actual, stock_minimo, fecha_actualizacion)
        VALUES (v_id_var, 1, 1, 30, 8, NOW());

        INSERT INTO historial_precio (id_variante, id_usuario, precio_anterior, precio_nuevo, fecha_modificacion)
        VALUES (v_id_var, 1, 38.0, 65.0, NOW());
    END IF;
END $$;
DO $$
DECLARE
    v_id_sub INT;
    v_id_uni INT;
    v_id_prod INT;
    v_id_var INT;
BEGIN
    SELECT id_subcategoria INTO v_id_sub FROM subcategoria WHERE nombre = 'Juguetes Educativos y Figuras' LIMIT 1;
    SELECT id_unidad INTO v_id_uni FROM unidad_medida WHERE codigo = 'SET' LIMIT 1;
    IF v_id_uni IS NULL THEN
        SELECT id_unidad INTO v_id_uni FROM unidad_medida WHERE codigo = 'UND' LIMIT 1;
    END IF;

    SELECT id_producto INTO v_id_prod FROM producto WHERE nombre = 'Juego de Té y Pastelería Infantil 14 Piezas';
    IF v_id_prod IS NULL THEN
        INSERT INTO producto (id_subcategoria, id_unidad, nombre, descripcion, imagen_url, estado, fecha_creacion)
        VALUES (v_id_sub, v_id_uni, 'Juego de Té y Pastelería Infantil 14 Piezas', 'Juego de tacitas de té, tetera y platitos de colores para niñas', NULL, 'Activo', NOW())
        RETURNING id_producto INTO v_id_prod;

        INSERT INTO variante_producto (id_producto, codigo_barras, talla, color, precio_detalle, precio_mayoreo, costo_promedio)
        VALUES (v_id_prod, '7401202601088', '14 Piezas', 'Tonos Pastel', 48.0, 40.0, 28.0)
        RETURNING id_variante INTO v_id_var;

        INSERT INTO inventario_sucursal (id_variante, id_sucursal, id_area, stock_actual, stock_minimo, fecha_actualizacion)
        VALUES (v_id_var, 1, 1, 25, 6, NOW());

        INSERT INTO historial_precio (id_variante, id_usuario, precio_anterior, precio_nuevo, fecha_modificacion)
        VALUES (v_id_var, 1, 28.0, 48.0, NOW());
    END IF;
END $$;
DO $$
DECLARE
    v_id_sub INT;
    v_id_uni INT;
    v_id_prod INT;
    v_id_var INT;
BEGIN
    SELECT id_subcategoria INTO v_id_sub FROM subcategoria WHERE nombre = 'Juguetes Educativos y Figuras' LIMIT 1;
    SELECT id_unidad INTO v_id_uni FROM unidad_medida WHERE codigo = 'UND' LIMIT 1;
    IF v_id_uni IS NULL THEN
        SELECT id_unidad INTO v_id_uni FROM unidad_medida WHERE codigo = 'UND' LIMIT 1;
    END IF;

    SELECT id_producto INTO v_id_prod FROM producto WHERE nombre = 'Pistola de Burbujas Eléctrica con Luz LED';
    IF v_id_prod IS NULL THEN
        INSERT INTO producto (id_subcategoria, id_unidad, nombre, descripcion, imagen_url, estado, fecha_creacion)
        VALUES (v_id_sub, v_id_uni, 'Pistola de Burbujas Eléctrica con Luz LED', 'Lanzador automático que genera cientos de burbujas por minuto', NULL, 'Activo', NOW())
        RETURNING id_producto INTO v_id_prod;

        INSERT INTO variante_producto (id_producto, codigo_barras, talla, color, precio_detalle, precio_mayoreo, costo_promedio)
        VALUES (v_id_prod, '7401202601089', 'Pistola + Solución', 'Celeste', 44.0, 36.0, 25.0)
        RETURNING id_variante INTO v_id_var;

        INSERT INTO inventario_sucursal (id_variante, id_sucursal, id_area, stock_actual, stock_minimo, fecha_actualizacion)
        VALUES (v_id_var, 1, 3, 32, 8, NOW());

        INSERT INTO historial_precio (id_variante, id_usuario, precio_anterior, precio_nuevo, fecha_modificacion)
        VALUES (v_id_var, 1, 25.0, 44.0, NOW());
    END IF;
END $$;
DO $$
DECLARE
    v_id_sub INT;
    v_id_uni INT;
    v_id_prod INT;
    v_id_var INT;
BEGIN
    SELECT id_subcategoria INTO v_id_sub FROM subcategoria WHERE nombre = 'Juguetes Educativos y Figuras' LIMIT 1;
    SELECT id_unidad INTO v_id_uni FROM unidad_medida WHERE codigo = 'UND' LIMIT 1;
    IF v_id_uni IS NULL THEN
        SELECT id_unidad INTO v_id_uni FROM unidad_medida WHERE codigo = 'UND' LIMIT 1;
    END IF;

    SELECT id_producto INTO v_id_prod FROM producto WHERE nombre = 'Cocinita de Juguete con Sonidos y Accesorios';
    IF v_id_prod IS NULL THEN
        INSERT INTO producto (id_subcategoria, id_unidad, nombre, descripcion, imagen_url, estado, fecha_creacion)
        VALUES (v_id_sub, v_id_uni, 'Cocinita de Juguete con Sonidos y Accesorios', 'Mini cocina infantil con estufa que enciende luz y sartencitos', NULL, 'Activo', NOW())
        RETURNING id_producto INTO v_id_prod;

        INSERT INTO variante_producto (id_producto, codigo_barras, talla, color, precio_detalle, precio_mayoreo, costo_promedio)
        VALUES (v_id_prod, '7401202601090', 'Mediana', 'Rosa/Blanco', 160.0, 135.0, 98.0)
        RETURNING id_variante INTO v_id_var;

        INSERT INTO inventario_sucursal (id_variante, id_sucursal, id_area, stock_actual, stock_minimo, fecha_actualizacion)
        VALUES (v_id_var, 1, 1, 14, 4, NOW());

        INSERT INTO historial_precio (id_variante, id_usuario, precio_anterior, precio_nuevo, fecha_modificacion)
        VALUES (v_id_var, 1, 98.0, 160.0, NOW());
    END IF;
END $$;

-- --- Subcatálogo: Carteras y Billeteras (10 productos) ---
DO $$
DECLARE
    v_id_sub INT;
    v_id_uni INT;
    v_id_prod INT;
    v_id_var INT;
BEGIN
    SELECT id_subcategoria INTO v_id_sub FROM subcategoria WHERE nombre = 'Carteras y Billeteras' LIMIT 1;
    SELECT id_unidad INTO v_id_uni FROM unidad_medida WHERE codigo = 'UND' LIMIT 1;
    IF v_id_uni IS NULL THEN
        SELECT id_unidad INTO v_id_uni FROM unidad_medida WHERE codigo = 'UND' LIMIT 1;
    END IF;

    SELECT id_producto INTO v_id_prod FROM producto WHERE nombre = 'Billetera de Cuero Auténtico Plegable para Caballero';
    IF v_id_prod IS NULL THEN
        INSERT INTO producto (id_subcategoria, id_unidad, nombre, descripcion, imagen_url, estado, fecha_creacion)
        VALUES (v_id_sub, v_id_uni, 'Billetera de Cuero Auténtico Plegable para Caballero', 'Billetera bifold con tarjetero, billetero doble y ventana para ID', NULL, 'Activo', NOW())
        RETURNING id_producto INTO v_id_prod;

        INSERT INTO variante_producto (id_producto, codigo_barras, talla, color, precio_detalle, precio_mayoreo, costo_promedio)
        VALUES (v_id_prod, '7401202601091', 'Clásica', 'Café Oscuro', 85.0, 68.0, 48.0)
        RETURNING id_variante INTO v_id_var;

        INSERT INTO inventario_sucursal (id_variante, id_sucursal, id_area, stock_actual, stock_minimo, fecha_actualizacion)
        VALUES (v_id_var, 1, 1, 30, 8, NOW());

        INSERT INTO historial_precio (id_variante, id_usuario, precio_anterior, precio_nuevo, fecha_modificacion)
        VALUES (v_id_var, 1, 48.0, 85.0, NOW());
    END IF;
END $$;
DO $$
DECLARE
    v_id_sub INT;
    v_id_uni INT;
    v_id_prod INT;
    v_id_var INT;
BEGIN
    SELECT id_subcategoria INTO v_id_sub FROM subcategoria WHERE nombre = 'Carteras y Billeteras' LIMIT 1;
    SELECT id_unidad INTO v_id_uni FROM unidad_medida WHERE codigo = 'UND' LIMIT 1;
    IF v_id_uni IS NULL THEN
        SELECT id_unidad INTO v_id_uni FROM unidad_medida WHERE codigo = 'UND' LIMIT 1;
    END IF;

    SELECT id_producto INTO v_id_prod FROM producto WHERE nombre = 'Cartera Larga para Dama con Cierre y Asa';
    IF v_id_prod IS NULL THEN
        INSERT INTO producto (id_subcategoria, id_unidad, nombre, descripcion, imagen_url, estado, fecha_creacion)
        VALUES (v_id_sub, v_id_uni, 'Cartera Larga para Dama con Cierre y Asa', 'Billetera clutch con compartimento para billetes, monedas y celular', NULL, 'Activo', NOW())
        RETURNING id_producto INTO v_id_prod;

        INSERT INTO variante_producto (id_producto, codigo_barras, talla, color, precio_detalle, precio_mayoreo, costo_promedio)
        VALUES (v_id_prod, '7401202601092', '20x10cm', 'Rojo Borgoña', 78.0, 64.0, 45.0)
        RETURNING id_variante INTO v_id_var;

        INSERT INTO inventario_sucursal (id_variante, id_sucursal, id_area, stock_actual, stock_minimo, fecha_actualizacion)
        VALUES (v_id_var, 1, 1, 28, 7, NOW());

        INSERT INTO historial_precio (id_variante, id_usuario, precio_anterior, precio_nuevo, fecha_modificacion)
        VALUES (v_id_var, 1, 45.0, 78.0, NOW());
    END IF;
END $$;
DO $$
DECLARE
    v_id_sub INT;
    v_id_uni INT;
    v_id_prod INT;
    v_id_var INT;
BEGIN
    SELECT id_subcategoria INTO v_id_sub FROM subcategoria WHERE nombre = 'Carteras y Billeteras' LIMIT 1;
    SELECT id_unidad INTO v_id_uni FROM unidad_medida WHERE codigo = 'UND' LIMIT 1;
    IF v_id_uni IS NULL THEN
        SELECT id_unidad INTO v_id_uni FROM unidad_medida WHERE codigo = 'UND' LIMIT 1;
    END IF;

    SELECT id_producto INTO v_id_prod FROM producto WHERE nombre = 'Billetera Slim Minimalista con Bloqueo RFID';
    IF v_id_prod IS NULL THEN
        INSERT INTO producto (id_subcategoria, id_unidad, nombre, descripcion, imagen_url, estado, fecha_creacion)
        VALUES (v_id_sub, v_id_uni, 'Billetera Slim Minimalista con Bloqueo RFID', 'Billetera delgada de bolsillo con protección magnética y clip', NULL, 'Activo', NOW())
        RETURNING id_producto INTO v_id_prod;

        INSERT INTO variante_producto (id_producto, codigo_barras, talla, color, precio_detalle, precio_mayoreo, costo_promedio)
        VALUES (v_id_prod, '7401202601093', 'Slim', 'Negro', 55.0, 45.0, 32.0)
        RETURNING id_variante INTO v_id_var;

        INSERT INTO inventario_sucursal (id_variante, id_sucursal, id_area, stock_actual, stock_minimo, fecha_actualizacion)
        VALUES (v_id_var, 1, 3, 40, 10, NOW());

        INSERT INTO historial_precio (id_variante, id_usuario, precio_anterior, precio_nuevo, fecha_modificacion)
        VALUES (v_id_var, 1, 32.0, 55.0, NOW());
    END IF;
END $$;
DO $$
DECLARE
    v_id_sub INT;
    v_id_uni INT;
    v_id_prod INT;
    v_id_var INT;
BEGIN
    SELECT id_subcategoria INTO v_id_sub FROM subcategoria WHERE nombre = 'Carteras y Billeteras' LIMIT 1;
    SELECT id_unidad INTO v_id_uni FROM unidad_medida WHERE codigo = 'UND' LIMIT 1;
    IF v_id_uni IS NULL THEN
        SELECT id_unidad INTO v_id_uni FROM unidad_medida WHERE codigo = 'UND' LIMIT 1;
    END IF;

    SELECT id_producto INTO v_id_prod FROM producto WHERE nombre = 'Monedero Cartera Pequeño con Broche Metálico';
    IF v_id_prod IS NULL THEN
        INSERT INTO producto (id_subcategoria, id_unidad, nombre, descripcion, imagen_url, estado, fecha_creacion)
        VALUES (v_id_sub, v_id_uni, 'Monedero Cartera Pequeño con Broche Metálico', 'Monedero de cuero sintético suave con forro interior', NULL, 'Activo', NOW())
        RETURNING id_producto INTO v_id_prod;

        INSERT INTO variante_producto (id_producto, codigo_barras, talla, color, precio_detalle, precio_mayoreo, costo_promedio)
        VALUES (v_id_prod, '7401202601094', '10x8cm', 'Café Claro', 19.0, 15.0, 10.0)
        RETURNING id_variante INTO v_id_var;

        INSERT INTO inventario_sucursal (id_variante, id_sucursal, id_area, stock_actual, stock_minimo, fecha_actualizacion)
        VALUES (v_id_var, 1, 3, 50, 15, NOW());

        INSERT INTO historial_precio (id_variante, id_usuario, precio_anterior, precio_nuevo, fecha_modificacion)
        VALUES (v_id_var, 1, 10.0, 19.0, NOW());
    END IF;
END $$;
DO $$
DECLARE
    v_id_sub INT;
    v_id_uni INT;
    v_id_prod INT;
    v_id_var INT;
BEGIN
    SELECT id_subcategoria INTO v_id_sub FROM subcategoria WHERE nombre = 'Carteras y Billeteras' LIMIT 1;
    SELECT id_unidad INTO v_id_uni FROM unidad_medida WHERE codigo = 'UND' LIMIT 1;
    IF v_id_uni IS NULL THEN
        SELECT id_unidad INTO v_id_uni FROM unidad_medida WHERE codigo = 'UND' LIMIT 1;
    END IF;

    SELECT id_producto INTO v_id_prod FROM producto WHERE nombre = 'Billetera Trifold Deportiva de Lona con Cierre';
    IF v_id_prod IS NULL THEN
        INSERT INTO producto (id_subcategoria, id_unidad, nombre, descripcion, imagen_url, estado, fecha_creacion)
        VALUES (v_id_sub, v_id_uni, 'Billetera Trifold Deportiva de Lona con Cierre', 'Billetera triple pliegue con cierre de velcro resistente al agua', NULL, 'Activo', NOW())
        RETURNING id_producto INTO v_id_prod;

        INSERT INTO variante_producto (id_producto, codigo_barras, talla, color, precio_detalle, precio_mayoreo, costo_promedio)
        VALUES (v_id_prod, '7401202601095', 'Trifold', 'Azul Marino', 32.0, 26.0, 18.0)
        RETURNING id_variante INTO v_id_var;

        INSERT INTO inventario_sucursal (id_variante, id_sucursal, id_area, stock_actual, stock_minimo, fecha_actualizacion)
        VALUES (v_id_var, 1, 1, 35, 8, NOW());

        INSERT INTO historial_precio (id_variante, id_usuario, precio_anterior, precio_nuevo, fecha_modificacion)
        VALUES (v_id_var, 1, 18.0, 32.0, NOW());
    END IF;
END $$;
DO $$
DECLARE
    v_id_sub INT;
    v_id_uni INT;
    v_id_prod INT;
    v_id_var INT;
BEGIN
    SELECT id_subcategoria INTO v_id_sub FROM subcategoria WHERE nombre = 'Carteras y Billeteras' LIMIT 1;
    SELECT id_unidad INTO v_id_uni FROM unidad_medida WHERE codigo = 'UND' LIMIT 1;
    IF v_id_uni IS NULL THEN
        SELECT id_unidad INTO v_id_uni FROM unidad_medida WHERE codigo = 'UND' LIMIT 1;
    END IF;

    SELECT id_producto INTO v_id_prod FROM producto WHERE nombre = 'Cartera Dama con Diseños Típicos de Telar';
    IF v_id_prod IS NULL THEN
        INSERT INTO producto (id_subcategoria, id_unidad, nombre, descripcion, imagen_url, estado, fecha_creacion)
        VALUES (v_id_sub, v_id_uni, 'Cartera Dama con Diseños Típicos de Telar', 'Cartera con aplicación de telar bordado típico de Sololá', NULL, 'Activo', NOW())
        RETURNING id_producto INTO v_id_prod;

        INSERT INTO variante_producto (id_producto, codigo_barras, talla, color, precio_detalle, precio_mayoreo, costo_promedio)
        VALUES (v_id_prod, '7401202601096', '19x10cm', 'Multicolor Típico', 68.0, 56.0, 40.0)
        RETURNING id_variante INTO v_id_var;

        INSERT INTO inventario_sucursal (id_variante, id_sucursal, id_area, stock_actual, stock_minimo, fecha_actualizacion)
        VALUES (v_id_var, 1, 1, 25, 6, NOW());

        INSERT INTO historial_precio (id_variante, id_usuario, precio_anterior, precio_nuevo, fecha_modificacion)
        VALUES (v_id_var, 1, 40.0, 68.0, NOW());
    END IF;
END $$;
DO $$
DECLARE
    v_id_sub INT;
    v_id_uni INT;
    v_id_prod INT;
    v_id_var INT;
BEGIN
    SELECT id_subcategoria INTO v_id_sub FROM subcategoria WHERE nombre = 'Carteras y Billeteras' LIMIT 1;
    SELECT id_unidad INTO v_id_uni FROM unidad_medida WHERE codigo = 'UND' LIMIT 1;
    IF v_id_uni IS NULL THEN
        SELECT id_unidad INTO v_id_uni FROM unidad_medida WHERE codigo = 'UND' LIMIT 1;
    END IF;

    SELECT id_producto INTO v_id_prod FROM producto WHERE nombre = 'Cartera Tipo Sobre de Fiesta con Cadena Dorada';
    IF v_id_prod IS NULL THEN
        INSERT INTO producto (id_subcategoria, id_unidad, nombre, descripcion, imagen_url, estado, fecha_creacion)
        VALUES (v_id_sub, v_id_uni, 'Cartera Tipo Sobre de Fiesta con Cadena Dorada', 'Bolso de mano para eventos con cadena desmontable elegante', NULL, 'Activo', NOW())
        RETURNING id_producto INTO v_id_prod;

        INSERT INTO variante_producto (id_producto, codigo_barras, talla, color, precio_detalle, precio_mayoreo, costo_promedio)
        VALUES (v_id_prod, '7401202601097', '24x14cm', 'Negro Elegante', 65.0, 54.0, 38.0)
        RETURNING id_variante INTO v_id_var;

        INSERT INTO inventario_sucursal (id_variante, id_sucursal, id_area, stock_actual, stock_minimo, fecha_actualizacion)
        VALUES (v_id_var, 1, 1, 22, 5, NOW());

        INSERT INTO historial_precio (id_variante, id_usuario, precio_anterior, precio_nuevo, fecha_modificacion)
        VALUES (v_id_var, 1, 38.0, 65.0, NOW());
    END IF;
END $$;
DO $$
DECLARE
    v_id_sub INT;
    v_id_uni INT;
    v_id_prod INT;
    v_id_var INT;
BEGIN
    SELECT id_subcategoria INTO v_id_sub FROM subcategoria WHERE nombre = 'Carteras y Billeteras' LIMIT 1;
    SELECT id_unidad INTO v_id_uni FROM unidad_medida WHERE codigo = 'UND' LIMIT 1;
    IF v_id_uni IS NULL THEN
        SELECT id_unidad INTO v_id_uni FROM unidad_medida WHERE codigo = 'UND' LIMIT 1;
    END IF;

    SELECT id_producto INTO v_id_prod FROM producto WHERE nombre = 'Billetera Juvenil con Estampado Urbano';
    IF v_id_prod IS NULL THEN
        INSERT INTO producto (id_subcategoria, id_unidad, nombre, descripcion, imagen_url, estado, fecha_creacion)
        VALUES (v_id_sub, v_id_uni, 'Billetera Juvenil con Estampado Urbano', 'Billetera de material sintético resistente para jóvenes', NULL, 'Activo', NOW())
        RETURNING id_producto INTO v_id_prod;

        INSERT INTO variante_producto (id_producto, codigo_barras, talla, color, precio_detalle, precio_mayoreo, costo_promedio)
        VALUES (v_id_prod, '7401202601098', 'Bifold', 'Gris Grafiti', 35.0, 28.0, 20.0)
        RETURNING id_variante INTO v_id_var;

        INSERT INTO inventario_sucursal (id_variante, id_sucursal, id_area, stock_actual, stock_minimo, fecha_actualizacion)
        VALUES (v_id_var, 1, 1, 35, 8, NOW());

        INSERT INTO historial_precio (id_variante, id_usuario, precio_anterior, precio_nuevo, fecha_modificacion)
        VALUES (v_id_var, 1, 20.0, 35.0, NOW());
    END IF;
END $$;
DO $$
DECLARE
    v_id_sub INT;
    v_id_uni INT;
    v_id_prod INT;
    v_id_var INT;
BEGIN
    SELECT id_subcategoria INTO v_id_sub FROM subcategoria WHERE nombre = 'Carteras y Billeteras' LIMIT 1;
    SELECT id_unidad INTO v_id_uni FROM unidad_medida WHERE codigo = 'UND' LIMIT 1;
    IF v_id_uni IS NULL THEN
        SELECT id_unidad INTO v_id_uni FROM unidad_medida WHERE codigo = 'UND' LIMIT 1;
    END IF;

    SELECT id_producto INTO v_id_prod FROM producto WHERE nombre = 'Tarjetero Pop-Up Automático de Aluminio';
    IF v_id_prod IS NULL THEN
        INSERT INTO producto (id_subcategoria, id_unidad, nombre, descripcion, imagen_url, estado, fecha_creacion)
        VALUES (v_id_sub, v_id_uni, 'Tarjetero Pop-Up Automático de Aluminio', 'Portatarjetas con expulsador automático y cubierta de piel', NULL, 'Activo', NOW())
        RETURNING id_producto INTO v_id_prod;

        INSERT INTO variante_producto (id_producto, codigo_barras, talla, color, precio_detalle, precio_mayoreo, costo_promedio)
        VALUES (v_id_prod, '7401202601099', '6 Tarjetas', 'Plata/Negro', 60.0, 48.0, 35.0)
        RETURNING id_variante INTO v_id_var;

        INSERT INTO inventario_sucursal (id_variante, id_sucursal, id_area, stock_actual, stock_minimo, fecha_actualizacion)
        VALUES (v_id_var, 1, 3, 30, 8, NOW());

        INSERT INTO historial_precio (id_variante, id_usuario, precio_anterior, precio_nuevo, fecha_modificacion)
        VALUES (v_id_var, 1, 35.0, 60.0, NOW());
    END IF;
END $$;
DO $$
DECLARE
    v_id_sub INT;
    v_id_uni INT;
    v_id_prod INT;
    v_id_var INT;
BEGIN
    SELECT id_subcategoria INTO v_id_sub FROM subcategoria WHERE nombre = 'Carteras y Billeteras' LIMIT 1;
    SELECT id_unidad INTO v_id_uni FROM unidad_medida WHERE codigo = 'UND' LIMIT 1;
    IF v_id_uni IS NULL THEN
        SELECT id_unidad INTO v_id_uni FROM unidad_medida WHERE codigo = 'UND' LIMIT 1;
    END IF;

    SELECT id_producto INTO v_id_prod FROM producto WHERE nombre = 'Cartera Bandolera Pequeña para Celular y Dinero';
    IF v_id_prod IS NULL THEN
        INSERT INTO producto (id_subcategoria, id_unidad, nombre, descripcion, imagen_url, estado, fecha_creacion)
        VALUES (v_id_sub, v_id_uni, 'Cartera Bandolera Pequeña para Celular y Dinero', 'Minibolso cruzado para dama con correa ajustable práctica', NULL, 'Activo', NOW())
        RETURNING id_producto INTO v_id_prod;

        INSERT INTO variante_producto (id_producto, codigo_barras, talla, color, precio_detalle, precio_mayoreo, costo_promedio)
        VALUES (v_id_prod, '7401202601100', '18x11cm', 'Mostaza', 62.0, 50.0, 36.0)
        RETURNING id_variante INTO v_id_var;

        INSERT INTO inventario_sucursal (id_variante, id_sucursal, id_area, stock_actual, stock_minimo, fecha_actualizacion)
        VALUES (v_id_var, 1, 1, 26, 6, NOW());

        INSERT INTO historial_precio (id_variante, id_usuario, precio_anterior, precio_nuevo, fecha_modificacion)
        VALUES (v_id_var, 1, 36.0, 62.0, NOW());
    END IF;
END $$;

-- 7. Órdenes de Compra y Compras Recibidas
DO $$
DECLARE
    v_id_prov INT;
    v_id_orden INT;
    v_id_compra INT;
    v_total_mercaderia DECIMAL(10,2) := 0;
    v_rec RECORD;
BEGIN
    SELECT id_proveedor INTO v_id_prov FROM proveedor WHERE distribuidora = 'Industrias Textiles del Lago' LIMIT 1;
    IF v_id_prov IS NULL THEN
        SELECT id_proveedor INTO v_id_prov FROM proveedor ORDER BY id_proveedor LIMIT 1;
    END IF;

    -- Verificar si la compra ya fue registrada
    SELECT id_compra INTO v_id_compra FROM compra WHERE numero_factura_proveedor = 'FAC-2026-00381';
    IF v_id_compra IS NULL THEN
        -- Crear Orden de Compra previa
        INSERT INTO orden_compra (id_proveedor, id_usuario, fecha_emision, total_estimado, estado)
        VALUES (v_id_prov, 1, '2026-10-15'::DATE - INTERVAL '3 days', 0.00, 'Recibida')
        RETURNING id_orden INTO v_id_orden;

        -- Crear Compra
        INSERT INTO compra (id_orden, id_proveedor, id_usuario, numero_factura_proveedor, fecha_ingreso, subtotal_mercaderia, gasto_flete, gasto_cargadores, total_compra)
        VALUES (v_id_orden, v_id_prov, 1, 'FAC-2026-00381', '2026-10-15', 0.00, 125.0, 45.0, 0.00)
        RETURNING id_compra INTO v_id_compra;

        -- Insertar detalles para los productos de las subcategorías correspondientes
        FOR v_rec IN (
            SELECT vp.id_variante, vp.costo_promedio, COALESCE(inv.stock_actual, 25) AS cantidad
            FROM variante_producto vp
            JOIN producto p ON vp.id_producto = p.id_producto
            JOIN subcategoria s ON p.id_subcategoria = s.id_subcategoria
            LEFT JOIN inventario_sucursal inv ON vp.id_variante = inv.id_variante AND inv.id_sucursal = 1
            WHERE s.nombre IN ('Toallas y Blancos', 'Chamarras y Abrigos')
        ) LOOP
            INSERT INTO detalle_orden_compra (id_orden, id_variante, cantidad_pedida, costo_pactado)
            VALUES (v_id_orden, v_rec.id_variante, v_rec.cantidad, v_rec.costo_promedio);

            INSERT INTO detalle_compra (id_compra, id_variante, cantidad_recibida, costo_unitario, subtotal)
            VALUES (v_id_compra, v_rec.id_variante, v_rec.cantidad, v_rec.costo_promedio, v_rec.cantidad * v_rec.costo_promedio);

            v_total_mercaderia := v_total_mercaderia + (v_rec.cantidad * v_rec.costo_promedio);
        END LOOP;

        -- Actualizar totales en orden y compra
        UPDATE orden_compra SET total_estimado = v_total_mercaderia WHERE id_orden = v_id_orden;
        UPDATE compra
        SET subtotal_mercaderia = v_total_mercaderia,
            total_compra = v_total_mercaderia + 125.0 + 45.0
        WHERE id_compra = v_id_compra;
    END IF;
END $$;

DO $$
DECLARE
    v_id_prov INT;
    v_id_orden INT;
    v_id_compra INT;
    v_total_mercaderia DECIMAL(10,2) := 0;
    v_rec RECORD;
BEGIN
    SELECT id_proveedor INTO v_id_prov FROM proveedor WHERE distribuidora = 'Juguetes Educativos y Novedades del Altiplano' LIMIT 1;
    IF v_id_prov IS NULL THEN
        SELECT id_proveedor INTO v_id_prov FROM proveedor ORDER BY id_proveedor LIMIT 1;
    END IF;

    -- Verificar si la compra ya fue registrada
    SELECT id_compra INTO v_id_compra FROM compra WHERE numero_factura_proveedor = 'FAC-2026-00412';
    IF v_id_compra IS NULL THEN
        -- Crear Orden de Compra previa
        INSERT INTO orden_compra (id_proveedor, id_usuario, fecha_emision, total_estimado, estado)
        VALUES (v_id_prov, 1, '2026-10-18'::DATE - INTERVAL '3 days', 0.00, 'Recibida')
        RETURNING id_orden INTO v_id_orden;

        -- Crear Compra
        INSERT INTO compra (id_orden, id_proveedor, id_usuario, numero_factura_proveedor, fecha_ingreso, subtotal_mercaderia, gasto_flete, gasto_cargadores, total_compra)
        VALUES (v_id_orden, v_id_prov, 1, 'FAC-2026-00412', '2026-10-18', 0.00, 95.0, 35.0, 0.00)
        RETURNING id_compra INTO v_id_compra;

        -- Insertar detalles para los productos de las subcategorías correspondientes
        FOR v_rec IN (
            SELECT vp.id_variante, vp.costo_promedio, COALESCE(inv.stock_actual, 25) AS cantidad
            FROM variante_producto vp
            JOIN producto p ON vp.id_producto = p.id_producto
            JOIN subcategoria s ON p.id_subcategoria = s.id_subcategoria
            LEFT JOIN inventario_sucursal inv ON vp.id_variante = inv.id_variante AND inv.id_sucursal = 1
            WHERE s.nombre IN ('Peluches', 'Juguetes Educativos y Figuras')
        ) LOOP
            INSERT INTO detalle_orden_compra (id_orden, id_variante, cantidad_pedida, costo_pactado)
            VALUES (v_id_orden, v_rec.id_variante, v_rec.cantidad, v_rec.costo_promedio);

            INSERT INTO detalle_compra (id_compra, id_variante, cantidad_recibida, costo_unitario, subtotal)
            VALUES (v_id_compra, v_rec.id_variante, v_rec.cantidad, v_rec.costo_promedio, v_rec.cantidad * v_rec.costo_promedio);

            v_total_mercaderia := v_total_mercaderia + (v_rec.cantidad * v_rec.costo_promedio);
        END LOOP;

        -- Actualizar totales en orden y compra
        UPDATE orden_compra SET total_estimado = v_total_mercaderia WHERE id_orden = v_id_orden;
        UPDATE compra
        SET subtotal_mercaderia = v_total_mercaderia,
            total_compra = v_total_mercaderia + 95.0 + 35.0
        WHERE id_compra = v_id_compra;
    END IF;
END $$;

DO $$
DECLARE
    v_id_prov INT;
    v_id_orden INT;
    v_id_compra INT;
    v_total_mercaderia DECIMAL(10,2) := 0;
    v_rec RECORD;
BEGIN
    SELECT id_proveedor INTO v_id_prov FROM proveedor WHERE distribuidora = 'Distribuidora Menaje y Hogar S.A.' LIMIT 1;
    IF v_id_prov IS NULL THEN
        SELECT id_proveedor INTO v_id_prov FROM proveedor ORDER BY id_proveedor LIMIT 1;
    END IF;

    -- Verificar si la compra ya fue registrada
    SELECT id_compra INTO v_id_compra FROM compra WHERE numero_factura_proveedor = 'FAC-2026-00529';
    IF v_id_compra IS NULL THEN
        -- Crear Orden de Compra previa
        INSERT INTO orden_compra (id_proveedor, id_usuario, fecha_emision, total_estimado, estado)
        VALUES (v_id_prov, 1, '2026-10-20'::DATE - INTERVAL '3 days', 0.00, 'Recibida')
        RETURNING id_orden INTO v_id_orden;

        -- Crear Compra
        INSERT INTO compra (id_orden, id_proveedor, id_usuario, numero_factura_proveedor, fecha_ingreso, subtotal_mercaderia, gasto_flete, gasto_cargadores, total_compra)
        VALUES (v_id_orden, v_id_prov, 1, 'FAC-2026-00529', '2026-10-20', 0.00, 140.0, 50.0, 0.00)
        RETURNING id_compra INTO v_id_compra;

        -- Insertar detalles para los productos de las subcategorías correspondientes
        FOR v_rec IN (
            SELECT vp.id_variante, vp.costo_promedio, COALESCE(inv.stock_actual, 25) AS cantidad
            FROM variante_producto vp
            JOIN producto p ON vp.id_producto = p.id_producto
            JOIN subcategoria s ON p.id_subcategoria = s.id_subcategoria
            LEFT JOIN inventario_sucursal inv ON vp.id_variante = inv.id_variante AND inv.id_sucursal = 1
            WHERE s.nombre IN ('Ollas y Baterías de Cocina', 'Servilletas y Mantelería')
        ) LOOP
            INSERT INTO detalle_orden_compra (id_orden, id_variante, cantidad_pedida, costo_pactado)
            VALUES (v_id_orden, v_rec.id_variante, v_rec.cantidad, v_rec.costo_promedio);

            INSERT INTO detalle_compra (id_compra, id_variante, cantidad_recibida, costo_unitario, subtotal)
            VALUES (v_id_compra, v_rec.id_variante, v_rec.cantidad, v_rec.costo_promedio, v_rec.cantidad * v_rec.costo_promedio);

            v_total_mercaderia := v_total_mercaderia + (v_rec.cantidad * v_rec.costo_promedio);
        END LOOP;

        -- Actualizar totales en orden y compra
        UPDATE orden_compra SET total_estimado = v_total_mercaderia WHERE id_orden = v_id_orden;
        UPDATE compra
        SET subtotal_mercaderia = v_total_mercaderia,
            total_compra = v_total_mercaderia + 140.0 + 50.0
        WHERE id_compra = v_id_compra;
    END IF;
END $$;

DO $$
DECLARE
    v_id_prov INT;
    v_id_orden INT;
    v_id_compra INT;
    v_total_mercaderia DECIMAL(10,2) := 0;
    v_rec RECORD;
BEGIN
    SELECT id_proveedor INTO v_id_prov FROM proveedor WHERE distribuidora = 'Importadora Cristalería y Porcelana Maya' LIMIT 1;
    IF v_id_prov IS NULL THEN
        SELECT id_proveedor INTO v_id_prov FROM proveedor ORDER BY id_proveedor LIMIT 1;
    END IF;

    -- Verificar si la compra ya fue registrada
    SELECT id_compra INTO v_id_compra FROM compra WHERE numero_factura_proveedor = 'FAC-2026-00618';
    IF v_id_compra IS NULL THEN
        -- Crear Orden de Compra previa
        INSERT INTO orden_compra (id_proveedor, id_usuario, fecha_emision, total_estimado, estado)
        VALUES (v_id_prov, 1, '2026-10-22'::DATE - INTERVAL '3 days', 0.00, 'Recibida')
        RETURNING id_orden INTO v_id_orden;

        -- Crear Compra
        INSERT INTO compra (id_orden, id_proveedor, id_usuario, numero_factura_proveedor, fecha_ingreso, subtotal_mercaderia, gasto_flete, gasto_cargadores, total_compra)
        VALUES (v_id_orden, v_id_prov, 1, 'FAC-2026-00618', '2026-10-22', 0.00, 110.0, 40.0, 0.00)
        RETURNING id_compra INTO v_id_compra;

        -- Insertar detalles para los productos de las subcategorías correspondientes
        FOR v_rec IN (
            SELECT vp.id_variante, vp.costo_promedio, COALESCE(inv.stock_actual, 25) AS cantidad
            FROM variante_producto vp
            JOIN producto p ON vp.id_producto = p.id_producto
            JOIN subcategoria s ON p.id_subcategoria = s.id_subcategoria
            LEFT JOIN inventario_sucursal inv ON vp.id_variante = inv.id_variante AND inv.id_sucursal = 1
            WHERE s.nombre IN ('Platos y Vajillas')
        ) LOOP
            INSERT INTO detalle_orden_compra (id_orden, id_variante, cantidad_pedida, costo_pactado)
            VALUES (v_id_orden, v_rec.id_variante, v_rec.cantidad, v_rec.costo_promedio);

            INSERT INTO detalle_compra (id_compra, id_variante, cantidad_recibida, costo_unitario, subtotal)
            VALUES (v_id_compra, v_rec.id_variante, v_rec.cantidad, v_rec.costo_promedio, v_rec.cantidad * v_rec.costo_promedio);

            v_total_mercaderia := v_total_mercaderia + (v_rec.cantidad * v_rec.costo_promedio);
        END LOOP;

        -- Actualizar totales en orden y compra
        UPDATE orden_compra SET total_estimado = v_total_mercaderia WHERE id_orden = v_id_orden;
        UPDATE compra
        SET subtotal_mercaderia = v_total_mercaderia,
            total_compra = v_total_mercaderia + 110.0 + 40.0
        WHERE id_compra = v_id_compra;
    END IF;
END $$;

DO $$
DECLARE
    v_id_prov INT;
    v_id_orden INT;
    v_id_compra INT;
    v_total_mercaderia DECIMAL(10,2) := 0;
    v_rec RECORD;
BEGIN
    SELECT id_proveedor INTO v_id_prov FROM proveedor WHERE distribuidora = 'Distribuidora de Cuidado y Cosméticos El Quetzal' LIMIT 1;
    IF v_id_prov IS NULL THEN
        SELECT id_proveedor INTO v_id_prov FROM proveedor ORDER BY id_proveedor LIMIT 1;
    END IF;

    -- Verificar si la compra ya fue registrada
    SELECT id_compra INTO v_id_compra FROM compra WHERE numero_factura_proveedor = 'FAC-2026-00744';
    IF v_id_compra IS NULL THEN
        -- Crear Orden de Compra previa
        INSERT INTO orden_compra (id_proveedor, id_usuario, fecha_emision, total_estimado, estado)
        VALUES (v_id_prov, 1, '2026-10-25'::DATE - INTERVAL '3 days', 0.00, 'Recibida')
        RETURNING id_orden INTO v_id_orden;

        -- Crear Compra
        INSERT INTO compra (id_orden, id_proveedor, id_usuario, numero_factura_proveedor, fecha_ingreso, subtotal_mercaderia, gasto_flete, gasto_cargadores, total_compra)
        VALUES (v_id_orden, v_id_prov, 1, 'FAC-2026-00744', '2026-10-25', 0.00, 80.0, 30.0, 0.00)
        RETURNING id_compra INTO v_id_compra;

        -- Insertar detalles para los productos de las subcategorías correspondientes
        FOR v_rec IN (
            SELECT vp.id_variante, vp.costo_promedio, COALESCE(inv.stock_actual, 25) AS cantidad
            FROM variante_producto vp
            JOIN producto p ON vp.id_producto = p.id_producto
            JOIN subcategoria s ON p.id_subcategoria = s.id_subcategoria
            LEFT JOIN inventario_sucursal inv ON vp.id_variante = inv.id_variante AND inv.id_sucursal = 1
            WHERE s.nombre IN ('Desodorantes e Higiene Corporal')
        ) LOOP
            INSERT INTO detalle_orden_compra (id_orden, id_variante, cantidad_pedida, costo_pactado)
            VALUES (v_id_orden, v_rec.id_variante, v_rec.cantidad, v_rec.costo_promedio);

            INSERT INTO detalle_compra (id_compra, id_variante, cantidad_recibida, costo_unitario, subtotal)
            VALUES (v_id_compra, v_rec.id_variante, v_rec.cantidad, v_rec.costo_promedio, v_rec.cantidad * v_rec.costo_promedio);

            v_total_mercaderia := v_total_mercaderia + (v_rec.cantidad * v_rec.costo_promedio);
        END LOOP;

        -- Actualizar totales en orden y compra
        UPDATE orden_compra SET total_estimado = v_total_mercaderia WHERE id_orden = v_id_orden;
        UPDATE compra
        SET subtotal_mercaderia = v_total_mercaderia,
            total_compra = v_total_mercaderia + 80.0 + 30.0
        WHERE id_compra = v_id_compra;
    END IF;
END $$;

DO $$
DECLARE
    v_id_prov INT;
    v_id_orden INT;
    v_id_compra INT;
    v_total_mercaderia DECIMAL(10,2) := 0;
    v_rec RECORD;
BEGIN
    SELECT id_proveedor INTO v_id_prov FROM proveedor WHERE distribuidora = 'Marroquinería y Accesorios Chapines' LIMIT 1;
    IF v_id_prov IS NULL THEN
        SELECT id_proveedor INTO v_id_prov FROM proveedor ORDER BY id_proveedor LIMIT 1;
    END IF;

    -- Verificar si la compra ya fue registrada
    SELECT id_compra INTO v_id_compra FROM compra WHERE numero_factura_proveedor = 'FAC-2026-00832';
    IF v_id_compra IS NULL THEN
        -- Crear Orden de Compra previa
        INSERT INTO orden_compra (id_proveedor, id_usuario, fecha_emision, total_estimado, estado)
        VALUES (v_id_prov, 1, '2026-10-28'::DATE - INTERVAL '3 days', 0.00, 'Recibida')
        RETURNING id_orden INTO v_id_orden;

        -- Crear Compra
        INSERT INTO compra (id_orden, id_proveedor, id_usuario, numero_factura_proveedor, fecha_ingreso, subtotal_mercaderia, gasto_flete, gasto_cargadores, total_compra)
        VALUES (v_id_orden, v_id_prov, 1, 'FAC-2026-00832', '2026-10-28', 0.00, 115.0, 40.0, 0.00)
        RETURNING id_compra INTO v_id_compra;

        -- Insertar detalles para los productos de las subcategorías correspondientes
        FOR v_rec IN (
            SELECT vp.id_variante, vp.costo_promedio, COALESCE(inv.stock_actual, 25) AS cantidad
            FROM variante_producto vp
            JOIN producto p ON vp.id_producto = p.id_producto
            JOIN subcategoria s ON p.id_subcategoria = s.id_subcategoria
            LEFT JOIN inventario_sucursal inv ON vp.id_variante = inv.id_variante AND inv.id_sucursal = 1
            WHERE s.nombre IN ('Bolsas y Mochilas', 'Carteras y Billeteras')
        ) LOOP
            INSERT INTO detalle_orden_compra (id_orden, id_variante, cantidad_pedida, costo_pactado)
            VALUES (v_id_orden, v_rec.id_variante, v_rec.cantidad, v_rec.costo_promedio);

            INSERT INTO detalle_compra (id_compra, id_variante, cantidad_recibida, costo_unitario, subtotal)
            VALUES (v_id_compra, v_rec.id_variante, v_rec.cantidad, v_rec.costo_promedio, v_rec.cantidad * v_rec.costo_promedio);

            v_total_mercaderia := v_total_mercaderia + (v_rec.cantidad * v_rec.costo_promedio);
        END LOOP;

        -- Actualizar totales en orden y compra
        UPDATE orden_compra SET total_estimado = v_total_mercaderia WHERE id_orden = v_id_orden;
        UPDATE compra
        SET subtotal_mercaderia = v_total_mercaderia,
            total_compra = v_total_mercaderia + 115.0 + 40.0
        WHERE id_compra = v_id_compra;
    END IF;
END $$;

-- 8. Sincronización de secuencias
SELECT setval('categoria_id_categoria_seq', COALESCE((SELECT MAX(id_categoria) FROM categoria), 0) + 1, false);
SELECT setval('subcategoria_id_subcategoria_seq', COALESCE((SELECT MAX(id_subcategoria) FROM subcategoria), 0) + 1, false);
SELECT setval('unidad_medida_id_unidad_seq', COALESCE((SELECT MAX(id_unidad) FROM unidad_medida), 0) + 1, false);
SELECT setval('producto_id_producto_seq', COALESCE((SELECT MAX(id_producto) FROM producto), 0) + 1, false);
SELECT setval('variante_producto_id_variante_seq', COALESCE((SELECT MAX(id_variante) FROM variante_producto), 0) + 1, false);
SELECT setval('inventario_sucursal_id_inventario_seq', COALESCE((SELECT MAX(id_inventario) FROM inventario_sucursal), 0) + 1, false);
SELECT setval('historial_precio_id_historial_seq', COALESCE((SELECT MAX(id_historial) FROM historial_precio), 0) + 1, false);
SELECT setval('cliente_id_cliente_seq', COALESCE((SELECT MAX(id_cliente) FROM cliente), 0) + 1, false);
SELECT setval('cliente_contacto_id_contacto_seq', COALESCE((SELECT MAX(id_contacto) FROM cliente_contacto), 0) + 1, false);
SELECT setval('proveedor_id_proveedor_seq', COALESCE((SELECT MAX(id_proveedor) FROM proveedor), 0) + 1, false);
SELECT setval('orden_compra_id_orden_seq', COALESCE((SELECT MAX(id_orden) FROM orden_compra), 0) + 1, false);
SELECT setval('detalle_orden_compra_id_detalle_orden_seq', COALESCE((SELECT MAX(id_detalle_orden) FROM detalle_orden_compra), 0) + 1, false);
SELECT setval('compra_id_compra_seq', COALESCE((SELECT MAX(id_compra) FROM compra), 0) + 1, false);
SELECT setval('detalle_compra_id_detalle_compra_seq', COALESCE((SELECT MAX(id_detalle_compra) FROM detalle_compra), 0) + 1, false);


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


SELECT setval('orden_compra_id_orden_seq', COALESCE((SELECT MAX(id_orden) FROM orden_compra), 0) + 1, false);
SELECT setval('detalle_orden_compra_id_detalle_orden_seq', COALESCE((SELECT MAX(id_detalle_orden) FROM detalle_orden_compra), 0) + 1, false);
SELECT setval('compra_id_compra_seq', COALESCE((SELECT MAX(id_compra) FROM compra), 0) + 1, false);
SELECT setval('detalle_compra_id_detalle_compra_seq', COALESCE((SELECT MAX(id_detalle_compra) FROM detalle_compra), 0) + 1, false);

SELECT setval('sync_cache_metadata_id_sync_seq', COALESCE((SELECT MAX(id_sync) FROM sync_cache_metadata), 0) + 1, false);
SELECT setval('sync_queue_id_sync_seq', COALESCE((SELECT MAX(id_sync) FROM sync_queue), 0) + 1, false);

-- ============================================================================
-- NOTA DE DESPLIEGUE
-- Para limpiar el volumen y aplicar esta base nueva:
--   docker compose down -v
--   docker compose up -d db
-- (borra el volumen postgres_data y re-ejecuta este init.sql desde cero)
-- ============================================================================

-- ============================================================================
-- IMÁGENES LOCALES DEL CATÁLOGO
-- ============================================================================
-- Imágenes locales del catálogo (idempotente)
UPDATE producto SET imagen_url = v.imagen_url
FROM (VALUES
  (1, '/img/productos/1.jpg'),
  (2, '/img/productos/2.jpg'),
  (3, '/img/productos/3.jpg'),
  (4, '/img/productos/4.jpg'),
  (5, '/img/productos/5.jpg'),
  (106, '/img/productos/106.jpg'),
  (107, '/img/productos/107.jpg'),
  (108, '/img/productos/108.jpg'),
  (109, '/img/productos/109.jpg'),
  (110, '/img/productos/110.jpg'),
  (111, '/img/productos/111.jpg'),
  (112, '/img/productos/112.jpg'),
  (113, '/img/productos/113.jpg'),
  (114, '/img/productos/114.jpg'),
  (115, '/img/productos/115.jpg'),
  (116, '/img/productos/116.jpg'),
  (117, '/img/productos/117.jpg'),
  (118, '/img/productos/118.jpg'),
  (119, '/img/productos/119.jpg'),
  (120, '/img/productos/120.jpg'),
  (121, '/img/productos/121.jpg'),
  (122, '/img/productos/122.jpg'),
  (123, '/img/productos/123.jpg'),
  (124, '/img/productos/124.jpg'),
  (125, '/img/productos/125.jpg'),
  (126, '/img/productos/126.jpg'),
  (127, '/img/productos/127.jpg'),
  (128, '/img/productos/128.jpg'),
  (129, '/img/productos/129.jpg'),
  (130, '/img/productos/130.jpg'),
  (131, '/img/productos/131.jpg'),
  (132, '/img/productos/132.jpg'),
  (133, '/img/productos/133.jpg'),
  (134, '/img/productos/134.jpg'),
  (135, '/img/productos/135.jpg'),
  (136, '/img/productos/136.jpg'),
  (137, '/img/productos/137.jpg'),
  (138, '/img/productos/138.jpg'),
  (139, '/img/productos/139.jpg'),
  (140, '/img/productos/140.jpg'),
  (141, '/img/productos/141.jpg'),
  (142, '/img/productos/142.jpg'),
  (143, '/img/productos/143.jpg'),
  (144, '/img/productos/144.jpg'),
  (145, '/img/productos/145.jpg'),
  (146, '/img/productos/146.jpg'),
  (147, '/img/productos/147.jpg'),
  (148, '/img/productos/148.jpg'),
  (149, '/img/productos/149.jpg'),
  (150, '/img/productos/150.jpg'),
  (151, '/img/productos/151.jpg'),
  (152, '/img/productos/152.jpg'),
  (153, '/img/productos/153.jpg'),
  (154, '/img/productos/154.jpg'),
  (155, '/img/productos/155.jpg'),
  (156, '/img/productos/156.jpg'),
  (157, '/img/productos/157.jpg'),
  (158, '/img/productos/158.jpg'),
  (159, '/img/productos/159.jpg'),
  (160, '/img/productos/160.jpg'),
  (161, '/img/productos/161.jpg'),
  (162, '/img/productos/162.jpg'),
  (163, '/img/productos/163.jpg'),
  (164, '/img/productos/164.jpg'),
  (165, '/img/productos/165.jpg'),
  (166, '/img/productos/166.jpg'),
  (167, '/img/productos/167.jpg'),
  (168, '/img/productos/168.jpg'),
  (169, '/img/productos/169.jpg'),
  (170, '/img/productos/170.jpg'),
  (171, '/img/productos/171.jpg'),
  (172, '/img/productos/172.jpg'),
  (173, '/img/productos/173.jpg'),
  (174, '/img/productos/174.jpg'),
  (175, '/img/productos/175.jpg'),
  (176, '/img/productos/176.jpg'),
  (177, '/img/productos/177.jpg'),
  (178, '/img/productos/178.jpg'),
  (179, '/img/productos/179.jpg'),
  (180, '/img/productos/180.jpg'),
  (181, '/img/productos/181.jpg'),
  (182, '/img/productos/182.jpg'),
  (183, '/img/productos/183.jpg'),
  (184, '/img/productos/184.jpg'),
  (185, '/img/productos/185.jpg'),
  (186, '/img/productos/186.jpg'),
  (187, '/img/productos/187.jpg'),
  (188, '/img/productos/188.jpg'),
  (189, '/img/productos/189.jpg'),
  (190, '/img/productos/190.jpg'),
  (191, '/img/productos/191.jpg'),
  (192, '/img/productos/192.jpg'),
  (193, '/img/productos/193.jpg'),
  (194, '/img/productos/194.jpg'),
  (195, '/img/productos/195.jpg'),
  (196, '/img/productos/196.jpg'),
  (197, '/img/productos/197.jpg'),
  (198, '/img/productos/198.jpg'),
  (199, '/img/productos/199.jpg'),
  (200, '/img/productos/200.jpg'),
  (201, '/img/productos/201.jpg'),
  (202, '/img/productos/202.jpg'),
  (203, '/img/productos/203.jpg'),
  (204, '/img/productos/204.jpg'),
  (205, '/img/productos/205.jpg')
) AS v(id_producto, imagen_url)
WHERE producto.id_producto = v.id_producto;
