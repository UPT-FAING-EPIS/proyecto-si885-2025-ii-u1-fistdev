from sqlalchemy import Column, String, Text, DateTime, Boolean, Integer, ARRAY, Numeric
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey
import uuid

from app.core.database import Base


class Proceso(Base):
    __tablename__ = "procesos"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    id_proceso = Column(String(255), unique=True, nullable=False, index=True)
    url_proceso = Column(Text)
    numero_convocatoria = Column(String(255))
    entidad_nombre = Column(String(500))
    entidad_ruc = Column(String(11))
    objeto_contratacion = Column(Text)
    tipo_proceso = Column(String(100))
    estado_proceso = Column(String(100), index=True)
    fecha_publicacion = Column(DateTime, index=True)
    fecha_limite_presentacion = Column(DateTime)
    monto_referencial = Column(Numeric(15, 2), index=True)
    moneda = Column(String(10))
    rubro = Column(String(200), index=True)
    departamento = Column(String(100))
    provincia = Column(String(100))
    distrito = Column(String(100))
    requiere_visita_previa = Column(Boolean, default=False)
    datos_ocds = Column(JSONB)
    fecha_extraccion = Column(DateTime, default=func.now())
    fecha_actualizacion = Column(DateTime, default=func.now(), onupdate=func.now())
    procesado_nlp = Column(Boolean, default=False)
    complejidad_estimada = Column(String(50))
    categoria_proyecto = Column(String(100))

    # Relaciones
    embeddings = relationship("ProcesoEmbedding", back_populates="proceso", cascade="all, delete-orphan")
    anexos = relationship("Anexo", back_populates="proceso", cascade="all, delete-orphan")
    recomendaciones = relationship("Recomendacion", back_populates="proceso", cascade="all, delete-orphan")


class ProcesoEmbedding(Base):
    __tablename__ = "proceso_embeddings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    proceso_id = Column(UUID(as_uuid=True), ForeignKey("procesos.id", ondelete="CASCADE"), nullable=False, index=True)
    content_type = Column(String(50))  # 'objeto', 'descripcion', 'especificaciones'
    content_text = Column(Text)
    embedding = Column("embedding", Text)  # Almacenar como texto para compatibilidad
    created_at = Column(DateTime, default=func.now())

    # Relaciones
    proceso = relationship("Proceso", back_populates="embeddings")


class Anexo(Base):
    __tablename__ = "anexos"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    proceso_id = Column(UUID(as_uuid=True), ForeignKey("procesos.id", ondelete="CASCADE"), nullable=False, index=True)
    nombre_archivo = Column(String(255))
    url_descarga = Column(Text)
    tipo_documento = Column(String(100))
    tamaño_kb = Column(Integer)
    fecha_subida = Column(DateTime)
    procesado = Column(Boolean, default=False)
    contenido_extraido = Column(Text)
    created_at = Column(DateTime, default=func.now())

    # Relaciones
    proceso = relationship("Proceso", back_populates="anexos")


class Recomendacion(Base):
    __tablename__ = "recomendaciones"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    proceso_id = Column(UUID(as_uuid=True), ForeignKey("procesos.id", ondelete="CASCADE"), nullable=False, index=True)
    tipo_recomendacion = Column(String(100))  # 'mvp', 'sprint1', 'stack_tech', 'estimacion'
    titulo = Column(String(255))
    descripcion = Column(Text)
    datos_estructurados = Column(JSONB)
    confianza_score = Column(Numeric(3, 2))  # 0.00 a 1.00
    generated_by = Column(String(50))  # 'gemini-2.5-flash', etc.
    created_at = Column(DateTime, default=func.now())

    # Relaciones
    proceso = relationship("Proceso", back_populates="recomendaciones")


class ChatbotLog(Base):
    __tablename__ = "chatbot_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(String(255))
    user_query = Column(Text)
    ai_response = Column(Text)
    relevant_processes = Column(ARRAY(UUID(as_uuid=True)))  # Array de IDs de procesos relacionados
    response_time_ms = Column(Integer)
    model_used = Column(String(50))
    created_at = Column(DateTime, default=func.now())


class Configuracion(Base):
    __tablename__ = "configuracion"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    clave = Column(String(100), unique=True, nullable=False)
    valor = Column(Text)
    descripcion = Column(Text)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
