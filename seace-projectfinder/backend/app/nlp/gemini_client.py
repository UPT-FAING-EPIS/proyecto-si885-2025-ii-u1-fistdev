import google.generativeai as genai
import asyncio
from typing import List, Dict, Any, Optional
from loguru import logger
from tenacity import retry, stop_after_attempt, wait_exponential
import json
import time
from datetime import datetime

from app.core.config import settings
from app.core.exceptions import NLPException


class GeminiClient:
    """Cliente para interactuar con Google Gemini API"""
    
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        self.model_name = "gemini-2.5-flash"
        self.rate_limit_delay = 60 / settings.GEMINI_RATE_LIMIT_PER_MINUTE
        self._last_request_time = 0
        
        # Configurar Gemini
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel(self.model_name)
        else:
            logger.warning("API key de Gemini no configurada")
            self.model = None
    
    async def _rate_limit(self):
        """Aplicar rate limiting"""
        current_time = time.time()
        time_since_last = current_time - self._last_request_time
        
        if time_since_last < self.rate_limit_delay:
            await asyncio.sleep(self.rate_limit_delay - time_since_last)
        
        self._last_request_time = time.time()
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def generate_content(self, prompt: str) -> str:
        """Generar contenido usando Gemini"""
        if not self.model:
            raise NLPException("Cliente Gemini no inicializado")
        
        await self._rate_limit()
        
        try:
            response = await asyncio.to_thread(
                self.model.generate_content,
                prompt
            )
            
            if response.text:
                return response.text.strip()
            else:
                raise NLPException("Respuesta vacía de Gemini")
                
        except Exception as e:
            logger.error(f"Error en Gemini API: {str(e)}")
            raise NLPException(f"Error generando contenido: {str(e)}")
    
    async def classify_proceso_complexity(self, proceso_data: Dict[str, Any]) -> Dict[str, Any]:
        """Clasificar complejidad de un proceso"""
        
        prompt = f"""
        Analiza el siguiente proceso de contratación pública y clasifica su complejidad técnica.
        
        Título: {proceso_data.get('objeto_contratacion', 'N/A')}
        Descripción: {proceso_data.get('descripcion', 'N/A')}
        Monto: {proceso_data.get('monto_referencial', 'N/A')} {proceso_data.get('moneda', '')}
        Entidad: {proceso_data.get('entidad_nombre', 'N/A')}
        
        Clasifica la complejidad como:
        - baja: Proyectos simples, mantenimiento, configuraciones básicas
        - media: Desarrollo de aplicaciones estándar, integraciones moderadas
        - alta: Sistemas complejos, arquitecturas avanzadas, múltiples integraciones
        
        Responde en formato JSON:
        {{
            "complejidad": "baja|media|alta",
            "justificacion": "breve explicación",
            "factores_clave": ["factor1", "factor2"],
            "tiempo_estimado_meses": número,
            "equipo_recomendado": número_personas
        }}
        """
        
        try:
            response = await self.generate_content(prompt)
            result = json.loads(response)
            result["confianza"] = 0.8  # Confianza base para clasificación
            return result
        except json.JSONDecodeError:
            logger.error(f"Error parseando respuesta de clasificación: {response}")
            return {
                "complejidad": "media",
                "justificacion": "Error en análisis automático",
                "factores_clave": [],
                "tiempo_estimado_meses": 6,
                "equipo_recomendado": 3,
                "confianza": 0.3
            }
    
    async def generate_project_recommendations(self, proceso_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generar recomendaciones de proyecto"""
        
        prompt = f"""
        Basándote en este proceso de contratación pública peruana, genera recomendaciones para un proyecto de software.
        
        Proceso: {proceso_data.get('objeto_contratacion', 'N/A')}
        Descripción: {proceso_data.get('descripcion', 'N/A')}
        Entidad: {proceso_data.get('entidad_nombre', 'N/A')}
        Monto: {proceso_data.get('monto_referencial', 'N/A')} {proceso_data.get('moneda', '')}
        Categoría TI: {proceso_data.get('categoria_proyecto', 'N/A')}
        
        Como experto en ingeniería de software en Perú, proporciona:
        
        1. **MVP (Producto Mínimo Viable)**: Funcionalidades esenciales para la primera versión
        2. **Sprint 1**: Tareas específicas para las primeras 2-3 semanas
        3. **Stack Tecnológico**: Tecnologías recomendadas considerando el contexto peruano
        4. **Consideraciones Especiales**: Aspectos únicos del sector público peruano
        
        Responde en formato JSON:
        {{
            "mvp": {{
                "funcionalidades": ["func1", "func2"],
                "descripcion": "descripción del MVP",
                "tiempo_estimado": "semanas"
            }},
            "sprint1": {{
                "tareas": ["tarea1", "tarea2"],
                "entregables": ["entregable1", "entregable2"],
                "duracion_semanas": número
            }},
            "stack_tecnologico": {{
                "frontend": ["tech1", "tech2"],
                "backend": ["tech1", "tech2"],
                "base_datos": "tecnología",
                "justificacion": "por qué estas tecnologías"
            }},
            "consideraciones_especiales": ["aspecto1", "aspecto2"],
            "riesgos_identificados": ["riesgo1", "riesgo2"],
            "presupuesto_estimado_soles": número
        }}
        """
        
        try:
            response = await self.generate_content(prompt)
            result = json.loads(response)
            result["generado_por"] = self.model_name
            result["fecha_generacion"] = datetime.now().isoformat()
            result["confianza"] = 0.85
            return result
        except json.JSONDecodeError:
            logger.error(f"Error parseando recomendaciones: {response}")
            return self._get_default_recommendations()
    
    async def extract_requirements(self, proceso_text: str) -> Dict[str, Any]:
        """Extraer requerimientos técnicos del texto del proceso"""
        
        prompt = f"""
        Analiza el siguiente texto de un proceso de contratación pública y extrae los requerimientos técnicos específicos.
        
        Texto: {proceso_text}
        
        Identifica y categoriza:
        
        1. **Requerimientos Funcionales**: Qué debe hacer el sistema
        2. **Requerimientos No Funcionales**: Rendimiento, seguridad, usabilidad
        3. **Tecnologías Mencionadas**: Tecnologías específicas requeridas
        4. **Integraciones**: Sistemas externos con los que debe conectarse
        5. **Usuarios Objetivo**: Quiénes usarán el sistema
        
        Responde en formato JSON:
        {{
            "requerimientos_funcionales": ["req1", "req2"],
            "requerimientos_no_funcionales": ["req1", "req2"],
            "tecnologias_mencionadas": ["tech1", "tech2"],
            "integraciones_requeridas": ["sistema1", "sistema2"],
            "usuarios_objetivo": ["tipo_usuario1", "tipo_usuario2"],
            "alcance_geografico": "local|regional|nacional",
            "nivel_criticidad": "bajo|medio|alto"
        }}
        """
        
        try:
            response = await self.generate_content(prompt)
            return json.loads(response)
        except json.JSONDecodeError:
            logger.error(f"Error parseando requerimientos: {response}")
            return {
                "requerimientos_funcionales": [],
                "requerimientos_no_funcionales": [],
                "tecnologias_mencionadas": [],
                "integraciones_requeridas": [],
                "usuarios_objetivo": [],
                "alcance_geografico": "local",
                "nivel_criticidad": "medio"
            }
    
    async def answer_query_with_context(
        self, 
        query: str, 
        context_processes: List[Dict[str, Any]],
        max_context_length: int = 4000
    ) -> Dict[str, Any]:
        """Responder consulta usando contexto de procesos"""
        
        # Preparar contexto
        context_text = self._prepare_context(context_processes, max_context_length)
        
        prompt = f"""
        Eres un asistente especializado en contratación pública peruana y proyectos de software.
        
        CONTEXTO (procesos SEACE relevantes):
        {context_text}
        
        RESTRICCIONES:
        - Solo responde sobre contratación pública peruana y oportunidades de TI
        - Cita siempre las fuentes (ID de proceso) cuando uses información específica
        - Si no tienes información suficiente, dilo claramente
        - No inventes datos o estadísticas
        
        CONSULTA DEL USUARIO: {query}
        
        Proporciona una respuesta útil y precisa. Si recomiendas algún proyecto, incluye:
        - Justificación basada en los datos del contexto
        - Referencias específicas a los procesos mencionados
        - Recomendaciones prácticas para ingenieros de sistemas
        
        Responde en formato JSON:
        {{
            "respuesta": "respuesta detallada",
            "fuentes_citadas": ["id_proceso1", "id_proceso2"],
            "recomendaciones": ["rec1", "rec2"],
            "confianza": 0.0-1.0
        }}
        """
        
        try:
            response = await self.generate_content(prompt)
            
            # Limpiar la respuesta de markdown si existe
            cleaned_response = response.strip()
            if cleaned_response.startswith("```json"):
                cleaned_response = cleaned_response[7:]  # Remover ```json
            if cleaned_response.endswith("```"):
                cleaned_response = cleaned_response[:-3]  # Remover ```
            cleaned_response = cleaned_response.strip()
            
            result = json.loads(cleaned_response)
            result["modelo_usado"] = self.model_name
            result["timestamp"] = datetime.now().isoformat()
            return result
        except json.JSONDecodeError as e:
            logger.error(f"Error parseando respuesta del chatbot: {response}")
            logger.error(f"JSON Error: {str(e)}")
            return {
                "respuesta": "Lo siento, hubo un error procesando tu consulta. Por favor, intenta reformular tu pregunta.",
                "fuentes_citadas": [],
                "recomendaciones": [],
                "confianza": 0.0,
                "modelo_usado": self.model_name,
                "timestamp": datetime.now().isoformat()
            }
    
    def _prepare_context(self, processes: List[Dict[str, Any]], max_length: int) -> str:
        """Preparar contexto de procesos para el prompt"""
        
        context_parts = []
        current_length = 0
        
        for process in processes:
            process_text = f"""
ID: {process.get('id_proceso', 'N/A')}
Título: {process.get('objeto_contratacion', 'N/A')}
Entidad: {process.get('entidad_nombre', 'N/A')}
Monto: {process.get('monto_referencial', 'N/A')} {process.get('moneda', '')}
Estado: {process.get('estado_proceso', 'N/A')}
Categoría: {process.get('categoria_proyecto', 'N/A')}
---
"""
            
            if current_length + len(process_text) > max_length:
                break
                
            context_parts.append(process_text)
            current_length += len(process_text)
        
        return "\n".join(context_parts)
    
    def _get_default_recommendations(self) -> Dict[str, Any]:
        """Recomendaciones por defecto en caso de error"""
        return {
            "mvp": {
                "funcionalidades": ["Autenticación de usuarios", "Gestión básica de datos", "Reportes simples"],
                "descripcion": "Sistema básico con funcionalidades esenciales",
                "tiempo_estimado": "4-6 semanas"
            },
            "sprint1": {
                "tareas": ["Configurar entorno de desarrollo", "Diseñar base de datos", "Implementar autenticación"],
                "entregables": ["Prototipo de login", "Modelo de datos", "Documentación técnica"],
                "duracion_semanas": 2
            },
            "stack_tecnologico": {
                "frontend": ["React", "TailwindCSS"],
                "backend": ["Python", "FastAPI"],
                "base_datos": "PostgreSQL",
                "justificacion": "Stack moderno y escalable, apropiado para sector público"
            },
            "consideraciones_especiales": [
                "Cumplimiento con normativas del sector público peruano",
                "Implementar medidas de seguridad robustas",
                "Considerar accesibilidad web"
            ],
            "riesgos_identificados": [
                "Cambios en requerimientos durante desarrollo",
                "Integración con sistemas legacy del estado"
            ],
            "presupuesto_estimado_soles": 150000,
            "generado_por": "default",
            "fecha_generacion": datetime.now().isoformat(),
            "confianza": 0.5
        }
