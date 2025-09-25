import React, { useState } from 'react';

interface Etapa {
    numero: number;
    titulo: string;
    componente: React.ComponentType<any>;
    props?: any;
}

interface FormularioEtapasProps {
    etapas: Etapa[];
    dadosIniciais?: any;
    onSalvar?: (dados: any) => void;
    onCancelar?: () => void;
}

const FormularioEtapas: React.FC<FormularioEtapasProps> = ({
    etapas,
    dadosIniciais = {},
    onSalvar,
    onCancelar
}) => {
    const [etapaAtual, setEtapaAtual] = useState(0);
    const [dados, setDados] = useState(dadosIniciais);

    const etapa = etapas[etapaAtual];
    const ComponenteEtapa = etapa?.componente;

    const avancarEtapa = () => {
        if (etapaAtual < etapas.length - 1) {
            setEtapaAtual(etapaAtual + 1);
        }
    };

    const voltarEtapa = () => {
        if (etapaAtual > 0) {
            setEtapaAtual(etapaAtual - 1);
        }
    };

    const atualizarDados = (novosDados: any) => {
        setDados(prev => ({ ...prev, ...novosDados }));
    };

    const handleSalvar = () => {
        if (onSalvar) {
            onSalvar(dados);
        }
    };

    if (!etapa || !ComponenteEtapa) {
        return (
            <div className="text-center py-8 text-gray-500">
                Nenhuma etapa configurada
            </div>
        );
    }

    return (
        <div className="max-w-4xl mx-auto">
            {/* Indicador de Progresso */}
            <div className="mb-8">
                <div className="flex items-center justify-between mb-4">
                    {etapas.map((etapaItem, index) => (
                        <div key={index} className="flex items-center">
                            <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${
                                index <= etapaAtual
                                    ? 'bg-blue-600 text-white'
                                    : 'bg-gray-200 text-gray-600'
                            }`}>
                                {index + 1}
                            </div>
                            <span className={`ml-2 text-sm ${
                                index <= etapaAtual ? 'text-blue-600 font-medium' : 'text-gray-500'
                            }`}>
                                {etapaItem.titulo}
                            </span>
                            {index < etapas.length - 1 && (
                                <div className={`w-12 h-0.5 mx-4 ${
                                    index < etapaAtual ? 'bg-blue-600' : 'bg-gray-200'
                                }`} />
                            )}
                        </div>
                    ))}
                </div>
            </div>

            {/* Conteúdo da Etapa */}
            <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
                <ComponenteEtapa
                    {...etapa.props}
                    dados={dados}
                    onChange={atualizarDados}
                />
            </div>

            {/* Controles de Navegação */}
            <div className="flex justify-between items-center">
                <div>
                    {etapaAtual > 0 && (
                        <button
                            onClick={voltarEtapa}
                            className="px-6 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50 transition-colors"
                        >
                            ← Voltar
                        </button>
                    )}
                </div>

                <div className="flex space-x-3">
                    {onCancelar && (
                        <button
                            onClick={onCancelar}
                            className="px-6 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50 transition-colors"
                        >
                            Cancelar
                        </button>
                    )}

                    {etapaAtual < etapas.length - 1 ? (
                        <button
                            onClick={avancarEtapa}
                            className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
                        >
                            Próxima Etapa →
                        </button>
                    ) : (
                        <button
                            onClick={handleSalvar}
                            className="px-6 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors"
                        >
                            💾 Salvar Apontamento
                        </button>
                    )}
                </div>
            </div>
        </div>
    );
};

export default FormularioEtapas;