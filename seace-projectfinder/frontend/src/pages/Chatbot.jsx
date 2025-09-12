import React, { useState, useRef, useEffect } from 'react';
import { 
  PaperAirplaneIcon, 
  ChatBubbleLeftRightIcon,
  LightBulbIcon,
  TrashIcon,
  DocumentTextIcon,
  LinkIcon
} from '@heroicons/react/24/outline';
import { useChatbot, useChatbotSuggestions } from '../hooks/useChatbot';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { LoadingSpinner } from '../components/ui/Loading';
import { ErrorAlert } from '../components/ui/Alert';
import { utils } from '../services/seaceService';

export const Chatbot = () => {
  const [inputMessage, setInputMessage] = useState('');
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  const { 
    messages, 
    loading, 
    error, 
    sendMessage, 
    clearMessages 
  } = useChatbot();

  const { 
    suggestions, 
    loading: suggestionsLoading 
  } = useChatbotSuggestions();

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async () => {
    if (!inputMessage.trim() || loading) return;

    const message = inputMessage.trim();
    setInputMessage('');
    
    try {
      await sendMessage(message);
    } catch (err) {
      console.error('Error sending message:', err);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleSuggestionClick = (suggestion) => {
    setInputMessage(suggestion);
    inputRef.current?.focus();
  };

  return (
    <div className="h-full flex flex-col bg-white">
      {/* Welcome Message - Only show when no messages */}
      {messages.length === 0 && (
        <div className="p-6 text-center">
          <div className="w-12 h-12 bg-gradient-to-r from-seace-blue to-seace-blue-dark rounded-xl flex items-center justify-center mx-auto mb-3">
            <ChatBubbleLeftRightIcon className="w-6 h-6 text-white" />
          </div>
          <h3 className="text-lg font-semibold text-gray-900 mb-1">¡Hola! 👋</h3>
          <p className="text-sm text-gray-600 mb-4">
            Soy tu asistente IA para consultas SEACE. Puedo ayudarte con:
          </p>
          <div className="text-left space-y-2 text-xs text-gray-500 mb-4">
            <div className="flex items-center space-x-2">
              <div className="w-1.5 h-1.5 bg-seace-blue rounded-full"></div>
              <span>Buscar procesos específicos</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-1.5 h-1.5 bg-seace-green rounded-full"></div>
              <span>Recomendaciones de TI</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-1.5 h-1.5 bg-seace-orange rounded-full"></div>
              <span>Análisis de licitaciones</span>
            </div>
          </div>
        </div>
      )}

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto px-4 py-2 space-y-3">
        {messages.map((message) => (
          <MessageBubble key={message.id} message={message} />
        ))}
        
        {loading && (
          <div className="flex justify-start">
            <div className="bg-gray-100 rounded-2xl px-4 py-3 max-w-xs animate-pulse">
              <div className="flex items-center space-x-2">
                <div className="flex space-x-1">
                  <div className="w-2 h-2 bg-seace-blue rounded-full animate-bounce"></div>
                  <div className="w-2 h-2 bg-seace-blue rounded-full animate-bounce" style={{animationDelay: '0.1s'}}></div>
                  <div className="w-2 h-2 bg-seace-blue rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
                </div>
                <span className="text-xs text-gray-500">Pensando...</span>
              </div>
            </div>
          </div>
        )}
          
          <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="border-t p-3 bg-gray-50/50">
        {error && (
          <ErrorAlert 
            error={error} 
            onDismiss={() => {}} 
            className="mb-3"
          />
        )}

        <div className="flex items-end space-x-2">
          <div className="flex-1">
            <textarea
              ref={inputRef}
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Pregunta sobre procesos SEACE..."
              className="w-full px-3 py-2 border border-gray-200 rounded-xl resize-none focus:outline-none focus:ring-2 focus:ring-seace-blue/20 focus:border-seace-blue text-sm bg-white"
              rows={1}
              disabled={loading}
              style={{ minHeight: '36px', maxHeight: '120px' }}
            />
          </div>
          <button
            onClick={handleSendMessage}
            disabled={!inputMessage.trim() || loading}
            className="p-2 bg-seace-blue text-white rounded-xl disabled:opacity-50 disabled:cursor-not-allowed hover:bg-seace-blue-dark transition-colors"
          >
            <PaperAirplaneIcon className="w-4 h-4" />
          </button>
        </div>
        
        {/* Quick suggestions */}
        {messages.length === 0 && (
          <div className="mt-3 flex flex-wrap gap-2">
            {['Procesos TI', 'Licitaciones activas', 'Recomendaciones'].map((suggestion) => (
              <button
                key={suggestion}
                onClick={() => setInputMessage(suggestion)}
                className="px-3 py-1 text-xs bg-gray-100 hover:bg-gray-200 rounded-full transition-colors"
              >
                {suggestion}
              </button>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

const MessageBubble = ({ message }) => {
  const isUser = message.type === 'user';
  const isError = message.error;

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-3`}>
      {!isUser && (
        <div className="w-7 h-7 bg-gradient-to-r from-seace-blue to-seace-blue-dark rounded-full flex items-center justify-center mr-2 mt-1 flex-shrink-0">
          <span className="text-white text-xs font-semibold">AI</span>
        </div>
      )}
      
      <div className={`max-w-[280px] px-4 py-3 rounded-2xl ${
        isUser 
          ? 'bg-seace-blue text-white rounded-br-md' 
          : isError 
            ? 'bg-red-50 text-red-800 border border-red-200'
            : 'bg-gray-100 text-gray-800 rounded-bl-md'
      } shadow-sm`}>
        <div className="text-sm leading-relaxed whitespace-pre-wrap">
          {message.content}
        </div>
        
        {/* Sources */}
        {message.sources && message.sources.length > 0 && (
          <div className="mt-2 pt-2 border-t border-gray-300/50">
            <div className="text-xs text-gray-500 mb-1">📄 Fuentes:</div>
            <div className="space-y-1">
              {message.sources.slice(0, 2).map((source, index) => (
                <div key={index} className="flex items-center text-xs text-gray-600">
                  <span className="w-1 h-1 bg-seace-blue rounded-full mr-2"></span>
                  <span className="truncate">{source.title || source.codigo_proceso}</span>
                </div>
              ))}
            </div>
          </div>
        )}
        
        <div className="text-xs opacity-60 mt-2">
          {new Date(message.timestamp).toLocaleTimeString('es-PE', { 
            hour: '2-digit', 
            minute: '2-digit' 
          })}
        </div>
      </div>
      
      {isUser && (
        <div className="w-7 h-7 bg-seace-green rounded-full flex items-center justify-center ml-2 mt-1 flex-shrink-0">
          <span className="text-white text-xs font-semibold">Tú</span>
        </div>
      )}
    </div>
  );
};
