import { useState, useEffect } from 'react';
import { adminService } from '../services/seaceService';

export const useAdminStatus = () => {
  const [status, setStatus] = useState({
    etl: null,
    health: null,
    system: null
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchAllStatus = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const [etlStatus, healthStatus, systemStatus] = await Promise.all([
        adminService.getETLStatus(),
        adminService.healthCheck(),
        adminService.getSystemStatus()
      ]);
      
      setStatus({
        etl: etlStatus,
        health: healthStatus,
        system: systemStatus
      });
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAllStatus();
    
    // Actualizar cada 30 segundos
    const interval = setInterval(fetchAllStatus, 30000);
    
    return () => clearInterval(interval);
  }, []);

  return {
    status,
    loading,
    error,
    refetch: fetchAllStatus
  };
};

export const useETLOperations = () => {
  const [operations, setOperations] = useState({
    dailySync: { loading: false, error: null, result: null },
    fullSync: { loading: false, error: null, result: null },
    tiSync: { loading: false, error: null, result: null },
    generateEmbeddings: { loading: false, error: null, result: null }
  });

  const runDailySync = async () => {
    try {
      setOperations(prev => ({
        ...prev,
        dailySync: { loading: true, error: null, result: null }
      }));
      
      const result = await adminService.runDailySync();
      
      setOperations(prev => ({
        ...prev,
        dailySync: { loading: false, error: null, result }
      }));
      
      return result;
    } catch (err) {
      setOperations(prev => ({
        ...prev,
        dailySync: { loading: false, error: err.message, result: null }
      }));
      throw err;
    }
  };

  const runFullSync = async (daysBack = 365) => {
    try {
      setOperations(prev => ({
        ...prev,
        fullSync: { loading: true, error: null, result: null }
      }));
      
      const result = await adminService.runFullSync(daysBack);
      
      setOperations(prev => ({
        ...prev,
        fullSync: { loading: false, error: null, result }
      }));
      
      return result;
    } catch (err) {
      setOperations(prev => ({
        ...prev,
        fullSync: { loading: false, error: err.message, result: null }
      }));
      throw err;
    }
  };

  const runTISync = async () => {
    try {
      setOperations(prev => ({
        ...prev,
        tiSync: { loading: true, error: null, result: null }
      }));
      
      const result = await adminService.runTISync();
      
      setOperations(prev => ({
        ...prev,
        tiSync: { loading: false, error: null, result }
      }));
      
      return result;
    } catch (err) {
      setOperations(prev => ({
        ...prev,
        tiSync: { loading: false, error: err.message, result: null }
      }));
      throw err;
    }
  };

  const generateEmbeddings = async (batchSize = 50) => {
    try {
      setOperations(prev => ({
        ...prev,
        generateEmbeddings: { loading: true, error: null, result: null }
      }));
      
      const result = await adminService.generateEmbeddings(batchSize);
      
      setOperations(prev => ({
        ...prev,
        generateEmbeddings: { loading: false, error: null, result }
      }));
      
      return result;
    } catch (err) {
      setOperations(prev => ({
        ...prev,
        generateEmbeddings: { loading: false, error: err.message, result: null }
      }));
      throw err;
    }
  };

  const clearOperationResult = (operationType) => {
    setOperations(prev => ({
      ...prev,
      [operationType]: { loading: false, error: null, result: null }
    }));
  };

  return {
    operations,
    runDailySync,
    runFullSync,
    runTISync,
    generateEmbeddings,
    clearOperationResult
  };
};

export const useStats = () => {
  const [stats, setStats] = useState({
    procesos: null,
    chatbot: null
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchStats = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Importar servicios necesarios
      const { procesosService, chatbotService } = await import('../services/seaceService');
      
      const [procesosStats, chatbotStats] = await Promise.all([
        procesosService.getStats(),
        chatbotService.getStats()
      ]);
      
      setStats({
        procesos: procesosStats,
        chatbot: chatbotStats
      });
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStats();
  }, []);

  return {
    stats,
    loading,
    error,
    refetch: fetchStats
  };
};
