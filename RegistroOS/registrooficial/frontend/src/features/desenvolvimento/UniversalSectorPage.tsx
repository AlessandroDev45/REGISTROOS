import React, { Suspense, useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useSetor } from '../../contexts/SetorContext';
import { setorMap, initializeSetorMap, initializeAvailableSectors, getAvailableSectors } from './setorMap';
import DevelopmentTemplate from './DevelopmentTemplate';

const UniversalSectorPage: React.FC = () => {
    const { setor: setorChave } = useParams<{ setor: string }>();
    const navigate = useNavigate();
    const { alterarSetor, setCarregando } = useSetor();
    const [activeTab, setActiveTab] = useState('apontamento');
    const [setorNome, setSetorNome] = useState<string>('');
    const [sectorConfig, setSectorConfig] = useState<any>(null);

    const handleTabChange = (tab: string) => {
        console.log(`[UniversalSectorPage] Mudando para aba: ${tab}`);
        setActiveTab(tab);
    };

    useEffect(() => {
        const loadSector = async () => {
            if (!setorChave) {
                console.log('Nenhuma chave de setor fornecida');
                return;
            }

            console.log('Carregando setor:', setorChave);
            setCarregando(true);

            try {
                // Inicializar o mapa de setores dinamicamente
                await initializeSetorMap();
                await initializeAvailableSectors();

                // Verificar se o setor existe no mapa após inicialização
                if (!setorMap[setorChave]) {
                    console.error(`Setor ${setorChave} não encontrado no mapa`);

                    // Tentar buscar setores disponíveis para debug
                    const availableSectors = await getAvailableSectors();
                    console.log('Setores disponíveis:', availableSectors);

                    navigate('/desenvolvimento');
                    return;
                }

                // Carregar a configuração do setor
                const setorModule = setorMap[setorChave];
                const configModule = await setorModule.loadConfig();
                const config = configModule.default;

                // Armazenar a configuração para passar para a página
                setSectorConfig(config);

                alterarSetor(setorChave, config);

                if (config && config.NomeSetor) {
                    setSetorNome(config.NomeSetor);
                }

                console.log('Setor carregado com sucesso:', config);
            } catch (error) {
                console.error(`Falha ao carregar o módulo do setor ${setorChave}:`, error);
                navigate('/desenvolvimento');
            } finally {
                setCarregando(false);
            }
        };

        loadSector();
    }, [setorChave, alterarSetor, setCarregando, navigate]);

    if (!setorChave || !sectorConfig) {
        return (
            <div className="flex justify-center items-center h-64">
                <div className="text-center">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
                    <p className="text-gray-600">Carregando setor...</p>
                </div>
            </div>
        );
    }

    return (
        <DevelopmentTemplate
            sectorConfig={sectorConfig}
            sectorKey={setorChave}
        />
    );
};

export default UniversalSectorPage;