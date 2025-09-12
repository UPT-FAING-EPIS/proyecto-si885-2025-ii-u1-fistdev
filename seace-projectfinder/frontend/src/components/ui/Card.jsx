import React from 'react';

export const Card = ({ 
  children, 
  title, 
  subtitle, 
  className = '', 
  padding = true,
  shadow = true,
  hover = false 
}) => {
  const baseClasses = 'bg-white rounded-lg border border-gray-200';
  const shadowClass = shadow ? 'shadow-sm' : '';
  const hoverClass = hover ? 'hover:shadow-md transition-shadow duration-200' : '';
  const paddingClass = padding ? 'p-6' : '';

  return (
    <div className={`${baseClasses} ${shadowClass} ${hoverClass} ${className}`}>
      {(title || subtitle) && (
        <div className={`${paddingClass} ${!padding ? 'px-6 pt-6' : ''} pb-4 border-b border-gray-200`}>
          {title && (
            <h3 className="text-lg font-medium text-gray-900">
              {title}
            </h3>
          )}
          {subtitle && (
            <p className="mt-1 text-sm text-gray-500">
              {subtitle}
            </p>
          )}
        </div>
      )}
      <div className={padding && (title || subtitle) ? 'p-6 pt-4' : paddingClass}>
        {children}
      </div>
    </div>
  );
};

export const CardHeader = ({ children, className = '' }) => {
  return (
    <div className={`px-6 py-4 border-b border-gray-200 ${className}`}>
      {children}
    </div>
  );
};

export const CardBody = ({ children, className = '' }) => {
  return (
    <div className={`p-6 ${className}`}>
      {children}
    </div>
  );
};

export const CardFooter = ({ children, className = '' }) => {
  return (
    <div className={`px-6 py-4 border-t border-gray-200 bg-gray-50 rounded-b-lg ${className}`}>
      {children}
    </div>
  );
};
