from datetime import date, datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field

MODULOS_DEFAULT = [
    "POS/Ventas",
    "Inventario",
    "Compras",
    "Caja",
    "Usuarios",
    "Catálogos",
    "Reportes",
    "Configuración",
    "Clientes",
    "Facturación",
]

RESULTADOS_PERMITIDOS = ["Conforme", "Modificar", "Agregar"]


class ModuloEvaluacionInput(BaseModel):
    nombre_modulo: str
    resultado: Optional[str] = None  # Conforme, Modificar, Agregar
    calificacion: Optional[int] = Field(None, ge=1, le=5)
    comentario: Optional[str] = None


class ModuloEvaluacionOut(BaseModel):
    id_modulo_eval: int
    id_visita: int
    nombre_modulo: str
    resultado: Optional[str] = None
    calificacion: Optional[int] = None
    comentario: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class VisitaCreate(BaseModel):
    fecha_visita: Optional[date] = None
    lugar: Optional[str] = None
    nombre_representante: Optional[str] = None
    cargo_representante: Optional[str] = None
    calificacion_general: Optional[int] = Field(None, ge=1, le=5)
    observaciones: Optional[str] = None
    modulos: List[ModuloEvaluacionInput] = []


class VisitaUpdate(BaseModel):
    fecha_visita: Optional[date] = None
    lugar: Optional[str] = None
    nombre_representante: Optional[str] = None
    cargo_representante: Optional[str] = None
    calificacion_general: Optional[int] = Field(None, ge=1, le=5)
    observaciones: Optional[str] = None
    modulos: Optional[List[ModuloEvaluacionInput]] = None


class VisitaResumen(BaseModel):
    total_modulos: int = 10
    conformes: int = 0
    modificar: int = 0
    agregar: int = 0
    sin_evaluar: int = 0


class VisitaOut(BaseModel):
    id_visita: int
    id_usuario: int
    id_cliente: Optional[int] = None
    fecha_visita: date
    lugar: Optional[str] = None
    nombre_representante: Optional[str] = None
    cargo_representante: Optional[str] = None
    calificacion_general: Optional[int] = None
    observaciones: Optional[str] = None
    estado: str
    fecha_creacion: datetime

    evaluador_nombre: Optional[str] = None
    modulos: List[ModuloEvaluacionOut] = []
    resumen: Optional[VisitaResumen] = None

    model_config = ConfigDict(from_attributes=True)
