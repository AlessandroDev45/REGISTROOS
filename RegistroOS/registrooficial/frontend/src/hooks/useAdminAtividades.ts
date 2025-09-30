import { useState, useEffect } from 'react';
import api from '../services/api';

export interface TipoAtividade {
  id: number;
  nome_tipo: string;
  descricao: string;
  departamento: string;
  setor: string;
  id_tipo_maquina?: number;
  tipo_maquina_nome?: string;
  ativo: boolean;
  data_criacao?: string;
  data_ultima_atualizacao?: string;
}

export interface TipoAtividadeFormData {
  nome_tipo: string;
  descricao: string;
  departamento: string;
  setor: string;
  id_tipo_maquina?: number;
  ativo: boolean;
}

export const useAdminAtividades = () => {
  const [tiposAtividade, setTiposAtividade] = useState<TipoAtividade[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Carregar todos os tipos de atividade
  const loadTiposAtividade = async (tipoMaquinaId?: number) => {
    setLoading(true);
    setError(null);
    try {
      let url = '/desenvolvimento/formulario/tipos-atividade';
      if (tipoMaquinaId) {
        url += `?tipo_maquina_id=${tipoMaquinaId}`;
      }
      const response = await api.get(url);
      setTiposAtividade(response.data || []);
    } catch (err: any) {
      setError(err.response?.data?.message || 'Erro ao carregar tipos de atividade');
      console.error('Erro ao carregar tipos de atividade:', err);
    } finally {
      setLoading(false);
    }
  };

  // Criar novo tipo de atividade
  const createTipoAtividade = async (data: TipoAtividadeFormData): Promise<boolean> => {
    setLoading(true);
    setError(null);
    try {
      await api.post('/admin/tipos-atividade', data);
      await loadTiposAtividade(); // Recarregar lista
      return true;
    } catch (err: any) {
      setError(err.response?.data?.message || 'Erro ao criar tipo de atividade');
      console.error('Erro ao criar tipo de atividade:', err);
      return false;
    } finally {
      setLoading(false);
    }
  };

  // Atualizar tipo de atividade
  const updateTipoAtividade = async (id: number, data: TipoAtividadeFormData): Promise<boolean> => {
    setLoading(true);
    setError(null);
    try {
      await api.put(`/admin/tipos-atividade/${id}`, data);
      await loadTiposAtividade(); // Recarregar lista
      return true;
    } catch (err: any) {
      setError(err.response?.data?.message || 'Erro ao atualizar tipo de atividade');
      console.error('Erro ao atualizar tipo de atividade:', err);
      return false;
    } finally {
      setLoading(false);
    }
  };

  // Deletar tipo de atividade
  const deleteTipoAtividade = async (id: number): Promise<boolean> => {
    setLoading(true);
    setError(null);
    try {
      await api.delete(`/admin/tipos-atividade/${id}`);
      await loadTiposAtividade(); // Recarregar lista
      return true;
    } catch (err: any) {
      setError(err.response?.data?.message || 'Erro ao deletar tipo de atividade');
      console.error('Erro ao deletar tipo de atividade:', err);
      return false;
    } finally {
      setLoading(false);
    }
  };

  // Alternar status ativo/inativo
  const toggleTipoAtividadeStatus = async (id: number): Promise<boolean> => {
    const tipoAtividade = tiposAtividade.find(ta => ta.id === id);
    if (!tipoAtividade) return false;

    return await updateTipoAtividade(id, {
      nome_tipo: tipoAtividade.nome_tipo,
      descricao: tipoAtividade.descricao,
      departamento: tipoAtividade.departamento,
      setor: tipoAtividade.setor,
      id_tipo_maquina: tipoAtividade.id_tipo_maquina,
      ativo: !tipoAtividade.ativo
    });
  };

  // Filtrar tipos de atividade
  const filterTiposAtividade = (searchTerm: string, departamento?: string, setor?: string) => {
    return tiposAtividade.filter(ta => {
      const matchesSearch = !searchTerm || 
        ta.nome_tipo.toLowerCase().includes(searchTerm.toLowerCase()) ||
        ta.descricao.toLowerCase().includes(searchTerm.toLowerCase()) ||
        (ta.tipo_maquina_nome && ta.tipo_maquina_nome.toLowerCase().includes(searchTerm.toLowerCase()));
      
      const matchesDepartamento = !departamento || ta.departamento === departamento;
      const matchesSetor = !setor || ta.setor === setor;
      
      return matchesSearch && matchesDepartamento && matchesSetor;
    });
  };

  useEffect(() => {
    loadTiposAtividade();
  }, []);

  return {
    tiposAtividade,
    loading,
    error,
    loadTiposAtividade,
    createTipoAtividade,
    updateTipoAtividade,
    deleteTipoAtividade,
    toggleTipoAtividadeStatus,
    filterTiposAtividade
  };
};
