import React, { useState, useEffect, useMemo } from 'react';
import { StyledInput, SelectField } from '../../../../components/UIComponents';
import { setorService, departamentoService } from '../../../../services/adminApi';
import { toast, ToastContainer } from 'react-toastify';

// Tipos de dados
interface SelectedItem {
    id: string;
    label: string;
    category: string;
}

interface FilteredItem {
    id: string;
    label: string;
    category: string;
    matchScore?: number;
}

// Test data arrays from user specification
const tiposMaquinaOptions = [
    'MAQUINA ESTATICA CA',
    'MAQUINA ROTATIVA CA',
    'MAQUINA ROTATIVA CC',
    'PROGRAMACAO DE ATIVIDADE',
    'PARADA OS'
];

const tiposAtividadeOptions = [
    'TESTES INICIAIS',
    'TESTES PARCIAIS',
    'TESTES FINAIS',
    'RELATORIO',
    'DAIMER',
    'PARADA'
];

const descricoesAtividadeOptions = [
    'TESTES INICIAIS INTERNOS',
    'TESTES INICIAIS COM CLIENTE',
    'TESTES PARCIAIS (LIBERACAO PARA IMPREGNAR)',
    'TESTES PARCIAIS (ACOMPANHAMENTO)',
    'TESTES PARCIAIS COM CLIENTE',
    'TESTES FINAIS INTERNOS',
    'TESTES FINAIS COM CLIENTE',
    'RELATORIO',
    'LANCAMENTO DE PROGRAMACAO',
    'REGISTRO DE NAO CONFORMIDADE',
    'REUNIAO',
    'MONTAGEM DE CIRCUITO',
    'DESMONTAGEM DE CIRCUITO',
    'SERVIÇO DE CAMPO',
    'ALINHAMENTO DE MOTOR',
    'LUBRIFICACAO DE MOTOR',
    'FIXACAO DE MOTOR NA BASE',
    'BALANCEAMENTO DE MOTOR',
    'MOVIMENTACAO DE CARGA',
    '00001 APLICACAO',
    '00002 COMERCIAL',
    '00003 CONSUMO',
    '00004 DISOC',
    '00005 FERRAMENTA',
    '00006 MANEQUIP',
    '00007 MANPRED',
    '00008 PATRIMÔNIO',
    '00009 PARADA PARA TREINAMENTO/REUNIÃO',
    '00011 ESTOQUE',
    '00012 PARADA PARA SSMA (EXAMES)',
    '00013 INCENDIO',
    '00014 REVENDA',
    '00015 PARADA POR IMPRODUTIVIDADE',
    '00020 MAN PONTE',
    '00021 AMFBM',
    '00022 AMPFT',
    '00023 PARADA PARA MOVIMENTACAO DE CARGA',
    '00024 PARADA PARA MANUTENCAO DE EQUIP.',
    '00025 PARADA POR INDISPONIBILIDADE DE PONTE ROLANTE',
    '00026 PARADA POR FALTA DE MATERIAL',
    '00027 PARADA POR ATRASO DE PROJETO',
    '00028 PARADA POR ATRASO DA SEÇÃO ANTERIOR',
    '00029 PARADA POR FALTA DE OS',
    '00030 PARADA PARA LIMPEZA',
    '00032 SOROCABA',
    '00051 NOVO LABORATORIO'
];

