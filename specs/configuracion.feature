# language: es
Característica: Gestión de Configuración y Parámetros del Sistema
  Como Administradora del Sistema Regalito
  Quiero acceder a un módulo de configuración general
  Para gestionar los parámetros operativos y las credenciales (NIT, Razón Social, Token FEL) de forma segura

  Escenario: Acceso y edición exitosa por parte de la Administradora
    Dado que un usuario ha iniciado sesión con el rol "Administradora"
    Cuando solicita acceder a la vista de configuración
    Y envía una actualización para parámetros del negocio (ej. "NIT", "Razón Social", "Token FEL")
    Entonces el sistema debe actualizar los valores correspondientes en la tabla parametro_sistema
    Y confirmar que los cambios fueron guardados exitosamente

  Escenario: Validación estricta de parámetros críticos vacíos
    Dado que un usuario ha iniciado sesión con el rol "Administradora"
    Cuando intenta guardar la configuración enviando claves críticas vacías (ej. NIT vacío)
    Entonces el sistema debe rechazar la operación
    Y devolver un error indicando que las claves críticas no pueden estar vacías
    Y los parámetros originales deben permanecer inalterados en la base de datos

  Escenario: Acceso denegado a usuarios no autorizados (RBAC)
    Dado que un usuario ha iniciado sesión con un rol diferente a Administradora (ej. "Cajero" o "Bodeguero")
    Cuando intenta acceder a la vista de configuración o modificar algún parámetro
    Entonces el sistema debe rechazar la petición con un error de acceso denegado (HTTP 403)
    Y no debe exponer ni alterar ninguna clave-valor de la tabla parametro_sistema
