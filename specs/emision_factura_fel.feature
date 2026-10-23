# language: es
Característica: Emisión de Factura Electrónica en Línea (FEL)
  Como cajero del Sistema Tienda el Regalito POS
  Quiero emitir una Factura Electrónica (FEL) al finalizar una venta
  Para cumplir con los requerimientos fiscales de la SAT y registrar la venta formalmente.

  Antecedentes:
    Dado que el usuario tiene el rol "Cajero" o "Administradora"
    Y tiene una sesión activa y un "Turno de Caja" abierto
    Y se encuentra en el módulo "POS / Ventas"

  # ----------------------------------------------------------------------
  # CAMINO FELIZ
  # ----------------------------------------------------------------------
  Escenario: Generación exitosa de factura electrónica (FEL) con cliente válido
    Dado que el cajero ha agregado productos al carrito con un total mayor a cero
    Y el cajero ha ingresado un NIT válido (ej. "123456-7" o "CF") y el nombre del cliente
    Cuando el cajero confirma el método de pago y presiona "Facturar y Cobrar"
    Entonces el sistema envía los detalles de la venta al proveedor certificador FEL
    Y el certificador responde con éxito, retornando un número de autorización (UUID), serie y número de DTE
    Y el sistema registra la venta en la base de datos local con estado "Certificada" guardando los datos del DTE
    Y el sistema descuenta el inventario de los productos vendidos
    Y el sistema muestra el modal de éxito con la opción de "Imprimir Ticket FEL"

  # ----------------------------------------------------------------------
  # MANEJO DE ERRORES (Falla de Comunicación)
  # ----------------------------------------------------------------------
  Escenario: Falla de comunicación o caída del certificador FEL (Timeout)
    Dado que el cajero ha preparado la venta para su cobro
    Cuando el cajero presiona "Facturar y Cobrar"
    Y el API del proveedor certificador FEL no responde en el tiempo límite (timeout) o devuelve error 503/500
    Entonces el sistema interrumpe el intento de certificación
    Y el sistema revierte (rollback) el intento a nivel del certificador
    Y el sistema registra la venta en la base de datos local con estado "Pendiente DTE" o "Contingencia"
    Y el sistema descuenta el inventario para no detener la operación de la tienda
    Y el sistema muestra un Toast de advertencia: "Problemas de conexión con el certificador FEL. La venta se guardó como Contingencia y debe certificarse más tarde."

  Escenario: El certificador rechaza la firma por reglas fiscales de SAT
    Dado que el cajero intenta certificar una venta
    Cuando el certificador FEL devuelve un error 400 por incumplimiento de regla (ej. "NIT del receptor inválido en SAT")
    Entonces el sistema no registra la venta ni descuenta inventario
    Y el sistema muestra un modal de error con el mensaje devuelto por el certificador: "Rechazado: El NIT ingresado no está activo o es inválido."
    Y el cajero puede corregir el NIT y volver a intentar.

  # ----------------------------------------------------------------------
  # VALIDACIONES REQUERIDAS (Reglas de Negocio Locales)
  # ----------------------------------------------------------------------
  Escenario: Prevención de facturación con montos inválidos
    Dado que el cajero modificó un producto dejando su precio de venta final en Q0.00
    O hay una cantidad negativa en el detalle de venta
    Cuando el cajero presiona "Facturar y Cobrar"
    Entonces el sistema detiene la operación antes de contactar al certificador
    Y el sistema muestra una notificación Toast: "Los totales de la factura deben ser mayores a cero y no pueden contener cantidades negativas."

  Escenario: Validación estricta de CF (Consumidor Final) por monto límite (Decreto 7-2019/SAT)
    Dado que el total de la venta es superior a Q2,500.00
    Cuando el cajero ingresa "CF" como NIT o lo deja en blanco
    Y presiona "Facturar y Cobrar"
    Entonces el sistema detiene la operación antes de contactar al certificador
    Y el sistema muestra una notificación de error: "Para compras mayores a Q2,500.00 es obligatorio ingresar el NIT y Nombre del cliente. No se permite CF."
