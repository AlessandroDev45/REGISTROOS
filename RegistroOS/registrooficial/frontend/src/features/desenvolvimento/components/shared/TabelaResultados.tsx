import React from 'react';

interface Coluna {
    chave: string;
    titulo: string;
    render?: (valor: any, item: any) => React.ReactNode;
    className?: string;
}

interface TabelaResultadosProps {
    dados: any[];
    colunas: Coluna[];
    loading?: boolean;
    mensagemVazia?: string;
    onRowClick?: (item: any) => void;
}

const TabelaResultados: React.FC<TabelaResultadosProps> = ({
    dados,
    colunas,
    loading = false,
    mensagemVazia = "Nenhum resultado encontrado",
    onRowClick
}) => {
    if (loading) {
        return (
            <div className="flex items-center justify-center py-8">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
                <span className="ml-2 text-gray-600">Carregando dados...</span>
            </div>
        );
    }

    if (dados.length === 0) {
        return (
            <div className="text-center py-8 text-gray-500">
                {mensagemVazia}
            </div>
        );
    }

    return (
        <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                    <tr>
                        {colunas.map((coluna) => (
                            <th
                                key={coluna.chave}
                                className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                            >
                                {coluna.titulo}
                            </th>
                        ))}
                    </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                    {dados.map((item, index) => (
                        <tr
                            key={item.id || index}
                            className={`hover:bg-gray-50 ${onRowClick ? 'cursor-pointer' : ''}`}
                            onClick={() => onRowClick?.(item)}
                        >
                            {colunas.map((coluna) => (
                                <td
                                    key={coluna.chave}
                                    className={`px-6 py-4 whitespace-nowrap text-sm text-gray-900 ${coluna.className || ''}`}
                                >
                                    {coluna.render
                                        ? coluna.render(item[coluna.chave], item)
                                        : item[coluna.chave] || '-'
                                    }
                                </td>
                            ))}
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
};

export default TabelaResultados;