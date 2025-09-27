import React, { useState, useEffect } from 'react';
import { createProgramacao, updateProgramacao, getProgramacaoFormData } from '../../../services/api';

interface OrdemServico {
  id: number;
  os_numero: string;
  descricao_maquina: string;
  status: string;
  cliente_nome: string;
  tipo_maquina_nome: string;
  setor: string;
}

interface Usuario {
  id: number;
  nome_completo: string;
  setor: string;
  departamento?: string;
  privilege_level?: string;
  trabalha_producao?: boolean;
}

interface Setor {
  id: number;
  nome: string;
  id_departamento?: number;
  departamento_nome?: string;
}

interface Departamento {
  id: number;
  nome: string;
}

interface FormData {
  ordens_servico: OrdemServico[];
  usuarios: Usuario[];
  setores: Setor[];
  departamentos: Departamento[];
  status_opcoes: string[];
}

interface ProgramacaoFormData {
  id_ordem_servico: number;
  os_numero?: string;
  inicio_previsto: string;
  fim_previsto: string;
  id_departamento?: number;
  id_setor?: number;
  responsavel_id?: number;
  prioridade?: string;
  observacoes?: string;
  status?: string;
}

interface ProgramacaoFormProps {
  programacaoInicial?: any;
  onSalvar: (programacao: any) => void;
  onCancelar: () => void;
  isEditing?: boolean;
}

