import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { 
  ArrowLeftIcon,
  DocumentTextIcon,
  CalendarIcon,
  CurrencyDollarIcon,
  BuildingOfficeIcon,
  ClockIcon,
  PaperClipIcon,
  SparklesIcon,
  ExclamationTriangleIcon
} from '@heroicons/react/24/outline';
import { useProceso } from '../hooks/useProcesos';
import { useRecomendaciones } from '../hooks/useRecomendaciones';
import { Card, CardHeader, CardBody } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { LoadingSpinner } from '../components/ui/Loading';
import { ErrorAlert, Alert } from '../components/ui/Alert';
import { utils } from '../services/seaceService';

export const ProcessDetail = () => {
  const { id } = useParams();
  const [activeTab, setActiveTab] = useState('details');

  const { 
    proceso, 
    anexos, 
    loading, 
    error 
  } = useProceso(id);

  const {
    recomendaciones,
    loading: recomendacionesLoading,
    error: recomendacionesError,
    generating,
    generateRecomendaciones
  } = useRecomendaciones(id);

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex justify-center items-center h-64">
          <LoadingSpinner size="lg" />
        </div>
      </div>
    );
  }

  if (error || !proceso) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <ErrorAlert 
          error={error || 'Proceso no encontrado'} 
          onDismiss={() => {}} 
        />
        <div className="mt-4">
          <Button variant="outline" asChild>
            <Link to="/catalog">
              <ArrowLeftIcon className="w-4 h-4 mr-2" />
              Volver al Catálogo
            </Link>
          </Button>
        </div>
      </div>
    );
  }

  const tabs = [
    { id: 'details', name: 'Detalles', icon: DocumentTextIcon },
    { id: 'anexos', name: 'Anexos', icon: PaperClipIcon },
    { id: 'recomendaciones', name: 'Recomendaciones IA', icon: SparklesIcon }
  ];

  return (
    <div className="min-h-full">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Breadcrumb */}
        <div className="mb-6 animate-fade-in">
          <Button variant="ghost" asChild className="text-gray-600 hover:text-gray-900 hover:bg-white/50 transition-all duration-200">
            <Link to="/catalog" className="flex items-center">
              <ArrowLeftIcon className="w-4 h-4 mr-2" />
              Volver al Catálogo
            </Link>
          </Button>
        </div>

        {/* Header */}
        <div className="mb-8 animate-slide-up">
          <div className="flex items-start justify-between mb-4">
          <div className="flex-1">
            <div className="flex items-center mb-2">
              <h1 className="text-2xl font-bold text-gray-900 mr-3">
                {proceso.id_proceso}
              </h1>
              {proceso.categoria_proyecto === 'TI' && (
                <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                  TI
                </span>
              )}
              <span className={`ml-2 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                proceso.estado_proceso === 'Adjudicado' ? 'bg-green-100 text-green-800' :
                proceso.estado_proceso === 'En proceso' ? 'bg-blue-100 text-blue-800' :
                proceso.estado_proceso === 'Desierto' ? 'bg-red-100 text-red-800' :
                'bg-gray-100 text-gray-800'
              }`}>
                {proceso.estado_proceso || 'En proceso'}
              </span>
            </div>
            <p className="text-lg text-gray-700 mb-4">
              {proceso.objeto_contratacion}
            </p>
          </div>
        </div>

        {/* Quick Info */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="flex items-center p-4 bg-gray-50 rounded-lg">
            <BuildingOfficeIcon className="w-5 h-5 text-gray-400 mr-3" />
            <div>
              <div className="text-sm text-gray-500">Entidad</div>
              <div className="font-medium">{proceso.entidad_nombre}</div>
            </div>
          </div>
          
          <div className="flex items-center p-4 bg-gray-50 rounded-lg">
            <CurrencyDollarIcon className="w-5 h-5 text-gray-400 mr-3" />
            <div>
              <div className="text-sm text-gray-500">Valor Estimado</div>
              <div className="font-medium">
                {utils.formatCurrency(proceso.monto_referencial, proceso.moneda)}
              </div>
            </div>
          </div>
          
          <div className="flex items-center p-4 bg-gray-50 rounded-lg">
            <CalendarIcon className="w-5 h-5 text-gray-400 mr-3" />
            <div>
              <div className="text-sm text-gray-500">Fecha Publicación</div>
              <div className="font-medium">
                {utils.formatDateShort(proceso.fecha_publicacion)}
              </div>
            </div>
          </div>
          
          <div className="flex items-center p-4 bg-gray-50 rounded-lg">
            <ClockIcon className="w-5 h-5 text-gray-400 mr-3" />
            <div>
              <div className="text-sm text-gray-500">Tipo de Proceso</div>
              <div className="font-medium">{proceso.tipo_proceso}</div>
            </div>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200 mb-6">
        <nav className="-mb-px flex space-x-8">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`py-2 px-1 border-b-2 font-medium text-sm flex items-center ${
                  activeTab === tab.id
                    ? 'border-seace-blue text-seace-blue'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <Icon className="w-4 h-4 mr-2" />
                {tab.name}
              </button>
            );
          })}
        </nav>
      </div>

      {/* Tab Content */}
      {activeTab === 'details' && (
        <ProcessDetails proceso={proceso} />
      )}
      
      {activeTab === 'anexos' && (
        <ProcessAnexos anexos={anexos} />
      )}
      
      {activeTab === 'recomendaciones' && (
        <ProcessRecomendaciones 
          proceso={proceso}
          recomendaciones={recomendaciones}
          loading={recomendacionesLoading}
          error={recomendacionesError}
          generating={generating}
          onGenerate={generateRecomendaciones}
        />
      )}
      </div>
    </div>
  );
};

const ProcessDetails = ({ proceso }) => {
  const details = [
    { label: 'Código Proceso', value: proceso.id_proceso },
    { label: 'Número Convocatoria', value: proceso.numero_convocatoria },
    { label: 'Tipo de Proceso', value: proceso.tipo_proceso },
    { label: 'Tipo de Moneda', value: proceso.moneda },
    { label: 'Fecha Límite Presentación', value: utils.formatDate(proceso.fecha_limite_presentacion) },
    { label: 'Fecha de Extracción', value: utils.formatDate(proceso.fecha_extraccion) },
    { label: 'RUC Entidad', value: proceso.entidad_ruc },
    { label: 'Departamento', value: proceso.departamento },
    { label: 'Provincia', value: proceso.provincia },
    { label: 'Distrito', value: proceso.distrito }
  ];

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <Card className="shadow-xl bg-white/95 backdrop-blur-sm border-l-4 border-seace-blue animate-fade-in">
        <CardHeader className="bg-gradient-to-r from-seace-blue to-seace-blue-dark text-white">
          <h3 className="text-lg font-semibold">Información General</h3>
        </CardHeader>
        <CardBody>
          <dl className="space-y-4">
            {details.slice(0, 5).map((detail) => (
              <div key={detail.label} className="border-b border-gray-100 pb-2">
                <dt className="text-sm font-semibold text-seace-blue-dark">{detail.label}</dt>
                <dd className="mt-1 text-sm text-seace-gray-dark font-medium">{detail.value || 'No especificado'}</dd>
              </div>
            ))}
          </dl>
        </CardBody>
      </Card>

      <Card className="shadow-xl bg-white/95 backdrop-blur-sm border-l-4 border-seace-green animate-fade-in">
        <CardHeader className="bg-gradient-to-r from-seace-green to-seace-green-dark text-white">
          <h3 className="text-lg font-semibold">Información Adicional</h3>
        </CardHeader>
        <CardBody>
          <dl className="space-y-4">
            {details.slice(5).map((detail) => (
              <div key={detail.label} className="border-b border-gray-100 pb-2">
                <dt className="text-sm font-semibold text-seace-green-dark">{detail.label}</dt>
                <dd className="mt-1 text-sm text-seace-gray-dark font-medium">{detail.value || 'No especificado'}</dd>
              </div>
            ))}
          </dl>
        </CardBody>
      </Card>

      {proceso.descripcion && (
        <Card className="lg:col-span-2 shadow-xl bg-white/95 backdrop-blur-sm border-l-4 border-seace-orange animate-slide-up">
          <CardHeader className="bg-gradient-to-r from-seace-orange to-seace-orange-dark text-white">
            <h3 className="text-lg font-semibold">Descripción Detallada</h3>
          </CardHeader>
          <CardBody>
            <p className="text-seace-gray-dark whitespace-pre-wrap leading-relaxed">{proceso.descripcion}</p>
          </CardBody>
        </Card>
      )}
    </div>
  );
};

const ProcessAnexos = ({ anexos }) => {
  if (!anexos || anexos.length === 0) {
    return (
      <Card className="text-center py-12">
        <PaperClipIcon className="mx-auto h-12 w-12 text-gray-400 mb-4" />
        <h3 className="text-lg font-medium text-gray-900 mb-2">
          No hay anexos disponibles
        </h3>
        <p className="text-gray-600">
          Este proceso no tiene documentos anexos registrados.
        </p>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <h3 className="text-lg font-semibold">Documentos Anexos ({anexos.length})</h3>
      </CardHeader>
      <CardBody>
        <div className="space-y-4">
          {anexos.map((anexo) => (
            <div key={anexo.id} className="border border-gray-200 rounded-lg p-4 hover:border-gray-300 transition-colors">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <h4 className="text-sm font-medium text-gray-900 mb-1">
                    {anexo.nombre}
                  </h4>
                  {anexo.descripcion && (
                    <p className="text-sm text-gray-600 mb-2">
                      {anexo.descripcion}
                    </p>
                  )}
                  <div className="flex items-center space-x-4 text-xs text-gray-500">
                    {anexo.tipo && (
                      <span>Tipo: {anexo.tipo}</span>
                    )}
                    {anexo.fecha_actualizacion && (
                      <span>Actualizado: {utils.formatDateShort(anexo.fecha_actualizacion)}</span>
                    )}
                  </div>
                </div>
                {anexo.url && (
                  <Button variant="outline" size="sm" asChild>
                    <a 
                      href={anexo.url} 
                      target="_blank" 
                      rel="noopener noreferrer"
                      className="flex items-center"
                    >
                      <DocumentTextIcon className="w-4 h-4 mr-2" />
                      Ver
                    </a>
                  </Button>
                )}
              </div>
            </div>
          ))}
        </div>
      </CardBody>
    </Card>
  );
};

const ProcessRecomendaciones = ({ 
  proceso, 
  recomendaciones, 
  loading, 
  error, 
  generating, 
  onGenerate 
}) => {
  if (proceso.categoria_proyecto !== 'TI') {
    return (
      <Alert
        type="info"
        title="Recomendaciones no disponibles"
        message="Las recomendaciones de IA están disponibles únicamente para procesos de Tecnologías de la Información (TI)."
      />
    );
  }

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  if (error) {
    return (
      <ErrorAlert 
        error={error}
        onRetry={() => onGenerate(false)}
        onDismiss={() => {}}
      />
    );
  }

  if (!recomendaciones) {
    return (
      <Card className="text-center py-12">
        <SparklesIcon className="mx-auto h-12 w-12 text-gray-400 mb-4" />
        <h3 className="text-lg font-medium text-gray-900 mb-2">
          No hay recomendaciones generadas
        </h3>
        <p className="text-gray-600 mb-6">
          Genera recomendaciones inteligentes para este proceso TI utilizando IA.
        </p>
        <Button 
          onClick={() => onGenerate(false)}
          loading={generating}
          className="flex items-center"
        >
          <SparklesIcon className="w-4 h-4 mr-2" />
          Generar Recomendaciones
        </Button>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      {/* Actions */}
      <div className="flex justify-end">
        <Button 
          variant="outline"
          onClick={() => onGenerate(true)}
          loading={generating}
          className="flex items-center"
        >
          <SparklesIcon className="w-4 h-4 mr-2" />
          Regenerar
        </Button>
      </div>

      {/* MVP Recommendation */}
      {recomendaciones.mvp && (
        <Card>
          <CardHeader>
            <h3 className="text-lg font-semibold text-green-700">
              Recomendación MVP (Producto Mínimo Viable)
            </h3>
          </CardHeader>
          <CardBody>
            <div className="prose max-w-none">
              <div className="whitespace-pre-wrap text-gray-700">
                {recomendaciones.mvp.contenido}
              </div>
            </div>
          </CardBody>
        </Card>
      )}

      {/* Sprint 1 Recommendation */}
      {recomendaciones.sprint1 && (
        <Card>
          <CardHeader>
            <h3 className="text-lg font-semibold text-blue-700">
              Recomendación Sprint 1
            </h3>
          </CardHeader>
          <CardBody>
            <div className="prose max-w-none">
              <div className="whitespace-pre-wrap text-gray-700">
                {recomendaciones.sprint1.contenido}
              </div>
            </div>
          </CardBody>
        </Card>
      )}

      {/* Tech Stack Recommendation */}
      {recomendaciones.stack_tech && (
        <Card>
          <CardHeader>
            <h3 className="text-lg font-semibold text-purple-700">
              Stack Tecnológico Recomendado
            </h3>
          </CardHeader>
          <CardBody>
            <div className="prose max-w-none">
              <div className="whitespace-pre-wrap text-gray-700">
                {recomendaciones.stack_tech.contenido}
              </div>
            </div>
          </CardBody>
        </Card>
      )}

      {/* Metadata */}
      {recomendaciones.fecha_generacion && (
        <div className="text-sm text-gray-500 text-center">
          Recomendaciones generadas el {utils.formatDate(recomendaciones.fecha_generacion)}
        </div>
      )}
    </div>
  );
};
