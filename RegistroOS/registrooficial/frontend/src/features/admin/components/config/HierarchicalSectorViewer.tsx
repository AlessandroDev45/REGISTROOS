import React, { useState, useEffect } from 'react';
import { useAuth } from '../../../../contexts/AuthContext';
import api from '../../../../services/api';

interface TipoTeste {
  id: number;
  nome_tipo: string;
  descricao?: string;
}

interface TipoMaquina {
  id: number;
  nome_tipo: string;
  categoria?: string;
  descricao?: string;
  tipos_teste: TipoTeste[];
}

interface TipoAtividade {
  id: number;
  nome_tipo: string;
  descricao?: string;
  id_tipo_maquina?: number;
}

interface DescricaoAtividade {
  id: number;
  codigo: string;
  descricao: string;
}

interface TipoFalha {
  id: number;
  codigo: string;
  descricao: string;
}

interface CausaRetrabalho {
  id: number;
  codigo: string;
  descricao: string;
}

interface SetorData {
  id: number;
  nome: string;
  descricao?: string;
  tipos_maquina: TipoMaquina[];
  tipos_atividade: TipoAtividade[];
  descricoes_atividade: DescricaoAtividade[];
  tipos_falha: TipoFalha[];
  causas_retrabalho: CausaRetrabalho[];
}

interface DepartamentoData {
  id: number;
  nome: string;
  descricao?: string;
  setores: SetorData[];
}

interface EstruturaResponse {
  estrutura: DepartamentoData[];
  total_departamentos: number;
  filtros_aplicados: {
    departamento?: string;
    setor?: string;
    usuario_privilege: string;
  };
}

interface HierarchicalSectorViewerProps {
    onSelectItem?: (item: any) => void;
    selectedItemId?: string;
    height?: string;
}

