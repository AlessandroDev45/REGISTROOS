import React from 'react';
import { useSetor } from '../contexts/SetorContext';
import { availableSectors } from '../features/desenvolvimento/setorMap'; // Ajuste o caminho se necessário

const SetorSelector: React.FC = () => {
    const { setorAtivo, alterarSetor } = useSetor();

    const handleSetorChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
        const novaChave = e.target.value;
        // Encontra o nome do setor para o contexto
        const setorNome = novaChave.charAt(0).toUpperCase() + novaChave.slice(1).replace('-', ' ');

        // Criar configuração básica
        const config = {
            NomeSetor: setorNome,
            ChaveSetor: novaChave,
            EsquemaCamposOS: {},
            DicionarioTestes: {},
            ListaAtividades: [],
            ComponentesFormularioPrincipal: [],
            ConfiguracaoBackend: {
                endPointApontamento: '/api/apontamentos',
                endPointOrdemServico: '/api/ordens-servico'
            }
        };

        alterarSetor(novaChave, config);
    };

    return (
        <div className="mb-6"> {/* Ajuste a margem conforme o layout */}
            <label htmlFor="setor-select" className="block text-sm font-medium text-gray-700 mb-2">Selecionar Setor</label>
            <select
                id="setor-select"
                value={setorAtivo?.chave || ''}
                onChange={handleSetorChange}
                className="w-full md:w-auto px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            >
                {availableSectors.map(chave => {
                    const nome = chave.charAt(0).toUpperCase() + chave.slice(1).replace('-', ' ');
                    return (
                        <option key={chave} value={chave}>{nome}</option>
                    );
                })}
            </select>
        </div>
    );
};

export default SetorSelector;