const tiposFalhaOptions = [
    'ISOLAMENTO RESSECADO (ESTATOR)',
    'ISOLAMENTO RESSECADO (ROTOR)',
    'ISOLAMENTO RESSECADO (ESTATOR AUX)',
    'ISOLAMENTO RESSECADO (ROTOR AUX)',
    'ISOLAMENTO RESSECADO (INTERPOLOS)',
    'ISOLAMENTO RESSECADO (CAMPO SHUNT)',
    'ISOLAMENTO RESSECADO (CAMPO SERIE)',
    'ISOLAMENTO RESSECADO (COMPENSACAO)',
    'ISOLAMENTO RESSECADO (ARMADURA)',
    'BAIXA RESISTENCIA DE ISOLAMENTO (ESTATOR)',
    'BAIXA RESISTENCIA DE ISOLAMENTO (ROTOR)',
    'BAIXA RESISTENCIA DE ISOLAMENTO (ANEIS DO ROTOR)',
    'BAIXA RESISTENCIA DE ISOLAMENTO (ESTATOR AUX)',
    'BAIXA RESISTENCIA DE ISOLAMENTO (ROTOR AUX)',
    'BAIXA RESISTENCIA DE ISOLAMENTO (ESTATOR PMG)',
    'BAIXA RESISTENCIA DE ISOLAMENTO (PORTA ESCOVAS)',
    'BAIXA RESISTENCIA DE ISOLAMENTO (TAMPA)',
    'BAIXA RESISTENCIA DE ISOLAMENTO (TAMPA RECUPERADA)',
    'BAIXA RESISTENCIA DE ISOLAMENTO (MANCAL)',
    'BAIXA RESISTENCIA DE ISOLAMENTO (MANCAL RECUPERADO)',
    'BAIXA RESISTENCIA DE ISOLAMENTO (ROLAMENTO)',
    'BAIXA RESISTENCIA DE ISOLAMENTO (RESISTOR DE AQUEC)',
    'BAIXA RESISTENCIA DE ISOLAMENTO(RTD\'S ENROL.)',
    'BAIXA RESISTENCIA DE ISOLAMENTO(RTD\'S LA)',
    'BAIXA RESISTENCIA DE ISOLAMENTO(RTD\'S LOA)',
    'BAIXA RESISTENCIA DE ISOLAMENTO (ARMADURA)',
    'BAIXA RESISTENCIA DE ISOLAMENTO (INTERPOLOS)',
    'BAIXA RESISTENCIA DE ISOLAMENTO (CAMPO SHUNT)',
    'BAIXA RESISTENCIA DE ISOLAMENTO (COMPENSACAO)',
    'RESISTENCIA OHMICA DESEQUILIBRADA (ESTATOR)',
    'RESISTENCIA OHMICA SOLDA RUIM(ESTATOR)',
    'RESISTENCIA OHMICA DESEQUILIBRADA (ROTOR)',
    'RESISTENCIA OHMICA SOLDA RUIM (ROTOR)',
    'RESISTENCIA OHMICA ANORMAL SOLDA RUIM (RESIS CONTATO ANEIS DO ROTOR)',
    'RESISTENCIA OHMICA DESEQUILIBRADA (ESTATOR  AUX)',
    'RESISTENCIA OHMICA SOLDA RUIM (ESTATOR  AUX)',
    'RESISTENCIA OHMICA DESEQUILIBRADA (ROTOR  AUX)',
    'RESISTENCIA OHMICA SOLDA RUIM (ROTOR  AUX)',
    'RESISTENCIA OHMICA DESEQUILIBRADA ESTATOR(PMG)',
    'RESISTENCIA OHMICA  SOLDA RUIM(ARMADURA)',
    'RESISTENCIA OHMICA  SOLDA RUIM(INTERPOLOS)',
    'RESISTENCIA OHMICA  SOLDA RUIM(CAMPO SHUNT)',
    'RESISTENCIA OHMICA  SOLDA RUIM(COMPENSACAO)',
    'RESISTENCIA OHMICA CIRCUITO ABERTO(ESTATOR)',
    'RESISTENCIA OHMICA CIRCUITO ABERTO(ROTOR)',
    'RESISTENCIA OHMICA CIRCUITO ABERTO(ESTATOR AUX)',
    'RESISTENCIA OHMICA CIRCUITO ABERTO(PMG)',
    'RESISTENCIA OHMICA CIRCUITO ABERTO(ROTOR AUX)',
    'RESISTENCIA OHMICA CIRCUITO ABERTO(RESISTOR AQUEC)',
    'RESISTENCIA OHMICA CIRCUITO ABERTO BAIXA RESISTENCIA DE ISOLAMENTO(RTD\'S ENROL.)',
    'RESISTENCIA DE ISOLAMENTO(RTD\'S LA)',
    'RESISTENCIA DE ISOLAMENTO(RTD\'S LOA)',
    'SURGE TEST COM ERRO SUPERIOR AO TOLERAVEL (ESTATOR)',
    'SURGE TEST COM ERRO SUPERIOR AO TOLERAVEL (ROTOR)',
    'SURGE TEST COM ERRO SUPERIOR AO TOLERAVEL (ROTOR AUX)',
    'SURGE TEST COM ERRO SUPERIOR AO TOLERAVEL (BOBINA SOLTEIRA)',
    'SURGE TEST COM ERRO SUPERIOR AO TOLERAVEL (PMG)',
    'CURTO ENTRE ESPIRAS  (ESTATOR)',
    'CURTO ENTRE ESPIRAS (ROTOR)',
    'CURTO ENTRE ESPIRAS (ESTATOR AUX)',
    'CURTO ENTRE ESPIRAS (ROTOR AUX)',
    'CURTO ENTRE ESPIRAS (INTERPOLOS)',
    'CURTO ENTRE ESPIRAS (CAMPO SHUNT)',
    'CURTO ENTRE ESPIRAS (CAMPO SERIE)',
    'CURTO ENTRE ESPIRAS (COMPENSACAO)',
    'CURTO ENTRE ESPIRAS (ARMADURA)',
    'CURTO ENTRE CABOS (RTD\'S ENROL.)',
    'CURTO ENTRE CABOS (RTD\'S LA)',
    'CURTO ENTRE CABOS (RTD\'S LOA)',
    'PONTO(S) QUENTE(S) DURANTE O TESTE DE IMPEDANCIA (ESTATOR)',
    'PONTO(S) QUENTE(S) DURANTE O TESTE DE IMPEDANCIA (ROTOR)',
    'PONTO(S) QUENTE(S) DURANTE O TESTE DE IMPEDANCIA (ESTATOR AUX)',
    'PONTO(S) QUENTE(S) DURANTE O TESTE DE IMPEDANCIA (ROTOR AUX)',
    'PONTO(S) QUENTE(S) DURANTE O TESTE DE IMPEDANCIA (CONEXOES)',
    'DESEQUILIBRIO DE CORRENTE DURANTE O TESTE DE IMPEDANCIA (ESTATOR)',
    'DESEQUILÍBRIO DE CORRENTE DURANTE O TESTE DE IMPEDANCIA (ROTOR)',
    'ERRO NA LIGACAO (TESTE DE IMPEDANCIA) (ESTATOR)',
    'ERRO NA LIGACAO (TESTE DE IMPEDANCIA) (ROTOR)',
    'ERRO NA LIGACAO (TESTE DE IMPEDANCIA) (ESTATOR AUX)',
    'ERRO NA LIGACAO (TESTE DE IMPEDANCIA) (ROTOR AUX)',
    'ERRO NA IDENTIFICACAO DOS CABOS DE LIGACAO (ESTATOR)',
    'ERRO NA IDENTIFICACAO DOS CABOS DE LIGACAO (ROTOR)',
    'ERRO NA LIGACAO (POLARIDADE) (ESTATOR)',
    'ERRO NA LIGACAO (POLARIDADE) (ESTATOR AUX)',
    'ERRO NA LIGACAO (POLARIDADE) (ROTOR)',
    'ERRO NA LIGACAO (POLARIDADE) (ROTOR AUX)',
    'ERRO NA LIGACAO (QUEDA DE TENSAO) (INTERPOLOS)',
    'ERRO NA LIGACAO (QUEDA DE TENSAO) (CAMPO SHUNT)',
    'ERRO NA LIGACAO (QUEDA DE TENSAO) (COMPENSACAO)',
    'ERRO NA LIGACAO (QUEDA DE TENSAO) (ROTOR )',
    'SENSOR DE PROXIMIDADE DANIFICADO',
    'SENSOR DE VIBRACAO DANIFICADO',
    'PACOTE MAGNETICO RASPADO (ESTATOR)',
    'PACOTE MAGNETICO RASPADO (ESTATOR AUX)',
    'PACOTE MAGNETICO RASPADO (ESTATOR PMG)',
    'PACOTE MAGNETICO RASPADO (ROTOR)',
    'PACOTE MAGNETICO RASPADO (ROTOR AUX)',
    'PACOTE MAGNETICO RASPADO (ROTOR PMG)',
    'ROTOR COM BARRA TRINCADA',
    'PACOTE MAGNETICO REPROVADO NO LOOP TEST (ESTATOR)',
    'PACOTE MAGNETICO REPROVADO NO LOOP TEST (ARMADURA)',
    'FALHA NO TESTE DE TENSAO APLICADA (HIPOT) (ESTATOR)',
    'FALHA NO TESTE DE TENSAO APLICADA (HIPOT) (ROTOR)',
    'FALHA NO TESTE DE TENSAO APLICADA (HIPOT) (ESTATOR AUXILIAR)',
    'FALHA NO TESTE DE TENSAO APLICADA (HIPOT) (ROTOR AUXILIAR)',
    'FALHA NO TESTE DE TENSAO APLICADA (HIPOT) (ESTATOR PMG)',
    'FALHA NO TESTE DE TENSAO APLICADA (HIPOT) (ARMADURA)',
    'FALHA NO TESTE DE TENSAO APLICADA (HIPOT) (INTER PÓLOS)',
    'FALHA NO TESTE DE TENSAO APLICADA (HIPOT) (COMPENSACAO)',
    'FALHA NO TESTE DE TENSAO APLICADA (HIPOT) (CAMPO SHUNT)',
    'FALHA NO TESTE DE TENSAO APLICADA (HIPOT) (CAMPO SERIE)',
    'QUEDA DE TENSAO CA COM ERRO SUPERIOR AO TOLERAVEL (ROTOR)',
    'QUEDA DE TENSAO CA COM ERRO SUPERIOR AO TOLERAVEL (ESTATOR AUXILIAR)',
    'QUEDA DE TENSAO CC COM ERRO SUPERIOR AO TOLERAVEL (ROTOR)',
    'QUEDA DE TENSAO CC COM ERRO SUPERIOR AO TOLERAVEL (ESTATOR AUXILIAR)',
    'FALHA POR TEMPERATURA ELEVADA DO MANCAL LA',
    'FALHA POR TEMPERATURA ELEVADA DO MANCAL LOA',
    'FALHA POR TEMPERATURA ELEVADA DO ENROLAMENTO',
    'FALHA POR VIBRACAO ELEVADA (VELOCIDADE)',
    'FALHA POR VIBRACAO ELEVADA (ACELERACAO)',
    'FALHA POR VIBRACAO ELEVADA (PROXIMIDADE)',
    'FALHA POR VIBRACAO ELEVADA (ENVELOPE)',
    'FALHA POR ROCAMENTO DO ROTOR COM PARTES FIXAS',
    'FALHA POR CENTRO MAGNETICO FORA DA POSICAO CORRETA',
    'FALHA POR CURTO CIRCUITO DURANTE TESTES EM VAZIO',
    'FALHA POR ATRITO ENTRE PARTES DINAMICAS E ESTATICAS',
    'FALHA POR MONTAGEM INCOMPLETA',
    'ANEL COLETOR/COMUTADOR DANIFICADO',
    'CORONA VISUAL',
    'FALHA NO TESTE DE SATURACAO DO NUCLEO(TRANSFORMADOR)',
    'FALHA NO TESTE DE TENSAO APLICADA (HIPOT) (TRANSFORMADOR AT)',
    'FALHA NO TESTE DE TENSAO APLICADA (HIPOT) (TRANSFORMADOR BT)',
    'FALHA NO TESTE DE TENSAO APLICADA (HIPOT) (TRANSFORMADOR TERC)',
    'FALHA NO TESTE DE TENSAO INDUZIDA DANO INTERNO',
    'DESCARGAS PARCIAIS >500 PC',
    'FALHA NO TESTE DE IMPULSO ATMOSFERICO EM AT',
    'FALHA NO TESTE DE IMPULSO ATMOSFERICO EM BT',
    'FALHA NO TESTE DE IMPULSO ATMOSFERICO EM TERC',
    'PERDAS EM VAZIO SUPERIOR AO PROJETO',
    'FALHA DURANTE TESTE EM VAZIO',
    'PERDAS EM CARGA SUPERIOR AO PROJETO',
    'IMPEDANCIA SEQ POSITIVA COM DESVIO SUPERIOR AO PROJETO',
    'IMPEDANCIA SEQ ZERO COM DESVIO SUPERIOR AO PROJETO',
    'ELEVAÇÃO DE TEMPERATURA SUPERIOR AO PROJETO',
    'VALOR  DE RUIDO  SUPERIOR AO PROJETO',
    'BAIXA RESISTENCIA DE ISOLAMENTO AT',
    'BAIXA RESISTENCIA DE ISOLAMENTO BT',
    'BAIXA RESISTENCIA DE ISOLAMENTO TERCIARIO',
    'BAIXA RESISTENCIA DE ISOLAMENTO NO NUCLEO',
    'RESISTENCIA OHMICA DESEQUILIBRADA AT',
    'RESISTENCIA OHMICA DESEQUILIBRADA BT',
    'RESISTENCIA OHMICA DESEQUILIBRADA TERCIARIO',
    'ERRO NA LIGACAO AT',
    'ERRO NA LIGACAO BT',
    'ERRO NA LIGACAO TERCIARIO',
    'SENSOR DE TEMPERATURA DANIFICADO',
    'TC  DANIFICADO',
    'ERRO NA LIGACAO DO TCEN'
];

