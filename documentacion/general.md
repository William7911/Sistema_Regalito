# Tienda el Regalito POS — Documentación General

Sistema POS empresarial y de gestión integral para **Curiosidades El Regalito** (Panajachel, Sololá, Guatemala). Diseñado para operar de forma 100% local, robusta y con alta tolerancia a fallos, utilizando PostgreSQL 15 en Docker, API REST con FastAPI (Python 3.13) y Frontend web accesible y optimizado (Bootstrap 5 sin necesidad de compilación o build steps).

---

## 1. Arquitectura del Sistema

El sistema implementa una arquitectura monolítica modular en contenedores Docker:
- **Frontend Web**: HTML5, CSS3 y JavaScript moderno modular, servido a través de **Nginx** en el puerto de producción `9090` (o directamente por FastAPI en desarrollo).
- **Backend API**: **FastAPI** asíncrono con arquitectura por capas (Controllers, Services, Repositories, Interfaces, DTOs con Pydantic v2).
- **Base de Datos**: **PostgreSQL 15** con 48 tablas relacionales en español y migraciones versionadas con **Alembic**.

```
Sistema_Regalito/
├── backend/                     # API REST (FastAPI, Python 3.13)
│   ├── alembic/                 # Migraciones versionadas (0001 a 0016)
│   ├── app/
│   │   ├── main.py              # Inicializador FastAPI, CORS y montaje de rutas
│   │   ├── api/                 # Capa Controladores (Routers HTTP)
│   │   │   ├── auth.py          # Autenticación OAuth2 y JWT
│   │   │   ├── bitacora.py      # Auditoría de eventos
│   │   │   ├── caja.py / cash_register.py # Apertura, movimientos y arqueo ciego
│   │   │   ├── catalogos.py     # Categorías, subcategorías, unidades, sucursales
│   │   │   ├── catalogos_generales.py # Proveedores, motivos merma, métodos pago
│   │   │   ├── clientes.py      # Gestión de clientes y contactos
│   │   │   ├── compras.py       # Ingreso directo de mercadería y órdenes
│   │   │   ├── configuracion.py # Parámetros del sistema
│   │   │   ├── dashboard.py     # KPIs y métricas operativas del día
│   │   │   ├── facturacion.py   # Emisión y certificación FEL
│   │   │   ├── health.py        # Healthcheck de API y Base de Datos
│   │   │   ├── historial_precios.py # Registro histórico de cambios de precio
│   │   │   ├── inventory.py     # Existencias, ajustes y alertas de stock
│   │   │   ├── mermas.py        # Registro de productos dañados / merma
│   │   │   ├── products.py      # Catálogo de productos y variantes
│   │   │   ├── reportes.py      # Reportes contables, ventas y exportación
│   │   │   ├── roles.py         # Roles y matriz de permisos
│   │   │   ├── sales.py         # Punto de venta (POS) y transacciones
│   │   │   ├── tipos_cliente.py # Clasificación de clientes
│   │   │   ├── traslados.py     # Movimientos entre bodegas/sucursales
│   │   │   ├── users.py         # Usuarios y personal
│   │   │   ├── visitas.py       # Visitas de supervisión
│   │   │   └── deps.py          # Inyección de dependencias (DI)
│   │   ├── services/            # Capa de Lógica de Negocio
│   │   ├── repositories/        # Capa de Acceso a Datos (SQLAlchemy Async)
│   │   ├── interfaces/          # Contratos abstractos (ABC)
│   │   ├── schemas/             # DTOs y validaciones (Pydantic v2)
│   │   ├── db/                  # Motor asíncrono y modelos ORM
│   │   └── core/                # Seguridad, configuración y tokens
│   ├── scripts/                 # Scripts auxiliares de mantenimiento
│   ├── auto_migrate.py          # Script de auto-migración al iniciar contenedor
│   └── requirements.txt         # Dependencias Python
├── database/
│   └── init.sql                 # Esquema DDL inicial y datos semilla completos
├── documentacion/               # Manuales y registro de cambios
├── frontend/                    # Interfaz de usuario (HTML/CSS/JS)
│   ├── css/style.css            # Estilos globales y tokens corporativos
│   ├── js/                      # Controladores modulares de interfaz
│   ├── index.html               # Aplicación SPA principal
│   └── cliente.html             # Pantalla secundaria para el cliente (POS)
├── respaldos/                   # Copias de seguridad de la base de datos
├── docker-compose.prod.yml      # Orquestación de producción (Nginx, Backend, DB)
├── docker-compose.yml           # Orquestación de desarrollo
└── nginx.conf                   # Configuración del servidor web proxy inverso
```

