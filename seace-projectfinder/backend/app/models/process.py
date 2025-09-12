from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, Numeric, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid

Base = declarative_base()


class Process(Base):
    __tablename__ = "procesos"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    id_proceso = Column(String(255), unique=True, nullable=False, index=True)
    url_proceso = Column(Text, nullable=True)
    numero_convocatoria = Column(String(255), nullable=True)
    entidad_nombre = Column(String(500), nullable=True)
    entidad_ruc = Column(String(11), nullable=True)
    objeto_contratacion = Column(Text, nullable=True)
    tipo_proceso = Column(String(100), nullable=True)
    estado_proceso = Column(String(100), nullable=True)
    fecha_publicacion = Column(DateTime, nullable=True)
    fecha_limite_presentacion = Column(DateTime, nullable=True)
    monto_referencial = Column(Numeric(15, 2), nullable=True)
    moneda = Column(String(10), nullable=True)
    rubro = Column(String(200), nullable=True)
    departamento = Column(String(100), nullable=True)
    provincia = Column(String(100), nullable=True)
    distrito = Column(String(100), nullable=True)
    requiere_visita_previa = Column(Boolean, default=False)
    datos_ocds = Column(Text, nullable=True)  # JSONB en PostgreSQL
    fecha_extraccion = Column(DateTime, default=datetime.utcnow)
    fecha_actualizacion = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    procesado_nlp = Column(Boolean, default=False)
    complejidad_estimada = Column(String(50), nullable=True)
    categoria_proyecto = Column(String(100), nullable=True)
    
    def __repr__(self):
        return f"<Process {self.id_proceso}: {self.objeto_contratacion[:50] if self.objeto_contratacion else 'N/A'}...>"
