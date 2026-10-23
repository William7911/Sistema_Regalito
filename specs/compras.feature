# language: es
Característica: Módulo de Compras e Ingreso a Bodega
  Como Administrador o Bodeguero del Sistema Tienda el Regalito
  Quiero gestionar las órdenes de compra a proveedores y el posterior ingreso físico de los productos
  Para mantener un control riguroso sobre las compras y mantener actualizado el inventario automáticamente.

  Antecedentes:
    Dado que el sistema tiene configurados los permisos RBAC (Role-Based Access Control)
    Y existen proveedores y productos registrados en el catálogo de la tienda

  # ----------------------------------------------------------------------
  # CAMINOS FELICES (HAPPY PATHS)
  # ----------------------------------------------------------------------
  Escenario: Emisión exitosa de una Orden de Compra por un usuario autorizado
    Dado que un usuario autenticado posee el permiso "COMPRA_EMITIR_ORDEN"
    Cuando el usuario ingresa los datos del proveedor, una lista de variantes de productos y sus cantidades
    Y confirma la creación de la orden
    Entonces el sistema registra la orden de compra en la base de datos con el estado inicial "Emitida"
    Y el sistema no afecta el inventario local en este paso (solo queda como mercadería en tránsito)

  Escenario: Ingreso de mercadería a bodega por el rol Bodeguero
    Dado que existe una orden de compra registrada en el sistema con estado "Emitida"
    Y un usuario autenticado con el permiso "INV_INGRESAR_MERCADERIA" (ej. rol "Bodeguero") abre la orden
    Cuando el usuario confirma la recepción de todos los productos listados en la orden de compra
    Entonces el sistema cambia automáticamente el estado de la orden de compra a "Recibida"
    Y el sistema suma automáticamente la cantidad recibida de cada producto al `stock_actual` del inventario de la sucursal correspondiente
    Y se registra en la bitácora de auditoría el ingreso de inventario

  # ----------------------------------------------------------------------
  # RESTRICCIONES DE ACCESO Y SEGURIDAD (HTTP 403)
  # ----------------------------------------------------------------------
  Escenario: Rechazo en la emisión de orden por falta de permiso
    Dado que un usuario autenticado (ej. rol "Cajero" sin privilegios de compras) inicia sesión
    Cuando el usuario intenta enviar una solicitud para emitir una orden de compra
    Entonces el sistema valida los permisos del token JWT
    Y detiene inmediatamente la transacción
    Y devuelve un código de error HTTP 403 Forbidden con el mensaje "Privilegios insuficientes"
    Y ninguna orden de compra es registrada en el sistema

  Escenario: Rechazo en el ingreso de mercadería por falta de permiso
    Dado que un usuario autenticado carece del permiso "INV_INGRESAR_MERCADERIA"
    Cuando el usuario intenta enviar una solicitud para cambiar el estado de una orden a "Recibida" e ingresar stock
    Entonces el sistema valida los permisos del token JWT
    Y detiene la ejecución antes de alterar cualquier inventario
    Y devuelve un código de error HTTP 403 Forbidden con el mensaje "Privilegios insuficientes"
    Y el `stock_actual` de los productos permanece intacto
