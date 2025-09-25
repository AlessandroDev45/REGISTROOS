import React, { useEffect, useState } from 'react';
import { Button, FlexContainer } from './UIComponents';
import { useAuth } from '../contexts/AuthContext';
import { availableSectors, setorMap } from '../features/desenvolvimento/setorMap';
import { useNavigate } from 'react-router-dom';

interface SectorSelectorProps {
    children: React.ReactNode;
    show?: boolean; // Prop opcional para controlar a exibição
}

const SectorSelector: React.FC<SectorSelectorProps> = ({ children, show: propShow }) => {
    const { user, selectedSector, setSelectedSector, isAdmin, logout } = useAuth();
    const navigate = useNavigate();
    const [internalShowSelector, setInternalShowSelector] = useState(false);
    const [sectorConfigs, setSectorConfigs] = useState<Record<string, any>>({});

    // Se `show` for passado via props, usa-o. Caso contrário, usa a lógica interna.
    const showSelector = propShow !== undefined ? propShow : internalShowSelector;

    // Carregar configurações dos setores disponíveis
    useEffect(() => {
        const loadSectorConfigs = async () => {
            const configs: Record<string, any> = {};
            for (const sectorKey of availableSectors) {
                try {
                    const configModule = await setorMap[sectorKey].loadConfig();
                    configs[sectorKey] = configModule.default;
                } catch (error) {
                    console.error(`Erro ao carregar configuração do setor ${sectorKey}:`, error);
                }
            }
            setSectorConfigs(configs);
        };

        if (showSelector) {
            loadSectorConfigs();
        }
    }, [showSelector]);

    useEffect(() => {
        // Esta lógica interna só se aplica se `show` não for passado via props
        if (propShow === undefined && isAdmin && !selectedSector && user) {
            setInternalShowSelector(true);
        }
    }, [isAdmin, selectedSector, user, propShow]);

    useEffect(() => {
        // Esse efeito é mais para o comportamento interno do seletor.
        // Se `showSelector` se tornou falso (por exemplo, `selectedSector` foi definido),
        // e `propShow` não está forçando a exibição, então `internalShowSelector` deve ser atualizado.
        if (propShow === undefined && selectedSector && showSelector) {
             // A condição `showSelector` já é true, então SelectedSector foi definido.
             // Isso significa que a seleção foi feita e o seletor deve ser ocultado internamente.
             // No entanto, a renderização é controlada apenas por `showSelector` final.
             // Se `propShow` for true, o seletor continuará visível até que `propShow` se torne falso.
             // Se `propShow` for undefined, então podemos ocultar o seletor interno.
             setInternalShowSelector(false);
        }
    }, [selectedSector, showSelector, propShow]);

    const handleSectorChange = (sector: string) => {
        setSelectedSector(sector);
    };

    const handleCancel = async () => {
        try {
            console.log('SectorSelector: Cancelando e fazendo logout...');
            await logout();
            console.log('SectorSelector: Logout concluído, redirecionando...');

            // Redirecionar imediatamente
            window.location.href = '/login';

        } catch (error) {
            console.error('SectorSelector: Erro durante logout:', error);

            // Mesmo com erro, forçar redirecionamento
            window.location.href = '/login';
        }
    };

    // Função para formatar o nome do setor
    const formatSectorName = (sectorKey: string): string => {
        const config = sectorConfigs[sectorKey];
        return config?.NomeSetor || sectorKey.replace(/-/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
    };

    if (!showSelector) {
        return <>{children}</>;
    }

    // Se showSelector é true (por props ou lógica interna), renderiza o modal de seleção
    return (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white p-6 rounded-lg shadow-lg max-w-md w-full mx-4">
                <h3 className="text-lg font-semibold mb-4">Selecione um Setor</h3>
                <p className="mb-6">Como administrador, você precisa selecionar um setor para acessar as páginas de desenvolvimento.</p>

                <FlexContainer className="flex-col space-y-3 mb-6">
                    {availableSectors.map((sectorKey) => (
                        <Button
                            key={sectorKey}
                            onClick={() => handleSectorChange(sectorKey)}
                            className="btn-primary"
                        >
                            {formatSectorName(sectorKey)}
                        </Button>
                    ))}
                </FlexContainer>

                <div className="flex justify-end space-x-4">
                    <Button onClick={handleCancel} className="btn-outline">
                        Sair
                    </Button>
                </div>
            </div>
        </div>
    );
};

export default SectorSelector;
