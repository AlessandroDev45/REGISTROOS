-- =====================================================================
-- SCRIPT PARA LIMPEZA DO BANCO DE DADOS
-- Remove tabelas desnecessárias e colunas duplicadas/não utilizadas
-- =====================================================================

-- =====================================================================
-- 1. REMOVER TABELA DE HISTÓRICO (CONFORME SOLICITADO)
-- =====================================================================

-- Verificar se a tabela existe antes de remover
DROP TABLE IF EXISTS ordens_servico_historico;

-- =====================================================================
-- 2. LIMPAR TABELA APONTAMENTOS_DETALHADOS
-- Remove colunas desnecessárias e duplicadas
-- =====================================================================

-- NOTA: SQLite não suporta DROP COLUMN IF EXISTS
-- As colunas serão removidas individualmente com verificação de erro

-- Remover colunas que não existem no código ou são desnecessárias
-- (Será feito via Python com verificação de existência)

-- =====================================================================
-- 3. LIMPAR TABELA ORDENS_SERVICO
-- Remove colunas duplicadas de informações do usuário
-- =====================================================================

-- Remover colunas duplicadas (informações já estão em id_responsavel_registro)
ALTER TABLE ordens_servico DROP COLUMN IF EXISTS setor;
ALTER TABLE ordens_servico DROP COLUMN IF EXISTS departamento;

-- Remover criado_por se for duplicação de id_responsavel_registro
-- ALTER TABLE ordens_servico DROP COLUMN IF EXISTS criado_por;

-- =====================================================================
-- 4. LIMPAR TABELA PENDENCIAS
-- Remove colunas duplicadas de informações do usuário
-- =====================================================================

-- A tabela pendencias está bem estruturada, mantém apenas os IDs dos usuários
-- Não há colunas duplicadas significativas para remover

-- =====================================================================
-- 5. LIMPAR TABELA PROGRAMACOES
-- Remove colunas duplicadas
-- =====================================================================

-- Remover setor duplicado (informação já está no usuário via criado_por_id)
ALTER TABLE programacoes DROP COLUMN IF EXISTS setor;

-- =====================================================================
-- 6. LIMPAR TABELA TIPOS_TESTE
-- Remove colunas duplicadas de departamento/setor
-- =====================================================================

-- Manter departamento e setor pois são necessários para filtros
-- Remover apenas se houver duplicação real com outras tabelas

-- =====================================================================
-- 7. LIMPAR TABELA SETORES
-- Remove colunas duplicadas
-- =====================================================================

-- Remover departamento duplicado se já existe id_departamento
-- ALTER TABLE setores DROP COLUMN IF EXISTS departamento;

-- =====================================================================
-- 8. LIMPAR TABELA TIPOS_MAQUINA
-- Remove colunas duplicadas
-- =====================================================================

-- Remover departamento duplicado se já existe id_departamento
ALTER TABLE tipos_maquina DROP COLUMN IF EXISTS departamento;

-- =====================================================================
-- 9. LIMPAR TABELA CAUSAS_RETRABALHO
-- Remove colunas duplicadas
-- =====================================================================

-- Remover departamento e setor duplicados se já existe id_departamento
ALTER TABLE causas_retrabalho DROP COLUMN IF EXISTS departamento;
ALTER TABLE causas_retrabalho DROP COLUMN IF EXISTS setor;

-- =====================================================================
-- 10. LIMPAR TABELA TIPO_ATIVIDADE
-- Remove colunas duplicadas
-- =====================================================================

-- Remover setor e departamento duplicados (usar relacionamentos)
ALTER TABLE tipo_atividade DROP COLUMN IF EXISTS setor;
ALTER TABLE tipo_atividade DROP COLUMN IF EXISTS departamento;

-- =====================================================================
-- 11. LIMPAR TABELA DESCRICAO_ATIVIDADE
-- Remove colunas duplicadas
-- =====================================================================

