from sqlalchemy import Column, String, DateTime, Text, Integer, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid

Base = declarative_base()


class ChatbotLog(Base):
    __tablename__ = "chatbot_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(String(255), nullable=True, index=True)
    user_query = Column(Text, nullable=True)
    ai_response = Column(Text, nullable=True)
    response_time_ms = Column(Integer, nullable=True)
    model_used = Column(String(50), nullable=True)
    
    # Metadatos
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<ChatbotLog {self.session_id}: {self.user_query[:50]}...>"
