import { useState, useEffect } from 'react';
import { procesosService } from '../services/seaceService';

export const useProcesos = (initialParams = {}) => {
  const [procesos, setProcesos] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [pagination, setPagination] = useState({
    page: 1,
    limit: 20,
    total: 0,
    totalPages: 0
  });

  const fetchProcesos = async (params = {}) => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await procesosService.getList({
        ...initialParams,
        ...params
      });
      
      setProcesos(response.items || []);
      setPagination({
        page: response.page || 1,
        limit: response.limit || 20,
        total: response.total || 0,
        totalPages: Math.ceil((response.total || 0) / (response.limit || 20))
      });
    } catch (err) {
      setError(err.message);
      setProcesos([]);
    } finally {
      setLoading(false);
    }
  };

  const refreshProcesos = () => {
    fetchProcesos();
  };

  useEffect(() => {
    fetchProcesos();
  }, []);

  return {
    procesos,
    loading,
    error,
    pagination,
    fetchProcesos,
    refreshProcesos
  };
};

export const useProceso = (procesoId) => {
  const [proceso, setProceso] = useState(null);
  const [anexos, setAnexos] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchProceso = async () => {
    if (!procesoId) return;

    try {
      setLoading(true);
      setError(null);
      
      const [procesoData, anexosData] = await Promise.all([
        procesosService.getById(procesoId),
        procesosService.getAnexos(procesoId)
      ]);
      
      setProceso(procesoData);
      setAnexos(anexosData || []);
    } catch (err) {
      setError(err.message);
      setProceso(null);
      setAnexos([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchProceso();
  }, [procesoId]);

  return {
    proceso,
    anexos,
    loading,
    error,
    refetch: fetchProceso
  };
};

export const useSearchProcesos = () => {
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const search = async (query, params = {}) => {
    if (!query.trim()) {
      setResults([]);
      return;
    }

    try {
      setLoading(true);
      setError(null);
      
      const response = await procesosService.search(query, params);
      setResults(response.items || []);
    } catch (err) {
      setError(err.message);
      setResults([]);
    } finally {
      setLoading(false);
    }
  };

  const clearResults = () => {
    setResults([]);
    setError(null);
  };

  return {
    results,
    loading,
    error,
    search,
    clearResults
  };
};
