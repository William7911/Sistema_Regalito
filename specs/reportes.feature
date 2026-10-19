Feature: Módulo de Reportes y Estadísticas
  Como administrador del sistema
  Quiero acceder a un panel de reportes de ventas, mermas e ingresos
  Para visualizar métricas clave en rangos de fechas específicos y exportar la información.

  Scenario: Acceso permitido a la vista de reportes para la Administradora
    Given que el usuario autenticado tiene el rol "Administradora"
    When el usuario intenta acceder a la vista principal del módulo de Reportes
    Then el sistema debe otorgar el acceso
    And mostrar el panel de estadísticas.

  Scenario: Filtrado de ventas, mermas e ingresos por rango de fechas
    Given que el usuario tiene acceso a la vista de Reportes
    When el usuario define una "Fecha Inicial" y una "Fecha Final"
    And solicita generar el consolidado de datos
    Then el sistema debe procesar la solicitud
    And mostrar únicamente los registros de ventas, mermas e ingresos que ocurrieron dentro de dicho rango.

  Scenario: Descarga de reportes en formato Excel o CSV
    Given que el usuario ha filtrado datos exitosamente en la vista de Reportes
    When el usuario solicita exportar los datos
    And selecciona el formato de salida ("Excel" o "CSV")
    Then el sistema debe reutilizar la lógica de exportación central (del módulo de Usuarios)
    And compilar los datos en un archivo con el formato elegido
    And disparar la descarga directa del archivo en el navegador del usuario.

  Scenario: Intento de acceso denegado a roles operativos (Cajero o Bodeguero)
    Given que un usuario con el rol "Cajero" o "Bodeguero" está autenticado en el sistema
    When el usuario intenta acceder a la ruta o a la API del módulo de Reportes
    Then el sistema debe rechazar el acceso por falta de privilegios (HTTP 403 Forbidden)
    And redirigir al usuario automáticamente a su Dashboard principal con una notificación de advertencia.
