--
-- PostgreSQL database dump
--

\restrict 5OgBlypL75iNVJlhszhqWlhH1skhoXBgKhuddTckEtAHrLAdxda8jbdmepF3KyC

-- Dumped from database version 15.19
-- Dumped by pg_dump version 15.19

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: alerta_stock; Type: TABLE; Schema: public; Owner: regalito_admin
--

CREATE TABLE public.alerta_stock (
    id_alerta integer NOT NULL,
    id_inventario integer NOT NULL,
    mensaje character varying(150) NOT NULL,
    fecha_generacion timestamp without time zone NOT NULL,
    estado character varying(20) NOT NULL
);


ALTER TABLE public.alerta_stock OWNER TO regalito_admin;

--
-- Name: alerta_stock_id_alerta_seq; Type: SEQUENCE; Schema: public; Owner: regalito_admin
--

CREATE SEQUENCE public.alerta_stock_id_alerta_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.alerta_stock_id_alerta_seq OWNER TO regalito_admin;

--
-- Name: alerta_stock_id_alerta_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: regalito_admin
--

ALTER SEQUENCE public.alerta_stock_id_alerta_seq OWNED BY public.alerta_stock.id_alerta;


--
-- Name: area_bodega; Type: TABLE; Schema: public; Owner: regalito_admin
--

CREATE TABLE public.area_bodega (
    id_area integer NOT NULL,
    id_sucursal integer NOT NULL,
    nombre_area character varying(50) NOT NULL
);


ALTER TABLE public.area_bodega OWNER TO regalito_admin;

--
-- Name: area_bodega_id_area_seq; Type: SEQUENCE; Schema: public; Owner: regalito_admin
--

CREATE SEQUENCE public.area_bodega_id_area_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.area_bodega_id_area_seq OWNER TO regalito_admin;

--
-- Name: area_bodega_id_area_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: regalito_admin
--

ALTER SEQUENCE public.area_bodega_id_area_seq OWNED BY public.area_bodega.id_area;


--
-- Name: bitacora_auditoria; Type: TABLE; Schema: public; Owner: regalito_admin
--

CREATE TABLE public.bitacora_auditoria (
    id_bitacora integer NOT NULL,
    id_usuario integer NOT NULL,
    tabla_afectada character varying(50) NOT NULL,
    accion character varying(20) NOT NULL,
    descripcion text NOT NULL,
    fecha_hora timestamp without time zone NOT NULL
);


ALTER TABLE public.bitacora_auditoria OWNER TO regalito_admin;

--
-- Name: bitacora_auditoria_id_bitacora_seq; Type: SEQUENCE; Schema: public; Owner: regalito_admin
--

CREATE SEQUENCE public.bitacora_auditoria_id_bitacora_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.bitacora_auditoria_id_bitacora_seq OWNER TO regalito_admin;

--
-- Name: bitacora_auditoria_id_bitacora_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: regalito_admin
--

ALTER SEQUENCE public.bitacora_auditoria_id_bitacora_seq OWNED BY public.bitacora_auditoria.id_bitacora;


--
-- Name: caja; Type: TABLE; Schema: public; Owner: regalito_admin
--

CREATE TABLE public.caja (
    id_caja integer NOT NULL,
    id_sucursal integer NOT NULL,
    descripcion character varying(50) NOT NULL,
    estado character varying(20) NOT NULL
);


ALTER TABLE public.caja OWNER TO regalito_admin;

--
-- Name: caja_id_caja_seq; Type: SEQUENCE; Schema: public; Owner: regalito_admin
--

CREATE SEQUENCE public.caja_id_caja_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.caja_id_caja_seq OWNER TO regalito_admin;

--
-- Name: caja_id_caja_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: regalito_admin
--

ALTER SEQUENCE public.caja_id_caja_seq OWNED BY public.caja.id_caja;


--
-- Name: categoria; Type: TABLE; Schema: public; Owner: regalito_admin
--

CREATE TABLE public.categoria (
    id_categoria integer NOT NULL,
    nombre character varying(50) NOT NULL,
    estado character varying(20) NOT NULL
);


ALTER TABLE public.categoria OWNER TO regalito_admin;

--
-- Name: categoria_id_categoria_seq; Type: SEQUENCE; Schema: public; Owner: regalito_admin
--

CREATE SEQUENCE public.categoria_id_categoria_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.categoria_id_categoria_seq OWNER TO regalito_admin;

--
-- Name: categoria_id_categoria_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: regalito_admin
--

ALTER SEQUENCE public.categoria_id_categoria_seq OWNED BY public.categoria.id_categoria;


--
-- Name: cierre_caja_ciegas; Type: TABLE; Schema: public; Owner: regalito_admin
--

CREATE TABLE public.cierre_caja_ciegas (
    id_cierre integer NOT NULL,
    id_turno integer NOT NULL,
    id_usuario_cajero integer NOT NULL,
    id_usuario_supervisor integer NOT NULL,
    total_contado_ciegas numeric(10,2) NOT NULL,
    total_calculado_sistema numeric(10,2) NOT NULL,
    diferencia numeric(10,2) NOT NULL,
    observaciones text,
    fecha_cierre timestamp without time zone NOT NULL
);


ALTER TABLE public.cierre_caja_ciegas OWNER TO regalito_admin;

--
-- Name: cierre_caja_ciegas_id_cierre_seq; Type: SEQUENCE; Schema: public; Owner: regalito_admin
--

CREATE SEQUENCE public.cierre_caja_ciegas_id_cierre_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.cierre_caja_ciegas_id_cierre_seq OWNER TO regalito_admin;

--
-- Name: cierre_caja_ciegas_id_cierre_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: regalito_admin
--

ALTER SEQUENCE public.cierre_caja_ciegas_id_cierre_seq OWNED BY public.cierre_caja_ciegas.id_cierre;


--
-- Name: cliente; Type: TABLE; Schema: public; Owner: regalito_admin
--

CREATE TABLE public.cliente (
    id_cliente integer NOT NULL,
    id_tipo_cliente integer NOT NULL,
    id_municipio integer,
    nit character varying(15) NOT NULL,
    nombre_comercial character varying(120) NOT NULL,
    direccion character varying(200)
);


ALTER TABLE public.cliente OWNER TO regalito_admin;

--
-- Name: cliente_contacto; Type: TABLE; Schema: public; Owner: regalito_admin
--

CREATE TABLE public.cliente_contacto (
    id_contacto integer NOT NULL,
    id_cliente integer NOT NULL,
    telefono character varying(20),
    correo character varying(100)
);


ALTER TABLE public.cliente_contacto OWNER TO regalito_admin;

--
-- Name: cliente_contacto_id_contacto_seq; Type: SEQUENCE; Schema: public; Owner: regalito_admin
--

CREATE SEQUENCE public.cliente_contacto_id_contacto_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.cliente_contacto_id_contacto_seq OWNER TO regalito_admin;

--
-- Name: cliente_contacto_id_contacto_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: regalito_admin
--

ALTER SEQUENCE public.cliente_contacto_id_contacto_seq OWNED BY public.cliente_contacto.id_contacto;


--
-- Name: cliente_id_cliente_seq; Type: SEQUENCE; Schema: public; Owner: regalito_admin
--

CREATE SEQUENCE public.cliente_id_cliente_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.cliente_id_cliente_seq OWNER TO regalito_admin;

--
-- Name: cliente_id_cliente_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: regalito_admin
--

ALTER SEQUENCE public.cliente_id_cliente_seq OWNED BY public.cliente.id_cliente;


--
-- Name: compra; Type: TABLE; Schema: public; Owner: regalito_admin
--

CREATE TABLE public.compra (
    id_compra integer NOT NULL,
    id_orden integer,
    id_proveedor integer NOT NULL,
    id_usuario integer NOT NULL,
    numero_factura_proveedor character varying(50) NOT NULL,
    fecha_ingreso date NOT NULL,
    subtotal_mercaderia numeric(10,2) NOT NULL,
    gasto_flete numeric(10,2) NOT NULL,
    gasto_cargadores numeric(10,2) NOT NULL,
    total_compra numeric(10,2) NOT NULL
);


ALTER TABLE public.compra OWNER TO regalito_admin;

--
-- Name: compra_id_compra_seq; Type: SEQUENCE; Schema: public; Owner: regalito_admin
--

CREATE SEQUENCE public.compra_id_compra_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.compra_id_compra_seq OWNER TO regalito_admin;

--
-- Name: compra_id_compra_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: regalito_admin
--

ALTER SEQUENCE public.compra_id_compra_seq OWNED BY public.compra.id_compra;


--
-- Name: denominacion_efectivo; Type: TABLE; Schema: public; Owner: regalito_admin
--

CREATE TABLE public.denominacion_efectivo (
    id_denominacion integer NOT NULL,
    valor numeric(10,2) NOT NULL,
    tipo character varying(15) NOT NULL
);


ALTER TABLE public.denominacion_efectivo OWNER TO regalito_admin;

--
-- Name: denominacion_efectivo_id_denominacion_seq; Type: SEQUENCE; Schema: public; Owner: regalito_admin
--

CREATE SEQUENCE public.denominacion_efectivo_id_denominacion_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.denominacion_efectivo_id_denominacion_seq OWNER TO regalito_admin;

--
-- Name: denominacion_efectivo_id_denominacion_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: regalito_admin
--

ALTER SEQUENCE public.denominacion_efectivo_id_denominacion_seq OWNED BY public.denominacion_efectivo.id_denominacion;


--
-- Name: departamento_geografico; Type: TABLE; Schema: public; Owner: regalito_admin
--

CREATE TABLE public.departamento_geografico (
    id_departamento integer NOT NULL,
    nombre character varying(50) NOT NULL
);


ALTER TABLE public.departamento_geografico OWNER TO regalito_admin;

--
-- Name: departamento_geografico_id_departamento_seq; Type: SEQUENCE; Schema: public; Owner: regalito_admin
--

CREATE SEQUENCE public.departamento_geografico_id_departamento_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.departamento_geografico_id_departamento_seq OWNER TO regalito_admin;

--
-- Name: departamento_geografico_id_departamento_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: regalito_admin
--

ALTER SEQUENCE public.departamento_geografico_id_departamento_seq OWNED BY public.departamento_geografico.id_departamento;


--
-- Name: detalle_arqueo_efectivo; Type: TABLE; Schema: public; Owner: regalito_admin
--

CREATE TABLE public.detalle_arqueo_efectivo (
    id_detalle_arqueo integer NOT NULL,
    id_cierre integer NOT NULL,
    id_denominacion integer NOT NULL,
    cantidad_piezas integer NOT NULL,
    subtotal numeric(10,2) NOT NULL
);


ALTER TABLE public.detalle_arqueo_efectivo OWNER TO regalito_admin;

--
-- Name: detalle_arqueo_efectivo_id_detalle_arqueo_seq; Type: SEQUENCE; Schema: public; Owner: regalito_admin
--

CREATE SEQUENCE public.detalle_arqueo_efectivo_id_detalle_arqueo_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.detalle_arqueo_efectivo_id_detalle_arqueo_seq OWNER TO regalito_admin;

--
-- Name: detalle_arqueo_efectivo_id_detalle_arqueo_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: regalito_admin
--

ALTER SEQUENCE public.detalle_arqueo_efectivo_id_detalle_arqueo_seq OWNED BY public.detalle_arqueo_efectivo.id_detalle_arqueo;


--
-- Name: detalle_compra; Type: TABLE; Schema: public; Owner: regalito_admin
--

CREATE TABLE public.detalle_compra (
    id_detalle_compra integer NOT NULL,
    id_compra integer NOT NULL,
    id_variante integer NOT NULL,
    cantidad_recibida integer NOT NULL,
    costo_unitario numeric(10,2) NOT NULL,
    subtotal numeric(10,2) NOT NULL
);


ALTER TABLE public.detalle_compra OWNER TO regalito_admin;

--
-- Name: detalle_compra_id_detalle_compra_seq; Type: SEQUENCE; Schema: public; Owner: regalito_admin
--

CREATE SEQUENCE public.detalle_compra_id_detalle_compra_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.detalle_compra_id_detalle_compra_seq OWNER TO regalito_admin;

--
-- Name: detalle_compra_id_detalle_compra_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: regalito_admin
--

ALTER SEQUENCE public.detalle_compra_id_detalle_compra_seq OWNED BY public.detalle_compra.id_detalle_compra;


--
-- Name: detalle_merma; Type: TABLE; Schema: public; Owner: regalito_admin
--

CREATE TABLE public.detalle_merma (
    id_detalle_merma integer NOT NULL,
    id_merma integer NOT NULL,
    id_variante integer NOT NULL,
    id_motivo integer NOT NULL,
    cantidad integer NOT NULL,
    costo_perdida numeric(10,2) NOT NULL
);


ALTER TABLE public.detalle_merma OWNER TO regalito_admin;

--
-- Name: detalle_merma_id_detalle_merma_seq; Type: SEQUENCE; Schema: public; Owner: regalito_admin
--

CREATE SEQUENCE public.detalle_merma_id_detalle_merma_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.detalle_merma_id_detalle_merma_seq OWNER TO regalito_admin;

--
-- Name: detalle_merma_id_detalle_merma_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: regalito_admin
--

ALTER SEQUENCE public.detalle_merma_id_detalle_merma_seq OWNED BY public.detalle_merma.id_detalle_merma;


--
-- Name: detalle_orden_compra; Type: TABLE; Schema: public; Owner: regalito_admin
--

CREATE TABLE public.detalle_orden_compra (
    id_detalle_orden integer NOT NULL,
    id_orden integer NOT NULL,
    id_variante integer NOT NULL,
    cantidad_pedida integer NOT NULL,
    costo_pactado numeric(10,2) NOT NULL
);


ALTER TABLE public.detalle_orden_compra OWNER TO regalito_admin;

--
-- Name: detalle_orden_compra_id_detalle_orden_seq; Type: SEQUENCE; Schema: public; Owner: regalito_admin
--

CREATE SEQUENCE public.detalle_orden_compra_id_detalle_orden_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.detalle_orden_compra_id_detalle_orden_seq OWNER TO regalito_admin;

--
-- Name: detalle_orden_compra_id_detalle_orden_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: regalito_admin
--

ALTER SEQUENCE public.detalle_orden_compra_id_detalle_orden_seq OWNED BY public.detalle_orden_compra.id_detalle_orden;


--
-- Name: detalle_venta; Type: TABLE; Schema: public; Owner: regalito_admin
--

CREATE TABLE public.detalle_venta (
    id_detalle_venta integer NOT NULL,
    id_venta integer NOT NULL,
    id_variante integer NOT NULL,
    cantidad integer NOT NULL,
    precio_unitario numeric(10,2) NOT NULL,
    descuento_item numeric(10,2) NOT NULL,
    subtotal numeric(10,2) NOT NULL
);


ALTER TABLE public.detalle_venta OWNER TO regalito_admin;

--
-- Name: detalle_venta_id_detalle_venta_seq; Type: SEQUENCE; Schema: public; Owner: regalito_admin
--

CREATE SEQUENCE public.detalle_venta_id_detalle_venta_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.detalle_venta_id_detalle_venta_seq OWNER TO regalito_admin;

--
-- Name: detalle_venta_id_detalle_venta_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: regalito_admin
--

ALTER SEQUENCE public.detalle_venta_id_detalle_venta_seq OWNED BY public.detalle_venta.id_detalle_venta;


--
-- Name: factura_fel; Type: TABLE; Schema: public; Owner: regalito_admin
--

CREATE TABLE public.factura_fel (
    id_factura integer NOT NULL,
    id_venta integer NOT NULL,
    numero_autorizacion_sat character varying(50) NOT NULL,
    serie character varying(20) NOT NULL,
    numero_dte character varying(30) NOT NULL,
    fecha_certificacion timestamp without time zone NOT NULL,
    nit_receptor character varying(15) NOT NULL,
    nombre_receptor character varying(120) NOT NULL,
    total_facturado numeric(10,2) NOT NULL
);