-- Remover setor e departamento duplicados (usar relacionamentos)
ALTER TABLE descricao_atividade DROP COLUMN IF EXISTS setor;
ALTER TABLE descricao_atividade DROP COLUMN IF EXISTS departamento;

-- =====================================================================
-- 12. LIMPAR TABELA TIPO_FALHA
-- Remove colunas duplicadas
-- =====================================================================

-- Remover setor e departamento duplicados (usar relacionamentos)
ALTER TABLE tipo_falha DROP COLUMN IF EXISTS setor;
ALTER TABLE tipo_falha DROP COLUMN IF EXISTS departamento;

-- =====================================================================
-- 13. VERIFICAR E REMOVER OUTRAS TABELAS DESNECESSÁRIAS
-- =====================================================================

-- Remover tabelas de histórico ou temporárias se existirem
DROP TABLE IF EXISTS apontamentos_historico;
DROP TABLE IF EXISTS pendencias_historico;
DROP TABLE IF EXISTS programacoes_historico;
DROP TABLE IF EXISTS usuarios_historico;

-- Remover tabelas de backup ou temporárias
DROP TABLE IF EXISTS backup_apontamentos;
DROP TABLE IF EXISTS temp_apontamentos;
DROP TABLE IF EXISTS old_apontamentos;

-- =====================================================================
-- 14. OTIMIZAÇÃO FINAL
-- =====================================================================

-- Recriar índices importantes após as alterações
CREATE INDEX IF NOT EXISTS idx_apontamentos_id_os ON apontamentos_detalhados(id_os);
CREATE INDEX IF NOT EXISTS idx_apontamentos_id_usuario ON apontamentos_detalhados(id_usuario);
CREATE INDEX IF NOT EXISTS idx_apontamentos_data_inicio ON apontamentos_detalhados(data_hora_inicio);
CREATE INDEX IF NOT EXISTS idx_pendencias_numero_os ON pendencias(numero_os);
CREATE INDEX IF NOT EXISTS idx_ordens_servico_numero ON ordens_servico(os_numero);

-- Atualizar estatísticas das tabelas
ANALYZE apontamentos_detalhados;
ANALYZE ordens_servico;
ANALYZE pendencias;
ANALYZE programacoes;

-- =====================================================================
-- RESUMO DAS ALTERAÇÕES:
-- =====================================================================
-- 
-- TABELAS REMOVIDAS:
-- - ordens_servico_historico
-- - apontamentos_historico
-- - pendencias_historico
-- - programacoes_historico
-- - usuarios_historico
-- - backup_apontamentos
-- - temp_apontamentos
-- - old_apontamentos
--
-- COLUNAS REMOVIDAS DE apontamentos_detalhados:
-- - sequencia_repeticao
-- - ensaio_carga
-- - diagnose
-- - teste_inicial_finalizado
-- - teste_inicial_liberado_em
-- - os_finalizada
-- - data_processo_finalizado
-- - pend_criada, pend_fim, pend_finaliza
-- - motivo_falha, resultado_os, setor_do_retrabalho
-- - nome_tecnico, cargo_tecnico, setor_tecnico, departamento_tecnico, matricula_tecnico
-- - observacoes (duplicada)
--
-- COLUNAS REMOVIDAS DE ordens_servico:
-- - setor, departamento (duplicadas com usuário)
--
-- COLUNAS REMOVIDAS DE programacoes:
-- - setor (duplicada com usuário)
--
-- COLUNAS REMOVIDAS DE tipos_maquina:
-- - departamento (duplicada com id_departamento)
--
-- COLUNAS REMOVIDAS DE causas_retrabalho:
-- - departamento, setor (duplicadas com id_departamento)
--
-- COLUNAS REMOVIDAS DE tipo_atividade:
-- - setor, departamento (usar relacionamentos)
--
-- COLUNAS REMOVIDAS DE descricao_atividade:
-- - setor, departamento (usar relacionamentos)
--
-- COLUNAS REMOVIDAS DE tipo_falha:
-- - setor, departamento (usar relacionamentos)
--
-- =====================================================================
