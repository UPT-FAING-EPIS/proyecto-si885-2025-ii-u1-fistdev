import React from 'react';
import { Link } from 'react-router-dom';
import { 
  MagnifyingGlassIcon, 
  ChatBubbleLeftRightIcon, 
  ChartBarIcon,
  DocumentTextIcon,
  SparklesIcon,
  ArrowRightIcon
} from '@heroicons/react/24/outline';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';

export const Home = () => {
  return (
    <div className="min-h-full">
      {/* Hero Section */}
      <div className="relative overflow-hidden">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24">
          <div className="text-center">
            <h1 className="text-4xl sm:text-6xl font-bold text-gray-900 mb-6">
              <span className="text-seace-blue">SEACE</span> ProjectFinder
            </h1>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto mb-8">
              Plataforma inteligente para el análisis, búsqueda y recomendaciones de 
              procesos de contratación del Sistema Electrónico de Contrataciones del Estado
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Button asChild size="lg">
                <Link to="/catalog" className="flex items-center">
                  <MagnifyingGlassIcon className="w-5 h-5 mr-2" />
                  Explorar Catálogo
                </Link>
              </Button>
              <Button variant="outline" size="lg" asChild>
                <Link to="/chatbot" className="flex items-center">
                  <ChatBubbleLeftRightIcon className="w-5 h-5 mr-2" />
                  Consultar IA
                </Link>
              </Button>
            </div>
          </div>
        </div>
      </div>

      {/* Features Section */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <div className="text-center mb-12">
          <h2 className="text-3xl font-bold text-gray-900 mb-4">
            Características Principales
          </h2>
          <p className="text-lg text-gray-600">
            Herramientas avanzadas para el análisis de procesos de contratación pública
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {/* Catálogo de Procesos */}
          <Card hover className="text-center">
            <div className="flex justify-center mb-4">
              <div className="p-3 bg-seace-blue bg-opacity-10 rounded-full">
                <DocumentTextIcon className="w-8 h-8 text-seace-blue" />
              </div>
            </div>
            <h3 className="text-xl font-semibold text-gray-900 mb-2">
              Catálogo de Procesos
            </h3>
            <p className="text-gray-600 mb-4">
              Explora y filtra miles de procesos de contratación del SEACE con 
              herramientas de búsqueda avanzadas.
            </p>
            <Button variant="ghost" asChild>
              <Link to="/catalog" className="flex items-center justify-center">
                Ver Catálogo
                <ArrowRightIcon className="w-4 h-4 ml-2" />
              </Link>
            </Button>
          </Card>

          {/* Asistente IA */}
          <Card hover className="text-center">
            <div className="flex justify-center mb-4">
              <div className="p-3 bg-green-500 bg-opacity-10 rounded-full">
                <SparklesIcon className="w-8 h-8 text-green-500" />
              </div>
            </div>
            <h3 className="text-xl font-semibold text-gray-900 mb-2">
              Asistente con IA
            </h3>
            <p className="text-gray-600 mb-4">
              Realiza consultas en lenguaje natural y obtén recomendaciones 
              inteligentes sobre procesos TI.
            </p>
            <Button variant="ghost" asChild>
              <Link to="/chatbot" className="flex items-center justify-center">
                Probar Asistente
                <ArrowRightIcon className="w-4 h-4 ml-2" />
              </Link>
            </Button>
          </Card>

          {/* Dashboard Analítico */}
          <Card hover className="text-center">
            <div className="flex justify-center mb-4">
              <div className="p-3 bg-purple-500 bg-opacity-10 rounded-full">
                <ChartBarIcon className="w-8 h-8 text-purple-500" />
              </div>
            </div>
            <h3 className="text-xl font-semibold text-gray-900 mb-2">
              Dashboard Analítico
            </h3>
            <p className="text-gray-600 mb-4">
              Visualiza estadísticas y tendencias de los procesos de contratación 
              con dashboards interactivos.
            </p>
            <Button variant="ghost" asChild>
              <Link to="/dashboard" className="flex items-center justify-center">
                Ver Dashboard
                <ArrowRightIcon className="w-4 h-4 ml-2" />
              </Link>
            </Button>
          </Card>
        </div>
      </div>

      {/* Stats Section */}
      <div className="bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">
              Datos del Sistema
            </h2>
            <p className="text-lg text-gray-600">
              Información actualizada sobre los procesos en la plataforma
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
            <div className="text-center">
              <div className="text-3xl font-bold text-seace-blue mb-2">15,000+</div>
              <div className="text-gray-600">Procesos Analizados</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-seace-blue mb-2">2,500+</div>
              <div className="text-gray-600">Procesos TI</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-seace-blue mb-2">500+</div>
              <div className="text-gray-600">Entidades Públicas</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-seace-blue mb-2">24/7</div>
              <div className="text-gray-600">Disponibilidad</div>
            </div>
          </div>
        </div>
      </div>

      {/* CTA Section */}
      <div className="bg-seace-blue">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
          <div className="text-center">
            <h2 className="text-3xl font-bold text-white mb-4">
              ¿Listo para comenzar?
            </h2>
            <p className="text-xl text-blue-100 mb-8 max-w-2xl mx-auto">
              Explora los procesos de contratación pública con herramientas 
              de análisis avanzadas y recomendaciones de IA.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Button variant="secondary" size="lg" asChild>
                <Link to="/catalog">
                  Comenzar Exploración
                </Link>
              </Button>
              <Button variant="outline" size="lg" asChild className="border-white text-white hover:bg-white hover:text-seace-blue">
                <Link to="/about">
                  Conocer Más
                </Link>
              </Button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
