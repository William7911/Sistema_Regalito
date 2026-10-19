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
    fecha_hora TIMESTAMP NOT NULL
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
    estado VARCHAR(20) NOT NULL CHECK (estado IN ('Activo', 'Inactivo'))
);

CREATE TABLE area_bodega (
    id_area SERIAL PRIMARY KEY,
    id_sucursal INT NOT NULL REFERENCES sucursal(id_sucursal),
    nombre_area VARCHAR(50) NOT NULL
);

CREATE TABLE departamento_geografico (
    id_departamento SERIAL PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL UNIQUE
);

CREATE TABLE municipio (
    id_municipio SERIAL PRIMARY KEY,
    id_departamento INT NOT NULL REFERENCES departamento_geografico(id_departamento),
    nombre VARCHAR(50) NOT NULL UNIQUE
);

CREATE TABLE tipo_cliente (
    id_tipo_cliente SERIAL PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL,
    descuento_predeterminado DECIMAL(5,2)
);

CREATE TABLE cliente (
    id_cliente SERIAL PRIMARY KEY,
    id_tipo_cliente INT NOT NULL REFERENCES tipo_cliente(id_tipo_cliente),
    id_municipio INT REFERENCES municipio(id_municipio),
    nit VARCHAR(15) NOT NULL,
    nombre_comercial VARCHAR(120) NOT NULL,
    direccion VARCHAR(200)
);

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
    nombre VARCHAR(50) NOT NULL UNIQUE
);

CREATE TABLE unidad_medida (
    id_unidad SERIAL PRIMARY KEY,
    codigo VARCHAR(10) NOT NULL UNIQUE,
    descripcion VARCHAR(50) NOT NULL
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
    descripcion VARCHAR(100) NOT NULL
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
    cantidad INT NOT NULL CHECK (cantidad >= 0),
    fecha_traslado TIMESTAMP NOT NULL
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
    nombre VARCHAR(30) NOT NULL
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
    direccion VARCHAR(150)
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
(5, 'Compras', 'COMPRA_EMITIR_ORDEN', 'Emitir órdenes de compra');

INSERT INTO rol_permiso (id_rol, id_permiso) VALUES
(1,1),(1,2),(1,3),(1,4),(1,5),
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

INSERT INTO departamento_geografico (id_departamento, nombre) VALUES
(1, 'Sololá'),
(2, 'Quetzaltenango');

INSERT INTO municipio (id_municipio, id_departamento, nombre) VALUES
(1, 1, 'Panajachel'),
(2, 1, 'Sololá'),
(3, 2, 'Quetzaltenango');

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

-- ============================================================================
-- NOTA DE DESPLIEGUE
-- Para limpiar el volumen y aplicar esta base nueva:
--   docker compose down -v
--   docker compose up -d db
-- (borra el volumen postgres_data y re-ejecuta este init.sql desde cero)
-- ============================================================================