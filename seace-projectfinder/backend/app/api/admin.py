from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Dict, Any
from datetime import datetime
import logging

from app.core.database import get_db
from app.etl.etl_processor import ETLProcessor
from app.nlp.rag_service import RAGService
from app.core.config import settings

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/etl/sync-daily")
async def run_daily_sync(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Ejecutar sincronización diaria con OSCE"""
    
    background_tasks.add_task(execute_daily_sync_task)
    
    return {
        "message": "Sincronización diaria iniciada",
        "status": "processing",
        "timestamp": datetime.now()
    }


@router.post("/etl/sync-full")
async def run_full_sync(
    days_back: int = 365,
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(get_db)
):
    """Ejecutar sincronización completa"""
    
    if background_tasks:
        background_tasks.add_task(execute_full_sync_task, days_back)
        
        return {
            "message": f"Sincronización completa iniciada ({days_back} días)",
            "status": "processing",
            "timestamp": datetime.now()
        }
    else:
        # Ejecutar sincrónicamente (para testing)
        etl = ETLProcessor()
        stats = await etl.run_full_sync(days_back)
        return stats


@router.post("/etl/sync-ti")
async def run_ti_sync(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Ejecutar sincronización solo de procesos TI"""
    
    background_tasks.add_task(execute_ti_sync_task)
    
    return {
        "message": "Sincronización de procesos TI iniciada",
        "status": "processing",
        "timestamp": datetime.now()
    }


@router.post("/nlp/generate-embeddings")
async def generate_embeddings_batch(
    batch_size: int = 50,
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(get_db)
):
    """Generar embeddings para procesos sin procesar"""
    
    if background_tasks:
        background_tasks.add_task(execute_embeddings_task, batch_size)
        
        return {
            "message": f"Generación de embeddings iniciada (lote: {batch_size})",
            "status": "processing",
            "timestamp": datetime.now()
        }
    else:
        # Ejecutar sincrónicamente (para testing)
        rag_service = RAGService()
        stats = await rag_service.batch_generate_embeddings(batch_size)
        return stats


@router.get("/status/etl")
async def get_etl_status(db: Session = Depends(get_db)):
    """Obtener estado del proceso ETL"""
    
    try:
        from app.db.models import Configuracion, Proceso
        
        # Última sincronización
        last_sync = (
            db.query(Configuracion)
            .filter(Configuracion.clave == "last_osce_sync")
            .first()
        )
        
        # Estadísticas de procesos
        total_procesos = db.query(Proceso).count()
        procesados_nlp = db.query(Proceso).filter(Proceso.procesado_nlp == True).count()
        procesos_ti = db.query(Proceso).filter(Proceso.categoria_proyecto.isnot(None)).count()
        
        # Procesos recientes
        procesos_hoy = db.query(Proceso).filter(
            Proceso.fecha_extraccion >= datetime.now().date()
        ).count()
        
        return {
            "last_sync": last_sync.valor if last_sync else None,
            "total_procesos": total_procesos,
            "procesados_nlp": procesados_nlp,
            "procesos_ti": procesos_ti,
            "procesos_hoy": procesos_hoy,
            "porcentaje_procesado": round((procesados_nlp / total_procesos * 100), 2) if total_procesos > 0 else 0,
            "timestamp": datetime.now()
        }
        
    except Exception as e:
        logger.error(f"Error obteniendo estado ETL: {str(e)}")
        raise HTTPException(status_code=500, detail="Error obteniendo estado")


@router.get("/status/health")
async def health_check():
    """Verificación de salud del sistema"""
    
    health_status = {
        "status": "healthy",
        "timestamp": datetime.now(),
        "services": {}
    }
    
    # Verificar base de datos
    try:
        with SessionLocal() as db:
            db.execute("SELECT 1")
        health_status["services"]["database"] = "healthy"
    except Exception as e:
        health_status["services"]["database"] = "unhealthy"
        health_status["status"] = "degraded"
        logger.error(f"Database health check failed: {str(e)}")
    
    # Verificar Gemini API
    try:
        if settings.GEMINI_API_KEY:
            health_status["services"]["gemini_api"] = "configured"
        else:
            health_status["services"]["gemini_api"] = "not_configured"
    except Exception as e:
        health_status["services"]["gemini_api"] = "error"
        logger.error(f"Gemini API check failed: {str(e)}")
    
    # Verificar configuración OSCE
    try:
        if settings.OSCE_API_URL:
            health_status["services"]["osce_api"] = "configured"
        else:
            health_status["services"]["osce_api"] = "not_configured"
    except Exception as e:
        health_status["services"]["osce_api"] = "error"
    
    return health_status


@router.get("/status/system")
async def get_system_status():
    """Obtener estado general del sistema"""
    
    return {
        "application": settings.PROJECT_NAME,
        "environment": settings.ENVIRONMENT,
        "api_version": settings.API_V1_STR,
        "timestamp": datetime.now(),
        "uptime": "running",  # Simplificado
        "configuration": {
            "gemini_configured": bool(settings.GEMINI_API_KEY),
            "powerbi_configured": bool(settings.POWERBI_IFRAME_URL),
            "osce_api_configured": bool(settings.OSCE_API_URL),
            "rate_limits": {
                "gemini_per_minute": settings.GEMINI_RATE_LIMIT_PER_MINUTE,
                "osce_per_minute": settings.OSCE_RATE_LIMIT_PER_MINUTE
            }
        }
    }


# Tareas en background
async def execute_daily_sync_task():
    """Ejecutar sincronización diaria en background"""
    try:
        etl = ETLProcessor()
        stats = await etl.run_daily_sync()
        logger.info(f"Sincronización diaria completada: {stats}")
    except Exception as e:
        logger.error(f"Error en sincronización diaria: {str(e)}")


async def execute_full_sync_task(days_back: int):
    """Ejecutar sincronización completa en background"""
    try:
        etl = ETLProcessor()
        stats = await etl.run_full_sync(days_back)
        logger.info(f"Sincronización completa completada: {stats}")
    except Exception as e:
        logger.error(f"Error en sincronización completa: {str(e)}")


async def execute_ti_sync_task():
    """Ejecutar sincronización TI en background"""
    try:
        etl = ETLProcessor()
        stats = await etl.sync_ti_processes_only()
        logger.info(f"Sincronización TI completada: {stats}")
    except Exception as e:
        logger.error(f"Error en sincronización TI: {str(e)}")


async def execute_embeddings_task(batch_size: int):
    """Ejecutar generación de embeddings en background"""
    try:
        rag_service = RAGService()
        stats = await rag_service.batch_generate_embeddings(batch_size)
        logger.info(f"Generación de embeddings completada: {stats}")
    except Exception as e:
        logger.error(f"Error en generación de embeddings: {str(e)}")


# Importar SessionLocal aquí para evitar imports circulares
from app.core.database import SessionLocal
