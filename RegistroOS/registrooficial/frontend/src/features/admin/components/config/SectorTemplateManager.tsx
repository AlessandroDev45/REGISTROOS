import React, { useState, useEffect } from 'react';
import { toast, ToastContainer } from 'react-toastify';
import { StyledInput, SelectField } from '../../../../components/UIComponents';

interface SectorTemplate {
    id: string;
    name: string;
    description: string;
    data: any;
    createdAt: string;
    updatedAt: string;
}

interface SectorTemplateManagerProps {
    onTemplateSelect: (templateData: any) => void;
    onCreateNew: () => void;
    onCancel: () => void;
    currentSector?: any;
}

const SectorTemplateManager: React.FC<SectorTemplateManagerProps> = ({
    onTemplateSelect,
    onCreateNew,
    onCancel,
    currentSector
}) => {
    const [templates, setTemplates] = useState<SectorTemplate[]>([]);
    const [selectedTemplate, setSelectedTemplate] = useState<string>('');
    const [isLoading, setIsLoading] = useState(true);
    const [searchTerm, setSearchTerm] = useState('');
    const [filteredTemplates, setFilteredTemplates] = useState<SectorTemplate[]>([]);

    // Templates serão carregados da API
    const [templates, setTemplates] = useState<SectorTemplate[]>([]);
                    rotor: ['ca_rotor_res_isol', 'ca_rotor_res_ohmica', 'ca_rotor_surge']
                }
            },
            createdAt: '2024-01-15',
            updatedAt: '2024-01-20'
        },
        {
            id: '2',
            name: 'Transformador Industrial',
            description: 'Template para setores que trabalham com transformadores',
            data: {
                tiposMaquina: ['MAQUINA ESTATICA CA'],
                tiposAtividade: ['TESTES INICIAIS', 'TESTES FINAIS', 'RELATORIO'],
                descricoesAtividade: ['TESTES INICIAIS COM CLIENTE', 'TESTES FINAIS INTERNOS'],
                tiposFalha: ['ISOLAMENTO RESSECADO (ESTATOR)', 'FALHA NO TESTE DE SATURACAO DO NUCLEO'],
                testesEstaticos: {
                    carcaca: ['ca_carc_inspecao_visual', 'ca_carc_supressores'],
                    estator: ['ca_estator_res_isol', 'ca_estator_impedancia', 'ca_estator_hipot']
                }
            },
            createdAt: '2024-02-10',
            updatedAt: '2024-02-15'
        }
    ];

    useEffect(() => {
        // Simular carregamento de templates
        const fetchTemplates = async () => {
            setIsLoading(true);
            try {
                // Na implementação real, chamaria a API
                // const data = await templateService.getAll();
                setTemplates(mockTemplates);
                setFilteredTemplates(mockTemplates);
            } catch (error) {
                console.error('Error fetching templates:', error);
                toast.error('Erro ao carregar templates');
            } finally {
                setIsLoading(false);
            }
        };

        fetchTemplates();
    }, []);

    useEffect(() => {
        if (searchTerm) {
            const filtered = templates.filter(template =>
                template.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                template.description.toLowerCase().includes(searchTerm.toLowerCase())
            );
            setFilteredTemplates(filtered);
        } else {
            setFilteredTemplates(templates);
        }
    }, [searchTerm, templates]);

    const handleTemplateSelect = (templateId: string) => {
        setSelectedTemplate(templateId);
    };

    const handleApplyTemplate = () => {
        if (!selectedTemplate) {
            toast.error('Por favor, selecione um template');
            return;
        }

        const template = templates.find(t => t.id === selectedTemplate);
        if (template) {
            onTemplateSelect(template.data);
            toast.success('Template aplicado com sucesso!');
        }
    };

    const handleCreateFromTemplate = () => {
        if (!selectedTemplate) {
            toast.error('Por favor, selecione um template');
            return;
        }

        const template = templates.find(t => t.id === selectedTemplate);
        if (template) {
            // Preencher o formulário com os dados do template
            if (currentSector) {
                // Se houver um setor atual, copiar os dados
                onTemplateSelect({
                    ...currentSector,
                    ...template.data
                });
            } else {
                // Criar novo com base no template
                onTemplateSelect(template.data);
            }
            toast.success('Template aplicado para criação!');
        }
    };

    const handleExportTemplate = () => {
        if (!selectedTemplate) {
            toast.error('Por favor, selecione um template');
            return;
        }

        const template = templates.find(t => t.id === selectedTemplate);
        if (template) {
            // Criar um blob com os dados do template
            const dataStr = JSON.stringify(template.data, null, 2);
            const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr);
            
            const exportFileDefaultName = `template-setor-${template.name.toLowerCase().replace(/\s+/g, '-')}.json`;
            
            const linkElement = document.createElement('a');
            linkElement.setAttribute('href', dataUri);
            linkElement.setAttribute('download', exportFileDefaultName);
            linkElement.click();
            
            toast.success('Template exportado com sucesso!');
        }
    };

    const handleDeleteTemplate = () => {
        if (!selectedTemplate) {
            toast.error('Por favor, selecione um template');
            return;
        }

        if (window.confirm('Tem certeza que deseja excluir este template?')) {
            setTemplates(prev => prev.filter(t => t.id !== selectedTemplate));
            setFilteredTemplates(prev => prev.filter(t => t.id !== selectedTemplate));
            setSelectedTemplate('');
            toast.success('Template excluído com sucesso!');
        }
    };

    return (
        <div className="p-6 bg-white rounded-lg border border-gray-200 shadow-sm max-h-[80vh] overflow-y-auto">
            <ToastContainer position="top-right" autoClose={3000} hideProgressBar={false} />

            <div className="mb-6">
                <h2 className="text-2xl font-semibold text-gray-800">Gerenciador de Templates de Setor</h2>
                <p className="text-gray-600 mt-2">Selecione um template para aplicar ou criar um novo setor baseado nele</p>
            </div>

            {/* Campo de busca */}
            <div className="mb-6">
                <div className="relative">
                    <input
                        type="text"
                        placeholder="Buscar templates..."
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

            {/* Lista de templates */}
            <div className="mb-6">
                <h3 className="text-lg font-medium text-gray-800 mb-4">Templates Disponíveis</h3>
                
                {isLoading ? (
                    <div className="flex justify-center py-8">
                        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
                    </div>
                ) : filteredTemplates.length > 0 ? (
                    <div className="space-y-3 max-h-60 overflow-y-auto">
                        {filteredTemplates.map(template => (
                            <div
                                key={template.id}
                                className={`p-4 border rounded-lg cursor-pointer transition-colors duration-200 ${
                                    selectedTemplate === template.id
                                        ? 'border-blue-500 bg-blue-50'
                                        : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
                                }`}
                                onClick={() => handleTemplateSelect(template.id)}
                            >
                                <div className="flex justify-between items-start">
                                    <div className="flex-1">
                                        <h4 className="font-medium text-gray-900">{template.name}</h4>
                                        <p className="text-sm text-gray-600 mt-1">{template.description}</p>
                                        <div className="flex items-center text-xs text-gray-500 mt-2">
                                            <span>Criado: {new Date(template.createdAt).toLocaleDateString()}</span>
                                            {template.updatedAt !== template.createdAt && (
                                                <span className="ml-3">
                                                    Atualizado: {new Date(template.updatedAt).toLocaleDateString()}
                                                </span>
                                            )}
                                        </div>
                                    </div>
                                    <div className="flex flex-col items-end">
                                        <span className="text-xs bg-gray-200 text-gray-700 px-2 py-1 rounded-full">
                                            {Object.keys(template.data.tiposMaquina || {}).length} itens
                                        </span>
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                ) : (
                    <div className="text-center py-8">
                        <p className="text-gray-500">Nenhum template encontrado</p>
                    </div>
                )}
            </div>

            {/* Botões de ação */}
            <div className="flex flex-wrap gap-3 justify-between pt-4 border-t border-gray-200">
                <div className="flex flex-wrap gap-3">
                    <button
                        type="button"
                        onClick={handleApplyTemplate}
                        disabled={!selectedTemplate}
                        className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors duration-200"
                    >
                        Aplicar Template
                    </button>
                    
                    <button
                        type="button"
                        onClick={handleCreateFromTemplate}
                        disabled={!selectedTemplate}
                        className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors duration-200"
                    >
                        Criar a partir do Template
                    </button>
                    
                    <button
                        type="button"
                        onClick={handleExportTemplate}
                        disabled={!selectedTemplate}
                        className="px-4 py-2 bg-purple-600 text-white rounded-md hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors duration-200"
                    >
                        Exportar Template
                    </button>
                    
                    <button
                        type="button"
                        onClick={handleDeleteTemplate}
                        disabled={!selectedTemplate}
                        className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors duration-200"
                    >
                        Excluir Template
                    </button>
                </div>
                
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

export default SectorTemplateManager;
