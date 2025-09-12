from sqlalchemy import Column, String, DateTime, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

Base = declarative_base()


class Recomendacion(Base):
    __tablename__ = "recomendaciones"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    proceso_id = Column(UUID(as_uuid=True), ForeignKey("procesos.id"), nullable=False)
    tipo_recomendacion = Column(String(50), nullable=False)  # mvp, stack, presupuesto, sprint
    titulo = Column(String(200), nullable=False)
    descripcion = Column(Text, nullable=False)
    justificacion = Column(Text, nullable=True)
    
    # Metadatos
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<Recomendacion {self.tipo_recomendacion}: {self.titulo}>"
