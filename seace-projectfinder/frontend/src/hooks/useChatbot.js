import { useState, useEffect, useCallback } from 'react';
import { chatbotService, utils } from '../services/seaceService';

export const useChatbot = () => {
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [sessionId, setSessionId] = useState(null);
  const [error, setError] = useState(null);

  // Inicializar sesión
  useEffect(() => {
    const newSessionId = utils.generateSessionId();
    setSessionId(newSessionId);
    
    // Mensaje de bienvenida
    const welcomeMessage = {
      id: Date.now(),
      type: 'bot',
      content: '¡Hola! Soy el asistente de SEACE ProjectFinder. ¿En qué puedo ayudarte hoy?',
      timestamp: new Date().toISOString()
    };
    
    setMessages([welcomeMessage]);
  }, []);

  const sendMessage = async (content, context = {}) => {
    if (!content.trim()) return;

    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: content.trim(),
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);
    setLoading(true);
    setError(null);

    try {
      const response = await chatbotService.query({
        query: content.trim(),
        session_id: sessionId,
        context: context
      });

      const botMessage = {
        id: Date.now() + 1,
        type: 'bot',
        content: response.response,
        metadata: response.metadata,
        sources: response.sources,
        timestamp: new Date().toISOString()
      };

      setMessages(prev => [...prev, botMessage]);
    } catch (err) {
      setError(err.message);
      
      const errorMessage = {
        id: Date.now() + 1,
        type: 'bot',
        content: 'Lo siento, ha ocurrido un error. Por favor, intenta nuevamente.',
        error: true,
        timestamp: new Date().toISOString()
      };
      
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const clearMessages = useCallback(() => {
    const newSessionId = utils.generateSessionId();
    setSessionId(newSessionId);
    setMessages([{
      id: Date.now(),
      type: 'bot',
      content: '¡Hola! Soy el asistente de SEACE ProjectFinder. ¿En qué puedo ayudarte hoy?',
      timestamp: new Date().toISOString()
    }]);
    setError(null);
  }, []);

  return {
    messages,
    loading,
    sessionId,
    error,
    sendMessage,
    clearMessages
  };
};

export const useChatbotSuggestions = () => {
  const [suggestions, setSuggestions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchSuggestions = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await chatbotService.getSuggestions();
      setSuggestions(response.suggestions || []);
    } catch (err) {
      setError(err.message);
      setSuggestions([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSuggestions();
  }, []);

  return {
    suggestions,
    loading,
    error,
    refetch: fetchSuggestions
  };
};
