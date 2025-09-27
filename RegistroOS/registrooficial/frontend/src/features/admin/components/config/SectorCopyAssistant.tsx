import React, { useState, useEffect } from 'react';
import { toast, ToastContainer } from 'react-toastify';
import { StyledInput, SelectField } from '../../../../components/UIComponents';
import { setorService, departamentoService } from '../../../../services/adminApi';

interface SetorData {
    id: string;
    nome: string;
    departamento: string;
    descricao?: string;
    tiposMaquina: string[];
    tiposAtividade: string[];
    descricoesAtividade: string[];
    tiposFalha: string[];
    testesEstaticos: {
        carcaca: string[];
        estator: string[];
        rotor: string[];
        auxPmg: string[];
        rotorPmg: string[];
    };
    testesDinamicos: {
        tipo: string;
        vazio: string[];
        carga: string[];
    };
}

interface SectorCopyAssistantProps {
    onSectorSelect: (sectorData: SetorData) => void;
    onCreateNew: () => void;
    onCancel: () => void;
}

const SectorCopyAssistant: React.FC<SectorCopyAssistantProps> = ({
    onSectorSelect,
    onCreateNew,
    onCancel
}) => {
    const [departamentos, setDepartamentos] = useState<any[]>([]);
    const [setores, setSetores] = useState<SetorData[]>([]);
    const [selectedDepartamento, setSelectedDepartamento] = useState<string>('');
    const [searchTerm, setSearchTerm] = useState('');
    const [filteredSetores, setFilteredSetores] = useState<SetorData[]>([]);
    const [selectedSetor, setSelectedSetor] = useState<string>('');
    const [isLoading, setIsLoading] = useState(true);
    const [previewData, setPreviewData] = useState<SetorData | null>(null);
    const [showAdvancedOptions, setShowAdvancedOptions] = useState(false);
    const [selectedOptions, setSelectedOptions] = useState({
        copyTiposMaquina: true,
        copyTiposAtividade: true,
        copyDescricoesAtividade: true,
        copyTiposFalha: true,
        copyTestesEstaticos: true,
        copyTestesDinamicos: true,
        copyAll: true
    });

    useEffect(() => {
        const fetchData = async () => {
            setIsLoading(true);
            try {
                const [depts, sectors] = await Promise.all([
                    departamentoService.getDepartamentos(),
                    // Buscar setores reais da API sem dados fake
                    setorService.getSetores()
                ]);
                
                setDepartamentos(depts);
                setSetores(sectors as SetorData[]);
                setFilteredSetores(sectors as SetorData[]);
            } catch (error) {
                console.error('Error fetching data:', error);
                toast.error('Erro ao carregar dados');
            } finally {
                setIsLoading(false);
            }
        };

        fetchData();
    }, []);

    useEffect(() => {
        if (selectedDepartamento) {
            const filtered = setores.filter(setor => 
                setor.departamento === selectedDepartamento &&
                (setor.nome.toLowerCase().includes(searchTerm.toLowerCase()) ||
                 setor.descricao?.toLowerCase().includes(searchTerm.toLowerCase()))
            );
            setFilteredSetores(filtered);
        } else if (searchTerm) {
            const filtered = setores.filter(setor =>
                setor.nome.toLowerCase().includes(searchTerm.toLowerCase()) ||
                setor.descricao?.toLowerCase().includes(searchTerm.toLowerCase())
            );
            setFilteredSetores(filtered);
        } else {
            setFilteredSetores(setores);
        }
    }, [selectedDepartamento, searchTerm, setores]);

    const handleSetorSelect = (setorId: string) => {
        setSelectedSetor(setorId);
        const setor = setores.find(s => s.id === setorId);
        if (setor) {
            setPreviewData(setor);
        }
    };

    const handleAdvancedOptionChange = (option: keyof typeof selectedOptions, value: boolean) => {
        setSelectedOptions(prev => ({
            ...prev,
            [option]: value
        }));
    };

    const handleCopySector = () => {
        if (!selectedSetor) {
            toast.error('Por favor, selecione um setor para copiar');
            return;
        }

        const setor = setores.find(s => s.id === selectedSetor) as SetorData;
        if (!setor) {
            toast.error('Setor não encontrado');
            return;
        }

        // Aplicar as opções de cópia selecionadas
        let copiedData: Partial<SetorData> = {
            nome: `${setor.nome} (Cópia)`,
            departamento: setor.departamento,
            descricao: setor.descricao
        };

        if (selectedOptions.copyAll || selectedOptions.copyTiposMaquina) {
            copiedData.tiposMaquina = [...setor.tiposMaquina];
        }

        if (selectedOptions.copyAll || selectedOptions.copyTiposAtividade) {
            copiedData.tiposAtividade = [...setor.tiposAtividade];
        }

        if (selectedOptions.copyAll || selectedOptions.copyDescricoesAtividade) {
            copiedData.descricoesAtividade = [...setor.descricoesAtividade];
        }

        if (selectedOptions.copyAll || selectedOptions.copyTiposFalha) {
            copiedData.tiposFalha = [...setor.tiposFalha];
        }

        if (selectedOptions.copyAll || selectedOptions.copyTestesEstaticos) {
            copiedData.testesEstaticos = { ...setor.testesEstaticos };
        }

        if (selectedOptions.copyAll || selectedOptions.copyTestesDinamicos) {
            copiedData.testesDinamicos = { ...setor.testesDinamicos };
        }

        onSectorSelect(copiedData as SetorData);
        toast.success('Setor copiado com sucesso!');
    };

    // Função auxiliar para contar itens aninhados
    const countNestedItems = (obj: any): number => {
        if (Array.isArray(obj)) {
            return obj.length;
        } else if (typeof obj === 'object' && obj !== null) {
            return Object.values(obj).reduce((total: number, val: any) => total + countNestedItems(val), 0);
        }
        return 0;
    };

    const renderPreview = () => {
        if (!previewData) return null;

        return (
            <div className="border border-gray-200 rounded-lg p-4 bg-gray-50">
                <h4 className="font-medium text-gray-800 mb-3">Pré-visualização dos dados copiados</h4>
                
                <div className="space-y-3">
                    <div>
                        <span className="text-sm text-gray-600">Nome: </span>
                        <span className="font-medium">{previewData.nome}</span>
                    </div>
                    
                    <div>
                        <span className="text-sm text-gray-600">Departamento: </span>
                        <span className="font-medium">{previewData.departamento}</span>
                    </div>
                    
                    {previewData.descricao && (
                        <div>
                            <span className="text-sm text-gray-600">Descrição: </span>
                            <span className="font-medium">{previewData.descricao}</span>
                        </div>
                    )}
                    
                    <div>
                        <span className="text-sm text-gray-600">Tipos de Máquina: </span>
                        <span className="font-medium">{previewData.tiposMaquina.length} selecionados</span>
                    </div>
                    
                    <div>
                        <span className="text-sm text-gray-600">Tipos de Atividade: </span>
                        <span className="font-medium">{previewData.tiposAtividade.length} selecionados</span>
                    </div>
                    
                    <div>
                        <span className="text-sm text-gray-600">Descrições de Atividade: </span>
                        <span className="font-medium">{previewData.descricoesAtividade.length} selecionados</span>
                    </div>
                    
                    <div>
                        <span className="text-sm text-gray-600">Tipos de Falha: </span>
                        <span className="font-medium">{previewData.tiposFalha.length} selecionados</span>
                    </div>
                    
                    <div>
                        <span className="text-sm text-gray-600">Testes Estáticos: </span>
                        <span className="font-medium">
                            {countNestedItems(previewData.testesEstaticos)} selecionados
                        </span>
                    </div>
                    
                    <div>
                        <span className="text-sm text-gray-600">Testes Dinâmicos: </span>
                        <span className="font-medium">
                            {countNestedItems(previewData.testesDinamicos)} selecionados
                        </span>
                    </div>
                </div>
            </div>
        );
    };

    return (
        <div className="p-6 bg-white rounded-lg border border-gray-200 shadow-sm max-h-[80vh] overflow-y-auto">
            <ToastContainer position="top-right" autoClose={3000} hideProgressBar={false} />

            <div className="mb-6">
                <h2 className="text-2xl font-semibold text-gray-800">Assistente de Cópia de Setor</h2>
                <p className="text-gray-600 mt-2">Selecione um setor existente para copiar seus dados</p>
            </div>

            {/* Filtros */}
            <div className="mb-6 space-y-4">
                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                        Filtrar por Departamento (opcional)
                    </label>
                    <SelectField
                        id="departamento"
                        value={selectedDepartamento}
                        onChange={(e) => setSelectedDepartamento(e.target.value)}
                    >
                        <option value="">Todos os departamentos</option>
                        {departamentos.map(dept => (
                            <option key={dept.id} value={dept.nome}>
                                {dept.nome}
                            </option>
                        ))}
                    </SelectField>
                </div>

                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                        Buscar setores
                    </label>
                    <div className="relative">
                        <input
                            type="text"
                            placeholder="Buscar por nome ou descrição..."
                            className="w-full p-3 border border-gray-300 rounded-md"
                            value={searchTerm}
                            onChange={(e) => setSearchTerm(e.target.value)}
                        />
                        {searchTerm && (
                            <button
                                type="button"
                                className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-500 hover:text-gray-700"
                                onClick={() => setSearchTerm('')}
                            >
                                ×
                            </button>
                        )}
                    </div>
                </div>
            </div>

            {/* Lista de setores */}
            <div className="mb-6">
                <h3 className="text-lg font-medium text-gray-800 mb-4">Setores Disponíveis</h3>
                
                {isLoading ? (
                    <div className="flex justify-center py-8">
                        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
                    </div>
                ) : filteredSetores.length > 0 ? (
                    <div className="space-y-3 max-h-60 overflow-y-auto">
                        {filteredSetores.map(setor => (
                            <div
                                key={setor.id}
                                className={`p-4 border rounded-lg cursor-pointer transition-colors duration-200 ${
                                    selectedSetor === setor.id
                                        ? 'border-blue-500 bg-blue-50'
                                        : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
                                }`}
                                onClick={() => handleSetorSelect(setor.id)}
                            >
                                <div className="flex justify-between items-start">
                                    <div className="flex-1">
                                        <h4 className="font-medium text-gray-900">{setor.nome}</h4>
                                        <p className="text-sm text-gray-600 mt-1">
                                            Departamento: {setor.departamento}
                                        </p>
                                        {setor.descricao && (
                                            <p className="text-sm text-gray-500 mt-1">{setor.descricao}</p>
                                        )}
                                        <div className="flex items-center text-xs text-gray-500 mt-2 space-x-3">
                                            <span>{setor.tiposMaquina.length} tipos de máquina</span>
                                            <span>{setor.tiposAtividade.length} tipos de atividade</span>
                                            <span>{setor.tiposFalha.length} tipos de falha</span>
                                        </div>
                                    </div>
                                    <div className="text-xs bg-gray-100 text-gray-600 px-2 py-1 rounded-full">
                                        {countNestedItems(setor.testesEstaticos) + 
                                         countNestedItems(setor.testesDinamicos)} testes
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                ) : (
                    <div className="text-center py-8">
                        <p className="text-gray-500">Nenhum setor encontrado</p>
                    </div>
                )}
            </div>

            {/* Pré-visualização */}
            {previewData && renderPreview()}

            {/* Opções avançadas */}
            <div className="mb-6">
                <button
                    type="button"
                    onClick={() => setShowAdvancedOptions(!showAdvancedOptions)}
                    className="flex items-center text-sm text-blue-600 hover:text-blue-800"
                >
                    {showAdvancedOptions ? 'Ocultar' : 'Mostrar'} opções avançadas de cópia
                    <svg
                        className={`ml-2 w-4 h-4 transition-transform duration-200 ${
                            showAdvancedOptions ? 'rotate-180' : ''
                        }`}
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                    >
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                    </svg>
                </button>

                {showAdvancedOptions && (
                    <div className="mt-4 p-4 border border-gray-200 rounded-lg bg-gray-50">
                        <h4 className="font-medium text-gray-800 mb-3">O que deseja copiar?</h4>
                        
                        <div className="space-y-2">
                            {[
                                { id: 'copyAll', label: 'Copiar tudo (recomendado)' },
                                { id: 'copyTiposMaquina', label: 'Tipos de Máquina' },
                                { id: 'copyTiposAtividade', label: 'Tipos de Atividade' },
                                { id: 'copyDescricoesAtividade', label: 'Descrições de Atividade' },
                                { id: 'copyTiposFalha', label: 'Tipos de Falha' },
                                { id: 'copyTestesEstaticos', label: 'Testes Estáticos' },
                                { id: 'copyTestesDinamicos', label: 'Testes Dinâmicos' }
                            ].map(option => (
                                <label key={option.id} className="flex items-center">
                                    <input
                                        type="checkbox"
                                        checked={selectedOptions[option.id as keyof typeof selectedOptions]}
                                        onChange={(e) => handleAdvancedOptionChange(
                                            option.id as keyof typeof selectedOptions, 
                                            e.target.checked
                                        )}
                                        className="mr-2"
                                    />
                                    <span className="text-sm">{option.label}</span>
                                </label>
                            ))}
                        </div>
                    </div>
                )}
            </div>

            {/* Botões de ação */}
            <div className="flex flex-wrap gap-3 justify-between pt-4 border-t border-gray-200">
                <button
                    type="button"
                    onClick={handleCopySector}
                    disabled={!selectedSetor}
                    className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors duration-200"
                >
                    Copiar Setor
                </button>
                
                <div className="flex gap-3">
                    <button
                        type="button"
                        onClick={onCreateNew}
                        className="px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700 transition-colors duration-200"
                    >
                        Criar Novo do Zero
                    </button>
                    
                    <button
                        type="button"
                        onClick={onCancel}
                        className="px-4 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50 transition-colors duration-200"
                    >
                        Cancelar
                    </button>
                </div>
            </div>
        </div>
    );
};

export default SectorCopyAssistant;