---

## 2. Tecnologías y Entorno de Ejecución

| Componente | Tecnología | Rol / Versión |
|---|---|---|
| **Backend** | Python 3.13 + FastAPI | Framework asíncrono de alto rendimiento |
| **Servidor ASGI** | Uvicorn | Ejecución asíncrona del backend |
| **Base de Datos** | PostgreSQL 15 | Base de datos relacional ACID |
| **Driver BD** | asyncpg + SQLAlchemy 2.x | Conexión y ORM asíncrono |
| **Migraciones** | Alembic | Control de versiones del esquema DDL |
| **Frontend** | HTML5, CSS3, JavaScript ES6+ | Sin frameworks pesados ni compilación |
| **Estilos UI** | Bootstrap 5.3 + Bootstrap Icons | Diseño limpio, industrial y responsivo |
| **Proxy / Web Server** | Nginx Alpine | Servidor web estático y reverse proxy |
| **Contenedores** | Docker & Docker Compose | Aislamiento y portabilidad completa |

---

## 3. Puertos y Direcciones de Red

| Servicio | Puerto en Host | Puerto Interno | Descripción |
|---|---|---|---|
| **Frontend (Nginx)** | `9090` | `80` | URL principal de la tienda: `http://localhost:9090/` |
| **Backend API** | `8000` | `8000` | API FastAPI directa (desarrollo): `http://localhost:8000/` |
| **PostgreSQL** | `5433` (dev) / `5432` | `5432` | Base de datos relacional de la tienda |

---

## 4. Esquema de Base de Datos (48 Tablas en Español)

El modelo de datos está completamente normalizado y en idioma español para facilitar la auditoría y mantenimiento contable:

### 4.1 Ventas y Facturación
- `venta`: Encabezado de transacciones de venta (fecha, total, cliente, turno).
- `detalle_venta`: Artículos vendidos, cantidades, precios unitarios y subtotales.
- `pago_venta`: Desglose de pagos recibidos (efectivo, tarjeta, transferencia).
- `factura_fel`: Comprobantes tributarios electrónicos emitidos ante la SAT.

### 4.2 Control de Caja y Turnos
- `caja`: Puntos de cobro físicos de la tienda.
- `turno_caja`: Turnos de trabajo asignados a cajeros (aperturas y cierres).
- `movimiento_caja`: Entradas y salidas manuales de efectivo durante el turno.
- `cierre_caja_ciegas`: Arqueo ciego de efectivo al finalizar la jornada.
- `detalle_arqueo_efectivo`: Desglose por denominación de billetes y monedas.
- `denominacion_efectivo`: Catálogo oficial de billetes y monedas en Quetzales.
- `tipo_movimiento_caja`: Clasificación de ingresos y egresos de caja.

### 4.3 Inventario y Bodega
- `producto`: Maestro de productos.
- `variante_producto`: Códigos de barra, presentaciones y costos.
- `inventario_sucursal`: Existencias físicas por sucursal y bodega.
- `area_bodega`: Ubicaciones físicas dentro de la tienda (mostrador, estantes, bodega).
- `alerta_stock`: Notificaciones automáticas de stock mínimo o agotado.
- `historial_precio`: Trazabilidad histórica de cambios en precios y costos.
- `traslado_inventario`: Transferencia de mercadería entre áreas o sucursales.

