/**
 * Utilitários de Validação de Texto - RegistroOS
 * ===============================================
 *
 * Garante que todos os campos de texto aceitem apenas:
 * - Letras maiúsculas (A-Z)
 * - Números (0-9)
 * - Caracteres permitidos: espaço, hífen, underscore, ponto
 *
 * Bloqueia:
 * - Letras minúsculas
 * - Caracteres especiais não permitidos
 */

import React from 'react';

// Caracteres permitidos além de letras maiúsculas e números
const CARACTERES_PERMITIDOS = [
    ' ',  // Espaço
    '-',  // Hífen
    '_',  // Underscore
    '.',  // Ponto
    '/',  // Barra
    '(',  // Parêntese aberto
    ')',  // Parêntese fechado
];

// Regex para validação completa
const REGEX_TEXTO_VALIDO = /^[A-Z0-9\s\-_.\/()]*$/;

// Regex para caracteres não permitidos
const REGEX_CARACTERES_INVALIDOS = /[^A-Z0-9\s\-_.\/()]/g;

/**
 * Limpa o texto removendo caracteres não permitidos e convertendo para maiúscula
 */
export const limparTexto = (texto: string): string => {
    if (!texto) return '';
    
    // Converter para maiúscula e remover caracteres não permitidos
    return texto
        .toUpperCase()
        .replace(REGEX_CARACTERES_INVALIDOS, '');
};

/**
 * Valida se o texto contém apenas caracteres permitidos
 */
export const validarTexto = (texto: string): boolean => {
    if (!texto) return true; // Texto vazio é válido
    return REGEX_TEXTO_VALIDO.test(texto);
};

/**
 * Formata o texto em tempo real durante a digitação
 */
export const formatarTextoInput = (valor: string): string => {
    return limparTexto(valor);
};

/**
 * Handler para eventos de input que aplica validação automática
 */
export const criarHandlerTextoValidado = (
    setValue: (value: string) => void,
    onError?: (error: string | null) => void
) => {
    return (event: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
        const valorOriginal = event.target.value;
        const valorLimpo = formatarTextoInput(valorOriginal);
        
        // Atualizar o valor
        setValue(valorLimpo);
        
        // Verificar se houve mudança (caracteres inválidos removidos)
        if (valorOriginal !== valorLimpo && onError) {
            onError('Apenas letras maiúsculas, números e caracteres básicos são permitidos');
        } else if (onError) {
            onError(null);
        }
    };
};

/**
 * Propriedades para input com validação automática
 */
export const getPropsInputValidado = (
    value: string,
    onChange: (value: string) => void,
    onError?: (error: string | null) => void
) => {
    return {
        value,
        onChange: criarHandlerTextoValidado(onChange, onError),
        onPaste: (event: React.ClipboardEvent) => {
            // Interceptar paste para limpar o texto colado
            event.preventDefault();
            const textoPaste = event.clipboardData.getData('text');
            const textoLimpo = formatarTextoInput(textoPaste);
            onChange(textoLimpo);
            
            if (textoPaste !== textoLimpo && onError) {
                onError('Texto colado foi formatado para maiúsculas e caracteres válidos');
            }
        },
        style: { textTransform: 'uppercase' as const }
    };
};

/**
 * Componente de Input com validação automática
 */
interface InputValidadoProps {
    value: string;
    onChange: (value: string) => void;
    placeholder?: string;
    className?: string;
    disabled?: boolean;
    maxLength?: number;
    onError?: (error: string | null) => void;
    type?: 'text' | 'textarea';
    rows?: number;
}

