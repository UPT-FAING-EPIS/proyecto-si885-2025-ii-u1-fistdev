import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import text
from loguru import logger
import asyncio

from app.core.database import SessionLocal
from app.db.models import Proceso, ProcesoEmbedding
from app.nlp.gemini_client import GeminiClient
from app.core.exceptions import NLPException


class RAGService:
    """Servicio de Generación Aumentada por Recuperación (RAG)"""
    
    def __init__(self):
        self.gemini_client = GeminiClient()
        self.embedding_dimension = 1536  # Dimensión típica para embeddings
        
    async def generate_embeddings_for_process(self, proceso_id: str) -> Dict[str, Any]:
        """Generar embeddings para un proceso específico"""
        
        with SessionLocal() as db:
            proceso = db.query(Proceso).filter(Proceso.id == proceso_id).first()
            if not proceso:
                raise NLPException(f"Proceso no encontrado: {proceso_id}")
            
            # Preparar textos para embeddings
            texts_to_embed = self._prepare_texts_for_embedding(proceso)
            
            # Generar embeddings (simulación - en producción usaríamos una API real)
            embeddings_created = 0
            
            for content_type, text in texts_to_embed.items():
                if text and text.strip():
                    # Simular embedding (en producción usaríamos OpenAI, Cohere, etc.)
                    embedding_vector = self._simulate_embedding(text)
                    
                    # Verificar si ya existe
                    existing = db.query(ProcesoEmbedding).filter(
                        ProcesoEmbedding.proceso_id == proceso.id,
                        ProcesoEmbedding.content_type == content_type
                    ).first()
                    
                    if existing:
                        # Actualizar
                        existing.content_text = text
                        existing.embedding = self._vector_to_string(embedding_vector)
                    else:
                        # Crear nuevo
                        embedding_record = ProcesoEmbedding(
                            proceso_id=proceso.id,
                            content_type=content_type,
                            content_text=text,
                            embedding=self._vector_to_string(embedding_vector)
                        )
                        db.add(embedding_record)
                    
                    embeddings_created += 1
            
            db.commit()
            
            return {
                "proceso_id": str(proceso.id),
                "embeddings_created": embeddings_created,
                "status": "success"
            }
    
    async def search_similar_processes(
        self, 
        query: str, 
        limit: int = 5,
        similarity_threshold: float = 0.7
    ) -> List[Dict[str, Any]]:
        """Buscar procesos similares usando embeddings"""
        
        # Generar embedding para la consulta
        query_embedding = self._simulate_embedding(query)
        query_vector_str = self._vector_to_string(query_embedding)
        
        with SessionLocal() as db:
            # Buscar embeddings similares usando cosine similarity
            # Nota: En PostgreSQL con pgvector usaríamos: embedding <=> %s
            # Por ahora simulamos la búsqueda
            
            similar_processes = []
            
            # Obtener todos los embeddings (en producción optimizaríamos esto)
            embeddings = db.query(ProcesoEmbedding).join(Proceso).limit(1000).all()
            
            similarities = []
            for emb in embeddings:
                if emb.embedding:
                    emb_vector = self._string_to_vector(emb.embedding)
                    similarity = self._cosine_similarity(query_embedding, emb_vector)
                    
                    if similarity >= similarity_threshold:
                        similarities.append((similarity, emb))
            
            # Ordenar por similitud
            similarities.sort(key=lambda x: x[0], reverse=True)
            
            # Tomar los top resultados
            for similarity, embedding in similarities[:limit]:
                proceso = embedding.proceso
                
                similar_processes.append({
                    "proceso_id": str(proceso.id),
                    "id_proceso": proceso.id_proceso,
                    "objeto_contratacion": proceso.objeto_contratacion,
                    "entidad_nombre": proceso.entidad_nombre,
                    "monto_referencial": float(proceso.monto_referencial) if proceso.monto_referencial else None,
                    "estado_proceso": proceso.estado_proceso,
                    "categoria_proyecto": proceso.categoria_proyecto,
                    "similarity_score": float(similarity),
                    "matched_content": embedding.content_type
                })
            
            return similar_processes
    
    async def get_context_for_query(
        self, 
        query: str, 
        max_processes: int = 10
    ) -> List[Dict[str, Any]]:
        """Obtener contexto relevante para una consulta"""
        
        # Buscar procesos similares
        similar_processes = await self.search_similar_processes(
            query, 
            limit=max_processes,
            similarity_threshold=0.6
        )
        
        # Si no hay suficientes resultados similares, agregar algunos aleatorios
        if len(similar_processes) < max_processes // 2:
            with SessionLocal() as db:
                additional_processes = (
                    db.query(Proceso)
                    .filter(Proceso.procesado_nlp == True)
                    .order_by(Proceso.fecha_publicacion.desc())
                    .limit(max_processes - len(similar_processes))
                    .all()
                )
                
                for proceso in additional_processes:
                    # Evitar duplicados
                    if not any(p["proceso_id"] == str(proceso.id) for p in similar_processes):
                        similar_processes.append({
                            "proceso_id": str(proceso.id),
                            "id_proceso": proceso.id_proceso,
                            "objeto_contratacion": proceso.objeto_contratacion,
                            "entidad_nombre": proceso.entidad_nombre,
                            "monto_referencial": float(proceso.monto_referencial) if proceso.monto_referencial else None,
                            "estado_proceso": proceso.estado_proceso,
                            "categoria_proyecto": proceso.categoria_proyecto,
                            "similarity_score": 0.5,  # Score neutral
                            "matched_content": "general"
                        })
        
        return similar_processes
    
    async def generate_rag_response(
        self, 
        query: str, 
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generar respuesta usando RAG"""
        
        start_time = asyncio.get_event_loop().time()
        
        try:
            # Obtener contexto relevante
            context_processes = await self.get_context_for_query(query)
            
            # Generar respuesta usando Gemini con contexto
            response = await self.gemini_client.answer_query_with_context(
                query, context_processes
            )
            
            end_time = asyncio.get_event_loop().time()
            response_time_ms = int((end_time - start_time) * 1000)
            
            # Agregar metadatos
            response.update({
                "session_id": session_id or "anonymous",
                "response_time_ms": response_time_ms,
                "context_processes_count": len(context_processes),
                "relevant_process_ids": [p["proceso_id"] for p in context_processes]
            })
            
            return response
            
        except Exception as e:
            logger.error(f"Error en RAG response: {str(e)}")
            end_time = asyncio.get_event_loop().time()
            response_time_ms = int((end_time - start_time) * 1000)
            
            return {
                "respuesta": "Lo siento, ocurrió un error procesando tu consulta. Por favor, intenta nuevamente.",
                "fuentes_citadas": [],
                "recomendaciones": [],
                "confianza": 0.0,
                "session_id": session_id or "anonymous",
                "response_time_ms": response_time_ms,
                "error": str(e)
            }
    
    async def batch_generate_embeddings(self, batch_size: int = 50) -> Dict[str, Any]:
        """Generar embeddings para procesos que no los tienen"""
        
        with SessionLocal() as db:
            # Obtener procesos sin embeddings
            procesos_sin_embeddings = (
                db.query(Proceso)
                .filter(Proceso.procesado_nlp == False)
                .limit(batch_size)
                .all()
            )
            
            total_procesados = 0
            errores = 0
            
            for proceso in procesos_sin_embeddings:
                try:
                    await self.generate_embeddings_for_process(str(proceso.id))
                    
                    # Marcar como procesado
                    proceso.procesado_nlp = True
                    total_procesados += 1
                    
                except Exception as e:
                    logger.error(f"Error generando embeddings para proceso {proceso.id}: {str(e)}")
                    errores += 1
            
            db.commit()
            
            return {
                "total_procesados": total_procesados,
                "errores": errores,
                "batch_size": batch_size
            }
    
    def _prepare_texts_for_embedding(self, proceso: Proceso) -> Dict[str, str]:
        """Preparar textos del proceso para generar embeddings"""
        
        texts = {}
        
        # Objeto de contratación
        if proceso.objeto_contratacion:
            texts["objeto"] = proceso.objeto_contratacion
        
        # Descripción combinada
        descripcion_parts = []
        if proceso.objeto_contratacion:
            descripcion_parts.append(proceso.objeto_contratacion)
        if proceso.entidad_nombre:
            descripcion_parts.append(f"Entidad: {proceso.entidad_nombre}")
        if proceso.rubro:
            descripcion_parts.append(f"Rubro: {proceso.rubro}")
        
        if descripcion_parts:
            texts["descripcion"] = " | ".join(descripcion_parts)
        
        # Datos OCDS si están disponibles
        if proceso.datos_ocds:
            ocds_text_parts = []
            
            if isinstance(proceso.datos_ocds, dict):
                # Extraer campos relevantes del OCDS
                for key in ["title", "description", "tender.title", "tender.description"]:
                    value = self._get_nested_value(proceso.datos_ocds, key)
                    if value:
                        ocds_text_parts.append(str(value))
            
            if ocds_text_parts:
                texts["especificaciones"] = " | ".join(ocds_text_parts)
        
        return texts
    
    def _get_nested_value(self, data: dict, key_path: str) -> Any:
        """Obtener valor anidado usando path con puntos"""
        keys = key_path.split(".")
        current = data
        
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return None
        
        return current
    
    def _simulate_embedding(self, text: str) -> np.ndarray:
        """Simular generación de embedding (reemplazar con API real)"""
        # Esta es una simulación simple - en producción usaríamos una API real
        # como OpenAI embeddings, Cohere, o un modelo local
        
        # Generar vector pseudo-aleatorio basado en hash del texto
        import hashlib
        text_hash = hashlib.md5(text.encode()).hexdigest()
        
        # Convertir hash a números y normalizar
        numbers = [int(text_hash[i:i+2], 16) for i in range(0, len(text_hash), 2)]
        
        # Expandir a la dimensión deseada
        while len(numbers) < self.embedding_dimension:
            numbers.extend(numbers)
        
        # Tomar solo las dimensiones necesarias
        vector = np.array(numbers[:self.embedding_dimension], dtype=np.float32)
        
        # Normalizar
        vector = vector / np.linalg.norm(vector)
        
        return vector
    
    def _vector_to_string(self, vector: np.ndarray) -> str:
        """Convertir vector numpy a string para almacenamiento"""
        return ",".join(map(str, vector.tolist()))
    
    def _string_to_vector(self, vector_str: str) -> np.ndarray:
        """Convertir string a vector numpy"""
        try:
            return np.array([float(x) for x in vector_str.split(",")], dtype=np.float32)
        except:
            # Vector por defecto en caso de error
            return np.zeros(self.embedding_dimension, dtype=np.float32)
    
    def _cosine_similarity(self, a: np.ndarray, b: np.ndarray) -> float:
        """Calcular similitud coseno entre dos vectores"""
        try:
            return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))
        except:
            return 0.0
