import httpx
import asyncio
from typing import List, Dict, Any, Optional
from loguru import logger
from tenacity import retry, stop_after_attempt, wait_exponential
from datetime import datetime, date
import json

from app.core.config import settings
from app.core.exceptions import ExternalAPIException


class OSCEClient:
    """Cliente para interactuar con la API de OSCE"""
    
    def __init__(self):
        self.base_url = settings.OSCE_API_URL
        self.session: Optional[httpx.AsyncClient] = None
        self.rate_limit_delay = 60 / settings.OSCE_RATE_LIMIT_PER_MINUTE  # Segundos entre requests
        
    async def __aenter__(self):
        self.session = httpx.AsyncClient(
            timeout=30.0,
            headers={
                "User-Agent": "SEACE-ProjectFinder/1.0",
                "Accept": "application/json"
            }
        )
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.aclose()
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def _make_request(self, endpoint: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Realizar request con retry y rate limiting"""
        if not self.session:
            raise ExternalAPIException("Cliente no inicializado")
            
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        try:
            # Rate limiting
            await asyncio.sleep(self.rate_limit_delay)
            
            response = await self.session.get(url, params=params)
            response.raise_for_status()
            
            return response.json()
            
        except httpx.HTTPStatusError as e:
            logger.error(f"Error HTTP en OSCE API: {e.response.status_code} - {e.response.text}")
            raise ExternalAPIException(f"Error en API OSCE: {e.response.status_code}")
        except httpx.RequestError as e:
            logger.error(f"Error de conexión con OSCE API: {str(e)}")
            raise ExternalAPIException(f"Error de conexión: {str(e)}")
        except json.JSONDecodeError as e:
            logger.error(f"Error decodificando JSON de OSCE API: {str(e)}")
            raise ExternalAPIException("Respuesta inválida de la API")
    
    async def get_procesos_pagination(self, page: int = 1, size: int = 100) -> Dict[str, Any]:
        """Obtener procesos con paginación"""
        params = {
            "page": page,
            "size": size,
            "sort": "fecha_publicacion,desc"
        }
        
        return await self._make_request("procesos", params)
    
    async def get_proceso_detalle(self, proceso_id: str) -> Dict[str, Any]:
        """Obtener detalle de un proceso específico"""
        return await self._make_request(f"procesos/{proceso_id}")
    
    async def get_procesos_by_date_range(
        self, 
        fecha_inicio: date, 
        fecha_fin: date,
        page: int = 1,
        size: int = 100
    ) -> Dict[str, Any]:
        """Obtener procesos por rango de fechas"""
        params = {
            "fecha_inicio": fecha_inicio.isoformat(),
            "fecha_fin": fecha_fin.isoformat(),
            "page": page,
            "size": size
        }
        
        return await self._make_request("procesos/by-date", params)
    
    async def get_procesos_by_entidad(self, entidad_ruc: str) -> List[Dict[str, Any]]:
        """Obtener procesos de una entidad específica"""
        params = {"entidad_ruc": entidad_ruc}
        response = await self._make_request("procesos/by-entidad", params)
        return response.get("data", [])
    
    async def search_procesos(
        self, 
        query: str, 
        filters: Dict[str, Any] = None,
        page: int = 1,
        size: int = 100
    ) -> Dict[str, Any]:
        """Buscar procesos por texto y filtros"""
        params = {
            "q": query,
            "page": page,
            "size": size
        }
        
        if filters:
            params.update(filters)
            
        return await self._make_request("procesos/search", params)
    
    async def get_proceso_anexos(self, proceso_id: str) -> List[Dict[str, Any]]:
        """Obtener anexos de un proceso"""
        response = await self._make_request(f"procesos/{proceso_id}/anexos")
        return response.get("anexos", [])
    
    async def get_latest_procesos(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Obtener los procesos más recientes"""
        params = {
            "limit": limit,
            "sort": "fecha_publicacion,desc"
        }
        
        response = await self._make_request("procesos/latest", params)
        return response.get("data", [])
    
    async def get_procesos_ti(self, page: int = 1, size: int = 100) -> Dict[str, Any]:
        """Obtener procesos relacionados con TI específicamente"""
        # Filtros para identificar procesos de TI
        ti_keywords = [
            "software", "sistema", "aplicacion", "desarrollo", "programacion",
            "base de datos", "web", "tecnologia", "informatica", "digital",
            "plataforma", "portal", "app", "móvil", "cloud", "nube"
        ]
        
        params = {
            "rubros": "tecnologia,informatica,sistemas",
            "keywords": ",".join(ti_keywords),
            "page": page,
            "size": size
        }
        
        return await self._make_request("procesos/ti", params)


# Funciones helper para trabajar con datos OCDS
def clean_ocds_data(raw_data: Dict[str, Any]) -> Dict[str, Any]:
    """Limpiar y normalizar datos OCDS"""
    cleaned = {}
    
    try:
        # Extraer información básica
        if "tender" in raw_data:
            tender = raw_data["tender"]
            cleaned.update({
                "titulo": tender.get("title", ""),
                "descripcion": tender.get("description", ""),
                "monto": tender.get("value", {}).get("amount"),
                "moneda": tender.get("value", {}).get("currency"),
                "fecha_publicacion": tender.get("datePublished"),
                "fecha_limite": tender.get("tenderPeriod", {}).get("endDate")
            })
        
        # Extraer información de la entidad compradora
        if "buyer" in raw_data:
            buyer = raw_data["buyer"]
            cleaned.update({
                "entidad_nombre": buyer.get("name", ""),
                "entidad_id": buyer.get("identifier", {}).get("id", "")
            })
        
        # Extraer clasificación
        if "tender" in raw_data and "classification" in raw_data["tender"]:
            classification = raw_data["tender"]["classification"]
            cleaned["categoria"] = classification.get("description", "")
            cleaned["codigo_categoria"] = classification.get("id", "")
        
        # Extraer documentos/anexos
        if "tender" in raw_data and "documents" in raw_data["tender"]:
            documents = raw_data["tender"]["documents"]
            cleaned["documentos"] = [
                {
                    "titulo": doc.get("title", ""),
                    "url": doc.get("url", ""),
                    "tipo": doc.get("documentType", "")
                }
                for doc in documents
            ]
        
        return cleaned
        
    except Exception as e:
        logger.error(f"Error limpiando datos OCDS: {str(e)}")
        return raw_data


def extract_ti_indicators(proceso_data: Dict[str, Any]) -> Dict[str, Any]:
    """Extraer indicadores de que un proceso es relacionado con TI"""
    
    ti_keywords = [
        "software", "sistema", "aplicación", "desarrollo", "programación",
        "base de datos", "web", "tecnología", "informática", "digital",
        "plataforma", "portal", "app", "móvil", "cloud", "nube", "api",
        "backend", "frontend", "inteligencia artificial", "machine learning"
    ]
    
    indicators = {
        "es_ti": False,
        "confianza": 0.0,
        "keywords_encontradas": [],
        "categoria_ti": None
    }
    
    # Texto a analizar
    texto_analisis = " ".join([
        proceso_data.get("objeto_contratacion", ""),
        proceso_data.get("titulo", ""),
        proceso_data.get("descripcion", ""),
    ]).lower()
    
    # Buscar keywords
    keywords_encontradas = [kw for kw in ti_keywords if kw in texto_analisis]
    
    if keywords_encontradas:
        indicators["keywords_encontradas"] = keywords_encontradas
        indicators["confianza"] = min(len(keywords_encontradas) * 0.2, 1.0)
        
        # Determinar si es proceso TI
        if indicators["confianza"] >= 0.3:
            indicators["es_ti"] = True
            
            # Categorizar tipo de proyecto TI
            if any(kw in keywords_encontradas for kw in ["desarrollo", "software", "aplicación"]):
                indicators["categoria_ti"] = "desarrollo_software"
            elif any(kw in keywords_encontradas for kw in ["web", "portal", "plataforma"]):
                indicators["categoria_ti"] = "desarrollo_web"
            elif any(kw in keywords_encontradas for kw in ["base de datos", "sistema"]):
                indicators["categoria_ti"] = "sistema_gestion"
            elif any(kw in keywords_encontradas for kw in ["móvil", "app"]):
                indicators["categoria_ti"] = "aplicacion_movil"
            else:
                indicators["categoria_ti"] = "tecnologia_general"
    
    return indicators