ALTER TABLE public.factura_fel OWNER TO regalito_admin;

--
-- Name: factura_fel_id_factura_seq; Type: SEQUENCE; Schema: public; Owner: regalito_admin
--

CREATE SEQUENCE public.factura_fel_id_factura_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.factura_fel_id_factura_seq OWNER TO regalito_admin;

--
-- Name: factura_fel_id_factura_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: regalito_admin
--

ALTER SEQUENCE public.factura_fel_id_factura_seq OWNED BY public.factura_fel.id_factura;


--
-- Name: historial_precio; Type: TABLE; Schema: public; Owner: regalito_admin
--

CREATE TABLE public.historial_precio (
    id_historial integer NOT NULL,
    id_variante integer NOT NULL,
    id_usuario integer NOT NULL,
    precio_anterior numeric(10,2) NOT NULL,
    precio_nuevo numeric(10,2) NOT NULL,
    fecha_modificacion timestamp without time zone NOT NULL
);


ALTER TABLE public.historial_precio OWNER TO regalito_admin;

--
-- Name: historial_precio_id_historial_seq; Type: SEQUENCE; Schema: public; Owner: regalito_admin
--

CREATE SEQUENCE public.historial_precio_id_historial_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.historial_precio_id_historial_seq OWNER TO regalito_admin;

--
-- Name: historial_precio_id_historial_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: regalito_admin
--

ALTER SEQUENCE public.historial_precio_id_historial_seq OWNED BY public.historial_precio.id_historial;


--
-- Name: intento_login; Type: TABLE; Schema: public; Owner: regalito_admin
--

CREATE TABLE public.intento_login (
    id_intento integer NOT NULL,
    username character varying(50) NOT NULL,
    intentos_fallidos integer NOT NULL,
    bloqueado_hasta timestamp without time zone,
    ultimo_intento timestamp without time zone NOT NULL
);


ALTER TABLE public.intento_login OWNER TO regalito_admin;

--
-- Name: intento_login_id_intento_seq; Type: SEQUENCE; Schema: public; Owner: regalito_admin
--

CREATE SEQUENCE public.intento_login_id_intento_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.intento_login_id_intento_seq OWNER TO regalito_admin;

--
-- Name: intento_login_id_intento_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: regalito_admin
--

ALTER SEQUENCE public.intento_login_id_intento_seq OWNED BY public.intento_login.id_intento;


--
-- Name: inventario_sucursal; Type: TABLE; Schema: public; Owner: regalito_admin
--

CREATE TABLE public.inventario_sucursal (
    id_inventario integer NOT NULL,
    id_variante integer NOT NULL,
    id_sucursal integer NOT NULL,
    id_area integer,
    stock_actual integer NOT NULL,
    stock_minimo integer NOT NULL,
    fecha_actualizacion timestamp without time zone NOT NULL
);


ALTER TABLE public.inventario_sucursal OWNER TO regalito_admin;

--
-- Name: inventario_sucursal_id_inventario_seq; Type: SEQUENCE; Schema: public; Owner: regalito_admin
--

CREATE SEQUENCE public.inventario_sucursal_id_inventario_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.inventario_sucursal_id_inventario_seq OWNER TO regalito_admin;

--
-- Name: inventario_sucursal_id_inventario_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: regalito_admin
--

ALTER SEQUENCE public.inventario_sucursal_id_inventario_seq OWNED BY public.inventario_sucursal.id_inventario;


--
-- Name: merma; Type: TABLE; Schema: public; Owner: regalito_admin
--

CREATE TABLE public.merma (
    id_merma integer NOT NULL,
    id_sucursal integer NOT NULL,
    id_usuario integer NOT NULL,
    fecha_merma timestamp without time zone NOT NULL,
    observaciones text
);


ALTER TABLE public.merma OWNER TO regalito_admin;

--
-- Name: merma_id_merma_seq; Type: SEQUENCE; Schema: public; Owner: regalito_admin
--

CREATE SEQUENCE public.merma_id_merma_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.merma_id_merma_seq OWNER TO regalito_admin;

--
-- Name: merma_id_merma_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: regalito_admin
--

ALTER SEQUENCE public.merma_id_merma_seq OWNED BY public.merma.id_merma;


--
-- Name: metodo_pago; Type: TABLE; Schema: public; Owner: regalito_admin
--

CREATE TABLE public.metodo_pago (
    id_metodo_pago integer NOT NULL,
    nombre character varying(30) NOT NULL
);


ALTER TABLE public.metodo_pago OWNER TO regalito_admin;

--
-- Name: metodo_pago_id_metodo_pago_seq; Type: SEQUENCE; Schema: public; Owner: regalito_admin
--

CREATE SEQUENCE public.metodo_pago_id_metodo_pago_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.metodo_pago_id_metodo_pago_seq OWNER TO regalito_admin;

--
-- Name: metodo_pago_id_metodo_pago_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: regalito_admin
--

ALTER SEQUENCE public.metodo_pago_id_metodo_pago_seq OWNED BY public.metodo_pago.id_metodo_pago;


--
-- Name: motivo_merma; Type: TABLE; Schema: public; Owner: regalito_admin
--

CREATE TABLE public.motivo_merma (
    id_motivo integer NOT NULL,
    descripcion character varying(100) NOT NULL
);


ALTER TABLE public.motivo_merma OWNER TO regalito_admin;

--
-- Name: motivo_merma_id_motivo_seq; Type: SEQUENCE; Schema: public; Owner: regalito_admin
--

CREATE SEQUENCE public.motivo_merma_id_motivo_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.motivo_merma_id_motivo_seq OWNER TO regalito_admin;

--
-- Name: motivo_merma_id_motivo_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: regalito_admin
--

ALTER SEQUENCE public.motivo_merma_id_motivo_seq OWNED BY public.motivo_merma.id_motivo;


--
-- Name: movimiento_caja; Type: TABLE; Schema: public; Owner: regalito_admin
--

CREATE TABLE public.movimiento_caja (
    id_movimiento integer NOT NULL,
    id_turno integer NOT NULL,
    id_tipo_movimiento integer NOT NULL,
    id_usuario integer NOT NULL,
    monto numeric(10,2) NOT NULL,
    justificacion character varying(255) NOT NULL,
    fecha_hora timestamp without time zone NOT NULL
);


ALTER TABLE public.movimiento_caja OWNER TO regalito_admin;

--
-- Name: movimiento_caja_id_movimiento_seq; Type: SEQUENCE; Schema: public; Owner: regalito_admin
--

CREATE SEQUENCE public.movimiento_caja_id_movimiento_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.movimiento_caja_id_movimiento_seq OWNER TO regalito_admin;

--
-- Name: movimiento_caja_id_movimiento_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: regalito_admin
--

ALTER SEQUENCE public.movimiento_caja_id_movimiento_seq OWNED BY public.movimiento_caja.id_movimiento;


--
-- Name: municipio; Type: TABLE; Schema: public; Owner: regalito_admin
--

CREATE TABLE public.municipio (
    id_municipio integer NOT NULL,
    id_departamento integer NOT NULL,
    nombre character varying(50) NOT NULL
);


ALTER TABLE public.municipio OWNER TO regalito_admin;

--
-- Name: municipio_id_municipio_seq; Type: SEQUENCE; Schema: public; Owner: regalito_admin
--

CREATE SEQUENCE public.municipio_id_municipio_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.municipio_id_municipio_seq OWNER TO regalito_admin;

--
-- Name: municipio_id_municipio_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: regalito_admin
--

ALTER SEQUENCE public.municipio_id_municipio_seq OWNED BY public.municipio.id_municipio;


--
-- Name: orden_compra; Type: TABLE; Schema: public; Owner: regalito_admin
--

CREATE TABLE public.orden_compra (
    id_orden integer NOT NULL,
    id_proveedor integer NOT NULL,
    id_usuario integer NOT NULL,
    fecha_emision date NOT NULL,
    total_estimado numeric(10,2) NOT NULL,
    estado character varying(20) NOT NULL
);


ALTER TABLE public.orden_compra OWNER TO regalito_admin;

--
-- Name: orden_compra_id_orden_seq; Type: SEQUENCE; Schema: public; Owner: regalito_admin
--

CREATE SEQUENCE public.orden_compra_id_orden_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.orden_compra_id_orden_seq OWNER TO regalito_admin;

--
-- Name: orden_compra_id_orden_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: regalito_admin
--

ALTER SEQUENCE public.orden_compra_id_orden_seq OWNED BY public.orden_compra.id_orden;


--
-- Name: pago_venta; Type: TABLE; Schema: public; Owner: regalito_admin
--

CREATE TABLE public.pago_venta (
    id_pago integer NOT NULL,
    id_venta integer NOT NULL,
    id_metodo_pago integer NOT NULL,
    monto_recibido numeric(10,2) NOT NULL,
    vuelto_entregado numeric(10,2) NOT NULL
);


ALTER TABLE public.pago_venta OWNER TO regalito_admin;

--
-- Name: pago_venta_id_pago_seq; Type: SEQUENCE; Schema: public; Owner: regalito_admin
--

CREATE SEQUENCE public.pago_venta_id_pago_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.pago_venta_id_pago_seq OWNER TO regalito_admin;

--
-- Name: pago_venta_id_pago_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: regalito_admin
--

ALTER SEQUENCE public.pago_venta_id_pago_seq OWNED BY public.pago_venta.id_pago;


--
-- Name: parametro_sistema; Type: TABLE; Schema: public; Owner: regalito_admin
--

CREATE TABLE public.parametro_sistema (
    id_parametro integer NOT NULL,
    clave character varying(50) NOT NULL,
    valor character varying(255) NOT NULL
);


ALTER TABLE public.parametro_sistema OWNER TO regalito_admin;

--
-- Name: parametro_sistema_id_parametro_seq; Type: SEQUENCE; Schema: public; Owner: regalito_admin
--

CREATE SEQUENCE public.parametro_sistema_id_parametro_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.parametro_sistema_id_parametro_seq OWNER TO regalito_admin;

--
-- Name: parametro_sistema_id_parametro_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: regalito_admin
--

ALTER SEQUENCE public.parametro_sistema_id_parametro_seq OWNED BY public.parametro_sistema.id_parametro;


--
-- Name: permiso; Type: TABLE; Schema: public; Owner: regalito_admin
--

CREATE TABLE public.permiso (
    id_permiso integer NOT NULL,
    modulo character varying(50) NOT NULL,
    codigo character varying(50) NOT NULL,
    descripcion character varying(150)
);


ALTER TABLE public.permiso OWNER TO regalito_admin;

--
-- Name: permiso_id_permiso_seq; Type: SEQUENCE; Schema: public; Owner: regalito_admin
--

CREATE SEQUENCE public.permiso_id_permiso_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.permiso_id_permiso_seq OWNER TO regalito_admin;

--
-- Name: permiso_id_permiso_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: regalito_admin
--

ALTER SEQUENCE public.permiso_id_permiso_seq OWNED BY public.permiso.id_permiso;


--
-- Name: producto; Type: TABLE; Schema: public; Owner: regalito_admin
--

