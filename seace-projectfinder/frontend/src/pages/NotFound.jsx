import React from 'react';
import { Link } from 'react-router-dom';
import { 
  ExclamationTriangleIcon,
  HomeIcon,
  MagnifyingGlassIcon
} from '@heroicons/react/24/outline';
import { Button } from '../components/ui/Button';
import { Card } from '../components/ui/Card';

export const NotFound = () => {
  return (
    <div className="min-h-[60vh] flex items-center justify-center px-4 sm:px-6 lg:px-8">
      <Card className="max-w-md w-full text-center">
        <div className="p-8">
          {/* Icon */}
          <div className="flex justify-center mb-6">
            <div className="p-4 bg-red-100 rounded-full">
              <ExclamationTriangleIcon className="w-12 h-12 text-red-600" />
            </div>
          </div>
          
          {/* Error Code */}
          <h1 className="text-6xl font-bold text-gray-900 mb-4">404</h1>
          
          {/* Error Message */}
          <h2 className="text-2xl font-semibold text-gray-900 mb-4">
            Página no encontrada
          </h2>
          
          <p className="text-gray-600 mb-8">
            Lo sentimos, la página que estás buscando no existe o ha sido movida.
          </p>
          
          {/* Action Buttons */}
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Button asChild>
              <Link to="/" className="flex items-center justify-center">
                <HomeIcon className="w-4 h-4 mr-2" />
                Ir al Inicio
              </Link>
            </Button>
            
            <Button variant="outline" asChild>
              <Link to="/catalog" className="flex items-center justify-center">
                <MagnifyingGlassIcon className="w-4 h-4 mr-2" />
                Explorar Catálogo
              </Link>
            </Button>
          </div>
          
          {/* Additional Help */}
          <div className="mt-8 pt-6 border-t border-gray-200">
            <p className="text-sm text-gray-500 mb-4">
              ¿Necesitas ayuda? Puedes:
            </p>
            <div className="space-y-2 text-sm">
              <Link 
                to="/about" 
                className="block text-seace-blue hover:text-seace-blue-dark"
              >
                Conocer más sobre el proyecto
              </Link>
              <Link 
                to="/chatbot" 
                className="block text-seace-blue hover:text-seace-blue-dark"
              >
                Consultar con nuestro asistente IA
              </Link>
              <a 
                href="mailto:soporte@seaceprojectfinder.com" 
                className="block text-seace-blue hover:text-seace-blue-dark"
              >
                Contactar soporte técnico
              </a>
            </div>
          </div>
        </div>
      </Card>
    </div>
  );
};
