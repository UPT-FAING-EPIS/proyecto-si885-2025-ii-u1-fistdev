import React from 'react';
import { Link } from 'react-router-dom';
import { 
  InformationCircleIcon,
  AcademicCapIcon,
  CodeBracketIcon,
  ChartBarIcon,
  SparklesIcon,
  UsersIcon,
  BuildingLibraryIcon,
  LinkIcon
} from '@heroicons/react/24/outline';
import { Card, CardHeader, CardBody } from '../components/ui/Card';
import { Button } from '../components/ui/Button';

export const About = () => {
  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="text-center mb-12">
        <div className="flex justify-center mb-6">
          <div className="p-4 bg-seace-blue bg-opacity-10 rounded-full">
            <InformationCircleIcon className="w-12 h-12 text-seace-blue" />
          </div>
        </div>
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
          Acerca de SEACE ProjectFinder
        </h1>
        <p className="text-xl text-gray-600 max-w-3xl mx-auto">
          Una plataforma inteligente para el análisis y búsqueda de procesos de contratación 
          del Sistema Electrónico de Contrataciones del Estado (SEACE)
        </p>
      </div>

      {/* Project Overview */}
      <Card className="mb-8">
        <CardHeader>
          <h2 className="text-2xl font-bold text-gray-900">¿Qué es SEACE ProjectFinder?</h2>
        </CardHeader>
        <CardBody>
          <div className="prose max-w-none">
            <p className="text-gray-700 mb-4">
              SEACE ProjectFinder es una aplicación web desarrollada como proyecto de 
              Inteligencia de Negocios que utiliza tecnologías de vanguardia para facilitar 
              el análisis y búsqueda de procesos de contratación pública en el Perú.
            </p>
            <p className="text-gray-700 mb-4">
              La plataforma integra técnicas de web scraping, procesamiento de lenguaje natural 
              y análisis de datos para ofrecer una experiencia de usuario moderna e intuitiva 
              en la exploración de datos del SEACE.
            </p>
            <p className="text-gray-700">
              Con un enfoque especial en procesos de Tecnologías de la Información (TI), 
              la aplicación proporciona recomendaciones inteligentes utilizando IA para 
              ayudar en la toma de decisiones en contrataciones públicas.
            </p>
          </div>
        </CardBody>
      </Card>

      {/* Features */}
      <Card className="mb-8">
        <CardHeader>
          <h2 className="text-2xl font-bold text-gray-900">Características Principales</h2>
        </CardHeader>
        <CardBody>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="flex items-start">
              <ChartBarIcon className="w-6 h-6 text-seace-blue mr-3 mt-1 flex-shrink-0" />
              <div>
                <h3 className="font-semibold text-gray-900 mb-2">Análisis de Datos</h3>
                <p className="text-gray-600 text-sm">
                  Visualización interactiva de estadísticas y tendencias de procesos de contratación
                </p>
              </div>
            </div>
            
            <div className="flex items-start">
              <SparklesIcon className="w-6 h-6 text-seace-blue mr-3 mt-1 flex-shrink-0" />
              <div>
                <h3 className="font-semibold text-gray-900 mb-2">Inteligencia Artificial</h3>
                <p className="text-gray-600 text-sm">
                  Chatbot inteligente y recomendaciones automatizadas para procesos TI
                </p>
              </div>
            </div>
            
            <div className="flex items-start">
              <CodeBracketIcon className="w-6 h-6 text-seace-blue mr-3 mt-1 flex-shrink-0" />
              <div>
                <h3 className="font-semibold text-gray-900 mb-2">Tecnología Moderna</h3>
                <p className="text-gray-600 text-sm">
                  Desarrollado con Python, React, PostgreSQL y Google Gemini AI
                </p>
              </div>
            </div>
            
            <div className="flex items-start">
              <UsersIcon className="w-6 h-6 text-seace-blue mr-3 mt-1 flex-shrink-0" />
              <div>
                <h3 className="font-semibold text-gray-900 mb-2">Interfaz Intuitiva</h3>
                <p className="text-gray-600 text-sm">
                  Diseño responsivo y experiencia de usuario optimizada
                </p>
              </div>
            </div>
          </div>
        </CardBody>
      </Card>

      {/* Academic Context */}
      <Card className="mb-8">
        <CardHeader>
          <div className="flex items-center">
            <AcademicCapIcon className="w-6 h-6 text-seace-blue mr-3" />
            <h2 className="text-2xl font-bold text-gray-900">Contexto Académico</h2>
          </div>
        </CardHeader>
        <CardBody>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Universidad</h3>
              <div className="flex items-center mb-4">
                <BuildingLibraryIcon className="w-5 h-5 text-gray-400 mr-2" />
                <span className="text-gray-700">Universidad Privada de Tacna (UPT)</span>
              </div>
              
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Carrera</h3>
              <p className="text-gray-700 mb-4">Ingeniería de Sistemas</p>
              
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Asignatura</h3>
              <p className="text-gray-700">Inteligencia de Negocios</p>
            </div>
            
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Objetivos del Proyecto</h3>
              <ul className="space-y-2 text-gray-700">
                <li className="flex items-start">
                  <span className="w-2 h-2 bg-seace-blue rounded-full mr-3 mt-2"></span>
                  Aplicar técnicas de inteligencia de negocios
                </li>
                <li className="flex items-start">
                  <span className="w-2 h-2 bg-seace-blue rounded-full mr-3 mt-2"></span>
                  Integrar tecnologías de IA y ML
                </li>
                <li className="flex items-start">
                  <span className="w-2 h-2 bg-seace-blue rounded-full mr-3 mt-2"></span>
                  Desarrollar una solución práctica
                </li>
                <li className="flex items-start">
                  <span className="w-2 h-2 bg-seace-blue rounded-full mr-3 mt-2"></span>
                  Crear valor para el sector público
                </li>
              </ul>
            </div>
          </div>
        </CardBody>
      </Card>

      {/* Resources */}
      <Card className="mb-8">
        <CardHeader>
          <h2 className="text-2xl font-bold text-gray-900">Recursos y Enlaces</h2>
        </CardHeader>
        <CardBody>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Fuentes de Datos</h3>
              <div className="space-y-3">
                <a 
                  href="https://www.seace.gob.pe/"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center text-seace-blue hover:text-seace-blue-dark"
                >
                  <LinkIcon className="w-4 h-4 mr-2" />
                  Portal SEACE - OSCE
                </a>
                <a 
                  href="https://www.osce.gob.pe/"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center text-seace-blue hover:text-seace-blue-dark"
                >
                  <LinkIcon className="w-4 h-4 mr-2" />
                  Organismo Supervisor de las Contrataciones del Estado
                </a>
              </div>
            </div>
            
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Navegación</h3>
              <div className="space-y-3">
                <Link 
                  to="/catalog"
                  className="flex items-center text-seace-blue hover:text-seace-blue-dark"
                >
                  <LinkIcon className="w-4 h-4 mr-2" />
                  Explorar Catálogo de Procesos
                </Link>
                <Link 
                  to="/chatbot"
                  className="flex items-center text-seace-blue hover:text-seace-blue-dark"
                >
                  <LinkIcon className="w-4 h-4 mr-2" />
                  Probar Asistente IA
                </Link>
                <Link 
                  to="/dashboard"
                  className="flex items-center text-seace-blue hover:text-seace-blue-dark"
                >
                  <LinkIcon className="w-4 h-4 mr-2" />
                  Ver Dashboard Analítico
                </Link>
              </div>
            </div>
          </div>
        </CardBody>
      </Card>

      {/* CTA */}
      <div className="text-center">
        <div className="bg-seace-blue bg-opacity-10 rounded-lg p-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">
            ¿Listo para explorar?
          </h2>
          <p className="text-gray-600 mb-6 max-w-2xl mx-auto">
            Descubre cómo SEACE ProjectFinder puede ayudarte a encontrar y analizar 
            procesos de contratación pública de manera más eficiente.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Button size="lg" asChild>
              <Link to="/catalog">
                Explorar Procesos
              </Link>
            </Button>
            <Button variant="outline" size="lg" asChild>
              <Link to="/chatbot">
                Consultar IA
              </Link>
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
};
