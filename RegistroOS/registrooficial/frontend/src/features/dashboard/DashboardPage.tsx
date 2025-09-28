import React, { useState, useEffect } from 'react';
import Layout from '../../components/Layout';
import api from '../../services/api';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, BarChart, Bar, PieChart, Pie, Cell } from 'recharts';

const DashboardPage: React.FC = () => {
const [dashboardData, setDashboardData] = useState<any>({
    geral: {
        totalApontamentos: 0,
        totalHoras: 0,
        horasExtras: 0,
        retrabalhos: 0,
        osUnicas: 0
    },
    departamentos: [] as any[],
    setores: [] as any[],
    programacoes: {
        total: 0,
        enviadas: 0,
        emAndamento: 0,
        concluidas: 0,
        recentes: [] as any[]
    },
    pendencias: {
        total: 0,
        abertas: 0,
        fechadas: 0,
        recentes: [] as any[]
    },
    performanceDepartamentos: [] as any[],
    topSetores: [] as any[],
    apontamentosRecentes: [] as any[]
});

    const [filtros, setFiltros] = useState({
        departamentoSelecionado: '',
        setorSelecionado: '',
        periodo: '6meses'
    });

    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [setoresDisponiveis, setSetoresDisponiveis] = useState<any[]>([]);
    const [departamentosDisponiveis, setDepartamentosDisponiveis] = useState<any[]>([]);
    const [dadosOriginais, setDadosOriginais] = useState<any>({
        apontamentos: [],
        programacoes: [],
        pendencias: []
    });

    useEffect(() => {
        const fetchDashboardData = async () => {
            try {
                setLoading(true);
                console.log('Buscando dados do dashboard...');

                // Buscar dados de forma sequencial para melhor debugging
                console.log('Buscando apontamentos...');
                const apontamentosResponse = await api.get('/apontamentos-detalhados');
                console.log('Apontamentos:', apontamentosResponse.data?.length || 0);

                console.log('Buscando programações...');
                const programacoesResponse = await api.get('/pcp/programacoes');
                console.log('Programações:', programacoesResponse.data?.length || 0);

                console.log('Buscando pendências...');
                const pendenciasResponse = await api.get('/pcp/pendencias');
                console.log('Pendências:', pendenciasResponse.data?.length || 0);

                console.log('Buscando departamentos...');
                const departamentosResponse = await api.get('/departamentos');
                console.log('Departamentos:', departamentosResponse.data?.length || 0);

                console.log('Buscando setores...');
                const setoresResponse = await api.get('/setores');
                console.log('Setores:', setoresResponse.data?.length || 0);

                const apontamentos = Array.isArray(apontamentosResponse.data) ? apontamentosResponse.data : [];
                const programacoes = Array.isArray(programacoesResponse.data) ? programacoesResponse.data : [];
                const pendencias = Array.isArray(pendenciasResponse.data) ? pendenciasResponse.data : [];

                console.log('Total de apontamentos:', apontamentos.length);
                console.log('Total de programações:', programacoes.length);
                console.log('Total de pendências:', pendencias.length);

                const departamentos = Array.isArray(departamentosResponse.data) ? departamentosResponse.data : [];
                const setores = Array.isArray(setoresResponse.data) ? setoresResponse.data : [];

                console.log('Departamentos brutos:', departamentos);
                console.log('Setores brutos:', setores);

                setDepartamentosDisponiveis(departamentos);
                setSetoresDisponiveis(setores);

                // Armazenar dados originais para reprocessamento com filtros
                setDadosOriginais({
                    apontamentos,
                    programacoes,
                    pendencias
                });

                console.log('Departamentos encontrados:', departamentos.length);
                console.log('Setores encontrados:', setores.length);

                // Log dos primeiros apontamentos para verificar estrutura
                if (apontamentos.length > 0) {
                    console.log('Estrutura do primeiro apontamento:', apontamentos[0]);
                    console.log('Departamentos únicos nos apontamentos:', [...new Set(apontamentos.map((a: any) => a.departamento))]);
                    console.log('Setores únicos nos apontamentos:', [...new Set(apontamentos.map((a: any) => a.setor))]);
                }

                // Função para processar dados de forma escalável
                const processarDadosEscalaveis = (apontamentos: any[], programacoes: any[], pendencias: any[]) => {
                    console.log('Processando dados de forma escalável...');

                    // 1. MÉTRICAS GERAIS
                    const totalHoras = apontamentos.reduce((total, a) => total + parseFloat(a.tempo_trabalhado || 0), 0);
                    const horasExtras = apontamentos
                        .filter(a => a.horas_extras && a.horas_extras > 0)
                        .reduce((total, a) => total + parseFloat(a.horas_extras || 0), 0);
                    const retrabalhos = apontamentos.filter(a =>
                        a.foi_retrabalho === true ||
                        a.descricao_atividade?.toLowerCase().includes('retrabalho')
                    ).length;
                    const osUnicas = new Set(apontamentos.map(a => a.numero_os)).size;

                    // 1.1. MÉTRICAS DE PROGRAMAÇÕES
                    const totalProgramacoes = programacoes.length;
                    const programacoesEnviadas = programacoes.filter(p => p.status === 'ENVIADA').length;
                    const programacoesEmAndamento = programacoes.filter(p => p.status === 'EM_ANDAMENTO').length;
                    const programacoesConcluidas = programacoes.filter(p => p.status === 'CONCLUIDA').length;

                    // 1.2. MÉTRICAS DE PENDÊNCIAS
                    const totalPendencias = pendencias.length;
                    const pendenciasAbertas = pendencias.filter(p => p.status === 'ABERTA').length;
                    const pendenciasFechadas = pendencias.filter(p => p.status === 'FECHADA').length;

                    // 2. AGRUPAMENTO POR DEPARTAMENTO
                    const apontamentosPorDepartamento = apontamentos.reduce((acc, a) => {
                        const dept = a.departamento || 'SEM_DEPARTAMENTO';
                        if (!acc[dept]) acc[dept] = [];
                        acc[dept].push(a);
                        return acc;
                    }, {});

                    const departamentosData = Object.entries(apontamentosPorDepartamento).map(([nome, apts]) => {
                        const aptsArray = apts as any[];
                        const horasDept = aptsArray.reduce((total, a) => total + parseFloat(a.tempo_trabalhado || 0), 0);
                        const horasExtrasDept = aptsArray.filter(a => a.horas_extras && a.horas_extras > 0)
                            .reduce((total, a) => total + parseFloat(a.horas_extras || 0), 0);
                        const retrabalhosDept = aptsArray.filter(a => a.foi_retrabalho === true).length;
                        const osUnicasDept = new Set(aptsArray.map(a => a.numero_os)).size;

                        return {
                            nome,
                            totalHoras: Math.round(horasDept),
                            horasExtras: Math.round(horasExtrasDept),
                            retrabalhos: retrabalhosDept,
                            osUnicas: osUnicasDept,
                            apontamentos: aptsArray.length,
                            percentualHoras: totalHoras > 0 ? Math.round((horasDept / totalHoras) * 100) : 0
                        };
                    }).sort((a, b) => b.totalHoras - a.totalHoras);

                    // 3. AGRUPAMENTO POR SETOR (TOP 10 para evitar sobrecarga)
                    const apontamentosPorSetor = apontamentos.reduce((acc, a) => {
                        const setor = a.setor || 'SEM_SETOR';
                        if (!acc[setor]) acc[setor] = [];
                        acc[setor].push(a);
                        return acc;
                    }, {});

                    const setoresData = Object.entries(apontamentosPorSetor).map(([nome, apts]) => {
                        const aptsArray = apts as any[];
                        const horasSetor = aptsArray.reduce((total: number, a: any) => total + parseFloat(a.tempo_trabalhado || 0), 0);
                        const departamento = aptsArray[0]?.departamento || 'SEM_DEPARTAMENTO';

                        return {
                            nome,
                            departamento,
                            totalHoras: Math.round(horasSetor),
                            apontamentos: aptsArray.length,
                            osUnicas: new Set(aptsArray.map((a: any) => a.numero_os)).size,
                            percentualHoras: totalHoras > 0 ? Math.round((horasSetor / totalHoras) * 100) : 0
                        };
                    }).sort((a, b) => b.totalHoras - a.totalHoras).slice(0, 10); // TOP 10 setores

                    return {
                        geral: {
                            totalApontamentos: apontamentos.length,
                            totalHoras: Math.round(totalHoras),
                            horasExtras: Math.round(horasExtras),
                            retrabalhos,
                            osUnicas
                        },
                        programacoes: {
                            total: totalProgramacoes,
                            enviadas: programacoesEnviadas,
                            emAndamento: programacoesEmAndamento,
                            concluidas: programacoesConcluidas,
                            recentes: programacoes.slice(0, 5).map(p => ({
                                id: p.id,
                                os_numero: p.os_numero || 'N/A',
                                status: p.status || 'N/A',
                                responsavel: p.responsavel_nome || 'N/A',
                                setor: p.setor_nome || 'N/A'
                            }))
                        },
                        pendencias: {
                            total: totalPendencias,
                            abertas: pendenciasAbertas,
                            fechadas: pendenciasFechadas,
                            recentes: pendencias.slice(0, 5).map(p => ({
                                id: p.id,
                                descricao: p.descricao || 'N/A',
                                status: p.status || 'ABERTA',
                                numero_os: p.numero_os || 'N/A',
                                responsavel: p.responsavel_nome || 'N/A'
                            }))
                        },
                        departamentos: departamentosData,
                        topSetores: setoresData,
                        apontamentosRecentes: apontamentos.slice(0, 10).map(a => ({
                            numero_os: a.numero_os || 'N/A',
                            cliente: a.cliente || 'Cliente não informado',
                            setor: a.setor || 'N/A',
                            departamento: a.departamento || 'N/A',
                            status: a.status_apontamento || 'FINALIZADO',
                            horas: parseFloat(a.tempo_trabalhado || 0)
                        }))
                    };
                };

                // Função para gerar performance por departamento (mais escalável)
                const gerarPerformanceDepartamentos = (apontamentos: any[], departamentosData: any[]) => {
                    const hoje = new Date();
                    const meses = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun'];

                    return meses.map((mes, index) => {
                        const mesAtual = hoje.getMonth();
                        const anoAtual = hoje.getFullYear();
                        const mesCalculado = mesAtual - (5 - index);

                        const dataInicio = new Date(anoAtual, mesCalculado, 1);
                        const dataFim = new Date(anoAtual, mesCalculado + 1, 0);

                        const dadosMes: any = { mes };

                        // Para cada departamento, calcular horas do mês
                        departamentosData.forEach(dept => {
                            const apontamentosDept = apontamentos.filter(a =>
                                a.departamento === dept.nome
                            );

                            const apontamentosMes = apontamentosDept.filter(a => {
                                const dataApontamento = new Date(a.data_hora_inicio);
                                return dataApontamento >= dataInicio && dataApontamento <= dataFim;
                            });

                            const horasMes = apontamentosMes.reduce((total, a) =>
                                total + parseFloat(a.tempo_trabalhado || 0), 0
                            );

                            dadosMes[dept.nome] = Math.round(horasMes);
                        });

                        return dadosMes;
                    });
                };

                // Função para filtrar dados por filtros selecionados
                const aplicarFiltros = (apontamentos: any[]) => {
                    let apontamentosFiltrados = [...apontamentos];

                    if (filtros.departamentoSelecionado) {
                        apontamentosFiltrados = apontamentosFiltrados.filter(a =>
                            a.departamento === filtros.departamentoSelecionado
                        );
                    }

                    if (filtros.setorSelecionado) {
                        apontamentosFiltrados = apontamentosFiltrados.filter(a =>
                            a.setor === filtros.setorSelecionado
                        );
                    }

                    return apontamentosFiltrados;
                };

                // Aplicar filtros aos apontamentos
                const apontamentosFiltrados = aplicarFiltros(apontamentos);

                // Processar dados de forma escalável
                const dadosProcessados = processarDadosEscalaveis(apontamentosFiltrados, programacoes, pendencias);

                // Gerar performance por departamento
                const performanceDepartamentos = gerarPerformanceDepartamentos(apontamentosFiltrados, dadosProcessados.departamentos);

                console.log('Dados processados:', {
                    geral: dadosProcessados.geral,
                    departamentos: dadosProcessados.departamentos.length,
                    topSetores: dadosProcessados.topSetores.length
                });

                // Atualizar estado com dados escaláveis
                setDashboardData({
                    ...dadosProcessados,
                    performanceDepartamentos
                });

            } catch (err: any) {
                console.error('Erro ao carregar dados do dashboard:', err);

                // Log detalhado do erro
                if (err?.response) {
                    console.error('Status:', err.response.status);
                    console.error('Data:', err.response.data);
                    setError(`Erro ${err.response.status}: ${err.response.data?.detail || 'Erro no servidor'}`);
                } else if (err?.request) {
                    console.error('Erro de rede:', err.request);
                    setError('Erro de conexão com o servidor');
                } else {
                    console.error('Erro:', err?.message);
                    setError(err?.message || 'Erro desconhecido');
                }

                // Manter dados padrão em caso de erro
                setDashboardData({
                    geral: {
                        totalApontamentos: 0,
                        totalHoras: 0,
                        horasExtras: 0,
                        retrabalhos: 0,
                        osUnicas: 0
                    },
                    programacoes: {
                        total: 0,
                        enviadas: 0,
                        emAndamento: 0,
                        concluidas: 0,
                        recentes: []
                    },
                    pendencias: {
                        total: 0,
                        abertas: 0,
                        fechadas: 0,
                        recentes: []
                    },
                    departamentos: [],
                    setores: [],
                    performanceDepartamentos: [],
                    topSetores: [],
                    apontamentosRecentes: []
                });
            } finally {
                setLoading(false);
                console.log('Carregamento do dashboard finalizado');
            }
        };

        fetchDashboardData();
    }, []); // Carregar dados apenas uma vez

    // useEffect separado para reprocessar dados quando filtros mudarem
    useEffect(() => {
        console.log('useEffect de filtros executado!');
        console.log('Dados originais disponíveis:', dadosOriginais.apontamentos.length);
        console.log('Filtros atuais:', filtros);

        if (dadosOriginais.apontamentos.length > 0) {
            console.log('Reprocessando dados com novos filtros...');

            // Função para aplicar filtros
            const aplicarFiltros = (apontamentos: any[]) => {
                let apontamentosFiltrados = [...apontamentos];

                console.log('Apontamentos antes do filtro:', apontamentosFiltrados.length);

                if (filtros.departamentoSelecionado) {
                    console.log('Filtrando por departamento:', filtros.departamentoSelecionado);
                    apontamentosFiltrados = apontamentosFiltrados.filter(a => {
                        console.log('Comparando:', a.departamento, '===', filtros.departamentoSelecionado);
                        return a.departamento === filtros.departamentoSelecionado;
                    });
                    console.log('Após filtro departamento:', apontamentosFiltrados.length);
                }

                if (filtros.setorSelecionado) {
                    console.log('Filtrando por setor:', filtros.setorSelecionado);
                    apontamentosFiltrados = apontamentosFiltrados.filter(a => {
                        console.log('Comparando:', a.setor, '===', filtros.setorSelecionado);
                        return a.setor === filtros.setorSelecionado;
                    });
                    console.log('Após filtro setor:', apontamentosFiltrados.length);
                }

                console.log('Apontamentos após todos os filtros:', apontamentosFiltrados.length);
                return apontamentosFiltrados;
            };

            // Aplicar filtros aos dados originais
            const apontamentosFiltrados = aplicarFiltros(dadosOriginais.apontamentos);

            console.log('Filtros aplicados:', filtros);
            console.log('Apontamentos antes do filtro:', dadosOriginais.apontamentos.length);
            console.log('Apontamentos após filtro:', apontamentosFiltrados.length);

            // Reprocessar dados com filtros aplicados
            const processarDadosEscalaveis = (apontamentos: any[], programacoes: any[], pendencias: any[]) => {
                console.log('Processando dados de forma escalável...');

                // Calcular totais gerais
                const totalHoras = apontamentos.reduce((total: number, a: any) => total + parseFloat(a.tempo_trabalhado || 0), 0);
                const horasExtras = apontamentos.filter((a: any) => a.horas_extras && a.horas_extras > 0)
                    .reduce((total: number, a: any) => total + parseFloat(a.horas_extras || 0), 0);
                const retrabalhos = apontamentos.filter((a: any) => a.foi_retrabalho === true).length;
                const osUnicas = new Set(apontamentos.map((a: any) => a.numero_os)).size;

                // Agrupar por departamento
                const apontamentosPorDepartamento = apontamentos.reduce((acc: any, a: any) => {
                    const dept = a.departamento || 'SEM_DEPARTAMENTO';
                    if (!acc[dept]) acc[dept] = [];
                    acc[dept].push(a);
                    return acc;
                }, {});

                const departamentosData = Object.entries(apontamentosPorDepartamento).map(([nome, apts]) => {
                    const aptsArray = apts as any[];
                    const horasDept = aptsArray.reduce((total: number, a: any) => total + parseFloat(a.tempo_trabalhado || 0), 0);
                    const horasExtrasDept = aptsArray.filter((a: any) => a.horas_extras && a.horas_extras > 0)
                        .reduce((total: number, a: any) => total + parseFloat(a.horas_extras || 0), 0);
                    const retrabalhosDept = aptsArray.filter((a: any) => a.foi_retrabalho === true).length;
                    const osUnicasDept = new Set(aptsArray.map((a: any) => a.numero_os)).size;

                    return {
                        nome,
                        totalHoras: Math.round(horasDept),
                        horasExtras: Math.round(horasExtrasDept),
                        retrabalhos: retrabalhosDept,
                        osUnicas: osUnicasDept,
                        apontamentos: aptsArray.length,
                        percentualHoras: totalHoras > 0 ? Math.round((horasDept / totalHoras) * 100) : 0
                    };
                }).sort((a, b) => b.totalHoras - a.totalHoras);

                // Agrupar por setor
                const apontamentosPorSetor = apontamentos.reduce((acc: any, a: any) => {
                    const setor = a.setor || 'SEM_SETOR';
                    if (!acc[setor]) acc[setor] = [];
                    acc[setor].push(a);
                    return acc;
                }, {});

                const setoresData = Object.entries(apontamentosPorSetor).map(([nome, apts]) => {
                    const aptsArray = apts as any[];
                    const horasSetor = aptsArray.reduce((total: number, a: any) => total + parseFloat(a.tempo_trabalhado || 0), 0);
                    const departamento = aptsArray[0]?.departamento || 'SEM_DEPARTAMENTO';

                    return {
                        nome,
                        departamento,
                        totalHoras: Math.round(horasSetor),
                        apontamentos: aptsArray.length,
                        osUnicas: new Set(aptsArray.map((a: any) => a.numero_os)).size,
                        percentualHoras: totalHoras > 0 ? Math.round((horasSetor / totalHoras) * 100) : 0
                    };
                }).sort((a, b) => b.totalHoras - a.totalHoras).slice(0, 10); // TOP 10 setores

                return {
                    geral: {
                        totalApontamentos: apontamentos.length,
                        totalHoras: Math.round(totalHoras),
                        horasExtras: Math.round(horasExtras),
                        retrabalhos,
                        osUnicas
                    },
                    departamentos: departamentosData,
                    topSetores: setoresData,
                    apontamentosRecentes: apontamentos.slice(-3).reverse(),
                    programacoes: {
                        total: programacoes.length,
                        enviadas: programacoes.filter((p: any) => p.status === 'ENVIADA').length,
                        emAndamento: programacoes.filter((p: any) => p.status === 'EM_ANDAMENTO').length,
                        concluidas: programacoes.filter((p: any) => p.status === 'CONCLUIDA').length,
                        recentes: programacoes.slice(-3).reverse()
                    },
                    pendencias: {
                        total: pendencias.length,
                        abertas: pendencias.filter((p: any) => p.status === 'ABERTA').length,
                        fechadas: pendencias.filter((p: any) => p.status === 'FECHADA').length,
                        recentes: pendencias.slice(-3).reverse()
                    }
                };
            };

            const dadosProcessados = processarDadosEscalaveis(apontamentosFiltrados, dadosOriginais.programacoes, dadosOriginais.pendencias);

            // Atualizar estado com dados filtrados
            setDashboardData({
                ...dadosProcessados,
                performanceDepartamentos: dadosProcessados.departamentos
            });
        }
    }, [filtros, dadosOriginais]); // Reprocessar quando filtros ou dados originais mudarem

    // Componente de filtros - COMPACTO
    const FiltrosComponent: React.FC = () => (
        <div className="bg-white p-3 rounded-lg border border-gray-200">
            <div className="flex items-center space-x-4">
                <h3 className="text-sm font-semibold text-gray-700">Filtros:</h3>
                <div className="flex items-center space-x-2">
                    <label className="text-xs font-medium text-gray-600">Departamento:</label>
                    <select
                        value={filtros.departamentoSelecionado}
                        onChange={(e) => setFiltros(prev => ({ ...prev, departamentoSelecionado: e.target.value }))}
                        className="px-2 py-1 text-xs border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500"
                    >
                        <option value="">Todos</option>
                        {departamentosDisponiveis.map((dept: any) => (
                            <option key={dept.id} value={dept.nome_tipo || dept.nome}>
                                {dept.nome_tipo || dept.nome}
                            </option>
                        ))}
                    </select>
                </div>
                <div className="flex items-center space-x-2">
                    <label className="text-xs font-medium text-gray-600">Setor:</label>
                    <select
                        value={filtros.setorSelecionado}
                        onChange={(e) => setFiltros(prev => ({ ...prev, setorSelecionado: e.target.value }))}
                        className="px-2 py-1 text-xs border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500"
                    >
                        <option value="">Todos</option>
                        {setoresDisponiveis
                            .filter((setor: any) => !filtros.departamentoSelecionado || setor.departamento === filtros.departamentoSelecionado)
                            .map((setor: any) => (
                                <option key={setor.id} value={setor.nome}>
                                    {setor.nome}
                                </option>
                            ))}
                    </select>
                </div>
                <div className="flex items-center space-x-2">
                    <label className="text-xs font-medium text-gray-600">Período:</label>
                    <select
                        value={filtros.periodo}
                        onChange={(e) => setFiltros(prev => ({ ...prev, periodo: e.target.value }))}
                        className="px-2 py-1 text-xs border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500"
                    >
                        <option value="6meses">6 meses</option>
                        <option value="3meses">3 meses</option>
                        <option value="1mes">1 mês</option>
                    </select>
                </div>
            </div>
        </div>
    );

    // Componente de métricas gerais - COMPACTO
    const MetricasGeraisComponent: React.FC = () => (
        <div className="grid grid-cols-5 gap-3">
            <div className="bg-gray-50 p-3 rounded-lg border border-gray-200 text-center">
                <p className="text-xs text-gray-700 font-medium">Apontamentos</p>
                <p className="text-lg font-bold text-gray-900">
                    {loading ? '...' : dashboardData.geral.totalApontamentos.toLocaleString()}
                </p>
            </div>
            <div className="bg-gray-50 p-3 rounded-lg border border-gray-200 text-center">
                <p className="text-xs text-gray-700 font-medium">Horas</p>
                <p className="text-lg font-bold text-gray-900">
                    {loading ? '...' : `${dashboardData.geral.totalHoras.toLocaleString()}h`}
                </p>
            </div>
            <div className="bg-gray-50 p-3 rounded-lg border border-gray-200 text-center">
                <p className="text-xs text-gray-700 font-medium">H. Extras</p>
                <p className="text-lg font-bold text-gray-900">
                    {loading ? '...' : `${dashboardData.geral.horasExtras.toLocaleString()}h`}
                </p>
            </div>
            <div className="bg-gray-50 p-3 rounded-lg border border-gray-200 text-center">
                <p className="text-xs text-gray-700 font-medium">Retrabalhos</p>
                <p className="text-lg font-bold text-gray-900">
                    {loading ? '...' : dashboardData.geral.retrabalhos.toLocaleString()}
                </p>
            </div>
            <div className="bg-gray-50 p-3 rounded-lg border border-gray-200 text-center">
                <p className="text-xs text-gray-700 font-medium">OS Únicas</p>
                <p className="text-lg font-bold text-gray-900">
                    {loading ? '...' : dashboardData.geral.osUnicas.toLocaleString()}
                </p>
            </div>
        </div>
    );

    // Componente de métricas de programações - COMPACTO
    const ProgramacoesComponent: React.FC = () => (
        <div className="bg-white p-3 rounded border border-gray-200">
            <h3 className="text-sm font-semibold mb-2">Programações</h3>
            <div className="grid grid-cols-4 gap-2 mb-2">
                <div className="text-center">
                    <p className="text-xs text-gray-600">Total</p>
                    <p className="text-sm font-bold text-gray-700">
                        {loading ? '...' : dashboardData.programacoes?.total || 0}
                    </p>
                </div>
                <div className="text-center">
                    <p className="text-xs text-gray-600">Enviadas</p>
                    <p className="text-sm font-bold text-gray-700">
                        {loading ? '...' : dashboardData.programacoes?.enviadas || 0}
                    </p>
                </div>
                <div className="text-center">
                    <p className="text-xs text-gray-600">Andamento</p>
                    <p className="text-sm font-bold text-gray-700">
                        {loading ? '...' : dashboardData.programacoes?.emAndamento || 0}
                    </p>
                </div>
                <div className="text-center">
                    <p className="text-xs text-gray-600">Concluídas</p>
                    <p className="text-sm font-bold text-gray-700">
                        {loading ? '...' : dashboardData.programacoes?.concluidas || 0}
                    </p>
                </div>
            </div>
            {dashboardData.programacoes?.recentes && dashboardData.programacoes.recentes.length > 0 && (
                <div className="max-h-16 overflow-y-auto">
                    {dashboardData.programacoes.recentes.slice(0, 2).map((prog: any, index: number) => (
                        <div key={index} className="text-xs bg-gray-50 p-1 rounded mb-1">
                            <span className="font-medium">OS {prog.os_numero}</span> -
                            <span className={`ml-1 px-1 rounded text-xs ${
                                prog.status === 'CONCLUIDA' ? 'bg-green-100 text-green-800' :
                                prog.status === 'EM_ANDAMENTO' ? 'bg-yellow-100 text-yellow-800' :
                                'bg-gray-100 text-gray-800'
                            }`}>
                                {prog.status}
                            </span>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );

    // Componente de métricas de pendências - COMPACTO
    const PendenciasComponent: React.FC = () => (
        <div className="bg-white p-3 rounded border border-gray-200">
            <h3 className="text-sm font-semibold mb-2">Pendências</h3>
            <div className="grid grid-cols-3 gap-2 mb-2">
                <div className="text-center">
                    <p className="text-xs text-gray-600">Total</p>
                    <p className="text-sm font-bold text-gray-700">
                        {loading ? '...' : dashboardData.pendencias?.total || 0}
                    </p>
                </div>
                <div className="text-center">
                    <p className="text-xs text-gray-600">Abertas</p>
                    <p className="text-sm font-bold text-gray-700">
                        {loading ? '...' : dashboardData.pendencias?.abertas || 0}
                    </p>
                </div>
                <div className="text-center">
                    <p className="text-xs text-gray-600">Fechadas</p>
                    <p className="text-sm font-bold text-gray-700">
                        {loading ? '...' : dashboardData.pendencias?.fechadas || 0}
                    </p>
                </div>
            </div>
            {dashboardData.pendencias?.recentes && dashboardData.pendencias.recentes.length > 0 && (
                <div className="max-h-16 overflow-y-auto">
                    {dashboardData.pendencias.recentes.slice(0, 2).map((pend: any, index: number) => (
                        <div key={index} className="text-xs bg-gray-50 p-1 rounded mb-1">
                            <span className="font-medium">OS {pend.numero_os}</span> -
                            <span className={`ml-1 px-1 rounded text-xs ${
                                pend.status === 'FECHADA' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                            }`}>
                                {pend.status}
                            </span>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );

    // Componente de gráfico de performance por departamento
    const PerformanceDepartamentosComponent: React.FC = () => {
        const colors = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6'];

        return (
            <div className="bg-white p-4 rounded-lg border border-gray-200">
                <h3 className="text-sm font-semibold text-gray-700 mb-3">Performance Departamentos (6m)</h3>
                <div className="h-32">
                    <ResponsiveContainer width="100%" height="100%">
                        <LineChart data={dashboardData.performanceDepartamentos}>
                            <CartesianGrid strokeDasharray="3 3" />
                            <XAxis dataKey="mes" tick={{ fontSize: 10 }} />
                            <YAxis tick={{ fontSize: 10 }} />
                            <Tooltip formatter={(value, name) => [`${value}h`, name]} />
                            <Legend wrapperStyle={{ fontSize: 9 }} />
                            {(dashboardData.departamentos || []).slice(0, 3).map((dept: any, index: number) => (
                                <Line
                                    key={dept.nome || `dept-${index}`}
                                    type="monotone"
                                    dataKey={dept.nome}
                                    stroke={colors[index % colors.length]}
                                    strokeWidth={2}
                                    dot={{ r: 3 }}
                                    activeDot={{ r: 6 }}
                                />
                            ))}
                        </LineChart>
                    </ResponsiveContainer>
                </div>
            </div>
        );
    };

    // Componente de gráfico de pizza para departamentos
    const DepartamentosPieComponent: React.FC = () => {
        const colors = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#06B6D4'];

        return (
            <div className="bg-white p-3 rounded border border-gray-200">
                <h3 className="text-sm font-semibold mb-2">Distribuição Horas</h3>
                <div className="h-32">
                    <ResponsiveContainer width="100%" height="100%">
                        <PieChart>
                            <Pie
                                data={(dashboardData.departamentos || []).slice(0, 4)}
                                dataKey="totalHoras"
                                nameKey="nome"
                                cx="50%"
                                cy="50%"
                                outerRadius={50}
                                label={({ percentualHoras }: any) => `${percentualHoras || 0}%`}
                            >
                                {(dashboardData.departamentos || []).slice(0, 4).map((_: any, index: number) => (
                                    <Cell key={`cell-${index}`} fill={colors[index % colors.length]} />
                                ))}
                            </Pie>
                            <Tooltip formatter={(value) => [`${value}h`, 'Horas']} />
                        </PieChart>
                    </ResponsiveContainer>
                </div>
            </div>
        );
    };

    // Componente de top setores - COMPACTO
    const TopSetoresComponent: React.FC = () => (
        <div className="bg-white p-3 rounded border border-gray-200">
            <h3 className="text-sm font-semibold mb-2">Top 5 Setores</h3>
            <div className="h-32">
                <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={dashboardData.topSetores.slice(0, 5)} layout="horizontal">
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis type="number" tick={{ fontSize: 10 }} />
                        <YAxis dataKey="nome" type="category" width={80} tick={{ fontSize: 10 }} />
                        <Tooltip formatter={(value) => [`${value}h`, 'Horas']} />
                        <Bar dataKey="totalHoras" fill="#3B82F6" />
                    </BarChart>
                </ResponsiveContainer>
            </div>
        </div>
    );

    if (loading) {
        return (
            <Layout>
                <div className="flex items-center justify-center h-64">
                    <div className="text-center">
                        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-gray-600 mx-auto"></div>
                        <p className="mt-4 text-gray-600">Carregando dashboard...</p>
                    </div>
                </div>
            </Layout>
        );
    }

    if (error) {
        return (
            <Layout>
                <div className="flex items-center justify-center h-64">
                    <div className="text-center">
                        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
                            <h3 className="font-bold">Erro ao carregar Dashboard</h3>
                            <p className="mt-2">{error}</p>
                            <button
                                onClick={() => window.location.reload()}
                                className="mt-4 bg-red-500 hover:bg-red-700 text-white font-bold py-2 px-4 rounded"
                            >
                                Tentar Novamente
                            </button>
                        </div>
                    </div>
                </div>
            </Layout>
        );
    }

    return (
        <Layout>
            <div className="h-screen bg-gray-100 p-3 overflow-hidden">
                <div className="w-full h-full flex flex-col space-y-3">
                    {/* HEADER COMPACTO */}
                    <div className="bg-white rounded-lg border border-gray-200 p-3 flex-shrink-0">
                        <div className="flex justify-between items-center">
                            <div>
                                <h1 className="text-xl font-semibold text-gray-800">Dashboard RegistroOS</h1>
                                <p className="text-sm text-gray-600">Visão geral do sistema</p>
                            </div>
                            <div className="text-right">
                                <p className="text-xs text-gray-500">Última atualização</p>
                                <p className="text-sm font-medium text-gray-800">{new Date().toLocaleTimeString()}</p>
                            </div>
                        </div>
                    </div>

                    {/* FILTROS COMPACTOS */}
                    <div className="flex-shrink-0">
                        <FiltrosComponent />
                    </div>

                    {/* MÉTRICAS PRINCIPAIS E APONTAMENTOS RECENTES */}
                    <div className="grid grid-cols-1 xl:grid-cols-3 gap-3 flex-shrink-0">
                        {/* MÉTRICAS PRINCIPAIS */}
                        <div className="xl:col-span-2 bg-white rounded-lg border border-gray-200 p-3">
                            <h2 className="text-lg font-semibold text-gray-800 mb-2">Métricas Principais</h2>
                            <MetricasGeraisComponent />
                        </div>

                        {/* APONTAMENTOS RECENTES */}
                        <div className="bg-white rounded-lg border border-gray-200 p-3">
                            <h2 className="text-lg font-semibold text-gray-800 mb-2">Apontamentos Recentes</h2>
                            <div className="overflow-y-auto max-h-32">
                                <table className="w-full">
                                    <thead className="sticky top-0 bg-white">
                                        <tr className="border-b border-gray-200">
                                            <th className="text-left py-1 px-1 font-semibold text-gray-700 text-xs">OS</th>
                                            <th className="text-left py-1 px-1 font-semibold text-gray-700 text-xs">Setor</th>
                                            <th className="text-right py-1 px-1 font-semibold text-gray-700 text-xs">Horas</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {(dashboardData.apontamentosRecentes || []).slice(0, 6).map((apt: any, index: number) => (
                                            <tr key={index} className="border-b border-gray-100 hover:bg-gray-50 transition-colors">
                                                <td className="py-1 px-1 font-medium text-blue-600 text-xs">{apt.numero_os}</td>
                                                <td className="py-1 px-1 text-gray-600 text-xs">{apt.setor}</td>
                                                <td className="py-1 px-1 text-right font-medium text-gray-800 text-xs">{apt.horas}h</td>
                                            </tr>
                                        ))}
                                        {(!dashboardData.apontamentosRecentes || dashboardData.apontamentosRecentes.length === 0) && (
                                            <tr>
                                                <td colSpan={3} className="py-2 text-center text-gray-400 text-xs">
                                                    Nenhum apontamento recente
                                                </td>
                                            </tr>
                                        )}
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </div>

                    {/* GRID PRINCIPAL - LARGURA TOTAL SEM SCROLL */}
                    <div className="flex-1 grid grid-cols-1 xl:grid-cols-4 gap-3 min-h-0">
                        {/* COLUNA 1: PROGRAMAÇÕES */}
                        <div className="bg-white rounded-lg border border-gray-200 p-4 flex flex-col">
                            <h2 className="text-sm font-semibold text-gray-700 mb-3">Programações</h2>
                            <div className="bg-gray-50 rounded-lg p-3 border border-gray-200 flex-1">
                                <div className="flex items-center justify-between mb-3">
                                    <h3 className="font-medium text-gray-700">Total</h3>
                                    <span className="bg-gray-500 text-white text-xs px-2 py-1 rounded-full">
                                        {loading ? '...' : dashboardData.programacoes?.total || 0}
                                    </span>
                                </div>
                                <div className="space-y-2">
                                    <div className="flex justify-between items-center">
                                        <span className="text-xs text-gray-600">Enviadas</span>
                                        <span className="font-medium text-gray-700 bg-white px-2 py-1 rounded text-xs">
                                            {loading ? '...' : dashboardData.programacoes?.enviadas || 0}
                                        </span>
                                    </div>
                                    <div className="flex justify-between items-center">
                                        <span className="text-xs text-gray-600">Em Andamento</span>
                                        <span className="font-medium text-gray-700 bg-white px-2 py-1 rounded text-xs">
                                            {loading ? '...' : dashboardData.programacoes?.emAndamento || 0}
                                        </span>
                                    </div>
                                    <div className="flex justify-between items-center">
                                        <span className="text-xs text-gray-600">Concluídas</span>
                                        <span className="font-medium text-gray-700 bg-white px-2 py-1 rounded text-xs">
                                            {loading ? '...' : dashboardData.programacoes?.concluidas || 0}
                                        </span>
                                    </div>
                                </div>
                            </div>
                        </div>

                        {/* COLUNA 2: PENDÊNCIAS */}
                        <div className="bg-white rounded-lg border border-gray-200 p-4 flex flex-col">
                            <h2 className="text-sm font-semibold text-gray-700 mb-3">Pendências</h2>
                            <div className="bg-gray-50 rounded-lg p-3 border border-gray-200 flex-1">
                                <div className="flex items-center justify-between mb-3">
                                    <h3 className="font-medium text-gray-700">Total</h3>
                                    <span className="bg-gray-500 text-white text-xs px-2 py-1 rounded-full">
                                        {loading ? '...' : dashboardData.pendencias?.total || 0}
                                    </span>
                                </div>
                                <div className="space-y-2">
                                    <div className="flex justify-between items-center">
                                        <span className="text-xs text-gray-600">Abertas</span>
                                        <span className="font-medium text-gray-700 bg-white px-2 py-1 rounded text-xs">
                                            {loading ? '...' : dashboardData.pendencias?.abertas || 0}
                                        </span>
                                    </div>
                                    <div className="flex justify-between items-center">
                                        <span className="text-xs text-gray-600">Fechadas</span>
                                        <span className="font-medium text-gray-700 bg-white px-2 py-1 rounded text-xs">
                                            {loading ? '...' : dashboardData.pendencias?.fechadas || 0}
                                        </span>
                                    </div>
                                </div>
                            </div>
                        </div>

                        {/* COLUNA 3: PERFORMANCE DEPARTAMENTOS */}
                        <div className="bg-white rounded-lg border border-gray-200 p-4 flex flex-col">
                            <h2 className="text-sm font-semibold text-gray-700 mb-3">Departamentos</h2>
                            <div className="flex-1 min-h-0">
                                <PerformanceDepartamentosComponent />
                            </div>
                        </div>

                        {/* COLUNA 4: TOP SETORES */}
                        <div className="bg-white rounded-lg border border-gray-200 p-4 flex flex-col">
                            <h2 className="text-sm font-semibold text-gray-700 mb-3">Top Setores</h2>
                            <div className="flex-1 min-h-0">
                                <ResponsiveContainer width="100%" height="100%">
                                    <BarChart
                                        data={(dashboardData.topSetores || []).slice(0, 6)}
                                        margin={{ top: 10, right: 10, left: 10, bottom: 40 }}
                                    >
                                        <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                                        <XAxis
                                            dataKey="nome"
                                            fontSize={10}
                                            angle={-45}
                                            textAnchor="end"
                                            height={40}
                                            interval={0}
                                        />
                                        <YAxis fontSize={10} />
                                        <Tooltip
                                            contentStyle={{
                                                backgroundColor: '#f8fafc',
                                                border: '1px solid #e2e8f0',
                                                borderRadius: '8px',
                                                fontSize: '12px'
                                            }}
                                        />
                                        <Bar dataKey="totalHoras" fill="#3B82F6" radius={[2, 2, 0, 0]} />
                                    </BarChart>
                                </ResponsiveContainer>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </Layout>
    );
};

export default DashboardPage;
