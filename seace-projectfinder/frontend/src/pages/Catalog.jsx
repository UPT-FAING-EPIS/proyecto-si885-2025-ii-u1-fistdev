import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { 
  MagnifyingGlassIcon, 
  FunnelIcon,
  DocumentTextIcon,
  CalendarIcon,
  CurrencyDollarIcon,
  BuildingOfficeIcon,
  ChatBubbleLeftRightIcon
} from '@heroicons/react/24/outline';
import { useProcesos, useSearchProcesos } from '../hooks/useProcesos';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { LoadingSpinner, LoadingList } from '../components/ui/Loading';
import { ErrorAlert } from '../components/ui/Alert';
import { Pagination } from '../components/ui/Pagination';
import { utils } from '../services/seaceService';
import { Chatbot } from './Chatbot';

export const Catalog = () => {
  const [filters, setFilters] = useState({
    tipo_proceso: '',
    estado: '',
    entidad: '',
    fecha_desde: '',
    fecha_hasta: '',
    monto_min: '',
    monto_max: '',
    es_ti: false
  });

  const [isChatbotOpen, setIsChatbotOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [showFilters, setShowFilters] = useState(false);
  const [currentPage, setCurrentPage] = useState(1);

  const { 
    procesos, 
    loading, 
    error, 
    pagination, 
    fetchProcesos 
  } = useProcesos();

  const {
    results: searchResults,
    loading: searchLoading,
    error: searchError,
    search,
    clearResults
  } = useSearchProcesos();

  // Debounced search
  const debouncedSearch = utils.debounce((query) => {
    if (query.trim()) {
      search(query, { page: 1, limit: 20 });
    } else {
      clearResults();
    }
  }, 500);

  useEffect(() => {
    debouncedSearch(searchQuery);
  }, [searchQuery]);

  const handleFilterChange = (key, value) => {
    setFilters(prev => ({ ...prev, [key]: value }));
  };

  const applyFilters = () => {
    const params = {
      page: 1,
      limit: 20,
      ...filters
    };
    
    // Limpiar parámetros vacíos
    Object.keys(params).forEach(key => {
      if (params[key] === '' || params[key] === false) {
        delete params[key];
      }
    });

    fetchProcesos(params);
    setCurrentPage(1);
  };

  const clearFilters = () => {
    setFilters({
      tipo_proceso: '',
      estado: '',
      entidad: '',
      fecha_desde: '',
      fecha_hasta: '',
      monto_min: '',
      monto_max: '',
      es_ti: false
    });
    fetchProcesos({ page: 1, limit: 20 });
    setCurrentPage(1);
  };

  const handlePageChange = (page) => {
    setCurrentPage(page);
    fetchProcesos({ 
      page, 
      limit: 20,
      ...filters 
    });
  };

  const displayProcesos = searchQuery.trim() ? searchResults : procesos;
  const isSearchMode = searchQuery.trim().length > 0;

  return (
    <div className="min-h-full">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8 animate-fade-in">
          <h1 className="text-4xl font-bold text-gray-900 mb-2 drop-shadow-sm">
            Catálogo de Procesos SEACE
          </h1>
          <p className="text-gray-600 text-lg">
            Explora y busca procesos de contratación pública con inteligencia artificial
          </p>
        </div>

        {/* Search and Filters */}
        <Card className="mb-6 shadow-2xl border-0 bg-white/95 backdrop-blur-sm animate-slide-up">
          <div className="space-y-4">
          {/* Search Bar */}
          <div className="relative">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <MagnifyingGlassIcon className="h-5 w-5 text-gray-400" />
            </div>
            <input
              type="text"
              placeholder="Buscar por objeto, entidad, código..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md leading-5 bg-white placeholder-gray-500 focus:outline-none focus:placeholder-gray-400 focus:ring-1 focus:ring-seace-blue focus:border-seace-blue"
            />
            {(searchLoading || loading) && (
              <div className="absolute inset-y-0 right-0 pr-3 flex items-center">
                <LoadingSpinner size="sm" />
              </div>
            )}
          </div>

          {/* Filter Toggle */}
          <div className="flex justify-between items-center">
            <Button
              variant="outline"
              onClick={() => setShowFilters(!showFilters)}
              className="flex items-center"
            >
              <FunnelIcon className="w-4 h-4 mr-2" />
              {showFilters ? 'Ocultar Filtros' : 'Mostrar Filtros'}
            </Button>
            
            {isSearchMode && (
              <div className="text-sm text-gray-600">
                Resultados de búsqueda para: "{searchQuery}"
              </div>
            )}
          </div>

          {/* Filters Panel */}
          {showFilters && (
            <div className="border-t pt-4">
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Tipo de Proceso
                  </label>
                  <select
                    value={filters.tipo_proceso}
                    onChange={(e) => handleFilterChange('tipo_proceso', e.target.value)}
                    className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-1 focus:ring-seace-blue focus:border-seace-blue"
                  >
                    <option value="">Todos</option>
                    <option value="LP">Licitación Pública</option>
                    <option value="CP">Concurso Público</option>
                    <option value="ADS">Adjudicación Directa Selectiva</option>
                    <option value="ADU">Adjudicación Directa de Urgencia</option>
                    <option value="ME">Menor Cuantía</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Estado
                  </label>
                  <select
                    value={filters.estado}
                    onChange={(e) => handleFilterChange('estado', e.target.value)}
                    className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-1 focus:ring-seace-blue focus:border-seace-blue"
                  >
                    <option value="">Todos</option>
                    <option value="En proceso">En proceso</option>
                    <option value="Adjudicado">Adjudicado</option>
                    <option value="Desierto">Desierto</option>
                    <option value="Cancelado">Cancelado</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Fecha Desde
                  </label>
                  <input
                    type="date"
                    value={filters.fecha_desde}
                    onChange={(e) => handleFilterChange('fecha_desde', e.target.value)}
                    className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-1 focus:ring-seace-blue focus:border-seace-blue"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Fecha Hasta
                  </label>
                  <input
                    type="date"
                    value={filters.fecha_hasta}
                    onChange={(e) => handleFilterChange('fecha_hasta', e.target.value)}
                    className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-1 focus:ring-seace-blue focus:border-seace-blue"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Monto Mínimo (S/)
                  </label>
                  <input
                    type="number"
                    placeholder="0"
                    value={filters.monto_min}
                    onChange={(e) => handleFilterChange('monto_min', e.target.value)}
                    className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-1 focus:ring-seace-blue focus:border-seace-blue"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Monto Máximo (S/)
                  </label>
                  <input
                    type="number"
                    placeholder="9999999"
                    value={filters.monto_max}
                    onChange={(e) => handleFilterChange('monto_max', e.target.value)}
                    className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-1 focus:ring-seace-blue focus:border-seace-blue"
                  />
                </div>

                <div className="flex items-center">
                  <input
                    type="checkbox"
                    id="es_ti"
                    checked={filters.es_ti}
                    onChange={(e) => handleFilterChange('es_ti', e.target.checked)}
                    className="h-4 w-4 text-seace-blue focus:ring-seace-blue border-gray-300 rounded"
                  />
                  <label htmlFor="es_ti" className="ml-2 block text-sm text-gray-700">
                    Solo procesos TI
                  </label>
                </div>
              </div>

              <div className="flex justify-end space-x-2 mt-4">
                <Button variant="outline" onClick={clearFilters}>
                  Limpiar
                </Button>
                <Button onClick={applyFilters}>
                  Aplicar Filtros
                </Button>
              </div>
            </div>
          )}
        </div>
      </Card>

      {/* Error Handling */}
      {(error || searchError) && (
        <ErrorAlert 
          error={error || searchError} 
          onDismiss={() => {}} 
        />
      )}

      {/* Results */}
      {loading || searchLoading ? (
        <LoadingList items={6} />
      ) : (
        <>
          {displayProcesos.length > 0 ? (
            <div className="space-y-4">
              {displayProcesos.map((proceso) => (
                <ProcessCard key={proceso.id} proceso={proceso} />
              ))}
            </div>
          ) : (
            <Card className="text-center py-12">
              <DocumentTextIcon className="mx-auto h-12 w-12 text-gray-400 mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">
                No se encontraron procesos
              </h3>
              <p className="text-gray-600">
                {isSearchMode 
                  ? 'Intenta con otros términos de búsqueda o ajusta los filtros.'
                  : 'No hay procesos que coincidan con los filtros aplicados.'
                }
              </p>
            </Card>
          )}

          {/* Pagination */}
          {!isSearchMode && pagination.totalPages > 1 && (
            <div className="mt-8">
              <Pagination
                currentPage={pagination.page}
                totalPages={pagination.totalPages}
                totalItems={pagination.total}
                pageSize={pagination.limit}
                onPageChange={handlePageChange}
                showInfo={true}
              />
            </div>
          )}
        </>
      )}
      </div>

      {/* Floating Chatbot Button */}
      <div className="fixed bottom-8 right-8 z-50">
        {!isChatbotOpen ? (
          <button
            onClick={() => setIsChatbotOpen(true)}
            className="group relative bg-gradient-to-r from-seace-blue to-seace-blue-dark hover:from-seace-blue-dark hover:to-seace-blue text-white p-4 rounded-full shadow-2xl transition-all duration-300 transform hover:scale-110 hover:shadow-3xl"
          >
            <ChatBubbleLeftRightIcon className="w-6 h-6" />
            <div className="absolute -top-2 -right-2 w-3 h-3 bg-seace-green rounded-full animate-pulse"></div>
            
            {/* Tooltip */}
            <div className="absolute bottom-full right-0 mb-2 px-3 py-2 bg-gray-900 text-white text-sm rounded-lg opacity-0 group-hover:opacity-100 transition-opacity duration-200 whitespace-nowrap">
              Pregúntame sobre procesos SEACE
              <div className="absolute top-full right-3 w-0 h-0 border-l-2 border-r-2 border-t-4 border-transparent border-t-gray-900"></div>
            </div>
          </button>
        ) : (
          <div className="bg-white rounded-2xl shadow-2xl border border-gray-200 w-96 h-[600px] flex flex-col animate-slide-up overflow-hidden">
            {/* Header */}
            <div className="flex items-center justify-between p-4 border-b bg-gradient-to-r from-seace-blue to-seace-blue-dark text-white rounded-t-2xl">
              <div className="flex items-center space-x-3">
                <div className="w-8 h-8 bg-white/20 rounded-full flex items-center justify-center">
                  <ChatBubbleLeftRightIcon className="w-4 h-4" />
                </div>
                <div>
                  <h3 className="font-semibold text-sm">Asistente SEACE IA</h3>
                  <p className="text-xs text-seace-blue-light">Consulta procesos públicos</p>
                </div>
              </div>
              <button
                onClick={() => setIsChatbotOpen(false)}
                className="text-white/80 hover:text-white transition-colors p-1 rounded-full hover:bg-white/10"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            
            {/* Chat Content */}
            <div className="flex-1 overflow-hidden">
              <Chatbot />
            </div>
            
            {/* Status Bar */}
            <div className="px-4 py-2 bg-gray-50 border-t text-center">
              <p className="text-xs text-gray-500">
                ✨ Potenciado por Gemini AI
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

const ProcessCard = ({ proceso }) => {
  return (
    <Card hover className="transition-all duration-300 transform hover:scale-[1.02] shadow-lg hover:shadow-2xl bg-white border-l-4 border-seace-blue animate-fade-in">
      <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between">
        <div className="flex-1">
          <div className="flex items-start justify-between mb-2">
            <h3 className="text-lg font-semibold text-seace-blue-dark hover:text-seace-blue transition-colors">
              <Link to={`/process/${proceso.id}`}>
                {utils.truncateText(proceso.objeto_contratacion, 100)}
              </Link>
            </h3>
            {proceso.categoria_proyecto === 'TI' && (
              <span className="ml-2 inline-flex items-center px-3 py-1 rounded-full text-xs font-bold bg-seace-green text-white shadow-md animate-pulse">
                TI
              </span>
            )}
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm text-seace-gray-dark">
            <div className="flex items-center">
              <DocumentTextIcon className="w-4 h-4 mr-2 text-seace-blue" />
              <span className="font-medium">{proceso.id_proceso}</span>
            </div>
            <div className="flex items-center">
              <BuildingOfficeIcon className="w-4 h-4 mr-2 text-seace-blue" />
              <span>{utils.truncateText(proceso.entidad_nombre, 40)}</span>
            </div>
            <div className="flex items-center">
              <CalendarIcon className="w-4 h-4 mr-2 text-seace-blue" />
              <span>{utils.formatDateShort(proceso.fecha_publicacion)}</span>
            </div>
            <div className="flex items-center">
              <CurrencyDollarIcon className="w-4 h-4 mr-2 text-seace-blue" />
              <span className="font-semibold">{utils.formatCurrency(proceso.monto_referencial, proceso.moneda)}</span>
            </div>
          </div>
        </div>
        
        <div className="mt-4 lg:mt-0 lg:ml-6 flex flex-col lg:items-end">
          <span className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-bold mb-2 shadow-md ${
            proceso.estado_proceso === 'Adjudicado' ? 'bg-seace-green text-white' :
            proceso.estado_proceso === 'En proceso' ? 'bg-seace-blue text-white' :
            proceso.estado_proceso === 'Desierto' ? 'bg-seace-orange text-white' :
            'bg-seace-gray text-white'
          }`}>
            {proceso.estado_proceso || 'En proceso'}
          </span>
          
          <Button variant="outline" size="sm" asChild className="border-seace-blue text-seace-blue hover:bg-seace-blue hover:text-white transition-all duration-200">
            <Link to={`/process/${proceso.id}`}>
              Ver Detalle
            </Link>
          </Button>
        </div>
      </div>
    </Card>
  );
};
