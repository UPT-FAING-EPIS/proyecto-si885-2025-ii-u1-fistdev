from fastapi import APIRouter, BackgroundTasks, HTTPException, Depends
from typing import Dict, Any
import asyncio
import logging
from app.etl.etl_processor import ETLProcessor
from app.core.database import get_db
from sqlalchemy.orm import Session

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/run", response_model=Dict[str, Any])
async def run_etl(background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """
    Ejecutar ETL para extraer datos del SEACE
    """
    try:
        # Ejecutar ETL en background
        background_tasks.add_task(execute_etl, db)
        
        return {
            "message": "ETL iniciado exitosamente",
            "status": "running"
        }
    except Exception as e:
        logger.error(f"Error al iniciar ETL: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error al iniciar ETL: {str(e)}")

async def execute_etl(db: Session):
    """
    Ejecutar el proceso ETL
    """
    try:
        logger.info("Iniciando proceso ETL")
        processor = ETLProcessor()
        
        # Ejecutar sincronización diaria
        result = await processor.run_daily_sync()
        
        logger.info(f"ETL completado exitosamente: {result}")
    except Exception as e:
        logger.error(f"Error durante ETL: {str(e)}")

@router.get("/status", response_model=Dict[str, Any])
async def get_etl_status(db: Session = Depends(get_db)):
    """
    Obtener estado del ETL y estadísticas de datos
    """
    try:
        from app.db.models import Proceso
        
        # Contar procesos en la base de datos
        total_procesos = db.query(Proceso).count()
        
        return {
            "total_procesos": total_procesos,
            "last_update": "Información disponible",
            "status": "ready" if total_procesos > 0 else "empty"
        }
    except Exception as e:
        logger.error(f"Error al obtener estado ETL: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error al obtener estado: {str(e)}")
