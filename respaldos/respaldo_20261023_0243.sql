--
-- PostgreSQL database dump
--

\restrict t8CsEU5Y9V4BGa9mAQv6wcUtsxzKbiwgImXORsZY5F4qZslM3Hu74ijtCM9aHyB

-- Dumped from database version 15.19 (Debian 15.19-1.pgdg13+2)
-- Dumped by pg_dump version 15.19 (Debian 15.19-1.pgdg13+2)

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
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: regalito_admin
--

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);


ALTER TABLE public.alembic_version OWNER TO regalito_admin;

--
-- Name: alerta_stock; Type: TABLE; Schema: public; Owner: regalito_admin
--

CREATE TABLE public.alerta_stock (
    id_alerta integer NOT NULL,
    id_inventario integer NOT NULL,
    mensaje character varying(150) NOT NULL,
    fecha_generacion timestamp without time zone NOT NULL,
    estado character varying(20) NOT NULL,
    CONSTRAINT alerta_stock_estado_check CHECK (((estado)::text = ANY ((ARRAY['Pendiente'::character varying, 'Atendida'::character varying, 'Descartada'::character varying])::text[])))
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
    nombre_area character varying(50) NOT NULL,
    estado character varying(20) DEFAULT 'Activo'::character varying NOT NULL,
    CONSTRAINT area_bodega_estado_check CHECK (((estado)::text = ANY ((ARRAY['Activo'::character varying, 'Inactivo'::character varying])::text[])))
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
    fecha_hora timestamp without time zone DEFAULT now() NOT NULL
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
    estado character varying(20) NOT NULL,
    CONSTRAINT caja_estado_check CHECK (((estado)::text = ANY ((ARRAY['Activa'::character varying, 'Inactiva'::character varying, 'Activo'::character varying, 'Inactivo'::character varying])::text[])))
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
    estado character varying(20) NOT NULL,
    CONSTRAINT categoria_estado_check CHECK (((estado)::text = ANY ((ARRAY['Activo'::character varying, 'Inactivo'::character varying])::text[])))
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
    direccion character varying(200),
    estado character varying(20) DEFAULT 'Activo'::character varying NOT NULL,
    fecha_creacion timestamp without time zone DEFAULT now() NOT NULL,
    CONSTRAINT cliente_estado_check CHECK (((estado)::text = ANY ((ARRAY['Activo'::character varying, 'Inactivo'::character varying])::text[])))
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
    nombre character varying(50) NOT NULL,
    estado character varying(20) DEFAULT 'Activo'::character varying NOT NULL,
    CONSTRAINT departamento_geografico_estado_check CHECK (((estado)::text = ANY ((ARRAY['Activo'::character varying, 'Inactivo'::character varying])::text[])))
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
    subtotal numeric(10,2) NOT NULL,
    CONSTRAINT detalle_arqueo_efectivo_cantidad_piezas_check CHECK ((cantidad_piezas >= 0))
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
    subtotal numeric(10,2) NOT NULL,
    CONSTRAINT detalle_compra_cantidad_recibida_check CHECK ((cantidad_recibida >= 0))
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
    costo_perdida numeric(10,2) NOT NULL,
    CONSTRAINT detalle_merma_cantidad_check CHECK ((cantidad >= 0))
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
    costo_pactado numeric(10,2) NOT NULL,
    CONSTRAINT detalle_orden_compra_cantidad_pedida_check CHECK ((cantidad_pedida >= 0))
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
    subtotal numeric(10,2) NOT NULL,
    CONSTRAINT detalle_venta_cantidad_check CHECK ((cantidad >= 0))
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
    numero_autorizacion_sat character varying(50),
    serie character varying(20),
    numero_dte character varying(30),
    fecha_certificacion timestamp without time zone,
    nit_receptor character varying(15) NOT NULL,
    nombre_receptor character varying(120) NOT NULL,
    total_facturado numeric(10,2) NOT NULL,
    estado character varying(20) DEFAULT 'Certificada'::character varying NOT NULL
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
    intentos_fallidos integer DEFAULT 0 NOT NULL,
    bloqueado_hasta timestamp without time zone,
    ultimo_intento timestamp without time zone DEFAULT now() NOT NULL
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
    fecha_actualizacion timestamp without time zone NOT NULL,
    CONSTRAINT inventario_sucursal_stock_actual_check CHECK ((stock_actual >= 0)),
    CONSTRAINT inventario_sucursal_stock_minimo_check CHECK ((stock_minimo >= 0))
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
    nombre character varying(30) NOT NULL,
    estado character varying(20) DEFAULT 'Activo'::character varying NOT NULL,
    CONSTRAINT metodo_pago_estado_check CHECK (((estado)::text = ANY ((ARRAY['Activo'::character varying, 'Inactivo'::character varying])::text[])))
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
    descripcion character varying(100) NOT NULL,
    estado character varying(20) DEFAULT 'Activo'::character varying NOT NULL,
    CONSTRAINT motivo_merma_estado_check CHECK (((estado)::text = ANY ((ARRAY['Activo'::character varying, 'Inactivo'::character varying])::text[])))
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
    nombre character varying(50) NOT NULL,
    estado character varying(20) DEFAULT 'Activo'::character varying NOT NULL,
    CONSTRAINT municipio_estado_check CHECK (((estado)::text = ANY ((ARRAY['Activo'::character varying, 'Inactivo'::character varying])::text[])))
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
    estado character varying(20) NOT NULL,
    CONSTRAINT orden_compra_estado_check CHECK (((estado)::text = ANY ((ARRAY['Emitida'::character varying, 'Recibida'::character varying, 'Cancelada'::character varying])::text[])))
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
    fecha_creacion timestamp without time zone DEFAULT now() NOT NULL,
    CONSTRAINT producto_estado_check CHECK (((estado)::text = ANY ((ARRAY['Activo'::character varying, 'Inactivo'::character varying])::text[])))
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
    direccion character varying(150),
    estado character varying(20) DEFAULT 'Activo'::character varying NOT NULL,
    fecha_creacion timestamp without time zone DEFAULT now() NOT NULL,
    CONSTRAINT proveedor_estado_check CHECK (((estado)::text = ANY ((ARRAY['Activo'::character varying, 'Inactivo'::character varying])::text[])))
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
    estado character varying(20) NOT NULL,
    CONSTRAINT rol_estado_check CHECK (((estado)::text = ANY ((ARRAY['Activo'::character varying, 'Inactivo'::character varying])::text[])))
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
    nombre character varying(50) NOT NULL,
    estado character varying(20) DEFAULT 'Activo'::character varying NOT NULL,
    CONSTRAINT subcategoria_estado_check CHECK (((estado)::text = ANY ((ARRAY['Activo'::character varying, 'Inactivo'::character varying])::text[])))
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
    estado character varying(20) NOT NULL,
    fecha_creacion timestamp without time zone DEFAULT now() NOT NULL,
    CONSTRAINT sucursal_estado_check CHECK (((estado)::text = ANY ((ARRAY['Activo'::character varying, 'Inactivo'::character varying])::text[])))
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
-- Name: tipo_cliente; Type: TABLE; Schema: public; Owner: regalito_admin
--

CREATE TABLE public.tipo_cliente (
    id_tipo_cliente integer NOT NULL,
    nombre character varying(50) NOT NULL,
    descuento_predeterminado numeric(5,2),
    estado character varying(20) DEFAULT 'Activo'::character varying NOT NULL,
    CONSTRAINT tipo_cliente_estado_check CHECK (((estado)::text = ANY ((ARRAY['Activo'::character varying, 'Inactivo'::character varying])::text[])))
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
    fecha_traslado timestamp without time zone NOT NULL,
    estado character varying(20) DEFAULT 'En tránsito'::character varying NOT NULL,
    id_usuario_envia integer,
    id_usuario_recibe integer,
    fecha_recepcion timestamp without time zone,
    observaciones text,
    CONSTRAINT traslado_inventario_cantidad_check CHECK ((cantidad >= 0))
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
    notas text,
    CONSTRAINT turno_caja_estado_check CHECK (((estado)::text = ANY ((ARRAY['Abierto'::character varying, 'Cerrado'::character varying, 'Abierta'::character varying, 'Cerrada'::character varying])::text[])))
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
    descripcion character varying(50) NOT NULL,
    estado character varying(20) DEFAULT 'Activo'::character varying NOT NULL,
    CONSTRAINT unidad_medida_estado_check CHECK (((estado)::text = ANY ((ARRAY['Activo'::character varying, 'Inactivo'::character varying])::text[])))
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
    fecha_creacion timestamp without time zone DEFAULT now() NOT NULL,
    CONSTRAINT usuario_estado_check CHECK (((estado)::text = ANY ((ARRAY['Activo'::character varying, 'Inactivo'::character varying])::text[])))
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
    estado character varying(20) NOT NULL,
    CONSTRAINT venta_estado_check CHECK (((estado)::text = ANY ((ARRAY['Completada'::character varying, 'Anulada'::character varying])::text[])))
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
-- Name: visita_modulo_evaluacion; Type: TABLE; Schema: public; Owner: regalito_admin
--

CREATE TABLE public.visita_modulo_evaluacion (
    id_modulo_eval integer NOT NULL,
    id_visita integer NOT NULL,
    nombre_modulo character varying(100) NOT NULL,
    calificacion smallint,
    comentario text,
    resultado character varying(20),
    CONSTRAINT visita_modulo_evaluacion_calificacion_check CHECK (((calificacion >= 1) AND (calificacion <= 10)))
);


ALTER TABLE public.visita_modulo_evaluacion OWNER TO regalito_admin;

--
-- Name: visita_modulo_evaluacion_id_modulo_eval_seq; Type: SEQUENCE; Schema: public; Owner: regalito_admin
--

CREATE SEQUENCE public.visita_modulo_evaluacion_id_modulo_eval_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.visita_modulo_evaluacion_id_modulo_eval_seq OWNER TO regalito_admin;

--
-- Name: visita_modulo_evaluacion_id_modulo_eval_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: regalito_admin
--

ALTER SEQUENCE public.visita_modulo_evaluacion_id_modulo_eval_seq OWNED BY public.visita_modulo_evaluacion.id_modulo_eval;


--
-- Name: visita_seguimiento; Type: TABLE; Schema: public; Owner: regalito_admin
--

CREATE TABLE public.visita_seguimiento (
    id_visita integer NOT NULL,
    id_cliente integer,
    id_usuario integer NOT NULL,
    fecha_visita date NOT NULL,
    observaciones text,
    estado character varying(20) DEFAULT 'Pendiente'::character varying NOT NULL,
    fecha_creacion timestamp without time zone DEFAULT now() NOT NULL,
    lugar character varying(150),
    nombre_representante character varying(150),
    cargo_representante character varying(100),
    calificacion_general smallint,
    CONSTRAINT visita_seguimiento_estado_check CHECK (((estado)::text = ANY ((ARRAY['Pendiente'::character varying, 'Completada'::character varying, 'Cancelada'::character varying])::text[])))
);


ALTER TABLE public.visita_seguimiento OWNER TO regalito_admin;

--
-- Name: visita_seguimiento_id_visita_seq; Type: SEQUENCE; Schema: public; Owner: regalito_admin
--

CREATE SEQUENCE public.visita_seguimiento_id_visita_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.visita_seguimiento_id_visita_seq OWNER TO regalito_admin;

--
-- Name: visita_seguimiento_id_visita_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: regalito_admin
--

ALTER SEQUENCE public.visita_seguimiento_id_visita_seq OWNED BY public.visita_seguimiento.id_visita;


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
-- Name: visita_modulo_evaluacion id_modulo_eval; Type: DEFAULT; Schema: public; Owner: regalito_admin
--

ALTER TABLE ONLY public.visita_modulo_evaluacion ALTER COLUMN id_modulo_eval SET DEFAULT nextval('public.visita_modulo_evaluacion_id_modulo_eval_seq'::regclass);


--
-- Name: visita_seguimiento id_visita; Type: DEFAULT; Schema: public; Owner: regalito_admin
--

ALTER TABLE ONLY public.visita_seguimiento ALTER COLUMN id_visita SET DEFAULT nextval('public.visita_seguimiento_id_visita_seq'::regclass);


--
-- Data for Name: alembic_version; Type: TABLE DATA; Schema: public; Owner: regalito_admin
--

COPY public.alembic_version (version_num) FROM stdin;
0015
\.


--
-- Data for Name: alerta_stock; Type: TABLE DATA; Schema: public; Owner: regalito_admin
--

COPY public.alerta_stock (id_alerta, id_inventario, mensaje, fecha_generacion, estado) FROM stdin;
1	2	Vestido de Niña 2T por debajo del stock mínimo	2026-10-22 02:49:43.921364	Pendiente
\.


--
-- Data for Name: area_bodega; Type: TABLE DATA; Schema: public; Owner: regalito_admin
--

COPY public.area_bodega (id_area, id_sucursal, nombre_area, estado) FROM stdin;
1	1	Vitrina Principal	Activo
2	1	Bodega Fondo	Activo
3	1	Mostrador	Activo
\.


--
-- Data for Name: bitacora_auditoria; Type: TABLE DATA; Schema: public; Owner: regalito_admin
--

COPY public.bitacora_auditoria (id_bitacora, id_usuario, tabla_afectada, accion, descripcion, fecha_hora) FROM stdin;
17	1	Subcategoria	CREATE	Creó subcategoría 'Subcat Playwright Test' en categoría 1	2026-10-21 23:41:58.10955
19	1	Subcategoria	CREATE	Creó subcategoría 'Subcat Playwright Test' en categoría 1	2026-10-21 23:45:01.191504
21	1	Subcategoria	CREATE	Creó subcategoría 'Subcat Playwright Test' en categoría 1	2026-10-21 23:45:35.790326
22	1	Subcategoria	UPDATE	Actualizó subcategoría 'Subcat Playwright Editada' (ID: 8)	2026-10-21 23:45:37.672879
23	1	Subcategoria	DEACTIVATE	Desactivó subcategoría 'Subcat Playwright Editada' (ID: 8)	2026-10-21 23:45:40.377352
24	1	Subcategoria	ACTIVATE	Reactivó subcategoría 'Subcat Playwright Editada' (ID: 8)	2026-10-21 23:45:41.671433
26	1	Subcategoria	CREATE	Creó subcategoría 'Subcat Playwright Test' en categoría 1	2026-10-21 23:46:16.972689
27	1	Subcategoria	UPDATE	Actualizó subcategoría 'Subcat Playwright Editada' (ID: 9)	2026-10-21 23:46:18.852999
28	1	Subcategoria	DEACTIVATE	Desactivó subcategoría 'Subcat Playwright Editada' (ID: 9)	2026-10-21 23:46:21.591751
29	1	Subcategoria	ACTIVATE	Reactivó subcategoría 'Subcat Playwright Editada' (ID: 9)	2026-10-21 23:46:22.916683
31	1	Subcategoria	CREATE	Creó subcategoría 'Subcat Playwright Test' en categoría 1	2026-10-21 23:47:17.784617
32	1	Subcategoria	UPDATE	Actualizó subcategoría 'Subcat Playwright Editada' (ID: 10)	2026-10-21 23:47:19.750272
33	1	Subcategoria	DEACTIVATE	Desactivó subcategoría 'Subcat Playwright Editada' (ID: 10)	2026-10-21 23:47:22.498772
34	1	Subcategoria	ACTIVATE	Reactivó subcategoría 'Subcat Playwright Editada' (ID: 10)	2026-10-21 23:47:23.832946
35	1	UnidadMedida	CREATE	Creó unidad de medida 'Galón Playwright' (GLN)	2026-10-21 23:47:26.599695
36	1	UnidadMedida	DEACTIVATE	Desactivó unidad de medida 'Galón Playwright' (ID: 5)	2026-10-21 23:47:29.994476
37	1	UnidadMedida	ACTIVATE	Reactivó unidad de medida 'Galón Playwright' (ID: 5)	2026-10-21 23:47:31.233908
38	1	Sucursal	CREATE	Creó sucursal 'Sucursal Playwright Test' (ID: 2)	2026-10-21 23:47:33.835397
39	1	Sucursal	DEACTIVATE	Desactivó sucursal 'Sucursal Playwright Test' (ID: 2)	2026-10-21 23:47:35.700067
40	1	Sucursal	ACTIVATE	Reactivó sucursal 'Sucursal Playwright Test' (ID: 2)	2026-10-21 23:47:36.932544
42	1	Subcategoria	CREATE	Creó subcategoría 'Subcat Playwright Test' en categoría 1	2026-10-21 23:48:23.900261
43	1	Subcategoria	UPDATE	Actualizó subcategoría 'Subcat Playwright Editada' (ID: 11)	2026-10-21 23:48:25.918726
44	1	Subcategoria	DEACTIVATE	Desactivó subcategoría 'Subcat Playwright Editada' (ID: 11)	2026-10-21 23:48:28.528515
45	1	Subcategoria	ACTIVATE	Reactivó subcategoría 'Subcat Playwright Editada' (ID: 11)	2026-10-21 23:48:29.845728
46	1	UnidadMedida	CREATE	Creó unidad de medida 'Galón Playwright' (GLN)	2026-10-21 23:48:32.595439
47	1	UnidadMedida	DEACTIVATE	Desactivó unidad de medida 'Galón Playwright' (ID: 6)	2026-10-21 23:48:35.912583
48	1	UnidadMedida	ACTIVATE	Reactivó unidad de medida 'Galón Playwright' (ID: 6)	2026-10-21 23:48:37.144357
49	1	Sucursal	CREATE	Creó sucursal 'Sucursal Playwright Test' (ID: 3)	2026-10-21 23:48:39.745114
50	1	Sucursal	DEACTIVATE	Desactivó sucursal 'Sucursal Playwright Test' (ID: 3)	2026-10-21 23:48:41.632263
51	1	Sucursal	ACTIVATE	Reactivó sucursal 'Sucursal Playwright Test' (ID: 3)	2026-10-21 23:48:42.862751
52	1	AreaBodega	CREATE	Creó área de bodega 'Bodega Playwright Test' en sucursal 3	2026-10-21 23:48:45.582992
53	1	AreaBodega	DEACTIVATE	Desactivó área de bodega 'Bodega Playwright Test' (ID: 4)	2026-10-21 23:48:49.795655
54	1	AreaBodega	ACTIVATE	Reactivó área de bodega 'Bodega Playwright Test' (ID: 4)	2026-10-21 23:48:51.029546
\.


--
-- Data for Name: caja; Type: TABLE DATA; Schema: public; Owner: regalito_admin
--

COPY public.caja (id_caja, id_sucursal, descripcion, estado) FROM stdin;
1	1	Caja Principal Mostrador	Activa
\.


--
-- Data for Name: categoria; Type: TABLE DATA; Schema: public; Owner: regalito_admin
--

COPY public.categoria (id_categoria, nombre, estado) FROM stdin;
1	Cristalería	Activo
2	Ropa	Activo
3	Juguetes	Activo
4	Hogar	Activo
\.


--
-- Data for Name: cierre_caja_ciegas; Type: TABLE DATA; Schema: public; Owner: regalito_admin
--

COPY public.cierre_caja_ciegas (id_cierre, id_turno, id_usuario_cajero, id_usuario_supervisor, total_contado_ciegas, total_calculado_sistema, diferencia, observaciones, fecha_cierre) FROM stdin;
\.


--
-- Data for Name: cliente; Type: TABLE DATA; Schema: public; Owner: regalito_admin
--

COPY public.cliente (id_cliente, id_tipo_cliente, id_municipio, nit, nombre_comercial, direccion, estado, fecha_creacion) FROM stdin;
1	1	1	CF	Consumidor Final	\N	Activo	2026-10-22 02:51:06.832772
2	3	1	9876543-2	Tienda Suyapa	Calle Santander, Panajachel	Activo	2026-10-22 02:51:06.832772
\.


--
-- Data for Name: cliente_contacto; Type: TABLE DATA; Schema: public; Owner: regalito_admin
--

COPY public.cliente_contacto (id_contacto, id_cliente, telefono, correo) FROM stdin;
1	2	5522-3344	tienda.suyapa@mail.com
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
1	200.00	Billete
2	100.00	Billete
3	50.00	Billete
4	20.00	Billete
5	10.00	Billete
6	5.00	Billete
7	1.00	Moneda
8	0.50	Moneda
\.


--
-- Data for Name: departamento_geografico; Type: TABLE DATA; Schema: public; Owner: regalito_admin
--

COPY public.departamento_geografico (id_departamento, nombre, estado) FROM stdin;
1	Sololá	Activo
2	Quetzaltenango	Activo
3	Alta Verapaz	Activo
4	Baja Verapaz	Activo
5	Chimaltenango	Activo
6	Chiquimula	Activo
7	El Progreso	Activo
8	Escuintla	Activo
9	Guatemala	Activo
10	Huehuetenango	Activo
11	Izabal	Activo
12	Jalapa	Activo
13	Jutiapa	Activo
14	Petén	Activo
16	Quiché	Activo
17	Retalhuleu	Activo
18	Sacatepéquez	Activo
19	San Marcos	Activo
20	Santa Rosa	Activo
22	Suchitepéquez	Activo
23	Totonicapán	Activo
24	Zacapa	Activo
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

COPY public.factura_fel (id_factura, id_venta, numero_autorizacion_sat, serie, numero_dte, fecha_certificacion, nit_receptor, nombre_receptor, total_facturado, estado) FROM stdin;
\.


--
-- Data for Name: historial_precio; Type: TABLE DATA; Schema: public; Owner: regalito_admin
--

COPY public.historial_precio (id_historial, id_variante, id_usuario, precio_anterior, precio_nuevo, fecha_modificacion) FROM stdin;
1	1	1	80.00	85.00	2026-10-22 02:49:43.919723
\.


--
-- Data for Name: intento_login; Type: TABLE DATA; Schema: public; Owner: regalito_admin
--

COPY public.intento_login (id_intento, username, intentos_fallidos, bloqueado_hasta, ultimo_intento) FROM stdin;
\.


--
-- Data for Name: inventario_sucursal; Type: TABLE DATA; Schema: public; Owner: regalito_admin
--

COPY public.inventario_sucursal (id_inventario, id_variante, id_sucursal, id_area, stock_actual, stock_minimo, fecha_actualizacion) FROM stdin;
1	1	1	1	24	8	2026-10-22 02:49:43.917895
2	2	1	1	12	5	2026-10-22 02:49:43.917895
3	3	1	2	10	5	2026-10-22 02:49:43.917895
4	4	1	1	30	10	2026-10-22 02:49:43.917895
\.


--
-- Data for Name: merma; Type: TABLE DATA; Schema: public; Owner: regalito_admin
--

COPY public.merma (id_merma, id_sucursal, id_usuario, fecha_merma, observaciones) FROM stdin;
\.


--
-- Data for Name: metodo_pago; Type: TABLE DATA; Schema: public; Owner: regalito_admin
--

COPY public.metodo_pago (id_metodo_pago, nombre, estado) FROM stdin;
1	Efectivo	Activo
2	Transferencia	Activo
\.


--
-- Data for Name: motivo_merma; Type: TABLE DATA; Schema: public; Owner: regalito_admin
--

COPY public.motivo_merma (id_motivo, descripcion, estado) FROM stdin;
1	Cristalería Quebrada	Activo
2	Ropa Manchada	Activo
3	Defecto Fábrica	Activo
\.


--
-- Data for Name: movimiento_caja; Type: TABLE DATA; Schema: public; Owner: regalito_admin
--

COPY public.movimiento_caja (id_movimiento, id_turno, id_tipo_movimiento, id_usuario, monto, justificacion, fecha_hora) FROM stdin;
\.


--
-- Data for Name: municipio; Type: TABLE DATA; Schema: public; Owner: regalito_admin
--

COPY public.municipio (id_municipio, id_departamento, nombre, estado) FROM stdin;
1	1	Panajachel	Activo
2	1	Sololá	Activo
3	2	Quetzaltenango	Activo
4	3	Cobán	Activo
5	3	Santa Cruz Verapaz	Activo
6	3	San Cristóbal Verapaz	Activo
7	3	Tactic	Activo
8	3	Tamahú	Activo
9	3	Tucurú	Activo
10	3	Panzós	Activo
11	3	Senahú	Activo
12	3	San Pedro Carchá	Activo
13	3	San Juan Chamelco	Activo
14	3	Lanquín	Activo
15	3	Cahabón	Activo
16	3	Chisec	Activo
17	3	Chahal	Activo
18	3	Fray Bartolomé de las Casas	Activo
19	3	Santa Catalina La Tinta	Activo
20	3	Raxruhá	Activo
21	4	Salamá	Activo
22	4	San Miguel Chicaj	Activo
23	4	Rabinal	Activo
24	4	Cubulco	Activo
25	4	Granados	Activo
26	4	El Chol	Activo
27	4	San Jerónimo	Activo
28	4	Purulhá	Activo
29	5	Chimaltenango	Activo
30	5	San José Poaquil	Activo
31	5	San Martín Jilotepeque	Activo
32	5	Comalapa	Activo
33	5	Santa Apolonia	Activo
34	5	Tecpán Guatemala	Activo
35	5	Patzún	Activo
36	5	Pochuta	Activo
37	5	Patzicía	Activo
38	5	Santa Cruz Balanyá	Activo
39	5	Acatenango	Activo
40	5	Yepocapa	Activo
41	5	San Andrés Itzapa	Activo
42	5	Parramos	Activo
43	5	Zaragoza	Activo
44	5	El Tejar	Activo
45	6	Chiquimula	Activo
46	6	San José La Arada	Activo
47	6	San Juan La Ermita	Activo
48	6	Jocotán	Activo
49	6	Camotán	Activo
50	6	Olopa	Activo
51	6	Esquipulas	Activo
52	6	Concepción Las Minas	Activo
53	6	Quezaltepeque	Activo
54	6	San Jacinto	Activo
55	6	Ipala	Activo
56	7	Guastatoya	Activo
57	7	Morazán	Activo
58	7	San Agustín Acasaguastlán	Activo
59	7	San Cristóbal Acasaguastlán	Activo
60	7	El Jícaro	Activo
61	7	Sansare	Activo
62	7	Sanarate	Activo
63	7	San Antonio La Paz	Activo
64	8	Escuintla	Activo
65	8	Santa Lucía Cotzumalguapa	Activo
66	8	La Democracia	Activo
67	8	Siquinalá	Activo
68	8	Masagua	Activo
69	8	Tiquisate	Activo
70	8	La Gomera	Activo
71	8	Guanagazapa	Activo
72	8	San José	Activo
73	8	Iztapa	Activo
74	8	Palín	Activo
75	8	San Vicente Pacaya	Activo
76	8	Nueva Concepción	Activo
77	9	Guatemala	Activo
78	9	Santa Catarina Pinula	Activo
79	9	San José Pinula	Activo
80	9	San José del Golfo	Activo
81	9	Palencia	Activo
82	9	Chinautla	Activo
83	9	San Pedro Ayampuc	Activo
84	9	Mixco	Activo
85	9	San Pedro Sacatepéquez	Activo
86	9	San Juan Sacatepéquez	Activo
87	9	San Raymundo	Activo
88	9	Chuarrancho	Activo
89	9	Fraijanes	Activo
90	9	Amatitlán	Activo
91	9	Villa Nueva	Activo
92	9	Villa Canales	Activo
93	9	San Miguel Petapa	Activo
94	10	Huehuetenango	Activo
95	10	Chiantla	Activo
96	10	Malacatancito	Activo
97	10	Cuilco	Activo
98	10	Nentón	Activo
99	10	San Pedro Necta	Activo
100	10	Jacaltenango	Activo
101	10	Soloma	Activo
102	10	Ixtahuacán	Activo
103	10	Santa Bárbara	Activo
104	10	La Libertad	Activo
105	10	La Democracia	Activo
106	10	San Miguel Acatán	Activo
107	10	San Rafael La Independencia	Activo
108	10	Todos Santos Cuchumatán	Activo
109	10	San Juan Atitán	Activo
110	10	Santa Eulalia	Activo
111	10	San Mateo Ixtatán	Activo
112	10	Colotenango	Activo
113	10	San Sebastián Huehuetenango	Activo
114	10	Tectitán	Activo
115	10	Concepción Huista	Activo
116	10	San Juan Ixcoy	Activo
117	10	San Antonio Huista	Activo
118	10	San Sebastián Coatán	Activo
119	10	Barillas	Activo
120	10	Aguacatán	Activo
121	10	San Rafael Petzal	Activo
122	10	San Gaspar Ixchil	Activo
123	10	Santiago Chimaltenango	Activo
124	10	Santa Ana Huista	Activo
125	10	Unión Cantinil	Activo
126	11	Puerto Barrios	Activo
127	11	Livingston	Activo
128	11	El Estor	Activo
129	11	Morales	Activo
130	11	Los Amates	Activo
131	12	Jalapa	Activo
132	12	San Pedro Pinula	Activo
133	12	San Luis Jilotepeque	Activo
134	12	San Manuel Chaparrón	Activo
135	12	San Carlos Alzatate	Activo
136	12	Monjas	Activo
137	12	Mataquescuintla	Activo
138	13	Jutiapa	Activo
139	13	El Progreso	Activo
140	13	Santa Catarina Mita	Activo
141	13	Agua Blanca	Activo
142	13	Asunción Mita	Activo
143	13	Yupiltepeque	Activo
144	13	Atescatempa	Activo
145	13	Jerez	Activo
146	13	El Adelanto	Activo
147	13	Zapotitlán	Activo
148	13	Comapa	Activo
149	13	Jalpatagua	Activo
150	13	Conguaco	Activo
151	13	Moyuta	Activo
152	13	Pasaco	Activo
153	13	San José Acatempa	Activo
154	13	Quesada	Activo
155	14	Flores	Activo
156	14	San José	Activo
157	14	San Benito	Activo
158	14	San Andrés	Activo
159	14	La Libertad	Activo
160	14	San Francisco	Activo
161	14	Santa Ana	Activo
162	14	Dolores	Activo
163	14	San Luis	Activo
164	14	Sayaxché	Activo
165	14	Melchor de Mencos	Activo
166	14	Poptún	Activo
168	2	Salcajá	Activo
169	2	Olintepeque	Activo
170	2	San Carlos Sija	Activo
171	2	Sibilia	Activo
172	2	Cabricán	Activo
173	2	Cajolá	Activo
174	2	San Miguel Sigüilá	Activo
175	2	Ostuncalco	Activo
176	2	San Mateo	Activo
177	2	Concepción Chiquirichapa	Activo
178	2	San Martín Sacatepéquez	Activo
179	2	Almolonga	Activo
180	2	Cantel	Activo
181	2	Huitán	Activo
182	2	Zunil	Activo
183	2	Colomba	Activo
184	2	San Francisco La Unión	Activo
185	2	El Palmar	Activo
186	2	Coatepeque	Activo
187	2	Génova	Activo
188	2	Flores Costa Cuca	Activo
189	2	La Esperanza	Activo
190	2	Palestina de Los Altos	Activo
191	16	Santa Cruz del Quiché	Activo
192	16	Chiché	Activo
193	16	Chinique	Activo
194	16	Zacualpa	Activo
195	16	Chajul	Activo
196	16	Chichicastenango	Activo
197	16	Patzité	Activo
198	16	San Antonio Ilotenango	Activo
199	16	San Pedro Jocopilas	Activo
200	16	Cunén	Activo
201	16	San Juan Cotzal	Activo
202	16	Joyabaj	Activo
203	16	Nebaj	Activo
204	16	San Andrés Sajcabajá	Activo
205	16	Uspantán	Activo
206	16	Sacapulas	Activo
207	16	San Bartolomé Jocotenango	Activo
208	16	Canillá	Activo
209	16	Chicamán	Activo
210	16	Ixcán	Activo
211	16	Pachalum	Activo
212	17	Retalhuleu	Activo
213	17	San Sebastián	Activo
214	17	Santa Cruz Muluá	Activo
215	17	San Martín Zapotitlán	Activo
216	17	San Felipe	Activo
217	17	San Andrés Villa Seca	Activo
218	17	Champerico	Activo
219	17	Nuevo San Carlos	Activo
220	17	El Asintal	Activo
221	18	Antigua Guatemala	Activo
222	18	Jocotenango	Activo
223	18	Pastores	Activo
224	18	Sumpango	Activo
225	18	Santo Domingo Xenacoj	Activo
226	18	Santiago Sacatepéquez	Activo
227	18	San Bartolomé Milpas Altas	Activo
228	18	San Lucas Sacatepéquez	Activo
229	18	Santa Lucía Milpas Altas	Activo
230	18	Magdalena Milpas Altas	Activo
231	18	Santa María de Jesús	Activo
232	18	Ciudad Vieja	Activo
233	18	San Miguel Dueñas	Activo
234	18	Alotenango	Activo
235	18	San Antonio Aguas Calientes	Activo
236	18	Santa Catarina Barahona	Activo
237	19	San Marcos	Activo
238	19	San Pedro Sacatepéquez	Activo
239	19	San Antonio Sacatepéquez	Activo
240	19	Comitancillo	Activo
241	19	San Miguel Ixtahuacán	Activo
242	19	Concepción Tutuapa	Activo
243	19	Tacaná	Activo
244	19	Sibinal	Activo
245	19	Tajumulco	Activo
246	19	Tejutla	Activo
247	19	San Rafael Pie de la Cuesta	Activo
248	19	Nuevo Progreso	Activo
249	19	El Tumbador	Activo
250	19	El Rodeo	Activo
251	19	Malacatán	Activo
252	19	Catarina	Activo
253	19	Ayutla	Activo
254	19	Ocós	Activo
255	19	San Pablo	Activo
256	19	El Quetzal	Activo
257	19	La Reforma	Activo
258	19	Pajapita	Activo
259	19	Ixchiguán	Activo
260	19	San José Ojetenam	Activo
261	19	San Cristóbal Cucho	Activo
262	19	Sipacapa	Activo
263	19	Esquipulas Palo Gordo	Activo
264	19	Río Blanco	Activo
265	19	San Lorenzo	Activo
266	19	La Blanca	Activo
267	20	Cuilapa	Activo
268	20	Barberena	Activo
269	20	Santa Rosa de Lima	Activo
270	20	Casillas	Activo
271	20	San Rafael Las Flores	Activo
272	20	Oratorio	Activo
273	20	San Juan Tecuaco	Activo
274	20	Chiquimulilla	Activo
275	20	Taxisco	Activo
276	20	Santa María Ixhuatán	Activo
277	20	Guazacapán	Activo
278	20	Santa Cruz Naranjo	Activo
279	20	Pueblo Nuevo Viñas	Activo
280	20	Nueva Santa Rosa	Activo
282	1	San José Chacayá	Activo
283	1	Santa María Visitación	Activo
284	1	Santa Lucía Utatlán	Activo
285	1	Nahualá	Activo
286	1	Santa Catarina Ixtahuacán	Activo
287	1	Santa Clara La Laguna	Activo
288	1	Concepción	Activo
289	1	San Andrés Semetabaj	Activo
291	1	Santa Catarina Palopó	Activo
292	1	San Antonio Palopó	Activo
293	1	San Lucas Tolimán	Activo
294	1	Santa Cruz La Laguna	Activo
295	1	San Pablo La Laguna	Activo
296	1	San Marcos La Laguna	Activo
297	1	San Juan La Laguna	Activo
298	1	San Pedro La Laguna	Activo
299	1	Santiago Atitlán	Activo
300	22	Mazatenango	Activo
301	22	Cuyotenango	Activo
302	22	San Francisco Zapotitlán	Activo
303	22	San Bernardino	Activo
304	22	San José El Ídolo	Activo
305	22	Santo Domingo Suchitepéquez	Activo
306	22	San Lorenzo	Activo
307	22	Samayac	Activo
308	22	San Pablo Jocopilas	Activo
309	22	San Antonio Suchitepéquez	Activo
310	22	San Miguel Panán	Activo
311	22	San Gabriel	Activo
312	22	Chicacao	Activo
313	22	Patulul	Activo
314	22	Santa Bárbara	Activo
315	22	San Juan Bautista	Activo
316	22	Santo Tomás La Unión	Activo
317	22	Zunilito	Activo
318	22	Pueblo Nuevo	Activo
319	22	Río Bravo	Activo
320	22	San José La Máquina	Activo
321	23	Totonicapán	Activo
322	23	San Cristóbal Totonicapán	Activo
323	23	San Francisco El Alto	Activo
324	23	San Andrés Xecul	Activo
325	23	Momostenango	Activo
326	23	Santa María Chiquimula	Activo
327	23	Santa Lucía La Reforma	Activo
328	23	San Bartolo	Activo
329	24	Zacapa	Activo
330	24	Estanzuela	Activo
331	24	Río Hondo	Activo
332	24	Gualán	Activo
333	24	Teculután	Activo
334	24	Usumatlán	Activo
335	24	Cabañas	Activo
336	24	San Diego	Activo
337	24	La Unión	Activo
338	24	Huité	Activo
339	24	San Jorge	Activo
340	10	Petatán	Activo
341	14	El Chal	Activo
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
1	NIT_EMPRESA	12345678-9
2	IVA_PORCENTAJE	12
3	SERIE_DTE	A
4	RUTA_LOGO	/img/logo.png
\.


--
-- Data for Name: permiso; Type: TABLE DATA; Schema: public; Owner: regalito_admin
--

COPY public.permiso (id_permiso, modulo, codigo, descripcion) FROM stdin;
1	Ventas	VENTA_COBRAR	Registrar cobros en mostrador
2	Ventas	VENTA_APLICAR_DESCUENTO	Aplicar descuentos por volumen
3	Inventario	INV_INGRESAR_MERCADERIA	Registrar ingreso de compras
4	Caja	CAJA_CIERRE_CIEGAS	Ejecutar arqueo de caja a ciegas
5	Compras	COMPRA_EMITIR_ORDEN	Emitir órdenes de compra
6	Clientes	CLIENTE_ADMIN	Gestión completa de clientes
7	Seguridad	BITACORA_CONSULTAR	Consultar bitácora de auditoría
8	Reportes	REPORTE_VER	Ver reportes del sistema
9	Catálogo	CATALOGO_ADMIN	Gestión completa de catálogos
10	Visitas	VISITA_REGISTRAR	Registrar y consultar visitas de seguimiento
11	Seguridad	ROL_ADMIN	Gestión completa de roles y permisos
12	Seguridad	USUARIO_ADMIN	Gestión completa de usuarios
\.


--
-- Data for Name: producto; Type: TABLE DATA; Schema: public; Owner: regalito_admin
--

COPY public.producto (id_producto, id_subcategoria, id_unidad, nombre, descripcion, imagen_url, estado, fecha_creacion) FROM stdin;
1	1	1	Juego de Vasos de Cristal	Set de 6 vasos de cristal templado para mesa	/img/vasos-cristal.jpg	Activo	2026-10-22 02:49:43.91434
2	3	1	Vestido de Niña 2T	Vestido de algodón con bordado guatemalteco	/img/vestido-2t.jpg	Activo	2026-10-22 02:49:43.91434
3	4	1	Muñeca de Trapo Artesanal	Muñeca de tela tejida a mano, vestido tradicional	/img/muneca-trapo.jpg	Activo	2026-10-22 02:49:43.91434
\.


--
-- Data for Name: proveedor; Type: TABLE DATA; Schema: public; Owner: regalito_admin
--

COPY public.proveedor (id_proveedor, nombre_contacto, distribuidora, telefono, correo, cuenta_bancaria, direccion, estado, fecha_creacion) FROM stdin;
1	Carlos Mendoza	Vidriería Lago S.A.	5522-7788	ventas@vidrierialago.com	3456-789012-3	Zona 3, Sololá	Activo	2026-10-22 02:51:06.832772
2	Lucía Ramírez	Textiles del Altiplano	5544-2233	pedidos@textilesaltiplano.com	6789-012345-6	Zona 5, Quetzaltenango	Activo	2026-10-22 02:51:06.832772
3	Ana Pérez	Juguetería Maya Distribuciones	5500-1122	ventas@jugueteriamaya.com	1234-567890-1	Zona 2, Panajachel	Activo	2026-10-22 02:51:06.832772
\.


--
-- Data for Name: rol; Type: TABLE DATA; Schema: public; Owner: regalito_admin
--

COPY public.rol (id_rol, nombre, descripcion, estado) FROM stdin;
1	Administradora	Control total del sistema y arqueos de caja	Activo
2	Cajero	Opera el punto de venta y cobros en mostrador	Activo
3	Bodeguero	Gestiona inventario, mermas y traslados	Activo
\.


--
-- Data for Name: rol_permiso; Type: TABLE DATA; Schema: public; Owner: regalito_admin
--

COPY public.rol_permiso (id_rol, id_permiso) FROM stdin;
1	1
1	2
1	3
1	4
1	5
2	1
2	2
3	3
1	6
1	7
1	8
1	9
1	10
1	11
1	12
\.


--
-- Data for Name: sesion_usuario; Type: TABLE DATA; Schema: public; Owner: regalito_admin
--

COPY public.sesion_usuario (id_sesion, id_usuario, fecha_inicio, fecha_fin, ip_origen) FROM stdin;
\.


--
-- Data for Name: subcategoria; Type: TABLE DATA; Schema: public; Owner: regalito_admin
--

COPY public.subcategoria (id_subcategoria, id_categoria, nombre, estado) FROM stdin;
1	1	Vasos	Activo
2	1	Floreros	Activo
3	2	Ropa Bebé	Activo
4	3	Muñecas	Activo
5	4	Deco Hogar	Activo
\.


--
-- Data for Name: sucursal; Type: TABLE DATA; Schema: public; Owner: regalito_admin
--

COPY public.sucursal (id_sucursal, nombre, direccion, telefono, estado, fecha_creacion) FROM stdin;
1	Tienda Central Panajachel	Callejón Don Fidel, zona 1	7762-3456	Activo	2026-10-22 02:51:06.832772
\.


--
-- Data for Name: tipo_cliente; Type: TABLE DATA; Schema: public; Owner: regalito_admin
--

COPY public.tipo_cliente (id_tipo_cliente, nombre, descuento_predeterminado, estado) FROM stdin;
1	Consumidor Final	0.00	Activo
2	Minorista	5.00	Activo
3	Mayorista	10.00	Activo
\.


--
-- Data for Name: tipo_movimiento_caja; Type: TABLE DATA; Schema: public; Owner: regalito_admin
--

COPY public.tipo_movimiento_caja (id_tipo_movimiento, nombre) FROM stdin;
1	Ingreso Sencillo Extra
2	Vale Caja Chica
3	Flete
\.


--
-- Data for Name: traslado_inventario; Type: TABLE DATA; Schema: public; Owner: regalito_admin
--

COPY public.traslado_inventario (id_traslado, id_variante, id_sucursal_origen, id_sucursal_destino, cantidad, fecha_traslado, estado, id_usuario_envia, id_usuario_recibe, fecha_recepcion, observaciones) FROM stdin;
\.


--
-- Data for Name: turno_caja; Type: TABLE DATA; Schema: public; Owner: regalito_admin
--

COPY public.turno_caja (id_turno, id_caja, id_usuario, monto_apertura, fecha_apertura, fecha_cierre, estado, monto_cierre, notas) FROM stdin;
\.


--
-- Data for Name: unidad_medida; Type: TABLE DATA; Schema: public; Owner: regalito_admin
--

COPY public.unidad_medida (id_unidad, codigo, descripcion, estado) FROM stdin;
1	UND	Unidad	Activo
2	PAR	Par	Activo
3	DOC	Docena	Activo
4	CJ	Caja cerrada	Activo
\.


--
-- Data for Name: usuario; Type: TABLE DATA; Schema: public; Owner: regalito_admin
--

COPY public.usuario (id_usuario, id_rol, nombre_completo, username, password_hash, estado, fecha_creacion) FROM stdin;
1	1	Propietaria Regalito	admin	$2b$12$igeDz03pyYibOqQO3WJCY.a/XKMHvAAZ2sfh13w.YT7hurdmKFlpG	Activo	2026-10-22 02:49:43.893383
2	2	María Xicay	cajera	$2b$12$igeDz03pyYibOqQO3WJCY.a/XKMHvAAZ2sfh13w.YT7hurdmKFlpG	Activo	2026-10-22 02:49:43.893383
3	3	Pedro Tzoc	bodega	$2b$12$igeDz03pyYibOqQO3WJCY.a/XKMHvAAZ2sfh13w.YT7hurdmKFlpG	Activo	2026-10-22 02:49:43.893383
\.


--
-- Data for Name: variante_producto; Type: TABLE DATA; Schema: public; Owner: regalito_admin
--

COPY public.variante_producto (id_variante, id_producto, codigo_barras, talla, color, precio_detalle, precio_mayoreo, costo_promedio) FROM stdin;
1	1	7401000000011	\N	Transparente	85.00	75.00	52.00
2	2	7401000000028	2T	Rosado	120.00	105.00	68.00
3	2	7401000000035	4T	Azul	120.00	105.00	68.00
4	3	7401000000042	\N	Multicolor	45.00	38.00	24.00
\.


--
-- Data for Name: venta; Type: TABLE DATA; Schema: public; Owner: regalito_admin
--

COPY public.venta (id_venta, id_turno, id_cliente, id_usuario, fecha_venta, subtotal, descuento_total, total_venta, estado) FROM stdin;
\.


--
-- Data for Name: visita_modulo_evaluacion; Type: TABLE DATA; Schema: public; Owner: regalito_admin
--

COPY public.visita_modulo_evaluacion (id_modulo_eval, id_visita, nombre_modulo, calificacion, comentario, resultado) FROM stdin;
\.


--
-- Data for Name: visita_seguimiento; Type: TABLE DATA; Schema: public; Owner: regalito_admin
--

COPY public.visita_seguimiento (id_visita, id_cliente, id_usuario, fecha_visita, observaciones, estado, fecha_creacion, lugar, nombre_representante, cargo_representante, calificacion_general) FROM stdin;
\.


--
-- Name: alerta_stock_id_alerta_seq; Type: SEQUENCE SET; Schema: public; Owner: regalito_admin
--

SELECT pg_catalog.setval('public.alerta_stock_id_alerta_seq', 2, false);


--
-- Name: area_bodega_id_area_seq; Type: SEQUENCE SET; Schema: public; Owner: regalito_admin
--

SELECT pg_catalog.setval('public.area_bodega_id_area_seq', 4, true);


--
-- Name: bitacora_auditoria_id_bitacora_seq; Type: SEQUENCE SET; Schema: public; Owner: regalito_admin
--

SELECT pg_catalog.setval('public.bitacora_auditoria_id_bitacora_seq', 54, true);


--
-- Name: caja_id_caja_seq; Type: SEQUENCE SET; Schema: public; Owner: regalito_admin
--

SELECT pg_catalog.setval('public.caja_id_caja_seq', 2, false);


--
-- Name: categoria_id_categoria_seq; Type: SEQUENCE SET; Schema: public; Owner: regalito_admin
--

SELECT pg_catalog.setval('public.categoria_id_categoria_seq', 5, false);


--
-- Name: cierre_caja_ciegas_id_cierre_seq; Type: SEQUENCE SET; Schema: public; Owner: regalito_admin
--

SELECT pg_catalog.setval('public.cierre_caja_ciegas_id_cierre_seq', 1, false);


--
-- Name: cliente_contacto_id_contacto_seq; Type: SEQUENCE SET; Schema: public; Owner: regalito_admin
--

SELECT pg_catalog.setval('public.cliente_contacto_id_contacto_seq', 11, true);


--
-- Name: cliente_id_cliente_seq; Type: SEQUENCE SET; Schema: public; Owner: regalito_admin
--

SELECT pg_catalog.setval('public.cliente_id_cliente_seq', 6, true);


--
-- Name: compra_id_compra_seq; Type: SEQUENCE SET; Schema: public; Owner: regalito_admin
--

SELECT pg_catalog.setval('public.compra_id_compra_seq', 1, false);


--
-- Name: denominacion_efectivo_id_denominacion_seq; Type: SEQUENCE SET; Schema: public; Owner: regalito_admin
--

SELECT pg_catalog.setval('public.denominacion_efectivo_id_denominacion_seq', 9, false);


--
-- Name: departamento_geografico_id_departamento_seq; Type: SEQUENCE SET; Schema: public; Owner: regalito_admin
--

SELECT pg_catalog.setval('public.departamento_geografico_id_departamento_seq', 24, true);


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

SELECT pg_catalog.setval('public.historial_precio_id_historial_seq', 2, false);


--
-- Name: intento_login_id_intento_seq; Type: SEQUENCE SET; Schema: public; Owner: regalito_admin
--

SELECT pg_catalog.setval('public.intento_login_id_intento_seq', 1, false);


--
-- Name: inventario_sucursal_id_inventario_seq; Type: SEQUENCE SET; Schema: public; Owner: regalito_admin
--

SELECT pg_catalog.setval('public.inventario_sucursal_id_inventario_seq', 5, false);


--
-- Name: merma_id_merma_seq; Type: SEQUENCE SET; Schema: public; Owner: regalito_admin
--

SELECT pg_catalog.setval('public.merma_id_merma_seq', 1, false);


--
-- Name: metodo_pago_id_metodo_pago_seq; Type: SEQUENCE SET; Schema: public; Owner: regalito_admin
--

SELECT pg_catalog.setval('public.metodo_pago_id_metodo_pago_seq', 3, false);


--
-- Name: motivo_merma_id_motivo_seq; Type: SEQUENCE SET; Schema: public; Owner: regalito_admin
--

SELECT pg_catalog.setval('public.motivo_merma_id_motivo_seq', 4, false);


--
-- Name: movimiento_caja_id_movimiento_seq; Type: SEQUENCE SET; Schema: public; Owner: regalito_admin
--

SELECT pg_catalog.setval('public.movimiento_caja_id_movimiento_seq', 1, false);


--
-- Name: municipio_id_municipio_seq; Type: SEQUENCE SET; Schema: public; Owner: regalito_admin
--

SELECT pg_catalog.setval('public.municipio_id_municipio_seq', 341, true);


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

SELECT pg_catalog.setval('public.parametro_sistema_id_parametro_seq', 5, false);


--
-- Name: permiso_id_permiso_seq; Type: SEQUENCE SET; Schema: public; Owner: regalito_admin
--

SELECT pg_catalog.setval('public.permiso_id_permiso_seq', 12, true);


--
-- Name: producto_id_producto_seq; Type: SEQUENCE SET; Schema: public; Owner: regalito_admin
--

SELECT pg_catalog.setval('public.producto_id_producto_seq', 4, false);


--
-- Name: proveedor_id_proveedor_seq; Type: SEQUENCE SET; Schema: public; Owner: regalito_admin
--

SELECT pg_catalog.setval('public.proveedor_id_proveedor_seq', 4, false);


--
-- Name: rol_id_rol_seq; Type: SEQUENCE SET; Schema: public; Owner: regalito_admin
--

SELECT pg_catalog.setval('public.rol_id_rol_seq', 4, true);


--
-- Name: sesion_usuario_id_sesion_seq; Type: SEQUENCE SET; Schema: public; Owner: regalito_admin
--

SELECT pg_catalog.setval('public.sesion_usuario_id_sesion_seq', 1, false);


--
-- Name: subcategoria_id_subcategoria_seq; Type: SEQUENCE SET; Schema: public; Owner: regalito_admin
--

SELECT pg_catalog.setval('public.subcategoria_id_subcategoria_seq', 11, true);


--
-- Name: sucursal_id_sucursal_seq; Type: SEQUENCE SET; Schema: public; Owner: regalito_admin
--

SELECT pg_catalog.setval('public.sucursal_id_sucursal_seq', 3, true);


--
-- Name: tipo_cliente_id_tipo_cliente_seq; Type: SEQUENCE SET; Schema: public; Owner: regalito_admin
--

SELECT pg_catalog.setval('public.tipo_cliente_id_tipo_cliente_seq', 5, true);


--
-- Name: tipo_movimiento_caja_id_tipo_movimiento_seq; Type: SEQUENCE SET; Schema: public; Owner: regalito_admin
--

SELECT pg_catalog.setval('public.tipo_movimiento_caja_id_tipo_movimiento_seq', 4, false);


--
-- Name: traslado_inventario_id_traslado_seq; Type: SEQUENCE SET; Schema: public; Owner: regalito_admin
--

SELECT pg_catalog.setval('public.traslado_inventario_id_traslado_seq', 1, false);


--
-- Name: turno_caja_id_turno_seq; Type: SEQUENCE SET; Schema: public; Owner: regalito_admin
--

SELECT pg_catalog.setval('public.turno_caja_id_turno_seq', 1, true);


--
-- Name: unidad_medida_id_unidad_seq; Type: SEQUENCE SET; Schema: public; Owner: regalito_admin
--

SELECT pg_catalog.setval('public.unidad_medida_id_unidad_seq', 6, true);


--
-- Name: usuario_id_usuario_seq; Type: SEQUENCE SET; Schema: public; Owner: regalito_admin
--

SELECT pg_catalog.setval('public.usuario_id_usuario_seq', 4, false);


--
-- Name: variante_producto_id_variante_seq; Type: SEQUENCE SET; Schema: public; Owner: regalito_admin
--

SELECT pg_catalog.setval('public.variante_producto_id_variante_seq', 5, false);


--
-- Name: venta_id_venta_seq; Type: SEQUENCE SET; Schema: public; Owner: regalito_admin
--

SELECT pg_catalog.setval('public.venta_id_venta_seq', 1, false);


--
-- Name: visita_modulo_evaluacion_id_modulo_eval_seq; Type: SEQUENCE SET; Schema: public; Owner: regalito_admin
--

SELECT pg_catalog.setval('public.visita_modulo_evaluacion_id_modulo_eval_seq', 1, false);


--
-- Name: visita_seguimiento_id_visita_seq; Type: SEQUENCE SET; Schema: public; Owner: regalito_admin
--

SELECT pg_catalog.setval('public.visita_seguimiento_id_visita_seq', 1, false);


--
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: regalito_admin
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


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
-- Name: intento_login intento_login_username_key; Type: CONSTRAINT; Schema: public; Owner: regalito_admin
--

ALTER TABLE ONLY public.intento_login
    ADD CONSTRAINT intento_login_username_key UNIQUE (username);


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
-- Name: municipio uq_municipio_depto_nombre; Type: CONSTRAINT; Schema: public; Owner: regalito_admin
--

ALTER TABLE ONLY public.municipio
    ADD CONSTRAINT uq_municipio_depto_nombre UNIQUE (id_departamento, nombre);


--
-- Name: subcategoria uq_subcategoria_cat_nombre; Type: CONSTRAINT; Schema: public; Owner: regalito_admin
--

ALTER TABLE ONLY public.subcategoria
    ADD CONSTRAINT uq_subcategoria_cat_nombre UNIQUE (id_categoria, nombre);


--
-- Name: visita_modulo_evaluacion uq_visita_modulo; Type: CONSTRAINT; Schema: public; Owner: regalito_admin
--

ALTER TABLE ONLY public.visita_modulo_evaluacion
    ADD CONSTRAINT uq_visita_modulo UNIQUE (id_visita, nombre_modulo);


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
-- Name: visita_modulo_evaluacion visita_modulo_evaluacion_pkey; Type: CONSTRAINT; Schema: public; Owner: regalito_admin
--

ALTER TABLE ONLY public.visita_modulo_evaluacion
    ADD CONSTRAINT visita_modulo_evaluacion_pkey PRIMARY KEY (id_modulo_eval);


--
-- Name: visita_seguimiento visita_seguimiento_pkey; Type: CONSTRAINT; Schema: public; Owner: regalito_admin
--

ALTER TABLE ONLY public.visita_seguimiento
    ADD CONSTRAINT visita_seguimiento_pkey PRIMARY KEY (id_visita);


--
-- Name: idx_alerta_stock_id_inventario; Type: INDEX; Schema: public; Owner: regalito_admin
--

CREATE INDEX idx_alerta_stock_id_inventario ON public.alerta_stock USING btree (id_inventario);


--
-- Name: idx_area_bodega_id_sucursal; Type: INDEX; Schema: public; Owner: regalito_admin
--

CREATE INDEX idx_area_bodega_id_sucursal ON public.area_bodega USING btree (id_sucursal);


--
-- Name: idx_bitacora_auditoria_id_usuario; Type: INDEX; Schema: public; Owner: regalito_admin
--

CREATE INDEX idx_bitacora_auditoria_id_usuario ON public.bitacora_auditoria USING btree (id_usuario);


--
-- Name: idx_caja_id_sucursal; Type: INDEX; Schema: public; Owner: regalito_admin
--

CREATE INDEX idx_caja_id_sucursal ON public.caja USING btree (id_sucursal);


--
-- Name: idx_cierre_caja_ciegas_id_turno; Type: INDEX; Schema: public; Owner: regalito_admin
--

CREATE INDEX idx_cierre_caja_ciegas_id_turno ON public.cierre_caja_ciegas USING btree (id_turno);


--
-- Name: idx_cierre_ciegas_cajero; Type: INDEX; Schema: public; Owner: regalito_admin
--

CREATE INDEX idx_cierre_ciegas_cajero ON public.cierre_caja_ciegas USING btree (id_usuario_cajero);


--
-- Name: idx_cierre_ciegas_supervisor; Type: INDEX; Schema: public; Owner: regalito_admin
--

CREATE INDEX idx_cierre_ciegas_supervisor ON public.cierre_caja_ciegas USING btree (id_usuario_supervisor);


--
-- Name: idx_cliente_contacto_id_cliente; Type: INDEX; Schema: public; Owner: regalito_admin
--

CREATE INDEX idx_cliente_contacto_id_cliente ON public.cliente_contacto USING btree (id_cliente);


--
-- Name: idx_cliente_id_municipio; Type: INDEX; Schema: public; Owner: regalito_admin
--

CREATE INDEX idx_cliente_id_municipio ON public.cliente USING btree (id_municipio);


--
-- Name: idx_cliente_id_tipo_cliente; Type: INDEX; Schema: public; Owner: regalito_admin
--

CREATE INDEX idx_cliente_id_tipo_cliente ON public.cliente USING btree (id_tipo_cliente);


--
-- Name: idx_compra_id_orden; Type: INDEX; Schema: public; Owner: regalito_admin
--

CREATE INDEX idx_compra_id_orden ON public.compra USING btree (id_orden);


--
-- Name: idx_compra_id_proveedor; Type: INDEX; Schema: public; Owner: regalito_admin
--

CREATE INDEX idx_compra_id_proveedor ON public.compra USING btree (id_proveedor);


--
-- Name: idx_compra_id_usuario; Type: INDEX; Schema: public; Owner: regalito_admin
--

CREATE INDEX idx_compra_id_usuario ON public.compra USING btree (id_usuario);


--
-- Name: idx_detalle_arqueo_id_cierre; Type: INDEX; Schema: public; Owner: regalito_admin
--

CREATE INDEX idx_detalle_arqueo_id_cierre ON public.detalle_arqueo_efectivo USING btree (id_cierre);


--
-- Name: idx_detalle_arqueo_id_denominacion; Type: INDEX; Schema: public; Owner: regalito_admin
--

CREATE INDEX idx_detalle_arqueo_id_denominacion ON public.detalle_arqueo_efectivo USING btree (id_denominacion);


--
-- Name: idx_detalle_compra_id_compra; Type: INDEX; Schema: public; Owner: regalito_admin
--

CREATE INDEX idx_detalle_compra_id_compra ON public.detalle_compra USING btree (id_compra);


--
-- Name: idx_detalle_compra_id_variante; Type: INDEX; Schema: public; Owner: regalito_admin
--

CREATE INDEX idx_detalle_compra_id_variante ON public.detalle_compra USING btree (id_variante);


--
-- Name: idx_detalle_merma_id_merma; Type: INDEX; Schema: public; Owner: regalito_admin
--

CREATE INDEX idx_detalle_merma_id_merma ON public.detalle_merma USING btree (id_merma);


--
-- Name: idx_detalle_merma_id_motivo; Type: INDEX; Schema: public; Owner: regalito_admin
--

CREATE INDEX idx_detalle_merma_id_motivo ON public.detalle_merma USING btree (id_motivo);


--
-- Name: idx_detalle_merma_id_variante; Type: INDEX; Schema: public; Owner: regalito_admin
--

CREATE INDEX idx_detalle_merma_id_variante ON public.detalle_merma USING btree (id_variante);


--
-- Name: idx_detalle_orden_compra_id_orden; Type: INDEX; Schema: public; Owner: regalito_admin
--

CREATE INDEX idx_detalle_orden_compra_id_orden ON public.detalle_orden_compra USING btree (id_orden);


--
-- Name: idx_detalle_orden_compra_id_variante; Type: INDEX; Schema: public; Owner: regalito_admin
--

CREATE INDEX idx_detalle_orden_compra_id_variante ON public.detalle_orden_compra USING btree (id_variante);


--
-- Name: idx_detalle_venta_id_variante; Type: INDEX; Schema: public; Owner: regalito_admin
--

CREATE INDEX idx_detalle_venta_id_variante ON public.detalle_venta USING btree (id_variante);


--
-- Name: idx_detalle_venta_id_venta; Type: INDEX; Schema: public; Owner: regalito_admin
--

CREATE INDEX idx_detalle_venta_id_venta ON public.detalle_venta USING btree (id_venta);


--
-- Name: idx_factura_fel_id_venta; Type: INDEX; Schema: public; Owner: regalito_admin
--

CREATE INDEX idx_factura_fel_id_venta ON public.factura_fel USING btree (id_venta);


--
-- Name: idx_historial_precio_id_usuario; Type: INDEX; Schema: public; Owner: regalito_admin
--

CREATE INDEX idx_historial_precio_id_usuario ON public.historial_precio USING btree (id_usuario);


--
-- Name: idx_historial_precio_id_variante; Type: INDEX; Schema: public; Owner: regalito_admin
--

CREATE INDEX idx_historial_precio_id_variante ON public.historial_precio USING btree (id_variante);


--
-- Name: idx_inventario_sucursal_id_area; Type: INDEX; Schema: public; Owner: regalito_admin
--

CREATE INDEX idx_inventario_sucursal_id_area ON public.inventario_sucursal USING btree (id_area);


--
-- Name: idx_inventario_sucursal_id_sucursal; Type: INDEX; Schema: public; Owner: regalito_admin
--

CREATE INDEX idx_inventario_sucursal_id_sucursal ON public.inventario_sucursal USING btree (id_sucursal);


--
-- Name: idx_inventario_sucursal_id_variante; Type: INDEX; Schema: public; Owner: regalito_admin
--

CREATE INDEX idx_inventario_sucursal_id_variante ON public.inventario_sucursal USING btree (id_variante);


--
-- Name: idx_merma_id_sucursal; Type: INDEX; Schema: public; Owner: regalito_admin
--

CREATE INDEX idx_merma_id_sucursal ON public.merma USING btree (id_sucursal);


--
-- Name: idx_merma_id_usuario; Type: INDEX; Schema: public; Owner: regalito_admin
--

CREATE INDEX idx_merma_id_usuario ON public.merma USING btree (id_usuario);


--
-- Name: idx_movimiento_caja_id_tipo_movimiento; Type: INDEX; Schema: public; Owner: regalito_admin
--

CREATE INDEX idx_movimiento_caja_id_tipo_movimiento ON public.movimiento_caja USING btree (id_tipo_movimiento);


--
-- Name: idx_movimiento_caja_id_turno; Type: INDEX; Schema: public; Owner: regalito_admin
--

CREATE INDEX idx_movimiento_caja_id_turno ON public.movimiento_caja USING btree (id_turno);


--
-- Name: idx_movimiento_caja_id_usuario; Type: INDEX; Schema: public; Owner: regalito_admin
--

CREATE INDEX idx_movimiento_caja_id_usuario ON public.movimiento_caja USING btree (id_usuario);


--
-- Name: idx_municipio_id_departamento; Type: INDEX; Schema: public; Owner: regalito_admin
--

CREATE INDEX idx_municipio_id_departamento ON public.municipio USING btree (id_departamento);


--
-- Name: idx_orden_compra_id_proveedor; Type: INDEX; Schema: public; Owner: regalito_admin
--

CREATE INDEX idx_orden_compra_id_proveedor ON public.orden_compra USING btree (id_proveedor);


--
-- Name: idx_orden_compra_id_usuario; Type: INDEX; Schema: public; Owner: regalito_admin
--

CREATE INDEX idx_orden_compra_id_usuario ON public.orden_compra USING btree (id_usuario);


--
-- Name: idx_pago_venta_id_metodo_pago; Type: INDEX; Schema: public; Owner: regalito_admin
--

CREATE INDEX idx_pago_venta_id_metodo_pago ON public.pago_venta USING btree (id_metodo_pago);


--
-- Name: idx_pago_venta_id_venta; Type: INDEX; Schema: public; Owner: regalito_admin
--

CREATE INDEX idx_pago_venta_id_venta ON public.pago_venta USING btree (id_venta);


--
-- Name: idx_producto_id_subcategoria; Type: INDEX; Schema: public; Owner: regalito_admin
--

CREATE INDEX idx_producto_id_subcategoria ON public.producto USING btree (id_subcategoria);


--
-- Name: idx_producto_id_unidad; Type: INDEX; Schema: public; Owner: regalito_admin
--

CREATE INDEX idx_producto_id_unidad ON public.producto USING btree (id_unidad);


--
-- Name: idx_sesion_usuario_id_usuario; Type: INDEX; Schema: public; Owner: regalito_admin
--

CREATE INDEX idx_sesion_usuario_id_usuario ON public.sesion_usuario USING btree (id_usuario);


--
-- Name: idx_subcategoria_id_categoria; Type: INDEX; Schema: public; Owner: regalito_admin
--

CREATE INDEX idx_subcategoria_id_categoria ON public.subcategoria USING btree (id_categoria);


--
-- Name: idx_traslado_inventario_destino; Type: INDEX; Schema: public; Owner: regalito_admin
--

CREATE INDEX idx_traslado_inventario_destino ON public.traslado_inventario USING btree (id_sucursal_destino);


--
-- Name: idx_traslado_inventario_id_variante; Type: INDEX; Schema: public; Owner: regalito_admin
--

CREATE INDEX idx_traslado_inventario_id_variante ON public.traslado_inventario USING btree (id_variante);


--
-- Name: idx_traslado_inventario_origen; Type: INDEX; Schema: public; Owner: regalito_admin
--

CREATE INDEX idx_traslado_inventario_origen ON public.traslado_inventario USING btree (id_sucursal_origen);


--
-- Name: idx_turno_caja_id_caja; Type: INDEX; Schema: public; Owner: regalito_admin
--

CREATE INDEX idx_turno_caja_id_caja ON public.turno_caja USING btree (id_caja);


--
-- Name: idx_turno_caja_id_usuario; Type: INDEX; Schema: public; Owner: regalito_admin
--

CREATE INDEX idx_turno_caja_id_usuario ON public.turno_caja USING btree (id_usuario);


--
-- Name: idx_usuario_id_rol; Type: INDEX; Schema: public; Owner: regalito_admin
--

CREATE INDEX idx_usuario_id_rol ON public.usuario USING btree (id_rol);


--
-- Name: idx_variante_producto_id_producto; Type: INDEX; Schema: public; Owner: regalito_admin
--

CREATE INDEX idx_variante_producto_id_producto ON public.variante_producto USING btree (id_producto);


--
-- Name: idx_venta_id_cliente; Type: INDEX; Schema: public; Owner: regalito_admin
--

CREATE INDEX idx_venta_id_cliente ON public.venta USING btree (id_cliente);


--
-- Name: idx_venta_id_turno; Type: INDEX; Schema: public; Owner: regalito_admin
--

CREATE INDEX idx_venta_id_turno ON public.venta USING btree (id_turno);


--
-- Name: idx_venta_id_usuario; Type: INDEX; Schema: public; Owner: regalito_admin
--

CREATE INDEX idx_venta_id_usuario ON public.venta USING btree (id_usuario);


--
-- Name: uq_cliente_nit_no_cf; Type: INDEX; Schema: public; Owner: regalito_admin
--

CREATE UNIQUE INDEX uq_cliente_nit_no_cf ON public.cliente USING btree (nit) WHERE ((nit)::text <> 'CF'::text);


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
-- Name: traslado_inventario traslado_inventario_id_usuario_envia_fkey; Type: FK CONSTRAINT; Schema: public; Owner: regalito_admin
--

ALTER TABLE ONLY public.traslado_inventario
    ADD CONSTRAINT traslado_inventario_id_usuario_envia_fkey FOREIGN KEY (id_usuario_envia) REFERENCES public.usuario(id_usuario);


--
-- Name: traslado_inventario traslado_inventario_id_usuario_recibe_fkey; Type: FK CONSTRAINT; Schema: public; Owner: regalito_admin
--

ALTER TABLE ONLY public.traslado_inventario
    ADD CONSTRAINT traslado_inventario_id_usuario_recibe_fkey FOREIGN KEY (id_usuario_recibe) REFERENCES public.usuario(id_usuario);


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
-- Name: visita_modulo_evaluacion visita_modulo_evaluacion_id_visita_fkey; Type: FK CONSTRAINT; Schema: public; Owner: regalito_admin
--

ALTER TABLE ONLY public.visita_modulo_evaluacion
    ADD CONSTRAINT visita_modulo_evaluacion_id_visita_fkey FOREIGN KEY (id_visita) REFERENCES public.visita_seguimiento(id_visita) ON DELETE CASCADE;


--
-- Name: visita_seguimiento visita_seguimiento_id_cliente_fkey; Type: FK CONSTRAINT; Schema: public; Owner: regalito_admin
--

ALTER TABLE ONLY public.visita_seguimiento
    ADD CONSTRAINT visita_seguimiento_id_cliente_fkey FOREIGN KEY (id_cliente) REFERENCES public.cliente(id_cliente);


--
-- Name: visita_seguimiento visita_seguimiento_id_usuario_fkey; Type: FK CONSTRAINT; Schema: public; Owner: regalito_admin
--

ALTER TABLE ONLY public.visita_seguimiento
    ADD CONSTRAINT visita_seguimiento_id_usuario_fkey FOREIGN KEY (id_usuario) REFERENCES public.usuario(id_usuario);


--
-- PostgreSQL database dump complete
--

\unrestrict t8CsEU5Y9V4BGa9mAQv6wcUtsxzKbiwgImXORsZY5F4qZslM3Hu74ijtCM9aHyB

