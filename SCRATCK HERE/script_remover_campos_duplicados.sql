-- =====================================================================
-- SCRIPT PARA REMOÇÃO DE CAMPOS DUPLICADOS E SIMILARES
-- =====================================================================
-- 
-- OBJETIVO: Eliminar campos redundantes e ambíguos
-- RISCO: MÉDIO - Remove campos que podem estar sendo usados
-- RECOMENDAÇÃO: Executar em ambiente de teste primeiro
--
-- =====================================================================

-- =====================================================================
-- 1. BACKUP E VERIFICAÇÕES INICIAIS
-- =====================================================================

SELECT 'INICIANDO LIMPEZA DE CAMPOS DUPLICADOS' as status;

-- Verificar dados antes da limpeza
SELECT COUNT(*) as total_ordens_servico FROM ordens_servico;
SELECT COUNT(*) as total_apontamentos FROM apontamentos_detalhados;
SELECT COUNT(*) as total_usuarios FROM tipo_usuarios;

-- =====================================================================
-- 2. VERIFICAR CAMPOS QUE SERÃO REMOVIDOS
-- =====================================================================

-- Verificar se campos duplicados têm dados diferentes
SELECT 'VERIFICANDO INCONSISTÊNCIAS ANTES DA REMOÇÃO' as status;

-- Verificar se status_os e status_geral são diferentes
SELECT 
    COUNT(*) as total_registros,
    COUNT(CASE WHEN status_os != status_geral THEN 1 END) as diferentes,
    COUNT(CASE WHEN status_os IS NULL OR status_geral IS NULL THEN 1 END) as nulos
FROM ordens_servico 
WHERE status_os IS NOT NULL AND status_geral IS NOT NULL;

-- Verificar se setor (texto) e id_setor apontam para o mesmo setor
SELECT 
    a.id,
    a.setor as setor_texto,
    s.nome as setor_fk,
    CASE WHEN a.setor = s.nome THEN 'IGUAL' ELSE 'DIFERENTE' END as comparacao
FROM apontamentos_detalhados a
LEFT JOIN tipo_setores s ON a.id_setor = s.id
WHERE a.setor IS NOT NULL AND a.id_setor IS NOT NULL
LIMIT 10;

-- =====================================================================
-- 3. FASE 1 - REMOÇÕES SEGURAS (CAMPOS CLARAMENTE DUPLICADOS)
-- =====================================================================

SELECT 'FASE 1: REMOVENDO CAMPOS CLARAMENTE DUPLICADOS' as status;

-- 3.1 Remover status_geral de ordens_servico (manter status_os)
-- NOTA: Comentado para segurança - descomentar após verificação
-- ALTER TABLE ordens_servico DROP COLUMN status_geral;

-- 3.2 Remover setor de apontamentos_detalhados (manter id_setor)
-- NOTA: Comentado para segurança - descomentar após verificação
-- ALTER TABLE apontamentos_detalhados DROP COLUMN setor;

-- =====================================================================
-- 4. VERIFICAR DEPENDÊNCIAS NO CÓDIGO
-- =====================================================================

SELECT 'VERIFICANDO DEPENDÊNCIAS DOS CAMPOS A SEREM REMOVIDOS' as status;

-- Listar campos que serão removidos para verificação manual
SELECT 'CAMPOS QUE SERÃO REMOVIDOS:' as info;
SELECT 'ordens_servico.status_geral' as campo_removido;
SELECT 'apontamentos_detalhados.setor' as campo_removido;
SELECT 'tipo_usuarios.setor' as campo_removido;
SELECT 'tipo_usuarios.departamento' as campo_removido;
SELECT 'tipo_setores.departamento' as campo_removido;
SELECT 'tipos_maquina.setor' as campo_removido;
SELECT 'tipos_maquina.departamento' as campo_removido;

-- =====================================================================
-- 5. SCRIPT DE REMOÇÃO COMPLETA (EXECUTAR APENAS APÓS TESTES)
-- =====================================================================