### 4.4 Compras y Abastecimiento
- `compra`: Registro de compras e ingreso de mercadería a inventario.
- `detalle_compra`: Desglose de productos ingresados, costos y cantidades.
- `orden_compra`: Órdenes de abastecimiento y pedidos a proveedores.
- `detalle_orden_compra`: Ítems asociados a la orden de compra.
- `proveedor`: Directorio de proveedores y distribuidores comerciales.

### 4.5 Mermas y Desperdicios
- `merma`: Registro de productos dañados, vencidos o averiados.
- `detalle_merma`: Cantidades y productos específicos dados de baja.
- `motivo_merma`: Catálogo de causales (vencimiento, daño físico, rotura).

### 4.6 Catálogos y Clasificación
- `categoria`: Familias principales de artículos.
- `subcategoria`: Subfamilias de clasificación de producto.
- `unidad_medida`: Unidades comerciales (unidad, docena, fardo, caja).
- `metodo_pago`: Medios de cobro aceptados (efectivo, tarjeta, transferencia).
- `departamento_geografico`: Departamentos de Guatemala (Sololá, etc.).
- `municipio`: Municipios de Guatemala (Panajachel, etc.).
- `sucursal`: Sedes físicas del negocio.

### 4.7 Clientes y Relaciones Comerciales
- `cliente`: Directorio de clientes con NIT o Consumidor Final.
- `tipo_cliente`: Categorías de cliente (Mayorista, Minorista, Frecuente).
- `cliente_contacto`: Canales de comunicación y teléfonos de clientes.
- `visita_seguimiento`: Bitácora de supervisión y visitas de clientes mayoristas.
- `visita_modulo_evaluacion`: Evaluaciones y calificaciones de visitas.

### 4.8 Seguridad, Usuarios y Auditoría
- `usuario`: Cuentas de personal administrativo y cajeros.
- `rol`: Perfiles de acceso (Administrador, Cajero, Bodeguero).
- `permiso`: Permisos atómicos del sistema.
- `rol_permiso`: Asignación granular de permisos a perfiles.
- `sesion_usuario`: Control de sesiones activas.
- `intento_login`: Registro de seguridad y prevención de fuerza bruta.
- `bitacora_auditoria`: Registro de auditoría inmutable de todas las acciones del sistema.
- `parametro_sistema`: Configuración global de la aplicación.
- `sync_cache_metadata` / `sync_queue`: Tablas inactivas preservadas para integridad de migraciones históricas.

---

## 5. Facturación Electrónica SAT (FEL)

El módulo FEL emite Documentos Tributarios Electrónicos (DTE) válidos ante la SAT:
- **Validaciones automáticas**:
  - Ventas con monto Q0.00 o negativo son bloqueadas de inmediato.
  - El NIT "CF" (Consumidor Final) se rechaza si la venta supera los Q2,500.00 (Decreto 7-2019 de la SAT).
- **Mecanismo de contingencia**: Si el certificador SAT experimenta caídas o demoras, la venta no se detiene; se registra en estado `Contingencia` y permite su certificación posterior vía `POST /api/facturacion/reintentar/{id_venta}`.

---

## 6. Procedimiento de Inicio y Parada

### 6.1 Iniciar el sistema en Producción (Docker)
```bash
docker compose -f docker-compose.prod.yml up -d
```
Acceder a la aplicación en: `http://localhost:9090`

### 6.2 Ver estado de los contenedores
```bash
docker ps
```

### 6.3 Ver registros en tiempo real
```bash
docker logs -f regalito_backend_prod
```

### 6.4 Detener el sistema
```bash
docker compose -f docker-compose.prod.yml down
```

---

## 7. Pruebas y Verificación Automatizada

El proyecto cuenta con scripts de validación con **Playwright Chromium**:
- Pruebas E2E de flujos de venta en POS.
- Comprobación de apertura y cierre de caja con arqueo ciego.
- Verificación de estandarización de interfaz y cabeceras de tabla sin emojis.
