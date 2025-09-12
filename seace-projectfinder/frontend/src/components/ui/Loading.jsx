import React from 'react';

export const LoadingSpinner = ({ size = 'md', className = '' }) => {
  const sizeClasses = {
    sm: 'h-4 w-4',
    md: 'h-8 w-8',
    lg: 'h-12 w-12',
    xl: 'h-16 w-16'
  };

  return (
    <div className={`animate-spin rounded-full border-4 border-seace-blue-light border-t-seace-blue shadow-lg ${sizeClasses[size]} ${className}`}>
    </div>
  );
};

export const LoadingCard = ({ className = '' }) => {
  return (
    <div className={`animate-pulse bg-white rounded-lg shadow-lg border-l-4 border-seace-blue p-6 ${className}`}>
      <div className="space-y-4">
        <div className="h-6 bg-gradient-to-r from-seace-blue-light to-seace-blue rounded animate-pulse"></div>
        <div className="space-y-2">
          <div className="h-4 bg-seace-blue-light rounded w-3/4 animate-pulse"></div>
          <div className="h-4 bg-seace-blue-light rounded w-1/2 animate-pulse"></div>
        </div>
        <div className="flex space-x-2">
          <div className="h-8 bg-seace-green rounded w-20 animate-pulse"></div>
          <div className="h-8 bg-seace-orange rounded w-24 animate-pulse"></div>
        </div>
      </div>
    </div>
  );
};

export const LoadingList = ({ items = 3, className = '' }) => {
  return (
    <div className={`space-y-4 ${className}`}>
      {Array.from({ length: items }).map((_, index) => (
        <LoadingCard key={index} />
      ))}
    </div>
  );
};
