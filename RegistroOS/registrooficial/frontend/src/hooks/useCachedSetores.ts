import { useState, useEffect, useCallback } from 'react';
import { setorService } from '../services/adminApi';

interface Setor {
  id: number;
  nome: string;
  departamento: string;
  ativo: boolean;
}

interface UseSetoresReturn {
  setoresMotores: Setor[];
  setoresTransformadores: Setor[];
  todosSetores: Setor[];
  loading: boolean;
  error: string | null;
  refreshSetores: () => Promise<void>;
}

// Global cache for sectors
let cachedSetoresMotores: Setor[] = [];
let cachedSetoresTransformadores: Setor[] = [];
let isGlobalLoading = false;
let globalError: string | null = null;

export const useCachedSetores = (): UseSetoresReturn => {
  const [setoresMotores, setSetoresMotores] = useState<Setor[]>(cachedSetoresMotores);
  const [setoresTransformadores, setSetoresTransformadores] = useState<Setor[]>(cachedSetoresTransformadores);
  const [loading, setLoading] = useState<boolean>(isGlobalLoading);
  const [error, setError] = useState<string | null>(globalError);

  const carregarSetores = useCallback(async () => {
    if (isGlobalLoading) return; // Prevent multiple simultaneous fetches

    setLoading(true);
    setError(null);
    isGlobalLoading = true;
    globalError = null;

    try {
      const setores = await setorService.getSetores();

      const motores = setores
        .filter(setor => setor.departamento === 'MOTORES' && setor.ativo);

      const transformadores = setores
        .filter(setor => setor.departamento === 'TRANSFORMADORES' && setor.ativo);

      cachedSetoresMotores = motores;
      cachedSetoresTransformadores = transformadores;

      setSetoresMotores(motores);
      setSetoresTransformadores(transformadores);

    } catch (err) {
      const errorMessage = 'Erro ao carregar setores';
      setError(errorMessage);
      globalError = errorMessage;
      console.error(err);
    } finally {
      setLoading(false);
      isGlobalLoading = false;
    }
  }, []);

  useEffect(() => {
    // If cache is empty and not already loading, trigger fetch
    if (cachedSetoresMotores.length === 0 && !isGlobalLoading) {
      carregarSetores();
    } else {
      // Otherwise, update state from cache (useful for re-mounts)
      setSetoresMotores(cachedSetoresMotores);
      setSetoresTransformadores(cachedSetoresTransformadores);
      setLoading(isGlobalLoading);
      setError(globalError);
    }
  }, [carregarSetores]);

  const todosSetores = [...setoresMotores, ...setoresTransformadores];

  return {
    setoresMotores,
    setoresTransformadores,
    todosSetores,
    loading,
    error,
    refreshSetores: carregarSetores
  };
};