// Test arrays from user specification
export const testesCaCarcaça: any[] = [
    { id: 'ca_carc_inspecao_visual', label: 'Inspeção Visual', options: true },
    { id: 'ca_carc_placa_id', label: 'Placa de identificação', options: true },
    { id: 'ca_carc_rtd_la', label: 'Rtd\'s Mancal LA', options: true },
    { id: 'ca_carc_rtd_loa', label: 'Rtd\'s Mancal LOA', options: true },
    { id: 'ca_carc_rtd_enrol', label: 'Rtd\'s Enrolamento', options: true },
    { id: 'ca_carc_resistor_aquec', label: 'Resistor de Aquecimento', options: true },
    { id: 'ca_carc_capacitores', label: 'Capacitores', options: true },
    { id: 'ca_carc_supressores', label: 'Supressores de Surto', options: true },
    { id: 'ca_carc_tcs', label: 'Tc\'s', options: true },
    { id: 'ca_carc_isoladores', label: 'Isoladores', options: true },
    { id: 'ca_carc_terminais', label: 'Terminais/Barramentos', options: true },
    { id: 'ca_carc_cabos', label: 'Cabos', options: true },
    { id: 'ca_carc_amarracoes', label: 'Amarrações', options: true },
    { id: 'ca_carc_sensor_vib_la', label: 'Sensor Vibração LA', options: true },
    { id: 'ca_carc_sensor_vib_loa', label: 'Sensor Vibração LOA', options: true },
    { id: 'ca_carc_caixa_lig_princ', label: 'Caixa de Ligação Principal', options: true },
    { id: 'ca_carc_caixa_lig_acess', label: 'Caixa de Ligação Dos Acessórios', options: true },
    { id: 'ca_carc_relatorio_tec', label: 'Relatório Técnico', options: false },
    { id: 'ca_carc_programacao', label: 'Programação', options: false },
    { id: 'ca_carc_liberacao_lc', label: 'Liberação de LC', options: false },
];

