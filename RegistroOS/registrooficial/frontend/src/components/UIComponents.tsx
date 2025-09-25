import React from 'react';

// Interface para StyledInput (com estilo mais específico)
export interface StyledInputProps {
  type?: string;
  placeholder?: string;
  value?: string;
  onChange?: (e: React.ChangeEvent<HTMLInputElement>) => void;
  className?: string;
  defaultValue?: string;
  style?: React.CSSProperties;
  disabled?: boolean;
  name?: string;
  readOnly?: boolean;
  error?: string;
  required?: boolean;
  label?: string;
  id?: string;
  min?: string;
  step?: string;
}

// Componente de Input com estilo consistente
export const StyledInput: React.FC<StyledInputProps> = ({
  type = 'text',
  placeholder,
  value,
  onChange,
  className = '',
  defaultValue,
  style,
  disabled,
  name,
  readOnly,
  error,
  required,
  label,
  min,
  step,
}) => {
  const inputClasses = `w-full h-12 px-3 border ${error ? 'border-red-500' : 'border-gray-300'} rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${className}`.trim();
  
  return (
    <div className="mb-4">
      {label && (
        <label className="block text-sm font-medium text-gray-700 mb-1">
          {label}
          {required && <span className="text-red-500">*</span>}
        </label>
      )}
      <input
        type={type}
        placeholder={placeholder}
        value={value}
        onChange={onChange}
        defaultValue={defaultValue}
        className={inputClasses}
        style={style}
        disabled={disabled}
        readOnly={readOnly}
        name={name}
        required={required}
        min={min}
        step={step}
      />
      {error && <p className="mt-1 text-sm text-red-600">{error}</p>}
    </div>
  );
};

