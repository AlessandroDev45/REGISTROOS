// frontend/src/features/admin/components/config/DepartamentoList.tsx
import React, { useState, useEffect } from 'react';
import { departamentoService, DepartamentoData } from '../../../../services/adminApi';

interface DepartamentoListProps {
    onEdit: (departamento: DepartamentoData) => void;
    onCreateNew: () => void;
    refreshData: () => void;
}

const DepartamentoList: React.FC<DepartamentoListProps> = ({ onEdit, onCreateNew, refreshData }) => {
    const [departamentos, setDepartamentos] = useState<DepartamentoData[]>([]);
    const [loading, setLoading] = useState<boolean>(true);
    const [error, setError] = useState<string | null>(null);
    const [deletingId, setDeletingId] = useState<number | null>(null);

    useEffect(() => {
        fetchDepartamentos();
    }, [refreshData]);

    const fetchDepartamentos = async () => {
        setLoading(true);
        setError(null);
        try {
            const data = await departamentoService.getDepartamentos();
            setDepartamentos(data);
        } catch (err: any) {
            setError(err.message || 'Falha ao carregar departamentos.');
        } finally {
            setLoading(false);
        }
    };

    const handleDelete = async (id: number, nome: string) => {
        if (!window.confirm(`Tem certeza de que deseja deletar o departamento "${nome}"?`)) {
            return;
        }

        setDeletingId(id);
        try {
            await departamentoService.deleteDepartamento(id);
            refreshData();
        } catch (err: any) {
            setError(err.message || 'Falha ao deletar departamento.');
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
                    Adicionar Novo Departamento
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
                        {departamentos.length > 0 ? (
                            departamentos.map((item) => (
                                <tr key={item.id}>
                                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{item.nome}</td>
                                    <td className="px-6 py-4 text-sm text-gray-500 max-w-xs truncate" title={item.descricao}>{item.descricao || '-'}</td>
                                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                        {item.ativo ? (
                                            <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800">Sim</span>
                                        ) : (
                                            <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-red-100 text-red-800">Não</span>
                                        )}
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                                        <button onClick={() => onEdit(item)} className="text-indigo-600 hover:text-indigo-900 mr-4">Editar</button>
                                        <button onClick={() => handleDelete(item.id!, item.nome)} disabled={deletingId === item.id} className="text-red-600 hover:text-red-900 disabled:opacity-50">
                                            {deletingId === item.id ? 'Deletando...' : 'Excluir'}
                                        </button>
                                    </td>
                                </tr>
                            ))
                        ) : (
                            <tr>
                                <td colSpan={4} className="px-6 py-4 text-center text-sm text-gray-500">Nenhum departamento encontrado.</td>
                            </tr>
                        )}
                    </tbody>
                </table>
            </div>
        </div>
    );
};

export default DepartamentoList;