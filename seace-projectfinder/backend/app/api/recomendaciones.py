from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Optional
from uuid import UUID
import logging

from app.core.database import get_db
from app.schemas.schemas import RecomendacionCreate, Recomendacion as RecomendacionSchema
from app.models.process import Process
from app.models.recomendacion import Recomendacion as RecomendacionModel
from app.nlp.gemini_client import GeminiClient

router = APIRouter()
gemini_client = GeminiClient()
logger = logging.getLogger(__name__)


@router.get("/{proceso_id}", response_model=list[RecomendacionSchema])
async def get_proceso_recomendaciones(
    proceso_id: UUID,
    db: Session = Depends(get_db)
):
    """Obtener recomendaciones de un proceso"""
    
    # Verificar que el proceso existe
    proceso = db.query(Process).filter(Process.id == proceso_id).first()
    if not proceso:
        raise HTTPException(status_code=404, detail="Proceso no encontrado")
    
    # Obtener recomendaciones
    recomendaciones = (
        db.query(RecomendacionModel)
        .filter(RecomendacionModel.proceso_id == proceso_id)
        .order_by(RecomendacionModel.created_at.desc())
        .all()
    )
    
    return [RecomendacionSchema.model_validate(rec) for rec in recomendaciones]


@router.post("/{proceso_id}/generate")
async def generate_recomendaciones(
    proceso_id: UUID,
    background_tasks: BackgroundTasks,
    force_regenerate: bool = False,
    db: Session = Depends(get_db)
):
    """Generar recomendaciones para un proceso usando IA"""
    
    # Verificar que el proceso existe
    proceso = db.query(Process).filter(Process.id == proceso_id).first()
    if not proceso:
        raise HTTPException(status_code=404, detail="Proceso no encontrado")
    
    # Verificar si ya tiene recomendaciones
    existing_recs = (
        db.query(RecomendacionModel)
        .filter(RecomendacionModel.proceso_id == proceso_id)
        .count()
    )
    
    if existing_recs > 0 and not force_regenerate:
        return {
            "message": "El proceso ya tiene recomendaciones. Use force_regenerate=true para regenerar.",
            "existing_count": existing_recs
        }
    
    # Programar generación en background
    background_tasks.add_task(
        generate_proceso_recommendations_task,
        str(proceso_id),
        force_regenerate
    )
    
    return {
        "message": "Generación de recomendaciones iniciada",
        "proceso_id": str(proceso_id),
        "status": "processing"
    }


@router.get("/{proceso_id}/mvp")
async def get_mvp_recommendation(
    proceso_id: UUID,
    db: Session = Depends(get_db)
):
    """Obtener recomendación específica de MVP"""
    
    recomendacion = (
        db.query(RecomendacionModel)
        .filter(
            RecomendacionModel.proceso_id == proceso_id,
            RecomendacionModel.tipo_recomendacion == "mvp"
        )
        .first()
    )
    
    if not recomendacion:
        raise HTTPException(status_code=404, detail="Recomendación MVP no encontrada")
    
    return Recomendacion.model_validate(recomendacion)


@router.get("/{proceso_id}/sprint1")
async def get_sprint1_recommendation(
    proceso_id: UUID,
    db: Session = Depends(get_db)
):
    """Obtener recomendación específica de Sprint 1"""
    
    recomendacion = (
        db.query(RecomendacionModel)
        .filter(
            RecomendacionModel.proceso_id == proceso_id,
            RecomendacionModel.tipo_recomendacion == "sprint1"
        )
        .first()
    )
    
    if not recomendacion:
        raise HTTPException(status_code=404, detail="Recomendación Sprint 1 no encontrada")
    
    return Recomendacion.model_validate(recomendacion)


@router.get("/{proceso_id}/stack-tech")
async def get_stack_tech_recommendation(
    proceso_id: UUID,
    db: Session = Depends(get_db)
):
    """Obtener recomendación de stack tecnológico"""
    
    recomendacion = (
        db.query(RecomendacionModel)
        .filter(
            RecomendacionModel.proceso_id == proceso_id,
            RecomendacionModel.tipo_recomendacion == "stack_tech"
        )
        .first()
    )
    
    if not recomendacion:
        raise HTTPException(status_code=404, detail="Recomendación de stack tecnológico no encontrada")
    
    return Recomendacion.model_validate(recomendacion)


@router.delete("/{proceso_id}/clear")
async def clear_proceso_recomendaciones(
    proceso_id: UUID,
    db: Session = Depends(get_db)
):
    """Eliminar todas las recomendaciones de un proceso"""
    
    # Verificar que el proceso existe
    proceso = db.query(Proceso).filter(Proceso.id == proceso_id).first()
    if not proceso:
        raise HTTPException(status_code=404, detail="Proceso no encontrado")
    
    # Eliminar recomendaciones
    deleted_count = (
        db.query(RecomendacionModel)
        .filter(RecomendacionModel.proceso_id == proceso_id)
        .delete()
    )
    
    db.commit()
    
    return {
        "message": f"Se eliminaron {deleted_count} recomendaciones",
        "proceso_id": str(proceso_id)
    }


