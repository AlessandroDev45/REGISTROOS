/**
 * HOOK PARA SCRAPING ASSÍNCRONO
 * =============================
 * 
 * Hook React para gerenciar scraping assíncrono de OSs
 * Suporta fallback automático para scraping síncrono
 */

import { useState, useCallback } from 'react';
import { message } from 'antd';

interface ScrapingResult {
  status: string;
  message: string;
  data?: any;
  fonte?: string;
  task_id?: string;
  estimated_time?: string;
}

interface UseAsyncScrapingReturn {
  isLoading: boolean;
  startScraping: (numeroOS: string) => Promise<ScrapingResult | null>;
  currentTaskId: string | null;
  error: string | null;
  clearError: () => void;
}

export const useAsyncScraping = (): UseAsyncScrapingReturn => {
  const [isLoading, setIsLoading] = useState(false);
  const [currentTaskId, setCurrentTaskId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const clearError = useCallback(() => {
    setError(null);
  }, []);

  const startScraping = useCallback(async (numeroOS: string): Promise<ScrapingResult | null> => {
    if (!numeroOS || !numeroOS.trim()) {
      setError('Número da OS é obrigatório');
      return null;
    }

    setIsLoading(true);
    setError(null);
    setCurrentTaskId(null);

    try {
      // 1. Tentar scraping assíncrono primeiro
      console.log(`🚀 Iniciando scraping assíncrono para OS ${numeroOS}`);
      
      const asyncResponse = await fetch(`/api/desenvolvimento/buscar-os-async/${numeroOS}`, {
        method: 'POST',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
        }
      });

      if (!asyncResponse.ok) {
        throw new Error(`HTTP ${asyncResponse.status}: ${asyncResponse.statusText}`);
      }

      const asyncResult = await asyncResponse.json();
      console.log('📊 Resultado scraping assíncrono:', asyncResult);

      // 2. Processar resultado
      if (asyncResult.status === 'found_existing') {
        // OS já existe no banco
        setIsLoading(false);
        message.success(`OS ${numeroOS} encontrada no sistema local`);
        return asyncResult;
        
      } else if (asyncResult.status === 'queued') {
        // Scraping iniciado - retornar task_id para monitoramento
        setCurrentTaskId(asyncResult.task_id);
        message.info(`OS ${numeroOS} adicionada à fila de processamento`);
        return asyncResult;
        
      } else if (asyncResult.status === 'error') {
        // Erro no scraping assíncrono - tentar fallback
        console.warn('⚠️ Erro no scraping assíncrono, tentando fallback síncrono');
        return await fallbackToSyncScraping(numeroOS);
        
      } else {
        // Status desconhecido
        throw new Error(`Status desconhecido: ${asyncResult.status}`);
      }

    } catch (error) {
      console.error('❌ Erro no scraping assíncrono:', error);
      
      // Fallback para scraping síncrono
      console.log('🔄 Tentando fallback para scraping síncrono...');
      return await fallbackToSyncScraping(numeroOS);
    }
  }, []);

  const fallbackToSyncScraping = async (numeroOS: string): Promise<ScrapingResult | null> => {
    try {
      console.log(`🔄 Executando scraping síncrono (fallback) para OS ${numeroOS}`);
      
      const syncResponse = await fetch(`/api/desenvolvimento/formulario/buscar-os/${numeroOS}`, {
        method: 'GET',
        credentials: 'include'
      });

      if (!syncResponse.ok) {
        throw new Error(`HTTP ${syncResponse.status}: ${syncResponse.statusText}`);
      }

      const syncResult = await syncResponse.json();
      console.log('📊 Resultado scraping síncrono:', syncResult);

      setIsLoading(false);

      if (syncResult.erro) {
        setError(syncResult.erro);
        message.error(`Erro no scraping: ${syncResult.erro}`);
        return null;
      }

      if (syncResult.dados) {
        message.success(`OS ${numeroOS} coletada com sucesso (modo síncrono)`);
        return {
          status: 'success',
          message: 'OS coletada com sucesso',
          data: syncResult.dados,
          fonte: 'scraping_sincrono'
        };
      }

      throw new Error('Nenhum dado retornado do scraping síncrono');

    } catch (error) {
      console.error('❌ Erro no scraping síncrono (fallback):', error);
      setIsLoading(false);
      
      const errorMessage = error instanceof Error ? error.message : 'Erro desconhecido';
      setError(errorMessage);
      message.error(`Erro no scraping: ${errorMessage}`);
      
      return null;
    }
  };

  return {
    isLoading,
    startScraping,
    currentTaskId,
    error,
    clearError
  };
};

// Hook para monitorar status de uma task específica
export const useScrapingStatus = (taskId: string | null) => {
  const [status, setStatus] = useState<any>(null);
  const [isPolling, setIsPolling] = useState(false);

  const checkStatus = useCallback(async () => {
    if (!taskId) return null;

    try {
      const response = await fetch(`/api/desenvolvimento/scraping-status/${taskId}`, {
        credentials: 'include'
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const data = await response.json();
      setStatus(data);
      return data;

    } catch (error) {
      console.error('Erro ao verificar status:', error);
      return null;
    }
  }, [taskId]);

  const startPolling = useCallback(() => {
    if (!taskId || isPolling) return;

    setIsPolling(true);
    const interval = setInterval(async () => {
      const statusData = await checkStatus();
      
      if (statusData && (statusData.status === 'SUCCESS' || statusData.status === 'FAILURE')) {
        setIsPolling(false);
        clearInterval(interval);
      }
    }, 5000);

    return () => {
      clearInterval(interval);
      setIsPolling(false);
    };
  }, [taskId, isPolling, checkStatus]);

  const stopPolling = useCallback(() => {
    setIsPolling(false);
  }, []);

  return {
    status,
    isPolling,
    checkStatus,
    startPolling,
    stopPolling
  };
};

export default useAsyncScraping;
