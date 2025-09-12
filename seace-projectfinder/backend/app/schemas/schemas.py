from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime
from decimal import Decimal
from uuid import UUID


# Esquemas para Process (coincidiendo con tabla existente)
class ProcessBase(BaseModel):
    id_proceso: str
    url_proceso: Optional[str] = None
    numero_convocatoria: Optional[str] = None
    entidad_nombre: Optional[str] = None
    entidad_ruc: Optional[str] = None
    objeto_contratacion: Optional[str] = None
    tipo_proceso: Optional[str] = None
    estado_proceso: Optional[str] = None
    fecha_publicacion: Optional[datetime] = None
    fecha_limite_presentacion: Optional[datetime] = None
    monto_referencial: Optional[Decimal] = None
    moneda: Optional[str] = None
    rubro: Optional[str] = None
    departamento: Optional[str] = None
    provincia: Optional[str] = None
    distrito: Optional[str] = None
    requiere_visita_previa: Optional[bool] = False
    complejidad_estimada: Optional[str] = None
    categoria_proyecto: Optional[str] = None


class ProcessResponse(ProcessBase):
    id: UUID
    fecha_extraccion: Optional[datetime] = None
    fecha_actualizacion: Optional[datetime] = None
    procesado_nlp: Optional[bool] = False
    
    model_config = ConfigDict(from_attributes=True)


class ProcessFilter(BaseModel):
    estado_proceso: Optional[str] = None
    tipo_proceso: Optional[str] = None
    rubro: Optional[str] = None
    departamento: Optional[str] = None
    monto_min: Optional[float] = None
    monto_max: Optional[float] = None
    search_text: Optional[str] = None


# Esquemas de paginación
class PaginatedResponse(BaseModel):
    items: List[ProcessResponse]
    total: int
    page: int
    size: int
    pages: int


# Esquemas heredados (para compatibilidad)
class ProcesoBase(BaseModel):
    id_proceso: str
    url_proceso: Optional[str] = None
    numero_convocatoria: Optional[str] = None
    entidad_nombre: Optional[str] = None
    entidad_ruc: Optional[str] = None
    objeto_contratacion: Optional[str] = None
    tipo_proceso: Optional[str] = None
    estado_proceso: Optional[str] = None
    fecha_publicacion: Optional[datetime] = None
    fecha_limite_presentacion: Optional[datetime] = None
    monto_referencial: Optional[Decimal] = None
    moneda: Optional[str] = None
    rubro: Optional[str] = None
    departamento: Optional[str] = None
    provincia: Optional[str] = None
    distrito: Optional[str] = None
    requiere_visita_previa: Optional[bool] = False
    datos_ocds: Optional[Dict[str, Any]] = None
    complejidad_estimada: Optional[str] = None
    categoria_proyecto: Optional[str] = None


class ProcesoCreate(ProcesoBase):
    pass


class ProcesoUpdate(BaseModel):
    objeto_contratacion: Optional[str] = None
    estado_proceso: Optional[str] = None
    monto_referencial: Optional[Decimal] = None
    complejidad_estimada: Optional[str] = None
    categoria_proyecto: Optional[str] = None
    procesado_nlp: Optional[bool] = None


class ProcesoInDB(ProcesoBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    fecha_extraccion: datetime
    fecha_actualizacion: datetime
    procesado_nlp: bool


class Proceso(ProcesoInDB):
    pass


class AnexoBase(BaseModel):
    nombre_archivo: str
    url_descarga: Optional[str] = None
    tipo_documento: Optional[str] = None
    tamaño_kb: Optional[int] = None
    fecha_subida: Optional[datetime] = None


class AnexoCreate(AnexoBase):
    proceso_id: UUID


class AnexoInDB(AnexoBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    proceso_id: UUID
    procesado: bool
    contenido_extraido: Optional[str] = None
    created_at: datetime


class Anexo(AnexoInDB):
    pass


class RecomendacionBase(BaseModel):
    tipo_recomendacion: str
    titulo: str
    descripcion: str
    datos_estructurados: Optional[Dict[str, Any]] = None
    confianza_score: Optional[Decimal] = None
    generated_by: Optional[str] = None


class RecomendacionCreate(RecomendacionBase):
    proceso_id: UUID


class RecomendacionInDB(RecomendacionBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    proceso_id: UUID
    created_at: datetime


class Recomendacion(RecomendacionInDB):
    pass


class ChatbotQuery(BaseModel):
    query: str
    session_id: Optional[str] = None
    max_results: Optional[int] = Field(default=5, ge=1, le=20)


class ChatbotResponse(BaseModel):
    response: str
    relevant_processes: List[UUID] = []
    session_id: str
    response_time_ms: int
    model_used: str
    sources_cited: List[str] = []


class ProcesoFilter(BaseModel):
    estado_proceso: Optional[str] = None
    rubro: Optional[str] = None
    departamento: Optional[str] = None
    monto_min: Optional[Decimal] = None
    monto_max: Optional[Decimal] = None
    fecha_inicio: Optional[datetime] = None
    fecha_fin: Optional[datetime] = None
    search_text: Optional[str] = None
    procesado_nlp: Optional[bool] = None


class PaginatedResponse(BaseModel):
    items: List[Any]
    total: int
    page: int
    size: int
    pages: int


class APIError(BaseModel):
    error: str
    message: str
    status_code: int = 400