CREATE TABLE public.producto (
    id_producto integer NOT NULL,
    id_subcategoria integer NOT NULL,
    id_unidad integer NOT NULL,
    nombre character varying(100) NOT NULL,
    descripcion text,
    imagen_url character varying(255),
    estado character varying(20) NOT NULL,
    fecha_creacion timestamp without time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.producto OWNER TO regalito_admin;

--
-- Name: producto_id_producto_seq; Type: SEQUENCE; Schema: public; Owner: regalito_admin
--

CREATE SEQUENCE public.producto_id_producto_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.producto_id_producto_seq OWNER TO regalito_admin;

--
-- Name: producto_id_producto_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: regalito_admin
--

ALTER SEQUENCE public.producto_id_producto_seq OWNED BY public.producto.id_producto;


--
-- Name: proveedor; Type: TABLE; Schema: public; Owner: regalito_admin
--

CREATE TABLE public.proveedor (
    id_proveedor integer NOT NULL,
    nombre_contacto character varying(100) NOT NULL,
    distribuidora character varying(100) NOT NULL,
    telefono character varying(20),
    correo character varying(100),
    cuenta_bancaria character varying(50),
    direccion character varying(150)
);


ALTER TABLE public.proveedor OWNER TO regalito_admin;

--
-- Name: proveedor_id_proveedor_seq; Type: SEQUENCE; Schema: public; Owner: regalito_admin
--

CREATE SEQUENCE public.proveedor_id_proveedor_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.proveedor_id_proveedor_seq OWNER TO regalito_admin;

--
-- Name: proveedor_id_proveedor_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: regalito_admin
--

ALTER SEQUENCE public.proveedor_id_proveedor_seq OWNED BY public.proveedor.id_proveedor;


--
-- Name: rol; Type: TABLE; Schema: public; Owner: regalito_admin
--

CREATE TABLE public.rol (
    id_rol integer NOT NULL,
    nombre character varying(50) NOT NULL,
    descripcion character varying(150),
    estado character varying(20) NOT NULL
);


ALTER TABLE public.rol OWNER TO regalito_admin;

--
-- Name: rol_id_rol_seq; Type: SEQUENCE; Schema: public; Owner: regalito_admin
--

CREATE SEQUENCE public.rol_id_rol_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.rol_id_rol_seq OWNER TO regalito_admin;

--
-- Name: rol_id_rol_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: regalito_admin
--

ALTER SEQUENCE public.rol_id_rol_seq OWNED BY public.rol.id_rol;


--
-- Name: rol_permiso; Type: TABLE; Schema: public; Owner: regalito_admin
--

CREATE TABLE public.rol_permiso (
    id_rol integer NOT NULL,
    id_permiso integer NOT NULL
);


ALTER TABLE public.rol_permiso OWNER TO regalito_admin;

--
-- Name: sesion_usuario; Type: TABLE; Schema: public; Owner: regalito_admin
--

CREATE TABLE public.sesion_usuario (
    id_sesion integer NOT NULL,
    id_usuario integer NOT NULL,
    fecha_inicio timestamp without time zone NOT NULL,
    fecha_fin timestamp without time zone,
    ip_origen character varying(45)
);


ALTER TABLE public.sesion_usuario OWNER TO regalito_admin;

--
-- Name: sesion_usuario_id_sesion_seq; Type: SEQUENCE; Schema: public; Owner: regalito_admin
--

CREATE SEQUENCE public.sesion_usuario_id_sesion_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.sesion_usuario_id_sesion_seq OWNER TO regalito_admin;

--
-- Name: sesion_usuario_id_sesion_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: regalito_admin
--

ALTER SEQUENCE public.sesion_usuario_id_sesion_seq OWNED BY public.sesion_usuario.id_sesion;


--
-- Name: subcategoria; Type: TABLE; Schema: public; Owner: regalito_admin
--

CREATE TABLE public.subcategoria (
    id_subcategoria integer NOT NULL,
    id_categoria integer NOT NULL,
    nombre character varying(50) NOT NULL
);


ALTER TABLE public.subcategoria OWNER TO regalito_admin;

--
-- Name: subcategoria_id_subcategoria_seq; Type: SEQUENCE; Schema: public; Owner: regalito_admin
--

CREATE SEQUENCE public.subcategoria_id_subcategoria_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.subcategoria_id_subcategoria_seq OWNER TO regalito_admin;

--
-- Name: subcategoria_id_subcategoria_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: regalito_admin
--

ALTER SEQUENCE public.subcategoria_id_subcategoria_seq OWNED BY public.subcategoria.id_subcategoria;


--
-- Name: sucursal; Type: TABLE; Schema: public; Owner: regalito_admin
--

CREATE TABLE public.sucursal (
    id_sucursal integer NOT NULL,
    nombre character varying(100) NOT NULL,
    direccion character varying(200) NOT NULL,
    telefono character varying(20),
    estado character varying(20) NOT NULL
);


ALTER TABLE public.sucursal OWNER TO regalito_admin;

--
-- Name: sucursal_id_sucursal_seq; Type: SEQUENCE; Schema: public; Owner: regalito_admin
--

CREATE SEQUENCE public.sucursal_id_sucursal_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.sucursal_id_sucursal_seq OWNER TO regalito_admin;

--
-- Name: sucursal_id_sucursal_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: regalito_admin
--

ALTER SEQUENCE public.sucursal_id_sucursal_seq OWNED BY public.sucursal.id_sucursal;


--
-- Name: sync_cache_metadata; Type: TABLE; Schema: public; Owner: regalito_admin
--

CREATE TABLE public.sync_cache_metadata (
    id_sync integer NOT NULL,
    tabla character varying(50) NOT NULL,
    registros_sincronizados integer NOT NULL,
    fecha_sincronizacion timestamp without time zone NOT NULL
);


ALTER TABLE public.sync_cache_metadata OWNER TO regalito_admin;

--
-- Name: sync_cache_metadata_id_sync_seq; Type: SEQUENCE; Schema: public; Owner: regalito_admin
--

CREATE SEQUENCE public.sync_cache_metadata_id_sync_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.sync_cache_metadata_id_sync_seq OWNER TO regalito_admin;

--
-- Name: sync_cache_metadata_id_sync_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: regalito_admin
--

ALTER SEQUENCE public.sync_cache_metadata_id_sync_seq OWNED BY public.sync_cache_metadata.id_sync;


--
-- Name: sync_queue; Type: TABLE; Schema: public; Owner: regalito_admin
--

CREATE TABLE public.sync_queue (
    id_sync integer NOT NULL,
    idempotency_key character varying(36) NOT NULL,
    entidad character varying(50) NOT NULL,
    entidad_id integer NOT NULL,
    operacion character varying(20) NOT NULL,
    payload text NOT NULL,
    estado character varying(20) NOT NULL,
    intentos integer,
    ultimo_error text,
    creado_en timestamp without time zone,
    actualizado_en timestamp without time zone
);


ALTER TABLE public.sync_queue OWNER TO regalito_admin;

--
-- Name: sync_queue_id_sync_seq; Type: SEQUENCE; Schema: public; Owner: regalito_admin
--

CREATE SEQUENCE public.sync_queue_id_sync_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.sync_queue_id_sync_seq OWNER TO regalito_admin;

--
-- Name: sync_queue_id_sync_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: regalito_admin
--

ALTER SEQUENCE public.sync_queue_id_sync_seq OWNED BY public.sync_queue.id_sync;


--
-- Name: tipo_cliente; Type: TABLE; Schema: public; Owner: regalito_admin
--

CREATE TABLE public.tipo_cliente (
    id_tipo_cliente integer NOT NULL,
    nombre character varying(50) NOT NULL,
    descuento_predeterminado numeric(5,2)
);


ALTER TABLE public.tipo_cliente OWNER TO regalito_admin;

--
-- Name: tipo_cliente_id_tipo_cliente_seq; Type: SEQUENCE; Schema: public; Owner: regalito_admin
--

CREATE SEQUENCE public.tipo_cliente_id_tipo_cliente_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.tipo_cliente_id_tipo_cliente_seq OWNER TO regalito_admin;

--
-- Name: tipo_cliente_id_tipo_cliente_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: regalito_admin
--

ALTER SEQUENCE public.tipo_cliente_id_tipo_cliente_seq OWNED BY public.tipo_cliente.id_tipo_cliente;


--
-- Name: tipo_movimiento_caja; Type: TABLE; Schema: public; Owner: regalito_admin
--

CREATE TABLE public.tipo_movimiento_caja (
    id_tipo_movimiento integer NOT NULL,
    nombre character varying(50) NOT NULL
);


ALTER TABLE public.tipo_movimiento_caja OWNER TO regalito_admin;

--
-- Name: tipo_movimiento_caja_id_tipo_movimiento_seq; Type: SEQUENCE; Schema: public; Owner: regalito_admin
--

CREATE SEQUENCE public.tipo_movimiento_caja_id_tipo_movimiento_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.tipo_movimiento_caja_id_tipo_movimiento_seq OWNER TO regalito_admin;

--
-- Name: tipo_movimiento_caja_id_tipo_movimiento_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: regalito_admin
--

ALTER SEQUENCE public.tipo_movimiento_caja_id_tipo_movimiento_seq OWNED BY public.tipo_movimiento_caja.id_tipo_movimiento;


--
-- Name: traslado_inventario; Type: TABLE; Schema: public; Owner: regalito_admin
--

CREATE TABLE public.traslado_inventario (
    id_traslado integer NOT NULL,
    id_variante integer NOT NULL,
    id_sucursal_origen integer NOT NULL,
    id_sucursal_destino integer NOT NULL,
    cantidad integer NOT NULL,
    fecha_traslado timestamp without time zone NOT NULL
);


ALTER TABLE public.traslado_inventario OWNER TO regalito_admin;

--
-- Name: traslado_inventario_id_traslado_seq; Type: SEQUENCE; Schema: public; Owner: regalito_admin
--

CREATE SEQUENCE public.traslado_inventario_id_traslado_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.traslado_inventario_id_traslado_seq OWNER TO regalito_admin;

--
-- Name: traslado_inventario_id_traslado_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: regalito_admin
--

ALTER SEQUENCE public.traslado_inventario_id_traslado_seq OWNED BY public.traslado_inventario.id_traslado;


--
-- Name: turno_caja; Type: TABLE; Schema: public; Owner: regalito_admin
--

CREATE TABLE public.turno_caja (
    id_turno integer NOT NULL,
    id_caja integer NOT NULL,
    id_usuario integer NOT NULL,
    monto_apertura numeric(10,2) NOT NULL,
    fecha_apertura timestamp without time zone NOT NULL,
    fecha_cierre timestamp without time zone,
    estado character varying(20) NOT NULL,
    monto_cierre numeric(10,2),
    notas text
);


ALTER TABLE public.turno_caja OWNER TO regalito_admin;

--
-- Name: turno_caja_id_turno_seq; Type: SEQUENCE; Schema: public; Owner: regalito_admin
--

CREATE SEQUENCE public.turno_caja_id_turno_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.turno_caja_id_turno_seq OWNER TO regalito_admin;

--
-- Name: turno_caja_id_turno_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: regalito_admin
--

ALTER SEQUENCE public.turno_caja_id_turno_seq OWNED BY public.turno_caja.id_turno;


--
-- Name: unidad_medida; Type: TABLE; Schema: public; Owner: regalito_admin
--

CREATE TABLE public.unidad_medida (
    id_unidad integer NOT NULL,
    codigo character varying(10) NOT NULL,
    descripcion character varying(50) NOT NULL
);


ALTER TABLE public.unidad_medida OWNER TO regalito_admin;

--
-- Name: unidad_medida_id_unidad_seq; Type: SEQUENCE; Schema: public; Owner: regalito_admin
--

CREATE SEQUENCE public.unidad_medida_id_unidad_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.unidad_medida_id_unidad_seq OWNER TO regalito_admin;

--
-- Name: unidad_medida_id_unidad_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: regalito_admin
--

ALTER SEQUENCE public.unidad_medida_id_unidad_seq OWNED BY public.unidad_medida.id_unidad;


--
-- Name: usuario; Type: TABLE; Schema: public; Owner: regalito_admin
--

CREATE TABLE public.usuario (
    id_usuario integer NOT NULL,
    id_rol integer NOT NULL,
    nombre_completo character varying(100) NOT NULL,
    username character varying(50) NOT NULL,
    password_hash character varying(255) NOT NULL,
    estado character varying(20) NOT NULL,
    fecha_creacion timestamp without time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.usuario OWNER TO regalito_admin;

--
-- Name: usuario_id_usuario_seq; Type: SEQUENCE; Schema: public; Owner: regalito_admin
--

CREATE SEQUENCE public.usuario_id_usuario_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.usuario_id_usuario_seq OWNER TO regalito_admin;

--
-- Name: usuario_id_usuario_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: regalito_admin
--

ALTER SEQUENCE public.usuario_id_usuario_seq OWNED BY public.usuario.id_usuario;


--
-- Name: variante_producto; Type: TABLE; Schema: public; Owner: regalito_admin
--

CREATE TABLE public.variante_producto (
    id_variante integer NOT NULL,
    id_producto integer NOT NULL,
    codigo_barras character varying(50),
    talla character varying(20),
    color character varying(30),
    precio_detalle numeric(10,2) NOT NULL,
    precio_mayoreo numeric(10,2) NOT NULL,
    costo_promedio numeric(10,2) NOT NULL
);


ALTER TABLE public.variante_producto OWNER TO regalito_admin;

--
-- Name: variante_producto_id_variante_seq; Type: SEQUENCE; Schema: public; Owner: regalito_admin
--

CREATE SEQUENCE public.variante_producto_id_variante_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.variante_producto_id_variante_seq OWNER TO regalito_admin;

--
-- Name: variante_producto_id_variante_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: regalito_admin
--

ALTER SEQUENCE public.variante_producto_id_variante_seq OWNED BY public.variante_producto.id_variante;


--
-- Name: venta; Type: TABLE; Schema: public; Owner: regalito_admin
--

CREATE TABLE public.venta (
    id_venta integer NOT NULL,
    id_turno integer NOT NULL,
    id_cliente integer,
    id_usuario integer NOT NULL,
    fecha_venta timestamp without time zone NOT NULL,
    subtotal numeric(10,2) NOT NULL,
    descuento_total numeric(10,2) NOT NULL,
    total_venta numeric(10,2) NOT NULL,
    estado character varying(20) NOT NULL
);


ALTER TABLE public.venta OWNER TO regalito_admin;

--
-- Name: venta_id_venta_seq; Type: SEQUENCE; Schema: public; Owner: regalito_admin
--

CREATE SEQUENCE public.venta_id_venta_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.venta_id_venta_seq OWNER TO regalito_admin;

--
-- Name: venta_id_venta_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: regalito_admin
--

ALTER SEQUENCE public.venta_id_venta_seq OWNED BY public.venta.id_venta;


--
-- Name: alerta_stock id_alerta; Type: DEFAULT; Schema: public; Owner: regalito_admin
--

ALTER TABLE ONLY public.alerta_stock ALTER COLUMN id_alerta SET DEFAULT nextval('public.alerta_stock_id_alerta_seq'::regclass);


--
-- Name: area_bodega id_area; Type: DEFAULT; Schema: public; Owner: regalito_admin
--

ALTER TABLE ONLY public.area_bodega ALTER COLUMN id_area SET DEFAULT nextval('public.area_bodega_id_area_seq'::regclass);


--
-- Name: bitacora_auditoria id_bitacora; Type: DEFAULT; Schema: public; Owner: regalito_admin
--

ALTER TABLE ONLY public.bitacora_auditoria ALTER COLUMN id_bitacora SET DEFAULT nextval('public.bitacora_auditoria_id_bitacora_seq'::regclass);


--
-- Name: caja id_caja; Type: DEFAULT; Schema: public; Owner: regalito_admin
--

ALTER TABLE ONLY public.caja ALTER COLUMN id_caja SET DEFAULT nextval('public.caja_id_caja_seq'::regclass);


--
-- Name: categoria id_categoria; Type: DEFAULT; Schema: public; Owner: regalito_admin
--

ALTER TABLE ONLY public.categoria ALTER COLUMN id_categoria SET DEFAULT nextval('public.categoria_id_categoria_seq'::regclass);


--
-- Name: cierre_caja_ciegas id_cierre; Type: DEFAULT; Schema: public; Owner: regalito_admin
--

ALTER TABLE ONLY public.cierre_caja_ciegas ALTER COLUMN id_cierre SET DEFAULT nextval('public.cierre_caja_ciegas_id_cierre_seq'::regclass);


--
-- Name: cliente id_cliente; Type: DEFAULT; Schema: public; Owner: regalito_admin
--

ALTER TABLE ONLY public.cliente ALTER COLUMN id_cliente SET DEFAULT nextval('public.cliente_id_cliente_seq'::regclass);


--
-- Name: cliente_contacto id_contacto; Type: DEFAULT; Schema: public; Owner: regalito_admin
--

ALTER TABLE ONLY public.cliente_contacto ALTER COLUMN id_contacto SET DEFAULT nextval('public.cliente_contacto_id_contacto_seq'::regclass);


--
-- Name: compra id_compra; Type: DEFAULT; Schema: public; Owner: regalito_admin
--

ALTER TABLE ONLY public.compra ALTER COLUMN id_compra SET DEFAULT nextval('public.compra_id_compra_seq'::regclass);


--
-- Name: denominacion_efectivo id_denominacion; Type: DEFAULT; Schema: public; Owner: regalito_admin
--

ALTER TABLE ONLY public.denominacion_efectivo ALTER COLUMN id_denominacion SET DEFAULT nextval('public.denominacion_efectivo_id_denominacion_seq'::regclass);


--
-- Name: departamento_geografico id_departamento; Type: DEFAULT; Schema: public; Owner: regalito_admin
--

ALTER TABLE ONLY public.departamento_geografico ALTER COLUMN id_departamento SET DEFAULT nextval('public.departamento_geografico_id_departamento_seq'::regclass);


--
-- Name: detalle_arqueo_efectivo id_detalle_arqueo; Type: DEFAULT; Schema: public; Owner: regalito_admin
--

ALTER TABLE ONLY public.detalle_arqueo_efectivo ALTER COLUMN id_detalle_arqueo SET DEFAULT nextval('public.detalle_arqueo_efectivo_id_detalle_arqueo_seq'::regclass);


--
-- Name: detalle_compra id_detalle_compra; Type: DEFAULT; Schema: public; Owner: regalito_admin
--

ALTER TABLE ONLY public.detalle_compra ALTER COLUMN id_detalle_compra SET DEFAULT nextval('public.detalle_compra_id_detalle_compra_seq'::regclass);


--
-- Name: detalle_merma id_detalle_merma; Type: DEFAULT; Schema: public; Owner: regalito_admin
--

ALTER TABLE ONLY public.detalle_merma ALTER COLUMN id_detalle_merma SET DEFAULT nextval('public.detalle_merma_id_detalle_merma_seq'::regclass);


--
-- Name: detalle_orden_compra id_detalle_orden; Type: DEFAULT; Schema: public; Owner: regalito_admin
--

ALTER TABLE ONLY public.detalle_orden_compra ALTER COLUMN id_detalle_orden SET DEFAULT nextval('public.detalle_orden_compra_id_detalle_orden_seq'::regclass);


--
-- Name: detalle_venta id_detalle_venta; Type: DEFAULT; Schema: public; Owner: regalito_admin
--

ALTER TABLE ONLY public.detalle_venta ALTER COLUMN id_detalle_venta SET DEFAULT nextval('public.detalle_venta_id_detalle_venta_seq'::regclass);


--
-- Name: factura_fel id_factura; Type: DEFAULT; Schema: public; Owner: regalito_admin
--

ALTER TABLE ONLY public.factura_fel ALTER COLUMN id_factura SET DEFAULT nextval('public.factura_fel_id_factura_seq'::regclass);


--
-- Name: historial_precio id_historial; Type: DEFAULT; Schema: public; Owner: regalito_admin
--

ALTER TABLE ONLY public.historial_precio ALTER COLUMN id_historial SET DEFAULT nextval('public.historial_precio_id_historial_seq'::regclass);


--
-- Name: intento_login id_intento; Type: DEFAULT; Schema: public; Owner: regalito_admin
--

ALTER TABLE ONLY public.intento_login ALTER COLUMN id_intento SET DEFAULT nextval('public.intento_login_id_intento_seq'::regclass);


--
-- Name: inventario_sucursal id_inventario; Type: DEFAULT; Schema: public; Owner: regalito_admin
--

ALTER TABLE ONLY public.inventario_sucursal ALTER COLUMN id_inventario SET DEFAULT nextval('public.inventario_sucursal_id_inventario_seq'::regclass);


--
-- Name: merma id_merma; Type: DEFAULT; Schema: public; Owner: regalito_admin
--

ALTER TABLE ONLY public.merma ALTER COLUMN id_merma SET DEFAULT nextval('public.merma_id_merma_seq'::regclass);


--
-- Name: metodo_pago id_metodo_pago; Type: DEFAULT; Schema: public; Owner: regalito_admin
--

ALTER TABLE ONLY public.metodo_pago ALTER COLUMN id_metodo_pago SET DEFAULT nextval('public.metodo_pago_id_metodo_pago_seq'::regclass);


--
-- Name: motivo_merma id_motivo; Type: DEFAULT; Schema: public; Owner: regalito_admin
--

ALTER TABLE ONLY public.motivo_merma ALTER COLUMN id_motivo SET DEFAULT nextval('public.motivo_merma_id_motivo_seq'::regclass);


--
-- Name: movimiento_caja id_movimiento; Type: DEFAULT; Schema: public; Owner: regalito_admin
--

ALTER TABLE ONLY public.movimiento_caja ALTER COLUMN id_movimiento SET DEFAULT nextval('public.movimiento_caja_id_movimiento_seq'::regclass);


--
-- Name: municipio id_municipio; Type: DEFAULT; Schema: public; Owner: regalito_admin
--

ALTER TABLE ONLY public.municipio ALTER COLUMN id_municipio SET DEFAULT nextval('public.municipio_id_municipio_seq'::regclass);


--
-- Name: orden_compra id_orden; Type: DEFAULT; Schema: public; Owner: regalito_admin
--

ALTER TABLE ONLY public.orden_compra ALTER COLUMN id_orden SET DEFAULT nextval('public.orden_compra_id_orden_seq'::regclass);


--
-- Name: pago_venta id_pago; Type: DEFAULT; Schema: public; Owner: regalito_admin
--

ALTER TABLE ONLY public.pago_venta ALTER COLUMN id_pago SET DEFAULT nextval('public.pago_venta_id_pago_seq'::regclass);


--
-- Name: parametro_sistema id_parametro; Type: DEFAULT; Schema: public; Owner: regalito_admin
--

ALTER TABLE ONLY public.parametro_sistema ALTER COLUMN id_parametro SET DEFAULT nextval('public.parametro_sistema_id_parametro_seq'::regclass);


--
-- Name: permiso id_permiso; Type: DEFAULT; Schema: public; Owner: regalito_admin
--

ALTER TABLE ONLY public.permiso ALTER COLUMN id_permiso SET DEFAULT nextval('public.permiso_id_permiso_seq'::regclass);


--
-- Name: producto id_producto; Type: DEFAULT; Schema: public; Owner: regalito_admin
--

ALTER TABLE ONLY public.producto ALTER COLUMN id_producto SET DEFAULT nextval('public.producto_id_producto_seq'::regclass);


--
-- Name: proveedor id_proveedor; Type: DEFAULT; Schema: public; Owner: regalito_admin
--

ALTER TABLE ONLY public.proveedor ALTER COLUMN id_proveedor SET DEFAULT nextval('public.proveedor_id_proveedor_seq'::regclass);


--
-- Name: rol id_rol; Type: DEFAULT; Schema: public; Owner: regalito_admin
--

ALTER TABLE ONLY public.rol ALTER COLUMN id_rol SET DEFAULT nextval('public.rol_id_rol_seq'::regclass);


--
-- Name: sesion_usuario id_sesion; Type: DEFAULT; Schema: public; Owner: regalito_admin
--

ALTER TABLE ONLY public.sesion_usuario ALTER COLUMN id_sesion SET DEFAULT nextval('public.sesion_usuario_id_sesion_seq'::regclass);


--
-- Name: subcategoria id_subcategoria; Type: DEFAULT; Schema: public; Owner: regalito_admin
--

ALTER TABLE ONLY public.subcategoria ALTER COLUMN id_subcategoria SET DEFAULT nextval('public.subcategoria_id_subcategoria_seq'::regclass);


--
-- Name: sucursal id_sucursal; Type: DEFAULT; Schema: public; Owner: regalito_admin
--

ALTER TABLE ONLY public.sucursal ALTER COLUMN id_sucursal SET DEFAULT nextval('public.sucursal_id_sucursal_seq'::regclass);


--
-- Name: sync_cache_metadata id_sync; Type: DEFAULT; Schema: public; Owner: regalito_admin
--

ALTER TABLE ONLY public.sync_cache_metadata ALTER COLUMN id_sync SET DEFAULT nextval('public.sync_cache_metadata_id_sync_seq'::regclass);


--
-- Name: sync_queue id_sync; Type: DEFAULT; Schema: public; Owner: regalito_admin
--

ALTER TABLE ONLY public.sync_queue ALTER COLUMN id_sync SET DEFAULT nextval('public.sync_queue_id_sync_seq'::regclass);


--
-- Name: tipo_cliente id_tipo_cliente; Type: DEFAULT; Schema: public; Owner: regalito_admin
--

ALTER TABLE ONLY public.tipo_cliente ALTER COLUMN id_tipo_cliente SET DEFAULT nextval('public.tipo_cliente_id_tipo_cliente_seq'::regclass);


--
-- Name: tipo_movimiento_caja id_tipo_movimiento; Type: DEFAULT; Schema: public; Owner: regalito_admin
--

ALTER TABLE ONLY public.tipo_movimiento_caja ALTER COLUMN id_tipo_movimiento SET DEFAULT nextval('public.tipo_movimiento_caja_id_tipo_movimiento_seq'::regclass);


--
-- Name: traslado_inventario id_traslado; Type: DEFAULT; Schema: public; Owner: regalito_admin
--

ALTER TABLE ONLY public.traslado_inventario ALTER COLUMN id_traslado SET DEFAULT nextval('public.traslado_inventario_id_traslado_seq'::regclass);


--
-- Name: turno_caja id_turno; Type: DEFAULT; Schema: public; Owner: regalito_admin
--

ALTER TABLE ONLY public.turno_caja ALTER COLUMN id_turno SET DEFAULT nextval('public.turno_caja_id_turno_seq'::regclass);


--
-- Name: unidad_medida id_unidad; Type: DEFAULT; Schema: public; Owner: regalito_admin
--

ALTER TABLE ONLY public.unidad_medida ALTER COLUMN id_unidad SET DEFAULT nextval('public.unidad_medida_id_unidad_seq'::regclass);


--
-- Name: usuario id_usuario; Type: DEFAULT; Schema: public; Owner: regalito_admin
--

ALTER TABLE ONLY public.usuario ALTER COLUMN id_usuario SET DEFAULT nextval('public.usuario_id_usuario_seq'::regclass);


--
-- Name: variante_producto id_variante; Type: DEFAULT; Schema: public; Owner: regalito_admin
--

ALTER TABLE ONLY public.variante_producto ALTER COLUMN id_variante SET DEFAULT nextval('public.variante_producto_id_variante_seq'::regclass);


--
-- Name: venta id_venta; Type: DEFAULT; Schema: public; Owner: regalito_admin
--

ALTER TABLE ONLY public.venta ALTER COLUMN id_venta SET DEFAULT nextval('public.venta_id_venta_seq'::regclass);


--
-- Data for Name: alerta_stock; Type: TABLE DATA; Schema: public; Owner: regalito_admin
--

COPY public.alerta_stock (id_alerta, id_inventario, mensaje, fecha_generacion, estado) FROM stdin;
\.


--
-- Data for Name: area_bodega; Type: TABLE DATA; Schema: public; Owner: regalito_admin
--

COPY public.area_bodega (id_area, id_sucursal, nombre_area) FROM stdin;
\.


--
-- Data for Name: bitacora_auditoria; Type: TABLE DATA; Schema: public; Owner: regalito_admin
--

COPY public.bitacora_auditoria (id_bitacora, id_usuario, tabla_afectada, accion, descripcion, fecha_hora) FROM stdin;
\.


--
-- Data for Name: caja; Type: TABLE DATA; Schema: public; Owner: regalito_admin
--

COPY public.caja (id_caja, id_sucursal, descripcion, estado) FROM stdin;
\.


--
-- Data for Name: categoria; Type: TABLE DATA; Schema: public; Owner: regalito_admin
--

COPY public.categoria (id_categoria, nombre, estado) FROM stdin;
\.


--
-- Data for Name: cierre_caja_ciegas; Type: TABLE DATA; Schema: public; Owner: regalito_admin
--

COPY public.cierre_caja_ciegas (id_cierre, id_turno, id_usuario_cajero, id_usuario_supervisor, total_contado_ciegas, total_calculado_sistema, diferencia, observaciones, fecha_cierre) FROM stdin;
\.


--
-- Data for Name: cliente; Type: TABLE DATA; Schema: public; Owner: regalito_admin
--

COPY public.cliente (id_cliente, id_tipo_cliente, id_municipio, nit, nombre_comercial, direccion) FROM stdin;
\.


--
-- Data for Name: cliente_contacto; Type: TABLE DATA; Schema: public; Owner: regalito_admin
--

COPY public.cliente_contacto (id_contacto, id_cliente, telefono, correo) FROM stdin;
\.


--
-- Data for Name: compra; Type: TABLE DATA; Schema: public; Owner: regalito_admin
--

COPY public.compra (id_compra, id_orden, id_proveedor, id_usuario, numero_factura_proveedor, fecha_ingreso, subtotal_mercaderia, gasto_flete, gasto_cargadores, total_compra) FROM stdin;
\.


--
-- Data for Name: denominacion_efectivo; Type: TABLE DATA; Schema: public; Owner: regalito_admin
--

COPY public.denominacion_efectivo (id_denominacion, valor, tipo) FROM stdin;
\.


--
-- Data for Name: departamento_geografico; Type: TABLE DATA; Schema: public; Owner: regalito_admin
--

COPY public.departamento_geografico (id_departamento, nombre) FROM stdin;
\.


--
-- Data for Name: detalle_arqueo_efectivo; Type: TABLE DATA; Schema: public; Owner: regalito_admin
--

COPY public.detalle_arqueo_efectivo (id_detalle_arqueo, id_cierre, id_denominacion, cantidad_piezas, subtotal) FROM stdin;
\.


--
-- Data for Name: detalle_compra; Type: TABLE DATA; Schema: public; Owner: regalito_admin
--

COPY public.detalle_compra (id_detalle_compra, id_compra, id_variante, cantidad_recibida, costo_unitario, subtotal) FROM stdin;
\.


--
-- Data for Name: detalle_merma; Type: TABLE DATA; Schema: public; Owner: regalito_admin
--

COPY public.detalle_merma (id_detalle_merma, id_merma, id_variante, id_motivo, cantidad, costo_perdida) FROM stdin;
\.


--
-- Data for Name: detalle_orden_compra; Type: TABLE DATA; Schema: public; Owner: regalito_admin
--

COPY public.detalle_orden_compra (id_detalle_orden, id_orden, id_variante, cantidad_pedida, costo_pactado) FROM stdin;
\.


--
-- Data for Name: detalle_venta; Type: TABLE DATA; Schema: public; Owner: regalito_admin
--

COPY public.detalle_venta (id_detalle_venta, id_venta, id_variante, cantidad, precio_unitario, descuento_item, subtotal) FROM stdin;
\.


--
-- Data for Name: factura_fel; Type: TABLE DATA; Schema: public; Owner: regalito_admin
--

COPY public.factura_fel (id_factura, id_venta, numero_autorizacion_sat, serie, numero_dte, fecha_certificacion, nit_receptor, nombre_receptor, total_facturado) FROM stdin;
\.


--
-- Data for Name: historial_precio; Type: TABLE DATA; Schema: public; Owner: regalito_admin
--

COPY public.historial_precio (id_historial, id_variante, id_usuario, precio_anterior, precio_nuevo, fecha_modificacion) FROM stdin;
\.


--
-- Data for Name: intento_login; Type: TABLE DATA; Schema: public; Owner: regalito_admin
--

COPY public.intento_login (id_intento, username, intentos_fallidos, bloqueado_hasta, ultimo_intento) FROM stdin;
1	admin	1	\N	2026-10-19 00:29:31.889973
\.


--
-- Data for Name: inventario_sucursal; Type: TABLE DATA; Schema: public; Owner: regalito_admin
--

COPY public.inventario_sucursal (id_inventario, id_variante, id_sucursal, id_area, stock_actual, stock_minimo, fecha_actualizacion) FROM stdin;
\.


--
-- Data for Name: merma; Type: TABLE DATA; Schema: public; Owner: regalito_admin
--

COPY public.merma (id_merma, id_sucursal, id_usuario, fecha_merma, observaciones) FROM stdin;
\.


--
-- Data for Name: metodo_pago; Type: TABLE DATA; Schema: public; Owner: regalito_admin
--

COPY public.metodo_pago (id_metodo_pago, nombre) FROM stdin;
\.


--
-- Data for Name: motivo_merma; Type: TABLE DATA; Schema: public; Owner: regalito_admin
--

COPY public.motivo_merma (id_motivo, descripcion) FROM stdin;
\.


--
-- Data for Name: movimiento_caja; Type: TABLE DATA; Schema: public; Owner: regalito_admin
--

COPY public.movimiento_caja (id_movimiento, id_turno, id_tipo_movimiento, id_usuario, monto, justificacion, fecha_hora) FROM stdin;
\.


--
-- Data for Name: municipio; Type: TABLE DATA; Schema: public; Owner: regalito_admin
--

COPY public.municipio (id_municipio, id_departamento, nombre) FROM stdin;
\.


--
-- Data for Name: orden_compra; Type: TABLE DATA; Schema: public; Owner: regalito_admin
--

COPY public.orden_compra (id_orden, id_proveedor, id_usuario, fecha_emision, total_estimado, estado) FROM stdin;
\.


--
-- Data for Name: pago_venta; Type: TABLE DATA; Schema: public; Owner: regalito_admin
--

COPY public.pago_venta (id_pago, id_venta, id_metodo_pago, monto_recibido, vuelto_entregado) FROM stdin;
\.


--
-- Data for Name: parametro_sistema; Type: TABLE DATA; Schema: public; Owner: regalito_admin
--

COPY public.parametro_sistema (id_parametro, clave, valor) FROM stdin;
\.


--
-- Data for Name: permiso; Type: TABLE DATA; Schema: public; Owner: regalito_admin
--

COPY public.permiso (id_permiso, modulo, codigo, descripcion) FROM stdin;
\.


--
-- Data for Name: producto; Type: TABLE DATA; Schema: public; Owner: regalito_admin
--

COPY public.producto (id_producto, id_subcategoria, id_unidad, nombre, descripcion, imagen_url, estado, fecha_creacion) FROM stdin;
\.


--
-- Data for Name: proveedor; Type: TABLE DATA; Schema: public; Owner: regalito_admin
--

COPY public.proveedor (id_proveedor, nombre_contacto, distribuidora, telefono, correo, cuenta_bancaria, direccion) FROM stdin;
\.


--
-- Data for Name: rol; Type: TABLE DATA; Schema: public; Owner: regalito_admin
--

COPY public.rol (id_rol, nombre, descripcion, estado) FROM stdin;
1	Administradora	Acceso total al sistema	Activo
\.


--
-- Data for Name: rol_permiso; Type: TABLE DATA; Schema: public; Owner: regalito_admin
--

COPY public.rol_permiso (id_rol, id_permiso) FROM stdin;
\.


--
-- Data for Name: sesion_usuario; Type: TABLE DATA; Schema: public; Owner: regalito_admin
--

COPY public.sesion_usuario (id_sesion, id_usuario, fecha_inicio, fecha_fin, ip_origen) FROM stdin;
\.


--
-- Data for Name: subcategoria; Type: TABLE DATA; Schema: public; Owner: regalito_admin
--

COPY public.subcategoria (id_subcategoria, id_categoria, nombre) FROM stdin;
\.


--
-- Data for Name: sucursal; Type: TABLE DATA; Schema: public; Owner: regalito_admin
--

COPY public.sucursal (id_sucursal, nombre, direccion, telefono, estado) FROM stdin;
\.


--
-- Data for Name: sync_cache_metadata; Type: TABLE DATA; Schema: public; Owner: regalito_admin
--

COPY public.sync_cache_metadata (id_sync, tabla, registros_sincronizados, fecha_sincronizacion) FROM stdin;
\.


--
-- Data for Name: sync_queue; Type: TABLE DATA; Schema: public; Owner: regalito_admin
--

COPY public.sync_queue (id_sync, idempotency_key, entidad, entidad_id, operacion, payload, estado, intentos, ultimo_error, creado_en, actualizado_en) FROM stdin;
\.


--
-- Data for Name: tipo_cliente; Type: TABLE DATA; Schema: public; Owner: regalito_admin
--

COPY public.tipo_cliente (id_tipo_cliente, nombre, descuento_predeterminado) FROM stdin;
\.


--
-- Data for Name: tipo_movimiento_caja; Type: TABLE DATA; Schema: public; Owner: regalito_admin
--

COPY public.tipo_movimiento_caja (id_tipo_movimiento, nombre) FROM stdin;
\.


--
-- Data for Name: traslado_inventario; Type: TABLE DATA; Schema: public; Owner: regalito_admin
--

COPY public.traslado_inventario (id_traslado, id_variante, id_sucursal_origen, id_sucursal_destino, cantidad, fecha_traslado) FROM stdin;
\.


--
-- Data for Name: turno_caja; Type: TABLE DATA; Schema: public; Owner: regalito_admin
--

COPY public.turno_caja (id_turno, id_caja, id_usuario, monto_apertura, fecha_apertura, fecha_cierre, estado, monto_cierre, notas) FROM stdin;
\.


--
-- Data for Name: unidad_medida; Type: TABLE DATA; Schema: public; Owner: regalito_admin
--

COPY public.unidad_medida (id_unidad, codigo, descripcion) FROM stdin;
\.


--
-- Data for Name: usuario; Type: TABLE DATA; Schema: public; Owner: regalito_admin
--

COPY public.usuario (id_usuario, id_rol, nombre_completo, username, password_hash, estado, fecha_creacion) FROM stdin;
1	1	Super Administrador	admin	$2b$12$qD98Lo1tPvJhP0AfhkYtJuaSubSF4ZN60oHx.9Zaw6tZBF.5d253K	Activo	2026-10-05 20:16:10.799098
\.


--
-- Data for Name: variante_producto; Type: TABLE DATA; Schema: public; Owner: regalito_admin
--

COPY public.variante_producto (id_variante, id_producto, codigo_barras, talla, color, precio_detalle, precio_mayoreo, costo_promedio) FROM stdin;
\.


--
-- Data for Name: venta; Type: TABLE DATA; Schema: public; Owner: regalito_admin
--

COPY public.venta (id_venta, id_turno, id_cliente, id_usuario, fecha_venta, subtotal, descuento_total, total_venta, estado) FROM stdin;
\.


--
-- Name: alerta_stock_id_alerta_seq; Type: SEQUENCE SET; Schema: public; Owner: regalito_admin
--

SELECT pg_catalog.setval('public.alerta_stock_id_alerta_seq', 1, false);


--
-- Name: area_bodega_id_area_seq; Type: SEQUENCE SET; Schema: public; Owner: regalito_admin
--

SELECT pg_catalog.setval('public.area_bodega_id_area_seq', 1, false);


--
-- Name: bitacora_auditoria_id_bitacora_seq; Type: SEQUENCE SET; Schema: public; Owner: regalito_admin
--

SELECT pg_catalog.setval('public.bitacora_auditoria_id_bitacora_seq', 49, true);


--
-- Name: caja_id_caja_seq; Type: SEQUENCE SET; Schema: public; Owner: regalito_admin
--

SELECT pg_catalog.setval('public.caja_id_caja_seq', 1, false);


--
-- Name: categoria_id_categoria_seq; Type: SEQUENCE SET; Schema: public; Owner: regalito_admin
--

SELECT pg_catalog.setval('public.categoria_id_categoria_seq', 1, false);


--
-- Name: cierre_caja_ciegas_id_cierre_seq; Type: SEQUENCE SET; Schema: public; Owner: regalito_admin
--

SELECT pg_catalog.setval('public.cierre_caja_ciegas_id_cierre_seq', 1, false);


--
-- Name: cliente_contacto_id_contacto_seq; Type: SEQUENCE SET; Schema: public; Owner: regalito_admin
--

SELECT pg_catalog.setval('public.cliente_contacto_id_contacto_seq', 1, false);


--
-- Name: cliente_id_cliente_seq; Type: SEQUENCE SET; Schema: public; Owner: regalito_admin
--

SELECT pg_catalog.setval('public.cliente_id_cliente_seq', 1, false);


--
-- Name: compra_id_compra_seq; Type: SEQUENCE SET; Schema: public; Owner: regalito_admin
--

SELECT pg_catalog.setval('public.compra_id_compra_seq', 1, false);


--
-- Name: denominacion_efectivo_id_denominacion_seq; Type: SEQUENCE SET; Schema: public; Owner: regalito_admin
--

SELECT pg_catalog.setval('public.denominacion_efectivo_id_denominacion_seq', 1, false);


--
-- Name: departamento_geografico_id_departamento_seq; Type: SEQUENCE SET; Schema: public; Owner: regalito_admin
--

SELECT pg_catalog.setval('public.departamento_geografico_id_departamento_seq', 1, false);


--
-- Name: detalle_arqueo_efectivo_id_detalle_arqueo_seq; Type: SEQUENCE SET; Schema: public; Owner: regalito_admin
--

SELECT pg_catalog.setval('public.detalle_arqueo_efectivo_id_detalle_arqueo_seq', 1, false);


--
-- Name: detalle_compra_id_detalle_compra_seq; Type: SEQUENCE SET; Schema: public; Owner: regalito_admin
--

SELECT pg_catalog.setval('public.detalle_compra_id_detalle_compra_seq', 1, false);


--
-- Name: detalle_merma_id_detalle_merma_seq; Type: SEQUENCE SET; Schema: public; Owner: regalito_admin
--

SELECT pg_catalog.setval('public.detalle_merma_id_detalle_merma_seq', 1, false);


--
-- Name: detalle_orden_compra_id_detalle_orden_seq; Type: SEQUENCE SET; Schema: public; Owner: regalito_admin
--

SELECT pg_catalog.setval('public.detalle_orden_compra_id_detalle_orden_seq', 1, false);


--
-- Name: detalle_venta_id_detalle_venta_seq; Type: SEQUENCE SET; Schema: public; Owner: regalito_admin
--

SELECT pg_catalog.setval('public.detalle_venta_id_detalle_venta_seq', 1, false);


--
-- Name: factura_fel_id_factura_seq; Type: SEQUENCE SET; Schema: public; Owner: regalito_admin
--

SELECT pg_catalog.setval('public.factura_fel_id_factura_seq', 1, false);


--
-- Name: historial_precio_id_historial_seq; Type: SEQUENCE SET; Schema: public; Owner: regalito_admin
--

SELECT pg_catalog.setval('public.historial_precio_id_historial_seq', 1, false);


--
-- Name: intento_login_id_intento_seq; Type: SEQUENCE SET; Schema: public; Owner: regalito_admin
--

SELECT pg_catalog.setval('public.intento_login_id_intento_seq', 1, true);


--
-- Name: inventario_sucursal_id_inventario_seq; Type: SEQUENCE SET; Schema: public; Owner: regalito_admin
--

SELECT pg_catalog.setval('public.inventario_sucursal_id_inventario_seq', 1, false);


--
-- Name: merma_id_merma_seq; Type: SEQUENCE SET; Schema: public; Owner: regalito_admin
--

SELECT pg_catalog.setval('public.merma_id_merma_seq', 1, false);


--
-- Name: metodo_pago_id_metodo_pago_seq; Type: SEQUENCE SET; Schema: public; Owner: regalito_admin
--

SELECT pg_catalog.setval('public.metodo_pago_id_metodo_pago_seq', 1, false);


--
-- Name: motivo_merma_id_motivo_seq; Type: SEQUENCE SET; Schema: public; Owner: regalito_admin
--

SELECT pg_catalog.setval('public.motivo_merma_id_motivo_seq', 1, false);


--
-- Name: movimiento_caja_id_movimiento_seq; Type: SEQUENCE SET; Schema: public; Owner: regalito_admin
--

SELECT pg_catalog.setval('public.movimiento_caja_id_movimiento_seq', 1, false);


--
-- Name: municipio_id_municipio_seq; Type: SEQUENCE SET; Schema: public; Owner: regalito_admin
--

SELECT pg_catalog.setval('public.municipio_id_municipio_seq', 1, false);


--
-- Name: orden_compra_id_orden_seq; Type: SEQUENCE SET; Schema: public; Owner: regalito_admin
--

SELECT pg_catalog.setval('public.orden_compra_id_orden_seq', 1, false);


--
-- Name: pago_venta_id_pago_seq; Type: SEQUENCE SET; Schema: public; Owner: regalito_admin
--

SELECT pg_catalog.setval('public.pago_venta_id_pago_seq', 1, false);


--
-- Name: parametro_sistema_id_parametro_seq; Type: SEQUENCE SET; Schema: public; Owner: regalito_admin
--

SELECT pg_catalog.setval('public.parametro_sistema_id_parametro_seq', 1, false);


--
-- Name: permiso_id_permiso_seq; Type: SEQUENCE SET; Schema: public; Owner: regalito_admin
--

SELECT pg_catalog.setval('public.permiso_id_permiso_seq', 1, false);


--
-- Name: producto_id_producto_seq; Type: SEQUENCE SET; Schema: public; Owner: regalito_admin
--

SELECT pg_catalog.setval('public.producto_id_producto_seq', 1, false);


--
-- Name: proveedor_id_proveedor_seq; Type: SEQUENCE SET; Schema: public; Owner: regalito_admin
--

SELECT pg_catalog.setval('public.proveedor_id_proveedor_seq', 1, false);


--
-- Name: rol_id_rol_seq; Type: SEQUENCE SET; Schema: public; Owner: regalito_admin
--

SELECT pg_catalog.setval('public.rol_id_rol_seq', 33, true);


--
-- Name: sesion_usuario_id_sesion_seq; Type: SEQUENCE SET; Schema: public; Owner: regalito_admin
--

SELECT pg_catalog.setval('public.sesion_usuario_id_sesion_seq', 1, false);


--
-- Name: subcategoria_id_subcategoria_seq; Type: SEQUENCE SET; Schema: public; Owner: regalito_admin
--

SELECT pg_catalog.setval('public.subcategoria_id_subcategoria_seq', 1, false);


--
-- Name: sucursal_id_sucursal_seq; Type: SEQUENCE SET; Schema: public; Owner: regalito_admin
--

SELECT pg_catalog.setval('public.sucursal_id_sucursal_seq', 1, false);


--
-- Name: sync_cache_metadata_id_sync_seq; Type: SEQUENCE SET; Schema: public; Owner: regalito_admin
--

SELECT pg_catalog.setval('public.sync_cache_metadata_id_sync_seq', 1, false);


--
-- Name: sync_queue_id_sync_seq; Type: SEQUENCE SET; Schema: public; Owner: regalito_admin
--

SELECT pg_catalog.setval('public.sync_queue_id_sync_seq', 1, false);


--
-- Name: tipo_cliente_id_tipo_cliente_seq; Type: SEQUENCE SET; Schema: public; Owner: regalito_admin
--

SELECT pg_catalog.setval('public.tipo_cliente_id_tipo_cliente_seq', 1, false);


--
-- Name: tipo_movimiento_caja_id_tipo_movimiento_seq; Type: SEQUENCE SET; Schema: public; Owner: regalito_admin
--

SELECT pg_catalog.setval('public.tipo_movimiento_caja_id_tipo_movimiento_seq', 1, false);


--
-- Name: traslado_inventario_id_traslado_seq; Type: SEQUENCE SET; Schema: public; Owner: regalito_admin
--

SELECT pg_catalog.setval('public.traslado_inventario_id_traslado_seq', 1, false);


--
-- Name: turno_caja_id_turno_seq; Type: SEQUENCE SET; Schema: public; Owner: regalito_admin
--

SELECT pg_catalog.setval('public.turno_caja_id_turno_seq', 1, false);


--
-- Name: unidad_medida_id_unidad_seq; Type: SEQUENCE SET; Schema: public; Owner: regalito_admin
--

SELECT pg_catalog.setval('public.unidad_medida_id_unidad_seq', 1, false);


--
-- Name: usuario_id_usuario_seq; Type: SEQUENCE SET; Schema: public; Owner: regalito_admin
--

SELECT pg_catalog.setval('public.usuario_id_usuario_seq', 33, true);


--
-- Name: variante_producto_id_variante_seq; Type: SEQUENCE SET; Schema: public; Owner: regalito_admin
--

SELECT pg_catalog.setval('public.variante_producto_id_variante_seq', 1, false);


--
-- Name: venta_id_venta_seq; Type: SEQUENCE SET; Schema: public; Owner: regalito_admin
--

SELECT pg_catalog.setval('public.venta_id_venta_seq', 1, false);


--
-- Name: alerta_stock alerta_stock_pkey; Type: CONSTRAINT; Schema: public; Owner: regalito_admin
--

ALTER TABLE ONLY public.alerta_stock
    ADD CONSTRAINT alerta_stock_pkey PRIMARY KEY (id_alerta);


--
-- Name: area_bodega area_bodega_pkey; Type: CONSTRAINT; Schema: public; Owner: regalito_admin
--

ALTER TABLE ONLY public.area_bodega
    ADD CONSTRAINT area_bodega_pkey PRIMARY KEY (id_area);


--
-- Name: bitacora_auditoria bitacora_auditoria_pkey; Type: CONSTRAINT; Schema: public; Owner: regalito_admin
--

ALTER TABLE ONLY public.bitacora_auditoria
    ADD CONSTRAINT bitacora_auditoria_pkey PRIMARY KEY (id_bitacora);


--
-- Name: caja caja_pkey; Type: CONSTRAINT; Schema: public; Owner: regalito_admin
--

ALTER TABLE ONLY public.caja
    ADD CONSTRAINT caja_pkey PRIMARY KEY (id_caja);


--
-- Name: categoria categoria_nombre_key; Type: CONSTRAINT; Schema: public; Owner: regalito_admin
--

ALTER TABLE ONLY public.categoria
    ADD CONSTRAINT categoria_nombre_key UNIQUE (nombre);


--
-- Name: categoria categoria_pkey; Type: CONSTRAINT; Schema: public; Owner: regalito_admin
--

ALTER TABLE ONLY public.categoria
    ADD CONSTRAINT categoria_pkey PRIMARY KEY (id_categoria);


--
-- Name: cierre_caja_ciegas cierre_caja_ciegas_pkey; Type: CONSTRAINT; Schema: public; Owner: regalito_admin
--

ALTER TABLE ONLY public.cierre_caja_ciegas
    ADD CONSTRAINT cierre_caja_ciegas_pkey PRIMARY KEY (id_cierre);


--
-- Name: cliente_contacto cliente_contacto_pkey; Type: CONSTRAINT; Schema: public; Owner: regalito_admin
--

ALTER TABLE ONLY public.cliente_contacto
    ADD CONSTRAINT cliente_contacto_pkey PRIMARY KEY (id_contacto);


--
-- Name: cliente cliente_pkey; Type: CONSTRAINT; Schema: public; Owner: regalito_admin
--

ALTER TABLE ONLY public.cliente
    ADD CONSTRAINT cliente_pkey PRIMARY KEY (id_cliente);


--
-- Name: compra compra_pkey; Type: CONSTRAINT; Schema: public; Owner: regalito_admin
--

ALTER TABLE ONLY public.compra
    ADD CONSTRAINT compra_pkey PRIMARY KEY (id_compra);


--
-- Name: denominacion_efectivo denominacion_efectivo_pkey; Type: CONSTRAINT; Schema: public; Owner: regalito_admin
--

ALTER TABLE ONLY public.denominacion_efectivo
    ADD CONSTRAINT denominacion_efectivo_pkey PRIMARY KEY (id_denominacion);


--
-- Name: departamento_geografico departamento_geografico_nombre_key; Type: CONSTRAINT; Schema: public; Owner: regalito_admin
--

ALTER TABLE ONLY public.departamento_geografico
    ADD CONSTRAINT departamento_geografico_nombre_key UNIQUE (nombre);


--
-- Name: departamento_geografico departamento_geografico_pkey; Type: CONSTRAINT; Schema: public; Owner: regalito_admin
--

ALTER TABLE ONLY public.departamento_geografico
    ADD CONSTRAINT departamento_geografico_pkey PRIMARY KEY (id_departamento);


--
-- Name: detalle_arqueo_efectivo detalle_arqueo_efectivo_pkey; Type: CONSTRAINT; Schema: public; Owner: regalito_admin
--

ALTER TABLE ONLY public.detalle_arqueo_efectivo
    ADD CONSTRAINT detalle_arqueo_efectivo_pkey PRIMARY KEY (id_detalle_arqueo);


--
-- Name: detalle_compra detalle_compra_pkey; Type: CONSTRAINT; Schema: public; Owner: regalito_admin
--

ALTER TABLE ONLY public.detalle_compra
    ADD CONSTRAINT detalle_compra_pkey PRIMARY KEY (id_detalle_compra);


--
-- Name: detalle_merma detalle_merma_pkey; Type: CONSTRAINT; Schema: public; Owner: regalito_admin
--

ALTER TABLE ONLY public.detalle_merma
    ADD CONSTRAINT detalle_merma_pkey PRIMARY KEY (id_detalle_merma);


--
-- Name: detalle_orden_compra detalle_orden_compra_pkey; Type: CONSTRAINT; Schema: public; Owner: regalito_admin
--

ALTER TABLE ONLY public.detalle_orden_compra
    ADD CONSTRAINT detalle_orden_compra_pkey PRIMARY KEY (id_detalle_orden);


--
-- Name: detalle_venta detalle_venta_pkey; Type: CONSTRAINT; Schema: public; Owner: regalito_admin
--

ALTER TABLE ONLY public.detalle_venta
    ADD CONSTRAINT detalle_venta_pkey PRIMARY KEY (id_detalle_venta);


--
-- Name: factura_fel factura_fel_numero_dte_key; Type: CONSTRAINT; Schema: public; Owner: regalito_admin
--

ALTER TABLE ONLY public.factura_fel
    ADD CONSTRAINT factura_fel_numero_dte_key UNIQUE (numero_dte);


--
-- Name: factura_fel factura_fel_pkey; Type: CONSTRAINT; Schema: public; Owner: regalito_admin
--

ALTER TABLE ONLY public.factura_fel
    ADD CONSTRAINT factura_fel_pkey PRIMARY KEY (id_factura);


--
-- Name: historial_precio historial_precio_pkey; Type: CONSTRAINT; Schema: public; Owner: regalito_admin
--

ALTER TABLE ONLY public.historial_precio
    ADD CONSTRAINT historial_precio_pkey PRIMARY KEY (id_historial);


--
-- Name: intento_login intento_login_pkey; Type: CONSTRAINT; Schema: public; Owner: regalito_admin
--

ALTER TABLE ONLY public.intento_login
    ADD CONSTRAINT intento_login_pkey PRIMARY KEY (id_intento);


--
-- Name: inventario_sucursal inventario_sucursal_pkey; Type: CONSTRAINT; Schema: public; Owner: regalito_admin
--

ALTER TABLE ONLY public.inventario_sucursal
    ADD CONSTRAINT inventario_sucursal_pkey PRIMARY KEY (id_inventario);


--
-- Name: merma merma_pkey; Type: CONSTRAINT; Schema: public; Owner: regalito_admin
--

ALTER TABLE ONLY public.merma
    ADD CONSTRAINT merma_pkey PRIMARY KEY (id_merma);


--
-- Name: metodo_pago metodo_pago_pkey; Type: CONSTRAINT; Schema: public; Owner: regalito_admin
--

ALTER TABLE ONLY public.metodo_pago
    ADD CONSTRAINT metodo_pago_pkey PRIMARY KEY (id_metodo_pago);


--
-- Name: motivo_merma motivo_merma_pkey; Type: CONSTRAINT; Schema: public; Owner: regalito_admin
--

ALTER TABLE ONLY public.motivo_merma
    ADD CONSTRAINT motivo_merma_pkey PRIMARY KEY (id_motivo);


--
-- Name: movimiento_caja movimiento_caja_pkey; Type: CONSTRAINT; Schema: public; Owner: regalito_admin
--

ALTER TABLE ONLY public.movimiento_caja
    ADD CONSTRAINT movimiento_caja_pkey PRIMARY KEY (id_movimiento);


--
-- Name: municipio municipio_pkey; Type: CONSTRAINT; Schema: public; Owner: regalito_admin
--

ALTER TABLE ONLY public.municipio
    ADD CONSTRAINT municipio_pkey PRIMARY KEY (id_municipio);


--
-- Name: orden_compra orden_compra_pkey; Type: CONSTRAINT; Schema: public; Owner: regalito_admin
--

ALTER TABLE ONLY public.orden_compra
    ADD CONSTRAINT orden_compra_pkey PRIMARY KEY (id_orden);


--
-- Name: pago_venta pago_venta_pkey; Type: CONSTRAINT; Schema: public; Owner: regalito_admin
--

ALTER TABLE ONLY public.pago_venta
    ADD CONSTRAINT pago_venta_pkey PRIMARY KEY (id_pago);


--
-- Name: parametro_sistema parametro_sistema_clave_key; Type: CONSTRAINT; Schema: public; Owner: regalito_admin
--

ALTER TABLE ONLY public.parametro_sistema
    ADD CONSTRAINT parametro_sistema_clave_key UNIQUE (clave);


--
-- Name: parametro_sistema parametro_sistema_pkey; Type: CONSTRAINT; Schema: public; Owner: regalito_admin
--

ALTER TABLE ONLY public.parametro_sistema
    ADD CONSTRAINT parametro_sistema_pkey PRIMARY KEY (id_parametro);


--
-- Name: permiso permiso_codigo_key; Type: CONSTRAINT; Schema: public; Owner: regalito_admin
--

ALTER TABLE ONLY public.permiso
    ADD CONSTRAINT permiso_codigo_key UNIQUE (codigo);


--
-- Name: permiso permiso_pkey; Type: CONSTRAINT; Schema: public; Owner: regalito_admin
--

ALTER TABLE ONLY public.permiso
    ADD CONSTRAINT permiso_pkey PRIMARY KEY (id_permiso);


--
-- Name: producto producto_pkey; Type: CONSTRAINT; Schema: public; Owner: regalito_admin
--

ALTER TABLE ONLY public.producto
    ADD CONSTRAINT producto_pkey PRIMARY KEY (id_producto);


--
-- Name: proveedor proveedor_pkey; Type: CONSTRAINT; Schema: public; Owner: regalito_admin
--

ALTER TABLE ONLY public.proveedor
    ADD CONSTRAINT proveedor_pkey PRIMARY KEY (id_proveedor);


--
-- Name: rol rol_nombre_key; Type: CONSTRAINT; Schema: public; Owner: regalito_admin
--

ALTER TABLE ONLY public.rol
    ADD CONSTRAINT rol_nombre_key UNIQUE (nombre);


--
-- Name: rol_permiso rol_permiso_pkey; Type: CONSTRAINT; Schema: public; Owner: regalito_admin
--

ALTER TABLE ONLY public.rol_permiso
    ADD CONSTRAINT rol_permiso_pkey PRIMARY KEY (id_rol, id_permiso);


--
-- Name: rol rol_pkey; Type: CONSTRAINT; Schema: public; Owner: regalito_admin
--

ALTER TABLE ONLY public.rol
    ADD CONSTRAINT rol_pkey PRIMARY KEY (id_rol);


--
-- Name: sesion_usuario sesion_usuario_pkey; Type: CONSTRAINT; Schema: public; Owner: regalito_admin
--

ALTER TABLE ONLY public.sesion_usuario
    ADD CONSTRAINT sesion_usuario_pkey PRIMARY KEY (id_sesion);


--
-- Name: subcategoria subcategoria_pkey; Type: CONSTRAINT; Schema: public; Owner: regalito_admin
--

ALTER TABLE ONLY public.subcategoria
    ADD CONSTRAINT subcategoria_pkey PRIMARY KEY (id_subcategoria);


--
-- Name: sucursal sucursal_pkey; Type: CONSTRAINT; Schema: public; Owner: regalito_admin
--

ALTER TABLE ONLY public.sucursal
    ADD CONSTRAINT sucursal_pkey PRIMARY KEY (id_sucursal);


--
-- Name: sync_cache_metadata sync_cache_metadata_pkey; Type: CONSTRAINT; Schema: public; Owner: regalito_admin
--

ALTER TABLE ONLY public.sync_cache_metadata
    ADD CONSTRAINT sync_cache_metadata_pkey PRIMARY KEY (id_sync);


--
-- Name: sync_queue sync_queue_pkey; Type: CONSTRAINT; Schema: public; Owner: regalito_admin
--

ALTER TABLE ONLY public.sync_queue
    ADD CONSTRAINT sync_queue_pkey PRIMARY KEY (id_sync);


--
-- Name: tipo_cliente tipo_cliente_pkey; Type: CONSTRAINT; Schema: public; Owner: regalito_admin
--

ALTER TABLE ONLY public.tipo_cliente
    ADD CONSTRAINT tipo_cliente_pkey PRIMARY KEY (id_tipo_cliente);


--
-- Name: tipo_movimiento_caja tipo_movimiento_caja_pkey; Type: CONSTRAINT; Schema: public; Owner: regalito_admin
--

ALTER TABLE ONLY public.tipo_movimiento_caja
    ADD CONSTRAINT tipo_movimiento_caja_pkey PRIMARY KEY (id_tipo_movimiento);


--
-- Name: traslado_inventario traslado_inventario_pkey; Type: CONSTRAINT; Schema: public; Owner: regalito_admin
--

ALTER TABLE ONLY public.traslado_inventario
    ADD CONSTRAINT traslado_inventario_pkey PRIMARY KEY (id_traslado);


--
-- Name: turno_caja turno_caja_pkey; Type: CONSTRAINT; Schema: public; Owner: regalito_admin
--

ALTER TABLE ONLY public.turno_caja
    ADD CONSTRAINT turno_caja_pkey PRIMARY KEY (id_turno);


--
-- Name: unidad_medida unidad_medida_codigo_key; Type: CONSTRAINT; Schema: public; Owner: regalito_admin
--

ALTER TABLE ONLY public.unidad_medida
    ADD CONSTRAINT unidad_medida_codigo_key UNIQUE (codigo);


--
-- Name: unidad_medida unidad_medida_pkey; Type: CONSTRAINT; Schema: public; Owner: regalito_admin
--

ALTER TABLE ONLY public.unidad_medida
    ADD CONSTRAINT unidad_medida_pkey PRIMARY KEY (id_unidad);


--
-- Name: usuario usuario_pkey; Type: CONSTRAINT; Schema: public; Owner: regalito_admin
--

ALTER TABLE ONLY public.usuario
    ADD CONSTRAINT usuario_pkey PRIMARY KEY (id_usuario);


--
-- Name: usuario usuario_username_key; Type: CONSTRAINT; Schema: public; Owner: regalito_admin
--

ALTER TABLE ONLY public.usuario
    ADD CONSTRAINT usuario_username_key UNIQUE (username);


--
-- Name: variante_producto variante_producto_codigo_barras_key; Type: CONSTRAINT; Schema: public; Owner: regalito_admin
--

ALTER TABLE ONLY public.variante_producto
    ADD CONSTRAINT variante_producto_codigo_barras_key UNIQUE (codigo_barras);


--
-- Name: variante_producto variante_producto_pkey; Type: CONSTRAINT; Schema: public; Owner: regalito_admin
--

ALTER TABLE ONLY public.variante_producto
    ADD CONSTRAINT variante_producto_pkey PRIMARY KEY (id_variante);


--
-- Name: venta venta_pkey; Type: CONSTRAINT; Schema: public; Owner: regalito_admin
--

ALTER TABLE ONLY public.venta
    ADD CONSTRAINT venta_pkey PRIMARY KEY (id_venta);


--
-- Name: ix_alerta_stock_id_inventario; Type: INDEX; Schema: public; Owner: regalito_admin
--

CREATE INDEX ix_alerta_stock_id_inventario ON public.alerta_stock USING btree (id_inventario);


--
-- Name: ix_area_bodega_id_sucursal; Type: INDEX; Schema: public; Owner: regalito_admin
--

CREATE INDEX ix_area_bodega_id_sucursal ON public.area_bodega USING btree (id_sucursal);


--
-- Name: ix_bitacora_auditoria_id_usuario; Type: INDEX; Schema: public; Owner: regalito_admin
--

CREATE INDEX ix_bitacora_auditoria_id_usuario ON public.bitacora_auditoria USING btree (id_usuario);


--
-- Name: ix_caja_id_sucursal; Type: INDEX; Schema: public; Owner: regalito_admin
--

CREATE INDEX ix_caja_id_sucursal ON public.caja USING btree (id_sucursal);


--
-- Name: ix_cierre_caja_ciegas_id_turno; Type: INDEX; Schema: public; Owner: regalito_admin
--

CREATE INDEX ix_cierre_caja_ciegas_id_turno ON public.cierre_caja_ciegas USING btree (id_turno);


--
-- Name: ix_cierre_caja_ciegas_id_usuario_cajero; Type: INDEX; Schema: public; Owner: regalito_admin
--

CREATE INDEX ix_cierre_caja_ciegas_id_usuario_cajero ON public.cierre_caja_ciegas USING btree (id_usuario_cajero);


--
-- Name: ix_cierre_caja_ciegas_id_usuario_supervisor; Type: INDEX; Schema: public; Owner: regalito_admin
--

CREATE INDEX ix_cierre_caja_ciegas_id_usuario_supervisor ON public.cierre_caja_ciegas USING btree (id_usuario_supervisor);


--
-- Name: ix_cliente_contacto_id_cliente; Type: INDEX; Schema: public; Owner: regalito_admin
--

CREATE INDEX ix_cliente_contacto_id_cliente ON public.cliente_contacto USING btree (id_cliente);


--
-- Name: ix_cliente_id_municipio; Type: INDEX; Schema: public; Owner: regalito_admin
--

CREATE INDEX ix_cliente_id_municipio ON public.cliente USING btree (id_municipio);


--
-- Name: ix_cliente_id_tipo_cliente; Type: INDEX; Schema: public; Owner: regalito_admin
--

CREATE INDEX ix_cliente_id_tipo_cliente ON public.cliente USING btree (id_tipo_cliente);


--
-- Name: ix_compra_id_orden; Type: INDEX; Schema: public; Owner: regalito_admin
--

CREATE INDEX ix_compra_id_orden ON public.compra USING btree (id_orden);


--
-- Name: ix_compra_id_proveedor; Type: INDEX; Schema: public; Owner: regalito_admin
--

CREATE INDEX ix_compra_id_proveedor ON public.compra USING btree (id_proveedor);


--
-- Name: ix_compra_id_usuario; Type: INDEX; Schema: public; Owner: regalito_admin
--

CREATE INDEX ix_compra_id_usuario ON public.compra USING btree (id_usuario);


--
-- Name: ix_detalle_arqueo_efectivo_id_cierre; Type: INDEX; Schema: public; Owner: regalito_admin
--

CREATE INDEX ix_detalle_arqueo_efectivo_id_cierre ON public.detalle_arqueo_efectivo USING btree (id_cierre);


--
-- Name: ix_detalle_arqueo_efectivo_id_denominacion; Type: INDEX; Schema: public; Owner: regalito_admin
--

CREATE INDEX ix_detalle_arqueo_efectivo_id_denominacion ON public.detalle_arqueo_efectivo USING btree (id_denominacion);


--
-- Name: ix_detalle_compra_id_compra; Type: INDEX; Schema: public; Owner: regalito_admin
--

CREATE INDEX ix_detalle_compra_id_compra ON public.detalle_compra USING btree (id_compra);


--
-- Name: ix_detalle_compra_id_variante; Type: INDEX; Schema: public; Owner: regalito_admin
--

CREATE INDEX ix_detalle_compra_id_variante ON public.detalle_compra USING btree (id_variante);


--
-- Name: ix_detalle_merma_id_merma; Type: INDEX; Schema: public; Owner: regalito_admin
--

CREATE INDEX ix_detalle_merma_id_merma ON public.detalle_merma USING btree (id_merma);


--
-- Name: ix_detalle_merma_id_motivo; Type: INDEX; Schema: public; Owner: regalito_admin
--

CREATE INDEX ix_detalle_merma_id_motivo ON public.detalle_merma USING btree (id_motivo);


--
-- Name: ix_detalle_merma_id_variante; Type: INDEX; Schema: public; Owner: regalito_admin
--

CREATE INDEX ix_detalle_merma_id_variante ON public.detalle_merma USING btree (id_variante);


--
-- Name: ix_detalle_orden_compra_id_orden; Type: INDEX; Schema: public; Owner: regalito_admin
--

CREATE INDEX ix_detalle_orden_compra_id_orden ON public.detalle_orden_compra USING btree (id_orden);


--
-- Name: ix_detalle_orden_compra_id_variante; Type: INDEX; Schema: public; Owner: regalito_admin
--

CREATE INDEX ix_detalle_orden_compra_id_variante ON public.detalle_orden_compra USING btree (id_variante);


--
-- Name: ix_detalle_venta_id_variante; Type: INDEX; Schema: public; Owner: regalito_admin
--

CREATE INDEX ix_detalle_venta_id_variante ON public.detalle_venta USING btree (id_variante);


--
-- Name: ix_detalle_venta_id_venta; Type: INDEX; Schema: public; Owner: regalito_admin
--

CREATE INDEX ix_detalle_venta_id_venta ON public.detalle_venta USING btree (id_venta);


--
-- Name: ix_factura_fel_id_venta; Type: INDEX; Schema: public; Owner: regalito_admin
--

CREATE INDEX ix_factura_fel_id_venta ON public.factura_fel USING btree (id_venta);


--
-- Name: ix_historial_precio_id_usuario; Type: INDEX; Schema: public; Owner: regalito_admin
--

CREATE INDEX ix_historial_precio_id_usuario ON public.historial_precio USING btree (id_usuario);


--
-- Name: ix_historial_precio_id_variante; Type: INDEX; Schema: public; Owner: regalito_admin
--

CREATE INDEX ix_historial_precio_id_variante ON public.historial_precio USING btree (id_variante);


--
-- Name: ix_intento_login_username; Type: INDEX; Schema: public; Owner: regalito_admin
--

CREATE UNIQUE INDEX ix_intento_login_username ON public.intento_login USING btree (username);


--
-- Name: ix_inventario_sucursal_id_area; Type: INDEX; Schema: public; Owner: regalito_admin
--

CREATE INDEX ix_inventario_sucursal_id_area ON public.inventario_sucursal USING btree (id_area);


--
-- Name: ix_inventario_sucursal_id_sucursal; Type: INDEX; Schema: public; Owner: regalito_admin
--

CREATE INDEX ix_inventario_sucursal_id_sucursal ON public.inventario_sucursal USING btree (id_sucursal);


--
-- Name: ix_inventario_sucursal_id_variante; Type: INDEX; Schema: public; Owner: regalito_admin
--

CREATE INDEX ix_inventario_sucursal_id_variante ON public.inventario_sucursal USING btree (id_variante);


--
-- Name: ix_merma_id_sucursal; Type: INDEX; Schema: public; Owner: regalito_admin
--

CREATE INDEX ix_merma_id_sucursal ON public.merma USING btree (id_sucursal);


--
-- Name: ix_merma_id_usuario; Type: INDEX; Schema: public; Owner: regalito_admin
--

CREATE INDEX ix_merma_id_usuario ON public.merma USING btree (id_usuario);


--
-- Name: ix_movimiento_caja_id_tipo_movimiento; Type: INDEX; Schema: public; Owner: regalito_admin
--

CREATE INDEX ix_movimiento_caja_id_tipo_movimiento ON public.movimiento_caja USING btree (id_tipo_movimiento);


--
-- Name: ix_movimiento_caja_id_turno; Type: INDEX; Schema: public; Owner: regalito_admin
--

CREATE INDEX ix_movimiento_caja_id_turno ON public.movimiento_caja USING btree (id_turno);


--
-- Name: ix_movimiento_caja_id_usuario; Type: INDEX; Schema: public; Owner: regalito_admin
--

CREATE INDEX ix_movimiento_caja_id_usuario ON public.movimiento_caja USING btree (id_usuario);


--
-- Name: ix_municipio_id_departamento; Type: INDEX; Schema: public; Owner: regalito_admin
--

CREATE INDEX ix_municipio_id_departamento ON public.municipio USING btree (id_departamento);


--
-- Name: ix_orden_compra_id_proveedor; Type: INDEX; Schema: public; Owner: regalito_admin
--

CREATE INDEX ix_orden_compra_id_proveedor ON public.orden_compra USING btree (id_proveedor);


--
-- Name: ix_orden_compra_id_usuario; Type: INDEX; Schema: public; Owner: regalito_admin
--

CREATE INDEX ix_orden_compra_id_usuario ON public.orden_compra USING btree (id_usuario);


--
-- Name: ix_pago_venta_id_metodo_pago; Type: INDEX; Schema: public; Owner: regalito_admin
--

CREATE INDEX ix_pago_venta_id_metodo_pago ON public.pago_venta USING btree (id_metodo_pago);


--
-- Name: ix_pago_venta_id_venta; Type: INDEX; Schema: public; Owner: regalito_admin
--

CREATE INDEX ix_pago_venta_id_venta ON public.pago_venta USING btree (id_venta);


--
-- Name: ix_producto_id_subcategoria; Type: INDEX; Schema: public; Owner: regalito_admin
--

CREATE INDEX ix_producto_id_subcategoria ON public.producto USING btree (id_subcategoria);


--
-- Name: ix_producto_id_unidad; Type: INDEX; Schema: public; Owner: regalito_admin
--

CREATE INDEX ix_producto_id_unidad ON public.producto USING btree (id_unidad);


--
-- Name: ix_sesion_usuario_id_usuario; Type: INDEX; Schema: public; Owner: regalito_admin
--

CREATE INDEX ix_sesion_usuario_id_usuario ON public.sesion_usuario USING btree (id_usuario);


--
-- Name: ix_subcategoria_id_categoria; Type: INDEX; Schema: public; Owner: regalito_admin
--

CREATE INDEX ix_subcategoria_id_categoria ON public.subcategoria USING btree (id_categoria);


--
-- Name: ix_sync_cache_metadata_tabla; Type: INDEX; Schema: public; Owner: regalito_admin
--

CREATE UNIQUE INDEX ix_sync_cache_metadata_tabla ON public.sync_cache_metadata USING btree (tabla);


--
-- Name: ix_sync_queue_idempotency_key; Type: INDEX; Schema: public; Owner: regalito_admin
--

CREATE UNIQUE INDEX ix_sync_queue_idempotency_key ON public.sync_queue USING btree (idempotency_key);


--
-- Name: ix_traslado_inventario_id_sucursal_destino; Type: INDEX; Schema: public; Owner: regalito_admin
--

CREATE INDEX ix_traslado_inventario_id_sucursal_destino ON public.traslado_inventario USING btree (id_sucursal_destino);


--
-- Name: ix_traslado_inventario_id_sucursal_origen; Type: INDEX; Schema: public; Owner: regalito_admin
--

CREATE INDEX ix_traslado_inventario_id_sucursal_origen ON public.traslado_inventario USING btree (id_sucursal_origen);


--
-- Name: ix_traslado_inventario_id_variante; Type: INDEX; Schema: public; Owner: regalito_admin
--

CREATE INDEX ix_traslado_inventario_id_variante ON public.traslado_inventario USING btree (id_variante);


--
-- Name: ix_turno_caja_id_caja; Type: INDEX; Schema: public; Owner: regalito_admin
--

CREATE INDEX ix_turno_caja_id_caja ON public.turno_caja USING btree (id_caja);


--
-- Name: ix_turno_caja_id_usuario; Type: INDEX; Schema: public; Owner: regalito_admin
--

CREATE INDEX ix_turno_caja_id_usuario ON public.turno_caja USING btree (id_usuario);


--
-- Name: ix_usuario_id_rol; Type: INDEX; Schema: public; Owner: regalito_admin
--

CREATE INDEX ix_usuario_id_rol ON public.usuario USING btree (id_rol);


--
-- Name: ix_variante_producto_id_producto; Type: INDEX; Schema: public; Owner: regalito_admin
--

CREATE INDEX ix_variante_producto_id_producto ON public.variante_producto USING btree (id_producto);


--
-- Name: ix_venta_id_cliente; Type: INDEX; Schema: public; Owner: regalito_admin
--

CREATE INDEX ix_venta_id_cliente ON public.venta USING btree (id_cliente);


--
-- Name: ix_venta_id_turno; Type: INDEX; Schema: public; Owner: regalito_admin
--

CREATE INDEX ix_venta_id_turno ON public.venta USING btree (id_turno);


--
-- Name: ix_venta_id_usuario; Type: INDEX; Schema: public; Owner: regalito_admin
--

CREATE INDEX ix_venta_id_usuario ON public.venta USING btree (id_usuario);


--
-- Name: alerta_stock alerta_stock_id_inventario_fkey; Type: FK CONSTRAINT; Schema: public; Owner: regalito_admin
--

ALTER TABLE ONLY public.alerta_stock
    ADD CONSTRAINT alerta_stock_id_inventario_fkey FOREIGN KEY (id_inventario) REFERENCES public.inventario_sucursal(id_inventario);


--
-- Name: area_bodega area_bodega_id_sucursal_fkey; Type: FK CONSTRAINT; Schema: public; Owner: regalito_admin
--

ALTER TABLE ONLY public.area_bodega
    ADD CONSTRAINT area_bodega_id_sucursal_fkey FOREIGN KEY (id_sucursal) REFERENCES public.sucursal(id_sucursal);


--
-- Name: bitacora_auditoria bitacora_auditoria_id_usuario_fkey; Type: FK CONSTRAINT; Schema: public; Owner: regalito_admin
--

ALTER TABLE ONLY public.bitacora_auditoria
    ADD CONSTRAINT bitacora_auditoria_id_usuario_fkey FOREIGN KEY (id_usuario) REFERENCES public.usuario(id_usuario);


--
-- Name: caja caja_id_sucursal_fkey; Type: FK CONSTRAINT; Schema: public; Owner: regalito_admin
--

ALTER TABLE ONLY public.caja
    ADD CONSTRAINT caja_id_sucursal_fkey FOREIGN KEY (id_sucursal) REFERENCES public.sucursal(id_sucursal);


--
-- Name: cierre_caja_ciegas cierre_caja_ciegas_id_turno_fkey; Type: FK CONSTRAINT; Schema: public; Owner: regalito_admin
--

ALTER TABLE ONLY public.cierre_caja_ciegas
    ADD CONSTRAINT cierre_caja_ciegas_id_turno_fkey FOREIGN KEY (id_turno) REFERENCES public.turno_caja(id_turno);


--
-- Name: cierre_caja_ciegas cierre_caja_ciegas_id_usuario_cajero_fkey; Type: FK CONSTRAINT; Schema: public; Owner: regalito_admin
--

ALTER TABLE ONLY public.cierre_caja_ciegas
    ADD CONSTRAINT cierre_caja_ciegas_id_usuario_cajero_fkey FOREIGN KEY (id_usuario_cajero) REFERENCES public.usuario(id_usuario);


--
-- Name: cierre_caja_ciegas cierre_caja_ciegas_id_usuario_supervisor_fkey; Type: FK CONSTRAINT; Schema: public; Owner: regalito_admin
--

ALTER TABLE ONLY public.cierre_caja_ciegas
    ADD CONSTRAINT cierre_caja_ciegas_id_usuario_supervisor_fkey FOREIGN KEY (id_usuario_supervisor) REFERENCES public.usuario(id_usuario);


--
-- Name: cliente_contacto cliente_contacto_id_cliente_fkey; Type: FK CONSTRAINT; Schema: public; Owner: regalito_admin
--

ALTER TABLE ONLY public.cliente_contacto
    ADD CONSTRAINT cliente_contacto_id_cliente_fkey FOREIGN KEY (id_cliente) REFERENCES public.cliente(id_cliente);


--
-- Name: cliente cliente_id_municipio_fkey; Type: FK CONSTRAINT; Schema: public; Owner: regalito_admin
--

ALTER TABLE ONLY public.cliente
    ADD CONSTRAINT cliente_id_municipio_fkey FOREIGN KEY (id_municipio) REFERENCES public.municipio(id_municipio);


--
-- Name: cliente cliente_id_tipo_cliente_fkey; Type: FK CONSTRAINT; Schema: public; Owner: regalito_admin
--

ALTER TABLE ONLY public.cliente
    ADD CONSTRAINT cliente_id_tipo_cliente_fkey FOREIGN KEY (id_tipo_cliente) REFERENCES public.tipo_cliente(id_tipo_cliente);


--
-- Name: compra compra_id_orden_fkey; Type: FK CONSTRAINT; Schema: public; Owner: regalito_admin
--

ALTER TABLE ONLY public.compra
    ADD CONSTRAINT compra_id_orden_fkey FOREIGN KEY (id_orden) REFERENCES public.orden_compra(id_orden);


--
-- Name: compra compra_id_proveedor_fkey; Type: FK CONSTRAINT; Schema: public; Owner: regalito_admin
--

ALTER TABLE ONLY public.compra
    ADD CONSTRAINT compra_id_proveedor_fkey FOREIGN KEY (id_proveedor) REFERENCES public.proveedor(id_proveedor);


--
-- Name: compra compra_id_usuario_fkey; Type: FK CONSTRAINT; Schema: public; Owner: regalito_admin
--

ALTER TABLE ONLY public.compra
    ADD CONSTRAINT compra_id_usuario_fkey FOREIGN KEY (id_usuario) REFERENCES public.usuario(id_usuario);


--
-- Name: detalle_arqueo_efectivo detalle_arqueo_efectivo_id_cierre_fkey; Type: FK CONSTRAINT; Schema: public; Owner: regalito_admin
--

ALTER TABLE ONLY public.detalle_arqueo_efectivo
    ADD CONSTRAINT detalle_arqueo_efectivo_id_cierre_fkey FOREIGN KEY (id_cierre) REFERENCES public.cierre_caja_ciegas(id_cierre);


--
-- Name: detalle_arqueo_efectivo detalle_arqueo_efectivo_id_denominacion_fkey; Type: FK CONSTRAINT; Schema: public; Owner: regalito_admin
--

ALTER TABLE ONLY public.detalle_arqueo_efectivo
    ADD CONSTRAINT detalle_arqueo_efectivo_id_denominacion_fkey FOREIGN KEY (id_denominacion) REFERENCES public.denominacion_efectivo(id_denominacion);


--
-- Name: detalle_compra detalle_compra_id_compra_fkey; Type: FK CONSTRAINT; Schema: public; Owner: regalito_admin
--

ALTER TABLE ONLY public.detalle_compra
    ADD CONSTRAINT detalle_compra_id_compra_fkey FOREIGN KEY (id_compra) REFERENCES public.compra(id_compra);


--
-- Name: detalle_compra detalle_compra_id_variante_fkey; Type: FK CONSTRAINT; Schema: public; Owner: regalito_admin
--

ALTER TABLE ONLY public.detalle_compra
    ADD CONSTRAINT detalle_compra_id_variante_fkey FOREIGN KEY (id_variante) REFERENCES public.variante_producto(id_variante);


--
-- Name: detalle_merma detalle_merma_id_merma_fkey; Type: FK CONSTRAINT; Schema: public; Owner: regalito_admin
--

ALTER TABLE ONLY public.detalle_merma
    ADD CONSTRAINT detalle_merma_id_merma_fkey FOREIGN KEY (id_merma) REFERENCES public.merma(id_merma);


--
-- Name: detalle_merma detalle_merma_id_motivo_fkey; Type: FK CONSTRAINT; Schema: public; Owner: regalito_admin
--

ALTER TABLE ONLY public.detalle_merma
    ADD CONSTRAINT detalle_merma_id_motivo_fkey FOREIGN KEY (id_motivo) REFERENCES public.motivo_merma(id_motivo);


--
-- Name: detalle_merma detalle_merma_id_variante_fkey; Type: FK CONSTRAINT; Schema: public; Owner: regalito_admin
--

ALTER TABLE ONLY public.detalle_merma
    ADD CONSTRAINT detalle_merma_id_variante_fkey FOREIGN KEY (id_variante) REFERENCES public.variante_producto(id_variante);


--
-- Name: detalle_orden_compra detalle_orden_compra_id_orden_fkey; Type: FK CONSTRAINT; Schema: public; Owner: regalito_admin
--

ALTER TABLE ONLY public.detalle_orden_compra
    ADD CONSTRAINT detalle_orden_compra_id_orden_fkey FOREIGN KEY (id_orden) REFERENCES public.orden_compra(id_orden);


--
-- Name: detalle_orden_compra detalle_orden_compra_id_variante_fkey; Type: FK CONSTRAINT; Schema: public; Owner: regalito_admin
--

ALTER TABLE ONLY public.detalle_orden_compra
    ADD CONSTRAINT detalle_orden_compra_id_variante_fkey FOREIGN KEY (id_variante) REFERENCES public.variante_producto(id_variante);


--
-- Name: detalle_venta detalle_venta_id_variante_fkey; Type: FK CONSTRAINT; Schema: public; Owner: regalito_admin
--

ALTER TABLE ONLY public.detalle_venta
    ADD CONSTRAINT detalle_venta_id_variante_fkey FOREIGN KEY (id_variante) REFERENCES public.variante_producto(id_variante);


--
-- Name: detalle_venta detalle_venta_id_venta_fkey; Type: FK CONSTRAINT; Schema: public; Owner: regalito_admin
--

ALTER TABLE ONLY public.detalle_venta
    ADD CONSTRAINT detalle_venta_id_venta_fkey FOREIGN KEY (id_venta) REFERENCES public.venta(id_venta);


--
-- Name: factura_fel factura_fel_id_venta_fkey; Type: FK CONSTRAINT; Schema: public; Owner: regalito_admin
--

ALTER TABLE ONLY public.factura_fel
    ADD CONSTRAINT factura_fel_id_venta_fkey FOREIGN KEY (id_venta) REFERENCES public.venta(id_venta);


--
-- Name: historial_precio historial_precio_id_usuario_fkey; Type: FK CONSTRAINT; Schema: public; Owner: regalito_admin
--

ALTER TABLE ONLY public.historial_precio
    ADD CONSTRAINT historial_precio_id_usuario_fkey FOREIGN KEY (id_usuario) REFERENCES public.usuario(id_usuario);


--
-- Name: historial_precio historial_precio_id_variante_fkey; Type: FK CONSTRAINT; Schema: public; Owner: regalito_admin
--

ALTER TABLE ONLY public.historial_precio
    ADD CONSTRAINT historial_precio_id_variante_fkey FOREIGN KEY (id_variante) REFERENCES public.variante_producto(id_variante);


--
-- Name: inventario_sucursal inventario_sucursal_id_area_fkey; Type: FK CONSTRAINT; Schema: public; Owner: regalito_admin
--

ALTER TABLE ONLY public.inventario_sucursal
    ADD CONSTRAINT inventario_sucursal_id_area_fkey FOREIGN KEY (id_area) REFERENCES public.area_bodega(id_area);


--
-- Name: inventario_sucursal inventario_sucursal_id_sucursal_fkey; Type: FK CONSTRAINT; Schema: public; Owner: regalito_admin
--

ALTER TABLE ONLY public.inventario_sucursal
    ADD CONSTRAINT inventario_sucursal_id_sucursal_fkey FOREIGN KEY (id_sucursal) REFERENCES public.sucursal(id_sucursal);


--
-- Name: inventario_sucursal inventario_sucursal_id_variante_fkey; Type: FK CONSTRAINT; Schema: public; Owner: regalito_admin
--

ALTER TABLE ONLY public.inventario_sucursal
    ADD CONSTRAINT inventario_sucursal_id_variante_fkey FOREIGN KEY (id_variante) REFERENCES public.variante_producto(id_variante);


--
-- Name: merma merma_id_sucursal_fkey; Type: FK CONSTRAINT; Schema: public; Owner: regalito_admin
--

ALTER TABLE ONLY public.merma
    ADD CONSTRAINT merma_id_sucursal_fkey FOREIGN KEY (id_sucursal) REFERENCES public.sucursal(id_sucursal);


--
-- Name: merma merma_id_usuario_fkey; Type: FK CONSTRAINT; Schema: public; Owner: regalito_admin
--

ALTER TABLE ONLY public.merma
    ADD CONSTRAINT merma_id_usuario_fkey FOREIGN KEY (id_usuario) REFERENCES public.usuario(id_usuario);


--
-- Name: movimiento_caja movimiento_caja_id_tipo_movimiento_fkey; Type: FK CONSTRAINT; Schema: public; Owner: regalito_admin
--

ALTER TABLE ONLY public.movimiento_caja
    ADD CONSTRAINT movimiento_caja_id_tipo_movimiento_fkey FOREIGN KEY (id_tipo_movimiento) REFERENCES public.tipo_movimiento_caja(id_tipo_movimiento);


--
-- Name: movimiento_caja movimiento_caja_id_turno_fkey; Type: FK CONSTRAINT; Schema: public; Owner: regalito_admin
--

ALTER TABLE ONLY public.movimiento_caja
    ADD CONSTRAINT movimiento_caja_id_turno_fkey FOREIGN KEY (id_turno) REFERENCES public.turno_caja(id_turno);


--
-- Name: movimiento_caja movimiento_caja_id_usuario_fkey; Type: FK CONSTRAINT; Schema: public; Owner: regalito_admin
--

ALTER TABLE ONLY public.movimiento_caja
    ADD CONSTRAINT movimiento_caja_id_usuario_fkey FOREIGN KEY (id_usuario) REFERENCES public.usuario(id_usuario);


--
-- Name: municipio municipio_id_departamento_fkey; Type: FK CONSTRAINT; Schema: public; Owner: regalito_admin
--

ALTER TABLE ONLY public.municipio
    ADD CONSTRAINT municipio_id_departamento_fkey FOREIGN KEY (id_departamento) REFERENCES public.departamento_geografico(id_departamento);


--
-- Name: orden_compra orden_compra_id_proveedor_fkey; Type: FK CONSTRAINT; Schema: public; Owner: regalito_admin
--

ALTER TABLE ONLY public.orden_compra
    ADD CONSTRAINT orden_compra_id_proveedor_fkey FOREIGN KEY (id_proveedor) REFERENCES public.proveedor(id_proveedor);


--
-- Name: orden_compra orden_compra_id_usuario_fkey; Type: FK CONSTRAINT; Schema: public; Owner: regalito_admin
--

ALTER TABLE ONLY public.orden_compra
    ADD CONSTRAINT orden_compra_id_usuario_fkey FOREIGN KEY (id_usuario) REFERENCES public.usuario(id_usuario);


--
-- Name: pago_venta pago_venta_id_metodo_pago_fkey; Type: FK CONSTRAINT; Schema: public; Owner: regalito_admin
--

ALTER TABLE ONLY public.pago_venta
    ADD CONSTRAINT pago_venta_id_metodo_pago_fkey FOREIGN KEY (id_metodo_pago) REFERENCES public.metodo_pago(id_metodo_pago);


--
-- Name: pago_venta pago_venta_id_venta_fkey; Type: FK CONSTRAINT; Schema: public; Owner: regalito_admin
--

ALTER TABLE ONLY public.pago_venta
    ADD CONSTRAINT pago_venta_id_venta_fkey FOREIGN KEY (id_venta) REFERENCES public.venta(id_venta);


--
-- Name: producto producto_id_subcategoria_fkey; Type: FK CONSTRAINT; Schema: public; Owner: regalito_admin
--

ALTER TABLE ONLY public.producto
    ADD CONSTRAINT producto_id_subcategoria_fkey FOREIGN KEY (id_subcategoria) REFERENCES public.subcategoria(id_subcategoria);


--
-- Name: producto producto_id_unidad_fkey; Type: FK CONSTRAINT; Schema: public; Owner: regalito_admin
--

ALTER TABLE ONLY public.producto
    ADD CONSTRAINT producto_id_unidad_fkey FOREIGN KEY (id_unidad) REFERENCES public.unidad_medida(id_unidad);


--
-- Name: rol_permiso rol_permiso_id_permiso_fkey; Type: FK CONSTRAINT; Schema: public; Owner: regalito_admin
--

ALTER TABLE ONLY public.rol_permiso
    ADD CONSTRAINT rol_permiso_id_permiso_fkey FOREIGN KEY (id_permiso) REFERENCES public.permiso(id_permiso);


--
-- Name: rol_permiso rol_permiso_id_rol_fkey; Type: FK CONSTRAINT; Schema: public; Owner: regalito_admin
--

ALTER TABLE ONLY public.rol_permiso
    ADD CONSTRAINT rol_permiso_id_rol_fkey FOREIGN KEY (id_rol) REFERENCES public.rol(id_rol);


--
-- Name: sesion_usuario sesion_usuario_id_usuario_fkey; Type: FK CONSTRAINT; Schema: public; Owner: regalito_admin
--

ALTER TABLE ONLY public.sesion_usuario
    ADD CONSTRAINT sesion_usuario_id_usuario_fkey FOREIGN KEY (id_usuario) REFERENCES public.usuario(id_usuario);


--
-- Name: subcategoria subcategoria_id_categoria_fkey; Type: FK CONSTRAINT; Schema: public; Owner: regalito_admin
--

ALTER TABLE ONLY public.subcategoria
    ADD CONSTRAINT subcategoria_id_categoria_fkey FOREIGN KEY (id_categoria) REFERENCES public.categoria(id_categoria);


--
-- Name: traslado_inventario traslado_inventario_id_sucursal_destino_fkey; Type: FK CONSTRAINT; Schema: public; Owner: regalito_admin
--

ALTER TABLE ONLY public.traslado_inventario
    ADD CONSTRAINT traslado_inventario_id_sucursal_destino_fkey FOREIGN KEY (id_sucursal_destino) REFERENCES public.sucursal(id_sucursal);


--
-- Name: traslado_inventario traslado_inventario_id_sucursal_origen_fkey; Type: FK CONSTRAINT; Schema: public; Owner: regalito_admin
--

ALTER TABLE ONLY public.traslado_inventario
    ADD CONSTRAINT traslado_inventario_id_sucursal_origen_fkey FOREIGN KEY (id_sucursal_origen) REFERENCES public.sucursal(id_sucursal);


--
-- Name: traslado_inventario traslado_inventario_id_variante_fkey; Type: FK CONSTRAINT; Schema: public; Owner: regalito_admin
--

ALTER TABLE ONLY public.traslado_inventario
    ADD CONSTRAINT traslado_inventario_id_variante_fkey FOREIGN KEY (id_variante) REFERENCES public.variante_producto(id_variante);


--
-- Name: turno_caja turno_caja_id_caja_fkey; Type: FK CONSTRAINT; Schema: public; Owner: regalito_admin
--

ALTER TABLE ONLY public.turno_caja
    ADD CONSTRAINT turno_caja_id_caja_fkey FOREIGN KEY (id_caja) REFERENCES public.caja(id_caja);


--
-- Name: turno_caja turno_caja_id_usuario_fkey; Type: FK CONSTRAINT; Schema: public; Owner: regalito_admin
--

ALTER TABLE ONLY public.turno_caja
    ADD CONSTRAINT turno_caja_id_usuario_fkey FOREIGN KEY (id_usuario) REFERENCES public.usuario(id_usuario);


--
-- Name: usuario usuario_id_rol_fkey; Type: FK CONSTRAINT; Schema: public; Owner: regalito_admin
--

ALTER TABLE ONLY public.usuario
    ADD CONSTRAINT usuario_id_rol_fkey FOREIGN KEY (id_rol) REFERENCES public.rol(id_rol);


--
-- Name: variante_producto variante_producto_id_producto_fkey; Type: FK CONSTRAINT; Schema: public; Owner: regalito_admin
--

ALTER TABLE ONLY public.variante_producto
    ADD CONSTRAINT variante_producto_id_producto_fkey FOREIGN KEY (id_producto) REFERENCES public.producto(id_producto);


--
-- Name: venta venta_id_cliente_fkey; Type: FK CONSTRAINT; Schema: public; Owner: regalito_admin
--

ALTER TABLE ONLY public.venta
    ADD CONSTRAINT venta_id_cliente_fkey FOREIGN KEY (id_cliente) REFERENCES public.cliente(id_cliente);


--
-- Name: venta venta_id_turno_fkey; Type: FK CONSTRAINT; Schema: public; Owner: regalito_admin
--

ALTER TABLE ONLY public.venta
    ADD CONSTRAINT venta_id_turno_fkey FOREIGN KEY (id_turno) REFERENCES public.turno_caja(id_turno);


--
-- Name: venta venta_id_usuario_fkey; Type: FK CONSTRAINT; Schema: public; Owner: regalito_admin
--

ALTER TABLE ONLY public.venta
    ADD CONSTRAINT venta_id_usuario_fkey FOREIGN KEY (id_usuario) REFERENCES public.usuario(id_usuario);


--
-- PostgreSQL database dump complete
--

\unrestrict 5OgBlypL75iNVJlhszhqWlhH1skhoXBgKhuddTckEtAHrLAdxda8jbdmepF3KyC

