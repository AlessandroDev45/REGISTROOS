import React from 'react'; // Removido useState e useEffect
import { FalhaTipoData } from '../../../../services/adminApi';

interface TipoFalhaListProps {
    data?: FalhaTipoData[]; // Dados agora vêm via prop, opcional
    onEdit: (falha: FalhaTipoData) => void;
    onDelete: (falha: FalhaTipoData) => void; // Passa o item completo para delete
    onCreateNew: () => void;
    loading: boolean;
    error: string | null;
}

const TipoFalhaList: React.FC<TipoFalhaListProps> = ({ data: falhas = [], onEdit, onDelete, onCreateNew, loading, error }) => {
    const [deletingId, setDeletingId] = React.useState<number | null>(null);

    // Função para quebrar texto se maior que 15 caracteres
    const formatTextWithBreak = (text: string, maxLength: number = 15) => {
        if (!text || text.length <= maxLength) return text;

        // Quebrar em palavras para evitar cortar no meio de uma palavra
        const words = text.split(' ');
        let result = '';
        let currentLine = '';

        for (const word of words) {
            if ((currentLine + word).length <= maxLength) {
                currentLine += (currentLine ? ' ' : '') + word;
            } else {
                if (result) result += '\n';
                result += currentLine;
                currentLine = word;
            }
        }

        if (currentLine) {
            if (result) result += '\n';
            result += currentLine;
        }

        return result;
    };

    const handleDeleteClick = async (falha: FalhaTipoData) => {
        if (!window.confirm(`Tem certeza de que deseja deletar o tipo de falha "${falha.codigo}"?`)) {
            return;
        }
        setDeletingId(falha.id || null);
        try {
            await onDelete(falha); // Chama o onDelete passado via prop
        } finally {
            setDeletingId(null);
        }
    };

    if (loading) return <div className="p-4 text-center">Carregando tipos de falha...</div>;
    if (error) return <div className="p-4 text-red-600">Erro: {error}</div>;

    return (
        <div className="bg-white rounded-lg border border-gray-200 shadow-sm overflow-hidden">
            <div className="px-6 py-4 border-b border-gray-200 flex justify-between items-center">
                <h2 className="text-xl font-semibold text-gray-800">Lista de Tipos de Falha</h2>
                <button
                    onClick={onCreateNew}
                    className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-colors"
                >
                    Adicionar Novo Tipo de Falha
                </button>
            </div>
            <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                        <tr>
                            <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Código</th>
                            <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Descrição</th>
                            <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Departamento</th>
                            <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Setor</th>
                            <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Ativo</th>
                            <th scope="col" className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Ações</th>
                        </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                        {falhas.length > 0 ? (
                            falhas.map((falha) => (
                                <tr key={falha.id}>
                                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{falha.codigo}</td>
                                    <td className="px-6 py-4 text-sm text-gray-500 max-w-xs truncate" title={falha.descricao}>{falha.descricao}</td>
                                    <td className="px-6 py-4 text-sm text-gray-500">
                                        <div className="whitespace-pre-line">
                                            {formatTextWithBreak(falha.departamento || '-')}
                                        </div>
                                    </td>
                                    <td className="px-6 py-4 text-sm text-gray-500">
                                        <div className="whitespace-pre-line">
                                            {formatTextWithBreak(falha.setor || '-')}
                                        </div>
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                        {falha.ativo ? (
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
                                            onClick={() => onEdit(falha)}
                                            className="text-indigo-600 hover:text-indigo-900 mr-4"
                                        >
                                            Editar
                                        </button>
                                        <button
                                            onClick={() => handleDeleteClick(falha)}
                                            disabled={deletingId === falha.id}
                                            className="text-red-600 hover:text-red-900 disabled:opacity-50"
                                        >
                                            {deletingId === falha.id ? 'Deletando...' : 'Excluir'}
                                        </button>
                                    </td>
                                </tr>
                            ))
                        ) : (
                            <tr>
                                <td colSpan={6} className="px-6 py-4 text-center text-sm text-gray-500">
                                    Nenhum tipo de falha encontrado.
                                </td>
                            </tr>
                        )}
                    </tbody>
                </table>
            </div>
        </div>
    );
};

export default TipoFalhaList;