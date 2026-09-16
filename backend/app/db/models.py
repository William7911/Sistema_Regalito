from sqlalchemy import (
    Column, Integer, String, Numeric, Boolean, DateTime, Date, ForeignKey, Text
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from .database import Base


# ============================================================================
# MÓDULO 1: SEGURIDAD Y AUDITORÍA
# ============================================================================

class Rol(Base):
    __tablename__ = "rol"

    id_rol = Column(Integer, primary_key=True)
    nombre = Column(String(50), nullable=False)
    descripcion = Column(String(150), nullable=True)
    estado = Column(String(20), nullable=False)

    usuarios = relationship("Usuario", back_populates="rol")


class Usuario(Base):
    __tablename__ = "usuario"

    id_usuario = Column(Integer, primary_key=True)
    id_rol = Column(Integer, ForeignKey("rol.id_rol"), nullable=False)
    nombre_completo = Column(String(100), nullable=False)
    username = Column(String(50), nullable=False)
    password_hash = Column(String(255), nullable=False)
    estado = Column(String(20), nullable=False)
    fecha_creacion = Column(DateTime, server_default=func.now(), nullable=False)

    rol = relationship("Rol", back_populates="usuarios")


class Permiso(Base):
    __tablename__ = "permiso"

    id_permiso = Column(Integer, primary_key=True)
    modulo = Column(String(50), nullable=False)
    codigo = Column(String(50), nullable=False)
    descripcion = Column(String(150), nullable=True)

    roles = relationship("RolPermiso", back_populates="permiso")


class RolPermiso(Base):
    __tablename__ = "rol_permiso"

    id_rol = Column(Integer, ForeignKey("rol.id_rol"), primary_key=True)
    id_permiso = Column(Integer, ForeignKey("permiso.id_permiso"), primary_key=True)

    rol = relationship("Rol")
    permiso = relationship("Permiso", back_populates="roles")


class SesionUsuario(Base):
    __tablename__ = "sesion_usuario"

    id_sesion = Column(Integer, primary_key=True)
    id_usuario = Column(Integer, ForeignKey("usuario.id_usuario"), nullable=False)
    fecha_inicio = Column(DateTime, nullable=False)
    fecha_fin = Column(DateTime, nullable=True)
    ip_origen = Column(String(45), nullable=True)

    usuario = relationship("Usuario")


class BitacoraAuditoria(Base):
    __tablename__ = "bitacora_auditoria"

    id_bitacora = Column(Integer, primary_key=True)
    id_usuario = Column(Integer, ForeignKey("usuario.id_usuario"), nullable=False)
    tabla_afectada = Column(String(50), nullable=False)
    accion = Column(String(20), nullable=False)
    descripcion = Column(String(255), nullable=False)
    fecha_hora = Column(DateTime, nullable=False)

    usuario = relationship("Usuario")


class ParametroSistema(Base):
    __tablename__ = "parametro_sistema"

    id_parametro = Column(Integer, primary_key=True)
    clave = Column(String(50), nullable=False)
    valor = Column(String(255), nullable=False)


# ============================================================================
# MÓDULO 2: SUCURSALES, UBICACIÓN Y CLIENTES
# ============================================================================

class Sucursal(Base):
    __tablename__ = "sucursal"

    id_sucursal = Column(Integer, primary_key=True)
    nombre = Column(String(100), nullable=False)
    direccion = Column(String(200), nullable=False)
    telefono = Column(String(20), nullable=True)
    estado = Column(String(20), nullable=False)

    areas = relationship("AreaBodega", back_populates="sucursal")
    cajas = relationship("Caja", back_populates="sucursal")


class AreaBodega(Base):
    __tablename__ = "area_bodega"

    id_area = Column(Integer, primary_key=True)
    id_sucursal = Column(Integer, ForeignKey("sucursal.id_sucursal"), nullable=False)
    nombre_area = Column(String(50), nullable=False)

    sucursal = relationship("Sucursal", back_populates="areas")


class DepartamentoGeografico(Base):
    __tablename__ = "departamento_geografico"

    id_departamento = Column(Integer, primary_key=True)
    nombre = Column(String(50), nullable=False)

    municipios = relationship("Municipio", back_populates="departamento")


class Municipio(Base):
    __tablename__ = "municipio"

    id_municipio = Column(Integer, primary_key=True)
    id_departamento = Column(Integer, ForeignKey("departamento_geografico.id_departamento"), nullable=False)
    nombre = Column(String(50), nullable=False)

    departamento = relationship("DepartamentoGeografico", back_populates="municipios")


class TipoCliente(Base):
    __tablename__ = "tipo_cliente"

    id_tipo_cliente = Column(Integer, primary_key=True)
    nombre = Column(String(50), nullable=False)
    descuento_predeterminado = Column(Numeric(5, 2), nullable=True)

    clientes = relationship("Cliente", back_populates="tipo_cliente")


class Cliente(Base):
    __tablename__ = "cliente"

    id_cliente = Column(Integer, primary_key=True)
    id_tipo_cliente = Column(Integer, ForeignKey("tipo_cliente.id_tipo_cliente"), nullable=False)
    id_municipio = Column(Integer, ForeignKey("municipio.id_municipio"), nullable=True)
    nit = Column(String(15), nullable=False)
    nombre_comercial = Column(String(120), nullable=False)
    direccion = Column(String(200), nullable=True)

    tipo_cliente = relationship("TipoCliente", back_populates="clientes")
    municipio = relationship("Municipio")
    contactos = relationship("ClienteContacto", back_populates="cliente")


class ClienteContacto(Base):
    __tablename__ = "cliente_contacto"

    id_contacto = Column(Integer, primary_key=True)
    id_cliente = Column(Integer, ForeignKey("cliente.id_cliente"), nullable=False)
    telefono = Column(String(20), nullable=True)
    correo = Column(String(100), nullable=True)

    cliente = relationship("Cliente", back_populates="contactos")


# ============================================================================
# MÓDULO 3: CATÁLOGO E INVENTARIO
# ============================================================================

class Categoria(Base):
    __tablename__ = "categoria"

    id_categoria = Column(Integer, primary_key=True)
    nombre = Column(String(50), nullable=False)
    estado = Column(String(20), nullable=False)

    subcategorias = relationship("Subcategoria", back_populates="categoria")


class Subcategoria(Base):
    __tablename__ = "subcategoria"

    id_subcategoria = Column(Integer, primary_key=True)
    id_categoria = Column(Integer, ForeignKey("categoria.id_categoria"), nullable=False)
    nombre = Column(String(50), nullable=False)

    categoria = relationship("Categoria", back_populates="subcategorias")
    productos = relationship("Producto", back_populates="subcategoria")


class UnidadMedida(Base):
    __tablename__ = "unidad_medida"

    id_unidad = Column(Integer, primary_key=True)
    codigo = Column(String(10), nullable=False)
    descripcion = Column(String(50), nullable=False)

    productos = relationship("Producto", back_populates="unidad")


class Producto(Base):
    __tablename__ = "producto"

    id_producto = Column(Integer, primary_key=True)
    id_subcategoria = Column(Integer, ForeignKey("subcategoria.id_subcategoria"), nullable=False)
    id_unidad = Column(Integer, ForeignKey("unidad_medida.id_unidad"), nullable=False)
    nombre = Column(String(100), nullable=False)
    descripcion = Column(String(255), nullable=True)
    imagen_url = Column(String(255), nullable=True)
    estado = Column(String(20), nullable=False)
    fecha_creacion = Column(DateTime, server_default=func.now(), nullable=False)

    subcategoria = relationship("Subcategoria", back_populates="productos")
    unidad = relationship("UnidadMedida", back_populates="productos")
    variantes = relationship("VarianteProducto", back_populates="producto")


class VarianteProducto(Base):
    __tablename__ = "variante_producto"

    id_variante = Column(Integer, primary_key=True)
    id_producto = Column(Integer, ForeignKey("producto.id_producto"), nullable=False)
    codigo_barras = Column(String(50), nullable=True)
    talla = Column(String(20), nullable=True)
    color = Column(String(30), nullable=True)
    precio_detalle = Column(Numeric(10, 2), nullable=False)
    precio_mayoreo = Column(Numeric(10, 2), nullable=False)
    costo_promedio = Column(Numeric(10, 2), nullable=False)

    producto = relationship("Producto", back_populates="variantes")
    inventarios = relationship("InventarioSucursal", back_populates="variante")


class InventarioSucursal(Base):
    __tablename__ = "inventario_sucursal"

    id_inventario = Column(Integer, primary_key=True)
    id_variante = Column(Integer, ForeignKey("variante_producto.id_variante"), nullable=False)
    id_sucursal = Column(Integer, ForeignKey("sucursal.id_sucursal"), nullable=False)
    id_area = Column(Integer, ForeignKey("area_bodega.id_area"), nullable=True)
    stock_actual = Column(Integer, nullable=False)
    stock_minimo = Column(Integer, nullable=False)
    fecha_actualizacion = Column(DateTime, nullable=False)

    variante = relationship("VarianteProducto", back_populates="inventarios")
    sucursal = relationship("Sucursal")
    area = relationship("AreaBodega")
    alertas = relationship("AlertaStock", back_populates="inventario")


class HistorialPrecio(Base):
    __tablename__ = "historial_precio"

    id_historial = Column(Integer, primary_key=True)
    id_variante = Column(Integer, ForeignKey("variante_producto.id_variante"), nullable=False)
    id_usuario = Column(Integer, ForeignKey("usuario.id_usuario"), nullable=False)
    precio_anterior = Column(Numeric(10, 2), nullable=False)
    precio_nuevo = Column(Numeric(10, 2), nullable=False)
    fecha_modificacion = Column(DateTime, nullable=False)

    variante = relationship("VarianteProducto")
    usuario = relationship("Usuario")


class AlertaStock(Base):
    __tablename__ = "alerta_stock"

    id_alerta = Column(Integer, primary_key=True)
    id_inventario = Column(Integer, ForeignKey("inventario_sucursal.id_inventario"), nullable=False)
    mensaje = Column(String(150), nullable=False)
    fecha_generacion = Column(DateTime, nullable=False)
    estado = Column(String(20), nullable=False)

    inventario = relationship("InventarioSucursal", back_populates="alertas")


# ============================================================================
# MÓDULO 4: MOVIMIENTOS Y MERMAS
# ============================================================================

class MotivoMerma(Base):
    __tablename__ = "motivo_merma"

    id_motivo = Column(Integer, primary_key=True)
    descripcion = Column(String(100), nullable=False)


class Merma(Base):
    __tablename__ = "merma"

    id_merma = Column(Integer, primary_key=True)
    id_sucursal = Column(Integer, ForeignKey("sucursal.id_sucursal"), nullable=False)
    id_usuario = Column(Integer, ForeignKey("usuario.id_usuario"), nullable=False)
    fecha_merma = Column(DateTime, nullable=False)
    observaciones = Column(String(255), nullable=True)

    sucursal = relationship("Sucursal")
    usuario = relationship("Usuario")
    detalles = relationship("DetalleMerma", back_populates="merma")


class DetalleMerma(Base):
    __tablename__ = "detalle_merma"

    id_detalle_merma = Column(Integer, primary_key=True)
    id_merma = Column(Integer, ForeignKey("merma.id_merma"), nullable=False)
    id_variante = Column(Integer, ForeignKey("variante_producto.id_variante"), nullable=False)
    id_motivo = Column(Integer, ForeignKey("motivo_merma.id_motivo"), nullable=False)
    cantidad = Column(Integer, nullable=False)
    costo_perdida = Column(Numeric(10, 2), nullable=False)

    merma = relationship("Merma", back_populates="detalles")
    variante = relationship("VarianteProducto")
    motivo = relationship("MotivoMerma")


class TrasladoInventario(Base):
    __tablename__ = "traslado_inventario"

    id_traslado = Column(Integer, primary_key=True)
    id_variante = Column(Integer, ForeignKey("variante_producto.id_variante"), nullable=False)
    id_sucursal_origen = Column(Integer, ForeignKey("sucursal.id_sucursal"), nullable=False)
    id_sucursal_destino = Column(Integer, ForeignKey("sucursal.id_sucursal"), nullable=False)
    cantidad = Column(Integer, nullable=False)
    fecha_traslado = Column(DateTime, nullable=False)

    variante = relationship("VarianteProducto")
    sucursal_origen = relationship("Sucursal", foreign_keys=[id_sucursal_origen])
    sucursal_destino = relationship("Sucursal", foreign_keys=[id_sucursal_destino])


# ============================================================================
# MÓDULO 5: CAJA, TURNOS Y TESORERÍA
# ============================================================================

class Caja(Base):
    __tablename__ = "caja"

    id_caja = Column(Integer, primary_key=True)
    id_sucursal = Column(Integer, ForeignKey("sucursal.id_sucursal"), nullable=False)
    descripcion = Column(String(50), nullable=False)
    estado = Column(String(20), nullable=False)

    sucursal = relationship("Sucursal", back_populates="cajas")
    turnos = relationship("TurnoCaja", back_populates="caja")


class TurnoCaja(Base):
    __tablename__ = "turno_caja"

    id_turno = Column(Integer, primary_key=True)
    id_caja = Column(Integer, ForeignKey("caja.id_caja"), nullable=False)
    id_usuario = Column(Integer, ForeignKey("usuario.id_usuario"), nullable=False)
    monto_apertura = Column(Numeric(10, 2), nullable=False)
    fecha_apertura = Column(DateTime, nullable=False)
    fecha_cierre = Column(DateTime, nullable=True)
    estado = Column(String(20), nullable=False)
    monto_cierre = Column(Numeric(10, 2), nullable=True)
    notas = Column(String(255), nullable=True)

    caja = relationship("Caja", back_populates="turnos")
    usuario = relationship("Usuario")


class TipoMovimientoCaja(Base):
    __tablename__ = "tipo_movimiento_caja"

    id_tipo_movimiento = Column(Integer, primary_key=True)
    nombre = Column(String(50), nullable=False)


class MovimientoCaja(Base):
    __tablename__ = "movimiento_caja"

    id_movimiento = Column(Integer, primary_key=True)
    id_turno = Column(Integer, ForeignKey("turno_caja.id_turno"), nullable=False)
    id_tipo_movimiento = Column(Integer, ForeignKey("tipo_movimiento_caja.id_tipo_movimiento"), nullable=False)
    id_usuario = Column(Integer, ForeignKey("usuario.id_usuario"), nullable=False)
    monto = Column(Numeric(10, 2), nullable=False)
    justificacion = Column(String(255), nullable=False)
    fecha_hora = Column(DateTime, nullable=False)

    turno = relationship("TurnoCaja")
    tipo_movimiento = relationship("TipoMovimientoCaja")
    usuario = relationship("Usuario")


class CierreCajaCiegas(Base):
    __tablename__ = "cierre_caja_ciegas"

    id_cierre = Column(Integer, primary_key=True)
    id_turno = Column(Integer, ForeignKey("turno_caja.id_turno"), nullable=False)
    id_usuario_cajero = Column(Integer, ForeignKey("usuario.id_usuario"), nullable=False)
    id_usuario_supervisor = Column(Integer, ForeignKey("usuario.id_usuario"), nullable=False)
    total_contado_ciegas = Column(Numeric(10, 2), nullable=False)
    total_calculado_sistema = Column(Numeric(10, 2), nullable=False)
    diferencia = Column(Numeric(10, 2), nullable=False)
    observaciones = Column(String(255), nullable=True)
    fecha_cierre = Column(DateTime, nullable=False)

    turno = relationship("TurnoCaja")
    usuario_cajero = relationship("Usuario", foreign_keys=[id_usuario_cajero])
    usuario_supervisor = relationship("Usuario", foreign_keys=[id_usuario_supervisor])
    detalles_arqueo = relationship("DetalleArqueoEfectivo", back_populates="cierre")


class DenominacionEfectivo(Base):
    __tablename__ = "denominacion_efectivo"

    id_denominacion = Column(Integer, primary_key=True)
    valor = Column(Numeric(10, 2), nullable=False)
    tipo = Column(String(15), nullable=False)


class DetalleArqueoEfectivo(Base):
    __tablename__ = "detalle_arqueo_efectivo"

    id_detalle_arqueo = Column(Integer, primary_key=True)
    id_cierre = Column(Integer, ForeignKey("cierre_caja_ciegas.id_cierre"), nullable=False)
    id_denominacion = Column(Integer, ForeignKey("denominacion_efectivo.id_denominacion"), nullable=False)
    cantidad_piezas = Column(Integer, nullable=False)
    subtotal = Column(Numeric(10, 2), nullable=False)

    cierre = relationship("CierreCajaCiegas", back_populates="detalles_arqueo")
    denominacion = relationship("DenominacionEfectivo")


# ============================================================================
# MÓDULO 6: VENTAS, COBROS Y FACTURACIÓN
# ============================================================================

class MetodoPago(Base):
    __tablename__ = "metodo_pago"

    id_metodo_pago = Column(Integer, primary_key=True)
    nombre = Column(String(30), nullable=False)


class Venta(Base):
    __tablename__ = "venta"

    id_venta = Column(Integer, primary_key=True)
    id_turno = Column(Integer, ForeignKey("turno_caja.id_turno"), nullable=False)
    id_cliente = Column(Integer, ForeignKey("cliente.id_cliente"), nullable=True)
    id_usuario = Column(Integer, ForeignKey("usuario.id_usuario"), nullable=False)
    fecha_venta = Column(DateTime, nullable=False)
    subtotal = Column(Numeric(10, 2), nullable=False)
    descuento_total = Column(Numeric(10, 2), nullable=False)
    total_venta = Column(Numeric(10, 2), nullable=False)
    estado = Column(String(20), nullable=False)

    turno = relationship("TurnoCaja")
    cliente = relationship("Cliente")
    usuario = relationship("Usuario")
    detalles = relationship("DetalleVenta", back_populates="venta")
    pagos = relationship("PagoVenta", back_populates="venta")
    factura = relationship("FacturaFel", back_populates="venta", uselist=False)


class DetalleVenta(Base):
    __tablename__ = "detalle_venta"

    id_detalle_venta = Column(Integer, primary_key=True)
    id_venta = Column(Integer, ForeignKey("venta.id_venta"), nullable=False)
    id_variante = Column(Integer, ForeignKey("variante_producto.id_variante"), nullable=False)
    cantidad = Column(Integer, nullable=False)
    precio_unitario = Column(Numeric(10, 2), nullable=False)
    descuento_item = Column(Numeric(10, 2), nullable=False)
    subtotal = Column(Numeric(10, 2), nullable=False)

    venta = relationship("Venta", back_populates="detalles")
    variante = relationship("VarianteProducto")


class PagoVenta(Base):
    __tablename__ = "pago_venta"

    id_pago = Column(Integer, primary_key=True)
    id_venta = Column(Integer, ForeignKey("venta.id_venta"), nullable=False)
    id_metodo_pago = Column(Integer, ForeignKey("metodo_pago.id_metodo_pago"), nullable=False)
    monto_recibido = Column(Numeric(10, 2), nullable=False)
    vuelto_entregado = Column(Numeric(10, 2), nullable=False)

    venta = relationship("Venta", back_populates="pagos")
    metodo_pago = relationship("MetodoPago")


class FacturaFel(Base):
    __tablename__ = "factura_fel"

    id_factura = Column(Integer, primary_key=True)
    id_venta = Column(Integer, ForeignKey("venta.id_venta"), nullable=False)
    numero_autorizacion_sat = Column(String(50), nullable=False)
    serie = Column(String(20), nullable=False)
    numero_dte = Column(String(30), nullable=False)
    fecha_certificacion = Column(DateTime, nullable=False)
    nit_receptor = Column(String(15), nullable=False)
    nombre_receptor = Column(String(120), nullable=False)
    total_facturado = Column(Numeric(10, 2), nullable=False)

    venta = relationship("Venta", back_populates="factura")


# ============================================================================
# MÓDULO 7: COMPRAS Y PROVEEDORES
# ============================================================================

class Proveedor(Base):
    __tablename__ = "proveedor"

    id_proveedor = Column(Integer, primary_key=True)
    nombre_contacto = Column(String(100), nullable=False)
    distribuidora = Column(String(100), nullable=False)
    telefono = Column(String(20), nullable=True)
    correo = Column(String(100), nullable=True)
    cuenta_bancaria = Column(String(50), nullable=True)
    direccion = Column(String(150), nullable=True)

    ordenes = relationship("OrdenCompra", back_populates="proveedor")


class OrdenCompra(Base):
    __tablename__ = "orden_compra"

    id_orden = Column(Integer, primary_key=True)
    id_proveedor = Column(Integer, ForeignKey("proveedor.id_proveedor"), nullable=False)
    id_usuario = Column(Integer, ForeignKey("usuario.id_usuario"), nullable=False)
    fecha_emision = Column(Date, nullable=False)
    total_estimado = Column(Numeric(10, 2), nullable=False)
    estado = Column(String(20), nullable=False)

    proveedor = relationship("Proveedor", back_populates="ordenes")
    usuario = relationship("Usuario")
    detalles = relationship("DetalleOrdenCompra", back_populates="orden")
    compras = relationship("Compra", back_populates="orden")


class DetalleOrdenCompra(Base):
    __tablename__ = "detalle_orden_compra"

    id_detalle_orden = Column(Integer, primary_key=True)
    id_orden = Column(Integer, ForeignKey("orden_compra.id_orden"), nullable=False)
    id_variante = Column(Integer, ForeignKey("variante_producto.id_variante"), nullable=False)
    cantidad_pedida = Column(Integer, nullable=False)
    costo_pactado = Column(Numeric(10, 2), nullable=False)

    orden = relationship("OrdenCompra", back_populates="detalles")
    variante = relationship("VarianteProducto")


class Compra(Base):
    __tablename__ = "compra"

    id_compra = Column(Integer, primary_key=True)
    id_orden = Column(Integer, ForeignKey("orden_compra.id_orden"), nullable=True)
    id_proveedor = Column(Integer, ForeignKey("proveedor.id_proveedor"), nullable=False)
    id_usuario = Column(Integer, ForeignKey("usuario.id_usuario"), nullable=False)
    numero_factura_proveedor = Column(String(50), nullable=False)
    fecha_ingreso = Column(Date, nullable=False)
    subtotal_mercaderia = Column(Numeric(10, 2), nullable=False)
    gasto_flete = Column(Numeric(10, 2), nullable=False)
    gasto_cargadores = Column(Numeric(10, 2), nullable=False)
    total_compra = Column(Numeric(10, 2), nullable=False)

    orden = relationship("OrdenCompra", back_populates="compras")
    proveedor = relationship("Proveedor")
    usuario = relationship("Usuario")
    detalles = relationship("DetalleCompra", back_populates="compra")


class DetalleCompra(Base):
    __tablename__ = "detalle_compra"

    id_detalle_compra = Column(Integer, primary_key=True)
    id_compra = Column(Integer, ForeignKey("compra.id_compra"), nullable=False)
    id_variante = Column(Integer, ForeignKey("variante_producto.id_variante"), nullable=False)
    cantidad_recibida = Column(Integer, nullable=False)
    costo_unitario = Column(Numeric(10, 2), nullable=False)
    subtotal = Column(Numeric(10, 2), nullable=False)

    compra = relationship("Compra", back_populates="detalles")
    variante = relationship("VarianteProducto")