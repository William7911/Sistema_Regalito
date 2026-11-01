import os

# Categories and their subcategories
categories_data = [
    {
        "nombre": "Cristalería",
        "subcategorias": ["Platos y Vajillas"]
    },
    {
        "nombre": "Ropa",
        "subcategorias": ["Chamarras y Abrigos"]
    },
    {
        "nombre": "Juguetes",
        "subcategorias": ["Peluches", "Juguetes Educativos y Figuras"]
    },
    {
        "nombre": "Hogar",
        "subcategorias": ["Toallas y Blancos", "Ollas y Baterías de Cocina", "Servilletas y Mantelería"]
    },
    {
        "nombre": "Accesorios y Marroquinería",
        "subcategorias": ["Bolsas y Mochilas", "Carteras y Billeteras"]
    },
    {
        "nombre": "Cuidado Personal y Limpieza",
        "subcategorias": ["Desodorantes e Higiene Corporal"]
    }
]

# 10 Products for each of the 10 groups
products_groups = {
    # 1. TOALLAS
    "Toallas y Blancos": [
        {"nombre": "Toalla de Baño Cuerpo Entero 100% Algodón", "desc": "Toalla de felpa gruesa 70x140cm máxima absorción", "unidad": "UND", "color": "Blanco", "talla": "70x140cm", "costo": 45.00, "mayoreo": 65.00, "detalle": 75.00, "stock": 35, "min": 10, "area": 1},
        {"nombre": "Toalla de Mano Felpa Hotelera", "desc": "Toalla suave para manos y tocador 40x70cm", "unidad": "UND", "color": "Azul Marino", "talla": "40x70cm", "costo": 18.00, "mayoreo": 26.00, "detalle": 30.00, "stock": 40, "min": 10, "area": 1},
        {"nombre": "Toalla Facial Microfibra Extra Suave", "desc": "Toalla para rostro delicado de secado ultra rápido", "unidad": "UND", "color": "Celeste", "talla": "30x30cm", "costo": 8.00, "mayoreo": 12.00, "detalle": 15.00, "stock": 50, "min": 15, "area": 1},
        {"nombre": "Toalla Playera Grande Estampado Atitlán", "desc": "Toalla playera 90x170cm con diseño colorido del Lago de Atitlán", "unidad": "UND", "color": "Multicolor", "talla": "90x170cm", "costo": 60.00, "mayoreo": 85.00, "detalle": 98.00, "stock": 25, "min": 8, "area": 1},
        {"nombre": "Set de Toallas Familiar 3 Piezas", "desc": "Juego coordinado: cuerpo, mano y facial en caja de regalo", "unidad": "SET", "color": "Beige", "talla": "Set 3pz", "costo": 70.00, "mayoreo": 95.00, "detalle": 115.00, "stock": 20, "min": 5, "area": 2},
        {"nombre": "Toalla para Cabello Tipo Turbante", "desc": "Turbante de microfibra absorbente con botón de seguridad", "unidad": "UND", "color": "Rosa Pastel", "talla": "Unitalla", "costo": 15.00, "mayoreo": 22.00, "detalle": 28.00, "stock": 30, "min": 10, "area": 1},
        {"nombre": "Toalla de Cocina Absorbente Pack x3", "desc": "Paquete de 3 paños de cocina resistentes con cenefa decorativa", "unidad": "PKT", "color": "Estampado Frutas", "talla": "Pack 3", "costo": 22.00, "mayoreo": 32.00, "detalle": 38.00, "stock": 45, "min": 12, "area": 1},
        {"nombre": "Toalla Deportiva Microfibra con Estuche", "desc": "Toalla compacta para gimnasio y viaje con funda de transporte", "unidad": "UND", "color": "Gris/Verde", "talla": "50x100cm", "costo": 25.00, "mayoreo": 36.00, "detalle": 42.00, "stock": 30, "min": 8, "area": 1},
        {"nombre": "Toalla Infantil con Capucha Bordada Oso", "desc": "Toalla poncho para niños de felpa suave con orejitas", "unidad": "UND", "color": "Amarillo", "talla": "Infantil", "costo": 35.00, "mayoreo": 48.00, "detalle": 55.00, "stock": 25, "min": 6, "area": 1},
        {"nombre": "Toalla Tapete de Baño Antideslizante", "desc": "Piso de toalla afelpado para salida de regadera", "unidad": "UND", "color": "Gris Oxford", "talla": "50x80cm", "costo": 28.00, "mayoreo": 40.00, "detalle": 48.00, "stock": 30, "min": 8, "area": 2}
    ],

    # 2. PELUCHES
    "Peluches": [
        {"nombre": "Oso de Peluche Gigante 1 Metro con Moño", "desc": "Peluche de felpa extra suave premium relleno siliconado", "unidad": "UND", "color": "Café Claro", "talla": "100cm", "costo": 120.00, "mayoreo": 165.00, "detalle": 195.00, "stock": 15, "min": 4, "area": 1},
        {"nombre": "Peluche de Unicornio Mágico con Alas Tornasol", "desc": "Unicornio con detalles bordados y cuerno brillante", "unidad": "UND", "color": "Blanco/Rosa", "talla": "45cm", "costo": 48.00, "mayoreo": 68.00, "detalle": 78.00, "stock": 24, "min": 6, "area": 1},
        {"nombre": "Peluche de Perro San Bernardo Pelaje Largo", "desc": "Cachorro San Bernardo realista antialérgico", "unidad": "UND", "color": "Blanco/Café", "talla": "40cm", "costo": 52.00, "mayoreo": 72.00, "detalle": 85.00, "stock": 20, "min": 5, "area": 1},
        {"nombre": "Peluche Stitch Travieso 35cm", "desc": "Personaje Stitch clásico con orejas flexibles aterciopelado", "unidad": "UND", "color": "Azul", "talla": "35cm", "costo": 45.00, "mayoreo": 62.00, "detalle": 72.00, "stock": 30, "min": 8, "area": 1},
        {"nombre": "Peluche Pulpo Reversible de Emociones", "desc": "Pulpo reversible feliz / enojado de felpa suave", "unidad": "UND", "color": "Rosa/Azul", "talla": "20cm", "costo": 18.00, "mayoreo": 26.00, "detalle": 32.00, "stock": 50, "min": 15, "area": 3},
        {"nombre": "Peluche de Dinosaurio T-Rex Infantil", "desc": "Dinosaurio verde amigable y blandito para niños", "unidad": "UND", "color": "Verde", "talla": "38cm", "costo": 38.00, "mayoreo": 52.00, "detalle": 60.00, "stock": 22, "min": 6, "area": 1},
        {"nombre": "Peluche de Gato Dormilón Afelpado", "desc": "Gatito echado suave ideal para almohada o decoración", "unidad": "UND", "color": "Gris Atigrado", "talla": "50cm", "costo": 42.00, "mayoreo": 58.00, "detalle": 68.00, "stock": 25, "min": 6, "area": 1},
        {"nombre": "Peluche Conejo Orejas Caídas con Suéter", "desc": "Conejito tierno con vestimenta tejida desmontable", "unidad": "UND", "color": "Crema", "talla": "32cm", "costo": 36.00, "mayoreo": 50.00, "detalle": 58.00, "stock": 28, "min": 6, "area": 1},
        {"nombre": "Peluche Ave Quetzal Guatemalteco 30cm", "desc": "Quetzal representativo con cola larga y colores vivos", "unidad": "UND", "color": "Verde/Rojo", "talla": "30cm", "costo": 35.00, "mayoreo": 48.00, "detalle": 55.00, "stock": 35, "min": 10, "area": 1},
        {"nombre": "Peluche Elefante con Cobija para Bebé", "desc": "Elefantito afelpado con mantita térmica abrazable", "unidad": "UND", "color": "Gris/Celeste", "talla": "30cm", "costo": 55.00, "mayoreo": 75.00, "detalle": 88.00, "stock": 18, "min": 5, "area": 1}
    ],

    # 3. SERVILLETAS
    "Servilletas y Mantelería": [
        {"nombre": "Servilletas de Papel Doble Hoja Pack 100u", "desc": "Servilletas absorbentes texturizadas de celulosa pura", "unidad": "PKT", "color": "Blanco", "talla": "Pack 100", "costo": 6.50, "mayoreo": 9.00, "detalle": 11.00, "stock": 60, "min": 20, "area": 2},
        {"nombre": "Servilletas de Tela Algodón para Mesa Pack x6", "desc": "Juego de 6 servilletas de tela lavable con dobladillo fino", "unidad": "SET", "color": "Beige", "talla": "45x45cm", "costo": 32.00, "mayoreo": 45.00, "detalle": 55.00, "stock": 30, "min": 8, "area": 1},
        {"nombre": "Servilletas Decorativas Festivas Pack 50u", "desc": "Servilletas con estampados coloridos para fiestas y reuniones", "unidad": "PKT", "color": "Multicolor", "talla": "Pack 50", "costo": 8.00, "mayoreo": 12.00, "detalle": 15.00, "stock": 45, "min": 10, "area": 1},
        {"nombre": "Servilletas de Lino Fino para Eventos Pack x4", "desc": "Servilletas elegantes de lino ideales para cenas formales", "unidad": "SET", "color": "Blanco Hueso", "talla": "50x50cm", "costo": 40.00, "mayoreo": 56.00, "detalle": 68.00, "stock": 25, "min": 6, "area": 1},
        {"nombre": "Servilletas Cocktail Bar & Café Pack 100u", "desc": "Servilletas pequeñas cuadradas para bocadillos y bebidas", "unidad": "PKT", "color": "Negro", "talla": "25x25cm", "costo": 7.50, "mayoreo": 10.50, "detalle": 13.00, "stock": 50, "min": 15, "area": 3},
        {"nombre": "Servilletas de Cocina Rollo Jumbo Absorbente", "desc": "Toallín de cocina doble hoja resistente a líquidos y grasas", "unidad": "UND", "color": "Blanco", "talla": "Jumbo 200h", "costo": 12.00, "mayoreo": 16.50, "detalle": 19.50, "stock": 40, "min": 10, "area": 2},
        {"nombre": "Servilletas Kraft Ecológicas Biodegradables 200u", "desc": "Servilletas 100% recicladas sin blanqueadores químicos", "unidad": "PKT", "color": "Café Kraft", "talla": "Pack 200", "costo": 14.00, "mayoreo": 19.00, "detalle": 24.00, "stock": 35, "min": 10, "area": 2},
        {"nombre": "Servilletas Navideñas Tradicionales Pack x6", "desc": "Servilletas de tela con motivos navideños bordados", "unidad": "SET", "color": "Rojo/Verde", "talla": "40x40cm", "costo": 35.00, "mayoreo": 48.00, "detalle": 58.00, "stock": 20, "min": 5, "area": 1},
        {"nombre": "Servilletas Dispensador Restaurante Paquete 500u", "desc": "Servilleta doblada en V especial para dispensador de mesa", "unidad": "PKT", "color": "Blanco", "talla": "Pack 500", "costo": 22.00, "mayoreo": 30.00, "detalle": 36.00, "stock": 40, "min": 10, "area": 2},
        {"nombre": "Servilletas Típicas Tejidas en Telar Pack x4", "desc": "Servilletas artesanales tejidas a mano por artesanas de Sololá", "unidad": "SET", "color": "Típico Sololá", "talla": "38x38cm", "costo": 38.00, "mayoreo": 52.00, "detalle": 65.00, "stock": 25, "min": 6, "area": 1}
    ],

    # 4. BOLSAS
    "Bolsas y Mochilas": [
        {"nombre": "Bolsa de Tela Ecológica con Bordado Típico", "desc": "Bolsa totebag reutilizable resistente para compras y paseo", "unidad": "UND", "color": "Multicolor", "talla": "40x38cm", "costo": 20.00, "mayoreo": 28.00, "detalle": 35.00, "stock": 50, "min": 15, "area": 1},
        {"nombre": "Bolsa Térmica Lonchera Aislada", "desc": "Bolsa portaalimentos impermeable que mantiene temperatura", "unidad": "UND", "color": "Azul Marino", "talla": "Mediana", "costo": 28.00, "mayoreo": 38.00, "detalle": 45.00, "stock": 30, "min": 8, "area": 1},
        {"nombre": "Mochila Juvenil de Lona Casual", "desc": "Mochila resistente con compartimentos frontales para uso diario", "unidad": "UND", "color": "Negro", "talla": "Grande", "costo": 75.00, "mayoreo": 105.00, "detalle": 125.00, "stock": 25, "min": 6, "area": 1},
        {"nombre": "Bolsa de Malla Reforzada para Mercado", "desc": "Bolsa tradicional de plástico calado lavable de gran capacidad", "unidad": "UND", "color": "Verde", "talla": "Grande", "costo": 15.00, "mayoreo": 22.00, "detalle": 28.00, "stock": 45, "min": 10, "area": 2},
        {"nombre": "Bolsa de Regalo Premium Mate Grande", "desc": "Bolsa de cartón grueso laminado con cinta de seda y tarjeta", "unidad": "UND", "color": "Dorado Mate", "talla": "32x26x12cm", "costo": 7.00, "mayoreo": 10.00, "detalle": 14.00, "stock": 60, "min": 20, "area": 3},
        {"nombre": "Bolso Playero Impermeable Rayado", "desc": "Bolso amplio de lona náutica con cierre zipper y forro interior", "unidad": "UND", "color": "Azul/Blanco", "talla": "50x35cm", "costo": 45.00, "mayoreo": 62.00, "detalle": 75.00, "stock": 20, "min": 5, "area": 1},
        {"nombre": "Bolsa Riñonera Cruzada Deportiva", "desc": "Riñonera pechera impermeable con salida para audífonos", "unidad": "UND", "color": "Gris Carbón", "talla": "Ajustable", "costo": 32.00, "mayoreo": 44.00, "detalle": 52.00, "stock": 35, "min": 8, "area": 1},
        {"nombre": "Bolso Tote de Yute Natural con Asas Suaves", "desc": "Bolso ecológico de fibra vegetal con base reforzada", "unidad": "UND", "color": "Natural", "talla": "42x35x15cm", "costo": 35.00, "mayoreo": 48.00, "detalle": 58.00, "stock": 28, "min": 7, "area": 1},
        {"nombre": "Maletín Porta Laptop Acolchado 15.6 Pulgadas", "desc": "Funda maletín con protección antigolpes y correa al hombro", "unidad": "UND", "color": "Negro/Gris", "talla": "15.6 pulg", "costo": 68.00, "mayoreo": 95.00, "detalle": 115.00, "stock": 22, "min": 5, "area": 1},
        {"nombre": "Bolsa Plegable Reutilizable de Bolsillo", "desc": "Bolsa de nylon impermeable que se dobla en tamaño llavero", "unidad": "UND", "color": "Estampado Flores", "talla": "Compacta", "costo": 8.00, "mayoreo": 12.00, "detalle": 16.00, "stock": 55, "min": 15, "area": 3}
    ],

    # 5. OLLAS
    "Ollas y Baterías de Cocina": [
        {"nombre": "Olla de Presión de Aluminio Reforzado 6 Litros", "desc": "Olla exprés con doble válvula de seguridad y asas frías", "unidad": "UND", "color": "Plata", "talla": "6 Litros", "costo": 145.00, "mayoreo": 195.00, "detalle": 225.00, "stock": 18, "min": 5, "area": 1},
        {"nombre": "Olla Arrocera Antiadherente con Tapa de Vidrio", "desc": "Olla con revestimiento de teflón y pomo aislante 24cm", "unidad": "UND", "color": "Negro", "talla": "24cm / 4L", "costo": 72.00, "mayoreo": 98.00, "detalle": 115.00, "stock": 20, "min": 5, "area": 1},
        {"nombre": "Olla Vaporera Tamalera de Gran Capacidad 20L", "desc": "Olla tamalera de aluminio con rejilla divisoria desmontable", "unidad": "UND", "color": "Aluminio", "talla": "20 Litros", "costo": 125.00, "mayoreo": 165.00, "detalle": 190.00, "stock": 15, "min": 4, "area": 2},
        {"nombre": "Batería de Ollas Acero Inoxidable 5 Piezas", "desc": "Set de 3 ollas con tapas de vidrio templado y 2 cacerolas", "unidad": "SET", "color": "Acero Espejo", "talla": "Batería 5pz", "costo": 210.00, "mayoreo": 285.00, "detalle": 335.00, "stock": 12, "min": 3, "area": 1},
        {"nombre": "Olla Sopera Alta 10 Litros para Caldos", "desc": "Olla comercial profunda con remaches dobles reforzados", "unidad": "UND", "color": "Plata", "talla": "10 Litros", "costo": 85.00, "mayoreo": 115.00, "detalle": 135.00, "stock": 18, "min": 5, "area": 2},
        {"nombre": "Olla Holandesa de Cerámica Esmaltada 4L", "desc": "Cacerola gruesa de hierro fundido esmaltado ideal para horno", "unidad": "UND", "color": "Rojo Cereza", "talla": "4 Litros", "costo": 160.00, "mayoreo": 215.00, "detalle": 250.00, "stock": 10, "min": 3, "area": 1},
        {"nombre": "Olla Sartén Wok Antiadherente 28cm", "desc": "Wok hondo con fondo difusor de calor para salteados", "unidad": "UND", "color": "Negro Granito", "talla": "28cm", "costo": 65.00, "mayoreo": 88.00, "detalle": 105.00, "stock": 22, "min": 6, "area": 1},
        {"nombre": "Olla Lechera con Asa Aislante y Pico 2L", "desc": "Pocillo lechero de aluminio inoxidable vertedor antigoteo", "unidad": "UND", "color": "Acero", "talla": "2 Litros", "costo": 28.00, "mayoreo": 38.00, "detalle": 46.00, "stock": 30, "min": 8, "area": 1},
        {"nombre": "Olla de Barro Curado Tradicional 5 Litros", "desc": "Olla artesanal curada para frijoles y cocidos típicos", "unidad": "UND", "color": "Barro Natural", "talla": "5 Litros", "costo": 45.00, "mayoreo": 62.00, "detalle": 75.00, "stock": 20, "min": 5, "area": 2},
        {"nombre": "Cacerola Olla de Granito con Mango Soft-Touch", "desc": "Olla mediana con revestimiento mineral piedra anti rayones", "unidad": "UND", "color": "Gris Moteado", "talla": "20cm / 2.5L", "costo": 55.00, "mayoreo": 75.00, "detalle": 89.00, "stock": 24, "min": 6, "area": 1}
    ],

    # 6. PLATOS
    "Platos y Vajillas": [
        {"nombre": "Juego de Platos Tendidos Porcelana Blanca 6pz", "desc": "Set de 6 platos extendidos de porcelana lisa para mesa formal", "unidad": "SET", "color": "Blanco", "talla": "27cm x 6", "costo": 65.00, "mayoreo": 88.00, "detalle": 105.00, "stock": 25, "min": 6, "area": 1},
        {"nombre": "Plato Hondo Sencillo para Caldos y Sopas", "desc": "Plato hondo hondo de porcelana apto para microondas y lavavajillas", "unidad": "UND", "color": "Blanco", "talla": "22cm", "costo": 9.00, "mayoreo": 13.00, "detalle": 16.00, "stock": 60, "min": 15, "area": 1},
        {"nombre": "Plato Pastelero Cerámica con Filete Dorado", "desc": "Plato de postre fino con orilla decorada en oro", "unidad": "UND", "color": "Blanco/Oro", "talla": "19cm", "costo": 11.00, "mayoreo": 16.00, "detalle": 20.00, "stock": 45, "min": 12, "area": 1},
        {"nombre": "Plato Base Decorativo de Melamina Labrada 33cm", "desc": "Bajo plato de presentación con relieve barroco para eventos", "unidad": "UND", "color": "Dorado Metálico", "talla": "33cm", "costo": 16.00, "mayoreo": 23.00, "detalle": 28.00, "stock": 40, "min": 10, "area": 1},
        {"nombre": "Plato Botanero Dividido 3 Secciones Cerámica", "desc": "Plato para pasabocas, dips y boquitas con compartimentos", "unidad": "UND", "color": "Blanco", "talla": "25x15cm", "costo": 22.00, "mayoreo": 30.00, "detalle": 38.00, "stock": 30, "min": 8, "area": 1},
        {"nombre": "Plato Infantil Anticaídas con Divisiones y Ventosa", "desc": "Plato de silicón grado alimentario con base fijadora antideslizante", "unidad": "UND", "color": "Azul/Verde", "talla": "Infantil", "costo": 25.00, "mayoreo": 35.00, "detalle": 42.00, "stock": 28, "min": 6, "area": 1},
        {"nombre": "Plato Trinche Melamina Comercial Pack x6", "desc": "Platos irrompibles de alta resistencia para comedor y restaurante", "unidad": "SET", "color": "Blanco", "talla": "Pack 6pz", "costo": 42.00, "mayoreo": 58.00, "detalle": 70.00, "stock": 35, "min": 10, "area": 2},
        {"nombre": "Bandeja Plato de Servir Ovalado Porcelana 36cm", "desc": "Fuente amplia para servir carnes, asados y ensaladas", "unidad": "UND", "color": "Blanco", "talla": "36x24cm", "costo": 30.00, "mayoreo": 42.00, "detalle": 52.00, "stock": 20, "min": 5, "area": 1},
        {"nombre": "Plato Tendido Cuadrado Cerámica Contemporánea", "desc": "Plato moderno con bordes rectos acabado negro mate", "unidad": "UND", "color": "Negro Mate", "talla": "25x25cm", "costo": 15.00, "mayoreo": 22.00, "detalle": 27.00, "stock": 35, "min": 8, "area": 1},
        {"nombre": "Plato Hondo Artesanal de Barro Vidriado", "desc": "Plato rústico esmaltado libre de plomo para comida guatemalteca", "unidad": "UND", "color": "Café Típico", "talla": "20cm", "costo": 12.00, "mayoreo": 17.00, "detalle": 22.00, "stock": 40, "min": 10, "area": 2}
    ],

    # 7. CHAMARRAS
    "Chamarras y Abrigos": [
        {"nombre": "Chamarra Rompevientos Impermeable con Capucha", "desc": "Chamarra ligera repelente al agua y viento con forro transpirable", "unidad": "UND", "color": "Azul Marino", "talla": "M", "costo": 95.00, "mayoreo": 130.00, "detalle": 155.00, "stock": 24, "min": 6, "area": 1},
        {"nombre": "Chamarra Térmica de Pluma Sintética Acolchada", "desc": "Chamarra acolchada ultraliviana para bajas temperaturas", "unidad": "UND", "color": "Negro", "talla": "L", "costo": 130.00, "mayoreo": 175.00, "detalle": 210.00, "stock": 20, "min": 5, "area": 1},
        {"nombre": "Chamarra Biker Cuero Sintético Unisex", "desc": "Chamarra moderna estilo motociclista con broches y zipper", "unidad": "UND", "color": "Café Oscuro", "talla": "M", "costo": 140.00, "mayoreo": 190.00, "detalle": 230.00, "stock": 18, "min": 4, "area": 1},
        {"nombre": "Chamarra Deportiva Casual con Zipper Completo", "desc": "Chamarra de algodón perchado con puños y cintura elástica", "unidad": "UND", "color": "Gris Jaspe", "talla": "L", "costo": 78.00, "mayoreo": 105.00, "detalle": 125.00, "stock": 25, "min": 6, "area": 1},
        {"nombre": "Chamarra de Mezclilla Denim Tradicional Unisex", "desc": "Chamarra de lona jeans resistente con botones metálicos", "unidad": "UND", "color": "Azul Clásico", "talla": "M", "costo": 110.00, "mayoreo": 150.00, "detalle": 180.00, "stock": 22, "min": 5, "area": 1},
        {"nombre": "Chamarra Polar Térmica Cuello Alto para Frío", "desc": "Chamarra de microfleece suave antipilling con bolsillos", "unidad": "UND", "color": "Vino Tinto", "talla": "S", "costo": 65.00, "mayoreo": 90.00, "detalle": 110.00, "stock": 28, "min": 7, "area": 1},
        {"nombre": "Chamarra Infantil Acolchada con Gorro de Orejitas", "desc": "Abrigo tierno para niños con forro suave antialérgico", "unidad": "UND", "color": "Amarillo Mostaza", "talla": "Talla 6", "costo": 70.00, "mayoreo": 98.00, "detalle": 118.00, "stock": 20, "min": 5, "area": 1},
        {"nombre": "Chaleco Chamarra Acolchado sin Mangas", "desc": "Chaleco abrigador repelente al agua para movilidad cómoda", "unidad": "UND", "color": "Azul Petróleo", "talla": "XL", "costo": 75.00, "mayoreo": 105.00, "detalle": 125.00, "stock": 22, "min": 6, "area": 1},
        {"nombre": "Chamarra Parka Larga con Forro de Borrego", "desc": "Parka larga con forro afelpado interior para clima frío", "unidad": "UND", "color": "Verde Militar", "talla": "L", "costo": 165.00, "mayoreo": 225.00, "detalle": 265.00, "stock": 15, "min": 4, "area": 1},
        {"nombre": "Chamarra Suéter de Lana con Forro Interior", "desc": "Prenda de lana tejida artesanal con botones de madera", "unidad": "UND", "color": "Gris/Blanco", "talla": "M", "costo": 105.00, "mayoreo": 145.00, "detalle": 175.00, "stock": 20, "min": 5, "area": 1}
    ],

    # 8. DESODORANTES
    "Desodorantes e Higiene Corporal": [
        {"nombre": "Desodorante Antitranspirante Roll-On Clásico 50ml", "desc": "Protección contra sudor y mal olor durante 24 horas", "unidad": "UND", "color": "Blanco", "talla": "50ml", "costo": 11.50, "mayoreo": 16.00, "detalle": 20.00, "stock": 50, "min": 15, "area": 3},
        {"nombre": "Desodorante en Aerosol Protección Seca 150ml", "desc": "Spray seco sin residuos blancos fragancia fresca", "unidad": "UND", "color": "Azul", "talla": "150ml", "costo": 18.00, "mayoreo": 25.00, "detalle": 30.00, "stock": 45, "min": 12, "area": 1},
        {"nombre": "Desodorante en Barra Sport Duración 48h", "desc": "Barra sólida masculina para deportistas máxima protección", "unidad": "UND", "color": "Verde Sport", "talla": "85g", "costo": 16.50, "mayoreo": 23.00, "detalle": 28.00, "stock": 40, "min": 10, "area": 1},
        {"nombre": "Desodorante Natural Piedra de Alumbre 120g", "desc": "Cristal mineral 100% natural antibacterial sin químicos", "unidad": "UND", "color": "Transparente", "talla": "120g", "costo": 19.00, "mayoreo": 27.00, "detalle": 35.00, "stock": 35, "min": 10, "area": 1},
        {"nombre": "Desodorante Roll-On Aclarador y Suavizante 50ml", "desc": "Fórmula con perla hidrolizada que unifica el tono de piel", "unidad": "UND", "color": "Rosa", "talla": "50ml", "costo": 13.00, "mayoreo": 18.00, "detalle": 22.00, "stock": 40, "min": 10, "area": 1},
        {"nombre": "Desodorante en Gel Transparente Antitranspirante", "desc": "Gel refrescante de secado instantáneo sin manchas en ropa", "unidad": "UND", "color": "Azul Claro", "talla": "113g", "costo": 20.00, "mayoreo": 28.00, "detalle": 34.00, "stock": 35, "min": 10, "area": 1},
        {"nombre": "Body Spray Desodorante Fragancia Marina 200ml", "desc": "Aerosol corporal diario aroma fresco masculino", "unidad": "UND", "color": "Celeste", "talla": "200ml", "costo": 15.00, "mayoreo": 21.00, "detalle": 26.00, "stock": 42, "min": 10, "area": 1},
        {"nombre": "Desodorante Crema Antitranspirante Piel Sensible 60g", "desc": "Crema suave con aloe vera para pieles reactivas sin alcohol", "unidad": "UND", "color": "Blanco", "talla": "60g", "costo": 14.50, "mayoreo": 20.00, "detalle": 25.00, "stock": 38, "min": 10, "area": 1},
        {"nombre": "Desodorante Roll-On Carbón Activado 50ml", "desc": "Fórmula purificante con carbón activado neutralizador de olor", "unidad": "UND", "color": "Negro", "talla": "50ml", "costo": 13.50, "mayoreo": 19.00, "detalle": 23.00, "stock": 45, "min": 12, "area": 3},
        {"nombre": "Desodorante Hipoalergénico Cero Aluminio 75ml", "desc": "Roll-on orgánico con aceites esenciales naturales", "unidad": "UND", "color": "Verde Menta", "talla": "75ml", "costo": 17.00, "mayoreo": 24.00, "detalle": 30.00, "stock": 32, "min": 8, "area": 1}
    ],

    # 9. JUGUETES
    "Juguetes Educativos y Figuras": [
        {"nombre": "Juego de Bloques de Construcción Didácticos 150pz", "desc": "Bloques plásticos de ensamble en balde plástico con tapa", "unidad": "UND", "color": "Multicolor", "talla": "150 Piezas", "costo": 45.00, "mayoreo": 65.00, "detalle": 78.00, "stock": 25, "min": 6, "area": 1},
        {"nombre": "Carro a Control Remoto Todo Terreno Recargable", "desc": "Vehículo 4x4 con suspensión alta y batería USB incluida", "unidad": "UND", "color": "Rojo Metálico", "talla": "Escala 1:16", "costo": 90.00, "mayoreo": 125.00, "detalle": 150.00, "stock": 18, "min": 5, "area": 1},
        {"nombre": "Rompecabezas Didáctico de Madera Mapa de Guatemala", "desc": "Puzzle de madera con los 22 departamentos y cabeceras", "unidad": "UND", "color": "Multicolor", "talla": "30x40cm", "costo": 22.00, "mayoreo": 32.00, "detalle": 40.00, "stock": 35, "min": 10, "area": 1},
        {"nombre": "Pista de Carreras con Lanzador y 2 Autos Metálicos", "desc": "Pista con curva peraltada y doble loop para carritos de metal", "unidad": "UND", "color": "Naranja/Azul", "talla": "Pista 1.8m", "costo": 55.00, "mayoreo": 78.00, "detalle": 95.00, "stock": 20, "min": 5, "area": 1},
        {"nombre": "Juego de Mesa de Estrategia Familiar", "desc": "Juego de mesa clásico de finanzas y propiedades en español", "unidad": "UND", "color": "Multicolor", "talla": "Caja Grande", "costo": 42.00, "mayoreo": 60.00, "detalle": 72.00, "stock": 24, "min": 6, "area": 1},
        {"nombre": "Set de Masa no Tóxica 12 Colores con Moldes", "desc": "Plastilina moldeable perfumada segura para niños pequeños", "unidad": "SET", "color": "12 Colores", "talla": "Set Completo", "costo": 18.00, "mayoreo": 26.00, "detalle": 32.00, "stock": 45, "min": 12, "area": 1},
        {"nombre": "Figura de Acción Súper Héroe Articulada 30cm", "desc": "Muñeco articulado con luces y sonidos de combate", "unidad": "UND", "color": "Azul/Rojo", "talla": "30cm", "costo": 38.00, "mayoreo": 52.00, "detalle": 65.00, "stock": 30, "min": 8, "area": 1},
        {"nombre": "Juego de Té y Pastelería Infantil 14 Piezas", "desc": "Juego de tacitas de té, tetera y platitos de colores para niñas", "unidad": "SET", "color": "Tonos Pastel", "talla": "14 Piezas", "costo": 28.00, "mayoreo": 40.00, "detalle": 48.00, "stock": 25, "min": 6, "area": 1},
        {"nombre": "Pistola de Burbujas Eléctrica con Luz LED", "desc": "Lanzador automático que genera cientos de burbujas por minuto", "unidad": "UND", "color": "Celeste", "talla": "Pistola + Solución", "costo": 25.00, "mayoreo": 36.00, "detalle": 44.00, "stock": 32, "min": 8, "area": 3},
        {"nombre": "Cocinita de Juguete con Sonidos y Accesorios", "desc": "Mini cocina infantil con estufa que enciende luz y sartencitos", "unidad": "UND", "color": "Rosa/Blanco", "talla": "Mediana", "costo": 98.00, "mayoreo": 135.00, "detalle": 160.00, "stock": 14, "min": 4, "area": 1}
    ],

    # 10. CARTERAS O BILLETERAS
    "Carteras y Billeteras": [
        {"nombre": "Billetera de Cuero Auténtico Plegable para Caballero", "desc": "Billetera bifold con tarjetero, billetero doble y ventana para ID", "unidad": "UND", "color": "Café Oscuro", "talla": "Clásica", "costo": 48.00, "mayoreo": 68.00, "detalle": 85.00, "stock": 30, "min": 8, "area": 1},
        {"nombre": "Cartera Larga para Dama con Cierre y Asa", "desc": "Billetera clutch con compartimento para billetes, monedas y celular", "unidad": "UND", "color": "Rojo Borgoña", "talla": "20x10cm", "costo": 45.00, "mayoreo": 64.00, "detalle": 78.00, "stock": 28, "min": 7, "area": 1},
        {"nombre": "Billetera Slim Minimalista con Bloqueo RFID", "desc": "Billetera delgada de bolsillo con protección magnética y clip", "unidad": "UND", "color": "Negro", "talla": "Slim", "costo": 32.00, "mayoreo": 45.00, "detalle": 55.00, "stock": 40, "min": 10, "area": 3},
        {"nombre": "Monedero Cartera Pequeño con Broche Metálico", "desc": "Monedero de cuero sintético suave con forro interior", "unidad": "UND", "color": "Café Claro", "talla": "10x8cm", "costo": 10.00, "mayoreo": 15.00, "detalle": 19.00, "stock": 50, "min": 15, "area": 3},
        {"nombre": "Billetera Trifold Deportiva de Lona con Cierre", "desc": "Billetera triple pliegue con cierre de velcro resistente al agua", "unidad": "UND", "color": "Azul Marino", "talla": "Trifold", "costo": 18.00, "mayoreo": 26.00, "detalle": 32.00, "stock": 35, "min": 8, "area": 1},
        {"nombre": "Cartera Dama con Diseños Típicos de Telar", "desc": "Cartera con aplicación de telar bordado típico de Sololá", "unidad": "UND", "color": "Multicolor Típico", "talla": "19x10cm", "costo": 40.00, "mayoreo": 56.00, "detalle": 68.00, "stock": 25, "min": 6, "area": 1},
        {"nombre": "Cartera Tipo Sobre de Fiesta con Cadena Dorada", "desc": "Bolso de mano para eventos con cadena desmontable elegante", "unidad": "UND", "color": "Negro Elegante", "talla": "24x14cm", "costo": 38.00, "mayoreo": 54.00, "detalle": 65.00, "stock": 22, "min": 5, "area": 1},
        {"nombre": "Billetera Juvenil con Estampado Urbano", "desc": "Billetera de material sintético resistente para jóvenes", "unidad": "UND", "color": "Gris Grafiti", "talla": "Bifold", "costo": 20.00, "mayoreo": 28.00, "detalle": 35.00, "stock": 35, "min": 8, "area": 1},
        {"nombre": "Tarjetero Pop-Up Automático de Aluminio", "desc": "Portatarjetas con expulsador automático y cubierta de piel", "unidad": "UND", "color": "Plata/Negro", "talla": "6 Tarjetas", "costo": 35.00, "mayoreo": 48.00, "detalle": 60.00, "stock": 30, "min": 8, "area": 3},
        {"nombre": "Cartera Bandolera Pequeña para Celular y Dinero", "desc": "Minibolso cruzado para dama con correa ajustable práctica", "unidad": "UND", "color": "Mostaza", "talla": "18x11cm", "costo": 36.00, "mayoreo": 50.00, "detalle": 62.00, "stock": 26, "min": 6, "area": 1}
    ]
}

