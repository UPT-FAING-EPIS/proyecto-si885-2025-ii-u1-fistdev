import React, { useState } from 'react';
import { 
  CogIcon, 
  PlayIcon,
  ArrowPathIcon,
  DocumentTextIcon,
  SparklesIcon,
  ClockIcon,
  CheckCircleIcon,
  ExclamationCircleIcon
} from '@heroicons/react/24/outline';
import { useAdminStatus, useETLOperations, useStats } from '../hooks/useAdmin';
import { Card, CardHeader, CardBody } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { LoadingSpinner } from '../components/ui/Loading';
import { ErrorAlert, Alert } from '../components/ui/Alert';

export const Admin = () => {
  const [activeTab, setActiveTab] = useState('status');
  
  const { status, loading: statusLoading, error: statusError, refetch } = useAdminStatus();
  const { operations, runDailySync, runFullSync, runTISync, generateEmbeddings } = useETLOperations();
  const { stats, loading: statsLoading, error: statsError } = useStats();

  const tabs = [
    { id: 'status', name: 'Estado del Sistema', icon: CogIcon },
    { id: 'etl', name: 'Operaciones ETL', icon: ArrowPathIcon },
    { id: 'stats', name: 'Estadísticas', icon: DocumentTextIcon }
  ];

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center mb-4">
          <CogIcon className="w-8 h-8 text-seace-blue mr-3" />
          <h1 className="text-3xl font-bold text-gray-900">
            Panel de Administración
          </h1>
        </div>
        <p className="text-gray-600">
          Gestión y monitoreo del sistema SEACE ProjectFinder
        </p>
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
      {activeTab === 'status' && (
        <SystemStatus 
          status={status} 
          loading={statusLoading} 
          error={statusError} 
          onRefresh={refetch}
        />
      )}
      
      {activeTab === 'etl' && (
        <ETLOperations operations={operations} actions={{
          runDailySync,
          runFullSync,
          runTISync,
          generateEmbeddings
        }} />
      )}
      
      {activeTab === 'stats' && (
        <SystemStats 
          stats={stats} 
          loading={statsLoading} 
          error={statsError} 
        />
      )}
    </div>
  );
};

