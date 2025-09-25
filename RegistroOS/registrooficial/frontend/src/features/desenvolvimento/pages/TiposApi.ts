// Tipos base compartilhados entre todos os setores dentro de MOTORES

export interface CampoDeFormularioBaseResultado {
    id: string;
    tipo: 'TEXT' | 'TEXT_AREA' | 'SELECT' | 'NUMBER' | 'DATE' | 'CHECKBOX';
    label: string;
    obrigatorio: boolean;
    options?: string[];
}

export interface TipoGenericoTeste {
    id: string;
    nome: string;
    grupo: string;
    resultadosPossiveis: string[];
    camposAdicionaisResultado: CampoFormularioTeste[];
}

export interface CampoFormularioTeste {
    name: string;
    type: 'TEXT' | 'TEXT_AREA' | 'SELECT' | 'NUMBER' | 'DATE' | 'CHECKBOX';
    options?: string[];
    label?: string;
    obrigatorio?: boolean;
}

export interface Atividade {
    value: string;
    label: string;
}

// Interface para configuração de setor
export interface ConfiguracaoSetor {
    NomeSetor: string;
    ChaveSetor: string;
    EsquemaCamposOS: Record<string, CampoDeFormularioBaseResultado>;
    DicionarioTestes: Record<string, TipoGenericoTeste>;
    ListaAtividades: Atividade[];
    ComponentesPorTestId?: Record<string, any>;
    ComponentesFormularioPrincipal: Array<{
        etapa: number;
        componente: any;
        props?: Record<string, any>;
    }>;
    ConfiguracaoBackend: {
        endPointApontamento: string;
        endPointOrdemServico: string;
    };
}

// Interface para contexto de setor ativo
export interface SetorContextType {
    setorAtivo: {
        chave: string;
        nome: string;
    };
    configuracaoAtual: ConfiguracaoSetor | null;
    carregarConfiguracaoSetor: (chaveSetor: string) => Promise<void>;
}