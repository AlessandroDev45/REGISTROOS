import React, { useState } from 'react';
import api from '../../services/api';

interface ChangePasswordModalProps {
    isOpen: boolean;
    onClose: () => void;
    onSuccess: () => void;
    isFirstLogin?: boolean;
}

const ChangePasswordModal: React.FC<ChangePasswordModalProps> = ({
    isOpen,
    onClose,
    onSuccess,
    isFirstLogin = false
}) => {
    const [formData, setFormData] = useState({
        senha_atual: '',
        nova_senha: '',
        confirmar_senha: ''
    });
    const [errors, setErrors] = useState<string[]>([]);
    const [loading, setLoading] = useState(false);
    const [showPasswords, setShowPasswords] = useState({
        atual: false,
        nova: false,
        confirmar: false
    });

    const validatePassword = (password: string): string[] => {
        const errors: string[] = [];
        
        if (password.length < 6) {
            errors.push('A senha deve ter pelo menos 6 caracteres');
        }
        if (!/[A-Z]/.test(password)) {
            errors.push('A senha deve conter pelo menos uma letra maiúscula');
        }
        if (!/[a-z]/.test(password)) {
            errors.push('A senha deve conter pelo menos uma letra minúscula');
        }
        if (!/[0-9]/.test(password)) {
            errors.push('A senha deve conter pelo menos um número');
        }
        
        return errors;
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setErrors([]);
        setLoading(true);

        try {
            // Validações
            const validationErrors: string[] = [];

            if (!formData.senha_atual.trim()) {
                validationErrors.push('Senha atual é obrigatória');
            }

            if (!formData.nova_senha.trim()) {
                validationErrors.push('Nova senha é obrigatória');
            }

            if (formData.nova_senha !== formData.confirmar_senha) {
                validationErrors.push('As senhas não coincidem');
            }

            // Validar força da nova senha
            const passwordErrors = validatePassword(formData.nova_senha);
            validationErrors.push(...passwordErrors);

            if (validationErrors.length > 0) {
                setErrors(validationErrors);
                setLoading(false);
                return;
            }

            // Fazer requisição para alterar senha
            await api.put('/change-password', {
                senha_atual: formData.senha_atual,
                nova_senha: formData.nova_senha
            });

            // Sucesso
            setFormData({ senha_atual: '', nova_senha: '', confirmar_senha: '' });
            onSuccess();
            
            if (isFirstLogin) {
                alert('Senha alterada com sucesso! Você será redirecionado para o sistema.');
            }

        } catch (error: any) {
            console.error('Erro ao alterar senha:', error);
            const errorMessage = error.response?.data?.detail || 'Erro ao alterar senha';
            setErrors([errorMessage]);
        } finally {
            setLoading(false);
        }
    };

    const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const { name, value } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: value
        }));
        
        // Limpar erros quando usuário começar a digitar
        if (errors.length > 0) {
            setErrors([]);
        }
    };

    const togglePasswordVisibility = (field: 'atual' | 'nova' | 'confirmar') => {
        setShowPasswords(prev => ({
            ...prev,
            [field]: !prev[field]
        }));
    };

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg p-6 w-full max-w-md mx-4">
                <div className="flex justify-between items-center mb-4">
                    <h2 className="text-xl font-bold text-gray-900">
                        {isFirstLogin ? 'Alterar Senha - Primeiro Acesso' : 'Alterar Senha'}
                    </h2>
                    {!isFirstLogin && (
                        <button
                            onClick={onClose}
                            className="text-gray-400 hover:text-gray-600"
                        >
                            ✕
                        </button>
                    )}
                </div>

                {isFirstLogin && (
                    <div className="bg-yellow-50 border border-yellow-200 rounded-md p-3 mb-4">
                        <p className="text-sm text-yellow-800">
                            <strong>Primeiro acesso:</strong> Por segurança, você deve alterar sua senha temporária antes de continuar.
                        </p>
                    </div>
                )}

                <form onSubmit={handleSubmit} className="space-y-4">
                    {/* Senha Atual */}
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                            Senha Atual
                        </label>
                        <div className="relative">
                            <input
                                type={showPasswords.atual ? "text" : "password"}
                                name="senha_atual"
                                value={formData.senha_atual}
                                onChange={handleInputChange}
                                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 pr-10"
                                required
                            />
                            <button
                                type="button"
                                onClick={() => togglePasswordVisibility('atual')}
                                className="absolute inset-y-0 right-0 pr-3 flex items-center"
                            >
                                {showPasswords.atual ? '👁️' : '👁️‍🗨️'}
                            </button>
                        </div>
                    </div>

                    {/* Nova Senha */}
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                            Nova Senha
                        </label>
                        <div className="relative">
                            <input
                                type={showPasswords.nova ? "text" : "password"}
                                name="nova_senha"
                                value={formData.nova_senha}
                                onChange={handleInputChange}
                                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 pr-10"
                                required
                            />
                            <button
                                type="button"
                                onClick={() => togglePasswordVisibility('nova')}
                                className="absolute inset-y-0 right-0 pr-3 flex items-center"
                            >
                                {showPasswords.nova ? '👁️' : '👁️‍🗨️'}
                            </button>
                        </div>
                    </div>

                    {/* Confirmar Senha */}
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                            Confirmar Nova Senha
                        </label>
                        <div className="relative">
                            <input
                                type={showPasswords.confirmar ? "text" : "password"}
                                name="confirmar_senha"
                                value={formData.confirmar_senha}
                                onChange={handleInputChange}
                                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 pr-10"
                                required
                            />
                            <button
                                type="button"
                                onClick={() => togglePasswordVisibility('confirmar')}
                                className="absolute inset-y-0 right-0 pr-3 flex items-center"
                            >
                                {showPasswords.confirmar ? '👁️' : '👁️‍🗨️'}
                            </button>
                        </div>
                    </div>

                    {/* Requisitos da senha */}
                    <div className="bg-gray-50 border border-gray-200 rounded-md p-3">
                        <p className="text-sm font-medium text-gray-700 mb-2">Requisitos da senha:</p>
                        <ul className="text-xs text-gray-600 space-y-1">
                            <li>• Pelo menos 6 caracteres</li>
                            <li>• Pelo menos uma letra maiúscula</li>
                            <li>• Pelo menos uma letra minúscula</li>
                            <li>• Pelo menos um número</li>
                        </ul>
                    </div>

                    {/* Erros */}
                    {errors.length > 0 && (
                        <div className="bg-red-50 border border-red-200 rounded-md p-3">
                            <ul className="text-sm text-red-600 space-y-1">
                                {errors.map((error, index) => (
                                    <li key={index}>• {error}</li>
                                ))}
                            </ul>
                        </div>
                    )}

                    {/* Botões */}
                    <div className="flex gap-3 pt-4">
                        {!isFirstLogin && (
                            <button
                                type="button"
                                onClick={onClose}
                                className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50"
                                disabled={loading}
                            >
                                Cancelar
                            </button>
                        )}
                        <button
                            type="submit"
                            className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-blue-300"
                            disabled={loading}
                        >
                            {loading ? 'Alterando...' : 'Alterar Senha'}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
};

export default ChangePasswordModal;
