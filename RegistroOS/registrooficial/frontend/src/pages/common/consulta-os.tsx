import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../../services/api';
import Layout from '../../components/Layout';
import PesquisaPorOSTab from '../../features/desenvolvimento/components/tabs/PesquisaOSTab';
import RelatorioCompletoModal from '../../components/RelatorioCompletoModal';
import { useCachedSetores } from '../../hooks/useCachedSetores';

const ConsultaOsPage = () => {
    const navigate = useNavigate();
    const { setoresMotores, setoresTransformadores, loading: setoresLoading } = useCachedSetores();
    const [numos, setNumos] = useState('');
    const [loading, setLoading] = useState(false);
    const [osData, setOsData] = useState<any>(null);
    const [error, setError] = useState('');
    const [activeSubTab, setActiveSubTab] = useState<'consulta-dados' | 'pesquisa-por-os'>('consulta-dados');
    const [selectedSetorFiltro, setSelectedSetorFiltro] = useState<string>('');
    const [relatorioModalOpen, setRelatorioModalOpen] = useState(false);
    const [selectedOsId, setSelectedOsId] = useState<number | null>(null);

    const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const value = e.target.value;
        // Permite apenas números e limita a 5 caracteres
        const numericValue = value.replace(/\D/g, '').slice(0, 5);
        setNumos(numericValue);
    };

    const handleSearch = async (e: React.FormEvent) => {
        e.preventDefault();

        if (!numos.trim()) {
            setError('Por favor, digite o número da OS');
            return;
        }

        if (numos.length !== 5) {
            setError('O número da OS deve ter exatamente 5 dígitos');
            return;
        }

        setLoading(true);
        setError('');
        setOsData(null);

        try {
            // Primeiro tenta buscar no banco local
            const response = await api.get(`/os/${numos.trim()}`);
            setOsData(response.data);
        } catch (err: any) {
            if (err.response?.status === 404) {
                // Se não encontrou no banco, tenta o scraping
                console.log('OS não encontrada no banco, tentando scraping...');
                try {
                    const scrapingResponse = await api.post('/scraping/consulta-os', {
                        numero_os: numos.trim()
                    });

                    if (scrapingResponse.data.success && scrapingResponse.data.data.length > 0) {
                        // Converter dados do scraping para formato compatível
                        const scrapedData = scrapingResponse.data.data[0];
                        const formattedData = {
                            id: 0,
                            numero_os: scrapedData.OS || numos.trim(),
                            cliente: scrapedData.CLIENTE || scrapedData["NOME CLIENTE"] || "N/A",
                            tipo_maquina: scrapedData["TIPO DE MOTOR/GERADOR"] || scrapedData["TIPO DE TRANSFORMADOR"] || "N/A",
                            descricao_maquina: scrapedData.DESCRIÇÃO || "N/A",
                            status: scrapedData["STATUS DA OS"] || "CONSULTADO VIA SCRAPING",
                            data_inicio: null,
                            data_fechamento: null,
                            scraping_data: scrapedData // Dados completos do scraping
                        };
                        setOsData(formattedData);
                    } else {
                        setError(`OS ${numos} não encontrada nem no banco nem via scraping`);
                    }
                } catch (scrapingErr: any) {
                    console.error('Erro no scraping:', scrapingErr);
                    setError(`OS ${numos} não encontrada no banco. Erro ao tentar scraping: ${scrapingErr.response?.data?.detail || 'Erro desconhecido'}`);
                }
            } else if (err.response?.status === 401) {
                setError('Sessão expirada. Faça login novamente.');
                navigate('/login');
            } else {
                setError('Erro ao consultar OS. Tente novamente.');
            }
        } finally {
            setLoading(false);
        }
    };

    const formatDate = (dateStr: string) => {
        if (!dateStr) return 'N/A';
        try {
            const date = new Date(dateStr);
            return date.toLocaleDateString('pt-BR');
        } catch {
            return dateStr;
        }
    };

    const handleSetorFiltroChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
        setSelectedSetorFiltro(e.target.value);
    };

    const renderConsultaDadosContent = () => (
        <div>
            <div className="mb-6">
                <h1 className="text-2xl font-bold text-gray-800">Consulta de Ordem de Serviço</h1>
                <p className="text-gray-600">Digite o número da OS para consultar os dados completos</p>
            </div>

            <form onSubmit={handleSearch} className="mb-6">
                <div className="flex gap-4 items-end">
                    <div className="flex-1">
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                            Número da OS
                        </label>
                        <div className="relative">
                            <input
                                type="text"
                                value={numos}
                                onChange={handleInputChange}
                                placeholder="Ex: 20552"
                                className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                style={{ textTransform: 'uppercase' }}
                                disabled={loading}
                                maxLength={5}
                                pattern="[0-9]{5}"
                                title="Digite exatamente 5 números"
                            />
                            {loading && (
                                <div className="absolute right-3 top-1/2 transform -translate-y-1/2">
                                    <svg className="animate-spin h-5 w-5 text-blue-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                                    </svg>
                                </div>
                            )}
                        </div>
                    </div>
                    <button
                        type="submit"
                        disabled={loading || numos.length !== 5}
                        className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed font-medium flex items-center gap-2"
                    >
                        {loading && (
                            <svg className="animate-spin h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                            </svg>
                        )}
                        {loading ? 'Consultando...' : 'Consultar'}
                    </button>
                </div>
            </form>

            {error && (
                <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-md">
                    <div className="flex">
                        <div className="flex-shrink-0">
                            <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                            </svg>
                        </div>
                        <div className="ml-3">
                            <p className="text-sm text-red-700">{error}</p>
                        </div>
                    </div>
                </div>
            )}

            {osData && (
                <div className="space-y-6">
                    {/* Status da Consulta */}
                    <div className="bg-green-50 border border-green-200 rounded-md p-4">
                        <div className="flex items-center">
                            <svg className="h-5 w-5 text-green-400 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                            </svg>
                            <span className="text-sm font-medium text-green-800">{osData.message}</span>
                        </div>
                    </div>

                    {/* Dados da OS */}
                    {osData ? (
                        <div className="bg-white rounded-lg shadow-md p-6">
                            {/* Indicador de fonte dos dados */}
                            {osData.scraping_data && (
                                <div className="mb-4 p-3 bg-blue-50 border border-blue-200 rounded-md">
                                    <div className="flex items-center">
                                        <span className="text-blue-600 mr-2">🤖</span>
                                        <span className="text-blue-700 font-medium">
                                             Dados obtidos via web
                                        </span>
                                    </div>
                                </div>
                            )}

                            {/* Informações Básicas da OS */}
                            <div className="mb-8">
                                <h3 className="text-lg font-semibold text-gray-800 mb-4 flex items-center">
                                    <svg className="w-5 h-5 mr-2 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                                    </svg>
                                    Informações Básicas da OS
                                </h3>
                                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                                    <div className="bg-gray-50 p-3 rounded-md">
                                        <span className="text-xs font-medium text-gray-500 uppercase tracking-wide">Número da OS</span>
                                        <p className="text-lg font-bold text-blue-600 mt-1">{osData.numero_os || 'N/A'}</p>
                                    </div>
                                    <div className="bg-gray-50 p-3 rounded-md">
                                        <span className="text-xs font-medium text-gray-500 uppercase tracking-wide">Status</span>
                                        <p className="text-sm font-medium text-gray-900 mt-1">{osData.status || 'N/A'}</p>
                                    </div>
                                    <div className="bg-gray-50 p-3 rounded-md">
                                        <span className="text-xs font-medium text-gray-500 uppercase tracking-wide">Cliente</span>
                                        <p className="text-sm font-medium text-gray-900 mt-1">{osData.cliente || 'N/A'}</p>
                                    </div>
                                    <div className="bg-gray-50 p-3 rounded-md">
                                        <span className="text-xs font-medium text-gray-500 uppercase tracking-wide">Tipo de Máquina</span>
                                        <p className="text-sm font-medium text-gray-900 mt-1">{osData.tipo_maquina || 'N/A'}</p>
                                    </div>
                                    <div className="bg-gray-50 p-3 rounded-md">
                                        <span className="text-xs font-medium text-gray-500 uppercase tracking-wide">Descrição</span>
                                        <p className="text-sm font-medium text-gray-900 mt-1">{osData.descricao_maquina || 'N/A'}</p>
                                    </div>
                                    {osData.data_inicio && (
                                        <div className="bg-gray-50 p-3 rounded-md">
                                            <span className="text-xs font-medium text-gray-500 uppercase tracking-wide">Data Início</span>
                                            <p className="text-sm font-medium text-gray-900 mt-1">{formatDate(osData.data_inicio)}</p>
                                        </div>
                                    )}
                                </div>
                            </div>

                            {/* Dados detalhados do scraping */}
                            {osData.scraping_data && (
                                <div className="mb-8">
                                    <h3 className="text-lg font-semibold text-gray-800 mb-4 flex items-center">
                                        <span className="text-blue-600 mr-2">🔍</span>
                                        Dados Detalhados (Scraping)
                                    </h3>
                                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                                        {Object.entries(osData.scraping_data).map(([key, value]) => {
                                            if (value && String(value).trim() && key !== 'OS') {
                                                return (
                                                    <div key={key} className="bg-blue-50 p-3 rounded-md">
                                                        <span className="text-xs font-medium text-blue-600 uppercase tracking-wide">
                                                            {key.replace(/_/g, ' ')}
                                                        </span>
                                                        <p className="text-sm font-medium text-gray-900 mt-1">
                                                            {String(value)}
                                                        </p>
                                                    </div>
                                                );
                                            }
                                            return null;
                                        })}
                                    </div>
                                </div>
                            )}

                            {/* Informações Adicionais */}
                            {(osData.scraping_data?.CNPJ || osData.scraping_data?.["CODIGO DO CLIENTE"]) && (
                                <div className="mb-8">
                                    <h3 className="text-lg font-semibold text-gray-800 mb-4 flex items-center">
                                        <svg className="w-5 h-5 mr-2 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path>
                                        </svg>
                                        Informações do Cliente
                                    </h3>
                                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                        {osData.scraping_data?.CNPJ && (
                                            <div className="bg-green-50 p-4 rounded-md">
                                                <span className="text-xs font-medium text-gray-500 uppercase tracking-wide">CNPJ</span>
                                                <p className="text-base font-semibold text-gray-900 mt-1">{osData.scraping_data.CNPJ}</p>
                                            </div>
                                        )}
                                        {osData.scraping_data?.["CODIGO DO CLIENTE"] && (
                                            <div className="bg-green-50 p-4 rounded-md">
                                                <span className="text-xs font-medium text-gray-500 uppercase tracking-wide">Código do Cliente</span>
                                                <p className="text-base font-semibold text-gray-900 mt-1">{osData.scraping_data["CODIGO DO CLIENTE"]}</p>
                                            </div>
                                        )}
                                    </div>
                                </div>
                            )}

                            {/* Resumo dos Dados */}
                            <div className="mt-8 p-4 bg-blue-50 border border-blue-200 rounded-md">
                                <h4 className="text-sm font-medium text-blue-800 mb-2">
                                    Resumo dos Dados da OS {osData.numero_os}
                                </h4>
                                <div className="text-xs text-blue-700">
                                    <p>✅ <strong>Cliente:</strong> {osData.cliente || 'Não informado'}</p>
                                    <p>✅ <strong>Status:</strong> {osData.status || 'Não informado'}</p>
                                    <p>✅ <strong>Tipo:</strong> {osData.tipo_maquina || 'Não informado'}</p>
                                    {osData.scraping_data && (
                                        <p>🤖 <strong>Fonte:</strong>  Dados obtidos via web</p>
                                    )}
                                </div>
                            </div>
                        </div>
                    ) : (
                        <div className="text-center py-8">
                            <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9.172 16.172a4 4 0 015.656 0M9 12h6m-6-4h6m2 5.291A7.962 7.962 0 0112 15c-2.34 0-4.29-1.009-5.625-2.581"></path>
                            </svg>
                            <p className="mt-2 text-sm text-gray-500">Nenhum dado encontrado para esta OS.</p>
                        </div>
                    )}
                </div>
            )}

            {!osData && !error && !loading && (
                <div className="text-center py-12">
                    <svg className="mx-auto h-16 w-16 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
                    </svg>
                    <h3 className="mt-4 text-lg font-medium text-gray-900">Consulta de OS</h3>
                    <p className="mt-2 text-sm text-gray-500">Digite o número da OS acima para visualizar os dados completos</p>
                </div>
            )}
        </div>
    );

    return (
        <Layout>
            <div className="bg-white rounded-lg shadow-md p-6">
                {/* Sub-tabs Navigation */}
                <div className="border-b border-gray-200 mb-6">
                    <nav className="flex space-x-4">
                        <button
                            onClick={() => setActiveSubTab('consulta-dados')}
                            className={`py-4 px-1 border-b-2 font-medium text-sm ${
                                activeSubTab === 'consulta-dados'
                                    ? 'border-blue-500 text-blue-600'
                                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                            }`}
                        >
                            📊 Consulta Dados
                        </button>
                        <button
                            onClick={() => setActiveSubTab('pesquisa-por-os')}
                            className={`py-4 px-1 border-b-2 font-medium text-sm ${
                                activeSubTab === 'pesquisa-por-os'
                                    ? 'border-blue-500 text-blue-600'
                                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                            }`}
                        >
                            🔍 Pesquisa Por OS
                        </button>
                    </nav>
                </div>

                {/* Sub-tab Content */}
                <div>
                    {activeSubTab === 'consulta-dados' && renderConsultaDadosContent()}
                    {activeSubTab === 'pesquisa-por-os' && (
                        <div>
                            <div className="flex justify-between items-center mb-4">
                                <h2 className="text-lg font-semibold">Pesquisa de OS</h2>
                                <div>
                                    <label htmlFor="setorFiltroConsulta" className="block text-sm font-medium text-gray-700">Filtrar por Setor</label>
                                    <select
                                        id="setorFiltroConsulta"
                                        value={selectedSetorFiltro}
                                        onChange={handleSetorFiltroChange}
                                        className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm rounded-md"
                                    >
                                        <option value="">Todos os Setores</option>
                                        {[...new Set([...setoresMotores.map(s => s.nome), ...setoresTransformadores.map(s => s.nome)])].map((nomeSetor: string, index: number) => (
                                            <option key={`setor-${index}-${nomeSetor}`} value={nomeSetor}>{nomeSetor}</option>
                                        ))}
                                    </select>
                                </div>
                            </div>
                            <PesquisaPorOSTab
                                setorFiltro={selectedSetorFiltro}
                                onVerOS={(osId: number) => {
                                    setSelectedOsId(osId);
                                    setRelatorioModalOpen(true);
                                }}
                            />
                        </div>
                    )}
                </div>
            </div>

            {/* Modal de Relatório Completo */}
            <RelatorioCompletoModal
                isOpen={relatorioModalOpen}
                onClose={() => {
                    setRelatorioModalOpen(false);
                    setSelectedOsId(null);
                }}
                osId={selectedOsId || 0}
                origemPagina="consulta"
            />
        </Layout>
    );
};

export default ConsultaOsPage;
