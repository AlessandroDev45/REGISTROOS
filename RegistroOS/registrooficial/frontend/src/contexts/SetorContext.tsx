import React, { createContext, useContext, useState, useCallback, ReactNode } from 'react';
import { ConfiguracaoSetor, SetorContextType as BaseSetorContextType } from '../pages/common/TiposApi';

// Extend or merge with BaseSetorContextType if necessary, or simply replace it.
// Assuming the merged TiposApi.ts is the canonical source for ConfiguracaoSetor
interface SetorContextType extends BaseSetorContextType {
    // Add any specific context properties if not already in BaseSetorContextType
}

const SetorContext = createContext<SetorContextType | undefined>(undefined);

export const SetorProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
    const [setorAtivo, setSetorAtivo] = useState<{ chave: string; nome: string } | null>(null);
    const [configuracaoAtual, setConfiguracaoAtual] = useState<ConfiguracaoSetor | null>(null);
    const [carregando, setCarregando] = useState(true);

    const alterarSetor = useCallback((chave: string, config: ConfiguracaoSetor) => {
        console.log(`[SetorContext] Setor ativo alterado para: ${chave}`);
        setSetorAtivo({ chave, nome: config.NomeSetor });
        setConfiguracaoAtual(config);
    }, []);

    const value = {
        setorAtivo,
        configuracaoAtual,
        alterarSetor,
        carregando,
        setCarregando
    };

    return (
        <SetorContext.Provider value={value}>
            {children}
        </SetorContext.Provider>
    );
};

export const useSetor = (): SetorContextType => {
    const context = useContext(SetorContext);
    if (!context) {
        throw new Error('useSetor deve ser usado dentro de um SetorProvider');
    }
    return context;
};
