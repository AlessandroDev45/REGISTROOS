-- Script para remoção de campos duplicados no banco de dados
-- Baseado na análise em ANALISE_CAMPOS_DUPLICADOS_SIMILARES.md

-- Habilitar modo de transação para segurança
BEGIN TRANSACTION;

-- 1. Tabela ordens_servico - Remover status_geral
ALTER TABLE ordens_servico DROP COLUMN IF EXISTS status_geral;

-- 2. Tabela apontamentos_detalhados - Remover setor
ALTER TABLE apontamentos_detalhados DROP COLUMN IF EXISTS setor;

-- 3. Tabela tipo_usuarios - Remover setor e departamento
ALTER TABLE tipo_usuarios DROP COLUMN IF EXISTS setor;
ALTER TABLE tipo_usuarios DROP COLUMN IF EXISTS departamento;

-- 4. Tabela tipo_setores - Remover departamento
ALTER TABLE tipo_setores DROP COLUMN IF EXISTS departamento;

-- 5. Tabela tipos_maquina - Remover setor e departamento
ALTER TABLE tipos_maquina DROP COLUMN IF EXISTS setor;
ALTER TABLE tipos_maquina DROP COLUMN IF EXISTS departamento;

-- 6. Tabela tipo_causas_retrabalho - Remover departamento e setor
ALTER TABLE tipo_causas_retrabalho DROP COLUMN IF EXISTS departamento;
ALTER TABLE tipo_causas_retrabalho DROP COLUMN IF EXISTS setor;

-- 7. Tabela tipos_teste - Remover campos duplicados
-- Primeiro verificar se existem as colunas antes de remover
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'tipos_teste' AND column_name = 'departamento') THEN
        ALTER TABLE tipos_teste DROP COLUMN IF EXISTS departamento;
    END IF;
    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'tipos_teste' AND column_name = 'setor') THEN
        ALTER TABLE tipos_teste DROP COLUMN IF EXISTS setor;
    END IF;
    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'tipos_teste' AND column_name = 'tipo_maquina') THEN
        ALTER TABLE tipos_teste DROP COLUMN IF EXISTS tipo_maquina;
    END IF;
END $$;

-- 8. Tabela pendencias - Campos duplicados mantidos por compatibilidade
-- Campos cliente e tipo_maquina serão mantidos por enquanto
-- Porém, vamos adicionar comentários para documentar a necessidade de futura migração
COMMENT ON COLUMN pendencias.cliente IS 'Campo temporário - futuro migrar para id_cliente';
COMMENT ON COLUMN pendencias.tipo_maquina IS 'Campo temporário - futuro migrar para id_tipo_maquina';

-- Verificar se as alterações foram aplicadas com sucesso
DO $$
BEGIN
    -- Verificar colunas removidas
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'ordens_servico' AND column_name = 'status_geral') THEN
        RAISE NOTICE 'Campo status_geral removido com sucesso da tabela ordens_servico';
    ELSE
        RAISE EXCEPTION 'Falha ao remover campo status_geral da tabela ordens_servico';
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'apontamentos_detalhados' AND column_name = 'setor') THEN
        RAISE NOTICE 'Campo setor removido com sucesso da tabela apontamentos_detalhados';
    ELSE
        RAISE EXCEPTION 'Falha ao remover campo setor da tabela apontamentos_detalhados';
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'tipo_usuarios' AND column_name = 'setor') AND
       NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'tipo_usuarios' AND column_name = 'departamento') THEN
        RAISE NOTICE 'Campos setor e departamento removidos com sucesso da tabela tipo_usuarios';
    ELSE
        RAISE EXCEPTION 'Falha ao remover campos setor e departamento da tabela tipo_usuarios';
    END IF;

    RAISE NOTICE 'Todas as remoções de campos duplicados foram concluídas com sucesso!';
END $$;

-- Confirmar transação
COMMIT;

-- Script finalizado
-- Resultado: Estrutura de banco de dados limpa sem redundâncias
