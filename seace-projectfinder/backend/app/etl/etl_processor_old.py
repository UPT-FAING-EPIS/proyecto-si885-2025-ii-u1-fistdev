import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime, date, timedelta
from sqlalchemy.orm import Session
from loguru import logger

from app.core.database import SessionLocal
from app.db.models import Proceso, Anexo, Configuracion
from app.etl.osce_client import OSCEClient, clean_ocds_data, extract_ti_indicators
from app.schemas.schemas import ProcesoCreate
from app.core.exceptions import ETLException


class ETLProcessor:
    """Procesador ETL para datos SEACE/OSCE"""
    
    def __init__(self):
        self.batch_size = 100
        self.processed_count = 0
        self.error_count = 0
        
    async def run_daily_sync(self) -> Dict[str, Any]:
        """Ejecutar sincronización diaria"""
        logger.info("Iniciando sincronización diaria con OSCE")
        
        start_time = datetime.now()
        stats = {
            "procesados": 0,
            "nuevos": 0,
            "actualizados": 0,
            "errores": 0,
            "inicio": start_time,
            "fin": None
        }
        
        try:
            # Obtener fecha de última sincronización
            with SessionLocal() as db:
                last_sync = self._get_last_sync_date(db)
                
            # Si es la primera vez, sincronizar últimos 30 días
            if not last_sync:
                fecha_inicio = date.today() - timedelta(days=30)
            else:
                fecha_inicio = last_sync.date()
                
            fecha_fin = date.today()
            
            logger.info(f"Sincronizando desde {fecha_inicio} hasta {fecha_fin}")
            
            # Procesar datos por lotes
            async with OSCEClient() as client:
                stats = await self._process_date_range(client, fecha_inicio, fecha_fin, stats)
            
            # Actualizar fecha de última sincronización
            with SessionLocal() as db:
                self._update_last_sync_date(db, datetime.now())
                
            stats["fin"] = datetime.now()
            logger.info(f"Sincronización completada: {stats}")
            
            return stats
            
        except Exception as e:
            logger.error(f"Error en sincronización diaria: {str(e)}")
            stats["errores"] += 1
            stats["fin"] = datetime.now()
            raise ETLException(f"Error en sincronización: {str(e)}")
    
    async def run_full_sync(self, days_back: int = 365) -> Dict[str, Any]:
        """Ejecutar sincronización completa"""
        logger.info(f"Iniciando sincronización completa ({days_back} días)")
        
        start_time = datetime.now()
        stats = {
            "procesados": 0,
            "nuevos": 0,
            "actualizados": 0,
            "errores": 0,
            "inicio": start_time,
            "fin": None
        }
        
        try:
            fecha_inicio = date.today() - timedelta(days=days_back)
            fecha_fin = date.today()
            
            async with OSCEClient() as client:
                stats = await self._process_date_range(client, fecha_inicio, fecha_fin, stats)
            
            # Actualizar fecha de última sincronización
            with SessionLocal() as db:
                self._update_last_sync_date(db, datetime.now())
                
            stats["fin"] = datetime.now()
            logger.info(f"Sincronización completa finalizada: {stats}")
            
            return stats
            
        except Exception as e:
            logger.error(f"Error en sincronización completa: {str(e)}")
            stats["errores"] += 1
            stats["fin"] = datetime.now()
            raise ETLException(f"Error en sincronización completa: {str(e)}")
    
    async def sync_ti_processes_only(self) -> Dict[str, Any]:
        """Sincronizar solo procesos relacionados con TI"""
        logger.info("Iniciando sincronización de procesos TI")
        
        start_time = datetime.now()
        stats = {
            "procesados": 0,
            "nuevos": 0,
            "actualizados": 0,
            "errores": 0,
            "ti_detectados": 0,
            "inicio": start_time,
            "fin": None
        }
        
        try:
            async with OSCEClient() as client:
                page = 1
                total_pages = 1
                
                while page <= total_pages:
                    logger.info(f"Procesando página {page} de procesos TI")
                    
                    # Obtener procesos TI
                    response = await client.get_procesos_ti(page=page, size=self.batch_size)
                    
                    if "data" not in response:
                        break
                        
                    procesos = response["data"]
                    total_pages = response.get("total_pages", 1)
                    
                    # Procesar lote
                    batch_stats = await self._process_batch(procesos, ti_only=True)
                    
                    # Actualizar estadísticas
                    stats["procesados"] += batch_stats["procesados"]
                    stats["nuevos"] += batch_stats["nuevos"]
                    stats["actualizados"] += batch_stats["actualizados"]
                    stats["errores"] += batch_stats["errores"]
                    stats["ti_detectados"] += batch_stats.get("ti_detectados", 0)
                    
                    page += 1
                    
                    # Delay entre lotes para no saturar la API
                    await asyncio.sleep(1)
            
            stats["fin"] = datetime.now()
            logger.info(f"Sincronización TI completada: {stats}")
            
            return stats
            
        except Exception as e:
            logger.error(f"Error en sincronización TI: {str(e)}")
            stats["errores"] += 1
            stats["fin"] = datetime.now()
            raise ETLException(f"Error en sincronización TI: {str(e)}")
    
    async def _process_date_range(
        self, 
        client: OSCEClient, 
        fecha_inicio: date, 
        fecha_fin: date,
        stats: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Procesar rango de fechas"""
        
        page = 1
        total_pages = 1
        
        while page <= total_pages:
            logger.info(f"Procesando página {page}")
            
            # Obtener datos de OSCE
            response = await client.get_procesos_by_date_range(
                fecha_inicio, fecha_fin, page, self.batch_size
            )
            
            if "data" not in response:
                break
                
            procesos = response["data"]
            total_pages = response.get("total_pages", 1)
            
            # Procesar lote
            batch_stats = await self._process_batch(procesos)
            
            # Actualizar estadísticas
            stats["procesados"] += batch_stats["procesados"]
            stats["nuevos"] += batch_stats["nuevos"]
            stats["actualizados"] += batch_stats["actualizados"]
            stats["errores"] += batch_stats["errores"]
            
            page += 1
            
            # Delay entre lotes
            await asyncio.sleep(1)
        
        return stats
    
    async def _process_batch(self, procesos: List[Dict[str, Any]], ti_only: bool = False) -> Dict[str, Any]:
        """Procesar lote de procesos"""
        
        stats = {
            "procesados": 0,
            "nuevos": 0,
            "actualizados": 0,
            "errores": 0,
            "ti_detectados": 0
        }
        
        with SessionLocal() as db:
            for proceso_data in procesos:
                try:
                    # Limpiar datos OCDS
                    cleaned_data = clean_ocds_data(proceso_data)
                    
                    # Detectar si es proceso TI
                    ti_indicators = extract_ti_indicators(cleaned_data)
                    
                    # Si solo queremos procesos TI y este no lo es, saltar
                    if ti_only and not ti_indicators["es_ti"]:
                        continue
                        
                    if ti_indicators["es_ti"]:
                        stats["ti_detectados"] += 1
                    
                    # Verificar si el proceso ya existe
                    id_proceso = cleaned_data.get("id_proceso") or proceso_data.get("id")
                    
                    if not id_proceso:
                        logger.warning("Proceso sin ID, saltando")
                        continue
                    
                    existing = db.query(Proceso).filter(Proceso.id_proceso == id_proceso).first()
                    
                    if existing:
                        # Actualizar proceso existente
                        updated = self._update_proceso(db, existing, cleaned_data, ti_indicators)
                        if updated:
                            stats["actualizados"] += 1
                    else:
                        # Crear nuevo proceso
                        self._create_proceso(db, cleaned_data, ti_indicators)
                        stats["nuevos"] += 1
                    
                    stats["procesados"] += 1
                    
                except Exception as e:
                    logger.error(f"Error procesando proceso {proceso_data.get('id', 'unknown')}: {str(e)}")
                    stats["errores"] += 1
            
            db.commit()
        
        return stats
    
    def _create_proceso(
        self, 
        db: Session, 
        proceso_data: Dict[str, Any], 
        ti_indicators: Dict[str, Any]
    ) -> Proceso:
        """Crear nuevo proceso en base de datos"""
        
        # Mapear datos a modelo
        proceso = Proceso(
            id_proceso=proceso_data.get("id_proceso") or proceso_data.get("id"),
            url_proceso=proceso_data.get("url"),
            numero_convocatoria=proceso_data.get("numero_convocatoria"),
            entidad_nombre=proceso_data.get("entidad_nombre"),
            entidad_ruc=proceso_data.get("entidad_ruc") or proceso_data.get("entidad_id"),
            objeto_contratacion=proceso_data.get("objeto_contratacion") or proceso_data.get("titulo"),
            tipo_proceso=proceso_data.get("tipo_proceso"),
            estado_proceso=proceso_data.get("estado_proceso"),
            fecha_publicacion=self._parse_datetime(proceso_data.get("fecha_publicacion")),
            fecha_limite_presentacion=self._parse_datetime(proceso_data.get("fecha_limite")),
            monto_referencial=proceso_data.get("monto"),
            moneda=proceso_data.get("moneda"),
            rubro=proceso_data.get("categoria") or proceso_data.get("rubro"),
            departamento=proceso_data.get("departamento"),
            provincia=proceso_data.get("provincia"),
            distrito=proceso_data.get("distrito"),
            datos_ocds=proceso_data,
            complejidad_estimada="media",  # Default, será procesado por NLP
            categoria_proyecto=ti_indicators.get("categoria_ti") if ti_indicators["es_ti"] else None
        )
        
        db.add(proceso)
        db.flush()  # Para obtener el ID
        
        # Procesar anexos si existen
        if "documentos" in proceso_data:
            for doc in proceso_data["documentos"]:
                anexo = Anexo(
                    proceso_id=proceso.id,
                    nombre_archivo=doc.get("titulo", ""),
                    url_descarga=doc.get("url", ""),
                    tipo_documento=doc.get("tipo", "")
                )
                db.add(anexo)
        
        return proceso
    
    def _update_proceso(
        self, 
        db: Session, 
        proceso: Proceso, 
        proceso_data: Dict[str, Any],
        ti_indicators: Dict[str, Any]
    ) -> bool:
        """Actualizar proceso existente"""
        
        updated = False
        
        # Campos que pueden cambiar
        updates = {
            "estado_proceso": proceso_data.get("estado_proceso"),
            "fecha_limite_presentacion": self._parse_datetime(proceso_data.get("fecha_limite")),
            "monto_referencial": proceso_data.get("monto"),
            "datos_ocds": proceso_data
        }
        
        # Solo actualizar si hay cambios
        for field, new_value in updates.items():
            if new_value is not None and getattr(proceso, field) != new_value:
                setattr(proceso, field, new_value)
                updated = True
        
        # Actualizar categoría TI si se detectó
        if ti_indicators["es_ti"] and not proceso.categoria_proyecto:
            proceso.categoria_proyecto = ti_indicators.get("categoria_ti")
            updated = True
        
        if updated:
            proceso.fecha_actualizacion = datetime.now()
        
        return updated
    
    def _parse_datetime(self, date_str: Optional[str]) -> Optional[datetime]:
        """Parsear string de fecha a datetime"""
        if not date_str:
            return None
            
        try:
            # Intentar varios formatos
            formats = [
                "%Y-%m-%dT%H:%M:%S",
                "%Y-%m-%dT%H:%M:%SZ",
                "%Y-%m-%d %H:%M:%S",
                "%Y-%m-%d"
            ]
            
            for fmt in formats:
                try:
                    return datetime.strptime(date_str[:len(fmt)], fmt)
                except ValueError:
                    continue
                    
            logger.warning(f"No se pudo parsear fecha: {date_str}")
            return None
            
        except Exception as e:
            logger.error(f"Error parseando fecha {date_str}: {str(e)}")
            return None
    
    def _get_last_sync_date(self, db: Session) -> Optional[datetime]:
        """Obtener fecha de última sincronización"""
        config = db.query(Configuracion).filter(
            Configuracion.clave == "last_osce_sync"
        ).first()
        
        if config and config.valor:
            try:
                return datetime.fromisoformat(config.valor)
            except ValueError:
                return None
        
        return None
    
    def _update_last_sync_date(self, db: Session, sync_date: datetime):
        """Actualizar fecha de última sincronización"""
        config = db.query(Configuracion).filter(
            Configuracion.clave == "last_osce_sync"
        ).first()
        
        if config:
            config.valor = sync_date.isoformat()
            config.updated_at = datetime.now()
        else:
            config = Configuracion(
                clave="last_osce_sync",
                valor=sync_date.isoformat(),
                descripcion="Última sincronización con datos OSCE"
            )
            db.add(config)
        
        db.commit()


# Funciones utilitarias para limpieza de datos
def validate_proceso_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Validar y limpiar datos de proceso"""
    
    # Validaciones básicas
    required_fields = ["id_proceso"]
    for field in required_fields:
        if not data.get(field):
            raise ValueError(f"Campo requerido faltante: {field}")
    
    # Limpiar texto
    text_fields = ["objeto_contratacion", "entidad_nombre", "titulo", "descripcion"]
    for field in text_fields:
        if data.get(field):
            # Limpiar caracteres especiales y normalizar espacios
            data[field] = " ".join(data[field].split()).strip()
    
    # Validar montos
    if data.get("monto"):
        try:
            data["monto"] = float(data["monto"])
            if data["monto"] < 0:
                data["monto"] = None
        except (ValueError, TypeError):
            data["monto"] = None
    
    # Validar RUC
    if data.get("entidad_ruc"):
        ruc = str(data["entidad_ruc"]).strip()
        if len(ruc) == 11 and ruc.isdigit():
            data["entidad_ruc"] = ruc
        else:
            data["entidad_ruc"] = None
    
    return data


def deduplicate_processes(processes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Eliminar procesos duplicados"""
    
    seen_ids = set()
    unique_processes = []
    
    for process in processes:
        process_id = process.get("id_proceso") or process.get("id")
        if process_id and process_id not in seen_ids:
            seen_ids.add(process_id)
            unique_processes.append(process)
    
    logger.info(f"Procesos únicos después de deduplicación: {len(unique_processes)} de {len(processes)}")
    
    return unique_processes