# 10 Clients
clients_data = [
    {
        "nit": "CF-1001",
        "nombre": "Consumidor Final Mostrador Panajachel",
        "tipo": 1, # Consumidor Final
        "muni": 1, # Panajachel
        "dir": "Calle Santander, Panajachel",
        "tel": "5522-1001",
        "email": "cf.panajachel@cliente.gt"
    },
    {
        "nit": "5489623-1",
        "nombre": "Abarrotería y Variedades El Atardecer",
        "tipo": 2, # Minorista
        "muni": 1, # Panajachel
        "dir": "Calle Principal Callejón Don Fidel, Panajachel",
        "tel": "7762-4411",
        "email": "atardecer.ventas@gmail.com"
    },
    {
        "nit": "8912345-6",
        "nombre": "Hotel y Restaurante Jardines de Atitlán",
        "tipo": 3, # Mayorista
        "muni": 1, # Panajachel
        "dir": "Playa Pública Sector Poniente, Panajachel",
        "tel": "7762-2890",
        "email": "compras@jardinesatitlan.com"
    },
    {
        "nit": "4521789-0",
        "nombre": "Comercial La Bendición de Occidente",
        "tipo": 3, # Mayorista
        "muni": 2, # Sololá
        "dir": "4ta Avenida y 3ra Calle Zona 1, Sololá",
        "tel": "7765-3312",
        "email": "labendicion.solola@yahoo.com"
    },
    {
        "nit": "7823419-4",
        "nombre": "Novedades y Regalos San Antonio",
        "tipo": 2, # Minorista
        "muni": 3, # Quetzaltenango
        "dir": "12 Avenida 5-20 Zona 1, Quetzaltenango",
        "tel": "7761-8844",
        "email": "novedades.sanantonio@xela.gt"
    },
    {
        "nit": "3165489-7",
        "nombre": "Cristalería y Hogar Doña Elena",
        "tipo": 2, # Minorista
        "muni": 29, # Chimaltenango
        "dir": "Calle Real del Comercio Zona 2, Chimaltenango",
        "tel": "7839-5566",
        "email": "cristaleria.donaelena@gmail.com"
    },
    {
        "nit": "6291845-2",
        "nombre": "Hotel Posada Los Volcanes S.A.",
        "tipo": 3, # Mayorista
        "muni": 221, # Antigua Guatemala
        "dir": "5ta Avenida Norte No. 14, Antigua Guatemala",
        "tel": "7832-7799",
        "email": "adquisiciones@posadavolcanes.gt"
    },
    {
        "nit": "9134782-8",
        "nombre": "Distribuidora El Regalito Metropolitano",
        "tipo": 3, # Mayorista
        "muni": 77, # Guatemala
        "dir": "Calzada Roosevelt 22-50 Zona 11, Ciudad de Guatemala",
        "tel": "2471-9900",
        "email": "contacto@regalitometro.com.gt"
    },
    {
        "nit": "1029384-5",
        "nombre": "Carmen Alicia Xicay Mendoza",
        "tipo": 1, # Consumidor Final
        "muni": 1, # Panajachel
        "dir": "Barrio Monterrey, Panajachel, Sololá",
        "tel": "5899-4412",
        "email": "carmen.xicay@gmail.com"
    },
    {
        "nit": "7349182-3",
        "nombre": "Mario Roberto Tzunún Cabrera",
        "tipo": 1, # Consumidor Final
        "muni": 2, # Sololá
        "dir": "Cantón San Bartolo, Sololá",
        "tel": "4211-7788",
        "email": "mario.tzunun@outlook.com"
    }
]

