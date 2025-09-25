import React, { useState, ChangeEvent, useEffect } from 'react';
import { Trash2, Plus } from 'lucide-react';
import { TestField } from './TestFieldType'; // Importe a interface

interface TestFieldsConfiguratorProps {
  // Lista inicial de campos. Se for undefined, começa com um campo vazio.
  initialFields?: TestField[];
  // Função chamada quando a lista de campos muda.
  // Deve receber a lista atualizada de campos.
  onFieldsChange: (fields: TestField[]) => void;
}

const TestFieldsConfigurator: React.FC<TestFieldsConfiguratorProps> = ({
  initialFields = [{ id: '', label: '', type: 'string', required: false }],
  onFieldsChange,
}) => {
  const [fields, setFields] = useState<TestField[]>(initialFields);

  // Sync internal state with external prop changes
  useEffect(() => {
    if (initialFields) {
      setFields(initialFields);
    } else {
      setFields([{ id: '', label: '', type: 'string', required: false }]);
    }
  }, [initialFields]);

  const addField = () => {
    const newField: TestField = {
      id: generateId(), // Função auxiliar para gerar IDs únicos simples
      label: '',
      type: 'string',
      required: false,
    };
    const updatedFields = [...fields, newField];
    setFields(updatedFields);
    onFieldsChange(updatedFields);
  };

  const removeField = (index: number) => {
    if (fields.length <= 1) return; // Não permitir remover todos os campos
    const updatedFields = fields.filter((_, i) => i !== index);
    setFields(updatedFields);
    onFieldsChange(updatedFields);
  };

  const updateField = (index: number, updatedField: TestField) => {
    const newFields = [...fields];
    newFields[index] = updatedField;
    setFields(newFields);
    onFieldsChange(newFields);
  };

  const handleFieldPropertyChange = (
    index: number,
    property: keyof TestField,
    value: string | boolean | string[] // Adicionado string[] para o caso de 'options'
  ) => {
    const fieldToUpdate = fields[index];
    // Cria um novo objeto para garantir imutabilidade
    const updatedField: TestField = { ...fieldToUpdate, [property]: value };
    updateField(index, updatedField);
  };

  // Função auxiliar para gerar IDs simples
  function generateId(): string {
    return Math.random().toString(36).substr(2, 9);
  }

  return (
    <div className="w-full bg-white rounded-lg border border-gray-200 shadow-sm">
      <div className="p-6 border-b border-gray-200">
        <h3 className="text-lg font-semibold text-gray-900">Campos de Resultado de Teste</h3>
        <p className="text-sm text-gray-500 mt-1">
          Defina os campos personalizados para armazenar resultados de teste para este tipo de máquina.
        </p>
      </div>
      <div className="p-6 space-y-4">
        {fields.map((field, index) => (
          <div key={field.id || index} className="border rounded-lg p-4 space-y-3">
            <div className="flex justify-between items-center">
              <h4 className="font-medium">Campo {index + 1}</h4>
              {fields.length > 1 && (
                <button
                  type="button"
                  onClick={() => removeField(index)}
                  className="p-1 text-red-600 hover:text-red-800"
                  aria-label="Remover campo"
                >
                  <Trash2 className="h-4 w-4" />
                </button>
              )}
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              <div>
                <label htmlFor={`label-${index}`} className="block text-sm font-medium text-gray-700">Rótulo do Campo</label>
                <input
                  type="text"
                  id={`label-${index}`}
                  value={field.label}
                  onChange={(e: ChangeEvent<HTMLInputElement>) => handleFieldPropertyChange(index, 'label', e.target.value)}
                  placeholder="Ex: Perdas em Vazio"
                  className="mt-1 block w-full p-2 border border-gray-300 rounded-md shadow-sm"
                />
              </div>
              <div>
                <label htmlFor={`id-${index}`} className="block text-sm font-medium text-gray-700">ID do Campo (único)</label>
                <input
                  type="text"
                  id={`id-${index}`}
                  value={field.id}
                  onChange={(e: ChangeEvent<HTMLInputElement>) => handleFieldPropertyChange(index, 'id', e.target.value)}
                  placeholder="Ex: perdas_vazio"
                  className="mt-1 block w-full p-2 border border-gray-300 rounded-md shadow-sm"
                />
              </div>
              <div>
                <label htmlFor={`type-${index}`} className="block text-sm font-medium text-gray-700">Tipo de Dados</label>
                <select
                  id={`type-${index}`}
                  value={field.type}
                  onChange={(e: ChangeEvent<HTMLSelectElement>) => handleFieldPropertyChange(index, 'type', e.target.value as TestField['type'])}
                  className="mt-1 block w-full p-2 border border-gray-300 rounded-md shadow-sm"
                >
                  <option value="string">Texto Curto</option>
                  <option value="text">Texto Longo</option>
                  <option value="number">Número Inteiro</option>
                  <option value="float">Número Decimal</option>
                  <option value="select">Seleção (Opções)</option>
                </select>
              </div>
              <div>
                <label htmlFor={`unit-${index}`} className="block text-sm font-medium text-gray-700">Unidade (opcional)</label>
                <input
                  type="text"
                  id={`unit-${index}`}
                  value={field.unit || ''}
                  onChange={(e: ChangeEvent<HTMLInputElement>) => handleFieldPropertyChange(index, 'unit', e.target.value)}
                  placeholder="Ex: W, A, V, s"
                  className="mt-1 block w-full p-2 border border-gray-300 rounded-md shadow-sm"
                />
              </div>
            </div>
            <div className="flex items-center space-x-2">
              <input
                type="checkbox"
                id={`required-${index}`}
                checked={field.required || false}
                onChange={(e: ChangeEvent<HTMLInputElement>) => handleFieldPropertyChange(index, 'required', e.target.checked)}
                className="rounded border-gray-300 text-indigo-600 shadow-sm focus:ring-indigo-500"
              />
              <label htmlFor={`required-${index}`} className="block text-sm font-medium text-gray-700">Campo obrigatório</label>
            </div>
            {field.type === 'select' && (
              <div>
                <label htmlFor={`options-${index}`} className="block text-sm font-medium text-gray-700">Opções (uma por linha)</label>
                <textarea
                  id={`options-${index}`}
                  value={field.options?.join('\n') || ''}
                  onChange={(e: ChangeEvent<HTMLTextAreaElement>) =>
                    handleFieldPropertyChange(
                      index,
                      'options',
                      e.target.value.split('\n').filter((opt: string) => opt.trim() !== '')
                    )
                  }
                  placeholder="AP&#10;RE&#10;PENDENTE"
                  rows={3}
                  className="mt-1 block w-full p-2 border border-gray-300 rounded-md shadow-sm"
                />
              </div>
            )}
          </div>
        ))}
        <button
          type="button"
          onClick={addField}
          className="flex items-center justify-center w-full p-2 border border-gray-300 rounded-md hover:bg-gray-50"
        >
          <Plus className="h-4 w-4 mr-2" />
          Adicionar Novo Campo
        </button>
      </div>
    </div>
  );
};

export default TestFieldsConfigurator;