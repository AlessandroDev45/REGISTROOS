import React, { useState, useMemo } from 'react';
import { DescricaoAtividadeData } from '../../../../services/adminApi';

interface DescricaoAtividadeListProps {
    data?: DescricaoAtividadeData[];
    onEdit: (descricao: DescricaoAtividadeData) => void;
    onDelete: (descricao: DescricaoAtividadeData) => void;
    onCreateNew: () => void;
    loading: boolean;
    error: string | null;
}

const DescricaoAtividadeList: React.FC<DescricaoAtividadeListProps> = ({ data: descricoes = [], onEdit, onDelete, onCreateNew, loading, error }) => {
    const [deletingId, setDeletingId] = useState<number | null>(null);

    const handleDeleteClick = async (descricao: DescricaoAtividadeData) => {
        if (!window.confirm(`Tem certeza de que deseja deletar a descrição de atividade "${descricao.codigo}"?`)) {
            return;
        }
        setDeletingId(descricao.id || null);
        try {
            await onDelete(descricao);
        } finally {
            setDeletingId(null);
        }
    };

    if (loading) return <div className="p-4 text-center">Carregando descrições de atividade...</div>;
    if (error) return <div className="p-4 text-red-600">Erro: {error}</div>;

    return (
        <div className="bg-white rounded-lg border border-gray-200 shadow-sm overflow-hidden">
            <div className="px-6 py-4 border-b border-gray-200 flex justify-between items-center">
                <h2 className="text-xl font-semibold text-gray-800">Lista de Descrições de Atividades</h2>
                <button
                    onClick={onCreateNew}
                    className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-colors"
                >
                    ➕ Adicionar Nova
                </button>
            </div>


            <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                        <tr>
                            <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Código</th>
                            <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Descrição</th>
                            <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Setor</th>
                            <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Ativo</th>
                            <th scope="col" className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Ações</th>
                        </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                        {descricoes.length > 0 ? (
                            descricoes.map((descricao) => (
                                <tr key={descricao.id}>
                                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{descricao.codigo}</td>
                                    <td className="px-6 py-4 text-sm text-gray-500 max-w-xs truncate" title={descricao.descricao}>{descricao.descricao}</td>
                                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{descricao.setor}</td>
                                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                        {descricao.ativo ? (
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
                                            onClick={() => onEdit(descricao)}
                                            className="text-indigo-600 hover:text-indigo-900 mr-4"
                                        >
                                            Editar
                                        </button>
                                        <button
                                            onClick={() => handleDeleteClick(descricao)}
                                            disabled={deletingId === descricao.id}
                                            className="text-red-600 hover:text-red-900 disabled:opacity-50"
                                        >
                                            {deletingId === descricao.id ? 'Deletando...' : 'Excluir'}
                                        </button>
                                    </td>
                                </tr>
                            ))
                        ) : (
                            <tr>
                                <td colSpan={5} className="px-6 py-4 text-center text-sm text-gray-500">
                                    Nenhuma descrição de atividade encontrada.
                                </td>
                            </tr>
                        )}
                    </tbody>
                </table>
            </div>
        </div>
    );
};

export default DescricaoAtividadeList;