async def generate_proceso_recommendations_task(proceso_id: str, force_regenerate: bool = False):
    """Tarea en background para generar recomendaciones"""
    
    try:
        with Session() as db:
            proceso = db.query(Proceso).filter(Proceso.id == proceso_id).first()
            if not proceso:
                logger.error(f"Proceso no encontrado: {proceso_id}")
                return
            
            # Si force_regenerate, eliminar recomendaciones existentes
            if force_regenerate:
                db.query(RecomendacionModel).filter(
                    RecomendacionModel.proceso_id == proceso.id
                ).delete()
                db.commit()
            
            # Preparar datos del proceso
            proceso_data = {
                "objeto_contratacion": proceso.objeto_contratacion,
                "descripcion": proceso.objeto_contratacion,  # Puede ser mejorado
                "entidad_nombre": proceso.entidad_nombre,
                "monto_referencial": float(proceso.monto_referencial) if proceso.monto_referencial else None,
                "moneda": proceso.moneda,
                "categoria_proyecto": proceso.categoria_proyecto,
                "rubro": proceso.rubro
            }
            
            # Generar recomendaciones usando Gemini
            recommendations = await gemini_client.generate_project_recommendations(proceso_data)
            
            # Guardar recomendaciones en la base de datos
            await save_recommendations_to_db(db, proceso.id, recommendations)
            
            logger.info(f"Recomendaciones generadas para proceso {proceso_id}")
            
    except Exception as e:
        logger.error(f"Error generando recomendaciones para proceso {proceso_id}: {str(e)}")


async def save_recommendations_to_db(db: Session, proceso_id: UUID, recommendations: dict):
    """Guardar recomendaciones en la base de datos"""
    
    try:
        # MVP
        if "mvp" in recommendations:
            mvp_rec = RecomendacionModel(
                proceso_id=proceso_id,
                tipo_recomendacion="mvp",
                titulo="Producto Mínimo Viable (MVP)",
                descripcion=recommendations["mvp"].get("descripcion", ""),
                datos_estructurados=recommendations["mvp"],
                confianza_score=recommendations.get("confianza", 0.8),
                generated_by=recommendations.get("generado_por", "gemini-2.5-flash")
            )
            db.add(mvp_rec)
        
        # Sprint 1
        if "sprint1" in recommendations:
            sprint1_rec = RecomendacionModel(
                proceso_id=proceso_id,
                tipo_recomendacion="sprint1",
                titulo="Plan de Sprint 1",
                descripcion=f"Sprint de {recommendations['sprint1'].get('duracion_semanas', 2)} semanas",
                datos_estructurados=recommendations["sprint1"],
                confianza_score=recommendations.get("confianza", 0.8),
                generated_by=recommendations.get("generado_por", "gemini-2.5-flash")
            )
            db.add(sprint1_rec)
        
        # Stack Tecnológico
        if "stack_tecnologico" in recommendations:
            stack_rec = RecomendacionModel(
                proceso_id=proceso_id,
                tipo_recomendacion="stack_tech",
                titulo="Stack Tecnológico Recomendado",
                descripcion=recommendations["stack_tecnologico"].get("justificacion", ""),
                datos_estructurados=recommendations["stack_tecnologico"],
                confianza_score=recommendations.get("confianza", 0.8),
                generated_by=recommendations.get("generado_por", "gemini-2.5-flash")
            )
            db.add(stack_rec)
        
        # Estimación de presupuesto
        if "presupuesto_estimado_soles" in recommendations:
            presupuesto_rec = RecomendacionModel(
                proceso_id=proceso_id,
                tipo_recomendacion="estimacion",
                titulo="Estimación de Presupuesto",
                descripcion=f"Presupuesto estimado: S/ {recommendations['presupuesto_estimado_soles']:,.2f}",
                datos_estructurados={
                    "presupuesto_soles": recommendations["presupuesto_estimado_soles"],
                    "consideraciones": recommendations.get("consideraciones_especiales", []),
                    "riesgos": recommendations.get("riesgos_identificados", [])
                },
                confianza_score=recommendations.get("confianza", 0.8),
                generated_by=recommendations.get("generado_por", "gemini-2.5-flash")
            )
            db.add(presupuesto_rec)
        
        db.commit()
        
    except Exception as e:
        logger.error(f"Error guardando recomendaciones: {str(e)}")
        db.rollback()
        raise
