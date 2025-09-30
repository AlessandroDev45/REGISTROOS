import { useState, useEffect } from 'react';
import api from '../services/api';

export interface TipoMaquina {
  id: number;
  nome_tipo: string;
  categoria: string;
  descricao: string;
  ativo: boolean;
  departamento: string;
  setor: string;
  data_criacao?: string;
  data_ultima_atualizacao?: string;
}

export interface TipoMaquinaFormData {
  nome_tipo: string;
  categoria: string;
  descricao: string;
  departamento: string;
  setor: string;
  ativo: boolean;
}

export const useAdminTiposMaquina = () => {
  const [tiposMaquina, setTiposMaquina] = useState<TipoMaquina[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Carregar todos os tipos de máquina
  const loadTiposMaquina = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await api.get('/desenvolvimento/formulario/tipos-maquina');
      setTiposMaquina(response.data || []);
    } catch (err: any) {
      setError(err.response?.data?.message || 'Erro ao carregar tipos de máquina');
      console.error('Erro ao carregar tipos de máquina:', err);
    } finally {
      setLoading(false);
    }
  };

  // Criar novo tipo de máquina
  const createTipoMaquina = async (data: TipoMaquinaFormData): Promise<boolean> => {
    setLoading(true);
    setError(null);
    try {
      await api.post('/admin/tipos-maquina', data);
      await loadTiposMaquina(); // Recarregar lista
      return true;
    } catch (err: any) {
      setError(err.response?.data?.message || 'Erro ao criar tipo de máquina');
      console.error('Erro ao criar tipo de máquina:', err);
      return false;
    } finally {
      setLoading(false);
    }
  };

  // Atualizar tipo de máquina
  const updateTipoMaquina = async (id: number, data: TipoMaquinaFormData): Promise<boolean> => {
    setLoading(true);
    setError(null);
    try {
      await api.put(`/admin/tipos-maquina/${id}`, data);
      await loadTiposMaquina(); // Recarregar lista
      return true;
    } catch (err: any) {
      setError(err.response?.data?.message || 'Erro ao atualizar tipo de máquina');
      console.error('Erro ao atualizar tipo de máquina:', err);
      return false;
    } finally {
      setLoading(false);
    }
  };

  // Deletar tipo de máquina
  const deleteTipoMaquina = async (id: number): Promise<boolean> => {
    setLoading(true);
    setError(null);
    try {
      await api.delete(`/admin/tipos-maquina/${id}`);
      await loadTiposMaquina(); // Recarregar lista
      return true;
    } catch (err: any) {
      setError(err.response?.data?.message || 'Erro ao deletar tipo de máquina');
      console.error('Erro ao deletar tipo de máquina:', err);
      return false;
    } finally {
      setLoading(false);
    }
  };

  // Alternar status ativo/inativo
  const toggleTipoMaquinaStatus = async (id: number): Promise<boolean> => {
    const tipoMaquina = tiposMaquina.find(tm => tm.id === id);
    if (!tipoMaquina) return false;

    return await updateTipoMaquina(id, {
      nome_tipo: tipoMaquina.nome_tipo,
      categoria: tipoMaquina.categoria,
      descricao: tipoMaquina.descricao,
      departamento: tipoMaquina.departamento,
      setor: tipoMaquina.setor,
      ativo: !tipoMaquina.ativo
    });
  };

  // Filtrar tipos de máquina
  const filterTiposMaquina = (searchTerm: string, departamento?: string, setor?: string) => {
    return tiposMaquina.filter(tm => {
      const matchesSearch = !searchTerm || 
        tm.nome_tipo.toLowerCase().includes(searchTerm.toLowerCase()) ||
        tm.categoria.toLowerCase().includes(searchTerm.toLowerCase()) ||
        tm.descricao.toLowerCase().includes(searchTerm.toLowerCase());
      
      const matchesDepartamento = !departamento || tm.departamento === departamento;
      const matchesSetor = !setor || tm.setor === setor;
      
      return matchesSearch && matchesDepartamento && matchesSetor;
    });
  };

  useEffect(() => {
    loadTiposMaquina();
  }, []);

  return {
    tiposMaquina,
    loading,
    error,
    loadTiposMaquina,
    createTipoMaquina,
    updateTipoMaquina,
    deleteTipoMaquina,
    toggleTipoMaquinaStatus,
    filterTiposMaquina
  };
};
