import React, { useState, useEffect } from 'react';
import { X, FileText, Clock, CheckCircle, AlertTriangle, Users, BarChart3 } from 'lucide-react';
import api from '../services/api';

interface RelatorioCompletoModalProps {
    isOpen: boolean;
    onClose: () => void;
    osId: number;
    origemPagina?: 'desenvolvimento' | 'consulta';
}

interface RelatorioData {
    os_dados_gerais: any;
    apontamentos_por_setor: any;
    apontamentos_detalhados: any[];
    resultados_testes: any[];
    pendencias_retrabalhos: any[];
    programacoes: any[];
    metricas_consolidadas: any;
    resumo_gerencial: any;
    data_geracao: string;
}

const RelatorioCompletoModal: React.FC<RelatorioCompletoModalProps> = ({
    isOpen,
    onClose,
    osId,
    origemPagina = 'consulta'
}) => {
    const [activeTab, setActiveTab] = useState<'resumo' | 'apontamentos' | 'testes' | 'horas' | 'retrabalhos'>('resumo');
    const [loading, setLoading] = useState(false);
    const [relatorioData, setRelatorioData] = useState<RelatorioData | null>(null);
    const [error, setError] = useState('');

    useEffect(() => {
        if (isOpen && osId) {
            fetchRelatorioCompleto();
        }
    }, [isOpen, osId]);

    const fetchRelatorioCompleto = async () => {
        try {
            setLoading(true);
            setError('');
            
            const response = await api.get(`/os/${osId}/relatorio-completo`);
            setRelatorioData(response.data);
            
        } catch (err: any) {
            console.error('Erro ao buscar relatório completo:', err);
            setError('Erro ao carregar relatório completo');
        } finally {
            setLoading(false);
        }
    };

    const handleClose = () => {
        setRelatorioData(null);
        setError('');
        setActiveTab('resumo');
        onClose();
    };

    const formatDate = (dateStr: string) => {
        if (!dateStr) return 'N/A';
        try {
            return new Date(dateStr).toLocaleString('pt-BR');
        } catch {
            return 'Data inválida';
        }
    };

    const formatHours = (hours: number) => {
        return `${hours.toFixed(1)}h`;
    };

    const getStatusColor = (status: string) => {
        switch (status?.toUpperCase()) {
            case 'OK': return 'text-green-600 bg-green-100';
            case 'ATENÇÃO': return 'text-yellow-600 bg-yellow-100';
            case 'CRÍTICO': return 'text-red-600 bg-red-100';
            default: return 'text-gray-600 bg-gray-100';
        }
    };

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-lg shadow-xl w-full h-[90vh] flex flex-col">
                {/* Header */}
                <div className="flex items-center justify-between p-6 border-b border-gray-200">
                    <div className="flex items-center space-x-3">
                        <FileText className="h-6 w-6 text-blue-600" />
                        <div>
                            <h2 className="text-xl font-bold text-gray-900">
                                Relatório Completo da OS
                            </h2>
                            {relatorioData && (
                                <p className="text-sm text-gray-600">
                                    {relatorioData.os_dados_gerais.os_numero} - {relatorioData.os_dados_gerais.cliente_nome}
                                </p>
                            )}
                        </div>
                    </div>
                    <button
                        onClick={handleClose}
                        className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
                    >
                        <X className="h-5 w-5 text-gray-500" />
                    </button>
                </div>

                {/* Tabs */}
                <div className="flex border-b border-gray-200 px-6">
                    {[
                        { id: 'resumo', label: 'Resumo Gerencial', icon: BarChart3 },
                        { id: 'apontamentos', label: 'Apontamentos por Setor', icon: Users },
                        { id: 'testes', label: 'Resultados de Testes', icon: CheckCircle },
                        { id: 'horas', label: 'Análise de Horas', icon: Clock },
                        { id: 'retrabalhos', label: 'Retrabalhos e Falhas', icon: AlertTriangle }
                    ].map((tab) => {
                        const Icon = tab.icon;
                        return (
                            <button
                                key={tab.id}
                                onClick={() => setActiveTab(tab.id as any)}
                                className={`flex items-center space-x-2 px-4 py-3 border-b-2 font-medium text-sm transition-colors ${
                                    activeTab === tab.id
                                        ? 'border-blue-500 text-blue-600'
                                        : 'border-transparent text-gray-500 hover:text-gray-700'
                                }`}
                            >
                                <Icon className="h-4 w-4" />
                                <span>{tab.label}</span>
                            </button>
                        );
                    })}
                </div>

                {/* Content */}
                <div className="flex-1 overflow-auto p-6">
                    {loading && (
                        <div className="flex items-center justify-center h-64">
                            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                            <span className="ml-3 text-gray-600">Carregando relatório...</span>
                        </div>
                    )}

                    {error && (
                        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                            <div className="flex items-center">
                                <AlertTriangle className="h-5 w-5 text-red-500 mr-2" />
                                <span className="text-red-700">{error}</span>
                            </div>
                        </div>
                    )}

                    {relatorioData && !loading && !error && (
                        <>
                            {/* ABA 1: RESUMO GERENCIAL */}
                            {activeTab === 'resumo' && (
                                <div className="space-y-6">
                                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                                        {/* Cards de Status */}
                                        <div className="bg-white border border-gray-200 rounded-lg p-4">
                                            <div className="flex items-center justify-between">
                                                <div>
                                                    <p className="text-sm text-gray-600">Status da OS</p>
                                                    <p className="text-lg font-semibold">{relatorioData.resumo_gerencial.status_os}</p>
                                                </div>
                                                <div className={`px-2 py-1 rounded text-xs font-medium ${getStatusColor(relatorioData.resumo_gerencial.status_prazo)}`}>
                                                    {relatorioData.resumo_gerencial.status_prazo}
                                                </div>
                                            </div>
                                        </div>

                                        <div className="bg-white border border-gray-200 rounded-lg p-4">
                                            <div className="flex items-center justify-between">
                                                <div>
                                                    <p className="text-sm text-gray-600">Qualidade</p>
                                                    <p className="text-lg font-semibold">{relatorioData.resumo_gerencial.aprovacao_testes}%</p>
                                                </div>
                                                <div className={`px-2 py-1 rounded text-xs font-medium ${getStatusColor(relatorioData.resumo_gerencial.status_qualidade)}`}>
                                                    {relatorioData.resumo_gerencial.status_qualidade}
                                                </div>
                                            </div>
                                        </div>

                                        <div className="bg-white border border-gray-200 rounded-lg p-4">
                                            <div className="flex items-center justify-between">
                                                <div>
                                                    <p className="text-sm text-gray-600">Desvio de Horas</p>
                                                    <p className="text-lg font-semibold">{relatorioData.resumo_gerencial.desvio_percentual}%</p>
                                                </div>
                                                <div className={`px-2 py-1 rounded text-xs font-medium ${getStatusColor(relatorioData.resumo_gerencial.indicadores_principais.eficiencia_horas)}`}>
                                                    {Math.abs(relatorioData.resumo_gerencial.desvio_percentual) <= 10 ? 'OK' : 'ATENÇÃO'}
                                                </div>
                                            </div>
                                        </div>

                                        <div className="bg-white border border-gray-200 rounded-lg p-4">
                                            <div className="flex items-center justify-between">
                                                <div>
                                                    <p className="text-sm text-gray-600">Pendências</p>
                                                    <p className="text-lg font-semibold">{relatorioData.resumo_gerencial.pendencias_abertas}</p>
                                                </div>
                                                <div className={`px-2 py-1 rounded text-xs font-medium ${getStatusColor(relatorioData.resumo_gerencial.indicadores_principais.gestao_pendencias)}`}>
                                                    {relatorioData.resumo_gerencial.pendencias_abertas === 0 ? 'OK' : 'ATENÇÃO'}
                                                </div>
                                            </div>
                                        </div>
                                    </div>

                                    {/* Dados Gerais da OS */}
                                    <div className="bg-white border border-gray-200 rounded-lg p-6">
                                        <h3 className="text-lg font-semibold mb-4">Dados Gerais da OS</h3>
                                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                                            <div>
                                                <p className="text-sm text-gray-600">Número da OS</p>
                                                <p className="font-medium">{relatorioData.os_dados_gerais.os_numero}</p>
                                            </div>
                                            <div>
                                                <p className="text-sm text-gray-600">Cliente</p>
                                                <p className="font-medium">{relatorioData.os_dados_gerais.cliente_nome || 'N/A'}</p>
                                            </div>
                                            <div>
                                                <p className="text-sm text-gray-600">Equipamento</p>
                                                <p className="font-medium">{relatorioData.os_dados_gerais.descricao_maquina || 'N/A'}</p>
                                            </div>
                                            <div>
                                                <p className="text-sm text-gray-600">Tipo de Máquina</p>
                                                <p className="font-medium">{relatorioData.os_dados_gerais.tipo_maquina_nome || 'N/A'}</p>
                                            </div>
                                            <div>
                                                <p className="text-sm text-gray-600">Prioridade</p>
                                                <p className="font-medium">{relatorioData.os_dados_gerais.prioridade || 'MEDIA'}</p>
                                            </div>
                                            <div>
                                                <p className="text-sm text-gray-600">Data de Criação</p>
                                                <p className="font-medium">{formatDate(relatorioData.os_dados_gerais.data_criacao)}</p>
                                            </div>
                                        </div>
                                    </div>

                                    {/* Métricas Principais */}
                                    <div className="bg-white border border-gray-200 rounded-lg p-6">
                                        <h3 className="text-lg font-semibold mb-4">Métricas Principais</h3>
                                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                                            <div className="text-center">
                                                <p className="text-2xl font-bold text-blue-600">
                                                    {formatHours(relatorioData.metricas_consolidadas.horas_realizadas)}
                                                </p>
                                                <p className="text-sm text-gray-600">Horas Realizadas</p>
                                            </div>
                                            <div className="text-center">
                                                <p className="text-2xl font-bold text-green-600">
                                                    {formatHours(relatorioData.metricas_consolidadas.horas_orcadas)}
                                                </p>
                                                <p className="text-sm text-gray-600">Horas Orçadas</p>
                                            </div>
                                            <div className="text-center">
                                                <p className="text-2xl font-bold text-purple-600">
                                                    {relatorioData.resumo_gerencial.setores_envolvidos}
                                                </p>
                                                <p className="text-sm text-gray-600">Setores Envolvidos</p>
                                            </div>
                                            <div className="text-center">
                                                <p className="text-2xl font-bold text-orange-600">
                                                    {relatorioData.metricas_consolidadas.total_testes}
                                                </p>
                                                <p className="text-sm text-gray-600">Testes Realizados</p>
                                            </div>
                                        </div>
                                    </div>

                                    {/* Setor Gargalo */}
                                    {relatorioData.resumo_gerencial.setor_gargalo !== 'N/A' && (
                                        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                                            <div className="flex items-center">
                                                <AlertTriangle className="h-5 w-5 text-yellow-500 mr-2" />
                                                <div>
                                                    <p className="font-medium text-yellow-800">Setor Gargalo Identificado</p>
                                                    <p className="text-sm text-yellow-700">
                                                        {relatorioData.resumo_gerencial.setor_gargalo} - {formatHours(relatorioData.resumo_gerencial.horas_setor_gargalo)}
                                                    </p>
                                                </div>
                                            </div>
                                        </div>
                                    )}
                                </div>
                            )}

                            {/* ABA 2: APONTAMENTOS POR SETOR */}
                            {activeTab === 'apontamentos' && (
                                <div className="space-y-6">
                                    {Object.values(relatorioData.apontamentos_por_setor).map((setor: any, index) => (
                                        <div key={index} className="bg-white border border-gray-200 rounded-lg p-6">
                                            <div className="flex items-center justify-between mb-4">
                                                <h3 className="text-lg font-semibold">{setor.nome}</h3>
                                                <div className="flex space-x-4 text-sm text-gray-600">
                                                    <span>Horas: {formatHours(setor.horas_total)}</span>
                                                    <span>Testes: {setor.testes_realizados}</span>
                                                    <span>Usuários: {setor.usuarios.length}</span>
                                                </div>
                                            </div>
                                            
                                            <div className="overflow-x-auto">
                                                <table className="min-w-full divide-y divide-gray-200">
                                                    <thead className="bg-gray-50">
                                                        <tr>
                                                            <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Usuário</th>
                                                            <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Atividade</th>
                                                            <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Início</th>
                                                            <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Fim</th>
                                                            <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                                                        </tr>
                                                    </thead>
                                                    <tbody className="bg-white divide-y divide-gray-200">
                                                        {setor.apontamentos.slice(0, 5).map((apt: any, aptIndex: number) => (
                                                            <tr key={aptIndex}>
                                                                <td className="px-4 py-2 text-sm text-gray-900">{apt.usuario_nome}</td>
                                                                <td className="px-4 py-2 text-sm text-gray-900">{apt.atividade_nome || 'N/A'}</td>
                                                                <td className="px-4 py-2 text-sm text-gray-900">{formatDate(apt.data_hora_inicio)}</td>
                                                                <td className="px-4 py-2 text-sm text-gray-900">{formatDate(apt.data_hora_fim)}</td>
                                                                <td className="px-4 py-2 text-sm">
                                                                    <span className={`px-2 py-1 rounded text-xs font-medium ${
                                                                        apt.status_apontamento === 'FINALIZADO' ? 'bg-green-100 text-green-800' :
                                                                        apt.status_apontamento === 'EM_ANDAMENTO' ? 'bg-blue-100 text-blue-800' :
                                                                        'bg-gray-100 text-gray-800'
                                                                    }`}>
                                                                        {apt.status_apontamento}
                                                                    </span>
                                                                </td>
                                                            </tr>
                                                        ))}
                                                    </tbody>
                                                </table>
                                                {setor.apontamentos.length > 5 && (
                                                    <p className="text-sm text-gray-500 mt-2 text-center">
                                                        ... e mais {setor.apontamentos.length - 5} apontamentos
                                                    </p>
                                                )}
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            )}

                            {/* ABA 3: RESULTADOS DE TESTES */}
                            {activeTab === 'testes' && (
                                <div className="space-y-6">
                                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                                        <div className="bg-green-50 border border-green-200 rounded-lg p-4 text-center">
                                            <p className="text-2xl font-bold text-green-600">{relatorioData.metricas_consolidadas.testes_aprovados}</p>
                                            <p className="text-sm text-green-700">Aprovados</p>
                                        </div>
                                        <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-center">
                                            <p className="text-2xl font-bold text-red-600">{relatorioData.metricas_consolidadas.testes_reprovados}</p>
                                            <p className="text-sm text-red-700">Reprovados</p>
                                        </div>
                                        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 text-center">
                                            <p className="text-2xl font-bold text-yellow-600">{relatorioData.metricas_consolidadas.testes_pendentes}</p>
                                            <p className="text-sm text-yellow-700">Pendentes</p>
                                        </div>
                                    </div>

                                    <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
                                        <div className="px-6 py-4 border-b border-gray-200">
                                            <h3 className="text-lg font-semibold">Todos os Testes Realizados</h3>
                                        </div>
                                        <div className="overflow-x-auto">
                                            <table className="min-w-full divide-y divide-gray-200">
                                                <thead className="bg-gray-50">
                                                    <tr>
                                                        <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Teste</th>
                                                        <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Categoria</th>
                                                        <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Subcategoria</th>
                                                        <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Setor</th>
                                                        <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Usuário</th>
                                                        <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Resultado</th>
                                                        <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Data</th>
                                                        <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Observação</th>
                                                    </tr>
                                                </thead>
                                                <tbody className="bg-white divide-y divide-gray-200">
                                                    {relatorioData.resultados_testes.map((teste: any, index: number) => (
                                                        <tr key={index} className="hover:bg-gray-50">
                                                            <td className="px-4 py-3 text-sm font-medium text-gray-900">{teste.teste_nome}</td>
                                                            <td className="px-4 py-3 text-sm text-gray-900">
                                                                <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                                                                    teste.categoria === 'Visual' ? 'bg-blue-100 text-blue-800' :
                                                                    teste.categoria === 'Elétricos' ? 'bg-yellow-100 text-yellow-800' :
                                                                    teste.categoria === 'Mecânicos' ? 'bg-green-100 text-green-800' :
                                                                    'bg-gray-100 text-gray-800'
                                                                }`}>
                                                                    {teste.categoria || 'Visual'}
                                                                </span>
                                                            </td>
                                                            <td className="px-4 py-3 text-sm text-gray-900">
                                                                <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                                                                    teste.subcategoria === 1 ? 'bg-purple-100 text-purple-800' : 'bg-gray-100 text-gray-800'
                                                                }`}>
                                                                    {teste.subcategoria === 1 ? 'Especiais' : 'Padrão'}
                                                                </span>
                                                            </td>
                                                            <td className="px-4 py-3 text-sm text-gray-900">{teste.apontamento_setor}</td>
                                                            <td className="px-4 py-3 text-sm text-gray-900">{teste.usuario_nome}</td>
                                                            <td className="px-4 py-3 text-sm">
                                                                <span className={`px-2 py-1 rounded text-xs font-medium ${
                                                                    teste.resultado === 'APROVADO' ? 'bg-green-100 text-green-800' :
                                                                    teste.resultado === 'REPROVADO' ? 'bg-red-100 text-red-800' :
                                                                    'bg-yellow-100 text-yellow-800'
                                                                }`}>
                                                                    {teste.resultado}
                                                                </span>
                                                            </td>
                                                            <td className="px-4 py-3 text-sm text-gray-900">{formatDate(teste.data_registro)}</td>
                                                            <td className="px-4 py-3 text-sm text-gray-900 max-w-xs truncate" title={teste.observacao}>
                                                                {teste.observacao || 'N/A'}
                                                            </td>
                                                        </tr>
                                                    ))}
                                                </tbody>
                                            </table>
                                            {relatorioData.resultados_testes.length === 0 && (
                                                <div className="text-center py-8 text-gray-500">
                                                    Nenhum teste realizado ainda
                                                </div>
                                            )}
                                        </div>
                                    </div>
                                </div>
                            )}

                            {/* ABA 4: ANÁLISE DE HORAS */}
                            {activeTab === 'horas' && (
                                <div className="space-y-6">
                                    {/* Resumo de Horas */}
                                    <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                                        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 text-center">
                                            <p className="text-2xl font-bold text-blue-600">
                                                {formatHours(relatorioData.metricas_consolidadas.horas_orcadas)}
                                            </p>
                                            <p className="text-sm text-blue-700">Horas Orçadas</p>
                                        </div>
                                        <div className="bg-green-50 border border-green-200 rounded-lg p-4 text-center">
                                            <p className="text-2xl font-bold text-green-600">
                                                {formatHours(relatorioData.metricas_consolidadas.horas_realizadas)}
                                            </p>
                                            <p className="text-sm text-green-700">Horas Realizadas</p>
                                        </div>
                                        <div className={`border rounded-lg p-4 text-center ${
                                            relatorioData.metricas_consolidadas.desvio_horas >= 0
                                                ? 'bg-red-50 border-red-200'
                                                : 'bg-green-50 border-green-200'
                                        }`}>
                                            <p className={`text-2xl font-bold ${
                                                relatorioData.metricas_consolidadas.desvio_horas >= 0
                                                    ? 'text-red-600'
                                                    : 'text-green-600'
                                            }`}>
                                                {relatorioData.metricas_consolidadas.desvio_horas >= 0 ? '+' : ''}
                                                {formatHours(relatorioData.metricas_consolidadas.desvio_horas)}
                                            </p>
                                            <p className={`text-sm ${
                                                relatorioData.metricas_consolidadas.desvio_horas >= 0
                                                    ? 'text-red-700'
                                                    : 'text-green-700'
                                            }`}>
                                                Desvio ({relatorioData.metricas_consolidadas.percentual_desvio.toFixed(1)}%)
                                            </p>
                                        </div>
                                        <div className="bg-purple-50 border border-purple-200 rounded-lg p-4 text-center">
                                            <p className="text-2xl font-bold text-purple-600">
                                                {(relatorioData.metricas_consolidadas.etapas_realizadas?.inicial || 0) +
                                                 (relatorioData.metricas_consolidadas.etapas_realizadas?.parcial || 0) +
                                                 (relatorioData.metricas_consolidadas.etapas_realizadas?.final || 0)}
                                            </p>
                                            <p className="text-sm text-purple-700">Total de Etapas</p>
                                        </div>
                                    </div>

                                    {/* Análise de Etapas */}
                                    <div className="bg-white border border-gray-200 rounded-lg p-6">
                                        <h3 className="text-lg font-semibold mb-4">📋 Análise de Etapas</h3>
                                        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                                            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 text-center">
                                                <p className="text-xl font-bold text-blue-600">
                                                    {relatorioData.metricas_consolidadas.etapas_realizadas?.inicial || 0}
                                                </p>
                                                <p className="text-sm text-blue-700">Etapa Inicial</p>
                                                <p className="text-xs text-gray-600 mt-1">
                                                    {formatHours(relatorioData.metricas_consolidadas.horas_por_etapa?.inicial || 0)}
                                                </p>
                                            </div>
                                            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 text-center">
                                                <p className="text-xl font-bold text-yellow-600">
                                                    {relatorioData.metricas_consolidadas.etapas_realizadas?.parcial || 0}
                                                </p>
                                                <p className="text-sm text-yellow-700">Etapa Parcial</p>
                                                <p className="text-xs text-gray-600 mt-1">
                                                    {formatHours(relatorioData.metricas_consolidadas.horas_por_etapa?.parcial || 0)}
                                                </p>
                                            </div>
                                            <div className="bg-green-50 border border-green-200 rounded-lg p-4 text-center">
                                                <p className="text-xl font-bold text-green-600">
                                                    {relatorioData.metricas_consolidadas.etapas_realizadas?.final || 0}
                                                </p>
                                                <p className="text-sm text-green-700">Etapa Final</p>
                                                <p className="text-xs text-gray-600 mt-1">
                                                    {formatHours(relatorioData.metricas_consolidadas.horas_por_etapa?.final || 0)}
                                                </p>
                                            </div>
                                        </div>
                                    </div>

                                    {/* Horas por Setor */}
                                    <div className="bg-white border border-gray-200 rounded-lg p-6">
                                        <h3 className="text-lg font-semibold mb-4">Horas por Setor</h3>
                                        <div className="space-y-3">
                                            {Object.entries(relatorioData.metricas_consolidadas.horas_por_setor).map(([setor, horas]: [string, any]) => (
                                                <div key={setor} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                                                    <span className="font-medium">{setor}</span>
                                                    <span className="text-blue-600 font-semibold">{formatHours(horas)}</span>
                                                </div>
                                            ))}
                                        </div>
                                    </div>

                                    {/* Análise de Eficiência */}
                                    <div className="bg-white border border-gray-200 rounded-lg p-6">
                                        <h3 className="text-lg font-semibold mb-4">Análise de Eficiência</h3>
                                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                            <div>
                                                <h4 className="font-medium mb-2">Indicadores de Performance</h4>
                                                <div className="space-y-2">
                                                    <div className="flex justify-between">
                                                        <span>Eficiência de Horas:</span>
                                                        <span className={`font-medium ${
                                                            Math.abs(relatorioData.metricas_consolidadas.percentual_desvio) <= 10
                                                                ? 'text-green-600'
                                                                : 'text-red-600'
                                                        }`}>
                                                            {Math.abs(relatorioData.metricas_consolidadas.percentual_desvio) <= 10 ? 'Excelente' : 'Precisa Atenção'}
                                                        </span>
                                                    </div>
                                                    <div className="flex justify-between">
                                                        <span>Desvio Percentual:</span>
                                                        <span className="font-medium">{relatorioData.metricas_consolidadas.percentual_desvio.toFixed(1)}%</span>
                                                    </div>
                                                </div>
                                            </div>
                                            <div>
                                                <h4 className="font-medium mb-2">Recomendações</h4>
                                                <div className="text-sm text-gray-600 space-y-1">
                                                    {Math.abs(relatorioData.metricas_consolidadas.percentual_desvio) > 20 && (
                                                        <p>• Revisar processo de orçamentação</p>
                                                    )}
                                                    {relatorioData.metricas_consolidadas.percentual_desvio > 10 && (
                                                        <p>• Analisar gargalos no setor {relatorioData.resumo_gerencial.setor_gargalo}</p>
                                                    )}
                                                    {relatorioData.metricas_consolidadas.percentual_desvio < -10 && (
                                                        <p>• Considerar otimização do orçamento</p>
                                                    )}
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            )}

                            {/* ABA 5: RETRABALHOS E FALHAS */}
                            {activeTab === 'retrabalhos' && (
                                <div className="space-y-6">
                                    {/* Resumo de Pendências */}
                                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                                        <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-center">
                                            <p className="text-2xl font-bold text-red-600">{relatorioData.metricas_consolidadas.total_pendencias}</p>
                                            <p className="text-sm text-red-700">Total de Pendências</p>
                                        </div>
                                        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 text-center">
                                            <p className="text-2xl font-bold text-yellow-600">{relatorioData.metricas_consolidadas.pendencias_abertas}</p>
                                            <p className="text-sm text-yellow-700">Pendências Abertas</p>
                                        </div>
                                        <div className="bg-orange-50 border border-orange-200 rounded-lg p-4 text-center">
                                            <p className="text-2xl font-bold text-orange-600">{relatorioData.metricas_consolidadas.total_retrabalhos}</p>
                                            <p className="text-sm text-orange-700">Retrabalhos</p>
                                        </div>
                                    </div>

                                    {/* Lista de Pendências */}
                                    <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
                                        <div className="px-6 py-4 border-b border-gray-200">
                                            <h3 className="text-lg font-semibold">Histórico de Pendências e Retrabalhos</h3>
                                        </div>
                                        <div className="overflow-x-auto">
                                            <table className="min-w-full divide-y divide-gray-200">
                                                <thead className="bg-gray-50">
                                                    <tr>
                                                        <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Descrição</th>
                                                        <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                                                        <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Responsável</th>
                                                        <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Data Início</th>
                                                        <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Tempo Aberto</th>
                                                        <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Solução</th>
                                                    </tr>
                                                </thead>
                                                <tbody className="bg-white divide-y divide-gray-200">
                                                    {relatorioData.pendencias_retrabalhos.map((pendencia: any, index: number) => (
                                                        <tr key={index} className="hover:bg-gray-50">
                                                            <td className="px-4 py-3 text-sm text-gray-900 max-w-xs">
                                                                <div className="truncate" title={pendencia.descricao_pendencia}>
                                                                    {pendencia.descricao_pendencia}
                                                                </div>
                                                            </td>
                                                            <td className="px-4 py-3 text-sm">
                                                                <span className={`px-2 py-1 rounded text-xs font-medium ${
                                                                    pendencia.status === 'FECHADA' ? 'bg-green-100 text-green-800' :
                                                                    pendencia.status === 'ABERTA' ? 'bg-red-100 text-red-800' :
                                                                    'bg-yellow-100 text-yellow-800'
                                                                }`}>
                                                                    {pendencia.status}
                                                                </span>
                                                            </td>
                                                            <td className="px-4 py-3 text-sm text-gray-900">{pendencia.responsavel_inicio_nome}</td>
                                                            <td className="px-4 py-3 text-sm text-gray-900">{formatDate(pendencia.data_inicio)}</td>
                                                            <td className="px-4 py-3 text-sm text-gray-900">
                                                                {pendencia.tempo_aberto_horas ? `${pendencia.tempo_aberto_horas.toFixed(1)}h` : 'N/A'}
                                                            </td>
                                                            <td className="px-4 py-3 text-sm text-gray-900 max-w-xs">
                                                                <div className="truncate" title={pendencia.solucao_aplicada}>
                                                                    {pendencia.solucao_aplicada || 'Pendente'}
                                                                </div>
                                                            </td>
                                                        </tr>
                                                    ))}
                                                </tbody>
                                            </table>
                                            {relatorioData.pendencias_retrabalhos.length === 0 && (
                                                <div className="text-center py-8 text-gray-500">
                                                    Nenhuma pendência registrada
                                                </div>
                                            )}
                                        </div>
                                    </div>

                                    {/* Análise de Causas */}
                                    {relatorioData.pendencias_retrabalhos.length > 0 && (
                                        <div className="bg-white border border-gray-200 rounded-lg p-6">
                                            <h3 className="text-lg font-semibold mb-4">Análise de Causas</h3>
                                            <div className="text-sm text-gray-600">
                                                <p>• Total de pendências: {relatorioData.metricas_consolidadas.total_pendencias}</p>
                                                <p>• Pendências ainda abertas: {relatorioData.metricas_consolidadas.pendencias_abertas}</p>
                                                <p>• Taxa de resolução: {
                                                    relatorioData.metricas_consolidadas.total_pendencias > 0
                                                        ? ((relatorioData.metricas_consolidadas.total_pendencias - relatorioData.metricas_consolidadas.pendencias_abertas) / relatorioData.metricas_consolidadas.total_pendencias * 100).toFixed(1)
                                                        : 0
                                                }%</p>
                                            </div>
                                        </div>
                                    )}
                                </div>
                            )}
                        </>
                    )}
                </div>

                {/* Footer */}
                <div className="flex items-center justify-between p-6 border-t border-gray-200 bg-gray-50">
                    <div className="text-sm text-gray-600">
                        {relatorioData && (
                            <>Relatório gerado em: {formatDate(relatorioData.data_geracao)}</>
                        )}
                    </div>
                    <div className="flex space-x-3">
                        <button
                            onClick={handleClose}
                            className="px-4 py-2 text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
                        >
                            Fechar
                        </button>
                        <button
                            onClick={() => window.print()}
                            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                        >
                            Imprimir
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default RelatorioCompletoModal;