// Interface para SelectField
export interface SelectFieldProps {
  value?: string;
  onChange?: (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => void;
  className?: string;
  children: React.ReactNode;
  style?: React.CSSProperties;
  disabled?: boolean;
  name?: string;
  label?: string;
  required?: boolean;
  id?: string;
  error?: string;
}

// Componente de Select reutilizável
export const SelectField: React.FC<SelectFieldProps> = ({
  value,
  onChange,
  className = 'select-field',
  children,
  style,
  disabled,
  name,
  label,
  required,
  error
}) => (
  <div className="mb-4">
    {label && (
      <label className="block text-sm font-medium text-gray-700 mb-1">
        {label}
        {required && <span className="text-red-500">*</span>}
      </label>
    )}
    <select 
      value={value} 
      onChange={onChange as (e: React.ChangeEvent<HTMLSelectElement>) => void} 
      className={`w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 ${disabled ? 'bg-gray-100' : ''} ${error ? 'border-red-500' : ''}`.trim()}
      style={style} 
      disabled={disabled} 
      name={name}
      required={required}
      id={name}
    >
      {children}
    </select>
    {error && <p className="mt-1 text-sm text-red-600">{error}</p>}
  </div>
);

// Componente de Checkbox reutilizável
export const CheckboxField: React.FC<{
  id: string;
  label: string;
  checked?: boolean;
  onChange?: (e: React.ChangeEvent<HTMLInputElement>) => void;
  className?: string;
  labelClass?: string;
}> = ({ id, label, checked, onChange, className = 'checkbox-container', labelClass = 'checkbox-label' }) => (
  <div className={className}>
    <input type="checkbox" id={id} checked={checked} onChange={onChange} />
    <label htmlFor={id} className={labelClass}>{label}</label>
  </div>
);

// Componente de Radio Button reutilizável
export const RadioField: React.FC<{
  name: string;
  value: string;
  label: string;
  checked?: boolean;
  onChange?: (e: React.ChangeEvent<HTMLInputElement>) => void;
  className?: string;
  labelClass?: string;
}> = ({ name, value, label, checked, onChange, className = 'radio-container', labelClass = 'radio-label' }) => (
  <div className={className}>
    <input type="radio" name={name} value={value} checked={checked} onChange={onChange} />
    <label className={labelClass}>{label}</label>
  </div>
);

// Componente de Botão reutilizável
export const Button: React.FC<{
  onClick?: () => Promise<void> | void; // Permite Promise<void> para async handlers
  className?: string;
  children: React.ReactNode;
  type?: 'button' | 'submit' | 'reset';
  style?: React.CSSProperties;
  disabled?: boolean; // Adicionando a propriedade disabled
}> = ({ onClick, className = 'btn-primary', children, type = 'button', style, disabled }) => (
  <button type={type} onClick={onClick} className={className} style={style} disabled={disabled}>
    {children}
  </button>
);

// Container flexível
export const FlexContainer: React.FC<{
  children: React.ReactNode;
  className?: string;
  gap?: string;
  style?: React.CSSProperties;
}> = ({ children, className = 'flex-container', gap = '5px', style }) => (
  <div className={className} style={{ gap, ...style }}>
    {children}
  </div>
);

// Container centralizado
export const FlexCenter: React.FC<{
  children: React.ReactNode;
  className?: string;
  style?: React.CSSProperties;
}> = ({ children, className = 'flex-center', style }) => (
  <div className={className} style={style}>
    {children}
  </div>
);

// Componente de Tab
export const TabContainer: React.FC<{
  children: React.ReactNode;
  className?: string;
}> = ({ children, className = 'tab-container' }) => (
  <div className={className}>
    {children}
  </div>
);

export const TabButton: React.FC<{
  active?: boolean;
  onClick?: () => void;
  children: React.ReactNode;
  className?: string;
}> = ({ active, onClick, children, className }) => (
  <button
    onClick={onClick}
    className={`${className || 'tab-button'} ${active ? 'active' : ''}`}
  >
    {children}
  </button>
);

// Componente de Input com estilo consistente
export const InputField: React.FC<StyledInputProps> = (props) => <StyledInput {...props} />;

// Componente DateTime Input
export const DateTimeInput: React.FC<{
  type: 'date' | 'time' | 'datetime-local';
  name?: string;
  value?: string;
  onChange?: (e: React.ChangeEvent<HTMLInputElement>) => void;
  placeholder?: string;
  className?: string;
  required?: boolean;
  disabled?: boolean;
}> = ({
  type,
  name,
  value,
  onChange,
  placeholder,
  className = '',
  required,
  disabled
}) => (
  <input
    type={type}
    name={name}
    value={value}
    onChange={onChange}
    placeholder={placeholder}
    className={`w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${className}`.trim()}
    required={required}
    disabled={disabled}
  />
);

// Interface para TextareaField
export interface TextareaFieldProps {
  value?: string;
  onChange?: (e: React.ChangeEvent<HTMLTextAreaElement>) => void;
  className?: string;
  placeholder?: string;
  rows?: number;
  style?: React.CSSProperties;
  disabled?: boolean;
  name?: string;
  label?: string;
  required?: boolean;
  error?: string;
}

// Componente de Textarea reutilizável
export const TextareaField: React.FC<TextareaFieldProps> = ({
  value,
  onChange,
  className = '',
  placeholder,
  rows = 4,
  style,
  disabled,
  name,
  label,
  required,
  error,
}) => (
  <div className="mb-4">
    {label && (
      <label className="block text-sm font-medium text-gray-700 mb-1">
        {label}
        {required && <span className="text-red-500">*</span>}
      </label>
    )}
    <textarea
      value={value}
      onChange={onChange}
      className={`w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 ${disabled ? 'bg-gray-100' : ''} ${error ? 'border-red-500' : ''} ${className}`.trim()}
      placeholder={placeholder}
      rows={rows}
      style={style}
      disabled={disabled}
      name={name}
      required={required}
    />
    {error && <p className="mt-1 text-sm text-red-600">{error}</p>}
  </div>
);

// Simple Toast Utility
let toastContainer: HTMLDivElement | null = null;

export const showToast = (message: string, type: 'success' | 'error' | 'info' | 'warning' = 'info') => {
  // Create container if it doesn't exist
  if (!toastContainer) {
    toastContainer = document.createElement('div');
    toastContainer.className = 'fixed top-4 right-4 z-50 space-y-2';
    document.body.appendChild(toastContainer);
  }

  // Create toast element
  const toast = document.createElement('div');
  const toastId = Math.random().toString(36).substr(2, 9);
  toast.id = toastId;

  const baseStyles = "flex items-center p-4 rounded-lg shadow-lg transition-all duration-300 max-w-sm transform translate-x-full opacity-0";

  let bgColor = 'bg-blue-500';
  switch (type) {
    case 'success':
      bgColor = 'bg-green-500';
      break;
    case 'error':
      bgColor = 'bg-red-500';
      break;
    case 'warning':
      bgColor = 'bg-yellow-500';
      break;
  }

  toast.className = `${baseStyles} ${bgColor} text-white`;

  toast.innerHTML = `
    <div class="flex-1">${message}</div>
    <button class="ml-4 text-white hover:text-gray-200 focus:outline-none" onclick="this.parentElement.remove()">×</button>
  `;

  toastContainer.appendChild(toast);

  // Animate in
  setTimeout(() => {
    toast.classList.remove('translate-x-full', 'opacity-0');
    toast.classList.add('translate-x-0', 'opacity-100');
  }, 10);

  // Auto remove after 5 seconds
  setTimeout(() => {
    if (toast.parentElement) {
      toast.classList.remove('translate-x-0', 'opacity-100');
      toast.classList.add('translate-x-full', 'opacity-0');
      setTimeout(() => toast.remove(), 300);
    }
  }, 5000);
};
