import asyncio
from datetime import datetime, date, timedelta
from typing import List, Dict, Any, Optional
import logging
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.core.database import get_db
from app.models.process import Process
from app.etl.seace_client import SEACEClient
from app.core.exceptions import ETLException

logger = logging.getLogger(__name__)


class ETLProcessor:
    """Procesador ETL para extraer datos del portal SEACE"""
    
    def __init__(self):
        self.seace_client = SEACEClient()
        self.batch_size = 50
        self.max_pages = 10  # Límite de páginas por ejecución
        
    async def run_daily_sync(self) -> Dict[str, Any]:
        """Ejecutar sincronización diaria"""
        start_time = datetime.now()
        stats = {
            "start_time": start_time.isoformat(),
            "processes_found": 0,
            "processes_new": 0,
            "processes_updated": 0,
            "processes_skipped": 0,
            "errors": []
        }
        
        try:
            # Buscar procesos de TI de los últimos 30 días
            end_date = date.today()
            start_date = end_date - timedelta(days=30)
            
            async with self.seace_client as client:
                # Buscar procesos relacionados con TI
                results = await client.search_it_processes(page=1)
                stats["processes_found"] = results.get("total", 0)
                
                # Procesar resultados
                db = next(get_db())
                try:
                    for process_data in results.get("processes", []):
                        try:
                            result = await self._process_single_record(db, process_data)
                            if result == "new":
                                stats["processes_new"] += 1
                            elif result == "updated":
                                stats["processes_updated"] += 1
                            else:
                                stats["processes_skipped"] += 1
                                
                        except Exception as e:
                            error_msg = f"Error procesando proceso {process_data.get('numero_proceso', 'N/A')}: {str(e)}"
                            logger.error(error_msg)
                            stats["errors"].append(error_msg)
                    
                    db.commit()
                    
                finally:
                    db.close()
                    
        except Exception as e:
            error_msg = f"Error en sincronización diaria: {str(e)}"
            logger.error(error_msg)
            stats["errors"].append(error_msg)
            
        stats["end_time"] = datetime.now().isoformat()
        stats["duration_minutes"] = (datetime.now() - start_time).total_seconds() / 60
        
        logger.info(f"Sincronización completada: {stats}")
        return stats
    
    async def _process_single_record(self, db: Session, process_data: Dict[str, Any]) -> str:
        """Procesar un solo registro de proceso"""
        try:
            numero_proceso = process_data.get("numero_proceso")
            if not numero_proceso:
                return "skipped"
            
            # Verificar si el proceso ya existe
            existing = db.query(Process).filter(Process.numero_proceso == numero_proceso).first()
            
            if existing:
                # Actualizar si hay cambios
                updated = self._update_process_if_changed(existing, process_data)
                if updated:
                    db.commit()
                    return "updated"
                return "skipped"
            else:
                # Crear nuevo proceso
                new_process = self._create_process_from_data(process_data)
                db.add(new_process)
                db.commit()
                return "new"
                
        except IntegrityError:
            db.rollback()
            logger.warning(f"Proceso duplicado ignorado: {numero_proceso}")
            return "skipped"
        except Exception as e:
            db.rollback()
            raise e
    
    def _create_process_from_data(self, data: Dict[str, Any]) -> Process:
        """Crear objeto Process desde datos SEACE"""
        
        # Parsear fecha de publicación
        fecha_pub = None
        if data.get("fecha_publicacion"):
            try:
                fecha_pub = datetime.strptime(data["fecha_publicacion"], "%d/%m/%Y")
            except:
                pass
        
        return Process(
            numero_proceso=data.get("numero_proceso", ""),
            objeto_contratacion=data.get("objeto_contratacion", ""),
            tipo_proceso=data.get("tipo_proceso", ""),
            estado_proceso=data.get("estado", ""),
            entidad_nombre=data.get("entidad", ""),
            entidad_ruc="",  # No disponible en búsqueda básica
            fecha_publicacion=fecha_pub or datetime.now(),
            fecha_buenpro=None,
            monto_referencial=data.get("valor_referencial"),
            monto_adjudicado=None,
            tipo_moneda=data.get("moneda", "PEN"),
            departamento="",  # Requiere extracción adicional
            provincia="",
            distrito="",
            url_seace=data.get("url_detalle", ""),
            relevancia_ti=data.get("relevancia_ti", 0),
            procesado_nlp=False
        )
    
    def _update_process_if_changed(self, existing: Process, new_data: Dict[str, Any]) -> bool:
        """Actualizar proceso existente si hay cambios"""
        changed = False
        
        # Verificar campos que pueden cambiar
        if new_data.get("estado") != existing.estado_proceso:
            existing.estado_proceso = new_data.get("estado", existing.estado_proceso)
            changed = True
        
        if new_data.get("valor_referencial") and new_data["valor_referencial"] != existing.monto_referencial:
            existing.monto_referencial = new_data["valor_referencial"]
            changed = True
        
        if new_data.get("url_detalle") and new_data["url_detalle"] != existing.url_seace:
            existing.url_seace = new_data["url_detalle"]
            changed = True
        
        if changed:
            existing.updated_at = datetime.now()
        
        return changed
    
    async def search_processes_by_keyword(self, keyword: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Buscar procesos por palabra clave específica"""
        try:
            async with self.seace_client as client:
                results = await client.search_processes(objeto_contratacion=keyword)
                return results.get("processes", [])[:limit]
        except Exception as e:
            logger.error(f"Error buscando procesos por keyword '{keyword}': {e}")
            raise ETLException(f"Error en búsqueda: {e}")
    
    async def get_process_details(self, numero_proceso: str) -> Optional[Dict[str, Any]]:
        """Obtener detalles completos de un proceso específico"""
        try:
            async with self.seace_client as client:
                results = await client.search_processes(objeto_contratacion=numero_proceso)
                processes = results.get("processes", [])
                
                for process in processes:
                    if process.get("numero_proceso") == numero_proceso:
                        return process
                
                return None
        except Exception as e:
            logger.error(f"Error obteniendo detalles del proceso {numero_proceso}: {e}")
            return None
    
    async def extract_it_opportunities(self, days_back: int = 7) -> Dict[str, Any]:
        """Extraer oportunidades específicas de TI de los últimos días"""
        try:
            async with self.seace_client as client:
                results = await client.search_it_processes(page=1)
                
                # Filtrar por fechas recientes
                recent_processes = []
                cutoff_date = date.today() - timedelta(days=days_back)
                
                for process in results.get("processes", []):
                    fecha_pub = process.get("fecha_publicacion")
                    if fecha_pub:
                        try:
                            process_date = datetime.strptime(fecha_pub, "%d/%m/%Y").date()
                            if process_date >= cutoff_date:
                                recent_processes.append(process)
                        except:
                            continue
                
                return {
                    "total_found": len(recent_processes),
                    "opportunities": recent_processes,
                    "search_date": date.today().isoformat(),
                    "days_searched": days_back
                }
                
        except Exception as e:
            logger.error(f"Error extrayendo oportunidades TI: {e}")
            raise ETLException(f"Error en extracción: {e}")
    
    def get_sync_stats(self, db: Session) -> Dict[str, Any]:
        """Obtener estadísticas de sincronización"""
        try:
            total_processes = db.query(Process).count()
            processes_with_nlp = db.query(Process).filter(Process.procesado_nlp == True).count()
            recent_processes = db.query(Process).filter(
                Process.created_at >= datetime.now() - timedelta(days=7)
            ).count()
            
            return {
                "total_processes": total_processes,
                "processes_with_nlp": processes_with_nlp,
                "recent_processes": recent_processes,
                "nlp_coverage": (processes_with_nlp / total_processes * 100) if total_processes > 0 else 0
            }
        except Exception as e:
            logger.error(f"Error obteniendo estadísticas: {e}")
            return {"error": str(e)}