const HierarchicalSectorViewer: React.FC<HierarchicalSectorViewerProps> = ({
    onSelectItem,
    selectedItemId,
    height = '500px'
}) => {
    console.log('🌳 Admin HierarchicalSectorViewer renderizado');
    const { user } = useAuth();
    const [estrutura, setEstrutura] = useState<DepartamentoData[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [expandedDepartments, setExpandedDepartments] = useState<Set<number>>(new Set());
    const [expandedSectors, setExpandedSectors] = useState<Set<number>>(new Set());
    const [selectedFilters, setSelectedFilters] = useState({
        departamento: '',
        setor: ''
    });

    useEffect(() => {
        loadEstrutura();
    }, [selectedFilters]);

    const loadEstrutura = async () => {
        try {
            setLoading(true);
            setError(null);

            const params = new URLSearchParams();
            if (selectedFilters.departamento) {
                params.append('departamento', selectedFilters.departamento);
            }
            if (selectedFilters.setor) {
                params.append('setor', selectedFilters.setor);
            }

            const response = await api.get(`/estrutura-hierarquica-debug?${params.toString()}`);
            const data: EstruturaResponse = response.data;
            setEstrutura(data.estrutura);

            // Auto-expandir se houver apenas um departamento
            if (data.estrutura.length === 1) {
                setExpandedDepartments(new Set([data.estrutura[0].id]));
                // Auto-expandir se houver apenas um setor
                if (data.estrutura[0].setores.length === 1) {
                    setExpandedSectors(new Set([data.estrutura[0].setores[0].id]));
                }
            }

        } catch (error: any) {
            console.error('Erro ao carregar estrutura hierárquica:', error);

            // Se for erro de autenticação, mostrar mensagem específica
            if (error.response?.status === 401) {
                setError('Usuário não autenticado. Faça login para acessar a estrutura hierárquica.');
            } else if (error.response?.status === 403) {
                setError('Acesso negado. Você não tem permissão para visualizar a estrutura hierárquica.');
            } else {
                setError(`Erro ao carregar dados da estrutura hierárquica: ${error.response?.data?.detail || error.message}`);
            }
        } finally {
            setLoading(false);
        }
    };

    const toggleDepartment = (deptId: number, event?: React.MouseEvent) => {
        console.log('🏢 Admin - CLIQUE NO DEPARTAMENTO - ID:', deptId, 'Event:', event);

        if (event) {
            event.preventDefault();
            event.stopPropagation();
            event.nativeEvent?.stopImmediatePropagation?.();
            console.log('🛑 Admin - Eventos bloqueados para departamento');
        }

        const newExpanded = new Set(expandedDepartments);
        if (newExpanded.has(deptId)) {
            newExpanded.delete(deptId);
            console.log('📁 Admin - Departamento contraído:', deptId);
        } else {
            newExpanded.add(deptId);
            console.log('📂 Admin - Departamento expandido:', deptId);
        }
        setExpandedDepartments(newExpanded);
    };

    const toggleSector = (sectorId: number, event?: React.MouseEvent) => {
        console.log('🏭 Admin - CLIQUE NO SETOR - ID:', sectorId, 'Event:', event);

        if (event) {
            event.preventDefault();
            event.stopPropagation();
            event.nativeEvent?.stopImmediatePropagation?.();
            console.log('🛑 Admin - Eventos bloqueados para setor');
        }

        const newExpanded = new Set(expandedSectors);
        if (newExpanded.has(sectorId)) {
            newExpanded.delete(sectorId);
            console.log('📁 Admin - Setor contraído:', sectorId);
        } else {
            newExpanded.add(sectorId);
            console.log('📂 Admin - Setor expandido:', sectorId);
        }
        setExpandedSectors(newExpanded);
    };

    const handleSectorSelect = (setor: any, event?: React.MouseEvent) => {
        console.log('🎯 Admin - SELEÇÃO DE SETOR:', setor.nome, setor.id);

        if (event) {
            event.preventDefault();
            event.stopPropagation();
        }

        // Apenas selecionar o setor, não navegar
        if (onSelectItem) {
            onSelectItem({
                id: setor.id,
                name: setor.nome,
                type: 'setor',
                data: setor
            });
        }
    };

    const renderTreeIcon = (isExpanded: boolean) => (
        <span className="text-gray-400 mr-2">
            {isExpanded ? '📂' : '📁'}
        </span>
    );

    const renderMachineTypes = (tipos: TipoMaquina[]) => (
        <div className="ml-8 mt-2">
            <div className="text-sm font-medium text-gray-700 mb-2">
                🔧 TIPOS DE MÁQUINA ({tipos.length})
            </div>
            {tipos.map((tipo) => (
                <div key={tipo.id} className="ml-4 mb-2">
                    <div className="text-sm text-gray-600">
                        ├── {tipo.nome_tipo}
                        {tipo.categoria && <span className="text-gray-500"> ({tipo.categoria})</span>}
                    </div>
                    {tipo.tipos_teste.length > 0 && (
                        <div className="ml-4 mt-1">
                            <div className="text-xs text-gray-500 mb-1">└── TIPOS DE TESTE ({tipo.tipos_teste.length})</div>
                            {tipo.tipos_teste.map((teste) => (
                                <div key={teste.id} className="ml-6 text-xs text-gray-500">
                                    └── {teste.nome_tipo}
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            ))}
        </div>
    );

    const renderActivities = (atividades: TipoAtividade[]) => (
        <div className="ml-8 mt-2">
            <div className="text-sm font-medium text-gray-700 mb-2">
                ⚙️ TIPOS DE ATIVIDADE ({atividades.length})
            </div>
            {atividades.map((atividade) => (
                <div key={atividade.id} className="ml-4 text-sm text-gray-600">
                    ├── {atividade.nome_tipo}
                </div>
            ))}
        </div>
    );

    const renderActivityDescriptions = (descricoes: DescricaoAtividade[]) => (
        <div className="ml-8 mt-2">
            <div className="text-sm font-medium text-gray-700 mb-2">
                📝 DESCRIÇÕES DE ATIVIDADE ({descricoes.length})
            </div>
            {descricoes.map((desc) => (
                <div key={desc.id} className="ml-4 text-sm text-gray-600">
                    ├── {desc.codigo}: {desc.descricao}
                </div>
            ))}
        </div>
    );

    const renderFailureTypes = (falhas: TipoFalha[]) => (
        <div className="ml-8 mt-2">
            <div className="text-sm font-medium text-gray-700 mb-2">
                ⚠️ TIPOS DE FALHA ({falhas.length})
            </div>
            {falhas.map((falha) => (
                <div key={falha.id} className="ml-4 text-sm text-gray-600">
                    ├── {falha.codigo}: {falha.descricao}
                </div>
            ))}
        </div>
    );

    const renderReworkCauses = (causas: CausaRetrabalho[]) => (
        <div className="ml-8 mt-2">
            <div className="text-sm font-medium text-gray-700 mb-2">
                🔄 CAUSAS DE RETRABALHO ({causas.length})
            </div>
            {causas.map((causa) => (
                <div key={causa.id} className="ml-4 text-sm text-gray-600">
                    ├── {causa.codigo}: {causa.descricao}
                </div>
            ))}
        </div>
    );

    if (loading) {
        return (
            <div className="flex items-center justify-center p-8" style={{ height }}>
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
                <span className="ml-2">Carregando estrutura hierárquica...</span>
            </div>
        );
    }

    if (error) {
        return (
            <div className="p-6" style={{ height }}>
                <div className="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
                    <div className="text-red-500 text-5xl mb-3">❌</div>
                    <h3 className="text-lg font-medium text-red-800 mb-2">Erro ao Carregar</h3>
                    <p className="text-red-700 mb-4">{error}</p>
                    <button
                        onClick={loadEstrutura}
                        className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700"
                    >
                        Tentar Novamente
                    </button>
                </div>
            </div>
        );
    }

    return (
        <div className="bg-white border border-gray-200 rounded-lg shadow-sm" style={{ height }}>
            <div className="p-4 border-b border-gray-200">
                <h3 className="text-lg font-semibold text-gray-900 mb-2">
                    🌳 Estrutura Hierárquica
                </h3>
                <p className="text-sm text-gray-600">
                    Visualização completa da estrutura organizacional: Departamentos → Setores → Tipos de Máquina → Atividades → Testes → Falhas → Retrabalho
                </p>
            </div>

            {/* Filtros */}
            {user?.privilege_level === 'ADMIN' && (
                <div className="p-4 border-b border-gray-200 bg-gray-50">
                    <h4 className="font-medium text-gray-900 mb-4">Filtros (Apenas Admin)</h4>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">Departamento</label>
                            <input
                                type="text"
                                value={selectedFilters.departamento}
                                onChange={(e) => setSelectedFilters(prev => ({ ...prev, departamento: e.target.value }))}
                                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                                placeholder="Filtrar por departamento..."
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">Setor</label>
                            <input
                                type="text"
                                value={selectedFilters.setor}
                                onChange={(e) => setSelectedFilters(prev => ({ ...prev, setor: e.target.value }))}
                                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                                placeholder="Filtrar por setor..."
                            />
                        </div>
                    </div>
                    <button
                        onClick={() => setSelectedFilters({ departamento: '', setor: '' })}
                        className="mt-4 px-4 py-2 bg-gray-600 text-white rounded hover:bg-gray-700"
                    >
                        Limpar Filtros
                    </button>
                </div>
            )}

            {/* Estrutura */}
            <div className="p-4 overflow-y-auto" style={{ maxHeight: 'calc(100% - 200px)' }}>
                {estrutura.length === 0 ? (
                    <div className="text-center py-12">
                        <div className="text-gray-400 text-6xl mb-4">🏗️</div>
                        <h3 className="text-lg font-medium text-gray-900 mb-2">
                            Nenhuma estrutura encontrada
                        </h3>
                        <p className="text-gray-500">
                            Não há dados disponíveis para os filtros aplicados.
                        </p>
                    </div>
                ) : (
                    <div className="space-y-4">
                        {estrutura.map((departamento) => (
                            <div key={departamento.id} className="border border-gray-200 rounded-lg">
                                <div
                                    className="p-4 bg-blue-50 cursor-pointer hover:bg-blue-100 transition-colors"
                                    onClick={(e) => {
                                        console.log('🎯 Admin - CLIQUE DIRETO NO DEPARTAMENTO:', departamento.nome, departamento.id);
                                        e.preventDefault();
                                        e.stopPropagation();
                                        e.nativeEvent?.stopImmediatePropagation?.();
                                        toggleDepartment(departamento.id, e);
                                        return false;
                                    }}
                                    onMouseDown={(e) => {
                                        console.log('🖱️ Admin - MOUSE DOWN NO DEPARTAMENTO:', departamento.nome);
                                        e.preventDefault();
                                        e.stopPropagation();
                                    }}
                                >
                                    <div className="flex items-center">
                                        {renderTreeIcon(expandedDepartments.has(departamento.id))}
                                        <h3 className="text-lg font-semibold text-blue-900">
                                            DEPARTAMENTO ({departamento.nome.toUpperCase()})
                                        </h3>
                                        <span className="ml-2 text-sm text-blue-700">
                                            ({departamento.setores.length} setores)
                                        </span>
                                    </div>
                                    {departamento.descricao && (
                                        <p className="text-sm text-blue-700 mt-1 ml-6">{departamento.descricao}</p>
                                    )}
                                </div>

                                {expandedDepartments.has(departamento.id) && (
                                    <div className="p-4 border-t border-gray-200">
                                        {departamento.setores.map((setor) => (
                                            <div key={setor.id} className="mb-4 border-l-2 border-gray-300 pl-4">
                                                <div className="flex items-center justify-between p-2 rounded hover:bg-gray-50">
                                                    <div
                                                        className="flex items-center cursor-pointer flex-1"
                                                        onClick={(e) => {
                                                            console.log('🎯 Admin - CLIQUE NO HEADER DO SETOR:', setor.nome, setor.id);
                                                            e.preventDefault();
                                                            e.stopPropagation();
                                                            toggleSector(setor.id, e);
                                                        }}
                                                    >
                                                        {renderTreeIcon(expandedSectors.has(setor.id))}
                                                        <span className="font-medium text-green-700">
                                                            🏭 {setor.nome}
                                                        </span>
                                                        {setor.descricao && (
                                                            <span className="ml-2 text-sm text-gray-500">
                                                                - {setor.descricao}
                                                            </span>
                                                        )}
                                                    </div>
                                                    <button
                                                        onClick={(e) => handleSectorSelect(setor, e)}
                                                        className="ml-2 px-3 py-1 text-xs bg-green-100 text-green-700 rounded hover:bg-green-200"
                                                        title="Selecionar este setor"
                                                    >
                                                        Selecionar
                                                    </button>
                                                </div>

                                                {expandedSectors.has(setor.id) && (
                                                    <div className="mt-2 ml-4 border-l-2 border-gray-200 pl-4">
                                                        <div className="flex items-center mb-2">
                                                            {renderTreeIcon(true)}
                                                            <h4 className="text-md font-medium text-gray-800">
                                                                📋 DETALHES DO SETOR ({setor.nome})
                                                            </h4>
                                                        </div>
                                                        {setor.descricao && (
                                                            <p className="text-sm text-gray-600 mb-3 ml-6">{setor.descricao}</p>
                                                        )}

                                                        {setor.tipos_maquina && setor.tipos_maquina.length > 0 && renderMachineTypes(setor.tipos_maquina)}
                                                        {setor.tipos_atividade && setor.tipos_atividade.length > 0 && renderActivities(setor.tipos_atividade)}
                                                        {setor.descricoes_atividade && setor.descricoes_atividade.length > 0 && renderActivityDescriptions(setor.descricoes_atividade)}
                                                        {setor.tipos_falha && setor.tipos_falha.length > 0 && renderFailureTypes(setor.tipos_falha)}
                                                        {setor.causas_retrabalho && setor.causas_retrabalho.length > 0 && renderReworkCauses(setor.causas_retrabalho)}
                                                    </div>
                                                )}
                                            </div>
                                        ))}
                                    </div>
                                )}
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
};

export default HierarchicalSectorViewer;