# 6 New Suppliers to support the 10 requested product lines
suppliers_data = [
    {
        "id": 5,
        "contacto": "Carlos Enrique Gómez",
        "distribuidora": "Distribuidora Menaje y Hogar S.A.",
        "tel": "7762-1122",
        "correo": "ventas@menajeyhogar.com.gt",
        "cuenta": "4567-890123-4",
        "dir": "Km 138 Carretera Interamericana, Sololá"
    },
    {
        "id": 6,
        "contacto": "Marta Lidia Morales",
        "distribuidora": "Industrias Textiles del Lago",
        "tel": "7765-8899",
        "correo": "pedidos@textilesdellago.gt",
        "cuenta": "1234-987654-1",
        "dir": "Calle Real de la Laguna, Panajachel, Sololá"
    },
    {
        "id": 7,
        "contacto": "Jorge Mario Soto",
        "distribuidora": "Importadora Cristalería y Porcelana Maya",
        "tel": "2334-5566",
        "correo": "ventas@cristaleriamaya.com.gt",
        "cuenta": "7890-123456-2",
        "dir": "Zona 12 Industrial, Ciudad de Guatemala"
    },
    {
        "id": 8,
        "contacto": "Patricia Elizabeth Ruiz",
        "distribuidora": "Distribuidora de Cuidado y Cosméticos El Quetzal",
        "tel": "7761-4433",
        "correo": "contacto@cosmeticoselquetzal.gt",
        "cuenta": "3456-112233-5",
        "dir": "Zona 3 Las Rosas, Quetzaltenango"
    },
    {
        "id": 9,
        "contacto": "Roberto Vásquez Fuentes",
        "distribuidora": "Marroquinería y Accesorios Chapines",
        "tel": "7832-1144",
        "correo": "ventas@marroquineriachapina.gt",
        "cuenta": "9012-334455-8",
        "dir": "Calle del Arco No. 25, Antigua Guatemala"
    },
    {
        "id": 10,
        "contacto": "Lorena Astrid Estrada",
        "distribuidora": "Juguetes Educativos y Novedades del Altiplano",
        "tel": "7763-9988",
        "correo": "info@juguetesaltiplano.gt",
        "cuenta": "5678-223344-9",
        "dir": "Zona 1 Centro, Quetzaltenango"
    }
]