export const testesCaEstator: any[] = [
    { id: 'ca_estator_inspecao_enrol', label: 'Inspeção Visual Enrolamento', options: true },
    { id: 'ca_estator_inspecao_cabos', label: 'Inspeção Visual Cabos e Amarrações', options: true },
    { id: 'ca_estator_rtd_enrol', label: 'Rtd\'s Enrolamento', options: true },
    { id: 'ca_estator_res_isol', label: 'Resistência de Isolamento', options: true },
    { id: 'ca_estator_res_ohmica', label: 'Resistência Ôhmica', options: true },
    { id: 'ca_estator_surge', label: 'Surge Teste', options: true },
    { id: 'ca_estator_impedancia', label: 'Impedância Trifásica', options: true },
    { id: 'ca_estator_loop', label: 'Loop Teste/Aço Silício', options: true },
    { id: 'ca_estator_hipot', label: 'Hipot', options: true },
    { id: 'ca_estator_polaridade_ca', label: 'Polaridade CA', options: true },
    { id: 'ca_estator_corona', label: 'Corona visual', options: true },
    { id: 'ca_estator_tangente', label: 'Tangente Delta', options: true },
    { id: 'ca_estator_desc_parciais', label: 'Descargas Parciais', options: true },
    { id: 'ca_estator_desc_dieletricas', label: 'Descargas Dielétricas', options: true },
    { id: 'ca_estator_step_volt', label: 'Step Voltage', options: true },
    { id: 'ca_estator_rel_transf', label: 'Relação de Transformação', options: true },
    { id: 'ca_estator_rotor_bloq', label: 'Rotor Bloqueado', options: true },
    { id: 'ca_estator_relatorio', label: 'Relatório Técnico', options: false },
];

export const testesCaRotor: any[] = [
    { id: 'ca_rotor_inspecao_enrol', label: 'Inspeção Visual Enrolamento', options: true },
    { id: 'ca_rotor_inspecao_cabos', label: 'Inspeção Visual Cabos e Amarrações', options: true },
    { id: 'ca_rotor_aneis_visual', label: 'Anéis Inspeção Visual', options: true },
    { id: 'ca_rotor_aneis_res_contato', label: 'Anéis Resistência de Contato', options: true },
    { id: 'ca_rotor_aneis_res_isol', label: 'Anéis Resistência de Isolamento', options: true },
    { id: 'ca_rotor_res_isol', label: 'Resistência de Isolamento', options: true },
    { id: 'ca_rotor_res_ohmica', label: 'Resistência Ôhmica', options: true },
    { id: 'ca_rotor_surge', label: 'Surge Teste', options: true },
    { id: 'ca_rotor_impedancia', label: 'Impedância Trifásica', options: true },
    { id: 'ca_rotor_queda_ca', label: 'Queda de Tensão CA', options: true },
    { id: 'ca_rotor_queda_cc', label: 'Queda de Tensão CC', options: true },
    { id: 'ca_rotor_rso', label: 'RSO', options: true },
    { id: 'ca_rotor_rel_transf', label: 'Relação de Transformação', options: true },
    { id: 'ca_rotor_relatorio', label: 'Relatório Técnico', options: false },
];

export const testesCaAuxPmg: any[] = [
    { id: 'ca_aux_inspecao_enrol', label: 'Inspeção Visual Enrolamento', options: true },
    { id: 'ca_aux_inspecao_cabos', label: 'Inspeção Visual Cabos e Amarrações', options: true },
    { id: 'ca_aux_res_isol', label: 'Resistência de Isolamento', options: true },
    { id: 'ca_aux_res_ohmica', label: 'Resistência Ôhmica', options: true },
    { id: 'ca_aux_surge', label: 'Surge Teste', options: true },
    { id: 'ca_aux_rel_transf', label: 'Relação de Transformação', options: true },
    { id: 'ca_aux_queda_ca', label: 'Queda de Tensão CA', options: true },
    { id: 'ca_aux_queda_cc', label: 'Queda de Tensão CC', options: true },
    { id: 'ca_aux_rso', label: 'RSO', options: true },
    { id: 'ca_aux_impedancia', label: 'Impedância Trifásica', options: true },
    { id: 'ca_aux_loop', label: 'Loop Teste/Aço Silício', options: true },
    { id: 'ca_aux_hipot', label: 'Hipot', options: true },
    { id: 'ca_aux_polaridade_ca', label: 'Polaridade CA', options: true },
    { id: 'ca_aux_polaridade_cc', label: 'Polaridade CC', options: true },
    { id: 'ca_aux_diodos', label: 'Diodos', options: true },
    { id: 'ca_aux_varistores', label: 'Varistores', options: true },
    { id: 'ca_aux_tiristores', label: 'Tiristores', options: true },
    { id: 'ca_aux_resistor_roda', label: 'Resistor da Roda de Diodos', options: true },
    { id: 'ca_aux_relatorio', label: 'Relatório Técnico', options: false },
];

export const testesCaRotorPmg: any[] = [
    { id: 'ca_rotor_pmg_inspecao_imas', label: 'Inspeção Visual Imãs', options: true },
    { id: 'ca_rotor_pmg_inspecao_aco', label: 'Inspeção Visual Aço Silício', options: true },
    { id: 'ca_rotor_pmg_relatorio', label: 'Relatório Técnico', options: false },
];

interface FullSectorCreationFormProps {
    onCancel: () => void;
    onSubmit: (data: any) => void;
}

