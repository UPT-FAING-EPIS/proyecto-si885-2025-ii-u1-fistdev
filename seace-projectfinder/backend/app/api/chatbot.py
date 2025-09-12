from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Dict, Any
import uuid
import asyncio
from datetime import datetime
import logging

from app.core.database import get_db
from app.schemas.schemas import ChatbotQuery, ChatbotResponse
from app.nlp.rag_service import RAGService
from app.models.chatbot_log import ChatbotLog
from app.core.exceptions import NLPException

router = APIRouter()
rag_service = RAGService()
logger = logging.getLogger(__name__)


@router.post("/query", response_model=ChatbotResponse)
async def chatbot_query(
    query_data: ChatbotQuery,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Procesar consulta del chatbot usando RAG"""
    
    try:
        # Generar session_id si no se proporciona
        session_id = query_data.session_id or str(uuid.uuid4())
        
        # Validar que la consulta esté relacionada con SEACE/contratación pública
        if not _is_valid_seace_query(query_data.query):
            return ChatbotResponse(
                response="Lo siento, solo puedo responder preguntas relacionadas con contratación pública peruana y oportunidades de TI en el SEACE. Por favor, reformula tu pregunta sobre estos temas.",
                relevant_processes=[],
                session_id=session_id,
                response_time_ms=0,
                model_used="filter",
                sources_cited=[]
            )
        
        # Generar respuesta usando RAG
        start_time = asyncio.get_event_loop().time()
        
        rag_response = await rag_service.generate_rag_response(
            query_data.query,
            session_id
        )
        
        end_time = asyncio.get_event_loop().time()
        response_time_ms = int((end_time - start_time) * 1000)
        
        # Preparar respuesta
        response = ChatbotResponse(
            response=rag_response.get("respuesta", "No pude generar una respuesta adecuada."),
            relevant_processes=[
                uuid.UUID(pid) for pid in rag_response.get("relevant_process_ids", [])
            ],
            session_id=session_id,
            response_time_ms=response_time_ms,
            model_used=rag_response.get("modelo_usado", "gemini-2.5-flash"),
            sources_cited=rag_response.get("fuentes_citadas", [])
        )
        
        # Programar logging en background
        background_tasks.add_task(
            log_chatbot_interaction,
            db,
            query_data.query,
            response,
            rag_response.get("relevant_process_ids", [])
        )
        
        return response
        
    except NLPException as e:
        logger.error(f"Error NLP en chatbot: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error procesando consulta: {str(e)}")
    except Exception as e:
        logger.error(f"Error inesperado en chatbot: {str(e)}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")


@router.get("/suggestions")
async def get_query_suggestions():
    """Obtener sugerencias de consultas para el chatbot"""
    
    suggestions = [
        "¿Qué procesos de desarrollo de software están disponibles?",
        "Muéstrame las últimas convocatorias de tecnología",
        "¿Cuáles son los proyectos TI con mayor presupuesto?",
        "Dame recomendaciones para un proyecto de sistema web",
        "¿Qué entidades públicas más contratan servicios de TI?",
        "Busca procesos de aplicaciones móviles",
        "¿Cuál es el stack tecnológico más común en el sector público?",
        "Proyectos de inteligencia artificial en el estado peruano",
        "¿Cómo puedo participar en licitaciones de software?",
        "Tendencias en contratación pública de tecnología"
    ]
    
    return {
        "suggestions": suggestions,
        "categories": [
            {
                "name": "Búsqueda de Procesos",
                "queries": [
                    "¿Qué procesos de desarrollo de software están disponibles?",
                    "Muéstrame las últimas convocatorias de tecnología",
                    "Busca procesos de aplicaciones móviles"
                ]
            },
            {
                "name": "Análisis y Tendencias",
                "queries": [
                    "¿Cuáles son los proyectos TI con mayor presupuesto?",
                    "¿Qué entidades públicas más contratan servicios de TI?",
                    "Tendencias en contratación pública de tecnología"
                ]
            },
            {
                "name": "Recomendaciones de Proyectos",
                "queries": [
                    "Dame recomendaciones para un proyecto de sistema web",
                    "¿Cuál es el stack tecnológico más común en el sector público?",
                    "Proyectos de inteligencia artificial en el estado peruano"
                ]
            }
        ]
    }


@router.get("/session/{session_id}/history")
async def get_session_history(
    session_id: str,
    db: Session = Depends(get_db)
):
    """Obtener historial de una sesión de chat"""
    
    try:
        logs = (
            db.query(ChatbotLog)
            .filter(ChatbotLog.session_id == session_id)
            .order_by(ChatbotLog.created_at)
            .all()
        )
        
        return {
            "session_id": session_id,
            "message_count": len(logs),
            "messages": [
                {
                    "timestamp": log.created_at,
                    "user_query": log.user_query,
                    "ai_response": log.ai_response,
                    "response_time_ms": log.response_time_ms,
                    "model_used": log.model_used
                }
                for log in logs
            ]
        }
        
    except Exception as e:
        logger.error(f"Error obteniendo historial de sesión: {str(e)}")
        raise HTTPException(status_code=500, detail="Error obteniendo historial")


@router.get("/stats/usage")
async def get_chatbot_stats(db: Session = Depends(get_db)):
    """Obtener estadísticas de uso del chatbot"""
    
    try:
        # Estadísticas básicas
        total_queries = db.query(ChatbotLog).count()
        unique_sessions = db.query(ChatbotLog.session_id).distinct().count()
        
        # Tiempo promedio de respuesta
        avg_response_time = db.query(
            func.avg(ChatbotLog.response_time_ms)
        ).scalar() or 0
        
        # Consultas más frecuentes (por palabras clave)
        recent_queries = (
            db.query(ChatbotLog.user_query)
            .order_by(ChatbotLog.created_at.desc())
            .limit(100)
            .all()
        )
        
        # Análisis simple de palabras clave
        keyword_counts = {}
        common_keywords = [
            "software", "desarrollo", "sistema", "web", "aplicacion", "movil",
            "tecnologia", "digital", "plataforma", "api", "base de datos"
        ]
        
        for query_tuple in recent_queries:
            query = query_tuple[0].lower()
            for keyword in common_keywords:
                if keyword in query:
                    keyword_counts[keyword] = keyword_counts.get(keyword, 0) + 1
        
        return {
            "total_queries": total_queries,
            "unique_sessions": unique_sessions,
            "avg_response_time_ms": round(avg_response_time, 2),
            "popular_keywords": sorted(
                keyword_counts.items(), 
                key=lambda x: x[1], 
                reverse=True
            )[:10]
        }
        
    except Exception as e:
        logger.error(f"Error obteniendo estadísticas del chatbot: {str(e)}")
        raise HTTPException(status_code=500, detail="Error obteniendo estadísticas")


def _is_valid_seace_query(query: str) -> bool:
    """Validar que la consulta esté relacionada con SEACE/contratación pública"""
    
    # Palabras clave relacionadas con contratación pública y TI
    seace_keywords = [
        "seace", "osce", "contratacion", "licitacion", "convocatoria",
        "proceso", "entidad", "publica", "estado", "gobierno",
        "software", "sistema", "desarrollo", "tecnologia", "ti",
        "aplicacion", "web", "digital", "plataforma", "proyecto"
    ]
    
    query_lower = query.lower()
    
    # Si contiene alguna palabra clave relacionada, es válida
    for keyword in seace_keywords:
        if keyword in query_lower:
            return True
    
    # También permitir preguntas generales sobre procesos
    general_keywords = [
        "como", "que", "cual", "donde", "cuando", "quien",
        "mostrar", "buscar", "encontrar", "dame", "necesito"
    ]
    
    has_general = any(gk in query_lower for gk in general_keywords)
    
    # Si tiene estructura de pregunta pero no palabras clave específicas,
    # podemos ser más permisivos
    if has_general and len(query.strip()) > 10:
        return True
    
    return False


async def log_chatbot_interaction(
    db: Session,
    user_query: str,
    response: ChatbotResponse,
    relevant_process_ids: list
):
    """Registrar interacción del chatbot en la base de datos"""
    
    try:
        log_entry = ChatbotLog(
            session_id=response.session_id,
            user_query=user_query,
            ai_response=response.response,
            response_time_ms=response.response_time_ms,
            model_used=response.model_used
        )
        
        db.add(log_entry)
        db.commit()
        
    except Exception as e:
        logger.error(f"Error registrando interacción del chatbot: {str(e)}")
        # No re-raise, ya que es una tarea de background
