-- ============================================================================
-- SEED DEMO DATA: CATÁLOGOS, 100 PRODUCTOS, 10 CLIENTES Y COMPRAS ASOCIADAS
-- ============================================================================
BEGIN;

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

COMMIT;