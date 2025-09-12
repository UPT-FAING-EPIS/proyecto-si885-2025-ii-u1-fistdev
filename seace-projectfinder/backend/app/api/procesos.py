from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
import logging

from app.core.database import get_db
from app.models.process import Process
from app.schemas.schemas import (
    ProcessResponse,
    ProcessFilter,
    PaginatedResponse
)
from sqlalchemy import desc, asc, and_, or_, func

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/", response_model=PaginatedResponse)
async def get_procesos(
    page: int = Query(1, ge=1, description="Número de página"),
    size: int = Query(20, ge=1, le=100, description="Tamaño de página"),
    estado_proceso: Optional[str] = Query(None, description="Filtrar por estado"),
    tipo_proceso: Optional[str] = Query(None, description="Filtrar por tipo de proceso"),
    rubro: Optional[str] = Query(None, description="Filtrar por rubro"),
    departamento: Optional[str] = Query(None, description="Filtrar por departamento"),
    monto_min: Optional[float] = Query(None, description="Monto mínimo"),
    monto_max: Optional[float] = Query(None, description="Monto máximo"),
    search_text: Optional[str] = Query(None, description="Búsqueda en texto"),
    sort_by: str = Query("fecha_publicacion", description="Campo para ordenar"),
    sort_order: str = Query("desc", description="Orden: asc o desc"),
    db: Session = Depends(get_db)
):
    """Obtener lista paginada de procesos con filtros"""
    
    try:
        # Construcción de query base
        query = db.query(Process)
        
        # Aplicar filtros
        filters = []
        
        if estado_proceso:
            filters.append(Process.estado_proceso == estado_proceso)
        
        if tipo_proceso:
            filters.append(Process.tipo_proceso.ilike(f"%{tipo_proceso}%"))
        
        if rubro:
            filters.append(Process.rubro.ilike(f"%{rubro}%"))
        
        if departamento:
            filters.append(Process.departamento.ilike(f"%{departamento}%"))
        
        if monto_min:
            filters.append(Process.monto_referencial >= monto_min)
        
        if monto_max:
            filters.append(Process.monto_referencial <= monto_max)
        
        if search_text:
            filters.append(or_(
                Process.objeto_contratacion.ilike(f"%{search_text}%"),
                Process.entidad_nombre.ilike(f"%{search_text}%"),
                Process.rubro.ilike(f"%{search_text}%")
            ))
        
        # Aplicar filtros
        if filters:
            query = query.filter(and_(*filters))
        
        # Ordenamiento
        sort_column = getattr(Process, sort_by, Process.fecha_publicacion)
        if sort_order.lower() == "desc":
            query = query.order_by(desc(sort_column))
        else:
            query = query.order_by(asc(sort_column))
        
        # Paginación
        total = query.count()
        skip = (page - 1) * size
        procesos = query.offset(skip).limit(size).all()
        
        return PaginatedResponse(
            items=[ProcessResponse.model_validate(proceso) for proceso in procesos],
            total=total,
            page=page,
            size=size,
            pages=(total + size - 1) // size
        )
        
    except Exception as e:
        logger.error(f"Error en get_procesos: {str(e)}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")


@router.get("/{proceso_id}", response_model=ProcessResponse)
async def get_proceso_detail(
    proceso_id: UUID,
    db: Session = Depends(get_db)
):
    """Obtener detalles de un proceso específico"""
    
    proceso = db.query(Process).filter(Process.id == proceso_id).first()
    
    if not proceso:
        raise HTTPException(status_code=404, detail="Proceso no encontrado")
    
    return ProcessResponse.model_validate(proceso)


@router.get("/stats/general")
async def get_stats(
    db: Session = Depends(get_db)
):
    """Obtener estadísticas generales de procesos"""
    
    try:
        total_procesos = db.query(Process).count()
        procesos_activos = db.query(Process).filter(Process.estado_proceso == "En proceso").count()
        procesos_adjudicados = db.query(Process).filter(Process.estado_proceso == "Adjudicado").count()
        
        # Valor total de procesos
        total_valor_result = db.query(func.sum(Process.monto_referencial)).filter(
            Process.monto_referencial.isnot(None)
        ).scalar()
        total_valor = float(total_valor_result) if total_valor_result else 0
        
        return {
            "total_procesos": total_procesos,
            "procesos_activos": procesos_activos,
            "procesos_adjudicados": procesos_adjudicados,
            "valor_total": total_valor
        }
        
    except Exception as e:
        logger.error(f"Error en get_stats: {str(e)}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")


@router.get("/search/text")
async def search_procesos_text(
    q: str = Query(..., description="Texto a buscar"),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Búsqueda de texto completo en procesos"""
    
    try:
        # Búsqueda en múltiples campos
        search_filter = or_(
            Process.objeto_contratacion.ilike(f"%{q}%"),
            Process.entidad_nombre.ilike(f"%{q}%"),
            Process.tipo_proceso.ilike(f"%{q}%"),
            Process.rubro.ilike(f"%{q}%")
        )
        
        query = db.query(Process).filter(search_filter)
        
        total = query.count()
        
        # Ordenar por relevancia (fecha publicación desc por ahora)
        procesos = (
            query.order_by(desc(Process.fecha_publicacion))
            .offset((page - 1) * size)
            .limit(size)
            .all()
        )
        
        return {
            "query": q,
            "total": total,
            "page": page,
            "size": size,
            "results": [ProcessResponse.model_validate(p) for p in procesos]
        }
        
    except Exception as e:
        logger.error(f"Error en búsqueda de texto: {str(e)}")
        raise HTTPException(status_code=500, detail="Error en búsqueda")


@router.get("/stats/overview")
async def get_procesos_stats(db: Session = Depends(get_db)):
    """Obtener estadísticas generales de procesos"""
    
    try:
        # Estadísticas básicas
        total_procesos = db.query(Process).count()
        total_ti = db.query(Process).filter(Process.categoria_proyecto == "TI").count()
        
        # Monto total simplificado
        monto_total = 0
        
        # Procesos por estado (simplificado)
        estados = [{"estado": "Sin definir", "cantidad": total_procesos}]
        
        # Procesos por tipo
        tipos = db.query(
            Process.tipo_proceso,
            func.count(Process.id)
        ).group_by(Process.tipo_proceso).all()
        
        # Entidades más activas
        entidades = db.query(
            Process.entidad_nombre,
            func.count(Process.id)
        ).group_by(Process.entidad_nombre).order_by(
            func.count(Process.id).desc()
        ).limit(5).all()
        
        return {
            "total_procesos": total_procesos,
            "total_ti": total_ti,
            "monto_total": monto_total,
            "por_estado": estados,
            "por_tipo": [{"tipo": t[0] or "Sin definir", "cantidad": t[1]} for t in tipos],
            "entidades_activas": [{"entidad": ent[0], "cantidad": ent[1]} for ent in entidades]
        }
        
    except Exception as e:
        logger.error(f"Error obteniendo estadísticas: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error obteniendo estadísticas: {str(e)}")