const ProgramacaoForm: React.FC<ProgramacaoFormProps> = ({
  programacaoInicial,
  onSalvar,
  onCancelar,
  isEditing = false
}) => {
  const [formData, setFormData] = useState<FormData>({
    ordens_servico: [],
    usuarios: [],
    setores: [],
    departamentos: [],
    status_opcoes: []
  });
  const [programacao, setProgramacao] = useState<ProgramacaoFormData>({
    id_ordem_servico: 0,
    os_numero: '',
    inicio_previsto: '',
    fim_previsto: '',
    id_departamento: undefined,
    id_setor: undefined,
    responsavel_id: undefined,
    prioridade: 'NORMAL',
    observacoes: '',
    status: 'PROGRAMADA'
  });
  const [loading, setLoading] = useState(false);
  const [loadingForm, setLoadingForm] = useState(true);
  const [errors, setErrors] = useState<Record<string, string>>({});

  useEffect(() => {
    carregarDadosFormulario();
  }, []);

  useEffect(() => {
    if (programacaoInicial && isEditing) {
      setProgramacao({
        id_ordem_servico: programacaoInicial.id_ordem_servico,
        os_numero: programacaoInicial.os_numero || '',
        inicio_previsto: programacaoInicial.inicio_previsto?.slice(0, 16) || '',
        fim_previsto: programacaoInicial.fim_previsto?.slice(0, 16) || '',
        id_departamento: programacaoInicial.id_departamento,
        id_setor: programacaoInicial.id_setor,
        responsavel_id: programacaoInicial.responsavel_id,
        prioridade: programacaoInicial.prioridade || 'NORMAL',
        observacoes: programacaoInicial.observacoes || '',
        status: programacaoInicial.status || 'PROGRAMADA'
      });
    }
  }, [programacaoInicial, isEditing]);

  const carregarDadosFormulario = async () => {
    try {
      console.log('Carregando dados do formulário de programação...');
      const dados = await getProgramacaoFormData();
      console.log('Dados do formulário recebidos:', dados);

      // Verificar se os dados estão no formato esperado
      if (dados && typeof dados === 'object') {
        setFormData({
          ordens_servico: Array.isArray(dados.ordens_servico) ? dados.ordens_servico : [],
          usuarios: Array.isArray(dados.usuarios) ? dados.usuarios : [],
          setores: Array.isArray(dados.setores) ? dados.setores : [],
          departamentos: Array.isArray(dados.departamentos) ? dados.departamentos : [],
          status_opcoes: Array.isArray(dados.status_opcoes) ? dados.status_opcoes : ['PROGRAMADA', 'EM_ANDAMENTO', 'ENVIADA', 'CONCLUIDA', 'CANCELADA']
        });
        console.log(`Formulário carregado: ${dados.ordens_servico?.length || 0} OS, ${dados.usuarios?.length || 0} usuários, ${dados.setores?.length || 0} setores, ${dados.departamentos?.length || 0} departamentos`);
      } else {
        console.warn('Dados do formulário em formato inesperado, usando dados padrão');
        setFormData({
          ordens_servico: [],
          usuarios: [],
          setores: [],
          departamentos: [],
          status_opcoes: ['PROGRAMADA', 'EM_ANDAMENTO', 'ENVIADA', 'CONCLUIDA', 'CANCELADA']
        });
      }
    } catch (error) {
      console.error('Erro ao carregar dados do formulário:', error);
      // Em caso de erro, usar dados padrão para não quebrar o formulário
      setFormData({
        ordens_servico: [],
        usuarios: [],
        setores: [],
        departamentos: [],
        status_opcoes: ['PROGRAMADA', 'EM_ANDAMENTO', 'ENVIADA', 'CONCLUIDA', 'CANCELADA']
      });
    } finally {
      setLoadingForm(false);
    }
  };

  const validarFormulario = (): boolean => {
    const novosErrors: Record<string, string> = {};

    // Validar OS número (campo obrigatório)
    if (!programacao.os_numero || programacao.os_numero.trim() === '') {
      novosErrors.os_numero = 'Número da OS é obrigatório';
    }

    if (!programacao.id_departamento) {
      novosErrors.id_departamento = 'Selecione um departamento';
    }

    if (!programacao.id_setor) {
      novosErrors.id_setor = 'Selecione um setor';
    }

    if (!programacao.inicio_previsto) {
      novosErrors.inicio_previsto = 'Data/hora de início é obrigatória';
    }

    if (!programacao.fim_previsto) {
      novosErrors.fim_previsto = 'Data/hora de fim é obrigatória';
    }

    if (programacao.inicio_previsto && programacao.fim_previsto) {
      const inicio = new Date(programacao.inicio_previsto);
      const fim = new Date(programacao.fim_previsto);

      if (fim <= inicio) {
        novosErrors.fim_previsto = 'Data/hora de fim deve ser posterior ao início';
      }
    }

    setErrors(novosErrors);
    return Object.keys(novosErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validarFormulario()) {
      return;
    }

    setLoading(true);
    try {
      // Preparar dados para envio
      // Formatar OS número com zeros à esquerda se necessário
      let osNumeroFormatado = programacao.os_numero?.trim() || '';
      if (osNumeroFormatado && !osNumeroFormatado.startsWith('000')) {
        // Se não começar com 000, adicionar zeros à esquerda para ter 9 dígitos
        osNumeroFormatado = osNumeroFormatado.padStart(9, '0');
        if (!osNumeroFormatado.startsWith('000')) {
          osNumeroFormatado = '000' + osNumeroFormatado.slice(-6);
        }
      }

      const dadosParaEnvio = {
        os_numero: osNumeroFormatado,
        inicio_previsto: programacao.inicio_previsto,
        fim_previsto: programacao.fim_previsto,
        id_departamento: programacao.id_departamento,
        id_setor: programacao.id_setor,
        responsavel_id: programacao.responsavel_id,
        observacoes: programacao.observacoes || '',
        status: programacao.status || 'PROGRAMADA'
      };

      console.log('🚀 DADOS SENDO ENVIADOS PARA O BACKEND:', dadosParaEnvio);
      console.log('🔍 URL da requisição:', '/pcp/programacoes');
      console.log('📊 Método:', 'POST');

      let resultado;

      if (isEditing && programacaoInicial) {
        resultado = await updateProgramacao(programacaoInicial.id, dadosParaEnvio);
      } else {
        resultado = await createProgramacao(dadosParaEnvio);
      }

      onSalvar(resultado);
    } catch (error: any) {
      console.error('🚨 ERRO AO SALVAR PROGRAMAÇÃO:', error);
      console.error('🔍 Status do erro:', error.response?.status);
      console.error('📄 Dados do erro:', error.response?.data);
      console.error('🌐 URL do erro:', error.config?.url);
      console.error('📊 Dados enviados:', error.config?.data);

      const errorMessage = error.response?.data?.detail || error.message || 'Erro ao salvar programação';
      alert(`Erro: ${errorMessage}`);
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (campo: keyof ProgramacaoFormData, valor: any) => {
    setProgramacao(prev => ({
      ...prev,
      [campo]: valor
    }));
    
    // Limpar erro do campo quando o usuário começar a digitar
    if (errors[campo]) {
      setErrors(prev => ({
        ...prev,
        [campo]: ''
      }));
    }
  };

  const calcularDuracao = () => {
    if (programacao.inicio_previsto && programacao.fim_previsto) {
      const inicio = new Date(programacao.inicio_previsto);
      const fim = new Date(programacao.fim_previsto);
      const diffMs = fim.getTime() - inicio.getTime();
      const diffHours = diffMs / (1000 * 60 * 60);
      
      if (diffHours > 0) {
        return `${Math.round(diffHours * 10) / 10} horas`;
      }
    }
    return '';
  };

  if (loadingForm) {
    return (
      <div className="flex justify-center items-center p-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        <span className="ml-2">Carregando formulário...</span>
      </div>
    );
  }

  return (
    <div className="bg-white p-6 rounded-lg shadow border">
      <div className="flex justify-between items-center mb-6">
        <h3 className="text-lg font-semibold text-gray-900">
          {isEditing ? 'Editar Programação' : 'Nova Programação'}
        </h3>
        <button
          onClick={onCancelar}
          className="text-gray-400 hover:text-gray-600"
        >
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        {/* OS, Departamento, Setor */}
        <div className="flex space-x-4 mb-4">
          <div className="flex-1">
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Número da Ordem de Serviço *
            </label>
            <input
              type="text"
              value={programacao.os_numero}
              onChange={(e) => {
                let valor = e.target.value.replace(/\D/g, ''); // Apenas números
                handleInputChange('os_numero', valor);
              }}
              className={`w-full border rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                errors.os_numero ? 'border-red-300' : 'border-gray-300'
              }`}
              placeholder="Ex: 12345 (será formatado como 000012345)"
              maxLength={9}
            />
            {errors.os_numero && (
              <p className="text-red-500 text-xs mt-1">{errors.os_numero}</p>
            )}
          </div>

          <div className="flex-1">
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Departamento *
            </label>
            <select
              value={programacao.id_departamento || ''}
              onChange={(e) => {
                const departamentoId = e.target.value ? Number(e.target.value) : undefined;
                handleInputChange('id_departamento', departamentoId);
                // Reset setor quando departamento muda
                handleInputChange('id_setor', undefined);
              }}
              className={`w-full border rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                errors.id_departamento ? 'border-red-300' : 'border-gray-300'
              }`}
            >
              <option value="">Selecione um departamento</option>
              {formData.departamentos.map((departamento) => (
                <option key={departamento.id} value={departamento.id}>
                  {departamento.nome}
                </option>
              ))}
            </select>
            {errors.id_departamento && (
              <p className="text-red-500 text-xs mt-1">{errors.id_departamento}</p>
            )}
          </div>

          <div className="flex-1">
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Setor *
            </label>
            <select
              value={programacao.id_setor || ''}
              onChange={(e) => {
                const setorId = e.target.value ? Number(e.target.value) : undefined;
                handleInputChange('id_setor', setorId);

                // Selecionar automaticamente o supervisor do setor
                if (setorId) {
                  const supervisorDoSetor = formData.usuarios.find(usuario =>
                    usuario.id_setor === setorId &&
                    usuario.privilege_level === 'SUPERVISOR' &&
                    usuario.trabalha_producao === true
                  );

                  if (supervisorDoSetor) {
                    handleInputChange('responsavel_id', supervisorDoSetor.id);
                    console.log(`Supervisor selecionado automaticamente: ${supervisorDoSetor.nome_completo}`);
                  } else {
                    handleInputChange('responsavel_id', undefined);
                    console.log('Nenhum supervisor encontrado para este setor');
                  }
                } else {
                  handleInputChange('responsavel_id', undefined);
                }
              }}
              className={`w-full border rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                errors.id_setor ? 'border-red-300' : 'border-gray-300'
              }`}
              disabled={!programacao.id_departamento}
            >
              <option value="">Selecione um setor</option>
              {formData.setores
                .filter(setor => !programacao.id_departamento || setor.id_departamento === programacao.id_departamento)
                .map((setor) => (
                  <option key={setor.id} value={setor.id}>
                    {setor.nome}
                  </option>
                ))}
            </select>
            {errors.id_setor && (
              <p className="text-red-500 text-xs mt-1">{errors.id_setor}</p>
            )}
            {!programacao.id_departamento && (
              <p className="text-gray-500 text-xs mt-1">
                Selecione um departamento primeiro
              </p>
            )}
          </div>
        </div>

        {/* Prioridade, Data Início, Data Fim */}
        <div className="flex space-x-4 mb-4">
          <div className="flex-1">
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Prioridade *
            </label>
            <select
              value={programacao.prioridade}
              onChange={(e) => handleInputChange('prioridade', e.target.value)}
              className={`w-full border rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                errors.prioridade ? 'border-red-300' : 'border-gray-300'
              }`}
            >
              <option value="BAIXA">Baixa</option>
              <option value="NORMAL">Normal</option>
              <option value="ALTA">Alta</option>
              <option value="URGENTE">Urgente</option>
            </select>
            {errors.prioridade && (
              <p className="text-red-500 text-xs mt-1">{errors.prioridade}</p>
            )}
          </div>

          <div className="flex-1">
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Data/Hora de Início *
            </label>
            <input
              type="datetime-local"
              value={programacao.inicio_previsto}
              onChange={(e) => handleInputChange('inicio_previsto', e.target.value)}
              className={`w-full border rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                errors.inicio_previsto ? 'border-red-300' : 'border-gray-300'
              }`}
            />
            {errors.inicio_previsto && (
              <p className="text-red-500 text-xs mt-1">{errors.inicio_previsto}</p>
            )}
          </div>

          <div className="flex-1">
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Data/Hora de Fim *
            </label>
            <input
              type="datetime-local"
              value={programacao.fim_previsto}
              onChange={(e) => handleInputChange('fim_previsto', e.target.value)}
              className={`w-full border rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                errors.fim_previsto ? 'border-red-300' : 'border-gray-300'
              }`}
            />
            {errors.fim_previsto && (
              <p className="text-red-500 text-xs mt-1">{errors.fim_previsto}</p>
            )}
            {calcularDuracao() && (
              <p className="text-blue-600 text-xs mt-1">Duração: {calcularDuracao()}</p>
            )}
          </div>
        </div>

        {/* Status (apenas para edição) */}
        {isEditing && (
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Status
            </label>
            <select
              value={programacao.status}
              onChange={(e) => handleInputChange('status', e.target.value)}
              className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              {formData.status_opcoes.map((status) => (
                <option key={status} value={status}>
                  {status.replace('_', ' ')}
                </option>
              ))}
            </select>
          </div>
        )}

        {/* Responsável e Observações */}
        <div className="flex space-x-4 mb-4">
          <div className="flex-1">
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Responsável (Supervisor)
            </label>
            <select
              value={programacao.responsavel_id || ''}
              onChange={(e) => handleInputChange('responsavel_id', e.target.value ? Number(e.target.value) : undefined)}
              className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">Selecione um supervisor</option>
              {formData.usuarios
                .filter(usuario =>
                  usuario.privilege_level === 'SUPERVISOR' &&
                  usuario.trabalha_producao === true &&
                  (!programacao.id_setor || usuario.id_setor === programacao.id_setor)
                )
                .map((usuario) => (
                  <option key={usuario.id} value={usuario.id}>
                    {usuario.nome_completo} - {usuario.setor}
                  </option>
                ))}
            </select>
            <p className="text-xs text-gray-500 mt-1">
              Apenas supervisores que trabalham na produção podem ser responsáveis
            </p>
          </div>

          <div className="flex-1">
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Observações
            </label>
            <textarea
              value={programacao.observacoes}
              onChange={(e) => handleInputChange('observacoes', e.target.value)}
              rows={3}
              className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Observações sobre a programação..."
            />
          </div>
        </div>

        {/* Botões */}
        <div className="flex justify-end space-x-3 pt-4">
          <button
            type="button"
            onClick={onCancelar}
            className="px-4 py-2 text-sm text-gray-700 border border-gray-300 rounded hover:bg-gray-50"
          >
            Cancelar
          </button>
          <button
            type="submit"
            disabled={loading}
            className="px-4 py-2 text-sm bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
          >
            {loading ? 'Salvando...' : (isEditing ? 'Atualizar' : 'Criar Programação')}
          </button>
        </div>
      </form>
    </div>
  );
};

export default ProgramacaoForm;
