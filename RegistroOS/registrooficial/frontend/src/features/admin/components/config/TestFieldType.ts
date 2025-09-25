// Arquivo: RegistroOS/registrooficial/frontend/src/features/admin/components/config/TestFieldType.ts
export interface TestField {
  id: string;
  label: string;
  type: 'number' | 'float' | 'string' | 'text' | 'select';
  unit?: string;
  required?: boolean;
  options?: string[]; // Para 'select'
}