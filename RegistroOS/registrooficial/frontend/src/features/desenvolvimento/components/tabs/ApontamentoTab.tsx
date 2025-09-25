import React, { useState, useEffect } from 'react';
import { ConfiguracaoSetor } from '../../../../pages/common/TiposApi';
import { createApontamento } from '../../../../services/api';
import { useAuth } from '../../../../contexts/AuthContext';

interface ApontamentoTabProps {
  sectorConfig: ConfiguracaoSetor;
  sectorKey: string;
}

const ApontamentoTab: React.FC<ApontamentoTabProps> = ({ sectorConfig, sectorKey }) => {
  const { user } = useAuth();
  const [formData, setFormData] = useState<any>({});
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  // Campos básicos do formulário
  const [osNumero, setOsNumero] = useState('');
  const [atividade, setAtividade] = useState('');
  const [descricaoAtividade, setDescricaoAtividade] = useState('');
  const [categoria, setCategoria] = useState('');
  const [subcategoria, setSubcategoria] = useState('');
  const [descricaoSubcategoria, setDescricaoSubcategoria] = useState('');
  const [observacoes, setObservacoes] = useState('');
  const [horaInicio, setHoraInicio] = useState('');
  const [horaFim, setHoraFim] = useState('');

  // Estados para controle de etapas
  const [etapaInicial, setEtapaInicial] = useState(false);
  const [etapaParcial, setEtapaParcial] = useState(false);
  const [etapaFinal, setEtapaFinal] = useState(false);
  const [subcategoriaFinalizada, setSubcategoriaFinalizada] = useState(false);

  // Estados para estrutura hierárquica
  const [tipoMaquinaId, setTipoMaquinaId] = useState<number | null>(null);
  const [parteSelecionada, setParteSelecionada] = useState('');
  const [partes, setPartes] = useState<any[]>([]);
  const [atividades, setAtividades] = useState<any[]>([]);
  const [categorias, setCategorias] = useState<any>({});
  const [loadingPartes, setLoadingPartes] = useState(false);
  const [loadingAtividades, setLoadingAtividades] = useState(false);

  // Função para buscar partes de um tipo de máquina
  const buscarPartes = async (tipoMaquinaId: number) => {
    setLoadingPartes(true);
    try {
      const response = await fetch(`/api/tipos-maquina/${tipoMaquinaId}/partes`);
      if (response.ok) {
        const data = await response.json();
        setPartes(data.partes || []);
      }
    } catch (error) {
      console.error('Erro ao buscar partes:', error);
    } finally {
      setLoadingPartes(false);
    }
  };

  // Função para buscar atividades por categoria/subcategoria
  const buscarAtividades = async (categoria?: string, subcategoria?: string) => {
    setLoadingAtividades(true);
    try {
      const params = new URLSearchParams();
      if (categoria) params.append('categoria', categoria);
      if (subcategoria) params.append('subcategoria', subcategoria);

      const response = await fetch(`/api/atividades-por-categoria?${params}`);
      if (response.ok) {
        const data = await response.json();
        setAtividades(data.atividades || []);
      }
    } catch (error) {
      console.error('Erro ao buscar atividades:', error);
    } finally {
      setLoadingAtividades(false);
    }
  };

  // Função para buscar categorias e subcategorias
  const buscarCategorias = async () => {
    try {
      const response = await fetch('/api/categorias-subcategorias');
      if (response.ok) {
        const data = await response.json();
        setCategorias(data.categorias || {});
      }
    } catch (error) {
      console.error('Erro ao buscar categorias:', error);
    }
  };

  useEffect(() => {
    // Configurar hora atual como padrão
    const now = new Date();
    const timeString = now.toTimeString().slice(0, 5);
    setHoraInicio(timeString);

    // Buscar categorias ao carregar
    buscarCategorias();
  }, []);

  // Effect para buscar atividades quando categoria/subcategoria mudam
  useEffect(() => {
    if (categoria) {
      buscarAtividades(categoria, subcategoria);
    }
  }, [categoria, subcategoria]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setMessage(null);

    try {
      const apontamentoData = {
        os_numero: osNumero,
        usuario_id: user?.id,
        setor: sectorKey,
        // Campos hierárquicos - usando ressignificação conforme especificação
        tipo_maquina: parteSelecionada, // NOME DA PARTE
        tipo_atividade: atividade, // NOME DA ATIVIDADE
        descricao_atividade: descricaoAtividade,
        categoria: categoria,
        subcategoria: subcategoria,
        descricao_subcategoria: descricaoSubcategoria,
        etapa_inicial: etapaInicial,
        etapa_parcial: etapaParcial,
        etapa_final: etapaFinal,
        subcategoria_finalizada: subcategoriaFinalizada,
        observacoes,
        hora_inicio: horaInicio,
        hora_fim: horaFim,
        data_apontamento: new Date().toISOString().split('T')[0],
        ...formData
      };

      await createApontamento(apontamentoData);
      
      setMessage({ type: 'success', text: 'Apontamento criado com sucesso!' });
      
      // Limpar formulário
      setOsNumero('');
      setAtividade('');
      setDescricaoAtividade('');
      setObservacoes('');
      setHoraFim('');
      setFormData({});
      
    } catch (error: any) {
      setMessage({ 
        type: 'error', 
        text: error.message || 'Erro ao criar apontamento' 
      });
    } finally {
      setLoading(false);
    }
  };

  const renderFormField = (field: any, index: number) => {
    const fieldKey = `field_${index}`;
    
    switch (field.tipo) {
      case 'text':
        return (
          <div key={fieldKey} className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              {field.label}
            </label>
            <input
              type="text"
              value={formData[fieldKey] || ''}
              onChange={(e) => setFormData((prev: any) => ({ ...prev, [fieldKey]: e.target.value }))}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder={field.placeholder}
            />
          </div>
        );
      
      case 'select':
        return (
          <div key={fieldKey} className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              {field.label}
            </label>
            <select
              value={formData[fieldKey] || ''}
              onChange={(e) => setFormData((prev: any) => ({ ...prev, [fieldKey]: e.target.value }))}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">Selecione...</option>
              {field.options?.map((option: string, idx: number) => (
                <option key={idx} value={option}>{option}</option>
              ))}
            </select>
          </div>
        );
      
      default:
        return null;
    }
  };

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h2 className="text-xl font-semibold mb-6">Novo Apontamento - {sectorConfig.NomeSetor}</h2>
      
      {message && (
        <div className={`mb-4 p-4 rounded-md ${
          message.type === 'success' ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-700'
        }`}>
          {message.text}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-8">
        {/* SEÇÃO: DADOS BÁSICOS */}
        <div className="bg-gray-50 p-6 rounded-lg">
          <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
            📋 Dados Básicos
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Número da OS *
            </label>
            <input
              type="text"
              value={osNumero}
              onChange={(e) => {
                let valor = e.target.value;
                // VALIDAÇÃO: Apenas números, máximo 5 dígitos
                valor = valor.replace(/[^0-9]/g, '').slice(0, 5);
                setOsNumero(valor);
              }}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Ex: 12345 (5 dígitos)"
              maxLength={5}
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Tipo de Atividade *
            </label>
            <select
              value={atividade}
              onChange={(e) => setAtividade(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              required
              disabled={loadingAtividades}
            >
              <option value="">Selecione...</option>
              {/* Atividades filtradas por categoria/subcategoria */}
              {atividades.map((ativ) => (
                <option key={ativ.id} value={ativ.nome}>
                  {ativ.nome} {ativ.descricao && `- ${ativ.descricao}`}
                </option>
              ))}
              {/* Fallback para atividades do setor se não houver filtradas */}
              {atividades.length === 0 && !loadingAtividades && sectorConfig.ListaAtividades?.map((ativ, idx) => (
                <option key={idx} value={ativ.nome}>{ativ.nome}</option>
              ))}
            </select>
            {loadingAtividades && (
              <p className="text-sm text-gray-500 mt-1">Carregando atividades...</p>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Parte da Máquina *
            </label>
            <select
              value={parteSelecionada}
              onChange={(e) => setParteSelecionada(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              required
              disabled={loadingPartes}
            >
              <option value="">Selecione uma parte...</option>
              {partes.map((parte, idx) => (
                <option key={idx} value={parte.nome}>{parte.nome}</option>
              ))}
              {partes.length === 0 && !loadingPartes && (
                <option value="" disabled>Nenhuma parte disponível</option>
              )}
            </select>
            {loadingPartes && (
              <p className="text-sm text-gray-500 mt-1">Carregando partes...</p>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Categoria *
            </label>
            <select
              value={categoria}
              onChange={(e) => {
                setCategoria(e.target.value);
                setSubcategoria(''); // Reset subcategoria quando categoria muda
              }}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              required
            >
              <option value="">Selecione...</option>
              {Object.keys(categorias).map((cat) => (
                <option key={cat} value={cat}>{cat}</option>
              ))}
              {Object.keys(categorias).length === 0 && (
                <>
                  <option value="ESTATICOS">Estáticos</option>
                  <option value="DINAMICOS">Dinâmicos</option>
                </>
              )}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Subcategoria *
            </label>
            <select
              value={subcategoria}
              onChange={(e) => setSubcategoria(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              required
              disabled={!categoria}
            >
              <option value="">Selecione...</option>
              {categoria && categorias[categoria] && categorias[categoria].map((subcat: string) => (
                <option key={subcat} value={subcat}>{subcat}</option>
              ))}
              {(!categoria || !categorias[categoria] || categorias[categoria].length === 0) && (
                <>
                  <option value="VISUAL">Visual</option>
                  <option value="ELETRICO">Elétrico</option>
                  <option value="MECANICO">Mecânico</option>
                </>
              )}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Hora Início *
            </label>
            <input
              type="time"
              value={horaInicio}
              onChange={(e) => setHoraInicio(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Hora Fim
            </label>
            <input
              type="time"
              value={horaFim}
              onChange={(e) => setHoraFim(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          </div>
        </div>

        {/* SEÇÃO: TESTES E ESTRUTURA HIERÁRQUICA */}
        <div className="bg-blue-50 p-6 rounded-lg">
          <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
            🔬 Testes e Estrutura Hierárquica
          </h3>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Parte da Máquina *
              </label>
              <select
                value={parteSelecionada}
                onChange={(e) => setParteSelecionada(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                required
                disabled={loadingPartes}
              >
                <option value="">Selecione uma parte...</option>
                {partes.map((parte, idx) => (
                  <option key={idx} value={parte.nome}>{parte.nome}</option>
                ))}
                {partes.length === 0 && !loadingPartes && (
                  <option value="" disabled>Nenhuma parte disponível</option>
                )}
              </select>
              {loadingPartes && (
                <p className="text-sm text-gray-500 mt-1">Carregando partes...</p>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Categoria *
              </label>
              <select
                value={categoria}
                onChange={(e) => {
                  setCategoria(e.target.value);
                  setSubcategoria(''); // Reset subcategoria quando categoria muda
                }}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                required
              >
                <option value="">Selecione...</option>
                {Object.keys(categorias).map((cat) => (
                  <option key={cat} value={cat}>{cat}</option>
                ))}
                {Object.keys(categorias).length === 0 && (
                  <>
                    <option value="ESTATICOS">Estáticos</option>
                    <option value="DINAMICOS">Dinâmicos</option>
                  </>
                )}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Subcategoria *
              </label>
              <select
                value={subcategoria}
                onChange={(e) => setSubcategoria(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                required
                disabled={!categoria}
              >
                <option value="">Selecione...</option>
                {categoria && categorias[categoria] && categorias[categoria].map((subcat: string) => (
                  <option key={subcat} value={subcat}>{subcat}</option>
                ))}
                {(!categoria || !categorias[categoria] || categorias[categoria].length === 0) && (
                  <>
                    <option value="VISUAL">Visual</option>
                    <option value="ELETRICO">Elétrico</option>
                    <option value="MECANICO">Mecânico</option>
                  </>
                )}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Tipo de Atividade *
              </label>
              <select
                value={atividade}
                onChange={(e) => setAtividade(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                required
                disabled={loadingAtividades}
              >
                <option value="">Selecione...</option>
                {/* Atividades filtradas por categoria/subcategoria */}
                {atividades.map((ativ) => (
                  <option key={ativ.id} value={ativ.nome}>
                    {ativ.nome} {ativ.descricao && `- ${ativ.descricao}`}
                  </option>
                ))}
                {/* Fallback para atividades do setor se não houver filtradas */}
                {atividades.length === 0 && !loadingAtividades && sectorConfig.ListaAtividades?.map((ativ, idx) => (
                  <option key={idx} value={ativ.nome}>{ativ.nome}</option>
                ))}
              </select>
              {loadingAtividades && (
                <p className="text-sm text-gray-500 mt-1">Carregando atividades...</p>
              )}
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Descrição da Atividade
              </label>
              <textarea
                value={descricaoAtividade}
                onChange={(e) => setDescricaoAtividade(e.target.value)}
                rows={3}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Descreva a atividade realizada..."
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Descrição da Subcategoria
              </label>
              <textarea
                value={descricaoSubcategoria}
                onChange={(e) => setDescricaoSubcategoria(e.target.value)}
                rows={3}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Descreva detalhes específicos da subcategoria..."
              />
            </div>
          </div>

          {/* Controles de Etapas */}
          <div className="bg-white p-4 rounded-lg border">
            <h4 className="text-md font-medium text-gray-900 mb-4">⚙️ Controle de Etapas</h4>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <div className="flex items-center">
                <input
                  type="checkbox"
                  id="etapa-inicial"
                  checked={etapaInicial}
                  onChange={(e) => setEtapaInicial(e.target.checked)}
                  className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                />
                <label htmlFor="etapa-inicial" className="ml-2 text-sm text-gray-700">
                  Etapa Inicial
                </label>
              </div>

              <div className="flex items-center">
                <input
                  type="checkbox"
                  id="etapa-parcial"
                  checked={etapaParcial}
                  onChange={(e) => setEtapaParcial(e.target.checked)}
                  className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                />
                <label htmlFor="etapa-parcial" className="ml-2 text-sm text-gray-700">
                  Etapa Parcial
                </label>
              </div>

              <div className="flex items-center">
                <input
                  type="checkbox"
                  id="etapa-final"
                  checked={etapaFinal}
                  onChange={(e) => setEtapaFinal(e.target.checked)}
                  className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                />
                <label htmlFor="etapa-final" className="ml-2 text-sm text-gray-700">
                  Etapa Final
                </label>
              </div>

              <div className="flex items-center">
                <button
                  type="button"
                  onClick={() => setSubcategoriaFinalizada(!subcategoriaFinalizada)}
                  className={`px-3 py-1 rounded text-sm font-medium ${
                    subcategoriaFinalizada
                      ? 'bg-green-100 text-green-800 border border-green-300'
                      : 'bg-gray-100 text-gray-700 border border-gray-300'
                  }`}
                >
                  {subcategoriaFinalizada ? '✅ Subcategoria Finalizada' : '⏳ Finalizar Subcategoria'}
                </button>
              </div>
            </div>
          </div>
        </div>



        {/* Campos específicos do setor */}
        {sectorConfig.ComponentesFormularioPrincipal?.map((component, index) => 
          renderFormField(component, index)
        )}

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Observações
          </label>
          <textarea
            value={observacoes}
            onChange={(e) => setObservacoes(e.target.value)}
            rows={3}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Observações adicionais..."
          />
        </div>

        <div className="flex justify-end space-x-4">
          <button
            type="button"
            onClick={() => {
              setOsNumero('');
              setAtividade('');
              setDescricaoAtividade('');
              setCategoria('');
              setSubcategoria('');
              setDescricaoSubcategoria('');
              setParteSelecionada('');
              setObservacoes('');
              setHoraFim('');
              setEtapaInicial(false);
              setEtapaParcial(false);
              setEtapaFinal(false);
              setSubcategoriaFinalizada(false);
              setFormData({});
            }}
            className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
          >
            Limpar
          </button>
          <button
            type="submit"
            disabled={loading}
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
          >
            {loading ? 'Salvando...' : 'Salvar Apontamento'}
          </button>
        </div>
      </form>
    </div>
  );
};

export default ApontamentoTab;