const FullSectorCreationForm: React.FC<FullSectorCreationFormProps> = ({
    onCancel,
    onSubmit,
}) => {
    const [departamentos, setDepartamentos] = useState<any[]>([]);
    const [setores, setSetores] = useState<any[]>([]);
    const [formData, setFormData] = useState({
        departamento: '',
        setor: '',
        tiposMaquina: [] as string[],
        tiposAtividade: [] as string[],
        descricoesAtividade: [] as string[],
        tiposFalha: [] as string[],
        testesEstaticos: {
            carcaca: [] as string[],
            estator: [] as string[],
            rotor: [] as string[],
            auxPmg: [] as string[],
            rotorPmg: [] as string[],
        },
        testesDinamicos: {
            tipo: '', // 'VAZIO' or 'CARGA'
            vazio: [] as string[],
            carga: [] as string[],
        },
        customTiposMaquina: [] as string[],
        customTiposAtividade: [] as string[],
        customDescricoesAtividade: [] as string[],
        customTiposFalha: [] as string[],
        customTestesEstaticos: {
            carcaca: [] as string[],
            estator: [] as string[],
            rotor: [] as string[],
            auxPmg: [] as string[],
            rotorPmg: [] as string[],
        },
        customTestesDinamicos: {
            vazio: [] as string[],
            carga: [] as string[],
        },
    });
    const [errors, setErrors] = useState<any>({});

    // Estados para busca e autocomplete
    const [tiposMaquinaSearch, setTiposMaquinaSearch] = useState('');
    const [tiposAtividadeSearch, setTiposAtividadeSearch] = useState('');
    const [descricoesAtividadeSearch, setDescricoesAtividadeSearch] = useState('');
    const [tiposFalhaSearch, setTiposFalhaSearch] = useState('');
    const [testesEstaticosSearch, setTestesEstaticosSearch] = useState('');
    const [testesDinamicosSearch, setTestesDinamicosSearch] = useState('');

    // Estados para preview
    const [showPreview, setShowPreview] = useState(false);
    const [searchFilter, setSearchFilter] = useState('');

    // Estados para paginação
    const [currentPage, setCurrentPage] = useState(1);
    const itemsPerPage = 20;

    useEffect(() => {
        const fetchDepartamentos = async () => {
            try {
                const data = await departamentoService.getDepartamentos();
                setDepartamentos(data);
            } catch (error) {
                console.error('Error fetching departments:', error);
            }
        };
        fetchDepartamentos();
    }, []);

    useEffect(() => {
        if (formData.departamento) {
            const fetchSetores = async () => {
                try {
                    const data = await setorService.getSetores();
                    setSetores(data);
                } catch (error) {
                    console.error('Error fetching setores:', error);
                }
            };
            fetchSetores();
        }
    }, [formData.departamento]);

    // Funções de busca e filtro
    const filterItems = (items: string[], searchTerm: string): FilteredItem[] => {
        if (!searchTerm) return items.map(item => ({ id: item, label: item, category: 'default' }));
        
        const term = searchTerm.toLowerCase();
        return items
            .map(item => {
                const label = item.toLowerCase();
                let matchScore = 0;
                
                // Scores de correspondência
                if (label === term) matchScore += 3;
                else if (label.startsWith(term)) matchScore += 2;
                else if (label.includes(term)) matchScore += 1;
                
                return {
                    id: item,
                    label: item,
                    category: 'default',
                    matchScore
                };
            })
            .filter(item => item.matchScore)
            .sort((a, b) => (b.matchScore || 0) - (a.matchScore || 0));
    };

    const filteredTiposMaquina = filterItems(tiposMaquinaOptions, tiposMaquinaSearch);
    const filteredTiposAtividade = filterItems(tiposAtividadeOptions, tiposAtividadeSearch);
    const filteredDescricoesAtividade = filterItems(descricoesAtividadeOptions, descricoesAtividadeSearch);
    const filteredTiposFalha = filterItems(tiposFalhaOptions, tiposFalhaSearch);

    // Funções para busca em coleções aninhadas
    const filterTestes = (testesArray: any[], searchTerm: string): FilteredItem[] => {
        if (!searchTerm) return testesArray.map(test => ({ id: test.id, label: test.label, category: 'test' }));
        
        const term = searchTerm.toLowerCase();
        return testesArray
            .map(test => {
                const label = test.label.toLowerCase();
                let matchScore = 0;
                
                if (label === term) matchScore += 3;
                else if (label.startsWith(term)) matchScore += 2;
                else if (label.includes(term)) matchScore += 1;
                
                return {
                    id: test.id,
                    label: test.label,
                    category: 'test',
                    matchScore
                };
            })
            .filter(item => item.matchScore)
            .sort((a, b) => (b.matchScore || 0) - (a.matchScore || 0));
    };

    const filteredTestesCarcaça = filterTestes(testesCaCarcaça, testesEstaticosSearch);
    const filteredTestesEstator = filterTestes(testesCaEstator, testesEstaticosSearch);
    const filteredTestesRotor = filterTestes(testesCaRotor, testesEstaticosSearch);
    const filteredTestesAuxPmg = filterTestes(testesCaAuxPmg, testesEstaticosSearch);
    const filteredTestesRotorPmg = filterTestes(testesCaRotorPmg, testesEstaticosSearch);

    // Pagination
    const paginateItems = (items: FilteredItem[], page: number, limit: number) => {
        const start = (page - 1) * limit;
        return items.slice(start, start + limit);
    };

    const currentTiposMaquina = paginateItems(filteredTiposMaquina, currentPage, itemsPerPage);
    const currentTiposAtividade = paginateItems(filteredTiposAtividade, currentPage, itemsPerPage);
    const currentDescricoes = paginateItems(filteredDescricoesAtividade, currentPage, itemsPerPage);
    const currentTiposFalha = paginateItems(filteredTiposFalha, currentPage, itemsPerPage);

    // Handle changes
    const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
        const { name, value } = e.target;
        setFormData(prev => ({ ...prev, [name]: value }));
        if (errors[name]) {
            setErrors((prev: any) => ({ ...prev, [name]: undefined }));
        }
    };

    const handleCheckboxChange = (category: string, value: string, checked: boolean) => {
        setFormData(prev => {
            const current = prev[category as keyof typeof prev] as string[];
            if (checked) {
                return { ...prev, [category]: [...current, value] };
            } else {
                return { ...prev, [category]: current.filter(item => item !== value) };
            }
        });
    };

    const handleTestesEstaticosChange = (subcategory: string, value: string, checked: boolean) => {
        setFormData(prev => ({
            ...prev,
            testesEstaticos: {
                ...prev.testesEstaticos,
                [subcategory]: checked
                    ? [...(prev.testesEstaticos[subcategory as keyof typeof prev.testesEstaticos] as string[]), value]
                    : (prev.testesEstaticos[subcategory as keyof typeof prev.testesEstaticos] as string[]).filter(item => item !== value)
            }
        }));
    };

    const addCustomItem = (category: string, value: string) => {
        if (!value.trim()) return;
        const upperValue = value.toUpperCase();
        if (category.startsWith('custom')) {
            setFormData(prev => ({
                ...prev,
                [category]: [...(prev[category as keyof typeof prev] as string[]), upperValue]
            }));
            toast.success(`"${upperValue}" adicionado com sucesso!`);
        }
    };

    // Preview items
    const allSelectedItems = useMemo(() => {
        const items: SelectedItem[] = [];
        
        // Adicionar itens selecionados de cada categoria
        formData.tiposMaquina.forEach(item => {
            items.push({ id: item, label: item, category: 'Tipos de Máquina' });
        });
        
        formData.tiposAtividade.forEach(item => {
            items.push({ id: item, label: item, category: 'Tipos de Atividade' });
        });
        
        formData.descricoesAtividade.forEach(item => {
            items.push({ id: item, label: item, category: 'Descrições de Atividade' });
        });
        
        formData.tiposFalha.forEach(item => {
            items.push({ id: item, label: item, category: 'Tipos de Falha' });
        });
        
        // Adicionar testes estáticos
        Object.entries(formData.testesEstaticos).forEach(([subcategory, tests]) => {
            if (Array.isArray(tests)) {
                tests.forEach(testId => {
                    items.push({ id: testId, label: testId, category: `Testes Estáticos - ${subcategory}` });
                });
            }
        });
        
        return items;
    }, [formData]);

    const filteredPreviewItems = useMemo(() => {
        if (!searchFilter) return allSelectedItems;
        const filter = searchFilter.toLowerCase();
        return allSelectedItems.filter(item => 
            item.label.toLowerCase().includes(filter) || 
            item.category.toLowerCase().includes(filter)
        );
    }, [allSelectedItems, searchFilter]);

    const validateForm = () => {
        const newErrors: any = {};
        if (!formData.departamento) newErrors.departamento = 'Departamento é obrigatório';
        if (!formData.setor) newErrors.setor = 'Setor é obrigatório';
        setErrors(newErrors);
        return Object.keys(newErrors).length === 0;
    };

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        if (validateForm()) {
            onSubmit(formData);
        }
    };

    return (
        <div className="p-6 bg-white rounded-lg border border-gray-200 shadow-sm max-h-[80vh] overflow-y-auto">
            {/* Toast Container */}
            <ToastContainer position="top-right" autoClose={3000} hideProgressBar={false} />

            <div className="mb-6">
                <h2 className="text-2xl font-semibold text-gray-800">Criar Novo Setor Completo</h2>
                <div className="mt-2 border-b border-gray-200"></div>
            </div>

            <form onSubmit={handleSubmit} className="space-y-8">
                {/* Departamento */}
                <div>
                    <SelectField
                        id="departamento"
                        name="departamento"
                        value={formData.departamento}
                        onChange={handleInputChange}
                        label="DEPARTAMENTO *"
                        error={errors.departamento}
                        required
                    >
                        <option value="">Selecione um departamento</option>
                        {departamentos.map(dept => (
                            <option key={dept.id} value={dept.nome}>
                                {dept.nome}
                            </option>
                        ))}
                    </SelectField>
                </div>

                {/* Setor */}
                <div>
                    <SelectField
                        id="setor"
                        name="setor"
                        value={formData.setor}
                        onChange={handleInputChange}
                        label="SETOR *"
                        error={errors.setor}
                        required
                    >
                        <option value="">Selecione um setor</option>
                        {setores.map(setor => (
                            <option key={setor.id} value={setor.nome}>
                                {setor.nome}
                            </option>
                        ))}
                    </SelectField>
                </div>

                {/* Tipos de Máquina */}
                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                        TIPOS DE MAQUINAS
                    </label>
                    
                    {/* Campo de busca */}
                    <div className="relative mb-3">
                        <input
                            type="text"
                            placeholder="Buscar tipos de máquina..."
                            className="w-full p-2 border border-gray-300 rounded-md"
                            value={tiposMaquinaSearch}
                            onChange={(e) => setTiposMaquinaSearch(e.target.value)}
                        />
                        {tiposMaquinaSearch && (
                            <button
                                type="button"
                                className="absolute right-2 top-1/2 transform -translate-y-1/2 text-gray-500 hover:text-gray-700"
                                onClick={() => setTiposMaquinaSearch('')}
                            >
                                ×
                            </button>
                        )}
                    </div>

                    {/* Lista de opções com paginação */}
                    <div className="grid grid-cols-2 gap-2 max-h-60 overflow-y-auto border border-gray-200 rounded-md p-2">
                        {currentTiposMaquina.map(item => (
                            <label key={item.id} className="flex items-center text-sm">
                                <input
                                    type="checkbox"
                                    checked={formData.tiposMaquina.includes(item.id)}
                                    onChange={(e) => handleCheckboxChange('tiposMaquina', item.id, e.target.checked)}
                                    className="mr-2"
                                />
                                {item.label}
                            </label>
                        ))}
                    </div>

                    {/* Controles de paginação */}
                    <div className="flex justify-between items-center mt-2">
                        <span className="text-xs text-gray-500">
                            {tiposMaquinaSearch ? 
                                `${filteredTiposMaquina.length} resultados` : 
                                `Mostrando ${currentTiposMaquina.length} de ${tiposMaquinaOptions.length} itens`
                            }
                        </span>
                        <div className="flex space-x-1">
                            <button
                                type="button"
                                className="px-2 py-1 text-xs bg-gray-200 rounded disabled:opacity-50"
                                onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                                disabled={currentPage === 1}
                            >
                                Anterior
                            </button>
                            <span className="px-2 py-1 text-xs">{currentPage}</span>
                            <button
                                type="button"
                                className="px-2 py-1 text-xs bg-gray-200 rounded disabled:opacity-50"
                                onClick={() => setCurrentPage(p => 
                                    p < Math.ceil((tiposMaquinaSearch ? filteredTiposMaquina.length : tiposMaquinaOptions.length) / itemsPerPage) ? p + 1 : p
                                )}
                                disabled={currentPage >= Math.ceil((tiposMaquinaSearch ? filteredTiposMaquina.length : tiposMaquinaOptions.length) / itemsPerPage)}
                            >
                                Próximo
                            </button>
                        </div>
                    </div>

                    {/* Adicionar custom */}
                    <div className="mt-2 flex">
                        <input
                            type="text"
                            placeholder="Novo tipo de máquina"
                            className="flex-1 p-2 border border-gray-300 rounded-l"
                            onKeyPress={(e) => {
                                if (e.key === 'Enter') {
                                    e.preventDefault();
                                    addCustomItem('customTiposMaquina', (e.target as HTMLInputElement).value);
                                    (e.target as HTMLInputElement).value = '';
                                }
                            }}
                        />
                        <button
                            type="button"
                            className="px-3 py-2 bg-blue-500 text-white rounded-r"
                            onClick={(e) => {
                                const input = e.currentTarget.previousElementSibling as HTMLInputElement;
                                addCustomItem('customTiposMaquina', input.value);
                                input.value = '';
                            }}
                        >
                            +
                        </button>
                    </div>
                </div>

                {/* Tipo de Atividade */}
                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                        TIPO DE ATIVIDADE
                    </label>
                    
                    {/* Campo de busca */}
                    <div className="relative mb-3">
                        <input
                            type="text"
                            placeholder="Buscar tipos de atividade..."
                            className="w-full p-2 border border-gray-300 rounded-md"
                            value={tiposAtividadeSearch}
                            onChange={(e) => setTiposAtividadeSearch(e.target.value)}
                        />
                        {tiposAtividadeSearch && (
                            <button
                                type="button"
                                className="absolute right-2 top-1/2 transform -translate-y-1/2 text-gray-500 hover:text-gray-700"
                                onClick={() => setTiposAtividadeSearch('')}
                            >
                                ×
                            </button>
                        )}
                    </div>

                    {/* Lista de opções */}
                    <div className="grid grid-cols-2 gap-2 max-h-60 overflow-y-auto border border-gray-200 rounded-md p-2">
                        {currentTiposAtividade.map(item => (
                            <label key={item.id} className="flex items-center text-sm">
                                <input
                                    type="checkbox"
                                    checked={formData.tiposAtividade.includes(item.id)}
                                    onChange={(e) => handleCheckboxChange('tiposAtividade', item.id, e.target.checked)}
                                    className="mr-2"
                                />
                                {item.label}
                            </label>
                        ))}
                    </div>

                    {/* Controles de paginação */}
                    <div className="flex justify-between items-center mt-2">
                        <span className="text-xs text-gray-500">
                            {tiposAtividadeSearch ? 
                                `${filteredTiposAtividade.length} resultados` : 
                                `Mostrando ${currentTiposAtividade.length} de ${tiposAtividadeOptions.length} itens`
                            }
                        </span>
                        <div className="flex space-x-1">
                            <button
                                type="button"
                                className="px-2 py-1 text-xs bg-gray-200 rounded disabled:opacity-50"
                                onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                                disabled={currentPage === 1}
                            >
                                Anterior
                            </button>
                            <span className="px-2 py-1 text-xs">{currentPage}</span>
                            <button
                                type="button"
                                className="px-2 py-1 text-xs bg-gray-200 rounded disabled:opacity-50"
                                onClick={() => setCurrentPage(p => 
                                    p < Math.ceil((tiposAtividadeSearch ? filteredTiposAtividade.length : tiposAtividadeOptions.length) / itemsPerPage) ? p + 1 : p
                                )}
                                disabled={currentPage >= Math.ceil((tiposAtividadeSearch ? filteredTiposAtividade.length : tiposAtividadeOptions.length) / itemsPerPage)}
                            >
                                Próximo
                            </button>
                        </div>
                    </div>

                    {/* Adicionar custom */}
                    <div className="mt-2 flex">
                        <input
                            type="text"
                            placeholder="Novo tipo de atividade"
                            className="flex-1 p-2 border border-gray-300 rounded-l"
                            onKeyPress={(e) => {
                                if (e.key === 'Enter') {
                                    e.preventDefault();
                                    addCustomItem('customTiposAtividade', (e.target as HTMLInputElement).value);
                                    (e.target as HTMLInputElement).value = '';
                                }
                            }}
                        />
                        <button
                            type="button"
                            className="px-3 py-2 bg-blue-500 text-white rounded-r"
                            onClick={(e) => {
                                const input = e.currentTarget.previousElementSibling as HTMLInputElement;
                                addCustomItem('customTiposAtividade', input.value);
                                input.value = '';
                            }}
                        >
                            +
                        </button>
                    </div>
                </div>

                {/* Descrição da Atividade */}
                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                        DESCRIÇÃO DA ATIVIDADE
                    </label>
                    
                    {/* Campo de busca */}
                    <div className="relative mb-3">
                        <input
                            type="text"
                            placeholder="Buscar descrições..."
                            className="w-full p-2 border border-gray-300 rounded-md"
                            value={descricoesAtividadeSearch}
                            onChange={(e) => setDescricoesAtividadeSearch(e.target.value)}
                        />
                        {descricoesAtividadeSearch && (
                            <button
                                type="button"
                                className="absolute right-2 top-1/2 transform -translate-y-1/2 text-gray-500 hover:text-gray-700"
                                onClick={() => setDescricoesAtividadeSearch('')}
                            >
                                ×
                            </button>
                        )}
                    </div>

                    {/* Lista de opções */}
                    <div className="grid grid-cols-3 gap-2 max-h-60 overflow-y-auto border border-gray-200 rounded-md p-2">
                        {currentDescricoes.map(item => (
                            <label key={item.id} className="flex items-center text-sm">
                                <input
                                    type="checkbox"
                                    checked={formData.descricoesAtividade.includes(item.id)}
                                    onChange={(e) => handleCheckboxChange('descricoesAtividade', item.id, e.target.checked)}
                                    className="mr-2"
                                />
                                {item.label}
                            </label>
                        ))}
                    </div>

                    {/* Controles de paginação */}
                    <div className="flex justify-between items-center mt-2">
                        <span className="text-xs text-gray-500">
                            {descricoesAtividadeSearch ? 
                                `${filteredDescricoesAtividade.length} resultados` : 
                                `Mostrando ${currentDescricoes.length} de ${descricoesAtividadeOptions.length} itens`
                            }
                        </span>
                        <div className="flex space-x-1">
                            <button
                                type="button"
                                className="px-2 py-1 text-xs bg-gray-200 rounded disabled:opacity-50"
                                onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                                disabled={currentPage === 1}
                            >
                                Anterior
                            </button>
                            <span className="px-2 py-1 text-xs">{currentPage}</span>
                            <button
                                type="button"
                                className="px-2 py-1 text-xs bg-gray-200 rounded disabled:opacity-50"
                                onClick={() => setCurrentPage(p => 
                                    p < Math.ceil((descricoesAtividadeSearch ? filteredDescricoesAtividade.length : descricoesAtividadeOptions.length) / itemsPerPage) ? p + 1 : p
                                )}
                                disabled={currentPage >= Math.ceil((descricoesAtividadeSearch ? filteredDescricoesAtividade.length : descricoesAtividadeOptions.length) / itemsPerPage)}
                            >
                                Próximo
                            </button>
                        </div>
                    </div>

                    {/* Adicionar custom */}
                    <div className="mt-2 flex">
                        <input
                            type="text"
                            placeholder="Nova descrição"
                            className="flex-1 p-2 border border-gray-300 rounded-l"
                            onKeyPress={(e) => {
                                if (e.key === 'Enter') {
                                    e.preventDefault();
                                    addCustomItem('customDescricoesAtividade', (e.target as HTMLInputElement).value);
                                    (e.target as HTMLInputElement).value = '';
                                }
                            }}
                        />
                        <button
                            type="button"
                            className="px-3 py-2 bg-blue-500 text-white rounded-r"
                            onClick={(e) => {
                                const input = e.currentTarget.previousElementSibling as HTMLInputElement;
                                addCustomItem('customDescricoesAtividade', input.value);
                                input.value = '';
                            }}
                        >
                            +
                        </button>
                    </div>
                </div>

                {/* Tipos de Falha */}
                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                        TIPOS DE FALHA
                    </label>
                    
                    {/* Campo de busca */}
                    <div className="relative mb-3">
                        <input
                            type="text"
                            placeholder="Buscar tipos de falha..."
                            className="w-full p-2 border border-gray-300 rounded-md"
                            value={tiposFalhaSearch}
                            onChange={(e) => setTiposFalhaSearch(e.target.value)}
                        />
                        {tiposFalhaSearch && (
                            <button
                                type="button"
                                className="absolute right-2 top-1/2 transform -translate-y-1/2 text-gray-500 hover:text-gray-700"
                                onClick={() => setTiposFalhaSearch('')}
                            >
                                ×
                            </button>
                        )}
                    </div>

                    {/* Lista de opções com paginação */}
                    <div className="grid grid-cols-4 gap-2 max-h-60 overflow-y-auto border border-gray-200 rounded-md p-2">
                        {currentTiposFalha.map(item => (
                            <label key={item.id} className="flex items-center text-xs">
                                <input
                                    type="checkbox"
                                    checked={formData.tiposFalha.includes(item.id)}
                                    onChange={(e) => handleCheckboxChange('tiposFalha', item.id, e.target.checked)}
                                    className="mr-2"
                                />
                                {item.label}
                            </label>
                        ))}
                    </div>

                    {/* Controles de paginação */}
                    <div className="flex justify-between items-center mt-2">
                        <span className="text-xs text-gray-500">
                            {tiposFalhaSearch ? 
                                `${filteredTiposFalha.length} resultados` : 
                                `Mostrando ${currentTiposFalha.length} de ${tiposFalhaOptions.length} itens`
                            }
                        </span>
                        <div className="flex space-x-1">
                            <button
                                type="button"
                                className="px-2 py-1 text-xs bg-gray-200 rounded disabled:opacity-50"
                                onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                                disabled={currentPage === 1}
                            >
                                Anterior
                            </button>
                            <span className="px-2 py-1 text-xs">{currentPage}</span>
                            <button
                                type="button"
                                className="px-2 py-1 text-xs bg-gray-200 rounded disabled:opacity-50"
                                onClick={() => setCurrentPage(p => 
                                    p < Math.ceil((tiposFalhaSearch ? filteredTiposFalha.length : tiposFalhaOptions.length) / itemsPerPage) ? p + 1 : p
                                )}
                                disabled={currentPage >= Math.ceil((tiposFalhaSearch ? filteredTiposFalha.length : tiposFalhaOptions.length) / itemsPerPage)}
                            >
                                Próximo
                            </button>
                        </div>
                    </div>

                    {/* Adicionar custom */}
                    <div className="mt-2 flex">
                        <input
                            type="text"
                            placeholder="Novo tipo de falha"
                            className="flex-1 p-2 border border-gray-300 rounded-l"
                            onKeyPress={(e) => {
                                if (e.key === 'Enter') {
                                    e.preventDefault();
                                    addCustomItem('customTiposFalha', (e.target as HTMLInputElement).value);
                                    (e.target as HTMLInputElement).value = '';
                                }
                            }}
                        />
                        <button
                            type="button"
                            className="px-3 py-2 bg-blue-500 text-white rounded-r"
                            onClick={(e) => {
                                const input = e.currentTarget.previousElementSibling as HTMLInputElement;
                                addCustomItem('customTiposFalha', input.value);
                                input.value = '';
                            }}
                        >
                            +
                        </button>
                    </div>
                </div>

                {/* Preview Section */}
                <div className="border border-gray-200 rounded-lg p-4">
                    <div className="flex justify-between items-center mb-4">
                        <h3 className="text-lg font-medium text-gray-800">Preview dos Itens Selecionados</h3>
                        <button
                            type="button"
                            onClick={() => setShowPreview(!showPreview)}
                            className="px-3 py-1 text-sm bg-blue-500 text-white rounded hover:bg-blue-600"
                        >
                            {showPreview ? 'Ocultar' : 'Mostrar'} Preview
                        </button>
                    </div>
                    
                    {showPreview && (
                        <div>
                            {/* Campo de busca para preview */}
                            <div className="relative mb-3">
                                <input
                                    type="text"
                                    placeholder="Filtrar itens selecionados..."
                                    className="w-full p-2 border border-gray-300 rounded-md"
                                    value={searchFilter}
                                    onChange={(e) => setSearchFilter(e.target.value)}
                                />
                                {searchFilter && (
                                    <button
                                        type="button"
                                        className="absolute right-2 top-1/2 transform -translate-y-1/2 text-gray-500 hover:text-gray-700"
                                        onClick={() => setSearchFilter('')}
                                    >
                                        ×
                                    </button>
                                )}
                            </div>
                            
                            {/* Lista de itens selecionados */}
                            <div className="max-h-60 overflow-y-auto border border-gray-200 rounded-md p-2">
                                {filteredPreviewItems.length > 0 ? (
                                    <div className="grid grid-cols-1 gap-2">
                                        {filteredPreviewItems.map(item => (
                                            <div key={item.id} className="flex justify-between items-center p-2 bg-gray-50 rounded">
                                                <div>
                                                    <span className="font-medium">{item.label}</span>
                                                    <span className="text-xs text-gray-500 ml-2">({item.category})</span>
                                                </div>
                                                <button
                                                    type="button"
                                                    onClick={() => {
                                                        // Remover item selecionado
                                                        const categoryMap: Record<string, string> = {
                                                            'Tipos de Máquina': 'tiposMaquina',
                                                            'Tipos de Atividade': 'tiposAtividade',
                                                            'Descrições de Atividade': 'descricoesAtividade',
                                                            'Tipos de Falha': 'tiposFalha'
                                                        };
                                                        
                                                        const category = categoryMap[item.category];
                                                        if (category) {
                                                            setFormData(prev => ({
                                                                ...prev,
                                                                [category]: (prev[category as keyof typeof prev] as string[]).filter(id => id !== item.id)
                                                            }));
                                                        }
                                                    }}
                                                    className="text-red-500 hover:text-red-700"
                                                >
                                                    Remover
                                                </button>
                                            </div>
                                        ))}
                                    </div>
                                ) : (
                                    <p className="text-gray-500 text-center py-4">Nenhum item selecionado</p>
                                )}
                            </div>
                        </div>
                    )}
                </div>

                {/* Botões */}
                <div className="flex justify-end space-x-4 pt-6 border-t border-gray-200">
                    <button
                        type="button"
                        onClick={onCancel}
                        className="px-6 py-3 bg-gray-600 text-white font-medium rounded-md hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500 transition-colors duration-200"
                    >
                        Cancelar
                    </button>
                    <button
                        type="submit"
                        className="px-6 py-3 bg-blue-600 text-white font-medium rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                        Criar Setor Completo
                    </button>
                </div>
            </form>
        </div>
    );
};

export default FullSectorCreationForm;
