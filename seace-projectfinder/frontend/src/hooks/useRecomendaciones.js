import { useState, useEffect } from 'react';
import { recomendacionesService } from '../services/seaceService';

export const useRecomendaciones = (procesoId) => {
  const [recomendaciones, setRecomendaciones] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [generating, setGenerating] = useState(false);

  const fetchRecomendaciones = async () => {
    if (!procesoId) return;

    try {
      setLoading(true);
      setError(null);
      
      const response = await recomendacionesService.getByProceso(procesoId);
      setRecomendaciones(response);
    } catch (err) {
      setError(err.message);
      setRecomendaciones(null);
    } finally {
      setLoading(false);
    }
  };

  const generateRecomendaciones = async (forceRegenerate = false) => {
    if (!procesoId) return;

    try {
      setGenerating(true);
      setError(null);
      
      const response = await recomendacionesService.generate(procesoId, forceRegenerate);
      
      // Actualizar las recomendaciones después de la generación
      await fetchRecomendaciones();
      
      return response;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setGenerating(false);
    }
  };

  const clearRecomendaciones = async () => {
    if (!procesoId) return;

    try {
      setLoading(true);
      setError(null);
      
      await recomendacionesService.clear(procesoId);
      setRecomendaciones(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRecomendaciones();
  }, [procesoId]);

  return {
    recomendaciones,
    loading,
    error,
    generating,
    fetchRecomendaciones,
    generateRecomendaciones,
    clearRecomendaciones
  };
};

export const useRecomendacionMVP = (procesoId) => {
  const [mvp, setMvp] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchMVP = async () => {
    if (!procesoId) return;

    try {
      setLoading(true);
      setError(null);
      
      const response = await recomendacionesService.getMVP(procesoId);
      setMvp(response);
    } catch (err) {
      setError(err.message);
      setMvp(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchMVP();
  }, [procesoId]);

  return {
    mvp,
    loading,
    error,
    refetch: fetchMVP
  };
};

export const useRecomendacionSprint1 = (procesoId) => {
  const [sprint1, setSprint1] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchSprint1 = async () => {
    if (!procesoId) return;

    try {
      setLoading(true);
      setError(null);
      
      const response = await recomendacionesService.getSprint1(procesoId);
      setSprint1(response);
    } catch (err) {
      setError(err.message);
      setSprint1(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSprint1();
  }, [procesoId]);

  return {
    sprint1,
    loading,
    error,
    refetch: fetchSprint1
  };
};

export const useStackTech = (procesoId) => {
  const [stackTech, setStackTech] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchStackTech = async () => {
    if (!procesoId) return;

    try {
      setLoading(true);
      setError(null);
      
      const response = await recomendacionesService.getStackTech(procesoId);
      setStackTech(response);
    } catch (err) {
      setError(err.message);
      setStackTech(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStackTech();
  }, [procesoId]);

  return {
    stackTech,
    loading,
    error,
    refetch: fetchStackTech
  };
};