const SystemStatus = ({ status, loading, error, onRefresh }) => {
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
        onRetry={onRefresh}
        onDismiss={() => {}}
      />
    );
  }

  const getStatusColor = (status) => {
    if (status === 'healthy' || status === 'success') return 'text-green-600';
    if (status === 'warning') return 'text-yellow-600';
    if (status === 'error' || status === 'failed') return 'text-red-600';
    return 'text-gray-600';
  };

  const getStatusIcon = (status) => {
    if (status === 'healthy' || status === 'success') return CheckCircleIcon;
    if (status === 'warning') return ExclamationCircleIcon;
    if (status === 'error' || status === 'failed') return ExclamationCircleIcon;
    return ClockIcon;
  };

  return (
    <div className="space-y-6">
      {/* Health Check */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-semibold">Estado de Salud del Sistema</h3>
            <Button variant="outline" onClick={onRefresh}>
              <ArrowPathIcon className="w-4 h-4 mr-2" />
              Actualizar
            </Button>
          </div>
        </CardHeader>
        <CardBody>
          {status?.health && (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              {Object.entries(status.health).map(([key, value]) => {
                const StatusIcon = getStatusIcon(value.status);
                return (
                  <div key={key} className="p-4 bg-gray-50 rounded-lg">
                    <div className="flex items-center mb-2">
                      <StatusIcon className={`w-5 h-5 mr-2 ${getStatusColor(value.status)}`} />
                      <span className="font-medium capitalize">{key.replace('_', ' ')}</span>
                    </div>
                    <div className={`text-sm ${getStatusColor(value.status)}`}>
                      {value.message || value.status}
                    </div>
                    {value.details && (
                      <div className="text-xs text-gray-500 mt-1">
                        {JSON.stringify(value.details)}
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          )}
        </CardBody>
      </Card>

      {/* ETL Status */}
      <Card>
        <CardHeader>
          <h3 className="text-lg font-semibold">Estado ETL</h3>
        </CardHeader>
        <CardBody>
          {status?.etl ? (
            <div className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="p-4 bg-gray-50 rounded-lg">
                  <div className="text-sm text-gray-500">Última Sincronización</div>
                  <div className="font-medium">
                    {status.etl.last_sync ? new Date(status.etl.last_sync).toLocaleString('es-PE') : 'Nunca'}
                  </div>
                </div>
                <div className="p-4 bg-gray-50 rounded-lg">
                  <div className="text-sm text-gray-500">Procesos Totales</div>
                  <div className="font-medium">{status.etl.total_processes || 0}</div>
                </div>
                <div className="p-4 bg-gray-50 rounded-lg">
                  <div className="text-sm text-gray-500">Procesos TI</div>
                  <div className="font-medium">{status.etl.ti_processes || 0}</div>
                </div>
              </div>
              
              {status.etl.sync_in_progress && (
                <Alert
                  type="info"
                  title="Sincronización en progreso"
                  message="El sistema está procesando datos del SEACE. Esta operación puede tomar varios minutos."
                />
              )}
            </div>
          ) : (
            <div className="text-gray-500">No hay información de ETL disponible</div>
          )}
        </CardBody>
      </Card>

      {/* System Status */}
      <Card>
        <CardHeader>
          <h3 className="text-lg font-semibold">Estado del Sistema</h3>
        </CardHeader>
        <CardBody>
          {status?.system ? (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="p-4 bg-gray-50 rounded-lg">
                <div className="text-sm text-gray-500">Uso de CPU</div>
                <div className="font-medium">{status.system.cpu_usage || 'N/A'}%</div>
              </div>
              <div className="p-4 bg-gray-50 rounded-lg">
                <div className="text-sm text-gray-500">Uso de Memoria</div>
                <div className="font-medium">{status.system.memory_usage || 'N/A'}%</div>
              </div>
              <div className="p-4 bg-gray-50 rounded-lg">
                <div className="text-sm text-gray-500">Espacio en Disco</div>
                <div className="font-medium">{status.system.disk_usage || 'N/A'}%</div>
              </div>
              <div className="p-4 bg-gray-50 rounded-lg">
                <div className="text-sm text-gray-500">Tiempo Activo</div>
                <div className="font-medium">{status.system.uptime || 'N/A'}</div>
              </div>
            </div>
          ) : (
            <div className="text-gray-500">No hay información del sistema disponible</div>
          )}
        </CardBody>
      </Card>
    </div>
  );
};

const ETLOperations = ({ operations, actions }) => {
  const [fullSyncDays, setFullSyncDays] = useState(365);
  const [embeddingsBatchSize, setEmbeddingsBatchSize] = useState(50);

  const operationsList = [
    {
      id: 'dailySync',
      title: 'Sincronización Diaria',
      description: 'Sincroniza los procesos de las últimas 24 horas',
      action: actions.runDailySync,
      icon: ClockIcon
    },
    {
      id: 'fullSync',
      title: 'Sincronización Completa',
      description: 'Sincroniza todos los procesos del período especificado',
      action: () => actions.runFullSync(fullSyncDays),
      icon: ArrowPathIcon,
      hasOptions: true
    },
    {
      id: 'tiSync',
      title: 'Sincronización TI',
      description: 'Sincroniza específicamente procesos de TI',
      action: actions.runTISync,
      icon: DocumentTextIcon
    },
    {
      id: 'generateEmbeddings',
      title: 'Generar Embeddings',
      description: 'Genera embeddings para búsqueda semántica',
      action: () => actions.generateEmbeddings(embeddingsBatchSize),
      icon: SparklesIcon,
      hasOptions: true
    }
  ];

  return (
    <div className="space-y-6">
      {operationsList.map((operation) => {
        const Icon = operation.icon;
        const operationState = operations[operation.id];
        
        return (
          <Card key={operation.id}>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div className="flex items-center">
                  <Icon className="w-6 h-6 text-seace-blue mr-3" />
                  <div>
                    <h3 className="text-lg font-semibold">{operation.title}</h3>
                    <p className="text-gray-600 text-sm">{operation.description}</p>
                  </div>
                </div>
                <Button
                  onClick={operation.action}
                  loading={operationState?.loading}
                  disabled={operationState?.loading}
                  className="flex items-center"
                >
                  <PlayIcon className="w-4 h-4 mr-2" />
                  Ejecutar
                </Button>
              </div>
            </CardHeader>
            <CardBody>
              {/* Options */}
              {operation.hasOptions && (
                <div className="mb-4">
                  {operation.id === 'fullSync' && (
                    <div className="flex items-center space-x-4">
                      <label className="text-sm font-medium text-gray-700">
                        Días hacia atrás:
                      </label>
                      <input
                        type="number"
                        value={fullSyncDays}
                        onChange={(e) => setFullSyncDays(Number(e.target.value))}
                        className="w-20 px-2 py-1 border border-gray-300 rounded text-sm"
                        min="1"
                        max="3650"
                      />
                    </div>
                  )}
                  {operation.id === 'generateEmbeddings' && (
                    <div className="flex items-center space-x-4">
                      <label className="text-sm font-medium text-gray-700">
                        Tamaño del lote:
                      </label>
                      <input
                        type="number"
                        value={embeddingsBatchSize}
                        onChange={(e) => setEmbeddingsBatchSize(Number(e.target.value))}
                        className="w-20 px-2 py-1 border border-gray-300 rounded text-sm"
                        min="1"
                        max="100"
                      />
                    </div>
                  )}
                </div>
              )}
              
              {/* Status */}
              {operationState?.loading && (
                <Alert
                  type="info"
                  title="Operación en progreso"
                  message="Esta operación puede tomar varios minutos. No cierres esta página."
                />
              )}
              
              {operationState?.error && (
                <ErrorAlert
                  error={operationState.error}
                  onDismiss={() => {}}
                />
              )}
              
              {operationState?.result && (
                <Alert
                  type="success"
                  title="Operación completada"
                  message={JSON.stringify(operationState.result, null, 2)}
                />
              )}
            </CardBody>
          </Card>
        );
      })}
    </div>
  );
};

const SystemStats = ({ stats, loading, error }) => {
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
        onDismiss={() => {}}
      />
    );
  }

  return (
    <div className="space-y-6">
      {/* Procesos Stats */}
      {stats?.procesos && (
        <Card>
          <CardHeader>
            <h3 className="text-lg font-semibold">Estadísticas de Procesos</h3>
          </CardHeader>
          <CardBody>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <div className="p-4 bg-blue-50 rounded-lg">
                <div className="text-2xl font-bold text-blue-600">
                  {stats.procesos.total || 0}
                </div>
                <div className="text-sm text-blue-700">Total de Procesos</div>
              </div>
              <div className="p-4 bg-green-50 rounded-lg">
                <div className="text-2xl font-bold text-green-600">
                  {stats.procesos.ti_count || 0}
                </div>
                <div className="text-sm text-green-700">Procesos TI</div>
              </div>
              <div className="p-4 bg-purple-50 rounded-lg">
                <div className="text-2xl font-bold text-purple-600">
                  {stats.procesos.adjudicados || 0}
                </div>
                <div className="text-sm text-purple-700">Adjudicados</div>
              </div>
              <div className="p-4 bg-yellow-50 rounded-lg">
                <div className="text-2xl font-bold text-yellow-600">
                  {stats.procesos.en_proceso || 0}
                </div>
                <div className="text-sm text-yellow-700">En Proceso</div>
              </div>
            </div>
          </CardBody>
        </Card>
      )}

      {/* Chatbot Stats */}
      {stats?.chatbot && (
        <Card>
          <CardHeader>
            <h3 className="text-lg font-semibold">Estadísticas del Chatbot</h3>
          </CardHeader>
          <CardBody>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="p-4 bg-indigo-50 rounded-lg">
                <div className="text-2xl font-bold text-indigo-600">
                  {stats.chatbot.total_queries || 0}
                </div>
                <div className="text-sm text-indigo-700">Consultas Totales</div>
              </div>
              <div className="p-4 bg-cyan-50 rounded-lg">
                <div className="text-2xl font-bold text-cyan-600">
                  {stats.chatbot.unique_sessions || 0}
                </div>
                <div className="text-sm text-cyan-700">Sesiones Únicas</div>
              </div>
              <div className="p-4 bg-pink-50 rounded-lg">
                <div className="text-2xl font-bold text-pink-600">
                  {Math.round(stats.chatbot.avg_response_time || 0)}ms
                </div>
                <div className="text-sm text-pink-700">Tiempo Promedio</div>
              </div>
            </div>
          </CardBody>
        </Card>
      )}
    </div>
  );
};
