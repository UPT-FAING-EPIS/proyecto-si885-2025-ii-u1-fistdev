from fastapi import APIRouter
from app.core.config import settings

router = APIRouter()


@router.get("/dashboard")
async def get_dashboard_url():
    """Obtener URL del dashboard Power BI"""
    
    if not settings.POWERBI_IFRAME_URL:
        return {
            "error": "Dashboard no configurado",
            "message": "La URL del dashboard Power BI no está configurada en las variables de entorno"
        }
    
    return {
        "iframe_url": settings.POWERBI_IFRAME_URL,
        "status": "available",
        "type": "powerbi"
    }


@router.get("/dashboard/config")
async def get_dashboard_config():
    """Obtener configuración del dashboard"""
    
    return {
        "configured": bool(settings.POWERBI_IFRAME_URL),
        "iframe_url": settings.POWERBI_IFRAME_URL if settings.POWERBI_IFRAME_URL else None,
        "recommended_settings": {
            "width": "100%",
            "height": "600px",
            "frameborder": "0",
            "allowfullscreen": True
        },
        "instructions": {
            "step1": "Crear reporte en Power BI Service",
            "step2": "Obtener enlace de iframe embebido",
            "step3": "Configurar POWERBI_IFRAME_URL en variables de entorno",
            "step4": "Reiniciar aplicación"
        }
    }
