import React, { useState, useEffect } from 'react';
import Layout from '../../components/Layout';
import api from '../../services/api';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, BarChart, Bar, PieChart, Pie, Cell } from 'recharts';

const DashboardPage: React.FC = () => {
    const [dashboardData, setDashboardData] = useState({
        geral: {
            totalApontamentos: 0,
            totalHoras: 0,
            horasExtras: 0,
            retrabalhos: 0,
            osUnicas: 0
        },
        departamentos: [],
        setores: [],
        performanceDepartamentos: [],
        topSetores: [],
        apontamentosRecentes: []
    });

    const [filtros, setFiltros] = useState({
        departamentoSelecionado: '',
        setorSelecionado: '',
        periodo: '6meses'
    });

    const [loading, setLoading] = useState(true);
    const [setoresDisponiveis, setSetoresDisponiveis] = useState([]);
    const [departamentosDisponiveis, setDepartamentosDisponiveis] = useState([]);

    useEffect(() => {
        const fetchDashboardData = async () => {
            try {
                setLoading(true);
                console.log('🔍 Buscando dados escaláveis do dashboard...');

                // Buscar apontamentos detalhados
                const apontamentosResponse = await api.get('/apontamentos-detalhados');
                const apontamentos = Array.isArray(apontamentosResponse.data) ? apontamentosResponse.data : [];
                console.log('📊 Total de apontamentos:', apontamentos.length);

                // Buscar departamentos e setores disponíveis
                const [departamentosResponse, setoresResponse] = await Promise.all([
                    api.get('/departamentos'),
                    api.get('/setores')
                ]);

                const departamentos = Array.isArray(departamentosResponse.data) ? departamentosResponse.data : [];
                const setores = Array.isArray(setoresResponse.data) ? setoresResponse.data : [];

                setDepartamentosDisponiveis(departamentos);
                setSetoresDisponiveis(setores);

                console.log('🏢 Departamentos encontrados:', departamentos.length);
                console.log('🏭 Setores encontrados:', setores.length);

                // Função para processar dados de forma escalável
                const processarDadosEscalaveis = (apontamentos: any[]) => {
                    console.log('🔄 Processando dados de forma escalável...');

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

                    // 2. AGRUPAMENTO POR DEPARTAMENTO
                    const apontamentosPorDepartamento = apontamentos.reduce((acc, a) => {
                        const dept = a.departamento || 'SEM_DEPARTAMENTO';
                        if (!acc[dept]) acc[dept] = [];
                        acc[dept].push(a);
                        return acc;
                    }, {});

                    const departamentosData = Object.entries(apontamentosPorDepartamento).map(([nome, apts]: [string, any[]]) => {
                        const horasDept = apts.reduce((total, a) => total + parseFloat(a.tempo_trabalhado || 0), 0);
                        const horasExtrasDept = apts.filter(a => a.horas_extras && a.horas_extras > 0)
                            .reduce((total, a) => total + parseFloat(a.horas_extras || 0), 0);
                        const retrabalhosDept = apts.filter(a => a.foi_retrabalho === true).length;
                        const osUnicasDept = new Set(apts.map(a => a.numero_os)).size;

                        return {
                            nome,
                            totalHoras: Math.round(horasDept),
                            horasExtras: Math.round(horasExtrasDept),
                            retrabalhos: retrabalhosDept,
                            osUnicas: osUnicasDept,
                            apontamentos: apts.length,
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

                    const setoresData = Object.entries(apontamentosPorSetor).map(([nome, apts]: [string, any[]]) => {
                        const horasSetor = apts.reduce((total, a) => total + parseFloat(a.tempo_trabalhado || 0), 0);
                        const departamento = apts[0]?.departamento || 'SEM_DEPARTAMENTO';

                        return {
                            nome,
                            departamento,
                            totalHoras: Math.round(horasSetor),
                            apontamentos: apts.length,
                            osUnicas: new Set(apts.map(a => a.numero_os)).size,
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
                const dadosProcessados = processarDadosEscalaveis(apontamentosFiltrados);

                // Gerar performance por departamento
                const performanceDepartamentos = gerarPerformanceDepartamentos(apontamentosFiltrados, dadosProcessados.departamentos);

                console.log('📊 Dados processados:', {
                    geral: dadosProcessados.geral,
                    departamentos: dadosProcessados.departamentos.length,
                    topSetores: dadosProcessados.topSetores.length
                });

                // Atualizar estado com dados escaláveis
                setDashboardData({
                    ...dadosProcessados,
                    performanceDepartamentos
                });

            } catch (error) {
                console.error('Erro ao carregar dados do dashboard:', error);
                // Manter dados padrão em caso de erro
                setDashboardData({
                    geral: {
                        totalApontamentos: 0,
                        totalHoras: 0,
                        horasExtras: 0,
                        retrabalhos: 0,
                        osUnicas: 0
                    },
                    departamentos: [],
                    setores: [],
                    performanceDepartamentos: [],
                    topSetores: [],
                    apontamentosRecentes: []
                });
            } finally {
                setLoading(false);
            }
        };

        fetchDashboardData();
    }, [filtros]); // Recarregar quando filtros mudarem

    // Componente de gráfico de linha descendente
    const ChartComponent: React.FC<{ title: string, data: any[] }> = ({ title, data }) => {
        // Transformar dados para formato do gráfico de linha
        const chartData = [
            { mes: 'Jan', ...data.reduce((acc, item) => ({ ...acc, [item.setor]: item.janeiro }), {}) },
            { mes: 'Fev', ...data.reduce((acc, item) => ({ ...acc, [item.setor]: item.fevereiro }), {}) },
            { mes: 'Mar', ...data.reduce((acc, item) => ({ ...acc, [item.setor]: item.marco }), {}) },
            { mes: 'Abr', ...data.reduce((acc, item) => ({ ...acc, [item.setor]: item.abril }), {}) },
            { mes: 'Mai', ...data.reduce((acc, item) => ({ ...acc, [item.setor]: item.maio }), {}) },
            { mes: 'Jun', ...data.reduce((acc, item) => ({ ...acc, [item.setor]: item.junho }), {}) }
        ];

        const colors = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#06B6D4'];

        return (
            <div className="bg-white p-4 rounded-lg shadow">
                <h3 className="text-lg font-semibold mb-4">{title}</h3>
                <div className="h-64">
                    <ResponsiveContainer width="100%" height="100%">
                        <LineChart data={chartData}>
                            <CartesianGrid strokeDasharray="3 3" />
                            <XAxis dataKey="mes" />
                            <YAxis />
                            <Tooltip />
                            <Legend />
                            {data.map((item, index) => (
                                <Line
                                    key={item.setor}
                                    type="monotone"
                                    dataKey={item.setor}
                                    stroke={colors[index % colors.length]}
                                    strokeWidth={2}
                                    dot={{ r: 4 }}
                                />
                            ))}
                        </LineChart>
                    </ResponsiveContainer>
                </div>
            </div>
        );
    };

    // Componente de filtros
    const FiltrosComponent: React.FC = () => (
        <div className="bg-white p-4 rounded-lg shadow mb-6">
            <h3 className="text-lg font-semibold mb-4">Filtros</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Departamento</label>
                    <select
                        value={filtros.departamentoSelecionado}
                        onChange={(e) => setFiltros(prev => ({ ...prev, departamentoSelecionado: e.target.value }))}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                        <option value="">Todos os Departamentos</option>
                        {departamentosDisponiveis.map((dept: any) => (
                            <option key={dept.id} value={dept.nome_tipo || dept.nome}>
                                {dept.nome_tipo || dept.nome}
                            </option>
                        ))}
                    </select>
                </div>
                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Setor</label>
                    <select
                        value={filtros.setorSelecionado}
                        onChange={(e) => setFiltros(prev => ({ ...prev, setorSelecionado: e.target.value }))}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                        <option value="">Todos os Setores</option>
                        {setoresDisponiveis
                            .filter((setor: any) => !filtros.departamentoSelecionado || setor.departamento === filtros.departamentoSelecionado)
                            .map((setor: any) => (
                                <option key={setor.id} value={setor.nome}>
                                    {setor.nome}
                                </option>
                            ))}
                    </select>
                </div>
                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Período</label>
                    <select
                        value={filtros.periodo}
                        onChange={(e) => setFiltros(prev => ({ ...prev, periodo: e.target.value }))}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                        <option value="6meses">Últimos 6 meses</option>
                        <option value="3meses">Últimos 3 meses</option>
                        <option value="1mes">Último mês</option>
                    </select>
                </div>
            </div>
        </div>
    );

    // Componente de métricas gerais
    const MetricasGeraisComponent: React.FC = () => (
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-6">
            <div className="bg-white p-4 rounded-lg shadow text-center">
                <p className="text-sm text-gray-600">Total Apontamentos</p>
                <p className="text-2xl font-bold text-blue-600">
                    {loading ? '...' : dashboardData.geral.totalApontamentos.toLocaleString()}
                </p>
            </div>
            <div className="bg-white p-4 rounded-lg shadow text-center">
                <p className="text-sm text-gray-600">Total Horas</p>
                <p className="text-2xl font-bold text-green-600">
                    {loading ? '...' : `${dashboardData.geral.totalHoras.toLocaleString()}h`}
                </p>
            </div>
            <div className="bg-white p-4 rounded-lg shadow text-center">
                <p className="text-sm text-gray-600">Horas Extras</p>
                <p className="text-2xl font-bold text-yellow-600">
                    {loading ? '...' : `${dashboardData.geral.horasExtras.toLocaleString()}h`}
                </p>
            </div>
            <div className="bg-white p-4 rounded-lg shadow text-center">
                <p className="text-sm text-gray-600">Retrabalhos</p>
                <p className="text-2xl font-bold text-red-600">
                    {loading ? '...' : dashboardData.geral.retrabalhos.toLocaleString()}
                </p>
            </div>
            <div className="bg-white p-4 rounded-lg shadow text-center">
                <p className="text-sm text-gray-600">OS Únicas</p>
                <p className="text-2xl font-bold text-purple-600">
                    {loading ? '...' : dashboardData.geral.osUnicas.toLocaleString()}
                </p>
            </div>
        </div>
    );

    const TableComponent: React.FC<{ title: string, columns: string[], data: any[] }> = ({ title, columns, data }) => (
        <div className="bg-white p-4 rounded-lg shadow overflow-hidden">
            <h3 className="text-lg font-semibold mb-4">{title}</h3>
            <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                        <tr>
                            {columns.map((col, index) => (
                                <th key={index} className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                    {col}
                                </th>
                            ))}
                        </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                        {data.length > 0 ? data.map((row, rowIndex) => (
                            <tr key={rowIndex}>
                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                    {row.numero_os || 'N/A'}
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                    {row.cliente || 'Cliente não informado'}
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                    {row.status || 'TESTE'}
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                    {row.prioridade || 'MEDIA'}
                                </td>
                            </tr>
                        )) : (
                            <tr>
                                <td colSpan={4} className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 text-center">
                                    Nenhuma OS encontrada
                                </td>
                            </tr>
                        )}
                    </tbody>
                </table>
            </div>
        </div>
    );

    // Componente de gráfico de performance por departamento
    const PerformanceDepartamentosComponent: React.FC = () => {
        const colors = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6'];

        return (
            <div className="bg-white p-4 rounded-lg shadow">
                <h3 className="text-lg font-semibold mb-4">Performance por Departamento (Últimos 6 Meses)</h3>
                <div className="h-80">
                    <ResponsiveContainer width="100%" height="100%">
                        <LineChart data={dashboardData.performanceDepartamentos}>
                            <CartesianGrid strokeDasharray="3 3" />
                            <XAxis dataKey="mes" />
                            <YAxis />
                            <Tooltip formatter={(value, name) => [`${value}h`, name]} />
                            <Legend />
                            {dashboardData.departamentos.map((dept, index) => (
                                <Line
                                    key={dept.nome}
                                    type="monotone"
                                    dataKey={dept.nome}
                                    stroke={colors[index % colors.length]}
                                    strokeWidth={3}
                                    dot={{ r: 5 }}
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
            <div className="bg-white p-4 rounded-lg shadow">
                <h3 className="text-lg font-semibold mb-4">Distribuição de Horas por Departamento</h3>
                <div className="h-80">
                    <ResponsiveContainer width="100%" height="100%">
                        <PieChart>
                            <Pie
                                data={dashboardData.departamentos}
                                dataKey="totalHoras"
                                nameKey="nome"
                                cx="50%"
                                cy="50%"
                                outerRadius={100}
                                label={({ nome, percentualHoras }) => `${nome}: ${percentualHoras}%`}
                            >
                                {dashboardData.departamentos.map((entry, index) => (
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

    // Componente de top setores
    const TopSetoresComponent: React.FC = () => (
        <div className="bg-white p-4 rounded-lg shadow">
            <h3 className="text-lg font-semibold mb-4">Top 10 Setores por Horas Trabalhadas</h3>
            <div className="h-80">
                <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={dashboardData.topSetores} layout="horizontal">
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis type="number" />
                        <YAxis dataKey="nome" type="category" width={120} />
                        <Tooltip formatter={(value) => [`${value}h`, 'Horas']} />
                        <Bar dataKey="totalHoras" fill="#3B82F6" />
                    </BarChart>
                </ResponsiveContainer>
            </div>
        </div>
    );

    return (
        <Layout>
            <div className="space-y-6">
                {/* Cabeçalho */}
                <div className="bg-white rounded-lg shadow-md p-6">
                    <h1 className="text-3xl font-bold text-gray-800">Dashboard Geral</h1>
                    <p className="text-gray-600">Visão geral escalável dos apontamentos de todos os departamentos e setores</p>
                </div>

                {/* Filtros */}
                <FiltrosComponent />

                {/* Métricas Gerais */}
                <MetricasGeraisComponent />

                {/* Gráficos Principais */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    <PerformanceDepartamentosComponent />
                    <DepartamentosPieComponent />
                </div>

                {/* Top Setores */}
                <TopSetoresComponent />

                {/* Tabelas de Dados */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    {/* Departamentos */}
                    <div className="bg-white p-4 rounded-lg shadow">
                        <h3 className="text-lg font-semibold mb-4">Departamentos - Resumo</h3>
                        <div className="overflow-x-auto">
                            <table className="min-w-full divide-y divide-gray-200">
                                <thead className="bg-gray-50">
                                    <tr>
                                        <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Departamento</th>
                                        <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Horas</th>
                                        <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">OS</th>
                                        <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">%</th>
                                    </tr>
                                </thead>
                                <tbody className="bg-white divide-y divide-gray-200">
                                    {dashboardData.departamentos.map((dept, index) => (
                                        <tr key={index}>
                                            <td className="px-4 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                                                {dept.nome}
                                            </td>
                                            <td className="px-4 py-4 whitespace-nowrap text-sm text-gray-500">
                                                {dept.totalHoras.toLocaleString()}h
                                            </td>
                                            <td className="px-4 py-4 whitespace-nowrap text-sm text-gray-500">
                                                {dept.osUnicas}
                                            </td>
                                            <td className="px-4 py-4 whitespace-nowrap text-sm text-gray-500">
                                                {dept.percentualHoras}%
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    </div>

                    {/* Apontamentos Recentes */}
                    <div className="bg-white p-4 rounded-lg shadow">
                        <h3 className="text-lg font-semibold mb-4">Apontamentos Recentes</h3>
                        <div className="overflow-x-auto">
                            <table className="min-w-full divide-y divide-gray-200">
                                <thead className="bg-gray-50">
                                    <tr>
                                        <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">OS</th>
                                        <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Setor</th>
                                        <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Horas</th>
                                        <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                                    </tr>
                                </thead>
                                <tbody className="bg-white divide-y divide-gray-200">
                                    {dashboardData.apontamentosRecentes.map((apt, index) => (
                                        <tr key={index}>
                                            <td className="px-4 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                                                {apt.numero_os}
                                            </td>
                                            <td className="px-4 py-4 whitespace-nowrap text-sm text-gray-500">
                                                {apt.setor}
                                            </td>
                                            <td className="px-4 py-4 whitespace-nowrap text-sm text-gray-500">
                                                {apt.horas.toFixed(1)}h
                                            </td>
                                            <td className="px-4 py-4 whitespace-nowrap text-sm text-gray-500">
                                                <span className={`px-2 py-1 text-xs rounded-full ${
                                                    apt.status === 'FINALIZADO'
                                                        ? 'bg-green-100 text-green-800'
                                                        : 'bg-yellow-100 text-yellow-800'
                                                }`}>
                                                    {apt.status}
                                                </span>
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>
        </Layout>
    );
};

export default DashboardPage;
