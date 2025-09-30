import { useEffect, useRef, useCallback } from 'react';

/**
 * Hook personalizado para detectar cliques fora de um elemento
 * @param onClickOutside - Função a ser executada quando clicar fora
 * @returns ref - Referência para o elemento
 */
export const useClickOutside = <T extends HTMLElement>(
  onClickOutside: () => void
) => {
  const ref = useRef<T>(null);

  // Usar useCallback para estabilizar a função
  const handleClickOutside = useCallback((event: MouseEvent) => {
    if (ref.current && !ref.current.contains(event.target as Node)) {
      console.log('🖱️ [useClickOutside] Clique fora detectado, executando callback');
      onClickOutside();
    }
  }, [onClickOutside]);

  useEffect(() => {
    console.log('🖱️ [useClickOutside] Adicionando listener de clique');
    document.addEventListener('mousedown', handleClickOutside);

    return () => {
      console.log('🖱️ [useClickOutside] Removendo listener de clique');
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [handleClickOutside]);

  return ref;
};
