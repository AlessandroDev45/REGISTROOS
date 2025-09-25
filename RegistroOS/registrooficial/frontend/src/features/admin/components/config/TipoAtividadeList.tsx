import React from 'react'; // Removido useState e useEffect
import { AtividadeTipoData } from '../../../../services/adminApi';

interface TipoAtividadeListProps {
    data?: AtividadeTipoData[]; // Dados agora vêm via prop, opcional
    onEdit: (atividade: AtividadeTipoData) => void;
    onDelete: (atividade: AtividadeTipoData) => void; // Passa o item completo para delete
    onCreateNew: () => void;
    loading: boolean;
    error: string | null;
}

const TipoAtividadeList: React.FC<TipoAtividadeListProps> = ({ data: atividades = [], onEdit, onDelete, onCreateNew, loading, error }) => {
    const [deletingId, setDeletingId] = React.useState<number | null>(null);

    const handleDeleteClick = async (atividade: AtividadeTipoData) => {
        if (!window.confirm(`Tem certeza de que deseja deletar o tipo de atividade "${atividade.nome_tipo}"?`)) {
            return;
        }
        setDeletingId(atividade.id || null);
        try {
            await onDelete(atividade); // Chama o onDelete passado via prop
        } finally {
            setDeletingId(null);
        }
    };

    if (loading) return <div className="p-4 text-center">Carregando tipos de atividade...</div>;
    if (error) return <div className="p-4 text-red-600">Erro: {error}</div>;

    return (
        <div className="bg-white rounded-lg border border-gray-200 shadow-sm overflow-hidden">
            <div className="px-6 py-4 border-b border-gray-200 flex justify-between items-center">
                <h2 className="text-xl font-semibold text-gray-800">Lista de Tipos de Atividade</h2>
                <button
                    onClick={onCreateNew}
                    className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-colors"
                >
                    Adicionar Novo Tipo de Atividade
                </button>
            </div>
            <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                        <tr>
                            <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Nome do Tipo</th>
                            <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Descrição</th>
                            <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Ativo</th>
                            <th scope="col" className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Ações</th>
                        </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                        {atividades.length > 0 ? (
                            atividades.map((atividade) => (
                                <tr key={atividade.id}>
                                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{atividade.nome_tipo}</td>
                                    <td className="px-6 py-4 text-sm text-gray-500 max-w-xs truncate" title={atividade.descricao}>{atividade.descricao || '-'}</td>
                                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                        {atividade.ativo ? (
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
                                            onClick={() => onEdit(atividade)}
                                            className="text-indigo-600 hover:text-indigo-900 mr-4"
                                        >
                                            Editar
                                        </button>
                                        <button
                                            onClick={() => handleDeleteClick(atividade)}
                                            disabled={deletingId === atividade.id}
                                            className="text-red-600 hover:text-red-900 disabled:opacity-50"
                                        >
                                            {deletingId === atividade.id ? 'Deletando...' : 'Excluir'}
                                        </button>
                                    </td>
                                </tr>
                            ))
                        ) : (
                            <tr>
                                <td colSpan={4} className="px-6 py-4 text-center text-sm text-gray-500">
                                    Nenhum tipo de atividade encontrado.
                                </td>
                            </tr>
                        )}
                    </tbody>
                </table>
            </div>
        </div>
    );
};

export default TipoAtividadeList;