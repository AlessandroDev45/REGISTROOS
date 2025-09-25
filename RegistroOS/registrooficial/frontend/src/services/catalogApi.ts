import api from './api';

// Dynamic catalog endpoints for sector-specific configurations
export const fetchTestesPorSetor = async (setor: string) => {
  try {
    const response = await api.get(`/catalogos/testes/${setor}`);
    return response.data.testes || [];
  } catch (error) {
    console.error("Erro ao buscar testes por setor:", error);
    return [];
  }
};

export const fetchAtividadesPorSetor = async (setor: string) => {
  try {
    const response = await api.get(`/catalogos/atividades/${setor}`);
    return response.data.atividades || [];
  } catch (error) {
    console.error("Erro ao buscar atividades por setor:", error);
    return [];
  }
};