export const InputValidado: React.FC<InputValidadoProps> = ({
    value,
    onChange,
    placeholder,
    className = '',
    disabled = false,
    maxLength,
    onError,
    type = 'text',
    rows = 3
}) => {
    const props = getPropsInputValidado(value, onChange, onError);
    
    const baseClassName = `
        block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 
        focus:outline-none focus:ring-blue-500 focus:border-blue-500
        disabled:bg-gray-100 disabled:cursor-not-allowed
        ${className}
    `.trim();

    if (type === 'textarea') {
        return (
            <textarea
                {...props}
                placeholder={placeholder}
                className={baseClassName}
                disabled={disabled}
                maxLength={maxLength}
                rows={rows}
            />
        );
    }

    return (
        <input
            type="text"
            {...props}
            placeholder={placeholder}
            className={baseClassName}
            disabled={disabled}
            maxLength={maxLength}
        />
    );
};

/**
 * Hook para gerenciar estado de campo com validação
 */
export const useCampoValidado = (valorInicial: string = '') => {
    const [valor, setValor] = React.useState(valorInicial);
    const [erro, setErro] = React.useState<string | null>(null);

    const atualizarValor = (novoValor: string) => {
        const valorLimpo = formatarTextoInput(novoValor);
        setValor(valorLimpo);
        
        if (novoValor !== valorLimpo) {
            setErro('Apenas letras maiúsculas, números e caracteres básicos são permitidos');
        } else {
            setErro(null);
        }
    };

    const limpar = () => {
        setValor('');
        setErro(null);
    };

    return {
        valor,
        erro,
        atualizarValor,
        limpar,
        props: getPropsInputValidado(valor, atualizarValor, setErro)
    };
};

/**
 * Validações específicas para diferentes tipos de campo
 */
export const validadores = {
    nomeCompleto: (texto: string): string | null => {
        if (!texto.trim()) return 'Nome é obrigatório';
        if (texto.length < 3) return 'Nome deve ter pelo menos 3 caracteres';
        if (!validarTexto(texto)) return 'Apenas letras maiúsculas e espaços são permitidos';
        return null;
    },

    descricao: (texto: string): string | null => {
        if (texto && texto.length > 500) return 'Descrição deve ter no máximo 500 caracteres';
        if (!validarTexto(texto)) return 'Apenas letras maiúsculas, números e caracteres básicos são permitidos';
        return null;
    },

    codigo: (texto: string): string | null => {
        if (!texto.trim()) return 'Código é obrigatório';
        if (!/^[A-Z0-9_-]+$/.test(texto)) return 'Código deve conter apenas letras maiúsculas, números, hífen e underscore';
        return null;
    },

    email: (texto: string): string | null => {
        if (!texto.trim()) return 'Email é obrigatório';
        // Para email, permitimos minúsculas mas convertemos
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(texto.toLowerCase())) return 'Email inválido';
        return null;
    }
};

/**
 * Aplicar validação a todos os inputs de um formulário
 */
export const aplicarValidacaoFormulario = (formElement: HTMLFormElement) => {
    const inputs = formElement.querySelectorAll('input[type="text"], textarea');
    
    inputs.forEach((input) => {
        const element = input as HTMLInputElement | HTMLTextAreaElement;
        
        // Aplicar formatação ao valor atual
        element.value = formatarTextoInput(element.value);
        
        // Adicionar event listeners
        element.addEventListener('input', (e) => {
            const target = e.target as HTMLInputElement | HTMLTextAreaElement;
            const valorOriginal = target.value;
            const valorLimpo = formatarTextoInput(valorOriginal);
            
            if (valorOriginal !== valorLimpo) {
                target.value = valorLimpo;
            }
        });
        
        element.addEventListener('paste', (e) => {
            e.preventDefault();
            const textoPaste = e.clipboardData?.getData('text') || '';
            const textoLimpo = formatarTextoInput(textoPaste);
            element.value = textoLimpo;
            
            // Disparar evento de input para atualizar estado
            element.dispatchEvent(new Event('input', { bubbles: true }));
        });
    });
};

export default {
    limparTexto,
    validarTexto,
    formatarTextoInput,
    criarHandlerTextoValidado,
    getPropsInputValidado,
    InputValidado,
    useCampoValidado,
    validadores,
    aplicarValidacaoFormulario
};
