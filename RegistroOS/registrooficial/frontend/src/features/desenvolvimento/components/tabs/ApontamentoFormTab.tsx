import React, { useState, useEffect, useCallback } from 'react';
import { useSearchParams } from 'react-router-dom';
import { useSetor } from '../../../../contexts/SetorContext';
import { useAuth } from '../../../../contexts/AuthContext';
import api from '../../../../services/api';
import { formatarTextoInput, criarHandlerTextoValidado } from '../../../../utils/textValidation';

interface ApontamentoFormTabProps {
    formData: any;
    setFormData: (data: any) => void;
    testResults: any;
    testObservations: any;
    onTestResultChange: (testId: string, result: string) => void;
    onTestCheckboxChange: (testId: string, checked: boolean) => void;
    onTestObservationChange: (testId: string, obs: string) => void;

    handleSupervisorHorasOrcadasChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
    handleSupervisorTestesIniciaisChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
    handleSupervisorTestesParciaisChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
    handleSupervisorTestesFinaisChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
    handleSaveApontamento: () => Promise<void>;

    // Novas props para resolução de pendências e programações
    dadosPreenchidos?: any;
    pendenciaParaResolver?: any;
    programacaoParaIniciar?: any;
    onPendenciaResolvida?: () => void;
    onProgramacaoIniciada?: () => void;
}
const ApontamentoFormTab: React.FC<ApontamentoFormTabProps> = ({
    formData,
    setFormData,
    testResults,
    testObservations,
    onTestResultChange,
    onTestCheckboxChange,
    onTestObservationChange,
    handleSupervisorHorasOrcadasChange,
    handleSupervisorTestesIniciaisChange,
    handleSupervisorTestesParciaisChange,
    handleSupervisorTestesFinaisChange,
    dadosPreenchidos,
    pendenciaParaResolver,
    programacaoParaIniciar,
    onPendenciaResolvida,
    onProgramacaoIniciada
}) => {
    const [searchParams] = useSearchParams();
    const { configuracaoAtual, setorAtivo } = useSetor();
    const { user } = useAuth();

    // Detectar se vem de uma programação
    const osFromUrl = searchParams.get('os');
    const programacaoId = searchParams.get('programacao_id');

    // Debug dos parâmetros da URL
    console.log('🔍 Parâmetros da URL detectados:', {
        osFromUrl,
        programacaoId,
        allParams: Object.fromEntries(searchParams.entries())
    });

    // Estados para dropdowns
    const [tiposMaquina, setTiposMaquina] = useState<any[]>([]);
    const [tiposAtividade, setTiposAtividade] = useState<any[]>([]);
    const [descricoesAtividade, setDescricoesAtividade] = useState<any[]>([]);
    const [causasRetrabalho, setCausasRetrabalho] = useState<any[]>([]);
    const [tiposTeste, setTiposTeste] = useState<any[]>([]);
    const [tiposTesteOriginais, setTiposTesteOriginais] = useState<any[]>([]);
    const [tiposTesteUnicos, setTiposTesteUnicos] = useState<string[]>([]);
    const [filtroTipoTeste, setFiltroTipoTeste] = useState<string>('');
    const [filtroNomeTeste, setFiltroNomeTeste] = useState<string>('');
    const [filtroCategoria, setFiltroCategoria] = useState<string>('');
    const [filtroSubcategoria, setFiltroSubcategoria] = useState<string>('');
    const [categoriasUnicas, setCategoriasUnicas] = useState<string[]>([]);
    const [testesExclusivos, setTestesExclusivos] = useState<any[]>([]);
    const [testesExclusivosSelecionados, setTestesExclusivosSelecionados] = useState<Record<number, boolean>>({});
    const [loadingDropdowns, setLoadingDropdowns] = useState(false);

    // Estados para controlar carregamentos únicos
    const [dadosInicaisCarregados, setDadosInicaisCarregados] = useState(false);

    // Estados para categorias e subcategorias
    const [categoriasMaquina, setCategoriasMaquina] = useState<string[]>([]);
    const [subcategoriasDisponiveis, setSubcategoriasDisponiveis] = useState<string[]>([]);
    const [tiposMaquinaCategoria, setTiposMaquinaCategoria] = useState<any[]>([]);
    const [tipoMaquinaSelecionado, setTipoMaquinaSelecionado] = useState<any>(null);

    // Estados removidos - sistema de testes exclusivos simplificado

    // Estados para busca de OS
    const [loadingOS, setLoadingOS] = useState(false);
    const [osEncontrada, setOsEncontrada] = useState<boolean | null>(null);
    const [mensagemOS, setMensagemOS] = useState<string>('');
    const [osBloqueadaParaApontamento, setOsBloqueadaParaApontamento] = useState(false);

    // Estados para detecção de programação
    const [programacaoDetectada, setProgramacaoDetectada] = useState<any>(null);
    const [loadingProgramacao, setLoadingProgramacao] = useState(false);
    const [mostraOpcoesFinalizacao, setMostraOpcoesFinalizacao] = useState(false);

    // Estados para testes selecionados
    const [testesSelecionados, setTestesSelecionados] = useState<{[key: number]: {
        selecionado: boolean;
        resultado: 'APROVADO' | 'REPROVADO' | 'INCONCLUSIVO' | '';
        observacao: string;
    }}>({});
    const [ComponentesEtapa1, setComponentesEtapa1] = useState<React.ComponentType<any>[]>([]);
    const [ComponentesEtapa2, setComponentesEtapa2] = useState<React.ComponentType<any>[]>([]);



    useEffect(() => {
        if (configuracaoAtual && configuracaoAtual.ComponentesFormularioPrincipal) {
            const componentesPorEtapa: Record<number, React.ComponentType<any>[]> = {};

            configuracaoAtual.ComponentesFormularioPrincipal.forEach((comp: any) => {
                if (!componentesPorEtapa[comp.etapa]) {
                    componentesPorEtapa[comp.etapa] = [];
                }
                componentesPorEtapa[comp.etapa].push(comp.componente);
            });

            setComponentesEtapa1(componentesPorEtapa[1] || []);
            setComponentesEtapa2(componentesPorEtapa[2] || []);
        } else {
            // Se não há configuração, definir componentes vazios para permitir que a página carregue
            setComponentesEtapa1([]);
            setComponentesEtapa2([]);
        }
    }, [configuracaoAtual]);

    // Função para remover duplicatas por ID
    const removeDuplicatesById = (array: any[]) => {
        const seen = new Set();
        return array.filter(item => {
            if (seen.has(item.id)) {
                console.warn(`🚨 ID duplicado encontrado: ${item.id}`, item);
                return false;
            }
            seen.add(item.id);
            return true;
        });
    };

    // Funções para carregar dados dos dropdowns
    const loadTiposMaquina = async () => {
        try {
            const response = await api.get('/desenvolvimento/formulario/tipos-maquina');
            const dadosLimpos = removeDuplicatesById(response.data || []);
            console.log(`📋 Tipos de máquina carregados: ${dadosLimpos.length} (originais: ${response.data?.length || 0})`);

            // Log das categorias para debug
            console.log('📋 Categorias encontradas:');
            dadosLimpos.forEach(tipo => {
                console.log(`   - ${tipo.nome_tipo} | Categoria: '${tipo.categoria}'`);
            });

            setTiposMaquina(dadosLimpos);
        } catch (error) {
            console.error('Erro ao carregar tipos de máquina:', error);
            setTiposMaquina([]);
        }
    };

    const loadTiposAtividade = async (tipoMaquinaId?: number) => {
        try {
            let url = '/desenvolvimento/formulario/tipos-atividade';
            if (tipoMaquinaId) {
                url += `?tipo_maquina_id=${tipoMaquinaId}`;
                console.log(`🔧 Carregando tipos de atividade para tipo de máquina ID: ${tipoMaquinaId}`);
            } else {
                console.log('🔧 Carregando TODOS os tipos de atividade');
            }

            const response = await api.get(url);
            const dadosLimpos = removeDuplicatesById(response.data || []);
            console.log(`🔧 Tipos de atividade carregados: ${dadosLimpos.length} (originais: ${response.data?.length || 0})`);
            setTiposAtividade(dadosLimpos);
        } catch (error) {
            console.error('Erro ao carregar tipos de atividade:', error);
            setTiposAtividade([]);
        }
    };

    const loadDescricoesAtividade = async (tipoAtividade?: string) => {
        console.log('🚀 FUNÇÃO loadDescricoesAtividade CHAMADA!');
        try {
            // ✅ CORREÇÃO: Não enviar filtro por tipo_atividade pois não há relacionamento direto
            // Sempre carregar todas as descrições disponíveis
            const url = `/desenvolvimento/formulario/descricoes-atividade`;
            console.log('📄 Carregando TODAS as descrições de atividade (sem filtro)');
            console.log('📡 URL da chamada:', url);
            console.log('🔧 API base URL:', api.defaults.baseURL);

            const response = await api.get(url);
            console.log('📄 Resposta da API descrições:', {
                status: response.status,
                statusText: response.statusText,
                dataLength: response.data?.length || 0,
                dataType: typeof response.data,
                isArray: Array.isArray(response.data),
                primeirasDescricoes: response.data?.slice(0, 3)
            });

            const descricoes = response.data || [];
            const dadosLimpos = removeDuplicatesById(descricoes);
            console.log('📄 Descrições processadas:', {
                length: dadosLimpos.length,
                originais: descricoes.length,
                isArray: Array.isArray(dadosLimpos),
                sample: dadosLimpos.slice(0, 2)
            });

            setDescricoesAtividade(dadosLimpos);
            console.log('✅ Estado descrições atualizado com sucesso!');

        } catch (error: unknown) {
            console.error('❌ ERRO DETALHADO ao carregar descrições:', {
                message: (error as Error).message,
                response: (error as any).response?.data,
                status: (error as any).response?.status,
                config: (error as any).config
            });
            setDescricoesAtividade([]);
        }
    };

    const loadCausasRetrabalho = async () => {
        try {
            const response = await api.get('/desenvolvimento/formulario/causas-retrabalho');
            const dadosLimpos = removeDuplicatesById(response.data || []);
            console.log(`🔄 Causas de retrabalho carregadas: ${dadosLimpos.length} (originais: ${response.data?.length || 0})`);
            setCausasRetrabalho(dadosLimpos);
        } catch (error) {
            console.error('Erro ao carregar causas de retrabalho:', error);
            setCausasRetrabalho([]);
        }
    };

    const loadTiposPorCategoria = async (nomeGeral: string) => {
        try {
            console.log(`🔧 Carregando todos os tipos específicos para nome geral: ${nomeGeral}`);

            // Usar o novo endpoint que separa as categorias por vírgula
            const response = await api.get(`/desenvolvimento/formulario/categorias-por-nome-tipo/${encodeURIComponent(nomeGeral)}`);
            const categorias = response.data || [];

            console.log(`🔧 Categorias encontradas para '${nomeGeral}':`, categorias);
            console.log(`🔧 Total de categorias: ${categorias.length}`);

            // Atualizar lista com as categorias específicas
            setCategoriasMaquina(categorias);

            // Limpar seleções
            setFormData((prev: any) => ({
                ...prev,
                categoriaSelecionada: '',
                subcategoriasSelecionadas: []
            }));
            setSubcategoriasDisponiveis([]);

            return categorias;
        } catch (error) {
            console.error('Erro ao carregar tipos por categoria:', error);
            setCategoriasMaquina([]);
            return [];
        }
    };

    const loadSubcategoriasPorTipo = async (tipoEspecifico: string) => {
        try {
            console.log(`🔧 Carregando subcategorias para tipo específico: ${tipoEspecifico}`);

            // Usar o novo endpoint que busca subcategorias por categoria
            const response = await api.get(`/desenvolvimento/formulario/subcategorias-por-categoria/${encodeURIComponent(tipoEspecifico)}`);
            const subcategorias = response.data || [];

            console.log(`🔧 Subcategorias encontradas para '${tipoEspecifico}': ${subcategorias.join(', ')}`);

            // Atualizar lista de subcategorias disponíveis
            setSubcategoriasDisponiveis(subcategorias);

            return subcategorias;
        } catch (error) {
            console.error('Erro ao carregar subcategorias por tipo:', error);
            setSubcategoriasDisponiveis([]);
            return [];
        }
    };

    const loadTiposTeste = async (departamento?: string, setor?: string, tipoMaquina?: string) => {
        try {
            const params = new URLSearchParams();
            if (departamento) params.append('departamento', departamento);
            if (setor) params.append('setor', setor);
            if (tipoMaquina) params.append('tipo_maquina', tipoMaquina);

            console.log('🧪 Carregando tipos de teste com filtros:', { departamento, setor, tipoMaquina });
            console.log('🔍 URL completa da requisição:', `/tipos-teste?${params.toString()}`);
            const response = await api.get(`/tipos-teste?${params.toString()}`);
            console.log('🧪 Tipos de teste carregados:', response.data);

            const dadosCarregados = response.data || [];
            setTiposTesteOriginais(dadosCarregados);
            setTiposTeste(dadosCarregados);

            // Extrair tipos únicos da coluna tipo_teste
            const tiposUnicos = [...new Set(dadosCarregados
                .map((teste: any) => teste.tipo_teste)
                .filter((tipo: string) => tipo && tipo.trim() !== '')
            )] as string[];
            tiposUnicos.sort();

            // Extrair categorias únicas
            const categoriasUnicas = [...new Set(dadosCarregados
                .map((teste: any) => teste.categoria)
                .filter((categoria: string) => categoria && categoria.trim() !== '')
            )] as string[];
            categoriasUnicas.sort();

            console.log('🏷️ Tipos únicos encontrados:', tiposUnicos);
            console.log('🏷️ Categorias únicas encontradas:', categoriasUnicas);
            setTiposTesteUnicos(tiposUnicos);
            setCategoriasUnicas(categoriasUnicas);

            // Limpar filtros e seleções anteriores
            setFiltroTipoTeste('');
            setFiltroNomeTeste('');
            setFiltroCategoria('');
            setFiltroSubcategoria('');
            setTestesSelecionados({});
        } catch (error) {
            console.error('Erro ao carregar tipos de teste:', error);
            setTiposTeste([]);
            setTiposTesteOriginais([]);
            setTiposTesteUnicos([]);
            setTestesSelecionados({});
        }
    };

    const loadTestesExclusivos = async (departamento?: string, setor?: string) => {
        try {
            const params = new URLSearchParams();
            if (departamento) params.append('departamento', departamento);
            if (setor) params.append('setor', setor);
            params.append('teste_exclusivo_setor', '1');

            console.log('🔍 Carregando testes exclusivos com filtros:', { departamento, setor });
            const response = await api.get(`/tipos-teste?${params.toString()}`);
            console.log('🔍 Testes exclusivos carregados:', response.data);

            const testesExclusivos = response.data || [];
            setTestesExclusivos(testesExclusivos);

            // Limpar seleções anteriores
            setTestesExclusivosSelecionados({});
        } catch (error) {
            console.error('Erro ao carregar testes exclusivos:', error);
            setTestesExclusivos([]);
            setTestesExclusivosSelecionados({});
        }
    };

    // Funções para manipular testes selecionados
    const handleTesteClick = (testeId: number) => {
        setTestesSelecionados(prev => ({
            ...prev,
            [testeId]: {
                selecionado: !prev[testeId]?.selecionado,
                resultado: prev[testeId]?.resultado || '',
                observacao: prev[testeId]?.observacao || ''
            }
        }));
    };

    const handleResultadoChange = (testeId: number, resultado: 'APROVADO' | 'REPROVADO' | 'INCONCLUSIVO') => {
        setTestesSelecionados(prev => ({
            ...prev,
            [testeId]: {
                ...prev[testeId],
                resultado
            }
        }));
    };

    const handleObservacaoChange = (testeId: number, observacao: string) => {
        if (observacao.length <= 100) {
            setTestesSelecionados(prev => ({
                ...prev,
                [testeId]: {
                    ...prev[testeId],
                    observacao
                }
            }));
        }
    };

    // Função para aplicar todos os filtros
    const aplicarFiltros = (
        tipoTeste: string = filtroTipoTeste,
        nomeTeste: string = filtroNomeTeste,
        categoria: string = filtroCategoria,
        subcategoria: string = filtroSubcategoria
    ) => {
        console.log('🔍 Aplicando filtros:', { tipoTeste, nomeTeste, categoria, subcategoria });

        let tiposFiltrados = [...tiposTesteOriginais];

        // Filtrar por tipo_teste (Estático/Dinâmico)
        if (tipoTeste !== '') {
            tiposFiltrados = tiposFiltrados.filter(teste => teste.tipo_teste === tipoTeste);
        }

        // Filtrar por nome do teste
        if (nomeTeste !== '') {
            tiposFiltrados = tiposFiltrados.filter(teste =>
                teste.nome.toLowerCase().includes(nomeTeste.toLowerCase())
            );
        }

        // Filtrar por categoria (Visual, Elétricos, Mecânicos)
        if (categoria !== '') {
            tiposFiltrados = tiposFiltrados.filter(teste => teste.categoria === categoria);
        }

        // Filtrar por subcategoria (Padrão/Especiais)
        if (subcategoria !== '') {
            const subcategoriaValue = subcategoria === 'especiais' ? 1 : 0;
            tiposFiltrados = tiposFiltrados.filter(teste => teste.subcategoria === subcategoriaValue);
        }

        setTiposTeste(tiposFiltrados);
        console.log('🔍 Resultados filtrados:', tiposFiltrados.length);
    };

    // Função para filtrar tipos de teste
    const handleFiltroTipoTeste = (tipoTeste: string) => {
        setFiltroTipoTeste(tipoTeste);
        aplicarFiltros(tipoTeste, filtroNomeTeste, filtroCategoria, filtroSubcategoria);
    };

    // Função para filtrar por nome do teste
    const handleFiltroNomeTeste = (nomeTeste: string) => {
        setFiltroNomeTeste(nomeTeste);
        aplicarFiltros(filtroTipoTeste, nomeTeste, filtroCategoria, filtroSubcategoria);
    };

    // Função para filtrar por categoria
    const handleFiltroCategoria = (categoria: string) => {
        setFiltroCategoria(categoria);
        aplicarFiltros(filtroTipoTeste, filtroNomeTeste, categoria, filtroSubcategoria);
    };

    // Função para filtrar por subcategoria
    const handleFiltroSubcategoria = (subcategoria: string) => {
        setFiltroSubcategoria(subcategoria);
        aplicarFiltros(filtroTipoTeste, filtroNomeTeste, filtroCategoria, subcategoria);
    };

    // Funções para carregar categorias e subcategorias do banco
    const loadCategoriasMaquina = async () => { // Removidos parâmetros opcionais, o contexto do usuário é sempre disponível via `user`
        try {
            // Usar o endpoint correto para categorias de máquina
            // O backend filtra por departamento/setor do usuário logado se não for ADMIN
            const response = await api.get('/desenvolvimento/admin/categorias-maquina');
            console.log('🎯 Categorias carregadas:', response.data);
            setCategoriasMaquina(response.data || []);
        } catch (error) {
            console.error('Erro ao carregar categorias de máquina:', error);
            setCategoriasMaquina([]);
        }
    };

    const loadSubcategoriasPorCategoria = async (categoria: string, departamento?: string, setor?: string) => {
        try {
            const params = new URLSearchParams();
            params.append('categoria', categoria);
            if (departamento) params.append('departamento', departamento);
            if (setor) params.append('setor', setor);

            const response = await api.get(`/desenvolvimento/tipos-maquina/subcategorias?${params.toString()}`);
            console.log('🎯 Subcategorias carregadas para', categoria, ':', response.data);
            setSubcategoriasDisponiveis(response.data || []);
        } catch (error) {
            console.error('Erro ao carregar subcategorias:', error);
            setSubcategoriasDisponiveis([]);
        }
    };



    const handleTesteExclusivoChange = (testeId: number, checked: boolean) => {
        setTestesExclusivosSelecionados(prev => ({
            ...prev,
            [testeId]: checked
        }));
        console.log('🔍 Teste exclusivo alterado:', { testeId, checked });
    };

    // Função para carregar categorias e subcategorias por nome do tipo de máquina
    const loadCategoriasSubcategoriasPorNomeTipo = async (nomeTipo: string) => {
        try {
            // CORREÇÃO: nome_tipo é a categoria geral, não o tipo específico
            console.log(`🔧 Carregando tipos específicos para categoria geral: ${nomeTipo}`);

            // Carregar todos os tipos específicos da categoria geral
            await loadTiposPorCategoria(nomeTipo);
            return nomeTipo;
        } catch (error) {
            console.error('Erro ao carregar categorias/subcategorias por tipo:', error);
            return null;
        }
    };

    // Função detectarTestesAutomaticamente removida - sistema simplificado

    // Função confirmarFinalizacaoTeste removida - sistema simplificado

    // Função para buscar OS na base de dados
    const buscarOS = async (numeroOS: string) => {
        if (!numeroOS || numeroOS.trim() === '') {
            setOsEncontrada(null);
            setMensagemOS('');
            return;
        }

        setLoadingOS(true);
        setMensagemOS('⚠️ OS não cadastrada na base de dados. AGUARDE CONSULTA VIA WEB.');
        setOsBloqueadaParaApontamento(false); // Reset do estado de bloqueio

        try {
            console.log('🔍 Buscando OS:', numeroOS);

            // Timeout maior para permitir scraping (5 minutos)
            const response = await api.get(`/desenvolvimento/formulario/buscar-os/${numeroOS}`, {
                timeout: 300000 // 5 minutos
            });

            if (response.data) {
                console.log('✅ OS encontrada:', response.data);

                // Preencher campos automaticamente
                setFormData((prev: any) => ({
                    ...prev,
                    statusOS: response.data.status || '',
                    inpCliente: response.data.cliente || '',
                    inpEquipamento: response.data.equipamento || ''
                }));

                setOsEncontrada(true);

                // Verificar se a OS está bloqueada para apontamentos
                const statusFinalizados = [
                    'RECUSADA - CONFERIDA',
                    'TERMINADA - CONFERIDA',
                    'TERMINADA - EXPEDIDA',
                    'OS CANCELADA'
                ];

                const statusAtual = response.data.status || '';
                const bloqueada = statusFinalizados.includes(statusAtual);
                setOsBloqueadaParaApontamento(bloqueada);

                // Mostrar mensagem apropriada
                const fonte = response.data.fonte || 'banco';
                if (bloqueada) {
                    setMensagemOS('⚠️ OS não permitida para apontamento');
                } else if (fonte === 'scraping') {
                    setMensagemOS('✅ OS encontrada via consulta web e campos preenchidos automaticamente');
                } else {
                    setMensagemOS('✅ OS encontrada no banco e campos preenchidos automaticamente');
                }
            } else {
                console.log('❌ OS não encontrada');
                setOsEncontrada(false);
                setMensagemOS('⚠️ OS não cadastrada na base de dados. Você pode preencher os campos manualmente.');
            }
        } catch (error: any) {
            console.error('Erro ao buscar OS:', error);
            setOsEncontrada(false);

            // Usar a mensagem de erro do backend se disponível
            const errorMessage = error?.response?.data?.detail ||
                               '⚠️ OS não cadastrada na base de dados. Você pode preencher os campos manualmente.';
            setMensagemOS(errorMessage);
        } finally {
            setLoadingOS(false);
        }
    };

    // Função para validar regras de negócio
    const validarRegrasNegocio = async () => {
        const erros: string[] = [];
        const avisos: string[] = [];

        console.log('🔍 Iniciando validações de regras de negócio...');

        // 1. VALIDAR CAMPOS OBRIGATÓRIOS
        if (!formData.inpNumOS) erros.push('📋 Número da OS é obrigatório');
        if (!formData.statusOS) erros.push('📊 Status OS é obrigatório');
        if (!formData.inpCliente) erros.push('🏢 Cliente é obrigatório');
        if (!formData.inpEquipamento) erros.push('⚙️ Equipamento é obrigatório');
        if (!formData.selMaq) erros.push('🔧 Tipo de Máquina é obrigatório');
        if (!formData.selAtiv) erros.push('📝 Tipo de Atividade é obrigatório');
        if (!formData.selDescAtiv) erros.push('📄 Descrição da Atividade é obrigatório');
        if (!formData.inpData) erros.push('📅 Data Início é obrigatório');
        if (!formData.inpHora) erros.push('🕒 Hora Início é obrigatório');
        if (!formData.observacao) erros.push('💬 Observação Geral é obrigatório');
        if (!formData.resultadoGlobal) erros.push('🎯 Resultado Global é obrigatório');
        if (!formData.inpDataFim) erros.push('📅 Data Fim é obrigatório');
        if (!formData.inpHoraFim) erros.push('🕒 Hora Fim é obrigatório');

        console.log('✅ Validação de campos obrigatórios concluída');

        // 2. VALIDAR DATAS - NÃO PODE SER FUTURO E MAX 5 DIAS ÚTEIS ANTERIORES
        if (formData.inpData) {
            const dataInicio = new Date(formData.inpData);
            const hoje = new Date();
            hoje.setHours(0, 0, 0, 0); // Zerar horas para comparação apenas de data
            dataInicio.setHours(0, 0, 0, 0);

            console.log('📅 Validando datas:', { dataInicio, hoje });

            // Não pode ser futuro
            if (dataInicio > hoje) {
                erros.push('🚫 Não é permitido fazer lançamentos futuros');
            }

            // Não pode ser mais de 5 dias úteis anteriores
            if (dataInicio < hoje) {
                // Calcular dias úteis entre as datas
                let diasUteisAtras = 0;
                const tempDate = new Date(dataInicio);

                while (tempDate < hoje) {
                    tempDate.setDate(tempDate.getDate() + 1);
                    const dayOfWeek = tempDate.getDay();
                    // 0 = Domingo, 6 = Sábado
                    if (dayOfWeek !== 0 && dayOfWeek !== 6) {
                        diasUteisAtras++;
                    }
                }

                console.log('📊 Dias úteis atrás:', diasUteisAtras);

                if (diasUteisAtras > 5) {
                    erros.push('📅 Não é permitido fazer apontamentos com mais de 5 dias úteis anteriores à data atual');
                }
            }
        }

        // 3. VALIDAR DATA/HORA FINAL MAIOR QUE INICIAL
        if (formData.inpData && formData.inpHora && formData.inpDataFim && formData.inpHoraFim) {
            const dataHoraInicio = new Date(`${formData.inpData}T${formData.inpHora}`);
            const dataHoraFim = new Date(`${formData.inpDataFim}T${formData.inpHoraFim}`);

            console.log('🕒 Validando datas:', { inicio: dataHoraInicio, fim: dataHoraFim });

            if (dataHoraFim <= dataHoraInicio) {
                erros.push('⏰ Data/Hora final deve ser maior que inicial');
            }

            // 4. VALIDAR QUANTIDADE DE HORAS < 12
            const diferencaHoras = (dataHoraFim.getTime() - dataHoraInicio.getTime()) / (1000 * 60 * 60);
            console.log('⏱️ Diferença de horas:', diferencaHoras);

            if (diferencaHoras >= 12) {
                erros.push('⏱️ Apontamento não pode ter 12 horas ou mais. Faça outro apontamento para o período restante.');
            }
        }

        // 5. VERIFICAÇÃO DE TESTES EXCLUSIVOS REMOVIDA - sistema simplificado

        // 6. VERIFICAR STATUS DA OS
        if (formData.statusOS === 'TERMINADA') {
            erros.push('🚫 Esta OS está TERMINADA. Não é possível fazer novos lançamentos.');
        }

        // 6. VALIDAÇÕES ADICIONAIS (sem dependência de API por enquanto)

        // Verificar se é retrabalho e mostrar aviso
        if (formData.inpRetrabalho && formData.selCausaRetrabalho) {
            avisos.push(`🔄 Este apontamento está marcado como RETRABALHO (Causa: ${formData.selCausaRetrabalho})`);
        }

        console.log('✅ Todas as validações básicas concluídas');

        return { erros, avisos };
    };



    // Carregar dados iniciais dos dropdowns
    useEffect(() => {
        const loadInitialData = async () => {
            if (dadosInicaisCarregados) {
                console.log('⚠️ Dados iniciais já foram carregados, pulando...');
                return;
            }

            console.log('🚀 Iniciando carregamento dos dados iniciais...');
            setLoadingDropdowns(true);

            try {
                console.log('📋 Carregando tipos de máquina...');
                await loadTiposMaquina();
                console.log('✅ Tipos de máquina carregados');

                console.log('🔧 Tipos de atividade serão carregados quando tipo de máquina for selecionado');
                // Não carregar tipos de atividade inicialmente - eles dependem do tipo de máquina selecionado

                console.log('📄 Carregando descrições de atividade...');
                await loadDescricoesAtividade();
                console.log('✅ Descrições de atividade carregadas');

                console.log('🔄 Carregando causas de retrabalho...');
                await loadCausasRetrabalho();
                console.log('✅ Causas de retrabalho carregadas');

                console.log('🎯 Carregando categorias de máquina...');
                // Não precisa de user?.departamento e user?.setor aqui, o endpoint já filtra se o usuário não for ADMIN
                await loadCategoriasMaquina();
                console.log('✅ Categorias de máquina carregadas');

                setDadosInicaisCarregados(true);

            } catch (error) {
                console.error('❌ Erro no carregamento inicial:', error);
            } finally {
                setLoadingDropdowns(false);
                console.log('🏁 Carregamento inicial finalizado');
            }
        };

        loadInitialData();
    }, []);

    // Pré-preenchimento da OS agora é feito no DevelopmentTemplate

    // Detectar programação automaticamente quando vem da URL
    useEffect(() => {
        if (programacaoId && osFromUrl) {
            console.log('🎯 Detectando programação da URL:', { programacaoId, osFromUrl });
            // Simular a detecção de programação com os dados da URL
            setProgramacaoDetectada({
                programacao_id: parseInt(programacaoId),
                os_numero: osFromUrl,
                status_programacao: 'EM_ANDAMENTO',
                tem_programacao: true
            });
            setMostraOpcoesFinalizacao(true);
        }
    }, [programacaoId, osFromUrl]);

    // Estado para controlar se é a primeira vez que o tipo de máquina está sendo carregado
    const [tipoMaquinaAnterior, setTipoMaquinaAnterior] = useState<string>('');

    // Recarregar tipos de atividade quando tipo de máquina mudar
    useEffect(() => {
        if (formData.selMaq) {
            // Só limpar seleções se o tipo de máquina realmente mudou (não na primeira carga)
            if (tipoMaquinaAnterior && tipoMaquinaAnterior !== formData.selMaq) {
                console.log('🔄 Tipo de máquina mudou de', tipoMaquinaAnterior, 'para', formData.selMaq, '- limpando seleções dependentes');
                setFormData((prev: any) => ({ ...prev, selAtiv: '', selDescAtiv: '', categoriaSelecionada: '', subcategoriasSelecionadas: [] }));
            }

            // Atualizar o tipo de máquina anterior
            setTipoMaquinaAnterior(formData.selMaq);

            // Carregar tipos de atividade filtrados pelo tipo de máquina
            const tipoMaquinaSelecionado = tiposMaquina.find(tm => tm.nome_tipo === formData.selMaq);
            if (tipoMaquinaSelecionado) {
                console.log('🔄 Carregando tipos de atividade para tipo de máquina:', tipoMaquinaSelecionado.nome_tipo);
                loadTiposAtividade(tipoMaquinaSelecionado.id);

                // ✨ NOVO: Carregar todos os tipos específicos da categoria geral selecionada
                // CORREÇÃO: nome_tipo é a categoria geral (ex: "MAQUINA ROTATIVA CA")
                loadTiposPorCategoria(formData.selMaq);
            }
        } else {
            // Limpar tipos de atividade quando não há tipo de máquina selecionado
            console.log('🔄 Limpando tipos de atividade (nenhum tipo de máquina selecionado)');
            setTiposAtividade([]); // Limpar lista de atividades
            setFormData((prev: any) => ({ ...prev, selAtiv: '', selDescAtiv: '', categoriaSelecionada: '', subcategoriasSelecionadas: [] }));
            setTipoMaquinaAnterior('');
        }
    }, [formData.selMaq, tiposMaquina, user]); // Adicionado 'user' à lista de dependências

    // ✅ REMOVIDO: useEffect para recarregar descrições
    // Agora as descrições são carregadas uma vez no início e ficam sempre disponíveis
    // Não há relacionamento direto entre TipoAtividade e DescricaoAtividade

    // Carregar tipos de teste quando filtros mudarem
    useEffect(() => {
        console.log('🔍 useEffect tipos de teste executado:', {
            user: user?.primeiro_nome,
            departamento: user?.departamento,
            setor: user?.setor,
            selMaq: formData.selMaq
        });

        if (user && formData.selMaq) {
            const departamento = user.departamento;
            const setor = user.setor;
            console.log('✅ Condições atendidas, carregando tipos de teste...');
            loadTiposTeste(departamento, setor, formData.selMaq);
        } else {
            console.log('❌ Condições não atendidas:', {
                hasUser: !!user,
                hasSelMaq: !!formData.selMaq
            });
        }
    }, [formData.selMaq, user]);

    // Carregar testes exclusivos quando usuário estiver disponível
    useEffect(() => {
        console.log('🔍 useEffect testes exclusivos executado:', {
            user: user?.primeiro_nome,
            departamento: user?.departamento,
            setor: user?.setor
        });

        if (user && user.departamento && user.setor) {
            console.log('✅ Condições atendidas, carregando testes exclusivos...');
            loadTestesExclusivos(user.departamento, user.setor);
        } else {
            console.log('❌ Condições não atendidas para testes exclusivos:', {
                hasUser: !!user,
                hasDepartamento: !!user?.departamento,
                hasSetor: !!user?.setor
            });
        }
    }, [user]);

    // Carregar descrições de atividade automaticamente quando usuário estiver logado
    useEffect(() => {
        console.log('🔍 useEffect descrições de atividade executado:', {
            user: user?.primeiro_nome,
            departamento: user?.departamento,
            setor: user?.setor,
            dadosJaCarregados: dadosInicaisCarregados
        });

        // Só carregar se os dados iniciais ainda não foram carregados
        if (user && user.departamento && user.setor && !dadosInicaisCarregados) {
            console.log('✅ Condições atendidas para carregar descrições (dados iniciais não carregados ainda)');
            loadDescricoesAtividade();
        } else {
            console.log('❌ Condições não atendidas para descrições:', {
                hasUser: !!user,
                hasDepartamento: !!user?.departamento,
                hasSetor: !!user?.setor,
                dadosJaCarregados: dadosInicaisCarregados
            });
        }
    }, [user?.departamento, user?.setor, user, dadosInicaisCarregados]);

    // useEffect para limpar categorias quando tipo de máquina mudar para vazio
    useEffect(() => {
        if (!formData.selMaq && tipoMaquinaAnterior) {
            console.log('🔄 Tipo de máquina removido - limpando categorias');
            setFormData((prev: any) => ({ ...prev, categoriaSelecionada: '', subcategoriasSelecionadas: [] }));
            setSubcategoriasDisponiveis([]);
        }
    }, [formData.selMaq, tipoMaquinaAnterior]);

    // useEffect para carregar subcategorias quando categoria mudar (ou for pré-selecionada)
    useEffect(() => {
        if (formData.categoriaSelecionada && user?.departamento && user?.setor) {
            console.log('🔄 Carregando subcategorias para categoria:', formData.categoriaSelecionada);
            loadSubcategoriasPorCategoria(formData.categoriaSelecionada, user.departamento, user.setor);
        } else {
            setSubcategoriasDisponiveis([]);
        }
    }, [formData.categoriaSelecionada, user]);

    // useEffects para detecção automática e testes finalizados removidos - sistema simplificado

    // Função para resetar formulário completo
    const resetarFormulario = () => {
        console.log('🔄 Resetando formulário...');

        // Reset do formData
        setFormData({
            inpNumOS: '',
            statusOS: '',
            inpCliente: '',
            inpEquipamento: '',
            selMaq: '',
            selAtiv: '',
            selDescAtiv: '',
            inpData: '',
            inpHora: '',
            observacao: '',
            resultadoGlobal: '',
            inpDataFim: '',
            inpHoraFim: '',

            // Campos da estrutura hierárquica
            categoriaSelecionada: '',
            subcategoriasSelecionadas: [],

            supervisor_horas_orcadas: 0,
            supervisor_testes_iniciais: false,
            supervisor_testes_parciais: false,
            supervisor_testes_finais: false
        });

        // Reset dos estados
        setOsEncontrada(null);
        setMensagemOS('');
        setLoadingOS(false);
        setLoadingDropdowns(false);
        setDadosInicaisCarregados(false); // Reset do flag de carregamento
        setTiposMaquina([]); // Recarregar tipos de máquina
        setTiposAtividade([]); // Recarregar tipos de atividade
        setDescricoesAtividade([]); // Recarregar descrições de atividade
        setCausasRetrabalho([]); // Recarregar causas de retrabalho
        setTiposTeste([]); // Limpar tipos de teste
        setTiposTesteOriginais([]); // Limpar tipos de teste originais
        setTiposTesteUnicos([]); // Limpar tipos de teste únicos
        setFiltroTipoTeste('');
        setFiltroNomeTeste('');
        setFiltroCategoria('');
        setFiltroSubcategoria('');
        setCategoriasMaquina([]); // Limpar categorias de máquina
        setSubcategoriasDisponiveis([]); // Limpar subcategorias disponíveis
        setTestesExclusivos([]); // Limpar testes exclusivos
        setTestesExclusivosSelecionados({}); // Limpar testes exclusivos selecionados
        setTestesSelecionados({}); // Limpar testes selecionados

        // Recarregar dados iniciais para popular os dropdowns novamente
        const loadInitialDataAfterReset = async () => {
            setLoadingDropdowns(true);
            try {
                await loadTiposMaquina();
                await loadTiposAtividade();
                await loadDescricoesAtividade();
                await loadCausasRetrabalho();
                await loadCategoriasMaquina();
            } catch (error) {
                console.error('Erro ao recarregar dados após reset:', error);
            } finally {
                setLoadingDropdowns(false);
            }
        };
        loadInitialDataAfterReset();

        console.log('✅ Formulário resetado com sucesso');
    };

    // 🎯 USEEFFECT PARA PREENCHER DADOS DA PENDÊNCIA
    useEffect(() => {
        if (dadosPreenchidos && pendenciaParaResolver) {
            console.log('📋 Preenchendo formulário com dados da pendência:', dadosPreenchidos);

            // Preencher campos do formulário
            setFormData(prevData => ({
                ...prevData,
                ...dadosPreenchidos
            }));

            // Buscar dados completos da OS automaticamente
            if (dadosPreenchidos.inpNumOS) {
                console.log('🔍 Buscando dados completos da OS:', dadosPreenchidos.inpNumOS);
                buscarOS(dadosPreenchidos.inpNumOS);
            }

            // Mostrar notificação
            alert(`📋 Formulário preenchido com dados da pendência #${pendenciaParaResolver.id}\n\nOS: ${dadosPreenchidos.inpNumOS}\nCliente: ${dadosPreenchidos.inpCliente}\n\nProssiga com o apontamento para resolver a pendência.`);
        }
    }, [dadosPreenchidos, pendenciaParaResolver]);

    // 🎯 USEEFFECT PARA PREENCHER DADOS DA PROGRAMAÇÃO
    useEffect(() => {
        if (dadosPreenchidos && programacaoParaIniciar) {
            console.log('📋 Preenchendo formulário com dados da programação:', dadosPreenchidos);

            // Preencher campos do formulário
            setFormData(prevData => ({
                ...prevData,
                ...dadosPreenchidos
            }));

            // Buscar dados completos da OS automaticamente
            if (dadosPreenchidos.inpNumOS) {
                console.log('🔍 Buscando dados completos da OS:', dadosPreenchidos.inpNumOS);
                buscarOS(dadosPreenchidos.inpNumOS);
            }

            // Mostrar notificação
            alert(`🚀 Formulário preenchido com dados da programação #${programacaoParaIniciar.id}\n\nOS: ${dadosPreenchidos.inpNumOS}\nCliente: ${dadosPreenchidos.inpCliente}\n\nProssiga com o apontamento para executar a programação.`);
        }
    }, [dadosPreenchidos, programacaoParaIniciar]);

    // 🎯 FUNÇÃO PARA VERIFICAR PROGRAMAÇÃO ATIVA POR OS
    const verificarProgramacaoPorOS = async (numeroOS: string) => {
        if (!numeroOS || numeroOS.length < 3) {
            setProgramacaoDetectada(null);
            setMostraOpcoesFinalizacao(false);
            return;
        }

        try {
            setLoadingProgramacao(true);
            console.log(`🔍 Verificando programação para OS: ${numeroOS}`);

            const response = await api.get(`/desenvolvimento/verificar-programacao-os/${numeroOS}`);

            if (response.data.tem_programacao) {
                console.log('✅ Programação detectada:', response.data);
                setProgramacaoDetectada(response.data);
                setMostraOpcoesFinalizacao(true);
            } else {
                console.log('ℹ️ Nenhuma programação ativa encontrada');
                setProgramacaoDetectada(null);
                setMostraOpcoesFinalizacao(false);
            }
        } catch (error) {
            console.error('❌ Erro ao verificar programação:', error);
            setProgramacaoDetectada(null);
            setMostraOpcoesFinalizacao(false);
        } finally {
            setLoadingProgramacao(false);
        }
    };

    // 🎯 FUNÇÃO PARA VERIFICAR SE PROGRAMAÇÃO FOI FINALIZADA
    const verificarProgramacaoFinalizada = async (numeroOS: string) => {
        try {
            // Buscar programações da OS
            const response = await api.get(`/desenvolvimento/programacao?os_numero=${numeroOS}`);

            if (response.data && response.data.length > 0) {
                const programacoes = response.data;

                // Verificar se alguma programação está em andamento
                const programacaoAtiva = programacoes.find((prog: any) =>
                    prog.status === 'PROGRAMADA' || prog.status === 'EM_ANDAMENTO'
                );

                if (programacaoAtiva) {
                    // Perguntar se a programação foi finalizada
                    const finalizada = window.confirm(
                        `🎯 PROGRAMAÇÃO DETECTADA!\n\n` +
                        `OS: ${numeroOS}\n` +
                        `Responsável: ${programacaoAtiva.responsavel_nome || 'N/A'}\n` +
                        `Status: ${programacaoAtiva.status}\n\n` +
                        `A programação foi FINALIZADA com este apontamento?`
                    );

                    if (finalizada) {
                        // Atualizar status da programação para FINALIZADA
                        await api.patch(`/desenvolvimento/programacao/${programacaoAtiva.id}/finalizar`, {
                            status: 'FINALIZADA',
                            data_finalizacao: new Date().toISOString(),
                            finalizada_por: user?.id
                        });

                        alert(`✅ Programação marcada como FINALIZADA!`);
                    }
                }
            }
        } catch (error) {
            console.error('Erro ao verificar programação:', error);
            // Não bloquear o fluxo se a verificação falhar
        }
    };

    // 🎯 FUNÇÃO PARA FINALIZAR ATIVIDADE
    const finalizarAtividade = async () => {
        if (!programacaoDetectada?.programacao_id) {
            alert('❌ Nenhuma programação detectada para finalizar atividade');
            return;
        }

        const descricaoAtividade = prompt('📝 Descreva a atividade que foi finalizada:');
        if (!descricaoAtividade) return;

        try {
            const dados = {
                apontamento_id: 1, // Será o ID do apontamento atual quando salvo
                programacao_id: programacaoDetectada.programacao_id,
                descricao_atividade: descricaoAtividade
            };

            const response = await api.post('/desenvolvimento/finalizar-atividade', dados);

            alert(`✅ ${response.data.message}`);

            // Atualizar status da programação detectada
            setProgramacaoDetectada({
                ...programacaoDetectada,
                status_programacao: response.data.status_programacao
            });

        } catch (error: any) {
            console.error('❌ Erro ao finalizar atividade:', error);
            alert(`❌ Erro ao finalizar atividade: ${error.response?.data?.detail || error.message}`);
        }
    };

    // 🎯 FUNÇÃO PARA FINALIZAR PROGRAMAÇÃO
    const finalizarProgramacao = async () => {
        if (!programacaoDetectada?.programacao_id) {
            alert('❌ Nenhuma programação detectada para finalizar');
            return;
        }

        const observacoesFinais = prompt('📝 Observações finais da programação (opcional):') || '';

        const confirmacao = confirm(
            '🏁 Tem certeza que deseja finalizar esta programação?\n\n' +
            'Isso enviará a programação para aprovação do supervisor.'
        );

        if (!confirmacao) return;

        try {
            const dados = {
                programacao_id: programacaoDetectada.programacao_id,
                observacoes_finais: observacoesFinais
            };

            const response = await api.post('/desenvolvimento/finalizar-programacao', dados);

            alert(`🎉 ${response.data.message}`);

            // Limpar detecção de programação após finalizar
            setProgramacaoDetectada(null);
            setMostraOpcoesFinalizacao(false);

        } catch (error: any) {
            console.error('❌ Erro ao finalizar programação:', error);
            alert(`❌ Erro ao finalizar programação: ${error.response?.data?.detail || error.message}`);
        }
    };

    // Funções para salvar apontamento
    const handleSaveApontamento = async () => {
        try {
            setLoadingDropdowns(true);
            console.log('💾 Iniciando salvamento do apontamento...');

            // EXECUTAR TODAS AS VALIDAÇÕES
            const { erros, avisos } = await validarRegrasNegocio();

            // Mostrar avisos se houver
            if (avisos.length > 0) {
                const mensagemAvisos = avisos.join('\n\n');
                alert(`⚠️ AVISOS:\n\n${mensagemAvisos}`);
            }

            // Parar se houver erros
            if (erros.length > 0) {
                const mensagemErros = erros.join('\n\n');
                alert(`❌ ERROS ENCONTRADOS:\n\n${mensagemErros}`);
                return;
            }

            console.log('✅ Todas as validações passaram');

            // Preparar dados para envio
            const apontamentoData = {
                numero_os: formData.inpNumOS,
                status_os: formData.statusOS,
                cliente: formData.inpCliente,
                equipamento: formData.inpEquipamento || 'Não informado',
                tipo_maquina: formData.selMaq,
                tipo_atividade: formData.selAtiv,
                descricao_atividade: formData.selDescAtiv,
                categoria_maquina: formData.categoriaSelecionada,
                subcategorias_maquina: formData.subcategoriasSelecionadas,
                data_inicio: formData.inpData,
                hora_inicio: formData.inpHora,
                data_fim: formData.inpDataFim,
                hora_fim: formData.inpHoraFim,
                retrabalho: formData.inpRetrabalho || false,
                causa_retrabalho: formData.selCausaRetrabalho,
                observacao_geral: formData.observacao,
                resultado_global: formData.resultadoGlobal,
                usuario_id: user?.id,
                departamento: user?.departamento,
                setor: user?.setor,
                testes_selecionados: testesSelecionados,
                testes_exclusivos_selecionados: testesExclusivosSelecionados,
                tipo_salvamento: 'APONTAMENTO',
                supervisor_config: {
                    horas_orcadas: formData.supervisor_horas_orcadas,
                    testes_iniciais: formData.supervisor_testes_iniciais,
                    testes_parciais: formData.supervisor_testes_parciais,
                    testes_finais: formData.supervisor_testes_finais
                },
                // Incluir ID da pendência se estiver resolvendo uma
                pendencia_origem_id: pendenciaParaResolver?.id || null
            };

            const response = await api.post('/desenvolvimento/os/apontamentos', apontamentoData);

            // Se estava resolvendo uma pendência, finalizá-la
            if (pendenciaParaResolver) {
                try {
                    await api.patch(`/desenvolvimento/pendencias/${pendenciaParaResolver.id}/resolver`, {
                        solucao_aplicada: formData.observacao || 'Resolvida via apontamento',
                        observacoes_fechamento: `Pendência resolvida através do apontamento #${response.data.id}`,
                        status: 'FECHADA'
                    });

                    console.log('✅ Pendência finalizada automaticamente');

                    // Chamar callback para limpar estado
                    if (onPendenciaResolvida) {
                        onPendenciaResolvida();
                    }
                } catch (errorPendencia) {
                    console.error('❌ Erro ao finalizar pendência:', errorPendencia);
                    // Não bloquear o fluxo se a finalização da pendência falhar
                }
            }

            // Se estava executando uma programação, marcar como em andamento
            if (programacaoParaIniciar) {
                try {
                    console.log('🚀 Marcando programação como em andamento...');

                    // Chamar callback para limpar estado
                    if (onProgramacaoIniciada) {
                        onProgramacaoIniciada();
                    }
                } catch (errorProgramacao) {
                    console.error('❌ Erro ao processar programação:', errorProgramacao);
                    // Não bloquear o fluxo se o processamento da programação falhar
                }
            }

            // Se vem de uma programação via URL, finalizar a programação
            if (programacaoId && !response.data.programacao_finalizada) {
                try {
                    await api.patch(`/pcp/programacoes/${programacaoId}/status`, {
                        status: 'CONCLUIDA',
                        observacoes_finais: formData.observacao || 'Programação finalizada via apontamento'
                    });
                    console.log('✅ Programação finalizada via URL com observações do apontamento');
                } catch (errorProgramacao) {
                    console.error('❌ Erro ao finalizar programação via URL:', errorProgramacao);
                }
            }

            // Se há programação detectada (não via URL), também finalizar
            if (programacaoDetectada && !response.data.programacao_finalizada && !programacaoId) {
                try {
                    await api.patch(`/pcp/programacoes/${programacaoDetectada.programacao_id}/status`, {
                        status: 'CONCLUIDA',
                        observacoes_finais: formData.observacao || 'Programação finalizada via apontamento'
                    });
                    console.log('✅ Programação detectada finalizada com observações do apontamento');
                } catch (errorProgramacao) {
                    console.error('❌ Erro ao finalizar programação detectada:', errorProgramacao);
                }
            }

            // Verificar se programação foi finalizada automaticamente
            let mensagem = `✅ Apontamento salvo com sucesso! OS: ${response.data.numero_os || response.data.os_numero}`;

            if (response.data.programacao_finalizada || programacaoId) {
                mensagem += '\n🎯 Programação finalizada automaticamente!';
                // Limpar detecção de programação
                setProgramacaoDetectada(null);
                setMostraOpcoesFinalizacao(false);
            }

            if (pendenciaParaResolver) {
                mensagem += `\n📋 Pendência #${pendenciaParaResolver.id} resolvida!`;
            }

            if (programacaoParaIniciar) {
                mensagem += `\n🚀 Programação #${programacaoParaIniciar.id} iniciada!`;
            }

            alert(mensagem);

            // RESET COMPLETO DA PÁGINA
            resetarFormulario();

        } catch (error) {
            console.error('Erro ao salvar apontamento:', error);
            alert('Erro ao salvar apontamento. Verifique os dados e tente novamente.');
        } finally {
            setLoadingDropdowns(false);
        }
    };

    const handleSaveWithPendencia = async () => {
        try {
            setLoadingDropdowns(true);
            console.log('📋 Iniciando salvamento com pendência...');

            // EXECUTAR TODAS AS VALIDAÇÕES
            const { erros, avisos } = await validarRegrasNegocio();

            // Mostrar avisos se houver
            if (avisos.length > 0) {
                const mensagemAvisos = avisos.join('\n\n');
                alert(`⚠️ AVISOS:\n\n${mensagemAvisos}`);
            }

            // Parar se houver erros
            if (erros.length > 0) {
                const mensagemErros = erros.join('\n\n');
                alert(`❌ ERROS ENCONTRADOS:\n\n${mensagemErros}`);
                return;
            }

            console.log('✅ Todas as validações passaram para pendência');

            // Preparar dados do apontamento com pendência
            const apontamentoData = {
                numero_os: formData.inpNumOS,
                status_os: formData.statusOS,
                cliente: formData.inpCliente,
                equipamento: formData.inpEquipamento || 'Não informado',
                tipo_maquina: formData.selMaq,
                tipo_atividade: formData.selAtiv,
                descricao_atividade: formData.selDescAtiv,
                categoria_maquina: formData.categoriaSelecionada,
                subcategorias_maquina: formData.subcategoriasSelecionadas,
                data_inicio: formData.inpData,
                hora_inicio: formData.inpHora,
                data_fim: formData.inpDataFim,
                hora_fim: formData.inpHoraFim,
                retrabalho: formData.inpRetrabalho || false,
                causa_retrabalho: formData.selCausaRetrabalho,
                observacao_geral: formData.observacao,
                resultado_global: formData.resultadoGlobal,
                usuario_id: user?.id,
                departamento: user?.departamento,
                setor: user?.setor,
                testes_selecionados: testesSelecionados,
                testes_exclusivos_selecionados: testesExclusivosSelecionados,
                tipo_salvamento: 'APONTAMENTO_COM_PENDENCIA',
                supervisor_config: {
                    horas_orcadas: formData.supervisor_horas_orcadas,
                    testes_iniciais: formData.supervisor_testes_iniciais,
                    testes_parciais: formData.supervisor_testes_parciais,
                    testes_finais: formData.supervisor_testes_finais
                }
            };

            console.log('📋 Dados do apontamento com pendência:', apontamentoData);

            const response = await api.post('/save-apontamento-with-pendencia', apontamentoData);

            if (response.data) {
                console.log('✅ Apontamento e pendência salvos:', response.data);
                alert(`✅ Apontamento salvo com sucesso!\n📋 Pendência criada: #${response.data.numero_pendencia || 'N/A'}`);

                // RESET COMPLETO DA PÁGINA
                resetarFormulario();
            }

        } catch (error) {
            console.error('❌ Erro ao salvar apontamento com pendência:', error);
            alert('❌ Erro ao salvar apontamento com pendência. Tente novamente.');
        } finally {
            setLoadingDropdowns(false);
        }
    };

    return (
        <div className="space-y-6">
            {/* Progress Indicator */}
            <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
                <div className="flex items-center justify-between mb-4">
                    <h2 className="text-lg font-semibold text-gray-900">Progresso do Apontamento</h2>
                    <span className="text-sm text-gray-500">Etapas concluídas</span>
                </div>
                <div className="flex items-center space-x-4">
                    <div className="flex items-center">
                        <div className={`w-8 h-8 rounded-full flex items-center justify-center ${ComponentesEtapa1.length > 0 ? 'bg-green-500' : 'bg-gray-300'}`}>
                            <span className="text-white text-sm font-medium">1</span>
                        </div>
                        <span className={`ml-2 text-sm font-medium ${ComponentesEtapa1.length > 0 ? 'text-gray-900' : 'text-gray-500'}`}>Dados Básicos</span>
                    </div>
                    <div className="flex-1 h-px bg-gray-300"></div>
                    <div className="flex items-center">
                        <div className={`w-8 h-8 rounded-full flex items-center justify-center ${ComponentesEtapa2.length > 0 ? 'bg-green-500' : 'bg-gray-300'}`}>
                            <span className="text-white text-sm font-medium">2</span>
                        </div>
                        <span className={`ml-2 text-sm font-medium ${ComponentesEtapa2.length > 0 ? 'text-gray-900' : 'text-gray-500'}`}>Detalhes</span>
                    </div>
                    <div className="flex-1 h-px bg-gray-300"></div>
                    <div className="flex items-center">
                        <div className="w-8 h-8 bg-gray-300 rounded-full flex items-center justify-center">
                            <span className="text-gray-600 text-sm font-medium">3</span>
                        </div>
                        <span className="ml-2 text-sm font-medium text-gray-500">Finalização</span>
                    </div>
                </div>
            </div>

            {/* ETAPA 1: DADOS BÁSICOS E TESTES - SEMPRE MOSTRAR */}
            {(true) && (
                <div className="bg-white rounded-lg shadow-sm border border-gray-200">
                    <div className="px-6 py-4 border-b border-gray-200 bg-gradient-to-r from-blue-50 to-indigo-50">
                        <div className="flex items-center justify-between">
                            <div className="flex items-center">
                                <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center mr-3">
                                    <span className="text-white font-bold text-sm">1</span>
                                </div>
                                <div>
                                    <h3 className="text-lg font-semibold text-gray-900">Dados Básicos e Testes</h3>
                                    <p className="text-sm text-gray-600">Informações da OS, equipamento e testes específicos</p>
                                </div>
                            </div>
                            <button
                                onClick={() => {
                                    setFormData({
                                         inpNumOS: '',
                                         statusOS: '',
                                         inpCliente: '',
                                         inpEquipamento: '',
                                         selMaq: '',
                                         selAtiv: '',
                                         selDescAtiv: '',
                                         inpData: '',
                                         inpHora: '',
                                         observacao: '',
                                         resultadoGlobal: '',
                                         inpDataFim: '',
                                         inpHoraFim: '',
                                         categoriaSelecionada: '',
                                         subcategoriasSelecionadas: [],
                                         supervisor_horas_orcadas: 0,
                                         supervisor_testes_iniciais: false,
                                         supervisor_testes_parciais: false,
                                         supervisor_testes_finais: false
                                     });
                                    // Reset test results and observations
                                    Object.keys(testResults).forEach(testId => {
                                        onTestResultChange(testId, '');
                                        onTestCheckboxChange(testId, false);
                                        onTestObservationChange(testId, '');
                                    });
                                    // Adicionar reset de estados de filtros e testes aqui se necessário
                                    setOsEncontrada(null);
                                    setMensagemOS('');
                                    setLoadingOS(false);
                                    setLoadingDropdowns(false);
                                    setTiposTeste([]);
                                    setTiposTesteOriginais([]);
                                    setTiposTesteUnicos([]);
                                    setFiltroTipoTeste('');
                                    setFiltroNomeTeste('');
                                    setFiltroCategoria('');
                                    setFiltroSubcategoria('');
                                    setCategoriasUnicas([]); // Limpar categorias únicas dos testes
                                    setTestesExclusivos([]);
                                    setTestesExclusivosSelecionados({});
                                    setTestesSelecionados({}); // Limpar testes selecionados
                                    setCategoriasMaquina([]); // Limpar categorias de máquina
                                    setSubcategoriasDisponiveis([]); // Limpar subcategorias disponíveis
                                    // Recarregar os dados iniciais dos dropdowns
                                    // loadInitialData(); // Chamar a função de carregamento inicial
                                    resetarFormulario(); // Usar a função completa de reset
                                }}
                                className="px-4 py-2 bg-red-500 text-white text-sm rounded hover:bg-red-600 transition-colors"
                                title="Limpar todos os campos"
                            >
                                🗑️ Limpar Formulário
                            </button>
                        </div>
                    </div>
                    <div className="p-6">
                        {/* Formulário básico sempre visível */}
                        {(
                            <div className="space-y-6">
                                {/* Dados da OS */}
                                <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                                    <div>
                                        <label className="block text-sm font-medium text-gray-700 mb-2">📋 Número da OS</label>
                                        <div className="relative">
                                            <input
                                                type="text"
                                                value={formData.inpNumOS || ''}
                                                onChange={(e) => {
                                                    let valor = e.target.value;

                                                    // VALIDAÇÃO: Apenas números, máximo 5 dígitos
                                                    valor = valor.replace(/[^0-9]/g, '').slice(0, 5);

                                                    setFormData({ ...formData, inpNumOS: valor });

                                                    // Buscar OS e verificar programação automaticamente
                                                    if (valor.length >= 3) {
                                                        const timeoutId = setTimeout(() => {
                                                            // Verificar programação primeiro
                                                            verificarProgramacaoPorOS(valor);

                                                            // Buscar OS se tiver 5 dígitos
                                                            if (valor.length === 5) {
                                                                buscarOS(valor);
                                                            }
                                                        }, 800); // 800ms de delay

                                                        return () => clearTimeout(timeoutId);
                                                    } else {
                                                        setOsEncontrada(null);
                                                        setMensagemOS(valor.length > 0 && valor.length < 5 ? 'OS deve ter exatamente 5 dígitos' : '');
                                                        setProgramacaoDetectada(null);
                                                        setMostraOpcoesFinalizacao(false);
                                                    }
                                                }}
                                                onBlur={(e) => {
                                                    // Buscar também quando o campo perde o foco
                                                    if (e.target.value.length === 5) {
                                                        buscarOS(e.target.value);
                                                    }
                                                }}
                                                className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 ${
                                                    osEncontrada === true
                                                        ? 'border-green-500 focus:ring-green-500 bg-green-50'
                                                        : osEncontrada === false
                                                        ? 'border-orange-500 focus:ring-orange-500 bg-orange-50'
                                                        : 'border-gray-300 focus:ring-blue-500'
                                                }`}
                                                placeholder="Ex: 12345 (5 dígitos)"
                                                maxLength={5}
                                                disabled={loadingOS}
                                            />
                                            {loadingOS && (
                                                <div className="absolute right-3 top-1/2 transform -translate-y-1/2">
                                                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
                                                </div>
                                            )}
                                        </div>
                                        {mensagemOS && (
                                            <div className={`mt-1 text-xs ${
                                                osEncontrada === true
                                                    ? 'text-green-600'
                                                    : osEncontrada === false
                                                    ? 'text-orange-600'
                                                    : 'text-blue-600'
                                            }`}>
                                                {mensagemOS}
                                            </div>
                                        )}
                                    </div>
                                    <div>
                                        <label className="block text-sm font-medium text-gray-700 mb-2">📊 Status OS</label>
                                        {osEncontrada && formData.statusOS ? (
                                            // Campo somente leitura quando OS foi encontrada e tem status
                                            <>
                                                <input
                                                    type="text"
                                                    value={formData.statusOS || ''}
                                                    readOnly
                                                    className="w-full px-3 py-2 border border-green-500 rounded-md bg-green-50 text-gray-700 focus:outline-none focus:ring-2 focus:ring-green-500"
                                                />
                                                <div className="mt-1 text-sm text-green-600">
                                                    ✅ Do sistema
                                                </div>
                                            </>
                                        ) : (
                                            // Select normal quando OS não foi encontrada ou não tem status
                                            <select
                                                value={formData.statusOS || ''}
                                                onChange={(e) => setFormData({ ...formData, statusOS: e.target.value })}
                                                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                                            >
                                                <option value="">Selecione o status</option>
                                                <option value="ABERTA">Aberta</option>
                                                <option value="EM_ANDAMENTO">Em Andamento</option>
                                                <option value="AGUARDANDO_PECA">Aguardando Peça</option>
                                                <option value="AGUARDANDO_CLIENTE">Aguardando Cliente</option>
                                                <option value="FINALIZADA">Finalizada</option>
                                                <option value="CANCELADA">Cancelada</option>
                                            </select>
                                        )}
                                    </div>
                                    <div>
                                        <label className="block text-sm font-medium text-gray-700 mb-2">🏢 Cliente</label>
                                        {osBloqueadaParaApontamento ? (
                                            <div className="w-full px-3 py-2 border border-gray-300 rounded-md bg-gray-50 text-gray-700">
                                                {formData.inpCliente || 'Cliente não informado'}
                                            </div>
                                        ) : (
                                            <input
                                                type="text"
                                                value={formData.inpCliente || ''}
                                                onChange={(e) => setFormData({ ...formData, inpCliente: e.target.value })}
                                                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                                                placeholder="Nome do cliente"
                                            />
                                        )}
                                    </div>
                                    <div>
                                        <label className="block text-sm font-medium text-gray-700 mb-2">⚙️ Equipamento</label>
                                        {osBloqueadaParaApontamento ? (
                                            <div className="w-full px-3 py-2 border border-gray-300 rounded-md bg-gray-50 text-gray-700">
                                                {formData.inpEquipamento || 'Equipamento não informado'}
                                            </div>
                                        ) : (
                                            <input
                                                type="text"
                                                value={formData.inpEquipamento || ''}
                                                onChange={(e) => setFormData({ ...formData, inpEquipamento: e.target.value })}
                                                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                                                placeholder="Descrição do equipamento"
                                            />
                                        )}
                                    </div>
                                </div>

                                {/* 🎯 PROGRAMAÇÃO DETECTADA */}
                                {loadingProgramacao && (
                                    <div className="bg-blue-50 p-4 rounded-lg border border-blue-200">
                                        <div className="flex items-center">
                                            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600 mr-2"></div>
                                            <span className="text-blue-800">🔍 Verificando programação para esta OS...</span>
                                        </div>
                                    </div>
                                )}

                                {programacaoDetectada && (
                                    <div className="bg-green-50 p-4 rounded-lg border border-green-200">
                                        <h4 className="font-semibold text-green-800 mb-3 flex items-center">
                                            🎯 Programação Detectada!
                                            <span className={`ml-2 px-2 py-1 rounded text-xs ${
                                                programacaoDetectada.status_programacao === 'PROGRAMADA' ? 'bg-yellow-100 text-yellow-800' :
                                                programacaoDetectada.status_programacao === 'EM_ANDAMENTO' ? 'bg-blue-100 text-blue-800' :
                                                'bg-gray-100 text-gray-800'
                                            }`}>
                                                {programacaoDetectada.status_programacao}
                                            </span>
                                        </h4>

                                        <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mb-4 text-sm">
                                            <div>
                                                <strong>📋 OS:</strong> {programacaoDetectada.os_numero}
                                            </div>
                                            <div>
                                                <strong>👤 Responsável:</strong> {programacaoDetectada.responsavel_nome}
                                            </div>
                                            {programacaoDetectada.inicio_previsto && (
                                                <div>
                                                    <strong>📅 Início:</strong> {new Date(programacaoDetectada.inicio_previsto).toLocaleString()}
                                                </div>
                                            )}
                                            {programacaoDetectada.fim_previsto && (
                                                <div>
                                                    <strong>🏁 Fim:</strong> {new Date(programacaoDetectada.fim_previsto).toLocaleString()}
                                                </div>
                                            )}
                                        </div>

                                        {programacaoDetectada.observacoes && (
                                            <div className="mb-4 p-3 bg-white rounded border">
                                                <strong>📝 Observações:</strong>
                                                <div className="mt-1 text-sm text-gray-700 whitespace-pre-line">
                                                    {programacaoDetectada.observacoes}
                                                </div>
                                            </div>
                                        )}

                                        {mostraOpcoesFinalizacao && (
                                            <div className="border-t pt-3">
                                                <p className="text-green-700 mb-3 font-medium">
                                                    🎮 Como deseja finalizar ao concluir este apontamento?
                                                </p>

                                                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                                                    <button
                                                        onClick={finalizarAtividade}
                                                        className="bg-yellow-500 text-white px-4 py-2 rounded hover:bg-yellow-600 transition-colors"
                                                    >
                                                        ✅ Finalizar Atividade
                                                        <div className="text-xs text-yellow-100 mt-1">
                                                            (Apenas esta tarefa específica)
                                                        </div>
                                                    </button>

                                                    <button
                                                        onClick={finalizarProgramacao}
                                                        className="bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600 transition-colors"
                                                    >
                                                        🏁 Finalizar Programação
                                                        <div className="text-xs text-green-100 mt-1">
                                                            (Toda a programação completa)
                                                        </div>
                                                    </button>
                                                </div>
                                            </div>
                                        )}
                                    </div>
                                )}

                                {/* Seleções - DADOS DO BANCO */}
                                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                                    <div>
                                        <label className="block text-sm font-medium text-gray-700 mb-2">🔧 Tipo de Máquina</label>
                                        <select
                                            value={formData.selMaq || ''}
                                            onChange={async (e) => {
                                                const novoTipo = e.target.value;
                                                setFormData({
                                                    ...formData,
                                                    selMaq: novoTipo,
                                                    selAtiv: '', // Limpar tipo de atividade
                                                    selDescAtiv: '', // Limpar descrição de atividade
                                                    categoriaSelecionada: '', // Limpar categoria selecionada
                                                    subcategoriasSelecionadas: [] // Limpar subcategorias
                                                });

                                                // Buscar todos os tipos específicos da categoria geral selecionada
                                                if (novoTipo) {
                                                    // CORREÇÃO: novoTipo é a categoria geral (ex: "MAQUINA ROTATIVA CA")
                                                    loadTiposPorCategoria(novoTipo);
                                                }
                                            }}
                                            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                                            disabled={loadingDropdowns}
                                        >
                                            <option value="">
                                                {loadingDropdowns ? 'Carregando...' : 'Selecione o tipo de máquina'}
                                            </option>
                                            {tiposMaquina.map((tipo, index) => (
                                                <option key={`maq-${tipo.id}-${index}`} value={tipo.nome_tipo}>
                                                    {tipo.nome_tipo}
                                                </option>
                                            ))}
                                        </select>
                                    </div>
                                    <div>
                                        <label className="block text-sm font-medium text-gray-700 mb-2">📝 Tipo de Atividade</label>
                                        <select
                                            value={formData.selAtiv || ''}
                                            onChange={(e) => setFormData({ ...formData, selAtiv: e.target.value, selDescAtiv: '' })}
                                            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                                            disabled={loadingDropdowns || !formData.selMaq}
                                        >
                                            <option value="">
                                                {!formData.selMaq
                                                    ? 'Selecione primeiro o tipo de máquina'
                                                    : loadingDropdowns
                                                    ? 'Carregando...'
                                                    : 'Selecione a atividade'
                                                }
                                            </option>
                                            {tiposAtividade.map((tipo, index) => (
                                                <option key={`ativ-${tipo.id}-${index}`} value={tipo.nome_tipo}>
                                                    {tipo.nome_tipo}
                                                </option>
                                            ))}
                                        </select>
                                    </div>
                                    <div>
                                        <label className="block text-sm font-medium text-gray-700 mb-2">
                                            📄 Descrição da Atividade
                                            <span className="text-xs text-gray-500">
                                                ({descricoesAtividade.length} opções)
                                            </span>
                                        </label>
                                        <select
                                            value={formData.selDescAtiv || ''}
                                            onChange={(e) => {
                                                console.log('📄 Selecionando descrição:', e.target.value);
                                                setFormData({ ...formData, selDescAtiv: e.target.value });
                                            }}
                                            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                                            disabled={loadingDropdowns}
                                        >
                                            <option value="">
                                                {loadingDropdowns
                                                    ? 'Carregando...'
                                                    : 'Selecione a descrição'
                                                }
                                            </option>
                                            {descricoesAtividade.map((desc, index) => {
                                                console.log('📄 Renderizando descrição:', desc);
                                                return (
                                                    <option key={`desc-${desc.id}-${index}`} value={desc.descricao}>
                                                        {desc.codigo} - {desc.descricao}
                                                    </option>
                                                );
                                            })}
                                        </select>
                                    </div>
                                </div>

                                {/* Card de Categorias e Subcategorias */}
                                {formData.selMaq && (
                                    <div className="bg-gradient-to-r from-purple-50 to-blue-50 border border-purple-200 rounded-lg p-4 mt-4">
                                        <h4 className="text-sm font-medium text-purple-900 mb-3 flex items-center">
                                            🎯 Categorias e Subcategorias da Máquina
                                            <span className="ml-2 text-xs bg-purple-100 text-purple-700 px-2 py-1 rounded-full">
                                                {formData.selMaq}
                                            </span>
                                        </h4>

                                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                            {/* Categoria da Máquina */}
                                            <div className="bg-white rounded-lg border border-purple-200 p-3">
                                                <div className="text-sm font-semibold text-purple-800 mb-2">
                                                    🎯 Tipos de Máquina da Categoria
                                                    <span className="text-xs text-gray-500 ml-2">
                                                        ({categoriasMaquina.length} disponíveis)
                                                    </span>
                                                </div>
                                                {categoriasMaquina.length > 0 ? (
                                                    <div className="space-y-1 max-h-32 overflow-y-auto">
                                                        {categoriasMaquina.map((tipoNome, index) => (
                                                            <label key={`cat-${tipoNome}-${index}`} className="flex items-center text-sm">
                                                                <input
                                                                    type="radio"
                                                                    name="categoria"
                                                                    value={tipoNome}
                                                                    checked={formData.categoriaSelecionada === tipoNome}
                                                                    onChange={(e) => {
                                                                        const tipoSelecionado = e.target.value;
                                                                        setFormData({
                                                                            ...formData,
                                                                            categoriaSelecionada: tipoSelecionado,
                                                                            subcategoriasSelecionadas: [] // Reset subcategorias
                                                                        });

                                                                        // Carregar subcategorias do tipo selecionado
                                                                        loadSubcategoriasPorTipo(tipoSelecionado);
                                                                    }}
                                                                    className="h-4 w-4 text-purple-600 mr-2"
                                                                />
                                                                <span className="text-xs">{tipoNome}</span>
                                                            </label>
                                                        ))}
                                                    </div>
                                                ) : (
                                                    <div className="text-xs text-gray-500 italic">
                                                        Selecione um tipo de máquina para ver as opções da categoria
                                                    </div>
                                                )}
                                            </div>

                                            {/* Subcategorias da Máquina */}
                                            <div className="bg-white rounded-lg border border-purple-200 p-3">
                                                <div className="text-sm font-semibold text-purple-800 mb-2">
                                                    🎯 Subcategorias (Partes da Máquina a serem trabalhadas)
                                                    <span className="text-xs text-gray-500 ml-2">
                                                        ({subcategoriasDisponiveis.length} disponíveis)
                                                    </span>
                                                </div>
                                                {formData.categoriaSelecionada ? (
                                                    subcategoriasDisponiveis.length > 0 ? (
                                                        <div className="grid grid-cols-2 gap-1 max-h-32 overflow-y-auto">
                                                            {subcategoriasDisponiveis.map((subcategoria, index) => (
                                                                <label key={`subcat-${subcategoria}-${index}`} className="flex items-center text-xs">
                                                                    <input
                                                                        type="checkbox"
                                                                        className="h-3 w-3 text-purple-600 mr-2"
                                                                        checked={formData.subcategoriasSelecionadas?.includes(subcategoria) || false}
                                                                        onChange={(e) => {
                                                                            const subcategorias = formData.subcategoriasSelecionadas || [];
                                                                            if (e.target.checked) {
                                                                                setFormData({
                                                                                    ...formData,
                                                                                    subcategoriasSelecionadas: [...subcategorias, subcategoria]
                                                                                });
                                                                            } else {
                                                                                setFormData({
                                                                                    ...formData,
                                                                                    subcategoriasSelecionadas: subcategorias.filter((s: string) => s !== subcategoria)
                                                                                });
                                                                            }
                                                                        }}
                                                                    />
                                                                    {subcategoria}
                                                                </label>
                                                            ))}
                                                        </div>
                                                    ) : (
                                                        <div className="text-xs text-gray-500 italic">
                                                            Nenhuma subcategoria encontrada para esta categoria.
                                                        </div>
                                                    )
                                                ) : (
                                                    <div className="text-xs text-gray-500 italic">
                                                        Selecione uma categoria para ver as subcategorias.
                                                    </div>
                                                )}
                                            </div>
                                        </div>

                                        {/* Resumo das seleções */}
                                        {formData.subcategoriasSelecionadas && formData.subcategoriasSelecionadas.length > 0 && (
                                            <div className="mt-3 p-2 bg-purple-100 border border-purple-300 rounded-lg">
                                                <div className="text-xs font-medium text-purple-900 mb-1">
                                                    📊 Subcategorias selecionadas: {formData.subcategoriasSelecionadas.length}
                                                </div>
                                                <div className="text-xs text-purple-700">
                                                    {formData.subcategoriasSelecionadas.join(', ')}
                                                </div>
                                            </div>
                                        )}
                                    </div>
                                )}

                                {/* Data e Hora */}
                                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                                    <div>
                                        <label className="block text-sm font-medium text-gray-700 mb-2">📅 Data Início</label>
                                        <input
                                            type="date"
                                            value={formData.inpData || ''}
                                            onChange={(e) => setFormData({ ...formData, inpData: e.target.value })}
                                            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                                        />
                                    </div>
                                    <div>
                                        <label className="block text-sm font-medium text-gray-700 mb-2">🕒 Hora Início</label>
                                        <input
                                            type="time"
                                            value={formData.inpHora || ''}
                                            onChange={(e) => setFormData({ ...formData, inpHora: e.target.value })}
                                            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                                        />
                                    </div>
                                    <div className="flex items-end">
                                        <button
                                            onClick={() => {
                                                const now = new Date();
                                                const currentDate = now.toISOString().split('T')[0];
                                                const currentTime = now.toTimeString().slice(0, 5);
                                                setFormData({
                                                    ...formData,
                                                    inpData: currentDate,
                                                    inpHora: currentTime
                                                });
                                            }}
                                            className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 whitespace-nowrap"
                                        >
                                            🕒 Iniciar Agora
                                        </button>
                                    </div>
                                </div>

                                {/* Retrabalho */}
                                <div className="bg-gray-50 p-4 rounded-lg">
                                    <div className="flex items-center space-x-3 mb-3">
                                        <input
                                            type="checkbox"
                                            id="retrabalho"
                                            checked={formData.inpRetrabalho || false}
                                            onChange={(e) => setFormData({ ...formData, inpRetrabalho: e.target.checked })}
                                            className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                                        />
                                        <label htmlFor="retrabalho" className="text-sm font-medium text-gray-700">
                                            🔄 Este é um retrabalho?
                                        </label>
                                    </div>

                                    {formData.inpRetrabalho && (
                                        <div>
                                            <label className="block text-sm font-medium text-gray-700 mb-2">Causa do Retrabalho</label>
                                            <select
                                                value={formData.selCausaRetrabalho || ''}
                                                onChange={(e) => setFormData({ ...formData, selCausaRetrabalho: e.target.value })}
                                                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                                                disabled={loadingDropdowns}
                                            >
                                                <option value="">
                                                    {loadingDropdowns ? 'Carregando...' : 'Selecione a causa'}
                                                </option>
                                                {causasRetrabalho.map((causa, index) => (
                                                    <option key={`causa-${causa.id}-${index}`} value={causa.codigo}>
                                                        {causa.codigo} - {causa.descricao}
                                                    </option>
                                                ))}
                                            </select>
                                        </div>
                                    )}
                                </div>

                                {/* Tabela de Tipos de Teste */}
                                {(() => {
                                    console.log('🧪 Renderizando tabela:', { tiposTesteLength: tiposTeste.length, tiposTeste });
                                    return null;
                                })()}
                                {tiposTesteOriginais.length > 0 && (
                                    <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                                        {/* Header com título e busca */}
                                        <div className="flex items-center justify-between mb-4">
                                            <div className="flex items-center">
                                                <h4 className="text-sm font-medium text-blue-900">
                                                    🧪 Tipos de Teste - {formData.selMaq}
                                                </h4>
                                                <span className="ml-2 text-xs bg-blue-200 text-blue-800 px-2 py-1 rounded-full">
                                                    {tiposTeste.length} de {tiposTesteOriginais.length}
                                                </span>
                                            </div>

                                            {/* Campo de Busca por Nome - Movido para cá */}
                                            <div className="flex items-center gap-2">
                                                <label className="text-xs font-medium text-blue-900">🔍 Buscar:</label>
                                                <input
                                                    type="text"
                                                    value={filtroNomeTeste}
                                                    onChange={(e) => handleFiltroNomeTeste(e.target.value)}
                                                    placeholder="Nome do teste..."
                                                    className="w-64 px-3 py-1 text-sm border border-blue-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                                />
                                                {filtroNomeTeste && (
                                                    <button
                                                        type="button"
                                                        onClick={() => handleFiltroNomeTeste('')}
                                                        className="text-xs bg-red-100 text-red-700 hover:bg-red-200 px-2 py-1 rounded"
                                                    >
                                                        ✕
                                                    </button>
                                                )}
                                            </div>
                                        </div>

                                        {/* Seção de Filtros Organizados */}
                                        <div className="bg-white rounded-lg border border-blue-200 p-3 mb-4">
                                            <div className="text-xs font-medium text-blue-900 mb-3 flex items-center justify-between">
                                                <span>🎛️ Filtros Avançados</span>
                                                <span className="text-xs text-blue-600 bg-blue-50 px-2 py-1 rounded-full">
                                                    📊 {tiposTeste.length} testes encontrados
                                                </span>
                                            </div>

                                            {/* Filtros Alinhados na Mesma Linha */}
                                            <div className="space-y-3">
                                                {/* Filtros por Tipo */}
                                                {tiposTesteUnicos.length > 0 && (
                                                    <div className="flex items-center gap-3">
                                                        <div className="text-xs font-medium text-gray-700 min-w-[80px]">📋 Por Tipo:</div>
                                                        <div className="flex flex-wrap gap-1">
                                                    <button
                                                        type="button"
                                                        onClick={() => handleFiltroTipoTeste('')}
                                                        className={`px-3 py-1 rounded-full text-xs font-medium transition-colors ${
                                                            filtroTipoTeste === ''
                                                                ? 'bg-blue-600 text-white'
                                                                : 'bg-blue-100 text-blue-700 hover:bg-blue-200'
                                                        }`}
                                                    >
                                                        TODOS ({tiposTeste.length})
                                                    </button>
                                                    {tiposTesteUnicos.map((tipo, index) => {
                                                        // Calcular contadores baseados nos filtros já aplicados (exceto tipo)
                                                        let testesParaContar = tiposTesteOriginais;

                                                        // Aplicar filtros de categoria se ativo
                                                        if (filtroCategoria !== '') {
                                                            testesParaContar = testesParaContar.filter(teste => teste.categoria === filtroCategoria);
                                                        }

                                                        // Aplicar filtros de subcategoria se ativo
                                                        if (filtroSubcategoria !== '') {
                                                            const subcategoriaValue = filtroSubcategoria === 'especiais' ? 1 : 0;
                                                            testesParaContar = testesParaContar.filter(teste => teste.subcategoria === subcategoriaValue);
                                                        }

                                                        // Aplicar filtro de nome se ativo
                                                        if (filtroNomeTeste !== '') {
                                                            testesParaContar = testesParaContar.filter(teste =>
                                                                teste.nome && teste.nome.toLowerCase().includes(filtroNomeTeste.toLowerCase())
                                                            );
                                                        }

                                                        const count = testesParaContar.filter(teste => teste.tipo_teste === tipo).length;
                                                        return (
                                                            <button
                                                                key={`filtro-tipo-${tipo}-${index}`}
                                                                type="button"
                                                                onClick={() => handleFiltroTipoTeste(tipo)}
                                                                className={`px-3 py-1 rounded-full text-xs font-medium transition-colors ${
                                                                    filtroTipoTeste === tipo
                                                                        ? 'bg-green-600 text-white'
                                                                        : 'bg-green-100 text-green-700 hover:bg-green-200'
                                                                }`}
                                                            >
                                                                {tipo} ({count})
                                                            </button>
                                                        );
                                                    })}
                                                </div>
                                            </div>
                                        )}

                                                {/* Filtros por Categoria */}
                                                {categoriasUnicas.length > 0 && (
                                                    <div className="flex items-center gap-3">
                                                        <div className="text-xs font-medium text-gray-700 min-w-[80px]">🏷️ Por Categoria:</div>
                                                        <div className="flex flex-wrap gap-1">
                                                    <button
                                                        type="button"
                                                        onClick={() => handleFiltroCategoria('')}
                                                        className={`px-3 py-1 rounded-full text-xs font-medium transition-colors ${
                                                            filtroCategoria === ''
                                                                ? 'bg-blue-600 text-white'
                                                                : 'bg-blue-100 text-blue-700 hover:bg-blue-200'
                                                        }`}
                                                    >
                                                        TODAS ({tiposTeste.length})
                                                    </button>
                                                    {categoriasUnicas.map((categoria, index) => {
                                                        // Calcular contadores baseados nos filtros já aplicados (exceto categoria)
                                                        let testesParaContar = tiposTesteOriginais;

                                                        // Aplicar filtros de tipo se ativo
                                                        if (filtroTipoTeste !== '') {
                                                            testesParaContar = testesParaContar.filter(teste => teste.tipo_teste === filtroTipoTeste);
                                                        }

                                                        // Aplicar filtros de subcategoria se ativo
                                                        if (filtroSubcategoria !== '') {
                                                            const subcategoriaValue = filtroSubcategoria === 'especiais' ? 1 : 0;
                                                            testesParaContar = testesParaContar.filter(teste => teste.subcategoria === subcategoriaValue);
                                                        }

                                                        // Aplicar filtro de nome se ativo
                                                        if (filtroNomeTeste !== '') {
                                                            testesParaContar = testesParaContar.filter(teste =>
                                                                teste.nome && teste.nome.toLowerCase().includes(filtroNomeTeste.toLowerCase())
                                                            );
                                                        }

                                                        const count = testesParaContar.filter(teste => teste.categoria === categoria).length;
                                                        const colorClass = categoria === 'Visual' ? 'bg-blue-100 text-blue-700 hover:bg-blue-200' :
                                                                          categoria === 'Elétricos' ? 'bg-yellow-100 text-yellow-700 hover:bg-yellow-200' :
                                                                          categoria === 'Mecânicos' ? 'bg-green-100 text-green-700 hover:bg-green-200' :
                                                                          'bg-gray-100 text-gray-700 hover:bg-gray-200';
                                                        const activeColorClass = categoria === 'Visual' ? 'bg-blue-600 text-white' :
                                                                                categoria === 'Elétricos' ? 'bg-yellow-600 text-white' :
                                                                                categoria === 'Mecânicos' ? 'bg-green-600 text-white' :
                                                                                'bg-gray-600 text-white';
                                                        return (
                                                            <button
                                                                key={`filtro-cat-${categoria}-${index}`}
                                                                type="button"
                                                                onClick={() => handleFiltroCategoria(categoria)}
                                                                className={`px-3 py-1 rounded-full text-xs font-medium transition-colors ${
                                                                    filtroCategoria === categoria ? activeColorClass : colorClass
                                                                }`}
                                                            >
                                                                {categoria} ({count})
                                                            </button>
                                                        );
                                                    })}
                                                </div>
                                            </div>
                                        )}

                                                {/* Filtros por Subcategoria */}
                                                <div className="flex items-center gap-3">
                                                    <div className="text-xs font-medium text-gray-700 min-w-[80px]">⭐ Por Subcategoria:</div>
                                                    <div className="flex flex-wrap gap-1">
                                                <button
                                                    type="button"
                                                    onClick={() => handleFiltroSubcategoria('')}
                                                    className={`px-3 py-1 rounded-full text-xs font-medium transition-colors ${
                                                        filtroSubcategoria === ''
                                                            ? 'bg-blue-600 text-white'
                                                            : 'bg-blue-100 text-blue-700 hover:bg-blue-200'
                                                    }`}
                                                >
                                                    TODAS ({tiposTeste.length})
                                                </button>
                                                <button
                                                    type="button"
                                                    onClick={() => handleFiltroSubcategoria('padrao')}
                                                    className={`px-3 py-1 rounded-full text-xs font-medium transition-colors ${
                                                        filtroSubcategoria === 'padrao'
                                                            ? 'bg-gray-600 text-white'
                                                            : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                                                    }`}
                                                >
                                                    Padrão ({(() => {
                                                        // Calcular contadores baseados nos filtros já aplicados (exceto subcategoria)
                                                        let testesParaContar = tiposTesteOriginais;

                                                        // Aplicar filtros de tipo se ativo
                                                        if (filtroTipoTeste !== '') {
                                                            testesParaContar = testesParaContar.filter(teste => teste.tipo_teste === filtroTipoTeste);
                                                        }

                                                        // Aplicar filtros de categoria se ativo
                                                        if (filtroCategoria !== '') {
                                                            testesParaContar = testesParaContar.filter(teste => teste.categoria === filtroCategoria);
                                                        }

                                                        // Aplicar filtro de nome se ativo
                                                        if (filtroNomeTeste !== '') {
                                                            testesParaContar = testesParaContar.filter(teste =>
                                                                teste.nome && teste.nome.toLowerCase().includes(filtroNomeTeste.toLowerCase())
                                                            );
                                                        }

                                                        return testesParaContar.filter(teste => teste.subcategoria === 0).length;
                                                    })()})
                                                </button>
                                                <button
                                                    type="button"
                                                    onClick={() => handleFiltroSubcategoria('especiais')}
                                                    className={`px-3 py-1 rounded-full text-xs font-medium transition-colors ${
                                                        filtroSubcategoria === 'especiais'
                                                            ? 'bg-purple-600 text-white'
                                                            : 'bg-purple-100 text-purple-700 hover:bg-purple-200'
                                                    }`}
                                                >
                                                    Especiais ({(() => {
                                                        // Calcular contadores baseados nos filtros já aplicados (exceto subcategoria)
                                                        let testesParaContar = tiposTesteOriginais;

                                                        // Aplicar filtros de tipo se ativo
                                                        if (filtroTipoTeste !== '') {
                                                            testesParaContar = testesParaContar.filter(teste => teste.tipo_teste === filtroTipoTeste);
                                                        }

                                                        // Aplicar filtros de categoria se ativo
                                                        if (filtroCategoria !== '') {
                                                            testesParaContar = testesParaContar.filter(teste => teste.categoria === filtroCategoria);
                                                        }

                                                        // Aplicar filtro de nome se ativo
                                                        if (filtroNomeTeste !== '') {
                                                            testesParaContar = testesParaContar.filter(teste =>
                                                                teste.nome && teste.nome.toLowerCase().includes(filtroNomeTeste.toLowerCase())
                                                            );
                                                        }

                                                        return testesParaContar.filter(teste => teste.subcategoria === 1).length;
                                                    })()}
                                                </button>
                                                    </div>
                                                </div>
                                            </div>

                                            {/* Botões de Limpeza */}
                                        {(filtroTipoTeste || filtroCategoria || filtroSubcategoria || filtroNomeTeste) && (
                                            <div className="flex items-center justify-between pt-2 border-t border-blue-200">
                                                <span className="text-xs text-blue-600">
                                                    📊 {tiposTeste.length} de {tiposTesteOriginais.length} testes
                                                </span>
                                                <button
                                                    type="button"
                                                    onClick={() => {
                                                        setFiltroTipoTeste('');
                                                        setFiltroCategoria('');
                                                        setFiltroSubcategoria('');
                                                        handleFiltroNomeTeste('');
                                                    }}
                                                    className="text-xs bg-red-100 text-red-700 hover:bg-red-200 px-3 py-1 rounded-full transition-colors"
                                                >
                                                    🗑️ Limpar todos os filtros
                                                </button>
                                            </div>
                                        )}
                                    </div>

                                    {/* Tabela de 3 Colunas */}
                                    <div className="overflow-x-auto">
                                            {/* Dividir testes em 3 colunas */}
                                            {(() => {
                                                const testesPerColumn = Math.ceil(tiposTeste.length / 3);
                                                const column1 = tiposTeste.slice(0, testesPerColumn);
                                                const column2 = tiposTeste.slice(testesPerColumn, testesPerColumn * 2);
                                                const column3 = tiposTeste.slice(testesPerColumn * 2);

                                                return (
                                                    <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
                                                        {/* Coluna 1 */}
                                                        <div className="bg-white border border-blue-200 rounded-lg overflow-hidden">
                                                            <table className="w-full text-xs">
                                                                <thead>
                                                                    <tr className="bg-blue-100">
                                                                        <th className="p-2 text-left font-medium text-blue-900 border-b border-blue-200">Tipo de Teste</th>
                                                                        <th className="p-2 text-center font-medium text-blue-900 border-b border-blue-200 w-24">Resultado</th>
                                                                        <th className="p-2 text-left font-medium text-blue-900 border-b border-blue-200 w-32">Observação</th>
                                                                    </tr>
                                                                </thead>
                                                                <tbody>
                                                                    {column1.map((teste, index) => {
                                                                        const testeSelecionado = testesSelecionados[teste.id];
                                                                        const isSelected = testeSelecionado?.selecionado || false;
                                                                        const isEvenRow = index % 2 === 0;

                                                                        return (
                                                                            <tr
                                                                                key={`col1-${teste.id}`}
                                                                                className={`${
                                                                                    isSelected
                                                                                        ? 'bg-blue-50'
                                                                                        : isEvenRow
                                                                                            ? 'bg-gray-50'
                                                                                            : 'bg-white'
                                                                                } hover:bg-blue-100 transition-colors cursor-pointer border-b border-gray-200`}
                                                                                onClick={() => handleTesteClick(teste.id)}
                                                                            >
                                                                                {/* Tipo de Teste */}
                                                                                <td className="p-2">
                                                                                    <div className={`text-left ${
                                                                                        isSelected
                                                                                            ? 'text-blue-900 font-medium'
                                                                                            : 'text-gray-700'
                                                                                    }`}>
                                                                                        <div className="font-medium text-xs">{teste.nome}</div>
                                                                                        {teste.tipo_teste && (
                                                                                            <div className="text-xs text-blue-600 mt-1">
                                                                                                📋 {teste.tipo_teste}
                                                                                            </div>
                                                                                        )}
                                                                                        {/* Badges de categoria inline */}
                                                                                        <div className="flex gap-1 mt-1">
                                                                                            <span className={`px-1 py-0.5 rounded text-xs font-medium ${
                                                                                                teste.categoria === 'Visual' ? 'bg-blue-100 text-blue-700' :
                                                                                                teste.categoria === 'Elétricos' ? 'bg-yellow-100 text-yellow-700' :
                                                                                                teste.categoria === 'Mecânicos' ? 'bg-green-100 text-green-700' :
                                                                                                'bg-gray-100 text-gray-700'
                                                                                            }`}>
                                                                                                {teste.categoria || 'Visual'}
                                                                                            </span>
                                                                                            <span className={`px-1 py-0.5 rounded text-xs font-medium ${
                                                                                                teste.subcategoria === 1 ? 'bg-purple-100 text-purple-700' : 'bg-gray-100 text-gray-700'
                                                                                            }`}>
                                                                                                {teste.subcategoria === 1 ? 'Esp' : 'Pad'}
                                                                                            </span>
                                                                                        </div>
                                                                                    </div>
                                                                                </td>

                                                                                {/* Resultado */}
                                                                                <td className="p-2">
                                                                                    {isSelected && (
                                                                                        <div className="flex flex-col gap-1">
                                                                                            <button
                                                                                                type="button"
                                                                                                onClick={osBloqueadaParaApontamento ? undefined : (e) => {
                                                                                                    e.stopPropagation();
                                                                                                    handleResultadoChange(teste.id, 'APROVADO');
                                                                                                }}
                                                                                                disabled={osBloqueadaParaApontamento}
                                                                                                className={`px-2 py-1 rounded text-xs font-medium transition-colors ${
                                                                                                    osBloqueadaParaApontamento
                                                                                                        ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                                                                                                        : testeSelecionado?.resultado === 'APROVADO'
                                                                                                            ? 'bg-green-500 text-white'
                                                                                                            : 'bg-green-100 text-green-700 hover:bg-green-200'
                                                                                                }`}
                                                                                            >
                                                                                                ✓ APR
                                                                                            </button>
                                                                                            <button
                                                                                                type="button"
                                                                                                onClick={osBloqueadaParaApontamento ? undefined : (e) => {
                                                                                                    e.stopPropagation();
                                                                                                    handleResultadoChange(teste.id, 'REPROVADO');
                                                                                                }}
                                                                                                disabled={osBloqueadaParaApontamento}
                                                                                                className={`px-2 py-1 rounded text-xs font-medium transition-colors ${
                                                                                                    osBloqueadaParaApontamento
                                                                                                        ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                                                                                                        : testeSelecionado?.resultado === 'REPROVADO'
                                                                                                            ? 'bg-red-500 text-white'
                                                                                                            : 'bg-red-100 text-red-700 hover:bg-red-200'
                                                                                                }`}
                                                                                            >
                                                                                                ✗ REP
                                                                                            </button>
                                                                                            <button
                                                                                                type="button"
                                                                                                onClick={osBloqueadaParaApontamento ? undefined : (e) => {
                                                                                                    e.stopPropagation();
                                                                                                    handleResultadoChange(teste.id, 'INCONCLUSIVO');
                                                                                                }}
                                                                                                disabled={osBloqueadaParaApontamento}
                                                                                                className={`px-2 py-1 rounded text-xs font-medium transition-colors ${
                                                                                                    osBloqueadaParaApontamento
                                                                                                        ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                                                                                                        : testeSelecionado?.resultado === 'INCONCLUSIVO'
                                                                                                            ? 'bg-orange-500 text-white'
                                                                                                            : 'bg-orange-100 text-orange-700 hover:bg-orange-200'
                                                                                                }`}
                                                                                            >
                                                                                                ? INC
                                                                                            </button>
                                                                                        </div>
                                                                                    )}
                                                                                    {!isSelected && (
                                                                                        <div className="text-center text-xs text-gray-400">
                                                                                            Clique
                                                                                        </div>
                                                                                    )}
                                                                                </td>

                                                                                {/* Observação */}
                                                                                <td className="p-2">
                                                                                    {isSelected && (
                                                                                        <div className="space-y-1">
                                                                                            <textarea
                                                                                                placeholder={osBloqueadaParaApontamento ? "Bloqueado" : "Observação..."}
                                                                                                value={testeSelecionado?.observacao || ''}
                                                                                                onChange={osBloqueadaParaApontamento ? undefined : (e) => {
                                                                                                    e.stopPropagation();
                                                                                                    handleObservacaoChange(teste.id, e.target.value);
                                                                                                }}
                                                                                                onClick={(e) => e.stopPropagation()}
                                                                                                disabled={osBloqueadaParaApontamento}
                                                                                                className={`w-full p-1 text-xs border rounded focus:outline-none resize-none ${
                                                                                                    osBloqueadaParaApontamento
                                                                                                        ? 'border-gray-300 bg-gray-100 text-gray-500 cursor-not-allowed'
                                                                                                        : 'border-gray-300 focus:ring-1 focus:ring-blue-500'
                                                                                                }`}
                                                                                                rows={2}
                                                                                                maxLength={100}
                                                                                            />
                                                                                            <div className="text-right">
                                                                                                <span className={`text-xs ${
                                                                                                    (testeSelecionado?.observacao?.length || 0) > 90
                                                                                                        ? 'text-red-600 font-medium'
                                                                                                        : 'text-gray-500'
                                                                                                }`}>
                                                                                                    {testeSelecionado?.observacao?.length || 0}/100
                                                                                                </span>
                                                                                            </div>
                                                                                        </div>
                                                                                    )}
                                                                                    {!isSelected && (
                                                                                        <div className="text-center text-xs text-gray-400">
                                                                                            -
                                                                                        </div>
                                                                                    )}
                                                                                </td>
                                                                            </tr>
                                                        );
                                                    })}
                                                </tbody>
                                            </table>
                                        </div>

                                                        {/* Coluna 2 */}
                                                        <div className="bg-white border border-blue-200 rounded-lg overflow-hidden">
                                                            <table className="w-full text-xs">
                                                                <thead>
                                                                    <tr className="bg-blue-100">
                                                                        <th className="p-2 text-left font-medium text-blue-900 border-b border-blue-200">Tipo de Teste</th>
                                                                        <th className="p-2 text-center font-medium text-blue-900 border-b border-blue-200 w-24">Resultado</th>
                                                                        <th className="p-2 text-left font-medium text-blue-900 border-b border-blue-200 w-32">Observação</th>
                                                                    </tr>
                                                                </thead>
                                                                <tbody>
                                                                    {column2.map((teste, index) => {
                                                                        const testeSelecionado = testesSelecionados[teste.id];
                                                                        const isSelected = testeSelecionado?.selecionado || false;
                                                                        const isEvenRow = index % 2 === 0;

                                                                        return (
                                                                            <tr
                                                                                key={`col2-${teste.id}`}
                                                                                className={`${
                                                                                    isSelected
                                                                                        ? 'bg-blue-50'
                                                                                        : isEvenRow
                                                                                            ? 'bg-gray-50'
                                                                                            : 'bg-white'
                                                                                } hover:bg-blue-100 transition-colors cursor-pointer border-b border-gray-200`}
                                                                                onClick={() => handleTesteClick(teste.id)}
                                                                            >
                                                                                {/* Tipo de Teste */}
                                                                                <td className="p-2">
                                                                                    <div className={`text-left ${
                                                                                        isSelected
                                                                                            ? 'text-blue-900 font-medium'
                                                                                            : 'text-gray-700'
                                                                                    }`}>
                                                                                        <div className="font-medium text-xs">{teste.nome}</div>
                                                                                        {teste.tipo_teste && (
                                                                                            <div className="text-xs text-blue-600 mt-1">
                                                                                                📋 {teste.tipo_teste}
                                                                                            </div>
                                                                                        )}
                                                                                        {/* Badges de categoria inline */}
                                                                                        <div className="flex gap-1 mt-1">
                                                                                            <span className={`px-1 py-0.5 rounded text-xs font-medium ${
                                                                                                teste.categoria === 'Visual' ? 'bg-blue-100 text-blue-700' :
                                                                                                teste.categoria === 'Elétricos' ? 'bg-yellow-100 text-yellow-700' :
                                                                                                teste.categoria === 'Mecânicos' ? 'bg-green-100 text-green-700' :
                                                                                                'bg-gray-100 text-gray-700'
                                                                                            }`}>
                                                                                                {teste.categoria || 'Visual'}
                                                                                            </span>
                                                                                            <span className={`px-1 py-0.5 rounded text-xs font-medium ${
                                                                                                teste.subcategoria === 1 ? 'bg-purple-100 text-purple-700' : 'bg-gray-100 text-gray-700'
                                                                                            }`}>
                                                                                                {teste.subcategoria === 1 ? 'Esp' : 'Pad'}
                                                                                            </span>
                                                                                        </div>
                                                                                    </div>
                                                                                </td>

                                                                                {/* Resultado */}
                                                                                <td className="p-2">
                                                                                    {isSelected && (
                                                                                        <div className="flex flex-col gap-1">
                                                                                            <button
                                                                                                type="button"
                                                                                                onClick={osBloqueadaParaApontamento ? undefined : (e) => {
                                                                                                    e.stopPropagation();
                                                                                                    handleResultadoChange(teste.id, 'APROVADO');
                                                                                                }}
                                                                                                disabled={osBloqueadaParaApontamento}
                                                                                                className={`px-2 py-1 rounded text-xs font-medium transition-colors ${
                                                                                                    osBloqueadaParaApontamento
                                                                                                        ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                                                                                                        : testeSelecionado?.resultado === 'APROVADO'
                                                                                                            ? 'bg-green-500 text-white'
                                                                                                            : 'bg-green-100 text-green-700 hover:bg-green-200'
                                                                                                }`}
                                                                                            >
                                                                                                ✓ APR
                                                                                            </button>
                                                                                            <button
                                                                                                type="button"
                                                                                                onClick={osBloqueadaParaApontamento ? undefined : (e) => {
                                                                                                    e.stopPropagation();
                                                                                                    handleResultadoChange(teste.id, 'REPROVADO');
                                                                                                }}
                                                                                                disabled={osBloqueadaParaApontamento}
                                                                                                className={`px-2 py-1 rounded text-xs font-medium transition-colors ${
                                                                                                    osBloqueadaParaApontamento
                                                                                                        ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                                                                                                        : testeSelecionado?.resultado === 'REPROVADO'
                                                                                                            ? 'bg-red-500 text-white'
                                                                                                            : 'bg-red-100 text-red-700 hover:bg-red-200'
                                                                                                }`}
                                                                                            >
                                                                                                ✗ REP
                                                                                            </button>
                                                                                            <button
                                                                                                type="button"
                                                                                                onClick={osBloqueadaParaApontamento ? undefined : (e) => {
                                                                                                    e.stopPropagation();
                                                                                                    handleResultadoChange(teste.id, 'INCONCLUSIVO');
                                                                                                }}
                                                                                                disabled={osBloqueadaParaApontamento}
                                                                                                className={`px-2 py-1 rounded text-xs font-medium transition-colors ${
                                                                                                    osBloqueadaParaApontamento
                                                                                                        ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                                                                                                        : testeSelecionado?.resultado === 'INCONCLUSIVO'
                                                                                                            ? 'bg-orange-500 text-white'
                                                                                                            : 'bg-orange-100 text-orange-700 hover:bg-orange-200'
                                                                                                }`}
                                                                                            >
                                                                                                ? INC
                                                                                            </button>
                                                                                        </div>
                                                                                    )}
                                                                                    {!isSelected && (
                                                                                        <div className="text-center text-xs text-gray-400">
                                                                                            Clique
                                                                                        </div>
                                                                                    )}
                                                                                </td>

                                                                                {/* Observação */}
                                                                                <td className="p-2">
                                                                                    {isSelected && (
                                                                                        <div className="space-y-1">
                                                                                            <textarea
                                                                                                placeholder={osBloqueadaParaApontamento ? "Bloqueado" : "Observação..."}
                                                                                                value={testeSelecionado?.observacao || ''}
                                                                                                onChange={osBloqueadaParaApontamento ? undefined : (e) => {
                                                                                                    e.stopPropagation();
                                                                                                    handleObservacaoChange(teste.id, e.target.value);
                                                                                                }}
                                                                                                onClick={(e) => e.stopPropagation()}
                                                                                                disabled={osBloqueadaParaApontamento}
                                                                                                className={`w-full p-1 text-xs border rounded focus:outline-none resize-none ${
                                                                                                    osBloqueadaParaApontamento
                                                                                                        ? 'border-gray-300 bg-gray-100 text-gray-500 cursor-not-allowed'
                                                                                                        : 'border-gray-300 focus:ring-1 focus:ring-blue-500'
                                                                                                }`}
                                                                                                rows={2}
                                                                                                maxLength={100}
                                                                                            />
                                                                                            <div className="text-right">
                                                                                                <span className={`text-xs ${
                                                                                                    (testeSelecionado?.observacao?.length || 0) > 90
                                                                                                        ? 'text-red-600 font-medium'
                                                                                                        : 'text-gray-500'
                                                                                                }`}>
                                                                                                    {testeSelecionado?.observacao?.length || 0}/100
                                                                                                </span>
                                                                                            </div>
                                                                                        </div>
                                                                                    )}
                                                                                    {!isSelected && (
                                                                                        <div className="text-center text-xs text-gray-400">
                                                                                            -
                                                                                        </div>
                                                                                    )}
                                                                                </td>
                                                                            </tr>
                                                                        );
                                                                    })}
                                                                </tbody>
                                                            </table>
                                                        </div>

                                                        {/* Coluna 3 */}
                                                        <div className="bg-white border border-blue-200 rounded-lg overflow-hidden">
                                                            <table className="w-full text-xs">
                                                                <thead>
                                                                    <tr className="bg-blue-100">
                                                                        <th className="p-2 text-left font-medium text-blue-900 border-b border-blue-200">Tipo de Teste</th>
                                                                        <th className="p-2 text-center font-medium text-blue-900 border-b border-blue-200 w-24">Resultado</th>
                                                                        <th className="p-2 text-left font-medium text-blue-900 border-b border-blue-200 w-32">Observação</th>
                                                                    </tr>
                                                                </thead>
                                                                <tbody>
                                                                    {column3.map((teste, index) => {
                                                                        const testeSelecionado = testesSelecionados[teste.id];
                                                                        const isSelected = testeSelecionado?.selecionado || false;
                                                                        const isEvenRow = index % 2 === 0;

                                                                        return (
                                                                            <tr
                                                                                key={`col3-${teste.id}`}
                                                                                className={`${
                                                                                    isSelected
                                                                                        ? 'bg-blue-50'
                                                                                        : isEvenRow
                                                                                            ? 'bg-gray-50'
                                                                                            : 'bg-white'
                                                                                } hover:bg-blue-100 transition-colors cursor-pointer border-b border-gray-200`}
                                                                                onClick={() => handleTesteClick(teste.id)}
                                                                            >
                                                                                {/* Tipo de Teste */}
                                                                                <td className="p-2">
                                                                                    <div className={`text-left ${
                                                                                        isSelected
                                                                                            ? 'text-blue-900 font-medium'
                                                                                            : 'text-gray-700'
                                                                                    }`}>
                                                                                        <div className="font-medium text-xs">{teste.nome}</div>
                                                                                        {teste.tipo_teste && (
                                                                                            <div className="text-xs text-blue-600 mt-1">
                                                                                                📋 {teste.tipo_teste}
                                                                                            </div>
                                                                                        )}
                                                                                        {/* Badges de categoria inline */}
                                                                                        <div className="flex gap-1 mt-1">
                                                                                            <span className={`px-1 py-0.5 rounded text-xs font-medium ${
                                                                                                teste.categoria === 'Visual' ? 'bg-blue-100 text-blue-700' :
                                                                                                teste.categoria === 'Elétricos' ? 'bg-yellow-100 text-yellow-700' :
                                                                                                teste.categoria === 'Mecânicos' ? 'bg-green-100 text-green-700' :
                                                                                                'bg-gray-100 text-gray-700'
                                                                                            }`}>
                                                                                                {teste.categoria || 'Visual'}
                                                                                            </span>
                                                                                            <span className={`px-1 py-0.5 rounded text-xs font-medium ${
                                                                                                teste.subcategoria === 1 ? 'bg-purple-100 text-purple-700' : 'bg-gray-100 text-gray-700'
                                                                                            }`}>
                                                                                                {teste.subcategoria === 1 ? 'Esp' : 'Pad'}
                                                                                            </span>
                                                                                        </div>
                                                                                    </div>
                                                                                </td>

                                                                                {/* Resultado */}
                                                                                <td className="p-2">
                                                                                    {isSelected && (
                                                                                        <div className="flex flex-col gap-1">
                                                                                            <button
                                                                                                type="button"
                                                                                                onClick={osBloqueadaParaApontamento ? undefined : (e) => {
                                                                                                    e.stopPropagation();
                                                                                                    handleResultadoChange(teste.id, 'APROVADO');
                                                                                                }}
                                                                                                disabled={osBloqueadaParaApontamento}
                                                                                                className={`px-2 py-1 rounded text-xs font-medium transition-colors ${
                                                                                                    osBloqueadaParaApontamento
                                                                                                        ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                                                                                                        : testeSelecionado?.resultado === 'APROVADO'
                                                                                                            ? 'bg-green-500 text-white'
                                                                                                            : 'bg-green-100 text-green-700 hover:bg-green-200'
                                                                                                }`}
                                                                                            >
                                                                                                ✓ APR
                                                                                            </button>
                                                                                            <button
                                                                                                type="button"
                                                                                                onClick={osBloqueadaParaApontamento ? undefined : (e) => {
                                                                                                    e.stopPropagation();
                                                                                                    handleResultadoChange(teste.id, 'REPROVADO');
                                                                                                }}
                                                                                                disabled={osBloqueadaParaApontamento}
                                                                                                className={`px-2 py-1 rounded text-xs font-medium transition-colors ${
                                                                                                    osBloqueadaParaApontamento
                                                                                                        ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                                                                                                        : testeSelecionado?.resultado === 'REPROVADO'
                                                                                                            ? 'bg-red-500 text-white'
                                                                                                            : 'bg-red-100 text-red-700 hover:bg-red-200'
                                                                                                }`}
                                                                                            >
                                                                                                ✗ REP
                                                                                            </button>
                                                                                            <button
                                                                                                type="button"
                                                                                                onClick={osBloqueadaParaApontamento ? undefined : (e) => {
                                                                                                    e.stopPropagation();
                                                                                                    handleResultadoChange(teste.id, 'INCONCLUSIVO');
                                                                                                }}
                                                                                                disabled={osBloqueadaParaApontamento}
                                                                                                className={`px-2 py-1 rounded text-xs font-medium transition-colors ${
                                                                                                    osBloqueadaParaApontamento
                                                                                                        ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                                                                                                        : testeSelecionado?.resultado === 'INCONCLUSIVO'
                                                                                                            ? 'bg-orange-500 text-white'
                                                                                                            : 'bg-orange-100 text-orange-700 hover:bg-orange-200'
                                                                                                }`}
                                                                                            >
                                                                                                ? INC
                                                                                            </button>
                                                                                        </div>
                                                                                    )}
                                                                                    {!isSelected && (
                                                                                        <div className="text-center text-xs text-gray-400">
                                                                                            Clique
                                                                                        </div>
                                                                                    )}
                                                                                </td>

                                                                                {/* Observação */}
                                                                                <td className="p-2">
                                                                                    {isSelected && (
                                                                                        <div className="space-y-1">
                                                                                            <textarea
                                                                                                placeholder={osBloqueadaParaApontamento ? "Bloqueado" : "Observação..."}
                                                                                                value={testeSelecionado?.observacao || ''}
                                                                                                onChange={osBloqueadaParaApontamento ? undefined : (e) => {
                                                                                                    e.stopPropagation();
                                                                                                    handleObservacaoChange(teste.id, e.target.value);
                                                                                                }}
                                                                                                onClick={(e) => e.stopPropagation()}
                                                                                                disabled={osBloqueadaParaApontamento}
                                                                                                className={`w-full p-1 text-xs border rounded focus:outline-none resize-none ${
                                                                                                    osBloqueadaParaApontamento
                                                                                                        ? 'border-gray-300 bg-gray-100 text-gray-500 cursor-not-allowed'
                                                                                                        : 'border-gray-300 focus:ring-1 focus:ring-blue-500'
                                                                                                }`}
                                                                                                rows={2}
                                                                                                maxLength={100}
                                                                                            />
                                                                                            <div className="text-right">
                                                                                                <span className={`text-xs ${
                                                                                                    (testeSelecionado?.observacao?.length || 0) > 90
                                                                                                        ? 'text-red-600 font-medium'
                                                                                                        : 'text-gray-500'
                                                                                                }`}>
                                                                                                    {testeSelecionado?.observacao?.length || 0}/100
                                                                                                </span>
                                                                                            </div>
                                                                                        </div>
                                                                                    )}
                                                                                    {!isSelected && (
                                                                                        <div className="text-center text-xs text-gray-400">
                                                                                            -
                                                                                        </div>
                                                                                    )}
                                                                                </td>
                                                                            </tr>
                                                                        );
                                                                    })}
                                                                </tbody>
                                                            </table>
                                                        </div>
                                                    </div>
                                                );
                                            })()}

                                        {/* Mensagem quando há filtros mas nenhum resultado */}
                                        {tiposTeste.length === 0 && (filtroTipoTeste !== '' || filtroNomeTeste !== '' || filtroCategoria !== '' || filtroSubcategoria !== '') && (
                                            <div className="mt-3 p-4 bg-yellow-50 border border-yellow-200 rounded-lg text-center">
                                                <div className="text-yellow-800 text-sm font-medium mb-2">
                                                    🔍 Nenhum teste encontrado
                                                </div>
                                                <div className="text-yellow-700 text-xs">
                                                    {filtroTipoTeste && filtroNomeTeste ? (
                                                        <>Nenhum teste do tipo "<strong>{filtroTipoTeste}</strong>" contém "<strong>{filtroNomeTeste}</strong>"</>
                                                    ) : filtroTipoTeste ? (
                                                        <>Nenhum teste do tipo "<strong>{filtroTipoTeste}</strong>" encontrado</>
                                                    ) : (
                                                        <>Nenhum teste contém "<strong>{filtroNomeTeste}</strong>"</>
                                                    )}
                                                </div>

                                            </div>
                                        )}

                                        <div className="mt-2 text-xs text-blue-700">
                                            💡 Clique no nome do teste para selecioná-lo. Testes selecionados ficam destacados em azul.
                                        </div>


                                        </div>
                                    </div>
                                )}
                            </div>
                        )}
                    </div>
                </div>
            )}

            {/* ETAPA 2: DETALHES COMPLEMENTARES - SEMPRE VISÍVEL */}
            <div className="bg-white rounded-lg shadow-sm border border-gray-200">
                <div className="px-6 py-4 border-b border-gray-200 bg-gradient-to-r from-green-50 to-emerald-50">
                    <div className="flex items-center">
                        <div className="w-8 h-8 bg-green-600 rounded-full flex items-center justify-center mr-3">
                            <span className="text-white font-bold text-sm">2</span>
                        </div>
                        <div>
                            <h3 className="text-lg font-semibold text-gray-900">Detalhes Complementares</h3>
                            <p className="text-sm text-gray-600">Observações gerais e resultado global do apontamento</p>
                        </div>
                    </div>
                </div>
                <div className="p-6">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">💬 Observação Geral</label>
                            <textarea
                                value={formData.observacao || ''}
                                onChange={criarHandlerTextoValidado((valor) => setFormData({ ...formData, observacao: valor }))}
                                onPaste={(e) => {
                                    e.preventDefault();
                                    const texto = e.clipboardData.getData('text');
                                    const textoLimpo = formatarTextoInput(texto);
                                    setFormData({ ...formData, observacao: textoLimpo });
                                }}
                                rows={3}
                                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                                placeholder="OBSERVAÇÕES GERAIS SOBRE O APONTAMENTO..."
                                style={{ textTransform: 'uppercase' }}
                                disabled={osBloqueadaParaApontamento}
                            />
                            {osBloqueadaParaApontamento && (
                                <p className="text-xs text-red-600 mt-1">⚠️ OS finalizada - campo bloqueado</p>
                            )}
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">🎯 Resultado Global</label>
                            <select
                                value={formData.resultadoGlobal || ''}
                                onChange={(e) => setFormData({ ...formData, resultadoGlobal: e.target.value })}
                                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                                disabled={osBloqueadaParaApontamento}
                            >
                                <option value="">Selecione o resultado</option>
                                <option value="APROVADO">✅ Aprovado</option>
                                <option value="REPROVADO">❌ Reprovado</option>
                                <option value="APROVADO_COM_RESTRICAO">⚠️ Aprovado com Restrição</option>
                                <option value="PENDENTE">🔄 Pendente</option>
                                <option value="EM_ANALISE">🔍 Em Análise</option>
                            </select>
                            {osBloqueadaParaApontamento && (
                                <p className="text-xs text-red-600 mt-1">⚠️ OS finalizada - campo bloqueado</p>
                            )}
                        </div>
                    </div>
                </div>
            </div>

            {/* ETAPA 3: FINALIZAÇÃO */}
            <div className="bg-white rounded-lg shadow-sm border border-gray-200">
                <div className="px-6 py-4 border-b border-gray-200 bg-gradient-to-r from-purple-50 to-pink-50">
                    <div className="flex items-center">
                        <div className="w-8 h-8 bg-purple-600 rounded-full flex items-center justify-center mr-3">
                            <span className="text-white font-bold text-sm">3</span>
                        </div>
                        <div>
                            <h3 className="text-lg font-semibold text-gray-900">Finalização</h3>
                            <p className="text-sm text-gray-600">Data e hora de finalização do apontamento</p>
                        </div>
                    </div>
                </div>
                <div className="p-6">
                    {/* Configuração de Supervisor */}
                    {(user?.privilege_level === 'ADMIN' || user?.privilege_level === 'SUPERVISOR') && (
                        <div className="bg-white border border-gray-200 rounded-lg p-3 mb-3">
                            <div className="flex items-center mb-2">
                                <div className="w-5 h-5 bg-purple-600 rounded-full flex items-center justify-center mr-2">
                                    <span className="text-white font-bold text-xs">S</span>
                                </div>
                                <h4 className="text-base font-semibold text-gray-900">Etapas</h4>
                                <div className="ml-2 text-xs bg-purple-100 text-purple-800 px-2 py-1 rounded">
                                    {user?.privilege_level === 'ADMIN' ? 'Admin' : 'Supervisor'}
                                </div>
                            </div>
                            <p className="text-xs text-gray-600 mb-2">
                                Configurações disponíveis apenas para supervisores e administradores.
                            </p>
                        {/* Testes Exclusivos do Setor */}
                        {testesExclusivos.length > 0 && (
                            <div className="mb-4">
                                <h5 className="text-sm font-medium text-gray-700 mb-2">🧪 Testes Exclusivos do Setor</h5>
                                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                                    {testesExclusivos.map((teste, index) => (
                                        <div key={`teste-excl-${teste.id}-${index}`}>
                                            <label className="flex items-center space-x-2">
                                                <input
                                                    type="checkbox"
                                                    checked={testesExclusivosSelecionados[teste.id] || false}
                                                    onChange={(e) => handleTesteExclusivoChange(teste.id, e.target.checked)}
                                                    className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                                                />
                                                <span className="text-xs font-medium text-gray-700">
                                                    {teste.descricao_teste_exclusivo || teste.nome}
                                                </span>
                                            </label>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )}

                        {/* Campo Horas Orçadas em linha separada */}
                        <div className="mb-3">
                            <div className="max-w-xs">
                                <label className="block text-xs font-medium text-gray-700 mb-1">Horas Orçadas (h)</label>
                                <input
                                    type="number"
                                    step="0.1"
                                    min="0"
                                    value={formData.supervisor_horas_orcadas || 0}
                                    onChange={handleSupervisorHorasOrcadasChange}
                                    className="w-full px-2 py-1 border border-gray-300 rounded text-xs focus:outline-none focus:ring-2 focus:ring-blue-500"
                                    placeholder="Digite as horas"
                                />
                            </div>
                        </div>

                        {/* Etapas na mesma linha */}
                        <div className="grid grid-cols-3 gap-3">
                            <div>
                                <label className="flex items-center space-x-2">
                                    <input
                                        type="checkbox"
                                        checked={formData.supervisor_testes_iniciais || false}
                                        onChange={handleSupervisorTestesIniciaisChange}
                                        className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                                    />
                                    <span className="text-xs font-medium text-gray-700">Etapa Inicial</span>
                                </label>
                            </div>
                            <div>
                                <label className="flex items-center space-x-2">
                                    <input
                                        type="checkbox"
                                        checked={formData.supervisor_testes_parciais || false}
                                        onChange={handleSupervisorTestesParciaisChange}
                                        className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                                    />
                                    <span className="text-xs font-medium text-gray-700">Etapa Parcial</span>
                                </label>
                            </div>
                            <div>
                                <label className="flex items-center space-x-2">
                                    <input
                                        type="checkbox"
                                        checked={formData.supervisor_testes_finais || false}
                                        onChange={handleSupervisorTestesFinaisChange}
                                        className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                                    />
                                    <span className="text-xs font-medium text-gray-700">Etapa Final</span>
                                </label>
                            </div>
                        </div>
                    </div>
                    )}

                    <div className="flex flex-wrap items-end gap-4 mb-4">
                        <div className="flex-1 min-w-[200px]">
                            <label className="block text-sm font-medium text-gray-700 mb-2">📅 Data Fim</label>
                            <input
                                type="date"
                                name="inpDataFim"
                                value={formData.inpDataFim || ''}
                                onChange={(e) => setFormData({ ...formData, inpDataFim: e.target.value })}
                                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                            />
                        </div>
                        <div className="flex-1 min-w-[200px]">
                            <label className="block text-sm font-medium text-gray-700 mb-2">🕒 Hora Fim</label>
                            <input
                                type="time"
                                name="inpHoraFim"
                                value={formData.inpHoraFim || ''}
                                onChange={(e) => setFormData({ ...formData, inpHoraFim: e.target.value })}
                                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                            />
                        </div>
                        <div className="flex-shrink-0">
                            <button
                                onClick={() => {
                                    const now = new Date();
                                    const currentDate = now.toISOString().split('T')[0];
                                    const currentTime = now.toTimeString().slice(0, 5);
                                    setFormData({
                                        ...formData,
                                        inpDataFim: currentDate,
                                        inpHoraFim: currentTime
                                    });
                                }}
                                className="px-4 py-2 bg-yellow-600 text-white rounded hover:bg-yellow-700 whitespace-nowrap"
                            >
                                🕒 Finalizar Agora
                            </button>
                        </div>
                        <div className="flex-shrink-0">
                            <button
                                onClick={osBloqueadaParaApontamento ? undefined : handleSaveApontamento}
                                disabled={osBloqueadaParaApontamento}
                                className={`px-4 py-2 text-white rounded whitespace-nowrap ${
                                    osBloqueadaParaApontamento
                                        ? 'bg-gray-400 cursor-not-allowed'
                                        : programacaoDetectada
                                        ? 'bg-blue-600 hover:bg-blue-700'
                                        : 'bg-green-600 hover:bg-green-700'
                                }`}
                                title={
                                    osBloqueadaParaApontamento
                                        ? "OS não permite apontamentos"
                                        : programacaoDetectada
                                        ? "Salvar apontamento e finalizar programação"
                                        : "Salvar apontamento"
                                }
                            >
                                {osBloqueadaParaApontamento
                                    ? '🚫 Bloqueado'
                                    : programacaoDetectada
                                    ? '💾 Salvar Apontamento/Programação'
                                    : '💾 Salvar Apontamento'
                                }
                            </button>
                        </div>
                        <div className="flex-shrink-0">
                            <button
                                onClick={osBloqueadaParaApontamento ? undefined : handleSaveWithPendencia}
                                disabled={osBloqueadaParaApontamento}
                                className={`px-4 py-2 text-white rounded whitespace-nowrap ${
                                    osBloqueadaParaApontamento
                                        ? 'bg-gray-400 cursor-not-allowed'
                                        : 'bg-orange-600 hover:bg-orange-700'
                                }`}
                                title={osBloqueadaParaApontamento ? "OS não permite apontamentos" : "Salvar com pendência"}
                            >
                                {osBloqueadaParaApontamento ? '🚫 Bloqueado' : '📋 Salvar com Pendência'}
                            </button>
                        </div>
                    </div>
                </div>
            </div>

            {/* Modal e seção de testes exclusivos removidos - sistema simplificado */}
        </div>
    );
};

export default ApontamentoFormTab;