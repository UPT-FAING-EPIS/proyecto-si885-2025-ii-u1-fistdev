from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import logging

from app.core.config import settings
from app.core.database import engine, Base
from app.models import Process, User, ChatbotLog, Recomendacion

# Import routers
from app.api import procesos, chatbot, recomendaciones, admin, dashboard, etl

# Configurar logging
logging.basicConfig(level=getattr(logging, settings.LOG_LEVEL.upper()))
logger = logging.getLogger(__name__)


# Exception handlers
async def global_exception_handler(request, exc):
    """Handler global para excepciones no manejadas"""
    logger.error(f"Error no manejado en {request.url}: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Error interno del servidor",
            "message": "Ha ocurrido un error inesperado."
        }
    )


async def http_exception_handler(request, exc: HTTPException):
    """Handler para HTTPException"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code
        }
    )

# Crear tablas de base de datos
Base.metadata.create_all(bind=engine)
try:
    Base.metadata.create_all(bind=engine)
    logger.info("Tablas de base de datos creadas exitosamente")
except Exception as e:
    logger.error(f"Error creando tablas de base de datos: {str(e)}")

# Crear aplicación FastAPI
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="API para SEACE ProjectFinder - Transformando procesos públicos en oportunidades de software",
    version="1.0.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Agregar exception handlers
app.add_exception_handler(Exception, global_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)

# Incluir routers
app.include_router(
    procesos.router,
    prefix=f"{settings.API_V1_STR}/procesos",
    tags=["procesos"]
)

app.include_router(
    chatbot.router,
    prefix=f"{settings.API_V1_STR}/chatbot",
    tags=["chatbot"]
)

app.include_router(
    recomendaciones.router,
    prefix=f"{settings.API_V1_STR}/recomendaciones",
    tags=["recomendaciones"]
)

app.include_router(
    admin.router,
    prefix=f"{settings.API_V1_STR}/admin",
    tags=["admin"]
)

app.include_router(
    dashboard.router,
    prefix=f"{settings.API_V1_STR}/dashboard",
    tags=["dashboard"]
)

app.include_router(
    etl.router,
    prefix=f"{settings.API_V1_STR}/etl",
    tags=["etl"]
)


@app.get("/")
async def root():
    """Endpoint raíz con información de la API"""
    return {
        "message": "SEACE ProjectFinder API",
        "description": "API para transformar procesos públicos SEACE en oportunidades de software",
        "version": "1.0.0",
        "docs": f"{settings.API_V1_STR}/docs",
        "redoc": f"{settings.API_V1_STR}/redoc",
        "status": "running",
        "environment": settings.ENVIRONMENT
    }


@app.get("/health")
async def health_check():
    """Verificación básica de salud"""
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "environment": settings.ENVIRONMENT
    }


@app.on_event("startup")
async def startup_event():
    """Eventos al iniciar la aplicación"""
    # Crear todas las tablas
    Base.metadata.create_all(bind=engine)
    
    logger.info(f"Iniciando {settings.PROJECT_NAME}")
    logger.info(f"Entorno: {settings.ENVIRONMENT}")
    logger.info(f"API URL: {settings.API_V1_STR}")
    logger.info("Tablas de base de datos creadas/verificadas")


@app.on_event("shutdown")
async def shutdown_event():
    """Eventos al cerrar la aplicación"""
    logger.info(f"Cerrando {settings.PROJECT_NAME}")


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.ENVIRONMENT == "development",
        log_level=settings.LOG_LEVEL.lower()
    )
