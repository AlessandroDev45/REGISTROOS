import React, { createContext, useContext, useState, useCallback, ReactNode } from 'react';
import { createApontamento } from '../services/api';

interface ApontamentoContextType {
    // Form data state
    formData: any;
    setFormData: (data: any) => void;
    testResults: any;
    testObservations: any;

    // Handler functions
    handleTestResultChange: (testId: string, result: string) => void;
    handleTestCheckboxChange: (testId: string, checked: boolean) => void;
    handleTestObservationChange: (testId: string, obs: string) => void;
    handleTesteExclusivoChange: (testeId: number, checked: boolean) => void;
    handleSupervisorHorasOrcadasChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
    handleSupervisorTestesIniciaisChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
    handleSupervisorTestesParciaisChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
    handleSupervisorTestesFinaisChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
    handleSaveApontamento: () => Promise<void>;
}

const ApontamentoContext = createContext<ApontamentoContextType | undefined>(undefined);

interface ApontamentoProviderProps {
    children: ReactNode;
}

export const ApontamentoProvider: React.FC<ApontamentoProviderProps> = ({ children }) => {
    const [formData, setFormData] = useState<any>({
        // Campos básicos da OS
        inpNumOS: '',
        statusOS: '',
        inpCliente: '',
        inpEquipamento: '',

        // Campos de seleção
        selMaq: '',
        selAtiv: '',
        selDescAtiv: '',

        // Campos de data/hora
        inpData: '',
        inpHora: '',
        inpDataFim: '',
        inpHoraFim: '',

        // Campos de retrabalho
        inpRetrabalho: false,
        selCausaRetrabalho: '',

        // Campos de observação e resultado - CORRIGIDO
        observacao: '',
        resultadoGlobal: '',

        // Campos hierárquicos
        categoriaSelecionada: '',
        subcategoriasSelecionadas: [],

        // Campos de testes
        testes: {},
        observacoes_testes: {},

        // Campos do supervisor
        supervisor_daimer: false,
        supervisor_carga: false,
        supervisor_horas_orcadas: 0,
        supervisor_testes_iniciais: false,
        supervisor_testes_parciais: false,
        supervisor_testes_finais: false,
    });

    const handleTestResultChange = useCallback((testId: string, result: string) => {
        setFormData((prev: { [key: string]: any }) => ({
            ...prev,
            testes: { ...prev.testes, [testId]: result }
        }));
    }, []);

    const handleTestCheckboxChange = useCallback((testId: string, checked: boolean) => {
        setFormData((prev: { [key: string]: any }) => ({
            ...prev,
            testes: {
                ...prev.testes,
                [testId]: checked ? 'INCONCLUSIVO' : undefined
            }
        }));
    }, []);

    const handleTestObservationChange = useCallback((testId: string, obs: string) => {
        setFormData((prev: any) => ({
            ...prev,
            observacoes_testes: { ...prev.observacoes_testes, [testId]: obs }
        }));
    }, []);

    const handleTesteExclusivoChange = useCallback((testeId: number, checked: boolean) => {
        // Este handler será implementado no componente específico
        console.log('Teste exclusivo alterado:', { testeId, checked });
    }, []);



    const handleSupervisorHorasOrcadasChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
        setFormData((prev: { [key: string]: any }) => ({
            ...prev,
            supervisor_horas_orcadas: parseFloat(e.target.value) || 0
        }));
    }, []);

    const handleSupervisorTestesIniciaisChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
        setFormData((prev: { [key: string]: any }) => ({
            ...prev,
            supervisor_testes_iniciais: e.target.checked
        }));
    }, []);

    const handleSupervisorTestesParciaisChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
        setFormData((prev: { [key: string]: any }) => ({
            ...prev,
            supervisor_testes_parciais: e.target.checked
        }));
    }, []);

    const handleSupervisorTestesFinaisChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
        setFormData((prev: { [key: string]: any }) => ({
            ...prev,
            supervisor_testes_finais: e.target.checked
        }));
    }, []);

    const handleSaveApontamento = useCallback(async () => {
        try {
            const payloadToSend = {
                ...formData,
                setor_responsavel: 'eletrica'
            };

            console.log("Payload para salvar:", payloadToSend);
            const result = await createApontamento(payloadToSend);
            alert(result.message || 'Apontamento salvo com sucesso!');
        } catch (error: any) {
            console.error('Erro ao salvar apontamento:', error);
            if (error.response && error.response.status === 401) {
                alert('Usuário não autenticado. Faça login novamente.');
            } else if (error.response && error.response.data && error.response.data.detail) {
                alert(`Erro ao salvar apontamento: ${error.response.data.detail}`);
            } else {
                alert('Ocorreu um erro ao tentar salvar o apontamento.');
            }
        }
    }, [formData]);

    const value: ApontamentoContextType = {
        formData,
        setFormData,
        testResults: formData.testes,
        testObservations: formData.observacoes_testes,
        handleTestResultChange,
        handleTestCheckboxChange,
        handleTestObservationChange,
        handleTesteExclusivoChange,
        handleSupervisorHorasOrcadasChange,
        handleSupervisorTestesIniciaisChange,
        handleSupervisorTestesParciaisChange,
        handleSupervisorTestesFinaisChange,
        handleSaveApontamento,
    };

    return (
        <ApontamentoContext.Provider value={value}>
            {children}
        </ApontamentoContext.Provider>
    );
};

export const useApontamento = (): ApontamentoContextType => {
    const context = useContext(ApontamentoContext);
    if (!context) {
        throw new Error('useApontamento deve ser usado dentro de um ApontamentoProvider');
    }
    return context;
};
