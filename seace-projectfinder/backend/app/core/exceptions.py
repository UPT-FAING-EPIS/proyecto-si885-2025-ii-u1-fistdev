from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
import logging
import traceback

logger = logging.getLogger(__name__)


class BaseSeaceException(Exception):
    """Base exception for all SEACE-related errors"""
    def __init__(self, message: str, error_code: str = None):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)


class NLPException(BaseSeaceException):
    """Exception for NLP processing errors"""
    pass


class ETLException(BaseSeaceException):
    """Exception for ETL processing errors"""
    pass


class OSCEAPIException(BaseSeaceException):
    """Exception for OSCE API related errors"""
    pass


class DatabaseException(BaseSeaceException):
    """Exception for database operation errors"""
    pass


class AuthenticationException(BaseSeaceException):
    """Exception for authentication errors"""
    pass


class ValidationException(BaseSeaceException):
    """Exception for data validation errors"""
    pass


async def global_exception_handler(request: Request, exc: Exception):
    """Handler global para excepciones no manejadas"""
    
    # Log del error
    logger.error(f"Error no manejado en {request.url}: {str(exc)}")
    logger.error(f"Traceback: {traceback.format_exc()}")
    
    # Respuesta de error genérica
    return JSONResponse(
        status_code=500,
        content={
            "error": "Error interno del servidor",
            "message": "Ha ocurrido un error inesperado. Por favor, inténtelo más tarde.",
            "request_id": getattr(request.state, 'request_id', 'unknown')
        }
    )


async def http_exception_handler(request: Request, exc: HTTPException):
    """Handler para excepciones HTTP"""
    
    logger.warning(f"HTTP Exception en {request.url}: {exc.status_code} - {exc.detail}")
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": "Error de solicitud",
            "message": exc.detail,
            "status_code": exc.status_code
        }
    )


class SeaceProjectFinderException(Exception):
    """Excepción base para el proyecto"""
    def __init__(self, message: str, error_code: str = None):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)


class ETLException(SeaceProjectFinderException):
    """Excepción para errores en el proceso ETL"""
    pass


class NLPException(SeaceProjectFinderException):
    """Excepción para errores en procesamiento NLP"""
    pass


class ExternalAPIException(SeaceProjectFinderException):
    """Excepción para errores en APIs externas"""
    pass
