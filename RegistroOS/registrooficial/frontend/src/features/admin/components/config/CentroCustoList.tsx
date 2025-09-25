import React, { useState } from 'react';
import { CentroCustoData } from '../../../../services/adminApi';

interface CentroCustoListProps {
    data?: CentroCustoData[];
    onEdit: (centro: CentroCustoData) => void;
    onDelete: (centro: CentroCustoData) => void;
    onCreateNew: () => void;
    loading: boolean;
    error: string | null;
}

const CentroCustoList: React.FC<CentroCustoListProps> = ({ data: centrosCusto = [], onEdit, onDelete, onCreateNew, loading, error }) => {
    const [deletingId, setDeletingId] = useState<number | null>(null);



    const handleDeleteClick = async (centro: CentroCustoData) => {
        if (!window.confirm(`Tem certeza de que deseja deletar o departamento "${centro.nome}"?`)) {
            return;
        }
        setDeletingId(centro.id || null);
        try {
            await onDelete(centro);
        } finally {
            setDeletingId(null);
        }
    };

    if (loading) return <div className="p-4 text-center">Carregando departamentos...</div>;
    if (error) return <div className="p-4 text-red-600">Erro: {error}</div>;

    return (
        <div className="bg-white rounded-lg border border-gray-200 shadow-sm overflow-hidden">
            <div className="px-6 py-4 border-b border-gray-200 flex justify-between items-center">
                <h2 className="text-xl font-semibold text-gray-800">Lista de Departamentos</h2>
                <button
                    onClick={onCreateNew}
                    className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-colors"
                >
                    ➕ Adicionar Novo
                </button>
            </div>
            
            
            <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                        <tr>
                            <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Nome</th>
                            <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Descrição</th>
                            <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Ativo</th>
                            <th scope="col" className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Ações</th>
                        </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                        {centrosCusto.length > 0 ? (
                            centrosCusto.map((centro) => (
                                <tr key={centro.id}>
                                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{centro.nome}</td>
                                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{centro.descricao || '-'}</td>
                                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                        {centro.ativo ? (
                                            <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800">
                                                Sim
                                            </span>
                                        ) : (
                                            <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-red-100 text-red-800">
                                                Não
                                            </span>
                                        )}
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                                        <button
                                            onClick={() => onEdit(centro)}
                                            className="text-indigo-600 hover:text-indigo-900 mr-4"
                                        >
                                            Editar
                                        </button>
                                        <button
                                            onClick={() => handleDeleteClick(centro)}
                                            disabled={deletingId === centro.id}
                                            className="text-red-600 hover:text-red-900 disabled:opacity-50"
                                        >
                                            {deletingId === centro.id ? 'Deletando...' : 'Excluir'}
                                        </button>
                                    </td>
                                </tr>
                            ))
                        ) : (
                            <tr>
                                <td colSpan={4} className="px-6 py-4 text-center text-sm text-gray-500">
                                    Nenhum departamento encontrado.
                                </td>
                            </tr>
                        )}
                    </tbody>
                </table>
            </div>
        </div>
    );
};

export default CentroCustoList;