/*
-- ATENÇÃO: DESCOMENTE APENAS APÓS VERIFICAR QUE NÃO HÁ DEPENDÊNCIAS

-- 5.1 Tabela ordens_servico
ALTER TABLE ordens_servico DROP COLUMN status_geral;

-- 5.2 Tabela apontamentos_detalhados  
ALTER TABLE apontamentos_detalhados DROP COLUMN setor;

-- 5.3 Tabela tipo_usuarios
ALTER TABLE tipo_usuarios DROP COLUMN setor;
ALTER TABLE tipo_usuarios DROP COLUMN departamento;

-- 5.4 Tabela tipo_setores
ALTER TABLE tipo_setores DROP COLUMN departamento;

-- 5.5 Tabela tipos_maquina
ALTER TABLE tipos_maquina DROP COLUMN setor;
ALTER TABLE tipos_maquina DROP COLUMN departamento;

-- 5.6 Tabela tipo_causas_retrabalho
ALTER TABLE tipo_causas_retrabalho DROP COLUMN departamento;
ALTER TABLE tipo_causas_retrabalho DROP COLUMN setor;
*/

-- =====================================================================
-- 6. VERIFICAÇÕES PÓS-REMOÇÃO
-- =====================================================================

SELECT 'VERIFICAÇÕES PÓS-REMOÇÃO (executar após remoções)' as status;

-- Verificar estrutura das tabelas após remoção
-- PRAGMA table_info(ordens_servico);
-- PRAGMA table_info(apontamentos_detalhados);
-- PRAGMA table_info(tipo_usuarios);

-- Verificar se dados foram preservados
-- SELECT COUNT(*) as total_ordens_servico_final FROM ordens_servico;
-- SELECT COUNT(*) as total_apontamentos_final FROM apontamentos_detalhados;
-- SELECT COUNT(*) as total_usuarios_final FROM tipo_usuarios;

-- =====================================================================
-- 7. SCRIPT DE ROLLBACK (EM CASO DE PROBLEMAS)
-- =====================================================================

/*
-- ROLLBACK: Recriar campos removidos (se necessário)

-- Recriar status_geral em ordens_servico
ALTER TABLE ordens_servico ADD COLUMN status_geral VARCHAR(50);
UPDATE ordens_servico SET status_geral = status_os;

-- Recriar setor em apontamentos_detalhados
ALTER TABLE apontamentos_detalhados ADD COLUMN setor VARCHAR(100);
UPDATE apontamentos_detalhados 
SET setor = (SELECT nome FROM tipo_setores WHERE id = apontamentos_detalhados.id_setor);

-- Recriar setor e departamento em tipo_usuarios
ALTER TABLE tipo_usuarios ADD COLUMN setor VARCHAR(100);
ALTER TABLE tipo_usuarios ADD COLUMN departamento VARCHAR(100);
UPDATE tipo_usuarios 
SET setor = (SELECT nome FROM tipo_setores WHERE id = tipo_usuarios.id_setor);
UPDATE tipo_usuarios 
SET departamento = (SELECT nome_tipo FROM tipo_departamentos WHERE id = tipo_usuarios.id_departamento);
*/

-- =====================================================================
-- 8. RELATÓRIO FINAL
-- =====================================================================

SELECT 'RELATÓRIO DE CAMPOS DUPLICADOS IDENTIFICADOS' as status;

SELECT 'TOTAL DE CAMPOS DUPLICADOS ENCONTRADOS: 8 tabelas afetadas' as resumo;
SELECT 'CAMPOS MAIS CRÍTICOS:' as info;
SELECT '- ordens_servico: status_os vs status_geral' as campo_critico;
SELECT '- apontamentos_detalhados: id_setor vs setor' as campo_critico;
SELECT '- tipo_usuarios: id_setor vs setor, id_departamento vs departamento' as campo_critico;
SELECT '- tipo_setores: id_departamento vs departamento' as campo_critico;
SELECT '- tipos_maquina: id_departamento vs setor/departamento' as campo_critico;

SELECT 'RECOMENDAÇÃO: Executar remoções gradualmente após testes' as recomendacao;

-- =====================================================================
-- FIM DO SCRIPT
-- =====================================================================
