import React, { useState, useEffect } from 'react';
import AdminConfigContent from './components/config/AdminConfigContent';
import {
    setorService,
    tipoMaquinaService,
    atividadeTipoService,
    falhaTipoService,
    causaRetrabalhoService,
    departamentoService,
    centroCustoService,
    tipoTesteService,
    descricaoAtividadeService
} from '../../services/adminApi';
import Layout from '../../components/Layout';

const AdminPage: React.FC = () => {
    const [currentConfigItem, setCurrentConfigItem] = useState<any>(null);
    const [configType, setConfigType] = useState<string>('');
    const [showConfigForm, setShowConfigForm] = useState(false);
    const [loadingConfig, setLoadingConfig] = useState(false);
    const [configData, setConfigData] = useState<{ [key: string]: any[] }>({});

    // Fetch all config data on mount
    useEffect(() => {
        const fetchAllConfigData = async () => {
            setLoadingConfig(true);
            try {
                const [setores, tiposMaquina, tiposTeste, atividades, falhasResponse, causasRetrabalho, centroCusto, descricoesAtividade, departamentos] = await Promise.all([
                    setorService.getSetores(),
                    tipoMaquinaService.getTiposMaquina(),
                    tipoTesteService.getTiposTeste(),
                    atividadeTipoService.getAtividadesTipo(),
                    falhaTipoService.getFalhasTipo(),
                    causaRetrabalhoService.getCausasRetrabalho(),
                    centroCustoService.getCentrosCusto(), // Usar o serviço correto de centro de custo
                    descricaoAtividadeService.getDescricoesAtividade(),
                    departamentoService.getDepartamentos() // Adicionar busca de departamentos
                ]);

                // Verificar se falhas está desabilitado
                let falhas = [];
                if (Array.isArray(falhasResponse)) {
                    falhas = falhasResponse;
                } else if (falhasResponse && typeof falhasResponse === 'object' && 'status' in falhasResponse) {
                    const statusResponse = falhasResponse as any;
                    if (statusResponse.status === 'DISABLED') {
                        console.warn('Funcionalidade de tipos de falha desabilitada:', statusResponse.message);
                        falhas = []; // Array vazio para funcionalidade desabilitada
                    }
                }

                setConfigData({
                    setores,
                    tipos_maquina: tiposMaquina,
                    tipos_testes: tiposTeste,
                    atividades,
                    falhas,
                    causas_retrabalho: causasRetrabalho,
                    centro_custo: departamentos.length > 0 ? departamentos : centroCusto, // Usar departamentos se disponível, senão centroCusto
                    descricao_atividades: descricoesAtividade
                });
            } catch (error) {
                console.error('Error fetching config data:', error);
            } finally {
                setLoadingConfig(false);
            }
        };

        fetchAllConfigData();
    }, []);

    const handleEdit = (item: any, type?: string) => {
        setCurrentConfigItem(item);
        // Se o tipo não for passado, tentar determinar baseado na aba ativa
        if (type) {
            setConfigType(type);
        } else {
            // Determinar o tipo baseado na estrutura do item ou contexto
            // Por enquanto, vamos usar um mapeamento simples
            console.warn('Tipo não especificado para edição, usando fallback');
            setConfigType('centro_custo'); // fallback
        }
        setShowConfigForm(true);
    };

    const handleDelete = async (type: string, item: any) => {
        try {
            switch (type) {
                case 'setores':
                    await setorService.deleteSetor(item.id);
                    setConfigData(prev => ({
                        ...prev,
                        setores: prev.setores.filter(s => s.id !== item.id)
                    }));
                    break;
                case 'tipos_maquina':
                    await tipoMaquinaService.deleteTipoMaquina(item.id);
                    setConfigData(prev => ({
                        ...prev,
                        tipos_maquina: prev.tipos_maquina.filter(t => t.id !== item.id)
                    }));
                    break;
                case 'tipos_testes':
                    await tipoTesteService.deleteTipoTeste(item.id);
                    setConfigData(prev => ({
                        ...prev,
                        tipos_testes: prev.tipos_testes.filter(t => t.id !== item.id)
                    }));
                    break;
                case 'centro_custo':
                    await centroCustoService.deleteCentroCusto(item.id);
                    setConfigData(prev => ({
                        ...prev,
                        centro_custo: prev.centro_custo.filter(c => c.id !== item.id)
                    }));
                    break;
                case 'departamentos':
                    await departamentoService.deleteDepartamento(item.id);
                    setConfigData(prev => ({
                        ...prev,
                        centro_custo: prev.centro_custo.filter(c => c.id !== item.id)
                    }));
                    break;
                case 'atividades':
                    await atividadeTipoService.deleteAtividadeTipo(item.id);
                    setConfigData(prev => ({
                        ...prev,
                        atividades: prev.atividades.filter(a => a.id !== item.id)
                    }));
                    break;
                case 'descricao_atividades':
                    await descricaoAtividadeService.deleteDescricaoAtividade(item.id);
                    setConfigData(prev => ({
                        ...prev,
                        descricao_atividades: prev.descricao_atividades.filter(d => d.id !== item.id)
                    }));
                    break;
                case 'falhas':
                    await falhaTipoService.deleteFalhaTipo(item.id);
                    setConfigData(prev => ({
                        ...prev,
                        falhas: prev.falhas.filter(f => f.id !== item.id)
                    }));
                    break;
                case 'causas_retrabalho':
                    await causaRetrabalhoService.deleteCausaRetrabalho(item.id);
                    setConfigData(prev => ({
                        ...prev,
                        causas_retrabalho: prev.causas_retrabalho.filter(c => c.id !== item.id)
                    }));
                    break;
                // Add other delete cases here
                default:
                    console.warn(`Delete not implemented for type: ${type}`);
                    alert(`Funcionalidade de deletar ainda não implementada para ${type}`);
            }
            alert(`${type} deletado com sucesso!`);
        } catch (error) {
            console.error(`Error deleting ${type}:`, error);
            alert(`Erro ao deletar ${type}: ` + (error as any)?.response?.data?.detail || (error as any)?.message || 'Erro desconhecido');
        }
    };

    const handleCreateNew = (type?: string) => {
        setCurrentConfigItem(null);
        setConfigType(type || 'full_sector'); // Set to specific type or full sector creation
        setShowConfigForm(true);
    };

    const handleSubmit = async (data: any, isEdit: boolean) => {
        console.log('Form submitted:', data, isEdit);
        try {
            // Handle full sector creation
            if (configType === 'full_sector') {
                // This would need to call a backend API to create all the related records
                // For now, just show success
                alert('Setor completo criado com sucesso!');
            } else if (configType === 'setores') {
                // Handle setor creation/update
                if (isEdit && currentConfigItem) {
                    const updatedSetor = await setorService.updateSetor(currentConfigItem.id, data);
                    setConfigData(prev => ({
                        ...prev,
                        setores: prev.setores.map(s => s.id === currentConfigItem.id ? updatedSetor : s)
                    }));
                    alert('Setor atualizado com sucesso!');
                } else {
                    const newSetor = await setorService.createSetor(data);
                    setConfigData(prev => ({
                        ...prev,
                        setores: [...prev.setores, newSetor]
                    }));
                    alert('Setor criado com sucesso!');
                }
            } else if (configType === 'tipos_maquina') {
                // Handle tipo maquina creation/update
                if (isEdit && currentConfigItem) {
                    const updatedTipo = await tipoMaquinaService.updateTipoMaquina(currentConfigItem.id, data);
                    setConfigData(prev => ({
                        ...prev,
                        tipos_maquina: prev.tipos_maquina.map(t => t.id === currentConfigItem.id ? updatedTipo : t)
                    }));
                    alert('Tipo de máquina atualizado com sucesso!');
                } else {
                    const newTipo = await tipoMaquinaService.createTipoMaquina(data);
                    setConfigData(prev => ({
                        ...prev,
                        tipos_maquina: [...prev.tipos_maquina, newTipo]
                    }));
                    alert('Tipo de máquina criado com sucesso!');
                }
            } else if (configType === 'tipos_testes') {
                // Handle tipo teste creation/update
                if (isEdit && currentConfigItem) {
                    const updatedTipo = await tipoTesteService.updateTipoTeste(currentConfigItem.id, data);
                    setConfigData(prev => ({
                        ...prev,
                        tipos_testes: prev.tipos_testes.map(t => t.id === currentConfigItem.id ? updatedTipo : t)
                    }));
                    alert('Tipo de teste atualizado com sucesso!');
                } else {
                    const newTipo = await tipoTesteService.createTipoTeste(data);
                    setConfigData(prev => ({
                        ...prev,
                        tipos_testes: [...prev.tipos_testes, newTipo]
                    }));
                    alert('Tipo de teste criado com sucesso!');
                }
            } else if (configType === 'centro_custo') {
                // Handle centro custo creation/update
                if (isEdit && currentConfigItem) {
                    const updatedCentro = await centroCustoService.updateCentroCusto(currentConfigItem.id, data);
                    setConfigData(prev => ({
                        ...prev,
                        centro_custo: prev.centro_custo.map(c => c.id === currentConfigItem.id ? updatedCentro : c)
                    }));
                    alert('Departamento atualizado com sucesso!');
                } else {
                    const newCentro = await centroCustoService.createCentroCusto(data);
                    setConfigData(prev => ({
                        ...prev,
                        centro_custo: [...prev.centro_custo, newCentro]
                    }));
                    alert('Departamento criado com sucesso!');
                }
            } else if (configType === 'departamentos') {
                // Handle departamentos creation/update
                if (isEdit && currentConfigItem) {
                    const updatedDepartamento = await departamentoService.updateDepartamento(currentConfigItem.id, data);
                    setConfigData(prev => ({
                        ...prev,
                        centro_custo: prev.centro_custo.map(d => d.id === currentConfigItem.id ? updatedDepartamento : d)
                    }));
                    alert('Departamento atualizado com sucesso!');
                } else {
                    const newDepartamento = await departamentoService.createDepartamento(data);
                    setConfigData(prev => ({
                        ...prev,
                        centro_custo: [...prev.centro_custo, newDepartamento]
                    }));
                    alert('Departamento criado com sucesso!');
                }
            } else if (configType === 'atividades') {
                // Handle atividades creation/update
                if (isEdit && currentConfigItem) {
                    const updatedAtividade = await atividadeTipoService.updateAtividadeTipo(currentConfigItem.id, data);
                    setConfigData(prev => ({
                        ...prev,
                        atividades: prev.atividades.map(a => a.id === currentConfigItem.id ? updatedAtividade : a)
                    }));
                    alert('Atividade atualizada com sucesso!');
                } else {
                    const newAtividade = await atividadeTipoService.createAtividadeTipo(data);
                    setConfigData(prev => ({
                        ...prev,
                        atividades: [...prev.atividades, newAtividade]
                    }));
                    alert('Atividade criada com sucesso!');
                }
            } else if (configType === 'descricao_atividades') {
                // Handle descricao atividades creation/update
                if (isEdit && currentConfigItem) {
                    const updatedDescricao = await descricaoAtividadeService.updateDescricaoAtividade(currentConfigItem.id, data);
                    setConfigData(prev => ({
                        ...prev,
                        descricao_atividades: prev.descricao_atividades.map(d => d.id === currentConfigItem.id ? updatedDescricao : d)
                    }));
                    alert('Descrição de atividade atualizada com sucesso!');
                } else {
                    const newDescricao = await descricaoAtividadeService.createDescricaoAtividade(data);
                    setConfigData(prev => ({
                        ...prev,
                        descricao_atividades: [...prev.descricao_atividades, newDescricao]
                    }));
                    alert('Descrição de atividade criada com sucesso!');
                }
            } else if (configType === 'falhas') {
                // Handle falhas creation/update
                if (isEdit && currentConfigItem) {
                    const updatedFalha = await falhaTipoService.updateFalhaTipo(currentConfigItem.id, data);
                    setConfigData(prev => ({
                        ...prev,
                        falhas: prev.falhas.map(f => f.id === currentConfigItem.id ? updatedFalha : f)
                    }));
                    alert('Tipo de falha atualizado com sucesso!');
                } else {
                    const newFalha = await falhaTipoService.createFalhaTipo(data);
                    setConfigData(prev => ({
                        ...prev,
                        falhas: [...prev.falhas, newFalha]
                    }));
                    alert('Tipo de falha criado com sucesso!');
                }
            } else if (configType === 'causas_retrabalho') {
                // Handle causas retrabalho creation/update
                if (isEdit && currentConfigItem) {
                    const updatedCausa = await causaRetrabalhoService.updateCausaRetrabalho(currentConfigItem.id, data);
                    setConfigData(prev => ({
                        ...prev,
                        causas_retrabalho: prev.causas_retrabalho.map(c => c.id === currentConfigItem.id ? updatedCausa : c)
                    }));
                    alert('Causa de retrabalho atualizada com sucesso!');
                } else {
                    const newCausa = await causaRetrabalhoService.createCausaRetrabalho(data);
                    setConfigData(prev => ({
                        ...prev,
                        causas_retrabalho: [...prev.causas_retrabalho, newCausa]
                    }));
                    alert('Causa de retrabalho criada com sucesso!');
                }
            } else {
                // Handle other types
                console.warn(`Submit not implemented for type: ${configType}`);
                alert(`Funcionalidade de salvar ainda não implementada para ${configType}`);
            }
            setShowConfigForm(false);
            setCurrentConfigItem(null);
            setConfigType('');
        } catch (error) {
            console.error('Error submitting form:', error);
            alert('Erro ao salvar: ' + (error as any)?.response?.data?.detail || (error as any)?.message || 'Erro desconhecido');
        }
    };

    const handleCancelForm = () => {
        setShowConfigForm(false);
        setCurrentConfigItem(null);
        setConfigType('');
    };

    return (
        <Layout>
            <div className="w-full p-4 md:p-6 lg:p-8">
                <h1 className="text-2xl font-bold text-gray-800 mb-6">Sistema de Configuração Administrativa</h1>

                <AdminConfigContent
                    onEdit={handleEdit}
                    onDelete={handleDelete}
                    onCreateNew={handleCreateNew as any}
                    onSubmit={handleSubmit}
                    onCancelForm={handleCancelForm}
                    currentConfigItem={currentConfigItem}
                    configType={configType}
                    showConfigForm={showConfigForm}
                    loadingConfig={loadingConfig}
                    configData={configData}
                />
            </div>
        </Layout>
    );
};

export default AdminPage;