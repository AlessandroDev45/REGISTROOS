-- Script para implementar estrutura hierárquica de máquinas
-- Adiciona campo descricao_partes na tabela tipos_maquina

-- 1. Adicionar campo descricao_partes na tabela tipos_maquina
ALTER TABLE tipos_maquina ADD COLUMN descricao_partes TEXT NULL;

-- 2. Inserir estrutura exemplo para Rotativa CC
UPDATE tipos_maquina 
SET descricao_partes = '{
  "partes": [
    {"nome": "Campo Shunt", "id_pai": null, "ordem": 1},
    {"nome": "Campo Série", "id_pai": null, "ordem": 2},
    {"nome": "Interpolos", "id_pai": null, "ordem": 3},
    {"nome": "Armadura", "id_pai": null, "ordem": 4},
    {"nome": "Acessórios", "id_pai": null, "ordem": 5,
     "subpartes": [
       {"nome": "Sensores", "id_pai": 5, "ordem": 1},
       {"nome": "Resistores", "id_pai": 5, "ordem": 2},
       {"nome": "Caixa Ligacao", "id_pai": 5, "ordem": 3}
     ]
    }
  ]
}'
WHERE nome_tipo LIKE '%Rotativa%' OR nome_tipo LIKE '%CC%';

-- 3. Verificar se a alteração foi aplicada
SELECT id, nome_tipo, descricao_partes FROM tipos_maquina WHERE descricao_partes IS NOT NULL;
