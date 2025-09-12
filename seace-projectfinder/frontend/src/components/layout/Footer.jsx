import React from 'react';
import { Link } from 'react-router-dom';

export const Footer = () => {
  return (
    <footer className="bg-gray-800 text-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          {/* Logo y descripción */}
          <div className="col-span-1 md:col-span-2">
            <div className="flex items-center space-x-2 mb-4">
              <img 
                src="/seace-icon.svg" 
                alt="SEACE ProjectFinder" 
                className="h-8 w-8 filter brightness-0 invert"
              />
              <span className="text-xl font-bold">SEACE ProjectFinder</span>
            </div>
            <p className="text-gray-300 mb-4">
              Plataforma inteligente para el análisis y búsqueda de procesos de contratación 
              del Sistema Electrónico de Contrataciones del Estado (SEACE).
            </p>
            <p className="text-sm text-gray-400">
              Desarrollado como parte del proyecto de Inteligencia de Negocios - UPT
            </p>
          </div>

          {/* Enlaces rápidos */}
          <div>
            <h3 className="text-lg font-semibold mb-4">Enlaces Rápidos</h3>
            <ul className="space-y-2">
              <li>
                <Link 
                  to="/" 
                  className="text-gray-300 hover:text-white transition-colors duration-200"
                >
                  Inicio
                </Link>
              </li>
              <li>
                <Link 
                  to="/catalog" 
                  className="text-gray-300 hover:text-white transition-colors duration-200"
                >
                  Catálogo de Procesos
                </Link>
              </li>
              <li>
                <Link 
                  to="/chatbot" 
                  className="text-gray-300 hover:text-white transition-colors duration-200"
                >
                  Asistente IA
                </Link>
              </li>
              <li>
                <Link 
                  to="/dashboard" 
                  className="text-gray-300 hover:text-white transition-colors duration-200"
                >
                  Dashboard
                </Link>
              </li>
            </ul>
          </div>

          {/* Información */}
          <div>
            <h3 className="text-lg font-semibold mb-4">Información</h3>
            <ul className="space-y-2">
              <li>
                <Link 
                  to="/about" 
                  className="text-gray-300 hover:text-white transition-colors duration-200"
                >
                  Acerca del Proyecto
                </Link>
              </li>
              <li>
                <a 
                  href="https://www.osce.gob.pe/" 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="text-gray-300 hover:text-white transition-colors duration-200"
                >
                  OSCE
                </a>
              </li>
              <li>
                <a 
                  href="https://www.seace.gob.pe/" 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="text-gray-300 hover:text-white transition-colors duration-200"
                >
                  SEACE
                </a>
              </li>
              <li>
                <a 
                  href="https://www.upt.edu.pe/" 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="text-gray-300 hover:text-white transition-colors duration-200"
                >
                  Universidad Privada de Tacna
                </a>
              </li>
            </ul>
          </div>
        </div>

        {/* Línea divisoria y copyright */}
        <div className="border-t border-gray-700 mt-8 pt-8">
          <div className="flex flex-col md:flex-row justify-between items-center">
            <p className="text-gray-400 text-sm">
              © {new Date().getFullYear()} SEACE ProjectFinder. Proyecto académico - UPT.
            </p>
            <div className="mt-4 md:mt-0">
              <p className="text-gray-400 text-sm">
                Última actualización: {new Date().toLocaleDateString('es-PE')}
              </p>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
};
