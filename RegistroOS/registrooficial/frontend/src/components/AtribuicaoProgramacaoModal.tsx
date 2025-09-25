import React, { useState, useEffect } from 'react';
import api from '../services/api';

interface AtribuicaoProgramacaoModalProps {
    isOpen: boolean;
    onClose: () => void;
    programacaoId?: number;
    onSuccess: () => void;
    isEdit?: boolean;
    isReatribuir?: boolean;
    programacaoData?: any;
}

interface FormData {
    responsavel_id: number | '';
    setor_destino: string;
    departamento_destino: string;
    data_inicio: string;
    data_fim: string;
    prioridade: string;
    observacoes: string;
}

interface Usuario {
    id: number;
    nome_completo: string;
    setor: string;
    departamento: string;
    privilege_level: string;
}

interface Setor {
    id: number;
    nome: string;
    departamento: string;
}

interface Departamento {
    id: number;
    nome: string;
}

const AtribuicaoProgramacaoModal: React.FC<AtribuicaoProgramacaoModalProps> = ({
    isOpen,
    onClose,
    programacaoId,
    onSuccess,
    isEdit = false,
    isReatribuir = false,
    programacaoData
}) => {
    const [formData, setFormData] = useState<FormData>({
        responsavel_id: '',
        setor_destino: '',
        departamento_destino: '',
        data_inicio: '',
        data_fim: '',
        prioridade: 'NORMAL',
        observacoes: ''
    });

    const [usuarios, setUsuarios] = useState<Usuario[]>([]);
    const [usuariosFiltrados, setUsuariosFiltrados] = useState<Usuario[]>([]);
    const [setores, setSetores] = useState<Setor[]>([]);
    const [setoresFiltrados, setSetoresFiltrados] = useState<Setor[]>([]);
    const [departamentos, setDepartamentos] = useState<Departamento[]>([]);
    const [loading, setLoading] = useState(false);
    const [errors, setErrors] = useState<Record<string, string>>({});

    useEffect(() => {
        if (isOpen) {
            carregarDados();
            if (programacaoData && (isEdit || isReatribuir)) {
                preencherFormulario();
            }
        }
    }, [isOpen, programacaoData, isEdit, isReatribuir]);

    // Filtrar setores quando departamento muda
    useEffect(() => {
        if (formData.departamento_destino) {
            const setoresDoDepartamento = setores.filter(
                setor => setor.departamento === formData.departamento_destino
            );
            setSetoresFiltrados(setoresDoDepartamento);
        } else {
            setSetoresFiltrados(setores);
        }
    }, [formData.departamento_destino, setores]);

    // Filtrar usuários quando departamento/setor muda
    useEffect(() => {
        let usuariosFiltered = usuarios;

        if (formData.departamento_destino) {
            usuariosFiltered = usuariosFiltered.filter(
                usuario => usuario.departamento === formData.departamento_destino
            );
        }

        if (formData.setor_destino) {
            usuariosFiltered = usuariosFiltered.filter(
                usuario => usuario.setor === formData.setor_destino
            );
        }

        // Filtrar apenas supervisores e gestores para programação
        usuariosFiltered = usuariosFiltered.filter(
            usuario => ['SUPERVISOR', 'GESTAO'].includes(usuario.privilege_level)
        );

        setUsuariosFiltrados(usuariosFiltered);
    }, [formData.departamento_destino, formData.setor_destino, usuarios]);

    const carregarDados = async () => {
        try {
            const [usuariosRes, setoresRes, departamentosRes] = await Promise.all([
                api.get('/usuarios'),
                api.get('/setores'),
                api.get('/departamentos')
            ]);

            setUsuarios(usuariosRes.data || []);
            setUsuariosFiltrados(usuariosRes.data || []);
            setSetores(setoresRes.data || []);
            setSetoresFiltrados(setoresRes.data || []);
            setDepartamentos(departamentosRes.data || []);
        } catch (error) {
            console.error('Erro ao carregar dados:', error);
        }
    };

    const preencherFormulario = () => {
        if (programacaoData) {
            setFormData({
                responsavel_id: programacaoData.responsavel_id || '',
                setor_destino: programacaoData.setor_destino || '',
                departamento_destino: programacaoData.departamento_destino || '',
                data_inicio: programacaoData.data_inicio ?
                    new Date(programacaoData.data_inicio).toISOString().slice(0, 16) : '',
                data_fim: programacaoData.data_fim ?
                    new Date(programacaoData.data_fim).toISOString().slice(0, 16) : '',
                prioridade: programacaoData.prioridade || 'NORMAL',
                observacoes: programacaoData.observacoes || ''
            });
        }
    };

    const handleInputChange = (field: keyof FormData, value: string | number) => {
        setFormData(prev => ({
            ...prev,
            [field]: value
        }));
        
        // Limpar erro do campo
        if (errors[field]) {
            setErrors(prev => ({
                ...prev,
                [field]: ''
            }));
        }
    };

    const validarFormulario = (): boolean => {
        const novosErros: Record<string, string> = {};

        if (!formData.responsavel_id) {
            novosErros.responsavel_id = 'Responsável é obrigatório';
        }

        if (!formData.setor_destino) {
            novosErros.setor_destino = 'Setor de destino é obrigatório';
        }

        if (!formData.departamento_destino) {
            novosErros.departamento_destino = 'Departamento de destino é obrigatório';
        }

        if (!formData.data_inicio) {
            novosErros.data_inicio = 'Data de início é obrigatória';
        }

        if (!formData.data_fim) {
            novosErros.data_fim = 'Data de fim é obrigatória';
        }

        if (formData.data_inicio && formData.data_fim && formData.data_inicio > formData.data_fim) {
            novosErros.data_fim = 'Data de fim deve ser posterior à data de início';
        }

        setErrors(novosErros);
        return Object.keys(novosErros).length === 0;
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();

        if (!validarFormulario()) {
            return;
        }

        setLoading(true);
        try {
            const dadosAtribuicao = {
                ...formData,
                responsavel_id: Number(formData.responsavel_id)
            };

            let endpoint = '/pcp/programacoes/atribuir';
            let method = 'post';
            let mensagem = 'Programação atribuída com sucesso!';

            if (isEdit && programacaoId) {
                endpoint = `/pcp/programacoes/${programacaoId}`;
                method = 'put';
                mensagem = 'Programação editada com sucesso!';
            } else if (isReatribuir && programacaoId) {
                endpoint = `/pcp/programacoes/${programacaoId}/reatribuir`;
                method = 'patch';
                mensagem = 'Programação reatribuída com sucesso!';
            } else if (programacaoId) {
                endpoint = `/pcp/programacoes/${programacaoId}/atribuir`;
                method = 'put';
            }

            if (method === 'post') {
                await api.post(endpoint, dadosAtribuicao);
            } else if (method === 'put') {
                await api.put(endpoint, dadosAtribuicao);
            } else if (method === 'patch') {
                await api.patch(endpoint, dadosAtribuicao);
            }

            alert(mensagem);
            onSuccess();
            onClose();
            resetForm();
        } catch (error: any) {
            console.error('Erro ao processar programação:', error);
            alert(error.response?.data?.detail || 'Erro ao processar programação');
        } finally {
            setLoading(false);
        }
    };

    const resetForm = () => {
        setFormData({
            responsavel_id: '',
            setor_destino: '',
            departamento_destino: '',
            data_inicio: '',
            data_fim: '',
            prioridade: 'NORMAL',
            observacoes: ''
        });
        setErrors({});
    };

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg p-6 max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
                <div className="flex justify-between items-center mb-6">
                    <h2 className="text-xl font-semibold text-gray-900">
                        {isEdit ? '✏️ Editar Programação' :
                         isReatribuir ? '🔄 Reatribuir Programação' :
                         '📋 Atribuir Programação'}
                    </h2>
                    <button
                        onClick={onClose}
                        className="text-gray-400 hover:text-gray-600"
                    >
                        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                        </svg>
                    </button>
                </div>

                <form onSubmit={handleSubmit} className="space-y-4">
                    {/* Departamento e Setor */}
                    <div className="grid grid-cols-2 gap-4">
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">
                                Departamento de Destino *
                            </label>
                            <select
                                value={formData.departamento_destino}
                                onChange={(e) => {
                                    handleInputChange('departamento_destino', e.target.value);
                                    handleInputChange('setor_destino', ''); // Reset setor
                                }}
                                className={`w-full border rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                                    errors.departamento_destino ? 'border-red-300' : 'border-gray-300'
                                }`}
                            >
                                <option value="">Selecione um departamento</option>
                                {departamentos.map(dept => (
                                    <option key={dept.id} value={dept.nome}>
                                        {dept.nome}
                                    </option>
                                ))}
                            </select>
                            {errors.departamento_destino && (
                                <p className="text-red-500 text-xs mt-1">{errors.departamento_destino}</p>
                            )}
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">
                                Setor de Destino *
                            </label>
                            <select
                                value={formData.setor_destino}
                                onChange={(e) => handleInputChange('setor_destino', e.target.value)}
                                className={`w-full border rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                                    errors.setor_destino ? 'border-red-300' : 'border-gray-300'
                                }`}
                                disabled={!formData.departamento_destino}
                            >
                                <option value="">Selecione um setor</option>
                                {setoresFiltrados.map(setor => (
                                    <option key={setor.id} value={setor.nome}>
                                        {setor.nome}
                                    </option>
                                ))}
                            </select>
                            {errors.setor_destino && (
                                <p className="text-red-500 text-xs mt-1">{errors.setor_destino}</p>
                            )}
                        </div>
                    </div>

                    {/* Responsável */}
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                            Responsável (Supervisor) *
                        </label>
                        <select
                            value={formData.responsavel_id}
                            onChange={(e) => handleInputChange('responsavel_id', e.target.value ? Number(e.target.value) : '')}
                            className={`w-full border rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                                errors.responsavel_id ? 'border-red-300' : 'border-gray-300'
                            }`}
                            disabled={!formData.departamento_destino}
                        >
                            <option value="">
                                {!formData.departamento_destino
                                    ? 'Selecione primeiro o departamento'
                                    : 'Selecione um responsável'}
                            </option>
                            {usuariosFiltrados.map(supervisor => (
                                <option key={supervisor.id} value={supervisor.id}>
                                    {supervisor.nome_completo} - {supervisor.setor} ({supervisor.privilege_level})
                                </option>
                            ))}
                        </select>
                        {errors.responsavel_id && (
                            <p className="text-red-500 text-xs mt-1">{errors.responsavel_id}</p>
                        )}
                    </div>

                    {/* Datas */}
                    <div className="grid grid-cols-2 gap-4">
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">
                                Data de Início *
                            </label>
                            <input
                                type="datetime-local"
                                value={formData.data_inicio}
                                onChange={(e) => handleInputChange('data_inicio', e.target.value)}
                                className={`w-full border rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                                    errors.data_inicio ? 'border-red-300' : 'border-gray-300'
                                }`}
                            />
                            {errors.data_inicio && (
                                <p className="text-red-500 text-xs mt-1">{errors.data_inicio}</p>
                            )}
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">
                                Data de Fim *
                            </label>
                            <input
                                type="datetime-local"
                                value={formData.data_fim}
                                onChange={(e) => handleInputChange('data_fim', e.target.value)}
                                className={`w-full border rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                                    errors.data_fim ? 'border-red-300' : 'border-gray-300'
                                }`}
                            />
                            {errors.data_fim && (
                                <p className="text-red-500 text-xs mt-1">{errors.data_fim}</p>
                            )}
                        </div>
                    </div>

                    {/* Prioridade */}
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                            Prioridade
                        </label>
                        <select
                            value={formData.prioridade}
                            onChange={(e) => handleInputChange('prioridade', e.target.value)}
                            className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                        >
                            <option value="BAIXA">Baixa</option>
                            <option value="NORMAL">Normal</option>
                            <option value="ALTA">Alta</option>
                            <option value="URGENTE">Urgente</option>
                        </select>
                    </div>

                    {/* Observações */}
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                            Observações
                        </label>
                        <textarea
                            value={formData.observacoes}
                            onChange={(e) => handleInputChange('observacoes', e.target.value)}
                            rows={3}
                            className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                            placeholder="Observações sobre a atribuição..."
                        />
                    </div>

                    {/* Botões */}
                    <div className="flex justify-end space-x-3 pt-4">
                        <button
                            type="button"
                            onClick={onClose}
                            className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 border border-gray-300 rounded-md hover:bg-gray-200 focus:outline-none focus:ring-2 focus:ring-gray-500"
                        >
                            Cancelar
                        </button>
                        <button
                            type="submit"
                            disabled={loading}
                            className="px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
                        >
                            {loading ? 'Atribuindo...' : 'Atribuir Programação'}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
};

export default AtribuicaoProgramacaoModal;
