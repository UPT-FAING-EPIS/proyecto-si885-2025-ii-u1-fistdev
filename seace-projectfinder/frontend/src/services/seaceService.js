import api from './api';

// Servicios para procesos
export const procesosService = {
  // Obtener lista de procesos con filtros y paginación
  getList: async (params = {}) => {
    try {
      const response = await api.get('/procesos/', { params });
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.message || 'Error obteniendo procesos');
    }
  },

  // Obtener detalle de un proceso
  getById: async (procesoId) => {
    try {
      const response = await api.get(`/procesos/${procesoId}`);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.message || 'Error obteniendo proceso');
    }
  },

  // Obtener anexos de un proceso (no implementado aún)
  getAnexos: async (procesoId) => {
    try {
      return [];
    } catch (error) {
      throw new Error(error.response?.data?.message || 'Error obteniendo anexos');
    }
  },

  // Búsqueda de texto en procesos
  search: async (query, params = {}) => {
    try {
      const response = await api.get('/procesos/search/text', {
        params: { q: query, ...params }
      });
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.message || 'Error en búsqueda');
    }
  },

  // Obtener estadísticas de procesos
  getStats: async () => {
    try {
      const response = await api.get('/procesos/stats/overview');
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.message || 'Error obteniendo estadísticas');
    }
  },

  // Obtener procesos TI más recientes (simplificado)
  getLatestTI: async (limit = 10) => {
    try {
      const response = await api.get('/procesos/', {
        params: { 
          limit,
          categoria_proyecto: 'TI',
          sort_by: 'fecha_publicacion',
          sort_order: 'desc'
        }
      });
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.message || 'Error obteniendo procesos TI');
    }
  }
};

// Servicios para chatbot
export const chatbotService = {
  // Enviar consulta al chatbot
  query: async (queryData) => {
    try {
      const response = await api.post('/chatbot/query', queryData);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.message || 'Error en consulta del chatbot');
    }
  },

  // Obtener sugerencias de consultas
  getSuggestions: async () => {
    try {
      const response = await api.get('/chatbot/suggestions');
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.message || 'Error obteniendo sugerencias');
    }
  },

  // Obtener historial de una sesión
  getSessionHistory: async (sessionId) => {
    try {
      const response = await api.get(`/chatbot/session/${sessionId}/history`);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.message || 'Error obteniendo historial');
    }
  },

  // Obtener estadísticas de uso del chatbot
  getStats: async () => {
    try {
      const response = await api.get('/chatbot/stats/usage');
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.message || 'Error obteniendo estadísticas del chatbot');
    }
  }
};

// Servicios para recomendaciones
export const recomendacionesService = {
  // Obtener recomendaciones de un proceso
  getByProceso: async (procesoId) => {
    try {
      const response = await api.get(`/recomendaciones/${procesoId}`);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.message || 'Error obteniendo recomendaciones');
    }
  },

  // Generar recomendaciones para un proceso
  generate: async (procesoId, forceRegenerate = false) => {
    try {
      const response = await api.post(`/recomendaciones/${procesoId}/generate`, null, {
        params: { force_regenerate: forceRegenerate }
      });
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.message || 'Error generando recomendaciones');
    }
  },

  // Obtener recomendación específica de MVP
  getMVP: async (procesoId) => {
    try {
      const response = await api.get(`/recomendaciones/${procesoId}/mvp`);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.message || 'Error obteniendo MVP');
    }
  },

  // Obtener recomendación específica de Sprint 1
  getSprint1: async (procesoId) => {
    try {
      const response = await api.get(`/recomendaciones/${procesoId}/sprint1`);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.message || 'Error obteniendo Sprint 1');
    }
  },

  // Obtener recomendación de stack tecnológico
  getStackTech: async (procesoId) => {
    try {
      const response = await api.get(`/recomendaciones/${procesoId}/stack-tech`);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.message || 'Error obteniendo stack tecnológico');
    }
  },

  // Limpiar recomendaciones de un proceso
  clear: async (procesoId) => {
    try {
      const response = await api.delete(`/recomendaciones/${procesoId}/clear`);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.message || 'Error limpiando recomendaciones');
    }
  }
};

// Servicios para dashboard
export const dashboardService = {
  // Obtener URL del dashboard Power BI
  getUrl: async () => {
    try {
      const response = await api.get('/dashboard/dashboard');
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.message || 'Error obteniendo dashboard');
    }
  },

  // Obtener configuración del dashboard
  getConfig: async () => {
    try {
      const response = await api.get('/dashboard/dashboard/config');
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.message || 'Error obteniendo configuración');
    }
  }
};

// Servicios de administración
export const adminService = {
  // Ejecutar sincronización diaria
  runDailySync: async () => {
    try {
      const response = await api.post('/admin/etl/sync-daily');
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.message || 'Error en sincronización diaria');
    }
  },

  // Ejecutar sincronización completa
  runFullSync: async (daysBack = 365) => {
    try {
      const response = await api.post('/admin/etl/sync-full', null, {
        params: { days_back: daysBack }
      });
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.message || 'Error en sincronización completa');
    }
  },

  // Ejecutar sincronización TI
  runTISync: async () => {
    try {
      const response = await api.post('/admin/etl/sync-ti');
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.message || 'Error en sincronización TI');
    }
  },

  // Generar embeddings
  generateEmbeddings: async (batchSize = 50) => {
    try {
      const response = await api.post('/admin/nlp/generate-embeddings', null, {
        params: { batch_size: batchSize }
      });
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.message || 'Error generando embeddings');
    }
  },

  // Obtener estado del ETL
  getETLStatus: async () => {
    try {
      const response = await api.get('/admin/status/etl');
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.message || 'Error obteniendo estado ETL');
    }
  },

  // Verificación de salud
  healthCheck: async () => {
    try {
      const response = await api.get('/admin/status/health');
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.message || 'Error en verificación de salud');
    }
  },

  // Estado del sistema
  getSystemStatus: async () => {
    try {
      const response = await api.get('/admin/status/system');
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.message || 'Error obteniendo estado del sistema');
    }
  }
};

// Utilidades
export const utils = {
  // Formatear moneda peruana
  formatCurrency: (amount, currency = 'PEN') => {
    if (!amount) return 'No especificado';
    
    const formatter = new Intl.NumberFormat('es-PE', {
      style: 'currency',
      currency: currency === 'PEN' ? 'PEN' : 'USD',
      minimumFractionDigits: 2
    });
    
    return formatter.format(amount);
  },

  // Formatear fecha
  formatDate: (dateString) => {
    if (!dateString) return 'No especificado';
    
    const date = new Date(dateString);
    return new Intl.DateTimeFormat('es-PE', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    }).format(date);
  },

  // Formatear fecha corta
  formatDateShort: (dateString) => {
    if (!dateString) return 'No especificado';
    
    const date = new Date(dateString);
    return new Intl.DateTimeFormat('es-PE', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit'
    }).format(date);
  },

  // Truncar texto
  truncateText: (text, maxLength = 100) => {
    if (!text) return '';
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
  },

  // Generar session ID para chatbot
  generateSessionId: () => {
    return 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
  },

  // Validar email
  isValidEmail: (email) => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  },

  // Debounce para búsquedas
  debounce: (func, wait) => {
    let timeout;
    return function executedFunction(...args) {
      const later = () => {
        clearTimeout(timeout);
        func(...args);
      };
      clearTimeout(timeout);
      timeout = setTimeout(later, wait);
    };
  }
};
