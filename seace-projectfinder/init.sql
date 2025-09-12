-- Inicialización de la base de datos para SEACE ProjectFinder
-- Instalación de extensiones necesarias
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "vector";

-- Tabla para almacenar procesos SEACE
CREATE TABLE IF NOT EXISTS procesos (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    id_proceso VARCHAR(255) UNIQUE NOT NULL,
    url_proceso TEXT,
    numero_convocatoria VARCHAR(255),
    entidad_nombre VARCHAR(500),
    entidad_ruc VARCHAR(11),
    objeto_contratacion TEXT,
    tipo_proceso VARCHAR(100),
    estado_proceso VARCHAR(100),
    fecha_publicacion TIMESTAMP,
    fecha_limite_presentacion TIMESTAMP,
    monto_referencial DECIMAL(15,2),
    moneda VARCHAR(10),
    rubro VARCHAR(200),
    departamento VARCHAR(100),
    provincia VARCHAR(100),
    distrito VARCHAR(100),
    requiere_visita_previa BOOLEAN DEFAULT FALSE,
    datos_ocds JSONB,
    fecha_extraccion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    procesado_nlp BOOLEAN DEFAULT FALSE,
    complejidad_estimada VARCHAR(50),
    categoria_proyecto VARCHAR(100)
);

-- Tabla para almacenar embeddings vectoriales para RAG
CREATE TABLE IF NOT EXISTS proceso_embeddings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    proceso_id UUID REFERENCES procesos(id) ON DELETE CASCADE,
    content_type VARCHAR(50), -- 'objeto', 'descripcion', 'especificaciones'
    content_text TEXT,
    embedding vector(1536), -- Dimensión típica para embeddings de OpenAI/Gemini
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla para almacenar anexos y documentos
CREATE TABLE IF NOT EXISTS anexos (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    proceso_id UUID REFERENCES procesos(id) ON DELETE CASCADE,
    nombre_archivo VARCHAR(255),
    url_descarga TEXT,
    tipo_documento VARCHAR(100),
    tamaño_kb INTEGER,
    fecha_subida TIMESTAMP,
    procesado BOOLEAN DEFAULT FALSE,
    contenido_extraido TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla para almacenar recomendaciones generadas por IA
CREATE TABLE IF NOT EXISTS recomendaciones (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    proceso_id UUID REFERENCES procesos(id) ON DELETE CASCADE,
    tipo_recomendacion VARCHAR(100), -- 'mvp', 'sprint1', 'stack_tech', 'estimacion'
    titulo VARCHAR(255),
    descripcion TEXT,
    datos_estructurados JSONB,
    confianza_score DECIMAL(3,2), -- 0.00 a 1.00
    generated_by VARCHAR(50), -- 'gemini-2.5-flash', etc.
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla para logs de consultas al chatbot
CREATE TABLE IF NOT EXISTS chatbot_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id VARCHAR(255),
    user_query TEXT,
    ai_response TEXT,
    relevant_processes UUID[], -- Array de IDs de procesos relacionados
    response_time_ms INTEGER,
    model_used VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla para configuración del sistema
CREATE TABLE IF NOT EXISTS configuracion (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    clave VARCHAR(100) UNIQUE NOT NULL,
    valor TEXT,
    descripcion TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insertar configuraciones iniciales
INSERT INTO configuracion (clave, valor, descripcion) VALUES
('last_osce_sync', '2024-01-01 00:00:00', 'Última sincronización con datos OSCE'),
('etl_batch_size', '100', 'Tamaño de lote para procesamiento ETL'),
('gemini_model', 'gemini-2.5-flash', 'Modelo Gemini utilizado'),
('embedding_model', 'text-embedding-004', 'Modelo para generar embeddings')
ON CONFLICT (clave) DO NOTHING;

-- Índices para optimizar consultas
CREATE INDEX IF NOT EXISTS idx_procesos_estado ON procesos(estado_proceso);
CREATE INDEX IF NOT EXISTS idx_procesos_fecha_pub ON procesos(fecha_publicacion);
CREATE INDEX IF NOT EXISTS idx_procesos_rubro ON procesos(rubro);
CREATE INDEX IF NOT EXISTS idx_procesos_monto ON procesos(monto_referencial);
CREATE INDEX IF NOT EXISTS idx_procesos_id_proceso ON procesos(id_proceso);
CREATE INDEX IF NOT EXISTS idx_embeddings_proceso_id ON proceso_embeddings(proceso_id);
CREATE INDEX IF NOT EXISTS idx_anexos_proceso_id ON anexos(proceso_id);
CREATE INDEX IF NOT EXISTS idx_recomendaciones_proceso_id ON recomendaciones(proceso_id);

-- Índice vectorial para búsquedas de similitud
CREATE INDEX IF NOT EXISTS idx_embeddings_vector ON proceso_embeddings USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

-- Trigger para actualizar fecha_actualizacion
CREATE OR REPLACE FUNCTION update_fecha_actualizacion()
RETURNS TRIGGER AS $$
BEGIN
    NEW.fecha_actualizacion = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_procesos_fecha
    BEFORE UPDATE ON procesos
    FOR EACH ROW
    EXECUTE FUNCTION update_fecha_actualizacion();
