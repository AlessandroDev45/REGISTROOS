import React, { useState, useEffect } from 'react';
import api from '../services/api';

interface ResolucaoPendenciaModalProps {
    isOpen: boolean;
    onClose: () => void;
    pendencia: Pendencia | null;
    onSuccess: () => void;
}

interface Usuario {
    id: number;
    nome_completo: string;
    email: string;
    privilege_level: string;
    setor?: string;
    departamento?: string;
}

interface Pendencia {
    id: number;
    numero_os: string;
    cliente: string;
    tipo_maquina: string;
    descricao_maquina: string;
    descricao_pendencia: string;
    prioridade: string;
    status: string;
    setor_origem: string;
    departamento_origem: string;
    data_criacao: string;
    data_prazo?: string;
    usuario_criacao?: string;
}

interface FormData {
    solucao_aplicada: string;
    observacoes_fechamento: string;
    tempo_resolucao_horas: number | '';
    materiais_utilizados: string;
    custo_resolucao: number | '';
    responsavel_resolucao: string;
    data_resolucao: string;
    status_final: string;
}

const ResolucaoPendenciaModal: React.FC<ResolucaoPendenciaModalProps> = ({
    isOpen,
    onClose,
    pendencia,
    onSuccess
}) => {
    const [formData, setFormData] = useState<FormData>({
        solucao_aplicada: '',
        observacoes_fechamento: '',
        tempo_resolucao_horas: '',
        materiais_utilizados: '',
        custo_resolucao: '',
        responsavel_resolucao: '',
        data_resolucao: new Date().toISOString().slice(0, 16),
        status_final: 'FECHADA'
    });

    const [usuarios, setUsuarios] = useState<Usuario[]>([]);
    const [usuariosFiltrados, setUsuariosFiltrados] = useState<Usuario[]>([]);
    const [loading, setLoading] = useState(false);
    const [errors, setErrors] = useState<Record<string, string>>({});

    useEffect(() => {
        if (isOpen && pendencia) {
            carregarUsuarios();
            // Reset form when opening
            setFormData({
                solucao_aplicada: '',
                observacoes_fechamento: '',
                tempo_resolucao_horas: '',
                materiais_utilizados: '',
                custo_resolucao: '',
                responsavel_resolucao: '',
                data_resolucao: new Date().toISOString().slice(0, 16),
                status_final: 'FECHADA'
            });
            setErrors({});
        }
    }, [isOpen, pendencia]);

    // Filtrar usuários por departamento/setor da pendência
    useEffect(() => {
        if (pendencia && usuarios.length > 0) {
            let usuariosFiltered = usuarios;

            // Filtrar por departamento da pendência
            if (pendencia.departamento_origem) {
                usuariosFiltered = usuariosFiltered.filter(
                    usuario => usuario.departamento === pendencia.departamento_origem
                );
            }

            // Filtrar por setor da pendência
            if (pendencia.setor_origem) {
                usuariosFiltered = usuariosFiltered.filter(
                    usuario => usuario.setor === pendencia.setor_origem
                );
            }

            // Filtrar apenas técnicos e supervisores para resolução
            usuariosFiltered = usuariosFiltered.filter(
                usuario => ['TECNICO', 'SUPERVISOR', 'GESTAO'].includes(usuario.privilege_level)
            );

            setUsuariosFiltrados(usuariosFiltered);
        }
    }, [pendencia, usuarios]);

    const carregarUsuarios = async () => {
        try {
            const response = await api.get('/usuarios');
            setUsuarios(response.data || []);
        } catch (error) {
            console.error('Erro ao carregar usuários:', error);
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

        if (!formData.solucao_aplicada.trim()) {
            novosErros.solucao_aplicada = 'Solução aplicada é obrigatória';
        }

        if (formData.solucao_aplicada.trim().length < 10) {
            novosErros.solucao_aplicada = 'Solução deve ter pelo menos 10 caracteres';
        }

        if (!formData.responsavel_resolucao.trim()) {
            novosErros.responsavel_resolucao = 'Responsável pela resolução é obrigatório';
        }

        if (!formData.data_resolucao) {
            novosErros.data_resolucao = 'Data de resolução é obrigatória';
        }

        if (formData.tempo_resolucao_horas && Number(formData.tempo_resolucao_horas) <= 0) {
            novosErros.tempo_resolucao_horas = 'Tempo deve ser maior que zero';
        }

        if (formData.custo_resolucao && Number(formData.custo_resolucao) < 0) {
            novosErros.custo_resolucao = 'Custo não pode ser negativo';
        }

        setErrors(novosErros);
        return Object.keys(novosErros).length === 0;
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();

        if (!pendencia || !validarFormulario()) {
            return;
        }

        setLoading(true);
        try {
            const dadosResolucao = {
                ...formData,
                tempo_resolucao_horas: formData.tempo_resolucao_horas ? Number(formData.tempo_resolucao_horas) : null,
                custo_resolucao: formData.custo_resolucao ? Number(formData.custo_resolucao) : null,
                status: formData.status_final
            };

            await api.patch(`/pendencias/${pendencia.id}/resolver`, dadosResolucao);

            alert('Pendência resolvida com sucesso!');
            onSuccess();
            onClose();
        } catch (error: any) {
            console.error('Erro ao resolver pendência:', error);
            alert(error.response?.data?.detail || 'Erro ao resolver pendência');
        } finally {
            setLoading(false);
        }
    };

    const calcularDiasAberta = () => {
        if (!pendencia) return 0;
        const dataAtual = new Date();
        const dataCriacao = new Date(pendencia.data_criacao);
        const diffTime = Math.abs(dataAtual.getTime() - dataCriacao.getTime());
        return Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    };

    const getPriorityColor = (prioridade: string) => {
        switch (prioridade) {
            case 'URGENTE': return 'text-red-600 bg-red-100';
            case 'ALTA': return 'text-orange-600 bg-orange-100';
            case 'NORMAL': return 'text-blue-600 bg-blue-100';
            case 'BAIXA': return 'text-green-600 bg-green-100';
            default: return 'text-gray-600 bg-gray-100';
        }
    };

    if (!isOpen || !pendencia) return null;

    const diasAberta = calcularDiasAberta();
    const isVencida = diasAberta > 7; // Considera vencida após 7 dias

    return (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg p-6 max-w-4xl w-full mx-4 max-h-[90vh] overflow-y-auto">
                <div className="flex justify-between items-center mb-6">
                    <h2 className="text-xl font-semibold text-gray-900">
                        🔧 Resolver Pendência #{pendencia.id}
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

                {/* Informações da Pendência */}
                <div className="bg-gray-50 rounded-lg p-4 mb-6">
                    <h3 className="text-lg font-medium text-gray-900 mb-3">📋 Informações da Pendência</h3>
                    <div className="grid grid-cols-2 gap-4">
                        <div>
                            <p className="text-sm text-gray-600">OS:</p>
                            <p className="font-medium">{pendencia.numero_os}</p>
                        </div>
                        <div>
                            <p className="text-sm text-gray-600">Cliente:</p>
                            <p className="font-medium">{pendencia.cliente}</p>
                        </div>
                        <div>
                            <p className="text-sm text-gray-600">Equipamento:</p>
                            <p className="font-medium">{pendencia.tipo_maquina} - {pendencia.descricao_maquina}</p>
                        </div>
                        <div>
                            <p className="text-sm text-gray-600">Setor/Departamento:</p>
                            <p className="font-medium">{pendencia.setor_origem} - {pendencia.departamento_origem}</p>
                        </div>
                        <div>
                            <p className="text-sm text-gray-600">Prioridade:</p>
                            <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getPriorityColor(pendencia.prioridade)}`}>
                                {pendencia.prioridade}
                            </span>
                        </div>
                        <div>
                            <p className="text-sm text-gray-600">Dias em aberto:</p>
                            <p className={`font-medium ${isVencida ? 'text-red-600' : ''}`}>
                                {diasAberta} dia(s) {isVencida && '⚠️ VENCIDA'}
                            </p>
                        </div>
                    </div>
                    <div className="mt-4">
                        <p className="text-sm text-gray-600">Descrição da Pendência:</p>
                        <p className="font-medium bg-white p-3 rounded border">{pendencia.descricao_pendencia}</p>
                    </div>
                </div>

                {/* Formulário de Resolução */}
                <form onSubmit={handleSubmit} className="space-y-4">
                    {/* Solução Aplicada */}
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                            Solução Aplicada *
                        </label>
                        <textarea
                            value={formData.solucao_aplicada}
                            onChange={(e) => handleInputChange('solucao_aplicada', e.target.value)}
                            rows={4}
                            className={`w-full border rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                                errors.solucao_aplicada ? 'border-red-300' : 'border-gray-300'
                            }`}
                            placeholder="Descreva detalhadamente a solução aplicada para resolver a pendência..."
                        />
                        {errors.solucao_aplicada && (
                            <p className="text-red-500 text-xs mt-1">{errors.solucao_aplicada}</p>
                        )}
                    </div>

                    {/* Responsável e Data */}
                    <div className="grid grid-cols-2 gap-4">
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">
                                Responsável pela Resolução *
                            </label>
                            <select
                                value={formData.responsavel_resolucao}
                                onChange={(e) => handleInputChange('responsavel_resolucao', e.target.value)}
                                className={`w-full border rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                                    errors.responsavel_resolucao ? 'border-red-300' : 'border-gray-300'
                                }`}
                            >
                                <option value="">Selecione o responsável</option>
                                {usuariosFiltrados.map(usuario => (
                                    <option key={usuario.id} value={usuario.nome_completo}>
                                        {usuario.nome_completo} - {usuario.setor} ({usuario.privilege_level})
                                    </option>
                                ))}
                            </select>
                            {usuariosFiltrados.length === 0 && pendencia && (
                                <p className="text-amber-600 text-xs mt-1">
                                    ⚠️ Nenhum técnico encontrado para {pendencia.departamento_origem} - {pendencia.setor_origem}
                                </p>
                            )}
                            {errors.responsavel_resolucao && (
                                <p className="text-red-500 text-xs mt-1">{errors.responsavel_resolucao}</p>
                            )}
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">
                                Data/Hora da Resolução *
                            </label>
                            <input
                                type="datetime-local"
                                value={formData.data_resolucao}
                                onChange={(e) => handleInputChange('data_resolucao', e.target.value)}
                                className={`w-full border rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                                    errors.data_resolucao ? 'border-red-300' : 'border-gray-300'
                                }`}
                            />
                            {errors.data_resolucao && (
                                <p className="text-red-500 text-xs mt-1">{errors.data_resolucao}</p>
                            )}
                        </div>
                    </div>

                    {/* Tempo e Custo */}
                    <div className="grid grid-cols-2 gap-4">
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">
                                Tempo de Resolução (horas)
                            </label>
                            <input
                                type="number"
                                step="0.5"
                                min="0"
                                value={formData.tempo_resolucao_horas}
                                onChange={(e) => handleInputChange('tempo_resolucao_horas', e.target.value ? Number(e.target.value) : '')}
                                className={`w-full border rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                                    errors.tempo_resolucao_horas ? 'border-red-300' : 'border-gray-300'
                                }`}
                                placeholder="Ex: 2.5"
                            />
                            {errors.tempo_resolucao_horas && (
                                <p className="text-red-500 text-xs mt-1">{errors.tempo_resolucao_horas}</p>
                            )}
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">
                                Custo da Resolução (R$)
                            </label>
                            <input
                                type="number"
                                step="0.01"
                                min="0"
                                value={formData.custo_resolucao}
                                onChange={(e) => handleInputChange('custo_resolucao', e.target.value ? Number(e.target.value) : '')}
                                className={`w-full border rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                                    errors.custo_resolucao ? 'border-red-300' : 'border-gray-300'
                                }`}
                                placeholder="Ex: 150.00"
                            />
                            {errors.custo_resolucao && (
                                <p className="text-red-500 text-xs mt-1">{errors.custo_resolucao}</p>
                            )}
                        </div>
                    </div>

                    {/* Materiais Utilizados */}
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                            Materiais/Peças Utilizados
                        </label>
                        <textarea
                            value={formData.materiais_utilizados}
                            onChange={(e) => handleInputChange('materiais_utilizados', e.target.value)}
                            rows={2}
                            className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                            placeholder="Liste os materiais, peças ou componentes utilizados na resolução..."
                        />
                    </div>

                    {/* Observações */}
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                            Observações Adicionais
                        </label>
                        <textarea
                            value={formData.observacoes_fechamento}
                            onChange={(e) => handleInputChange('observacoes_fechamento', e.target.value)}
                            rows={3}
                            className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                            placeholder="Observações adicionais sobre a resolução, lições aprendidas, etc..."
                        />
                    </div>

                    {/* Status Final */}
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                            Status Final
                        </label>
                        <select
                            value={formData.status_final}
                            onChange={(e) => handleInputChange('status_final', e.target.value)}
                            className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                        >
                            <option value="FECHADA">✅ Fechada - Resolvida</option>
                            <option value="CANCELADA">❌ Cancelada - Não aplicável</option>
                            <option value="TRANSFERIDA">🔄 Transferida - Para outro setor</option>
                        </select>
                    </div>

                    {/* Botões */}
                    <div className="flex justify-end space-x-3 pt-6 border-t">
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
                            className="px-6 py-2 text-sm font-medium text-white bg-green-600 border border-transparent rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 disabled:opacity-50"
                        >
                            {loading ? 'Resolvendo...' : '🔧 Resolver Pendência'}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
};

export default ResolucaoPendenciaModal;
