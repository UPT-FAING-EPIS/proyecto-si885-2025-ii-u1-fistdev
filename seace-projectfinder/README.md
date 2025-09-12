# SEACE ProjectFinder

Una plataforma inteligente para el análisis y búsqueda de procesos de contratación del Sistema Electrónico de Contrataciones del Estado (SEACE).

## 🎯 Descripción del Proyecto

SEACE ProjectFinder es una aplicación web desarrollada como proyecto de Inteligencia de Negocios que utiliza tecnologías de vanguardia para facilitar el análisis y búsqueda de procesos de contratación pública en el Perú. La plataforma integra técnicas de web scraping, procesamiento de lenguaje natural y análisis de datos para ofrecer una experiencia de usuario moderna e intuitiva.

### Características Principales

- **🔍 Catálogo Avanzado**: Búsqueda y filtrado inteligente de procesos SEACE
- **🤖 Asistente IA**: Chatbot con Google Gemini para consultas en lenguaje natural
- **📊 Dashboard Analítico**: Visualización interactiva de datos con Power BI
- **⚡ Recomendaciones IA**: Sugerencias automatizadas para procesos TI
- **🎯 Enfoque TI**: Especialización en procesos de tecnologías de información

### Base de Datos (PostgreSQL)
- **Procesos**: Información completa de procesos SEACE
- **Embeddings**: Vectores para búsqueda semántica
- **Recomendaciones**: Sugerencias generadas por IA
- **Logs**: Registro de interacciones del chatbot

## 🚀 Stack Tecnológico

### Backend
- **Python 3.11+** - Lenguaje principal
- **FastAPI** - Framework web moderno y rápido
- **SQLAlchemy** - ORM para manejo de base de datos
- **PostgreSQL** - Base de datos principal
- **pgvector** - Extensión para búsqueda vectorial
- **Google Gemini AI** - API para procesamiento de lenguaje natural
- **BeautifulSoup** - Web scraping de datos SEACE
- **Alembic** - Migraciones de base de datos

### Frontend
- **React 18** - Biblioteca de UI
- **Vite** - Herramienta de build moderna
- **TailwindCSS** - Framework de CSS utilitario
- **React Router** - Enrutamiento del lado del cliente
- **Axios** - Cliente HTTP
- **Heroicons** - Iconografía

### DevOps & Deployment
- **Docker** - Containerización
- **Docker Compose** - Orquestación de contenedores
- **Nginx** - Servidor web para producción

## 📋 Requisitos Previos

- **Docker** y **Docker Compose**
- **Node.js 18+** (para desarrollo del frontend)
- **Python 3.11+** (para desarrollo del backend)
- **PostgreSQL 15+** (si se ejecuta localmente)

## 🛠️ Instalación y Configuración

### 1. Clonar el Repositorio
```bash
git clone <repository-url>
cd seace-projectfinder
```

### 2. Configuración con Docker (Recomendado)

#### Variables de Entorno
Crear archivo `.env` en la raíz del proyecto:
```env
# Base de datos
DATABASE_URL=postgresql://seace_user:seace_password@db:5432/seace_db
POSTGRES_USER=seace_user
POSTGRES_PASSWORD=seace_password
POSTGRES_DB=seace_db

# Google Gemini API
GOOGLE_API_KEY=tu_api_key_aqui

# Configuración de la aplicación
SECRET_KEY=tu_secret_key_super_seguro_aqui
DEBUG=False
ENVIRONMENT=production

# SEACE URLs
SEACE_BASE_URL=https://www.seace.gob.pe
OSCE_API_URL=https://api.osce.gob.pe
```

#### Ejecutar con Docker Compose
```bash
# Construir y ejecutar todos los servicios
docker-compose up --build

# Ejecutar en segundo plano
docker-compose up -d
```

### 3. Configuración Manual (Desarrollo)

#### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tus configuraciones

# Ejecutar migraciones
alembic upgrade head

# Iniciar servidor de desarrollo
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend
```bash
cd frontend
npm install

# Iniciar servidor de desarrollo
npm run dev
```

## 🎮 Uso de la Aplicación

### Acceso Local
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **Documentación API**: http://localhost:8000/docs

### Funcionalidades Principales

#### 1. Catálogo de Procesos
- Explorar procesos de contratación pública
- Filtros avanzados por tipo, estado, fecha, monto
- Búsqueda de texto completo
- Visualización detallada de cada proceso

#### 2. Asistente IA
- Consultas en lenguaje natural
- Recomendaciones inteligentes
- Búsqueda semántica en procesos
- Historial de conversaciones

