# language: es
Característica: Facturación Electrónica y Modo Offline
  Como cajero del Sistema Regalito
  Quiero procesar ventas tanto con conexión como sin conexión a internet
  Para asegurar la continuidad del negocio y el cumplimiento de la Facturación Electrónica (FEL)

  Escenario: Certificación inmediata de factura con conexión a internet
    Dado que el sistema detecta una conexión a internet activa
    Y hay inventario local suficiente para la venta
    Cuando el cajero completa la transacción de la venta en el POS
    Entonces el sistema debe certificar la factura inmediatamente con el proveedor FEL
    Y el estado de la venta debe registrarse como 'Completada'

  Escenario: Registro de venta en modo offline (Sin conexión)
    Dado que el sistema detecta pérdida de conexión a internet
    Y hay inventario local suficiente para la venta
    Cuando el cajero completa la transacción de la venta en el POS
    Entonces la transacción debe registrarse localmente en la cola de escritura (sync_queue)
    Y el estado de la sincronización debe ser 'PENDIENTE'
    Y la transacción debe incluir una clave de idempotencia única (UUIDv4)

  Escenario: Sincronización automática de transacciones offline al recuperar la red
    Dado que existen transacciones en la cola de escritura (sync_queue) con estado 'PENDIENTE'
    Cuando el componente SyncEngine detecta que la conexión a internet ha sido restaurada
    Entonces el sistema debe enviar automáticamente las transacciones pendientes a la nube
    Y tras certificarse exitosamente, el estado de la transacción en la cola debe cambiar a 'SINCRONIZADO'

  Escenario: Rechazo estricto de venta offline por falta de inventario
    Dado que el sistema se encuentra en modo offline
    Cuando el cajero intenta registrar una venta en el POS
    Y el inventario local no es suficiente para cubrir la cantidad solicitada del producto
    Entonces el sistema debe tener una política estricta para rechazar la transacción
    Y debe mostrar una alerta indicando que no hay stock suficiente para concretar la venta