# Purchases mapping: Supplier -> list of subcategory names
purchases_plan = [
    {
        "orden_id": 1,
        "compra_id": 1,
        "distribuidora": "Industrias Textiles del Lago",
        "factura": "FAC-2026-00381",
        "fecha": "2026-10-15",
        "flete": 125.00,
        "cargadores": 45.00,
        "subcategorias": ["Toallas y Blancos", "Chamarras y Abrigos"]
    },
    {
        "orden_id": 2,
        "compra_id": 2,
        "distribuidora": "Juguetes Educativos y Novedades del Altiplano",
        "factura": "FAC-2026-00412",
        "fecha": "2026-10-18",
        "flete": 95.00,
        "cargadores": 35.00,
        "subcategorias": ["Peluches", "Juguetes Educativos y Figuras"]
    },
    {
        "orden_id": 3,
        "compra_id": 3,
        "distribuidora": "Distribuidora Menaje y Hogar S.A.",
        "factura": "FAC-2026-00529",
        "fecha": "2026-10-20",
        "flete": 140.00,
        "cargadores": 50.00,
        "subcategorias": ["Ollas y Baterías de Cocina", "Servilletas y Mantelería"]
    },
    {
        "orden_id": 4,
        "compra_id": 4,
        "distribuidora": "Importadora Cristalería y Porcelana Maya",
        "factura": "FAC-2026-00618",
        "fecha": "2026-10-22",
        "flete": 110.00,
        "cargadores": 40.00,
        "subcategorias": ["Platos y Vajillas"]
    },
    {
        "orden_id": 5,
        "compra_id": 5,
        "distribuidora": "Distribuidora de Cuidado y Cosméticos El Quetzal",
        "factura": "FAC-2026-00744",
        "fecha": "2026-10-25",
        "flete": 80.00,
        "cargadores": 30.00,
        "subcategorias": ["Desodorantes e Higiene Corporal"]
    },
    {
        "orden_id": 6,
        "compra_id": 6,
        "distribuidora": "Marroquinería y Accesorios Chapines",
        "factura": "FAC-2026-00832",
        "fecha": "2026-10-28",
        "flete": 115.00,
        "cargadores": 40.00,
        "subcategorias": ["Bolsas y Mochilas", "Carteras y Billeteras"]
    }
]

