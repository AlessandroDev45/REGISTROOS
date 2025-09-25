/**
 * Provedor de Validação Global para Formulários - RegistroOS
 * ==========================================================
 * 
 * Aplica automaticamente validação de texto maiúsculo em todos os formulários
 * da aplicação sem necessidade de modificar cada componente individualmente.
 */

import React, { useEffect, useRef } from 'react';
import { formatarTextoInput } from '../utils/textValidation';

interface FormValidationProviderProps {
    children: React.ReactNode;
    enabled?: boolean;
}

/**
 * Componente que aplica validação automática a todos os inputs de texto
 * dentro de seus filhos
 */
export const FormValidationProvider: React.FC<FormValidationProviderProps> = ({
    children,
    enabled = true
}) => {
    const containerRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        if (!enabled || !containerRef.current) return;

        const container = containerRef.current;

        // Função para aplicar validação a um elemento
        const aplicarValidacao = (element: HTMLInputElement | HTMLTextAreaElement) => {
            // Pular se já tem validação aplicada
            if (element.dataset.validacaoAplicada === 'true') return;

            // Marcar como validado
            element.dataset.validacaoAplicada = 'true';

            // Aplicar estilo de maiúscula
            element.style.textTransform = 'uppercase';

            // Formatar valor inicial
            if (element.value) {
                const valorFormatado = formatarTextoInput(element.value);
                if (valorFormatado !== element.value) {
                    element.value = valorFormatado;
                    // Disparar evento para atualizar estado do React
                    element.dispatchEvent(new Event('input', { bubbles: true }));
                }
            }

            // Handler para input
            const handleInput = (e: Event) => {
                const target = e.target as HTMLInputElement | HTMLTextAreaElement;
                const valorOriginal = target.value;
                const valorLimpo = formatarTextoInput(valorOriginal);
                
                if (valorOriginal !== valorLimpo) {
                    target.value = valorLimpo;
                    // Disparar evento novamente para sincronizar com React
                    target.dispatchEvent(new Event('input', { bubbles: true }));
                }
            };

            // Handler para paste
            const handlePaste = (e: ClipboardEvent) => {
                e.preventDefault();
                const textoPaste = e.clipboardData?.getData('text') || '';
                const textoLimpo = formatarTextoInput(textoPaste);
                
                const target = e.target as HTMLInputElement | HTMLTextAreaElement;
                target.value = textoLimpo;
                target.dispatchEvent(new Event('input', { bubbles: true }));
            };

            // Adicionar event listeners
            element.addEventListener('input', handleInput);
            element.addEventListener('paste', handlePaste);

            // Cleanup function
            const cleanup = () => {
                element.removeEventListener('input', handleInput);
                element.removeEventListener('paste', handlePaste);
                delete element.dataset.validacaoAplicada;
            };

            // Armazenar cleanup para uso posterior
            (element as any).__validacaoCleanup = cleanup;
        };

        // Função para processar todos os inputs existentes
        const processarInputsExistentes = () => {
            const inputs = container.querySelectorAll('input[type="text"], textarea');
            inputs.forEach((input) => {
                aplicarValidacao(input as HTMLInputElement | HTMLTextAreaElement);
            });
        };

        // Processar inputs existentes
        processarInputsExistentes();

        // Observer para novos elementos
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                mutation.addedNodes.forEach((node) => {
                    if (node.nodeType === Node.ELEMENT_NODE) {
                        const element = node as Element;
                        
                        // Verificar se o próprio elemento é um input
                        if (element.matches('input[type="text"], textarea')) {
                            aplicarValidacao(element as HTMLInputElement | HTMLTextAreaElement);
                        }
                        
                        // Verificar inputs filhos
                        const childInputs = element.querySelectorAll('input[type="text"], textarea');
                        childInputs.forEach((input) => {
                            aplicarValidacao(input as HTMLInputElement | HTMLTextAreaElement);
                        });
                    }
                });
            });
        });

        // Iniciar observação
        observer.observe(container, {
            childList: true,
            subtree: true
        });

        // Cleanup
        return () => {
            observer.disconnect();
            
            // Limpar validações aplicadas
            const inputs = container.querySelectorAll('input[type="text"], textarea');
            inputs.forEach((input) => {
                const element = input as any;
                if (element.__validacaoCleanup) {
                    element.__validacaoCleanup();
                }
            });
        };
    }, [enabled]);

    return (
        <div ref={containerRef} style={{ display: 'contents' }}>
            {children}
        </div>
    );
};

/**
 * Hook para aplicar validação manual a um formulário específico
 */
export const useFormValidation = (formRef: React.RefObject<HTMLFormElement>) => {
    useEffect(() => {
        if (!formRef.current) return;

        const form = formRef.current;
        const inputs = form.querySelectorAll('input[type="text"], textarea');

        inputs.forEach((input) => {
            const element = input as HTMLInputElement | HTMLTextAreaElement;
            
            // Aplicar estilo
            element.style.textTransform = 'uppercase';
            
            // Formatar valor inicial
            if (element.value) {
                element.value = formatarTextoInput(element.value);
            }

            // Handler para input
            const handleInput = (e: Event) => {
                const target = e.target as HTMLInputElement | HTMLTextAreaElement;
                const valorOriginal = target.value;
                const valorLimpo = formatarTextoInput(valorOriginal);
                
                if (valorOriginal !== valorLimpo) {
                    target.value = valorLimpo;
                }
            };

            // Handler para paste
            const handlePaste = (e: ClipboardEvent) => {
                e.preventDefault();
                const textoPaste = e.clipboardData?.getData('text') || '';
                const textoLimpo = formatarTextoInput(textoPaste);
                element.value = textoLimpo;
                element.dispatchEvent(new Event('input', { bubbles: true }));
            };

            element.addEventListener('input', handleInput);
            element.addEventListener('paste', handlePaste);
        });
    }, [formRef]);
};

/**
 * Componente wrapper para formulários com validação automática
 */
interface ValidatedFormProps {
    children: React.ReactNode;
    onSubmit?: (e: React.FormEvent) => void;
    className?: string;
}

export const ValidatedForm: React.FC<ValidatedFormProps> = ({
    children,
    onSubmit,
    className
}) => {
    const formRef = useRef<HTMLFormElement>(null);
    
    useFormValidation(formRef);

    return (
        <form ref={formRef} onSubmit={onSubmit} className={className}>
            {children}
        </form>
    );
};

export default FormValidationProvider;
