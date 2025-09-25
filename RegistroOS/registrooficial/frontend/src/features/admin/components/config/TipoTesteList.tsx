import React, { useState } from 'react';
import { TipoTesteData } from '../../../../services/adminApi';

interface TipoTesteListProps {
    data?: TipoTesteData[];
    onEdit: (tipo: TipoTesteData) => void;
    onDelete: (tipo: TipoTesteData) => void;
    onCreateNew: () => void;
    loading: boolean;
    error: string | null;
}

const TipoTesteList: React.FC<TipoTesteListProps> = ({ data: tiposTeste = [], onEdit, onDelete, onCreateNew, loading, error }) => {
    const [deletingId, setDeletingId] = useState<number | null>(null);

    const handleDeleteClick = async (tipo: TipoTesteData) => {
        if (!window.confirm(`Tem certeza de que deseja deletar o tipo de teste "${tipo.nome}"?`)) {
            return;
        }
        setDeletingId(tipo.id || null);
        try {
            await onDelete(tipo);
        } finally {
            setDeletingId(null);
        }
    };

    if (loading) return <div className="p-4 text-center">Carregando tipos de teste...</div>;
    if (error) return <div className="p-4 text-red-600">Erro: {error}</div>;

    return (
        <div className="bg-white rounded-lg border border-gray-200 shadow-sm overflow-hidden">
            <div className="px-6 py-4 border-b border-gray-200 flex justify-between items-center">
                <h2 className="text-xl font-semibold text-gray-800">Lista de Tipos de Teste</h2>
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
                            <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Tipo de Teste</th>
                            <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Categoria</th>
                            <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Subcategoria</th>
                            <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Departamento</th>
                            <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Setor</th>
                            <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Ativo</th>
                            <th scope="col" className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Ações</th>
                        </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                        {tiposTeste.length > 0 ? (
                            tiposTeste.map((tipo) => (
                                <tr key={tipo.id}>
                                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{tipo.nome}</td>
                                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{tipo.tipo_teste || '-'}</td>
                                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                                            tipo.categoria === 'Visual' ? 'bg-blue-100 text-blue-800' :
                                            tipo.categoria === 'Elétricos' ? 'bg-yellow-100 text-yellow-800' :
                                            tipo.categoria === 'Mecânicos' ? 'bg-green-100 text-green-800' :
                                            'bg-gray-100 text-gray-800'
                                        }`}>
                                            {tipo.categoria || 'Visual'}
                                        </span>
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                                            tipo.subcategoria === 1 ? 'bg-purple-100 text-purple-800' : 'bg-gray-100 text-gray-800'
                                        }`}>
                                            {tipo.subcategoria === 1 ? 'Especiais' : 'Padrão'}
                                        </span>
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{tipo.departamento}</td>
                                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{tipo.setor || '-'}</td>
                                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                        {tipo.ativo ? (
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
                                            onClick={() => onEdit(tipo)}
                                            className="text-indigo-600 hover:text-indigo-900 mr-4"
                                        >
                                            Editar
                                        </button>
                                        <button
                                            onClick={() => handleDeleteClick(tipo)}
                                            disabled={deletingId === tipo.id}
                                            className="text-red-600 hover:text-red-900 disabled:opacity-50"
                                        >
                                            {deletingId === tipo.id ? 'Deletando...' : 'Excluir'}
                                        </button>
                                    </td>
                                </tr>
                            ))
                        ) : (
                            <tr>
                                <td colSpan={6} className="px-6 py-4 text-center text-sm text-gray-500">
                                    Nenhum tipo de teste encontrado.
                                </td>
                            </tr>
                        )}
                    </tbody>
                </table>
            </div>
        </div>
    );
};

export default TipoTesteList;