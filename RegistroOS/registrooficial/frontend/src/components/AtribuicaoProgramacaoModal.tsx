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
    responsavel_id: number | '';  // Colaborador do setor
    data_inicio: string;
    data_fim: string;
    observacoes: string;
    setor_destino: string;
    departamento_destino: string;
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
        data_inicio: '',
        data_fim: '',
        observacoes: '',
        setor_destino: '',
        departamento_destino: ''
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

    // Filtrar usuários do setor do usuário logado
    useEffect(() => {
        // Em desenvolvimento, buscar apenas usuários do mesmo setor
        // Será implementado via API que já filtra por setor
        setUsuariosFiltrados(usuarios);
    }, [usuarios]);

    const carregarDados = async () => {
        try {
            // 1. Buscar dados do usuário logado para setor e departamento
            const userDataFromStorage = JSON.parse(localStorage.getItem('user') || '{}');

            // 2. Buscar colaboradores do setor
            const usuariosRes = await api.get('/desenvolvimento/colaboradores');
            setUsuarios(usuariosRes.data || []);
            setUsuariosFiltrados(usuariosRes.data || []);

            // 3. Buscar dados de setores para obter nomes corretos
            try {
                // Usar endpoint público de setores ao invés do admin
                const setoresRes = await api.get('/setores');
                const setores = setoresRes.data || [];

                // Encontrar o setor do usuário logado
                const setorUsuario = setores.find((s: any) => s.id === userDataFromStorage.id_setor);

                if (setorUsuario) {
                    setFormData(prev => ({
                        ...prev,
                        setor_destino: setorUsuario.nome,
                        departamento_destino: setorUsuario.departamento
                    }));
                    console.log(`✅ Setor definido: ${setorUsuario.nome} - Dept: ${setorUsuario.departamento}`);
                } else {
                    // Fallback para primeiro setor disponível
                    if (setores.length > 0) {
                        setFormData(prev => ({
                            ...prev,
                            setor_destino: setores[0].nome,
                            departamento_destino: setores[0].departamento
                        }));
                        console.log(`⚠️ Usando setor fallback: ${setores[0].nome} - Dept: ${setores[0].departamento}`);
                    }
                }
            } catch (setorError) {
                console.error('Erro ao buscar setores:', setorError);
            }

        } catch (error) {
            console.error('Erro ao carregar colaboradores:', error);
            // Fallback para endpoint geral se específico não existir
            try {
                const usuariosRes = await api.get('/users/usuarios/');
                // Filtrar apenas usuários do mesmo setor no frontend como fallback
                const usuariosFiltrados = usuariosRes.data?.filter((user: any) =>
                    user.id_setor === JSON.parse(localStorage.getItem('user') || '{}').id_setor
                ) || [];
                setUsuarios(usuariosFiltrados);
                setUsuariosFiltrados(usuariosFiltrados);
            } catch (fallbackError) {
                console.error('Erro ao carregar usuários:', fallbackError);
            }
        }
    };

    // Função para converter data para formato datetime-local brasileiro
    const formatDateTimeLocal = (dateString: string) => {
        if (!dateString) return '';

        const date = new Date(dateString);
        // Ajustar para timezone local brasileiro
        const offset = date.getTimezoneOffset();
        const localDate = new Date(date.getTime() - (offset * 60 * 1000));

        return localDate.toISOString().slice(0, 16);
    };

    const preencherFormulario = () => {
        if (programacaoData) {
            setFormData(prev => ({
                ...prev,
                responsavel_id: programacaoData.responsavel_id || '',
                data_inicio: programacaoData.inicio_previsto ?
                    formatDateTimeLocal(programacaoData.inicio_previsto) : '',
                data_fim: programacaoData.fim_previsto ?
                    formatDateTimeLocal(programacaoData.fim_previsto) : '',
                observacoes: programacaoData.observacoes || ''
                // Manter setor_destino e departamento_destino já definidos
            }));
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

            // 🎯 NOTIFICAR COLABORADOR ATRIBUÍDO/EDITADO
            await notificarColaborador(Number(formData.responsavel_id), mensagem);

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

    // 🎯 FUNÇÃO PARA NOTIFICAR COLABORADOR ATRIBUÍDO/EDITADO
    const notificarColaborador = async (colaboradorId: number, mensagem: string) => {
        try {
            const colaborador = usuarios.find(u => u.id === colaboradorId);
            if (colaborador) {
                // Criar notificação no sistema
                await api.post('/api/notificacoes', {
                    usuario_id: colaboradorId,
                    titulo: isEdit ? 'Programação Editada' : isReatribuir ? 'Nova Atribuição' : 'Nova Programação',
                    mensagem: `${mensagem} - Responsável: ${colaborador.nome_completo}`,
                    tipo: 'PROGRAMACAO',
                    prioridade: 'ALTA'
                });

                console.log(`🔔 Notificação enviada para ${colaborador.nome_completo}`);
            }
        } catch (error) {
            console.error('Erro ao notificar colaborador:', error);
            // Não bloquear o fluxo se a notificação falhar
        }
    };

    const resetForm = () => {
        setFormData({
            responsavel_id: '',
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
                    {/* Informação sobre setor automático */}
                    <div className="bg-blue-50 border border-blue-200 rounded-md p-3">
                        <p className="text-sm text-blue-800">
                            <span className="font-medium">ℹ️ Setor:</span> A programação será atribuída automaticamente ao seu setor atual.
                        </p>
                    </div>

                    {/* Colaborador do Setor */}
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                            Colaborador do Setor *
                        </label>
                        <select
                            value={formData.responsavel_id}
                            onChange={(e) => handleInputChange('responsavel_id', e.target.value ? Number(e.target.value) : '')}
                            className={`w-full border rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                                errors.responsavel_id ? 'border-red-300' : 'border-gray-300'
                            }`}
                        >
                            <option value="">Selecione um colaborador</option>
                            {usuariosFiltrados.map(colaborador => (
                                <option key={colaborador.id} value={colaborador.id}>
                                    {colaborador.nome_completo} - {colaborador.privilege_level}
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
