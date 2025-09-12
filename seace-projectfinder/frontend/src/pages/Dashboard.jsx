import React, { useEffect, useState } from 'react';
import { dashboardService } from '../services/seaceService';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { LoadingSpinner } from '../components/ui/Loading';
import { ErrorAlert } from '../components/ui/Alert';
import { 
  ChartBarIcon, 
  ArrowTopRightOnSquareIcon,
  ExclamationTriangleIcon 
} from '@heroicons/react/24/outline';

export const Dashboard = () => {
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchDashboard = async () => {
      try {
        setLoading(true);
        setError(null);
        
        const response = await dashboardService.getUrl();
        setDashboardData(response);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchDashboard();
  }, []);

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex justify-center items-center h-64">
          <LoadingSpinner size="lg" />
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <ErrorAlert 
          error={error}
          onDismiss={() => setError(null)}
        />
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center mb-4">
          <ChartBarIcon className="w-8 h-8 text-seace-blue mr-3" />
          <h1 className="text-3xl font-bold text-gray-900">
            Dashboard Analítico
          </h1>
        </div>
        <p className="text-gray-600">
          Visualización interactiva de datos y estadísticas de procesos SEACE
        </p>
      </div>

      {/* Dashboard Content */}
      {dashboardData?.url ? (
        <div className="space-y-6">
          {/* Quick Actions */}
          <Card>
            <div className="flex items-center justify-between p-6">
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">
                  Dashboard Interactivo
                </h3>
                <p className="text-gray-600">
                  Accede al dashboard completo de Power BI con todas las visualizaciones disponibles
                </p>
              </div>
              <Button asChild>
                <a 
                  href={dashboardData.url} 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="flex items-center"
                >
                  <ArrowTopRightOnSquareIcon className="w-4 h-4 mr-2" />
                  Abrir Dashboard
                </a>
              </Button>
            </div>
          </Card>

          {/* Embedded Dashboard */}
          <Card padding={false}>
            <div className="aspect-video w-full bg-gray-100 rounded-lg overflow-hidden">
              <iframe
                src={dashboardData.url}
                className="w-full h-full border-0"
                title="SEACE Dashboard"
                allowFullScreen
                loading="lazy"
              />
            </div>
          </Card>

          {/* Dashboard Info */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <Card>
              <div className="text-center p-6">
                <div className="text-2xl font-bold text-seace-blue mb-2">
                  📊
                </div>
                <h3 className="text-lg font-semibold mb-2">Análisis Temporal</h3>
                <p className="text-gray-600 text-sm">
                  Visualiza tendencias y patrones temporales de los procesos de contratación
                </p>
              </div>
            </Card>

            <Card>
              <div className="text-center p-6">
                <div className="text-2xl font-bold text-seace-blue mb-2">
                  🏢
                </div>
                <h3 className="text-lg font-semibold mb-2">Por Entidades</h3>
                <p className="text-gray-600 text-sm">
                  Analiza el desempeño y actividad de contratación por entidad pública
                </p>
              </div>
            </Card>

            <Card>
              <div className="text-center p-6">
                <div className="text-2xl font-bold text-seace-blue mb-2">
                  💻
                </div>
                <h3 className="text-lg font-semibold mb-2">Procesos TI</h3>
                <p className="text-gray-600 text-sm">
                  Foco específico en procesos de tecnologías de la información
                </p>
              </div>
            </Card>
          </div>

          {/* Additional Info */}
          <Card className="bg-blue-50 border-blue-200">
            <div className="p-6">
              <h3 className="text-lg font-semibold text-blue-900 mb-4">
                Características del Dashboard
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <h4 className="font-medium text-blue-800 mb-2">Métricas Principales</h4>
                  <ul className="text-sm text-blue-700 space-y-1">
                    <li>• Total de procesos por periodo</li>
                    <li>• Distribución por tipo de proceso</li>
                    <li>• Valores adjudicados y estimados</li>
                    <li>• Estados de procesos en tiempo real</li>
                  </ul>
                </div>
                <div>
                  <h4 className="font-medium text-blue-800 mb-2">Filtros Interactivos</h4>
                  <ul className="text-sm text-blue-700 space-y-1">
                    <li>• Filtrado por fechas y periodos</li>
                    <li>• Selección por entidades</li>
                    <li>• Categorización por tipo de proceso</li>
                    <li>• Segmentación geográfica</li>
                  </ul>
                </div>
              </div>
            </div>
          </Card>
        </div>
      ) : (
        <Card className="text-center py-12">
          <ExclamationTriangleIcon className="mx-auto h-12 w-12 text-yellow-400 mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">
            Dashboard no disponible
          </h3>
          <p className="text-gray-600 mb-6">
            El dashboard de Power BI no está configurado o no se encuentra disponible en este momento.
          </p>
          <Button variant="outline" onClick={() => window.location.reload()}>
            Reintentar
          </Button>
        </Card>
      )}
    </div>
  );
};