#### 3. Dashboard Analítico
- Estadísticas en tiempo real
- Visualizaciones interactivas
- Análisis de tendencias
- Métricas por entidad y tipo

#### 4. Panel de Administración
- Sincronización de datos SEACE
- Generación de embeddings
- Monitoreo del sistema
- Estadísticas de uso

## 📚 Estructura de la API

### Endpoints Principales

#### Procesos
- `GET /api/v1/procesos` - Lista procesos con filtros
- `GET /api/v1/procesos/{id}` - Detalle de proceso
- `GET /api/v1/procesos/search/text` - Búsqueda de texto
- `GET /api/v1/procesos/stats/overview` - Estadísticas

#### Chatbot
- `POST /api/v1/chatbot/query` - Consulta al asistente IA
- `GET /api/v1/chatbot/suggestions` - Sugerencias de consultas
- `GET /api/v1/chatbot/session/{id}/history` - Historial

#### Recomendaciones
- `GET /api/v1/recomendaciones/{proceso_id}` - Obtener recomendaciones
- `POST /api/v1/recomendaciones/{proceso_id}/generate` - Generar nuevas
- `GET /api/v1/recomendaciones/{proceso_id}/mvp` - Recomendación MVP

#### Administración
- `POST /api/v1/admin/etl/sync-daily` - Sincronización diaria
- `POST /api/v1/admin/etl/sync-full` - Sincronización completa
- `GET /api/v1/admin/status/health` - Estado del sistema

## 🧪 Testing

### Backend
```bash
cd backend
pytest tests/ -v
pytest tests/ --cov=app
```

### Frontend
```bash
cd frontend
npm test
npm run test:coverage
```

## 🚀 Deployment

### Producción con Docker
```bash
# Variables de entorno de producción
cp .env.example .env.production
# Configurar valores de producción

# Deploy
docker-compose -f docker-compose.prod.yml up -d
```

### Consideraciones de Producción
- Usar HTTPS con certificados SSL
- Configurar límites de rate limiting
- Implementar monitoreo y logging
- Backup automático de la base de datos
- Optimizar configuración de PostgreSQL

## 📊 Monitoreo y Logs

### Logs de Aplicación
```bash
# Backend logs
docker-compose logs backend

# Frontend logs
docker-compose logs frontend

# Base de datos logs
docker-compose logs db
```

### Métricas del Sistema
- Uso de CPU y memoria
- Tiempo de respuesta de API
- Estadísticas de uso del chatbot
- Frecuencia de sincronización ETL

## 🤝 Contribución

### Desarrollo Local
1. Fork del repositorio
2. Crear rama feature: `git checkout -b feature/nueva-funcionalidad`
3. Commit cambios: `git commit -am 'Agrega nueva funcionalidad'`
4. Push a la rama: `git push origin feature/nueva-funcionalidad`
5. Crear Pull Request

### Estándares de Código
- **Python**: PEP 8, Black formatting
- **JavaScript**: ESLint + Prettier
- **Commits**: Conventional Commits format
- **Tests**: Cobertura mínima del 80%

## 🎓 Contexto Académico

### Universidad
**Universidad Privada de Tacna (UPT)**
- Carrera: Ingeniería de Sistemas
- Asignatura: Inteligencia de Negocios
- Ciclo: VIII

### Objetivos Educativos
- Aplicar técnicas de inteligencia de negocios
- Integrar tecnologías de IA y machine learning
- Desarrollar soluciones prácticas para el sector público
- Crear valor mediante análisis de datos

## 📄 Licencia

Este proyecto es desarrollado con fines académicos como parte del curso de Inteligencia de Negocios de la Universidad Privada de Tacna.

## 📞 Soporte

Para consultas técnicas o académicas, contactar a:
- **Desarrollo**: [correo-desarrollador]
- **Académico**: [correo-profesor]
- **Universidad**: https://www.upt.edu.pe

## 🔗 Enlaces Útiles

- **SEACE**: https://www.seace.gob.pe
- **OSCE**: https://www.osce.gob.pe
- **Google Gemini AI**: https://ai.google.dev
- **FastAPI Docs**: https://fastapi.tiangolo.com
- **React Docs**: https://react.dev

---

**Última actualización**: Diciembre 2024  
**Versión**: 1.0.0  
**Estado**: Desarrollo Activo 🚧

Prefijo de la API: /api/v1

URLs principales:

Documentación Swagger: http://localhost:8001/api/v1/docs
ReDoc: http://localhost:8001/api/v1/redoc
OpenAPI JSON: http://localhost:8001/api/v1/openapi.json
Health check: http://localhost:8001/health
Root info: http://localhost:8001/