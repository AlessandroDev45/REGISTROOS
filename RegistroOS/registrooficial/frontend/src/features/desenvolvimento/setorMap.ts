import { ConfiguracaoSetor } from '../../pages/common/TiposApi';
import api from '../../services/api';

// Interface para o nosso mapa unificado
interface SetorModule {
    loadConfig: () => Promise<{ default: ConfiguracaoSetor }>;
}

// Cache para configurações de setores
const setorConfigCache = new Map<string, ConfiguracaoSetor>();

// Configuração padrão genérica para qualquer setor
const createDefaultConfig = (setorNome: string, setorId: string): ConfiguracaoSetor => ({
    NomeSetor: setorNome,
    ChaveSetor: setorId,
    EsquemaCamposOS: {
        observacoes_gerais: { label: 'Observações Gerais', tipo: 'text' },
        prioridade: { label: 'Prioridade', tipo: 'select', opcoes: ['BAIXA', 'MEDIA', 'ALTA', 'URGENTE'] }
    },
    DicionarioTestes: {
        'Verificação Geral': {
            campos: {
                resultado: { label: 'Resultado', tipo: 'select', opcoes: ['APROVADO', 'REPROVADO', 'PENDENTE'] },
                observacoes: { label: 'Observações', tipo: 'text', placeholder: 'Descreva os resultados...' }
            }
        },
        'Inspeção Visual': {
            campos: {
                condicao_geral: { label: 'Condição Geral', tipo: 'select', opcoes: ['EXCELENTE', 'BOM', 'REGULAR', 'RUIM'] },
                defeitos_encontrados: { label: 'Defeitos Encontrados', tipo: 'text', placeholder: 'Liste os defeitos...' }
            }
        }
    },
    ListaAtividades: [
        { nome: 'Recebimento', descricao: 'Recebimento do equipamento/material' },
        { nome: 'Análise Inicial', descricao: 'Análise inicial do trabalho a ser realizado' },
        { nome: 'Execução', descricao: 'Execução do trabalho principal' },
        { nome: 'Verificação', descricao: 'Verificação e controle de qualidade' },
        { nome: 'Finalização', descricao: 'Finalização e entrega' }
    ],
    ComponentesFormularioPrincipal: [
        { etapa: 1, componente: 'input', props: { tipo: 'text', label: 'Código/Identificação', placeholder: 'Ex: ID-001' } },
        { etapa: 2, componente: 'select', props: { label: 'Tipo de Trabalho', opcoes: ['MANUTENCAO', 'REPARO', 'FABRICACAO', 'INSPECAO'] } }
    ],
    ConfiguracaoBackend: {
        endPointApontamento: '/desenvolvimento/apontamentos',
        endPointOrdemServico: '/api/ordens-servico'
    }
});

// Função para buscar setores do banco de dados
const fetchSetoresFromDatabase = async (): Promise<any[]> => {
    try {
        const response = await api.get('/setores');
        return response.data || [];
    } catch (error) {
        console.error('Erro ao buscar setores:', error);
        return [];
    }
};

// Função para carregar configuração de um setor específico
const loadSetorConfig = async (setorId: string): Promise<ConfiguracaoSetor> => {
    // Verificar cache primeiro
    if (setorConfigCache.has(setorId)) {
        return setorConfigCache.get(setorId)!;
    }

    try {
        // Buscar informações do setor no banco
        const setores = await fetchSetoresFromDatabase();
        const setor = setores.find(s =>
            s.id.toString() === setorId ||
            s.nome.toLowerCase().replace(/\s+/g, '-') === setorId ||
            s.nome.toLowerCase() === setorId.toLowerCase()
        );

        if (!setor) {
            throw new Error(`Setor ${setorId} não encontrado`);
        }

        // Criar configuração padrão baseada nos dados do banco
        const config = createDefaultConfig(setor.nome, setorId);

        // Tentar carregar configurações específicas se existirem
        try {
            const specificConfigResponse = await api.get(`/desenvolvimento/setores/${setor.id}/configuracao`);
            if (specificConfigResponse.data) {
                // Mesclar configuração específica com a padrão
                Object.assign(config, specificConfigResponse.data);
            }
        } catch (error) {
            // Se não houver configuração específica, usar a padrão
            console.log(`Usando configuração padrão para setor ${setor.nome}`);
        }

        // Armazenar no cache
        setorConfigCache.set(setorId, config);

        return config;
    } catch (error) {
        console.error(`Erro ao carregar configuração do setor ${setorId}:`, error);
        // Retornar configuração padrão em caso de erro
        return createDefaultConfig(`Setor ${setorId}`, setorId);
    }
};

// Função para criar o mapa dinâmico de setores
const createDynamicSetorMap = async (): Promise<Record<string, SetorModule>> => {
    try {
        const setores = await fetchSetoresFromDatabase();
        const dynamicMap: Record<string, SetorModule> = {};

        for (const setor of setores) {
            // Criar chaves múltiplas para o mesmo setor (por ID e por nome)
            const setorKey = setor.nome.toLowerCase().replace(/\s+/g, '-');
            const setorIdKey = setor.id.toString();

            const module: SetorModule = {
                loadConfig: () => loadSetorConfig(setorKey).then(config => ({ default: config }))
            };

            dynamicMap[setorKey] = module;
            dynamicMap[setorIdKey] = module;
            dynamicMap[setor.nome.toLowerCase()] = module;
        }

        return dynamicMap;
    } catch (error) {
        console.error('Erro ao criar mapa dinâmico de setores:', error);
        return {};
    }
};

// Cache para o mapa de setores
let cachedSetorMap: Record<string, SetorModule> | null = null;

// Função para obter o mapa de setores (com cache)
export const getSetorMap = async (): Promise<Record<string, SetorModule>> => {
    if (!cachedSetorMap) {
        cachedSetorMap = await createDynamicSetorMap();
    }
    return cachedSetorMap;
};

// Mapa inicial vazio - será preenchido dinamicamente
export const setorMap: Record<string, SetorModule> = {};

// Função para inicializar o mapa de setores
export const initializeSetorMap = async (): Promise<void> => {
    const dynamicMap = await getSetorMap();
    Object.assign(setorMap, dynamicMap);
};

// Função para obter lista de setores disponíveis
export const getAvailableSectors = async (): Promise<string[]> => {
    try {
        const setores = await fetchSetoresFromDatabase();
        return setores
            .filter(setor => setor.ativo !== false)
            .map(setor => setor.nome.toLowerCase().replace(/\s+/g, '-'));
    } catch (error) {
        console.error('Erro ao buscar setores disponíveis:', error);
        return [];
    }
};

// Lista inicial vazia - será preenchida dinamicamente
export const availableSectors: string[] = [];

// Função para inicializar a lista de setores disponíveis
export const initializeAvailableSectors = async (): Promise<void> => {
    const sectors = await getAvailableSectors();
    availableSectors.length = 0; // Limpar array
    availableSectors.push(...sectors); // Adicionar novos setores
};

// Função para verificar se um setor existe
export const sectorExists = (sectorKey: string): boolean => {
    return sectorKey in setorMap;
};