def generate_sql():
    sql = []
    sql.append("-- ============================================================================")
    sql.append("-- SEED DEMO DATA: CATÁLOGOS, 100 PRODUCTOS, 10 CLIENTES Y COMPRAS ASOCIADAS")
    sql.append("-- ============================================================================")
    sql.append("BEGIN;")
    sql.append("")

    # 1. Unidades de Medida extra (SET, PKT)
    sql.append("-- 1. Unidades de Medida adicionales")
    sql.append("INSERT INTO unidad_medida (codigo, descripcion, estado)")
    sql.append("VALUES ('SET', 'Juego o Set', 'Activo'), ('PKT', 'Paquete', 'Activo')")
    sql.append("ON CONFLICT (codigo) DO NOTHING;")
    sql.append("")

    # 2. Categorías
    sql.append("-- 2. Categorías (Catálogos)")
    for cat in categories_data:
        sql.append(f"INSERT INTO categoria (nombre, estado) VALUES ('{cat['nombre']}', 'Activo') ON CONFLICT (nombre) DO NOTHING;")
    sql.append("")

    # 3. Subcategorías
    sql.append("-- 3. Subcategorías (Subcatálogos)")
    for cat in categories_data:
        for sub in cat["subcategorias"]:
            sql.append(f"""INSERT INTO subcategoria (id_categoria, nombre, estado)
SELECT c.id_categoria, '{sub}', 'Activo'
FROM categoria c WHERE c.nombre = '{cat['nombre']}'
ON CONFLICT (id_categoria, nombre) DO NOTHING;""")
    sql.append("")

    # 4. Proveedores
    sql.append("-- 4. Proveedores")
    for prov in suppliers_data:
        sql.append(f"""INSERT INTO proveedor (nombre_contacto, distribuidora, telefono, correo, cuenta_bancaria, direccion, estado)
VALUES ('{prov['contacto']}', '{prov['distribuidora']}', '{prov['tel']}', '{prov['correo']}', '{prov['cuenta']}', '{prov['dir']}', 'Activo')
ON CONFLICT DO NOTHING;""")
    sql.append("")

    # 5. Clientes
    sql.append("-- 5. Clientes de Ejemplo")
    for cli in clients_data:
        sql.append(f"""DO $$
DECLARE
    v_id_cliente INT;
BEGIN
    SELECT id_cliente INTO v_id_cliente FROM cliente WHERE nit = '{cli['nit']}';
    IF v_id_cliente IS NULL THEN
        INSERT INTO cliente (id_tipo_cliente, id_municipio, nit, nombre_comercial, direccion, estado)
        VALUES ({cli['tipo']}, {cli['muni']}, '{cli['nit']}', '{cli['nombre']}', '{cli['dir']}', 'Activo')
        RETURNING id_cliente INTO v_id_cliente;

        INSERT INTO cliente_contacto (id_cliente, telefono, correo)
        VALUES (v_id_cliente, '{cli['tel']}', '{cli['email']}');
    END IF;
END $$;""")
    sql.append("")

    # 6. Productos, Variantes, Inventario e Historial de Precios
    sql.append("-- 6. 100 Productos (10 por cada subcatálogo)")
    barcode_counter = 7401202601001

    for subcat_name, prods in products_groups.items():
        sql.append(f"-- --- Subcatálogo: {subcat_name} (10 productos) ---")
        for prod in prods:
            barcode = str(barcode_counter)
            barcode_counter += 1
            talla_val = f"'{prod['talla']}'" if prod['talla'] else "NULL"
            color_val = f"'{prod['color']}'" if prod['color'] else "NULL"

            sql.append(f"""DO $$
DECLARE
    v_id_sub INT;
    v_id_uni INT;
    v_id_prod INT;
    v_id_var INT;
BEGIN
    SELECT id_subcategoria INTO v_id_sub FROM subcategoria WHERE nombre = '{subcat_name}' LIMIT 1;
    SELECT id_unidad INTO v_id_uni FROM unidad_medida WHERE codigo = '{prod['unidad']}' LIMIT 1;
    IF v_id_uni IS NULL THEN
        SELECT id_unidad INTO v_id_uni FROM unidad_medida WHERE codigo = 'UND' LIMIT 1;
    END IF;

    SELECT id_producto INTO v_id_prod FROM producto WHERE nombre = '{prod['nombre']}';
    IF v_id_prod IS NULL THEN
        INSERT INTO producto (id_subcategoria, id_unidad, nombre, descripcion, imagen_url, estado, fecha_creacion)
        VALUES (v_id_sub, v_id_uni, '{prod['nombre']}', '{prod['desc']}', NULL, 'Activo', NOW())
        RETURNING id_producto INTO v_id_prod;

        INSERT INTO variante_producto (id_producto, codigo_barras, talla, color, precio_detalle, precio_mayoreo, costo_promedio)
        VALUES (v_id_prod, '{barcode}', {talla_val}, {color_val}, {prod['detalle']}, {prod['mayoreo']}, {prod['costo']})
        RETURNING id_variante INTO v_id_var;

        INSERT INTO inventario_sucursal (id_variante, id_sucursal, id_area, stock_actual, stock_minimo, fecha_actualizacion)
        VALUES (v_id_var, 1, {prod['area']}, {prod['stock']}, {prod['min']}, NOW());

        INSERT INTO historial_precio (id_variante, id_usuario, precio_anterior, precio_nuevo, fecha_modificacion)
        VALUES (v_id_var, 1, {prod['costo']}, {prod['detalle']}, NOW());
    END IF;
END $$;""")
        sql.append("")

    # 7. Órdenes de Compra y Compras
    sql.append("-- 7. Órdenes de Compra y Compras Recibidas")
    for plan in purchases_plan:
        subcats_str = "', '".join(plan["subcategorias"])
        sql.append(f"""DO $$
DECLARE
    v_id_prov INT;
    v_id_orden INT;
    v_id_compra INT;
    v_total_mercaderia DECIMAL(10,2) := 0;
    v_rec RECORD;
BEGIN
    SELECT id_proveedor INTO v_id_prov FROM proveedor WHERE distribuidora = '{plan['distribuidora']}' LIMIT 1;
    IF v_id_prov IS NULL THEN
        SELECT id_proveedor INTO v_id_prov FROM proveedor ORDER BY id_proveedor LIMIT 1;
    END IF;

    -- Verificar si la compra ya fue registrada
    SELECT id_compra INTO v_id_compra FROM compra WHERE numero_factura_proveedor = '{plan['factura']}';
    IF v_id_compra IS NULL THEN
        -- Crear Orden de Compra previa
        INSERT INTO orden_compra (id_proveedor, id_usuario, fecha_emision, total_estimado, estado)
        VALUES (v_id_prov, 1, '{plan['fecha']}'::DATE - INTERVAL '3 days', 0.00, 'Recibida')
        RETURNING id_orden INTO v_id_orden;

        -- Crear Compra
        INSERT INTO compra (id_orden, id_proveedor, id_usuario, numero_factura_proveedor, fecha_ingreso, subtotal_mercaderia, gasto_flete, gasto_cargadores, total_compra)
        VALUES (v_id_orden, v_id_prov, 1, '{plan['factura']}', '{plan['fecha']}', 0.00, {plan['flete']}, {plan['cargadores']}, 0.00)
        RETURNING id_compra INTO v_id_compra;

        -- Insertar detalles para los productos de las subcategorías correspondientes
        FOR v_rec IN (
            SELECT vp.id_variante, vp.costo_promedio, COALESCE(inv.stock_actual, 25) AS cantidad
            FROM variante_producto vp
            JOIN producto p ON vp.id_producto = p.id_producto
            JOIN subcategoria s ON p.id_subcategoria = s.id_subcategoria
            LEFT JOIN inventario_sucursal inv ON vp.id_variante = inv.id_variante AND inv.id_sucursal = 1
            WHERE s.nombre IN ('{subcats_str}')
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
            total_compra = v_total_mercaderia + {plan['flete']} + {plan['cargadores']}
        WHERE id_compra = v_id_compra;
    END IF;
END $$;""")
        sql.append("")

    # 8. Sincronización de secuencias
    sql.append("-- 8. Sincronización de secuencias")
    sequences = [
        ("categoria_id_categoria_seq", "categoria", "id_categoria"),
        ("subcategoria_id_subcategoria_seq", "subcategoria", "id_subcategoria"),
        ("unidad_medida_id_unidad_seq", "unidad_medida", "id_unidad"),
        ("producto_id_producto_seq", "producto", "id_producto"),
        ("variante_producto_id_variante_seq", "variante_producto", "id_variante"),
        ("inventario_sucursal_id_inventario_seq", "inventario_sucursal", "id_inventario"),
        ("historial_precio_id_historial_seq", "historial_precio", "id_historial"),
        ("cliente_id_cliente_seq", "cliente", "id_cliente"),
        ("cliente_contacto_id_contacto_seq", "cliente_contacto", "id_contacto"),
        ("proveedor_id_proveedor_seq", "proveedor", "id_proveedor"),
        ("orden_compra_id_orden_seq", "orden_compra", "id_orden"),
        ("detalle_orden_compra_id_detalle_orden_seq", "detalle_orden_compra", "id_detalle_orden"),
        ("compra_id_compra_seq", "compra", "id_compra"),
        ("detalle_compra_id_detalle_compra_seq", "detalle_compra", "id_detalle_compra")
    ]
    for seq, tbl, col in sequences:
        sql.append(f"SELECT setval('{seq}', COALESCE((SELECT MAX({col}) FROM {tbl}), 0) + 1, false);")

    sql.append("")
    sql.append("COMMIT;")

    return "\n".join(sql)

if __name__ == "__main__":
    sql_content = generate_sql()
    out_path = os.path.join("database", "seed_demo_data.sql")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(sql_content)
    print(f"Generated {out_path} with {len(sql_content.splitlines())} lines.")
