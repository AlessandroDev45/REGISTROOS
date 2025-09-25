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

export interface Atividade { // This was previously 'value: string; label: string;' in one TiposApi and different in another. Consolidated.
    id: string | number; // Assuming ID can be string or number based on context
    nome: string;
    descricao: string;
    ativo?: boolean; // Added based on TipoAtividadeData from adminApi
}


export interface SetorContextType {
    setorAtivo: {
        chave: string;
        nome: string;
    } | null;
    configuracaoAtual: ConfiguracaoSetor | null;
    alterarSetor: (chave: string, config: ConfiguracaoSetor) => void;
    carregando: boolean;
    setCarregando: (isLoading: boolean) => void;
}

export interface User {
  id: number;
  nome_completo: string;
  primeiro_nome?: string;
  email: string;
  privilege_level: string;
  setor: string;
  matricula?: string;
  departamento?: string;
  is_approved?: boolean;
  trabalha_producao?: boolean;
  primeiro_login?: boolean;
}
