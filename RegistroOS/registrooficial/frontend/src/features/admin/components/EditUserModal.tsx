import React, { useState, useEffect } from 'react';
import { formatarTextoInput, criarHandlerTextoValidado } from '../../../utils/textValidation';

interface Usuario {
    id: number;
    nome_completo: string;
    email: string;
    matricula?: string;
    cargo?: string;
    setor: string;
    departamento: string;
    privilege_level: string;
    trabalha_producao: boolean;
    is_approved: boolean;
}

interface Setor {
    id: number;
    nome: string;
    descricao: string;
    id_departamento: number;
    ativo: boolean;
}

interface EditUserModalProps {
    isOpen: boolean;
    onClose: () => void;
    user: Usuario | null;
    setores: Setor[];
    onSave: (userData: Partial<Usuario>) => Promise<void>;
    loading: boolean;
}

const EditUserModal: React.FC<EditUserModalProps> = ({
    isOpen,
    onClose,
    user,
    setores,
    onSave,
    loading
}) => {
    const [formData, setFormData] = useState<Partial<Usuario>>({
        nome_completo: '',
        email: '',
        matricula: '',
        setor: '',
        departamento: 'MOTORES',
        cargo: '',
        privilege_level: 'USER',
        trabalha_producao: false
    });

    useEffect(() => {
        if (user && isOpen) {
            setFormData({
                nome_completo: user.nome_completo,
                email: user.email,
                matricula: user.matricula || '',
                setor: user.setor,
                departamento: user.departamento,
                cargo: user.cargo || '',
                privilege_level: user.privilege_level,
                trabalha_producao: user.trabalha_producao
            });
        }
    }, [user, isOpen]);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!user) return;

        try {
            await onSave(formData);
            onClose();
        } catch (error) {
            console.error('Erro ao salvar usuário:', error);
        }
    };

    const handleClose = () => {
        setFormData({
            nome_completo: '',
            email: '',
            matricula: '',
            setor: '',
            departamento: 'MOTORES',
            cargo: '',
            privilege_level: 'USER',
            trabalha_producao: false
        });
        onClose();
    };

    if (!isOpen || !user) return null;

    return (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg shadow-xl max-w-md w-full mx-4 max-h-[90vh] overflow-y-auto">
                <div className="p-6">
                    <div className="flex justify-between items-center mb-4">
                        <h3 className="text-lg font-medium text-gray-900">
                            Editar Usuário
                        </h3>
                        <button
                            onClick={handleClose}
                            className="text-gray-400 hover:text-gray-600"
                        >
                            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                            </svg>
                        </button>
                    </div>

                    <form onSubmit={handleSubmit} className="space-y-4">
                        <div>
                            <label className="block text-sm font-medium text-gray-700">
                                Nome Completo
                            </label>
                            <input
                                type="text"
                                value={formData.nome_completo || ''}
                                onChange={criarHandlerTextoValidado((valor) => setFormData({...formData, nome_completo: valor}))}
                                onPaste={(e) => {
                                    e.preventDefault();
                                    const texto = e.clipboardData.getData('text');
                                    const textoLimpo = formatarTextoInput(texto);
                                    setFormData({...formData, nome_completo: textoLimpo});
                                }}
                                className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                                placeholder="NOME COMPLETO EM MAIÚSCULAS"
                                style={{ textTransform: 'uppercase' }}
                                required
                            />
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-gray-700">
                                E-mail
                            </label>
                            <input
                                type="email"
                                value={formData.email || ''}
                                onChange={(e) => setFormData({...formData, email: e.target.value})}
                                className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                                required
                            />
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-gray-700">
                                Matrícula (opcional)
                            </label>
                            <input
                                type="text"
                                value={formData.matricula || ''}
                                onChange={(e) => setFormData({...formData, matricula: e.target.value})}
                                className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                            />
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-gray-700">
                                Setor
                            </label>
                            <select
                                value={formData.setor || ''}
                                onChange={(e) => setFormData({...formData, setor: e.target.value})}
                                className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                                required
                            >
                                <option value="">Selecione um setor</option>
                                {setores.map((setor) => (
                                    <option key={setor.id} value={setor.nome}>
                                        {setor.nome}
                                    </option>
                                ))}
                            </select>
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-gray-700">
                                Departamento
                            </label>
                            <select
                                value={formData.departamento || 'MOTORES'}
                                onChange={(e) => setFormData({...formData, departamento: e.target.value})}
                                className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                            >
                                <option value="MOTORES">MOTORES</option>
                                <option value="TRANSFORMADORES">TRANSFORMADORES</option>
                            </select>
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-gray-700">
                                Cargo (opcional)
                            </label>
                            <input
                                type="text"
                                value={formData.cargo || ''}
                                onChange={(e) => setFormData({...formData, cargo: e.target.value})}
                                className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                            />
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-gray-700">
                                Privilégio
                            </label>
                            <select
                                value={formData.privilege_level || 'USER'}
                                onChange={(e) => setFormData({...formData, privilege_level: e.target.value})}
                                className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                            >
                                <option value="USER">USER</option>
                                <option value="SUPERVISOR">SUPERVISOR</option>
                                <option value="GESTAO">GESTAO</option>
                                <option value="ADMIN">ADMIN</option>
                            </select>
                        </div>

                        <div className="flex items-center">
                            <input
                                id="trabalha_producao_edit"
                                type="checkbox"
                                checked={formData.trabalha_producao || false}
                                onChange={(e) => setFormData({...formData, trabalha_producao: e.target.checked})}
                                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                            />
                            <label htmlFor="trabalha_producao_edit" className="ml-2 block text-sm text-gray-900">
                                Trabalha na produção
                            </label>
                        </div>

                        <div className="flex justify-end space-x-3 pt-4">
                            <button
                                type="button"
                                onClick={handleClose}
                                className="px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                                disabled={loading}
                            >
                                Cancelar
                            </button>
                            <button
                                type="submit"
                                className="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
                                disabled={loading}
                            >
                                {loading ? 'Salvando...' : 'Salvar'}
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    );
};

export default EditUserModal;